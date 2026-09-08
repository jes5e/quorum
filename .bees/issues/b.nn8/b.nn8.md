---
id: b.nn8
type: bee
title: Routing table gates every multi-path finding; default to orchestrator picking the highest-quality path, gate only re-architect/scope
tags:
- process
- quo-fix-issue
- quo-execute
- routing
parent: null
reference_materials: null
created_at: '2026-09-02T20:22:55.435746'
status: done
schema_version: '0.1'
guid: nn8fqmxghiy55q5ncjmt1w6popxb16s9
---

## Description

The "Orchestrator discipline: routing review findings" table in `/quo-fix-issue` (and its mirror in `/quo-execute`) routes every finding with **more than one fix path** to a user gate (`AskUserQuestion`), regardless of depth. In practice reviewers almost always enumerate two or three paths (a trivial narrowing, a proper fix, sometimes a re-architect), with `[preferred]` on one of them. The table therefore turns most substantive findings into a user prompt whose answer is an engineering call the orchestrator already has the context to make.

## Reference run (worked example)

event_consumer_service Issue b.239, 2026-09-02. After the first review round the orchestrator fired one `AskUserQuestion` with three multi-path findings (test-ordering pin scope: 3 paths; runbook honesty vs. adding a log field: 2 paths; fix-a-comment vs. enforce validation everywhere: 3 paths). The user rejected the prompt: *"I have no idea what you're talking about - what's the best approach to fixing this - remember that we don't care about how much work, we care about best quality outcome."* The orchestrator then picked the most complete path for each and proceeded; the outcomes were uncontroversial.

The gate cost a turn, produced no information the orchestrator lacked, and asked the user to acquire context they did not want.

## Expected behavior

Routing defaults to **orchestrator judgment toward the highest-quality path**, with a user gate only where the decision is genuinely the user's:

| Condition | Routing |
|---|---|
| Any number of paths, max depth `trivial-tweak` or `refactor-locally` | Orchestrator picks the highest-quality path (prefer the reviewer's `[preferred]` when it is also the most complete; when the reviewer's `[preferred]` is a narrowing and a fuller path exists at `refactor-locally`, pick the fuller path). Record choice + rationale in the compromise tracker (new `Decision` value: `Orchestrator picked path (x) — highest-quality`). No gate. |
| Any path tagged `re-architect` that the orchestrator would pick | User gate (design direction). |
| The fuller path changes public API/contract behavior beyond the Issue's stated scope, or is a breaking change | User gate (scope). |
| Finding without depth tags / malformed tags | Unchanged: treat as `re-architect` → gate. |

Rationale: effort is never the tiebreaker (see the user quote); the user reserves gates for design-direction and scope decisions. The compromise tracker + post-completion review already provide the challenge surface for an orchestrator pick that turns out wrong.

## Suggested fix

1. Replace the `(num-paths, max-depth)` table in `skills/quo-fix-issue/SKILL.md` "Orchestrator discipline: routing review findings" (a) and the routing-decision gate (d) with the table above; keep the scope-bounding gate (c) as the *only* narrowing path (the orchestrator must never narrow silently), and keep the tracker append triggers, adding the new `Decision` value to the tracker entry shape.
2. Mirror in `skills/quo-execute/SKILL.md`.
3. Update the post-completion reviewer prompt (Section 8) so PHASE 2/3 challenge `Orchestrator picked path` entries the same way they challenge auto-routes.

## Related

- Sibling Issues from the same run: Analyst blast-radius sweep; strict lane sequencing.
- Sibling Issue IDs: b.q3f (Analyst blast-radius sweep), b.pdq (lane sequencing). Reference run: event_consumer_service b.239, 2026-09-02.
## Amendment (2026-09-03) — mechanism-introducing findings are design changes, not fixes

Source: the retrospective of the `/quo-fix-issue b.pdq` run. Of ~35 findings after round 1, only a handful concerned what the Issue asked for; the rest concerned machinery that did not exist when the run began (a report receiver, an `aborted-*` marker, an unexplained-movement gate, per-scope close-outs, naming in two more scopes). Each new mechanism has a lifecycle across four or five scopes, so each one generated further rounds. The routing table routes by fix-path count and depth and has no notion of "this fix adds a mechanism."

1. **New routing condition.** A finding whose preferred (or only) fix path introduces a new state, TaskList name class, gate, or marker — reviewer-tagged `introduces-mechanism` per b.q3f Amendment 3, or detected by the orchestrator when the fix path names one — is routed to the **scope-bounding gate** (Fix properly now / Defer to follow-up Issue / Accept the limitation) regardless of depth tag, with **Defer to follow-up Issue as the recommended default** when the mechanism serves a case the Issue body never mentioned. The follow-up Issue carries the reviewer's sketched design verbatim so nothing is lost. Under this rule the reference run would have closed around round 2 with two or three follow-up Issues instead of six rounds.

2. **"Highest quality" is defined for the orchestrator.** When picking among fix paths, highest quality means the smallest change that leaves the text or code internally consistent and complete for the Issue's stated defect — total-system complexity counts against a path. "Adds a mechanism" is a reason to defer, not a reason to build; effort is still never the tiebreaker between paths of equal completeness. The orchestrator on the reference run read "highest quality" as "structurally complete every time" and about ten refactor-locally choices each spawned a round of scope variants; encode the definition in the routing prose so it does not depend on orchestrator judgment.

3. **Mirror in `/quo-execute`**, as the base Issue already requires for the routing table.
## Amendment — clarification (2026-09-03): stack-neutral wording

The mechanism-introducing-finding rule above must be phrased for code projects in the shipped routing prose (design rule 1): "introduces a mechanism" means the fix path adds a new state, configuration surface, persisted or wire field, background task, exception type, metric/log/trace attribute, identifier class, gate, or retry/fallback path that the Analyst's proposal did not enumerate. "Smallest internally-consistent change" means the smallest change under which the code compiles, tests pass, and every surface agrees with the invariant the Issue names — prose consistency is the degenerate case for prose repos like this one. The b.239 Python-service run is the primary worked example; this repo's b.pdq run is the secondary.

## Deferred from /quo-fix-issue run (2026-09-04 01:30)

**From b.pdq (landed): three coherence checks on the same section, deferred here because b.pdq kept parts (a)–(f) textually untouched for you.** b.pdq added a new part **(g)** to `### Orchestrator discipline: routing review findings` in BOTH orchestrator skills — when a finding's chosen fix path changes source, the re-dispatch is ordered (Engineer → code review for that site → the affected writer), never concurrent, with the Engineer-dispatch freeze as a TaskList name-prefix + status precondition. It also added a shared aborted-unit close-out in each skill (`skills/quo-fix-issue/SKILL.md` `#### Aborted-Issue close-out`; `skills/quo-execute/SKILL.md` `##### Aborted-run close-out`) that both the unexplained-movement gate's Abort and `/quo-fix-issue` Section 3's Analyst-gate Cancel route through. When rewriting (a) and (d):

1. **Route the new `Orchestrator picked path` decision through part (g), not around it.** Whatever path the orchestrator picks, if it changes source the dispatch must follow (g)'s ordering. State that in the rewritten table's routing column or in (g)'s lead sentence, whichever reads as the single rule.
2. **Refresh part (g)'s cross-references.** It currently cites "part (a)" (the auto-dispatch row) and "the gate in part (c) or (d)"; after the rewrite confirm those referents still exist and still mean what (g) assumes. Also re-read `skills/quo-engineer-review/SKILL.md`'s compatibility constraint ("the numbered list stays the sole routing surface, so `(num-paths, max-depth)` remains the orchestrator's only parse input") — depth tags survive your table, so the constraint survives in substance, but its wording names the old tuple.
3. **Route part (d)'s `Cancel` option through the shared aborted-unit close-out.** Today (d)'s `Cancel` "aborts the current Issue's fix run (proceed to the next Issue in batch / `all` mode, or end cleanly if none remain)". That exit predates the close-out and skips it: it does not sweep `aborted-*` markers, does not run Section 7.5's deferral-hygiene gate, and does not run the Issue-boundary state-externalization checkpoint on its aborted path or the batch-mode context-window guard. Point (d)'s `Cancel` at `#### Aborted-Issue close-out` (and its `/quo-execute` mirror at `##### Aborted-run close-out`) so all three abort routes behave identically. The b.pdq `### Feature:` entry in `docs/sdd.md` names the two routers that exist today; add the third when you land this.

## Amendment (2026-09-08) — operator directives applied during the fix run, and decisions ratified at post-completion review

The fix landed with these behaviors that the body above does not name. They are recorded here so the ticket carries them, not only the PRD and SDD.

1. **Both gates are severity-aware; a `blocker` can never be accepted, and can be deferred only with a narrowing.** Operator directive, refined at the post-completion review (2026-09-08). `Accept the limitation` is unreachable for a blocker unconditionally. `Defer to follow-up Issue` is reachable for a blocker only when both hold: the fix the finding needs introduces a mechanism (the `[introduces-mechanism]` tag or the orchestrator's reading against the definition in `agents/analyst.md`), **and** that mechanism serves a case outside the Issue's stated defect, so the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships. The deferral is paired with the narrowing in the same round and never shipped alone; the narrowing is dispatched directly (not re-entered into the routing table, which would loop through row 4) and recorded in the compromise tracker's Trigger A entry. **Guard:** a narrowing may never reduce coverage of the stated defect — when the blocker cannot be made inapplicable to what ships without leaving the stated defect partly unfixed, it is in scope and takes `Fix properly now` or the Analyst re-dispatch, never `Defer`. Otherwise a blocker gets exactly two choices: in `/quo-fix-issue`, `Fix properly now` or `Re-dispatch the Analyst with this finding` (reusing Section 3's Revise-branch re-dispatch — which makes Section 3's approval gate reachable from Phase A and Phase C, so on Approve the orchestrator marks any in-flight writer, reviewer, and PM lanes `completed`, discards their findings as raised against a superseded directive, and re-enters Phase A against the current tree, and the aborted-Issue close-out reads the tree rather than assuming it clean; the routing-decision gate offers the enumerated paths plus the Analyst re-dispatch plus `Cancel`); in `/quo-execute`, which has no Analyst, `Fix properly now` or `Cancel` through the shared aborted-run close-out. The PM's traceability pass and the post-completion reviewer's PHASE 2 treat a blocker that was accepted, a blocker deferred without a narrowing record, or a blocker deferred with a narrowing that leaves the stated defect partly unfixed as a `blocker`. An earlier reading of the directive (Defer unreachable for every blocker) was applied first and drove most of this run's review rounds; the post-completion review's under-enumeration challenge to an earlier gateless-dispatch shape in `/quo-execute` was also accepted and that shape removed.
2. **The `[introduces-mechanism]` reviewer tag ships here, emitter and consumer.** Operator directive. `/quo-engineer-review` emits it with a convergence brief; `agents/code-reviewer.md` and `agents/pm.md` relay it; row 2 of the routing table consumes it as the primary signal, with orchestrator-side detection as the fallback. The stack-neutral **mechanism definition lives once, in `agents/analyst.md`**, written by the concurrent b.q3f change; shipped prose points at it. The one recorded departure: the two post-completion reviewer prompt skeletons inline the enumeration, because their reader is a fresh Agent in the target repo where the role file does not exist. Follow-on b.21w flips the strict expected-failure test pin when the definition lands.
3. **The orchestrator's pick is always one of the paths the reviewer enumerated.** During the run Step 1 was widened to let the orchestrator compose a fix path when no enumerated path was the smallest internally-consistent complete change (surfaced by the PM because this run's own tracker had already done so twice). The post-completion review challenged that as an authority extension beyond this Issue's table, and the operator directed it **stripped** (2026-09-08): an incomplete menu now routes the most complete enumerated path through the table like any other pick — rows 2, 3 and 4 send it to the scope-bounding gate, where `Fix properly now` dispatches the complete fix; the exception is a finding whose depth tag is absent or malformed, which row 1 sends to the routing-decision gate (no `Fix properly now` there; the user picks among the paths as emitted) — and the incomplete menu becomes visible through the gate fire and, on a deferral, a Trigger A entry, which is what reaches the post-completion review. The stripped design is filed verbatim as **b.kxx** for the operator to decide as policy.
4. **The PM's Final report carries a unit-scoped deferred-blocker check** over the run's compromise tracker (path passed in the PM dispatch prompt), reporting an in-scope violation as a `blocker` and naming an earlier unit's as a pre-existing report note. Operator directive (the PM traceability pass was named explicitly). The post-completion reviewer noted the unit-boundary checkpoint could host the check with no PM contract change; **kept at the PM site as directed**, alternative recorded in the run's tracker.
5. **The three-round review cap set for the run was exceeded** (16 code-review rounds before the first close-out, plus post-completion fix rounds) because open blockers had no Defer route under the first reading of item 1; every round was a fresh cold full-diff pass.

Follow-ups filed from this run: b.262 (tracker vocabulary and enum hygiene; extended with the gate-(d) audit gap and the unpinned byte-matched strings), b.isi (post-completion review at high tracker volume), b.egb (repo-governance hygiene, rule 3; extended with the SDD checkpoint-invoker count), b.21w (b.q3f follow-on), b.kxx (composed-path design decision), b.8ub (Section 3 `Cancel` vs 7.5 Step 0 on banking the Analyst's deferred refinements).

## Post-completion observations for the consolidation pass

Recorded verbatim from the second post-completion review (over commit c9b1651, 2026-09-08). On the operator's direction these three are **not** routed through the SR-6.7 recovery gates and are **not** acted on by this run; they are accepted as observations for an upcoming whole-skill consolidation to judge. Each is also recorded in the run's compromise tracker with that rationale.

**1. `[compromise-challenge]` `suggestion` — three of this run's picks were orchestrator-*composed* paths, and one of them ships, under a rule the diff itself now forbids.**
Compromise tracker entries 8, 9, 31 · artifact at `tests/test_routing_decision_contract.py` (the strict `xfail` on the `agents/analyst.md` mechanism definition).
Compromise 8 picked "(c) (orchestrator variant, not enumerated by the reviewer)"; Compromise 9 applied (a) **and** (b) together; Compromise 31 picked an orchestrator-authored `xfail(strict=True)` variant. The shipped Step 1 (`skills/quo-fix-issue/SKILL.md`, `skills/quo-execute/SKILL.md`) now reads **"The pick is always one of the paths the reviewer enumerated."** Compromises 8 and 21's machinery were stripped on the operator's direction (Compromise 43), but Compromise 31's composed path was never re-decided under the landed rule — its artifact is in the diff. Under the landed rule it would route to gate (c) via row 4 and reach the same place through `Fix properly now`, so the *substance* is defensible; the *authority* was the one the operator revoked. This is also the clearest PHASE 4 evidence in the run: three separate findings where the reviewer's menu had no complete option.
- (a) [depth:trivial-tweak] [preferred] Note the three composed picks in the b.nn8 body's 2026-09-08 amendment item 3 alongside the "stripped" record, so the ticket does not read as though the rule was honoured throughout. No code change.
- (b) [depth:trivial-tweak] Re-run Compromise 31's decision through the landed table (row 4 → gate (c)) and record the answer.
- (c) [depth:refactor-locally] Revert the xfail to the reviewer's enumerated path (a) and accept a red branch until b.q3f lands. **Not recommended** — it trades a documented gap for a broken suite.

**4. `[compromise-challenge]` `suggestion` — Compromise 44 was self-approved on the operator's behalf, and axis (ii) applies to it.**
Compromise tracker entry 44 · `agents/pm.md` (the unit-scoped deferred-blocker check), the `<compromise-tracker-path>` placeholder at the PM dispatch sites in both orchestrators.
The post-completion reviewer's `[preferred]` was to host the deferred-blocker check at the unit-boundary checkpoint (which already reads the tracker, is orchestrator-owned, and needs no PM contract change). The orchestrator kept the PM site and recorded `Decision: User accepted under-enumeration after post-completion challenge` while the Rationale says "self-approved by the orchestrator on the operator's behalf". Under PHASE 3 axis (ii) the kept path **did** introduce machinery the Issue body never enumerated: a new `<compromise-tracker-path>` dispatch placeholder threaded through three dispatch sites, a run-vs-unit scoping split, a "report note, not a finding" class, and a shim exemption. I judge the substance defensible — the PM site is the only one that produces a *routable* finding, which the checkpoint cannot — but the mechanism should have been named as such at the gate rather than after the fact.
- (a) [depth:trivial-tweak] [preferred] Keep as shipped; record the mechanism explicitly in the tracker entry's Rationale so PHASE 3 axis (ii) has something to read.
- (b) [depth:refactor-locally] Move the check to both boundary checkpoints and drop the placeholder, scoping split, and shim exemption.
- (c) [depth:trivial-tweak] Put the choice to the operator now, before merge.

**8. `[design]` `nit` — the boundary checkpoint's tracker verification now depends on recalling the run's own routing decisions.**
`skills/quo-execute/SKILL.md` (Epic-boundary checkpoint tracker bullet), `skills/quo-fix-issue/SKILL.md` (Issue-boundary checkpoint tracker bullet).
Rewritten to *"do not read an absent file as the expected state; read it as 'nothing was appended', and check that against what this Epic actually did."* That check requires the orchestrator to remember which ungated picks it made — a value carried nowhere on disk — at precisely the boundary where a compaction is expected. The memory dependency is pre-existing, but it was near-vacuous when the tracker was rare and is now load-bearing on most runs.
- (a) [depth:trivial-tweak] [preferred] Scope the check to what *is* re-derivable, or state plainly that it is a best-effort pre-compaction check.
- (b) [depth:refactor-locally] [introduces-mechanism] Record ungated picks in the run-state manifest. **Defer** — new manifest field.

