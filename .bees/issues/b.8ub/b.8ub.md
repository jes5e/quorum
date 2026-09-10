---
id: b.8ub
type: bee
title: '/quo-fix-issue: Section 3 Cancel says no defer-* tasks come from the Analyst block, but 7.5 Step 0 banks them on the aborted path'
parent: null
reference_materials: null
created_at: '2026-09-08T17:46:35.021942'
status: done
schema_version: '0.1'
guid: 8ubusg8oxsjza8rsbta7ygfoy193whac
---

## Description

`/quo-fix-issue` states two things about what happens to the Analyst's `### Deferred refinements` block when the user picks `Cancel` at Section 3's approval gate, and they contradict each other.

## Current behavior

- Section 3's `#### Consume the Analyst's ### Deferred refinements block` says: "On Cancel, no `defer-*` tasks are created from the Analyst's `### Deferred refinements` block — the Issue stays `open` and the deferrals travel with the next Analyst pass when the user re-runs `/quo-fix-issue` on the Issue."
- Section 7.5's Step 0, which `#### Aborted-Issue close-out` step 2 invokes on exactly that path, says the Analyst surface "still appl[ies] on that path: the Analyst's block exists whenever Section 3 ran", and surface 3 directs creating a `defer-*` task per non-`None` bullet.

So Step 0 banks on a Cancel precisely what Section 3 says is not banked. Both sentences predate b.nn8 (present at `91eb07d`). b.nn8 made Section 3's gate re-fireable from Phase A and Phase C via `Re-dispatch the Analyst with this finding`, so a Section 3 `Cancel` is now reachable after a full Phase A/B pass, where the approved iteration's block is richer than at the initial gate and the tension bites harder.

## Expected behavior

One rule. Either Section 3's Cancel sentence is qualified to say the deferral-hygiene safety net still banks the block's items on the aborted path (and "travel with the next Analyst pass" is dropped), or Step 0's aborted-path note excludes the Analyst surface after a Section 3 `Cancel` (and the items really do travel with the next pass). Pick whichever matches the intended semantics of an aborted Issue's deferrals.

## Impact

Prose contradiction in a shipped skill; an orchestrator following Section 3 leaves the aborted Issue's Analyst-surfaced refinements unbanked, while one following the close-out banks them. Either outcome is defensible; the two texts disagreeing is the defect.

## Suggested fix

One clause in `skills/quo-fix-issue/SKILL.md`, at whichever of the two sites is wrong once the intended semantics are chosen. No mirror in `/quo-execute` (no Analyst there).

## Background and rationale

Surfaced by the b.nn8 post-completion code review (round 14) while re-reading the deferred-refinements consumption paragraph that b.nn8 rewrote for the third route into Approve. Confirmed pre-existing at `91eb07d`, so deferred rather than fixed in that run.

## Related

- b.nn8 (landed): rewrote the surrounding paragraph; made Section 3's gate re-fireable mid-run.
- b.pdq (landed): origin of the shared aborted-Issue close-out and the Step 0 aborted-path note.

## Resolution (2026-09-10)

Resolved by the clean-room orchestrator rewrite merged at `b611786`, not by a `/quo-fix-issue` run. The rewrite resolved the `FX-DEFC-18` / `FX-HYG-10` conflict in the hygiene direction: the Analyst gate's `Cancel` now routes through `#### Aborted-Issue close-out`, whose deferral-hygiene step treats the Analyst's `### Deferred refinements` block as a hygiene surface whenever the Analyst ran, and the "travel with the next Analyst pass" sentence no longer exists in `skills/quo-fix-issue/SKILL.md`. One rule remains. `docs/sdd.md`'s D10/D11 note records the choice. Confirmed against the body at `d736ff8` during the post-rewrite validation triage; closed without a dedicated fix commit.
