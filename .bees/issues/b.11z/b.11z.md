---
id: b.11z
type: bee
title: Cross-check finding-emission shape across the four review skills after b.ut9 Phase-1 lands
parent: null
reference_materials: null
created_at: '2026-05-29T01:37:57.908467'
status: done
schema_version: '0.1'
guid: 11zh6w5tm8ysb6z51qf29vk2grwa5tft
---

## Description

After all four Phase-1 emission Epics under Plan Bee `b.ut9` land — `t1.ut9.9c` (`/quo-engineer-review`), `t1.ut9.jn` (`/quo-doc-writer-review`), `t1.ut9.q2` (`/quo-test-writer-review`), and `t1.ut9.29` (`/quo-spec-review`) — the four review skills' documented finding-emission shapes need a cross-check for byte-identical conformance to the authoritative SDD data model (Spec Bee SDD child `t1.tip.ux`, "Finding shape with two-dimensional tagging"). This is a follow-up integration-time verification task surfaced during planning, not a present-state bug.

## Current behavior

Each emission Epic independently pins the severity vocabulary (`blocker` / `suggestion` / `nit`), the depth vocabulary (`trivial-tweak` / `refactor-locally` / `re-architect`), and the finding-line / fix-path-line shapes by referencing the shared SDD data model. There is no shared canonical example block enforcing uniformity, and the Epics land at different times, so rendering drift between the four sections is possible but currently unverified.

## Expected behavior

All four review skills (`quo-engineer-review` Step 4, `quo-doc-writer-review` Step 6, `quo-test-writer-review` Step 4, `quo-spec-review` Step 4) document byte-identical finding-line and fix-path-line shapes and identical severity/depth tag vocabularies, matching the SDD `t1.tip.ux` data model. The Phase-2 orchestrator routing table (Epic `t1.ut9.no`) keys its `(num-paths, max-depth)` tuple on parsing these lines uniformly across all four skills, so uniformity is load-bearing for the parser.

**Important nuance discovered during breakdown of `t1.ut9.29`:** `/quo-spec-review` keeps its pre-existing `[blocker]` **bracket** severity rendering, while the three implementer-side skills (`9c`/`jn`/`q2`) use the backtick `` `blocker` `` form per the SDD data model. This severity-rendering asymmetry is intentional and SDD-acknowledged. The cross-check must therefore verify uniformity of the **fix-path-line shape `(<letter>) [depth:...]`** (the part the routing parser keys on) across all four skills, and explicitly treat the severity-rendering bracket-vs-backtick difference as acceptable (routing keys on `(num-paths, max-depth)`, not severity — PRD FR-2).

## Impact

If rendering drifts between the four emission sections, the Phase-2 routing-table parser could misparse one or more skills' findings, breaking depth-aware routing. Correctness impact on the Phase-2 feature.

## Suggested fix

After Epics `q2` and `29` also land, read the output-shape sections of all four review skills' SKILL.md files and diff the finding-line + fix-path-line shapes and the severity/depth tag vocabularies for byte-identical conformance to each other and to the SDD `t1.tip.ux` data model (allowing the documented spec-review bracket-severity asymmetry). Flag and fix any divergence.

Key files:
- `skills/quo-engineer-review/SKILL.md` (Step 4 — Generate Work Item List)
- `skills/quo-doc-writer-review/SKILL.md` (Step 6 — Output Work Items)
- `skills/quo-test-writer-review/SKILL.md` (Step 4 — Generate Work Item List)
- `skills/quo-spec-review/SKILL.md` (Step 4 — Generate Work Item List)

## Background and rationale

Surfaced as PM finding F3 during `/quo-breakdown-epic` of Epic `t1.ut9.jn` (per-Task PM review). The PM noted cross-Epic shape-identity is currently enforced only by each emission Epic's Subtask independently pinning the same SDD data model (sound, since no emission Epic has landed yet), with no shared canonical example block to diff against. Deferred via the deferral-hygiene gate as `defer-to-new-Issue` because the cross-check is only actionable after all four emission Epics land. This Issue is the durable carrier for that integration-time verification.

## Deferred from /quo-breakdown-epic run (2026-05-29)

A second integration-time reconciliation item, surfaced as a PM-deferred item during `/quo-breakdown-epic` of Epic `t1.ut9.29` (per-Task PM review), is bundled into this Issue's scope:

- **Stale SDD-check count in the PRD spec source.** PRD child `t1.tip.bo` (under Spec Bee `b.tip`) states in its `## Non-Goals / Out of Scope` (and FR-1-area prose) that `/quo-spec-review` has **seven** SDD checks, but the SDD child `t1.tip.ux` and the live `skills/quo-spec-review/SKILL.md` carry **ten** SDD checks (Step 2 SDD checklist, items 1–10). The Epic/Task/Subtask correctly preserve the actual ten; the discrepancy is in the PRD child's wording only.
- **Action during the integration cross-check:** reconcile the PRD `t1.tip.bo` figure from "seven SDD checks" to "ten SDD checks" so the spec source matches reality. This is a one-line spec-doc correction to the Spec Bee PRD child body (via `bees update-ticket`), not a skill-prose change. Low priority; bundled here to avoid a standalone micro-ticket per `/quo-file-issue` house style.

## Deferred from /quo-execute run (2026-05-29)

A third integration-time reconciliation item, surfaced as a PM-deferred item during `/quo-execute` of Plan Bee `b.ut9` (per-Task PM review of `t2.ut9.q2.5c`, severity `nit`; re-confirmed by the post-completion review), is bundled into this Issue's scope:

- **Explanatory-tail prose divergence across the four review skills' fix-path-line docs.** `quo-doc-writer-review` and `quo-test-writer-review` carry the trailing sentence "The shape is uniform whether 1 or N paths are enumerated." after the fix-path-line grammar; `quo-engineer-review` and `quo-spec-review` omit it. This is human-facing prose only — the parser-relevant `(<letter>) [depth:...]` token is byte-identical across all four (already covered by this Issue's primary cross-check), so it is non-blocking.
- **Action during the integration cross-check:** align all four either way — add the trailing sentence to `quo-engineer-review` and `quo-spec-review` for uniformity, or remove it from the other two. Low priority; bundled here under the same integration-cross-check scope.
