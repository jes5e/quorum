---
id: b.isi
type: bee
title: 'Post-completion review at high compromise-tracker volume: bound the recovery-gate sequence, recalibrate the >10-entries render rule, distinguish remediated contract violations'
parent: null
reference_materials: null
created_at: '2026-09-04T08:37:57.944726'
status: open
schema_version: '0.1'
guid: isidyejamcntdfj9k1565kezpex8madu
---

## Description

b.nn8 made the compromise tracker a routinely-written ledger (Trigger C appends on every ungated multi-path pick, with the lone-`trivial-tweak` carve-out as the only non-appending ungated route; the b.nn8 run itself produced on the order of a hundred entries across its in-flight and post-completion passes). Three parts of the post-completion review (Section 8 in `/quo-fix-issue`, Section 6 in `/quo-execute`) were calibrated for the earlier rare-tracker world and now scale badly or read stale state. All three sit in the same section and are best fixed in one pass.

1. **No bound on the recovery-gate sequence.** Step 7 fires one SR-6.7 or SR-4.6 recovery gate per `[compromise-challenge]` finding, non-aggregated, in emission order; PHASE 3 evaluates every `Orchestrator picked path (…)` entry on two axes. A post-completion reviewer that challenges even a fraction of a large tracker produces a serial `AskUserQuestion` sequence with no volume handling — the gates removed from the in-flight loop can reappear, in bulk, at run end.
2. **The `>10 entries → surface them ALL in full, no truncation` render rule** for `**Accepted compromises**` was written when the tracker rarely existed; tens of entries are now normal, so the end-of-run summary grew by roughly an order of magnitude and no surface revisits the rule. It fires correctly at any volume — this is calibration, not inconsistency.
3. **PHASE 2's blocker contract check reads a tracker field that is never rewritten.** `agents/pm.md`'s unit-scoped in-flight check (added in b.nn8) names an already-resolved entry in one line rather than re-emitting it, but PHASE 2 has no such carve-out: an entry remediated in-flight still reads as live at post-completion, where step 7 recommends `Fix in this session`. The fix touches the PHASE blocks that a test pins byte-identical across both skills through PHASE 5.

## Current behavior

Post-completion review cost and prompt count scale linearly with tracker entries with no ceiling; the summary renders every entry in full; a remediated contract violation cannot be distinguished from a live one at run end.

## Expected behavior

The post-completion review degrades gracefully with tracker volume (aggregate or paginate the recovery gates, or challenge only above a plausibility threshold), the render rule has a volume mode calibrated for the new base rate, and PHASE 2 can tell a remediated violation from a live one (or the in-flight check records remediation in a form PHASE 2 reads).

## Impact

Operator experience at run end (gate storms; long summaries) and one latent false-positive path in PHASE 2. No correctness impact on the fix itself.

## Suggested fix

One pass over `skills/quo-fix-issue/SKILL.md` Section 7 step 4 (render) and Section 8 (PHASE 1–3, step 6, step 7), mirrored in `skills/quo-execute/SKILL.md` Section 9 render and Section 6, keeping the two prompt skeletons byte-identical through PHASE 5. If (3) needs a "remediated" marker on tracker entries, that is a new tracker field threaded through the entry shape and every trigger — decide deliberately and record it in `docs/sdd.md`. Update `docs/prd.md` / `docs/sdd.md` b.nn8 entries and any render-step pins in `tests/test_routing_decision_contract.py`.

## Background and rationale

Surfaced by the PM during the b.nn8 run (rounds 2 and 3) and by several Code Reviewer second-order-effects notes. Deferred because bounding the gate sequence or adding a remediation marker is new machinery the Issue never asked for; b.nn8 shipped the base-rate corrections (render steps and checkpoint tracker-absent notes) and the PM-side already-resolved carve-out only.

## Related

- b.nn8 (landed): tracker base-rate inversion.
- b.qb1 (open): in-flight review-loop convergence — adjacent but about the in-flight loop, not post-completion.
- b.3og (open): pipeline sizing to the Analyst's blast radius.

