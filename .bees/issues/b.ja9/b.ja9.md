---
id: b.ja9
type: bee
title: Epic-boundary context-clear discipline instructs an unexecutable action; rewrite as state-externalization + run-state manifest
status: open
created_at: '2026-08-15T18:08:57.557520'
schema_version: '0.1'
reference_materials: null
guid: ja9s7n9wyqpncg73srfc7j6yzh2i3ib3
---

## Description

The orchestrator skills tell the model to perform an action it cannot perform: "clear your working context" at each Epic/Issue boundary. `skills/quo-execute/SKILL.md` Section 4.2 defines this "Epic-boundary context-clear discipline" (invoked on both the Mode 1 continue path and the Mode 2 auto-continue path), and Section 3 ("Recursive delegation: not supported") states as fact that it "clears the orchestrator's context window between Epics." No such model-invocable mechanism exists, so the instruction is wishful prose.

## Current behavior

- Section 4.2's discipline instructs the orchestrator to clear its own context at the Epic boundary; Section 3 asserts this happens.
- Verified (official Claude Code docs + live probe, 2026-08-14/15): the model **cannot** clear or compact its own context. `/clear` and `/compact` are user-only commands; automatic compaction fires on its own at ~83% of the window (only *lowerable* via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` / the `autoCompactWindow` setting); model-initiated compaction is an **open** upstream feature request (anthropics/claude-code#33026), not shipped. An orchestrator reaching the instruction can only NARRATE compliance — the narrate-instead-of-do failure mode already documented in `CONTRIBUTING.md` `## Known limitations` (the b.sfy / b.fpm / b.wii chain).
- Additional stale/false claims that travel with the same defect:
  - (a) The Mode-2 option text in `skills/quo-execute/SKILL.md` (~line 188), `docs/prd.md` (~line 190), and `docs/sdd.md` (~line 254) says Mode 2 still "pauses on" the Epic-boundary context-clear discipline. Section 4.2 branch 2 does **not** pause there — it auto-continues with a one-line note.
  - (b) The "~25–30% of the 1M context window per Epic" budget in Section 4.2 is neither measurable nor enforceable by the model.
  - (c) `skills/quo-breakdown-epic/SKILL.md` (~line 415) claims that "when this skill returns at Section 7, the orchestrator's working context is released back to the caller's session." False: skills run inline, so returning releases nothing; and under Mode 2 auto-continue (~line 747) the skill does not even return — it loops in-session across Epics with **no** boundary discipline at all.
  - (d) `skills/quo-fix-issue/SKILL.md` `all`/list mode (~line 95) explicitly declares "no inter-issue cleanup ceremony is needed" and carries no context discipline of any kind.

## Expected behavior

- **Rewrite the discipline honestly** as an Epic-boundary (and Issue-boundary) **state-externalization** discipline. At the boundary the orchestrator:
  1. verifies all load-bearing state is already externalized to durable carriers (bees ticket statuses flipped, per-Task/Issue commits landed, compromise tracker on disk, TaskList entries closed) — which it is, by construction;
  2. treats prior-Epic/Issue **conversation** as non-authoritative from that point on, re-deriving all next-unit state from bees/git rather than memory;
  3. states honestly that token reclamation is owned by the harness (automatic microcompaction of old tool results + auto-compaction at ~83%), and this discipline's job is to guarantee that whenever compaction fires — **including mid-Epic** — nothing is lost.
- **Add a run-state manifest.** At run start, write the run-scoped values that otherwise live only in conversation (the captured multi-Epic run mode, the pre-Bee SHA, the compromise-tracker path, the isolation-strategy choice) to a durable scratch file under the standard `<tempdir>/.quorum/` scratch-file convention, updated at Epic boundaries.
- **Add a post-compaction recovery instruction.** If the orchestrator notices its context was summarized, treat the summary as non-authoritative and run a full Read-state reconciliation tick (bees + TaskList + git + run-state manifest) before dispatching anything.
- **Apply to all three orchestrators**: `quo-execute` Section 4.2, `quo-breakdown-epic` Mode 2 auto-continue (~line 747), and `quo-fix-issue` `all`/list inter-issue boundary. Fix claims (a)–(d) and bring `docs/prd.md` / `docs/sdd.md` into line.
- Add a `## Known limitations` entry in `CONTRIBUTING.md` recording that model-initiated context clearing is unavailable upstream (mechanism-unavailable class), cross-referencing the separately-filed upstream re-probe Issue.

## Impact

Correctness / maintainer-trust defect. The prose tells maintainers the design does something it cannot, and instructs the model to perform an impossible action — producing narrate-instead-of-do stalls on long Mode 2 runs, and leaving `quo-breakdown-epic` Mode 2 and `quo-fix-issue all` with no boundary discipline at all. This is the **foundation fix** that makes harness compaction lossless whenever it fires. A separate follow-up feature — a statusline-fed Epic-boundary context guard that stops gracefully *before* compaction — will build on this corrected framing and is being planned separately via `/quo-plan`; it should not block this defect fix.

## Suggested fix

As in Expected behavior. Sequence the honesty rewrite ahead of the guard feature. Because this is skill-prose + docs work in **this** repo, the three quorum design rules plus the scratch-file convention apply as review criteria: the run-state manifest scratch file must follow the `<tempdir>/.quorum/` convention with paired POSIX + PowerShell snippets and no `rm` / `Remove-Item` cleanup.

Key files: `skills/quo-execute/SKILL.md` (Section 3 + Section 4.2), `skills/quo-breakdown-epic/SKILL.md` (~415, ~747), `skills/quo-fix-issue/SKILL.md` (~95 + inter-issue boundary), `docs/prd.md` (~190), `docs/sdd.md` (~74, ~254), `CONTRIBUTING.md` (`## Known limitations`).

## Background and rationale

Diagnosed in an investigation on 2026-08-14/15. The architecture is already compaction-safe — all load-bearing state is externalized at boundaries — so only the imperative sentence pretends at a mechanism that does not exist; the fix is prose honesty plus two small durability additions, not a redesign. Root cause ruled in: the phrase was minted in the b.5tm Epic-8s rewrite as the replacement for the old team-disband ceremony and was never load-tested against whether the model can execute it. Design-philosophy match: `docs/sdd.md` already prefers enforcement "through a substrate ... rather than through a rule the model can drop" — the context-clear is exactly such a droppable rule and should be reframed accordingly. Unlike the warm-Agent gap (which got an audit trail via a re-probe Issue + in-skill callout + SDD note), this discipline received no such skepticism; the sweep found zero tickets/docs questioning its executability.

## Decisions and rejected alternatives

- **Rejected: pass conversation state across sessions / relax the fresh-session recommendation.** This is the design the honesty fix depends on (fresh sessions read only bees/CLAUDE.md/source), and relaxing it trades a recoverable failure (lost deferrals) for an unrecoverable one (context blowup mid-Bee) — already rejected in Issue b.dgq.
- **Rejected: keep the "clear your context" wording and rely on the model to do it.** The whole point of the defect is that it cannot; retaining it is the narrate-instead-of-do trap CONTRIBUTING.md already documents.
- **Rejected: fold this into the context-guard feature.** The honesty fix is independent (the guard depends on it, not vice versa), is a real defect that should be corrected promptly, and is lower-risk; coupling it to a larger feature would delay a certain, simple correction.

## Doc divergence noted

- `docs/sdd.md` (Internal architecture docs (SDD), ~line 254) and `docs/prd.md` (PRD, ~line 190) both state that Mode 2 "pauses on" the Epic-boundary context-clear discipline, which does not match `quo-execute` Section 4.2 branch 2's auto-continue behavior.
- `docs/sdd.md` (~line 75) documents the Epic-boundary context-clear discipline as the bound on flat-orchestration context growth, framed as an already-working mechanism. Both docs must be updated in step with the skill-prose rewrite so the SDD/PRD describe state-externalization + harness-owned compaction rather than a model-invoked context clear.

