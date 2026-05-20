---
id: b.dgq
type: bee
title: Phase skills silently drop "defer to next session" items at session handoff
status: open
created_at: '2026-05-20T14:25:06.166679'
schema_version: '0.1'
reference_materials: null
guid: dgq7h59ck39eedyi6rzfu283vwh482fw
---

## Description

Phase skills (`/quo-plan`, `/quo-breakdown-epic`, `/quo-execute`, `/quo-fix-issue`) routinely have the team-lead orchestrator (or a dispatched agent) flag items as "defer to execution / address later / handle in fix mode / address during Epic implementation / pick up during /quo-breakdown-epic" during a run, without encoding the deferred item into a durable carrier (ticket body update or new Issue) before the run ends. Each phase skill ends by recommending a fresh Claude Code session for the next phase — which is correct, because flat orchestration plus the Epic-boundary context-clear is load-bearing for context-budget management on long Bees. But fresh sessions read only bees tickets, CLAUDE.md, and source code; they have zero visibility into the prior session's conversation. Any deferral that was not written to a ticket is silently lost.

## Current behavior

During a phase skill's run, the team-lead orchestrator may surface items it judges should be addressed in a later phase. The skill then returns control and recommends a fresh session for the next phase. The deferred items live only in the prior session's conversation. When the next session starts, it reads tickets, CLAUDE.md, and code — it sees no record of the deferrals. They are effectively forgotten.

Concrete example from a `/quo-plan` run today: the team-lead proposed 5 amendments to the just-authored PRD/SDD/Plan-Bee/Epic set and recommended "do amendments 1+2 now, defer 3-5 to per-Epic implementation." When questioned on "how will the next `/quo-execute` session even know about 4 and 5?", the team-lead correctly realized that "defer to execution" was sloppy framing and addressed all 5 in-session. The underlying skill prose offered no guardrail against the original sloppy framing — only the user's pointed question caught it.

## Expected behavior

Each phase skill (`/quo-plan`, `/quo-breakdown-epic`, `/quo-execute`, `/quo-fix-issue`) carries a "Before handoff (deferral hygiene)" gate near the end of its workflow, invoked before the skill returns control to the user. The gate:

1. Enumerates every item the team-lead or any dispatched agent flagged with "defer / later / follow-up / address during X / handle in next phase / pick up during Y" semantics during the run.
2. For each item, requires confirmation that it has been encoded in a durable carrier:
   - A ticket-body update (Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or project PRD/SDD via the doc-writer pass — whichever the next phase actually reads), OR
   - A new Issue filed via `/quo-file-issue` (the Issues hive is the natural catch-all for cross-cutting follow-ups not tied to a specific planned ticket).
3. Hard-stops if any flagged item is unaccounted for — the skill cannot return until each deferral is resolved.

Agent role contracts also tightened so dispatched agents stop offering vague "defer to X" recommendations. `agents/pm.md`'s "Final report contract" — when the PM recommends deferring any review-surfaced finding, the recommendation must name a destination (existing ticket body, new Issue, or "addressed now in this Task"). `agents/analyst.md`'s verdict trailers (`recommend-with-refinements`, `recommend-different-approach`, `escalate-to-user`) — when the Analyst proposes refinements the orchestrator might defer to implementation, the verdict must indicate whether each refinement is in-scope-for-this-Issue, defer-to-new-Issue, or defer-to-existing-ticket-body-update (and name which ticket body). Code/test/doc reviewer contracts may need the same principle — engineer to confirm during implementation.

## Impact

- **Correctness.** Closes a known data-loss failure mode in cross-session handoff: items the team-lead judges important enough to surface and "defer" routinely vanish when the next session starts cold.
- **UX.** Users no longer have to notice the loss themselves and figure out, mid-workflow, what to do about it.
- **Workflow integrity.** Makes explicit and enforced what is currently implicit and routinely violated: the bees ticket store is the only durable inter-session channel.

## Suggested fix

Coordinated edit across four phase skills and at least two agent contracts. Files implicated:

- `skills/quo-plan/SKILL.md` — add "Before handoff (deferral hygiene)" between the existing Step 5/6 final operations and the end-of-skill report.
- `skills/quo-breakdown-epic/SKILL.md` — add the same gate between Step 6 (commit ticket files) and Step 7 (offer next steps), because Step 7 explicitly recommends a fresh session.
- `skills/quo-execute/SKILL.md` — strengthen Section 7 (Final Output) so it enumerates deferrals from the full Epic loop, not just the Section 6 post-completion review findings. Section 6's existing Fix/File/Skip pattern is the right shape and should be reused; this is about widening its scope to deferrals surfaced anywhere during the run.
- `skills/quo-fix-issue/SKILL.md` — add the gate between Step 7 (mark issue done + commit) and Step 8 (post-completion review), or fold into Step 8's existing Fix/File/Skip pattern.
- `agents/pm.md` — tighten the "Final report contract" so "defer" items must name a destination.
- `agents/analyst.md` — tighten the verdict-trailer contract so deferred-refinement recommendations name a destination.
- Possibly `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md` — engineer to confirm during implementation whether their finding outputs have a "defer this" surface that needs the same tightening.

The gate's prose should reuse the Section-6-of-`/quo-execute` shape (Fix in this session / File as issue tickets / Skip and surface in summary) as the canonical pattern — that is the existing partial mechanism, and a uniform shape across phase skills is the design goal.

## Background and rationale

The cross-session SDLC architecture (each phase recommends a fresh session) is load-bearing for context-budget management. `/quo-execute` Section 4.2 explicitly invokes "Epic-boundary context-clear discipline" to keep the orchestrator's working set bounded at ~25-30% of the 1M context window per Epic; flat orchestration (no recursive delegation) plus per-Epic context clearing is the architectural answer to long Bees not blowing up the context window. The fresh-session recommendation across phase boundaries is not a workaround — it is the design.

The gap is that some team-lead and agent behaviors implicitly assume conversation continuity ("defer X to later") that does not survive the session boundary. The fix is not to abandon fresh-session handoffs; it is to make the durable-artifact contract explicit and enforced.

Existing partial mechanisms that the fix must NOT duplicate (each surfaces items within a single run, but none bridges to the next session):

- `/quo-execute` Section 5: requires ignored reviewer feedback to be presented in Final Review (within a single run).
- `/quo-execute` Section 6: explicit "Fix in this session / File as issue tickets / Skip" branching — exactly the right pattern, but scoped to one specific reviewer pass at the very end of `/quo-execute`, not to every deferral surfaced during the run.
- `/quo-execute` Section 7: shows ignored feedback at Bee close-out (display only — no requirement to encode in a durable carrier).
- `/quo-plan` Step 4c End-of-Step-4 summary: captures acknowledged findings, overridden blockers, and time-budget-deferred items for the end-of-skill report (display only).
- `agents/pm.md` "Final report contract": requires ignored reviewer feedback be surfaced (within the per-Task report, no cross-session bridge).

The fix layers on top of these mechanisms rather than replacing any of them. The Section 6 Fix/File/Skip pattern in `/quo-execute` is the canonical shape to generalize.

## Decisions and rejected alternatives

- **Rejected: relax the fresh-session recommendation and pass conversation state across sessions.** This breaks the flat-orchestration + Epic-boundary-context-clear architecture that is load-bearing for long Bees. Doing this to fix deferral-hygiene would trade a recoverable failure mode (lost deferrals) for an unrecoverable one (context blowup mid-Bee).
- **Rejected: only fix `/quo-plan` since that's where the user encountered it today.** The failure mode is cross-cutting — `/quo-execute`, `/quo-breakdown-epic`, and `/quo-fix-issue` all exhibit the same recommend-fresh-session pattern at their tail. Per-skill ad-hoc solutions would fragment the deferral-hygiene UX across the workflow.
- **Rejected: a new dedicated "deferral tracker" skill or artifact.** The Issues hive already exists as the catch-all carrier; ticket-body updates handle in-scope deferrals. A new artifact would be redundant and would add a fifth tracking surface (alongside Plans, Issues, Specs, and the working diff) for users to monitor.
- **Rejected: split into multiple smaller issues per file changed.** The fix is coherent: same root cause, same fix pattern, same review criteria across all the affected files. Per `/quo-file-issue`'s house style ("bundle related issues into fewer tickets"), one ticket is the right shape; the engineer treats it as a coordinated edit across files rather than separate per-file passes.

