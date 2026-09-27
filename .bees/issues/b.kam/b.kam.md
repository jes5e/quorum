---
id: b.kam
type: bee
title: A revised Analyst design returned as a delta overwrites the proposal file, so the full approved design is lost
down_dependencies:
- b.87t
parent: null
reference_materials: null
created_at: '2026-09-26T11:34:26.747364'
status: done
schema_version: '0.1'
guid: kamw8yr2hcnygxznitp7we38xt4b4m3b
---

## Description

When the Analyst revises an approved design mid-run, it can return only the changes ("revision 1's sections A, C, D stand unless changed"). `/quo-fix-issue` §6 writes each Analyst return to the `**Proposal:**` file, "overwritten on each later one". So after a revision gate the full approved design exists nowhere on disk: the file holds only the delta, and revision 1 survives only in the orchestrator's conversation.

## Current behavior

Observed in live_edit Issue b.62m (2026-09-25, during b.37n's validation). A Test Writer design gap triggered Analyst revision 2, returned as a delta. The two later PM dispatches received the directive by path plus an orchestrator summary, not inline, contrary to the `## Blast radius` row's "verbatim and inline, never as a file path". PM pass 2's prompt told a cold agent that revision 1 "was relayed to your first pass in full", a false premise for a fresh dispatch; its revision-1 content was a summary. PM pass 3 also received the three relay headings merged into one.

Three questions: how often, every revision gate that follows an Approve; announces itself, no; recovered unaided, yes this time (the PM read the file and traced correctly). It is a gap between two agents (the Analyst's return shape, the proposal-file overwrite, and the relay contract), and a compaction after the revision would lose revision 1 entirely.

## Expected behavior

After any revision gate, the proposal file holds the complete approved design, so every later relay can carry the directive verbatim and inline with its exact headings.

## Suggested fix

The smallest contract change: `agents/analyst.md` states that a revision returns the whole Design Proposal, every section, not a delta, because the orchestrator keeps only the latest return and relays it verbatim. The overwrite rule then loses nothing. Check `/quo-execute`'s Revise path (it quotes "the prior revision in full") for the same assumption; execute's rebuild (b.87t) mirrors fix-issue's loop, so fix this first.

Hand edit with one cold review, per CLAUDE.md `## Working on the orchestrator skills`. No dedicated validation run: a revision can't be triggered on demand, so the next real run with a revision gate is the check.
## Closed (2026-09-26)

Landed in `f01bf79`, merged to main by fast-forward (not pushed).
- `agents/analyst.md`, the `## Prior proposal and user feedback` bullet: a revision is returned as a whole Design Proposal, restating what stands from any earlier proposal rather than referring to it, because the orchestrator keeps only the latest return and relays it verbatim to roles that never saw the earlier one. "Any earlier proposal" leaves execute's first escalation alone, since its prior design is the tickets, which persist.
- Deleted: the clause naming `/quo-fix-issue`'s reason for passing the proposal as a path.
- Cap: `agents/analyst.md` 5000 → 5024. `docs/sdd.md` gains a feature entry.
- Neither orchestrator body changed: fix-issue's overwrite of the proposal file is now lossless, and its inline-relay rule already stood; execute's "prior revision in full" and its ticket-recorded `## Design revision (Analyst)` now hold.

**Review:** the overseer read the diff and traced its readers, and waived the cold round (one contract sentence in a role file, no body change).

**Validation:** no dedicated run, because a revision gate can't be triggered on demand. The check is the next real run that reaches a revision gate after an Approve (the execute rebuild's first such run can serve). Confirm: the Analyst's revised return is whole; the `**Proposal:**` file holds the complete approved design after the gate; later relays carry `## Authoritative design directive (from the Analyst gate)`, `## Blast radius`, and `## Design decisions for writers` verbatim, inline, and under separate headings.
## Check still open (2026-09-27)

The b.87t validation run (live_edit b.v9c Epic 1) reached no Analyst revision gate: both Analyst returns were premise checks. The three checks in the close-out note wait for the next real run with a revision gate after an Approve.

