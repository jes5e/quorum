---
id: b.21w
type: bee
title: 'b.q3f follow-on: when the agents/analyst.md mechanism definition lands, flip b.nn8''s strict xfail and reconcile the citer set'
parent: null
reference_materials: null
created_at: '2026-09-04T08:38:00.695507'
status: done
schema_version: '0.1'
guid: 21ww9jfkj4hw57spqd6kgy7v9iswjzg8
---

## Description

b.nn8 shipped the **consumer** half of the `[introduces-mechanism]` reviewer tag described in b.q3f Amendment 3: the routing rule reads the tag (row 2 of the pick-then-route table in both orchestrators), `/quo-engineer-review` emits it with a convergence brief and a worked example, and `agents/code-reviewer.md` and `agents/pm.md` relay it. Four shipped artifacts point at "the mechanism definition in `agents/analyst.md`": `skills/quo-fix-issue/SKILL.md` part (a), `skills/quo-execute/SKILL.md` part (a), `skills/quo-engineer-review/SKILL.md`'s `[introduces-mechanism]` bullet, and `agents/code-reviewer.md`'s relay bullet. The **definition itself** is b.q3f's deliverable (its Amendment 3 clarification gives the stack-neutral enumeration: a new state, configuration surface, persisted or wire field, background task, exception or error type, metric/log/trace attribute, name or identifier class, gate, or retry/fallback path). Until b.q3f lands, the pointer dangles; the two post-completion prompt skeletons inline the enumeration and are unaffected.

When b.q3f lands, three things need to happen on this repo's side, in this Issue:

1. **Flip the strict expected-failure pin.** `tests/test_routing_decision_contract.py::test_analyst_role_carries_the_mechanism_definition_its_citers_point_at` is marked `@pytest.mark.xfail(strict=True, reason=…)` naming b.q3f. It anchors on the word `mechanism` plus enumeration vocabulary (`configuration surface`; `identifier class`; `retry` or `fallback`), not on a heading. The moment the definition lands the test XPASSes and fails the suite — remove the marker then. If b.q3f words the definition without those terms, the test stays XFAIL silently; check it is genuinely passing before removing the marker.
2. **Reconcile the citer set.** `MECHANISM_DEFINITION_CITERS` in the same test module lists the four citers above. `agents/pm.md`'s relay bullet deliberately does not cite the definition (a relayer relays, it never judges; adding a fifth pointer widens the dangle). If b.q3f decides the PM should cite it, extend the list to five in the same change.
3. **Confirm the operator's placement direction held.** The operator directed that the definition live once, in `agents/analyst.md`, and be referenced from the routing prose. b.nn8's one recorded departure: the two post-completion prompt skeletons inline the enumeration because they are dispatched to a fresh Agent in the target project repo, where `agents/analyst.md` does not exist (recorded in the b.nn8 tracker as Compromise 2 and in `docs/sdd.md`). Leave that as is unless b.q3f changes the skeletons' contract.

## Current behavior

Four shipped pointers resolve to a file with no mechanism definition; one test is a deliberate strict xfail; `docs/sdd.md` and `docs/prd.md` state the dependency explicitly.

## Expected behavior

After b.q3f: the pointers resolve; the xfail marker is gone and the test passes; the citer list matches the actual set of citing artifacts; docs no longer say the definition is pending.

## Impact

Until then, the reviewer-side tagging criterion and the orchestrator-side detection fallback for row 2 resolve to nothing except the phrase "requires new machinery"; the post-completion challenge (PHASE 3 axis (ii)) is unaffected.

## Suggested fix

Work this Issue immediately after b.q3f merges. Files: `tests/test_routing_decision_contract.py` (remove the marker; adjust `MECHANISM_DEFINITION_CITERS` if needed), `docs/sdd.md` and `docs/prd.md` (retire the "not present until b.q3f lands" wording in the b.nn8 entries), and `agents/pm.md` only if b.q3f decides the PM cites the definition.

## Decisions and rejected alternatives

- The b.nn8 Analyst's destination for this item was `defer-to-existing-ticket-body: b.q3f`. It was filed as a new Issue instead because b.q3f is being worked in a concurrent worktree; editing its ticket file from the b.nn8 branch would produce a merge conflict on `.bees/issues/b.q3f/b.q3f.md`.
- A plain (non-xfail) pin was rejected in b.nn8 because it would leave that branch's suite red on a deliverable it does not own; the strict xfail fails closed in both directions.

## Related

- b.q3f (open): owns the definition (Amendment 3 and its clarification). This Issue depends on it.
- b.nn8 (landed): consumer half; the strict xfail; Compromise 2.
