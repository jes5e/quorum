---
id: b.kiw
type: bee
title: /quo-status suggests /quo-execute [issue-id]; execute takes no Issue IDs
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:51.292568'
status: done
schema_version: '0.1'
guid: kiwfmw8yksay89aaoqsmamjgq4f6mvbr
---

## Description

`skills/quo-status/SKILL.md` (around line 113) suggests running `/quo-execute [issue-id]`, but `/quo-execute` takes a Bee ID or an Epic ID, never an Issue ID; Issues are fixed with `/quo-fix-issue`. A pre-existing error, found during the b.87t rebuild.

## Suggested fix

Point the suggestion at `/quo-fix-issue <issue-id>` for Issues (and `/quo-execute <bee-id>` for Plan Bees). A bounded prose fix; suitable for a `/quo-fix-issue` run.
## Closed (2026-10-04)

Fixed in small batch 1, merged to main by fast-forward, head `cc319f3`, not pushed. `/quo-status` now suggests `/quo-fix-issue <issue-id>` for open Issues and `/quo-execute <bee-id>` for Plan Bees. The cold round checked every suggestion in its decision tree against the target skill's arguments. The tree's rule order, which the round also noticed, is filed separately.
