# Feature Specification: React Frontend Replacement

**Feature Branch**: `002-react-frontend-replacement`
**Created**: 2026-04-11
**Status**: Draft
**Input**: User description: "Replace current Jinja2/HTMX server-rendered frontend with React/Vite/TypeScript/shadcn-ui SPA frontend based on docs/design-docs/prototype2"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — 文档库浏览与筛选 (Priority: P1)

工程师在浏览器中打开首页，看到仪表盘概览。导航到"文档库"页面后，看到文档列表表格，可按部门、类型、层级筛选，也可通过搜索框模糊查找。点击某行进入文档详情页，查看元数据、上下游关系和章节内容。

**Why this priority**: 文档浏览是所有后续操作（草稿、影响分析、图谱）的入口，是核心主路径。

**Independent Test**: 启动前端 dev server + 后端 API，打开浏览器 → 看到仪表盘 → 点击"文档库" → 表格显示 10 条文档 → 筛选"系统工程部" → 结果缩小 → 点击 DOC-ICD-001 → 详情页正确展示元数据、章节和上下游关系。

**Acceptance Scenarios**:

1. **Given** 后端已 ingest 10 份样本文档, **When** 用户访问 /documents, **Then** 表格展示 10 行文档并显示编号、标题、部门、类型、层级、版本、状态、更新时间列
2. **Given** 文档列表页, **When** 用户选择部门筛选"系统工程部", **Then** 仅显示该部门的文档
3. **Given** 文档列表页, **When** 用户在搜索框输入"ICD", **Then** 标题或编号包含 ICD 的文档被高亮展示
4. **Given** 文档列表页, **When** 用户点击文档行, **Then** 跳转到文档详情页，展示元数据面板、上下游文档关系卡片和章节列表

---

### User Story 2 — 草稿生成工作台 (Priority: P1)

工程师在"草稿台"页面填写主题描述、选择负责部门/文档类型/系统层级，点击"检索候选来源"后看到系统推荐的候选来源文档列表。勾选需要引用的文档后，点击"生成对齐草稿"，等待片刻后跳转到草稿展示页。草稿展示页分左右两栏：左栏为 Markdown 预览（只读），右栏为评估结果（通过/告警/阻断）和引用来源列表。

**Why this priority**: 草稿生成是产品的核心价值交付，与文档浏览并列为第一优先级。

**Independent Test**: 打开 /draft → 填入主题 → 完成步骤一 → 步骤二显示候选文档 → 勾选 3 份 → 点击"生成" → 自动跳转 /draft/:id → 左栏展示 Markdown 内容，右栏展示评估结果和引用来源。

**Acceptance Scenarios**:

1. **Given** 草稿工作台, **When** 用户填写主题并点击"检索候选来源", **Then** 展示候选文档列表，每项显示编号、版本、类型
2. **Given** 候选文档已展示, **When** 用户勾选 3 份来源并点击"生成", **Then** 页面显示加载动画随后跳转到草稿展示页
3. **Given** 草稿展示页, **When** 页面加载完成, **Then** 左栏显示草稿 Markdown 内容，右栏显示评估结果汇总和逐条详情以及引用来源列表

---

### User Story 3 — 变更影响分析 (Priority: P2)

工程师在"变更影响"页面选择一份触发文档并指定新版本号，系统返回影响分析报告列表。点击某份报告后进入详情页，显示汇总卡片（受影响文档数、Critical/Major/Minor 分布）、受影响文档表格和影响详情卡片。

**Why this priority**: 变更影响分析是辅助决策的高价值功能，紧随核心浏览和草稿之后。

**Independent Test**: 打开 /impact → 看到上传表单和历史报告 → 点击报告 → 进入 /impact/:id → 汇总卡片 + 表格 + 详情卡片均正确渲染。

**Acceptance Scenarios**:

1. **Given** 影响分析首页, **When** 页面加载, **Then** 显示"发起新分析"表单和历史报告列表
2. **Given** 历史报告列表, **When** 用户点击某条报告, **Then** 进入报告详情页展示 4 张汇总卡片、受影响文档表格和影响详情卡片

---

### User Story 4 — 文档图谱可视化 (Priority: P2)

工程师在"图谱"页面看到以 SVG 绘制的文档关系图（节点=文档，边=关系），支持按部门筛选和鼠标 hover 高亮。点击节点跳转到文档详情页。侧边栏展示筛选器、关系图例和 hover 时的文档信息卡片。

**Why this priority**: 图谱提供全局视角，与影响分析并列为 P2。

**Independent Test**: 打开 /graph → SVG 图谱渲染 8 个节点和 10 条边 → hover DOC-ICD-001 → 节点高亮且侧边栏显示文档信息 → 筛选"动力系统部" → 仅该部门节点可见 → 点击节点 → 跳转详情页。

**Acceptance Scenarios**:

1. **Given** 图谱页面, **When** 页面加载, **Then** SVG 画布显示所有文档节点和关系边，带箭头和颜色区分
2. **Given** 图谱页面, **When** 用户 hover 某节点, **Then** 该节点放大高亮，其余节点半透明，侧边栏展示该文档信息
3. **Given** 图谱页面, **When** 用户点击"动力系统部"筛选器, **Then** 仅该部门的文档节点和相关边可见

---

### User Story 5 — 仪表盘概览 (Priority: P3)

工程师首次访问系统时落在仪表盘页面，看到统计卡片（文档总数、跨文档关系数、过期引用告警数）、文档健康度进度条（引用最新版本率/ICD 参数一致性/引注覆盖率）、快捷操作入口和最近操作时间线。

**Why this priority**: 仪表盘是落地页，提供全局概览，但不影响核心工作流。

**Independent Test**: 打开 / → 重定向到仪表盘 → 3 张统计卡片有数字 → 健康度进度条渲染 → 快捷操作链接可点击。

**Acceptance Scenarios**:

1. **Given** 用户访问根路径, **When** 页面加载, **Then** 展示 3 张统计卡片、健康度面板、快捷操作面板和最近操作时间线

---

### Edge Cases

- 文档列表为空时，表格显示"未找到匹配文档"空状态提示
- 文档详情页收到不存在的 id 时，展示 404 提示并提供返回按钮
- 网络请求失败时前端展示友好错误提示而非白屏
- 图谱节点位置数据不存在的文档不渲染

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 前端 MUST 为 React 18 + TypeScript + Vite 构建的单页应用
- **FR-002**: 前端 MUST 使用 shadcn/ui 组件库 + amethyst-haze 主题 + Tailwind CSS v4
- **FR-003**: 前端 MUST 使用 react-router-dom 实现客户端路由，路由表包含：/, /documents, /documents/:id, /draft, /draft/:id, /impact, /impact/:id, /graph
- **FR-004**: 前端 MUST 通过 fetch 调用后端 `/api/*` JSON 接口获取数据，不再依赖 Jinja2 服务端渲染
- **FR-005**: 后端 MUST 保留现有 `/api/documents`, `/api/documents/{id}`, `/api/graph/edges`, `/api/draft/generate`, `/api/draft/{id}` 等 JSON API 端点
- **FR-006**: 后端 MUST 在生产模式下通过 FastAPI StaticFiles 中间件托管前端构建产物（dist/）
- **FR-007**: 开发模式下前端 MUST 通过 Vite dev server 独立运行并代理 API 到后端
- **FR-008**: 前端 MUST 包含 Header（导航栏）和 Footer（底部信息栏）全局布局组件
- **FR-009**: 文档列表页 MUST 支持按部门、类型、层级筛选和关键词搜索
- **FR-010**: 文档详情页 MUST 展示元数据面板、上下游关系卡片和章节列表
- **FR-011**: 草稿工作台 MUST 提供两步式操作流：步骤一填写参数 → 步骤二确认来源 → 生成
- **FR-012**: 草稿展示页 MUST 分左右两栏：左栏 Markdown 内容预览，右栏评估结果和引用来源
- **FR-013**: 影响分析首页 MUST 展示"发起新分析"表单和历史报告列表
- **FR-014**: 影响分析详情页 MUST 展示汇总卡片、受影响文档表格和影响详情卡片
- **FR-015**: 图谱页 MUST 用 SVG 绘制文档关系图，支持节点 hover 高亮、部门筛选和节点点击跳转
- **FR-016**: 仪表盘 MUST 展示统计卡片、健康度进度条、快捷操作入口和最近操作时间线
- **FR-017**: 旧的 Jinja2 模板和 HTMX 前端路由 MUST 被移除，所有 UI 由 React SPA 承担
- **FR-018**: 前端源码 MUST 位于 `frontend/` 顶级目录，与后端 `src/` 分离

### Key Entities

- **Document**: 文档实体，包含 id, doc_id, title, department, doc_type, system_level, version, status, last_updated, section_count 等属性
- **Section**: 文档章节，包含 section_id, heading, content, level
- **DocumentEdge**: 文档间关系，包含 source, target, relation (traces_to/references/derived_from/constrained_by)
- **Draft**: AI 生成的对齐草稿，包含 Markdown 内容、评估结果和引用来源
- **ImpactReport**: 变更影响报告，包含触发文档、版本变更、受影响文档清单

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 用户从启动到看到仪表盘首屏渲染不超过 3 秒（开发模式）
- **SC-002**: 文档列表页在 10 份文档规模下筛选响应不超过 500 毫秒
- **SC-003**: 所有 9 个前端路由均可成功渲染且无控制台错误
- **SC-004**: `npm run build` 生成的产物可被 FastAPI 正确托管，无需 Node.js 运行时
- **SC-005**: prototype2 中的全部页面效果在新前端中完整复现
- **SC-006**: 后端现有 19 个 pytest 用例全部通过，不因前端迁移而回归

## Assumptions

- 当前后端 `/api/*` JSON 端点已基本满足前端数据需求，仅需少量补充（如 graph edges、impact report 等端点）
- prototype2 的 mock 数据结构与后端 API 响应结构可能存在差异，前端需做适配层映射
- 移除 Jinja2 模板不影响后端 API 功能，仅影响 HTML 渲染路由
- 生产部署通过 `npm run build` → FastAPI 托管 `dist/` 静态文件的方式实现
- 设计系统展示页（/design-system）作为开发辅助页面保留但不在正式导航中展示
