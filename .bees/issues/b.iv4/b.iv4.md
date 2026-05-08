---
id: b.iv4
type: bee
title: 'Refactor /quo-file-issue: fold Step 4 into Step 3 (option-a structural cleanup)'
parent: null
reference_materials: null
created_at: '2026-05-07T11:30:24.765544'
status: done
schema_version: '0.1'
guid: iv4o16qh5b8dug5f8njoqff8i4hd5eqh
---

## Description

Refactor `skills/quo-file-issue/SKILL.md` Steps 3 and 4 by folding
Step 4 entirely into Step 3, eliminating the temporal-ordering
ambiguity between "create the ticket" and "capture doc divergence in
the body" that today is bridged by a one-line clarifier paragraph.

## Background and rationale

During the execution of `b.31f` Epic 8 (`/quo-file-issue` redesign),
the per-Task PM review surfaced a temporal-ordering ambiguity between
Step 3 (create ticket via `bees create-ticket`) and Step 4 (the new
"capture `## Doc divergence noted` in the body" step). PM offered two
fix shapes:

- **Option (a) — structural rewrite.** Fold Step 4 entirely into
  Step 3, so the body-template-with-optional-doc-divergence-section
  is authored before `bees create-ticket` runs and there is no
  separate Step 4 with its own ordering question. This is the
  cleaner shape — Step 3 becomes the single locus of "decide what
  goes in the body, then file." But it's a structural rewrite of
  Step 3's prose.
- **Option (b) — one-line clarifier.** Leave Step 3 and Step 4 as
  separate steps in their current shape, add a one-line paragraph
  clarifying the temporal interleaving. Smaller blast radius — only
  one paragraph changes — but the underlying two-step shape remains.

The fix landed during `b.31f` chose **option (b)** (commit `4d88445`
on the `b.31f` execution branch) because (i) it was a fix-up
inside an already-PM-reviewed Epic, where minimum-blast-radius is
preferable to structural rewrites, and (ii) the clarifier paragraph
is sufficient to remove the ambiguity for any reader who notices it.

Option (a) remains the cleaner long-run shape. This Issue exists so
the cleaner alternative isn't lost — when a future reader of
`skills/quo-file-issue/SKILL.md` Steps 3 and 4 finds the
interleaving still confusing, this Issue is the entry point for the
restructure.

## Suggested fix

When the trigger condition is met (a reader finds Steps 3/4
confusing despite the option (b) clarifier):

1. Read `skills/quo-file-issue/SKILL.md` Steps 3 and 4.
2. Restructure: collapse Step 4's "capture `## Doc divergence noted`"
   guidance into Step 3's body-authoring prose. Step 3's body
   template becomes the canonical location where ALL optional
   sections (`## Doc divergence noted`, `## Background and
   rationale`, `## Decisions and rejected alternatives`) are
   documented and conditionally populated.
3. Renumber subsequent steps (Step 5 → Step 4, etc.) and update any
   cross-references inside the file.
4. Verify the restructured prose preserves all current behavior:
   the doc-divergence capture pattern, mid-conversation context
   awareness, the optional-rationale-sections template, and the
   `/quo-fix-issue` doc-writer consumption hook.
5. Run a quick read-through against `skills/quo-fix-issue/SKILL.md`
   to verify the cross-skill references (mentions of
   `/quo-file-issue`'s steps by number) are still accurate, or
   make them name-based instead of number-based to avoid future
   renumbering churn.

## Trigger condition

This is a quality / clarity refactor, not a bug. File when the
reader-confusion threshold is met:

- A future maintainer (human or agent) reads
  `skills/quo-file-issue/SKILL.md` Steps 3-4 and finds the
  interleaving confusing despite the option (b) clarifier paragraph.
- Or: a `/quo-file-issue` review run flags Steps 3-4 ordering
  as still ambiguous.
- Or: a sibling skill's redesign (`/quo-plan`, `/quo-fix-issue`)
  prompts a coherence pass across the planning/filing skills and
  the option (b) shape stands out as inconsistent.

If none of these triggers fire, the option (b) shape is fine to leave.

## Out of scope

- Re-litigating the option (a) vs option (b) choice for `b.31f`'s
  in-flight fix. That decision is made and the fix is committed.
- Other refactors to `/quo-file-issue` beyond Steps 3-4. Any other
  changes should be filed separately.
- Changes to `/quo-fix-issue` beyond the cross-reference accuracy
  check in step 5 of the suggested fix.

## Dependencies

None. `b.31f` does not need to be `done` first — Steps 3-4 in their
post-Epic-8 shape are already in place. This Issue is forward-looking
cleanup, runnable any time the trigger condition is met.
