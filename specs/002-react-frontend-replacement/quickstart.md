# Quickstart: React Frontend Replacement

## 前置条件

- Python 3.11+ + uv (后端)
- Node.js 20+ + npm (前端)

## 安装与启动

```bash
# 1. 后端依赖
uv sync --dev

# 2. 初始化数据库并导入样本
uv run python -m harnetics.cli.main init --reset
uv run python -m harnetics.cli.main ingest fixtures/

# 3. 启动后端 API (端口 8000)
uv run python -m harnetics.cli.main serve --reload &

# 4. 前端依赖
cd frontend
npm install

# 5. 启动前端 dev server (端口 5173, 代理 /api → localhost:8000)
npm run dev
```

打开 http://localhost:5173 即可看到 React 前端。

## 生产构建

```bash
cd frontend
npm run build
# 产物在 frontend/dist/
# 后端 FastAPI 自动托管 dist/ 静态文件
```

## 冒烟测试

```bash
# 后端 API
curl http://localhost:8000/health
curl http://localhost:8000/api/documents

# 前端 (dev 模式)
# 打开 http://localhost:5173 → 看到仪表盘
# 点击"文档库" → 10 份文档
# 点击 DOC-ICD-001 → 文档详情
```
