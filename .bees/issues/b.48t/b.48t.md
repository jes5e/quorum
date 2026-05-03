---
id: b.48t
type: bee
title: 'bees-execute: don''t suggest closing Plan Bee when drafted Epics still exist'
status: open
created_at: '2026-05-02T23:53:59.186300'
schema_version: '0.1'
egg: null
guid: 48tfudrfbgnj1udodkvbpjzwmfcnjw9y
---

## Description

`bees-execute` mistakes "no more *workable* Epics" for "Bee is done." When a Plan Bee contains multiple Epics but only the first one has been broken down via `/bees-breakdown-epic`, the remaining Epics are still in `status=drafted`. After the first Epic completes, the skill proceeds to final review and asks the user to mark the Bee done — instead of telling them to break down the remaining Epics first.

This was hit in a real project: only the first Epic was broken down, `/bees-execute` ran on it, and after completion the agent suggested closing the Plan Bee. The other Epics in the plan were still drafted and unfinished.

There are two coupled defects in `skills/bees-execute/SKILL.md`:

### Defect A — Step 4.2 ("Find next Epic or move to Final Review")

Step 4.2 (lines 442-463) flows from the just-completed Epic into one of two branches:

> "If there are more Epics to work on … go back to step 2. If not, move to final Bee review."

"More Epics to work on" implicitly means *workable* Epics — Step 2's filter is `status` in `{ready, in_progress}` with all `up_dependencies` `done`. There is no check for the third case: **other Epics under this Bee exist but are still in `status=drafted` (or are `ready` but blocked on a dependency that's still `drafted`).** Drafted Epics fall through both branches and the skill proceeds to Step 5 final review.

### Defect B — Step 8 ("Mark Bee Complete")

Step 8 (lines 577-589) runs:

```
bees update-ticket --ids <epic-id> --status done   # for every Epic in the Bee
bees update-ticket --ids <bee-id> --status done
```

Step 8 has no precondition that every Epic is already `done` from the per-Epic loop. If the user answers "Yes, mark as done" in Step 7 while drafted Epics remain, Step 8 silently flips those drafted Epics to `done` — burying unbroken-down planned work behind a green status. The Bee then looks finished even though planned scope was never executed.

## Current behavior

1. User runs `/bees-plan` → Plan Bee created with Epics E1, E2, E3 in `status=drafted`.
2. User runs `/bees-breakdown-epic` on E1 only → E1 becomes `ready` with Tasks/Subtasks; E2 and E3 stay `drafted`.
3. User runs `/bees-execute` → completes E1.
4. Step 4.2 searches for the "next Epic to work on," sees no `ready`/`in_progress` Epics, and falls through to "move to final Bee review."
5. Steps 5-7 run. Step 7 asks "Are you ready to mark this Bee as done?"
6. If user says yes, Step 8 marks E1, E2, E3, and the Bee itself as `status=done` — even though E2 and E3 were never broken down or executed.

## Expected behavior

Step 4.2 should classify the post-Epic state into three cases, not two:

- **Workable Epics remain** (`ready`/`in_progress`, dependencies `done`) → continue the loop (current "if" branch).
- **All Epics under this Bee are `done`** → proceed to final review (current "else" branch).
- **Other Epics exist in `drafted` state** (or in `ready` blocked on a `drafted` dependency) → stop the loop and tell the user: "Epic <id> is complete, but Epics <ids> in this Bee are still drafted and need breakdown before this Bee can be closed. Run `/bees-breakdown-epic <bee-id>` (in a fresh session is reasonable to keep context clean) to break down the remaining Epics, then re-run `/bees-execute <bee-id>`." Do **not** proceed to Step 5 final review and do **not** offer to mark the Bee done.

Step 8 should hard-fail with a clear message — not silently mass-mark — if any Epic under the Bee is not already `status=done`. This is a defense-in-depth check; the Step 4.2 fix should already prevent reaching Step 8 with drafted Epics, but the destructive bulk update should refuse to fire if its precondition is violated.

The status vocabulary for the Plans hive is documented in this repo's `CLAUDE.md` `## Hives and status vocabulary` section: `drafted` → `ready` → `in_progress` → `done`. The fix should reference `drafted` explicitly in the new Step 4.2 branch.

## Impact

- **Correctness (high).** Defect B is destructive: it flips drafted Epics — which represent planned but un-executed work — to `done`. Once marked done, downstream queries (`status=ready` Epic lookups, Bee-level "is this finished?" checks) treat that scope as shipped. The user has to manually audit and revert, or worse, the planned work is never recovered.
- **UX (medium).** Defect A makes `/bees-execute` actively misleading at the close-out step. The user expects the skill to know whether their plan is done and instead gets a "ready to close?" prompt as if it were.
- **Workflow integrity.** The bees workflow's value is that ticket state is a reliable source of truth; both defects undermine that.

## Suggested fix

Both defects sit in `skills/bees-execute/SKILL.md`. The fix is one coherent change touching two adjacent steps:

**Step 4.2 — re-query for any non-`done` Epics, not just workable ones.** After the inter-Epic checkpoint passes, run a query that returns *all* Epics under the Bee with their `ticket_status` and `up_dependencies`:

```yaml
stages:
  - [parent=<bee-id>, type=t1]
report: [title, ticket_status, up_dependencies]
```

Branch on the result:

1. Any Epic with `status` in `{ready, in_progress}` and dependencies satisfied → continue loop (existing behavior).
2. Any Epic with `status=drafted`, OR `status=ready` blocked on a non-`done` dependency → stop the loop, tell the user which Epics still need breakdown, suggest `/bees-breakdown-epic <bee-id>` (a fresh session is reasonable for context hygiene), and exit. Do not advance to Step 5.
3. All Epics `done` → proceed to Step 5 final review (existing "else" branch).

**Step 8 — add a precondition guard.** Before the bulk `bees update-ticket --ids <epic-id> --status done`, verify every Epic under the Bee is already at `status=done` (from the loop in Step 4.2). If any Epic is not `done`, abort with `Cannot mark Bee complete — Epics <ids> are still <status>. Run /bees-breakdown-epic and /bees-execute on them first.` Do not silently flip them. The original wording "Mark all Epics in the Bee as `status=done`" is wrong as a directive — by the time Step 8 runs in a healthy flow, every Epic should already be `done` from per-Epic transitions in Step 4.1; the bulk update is at best a no-op safety net and at worst the destructive action described above. Rewrite as a precondition check rather than a write.

**Key files:**
- `skills/bees-execute/SKILL.md` — Step 4.2 ("Find next Epic or move to Final Review", lines ~442-463) and Step 8 ("Mark Bee Complete", lines ~577-589).
- This repo's `CLAUDE.md` `## Hives and status vocabulary` section is the canonical reference for the `drafted` → `ready` → `in_progress` → `done` ladder; the new Step 4.2 prose should align with it.

No changes needed to `bees-breakdown-epic` or `bees-plan` — those skills behave correctly; the bug is purely in `bees-execute`'s end-of-loop classification and Bee-close precondition.

