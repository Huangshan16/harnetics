# Research: React Frontend Replacement

**Branch**: `002-react-frontend-replacement` | **Date**: 2026-04-11

## Decision 1: Frontend Framework & Build Tool

- **Decision**: React 18 + TypeScript + Vite 6
- **Rationale**: prototype2 已验证此组合。Vite 提供极快的 HMR 和构建速度。TypeScript 保障类型安全。React 18 生态成熟。
- **Alternatives**: Next.js (SSR 过重)、Astro (不需要 islands)、Vue (团队已有 React 原型)

## Decision 2: UI 组件库 & 设计系统

- **Decision**: shadcn/ui + amethyst-haze 主题 + Tailwind CSS v4
- **Rationale**: prototype2 已实现完整设计系统，组件可直接复用。shadcn/ui 生成到源码中，无黑盒依赖。
- **Alternatives**: Radix UI 裸组件 (需自建样式)、Ant Design (风格不匹配)、MUI (体积大)

## Decision 3: 前端与后端的集成策略

- **Decision**: 前端独立 Vite 项目位于 `frontend/`，开发模式下 Vite 反向代理 `/api/*` 到 FastAPI 8000 端口；生产模式 `npm run build` 产物由 FastAPI StaticFiles 托管。
- **Rationale**: 开发体验最佳——前端 HMR + 后端热重载各自独立。生产部署无需 Node.js runtime。
- **Alternatives**: 纯 SPA + 独立部署 (增加部署复杂度)、monorepo vite+fastapi 插件 (不成熟)

## Decision 4: 数据对接层

- **Decision**: 前端 `lib/api.ts` 封装 fetch 调用，TypeScript 接口定义与后端 JSON 响应对齐。Mock 数据仅在 API 不可用时作 fallback（开发阶段）。
- **Rationale**: 后端已有完整 `/api/*` 端点 (documents/draft/impact/graph/evaluate/status)，前端只需 HTTP 调用。
- **Alternatives**: GraphQL (过度)、tRPC (需要端到端 TS 栈)

## Decision 5: 旧前端处理策略

- **Decision**: 移除 Jinja2 模板渲染路由 (`web/routes.py` 中的 HTML 响应路由)。保留 `web/templates/` 目录但不再使用。不删除旧文件以降低风险——仅从 app.py 中移除 web_router 注册。
- **Rationale**: 渐进式迁移，不破坏现有 API 路由。旧模板保留作为参考。
- **Alternatives**: 完全删除旧模板 (一步到位但风险高)

## Decision 6: 后端 API 补充

- **Decision**: 后端 API 基本完备，需补充：
  1. `GET /api/graph/edges` — 返回原始边列表（前端图谱需要）
  2. `GET /api/impact` — 列出所有影响分析报告（当前缺失）
  3. `GET /api/dashboard/stats` — 仪表盘统计数据
  4. 在 `create_api_app()` 中增加 SPA fallback — 未匹配路由返回 `index.html`
- **Rationale**: prototype2 的页面需要这些端点来替代 mock 数据。
- **Alternatives**: 前端硬编码 mock (违背前后端分离原则)
