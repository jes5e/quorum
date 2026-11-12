---
id: b.usq
type: bee
title: Define GAP in breakdown's PM traceability prompt, so a defect in a covered requirement stops forcing another review round
parent: null
reference_materials: null
created_at: '2026-11-11T14:13:20.280135'
status: done
schema_version: '0.1'
guid: usqdentapbaccukrpijnpx974emrobcf
---

## Description

Breakdown re-runs its PM traceability review whenever a pass reports a `GAP`. The PM prompt says "Status is `OK` or `GAP`" but never defines `GAP`. So a PM marks a requirement `GAP` when the draft has any defect under it, even when a Subtask covers it. For a requirement such as "tests and CI stay green", a reviewer reading a plan can always find one more test the plan would break, so the loop has no natural end.

### Evidence (operator go 2026-11-11)

- **live_edit, `/quo-breakdown-epic` on Plan b.tv3 Epic 3 (2026-11-11): six PM rounds.** Rounds 3–5 each raised their `GAP` on the same covered row, the Epic AC "Gates (guard tests, clippy, CI)", which Task 4's AC owns:
  - r3: a test that wouldn't compile;
  - r4: tests failing under a new `TestValkey` default;
  - r5: five fixtures that bypass `TestValkey`.

  Round 6 found nothing beyond citations. The worker judged diminishing returns after r5, but the skill's rule forced r6. Files: `~/.quorum-scratch/run-state-quo-breakdown-epic-b.tv3.md` and `pm-review-dre3-w6-r1..r6.md`.
- **Frequency:** 2 of 9 saved breakdown runs went past two PM rounds (b.tv3 and b.dkt.5o).
- **Three questions:** it isn't rare, it's loud, and the run did not recover by itself, because the rule forced the extra round.

### The change

Define the status in the place both agents act on it, the PM prompt in `skills/quo-breakdown-epic/SKILL.md` §7, which the orchestrator re-dispatches on. Something like:

> `GAP` means no Subtask covers the requirement; a defect in a Subtask that covers it is a finding for the draft, not a `GAP`.

- Those defects are still fixed in the draft as `addressed-now` findings. They just stop forcing another review.
- What the draft still misses is caught when each Task is built: the Engineer's narrow tests, the per-Task PM, and CI.
- This defines a contract term two agents already key on. It adds no new rule, and no routing to other roles. (live_edit suggested routing fixture-level findings to the test-writer. That's declined: no test-writer exists at breakdown time, and the defects are already fixed in the draft.)

### Constraints

- One sentence, in §7's prompt. Reword "Status is `OK` or `GAP`" rather than adding a clause beside it.
- Check every reader of `GAP`: breakdown §7 and its report line; `agents/pm.md`, which doesn't use the word today; `docs/sdd.md`; `docs/prd.md`; and `tests/test_breakdown_structure.py` pins.
- Don't touch the re-dispatch rule itself.

## Process

A small, bounded prose fix to one rule in one place. A hand edit with one cold review, or the overseer's own trace, under the exit rule. The role-play is the b.tv3 run: replay r3–r5's findings against the new definition. Each should become `addressed-now` with no re-dispatch, while r1's real `GAP`s still re-dispatch.

## Closed (2026-11-11)

Merged by fast-forward to `1f07a70`, with the operator's go. This was one reworded sentence in §7's PM prompt (+20 words):

> Status is `GAP` when no Subtask covers the requirement, otherwise `OK`; a defect in a Subtask that covers it is a finding, not a `GAP`.

The re-dispatch rule is unchanged.

The overseer traced it in place of a cold round:
- every reader of `GAP` still holds: §7 item 3, the re-dispatch line, the report line, `docs/sdd.md:964`, and the `test_breakdown_structure.py` pins;
- Full test passes (601).

Worker 1's checkpoint is `~/.quorum-overseer/busq-checkpoint-1.md`.

### Replay

The b.tv3 run would stop after r2, not r6.
- r1 still re-dispatches on real GAPs: S7 and S10, which no Subtask covers.
- r2's three GAP rows were all covered, so they become findings. This goes further than the ticket predicted.
- r3's finds move to build-time checks, a trade the operator accepted:
  - a compile break, caught by Compile/type-check and Narrow test;
  - a metric left unremoved, caught by the per-Task PM or the code review;
  - two stale docs, caught by the Doc Writer.

### Watch

The next breakdown runs. Do they stop after a covered-row round? Do build-time checks catch what the earlier stop leaves?
