---
id: b.17n
type: bee
title: Clarify multi-item routing UX under multi-choice AskUserQuestion in deferral-hygiene gates
parent: null
reference_materials: null
created_at: '2026-05-28T19:41:56.089075'
status: done
schema_version: '0.1'
guid: 17nubmybpczmv1w67x98dr8c4go5dicw
---

## Description

The deferral-hygiene gates shipped in b.dgq (commit 63f75cc) present the user with a three-option `AskUserQuestion` — Fix in this session / File as issue tickets / Encode in an existing ticket body — when the `defer-*` active set is non-empty. Skill prose elsewhere notes that the user "may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., 'fix items 1 and 2 now, file 3 as an Issue')."

The mechanism by which the orchestrator accepts per-item routing is the `AskUserQuestion` tool's auto-appended free-text "Chat about this" slot (per CLAUDE.md `## AskUserQuestion usage`: `AskUserQuestion` is multi-choice only and auto-appends `Type something.` and `Chat about this`). When the user picks "Chat about this" and writes "fix items 1 and 2, file item 3", the orchestrator parses that reply and routes per-item. The current skill prose under-explains this — a strict reader of `AskUserQuestion`'s multi-choice-only contract would conclude the user must pick exactly one option for the whole set.

## Current behavior

`skills/quo-execute/SKILL.md` Section 6.5, `skills/quo-fix-issue/SKILL.md` Section 7.5, `skills/quo-plan/SKILL.md` Step 5g, `skills/quo-breakdown-epic/SKILL.md` Section 6.5 — each gate's Step 2 prose mentions the per-item routing as a parenthetical aside, but the actual `AskUserQuestion` mechanism (the auto-appended free-text slot) is not named.

## Expected behavior

Each gate's Step 2 prose names the mechanism explicitly: when the user wants to route different items to different branches, they pick `AskUserQuestion`'s auto-appended "Chat about this" slot and type the per-item routing in free-form (e.g., "fix items 1 and 2, file item 3 as an Issue"). The orchestrator parses the free-text reply and closes out each `defer-*` task per the user's per-item routing.

Optionally — centralize the mechanism note in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract` (since this is a property of every workflow `AskUserQuestion` gate, not just the deferral-hygiene gate) and cross-link from the four gates' Step 2 prose.

## Impact

- **UX clarity.** Users currently have to discover the multi-item routing path empirically (or read past the parenthetical aside). Naming the mechanism explicitly removes the guesswork.
- **Skill prose-honesty.** CLAUDE.md says `AskUserQuestion` is multi-choice only; the parenthetical aside contradicts that without naming the resolution. Closing the gap restores internal consistency.

## Suggested fix

1. Add a sentence to `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract` naming the "Chat about this" auto-slot as the per-item-routing mechanism for multi-item gates.
2. Cross-link from the four gates' Step 2 prose (one-line reference, not duplicated mechanism prose).

## Background and rationale

Caught by external reviewer in a fresh-eyes pass against the b.dgq deferral-hygiene gate. Filed as a follow-up rather than fixed inline because the multi-item routing UX is a property of every workflow `AskUserQuestion` gate (not just the deferral-hygiene one), so the right surface to update is the central contract in `docs/doc-writing-guide.md` plus the four gate references — discrete enough scope to merit a clean commit.
