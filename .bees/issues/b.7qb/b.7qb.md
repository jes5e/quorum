---
id: b.7qb
type: bee
title: 'This repo''s own docs/sdd.md and docs/prd.md: per-repo cleanup to the Doc Writer''s table and the PRD row'
status: open
created_at: '2026-10-04T20:37:35.113246'
schema_version: '0.1'
reference_materials: null
guid: 7qbhirvqhynxzbduri5xwgzxct3bjdnq
---

## Description

This repo's own `docs/sdd.md` and `docs/prd.md` have not had the per-repo cleanup that b.sb7 (SDD) and b.dh9 (PRD) leave to each repo. They still carry per-feature `### Feature:` sections, history, and some false statements.

## Known false statements

- `docs/prd.md` `:11` and `:15` say cumulative PRD/SDD entries "are appended post-implementation by the `doc-writer` agent". b.sb7 retired that (found by small batch 1's cold review, 2026-10-04).

## Expected behavior

- `docs/prd.md` holds only the PRD row: goals, non-goals, product-level targets, and promises with pointers to the SDD.
- `docs/sdd.md` holds only what the Doc Writer's table puts in the SDD: where things are, guarantees, cross-module rules, the client contract, and decisions with their rejected alternatives.
- History moves to the tickets and commits that already hold it.
- The feature-entry records written by recent batches (b.sb7, b.dh9, b.gmg) shrink to the rules and decisions they carry.

## Notes

- Same shape as live_edit's cleanups. Never lose a fact: check that each one lives elsewhere before deleting it.
- Coordinate with item 12a (`/quo-plan-from-specs --feature` parses `### Feature:` sections). This repo's docs are not planning input, so the cleanup does not depend on it.
- `docs/inventory/` is the orchestrators' rewrite record and is out of scope.

