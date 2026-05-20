---
id: b.tip
type: bee
title: Depth-aware finding routing and compromise tracking in /quo-fix-issue and /quo-execute
parent: null
children:
- t1.tip.bo
- t1.tip.ux
reference_materials: null
created_at: '2026-05-20T02:54:51.828615'
status: ready
schema_version: '0.1'
guid: tipnb5xhoygn81nd6fq3vui1c3ckhttn
---

Add two-dimensional finding tagging (severity + per-fix-path depth) and a session-scoped compromise tracker across the quorum review-and-routing workflow, with orchestrator-discipline rules in `/quo-fix-issue` and `/quo-execute` that fire user gates on multi-path or single-path-re-architect findings. Goal: prevent the recurring failure mode where reviewers find real issues but the orchestrator picks cheap fix paths and scope-bounds harder fixes as "out of scope" without user input, shipping compromises that accumulate as foot-guns. Substantive PRD/SDD content lives in the t1=Doc children of this Spec Bee.
