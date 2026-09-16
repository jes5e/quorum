---
id: b.7d5
type: bee
title: 'Give the manifest''s ## Rounds exit decision a post-compaction reader: a row whose decision names an action that has not landed re-dispatches the reviewer instead of trusting the counts (one-tick window; follow-up to b.upt)'
parent: null
reference_materials: null
created_at: '2026-09-16T13:42:32.942251'
status: done
schema_version: '0.1'
guid: 7d5vgjx5b3mc5ique3k3uj6z5v47rumj
---

## Description

The per-round exit decision that `b.upt` added to `/quo-fix-issue` and `/quo-execute` is written to the run-state manifest's `## Rounds` row before the action it names (the re-dispatch, the final implementer pass, or marking the lane `closed`). That borrows the manifest-write-then-act shape the gates use, but the gates' shape is safe because Section 3's post-compaction rule re-fires a filled `## Open gate`. The `## Rounds` row has no analogue: its `decision` column is written by rule and read by no rule in either body, and `## 4. The loop`'s Tick step 1 names only `## Lanes` and `## Obligations` as in-flight state.

## Current behavior

The window is one tick: after the `## Rounds` row is written with `close — nits only` or `close — residual` and its counts, and before the final implementer lane row is added at that scope. If a compaction lands there, the resumed orchestrator sees a `closed` reviewer lane, no implementer lane, and a row asserting counts for work that never landed; the findings the pass would have applied lived only in the reviewer's return, which the compaction removed. What happens next is governed by existing text: the phase ladder has no clean return to stop on, so the orchestrator dispatches a fresh cold reviewer at the same scope, that pass re-raises whatever was never applied, and that round's decision rewrites the row. The failure therefore degrades to one extra cold round rather than to lost coverage, and the post-completion sweep reads the diff either way. The `routing.md` rationale bullet for the write-before-act rule states this outcome honestly since the `b.upt` batch's fourth cold round; before that it claimed a compaction in the window "loses nothing".

## Expected behavior

The row has a reader. The reviewer's sketch, verbatim in substance: extend Section 3's existing post-compaction recovery sentence — today it names only `## Open gate` — so that a `## Rounds` row whose `decision` names an action that has not landed re-dispatches that lane's reviewer at the same round instead of trusting the counts. The rule needs to state how "action pending" is detected from durable state, because no field in the row distinguishes "action landed" from "action pending": candidates are the absence of an implementer lane row at that scope dispatched after the reviewer's return, or a new column, each with its own compaction and empty-lane cases.

## Suggested fix

A design item, not a fix-now sentence: it adds a reader to a manifest section and so is a routing input under CLAUDE.md `## Working on the orchestrator skills`. Enumerate first — the inputs (the row, `## Lanes` at that scope, the reviewer's return), what a compaction destroys at each of the three write points (before the row write, between the row write and the implementer dispatch, after the implementer lane is `closed`), the empty-lane case, the `close — clean` case where no action is owed, and the PM in-flight site where the implementer passes are the PM's, not the orchestrator's — then write the rule once in Section 3 of both bodies (Tier 1) and edit every reader (`docs/sdd.md` D1 and the exit-rule feature, the brief's D9 amendment, `references/routing.md`'s rationale bullet). Weigh it against the alternative of leaving the one-tick window as documented behavior: the cost of the window is one extra cold round and a **Reviews** line that can over-count until the row is rewritten; the cost of the rule is a new reader of the manifest and its own cases.

## Background

Surfaced by the fourth cold round of the `b.upt` implementation batch (2026-09-16) as a `suggestion` whose fix path (b) was judged new machinery and deferred here, with path (a), the narrowed rationale claim, applied in that batch. Sequenced after `b.upt`'s validation run in a code repository, which is the first run that will produce `## Rounds` rows at all.

## Status (2026-09-16) — done, absorbed by b.vtw Batch A

The `## Rounds` row gained readers without the dedicated post-compaction reader sketched above. Batch A of Issue `b.vtw` (commit `cf4b27e` and its round-5 follow-ups) makes the row a routing input: the earned-chain escalation reads two consecutive `earned` classifications and routes the chain to the escalation target instead of another implementer; the `decision` column's `to the escalation target` value marks an in-flight premise check or escalation so a resumed orchestrator can tell that Analyst (or operator-gate) dispatch from a Design Proposal one; and the hold-set rule rewrites a `close — text` row to `another round` when the final pass returns `code` or `tests`. The one-tick window this ticket described remains as documented behavior: a compaction between the row write and the action costs one extra cold round, never coverage, and the `routing.md` rationale bullet states that honestly. The design-item alternative (a new column or an implementer-lane-presence rule) was weighed in the Batch A rounds and not built; the reader the row needed arrived through the escalation rule instead.
