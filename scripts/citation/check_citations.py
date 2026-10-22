#!/usr/bin/env python3
"""Inspect a .docx for EndNote CWYW fields, temporary citations, and links."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Iterable


TEMP_CITATION_RE = re.compile(r"\{[^{}<>]+#[0-9]+[^{}<>]*\}")


def read_docx_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        with zf.open("word/document.xml") as f:
            return f.read().decode("utf-8", errors="replace")


def check(path: Path) -> dict:
    xml = read_docx_xml(path)
    doi_texts = re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", xml)
    url_texts = re.findall(r"https?://[^<\s\"']+", xml)
    return {
        "docx": str(path),
        "addin_en_cite": len(re.findall(r"ADDIN EN\.CITE", xml)),
        "addin_en_reflist": len(re.findall(r"ADDIN EN\.REFLIST", xml)),
        "temporary_citations": len(TEMP_CITATION_RE.findall(xml)),
        "hyperlink_elements": len(re.findall(r"<w:hyperlink", xml)),
        "bookmark_starts": len(re.findall(r"<w:bookmarkStart", xml)),
        "anchor_links": len(re.findall(r"w:anchor=", xml)),
        "doi_text_count": len(doi_texts),
        "url_text_count": len(url_texts),
        "sample_doi": sorted(set(doi_texts))[:10],
        "sample_url": sorted(set(url_texts))[:10],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = check(args.docx)
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f"check_citations.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

