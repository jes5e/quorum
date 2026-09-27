---
id: b.h1t
type: bee
title: '/quo-execute follow-ups from the b.v9c run: deferrals aimed at a later Task, target-repo obligations, committing the Epic done flip'
status: open
created_at: '2026-09-27T14:04:49.078507'
schema_version: '0.1'
reference_materials: null
guid: h1tof2fim5dae25jzrn3kygn2ppy1vee
---

## Description

Three `/quo-execute` gaps from the b.87t validation run (live_edit b.v9c Epic 1). The agent handled each correctly without a rule, so decide them against the big feature's run rather than now.

## Items

1. **A deferral aimed at a later Task in the same Epic.** Deferral hygiene fires at the Epic boundary or an exit, which is too late for an item whose destination is a Task that hasn't run yet. The agent encoded such items mid-Epic three times (`fa6ebced`, `89871372`, `beede20d`). Three questions: 3 times; silent if missed; recovered unaided. Candidate: one goal sentence (encode it before that Task starts), or nothing.
2. **Obligations the target repo imposes.** The run improvised manifest fields for them (Epic completion notes a Subtask asked "the orchestrator" to record; live_edit's end-of-run scratch-deletion convention) and carried them into the resumed session. Continuous; visible; recovered unaided. Decide deliberately: a manifest section that survives a resume, or routing such obligations to tickets (the agent did the latter once, `defer-19`).
3. **Committing the Epic (and Bee) `done` flip.** The flip changes an in-repo ticket file after the last Task commit; the agent committed it separately (`026a4b59`). Every Epic; leaves a dirty tree if missed; recovered unaided. Candidate: one clause in the Epic-boundary step (commit the flip with the Plans-hive path), or fold it into the hygiene commit.

## Sequencing

Decide after the operator's big feature, using its run. Evidence: `/tmp/.quorum/b87t-checkpoint-5.md` triage items 1, 3, and 5.

