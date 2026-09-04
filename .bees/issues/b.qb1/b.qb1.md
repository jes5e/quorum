---
id: b.qb1
type: bee
title: 'Review loops must converge: delta re-review, blockers and regressions only after round 1, round-3 cap'
status: open
created_at: '2026-09-04T00:02:06.972824'
schema_version: '0.1'
reference_materials: null
guid: qb1cdqsrts315zuyxi328p3c76ik49in
---

## Description

Review loops in `/quo-fix-issue` and `/quo-execute` are generative rather than convergent: each reviewer round re-reviews the whole diff with the same open-ended brief, so later rounds keep producing new suggestions and nits about the previous round's fix rather than closing on the Issue's defect. Nothing tells a reviewer that round N+1 has a narrower job than round 1.

## Current behavior

On b.y2q, doc review ran 4 rounds for a one-clause edit; on b.pdq, ~35 findings after round 1, of which only a handful concerned what the Issue asked for — the rest concerned machinery earlier rounds had added. Each round's findings were legitimate in isolation; the loop had no convergence criterion.

## Expected behavior

- **Round 1** reviews the full diff with the full brief (including the second-order-effects ask from b.pdq).
- **Round N+1** reviews the **delta since round N's findings** and may raise only (a) `blocker`-severity items, (b) **correctness regressions introduced by the previous round's fix** (in code these are the common and dangerous case — e.g. a new log line that can raise), and (c) unaddressed items from its own previous list. New `suggestion`/`nit` items are recorded in the final report as acknowledged, not fed back as another round.
- **Hard cap:** after round 3 the orchestrator stops the loop, triages remaining items to blockers and regressions, dispatches one final fix, and defers the rest to the report (matching the ~3-turn bound the spec-review and plan-review gates already use).
- Reviewer dispatch prompts carry the round number and the previous findings so the reviewer knows which brief applies.

## Impact

Round count on every run, without lowering the quality gate: blockers and regressions remain reportable in every round; only the open-ended rediscovery of nits is bounded.

## Suggested fix

1. `skills/quo-engineer-review/SKILL.md`, `skills/quo-test-writer-review/SKILL.md`, `skills/quo-doc-writer-review/SKILL.md`: add a "re-review brief" section keyed on a `round:` field in the dispatch args.
2. `skills/quo-fix-issue/SKILL.md` Section 5 and `skills/quo-execute/SKILL.md` Section 5: pass the round number and prior findings; enforce the round-3 cap; route acknowledged items to the report.
3. `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`: mirror the brief.

## Background and rationale

Surfaced by the speed review of 2026-09-03 (b.y2q, b.pdq). Complements Issue b.nn8's mechanism-introducing-finding rule: b.nn8 keeps later rounds from *building* new machinery; this Issue keeps them from *rediscovering* nits.

