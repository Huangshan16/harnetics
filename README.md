# Harnetics

商业航天文档对齐产品工作台。当前实现是一条最小可运行闭环：导入受控文档，浏览目录，基于模板和来源文档生成带引注的草稿，并在浏览器里编辑与导出。

## 当前能力

- 导入 Markdown front matter 文档和 YAML 接口文档
- 将文档、章节、模板、草稿和校验结果持久化到 SQLite
- 提供 `/documents/*` 和 `/drafts/*` Web 工作台
- 通过本地 OpenAI-compatible LLM 生成 Markdown 草稿
- 对草稿执行引注和最小规则校验

## 依赖

- Python `>=3.12`
- `uv`
- 一个本地 OpenAI-compatible 接口，默认地址是 `http://127.0.0.1:11434/v1`

当前默认模型配置在 [src/harnetics/config.py](src/harnetics/config.py)，默认值是 `gemma-3-27b-it`。如果本机没有本地模型服务，应用仍可启动，但草稿生成接口会失败。

## 安装

```bash
uv sync --dev
```

## 启动

```bash
uv run uvicorn harnetics.app:app --app-dir src --reload
```

默认访问地址：

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/documents`
- `http://127.0.0.1:8000/drafts/new`

根路径 `/` 会重定向到 `/documents`，用于作为浏览器首页入口。

运行时数据默认落在当前工作目录下的 `var/`：

- `var/harnetics.db`
- `var/uploads/`
- `var/exports/`

如果你想做隔离冒烟，不污染仓库根目录，可以从临时目录启动，但把代码入口仍指向仓库：

```bash
export REPO_ROOT=/path/to/harnetics
cd /tmp/harnetics-smoke
$REPO_ROOT/.venv/bin/python -m uvicorn \
  harnetics.app:app \
  --app-dir $REPO_ROOT/src \
  --host 127.0.0.1 \
  --port 8765
```

## 最小跑通路径

1. 启动应用。
2. 导入样本文档。
3. 访问 `/documents` 确认文档已入库。
4. 访问 `/drafts/new` 生成草稿。
5. 在草稿详情页编辑并导出 Markdown。

用 `curl` 导入样本：

```bash
curl -F file=@fixtures/requirements/DOC-SYS-001.md http://127.0.0.1:8000/documents/import
curl -F file=@fixtures/design/DOC-DES-001.md http://127.0.0.1:8000/documents/import
curl -F file=@fixtures/templates/DOC-TPL-001.md http://127.0.0.1:8000/documents/import
curl -F file=@fixtures/test_plans/DOC-TST-003.md http://127.0.0.1:8000/documents/import
```

## 测试

```bash
uv run pytest -q
```

这次我实际跑通了下面这条链路：

- 启动 FastAPI 应用
- `GET /health`
- 导入 `fixtures/` 下 4 份样本文档
- `GET /documents`
- `POST /drafts/plan`
- `POST /drafts`
- `GET /drafts/1`
- `GET /drafts/1/export`

其中草稿生成阶段使用了一个临时本地 mock OpenAI-compatible 服务来占位默认 LLM 端口，目的是验证应用链路本身，而不是验证某个具体模型。

## 目录入口

- [ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/PRODUCT_SENSE.md](docs/PRODUCT_SENSE.md)
- [docs/RELIABILITY.md](docs/RELIABILITY.md)
- [docs/SECURITY.md](docs/SECURITY.md)
- [docs/product-specs/mvp-prd.md](docs/product-specs/mvp-prd.md)
