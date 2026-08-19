#!/usr/bin/env python3
"""Publish and read a per-session context-window usage gauge.

Claude Code hands its status-line command a JSON payload describing the current
session, including how much of the model's context window is in use. That
payload is delivered only to the status-line process, so nothing else in a
session can see it. This helper bridges the gap: a `produce` run (wired as the
status-line command) captures the reading and publishes it to a well-known
file, and a `read` run (invoked by a skill that wants to know how much headroom
is left) reads that file back.

The two halves never talk to each other directly — they meet only at the gauge
file path and field names below, which are therefore a contract rather than an
implementation detail.

CLI contract
------------
Two modes, selected by an argparse subcommand.

**Producer mode:**

    context_gauge.py produce [--wrap-command <cmd>]

Reads the status-line JSON payload from stdin exactly once, extracts the
session identifier and the context-window object, and publishes them to the
gauge file. Prints a status-line display string on stdout.

- `--wrap-command <cmd>` (OPTIONAL, single string): an existing status-line
  command to preserve. When given, `<cmd>` is invoked on EVERY refresh with
  exactly the bytes that arrived on stdin — valid payloads, empty stdin, and
  bytes that did not parse alike — and its stdout is re-emitted verbatim as the
  display, so an operator's current status line is wrapped rather than replaced.
  This transparency has an honest limit: `produce` cannot guarantee a non-blank
  display, because the wrapped command may itself print nothing for a given
  input. What it guarantees is narrower — `produce` never causes the blank of
  its own accord. When omitted, a minimal default display line is printed; note
  that this always-emit guarantee is about the wrap path, so without
  `--wrap-command` an empty or unparseable payload yields an empty default
  display (there is no payload to derive one from) and the harness blanks the
  line on empty output. That empty display is `produce`'s own and is
  legitimately empty.

**Reader mode:**

    context_gauge.py read --session-id <id>

Prints exactly one value on stdout describing the current reading for that
session.

- `--session-id <id>` (REQUIRED): the session identifier to read. It selects
  the gauge file, so it must match the identifier the producer wrote under.

Gauge file
----------
    <tempdir>/.quorum/context-usage-<session_id>.json

`<tempdir>` is the platform temporary directory (`tempfile.gettempdir()`), so
this resolves correctly on POSIX and on Windows without per-OS branching. The
directory is created if absent. The filename is keyed by session identifier so
concurrent sessions in one environment never collide.

The written JSON shape is:

    {"session_id": <str>, "context_window": {...}}

where `context_window` is the object from the status-line payload, carried
through as-is. The reader looks for a `used_percentage` field inside it.

Reader output values
--------------------
`read` prints exactly one of four values:

- an integer percentage — a fresh reading of how much of the window is in use.
- `no-reading` — the file exists and is fresh, but the percentage is null or
  absent. This is a transient state (early in a session, or just after the
  context was compacted): the producer IS running, the number just is not
  populated yet.
- `stale` — the file exists but was last written longer ago than the freshness
  window. The producer appears to have stopped updating.
- `missing` — no gauge file exists for this session. Usually means no producer
  is configured in this environment.

Fail-safe rules a consumer MUST honor
-------------------------------------
- NEVER treat an absent, null, or stale reading as `0`, and never treat it as
  evidence of available headroom. Those values mean "no trustworthy reading",
  not "plenty of room".
- `stale` and `no-reading` are DISTINCT and must not be collapsed into one
  another. A fresh-but-null reading means the gauge is live and simply has no
  number yet; a stale reading means the gauge itself is not being updated, and
  because usage only grows within a session, a stale number biases low.

Exit codes
----------
The split is per subcommand.

- `produce` returns `0` on every input shape — valid, empty, and unparseable
  stdin all exit `0`. Its only non-zero exit is an argparse usage error, which
  is raised before `cmd_produce` runs. An unparseable stdin payload writes one
  diagnostic line to stderr and still exits `0`.
- `read` returns `0` for every normal reading value, including `missing`,
  `stale`, and `no-reading` — these are ordinary conditions, not errors, and a
  consumer must be able to distinguish them from a crash. It returns `2` only on
  a malformed gauge file (unreadable or non-conforming), reported as a single
  human-readable line on stderr, with an invalid `--session-id` or an argparse
  usage error also exiting `2`.

Invariants (load-bearing)
-------------------------
- NEVER write anywhere outside the gauge directory.
- NEVER delete any file — not the gauge file, not the directory, not anything
  else. This helper has no cleanup path by design.
- Writes are overwrite-per-refresh: truncate-and-write, NEVER append. The gauge
  is a live reading, not a log, and the overwrite is what keeps its modification
  time current for the freshness check.
- The gauge path and the JSON field names are a protected cross-skill contract.
  They are shared with the installer that wires up the producer, with the
  consumers that read the gauge, and with any environment owner who publishes
  the gauge themselves instead of using this helper. Changing either breaks
  every one of those parties silently — a reader that finds nothing reports
  `missing`, which looks like an unconfigured environment rather than a bug.
- Display transparency under `--wrap-command`: no input-parse outcome may skip
  invoking the wrapped command or skip emitting its stdout, and `produce` must
  never return non-zero on the wrap path. The reason is load-bearing, not a
  style choice: the harness blanks the status line when a status-line command
  exits non-zero OR produces no output (Claude Code status-line documentation,
  Troubleshooting > "Script errors or hangs",
  https://code.claude.com/docs/en/statusline). A non-zero exit or a skipped
  display on the wrap path would therefore blank the operator's status line —
  the exact outcome the wrap path exists to prevent — so a future edit that
  reintroduces an early non-zero return would silently undo this guarantee.

Decision record
---------------
Two stdin shapes used to blank a wrapped display: empty stdin (a refresh that
carried no payload) and stdin that did not parse as a JSON object. Both now take
the wrap path and exit `0`. The alternative of emitting the display while still
exiting non-zero was rejected: per the harness behavior cited in the invariant
above, the status line is blanked on a non-zero exit code regardless of what was
printed, so a non-zero exit cannot coexist with a preserved display. The
malformation signal is not discarded — an unparseable payload still writes one
line to stderr — it is simply carried there rather than in the exit code.
Detecting a producer that has genuinely stopped or whose payload has drifted
therefore rests on `read`'s `missing`/`stale` routing rather than on any signal
`produce` emits: on a mid-session payload drift the gauge file already exists, so
the surviving classification is `stale`, not `missing`. That is a dependency on
the reader's routing, not an unconditional guarantee from `produce`.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional  # `Optional[...]` only; no PEP 604 unions — see below.


# Stop point, as a percentage of the context window, for a consumer deciding
# whether to begin another unit of work. Arithmetic behind the value: the
# harness begins auto-compacting near ~83% of the window, and a single large
# unit of work can consume roughly 25-30% of it. That 25-30% figure is an
# unverified working estimate, NOT a measured or enforced budget — nothing in
# the workflow measures per-unit consumption. Stopping at 50 keeps 50 + ~30
# under ~83; raising the stop point to 55 fails that same arithmetic
# (55 + 30 = 85 > 83), which is why 50 is the highest safe value. This is the
# single definition site of the tunable: consumers read it here rather than
# re-deriving it.
STOP_THRESHOLD_PERCENT = 50

# How recently the gauge must have been written for its reading to be trusted.
# Freshness is judged from the gauge file's modification time — there is no
# embedded timestamp field — and the overwrite-per-refresh write semantics are
# what keep that mtime current. A gauge older than this window signals a
# stalled producer, not a healthy low reading.
FRESHNESS_WINDOW_SECONDS = 120

# The gauge file contract, defined once so no other code path spells it out.
GAUGE_DIR_NAME = ".quorum"
GAUGE_FILENAME_TEMPLATE = "context-usage-{session_id}.json"

# Conservative charset guard for a session identifier. Because the identifier
# is interpolated into a filename, anything outside this set — a path
# separator, a `..` segment, an empty string — could escape the gauge
# directory, so it is rejected rather than sanitized.
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")

# How long a wrapped status-line command is allowed to run before it is
# abandoned. The producer runs on every status-line refresh, so an operator
# command that hangs would otherwise hang the status line indefinitely, once
# per refresh. On timeout the producer keeps whatever output it captured and
# still succeeds — the gauge has already been written by then.
WRAPPED_COMMAND_TIMEOUT_SECONDS = 10

# The three non-numeric values `read` can print, defined once each because
# consumers branch on them as exact strings. `READING_STALE` and
# `READING_NO_READING` are deliberately distinct and MUST NOT be collapsed:
# since usage only grows within a session, a stale number biases low — i.e.
# toward the banned "looks like there is headroom" direction.
READING_NO_READING = "no-reading"
READING_STALE = "stale"
READING_MISSING = "missing"


class MalformedGauge(Exception):
    """A gauge file exists and is fresh but does not conform to the contract.

    Raised by `classify_reading`, which stays pure — it neither prints nor
    exits, so it can be unit-tested in-process. The CLI layer is what turns
    this into a single stderr line and exit code 2.

    This is NOT one of the four normal reading states: `missing`, `stale`, and
    `no-reading` are ordinary conditions that exit 0.
    """


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def warn(message: str) -> None:
    print(message, file=sys.stderr)


def gauge_dir() -> Path:
    """Return the gauge directory path. Pure — creates nothing.

    The temporary directory is resolved at call time, not captured at import
    time, so a caller that redirects it sees the redirection take effect.
    """
    return Path(tempfile.gettempdir()) / GAUGE_DIR_NAME


def ensure_gauge_dir() -> Path:
    """Return the gauge directory, creating it if absent. Never deletes."""
    path = gauge_dir()
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_valid_session_id(session_id) -> bool:
    """True iff `session_id` is a non-empty str safe to place in a filename."""
    return isinstance(session_id, str) and bool(SESSION_ID_RE.fullmatch(session_id))


def gauge_path(session_id: str) -> Path:
    """Return the gauge file path for `session_id`.

    The caller is responsible for validating the identifier with
    `is_valid_session_id` first; this function does no checking of its own.
    """
    return gauge_dir() / GAUGE_FILENAME_TEMPLATE.format(session_id=session_id)


def read_stdin_once() -> bytes:
    """Drain stdin exactly once and return the raw bytes.

    This is the ONLY place in this file that reads stdin, and it must stay
    that way. Stdin is a pipe: it can be drained once, so the bytes are
    captured here and reused by every consumer (the JSON parse and the wrapped
    command's own stdin). A second read would come back empty and silently
    blank out a wrapped operator status line.

    Returns `b""` when there is no readable stdin at all.
    """
    stream = getattr(sys.stdin, "buffer", None)
    if stream is None:
        return b""
    try:
        return stream.read()
    except (OSError, ValueError):
        return b""


def parse_payload(raw: bytes):
    """Decode and parse the captured status-line payload.

    Returns the payload dict, or `None` when stdin was empty or whitespace
    only — a refresh that carried no payload, which is a no-op rather than a
    failure. Raises `ValueError` when the input is non-empty but is not JSON,
    or parses to something other than an object, so the caller can route it to
    `fail()`.
    """
    text = raw.decode("utf-8", errors="replace")
    if not text.strip():
        return None
    payload = json.loads(text)  # json.JSONDecodeError subclasses ValueError
    if not isinstance(payload, dict):
        raise ValueError("top-level JSON value is not an object")
    return payload


def extract_gauge_record(payload: dict):
    """Build the gauge record to publish, or `None` when there is nothing to.

    `None` means no usable session identity in this payload (absent, empty,
    non-`str`, or outside the filename-safe charset). That is the no-op
    signal: the caller writes nothing and still exits 0.

    An absent or non-object `context_window` is carried through as an empty
    object rather than being filled in. The reader classifies that as
    "no reading", which is the whole point — a fabricated number, or a `0`,
    would read as abundant headroom.
    """
    session_id = payload.get("session_id")
    if not is_valid_session_id(session_id):
        return None
    context_window = payload.get("context_window")
    if not isinstance(context_window, dict):
        context_window = {}
    return {"session_id": session_id, "context_window": context_window}


def write_gauge(record: dict) -> Path:
    """Publish `record` to this session's gauge file and return its path.

    Writes only ever land under `gauge_dir()`, keyed by session identifier so
    concurrent sessions cannot collide.
    """
    ensure_gauge_dir()
    path = gauge_path(record["session_id"])
    # Serialize before opening the file: a serialization failure must not
    # truncate a gauge that already holds a good reading.
    serialized = json.dumps(record)
    # Explicit "w", never "a" — overwrite-per-refresh. The gauge is a live
    # reading, not a log, and the truncating rewrite is also what keeps the
    # file's modification time current for the reader's freshness check.
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(serialized)
    return path


def default_display(payload) -> str:
    """Return the minimal display used when no command is being wrapped.

    Just the working directory's basename — nothing decorative, and
    deliberately NOT the usage percentage. The status line belongs to the
    operator; this helper is a gauge publisher that happens to occupy that
    slot, not a place to advertise its own reading.
    """
    if not isinstance(payload, dict):
        return ""
    workspace = payload.get("workspace")
    if isinstance(workspace, dict):
        current_dir = workspace.get("current_dir")
        if isinstance(current_dir, str) and current_dir:
            return os.path.basename(current_dir)
    cwd = payload.get("cwd")
    if isinstance(cwd, str) and cwd:
        return os.path.basename(cwd)
    return ""


def run_wrapped(command: str, stdin_bytes: bytes) -> str:
    """Run the operator's own status-line command and return its stdout.

    `stdin_bytes` is the already-captured payload, replayed onto the wrapped
    command's stdin so it sees exactly what it would have seen had it been
    invoked directly by the harness.

    `shell=True` is deliberate: the wrapped value is a settings-file
    `statusLine` command *string*, which the harness itself runs through the
    platform shell (`/bin/sh` on POSIX, `cmd.exe` on Windows). Running it any
    other way would break commands with pipes, quoting, or redirection that
    work fine today. It is operator-authored configuration, not untrusted
    input.

    Failures never propagate. A command that cannot spawn, exits non-zero, or
    outruns the timeout yields whatever stdout was captured (possibly empty)
    and the producer still succeeds: the gauge write has already happened, and
    a blank status line beats a broken one. Note the direction of that blank:
    `produce` never blanks the display of its own accord, but a blank that
    originates in the wrapped command's own failure or silence is passed
    through here as-is rather than papered over.

    This is the one extra short-lived, time-bounded process spawn per
    status-line refresh, accepted as a small bounded cost.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            input=stdin_bytes,
            capture_output=True,
            timeout=WRAPPED_COMMAND_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as expired:
        partial = expired.stdout or b""
        return partial.decode("utf-8", errors="replace")
    except OSError:
        return ""
    return result.stdout.decode("utf-8", errors="replace")


def emit_display(display: str) -> None:
    """Print the status-line display.

    `sys.stdout.write` rather than `print` so wrapped output is reproduced
    byte for byte — a trailing newline is neither added nor stripped, and an
    empty display prints nothing at all rather than a bare newline.
    """
    sys.stdout.write(display)


def cmd_produce(args) -> int:
    # Capture stdin once, up front; `captured` is the single source for both
    # the parse below and the wrapped command's stdin further down.
    captured = read_stdin_once()

    try:
        payload = parse_payload(captured)
    except ValueError as error:
        # An unparseable payload is not fatal: record the diagnostic and
        # normalize to None so this refresh joins the empty-stdin path rather
        # than short-circuiting. The display tail below still runs — the
        # operator's status line does not get to go blank just because this
        # refresh's stdin was garbage.
        warn(f"unreadable status-line payload on stdin: {error}")
        payload = None

    if payload is not None:
        record = extract_gauge_record(payload)
        if record is not None:
            # Ordering is load-bearing: publish the gauge BEFORE running the
            # wrapped command, so a slow or failing wrapped command cannot cost
            # this refresh its reading.
            write_gauge(record)
        # A payload with no usable session identity writes nothing, but the
        # display still has to be emitted — the operator's status line does not
        # get to go blank just because this refresh had no session context.

    # Single exit, unconditional display tail: every path above converges here,
    # so the display is emitted exactly once no matter what stdin carried. This
    # generalizes the no-usable-session-id principle just above — a refresh
    # never blanks the operator's status line on account of missing or garbled
    # input, and the function never returns non-zero on the wrap path. On the
    # wrap path the captured bytes are replayed as-is; any blank that results is
    # the wrapped command's own, never this function's doing.
    if args.wrap_command:
        emit_display(run_wrapped(args.wrap_command, captured))
    else:
        emit_display(default_display(payload))
    return 0


def classify_reading(
    path: Path,
    now: Optional[float] = None,
    freshness_seconds: int = FRESHNESS_WINDOW_SECONDS,
) -> str:
    """Classify the gauge at `path` into exactly one of the four reading values.

    Returns a decimal integer string (a genuine measured percentage), or one of
    `READING_NO_READING`, `READING_STALE`, `READING_MISSING`. Raises
    `MalformedGauge` when the file is fresh but non-conforming.

    Pure by design: no printing, no `sys.exit`, no writes, and no directory
    creation. `now` (float epoch seconds, defaulting to the current time) and
    `freshness_seconds` are injectable so tests can age a gauge without
    sleeping.

    `Optional[float]` rather than a PEP 604 union is deliberate, and the whole
    file must stay free of that syntax. This helper is unique among the bundled
    scripts in being run by the harness's status line under whatever `python3`
    resolves on the operator's PATH — a system 3.9 is realistic there — and a
    PEP 604 union raises at definition time on 3.9, which would break the
    annotated function at import. The repo's general 3.10+ toolchain floor does
    not govern this file.

    NEVER returns `"0"` for an absent, null, or stale reading. The only path to
    a `0` output is a measured `used_percentage` that rounds to zero.
    """
    if now is None:
        now = time.time()

    # The evaluation order below is LOAD-BEARING; do not reorder the steps.

    # (a) Missing beats everything: no file means no producer is configured
    # here. Caught from `stat` rather than pre-checked with `exists()` so the
    # existence test and the mtime read are the same syscall (no TOCTOU gap).
    try:
        mtime = path.stat().st_mtime
    except FileNotFoundError:
        return READING_MISSING
    except OSError as error:
        # Present but un-stat-able (permissions, a non-directory component in
        # the path): not a normal state, so it is malformation, not `missing`.
        raise MalformedGauge(f"cannot stat gauge file: {error}") from error

    # (b) Staleness is checked BEFORE parsing, on purpose: a stalled producer's
    # last write is untrustworthy no matter what it contains. A consequence
    # worth stating outright — a file that is BOTH aged and malformed
    # classifies as `stale` (exit 0, stop) rather than exiting 2. Either
    # outcome is fail-safe, so the cheaper, more informative one wins.
    if now - mtime > freshness_seconds:
        return READING_STALE

    # (c) Fresh: now the contents have to hold up.
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        # Raced away between the stat and this read. Still just `missing`.
        return READING_MISSING
    except OSError as error:
        raise MalformedGauge(f"gauge file is unreadable: {error}") from error
    except UnicodeDecodeError as error:
        raise MalformedGauge(f"gauge file is not valid UTF-8: {error}") from error

    try:
        payload = json.loads(text)  # json.JSONDecodeError subclasses ValueError
    except ValueError as error:
        raise MalformedGauge(f"gauge file is not valid JSON: {error}") from error
    if not isinstance(payload, dict):
        raise MalformedGauge("top-level JSON value is not an object")

    if "context_window" in payload:
        context_window = payload["context_window"]
        if not isinstance(context_window, dict):
            # Present but not an object (including an explicit `null`): the
            # producer never writes that shape, so the file is non-conforming.
            raise MalformedGauge('"context_window" is present but is not an object')
    else:
        # Absent entirely — treated as empty, which falls through to
        # `no-reading` below rather than being called malformed.
        context_window = {}

    # (d) Fresh file, live producer, no number yet: early in a session or right
    # after a compaction. Transient, and explicitly NOT `0`.
    value = context_window.get("used_percentage")
    if value is None:
        return READING_NO_READING

    # (e) `bool` is an `int` subclass, so it MUST be rejected before the
    # numeric check — otherwise `true` would silently read as `1`.
    if isinstance(value, bool):
        raise MalformedGauge('"used_percentage" is a boolean, not a number')
    if isinstance(value, (int, float)):
        try:
            # Deliberately NOT clamped to 0-100: report what was measured, so a
            # nonsensical reading stays visible instead of being massaged into
            # a plausible one.
            rounded = int(round(value))
        except (ValueError, OverflowError) as error:
            # NaN / Infinity — JSON allows them, this contract does not.
            raise MalformedGauge('"used_percentage" is not a finite number') from error
        return str(rounded)
    raise MalformedGauge(
        f'"used_percentage" is not a number (got {type(value).__name__})'
    )


def cmd_read(args) -> int:
    # An identifier that fails the charset guard is a caller bug, not a state
    # of the gauge. It must NOT be mapped onto one of the four reading values —
    # a consumer would read `missing` as "no producer here" and carry on.
    if not is_valid_session_id(args.session_id):
        return fail(
            f"invalid --session-id {args.session_id!r}: expected a non-empty "
            "string of letters, digits, '.', '_', or '-'"
        )

    # `gauge_path`, never `ensure_gauge_dir`: reading is strictly read-only and
    # must not bring the gauge directory into existence as a side effect.
    path = gauge_path(args.session_id)
    try:
        reading = classify_reading(path)
    except MalformedGauge as error:
        return fail(f"malformed gauge file {path}: {error}")

    print(reading)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Publish or read a per-session context-window usage gauge.",
        add_help=True,
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    produce = subparsers.add_parser(
        "produce",
        help="read the status-line payload from stdin and publish the gauge file",
    )
    produce.add_argument(
        "--wrap-command",
        dest="wrap_command",
        help="existing status-line command to wrap; its stdout becomes the display",
    )

    read = subparsers.add_parser(
        "read",
        help="print the current reading for a session (percentage, no-reading, stale, or missing)",
    )
    read.add_argument(
        "--session-id",
        dest="session_id",
        required=True,
        help="session identifier selecting the gauge file to read",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.mode == "produce":
        return cmd_produce(args)
    return cmd_read(args)


if __name__ == "__main__":
    sys.exit(main())
