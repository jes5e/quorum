---
id: b.hc5
type: bee
title: 'Candidate: one shared per-unit loop reference for /quo-fix-issue and /quo-execute instead of mirrored text'
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:52.413268'
status: done
schema_version: '0.1'
guid: hc5zqfvw53rv9i7pesdcrv6vp3ttn6yr
---

## Description

About 6,000 words of `/quo-fix-issue` and `/quo-execute` are Tier 1/Tier 2 mirrors of each other (§7 routing, §10 compromise tracker, the Phase A loop, Phase C, the Engineer-dispatch precondition), pinned byte-identical by the tests, so every shared-rule edit is made twice (operator, 2026-09-26).

## Candidate

Move the shared per-unit loop into one shared reference, which each body reads at run start and again after a compaction, keeping each body's first-150-line core. One copy instead of two. It needs a REWRITE-BRIEF D2 amendment (a gate's text may live in a reference the body reads) and touches `/quo-fix-issue`, so it is its own batch with its own validation. Merging the two skills into one with two entry modes was considered and not recommended (a much larger redesign).

## When to decide

After the big feature, once it shows how often shared rules actually change. The post-compaction self re-read (mirrored batch item 2) removes the compaction argument for this, leaving the maintenance argument.
## Closed (2026-09-29, operator): not now

Since the rebuild, shared-rule edits have landed in both bodies at once (b.rqc, b.d7t), and the tests keep the mirrored text byte-identical, so the cost is editing twice, not drift. No run has failed because of the mirror. Reopen if a mirrored edit ever causes a real failure or drift.
