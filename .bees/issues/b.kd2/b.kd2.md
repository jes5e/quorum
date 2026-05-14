---
id: b.kd2
type: bee
title: Dispatch prompt must not loosen role boundaries
status: open
created_at: '2026-05-14T11:02:02.086897'
schema_version: '0.1'
reference_materials: null
guid: kd2cgvvgv2q1ya9deo4ydywdpugxexyd
---

## Description
In both `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md`, the "Dispatch prompt: quote the ticket/issue body verbatim" sub-sections (`quo-fix-issue` line 262, `quo-execute` line 239) discipline what goes INSIDE the quoted body (verbatim, no paraphrase, no identifier "clean-up") but explicitly allow free-form "framing prose around the quoted block" — and have no constraint on what that framing prose may say. In practice that lets the orchestrator carve role-boundary exceptions in the dispatch prompt, overriding the strict role contracts defined in the `agents/*.md` files.

## Current behavior
- `skills/quo-fix-issue/SKILL.md` line 270: "Framing prose around the quoted block (e.g., 'your gating precondition is met — start now') is fine; the body itself stays untouched."
- `skills/quo-execute/SKILL.md` line 241: identical sentence in the analogous sub-section.
- Neither sub-section forbids the orchestrator from softening role boundaries in that framing prose.
- The role contracts (`agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`) are strict, but only at the role-file layer.

Observed instance (sibling-repo run): the Engineer dispatch prompt said "The Test Writer handles dedicated test files; you may add the new `tests/misc/generate_slowpath_chunk.rs` generator test recipe if the preferred path is chosen ... but coordinate with the Test Writer's diff." This contradicts `agents/engineer.md`:
- Line 3 (frontmatter description): "Does NOT update tests or docs — those are owned by the test-writer and doc-writer subagents."
- Line 8: "The work is source-code-only — unit tests are owned by the test-writer subagent and documentation is owned by the doc-writer subagent."

Both the Engineer and the Test Writer subsequently wrote to `tests/misc/generate_slowpath_chunk.rs` in parallel. Workers are explicitly hub-and-spoke through the orchestrator with no peer messaging (`skills/quo-fix-issue/SKILL.md` lines 274-276: "Workers do not message each other. The orchestrator is the hub; each dispatched Agent is a spoke that reads its prompt, edits files, and exits. The diff is the handoff between roles."), so "coordinate with the Test Writer's diff" cannot mean what it sounds like — there is no inter-Agent channel. The Engineer's later write effectively overwrote the Test Writer's earlier one.

## Expected behavior
Both SKILL.md files should explicitly forbid the orchestrator from carving role-boundary exceptions in the dispatch prompt's framing prose. Add one paragraph to each "Dispatch prompt: quote the ticket/issue body verbatim" sub-section, immediately after the "Framing prose around the quoted block ... is fine; the body itself stays untouched." sentence. Recommended substance:

> The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the role's contract file (`agents/<role>.md`). The orchestrator MUST NOT tell the Engineer it may also write tests or docs; MUST NOT tell the Test Writer it may also modify source code; MUST NOT tell the Doc Writer it may also modify source or test files. The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also add this one test file" / "you may also touch this one source line"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer dispatch, a redirect of the Issue, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other and the diff is the only handoff between roles — there is no "coordinate with the other role's diff" channel for the worker to actually use, so a softening clause cannot be made safe by adding coordination prose.

## Impact
- **Silent signal loss.** Parallel writes to the same file (the observed failure mode) overwrite each other in git's working tree. If the Engineer's and Test Writer's versions of a test file differ in their regression-guard coverage, one is silently lost; the surviving version may or may not catch the bug the Issue is meant to prevent.
- **Role-contract drift risk.** When SKILL.md dispatch prompts override `agents/*.md` role contracts, future maintainers may try to "fix" the role files to match — which would loosen the role contracts and erode the workflow's structural integrity.
- **Workflow audit gap.** `/quo-engineer-review`, `/quo-test-writer-review`, and `/quo-doc-writer-review` review per-role diffs against the role contract. A softened dispatch prompt invites a worker to produce work that violates the contract, which the reviewer then has to reject — wasted Agent cycles, plus the risk that a subtle softening goes unflagged.

## Suggested fix
Skill-prose-only change. No source code, tests, or role-file changes.

1. **`skills/quo-fix-issue/SKILL.md` "Dispatch prompt: quote the issue body verbatim" sub-section (lines 262-272)** — add one paragraph immediately after the "Framing prose around the quoted block ... is fine; the body itself stays untouched." sentence (line 270). Substance per "Expected behavior" above.
2. **`skills/quo-execute/SKILL.md` "Dispatch prompt: quote the ticket body verbatim" sub-section (lines 239-241)** — add the same paragraph in the analogous location. Reword "the Issue" / "the Engineer" / etc. to match the execute-mode terminology already used (Subtask scope rather than Issue scope), but keep the substantive rule identical so the two skills stay aligned.

The change is additive — no existing prose is removed or revised, so it does not alter today's working behavior for runs where the orchestrator already respected the role boundaries.

## Background and rationale
The role contracts in `agents/*.md` define the structural property of the workflow: Engineer handles source, Test Writer handles tests, Doc Writer handles docs. The orchestrator dispatches them in parallel (or in phased waves) and the diff is the only handoff. That model relies on each worker staying inside its lane; when the orchestrator's dispatch prompt loosens a lane, the workers race for the same files and the diff merges by last-write-wins.

A single observed slip is weak evidence on its own, but the failure mode is silent — there is no exit code, no test failure, no reviewer complaint to surface that one version of a file got overwritten by another. Silent failures are the most expensive to debug later, and the fix here is one paragraph per skill. Cheap to apply now.

## Decisions and rejected alternatives
- **Strengthen `agents/engineer.md` (and the other implementer role files) with a self-defense rule** ("if the dispatch prompt tells you to write tests, refuse and exit"). Rejected: shifts the burden from the orchestrator (who has full run context) to the worker (who has only its assigned ticket); the role file already says "does not write tests or docs" and a self-defense clause would duplicate that contract. The orchestrator-side guardrail is the natural fix because the orchestrator is the one writing the prompt that violates the contract.
- **Restrict the Engineer's `tools` allowlist (`agents/engineer.md` frontmatter) to forbid writes under `tests/`.** Rejected: the harness's tool gating is path-blind — the Engineer's `Write` tool either works everywhere or not at all. A path-restricted Write would be a harness change, out of scope here. And the Engineer legitimately needs Write for source files, so forbidding Write entirely is not viable.
- **Wait for a second occurrence before treating this as a recurring pattern.** Rejected: the single observed instance silently lost a regression guard (a write-after-write race overwrote one version of the test file); silent loss is worse than loud failure, and the fix is one paragraph per skill. Cheap to apply now, expensive to find in a future debugging session.

