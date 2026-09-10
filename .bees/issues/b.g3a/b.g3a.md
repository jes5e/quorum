---
id: b.g3a
type: bee
title: 'quo-setup gauge-producer step: add a branch for a reading present but no recognised producer'
tags:
- quo-setup
- context-guard
status: open
created_at: '2026-09-10T19:09:40.339530'
schema_version: '0.1'
reference_materials: null
guid: g3ag1fzokczj2ig1m3qnbgx9i98hy8q7
---

## Description

`/quo-setup`'s gauge-producer step has no branch for "a reading exists but the inspector recognises no producer". On a real run the `inspect-statusline` inspector reported `producer_state: absent` and flagged the project-level `statusLine` as a higher-precedence source, yet a gauge file for the current session already existed under `<tempdir>/.quorum/`. Something publishes readings the inspector does not recognise, and the gate fires as if no producer exists.

## Expected behavior

The inspector (or the skill step that consumes it) gains a branch for "reading present, producer unknown": report that a reading is being produced by an unrecognised source, do not fire the configure-now gate as if nothing publishes, and tell the operator which settings file carries the higher-precedence `statusLine` so they can decide whether to leave it.

## Source

First validation run of the rewritten orchestrators (2026-09-10), Event Consumer Service repo, defect 3 in the run's report. Not an orchestrator defect; `/quo-setup` and `context_gauge.py` are the owners.

