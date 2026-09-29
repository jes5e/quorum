---
id: b.i15
type: bee
title: '/quo-breakdown-epic: work addressed to ''the orchestrator'' should name the role that executes it'
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:50.238477'
status: done
schema_version: '0.1'
guid: i153stnyhchum63zqg6mn69wz19cxsu5
---

## Description

`/quo-breakdown-epic` can write a Subtask that asks "the orchestrator" to do something: b.v9c Epic 1's `t3.v9c.94.o1.ps` asks the orchestrator to record Epic completion notes. `/quo-execute` has no step for that, so the request relies on the agent improvising (in the b.87t validation run the PM's check routed it to the Engineer, and it was later recorded as a deferral).

## Expected behavior

Every piece of work breakdown writes names a role that executes it (the role tag already does this for Subtasks); a record the Epic needs belongs in a role's Subtask or in the Task body, not addressed to the orchestrator.

## Suggested fix

One goal sentence in breakdown's Subtask rules, if the big feature's breakdown shows the pattern again. Evidence: `/tmp/.quorum/b87t-checkpoint-5.md` (lost in a 2026-09-28 restart; copy at `~/.quorum-overseer/precedent-b87t-checkpoint-5.md`).
## Not repeated (2026-09-29)

The breakdown of b.v9c Epics 2–3 (live_edit worktree, commits `e548ae5e` and `ed487909`; 10 Tasks) addresses no work to "the orchestrator". Evidence so far is one occurrence, so it leans toward no rule.
## Closed (2026-09-29, operator)

No rule: one occurrence (b.v9c), and no recurrence in the b.v9c Epics 2–3 breakdown (10 Tasks, checked). Reopen if it recurs.
