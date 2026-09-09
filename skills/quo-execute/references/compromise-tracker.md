# Compromise tracker reference — rationale, trigger detail, and the Decision-value history

This file is read on demand by `/quo-execute` and `/quo-fix-issue`. The tracker's file name, entry shape, Decision enum, and trigger table live in the invoking skill's body; this file carries the reasoning behind them and the detail a writer needs when a trigger's edge case is in play. Nothing here fires a gate.

## Why the tracker exists

- An accepted compromise — a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override — would otherwise be baked silently into the new baseline.
- The tracker keeps each one visible and challengeable; the post-completion review reads it first and challenges every entry before it sweeps for discrete defects.
- The PM's Final report reads the same file per unit and reports any accepted or improperly deferred `blocker` it records.

## File naming

- The timestamp prefix in `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` makes tracker files debuggably identifiable across many runs accumulated in `<tempdir>/.quorum/`; without it the user has no easy way to map a file to a session.
- The random `<short-suffix>` is acceptable here, unlike the run-state manifest, because the tracker's reader is a dispatched Agent handed the path in its prompt, and the manifest records that path for the orchestrator's own post-compaction recovery.
- A new run always writes its own new file; previous-run files are never appended to.
- The file is a scratch artifact: author and append it via the `Write` tool, never a shell redirect, and never delete it.

## Entry-shape rationale

- `<n>` in `## Compromise <n>` is a 1-based counter scoped to the current run's file, not a globally unique identifier.
- `Finding (verbatim)` carries the severity tag, the fix-path enumeration with depth tags, and the description, so a later reader can re-judge the routing without the conversation.
- `Fix paths surfaced by reviewer` is recorded so the post-completion review can judge under-enumeration; the run-end summaries deliberately hide this field because they show the path that was chosen, not the menu.
- `Rationale` on an ungated pick must be the orchestrator's own one-line reason the path was preferred — why it is the smallest internally-consistent complete change — because a bare rule name gives the post-completion challenge nothing to push against.
- `Rationale` on a `Defer to follow-up Issue` entry names which remaining enumerated path shipped as the soft fix, by letter, or that none did; on a blocker deferral it carries the narrowing record instead. The deferral and what shipped in its place are one decision.
- A blocker deferral without a narrowing record is the shape every downstream consumer reads as a contract violation.

## Trigger detail

- **Trigger A** fires from either gate's `Defer to follow-up Issue` branch. Append the entry immediately after `/quo-file-issue` returns the new Issue ID and before the soft-fix or narrowing dispatch. Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all, which is reachable at gate (d) because its `Defer` is offered whatever the path count. "None did" applies to the single-path case at gate (c) and to every deferral at gate (d), whose `Defer` ships nothing against the finding.
- **Trigger B** fires from gate (c)'s `Accept the limitation` branch. Append immediately after `AskUserQuestion` returns and before continuing without a fix. It is unreachable for a `blocker` because the gate never offers a blocker that choice.
- **Trigger C** has no gate; the write is wired into the row-6 dispatch itself, in the same logical block as the dispatch. A finding whose only fix path is `trivial-tweak` appends nothing; a pick among two or more paths always appends, even when every path is shallow. Row 6 is the only firing site; a user-picked path at gate (c) or (d) is not an ungated route and writes no Trigger C entry.
- **Trigger D** is the single owner of every post-completion-override write. It covers both recovery gates, and its choice labels are byte-identical to theirs so the branches line up. The recovery gates fire the write; they do not author it.

## The two override Decision values

- `User overrode auto-route after post-completion challenge (depth misjudgment)` is written by the SR-6.7 ungated-route recovery gate's `Accept the misjudgment and proceed` branch.
- `User accepted under-enumeration after post-completion challenge` is written by the SR-4.6 under-enumeration recovery gate's `Accept the under-enumeration and proceed` branch.
- Two values exist because Trigger D owns both gates' writes regardless of which fired, and a reader of the file must be able to tell the two overrides apart.
- The SR-6.7 `File follow-up Issue to revisit the depth decision` branch appends nothing new; it updates the originating Trigger C entry's `Follow-up Issue` in place, because a depth misjudgment always concerns a path the orchestrator routed ungated and so always has an originating entry.
- The SR-4.6 `File follow-up Issue to surface the missing path` branch usually has no originating entry to amend, so it appends a new entry with the under-enumeration Decision and the new Issue ID; when an originating Trigger C entry does exist, it updates that entry's `Follow-up Issue` in place instead.
- `Pause to discuss` at either gate defers every tracker write until the user picks `Accept` or `File` again.

## The SR gate labels read generically

- `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and the matching Decision value name the routing misjudgment the challenge landed on, on either PHASE 3 axis — the mechanism axis included, not the depth axis only.
- Read "depth decision" and "misjudgment" that way rather than concluding the mechanism axis has no gate.

## Why PHASE 2 has no recovery gate

- A PHASE 2 contract violation records an acceptance the gates should never have offered, an unnarrowed deferral, or a narrowing that left the stated defect partly unfixed. There is nothing to recover; the aggregate Fix / File / Skip gate dispositions it, with `Fix in this session` recommended because it is a `blocker`.
- Do not invent a fourth gate for it.

## Why PHASE 3 and PHASE 4 are both required

- PHASE 3 catches misjudged depth or an unnoticed mechanism on a path that was surfaced; an ungated pick is an orchestrator judgment no gate reviewed, and PHASE 3 is the only place it gets challenged.
- PHASE 4 catches a plausible path that was not surfaced at all; the pick, the orchestrator's or the user's, was made from an incomplete menu.
