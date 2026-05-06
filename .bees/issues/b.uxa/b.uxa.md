---
id: b.uxa
type: bee
title: Add /bees-spec-review skill (apiary /req-review analog)
up_dependencies:
- b.31f
status: open
created_at: '2026-05-06T17:38:04.881184'
schema_version: '0.1'
reference_materials: null
guid: uxaubc93oz8ff6hrghtd92nnkvxy4fij
---

## Description

Add a `/bees-spec-review` skill — a fresh-eyes review pass over the
PRD and SDD ticket bodies authored by `/bees-write-prd` and
`/bees-write-sdd` (Plan Bee `b.31f` Epics 2 and 3). Parallel to our
existing `/bees-code-review`, `/bees-test-review`, and `/bees-doc-review`
skills, but for spec content. Apiary's `/req-review` is the conceptual
analog.

## Background and rationale

This was deferred during the planning of `b.31f` ("Side-effect-free
/bees-plan and /bees-file-issue with preserved context") on the
following reasoning:

- The core problem `b.31f` solves is docs pollution + info loss across
  the planning boundary — both addressable without a reviewer skill.
- `/bees-write-prd` and `/bees-write-sdd` (Epics 2 and 3 of `b.31f`)
  carry quality checklists in their own skill bodies (apiary's writers
  do — we inherit those). Baseline quality is in place before any
  formal reviewer.
- `/bees-plan`'s user-facing scope-approval and Epic-list-approval
  gates remain — covers a lot of the gap until a programmatic review
  is justified.
- Risk of premature investment: building a reviewer for problems we
  haven't observed in practice could miss the actual failure shapes
  when they emerge. Better to ship `b.31f`, observe the spec quality,
  then build the reviewer targeted at real failure modes.

This Issue exists so the design intent isn't lost — when spec quality
becomes a real pain point, this Issue is the entry point.

## Suggested fix

Once `b.31f` is in steady use:

1. Observe the failure modes of `/bees-write-prd` and `/bees-write-sdd`
   output — what shapes of low-quality spec slip through? (vague
   acceptance criteria, missing edge cases, contradictions between
   PRD and SDD, etc.)
2. Author `skills/bees-spec-review/SKILL.md` adapted from apiary's
   `/req-review`, targeting the observed failure modes.
3. Add a `/bees-write-prd` / `/bees-write-sdd` post-write hook
   (or an explicit `/bees-spec-review <spec-bee-id>` step in
   `/bees-plan`) that gates the Spec Bee's `drafted → ready`
   transition on spec-review approval.
4. Update CLAUDE.md `## Documentation Locations` if any spec-review
   guide doc gets added (parallel to the Test review guide and Doc
   writing guide entries).

## Out of scope

- Building this before `b.31f` lands and is in use. Premature
  optimization risk.
- Designing the failure-mode taxonomy without empirical data from
  actual `b.31f` runs.

## Dependencies

`up_deps`: `b.31f`. This Issue cannot proceed until that Plan Bee
is `done` and the new spec-authoring skills have been exercised
enough to identify real failure modes.

