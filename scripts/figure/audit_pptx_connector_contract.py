#!/usr/bin/env python3
"""Fail-closed audit for native PowerPoint connector construction."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}
EMU_PER_POINT = 12700
AXIS_TOLERANCE_EMU = int(0.1 * EMU_PER_POINT)
VALID_ANCHORS = {"left", "right", "top", "bottom"}
SEGMENT_PATTERN = re.compile(r"(?:^|[_-])(seg(?:ment)?|part)(?:[_-]|\d|$)", re.I)


def slide_index(name: str) -> int:
    match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
    if not match:
        raise ValueError(f"Not a slide XML path: {name}")
    return int(match.group(1))


def c_nv_pr(element: ET.Element) -> ET.Element | None:
    for path in (
        "./p:nvSpPr/p:cNvPr",
        "./p:nvPicPr/p:cNvPr",
        "./p:nvGraphicFramePr/p:cNvPr",
        "./p:nvGrpSpPr/p:cNvPr",
        "./p:nvCxnSpPr/p:cNvPr",
    ):
        result = element.find(path, NS)
        if result is not None:
            return result
    return None


def xfrm_for(element: ET.Element) -> ET.Element | None:
    for path in (
        "./p:spPr/a:xfrm",
        "./p:grpSpPr/a:xfrm",
        "./p:xfrm",
    ):
        result = element.find(path, NS)
        if result is not None:
            return result
    return None


def bbox_for(element: ET.Element) -> dict[str, int] | None:
    xfrm = xfrm_for(element)
    if xfrm is None:
        return None
    off = xfrm.find("./a:off", NS)
    ext = xfrm.find("./a:ext", NS)
    if off is None or ext is None:
        return None
    try:
        x = int(off.get("x", "0"))
        y = int(off.get("y", "0"))
        cx = int(ext.get("cx", "0"))
        cy = int(ext.get("cy", "0"))
    except ValueError:
        return None
    return {
        "x": x,
        "y": y,
        "cx": cx,
        "cy": cy,
        "center_x": x + cx // 2,
        "center_y": y + cy // 2,
    }


def geometry_for(element: ET.Element) -> str | None:
    geometry = element.find("./p:spPr/a:prstGeom", NS)
    if geometry is not None:
        return geometry.get("prst")
    if element.find("./p:spPr/a:custGeom", NS) is not None:
        return "custGeom"
    return None


def normalized_geometry(value: str | None) -> str:
    geometry = str(value or "")
    if geometry in {"line", "straightConnector1"}:
        return "line"
    return geometry


def arrow_end_type(element: ET.Element, end_name: str) -> str:
    arrow = element.find(f"./p:spPr/a:ln/a:{end_name}", NS)
    return str(arrow.get("type") or "none") if arrow is not None else "none"


def is_arrow_like_ordinary_shape(element: ET.Element) -> bool:
    geometry = geometry_for(element)
    if geometry not in {"line", "straightConnector1"}:
        return False
    return any(
        arrow_end_type(element, end_name).lower() not in {"", "none"}
        for end_name in ("headEnd", "tailEnd")
    )


def color_is_fully_transparent(container: ET.Element | None) -> bool:
    if container is None:
        return False
    for alpha in container.findall(".//a:alpha", NS):
        try:
            if int(alpha.get("val", "100000")) == 0:
                return True
        except ValueError:
            continue
    return False


def is_invisible_proxy_candidate(element: ET.Element) -> bool:
    shape_properties = element.find("./p:spPr", NS)
    if shape_properties is None:
        return False
    fill_invisible = (
        shape_properties.find("./a:noFill", NS) is not None
        or color_is_fully_transparent(shape_properties.find("./a:solidFill", NS))
    )
    line = shape_properties.find("./a:ln", NS)
    line_invisible = (
        line is not None
        and (
            line.find("./a:noFill", NS) is not None
            or color_is_fully_transparent(line.find("./a:solidFill", NS))
        )
    )
    has_text = any(
        str(text.text or "").strip()
        for text in element.findall("./p:txBody//a:t", NS)
    )
    return fill_invisible and line_invisible and not has_text


def looks_like_proxy(name: str | None) -> bool:
    if not name:
        return False
    normalized = name.upper().replace(" ", "-")
    return (
        normalized.startswith(("ANCHOR_", "ANCHOR-", "PROXY_", "PROXY-"))
        or "-ANCHOR-" in normalized
        or "_ANCHOR_" in normalized
        or normalized.startswith("AXIS-ANCHOR")
    )


def load_ledger(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Connector ledger does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Connector ledger must be a JSON object.")
    for field in ("connectors", "proxy_whitelist", "ordinary_arrow_whitelist"):
        if field not in payload or not isinstance(payload[field], list):
            raise ValueError(f"Ledger field '{field}' must be an array.")
    if "expected_connector_count" not in payload:
        raise ValueError("Ledger field 'expected_connector_count' is required.")
    try:
        expected_count = int(payload["expected_connector_count"])
    except (TypeError, ValueError) as exc:
        raise ValueError("expected_connector_count must be an integer.") from exc
    if expected_count < 0:
        raise ValueError("expected_connector_count cannot be negative.")
    if expected_count != len(payload["connectors"]):
        raise ValueError(
            "expected_connector_count must equal the number of connector ledger entries."
        )
    return payload


def load_pptx(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"PPTX does not exist: {path}")
    connectors: list[dict[str, Any]] = []
    ordinary_arrows: list[dict[str, Any]] = []
    shapes_by_slide: dict[int, dict[str, dict[str, Any]]] = {}
    with zipfile.ZipFile(path) as archive:
        slide_names = sorted(
            (
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ),
            key=slide_index,
        )
        for slide_name in slide_names:
            number = slide_index(slide_name)
            root = ET.fromstring(archive.read(slide_name))
            id_to_shape: dict[str, dict[str, Any]] = {}
            name_to_shape: dict[str, dict[str, Any]] = {}
            for tag in ("sp", "pic", "graphicFrame", "grpSp", "cxnSp"):
                for element in root.findall(f".//p:{tag}", NS):
                    identity = c_nv_pr(element)
                    if identity is None:
                        continue
                    shape = {
                        "slide_index": number,
                        "shape_id": str(identity.get("id") or ""),
                        "shape_name": str(identity.get("name") or ""),
                        "shape_tag": tag,
                        "bbox": bbox_for(element),
                        "invisible_proxy_candidate": (
                            is_invisible_proxy_candidate(element) if tag == "sp" else False
                        ),
                    }
                    id_to_shape[shape["shape_id"]] = shape
                    name_to_shape[shape["shape_name"]] = shape
                    if tag == "sp" and is_arrow_like_ordinary_shape(element):
                        ordinary_arrows.append(
                            {
                                **shape,
                                "geometry": geometry_for(element),
                                "head_end": arrow_end_type(element, "headEnd"),
                                "tail_end": arrow_end_type(element, "tailEnd"),
                            }
                        )
            shapes_by_slide[number] = name_to_shape

            for element in root.findall(".//p:cxnSp", NS):
                identity = c_nv_pr(element)
                name = str(identity.get("name") or "") if identity is not None else ""
                properties = element.find("./p:nvCxnSpPr/p:cNvCxnSpPr", NS)
                start = properties.find("./a:stCxn", NS) if properties is not None else None
                end = properties.find("./a:endCxn", NS) if properties is not None else None
                source_id = str(start.get("id")) if start is not None else None
                target_id = str(end.get("id")) if end is not None else None
                source = id_to_shape.get(source_id or "")
                target = id_to_shape.get(target_id or "")
                connectors.append(
                    {
                        "slide_index": number,
                        "connector_name": name,
                        "geometry": geometry_for(element),
                        "source_id": source_id,
                        "source_name": source["shape_name"] if source else None,
                        "target_id": target_id,
                        "target_name": target["shape_name"] if target else None,
                    }
                )
    return {
        "connectors": connectors,
        "ordinary_arrows": ordinary_arrows,
        "shapes_by_slide": shapes_by_slide,
    }


def audit(document: dict[str, Any], ledger: dict[str, Any]) -> dict[str, Any]:
    connectors = document["connectors"]
    ordinary_arrows = document["ordinary_arrows"]
    shapes_by_slide = document["shapes_by_slide"]

    actual_counter = Counter(
        (int(item["slide_index"]), str(item["connector_name"])) for item in connectors
    )
    ledger_counter = Counter(
        (int(item["slide_index"]), str(item["connector_name"]))
        for item in ledger["connectors"]
    )
    actual_by_key = {
        (int(item["slide_index"]), str(item["connector_name"])): item
        for item in connectors
    }
    ledger_by_key = {
        (int(item["slide_index"]), str(item["connector_name"])): item
        for item in ledger["connectors"]
    }

    malformed_ledger: list[dict[str, Any]] = []
    logical_path_keys: list[tuple[int, str]] = []
    required_fields = (
        "slide_index",
        "connector_name",
        "logical_path_id",
        "expected_source",
        "expected_target",
        "source_anchor",
        "target_anchor",
        "expected_geometry",
        "reason",
    )
    for item in ledger["connectors"]:
        missing = [field for field in required_fields if not str(item.get(field, "")).strip()]
        invalid_anchors = [
            field
            for field in ("source_anchor", "target_anchor")
            if str(item.get(field, "")).lower() not in VALID_ANCHORS
        ]
        if missing or invalid_anchors:
            malformed_ledger.append(
                {
                    "slide_index": item.get("slide_index"),
                    "connector_name": item.get("connector_name"),
                    "missing_fields": missing,
                    "invalid_anchor_fields": invalid_anchors,
                }
            )
        logical_path_keys.append(
            (int(item.get("slide_index", 0)), str(item.get("logical_path_id") or ""))
        )

    duplicate_connector_names = [
        {"slide_index": key[0], "connector_name": key[1], "count": count}
        for key, count in actual_counter.items()
        if count > 1
    ]
    duplicate_ledger_names = [
        {"slide_index": key[0], "connector_name": key[1], "count": count}
        for key, count in ledger_counter.items()
        if count > 1
    ]
    logical_path_counter = Counter(logical_path_keys)
    duplicate_logical_paths = [
        {"slide_index": key[0], "logical_path_id": key[1], "count": count}
        for key, count in logical_path_counter.items()
        if count > 1 or not key[1]
    ]

    proxy_whitelist: dict[tuple[int, str, str, str], dict[str, Any]] = {}
    invalid_proxy_whitelist: list[dict[str, Any]] = []
    for item in ledger["proxy_whitelist"]:
        endpoint = str(item.get("endpoint") or "").lower()
        key = (
            int(item.get("slide_index", 0)),
            str(item.get("connector_name") or ""),
            endpoint,
            str(item.get("shape_name") or ""),
        )
        required = (
            "slide_index",
            "connector_name",
            "endpoint",
            "shape_name",
            "owner_shape",
            "side",
            "relative_position",
            "reason",
            "move_follow_verified",
        )
        missing = [field for field in required if item.get(field) in (None, "")]
        if endpoint not in {"source", "target"}:
            missing.append("endpoint(source|target)")
        if item.get("move_follow_verified") is not True:
            missing.append("move_follow_verified=true")
        if str(item.get("side") or "").lower() not in VALID_ANCHORS:
            missing.append("side(left|right|top|bottom)")
        owner = str(item.get("owner_shape") or "")
        if owner and owner not in shapes_by_slide.get(key[0], {}):
            missing.append("owner_shape must exist on slide")
        proxy_shape = str(item.get("shape_name") or "")
        if proxy_shape and proxy_shape not in shapes_by_slide.get(key[0], {}):
            missing.append("shape_name must exist on slide")
        if missing:
            invalid_proxy_whitelist.append({"entry": item, "problems": sorted(set(missing))})
        proxy_whitelist[key] = item

    ordinary_whitelist = {
        (int(item.get("slide_index", 0)), str(item.get("shape_name") or "")): item
        for item in ledger["ordinary_arrow_whitelist"]
        if str(item.get("reason") or "").strip()
    }
    invalid_ordinary_whitelist = [
        item
        for item in ledger["ordinary_arrow_whitelist"]
        if not str(item.get("shape_name") or "").strip()
        or not str(item.get("reason") or "").strip()
    ]

    unconnected: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    unapproved_proxies: list[dict[str, Any]] = []
    geometry_mismatches: list[dict[str, Any]] = []
    unnecessary_elbows: list[dict[str, Any]] = []
    non_axis_aligned_straight_connectors: list[dict[str, Any]] = []
    missing_geometry_inputs: list[dict[str, Any]] = []

    for key, expected in ledger_by_key.items():
        actual = actual_by_key.get(key)
        if actual is None:
            continue
        effective_names: dict[str, str | None] = {}
        for endpoint in ("source", "target"):
            actual_name = actual.get(f"{endpoint}_name")
            effective_name = actual_name
            proxy_candidate = False
            if not actual_name:
                unconnected.append(
                    {
                        "slide_index": key[0],
                        "connector_name": key[1],
                        "endpoint": endpoint,
                    }
                )
            else:
                actual_shape = shapes_by_slide.get(key[0], {}).get(str(actual_name))
                proxy_candidate = looks_like_proxy(str(actual_name)) or bool(
                    actual_shape and actual_shape.get("invisible_proxy_candidate")
                )
            if actual_name and proxy_candidate:
                whitelist_key = (key[0], key[1], endpoint, str(actual_name))
                whitelist_item = proxy_whitelist.get(whitelist_key)
                if whitelist_item is None:
                    unapproved_proxies.append(
                        {
                            "slide_index": key[0],
                            "connector_name": key[1],
                            "endpoint": endpoint,
                            "shape_name": actual_name,
                        }
                    )
                else:
                    effective_name = str(whitelist_item.get("owner_shape") or actual_name)
            effective_names[endpoint] = effective_name
            expected_name = str(expected.get(f"expected_{endpoint}") or "")
            if actual_name and effective_name != expected_name:
                mismatches.append(
                    {
                        "slide_index": key[0],
                        "connector_name": key[1],
                        "endpoint": endpoint,
                        "expected": expected_name,
                        "actual": actual_name,
                        "effective_actual": effective_name,
                    }
                )

        expected_geometry = normalized_geometry(
            str(expected.get("expected_geometry") or "")
        )
        actual_geometry = normalized_geometry(str(actual.get("geometry") or ""))
        if expected_geometry != actual_geometry:
            geometry_mismatches.append(
                {
                    "slide_index": key[0],
                    "connector_name": key[1],
                    "expected": expected_geometry,
                    "actual": actual_geometry,
                }
            )

        slide_shapes = shapes_by_slide.get(key[0], {})
        source_shape = slide_shapes.get(str(actual.get("source_name") or ""))
        target_shape = slide_shapes.get(str(actual.get("target_name") or ""))
        source_bbox = source_shape.get("bbox") if source_shape else None
        target_bbox = target_shape.get("bbox") if target_shape else None
        if source_bbox is None or target_bbox is None:
            missing_geometry_inputs.append(
                {
                    "slide_index": key[0],
                    "connector_name": key[1],
                    "source": effective_names.get("source"),
                    "target": effective_names.get("target"),
                }
            )
            continue

        source_anchor = str(expected.get("source_anchor") or "").lower()
        target_anchor = str(expected.get("target_anchor") or "").lower()
        horizontal_pair = {source_anchor, target_anchor} == {"left", "right"}
        vertical_pair = {source_anchor, target_anchor} == {"top", "bottom"}
        co_axial = (
            horizontal_pair
            and abs(source_bbox["center_y"] - target_bbox["center_y"])
            <= AXIS_TOLERANCE_EMU
        ) or (
            vertical_pair
            and abs(source_bbox["center_x"] - target_bbox["center_x"])
            <= AXIS_TOLERANCE_EMU
        )
        if co_axial and actual_geometry != "line":
            unnecessary_elbows.append(
                {
                    "slide_index": key[0],
                    "connector_name": key[1],
                    "actual_geometry": actual_geometry,
                    "axis_error_pt": round(
                        (
                            abs(source_bbox["center_y"] - target_bbox["center_y"])
                            if horizontal_pair
                            else abs(source_bbox["center_x"] - target_bbox["center_x"])
                        )
                        / EMU_PER_POINT,
                        4,
                    ),
                }
            )
        axis_error_emu = (
            abs(source_bbox["center_y"] - target_bbox["center_y"])
            if horizontal_pair
            else abs(source_bbox["center_x"] - target_bbox["center_x"])
            if vertical_pair
            else None
        )
        if (
            actual_geometry == "line"
            and axis_error_emu is not None
            and axis_error_emu > AXIS_TOLERANCE_EMU
        ):
            non_axis_aligned_straight_connectors.append(
                {
                    "slide_index": key[0],
                    "connector_name": key[1],
                    "axis_error_pt": round(axis_error_emu / EMU_PER_POINT, 4),
                    "source_anchor": source_anchor,
                    "target_anchor": target_anchor,
                }
            )

    unledgered_connectors = [
        {"slide_index": key[0], "connector_name": key[1]}
        for key in actual_counter
        if key not in ledger_counter
    ]
    missing_connectors = [
        {"slide_index": key[0], "connector_name": key[1]}
        for key in ledger_counter
        if key not in actual_counter
    ]
    unapproved_ordinary_arrows = [
        item
        for item in ordinary_arrows
        if (int(item["slide_index"]), str(item["shape_name"])) not in ordinary_whitelist
    ]
    stale_ordinary_whitelist = [
        {"slide_index": key[0], "shape_name": key[1]}
        for key in ordinary_whitelist
        if not any(
            int(item["slide_index"]) == key[0] and str(item["shape_name"]) == key[1]
            for item in ordinary_arrows
        )
    ]
    used_proxy_keys = {
        (
            int(item["slide_index"]),
            str(item["connector_name"]),
            endpoint,
            str(item.get(f"{endpoint}_name") or ""),
        )
        for item in connectors
        for endpoint in ("source", "target")
    }
    stale_proxy_whitelist = [
        {
            "slide_index": key[0],
            "connector_name": key[1],
            "endpoint": key[2],
            "shape_name": key[3],
        }
        for key in proxy_whitelist
        if key not in used_proxy_keys
    ]
    segmented_path_objects = [
        {
            "slide_index": int(item["slide_index"]),
            "shape_name": str(item.get("connector_name") or item.get("shape_name") or ""),
        }
        for item in [*connectors, *ordinary_arrows]
        if SEGMENT_PATTERN.search(
            str(item.get("connector_name") or item.get("shape_name") or "")
        )
    ]

    expected_count = int(ledger["expected_connector_count"])
    actual_count = len(connectors)
    counts = {
        "expected_connector_count": expected_count,
        "connector_count": actual_count,
        "connector_count_mismatch_count": int(expected_count != actual_count),
        "vacuous_pass_count": int(expected_count > 0 and actual_count == 0),
        "malformed_ledger_entry_count": len(malformed_ledger),
        "duplicate_connector_name_count": len(duplicate_connector_names),
        "duplicate_ledger_connector_name_count": len(duplicate_ledger_names),
        "duplicate_logical_path_id_count": len(duplicate_logical_paths),
        "unconnected_endpoint_count": len(unconnected),
        "anchor_target_mismatch_count": len(mismatches),
        "unapproved_proxy_endpoint_count": len(unapproved_proxies),
        "invalid_proxy_whitelist_entry_count": len(invalid_proxy_whitelist),
        "stale_proxy_whitelist_entry_count": len(stale_proxy_whitelist),
        "geometry_mismatch_count": len(geometry_mismatches),
        "unnecessary_elbow_count": len(unnecessary_elbows),
        "non_axis_aligned_straight_connector_count": len(
            non_axis_aligned_straight_connectors
        ),
        "missing_geometry_input_count": len(missing_geometry_inputs),
        "unledgered_connector_count": len(unledgered_connectors),
        "ledger_missing_connector_count": len(missing_connectors),
        "non_connector_arrow_shape_count": len(ordinary_arrows),
        "unapproved_non_connector_arrow_shape_count": len(unapproved_ordinary_arrows),
        "invalid_ordinary_arrow_whitelist_entry_count": len(
            invalid_ordinary_whitelist
        ),
        "stale_ordinary_arrow_whitelist_count": len(stale_ordinary_whitelist),
        "segmented_path_object_count": len(segmented_path_objects),
    }
    informational_keys = {
        "expected_connector_count",
        "connector_count",
        "non_connector_arrow_shape_count",
    }
    blocker_keys = tuple(key for key in counts if key not in informational_keys)
    ok = all(counts[key] == 0 for key in blocker_keys)
    return {
        "ok": ok,
        "axis_tolerance_pt": 0.1,
        "counts": counts,
        "malformed_ledger_entries": malformed_ledger,
        "duplicate_connector_names": duplicate_connector_names,
        "duplicate_ledger_connector_names": duplicate_ledger_names,
        "duplicate_logical_paths": duplicate_logical_paths,
        "unconnected_endpoints": unconnected,
        "anchor_target_mismatches": mismatches,
        "unapproved_proxy_endpoints": unapproved_proxies,
        "invalid_proxy_whitelist_entries": invalid_proxy_whitelist,
        "stale_proxy_whitelist_entries": stale_proxy_whitelist,
        "geometry_mismatches": geometry_mismatches,
        "unnecessary_elbows": unnecessary_elbows,
        "non_axis_aligned_straight_connectors": non_axis_aligned_straight_connectors,
        "missing_geometry_inputs": missing_geometry_inputs,
        "unledgered_connectors": unledgered_connectors,
        "ledger_missing_connectors": missing_connectors,
        "ordinary_arrow_shapes": ordinary_arrows,
        "unapproved_ordinary_arrow_shapes": unapproved_ordinary_arrows,
        "invalid_ordinary_arrow_whitelist_entries": invalid_ordinary_whitelist,
        "stale_ordinary_arrow_whitelist": stale_ordinary_whitelist,
        "segmented_path_objects": segmented_path_objects,
        "connectors": connectors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail closed unless every logical connector is a native, anchored, "
            "ledgered, geometrically appropriate PowerPoint connector."
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    try:
        ledger = load_ledger(args.ledger.resolve())
        document = load_pptx(args.input.resolve())
        result = audit(document, ledger)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        result = {
            "ok": False,
            "fatal_error": str(exc),
            "counts": {"audit_fatal_error_count": 1},
        }

    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    sys.exit(main())
