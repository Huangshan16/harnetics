# Feature Specification: Aerospace Document Alignment Product

**Feature Branch**: `001-aerospace-doc-alignment`  
**Created**: 2026-04-06  
**Status**: Draft  
**Input**: 基于 MVP PRD 全盘实现航天文档对齐产品——文档导入解析、知识图谱、LLM 草稿生成（带引注与冲突检测）、Evaluator 质量门、变更影响分析、WebUI 全页面

## User Scenarios & Testing

### User Story 1 - 文档库导入与浏览 (Priority: P1)

航天工程师将部门级的 Markdown/YAML 技术文档拖入系统，系统自动解析章节结构、提取 ICD 参数、建立文档间引用关系，并在文档库中按部门/类型/层级浏览、搜索和查看文档详情。

**Why this priority**: 文档库是一切下游功能（草稿生成、影响分析、图谱可视化）的数据基础，没有文档入库其他功能无法运转。

**Independent Test**: 上传 10 份 fixture 文档（DOC-SYS-001 至 DOC-FMA-001），验证全部入库成功，章节正确拆分，ICD 参数完整提取，可按筛选条件检索。

**Acceptance Scenarios**:

1. **Given** 用户在文档库页面，**When** 拖入一份 Markdown 文档，**Then** 系统在 5 秒内完成解析入库，文档出现在列表中，状态为"已导入"
2. **Given** 10 份文档已入库，**When** 用户按"动力系统部"筛选，**Then** 只显示该部门的文档（DOC-DES-001, DOC-TST-001/002/003）
3. **Given** DOC-ICD-001（YAML 格式）已入库，**When** 用户查看其详情，**Then** 可看到 12 个 ICD 参数列表及其接口类型、子系统、值域
4. **Given** 用户在文档详情页，**When** 查看某文档的上下游关系，**Then** 显示该文档的上游依据文档和下游派生文档

---

### User Story 2 - 对齐草稿生成 (Priority: P1)

动力系统部工程师在草稿工作台中选择部门、文档类型和系统层级，输入主题描述，系统自动检索相关文档并调用本地 LLM 生成一份带引注标记的技术文档草稿，包含冲突检测和自动质量评估。

**Why this priority**: 草稿生成是产品的核心价值——将「手动翻档拼文档」变为「AI 自动对齐生成」，是用户购买产品的根本理由。

**Independent Test**: 以 MVP 场景（TQ-12 发动机热试车测试大纲）为输入，验证生成的草稿覆盖模板全部必填章节，100% 引注指向真实文档，冲突标记准确，Evaluator 阻断项全部通过。

**Acceptance Scenarios**:

1. **Given** 用户已选择部门=动力系统部、类型=测试大纲、层级=分系统层，**When** 输入主题"TQ-12液氧甲烷发动机地面全工况热试车测试大纲"并点击生成，**Then** 系统在 3 分钟内返回完整草稿
2. **Given** 草稿已生成，**When** 用户查看草稿内容，**Then** 每个技术指标旁都有 [📎 DOC-XXX-XXX §X.X] 引注标记
3. **Given** fixture 数据中 DOC-TST-003 引用了 ICD v2.1（当前 v2.3），**When** 草稿生成完成，**Then** 冲突区域出现 ⚠️ 标记，说明版本不一致
4. **Given** 草稿生成完成，**When** 用户查看 Evaluator 结果面板，**Then** 显示各检查项的通过/告警/阻断状态
5. **Given** 用户对草稿满意，**When** 点击"导出 .md"，**Then** 下载一份格式正确的 Markdown 文件

---

### User Story 3 - 变更影响分析 (Priority: P2)

当某份上游文档发生变更时，技术负责人需要快速识别哪些下游文档受到影响、影响程度（Critical/Major/Minor），并生成影响报告。

**Why this priority**: 变更影响分析解决"改了一份文档不知道波及多少下游"的工程痛点，但依赖文档库和图谱已就绪，因此排在 P2。

**Independent Test**: 模拟修改 DOC-ICD-001 的推力参数，验证系统识别出 4 份受影响文档并正确评估影响程度。

**Acceptance Scenarios**:

1. **Given** 用户在变更影响分析页面，**When** 选择 DOC-ICD-001 并上传新版本，**Then** 系统在 30 秒内返回影响报告
2. **Given** 影响报告已生成，**When** 用户查看报告，**Then** 列出受影响文档清单，每份标注影响程度（Critical/Major/Minor）和受影响章节
3. **Given** ICD 推力参数从 650kN 变为 680kN，**When** 运行影响分析，**Then** DOC-TST-001/002/003 和 DOC-DES-001 被识别为受影响文档

---

### User Story 4 - 文档图谱可视化 (Priority: P2)

用户通过交互式图谱查看所有文档间的引用关系网络，以 ICD 为枢纽理解系统级文档依赖，支持按部门和层级过滤、点击节点查看详情。

**Why this priority**: 图谱可视化直观呈现文档关系网络，帮助用户建立"系统级"认知，是产品差异化亮点，但非核心生产力功能。

**Independent Test**: 加载 10 份 fixture 文档后，验证图谱显示所有文档节点和至少 15 条关系边，ICD 文档居中显示，部门颜色区分正确。

**Acceptance Scenarios**:

1. **Given** 10 份文档已入库，**When** 用户访问图谱页面，**Then** 显示所有文档节点和关系边，ICD 文档在视觉中心
2. **Given** 图谱已渲染，**When** 用户按"动力系统部"过滤，**Then** 只显示该部门文档及其与其他部门的连接边
3. **Given** 图谱已渲染，**When** 用户点击某个文档节点，**Then** 弹出详情卡片展示文档元数据和关联信息

---

### User Story 5 - 系统仪表盘 (Priority: P3)

用户打开首页即能看到系统健康概览：文档总数、关系总数、过期引用数、最近操作时间线、Evaluator 通过率。

**Why this priority**: 仪表盘是锦上添花的全局视图，所有核心数据来自其他功能模块的聚合，开发成本低但独立价值有限。

**Independent Test**: 导入全部 fixture 后访问首页，验证统计数据与实际一致，时间线显示最近操作记录。

**Acceptance Scenarios**:

1. **Given** 10 份文档已入库，至少 15 条关系已识别，**When** 用户访问首页，**Then** 显示文档总数=10、关系总数≥15、过期引用数=1（DOC-TST-003）
2. **Given** 用户刚生成了一份草稿，**When** 返回首页，**Then** 时间线显示该操作记录

---

### User Story 6 - Evaluator 质量门 (Priority: P1)

生成的草稿必须经过 8 项自动质量检查（EA.1-5, EB.1, ED.1, ED.3），阻断级问题阻止导出，告警级问题标注但不阻止，确保每份对齐草稿的工程可靠性。

**Why this priority**: 质量门是产品"可信"承诺的技术保障，没有 Evaluator 的草稿等于没有质量背书，直接影响用户信任。

**Independent Test**: 对 fixture 场景生成的草稿运行全部 8 项检查，验证预埋的 4 处不一致被正确检测。

**Acceptance Scenarios**:

1. **Given** 草稿已生成，**When** 运行 EA.1（引注完整性），**Then** 检测每个技术指标段落是否有 📎 来源标记
2. **Given** 草稿引注了 DOC-XXX-001，**When** 运行 EA.2（引用真实性），**Then** 验证该编号在文档库中存在
3. **Given** 草稿引注了 ICD v2.1，**When** 运行 EA.3（版本最新），**Then** 告警"当前版本为 v2.3"
4. **Given** 文档图谱已构建，**When** 运行 EA.4（循环引用），**Then** DFS 检测无环并通过
5. **Given** 草稿有 20 个技术段落，16 个有引注，**When** 运行 EA.5（覆盖率），**Then** 显示覆盖率 80%，状态为 pass
6. **Given** 草稿中出现推力参数 650kN，ICD 表值也为 650kN，**When** 运行 EB.1（ICD 一致性），**Then** 通过
7. **Given** 草稿中每个数字都能在源文档中找到，**When** 运行 ED.1（无捏造），**Then** 通过
8. **Given** 生成时检测到冲突，**When** 运行 ED.3（冲突标记），**Then** 验证草稿正文中有对应 ⚠️ 标记

### Edge Cases

- 上传非 Markdown/YAML 格式文件时，提示"MVP 仅支持 Markdown 和 YAML 格式"并拒绝
- LLM 服务（Ollama）未启动时，草稿生成提示连接失败并给出启动指引
- 文档库为空时尝试生成草稿，提示"请先导入至少一份参考文档"
- 上传已存在的文档编号时，提示版本冲突并让用户选择覆盖或取消
- ICD YAML 格式不合法时，显示解析错误详情和行号
- LLM 生成内容未遵循引注格式时，Evaluator 阻断并提示重新生成
- 文档图谱出现循环引用时，EA.4 检测阻断并高亮问题边
- 超过 10 份文档时系统仍正常运行（性能不退化到用户可感知）

## Requirements

### Functional Requirements

- **FR-001**: 系统必须支持 Markdown (.md) 文件的上传和自动解析，拆分为标题层级对应的章节
- **FR-002**: 系统必须支持 YAML (.yaml/.yml) 文件的上传和自动解析，支持通用 YAML 和 ICD 专用 YAML 两种模式
- **FR-003**: ICD YAML 解析必须提取所有接口参数（参数名、接口类型、子系统、值域、单位、负责部门）
- **FR-004**: 文档入库时系统必须基于规则匹配（正则提取文档编号引用）自动建立文档间关系边
- **FR-005**: 系统必须支持按部门、文档类型、系统层级三个维度筛选文档列表
- **FR-006**: 系统必须支持关键词搜索文档标题和内容
- **FR-007**: 文档详情页必须展示元数据（编号、标题、类型、部门、版本、状态）和上下游关系文档列表
- **FR-008**: 系统必须提供文档图谱查询 API，支持完整图谱、上游追溯、下游追溯、过期引用检测
- **FR-009**: 系统必须集成本地 LLM（通过 Ollama 部署 Gemma 4 26B），用于草稿生成
- **FR-010**: 草稿生成时系统必须通过向量检索（chromadb）和规则匹配找到相关文档章节作为上下文
- **FR-011**: 生成的草稿必须包含 [📎 DOC-XXX-XXX §X.X] 格式的引注标记，每个技术指标必须有来源
- **FR-012**: 系统必须自动检测引用文档间的参数冲突并在草稿中用 ⚠️ 标记
- **FR-013**: 系统必须实现 8 项 Evaluator（EA.1-5, EB.1, ED.1, ED.3），分为阻断级和告警级
- **FR-014**: Evaluator 阻断级检查未通过时，系统必须阻止草稿导出
- **FR-015**: 系统必须支持草稿导出为 .md 文件下载
- **FR-016**: 系统必须支持变更影响分析——输入文档新版本，输出受影响文档清单及影响程度
- **FR-017**: 影响程度必须分为 Critical/Major/Minor 三个等级，基于关系类型和引用深度计算
- **FR-018**: 文档图谱页面必须以交互式网络可视化呈现文档关系，支持按部门/层级过滤和节点点击详情
- **FR-019**: 仪表盘必须展示文档总数、关系总数、过期引用数、最近操作时间线、Evaluator 通过率
- **FR-020**: 所有功能必须通过 Web 界面访问，用户无需使用命令行

### Key Entities

- **Document**: 航天技术文档实体，含编号（doc_id）、标题、类型（11种）、部门、系统层级（5级）、工程阶段、版本、状态、内容哈希
- **Section**: 文档章节，从属于 Document，含标题、内容、层级、排序索引
- **Edge**: 文档间关系边，含源/目标文档及章节、关系类型（6种：traces_to/references/derived_from/constrained_by/supersedes/impacts）、置信度
- **ICDParameter**: ICD 接口参数，含参数名、接口类型（6种）、子系统 A/B、值域、单位、负责部门
- **Draft**: AI 生成的对齐草稿，含请求配置、Markdown 内容、引注列表、冲突列表、Evaluator 结果、状态
- **ImpactReport**: 变更影响报告，含触发文档、变更章节、受影响文档清单及影响程度
- **EvalResult**: 单项质量检查结果，含评估器 ID、状态（pass/fail/warn/skip）、级别（block/warn）、问题位置

## Success Criteria

- **SC-001**: 10 份 fixture 文档全部在 5 秒内成功入库，章节正确拆分，ICD 参数完整提取
- **SC-002**: 文档间至少 15 条关系自动识别且正确
- **SC-003**: 草稿生成在 3 分钟内完成（10 份源文档场景），覆盖模板所有必填章节
- **SC-004**: 草稿中 100% 引注指向真实存在的文档和章节
- **SC-005**: 预埋的 4 处数据不一致（T1-T4）全部被 Evaluator 检测并报告
- **SC-006**: 修改 ICD 参数后变更影响分析在 30 秒内识别出 4 份下游受影响文档
- **SC-007**: 用户从打开浏览器到生成并导出草稿，全程不超过 5 步点击且无需命令行操作
- **SC-008**: 文档图谱正确渲染所有节点和关系边，部门颜色区分，节点可点击查看详情

## Assumptions

- MVP 阶段仅支持 Markdown (.md) 和 YAML (.yaml/.yml) 两种文档格式，Word/Excel/PDF 留待 Phase 1
- 仅服务天行一号运载火箭单一项目，不支持多型号
- 用户通过 http://localhost:8080 本地访问，无需用户认证和权限管理
- LLM 模型为 Gemma 4 26B（Ollama 本地部署），需 RTX 4090 级 GPU 或 Apple M 系列
- 文档关系抽取仅使用规则匹配（正则提取文档编号），不使用 LLM 辅助抽取
- 向量检索使用 chromadb + sentence-transformers 生成文档章节嵌入
- 中文界面，不支持国际化
- 前端原型已在 `docs/design-docs/prototype2/` 中以 React+shadcn/ui 实现，后端实现采用 FastAPI+Jinja2+HTMX 技术栈
