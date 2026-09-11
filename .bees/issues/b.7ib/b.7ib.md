---
id: b.7ib
type: bee
title: 'Rewrite /quo-plan the way the two orchestrators were rewritten: inventory first, manifest-carried state, no TaskList dependence, 500-line target (after the breakdown-epic rewrite)'
parent: null
reference_materials: null
created_at: '2026-09-11T01:15:20.509880'
status: open
schema_version: '0.1'
guid: 7ib1dcwwzyj8bfty77e2p7izxrvrotg9
---

## Description

`skills/quo-plan/SKILL.md` is the second-largest body in the repo and shares the pre-rewrite shape of the two orchestrators: 896 lines, 14.2k words, 29 TaskList-tool references (measured 2026-09-11). Its deferral-hygiene gate is TaskList-fronted (two-step `TaskCreate` → `AskUserQuestion`; `defer-*` TaskList tasks), and the TaskList tools are off by default in the current harness (`CLAUDE_CODE_ENABLE_TODO_TOOLS` is unset in every repo that uses quorum), so the gate machinery cannot execute without an environment change. It delegates to three sub-skills through the Skill tool (`/quo-write-prd`, `/quo-write-sdd`, `/quo-spec-review`). b.eid is already open against its plan path.

## Current behavior

896 lines of prose grown through fix runs; gates and the deferral ledger depend on tools the harness does not expose by default.

## Expected behavior

The rewritten orchestrators' shape: a body at or under the 500-line target with the load-bearing sections inside the first 150 lines, state carried in a run-state manifest with no TaskList reads, gates as manifest `Write` then `AskUserQuestion`, rationale in shipped reference files, structural tests in place of prose pins.

## Suggested fix

Same process as the companion `/quo-breakdown-epic` ticket (b.pcc), sequenced after it: inventory first, then decisions and a brief, then a clean-room rewrite in a worktree with cold reviews under the review-round exit rule, then validation on a code repo through the plan → breakdown → execute chain. Prerequisites: b.sb7 has landed (it edits this skill's `## Anticipated doc impact`, Encode prose, and opening tip); the `/quo-breakdown-epic` rewrite has landed, so the two planning-side bodies share one manifest and gate shape rather than being designed twice; the current rebuild's chain validation has run, which is what shows whether this skill executes without the todo tools.

## Background and rationale

Surfaced alongside the `/quo-breakdown-epic` ticket when the operator asked whether other skills needed the orchestrators' treatment. `/quo-setup` (891 lines) was considered and excluded: it is a linear wizard with no loop, no repeating gate, and no TaskList dependence; its length is the two bootstrap skeletons and per-OS snippets. The role files were excluded: `agents/pm.md` is the heaviest at 256 lines and could take the rationale-to-reference treatment later, but it has no loop of its own and was deliberately kept and trimmed in the rewrite.

