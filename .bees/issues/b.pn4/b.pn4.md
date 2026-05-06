---
id: b.pn4
type: bee
title: Document bundled-helper-script location in README's 'Where docs live' section
parent: null
created_at: '2026-05-04T16:44:54.195794'
status: done
schema_version: '0.1'
guid: pn4rmhm4ngb2n86b8zcxr4z6j61na67f
reference_materials: null
---
## Description

The README's `## Where docs live` section explains where PRD/SDD live in the target repo, but does not mention where the bees-workflow skills' bundled helper scripts (e.g., `file_list_resolver.py`, `force_clean_team.py`, `check_agent_teams.py`, `scoped_marker_resolver.py`, `detect_fast_path.py`) live. A user who hits a runtime error mentioning one of those scripts has no anchor in the README to find them.

## Current behavior

`README.md` `## Where docs live` covers only the `docs/prd.md` and `docs/sdd.md` artifacts the workflow maintains in the target repo. Bundled helper scripts are not mentioned anywhere user-facing in the README — only in `CLAUDE.md` (this repo's, contributor-facing) and in individual skill prose. If a downstream user's skill invocation surfaces an error like `helper not found: scripts/file_list_resolver.py`, they have no README anchor explaining that these scripts are resolved at runtime from each skill's own base directory (the `${SKILL_DIR}` Claude Code provides at invocation).

## What needs to change

Add a short paragraph (3-5 sentences) to README.md `## Where docs live` (or a small new subsection — author's call) noting:

- Skills bundle helper scripts under `skills/<skill-name>/scripts/`.
- Each skill resolves its own bundled scripts at runtime from its own base directory; users do not need to configure absolute paths.
- The earlier `## Skill Paths` section in CLAUDE.md was removed because per-machine paths could not be committed safely; that's why the skills now self-resolve.

Doc-only change. Single file (`README.md`). No source code, no helper scripts, no skill prose, no SDD touched.

## Acceptance criteria

- README.md has a short paragraph (or subsection) covering the bundled-helper-scripts location and self-resolution behavior.
- Wording is project-neutral and consistent with the rest of the README's voice.
- No other files modified.
