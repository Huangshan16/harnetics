# Implementation Plan: React Frontend Replacement

**Branch**: `002-react-frontend-replacement` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/002-react-frontend-replacement/spec.md`

## Summary

用 React 18 + TypeScript + Vite + shadcn/ui 单页应用替换现有 Jinja2/HTMX 服务端渲染前端。前端源码从 `docs/design-docs/prototype2` 迁入 `frontend/`，适配后端 API JSON 接口。后端补充 3 个缺失端点并添加 SPA fallback 路由。

## Technical Context

**Language/Version**: TypeScript 5.7 (frontend) + Python 3.11+ (backend, 已有)
**Primary Dependencies**: React 18, Vite 6, react-router-dom 6, shadcn/ui, Tailwind CSS v4, lucide-react, FastAPI (backend)
**Storage**: SQLite (backend, 已有) — 前端无本地持久化
**Testing**: pytest (backend, 已有) — 前端无测试需求 (prototype 阶段)
**Target Platform**: Modern browsers (Chrome/Edge/Firefox/Safari latest)
**Project Type**: Web application (SPA + API)
**Performance Goals**: 首屏 < 3s (dev mode), 筛选 < 500ms
**Constraints**: 生产部署无需 Node.js runtime, 前端产物由 FastAPI StaticFiles 托管
**Scale/Scope**: 9 个路由页面, 13 个 shadcn/ui 组件, 3 个布局组件

## Constitution Check

*Constitution 尚未配置自定义原则，使用默认通过。*

## Project Structure

### Documentation (this feature)

```text
specs/002-react-frontend-replacement/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-contracts.md
└── tasks.md
```

### Source Code (repository root)

```text
# 后端 (已有，仅补充端点)
src/harnetics/
├── api/
│   ├── app.py              # 修改: 添加 SPA fallback + 前端 dist 托管
│   └── routes/
│       ├── graph.py         # 修改: 新增 GET /api/graph/edges
│       ├── impact.py        # 修改: 新增 GET /api/impact (列表)
│       └── status.py        # 修改: 新增 GET /api/dashboard/stats

# 前端 (新增)
frontend/
├── index.html
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
├── vite.config.ts
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── index.css
    ├── vite-env.d.ts
    ├── lib/
    │   ├── utils.ts         # cn() 工具
    │   └── api.ts           # fetch 封装
    ├── types/
    │   └── index.ts         # TypeScript 接口定义
    ├── components/
    │   ├── Header.tsx
    │   ├── Footer.tsx
    │   ├── Hero.tsx
    │   └── ui/              # shadcn/ui 组件 (13 个)
    ├── pages/
    │   ├── Dashboard.tsx
    │   ├── Documents.tsx
    │   ├── DocumentDetail.tsx
    │   ├── DraftNew.tsx
    │   ├── DraftShow.tsx
    │   ├── Impact.tsx
    │   ├── ImpactReport.tsx
    │   ├── Graph.tsx
    │   └── DesignSystem.tsx
    └── data/
        └── mock.ts          # 开发阶段 fallback mock 数据
```

**Structure Decision**: Web application (frontend/ + 现有 src/) — 前端独立 Vite 项目，后端保持现有 src/harnetics/ 结构不变。
