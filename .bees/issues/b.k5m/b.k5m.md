---
id: b.k5m
type: bee
title: 'quo-setup: delete or script the dead Skill Paths migration (inlined multi-line python -c for a section removed at b.963)'
status: open
created_at: '2026-09-11T01:35:05.736548'
schema_version: '0.1'
reference_materials: null
guid: k5m1d11nr73g8ncwvqytcprwimzfxgti
---

## Description

`skills/quo-setup/SKILL.md` lines 285–368 carry a `## Skill Paths` migration: a ~30-line Python program inlined via `python3 -c '…'` and again as a PowerShell here-string, about 750 words. It migrates a CLAUDE.md section (`## Skill Paths`) that was removed at b.963 because committing per-machine paths broke multi-engineer collaboration. The multi-line `-c` shape is one CLAUDE.md `## Bash etiquette in this repo` explicitly forbids, and `/quo-setup` is the skill most likely to run in a fresh repo where every permission prompt fires.

## Current behavior

Every `/quo-setup` run carries the inlined migration program in its context. On a repo that still has a `## Skill Paths` section, the skill instructs the model to run a multi-line inline Python program in a shell.

## Expected behavior

Either the migration is one sentence — "if CLAUDE.md still carries a `## Skill Paths` section, delete it with the Edit tool" — or its logic moves into `skills/quo-setup/scripts/detect_fast_path.py` as a `--migrate-skill-paths` mode invoked as one literal command. Estimated saving ~650 words and the removal of a Bash-etiquette violation from the first skill a new user runs.

## Suggested fix

Hand edit with a cold review. Risk is very low: the behavior is either preserved by the helper or trivially performed by the model with `Edit`. The README's `## Install` section should be checked for any mention of the migration.

## Background and rationale

Surfaced by the prose-size research the operator requested on 2026-09-11. `quo-setup` is otherwise the healthiest of the large bodies (about 66% executable instruction, 2% duplication); this dead migration is its one clear cut.

