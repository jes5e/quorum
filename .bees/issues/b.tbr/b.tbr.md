---
id: b.tbr
type: bee
title: Verify doc-writer idempotency on pre-redesign Plan Bees (b.9xr, b.gar)
up_dependencies:
- b.31f
parent: null
reference_materials: null
created_at: '2026-05-07T12:02:54.848076'
status: done
schema_version: '0.1'
guid: tbrcp6gv8a98by1yax57b9tk5if4bche
---

## Description

When `/quo-execute` runs against a Plan Bee that was authored by the
*pre-redesign* `/quo-plan` (one that mutated `docs/prd.md` and
`docs/sdd.md` at plan time), the post-Epic-6 doc-writer agent — which
auto-appends a `### Feature: <title>` subsection to those cumulative
docs based on the implementation diff — could produce a near-duplicate
entry alongside the stale entry the old `/quo-plan` already wrote.
Verify Epic 6's idempotency clause ("if a `### Feature: <title>`
subsection already exists in the cumulative doc, the doc-writer must
update the existing subsection rather than appending a duplicate")
correctly handles real prior-shape data.

## Background and rationale

`b.31f` Epic 6 added a new responsibility to `agents/doc-writer.md`:
after implementation lands for a feature, append (or update) a
`### Feature: <title>` subsection in the cumulative PRD/SDD. The Epic
body explicitly includes an idempotency clause covering the case where
the subsection already exists — the doc-writer must *update* the
existing entry rather than create a duplicate.

That clause covers the right case in the abstract, but `b.31f`'s
acceptance criteria don't specifically exercise it against real
prior-shape data. Specifically, two Plan Bees in this repo are
currently `ready` but unexecuted and predate the redesign:

- **b.9xr** — Optional beads backend
- **b.gar** — Test strategy for the skills repo

If either was authored by the pre-redesign `/quo-plan` Step 4 doc-
mutation flow, `docs/prd.md` and/or `docs/sdd.md` already contain
`### Feature:` subsections describing those features (likely with
forward-tense / wishful content reflecting the *plan* rather than the
*implementation*). When `/quo-execute` is eventually run against
those Bees, the new doc-writer will read the diff and want to append
a fresh `### Feature: <same title>` subsection. The idempotency clause
should cause it to update the existing one in place.

This Issue is preventive: verify the idempotency clause works in
practice — title-matching tolerance, subsection-boundary detection,
update-vs-replace semantics — against the actual content shape the
old `/quo-plan` produced.

## Suggested fix

Once `b.31f` is `done` and Epic 6 has landed, *before* executing
`b.9xr` or `b.gar`:

1. Inspect `docs/prd.md` and `docs/sdd.md` for any `### Feature:`
   subsections that match titles of unexecuted Plan Bees in the repo.
   Use `bees execute-freeform-query` to enumerate the unexecuted Plan
   Bees, then grep the cumulative docs for matching headings.
2. If matches exist, manually verify that the new doc-writer's
   idempotency logic (per Epic 6's prose in `agents/doc-writer.md`)
   correctly:
   - Detects the existing subsection by title-exact-match.
   - Replaces the subsection content with implementation-derived
     content rather than appending a sibling subsection.
   - Preserves the surrounding `## Per-feature scope` /
     `## Per-feature design` heading and any other unrelated content.
3. If the idempotency logic is shaky (e.g., title-matching is too
   strict or subsection-boundary detection misses trailing whitespace),
   either tighten the doc-writer prose or write a helper script that
   normalizes the existing subsection before doc-writer runs.
4. Once verified or remediated, proceed with `/quo-execute b.9xr`
   and `/quo-execute b.gar` as planned. Visually inspect the
   resulting cumulative docs for duplicate `### Feature:` entries.

## Trigger condition

This Issue should be addressed:

- **Before** `/quo-execute b.9xr` or `/quo-execute b.gar` runs.
- **Or** in a quick verification pass right after Epic 6 lands but
  before any old Plan Bee is executed against the new flow.

If neither b.9xr nor b.gar is ever executed (e.g., they get cancelled
or scope-merged elsewhere), this Issue can be closed without action.

## Out of scope

- Re-shaping the existing pre-redesign `### Feature:` subsections in
  `docs/prd.md` / `docs/sdd.md` (b.5tm, b.kw3 are already `done` —
  their entries can be left as historical record, refreshed only if
  someone re-touches the underlying code).
- Migrating b.9xr or b.gar to the new Spec Bee + reference_materials
  shape — explicitly out of scope per `b.31f`'s body.
- General doc-writer refactoring beyond the idempotency-verification
  pass.

## Dependencies

`up_deps`: `b.31f`. Cannot run until that Plan Bee is `done` — Epic 6
is what introduces the doc-writer auto-append behavior this Issue
verifies.
