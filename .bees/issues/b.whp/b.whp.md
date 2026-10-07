---
id: b.whp
type: bee
title: '/quo-setup gauge step: when a committed project statusLine outranks the user-level one, offer the repo''s git-ignored settings.local.json'
status: open
created_at: '2026-10-07T12:50:33.301986'
schema_version: '0.1'
reference_materials: null
guid: whp8dohcxcm73r63y6mbj1zrh45uakz6
---

## Description

`/quo-setup`'s gauge-producer step detects when a repo's committed `.claude/settings.json` sets its own `statusLine`, which outranks the user-level one. It then offers only three choices: configure at user level (which may be outranked), not now, or opt out. None of them guards the repo the operator is in, so a fix-issue or execute run there gets `missing` from the guard and runs with no context guard at all.

## Evidence (host, 2026-10-07)

The operator prepared a host-side `/quo-fix-issue` run in event_consumer_service, whose committed `.claude/settings.json` sets a purple model/folder status line. The gauge step warned clearly, then offered no choice that worked for that repo. The operator recovered only with the overseer's help, by telling the agent through "Type something" to also write a `statusLine` to the repo's git-ignored `.claude/settings.local.json` that runs the producer wrapping the project's command. The agent did this without any helper change: it used the helper's classifier and self-check, changed nothing else in the file, and kept its 0600 permissions. A fresh session in that repo then published `context-usage-fe0f83b5-….json` (4%, updated live), with the purple display unchanged.

**Three questions:** once so far, but it recurs in any repo that commits a status line; it announces itself; not recovered unaided.

## Expected behavior

When a committed project `statusLine` outranks the user-level one, and the repo git-ignores `.claude/settings.local.json` (which outranks project settings), the step offers to install the producer there too, wrapping the project's command so its display is kept. The committed file is never touched.

## Suggested fix

- One choice in the gauge gate, offered only in that case, and one goal sentence. No new helper subcommand: the agent did the edit correctly from a plain instruction.
- A small reporting fix in `context_gauge.py inspect-statusline`. It lists the repo's settings files as `higher_precedence_sources` but does not say which one is effective in this repo, so the agent had to verify the local entry by hand. Its reader is the gate itself, which needs that answer to know whether a local install took effect.

## Notes for the design

- **The local entry holds a copy of the project's status-line command.** It goes stale if the project changes its command. That affects only the display; say so in the choice's description.
- **A re-run refreshes only the user-level entry.** After a Python upgrade or a moved checkout, the local entry still points at the old paths. Decide whether a re-run refreshes the local entry too, or whether the choice just says so.
- **On macOS, `tempfile.gettempdir()` is `$TMPDIR`** (`/var/folders/…/T`), not `/tmp`, so the gauge files and the opt-out marker live in `$TMPDIR/.quorum/` while skill-written scratch (manifests) goes to the literal `/tmp/.quorum/`. Readers and writers agree within each, so nothing breaks. But README's note that deleting the directory clears the opt-out marker points at the wrong directory on macOS. Check the README wording when this is done.

