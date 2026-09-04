---
id: b.7wb
type: bee
title: Record per-phase timings in the run-state manifest so speed work is data-driven
status: open
created_at: '2026-09-04T00:02:08.390359'
schema_version: '0.1'
reference_materials: null
guid: 7wbxcr91evevc3avn3vymg1mcmdbsnzc
---

## Description

The orchestrators record run-scoped state in the run-state manifest but nothing about **how long each phase takes**. Speed work on quorum is therefore anecdotal: we know b.pdq took six rounds and b.y2q ran four doc-review rounds, but not how wall-clock split across Analyst dispatch, each implementer dispatch, each review round, PM, gates waiting on the user, test runs, and the post-completion sweep.

## Current behavior

No timing is captured anywhere. The only durable per-run record is the manifest's progress fields and the commits' timestamps.

## Expected behavior

Each orchestrator stamps phase boundaries into the run-state manifest as a per-skill field `- **Phase timings:** <phase>=<start>..<end>; ...` (UTC, from the orchestrator's own clock via the Write tool — no shell substitution), for at minimum: Analyst dispatch→return, each implementer dispatch→return (by role and round), each reviewer dispatch→return (by role and round), PM, each user gate open→answered, each Narrow/Full test invocation, the post-completion sweep, and the deferral gate. Also echoed as one transcript line per phase end so the series survives the manifest's next-run truncation. The internal architecture docs describe how to aggregate the series across runs (per-phase medians; gate-wait share; dispatch count per unit).

## Impact

Turns the next round of speed decisions — pipeline tiering thresholds, review-round caps, whether execute over-decomposes into too many cold dispatches — into data-driven ones, exactly as Plan b.jp2 does for the context threshold. Cost: one manifest line and one echo per phase.

## Suggested fix

1. `skills/quo-fix-issue/SKILL.md`, `skills/quo-execute/SKILL.md`, `skills/quo-breakdown-epic/SKILL.md`: add the per-skill manifest field and the stamp points; keep the three manifest sections' shared lead statements byte-identical.
2. Consider a shared procedure file for the stamp instruction (the b.jp2 pattern) rather than three copies.
3. `docs/sdd.md`: aggregation guidance.

## Background and rationale

Surfaced by the speed review of 2026-09-03. Hypothesis to test first with this data: in code projects, `/quo-execute` wall-clock is dominated by cold-dispatch count (each Subtask dispatch reloads skills, agent contracts, docs, and code), so `/quo-breakdown-epic`'s Subtask granularity may be the largest lever — coarser Tasks with one Engineer dispatch per Task. Do not act on that hypothesis without the timings.

