# Method, RAG, Word, Equation, and Preservation Workflow

## Contents
- Core method workflow
- Execution checklist
- RAG schema and evidence ledger
- Word, equation, EndNote, and preservation quality

<!-- BEGIN SOURCE: method-workflow.md -->
## Method-SKILL

### Objective

Produce a verifiable doctoral-thesis chapter from heterogeneous research materials. Preserve source files and unrelated document content. Treat the RAG index, framework analysis, editable mathematics, Word formatting, citations, and final validation as one workflow.

### Non-negotiable instruction precedence and preservation

Apply the user's newest approved instruction before earlier answers, this skill's defaults, or a convenient implementation path. Record the active constraints in the build log before editing. Treat phrases such as “不管文献”, “不新增文献”, “保持现有引用和排版”, “不要刷新 EndNote”, “不重新生成图片”, and “不要生成 PDF” as hard freezes, not preferences.

Never introduce a forbidden mutation merely because the current pipeline depends on it. Redesign the pipeline or stop with a precise blocker. Do not reinterpret “preserve” as “recreate something visually similar”. Preserve the underlying field, bookmark, hyperlink, style, and relationship structures named by the user.

### Required five-question interview

Ask the following five questions one at a time. Briefly confirm each captured answer before asking the next. If the user already supplied an answer, capture it and move to the next unanswered question. Do not draft the chapter until all five are resolved.

1. Ask for the reusable RAG knowledge-base name and approved source scope.
   - Accept folders, EndNote libraries/groups, PDFs, Word files, BibTeX/RIS, DOI lists, websites, notes, and exclusions.
   - Ask whether to build a new index or update/reuse an existing named index.
2. Ask for the user's research-work framework.
   - Request the framework file or a description of research problems, technical route, chapter relationships, contributions, and downstream interfaces.
3. Ask for language style and formatting confirmation.
   - Capture language, academic tone, university/journal specification, template file, output format, heading convention, citation style, and whether an exemplar thesis should guide prose rhythm.
4. Ask for the existing body draft or principal formulas and the target length.
   - Clarify whether the page target is newly added body pages or final body pages. Exclude bibliography pages by default.
5. Ask whether to cite literature and whether EndNote must be truly linked to the body.
   - Distinguish real EndNote CWYW fields, Word citations, and manual numbering.
   - Ask which EndNote library/group to use and whether Ctrl+click citation-to-bibliography navigation is additionally required.

Record the five answers in the build log. When an answer materially changes scope, confirm it before continuing.

### Phase 1: Set up and inventory

Create `build/paper-agent/<timestamp>/method/` near the target file. Store extracted text, copied databases, scripts, backups, logs, screenshots, previews, and validation JSON there. Keep the project root limited to source files and user-facing outputs.

Inventory every approved source. Detect duplicates and unreadable/encrypted/scanned files. Never alter originals. Report sources that cannot be text-extracted rather than silently omitting them.

Read [method-and-word-workflow.md](method-and-word-workflow.md) before beginning substantive work.

### Phase 2: Build or reuse the named RAG knowledge base

Read [method-and-word-workflow.md](method-and-word-workflow.md). Build a reusable knowledge base named exactly as the user requested. Prefer incremental reuse only when the manifest name, source fingerprints, schema, and approved scope match.

Use `../scripts/method/build_method_rag.py` when local PDF/DOCX/Markdown/text sources fit its interface. Otherwise preserve the same output schema with a more suitable extractor.

Segment by detected headings and semantic paragraphs, not by fixed pages. Preserve formula context and heading paths. Extract document metadata, problem definition, framework, state and motion models, observation and residual models, optimization, contributions, limitations, formulas, symbol explanations, and application conditions when present.

Create `documents/`, `metadata/`, `formulas/`, `index/`, and `summary/`, plus a manifest containing the knowledge-base name and retrieval instructions. Test at least three representative queries before relying on the index.

### Phase 3: Map the research framework

Analyze the framework before drafting. Produce a chapter-interface map that states:

- the thesis-level problem and chapter purpose;
- the technical progression across chapters;
- which states, coordinate frames, map elements, observations, and residuals this chapter must define;
- what later chapters consume from this chapter;
- what content is excluded, such as experiments or results.

Organize the chapter around research logic and technical routes, not one paper per paragraph. Use references to support concrete claims rather than to replace synthesis.

Treat the approved writing guide as the highest authority for thesis logic, headings, method boundaries, and principal formulas. When the draft, code, or other resources conflict with it, revise toward the guide. Use the closest papers only to expand derivations, formula explanations, and necessary details without overriding the guide. Treat code as an aid to understanding, not proof that every described module was implemented; never fabricate implementation status, experiments, or results.

### Phase 3A: Learn the formula style from the closest papers

Before drafting formulas, read the writing guide and the one to three most relevant papers in the approved `resource/` scope for that chapter. Treat code only as an implementation aid. Build a formula-style contract that records:

- the source and page for each principal model;
- the source's state, observation, residual, and optimization notation;
- which relations are actual paper equations and which details remain prose or algorithms;
- the typical equation length, nesting depth, and multi-line layout;
- the exact role of intensity, uncertainty, robust weights, thresholds, and auxiliary variables.

Follow the closest paper's mathematical abstraction and compactness unless the writing guide explicitly overrides it. Never infer a different intensity normalization, confidence product, residual, or weighting formula from code or general knowledge. If the approved sources do not determine a formula, omit it or mark it for confirmation; do not invent one.

### Phase 4: Draft the chapter

Inspect the target document's styles, numbering, sections, page setup, paragraph spacing, and existing bibliography before editing. Make a timestamped backup.

Write formal, cumulative doctoral prose. Define every symbol at first use. Keep transitions causal and problem-oriented. Do not pad for length; add relevant modeling assumptions, uncertainty propagation, observability, interfaces, limitations, and boundary conditions.

#### Section opening and paragraph density

- Begin every method section with one coherent, unnumbered introductory paragraph before its first formula. State the problem or motivation, the method's purpose, its inputs, its principal action, and its output or downstream interface. Do not begin a section with a symbol list, equation, code detail, or citation-only survey.
- Treat paragraph density as a rendered-page requirement. Except for formula lead-ins, post-formula explanations, captions, headings, and unavoidable page-boundary fragments, target about two to four substantive body paragraphs on a full page.
- Do not produce consecutive three- or four-line microparagraphs, one-sentence blocks, or bullet-like narrative fragments. Merge adjacent paragraphs when they serve the same purpose or causal chain. Use bullets only when the writing guide explicitly requires a list.
- Build each substantive paragraph around a topic or purpose sentence, the mechanism or reasoning, and a constraint, interface, or transition. Split only when the topic, object, causal stage, or formula group changes.
- Judge density from Word's final pagination after the last save, not from character counts or Open XML paragraph counts alone.

Lead with the physical or estimation problem, then present only the minimum mathematical model needed to support the method. Keep software containers, clipping rules, cache policies, budget allocation, branch conditions, and implementation bookkeeping in prose, an algorithm, or a table unless the closest paper treats them as a principal equation.

Do not place a long formula inside a body-text sentence. Keep inline mathematics to a short symbol, scalar relation, or compact term. Move a substantive relation to a numbered display equation and explain it before and after.

Use the existing template styles by style ID or local style name. Do not type fake heading numbers when the template supplies numbering. Do not create blank headings or blank spacer paragraphs.

Measure the final body-page range in Word when a page target is required. An estimated count is not an exact count.

### Phase 5: Generate editable mathematics

Write both inline and display mathematics as native Word OMML. Never leave literal `\(...\)`, Pandoc `{=tex}`, raw LaTeX, equation images, or uneditable screenshots in the final document.

Before MathML-to-OMML conversion, remove explicit TeX spacing commands such as `\!`, `\quad`, `\qquad`, `\,`, `\:`, and `\;` when they create whitespace-only Word math runs. Rewrite fragile nested expressions into equivalent simple forms when converters drop operands. For example, prefer `T_{k-1}^{-1}T_k` over unnecessarily nested parenthesized powers.

#### Mathematical abstraction and compactness

Write formulas in the style of the closest approved paper, not in the style of source code.

- Give one mathematical claim per display equation. Use previously defined symbols instead of repeatedly nesting their full definitions.
- Reject code-shaped equations dominated by `clip`, `min/max`, `if/else`, indicator chains, cache or budget variables, trace-based tuning, and long threshold lists unless the writing guide or closest paper explicitly requires that exact equation.
- Reject “nested” optimization equations that expand residuals, robust weights, covariances, Jacobians, and multiple sums in one line. Define the residual, Jacobian, and weight first, then write compact normal equations such as `H=\sum J^T\Omega J` and `b=\sum J^T\Omega r`.
- Do not use a numbered formula merely to list software data structures or module interfaces. Express collections compactly and explain their contents in prose.
- Match source semantics exactly. Do not introduce a normalization rule, confidence model, or other mechanism that differs from the approved source; preserve the source definition and its stated assumptions.
- Require a traceable source or a necessary derivation for every new formula. If prose states the idea more clearly, use prose.

#### Long-equation layout

Do not rely on Word's automatic math wrapping. Determine fit from the actual Word text width and rendered equation width, not from character count alone.

- Set effective equation-paragraph `left`, `leftChars`, `firstLine`, and `firstLineChars` to zero.
- Keep a short equation on one line only when the equation and its number visibly fit inside the body width.
- Split a long comma-separated equation into two visually balanced rows at a comma or legal main operator.
- Put three or more parallel relations on separate rows; three parallel definitions normally occupy three rows.
- Break only at commas or operators such as `=`, `≈`, `+`, `−`, `×`, `÷`, `<`, and `>`. Never split a variable, subscript, superscript, function name, matrix, bracketed unit, or fraction.
- Align rows at the governing equals sign or main operator when practical.
- Place the equation number outside the OMML object in a dedicated right-hand cell or equivalent fixed region. Vertically center the number across all rows. Never append the number as ordinary flowing text after a tab when a formula can wrap.
- Prefer a borderless three-column table or an equivalent fixed layout for multi-line numbered equations: a balancing left column, centered formula column, and right-aligned number column with vertical centering.

Number display equations continuously and explain every symbol. Inspect every long or structurally important equation in Word after the final save. Use a Word-rendered PDF only when the user allows PDF generation; otherwise capture or inspect the relevant Word pages directly. XML validity alone does not prove correct content or layout.

Reject the document if any of these patterns remains:

- an intensity model that differs from the closest approved paper without an explicit derivation;
- an engineering tuning expression presented as a principal theoretical formula;
- a deeply nested or recursively expanded “套娃公式” that should be factorized;
- a comma-separated long equation left to automatic wrapping instead of explicit two-row layout;
- parallel definitions compressed into one line instead of one row per relation;
- a long formula embedded in body text;
- a multi-line equation whose number moves with the final line or splits at the hyphen.

### Phase 6: Insert citations

Classify the citation mode before touching the document.

#### Frozen citation mode

Use frozen mode when the user says not to handle references, not to add references, not to refresh EndNote, or to preserve the current citation formatting. The newest such instruction overrides an earlier request for real EndNote fields.

- Do not invoke EndNote, create temporary citations, run `ENFormatBibliography`, update `EN.REFLIST`, or globally update EndNote fields.
- Preserve each existing `EN.CITE` and `EN.REFLIST` field object, its result formatting, record payload, bookmarks, hyperlinks, and navigation targets. Edit prose around complete field subtrees instead of flattening and recreating them.
- Treat a temporary citation appearing in frozen mode as a pipeline failure. Redesign the field-aware replacement; never use it as a reason to refresh the document.
- Capture a baseline of citation field codes and record order, reference-list text, `ENREF_*` bookmark names, internal hyperlink targets, and navigation coverage. Require exact equality after the final Word save.
- Interpret “ignore references” as “make no reference mutation”, not as permission to skip validation.

#### Active citation-insertion mode

Only when the user explicitly authorizes adding or reformatting real EndNote citations, invoke the `endnote-cwyw-citations` skill and follow it exactly.

Resolve real EndNote record numbers. Insert temporary citations in the form `{Author, Year #RecordNumber}`, run `ENFormatBibliography`, and verify the inserted chapter itself contains `ADDIN EN.CITE`. Require `ADDIN EN.REFLIST` when a bibliography exists. Require zero unresolved temporary citations.

For comparison methods, datasets, platforms, or software listed in one sentence, place one CWYW field immediately after each supported object at its first occurrence in the chapter. Group records only when multiple records support the same named object. Never leave one aggregate citation field after a comma-separated list of different objects; a reader must be able to map every field to exactly one preceding method or dataset without inference.

Treat `ENFormatBibliography` as a document-wide mutation. Work on a copy, compare all pre-existing fields, bibliography text, bookmarks, hyperlinks, and navigation afterward, and do not deliver if unrelated citation structures changed. Do not infer authorization from the mere presence of temporary citations.

Do not infer success from the document-wide field count; the fields may all belong to earlier chapters. Count fields inside the inserted chapter boundary.

Treat CWYW editing links and Ctrl+click navigation as separate features. If the inserted citations have `EN.CITE` but no chapter-local hyperlink/bookmark structure, report that exact distinction.

### Phase 7: Finalize Word layout

Read [method-and-word-workflow.md](method-and-word-workflow.md) whenever the output is Word or EndNote-linked.

Update the table of contents through Word after citations and pagination are final only when the user authorizes TOC changes. In strict placement-only mode, do not update the TOC, table of figures/tables, or unrelated fields. Configure front-matter Roman numbering and body Arabic numbering according to the selected specification only when it is in scope.

Use odd/even headers required by the template. Query Word's localized `Style.NameLocal` before creating `STYLEREF` fields; do not assume English built-in style names work in a localized Word installation. Make chapter-title headers dynamic when a section contains multiple chapters.

For each body image paragraph, preserve the image data and aspect ratio, center the image, and explicitly set effective `left`, `leftChars`, `firstLine`, and `firstLineChars` to zero. Do not assign a body-text style with a two-character first-line indent unless direct zero values survive a Word reopen/save cycle. Do not change the global body style to fix an image paragraph. Exclude protected cover-page anchored shapes from body-image normalization.

Compute each section's available body width and printable height from its page size and margins. Auto-scale an oversized body image downward, preserving aspect ratio, so its rendered extent remains within the text width and leaves room for its caption and paragraph spacing. Conceptually use `min(1, available_width/original_width, available_height/original_height)`; do not enlarge an image unless the user authorizes it. For anchored images, also verify offsets, wrapping, and anchors. Move the image to a clean page or reduce it further when the caption would be orphaned or pushed beyond the printable region.

After any direct Open XML patch, reopen the document in Word, repaginate, and save. Update only the specific ordinary Word fields authorized by the user. In frozen citation mode, never run EndNote or blanket-update EndNote fields. Reinspect effective paragraph formatting after Word has normalized the file; pre-save XML is not final evidence.

When rewriting `word/document.xml`, preserve every source namespace declaration referenced by `mc:Ignorable`. Respect schema-sensitive child order in WordprocessingML and OMML. Keep display math in `m:oMathPara`; accept either `m:eqArr` rows or explicit `m:m/m:mr` rows for structured multi-line equations. A valid ZIP and parseable XML are insufficient: require the exact deliverable to open normally in desktop Word without an Open-and-Repair path.

Use staged outputs and a timestamped untouched backup. Finish in this order: generate the candidate, open and repaginate in Word, update only explicitly authorized ordinary fields such as TOC page numbers, save, remove converter-created whitespace-only math runs if present, reopen for page inspection, and run the preservation and structural checks on the exact final file. Never blanket-update all fields merely to refresh the TOC.

Generate a PDF preview only when the user requests or permits it. If PDF is prohibited, perform equivalent targeted visual inspection in Word for every long equation, multi-line number, body image, caption, and page boundary.

### Fixed page-edge placement for figures and tables

Treat figures and single-page tables as page-edge floats. Place them at the top of the text area whenever practical, otherwise at the bottom. Do not interrupt a continuous body paragraph or insert a visual in the middle band of a page merely because its first citation occurs there. Keep the prose continuous and move the visual to the nearest acceptable top or bottom position.

#### Enforce strict placement-only mode

Enter strict placement-only mode when the user says only to fix figures/tables in text boxes, forbids other changes, or gives an equivalent narrow instruction. This mode overrides the reconstruction and global-finalization defaults below.

- Change only the placement mechanism, object anchor, and the minimum missing body-reference prose explicitly requested.
- Do not change table rows, columns, orientation, merges, widths, heights, padding, borders, fonts, shading, data, emphasis, or notes. Do not change image data, dimensions, crop, or aspect ratio. Do not change headings, formulas, citations, references, TOC, or unrelated fields.
- Preserve the original figure, table, caption, and note appearance as exactly as Word permits. Never invoke the table-reconstruction rules unless the user separately authorizes redesign.
- Make a baseline before editing and compare the exact final DOCX against it. Treat any unrelated mutation as a failure, even when it appears visually harmless.

#### Use a fixed text-box container

- Put each figure or single-page table, its caption, and any inseparable note in one fixed, borderless Word text box when the template and field behavior permit it.
- Give the text box no visible outline and no fill. Keep the page visually white. In strict placement-only mode, use zero or the minimum necessary internal margins so the object's original geometry does not change.
- Size the box from the section's real text width and printable height. Keep the complete box, including caption and note, within the page margins with visible clearance.
- Position it horizontally relative to the page margins and center it in the text area.
- Position it vertically relative to the page: align its top edge with the top of the printable text area, or align its bottom edge with the bottom of the printable text area above the footer.
- Lock the anchor, disable overlap, and use top-and-bottom text wrapping. Do not use behind-text, in-front-of-text, square, or tight wrapping for thesis figures and tables.
- Anchor the box to a stable nearby main-story paragraph on the same page. Avoid long body paragraphs, paragraphs with `pageBreakBefore`, and fragile `keepNext`/`keepLines` chains because Word can move the whole anchor paragraph and create a blank page.
- Prefer a short stable paragraph. If necessary, use one dedicated zero-spacing anchor paragraph adjacent to the logical insertion point; do not use repeated, visible, or easily deleted spacer paragraphs.
- Treat the text-box extent as a rendered-content contract, not an estimate. After the Word save, verify the last table row, the complete visible caption, and every note; if any is clipped, enlarge or repaginate the container and render again. When enlarging would collide with a peer object or exceed the printable band, move that object to a dedicated top-of-page anchor instead of accepting overlap or hidden rows.
- Keep one page-edge band clear for each object. When two objects share a page, deliberately place one at the top and one at the bottom whenever they fit. With three objects, use top and bottom first and permit a middle-band exception only when page geometry proves it is necessary and non-overlapping.

#### Preserve caption and field behavior

- Keep the caption visually attached to the figure or table. Use the template's caption font, spacing, numbering, and punctuation.
- Verify whether the template's table-of-figures or table-of-tables field discovers captions stored in text boxes. Word fields in a drawing story may not behave like fields in the main document story.
- Capture every visible caption label and field result before moving it. Preserve the original `SEQ`, bookmark, list sequence, and cross-reference structure whenever it remains reliable.
- Word style-linked numbering can restart inside a drawing story. If moving the caption would reset its number or make it undiscoverable, keep the original numbered caption in the main story as a nonprinting numbering anchor and place a static copy of the correct visible label inside the text box. Preserve all bookmarks and field targets.
- On the visible text-box caption, explicitly set direct `numId=0`; merely removing `numPr` is insufficient when the caption style carries automatic numbering. Verify that Word renders exactly one label, never a duplicated label such as `图1-1 图1-1`.
- Ensure a hidden or nonprinting numbering anchor creates no visible/printed duplicate, orphan line, or pagination gap. Do not replace a working `SEQ`, bookmark, or cross-reference unless the fixed-container limitation makes it necessary.
- Preserve image data, aspect ratio, table data, bold-result semantics, hyperlinks, bookmarks, and citation fields during conversion to a fixed container.

#### Require numbered references and descriptions in the body

- Audit every figure caption and every data-table caption against the main-story prose.
- Before writing a reference, read the complete preceding paragraph, the target paragraph, the following paragraph, the caption, and the actual figure/table content. Identify whether the object provides evidence, comparison, mechanism, result interpretation, or a transition.
- Integrate the numbered reference into the local argument. Normally use a compact two- or three-sentence micro-passage: connect it to the preceding claim, interpret the object-specific information, then state the consequence or transition that leads into the following prose.
- Never append an isolated generic sentence such as `图1-2展示了……，表1-1进一步对比了……` merely to make the label appear. Never create a detached paragraph whose only function is to mention a figure/table number.
- Add only missing numbered references such as `见图3.2` or `如表3.5所示`, plus a context-matched explanation. A label count is not evidence of a valid reference.
- Refer to a figure/table pair in one passage only when both support the same local claim. Otherwise place each reference beside the paragraph where its information is actually analyzed.
- Explain what the visual evidence means for the current argument rather than repeating the caption. Do not invent details, causal claims, trends, or performance conclusions that the object and surrounding evidence do not support.
- Keep the passage concise enough to preserve pagination. If the added explanation introduces a blank page, shifts a fixed object to the wrong page-edge band, or disrupts paragraph rhythm, tighten the reference passage itself; do not move or rewrite unrelated body content.
- In frozen citation mode, insert prose around complete EndNote field subtrees. Do not alter citations or the reference list.
- After the final Word save, verify that every logical figure/table label appears once in a visible caption and at least once in relevant body prose. Account for OOXML `AlternateContent` compatibility copies so they are not misclassified as separate logical objects.

#### Handle exceptions without creating mid-page floats

- Do not put a multi-page table in one text box; text boxes cannot paginate as normal tables do. Split it into meaningful fixed blocks with repeated headers, or keep it in the main story beginning at a clean page top with repeating header rows.
- If a figure plus caption cannot fit in either page-edge band, scale it down without distortion or move it to a dedicated following page. Do not force it into the page middle.
- If a full-page visual is necessary, reserve a dedicated page and keep it inside the printable area rather than layering it over headers or footers.
- Do not use repeated blank paragraphs, manual spaces, hidden tables, or negative offsets to simulate fixed placement.

#### Validate fixed objects after pagination

- Reopen the exact DOCX in desktop Word, repaginate, save, and verify every shape's anchor page, horizontal position, vertical position, width, height, wrapping mode, and overlap setting.
- Inspect the page at 100% plus its preceding and following pages. Confirm that the visual occupies the top or bottom band, body text does not run beside it, the caption is not orphaned, and no anchor icon or box edge crosses the margins.
- Recalculate the final page, top coordinate, height, and vertical interval of every fixed shape after Word repaginates. Reject same-page interval overlaps, clipping, or objects outside the printable area; pre-pagination positions are not evidence.
- Compare final pagination with the baseline and scan for newly introduced blank or abnormally sparse body pages. If one appears, move only the drawing run/anchor to a short stable or dedicated zero-spacing paragraph; do not move or rewrite the body text.
- Recheck visible caption numbers and all existing cross-references after the final Word save. Recheck the table of figures/tables only when the user authorized updating it. A visually correct fixed text box is still a failure if numbering or navigation is broken.
- For placement-only work, require unchanged media hash multiset, unchanged table data signatures, unchanged heading sequence, unchanged field-code multiset, and exact EndNote field code/order equality in frozen mode.
- Treat the two `w:tbl` copies commonly stored in `mc:AlternateContent` Choice/Fallback inside a text box as one logical table. Verify that each source table signature survives rather than requiring naïve raw table-count equality.

### Thesis-table reconstruction and page-margin contract

Apply this section only when the user authorizes table repair or redesign. It does not apply in strict placement-only mode. When authorized, treat a thesis table as a data model that must be rendered clearly inside the active section's text area. Do not preserve a defective row/column orientation merely because it already exists. Preserve the data and meaning, but redesign the table when its geometry is unsuitable for the page.

#### Establish the controlling geometry

- Read the university template, style examples, and the actual section properties before formatting. Treat the retained thesis style as the visual authority.
- Compute `available_width = page_width - left_margin - right_margin` for the table's section. Account separately for portrait and landscape sections.
- Set one explicit table width no greater than the available width. Make `tblW`, `tblInd`, `tblGrid`, and every spanned or unspanned `tcW` agree in DXA. Center the table inside the text area; never rely on AutoFit or visual dragging.
- Leave visible clearance between the outer table rules and both page margins. A table that merely touches the margin is not acceptable.
- Normalize compatible portrait tables on the same page to the same total width whenever practical. Use content-aware column proportions; do not assign equal widths blindly.

#### Row height, padding, and text fit

- Do not use a fixed exact row height for thesis data tables. Let rows expand naturally and use moderate, consistent cell padding and line spacing.
- Reject rows that are either cramped or visibly hollow. As a starting range, use 15--30 DXA top and bottom cell padding and approximately 10.5--12 pt exact line spacing, then judge the rendered page.
- Center short labels and numeric values horizontally and vertically. Remove inherited first-line and left indents from all table-cell paragraphs.
- Keep method names, device names, sequence identifiers, and short categorical labels on one line whenever they are intended as atomic labels. Widen the relevant column before shrinking the font.
- Do not apply `w:noWrap` globally to a dense wide table. In Word, forced no-wrap cells can expand a fixed-width table beyond the page margins. Prefer column redistribution, reduced cell padding, a modest font reduction, or structural redesign.
- Use Song typeface for Chinese and Times New Roman for Latin letters and numerals unless the controlling university template specifies otherwise. Keep the background white.

#### Three-line table styling

- Use a restrained thesis three-line table by default: a strong top rule, a thin header-bottom rule, and a strong bottom rule. Do not add vertical borders, decorative fills, PowerPoint-like panels, or unexplained side rules.
- Use a thin horizontal separator between vertically stacked dataset groups when it improves scanning.
- Keep the caption above the table and explanatory notes below it. Preserve the existing table number and caption text unless the user authorizes a wording change.
- Preserve emphasis semantics exactly: retain bold best-performing values, failure marks such as `×`, units, decimal precision, method spelling, and dataset or sequence identifiers.

#### Redesign wide comparison tables instead of compressing them

Apply the following escalation order when a table is too wide:

1. Recalculate the real section width and remove erroneous indents or AutoFit behavior.
2. Redistribute columns according to content length.
3. Reduce horizontal cell padding.
4. Reduce the table font modestly while keeping it thesis-readable.
5. Transpose or regroup the data.
6. Use a dedicated landscape section only when the redesigned table still cannot fit naturally in portrait.

For a method-by-sequence comparison matrix with many sequences:

- Prefer methods as columns and sequences as rows when this reduces the column count substantially.
- Stack datasets vertically. Merge the dataset-name cell across its sequence rows, or use clearly separated stacked blocks when a merged label would be harder to read.
- Keep one consistent method order across all dataset groups.
- When the transposed table fits a portrait page, restore the isolated table section to portrait rather than retaining an unnecessary landscape page.
- Do not split one logical dataset into multiple unrelated tables solely to force a fit. If multiple blocks are necessary, repeat the method header and preserve an explicit group label.

#### Remove editing-view artifacts safely

- Diagnose black squares, bars, or unexplained left-edge marks in Word's formatting-mark view before changing borders. They may come from paragraph pagination controls rather than table rules.
- Remove unnecessary `keepNext`, `keepLines`, and `pageBreakBefore` settings from table-cell and caption paragraphs when they cause visible editing artifacts.
- Use an explicit page break or a dedicated section break to keep a table together. Do not use hidden empty tables, manual spaces, or fake border objects for placement.

#### Preservation and validation for a reconstructed table

- Capture the original table matrix before reconstruction. After transposition or stacking, verify a reversible mapping from every original method--sequence value to the new cell.
- Require exact preservation of all data values, labels, units, bold-result flags, and failure symbols. Verify all unrelated table text, media hashes, citation fields, and reference-list structures remain unchanged.
- Reopen the exact candidate in desktop Word, repaginate, and save before judging it. Word's final layout is authoritative.
- Render and inspect the table page at 100% plus the immediately preceding and following pages. Check page margins, caption pairing, column wrapping, group separators, row rhythm, headers, footers, and section orientation.
- Inspect the editing view with formatting marks enabled when the user reports black edges or unexplained symbols; a clean PDF alone does not validate the Word editing view.
- Reject the result if any outer rule, cell text, resize handle, or expanded no-wrap column reaches beyond the text area; if any atomic label wraps because of a narrow column; if row heights are visibly uneven without a semantic reason; or if same-page peer tables have avoidably inconsistent widths.

### Validation gate

Run `../scripts/method/inspect_docx_quality.py` and supplement it with Word/PDF checks. Do not hand off until all requested checks pass:

For a preservation rewrite, pass the untouched backup with `--baseline-docx`, select project-appropriate `--max-inline-math-chars` and `--max-single-line-display-chars` thresholds, and use `--strict`. Treat the static width thresholds as triage only; the final Word rendering remains authoritative.

- DOCX ZIP integrity is valid.
- The insertion boundary is correct and unrelated content is unchanged.
- Heading order is complete, with no empty or duplicated headings.
- Display-equation numbering is continuous within each chapter; validate chapter sequences separately when numbering resets by chapter.
- Literal inline LaTeX, empty math runs, whitespace-only math runs, boxes, and phantoms are zero unless explicitly justified.
- Every formula is traceable to the writing guide, an approved close paper, or a necessary derivation, and its abstraction level matches that source.
- Code-shaped tuning equations, unsupported intensity models, avoidable nested formulas, and long inline formulas are zero.
- Every long display equation uses explicit, balanced rows; no numbered long equation depends on automatic wrapping.
- Multi-line equation numbers occupy a separate fixed region, remain right-aligned, and are vertically centered without splitting.
- Equation and body-image paragraphs have effective zero left and first-line indentation after the final Word save, including character-based indent attributes.
- Every method section opens with a purpose-led paragraph covering its problem, input, action, and output before the first formula.
- Rendered body pages normally contain about two to four substantive prose paragraphs; repeated short fragments are merged unless they are formula explanations or logically distinct units.
- Every rendered image stays within its section's text width and printable height, retains its aspect ratio, and remains visually paired with its caption.
- Every single-page figure and table occupies a page-top or page-bottom band rather than interrupting the middle of continuous body text, unless the user explicitly approves an exception.
- Every fixed text box is borderless, inside the printable area, locked to a stable anchor, non-overlapping, and configured for top-and-bottom wrapping; its caption and cross-reference behavior still works after the final Word save.
- In strict placement-only mode, table/image/caption appearance and dimensions, table data signatures, media hashes, headings, formulas, field codes, citations, references, TOC, and unrelated content match the baseline except for explicitly authorized changes.
- Every visible text-box caption retains its original number, has direct `numId=0` when style-linked numbering could restart, and renders no duplicate label; any retained main-story numbering anchor is nonprinting and creates no pagination gap.
- Every logical figure and data table has a numbered reference and context-matched description in the relevant main-story prose.
- Every added figure/table reference passes the local-logic test: it is connected to the preceding claim, interprets object-specific information, and supports the following conclusion or transition; isolated label-only or caption-paraphrase sentences are zero.
- Final shape intervals do not overlap; no new blank or abnormally sparse page was introduced by an unstable anchor.
- Every thesis table stays within its section's text width with visible side clearance; compatible same-page tables use a consistent total width.
- Table rows have moderate natural height, atomic labels do not wrap from avoidably narrow columns, and Word's editing view contains no unexplained left-edge paragraph artifacts.
- Any transposed or vertically stacked comparison table has a verified one-to-one mapping to the original data, including bold best values and failure marks.
- Representative complex formulas visibly contain every operand and match the closest paper's mathematical style.
- The TOC shows the generated headings and current page numbers.
- Headers contain no stale chapter name, degree-type error, or `STYLEREF` error.
- Page-number fields and exact body-page count match the specification.
- The inserted chapter contains real EndNote fields only when active insertion was authorized.
- In frozen citation mode, citation field codes and order, reference-list text, `ENREF_*` bookmark names, internal hyperlinks, and navigation coverage exactly match the baseline; field-count equality alone is insufficient.
- In active mode, `EN.REFLIST` exists, temporary citations are zero, and both editing-link and navigation layers are verified.
- The final validation was run on the exact delivered DOCX after its last Word save, not on an earlier intermediate file.
- The final DOCX opens normally in desktop Word, preserves required `mc:Ignorable` namespace declarations, and passes structural checks for both `m:eqArr` and `m:m/m:mr` multi-line equations.

### Deliverables

Return the final DOCX plus the named RAG folder, knowledge summary, framework analysis, requested preview artifacts, validation JSON, and concise report. Do not generate a PDF when the user opts out. Link each user-facing file with an absolute path. State any unverified limitation plainly.
<!-- END SOURCE: method-workflow.md -->

<!-- BEGIN SOURCE: method-workflow-checklist.md -->
## Workflow checklist

### Interview gate

- [ ] RAG name and approved source scope captured.
- [ ] Research-work framework captured.
- [ ] Language, prose style, specification, and template captured.
- [ ] Draft/formulas and final or added body-page target captured.
- [ ] Citation method, EndNote library/group, and linking requirement captured.

### Build hygiene

- [ ] Timestamped process directory created.
- [ ] Original files remain unchanged.
- [ ] Existing target backed up before destructive editing.
- [ ] Unreadable, encrypted, scanned, and duplicate sources logged.

### RAG

- [ ] Manifest name exactly matches the user-provided name.
- [ ] Source scope matches the approved range.
- [ ] Semantic chunks retain heading and formula context.
- [ ] Metadata, formula records, index, summary, and query instructions exist.
- [ ] Three representative queries return useful results.
- [ ] The writing guide and closest chapter papers have a formula-style contract with source/page traceability.

### Framework and writing

- [ ] Chapter purpose and downstream mathematical interfaces are explicit.
- [ ] Content is organized by technical logic rather than paper-by-paper notes.
- [ ] Every formula supports the research route.
- [ ] Every symbol is defined at first appearance.
- [ ] Excluded material such as experiments remains excluded.
- [ ] Formula content follows the closest paper rather than code-level implementation details.
- [ ] Unsupported intensity normalization, weighting, residual, or confidence models are absent.
- [ ] Long formulas do not appear inside body-text sentences.

### Word and equations

- [ ] Existing styles and numbering are reused.
- [ ] Inline and display mathematics are native OMML.
- [ ] No literal LaTeX/Pandoc artifacts remain.
- [ ] No empty headings, empty equations, or blank spacer paragraphs remain.
- [ ] Equation numbers are continuous.
- [ ] Code-shaped tuning equations and avoidable nested “套娃公式” are absent.
- [ ] Comma-separated long equations use explicit balanced rows; parallel relations use one row per relation.
- [ ] Multi-line equation numbers are in a separate fixed region, right-aligned, and vertically centered.
- [ ] Long equations do not depend on Word automatic wrapping or a trailing ordinary-text number.
- [ ] Equation paragraphs have effective `left/leftChars/firstLine/firstLineChars=0` after the final Word save.
- [ ] Body inline-image paragraphs have effective zero left and first-line indentation, are centered, and preserve aspect ratio after the final Word save.
- [ ] Every long or structurally important equation is visually checked in Word; use PDF only when permitted.

### Pagination and headers

- [ ] Word repagination completed after the final edit.
- [ ] TOC updated after citations and formulas are final.
- [ ] Front matter and body numbering match the specification.
- [ ] Odd/even headers match the degree type and current chapter.
- [ ] Localized Word style names are used in STYLEREF.
- [ ] Exact chapter body pages are measured from chapter start to the next section.

### EndNote

- [ ] Citation mode is explicitly recorded as frozen or active insertion.
- [ ] Frozen mode created no temporary citations and invoked no EndNote macro or bibliography refresh.
- [ ] Frozen mode exactly preserves field codes/order, reference-list text, `ENREF_*` bookmarks, internal hyperlinks, and navigation coverage.
- [ ] In active mode, record numbers were resolved from the intended library/group and insertion was explicitly authorized.
- [ ] In active mode, the inserted chapter contains EN.CITE fields, EN.REFLIST exists, and no temporary citations remain.
- [ ] CWYW editing fields and Ctrl+click navigation are verified as separate layers; field-count equality is not accepted as preservation proof.

### Final handoff

- [ ] DOCX package integrity passes.
- [ ] Unrelated content comparison passes.
- [ ] Validation ran on the exact delivered DOCX after its last Word save.
- [ ] The requested Word/PDF preview evidence and validation report exist; no PDF was generated when prohibited.
- [ ] Limitations are stated without overstating verification.
<!-- END SOURCE: method-workflow-checklist.md -->

<!-- BEGIN SOURCE: method-rag-schema.md -->
## RAG schema

### Directory layout

```text
<knowledge-base>/
├── documents/
│   └── chunks.jsonl
├── metadata/
│   └── documents.jsonl
├── formulas/
│   └── formula_candidates.jsonl
├── index/
│   └── <name>.sqlite3
├── summary/
│   └── coverage.md
└── <name>.manifest.json
```

### Document metadata record

```json
{
  "document_id": "stable source-derived id",
  "title": "document title",
  "authors": "authors when available",
  "year": 2025,
  "source": "relative source path or URL",
  "source_type": "paper|thesis|book|note|web",
  "extraction_status": "ok|partial|failed",
  "content_hash": "sha256"
}
```

Leave uncertain metadata empty. Do not invent an author, year, venue, dataset, or result.

### Knowledge chunk record

```json
{
  "knowledge_base": "user-provided name",
  "chunk_id": "stable content id",
  "document_id": "parent id",
  "title": "semantic heading",
  "heading_path": ["chapter", "section", "subsection"],
  "source": "source path",
  "keywords": ["term"],
  "content": "self-contained semantic passage",
  "formulas": ["raw or normalized expression"],
  "variable_explanations": {},
  "chunking": "heading_then_paragraph"
}
```

Target 800–2000 Chinese characters for prose-heavy chunks, adjusted to preserve semantic completeness. Keep formulas with their definitions and application context. Avoid a chunk containing only an equation number or page footer.

### Extraction priorities

Extract when supported by the source:

- problem definition and assumptions;
- system architecture and data flow;
- state variables and coordinate frames;
- motion, observation, residual, and noise models;
- optimization variables, objectives, solvers, and priors;
- algorithm contributions, limitations, and applicable conditions;
- formulas, symbol definitions, and downstream interfaces.

Mark automatically extracted PDF formula strings as candidates requiring source verification. Keep a separate curated formula set for high-confidence reuse.

### Retrieval

At minimum, provide a local lexical index with Chinese-aware tokenization and a query example. Dense embeddings are optional; do not claim a vector index exists unless embeddings were actually generated and persisted.

Record the index type in the manifest. Test queries should cover a foundational formula, a method family, and a thesis-specific research problem.
<!-- END SOURCE: method-rag-schema.md -->

<!-- BEGIN SOURCE: method-word-endnote-quality.md -->
## Word, equation, and EndNote quality rules

### Editable equations

Use native OMML for inline and display equations. A DOCX containing OMML is not automatically correct: render it through Word and inspect representative pages.

Before generating formulas, learn the mathematical style from the writing guide and the closest approved paper. Prefer short, atomic paper equations over code-shaped expressions. Do not invent intensity normalization, robust weighting, confidence products, residuals, or tuning equations that the closest source does not use. Keep clipping, branching, caches, budgets, threshold chains, and software containers in prose or algorithms unless they are principal source equations.

Factorize nested formulas. Define compact residuals, Jacobians, and weights first, then express the normal equations with those symbols. Do not expand every sum, covariance, robust weight, and Jacobian inside one numbered equation. Keep inline mathematics short; move substantive relations into display equations.

Common failures and remedies:

- Literal `\(...\)` remains in prose: parse mixed text and replace every inline expression with an inline `m:oMath` element.
- Dotted empty placeholder appears: remove TeX spacing commands and whitespace-only `m:r` runs before saving.
- Operand disappears inside `Log` or `Exp`: simplify nested LaTeX and visually confirm the transformed expression.
- Equation numbers drift: generate the number from one sequence and verify `(chapter-1)` through `(chapter-N)` in document order.
- Formula is a picture: reject it unless the user explicitly requested a non-editable image.
- Long comma-separated formula wraps unpredictably: create two balanced OMML rows at legal commas/operators.
- Parallel definitions wrap as one sentence: put one relation on each row; use three rows for three parallel definitions.
- Multi-line number follows the last row or splits at its hyphen: place the number in a separate right-hand cell and vertically center it across the rows.
- Formula paragraph is shifted right: explicitly set `left`, `leftChars`, `firstLine`, and `firstLineChars` to zero and recheck after Word saves.

Count `m:box`, `m:phant`, empty math runs, whitespace-only math runs, and literal LaTeX. A zero count is the normal acceptance condition.

Do not treat `m:brk=0` plus a visually wrapped formula as a valid multi-line layout. Word automatic wrapping does not satisfy balanced row or number-centering requirements. Use a borderless three-column table or an equivalent fixed layout for multi-line numbered equations. Inspect every long equation after the final Word save; if PDF generation is prohibited, inspect the Word rendering directly.

### Body images

Preserve image bytes and aspect ratio. For each body inline-image paragraph, center it and explicitly set effective `left`, `leftChars`, `firstLine`, and `firstLineChars` to zero. A body-text style with a two-character first-line indent can override an incomplete `firstLine=0`; set both twip- and character-based values, reopen in Word, save, and verify again. Do not modify the global body style or normalize protected cover-page anchored shapes.

### Word sections, headers, and page numbers

Inspect every `sectPr`, header/footer relationship, page-number format, and link-to-previous state.

For common Chinese doctoral templates:

- front matter normally uses Roman numbering;
- body normally uses Arabic numbering starting at 1;
- odd pages normally show the current chapter title;
- even pages normally show the university and degree identity.

Follow the user's actual specification when it differs.

Do not hard-code a stale chapter header from another section into a section containing other chapters. Use STYLEREF or add correct section breaks. Query `Styles.Item(wdStyleHeading1).NameLocal`; Chinese Word may require `标题 1` instead of `heading 1`.

After field changes, run Word repagination, update the TOC, save, and export a fresh PDF. Search the rendered PDF for `错误!`, stale chapter names, and the wrong degree type.

Measure body pages from the adjusted page number of the chapter heading to the adjusted page number of the next major section. Do not count bibliography pages.

### EndNote CWYW

First classify the task as frozen citation mode or active citation-insertion mode.

In frozen mode—triggered by instructions such as “不管文献”, “不新增文献”, “保持现有引用和排版”, or “不要刷新 EndNote”—do not create temporary citations, invoke EndNote, run `ENFormatBibliography`, update `EN.REFLIST`, or globally update EndNote fields. Preserve complete field subtrees and edit prose around them. Capture and compare field codes/order, bibliography result text, `ENREF_*` bookmarks, internal hyperlink targets, and navigation coverage. A temporary citation in frozen mode is a pipeline failure, not authorization to refresh.

Only use the workflow below when active insertion or reformatting is explicitly authorized.

Use real record numbers and temporary citations:

```text
{FirstAuthorSurname, Year #RecordNumber}
{Author, Year #12; Author, Year #34}
```

Run EndNote's `ENFormatBibliography` macro. Formatting a large document may take several minutes; wait for Word to return before assuming a hang.

Treat the macro as a document-wide mutation. Run it on a copy and prove that all pre-existing citation fields, bibliography text, bookmarks, hyperlinks, and navigation survived. Do not accept unchanged field counts as sufficient evidence.

Verify inside the generated chapter boundary:

- `ADDIN EN.CITE` count is greater than zero;
- unresolved temporary citations equal zero;
- reference-list field `ADDIN EN.REFLIST` exists;
- cited records match the approved library/group.

Document-wide EN.CITE counts are insufficient because earlier chapters may already contain fields.

CWYW fields allow EndNote to edit and update citations. Ctrl+click from an in-text number to the bibliography requires separate Word hyperlink/bookmark structures. Report these layers separately.

### Process reliability

Keep only automation-created Word instances under agent control. Close them after saving. A lingering Word process can force the next session to open the target read-only.

If a direct DOCX XML patch is necessary after EndNote formatting, preserve EN.CITE and EN.REFLIST, then reopen the document in Word and repeat pagination, TOC update, save, and preview export.

Word can normalize direct paragraph formatting during a save. Re-run formula- and image-indent checks on the exact delivered DOCX after its last save. Never validate an intermediate file and assume later CWYW, field updates, or pagination saves preserve those results.
<!-- END SOURCE: method-word-endnote-quality.md -->
