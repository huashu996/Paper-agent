#!/usr/bin/env python3
"""Audit PowerPoint connector endpoint identities against visible-shape expectations."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"p": P_NS, "a": A_NS}


def _c_nv_pr(element: ET.Element) -> ET.Element | None:
    paths = (
        "./p:nvSpPr/p:cNvPr",
        "./p:nvPicPr/p:cNvPr",
        "./p:nvGraphicFramePr/p:cNvPr",
        "./p:nvGrpSpPr/p:cNvPr",
        "./p:nvCxnSpPr/p:cNvPr",
    )
    for path in paths:
        result = element.find(path, NS)
        if result is not None:
            return result
    return None


def _slide_index(name: str) -> int:
    match = re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name)
    if not match:
        raise ValueError(f"Not a slide XML path: {name}")
    return int(match.group(1))


def load_slide_connectors(pptx: Path) -> list[dict[str, Any]]:
    connectors: list[dict[str, Any]] = []
    with zipfile.ZipFile(pptx) as archive:
        slide_names = sorted(
            (
                name
                for name in archive.namelist()
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
            ),
            key=_slide_index,
        )
        for slide_name in slide_names:
            slide_number = _slide_index(slide_name)
            root = ET.fromstring(archive.read(slide_name))
            id_to_name: dict[str, str] = {}
            for tag in ("sp", "pic", "graphicFrame", "grpSp", "cxnSp"):
                for element in root.findall(f".//p:{tag}", NS):
                    c_nv_pr = _c_nv_pr(element)
                    if c_nv_pr is not None:
                        id_to_name[str(c_nv_pr.get("id"))] = str(
                            c_nv_pr.get("name") or ""
                        )

            for connector in root.findall(".//p:cxnSp", NS):
                c_nv_pr = _c_nv_pr(connector)
                connector_name = str(c_nv_pr.get("name") or "") if c_nv_pr is not None else ""
                properties = connector.find("./p:nvCxnSpPr/p:cNvCxnSpPr", NS)
                start = properties.find("./a:stCxn", NS) if properties is not None else None
                end = properties.find("./a:endCxn", NS) if properties is not None else None
                start_id = str(start.get("id")) if start is not None else None
                end_id = str(end.get("id")) if end is not None else None
                connectors.append(
                    {
                        "slide_index": slide_number,
                        "connector_name": connector_name,
                        "source_id": start_id,
                        "source_name": id_to_name.get(start_id or ""),
                        "target_id": end_id,
                        "target_name": id_to_name.get(end_id or ""),
                    }
                )
    return connectors


def load_ledger(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("Connector ledger must be a JSON object.")
    connectors = payload.get("connectors", [])
    whitelist = payload.get("proxy_whitelist", [])
    if not isinstance(connectors, list) or not isinstance(whitelist, list):
        raise ValueError("Ledger connectors and proxy_whitelist must be arrays.")
    return payload


def is_proxy(name: str | None, prefixes: list[str]) -> bool:
    if not name:
        return False
    upper_name = name.upper()
    return any(upper_name.startswith(prefix.upper()) for prefix in prefixes)


def audit(
    connectors: list[dict[str, Any]],
    ledger: dict[str, Any] | None,
    proxy_prefixes: list[str],
) -> dict[str, Any]:
    actual_by_key: dict[tuple[int, str], dict[str, Any]] = {}
    duplicate_connector_names: list[dict[str, Any]] = []
    for item in connectors:
        key = (int(item["slide_index"]), str(item["connector_name"]))
        if key in actual_by_key:
            duplicate_connector_names.append(
                {"slide_index": key[0], "connector_name": key[1]}
            )
        actual_by_key[key] = item

    ledger_by_key: dict[tuple[int, str], dict[str, Any]] = {}
    whitelist_by_key: dict[tuple[int, str, str, str], dict[str, Any]] = {}
    if ledger is not None:
        for item in ledger.get("connectors", []):
            key = (int(item["slide_index"]), str(item["connector_name"]))
            ledger_by_key[key] = item
        for item in ledger.get("proxy_whitelist", []):
            endpoint = str(item.get("endpoint") or "").lower()
            if endpoint not in {"source", "target"}:
                raise ValueError(
                    f"Invalid proxy whitelist endpoint for {item.get('shape_name')}: {endpoint}"
                )
            key = (
                int(item["slide_index"]),
                str(item["connector_name"]),
                endpoint,
                str(item["shape_name"]),
            )
            whitelist_by_key[key] = item

    unconnected: list[dict[str, Any]] = []
    proxy_endpoints: list[dict[str, Any]] = []
    unapproved_proxies: list[dict[str, Any]] = []
    mismatches: list[dict[str, Any]] = []
    unledgered: list[dict[str, Any]] = []

    for item in connectors:
        slide_index = int(item["slide_index"])
        connector_name = str(item["connector_name"])
        key = (slide_index, connector_name)
        expected = ledger_by_key.get(key)
        if ledger is not None and expected is None:
            unledgered.append(
                {"slide_index": slide_index, "connector_name": connector_name}
            )

        for endpoint in ("source", "target"):
            actual_name = item.get(f"{endpoint}_name")
            if not actual_name:
                unconnected.append(
                    {
                        "slide_index": slide_index,
                        "connector_name": connector_name,
                        "endpoint": endpoint,
                    }
                )
                continue

            whitelist_item = whitelist_by_key.get(
                (slide_index, connector_name, endpoint, str(actual_name))
            )
            effective_name = str(actual_name)
            if is_proxy(str(actual_name), proxy_prefixes):
                proxy_record = {
                    "slide_index": slide_index,
                    "connector_name": connector_name,
                    "endpoint": endpoint,
                    "shape_name": actual_name,
                }
                proxy_endpoints.append(proxy_record)
                if whitelist_item is None:
                    unapproved_proxies.append(proxy_record)
                else:
                    effective_name = str(
                        whitelist_item.get("owner_shape") or actual_name
                    )

            if expected is not None:
                expected_name = expected.get(f"expected_{endpoint}")
                if expected_name and str(expected_name) != effective_name:
                    mismatches.append(
                        {
                            "slide_index": slide_index,
                            "connector_name": connector_name,
                            "endpoint": endpoint,
                            "expected": str(expected_name),
                            "actual": str(actual_name),
                            "effective_actual": effective_name,
                        }
                    )

    missing_ledger_connectors = [
        {"slide_index": key[0], "connector_name": key[1]}
        for key in ledger_by_key
        if key not in actual_by_key
    ]

    counts = {
        "connector_count": len(connectors),
        "unconnected_endpoint_count": len(unconnected),
        "proxy_endpoint_count": len(proxy_endpoints),
        "unapproved_proxy_endpoint_count": len(unapproved_proxies),
        "anchor_target_mismatch_count": len(mismatches),
        "unledgered_connector_count": len(unledgered),
        "ledger_missing_connector_count": len(missing_ledger_connectors),
        "duplicate_connector_name_count": len(duplicate_connector_names),
    }
    blocker_keys = (
        "unconnected_endpoint_count",
        "unapproved_proxy_endpoint_count",
        "anchor_target_mismatch_count",
        "unledgered_connector_count",
        "ledger_missing_connector_count",
        "duplicate_connector_name_count",
    )
    ok = all(counts[key] == 0 for key in blocker_keys)
    return {
        "ok": ok,
        "ledger_supplied": ledger is not None,
        "counts": counts,
        "unconnected_endpoints": unconnected,
        "proxy_endpoints": proxy_endpoints,
        "unapproved_proxy_endpoints": unapproved_proxies,
        "anchor_target_mismatches": mismatches,
        "unledgered_connectors": unledgered,
        "ledger_missing_connectors": missing_ledger_connectors,
        "duplicate_connector_names": duplicate_connector_names,
        "connectors": connectors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit PPTX connector endpoint identities and reject unapproved "
            "ANCHOR_/PROXY_ targets."
        )
    )
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument(
        "--proxy-prefix",
        action="append",
        dest="proxy_prefixes",
        help="Proxy-name prefix. May be repeated.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    pptx = args.input.resolve()
    if not pptx.is_file():
        raise SystemExit(f"Input PPTX does not exist: {pptx}")
    if pptx.suffix.lower() != ".pptx":
        raise SystemExit(f"Input must be .pptx: {pptx}")

    prefixes = args.proxy_prefixes or ["ANCHOR_", "PROXY_", "BORDER_PROXY_"]
    ledger = load_ledger(args.ledger.resolve() if args.ledger else None)
    result = audit(load_slide_connectors(pptx), ledger, prefixes)
    result["input"] = str(pptx)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
