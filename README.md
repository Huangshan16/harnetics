# Harnetics

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/Huangshan16/harnetics/actions/workflows/ci.yml/badge.svg)](https://github.com/Huangshan16/harnetics/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

**Aerospace document alignment workbench** — cross-department traceability, draft generation, and change impact analysis powered by document graph and LLM.

> 中文文档：[README_zh.md](README_zh.md)

## Why Harnetics

Commercial aerospace engineers pay an alignment tax every day: 40–60% of their working time disappears into hunting upstream documents, checking ICD parameters, and verifying version consistency before they can write a single usable draft.

- **What is Harnetics?** A local-first document alignment workbench for engineering teams that need traceable drafts, citation-backed review, and downstream impact analysis.
- **What concrete pain does it solve?** It compresses cross-department document preparation from 2–3 days to half a day by turning scattered requirements, ICDs, design docs, and test plans into one executable graph workflow.
- **Why is it different from generic RAG or a document assistant?** It is not just “chat over files.” Harnetics builds explicit document relations, checks citation integrity, highlights conflicts, and answers the engineering question that normal RAG ignores: “if this upstream document changes, what else must be updated?”

## 3-Minute Experience

Run the shortest possible path from clone to visible output:

1. Install dependencies.
2. Import the fixture corpus.
3. Start the app.
4. Open the dashboard.
5. Generate a demo draft or inspect an impact report.

```bash
git clone https://github.com/Huangshan16/harnetics.git
cd harnetics
uv sync --dev
cd frontend && npm install && cd ..
uv run python -m harnetics.cli.main init --reset
uv run python -m harnetics.cli.main ingest fixtures/
uv run python -m harnetics.cli.main serve --reload
```

Then open `http://localhost:8000` and try one of these two flows:

- `Draft workbench` → generate a draft for `TQ-12 liquid oxygen methane engine ground hot-fire test outline`
- `Impact analysis` → inspect how an ICD parameter change propagates into downstream test and design documents

## Core Loop

This is the product you should remember:

```text
Ingest documents
  → Build document graph
    → Generate aligned draft
      → Evaluate citations and conflicts
        → Analyze change impact
```

- **Ingest documents**: parse Markdown/YAML and extract sections, metadata, and ICD parameters.
- **Build document graph**: persist traceability edges between requirements, ICDs, design docs, templates, and tests.
- **Generate aligned draft**: use graph-backed retrieval to assemble an LLM prompt that cites real sources.
- **Evaluate citations**: run EA/EB/ED evaluators to catch missing sources, stale references, and inconsistent parameters.
- **Analyze change impact**: traverse downstream dependencies and localize which documents and sections need review.

## Demo Snapshot

Even without screenshots, the expected output is concrete.

**Generated draft excerpt**

```markdown
## 3.1 Rated thrust performance test
Verify ground thrust >= 650 kN and mixture ratio 3.5:1 under rated conditions. [📎 DOC-SYS-001 §3.2] [📎 DOC-ICD-001 ICD-PRP-001]

> ⚠ Conflict: DOC-TST-003 still cites 600 kN from an outdated ICD version.
```

**Impact report excerpt**

```text
Changed parameter: ICD-PRP-001 Ground thrust 600 kN -> 650 kN
Impacted documents:
- DOC-DES-001  | Critical | §3.1 Thrust design point
- DOC-TST-001  | Critical | §3.1 Rated thrust test
- DOC-TST-003  | Critical | §2.1 Test parameters
- DOC-OVR-001  | Major    | §4.2 Propulsion metrics
```

## Capability Snapshot

| Module | Description |
|--------|-------------|
| **Document Library** | Upload and browse Markdown/YAML documents with automatic section parsing and ICD parameter extraction |
| **Draft Generation** | LLM-powered alignment draft with citation backfill, conflict detection, and evaluator quality gates |
| **Impact Analysis** | BFS-based downstream change propagation with dual mode (AI vector + heuristic) |
| **Document Graph** | Visualize reference/derivation/constraint relationships across documents |
| **Dashboard** | Overview of document count, drafts, stale references, LLM status |

## Run Locally

### Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | ≥ 3.12 | [python.org](https://www.python.org/downloads/) |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | ≥ 20 | [nodejs.org](https://nodejs.org/) |

### Install

```bash
git clone https://github.com/Huangshan16/harnetics.git
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
├── docs/                  # Public project docs + selected local notes
│   ├── ARCHITECTURE.md    # Public architecture overview
│   ├── CHANGELOG.md       # Release history
│   ├── CODE_OF_CONDUCT.md # Community standards
│   └── CONTRIBUTING.md    # Contribution workflow
├── src/harnetics/         # Python backend
│   ├── api/               #   FastAPI app factory + routes + SPA hosting
│   │   └── routes/        #     documents / draft / impact / graph / status / evaluate
│   ├── cli/               #   typer CLI (init / ingest / serve)
│   ├── engine/            #   Draft generation, conflict detection, impact analysis
│   ├── evaluators/        #   Quality gate evaluators (EA/EB/ED)
│   ├── graph/             #   SQLite store, DDL, queries + ChromaDB vector index
│   ├── llm/               #   OpenAI-compatible client, route normalisation, diagnostics
│   ├── models/            #   Domain dataclasses (document / icd / draft / impact)
│   ├── parsers/           #   Markdown / YAML / ICD parsers
│   └── config.py          #   Settings + .env loader
├── frontend/              # React 18 SPA
│   └── src/
│       ├── pages/         #   Route pages
│       ├── components/    #   Shared UI components
│       ├── lib/           #   API client + utilities
│       └── types/         #   TypeScript domain types
├── fixtures/              # Sample aerospace documents
├── tests/                 # pytest test suite
├── AGENTS.md              # Repository map and engineering protocol
├── README.md              # English public README
├── README_zh.md           # Chinese public README
└── var/                   # Runtime data (SQLite, ChromaDB) — gitignored
```

## Documentation

| Document | Description |
|----------|-------------|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System structure, data flow, module boundaries |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | How to contribute |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Release history |
| [docs/CODE_OF_CONDUCT.md](docs/CODE_OF_CONDUCT.md) | Community standards |
| [README_zh.md](README_zh.md) | Chinese public README |
| [.env.example](.env.example) | Environment variable reference |

## Roadmap

The roadmap below is derived from the MVP definition: solve one concrete pain first, then expand document coverage and governance without breaking the core alignment loop.

| Horizon | Focus | Planned work |
|---------|-------|--------------|
| **Now (MVP)** | Core alignment loop | Markdown/YAML ingest, document graph, citation-backed draft generation, impact analysis, evaluator gates, React workbench |
| **Next (P1)** | Broader document ingestion | Add Word, PDF, and Excel parsers; strengthen ICD table extraction; add file watcher-based re-indexing |
| **Next (P1)** | Human governance | Add review queue, AI edge confirmation workflow, stale-reference remediation, stronger conflict surfacing |
| **Later (P2)** | Scale and collaboration | Move from SQLite-only assumptions toward PostgreSQL-ready scale, add richer audit/history views, team review workflows, and real-time collaboration endpoints |
| **Later (P2)** | Domain depth | Extend support for CAD metadata ingestion, more reuse-aware knowledge retrieval, and stronger cross-department traceability analytics |

## Contributing: Where to Start

- **Document parsers** are a good first contribution area if you want to improve Markdown, YAML, ICD, or future Word/PDF/Excel ingest paths.
- **Evaluators** are intentionally modular and welcome expansion, especially around citation freshness, parameter consistency, and review policy.
- **Graph/query API changes** should be discussed before implementation because they affect traceability semantics and downstream UI behavior.
- **Frontend, fixtures, and docs** are all open for contribution if you want to improve usability, demo quality, or domain realism.

## Contributing

We welcome contributions! Please read [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on:

- Setting up your development environment
- Branch naming and commit conventions
- Pull request process
- Coding standards

## License

This project is licensed under the Apache License 2.0 — see [LICENSE](LICENSE) for details.
