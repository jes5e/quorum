---
id: b.q83
type: bee
title: Auto-detect URLs in /quo-file-issue and /quo-fix-issue
parent: null
children:
- t1.q83.qb
- t1.q83.a4
reference_materials: null
created_at: '2026-05-08T15:50:25.050304'
status: ready
schema_version: '0.1'
guid: q83odfvqnhv4z9amgz9dvufh7np2rxky
---

Drop the `--reference` / `--from-github` flag requirement: when a positional argument starts with `http://` or `https://`, the skill auto-routes to external-reference mode. `/quo-fix-issue` gains URL support too — files via `/quo-file-issue` then fixes end-to-end — eliminating the manual two-step. Existing flags remain accepted as silent no-op aliases for backward compat.
