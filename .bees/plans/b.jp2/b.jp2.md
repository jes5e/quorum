---
id: b.jp2
type: bee
title: Simplify the context-window guard
parent: null
children:
- t1.jp2.z7
- t1.jp2.q4
reference_materials:
- value: b.d8n
  resolver: bees
created_at: '2026-09-03T00:30:16.200635'
status: ready
schema_version: '0.1'
guid: jp2y4xww99rm6ti14c9p81djahtwygsu
---

Slim the context-window guard shipped by Plan b.55r to its load-bearing core while keeping its guarantee (stop cleanly at an Epic/Issue boundary when context usage leaves insufficient room for the next unit): the missing-reading hard-stop gate and persistent opt-out marker become a one-line fail-open notice; the three duplicated ~100-line guard sections in `/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` collapse into one shared procedure file (`skills/quo-setup/context-guard.md`) read at the boundary; the stop threshold is derived at run time from the operator's effective compaction window and the next unit's Task count instead of a fixed constant; readings are recorded at run start, per Task, per unit, and at run end so the provisional constants can be recalibrated from data; and the triplicated contract docs are trimmed to one shipped source of truth.

Authoritative spec: the PRD (`t1.d8n.9g`) and SDD (`t1.d8n.nd`) children of Spec Bee **b.d8n**. **Sequenced after** Issues b.pdq, b.q3f, b.nn8, and b.y2q land and `fix/b.ja9` is fast-forwarded to `main`. Two Epics in a strict chain (1 → 2). Epic 1 changes only the gauge helper, its tests, and the engineering-practices doc, in a backward-compatible way (the installed orchestrators' bare `stop-threshold` call keeps working), so the contract the procedure consumes exists before the consumers change; Epic 2 changes everything the orchestrators, setup skill, and remaining docs touch, plus the helper's opt-out removal (so callers and callee change together). The helper and its test module are therefore touched by both Epics in disjoint places; no function, test, or doc section is edited by both.

## Anticipated doc impact

- **Customer-facing docs** (`Customer-facing docs` key): README's long-runs paragraph, `### The context-usage gauge file` (both temp-directory namespaces stated plainly), `### Enabling the gauge producer` (two-option gate, no opt-out), and `### Scratch files` (no opt-out resident). Epic 2.
- **Internal architecture docs (SDD)** and **Project requirements doc (PRD)** (`Internal architecture docs (SDD)` / `Project requirements doc (PRD)` keys): corrections to the b.55r subsections' opt-out and threshold statements, plus one cumulative `### Feature: Simplify the context-window guard` subsection in each — including the threshold derivation formula and the recalibration procedure — authored exactly once by the post-implementation doc-writer pass under **Epic 2** (the final Epic). Epic 1 must NOT touch these docs.
- **Doc writing guide** (`Doc writing guide` key): `## The context-gauge file contract` — mid-turn-refresh correction, lockstep-list update, opt-out paragraph removed, section reduced to contributor rationale plus a pointer to the helper docstring. Epic 2.
- **Engineering best practices** (`Engineering best practices` key): the "auto-compaction fires at roughly 83%" statement replaced with the derived formula and the operator knobs, labeled version-bound. Epic 1.
- **Repo guidance** (`CLAUDE.md`, this repo only): helper description bullets updated, the opt-out scratch-file exception and related mentions removed, the shared procedure file added to the repo-layout bullet. Epic 2.
- **Follow-up Issue b.ebw** (filed from this plan's deferral gate, not by an Epic): unify the two temp-directory conventions (helper `tempfile.gettempdir()` vs. prose literal `/tmp`). Epic 2's README wording is the interim state until b.ebw lands.
