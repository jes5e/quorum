---
id: b.d7t
type: bee
title: 'Delegated gates: a quorum skill sends its gates to a named decider session (or its parent) instead of asking the operator'
up_dependencies:
- b.rqc
status: open
created_at: '2026-09-27T14:04:48.019034'
schema_version: '0.1'
reference_materials: null
guid: d7tbc1pae6xfp9wjc4cx74bhwk8dzqub
---

## Description

Let a quorum skill send its gates to a decider session the operator names, instead of prompting the operator. Today every gate is an `AskUserQuestion` in the running session. The operator keeps a separate decider Claude session, and at almost every gate picks "Type something" and pastes that session's reply, rarely taking a listed option (operator, 2026-09-26). So each gate costs a human relay of text between two agents.

## Current behavior

- Every gate in `/quo-execute`, `/quo-fix-issue`, `/quo-plan`, and `/quo-breakdown-epic` (and the solo spec writers) is a manifest `## Open gate` write plus `AskUserQuestion` in the same turn; the operator must be at the terminal to answer.
- A cross-session message cannot answer a pending `AskUserQuestion`: the session is blocked on the prompt, and Claude Code does not treat a peer message as the user's approval for a pending prompt.

## Expected behavior

At run start the operator can name a decider session (an argument, or one question). The address is the session's name, which the operator sets with `/rename` in that session; an unnamed session has a generated one. `ListAgents` shows the live sessions and their names, so the skill can confirm the decider exists before relying on it; names should be unique among live sessions, or the short ref disambiguates. Then each gate:
- is still written to the manifest's `## Open gate`, as the structural guard against a narrated gate;
- is sent to the decider with `SendMessage`, carrying the question, the choices, and the context the operator would have seen (for example the Analyst's proposal text, since the decider cannot see this session's screen);
- takes the decider's reply as the answer, free text included, recorded verbatim in the manifest with its source;
- leaves the operator able to see every message and interrupt at any time.

Some gates may stay operator-only (for example marking a Bee done); the design decides which.

## Considerations for the design

- Every skill with gates is in scope. The gate definition is shared text (Tier 1 in the two orchestrators, and the same shape in the planning skills), so change it in one pass.
- The operator authorizes the delegation once, at run start, in the running session; no peer message stands in for approval of a pending prompt, because none is pending.
- Both sessions must share a permission mode, or cross-session messages are held for approval.
- Cross-session messages carry text only; an `@` path attaches nothing.
- The decider is another agent's judgment on operator decisions; record every delegated answer and its source so validation triage can see what the decider decided.

## Variant: the worker as a subagent of the decider (operator question, 2026-09-26)

The operator asked whether the decider could instead be the main session, with the quorum worker as its subagent. What the Claude Code docs say (`code.claude.com/docs/en/sub-agents.md`, checked 2026-09-26):
- Nested subagents are on by default, "up to three layers below the main conversation" (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` changes it); decider → worker → role agents needs two.
- A subagent can invoke skills through the Skill tool, and a background subagent keeps `Agent`, `SendMessage`, `Skill`, `Bash`, `Edit`, and `Write`.
- `AskUserQuestion` is removed from every subagent, so a worker subagent cannot fire its gates at all; it must send them to its parent. That is this ticket's change with the parent (`main`) as the recipient.
- The parent resumes a completed subagent with `SendMessage`, and it keeps its full history; subagents can message `main` (v2.1.206+). The docs describe resuming after completion, not delivery mid-turn, so a gate would end the worker's turn with the question and resume it with the answer.
- Not documented, to test before relying on it: compaction inside a many-hour subagent; whether a worker subagent waits correctly on its own background agents across turns; the worker's fate when the decider session ends. The operator also can't type into a subagent directly.

The skills' statement "Subagents cannot spawn subagents" is also out of date as a fact about Claude Code, though the orchestrators still dispatch every role themselves.

## Suggested fix

**Step 1: a mechanics spike, before any skill edit (operator decision 2026-09-26).** Test what Claude Code actually does with small throwaway prompts and agents, not a quorum run. Record each result, with the Claude Code version, in this ticket. Nothing is designed or built until this step reports.

Separate-session variant (partly proven: the overseer and worker sessions already exchange checkpoint messages, the worker waiting idle and resuming on the reply):
- a session running a skill fires a "gate" by messaging a named session and ending its turn, and resumes correctly, mid-skill, when the reply arrives;
- the reply's free text arrives intact;
- behavior when the decider session is closed or unnamed (the send fails, and the worker falls back to asking the operator);
- both sessions' permission modes, and what happens when they differ.

Subagent variant (unproven; the docs are silent on the parts it depends on):
- a background subagent invokes a skill and follows it;
- that subagent dispatches its own background agents and waits for their completion notifications across its own turns, without ending and returning to the parent while children still run;
- a gate: the subagent sends the question to `main` (or ends its turn with it), the parent answers with `SendMessage`, and the subagent resumes with its full context, mid-skill, repeatedly;
- a long run: whether a subagent's context is compacted and how, over a run long enough to approach its window;
- what the operator can see and interrupt, and what happens to the subagent when the parent session ends.

**Step 2, decided from the spike.** Build only the variants that passed. Since the skill change is the same for both (a gate writes `## Open gate`, messages the recipient, and takes the reply as the answer), supporting both is one recipient setting (a named session, or the parent) if both pass. Then a design checkpoint (which gates delegate, the message shape, the wait and reply contract, the fallback to the operator), hand edits with a cold review, and a validation run in a code repo with a real decider.

**Where the text lives (recommended starting point, operator question 2026-09-26):** each skill's existing gate rule gains one or two sentences (when a decider is named, send the gate to it per the shared reference instead of asking), because the gate rule is where the agent looks when it fires a gate. Everything else (message shape, which context to include, the stop-and-wait rule, recording the answer and its source, the fallback) lives once in a shared reference file, read at run start when a decider is named and again after a compaction, the way `/quo-fix-issue` already reads `/quo-execute`'s routing reference. One copy of the details, and a sentence or two per skill.

## Sequencing

Operator decision 2026-09-26: after the `/quo-execute` rebuild (b.87t) merges, before the operator's big feature, where gate volume is highest. The spike (step 1) can run as soon as b.87t merges; it touches no skill.

