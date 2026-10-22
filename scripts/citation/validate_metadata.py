#!/usr/bin/env python3
"""Validate reference metadata exported as JSON, CSV, RIS, or BibTeX.

This script does not verify live DOI or publisher pages. It performs offline
completeness checks and emits explicit status labels for manual follow-up.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


REQUIRED_CORE = ["title", "year", "author"]
REQUIRED_SCHOLARLY = ["doi", "venue"]
REQUIRED_WEB = ["url", "access_date"]


def norm_key(key: str) -> str:
    key = key.strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "authors": "author",
        "journal": "venue",
        "conference": "venue",
        "booktitle": "venue",
        "publication": "venue",
        "publication_year": "year",
        "date": "year",
        "document_type": "type",
        "ref_type": "type",
        "record_number": "record",
        "url_link": "url",
        "accession_number": "accession",
        "pdf_attachment": "pdf",
    }
    return aliases.get(key, key)


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in record.items():
        out[norm_key(str(key))] = "" if value is None else str(value).strip()
    return out


def read_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        for key in ("records", "items", "references"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
        else:
            data = [data]
    if not isinstance(data, list):
        raise ValueError("JSON input must be a record object or a list of records.")
    return [normalize_record(x) for x in data if isinstance(x, dict)]


def read_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [normalize_record(row) for row in csv.DictReader(f)]


def read_ris(path: Path) -> List[Dict[str, Any]]:
    tag_map = {
        "AU": "author",
        "A1": "author",
        "PY": "year",
        "Y1": "year",
        "TI": "title",
        "T1": "title",
        "JO": "venue",
        "JF": "venue",
        "T2": "venue",
        "VL": "volume",
        "IS": "issue",
        "SP": "pages_start",
        "EP": "pages_end",
        "DO": "doi",
        "UR": "url",
        "PB": "publisher",
        "TY": "type",
        "AB": "abstract",
        "KW": "keywords",
        "Y2": "access_date",
        "L1": "pdf",
        "AN": "accession",
    }
    records: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if len(raw) < 6 or raw[2:6] != "  - ":
            continue
        tag, value = raw[:2], raw[6:].strip()
        if tag == "TY":
            current = {"type": value}
        elif tag == "ER":
            if current:
                if current.get("pages_start") or current.get("pages_end"):
                    current["pages"] = "-".join(x for x in [current.get("pages_start", ""), current.get("pages_end", "")] if x)
                records.append(normalize_record(current))
            current = {}
        else:
            key = tag_map.get(tag)
            if key:
                if key in current and value:
                    current[key] = f"{current[key]}; {value}"
                else:
                    current[key] = value
    return records


def read_bibtex(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    entries = re.split(r"(?=@\w+\s*\{)", text)
    records: List[Dict[str, Any]] = []
    for entry in entries:
        if not entry.strip().startswith("@"):
            continue
        record: Dict[str, Any] = {}
        m_type = re.match(r"@(\w+)\s*\{", entry)
        if m_type:
            record["type"] = m_type.group(1)
        for key, value in re.findall(r"(\w+)\s*=\s*[\{\"]([^{}\"]+)[\}\"]", entry):
            record[norm_key(key)] = value.strip()
        records.append(normalize_record(record))
    return records


def read_records(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        return read_json(path)
    if suffix in {".csv", ".tsv"}:
        return read_csv(path)
    if suffix == ".ris":
        return read_ris(path)
    if suffix in {".bib", ".bibtex"}:
        return read_bibtex(path)
    raise ValueError(f"Unsupported input extension: {suffix}")


def is_web_record(record: Dict[str, Any]) -> bool:
    typ = record.get("type", "").lower()
    return typ in {"web page", "webpage", "elec", "electronic article", "online"} or bool(record.get("url") and not record.get("doi"))


def validate(record: Dict[str, Any]) -> Dict[str, Any]:
    missing: List[str] = []
    for field in REQUIRED_CORE:
        if not record.get(field):
            missing.append(field)
    if is_web_record(record):
        for field in REQUIRED_WEB:
            if not record.get(field):
                missing.append(field)
    else:
        for field in REQUIRED_SCHOLARLY:
            if not record.get(field):
                missing.append(field)

    status: List[str] = []
    if missing:
        status.append("[Metadata incomplete]")
    pub_status = record.get("publication_status", "").lower()
    typ = record.get("type", "").lower()
    if any(x in typ for x in ("preprint", "arxiv")) or "requires verification" in pub_status:
        status.append("[Publication status requires verification]")

    return {
        "record": record.get("record", ""),
        "title": record.get("title", ""),
        "year": record.get("year", ""),
        "doi": record.get("doi", ""),
        "url": record.get("url", ""),
        "type": record.get("type", ""),
        "missing_fields": missing,
        "status": status,
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Input JSON/CSV/RIS/BibTeX file.")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON report. Defaults to stdout.")
    args = parser.parse_args(argv)

    try:
        records = read_records(args.input)
        report = {"input": str(args.input), "count": len(records), "records": [validate(r) for r in records]}
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f"validate_metadata.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

