# Literature Writing and EndNote CWYW Workflow

## Contents
- Interactive task configuration
- Import, metadata validation, and EndNote group scope
- Related-work writing and semantic citation matching
- Real CWYW insertion and hyperlink validation
- Style learning, Word formatting, and quality control
- Examples, tests, and IEEE RA-L two-column workflow

<!-- BEGIN SOURCE: 00_interactive_task_configuration.md -->
## Interactive Task Configuration

This file is the mandatory front gate for every EndNote-Helper-Skill task.

### Highest Priority Rule

Before reading an EndNote group, generating text, inserting citations, importing references, modifying Word, or changing files, the assistant must:

1. identify the requested function;
2. check which required parameters are already provided;
3. ask only for missing required parameters;
4. ask all missing required parameters together where practical;
5. avoid repeating questions for information the user already supplied;
6. produce a task configuration summary after the user answers;
7. ask the user to confirm the summary;
8. wait for an explicit confirmation such as `确认执行`;
9. execute only after confirmation.

Do not treat recommended defaults as confirmed user requirements. Defaults are allowed only when the user explicitly says `使用默认设置直接执行`, `按默认设置执行`, or equivalent. Even then, output the task configuration summary before execution.

### Task States

- `TASK_DETECTED`: requested function identified.
- `PARAMETERS_INCOMPLETE`: required parameters are missing; ask questions.
- `WAITING_FOR_CONFIRMATION`: task summary has been produced; wait for confirmation.
- `READY_TO_EXECUTE`: user confirmed the task summary.
- `EXECUTING`: confirmed task is running.
- `QUALITY_CHECK`: output is being verified.
- `COMPLETED`: task is complete.
- `BLOCKED`: required file, EndNote group, Word/EndNote capability, or user decision is unavailable.

Only `READY_TO_EXECUTE` permits modifying EndNote, reading a specified group, generating final prose, inserting CWYW citations, or writing Word files.

### Function Type Selection

If the task is unclear or the user only says to use the skill, ask:

```text
请选择本次需要执行的功能：

A. 将网页、DOI、PDF 或文献文件导入 EndNote
B. 整理或检查指定 EndNote Group
C. 基于指定 EndNote Group 撰写 Related Work
D. 为已有正文补充 EndNote 引用
E. 学习指定论文或 Word 文档的写作风格
F. 学习并复用 Word 排版格式
G. 修改已有 Related Work
H. 检查正文引用、参考文献和超链接
I. 执行以上多个功能的组合工作流
```

Then ask the parameter set for the selected function.

### Required Questions By Function

#### A. Reference Import

Ask for missing items:

- source type: webpage links, DOI, PDF, BibTeX, RIS, EndNote XML, list file;
- source path or pasted source content;
- target EndNote library;
- target EndNote group: existing group, new group, or library only;
- version preference: journal, conference, Early Access, arXiv, keep all;
- duplicate handling: report only, skip, keep formal version, ask per item;
- whether to download and attach PDFs;
- whether to complete Abstract, Keywords, DOI, URL, and publication fields;
- output files: RIS, BibTeX, EndNote XML, import report, all.

Do not import before confirmation.

#### B. EndNote Group Checking

Ask for missing items:

- EndNote library;
- EndNote group;
- checks required: metadata, duplicates, missing PDF, missing abstract, publication status, group membership;
- whether to modify records or only report;
- desired output report format and path.

#### C. Related Work Writing

Ask for missing items:

- EndNote library;
- EndNote group;
- whether only group references may be cited;
- whether external references may be added;
- year range and excluded source types;
- topic, paper/chapter title, user's work or innovation points, target method/chapter served by this related work;
- desired organization: time, technical route, sensor, algorithm framework, optimization, centralized/distributed, single/multi-robot, localization/mapping/reconstruction/understanding, traditional/learning, discrete/continuous time, custom outline, or skill recommends outline after reading and user confirms;
- language;
- document type: doctoral thesis, journal paper, conference paper, report;
- continuous prose or subsections;
- section title and numbering;
- whether to keep existing title structure;
- background opening, subsection summaries, final link to user's work;
- whether lists are allowed;
- style sample file and specific section/page range;
- style dimensions to learn: language, sentence length, paragraph structure, citation density, comparison method, critical analysis, transitions, Word formatting;
- target words or pages;
- page estimation basis if pages are requested;
- subsection allocation;
- maximum length and paragraph length control;
- citation insertion requirement;
- citation mode: real EndNote CWYW, temporary placeholders, no citations;
- EndNote output style;
- numeric or author-year format;
- grouped citations allowed;
- citation density;
- whether all group references must be cited;
- bibliography generation;
- citation-to-bibliography navigation;
- DOI and URL hyperlinks;
- Word write requirement;
- target Word file;
- exact insertion location;
- replace, append, or optimize existing text;
- preserve existing EndNote fields, comments, and tracked changes;
- tracked changes on/off;
- reuse target Word styles;
- update table of contents and bibliography;
- output path;
- backup requirement.

Do not read the EndNote group, draft final text, insert citations, or write Word until confirmation.

#### D. Insert Citations Into Existing Text

Ask for missing items:

- target Word file;
- chapter, section, paragraph, or range;
- EndNote library;
- EndNote group;
- output style;
- real CWYW or placeholders;
- whether source text may be modified;
- existing citation handling: restore original sources or treat static numbers as placeholders and choose suitable group references;
- sentence-level or paragraph-level matching;
- permitted optimization scope: citation-only, wording/grammar, claim narrowing, sentence reordering, transition improvement, or paragraph restructuring;
- unsupported-claim policy: leave and report, revise within permission, or ask before revision;
- multiple citations per sentence allowed;
- bibliography update;
- citation-to-bibliography navigation;
- DOI/URL hyperlink requirements;
- whether to report uncited records and unsupported claims.

If the user says existing content may be modified according to available references, treat that as permission for limited evidence-based and logic-improving edits, not permission for a full rewrite. Preserve the paragraph's research intent and report material meaning changes.

Do not match references only by keywords. Read enough evidence to support each citation.

#### E. Style Learning

Ask for missing items:

- style source file;
- section, chapter, or page range;
- Chinese or English style;
- dimensions to learn: language, paragraph, logic, citation, terminology, headings, formatting, all;
- whether to generate `style_profile.md`;
- whether to immediately apply the style;
- target writing task;
- target length.

#### F. Word Formatting Learning

Ask for missing items:

- template Word file;
- section or sample paragraphs to learn;
- styles to learn;
- target Word file;
- application range;
- whether to preserve existing target styles;
- whether new styles may be created;
- whether to process headings, body, captions, equations, bibliography;
- whether to update table of contents;
- whether to preserve headers, footers, pagination, and sections;
- backup requirement.

#### G. Existing Related Work Revision

Ask for missing items:

- source file and section;
- task type: polish, restructure logic, add references, full rewrite;
- preserve original paragraph structure;
- preserve original citations;
- allow deleting irrelevant citations;
- EndNote group for supplemental references;
- allow external references;
- target words or pages;
- writing style;
- write back to Word;
- preserve EndNote CWYW fields;
- output revision notes or comparison table.

#### H. Citation, Bibliography, And Link Checking

Ask for missing items:

- target Word file;
- check scope;
- expected EndNote library/group if relevant;
- whether to check CWYW fields, bibliography synchronization, numbering continuity, citation jumps, DOI links, URL links, duplicate bibliography entries;
- whether to modify or report only;
- report output path.

#### I. Combined Workflow

Ask once for all relevant staged parameters:

- import parameters: sources, library, group, version choice, duplicate handling, PDF attachment;
- related-work parameters: topic, scope, outline, language, style, words/pages, citation density, use all references;
- Word and citation parameters: target file, insertion location, replace/append/optimize, CWYW, output style, hyperlinks, bibliography update, output path.

Execute stages only after the combined configuration is confirmed.

### Related Work Question Template

Use this template when many parameters are missing:

```text
开始前需要确认本次写作配置。请填写以下信息；已明确的项目可以保留当前设置。

1. EndNote Library：
2. EndNote Group：
3. 是否仅使用该 Group 内文献：
4. Related Work 主题：
5. 论文或章节题目：
6. 本文研究内容或创新点：
7. 写作语言：
8. 文档类型：博士论文 / 期刊论文 / 会议论文
9. 写作大纲：
10. 组织逻辑：
11. 写作风格参考文件：
12. 需要学习的章节或页码：
13. 目标字数：
14. 目标页数：
15. 每小节篇幅：
16. 是否插入文献引用：
17. 引用方式：EndNote CWYW / 临时引用 / 不插入引用
18. EndNote Output Style：
19. 是否生成文后参考文献：
20. 是否生成正文到参考文献的跳转：
21. 是否添加 DOI 和 URL 超链接：
22. 目标 Word 文件：
23. 写入位置：
24. 原内容处理方式：保留优化 / 替换 / 追加
25. 是否备份原文件：
26. 输出文件路径：
27. 其他特殊要求：
```

### Simplified Question Mode

When the user already supplied most parameters, ask only missing items. Example:

```text
当前还需要确认以下 5 项：

1. 使用哪个 EndNote Library？
2. 是否仅引用该 Group 内文献？
3. EndNote Output Style 沿用目标 Word 当前样式，还是指定其他样式？
4. 原内容处理方式：替换 / 保留优化 / 追加？
5. 输出文件路径是否覆盖原文件？
```

### Task Configuration Summary

After the user answers, output:

```text
任务配置摘要：

- 执行功能：
- EndNote Library：
- EndNote Group：
- 文献范围：
- 写作主题：
- 写作语言：
- 文档类型：
- 大纲结构：
- 组织逻辑：
- 写作风格：
- 目标字数：
- 目标页数：
- 引用方式：
- Output Style：
- 是否插入参考文献：
- 超链接要求：
- 目标 Word：
- 写入位置：
- 原文处理方式：
- 现有引文处理方式：恢复原来源 / 作为占位符重新匹配：
- 语义匹配粒度：
- 允许的正文优化范围：
- 无法支撑的句子处理方式：
- 输出路径：

请确认以上配置。回复“确认执行”后开始；需要调整时请直接指出修改项。
```

Remain in `WAITING_FOR_CONFIRMATION` until the user confirms.

### Default Values

Only use defaults when the user explicitly allows defaults. Suggested defaults:

- language: infer from user input;
- document type: doctoral thesis;
- reference scope: specified EndNote group only;
- organization: technical route;
- citation mode: real EndNote CWYW;
- output style: current Word EndNote output style;
- writing style: current target Word section;
- original text handling: preserve and optimize;
- Word styles: reuse target document styles;
- hyperlinks: preserve EndNote-supported links;
- backup: create before modification.

Even with defaults, output and confirm the task configuration summary.

### Forbidden Behavior

- Do not read the whole library when no group is specified.
- Do not choose an EndNote group automatically.
- Do not choose outline, length, citation mode, or Word insertion point automatically.
- Do not insert citations if the user has not requested or confirmed citation insertion.
- Do not write Word when target location is unclear.
- Do not continue after asking questions before the user answers.
- Do not treat recommended settings as confirmed settings.
<!-- END SOURCE: 00_interactive_task_configuration.md -->

<!-- BEGIN SOURCE: 01_endnote_import.md -->
## EndNote Import Workflow

### Supported Inputs

- paper URLs, DOI lists, publisher pages, Google Scholar snippets, IEEE Xplore, Springer, Elsevier, Wiley, ACM, arXiv, author pages;
- BibTeX, RIS, EndNote XML;
- PDF files and folders;
- text files, CSV, Excel-like exports, or pasted lists containing many links or identifiers;
- official webpages, standards pages, government notices, and online documentation.

### Import Principles

- Prefer official publisher metadata and DOI metadata over partial webpage text.
- Prefer formally published records over arXiv/preprint/author-page PDF records.
- Do not fabricate missing volume, issue, pages, DOI, URL, abstract, keywords, or publisher.
- If publication status cannot be confirmed, mark `[Publication status requires verification]`.
- If required fields are missing, mark `[Metadata incomplete]`.
- Do not import duplicates silently.

### Procedure

1. Create `build/endnote-helper/<timestamp>/`.
2. Normalize input into a source table with: `source_id`, `source_type`, `input`, `notes`.
3. For DOI input, resolve DOI metadata when network access is allowed; otherwise mark it for verification.
4. For publisher pages, extract title, authors, venue, year, DOI, URL, abstract, and publication status.
5. For PDFs, extract title/first page metadata when possible, but verify against DOI/publisher metadata before import.
6. Generate an import file: RIS by default, BibTeX or EndNote XML if requested.
7. Import into the target EndNote library.
8. Add imported records to the requested group.
9. Confirm assigned EndNote record numbers after import.
10. Produce an import report with successful imports, skipped items, incomplete records, and duplicate candidates.

### Website Records

For web sources, capture at least:

- corporate author or author;
- year;
- title;
- website/publisher;
- publication or update date;
- URL;
- access date;
- document type.

Use `Web Page` for ordinary web pages and `Government Document`, `Report`, or `Standard` when the output style handles those types correctly.

For Chinese corporate authors, use a trailing comma in EndNote when needed to prevent name inversion, for example:

`示例机构,`

### Minimal RIS Example For A Website

The following record is fictional and illustrates syntax only. Replace every example value with verified metadata before importing.

```ris
TY  - ELEC
AU  - 示例机构,
PY  - 2000
TI  - 示例网页标题（仅说明元数据格式）
T2  - 示例机构
PB  - 示例机构
DA  - 2000/01/01
UR  - https://example.org/page.html
Y2  - 2000/01/02
ER  -
```

### Output Artifacts

- `sources.csv`
- `import_candidates.ris` or equivalent
- `import_report.md`
- `metadata_validation.json`
- `duplicate_candidates.json`
<!-- END SOURCE: 01_endnote_import.md -->

<!-- BEGIN SOURCE: 02_metadata_validation.md -->
## Metadata Validation

### Required Fields

Check each record for:

- `Author`
- `Year`
- `Title`
- `Journal` or `Conference`
- `Volume`
- `Issue`
- `Pages`
- `DOI`
- `URL`
- `Publisher`
- `Document Type`
- `Abstract`
- `Keywords`
- `Accession Number`
- `PDF Attachment`

Not every document type needs every field. For example, a conference paper may not have issue, and a website may not have pages. Mark missing fields according to document type rather than blindly failing every empty field.

### Status Labels

Use exact labels:

- `[Publication status requires verification]`
- `[Metadata incomplete]`
- `[The conclusion of this paper requires manual verification]`

### Version Preference

For same or near-same papers, default preference is:

1. formal journal version with volume/issue/pages;
2. formal conference version;
3. publisher early access;
4. accepted manuscript;
5. arXiv/preprint;
6. author homepage PDF;
7. temporary download page or search result.

Do not delete lower-priority versions automatically. Report candidates.

### Duplicate Signals

- Same DOI: high-confidence duplicate.
- Same title after normalization: high-confidence duplicate.
- High title similarity and overlapping author/year: candidate duplicate.
- Same arXiv ID and similar title: candidate duplicate.
- Same PDF filename only: weak signal.

### Validation Output

For each record report:

- record number if known;
- title;
- DOI;
- document type;
- missing fields;
- publication status;
- duplicate candidate IDs;
- recommended action.
<!-- END SOURCE: 02_metadata_validation.md -->

<!-- BEGIN SOURCE: 03_endnote_group_workflow.md -->
## EndNote Group Workflow

### Scope Rule

When the user specifies an EndNote group, use only that group unless the user explicitly allows using the whole library or adding external references.

### Required Group Report

Before writing, report or save:

- target library;
- target group name;
- number of records found;
- record numbers if available;
- records with missing PDF;
- records with missing abstract;
- records with incomplete metadata;
- duplicate candidates;
- unreadable records;
- records outside scope that were excluded.

### Reading Strategy

1. Prefer EndNote UI/export for exact group membership.
2. If using `.Data/rdb/refs.MYD`, treat group membership parsing as fragile and verify when exact membership matters.
3. Build a literature analysis table before drafting.
4. Track which records support each paragraph/topic.
5. For existing prose, track the exact sentence or proposition supported by each record and the evidence level used.
6. Do not infer citation mapping from static numbers or group order.
7. Do not force irrelevant records into unrelated paragraphs. If permitted, minimally narrow, reorder, or optimize the sentence and its transitions to match available evidence; otherwise report it as unsupported.
8. List unused records and the reason: irrelevant, duplicate, unreadable, metadata incomplete, outside topic, or manually excluded.

### Evidence Discipline

Use citations only for claims supported by the cited record. If only title/abstract was read, do not make detailed claims about experiments unless the abstract supports them clearly.

When modifying existing text, preserve its research purpose and improve logical continuity without inventing claims. Log any material change in meaning and the record numbers that justify it.
<!-- END SOURCE: 03_endnote_group_workflow.md -->

<!-- BEGIN SOURCE: 04_related_work_writing.md -->
## Related Work Writing

### Inputs To Capture

- EndNote library and group;
- topic and research question;
- section titles and insertion location;
- target length;
- language;
- target journal, conference, or thesis style;
- style sample or Word template;
- whether real EndNote CWYW citations are required.

### Literature Analysis Fields

For each paper extract:

- research problem;
- core method;
- sensor or data type;
- optimization model;
- system framework;
- dataset or scenario;
- main experimental conclusion;
- advantages;
- limitations;
- relation to the user's work;
- recommended citation position;
- method category.

### Organization Logic

Do not write one paper per paragraph. Choose an organizing logic that fits the topic:

- technical evolution;
- sensor type;
- algorithm framework;
- optimization model;
- centralized vs distributed;
- single robot vs multi-robot;
- localization, mapping, reconstruction, understanding;
- traditional vs learning-based;
- discrete time vs continuous time;
- geometry vs semantics;
- research problem, progress, limitation.

Each subsection should follow:

1. problem background;
2. representative methods;
3. method relationships and evolution;
4. advantages;
5. shared limitations;
6. connection to the user's work.

### Writing Quality

- Use formal academic prose.
- Synthesize related methods instead of concatenating paper summaries.
- Put citations next to supported claims.
- Avoid exaggerating contributions.
- Avoid unsupported claims and generic filler.
- Avoid repetitive paragraph openings.
- Distinguish existing work from the user's proposed work.
- If a claim is uncertain, mark `[The conclusion of this paper requires manual verification]`.

### Thesis Style Guidance

For Chinese doctoral thesis writing:

- start from broad research demand and narrow to technical bottlenecks;
- build paragraphs around causal logic and method evolution;
- use transitions such as `然而`, `与此同时`, `在此基础上`, `可以看出`, `基于上述分析可知` only when logically needed;
- end subsections with problem-oriented convergence;
- preserve the target Word template's heading and body styles.
<!-- END SOURCE: 04_related_work_writing.md -->

<!-- BEGIN SOURCE: 05_cwyw_citations.md -->
## EndNote CWYW Citations

### Goal

Create real, updateable EndNote Cite While You Write fields in Microsoft Word. Plain text citations, static bibliography entries, or manually typed `[1]` references are not acceptable.

### Preconditions

- EndNote is installed and the target library is open.
- Word has EndNote CWYW add-in available.
- Target `.docx` is writable.
- EndNote record numbers are known or can be resolved.

### Temporary Citation Format

Use:

`{FirstAuthorSurname, Year #RecordNumber}`

For multiple references:

`{FirstAuthorSurname, Year #RecordNumber; SecondAuthorSurname, Year #RecordNumber}`

For corporate website authors:

`{CorporateAuthor, Year #RecordNumber}`

The record number is the reliable identifier. Author/year text helps EndNote disambiguate.

### Existing Text Insertion

Before replacing static citations in existing prose:

1. confirm whether static numbers represent original sources or replaceable placeholders;
2. complete a sentence-to-reference semantic mapping within the confirmed EndNote group;
3. make only the text and logic revisions the user allowed;
4. preserve coherent progression between the preceding claim, cited evidence, and following conclusion;
5. place each temporary citation beside the precise supported claim;
6. keep unsupported claims uncited and reported instead of inserting loosely related references.

Do not assume that `[1]` corresponds to group record 1 or to the first displayed EndNote item.

### Formatting

Run the EndNote formatting macro through Word, commonly:

- `Project.EndNoteMacros.ENFormatBibliography`
- `EndNoteMacros.ENFormatBibliography`
- `ENFormatBibliography`

After formatting, update tables of contents if needed and save.

### Verification

Inspect `word/document.xml`:

- require `ADDIN EN.CITE`;
- require `ADDIN EN.REFLIST` when bibliography is generated;
- require zero remaining temporary citations such as `{... #123}`;
- count Word fields through Word COM when possible.

Do not claim linked EndNote citations exist unless these checks pass.

### Prohibited Actions

- Do not use `ENRemoveFieldCodes` unless explicitly requested.
- Do not type bibliography manually.
- Do not manually renumber references.
- Do not replace EndNote fields with static hyperlinks.
<!-- END SOURCE: 05_cwyw_citations.md -->

<!-- BEGIN SOURCE: 06_word_hyperlinks.md -->
## Word Hyperlinks

### Link Layers

EndNote CWYW fields and Word navigation hyperlinks are different:

- `ADDIN EN.CITE` keeps citation data connected to EndNote.
- citation-number-to-bibliography jumps require Word hyperlinks/bookmarks or output-style support.
- DOI and URL links in the bibliography are separate hyperlink requirements.

### Required Checks When Requested

Inspect `word/document.xml` for:

- `<w:hyperlink`;
- `<w:bookmarkStart`;
- `w:anchor=`;
- DOI text or `https://doi.org/`;
- URL text.

### DOI And URL Rules

- Prefer DOI permanent links: `https://doi.org/<doi>`.
- If no DOI exists, use the official publisher page.
- Avoid temporary download URLs, redirect-only links, search result links, and irrelevant pages.
- Do not show duplicate DOI and URL unless the output style requires both.
- If DOI or URL is absent in the rendered bibliography, fix EndNote fields or output style and rerun CWYW formatting.

### Post-Processing Warning

If EndNote does not generate citation-number hyperlinks, a post-processing step can add bookmarks and internal hyperlinks only after final EndNote formatting. Warn the user that future EndNote updates may remove those post-processed links.
<!-- END SOURCE: 06_word_hyperlinks.md -->

<!-- BEGIN SOURCE: 07_style_learning.md -->
## Style Learning

### Supported Sources

- thesis or dissertation;
- journal or conference paper;
- Word template;
- existing chapter;
- writing guideline;
- high-quality related work sample.

### Extracted Style Profile

Save findings to `../templates/style_profile.md` or a task-specific copy in the build directory.

Capture:

- sentence average length;
- paragraph average length;
- terminology and bilingual forms;
- abbreviation first-use style;
- citation density;
- citation position;
- single-paper vs multi-paper citation grouping;
- comparison expressions;
- section opening patterns;
- paragraph transition patterns;
- critical-analysis patterns;
- how the user's work is introduced;
- expressions to avoid;
- figure, table, and equation reference style.

### Use Rules

- Follow the style profile at the level of structure, rhythm, terminology, and citation behavior.
- Do not copy source sentences.
- If the sample conflicts with the user's explicit instructions, follow the user.
- If the sample is weak or inconsistent, report the issue and extract only stable traits.
<!-- END SOURCE: 07_style_learning.md -->

<!-- BEGIN SOURCE: 08_word_formatting.md -->
## Word Formatting

### Inspect Before Writing

Read the target document or template for:

- heading levels;
- Chinese font;
- English font;
- body size;
- line spacing;
- paragraph spacing;
- first-line indent;
- margins;
- citation style;
- bibliography style;
- hanging indent;
- DOI and URL style;
- caption styles;
- chapter numbering.

### Writing Rules

- Reuse existing Word styles.
- Do not create conflicting styles.
- Do not manually type fake section numbers if Word numbering controls headings.
- Do not use spaces for alignment.
- Do not write body text into the table of contents, bibliography, header, footer, or caption areas.
- Do not break existing EndNote fields or cross-references.
- Create a timestamped backup before replacing or deleting document ranges.
- When citation matching requires permitted wording or logic changes, preserve the paragraph role, surrounding style, tracked changes policy, and existing field boundaries; prefer the smallest local edit.
- After writing, update TOC only if needed and verify visible heading order.

### Page Count

When the user requests pages, count body-text pages by default. Do not count bibliography pages unless explicitly requested.
<!-- END SOURCE: 08_word_formatting.md -->

<!-- BEGIN SOURCE: 09_quality_control.md -->
## Quality Control

### Before Final Response

Confirm:

- task type was detected before execution;
- all required parameters were collected;
- task configuration summary was shown to the user;
- user explicitly confirmed before EndNote, Word, or file modification started;
- no default values were used unless explicitly allowed;
- all specified records were processed;
- group scope was followed;
- metadata validation was performed;
- publication versions were distinguished;
- duplicate candidates were listed;
- imported records were added to the correct EndNote group;
- related work has clear organization logic;
- related work is not a paper-summary collage;
- every factual claim has support;
- every inserted citation has a documented sentence- or proposition-level semantic match;
- existing static citation numbers were not mapped by group order or keyword overlap alone;
- existing-text revisions stayed within the confirmed permission and material meaning changes were logged;
- transitions and sentence order remain coherent around inserted citations;
- unsupported claims were revised with permission or reported without forced citations;
- no unverified conclusions are stated as facts;
- no references outside scope were added;
- EndNote CWYW fields remain updateable;
- bibliography matches in-text citations;
- DOI and URL links are present when required;
- citation-to-bibliography navigation was checked when requested;
- Word formatting matches the target document;
- existing fields and cross-references were preserved;
- output document opens normally.

### Required Artifacts

Keep task artifacts in `build/endnote-helper/<timestamp>/`:

- metadata table;
- duplicate report;
- literature analysis table;
- outline;
- style profile;
- Word backup;
- citation check report;
- sentence-to-reference semantic mapping table;
- existing-text revision log;
- final validation summary.

### Failure Reporting

If a required check fails, report:

1. failing check;
2. likely cause;
3. completed work;
4. incomplete work;
5. recommended next step.
<!-- END SOURCE: 09_quality_control.md -->

<!-- BEGIN SOURCE: 10_examples.md -->
## Examples

All examples must follow the interactive gate:

1. detect task type;
2. ask missing required parameters;
3. output task configuration summary;
4. wait for `确认执行`;
5. execute only after confirmation.

### Example 1: Import Paper Links Into EndNote

```text
使用 EndNote-Helper-Skill，读取 links.txt 中的论文链接，检查正式发表信息，生成 RIS 文件，导入 My EndNote Library，并加入 Research Topic 组集。
```

Expected first response if some parameters are missing:

```text
当前还需要确认以下项目：

1. EndNote Library 的完整路径是什么？
2. `Research Topic` 是已有 Group 还是需要新建？
3. 版本优先规则：正式期刊 / 正式会议 / Early Access / arXiv / 保留全部？
4. 疑似重复文献如何处理：只报告 / 跳过 / 保留正式版本 / 逐条确认？
5. 是否下载并关联 PDF？
6. 输出报告保存到哪里？
```

After user answers, output task summary and wait for `确认执行`.

Execution after confirmation:

1. Parse links.
2. Extract and validate metadata.
3. Generate RIS.
4. Import to EndNote.
5. Add to group.
6. Report duplicates and incomplete records.

### Example 2: Generate Related Work

```text
使用 EndNote-Helper-Skill，读取 EndNote Library 中的 Research Topic 组集，按照“基础方法、扩展方法、受限条件与综合比较”的逻辑生成高质量 Related Work，并将 EndNote CWYW 引用插入 thesis.docx 的 1.2.3 节。
```

Expected first response if some parameters are missing:

```text
当前还需要确认以下项目：

1. EndNote Library 的完整路径是什么？
2. 是否仅允许引用 `Research Topic` 组集内文献？
3. 写作语言和文档类型是什么？
4. 目标字数或页数是多少？
5. 是否有写作风格参考文件或沿用 thesis.docx 现有风格？
6. EndNote Output Style 沿用 Word 当前样式还是指定其他样式？
7. 写入方式：替换 1.2.3 原文 / 追加 / 保留并优化？
8. 输出文件覆盖 thesis.docx 还是另存？
```

After user answers, output task summary and wait for `确认执行`.

Execution after confirmation:

1. Read group only.
2. Build literature analysis table.
3. Plan sections by technical route.
4. Draft synthesis.
5. Insert temporary EndNote citations.
6. Run CWYW formatting.
7. Verify EndNote fields and bibliography.

### Example 3: Learn Writing Style

```text
使用 EndNote-Helper-Skill，学习 example_thesis.docx 中第 1.2 节的写作风格、引用密度和排版格式，然后基于 EndNote 的 Research Topic 组集撰写新的研究现状。
```

Expected first response if some parameters are missing:

```text
当前还需要确认以下项目：

1. EndNote Library 的完整路径是什么？
2. `Research Topic` 组集是否为唯一文献范围？
3. 新研究现状的章节标题和写入位置是什么？
4. 目标字数或页数是多少？
5. 是否插入真实 EndNote CWYW 引用？
6. 输出 Word 文件是什么？
```

After user answers, output task summary and wait for `确认执行`.

Execution after confirmation:

1. Extract style profile.
2. Inspect Word styles.
3. Read EndNote group.
4. Draft using style profile.
5. Write into Word using existing styles.

### Example 4: Update Existing Related Work

```text
使用 EndNote-Helper-Skill，检查 thesis.docx 中已有 Related Work，结合 EndNote 指定组集补充缺失文献，修正错误引用，保留现有 CWYW 字段，并更新文后参考文献。
```

Expected first response if some parameters are missing:

```text
当前还需要确认以下项目：

1. 需要检查 thesis.docx 的哪个章节或范围？
2. 使用哪个 EndNote Library 和 Group？
3. 是否允许删除不相关引用？
4. 是润色、补充、重构，还是三者都做？
5. 目标字数或页数是否需要变化？
6. 是否直接写回 thesis.docx？
7. 是否输出修改说明或对照表？
```

After user answers, output task summary and wait for `确认执行`.

Execution after confirmation:

1. Backup Word document.
2. Inspect existing citation fields.
3. Compare cited references with target group.
4. Draft targeted additions.
5. Preserve existing CWYW fields.
6. Rerun EndNote formatting and verify.

### Required Behavior Tests

#### Test 1

User:

```text
使用 Research Topic 组集写研究现状。
```

Skill must ask at least:

- EndNote Library;
- writing topic;
- outline or organization logic;
- language;
- target pages/words;
- citation insertion requirement;
- citation format;
- Word file;
- insertion location;
- writing style.

It must not read the whole library or start writing.

#### Test 2

User:

```text
基于 EndNote 中的 Research Topic 组写博士论文 1.2.1 节，约 10 页，按问题定义、主要方法、适用条件、性能权衡和研究局限组织，写入毕业论文.docx，并插入 CWYW 引用。
```

Skill must not repeat already clear parameters:

- group;
- page count;
- document type;
- outline;
- write location;
- citation mode.

It should ask only missing items:

- EndNote Library;
- style reference;
- EndNote Output Style;
- whether only the group may be cited;
- replace or optimize existing content;
- output path.

#### Test 3

User:

```text
把 links.txt 中的论文导入 EndNote。
```

Skill must ask:

- EndNote Library;
- EndNote Group;
- formal-version preference;
- duplicate handling;
- whether to download PDFs;
- output report format.

It must not import before confirmation.

#### Test 4

User:

```text
学习 example.docx 的写作风格。
```

Skill must ask:

- section or page range;
- style dimensions;
- whether to generate `style_profile.md`;
- whether to apply immediately;
- target task if applying.

It must not generate or apply a style profile before confirmation.
<!-- END SOURCE: 10_examples.md -->

<!-- BEGIN SOURCE: 11_existing_text_semantic_citation.md -->
## Existing Text Semantic Citation

Use this workflow when the user asks to optimize existing prose and insert suitable EndNote references according to sentence meaning.

### Confirmed Modes

Distinguish these modes before execution:

- `RESTORE_ORIGINAL`: identify and restore the sources intended by existing citation numbers.
- `GROUP_SEMANTIC_REPLACE`: treat existing numbers as placeholders and select suitable references from the confirmed EndNote group.
- `ADD_TO_UNCITED_TEXT`: keep supported prose and add citations where needed.

Never infer the mode from a static number alone.

### Claim Extraction

1. Read the confirmed Word range and preserve paragraph order.
2. Split compound sentences into propositions when different clauses require different evidence.
3. Classify each proposition as background fact, method description, comparison, limitation, trend, dataset/result claim, or author contribution.
4. Record existing citation markers without assuming their source identity.

### Semantic Matching

Build a mapping table with:

| Claim ID | Existing sentence or proposition | Allowed revision | Candidate record | Evidence read | Supported meaning | Confidence | Action |
|---|---|---|---|---|---|---|---|

Match by research meaning and evidence:

- use title metadata only for broad topical claims;
- use abstract or full text for method, limitation, experiment, result, or comparison claims;
- prefer direct support over loose topical similarity;
- prefer the smallest sufficient citation set;
- do not use EndNote order, PDF filename, static citation number, or keyword overlap as proof.

### Limited Text And Logic Optimization

When the user allows existing content to be modified according to available references:

- correct grammar, terminology, references, and sentence structure;
- narrow an overbroad claim to the scope supported by the selected records;
- replace an unsupported trend or application statement with a nearby claim that the group evidence supports;
- reorder adjacent sentences when the progression of background, problem, evidence, and conclusion is unclear;
- add or revise transition phrases so the citation fits the argument rather than interrupting it;
- repair pronoun reference, repeated subjects, abrupt topic shifts, and weak cause-effect links;
- preserve the paragraph's research purpose and the user's intended argument;
- avoid adding new technical conclusions, numerical results, novelty claims, or criticism not supported by the records;
- log each material semantic change as `original -> revised -> supporting record numbers`.

If no group record supports the sentence and revision would change its research intent, do not rewrite it. Mark it `[Unsupported by confirmed group]` in the process report and ask the user when necessary.

### Citation Placement

- place citations immediately after the supported clause or sentence;
- group references only when they support the same proposition;
- reuse the same EndNote record when a later sentence depends on the same source;
- do not preserve obsolete static numbering after the CWYW conversion;
- use real record numbers in temporary citations, then run EndNote formatting.

### Acceptance Checks

Verify:

- every inserted record belongs to the confirmed group unless broader scope was approved;
- each citation has documented sentence-level support;
- all text changes stay within the confirmed revision scope;
- paragraph logic remains coherent before and after each citation;
- static placeholders were removed only where replaced by real CWYW fields;
- `ADDIN EN.CITE` and, when requested, `ADDIN EN.REFLIST` exist;
- no temporary `{Author, Year #RecordNumber}` citations remain;
- unsupported claims and unused relevant records are reported.
<!-- END SOURCE: 11_existing_text_semantic_citation.md -->

<!-- BEGIN SOURCE: 12_ral_two_column_semantic_cwyw.md -->
## RA-L / IEEE Two-Column Semantic CWYW Workflow

Use this reference when the user provides an existing Word draft, an EndNote group, and a journal PDF such as an IEEE Robotics and Automation Letters paper as the prose/layout sample.

### Contents

1. Scope and prerequisites
2. Confirmation contract
3. Build artifacts
4. Target and style preflight
5. Group and metadata preflight
6. Claim decomposition and evidence mapping
7. RA-L prose reconstruction
8. Temporary citation construction
9. Safe Word/EndNote execution
10. RA-L layout profile
11. EndNote output-style rules
12. Automation fallback
13. Staged validation gates
14. Failure handling
15. Final reporting

### 1. Scope and prerequisites

Apply this workflow only after the task reaches `READY_TO_EXECUTE`.

Required confirmed inputs:

- target `.docx` and overwrite policy;
- target EndNote `.enl` library;
- exact group path;
- style sample PDF;
- language;
- permitted revision scope;
- whether existing static numbers are placeholders or original-source targets;
- whether exact IEEE/RA-L numeric output is required;
- whether headers, footers, and page numbers may be replaced by the learned journal layout.

Use only records verified as members of the confirmed group. A paper that exists elsewhere in the library is out of scope unless the user expands the scope.

### 2. Confirmation contract

The configuration summary must state:

- `semantic unit`: sentence or proposition;
- `citation policy`: smallest sufficient citation set;
- `text policy`: citation-only, local optimization, or paragraph restructuring;
- `unsupported claim policy`;
- `layout source`: sample PDF and which attributes will be learned;
- `CWYW policy`: real fields, no manual bibliography;
- `backup policy`: timestamped backup plus working copy;
- `validation policy`: field, XML, rendered text, visual PDF, and Word-open checks.

Do not assume that “format like this PDF” authorizes deleting existing headers, footers, or page numbers. Confirm that separately or preserve them.

### 3. Build artifacts

Create `build/endnote-helper/<timestamp>/` and keep these artifacts when applicable:

- `target.before.docx` — immutable backup;
- `target.working.docx` — file used for conversion and formatting;
- `style_profile.md` — prose and layout traits learned from the PDF;
- `sentence_reference_mapping.md` — claim-to-record evidence table;
- `revision_log.md` — material wording and logic changes;
- `metadata_exclusions.md` — records rejected because of malformed or incomplete metadata;
- `preview.pdf` and rendered page images;
- `preview.txt` — laid-out PDF text for reference audit;
- `citation_check.md` — field/link check output;
- automation scripts and logs.

Use `../templates/ral_semantic_cwyw_task.md` as the artifact skeleton.

### 4. Target and style preflight

#### 4.1 Audit the current Word file

Before rewriting, record:

- modified time and size;
- paragraph text and paragraph count;
- existing `ADDIN EN.CITE` count;
- existing `ADDIN EN.REFLIST` count;
- temporary citation count;
- whether visible numbers such as `[12]` are plain text;
- page size, margins, columns, section count, headers, footers, and page numbers;
- whether a References section already exists.

Never rely on an earlier audit if the file modification time changed. The current file may have been replaced during the conversation.

#### 4.2 Learn from the PDF in three views

Use all three:

1. Document metadata: paper size, page count, producer.
2. Laid-out text: column order, headings, citations, paragraph rhythm, reference form.
3. Rendered pages: first page, representative body page, reference page.

Suggested read-only commands:

```text
pdfinfo sample.pdf
pdftotext -layout -enc UTF-8 sample.pdf sample-layout.txt
pdftoppm -png -f <page> -singlefile -r 150 sample.pdf page
```

Separate the resulting style profile into:

- `rhetorical profile`: background → limitation → gap → response, claim density, transitions, method contrasts;
- `visual profile`: paper size, margins, columns, fonts, spacing, headings, citations, references;
- `non-transferable content`: title block, author affiliations, received dates, copyright footer, manuscript-specific figures.

Do not copy sample sentences.

### 5. Group and metadata preflight

#### 5.1 Verify group membership first

List exact group record numbers before selecting citations. Store the list in the mapping artifact.

#### 5.2 Read evidence at the required level

For each candidate claim, inspect at least the title and abstract. Inspect introduction or method text when the claim concerns implementation details, limitations, sensor assumptions, or evaluation scope.

#### 5.3 Preflight rendered metadata

Before inserting a record, check:

- author parsing and order;
- year;
- title;
- journal/conference;
- volume/issue/pages;
- DOI when available;
- document type.

Pay special attention to raw author strings containing commas plus prose conjunctions, because EndNote may render them as malformed initials. If a generated bibliography displays an impossible author string, exclude the record or repair it in EndNote and rerun CWYW.

Do not manually rewrite the bibliography field result to hide a bad record.

#### 5.4 Avoid accidental self-citation

If the draft describes the same paper that also appears as a record in the group, use that record only as a factual cross-check. Do not cite the paper inside its own introduction unless the document is a thesis or later work where self-citation is contextually correct.

### 6. Claim decomposition and evidence mapping

Split the draft into proposition-level units. A sentence may contain multiple independently citable claims.

For each unit record:

- original wording;
- proposed wording;
- paragraph role;
- candidate record numbers;
- evidence read;
- exact supported meaning;
- unsupported portion;
- confidence;
- action: cite, narrow, reorder, bridge, retain as author contribution, or report unsupported.

Use the smallest sufficient citation set. Prefer one direct source over several keyword-similar sources.

Recommended paragraph roles for a compact RA-L introduction:

1. Define the technical problem and importance.
2. Explain the hardware or methodological dependency.
3. Compare generalization-oriented alternatives and remaining limitations.
4. State the gap and the present work's response.

Do not cite author-contribution sentences merely to increase citation count.

### 7. RA-L prose reconstruction

Use compact English and a visible argument chain:

`background → representative mechanism → limitation → alternative → residual gap → proposed response`

Apply these rules:

- open with a precise technical role, not “has attracted extensive attention”;
- define acronyms once;
- keep one main assertion per sentence where practical;
- place citations adjacent to the supported clause;
- use method names only when they advance the comparison;
- distinguish demonstrated capability from intended design;
- prefer cautious verbs: `supports`, `targets`, `reports`, `is intended to`;
- avoid unsupported universals such as `independent of all environments`;
- repair spacing, hyphenation, capitalization, and sentence fragments;
- preserve the draft's core contribution and terminology.

When an existing paragraph is copied from a published paper, reconstruct the logic in original wording rather than performing superficial synonym replacement.

### 8. Temporary citation construction

Use real EndNote record numbers. The following is a schema, not an import-ready citation:

```text
{FirstAuthorSurname, Year #RecordNumber}
{FirstAuthorSurname, Year #RecordNumber; SecondAuthorSurname, Year #RecordNumber}
```

Rules:

- verify every record number against the group membership list;
- use the primary author's family name and stored year;
- keep repeated sources as repeated temporary citations where the claims recur;
- do not manually assign final numeric labels;
- treat final numbers as EndNote output, not author input.

### 9. Safe Word/EndNote execution

Use this sequence:

1. Create timestamped backup.
2. Create a separate working copy.
3. Insert revised prose and temporary citations into the working copy.
4. Save the working copy.
5. Run `Project.EndNoteMacros.ENFormatBibliography` or the available equivalent.
6. Wait for EndNote formatting to finish.
7. Reject the result if any `{... #123}` citation remains.
8. Count display citation fields and the bibliography field.
9. Audit the generated bibliography text for metadata corruption.
10. Apply final journal layout without replacing any EndNote field result.
11. Export a PDF preview.
12. Validate the working copy.
13. Copy it over the target only after every required gate passes.

When replacing an existing range that contains fields, replace only the confirmed target range. Never run `ENRemoveFieldCodes` as a shortcut.

### 10. RA-L layout profile

Use measurements from the supplied sample whenever possible. The following values are a reusable starting profile learned from an IEEE RA-L sample, not a universal mandate:

| Property | Starting value |
|---|---:|
| Paper | US Letter, 612 × 792 pt |
| Orientation | Portrait |
| Top margin | 54 pt |
| Bottom margin | 45 pt |
| Left/right margins | 48 pt |
| Columns | Two equal columns |
| Column gap | 18 pt |
| Body font | Times New Roman, 10 pt |
| Body alignment | Justified |
| Body spacing | Single, 0 pt before/after |
| First-line indent | 12 pt |
| Section heading | Centered, 10 pt, uppercase/small caps |
| Reference font | Times New Roman, 8 pt |
| Reference indent | 14 pt hanging |
| Citation position | Inline, not superscript |

Preserve existing headers and footers unless the confirmed task authorizes replacing them. A sample PDF may contain publisher material that should not be recreated.

For a short excerpt, references may continue on a second page with unused space. Do not shrink text merely to force a one-page result unless the user requires an exact page count.

### 11. EndNote output-style rules

- Select a real IEEE/RA-L-compatible EndNote output style before formatting when exact punctuation is required.
- Accept final numbering only from EndNote.
- Do not manually change `[1, 2]` into `[1], [2]` inside field results; correct the EndNote output style instead.
- Do not hand-type reference entries.
- A DOI may exist inside EndNote field data even if the selected output style does not display it. Report display and embedded metadata separately.
- Re-run the bibliography after metadata repairs or record substitutions.

### 12. Automation fallback

#### 12.1 Preferred path

Use background Word automation only when it does not require the user to stop normal input. Keep Word hidden and alerts disabled.

#### 12.2 Early-bound COM failure

PowerShell Word COM may fail with:

```text
TYPE_E_CANTLOADLIBRARY
0x80029C4A
Unable to cast ... Word.ApplicationClass ... _Application
```

After one clean retry, stop repeating the same early-bound method. Verify and terminate only orphaned hidden Word processes created by the task. Never terminate a user-visible Word process or one with unsaved work.

Use the late-bound VBScript fallback:

```text
cscript.exe //nologo ../scripts/citation/format_ral_cwyw.vbs working.docx preview.pdf 12
```

Late binding uses `CreateObject("Word.Application")` and can work even when the Office type library is unavailable to PowerShell.

Run Word `/regserver` only with explicit user approval and only when late binding is also unavailable or broader Office repair is required. It is not the first fallback.

#### 12.3 Background-operation rule

Prefer one batched write/format/validate pass. Do literature collection and mapping before controlling Word so the computer is not occupied while no text is being entered.

### 13. Staged validation gates

All applicable gates must pass before target replacement.

#### Gate A — semantic and metadata

- every citation maps to an analyzed group record;
- no unsupported claim is forced;
- no malformed rendered author/title/source;
- no accidental self-citation.

#### Gate B — EndNote field integrity

- `ADDIN EN.CITE` count matches citation locations;
- one `ADDIN EN.REFLIST` exists when required;
- temporary citation count is zero;
- bibliography entries come from the field result.

#### Gate C — OOXML layout

- two-column section exists;
- paper size matches the sample;
- margins and column gap are present;
- citation results are not superscript.

#### Gate D — rendered-text audit

Convert the preview to laid-out text and check:

- introduction order and paragraph continuity;
- final citation sequence;
- reference count;
- author names and source metadata;
- no visible temporary citations or duplicated References heading.

#### Gate E — visual audit

Render every page or at least all pages changed. Check:

- column balance and overflow;
- heading placement;
- orphaned headings;
- reference hanging indents;
- unexpected headers, footers, or page numbers;
- excessive whitespace caused by accidental breaks.

#### Gate F — native Word open

Open the final working copy read-only in Word and report:

- page count;
- paragraph count;
- total Word field count;
- display citation field count;
- bibliography field count.

#### Gate G — final copy

After copying the validated working file to the target, compare file hashes. Re-run the field check on the target when risk is high.

### 14. Failure handling

If a gate fails:

- keep the original target untouched;
- retain the working copy and logs;
- fix the earliest failing layer rather than patching visible output;
- rerun all downstream gates.

Examples:

- malformed author in bibliography → repair/exclude the EndNote record, rebuild citations, rerun all gates;
- temporary citation remains → fix record identity or macro execution, do not convert it to static text;
- wrong citation punctuation → change EndNote output style, do not edit field results;
- layout correct in XML but visually poor → adjust layout, export, and rerun visual plus Word-open checks;
- PowerShell COM type-library error → switch to late-bound script.

### 15. Final reporting

Report concisely:

- target file and backup;
- library and exact group;
- number of unique cited records and citation locations;
- real `EN.CITE` and `EN.REFLIST` counts;
- temporary citation count;
- page/column/paper checks;
- records excluded for metadata reasons;
- preview and semantic-mapping artifacts;
- remaining output-style or hyperlink limitations.
<!-- END SOURCE: 12_ral_two_column_semantic_cwyw.md -->
