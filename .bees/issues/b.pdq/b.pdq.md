---
id: b.pdq
type: bee
title: 'Sequence lanes strictly: Engineer + code review to clean before Test Writer / Doc Writer run once; ask reviewers for second-order effects'
tags:
- process
- quo-fix-issue
- quo-execute
parent: null
reference_materials: null
created_at: '2026-09-02T20:22:55.360353'
status: done
schema_version: '0.1'
guid: pdqp21jwfhrrmau3crp3xzwmiubkez8v
---

## Description

`/quo-fix-issue` Section 4 dispatches the implementer lanes (Engineer, Test Writer, Doc Writer) against one Issue and Section 5 dispatches all reviewers once the implementers return. The reconciliation loop then re-dispatches whichever lanes have findings. Two structural problems:

1. **Test Writer and Doc Writer run against a source tree that can still change.** The Doc Writer reads the Engineer's diff as its work signal, and the Test Writer pins the Engineer's behavior. When a code-review round then changes the source (which is the normal case — code review exists to find things), every doc and test written against the previous diff is rewritten. Nothing in the skill forbids running docs/tests concurrently with a not-yet-clean source, and the orchestrator has no rule telling it to wait.
2. **Reviewers are not asked for second-order effects.** Each reviewer is scoped to "the diff". A fix's consequence (a new log line that can raise; a redaction that changes a metric label; a validation that moves before a log statement) is only visible after the fix lands, so it costs a full extra round to surface.

## Reference run (worked example)

event_consumer_service Issue b.239, 2026-09-02:

- Doc Writer ran 3 times (r1 against Engineer r1; r2 after Engineer r2–r3 changed validation/logging; r3 after Engineer r4 renamed span/metric attributes and added redaction). Test Writer ran 3 times and once **stopped mid-run** with "a concurrent Engineer round landed in the source mid-session … pinning tests to half-landed behaviour would produce assertions that are wrong within minutes" — after the orchestrator had explicitly promised it a stable tree. The Test Writer also once ran `git checkout -- <file>` on a source file during a discrimination experiment, transiently discarding an Engineer's uncommitted change (restored, but avoidable).
- Code Review r2 found that the create log line added in Engineer r2 could raise `AuthenticationError` on a lapsed token after the queue was declared — a direct second-order effect of the r2 fix that the r2 Engineer could have been asked to consider.

## Expected behavior

- **Sequencing rule in Section 4/5:** Engineer → Code Reviewer, loop until the Code Reviewer returns clean (or the orchestrator explicitly accepts the remaining findings into the ledger). Only then dispatch Test Writer and Doc Writer, in parallel, once. Then Test Reviewer + Doc Reviewer + PM. A Test/Doc reviewer finding that requires a *source* change re-enters the Engineer → Code Reviewer loop first, and only then re-dispatches the affected writer.
- **Writers get a stability guarantee the orchestrator can actually keep:** the dispatch prompt states the source tree is frozen for the duration of the writer's run, and the orchestrator MUST NOT dispatch an Engineer while a Test Writer or Doc Writer is in flight.
- **Writers never use `git checkout`/`git stash` on files outside their lane.** `agents/test-writer.md` should say discrimination experiments copy the file to the scratchpad and restore from the copy.
- **Reviewer prompts ask for second-order effects:** "For each change in the diff, state what it newly exposes, weakens, or can now fail — not only whether it is correct." Add to `agents/code-reviewer.md` and the `/quo-engineer-review` skill output contract as a required subsection.

## Suggested fix

1. `skills/quo-fix-issue/SKILL.md` Section 4 "Reconcile" step and Section 5: replace "dispatch every implementer whose gating precondition is met" with the ordered lane rule above; add the no-Engineer-while-writer-in-flight invariant to the reconciliation loop's Reconcile step.
2. `agents/test-writer.md`, `agents/doc-writer.md`: add the frozen-tree assumption and the no-`git checkout`-on-source rule.
3. `agents/code-reviewer.md` + `skills/quo-engineer-review/SKILL.md`: add the second-order-effects subsection.
4. Mirror in `/quo-execute` where the same hub-and-spoke loop is used per Subtask.

## Related

- Sibling Issue: Analyst blast-radius sweep + implied policy decisions (front-loading removes most of the rounds this Issue makes cheaper).
- Sibling Issue IDs: b.q3f (Analyst blast-radius sweep), b.nn8 (routing table default). Reference run: event_consumer_service b.239, 2026-09-02.
## Amendment (2026-09-02, after the reference run completed)

**Evidence both ways.** Rounds 1–4 of the reference run ran the Test Writer and Doc Writer concurrently with Engineer rounds: docs were rewritten three times and the Test Writer aborted once. Rounds 5–6 followed the rule proposed here (Engineer alone → Code Reviewer → Engineer → Code Reviewer): zero writer rework. The explicit "second-order effects" request added to the round-4 Code Reviewer dispatch is what found the remaining trace-sink blocker.

**The second-order check must extend into shared libraries** the service depends on (here `../notification_common`), not only the service diff — the reviewer found the `http.url` sink only when the dispatch prompt asked for a whole-change-set second-order verdict.
## Amendment 2 (2026-09-02) — Engineer completeness evidence on sweep-type directives

Sequencing removed rework but did not shorten the round count on the reference run: Engineer rounds 4, 5, 6 and 7 each closed "the last" redaction site and each declared the sweep complete, and each was then shown one more site by the next review. When a directive includes a sweep (every site an invariant touches — see the sibling Analyst ticket), the Engineer's deliverable MUST include a **completeness check with evidence**: the search patterns run, every hit, and for each hit either the change made or the reason it is deliberately untouched. The reviewer verifies the diff against that list (and against the Analyst's Blast radius list) instead of rediscovering sites from scratch, so an incomplete sweep is caught as a list gap in one round rather than as a new finding per round. Add to `agents/engineer.md` (fix mode and execute mode) and to the Code Reviewer's checklist.
