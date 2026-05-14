---
id: b.kd2
type: bee
title: Dispatch prompt must not loosen role boundaries
parent: null
reference_materials: null
created_at: '2026-05-14T11:02:02.086897'
status: done
schema_version: '0.1'
guid: kd2cgvvgv2q1ya9deo4ydywdpugxexyd
---

## Description
In all three of `skills/quo-fix-issue/SKILL.md`, `skills/quo-execute/SKILL.md`, and `skills/quo-breakdown-epic/SKILL.md`, the "Dispatch prompt: quote the ticket/issue body verbatim" sub-sections (`quo-fix-issue` line 262, `quo-execute` line 239, `quo-breakdown-epic` line 344) discipline what goes INSIDE the quoted body (verbatim, no paraphrase, no identifier "clean-up") but explicitly allow free-form "framing prose around the quoted block" — and have no constraint on what that framing prose may say. In practice that lets the orchestrator carve role-boundary exceptions in the dispatch prompt, overriding the strict role contracts defined in the `agents/*.md` files.

## Current behavior
- `skills/quo-fix-issue/SKILL.md` line 270: "Framing prose around the quoted block (e.g., 'your gating precondition is met — start now') is fine; the body itself stays untouched."
- `skills/quo-execute/SKILL.md` line 241: identical sentence in the analogous sub-section.
- `skills/quo-breakdown-epic/SKILL.md` line 346: identical sentence in the analogous sub-section (which is the research-mode dispatch path).
- None of the three sub-sections forbids the orchestrator from softening role boundaries in that framing prose.
- The role contracts (`agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) are strict, but only at the role-file layer.

Observed instance (sibling-repo run): the Engineer dispatch prompt said "The Test Writer handles dedicated test files; you may add the new `tests/misc/generate_slowpath_chunk.rs` generator test recipe if the preferred path is chosen ... but coordinate with the Test Writer's diff." This contradicts `agents/engineer.md`:
- Line 3 (frontmatter description): "Does NOT update tests or docs — those are owned by the test-writer and doc-writer subagents."
- Line 8: "The work is source-code-only — unit tests are owned by the test-writer subagent and documentation is owned by the doc-writer subagent."

Both the Engineer and the Test Writer subsequently wrote to `tests/misc/generate_slowpath_chunk.rs` in parallel. Workers are explicitly hub-and-spoke through the orchestrator with no peer messaging (`skills/quo-fix-issue/SKILL.md` lines 274-276: "Workers do not message each other. The orchestrator is the hub; each dispatched Agent is a spoke that reads its prompt, edits files, and exits. The diff is the handoff between roles."), so "coordinate with the Test Writer's diff" cannot mean what it sounds like — there is no inter-Agent channel. The Engineer's later write effectively overwrote the Test Writer's earlier one.

## Expected behavior
All three SKILL.md files should explicitly forbid the orchestrator from carving role-boundary exceptions in the dispatch prompt's framing prose. Add one paragraph to each "Dispatch prompt: quote the ticket/issue body verbatim" sub-section, immediately after the "Framing prose around the quoted block ... is fine; the body itself stays untouched." sentence. Recommended substance:

> The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the dispatched role's contract file (`agents/<role>.md`). The rule applies to **every** dispatched role type — both the implementer roles (Engineer / Test Writer / Doc Writer) and the review-only roles (PM, Code Reviewer, Test Reviewer, Doc Reviewer). Concrete examples of forbidden softening (illustrative, not exhaustive):
>
> - MUST NOT tell the Engineer it may also write tests or docs.
> - MUST NOT tell the Test Writer it may also modify source code.
> - MUST NOT tell the Doc Writer it may also modify source or test files.
> - MUST NOT tell the PM or any reviewer (Code Reviewer / Test Reviewer / Doc Reviewer) it may write source, tests, or docs — these are review-only roles, and the contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (each reviewer) explicitly.
> - MUST NOT tell one reviewer it may also review another reviewer's lane (e.g., Code Reviewer reviewing tests, or Test Reviewer reviewing documentation).
>
> The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also add this one test file" / "you may also touch this one source line"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer dispatch, a redirect of the Issue, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other; the only handoff is from worker to orchestrator (the diff in execution mode, the JSON return in research mode), never worker-to-worker. So a softening clause cannot be made safe by adding "coordinate with the other role's diff" or similar coordination prose — that channel does not exist.

## Impact
- **Silent signal loss in execution mode.** Parallel writes to the same file (the observed failure mode in `quo-fix-issue` and `quo-execute`) overwrite each other in git's working tree. If the Engineer's and Test Writer's versions of a test file differ in their regression-guard coverage, one is silently lost; the surviving version may or may not catch the bug the Issue is meant to prevent.
- **Cross-role scope creep in research mode.** In `quo-breakdown-epic`, the research-mode preamble already locks workers to read-only behavior, so the parallel-write race cannot occur — but a softened dispatch prompt produces cross-role Subtask proposals in the worker's JSON return (e.g., the research-mode Engineer proposes test Subtasks that should have been the Test Writer's lane). The orchestrator's reconciliation step has visibility into each JSON return and can detect/de-dupe — louder than the silent execution-mode race, but still a workflow-integrity gap.
- **Role-contract drift risk.** When SKILL.md dispatch prompts override `agents/*.md` role contracts, future maintainers may try to "fix" the role files to match — which would loosen the role contracts and erode the workflow's structural integrity.
- **Workflow audit gap.** `/quo-engineer-review`, `/quo-test-writer-review`, and `/quo-doc-writer-review` review per-role diffs against the role contract. A softened dispatch prompt invites a worker to produce work that violates the contract, which the reviewer then has to reject — wasted Agent cycles, plus the risk that a subtle softening goes unflagged.

## Suggested fix
Skill-prose-only change. No source code, tests, or role-file changes.

1. **`skills/quo-fix-issue/SKILL.md` "Dispatch prompt: quote the issue body verbatim" sub-section (lines 262-272)** — add one paragraph immediately after the "Framing prose around the quoted block ... is fine; the body itself stays untouched." sentence (line 270). Substance per "Expected behavior" above.
2. **`skills/quo-execute/SKILL.md` "Dispatch prompt: quote the ticket body verbatim" sub-section (lines 239-241)** — add the same paragraph in the analogous location. Reword "the Issue" / "the Engineer" / etc. to match the execute-mode terminology already used (Subtask scope rather than Issue scope), but keep the substantive rule identical so the two skills stay aligned.
3. **`skills/quo-breakdown-epic/SKILL.md` "Dispatch prompt: quote the ticket body verbatim" sub-section (line 344, with the analogous "Framing prose ... is fine" sentence at line 346)** — add the same paragraph in the analogous location, immediately after line 346. The substance is identical to items 1 and 2 (the role-boundary rule applies to research-mode dispatches because the subagent types are the same `engineer` / `test-writer` / `doc-writer` / `pm` types reused from `/quo-execute`, per `quo-breakdown-epic` SKILL.md line 322). The closing sentence's "diff is the handoff" framing is already covered by the recommended-substance phrasing above (which names both execution-mode diff and research-mode JSON return), so no additional adjustment is needed for this skill. The research-mode preamble at lines 326-339 already prohibits file writes regardless of role, so the failure mode here is cross-role Subtask proposals rather than a parallel-write race — but the rule still applies because the role contracts are shared.

The change is additive — no existing prose is removed or revised, so it does not alter today's working behavior for runs where the orchestrator already respected the role boundaries.

## Background and rationale
The role contracts in `agents/*.md` define the structural property of the workflow: Engineer handles source, Test Writer handles tests, Doc Writer handles docs; PM and the three reviewers are review-only roles that don't write at all. The orchestrator dispatches them in parallel (or in phased waves) and the diff is the only handoff in execution mode (JSON return in research mode). That model relies on each worker staying inside its lane; when the orchestrator's dispatch prompt loosens a lane, the workers race for the same files (execution mode) or propose overlapping Subtasks (research mode), and the orchestrator's reconciliation step has to fix the mess after the fact — silently in execution mode, visibly in research mode.

A single observed slip is weak evidence on its own, but the failure mode in execution mode is silent — there is no exit code, no test failure, no reviewer complaint to surface that one version of a file got overwritten by another. Silent failures are the most expensive to debug later, and the fix here is one paragraph per skill. Cheap to apply now.

Including `quo-breakdown-epic` in the fix is for consistency: the same dispatch-prompt sub-section exists in all three skills, the same subagent types are dispatched, and the same role contracts apply. Documenting the rule in only two of the three skills would create skill-prose drift that future maintainers would have to reconcile — easier to land all three at once.

## Decisions and rejected alternatives
- **Strengthen `agents/engineer.md` (and the other implementer role files) with a self-defense rule** ("if the dispatch prompt tells you to write tests, refuse and exit"). Rejected: shifts the burden from the orchestrator (who has full run context) to the worker (who has only its assigned ticket); the role file already says "does not write tests or docs" and a self-defense clause would duplicate that contract. The orchestrator-side guardrail is the natural fix because the orchestrator is the one writing the prompt that violates the contract.
- **Restrict the Engineer's `tools` allowlist (`agents/engineer.md` frontmatter) to forbid writes under `tests/`.** Rejected: the harness's tool gating is path-blind — the Engineer's `Write` tool either works everywhere or not at all. A path-restricted Write would be a harness change, out of scope here. And the Engineer legitimately needs Write for source files, so forbidding Write entirely is not viable.
- **Limit the fix scope to write-mode skills (`quo-fix-issue`, `quo-execute`); leave `quo-breakdown-epic` for a follow-up.** Rejected: the dispatch-prompt sub-section in `quo-breakdown-epic` is structurally identical to the other two, the role contracts are shared (same subagent types), and the fix is the same one paragraph. Leaving one of the three skills out creates a documentation gap that future maintainers (or future Claude orchestrators following one skill's prose as a template) would propagate. The research-mode failure mode is softer (caught at reconciliation, not silent), but that's not a reason to skip the consistent fix.
- **Wait for a second occurrence before treating this as a recurring pattern.** Rejected: the single observed instance silently lost a regression guard (a write-after-write race overwrote one version of the test file); silent loss is worse than loud failure, and the fix is one paragraph per skill. Cheap to apply now, expensive to find in a future debugging session.

## Tracking
**Line-number references in this body** (e.g. `line 270`, `line 344`) are anchored to the SKILL.md / agents files as of 2026-05-14. If the files drift before this Issue is fixed, the Engineer should re-resolve each reference by content — every cited block has a quoted-prose or sub-section-heading anchor that survives line-number renumbering.
