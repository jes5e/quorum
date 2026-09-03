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

**Threshold mode:**

    context_gauge.py stop-threshold

Prints the integer stop threshold percentage on stdout and exits `0`. Takes no
arguments. Read-only: it reads nothing from stdin, writes no file, creates no
directory, and emits nothing on stderr. It exists so a consumer (a boundary
guard comparing a reading against the stop point) can obtain the threshold from
the single-definition-site constant `STOP_THRESHOLD_PERCENT` rather than
restating the number and creating a second definition site. This subcommand is
purely additive: it does NOT touch `read`'s four-value output vocabulary
(`integer` / `no-reading` / `stale` / `missing`) or the gauge-file
path/field-name contract.

**Inspection mode:**

    context_gauge.py inspect-statusline [--repo-root <path>]

Reports the current user-level status-line configuration as a single compact
JSON object on stdout and exits `0`. Read-only: it writes nothing and creates no
file or directory. `--repo-root` (OPTIONAL, default: current working directory)
is the repository whose project/local settings are checked for a
higher-precedence status line.

The emitted object carries these keys:

- `settings_path` — the resolved user settings file path.
- `settings_exists` — whether that file is present.
- `status_line_present` — whether an EFFECTIVE status-line command is
  configured. This is true ONLY when `statusLine` is an object carrying a
  non-empty string `command`. It is false for a missing `statusLine` key, a
  `statusLine` that is not an object, and a `statusLine` object whose `command`
  is missing, empty, or not a string — every such degenerate shape reports
  `status_line_present` false and `producer_state` `"absent"`.
- `status_line_command` — the existing command string, or `null` when none.
- `status_line_extra_keys` — every key of the existing `statusLine` object other
  than `type` and `command` (e.g. `padding`, `refreshInterval`,
  `hideVimModeIndicator`), so an installer can preserve them; `{}` when none.
- `producer_state` — one of five values: `"direct"` (this helper's `produce`,
  no wrapped command), `"wrapped"` (this helper's `produce` wrapping an operator
  command), `"other-install"` (a different `context_gauge.py` running
  `produce`), `"foreign"` (an unrelated status line, carried opaquely), or
  `"absent"` (no effective status-line command, per `status_line_present`).
- `wrapped_command` — the wrapped operator command extracted from a `wrapped`
  or `other-install` state, else `null`.
- `producer_current` — true only when `producer_state` is `direct` or `wrapped`
  AND the existing command is byte-identical to the command that would be
  composed now (this interpreter, this script path, the extracted wrap payload,
  the detected status-line shell); false in every other state. An interpreter or
  script-path change flips it false even while the state stays `direct`/
  `wrapped`, which is how a caller knows a refresh is needed.
- `script_path` — this helper's own resolved path.
- `python_executable` — the interpreter running this helper.
- `opt_out_marker_path`, `opt_out_marker_present` — the opt-out marker path (see
  below) and whether it exists.
- `higher_precedence_sources` — see "Higher-precedence settings" below.
- `status_line_shell` — the shell the harness runs the status-line command
  through: `"sh"` on POSIX, `"git-bash"` or `"powershell"` on Windows.

Exit codes: `inspect-statusline` exits `0` on every reportable configuration,
INCLUDING an absent settings file. It exits `2`, with a single stderr line
naming the path and nothing on stdout, in exactly one case — the settings file
exists but does not parse as a JSON object. That state is never reported as
`absent`, because a caller that writes settings keys off `absent` and would
otherwise clobber a file it could not read.

**Installer mode:**

    context_gauge.py install-statusline [--repo-root <path>] [--python <path>] [--no-self-check]

Writes or updates the user-level settings `statusLine` so it runs this helper's
`produce` on every refresh, then reports what it did as one compact JSON object
on stdout and exits `0`. `--repo-root` (OPTIONAL, default: current working
directory) is used only to report `higher_precedence_sources`. `--python`
(OPTIONAL) overrides the interpreter embedded in the composed command; the
default is `sys.executable`. `--no-self-check` (OPTIONAL) skips the post-write
self-check.

Wrap-don't-replace: an existing status line is preserved, never discarded, and a
re-run never nests one wrapper inside another. The wrap payload is chosen from
the inspected `producer_state`: `foreign` wraps the entire existing command
string opaquely; `wrapped` and `other-install` reuse the payload already
extracted from the existing wrapper (the anti-double-wrap rule — the payload is
reused, never re-wrapped); `direct` and `absent` wrap nothing.

`action` is one of four values, mapped explicitly from `producer_state`:

- `absent` → `"installed"` (no status line was configured).
- `foreign` → `"wrapped"` (an unrelated status line is now wrapped).
- `other-install` → `"repointed"` (a different `context_gauge.py` producer was
  replaced with this one, its wrap payload carried across).
- `direct` or `wrapped` whose recomposed command is NOT byte-identical to the
  existing one → `"repointed"` (same producer, moved interpreter or script path).
- `direct` or `wrapped` whose recomposed command IS byte-identical →
  `"already-configured"`; in this case NO write happens and the settings file's
  modification time is left untouched.

Never-clobber rule: if the settings file exists but does not parse as a JSON
object, `install-statusline` exits `2` with a single stderr line and writes
NOTHING — a file that cannot be read is never overwritten.

The rewrite preserves state: unrelated top-level settings keys are left
untouched, and the existing `statusLine` object's other keys (`padding`,
`refreshInterval`, `hideVimModeIndicator`, ...) are merged through, so only
`type` and `command` change. The write is atomic (`tempfile.mkstemp` in the
settings directory, `json.dump`, `os.replace`, temp file unlinked on any error);
there is no backup file — atomic replace plus key preservation plus the summary's
`previous_command` echo is the entire recovery story, and writing an undeletable
backup into the operator's config directory is not.

Self-check (skipped under `--no-self-check`): after the write, the composed
command is run once through the platform shell with a synthetic payload keyed by
the reserved self-check session id, and the summary's `self_check.verified` is
`true` when that run wrote a fresh gauge for the reserved id, `false` with a
non-empty `detail` when it did not. A failed self-check is ADVISORY only: it
never fails the install, because the settings write has already happened and
reverting it would be worse than reporting the failure — the exit code stays `0`.
When `--no-self-check` is given, no subprocess is spawned and `self_check` is
exactly `{"verified": null, "detail": "skipped: --no-self-check"}`.

The summary object carries: `action`, `settings_path`, `previous_command` (the
command the operator had before, or `null` — the only record of it, so a manual
restore is possible), `new_command`, `preserved_status_line_keys`, `self_check`,
`higher_precedence_sources`, and `status_line_shell`.

**Opt-out mode:**

    context_gauge.py write-opt-out

Writes the persistent opt-out marker (creating the gauge directory if absent),
prints its path, and exits `0`. Idempotent: a repeated run rewrites the same
content and reports the same path. The marker suppresses only the boundary
guard's missing-reading hard-stop — never a genuine over-threshold stop — and
deleting the file re-enables the guard. There is NO removal subcommand by
design: this helper never deletes anything, so opting back in is a manual file
delete, not a command.

Gauge file
----------
    <tempdir>/.quorum/context-usage-<session_id>.json

`<tempdir>` is the platform temporary directory (`tempfile.gettempdir()`), so
this resolves correctly on POSIX and on Windows without per-OS branching. The
directory is created if absent. The filename is keyed by session identifier so
concurrent sessions in one environment never collide.

Opt-out marker
--------------
    <tempdir>/.quorum/context-guard-opt-out

A persistent marker an operator writes to run unguarded. Its mere EXISTENCE is
the signal — the contents are advisory only and are never parsed. The name and
location are a cross-skill contract, so both the writer and the boundary guard
that reads it name the same file. What the marker suppresses is narrow: only the
missing-reading hard-stop (the stop that fires when no trustworthy reading is
available). It does NOT suppress a genuine over-threshold stop — an operator who
opts out of the missing-reading guard still stops when a real reading crosses the
threshold. `inspect-statusline` reports the path and whether it exists; it never
creates it.

Higher-precedence settings
--------------------------
`inspect-statusline`'s `higher_precedence_sources` lists settings sources that
outrank the user-level status line this helper configures, so a caller can warn
that a user-level write may be overridden. Settings precedence is, highest
first: managed settings, then command-line launch arguments, then local
(`.claude/settings.local.json`), then project (`.claude/settings.json`), then
user settings (lowest).

DETECTABLE (reported when present, each as a `{"scope", "path", "reason"}`
entry): a project- or local-scope `statusLine` in the repo's `.claude/`
directory; and, in the per-OS file-based managed-settings file and its
`managed-settings.d/` drop-in directory, a `statusLine` key, an
`allowManagedHooksOnly` truthy flag, or a `disableAllHooks` truthy flag (the
last two narrow the status line to managed settings only, disabling a
user-level value). Any such file that is absent, unreadable, or unparseable is
skipped silently.

NOT DETECTABLE (a caller cannot learn these from this helper): a status line
passed via the `--settings` launch flag or other command-line arguments;
server- or enterprise-managed settings delivered out-of-band; and MDM-delivered
policy that does not land in the file-based managed-settings location (a macOS
configuration profile / plist, a Windows registry policy).

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
- `missing` — no gauge file exists for this session, and the gauge directory is
  absent or traversable. Usually means no producer is configured in this
  environment. A gauge directory that cannot be traversed, or that is not a
  directory at all, is reported as a malformed gauge instead — see `Exit codes`.

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

- `produce` returns `0` on every input shape AND on a failed gauge write —
  valid, empty, and unparseable stdin all exit `0`, and so does a refresh whose
  gauge write raised `OSError` (an unwritable, read-only, or full gauge
  directory). Its only non-zero exit is an argparse usage error, which is raised
  before `cmd_produce` runs. Every one of those shapes still emits the display
  and still exits `0`; the two that are genuine failures — unparseable stdin and
  a failed gauge write — each also write one diagnostic line to stderr.
- `read` returns `0` for every normal reading value, including `missing`,
  `stale`, and `no-reading` — these are ordinary conditions, not errors, and a
  consumer must be able to distinguish them from a crash. It returns `2` only on
  a malformed gauge file (unreadable or non-conforming), or on a gauge directory
  that cannot be traversed or is not a directory at all — the latter reachable
  with no gauge file present, since the `stat` fails before absence can be
  established. Either is reported as a single human-readable line on stderr,
  with an invalid `--session-id` or an argparse usage error also exiting `2`.
- `stop-threshold` returns `0`; its only non-zero exit is an argparse usage
  error, which is raised before `cmd_stop_threshold` runs.

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
- Display transparency under `--wrap-command`: no producer-side failure —
  neither an input-parse outcome nor a failed gauge write — may skip invoking
  the wrapped command or skip emitting its stdout, and `produce` must never
  return non-zero on the wrap path. The scope is deliberately every
  producer-side failure and not just the input ones: an earlier input-only
  phrasing of this invariant is what let an unwritable gauge directory blank the
  display. The reason is load-bearing, not a style choice: the harness blanks
  the status line when a status-line command exits non-zero OR produces no
  output (Claude Code status-line documentation, Troubleshooting > "Script
  errors or hangs", https://code.claude.com/docs/en/statusline). A non-zero exit
  or a skipped display on the wrap path would therefore blank the operator's
  status line — the exact outcome the wrap path exists to prevent — so a future
  edit that reintroduces an early non-zero return, or that lets a new
  producer-side failure escape `cmd_produce`, would silently undo this
  guarantee.

Decision record
---------------
Two stdin shapes and one filesystem failure used to blank a wrapped display:
empty stdin (a refresh that carried no payload, a no-op rather than a failure),
stdin that did not parse as a JSON object, and a gauge write that raised
`OSError` (the gauge directory unwritable, read-only, or full — ordinary on a
shared machine, where the first user to create the directory under a
world-writable temporary directory owns it and every other user's producer then
fails on every refresh). All three now take the wrap path and exit `0`. The
write failure is caught at its call site in `cmd_produce` rather than inside
`write_gauge`, because the never-blank guarantee is a property of the process's
exit code and stdout, which only `cmd_produce` owns: the pure function raises
and the CLI layer disposes, the same layering `classify_reading` and `cmd_read`
use. Pre-checking writability was rejected as a TOCTOU-shaped duplicate of the
write itself, blind to a full or read-only filesystem; falling back to
another directory was rejected because it would violate the
never-write-outside-the-gauge-directory invariant above and the reader would
report `missing` anyway. The alternative of emitting the display
while still exiting non-zero was rejected: per the harness behavior cited in the
invariant above, the status line is blanked on a non-zero exit code regardless of
what was printed, so a non-zero exit cannot coexist with a preserved display. No
failure signal is discarded — an unparseable payload and a failed gauge write
each still write one line to stderr — it is simply carried there rather than in
the exit code. Detecting a producer that has genuinely stopped, whose payload has
drifted, or whose gauge directory it cannot write therefore rests on `read`'s
`missing`/`stale` routing rather than on any signal `produce` emits: on a
mid-session payload drift or a mid-session write failure the gauge file already
exists, so the surviving classification is `stale`, while a gauge that was never
written at all classifies as `missing` when the gauge directory is absent or
traversable, and exits `2` as a malformed gauge when that directory cannot be
traversed or is not a directory at all — `classify_reading` routes a `stat`
that raises any `OSError` other than `FileNotFoundError` to `MalformedGauge`.
That is a dependency on the reader's routing, not an unconditional guarantee
from `produce`.

The installer embeds `sys.executable` — the interpreter now running — rather than
a bare `python3`/`python` token, because the status line runs under whatever the
harness's shell resolves on PATH, which need not be the interpreter this install
verified. A bare token could resolve to a 2.x, a venv-less, or a
dependency-short interpreter that cannot run this helper, which would silently
blank the gauge. Every path in the composed command is forward-slashed (via
`to_command_path`) so the one command string works whether the harness runs it
through `sh`, Git Bash, PowerShell, or `cmd.exe`; a backslash would be consumed
by Git Bash. The wrapped payload's quoting style is chosen from the detected
status-line shell (via `quote_for_shell`), not guessed, because Git Bash and
PowerShell disagree on how a literal is escaped and the wrong choice would
corrupt an operator's wrapped command.
"""

import argparse
import json
import os
import re
import shlex
import shutil
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
# what keep that mtime current. The window is deliberately turn-scale: the
# status line does not refresh mid-turn (tool calls within a turn trigger no
# refresh), so a healthy-but-quiet session's gauge can legitimately be many
# minutes old by the time a boundary is reached — a sub-turn window would flag
# such a gauge stale even with a healthy producer and a valid reading. A gauge
# older than this window still signals a stalled producer, not a healthy low
# reading, so `stale` still routes to a stop; the window just has to clear a
# long turn's wall-clock before it does. This value is a post-first-use
# recalibration input — the same RESEARCH-NEEDED owner recorded for the stop
# threshold — so treat 1200 (20 minutes) as a first cut, not a measured floor.
FRESHNESS_WINDOW_SECONDS = 1200

# The gauge file contract, defined once so no other code path spells it out.
GAUGE_DIR_NAME = ".quorum"
GAUGE_FILENAME_TEMPLATE = "context-usage-{session_id}.json"

# The persistent opt-out marker. Its mere existence is the signal — the contents
# are advisory only, so the boundary guard that reads it never parses the body.
# This filename is a cross-skill string contract: the guard that suppresses its
# missing-reading hard-stop reads exactly this name under the gauge directory,
# so it lives here, beside the gauge-file constants, defined once for both sides.
OPT_OUT_MARKER_FILENAME = "context-guard-opt-out"

# Human-readable body written into the opt-out marker. The body is advisory only
# — the boundary guard keys off the file's existence and never parses it — but it
# states precisely what the marker does and does not suppress, and how to reverse
# it, for an operator who opens the file. Held here so `write-opt-out` writes
# byte-identical content on every run (idempotence). It deliberately never
# mentions a removal command, because none exists: opting back in is a plain file
# delete.
OPT_OUT_MARKER_BODY = (
    "This marker opts this environment out of the context-guard's "
    "missing-reading hard-stop only.\n"
    "While it exists, a boundary check that cannot obtain a trustworthy "
    "context-window reading proceeds instead of stopping.\n"
    "It does NOT suppress a genuine over-threshold stop: when a real reading "
    "crosses the stop threshold, the guard still stops.\n"
    "Delete this file to re-enable the missing-reading guard.\n"
)

# Where the operator's user-level settings file lives. `CLAUDE_CONFIG_DIR`, when
# set, overrides the default configuration directory (`~/.claude`); the settings
# file inside it is always `settings.json`. These are named constants rather than
# inline literals because both the inspector and the installer must agree on the
# exact path they read and write.
CONFIG_DIR_ENV_VAR = "CLAUDE_CONFIG_DIR"
DEFAULT_CONFIG_DIR_NAME = ".claude"
SETTINGS_FILENAME = "settings.json"

# The project- and local-scope settings filenames that sit above user settings
# in the precedence order. A local file, when present, outranks the project file,
# and both outrank the user file this helper writes.
LOCAL_SETTINGS_FILENAME = "settings.local.json"

# File-based managed-settings locations, one per OS. Managed settings are the
# highest-precedence source, so a `statusLine` (or a hooks lockdown) here can
# override or disable a user-level status line entirely. These are module-level
# constants — never inlined — so the inspection code can be pointed at a
# temporary directory instead of these real system paths, which nothing but an
# administrator may write to.
MANAGED_SETTINGS_DIRS = {
    "darwin": "/Library/Application Support/ClaudeCode",
    "linux": "/etc/claude-code",
    "win32": "C:\\Program Files\\ClaudeCode",
}
MANAGED_SETTINGS_FILENAME = "managed-settings.json"
MANAGED_SETTINGS_DROPIN_DIRNAME = "managed-settings.d"

# Session identifier reserved for the installer's post-write self-check. It must
# satisfy `SESSION_ID_RE` so the self-check can write a throwaway gauge under it.
SELF_CHECK_SESSION_ID = "quo-setup-self-check"

# Tolerance, in seconds, allowed between the moment the installer starts its
# self-check and the modification time of the gauge that check expects the
# composed command to write. Its only job is to distinguish a gauge this run just
# triggered from one left over long ago; a small slack absorbs coarse filesystem
# mtime resolution without admitting a stale leftover.
SELF_CHECK_MTIME_TOLERANCE_SECONDS = 5

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


def opt_out_marker_path() -> Path:
    """Return the opt-out marker path. Pure — creates nothing.

    Resolves the temporary directory at call time, exactly like `gauge_dir()`,
    so a caller that redirects the tempdir sees the redirection take effect.
    """
    return gauge_dir() / OPT_OUT_MARKER_FILENAME


def config_dir() -> Path:
    """Return the Claude Code configuration directory.

    `CLAUDE_CONFIG_DIR`, when set and non-empty, overrides the default location;
    otherwise the default is `~/.claude`. `Path.home()` resolves the home
    directory on every OS — it covers `%USERPROFILE%` on Windows — so no per-OS
    branching is needed.
    """
    override = os.environ.get(CONFIG_DIR_ENV_VAR)
    if override:
        return Path(override)
    return Path.home() / DEFAULT_CONFIG_DIR_NAME


def user_settings_path() -> Path:
    """Return the user-level settings file path (`<config dir>/settings.json`)."""
    return config_dir() / SETTINGS_FILENAME


def normalize_path_for_compare(value: str) -> str:
    """Normalize a filesystem path for comparison against another path token.

    Applies `normpath` (collapse `.`/`..` and redundant separators) and
    `normcase` (case- and separator-fold on Windows, no-op on POSIX), then folds
    any remaining backslash to a forward slash so a command string written with
    forward slashes compares equal to a native path. Used for every script-path
    comparison so a moved or differently-spelled path is still recognized.
    """
    return os.path.normcase(os.path.normpath(value)).replace("\\", "/")


def to_command_path(path) -> str:
    """Return an absolute path safe to embed in a status-line command string.

    Backslashes are replaced with forward slashes: on Windows the status-line
    command runs through Git Bash when it is installed, and Git Bash consumes
    unquoted backslashes in the command string — so a forward-slashed path is the
    only spelling that survives on every platform.
    """
    return os.path.abspath(str(path)).replace("\\", "/")


def _extract_wrap_command(tokens):
    """Return the `--wrap-command` payload from a token list, or `None`.

    Accepts both the space-separated (`--wrap-command X`) and the joined
    (`--wrap-command=X`) spellings, and returns the payload exactly as it was
    tokenized (already unquoted by `shlex.split`).
    """
    prefix = "--wrap-command="
    for index, token in enumerate(tokens):
        if token == "--wrap-command":
            if index + 1 < len(tokens):
                return tokens[index + 1]
            return None
        if token.startswith(prefix):
            return token[len(prefix):]
    return None


def classify_status_line_command(command, script_path) -> tuple:
    """Classify an existing status-line command against this helper.

    Returns `(state, wrapped_command)` where `state` is one of:

    - `"direct"` — a command that runs this exact script's `produce` with no
      wrapped command (`wrapped_command` is `None`).
    - `"wrapped"` — this exact script's `produce` wrapping an operator command;
      `wrapped_command` is that wrapped payload string.
    - `"other-install"` — some OTHER `context_gauge.py` (basename match, path
      differs) running `produce`; `wrapped_command` is any wrap payload it
      carried, else `None`.
    - `"foreign"` — anything else, carried as an opaque string; `wrapped_command`
      is `None`. A command that `shlex.split` cannot tokenize is `foreign` too —
      it is never parsed further.
    """
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        # Unbalanced quoting or similar: do not guess at its structure.
        return ("foreign", None)

    has_produce = "produce" in tokens
    wrap = _extract_wrap_command(tokens)
    target = normalize_path_for_compare(script_path)

    names_self = any(normalize_path_for_compare(token) == target for token in tokens)
    if names_self and has_produce:
        if wrap is not None:
            return ("wrapped", wrap)
        return ("direct", None)

    names_helper = any(
        os.path.basename(token) == "context_gauge.py" for token in tokens
    )
    if names_helper and has_produce:
        return ("other-install", wrap)

    return ("foreign", None)


def status_line_shell() -> str:
    """Return the shell the harness runs the status-line command through.

    `"sh"` on POSIX. On Windows the status-line command runs through Git Bash
    when Git Bash is installed, or through PowerShell when it is absent, so
    `"git-bash"` is returned when `shutil.which("bash")` finds one and
    `"powershell"` otherwise. The quoting of an embedded wrapped command depends
    on which of these it is.
    """
    if os.name == "nt":
        if shutil.which("bash"):
            return "git-bash"
        return "powershell"
    return "sh"


def quote_for_shell(value: str, shell: str) -> str:
    """Quote `value` for the shell the status-line command runs through.

    `sh` and `git-bash` both accept POSIX quoting, so `shlex.quote` covers them.
    `powershell` uses single quotes with every inner single quote doubled. The
    quoting shell is chosen at install time because Claude Code runs the
    status-line command through Git Bash when it is present on Windows and
    PowerShell otherwise, and the two disagree on how a literal is escaped.
    """
    if shell == "powershell":
        return "'" + value.replace("'", "''") + "'"
    return shlex.quote(value)


def compose_status_line_command(python_exe, script_path, wrap_command, shell) -> str:
    """Compose the status-line command that runs this helper's `produce`.

    Returns `"<python>" "<script>" produce`, both paths passed through
    `to_command_path` (absolute, forward-slashed) and wrapped in DOUBLE quotes.
    Double quotes on our own two tokens are safe in `sh`, Git Bash, PowerShell,
    and `cmd.exe` alike, and because the paths are forward-slashed there is no
    backslash for Git Bash to consume. When `wrap_command` is non-empty,
    ` --wrap-command <quoted>` is appended, quoted for `shell`.
    """
    python_token = to_command_path(python_exe)
    script_token = to_command_path(script_path)
    command = '"{0}" "{1}" produce'.format(python_token, script_token)
    if wrap_command:
        command += " --wrap-command " + quote_for_shell(wrap_command, shell)
    return command


def _managed_settings_dir() -> Path:
    """Return the file-based managed-settings directory for the current OS."""
    if sys.platform.startswith("darwin"):
        key = "darwin"
    elif os.name == "nt":
        key = "win32"
    else:
        key = "linux"
    return Path(MANAGED_SETTINGS_DIRS[key])


def detect_higher_precedence_sources(repo_root, managed_dir=None) -> list:
    """Report settings sources that outrank a user-level status line.

    Best-effort and never raises: any file that is absent, unreadable, or
    unparseable is skipped silently, because a malformed file belonging to
    someone else must not fail our inspection. Each returned entry is
    `{"scope": ..., "path": ..., "reason": ...}`.

    Checks the repo's project (`.claude/settings.json`) and local
    (`.claude/settings.local.json`) files for a `statusLine` key, and the per-OS
    managed-settings file plus every `*.json` in its `managed-settings.d/`
    drop-in directory for a `statusLine` key, for `allowManagedHooksOnly` truthy,
    and for `disableAllHooks` truthy. `managed_dir` is injectable so tests can
    point the managed-scope checks at a temporary directory instead of the real
    system location, which only an administrator may write to.
    """
    sources = []
    repo_root = Path(repo_root)

    def _load_object(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError, UnicodeDecodeError):
            return None
        if not isinstance(data, dict):
            return None
        return data

    project = repo_root / DEFAULT_CONFIG_DIR_NAME / SETTINGS_FILENAME
    project_data = _load_object(project)
    if project_data is not None and "statusLine" in project_data:
        sources.append({
            "scope": "project",
            "path": str(project),
            "reason": "project settings define a statusLine that outranks user settings",
        })

    local = repo_root / DEFAULT_CONFIG_DIR_NAME / LOCAL_SETTINGS_FILENAME
    local_data = _load_object(local)
    if local_data is not None and "statusLine" in local_data:
        sources.append({
            "scope": "local",
            "path": str(local),
            "reason": "local settings define a statusLine that outranks user settings",
        })

    if managed_dir is None:
        managed_dir = _managed_settings_dir()
    managed_dir = Path(managed_dir)
    managed_files = [managed_dir / MANAGED_SETTINGS_FILENAME]
    dropin = managed_dir / MANAGED_SETTINGS_DROPIN_DIRNAME
    try:
        managed_files.extend(sorted(dropin.glob("*.json")))
    except OSError:
        pass
    for managed_file in managed_files:
        managed_data = _load_object(managed_file)
        if managed_data is None:
            continue
        if "statusLine" in managed_data:
            sources.append({
                "scope": "managed",
                "path": str(managed_file),
                "reason": "managed settings define a statusLine that outranks user settings",
            })
        if managed_data.get("allowManagedHooksOnly"):
            sources.append({
                "scope": "managed",
                "path": str(managed_file),
                "reason": "managed settings set allowManagedHooksOnly, so only a managed statusLine runs",
            })
        if managed_data.get("disableAllHooks"):
            sources.append({
                "scope": "managed",
                "path": str(managed_file),
                "reason": "managed settings set disableAllHooks, so the status line is disabled",
            })
    return sources


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

    Propagates `OSError` from `ensure_gauge_dir`, from `open`, and from the
    implicit flush/close on exit from the `with` block: this function does not
    dispose of a write failure, its caller does.
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
            try:
                write_gauge(record)
            except OSError as error:
                # The gauge is best-effort; the display is not. An unwritable or
                # full gauge directory must not blank the operator's status line.
                # Catch here rather than inside `write_gauge`: pure functions
                # raise, the CLI layer disposes. `OSError` and not `Exception` —
                # `record` came from a `json.loads` result, so the `json.dumps`
                # inside `write_gauge` cannot raise `TypeError` on this path, and
                # a broader catch would swallow genuine bugs. The wrapped call
                # covers all three failure points: the `mkdir`, the `open`, and
                # the implicit flush/close where ENOSPC/EDQUOT surface. The
                # message names the gauge *directory* because that is the one
                # location correct on all three arms, and because the
                # exception's own `filename` is absent on the flush/close arm
                # (ENOSPC surfaces as a bare "No space left on device" with no
                # path). Naming the gauge-*file* path instead would be wrong on
                # the `mkdir` arm, which never reaches the file.
                warn(f"cannot publish the context gauge under {gauge_dir()}: {error}")
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
        raise MalformedGauge(
            f"cannot stat gauge file (is the gauge directory {gauge_dir()} "
            f"present as a directory you can traverse?): {error}"
        ) from error

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


def cmd_inspect_statusline(args) -> int:
    # The helper names itself (own-skill resolution): the script path is derived
    # from `__file__`, never passed in, so a caller cannot point the inspection
    # at a different script.
    script_path = str(Path(__file__).resolve())
    python_executable = sys.executable
    shell = status_line_shell()
    settings_path = user_settings_path()
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    settings_exists = settings_path.exists()
    status_line_present = False
    status_line_command = None
    status_line_extra_keys = {}
    producer_state = "absent"
    wrapped_command = None
    producer_current = False

    if settings_exists:
        # A settings file that exists but does not parse as a JSON object is the
        # one hard failure: reporting `absent` here would let the installer
        # clobber a file it could not read. Fail (exit 2) with a single stderr
        # line and print nothing on stdout.
        try:
            text = settings_path.read_text(encoding="utf-8")
            settings = json.loads(text)
        except (OSError, ValueError, UnicodeDecodeError) as error:
            return fail(f"cannot read settings file {settings_path}: {error}")
        if not isinstance(settings, dict):
            return fail(
                f"settings file {settings_path} is not a JSON object"
            )

        status_line = settings.get("statusLine")
        if isinstance(status_line, dict):
            # Every key other than `type` and `command` is carried through so the
            # installer can preserve it on a rewrite.
            status_line_extra_keys = {
                key: value
                for key, value in status_line.items()
                if key not in ("type", "command")
            }
            command = status_line.get("command")
            if isinstance(command, str) and command:
                status_line_present = True
                status_line_command = command
                state, wrap = classify_status_line_command(command, script_path)
                producer_state = state
                wrapped_command = wrap
                if state in ("direct", "wrapped"):
                    composed = compose_status_line_command(
                        python_executable, script_path, wrap, shell
                    )
                    producer_current = command == composed
            # A missing, empty, or non-string `command` leaves `producer_state`
            # `absent` and `status_line_present` false — a degenerate shape is
            # treated as no effective status line.
        # A non-object `statusLine` likewise leaves `producer_state` `absent`.

    opt_out_path = opt_out_marker_path()
    result = {
        "settings_path": str(settings_path),
        "settings_exists": settings_exists,
        "status_line_present": status_line_present,
        "status_line_command": status_line_command,
        "status_line_extra_keys": status_line_extra_keys,
        "producer_state": producer_state,
        "wrapped_command": wrapped_command,
        "producer_current": producer_current,
        "script_path": script_path,
        "python_executable": python_executable,
        "opt_out_marker_path": str(opt_out_path),
        # `.exists()` never creates the gauge directory as a side effect of the
        # lookup, so a read-only inspection stays read-only.
        "opt_out_marker_present": opt_out_path.exists(),
        "higher_precedence_sources": detect_higher_precedence_sources(repo_root),
        "status_line_shell": shell,
    }
    print(json.dumps(result))
    return 0


def _run_self_check(composed: str) -> dict:
    """Run the composed command once and report whether it wrote a fresh gauge.

    Advisory only — the caller NEVER fails the install on the outcome. Spawns the
    composed command through the platform shell (via `run_wrapped`, so the same
    `shell=True` / timeout discipline applies) with a synthetic payload keyed by
    the reserved self-check session id, then checks that the reserved gauge was
    written within `SELF_CHECK_MTIME_TOLERANCE_SECONDS` of when this check began.
    Returns `{"verified": <bool>, "detail": <str>}`.
    """
    payload = json.dumps({
        "session_id": SELF_CHECK_SESSION_ID,
        "context_window": {"used_percentage": 0},
        "workspace": {"current_dir": os.getcwd()},
    })
    started = time.time()
    run_wrapped(composed, payload.encode("utf-8"))
    check_path = gauge_path(SELF_CHECK_SESSION_ID)
    try:
        mtime = check_path.stat().st_mtime
    except OSError:
        return {
            "verified": False,
            "detail": (
                "composed command wrote no gauge for the reserved self-check "
                "session id"
            ),
        }
    if mtime >= started - SELF_CHECK_MTIME_TOLERANCE_SECONDS:
        return {
            "verified": True,
            "detail": "composed command wrote a fresh gauge for the reserved self-check session id",
        }
    return {
        "verified": False,
        "detail": "reserved self-check gauge exists but was not refreshed by this run",
    }


def cmd_install_statusline(args) -> int:
    # Own-skill resolution: the script path is derived from `__file__`, never
    # passed in, so the installer can only ever wire up THIS helper.
    script_path = str(Path(__file__).resolve())
    python_executable = args.python if args.python else sys.executable
    shell = status_line_shell()
    settings_path = user_settings_path()
    repo_root = Path(args.repo_root) if args.repo_root else Path.cwd()

    # Step 1: inspect existing settings. Start from an empty object so an absent
    # file writes a settings file whose only key is `statusLine`.
    settings = {}
    existing_status_line = {}
    existing_command = None
    producer_state = "absent"
    wrapped_payload = None
    extra_keys = {}

    if settings_path.exists():
        # Never clobber a settings file we could not read: an unparseable file is
        # the one hard failure, and it writes NOTHING.
        try:
            text = settings_path.read_text(encoding="utf-8")
            settings = json.loads(text)
        except (OSError, ValueError, UnicodeDecodeError) as error:
            return fail(f"cannot read settings file {settings_path}: {error}")
        if not isinstance(settings, dict):
            return fail(f"settings file {settings_path} is not a JSON object")
        status_line = settings.get("statusLine")
        if isinstance(status_line, dict):
            existing_status_line = status_line
            extra_keys = {
                key: value
                for key, value in status_line.items()
                if key not in ("type", "command")
            }
            command = status_line.get("command")
            if isinstance(command, str) and command:
                existing_command = command
                producer_state, wrapped_payload = classify_status_line_command(
                    command, script_path
                )

    # Step 2: determine the wrap payload. This is the anti-double-wrap step — a
    # `wrapped`/`other-install` payload is REUSED, never re-wrapped.
    if producer_state == "foreign":
        # Carry the entire existing command opaquely.
        wrap_command = existing_command
    elif producer_state in ("wrapped", "other-install"):
        # Reuse the payload already extracted from the existing wrapper.
        wrap_command = wrapped_payload
    else:
        # `direct` or `absent`: nothing to wrap.
        wrap_command = None

    # Step 3: compose the new command.
    composed = compose_status_line_command(
        python_executable, script_path, wrap_command, shell
    )

    # Step 4: an already-current producer is a no-op — do not touch the file.
    if producer_state in ("direct", "wrapped") and composed == existing_command:
        summary = {
            "action": "already-configured",
            "settings_path": str(settings_path),
            "previous_command": existing_command,
            "new_command": composed,
            "preserved_status_line_keys": sorted(extra_keys.keys()),
            "self_check": {
                "verified": None,
                "detail": "not run: already-configured, no write performed",
            },
            "higher_precedence_sources": detect_higher_precedence_sources(repo_root),
            "status_line_shell": shell,
        }
        print(json.dumps(summary))
        return 0

    # Explicit `producer_state` → `action` contract (see the module docstring).
    # `direct`/`wrapped` reaching here are, by the guard above, non-identical, so
    # they map to `repointed`.
    action = {
        "absent": "installed",
        "foreign": "wrapped",
        "other-install": "repointed",
        "direct": "repointed",
        "wrapped": "repointed",
    }[producer_state]

    # Step 5: read-modify-write. Merge over the existing `statusLine` object's
    # other keys so `padding`, `refreshInterval`, `hideVimModeIndicator`, ...
    # survive, and leave every unrelated top-level key untouched.
    new_status_line = dict(existing_status_line)
    new_status_line["type"] = "command"
    new_status_line["command"] = composed
    settings["statusLine"] = new_status_line

    config_directory = settings_path.parent
    config_directory.mkdir(parents=True, exist_ok=True)
    # Atomic write: temp file in the settings file's own directory, then
    # `os.replace`; unlink the temp file on any exception so no partial file is
    # left behind. No backup file by design.
    fd, tmp = tempfile.mkstemp(
        dir=str(config_directory), prefix="." + SETTINGS_FILENAME + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2)
            handle.write("\n")
        os.replace(tmp, str(settings_path))
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

    # Step 6: advisory self-check. Never fails the install — the write already
    # stands, so the exit code stays 0 regardless of the outcome.
    if args.no_self_check:
        self_check = {"verified": None, "detail": "skipped: --no-self-check"}
    else:
        self_check = _run_self_check(composed)

    # Step 7: one compact JSON summary, exit 0.
    summary = {
        "action": action,
        "settings_path": str(settings_path),
        "previous_command": existing_command,
        "new_command": composed,
        "preserved_status_line_keys": sorted(extra_keys.keys()),
        "self_check": self_check,
        "higher_precedence_sources": detect_higher_precedence_sources(repo_root),
        "status_line_shell": shell,
    }
    print(json.dumps(summary))
    return 0


def cmd_write_opt_out(args) -> int:
    # Reuse `ensure_gauge_dir()` so the marker lands beside the gauge files under
    # the same `<tempdir>/.quorum/` directory, created if absent.
    ensure_gauge_dir()
    marker_path = opt_out_marker_path()
    # Truncate-write (never append) so a repeated run rewrites byte-identical
    # content — idempotent. There is no removal path here, by design.
    with open(marker_path, "w", encoding="utf-8") as handle:
        handle.write(OPT_OUT_MARKER_BODY)
    print(str(marker_path))
    return 0


def cmd_stop_threshold(args) -> int:
    # Emit the single-definition-site constant directly so a consumer obtains the
    # threshold from here rather than restating the literal. Read-only: writes no
    # file, creates no directory, and prints nothing on stderr. `print` supplies
    # exactly one decimal integer followed by a trailing newline.
    print(STOP_THRESHOLD_PERCENT)
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

    inspect = subparsers.add_parser(
        "inspect-statusline",
        help="report the current user status-line configuration as one JSON object",
    )
    inspect.add_argument(
        "--repo-root",
        dest="repo_root",
        default=None,
        help="repository root to check for higher-precedence settings (default: cwd)",
    )

    install = subparsers.add_parser(
        "install-statusline",
        help="write or update the user status-line command to run the gauge producer",
    )
    install.add_argument(
        "--repo-root",
        dest="repo_root",
        default=None,
        help="repository root to report higher-precedence settings for (default: cwd)",
    )
    install.add_argument(
        "--python",
        dest="python",
        default=None,
        help="interpreter to embed in the composed command (default: sys.executable)",
    )
    install.add_argument(
        "--no-self-check",
        dest="no_self_check",
        action="store_true",
        help="skip the post-write self-check (no subprocess is spawned)",
    )

    subparsers.add_parser(
        "write-opt-out",
        help="write the persistent opt-out marker that suppresses the missing-reading stop",
    )

    subparsers.add_parser(
        "stop-threshold",
        help="print the stop threshold percentage a consumer compares a reading against",
    )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.mode == "produce":
        return cmd_produce(args)
    if args.mode == "read":
        return cmd_read(args)
    if args.mode == "inspect-statusline":
        return cmd_inspect_statusline(args)
    if args.mode == "install-statusline":
        return cmd_install_statusline(args)
    if args.mode == "write-opt-out":
        return cmd_write_opt_out(args)
    return cmd_stop_threshold(args)


if __name__ == "__main__":
    sys.exit(main())
