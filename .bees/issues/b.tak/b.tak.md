---
id: b.tak
type: bee
title: Follow-up doc-consistency cleanup from b.31f post-completion review (extended after fresh-eyes review)
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

Suggestion-level findings from the post-completion review of Bee `b.31f`
and from a follow-up code review session, all sharing a theme — stale
post-redesign cross-doc consistency — bundled here for a single later
pass. Findings 1-3 came from the post-completion review; findings 4-6
came from a subsequent fresh-eyes code review against the merged work.

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

### 4. `skills/bees-setup/SKILL.md:732` — stale `/bees-plan` prose in Next Steps

The "Next Steps" section's `/bees-plan` recommendation describes
pre-redesign behavior on three counts:

- *"optionally drafts PRD/SDD updates if the project has those docs"* —
  Step 4 doc-mutation was stripped under Epic `t1.31f.y2`; `/bees-plan`
  no longer drafts doc updates at plan time.
- *"The Plan Bee body itself becomes the authoritative scope document
  when no PRD/SDD exist (the Bee's `reference_materials` stays empty)"* —
  `/bees-plan` always creates a Spec Bee now (per its own SKILL.md
  Step 4 + Step 5a clauses) and always sets `reference_materials` to
  point at it. The body-as-spec branch was explicitly removed from
  `/bees-plan` itself; it survives only as a downstream-consumer
  fallback for legacy Bees with empty `reference_materials`.
- *"downstream skills (`/bees-breakdown-epic`, `/bees-execute`) will use
  the Bee body as the spec source"* — only true for legacy/bootstrap
  Plan Bees with empty `reference_materials`, not for new
  `/bees-plan`-authored ones.

The whole bullet should be rewritten to describe the new flow (creates
Spec Bee + PRD/SDD `t1=Doc` children + Plan Bee with `bees`-resolver
`reference_materials`).

Same flavor as findings 1-2 (stale post-redesign prose) but in a
different file the post-completion review didn't sweep.

### 5. `README.md:108` — "Plans + Issues" should be "Plans + Issues + Specs"

The "After install" paragraph says:

> *"It will colonize hives (Plans + Issues), write a `## Documentation
> Locations` and `## Build Commands` section to CLAUDE.md, and offer
> to bootstrap baseline PRD/SDD docs..."*

The hive list is now three. The post-completion review updated the
workflow diagram, status table, and the upgrading section to mention
Specs, but missed this line. README's other prose elsewhere correctly
mentions Specs.

### 6. `README.md:14` — workflow diagram annotation `(Specs hive, t1)`

The workflow diagram labels `Spec Bee  (Specs hive, t1)`. The Spec Bee
itself is `--ticket-type bee`, not `t1`; the `t1` annotation belongs to
the PRD/SDD children listed below. As written, a new reader of the
diagram would think the Spec Bee is `t1`-tier, which is wrong.

Suggested fix: change `(Specs hive, t1)` to `(Specs hive, top-level)`
or just `(Specs hive)`.

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
4. Rewrites `skills/bees-setup/SKILL.md`'s `/bees-plan` Next Steps bullet
   (line ~732) to describe the post-redesign flow: creates a Spec Bee in
   the Specs hive with PRD and SDD as `t1=Doc` children (via inline
   delegation to `/bees-write-prd` and `/bees-write-sdd`), then a Plan
   Bee whose `reference_materials` points at the Spec Bee via the `bees`
   resolver. No mention of "drafts PRD/SDD updates" or
   "`reference_materials` stays empty" — both are pre-redesign behavior.
5. Updates `README.md:108` from `(Plans + Issues)` to
   `(Plans + Issues + Specs)`.
6. Updates `README.md:14`'s workflow diagram annotation from
   `Spec Bee  (Specs hive, t1)` to `Spec Bee  (Specs hive, top-level)`
   (or drops the parenthetical entirely if surrounding context already
   makes it clear the Spec Bee is top-level).

## Out of scope

- Anything beyond these six findings.
- Other narrative-prose drift in `docs/prd.md` / `docs/sdd.md` not
  surfaced in the post-completion or follow-up reviews (filed separately
  if found later).

## Dependencies

`up_dependencies`: `b.31f`. Cannot be fully verified until that Plan Bee
is `done`, since the redesign that motivates these doc updates lives in
it. (`b.31f` is now `done`, so this Issue is unblocked.)

