---
id: b.tmk
type: bee
title: 'PM dispatch in /quo-fix-issue: drop Complex gate, Section 4 timing, short-circuit'
parent: null
reference_materials: null
created_at: '2026-05-14T10:58:50.270851'
status: done
schema_version: '0.1'
guid: tmksz56p92q51qcbki3n33vo983bm45b
---

## Description
PM dispatch in `skills/quo-fix-issue/SKILL.md` has two compounding miscalibrations:

1. **The orchestrator-direct Complex/Simple gate (Section 3) is structurally wrong.** The Simple criteria are described by category of work (rename, mechanical refactor, test-only, doc-only) while the Complex criteria are described by risk surface (3+ files, public API, auth, side effects). The two lists are not symmetric — a 2-file source+test fix doesn't cleanly match either side, and the catch-all bullet "Could have non-obvious side effects on other modules" pulls almost any code-touching change toward Complex. The gate also fires *before* the Engineer runs, but "changes span 3+ source files" is a property of the post-implementation diff — the orchestrator is guessing about a future diff from the Issue body, which is exactly the kind of structural signal it's worst at predicting. More fundamentally, the orchestrator lacks the context to predict spec-drift risk from the Issue body alone — that question only becomes answerable after reading the actual spec content, which the PM Agent has access to and the orchestrator does not. Pre-judging is consistently wrong.

2. **When the gate fires Complex, the PM is dispatched before a diff exists.** Section 3 dispatches the PM in parallel with the implementer Agents (Engineer / Test Writer / Doc Writer). The PM role contract in `agents/pm.md` is built around reviewing the implementers' diff, so dispatching the PM before any diff exists wastes the PM's turn. The same paragraph (line 220) also describes two incompatible orderings — "alongside" (parallel) and "joins the implementer outputs as input to Section 4" (sequential) — which is an internal contradiction.

The two miscalibrations interact: fixing the timing without dropping the gate leaves the orchestrator making an unreliable pre-Engineer judgement; dropping the gate without fixing the timing brings the no-diff problem back on every Issue rather than just Complex ones. The combined fix is cleaner than either fix alone.

## Current behavior
- Section 3 "Assess complexity" sub-section (lines 182-198) gates PM dispatch on an orchestrator-direct Simple/Complex classification. The criteria are non-symmetric (categories vs risk surfaces) and pre-fire before the Engineer runs.
- Section 3 reconciliation-loop step 2 (line 220): "If the Issue was classified Complex, the per-issue PM Agent is dispatched **alongside** the implementer Agents (see 'Per-issue cold dispatch' below); the PM's report joins the implementer outputs as input to Section 4."
- Section 3 "Per-issue PM dispatch" sub-section (line 295): "When the orchestrator classifies an Issue as Complex (per 'Assess complexity' above), it dispatches a fresh PM Agent **alongside** the implementer Agents for that Issue."
- Section 3 dispatch-roles bullet list (line 254) names PM as a per-Issue implementer-phase role with the "Dispatched only for Complex fixes" qualifier.
- Section 5 (lines 372-390) branches on the Complex/Simple classification — Complex defers spec-alignment to the PM dispatched in Section 3, Simple does an orchestrator-direct spec-vs-code check.
- Section 4 review-iteration logic (line 364) carries a "if the original fix was simple (no PM dispatched), do NOT dispatch the PM on iteration" branch.
- `agents/pm.md` (line 8): "The Product Manager is the per-Task quality gate dispatched by an orchestrating execution skill (/quo-execute or /quo-fix-issue) **after** the Engineer / Test Writer / Doc Writer have produced their work for a Task."
- `agents/pm.md` (line 19): the PM orchestrates `/quo-engineer-review` and `/quo-doc-writer-review` "against the Task's diff" — a diff that does not yet exist when the PM is dispatched in parallel with the implementers.
- README.md (line 31) describes the PM correctly as the after-implementers gate, so the README does not need correction — it is the SKILL.md side that drifted.

In a real run observed in a sibling repo, the PM correctly returned a "cannot proceed — no work to review" verdict and used its turn doing partial pre-flight spec validation against the Issue body, then was effectively re-dispatched at Section 4 timing.

## Expected behavior
Single combined design with three parts:

1. **Drop the Complex/Simple gate entirely.** Replace with the same always-dispatched pattern already used for Doc Writer in the same skill (line 253: "Doc Writer — always dispatched. The Doc Writer decides whether docs actually need updating after reading the diff; the orchestrator does not pre-judge."). PM is always dispatched per Issue — the orchestrator does not pre-judge spec-drift risk.

2. **Move PM dispatch from Section 3 to Section 4.** The PM lands alongside the reviewer Agents (Code Reviewer / Test Reviewer / Doc Reviewer), after the diff exists. This matches `agents/pm.md`'s existing role contract — the PM is the per-Task quality gate that runs **after** the implementers have produced their work — and removes the internal contradiction at line 220.

3. **Self-short-circuit in `agents/pm.md`** for the no-spec-surface case. The judgement is **content-based**, not shape-based. The PM first reads every available spec source: the Issue body itself, the Plan Bee body if `up_dependencies` links one, the PRD/SDD-equivalent docs (per CLAUDE.md `## Documentation Locations`) if the body cites them, and the upstream content fetched via `WebFetch` if `reference_materials` is set. After reading, the PM assesses whether those sources **collectively** carry substantive spec content — behavior described, architecture constrained, requirements specified — beyond a title plus a one-sentence problem statement that merely identifies what to fix without specifying how. When substantive content is present in **any** source, the PM proceeds with deep review against that substantive source. When substance is absent across **all** available sources, the PM exits with a one-line verdict ("no spec drift surface to review for this Issue") and skips the deep review. The orchestrator reads either outcome as a clean signal and includes it in the per-issue summary.

   The short-circuit MUST NOT key off shape signals — "PRD/SDD path mentioned in body," "Plan Bee linked in `up_dependencies`," "`reference_materials` is non-null" — because those do not reliably correlate with spec richness. A body can cite a PRD path and be a one-line rename; a Plan Bee can be linked for a trivial typo fix; a one-sentence GitHub Issue can sit behind a non-null `reference_materials` entry. Conversely a self-describing body with no external pointers can contain rich behavioral spec the PM must verify against. Substance can only be assessed after the PM has read the content; the orchestrator-side shape-check that this ticket eliminates from Section 3 must not be reintroduced inside the PM as a content-blind pre-read gate.

The Section 4 timing keeps the PM aligned with the role contract. The always-dispatched pattern matches Doc Writer's existing precedent. The self-short-circuit preserves the safety net (PM is available for every Issue with a spec surface) while eliminating the noise on trivial fixes the original Complex gate was trying to suppress.

## Impact
- **Miscalibrated gate causes noise on trivial fixes (current state).** The orchestrator-direct Simple/Complex classification produces false-positive Complex classifications on routine bug fixes, dispatching the PM unnecessarily and adding review-burden noise to the per-issue summary. This is the user-visible symptom that motivated the broader analysis.
- **Wasted dispatch turn on every Complex Issue (current state).** The PM is invoked with no diff to review, returns "no work to review," and is effectively re-dispatched at Section 4 time.
- **Internal contradiction confuses skill maintainers.** Line 220's "alongside ... joins ... as input to Section 4" describes parallel-vs-sequential timing simultaneously.
- **Risk of role-contract drift.** Maintainers who rely on the SKILL.md prose may try to "fix" `agents/pm.md` to remove the after-implementers framing, which would be the wrong direction — the role contract is already correct; the SKILL.md is the side that's wrong.
- **Eliminates a miscalibration class, not just symptoms.** Moving the spec-drift judgement into the PM Agent (which *has* the context) instead of the orchestrator (which *lacks* it) addresses the root cause of false-positive Complex classifications rather than tuning the gate's thresholds.

## Suggested fix
Skill-prose + role-contract change. No source code or tests are touched.

**In `skills/quo-fix-issue/SKILL.md`:**

1. **Delete the "Assess complexity" sub-section (lines 182-198).** No more orchestrator-direct Simple/Complex classification.
2. **Section 3 reconciliation-loop step 2 (line 220)** — drop the "If the Issue was classified Complex..." clause and the "alongside ... joins ... as input to Section 4" phrasing entirely. Replace with prose that says PM dispatch happens in Section 4, alongside the reviewers, on every Issue.
3. **Section 3 "Per-issue cold dispatch" sub-section (lines 249-254)** — remove PM from the per-Issue implementer-phase role list. PM is no longer an implementer-phase role.
4. **Section 3 "Per-issue PM dispatch" sub-section (lines 293-295)** — relocate to Section 4. Drop the Complex gate; keep the dispatch-prompt requirements (Issue ID + body verbatim + `up_dependencies` + `<scoped-marker-resolver-path>`) intact.
5. **Section 3 "Roles dispatched by the orchestrator" bullet at line 289** — relocate the PM bullet to a parallel block in Section 4 alongside the three reviewer-role bullets at lines 359-361. Drop the "Dispatched only for Complex fixes" qualifier. The bullet's prose (spec-source resolver branching, etc.) is unaffected.
6. **Section 4 reviewer dispatch block (lines 344-368)** — add PM as a fourth Agent dispatched in this block, **outside** the implementer-presence conditional-spawn rules at lines 348-353. The existing conditional-spawn rules ("only dispatch a reviewer whose corresponding implementer was used") apply to Code Reviewer / Test Reviewer / Doc Reviewer; PM is the exception — always dispatched per Issue regardless of which implementers ran, because spec-alignment review is meaningful on any diff. Update the dispatch-shape opener at line 346 to name PM as a fourth Agent dispatched alongside the three reviewers. Add a corollary that PM dispatches alongside the reviewers, not instead of any of them.
7. **Section 4 review-iteration logic at lines 363-368** — drop the "if the original fix was simple (no PM dispatched), do NOT dispatch the PM on iteration" branch. PM is always available for re-dispatch on review-loop iterations.
8. **Section 5 (lines 370-390)** — collapse the Complex/Simple branches into a single unified path. In the new design the PM was always dispatched in Section 4 and has either produced a spec-alignment verdict or short-circuited with "no spec drift surface" — either way the verdict lands in the per-issue summary, so Section 5 is always informational confirmation, never load-bearing orchestrator-direct work. Rewrite Section 5's body to remove the Complex-fix / Simple-fix branching at lines 372-385 entirely; the unified path references the PM as having been dispatched in Section 4 (superseding the current line-374 reference to Section 3). The `## Doc divergence noted` confirmation logic in the current Section 5 body (the named file/section now matches today's behavior post-fix) is preserved unchanged in the unified path.
9. **TaskList naming convention (line 316)** — `pm-<issue-id>` survives unchanged. Move the PM bullet from the implementer-Agents group to the reviewer-Agents group at line 317 to reflect the new dispatch phase.
10. **Anywhere else the words "Simple" / "Complex" appear as classification labels** (not as adjectives describing real attributes) — strip them.

**In `agents/pm.md`:**

Add a no-spec-surface short-circuit path at the top of the PM's flow. The decision is **content-based**, not shape-based:

1. **Read every available spec source first.** Pull in the Issue body itself, the Plan Bee body if `up_dependencies` links one (via the existing Path B in `agents/pm.md`'s Scoped-marker logic), the PRD/SDD-equivalent docs from CLAUDE.md `## Documentation Locations` if the body cites them, and the upstream content fetched via `WebFetch` if `reference_materials` is set (using the existing resolver-branching logic for `github-issue` / `linear-issue` / `url` / `file-path` / `bees`).
2. **Assess substance across the collective sources.** Substantive spec content describes behavior, constrains architecture, or specifies requirements, beyond a title plus a one-sentence problem statement that merely identifies what to fix without specifying how.
3. **Short-circuit when substance is absent across ALL sources.** Exit with a one-line verdict ("no spec drift surface to review for this Issue") and skip the deep review.
4. **Deep review when substance is present in ANY source.** Proceed against the substantive source(s) using the existing spec-vs-diff review path.

The short-circuit MUST NOT key off shape signals — "PRD/SDD path mentioned in body," "Plan Bee linked in `up_dependencies`," "`reference_materials` is non-null" — because those do not reliably correlate with spec richness. A body can cite a PRD path and be a one-line rename; a Plan Bee can be linked for a trivial typo fix; a one-sentence GitHub Issue can sit behind a non-null `reference_materials` entry. Conversely a self-describing body with no external pointers can contain rich behavioral spec the PM must verify against. Substance can only be assessed after content has been read.

**In `README.md`:**

Update any user-facing description of `/quo-fix-issue` that mentions the Simple/Complex distinction, if present. Update the workflow diagram if it shows the gate. The existing PM description at line 31 already describes the after-implementers timing correctly and does not need correction.

**Audit-and-update sweep:** anywhere in `agents/` or `skills/` that cross-references the Simple/Complex classification.

`/quo-execute` is unaffected — that skill always dispatches PM per Task and has no complexity gate to remove.

## Background and rationale
The skill currently conflates three separate concerns into one entangled design:

1. **Whether to dispatch PM** — the orchestrator-direct Complex/Simple gate.
2. **When to dispatch PM** — Section 3 (with implementers) vs Section 4 (with reviewers).
3. **What the PM does on a trivial Issue** — currently nothing graceful; the PM either does pre-flight spec validation against the Issue body, or returns "no work to review."

The current design picks the wrong answer on all three:
- **Whether:** orchestrator-direct gate (wrong context for the judgement).
- **When:** Section 3 (before the diff exists, contradicting the role contract).
- **What:** no first-class short-circuit, so the PM either wastes its turn or does ad-hoc pre-flight work.

The combined fix flips all three:
- **Whether:** always dispatched (move the judgement to the PM Agent, which has the context).
- **When:** Section 4 (after the diff exists, matching the role contract).
- **What:** explicit short-circuit in `agents/pm.md` when there's no spec surface to verify.

The internal-contradiction smoking gun is the single paragraph at line 220, which says both "dispatched alongside the implementer Agents" (parallel) AND "the PM's report joins the implementer outputs as input to Section 4" (sequential — implies the PM consumes the implementers' outputs). A reader cannot satisfy both readings simultaneously; the SKILL.md needs to pick one, and Section 4 is the right pick because it matches the role contract.

The Doc Writer pattern is the precedent for the always-dispatched part: the orchestrator does not pre-judge whether docs need updating; it dispatches the Doc Writer and lets the Doc Writer decide after reading the diff. The PM should work the same way, with the spec-surface check standing in for the docs-needed check.

The Complex-gate problem surfaced first as a user complaint that "we treat simple things as complex" — a calibration symptom. Investigating the calibration revealed that the gate's bullet lists are not symmetric (categories vs risk surfaces) and that the orchestrator can't predict spec-drift risk pre-Engineer regardless of how the bullets are worded. Tuning the gate would not fix the underlying problem; eliminating the gate does.

## Decisions and rejected alternatives

Six alternatives were considered:

- **Make the PM explicitly two-phase** (pre-flight at Section 3 dispatch time, spec-vs-diff at Section 4 review time). Rejected: doubles the PM's invocation count per Issue and forces `agents/pm.md` to split its instructions into two modes the orchestrator must select between. The pre-flight phase's added signal (Issue-body-vs-codebase framing check) is real but small relative to spec-vs-diff review, and the role-doubling complexity is not worth it.

- **Have the PM wait for the implementers internally** (stay dispatched alongside, but block on diff availability). Rejected: the orchestrator's reconciliation-loop yields on Agent completion notifications; an Agent that "waits internally" cannot release control back to the orchestrator without exiting. This would require either polling inside the PM Agent (rejected by Section 3's "Anti-pattern: no clock primitives" at lines 224-233) or a SendMessage-based handoff (unavailable per the SDD's warm-Agent intent being retired, captured by Issue b.x9w at line 260).

- **Keep the Complex gate; move PM dispatch to Section 4** (this Issue's original narrower scope, before the 2026-05-14 design conversation expanded it). Rejected as insufficient: fixes the timing contradiction but leaves the orchestrator-direct Complex/Simple gate in place, which is independently miscalibrated. The orchestrator lacks the context to predict spec-drift risk pre-Engineer, and the gate's bullet lists are structurally non-symmetric (categories vs risk surfaces). Fixing only the timing leaves users with the same false-positive Complex classifications on routine fixes.

- **Drop the Complex gate; keep PM in Section 3.** Rejected: brings back the "PM dispatched before a diff exists" problem on every Issue rather than only Complex ones. Strictly worse than the current state on the timing axis.

- **Shape-based short-circuit triggers inside the PM** (e.g., "short-circuit when no PRD/SDD path is mentioned in the body AND `up_dependencies` does not include a Plan Bee AND `reference_materials` is null or short"). Rejected as the same miscalibration as the original orchestrator-direct gate, just relocated from Section 3 to `agents/pm.md`. Shape signals do not reliably correlate with spec richness — a body can cite a PRD path and be a one-line rename; a Plan Bee can be linked for a trivial typo fix; a one-sentence GitHub Issue can sit behind a non-null `reference_materials` entry; conversely a self-describing body with no external pointers can carry rich behavioral spec. Pre-read shape checks reproduce the exact failure mode the orchestrator-side gate had (predicting drift risk from signals that don't correlate with it). The PM has the context to read content and make a substance-based judgement, and that's where the judgement belongs — full stop, no shape-based fallback.

- **Drop the Complex gate; move PM to Section 4; add a self-short-circuit (the chosen path).** Accepted: addresses all three concerns (whether, when, what) with a single coherent design. Matches the always-dispatched precedent set by Doc Writer in the same skill. **Cost profile:** one additional PM Agent invocation per Issue that today classifies as Simple (the PM used to be skipped entirely on those) — but that invocation typically hits the short-circuit and ends quickly, so the per-Issue token cost on the formerly-Simple path is small rather than zero. No latency penalty: PM runs in parallel with Code Reviewer / Test Reviewer / Doc Reviewer in Section 4, and the three reviewers already gate Section 5 entry, so adding PM to that parallel block does not lengthen Section 4. Section 4 timing also means the PM always has a diff to review when the short-circuit path does not fire.

## Tracking
This ticket's scope was expanded on 2026-05-14 from the narrower original framing ("PM Agent dispatched before a diff exists in /quo-fix-issue Complex path") to the broader combined design captured above. The original framing focused only on the Section 3 → Section 4 timing move with the Complex gate preserved. A design conversation surfaced that the gate itself is also miscalibrated, and that the cleanest combined fix is to address both miscalibrations together rather than land them as two sequential tickets that would touch overlapping prose. The Suggested fix above is the merged work list.

**Line-number references in this body** (e.g. `lines 182-198`, `line 220`) are anchored to `skills/quo-fix-issue/SKILL.md` as of 2026-05-14. If the file drifts before this Issue is fixed, the Engineer should re-resolve each reference by content — every cited block has a quoted-prose or sub-section-heading anchor in the Current behavior / Suggested fix sections that survives line-number renumbering.
