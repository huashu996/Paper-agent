#!/usr/bin/env python3
"""Extract a rough writing-style profile from TXT, MD, or DOCX files."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable, List


CONNECTORS = [
    "however",
    "therefore",
    "moreover",
    "in addition",
    "on the other hand",
    "同时",
    "然而",
    "因此",
    "在此基础上",
    "进一步",
    "总体而言",
    "可以看出",
    "综上所述",
    "基于上述分析",
]


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    if suffix == ".docx":
        with zipfile.ZipFile(path) as zf:
            xml = zf.read("word/document.xml").decode("utf-8", errors="replace")
        xml = re.sub(r"</w:p>", "\n", xml)
        xml = re.sub(r"<[^>]+>", "", xml)
        return xml
    raise ValueError(f"Unsupported file type: {suffix}")


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[。！？.!?])\s*", text)
    return [p.strip() for p in parts if p.strip()]


def split_paragraphs(text: str) -> List[str]:
    return [p.strip() for p in re.split(r"\n+", text) if p.strip()]


def count_citations(text: str) -> int:
    patterns = [
        r"\[[0-9,\-\s]+\]",
        r"\([A-Z][A-Za-z-]+,\s*\d{4}[a-z]?\)",
        r"\{[^{}]+#[0-9]+[^{}]*\}",
    ]
    return sum(len(re.findall(p, text)) for p in patterns)


def profile(path: Path) -> dict:
    text = read_text(path)
    paragraphs = split_paragraphs(text)
    sentences = split_sentences(text)
    citation_count = count_citations(text)
    connectors = {c: len(re.findall(re.escape(c), text, flags=re.IGNORECASE)) for c in CONNECTORS}
    words = re.findall(r"[A-Za-z][A-Za-z\-]+|[\u4e00-\u9fff]{2,}", text)
    common_terms = Counter(w for w in words if len(w) >= 2).most_common(30)
    return {
        "source": str(path),
        "characters": len(text),
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "average_sentence_chars": round(sum(len(s) for s in sentences) / max(len(sentences), 1), 2),
        "average_paragraph_chars": round(sum(len(p) for p in paragraphs) / max(len(paragraphs), 1), 2),
        "citation_count": citation_count,
        "citations_per_paragraph": round(citation_count / max(len(paragraphs), 1), 3),
        "connectors": {k: v for k, v in connectors.items() if v},
        "common_terms": common_terms,
    }


def to_markdown(data: dict) -> str:
    lines = [
        "# Style Profile",
        "",
        f"- Source: `{data['source']}`",
        f"- Characters: {data['characters']}",
        f"- Paragraphs: {data['paragraph_count']}",
        f"- Sentences: {data['sentence_count']}",
        f"- Average sentence chars: {data['average_sentence_chars']}",
        f"- Average paragraph chars: {data['average_paragraph_chars']}",
        f"- Citation count: {data['citation_count']}",
        f"- Citations per paragraph: {data['citations_per_paragraph']}",
        "",
        "## Connectors",
        "",
    ]
    for key, value in data["connectors"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Common Terms", ""])
    for term, count in data["common_terms"]:
        lines.append(f"- {term}: {count}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--json", action="store_true", help="Write JSON instead of markdown.")
    args = parser.parse_args(argv)
    try:
        data = profile(args.input)
        text = json.dumps(data, ensure_ascii=False, indent=2) if args.json else to_markdown(data)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text + "\n", encoding="utf-8")
        else:
            print(text)
        return 0
    except Exception as exc:
        print(f"extract_style_profile.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

