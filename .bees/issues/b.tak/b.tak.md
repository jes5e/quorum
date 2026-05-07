---
id: b.tak
type: bee
title: Follow-up doc-consistency cleanup from b.31f post-completion review
up_dependencies:
- b.31f
parent: null
reference_materials: null
created_at: '2026-05-07T13:23:40.068255'
status: open
schema_version: '0.1'
guid: tak8c9nvbnviyeu4pm2b9gyxz2x99wk2
---

## Description

Three suggestion-level findings from the post-completion review of Bee `b.31f`
were deferred from in-session fix to keep the Bee close-out scoped to blockers
+ nits. They share a theme — stale post-redesign cross-doc consistency — and
are bundled here for a single later pass.

## Findings to address

### 1. `docs/sdd.md:12` — stale skill count

The architecture overview still says "The repo ships eleven portable-core
skills under `skills/<name>/`". Two new skills (`/bees-write-prd` and
`/bees-write-sdd`) landed under Bee `b.31f` (Epics `t1.31f.by` and
`t1.31f.5u`), bringing the count to 13. README.md:173 was updated to "13
skills"; SDD was missed.

CLAUDE.md:158 also still says "11 portable-core skills" and should be
updated for consistency in the same pass.

### 2. `docs/sdd.md:24` — incomplete resolver description

The Architecture Overview says: "Plan Bees may carry one or more on-disk
source documents (PRD, SDD, etc.) in their `reference_materials` field,
resolved per-item by the bees CLI's built-in `file-path` resolver."

The new `bees`-resolver path (Plan Bee → Spec Bee → `t1=Doc` children)
is documented in `agents/pm.md`, `skills/bees-breakdown-epic/SKILL.md`,
and `docs/doc-writing-guide.md`, but not surfaced in this overview
paragraph. Update to describe both resolver shapes.

### 3. `skills/bees-plan/SKILL.md:146, 192, 226` — "(sibling Subtask)" labels

Three inline parenthetical "(sibling Subtask)" notes on Step 4's sub-steps
4a / 4b / 4c are leftovers from the per-Subtask authoring framing in
Bee `b.31f`'s decomposition. They speak to the implementer rather than
the runtime reader. Skill prose should be project-neutral and read
naturally for a downstream user invoking `/bees-plan` — the appropriate
phrasing is "sub-step" rather than "sibling Subtask". Functional impact
is zero (runtime Claude resolves the label correctly), but the prose is
worth tightening on the next sweep.

PM review of Task `t2.31f.y2.9q` (the parent of these sub-steps)
explicitly flagged this nit and deferred it.

## Suggested fix

One small commit / Issue-fix run that:

1. Updates `docs/sdd.md:12` and `CLAUDE.md:158` to "13 portable-core skills"
   (or whatever the count is at fix time — count `skills/<name>/` directories
   that are not in the tmux-dependent set).
2. Expands `docs/sdd.md:24`'s `reference_materials` description to cover
   both `file-path` and `bees` resolvers, mirroring the contract documented
   in `docs/doc-writing-guide.md` `## Project terminology`.
3. Renames the three "(sibling Subtask)" parentheticals in
   `skills/bees-plan/SKILL.md` Step 4 to "(sub-step)" or drops them
   entirely if the surrounding prose still parses.

## Out of scope

- Anything beyond these three findings.
- Other narrative-prose drift in `docs/prd.md` / `docs/sdd.md` not
  surfaced in the post-completion review (filed separately if found later).

## Dependencies

`up_dependencies`: `b.31f`. Cannot be fully verified until that Plan Bee
is `done`, since the redesign that motivates these doc updates lives in it.
