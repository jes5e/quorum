---
id: b.x9w
type: bee
title: Re-probe SendMessage-without-Agent-Teams as warm-Agent token-cost optimization
status: open
created_at: '2026-05-03T16:11:37.802648'
schema_version: '0.1'
guid: x9wngmdh2gtry51hkmyy4fnmhuwrtky9
reference_materials: null
---
## Description

Track the open question of whether Claude Code's `SendMessage` tool will eventually become available without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. If it does, the bees-execute / bees-fix-issue / bees-breakdown-epic skills should be enhanced to add warm-Agent dispatch as a token-cost optimization, restoring the original SDD intent that Epic 8s (b.5tm) had to diverge from.

## Current behavior

During the `/bees-breakdown-epic` of Epic t1.5tm.8s (under Plan Bee b.5tm — Ephemeral-Agent Orchestration), an architectural decision was made to use **per-Subtask cold dispatch** for Engineer/Test Writer/Doc Writer Agents in the rewritten bees-execute (and by extension bees-fix-issue and bees-breakdown-epic in Epics C/D).

This diverges from the SDD's `### Feature: Ephemeral-Agent Orchestration` `**Cold-start hybrid (warm vs fresh Agents)**` paragraph (lines ~188-193), which originally specified **warm Engineer/Test Writer Agents** via `Agent(name=<task-id>)` + subsequent `SendMessage` across Subtasks within a Task to preserve file-tree context.

The divergence was forced by the official Claude Code sub-agents documentation (https://code.claude.com/docs/en/sub-agents): "The `SendMessage` tool is only available when [agent teams](/en/agent-teams) are enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`." Since b.5tm removes Agent Teams entirely, SendMessage is unavailable and the warm-Agent pattern from the SDD's original intent is structurally impossible at b.5tm shipping time.

## Expected behavior

A periodic empirical probe verifies whether the upstream constraint has changed. If/when it has, a follow-up Plan Bee implements the warm-Agent optimization.

**Probe shape.** Periodically (e.g., when a new Claude Code release ships), empirically verify whether `Agent(name=<some-name>, ...)` followed by `SendMessage(to=<that-name>, ...)` works when `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is NOT set in the environment / settings.json. The probe is a small fixture: spawn a named background Agent with a trivial first task, wait for completion, then SendMessage it a second task and observe whether the message is delivered (success: warm-Agent works without Agent Teams) or rejected with `SendMessage tool not available` / similar (still gated).

**Trigger for action.** If the probe passes (docs are now outdated and SendMessage works without Agent Teams), file a new Plan Bee for "Add warm-Agent dispatch to bees-execute / bees-fix-issue / bees-breakdown-epic as a token-cost optimization" — this would re-introduce the SDD's original warm-Agent intent at per-Task granularity (Engineer warmed across Subtasks within a Task; Test Writer same; Doc Writer optional warm; reviewers and PM still cold per the SDD).

**Issue lifecycle — periodic re-test, do NOT close on first failure.** This Issue is intended to stay open under "periodic re-test" semantics. When a probe fails, append a one-line note (`re-tested YYYY-MM-DD on Claude Code vN.N.N — still gated`) and leave the Issue open. Close only when (a) the probe passes AND a follow-up Bee implementing warm-Agent dispatch lands, or (b) we explicitly decide to drop the optimization permanently.

## Impact

**Token-cost optimization deferred, not lost.** Current per-Subtask cold dispatch costs extra context-load tokens per Subtask vs. the SDD's warm-Agent design. Claude Code's prompt caching (5-min TTL) mitigates most of the cost — subsequent Subtasks within a Task that re-read the same files mostly hit cache — so the practical penalty is bounded. But for Tasks with many tightly-coupled Subtasks, warm dispatch would still save tokens and wall-clock time vs. cold-per-Subtask.

**Maintainer-confusion risk if not tracked.** A future maintainer reading `skills/bees-execute/SKILL.md` Section 3 alone would wonder "why don't we warm the Engineer across Subtasks within a Task?" and might re-introduce the warm pattern without the constraint context. This Issue + the in-skill callout + the SDD note form a triangulated audit trail.

## Suggested fix

**At Issue filing time (now):** none. The divergence is locked in by Epic 8s; the in-skill callout (added by Subtask t3.5tm.8s.mp.4k as part of the Section 3 rewrite) and the SDD note (added by Epic t1.5tm.fy per the appended addendum on its Bee body) reference this Issue's ID once it exists.

**At each periodic re-probe:**
1. Spawn a small fixture: a named background Agent with a trivial first task; wait for completion; SendMessage it a second task.
2. Run with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` unset.
3. If SendMessage is rejected: append the date + Claude Code version to this Issue's body and leave open.
4. If SendMessage works: file a new Plan Bee per the Trigger-for-action above; close this Issue once the new Bee ships.

**Cross-references.**
- Plan Bee that produced the divergence: b.5tm (Ephemeral-Agent Orchestration).
- Epic where the divergence is implemented: t1.5tm.8s (bees-execute rewrite).
- Subtask where the in-skill divergence callout lives: t3.5tm.8s.mp.4k (Section 3 skeleton — "Per-Subtask cold dispatch (vs SDD's warm-Agent intent)" callout paragraph).
- Epic F (t1.5tm.fy) carries an addendum on its body instructing it to add an SDD paragraph documenting this divergence with a reference to this Issue's ID.

