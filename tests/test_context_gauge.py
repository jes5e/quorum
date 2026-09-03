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

No test reads or writes the operator's real Claude Code user settings either.
This is the first module to touch that file at all, so a second autouse fixture,
`no_real_user_settings_writes`, snapshots the stat metadata of the real
`settings.json`, the real config directory's existence, and the reserved
self-check gauge, and asserts all three unchanged on teardown. Every test that
reaches a settings or marker path routes through an isolation helper that
redirects `HOME` and `USERPROFILE` (so `Path.home()` resolves into a `tmp_path`
sandbox on POSIX and Windows alike) and either sets or unsets `CLAUDE_CONFIG_DIR`
— always via `monkeypatch` (unit layer) or a copied environment (CLI layer),
never a bare `os.environ` assignment. Popping an inherited `CLAUDE_CONFIG_DIR`
is load-bearing: a developer or CI runner who exports it would otherwise point
every default-derivation test at their real configuration directory.
"""

import collections
import json
import os
import shlex
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

# Real user-settings paths, captured at IMPORT time before any test can
# monkeypatch HOME / USERPROFILE / CLAUDE_CONFIG_DIR. Spelled with literal
# `".claude"` / `"settings.json"` / `"quo-setup-self-check"` rather than read
# from `mod`, for the same reason REAL_GAUGE_DIR is: a test that mutates one of
# the helper's own constants must not be able to relocate the path the safety
# fixture watches.
_config_override = os.environ.get("CLAUDE_CONFIG_DIR")
REAL_CONFIG_DIR = Path(_config_override) if _config_override else Path.home() / ".claude"
REAL_USER_SETTINGS = REAL_CONFIG_DIR / "settings.json"
# The self-check session id is NOT under TEST_SESSION_PREFIX, so
# `no_real_tempdir_writes` does not watch it; the sibling subtask spawns a
# subprocess that writes a throwaway gauge under exactly this name, and a lost
# `env=` override would land it in the real temp dir. Spelled literally and
# pinned separately below.
REAL_SELF_CHECK_GAUGE = REAL_GAUGE_DIR / "context-usage-quo-setup-self-check.json"


def _stat_key(path):
    """Return `None` if `path` is absent, else `(st_size, st_mtime_ns)`.

    Stat-keyed rather than a mere existence check for the same reason
    `_real_prefixed_entries` is: an overwrite of an existing settings file must
    fire the delta even though the name is unchanged. Same coarse-granularity
    scope note applies — a same-size overwrite that lands in the same filesystem
    timestamp tick as the setup snapshot leaves both key components unchanged and
    would not show; that narrows detection in a corner rather than disarming it.
    Reads only stat metadata — never the file's contents.
    """
    try:
        st = path.stat()
    except OSError:
        return None
    return (st.st_size, st.st_mtime_ns)


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


@pytest.fixture(autouse=True)
def no_real_user_settings_writes():
    """Fail any test that reads-into-existence or writes the real user settings.

    A delta assertion over stat metadata, not an emptiness assertion: it must
    fire on an OVERWRITE of an already-present settings file, not only on a
    brand-new one, so it keys on `_stat_key`. Three things are snapshotted and
    asserted unchanged: the real `settings.json`'s stat key, the real config
    directory's existence, and the reserved self-check gauge's stat key. A test
    that forgets a HOME / USERPROFILE / CLAUDE_CONFIG_DIR override, or a
    subprocess self-check that loses its `env=` redirect, moves one of these and
    is caught here.

    This fixture reads stat metadata ONLY — it never opens the operator's
    settings file to read its contents, never creates anything, and never
    deletes anything (CLAUDE.md `## Scratch-file convention`).

    One accepted false positive: a genuine `/quo-setup` install running
    concurrently on this same machine would legitimately (re)write
    `REAL_SELF_CHECK_GAUGE` and fire this delta. That collision is judged
    acceptable — the test run and a live install racing on one machine is rare,
    and a spurious failure is safer than a silent real-settings write.
    """
    before = (
        _stat_key(REAL_USER_SETTINGS),
        REAL_CONFIG_DIR.exists(),
        _stat_key(REAL_SELF_CHECK_GAUGE),
    )
    yield
    assert _stat_key(REAL_USER_SETTINGS) == before[0], (
        f"test touched the real user settings file {REAL_USER_SETTINGS}"
    )
    assert REAL_CONFIG_DIR.exists() == before[1], (
        f"test created or removed the real config directory {REAL_CONFIG_DIR}"
    )
    assert _stat_key(REAL_SELF_CHECK_GAUGE) == before[2], (
        f"test touched the reserved self-check gauge {REAL_SELF_CHECK_GAUGE}"
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


def _isolate_settings_env(monkeypatch, tmp_path, config_dir=None):
    """Sandbox every home/config lookup a unit-layer settings test can make.

    Returns the fake home directory it points HOME/USERPROFILE at (created under
    `tmp_path`, not created on disk — callers that need the dir make it).

    - Redirects the tempdir via `_patch_tempdir` (the in-process module-object
      patch, because `tempfile.gettempdir()` caches its result in-process).
    - Sets BOTH `HOME` and `USERPROFILE` to `tmp_path/home`: `Path.home()` is
      `os.path.expanduser("~")`, which reads `HOME` on POSIX and `USERPROFILE`
      on Windows, so both are required for the helper's per-OS-branch-free
      `Path.home()` claim to be exercised on either platform. `HOMEDRIVE` /
      `HOMEPATH` are deleted so the Windows fallback chain cannot reach a real
      profile.
    - Also redirects `TMPDIR`/`TEMP`/`TMP` so any child process an in-process
      call might spawn inherits the sandbox (the `mod.tempfile` patch does not
      cross a process boundary).
    - `config_dir=None` unsets `CLAUDE_CONFIG_DIR` (default `~/.claude`
      derivation); otherwise sets it to the given path.

    Every mutation goes through `monkeypatch` (auto-undone), never a bare
    `os.environ[...] = ...`.
    """
    _patch_tempdir(monkeypatch, tmp_path)
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.delenv("HOMEDRIVE", raising=False)
    monkeypatch.delenv("HOMEPATH", raising=False)
    monkeypatch.setenv("TMPDIR", str(tmp_path))
    monkeypatch.setenv("TEMP", str(tmp_path))
    monkeypatch.setenv("TMP", str(tmp_path))
    if config_dir is None:
        monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
    else:
        monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config_dir))
    return home


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
    assert mod.FRESHNESS_WINDOW_SECONDS == 1200
    # Turn-scale window (>= 15 min): an accidental revert to the old 120-second
    # value fails loudly here, not just at the exact-equality pin above.
    assert mod.FRESHNESS_WINDOW_SECONDS >= 900


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


# --- cmd_produce: an unwritable gauge directory must not blank the display ---
#
# Same invariant as the blanking shapes above, one failure class further out:
# the payload parses and carries a usable session identity, but the gauge write
# itself raises `OSError`. `produce` must warn once, skip the write, and still
# reach the display tail with exit 0 — the harness blanks the status line on a
# non-zero exit OR on empty output, so a propagating `OSError` blanks the
# operator's line on EVERY refresh for as long as the condition lasts. The
# trigger is ordinary: a world-writable temp directory whose `.quorum` was
# created by a different user.
#
# The fixture below parametrizes over ALL THREE filesystem failure points rather
# than just the convenient one — see its docstring for why no single arm is
# enough, and in particular why the `open` failure needs a uid-independent arm.


#: What `unwritable_gauge_dir` hands its consumers. `session_id` travels WITH the
#: arm because one arm's sabotage is keyed to that exact gauge filename; see the
#: fixture docstring.
UnwritableGauge = collections.namedtuple("UnwritableGauge", "arm session_id")


@pytest.fixture(params=["blocked", "readonly", "gauge-path-is-dir"])
def unwritable_gauge_dir(request, tmp_path):
    """Make this session's gauge write fail three structurally different ways.

    All three arms live under `tmp_path`, so the autouse `no_real_tempdir_writes`
    fixture is satisfied and nothing touches the real temp directory. Returns an
    `UnwritableGauge(arm, session_id)`.

    Consumers MUST take the session id from here rather than minting their own.
    The `gauge-path-is-dir` arm sabotages one specific gauge FILENAME, so a
    consumer that used a different identifier would write successfully and the
    arm would pass WITHOUT TESTING — the same silent-green failure the
    `readonly` probe below exists to prevent.

    - `blocked` — a regular FILE sits where the gauge directory belongs, so
      `ensure_gauge_dir`'s `mkdir` raises `FileExistsError` (an `OSError`
      subclass). This arm is uid- and platform-independent, and it is the ONLY
      one that exercises the `mkdir` failure point; the `open` never runs.
      That platform-independence covers the PRODUCE side only. A reader that
      later `stat`s a path through this same non-directory component fails with
      a class this suite has verified on POSIX (`NotADirectoryError`) and has
      NOT verified on Windows, where a file in a path component is reported as
      `ERROR_PATH_NOT_FOUND` in at least some cases — which Python surfaces as
      `FileNotFoundError`, i.e. `missing` rather than malformation. Consumers
      that assert the reader-side class therefore skip on Windows and say so;
      consumers that only assert the produce-side behavior run everywhere.
    - `readonly` — a real directory at mode `0o555`, so the `mkdir` succeeds
      (`exist_ok=True`) and the `open(path, "w")` inside `write_gauge` raises
      `PermissionError`. This is the shipped-defect shape from the field report,
      reproduced with the field's own mechanism (permissions).
    - `gauge-path-is-dir` — the gauge DIRECTORY is left normal and writable, and
      a directory is pre-created at the gauge FILE's own path, so the `mkdir`
      succeeds and `open(path, "w")` raises `IsADirectoryError` (`[Errno 21]`,
      an `OSError`). This reaches the same `open` failure point as `readonly`
      but through structure rather than permissions, so it holds under ANY uid
      and on Windows. Without it, a root CI container — where `readonly` skips
      and `blocked` never gets past the `mkdir` — would run this whole suite with
      ZERO coverage of the shipped defect's actual failure point.

    Keeping all three matters because a single arm would leave part of the fix
    unexercised: `write_gauge` fails at distinct points and the production `try`
    has to span them all.

    The `readonly` arm is guarded by an actual writability PROBE rather than by
    an assumption that the mode bits bite. Root ignores mode bits entirely, and
    Windows does not honor `chmod` on directories, so on either an unprobed arm
    would pass WITHOUT TESTING — the write would succeed, the `except` branch
    would never run, and a regression would sail through green. The probe skips
    instead, which is loud. (It subsumes the narrower `os.geteuid() == 0` check:
    it is one condition covering root, Windows, and any ACL arrangement that
    overrides the mode.) The directory is restored to `0o755` at teardown so
    pytest's `tmp_path` reaper is never left with a directory it cannot clear.
    That skip is now survivable rather than a coverage hole, because
    `gauge-path-is-dir` covers the same failure point unconditionally.
    """
    # The arm name rides in the session id so a failure report names the arm.
    session_id = TEST_SESSION_PREFIX + "unwritable-" + request.param
    result = UnwritableGauge(request.param, session_id)
    target = tmp_path / ".quorum"

    if request.param == "blocked":
        target.write_text("a regular file, not a directory", encoding="utf-8")
        return result

    if request.param == "gauge-path-is-dir":
        target.mkdir()
        # `_cli_gauge_path` is the suite's single spelling of the gauge filename
        # template; reusing it here keeps this sabotage in step with what the
        # helper actually derives from `session_id`.
        _cli_gauge_path(tmp_path, session_id).mkdir()
        return result

    target.mkdir()
    target.chmod(0o555)
    request.addfinalizer(lambda: target.chmod(0o755))
    probe = target / "writability-probe"
    try:
        probe.touch()
    except OSError:
        return result
    probe.unlink()
    pytest.skip(
        "this environment can still write into a 0o555 directory (root, Windows, "
        "or an overriding ACL), so the read-only arm would pass without testing"
    )


def test_cmd_produce_unwritable_gauge_dir_still_emits_the_wrapped_display(
    monkeypatch, tmp_path, capsys, unwritable_gauge_dir
):
    """REGRESSION GUARD. Pre-fix this raised out of `cmd_produce`."""
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = unwritable_gauge_dir.session_id
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 44},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    raw = json.dumps(payload).encode("utf-8")
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(raw))
    recorded = []
    sentinel = "SENTINEL-DISPLAY"

    def recorder(command, stdin_bytes):
        recorded.append((command, stdin_bytes))
        return sentinel

    monkeypatch.setattr(mod, "run_wrapped", recorder)
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command="the-cmd"))
    out = capsys.readouterr()
    # The write failed, but the wrapped command still ran with the byte-exact
    # captured stdin and its display still reached stdout.
    assert recorded == [("the-cmd", raw)]
    assert out.out == sentinel
    assert rc == 0
    # The failure is carried on stderr, in exactly one line — not in the exit
    # code, which the harness would read as "blank the line". Assert WHAT that
    # line says, not merely that there is one: a count-only assertion would be
    # satisfied by the unrelated payload-parse diagnostic. All three arms fail
    # inside `write_gauge`, so this prefix holds arm-independently while the
    # `[Errno ...]` tail legitimately differs.
    err_lines = out.err.strip().splitlines()
    assert len(err_lines) == 1
    assert "cannot publish the context gauge" in err_lines[0]
    # Nothing was published: the reader will report `missing`, the documented
    # downstream signal.
    assert _gauge_files(tmp_path) == []


def test_cmd_produce_unwritable_gauge_dir_without_wrap_emits_the_default_display(
    monkeypatch, tmp_path, capsys, unwritable_gauge_dir
):
    """REGRESSION GUARD. The unwrapped arm blanked identically pre-fix."""
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = unwritable_gauge_dir.session_id
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 44},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    monkeypatch.setattr(mod.sys, "stdin", _StubStdin(json.dumps(payload).encode("utf-8")))
    recorded = []

    def recorder(command, stdin_bytes):
        recorded.append((command, stdin_bytes))
        return "SHOULD-NOT-APPEAR"

    monkeypatch.setattr(mod, "run_wrapped", recorder)
    rc = mod.cmd_produce(types.SimpleNamespace(wrap_command=None))
    out = capsys.readouterr()
    assert recorded == []
    # Unlike the blanking shapes, this payload PARSED — so the default display is
    # the workspace basename, non-empty. A write failure costs the reading, never
    # the display.
    assert out.out == "quorum"
    assert rc == 0
    err_lines = out.err.strip().splitlines()
    assert len(err_lines) == 1
    assert "cannot publish the context gauge" in err_lines[0]
    assert _gauge_files(tmp_path) == []


def test_write_gauge_still_raises_on_an_unwritable_gauge_dir(
    monkeypatch, tmp_path, unwritable_gauge_dir
):
    """The catch belongs at the call site, NOT inside `write_gauge`.

    `write_gauge` is a pure function: it raises, and its caller disposes — the
    same layering `classify_reading` and `cmd_read` use, and the one the helper's
    decision record states outright ("the pure function raises and the CLI layer
    disposes"). The never-blank guarantee is a property of the process's exit
    code and stdout, which only `cmd_produce` owns, so `cmd_produce` is where the
    `try` belongs.

    Today `cmd_produce` is `write_gauge`'s ONLY production caller, so moving the
    `try` inward would not break anything visible right now — which is exactly
    why this pin is worth having. A second caller (an installer verification, a
    future `publish` subcommand) that needs to know the write failed would find
    the failure already swallowed one layer down and silently report success it
    never achieved. This test fails on that "simplification" while the defect is
    still cheap to undo.
    """
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = unwritable_gauge_dir.session_id
    record = {"session_id": session_id, "context_window": {"used_percentage": 44}}
    with pytest.raises(OSError):
        mod.write_gauge(record)


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


def test_classify_reading_past_old_window_but_inside_new_window_returns_the_integer(
    monkeypatch, tmp_path
):
    """A reading aged well past the OLD 120s window still reads as the integer.

    240s is a literal chosen to sit ABOVE the retired 120-second window and
    comfortably BELOW the new turn-scale window (15-20 min). Classifying this as
    the integer — not `stale` — proves the window actually grew past 120, which a
    symbolic `mod.FRESHNESS_WINDOW_SECONDS - N` offset could not: that would pass
    for any window value, including the old one, and so would not pin the
    enlargement. Load-bearing that the literal stays strictly between 120 and the
    new window.
    """
    session_id = TEST_SESSION_PREFIX + "grew"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 3}}),
    )
    mtime = path.stat().st_mtime
    assert mod.classify_reading(path, now=mtime + 240) == "3"


def test_classify_reading_aged_via_os_utime_is_stale(monkeypatch, tmp_path):
    session_id = TEST_SESSION_PREFIX + "utime"
    path = _seed(
        monkeypatch,
        tmp_path,
        session_id,
        json.dumps({"session_id": session_id, "context_window": {"used_percentage": 5}}),
    )
    # Reference the helper constant so this ages the gauge past the CURRENT
    # window (with slack), not a hardcoded 300s that would sit inside it.
    aged = time.time() - (mod.FRESHNESS_WINDOW_SECONDS + 60)
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


@pytest.mark.skipif(
    os.name == "nt",
    reason=(
        "POSIX-only sabotage: a file at a path COMPONENT raises NotADirectoryError "
        "on POSIX, but Windows may report ERROR_PATH_NOT_FOUND -> FileNotFoundError, "
        "which classify_reading routes to `missing`, not MalformedGauge. Unverified "
        "on Windows. To lift this skip, confirm what Path.stat() raises there for a "
        "path whose parent is a regular file; if it is FileNotFoundError, this branch "
        "needs a different Windows-side un-stat-able trigger, not a weaker assertion."
    ),
)
def test_classify_reading_un_stat_able_gauge_is_malformed(monkeypatch, tmp_path):
    """A gauge whose `stat` raises is malformation, NOT `missing`.

    `classify_reading`'s first step catches `FileNotFoundError` as `missing` and
    routes every OTHER `OSError` to `MalformedGauge`. That split is the whole
    safety argument for the step: an un-stat-able path is not evidence of
    absence, and reporting `missing` would tell a consumer "no producer is
    configured here, carry on" when the truth is "the path cannot be examined".
    Widening the `except FileNotFoundError` to a bare `except OSError` is a
    realistic simplification that no other unit test would catch.

    The un-stat-able condition is built structurally rather than with
    permissions, so it holds under any uid: a regular FILE sits where the
    `.quorum` directory belongs, making `.quorum` a non-directory component of
    the gauge path, so `stat` raises `NotADirectoryError`. That stat-failure
    class is POSIX-verified and Windows-UNVERIFIED — hence the `skipif` above
    rather than a claim of platform independence. This is the unit twin of the
    CLI-layer `blocked` arm in
    `test_cli_a_failed_publish_leaves_the_reader_with_no_usable_reading` — the
    module's unit-pins-the-branch / CLI-pins-the-shape pattern — and that arm's
    reader-side assertion carries the same skip for the same reason.
    """
    _patch_tempdir(monkeypatch, tmp_path)
    session_id = TEST_SESSION_PREFIX + "un-stat-able"
    (tmp_path / ".quorum").write_text("a regular file, not a directory", encoding="utf-8")
    path = mod.gauge_path(session_id)

    with pytest.raises(mod.MalformedGauge) as excinfo:
        mod.classify_reading(path, now=time.time())
    # Assert the BRANCH, not just the exception type: several later steps raise
    # the same exception, and only this one can fire before the file is read.
    assert "cannot stat gauge file" in str(excinfo.value)


def test_classify_reading_unreadable_gauge_is_malformed(monkeypatch, tmp_path):
    """Unit pin for the branch the `gauge-path-is-dir` CLI arm exercises end-to-end.

    A DIRECTORY at the gauge file's own path stats fine (so the reading is
    fresh, not `missing`) and then fails at `read_text` with
    `IsADirectoryError` — an `OSError` that is not `FileNotFoundError`, so it
    must surface as malformation rather than `missing`. Built structurally so
    it holds under any uid.
    """
    _patch_tempdir(monkeypatch, tmp_path)
    mod.ensure_gauge_dir()
    session_id = TEST_SESSION_PREFIX + "unreadable"
    path = mod.gauge_path(session_id)
    path.mkdir()

    with pytest.raises(mod.MalformedGauge) as excinfo:
        mod.classify_reading(path, now=path.stat().st_mtime)
    # Assert the BRANCH, not just the exception type: the stat branch above and
    # the parse branches below raise the same exception with other messages.
    assert "gauge file is unreadable" in str(excinfo.value)


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
# Layer 1 — inspect-statusline: constants and path derivation
# ===========================================================================

def test_statusline_constants_are_the_published_contract():
    """Exact-equality pins on the five inspection constants.

    `OPT_OUT_MARKER_FILENAME` is a CROSS-SKILL string contract: the boundary
    guard that suppresses its missing-reading hard-stop lives in a different
    skill and reads exactly this filename under the gauge directory. A rename
    here would degrade that guard to a silent no-op (it would look for a marker
    nobody writes), so this test is meant to fail loudly rather than let the
    contract drift. The other four name the user-settings location the installer
    and the inspector must agree on byte-for-byte.
    """
    assert mod.OPT_OUT_MARKER_FILENAME == "context-guard-opt-out"
    assert mod.CONFIG_DIR_ENV_VAR == "CLAUDE_CONFIG_DIR"
    assert mod.DEFAULT_CONFIG_DIR_NAME == ".claude"
    assert mod.SETTINGS_FILENAME == "settings.json"
    assert mod.SELF_CHECK_SESSION_ID == "quo-setup-self-check"


def test_self_check_session_id_is_filename_safe(monkeypatch, tmp_path):
    # The installer's self-check writes a throwaway gauge under this id, so it
    # MUST pass the charset guard or that self-check would be unfalsifiable
    # (`gauge_path` would still compose a path, but `is_valid_session_id` is what
    # the producer gates on).
    assert mod.is_valid_session_id(mod.SELF_CHECK_SESSION_ID) is True
    _patch_tempdir(monkeypatch, tmp_path)
    path = mod.gauge_path(mod.SELF_CHECK_SESSION_ID)
    assert path.parent == tmp_path / ".quorum"


def test_opt_out_marker_path_shape(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    assert mod.opt_out_marker_path() == tmp_path / ".quorum" / "context-guard-opt-out"


def test_opt_out_marker_path_resolves_tempdir_at_call_time(monkeypatch, tmp_path):
    # Modeled on test_gauge_path_resolves_tempdir_at_call_time: the tempdir is
    # looked up per call, not captured at import, so a redirect takes effect.
    before = mod.opt_out_marker_path()
    _patch_tempdir(monkeypatch, tmp_path)
    after = mod.opt_out_marker_path()
    assert before != after
    assert after.parent.parent == tmp_path


def test_opt_out_marker_path_is_pure(monkeypatch, tmp_path):
    _patch_tempdir(monkeypatch, tmp_path)
    mod.opt_out_marker_path()
    assert not (tmp_path / ".quorum").exists()


def test_config_dir_honors_the_env_var(monkeypatch, tmp_path):
    override = tmp_path / "custom-config"
    _isolate_settings_env(monkeypatch, tmp_path, config_dir=override)
    assert mod.config_dir() == override


def test_config_dir_falls_back_to_home(monkeypatch, tmp_path):
    home = _isolate_settings_env(monkeypatch, tmp_path, config_dir=None)
    assert mod.config_dir() == home / ".claude"


def test_config_dir_ignores_an_empty_env_var(monkeypatch, tmp_path):
    # An empty string is falsy, so `config_dir` falls back to `<home>/.claude`.
    # A whitespace-only value's disposition is deliberately NOT asserted: the
    # landed `config_dir` treats any truthy string as the override (a `"   "`
    # would be used verbatim), and nothing in the helper pins whitespace as a
    # special case, so encoding one here would invent an unstated contract.
    home = _isolate_settings_env(monkeypatch, tmp_path, config_dir=None)
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", "")
    assert mod.config_dir() == home / ".claude"


def test_user_settings_path_in_both_modes(monkeypatch, tmp_path):
    override = tmp_path / "custom-config"
    _isolate_settings_env(monkeypatch, tmp_path, config_dir=override)
    assert mod.user_settings_path() == override / "settings.json"

    home = _isolate_settings_env(monkeypatch, tmp_path, config_dir=None)
    assert mod.user_settings_path() == home / ".claude" / "settings.json"


# ===========================================================================
# Layer 1 — the pure comparison and composition helpers
# ===========================================================================

def test_normalize_path_for_compare_folds_backslashes():
    # The function that makes a Windows-installed command recognizable on re-run:
    # the same path spelled with `\` and with `/` must compare equal on any OS.
    assert mod.normalize_path_for_compare(r"a\b\c") == mod.normalize_path_for_compare("a/b/c")


def test_normalize_path_for_compare_folds_redundant_segments():
    assert mod.normalize_path_for_compare("/a/./b//c") == mod.normalize_path_for_compare("/a/b/c")
    # Idempotence: normalizing an already-normalized token changes nothing.
    x = "/a/./b//c"
    assert mod.normalize_path_for_compare(mod.normalize_path_for_compare(x)) == mod.normalize_path_for_compare(x)
    # NOTE: case-folding is intentionally NOT asserted. `os.path.normcase` is
    # identity on POSIX, so any case assertion would be platform-dependent — a
    # later reader should not "fix" this omission by adding one.


def test_to_command_path_has_no_backslash(tmp_path):
    p = tmp_path / "some" / "context_gauge.py"
    out = mod.to_command_path(p)
    assert "\\" not in out
    # The forward-slashing must not be achieved by mangling the path: the output
    # still normalizes equal to the input.
    assert mod.normalize_path_for_compare(out) == mod.normalize_path_for_compare(str(p))


def test_to_command_path_is_absolute(tmp_path):
    out = mod.to_command_path(tmp_path / "x" / "y.py")
    assert os.path.isabs(out)


def test_status_line_shell_on_posix():
    shell = mod.status_line_shell()
    if os.name == "posix":
        assert shell == "sh"
    assert shell in {"sh", "git-bash", "powershell"}


@pytest.mark.parametrize(
    "which_result,expected",
    [("/usr/bin/bash", "git-bash"), (None, "powershell")],
    ids=["git-bash-present", "git-bash-absent"],
)
def test_status_line_shell_windows_branches(monkeypatch, which_result, expected):
    # The landed function branches on `os.name == "nt"` then `shutil.which("bash")`.
    # Patch both module-object references (auto-undone) to reach the Windows arms
    # on any host without a real Windows box.
    monkeypatch.setattr(mod.os, "name", "nt")
    monkeypatch.setattr(mod.shutil, "which", lambda cmd: which_result)
    assert mod.status_line_shell() == expected


# ===========================================================================
# Layer 1 — classify_status_line_command
# ===========================================================================

def _fake_script(tmp_path):
    """A `tmp_path`-based fake script path (forward-slashed str)."""
    return str(tmp_path / "context_gauge.py")


@pytest.mark.parametrize(
    "build,expected",
    [
        (lambda s: '"py" "{0}" produce'.format(s), ("direct", None)),
        (
            lambda s: '"py" "{0}" produce --wrap-command \'my status --flag\''.format(s),
            ("wrapped", "my status --flag"),
        ),
        (
            lambda s: '"py" "{0}" produce --wrap-command="my status --flag"'.format(s),
            ("wrapped", "my status --flag"),
        ),
    ],
    ids=["direct", "wrapped-space", "wrapped-equals"],
)
def test_classify_status_line_command_matrix(tmp_path, build, expected):
    script = _fake_script(tmp_path)
    assert mod.classify_status_line_command(build(script), script) == expected


def test_classify_status_line_command_other_install(tmp_path):
    script = _fake_script(tmp_path)
    other = str(tmp_path / "elsewhere" / "context_gauge.py")
    assert mod.classify_status_line_command(
        '"py" "{0}" produce'.format(other), script
    ) == ("other-install", None)
    # An other-install carrying a wrap payload still surfaces that payload.
    assert mod.classify_status_line_command(
        '"py" "{0}" produce --wrap-command \'x\''.format(other), script
    ) == ("other-install", "x")


def test_classify_status_line_command_foreign(tmp_path):
    script = _fake_script(tmp_path)
    assert mod.classify_status_line_command("vim /etc/hosts", script) == ("foreign", None)


def test_classify_status_line_command_unsplittable_is_foreign_without_raising(tmp_path):
    # An unbalanced-quote command raises `ValueError: No closing quotation` inside
    # `shlex.split`; the helper catches it and returns foreign. This is the branch
    # that keeps `inspect-statusline` from dying on an operator's exotic status
    # line.
    script = _fake_script(tmp_path)
    assert mod.classify_status_line_command("'unclosed", script) == ("foreign", None)


def test_classify_status_line_command_matches_a_backslash_spelled_script_path(tmp_path):
    # A Windows re-run spells its own script path with `\`; backslashes survive
    # `shlex.split` inside double quotes, and `normalize_path_for_compare` folds
    # them, so the command is still recognized as `direct`. Without this a Windows
    # re-run would fail to see its prior install and double-configure.
    script = _fake_script(tmp_path)
    backslashed = script.replace("/", "\\")
    command = '"py" "{0}" produce'.format(backslashed)
    assert mod.classify_status_line_command(command, script) == ("direct", None)


def test_classify_status_line_command_requires_the_produce_token(tmp_path):
    # The script path is present but the command runs `read`, not `produce`:
    # negative space that keeps the matcher from claiming any invocation of the
    # helper as a producer.
    script = _fake_script(tmp_path)
    assert mod.classify_status_line_command(
        '"py" "{0}" read --session-id x'.format(script), script
    ) == ("foreign", None)


def test_classify_status_line_command_never_parses_a_foreign_payload(tmp_path):
    # A foreign command that literally contains `--wrap-command something` must
    # still return `wrapped_command is None`: a foreign command is never parsed
    # for anything.
    script = _fake_script(tmp_path)
    state, wrap = mod.classify_status_line_command("echo --wrap-command something", script)
    assert state == "foreign"
    assert wrap is None


def test_classify_status_line_command_states_are_four_way_distinct(tmp_path):
    script = _fake_script(tmp_path)
    other = str(tmp_path / "elsewhere" / "context_gauge.py")
    results = [
        mod.classify_status_line_command('"py" "{0}" produce'.format(script), script),
        mod.classify_status_line_command(
            '"py" "{0}" produce --wrap-command \'w\''.format(script), script
        ),
        mod.classify_status_line_command('"py" "{0}" produce'.format(other), script),
        mod.classify_status_line_command("vim x", script),
    ]
    states = [r[0] for r in results]
    assert states == ["direct", "wrapped", "other-install", "foreign"]
    assert len(set(states)) == 4
    for state, _wrap in results:
        assert isinstance(state, str)
    for r in results:
        assert isinstance(r, tuple) and len(r) == 2


# ===========================================================================
# Layer 1 — detect_higher_precedence_sources: managed scope
# ===========================================================================
#
# The CLI `cmd_inspect_statusline` calls `detect_higher_precedence_sources`
# with the default (real) managed directory, so the ONLY safe way to exercise
# the managed-scope branches without writing to `/etc/claude-code/`,
# `/Library/Application Support/ClaudeCode/`, or `C:\Program Files\ClaudeCode\`
# is the function's own `managed_dir` injection point — the testability hook the
# implementation Subtask pinned. These unit-layer tests point it at a `tmp_path`
# sandbox and never touch the real system locations.


def test_detect_higher_precedence_sources_managed_status_line(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    managed = tmp_path / "managed"
    managed.mkdir()
    (managed / "managed-settings.json").write_text(
        json.dumps({"statusLine": {"type": "command", "command": "x"}}),
        encoding="utf-8",
    )
    sources = mod.detect_higher_precedence_sources(repo, managed_dir=managed)
    assert len(sources) == 1
    assert sources[0]["scope"] == "managed"
    assert sources[0]["path"] == str(managed / "managed-settings.json")
    assert "statusLine" in sources[0]["reason"]


@pytest.mark.parametrize("flag", ["allowManagedHooksOnly", "disableAllHooks"])
def test_detect_higher_precedence_sources_managed_hooks_lockdown(tmp_path, flag):
    repo = tmp_path / "repo"
    repo.mkdir()
    managed = tmp_path / "managed"
    managed.mkdir()
    (managed / "managed-settings.json").write_text(
        json.dumps({flag: True}), encoding="utf-8"
    )
    sources = mod.detect_higher_precedence_sources(repo, managed_dir=managed)
    assert len(sources) == 1
    assert sources[0]["scope"] == "managed"


def test_detect_higher_precedence_sources_managed_dropin(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    managed = tmp_path / "managed"
    dropin = managed / "managed-settings.d"
    dropin.mkdir(parents=True)
    (dropin / "10-status.json").write_text(
        json.dumps({"statusLine": {"command": "y"}}), encoding="utf-8"
    )
    sources = mod.detect_higher_precedence_sources(repo, managed_dir=managed)
    assert len(sources) == 1
    assert sources[0]["scope"] == "managed"
    assert sources[0]["path"] == str(dropin / "10-status.json")


def test_detect_higher_precedence_sources_absent_managed_dir_is_empty(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    # A managed dir that does not exist is skipped silently — no entry, no raise.
    assert mod.detect_higher_precedence_sources(repo, managed_dir=tmp_path / "nope") == []


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


def _run(args, stdin=None, env=None, cwd=None):
    # `cwd` is additive with a `None` default, so every pre-existing call site is
    # byte-for-byte unchanged. It exists so a test can exercise
    # `inspect-statusline`'s default `--repo-root` (the current working
    # directory) without chdir'ing the test process itself.
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=stdin,
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


def _isolated_cli_env(tmp_path, config_dir=None, home=None):
    """A copied environment sandboxed for a CLI `inspect-statusline` run.

    Built on `_env_with_tempdir` (TMPDIR/TEMP/TMP → `tmp_path`), then:

    - `HOME` and `USERPROFILE` → `home` (default `tmp_path/home`), with
      `HOMEDRIVE`/`HOMEPATH` popped so the Windows fallback cannot reach a real
      profile.
    - When `config_dir` is None, `CLAUDE_CONFIG_DIR` is POPPED from the copied
      environment. This is the single most important line here: `_env_with_tempdir`
      copies `os.environ`, so a developer or CI runner who exports
      `CLAUDE_CONFIG_DIR` would otherwise point every CLI test at their real
      config directory. A test asserting the default `~/.claude` derivation must
      pop it explicitly rather than assume it is unset.
    - When `config_dir` is given, `CLAUDE_CONFIG_DIR` is set to it.
    """
    env = _env_with_tempdir(tmp_path)
    resolved_home = home if home is not None else tmp_path / "home"
    env["HOME"] = str(resolved_home)
    env["USERPROFILE"] = str(resolved_home)
    env.pop("HOMEDRIVE", None)
    env.pop("HOMEPATH", None)
    if config_dir is None:
        env.pop("CLAUDE_CONFIG_DIR", None)
    else:
        env["CLAUDE_CONFIG_DIR"] = str(config_dir)
    return env


def _seed_settings(config_dir, obj_or_text):
    """Write `<config_dir>/settings.json`, creating the directory. Returns the path.

    Accepts either a dict (json-dumped) or raw text (written verbatim, for the
    unparseable / non-object cases no encoder would produce).
    """
    config_dir = Path(config_dir)
    config_dir.mkdir(parents=True, exist_ok=True)
    path = config_dir / "settings.json"
    if isinstance(obj_or_text, str):
        path.write_text(obj_or_text, encoding="utf-8")
    else:
        path.write_text(json.dumps(obj_or_text), encoding="utf-8")
    return path


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
    """Names of PUBLISHED gauge files under `<tmp_path>/.quorum`.

    `is_file()` is load-bearing, not defensive noise: the
    `unwritable_gauge_dir` fixture's `gauge-path-is-dir` arm pre-creates a
    DIRECTORY at the gauge file's own path, whose name matches this glob. A
    name-only listing would report that placeholder as a published gauge and
    turn every `_gauge_files(tmp_path) == []` assertion on that arm into a
    false failure — the question these call sites ask is whether a gauge was
    written, and a directory is not a written gauge.
    """
    directory = tmp_path / ".quorum"
    if not directory.is_dir():
        return []
    return sorted(
        p.name for p in directory.glob("context-usage-*.json") if p.is_file()
    )


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


# --- produce: an unwritable gauge directory under the CLI contract ----------
#
# The subprocess layer is where this defect was actually observed and where the
# harness reads the contract: a traceback out of `main()` means exit 1 and empty
# stdout, and the harness blanks the status line on either. These tests assert
# the process-level facts the unit layer cannot — the real `returncode`, real
# stderr with no `Traceback`, and a real wrapped command's bytes on stdout.
# `unwritable_gauge_dir` supplies all three filesystem failure points, and the
# session id each test publishes under comes FROM that fixture — see its
# docstring for why minting a local one would disarm an arm.


def test_cli_produce_unwritable_gauge_dir_with_wrap_emits_the_wrapped_display(
    tmp_path, unwritable_gauge_dir
):
    """REGRESSION GUARD. Pre-fix: exit 1, empty stdout, traceback on stderr."""
    session_id = unwritable_gauge_dir.session_id
    marker = "MARKER-no-trailing-newline"
    command = _stub(
        tmp_path,
        "marker_stub.py",
        "import sys\nsys.stdout.write(" + repr(marker) + ")\n",
    )
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 33},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    res = _run(
        ["produce", "--wrap-command", command],
        stdin=json.dumps(payload),
        env=_env_with_tempdir(tmp_path),
    )
    # Byte for byte: the wrapped display survives a failed gauge write intact.
    assert res.stdout == marker
    assert res.returncode == 0
    # One diagnostic line, it is a diagnostic — not a traceback — and it is THE
    # gauge-write diagnostic rather than some other line that happens to be
    # alone. All three arms fail inside `write_gauge`, so the message prefix is
    # arm-independent; the `[Errno ...]` tail legitimately differs per arm.
    err_lines = res.stderr.strip().splitlines()
    assert len(err_lines) == 1
    assert "cannot publish the context gauge" in err_lines[0]
    assert "Traceback" not in res.stderr
    assert _gauge_files(tmp_path) == []


def test_cli_produce_unwritable_gauge_dir_without_wrap_emits_the_default_display(
    tmp_path, unwritable_gauge_dir
):
    """REGRESSION GUARD. The unwrapped arm crashed identically pre-fix.

    The expected stdout here is the workspace basename, NOT the empty string: the
    payload is well-formed, so `default_display` has something to say. That
    distinguishes this from the parse-failure cases above, whose empty stdout is
    legitimate — an assertion of `""` would have passed against a producer that
    had stopped emitting a display at all.
    """
    session_id = unwritable_gauge_dir.session_id
    payload = {
        "session_id": session_id,
        "context_window": {"used_percentage": 33},
        "workspace": {"current_dir": "/home/dev/code/quorum"},
    }
    res = _run(
        ["produce"],
        stdin=json.dumps(payload),
        env=_env_with_tempdir(tmp_path),
    )
    assert res.stdout == "quorum"
    assert res.returncode == 0
    err_lines = res.stderr.strip().splitlines()
    assert len(err_lines) == 1
    assert "cannot publish the context gauge" in err_lines[0]
    assert "Traceback" not in res.stderr
    assert _gauge_files(tmp_path) == []


def test_cli_a_failed_publish_leaves_the_reader_with_no_usable_reading(
    tmp_path, unwritable_gauge_dir
):
    """End-to-end: `produce` swallows the write failure, so `read` carries it.

    The fix moves the failure signal off `produce`'s exit code, which makes the
    reader the only place a consumer can still learn that no reading exists. That
    hand-off is a claim the helper's decision record now makes, and nothing else
    in the suite crosses the two subcommands to check it. What matters for the
    guard's safety is what is asserted in EVERY arm: `read` never emits a
    percentage — asserted as "not a decimal integer at all", the same shape check
    `test_reading_values_are_four_way_distinct` uses, so it also holds against a
    reading this test never anticipated rather than only against the two literals
    this payload could have produced.

    The arms then legitimately diverge, and pinning that is the point:

    - `readonly` — the gauge directory is a real directory, the gauge file is
      simply absent, and `read` reports `missing` at exit 0. This is the shape
      the decision record describes.
    - `blocked` — a regular file occupies the directory's path, so `stat` on the
      gauge raises `NotADirectoryError` and `classify_reading` routes it to
      `MalformedGauge` -> exit 2. That is deliberate and commented as such in the
      helper ("present but un-stat-able ... a non-directory component in the
      path"), not a defect: an un-stat-able path is not evidence of absence.
      Asserting `missing` here would be asserting the decision record's prose
      over the code's documented behavior. This reader-side class is
      POSIX-verified and Windows-UNVERIFIED, so this arm's post-`read`
      assertions skip on Windows (the `produce` half above still runs there —
      the `mkdir` `FileExistsError` is platform-independent).
    - `gauge-path-is-dir` — a directory occupies the gauge FILE's path, so `stat`
      succeeds (a directory has an mtime, and it is fresh), staleness passes, and
      `read_text` raises `IsADirectoryError` -> `MalformedGauge` -> exit 2. Same
      contracted exit shape as `blocked` but reached through a LATER branch, so
      the two are pinned by their distinct diagnostics rather than lumped
      together; collapsing them would let one branch cover for the other.
    """
    session_id = unwritable_gauge_dir.session_id
    payload = {"session_id": session_id, "context_window": {"used_percentage": 33}}
    env = _env_with_tempdir(tmp_path)
    produced = _run(["produce"], stdin=json.dumps(payload), env=env)
    assert produced.returncode == 0
    # The publish really did fail — without this, an arm whose sabotage silently
    # stopped biting would still satisfy everything below via `missing`.
    assert "cannot publish the context gauge" in produced.stderr
    assert _gauge_files(tmp_path) == []

    res = _run(["read", "--session-id", session_id], env=env)
    # True in every arm, and the load-bearing half: a lost reading is never
    # reported as a percentage.
    assert not res.stdout.strip().isdigit()
    if unwritable_gauge_dir.arm == "blocked" and os.name == "nt":
        pytest.skip(
            "POSIX-only sabotage: a file at a path COMPONENT raises "
            "NotADirectoryError on POSIX, but Windows may report "
            "ERROR_PATH_NOT_FOUND -> FileNotFoundError, which classify_reading "
            "routes to `missing` (exit 0), not MalformedGauge (exit 2). "
            "Unverified on Windows. To lift this skip, confirm what Path.stat() "
            "raises there for a path whose parent is a regular file; if it is "
            "FileNotFoundError, this arm needs a different Windows-side "
            "un-stat-able trigger, not a weaker assertion. The produce-side "
            "assertions above already ran on this platform."
        )
    if unwritable_gauge_dir.arm == "readonly":
        assert res.returncode == 0, res.stderr
        assert res.stdout == "missing\n"
    else:
        assert res.returncode == 2
        assert res.stdout == ""
        err_lines = res.stderr.strip().splitlines()
        assert len(err_lines) == 1
        # Which malformation branch fired is the arm's whole point.
        if unwritable_gauge_dir.arm == "blocked":
            assert "cannot stat gauge file" in err_lines[0]
        else:
            assert "gauge file is unreadable" in err_lines[0]


@pytest.mark.parametrize("stdin_kind", ["valid", "unparseable", "empty"])
@pytest.mark.parametrize("wrap_kind", ["working", "broken", "absent"])
def test_cli_produce_never_crashes_across_the_adverse_environment_matrix(
    tmp_path, unwritable_gauge_dir, stdin_kind, wrap_kind
):
    """Structural guard for the whole class: no combination may exit non-zero.

    The named tests above pin the two cases that matter most precisely; this one
    sweeps every stdin shape x wrap-command state x gauge-dir failure point
    together, asserting only the two facts the harness actually branches on. It
    exists because the shipped defect was a MISSING combination rather than a
    wrong assertion — parse failures were covered, filesystem failures were not,
    and no single-axis test would have noticed. Deliberately thin: stdout content
    is the named tests' job, so widening this one is not the fix if it ever fails.

    Read the coverage claim precisely, because the axes are not equally live: the
    `unparseable` and `empty` stdin shapes bail before `write_gauge` is ever
    reached, so the gauge-dir sabotage is INERT in 18 of the 27 cases and those
    re-cover the blanking shape already pinned by the named parse-failure tests.
    The 9 `valid`-stdin cases are the sweep that actually exercises this fix. The
    other 18 are kept on purpose rather than trimmed: the defect being guarded is
    a missing COMBINATION, so the guard has to be the full cross-product — a
    matrix pruned to the combinations someone believed were live is exactly the
    reasoning that let the original gap through.
    """
    if stdin_kind == "valid":
        stdin = json.dumps(
            {
                # The fixture's session id, not a local one: on the
                # `gauge-path-is-dir` arm any other identifier would write
                # successfully and this sweep would stop covering that arm.
                "session_id": unwritable_gauge_dir.session_id,
                "context_window": {"used_percentage": 33},
                "workspace": {"current_dir": "/home/dev/code/quorum"},
            }
        )
    elif stdin_kind == "unparseable":
        stdin = "{not json"
    else:
        stdin = ""

    if wrap_kind == "working":
        args = ["produce", "--wrap-command", _stub(
            tmp_path, "marker_stub.py", "import sys\nsys.stdout.write('M')\n"
        )]
    elif wrap_kind == "broken":
        args = ["produce", "--wrap-command", _stub(
            tmp_path, "fail_stub.py", "import sys\nsys.exit(3)\n"
        )]
    else:
        args = ["produce"]

    res = _run(args, stdin=stdin, env=_env_with_tempdir(tmp_path))
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
    # Reference the helper constant so this ages the gauge past the CURRENT
    # window (with slack), not a hardcoded 300s that would sit inside it.
    aged = time.time() - (mod.FRESHNESS_WINDOW_SECONDS + 60)
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


# --- inspect-statusline: the reported object -------------------------------
#
# Every invocation goes through `_isolated_cli_env`, and every `higher_precedence`
# assertion passes an explicit clean `--repo-root` so a `.claude/` beside the
# test process's real cwd cannot bleed in.

INSPECT_KEYS = {
    "settings_path",
    "settings_exists",
    "status_line_present",
    "status_line_command",
    "status_line_extra_keys",
    "producer_state",
    "wrapped_command",
    "producer_current",
    "script_path",
    "python_executable",
    "opt_out_marker_path",
    "opt_out_marker_present",
    "higher_precedence_sources",
    "status_line_shell",
}


def _inspect(tmp_path, repo, env, cwd=None):
    args = ["inspect-statusline"]
    if repo is not None:
        args += ["--repo-root", str(repo)]
    return _run(args, env=env, cwd=cwd)


def test_cli_inspect_statusline_absent_settings_file(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert isinstance(obj, dict)
    # Exact key set: a key added later must force a decision here.
    assert set(obj) == INSPECT_KEYS
    assert obj["settings_exists"] is False
    assert obj["producer_state"] == "absent"
    assert obj["status_line_present"] is False
    assert obj["status_line_command"] is None
    assert obj["status_line_extra_keys"] == {}
    assert obj["wrapped_command"] is None
    assert obj["producer_current"] is False
    assert obj["opt_out_marker_present"] is False
    assert obj["higher_precedence_sources"] == []
    assert obj["python_executable"] == sys.executable
    assert obj["script_path"] == str(SCRIPT)


def test_cli_inspect_statusline_creates_nothing(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    before = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    after = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob("*"))
    assert before == after
    # Read-only: neither the default config dir nor the gauge dir springs up.
    assert not (tmp_path / "home" / ".claude").exists()
    assert not (tmp_path / ".quorum").exists()


def test_cli_inspect_statusline_reports_a_foreign_status_line(tmp_path):
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": "vim /etc/hosts"}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["producer_state"] == "foreign"
    assert obj["status_line_command"] == "vim /etc/hosts"
    assert obj["wrapped_command"] is None


def test_cli_inspect_statusline_reports_extra_status_line_keys(tmp_path):
    config = tmp_path / "cfg"
    extras = {"padding": 3, "refreshInterval": 1000, "hideVimModeIndicator": True}
    status_line = dict(extras)
    status_line["type"] = "command"
    status_line["command"] = "vim x"
    _seed_settings(config, {"statusLine": status_line})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["status_line_extra_keys"] == extras
    # `type` and `command` are never carried in the extra-keys map.
    assert "type" not in obj["status_line_extra_keys"]
    assert "command" not in obj["status_line_extra_keys"]


def test_cli_inspect_statusline_reports_no_extra_status_line_keys(tmp_path):
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": "vim x"}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["status_line_extra_keys"] == {}


@pytest.mark.parametrize(
    "status_line",
    ["a string", ["a", "list"], {"type": "command"}, {"command": ""}, {"command": 7}],
    ids=["string", "list", "no-command", "empty-command", "non-string-command"],
)
def test_cli_inspect_statusline_degenerate_status_line_is_absent(tmp_path, status_line):
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": status_line})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["producer_state"] == "absent"
    # The module docstring pins `status_line_present` false for every degenerate
    # shape ("every such degenerate shape reports status_line_present false and
    # producer_state absent"), so it is asserted here rather than left unstated.
    assert obj["status_line_present"] is False


def test_cli_inspect_statusline_unparseable_settings_exits_2(tmp_path):
    """An existing-but-unparseable settings file exits 2, never reports `absent`.

    Reporting `absent` would be the dangerous answer: a caller that writes
    settings keys off `absent` and would clobber a file it could not read. So the
    inspection must hard-fail (exit 2, one stderr line naming the path) rather
    than let a garbled file look like no configuration at all. The file must be
    left byte-identical.
    """
    config = tmp_path / "cfg"
    path = _seed_settings(config, "{not json")
    before = path.read_bytes()
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 2
    assert res.stdout == ""
    lines = res.stderr.strip().splitlines()
    assert len(lines) == 1
    assert str(path) in lines[0]
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "text", ["[1, 2]", "42", '"a string"', "null", "true"],
    ids=["array", "number", "string", "null", "bool"],
)
def test_cli_inspect_statusline_non_object_settings_exits_2(tmp_path, text):
    config = tmp_path / "cfg"
    path = _seed_settings(config, text)
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 2
    assert res.stdout == ""
    lines = res.stderr.strip().splitlines()
    assert len(lines) == 1
    assert str(path) in lines[0]


def test_cli_inspect_statusline_detects_a_direct_producer(tmp_path):
    shell = mod.status_line_shell()
    current = mod.compose_status_line_command(sys.executable, str(SCRIPT), None, shell)
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": current}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["producer_state"] == "direct"
    assert obj["wrapped_command"] is None
    assert obj["producer_current"] is True


def test_cli_inspect_statusline_detects_a_wrapped_producer(tmp_path):
    shell = mod.status_line_shell()
    current = mod.compose_status_line_command(sys.executable, str(SCRIPT), "my status", shell)
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": current}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["producer_state"] == "wrapped"
    assert obj["wrapped_command"] == "my status"
    assert obj["producer_current"] is True


def test_cli_inspect_statusline_direct_but_stale_interpreter_is_not_current(tmp_path):
    # Same `direct` state, different interpreter token: `producer_current` flips
    # false, which is how a caller learns a refresh is needed.
    shell = mod.status_line_shell()
    stale = mod.compose_status_line_command("/nonexistent/python3", str(SCRIPT), None, shell)
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": stale}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["producer_state"] == "direct"
    assert obj["producer_current"] is False


def test_cli_inspect_statusline_detects_an_other_install(tmp_path):
    other = mod.to_command_path(str(tmp_path / "otherdir" / "context_gauge.py"))
    command = '"{0}" "{1}" produce'.format(sys.executable, other)
    config = tmp_path / "cfg"
    _seed_settings(config, {"statusLine": {"type": "command", "command": command}})
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["producer_state"] == "other-install"


def test_cli_inspect_statusline_reports_the_opt_out_marker(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = _isolated_cli_env(tmp_path)
    # False before the marker exists — and the lookup creates nothing.
    res = _inspect(tmp_path, repo, env)
    assert res.returncode == 0, res.stderr
    obj = json.loads(res.stdout)
    assert obj["opt_out_marker_present"] is False
    assert not (tmp_path / ".quorum").exists()
    expected = tmp_path / ".quorum" / "context-guard-opt-out"
    assert obj["opt_out_marker_path"] == str(expected)

    # True once the marker is created under the sandboxed gauge dir.
    expected.parent.mkdir(parents=True, exist_ok=True)
    expected.write_text("", encoding="utf-8")
    res2 = _inspect(tmp_path, repo, env)
    obj2 = json.loads(res2.stdout)
    assert obj2["opt_out_marker_present"] is True
    assert obj2["opt_out_marker_path"] == str(expected)


def test_cli_inspect_statusline_honors_claude_config_dir(tmp_path):
    config = tmp_path / "cfg"
    config.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path, config_dir=config))
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["settings_path"] == str(config / "settings.json")


def test_cli_inspect_statusline_defaults_to_home_dot_claude(tmp_path):
    # Proves `_isolated_cli_env` pops any inherited CLAUDE_CONFIG_DIR: the default
    # derivation must resolve under the sandboxed home, not the developer's.
    repo = tmp_path / "repo"
    repo.mkdir()
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    expected = tmp_path / "home" / ".claude" / "settings.json"
    assert json.loads(res.stdout)["settings_path"] == str(expected)


def test_cli_inspect_statusline_reports_project_and_local_precedence(tmp_path):
    repo = tmp_path / "repo"
    dot = repo / ".claude"
    dot.mkdir(parents=True)
    project = dot / "settings.json"
    local = dot / "settings.local.json"
    project.write_text(json.dumps({"statusLine": {"command": "p"}}), encoding="utf-8")
    local.write_text(json.dumps({"statusLine": {"command": "l"}}), encoding="utf-8")
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    sources = json.loads(res.stdout)["higher_precedence_sources"]
    by_scope = {s["scope"]: s for s in sources}
    assert set(by_scope) == {"project", "local"}
    assert len([s for s in sources if s["scope"] == "project"]) == 1
    assert len([s for s in sources if s["scope"] == "local"]) == 1
    for scope, path in (("project", project), ("local", local)):
        assert set(by_scope[scope]) == {"scope", "path", "reason"}
        assert by_scope[scope]["path"] == str(path)


def test_cli_inspect_statusline_ignores_precedence_files_without_status_line(tmp_path):
    repo = tmp_path / "repo"
    dot = repo / ".claude"
    dot.mkdir(parents=True)
    (dot / "settings.json").write_text(json.dumps({"model": "opus"}), encoding="utf-8")
    (dot / "settings.local.json").write_text(json.dumps({"theme": "dark"}), encoding="utf-8")
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["higher_precedence_sources"] == []


@pytest.mark.parametrize(
    "text", ["{not valid json", "[1, 2, 3]"], ids=["invalid-json", "top-level-array"]
)
def test_cli_inspect_statusline_tolerates_a_broken_precedence_file(tmp_path, text):
    # Someone else's malformed project file must never fail our inspection.
    repo = tmp_path / "repo"
    dot = repo / ".claude"
    dot.mkdir(parents=True)
    (dot / "settings.json").write_text(text, encoding="utf-8")
    res = _inspect(tmp_path, repo, _isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr
    assert res.stderr == ""
    assert json.loads(res.stdout)["higher_precedence_sources"] == []


def test_cli_inspect_statusline_uses_the_cwd_as_the_default_repo_root(tmp_path):
    repo = tmp_path / "repo"
    dot = repo / ".claude"
    dot.mkdir(parents=True)
    (dot / "settings.json").write_text(
        json.dumps({"statusLine": {"command": "p"}}), encoding="utf-8"
    )
    # No --repo-root: the default is the process cwd, exercised via _run(cwd=...).
    res = _inspect(tmp_path, None, _isolated_cli_env(tmp_path), cwd=str(repo))
    assert res.returncode == 0, res.stderr
    scopes = [s["scope"] for s in json.loads(res.stdout)["higher_precedence_sources"]]
    assert "project" in scopes


def test_cli_inspect_statusline_help_exits_0(tmp_path):
    res = _run(["inspect-statusline", "--help"], env=_isolated_cli_env(tmp_path))
    assert res.returncode == 0, res.stderr


def test_cli_inspect_statusline_unknown_flag_exits_2(tmp_path):
    res = _run(["inspect-statusline", "--nope"], env=_isolated_cli_env(tmp_path))
    assert res.returncode == 2


# --- argparse contract -----------------------------------------------------

def test_cli_help_exits_0_and_names_the_core_subcommands(tmp_path):
    res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert "produce" in res.stdout
    assert "read" in res.stdout


def test_cli_help_names_the_inspection_subcommand(tmp_path):
    res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert "inspect-statusline" in res.stdout


def test_cli_no_subcommand_exits_2(tmp_path):
    res = _run([], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


def test_cli_unknown_subcommand_exits_2(tmp_path):
    res = _run(["bogus"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


def test_cli_read_requires_session_id(tmp_path):
    res = _run(["read"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


# --- stop-threshold CLI contract -------------------------------------------

def test_cli_stop_threshold_emits_the_constant(tmp_path):
    # One invocation yields the threshold integer on stdout, exit 0. The value is
    # compared to `mod.STOP_THRESHOLD_PERCENT` symbolically — never a bare literal
    # 50 — so the seam and the single-definition-site tunable stay pinned together:
    # a future retune of the constant moves this assertion with it, and the
    # value-is-50 pin lives once in `test_tunable_constants`.
    res = _run(["stop-threshold"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    # Parse to an int rather than asserting a byte-exact string: the Task pins only
    # that a consumer can obtain the threshold integer from one invocation.
    assert int(res.stdout.strip()) == mod.STOP_THRESHOLD_PERCENT
    # Success path is quiet on stderr.
    assert res.stderr == ""


def test_cli_help_names_the_stop_threshold_subcommand(tmp_path):
    res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert "stop-threshold" in res.stdout


def test_cli_stop_threshold_unknown_flag_exits_2(tmp_path):
    res = _run(["stop-threshold", "--nope"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 2


# ===========================================================================
# Layer 1 — quote_for_shell / compose_status_line_command (pure)
# ===========================================================================

# A single list of adversarial values reused across every quoting and wrapping
# round-trip below: a space, a single quote, a double quote, a shell variable, a
# backtick, a command separator, a newline, a literal `--wrap-command` token (the
# anti-double-wrap payload the CLI depends on), the empty string, and a unicode
# string. Any quoting bug on any of these shows up as a failed round trip rather
# than a shape mismatch.
NASTY_VALUES = [
    "a b",
    "it's",
    'say "hi"',
    "$HOME",
    "`",
    "a;b",
    "a\nb",
    "--wrap-command x",
    "",
    "unïcodé",
]


@pytest.mark.parametrize("value", NASTY_VALUES, ids=range(len(NASTY_VALUES)))
def test_quote_for_shell_sh_round_trips(value):
    # A genuine round-trip property, not a shape assertion: whatever `sh` quoting
    # produces must tokenize back to the single original value under `shlex.split`.
    assert shlex.split(mod.quote_for_shell(value, "sh")) == [value]


@pytest.mark.parametrize("value", NASTY_VALUES, ids=range(len(NASTY_VALUES)))
def test_quote_for_shell_git_bash_matches_sh(value):
    # Git Bash accepts POSIX quoting, so it MUST get byte-identical output to `sh`;
    # this pins that it is never handed a divergent quoting rule.
    assert mod.quote_for_shell(value, "git-bash") == mod.quote_for_shell(value, "sh")


def test_quote_for_shell_powershell_doubles_single_quotes():
    # PowerShell single-quoting: wrap in single quotes, every inner single quote
    # doubled. Exact-equality on each landmark case.
    assert mod.quote_for_shell("it's", "powershell") == "'it''s'"
    assert mod.quote_for_shell("a b", "powershell") == "'a b'"
    two = mod.quote_for_shell("a'b'c", "powershell")
    assert two == "'a''b''c'"
    # Both single quotes doubled, and the result is single-quote delimited.
    assert two.startswith("'") and two.endswith("'")


def test_quote_for_shell_powershell_does_not_expand():
    # A `$var` and a backtick are preserved character-for-character between the
    # outer single quotes — PowerShell single quotes suppress every expansion.
    value = "$PATH and a " + "`" + " backtick"
    result = mod.quote_for_shell(value, "powershell")
    assert result.startswith("'") and result.endswith("'")
    assert result[1:-1] == value


def test_quote_for_shell_empty_value():
    assert mod.quote_for_shell("", "sh") == "''"
    assert mod.quote_for_shell("", "powershell") == "''"


# The unknown-`shell` argument is deliberately left uncovered: the landed
# `quote_for_shell` docstring pins behavior only for `sh`, `git-bash`, and
# `powershell` and says nothing about any other value (the code happens to fall
# through to `shlex.quote`, but that is unstated), so asserting a contract for it
# would invent one the module never promises.


def test_compose_status_line_command_exact_shape():
    # Exact string equality, not a substring probe: the two own-tokens are
    # double-quoted, forward-slashed absolute paths joined by a single space and
    # the literal ` produce`.
    py = Path("/opt/py/bin/python3")
    script = Path("/opt/skills/context_gauge.py")
    expected = '"{0}" "{1}" produce'.format(
        mod.to_command_path(py), mod.to_command_path(script)
    )
    assert mod.compose_status_line_command(py, script, None, "sh") == expected


def test_compose_status_line_command_has_no_backslash():
    # Paths built with the native separator must never leave a backslash in the
    # composed command — Git Bash would consume it.
    py = os.sep.join(["", "opt", "py", "python3"])
    script = os.sep.join(["", "opt", "skills", "context_gauge.py"])
    result = mod.compose_status_line_command(py, script, None, "sh")
    assert "\\" not in result


@pytest.mark.parametrize("wrap", [None, ""], ids=["none", "empty"])
def test_compose_status_line_command_omits_the_flag_when_nothing_is_wrapped(wrap):
    result = mod.compose_status_line_command("/py", "/s/context_gauge.py", wrap, "sh")
    assert "--wrap-command" not in result
    assert shlex.split(result)[-1] == "produce"


# The empty string is excluded here: a falsy wrap payload is DEFINED to omit the
# flag entirely (see the omit test above), so it has no last-token to round-trip.
# Every non-empty adversarial value is exercised.
NASTY_WRAP_VALUES = [v for v in NASTY_VALUES if v]


@pytest.mark.parametrize("value", NASTY_WRAP_VALUES, ids=range(len(NASTY_WRAP_VALUES)))
def test_compose_status_line_command_wrap_payload_round_trips(value):
    # The property the anti-double-wrap CLI test rests on: an arbitrary wrap
    # payload survives composition byte-exactly through `shlex.split`, including a
    # payload that itself contains `--wrap-command` and one carrying embedded
    # quotes.
    composed = mod.compose_status_line_command("/py", "/s/context_gauge.py", value, "sh")
    assert shlex.split(composed)[-1] == value


@pytest.mark.parametrize(
    "wrap", [None, "orig --wrap-command x"], ids=["unwrapped", "wrapped"]
)
def test_compose_status_line_command_has_exactly_one_produce_token(wrap):
    tokens = shlex.split(
        mod.compose_status_line_command("/py", "/s/context_gauge.py", wrap, "sh")
    )
    assert tokens.count("produce") == 1
    assert tokens.count("--wrap-command") <= 1


# ===========================================================================
# Layer 2 — install-statusline / write-opt-out (CLI, subprocess)
# ===========================================================================
#
# Isolation rules specific to this surface (the only code in the repo that writes
# into the operator's Claude Code user settings AND the only code that spawns a
# subprocess writing a gauge under the reserved `quo-setup-self-check` id):
#
# - EVERY `install-statusline` invocation passes `--no-self-check` EXCEPT the
#   three tests whose subject IS the self-check (self-check verifies, failed
#   self-check is non-fatal, and the with-self-check leg of the delete-nothing
#   test). `--no-self-check` removes the subprocess-spawn variable from every
#   other test.
# - Those self-check invocations all run under `_isolated_cli_env(tmp_path,
#   config_dir=...)`, whose TMPDIR/TEMP/TMP are inherited by the spawned shell, so
#   the self-check gauge lands at
#   `tmp_path/".quorum"/"context-usage-quo-setup-self-check.json"` — never the
#   developer's real temp dir. `test_cli_install_statusline_self_check_verifies`
#   asserts that file's existence under `tmp_path`, which simultaneously proves
#   the self-check ran and proves the redirect held.
# - The one in-process test (`os.replace` failure) never runs a real self-check:
#   it calls `cmd_install_statusline` with the no-self-check flag under
#   `_isolate_settings_env`, whose `_patch_tempdir` patches only the in-process
#   `mod.tempfile` object and would NOT redirect a spawned child, so it disables
#   the spawn rather than crossing the boundary.


def _config_listing(config_dir):
    """Sorted names directly inside a config directory (temp files included)."""
    return sorted(p.name for p in Path(config_dir).iterdir())


def _read_settings(config_dir):
    return json.loads((Path(config_dir) / "settings.json").read_text(encoding="utf-8"))


def test_cli_install_statusline_fresh_install(tmp_path):
    config = tmp_path / "cfg"
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert summary["action"] == "installed"
    assert summary["previous_command"] is None
    assert summary["preserved_status_line_keys"] == []
    # Config directory was created and holds exactly the settings file.
    assert config.is_dir()
    on_disk = _read_settings(config)
    assert list(on_disk.keys()) == ["statusLine"]
    command = summary["new_command"]
    assert on_disk["statusLine"] == {"type": "command", "command": command}
    # Command shape: no backslash, the forward-slashed script path, produce last.
    assert "\\" not in command
    assert str(SCRIPT).replace("\\", "/") in command
    assert shlex.split(command)[-1] == "produce"


def test_cli_install_statusline_wraps_a_foreign_status_line(tmp_path):
    config = tmp_path / "cfg"
    foreign = "weather --loc 'San Jose'"
    unrelated = {"nested": {"a": [1, 2], "b": "keep"}}
    _seed_settings(
        config,
        {
            "unrelated": unrelated,
            "statusLine": {
                "type": "command",
                "command": foreign,
                "padding": 3,
                "refreshInterval": 1000,
            },
        },
    )
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert summary["action"] == "wrapped"
    assert summary["previous_command"] == foreign
    assert "padding" in summary["preserved_status_line_keys"]
    on_disk = _read_settings(config)
    # An unrelated top-level key deep-equals its seeded value.
    assert on_disk["unrelated"] == unrelated
    status_line = on_disk["statusLine"]
    assert status_line["type"] == "command"
    # The foreign statusLine's other keys survive the rewrite.
    assert status_line["padding"] == 3
    assert status_line["refreshInterval"] == 1000
    # The foreign command is carried opaquely as the wrap payload, byte-exactly.
    assert shlex.split(summary["new_command"])[-1] == foreign


def test_cli_install_statusline_is_idempotent(tmp_path):
    config = tmp_path / "cfg"
    env = _isolated_cli_env(tmp_path, config_dir=config)
    first = _run(["install-statusline", "--no-self-check"], env=env)
    assert first.returncode == 0, first.stderr
    settings_file = config / "settings.json"
    before_bytes = settings_file.read_bytes()
    before_mtime = settings_file.stat().st_mtime_ns

    second = _run(["install-statusline", "--no-self-check"], env=env)
    assert second.returncode == 0, second.stderr
    assert json.loads(second.stdout)["action"] == "already-configured"
    # No write: identical bytes AND an untouched mtime are the no-write proof.
    assert settings_file.read_bytes() == before_bytes
    assert settings_file.stat().st_mtime_ns == before_mtime
    assert _config_listing(config) == ["settings.json"]


def test_cli_install_statusline_repoints_without_nesting(tmp_path):
    # THE most important test here: a nesting regression (wrapping the previous
    # whole producer command instead of reusing its extracted payload) is invisible
    # to every other assertion. Seed a producer whose script path is a DIFFERENT
    # context_gauge.py (a moved install) carrying a wrap payload; the reinstall
    # must reuse that payload verbatim and never double-wrap.
    config = tmp_path / "cfg"
    other_script = str(tmp_path / "old" / "context_gauge.py")
    seeded = mod.compose_status_line_command(
        sys.executable, other_script, "orig-cmd --flag", "sh"
    )
    _seed_settings(config, {"statusLine": {"type": "command", "command": seeded}})
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert summary["action"] == "repointed"
    tokens = shlex.split(summary["new_command"])
    assert tokens.count("produce") == 1
    assert tokens.count("--wrap-command") == 1
    # The payload is exactly the previously-wrapped payload, NOT the whole prior
    # command string (which is what a nesting bug would carry).
    assert tokens[-1] == "orig-cmd --flag"


def test_cli_install_statusline_repoints_a_direct_install_on_a_python_change(tmp_path):
    # A `direct`/`wrapped` state whose recomposed command is not byte-identical
    # reports `repointed` — here forced by a moved interpreter.
    config = tmp_path / "cfg"
    current = mod.compose_status_line_command(sys.executable, str(SCRIPT), None, "sh")
    _seed_settings(config, {"statusLine": {"type": "command", "command": current}})
    other_python = str(tmp_path / "other-python")
    res = _run(
        ["install-statusline", "--no-self-check", "--python", other_python],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert summary["action"] == "repointed"
    assert summary["previous_command"] == current
    assert mod.to_command_path(other_python) in summary["new_command"]


def test_cli_install_statusline_wrap_payload_round_trips_through_shlex(tmp_path):
    config = tmp_path / "cfg"
    foreign = "prompt --api $KEY --note 'it''s fine'"
    _seed_settings(config, {"statusLine": {"type": "command", "command": foreign}})
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert shlex.split(summary["new_command"])[-1] == foreign


def test_cli_install_statusline_unparseable_settings_exits_2(tmp_path):
    config = tmp_path / "cfg"
    path = _seed_settings(config, "{not json")
    before = path.read_bytes()
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 2
    lines = res.stderr.strip().splitlines()
    assert len(lines) == 1
    # Never clobbered: byte-identical, no statusLine written, no temp file left.
    assert path.read_bytes() == before
    assert _config_listing(config) == ["settings.json"]


@pytest.mark.parametrize(
    "text", ["[1, 2]", "42", '"a string"', "null", "true"],
    ids=["array", "number", "string", "null", "bool"],
)
def test_cli_install_statusline_non_object_settings_exits_2(tmp_path, text):
    config = tmp_path / "cfg"
    path = _seed_settings(config, text)
    before = path.read_bytes()
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 2
    lines = res.stderr.strip().splitlines()
    assert len(lines) == 1
    assert path.read_bytes() == before
    assert _config_listing(config) == ["settings.json"]


def test_cli_install_statusline_leaves_no_temp_file(tmp_path):
    config = tmp_path / "cfg"
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    assert _config_listing(config) == ["settings.json"]


def test_cmd_install_statusline_replace_failure_leaves_the_original_intact(
    monkeypatch, tmp_path
):
    """The atomic-write `except`→unlink path leaves no observable partial file.

    In-process (not subprocess) so `mod.os.replace` can be forced to raise. This
    is the ONLY reachable proof that a failed replace never leaves a half-written
    settings file or an orphaned temp file behind. The self-check is disabled so
    no spawn crosses the in-process tempdir patch — but `os.replace` raises well
    before the self-check step anyway.
    """
    config = tmp_path / "cfg"
    path = _seed_settings(
        config,
        {"keep": {"x": 1}, "statusLine": {"type": "command", "command": "vim x"}},
    )
    before = path.read_bytes()
    _isolate_settings_env(monkeypatch, tmp_path, config_dir=config)

    def boom(*args, **kwargs):
        raise RuntimeError("replace refused")

    monkeypatch.setattr(mod.os, "replace", boom)
    args = types.SimpleNamespace(repo_root=None, python=None, no_self_check=True)
    with pytest.raises(RuntimeError):
        mod.cmd_install_statusline(args)

    assert path.read_bytes() == before
    assert _config_listing(config) == ["settings.json"]


def test_cli_install_statusline_no_self_check_performs_no_spawn(tmp_path):
    config = tmp_path / "cfg"
    res = _run(
        ["install-statusline", "--no-self-check"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    # No producer was spawned: no gauge dir, no gauge file.
    assert _gauge_files(tmp_path) == []
    assert not (tmp_path / ".quorum").exists()
    # The docstring pins the exact skipped shape.
    assert json.loads(res.stdout)["self_check"] == {
        "verified": None,
        "detail": "skipped: --no-self-check",
    }


def test_cli_install_statusline_self_check_verifies(tmp_path):
    # A self-check test: no `--no-self-check`, run under `_isolated_cli_env` so the
    # spawned producer's gauge lands under tmp_path.
    config = tmp_path / "cfg"
    res = _run(
        ["install-statusline"],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout)["self_check"]["verified"] is True
    gauge = tmp_path / ".quorum" / "context-usage-quo-setup-self-check.json"
    assert gauge.exists()
    record = json.loads(gauge.read_text(encoding="utf-8"))
    assert record["session_id"] == "quo-setup-self-check"
    assert abs(gauge.stat().st_mtime - time.time()) < 30


def test_cli_install_statusline_failed_self_check_is_non_fatal(tmp_path):
    # Force the self-check to fail with a non-interpreter `--python`. The install
    # is still reported (exit 0) and NOT reverted — the composed (broken) command
    # remains on disk.
    config = tmp_path / "cfg"
    broken_python = str(tmp_path / "definitely-not-an-interpreter")
    res = _run(
        ["install-statusline", "--python", broken_python],
        env=_isolated_cli_env(tmp_path, config_dir=config),
    )
    assert res.returncode == 0, res.stderr
    summary = json.loads(res.stdout)
    assert summary["self_check"]["verified"] is False
    assert isinstance(summary["self_check"]["detail"], str)
    assert summary["self_check"]["detail"]
    # The settings file still holds the composed (broken) command — reported, not
    # reverted.
    on_disk = _read_settings(config)
    assert on_disk["statusLine"]["command"] == summary["new_command"]
    assert mod.to_command_path(broken_python) in on_disk["statusLine"]["command"]
    assert "Traceback" not in res.stderr


# --- write-opt-out ---------------------------------------------------------

def test_cli_write_opt_out_creates_the_marker(tmp_path):
    assert not (tmp_path / ".quorum").exists()
    res = _run(["write-opt-out"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert (tmp_path / ".quorum").is_dir()
    marker = tmp_path / ".quorum" / "context-guard-opt-out"
    assert marker.exists()
    # The docstring pins "prints its path", so assert exact equality.
    assert res.stdout.strip() == str(marker)


def test_cli_write_opt_out_is_idempotent(tmp_path):
    env = _env_with_tempdir(tmp_path)
    first = _run(["write-opt-out"], env=env)
    assert first.returncode == 0, first.stderr
    marker = tmp_path / ".quorum" / "context-guard-opt-out"
    first_bytes = marker.read_bytes()
    second = _run(["write-opt-out"], env=env)
    assert second.returncode == 0, second.stderr
    assert marker.read_bytes() == first_bytes
    # Exactly one marker, and no gauge file was ever created.
    markers = [
        p for p in (tmp_path / ".quorum").iterdir() if p.name == "context-guard-opt-out"
    ]
    assert len(markers) == 1
    assert _gauge_files(tmp_path) == []


def test_cli_write_opt_out_marker_body_states_its_scope(tmp_path):
    # Deliberately loose substring checks — the body is advisory prose, never
    # parsed by the guard, so its exact wording is not a contract. What must hold:
    # it states the missing-reading scope, states that deletion re-enables the
    # guard, and clarifies it does NOT suppress a genuine over-threshold stop.
    res = _run(["write-opt-out"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    body = (tmp_path / ".quorum" / "context-guard-opt-out").read_text(encoding="utf-8")
    assert "missing-reading" in body
    assert "Delete this file" in body
    assert "over-threshold" in body
    assert "NOT suppress" in body


def test_cli_write_opt_out_has_no_removal_subcommand(tmp_path):
    # No removal path exists and none may be added — pinned at the CLI surface.
    help_res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert help_res.returncode == 0, help_res.stderr
    lowered = help_res.stdout.lower()
    for forbidden in ("remove-opt-out", "clear-opt-out", "delete-opt-out"):
        assert forbidden not in lowered
    bad = _run(["remove-opt-out"], env=_env_with_tempdir(tmp_path))
    assert bad.returncode == 2


# --- cross-subcommand round trips and the no-deletion invariant ------------

def test_cli_install_then_inspect_reports_direct(tmp_path):
    # The round trip the skill's idempotency skip rule depends on: nothing else
    # proves the writer and the classifier agree on a direct install.
    env = _isolated_cli_env(tmp_path)
    install = _run(["install-statusline", "--no-self-check"], env=env)
    assert install.returncode == 0, install.stderr
    installed = json.loads(install.stdout)["new_command"]
    inspect = _run(["inspect-statusline", "--repo-root", str(tmp_path)], env=env)
    assert inspect.returncode == 0, inspect.stderr
    obj = json.loads(inspect.stdout)
    assert obj["producer_state"] == "direct"
    assert obj["status_line_command"] == installed


def test_cli_install_over_a_foreign_line_then_inspect_reports_wrapped(tmp_path):
    config = tmp_path / "cfg"
    foreign = "vim /etc/hosts"
    _seed_settings(config, {"statusLine": {"type": "command", "command": foreign}})
    env = _isolated_cli_env(tmp_path, config_dir=config)
    install = _run(["install-statusline", "--no-self-check"], env=env)
    assert install.returncode == 0, install.stderr
    inspect = _run(["inspect-statusline", "--repo-root", str(tmp_path)], env=env)
    assert inspect.returncode == 0, inspect.stderr
    obj = json.loads(inspect.stdout)
    assert obj["producer_state"] == "wrapped"
    assert obj["wrapped_command"] == foreign


def test_cli_write_opt_out_then_inspect_reports_the_marker_present(tmp_path):
    env = _isolated_cli_env(tmp_path)
    write = _run(["write-opt-out"], env=env)
    assert write.returncode == 0, write.stderr
    inspect = _run(["inspect-statusline", "--repo-root", str(tmp_path)], env=env)
    assert inspect.returncode == 0, inspect.stderr
    assert json.loads(inspect.stdout)["opt_out_marker_present"] is True


def test_cli_mutating_subcommands_delete_nothing(tmp_path):
    """Every mutating subcommand leaves pre-existing files byte-identical.

    NO source-level grep for `unlink`/`remove`/`rmtree` is added on purpose: the
    atomic-write error path legitimately unlinks its OWN temp file, so a source
    scan would either be wrong or pressure the Engineer to weaken the atomic
    write. This behavioral seed-and-compare check proves the invariant that
    matters — no pre-existing file is destroyed — without constraining how the
    write is implemented.
    """
    config = tmp_path / "cfg"
    config.mkdir()
    quorum = tmp_path / ".quorum"
    quorum.mkdir()
    sentinels = {
        quorum / f"context-usage-{TEST_SESSION_PREFIX}sentinel.json": '{"a": 1}',
        quorum / "unrelated-sentinel.txt": "keep me",
        config / "sentinel.json": "config sentinel",
    }
    for path, text in sentinels.items():
        path.write_text(text, encoding="utf-8")
    before = {path: path.read_bytes() for path in sentinels}

    env = _isolated_cli_env(tmp_path, config_dir=config)
    # A with-self-check install (fresh → installs and spawns), a --no-self-check
    # install (now already-configured), and a write-opt-out.
    assert _run(["install-statusline"], env=env).returncode == 0
    assert _run(["install-statusline", "--no-self-check"], env=env).returncode == 0
    assert _run(["write-opt-out"], env=env).returncode == 0

    for path, original in before.items():
        assert path.exists(), f"a mutating subcommand deleted {path}"
        assert path.read_bytes() == original, f"a mutating subcommand rewrote {path}"


# --- argparse surface for the mutating subcommands -------------------------

def test_cli_help_names_the_mutating_subcommands(tmp_path):
    res = _run(["--help"], env=_env_with_tempdir(tmp_path))
    assert res.returncode == 0, res.stderr
    assert "install-statusline" in res.stdout
    assert "write-opt-out" in res.stdout


def test_cli_install_statusline_unknown_flag_exits_2(tmp_path):
    res = _run(["install-statusline", "--bogus"], env=_isolated_cli_env(tmp_path))
    assert res.returncode == 2
