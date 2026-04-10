# Tasks: React Frontend Replacement

**Input**: Design documents from `specs/002-react-frontend-replacement/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)

## Phase 1: Setup

**Purpose**: 前端项目初始化与基础结构搭建

- [x] T001 创建 `frontend/` 目录，从 prototype2 复制配置文件 (package.json/tsconfig*/vite.config.ts/index.html)，更新 package.json name 为 "harnetics-frontend"
- [x] T002 在 `frontend/` 执行 `npm install` 安装依赖
- [x] T003 [P] 复制 `frontend/src/index.css` (含 Tailwind v4 + amethyst-haze 主题变量)
- [x] T004 [P] 复制 `frontend/src/main.tsx` 与 `frontend/src/vite-env.d.ts`
- [x] T005 [P] 复制 `frontend/src/lib/utils.ts` (cn 工具函数)
- [x] T006 [P] 复制 `frontend/src/components/ui/` 全部 13 个 shadcn/ui 组件
- [x] T007 在 `vite.config.ts` 添加 API 代理配置 (proxy `/api` → `http://localhost:8000`)

**Checkpoint**: `npm run dev` 可启动空白 Vite 页面，无编译错误

---

## Phase 2: Foundational (Shared Infrastructure)

**Purpose**: 前端类型定义、API 层和全局布局 — 所有页面的共享基础

- [x] T008 创建 `frontend/src/types/index.ts`，定义 Document/Section/DocumentEdge/Draft/Citation/Conflict/EvalResult/ImpactReport/ImpactedDoc/DashboardStats 接口
- [x] T009 创建 `frontend/src/lib/api.ts`，封装 fetch 调用后端 `/api/*` 端点 (fetchDocuments/fetchDocument/fetchGraphEdges/fetchDraft/generateDraft/fetchImpactReports/fetchImpactReport/fetchDashboardStats)
- [x] T010 [P] 复制 `frontend/src/components/Header.tsx` (导航栏，含 react-router-dom Link)
- [x] T011 [P] 复制 `frontend/src/components/Footer.tsx`
- [x] T012 创建 `frontend/src/App.tsx` 路由表 (/, /documents, /documents/:id, /draft, /draft/:id, /impact, /impact/:id, /graph, /design-system)
- [x] T013 复制 `frontend/src/data/mock.ts` 作为开发阶段 fallback 数据源

**Checkpoint**: 导航栏可点击，各路由切换不报错（页面可暂为占位符）

---

## Phase 3: User Story 1 — 文档库浏览与筛选 (Priority: P1) 🎯 MVP

**Goal**: 文档列表表格 + 筛选 + 文档详情页，连接后端 API

**Independent Test**: 启动后端 → 启动前端 → /documents 显示 10 条 → 筛选 → 点击进入详情

### Implementation

- [x] T014 [US1] 创建 `frontend/src/pages/Documents.tsx`，调用 `fetchDocuments()` 渲染表格，支持 department/doc_type/system_level 筛选和搜索
- [x] T015 [US1] 创建 `frontend/src/pages/DocumentDetail.tsx`，调用 `fetchDocument(id)` 渲染元数据面板/上下游关系/章节列表
- [x] T016 [US1] 后端补充 `GET /api/graph/edges` 端点到 `src/harnetics/api/routes/graph.py`，返回所有边的 JSON 列表

**Checkpoint**: US1 完整闭环 — 文档列表 → 筛选 → 详情页 → 关系 + 章节

---

## Phase 4: User Story 2 — 草稿生成工作台 (Priority: P1)

**Goal**: 两步式草稿创建 + 草稿详情展示

**Independent Test**: /draft → 填参数 → 检索来源 → 生成 → 跳转 /draft/:id → 内容 + 评估 + 引用

### Implementation

- [x] T017 [US2] 创建 `frontend/src/pages/DraftNew.tsx`，两步式表单 (参数填写→候选文档选择→生成)，调用 `generateDraft()`
- [x] T018 [US2] 创建 `frontend/src/pages/DraftShow.tsx`，左右两栏布局 (Markdown 预览 + 评估结果/引用来源)，调用 `fetchDraft(id)`

**Checkpoint**: US2 完整闭环 — 草稿创建 → 预览 → 评估结果可见

---

## Phase 5: User Story 3 — 变更影响分析 (Priority: P2)

**Goal**: 影响分析首页 + 报告详情页

**Independent Test**: /impact → 看到报告列表 → 点击 → /impact/:id → 汇总 + 表格 + 详情

### Implementation

- [x] T019 [US3] 后端补充 `GET /api/impact` 列出所有影响报告到 `src/harnetics/api/routes/impact.py`
- [x] T020 [US3] 创建 `frontend/src/pages/Impact.tsx`，展示"发起新分析"表单和历史报告列表
- [x] T021 [US3] 创建 `frontend/src/pages/ImpactReport.tsx`，展示汇总卡片/受影响文档表格/影响详情卡片

**Checkpoint**: US3 完整闭环 — 影响首页 → 报告详情

---

## Phase 6: User Story 4 — 文档图谱可视化 (Priority: P2)

**Goal**: SVG 图谱渲染 + hover 高亮 + 部门筛选 + 节点点击跳转

**Independent Test**: /graph → 8 个节点 + 10 条边 → hover 高亮 → 点击跳转

### Implementation

- [x] T022 [US4] 创建 `frontend/src/pages/Graph.tsx`，SVG 绘制节点/边，支持 hover/筛选/点击

**Checkpoint**: US4 完整闭环 — 图谱可视化功能全部就绪

---

## Phase 7: User Story 5 — 仪表盘概览 (Priority: P3)

**Goal**: 仪表盘落地页展示统计/健康度/快捷操作/时间线

**Independent Test**: / → 仪表盘 → 3 张统计卡 + 健康度进度条 + 快捷操作 + 时间线

### Implementation

- [x] T023 [US5] 后端补充 `GET /api/dashboard/stats` 端点到 `src/harnetics/api/routes/status.py`
- [x] T024 [US5] 创建 `frontend/src/pages/Dashboard.tsx`，调用 stats API 渲染统计卡/健康度/快捷操作/时间线
- [x] T025 [P] [US5] 创建 `frontend/src/pages/DesignSystem.tsx`，设计系统展示页（从 prototype2 复制）

**Checkpoint**: US5 完整闭环 — 仪表盘功能全部就绪

---

## Phase 8: Backend Integration & SPA Fallback

**Purpose**: 后端适配前端 SPA 托管

- [x] T026 修改 `src/harnetics/api/app.py`：移除 web_router 注册，添加 `frontend/dist/` StaticFiles 托管与 SPA fallback (catch-all → index.html)
- [x] T027 验证 `npm run build` 生成 `frontend/dist/`，FastAPI 可正确托管

**Checkpoint**: 生产模式 — 单端口访问前端 + API

---

## Phase 9: Polish & Validation

**Purpose**: 全面验证与清理

- [x] T028 运行 `uv run pytest` 确保全部后端测试通过 (≥19 tests)
- [x] T029 运行前端 `npm run build`，确认零 TypeScript 错误
- [x] T030 端到端冒烟测试：init → ingest → serve → 访问所有 9 个前端路由无控制台错误

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 无依赖 — 立即开始
- **Phase 2 (Foundational)**: 依赖 Phase 1
- **Phase 3–7 (User Stories)**: 全部依赖 Phase 2，之后可并行
- **Phase 8 (Backend Integration)**: 依赖 Phase 2 + 至少 Phase 3
- **Phase 9 (Polish)**: 依赖所有前序 Phase

### User Story Dependencies

- **US1 (P1)**: Phase 2 后即可开始，无依赖其他 US
- **US2 (P1)**: Phase 2 后即可开始，可与 US1 并行
- **US3 (P2)**: Phase 2 后即可开始
- **US4 (P2)**: 需要 T016 (graph edges 端点)，可与 US3 并行
- **US5 (P3)**: 需要 T023 (dashboard stats 端点)
