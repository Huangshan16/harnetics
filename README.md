# Harnetics

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![CI](https://github.com/anthropic-sam/harnetics/actions/workflows/ci.yml/badge.svg)](https://github.com/anthropic-sam/harnetics/actions/workflows/ci.yml)

**Aerospace document alignment workbench** — cross-department traceability, draft generation, and change impact analysis powered by document graph and LLM.

> 商业航天工程师每天花 40–60% 的时间在文档编写和评审上。最耗时的不是"写"，而是"对齐"——确保一份文档与多部门、多层级的其他文档一致。Harnetics 通过文档图谱 + LLM 将这个过程从 2–3 天压缩到半天。

## Features

| Module | Description |
|--------|-------------|
| **Document Library** | Upload and browse Markdown/YAML documents with automatic section parsing and ICD parameter extraction |
| **Draft Generation** | LLM-powered alignment draft with citation backfill, conflict detection, and evaluator quality gates |
| **Impact Analysis** | BFS-based downstream change propagation with dual mode (AI vector + heuristic) |
| **Document Graph** | Visualize reference/derivation/constraint relationships across documents |
| **Dashboard** | Overview of document count, drafts, stale references, LLM status |

## Architecture

```
Ingest (Markdown/YAML)
  → Parse & Graph Index (SQLite + ChromaDB)
    → LLM Draft Generation (OpenAI-compatible)
      → Evaluator Quality Gates (EA/EB/ED)
        → Impact Analysis (BFS + vector search)
          → API / React SPA
```

- **Backend**: Python 3.12+ · FastAPI · SQLite · ChromaDB · OpenAI SDK
- **Frontend**: React 18 · TypeScript 5.7 · Vite 6 · Tailwind CSS v4 · shadcn/ui
- **LLM**: OpenAI-compatible routing with explicit Ollama fallback
- **Design**: Local-first — all data stays on your machine by default

## Quick Start

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.12 | [python.org](https://www.python.org/downloads/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | ≥ 20 | [nodejs.org](https://nodejs.org/) |

### Install

```bash
git clone https://github.com/anthropic-sam/harnetics.git
cd harnetics
uv sync --dev
cd frontend && npm install && cd ..
```

### Configure LLM

**Option A: Local Ollama** (offline, no API key)

```bash
export HARNETICS_LLM_MODEL="gemma3:12b"
export HARNETICS_LLM_BASE_URL="http://localhost:11434"
ollama pull gemma3:12b && ollama serve
```

**Option B: Cloud OpenAI-compatible** (any provider)

```bash
export HARNETICS_LLM_MODEL="gpt-4o"
export OPENAI_API_KEY="sk-..."
# Optional: custom base URL for third-party gateways
# export HARNETICS_LLM_BASE_URL="https://your-gateway/v1"
```

See [.env.example](.env.example) for all configuration options.

### Initialize & Run

```bash
# Seed the graph database with sample aerospace documents
uv run python -m harnetics.cli.main init --reset
uv run python -m harnetics.cli.main ingest fixtures/

# Start the server
uv run python -m harnetics.cli.main serve --reload
```

Open `http://localhost:8000` — you should see the dashboard with sample documents loaded.

For frontend hot-reload during development:

```bash
cd frontend && npm run dev    # → http://localhost:5173
```

### Smoke Test

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard/stats
curl http://localhost:8000/api/documents
```

## API Routes

| Route | Description |
|-------|-------------|
| `GET /health` | Health check |
| `GET /api/dashboard/stats` | Dashboard statistics |
| `GET /api/documents` | List all documents |
| `GET /api/documents/{doc_id}` | Document detail with sections |
| `POST /api/draft/generate` | Generate alignment draft |
| `GET /api/draft/{draft_id}` | View draft with citations |
| `POST /api/impact/analyze` | Trigger impact analysis |
| `GET /api/impact` | List impact reports |
| `GET /api/impact/{report_id}` | Impact report detail |
| `GET /api/graph/edges` | Raw graph edges |
| `GET /api/status` | LLM/embedding configuration status |

## UI Routes

| Path | Page |
|------|------|
| `/` | Dashboard |
| `/documents` | Document catalog |
| `/documents/{doc_id}` | Document detail |
| `/draft` | Draft workbench |
| `/draft/{draft_id}` | Draft viewer |
| `/impact` | Impact analysis |
| `/impact/{report_id}` | Impact report |
| `/graph` | Document graph visualization |

## Testing

```bash
# Backend
uv run pytest tests/ -q

# Frontend build
cd frontend && npm run build
```

## Docker

```bash
docker compose up
# → http://localhost:8000
```

The `docker-compose.yml` includes an optional Ollama service with GPU passthrough.

## Project Structure

```
harnetics/
├── src/harnetics/         # Python backend
│   ├── api/               #   FastAPI routes + SPA hosting
│   ├── cli/               #   typer CLI (init/ingest/serve)
│   ├── engine/            #   Draft generation + impact analysis
│   ├── evaluators/        #   Quality gate evaluators
│   ├── graph/             #   SQLite store + ChromaDB embeddings
│   ├── llm/               #   OpenAI-compatible LLM client
│   ├── models/            #   Domain dataclasses
│   └── parsers/           #   Markdown/YAML/ICD parsers
├── frontend/              # React 18 SPA
│   └── src/
│       ├── pages/         #   Route pages
│       ├── components/    #   Shared UI components
│       ├── lib/           #   API client + utilities
│       └── types/         #   TypeScript domain types
├── fixtures/              # Sample aerospace documents
├── tests/                 # pytest test suite
├── docs/                  # Design docs, specs, references
├── specs/                 # Feature specification archives
└── var/                   # Runtime data (SQLite, ChromaDB)
```

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | System structure, data flow, module boundaries |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |
| [CHANGELOG.md](CHANGELOG.md) | Release history |
| [docs/design-docs/aerospace-mvp-v3.md](docs/design-docs/aerospace-mvp-v3.md) | Core design narrative — the "why" behind Harnetics |
| [docs/design-docs/core-beliefs.md](docs/design-docs/core-beliefs.md) | Design principles |
| [docs/PRODUCT_SENSE.md](docs/PRODUCT_SENSE.md) | User profiles and value proposition |
| [docs/SECURITY.md](docs/SECURITY.md) | Security design rationale |
| [docs/RELIABILITY.md](docs/RELIABILITY.md) | Reliability boundaries |

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:

- Setting up your development environment
- Branch naming and commit conventions
- Pull request process
- Coding standards

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.
