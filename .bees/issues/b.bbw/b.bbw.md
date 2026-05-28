---
id: b.bbw
type: bee
title: Children-cascade Keep-branch leaves dangling up_dependencies on kept Epic's child Tasks
parent: null
reference_materials: null
created_at: '2026-05-28T19:41:57.096663'
status: done
schema_version: '0.1'
guid: bbw7wj8c1cpcszm6ahoz54fs1ibdurss
---

## Description

The children-cascade guard shipped in b.9q3 (commit 3896b01) added a three-choice `AskUserQuestion` gate at `skills/quo-plan/SKILL.md` Step 5d-i: when reuse-mode reconcile would `bees delete-ticket --ids <epic-id>` an Epic whose `children` array is non-empty, the user picks `Delete Epic and N child Task(s)` / `Keep Epic in decomposition` / `Cancel reconcile`.

The `Keep Epic in decomposition` branch adds the Epic back to the approved post-reconcile Epic list and skips the delete. But the kept Epic's child Task(s) may carry `up_dependencies` referencing sibling Epics that **are** being deleted in the same reconcile pass. The Keep-branch prose does not address dangling-dependency pruning — after the reconcile completes, the kept Epic's children may reference Epic IDs that no longer exist.

## Current behavior

`skills/quo-plan/SKILL.md` Step 5d-i's Keep-branch prose: "On `Keep Epic in decomposition`, add the Epic back to the approved post-reconcile Epic list and skip the delete — the rest of 5d-i's wiring (and the dependency-wiring pass below) runs against the updated list."

The dependency-wiring pass at the end of 5d-i analyzes blocking relationships and sets `up_dependencies` between Epics in the approved list. But the children-of-kept-Epics path is not re-analyzed — the children (Task tickets) keep whatever `up_dependencies` they had before the reconcile, including references to siblings that are now deleted.

## Expected behavior

When the Keep-branch fires, the orchestrator (in addition to adding the Epic back to the approved list) walks the kept Epic's `children` array and, for each child Task, removes any `up_dependencies` entries that reference Epics not in the post-reconcile approved list. The Task's other `up_dependencies` (referencing surviving Epics or other Tasks) are preserved.

Pruning happens once per Keep-branch fire, after the user confirms but before the rest of 5d-i's wiring runs. The post-reconcile state has no dangling-dependency references.

## Impact

- **Workflow correctness.** Downstream skills (`/quo-execute`'s blocked-on-dependency check, `/quo-breakdown-epic`'s up-dependency walk) may stumble on Task tickets whose `up_dependencies` reference deleted Epic IDs.
- **bees CLI behavior.** `bees show-ticket --ids <task-id>` on a Task with a dangling `up_dependencies` entry returns the entry as-is; whether downstream `bees execute-freeform-query` operations handle the missing target gracefully or surface an error is implementation-dependent.
- **User-surface.** A user who picks Keep expecting "the Epic survives intact" finds the Epic survives but its children carry references to ghosts.

## Suggested fix

Update `skills/quo-plan/SKILL.md` Step 5d-i's Keep-branch prose to add a pruning sub-step:

> On `Keep Epic in decomposition`, add the Epic back to the approved post-reconcile Epic list and skip the delete. **Then walk the kept Epic's `children` array and prune any `up_dependencies` entries referencing Epics that are not in the post-reconcile approved list.** The dependency-wiring pass below runs against the updated list.

The pruning is straightforward — for each child Task in the kept Epic's `children`:
1. `bees show-ticket --ids <task-id>` (the orchestrator may already have this from earlier 5b fetches; reuse if so)
2. Compute `pruned_deps = [d for d in task.up_dependencies if d in approved_epic_ids]`
3. If `pruned_deps != task.up_dependencies`, write `bees update-ticket --ids <task-id> --up-dependencies <pruned_deps>` (or whatever the bees CLI verb is for replacing dependency arrays)

Paired POSIX + PowerShell snippets needed for the bees CLI invocations.

## Background and rationale

Caught by external reviewer in a fresh-eyes pass against b.9q3. Filed as a follow-up rather than fixed inline because the pruning logic is small but non-trivial (touches the bees CLI's dependency-array verb, which may need verification), and the Keep-branch is rare enough that the dangling-deps surface has likely not yet manifested in practice.

## Decisions and rejected alternatives

- **Surface a warning instead of pruning.** Rejected — the user already opted-in to the Keep via `AskUserQuestion`; surfacing another prompt for the pruning would be UX noise. Silent pruning matches the user's intent ("keep this Epic intact in the post-reconcile state").
- **Skip Task-level pruning; only update Epic-level dependencies.** Rejected — Tasks are the unit that downstream skills query; leaving them dangling defeats the rest of the fix.
