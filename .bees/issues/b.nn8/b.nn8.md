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
status: open
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

