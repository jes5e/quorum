---
id: b.1bv
type: bee
title: Workflow trusts Issue ticket bodies as authoritative design specs
status: open
created_at: '2026-05-15T18:24:42.418149'
schema_version: '0.1'
reference_materials: null
guid: 1bv7yshtsv7gb1xhyupf4s1osz41n8fo
---

## Description

The `/quo-fix-issue` workflow treats Issue ticket bodies as authoritative design specs, regardless of how the Issue was filed. The Engineer is dispatched with the body's proposed solutions as instructions to execute. No role in the workflow does its own codebase research to evaluate whether the body's framing of the design space is correct, or to discover options the body didn't consider. The b.o6r case (described under "Impact" and "Background and rationale") happened to involve an upstream GitHub Issue, but the gap is fundamental to fix mode itself — an Issue filed conversationally by the local user has the same exposure.

The reality: Issue bodies come from many sources and many quality levels. They may be:
- A few-seconds-of-thought brainstorm — from a GitHub issue filed by someone in a different repo, or from a local user who just hit a bug and filed a quick ticket.
- A well-researched analysis from someone who has read this codebase (possibly authored from a Claude Code session in this codebase before filing — for either an upstream GH issue or a local bee ticket).
- Anywhere in between.

The workflow today can't tell the difference and trusts everything uniformly. That's the bug.

## Current behavior

- `/quo-fix-issue` resolves a URL to an Issue ticket (or accepts a ticket ID directly), then immediately dispatches the Engineer with the Issue body verbatim.
- The Engineer fetches upstream content (when `reference_materials` carries a URL) and implements per its instructions — including any solutions the upstream proposed.
- No codebase-research step happens between resolving the Issue and dispatching the Engineer. The body's framing is taken as the design.
- PM runs a post-implementation spec-alignment review: checks that the implementer faithfully executed what the body said. Doesn't challenge whether the body's framing was right.
- Reviewers (`code-reviewer`, `test-reviewer`, `doc-reviewer`) check execution quality only, not design quality.

## Expected behavior

Between resolving the Issue and dispatching the Engineer, an **Analyst** step does its own codebase research to evaluate the problem the body reported, treating any solutions the body proposed as **context for understanding the problem**, not as a menu to pick from. The Analyst returns a design proposal grounded in the actual codebase, not in the body's framing.

The Analyst's output naturally adapts to the quality of the body:
- When the body IS well-researched (cites code paths, references architectural decisions, weighs tradeoffs in this codebase's context), the Analyst's own research agrees and the proposal reflects the body's approach — possibly with refinements the Analyst found.
- When the body is a casual brainstorm, the Analyst's research diverges and produces a proposal the body didn't consider. The cleanest design path may not appear in the body's "Option 1/2/3" menu at all.

The Analyst's proposal is surfaced to the user (the quorum operator in *this* repo) for approval before the Engineer is dispatched. The user reacts to an **informed recommendation**, not a raw body menu.

## Impact

- **Half-fixes that contradict the implementer's own reasoning.** Concrete recent incident: during `/quo-fix-issue` against https://github.com/jes5e/quorum/issues/5 (commits since reverted), the Engineer's report explicitly argued one proposed solution was "fragile — orchestrator-side attention decay" — then implemented it anyway as a hybrid with another option, because that's what the upstream framed as the design space. The PM approved (alignment check passed: the body was faithfully executed). The fresh-eyes post-completion reviewer also approved. The user caught it only after explicit prompting ("is this actually a good fix?").
- **The cleanest fix is invisible.** The actually-clean fix in that incident (have `/quo-spec-review` emit plain-English findings at source, eliminating consumer-side translation entirely) was NOT in the upstream's three-option menu. The workflow had no mechanism to discover it. The user identified it only post-hoc during a critique conversation.
- **Quorum operator trust drift.** Users learn not to trust the workflow's output because it blindly trusts whatever the body author wrote, regardless of whether that author had any codebase context.
- **Failure mode is invisible.** Future similar incidents will be similarly invisible — no role is tasked with catching them.

## Suggested fix

Introduce an **Analyst** role and dispatch it as a new step in `/quo-fix-issue`, between Section 2 (Validate Issue) and Section 3 (per-issue Agent dispatch).

**Analyst role contract** (new file: `agents/analyst.md`):

- Reads the Issue body verbatim and (when `reference_materials` carries a URL) fetches upstream content via `WebFetch`. Treats both as problem-report context, NOT as authoritative design.
- Reads the local codebase: source files implicated by the Issue, relevant SDD section(s), related skills' contracts, adjacent Issue tickets' notes.
- Produces a design proposal grounded in the codebase research: what's actually broken, what the cleanest fix is, why (with explicit reasoning), and what alternatives were considered and rejected (including any solutions the body proposed — naming them and saying why they were kept, refined, or set aside).
- Surfaces the proposal as structured output to the orchestrator (not directly to the user — the orchestrator owns user interaction).

**Orchestrator-side gate** (new section in `skills/quo-fix-issue/SKILL.md`):

- Between current Section 2 (Validate Issue) and Section 3 (Per-issue Agent dispatch), insert a new "Design analysis" section.
- Dispatch the Analyst agent per the cold-dispatch pattern already used for Engineer/Test Writer/Doc Writer.
- When the Analyst returns, surface its proposal to the user via prose (the proposal is free-form analysis, not a finite multi-choice — `AskUserQuestion` is wrong for free-text design feedback) followed by `AskUserQuestion` with `Approve & dispatch Engineer` / `Revise` / `Cancel`.
- On Revise, iterate with the user in prose, optionally re-dispatching the Analyst with additional context.
- On Approve, pass the Analyst's design directive to the Engineer's dispatch prompt as the authoritative design.

**Preconditions / migration.** The Analyst becomes the **eighth required subagent type** in `/quo-fix-issue`'s precondition check (alongside `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`). Users who update the skills directory but not `agents/analyst.md` (or who update both but don't restart Claude Code / run `/agents` to hot-reload) hit the existing hard-fail at the top of the skill: `Run /quo-setup first. — required subagent type 'analyst' is not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` This is the same precondition discipline already used for the seven existing subagents; no new failure mode invented, just an extension of the existing list. The `/quo-execute` flow (Plan-Bee-driven execution, not fix mode) does NOT pick up the Analyst — design analysis there happens via `/quo-plan` upstream of execution.

**Model assignment.** The Analyst does substantive codebase research and design reasoning — Opus. Not user-configurable (same standard as Engineer/Test Writer/Code Reviewer/Test Reviewer).

**Files affected:**
- `agents/analyst.md` — new role file.
- `skills/quo-fix-issue/SKILL.md` — new "Design analysis" section between Section 2 and Section 3; orchestrator wiring; precondition list extended to eight subagents.
- `docs/sdd.md` — record the new role and the new gate as an architectural addition.
- `README.md` skill catalog — no change (no new skill, just a new role).

## Background and rationale

The b.o6r incident is the canonical example. The upstream Issue (https://github.com/jes5e/quorum/issues/5) was filed by a quorum operator who proposed three solutions; the actually-clean fix was a fourth option not in the menu. The workflow shipped the upstream's "Option 1 + Option 2 hybrid" — the Engineer's own report explicitly argued Option 2 was fragile, and shipped it anyway because the upstream framed the design space that way. The user caught the problem only by asking "is this actually a good fix?" during post-hoc critique. The full sequence (file → fix → critique → revert) lived briefly on `main` and was reverted via session force-push.

The deeper observation: Issue body authors come in a wide quality range. The naive end is "some rando in a different repo who spent a few seconds proposing fixes" — or a local user who filed a quick bee ticket without doing codebase research. The thorough end is someone who actually researched the codebase before filing (possibly authored from a Claude Code session in this codebase as a pre-step). The workflow needs to handle both well — and the way to do that is NOT to classify the body upfront (that's fragile) but to do our own research and let the research naturally absorb whatever context the body provides. When the body is good, our research agrees with it; when the body is shallow, our research diverges. Either way, the user sees an informed recommendation.

This is the same logic that motivated the trailer-as-artifact pattern (b.sfy): put load-bearing analysis where it travels with the artifact the agent actually re-reads, rather than relying on orchestrator-attention recall. Here we extend it: put design analysis where it happens BEFORE the Engineer is dispatched, on the basis of codebase research, rather than relying on the Engineer to silently reconcile a possibly-bad framing during implementation.

## Decisions and rejected alternatives

**Suggested fix: introduce an Analyst role with its own dispatch step before the Engineer.** Pros: clear separation of "design analysis" from "implementation"; the Engineer is dispatched with an unambiguous design directive; the user reacts to an informed proposal rather than a raw body menu; the workflow naturally absorbs body-context quality without needing to classify it. Cons: adds one role, one dispatch, one user-interaction gate to fix-mode flow.

**Rejected: surface the body's proposed solutions to the user via `AskUserQuestion` and let them pick one.** Treats the body's brainstorm as a menu, which is exactly the failure mode this Issue is filed to fix. The cleanest fix is often not in the body's options at all. The earlier draft of this very Issue made this mistake; reframed during user review.

**Rejected: have the Engineer surface tradeoffs to the orchestrator when multiple solutions are proposed.** Re-introduces the orchestrator-attention-decay risk the trailer-as-artifact pattern is designed to avoid. The Engineer's report in the b.o6r incident DID surface the tradeoff ("Option 2 is fragile"), and the orchestrator missed it. A worker-to-orchestrator channel that depends on the orchestrator remembering to read and act on it is fragile by construction.

**Rejected: add a "spec-quality" review pass to `agents/pm.md` that runs BEFORE the Engineer dispatch.** PM today is a post-implementation alignment check. Mixing "design before work begins" into the same role muddles its lane (the same agent would both propose the design and judge alignment to it — grading its own homework). Cleaner to introduce a separate Analyst role.

**Rejected: route every fix through `/quo-plan` first to produce a PRD/SDD.** Too heavy. `/quo-plan` is for new features; a bug fix doesn't need a full PRD/SDD. The Analyst is a lighter-weight version of the same kind of analysis, scoped to a single Issue.

**Rejected: classify the body upfront (well-researched vs. casual brainstorm) and only dispatch the Analyst on the casual branch.** Fragile classification heuristic, and the failure mode (mis-classify a casual issue as well-researched and trust its bad framing) is exactly what this Issue is filed to fix. Always running the Analyst is the safe shape — when the body IS well-researched, the Analyst's research agrees with it cheaply (prompt-caching helps), so the overhead is bounded.

**Rejected: dispatch the Analyst only when `reference_materials` is non-empty (external-reference mode).** Scopes the fix to upstream-GH-sourced Issues only, missing the bee-ticket-only path entirely. A locally-filed Issue can carry just-as-shallow a proposed-fix as a GH ticket — the Analyst's value isn't about the source URL, it's about challenging whatever the body proposes against the actual codebase. Always-dispatch is the right default; conditional dispatch would just re-introduce the trust-the-body failure mode on the un-gated branch.

