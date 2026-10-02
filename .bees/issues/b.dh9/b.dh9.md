---
id: b.dh9
type: bee
title: 'Doc roles: give the PRD its own row (goals, non-goals, targets, promises) and keep it true, instead of read-only'
status: open
created_at: '2026-10-02T15:38:28.031211'
schema_version: '0.1'
reference_materials: null
guid: dh9s8pzgfmu2q47n7q3xio4gzfabaisx
---

## Description

Give the PRD its own row in the Doc Writer's "where each fact lives" table and maintain it like the SDD, instead of "background: read it, never write it" (b.sb7's Q2). This reverses Q2 (operator, 2026-10-02).

## Evidence

On one day in live_edit (2026-10-01/02), three fixes were blocked from updating `docs-internal/prd.md`: b.xje (a ReorderChildren rule), b.v6d (operation ids), and b.v9c (presence). The operator had to edit the PRD by hand or authorize an exception each time. A stale PRD makes later reviews flag correct new behavior as a mistake. Three questions: 3 times in a day; it announces itself; not recovered unaided.

The live_edit agent's view, as asked by the operator: all three would have been no-ops, or a one-line promise edit, under a PRD defined as below. The blocked edits were detail (a command table, an error table, metrics, a per-feature "known gap") that doesn't belong in a PRD.

## Expected behavior

**PRD row:** what the product must do and why, at product level:
- the goals;
- the non-goals;
- product-level targets (for example sustained edit rate, confirm-latency target, supported layer size, availability);
- the promises to users and clients, stated briefly, each with a one-way pointer to the SDD section that contracts it.

It holds no commands, field names, error codes, metric names, env vars, limits, preconditions or exceptions, no mechanism, and no history.

**The PRD/SDD line, one shared test for writer and reviewer.** A sentence that names a field, code, metric or env var, or that says "unless / except / only when / within N", is the SDD's contract. A sentence whose deletion would change what a product owner signs off to users is the PRD's. Known user-visible limitations go in the customer docs and the SDD's residuals; the PRD carries only non-goals.

**The Doc Writer's two jobs apply to the PRD for its row:**
- correct any PRD statement a change makes false;
- update it when a change adds or changes a product-level goal, non-goal, target or promise;
- add nothing else, and no per-feature write-ups.

**The Doc Reviewer** checks the PRD the same way: only what the change touched, and that nothing added fails the test.

**Unchanged:** the guide-precedence rule (a project's guide wins where it places a fact differently, except that nothing is added to a per-feature or per-change section).

## Readers (confirm by grep)

- `agents/doc-writer.md`: the table, the jobs, and the PRD path key.
- `skills/quo-doc-writer-review/SKILL.md`: scope ("The PRD is not reviewed; no role writes it" changes) and the SDD contract sentence.
- `skills/quo-setup/SKILL.md`: the PRD's "used for" line and the bootstrap note ("nothing after this bootstrap writes it").
- README and CONTRIBUTING where they restate it; `skills/quo-file-issue` (`## Doc divergence noted` excludes the PRD today); the review/test pins.

Decide b.21d (the Encode deferral destination "project PRD/SDD via a doc-writer pass") in the same change: deferred work is still history, so likely remove it.

## Not in scope

- A PRD size cap: a prediction; the definition plus the test keeps it small.
- A PM rule for moved PRD section pointers: a prediction.
- `/quo-plan-from-specs --feature`, which parses `### Feature:` sections in a cumulative PRD/SDD: that is item 12a, parked. Existing sections remain until each repo's cleanup and new ones are not added. Note the dependency when 12a is decided.

## Per-repo cleanup (not this build)

Shrink each repo's existing PRD to the definition: keep goals, non-goals, targets and promises; replace command tables, error codes and metrics with pointers. For live_edit, a live_edit agent does this after that night's in-flight merge requests (three fixes were editing the PRD). Each repo's CLAUDE.md `## Documentation Locations` description of the PRD gets the one-line definition.

## Process

A small batch: a design checkpoint, hand edits, one cold review under the exit rule, and merge on the operator's go. No dedicated validation; the next real run that changes a promise is the check.

