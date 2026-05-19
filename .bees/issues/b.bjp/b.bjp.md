---
id: b.bjp
type: bee
title: Add fresh-eyes plan-review gate to /quo-plan before Step 6 next-steps prompt
status: open
created_at: '2026-05-19T23:11:57.439274'
schema_version: '0.1'
reference_materials: null
guid: bjprbhf3y94cgwistwpvfzrwsa4n4m92
---

## Description
After Epic creation, /quo-plan has no fresh-eyes review that asks "is the problem well understood and framed right, is the approach sound, are the Epics decomposed sensibly." /quo-spec-review (the existing gate at Step 4c) is checklist-focused on PRD/SDD content quality — section completeness, criterion measurability, codebase grounding, cross-doc consistency — and does not critique the overall plan as a coherent solution to the problem.

This gap was discovered when a user ran the workflow on a large plan, then opened a fresh Claude Code session and asked it to review what the planning session produced. The fresh session returned substantive critique that the planning session triaged (accepted some, pushed back on others) — a useful loop that currently lives outside the workflow.

## Current behavior
/quo-plan ends at Step 5d (Epic ticket creation + dependency wiring) and proceeds to Step 6 (next-steps prompt). The only quality gate between Spec Bee creation and Plan Bee promotion is /quo-spec-review (Step 4c), which runs a checklist-based review of PRD/SDD content. Plan-level concerns — whether the problem is well understood and framed right, approach correctness, Epic decomposition sensibility — are not reviewed.

## Expected behavior
After Step 5d (Epic creation) and before Step 6 (next steps), /quo-plan dispatches a general-purpose Agent with a cold-start, fresh-eyes prompt that:

- Reads the PRD child, SDD child, Plan Bee body, and Epic bodies via `bees show-ticket`.
- Returns a structured critique with severity-tagged findings + a verdict trailer (analogous to `agents/analyst.md`'s contract).
- Focuses on substance — problem understanding and framing, approach correctness, Epic decomposition, missing risks/alternatives — explicitly out of scope for the prose-quality nits /quo-spec-review already covers.

The orchestrator then triages findings, presents its take to the user ("address #2 and #5; push back on #1 because…"), runs an `AskUserQuestion` gate, and on Revise loops back through the relevant writer skills (`/quo-write-prd`, `/quo-write-sdd`) and/or amends Epics in place. Same time-budget short-circuit pattern as /quo-spec-review (~10-item / ~3-turn bounds) to avoid thrashing.

## Impact
Silent plan-quality issues currently only surface mid-execution — when an Engineer hits a contradiction in the Epic decomposition, or when a Task body author realizes the SDD didn't actually solve the stated problem. A pre-execution fresh-eyes gate catches these cheaply (one Opus pass over PRD+SDD+Epics) rather than expensively, during /quo-execute when context budget is already tight.

## Suggested fix
Add a new step to `skills/quo-plan/SKILL.md` (between current 5d and 5e/Report) that:

1. Dispatches a general-purpose Agent with a self-contained prompt naming the artifacts to read (Spec Bee ID, Plan Bee ID, Epic IDs) and the structured-output contract to return (severity-tagged findings + verdict trailer).
2. Reads the critique back in the orchestrator turn, evaluates each finding, presents a triage to the user with `AskUserQuestion` (Approve triage / Revise plan / Discuss).
3. On Revise: route findings back through `/quo-write-prd`, `/quo-write-sdd`, or in-place Epic-body amendments depending on which artifact each finding targets.
4. Time-budget short-circuit mirroring /quo-spec-review's ~10-item / ~3-turn bounds.

The dispatch prompt is embedded in the skill prose — no new file under `agents/` is created.

## Background and rationale
- /quo-spec-review was considered as the home for this work but rejected: it's a checklist review with a tight focused purpose. Overloading it with "is the approach right" critique would dilute that focus and make tuning harder for both modes.
- `agents/analyst.md` was considered: tools and shape are close, but it is purpose-built for /quo-fix-issue's flow — generating a Design Proposal from an Issue body, with a verdict trailer keyed to "did codebase research agree with the body's framing." Plan-review is the inverse job — critiquing an already-formed plan — with different inputs (PRD+SDD+Epics, not an Issue body), output shape (multi-finding critique, not a single proposal), and verdicts.
- The user's manual workaround (open a fresh Claude Code session, ask it to review) maps directly onto the general-purpose Agent dispatch pattern: cold-start, no warm-state, fresh eyes on the artifacts.

## Decisions and rejected alternatives
- **Extend /quo-spec-review to cover plan-level critique** — rejected. Two skills with distinct concerns (checklist content review vs holistic plan critique) are cleaner than one skill with two modes.
- **Add a custom subagent under `agents/` (e.g., `agents/plan-reviewer.md`)** — rejected. Custom subagents earn their weight when (i) the role is invoked many times with a stable contract across orchestrators, (ii) tool allowlist needs to be tighter than `*`, or (iii) instructions are too long to embed inline. Plan-review is one-shot per /quo-plan run, read-only (general-purpose's `*` allowlist is fine), and its instructions fit inline in the dispatch prompt.
- **Reuse `agents/analyst.md` (generalize it)** — rejected. analyst's description, structured-output contract, and verdict vocabulary are load-bearing for /quo-fix-issue's orchestrator routing. Generalizing them would muddy a currently-tight contract.

