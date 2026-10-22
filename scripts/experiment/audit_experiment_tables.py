#!/usr/bin/env python3
"""Audit source-to-thesis DOCX table fidelity after translation and restyling."""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import ZipFile

from lxml import etree


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
SUPERSCRIPT_TRANSLATION = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def xml_tables(docx_path, minimum_rows=2):
    with ZipFile(docx_path) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
    tables = root.xpath(".//w:tbl", namespaces=NS)
    return [
        table
        for table in tables
        if len(table.xpath("./w:tr", namespaces=NS)) >= minimum_rows
    ]


def table_rows(table):
    rows = []
    for row in table.xpath("./w:tr", namespaces=NS):
        values = []
        for cell in row.xpath("./w:tc", namespaces=NS):
            values.append("".join(cell.xpath(".//w:t/text()", namespaces=NS)).strip())
        rows.append(values)
    return rows


def bold_coordinates(table, header_rows):
    coordinates = []
    for row_index, row in enumerate(table.xpath("./w:tr", namespaces=NS)):
        if row_index < header_rows:
            continue
        for cell_index, cell in enumerate(row.xpath("./w:tc", namespaces=NS)):
            bold = cell.xpath(
                './/w:rPr/w:b[not(@w:val="0") and not(@w:val="false")]',
                namespaces=NS,
            )
            if bold:
                coordinates.append([row_index, cell_index])
    return coordinates


def normalize_source_text(text, replacements):
    text = re.sub(r"\[\s*\d+(?:\s*[-,;]\s*\d+)*\s*\]", "", text)
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def numeric_tokens(rows, replacements=(), source=False):
    text = " ".join(str(cell) for row in rows for cell in row)
    if source:
        text = normalize_source_text(text, replacements)
    text = text.translate(SUPERSCRIPT_TRANSLATION)
    return [
        token.replace(",", "")
        for token in re.findall(r"\d+(?:,\d{3})*(?:\.\d+)?", text)
    ]


def mark_count(rows):
    marks = ("×", "✕", "✖")
    return sum(
        str(cell).count(mark)
        for row in rows
        for cell in row
        for mark in marks
    )


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_replacements(values):
    replacements = []
    for value in values:
        if "=" not in value:
            raise ValueError(f"Replacement must be OLD=NEW: {value}")
        replacements.append(tuple(value.split("=", 1)))
    return replacements


def main():
    parser = argparse.ArgumentParser(
        description="Compare source and final DOCX experiment tables after translation."
    )
    parser.add_argument("source_docx", type=Path)
    parser.add_argument("final_docx", type=Path)
    parser.add_argument(
        "--header-rows",
        default="",
        help="Comma-separated header row counts per table; defaults to 1 for every table.",
    )
    parser.add_argument(
        "--source-table-json",
        type=Path,
        help="Optional JSON list with {'rows': [...]} records when source OOXML omits equation-object text.",
    )
    parser.add_argument(
        "--replacement",
        action="append",
        default=[],
        help="Source-only normalization OLD=NEW; may be repeated.",
    )
    parser.add_argument("--minimum-rows", type=int, default=2)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()

    replacements = parse_replacements(args.replacement)
    source_tables = xml_tables(args.source_docx, args.minimum_rows)
    final_tables = xml_tables(args.final_docx, args.minimum_rows)

    if args.source_table_json:
        raw = json.loads(args.source_table_json.read_text(encoding="utf-8"))
        source_rows = [entry["rows"] if isinstance(entry, dict) else entry for entry in raw]
    else:
        source_rows = [table_rows(table) for table in source_tables]
    final_rows = [table_rows(table) for table in final_tables]

    table_count = min(len(source_rows), len(final_rows), len(source_tables), len(final_tables))
    if args.header_rows:
        header_rows = [int(value) for value in args.header_rows.split(",")]
        if len(header_rows) != table_count:
            raise ValueError(
                f"--header-rows has {len(header_rows)} entries; expected {table_count}"
            )
    else:
        header_rows = [1] * table_count

    checks = []
    for index in range(table_count):
        source_numbers = numeric_tokens(source_rows[index], replacements, source=True)
        final_numbers = numeric_tokens(final_rows[index])
        source_bold = bold_coordinates(source_tables[index], header_rows[index])
        final_bold = bold_coordinates(final_tables[index], header_rows[index])
        checks.append(
            {
                "table": index + 1,
                "source_rows": len(source_rows[index]),
                "final_rows": len(final_rows[index]),
                "source_numeric_tokens": len(source_numbers),
                "final_numeric_tokens": len(final_numbers),
                "numeric_exact_order_match": source_numbers == final_numbers,
                "source_mark_count": mark_count(source_rows[index]),
                "final_mark_count": mark_count(final_rows[index]),
                "mark_count_match": mark_count(source_rows[index]) == mark_count(final_rows[index]),
                "source_bold_data_cells": source_bold,
                "final_bold_data_cells": final_bold,
                "bold_data_cells_match": source_bold == final_bold,
            }
        )

    report = {
        "source_docx": str(args.source_docx),
        "final_docx": str(args.final_docx),
        "source_sha256": sha256(args.source_docx),
        "final_sha256": sha256(args.final_docx),
        "source_table_count": len(source_rows),
        "final_table_count": len(final_rows),
        "table_count_match": len(source_rows) == len(final_rows),
        "tables": checks,
    }
    report["passed"] = (
        report["table_count_match"]
        and table_count == len(source_rows)
        and all(
            item["source_rows"] == item["final_rows"]
            and item["numeric_exact_order_match"]
            and item["mark_count_match"]
            and item["bold_data_cells_match"]
            for item in checks
        )
    )

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(output, encoding="utf-8")
    print(output)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
