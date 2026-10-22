from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from lxml import etree as ET


NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "v": "urn:schemas-microsoft-com:vml",
}
W = "{%s}" % NS["w"]


def text_of(node: ET._Element) -> str:
    return "".join(node.xpath('.//*[local-name()="t"]/text()'))


def digest(value: bytes | str) -> str:
    if isinstance(value, str):
        value = value.encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def semantic_class(tbl: ET._Element, rows: int, cols: int, text: str) -> str:
    has_math = bool(tbl.xpath(".//m:oMath", namespaces=NS))
    has_graphic = bool(tbl.xpath(".//w:drawing | .//w:pict | .//a:blip | .//v:imagedata", namespaces=NS))
    cover_markers = ("申请学位类别", "学位授予单位", "论文答辩日期", "学位授予日期", "答辩委员会主席")
    if has_math:
        return "formula_layout"
    if sum(marker in text for marker in cover_markers) >= 2:
        return "cover_layout"
    if has_graphic:
        return "figure_layout"
    if rows >= 2 and cols >= 2:
        return "data_table_candidate"
    return "unknown_layout"


def table_registry(path: Path) -> list[dict[str, object]]:
    registry: list[dict[str, object]] = []
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"DOCX ZIP CRC failure: {bad}")
        parts = [
            name
            for name in archive.namelist()
            if re.fullmatch(r"word/(document|header\d+|footer\d+|footnotes|endnotes)\.xml", name)
        ]
        for part in sorted(parts):
            root = ET.fromstring(archive.read(part))
            for index, tbl in enumerate(root.xpath(".//w:tbl", namespaces=NS), 1):
                rows_nodes = tbl.xpath("./w:tr", namespaces=NS)
                rows = len(rows_nodes)
                cols = max((len(row.xpath("./w:tc", namespaces=NS)) for row in rows_nodes), default=0)
                text = re.sub(r"\s+", " ", text_of(tbl)).strip()
                property_nodes = tbl.xpath("./w:tblPr | ./w:tblGrid | ./w:tr/w:trPr | ./w:tr/w:tc/w:tcPr", namespaces=NS)
                property_xml = b"".join(ET.tostring(node) for node in property_nodes)
                borders = []
                for node in tbl.xpath("./w:tblPr/w:tblBorders/* | .//w:tcPr/w:tcBorders/*", namespaces=NS):
                    borders.append(
                        {
                            "scope": ET.QName(node.getparent()).localname,
                            "edge": ET.QName(node).localname,
                            "value": node.get(W + "val", ""),
                            "size_eighth_pt": node.get(W + "sz", ""),
                        }
                    )
                registry.append(
                    {
                        "part": part,
                        "part_table_index": index,
                        "rows": rows,
                        "columns": cols,
                        "inside_textbox": bool(tbl.xpath("ancestor::w:txbxContent", namespaces=NS)),
                        "has_math": bool(tbl.xpath(".//m:oMath", namespaces=NS)),
                        "has_graphic": bool(tbl.xpath(".//w:drawing | .//w:pict", namespaces=NS)),
                        "class": semantic_class(tbl, rows, cols, text),
                        "text_preview": text[:160],
                        "text_sha256": digest(re.sub(r"\s+", "", text)),
                        "format_sha256": digest(property_xml),
                        "borders": borders,
                    }
                )
    return registry


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a non-mutating DOCX table-object registry.")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    registry = table_registry(args.docx)
    counts: dict[str, int] = {}
    for item in registry:
        key = str(item["class"])
        counts[key] = counts.get(key, 0) + 1
    payload = {
        "docx": str(args.docx.resolve()),
        "sha256": digest(args.docx.read_bytes()),
        "table_count": len(registry),
        "class_counts": counts,
        "warning": "data_table_candidate and unknown_layout require contextual review before edits",
        "tables": registry,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
