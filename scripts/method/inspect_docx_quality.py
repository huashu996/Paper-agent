#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"

INDENT_KEYS = (
    "left",
    "leftChars",
    "start",
    "startChars",
    "firstLine",
    "firstLineChars",
    "hanging",
    "hangingChars",
)


def q(ns: str, name: str) -> str:
    return f"{{{ns}}}{name}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(
        node.text or ""
        for node in paragraph.iter()
        if node.tag in {q(W, "t"), q(M, "t")}
    )


def math_text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.iter(q(M, "t")))


def compact_length(value: str) -> int:
    return len(re.sub(r"\s+", "", value))


def paragraph_style(paragraph: ET.Element, default_style: str = "") -> str:
    properties = paragraph.find(q(W, "pPr"))
    style = properties.find(q(W, "pStyle")) if properties is not None else None
    return style.get(q(W, "val"), default_style) if style is not None else default_style


def count_instr(root: ET.Element, needle: str) -> int:
    return sum((node.text or "").count(needle) for node in root.iter(q(W, "instrText")))


def field_codes(root: ET.Element) -> list[str]:
    """Return complex and simple field instructions in begin-order."""
    active: list[dict[str, Any]] = []
    completed: list[tuple[int, str]] = []
    next_order = 0

    def visit(node: ET.Element) -> None:
        nonlocal next_order
        if node.tag == q(W, "fldSimple"):
            completed.append((next_order, node.get(q(W, "instr"), "")))
            next_order += 1

        if node.tag == q(W, "fldChar"):
            kind = node.get(q(W, "fldCharType"), "")
            if kind == "begin":
                active.append({"order": next_order, "parts": []})
                next_order += 1
            elif kind == "end" and active:
                item = active.pop()
                completed.append((int(item["order"]), "".join(item["parts"])))
        elif node.tag == q(W, "instrText") and active:
            active[-1]["parts"].append(node.text or "")

        for child in node:
            visit(child)

    visit(root)
    return [code for _, code in sorted(completed, key=lambda item: item[0])]


def style_model(styles_root: ET.Element | None) -> tuple[dict[str, dict[str, Any]], str]:
    model: dict[str, dict[str, Any]] = {}
    default_style = ""
    if styles_root is None:
        return model, default_style

    for style in styles_root.iter(q(W, "style")):
        if style.get(q(W, "type")) != "paragraph":
            continue
        style_id = style.get(q(W, "styleId"), "")
        if not style_id:
            continue
        if style.get(q(W, "default")) in {"1", "true", "on"}:
            default_style = style_id
        based = style.find(q(W, "basedOn"))
        properties = style.find(q(W, "pPr"))
        model[style_id] = {
            "based_on": based.get(q(W, "val"), "") if based is not None else "",
            "indent": indent_values(properties),
            "alignment": alignment_value(properties),
        }
    return model, default_style


def indent_values(properties: ET.Element | None) -> dict[str, int | str]:
    indent = properties.find(q(W, "ind")) if properties is not None else None
    values: dict[str, int | str] = {}
    if indent is None:
        return values
    for key in INDENT_KEYS:
        value = indent.get(q(W, key))
        if value is None:
            continue
        try:
            values[key] = int(value)
        except ValueError:
            values[key] = value
    return values


def alignment_value(properties: ET.Element | None) -> str | None:
    alignment = properties.find(q(W, "jc")) if properties is not None else None
    return alignment.get(q(W, "val")) if alignment is not None else None


def style_chain(style_id: str, styles: dict[str, dict[str, Any]]) -> list[str]:
    chain: list[str] = []
    seen: set[str] = set()
    current = style_id
    while current and current not in seen and current in styles:
        seen.add(current)
        chain.append(current)
        current = str(styles[current].get("based_on", ""))
    return list(reversed(chain))


def effective_paragraph_format(
    paragraph: ET.Element,
    styles: dict[str, dict[str, Any]],
    default_style: str,
) -> tuple[str, dict[str, int | str], str | None]:
    style_id = paragraph_style(paragraph, default_style)
    indent: dict[str, int | str] = {}
    alignment: str | None = None
    for item in style_chain(style_id, styles):
        indent.update(styles[item].get("indent", {}))
        if styles[item].get("alignment") is not None:
            alignment = str(styles[item]["alignment"])
    properties = paragraph.find(q(W, "pPr"))
    indent.update(indent_values(properties))
    direct_alignment = alignment_value(properties)
    if direct_alignment is not None:
        alignment = direct_alignment
    return style_id, indent, alignment


def indent_is_zero(values: dict[str, int | str]) -> bool:
    for key in INDENT_KEYS:
        value = values.get(key, 0)
        try:
            if int(value) != 0:
                return False
        except (TypeError, ValueError):
            return False
    return True


def has_ancestor(
    element: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    tag: str,
) -> bool:
    current = parent_map.get(element)
    while current is not None:
        if current.tag == tag:
            return True
        current = parent_map.get(current)
    return False


def bibliography_text(paragraphs: list[ET.Element]) -> str:
    texts = [paragraph_text(paragraph).strip() for paragraph in paragraphs]
    try:
        start = texts.index("参考文献")
        end = texts.index("作者简介", start + 1)
    except ValueError:
        return ""
    return "\n".join(texts[start + 1 : end])


def endnote_snapshot(root: ET.Element, paragraphs: list[ET.Element]) -> dict[str, Any]:
    codes = field_codes(root)
    main_pattern = re.compile(r"^\s*ADDIN\s+EN\.CITE(?!\.DATA)", re.I)
    data_pattern = re.compile(r"^\s*ADDIN\s+EN\.CITE\.DATA", re.I)
    reflist_pattern = re.compile(r"^\s*ADDIN\s+EN\.REFLIST", re.I)
    main = [code for code in codes if main_pattern.search(code)]
    data = [code for code in codes if data_pattern.search(code)]
    reflist = [code for code in codes if reflist_pattern.search(code)]
    endnote_codes = [code for code in codes if "ADDIN EN." in code.upper()]
    record_sequence = [
        int(value)
        for code in endnote_codes
        for value in re.findall(r"<(?:rec-number|RecNum)>\s*(\d+)\s*</", code)
    ]
    bookmarks = [
        node.get(q(W, "name"), "")
        for node in root.iter(q(W, "bookmarkStart"))
        if node.get(q(W, "name"), "").upper().startswith("ENREF_")
    ]
    hyperlinks = [
        node.get(q(W, "anchor"), "")
        for node in root.iter(q(W, "hyperlink"))
        if node.get(q(W, "anchor"), "").upper().startswith("ENREF_")
    ]
    bibliography = bibliography_text(paragraphs)
    return {
        "main_en_cite_count": len(main),
        "en_cite_data_count": len(data),
        "en_reflist_count": len(reflist),
        "endnote_field_code_sha256": sha256_text("\x1e".join(endnote_codes)),
        "main_field_code_sha256": sha256_text("\x1e".join(main)),
        "record_sequence": record_sequence,
        "bibliography_text_sha256": sha256_text(bibliography),
        "bibliography_characters": len(bibliography),
        "enref_bookmark_names": bookmarks,
        "enref_hyperlink_targets": hyperlinks,
    }


def compare_endnote(current: dict[str, Any], baseline: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "main_en_cite_count",
        "en_cite_data_count",
        "en_reflist_count",
        "endnote_field_code_sha256",
        "main_field_code_sha256",
        "record_sequence",
        "bibliography_text_sha256",
        "bibliography_characters",
        "enref_bookmark_names",
        "enref_hyperlink_targets",
    )
    checks = {key: current.get(key) == baseline.get(key) for key in keys}
    return {"passed": all(checks.values()), "checks": checks, "baseline": baseline}


def read_docx(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        bad_member = archive.testzip()
        root = ET.fromstring(archive.read("word/document.xml"))
        styles_root = (
            ET.fromstring(archive.read("word/styles.xml"))
            if "word/styles.xml" in archive.namelist()
            else None
        )
        headers = "\n".join(
            archive.read(name).decode("utf-8", errors="replace")
            for name in archive.namelist()
            if name.startswith("word/header") and name.endswith(".xml")
        )
        footers = "\n".join(
            archive.read(name).decode("utf-8", errors="replace")
            for name in archive.namelist()
            if name.startswith("word/footer") and name.endswith(".xml")
        )
    return {
        "bad_member": bad_member,
        "root": root,
        "styles_root": styles_root,
        "headers": headers,
        "footers": footers,
    }


def selected_scope(
    paragraphs: list[ET.Element],
    chapter_heading: str | None,
    next_heading: str,
) -> list[ET.Element]:
    if not chapter_heading:
        return paragraphs
    start = next(
        index
        for index, paragraph in enumerate(paragraphs)
        if paragraph_text(paragraph).strip() == chapter_heading
    )
    end = next(
        index
        for index in range(start + 1, len(paragraphs))
        if paragraph_text(paragraphs[index]).strip() == next_heading
    )
    return paragraphs[start:end]


def summarize_details(items: Iterable[dict[str, Any]], limit: int = 100) -> list[dict[str, Any]]:
    return list(items)[:limit]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect DOCX equations, body images, Word fields, and optional EndNote preservation"
    )
    parser.add_argument("docx")
    parser.add_argument("--baseline-docx")
    parser.add_argument("--chapter-heading")
    parser.add_argument("--next-heading", default="参考文献")
    parser.add_argument("--expected-equations", type=int)
    parser.add_argument("--max-inline-math-chars", type=int, default=28)
    parser.add_argument("--max-single-line-display-chars", type=int, default=55)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json-out")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    path = Path(args.docx).resolve()
    package = read_docx(path)
    root: ET.Element = package["root"]
    paragraphs = list(root.iter(q(W, "p")))
    scope = selected_scope(paragraphs, args.chapter_heading, args.next_heading)
    styles, default_style = style_model(package["styles_root"])
    parent_map = {child: parent for parent in root.iter() for child in parent}

    literal_latex = 0
    empty_math_runs = 0
    whitespace_math_runs = 0
    display_numbers: list[int] = []
    chapter_cites = 0
    unresolved_temporary = 0
    long_inline: list[dict[str, Any]] = []
    auto_wrap_risks: list[dict[str, Any]] = []
    equation_indent_issues: list[dict[str, Any]] = []
    body_image_indent_issues: list[dict[str, Any]] = []
    body_image_alignment_issues: list[dict[str, Any]] = []
    body_inline_image_count = 0

    paragraph_positions = {paragraph: index for index, paragraph in enumerate(paragraphs, 1)}
    for paragraph in scope:
        position = paragraph_positions[paragraph]
        text = paragraph_text(paragraph)
        literal_latex += len(re.findall(r"\\\(.+?\\\)|\{=tex\}", text))
        unresolved_temporary += len(
            re.findall(r"\{[^{}]+,\s*(?:19|20)\d{2}[a-z]?\s+#\d+", text)
        )
        chapter_cites += count_instr(paragraph, "ADDIN EN.CITE")

        style_id, indent, alignment = effective_paragraph_format(
            paragraph, styles, default_style
        )
        math_objects = list(paragraph.iter(q(M, "oMath")))
        is_display = style_id == "MTDisplayEquation" or any(
            True for _ in paragraph.iter(q(M, "oMathPara"))
        )

        if style_id == "MTDisplayEquation":
            display_numbers.extend(int(value) for value in re.findall(r"\(\d+-(\d+)\)", text))
            if not indent_is_zero(indent):
                equation_indent_issues.append(
                    {"paragraph": position, "style": style_id, "effective_indent": indent}
                )

            formula_characters = sum(compact_length(math_text(item)) for item in math_objects)
            explicit_rows = any(True for _ in paragraph.iter(q(M, "brk"))) or any(
                True for _ in paragraph.iter(q(M, "eqArr"))
            ) or any(True for _ in paragraph.iter(q(W, "br")))
            number_match = re.search(r"\((\d+)-(\d+)\)", text)
            if (
                formula_characters > args.max_single_line_display_chars
                and not explicit_rows
            ):
                auto_wrap_risks.append(
                    {
                        "paragraph": position,
                        "equation_number": number_match.group(0) if number_match else "",
                        "formula_characters": formula_characters,
                        "number_in_same_flowing_paragraph": bool(number_match),
                        "reason": "single long OMML has no explicit row break or equation array",
                    }
                )

        if not is_display and not has_ancestor(paragraph, parent_map, q(W, "tbl")):
            for item in math_objects:
                value = math_text(item)
                length = compact_length(value)
                if length > args.max_inline_math_chars:
                    long_inline.append(
                        {
                            "paragraph": position,
                            "math_characters": length,
                            "math_text": value[:160],
                            "paragraph_text": text[:200],
                        }
                    )

        for run in paragraph.iter(q(M, "r")):
            values = [node.text or "" for node in run.iter(q(M, "t"))]
            # A Word line break can legally occupy an OMML run without an m:t node.
            # It is structural content, not an empty/corrupt math run.
            has_structural_break = any(True for _ in run.iter(q(W, "br"))) or any(
                True for _ in run.iter(q(M, "brk"))
            )
            if has_structural_break and (not values or not "".join(values)):
                continue
            if not values or not "".join(values):
                empty_math_runs += 1
            elif not "".join(values).strip():
                whitespace_math_runs += 1

        if any(True for _ in paragraph.iter(q(WP, "inline"))):
            body_inline_image_count += 1
            if not indent_is_zero(indent):
                body_image_indent_issues.append(
                    {"paragraph": position, "style": style_id, "effective_indent": indent}
                )
            if alignment != "center":
                body_image_alignment_issues.append(
                    {"paragraph": position, "style": style_id, "effective_alignment": alignment}
                )

    equation_sequence_ok = (
        display_numbers == list(range(1, len(display_numbers) + 1))
        if display_numbers
        else args.expected_equations in (None, 0)
    )
    if args.expected_equations is not None:
        equation_sequence_ok = (
            equation_sequence_ok and len(display_numbers) == args.expected_equations
        )

    current_endnote = endnote_snapshot(root, paragraphs)
    endnote_preservation: dict[str, Any] | None = None
    if args.baseline_docx:
        baseline_path = Path(args.baseline_docx).resolve()
        baseline_package = read_docx(baseline_path)
        baseline_root: ET.Element = baseline_package["root"]
        baseline_paragraphs = list(baseline_root.iter(q(W, "p")))
        baseline_endnote = endnote_snapshot(baseline_root, baseline_paragraphs)
        endnote_preservation = compare_endnote(current_endnote, baseline_endnote)
        endnote_preservation["baseline_path"] = str(baseline_path)

    result: dict[str, Any] = {
        "path": str(path),
        "docx_zip_integrity": package["bad_member"] is None,
        "thresholds": {
            "max_inline_math_characters": args.max_inline_math_chars,
            "max_single_line_display_characters": args.max_single_line_display_chars,
            "note": "Static thresholds are triage gates; final fit must be verified in Word.",
        },
        "literal_inline_latex": literal_latex,
        "empty_math_runs": empty_math_runs,
        "whitespace_math_runs": whitespace_math_runs,
        "math_box_count": len(list(root.iter(q(M, "box")))),
        "math_phantom_count": len(list(root.iter(q(M, "phant")))),
        "display_equation_count": len(display_numbers),
        "display_equation_sequence_ok": equation_sequence_ok,
        "long_inline_math_count": len(long_inline),
        "long_inline_math": summarize_details(long_inline),
        "auto_wrap_risk_display_equation_count": len(auto_wrap_risks),
        "auto_wrap_risk_display_equations": summarize_details(auto_wrap_risks),
        "display_equation_indent_issue_count": len(equation_indent_issues),
        "display_equation_indent_issues": summarize_details(equation_indent_issues),
        "body_inline_image_count": body_inline_image_count,
        "body_image_indent_issue_count": len(body_image_indent_issues),
        "body_image_indent_issues": summarize_details(body_image_indent_issues),
        "body_image_alignment_issue_count": len(body_image_alignment_issues),
        "body_image_alignment_issues": summarize_details(body_image_alignment_issues),
        "chapter_en_cite_count": chapter_cites,
        "document_en_cite_count": count_instr(root, "ADDIN EN.CITE"),
        "document_en_reflist_count": count_instr(root, "ADDIN EN.REFLIST"),
        "unresolved_temporary_citations": unresolved_temporary,
        "endnote_snapshot": current_endnote,
        "endnote_preservation": endnote_preservation,
        "toc_field_count": count_instr(root, "TOC "),
        "hyperlink_count": len(list(root.iter(q(W, "hyperlink")))),
        "bookmark_count": len(list(root.iter(q(W, "bookmarkStart")))),
        "header_has_word_error": "错误!" in package["headers"] or "Error!" in package["headers"],
        "header_has_stale_sixth_chapter": "第六章 结论与展望" in package["headers"],
        "footer_page_field_count": package["headers"].count("PAGE")
        + package["footers"].count("PAGE"),
    }

    strict_checks = {
        "docx_zip_integrity": result["docx_zip_integrity"],
        "no_literal_latex": literal_latex == 0,
        "no_empty_math_runs": empty_math_runs == 0,
        "no_whitespace_math_runs": whitespace_math_runs == 0,
        "no_math_boxes": result["math_box_count"] == 0,
        "no_math_phantoms": result["math_phantom_count"] == 0,
        "equation_sequence": equation_sequence_ok,
        "no_long_inline_math": len(long_inline) == 0,
        "no_auto_wrap_risk_equations": len(auto_wrap_risks) == 0,
        "zero_equation_indent": len(equation_indent_issues) == 0,
        "zero_body_image_indent": len(body_image_indent_issues) == 0,
        "centered_body_images": len(body_image_alignment_issues) == 0,
        "no_temporary_citations": unresolved_temporary == 0,
        "no_header_word_error": not result["header_has_word_error"],
        "no_stale_header": not result["header_has_stale_sixth_chapter"],
        "endnote_preserved": (
            bool(endnote_preservation and endnote_preservation["passed"])
            if args.baseline_docx
            else True
        ),
    }
    result["strict_checks"] = strict_checks
    result["strict_passed"] = all(strict_checks.values())

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.json_out:
        Path(args.json_out).write_text(output, encoding="utf-8")
    if args.strict and not result["strict_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
