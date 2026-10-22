#!/usr/bin/env python3
"""Detect duplicate reference candidates from JSON/CSV/RIS/BibTeX exports."""

from __future__ import annotations

import argparse
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import validate_metadata


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def normalize_doi(doi: str) -> str:
    doi = doi.lower().strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi


def first_author(record: Dict[str, str]) -> str:
    author = record.get("author", "")
    return re.split(r";|\|", author)[0].strip().lower()


def make_id(index: int, record: Dict[str, str]) -> str:
    return record.get("record") or record.get("id") or str(index + 1)


def detect(records: List[Dict[str, str]], title_threshold: float) -> List[Dict[str, object]]:
    candidates: List[Dict[str, object]] = []
    seen_pairs: set[Tuple[str, str]] = set()
    for i, a in enumerate(records):
        for j in range(i + 1, len(records)):
            b = records[j]
            id_a, id_b = make_id(i, a), make_id(j, b)
            pair = tuple(sorted([id_a, id_b]))
            if pair in seen_pairs:
                continue
            reason = ""
            confidence = "candidate"
            doi_a, doi_b = normalize_doi(a.get("doi", "")), normalize_doi(b.get("doi", ""))
            title_a, title_b = normalize_title(a.get("title", "")), normalize_title(b.get("title", ""))
            ratio = SequenceMatcher(None, title_a, title_b).ratio() if title_a and title_b else 0.0
            if doi_a and doi_b and doi_a == doi_b:
                reason = "same DOI"
                confidence = "high"
            elif title_a and title_a == title_b:
                reason = "same normalized title"
                confidence = "high"
            elif ratio >= title_threshold:
                same_year = a.get("year") and a.get("year") == b.get("year")
                same_author = first_author(a) and first_author(a) == first_author(b)
                if same_year or same_author:
                    reason = f"title similarity {ratio:.3f}"
                    confidence = "medium"
            if reason:
                seen_pairs.add(pair)
                candidates.append(
                    {
                        "record_a": id_a,
                        "record_b": id_b,
                        "title_a": a.get("title", ""),
                        "title_b": b.get("title", ""),
                        "doi_a": a.get("doi", ""),
                        "doi_b": b.get("doi", ""),
                        "confidence": confidence,
                        "reason": reason,
                    }
                )
    return candidates


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Input JSON/CSV/RIS/BibTeX file.")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON report. Defaults to stdout.")
    parser.add_argument("--title-threshold", type=float, default=0.92)
    args = parser.parse_args(argv)

    try:
        records = validate_metadata.read_records(args.input)
        candidates = detect(records, args.title_threshold)
        report = {"input": str(args.input), "count": len(records), "duplicate_candidates": candidates}
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f"detect_duplicate_references.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

