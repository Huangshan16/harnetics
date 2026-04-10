# 经验与教训

## WSL / 环境
- WSL drvfs `/mnt/c` I/O error（exit code 126）→ `wsl --shutdown` 后重启，不是权限问题
- WSL 终端无法 cd 到带空格的 Windows 路径 → 用引号包裹或手动创建文件替代脚手架工具

## 前端 / Tailwind v4
- Tailwind v4 不再使用 tailwind.config.js → 改用 `@theme inline {}` 在 CSS 中定义设计 token
- shadcn/ui 的 HSL CSS 变量模式需要 `@theme inline` 桥接映射才能与 Tailwind v4 工具类配合
- 不使用 Radix UI → 用原生 HTML + React context 实现 Tabs/Select/ScrollArea，减少依赖和抽象

## TypeScript
- Vite 项目需要 `src/vite-env.d.ts`（`/// <reference types="vite/client" />`）否则 .css 导入报 TS2307
