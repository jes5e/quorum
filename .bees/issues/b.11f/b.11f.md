---
id: b.11f
type: bee
title: PM agents idle mid-Task; bees-execute lacks team-lead orchestration
status: open
created_at: '2026-05-01T16:43:22.774627'
schema_version: '0.1'
egg: null
guid: 11fjce8bzcmgamir65uoqfxf1r7mmtm3
---

## Description

bees-execute SKILL.md describes the Product Manager as a job description (responsibilities + instructions), leaving the team-lead to improvise spawn prompts and inter-phase pings. Combined with Agent Teams' message-driven model — agents only run when they receive a message — PMs that finish processing one ping idle silently until the next ping, even when all preconditions for the next phase are met.

## Current behavior

Observed in real bees-execute runs: PM stuck after Engineer + Test Writer completed, only advanced after a human "are you stuck?" prompt. The PM had everything it needed (all subtasks at status=done) to start Step 5 reviews, but stayed silent because no incoming message told it to advance.

Why prescribed orchestration is missing: skills/bees-execute/SKILL.md Section 3 ("Form Team to Execute Tasks") and Section 4 ("Per-Task and Per-Epic Cleanup") describe what each agent's role is but never describe what messages the team-lead should send to advance the PM through phases. The PM Instructions block (lines 286-329) lists responsibilities but not "you are in phase X when condition Y holds, start it now" triggers.

Why this is structurally a problem in Agent Teams: there is no "teammate idle" event. Teammates that finish processing input and send no reply simply stop. The team-lead has no notification signal — it must proactively manage advancement.

## Expected behavior

Per skills/bees-execute/SKILL.md, the team-lead should reliably advance the PM through per-subtask review → cross-Task review → final report without requiring human nudges, and the PM should self-trigger when preconditions are clearly met.

## Impact

- Correctness: Tasks complete eventually, but only with human-in-the-loop nudges. Defeats the autonomy intended by Agent Teams.
- Throughput: Each idle stall is minutes-to-hours of wall time depending on whether a human is watching.
- UX: User has to babysit runs that should be fire-and-forget, eroding trust in the workflow.

## Suggested fix

Three coordinated changes to skills/bees-execute/SKILL.md, in priority order:

1. ORCHESTRATION (highest leverage). Add explicit team-lead choreography to Section 3 / Section 4 prescribing when the team-lead pings the PM and what message it sends. Example transitions to make explicit: after Engineer reports done, ping PM with "engineer subtasks done — review the diff and report"; after all subtasks status=done, ping PM with "all subtasks done, run reviews and produce final Task report". Today these transitions are left to team-lead discretion.

2. PM SELF-TRIGGER (paired with #1). Add to the PM Instructions block (currently lines 286-329) a top-of-turn self-evaluation checklist that replaces any passive "wait for X" framing the team-lead might improvise, e.g. "If all child subtasks are bees-status=done, you are in review-and-report mode; start it now, do not wait for further pings." Putting this in the SKILL.md ensures the team-lead's improvised spawn prompt inherits the trigger.

3. REVIEW-SKILL TIME BUDGET. Add to PM Instructions: if /bees-code-review or /bees-doc-review returns >N work items or runs >M turns, short-circuit to blocker-only triage and move on. The skill already warns at line 314 that these "could infinitely return work items" but provides no escape valve.

Key files: skills/bees-execute/SKILL.md (Section 3 lines ~188-329, Section 4 lines ~332-403, PM Instructions lines ~286-329).

Explicitly NOT proposing: mandatory heartbeat DMs from PM every turn. This was a candidate fix but adds chatter and masks the orchestration gap instead of fixing it. If #1 is done correctly, heartbeats become unnecessary.

Note on misdiagnosis to avoid: a prior analysis blamed a "Step 1 read specs ... Step 7 final report with wait-for-X framing" PM spawn prompt structure. That structure is NOT in the SKILL.md — it is improvised by the team-lead at runtime. Rewriting the PM section without fixing team-lead choreography will push the bug elsewhere rather than eliminate it.
