---
id: b.qb1
type: bee
title: 'Review loops: full-diff review every round by default; prior findings carried to suppress duplicates and verify fixes; blockers never deferred; three blocker rounds re-run the Analyst'
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
## Amendment 3 (2026-09-04) — blockers have no escape hatch; the design signal re-runs the Analyst, it does not open a gate

Corrects Amendment 2 item 3. Routing three consecutive blocker rounds to the scope-bounding gate was a cap in disguise: that gate's menu includes "defer to a follow-up Issue" and "accept the limitation", and for a `blocker` either choice closes the Issue with a known defect.

1. **A blocker is never deferred, accepted, or counted out.** An Issue (or a Task in `/quo-execute`) MUST NOT reach `done` while any `blocker` or correctness regression from any review round remains unaddressed. No round number, no gate option, and no orchestrator judgment can waive this.
2. **Three consecutive rounds that each surface a new blocker change the *method*, not the coverage.** The orchestrator automatically re-dispatches the Analyst with the full accumulated findings (all rounds, all lanes) and the current diff, asking for a revised Design Proposal; the Engineer → Code Reviewer loop then continues under the revised design, still with no cap. One transcript line and one manifest entry record that the re-Analyst fired and why. The user is informed, not asked; they may intervene at any time but nothing waits on them.
3. **The scope-bounding gate is for suggestions and nits only.** Its "defer" and "accept" options are unreachable for blocker-severity findings; the routing prose and the compromise tracker's entry shape must make that structurally true (a tracker entry cannot record a deferred blocker).
4. Tests this Issue adds must pin (a) no numeric round limit suppresses any finding, and (b) no routing path exists from a `blocker` to "defer" or "accept".
## Amendment 4 (2026-09-04) — the `/quo-execute` mirror, made concrete

Amendments 2–3 apply to `/quo-execute` in full, with the following specifics (the base Issue's "mirror in `/quo-execute`" was underspecified because execute has no Analyst dispatch today):

1. **No-deferral at every level.** A Task cannot be marked done with an open `blocker` or correctness regression from any review round; neither can an Epic, nor the Bee — including blockers raised by the Bee-level reviews (Section 5) and the fresh post-completion sweep (Section 6). Any option at the Section 6 findings gate, the deferral-hygiene gate, or the scope-bounding gate that would let the orchestrator close out over a blocker-severity finding is removed for that severity; the compromise tracker cannot record a deferred blocker. The user may always stop the run; nothing may mark it complete around a blocker.
2. **Design signal → conditional Analyst dispatch in execute mode.** When a Task's Engineer → Code Reviewer loop produces three consecutive rounds each surfacing a new blocker, the orchestrator automatically dispatches the Analyst (`agents/analyst.md`, extended with an execute-mode input: the Task body and its Subtask bodies, the SDD/PRD section the Task traces to via the Plan Bee's `reference_materials`, the current diff, and all accumulated findings across lanes) to produce a revised Task directive; the loop continues under it with no cap. One transcript line and one manifest entry record the dispatch and its cause. This is a *conditional* dispatch on a pathology signal — it does not conflict with Issue b.eid's rejection of an unconditional per-Subtask Analyst, and it should become rare once b.eid's per-Task site lists exist.
3. **Revised designs land in durable carriers.** If the revised directive changes the Task's scope or Subtask set, the orchestrator amends the Task body (and Subtask bodies) in bees before re-dispatching, so the change survives compaction and is visible to the PM's traceability pass; cross-Task or cross-Epic implications are surfaced at the existing inter-Epic interaction checkpoint rather than acted on silently.
4. **Contract updates.** `agents/analyst.md` frontmatter and `## Why this role exists` must stop saying the Analyst is dispatched only by `/quo-fix-issue`; CLAUDE.md's `agents/<role>.md` bullet and the SDD's model-assignment section are updated to match (same model/effort pins — `xhigh`).
5. **Out of scope for this mirror:** `/quo-plan`'s spec-review and plan-review "proceed anyway (override blockers)" options remain. Those blockers are document-quality checklist findings on PRD/SDD prose, and a human taking explicit, recorded responsibility at spec time is a different act from an orchestrator waiving a code defect; Issue b.eid is what tightens what those reviews check.
## Amendment 5 (2026-09-04) — the post-completion sweep is the whole-diff backstop for rounds 2+

Amendment 2's convergence-of-attention rule means rounds 2+ examine the change and its reach, not untouched code round 1 already reviewed. The residual risk is a round-1 miss in untouched code that today's repeated full passes sometimes catch. That coverage is preserved by the **fresh post-completion sweep** (`/quo-fix-issue` Section 8, `/quo-execute` Section 6), which must therefore:

1. Review the **entire** diff cold, at **all severities**, in every tier (per Issue b.3og's strict form) — it is the second whole-diff pass, by a reviewer with no anchoring on the intermediate rounds.
2. Route its findings into a normal fix-and-review cycle — blockers, suggestions, and nits alike are addressed, and that cycle is uncapped like every other — not into an acknowledged-items report.
3. Be dispatched with the round-1 and intermediate findings **withheld** (as today), so it cannot anchor on them; anchoring is exactly what makes intermediate rediscovery low-yield.

Net effect: whole-diff coverage happens twice (round 1 and the sweep); what the convergence rule removes is repeated *anchored* passes over unchanged text in between. Tests this Issue adds must pin that the sweep's dispatch prompt asks for all severities and that its findings enter the fix loop rather than the report.
## Amendment 6 (2026-09-04) — default is full-diff review in every round; change-plus-reach scope is opt-in only

Corrects Amendments 2 and 5. Each review round in this workflow is a fresh, cold agent (the reviewer contracts run cold by design), so rounds 2..N are additional independent full passes with real discovery value on untouched code — b.y2q's later doc rounds each found something that was fixed. Narrowing those rounds to the change and its reach would trade away discovery. Quality is non-negotiable, so:

1. **Default: every round reviews the full diff at all severities.** No convergence-of-attention narrowing by default. The final post-completion sweep remains as today (full, cold, all severities; findings enter the fix loop).
2. **What every round does get, with no coverage trade:** the dispatch prompt carries the prior rounds' findings and their fix status so the reviewer (a) does not re-raise an item already recorded, (b) verifies each recorded fix actually landed and did not regress, and (c) labels each new finding as new. This removes duplicate findings and lets the orchestrator see convergence, without removing a single pass.
3. **Change-plus-reach scope is an explicit per-project opt-in**, configured in the target repo's CLAUDE.md (a documented key, default absent = full review), for teams that consciously accept the discovery trade described in Amendment 5's residual. When enabled, Amendment 5's sweep-as-backstop rules apply in full. The default installation never narrows.
4. **Retained unchanged from Amendments 3–4:** blockers are never deferred, accepted, or counted out at any level; three consecutive new-blocker rounds trigger the automatic Analyst re-dispatch (execute mode where applicable) and the loop continues; the scope-bounding gate is unreachable for blocker severity.
5. **Where the speed comes from instead:** Issues b.q3f and b.nn8 remove the *causes* of extra rounds (mechanisms introduced mid-run; surfaces discovered one per round); b.pdq removes writer rework; b.3og (strict) removes one avoidable dispatch. This Issue's contribution is convergence *visibility* and duplicate suppression, not fewer passes.

Tests this Issue adds must pin: the default dispatch prompt asks for a full-diff review at all severities; the opt-in key is absent from the shipped skills' defaults; no numeric round limit suppresses any finding; no routing path exists from a `blocker` to defer/accept.
