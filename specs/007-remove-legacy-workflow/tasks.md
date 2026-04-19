# Tasks: Remove Legacy Repository Workflow

**Input**: Design documents from `specs/007-remove-legacy-workflow/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Organization**: Tasks grouped by user story to enable incremental verification after each phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create safety net — snapshot current test baseline before any deletion

- [X] T001 Run full test suite `uv run pytest tests/ -q` and record baseline count (expect ~72 passing tests)

---

## Phase 2: Foundational — Delete Pure Legacy Files

**Purpose**: Remove files that are 100% legacy with zero new-workflow dependencies. No editing, pure deletion.

**⚠️ CRITICAL**: These deletions MUST happen before any edit tasks, because edit tasks may reference files that should already be gone.

- [X] T002 [P] Delete `src/harnetics/repository.py`
- [X] T003 [P] Delete `src/harnetics/importer.py`
- [X] T004 [P] Delete `src/harnetics/retrieval.py`
- [X] T005 [P] Delete `src/harnetics/drafts.py`
- [X] T006 [P] Delete `src/harnetics/validation.py`
- [X] T007 [P] Delete `src/harnetics/app.py`
- [X] T008 [P] Delete `src/harnetics/web/routes.py`
- [X] T009 [P] Delete `src/harnetics/web/templates/` entire directory (all HTML templates + AGENTS.md)
- [X] T010 [P] Delete `src/harnetics/web/AGENTS.md`
- [X] T011 [P] Delete `src/harnetics/web/__init__.py` if exists, then delete `src/harnetics/web/` directory entirely
- [X] T012 [P] Delete `tests/test_repository.py`
- [X] T013 [P] Delete `tests/test_importer.py`
- [X] T014 [P] Delete `tests/test_retrieval.py`
- [X] T015 [P] Delete `tests/test_drafts.py`
- [X] T016 [P] Delete `tests/test_catalog_routes.py`
- [X] T017 [P] Delete `src/harnetics/models/records.py` if exists

**Checkpoint**: All pure legacy files are gone. The project will NOT pass tests yet because conftest.py and test_app.py still reference deleted modules.

---

## Phase 3: User Story 1 — Clean Imports and Pass Tests (Priority: P1) 🎯 MVP

**Goal**: Make the project import-clean and all remaining tests pass after legacy file deletion.

**Independent Test**: `uv run pytest tests/ -q` passes with zero import errors.

- [X] T018 [US1] Clean `tests/conftest.py` — remove legacy fixtures (`temp_db_path`, `temp_app`, `imported_fixture_app`, and any `Repository`/`ImportService` imports)
- [X] T019 [US1] Clean `tests/test_app.py` — remove old `create_app()` tests, keep only `create_api_app()` tests
- [X] T020 [US1] Rewrite `tests/test_graph_store.py::test_init_db_rejects_legacy_repository_schema` to use raw SQL instead of importing `Repository`
- [X] T021 [US1] Clean `src/harnetics/config.py` — remove `DEFAULT_REPOSITORY_DB_PATH` and `database_path` settings field
- [X] T022 [US1] Clean `src/harnetics/models/__init__.py` — remove any imports of `records` module
- [X] T023 [US1] Remove `jinja2>=3.1.4` and `python-multipart>=0.0.12` from `pyproject.toml` dependencies
- [X] T024 [US1] Run `uv sync --dev` to verify dependency resolution and then `uv run pytest tests/ -q` — all tests must pass

**Checkpoint**: Project builds, imports cleanly, and all graph/API/E2E tests pass.

---

## Phase 4: User Story 2 — Verify New Workflow Integrity (Priority: P1)

**Goal**: Confirm graph API, CLI, React build all work after removal.

**Independent Test**: CLI ingest + pytest + frontend build all succeed.

- [X] T025 [US2] Run `uv run python -m harnetics.cli.main init --reset && uv run python -m harnetics.cli.main ingest fixtures/` — verify CLI still works
- [X] T026 [US2] Run `cd frontend && npm run build` — verify frontend build still succeeds
- [X] T027 [US2] Verify zero legacy references: `grep -r "from.*repository import\|Jinja2Templates\|harnetics\.db" src/ --include="*.py"` returns nothing

**Checkpoint**: Full workflow verified — no legacy code remains in source, everything runs.

---

## Phase 5: User Story 3 — Update Documentation (Priority: P2)

**Goal**: Single-architecture documentation — no "旧版" narrative, no dual-workflow confusion.

**Independent Test**: README.md 和 ARCHITECTURE.md 只描述一套架构。

- [X] T028 [US3] Update `README.md` — remove "旧版 Repository" warning, "兼容保留" text, `var/harnetics.db` references, simplify to single-workflow narrative
- [X] T029 [P] [US3] Update `ARCHITECTURE.md` — remove legacy component descriptions
- [X] T030 [P] [US3] Update root `AGENTS.md` — remove legacy entries from directory/config sections, update Active Technologies and Recent Changes
- [X] T031 [P] [US3] Update `src/harnetics/AGENTS.md` — remove entries for deleted files (repository.py, importer.py, etc.), remove web/ directory entry
- [X] T032 [P] [US3] Update `tests/AGENTS.md` — remove entries for deleted test files

**Checkpoint**: All documentation reflects single unified architecture.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Final cleanup, dependency sync, GEB documentation compliance

- [X] T033 Run `uv sync --dev` to regenerate lockfile without removed dependencies
- [X] T034 Final full test suite: `uv run pytest tests/ -q --tb=short` — all pass
- [X] T035 Verify `src/harnetics/models.py` — if this file exists at root level AND `models/` directory exists, delete the root-level `models.py` if it's purely legacy

---

## Dependencies

```text
T001 → T002..T017 (baseline before deletion)
T002..T017 → T018..T024 (files must be deleted before editing references)
T018..T024 → T025..T027 (imports clean before workflow verification)
T025..T027 → T028..T032 (code clean before doc update)
T028..T032 → T033..T035 (docs done before final polish)
```

## Implementation Strategy

1. **MVP = Phase 1-3**: Delete files + clean imports + tests pass. This is the atomic minimum.
2. **Phase 4**: Verification — could technically be part of Phase 3's checkpoint but separated for clarity.
3. **Phase 5**: Documentation — important for open-source readiness but doesn't block functionality.
4. **Phase 6**: Polish — lockfile regeneration and final validation.

## Summary

| Phase | Tasks | Parallelizable |
|-------|-------|----------------|
| Setup | 1 | 0 |
| Delete Legacy | 16 | 16 |
| Clean Imports | 7 | 0 |
| Verify Workflow | 3 | 0 |
| Update Docs | 5 | 4 |
| Polish | 3 | 0 |
| **Total** | **35** | **20** |
