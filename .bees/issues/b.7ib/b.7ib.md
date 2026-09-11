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

## Evidence from the prose-size research (2026-09-11)

A cold research agent measured every shipped artifact and classified the four largest unrewritten files by paragraph. Findings that bear on this rewrite:

- Growth: `quo-plan` went from 1,909 words at the initial commit to 14,174 (7.4x) over 49 commits, the steepest curve in the repo.
- Bucket estimate (±5 points): executable instruction 53%; rationale 11%; counter-anchor prose 10% ("Future maintainers must not tighten…" twice; pre-commitment lines); duplication 11% (the two-step gate preamble seven times plus twelve `gate-askuserquestion-<short-suffix>` mentions; Step 5g is a 1,600-word near-copy of `quo-breakdown-epic` Section 6.5; the gate-task naming bullet duplicated); OS-paired snippets 5%; templates and examples 10%.
- Section hot spots: Step 5e fresh-eyes plan review 2,907 words, whose embedded reviewer prompt carries three trailer shapes differing only in where `(Recommended)` sits (~450 words for ~150 of information); Step 4c 1,683; Step 5a 1,406; Step 5g 1,600.
- Step 7's commit snippets are multi-line shell with `$(...)`, `case`, and pipes on both OSes, violating this repo's single-literal-command etiquette, for a job `hive_commit.py resolve-hive-paths --hive plans|specs` already performs for three sibling skills.

Estimated cuttable with no behavior change: ~5,000 words; movable to references: a further ~1,500. Sequence after b.pcc so the two planning-side bodies share one manifest and gate shape and one deferral-hygiene text instead of two near-copies.

