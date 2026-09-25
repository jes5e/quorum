---
id: b.8x3
type: bee
title: Guard the /quo-breakdown-epic menu same-session next-Epic continuation
parent: null
reference_materials: null
created_at: '2026-08-19T21:37:34.613112'
status: done
schema_version: '0.1'
guid: 8x3k2so5kvphbop8bx6he2cb1e9kaprf
---

## Description

The context-window boundary guard shipped by Bee b.55r Epic 3 (t1.55r.h9) does not fire on `/quo-breakdown-epic`'s menu-driven same-session "break down the next Epic" continuation. Epic 3 wires the guard into the Mode 2 auto-continue-to-next-Epic path in Section 7, but the six-option next-steps menu's "In a fresh session, break down the next Epic" option also blesses same-session continuation (the menu prose states "Same-session continuation is also reasonable here"), and that path is left unguarded.

## Current behavior

On the Mode 2 auto-continue path, the guard runs at the Epic boundary (reads the context-usage gauge and stops with a fresh-session recommendation when usage crosses the stop threshold, or when the reading is stale/missing). But when the operator instead reaches the next-steps menu and picks "break down the next Epic" and continues in the same session, no guard check runs — the run keeps growing context across another Epic breakdown with no boundary stop.

## Expected behavior

A same-session, boundary-crossing continuation of the breakdown loop should get the same boundary guard as the auto-continue path — this is the exact class SR-2.7 / FR2 target (guard fires on boundary-crossing continuing runs). The current omission is also inconsistent with `/quo-execute`, whose analogous operator-present Mode 1 accept path IS guarded by this feature.

## Impact

Correctness / coverage gap. Bounded blast radius: the menu already recommends a fresh session as its primary action, so only an operator who actively overrides that recommendation and continues in-session is exposed; and b.ja9's lossless-compaction backstop still applies, so any compaction that fires mid-breakdown is not data-loss. But the guard's whole value — surfacing the *measured* context percentage and stopping before an ill-timed compaction — is absent on this path, and the menu recommends fresh-session generically without knowing whether usage is at 20% or 75%.

## Suggested fix

Decide whether to add a second guard insertion site at the post-menu same-session loop-back in `skills/quo-breakdown-epic/SKILL.md` Section 7 (the "break down the next Epic" menu option's same-session continuation). The design decision to make — not a mechanical port — is whether it is right to re-stop an operator who was *just* prompted at the menu; weigh that against (a) the value of surfacing the measured context percentage the menu itself lacks, and (b) cross-skill consistency with `/quo-execute`'s already-guarded Mode 1 accept path. If the decision is to guard it, mirror the canonical guard branch logic already used at the Mode 2 auto-continue path (same four-value + non-zero-exit + unset-session-id branch table, same two-step `TaskCreate` → `AskUserQuestion` missing-reading gate, threshold obtained from the helper's `stop-threshold` seam).

Key files: `skills/quo-breakdown-epic/SKILL.md` Section 7 (`#### Menu options` "break down the next Epic" + the post-menu same-session loop-back).

## Background and rationale

Surfaced by the Task 3 PM review during the `/quo-breakdown-epic b.55r` Epic 3 breakdown (2026-08-19). The Task 3 engineer researcher deliberately scoped the guard to the Mode 2 auto-continue path only and flagged the menu continuation as a follow-up rather than silently widening scope. The PM confirmed it is a REAL coverage gap (not acceptable-as-is): the "operator is present at the menu so no guard needed" counter-argument does not hold, because the feature's own precedent contradicts it — `/quo-execute`'s Mode 1 accept path is an operator-present same-session continuation that the feature DOES guard, so leaving `/quo-breakdown-epic`'s analog unguarded is an inconsistency, not a principled carve-out.

Confirmed scope of the gap: `/quo-execute` has no analogous gap (Mode 1 accept is already guarded); `/quo-fix-issue` has none (no same-session menu continuation exists there). The gap is specific to `/quo-breakdown-epic`'s menu.

## Decisions and rejected alternatives

- **Rejected: fold the fix into Epic 3's Task 3 now.** The PM recommended defer-to-Issue over fold-now because (1) the Task 3 body deliberately scoped the guard to the Mode 2 auto-continue path and its own scope-note anticipated this exact question as a follow-up; (2) folding requires a genuine design decision (whether to re-stop a just-prompted user, plus a second insertion site that is structurally distinct from the auto-continue path) that should be blessed explicitly rather than bolted onto an execution Subtask mid-run; and (3) the blast radius is bounded (menu already recommends fresh-session; b.ja9 backstop applies).
- **Rejected: accept-as-is / drop the concern.** That would lose a real coverage question. Defer-to-Issue is the non-lossy disposition — the question is captured in this durable carrier.
## Closed (2026-09-25)

Resolved by `2ab84d5`, which guarded the menu's same-session continuation. The b.pcc rewrite (merged at `a0cd8c2`) keeps the rule general: the guard runs before every Epic broken down in the same session after the first, whichever path continues. The two-step missing-reading gate this ticket's fix mirrored is gone (operator decision 2026-09-25).
