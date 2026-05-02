---
id: b.hf8
type: bee
title: 'bees-execute team-lead/dispatcher: state-aware dispatch, verbatim ticket-body quoting, blocked_on signal'
parent: null
egg: null
created_at: '2026-05-02T13:36:22.499525'
status: done
schema_version: '0.1'
guid: hf8vkbf6at3ztvq9k5pjd9y42kq9ptc8
---

## Description

A user running `bees-execute` on another project reported three related defects in the team-lead / dispatcher loop. All three share a root cause: the dispatcher does not consult current ticket state at dispatch time, so it sends `task_assignment` messages based on stale or fabricated information.

## Sub-findings

### A1. Duplicate `task_assignment` for already-done tickets

The team-lead re-dispatched `task_assignment` messages for three Tasks (`.vt`, `.12`, `.g1`) after the engineer had already marked them done in both `TaskList` and bees. Three wasted round-trips in a single run.

### A2. Spec drift between assignment body and ticket body

The `.12` and `.g1` `task_assignment` messages referenced `record_hydration(...)` while the bees ticket bodies said `record_hydrate(...)`. Whoever generates the assignment body is paraphrasing the spec instead of quoting it — silently corrupting identifier names that the engineer then uses verbatim.

### A3. No "engineer is idle, here's why" signal

When the engineer is blocked on test-writer + team-lead, there is no protocol to surface the block proactively. The user had to send an ad-hoc message to unblock the loop. A status mechanism — e.g., `TaskUpdate` with a `blocked_on` field surfaced in the team-lead's view — would be cleaner than ad-hoc messages.

## Current behavior

- Dispatch loop emits `task_assignment` without checking ticket status or assignee at send time.
- Assignment bodies regenerate a summary of the ticket instead of quoting the canonical body.
- Idle / blocked engineers have no first-class way to surface "blocked on X"; the team-lead has no signal to act on.

## Expected behavior

- Before sending a `task_assignment`, the team-lead queries the ticket's current status (recipe in `docs/doc-writing-guide.md` `## Querying tickets`) and skips dispatch if `status=done` or the assignee already matches the intended recipient.
- The assignment message quotes the ticket body verbatim (or links to it) rather than paraphrasing.
- An engineer that is blocked surfaces a `blocked_on` signal that the team-lead's loop reads and acts on (e.g., dispatches the unblocker first, or surfaces the block to the human).

## Impact

- Wastes turns on round-trips that contribute nothing.
- Silent identifier drift can cause the engineer to call non-existent functions; the bug surfaces only at compile / test time.
- No idle-state protocol leads to ad-hoc human intervention to break deadlocks.

## Suggested fix

Edit `skills/bees-execute/SKILL.md` (team-lead role and dispatcher prose):

1. Add a pre-dispatch status check using `bees execute-freeform-query` — skip if `status=done` or `assignee` already matches the recipient.
2. Change assignment-body authoring to quote the ticket body verbatim instead of summarising. Cheapest shape: read the ticket via bees and embed the body block.
3. Define a `blocked_on` field convention on `TaskUpdate` (or a sibling message type) and add a team-lead step that reads it each tick and either dispatches the unblocker or surfaces the block to the human.

`skills/bees-fix-issue/SKILL.md` likely shares the same dispatcher prose and would need a parallel edit.

## Severity

Medium — wastes turns and corrupts identifier names in flight, but does not corrupt persisted state.
