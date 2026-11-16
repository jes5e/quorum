---
id: b.txn
type: bee
title: 'Measurement-dependent design: find how often a value a design needs was measured only after the build and its reviews, and get it measured first'
status: open
created_at: '2026-11-16T09:52:20.121123'
schema_version: '0.1'
reference_materials: null
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

