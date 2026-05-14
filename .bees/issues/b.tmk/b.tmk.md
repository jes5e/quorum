---
id: b.tmk
type: bee
title: PM Agent dispatched before a diff exists in /quo-fix-issue Complex path
status: open
created_at: '2026-05-14T10:58:50.270851'
schema_version: '0.1'
reference_materials: null
guid: tmksz56p92q51qcbki3n33vo983bm45b
---

## Description
In `skills/quo-fix-issue/SKILL.md`, Complex-classified Issues dispatch the PM Agent in parallel with the implementer Agents (Engineer / Test Writer / Doc Writer) in Section 3. But the PM role contract in `agents/pm.md` is built around reviewing the implementers' diff, so dispatching the PM before any diff exists wastes the PM's turn. The same paragraph (line 220) also describes two incompatible orderings — "alongside" (parallel) and "joins the implementer outputs as input to Section 4" (sequential) — which is an internal contradiction.

## Current behavior
- Section 3 reconciliation-loop step 2 (line 220): "If the Issue was classified Complex, the per-issue PM Agent is dispatched **alongside** the implementer Agents (see 'Per-issue cold dispatch' below); the PM's report joins the implementer outputs as input to Section 4."
- Section 3 "Per-issue PM dispatch" sub-section (line 295): "When the orchestrator classifies an Issue as Complex (per 'Assess complexity' above), it dispatches a fresh PM Agent **alongside** the implementer Agents for that Issue."
- Section 3 dispatch-roles bullet list (line 254) names PM as a per-Issue implementer-phase role.
- `agents/pm.md` (line 8): "The Product Manager is the per-Task quality gate dispatched by an orchestrating execution skill (/quo-execute or /quo-fix-issue) **after** the Engineer / Test Writer / Doc Writer have produced their work for a Task."
- `agents/pm.md` (line 19): the PM orchestrates `/quo-engineer-review` and `/quo-doc-writer-review` "against the Task's diff" — a diff that does not yet exist when the PM is dispatched in parallel with the implementers.

In a real run observed in a sibling repo, the PM correctly returned a "cannot proceed — no work to review" verdict and used its turn doing partial pre-flight spec validation against the Issue body, then was effectively re-dispatched at Section 4 timing.

## Expected behavior
PM dispatch should land in Section 4 (the review loop) alongside the three reviewer Agents (Code Reviewer / Test Reviewer / Doc Reviewer). The Complex-fix gate stays — Simple fixes still skip PM entirely. Only the timing changes:

- Section 3 dispatches only Engineer / Test Writer / Doc Writer on the implementer phase.
- Section 4 dispatches Code Reviewer / Test Reviewer / Doc Reviewer **plus** PM (on Complex fixes) — all four reviewers see the diff the implementers produced.
- The paragraph at line 220 drops the "alongside" phrasing and the contradictory "joins the implementer outputs as input to Section 4" clause.
- The TaskList naming convention (line 316: `pm-<issue-id>`) survives the move unchanged — the name does not encode timing.
- Section 5's complex-vs-simple branching at lines 372-390 already says "the per-issue PM Agent dispatched in Section 3 has already verified spec alignment" — after the move, this becomes "the per-issue PM Agent dispatched in Section 4 has already verified spec alignment" and the rest of Section 5's informational-confirmation-on-Complex / load-bearing-on-Simple split is preserved.

This matches `agents/pm.md`'s existing role contract — the PM is the per-Task quality gate that runs **after** the implementers have produced their work.

## Impact
- **Wasted dispatch turn on every Complex Issue.** The PM is invoked with no diff to review, returns "no work to review," and is effectively re-dispatched at Section 4 time. That's one wasted Agent invocation per Complex Issue.
- **Internal contradiction confuses skill maintainers.** The same paragraph describing parallel-vs-sequential timing makes it hard for a maintainer (or a reviewer skill like `/quo-engineer-review`) to know which behavior is intended.
- **Risk of role-contract drift.** Maintainers who rely on the SKILL.md prose may try to "fix" `agents/pm.md` to remove the after-implementers framing, which would be the wrong direction — the role contract is already correct; the SKILL.md is the side that's wrong.

## Suggested fix
Skill-prose-only change in `skills/quo-fix-issue/SKILL.md`. No source code or tests are touched.

1. **Section 3 reconciliation-loop step 2 (line 220)** — drop the "If the Issue was classified Complex, the per-issue PM Agent is dispatched alongside the implementer Agents..." clause. Replace with prose that says PM dispatch happens in Section 4 on the Complex path.
2. **Section 3 "Per-issue PM dispatch" sub-section (lines 293-295)** — relocate to Section 4 or rewrite to describe Section-4 timing. Keep the dispatch-prompt requirements (Issue ID + body verbatim + `up_dependencies` + `<scoped-marker-resolver-path>`) intact.
3. **Section 3 "Per-issue cold dispatch" sub-section (lines 249-254)** — remove PM from the per-Issue implementer-phase role list. PM is no longer an implementer-phase role on either Simple or Complex paths.
4. **Section 3 "Roles dispatched by the orchestrator" bullet at line 289** — relocate the PM bullet to a parallel block in Section 4 alongside the three reviewer-role bullets at lines 359-361. The bullet's prose (spec-source resolver branching, etc.) is unaffected.
5. **Section 4 reviewer dispatch block (lines 344-368)** — add PM to the conditional-spawn rules at lines 348-353 with the Complex-fix gate. Update the dispatch-shape opener at line 346 to name PM as a possible fourth Agent on the Complex path. Add a corollary that PM-on-Complex spawns alongside the reviewers, not instead of any of them.
6. **Section 5 complex-vs-simple branching (lines 370-390)** — change the line-374 phrase "the per-issue PM Agent dispatched in Section 3" to "the per-issue PM Agent dispatched in Section 4" on the Complex-path branch. The Simple-path branch is unaffected.
7. **TaskList naming convention (line 316)** — `pm-<issue-id>` survives. Move the PM bullet from the implementer-Agents group to the reviewer-Agents group at line 317 if a grouping-by-phase rewrite is preferred; otherwise leave the bullet untouched.

The Section-4 review-iteration logic at lines 363-368 (which already mentions PM re-dispatch on review iterations) lines up cleanly with the move — the original-Complex / iteration-PM-optional rule still applies after the move.

## Background and rationale
The skill currently conflates two reasonable but different PM jobs:
- **Pre-flight spec validation** — does the Issue body's framing match the codebase? Useful early, doesn't need a diff.
- **Spec-vs-diff review** — does the implementation match the spec? Requires a diff.

Doing both in one Agent forces the PM to either run with no diff (current observed behavior — wasted turn) or wait for the diff (defeats the "alongside" parallelism). The first option is what the SKILL.md prose currently says, the second is what `agents/pm.md`'s role contract describes.

The internal-contradiction smoking gun is the single paragraph at line 220, which says both "dispatched alongside the implementer Agents" (parallel) AND "the PM's report joins the implementer outputs as input to Section 4" (sequential — implies the PM consumes the implementers' outputs). A reader cannot satisfy both readings simultaneously; the SKILL.md needs to pick one.

## Decisions and rejected alternatives
Three alternatives were considered:

- **Make the PM explicitly two-phase** (pre-flight at Section 3 dispatch time, spec-vs-diff at Section 4 review time). Rejected: doubles the PM's invocation count per Complex Issue and forces `agents/pm.md` to split its instructions into two modes the orchestrator must select between. The pre-flight phase's added signal (Issue-body-vs-codebase framing check) is real but small relative to spec-vs-diff review, and the role-doubling complexity is not worth it.
- **Have the PM wait for the implementers internally** (stay dispatched alongside, but block on diff availability). Rejected: the orchestrator's reconciliation-loop yields on Agent completion notifications; an Agent that "waits internally" cannot release control back to the orchestrator without exiting. This would require either polling inside the PM Agent (rejected by Section 3's "Anti-pattern: no clock primitives" at lines 224-233) or a SendMessage-based handoff (unavailable per the SDD's warm-Agent intent being retired, captured by Issue b.x9w at line 260).
- **Move PM dispatch into Section 4 alongside the reviewers (the chosen path).** Accepted: keeps the role contract intact, costs no extra Agent invocations, matches the natural "reviewer phase" grouping, and removes the internal contradiction at line 220. The cost is minor SKILL.md restructuring; the win is conceptual coherence.

