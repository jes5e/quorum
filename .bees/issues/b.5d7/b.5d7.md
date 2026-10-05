---
id: b.5d7
type: bee
title: '/quo-status decision tree: rule order hides open Issues after a finished Plan Bee and sends new users to hand-write specs'
status: open
created_at: '2026-10-04T20:37:32.995531'
schema_version: '0.1'
reference_materials: null
guid: 5d7fjueme84cqjwxwsahn57322w5179q
---

## Description

`/quo-status`'s decision tree (`### 5. Decision Logic`, "first match wins") orders its rules so that some correct suggestions never appear. Found by small batch 1's cold review (2026-10-04) while fixing b.kiw. It is pre-existing, and no run has shown it yet.

## Current behavior

- **Rule 7 masks rule 8.** "All Epics are `done`" matches before "Issue Bees open", so once a Plan Bee is finished, open Issues are never suggested.
- **Rule 2 comes before rule 3.** "No specs found → Write PRD and SDD" fires first, so a new user is told to hand-write specs instead of being pointed at `/quo-plan`, which authors them.
- The stage table omits the Specs hive.

## Expected behavior

The suggestions reflect everything actionable: open Issues are suggested whatever the Plan Bees' state, and a repo without specs is pointed at `/quo-plan` (or `/quo-plan-from-specs` when specs exist on disk).

## Suggested fix

Reorder or merge the rules (for example, report open Issues alongside any Plan Bee suggestion), and add the Specs hive to the stage table. A small prose fix to one skill. Low priority: `/quo-status` is advisory and rarely used.

