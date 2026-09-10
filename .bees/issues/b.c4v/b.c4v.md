---
id: b.c4v
type: bee
title: 'Dispatch shape: decide whether Blast radius and completeness evidence may travel by a durable carrier instead of inline on every dispatch'
tags:
- process
- quo-fix-issue
- quo-execute
- dispatch
status: open
created_at: '2026-09-10T19:09:44.138283'
schema_version: '0.1'
reference_materials: null
guid: c4vmqdjz62mexmtoqxjbvr8wb59oazds
---

## Description

The dispatch shape requires the Issue body verbatim, `## Blast radius` verbatim, and every round's `## Engineer's completeness evidence` verbatim on each Engineer, Code Reviewer, and PM dispatch, inline and never as a file path. On a real run that repeated roughly 5 KB of unchanged text across eleven dispatches. Correctness was fine; the cost is prompt volume in the orchestrator's context on every round.

## Expected behavior

Decide whether the relay blocks may travel through a durable carrier the orchestrator writes once (a scratch file under `<tempdir>/.quorum/`, as the compromise tracker already does) with the dispatched Agent reading it, and if so under what conditions the inline form remains required (e.g. the dispatched role has no `Read` tool, or the block is under some size). The current "inline, never as a file path" rule was chosen deliberately so a stranded proposal is re-derived before the dispatch that needs it; any change must preserve that property.

## Source

First validation run of the rewritten orchestrators (2026-09-10), defect 13. Design question; filed rather than fixed in the validation pass.

