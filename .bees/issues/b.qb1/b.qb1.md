---
id: b.qb1
type: bee
title: 'Review loops must converge: delta re-review, blockers and regressions only after round 1, round-3 cap'
parent: null
reference_materials: null
created_at: '2026-09-04T00:02:06.972824'
status: open
schema_version: '0.1'
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
## Amendment (2026-09-04) — the cap bounds churn, never blockers; "delta" means the change and everything it reaches

Reviewed against large compiled codebases (Rust, C++), where a small textual change can break an invariant far from the diff and where round-2/3 findings are often genuine. Three corrections to the expected behavior above:

1. **Scope of a re-review is the delta plus its reach, never the changed lines alone.** Round N+1's brief: examine the changes since round N *and everything they touch* — call sites, trait/interface bounds and impls, error-propagation paths, ownership/lifetime and borrow assumptions, `unsafe` or otherwise contract-bearing blocks whose safety argument depends on the changed behavior, concurrency assumptions (`Send`/`Sync`, locks, async cancellation), and public API/ABI surfaces. What is excluded from later rounds is *rediscovery of style and clarity items in unchanged code*, not analysis of what the change affects.

2. **Blockers are never capped.** The round-3 rule bounds `suggestion`/`nit` churn only: after round 3, new suggestions and nits are recorded as acknowledged in the report. A `blocker` or a correctness regression is re-reviewed until clean in every round, at any round number. What changes at round 3 is the *response* to a blocker, not whether it is reviewed: three consecutive rounds that each produce a new blocker mean the fix is being designed by review — the orchestrator stops building and escalates through the scope-bounding gate (fix properly with a re-Analyst pass / defer to a follow-up Issue / accept the limitation), with the reviewer's findings attached, rather than dispatching a fourth blind fix.

3. **No churn cap on cross-cutting changes without consent.** When the Analyst's blast radius is Tier 3 (multiple subsystems or a shared library — Issue b.3og's tiers), the suggestion/nit cap does not apply automatically; the orchestrator surfaces the round count at the gate and the user chooses whether to bound it. On such changes a "suggestion" about a second subsystem is often a latent blocker.

Compiler and test gates are unaffected by this Issue: the Engineer's Compile/type-check, Lint, and Narrow/Full test runs happen on every round regardless of review-round rules.
## Amendment 2 (2026-09-04) — strict form: no cap at any severity; convergence of attention only

Supersedes the round-3 cap in the Expected behavior and in the first amendment. Quality is non-negotiable, so this Issue must not stop review at any severity. The final shape:

1. **No round cap on any finding.** `blocker`, `suggestion`, and `nit` items are all reportable and all addressed in every round, at any round number. Nothing is "acknowledged instead of fixed" by a counter.
2. **Speed comes only from not repeating.** Round N+1's brief: (a) review the change since round N **and everything it reaches** (call sites, trait/interface bounds and impls, error-propagation paths, ownership/borrow assumptions, `unsafe` or contract-bearing blocks, concurrency assumptions, public API/ABI surfaces); (b) do **not** re-litigate unchanged code the previous round already reviewed, and do not re-raise an item already recorded unless the fix regressed it; (c) every finding must be *new* relative to the prior rounds' lists, which are embedded in the dispatch prompt. This removes rediscovery — the source of b.y2q's four doc rounds and most of b.pdq's 35 post-round-1 findings — without removing coverage.
3. **Escalation, not cutoff, when blockers keep coming.** Three consecutive rounds that each produce a new blocker mean the fix is being designed by review; the orchestrator stops dispatching blind fixes and escalates through the scope-bounding gate (re-Analyst / defer to a follow-up Issue with the findings attached / accept) — a design signal for the user, never a reason to skip a round.
4. Compiler, lint, and Narrow/Full test gates run on every round regardless.

The tests this Issue adds must pin that no orchestrator prose contains a numeric round limit that suppresses findings.

