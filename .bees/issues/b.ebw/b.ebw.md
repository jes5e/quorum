---
id: b.ebw
type: bee
title: 'Unify the two temp-directory conventions: helpers use tempfile.gettempdir(), skill prose uses literal /tmp/.quorum'
parent: null
reference_materials: null
created_at: '2026-09-03T02:22:21.827998'
status: open
schema_version: '0.1'
guid: ebwzp17xytpiod5u63mnia9y8cqzyff6
---

## Description

The repository uses two different resolutions of "the platform temp directory" for files under `<tempdir>/.quorum/`. Bundled Python helpers resolve it with `tempfile.gettempdir()`, which honors `TMPDIR`; skill prose (the run-state manifests, `--body-file` scratch files, the compromise tracker, and every inline snippet) uses the literal `/tmp/.quorum` on POSIX. On Linux with `TMPDIR` unset these coincide. On macOS — where launchd sets a per-user `TMPDIR` under `/var/folders/.../T/` — they are two different directories, so helper-written artifacts (today: the per-session gauge file) and prose-written artifacts do not share the namespace the scratch-file convention and README describe.

## Current behavior

`skills/quo-setup/scripts/context_gauge.py` writes `context-usage-<session_id>.json` under `tempfile.gettempdir()/.quorum/`; the three orchestrators write `run-state-*.md` and body files under literal `/tmp/.quorum/`. README and CLAUDE.md's scratch-file convention describe `/tmp/.quorum` as *the* POSIX location. The now-superseded opt-out marker was written by the helper and checked by prose, and that mismatch made it silently inert on macOS — Plan b.d8n removes that artifact, and its Epic 2 changes README to state both locations honestly rather than pretending there is one.

## Expected behavior

One convention. Every artifact under the `.quorum` namespace resolves the temp directory the same way on a given platform, so README and the scratch-file convention can name a single location per OS and any future artifact that crosses the helper/prose boundary cannot repeat the opt-out marker's failure.

## Impact

Correctness on macOS for any future cross-boundary artifact; operator confusion when told to look in "the `.quorum` directory" and finding two; a standing exception in the docs (Plan b.d8n's README wording) that should be temporary.

## Suggested fix

Pick one and apply it everywhere:

- **(a) Helpers adopt the prose convention** — on POSIX resolve to literal `/tmp` (keep `tempfile.gettempdir()` on Windows, where both conventions already agree on `%TEMP%`). One small function in `context_gauge.py` (`gauge_dir()` and any future helper), plus README/CLAUDE.md simplification back to a single location. Ignores `TMPDIR` on POSIX, which is acceptable: `/tmp` is universally present and the convention already assumes it.
- **(b) Prose adopts the helper convention** — inline snippets resolve `${TMPDIR:-/tmp}`. Rejected in advance by the repo's bash etiquette (no shell variable expansion in Bash tool calls) and by the volume of snippets involved.
- **(c) A helper subcommand prints the scratch directory** and prose consumes it. Adds a Bash call before every scratch write; heavier than (a) for no gain.

Option (a) is the likely choice; the Analyst should confirm nothing depends on `TMPDIR` being honored (the status-line producer inherits the harness's environment either way).

## Background and rationale

Surfaced by the fresh-eyes plan review of Plan b.d8n (2026-09-03), which noted that describing the gauge path truthfully (via `tempfile.gettempdir()`) makes README's single-namespace framing false in the same edit. Unifying the convention is cross-cutting — it touches the scratch-file convention every skill relies on — so b.d8n documents both locations and defers the unification here rather than expanding its scope.

## Decisions and rejected alternatives

- Deferred out of Plan b.d8n rather than folded in: the plan's purpose is to shrink the guard; changing a repo-wide convention inside it would widen its blast radius.
- Option (b) rejected: violates the single-literal-command bash etiquette and would touch dozens of snippets.

## Deferred from /quo-fix-issue run (2026-09-03 22:25)

Surfaced while fixing Issue b.y2q (commit b2b113e on `fix/b.y2q`), which hardened `skills/quo-setup/scripts/context_gauge.py` so an unwritable, read-only, or full gauge directory no longer blanks the status line.

**Carry the shared-tempdir ownership hazard into the unification decision.** That fix hardens the *helper*, which resolves `<tempdir>` via `tempfile.gettempdir()`. Skill prose still writes the run-state manifests, `--body-file` scratch files, and the compromise tracker to the literal `/tmp/.quorum` with no tolerance path at all, so it retains the full shared-`/tmp` exposure b.y2q's Impact section describes: `/tmp` is world-writable with the sticky bit, the first user to create `/tmp/.quorum` owns it, and every other user's prose-side write then fails (and a non-traversable directory, e.g. created under `umask 077`, makes the reader exit `2` rather than report `missing`). On macOS the two conventions resolve to genuinely different directories (`$TMPDIR` vs `/tmp`), so one can be writable while the other is not. Whichever option this Issue picks should decide the collision-and-permissions behavior for the prose side explicitly — e.g. what a skill does when `mkdir -p /tmp/.quorum` succeeds but the directory is owned by another user — rather than inheriting it silently. Option (a) as written moves the helper *onto* the exposed path, so this consideration bears on the choice, not just on its follow-through.

