---
id: b.gar
type: bee
title: Test strategy for the skills repo
parent: null
children:
- t1.gar.9u
- t1.gar.hc
- t1.gar.y1
created_at: '2026-05-02T14:35:15.596968'
status: ready
schema_version: '0.1'
guid: gar4i66e8qut657irna2i8ate97b4hjq
reference_materials:
- value:
  - /Users/jesseg/code/bees-workflow/docs/prd.md
  - /Users/jesseg/code/bees-workflow/docs/sdd.md
  resolver: file_list_resolver
---
The Ephemeral-Agent Orchestration rewrite (parent Bee `b.5tm`) has shipped on `main`. The bees-workflow repo is now a bees-only project running on top of Claude Code's stable `Agent` tool; the abandoned beads-backend feature (Plan Bee `b.9xr`) remains paused, and the dispatcher seam (`ticket_backend.py`) it would have introduced does not exist on `main`. This body re-scopes `b.gar` for that bees-only world.

## Goal

Add a layered automated-testing approach for the bees-workflow repo itself, replacing the current single-check `python -m pyflakes` floor. The goal preserved from the original framing: catch the failure modes that actually bite (helper bugs, design-rule drift in skill prose) cheaply, without trying to fully test prose-driven LLM workflows.

## Layered approach (bees-only re-statement)

**Layer 1 — Helper unit tests.** Per-helper pytest unit tests on every bundled Python helper. Today the bundled helpers are:

- `skills/bees-setup/scripts/file_list_resolver.py` (the egg resolver)
- `skills/bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection)
- `skills/bees-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser/scoper)

Tests use pytest's `tmp_path` for filesystem isolation and `monkeypatch` for environment overrides. Coverage targets every public function, every error path, and every JSON contract field. Entrypoint: `pytest skills/`.

**Layer 2 — Structural SKILL.md linter.** A `tools/lint_skills.py` script (Python 3, no third-party deps) walks every `skills/*/SKILL.md`, parses YAML frontmatter, and asserts the project's design rules baked into CLAUDE.md:

- Rule 1 (language-agnostic): no hardcoded language-specific commands, file extensions, or manifest filenames in skill prose.
- Rule 2 (POSIX + Windows PowerShell): every fenced code block tagged `bash` (or labeled "POSIX") has a sibling block tagged `powershell` (or labeled "Windows") in the same section, and vice versa. No bash-only fallbacks.
- Rule 3 (project-neutral): no path starting with `/Users/`, `/home/`, or `C:\Users\`; no references to this repo's specific ticket IDs or internal workflow specifics.
- Scratch-file convention: any `--body-file` (or similar) scratch path lives under `<tempdir>/.bees-workflow/`, includes the create-if-absent step (`mkdir -p` / `New-Item -ItemType Directory -Force`), and does not instruct callers to delete the file afterward.
- Bundled-script references resolve from each skill's own base directory at runtime (no committed absolute paths).

Output is human-readable: `<file>:<line>: <rule>: <message>`. Exits non-zero on any rule violation. Entrypoint: `python tools/lint_skills.py`.

**Layer 2.5 — Backend-equivalence harness: deferred.** There is no second backend on `main` to validate against. The dispatcher seam (`ticket_backend.py`) and the bees+beads adapter pair were abandoned with the beads branch and are not coming back under this Plan Bee. If `b.9xr` ("Optional beads backend") ever resumes, Layer 2.5 comes back into scope at that point and `b.gar` can re-add the dependency; until then, this layer is out of scope.

**Layer 3 — Live Claude Code end-to-end smoke harness.** Out of scope, as in the original framing. May ship later as a separate Plan Bee.

## Top-level entrypoint

All in-scope layers (1 and 2) wire to a single `make test` target at the repo root, with a `tools/run_tests.py` Python fallback for Windows contributors without `make`. CLAUDE.md gains a contributor-facing `## Test Commands` section documenting the entrypoints; README's Contributing section gains a short paragraph naming the layers and pointing at `make test`. CI runs `make test` on every push and PR.

## Canonical spec source

Full scope, motivation, acceptance criteria, and architecture live in:

- `docs/prd.md` `### Feature: Test strategy for the skills repo`
- `docs/sdd.md` `### Feature: Test strategy for the skills repo`

Both are linked via this Bee's `egg`. Those subsections currently carry `**Status: paused as of 2026-05-03.**` prefixes whose narrative points at this body update as the bees-only re-scoping landing site; sibling Task 4 of the parent Epic (`t1.5tm.fy`) cleans those prefixes up immediately after this body lands. The spec subsections themselves still describe the originally-planned dual-backend Layer 2.5 architecture and will be re-scoped to match this body when the paused-prefix cleanup runs.

## Status

`b.gar` is no longer blocked. With Layer 2.5 deferred and the dual-backend seam gone, nothing in the refreshed scope depends on `b.9xr`'s state. A future `/bees-breakdown-epic b.gar` can run against `main` at any time and decompose against Layers 1 and 2 directly.

