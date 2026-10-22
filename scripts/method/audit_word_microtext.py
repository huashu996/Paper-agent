#!/usr/bin/env python3
"""Audit or remove verified 1 pt direct-text artifacts from a Word document.

An outer drawing-anchor run may be 1 pt while containing a normal-sized text
box and table.  Ancestor size never applies to nested text; tables and object
carrier runs are therefore protected, and only direct ``./w:t`` is eligible.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = NS["w"]


def qn(local: str) -> str:
    return f"{{{W}}}{local}"


def direct_text_nodes(run: etree._Element) -> list[etree._Element]:
    """Return only text owned by this run, never text nested in a drawing/text box."""
    return list(run.xpath("./w:t", namespaces=NS))


def is_protected_run(run: etree._Element) -> bool:
    """Protect real tables and object-carrier runs from recursive text deletion."""
    if run.xpath("ancestor::w:tbl", namespaces=NS):
        return True
    if run.xpath("ancestor::w:txbxContent[.//w:tbl]", namespaces=NS):
        return True
    return bool(run.xpath(".//w:drawing | .//w:pict | .//w:object | .//w:txbxContent", namespaces=NS))


def scan(root: etree._Element) -> list[dict[str, object]]:
    body = root.find("w:body", namespaces=NS)
    body_elements = list(body) if body is not None else []
    findings: list[dict[str, object]] = []
    for run in root.xpath("//w:r", namespaces=NS):
        if is_protected_run(run):
            continue
        nodes = direct_text_nodes(run)
        value = "".join(node.text or "" for node in nodes)
        if not value.strip():
            continue
        raw_sizes = run.xpath("./w:rPr/w:sz/@w:val | ./w:rPr/w:szCs/@w:val", namespaces=NS)
        sizes = [int(item) for item in raw_sizes if str(item).isdigit()]
        if not sizes or min(sizes) > 2:
            continue
        owner = run.xpath("ancestor::w:p[parent::w:body][1]", namespaces=NS)
        body_index = body_elements.index(owner[0]) if owner and owner[0] in body_elements else -1
        findings.append(
            {
                "body_index": body_index,
                "text": value,
                "half_point_sizes": raw_sizes,
                "hidden": bool(run.xpath("./w:rPr/w:vanish | ./w:rPr/w:webHidden", namespaces=NS)),
                "in_textbox": bool(run.xpath("ancestor::w:txbxContent", namespaces=NS)),
            }
        )
    return findings


def remove_blockers(root: etree._Element) -> list[dict[str, object]]:
    findings = scan(root)
    for run in list(root.xpath("//w:r", namespaces=NS)):
        if is_protected_run(run):
            continue
        nodes = direct_text_nodes(run)
        value = "".join(node.text or "" for node in nodes)
        raw_sizes = run.xpath("./w:rPr/w:sz/@w:val | ./w:rPr/w:szCs/@w:val", namespaces=NS)
        sizes = [int(item) for item in raw_sizes if str(item).isdigit()]
        if not value.strip() or not sizes or min(sizes) > 2:
            continue
        for node in nodes:
            parent = node.getparent()
            if parent is not None:
                parent.remove(node)
        protected = run.xpath(
            ".//w:drawing | .//w:pict | .//w:object | .//w:fldChar | .//w:instrText | .//w:br | .//w:tab",
            namespaces=NS,
        )
        if not protected and run.getparent() is not None:
            run.getparent().remove(run)
    return findings


def write_docx(source: Path, target: Path, document_xml: bytes) -> None:
    with zipfile.ZipFile(source) as src:
        package = {name: src.read(name) for name in src.namelist()}
    package["word/document.xml"] = document_xml
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as out:
        for name, data in package.items():
            out.writestr(name, data)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--fix", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    with zipfile.ZipFile(args.input) as zf:
        root = etree.fromstring(zf.read("word/document.xml"))
    before = scan(root)
    target = None
    if args.fix:
        remove_blockers(root)
        target = args.output or args.input.with_name(args.input.stem + "_no_microtext.docx")
        xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone="yes")
        write_docx(args.input, target, xml)
    after = scan(root)
    result = {
        "input": str(args.input),
        "output": str(target) if target else None,
        "blocking_before": len(before),
        "blocking_after": len(after),
        "removed": before if args.fix else [],
        "findings": after if args.fix else before,
    }
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    print(payload)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(payload, encoding="utf-8")
    return 0 if not after else 2


if __name__ == "__main__":
    raise SystemExit(main())
