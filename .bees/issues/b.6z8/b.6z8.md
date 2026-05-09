---
id: b.6z8
type: bee
title: quo-setup fast path silently re-registers a strict-subset hive set
parent: null
reference_materials:
- value: https://github.com/jes5e/quorum/issues/1
  resolver: github-issue
created_at: '2026-05-08T20:47:42.325610'
status: done
schema_version: '0.1'
guid: 6z88hres78qc1dj9e8zf2z85hsm84vqq
---

External reference: GitHub Issue https://github.com/jes5e/quorum/issues/1

`/quo-setup`'s fast-path eligibility check passes when at least one `.bees/<hive>/.hive/identity.json` marker exists on disk, then re-registers only those on-disk hives — so a repo originally set up before Specs became canonical (only Issues + Plans on disk) silently exits with "You're ready to go" while the missing Specs hive stays invisible until something forces the slow path to run. Suggested fix: add a fourth eligibility criterion to `skills/quo-setup/scripts/detect_fast_path.py` requiring `on_disk_hive_names` to be a superset of `{"issues", "plans", "specs"}`, so a strict-subset on-disk state falls through to the slow path's existing canonical-hive walkthrough.
