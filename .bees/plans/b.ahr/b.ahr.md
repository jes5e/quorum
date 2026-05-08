---
id: b.ahr
type: bee
title: Auto-detect URLs in /quo-file-issue and /quo-fix-issue
parent: null
children:
- t1.ahr.5a
- t1.ahr.st
reference_materials:
- value: b.q83
  resolver: bees
created_at: '2026-05-08T16:15:03.980616'
status: in_progress
schema_version: '0.1'
guid: ahrtq3uqyrvwkkb9yckfixrj75iwmriu
---

Drop the `--reference` / `--from-github` flag requirement: when a positional argument starts with `http://` or `https://`, the skill auto-routes to external-reference mode. `/quo-fix-issue` gains URL support too — files via `/quo-file-issue` (Skill-tool dispatch) then fixes end-to-end, eliminating the manual two-step. Existing flags remain accepted as silent no-op aliases for backward compat. Spec source: `b.q83` (Spec Bee with `t1=Doc` children `PRD` (`t1.q83.qb`) and `SDD` (`t1.q83.a4`)).

## Anticipated doc impact

- **`Project requirements doc (PRD)` (resolves to `docs/prd.md` per CLAUDE.md `## Documentation Locations`)** — append a new `### Feature: Auto-detect URLs in /quo-file-issue and /quo-fix-issue (no flag required)` subsection per the canonical PRD shape (`**What.**`, `**Why.**`, `**Acceptance criteria.**`, `**Out of scope.**`).
- **`Internal architecture docs (SDD)` (resolves to `docs/sdd.md`)** — append a new `### Feature:` subsection per the canonical SDD shape (`**Architecture.**`, component-level paragraphs, `**Decomposition.**`).
- **`Customer-facing docs` (resolves to `README.md`)** — update skill-table rows for `/quo-file-issue` and `/quo-fix-issue` to mention URL mode in their description columns.
