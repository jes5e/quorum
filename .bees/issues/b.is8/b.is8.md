---
id: b.is8
type: bee
title: SR-4.6 recovery gate has no 'ship an enumerated path now' choice; its interplay with the disposition gate is unstated
status: open
created_at: '2026-09-15T19:06:49.262222'
schema_version: '0.1'
reference_materials: null
guid: is8fh7w6yyj4vj2xve7wux1w7sk7dznv
---

## Description

The SR-4.6 under-enumeration recovery gate in `/quo-fix-issue` and `/quo-execute` §11 offers `File follow-up Issue to surface the missing path`, `Accept the under-enumeration and proceed`, and `Pause to discuss`. It has no option for "ship one of the reviewer's enumerated paths now". The b.pkn validation run (event_consumer_service, 2026-09-15) reached that case and had to combine the disposition gate's `Fix in this session` with SR-4.6's `Accept` to get there; the relationship between the two gates when a fix path is shipped is not stated.

## Expected behavior

Either SR-4.6 gains a fourth choice, `Ship path (x) now`, whose branch dispatches the implementer per §11 step 6 and appends Trigger D, or §11 step 5 states that the disposition gate's `Fix in this session` subsumes the recovery gate when the operator ships an enumerated path, and says which Trigger D append results. Either way the two gates' interplay is stated once.

## Suggested fix

Gate-option change, so a design decision: file-and-review before any edit. Same recorded literals must land byte-identically in both bodies (Tier-1 gate labels are pinned by `tests/test_orchestrator_structure.py`) and Trigger D's `Decision` strings in §10 must stay in step. Surfaced by the b.pkn report, item 6.

