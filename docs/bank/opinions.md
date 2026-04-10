# 偏好与判断

## 设计系统
- 一切 UI 必须来自设计系统颜色与组件，禁止 ad-hoc 样式 (c=0.95)
- 偏好 Tailwind v4 `@theme inline` 而非 tailwind.config.js (c=0.9)
- 偏好 shadcn/ui 的 CVA + cn() + forwardRef 模式 (c=0.9)
- 不用 Radix UI，纯 HTML 原生实现更简单 (c=0.8)

## 代码风格
- 注释：中文 + ASCII 分块风格，代码看起来像顶级开源库 (c=0.95)
- 函数不超过 20 行，三层缩进即设计错误 (c=0.9)
- 偏好 amethyst-haze 紫色主题（HSL ~274°）(c=0.85)

## 工具链
- 包管理用 uv（Python）/ npm（Node）(c=0.9)
- 路径别名 `@/` → `./src/` 双配置（vite.config.ts + tsconfig.app.json）(c=0.95)
