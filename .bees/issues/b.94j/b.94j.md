---
id: b.94j
type: bee
title: Define a reviewer preferred-fix-path emission contract consumed by the routing-decision gate
parent: null
reference_materials: null
created_at: '2026-05-29T16:48:17.960632'
status: done
schema_version: '0.1'
guid: 94jp41ywfat8on7k43mkk2t6vdtgcjza
---

## Description

The routing-decision gate added in `b.ut9` (the "### Orchestrator discipline: routing review findings" section in `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md`) places the `(Recommended)` marker on "the path the reviewer flagged as preferred when the reviewer surfaced a preference." But none of the in-flow reviewer emission contracts define HOW a reviewer signals a preferred fix path among multiple enumerated paths — the consumer (gate) reads a preference signal the producer (emission) never specifies.

## Current behavior

The four review skills (`quo-engineer-review`, `quo-doc-writer-review`, `quo-test-writer-review`, `quo-spec-review`) and `quo-plan` Step 5e emit fix-path lines as `(<letter>) [depth:<...>] <description>` with no preference marker, and their worked examples show none. Because no reviewer can emit a preference, the routing-decision gate never marks any path `(Recommended)` in practice.

## Expected behavior

An optional preferred-path marker exists in the shared fix-path emission contract, and the routing-decision gate consumes it to place the `(Recommended)` marker on the reviewer-preferred path when one is surfaced.

## Impact

Low / graceful. The gate explicitly handles the absent-preference case ("otherwise no path is marked Recommended"), so it degrades gracefully today; nothing is broken. This is a producer/consumer contract gap, not a correctness bug — but the `(Recommended)` affordance the gate advertises is currently unreachable.

## Suggested fix

Add an optional preferred-path marker to the shared fix-path emission contract (e.g., a `[preferred]` tag or a `(*)` marker on one fix-path line) across the four review skills + `quo-plan` Step 5e, and update the routing-decision gate prose + worked examples to consume it. Keep the marker OPTIONAL so the graceful-degradation path (no path marked Recommended) remains valid.

## Background and rationale

Surfaced by the `/quo-execute` post-completion review of Bee `b.ut9` (finding #3, severity `suggestion`). The routing-decision gate (Epic `t1.ut9.no`) consumes a preference signal that the Phase-1 emission Epics (`t1.ut9.9c` / `t1.ut9.jn` / `t1.ut9.q2` / `t1.ut9.29` / `t1.ut9.53`) never defined.

**Related — consider bundling.** This touches the same four-review-skill emission contract as open Issue `b.11z` ("Cross-check finding-emission shape across the four review skills after b.ut9 Phase-1 lands") and could share a single pass through those files. The two are distinct deliverables: `b.11z` verifies byte-consistency of the *existing* emission shape; this Issue adds a *new optional field* to it. Also slated for `b.11z` (per a `/quo-execute` PM deferral during the b.ut9 run): the explanatory-tail prose divergence where `quo-engineer-review` and `quo-spec-review` omit the "The shape is uniform whether 1 or N paths are enumerated" sentence that `quo-doc-writer-review` and `quo-test-writer-review` carry.
