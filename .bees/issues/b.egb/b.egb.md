---
id: b.egb
type: bee
title: 'Repo-governance hygiene: sever the dangling SDD Data models pointer in both tracker entry-shape blocks (rule 3); add the compromise tracker to CLAUDE.md''s resident illustration'
status: open
created_at: '2026-09-04T08:37:59.287911'
schema_version: '0.1'
reference_materials: null
guid: egb6ftu2zhd5iavfmhutpcp19g6k8711
---

## Description

Two small repo-governance hygiene items surfaced during the b.nn8 run, both outside that Issue's stated defect.

1. **A shipped-artifact reference to a doc section that does not exist (design rule 3).** Both orchestrators' compromise-tracker entry-shape blocks say the shape is "reproduced from the SDD Data models `#### Compromise tracker entry shape`" (`skills/quo-fix-issue/SKILL.md` Section 7.5; `skills/quo-execute/SKILL.md` Section 6.5). `docs/sdd.md` has no `## Data models` section and no such heading — the shape lives inside the b.ut9 `### Feature:` entry. This is a `skills/*` → `docs/*` reference, which dangles on a fresh install (the install copies only `skills/*` and `agents/*`), and it predates b.nn8 (it arrived with b.ut9). The shape is already fully inlined in both skills, so the reference carries nothing.
2. **This repo's `CLAUDE.md` scratch-file convention paragraph illustrates "what nothing recreates" with two residents** (the run-state manifest and the context-guard opt-out marker). After b.nn8 the README's `### Scratch files` enumerates three — the compromise tracker is appended across a run and never rebuilt, and is now written on most runs. The paragraph's operative instructions (README is the carrier; do not duplicate the note into skill prose; do not restate it as "safe to delete anytime") remain correct; the illustration is stale by omission.

## Current behavior

Two orchestrator skills point installed users at a doc heading that does not exist; the repo's governance file under-illustrates the README note it governs.

## Expected behavior

No shipped artifact references a repo-only doc section. `CLAUDE.md`'s illustration names the same residents the README does.

## Impact

Rule-3 violation in shipped prose (a reviewer criterion in `CLAUDE.md ## Review criteria for skill changes`); minor governance staleness.

## Suggested fix

- Sever the "reproduced from the SDD Data models …" phrase in both skills (one phrase each); the entry shape stays inlined. Do not create a `## Data models` section in the SDD to make the pointer resolve — that is the wrong direction.
- Add the compromise tracker to the `CLAUDE.md` scratch-file paragraph's resident illustration, matching the README's three.
- Consider extending `tests/test_shipped_artifact_portability.py` so a prose reference of the form "the SDD … `#### <heading>`" is caught even when it is not path-shaped — the current guard did not flag item 1.

## Background and rationale

Item 1 was surfaced by the b.nn8 Doc Writer and confirmed by the Doc Reviewer and PM; item 2 by the b.nn8 PM (round 4). Both were deferred because they are outside b.nn8's stated defect and `CLAUDE.md` is outside the Doc Writer's contract surface.

## Related

- b.ut9 (landed): origin of the dangling reference.
- b.nn8 (landed): made the tracker a routine resident.
- b.bq4 (landed): the shipped-artifact doc-reference review criterion this item falls under.

