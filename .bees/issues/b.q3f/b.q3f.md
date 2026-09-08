---
id: b.q3f
type: bee
title: Analyst must produce a blast-radius sweep and name implied policy decisions at the design gate
tags:
- process
- quo-fix-issue
- analyst
parent: null
reference_materials: null
created_at: '2026-09-02T20:22:55.277552'
status: done
schema_version: '0.1'
guid: q3fgxrryv8h9ibsij6hh39ye2cihkrbm
---

## Description

`/quo-fix-issue` Section 3 dispatches the Analyst once and gates on its Design Proposal (Problem / Root cause / Recommended approach / Why / Alternatives / Options the body did not consider). Two things the proposal does **not** require are what caused serial review-round churn on a real run:

1. **No blast-radius sweep.** The proposal names the approach but not *every site* an added/removed invariant touches (log lines, span attributes, metric labels, background-task names, exception messages, docstrings, deployment-manifest comments, customer docs, tests). Every one of those sites is grep-findable before implementation; instead they were discovered one per review round.
2. **No enumeration of implied policy decisions.** A change frequently forces a yes/no policy question the body never states ("is this value now a secret?", "does this validation apply on every surface or only the one the body names?"). On the reference run those were decided implicitly by a Doc Writer and a Code Reviewer mid-stream, each decision then obligating an unplanned sweep.

## Reference run (worked example)

event_consumer_service Issue b.239 (drop the hashed principal from durable-queue names), 2026-09-02. The Analyst correctly found the load-bearing refinement (the removed call was the service's only token-validation trigger). But the follow-on consequences arrived serially:

- Doc Writer r1 documented "reconnect tokens are secrets" → Code Review r1: secrecy missing from proto/REST contract text → Code Review r2 (blocker): token logged verbatim at INFO and in span attributes → Engineer r4 sweep found it also in metric labels, task names, `extra=` dicts, `__del__` warnings → Code Review r3 (blocker): one more task name + warning missed → Doc Writer r3: uvicorn access log still records the query string.
- Code Review r1: `QUEUE_ID_PATTERN` enforced only on create → Engineer r2 enforced on every API surface → Code Review r2: enforce structurally inside `DurableQueueConsumer` too.

Net: 5 Engineer rounds, 3 Test Writer rounds, 3 Doc Writer rounds, 3 code reviews, ~30 files, for a change whose design was approved at round 1. A single grep-backed sweep at the Analyst gate (`queue.name`, `queue_id`, `reconnect_token`, `extra=`, `add_current_span_attributes`, task `name=`) would have produced the full site list up front.

## Expected behavior

`agents/analyst.md` structured-output contract gains two required sections, and SKILL.md Section 3 surfaces both at the approval gate:

- **`### Blast radius`** — for each invariant the Recommended approach adds, removes, or weakens: the invariant in one line, then the enumerated sites (file:line) where it is observable or assumed, grouped by kind (source logic / logs / traces / metrics / error text / docstrings-comments / deployment manifests or charts / customer docs / internal docs / tests), each with the grep pattern used as evidence. "None found" is an acceptable entry only with the pattern that was tried.
- **`### Policy decisions this change implies`** — yes/no questions the body leaves open whose answer changes the sweep (e.g. "Is `<value>` a secret once `<change>` lands? If yes: redact from logs/spans/metrics/task names/error text; if no: document that it is not."). The Analyst recommends an answer for each; the orchestrator surfaces them in the Section 3 preamble so the user approves the design AND the policies in one gate.

The Engineer dispatch prompt embeds both sections alongside the Recommended approach, so implementation is one round. Reviewers check the diff against the Blast radius list (a site on the list not addressed is a finding; a site not on the list is a finding against the Analyst pass, not a new fix round).

## Suggested fix

1. `agents/analyst.md`: add the two sections to the return-shape contract with the grouping/evidence rules above; extend "Why this role exists" with the churn rationale.
2. `skills/quo-fix-issue/SKILL.md` Section 3: include both sections in the surfaced proposal (not stripped like `### Deferred refinements`); add the policy decisions to the verdict preamble; carry both into the Section 4 Engineer directive block and into the Section 5 reviewer dispatch prompts as the checklist.
3. Consider the same for `/quo-execute`'s design inputs where a Subtask removes or weakens an invariant.

## Related

- Sibling Issue: strict lane sequencing (Engineer → code review until clean → Test Writer + Doc Writer once) — same reference run.
- Sibling Issue: routing table sends every multi-path finding to a user gate.
- Sibling Issue IDs: b.pdq (lane sequencing), b.nn8 (routing table default). Reference run: event_consumer_service b.239, 2026-09-02.
## Amendment (2026-09-02, after the reference run completed)

**Scope-split recommendation is part of the Analyst's job.** When the Blast radius sweep surfaces a concern that is distinct from the Issue's stated defect (on the reference run: "the reconnect token becomes a bare bearer capability once the principal hash is gone" was distinct from "durable-queue names must not embed identity"), the Analyst MUST recommend, in the proposal, whether to (a) fold it into this Issue or (b) file it as its own Issue and only *document* the property here. The orchestrator surfaces that recommendation at the Section 3 gate. On the reference run the reconnect-token concern drove ~4 of the 6 Engineer rounds and every second-round review finding; splitting it at the gate would roughly have halved the run and kept the naming Issue's diff reviewable.

**The sweep must cross into shared libraries the service depends on** (first-party dependencies the team owns and can change; the host repo's CLAUDE.md typically names them). The last blocker on the reference run — the raw token recorded on the `http.url` span attribute — lived in `../notification_common/rest/middleware/tracing_middleware.py`, not in the service.
## Amendment 2 (2026-09-03) — policy decisions must be grounded in the full request pipeline

On the reference run the team documented a value as "a secret / a bearer capability: anyone who presents it attaches" across 13 surfaces. The user corrected it: every request still passed an authentication step and a per-principal permissions filter, so the value was an *identifier* usable only by an already-authenticated principal, subject to its own permissions. The claim had been derived from the one mechanism the change removed, and every reviewer verified the claim's *consistency* across surfaces rather than its *truth*. Add to the `### Policy decisions this change implies` contract: for any decision of the form "is X a secret / what does holding X grant?", the Analyst MUST enumerate the gates a request passes (authn, coarse authz, per-principal filters, per-principal caches) with file:line evidence and state what remains true after them; the Recommended approach must use that precise phrasing (e.g. "any authenticated principal that obtains X can …, subject to its own permissions") rather than "secret"/"capability". Reviewers check the claim against the enumerated gates, not against the other surfaces.
## Amendment 3 (2026-09-03) — lifecycle axis for the blast-radius sweep; Engineers return design questions instead of inventing mechanisms

Source: the retrospective of the `/quo-fix-issue b.pdq` run (six rounds; round 1 fixed the Issue, every later round fixed the previous round). Roughly three of those rounds were the *abort lifecycle* of a new TaskList name class being designed piecewise by review: each round found the one leg (create / consume / close-out) of one lifecycle in one scope (fix mode, execute Subtask, Task, Bee, post-completion) that the previous fix had missed.

1. **The `### Blast radius` sweep gains a lifecycle axis.** For every new state, TaskList name class, gate, or marker the Recommended approach introduces, the Analyst MUST name its **create site, consume site, and close-out site in every scope the change touches and on every exit path** (normal completion, cancel, abort, harness compaction), with file:line evidence for the sites that already exist and an explicit "new" for those the change adds. A lifecycle with a missing leg in any scope is a design gap the Analyst reports at the gate, not something reviewers discover one leg per round.

2. **Engineers must not invent mechanisms.** Add to `agents/engineer.md` (fix mode and execute mode) and to the Section 4 Engineer directive block: when a finding or directive cannot be implemented without introducing a new state, name class, gate, or marker that the Analyst's proposal did not enumerate, the Engineer returns the design question in its report instead of choosing — the orchestrator routes it through the design gate (or the mechanism-introducing-finding rule in sibling Issue b.nn8). On the reference run an Engineer added an exemption keyed on `metadata.activity` unprompted; it became the next round's blocker.

3. **Convergence is a stated goal of the review lane.** Pair the "state what the change newly exposes" second-order ask (landed by b.pdq) with: "prefer the smallest change that makes the text internally consistent, and tag any finding whose fix requires new machinery as `introduces-mechanism`." The tag is consumed by b.nn8's routing rule.
## Amendment 3 — clarification (2026-09-03): the contract must be written for code projects

Amendment 3 above was drafted from a prose-repo run and uses this repo's vocabulary ("TaskList name class", "text internally consistent"). The shipped contract in `agents/analyst.md` and `skills/quo-fix-issue/SKILL.md` MUST be phrased stack- and project-neutrally (design rule 1). Concretely: a "mechanism" is any new state, configuration surface (flag, env var, setting), persisted or wire field, background task, exception or error type, metric/log/trace attribute, name or identifier class, gate, or retry/fallback path. Its **lifecycle** is where it is created or initialized, where it is read or consumed, where it is mutated/invalidated/migrated, where it is torn down or removed, where it is observable (logs, spans, metrics, error text), and where it is documented — across every surface the change touches (service, CLI, API, tests, deployment manifests, docs). "Internally consistent" means the codebase compiles/passes and every surface agrees with the invariant, not merely that prose agrees with itself. This repo's runs are one worked example; the b.239 Python-service run (redaction across 13 surfaces; validation spreading to every API surface; a new log line adding a new exception path) is the primary one.

## Deferred from /quo-fix-issue run (2026-09-04 01:30)

**From b.pdq (landed): wire the reviewer's diff-verification against `### Blast radius` once this Issue adds that section.** b.pdq shipped the Engineer half of Amendment 2's check — `agents/engineer.md` now requires sweep-completeness evidence (patterns run, every hit, per-hit disposition) and a `## Files changed` list on every return, and `skills/quo-engineer-review/SKILL.md` check category #8 verifies the diff against that list when the invocation supplies it (the orchestrators and `agents/pm.md` / `agents/code-reviewer.md` relay it under `## Engineer's completeness evidence`). The Blast-radius half was deliberately not wired because no role file emits `### Blast radius` yet. `agents/engineer.md` carries the seam this Issue plugs into: "When the dispatch prompt carries an enumerated site list — a set of sites some upstream analysis already identified — reconcile your own list against it and account for every entry." When implementing this Issue:

1. Embed the Analyst's `### Blast radius` list in the Section 4 Engineer dispatch prompt as that enumerated site list, so the Engineer's completeness evidence reconciles against it.
2. Embed it alongside `## Engineer's completeness evidence` in the Code Reviewer and PM dispatch prompts (fix mode: `skills/quo-fix-issue/SKILL.md` Phase A Code Reviewer dispatch and Phase C PM dispatch; execute mode: `skills/quo-execute/SKILL.md` per-Task PM dispatch and Bee-level Code Reviewer / `pm-<bee-id>` dispatch), and have `agents/code-reviewer.md` / `agents/pm.md` relay it into their `/quo-engineer-review` invocations the same way they relay the completeness evidence.
3. Extend `skills/quo-engineer-review/SKILL.md` check #8 so the diff is verified against both lists: a Blast-radius site not addressed and not dispositioned in the Engineer's evidence is a finding against the Engineer; a site in the diff that is on neither list is a finding against the Analyst pass (report it as a list gap, not a new fix round).

## Post-completion observations for the consolidation pass

Recorded at the 2026-09-08 close-out of this Issue's `/quo-fix-issue` run, under the ignored-feedback rule. Each item was a coverage-only or cosmetic review observation that the operator directed be deferred rather than looped once the test lane had run thirteen review rounds without a defect in the shipped contract. None changes shipped behavior.

1. **Test coverage — the Revise light-feedback shortcut is unpinned.** `skills/quo-fix-issue/SKILL.md` Section 3's Revise branch says the orchestrator may "capture the original directive sections per the Approve branch above, plus the user's clarification" (this Issue widened it from "the original Recommended approach"). No test in `tests/test_blast_radius_contract.py` pins that sentence; a revert to the single-section wording passes the suite. Impact is bounded because the sentence routes into the Approve branch, whose three-section enumeration is pinned. A one-assertion test scoped to the paragraph anchored on "When the user's feedback is light enough to incorporate" (unique in the file) would close it. (Test review round 13, nit.)

2. **Test-guard boundary — attribution by segment.** `test_design_question_rung_introduces_no_machinery_of_its_own` splits the design-question rung into segments on `.`, `:`, `!`, `?`, and line breaks, and flags any segment naming a `gate-*` task or `AskUserQuestion` that does not also name Section 3. A minted token placed inside the rung's existing ~1000-character first bullet, which names Section 3 several times, still borrows attribution and passes. Both the Test Writer and the Test Reviewer adjudicated this as an accepted boundary: the only narrowing (splitting on `—` or `;`) would strand the rung's legitimate "reuses Section 3's gate" phrasing into its own segments and fail correct prose. The boundary is recorded in the `SENTENCE_SPLIT` comment; a realistically shaped drift (a new bullet or sentence) is caught. (Test review rounds 4 and 5.)

3. **Pre-existing prefix-only heading citation.** `skills/quo-fix-issue/SKILL.md` Section 3's surfacing paragraph cites `agents/analyst.md` `## Structured-output contract`; the actual heading is `## Structured-output contract (Analyst → orchestrator)`. Both the heading's parenthetical and the prefix citation predate this run (present at the branch point), the reference resolves unambiguously, and sixteen code-review rounds passed it. The SDD's own citation was tightened to the exact heading; the shipped one was left as a pre-existing cosmetic reference outside this Issue's diff. (Doc Writer observation, round 12.)

4. **Deferred coverage items already addressed in-run without a dedicated review round** (listed for the record): pinning the empty-list paragraph's closing licensed-check clause; paragraph-scoping the empty-list test; pinning the producer's emit-condition for the Blast-radius fixed empty line. Each got one writer pass under the operator's nit rule and was verified by the following round's full review.
