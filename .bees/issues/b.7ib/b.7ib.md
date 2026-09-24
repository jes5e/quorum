---
id: b.7ib
type: bee
title: 'Minimal rewrite of /quo-plan and its three sub-skills (or OpenSpec front end) under the prose standard: no TaskList dependence, 250/350-line budget'
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

## Evidence from the first planning-chain validation run (2026-09-16, event_consumer_service)

`/quo-plan` → `/quo-breakdown-epic` ran with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`; the TaskList tools worked once enabled. The agent's skill-text defect list, recorded here as rewrite input rather than patched (the operator decided 2026-09-16 not to hand-edit a body slated for clean-room rewrite):

1. Step 5g says the gate contract applies at every gate but its list omits the Step 0a distill gate and the Step 3 scope gate.
2. The Step 3 scope gate fires on identical content to the Step 0a distill gate; the second answer is predetermined.
3. `quo-write-prd` 3a then 6 and `quo-write-sdd` 4a then 7: on the inline path the draft gate and the final-body gate bracket only a file write, so the second is predetermined; the "not a duplicate" claim holds only on the solo path. Fired six times in one run.
4. Step 4b: the writers' findings payload is the only revise path; a one-line trivial-tweak costs a full writer invocation with two gates. Reviewer depth tags are never routed on. (The orchestrators' b.bix nit-batching rule never reached the planning side.)
5. Step 4c revise loop step 4: cross-document findings go to both writers regardless of which document the chosen fix path targets.
6. `quo-write-sdd`: "Explore dispatch runs on every invocation" vs the findings text's "re-dispatching where appropriate".
7. Step 5a detection query uses `report: [ticket_id, title, reference_materials]`, which the bees CLI rejects; `quo-file-issue` Sub-step A.1 already documents the limitation.
8. Step 5e time-budget short-circuit still routes blocker fixes through full writer re-invocations; no direct-edit path.
9. The plan reviewer suggested a cross-hive dependency edge the CLI rejects (an Epic cannot depend on a Bee); the reviewer prompt should say a release gate is prose.
10. Ordering: spec review runs before Epics exist, substance review after; the substance reviewer reopens PRD/SDD, which triggers a capped spec re-run, which can reopen the PRD again. Proposed: substance review on PRD and SDD before Epics, a short decomposition check after.
11. `/quo-file-issue` Step 4 commits mid-run; Step 7 does not anticipate an inline filing commit.

Cost observation: ~25 gates answered, ~9 carrying a real choice. Two compounding causes: two gates per writer invocation with no lightweight edit path, and three real first-draft design errors the plan reviewer correctly caught, each fix then paying full writer cost. The rewrite's decisions should give the planning loop the orchestrators' cost controls (one gate per real decision, trivial-tweak findings applied without re-invocation, routing by fix-path target) and settle the review ordering (item 10).

## Prerequisites revised and new inputs (2026-09-17)

The "chain validation has run" prerequisite is withdrawn for the same reason as on b.pcc: the operator decided (2026-09-17) that the plan → breakdown → execute chain runs once, *after* both planning rewrites, as `/quo-execute`'s first run. Order: b.vtw Batch B2 → b.sb7 (doc roles + orchestrators) → b.pcc → **this ticket** → chain validation. b.sb7's edits to this skill, `quo-plan-from-specs`, `quo-write-prd`, `quo-write-sdd`, and `quo-spec-review` (the `### Feature:` retirement, skeleton changes, hard-fail message, `## Anticipated doc impact`) fold into this rewrite rather than being made on the old body. The rewrite also consumes the writing rule on b.vtw (contracts literal, everything else a goal plus its reason) and the orchestrators' cost controls named in the evidence above, now landed as b.vtw Batches A and B1: the kind-keyed hold set, the smallest-complete-fix pick rule, confirming passes after a lane's first review, named implementers resumed for fix rounds, and the native ledger — the planning loop's "two gates per writer invocation with no lightweight edit path" is the same shape those fixed on the execution side. After this rewrite, the residual two-step `TaskCreate` → `AskUserQuestion` mentions in the three review skills, `quo-write-prd`, `quo-write-sdd`, and `quo-spec-review` are swept, since no caller will use that contract.
## Minimal rewrite (operator decisions 2026-09-24)

A minimal rewrite under CLAUDE.md `## How skill prose is written`, on the planning track after b.pcc. The order and the constraints shared with the execute track are on b.vtw's 2026-09-24 note.

This note supersedes, where they conflict: the clean-room process in `## Suggested fix`; the 500-line target; the b.vtw writing rule; the prerequisites (b.sb7 landed, chain validation); and the folding of b.sb7's edits into this rewrite, which stay with b.sb7. The 2026-09-17 note's cost controls remain goals: one gate per real decision, trivial fixes applied without re-invoking a writer, and findings routed by where the fix lands.

- **Scope:** `/quo-plan`, `quo-write-prd`, `quo-write-sdd`, and `quo-spec-review`, which all carry TaskList dependence. `/quo-plan-from-specs` has none and is out of scope.
- **Settle OpenSpec first.** Either OpenSpec is the front end (a custom schema with no living `specs` artifact, plus a thin importer), or the skills are rewritten minimally. Either way, keep the cold plan reviewer: it caught three real design errors on 2026-09-16.
- **Start from a failure inventory;** the 2026-09-16 defect list above is part of it. Gates only for real decisions.
- **No TaskList dependence,** with gates fronted by a tool call as b.pcc records. Bash etiquette stated once, as a goal; bees usage as orientation.
- **Budget:** 250-line target, 350-line hard cap for `/quo-plan`, plus a cap for each rewritten sub-skill, all pinned by a test.
- **Output contract breakdown consumes** (an OpenSpec importer emits the same):
  - Epics titled `Epic N — <title>`, with statuses `drafted` / `ready` and `up_dependencies`.
  - `reference_materials` as one of: a `bees` entry naming a Spec Bee whose `t1=Doc` children are titled exactly `PRD` and `SDD`; a `file-path` entry; or null, meaning the Plan Bee body is the spec.
  - `## Anticipated doc impact` in the Plan Bee body.
