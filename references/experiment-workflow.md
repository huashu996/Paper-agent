# Experiment Workflow and Fidelity Contract

## Contents
- Core experiment workflow
- Source-evidence fidelity contract

<!-- BEGIN SOURCE: experiment-workflow.md -->
## Experiment Skill

Produce a thesis-ready experimental section while treating source results as immutable evidence. Reuse source figures, preserve source table values and emphasis, write analytical Chinese prose, and verify the exact final DOCX in Word.

### Required companion skills

- Use the `documents` skill for DOCX creation, editing, rendering, and page-by-page inspection.
- Use the `pdf` skill when a PDF must be read or visually inspected.
- Also read and follow [方法工作流](method-and-word-workflow.md) when the request requires a reusable research knowledge base, exemplar-thesis style learning, exact page targets, or broader chapter integration.
- Read [experiment-workflow.md](experiment-workflow.md) before reconstructing any table or figure.

### Capture the task contract

Resolve these inputs from the request or source files before drafting:

1. Source paper or raw experimental document.
2. Exemplar dissertation or desired prose style.
3. University formatting specification or Word template.
4. Chapter/section number and page target.
5. Citation policy.
6. Whether later comparison, trajectory, or point-cloud figures need reserved positions.

Do not ask again for information already supplied. Record all constraints in a timestamped build log.

Treat the following as hard freezes:

- “表格只翻译，不修改” freezes values, units, row/column structure, order, sequence names, failure marks, averages, and bold best-result cells.
- “加入所有实验图” requires an inventory of the complete experimental section; do not substitute placeholders for existing source figures.
- “不插入文献” enables frozen citation mode: add no citations, bibliography, EndNote fields, or temporary citation tokens.
- A page target never authorizes omission of required source tables or figures. Preserve content first and report the resulting page count.
- Never modify the original source files. Convert legacy `.doc` only into an analysis copy.

### Build workflow

#### 1. Inventory the evidence

Create `build/paper-agent/<timestamp>/experiment/` with `sources/`, `extract/`, `previews/`, and `validation/`.

Identify the exact experiment boundary from headings. Inventory:

- every table number, title, row/column count, merged cell, unit, note, failure symbol, and bold cell;
- every experimental figure, subfigure, caption, embedded media relationship, crop rectangle, and display order;
- dataset descriptions, hardware, metrics, comparison methods, fairness settings, runtime, memory, and stated limitations.

Render the source experimental pages and inspect them visually. Text extraction alone is not proof of table or figure completeness.

#### 2. Learn the thesis style

Read representative experimental sections from the exemplar dissertation. Record:

- section-opening pattern;
- dataset and metric description order;
- quantitative analysis pattern: fact → magnitude → mechanism → boundary;
- treatment of failures, runtime, generalization, and limitations;
- caption, table, paragraph-density, header/footer, and page-number rules.

Keep source results authoritative. If narrative prose conflicts with a table, preserve the table exactly, use the tabulated value in the analysis, and log the discrepancy.

#### 3. Create the fidelity ledger

Before writing, build a table/figure ledger. For each source table, store its dimensions, cell text, numeric token order, failure marks, merged cells, bold data-cell coordinates, and notes. For each source figure, store its media target, byte hash, crop rectangle, aspect ratio, and caption.

Do not replace source tables with summaries, regrouped tables, or derived averages unless the user explicitly authorizes that transformation. Derived statistics may appear in prose only when labeled as calculations.

#### 4. Draft the experiment section

Preserve the chapter structure that the author or template has established. When drafting a new method-verification chapter without an outline, the following headings are one option if the available experiments support them:

1. `实验设置与数据集`
2. `消融实验`
3. `对比实验`
4. `计算效率与资源消耗`

Choose headings that reflect the tests actually performed. Give the conditions needed to interpret each comparison, including the setup, datasets, metrics and baselines. Group related comparisons when that helps readers follow the question. Discuss sensitivity, failure cases, resource costs or deployment limits where the evidence is most relevant.

Track where each dataset first appears in the thesis. At that point, explain what was used and why it suits this test. Include provenance, collection conditions, the selected subset and its limitations when they matter to the interpretation. Preserve or insert the authorized citation as appropriate. If the dataset is reused, describe what the later test asks and any relevant change in the setup.

Explain the comparison that answers the ablation question. Identify the configurations, what changed and which conditions were held constant. Interpret the relevant outcome in that context. When several components changed together, attribute the result to the combined configuration. Treat an untested explanation or a proposed follow-up as such.

Use this default research sequence when supported by the source:

1. Experimental purpose.
2. Datasets, platforms, metrics, comparison methods, hardware, and fairness settings.
3. Public benchmark results.
4. Results under challenging conditions or alternative measurement settings.
5. Cross-sensor and cross-scenario generalization.
6. Runtime and memory efficiency.
7. Limitations and section conclusion.

Write formal Chinese doctoral prose. Use concrete values from the original tables, explain why performance changes, and state failure cases and applicable boundaries. Do not claim mechanisms or experiments absent from the approved sources.

#### 5. Reconstruct tables without altering evidence

Translate only titles, headers, type labels, scene labels, units, and notes. Preserve method names and dataset/sequence identifiers.

Use chapter-based numbering such as `表3.1`. Rebuild three-line tables with explicit widths, repeated headers, non-splitting rows, centered numeric cells, and readable notes. Keep a complex wide table on one page when practical; use a deliberate page break or landscape section rather than splitting its semantic structure.

Preserve original bold coordinates even when the source emphasis appears inconsistent with the numerical minimum. Fidelity takes precedence over silent correction.

#### 6. Reuse every source experiment figure

Prefer the original embedded image bytes over screenshots. For legacy VML pictures, extract the media and reproduce the source `croptop`, `cropbottom`, `cropleft`, and `cropright` rectangle. Cropping away source-recorded whitespace is allowed; redrawing or regenerating the figure is not.

Insert figures inline, centered, within the text width, with zero paragraph indentation and preserved aspect ratio. Translate the caption, not the pixels inside the source figure, unless the user explicitly requests image editing.

Keep user-requested future figure positions as clearly labeled replaceable boxes. Existing source figures never count as placeholders.

#### 7. Render and validate

After every meaningful edit:

1. Open and repaginate in desktop Word.
2. Export a QA PDF.
3. Render every page to PNG.
4. Inspect every page at 100% for overlap, clipping, table crowding, missing glyphs, split tables, orphan captions, headers, footers, and page numbers.
5. Repeat until clean.

If the authorized experiment revision changes headings collected by the Word table of contents, wait until pagination is final, update only the main table-of-contents field once, and verify its entries, levels and page numbers against the rendered document. Do not update all fields and do not refresh EndNote, the bibliography, figure/table lists or unrelated cross-references unless separately authorized.

Run the bundled audit when both source and final DOCX files are available:

```powershell
python ../scripts/experiment/audit_experiment_tables.py SOURCE.docx FINAL.docx `
  --header-rows 1,1,1,1,2,1,2 `
  --source-table-json extracted_tables.json `
  --replacement A-LOAM1=A-LOAM `
  --replacement Livox_mapping2=Livox_mapping `
  --output-json table_audit.json
```

Also run `../scripts/method/inspect_docx_quality.py` when available. Require:

- exact data-table count;
- exact ordered numeric-token match;
- exact failure/multiplication-mark count;
- exact bold data-cell coordinates;
- expected source-image count and image/crop hash;
- zero unintended citations or EndNote fields;
- correct page count, headings, A4 geometry, headers, and page fields;
- a clean final Word render.

### Delivery

Deliver the final DOCX only unless the user requests validation artifacts. State the final page count, included source tables and figures, retained placeholders, citation mode, and any unresolved source conflict. Never describe a document as verified unless the validation ran on the exact final DOCX after its last Word save.
<!-- END SOURCE: experiment-workflow.md -->

<!-- BEGIN SOURCE: experiment-fidelity-contract.md -->
## Experimental evidence fidelity contract

### Table preservation

For each table, preserve:

- table order and chapter-local identity;
- row and column order;
- merged header groups;
- dataset and sequence identifiers;
- method names;
- every numeric value and decimal precision;
- signs, percentages, units, scientific notation, and `±`;
- failure marks such as `×`;
- average rows;
- bold data-cell coordinates;
- explanatory notes.

Allowed changes:

- translate the table title and descriptive labels;
- convert source numbering such as `TABLE II` to chapter numbering such as `表3.2`;
- restyle borders, fonts, widths, and alignment to the thesis format;
- replace equation-object headers with semantically identical editable text or Word math;
- convert time words such as `hr/min/sec` to equivalent thesis notation without changing numbers.

Forbidden without explicit authorization:

- recomputing averages;
- changing precision;
- excluding failed sequences from a newly presented average;
- combining several source tables into a summary table;
- splitting a source table into different semantic groupings;
- replacing `×` with zero, blank, or an estimated value;
- “correcting” source bolding based on the agent’s own minimum calculation;
- silently choosing narrative values over conflicting table values.

### Figure preservation

For each experimental figure:

- map the caption to the exact embedded media relationship;
- hash the original media bytes;
- inspect the source crop rectangle and aspect ratio;
- reproduce the source crop when the embedded file contains unused whitespace;
- insert the full experimental figure in its original order;
- preserve subfigure content and color semantics.

Do not:

- recreate the figure from visual memory;
- use a page screenshot when the embedded media is available;
- replace a source figure with a placeholder;
- crop away subfigures, legends, axes, labels, or sensor thumbnails;
- translate pixels unless image editing is explicitly requested.

### Conflict handling

When table and prose disagree:

1. Record both values and their source locations.
2. Preserve the table exactly.
3. Use the tabulated value in the thesis analysis unless the user directs otherwise.
4. Do not recompute or silently normalize the source.

### Minimum validation evidence

Create a validation report containing:

- final DOCX SHA-256;
- Word-rendered page count;
- source and final data-table counts;
- per-table numeric-token counts and exact-order comparison;
- per-table failure-mark counts;
- per-table bold data-cell coordinate comparison;
- source-crop and embedded-image hashes;
- placeholder count;
- citation and EndNote field counts;
- strict DOCX quality result;
- final pass/fail status.
<!-- END SOURCE: experiment-fidelity-contract.md -->
