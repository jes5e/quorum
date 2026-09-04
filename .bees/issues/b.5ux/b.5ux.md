---
id: b.5ux
type: bee
title: '/quo-execute ordering gaps after b.pdq: PM in-flight review, test-Subtask fan-out'
parent: null
reference_materials: null
created_at: '2026-09-04T01:58:24.486826'
status: open
schema_version: '0.1'
guid: 5ux8y5jogpfghfbq882dnw54wf13azhx
---

## Description

Issue b.pdq ordered the review-driven re-dispatch path in `/quo-execute` (new part (g) in `### Orchestrator discipline: routing review findings`, with a per-Task clause and a Bee-level clause) but deliberately left the forward per-Subtask fan-out concurrent, because the ticket graph already orders implementation before test/doc Subtasks. Two ordering gaps on that forward path surfaced during b.pdq's review rounds and were recorded as follow-ups rather than built, because each needs a new dispatch precondition or a new ordering rule — a design change to the documented cross-Subtask parallelism property, not a wording fix.

Both sub-findings live in `skills/quo-execute/SKILL.md` Section 3 (the Reconcile step and its Subtask-scoped fingerprint-list rule) and part (g), share one mental model (which Engineers may legitimately run concurrently with which readers of the diff), and are bundled here per house style.

### Sub-finding 1 — the per-Task PM's in-flight `/quo-engineer-review` pass is not ordered after a clean code review

In execute mode the Code Reviewer subagent is dispatched only at the Bee-level review (Section 5). The per-Task code-review surface is the PM's in-flight `/quo-engineer-review` invocation via the `Skill` tool (`agents/pm.md`, review-orchestration bullet). Subagents cannot dispatch subagents, so that review reaches implementers only indirectly through the PM's Final report, and the orchestrator re-dispatches implementers from it under part (g) Clause 1. Nothing orders the PM's review pass itself after the Task's implementation Subtasks have all returned and their code has settled: the PM is dispatched when all Subtasks of the Task are `done`, which is correct for the forward path, but a Clause 1 re-dispatch round (Engineer → PM review → writer) can begin while a sibling Subtask's Engineer for the same Task is still landing edits, so the PM reviews a diff a concurrent round is about to change. This is the same "reviewer reads a moving diff" defect b.pdq fixed for fix mode's Phase A, one level up.

### Sub-finding 2 — a test Subtask with empty `up_dependencies` gets a systematically partial fingerprint set

b.pdq made the parent-Task union the primary source for a Subtask-scoped Test Writer's `## Source paths to fingerprint` list (the union of the `## Files changed` lists from the Engineer returns for the parent Task's implementation Subtasks, narrowed by `up_dependencies` when non-empty). The union covers only Engineer returns the orchestrator holds at dispatch time. A test Subtask with empty `up_dependencies` is legal and is dispatched as soon as the Reconcile loop reaches it, so any same-Task implementation Subtask still in flight contributes nothing — and its later movement in a path it alone touches falls outside the writer's fingerprint set, so the writer neither stops nor reports. The union is therefore systematically partial in exactly the case where it is primary. `skills/quo-execute/SKILL.md` names this limitation but does not close it.

## Current behavior

- Clause 1 orders Engineer → PM review → writer *within* a re-dispatch round, but a forward-path Engineer on a sibling Subtask of the same Task may still be running when that round's PM review reads the diff.
- A Subtask-scoped Test Writer whose test Subtask carries empty `up_dependencies` is dispatched while sibling implementation Subtasks of the same Task may still be in flight; its fingerprint set omits their paths.

## Expected behavior

- The per-Task PM's `/quo-engineer-review` pass runs only after every implementation Subtask of that Task has returned (forward path) and after any Clause 1 Engineer re-dispatch for that Task has returned (re-dispatch path) — the PM never reviews a diff an in-flight same-Task Engineer can still change.
- A Subtask-scoped Test Writer is not dispatched while any `engineer-<subtask-id>` task for a sibling Subtask of the same parent Task is `pending` or `in_progress`, so the parent-Task union it receives is complete. Cross-Task concurrency (Engineer on Task N+1 alongside Test Writer on Task N) stays untouched — that is the documented parallelism property.

## Impact

Correctness of the review and fingerprint guarantees b.pdq introduced, in execute mode only. Today both gaps fail safe (a stale PM review costs a round; a missed movement is caught at the Bee-level review), so this is round-count and reviewer-trust, not data loss.

## Suggested fix

1. `skills/quo-execute/SKILL.md` Section 3 Reconcile step, forward per-Subtask fan-out: add a dispatch precondition on the Test Writer lane only — do not dispatch `test-writer-<subtask-id>` while any TaskList task whose name begins with `engineer-<sibling-subtask-id>` for a Subtask of the same parent Task is `pending` or `in_progress` (name prefix + status, matching part (g)'s style; carry over the stranded-`pending` clause so a `pending` task with no dispatch behind it is dispatched or cleared rather than waited on). Resolve "same parent Task" via `bees show-ticket --ids <subtask-id>` reading `parent`. Release when the sibling Engineer's task goes `completed`. State explicitly that this precondition is exempt from part (g)'s "review re-dispatch path only" scope limit, and amend that scope-limit sentence to name the exemption.
2. Same section, per-Task PM dispatch (Section 4.1): add the analogous precondition — do not dispatch `pm-<task-id>` while any `engineer-<subtask-id>` for a Subtask of that Task is `pending` or `in_progress` — and reference it from part (g) Clause 1 so a re-dispatch round's PM review waits for every same-Task Engineer, not only the one the round dispatched.
3. Update the TaskList naming-convention prose and Section 4.1's close-out sweep if either precondition needs a new name form (it should not — both key on existing `engineer-<subtask-id>` / `pm-<task-id>` names).
4. Mirror the two limitation notes b.pdq left in the fingerprint-list bullet (~"the union covers only Engineer returns the orchestrator holds at dispatch time") into statements that the precondition now makes the union complete for same-Task siblings.
5. Docs: `docs/sdd.md` `## Orchestration in execution skills` "Cold dispatch for all roles" bullet and the b.pdq `### Feature:` entry's "Why the `/quo-execute` mirror is deliberately narrow" paragraph must be re-qualified (the forward fan-out stays concurrent across Tasks and across implementation Subtasks; only the Test Writer lane and the per-Task PM now wait for same-Task Engineers). `README.md` "Parallel by construction" line may need a clause. Tests: extend `tests/test_review_lane_ordering_contract.py` (precondition presence, prefix + status matching) — note that its `EXPECTED_PRECONDITIONS = 3` non-vacuity floor counts `MUST NOT dispatch … Engineer` precondition lines per orchestrator and must be raised to match the new preconditions or the test fails — and `tests/test_tasklist_name_class_closeout.py` if any name form changes.

## Background and rationale

Sub-finding 1 was recorded by the Analyst at b.pdq's design gate as a genuine open question distinct from that Issue's defect (`### Deferred refinements`, destination new Issue). Sub-finding 2 was found by the Code Reviewer during b.pdq (round 6) as a second-order effect of the parent-Task union rule; the reviewer sketched fix 1 as a `[new-machinery]` path and the orchestrator deferred it under the run's convergence rule (a finding whose fix introduces a new state, name class, gate, marker, close-out or precondition is a design change to file, not build).

## Decisions and rejected alternatives

- Building the Test Writer precondition inside b.pdq was rejected: b.pdq's approved directive kept the forward fan-out concurrent because the ticket graph already orders implementation before tests; adding a precondition there is a change to that documented property and belongs in its own review.
- Ordering the whole per-Subtask fan-out (b.pdq's original item 4, read literally) was rejected in b.pdq and stays rejected here: cross-Task concurrency is a designed throughput property. The preconditions above are Task-scoped and touch only the two lanes that read a same-Task diff.
- Making the working-tree `git diff --name-only HEAD` derivation primary (so the fingerprint set is always complete) was rejected: in execute mode that derivation sweeps sibling-Task edits into the set and makes the writer stop on legitimate concurrency.

