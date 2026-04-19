<!--
[INPUT]: 依赖根目录模块边界、fixtures/ 样本文档库与本地规划工作区约束
[OUTPUT]: 对外提供当前系统结构、数据流与演进方向说明
[POS]: 项目根目录的公开架构总图，被 README.md、README_zh.md 与 AGENTS.md 引用
[PROTOCOL]: 变更时更新此头部，然后检查 AGENTS.md
-->

# Harnetics 架构总图

## 当前形态

仓库已收敛为单一工作流——FastAPI 图谱后端 + React/Vite SPA 前端：

- `fixtures/`：机器相原始语料，提供受控需求、设计、模板与测试样本。
- `src/harnetics/`：运行时主干，包含图谱存储、文档索引、草稿引擎、影响分析与 API 层。
- `frontend/`：React 18 SPA，基于 shadcn/ui + Tailwind v4 构建。
- 根级 `README.md` / `README_zh.md` / `ARCHITECTURE.md`：对外公开入口，承载开源仓库所需的运行与架构说明。
- `docs/` / `specs/`：本地规划工作区，保留设计稿、Spec Kit 产物与内部参考，但默认不进入 Git 发布。

## 核心数据流

1. `DocumentIndexer` 从 `fixtures/` 或上传文件解析 Markdown/YAML，提取章节、引用关系和 ICD 参数，持久化到 SQLite graph store (`var/harnetics-graph.db`)。
2. `DraftGenerator` 基于图谱中的来源文档与引用关系，经 OpenAI-compatible LLM 生成带引注的 Markdown 草稿。
3. `EvaluatorBus` 运行 8 个评估器（EA/EB/ED 系列），产出 Pass/Warning/Blocker 级别的质量门结果。
4. `ImpactAnalyzer` 沿引用图进行 BFS 遍历，分析文档变更对下游文档的波及影响。
5. `api/` 层暴露 REST JSON 端点，React SPA 通过 `/api/*` 消费数据。
6. 本地工作区 `docs/` 持续沉淀规格、执行计划和 schema 说明；公开仓库则由根级文档承担稳定入口。

## 模块边界

| 模块 | 职责 | 演进方向 |
| --- | --- | --- |
| `src/harnetics/graph/` | SQLite 图谱存储、DDL、索引引擎、向量检索 | 接入更细粒度 section-ranking |
| `src/harnetics/engine/` | 草稿生成、冲突检测、影响分析 | 引入更强约束与多轮生成 |
| `src/harnetics/evaluators/` | 草稿质量门评估器集合 | 扩展版本比对与参数一致性 |
| `src/harnetics/llm/` | OpenAI-compatible 会话客户端 + Ollama 兼容 | 多模型路由 |
| `src/harnetics/api/` | REST JSON API + SPA 静态托管 | 增加实时协作端点 |
| `src/harnetics/cli/` | init/ingest/serve 命令入口 | 增加 export/migrate 命令 |
| `frontend/` | React SPA 前端 | 增加更细的编辑/审阅交互 |
| `fixtures/` | 航天领域受控样本库 | 持续补充评测和回归语料 |
| 根级文档 | 对外公开的安装、架构、贡献与变更说明 | 保持 GitHub 首页和开源入口清晰稳定 |
| `docs/` / `specs/` | 本地规划、设计与特性闭环工件 | 保持为本地工作区，不进入 Git 发布物 |

## 运行时原则

- Graph Store 是唯一 SQLite 边界，引擎层不直接写 SQL。
- 索引、生成、评估分层明确，API 层只做请求编排与序列化。
- 当前实现闭环：导入文档 → 图谱索引 → 生成带引注草稿 → 评估质量门 → 影响分析 → 图谱可视化。
- 后续演进应继续消除特殊分支，而不是把复杂性堆进路由或模板。
