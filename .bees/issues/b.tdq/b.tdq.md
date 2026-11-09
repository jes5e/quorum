---
id: b.tdq
type: bee
title: 'Prune the doc review skill by evidence: keep the checks saved reviews show working, cut the rest'
status: open
created_at: '2026-11-09T11:23:00.616046'
schema_version: '0.1'
reference_materials: null
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

