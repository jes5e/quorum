# Delegated gates reference

Read at run start when the manifest's `**Decider:**` names a session, and after a compaction. Unread, it leaves the run asking the operator, always a correct gate.

## What goes to the decider

After the manifest write, every question the run would put to the operator goes to the decider: every gate, every prose question, and those of a skill invoked inline, fronted by this run's manifest. The decider alone decides whether a human answer is needed. Where the skill names the operator or the user as the one who answers, discusses, re-issues a choice, or states a reason, read whoever answered, and discuss by message.

## Firing

The decider cannot see this session's screen, so it reads the artifacts, not a retelling. In one turn, write the gate file, then the manifest's `## Open gate`, then send, and end the turn.

- **Gate file:** `gate-<short-suffix>.md` under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), created if absent, never deleted. Headings: `# Gate: <name> — <skill>, <scope>`; `## Question`, verbatim; `## Choices`, labels verbatim with descriptions, or `free text`; `## Context`, what the operator would have seen: paths to the files holding it, and content held only in this conversation (a return, a finding) copied verbatim under its own headings.
- **`## Open gate`:** the usual entry plus `delegated to <decider>: <gate file path>`.
- **Message:** `SendMessage` to the decider with `notify_when_idle: true`.

```
quorum gate: <question, verbatim>
Choices: <label> | <label> | … (or: free text)
Gate file: <path> — read it in full before answering.
Reply to this message's sender with a choice label or free text.
```

## The answer

The answer is whichever arrives first: a cross-session message whose `from-name` is the decider, or operator text typed into this session that answers the question. Read it as `Type something.` text is read. While the gate is open, anything else gets its bookkeeping and no dispatch, because `AskUserQuestion` would have held the run still.

Before acting on it, append `## Answer` to the gate file: `Source:` the decider's name, `operator`, or `operator (fallback)`, then the text verbatim. A later reply answers nothing.

## Fallback

A failed send, or a delivery notice that it was held or refused, falls back at once: ask the operator, source `operator (fallback)`. An idle, exit, or expiry notice about the decider while the question is still unanswered calls for `ListAgents`: one no longer listed falls back the same way; a listed one may be asking its own human, so keep waiting.

## After a compaction

A delegated `## Open gate` is never re-sent: read its gate file and act on a recorded `## Answer`, or keep waiting under the fallback rule.
