---
id: b.i15
type: bee
title: '/quo-breakdown-epic: work addressed to ''the orchestrator'' should name the role that executes it'
status: open
created_at: '2026-09-27T14:04:50.238477'
schema_version: '0.1'
reference_materials: null
guid: i153stnyhchum63zqg6mn69wz19cxsu5
---

## Description

`/quo-breakdown-epic` can write a Subtask that asks "the orchestrator" to do something: b.v9c Epic 1's `t3.v9c.94.o1.ps` asks the orchestrator to record Epic completion notes. `/quo-execute` has no step for that, so the request relies on the agent improvising (in the b.87t validation run the PM's check routed it to the Engineer, and it was later recorded as a deferral).

## Expected behavior

Every piece of work breakdown writes names a role that executes it (the role tag already does this for Subtasks); a record the Epic needs belongs in a role's Subtask or in the Task body, not addressed to the orchestrator.

## Suggested fix

One goal sentence in breakdown's Subtask rules, if the big feature's breakdown shows the pattern again. Evidence: `/tmp/.quorum/b87t-checkpoint-5.md`.

