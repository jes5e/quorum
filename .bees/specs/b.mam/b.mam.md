---
id: b.mam
type: bee
title: Rename and lock down the three review skills
parent: null
children:
- t1.mam.qr
- t1.mam.a2
reference_materials: null
created_at: '2026-05-07T14:15:38.582997'
status: ready
schema_version: '0.1'
guid: mamqzk1s872wcknwzgxybjbnm7habad8
---

# Rename and lock down the three review skills

Rename `bees-{code,test,doc}-review` → `bees-{engineer,test-writer,doc-writer}-review` and remove their standalone-use story so agents in fresh sessions stop mis-invoking them on generic review prompts. PRD and SDD live in this Spec Bee's `t1=Doc` children.
