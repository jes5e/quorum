---
id: b.ut9
type: bee
title: Depth-aware finding routing and compromise tracking in /quo-fix-issue and /quo-execute
parent: null
children:
- t1.ut9.9c
- t1.ut9.jn
- t1.ut9.q2
- t1.ut9.29
- t1.ut9.53
- t1.ut9.2q
- t1.ut9.no
- t1.ut9.po
- t1.ut9.od
- t1.ut9.pw
reference_materials:
- value: b.tip
  resolver: bees
created_at: '2026-05-20T03:38:28.661341'
status: done
schema_version: '0.1'
guid: ut99k9rd51jiqd3tor4tyujtvbsptmix
---

Add depth-aware finding routing and a session-scoped compromise tracker across the quorum review-and-routing workflow. The change extends in-flow review skills with two-dimensional finding tagging (severity + per-fix-path depth), introduces deterministic orchestrator routing rules in `/quo-fix-issue` and `/quo-execute` that fire user gates on multi-path or single-path-re-architect findings, adds an anti-pattern callout forbidding scope-bounding directives inside R2/R3 dispatch prompts, and reframes the post-completion review to challenge accepted compromises against the tracker.

Substantive PRD/SDD content lives in this Plan Bee's referenced Spec Bee children (PRD `t1.tip.bo`, SDD `t1.tip.ux` under Spec Bee `b.tip`).

## Phased landing

The 10 Epics land in two phases with respect to the load-bearing `b.wii` dependency (orchestrator-adherence failure mode; see PRD / SDD `## Risk / Known Dependencies` for the full framing):

**Phase 1 — Emission enrichment (Epics 1–6).** Per-skill emission extensions (`t1.ut9.9c`, `t1.ut9.jn`, `t1.ut9.q2`, `t1.ut9.29`, `t1.ut9.53`) plus reviewer-agent wrapper frontmatter alignment (`t1.ut9.2q`). All six Epics have empty `up_dependencies`. **Zero `b.wii` exposure** — no new user gates fire under Phase 1. Standalone value: severity tags become emitted for the first time across three implementer-side review skills; depth + fix-path enumeration land everywhere; reviewer-agent wrapper contracts get aligned with what the wrapped skills actually emit.

**Phase 2 — Routing + tracker + post-completion reframe (Epics 7–10).** Orchestrator-discipline routing rules + anti-pattern callout + scope-bounding gate + backwards-compat shim (`t1.ut9.no`), session-scoped compromise tracker with four append triggers (`t1.ut9.po`), end-of-run "Accepted compromises" surface (`t1.ut9.od`), post-completion review reframe + SR-4.5 / SR-4.6 plausibility checks + SR-6.7 recovery gate (`t1.ut9.pw`). **Inherits the `b.wii` fragility** — the new user gates the routing table and recovery gate fire use the same prose-strengthening adherence mechanism `b.wii` documents as intermittently failing.

**Recommended landing order:** Phase 1 first (b.wii-independent, standalone-valuable), then Phase 2 either (a) after `b.wii` resolves with a structural fix, or (b) with explicit user acknowledgement at the start of the Phase 2 `/quo-execute` run that the new gates may fail-as-prose intermittently. `/quo-execute b.ut9` will naturally land Phase 1 first (Epics 1–6 surface before Epic 7 in any topological ordering given the dependency wiring), so the phasing is enforced by existing dependency wiring without `/quo-execute` needing to learn a "phase" concept. The user controls the Phase 1 → Phase 2 boundary by either continuing the run after Phase 1 completes or pausing to wait on `b.wii`.

## Anticipated doc impact

Per the SDD's `## Documentation` section, this feature will warrant new `### Feature:` subsections in the cumulative project docs once it lands:

- **Project requirements doc (PRD)** — the cumulative PRD per CLAUDE.md `## Documentation Locations`. Will receive a feature subsection describing the depth-aware routing, the compromise tracker, and the post-completion review reframe as user-observable behaviors.
- **Internal architecture docs (SDD)** — the cumulative SDD per the same contract key. Will receive a feature subsection describing the section-numbering changes in `/quo-fix-issue` and `/quo-execute`, the routing table contract, the compromise-tracker file convention, and the dispatch-prompt rewrites.

`README.md` (Customer-facing docs) likely does NOT need an update — the user-typed invocation surface of `/quo-fix-issue` and `/quo-execute` is byte-for-byte unchanged (no new flags or arguments). The new gates are interactive prose + `AskUserQuestion` steps inside the existing flows. The doc-writer agent dispatched by `/quo-execute` will make the final call when the work lands.

`CONTRIBUTING.md` (Engineering best practices) may receive a light update to mention the anti-pattern callout (contributors working on future review-loop modifications should know that scope-bounding directives inside dispatch prompts are forbidden). To be decided during the doc-writer pass.

`docs/doc-writing-guide.md` (Doc writing guide) may receive a light update teaching the depth-dimension emission pattern for future review skills — the SDD's `## Documentation` section identifies this as a candidate. To be decided during the doc-writer pass.
