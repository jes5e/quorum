---
id: b.527
type: bee
title: '/quo-fix-issue: no deferral-hygiene pass after post-completion, so defer-* obligations created while routing post-completion findings are lost at run end'
status: open
created_at: '2026-09-11T00:17:26.461064'
schema_version: '0.1'
reference_materials: null
guid: 52774xgfggkr8ohbcufrsbujzpjrzji1
---

## Description

`/quo-fix-issue` is the only orchestrator body whose post-completion section (Section 11) has no deferral-hygiene pass after it. Section 8's Issue boundary and Section 12 step 3 both fire Section 9 *before* Section 11, and Section 9's own lead says the batch-close firing covers "anything surfaced between Issues". Section 11 step 6's **Fix in this session** branch applies per-unit rules, which include Section 7 routing, and Section 7 creates a `defer-*` obligation the moment a finding is ignored. Such an obligation is never enumerated, never gated, and never surfaced: `/quo-fix-issue`'s Section 13 emits only the GitHub close block, and there is no per-unit summary at `postcomp-<n>` scope to carry `**Ignored Review Feedback**`.

`/quo-execute` has no such gap: its Section 11 tail routes to Section 9 before Section 13, and Section 9's lead states that firing site explicitly.

## Current behavior

A `defer-*` obligation created while routing a post-completion finding in `/quo-fix-issue` is lost at run end. The manifest is truncated at the next run start, so the obligation reaches no durable carrier.

## Expected behavior

Every `defer-*` obligation created during post-completion routing reaches a durable carrier before the run ends, the same guarantee the per-Issue boundary already gives.

## Suggested fix

Mirror `/quo-execute`'s order in `/quo-fix-issue`: move the batch-close deferral-hygiene firing from before Section 11 to after it (Section 8 boundary and Section 12 step 3), retarget Section 11's tail to "proceed to Section 9, then Section 13", and update Section 9's lead enumeration to name that firing site. This reorders firings that already exist; it adds no new gate, obligation kind, or state. It is a structural change to the orchestrator body, so per CLAUDE.md `## Working on the orchestrator skills` it goes through inventory-anchored hand edits with cold reviews, not a `/quo-fix-issue` run, and the rule inventory (`F7-*` post-completion rules and the Section 9 firing-site enumeration) is amended alongside.

The fallback path, if the firing-site enumeration is judged too costly to touch: add to Section 11's tail that Section 9 fires once more when post-completion routing left any `defer-*` obligation `open`. That adds a clause where the reordering restructures, so it is the inferior path.

## Background and rationale

Surfaced by the thirteenth cold review of the second validation-run fix batch (2026-09-11), which confirmed the gap is pre-existing at `b611786` and not introduced by that batch. Filed rather than fixed in the batch because it reorders the loop's firing sites, a design change outside a validation-fix scope. Related: the handoff's known follow-up that `/quo-execute`'s "drafted Epics remain" exit arm never fires deferral hygiene — the same class of gap on the other body.

