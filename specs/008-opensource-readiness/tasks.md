# Tasks: Open-Source Readiness

**Feature**: `008-opensource-readiness`
**Generated**: 2026-04-19
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup

- [X] T001 Clean pyproject.toml: remove jinja2, add project metadata (description, authors, license, urls, classifiers) in `pyproject.toml`
- [X] T002 Create LICENSE file (Apache 2.0) at root `LICENSE`

## Phase 2: Foundational — Community Standards Files

- [X] T003 [P] Create CONTRIBUTING.md at root `CONTRIBUTING.md`
- [X] T004 [P] Create CODE_OF_CONDUCT.md (Contributor Covenant v2.1) at root `CODE_OF_CONDUCT.md`
- [X] T005 [P] Create .github/SECURITY.md at `.github/SECURITY.md`
- [X] T006 [P] Create CHANGELOG.md with v0.1.0 release notes at root `CHANGELOG.md`

## Phase 3: US1 — README Rewrite for Open-Source Audience

- [X] T007 [US1] Rewrite README.md as professional open-source project landing page at root `README.md`

## Phase 4: US2 — CI/CD Pipeline

- [X] T008 [US2] Create GitHub Actions CI workflow at `.github/workflows/ci.yml`

## Phase 5: US3 — Issue/PR Templates

- [X] T009 [P] [US3] Create Bug Report issue template at `.github/ISSUE_TEMPLATE/bug_report.yml`
- [X] T010 [P] [US3] Create Feature Request issue template at `.github/ISSUE_TEMPLATE/feature_request.yml`
- [X] T011 [US3] Create Pull Request template at `.github/PULL_REQUEST_TEMPLATE.md`

## Phase 6: Polish & Documentation

- [X] T012 Create open-source playbook doc at `docs/opensource-playbook.md`
- [X] T013 Update root AGENTS.md with 008 changelog entry at `AGENTS.md`
- [X] T014 Update specs/AGENTS.md with 008 entry at `specs/AGENTS.md`

## Dependencies

```text
T001, T002 → T003..T006 (foundational files need license chosen first)
T003..T006 → T007 (README references these files)
T007 → T008 (CI badge in README needs workflow)
T008 → T009..T011 (templates reference CI context)
T009..T011 → T012..T014 (polish after all deliverables)
```

## Parallel Execution

- T003, T004, T005, T006 can run in parallel (independent files)
- T009, T010 can run in parallel (independent templates)

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 14 |
| Setup | 2 |
| Foundational | 4 |
| US1 (README) | 1 |
| US2 (CI) | 1 |
| US3 (Templates) | 3 |
| Polish | 3 |
| Parallel opportunities | 6 |
