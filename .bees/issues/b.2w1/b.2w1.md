---
id: b.2w1
type: bee
title: 'Backfill cumulative ### Feature: subsections in PRD/SDD for b.31f'
up_dependencies:
- b.31f
parent: null
reference_materials: null
created_at: '2026-05-06T17:46:31.092134'
status: done
schema_version: '0.1'
guid: 2w1mqgdy8vqph8fkjefko4crqtxp321q
---

## Description

Backfill cumulative `### Feature: <title>` subsections in the project's
PRD and SDD (`docs/prd.md`, `docs/sdd.md`) covering the work done in
Plan Bee `b.31f` ("Side-effect-free /bees-plan and /bees-file-issue
with preserved context"). The cumulative customer-facing docs
(`README.md`, `docs/doc-writing-guide.md`) likely also need a final
review pass after the Bee is done.

## Background and rationale

`b.31f` is self-referential: Epic 6 (`t1.31f.6w` — "doc-writer owns
post-impl cumulative-doc updates") is the very Epic that adds the
auto-append behavior to the doc-writer agent. Looking at the
dependency graph:

- Wave 1 (no deps): Epic 1 (`ho`), Epic 8 (`g8`)
- Wave 2 (deps on Epic 1): Epic 2 (`by`), Epic 3 (`5u`), Epic 5 (`4u`)
- Wave 3: Epic 4 (`y2` — deps on 1, 2, 3); Epic 7 (`67` — deps on 5)
- Wave 4: Epic 6 (`6w` — deps on 1, 4, 5)

Epic 6 lands LAST. Every other Epic in `b.31f` runs against the OLD
doc-writer that doesn't auto-append `### Feature:` subsections to the
cumulative PRD/SDD. Epic 6 itself, when it executes, is *editing* the
doc-writer's prose — it's not *exercising* the new behavior. So none
of `b.31f`'s 8 Epics benefit from the auto-append; the cumulative
PRD and SDD will lack a coherent `### Feature: Side-effect-free
/bees-plan and /bees-file-issue with preserved context` entry covering
the whole feature.

This is a known consequence of bootstrapping a workflow change inside
its own workflow, called out in `b.31f`'s body under
`## Bootstrap-mode note`. The fix is a single manual pass after the
Bee is done — not blocking, not breaking, just incomplete cumulative-
doc state until backfilled.

## Suggested fix

Once `b.31f` is fully `done` and committed:

1. Identify the union diff across all 8 Epics' commits — the actual
   code/prose changes that landed for the whole feature.
2. Dispatch the (now-new) doc-writer agent — or do this manually —
   to author:
   - A `### Feature: Side-effect-free /bees-plan and /bees-file-issue
     with preserved context` subsection under
     `## Per-feature scope` in `docs/prd.md`. Content drawn from
     the Plan Bee body's `## What` and `## Acceptance criteria`
     sections, narrated to reflect what was actually built.
   - A `### Feature: <same title>` subsection under
     `## Per-feature design` in `docs/sdd.md`. Content covers the
     architectural changes: Specs hive (Epic 1), the new write-prd
     and write-sdd skills (Epics 2, 3), the Plan Bee
     `reference_materials` shape change with `bees` resolver (Epic 4),
     the PM/breakdown two-hop lookup (Epic 5), the doc-writer's
     expanded responsibility (Epic 6), the file-issue redesign (Epic 8).
3. Verify `README.md` got the skill catalog table updates,
   workflow diagram updates, and upgrading-from-older-versions section
   updates that the various Epics scheduled for it (these were
   covered by the old doc-writer's diff-review pass per Epic, so
   most should already be in place — but a final coherence pass
   is wise).
4. Verify `docs/doc-writing-guide.md` got the Reference materials and
   Scoped-marker contract updates that Epic 5 scheduled. Same
   coherence-check rationale.
5. Commit the backfilled cumulative-doc subsections in a single
   `Backfill cumulative ### Feature: subsections for b.31f` commit
   so the backfill is traceable as a discrete unit.

## Out of scope

- Re-running any of `b.31f`'s Epics — the implementation work is done;
  this Issue is purely about cumulative-doc state catch-up.
- Backfilling `### Feature:` subsections for prior Plan Bees (b.5tm,
  b.9xr, b.gar, b.kw3) — they predate the new pattern and were
  explicitly out of scope per `b.31f`'s body.
- Any further design changes to the workflow.

## Dependencies

`up_deps`: `b.31f`. Cannot proceed until that Plan Bee is `done` —
the union-diff and the new doc-writer behavior both depend on every
Epic having landed.
