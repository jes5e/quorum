---
id: b.h1t
type: bee
title: '/quo-execute follow-ups from the b.v9c run: deferrals aimed at a later Task, target-repo obligations, committing the Epic done flip'
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:49.078507'
status: done
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

## Decisions (operator, 2026-09-29)

Decided on the b.y3m evidence (Tasks 1–6 PM record, Tasks 1–4 run). Report: `~/.quorum-overseer/b-y3m-report.md`; PM analysis: `~/.quorum-overseer/b-y3m-pm-analysis.md`.
1. **Build:** one goal sentence in execute's deferral hygiene: encode a deferral whose destination is a later Task before that Task starts. Evidence: b.v9c ×3 and b.y3m, always handled unaided. But b.y3m Task 3's PM caught a hand-off planned for the Epic boundary as too late: a near-miss, and silent if missed.
2. **No change.** The improvised manifest fields for target-repo obligations are continuous, visible, and handled unaided.
3. **No change; watch.** Committing the Epic `done` flip was seen once (b.v9c) and handled unaided; b.y3m reached no Epic end.
4. **Keep the per-Task PM as is.** Of 40 findings, 6 duplicated another lane (all own-diff checks), and 16 were PM-only substantive (13 cross-Task, 3 spec/contract traceability, including the run's highest-consequence finding). All 17 hand-offs were written into later tickets before those Tasks ran. The PM costs about 9% of tokens.
5. **No change.** A premise-holds return carried a mechanism change twice, both harmless, through the Blast-radius channel.
6. **Build:** give execute's Analyst gate a proposal file, like fix-issue's `**Proposal:**`, and delete execute's §3 re-derive exception.

Items 1 and 6 form one small execute batch, next in the serial order before the docs change (b.sb7, small version). Close this ticket when that batch lands.

## Item 6 (2026-09-29): a proposal file for execute's Analyst gate

Execute keeps the Analyst's revision only in the conversation until Approve appends it to the ticket; fix-issue writes it to a `**Proposal:**` file. A file would let a delegated gate (b.d7t) name the full return by path instead of copying it. It would also carry `### Deferred refinements` across a compaction, which would let execute drop its §3 Analyst re-derive exception.
- Evidence: one paraphrased Analyst gate (b.y3m Task 3: a summary naming the proposal's rules inconsistently).
- Decide with the other items after the big feature.

The b.87t validation report cited above (`/tmp/.quorum/b87t-checkpoint-5.md`) was lost in a macOS restart on 2026-09-28. A copy is kept at `~/.quorum-overseer/precedent-b87t-checkpoint-5.md`.

## Item 5 revisited (operator, 2026-09-29): build

A third occurrence came from a live_edit `/quo-fix-issue` run on 2026-09-29. A premise check on stage-2 code-review findings silently changed two statements the decider had approved in the Issue's Revision 1: a waiting viewer is now cut off at about 240 edits/s rather than the approved 735, and a new exception was added to the refusal-after-data rule. The run later called this "arguably the wrong call". Three questions: 3 times; silent to the approver; not recovered unaided (the operator had to ask). The decision changes from "no change" to "build", in this batch.

## Closed (2026-09-29)

Merged to main by fast-forward, head `a7de6c4` (from `9bf86ea`), not pushed. Items 1, 5, and 6 were built; items 2, 3, and 4 are decided "no change" (above), and item 3 is watched.
- **Item 1:** execute's deferral hygiene also fires before a Task starts when an open `defer-*` obligation's destination is that Task or one of its Subtasks. `## Obligations` detail stays informational except for that destination.
- **Item 5:** a premise-check return that changes what the approved design states carries a whole Design Proposal and its `Analyst verdict:` trailer. §7 (Tier 1, both bodies) sends it through the Analyst gate before any finding routes, and a Revise there re-sends the `## Premise check`. §4's "no gate fires on it" is deleted in both bodies; `agents/analyst.md` `## Premise-check dispatch` carries the contract.
- **Item 6:** execute's Analyst gate writes the return to a `**Proposal:**` file, reusing fix-issue's mechanism verbatim. It is cleared at each Task's close-out and at the Epic boundary. Execute's §3 re-derive exception and the b.d7t amendment's exception are deleted, and a delegated gate names the proposal by path.
- **Size:** execute +134, fix-issue +41, analyst +57, rationale −19 words.
- **Review:** cold round 1 found a blocker (the verdict trigger "ending in" could never fire past `### Deferred refinements`) and a Revise-shape gap between the two bodies. Both were fixed; round 2 was clean.
- **Validation:** none dedicated. The next real `/quo-execute` run is the check (item 1 is likely at the big feature's resume), and items 5 and 6 are checked in any run where an Analyst gate or a design-changing premise return occurs. Checkpoints: `~/.quorum-overseer/bh1t-checkpoint-{1,2,3}.md`.
