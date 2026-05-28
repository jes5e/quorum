---
id: b.9q3
type: bee
title: /quo-plan reuse-mode Epic delete in 5d-i should guard against cascading deletes of Task children
parent: null
reference_materials: null
created_at: '2026-05-19T22:37:10.619420'
status: done
schema_version: '0.1'
guid: 9q3qkfourahdy54wr4qegnbz5huq84u7
---

## Description
b.bjp's follow-up fix (commit f0abfdf) added a reuse-mode `update-or-create-or-delete` reconcile to `/quo-plan` Step 5d-i: when re-running `/quo-plan` against an existing `drafted` Plan Bee, any existing child Epic that is NOT in the user's newly-approved Epic list is deleted via `bees delete-ticket --ids <epic-id>`. The `bees delete-ticket` CLI documents that "Deletion cascades — all child tickets are deleted too." Under the dominant reuse-mode scenario (the user Cancelled at 5e and is re-running before any Task breakdown), the deleted Epics have no children and the cascade is a no-op. But if a user gets into a sequence where an orphan `drafted` Plan Bee's Epics have already been broken down into Tasks — e.g., they Cancelled at 5e, ran `/quo-breakdown-epic` against the orphan Plan Bee anyway, then later re-ran `/quo-plan` and dropped one of those Epics from the decomposition — the reconcile silently destroys the Task work without surfacing the cascade.

## Current behavior
`skills/quo-plan/SKILL.md` Step 5a's "Reuse-mode downstream behavior" section and Step 5d-i's "Reuse-mode routing" sub-section both prescribe `bees delete-ticket --ids <epic-id>` against existing child Epics that are not in the approved Epic list. Neither sub-section checks whether the Epic has children before issuing the delete; the cascade fires silently and the user sees no warning that Task tickets were destroyed alongside the Epic.

## Expected behavior
Before issuing `bees delete-ticket --ids <epic-id>` in the reuse-mode reconcile, the orchestrator should check the Epic's `children` array (already available from the `bees show-ticket --ids <epic-id>` call 5b uses to seed the decomposition). When the children array is non-empty, surface the situation to the user via `AskUserQuestion` with finite choices — e.g., `Delete Epic and N child Task(s)` / `Keep Epic in decomposition` / `Cancel reconcile` — before the delete fires. Empty-children Epics (the dominant case) skip the prompt and delete cleanly.

## Impact
Silent destruction of authored Task content under a rare but real user sequence. Once the Tasks are gone, the work to re-author them is non-trivial — Task bodies carry codebase-research grounding from `/quo-breakdown-epic`'s explore-agent dispatch, scoped markers, and the user-approved decomposition. Losing them without warning is the failure mode the rest of the workflow's `drafted → ready → in_progress` status discipline is designed to prevent; reuse-mode shouldn't be the exception.

## Suggested fix
Add a defensive check in `skills/quo-plan/SKILL.md` Step 5d-i's "Reuse-mode routing" sub-section (and the matching prose in Step 5a's "Reuse-mode downstream behavior" section): for each existing child Epic flagged for deletion in the reconcile, inspect its `children` array from the `bees show-ticket --ids <epic-id>` payload 5b already fetches. If the array is non-empty, prompt the user via `AskUserQuestion` before issuing the delete; if empty, proceed as today.

The check is one extra branch inside an already-iterated loop, and the `bees show-ticket` payload that drives 5b's seed-from-existing-Epic-bodies behavior is already the source of truth for the children list — no extra CLI round-trip is required. Both paired POSIX and PowerShell snippets in 5d-i can stay as-is; the change is orchestrator-side prose.

## Background and rationale
This emerged from the post-landing review of b.bjp's follow-up fix (commit f0abfdf, which addressed the original Cancel-at-5e foot-gun). The follow-up correctly mirrored 4a's Spec-Bee reuse pattern on the Plan-Bee side, but 4a's pattern doesn't include a delete branch — Spec Bee reuse only ever updates the existing Spec Bee, never deletes it. The Plan-Bee reuse pattern adds the delete branch (needed because Epics drop in and out of decompositions across iterations) without inheriting the children-cascade guard the cascade behavior would warrant.

## Decisions and rejected alternatives
- **Defer to user's manual cleanup** — rejected. The whole point of b.bjp's follow-up was to eliminate manual cleanup between Cancel and re-run. Re-introducing manual responsibility here (the user must remember "don't run /quo-breakdown-epic against an orphan Plan Bee before re-running /quo-plan") puts the foot-gun back, just on a different sequence.
- **Block reuse-mode entirely when any Epic has children** — rejected as too heavy. The user may legitimately want to keep most existing Epics and just drop one childless one; blocking the whole reconcile on a single Epic having children would force them through Cancel + manual cleanup again.
- **Cascade-delete Tasks without prompting but log the deletion to the Step 5f end-of-skill report** — rejected. Surfacing the deletion *after* it happened is not the same as letting the user opt in. The report bucket is a record-keeping affordance; the gate is a decision affordance.
