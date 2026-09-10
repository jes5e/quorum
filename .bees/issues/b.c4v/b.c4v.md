---
id: b.c4v
type: bee
title: 'Dispatch shape: decide whether Blast radius and completeness evidence may travel by a durable carrier instead of inline on every dispatch'
tags:
- process
- quo-fix-issue
- quo-execute
- dispatch
parent: null
reference_materials: null
created_at: '2026-09-10T19:09:44.138283'
status: open
schema_version: '0.1'
guid: c4vmqdjz62mexmtoqxjbvr8wb59oazds
---

## Description

The dispatch shape requires the Issue body verbatim, `## Blast radius` verbatim, and every round's `## Engineer's completeness evidence` verbatim on each Engineer, Code Reviewer, and PM dispatch, inline and never as a file path. On a real run that repeated roughly 5 KB of unchanged text across eleven dispatches. Correctness was fine; the cost is prompt volume in the orchestrator's context on every round.

## Expected behavior

Decide whether the relay blocks may travel through a durable carrier the orchestrator writes once (a scratch file under `<tempdir>/.quorum/`, as the compromise tracker already does) with the dispatched Agent reading it, and if so under what conditions the inline form remains required (e.g. the dispatched role has no `Read` tool, or the block is under some size). The current "inline, never as a file path" rule was chosen deliberately so a stranded proposal is re-derived before the dispatch that needs it; any change must preserve that property.

## Source

First validation run of the rewritten orchestrators (2026-09-10), defect 13. Design question; filed rather than fixed in the validation pass.

## Note from b.sb7 (2026-09-10)

b.sb7 (internal docs as map + register) adds a third relay row to the §5 dispatch tables: `## Ratified decisions`, carrying exactly one section verbatim (`### Policy decisions this change implies` in fix mode; the spec's `## Decisions and rejected alternatives` in execute mode) to Doc Writer, Doc Reviewer, and PM, and adds the Doc Writer to the existing `## Blast radius` row's recipients. Any decision here about moving `## Blast radius` or completeness evidence to a durable carrier instead of inline relay applies to `## Ratified decisions` the same way; the heading name is fixed by b.sb7 and any later relay of that section reuses it rather than introducing a second name.

