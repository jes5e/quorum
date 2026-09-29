---
id: b.d7t
type: bee
title: 'Delegated gates: a quorum skill sends its gates to a named decider session (or its parent) instead of asking the operator'
up_dependencies:
- b.rqc
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:48.019034'
status: done
schema_version: '0.1'
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

## Step 1 spike results (Claude Code 2.1.283, host, 2026-09-27/28)

Evidence in `/tmp/.quorum/spike-d7t/logs`; report `/tmp/.quorum/bd7t-checkpoint-2.md`. The operator's big feature started before the spike, so the sequencing above was overtaken; the spike ran beside it.

**Separate-session variant: pass.**
- Basic round trip (message a named session, end the turn, resume mid-task on the reply, multi-line free text intact): observed in everyday overseer↔worker use across b.87t, b.rqc, and this spike; not re-tested.
- A lane notification while a delegated gate is pending: the worker is idle, not blocked, so every notification wakes it. Re-reading the manifest each turn, it kept `## Open gate` filled through a child's hand-back and two task-notifications (interim, then final), then resumed at the right step on the decider's reply.
- The operator typing the answer directly: it arrives as an unwrapped user turn, distinguishable from `<cross-session-message from-name=...>`, and was recorded as source=operator. A non-recipient peer's instruction was refused under the probe's rule; the operator's typed line overrode it.
- The decider disappearing while a gate is pending: the send succeeded while the decider was alive. Its exit (a `-p` session) produced an *idle* notice, not an exit notice (`[Cross-session idle notice] "d7t-ghost" ... is idle now — it finished a turn ... Its harness reports: «bye».`), then silence, since the subscription is one-shot. `ListAgents` dropped the row, and a re-send failed: `No agent named 'd7t-ghost' is reachable.` The fallback `AskUserQuestion` to the operator worked. Not tested: an interactive decider closed mid-wait.
- Permission-class and host↔container tests dropped: all real sessions run the same way in one container (operator).

**Subagent variant (decider = parent, worker = background subagent): the round trip passes, but it fails for real runs.**
- Pass: a background subagent invokes a skill and follows it; waits for its own children across turns; resumes its own child by agent ID after its own gate cycle; gates via `SubagentHandback` (once per run) or `SendMessage(to=main)`, answered by the parent's `SendMessage`; resumes with full context, repeatedly, including through a parent exit/resume while idle at a gate. Nested children's task-notifications carry `subagent_tokens` / `tool_uses` / `duration_ms`.
- Fail: exiting the parent (after a confirmation prompt) killed a running grandchild (`Exit code 137`) with no notification. After the resume the worker still believed the lane was running: a silent hang. The killed child was resumable by agent ID once the worker was told.
- The worker has no `AskUserQuestion` and no `ListAgents`, and its `CLAUDE_CODE_SESSION_ID` is the parent's, so the context guard would read the decider's gauge.
- Not tested: subagent compaction (`CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=15` did not force it; peak 124,143 tokens on haiku, no `compact_boundary`).

**Recommendation (spike worker, overseer concurs):** build the separate-session variant only, with a named decider session as the recipient. The subagent variant needs machinery the separate-session variant doesn't: lane-death detection after a decider restart, guard re-keying, and a second route for operator fallback.

**Out of scope, to route:** (1) ~~the `Agent` tool has no `name` parameter~~ Checked and withdrawn (overseer, 2026-09-28, 2.1.283, agent teams off): the tool's listed schema omits `name`, which is why the spike's agents concluded it was absent, but an `Agent` call passing `name` is accepted, the hand-back arrives from that name, and `SendMessage(to=<name>)` resumes the agent. This matches the docs' `### Subagent names`. The orchestrators' named dispatch and resume-by-name work without agent teams; no Issue. (2) Task-notifications can fire more than once per agent (interim plus final), and the report arrives as a separate `<agent-message>`; this touches the ledger and "read its return". No quorum run has shown a failure from it yet. (3) Foreground `sleep` is blocked by a tool-use guard.

**Open for step 2's design checkpoint:** REWRITE-BRIEF §4 says no reference file may be required to make a gate fire, which a shared delegation reference would need amended; the run-start gates that fire before the manifest exists (effort, pick, isolation); and the solo spec writers' file-write-fronted gate.

## Step 2 build and validation; closed (2026-09-29)

Merged to main by fast-forward, head `1634316` (commits `a78d19c`..`1634316`), not pushed. Separate-session variant only. A run launched with `--decider "<session name>"` sends every question it would put to the operator after its manifest write to that session: gates and prose questions, including an inline `/quo-file-issue`'s. The contract lives once in `skills/quo-execute/references/delegated-gates.md` (561 words; REWRITE-BRIEF §4 amended). Each question writes a gate file (question, choices, context by path or copied verbatim, then `## Answer` with its source) and sends a `quorum gate:` message. The run introduces itself to the decider once at launch. Shipped prose +1,140 words.

**Operator decisions (2026-09-28).**
- D1: no operator-only gate after launch ("the decider is the only thing that determines it needs a human answer"). Only the pre-manifest launch questions stay with the operator.
- D2: `--decider "<name>"`; a bare `--decider` lists every live session and stops.
- D3: a name no live session answers to stops the run at launch.
- D4: prose questions delegate too.
- D5: scope is execute, fix-issue, breakdown, plan, and inline `/quo-file-issue`. Out: plan-from-specs, setup, and the solo spec writers.
- Later the same day: the run introduces itself (no manual priming).

**Review.** Three cold rounds, closing clean.
- Deleted: the overseer's suggested re-subscribe on an idle notice. A subscription to an already-idle session fires at once, so it would loop.
- Documented residual: a decider still listed at its idle notice that later closes leaves the run visibly waiting for the operator.
- Added: a reply must name its gate file, or it answers nothing, so that after an operator override a late reply cannot land on the next gate.
- Execute's Analyst gate keeps its re-derive exception after a compaction.

**Paraphrase evidence (corrected).** b.v9c's Operator-action gate and b.y3m's Analyst gate.

**Validation (live_edit, 2026-09-28/29).** Three concurrent runs shared one decider ("Performance Planner 3"): `/quo-fix-issue b.v6i b.e1h` (10 questions), `/quo-plan` b.ayp (6), and `/quo-breakdown-epic` b.mqs (3).
- All 19 were answered by the decider; 18 of 19 replies named the gate file (the other arrived with no other gate open).
- 0 fallbacks, 0 operator overrides, 0 re-sends, and no cross-run mix-up. The decider opened by-path artifacts and verified claims before approving.
- It survived a machine restart mid-Issue (`claude --resume`, killed-lane recovery) and a context-full stop (a fresh session, told to skip run start, still delegated from `**Decider:**`).
- Improvised without harm: descriptive gate-file names (unique per fire); two runs kept the decider's standing instructions in improvised manifest text; two gates abridged or restructured conversation-only context and said so. Watch items, not rules.
- Report: `~/.quorum-overseer/bd7t-build-checkpoint-5.md`.

**Lost evidence.** The step-1 note cites `/tmp/.quorum/bd7t-checkpoint-2.md` and the spike logs, and Checkpoints 1–4 of step 2 lived in `/tmp/.quorum/`; a macOS restart on 2026-09-28 wiped them. The ticket and commit messages carry the substance.

**Follow-ups.** The `/quo-fix-issue` resume gaps the validation exposed are filed separately. The execute Analyst proposal-file idea is a note on b.h1t.
