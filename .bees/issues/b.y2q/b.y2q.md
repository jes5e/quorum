---
id: b.y2q
type: bee
title: context_gauge.py produce crashes and blanks the status line when the gauge directory is unwritable
status: open
created_at: '2026-09-02T22:33:59.186280'
schema_version: '0.1'
reference_materials: null
guid: y2qz41uvkh3i6faqvg6zscbhron3bfok
---

## Description

`cmd_produce` calls `write_gauge(record)` (which calls `ensure_gauge_dir()` and opens the gauge file for writing) with no exception handling. Any `OSError` from the filesystem propagates out of `main()`, so the status-line producer exits non-zero with a traceback and never reaches the unconditional display tail.

## Current behavior

Reproduced on 2026-09-02 against the branch tip: with `<tempdir>/.quorum` present but unwritable (mode 0555) and a valid payload on stdin, `produce --wrap-command 'echo WRAPPED-DISPLAY'` exits **1**, prints **nothing** on stdout, and emits a `PermissionError` traceback on stderr. Because the harness blanks the status line on non-zero exit or empty output, the operator's wrapped status line is blanked on every refresh for as long as the condition persists.

## Expected behavior

A gauge write failure is a producer-side failure like an unparseable payload: `produce` records one diagnostic line on stderr via `warn()`, skips the write, and still falls through to the display tail — wrapped command run with the captured bytes, its stdout re-emitted verbatim, exit 0. The module docstring's load-bearing invariant already states this contract ("no input-parse outcome may skip invoking the wrapped command ... `produce` must never return non-zero on the wrap path"); the code must make it true for filesystem failures too. Downstream the gauge stops refreshing, so a consumer's `read` reports `stale`/`missing` — the same operator-visible signal the docs already describe for payload drift.

## Impact

Correctness/UX. The trigger is ordinary on shared machines: `/tmp` is world-writable with the sticky bit, so the first user to create `/tmp/.quorum` owns it (mode 0755) and every other user's producer then crashes on every refresh, permanently blanking their status line — the exact outcome the wrap path exists to prevent. Also hits read-only or full tempdirs.

## Suggested fix

1. In `skills/quo-setup/scripts/context_gauge.py` `cmd_produce`, wrap the `write_gauge(record)` call (which covers `ensure_gauge_dir()`) in `try/except OSError`, `warn()` a single diagnostic naming the path and error, and continue to the display tail. Do not catch in `write_gauge` itself — it is used by the self-check path, which wants the exception.
2. Update the docstring's exit-code section and invariants to state the write-failure case explicitly.
3. Add tests in `tests/test_context_gauge.py`: unwritable gauge dir with `--wrap-command` → exit 0, wrapped stdout emitted byte-exact, one stderr line, no gauge written; same without `--wrap-command` → exit 0, default display emitted. Mirror the existing `test_cli_produce_broken_wrap_command_still_writes_the_gauge` / blanking-shape test structure.

## Background and rationale

Found during a full review of Plan b.55r. The helper's docstring documents the never-blank invariant carefully and the test suite (343 tests) covers serialization failure inside `write_gauge` and every stdin shape, but no test exercises an OS-level write failure reaching `cmd_produce` — the one path that violates the invariant. Payload-parse failures were fixed earlier (Epic 2, Task 1) for exactly this reason; the filesystem-failure path was missed.

## Decisions and rejected alternatives

- Catching inside `write_gauge` was rejected: `_run_self_check` relies on the gauge write being observable, and the installer's atomic settings write has its own error contract.
- Exiting non-zero while still printing the display was rejected for the same reason recorded in the module's decision record: the harness blanks the line on non-zero exit regardless of stdout.
- Pre-checking writability (`os.access`) was rejected as a TOCTOU-shaped duplicate of the write itself; catching the actual `OSError` is simpler and complete.

