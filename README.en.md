# Paper Agent

[简体中文](README.md) | **English**

Paper Agent is a Codex skill for writing, revising, and checking research papers and theses. It connects source evidence, research questions, methods, experiments, and conclusions, while preserving the parts of a document that the user has frozen.

It supports complete manuscripts and focused tasks: a method section, experiment analysis, editable research diagrams, citation work, conclusions, or a specific Word correction. Word and PowerPoint work includes inspection of the saved document's visible layout, not only its internal XML.

![Paper Agent: inputs, capabilities, and deliverables](docs/images/paper-agent-overview.svg)

## Start here

1. Install this repository as a skill in your Codex environment.
2. Create a **separate, private paper workspace** and put your manuscript, source evidence, and formatting rules there.
3. Invoke `$paper-agent` in a Codex conversation and identify the exact files, requested changes, output location, and protected content.
4. Provide any missing evidence or task-specific parameters. Review a diagram skeleton when the workflow requires one.
5. Receive the requested files after content, preservation, and visual checks appropriate to the task.

For example, send this as a **chat message**, replacing the project path:

```text
Use $paper-agent to revise /path/to/paper-project/source/manuscript.docx.
Apply the rules in /path/to/paper-project/style/formatting-rules.md.
Improve the connection between the research questions, methods, experiments,
and conclusions. Preserve all experimental values, equations, citation fields,
heading levels, and source figures. Save the revised DOCX and a concise change
record to /path/to/paper-project/output/. Keep the original unchanged.
```

`$paper-agent` is a **skill invocation in conversation**, not a terminal command. There is no `paper-agent` executable that automatically writes a paper. The bundled scripts support specific extraction, conversion, and audit steps; the host agent coordinates the workflow.

## Install

The current Codex skills documentation uses `~/.agents/skills` for user-level skills; project-level skills can live in the project's `.agents/skills` directory. See the [official skill-building guide](https://learn.chatgpt.com/docs/build-skills). Installation requires Git, network access to GitHub, repository read access, and permission to write to the target directory.

### Windows PowerShell

```powershell
$skillRoot = Join-Path $HOME '.agents\skills'
$skillTarget = Join-Path $skillRoot 'paper-agent'
New-Item -ItemType Directory -Path $skillRoot -Force | Out-Null
if (Test-Path -LiteralPath $skillTarget) {
    throw 'paper-agent already exists. Back it up and choose one active installation before continuing.'
}
git clone https://github.com/huashu996/Paper-agent.git $skillTarget
```

### macOS / Linux / Bash

```bash
skill_root="$HOME/.agents/skills"
skill_target="$skill_root/paper-agent"
mkdir -p "$skill_root"
if [ -e "$skill_target" ]; then
  printf '%s\n' 'paper-agent already exists. Back it up and choose one active installation before continuing.' >&2
  exit 1
fi
git clone https://github.com/huashu996/Paper-agent.git "$skill_target"
```

Before replacing an existing installation, copy it to a backup directory **outside the active skills directories**. Preserve local modifications and use only one active copy. Some existing hosts discover skills under `~/.codex/skills`; use the actual directory supported by your host instead of installing a second copy under another path. Restart or refresh the host if it does not discover the new skill. The installed directory must contain `SKILL.md` directly, not another nested repository directory.

If the repository is private, obtain access and configure GitHub authentication before cloning. Do not place access tokens in this README or in example scripts.

### Dependencies and platform support

Install dependencies only for the work you intend to perform. A Python virtual environment is recommended.

| Component | Needed for |
| --- | --- |
| A Codex host with skill and file/tool support | Loading `SKILL.md`, planning, executing, and reviewing tasks |
| Python 3.10 or newer; 3.12 recommended | Bundled Python helpers and audits |
| `lxml` | XML-based document and presentation inspection |
| `scripts/figure/requirements.txt` | Figure and formula helpers: `latex2mathml`, Pillow, PyMuPDF, `python-pptx`, and Windows-only `pywin32` |
| Poppler's `pdftotext` on `PATH` | PDF text extraction by `build_method_rag.py` |
| A compatible document renderer and required fonts | Checking actual page layout; availability depends on the host |
| The host's `documents` and `pdf` companion skills/tools, where referenced | Document and PDF handling used by the selected workflow; these are separate host capabilities, not bundled Python packages |
| Windows with desktop Microsoft Word / PowerPoint | Workflows that use native Office COM, native application rendering, and PowerShell/VBScript helpers |
| EndNote and its Word integration | Real, updateable Cite While You Write (CWYW) citation insertion |
| MathType | Tasks explicitly requesting MathType OLE equations |

From the installed skill directory, within your chosen Python environment:

```bash
python -m pip install lxml
python -m pip install -r scripts/figure/requirements.txt
```

The second command is needed for the corresponding figure/formula tooling, not for every writing task. Installing Python packages does not install Office, EndNote, MathType, fonts, or Poppler. Text work and several file-based audits can run across platforms; full native Office, CWYW, and MathType workflows require their compatible desktop applications. A missing application must be reported rather than replaced with a misleading imitation of its output.

This repository is an instruction-and-tool package for an agent host. Cloning it does not install a standalone desktop application, automatically grant access to your files, or configure every companion skill. Before a Word/PDF task, make the corresponding document and PDF capabilities available in your host and confirm that its renderer works in that environment.

## Two different directory structures

### 1. The skill repository

This directory contains reusable instructions and tooling. It is not the place to store your manuscript or research data.

```text
Paper-agent/
├── SKILL.md                         # Entry point and shared rules
├── README.md                        # Chinese usage guide
├── README.en.md                     # English usage guide
├── agents/
│   └── openai.yaml                  # Host-facing skill metadata
├── assets/
│   └── paper-figure-style-template.pptx
├── references/                      # Task-specific workflows and quality gates
│   ├── method-and-word-workflow.md
│   ├── experiment-workflow.md
│   ├── figure-workflow.md
│   ├── literature-citation-workflow.md
│   ├── full-thesis-final-optimization.md
│   ├── red-instruction-revision-workflow.md
│   └── ...
├── scripts/
│   ├── method/                      # Retrieval and Word inspection
│   ├── experiment/                  # Experiment table audits
│   ├── citation/                    # Metadata, references, styles, and CWYW helpers
│   └── figure/                      # Office equations, PPT geometry, and rendering audits
├── templates/                       # Literature and style process templates
└── docs/
    └── images/                      # README illustrations
```

The bundled [PowerPoint style template](assets/paper-figure-style-template.pptx) is a reusable layout asset. Instructions in `references/` explain when and how to use it; it does not establish evidence for your research claims.

### 2. Your private paper workspace

The following is a recommended organization, not a mandatory parser schema. Existing projects can retain their layout if you clearly identify each input and output path.

```text
paper-project/
├── source/
│   ├── manuscript.docx              # Authoritative manuscript, preserved as the baseline
│   └── revision-instructions.txt    # Review comments or requested edits
├── resource/
│   ├── papers/                      # Papers that may support the manuscript
│   ├── notes/                       # Reading notes and research outline
│   └── references.bib               # Optional bibliography export
├── style/
│   ├── formatting-rules.md          # Your explicit formatting contract
│   ├── university-template.docx     # Or the journal's authorized template
│   └── figure-reference.png         # Optional visual reference
├── data/
│   ├── raw/                         # Original measurements and logs; keep unchanged
│   └── processed/                   # Existing result tables with provenance
├── figures/
│   ├── source/                      # Editable PPTX, SVG, plots, and supplied image assets
│   └── reference/                   # References for style or faithful reconstruction
├── output/                          # Requested final deliverables only
└── build/
    └── paper-agent/
        └── <timestamp>/             # Working copy, evidence, logs, and QA
            ├── source/
            ├── rag/
            ├── draft/
            ├── citations/
            ├── figures/
            ├── tables/
            ├── qa/
            └── deliverables/
```

Put raw measurements in `data/raw/`, supporting publications in `resource/papers/`, and school or journal rules in `style/`. The manuscript's existing outline remains authoritative unless you authorize a change; a supporting paper must not silently replace it. Put exact revision requests in `source/revision-instructions.txt` or point to the annotated DOCX. Keep temporary PDFs, screenshots, retrieval indexes, and audit logs under `build/`, separate from `output/`.

Not every task creates every build subdirectory. A small correction should have a small working footprint. Never copy your private workspace into the public skill repository.

## Worked example: revise one experiment section

This example follows one task from input placement to checking the result. It uses generic file names; you supply your own actual evidence.

**1. Prepare a small workspace.** Create `paper-project/` outside the installed skill. Put the manuscript in `source/manuscript.docx`, the verified result table in `data/processed/results.csv`, the evaluation protocol in `resource/notes/protocol.md`, and its existing plots in `figures/source/`. Put the required fonts, spacing, heading styles, and caption rules in `style/formatting-rules.md`. Do not create fake results merely to fill this structure.

A minimal `formatting-rules.md` could say:

```text
Authoritative template: university-template.docx in this directory.
Preserve the manuscript's page orientation, headers, footers, heading hierarchy,
and equation-numbering scheme. Use the template's styles for body text,
headings, figure captions, table captions, and table notes.
Freeze experimental values, units, precision, failure markers, and citation fields.
New figures and tables need in-text references; keep captions with their objects.
Save a new output file without overwriting the manuscript in source/.
```

**2. Open the workspace in your host and send the task.** Replace the absolute root path below. Relative paths inside the prompt are resolved under that root.

```text
Use $paper-agent in experiment_only mode.
My workspace is /path/to/paper-project/.
Revise only Section 4, Experiments, from source/manuscript.docx.
Use data/processed/results.csv, resource/notes/protocol.md, and figures/source/.
Follow style/formatting-rules.md. Explain the dataset and settings, metrics,
comparative results, and limitations supported by these materials.
Freeze all result values, row order, units, failure markers, existing equations,
EndNote fields, heading hierarchy, and all sections outside Section 4.
Keep the input unchanged. Save the revised experiment section as
output/experiment-section.docx and its change record as output/change-record.txt.
Put rendering previews and audit details in build/.
If a setting is missing, identify it explicitly instead of guessing.
```

**3. Let the plan establish the scope.** The agent selects a mode and checks whether the protocol supports the requested explanations. A missing dataset split, measurement unit, or evaluation setting is an evidence gap. Supply it if available, or authorize a narrower statement. The draft and its verified tables remain the source of truth.

**4. Expect the files you requested.** With sufficient evidence and working tools, the final layout is:

```text
paper-project/
├── source/manuscript.docx                    # Preserved original
├── output/
│   ├── experiment-section.docx              # Requested experiment section
│   └── change-record.txt                    # Changes, checks, and remaining gaps
└── build/paper-agent/<timestamp>/
    ├── qa/                                  # Page renders and relevant audits
    └── ...                                  # Intermediate working material
```

These output names come from the prompt; they are not fixed names imposed by the skill. A separate diagram task would request its own `.pptx` and preview instead of automatically adding them to this experiment task.

**5. Know what verification means.** The change record should identify the actual scope and completed checks. Result values, units, and failure markers must match the original table; claims must follow from those results; figures and tables must have matching in-text references; equations and citation fields must remain intact. The final saved pages and affected neighbors should show no clipped tables, separated captions, or unintended blank space. These are checks the workflow must perform before delivery, not a substitute for checking evidence it never received.

## Choose the task, not a complicated configuration

Describe what you want in ordinary language. Paper Agent selects **one primary mode**, the relevant capability modules, and an execution tier. You can name these explicitly when useful.

| Primary mode | Typical inputs | Typical requested output |
| --- | --- | --- |
| `full_paper` | Draft or outline, source evidence, experiments, formatting rules | Complete manuscript revision or evidence-grounded manuscript, with relevant figures and checks |
| `method_only` | Target outline, method draft, algorithm/code, supported derivations | Method section with consistent definitions, equations, and explanations |
| `experiment_only` | Source experiments, result tables, plots, evaluation protocol | Experiment and analysis section preserving reported data |
| `figure_only` | Authorized source text or reference image, assets, diagram parameters | Editable research diagram PPTX and requested preview |
| `literature_citation` | Approved literature or EndNote Library/Group, writing scope | Supported prose and the authorized citation workflow |
| `conclusion_only` | Actual methods, results, and limitations | Conclusions and future work bounded by existing evidence |
| `revision_only` | Exact document and specific changes or annotations | Focused revision of the authorized content and objects |

The six optional modules are `word_layout`, `equation`, `figure_ppt`, `experiment_evidence`, `citation_endnote`, and `rag`. Modules load the relevant workflow rather than expanding the task automatically.

| Tier | Intended scope | Verification |
| --- | --- | --- |
| `fast_local` | Usually one page or no more than 10 objects, without chapter or main-topology changes | Immediate rollback protection, affected-page rendering, and relevant object checks |
| `standard` | A section, several connected pages, or a new diagram page | Affected-scope rendering, applicable audits, and consolidated review |
| `submission` | Chapter restructuring, full-manuscript work, or submission preparation | Full-scope rendering, preservation checks, chapter boundaries, and delivery audit |

Tiers change verification scope and iteration cost, not the requirement to preserve evidence. A request for full final-manuscript optimization routes to `full_paper + submission`; a genuinely local correction should not turn into a complete rewrite.

## How the work proceeds

![Planning, execution, review, and revision flow](docs/images/workflow.svg)

**Planner → Executor → Reviewer are three logical responsibilities inside one skill.** They are not three separately installed skills, and this workflow does not start three independent agents by default.

1. **Identify the source of truth.** Specify the latest manuscript, relevant data, template, source literature, and exact target files. Identify content that may change and content that must remain frozen.
2. **Plan the authorized change.** Select the mode, modules, tier, acceptance criteria, and applicable workflows. Resolve missing parameters that materially affect the result.
3. **Establish the baseline.** Diagnose before editing, preserve the original, and create the necessary working copy and evidence records. Existing school or journal formatting becomes the document's continuing formatting contract.
4. **Execute with evidence.** Revise the authorized scope. Keep terminology and numbering connected across sections, trace statements to sources, and preserve original values, formulas, figures, and citation structures unless their modification is authorized. Missing evidence is reported, not invented.
5. **Check content and layout together.** Review affected pages as edits change pagination. New diagrams require confirmed parameters and a static skeleton before formal PPT construction. Citation work uses the specified source scope and, when requested, real CWYW fields.
6. **Review the final saved state.** Examine visible results and appropriate structural checks. Failed implementation returns to execution; a problem with scope, evidence, or authorization returns to planning. Any subsequent edit invalidates the prior review.
7. **Deliver the requested files.** Separate final files from build artifacts and state what was changed, what was preserved, what was actually checked, and any unresolved limitations.

The normal state sequence is `USER_INPUT → PLANNED → EXECUTING → READY_FOR_REVIEW → APPROVED → DELIVERED`. “Approved” here describes the workflow's review result; it is not journal acceptance or a claim that an institution has approved the manuscript.

## Copyable task prompts

Replace every example path and bracketed value with your own. State your intended output path and frozen content each time. Windows users can use absolute paths such as `D:\paper-project\source\manuscript.docx`.

### Full manuscript revision

```text
Use $paper-agent in full_paper / submission mode.
Source: /path/to/paper-project/source/manuscript.docx.
Rules: /path/to/paper-project/style/formatting-rules.md.
Evidence: /path/to/paper-project/resource/ and /path/to/paper-project/data/.
Align the abstract, research questions, chapter introductions, methods,
experimental analysis, chapter summaries, and final conclusions.
Preserve experimental values, equations, citation fields, source figures,
and the existing heading hierarchy. Do not invent missing experiments.
Save a new final DOCX and change record under /path/to/paper-project/output/.
```

### Red annotations and itemized reviewer requests

```text
Use $paper-agent to revise /path/to/paper-project/source/annotated.docx.
Treat red comments and source/revision-instructions.txt as editing instructions.
Track each request to its location, action, supporting evidence, and verification.
Distinguish instructions from intended manuscript content before removing them.
Deliver a clean black-text copy and an itemized change record to output/.
Preserve original data, valid equations, figures, and EndNote fields.
```

### A local Word correction

```text
Use $paper-agent to fix Table 2 in /path/to/paper-project/source/manuscript.docx.
Apply the three-line table style specified in style/formatting-rules.md.
Keep the table values, row order, units, bold emphasis, notes, and caption unchanged.
Do not restyle equation layout tables or other tables. Check the table and any
neighboring page affected by the change. Save output/manuscript-table-fixed.docx.
```

### Experiment analysis from actual results

```text
Use $paper-agent in experiment_only mode.
Use source/experiment-draft.docx, data/processed/results.csv, the evaluation
protocol in resource/notes/protocol.md, and figures/source/.
Explain the settings, datasets, metrics, comparisons, ablations, and limitations
supported by these files. Preserve every source value and failure marker.
Do not fill missing settings by guessing. Follow style/formatting-rules.md
and save output/experiment-section.docx.
```

### An editable research diagram

```text
Use $paper-agent to create a method diagram from Section 3 of
/path/to/paper-project/source/manuscript.docx.
Target: /path/to/paper-project/output/method-diagram.pptx, a new single-slide file.
Use a 16:9 slide, a 16:9 diagram body, Arial 16 pt, and Office-native equations.
Use style/figure-reference.png for visual style only; use the manuscript for content.
Preserve the manuscript's terms, symbols, and dependencies. Reuse the supplied
assets in figures/source/ without redrawing them. Show a static skeleton first,
then build the editable PPTX after confirmation. Also export a PNG preview.
```

### What the bundled diagram layouts look like

The following images preview the bundled editable template. They are **generic layout illustrations**, not figures copied from a personal thesis or evidence of actual research results. Labels such as inputs, processing, and outputs demonstrate composition; a real task must replace them with terms traced to the authorized manuscript.

![Gallery of the five generic editable diagram layouts](docs/images/template-gallery.png)

Slides 1–2 provide starting points for background, problem, and source relationships; slides 3–5 illustrate method flows, branches, and local–global relationships. A larger method-layout example shows the separation of input, processing, and output areas:

![Generic method-layout example from the editable template](docs/images/template-method-example.png)

For a new figure, identify the source section, whether a reference controls content or only style, the page action, slide size, diagram-body ratio, font, and equation format. The agent checks the content-to-object mapping, presents a static skeleton for confirmation, builds native editable objects, and inspects the saved PPTX rendering. The reusable source is [assets/paper-figure-style-template.pptx](assets/paper-figure-style-template.pptx); the PNG previews illustrate it and do not replace the editable file.

### EndNote citation work

```text
Use $paper-agent for literature_citation with real EndNote CWYW fields.
Library: [absolute path to the EndNote library]. Group: [exact group name].
Use only that Group. Write related work for the topic [specific topic].
Target: /path/to/paper-project/source/manuscript.docx, Section 2.1.
Output Style: [exact style name]. Output: output/manuscript-cited.docx.
Keep all other sections, experimental data, and existing valid fields unchanged.
Present the source scope, insertion location, backup plan, and citation settings
for confirmation before active citation work. Do not substitute static numbers
for CWYW fields if the integration is unavailable.
```

### Conclusions bounded by the evidence

```text
Use $paper-agent to revise the conclusions in source/manuscript.docx.
Base them on the methods and experimental results already established there.
Connect each contribution back to a research question, and state the supported
scope, limitations, and future work. Add no new numbers, experiments, or novelty
claims. Preserve every other section and save output/manuscript-conclusion.docx.
```

## Optional local retrieval helpers

The `rag` module can organize permitted sources for evidence retrieval. The bundled implementation uses **SQLite FTS5 lexical search with BM25 ranking**, including Chinese bigram/trigram tokens. It does not create dense embeddings, use a vector database, or automatically validate a research claim.

From your private paper workspace, replace `/path/to/installed/paper-agent` with the installation path:

```bash
python /path/to/installed/paper-agent/scripts/method/build_method_rag.py --name project-evidence --sources ./resource/papers ./resource/notes --out ./build/paper-agent/evidence-rag
python /path/to/installed/paper-agent/scripts/method/query_method_rag.py --db ./build/paper-agent/evidence-rag/index/project-evidence.sqlite3 --query "evaluation assumptions and failure conditions" --top-k 8
```

Supported input extensions are `.pdf`, `.docx`, `.md`, `.txt`, `.tex`, `.bib`, and `.ris`. Directory inputs are searched recursively. PDF extraction requires `pdftotext`; the builder has no built-in OCR pipeline for scanned pages. It records extraction status, chunks, source metadata, candidate formula text, the SQLite index, and a coverage summary. Check these outputs before relying on search results.

Chunk defaults are `--target 1400`, `--maximum 2200`, and `--overlap 180` characters. Use a fresh output directory for a new index. `--force` is an explicit rebuild option; keep it restricted to the same named, generated knowledge base. Retrieved passages and formula candidates must be checked against the source, especially where extraction loses mathematical layout or context.

These helpers operate on local files. The privacy behavior of the assistant and its connected tools remains governed by the host and its settings; a local index is not a guarantee that every stage of an assisted writing session stays offline.

## Quality and scope boundaries

- **Evidence:** do not fabricate results, baselines, citations, novelty, mechanism explanations, or unsupported conclusions.
- **Preservation:** freeze requested data, headings, equations, media, page orientation, citation fields, and other protected objects before modification.
- **Tables:** classify Word tables by purpose. A data table, equation-numbering container, cover form, and image layout container must not receive the same bulk formatting treatment.
- **Editable outputs:** requested Office equations and PPT objects must be genuinely editable; screenshots and typed citation numbers do not substitute for native objects or CWYW fields.
- **Visible quality:** inspect the final saved rendering for clipping, collisions, orphan captions, broken pagination, distorted figures, and unwanted blank content. XML validity alone is insufficient.
- **Application boundaries:** native PowerPoint operations are restricted to the authorized target presentation; unrelated presentations must not be modified or closed.

The skill cannot supply evidence that was never collected, guarantee publication or institutional acceptance, or guarantee any plagiarism/AIGC detector score. Requirements beyond the available data or installed tools must be stated explicitly. School-specific defaults apply only when the relevant template is requested; they are not universal publishing standards.

Keep personal manuscripts, names, contact details, institution-specific identifiers, unpublished datasets, private bibliographies, local-path inventories, credentials, and session logs out of this public repository. Before sharing a customized copy, inspect text files **and** embedded document metadata, comments, notes, hidden content, and binary assets. Generated retrieval records can include full source paths and source text, so keep their outputs in the private workspace.

The public examples and diagram assets use generic research-workflow labels. The release uses a newly built editable template rather than personal manuscript figures. Your manuscript and its evidence belong in your separate private project, never in the installed skill folder or the public repository's `assets/` directory. Installing a skill does not authorize publication of your files. See the [release privacy notes](docs/PRIVACY.md) for the package's checks and their scope, including the distinction between current files and Git history or third-party copies.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| The skill is not available | Confirm the host's actual skill directory, a single active installation, and `paper-agent/SKILL.md`; refresh the host. |
| Cloning returns 404 or an authentication error | If the repository is private, confirm that your account has read access and GitHub authentication is configured; never embed a token in shared commands. |
| The skill asks for diagram parameters | Specify the target PPTX, page action, slide and diagram-body ratios, fonts, formula format, and reference-image purpose. New diagram tasks do not silently inherit old parameters. |
| A PDF produces no useful retrieval results | Check extraction status, the `pdftotext` installation, whether the PDF contains selectable text, and source coverage. |
| A DOCX looks different on another computer | Check fonts, Office/rendering versions, and the template; verify the actual target rendering before delivery. |
| CWYW insertion cannot run | Confirm Windows/Word/EndNote integration and the exact Library, Group, and Output Style. Do not accept static numbers as equivalent fields. |
| A requested result has insufficient evidence | Supply the missing source or narrow the claim; the workflow must not invent a result. |
| A small correction triggers broad changes | Restate the exact page/object, frozen scope, and output path; use `fast_local` when the change meets its limits. |

## File navigation

| Task or reference | Entry point |
| --- | --- |
| Overall contract, routing, and shared rules | [SKILL.md](SKILL.md) |
| Full-thesis final revision | [Full revision workflow](references/full-thesis-final-optimization.md) |
| Red annotations and itemized requests | [Revision closure workflow](references/red-instruction-revision-workflow.md) |
| Methods and Word documents | [Method and Word workflow](references/method-and-word-workflow.md) |
| Chinese thesis prose | [Language style](references/chinese-thesis-language-style.md) |
| Experiments | [Experiment workflow](references/experiment-workflow.md) |
| Research diagrams | [Figure workflow](references/figure-workflow.md) and [text-to-figure workflow](references/text-to-figure-workflow.md) |
| Literature and EndNote | [Citation workflow](references/literature-citation-workflow.md) |
| Word table classification | [Table object gate](references/table-object-classification-gate.md) |
| Persistent layout and page orientation | [Layout gate](references/layout-first-portrait-page-gate.md) |
| Requested Southeast University thesis layout | [Institution-specific layout reference](references/seu-thesis-layout.md) |
| Script usage | Run the relevant Python script with `--help`; inspect PowerShell script parameters before execution. |

The README explains how to use the package. `SKILL.md` and the selected workflow files define its detailed execution rules, subject to the user's explicit instructions and the host's permissions.
