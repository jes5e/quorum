---
id: b.d8n
type: bee
title: Simplify the context-window guard
parent: null
children:
- t1.d8n.9g
- t1.d8n.nd
reference_materials: null
created_at: '2026-09-02T22:56:10.173854'
status: ready
schema_version: '0.1'
guid: d8nm3nzgvrxefhoug7vya5kzhqaa71w7
---

Spec Bee for **simplifying the context-window guard** shipped by Plan b.55r (Spec Bee b.8sh). The guard's core — the status-line producer, the per-session gauge-file contract, `read`'s four-value vocabulary, stale-means-stop, and the `stop-threshold` seam — stays; the apparatus around it is reduced: the missing-reading hard-stop gate and persistent opt-out marker become a one-line fail-open notice, the three duplicated guard sections in `/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` collapse into one shared procedure file read lazily at the boundary, the stop threshold is re-anchored on the measured auto-compaction trigger and instrumented via per-boundary readings in the run-state manifest, and the triplicated contract docs are trimmed.

PRD and SDD live as `t1=Doc` children of this Spec Bee. Sequenced after Issues b.pdq, b.q3f, b.nn8, and b.y2q land and `fix/b.ja9` is merged to `main`.
