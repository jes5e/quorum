---
id: b.7wb
type: bee
title: Record per-phase timings in the run-state manifest so speed work is data-driven
parent: null
reference_materials: null
created_at: '2026-09-04T00:02:08.390359'
status: open
schema_version: '0.1'
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

## Amendment (2026-09-11) — record review rounds per lane and classify each round, so round waste is measurable

The per-phase timings this ticket asks for answer "where does wall-clock go". The second validation run of the rewritten orchestrators (b.zi3, Event Consumer Service) and the sixteen-round cold-review batch that followed it raised the adjacent question "are we running more review rounds than the work needs", and today nothing records the data to answer it.

**What to record.** For every review lane a run dispatches (Engineer → Code Reviewer, each writer → reviewer pair, the PM's in-flight reviews), the manifest already carries `## Rounds` (the trivial-tweak nit count) and `## Lanes` (`round`, the dispatch count). Add, at the point each round's findings are dispositioned, a one-word classification of every round after the first:

- **earned** — the round found a behavior defect in the previous round's fix (a dispatch condition, routing input, staging, commit, gate, or a code defect). The round paid for itself.
- **late** — the round found a pre-existing defect the first round should have caught. A reviewer-coverage problem, not a round-count problem.
- **variance** — the round found only wording or presentation items on text a previous round accepted unchanged. This is the waste.

The run summary's **Reviews** line renders, per slot, `N rounds (earned/late/variance = a/b/c)` beside the existing nit count. The classification is the orchestrator's judgment over the reviewer's findings list, made at the moment it already routes those findings, so it adds no dispatch and no gate.

**Why this shape.** Round count alone cannot distinguish a lane that converged on real defects from one paying a fresh reviewer for reviewer-to-reviewer wording variance. The b.zi3 report recorded three suggestion-tagged wording fixes at roughly 100K tokens each; the sixteen-round hand-edit batch scored roughly one third variance, with almost every earned round tracing to two edits made without enumerating their cases or readers. The shipped `**Severity bounds the loop**` rule holds a lane open for any `suggestion`; whether it needs an exit clause for variance rounds (the hand-edit process in this repo adopted one on 2026-09-11: a wording-only round on twice-accepted text closes the lane with residuals recorded) is a decision to make on this data, not on one run.

**Sequencing.** Land the instrumentation before the next validation runs (b.pkn in Event Consumer Service; the plan → breakdown → execute chain) so both produce classified round data. Do not change the shipped loop rule in the same change. The severity-calibration sentence added to the three review skills on 2026-09-11 ("a fix that changes neither what a true statement asserts nor what it causes a reader to do is a `nit`, not a `suggestion`") is the first lever and should be evaluated with the same data.

**Mechanism note.** The classification is a new column on an existing summary line and a new judgment at an existing routing moment; it introduces no state the manifest does not already carry per lane and no name class. If the design review judges even that too much, the fallback is to classify rounds after the fact from the run's review transcripts, which the run summary already links.

