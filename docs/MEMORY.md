# Harnetics 开发记忆

## 用户画像
- Sam · 商业航天文档对齐产品 · 深度思考型 · 追求"好品味"的代码美学
- 交互语言中文 · 技术思考英文 · 注释中文 ASCII 分块风格
- 偏好 Tailwind v4 + shadcn/ui 模式 · 不用 Radix UI · 纯 HTML 原生实现优先

## 项目状态
- 阶段：MVP 原型迭代 · prototype2（React + Vite + Tailwind v4 + shadcn）已完成全部页面
- 后端：Python + FastAPI · SQLite · 文档解析 + LLM 对齐 + 评估管线
- 核心交付物：文档库 → 草稿台 → 变更影响分析 → 文档图谱

## 活跃约束
- GEB 分形文档协议：代码变更必须同步 L1/L2/L3 AGENTS.md
- 设计约束：一切 UI 设计必须来自设计系统的颜色和组件
- 文件规模：每文件 ≤800 行 · 每目录层 ≤8 文件

## 验证过的路径
- WSL drvfs I/O error → `wsl --shutdown` 而非修权限
- Tailwind v4 主题：`@theme inline` + `hsl(var(--x))` 映射 CSS 变量
- prototype2 路径别名：`@/` → `./src/`（vite.config.ts + tsconfig.app.json 双配置）
