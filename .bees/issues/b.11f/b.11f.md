---
id: b.11f
type: bee
title: PM agents idle mid-Task; bees-execute lacks team-lead orchestration
parent: null
egg: null
created_at: '2026-05-01T16:43:22.774627'
status: open
schema_version: '0.1'
guid: 11fjce8bzcmgamir65uoqfxf1r7mmtm3
---

## Description

bees-execute SKILL.md describes each team role (Engineer, Test Writer, Doc Writer, Product Manager) as a job description (responsibilities + instructions) but never prescribes the message-flow choreography between them. The team-lead is left to improvise spawn prompts and inter-phase pings. Combined with Agent Teams' message-driven model — agents only run when they receive a message — any teammate that finishes processing one ping without a follow-up trigger idles silently, even when all preconditions for its next phase are met.

Verified by reading skills/bees-execute/SKILL.md end-to-end: zero occurrences of SendMessage / notify / ping anywhere in the file. Two independent runtime analyses both described prescribed messaging that does not exist in the SKILL.md (one claimed an Engineer→PM ping, one claimed a Step 1…Step 7 PM prompt structure). Both descriptions were of team-lead runtime improvisation, not of the SKILL.md itself.

## Current behavior

Two distinct stall patterns observed in real bees-execute runs, both with the same root cause:

**Pattern A — PM idle after subtasks complete.** PM stays silent after Engineer + Test Writer finish, even with all subtasks at status=done. Only advances after a human "are you stuck?" prompt. The PM had everything it needed to start Step 5 reviews.

**Pattern B — Test Writer idle after Engineer completes.** Test Writer is spawned, processes its initial framing, sits waiting for Engineer to finish, and never wakes up when the Engineer reports done. Observed on EVERY Task across a 4-Epic run (Task 1 of Epic 1, Task 2 of Epic 1, single Task of Epic 2 — three for three). Each time the team-lead had to be prompted by the user to notice and ping.

Both patterns trace to the same gap: skills/bees-execute/SKILL.md Section 3 ("Form Team to Execute Tasks") and Section 4 ("Per-Task and Per-Epic Cleanup") describe roles but not the inter-agent message flow. The PM Instructions block (lines ~286-329) and the Engineer / Test Writer Instructions blocks (lines ~243-271) list responsibilities but no "you are unblocked when condition Y holds, start now" triggers.

Why this is structurally a problem in Agent Teams: there is no "teammate idle" event. Teammates that finish processing input and send no reply simply stop. The team-lead has no notification signal — it must proactively manage advancement, but the SKILL.md never tells it to.

**Sibling skill comparison.** skills/bees-fix-issue/SKILL.md has a partial mitigation at lines 249-254 — an idle-handling escalation ladder ("first nudge ~10 min, second nudge, escalate, proceed and log") that tells the team-lead what to do when a teammate has gone silent. This is reactive, not proactive — it kicks in after stuckness is observed. bees-execute has no equivalent. Neither skill prescribes proactive choreography (when the team-lead should ping which agent in response to which subtask transition).

## Expected behavior

Per skills/bees-execute/SKILL.md the team-lead should reliably advance every teammate through its phases without requiring human nudges:
- Engineer reports done → Test Writer is pinged to start Phase A
- Test Writer reports Phase A done → PM is pinged to review the per-subtask diff
- All subtasks at status=done → PM is pinged to start Step 5 reviews and produce the final Task report

Additionally, each teammate should self-trigger when preconditions are unambiguously met, so a missed ping does not strand the team.

## Impact

- Correctness: Tasks complete eventually, but only with human-in-the-loop nudges. Defeats the autonomy intended by Agent Teams.
- Throughput: Each idle stall is minutes-to-hours of wall time depending on whether a human is watching. Pattern B has been seen on every Task in some runs — the cost compounds.
- UX: User has to babysit runs that should be fire-and-forget, eroding trust in the workflow.

## Suggested fix

Four coordinated changes to skills/bees-execute/SKILL.md, in priority order. All are prose-only (no shell, no language-specific tooling) — cross-platform and language-agnostic by construction.

1. PRESCRIBED CHOREOGRAPHY (highest leverage). Add explicit team-lead message-flow rules to Section 3 / Section 4 covering ALL worker hand-offs, not just PM advancement. Minimum set: (a) after Engineer reports a subtask done, team-lead pings the Test Writer with "engineer subtasks done — start Phase A"; (b) after Test Writer reports Phase A done, team-lead pings PM with "subtasks complete, review the diff"; (c) after all subtasks at status=done, team-lead pings PM with "all subtasks done, run reviews and produce the final Task report". This is the cleanest architectural answer: workers do work, team-lead routes. Do NOT instead encode peer-to-peer notification (engineer pings test-writer directly) — that bakes in coupling, breaks when a Task has no test writer (research-only), and adds parallel message channels that obscure the orchestration model.

2. SELF-TRIGGER CHECKLISTS (paired with #1, defensive). Add to each worker role's Instructions block a top-of-turn self-evaluation: "If your gating precondition is met (gating subtask at bees-status=done, or all child subtasks at status=done for the PM), you are unblocked; start your work now, do not wait for further pings." Apply symmetrically to Test Writer (gates on Engineer) and PM (gates on all subtasks). Backstops the proactive choreography in #1 against missed pings.

3. IDLE-HANDLING LADDER (port from sibling). Port skills/bees-fix-issue/SKILL.md's idle-handling ladder (lines 249-254) into bees-execute. This is the reactive backstop for when both #1 and #2 fail. Without it, the team-lead has no prescribed response to observed idle and falls back to printing "Waiting" turns indefinitely.

4. REVIEW-SKILL TIME BUDGET. Add to PM Instructions: if /bees-code-review or /bees-doc-review returns >N work items or runs >M turns, short-circuit to blocker-only triage and move on. The skill already warns at line 314 that these "could infinitely return work items" but provides no escape valve.

Key files: skills/bees-execute/SKILL.md (Section 3 ~lines 188-329, Section 4 ~lines 332-403, Engineer/Test Writer/PM Instructions ~lines 243-329); skills/bees-fix-issue/SKILL.md (lines 249-254 — source of the idle-handling ladder pattern). The fix should also audit skills/bees-fix-issue/SKILL.md for the same proactive-choreography gap and apply #1 and #2 there too — the engineer→test-writer dependency exists in both skills.

Explicitly NOT proposing:
- Mandatory heartbeat DMs from every teammate every turn — adds chatter, masks the orchestration gap rather than fixing it.
- Peer-to-peer notify (engineer SendMessages test-writer directly) — bakes in coupling, doesn't fix PM idle, doesn't generalize when a Task has no test writer.
- Polling on bees-status from worker agents — chicken-and-egg (who wakes the poller?), more brittle, does not address the architectural gap.

Note on misdiagnoses to avoid (both seen during triage): one analysis blamed a "Step 1 read specs … Step 7 final report with wait-for-X framing" PM prompt structure; another claimed "the engineer's prompt tells them to SendMessage the PM after they finish." Neither claim is in the SKILL.md — both describe runtime improvisation by the team-lead. Rewriting role sections without fixing prescribed choreography will push the bug elsewhere rather than eliminate it.
