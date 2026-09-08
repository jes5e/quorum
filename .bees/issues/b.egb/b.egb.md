---
id: b.egb
type: bee
title: 'Repo-governance hygiene: sever the dangling SDD Data models pointer in both tracker entry-shape blocks (rule 3); add the compromise tracker to CLAUDE.md''s resident illustration'
parent: null
reference_materials: null
created_at: '2026-09-04T08:37:59.287911'
status: open
schema_version: '0.1'
guid: egb6ftu2zhd5iavfmhutpcp19g6k8711
---

## Description

Three small repo-governance hygiene items surfaced during the b.nn8 run, all outside that Issue's stated defect.

1. **A shipped-artifact reference to a doc section that does not exist (design rule 3).** Both orchestrators' compromise-tracker entry-shape blocks say the shape is "reproduced from the SDD Data models `#### Compromise tracker entry shape`" (`skills/quo-fix-issue/SKILL.md` Section 7.5; `skills/quo-execute/SKILL.md` Section 6.5). `docs/sdd.md` has no `## Data models` section and no such heading — the shape lives inside the b.ut9 `### Feature:` entry. This is a `skills/*` → `docs/*` reference, which dangles on a fresh install (the install copies only `skills/*` and `agents/*`), and it predates b.nn8 (it arrived with b.ut9). The shape is already fully inlined in both skills, so the reference carries nothing.
2. **This repo's `CLAUDE.md` scratch-file convention paragraph illustrates "what nothing recreates" with two residents** (the run-state manifest and the context-guard opt-out marker). After b.nn8 the README's `### Scratch files` enumerates three — the compromise tracker is appended across a run and never rebuilt, and is now written on most runs. The paragraph's operative instructions (README is the carrier; do not duplicate the note into skill prose; do not restate it as "safe to delete anytime") remain correct; the illustration is stale by omission.
3. **`docs/sdd.md`'s Epic-boundary checkpoint entry undercounts its invokers.** The sentence "Section 4.2 enumerates the **five** paths that invoke it by name" predates b.pdq's `##### Aborted-run close-out`, which `skills/quo-execute/SKILL.md` Section 4.2 now names as a further invoker on the run-aborting path ("as does `##### Aborted-run close-out` below"). The count drifted at b.pdq, not at b.nn8, which only re-keyed what selects between the close-out's two shapes (recorded correctly in the b.pdq entry's supersession note). Correct the count or annotate the sentence.

## Current behavior

Two orchestrator skills point installed users at a doc heading that does not exist; the repo's governance file under-illustrates the README note it governs; the SDD's checkpoint entry names five invokers where the skill names six.

## Expected behavior

No shipped artifact references a repo-only doc section. `CLAUDE.md`'s illustration names the same residents the README does. The SDD's invoker count matches Section 4.2.

## Impact

Rule-3 violation in shipped prose (a reviewer criterion in `CLAUDE.md ## Review criteria for skill changes`); minor governance staleness; one stale count in the SDD.

## Suggested fix

- Sever the "reproduced from the SDD Data models …" phrase in both skills (one phrase each); the entry shape stays inlined. Do not create a `## Data models` section in the SDD to make the pointer resolve — that is the wrong direction.
- Add the compromise tracker to the `CLAUDE.md` scratch-file paragraph's resident illustration, matching the README's three.
- Correct "five" to the current invoker count in `docs/sdd.md`'s Epic-boundary checkpoint entry, or annotate it as superseded by b.pdq's close-out invoker.
- Consider extending `tests/test_shipped_artifact_portability.py` so a prose reference of the form "the SDD … `#### <heading>`" is caught even when it is not path-shaped — the current guard did not flag item 1.

## Background and rationale

Item 1 was surfaced by the b.nn8 Doc Writer and confirmed by the Doc Reviewer and PM; item 2 by the b.nn8 PM (round 4); item 3 by the b.nn8 post-completion Doc Reviewer (round 17), who confirmed it drifted at b.pdq. All three were deferred because they are outside b.nn8's stated defect (and `CLAUDE.md` is outside the Doc Writer's contract surface).

## Related

- b.ut9 (landed): origin of the dangling reference.
- b.pdq (landed): origin of the checkpoint-invoker count drift.
- b.nn8 (landed): made the tracker a routine resident.
- b.bq4 (landed): the shipped-artifact doc-reference review criterion this item falls under.

