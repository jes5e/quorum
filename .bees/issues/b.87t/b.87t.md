---
id: b.87t
type: bee
title: Rebuild /quo-execute as a plan-walker whose unit is the Task, each Task run through fix-issue's Phase A/B/C loop; per-Epic boundary review replaces the Bee-level lanes and final sweep
up_dependencies:
- b.37n
parent: null
reference_materials: null
created_at: '2026-09-23T11:35:59.951270'
status: open
schema_version: '0.1'
guid: 87tyy7m2wanqhcxu281y6dugrrzbt5tz
---

## Description

Rebuild `/quo-execute` as a plan-walker whose unit is the Task, with each Task run through `/quo-fix-issue`'s validated per-unit loop (Phase A → B → C). Today's execute per-Task structure differs from fix-issue's in exactly the places with known defects, and it has not run since the orchestrator rewrite; fix-issue's loop has been validated across several runs (b.ot3, b.sao, and the operator's runs through 2026-09-23). Decided with the operator 2026-09-23.

## Current behavior

- **Forward path is unordered.** Every Subtask whose `up_dependencies` are met gets its own implementer, concurrently (§4 phase ladder, "Per-Subtask fan-out"); part (g) ordering applies only to re-dispatch rounds ("The forward per-Subtask fan-out is exempt", §6 Engineer-dispatch precondition). Writers can write against code no review has read. b.5ux records both resulting gaps.
- **Per-Task review runs inside the PM.** No Code Reviewer per Task; the per-Task PM runs `/quo-engineer-review` and `/quo-doc-writer-review` in its own context alongside traceability, and `agents/pm.md` triages a list over ~10 items to blockers only. Tests are reviewed only at Bee level. The PM receives no `## Design decisions for writers` (b.sb7 note, 2026-09-19).
- **One cold implementer per Subtask.** "Never reuse an Agent across scopes" with Subtask scopes means a Task of 4 Engineer Subtasks gets 4 fresh Engineers; b.sao's ledger puts fresh first passes at 159k–245k tokens against 2.7k–58k per resume. b.55r's Task 2 (9 Subtasks) would be 9 cold implementer starts.
- **Review scale.** Dedicated Code, Test, and Doc Reviewer lanes run only at Bee scope, over the whole Bee diff; an Epic-boundary code reviewer fires only when an Epic's files overlap a prior Epic's; one post-completion sweep runs at the end.

## Expected behavior

### Shape

- The walker keeps what only execute does: preconditions, the manifest, Bee and Epic selection, run mode, the step-9 staleness check, per-Task commits, deferral hygiene, the final output and Bee-done gate.
- Each Task runs Phase A → B → C as fix-issue does. **Phase A:** one Engineer named `engineer-<task-id>` receives the Task body plus its Engineer Subtask bodies in dependency order, looped with a dedicated Code Reviewer to clean. **Phase B:** the Test Writer and Doc Writer run once, in parallel, each receiving its own Subtask bodies (more than fix-issue's writers get, which is fine). **Phase C:** Test Reviewer, Doc Reviewer, and a traceability-only PM with the Analyst directive relay as b.37n gives it in fix mode. Spec resolution stays Path A through the Plan Bee.
- `/quo-fix-issue` is **not edited**. Execute's new loop paragraphs are pinned Tier 1 (byte-identical) to fix-issue's in the mirror map, rather than moved into a shared reference, so the working skill carries no rewrite risk and Sections 1–5 stay inside the first 150 lines.

### Defaults

- **Analyst on escalation only** (unchanged since b.vtw B2a): the plan is the approved design; this avoids an `xhigh` dispatch and a gate per Task.
- **Text class for docs-only Tasks:** one Doc Writer plus one Doc Reviewer, as fix-issue's text class runs (breakdown produces such Tasks; b.55r's Task 3 was all doc Subtasks).
- **"Verify the Task" Subtasks** are absorbed by the orchestrator's close-out (Format, Full test when the target repo requires it) and flipped on the implementer's behalf.
- **Context guard at Task boundaries**, not Epic boundaries, for more clean restart points.

### Review: the Epic-boundary review (operator decision 2026-09-23)

Fold the Epic-boundary interaction reviewer and the post-completion sweep into one review at each Epic boundary: a fresh reviewer over that Epic's diff doing the sweep's full cold read of code, tests, and docs, challenging that Epic's compromise-tracker entries, and running the three interaction checks (contract drift, resource compounding, symmetric-change gaps) against earlier Epics' code. It fires on every Epic, not only on file overlap, since Epics interact without sharing files. No final Bee-level sweep and no Bee-level reviewer lanes. Why: smaller diffs review better and cheaper; defects are fixed before later Epics build on them, while that Epic's implementers are still resumable; one mechanism replaces two. Accepted: one review dispatch and one disposition gate per Epic instead of one per run, and no single whole-feature read (every Epic is checked against its predecessors; the acceptance-criteria sign-off at final output covers the whole). For a one-Epic Bee this equals today's single sweep.

### Parallelism

Tasks run one at a time; same-tree concurrency would reintroduce the moving-diff problem the phase ordering exists to prevent. Parallelism inside a Task (Phase B writers, Phase C reviewers) stays. Accepted cost: a 10-Task Bee may take roughly 10–20 hours of wall clock, unattended except for escalation gates; today's cross-Task parallelism has never run. Worktree-per-independent-Task concurrency is a follow-up, sized from the smoke Bee and big-feature ledgers (how many Tasks were actually independent, how long each took); its hard parts are recorded here for that ticket: `.bees/` state committed per worktree with path-based hive registration (flips from the main tree only), README/SDD merge conflicts between concurrent doc lanes, and per-agent working directory and cold build caches.

## Suggested fix

Hand edits plus cold reviews per CLAUDE.md `## Working on the orchestrator skills`, including its enumerate-before-write rule: before the first edit, list every reader of each changed dispatch condition, heading, relay recipient, and manifest field, and name them in the reviewer dispatch. Batches stay small; the cold-review exit rule applies.

Readers known now (extend in the enumeration):

1. `skills/quo-execute/SKILL.md` — §4 (phase ladder), §5 (dispatch table: Code Reviewer, Test Reviewer, Doc Reviewer per Task; PM recipients per b.37n), §6 (Engineer-dispatch precondition collapses to fix-issue's single clause), §7 divergence table (part (g) code-review rung is the Task's Code Reviewer), §8 (Task close-out, Epic-boundary review, guard at Task boundaries), §11 (per-Epic review replaces the Bee-end sweep).
2. `agents/pm.md` — one mode: traceability, scope, and the compromise tracker; the per-Task in-flight review orchestration, its time-budget short-circuit, and the "load-bearing in execute" `[introduces-mechanism]` relay note go.
3. `agents/engineer.md` — execute mode takes a Task's Engineer Subtasks as one assignment (already allowed: "a set of Subtasks in execute mode") and flips each.
4. `agents/test-writer.md`, `agents/doc-writer.md` — their Subtask bodies as the directive; fingerprint set scoped to the Task's Phase A union; the sibling-Subtask concurrency observation paths go.
5. `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md` — dispatched per Task in execute.
6. `skills/quo-execute/references/post-completion-prompt.md` — stays shared with fix-issue; gains an Epic scope and the three interaction checks as parameters rather than a fork.
7. `tests/test_orchestrator_structure.py` — execute anchors; mirror map gains Phase A/B/C as Tier 1; the Tier 2 post-completion pin is rewritten for the per-Epic scope (a planned design change argued here, not a test loosened).
8. `README.md` (execute row; "parallel by construction"), `docs/sdd.md`, `docs/prd.md`, `docs/inventory/` (brief amendment and inventory rows), `CLAUDE.md` repo-layout sentence if role dispatch changes.

## Sequencing

1. Docs-only (text-class) validation run.
2. b.37n (fix-mode PM receives the directive), validated on a small-code `/quo-fix-issue` run.
3. **This ticket.**
4. Validation: one small `/quo-fix-issue` Issue is not needed for this ticket, since fix-issue is untouched; instead, a smoke Bee in a code repo with **at least two Epics** (so the Epic-boundary review fires) and two or three Tasks each, broken down with the current `/quo-breakdown-epic` under `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`. Then the operator's big feature.
5. Then b.sb7 (lands its orchestrator edits once, on the mirrored loop), then b.pcc with this ticket's outputs as inputs.

## Relation to open tickets

- **b.5ux:** closes as moot when this lands; both gaps come from the per-Subtask fan-out this removes.
- **b.37n:** prerequisite; this rewrite mirrors its PM relay into execute's Phase C.
- **b.vtw:** its "Order from here" (b.sb7 → b.pcc → b.7ib → chain validation) is superseded by the sequencing above; record the change there when this starts.
- **b.sb7:** its execute-side edits shrink to the mirrored loop; its 2026-09-19 execute-PM note is addressed here. Decide at b.sb7's start whether its relays mirror both bodies at once.
- **b.pcc:** inputs change — execute consumes Tasks with per-role Subtask bodies; whether the Subtask layer (and its per-level acceptance criteria) earns its cost is b.pcc's question, informed by this rewrite's runs.
- **b.7ib:** unchanged by this ticket; the OpenSpec-as-planning-front-end question discussed 2026-09-23 stays open there.

## Open

- **Per-Task PM vs once per Epic.** Decide after b.37n: measure how often the fix-mode PM's traceability findings lead to a real fix. If rarely, the execute PM runs at the Epic boundary instead, saving one dispatch per Task.
## Order revised (operator decisions 2026-09-24)

This supersedes `## Sequencing` and the b.pcc and b.7ib lines of `## Relation to open tickets`. This ticket runs on the execute track after b.37n, in parallel with the planning track, and the smoke test follows both. The order and the cross-track constraints are on b.vtw's 2026-09-24 note.

- The rules this rewrite adds are recorded as an amendment to `docs/inventory/REWRITE-BRIEF.md` under A2, as the b.vtw batches did.
- It replaces execute's bees query recipes with orientation, since their `'stages:
  - [...]'` form fails when run literally. It also states the Bash etiquette once in the body, as a goal, because the per-site wording that enforces it today goes.
## After b.pcc and b.37n in the serial order (operator decision 2026-09-24)

This ticket now runs after b.pcc and b.37n; the order is on b.vtw's `## Serial order` note. It supersedes the first paragraph of `## Order revised` ("in parallel with the planning track"). It is designed against the Tasks b.pcc produced for the smoke Bee, including the role marker b.pcc chose.

**Validation:** execute the smoke Bee.
## Validation input (2026-09-25)

This rebuild is validated by executing smoke Bee b.v9c in live_edit after b.pcc breaks it down. Epic 1 opens with an in-script-publish probe. Its Azure Managed Redis part runs on the operator's host, so the implementer stops and asks the operator to run it rather than attempting it.

