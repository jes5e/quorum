---
id: b.txn
type: bee
title: 'Measurement-dependent design: find how often a value a design needs was measured only after the build and its reviews, and get it measured first'
parent: null
reference_materials: null
created_at: '2026-11-16T09:52:20.121123'
status: done
schema_version: '0.1'
guid: txn63oz2ngy88ia4r33cku717gny4tkb
---

## Description

When an approved design depends on a value only a measurement can give, live_edit's runs have built and reviewed the code before taking that measurement. Then they re-opened the design mid-build: Analyst revisions, measure-and-decide gates, re-pins. Find out how often and how much it cost, and whether quorum should get the measurement taken before the build. The likely form is a breakdown goal: a measurement-dependent decision gets its own "measure and decide" Task ahead of the "build" Task.

### Evidence so far (to confirm and complete at Checkpoint 1)

- **Epic 3 Task 3** (live_edit, about 2026-11-12/13): about 11 hours of wall time and 9.5 hours of agent time. The main cause was design discovered mid-build: four Analyst rounds and three measure-and-decide gates (the D9 tables, then the re-pins).
  - Source: `~/.quorum-scratch/quorum-note-epic3-pace-20261113.md`.
  - Its recommendation 1: "Settle measurement-dependent design before a Task starts … a design pass ahead of measurement-dependent Tasks may be worth building into quorum."
- **b.cn2** (live_edit `/quo-fix-issue`, fix-reconcile-charge, 2026-11-15): derived constants in `src/`, and records whose figures come from measurement. See:
  - `proposal-b.cn2-w8rc1.md`;
  - `gate-cn2-analyst-r1.md` and `gate-cn2-analyst-r2.md`;
  - `gate-cn2-validation-r1r2.md`;
  - `test-writer-rcharge-r1-measurements.md`;
  - `run-state-quo-fix-issue-live_edit-fix-reconcile-charge.md`;
  - `ledger-20261115-1416-rc8w2k.md`.

  All are in `~/.quorum-scratch`.
- **live_edit's own response (2026-11-13):** its decider split measurement-dependent Epic 4 Tasks into "measure and decide", then "build", and ran the measure Tasks ahead on spares. Overseer 6 recorded this: `overseer-state.md` UPDATE 10.
- **live_edit suggested this to quorum on 2026-11-15** (suggestion 2). The option of carrying "the value only as text" was declined then. Find the reason in the records, or say it isn't on file.

### What to find out first (Checkpoint 1, no edits)

1. **The cases.** For each case, across Epic 3, Epic 4 so far and the fix-issue runs:
   - which value came from a measurement;
   - when it was measured, against when the code and its reviews were done;
   - what re-opening it cost: rounds, gates, wall time.
2. **Is it already handled?** Did live_edit's measure-then-build split work on the Epic 4 Tasks that used it? If it did, quorum may need only the goal that leads a breakdown to make the split itself, or nothing.
3. **The smallest change**, in the carrier the evidence points at, plus every reader:
   - breakdown's Task-cutting goals;
   - the Analyst's design proposal, which could name the measurements its design depends on;
   - fix-issue, where there's no breakdown.

   Propose nothing for a case the evidence doesn't show.

### Constraints

- **Kind 5:** earned only by what the cases show. Prefer a goal sentence in an existing rule. No new gate, phase or manifest field unless the evidence shows nothing smaller works.
- **Neutral:** no project figures, no language-specific notion of a measurement.
- **Process:** a hand-edit batch in a worktree. Orchestrator or breakdown edits are inventory-anchored, with cold reviews under the exit rule. Checkpoint 1 is for operator approval.

## Closed (2026-11-16)

Merged by fast-forward from `8059690` to `08ffbe9`, with the operator's go: "ok to your recommendations" and "ok" at Checkpoint 1, then "merge", all given in the overseer's tab.

**Commits:**
- `7f63d57`: the change, in the narrower form;
- `08ffbe9`: cold round 1.

The work was Worker 2's. Its checkpoints are `~/.quorum-overseer/btxn-checkpoint-1.md` (the case table) and `-2.md`. Full test passes (602). The overseer ran it and read the diff.

**Net shipped: +50 words,** in `skills/quo-breakdown-epic/SKILL.md` (cap 3,156 → 3,206). `docs/sdd.md` gains a matching line, which isn't capped.

### Diagnosis

- **Epic 3 Task 3:** about 3.6 h of redesign. The breakdown named the measurement open, and even predicted the gate, but ordered it after the build. The run did not recover unaided; the planner's measure-then-build split fixed it.
- **Where live_edit split:** the build held where a measure Task covered the value (Epic 3, 5b and 9b). It re-opened where a value stayed inside a build (5a1).
- **The overhead of a measure Task:** about 17 agent-minutes, 9–18% of the total (5m and 5md). The cost is in the measurement and the Analyst, which a build pays anyway.
- **b.cn2** (fix-issue): one run, loud, recovered. Measuring first would have removed none of its gates.
- **Epic 2's "9 of 15"** is not evidence for this: one of the nine is a measurement case.

### What landed

Breakdown §6's Tasks bullet:

> When the spec leaves open a choice the Tasks must commit to, ask in prose before drafting past it; when only a measurement can settle the choice, measure before building on it, as the Task's first `engineer` Subtask or, when several Tasks build on it, as a Task of its own that writes the decision into their bodies, because building first re-opens the design over built and reviewed code.

"Ask in prose" moved there from the Subtasks bullet, so one sentence decides how an open choice is settled.

### Operator decisions

- **The narrower form.** The operator asked whether a separate measure Task pays the full per-Task machinery. The evidence showed it doesn't (about 17 min of overhead), and that the defect was the order. So the measurement goes in the build Task's first `engineer` Subtask, and a separate Task is used only when several Tasks build on it.
- **Cold round 1, F1** (applied): "first step" could have been met by a `test-writer` Subtask, which runs after the build. b.cn2's design did exactly that.
- **Declined:** Analyst and fix-issue changes.

### The Analyst side note (evidence only, no ticket)

In the measurement gates (Task 3, 5m, 5md, 5a1), the Analyst never set a measured figure. Every pin was the Engineer's figure under the project's rounding rule. The Analyst earned its time on new mechanisms, accounting choices, and correcting the Engineer's figures. A misfit that only moves a figure doesn't route to the Analyst (`## Design question` fires on an unlisted mechanism), and 5a1 settled with none. live_edit's measure Tasks used the Analyst because their own bodies asked for a gate. **No quorum change is needed.**

### Watch

- The next breakdown with a measurement-dependent choice puts the measurement first.
- A measurement whose figures fit goes on to the build with no Analyst and no gate.
