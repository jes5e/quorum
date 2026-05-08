---
id: b.mak
type: bee
title: Rename and lock down the three review skills
parent: null
children:
- t1.mak.eo
- t1.mak.su
- t1.mak.84
- t1.mak.ka
reference_materials:
- value: b.mam
  resolver: bees
created_at: '2026-05-07T15:55:55.685316'
status: done
schema_version: '0.1'
guid: makws6n46k6383scek8zbn92mq6ydunn
---

# Rename and lock down the three review skills

Rename `bees-{code,test,doc}-review` → `bees-{engineer,test-writer,doc-writer}-review` and remove their standalone-use story so agents in fresh sessions stop mis-invoking them on generic review prompts. PRD (`t1.mam.qr`) and SDD (`t1.mam.a2`) live under Spec Bee `b.mam` (referenced via `reference_materials`). Decomposed into four Epics: skill internals, callers, top-level docs, ticket sweep + verification — Epics 1 and 2 share one git commit; Epics 3 and 4 each get their own.

## Anticipated doc impact

Per the SDD's `## Documentation` section, the doc updates ARE the work itself (Epic 3); no separate post-implementation doc-writer pass is required. The cumulative project docs that get updated are:

- `Customer-facing docs` — `README.md` (skill catalog rows + dual-mode paragraph deletion).
- `Engineering best practices` — `CONTRIBUTING.md` (install-loop entries, rejected-suggestion note, and the rewrite of the "Status / type renames history" entry).
- `Internal architecture docs (SDD)` — `docs/sdd.md` (skill descriptions, agent/role mapping table, time-bounded review iteration prose).
- `Project requirements doc (PRD)` — `docs/prd.md` (parallel-review-skill discussion).
- *This repo's `CLAUDE.md`* — review-criteria layered-on-top section.
