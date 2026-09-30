---
id: b.21d
type: bee
title: Deferral hygiene's Encode still offers a PRD/SDD destination that nothing writes (dead end since b.sb7)
status: open
created_at: '2026-09-30T11:52:08.040312'
schema_version: '0.1'
reference_materials: null
guid: 21d2tjibqmm1jydvpdt4ce19gqchkyr5
---

## Description

The deferral-hygiene **Encode in existing ticket** branch still lists "the project PRD/SDD via a doc-writer pass" as a destination. It appears in `/quo-execute` §9, `/quo-fix-issue` §9, `agents/analyst.md`, and `agents/pm.md`, and the pinned helper literal `[--doc-path <abs-path> ...]` goes with it. Since b.sb7 (`dfc16d9`) nothing writes the PRD, and deferred work in the SDD is history under the Doc Writer's ownership table. The destination now contradicts both, and no rule dispatches the "doc-writer pass" it names, so it is a dead end.

## Suggested fix

Remove the PRD/SDD destination and the `--doc-path` literal from the §9 helper invocations (both bodies, a mirrored edit), from `agents/analyst.md` and `agents/pm.md`, and from the helper's docstring (the flag can stay inert). Deferred work goes to tickets only. Update the two pinned test literals. Small; no run has used the destination.

## Origin

Found during b.sb7 (2026-09-30), declined there as out of that build's scope.

