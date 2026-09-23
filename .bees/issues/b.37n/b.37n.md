---
id: b.37n
type: bee
title: Fix-mode PM traces the diff against the Issue body, not the approved Analyst directive
down_dependencies:
- b.87t
parent: null
reference_materials: null
created_at: '2026-09-23T11:23:18.151406'
status: open
schema_version: '0.1'
guid: 37nfhte9vnaybxgmmgkwp21ptauricd7
---

## Description

In `/quo-fix-issue` the PM traces the diff against the Issue body, never against the approved design. `skills/quo-fix-issue/SKILL.md` §5 passes the PM "the Issue ID, the body verbatim, and the `up_dependencies` array", and the PM is not a recipient of `## Blast radius` or `## Design decisions for writers`; nothing relays the Analyst's `### Recommended approach` or `### Policy decisions this change implies` to it. The Analyst treats the Issue body as a problem report, not as design, and §5 states that the directive wins where the two conflict — so the PM is the one role in Phase C checking traceability against the source the run has already overruled.

## Current behavior

- A diff that correctly implements an approved directive that refines or departs from the body (every `recommend-with-refinements` or `recommend-different-approach` verdict, and every policy answer the body did not settle) can read to the PM as drift or scope creep. That is the shape of b.yvu's Phase C PM `blocker`, which contradicted the Analyst's Blast radius and started the 1.09M-token cascade recorded on b.vtw. Since b.vtw Batch A the premise check catches such a finding, but only after the fact and at the cost of one Analyst dispatch per occurrence.
- The silent half: an Engineer change that goes beyond the directive while staying inside the body's wording passes the PM, because the PM checks against the body. Nothing announces this.

Triage (CLAUDE.md `## Working on the orchestrator skills`): frequent (any Issue where the directive diverges from the body), half silent, and the loud half recovers only by paying for the premise check. This is a contract gap between the orchestrator and the PM, not a procedural detail inside one agent.

## Expected behavior

The fix-mode PM receives the approved directive and traces the diff against it. The Issue body stays the problem statement: the PM checks that the diff solves the stated problem, and treats work outside the directive — not outside the body — as scope creep.

## Suggested fix

Hand-edit batch with a cold `/quo-engineer-review` round, per CLAUDE.md `## Working on the orchestrator skills`; not a `/quo-fix-issue` run. Enumerate every reader of the changed recipients before the first edit.

1. `skills/quo-fix-issue/SKILL.md` §5: pass the PM the same `## Authoritative design directive (from the Analyst gate)` block the Engineer receives, and add the PM to the recipients of the `## Blast radius` and `## Design decisions for writers` rows. The re-derivation and `**Proposal:**` read-back rules already cover a stranded directive.
2. `agents/pm.md`: in fix mode, spec traceability is against the approved directive, which wins over the Issue body where they conflict; the body is the problem statement.
3. `tests/test_orchestrator_structure.py`: add `AGENT_PM` as a consumer of the `## Blast radius`, `## Design decisions for writers`, and `## Authoritative design directive` contract-surface rows.

## Sequencing

After the docs-only (text-class) validation run, which dispatches no PM and so does not exercise this. Before the `/quo-execute` rewrite (execute adopting fix-issue's per-Task Phase A/B/C loop, discussed with the operator 2026-09-23), so the rewrite's Phase C mirrors the corrected PM dispatch rather than copying the gap into execute. Validate on the next small-code `/quo-fix-issue` run.

## Relation to open tickets

- b.sb7: its relay reconciliation (`## Ratified decisions` vs `## Design decisions for writers`) starts from the PM already holding the directive. Its 2026-09-19 note that the execute per-Task PM is not a recipient of `## Design decisions for writers` is addressed by the execute rewrite, whose Phase C PM mirrors this one.
- Supporting evidence to collect, not blocking: premise checks fired on PM findings in recent fix-issue runs, especially `premise-false` returns. Each is this gap costing an Analyst dispatch. The same data feeds the separate question of whether the fix-mode PM earns its keep, which should be measured after this fix so the PM is judged on the right input.
