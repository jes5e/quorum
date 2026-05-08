---
id: b.61t
type: bee
title: Orchestrator self-tracking TaskList tasks left in_progress when yielding to user
parent: null
reference_materials: null
created_at: '2026-05-07T16:30:16.193880'
status: done
schema_version: '0.1'
guid: 61tqu98or3wgn3efrfi5y9wvpe87qd3r
---

## Description

Orchestrator skills (`/quo-execute`, `/quo-fix-issue`, the standalone review skills, and likely others) frequently leave their **own self-tracking TaskList tasks** in `in_progress` state when they yield control back to the user — either at end-of-flow or at a question-the-user pause. The Claude Code UI then displays e.g. `9 tasks (8 done, 1 in progress, 0 open)` with an active orange indicator next to the trailing task ("Synthesize findings"), making it look like work is still ongoing when the orchestrator has actually stopped responding.

This is a sibling-bug to `b.4km`, not a duplicate. `b.4km` is scoped to **dispatched-Agent** TaskList tasks (issue-scoped naming convention `<role>-<issue-id>`) in `/quo-fix-issue` Section 7 step 6's "Fix in this session" branch. The bug here is about **the orchestrator's own self-managed tasks** — work units the orchestrator creates ad-hoc to track its synthesis steps (e.g., "Get diff scope", "Verify b.tak", "Synthesize findings") — which are not Agent dispatches and don't follow b.4km's naming convention. Both bugs share the close-out-discipline theme but live in different skill-prose surfaces and need different fixes.

Two recurring instances captured in screenshots provided with this filing:

1. End-of-flow: `/quo-fix-issue` post-completion review finishes, the final commit message is shown, the orchestrator prints its closing summary — and the trailing "Synthesize findings" task stays `in_progress` indefinitely.
2. Question-the-user pause: a code-review session ends with "Want me to file the bundle (or extend b.tak)?" and the orchestrator yields the turn — but "Synthesize findings" is still `in_progress` while waiting on the user's reply.

In both cases the work is genuinely done; only the progress-UI bookkeeping is wrong.

## Current behavior

The orchestrator naturally uses TaskCreate to break the post-completion review (and similar synthesis flows) into discrete tracked steps — e.g., "Get diff scope", per-ticket "Verify <id>" tasks, and a final "Synthesize findings" task. No skill prose tells it to do this; it emerges from Claude's general TaskCreate habit. As each step starts, the orchestrator marks the corresponding task `in_progress`; as each step completes, it marks the task `completed`. The pattern works fine for the early steps.

The trailing "Synthesize findings" task is the failure mode: the orchestrator marks it `in_progress` while drafting the synthesized findings, then outputs the final user-facing summary (or yields with a question) and stops responding — without flipping the task to `completed`. Because no skill prose anchors close-out for orchestrator self-managed tasks, the omission is invisible to a careful reader of the skills.

Greping the affected skills confirms the gap:

- `skills/quo-execute/SKILL.md` Section 6 ("Post-Completion Review") and `skills/quo-fix-issue/SKILL.md` Section 7 ("Post-Completion Review") describe a "Synthesize the findings" step (step 3 in each) but say nothing about TaskList progress for that synthesis step.
- The standalone review skills (`bees-code-review`, `bees-test-review`, `bees-doc-review`, `quo-spec-review`) contain no `TaskList` / `TaskCreate` / "Synthesize findings" prose at all — yet the second screenshot's "Synthesize findings" task appears at the end of one of these review flows.

## Expected behavior

Before the orchestrator yields control to the user — at end-of-flow OR at a question-the-user pause — every TaskList task it created for self-tracking should be in `completed` state. The UI should consistently read `X tasks (X done, 0 in progress, 0 open)` whenever the orchestrator has stopped responding, so the in_progress indicator is a reliable signal that work is genuinely ongoing.

## Impact

User-visible UX bug. The user has to mentally distinguish "agent still running" (real in-flight work) from "agent is done but forgot to close out its task list" (stale UI state). For interactive sessions this is small but annoying; for sessions where the user steps away and comes back, the stale state is confusing — they may wait unnecessarily, or interrupt thinking the agent is hung. Erodes trust in the TaskList progress indicator.

No correctness impact — the work itself completes; only the progress-UI bookkeeping is wrong. Same severity profile as `b.4km`, different surface area.

## Suggested fix

Add explicit close-out discipline for orchestrator self-managed TaskList tasks at every yield-point. Candidate edit sites:

1. `skills/quo-execute/SKILL.md` Section 6 ("Post-Completion Review") — at the end of step 3 ("Synthesize the findings before presenting") and again at step 4 / step 5 (the user-facing yield), add an explicit "mark all orchestrator self-tracking TaskList tasks `completed` before yielding" instruction.
2. `skills/quo-fix-issue/SKILL.md` Section 7 ("Post-Completion Review") — same edit at step 3 / step 4 / step 5. Coordinate with `b.4km`'s Section 7 step 6 fix so the two fixes don't step on each other; the close-out discipline added here is for orchestrator self-tracking tasks, while `b.4km`'s fix is for dispatched follow-up Agent tasks.
3. `skills/bees-code-review/SKILL.md`, `skills/bees-test-review/SKILL.md`, `skills/bees-doc-review/SKILL.md`, `skills/quo-spec-review/SKILL.md` — when invoked standalone, these skills produce the same self-tracking task pattern (the second screenshot is from one of these flows). Add a short close-out paragraph somewhere in the user-facing presentation step of each.
4. Optionally consider a single cross-cutting prose block (in a shared location like `agents/`-level guidance, or a top-of-skill convention paragraph) rather than four near-identical edits — but per the project's three design rules and the existing per-skill structure, repeating the discipline at each affected site is acceptable and probably clearer.

The fix is purely additive prose — no changes to skill structure, dispatch shapes, or task-naming conventions. Concretely, each edit should mirror the wording style of `quo-fix-issue` Section 6 step 3's per-issue close-out paragraph, retargeted to the orchestrator's own self-tracking tasks rather than per-issue dispatched tasks.

Out of scope:

- `b.4km`'s fix at `quo-fix-issue` Section 7 step 6 — that lives in its own ticket and covers a different surface (dispatched follow-up Agents, not orchestrator self-tracking). Whoever picks up either ticket should read the other's body to keep the two fixes coherent.
- No change to the TaskCreate / TaskUpdate tools themselves; the bug is skill-prose discipline, not tool behavior.
