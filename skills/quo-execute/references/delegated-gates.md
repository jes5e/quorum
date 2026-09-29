# Delegated gates reference

Read at launch when the run is given `--decider`, and after a compaction when the manifest's `**Decider:**` names a session. Unread, the run asks the operator, always a correct gate.

## Introduction

Once the launch check confirms the decider, send it this message, once, before any question; a failed send is handled as under Fallback.

```
quorum decider: <skill> <arguments>, run by session <this session's name>
The operator launched this run naming you its decider: questions it would ask the operator come to you.
Each arrives as a `quorum gate:` message naming a gate file; read that file in full.
Reply to the sender by message, naming the gate file, with a choice label or free text.
Answer as the operator's delegate; when you judge a human answer is needed, ask the operator in your own session.
```

## What goes to the decider

After the manifest write, every question the run would put to the operator goes to the decider: every gate, every prose question, and those of a skill invoked inline, fronted by this run's manifest. The decider alone decides whether a human answer is needed. Where the skill names the operator or the user as the one who answers, discusses, or states a reason, read whoever answered; discuss by message.

## Firing

The decider cannot see this session's screen, so it reads the artifacts, not a retelling. In one turn: the gate file, the manifest's `## Open gate`, the send; then end the turn.

- **Gate file:** `gate-<short-suffix>.md` under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), its directory created if absent, never deleted. Headings: `# Gate: <name> — <skill>, <scope>`; `## Question`, verbatim; `## Choices`, labels verbatim with descriptions, or `free text`; `## Context`, what the operator would have seen: paths to the files holding it, and content held only in this conversation (a return, a finding) copied verbatim under its own headings.
- **`## Open gate`:** the usual entry plus `delegated to <decider>: <gate file path>`.
- **Message:** `SendMessage` to the decider with `notify_when_idle: true`.

```
quorum gate: <gate name>, <scope>
Choices: <label> | <label> | … (or: free text)
Gate file: <path> — read it in full.
Reply to this message's sender naming the gate file, with a choice label or free text.
```

## The answer

The answer is whichever arrives first: a cross-session message whose `from-name` is the decider, or operator text typed into this session that answers it. Read it as `Type something.` text is read. While the gate is open, anything else gets its bookkeeping and no dispatch, because `AskUserQuestion` would have held the run still.

Before acting, append `## Answer` to the gate file: `Source:` the decider's name, `operator`, or `operator (fallback)`, then the text verbatim. A reply naming another gate's file, or arriving once no gate is open, answers nothing.

## Fallback

A failed send, or a delivery notice that it was held or refused, falls back at once: ask the operator, source `operator (fallback)`. An idle, exit, or expiry notice about the decider with the question unanswered calls for `ListAgents`: one no longer listed falls back the same way; a listed one may be asking its human, so keep waiting.

## After a compaction

A delegated `## Open gate` is never re-sent: read its gate file and act on a recorded `## Answer`, or keep waiting as above. A new session resuming the run fires it again when no `## Answer` is recorded, to its own `**Decider:**` or, when that is `none`, to the operator, since the decider replies to the session that sent it.
