---
id: b.pcc
type: bee
title: 'Rewrite /quo-breakdown-epic the way the two orchestrators were rewritten: inventory first, manifest-carried state, no TaskList dependence, 500-line target'
parent: null
reference_materials: null
created_at: '2026-09-11T01:15:18.807870'
status: open
schema_version: '0.1'
guid: pccrxyv5oh99ahdywhqc1natjaibzd8r
---

## Description

`skills/quo-breakdown-epic/SKILL.md` has the same disease the two orchestrator bodies had before their clean-room rewrite (b611786), at a larger scale. Measured 2026-09-11:

| Body | Lines | Words | TaskList-tool references |
|---|---|---|---|
| quo-breakdown-epic | 965 | 18.1k | 43 |
| quo-fix-issue (rewritten) | 352 | 9.1k | 0 |
| quo-execute (rewritten) | 369 | 9.3k | 0 |

It is an orchestrator: it dispatches four roles, runs a PM gap-fill loop, fires gates, and runs deferral hygiene. All of that is TaskList-fronted (the two-step `TaskCreate` → `AskUserQuestion` gate contract, `defer-*` TaskList tasks), and the TaskList tools are off by default in the current harness (`CLAUDE_CODE_ENABLE_TODO_TOOLS` is unset in every repo that uses quorum), so as shipped its gate and deferral machinery cannot execute without an environment change. It is also the third leg of CLAUDE.md's run-state-manifest mirror rule, so the two rewritten bodies carry mirror text for a sibling written in the old style. It grew the way the old bodies did, through `/quo-fix-issue` runs on prose (b.8x3 and others).

## Current behavior

965 lines, twice the word count of either rewritten orchestrator; gates and deferral ledger depend on tools the harness does not expose by default; CLAUDE.md `## Working on the orchestrator skills` explicitly notes it "still carries the older two-step `TaskCreate` contract".

## Expected behavior

The same shape the two orchestrators now have: a body at or under the 500-line target with Sections 1–5 inside the first 150 lines, state carried in the run-state manifest (no TaskList reads), gates as manifest `Write` then `AskUserQuestion`, rationale and shared prose moved to shipped reference files under `skills/quo-breakdown-epic/references/`, and a structural test suite in place of prose pins.

## Suggested fix

Follow the precedent exactly, in this order, and do not start until the prerequisites below hold:

1. **Inventory first.** Produce the rule inventory for this body (mechanisms, literals index, edges, single points of failure) in `docs/inventory/` the way `INVENTORY.md` / `EDGES.md` / the consolidated files did for the two orchestrators. No prose is written before the inventory is reviewed.
2. **Decisions and brief.** Record the decisions (state carrier, reference files, gate shape, what is cut) and a brief with acceptance criteria, mirroring `REWRITE-BRIEF.md` D1–D12 where they apply.
3. **Clean-room rewrite** from the inventory in a worktree, with cold `/quo-engineer-review` passes anchored on the brief, under the review-round exit rule in CLAUDE.md `## Working on the orchestrator skills`.
4. **Validate on a code repo** with the plan → breakdown → execute chain before merging.

Prerequisites: b.sb7 has landed (it edits `/quo-breakdown-epic`'s Encode prose and `/quo-plan`, so a concurrent rewrite of the same file is the collision that discarded the first b.sb7 worktree); the current rebuild's validation runs (b.pkn in event_consumer_service, then the plan → breakdown → execute chain) have run, because the chain run is what tells us whether this skill executes at all without the todo tools and how urgent this is.

## Background and rationale

Surfaced when the operator asked (2026-09-10) whether other skills needed the orchestrators' treatment, and confirmed (2026-09-11) when it emerged that no repo sets `CLAUDE_CODE_ENABLE_TODO_TOOLS`. Related: the rewrite handoff note's known follow-up "/quo-breakdown-epic still TaskList-fronted"; the companion ticket b.7ib for `/quo-plan`.

