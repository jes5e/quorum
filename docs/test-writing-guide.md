# Test writing guide

How to write and review tests for this repo's own artifacts — the bundled Python helper scripts under `skills/*/scripts/`, plus the structural invariants of the skill and role markdown. There is no application package; the suite exists to pin the helpers' CLI contracts and those structural invariants. The existing modules under `tests/` are the idiom of record: when this guide and a well-established pattern in those modules disagree, match the modules and file an issue against this guide.

## Scope: helpers and structural invariants only

Tests here cover two things and nothing else:

1. **Python helpers** — every module under `skills/*/scripts/`, through the two-layer pattern below.
2. **Structural invariants of shipped markdown** — properties a test can check without quoting a sentence: a heading or label anchor is present in the files that emit and consume it; two sections the mirror map declares identical are byte-identical (or identical after a declared token substitution); a body is within its line cap and its first sections sit within the first 150 lines; a gate's choice labels appear verbatim; no shipped artifact cites a repo-only document. `tests/test_orchestrator_structure.py` and `tests/test_shipped_artifact_portability.py` are the models.

**Pinning prose sentences is out of scope.** A test that asserts a sentence of skill or role prose is present freezes wording, not behavior, and turns every rewording into a test edit; the six retired prose-pin modules were replaced for that reason. Key an assertion on a heading, a label, a fixed line a consumer parses, a file name, a command, or an enum value — never on a sentence of explanation.

## Setup

Install the dev toolchain from the pinned manifest: `python -m pip install -r requirements-dev.txt` (see CONTRIBUTING.md `## Running the tests` for the PEP 668 caveat). The commands to run come from CLAUDE.md `## Build Commands`: `Narrow test` / `Full test` (`python -m pytest tests/`) and `Lint` (`python -m pyflakes skills/*/scripts/*.py`). The Lint glob covers only helper scripts — additionally run pyflakes over any test file you touch.

## The two-layer pattern

Every helper's test module has two layers; new modules must carry both.

1. **Unit layer** — load the helper in-process via `conftest.load_script(<RELPATH_CONSTANT>)` and call its pure functions directly. `load_script` imports by file path with a unique module name, so helpers that are not packages (no `.py`-importable location) still get real in-process coverage.
2. **CLI-contract layer** — run the script as a subprocess via `conftest.script_path(<RELPATH_CONSTANT>)`: `subprocess.run([sys.executable, str(SCRIPT), *args], input=..., capture_output=True, text=True, env=...)`, asserting on `returncode`, `stdout`, and `stderr`. This is the layer that pins the exit-code and output contract other skills consume.

Register each helper exactly once in `tests/conftest.py` as a repo-root-relative constant (`DETECT_FAST_PATH`, `SCOPED_MARKER_RESOLVER`, `HIVE_COMMIT`, ...) and import it from there — never hardcode a script path inside a test module.

## Fixtures and isolation rules

- **`tmp_path` for all file I/O.** No test writes to the repo tree or the real tempdir. Unit-layer code that resolves `tempfile.gettempdir()` gets redirected with `monkeypatch.setattr(mod.tempfile, "gettempdir", ...)` — always via `monkeypatch` (auto-undone), never a bare assignment, because `mod.tempfile` is the shared stdlib module object and a leaked patch is process-global.
- **Copied env for subprocesses.** CLI-layer invocations that could write pass a copied `os.environ` with `TMPDIR`, `TEMP`, and `TMP` all pointed at `tmp_path` (platforms consult different variables).
- **Stub executables, not system tools.** When a helper shells out, stub the callee with a small Python file written under `tmp_path` and invoked via `sys.executable` (see `test_hive_commit.py`'s stub-`bees` technique) — never depend on `echo`, `git`, or another system binary being present or behaving identically across OSes. In-process, monkeypatch `mod.subprocess.run` with a fake `CompletedProcess` stub.
- **No sleeping.** Time-dependent behavior takes an injectable `now` (unit layer) or ages files with `os.utime` (CLI layer).
- **Scratch-file convention applies to tests too.** Anything a test deliberately leaves outside pytest-managed temp roots goes under `<tempdir>/.quorum/` and is never deleted by the test (CLAUDE.md `## Scratch-file convention`).

## What to cover

- Every exit code the helper's contract documents, including the `fail()` → exit-2 convention and argparse usage errors normalized to 2.
- Every distinct stdout vocabulary value a consumer branches on — one named test per value, plus a distinctness assertion when collapsing two values would silently change consumer routing.
- Idempotency / overwrite semantics where the contract claims them (e.g., assert a second write truncates rather than appends by checking byte length shrinks).
- The negative space: inputs the helper must treat as no-ops or reject, not just the happy path.

## Reviewing tests

A test review checks, in order: (1) both layers present and each asserting the contract, not the implementation; (2) isolation — no real-tempdir writes, no un-monkeypatched global patches, no system-binary dependencies, no sleeps; (3) coverage of every documented exit code and output value, with at least one test that fails if a contract value is renamed or two values are collapsed; (4) assertions that are exact (`stdout == "stale"`) rather than substring-loose, except where the contract itself is loose; (5) no weakening of an assertion to make a shipped defect pass — a helper bug is surfaced to its owner, never encoded into the suite.
