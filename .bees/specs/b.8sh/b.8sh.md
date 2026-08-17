---
id: b.8sh
type: bee
title: Context-window guard for long orchestrator runs
parent: null
children:
- t1.8sh.c4
- t1.8sh.cg
reference_materials: null
created_at: '2026-08-16T17:12:53.108268'
status: ready
schema_version: '0.1'
guid: 8shmyjwzgfv84zap52afpdr86bjg6q4x
---

Spec Bee for the **context-window guard** feature: a producer/consumer mechanism that lets the orchestrator skills (`/quo-execute`, `/quo-breakdown-epic`, `/quo-fix-issue`) stop gracefully at an Epic/Issue boundary before Claude Code's auto-compaction fires on long boundary-crossing runs. A statusline-fed per-session gauge file supplies the context-usage reading the model cannot obtain natively; the skills read it at boundaries and hard-stop (recommending a fresh session) when usage nears the compaction threshold.

The authoritative PRD and SDD live in this Spec Bee's `t1=Doc` children. Sequenced to land after the foundation defect-fix Issue b.ja9 (honesty rewrite of the Epic-boundary discipline); upstream simplifications tracked in b.cj2.
