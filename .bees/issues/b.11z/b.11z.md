---
id: b.11z
type: bee
title: Cross-check finding-emission shape across the four review skills after b.ut9 Phase-1 lands
status: open
created_at: '2026-05-29T01:37:57.908467'
schema_version: '0.1'
reference_materials: null
guid: 11zh6w5tm8ysb6z51qf29vk2grwa5tft
---

## Description

After all four Phase-1 emission Epics under Plan Bee `b.ut9` land — `t1.ut9.9c` (`/quo-engineer-review`), `t1.ut9.jn` (`/quo-doc-writer-review`), `t1.ut9.q2` (`/quo-test-writer-review`), and `t1.ut9.29` (`/quo-spec-review`) — the four review skills' documented finding-emission shapes need a cross-check for byte-identical conformance to the authoritative SDD data model (Spec Bee SDD child `t1.tip.ux`, "Finding shape with two-dimensional tagging"). This is a follow-up integration-time verification task surfaced during planning, not a present-state bug.

## Current behavior

Each emission Epic independently pins the severity vocabulary (`blocker` / `suggestion` / `nit`), the depth vocabulary (`trivial-tweak` / `refactor-locally` / `re-architect`), and the finding-line / fix-path-line shapes by referencing the shared SDD data model. There is no shared canonical example block enforcing uniformity, and the Epics land at different times, so rendering drift between the four sections is possible but currently unverified.

## Expected behavior

All four review skills (`quo-engineer-review` Step 4, `quo-doc-writer-review` Step 6, `quo-test-writer-review` Step 4, `quo-spec-review` Step 4) document byte-identical finding-line and fix-path-line shapes and identical severity/depth tag vocabularies, matching the SDD `t1.tip.ux` data model. The Phase-2 orchestrator routing table (Epic `t1.ut9.no`) keys its `(num-paths, max-depth)` tuple on parsing these lines uniformly across all four skills, so uniformity is load-bearing for the parser.

## Impact

If rendering drifts between the four emission sections, the Phase-2 routing-table parser could misparse one or more skills' findings, breaking depth-aware routing. Correctness impact on the Phase-2 feature.

## Suggested fix

After Epics `q2` and `29` also land, read the output-shape sections of all four review skills' SKILL.md files and diff the finding-line + fix-path-line shapes and the severity/depth tag vocabularies for byte-identical conformance to each other and to the SDD `t1.tip.ux` data model. Flag and fix any divergence.

Key files:
- `skills/quo-engineer-review/SKILL.md` (Step 4 — Generate Work Item List)
- `skills/quo-doc-writer-review/SKILL.md` (Step 6 — Output Work Items)
- `skills/quo-test-writer-review/SKILL.md` (Step 4 — Generate Work Item List)
- `skills/quo-spec-review/SKILL.md` (Step 4 — Generate Work Item List)

## Background and rationale

Surfaced as PM finding F3 during `/quo-breakdown-epic` of Epic `t1.ut9.jn` (per-Task PM review). The PM noted cross-Epic shape-identity is currently enforced only by each emission Epic's Subtask independently pinning the same SDD data model (sound, since no emission Epic has landed yet), with no shared canonical example block to diff against. Deferred via the deferral-hygiene gate as `defer-to-new-Issue` because the cross-check is only actionable after all four emission Epics land. This Issue is the durable carrier for that integration-time verification.

