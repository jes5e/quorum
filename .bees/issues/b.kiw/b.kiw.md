---
id: b.kiw
type: bee
title: /quo-status suggests /quo-execute [issue-id]; execute takes no Issue IDs
status: open
created_at: '2026-09-27T14:04:51.292568'
schema_version: '0.1'
reference_materials: null
guid: kiwfmw8yksay89aaoqsmamjgq4f6mvbr
---

## Description

`skills/quo-status/SKILL.md` (around line 113) suggests running `/quo-execute [issue-id]`, but `/quo-execute` takes a Bee ID or an Epic ID, never an Issue ID; Issues are fixed with `/quo-fix-issue`. A pre-existing error, found during the b.87t rebuild.

## Suggested fix

Point the suggestion at `/quo-fix-issue <issue-id>` for Issues (and `/quo-execute <bee-id>` for Plan Bees). A bounded prose fix; suitable for a `/quo-fix-issue` run.

