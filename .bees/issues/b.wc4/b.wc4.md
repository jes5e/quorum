---
id: b.wc4
type: bee
title: Skill boundaries default to same-session continuation, burning context unnecessarily
status: open
created_at: '2026-05-01T15:44:54.941078'
schema_version: '0.1'
egg: null
guid: wc4gtmnheny9awgqsjrspgkv283hoqh2
---

## Description

Several skill boundaries in the bees-workflow chain recommend (or auto-trigger) running the next skill in the **same** Claude Code session. Each downstream skill re-reads its state from the bees CLI and from disk (Plan Bee body, Epics, ticket schemas, CLAUDE.md), so nothing in the conversation context is load-bearing across the boundary. Carrying the prior skill's conversation forward just consumes context budget that the next (heavier) skill needs.

This shows up most painfully on big features: by the time a user has run `/bees-plan` (deep codebase exploration + scope iteration) and `/bees-breakdown-epic` (PRD/SDD/Plan-Bee parsing + per-Task body authoring), there is little context left for `/bees-execute` (which spawns Engineer / Test Writer / Doc Writer / PM agents per Task and runs review cycles).

## Current behavior

Audit found four locations where same-session continuation is the current default:

| Location | Current behavior | Severity |
|---|---|---|
| `skills/bees-plan-from-specs/SKILL.md:165-168` ("Continue to bees-breakdown-epic") | Auto-loads `/bees-breakdown-epic` for each Epic with **no opt-out**. Prose: "Do not ask the user for permission — proceed automatically." | Worst — forces continuation |
| `skills/bees-breakdown-epic/SKILL.md:312-321` ("Offer Next Steps") | Offers `/bees-execute <bee-id>`, `/bees-execute <epic-id>`, and `/bees-breakdown-epic <next-epic-id>` as same-session options via `AskUserQuestion`. | High — boundary the user reported |
| `skills/bees-plan/SKILL.md:249-256` ("Offer Next Steps") | Offers both **Break down now** (`/bees-breakdown-epic`) and **Execute now** (`/bees-execute <bee-id>`) as same-session continuations. | High — `bees-plan` is itself heavy |
| `skills/bees-setup/SKILL.md:771-793` ("Next Steps") | Recommends running `/bees-plan-from-specs` or `/bees-plan` next with no fresh-session note. Setup may have just generated bootstrap PRD/SDD docs, which is heavy. | Medium |

## Expected behavior

Each "run X next" recommendation at a heavy → heavy boundary should default to a **fresh Claude Code session**, with a one-line justification: each skill re-reads its inputs from the bees CLI / disk, so prior conversation context is not load-bearing across the boundary.

For `bees-plan-from-specs`, the auto-chain should be replaced with the same "Offer Next Steps" structure the sibling skills use, defaulting to "fresh session." A small Bee with one or two Epics is the only case where same-session continuation is reasonable, and even then it should be an explicit opt-in.

## Impact

- **Big-feature execution quality**: by the time `/bees-execute` runs, the orchestrator's context is already largely consumed by planning conversation that adds no information bees-execute can't re-derive from tickets. Reduces headroom for per-Task review cycles, post-completion review, and the team-lead's running judgment.
- **Cost**: each subsequent assistant turn re-tokenizes a larger transcript than necessary.
- **User trust**: users who follow the recommendation in good faith hit context-pressure symptoms later in the run that look like skill bugs but are really session-management artifacts.

## Suggested fix

Apply a uniform pattern at all four boundaries:

1. **`bees-plan-from-specs:165-168`** — replace the auto-chain with an explicit "Offer Next Steps" block matching the structure in `bees-plan` and `bees-breakdown-epic`. Default option: "**In a fresh session**, run `/bees-breakdown-epic <bee-id>`." Same-session continuation becomes an explicit alternative for small Bees, not the default.

2. **`bees-breakdown-epic:312-321`** — reword each `AskUserQuestion` option to lead with "**In a fresh session**, run `/bees-execute <bee-id>`" (etc.). Add a one-line note above the options explaining why fresh-session is the recommended default. Keep "Break down the next Epic" as same-session-OK since it is the same skill repeating, with relatively low context growth per Epic — but still flag it as fresh-session-friendly.

3. **`bees-plan:249-256`** — same treatment: reword "**Break down now**" and "**Execute now**" to lead with "In a fresh session, run …". Add the same one-line justification.

4. **`bees-setup:771-793`** — append a one-line fresh-session recommendation to both arms of the next-step branch (PRD/SDD path → `/bees-plan-from-specs`; idea path → `/bees-plan`). bees-setup with bootstrap doc generation can itself consume substantial context.

**Keep as-is** (these are not the same anti-pattern):

- `bees-execute:500` "Fix in this session" — the orchestrator's in-context judgment about which reviewer feedback is worth fixing vs. ignoring is load-bearing; a fresh session would re-litigate.
- `bees-execute:501` and `bees-fix-issue:391` "File as issue tickets" — invokes lightweight `/bees-file-issue` per issue; same-session is correct.
- `bees-file-issue` end — already light, no continuation problem.

Add a short principle to the project's CLAUDE.md or to `docs/doc-writing-guide.md` capturing the rule:

> **Heavy → heavy skill boundaries default to fresh-session.** When a skill's "Offer Next Steps" block points at another skill that does its own deep state read (e.g. `/bees-plan` → `/bees-breakdown-epic` → `/bees-execute`), the recommended default should be running the next skill in a fresh Claude Code session. Prior conversation context is not load-bearing — the next skill re-reads from the bees CLI and disk. Same-session continuation is acceptable as an opt-in for small features, never as the default.

This is a workflow-level guidance issue, so the fix is six skill edits plus one documentation addition. No code or tests to add.
