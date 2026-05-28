---
id: b.wii
type: bee
title: Narrate-instead-of-do failure mode persists after b.fpm's prose-strengthening fix
parent: null
reference_materials: null
created_at: '2026-05-20T04:17:48.985945'
status: done
schema_version: '0.1'
guid: wiidq2sng1wr8y4ocek75ei752hb6ud3
---

## Description

The orchestrator routinely emits a routing trailer (e.g., `**Your next tool call MUST be AskUserQuestion** with finite choices ... Do not produce a text response describing this gate — call the tool directly.`) as prose and then yields the turn — instead of firing the prescribed tool call. This is the "narrate-instead-of-do" failure mode that `b.fpm` was filed to fix.

`b.fpm`'s shipped fix was prose-only: strengthen the routing trailers across review skills to the second-person imperative form (`**Your next tool call MUST be ...**`) plus a counter-anchor clause (`Do not produce a text response describing this gate — call the tool directly.`). The mechanism relied entirely on prose strength to compel adherence — no harness-level enforcement, no orchestrator-side self-check, no structural mechanism — and has demonstrably not held. See `## Background and rationale` below for the concrete data point.

## Current behavior

When skill prose prescribes a tool call via the second-person imperative + counter-anchor pattern, the orchestrator sometimes:

- Emits the prescription text as prose.
- Yields the turn (waiting for user input).
- Resumes only after the user surfaces that the gate didn't fire.

Observable across at least:

- `/quo-spec-review`'s three trailer shapes (Shape 1 / Shape 2 / Shape 3) in `skills/quo-spec-review/SKILL.md` `### Step 4: Generate Work Item List`.
- `/quo-plan` Step 5e's verdict-keyed Shape A/B/C trailers in `skills/quo-plan/SKILL.md`.
- Potentially every other location where skill prose says "your next tool call MUST be X." A future grep across `skills/*/SKILL.md` would enumerate the full set; this Issue does not attempt that enumeration because the design conversation comes first.

## Expected behavior

When the prose prescribes a tool call, the orchestrator fires that tool call on the same turn (or the next turn if waiting on a background Agent's completion notification). The orchestrator does NOT emit the prescription as prose and yield. The trailer's `Do not produce a text response describing this gate — call the tool directly.` counter-anchor clause holds reliably, not just most of the time.

## Impact

- **Workflow correctness gates can be silently skipped.** Every `AskUserQuestion`-gated review-loop decision in `/quo-spec-review`, `/quo-plan` Step 5e, and (with `b.tip`) `/quo-fix-issue` + `/quo-execute` is vulnerable to the same failure mode. The user has to catch each missed gate manually.
- **Direct dependency from `b.tip` (in flight).** `b.tip` adds new orchestrator-discipline routing rules to `/quo-fix-issue` and `/quo-execute` that fire user gates via the same prose-strengthening mechanism. If this bug is not structurally fixed, `b.tip`'s routing improvement is moot at the moment the gate is supposed to fire — the orchestrator can emit "**Your next tool call MUST be `AskUserQuestion`**" and yield, exactly recreating `b.fpm`'s failure mode at a new surface. The dependency is documented as a Risk callout in `b.tip`'s PRD and SDD.
- **User-surface friction.** The manual remediation step (user notices the missed gate, prompts the orchestrator to fire it) is exactly what the gates are supposed to eliminate. As more gates land across the workflow (`b.tip` adds several), the cumulative friction grows.

## Suggested fix

This is a **structural fix request**, not a prescribed fix. A design conversation is needed before any fix is attempted — pretending we have a known fix is exactly the kind of soft-fix shipping that `b.tip` is meant to prevent. Candidate directions, none settled:

1. **Harness-level enforcement.** The Claude Code harness detects when the orchestrator emits a `**Your next tool call MUST be X**` string and forces an actual tool call rather than yielding. Out of skill prose's reach; would need a harness change.
2. **Tool-use enforcement at the prompt level.** The Anthropic API supports forcing a specific tool call via `tool_choice`. Skills can't directly invoke this, but a harness wrapper could detect the prescription pattern and inject `tool_choice` so the next turn must include a tool call of the prescribed type.
3. **Pre-commitment self-check turn.** Before emitting any text, the orchestrator explicitly decides "am I about to fire a tool call or write a prose response?" and routes accordingly. Implementable as skill prose discipline but unclear it would work better than b.fpm.
4. **Structural decomposition of gate firing.** Split "decide to gate" from "fire the gate" into two prompted actions with no opportunity to emit text between them. Probably requires harness or scaffolding changes.
5. **Post-yield self-correction.** When the orchestrator returns from a yield and notices "the previous turn prescribed a tool call but I yielded instead," it self-corrects on the new turn. Doesn't prevent the initial failure but reduces user-surface friction.
6. **Stronger pre-commitment in the parent skill prose.** The orchestrating skill itself (not just the embedded reviewer) says before the dispatch: "When the dispatched skill returns, you MUST immediately call X. The skill's trailer will repeat this prescription; treat the trailer as a confirmation, not a new instruction." Tries to redundantly anchor the prescription before the failure point. (Closest to a "more prose" approach; included for completeness but the lesson from `b.fpm` is that pure prose-strengthening is insufficient.)

**Recommended next step:** hold a design conversation about the candidate directions (especially #1 / #2 harness-level enforcement, since the model-side mechanisms have demonstrably failed). Once a direction is settled, this Issue's resolution either lands as a SKILL.md change (skill-prose fixes) or pivots to a `CONTRIBUTING.md` known-limitation note pending harness work (harness-level fixes). The current Issue is intentionally NOT prescribing a specific fix — picking one without the design conversation would repeat `b.fpm`'s pattern.

## Background and rationale

The `b.fpm` prose strengthening **did not hold** in the very session that authored this Issue. Concrete data point: during `/quo-plan` for `b.tip` (the depth-aware finding routing + compromise tracker work), `/quo-spec-review` returned a Shape 2 trailer prescribing `**Your next tool call MUST be AskUserQuestion** with finite choices Proceed (acknowledge findings) / Revise. Do not produce a text response describing this gate — call the tool directly. The Spec Bee's drafted → ready promotion is gated on the user's answer.` — and the orchestrator (this very Claude instance) emitted the trailer as text and yielded the turn anyway, exactly the failure mode `b.fpm` was designed to prevent. The user surfaced the bug; the orchestrator fired the gate on the next turn — but only after the failure had already happened.

This is direct evidence that prose-strengthening alone is insufficient as a structural mechanism for compelling orchestrator gate-firing. The same Claude instance, in the same session, with the `b.fpm`-strengthened prose loaded, still failed it. The bug appears to be a model-adherence failure rather than a prompt-design failure.

The reason this Issue exists as a separate filing (rather than being absorbed into `b.tip`) is that `b.tip` has a load-bearing dependency on the structural fix: its new orchestrator-discipline routing rules user-gate via the same prose-strengthening mechanism. Without a structural fix for adherence, `b.tip`'s gates inherit the same fragility — they will sometimes fire correctly, and sometimes the orchestrator will emit the prescription as text and yield. `b.tip`'s PRD and SDD `## Risk / Known Dependencies` callouts reference this Issue ID explicitly so future readers see the fragility.

## Decisions and rejected alternatives

- **Ship a prose-only retry.** Rejected. `b.fpm` already tried prose strengthening (second-person imperative + counter-anchor); the failure in this session is direct evidence the approach doesn't reliably hold. Trying harder prose without a structural shift would be exactly the soft-fix pattern `b.tip` is meant to prevent.
- **Bundle the structural fix into `b.tip`.** Rejected. `b.tip` does not have a settled design for the structural fix. Adding scope without a design path is over-promising; the appropriate move is to land `b.tip` cleanly with an explicit Risk callout pointing at this Issue, and resolve this Issue once a structural-fix design exists.
- **Treat as a `b.tip` Open Question.** Rejected. An Open Question inside `b.tip` would dilute its scope and leave the structural problem without a discrete home for the design conversation. A separate Issue gives the conversation a place to live and lets `b.tip` ship without absorbing scope it can't honestly deliver on.
- **Defer this filing until a fix design exists.** Rejected. The deferral would mean `b.tip` lands without the Risk callout (since there's no Issue ID to reference), and future readers would have to reconstruct the fragility from session logs. Filing the Issue now — even without a settled fix — anchors the dependency.
