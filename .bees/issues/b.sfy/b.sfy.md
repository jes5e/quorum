---
id: b.sfy
type: bee
title: Spec-review loop-back UX gates dropped under orchestrator load
status: open
created_at: '2026-05-11T12:52:03.048829'
schema_version: '0.1'
reference_materials:
- value: https://github.com/jes5e/quorum/issues/4
  resolver: github-issue
guid: sfyiguzwkcoo1jnxrgdu6dx6hry5hpt4
---

External reference: GitHub Issue https://github.com/jes5e/quorum/issues/4

`/quo-plan` Step 4c (and the parallel `/quo-write-prd` Step 6a and `/quo-write-sdd` Step 7a) prescribe `AskUserQuestion` gates for routing on `/quo-spec-review` findings, but those rules live three levels deep in long skills and are reproducibly missed by orchestrator agents — both the "findings present, no blockers" case (agent emitted findings as prose and yielded instead of prompting) and the "no findings (clean re-check)" case (agent reported clean and yielded instead of promoting) broke the flow in a real planning session. Reporter recommends moving the load-bearing routing prescription from nested orchestrator prose into `/quo-spec-review`'s own output (a "**Next action for the orchestrator:**" trailer), with symmetric fixes for `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` and the orchestrator steps that consume them in `/quo-execute` / `/quo-fix-issue`.

