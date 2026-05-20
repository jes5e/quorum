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
status: ready
schema_version: '0.1'
guid: ut99k9rd51jiqd3tor4tyujtvbsptmix
---

Add depth-aware finding routing and a session-scoped compromise tracker across the quorum review-and-routing workflow. The change extends in-flow review skills with two-dimensional finding tagging (severity + per-fix-path depth), introduces deterministic orchestrator routing rules in `/quo-fix-issue` and `/quo-execute` that fire user gates on multi-path or single-path-re-architect findings, adds an anti-pattern callout forbidding scope-bounding directives inside R2/R3 dispatch prompts, and reframes the post-completion review to challenge accepted compromises against the tracker.

Substantive PRD/SDD content lives in this Plan Bee's referenced Spec Bee children (PRD `t1.tip.bo`, SDD `t1.tip.ux` under Spec Bee `b.tip`).

## Anticipated doc impact

Per the SDD's `## Documentation` section, this feature will warrant new `### Feature:` subsections in the cumulative project docs once it lands:

- **Project requirements doc (PRD)** — the cumulative PRD per CLAUDE.md `## Documentation Locations`. Will receive a feature subsection describing the depth-aware routing, the compromise tracker, and the post-completion review reframe as user-observable behaviors.
- **Internal architecture docs (SDD)** — the cumulative SDD per the same contract key. Will receive a feature subsection describing the section-numbering changes in `/quo-fix-issue` and `/quo-execute`, the routing table contract, the compromise-tracker file convention, and the dispatch-prompt rewrites.

`README.md` (Customer-facing docs) likely does NOT need an update — the user-typed invocation surface of `/quo-fix-issue` and `/quo-execute` is byte-for-byte unchanged (no new flags or arguments). The new gates are interactive prose + `AskUserQuestion` steps inside the existing flows. The doc-writer agent dispatched by `/quo-execute` will make the final call when the work lands.

`CONTRIBUTING.md` (Engineering best practices) may receive a light update to mention the anti-pattern callout (contributors working on future review-loop modifications should know that scope-bounding directives inside dispatch prompts are forbidden). To be decided during the doc-writer pass.

`docs/doc-writing-guide.md` (Doc writing guide) may receive a light update teaching the depth-dimension emission pattern for future review skills — the SDD's `## Documentation` section identifies this as a candidate. To be decided during the doc-writer pass.
