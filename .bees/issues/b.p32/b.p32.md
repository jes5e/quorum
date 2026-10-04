---
id: b.p32
type: bee
title: Doc review README floor bans security requirements, contradicting the Doc Writer's table (operator-required security configuration belongs in the README)
status: open
created_at: '2026-10-04T12:16:40.184501'
schema_version: '0.1'
reference_materials: null
guid: p32wg2b8t5dtevf9jknpmctja8xxufbg
---

## Description

`/quo-doc-writer-review`'s README rules (`### Readme`) include "No discussion of security implications or requirements". This contradicts the Doc Writer's ownership table, which puts "What users and operators do: install, commands, configuration" in the customer-facing docs. Operator-required security configuration, such as auth modes, service identity, and a trust-delegation model, is configuration an operator must set. So the writer puts it in the README, and the reviewer's floor asks for its removal. The skill also contradicts itself: its own example finding adds a required `API_TOKEN` variable to the README's Configuration section.

The skill calls its standard checks a floor that a target repo's CLAUDE.md cannot relax. The guide-precedence rule overrides the floor only on where a fact is placed, so a project cannot reliably opt out of this content ban.

## Evidence

Reported by a live_edit agent (operator relayed, 2026-10-04). live_edit's README legitimately documents operator-required security configuration: the trust-delegation model, service identity, and auth modes. Applied literally, a doc reviewer would delete those sections. This is a contract conflict between two agents (the Doc Writer's table and the Doc Reviewer's floor), visible in the text itself, so it qualifies as a gap between two agents, not a predicted scenario.

## Expected behavior

The README review lets operator-required security configuration and its user-visible consequences stay in the README. Security internals stay out of the README under the existing "No implementation details" bullet. Threat analysis and security guarantees go in the SDD under the Doc Writer's table ("the guarantees the system must keep").

## Suggested fix

Delete the bullet. Nothing it should still exclude is uncovered: implementation-level internals fall under "No implementation details", and guarantees fall under the table's SDD row. A narrowed rule would restate both. Check the readers: tests, README, and `docs/sdd.md`.

