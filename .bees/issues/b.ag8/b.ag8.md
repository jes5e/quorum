---
id: b.ag8
type: bee
title: 'Relay the Analyst''s Blast radius and Policy decisions to the remaining consumers: /quo-engineer-review callers, Phase B writers, writer-review skills'
status: open
created_at: '2026-09-08T17:34:44.749573'
schema_version: '0.1'
reference_materials: null
guid: ag8hyuh6uj8jdhb1spyuo37rhut42nd4
---

## Description

Issue b.q3f added two unconditional sections to the Analyst's structured-output contract — `### Blast radius` and `### Policy decisions this change implies` — and wired `## Blast radius` through `/quo-fix-issue`'s Engineer dispatch, Phase A Code Reviewer dispatch, and Phase C PM dispatch into `/quo-engineer-review` check #8 (via `agents/code-reviewer.md` and `agents/pm.md`). Two consumer groups were left out of that chain, both surfaced by b.q3f's own code reviews and deferred because each needs a new relay heading or a new check, which is new machinery beyond b.q3f's stated defect.

## Current behavior

**Gap 1 — ratified policy answers reach the Engineer but neither `/quo-engineer-review` caller.** The operator ratifies every recommended answer in `### Policy decisions this change implies` at the Section 3 gate, and the section rides the directive into the Engineer dispatch. But only `### Blast radius` is relayed onward to the Phase A Code Reviewer and the Phase C PM. Both reviewers therefore inspect a diff that encodes user-ratified yes/no answers they cannot see, so neither can flag a diff that silently re-decides one — a gap that did not exist before b.q3f, because before it there were no ratified answers to drop.

**Gap 2 — the Blast radius's doc and test entries reach no role permitted to act on them.** `### Blast radius` is required to group sites by kind including customer docs, internal docs, and tests, but its only wired consumers are source-lane roles. b.q3f's interim rule: `agents/engineer.md` dispositions those entries to the Test Writer / Doc Writer lanes in its completeness evidence, and `/quo-engineer-review` check #8 never counts them against the Engineer (recording an undispositioned one under `### Second-order effects` as owed to the other lane). Net effect today: a correctly-dispositioned doc entry reaches neither the Doc Writer's dispatch prompt nor the per-issue summary, while an ignored one at least surfaces in the summary. The Phase B writers never receive the list.

## Expected behavior

**Gap 1 (sketch from b.q3f code review round 1, item 5):** a second relay heading (`## Policy decisions`) mirroring the `## Blast radius` chain across exactly the four sites the Blast radius relay already touches — `skills/quo-fix-issue/SKILL.md` Phase A Code Reviewer dispatch and Phase C PM dispatch, plus the forward-verbatim bullets in `agents/code-reviewer.md` and `agents/pm.md` — with a consuming check phrased mode-agnostically ("when the invocation supplies ratified design decisions, verify the diff does not re-decide them"). The PM is the spec-alignment role and is the more natural owner of the check; consider giving `agents/pm.md` the consuming clause and leaving `/quo-engineer-review` untouched if that reads smaller.

**Gap 2 (sketch from b.q3f code review round 5, item 1 path (b)):** relay `## Blast radius` to the Phase B Test Writer and Doc Writer dispatches in `skills/quo-fix-issue/SKILL.md`, and into `/quo-test-writer-review` and `/quo-doc-writer-review` via forward-verbatim bullets in `agents/test-writer.md`, `agents/doc-writer.md`, `agents/test-reviewer.md`, and `agents/doc-reviewer.md` (the same shape `agents/code-reviewer.md` / `agents/pm.md` use: forward the block under the same heading; forward no heading when none was supplied). Each writer-review skill gains a consuming clause scoped to its own kind-groups (tests for the test review; customer docs / internal docs for the doc review), mirroring check #8's asymmetric outcomes: a listed site in the reviewer's own lane left unaddressed is a finding against that writer; a diff-touched site on no list is a list gap in the narrative subsection, not a fix round. Keep one heading string (`## Blast radius`) at every hop, relay the fixed empty line rather than omitting the heading, and resolve the lane by the consuming skill's own scope definition rather than the upstream kind-group label — all three are load-bearing rules b.q3f established for the existing chain.

## Impact

Review rounds spent on sites the Analyst already enumerated (the churn b.q3f exists to remove) whenever the sites are doc or test sites, and no reviewer able to catch a diff that quietly reverses a policy answer the operator ratified.

## Suggested fix

Land both gaps in one pass — they touch the same relay sites and the same test module. Constraints carried from b.q3f:

- The "mechanism" definition has exactly one normative home: `agents/analyst.md`'s lifecycle-axis paragraph. Reference it; do not restate it.
- `agents/analyst.md` must not contain the string `quo-engineer-review` (a test pins the review's invoker set to `code-reviewer.md` and `pm.md`); adding invokers changes that test deliberately, not accidentally.
- `tests/test_blast_radius_contract.py` pins the relay hops, the fixed empty line's byte identity at every site, and the wrapper bullets' byte identity between `code-reviewer.md` and `pm.md`; extend those tests to the new hops rather than weakening them.
- Design the writer-lane relay once for both modes if Issue b.eid (the plan-path / execute-mode counterpart) lands a per-Task site list; the execute-mode Phase B analogue is the per-Subtask Test Writer / Doc Writer dispatch in `/quo-execute`.

## Background and rationale

Both gaps were surfaced by `/quo-engineer-review` during b.q3f's Phase A (rounds 1 and 5) and deferred at the orchestrator's routing gate under the operator's rule that a fix adding a new relay heading or check category is a follow-up Issue carrying the reviewer's sketched design, not work for the current Issue. Related: b.q3f (landed) — the producer and the fix-mode source-lane chain; b.eid (open) — plan-path producer and execute-mode consumers; b.nn8 (concurrent) — the `introduces-mechanism` reviewer tag and routing-table rewrite, unrelated to these relays.

