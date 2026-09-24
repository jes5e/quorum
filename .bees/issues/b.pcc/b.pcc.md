---
id: b.pcc
type: bee
title: 'Minimal rewrite of /quo-breakdown-epic under the prose standard: no TaskList dependence, 250/350-line budget, output contract shared with b.87t'
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

## Evidence from the prose-size research (2026-09-11)

A cold research agent measured every shipped artifact and classified the four largest unrewritten files by paragraph. Findings that bear on this rewrite:

- Growth: `quo-breakdown-epic` went from 2,839 words at the initial commit to 18,108 (6.4x) over 51 commits, the same curve the two orchestrators followed before their rewrite (8.5x and 4.1x). The rewrite deleted 40% of the orchestrators' prose outright and moved 19% to reference files with no coverage loss by the brief's D12 criterion.
- Bucket estimate for this body (±5 points): executable instruction 47%; rationale 17%; counter-anchor prose 16% (55 "do not", 9 "MUST NOT", 14 "never"; the `general-purpose` fallback prohibition stated three times); duplication 14% (the two-step `TaskCreate` → `AskUserQuestion` preamble restated ten times at ~70 words each; the subagent precondition stated three times; base-directory resolution explained four times; the no-delete scratch note three times); OS-paired snippets 3%; templates 3%.
- Section hot spots against the rewritten equivalents: Section 1.5 manifest 1,579 words (rewritten ~600, of which ~1,000 here is a collision-case essay with one 480-word bullet); Section 6.5 deferral hygiene 1,919 words (rewritten ~450 for the identical Steps 0–3 plus Fix / File / Encode plus helper commit); Section 7 checkpoint plus guard 2,288 words (rewritten ~480). Section 4's TaskList section is 713 words of machinery the orchestrators abandoned under D1.
- Every checkpoint carries a ~100-word "does not clear, compact, or reclaim context" disclaimer against a claim the file no longer makes.

Estimated cuttable with no behavior change: ~7,000 words; movable to references: a further ~2,000. The guard is the one section where convergence is a design change rather than a trim (D4's silent-continue was scoped to the two orchestrators, and `quo-setup` names this skill's four-option gate as the opt-out marker's only consumer), so the inventory must decide it explicitly.

## Prerequisites revised and new inputs (2026-09-17)

**Prerequisite change.** The "chain validation has run" prerequisite is withdrawn: the operator decided (2026-09-17) that `/quo-execute`'s first run comes *after* this rewrite and `/quo-plan`'s, as one plan → breakdown → execute chain on a real feature, so execute is validated against the Subtask shape it will actually consume. The 2026-09-16 chain run (plan + breakdown with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`) already answered the other half: the skill executes only with the env var. b.sb7 remains a prerequisite for its *design* (the doc model this body must emit doc Subtasks for); b.sb7's own `quo-breakdown-epic` edits are folded into this rewrite rather than made on the old body. Order: b.vtw Batch B2 → b.sb7 (doc roles + orchestrators) → **this ticket** → b.7ib → chain validation.

**Inputs the rewrite must consume (landed since filing).** (1) The writing rule on b.vtw: inter-agent contracts (headings, return lines, manifest columns, gate labels, fixed lines) stay literal; every other rule is a goal plus its reason, never a procedure or decision table. (2) B1's dispatch shape, which the rewritten orchestrators now share and this body's four dispatched roles inherit: implementers carry `name=<role>-<scope>` (scope sanitized to letters, digits, hyphen, underscore) and are resumed by `SendMessage` for fix rounds; reviewers stay fresh; every implementer return carries `## Files changed` and `Kinds changed:`; the manifest names a companion ledger file and `**Cost:**`, one row per completion. (3) The rewritten `/quo-execute`'s consumption contract: Scoped markers via `scoped_marker_resolver.py`, `## Source paths to fingerprint` from the Task's Engineer Subtasks, doc Subtasks under the b.sb7 register model, and the b.sb7 items this body previously carried (`## Anticipated doc impact` naming map, register, README; Encode destinations tickets only). (4) The guard decision named in the evidence section stays with the inventory.
## New inputs from b.87t (operator decisions 2026-09-23)

This ticket now follows b.37n, b.87t, b.87t's smoke Bee, the operator's big feature, and b.sb7 (order recorded on b.vtw). What changes for this rewrite:

- **What execute consumes.** Rebuilt `/quo-execute` runs one Engineer per Task, given the Task body plus its Engineer Subtask bodies in dependency order; the Test Writer and Doc Writer each receive their own Subtask bodies; "Verify the Task" Subtasks are absorbed by the orchestrator's close-out; docs-only Tasks run as the text class. The emitted shape the prior note named (per-Subtask fingerprint sets, Subtask-level concurrency) is no longer what execute needs.
- **Whether the Subtask layer earns its cost is this ticket's question**, answered from b.87t's smoke Bee and big-feature ledgers. Acceptance criteria are currently restated at four levels (PRD → Epic → Task → Subtask), each authored by a different agent in this skill; with Tasks as the execution unit, a thinner Subtask layer (or per-role work lists inside the Task body) may serve execute as well at lower breakdown cost.
- **The chain-validation prerequisite is gone.** `/quo-execute` is validated by b.87t's smoke Bee against the current breakdown output, run under `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, before this rewrite starts.
## Minimal rewrite (operator decisions 2026-09-24)

A minimal rewrite under CLAUDE.md `## How skill prose is written`, on the planning track. The order and the constraints shared with the execute track are on b.vtw's 2026-09-24 note.

This note supersedes, where they conflict: the clean-room process in `## Suggested fix`; the 500-line target; the b.vtw writing rule and inputs (2)–(3) of the 2026-09-17 note; and the prerequisites (b.sb7 landed, chain validation). The 2026-09-23 question of whether the Subtask layer earns its cost moves to a follow-up after the smoke test and the big feature; this rewrite keeps the layer.

- **Start from a failure inventory, not a rule inventory.** A rule survives when it is one of the standard's kinds, or its failure earns it.
- **No TaskList dependence.** Gates stay fronted by the manifest write: it is a structural guard against the narrate-instead-of-do failure, which is not gone.
- **Decide the context guard explicitly.** Its missing-reading gate is the only guard that reads the opt-out marker. Dropping that gate updates `/quo-setup`'s run-unguarded choice and CLAUDE.md's opt-out-marker exception in the same change.
- **State the Bash etiquette once, as a goal,** since the per-site wording that enforces it today goes. Bees usage is orientation, not recipes.
- **Budget:** 250-line target, 350-line hard cap, pinned by a test.
- **Output contract execute consumes:**
  - Tasks titled `Task N — <title>`, with `up_dependencies`.
  - Subtasks in the Mandatory Subtask Description Template, with statuses `drafted` → `ready`.
  - The Plan Bee's Scoped marker and `## Anticipated doc impact`, read as today.
  - The two items defined with b.87t (b.vtw).
