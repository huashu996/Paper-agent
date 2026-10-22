#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys


def tokens(text: str) -> list[str]:
    text = text.lower()
    output = re.findall(r"[a-z][a-z0-9_+.-]{1,}|\d+(?:\.\d+)*", text)
    for seq in re.findall(r"[\u3400-\u9fff]{2,}", text):
        output.extend(seq[i:i+2] for i in range(len(seq)-1))
        output.extend(seq[i:i+3] for i in range(len(seq)-2))
    return list(dict.fromkeys(output))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=8)
    args = parser.parse_args()
    match = " OR ".join(f'"{token.replace(chr(34), "")}"' for token in tokens(args.query)[:30]) or '"research"'
    connection = sqlite3.connect(args.db)
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT chunk_id,title,source,content,bm25(chunks_fts,0.0,4.0,0.0,1.0,0.4) AS score FROM chunks_fts WHERE chunks_fts MATCH ? ORDER BY score LIMIT ?",
        (match, args.top_k),
    ).fetchall()
    print(json.dumps({"query": args.query, "results": [dict(row) for row in rows]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
