---
id: b.3og
type: bee
title: Size the /quo-fix-issue pipeline to the Analyst's blast radius (tiered lanes and post-completion sweep)
parent: null
reference_materials: null
created_at: '2026-09-04T00:02:05.471397'
status: open
schema_version: '0.1'
guid: 3ogo7uvu5sxpd4gffww95zjhyvzz1bn1
---

## Description

`/quo-fix-issue` runs the same pipeline depth for every Issue: Analyst, Engineer, Test Writer, Doc Writer, three reviewers, PM, deferral gate, and a fresh post-completion sweep. The pipeline's depth is not proportional to the change's blast radius, so small, local fixes pay the full ceremony.

## Current behavior

Issue b.y2q (a ~10-line `try/except` in one helper function, no contract or public-surface change) ran: 2 code-review rounds, 2 test-review rounds, **4 doc-review rounds** (six findings against a one-clause doc edit), a PM pass, a post-completion sweep (8 findings, 7 fixed), and a deferral-encode commit — three commits and seven files for a change whose blast radius was one function. Review found real items, but most of the wall-clock went to lanes and passes that a one-function fix does not need.

## Expected behavior

The orchestrator sizes the pipeline to the Analyst's blast radius (Issue b.q3f's `### Blast radius` section):

- **Tier 1 — local:** the sweep names one module/file, no public API, schema, wire, config, or shipped-doc surface. Dispatch Engineer and Test Writer; run code review and test review; **skip the Doc Writer and doc reviewer unless the sweep lists a doc site**; run the post-completion sweep in blocker-and-regression-only mode (or skip it when the sweep lists no cross-module site). PM traceability still runs (cheap).
- **Tier 2 — surface:** the sweep names a public API, schema, wire field, config surface, or customer/architecture doc. Full pipeline as today.
- **Tier 3 — cross-cutting:** the sweep names sites in more than one subsystem or a shared library. Full pipeline, and the Engineer's completeness-evidence requirement (b.pdq Amendment 2) is mandatory.

The tier is chosen by the orchestrator from the sweep, surfaced at the Section 3 design gate alongside the proposal, and recorded in the run-state manifest. The user may override it there.

## Impact

Speed on the most common case. Most Issues in a normal code project are Tier 1; today each costs the Tier-2/3 pipeline. Quality is preserved where it matters: the tier is derived from evidence the Analyst already produces, cross-cutting changes keep every lane, and the user sees and can override the tier at a gate they already pass through.

## Suggested fix

1. `skills/quo-fix-issue/SKILL.md` Section 3 (design gate) and Section 4 (dispatch): add the tier derivation and the per-tier lane set; record the tier in the manifest.
2. `skills/quo-fix-issue/SKILL.md` Section 8 (post-completion review): blocker-and-regression-only mode for Tier 1.
3. Mirror in `/quo-execute` at Task granularity where the Task body (via the PM's traceability) makes the surface known.
4. Depends on Issue b.q3f (the sweep is the signal); should land after it.

## Background and rationale

Surfaced by the speed review of 2026-09-03 across the b.y2q and b.pdq runs. Filed stack-neutrally: the tiers are defined by surfaces a code change touches, not by this repo's prose structure.
## Amendment (2026-09-04) — reviewers can escalate the tier

Tiering must not make blast-radius under-estimation silent. Any reviewer (code, test, doc, PM, or the post-completion sweep) that finds a site, surface, or dependency **outside the Analyst's `### Blast radius` list** reports it as a finding against the Analyst pass (per Issue b.q3f) **and the orchestrator escalates the tier** — Tier 1 → 2 when a public API, schema, wire, config, or doc surface appears; any tier → 3 when a second subsystem or shared library appears — re-dispatching the lanes the lower tier skipped (Doc Writer / doc reviewer; full-mode post-completion sweep) for the remainder of the run. Record the escalation and its cause in the run-state manifest and the final report. This is the quality guard for the speed gain: a wrong tier costs one extra dispatch, never a skipped lane.
## Amendment 2 (2026-09-04) — strict form: never skip a reviewer; tiering skips only the Doc Writer dispatch when there is provably nothing to write

Supersedes the Tier 1 lane set in the Expected behavior. Quality is non-negotiable, so no tier may reduce what is *reviewed*. The final shape:

- **Every reviewer runs in every tier:** code review, test review, doc review, PM traceability, and the fresh post-completion sweep — all in full mode, all tiers. No blocker-only mode.
- **The only lane tiering may drop is the Doc Writer dispatch**, and only when two independent sources agree there is nothing to write: the Analyst's `### Blast radius` lists no customer-facing, architecture, or shipped-skill doc site, **and** the PM's traceability pass confirms no doc surface is affected. The doc reviewer still runs and confirms the no-doc-impact conclusion against the diff; if it finds a doc site, the Doc Writer is dispatched (the escalation rule in the first amendment).
- **Tier is still derived and recorded** (Tier 1/2/3 from the blast radius) and surfaced at the design gate, because b.q3f's Engineer completeness-evidence requirement and b.qb1's escalation thresholds key on it — but it no longer gates any review.

The remaining speed gain is honest but smaller: one avoided cold Doc Writer dispatch on doc-free changes, and the reviewers' round-N briefs from b.qb1. If Issue b.7wb's phase timings later show review lanes dominate small-fix wall-clock, revisit with data, not by default.

