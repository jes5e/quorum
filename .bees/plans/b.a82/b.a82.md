---
id: b.a82
type: bee
title: README rewrite for ticket-agnostic framing
parent: null
children:
- t1.a82.tx
reference_materials:
- value: b.43w
  resolver: bees
created_at: '2026-05-08T15:13:07.495832'
status: done
schema_version: '0.1'
guid: a8267jpksoudaffp1xwqaoph5dp4ckcx
---

Rewrite `README.md` to reframe quorum as a portable, ticket-system-agnostic Claude Code SDLC workflow — bees today, beads (Plan Bee `b.9xr`) on the roadmap, others over time. Strip all "Apiary" references and the comparative "vs Apiary" framing. Audit the workflow diagram and skill catalog against the present-day skill set; the Explore agent's audit at SDD-authoring time confirmed both are accurate, so the rewrite is a positioning + scrub pass with a small (~20-30 line) diff localized to the lead paragraph, `## Why this exists`, `## Coming soon: optional skills`, and `## Credits` sections.

PRD and SDD live as `t1=Doc` children of the Spec Bee referenced in `reference_materials`.

## Anticipated doc impact

Resolved against the contract keys in CLAUDE.md `## Documentation Locations`:

- **Customer-facing docs (`README.md`)**: this Plan Bee **is** the customer-facing-doc change. The work itself updates the README; no post-implementation fold step is required.
- **Project requirements doc (cumulative project PRD)**: not modified. The doc-writer agent dispatched at end of `/quo-execute` should **skip** the cumulative-PRD `### Feature:` subsection-add step for this Plan Bee — the work is doc-only meta-work with no functional spec impact.
- **Internal architecture docs (cumulative project SDD)**: not modified. Same rationale as the cumulative PRD.
- **Engineering best practices (`CONTRIBUTING.md`)**: not modified. May be a follow-up Issue if its framing also needs scrubbing — out of scope here.
- **Doc writing guide**: not modified.
