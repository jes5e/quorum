---
id: b.bov
type: bee
title: Subagent definitions grant Grep but not Glob
parent: null
reference_materials:
- value: https://github.com/jes5e/quorum/issues/8
  resolver: github-issue
created_at: '2026-06-02T20:09:39.252189'
status: done
schema_version: '0.1'
guid: bov9c5dwwfwcxon5ggzekayp94u9jb85
---

External reference: GitHub Issue https://github.com/jes5e/quorum/issues/8

All eight quorum subagent definitions (`agents/*.md`) include `Grep` in their `tools:` allowlist but omit `Glob`, so agents cannot use the Glob tool even though it exists in the environment — agents misleadingly report that "Grep/Glob are not installed." Since Glob is a basic read-only file-finder and the natural companion to `Grep`, any agent granted `Grep` should also be granted `Glob`. The fix is to add `Glob` alongside `Grep` in each agent definition's `tools:` array. See the referenced GitHub Issue for the authoritative detail.
