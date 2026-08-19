"""Unit + CLI-contract tests for context_gauge.py.

Two layers, per docs/test-writing-guide.md `## The two-layer pattern`:

1. **Unit layer** — the helper is loaded in-process with `conftest.load_script`
   and its pure functions are called directly. The platform temp directory is
   redirected with `monkeypatch.setattr(mod.tempfile, "gettempdir", ...)` — via
   `monkeypatch` and never a bare assignment, because `mod.tempfile` IS the
   shared stdlib module object and a leaked patch would be process-global.
2. **CLI-contract layer** — the script is run as a subprocess and asserted on
   `returncode` / `stdout` / `stderr`. This is the layer that pins the contract
   the installer and the consuming skills branch on.

Assumed equality between the two session-id sources (SDD SR-4.4)
----------------------------------------------------------------
Every test here injects a SYNTHETIC session identifier on BOTH sides of the
gauge contract: on the produce side it is the `session_id` field of the JSON
payload fed to `produce` on stdin, and on the read side it is the value handed
to `read --session-id`. Because this suite supplies both values itself, it can
only ever prove that the producer and the reader agree with EACH OTHER — it
cannot detect an upstream divergence between the identifier the harness puts
in the status-line payload's `session_id` field and the identifier the consumer
reads out of the `CLAUDE_CODE_SESSION_ID` environment variable. Those two are
different channels owned by the harness, and nothing in this file observes
either one. Their equality was live-verified by hand when the feature was
designed; re-probing it if the harness changes is tracked by upstream Issue
**b.cj2**, not by any assertion below. Read a green run here as "the two halves
of this helper agree", never as "the harness still supplies the same id twice".

Isolation
---------
No test writes to the real temp directory. An autouse fixture enforces that by
snapshotting the real `<tempdir>/.quorum` at setup and asserting on teardown
that no entry under the pytest-reserved `quorum-pytest-` session-id prefix was
added OR rewritten (the snapshot keys on stat metadata, so an overwrite of a
name a previous run left behind still fails — see `_real_prefixed_entries`).
That stat keying is itself regression-pinned by the two `test_snapshot_helper_*`
tests, because a passing run leaves the fixture's delta empty and would not
otherwise notice the keying being weakened. Nothing in this module ever deletes
anything under that directory (CLAUDE.md `## Scratch-file convention`).
"""

import json
import os
import subprocess
import sys
import tempfile
import time
import types
from pathlib import Path

import pytest

from conftest import CONTEXT_GAUGE, load_script, script_path

mod = load_script(CONTEXT_GAUGE)
SCRIPT = script_path(CONTEXT_GAUGE)

# Captured at IMPORT time, before any test can monkeypatch `tempfile.gettempdir`.
# The safety fixture below keys on this so a test that leaks a patch cannot also
# hide the leak by moving the directory the fixture inspects.
REAL_TEMP_ROOT = Path(tempfile.gettempdir())

# Spelled literally rather than read from `mod`, so a mutation of the helper's
# own constant cannot relocate the directory the safety fixture watches.
REAL_GAUGE_DIR = REAL_TEMP_ROOT / ".quorum"

# Reserved token: every synthetic session id used by a test that WRITES a gauge
# file starts with this. Pure-derivation calls (e.g. `gauge_path("abc-123")`,
# which creates nothing) are exempt. Task 1's manual smoke-verify Subtask picks
# its real-tempdir session id OUTSIDE this prefix, so its never-deleted artifact
# cannot collide with the delta check below.
TEST_SESSION_PREFIX = "quorum-pytest-"


def _real_prefixed_entries(directory=None):
    """Identity tuples for REAL-gauge-dir files under this suite's reserved prefix.

    Keyed on `(name, size, mtime_ns)` rather than name alone, because a name-only
    snapshot is self-disarming: nothing here ever deletes a leaked artifact
    (CLAUDE.md `## Scratch-file convention`), so a genuinely-leaking test would
    fail on its first run, leave the file behind, and then OVERWRITE that same
    name on every later run for an empty delta — the fixture would silently stop
    detecting the leak it had just caught. Stat metadata re-arms it: an overwrite
    moves `mtime_ns` (and usually `size`), so the delta fires again.

    `directory` is a TEST-ONLY injection point, defaulting to `None` so the
    production path stays un-indirected: the autouse fixture calls this with no
    arguments and the module-level `REAL_GAUGE_DIR` constant is what gets
    inspected, exactly as before. It exists so the two
    `test_snapshot_helper_*` regression tests below can point this same code at
    a `tmp_path` and prove the tuple keying still detects an overwrite — that
    keying is the whole reason this helper is not a plain set of names, and
    nothing else in the suite would fail if someone "simplified" it back.

    Scope limit, stated rather than papered over: on a filesystem with coarse
    timestamp granularity (1-2s ticks are still real on some FAT/HFS+ and network
    mounts) a same-size overwrite that lands in the SAME tick as the setup
    snapshot leaves both key components unchanged and would not show in the
    delta. That needs the re-leak to happen within one session AND within one
    tick of the snapshot; the first leaking test already fails loudly, and
    separate runs are seconds-to-minutes apart, so this narrows detection in a
    corner rather than disarming it.
    """
    root = REAL_GAUGE_DIR if directory is None else Path(directory)
    if not root.is_dir():
        return set()
    entries = set()
    for p in root.glob(f"context-usage-{TEST_SESSION_PREFIX}*"):
        try:
            st = p.stat()
        except OSError:
            # Vanished between the glob yield and the stat — an OS tmp-reaper, or
            # a user clearing <tempdir>/.quorum mid-run. Skip rather than let this
            # safety net crash the test it is guarding. Detection power is
            # unaffected: an entry absent at snapshot time is absent from BOTH
            # sides of the delta unless a test recreates it, and a recreated name
            # lands in `after` as a new stat tuple and still fires.
            continue
        entries.add((p.name, st.st_size, st.st_mtime_ns))
    return entries


@pytest.fixture(autouse=True)
def no_real_tempdir_writes():
    """Fail any test that leaks a gauge write into the real temp directory.

    A delta assertion scoped to the reserved prefix, not an emptiness assertion:
    it must stay collision-proof against artifacts that were already there (the
    helper never deletes anything) and against genuinely-new NON-prefixed files
    a live status-line producer may write on this machine mid-run. Detection
    power survives the narrowing because every test that writes a gauge file is
    required to use `TEST_SESSION_PREFIX` — so a test that forgets its
    `monkeypatch` or its `env=` override still leaks under the reserved prefix
    and is caught here. Because the delta is over `_real_prefixed_entries`'s
    stat-keyed tuples, a leak that OVERWRITES a name left behind by an earlier
    run is caught too, not just a brand-new name. Nothing is ever deleted.
    """
    before = _real_prefixed_entries()
    yield
    after = _real_prefixed_entries()
    leaked = sorted({name for name, _size, _mtime in after - before})
    assert not leaked, (
        "test wrote a gauge file into the real temp directory "
        f"{REAL_GAUGE_DIR}: {leaked}"
    )


# --- the safety fixture's own regression pins -------------------------------
#
# These two tests guard the guard. `_real_prefixed_entries` keys on
# `(name, size, mtime_ns)` specifically so that an OVERWRITE of a name a leaking
# earlier run already left behind still shows up in the delta — see its
# docstring. Nothing else in this suite exercises that: the fixture's delta is
# empty on every passing run, so collapsing the tuple back to a bare set of
# names would leave the whole suite green while silently disarming the leak
# detector. Both tests below point the helper at `tmp_path` via its test-only
# `directory` argument and assert the delta fires for an overwrite whose NAME is
# unchanged — the exact case a name-only snapshot misses.

def test_snapshot_helper_detects_a_different_size_overwrite(tmp_path):
    entry = tmp_path / f"context-usage-{TEST_SESSION_PREFIX}snap-resize.json"
    entry.write_text("first", encoding="utf-8")
    before = _real_prefixed_entries(tmp_path)
    assert len(before) == 1

    entry.write_text("a considerably longer second body", encoding="utf-8")
    after = _real_prefixed_entries(tmp_path)

    assert after - before, "an overwrite must show in the delta"
    # The name did not change, so a name-keyed snapshot would have seen nothing.
    assert {name for name, _size, _mtime in after} == {
        name for name, _size, _mtime in before
    }


def test_snapshot_helper_detects_a_same_size_overwrite(tmp_path):
    entry = tmp_path / f"context-usage-{TEST_SESSION_PREFIX}snap-same-size.json"
    entry.write_text("AAAA", encoding="utf-8")
    before = _real_prefixed_entries(tmp_path)
    assert len(before) == 1

    entry.write_text("BBBB", encoding="utf-8")
    # Advance the mtime explicitly rather than sleeping: the write above may land
    # in the same filesystem timestamp tick as the snapshot, which is the coarse
    # granularity caveat the helper's docstring already scopes out. Forcing the
    # tick keeps this test about the KEYING, not about clock resolution.
    st = entry.stat()
    os.utime(entry, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000_000))
    after = _real_prefixed_entries(tmp_path)

    # Same name AND same size — `mtime_ns` is the only component that moved, so
    # this fails for any keying that drops it.
    assert after - before, "a same-size overwrite must still show in the delta"
    assert {name for name, _size, _mtime in after} == {
        name for name, _size, _mtime in before
    }
    assert {size for _name, size, _mtime in after} == {
        size for _name, size, _mtime in before
    }


# ===========================================================================
# Layer 1 — unit (in-process, `mod.*` called directly)
# ===========================================================================

def _patch_tempdir(monkeypatch, tmp_path):
    """Redirect the helper's temp-directory lookup at the module object it uses."""
    monkeypatch.setattr(mod.tempfile, "gettempdir", lambda: str(tmp_path))


def _seed(monkeypatch, tmp_path, session_id, text):
    """Create a gauge file with exact raw `text` under the patched temp root."""
    _patch_tempdir(monkeypatch, tmp_path)
    mod.ensure_gauge_dir()
    path = mod.gauge_path(session_id)
    path.write_text(text, encoding="utf-8")
    return path


# --- path derivation -------------------------------------------------------

def test_gauge_path_shape(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    assert mod.gauge_path("abc-123") == tmp_path / ".quorum" / "context-usage-abc-123.json"


def test_gauge_path_resolves_tempdir_at_call_time(monkeypatch, tmp_path):
    # Pure derivation, creates nothing — exempt from the TEST_SESSION_PREFIX rule.
    before = mod.gauge_path("abc-123")
    _patch_tempdir(monkeypatch, tmp_path)
    after = mod.gauge_path("abc-123")
    # Same call, different roots: the tempdir is looked up per call, not
    # captured at import time (which would make the redirection a no-op).
    assert before != after
    assert after.parent.parent == tmp_path


def test_gauge_dir_is_pure(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    assert mod.gauge_dir() == tmp_path / ".quorum"
    assert not (tmp_path / ".quorum").exists()


# --- session-id validation -------------------------------------------------

def test_is_valid_session_id_accepts_uuid_shape():
    assert mod.is_valid_session_id("3f2a1b7c-9d4e-4f80-8a11-6b0c2d5e7f91") is True


@pytest.mark.parametrize(
    "bad",
    ["", "../escape", "a/b", "a\\b", None, 123],
    ids=["empty", "dotdot", "posix-sep", "windows-sep", "none", "int"],
)
def test_is_valid_session_id_rejects(bad):
    assert mod.is_valid_session_id(bad) is False


# --- directory creation ----------------------------------------------------

def test_ensure_gauge_dir_creates_and_is_idempotent(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    target = tmp_path / ".quorum"
    assert not target.exists()
    first = mod.ensure_gauge_dir()
    assert first == target and target.is_dir()
    second = mod.ensure_gauge_dir()
    assert second == target and target.is_dir()


# --- tunable constants -----------------------------------------------------

def test_tunable_constants():
    # These two literals are the SINGLE definition sites of the guard's tunables:
    # consumers read them from here rather than re-deriving them. A change to
    # either is a deliberate re-calibration of the guard (and of the arithmetic
    # documented beside them in the helper), never an incidental edit — so this
    # test is meant to fail and force that decision to be made explicitly.
    assert mod.STOP_THRESHOLD_PERCENT == 50
    assert mod.FRESHNESS_WINDOW_SECONDS == 120


# --- extract_gauge_record --------------------------------------------------

def test_extract_gauge_record_carries_context_window_verbatim():
    window = {"used_percentage": 42, "extra": {"nested": [1, 2]}, "tokens": 8123}
    payload = {"session_id": "s-1", "context_window": window, "cwd": "/x/y"}
    record = mod.extract_gauge_record(payload)
    assert record == {"session_id": "s-1", "context_window": window}
    # Every field of the window survives, and nothing beyond the two keys leaks in.
    assert record["context_window"] == window
    assert set(record) == {"session_id", "context_window"}


@pytest.mark.parametrize(
    "payload",
    [
        {"session_id": "s-1"},
        {"session_id": "s-1", "context_window": None},
        {"session_id": "s-1", "context_window": 0},
        {"session_id": "s-1", "context_window": []},
        {"session_id": "s-1", "context_window": "37"},
    ],
    ids=["absent", "null", "zero", "list", "string"],
)
def test_extract_gauge_record_absent_or_non_dict_window_becomes_empty(payload):
    record = mod.extract_gauge_record(payload)
    # Empty object — never a fabricated percentage and never a `0`, either of
    # which the reader would classify as abundant headroom.
    assert record == {"session_id": "s-1", "context_window": {}}


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"session_id": ""},
        {"session_id": None},
        {"session_id": 123},
        {"session_id": ["s-1"]},
        {"session_id": "../escape"},
        {"session_id": "a/b"},
    ],
    ids=["absent", "empty", "none", "int", "list", "dotdot", "sep"],
)
def test_extract_gauge_record_returns_none_for_unusable_session_id(payload):
    assert mod.extract_gauge_record(payload) is None


# --- parse_payload ---------------------------------------------------------

@pytest.mark.parametrize(
    "raw", [b"", b"   ", b"\n", b" \t\r\n "], ids=["empty", "spaces", "newline", "mixed"]
)
def test_parse_payload_empty_or_whitespace_is_none(raw):
    assert mod.parse_payload(raw) is None


def test_parse_payload_valid_object():
    assert mod.parse_payload(b'{"session_id": "s-1"}') == {"session_id": "s-1"}


def test_parse_payload_unparseable_is_distinguishable_from_empty():
    # Task 1's body required only "a distinguishable condition" for this case
    # and did not pin the mechanism; the shipped helper raises ValueError
    # (json.JSONDecodeError subclasses it). Assert the mechanism that shipped.
    with pytest.raises(ValueError):
        mod.parse_payload(b"{not json")
    # ...and assert positively that it is distinguishable from the empty-stdin
    # `None`: the empty case returns, the malformed case raises.
    assert mod.parse_payload(b"") is None


@pytest.mark.parametrize(
    "raw", [b"[1, 2]", b'"a string"', b"42", b"null", b"true"],
    ids=["array", "string", "number", "null", "bool"],
)
def test_parse_payload_non_object_top_level_raises(raw):
    with pytest.raises(ValueError):
        mod.parse_payload(raw)


# --- read_stdin_once: the defensive branches -------------------------------
#
# `read_stdin_once` is the single stdin drain, and the CLI layer only ever
# exercises its happy path (a real pipe). Its two defensive branches are what
# keep a status-line refresh from crashing when the harness hands the producer
# no usable stdin at all — a status line that raises is worse than a blank one,
# and the gauge write happens downstream of this call. Both are pinned here
# in-process because there is no portable way to hand a subprocess a `sys.stdin`
# with no `buffer`.
#
# `mod.sys` IS the shared stdlib module object, so these patches go through
# `monkeypatch` (auto-undone) and never a bare assignment — a leaked patch would
# be process-global and would break pytest's own capture.


class _NoBufferStdin:
    """A stdin-like object with no `buffer` attribute at all."""


@pytest.mark.parametrize(
    "stdin", [None, _NoBufferStdin()], ids=["none", "no-buffer-attr"]
)
def test_read_stdin_once_without_a_usable_buffer_returns_empty_bytes(
    monkeypatch, stdin
):
    monkeypatch.setattr(mod.sys, "stdin", stdin)
    result = mod.read_stdin_once()
    # Exactly `b""` — not `None`, not `""`. `parse_payload` routes `b""` to the
    # silent no-op; anything else would either crash or look like a payload.
    assert result == b""
    assert isinstance(result, bytes)


@pytest.mark.parametrize(
    "error",
    [OSError("stdin is closed"), ValueError("I/O operation on closed file")],
    ids=["oserror", "valueerror"],
)
def test_read_stdin_once_swallows_a_failing_buffer_read(monkeypatch, error):
    """The shipped helper catches `(OSError, ValueError)`, so both are asserted.

    `ValueError` is not incidental: reading a closed file object raises
    `ValueError`, not `OSError`, and that is a realistic shape for a status-line
    process whose stdin has already been torn down.
    """

    class _FailingBuffer:
        def read(self):
            raise error

    class _Stdin:
        buffer = _FailingBuffer()

    monkeypatch.setattr(mod.sys, "stdin", _Stdin())
    result = mod.read_stdin_once()
    assert result == b""
    assert isinstance(result, bytes)


def test_read_stdin_once_returns_the_buffer_bytes_verbatim(monkeypatch):
    """Contrast case, so the two defensive tests above cannot pass vacuously."""

    class _Buffer:
        def read(self):
            return b'{"session_id": "s-1"}'

    class _Stdin:
        buffer = _Buffer()

    monkeypatch.setattr(mod.sys, "stdin", _Stdin())
    assert mod.read_stdin_once() == b'{"session_id": "s-1"}'


# --- write_gauge -----------------------------------------------------------

def test_write_gauge_writes_to_gauge_path(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = TEST_SESSION_PREFIX + "write"
    record = {"session_id": session_id, "context_window": {"used_percentage": 12}}
    path = mod.write_gauge(record)
    assert path == mod.gauge_path(session_id)
    assert json.loads(path.read_text(encoding="utf-8")) == record


def test_write_gauge_second_write_truncates_rather_than_appends(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = TEST_SESSION_PREFIX + "overwrite"
    big = {
        "session_id": session_id,
        "context_window": {"used_percentage": 42, "padding": "x" * 200},
    }
    small = {"session_id": session_id, "context_window": {"used_percentage": 7}}
    first = mod.write_gauge(big)
    first_size = first.stat().st_size
    second = mod.write_gauge(small)
    assert second == first
    # Exactly one file for this id...
    matches = sorted((tmp_path / ".quorum").glob(f"context-usage-{session_id}.json"))
    assert len(matches) == 1
    # ...holding exactly the SECOND record...
    assert json.loads(second.read_text(encoding="utf-8")) == small
    # ...and the byte length shrank, which append could not do.
    assert second.stat().st_size < first_size


def test_write_gauge_serialization_failure_does_not_truncate_the_previous_gauge(
    monkeypatch, tmp_path
):
    """`json.dumps` runs BEFORE `open(path, "w")`, so a bad record cannot truncate.

    The ordering inside `write_gauge` is load-bearing and commented as such in
    the helper. Reversed — open first, serialize inside the `with` — a record
    that fails to serialize would leave a zero-byte gauge behind. That file is
    still FRESH (the truncation bumps its mtime), so the reader would classify
    it as malformed and exit 2, turning a producer-side hiccup into a hard
    failure for every consumer of the session. Keeping the good reading in place
    means the next refresh simply overwrites it.

    A `set` is the trigger because `json.dumps` rejects it with `TypeError`
    while remaining a plausible thing to find in a carried-through
    `context_window` (the helper copies that object verbatim, whatever it holds).
    """
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = TEST_SESSION_PREFIX + "serialize-fail"
    good = {"session_id": session_id, "context_window": {"used_percentage": 42}}
    path = mod.write_gauge(good)
    before_bytes = path.read_bytes()
    assert before_bytes  # non-empty, so the survival assertion below has teeth

    doomed = {
        "session_id": session_id,
        "context_window": {"used_percentage": 42, "unserializable": {1, 2}},
    }
    with pytest.raises(TypeError):
        mod.write_gauge(doomed)

    # Byte-identical: not truncated, not partially rewritten, not deleted.
    assert path.exists()
    assert path.read_bytes() == before_bytes
    assert json.loads(path.read_text(encoding="utf-8")) == good


def test_write_gauge_two_sessions_are_independent(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    id_a = TEST_SESSION_PREFIX + "par-a"
    id_b = TEST_SESSION_PREFIX + "par-b"
    rec_a = {"session_id": id_a, "context_window": {"used_percentage": 11}}
    rec_b = {"session_id": id_b, "context_window": {"used_percentage": 88}}
    path_a = mod.write_gauge(rec_a)
    path_b = mod.write_gauge(rec_b)
    assert path_a != path_b
    assert json.loads(path_a.read_text(encoding="utf-8")) == rec_a
    assert json.loads(path_b.read_text(encoding="utf-8")) == rec_b
    assert len(sorted((tmp_path / ".quorum").glob("context-usage-*.json"))) == 2


# --- default_display -------------------------------------------------------

def test_default_display_prefers_workspace_current_dir():
    payload = {"workspace": {"current_dir": "/home/dev/code/quorum"}, "cwd": "/other/place"}
    assert mod.default_display(payload) == "quorum"


def test_default_display_falls_back_to_cwd():
    assert mod.default_display({"cwd": "/home/dev/code/other"}) == "other"
    assert mod.default_display({"workspace": {}, "cwd": "/a/b"}) == "b"
    assert mod.default_display({"workspace": {"current_dir": ""}, "cwd": "/a/b"}) == "b"


def test_default_display_empty_when_neither_present():
    assert mod.default_display({}) == ""
    assert mod.default_display({"workspace": {}}) == ""


@pytest.mark.parametrize(
    "workspace", ["not-a-dict", 7, None, ["a"]], ids=["str", "int", "none", "list"]
)
def test_default_display_does_not_raise_on_non_dict_workspace(workspace):
    assert mod.default_display({"workspace": workspace}) == ""
    assert mod.default_display({"workspace": workspace, "cwd": "/a/b"}) == "b"


def test_default_display_is_not_a_dict_payload():
    assert mod.default_display("not a dict") == ""
    assert mod.default_display(None) == ""


def test_default_display_never_contains_a_percentage():
    payload = {
        "workspace": {"current_dir": "/home/dev/code/quorum"},
        "context_window": {"used_percentage": 73},
    }
    display = mod.default_display(payload)
    assert "%" not in display
    assert "73" not in display


# --- run_wrapped failure tolerance -----------------------------------------

def test_run_wrapped_tolerates_timeout(monkeypatch):
    # Done in-process rather than at the CLI layer so the suite never waits on
    # the real WRAPPED_COMMAND_TIMEOUT_SECONDS (~10s) boundary.
    def boom(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="hang", timeout=1, output=b"partial")

    monkeypatch.setattr(mod.subprocess, "run", boom)
    out = mod.run_wrapped("hang", b"{}")
    assert isinstance(out, str)
    assert out == "partial"


def test_run_wrapped_tolerates_missing_command(monkeypatch):
    def boom(*args, **kwargs):
        raise FileNotFoundError("no such command")

    monkeypatch.setattr(mod.subprocess, "run", boom)
    out = mod.run_wrapped("nope", b"{}")
    assert isinstance(out, str)
    assert out == ""


# --- cmd_produce: blanking shapes still run the wrapped command -------------
#
# Path-independent invariant: under `--wrap-command`, a stdin shape that used to
# blank the status line (unparseable JSON, or empty/whitespace-only stdin) must
# still emit the wrapped command's display, replaying the ONCE-captured bytes.
# The implemented fix is path (b): `cmd_produce` returns 0 on every input shape
# (it warns to stderr on unparseable stdin, normalizes the payload to None, and
# always emits the display). These unit-layer tests call `cmd_produce` in-process
# with `run_wrapped` swapped for a recorder, so no real subprocess is spawned and
# the byte-exact stdin handed to the wrapped command can be asserted directly.
#
# `mod.sys` IS the shared stdlib module object, so the stdin patch goes through
# `monkeypatch` (auto-undone) and never a bare assignment.


class _StubBuffer:
    """A `sys.stdin.buffer` stand-in whose `read()` returns fixed bytes."""

    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return self._payload


class _StubStdin:
    """A `sys.stdin` stand-in exposing a `.buffer` with a `.read()`."""

    def __init__(self, payload):
        self.buffer = _StubBuffer(payload)


class _CountingBuffer:
    """A `.buffer` that yields the payload once, then `b""` forever after.

    A second drain of a real pipe comes back empty; this models that exactly so
    a test can prove `cmd_produce` reads stdin only once. If the helper ever
    re-read, the wrapped command would receive `b""` and silently blank.
    """

    def __init__(self, payload):
        self._payload = payload
        self.calls = 0

    def read(self):
        self.calls += 1
        if self.calls == 1:
            return self._payload
        return b""


class _CountingStdin:
    def __init__(self, payload):
        self.buffer = _CountingBuffer(payload)


def test_cmd_produce_unparseable_stdin_runs_the_wrapped_command_with_the_captured_bytes(
    monkeypatch, tmp_path, capsys
):
    _patch_tempdir(monkeypatch, tmp_path)
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(b"{not json"))
    recorded = []
    sentinel = "SENTINEL-DISPLAY"

    def recorder(command, stdin_bytes):
        recorded.append((command, stdin_bytes))
        return sentinel

    monkeypatch.setattr(mod, "run_wrapped", recorder)
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command="the-cmd"))
    # Byte-exact: the unparseable bytes are replayed to the wrapped command as-is.
    assert recorded == [("the-cmd", b"{not json")]
    assert capsys.readouterr().out == sentinel
    # Path (b): the wrap path always returns 0, never 2.
    assert rc == 0


def test_cmd_produce_empty_stdin_runs_the_wrapped_command(monkeypatch, tmp_path, capsys):
    _patch_tempdir(monkeypatch, tmp_path)
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(b""))
    recorded = []
    sentinel = "SENTINEL-DISPLAY"

    def recorder(command, stdin_bytes):
        recorded.append((command, stdin_bytes))
        return sentinel

    monkeypatch.setattr(mod, "run_wrapped", recorder)
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command="the-cmd"))
    assert recorded == [("the-cmd", b"")]
    assert capsys.readouterr().out == sentinel
    assert rc == 0


@pytest.mark.parametrize(
    "payload", [b"{not json", b""], ids=["unparseable", "empty"]
)
def test_cmd_produce_blanking_shapes_drain_stdin_exactly_once(
    monkeypatch, tmp_path, payload
):
    _patch_tempdir(monkeypatch, tmp_path)
    stdin = _CountingStdin(payload)
    monkeypatch.setattr(mod.sys, "stdin", stdin)
    recorded = []
    monkeypatch.setattr(
        mod, "run_wrapped", lambda command, stdin_bytes: recorded.append(stdin_bytes) or ""
    )
    mod.cmd_produce(types.SimpleNamespace(wrap_command="the-cmd"))
    # Exactly one drain: a second `read()` would come back empty and blank the
    # wrapped display. This is the regression `read_stdin_once` exists to prevent.
    assert stdin.buffer.calls == 1
    assert recorded == [payload]


@pytest.mark.parametrize(
    "payload", [b"{not json", b""], ids=["unparseable", "empty"]
)
def test_cmd_produce_blanking_shapes_without_wrap_do_not_run_a_wrapped_command(
    monkeypatch, tmp_path, capsys, payload
):
    _patch_tempdir(monkeypatch, tmp_path)
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(payload))
    recorded = []

    def recorder(command, stdin_bytes):
        recorded.append((command, stdin_bytes))
        return "SHOULD-NOT-APPEAR"

    monkeypatch.setattr(mod, "run_wrapped", recorder)
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command=None))
    # Contrast case: with no wrap command the wrapped path is never taken, and a
    # blanking shape yields an empty default display. Keeps tests 7-9 honest.
    assert recorded == []
    assert capsys.readouterr().out == ""
    assert rc == 0


@pytest.mark.parametrize(
    "payload", [b"{not json", b""], ids=["unparseable", "empty"]
)
@pytest.mark.parametrize("wrap", ["the-cmd", None], ids=["wrapped", "unwrapped"])
def test_cmd_produce_blanking_shapes_write_no_gauge(
    monkeypatch, tmp_path, payload, wrap
):
    _patch_tempdir(monkeypatch, tmp_path)
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(payload))
    monkeypatch.setattr(mod, "run_wrapped", lambda command, stdin_bytes: "")
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command=wrap))
    assert rc == 0
    # Gauge-write semantics are unchanged by the fix: a blanking shape carries no
    # usable session identity, so nothing is written and the dir is never created.
    assert not (tmp_path / ".quorum").exists()


# --- classify_reading: integer readings ------------------------------------

@pytest.mark.parametrize(
    "value,expected",
    [(37, "37"), (37.6, "38"), (0.4, "0"), (0, "0")],
    ids=["int", "rounds-up", "rounds-to-zero", "exact-zero"],
)
def test_classify_reading_integer_percentages(monkeypatch, tmp_path, value, expected):
    # A measured `used_percentage` that rounds to zero is the ONLY way `"0"` can
    # be produced. Absent, null, and stale readings must never reach this value.
    session_id = TEST_SESSION_PREFIX + "num"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": value}}),
    )
    assert mod.classify_reading(path, now=path.stat().st_mtime) == expected


@pytest.mark.parametrize(
    "window",
    [{"used_percentage": None}, {}, {"other": 1}],
    ids=["null", "empty-object", "no-such-key"],
)
def test_classify_reading_no_reading(monkeypatch, tmp_path, window):
    session_id = TEST_SESSION_PREFIX + "nor"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": window}),
    )
    assert mod.classify_reading(path, now=path.stat().st_mtime) == mod.READING_NO_READING


def test_classify_reading_absent_context_window_key_is_no_reading(monkeypatch, tmp_path):
    session_id = TEST_SESSION_PREFIX + "nokey"
    path = _seed(monkeypatch, tmp_path, session_id, json.dumps({"session_id": session_id}))
    assert mod.classify_reading(path, now=path.stat().st_mtime) == mod.READING_NO_READING


# --- classify_reading: staleness (the anti-collapse regression) -------------

def test_classify_reading_stale_wins_over_a_valid_low_integer(monkeypatch, tmp_path):
    """An aged gauge is `stale` even when it holds a perfectly valid number.

    This is the anti-collapse test. Usage only grows within a session, so a
    stale number biases LOW — i.e. toward "there is headroom", the banned
    direction. Returning the integer here, or returning `no-reading` (which
    routes a consumer to CONTINUE), both re-open that failure mode.
    """
    session_id = TEST_SESSION_PREFIX + "stale"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 3}}),
    )
    mtime = path.stat().st_mtime
    aged = mod.classify_reading(path, now=mtime + mod.FRESHNESS_WINDOW_SECONDS + 1)
    assert aged == mod.READING_STALE
    assert aged != "3"
    assert aged != mod.READING_NO_READING


def test_classify_reading_inside_freshness_window_returns_the_integer(monkeypatch, tmp_path):
    session_id = TEST_SESSION_PREFIX + "fresh"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 3}}),
    )
    mtime = path.stat().st_mtime
    # Deliberately one second INSIDE the window. The exact-equality boundary
    # (`now - mtime == window`) is not asserted anywhere: neither the SDD nor
    # Task 1 pins whether that instant is fresh or stale.
    assert mod.classify_reading(path, now=mtime + mod.FRESHNESS_WINDOW_SECONDS - 1) == "3"


def test_classify_reading_aged_via_os_utime_is_stale(monkeypatch, tmp_path):
    session_id = TEST_SESSION_PREFIX + "utime"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 5}}),
    )
    aged = time.time() - 300
    os.utime(path, (aged, aged))
    assert mod.classify_reading(path, now=time.time()) == mod.READING_STALE


# --- classify_reading: missing ---------------------------------------------

def test_classify_reading_missing_and_creates_nothing(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    path = mod.gauge_path("absent-session")
    result = mod.classify_reading(path, now=time.time())
    assert result == mod.READING_MISSING
    # An absent gauge is NEVER `0` and never empty — either would read to a
    # consumer as abundant headroom, the one banned direction. (The constants'
    # own distinctness is covered by `test_reading_values_are_four_way_distinct`;
    # these assertions pin what this call site actually returns.)
    assert result != "0"
    assert result != ""
    assert result != 0
    # Reading is strictly read-only: the gauge directory must not spring into
    # existence as a side effect of a `missing` classification.
    assert not (tmp_path / ".quorum").exists()


# --- classify_reading: four-way distinctness -------------------------------

def test_reading_values_are_four_way_distinct():
    """Collapsing any pair of these changes consumer routing silently."""
    values = [mod.READING_NO_READING, mod.READING_STALE, mod.READING_MISSING]
    assert len(set(values)) == 3
    for value in values:
        assert isinstance(value, str)
        assert value != "0"
        assert value != ""
        # And none of them is a decimal integer, so a consumer can tell a
        # measured percentage from a non-reading by shape alone.
        assert not value.isdigit()


# --- classify_reading: malformation ----------------------------------------

@pytest.mark.parametrize(
    "text",
    [
        "{not json",
        "[1, 2]",
        "42",
        '"a string"',
        "null",
        '{"session_id": "s", "context_window": null}',
        '{"session_id": "s", "context_window": 7}',
        '{"session_id": "s", "context_window": []}',
        '{"session_id": "s", "context_window": "37"}',
        '{"session_id": "s", "context_window": {"used_percentage": "37"}}',
        '{"session_id": "s", "context_window": {"used_percentage": []}}',
        '{"session_id": "s", "context_window": {"used_percentage": {"n": 1}}}',
        '{"session_id": "s", "context_window": {"used_percentage": NaN}}',
        '{"session_id": "s", "context_window": {"used_percentage": Infinity}}',
    ],
    ids=[
        "invalid-json",
        "array-top-level",
        "number-top-level",
        "string-top-level",
        "null-top-level",
        "window-null",
        "window-number",
        "window-array",
        "window-string",
        "percentage-string",
        "percentage-array",
        "percentage-object",
        "percentage-nan",
        "percentage-infinity",
    ],
)
def test_classify_reading_malformed(monkeypatch, tmp_path, text):
    path = _seed(monkeypatch, tmp_path, TEST_SESSION_PREFIX + "bad", text)
    with pytest.raises(mod.MalformedGauge):
        mod.classify_reading(path, now=path.stat().st_mtime)


def test_classify_reading_non_utf8_gauge_is_malformed(monkeypatch, tmp_path):
    """Undecodable bytes take the `UnicodeDecodeError` branch, not the JSON one.

    Every other malformation case in this module is valid UTF-8 that fails
    later, so this is the only test that reaches `read_text`'s decode guard.
    Without that guard the exception escapes `classify_reading` uncaught and the
    reader dies with a traceback instead of the contracted single stderr line —
    and `UnicodeDecodeError` subclasses `ValueError`, not `OSError`, so neither
    of the other two `except` clauses on that call would catch it.
    """
    _patch_tempdir(monkeypatch, tmp_path)
    mod.ensure_gauge_dir()
    session_id = TEST_SESSION_PREFIX + "non-utf8"
    path = mod.gauge_path(session_id)
    # `\xff` is not a legal UTF-8 lead byte in any position.
    path.write_bytes(b"\xff\xfe{")

    with pytest.raises(mod.MalformedGauge) as excinfo:
        mod.classify_reading(path, now=path.stat().st_mtime)
    # Assert the BRANCH, not just the exception type: a file that decoded and
    # then failed the JSON parse would also raise MalformedGauge here.
    assert "not valid UTF-8" in str(excinfo.value)


@pytest.mark.parametrize("value", ["true", "false"], ids=["true", "false"])
def test_classify_reading_boolean_percentage_is_malformed(monkeypatch, tmp_path, value):
    """`bool` is an `int` subclass — it MUST be rejected before the numeric check.

    Without the guard, `true` silently classifies as `1`: a near-empty context
    window, the most dangerous possible wrong answer. Its own named test
    because dropping the `isinstance(value, bool)` line is a realistic edit
    that every other numeric test would still pass.
    """
    session_id = TEST_SESSION_PREFIX + "bool"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        '{"session_id": "s", "context_window": {"used_percentage": ' + value + "}}",
    )
    with pytest.raises(mod.MalformedGauge):
        mod.classify_reading(path, now=path.stat().st_mtime)


# --- classify_reading: purity ----------------------------------------------

def test_classify_reading_is_silent_across_the_four_normal_cases(
    monkeypatch, tmp_path, capsys
):
    _patch_tempdir(monkeypatch, tmp_path)
    mod.ensure_gauge_dir()

    numeric = mod.gauge_path(TEST_SESSION_PREFIX + "silent-num")
    numeric.write_text(
        json.dumps({"session_id": "s", "context_window": {"used_percentage": 21}}),
        encoding="utf-8",
    )
    nulled = mod.gauge_path(TEST_SESSION_PREFIX + "silent-null")
    nulled.write_text(
        json.dumps({"session_id": "s", "context_window": {"used_percentage": None}}),
        encoding="utf-8",
    )
    absent = mod.gauge_path("silent-absent")

    results = [
        mod.classify_reading(numeric, now=numeric.stat().st_mtime),
        mod.classify_reading(nulled, now=nulled.stat().st_mtime),
        mod.classify_reading(
            numeric, now=numeric.stat().st_mtime + mod.FRESHNESS_WINDOW_SECONDS + 1
        ),
        mod.classify_reading(absent, now=time.time()),
    ]
    assert results == ["21", mod.READING_NO_READING, mod.READING_STALE, mod.READING_MISSING]
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


# ===========================================================================
# Layer 2 — CLI contract (subprocess)
# ===========================================================================

def _env_with_tempdir(tmp_path):
    """A copied environment whose temp directory is `tmp_path` on every platform.

    All three of TMPDIR / TEMP / TMP are set because `tempfile.gettempdir()`
    consults them differently across platforms. Each subprocess is fresh, so the
    in-process `tempfile.tempdir` cache is not a concern here.
    """
    env = dict(os.environ)
    env["TMPDIR"] = str(tmp_path)
    env["TEMP"] = str(tmp_path)
    env["TMP"] = str(tmp_path)
    return env


def _run(args, stdin=None, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
    )


def _stub(tmp_path, name, source):
    """Write a Python stub and return a shell-quotable command string for it.

    `--wrap-command` is run under `shell=True` (`/bin/sh` on POSIX, `cmd.exe` on
    Windows); double-quoted paths are accepted by both. Invoking a written stub
    through `sys.executable` is the cross-platform analogue of
    test_hive_commit.py's stub-`bees` technique — it avoids depending on a
    system `echo` existing or behaving identically across OSes.
    """
    stub = tmp_path / name
    stub.write_text(source, encoding="utf-8")
    return f'"{sys.executable}" "{stub}"'


def _cli_gauge_path(tmp_path, session_id):
    return tmp_path / ".quorum" / f"context-usage-{session_id}.json"


def _seed_cli_gauge(tmp_path, session_id, text):
    path = _cli_gauge_path(tmp_path, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _seed_cli_gauge_bytes(tmp_path, session_id, raw):
    """Seed a gauge with exact raw bytes — for content no encoder would produce."""
    path = _cli_gauge_path(tmp_path, session_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def _gauge_files(tmp_path):
    directory = tmp_path / ".quorum"
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.glob("context-usage-*.json"))


# --- produce: writing the gauge --------------------------------------------

def test_cli_produce_writes_gauge(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-write"
    window = {"used_percentage": 44, "tokens": 91234, "nested": {"a": [1, 2]}}
    payload = {
        "session_id": session_id,
        "context_window": window,
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    res = _run(["produce"], stdin=json.dumps(payload), env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    path = _cli_gauge_path(tmp_path, session_id)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == {
        "session_id": session_id,
        "context_window": window,
    }


def test_cli_produce_twice_same_id_overwrites(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-overwrite"
    big = {
        "session_id": session_id,
        "context_window": {"used_percentage": 44, "padding": "x" * 300},
    }
    small = {"session_id": session_id, "context_window": {"used_percentage": 9}}
    env = _env_with_tempdir(tmp_path)
    first = _run(["produce"], stdin=json.dumps(big), env=env)
    assert first.returncode == 0, first.stderr
    first_size = _cli_gauge_path(tmp_path, session_id).stat().st_size
    second = _run(["produce"], stdin=json.dumps(small), env=env)
    assert second.returncode == 0, second.stderr

    assert _gauge_files(tmp_path) == [f"context-usage-{session_id}.json"]
    path = _cli_gauge_path(tmp_path, session_id)
    assert json.loads(path.read_text(encoding="utf-8")) == small
    assert path.stat().st_size < first_size


def test_cli_produce_two_sessions_are_isolated(tmp_path):
    id_a = TEST_SESSION_PREFIX + "cli-par-a"
    id_b = TEST_SESSION_PREFIX + "cli-par-b"
    env = _env_with_tempdir(tmp_path)
    payload_a = {"session_id": id_a, "context_window": {"used_percentage": 11}}
    payload_b = {"session_id": id_b, "context_window": {"used_percentage": 88}}
    assert _run(["produce"], stdin=json.dumps(payload_a), env=env).returncode == 0
    assert _run(["produce"], stdin=json.dumps(payload_b), env=env).returncode == 0

    assert _gauge_files(tmp_path) == sorted(
        [f"context-usage-{id_a}.json", f"context-usage-{id_b}.json"]
    )
    assert json.loads(
        _cli_gauge_path(tmp_path, id_a).read_text(encoding="utf-8")
    ) == payload_a
    assert json.loads(
        _cli_gauge_path(tmp_path, id_b).read_text(encoding="utf-8")
    ) == payload_b


# --- produce: no-op session identities -------------------------------------

@pytest.mark.parametrize(
    "session_field",
    [{}, {"session_id": ""}, {"session_id": None}, {"session_id": 123},
     {"session_id": "../escape"}, {"session_id": "a/b"}],
    ids=["absent", "empty", "null", "non-string", "dotdot", "separator"],
)
def test_cli_produce_unusable_session_id_writes_nothing_but_still_displays(
    tmp_path, session_field
):
    payload = dict(session_field)
    payload["context_window"] = {"used_percentage": 61}
    payload["workspace"] = {"current_dir": "/home/dev/code/quorum"}
    res = _run(["produce"], stdin=json.dumps(payload), env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    # No gauge file at all — not even one under a sanitized name.
    assert _gauge_files(tmp_path) == []
    # ...and the operator's status line does NOT go blank just because this
    # refresh carried no usable session identity.
    assert res.stdout == "quorum"


# --- produce: stdin handling -----------------------------------------------

def test_cli_produce_empty_stdin_without_wrap_is_a_silent_noop(tmp_path):
    """Empty stdin is dispositioned two ways, and this pins only the unwrapped
    arm: with no `--wrap-command` there is nothing to display, so `produce`
    stays fully silent (exit 0, empty stdout, empty stderr, no gauge file). The
    wrapped arm — empty stdin still emits the wrapped command's display rather
    than blanking — is pinned by the sibling Subtask's wrapped-command test.
    """
    res = _run(["produce"], stdin="", env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0
    assert res.stdout == ""
    assert res.stderr == ""
    assert _gauge_files(tmp_path) == []


def test_cli_produce_unparseable_stdin_without_wrap_exits_0_and_warns(tmp_path):
    res = _run(["produce"], stdin="{not json", env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0
    assert res.stdout == ""
    assert len(res.stderr.strip().splitlines()) == 1
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


# --- produce: the display --------------------------------------------------

def test_cli_produce_default_display_is_the_workspace_basename(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-display"
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 5},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    res = _run(["produce"], stdin=json.dumps(payload), env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    # `sys.stdout.write`, not `print`: no trailing newline is added.
    assert res.stdout == "quorum"


def test_cli_produce_wrap_command_passthrough_is_byte_exact(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-wrap"
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    payload = {"session_id": session_id, "context_window": {"used_percentage": 33}}
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=json.dumps(payload),
        env=_env_with_tempdir(tmp_path),
    )
    assert res.returncode == 0, res.stderr
    # Byte for byte: the passthrough neither adds nor strips a newline.
    assert res.stdout == marker
    # ...and the gauge was still written.
    assert json.loads(
        _cli_gauge_path(tmp_path, session_id).read_text(encoding="utf-8")
    ) == payload


def test_cli_produce_wrap_command_receives_the_captured_stdin(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-stdin"
    command = _stub(
        tmp_path,
        "echo_stdin_stub.py",
        "import sys\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n",
    )
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 12},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=json.dumps(payload),
        env=_env_with_tempdir(tmp_path),
    )
    assert res.returncode == 0, res.stderr
    # The stub saw the full payload, which proves the once-captured stdin was
    # REPLAYED rather than re-read (a second read of the pipe returns nothing
    # and would silently blank the operator's wrapped status line).
    assert json.loads(res.stdout) == payload


@pytest.mark.parametrize("kind", ["nonzero", "missing"])
def test_cli_produce_broken_wrap_command_still_writes_the_gauge(tmp_path, kind):
    session_id = TEST_SESSION_PREFIX + "cli-broken-" + kind
    if kind == "nonzero":
        command = _stub(tmp_path, "fail_stub.py", "import sys\nsys.exit(3)\n")
    else:
        command = '"' + str(tmp_path / "definitely-not-a-real-command") + '"'
    payload = {"session_id": session_id, "context_window": {"used_percentage": 55}}
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=json.dumps(payload),
        env=_env_with_tempdir(tmp_path),
    )
    # A broken status line must never cost the guard its reading.
    assert res.returncode == 0
    assert json.loads(
        _cli_gauge_path(tmp_path, session_id).read_text(encoding="utf-8")
    ) == payload


# --- produce: blanking shapes under --wrap-command --------------------------
#
# Path-independent invariant: under `--wrap-command`, both former blanking
# shapes (unparseable JSON stdin, and empty/whitespace-only stdin) still emit the
# wrapped command's display byte-for-byte. The implemented fix is path (b) —
# `produce` returns exit code 0 on every input shape and never blanks of its own
# accord — so each test below asserts `returncode == 0` exactly (the superseded
# path (a) would have exited 2). Nothing here writes a gauge, so no session-id
# prefix is needed.


def test_cli_produce_unparseable_stdin_with_wrap_emits_the_wrapped_display(tmp_path):
    # The direct inverse of the shipped defect: unparseable stdin must NOT blank
    # the operator's wrapped status line.
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    res = _run(
        ["produce", "--wrap-command", command],
        stdin="{not json",
        env=_env_with_tempdir(tmp_path),
    )
    # Byte for byte: the wrapped command ran and its output passed through.
    assert res.stdout == marker
    # Path (b): exit 0 (the superseded path (a) value 2 must never be accepted).
    assert res.returncode == 0
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


def test_cli_produce_unparseable_stdin_with_wrap_replays_the_captured_bytes(tmp_path):
    command = _stub(
        tmp_path,
        "echo_stdin_stub.py",
        "import sys\nsys.stdout.buffer.write(sys.stdin.buffer.read())\n",
    )
    res = _run(
        ["produce", "--wrap-command", command],
        stdin="{not json",
        env=_env_with_tempdir(tmp_path),
    )
    # The failure path REPLAYS the once-captured bytes rather than re-reading a
    # drained pipe: the stub saw the exact non-JSON bytes fed in.
    assert res.stdout == "{not json"
    assert res.returncode == 0
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


@pytest.mark.parametrize(
    "raw", ["[1, 2]", '"a string"', "42", "null", "true"],
    ids=["array", "string", "number", "null", "bool"],
)
def test_cli_produce_non_object_json_with_wrap_emits_the_wrapped_display(tmp_path, raw):
    # Non-object top-level JSON takes the SAME `ValueError` branch as `{not json`
    # (parse_payload raises "top-level JSON value is not an object"), so it must
    # get the identical disposition — else a fix that special-cases only
    # JSONDecodeError would leave half the blanking shapes broken.
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=raw,
        env=_env_with_tempdir(tmp_path),
    )
    assert res.stdout == marker
    assert res.returncode == 0
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


def test_cli_produce_empty_stdin_with_wrap_emits_the_wrapped_display(tmp_path):
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    res = _run(
        ["produce", "--wrap-command", command],
        stdin="",
        env=_env_with_tempdir(tmp_path),
    )
    assert res.stdout == marker
    # Empty stdin is a no-op refresh under both paths, so exit 0 either way.
    assert res.returncode == 0
    # No warn is emitted for empty stdin (it is not a malformed payload).
    assert res.stderr == ""
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


@pytest.mark.parametrize(
    "raw", ["   ", "\n", " \t\r\n "], ids=["spaces", "newline", "mixed"]
)
def test_cli_produce_whitespace_only_stdin_with_wrap_emits_the_wrapped_display(tmp_path, raw):
    # parse_payload classifies whitespace-only input as empty (None), so these
    # follow the empty-stdin case, NOT the unparseable one — no warn, exit 0.
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=raw,
        env=_env_with_tempdir(tmp_path),
    )
    assert res.stdout == marker
    assert res.returncode == 0
    assert res.stderr == ""
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()


@pytest.mark.parametrize("kind", ["nonzero", "missing"])
@pytest.mark.parametrize("stdin", ["{not json", ""], ids=["unparseable", "empty"])
def test_cli_produce_broken_wrap_command_on_a_blanking_shape_does_not_crash(
    tmp_path, kind, stdin
):
    # A broken operator command on a blanking shape must not route the failure
    # path around run_wrapped's tolerance and turn into a producer crash.
    if kind == "nonzero":
        command = _stub(tmp_path, "fail_stub.py", "import sys\nsys.exit(3)\n")
    else:
        command = '"' + str(tmp_path / "definitely-not-a-real-command") + '"'
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=stdin,
        env=_env_with_tempdir(tmp_path),
    )
    # The wrapped command produced nothing; the producer passes that blank
    # through rather than crashing.
    assert res.stdout == ""
    assert res.returncode == 0
    assert "Traceback" not in res.stderr


# --- read: the four classifications ----------------------------------------

def test_cli_read_fresh_integer(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-read-num"
    _seed_cli_gauge(
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 37}}),
    )
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert res.stdout == "37\n"


def test_cli_read_no_reading(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-read-null"
    _seed_cli_gauge(
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": None}}),
    )
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert res.stdout == "no-reading\n"


def test_cli_read_stale(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-read-stale"
    path = _seed_cli_gauge(
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 4}}),
    )
    aged = time.time() - 300
    os.utime(path, (aged, aged))
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    # Aged, yet holding a valid low integer: `stale`, never the number.
    assert res.stdout == "stale\n"


def test_cli_read_creates_nothing_on_a_clean_temp_root(tmp_path):
    """Also the `missing` classification's CLI pin — same setup, same assertions.

    A separate `test_cli_read_missing` used to sit beside this one asserting the
    identical returncode and stdout against the identical setup; it was strictly
    subsumed and has been removed rather than left as a duplicate that would
    have to be kept in step with this one.
    """
    session_id = TEST_SESSION_PREFIX + "cli-read-clean"
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert res.stdout == "missing\n"
    # ...and reading a session with no gauge brings nothing into existence.
    assert not (tmp_path / ".quorum").exists()


# --- read: error paths -----------------------------------------------------

def test_cli_read_malformed_gauge_exits_2(tmp_path):
    session_id = TEST_SESSION_PREFIX + "cli-read-bad"
    _seed_cli_gauge(tmp_path, session_id, "{not json")
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2
    assert res.stdout == ""
    assert len(res.stderr.strip().splitlines()) == 1


def test_cli_read_non_utf8_gauge_exits_2(tmp_path):
    """Undecodable bytes reach the caller as the contracted exit-2 + one line.

    The unit-layer twin pins the `MalformedGauge` branch; this pins that the CLI
    turns it into the documented shape rather than a traceback on stderr.
    """
    session_id = TEST_SESSION_PREFIX + "cli-read-non-utf8"
    _seed_cli_gauge_bytes(tmp_path, session_id, b"\xff\xfe{")
    res = _run(["read", "--session-id", session_id], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2
    assert res.stdout == ""
    assert len(res.stderr.strip().splitlines()) == 1
    # Not one of the four reading values dressed up as an error line.
    for value in ("no-reading", "stale", "missing"):
        assert value not in res.stdout


@pytest.mark.parametrize(
    "bad", ["../escape", "", "a/b", "a b"], ids=["dotdot", "empty", "separator", "space"]
)
def test_cli_read_invalid_session_id_exits_2(tmp_path, bad):
    res = _run(["read", "--session-id", bad], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2
    # An invalid identifier is a caller bug, NOT one of the four reading states:
    # a consumer would read `missing` as "no producer configured" and carry on.
    for value in ("no-reading", "stale", "missing"):
        assert value not in res.stdout
    assert res.stdout.strip() == ""


# --- argparse contract -----------------------------------------------------

def test_cli_help_exits_0_and_names_both_subcommands(tmp_path):
    res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert "produce" in res.stdout
    assert "read" in res.stdout


def test_cli_no_subcommand_exits_2(tmp_path):
    res = _run([], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


def test_cli_unknown_subcommand_exits_2(tmp_path):
    res = _run(["bogus"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


def test_cli_read_requires_session_id(tmp_path):
    res = _run(["read"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2
