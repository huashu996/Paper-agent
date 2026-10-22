#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
SUPPORTED = {".pdf", ".docx", ".md", ".txt", ".tex", ".bib", ".ris"}


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="ignore")).hexdigest()


def normalize(text: str) -> str:
    text = text.replace("\x00", " ").replace("\r", "\n")
    text = re.sub(r"-\n(?=[a-z])", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n[ \t]+", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_pdf(path: Path) -> tuple[str, str]:
    try:
        cp = subprocess.run(
            ["pdftotext", "-enc", "UTF-8", "-layout", str(path), "-"],
            capture_output=True, timeout=300,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "", "failed"
    if not cp.stdout:
        return "", "failed"
    return normalize(cp.stdout.decode("utf-8", errors="replace")), "ok"


def extract_docx(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as zf:
            root = ET.fromstring(zf.read("word/document.xml"))
    except Exception:
        return "", "failed"
    paragraphs = []
    for p in root.iter(q(W, "p")):
        parts = []
        for n in p.iter():
            if n.tag in {q(W, "t"), q(M, "t")} and n.text:
                parts.append(n.text)
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    return normalize("\n\n".join(paragraphs)), "ok"


def extract(path: Path) -> tuple[str, str]:
    if path.suffix.lower() == ".pdf":
        return extract_pdf(path)
    if path.suffix.lower() == ".docx":
        return extract_docx(path)
    try:
        return normalize(path.read_text(encoding="utf-8", errors="replace")), "ok"
    except Exception:
        return "", "failed"


def collect_sources(inputs: list[str]) -> list[Path]:
    files = []
    for value in inputs:
        path = Path(value).expanduser().resolve()
        if path.is_file() and path.suffix.lower() in SUPPORTED:
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED)
    return sorted(set(files), key=lambda p: str(p).lower())


def is_heading(line: str) -> bool:
    line = re.sub(r"\s+", " ", line.strip())
    if not 2 <= len(line) <= 160:
        return False
    patterns = [
        r"^第[一二三四五六七八九十百\d]+[章节篇]",
        r"^\d+(?:\.\d+){0,4}\s+\S+",
        r"^[一二三四五六七八九十]+[、．.]\s*\S+",
        r"^(?:[IVX]+\.|[A-Z]\.)\s+\S+",
        r"^(?:ABSTRACT|INTRODUCTION|RELATED WORK|METHODS?|METHODOLOGY|RESULTS?|CONCLUSION|REFERENCES)$",
    ]
    return any(re.match(pattern, line, re.I) for pattern in patterns)


def sections(text: str, fallback: str) -> list[tuple[str, str]]:
    result, current, acc = [], fallback, []
    for raw in text.splitlines():
        line = raw.strip()
        if is_heading(line):
            body = normalize("\n".join(acc))
            if len(body) >= 120:
                result.append((current, body))
            current, acc = line, []
        else:
            acc.append(raw)
    body = normalize("\n".join(acc))
    if len(body) >= 120:
        result.append((current, body))
    return result or ([(fallback, text)] if len(text) >= 120 else [])


def chunks(text: str, target: int, maximum: int, overlap: int) -> list[str]:
    paragraphs = [normalize(p) for p in re.split(r"\n\s*\n", text) if len(normalize(p)) >= 20]
    if not paragraphs:
        paragraphs = [normalize(p) for p in text.splitlines() if len(normalize(p)) >= 20]
    output, current, length = [], [], 0
    for paragraph in paragraphs:
        units = re.split(r"(?<=[。！？.!?])\s*", paragraph) if len(paragraph) > maximum else [paragraph]
        for unit in units:
            if not unit:
                continue
            if current and length + len(unit) > maximum:
                block = "\n\n".join(current).strip()
                if len(block) >= 120:
                    output.append(block)
                tail = block[-overlap:] if overlap else ""
                current, length = ([tail, unit] if tail else [unit]), len(tail) + len(unit)
            else:
                current.append(unit)
                length += len(unit)
            if length >= target:
                block = "\n\n".join(current).strip()
                output.append(block)
                tail = block[-overlap:] if overlap else ""
                current, length = ([tail] if tail else []), len(tail)
    block = "\n\n".join(current).strip()
    if len(block) >= 120:
        output.append(block)
    return output


def formula_candidates(text: str) -> list[str]:
    found = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if 8 <= len(line) <= 320 and ("=" in line or "∑" in line or "argmin" in line.lower() or "arg max" in line.lower()):
            found.append(line)
        if len(found) >= 10:
            break
    return found


def search_tokens(text: str) -> str:
    text = text.lower()
    tokens = re.findall(r"[a-z][a-z0-9_+.-]{1,}|\d+(?:\.\d+)*", text)
    for seq in re.findall(r"[\u3400-\u9fff]{2,}", text):
        if len(seq) <= 12:
            tokens.append(seq)
        tokens.extend(seq[i:i+2] for i in range(len(seq)-1))
        tokens.extend(seq[i:i+3] for i in range(len(seq)-2))
    return " ".join(tokens)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reusable semantic research RAG index")
    parser.add_argument("--name", required=True)
    parser.add_argument("--sources", nargs="+", required=True)
    parser.add_argument("--out", required=True, help="Exact output directory for the named knowledge base")
    parser.add_argument("--target", type=int, default=1400)
    parser.add_argument("--maximum", type=int, default=2200)
    parser.add_argument("--overlap", type=int, default=180)
    parser.add_argument("--force", action="store_true", help="Overwrite generated files only when manifest name matches")
    args = parser.parse_args()

    out = Path(args.out).expanduser().resolve()
    manifest_path = out / f"{args.name}.manifest.json"
    if out.exists() and any(out.iterdir()):
        if not args.force:
            raise SystemExit(f"Output is not empty: {out}. Use --force only for the same named knowledge base.")
        if manifest_path.exists():
            old = json.loads(manifest_path.read_text(encoding="utf-8"))
            if old.get("name") != args.name:
                raise SystemExit("Refusing to overwrite a different named knowledge base")

    directories = {name: out / name for name in ("documents", "metadata", "formulas", "index", "summary")}
    for directory in directories.values():
        directory.mkdir(parents=True, exist_ok=True)

    source_paths = collect_sources(args.sources)
    documents, knowledge, formulas = [], [], []
    seen = set()
    for index, path in enumerate(source_paths, 1):
        text, status = extract(path)
        stat = path.stat()
        source_id = "D" + sha(str(path))[:14]
        title = path.stem.replace("_", " ")
        years = re.findall(r"\b(?:19|20)\d{2}\b", text[:20000])
        doc = {
            "document_id": source_id, "title": title, "authors": "",
            "year": int(years[0]) if years else None, "source": str(path),
            "source_type": path.suffix.lower().lstrip("."), "extraction_status": status,
            "content_hash": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": stat.st_size, "characters": len(text),
        }
        documents.append(doc)
        for heading, section in sections(text, title):
            for part, content in enumerate(chunks(section, args.target, args.maximum, args.overlap), 1):
                digest = sha(content)
                if digest in seen:
                    continue
                seen.add(digest)
                candidates = formula_candidates(content)
                chunk_id = "C" + digest[:16]
                record = {
                    "knowledge_base": args.name, "chunk_id": chunk_id,
                    "document_id": source_id, "title": heading,
                    "heading_path": [heading], "source": str(path),
                    "keywords": [], "content": content, "formulas": candidates,
                    "variable_explanations": {}, "chunking": "heading_then_paragraph",
                    "part": part,
                }
                knowledge.append(record)
                for number, candidate in enumerate(candidates, 1):
                    formulas.append({
                        "id": f"{chunk_id}-F{number}", "chunk_id": chunk_id,
                        "source": str(path), "heading": heading,
                        "raw_expression": candidate, "context": content[:800],
                        "quality": "candidate_requires_source_verification",
                    })
        if index % 10 == 0 or index == len(source_paths):
            print(f"processed {index}/{len(source_paths)} sources; chunks={len(knowledge)}", flush=True)

    write_jsonl(directories["documents"] / "chunks.jsonl", knowledge)
    write_jsonl(directories["metadata"] / "documents.jsonl", documents)
    write_jsonl(directories["formulas"] / "formula_candidates.jsonl", formulas)

    safe_name = re.sub(r"[^0-9A-Za-z._-]+", "_", args.name).strip("_") or "knowledge_base"
    db_path = directories["index"] / f"{safe_name}.sqlite3"
    if db_path.exists():
        db_path.unlink()
    connection = sqlite3.connect(db_path)
    connection.execute("CREATE VIRTUAL TABLE chunks_fts USING fts5(chunk_id UNINDEXED,title,source UNINDEXED,content,tokenized,tokenize='unicode61 remove_diacritics 2')")
    connection.executemany(
        "INSERT INTO chunks_fts(chunk_id,title,source,content,tokenized) VALUES(?,?,?,?,?)",
        [(r["chunk_id"], r["title"], r["source"], r["content"], search_tokens(r["title"] + " " + r["content"])) for r in knowledge],
    )
    connection.execute("CREATE TABLE manifest(name TEXT PRIMARY KEY,value TEXT)")
    connection.executemany("INSERT INTO manifest(name,value) VALUES(?,?)", {
        "name": args.name, "source_count": str(len(documents)), "chunk_count": str(len(knowledge)),
        "index_type": "SQLite FTS5 with Chinese bigram/trigram tokens",
    }.items())
    connection.commit()
    connection.close()

    manifest = {
        "name": args.name, "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source_count": len(documents), "chunk_count": len(knowledge),
        "formula_candidate_count": len(formulas), "index": str(db_path.relative_to(out)),
        "chunking": {"target": args.target, "maximum": args.maximum, "overlap": args.overlap},
        "retrieval": "SQLite FTS5 lexical index; dense embeddings not generated",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (directories["summary"] / "coverage.md").write_text(
        f"# {args.name}\n\n- Sources: {len(documents)}\n- Chunks: {len(knowledge)}\n- Formula candidates: {len(formulas)}\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()

