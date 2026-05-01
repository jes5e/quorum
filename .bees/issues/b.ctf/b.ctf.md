---
id: b.ctf
type: bee
title: bees-execute Epic-discovery prose says 'filter by up_dependencies status' but recipe returns only dep IDs
status: open
created_at: '2026-04-30T21:57:24.752272'
schema_version: '0.1'
egg: null
guid: ctf8vvceewc71um6b668h9hjnzw7x3p3
---

## Description

Surfaced during code review of commit 861e49f (b.tsj fix). The new query recipes in `skills/bees-execute/SKILL.md` ask the agent to filter Epics by their dependencies' statuses, but the recipes only project `up_dependencies` as IDs — leaving the agent to invent the status-lookup step. Same vague-prose anti-pattern b.tsj was filed for, applied here at the *prose-after-the-recipe* level rather than at the recipe level.

## Current behavior

`skills/bees-execute/SKILL.md:53-58` (Bee-ID-given path):

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=ready]
report: [title, up_dependencies]'
```

> Filter the result to Epics whose `up_dependencies` are all in `done` status (a dependency in `ready` state is a pending blocker, not satisfied).

`up_dependencies` (verified against live `bees execute-freeform-query` output) is a list of ticket IDs only. To know each dep's status, the agent needs a follow-up `bees show-ticket --ids <dep-id>` per dependency, or a multi-stage query that traverses the dep set and reports their statuses. Neither is shown in the prose.

The same gap repeats at `skills/bees-execute/SKILL.md:109-114` in `### 2. Find Epic to work on and validate`:

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1]
report: [title, ticket_status, up_dependencies]'
```

> From the result set, the Epic to work on must:
> - Have a status of `ready` or `in_progress`
> - Have all `up_dependencies` in `done` state

Same problem: dep IDs returned, dep statuses not.

## Expected behavior

Either (a) an explicit follow-up step that looks up each blocker's status with a concrete `bees show-ticket` invocation, or (b) a one-shot recipe shape that returns the Epic + its blockers' statuses in one go.

## Impact

**Agent reliability.** The agent will guess. Likely guesses:
- `bees show-ticket --ids <each-dep>` in a loop (works, but unnecessarily chatty if the recipe could batch it).
- Re-run the original query without `status=ready` and inspect everyone (slow on big Bees).
- Skip the dep-status check and just pick a `ready` Epic, hoping its deps are done — silently wrong when an Epic is `ready` but its blockers are still `in_progress` or `drafted`.

The correctness mode (skipping the dep check) is the bad case. An Epic in `ready` state can have unmet upstream blockers; the workflow assumes the team-lead checks before starting work.

## Suggested fix

For each of the two recipes, add a follow-up step. Two reasonable shapes:

**Shape A — explicit batch lookup** (matches existing `bees show-ticket --ids <id1> <id2>` patterns in `bees-fix-issue`):

```bash
# After getting the Epic candidates, batch-look-up their up_dependencies' statuses:
bees show-ticket --ids <dep-id-1> <dep-id-2> <...>
```

Then in prose: \"For each candidate Epic, check the returned `ticket_status` of its dependencies. An Epic is workable only if all its `up_dependencies` are in `done` status.\"

**Shape B — multi-stage recipe** (works in one query):

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=ready]
  - [up_dependencies]
report: [title, ticket_status]'
```

Returns the dependency tickets directly with their statuses. Then the agent maps blockers back to Epics out-of-band — slightly trickier because the result set loses the per-Epic grouping. Probably less ergonomic than Shape A, but worth considering.

Shape A is simpler to read and implement. Recommend Shape A.

## Files to modify

- `skills/bees-execute/SKILL.md:53-58` — add follow-up step to the Bee-ID-given recipe.
- `skills/bees-execute/SKILL.md:109-114` — add follow-up step to the \"Find Epic to work on\" recipe.

## Adjacent (note, do not bundle)

`skills/bees-fix-issue/SKILL.md:90-93` has a similar gap pre-dating these commits:

> Check `up_dependencies` array for any blockers. They must be in a completed state.

…with no lookup procedure. That's pre-existing prose (not part of either commit reviewed here), so it's out of scope for this ticket. If the same fix shape applies cleanly, it could be carried over in the same change — but a separate ticket would be cleaner if the bees-fix-issue context differs.

Out of scope: changing the ticket-discovery query shapes themselves (`[parent=<bee-id>, type=t1, status=ready]`, etc.). Those were verified against the live CLI during the same review and are correct. The issue is only the missing dep-status follow-up step.
