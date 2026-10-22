#!/usr/bin/env python3
"""Audit named PPTX objects against a Hybrid Reconstruction visual ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}
HEX_RE = re.compile(r"^#?([0-9A-Fa-f]{6})$")


def normalize_rgb(value: str | None) -> str | None:
    if value is None:
        return None
    match = HEX_RE.match(value.strip())
    if not match:
        raise ValueError(f"invalid RGB value: {value!r}")
    return match.group(1).upper()


def rgb_distance(left: str, right: str) -> int:
    return max(
        abs(int(left[index : index + 2], 16) - int(right[index : index + 2], 16))
        for index in (0, 2, 4)
    )


def direct_child(parent: ET.Element | None, tag: str) -> ET.Element | None:
    if parent is None:
        return None
    return parent.find(tag, NS)


def color_from_fill(fill: ET.Element | None) -> str | None:
    if fill is None:
        return None
    srgb = fill.find("a:srgbClr", NS)
    return srgb.get("val", "").upper() if srgb is not None else None


def shape_record(shape: ET.Element, kind: str) -> dict:
    if kind == "shape":
        props = shape.find("p:spPr", NS)
    elif kind == "picture":
        props = shape.find("p:spPr", NS)
    else:
        props = shape.find("p:grpSpPr", NS)

    if kind == "picture":
        fill_mode = "image"
        fill_rgb = None
    elif direct_child(props, "a:noFill") is not None:
        fill_mode = "none"
        fill_rgb = None
    elif direct_child(props, "a:solidFill") is not None:
        fill_mode = "solid"
        fill_rgb = color_from_fill(direct_child(props, "a:solidFill"))
    elif direct_child(props, "a:gradFill") is not None:
        fill_mode = "gradient"
        fill_rgb = None
    elif direct_child(props, "a:blipFill") is not None:
        fill_mode = "image"
        fill_rgb = None
    else:
        fill_mode = "unspecified"
        fill_rgb = None

    line_fill = direct_child(direct_child(props, "a:ln"), "a:solidFill")
    line_rgb = color_from_fill(line_fill)

    text_rgbs = {
        value.upper()
        for value in (
            node.get("val")
            for node in shape.findall(".//a:rPr/a:solidFill/a:srgbClr", NS)
            + shape.findall(".//a:defRPr/a:solidFill/a:srgbClr", NS)
            + shape.findall(".//a:endParaRPr/a:solidFill/a:srgbClr", NS)
        )
        if value
    }

    return {
        "kind": kind,
        "fill_mode": fill_mode,
        "fill_rgb": fill_rgb,
        "line_rgb": line_rgb,
        "text_rgbs": sorted(text_rgbs),
    }


def slide_objects(xml_bytes: bytes) -> dict[str, list[dict]]:
    root = ET.fromstring(xml_bytes)
    found: dict[str, list[dict]] = {}
    for element, kind, name_path in (
        ("p:sp", "shape", "p:nvSpPr/p:cNvPr"),
        ("p:pic", "picture", "p:nvPicPr/p:cNvPr"),
        ("p:grpSp", "group", "p:nvGrpSpPr/p:cNvPr"),
    ):
        for shape in root.findall(f".//{element}", NS):
            name_node = shape.find(name_path, NS)
            if name_node is None:
                continue
            name = name_node.get("name")
            if name:
                found.setdefault(name, []).append(shape_record(shape, kind))
    return found


def compare_rgb(
    issues: list[dict],
    *,
    field: str,
    expected: str | None,
    actual: str | None,
    tolerance: int,
    context: dict,
) -> None:
    if expected is None:
        return
    if actual is None or rgb_distance(expected, actual) > tolerance:
        issues.append(
            {
                **context,
                "issue": f"{field}_mismatch",
                "expected": f"#{expected}",
                "actual": f"#{actual}" if actual else None,
                "tolerance": tolerance,
            }
        )


def audit(pptx_path: Path, ledger_path: Path) -> dict:
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    entries = ledger.get("objects")
    if not isinstance(entries, list) or not entries:
        raise ValueError("ledger must contain a non-empty 'objects' list")

    issues: list[dict] = []
    checked = 0
    slides: dict[int, dict[str, list[dict]]] = {}

    with zipfile.ZipFile(pptx_path) as archive:
        for entry in entries:
            slide_index = int(entry["slide_index"])
            if slide_index not in slides:
                slide_name = f"ppt/slides/slide{slide_index}.xml"
                try:
                    slides[slide_index] = slide_objects(archive.read(slide_name))
                except KeyError:
                    slides[slide_index] = {}
                    issues.append(
                        {
                            "slide_index": slide_index,
                            "issue": "slide_missing",
                            "shape_name": entry.get("shape_name"),
                        }
                    )

            shape_name = str(entry["shape_name"])
            matches = slides[slide_index].get(shape_name, [])
            context = {"slide_index": slide_index, "shape_name": shape_name}
            if len(matches) != 1:
                issues.append(
                    {
                        **context,
                        "issue": "shape_count_mismatch",
                        "expected": 1,
                        "actual": len(matches),
                    }
                )
                continue

            checked += 1
            actual = matches[0]
            expected_mode = entry.get("expected_fill_mode")
            if expected_mode and actual["fill_mode"] != expected_mode:
                issues.append(
                    {
                        **context,
                        "issue": "fill_mode_mismatch",
                        "expected": expected_mode,
                        "actual": actual["fill_mode"],
                    }
                )

            tolerance = int(entry.get("rgb_tolerance", ledger.get("rgb_tolerance", 3)))
            compare_rgb(
                issues,
                field="fill_rgb",
                expected=normalize_rgb(entry.get("expected_fill_rgb")),
                actual=actual["fill_rgb"],
                tolerance=tolerance,
                context=context,
            )
            compare_rgb(
                issues,
                field="line_rgb",
                expected=normalize_rgb(entry.get("expected_line_rgb")),
                actual=actual["line_rgb"],
                tolerance=tolerance,
                context=context,
            )

            expected_text = normalize_rgb(entry.get("expected_text_rgb"))
            if expected_text is not None and not any(
                rgb_distance(expected_text, color) <= tolerance
                for color in actual["text_rgbs"]
            ):
                issues.append(
                    {
                        **context,
                        "issue": "text_rgb_mismatch",
                        "expected": f"#{expected_text}",
                        "actual": [f"#{value}" for value in actual["text_rgbs"]],
                        "tolerance": tolerance,
                    }
                )

    result = {
        "ok": not issues,
        "input": str(pptx_path.resolve()),
        "ledger": str(ledger_path.resolve()),
        "expected_object_count": len(entries),
        "checked_object_count": checked,
        "issue_count": len(issues),
        "issues": issues,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    result = audit(args.input, args.ledger)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        sys.exit(2)
