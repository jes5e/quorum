---
id: b.tdq
type: bee
title: 'Prune the doc review skill by evidence: keep the checks saved reviews show working, cut the rest'
parent: null
reference_materials: null
created_at: '2026-11-09T11:23:00.616046'
status: done
schema_version: '0.1'
guid: tdq353es96afyo2bjua3vg4qu31dibnm
---

## Description

`/quo-doc-writer-review` is about 3,250 words. The check that should have caught live_edit's SDD mechanism sat in it for weeks and was never used in about 95 reviews (b.9ar). The more rules a skill carries, the less weight each one gets. The goal is a shorter review: the checks that do the work, stated where they're read, and nothing else.

The operator agreed on 2026-11-09 to do this by evidence rather than by taste. live_edit's saved doc reviews show which checks fire.

### Method

1. **Map every check to its findings.** List every check the review skill states today, and every one in `agents/doc-reviewer.md`. Using the saved live_edit doc reviews, count which checks produced a finding, how often, and whether the finding was acted on. The reviews are the `*doc-review*`, `*docreview*` and `postcomp-*` files in `~/.quorum-scratch`. Reviews written under older skill versions count against the current check that carries the same rule.
2. **Classify each check:**
   - **(a) Fires and works.** Keep it, and move it near the top if it's buried.
   - **(b) Never fires.** Is it one of CLAUDE.md's protected kinds (a contract another agent keys on, state, a structural guard, operator policy)? If so, keep it. If not, ask whether any run shows the case arising and being handled without the check. If yes, it's a deletion under CLAUDE.md's rule. If the case never arose, it's a candidate: list it for the overseer and operator with its reason.
   - **(c) Duplicates another check or the writer's file.** Keep one home.
   - **(d) Generic review boilerplate the agent would do anyway.** Candidate to cut.
3. **Leave alone:**
   - b.9ar's text (the SDD test, and the growth list), which is untried;
   - the output contracts: the work-item shapes, the trailers, the `Confirming pass:` line, the `### Scope` section other skills cite;
   - anything a test pins, unless the pin goes for a recorded reason.

Two prior cleanup candidates fit here: the review's "Work item quality" list and its README-era clean line.

### Scope

`skills/quo-doc-writer-review/SKILL.md` and `agents/doc-reviewer.md` only. The same method applies later to the code and test reviews and the orchestrators, each as its own batch, if this one works.

## Process

One hand-edit batch:
- Checkpoint 1: the evidence table and the cut list, with no edits.
- The operator approves the candidate list.
- The draft, then one cold review under the exit rule.

The expected outcome is a net cut, with every deletion carrying its evidence in the commit.

## Closed (2026-11-09)

Merged by fast-forward to `4ac2dde`: `2eadb93` the prune, `4ac2dde` the round-1 nit. The cold round approved, and the lane closed under the exit rule. The work was Worker 1's; checkpoints are `~/.quorum-overseer/btdq-checkpoint-1.md` to `-3.md`. Full test 601 passes, run by the overseer. Net shipped −608 words:

| File | Before | After |
|---|---|---|
| review | 3251 | 2739 |
| doc-reviewer wrapper | 676 | 580 |

### Evidence

- **Saved live_edit doc reviews:** 123, with 343 findings.
- **Post-completion sweeps:** 30, with 137 doc misses.
- **Where the findings came from:**
  - true and agrees: 169
  - appears once, with its reason: 49
  - customer-text test: 18
  - confirming-pass questions: 68
- **What the misses show:** they fall under checks that already exist, so nothing new was added.

### What was cut

Each cut's evidence is in `2eadb93`'s message.

| Item | What went | Why |
|---|---|---|
| K1, K5 | "Concise …"; steps 1 and 2 | Generic |
| K2, K7 | Loop-bounding text | Its reader has been gone since b.vtw: re-review follows the fix's `Kinds changed` |
| K6 | "Only return issues if very important" | The severity scale and the runs contradict it |
| K8 | The "Work item quality" list | |
| K9 | The README-era clean line | |
| K4 | Step 0a's git recipe | Compressed to its goal |
| K10 | The worked-examples block | A duplicate of Shape 1's examples (approved by the operator) |
| K11–K13 | The wrapper's cold-start, responsibilities and intro restatements | |

### Kept

Kept word for word:
- every check that fired;
- the contracts and pins;
- b.9ar's text;
- the severity scale;
- the confirming pass.

The checks that fire now sit higher in the skill.

### Validation

The cold reviewer replayed the newest real review, `doc-review-redisrs-e2-t14-r1.md`, against the pruned skill. Its three defects were still found.

### Next

The same method applies to `/quo-engineer-review` and `/quo-test-writer-review` and their wrappers, which carry the same cut text. It reaches live_edit at the next container rebuild.
