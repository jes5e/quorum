---
id: b.upt
type: bee
title: 'Review-loop exit rule: the orchestrator judges whether a round is still worth running; reviewer severity tags become evidence, not verdict (placeholder until the chain validation reports)'
parent: null
reference_materials: null
created_at: '2026-09-15T19:06:47.762803'
status: open
schema_version: '0.1'
guid: uptryrnfwpzg7wndccokwjbo4jxbiaui
---

## Description

Placeholder filed 2026-09-15; the full design is written after the planning-chain validation run reports. Move this repo's hand-edit cold-review exit rule (CLAUDE.md `## Working on the orchestrator skills`) into the shipped review loop of `/quo-fix-issue` and `/quo-execute`.

## Current behavior

`**Severity bounds the loop**` treats the reviewer's severity tag as the verdict: any `blocker` or `suggestion`, or any `nit` deeper than `trivial-tweak`, holds the lane open for another cold round. The orchestrator has no judgment over whether a round is still worth running. The b.zi3 and b.pkn validation runs each showed reviewers tagging pure wording fixes as `suggestion`, each costing a fresh ~100k-token reviewer; b.pkn reported five extra doc rounds and two extra test rounds from one ambiguity.

## Expected behavior (sketch)

Reviewer tags become evidence, not verdict. Per round the orchestrator judges: does any remaining finding describe a behavior defect or a false claim, or would fixing it change what ships? If yes, another cold round. If no, apply the trivial fixes, close the lane, and render every applied item on the summary's **Reviews** line so the post-completion sweep re-reads them cold. Guards: the judgment is written to the manifest before the lane closes (manifest-write-then-act, the gate shape); a `blocker` is never closable this way; the post-completion sweep stays the backstop. Fold in b.7wb's per-lane round recording (earned / late / variance) and b.pkn report item 5 (a post-completion `suggestion` owes a reviewer pass — state it). Coverage is unchanged: every round still re-reads the whole diff; what stops is paying a full round for reviewer-to-reviewer wording variance.

## Suggested fix

Inventory-anchored hand edits with case enumeration up front (the loop condition's inputs, the manifest write, the compaction case, the blocker case), one cold round, then one `/quo-fix-issue` validation run in event_consumer_service comparing round counts against b.zi3 and b.pkn. Sequenced after the planning-chain validation and before b.sb7, so b.sb7's own validation runs under the new rule. Waits for the operator's go after ticket review.

## Addendum (2026-09-15) — redefine the severity scale by consequence so the exit decision reads it instead of re-grading it

The exit rule above splits two judgments: the reviewer classifies findings; the orchestrator decides whether a lane needs another round. Today's `blocker` / `suggestion` / `nit` scale is defined as "importance", which conflates "wrong as it stands" with "worth doing", so reviewers tag wording fixes as `suggestion` (three times in the b.pkn run alone) and every real finding lands in a level that holds the lane open. Redefine the levels by consequence, each with a one-line test:

- `blocker` — the code or text is wrong, or something ships broken. Test: a user or a downstream agent acting on the current state would be misled or fail.
- `suggestion` — not wrong today, but a reader or the code will do the wrong thing without this. Test: the fix changes what the text asserts or what the code does.
- `nit` — true and complete as it stands; this makes it better. Test: neither what is asserted nor what happens changes. Includes behavior-preserving refactors and wording.

Depth stays where it is, on each fix path. With consequence-defined levels the orchestrator's exit decision is near-mechanical: another round while any `blocker` remains or any `suggestion` remains outstanding; `nit`s are applied in the final implementer pass and recorded on the **Reviews** line, whatever their depth. The residual orchestrator judgment is the one the hand-edit exit rule already names: a `suggestion` whose fix is wording on text an earlier cold pass accepted closes the lane with the residual recorded. Each review skill carries worked examples per level (the current examples are where the 2026-09-11 calibration sentence was found to contradict the skill).

Scope: the three review skills' severity paragraphs and examples, the `**Severity bounds the loop**` paragraph in both bodies, the exit-decision manifest write. One designed change, not three appended sentences.

## Status (2026-09-16)

The planning-chain run has happened (its report is on b.7ib) and the operator has reset direction to fix-issue-first, so this ticket no longer waits on anything: the next action is to write its full design for operator review, then implement on the operator's go. The chain run's cost data corroborates the rationale — roughly 25 gates answered, about 9 carrying a real choice — though that run's own defects belong to the planning rewrite (b.7ib), not here. Scope stays `/quo-fix-issue`, `/quo-execute`, and the three review skills.

