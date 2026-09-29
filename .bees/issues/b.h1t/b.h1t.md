---
id: b.h1t
type: bee
title: '/quo-execute follow-ups from the b.v9c run: deferrals aimed at a later Task, target-repo obligations, committing the Epic done flip'
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:49.078507'
status: open
schema_version: '0.1'
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
## Item 4 (2026-09-27): trim the per-Task PM to its cross-Task role?

The b.v9c PM record (`~/.quorum-scratch/pm-findings-b.v9c.md`; b.87t's correction note) shows the per-Task PM's distinctive value was cross-Task: constraints written into later Tasks' tickets before they ran. Of 15 PM findings in Tasks 1–5, 5 duplicated another reviewer, 6 partly overlapped, and 4 were PM-only (2 substantive). On the big feature, record the PM's findings verbatim again and decide whether its per-Task scope can shrink to cross-Task and spec-traceability checks the dedicated reviewers don't make.
## Item 5 (2026-09-27): a premise-check return that carries a design change

In b.v9c Task 2 the Analyst's premise-check return held a revision-shaped body (Recommended approach, Blast radius, Decisions for writers, Deferred refinements), and the orchestrator appended it to the Task ticket under `## Design revision (Analyst)`. The premise-check contract has no place for a design change a `premise-holds` finding needs, beyond `### Blast radius` entries. One occurrence; the agent recovered unaided. Decide against the big feature's run: either the contract says a `premise-holds` finding that needs a design change goes through the Analyst gate as a revision, or nothing.

## Evidence from the big feature so far (b.y3m Epic 1, Tasks 1–4; 2026-09-29)

- **Item 1, second run:** deferrals aimed at later Tasks (5, 6, 8) were encoded into those Tasks' tickets before they ran, at the guard stop and at the operator's stop after Task 4. The agent was unprompted each time.
- **Item 2, heavily:** improvised manifest fields throughout. They include held findings per lane, a Blast-radius carrier, per-Task notes, "deletions owed at run end" (including a `/tmp/.quorum` file, per live_edit's convention), a Task 7 risk, and the commits made. Breakdown runs did the same (`## Operator decisions`, `## Decider standing context`).
- **Item 5, second occurrence:** in Task 3, PM finding F2's `premise-holds` return carried a mechanism change (a second connection for a pre-read). It was applied through row 6 without a gate, and the Blast radius was amended with it.

## Item 6 (2026-09-29): a proposal file for execute's Analyst gate

Execute keeps the Analyst's revision only in the conversation until Approve appends it to the ticket; fix-issue writes it to a `**Proposal:**` file. A file would let a delegated gate (b.d7t) name the full return by path instead of copying it. It would also carry `### Deferred refinements` across a compaction, which would let execute drop its §3 Analyst re-derive exception.
- Evidence: one paraphrased Analyst gate (b.y3m Task 3: a summary naming the proposal's rules inconsistently).
- Decide with the other items after the big feature.

The b.87t validation report cited above (`/tmp/.quorum/b87t-checkpoint-5.md`) was lost in a macOS restart on 2026-09-28. A copy is kept at `~/.quorum-overseer/precedent-b87t-checkpoint-5.md`.

