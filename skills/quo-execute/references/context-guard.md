# Context-window boundary guard reference — what the guard reads, why it stops, and the gauge contract

This file is read on demand by `/quo-execute` and `/quo-fix-issue`. The guard's steps, its branch table, and its stop live in the invoking skill's body; this file carries the reasoning and the gauge-file contract an operator needs to configure a producer.

## What the guard is, and is not

- The guard reads an external gauge file that a separate status-line producer process computed and wrote to disk.
- It does not measure the orchestrator's own token usage, and it is not self-introspection. The orchestrator must never invent or estimate its own remaining context, report a self-measured percentage, or gate a branch on such a self-estimate.
- Neither the read nor a boundary stop reclaims any context. The orchestrator has no model-invocable lever to clear or compact its own context; the harness owns compaction, and the only reclamation lever is a fresh session.
- The guard's job is narrow: stop the run at a clean unit boundary, where every load-bearing fact is already on disk, before the harness would auto-compact partway through the next unit.

## Why it runs only on the continuing in-session path

- On a run that ends in this session a fresh-session recommendation is noise, and an interruption would land immediately before the final review.
- A single-unit run crosses no boundary and never reaches the guard.
- The boundary checkpoint is unconditional on every exit path; the guard deliberately is not, and must not inherit that unconditionality.

## Why the reading is obtained the way it is

- The threshold lives in the helper's `stop-threshold` seam, which is the single definition site of the number; the skill bodies never restate it.
- The session id is read first and evaluated before anything else happens, mirroring the session-effort check, so that no gate is opened before the reading is in hand.
- The session id must be trimmed of trailing whitespace or a newline, because a trailing newline fails the helper's `--session-id` charset validation.
- An unset session id is the one silent-skip path, the unsupported-CLI carve-out; it matches how an unset `CLAUDE_EFFORT` is treated.

## Why an over-threshold reading stops unconditionally

- Usage only grows within a session, so a reading at or above the threshold is always a genuine stop.
- The guard offers no proceed option there: a human override at that point is exactly the risk the guard exists to remove, and the run is at a clean boundary where a fresh session costs nothing.

## Why `stale` and errors stop

- Usage only grows within a session, so a stale reading biases low and must not be trusted as headroom.
- `read` exits non-zero on a malformed gauge OR an invalid `--session-id`; do not assume a non-zero exit implies a corrupt file. Either way the reading is untrustworthy and the fail-safe is to stop.
- Recurring staleness across fresh sessions means the operator should check their status-line producer.

## Why `missing` continues silently

- `missing` means no producer is configured for this environment; the environment may override the operator's user-level status-line settings, so no reading is being published.
- A run with no producer records `no reading` in the manifest and continues; it does not stop, and it does not ask. Gating on an absent reading interrupted every unit boundary of every unguarded run for a question whose answer never changed within a run.
- The persistent opt-out marker at `<tempdir>/.quorum/context-guard-opt-out` records the same standing choice for an operator who never wants a producer; its presence changes nothing about the `missing` branch, which continues either way.
- An operator who wants the guard configures a producer with `/quo-setup --configure-gauge-producer`; a freshly-configured producer begins publishing only in the next session.

## The gauge file contract

- Path: `<tempdir>/.quorum/context-usage-<session_id>.json`, with `<tempdir>` the platform temporary directory.
- Required fields: `session_id`, and a `context_window` object carrying `used_percentage`.
- Semantics: overwritten on every status-line refresh; a fresh file with a null or absent percentage reads as `no-reading`.
- The helper's `read --session-id <trimmed-session-id>` subcommand prints exactly one of an integer percentage, `no-reading`, `stale`, or `missing`, and exits `0` for all four.
- The helper's `write-opt-out` subcommand writes the opt-out marker; there is no removal subcommand, and deleting `<tempdir>/.quorum/` clears it.
