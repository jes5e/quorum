---
id: b.mnr
type: bee
title: Add pytest unit tests for the three helper scripts
status: open
created_at: '2026-06-23T20:58:59.774864'
schema_version: '0.1'
reference_materials: null
guid: mnr9fxbp2b94nbyeb6cy5iqqzihdpcqa
---

## Description
The repo ships three live Python helper scripts but has zero automated test coverage for them. Add a `pytest` unit-test suite (top-level `tests/`) covering `scoped_marker_resolver.py`, `detect_fast_path.py`, and `hive_commit.py`, and wire it into CLAUDE.md's `## Build Commands` `Narrow test` / `Full test` keys (currently `echo 'no test suite for this repo'`).

Scope is **Tier 1 only** — unit tests for the scripts. An invariant/contract linter over the skill/agent prose ("Tier 2") was considered and explicitly dropped this round.

## Current behavior
- `Narrow test` / `Full test` are stubs (`echo 'no test suite for this repo'`), so pointing `/quo-execute` at this repo no-ops its test-writer / test-reviewer roles.
- The three scripts are pure-stdlib and deterministic but unguarded; edge cases and load-bearing invariants documented in their own docstrings can regress silently under prose-driven edits.

## Expected behavior
`pytest` run from the repo root discovers and passes a suite covering, at minimum:
- **scoped_marker_resolver.py** — marker match / malformed / absent discrimination (`find_marker`); subsection-extraction boundaries (`extract_subsection`); the `" and "` PRD/SDD separator ambiguity; missing-file, missing-heading, and empty-title failure exits (exit 2); UTF-8 BOM handling.
- **detect_fast_path.py** — `_glob_to_regex`; `scope_covers` including the Windows backslash-separator handling (testable POSIX-side, pure string work); fence-aware `_split_top_level_sections`; `_parse_keyed_bullets`; and the `fast_path_eligible` boolean incl. the superset-not-subset canonical-hive rule and the empty-`Compile/type-check` exception.
- **hive_commit.py** — `resolve_hive_paths` JSON parsing (incl. malformed / non-zero-exit / missing-binary -> None); and the encode-commit invariants against a throwaway temp git repo with a stub `bees` on PATH: no `git add -A`, no empty commit, exact commit-subject string, `--doc-path` existence check, plus the non-mutating `resolve-hive-paths` query mode.

CLAUDE.md `Narrow test` / `Full test` invoke the suite; CONTRIBUTING.md notes how to run it.

## Impact
Correctness / maintainability. No automated regression net today for the only executable code in the repo. The same wiring fixes a real workflow gap — quorum can't dogfood its own `/quo-execute` test cycle while the test command is a stub.

## Suggested fix
- Add top-level `tests/` (outside `skills/`, so design-rule-3 prose-neutrality is untouched — test code is repo infrastructure, free to reference this repo's paths).
- Use `pytest`; import script functions by file path (the scripts are single-file CLIs, not an importable package) and exercise CLI contracts via subprocess. Stub `bees` and a temp git repo for `hive_commit.py`'s mutating paths.
- Update CLAUDE.md `## Build Commands` `Narrow test` (narrow/changed-file scope) and `Full test` (whole suite) to invoke `pytest`; add a one-line bootstrap note (`pip install pytest`; also `pyflakes` for the existing `Lint` key — neither is currently installed).
- Stdlib + `pytest` only; no other new deps.

## Background and rationale
The three scripts' docstrings already enumerate the exact edge cases and invariants worth pinning (the `" and "` separator split, the superset-vs-subset hive rule, the empty-`Compile/type-check` allowance, the load-bearing commit-subject string with its em-dash). That makes them high-value, low-flakiness test targets. The deleted `ticket_backend.py` / `encode_deferral_commit.py` are out of scope — sources are gone, only stale gitignored `.pyc` remain.

## Decisions and rejected alternatives
- **Tier 2 invariant/contract linter — dropped this round.** Of six proposed checks, three were high-confidence (frontmatter validity, contract-key pinning, README-table<->filesystem catalog), but two were assessed as likely-flaky or outright wrong: a bash-etiquette forbidden-shape grep would flag skills' own intentional template snippets (e.g., `quo-plan/SKILL.md` deliberately contains `$(...)` + pipes), and POSIX/PowerShell shell-block pairing has no clean count/adjacency heuristic (quo-plan has 14 bash vs 12 powershell blocks). User opted for the high-confidence unit-test layer only.
- **pytest over stdlib `unittest`** — chosen for fixture ergonomics (`tmp_path`, `monkeypatch`); accepted as the single new dev dependency.
- **Top-level `tests/` over co-locating in `skills/<name>/`** — co-location would entangle test code with prose-neutral skill dirs.
- **Excluded:** behavioral/eval testing of skill execution, LLM-as-judge evals, testing the `bees` CLI itself, and CI/Actions wiring (possible follow-up).

