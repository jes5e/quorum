---
id: b.m7f
type: bee
title: Surface a one-time Mode 1 (stop per Epic) vs Mode 2 (work through all) choice at start of /quo-breakdown-epic and /quo-execute runs
status: open
created_at: '2026-05-08T20:44:46.070740'
schema_version: '0.1'
reference_materials: null
guid: m7fj9eppze2kymd37spq84t5tnkqi3x9
---

## Description
When `/quo-breakdown-epic` or `/quo-execute` runs against a Bee with more than one Epic, the skill should surface a one-time mode choice at the start of the run instead of re-prompting at every Epic boundary.

## Current behavior
- `/quo-breakdown-epic` (skills/quo-breakdown-epic/SKILL.md, Section 7 — lines ~540–593): after each Epic is broken down, an `AskUserQuestion` menu (~6 options) asks the user how to proceed.
- `/quo-execute` (skills/quo-execute/SKILL.md, Section 4.2 branch 2 — line ~400): when a workable Epic remains and no drafted Epics exist, the user is asked "if they want to continue with the next logical one."
- Both default to a per-Epic confirmation. There is no first-class way to opt into a batch run; the only override today is per-user memory (e.g., the user's existing "Auto-chain breakdown across Epics" / "bees-execute auto-continue across Epics" entries), which is undiscoverable to anyone else and forces a single answer across all sessions.

## Expected behavior
At the start of the run, when more than one Epic is in scope, present a single `AskUserQuestion` with two named modes:

- **Mode 1 — Stop after each Epic.** Today's per-Epic confirmation: pause at each Epic boundary to let the user review and approve continuation. (`/quo-breakdown-epic` keeps Section 7's full six-option menu; `/quo-execute` keeps Section 4.2 branch 2's "continue?" prompt.)
- **Mode 2 — Work through all Epics.** Auto-continue across Epics; only stop when there's an important reason — i.e., proceeding without user feedback would actively make things worse. The set of important reasons is the same set the skills already enumerate; Mode 2 does not weaken those. Specifically, Mode 2 still stops on:
  - Section 4.2 branch 1's drafted-or-blocked-on-drafted Epic stop in `/quo-execute`.
  - Section 7's drafted-siblings-with-reshape-risk case in `/quo-breakdown-epic` (the "execute this Epic first; defer downstream breakdown" recommendation) — that's a contract-stability concern, not a discretionary check-in.
  - Final Bee-level reviewer findings flagged as blockers.
  - Any other genuine red flag the orchestrator surfaces today.

The choice is made once, up front, and applies to the rest of the run.

## Impact
- **Discoverability.** Today's batch path is undocumented and only reachable via memory hacks. New users always get the slow per-Epic walk with no signal that a batch mode exists.
- **Consistency.** Two skills, two slightly different inter-Epic prompts. A shared two-mode vocabulary gives users one concept across both.
- **Per-session control.** Memory-based overrides commit a user to one behavior across all sessions. An up-front choice lets the user pick per-run — slow walk for unfamiliar Bees, batch for familiar ones.

## Suggested fix
- **`/quo-breakdown-epic`** (skills/quo-breakdown-epic/SKILL.md): add a new step early in the flow (after the parent Bee is resolved and before the first Epic is broken down) that fires only when more than one Epic remains under the Bee. Use `AskUserQuestion` with the two finite mode options. In Section 7's next-Epic-loop, branch on the choice: Mode 1 keeps today's six-option menu verbatim; Mode 2 auto-selects "break down the next Epic in this session" — except when Section 7's `Pick the Recommended option` logic identifies the reshape-risk case, which still pauses for the user (that's an "important reason to stop" per Mode 2's contract).
- **`/quo-execute`** (skills/quo-execute/SKILL.md): same shape — gate at the start of the run when more than one Epic is in scope. In Section 4.2 branch 2, branch on the choice: Mode 1 keeps today's "do you want to continue?" prompt; Mode 2 auto-continues to the next workable Epic (still respecting branch 1's drafted-Epic stop, the Epic-boundary context-clear discipline, and reviewer-surfaced blockers).
- Use identical option labels across both skills so the user sees one concept.
- Update README.md's skill table rows for `/quo-breakdown-epic` and `/quo-execute` to mention the two-mode choice.

## Background and rationale
This issue is a refinement of an existing pattern: the user has been overriding the default per-Epic prompt via personal memory entries ("Auto-chain breakdown across Epics in /quo-breakdown-epic", "bees-execute auto-continue across Epics") for some time. The behavior the user wants exists; the gap is that it's only reachable via memory and isn't a first-class user-facing affordance. Surfacing it as an explicit mode choice solves the discoverability and per-session-control problems without changing the underlying loop behavior of either skill.

The "important reason to stop" qualifier is load-bearing: Mode 2 is not "skip every interactive prompt" — it's "skip discretionary continue-or-not prompts; preserve every prompt where proceeding without user input would risk concrete downstream cost (stale Tasks, broken Epics, missed contract reshape)."

