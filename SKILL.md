---
name: paper-agent
description: 规划、撰写和修订中英文科研论文与学位论文。适用于方法与实验写作、论文逐段润色、Word 版式与公式、可编辑科研框图、EndNote 引用及送审前检查。也可根据论文和模板制作学位论文答辩 PPT，或提取参照稿的 Word 基础格式。
---

# Paper Agent

围绕论文所问的问题，把方法、模型、证据及其适用边界连起来。先确定作者要求的交付物、可改范围与依据，再选一个主模式。用户明确要求、已确认的模板及冻结项优先。研究事实取自当前稿件、源数据及已核实的文献，不用通用写法替代作者的方法或实验结果。

## 正文的默认写作路径

中英文正文都从要解释的问题、现象或结果落笔，写清具体的研究对象及其动作，判断限定在观测、条件或推导能够支持的范围内。承接上段尚待解释的问题或已建立的结果，再展开下一步论述。引用图表前交代本段希望检验什么，引用后指出图中可见的变化或表中关键差异，并说明据此可以得出什么结论。

- **中文论文**。起草、扩写或润色前读取[中文学位论文写作](references/chinese-thesis-language-style.md)，结合作者用语和邻近段落选择措辞、标点及段落节奏。
- **英文论文**。采用目标期刊或学位项目规定的语体，依其要求在首次使用时定义缩写，统一后文称谓。正文中的图表引述使用期刊规定的写法，如 `Fig. 2`、`Figure 2`、`Table 1`。
- **既有文稿的润色**。保留术语、数字、公式和引文。Word 只写获准的段落，保留题注、交叉引用及引文域，不因全文逐段润色而刷新目录、重排参考文献或重套版式。
- **执行作者红字或批注**。仅当批注、修订意见或清单含有作者要求执行的具体指令时，读取[逐项落实作者修改意见](references/red-instruction-revision-workflow.md)，逐项记录依据、改动或待补证项。

## 主模式与资料

只读取当前阶段需要的专项文件。用 `word_layout`、`equation`、`figure_ppt`、`experiment_evidence`、`citation_endnote`、`rag` 标记实际需要的能力。

| 主模式 | 何时采用、从何处开始 |
|---|---|
| `full_paper` | 构建方法、实验、结论等整篇论文。先读[方法、RAG 与 Word](references/method-and-word-workflow.md)，按当前阶段加入实验、绘图或文献。明确要求终稿全方位深度优化或送审前全稿整改时采用 `submission`，从[终稿全文优化](references/full-thesis-final-optimization.md)开始。 |
| `method_only` | 扩写方法、推导、变量或算法。以上述方法参考和当前论文大纲为准，外部资料补足有据可查的细节。说明模块目标、模型、算法和适用边界。 |
| `experiment_only` | 按[实验工作流](references/experiment-workflow.md)核对原始图表、设置、指标、精度、顺序、加粗位置及失败标记。沿用已确定的章节结构，并说明数据集在本次验证中的作用。作者要求机理解释或学习个人写作风格时加读[实验分析与作者风格](references/evidence-grounded-experiment-analysis.md)，区分作者的表达习惯与旧文技术事实。 |
| `conclusion_only` | 从已核实的正文证据回答研究问题，归纳贡献、实验结论、局限与未来工作。没有支撑的结论收窄到证据所及。 |
| `figure_only` | 新绘或定点修改科研框图、技术路线及章节图，读取[科研绘图](references/figure-workflow.md)。从论文文字生成或重构图时另读[正文生成框图](references/text-to-figure-workflow.md)。 |
| `literature_citation` | 核验已引文献真实性、著录或支撑位置时，读[文献核验与 CWYW 保真](references/reference-verification-and-cwyw-preservation.md)，分别说明检查深度。主动导入、从 EndNote Group 写作或插入可更新引文时读[文献与 EndNote](references/literature-citation-workflow.md)。 |
| `revision_only` | 修改指定文稿、章节、公式、图表或 PPT 的既有对象。依照上面的文字路线或下面的对象路线选择专项，不自动开启整稿工程。 |
| `defense_deck` | 按论文及指定模板制作或优化答辩 PPT，读[学位论文答辩 PPT](references/defense-ppt-workflow.md)。整套继承模板与已确认页面动作；单页反馈用 `revision_only + fast_local`，实际新绘的方法图再进入科研图流程。 |

## 按对象加载与写入

**Word。** 首次确认的学校或期刊模板、项目 `style/` 规则与用户覆盖值持续用于同一文档；每次写入只应用于授权对象。涉及 Word 版式、公式或跨页对象时读取[方法与 Word](references/method-and-word-workflow.md)。已定页面方向、版心或模板且增补内容会引起重分页时读取[纵向页面与版心](references/layout-first-portrait-page-gate.md)；仅对允许新增或调整的对象采用页面适配方案。新增、恢复或调整数据表、编号公式容器、封面布局、图像拼版及题注容器前，读[表格对象语义分类](references/table-object-classification-gate.md)。涉及 Word 域、兼容对象、小字、公式转换或分页异常时，按对象查[Word 对象与域的保真检查](references/word-object-fidelity.md)。明确采用东南大学博士论文规范时读[东南大学论文排版](references/seu-thesis-layout.md)，按章标题、下级标题与正文分别处理分页。

**参照格式与版面调整。** 只提取基础格式时按[参照论文的基础格式提取](references/thesis-basic-format-profile.md)只读归纳，各类取常用值并写为 Word 可设置的单位。参照例只在用户指定采用时生效。用户以最新摘要、目录题名为准时，先冻结术语、核对实际标题、层级和书签，按授权同步正文；分页稳定后只同步所需的目录页码。约定留白上限或允许调整图表锚点时，读[分页与锚点重排](references/word-pagination-and-anchor-reflow.md)，按约定口径测量实际页面。明确只要 Word 且禁止 PDF 时，以允许的 Word 原生页面或内部 XPS 核验。

**科研图。** 按[科研绘图](references/figure-workflow.md)选择视觉样式、原生对象、公式和审计范围；其中的对象、连接器与快速微调规范为实施依据。用[内置五页模板](assets/paper-figure-style-template.pptx)时，第 1–2 页适用叙述背景，第 3–5 页适用方法逻辑。指定参考图或既有模板优先。新主题、主拓扑或图体比例变动先落实目标页、比例、字体字号、素材用途、公式类型和页面动作，再按专项确认静态骨架；局部调整继承目标页参数。用户指定原样复用的素材按原比例作为独立对象。只操作 `Presentation.FullName` 与授权路径一致的演示文稿，不操作其他演示文稿或退出用户的 Office 实例。

## 计划、执行与复核

`Planner → Executor → Reviewer` 是同一技能内依次承担的三个职责，默认由一个智能体完成。需要并行时分派可独立核验的任务。状态为 `USER_INPUT → PLANNED → EXECUTING → READY_FOR_REVIEW → APPROVED → DELIVERED`。

1. **Planner** 只读确定目标文件、证据范围、主模式、输出格式和位置、可改与冻结项，以及怎样从最终文件验证。写作任务确认体例、篇幅、标题权限；公式任务确认 OMML、MathType 或 LaTeX 与编号要求；主动引文、绘图任务按各专项确认相关参数。沿用已明确的选择，无须再问。
2. **Executor** 先定位成因，保存原稿与基线，使用 `build/paper-agent/<timestamp>/` 的工作副本。按源证据集中写入获准对象，保留允许差异和必要的核验记录。授权或证据发生实质变化时退回 Planner；其余问题优先在现有范围修复。
3. **Reviewer** 从最终保存状态核对可见效果与相应结构。执行缺陷退回 Executor；若要改变任务范围、授权或依据，退回 Planner。修复后重验。产物、页数、公式、图表和引用按本次工作实际涉及的范围报告。缓存、开发脚本与中间预览留在构建目录，完整制作和单项任务分别交付用户所需文件。

| 档位 | 验收范围 |
|---|---|
| `fast_local` | 单对象或单页，通常不超过 10 个对象，章节与主拓扑不变。保存即时快照、复核授权页和改动对象。 |
| `standard` | 连续页面、一个小节、整页新图或主拓扑调整。复核受影响部分并合并处理反馈；分页变化沿传播到的页复核。 |
| `submission` | 章节重构、整稿送审或明确要求全范围检查。核对全范围实际页面、章节边界、数据证据与受保护对象；允许的模板空白页保留。 |

复用现有 [方法/RAG](scripts/method/)、[实验审计](scripts/experiment/)、[文献与引文](scripts/citation/)、[科研绘图与原生对象审计](scripts/figure/) 和[过程模板](templates/)。优先用 Python 处理数据、UTF-8 文字与 OOXML，Office 原生接口、MathType 或窗口绑定按需使用 PowerShell/VBScript。结构计数、XML 可解析或缩略图可用于定位问题；页面质量以最终保存后实际渲染的相应页面为准，未完成的验证明确注明。
