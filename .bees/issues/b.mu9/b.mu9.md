---
id: b.mu9
type: bee
title: /bees-plan Path A delegation breaks with cumulative PRDs
status: open
created_at: '2026-05-03T01:17:11.757996'
schema_version: '0.1'
egg: null
guid: mu9bufwvq7urhrkh25djzuz1py92xwnj
---

## Description

The `/bees-plan` skill's Step 5 Path A unconditionally delegates to `/bees-plan-from-specs <prd-path> <sdd-path>` when the project has PRD and SDD docs. This works for single-feature PRDs but breaks for the project's intended cumulative-PRD pattern — which is one of the project's stated priorities (per `README.md`: "Cumulative project-level docs. PRD/SDD live as files in `docs/`, accumulate sections as features are planned").

## Current behavior

When `/bees-plan` is invoked on a feature whose PRD/SDD already contain other per-feature subsections:

1. `/bees-plan` Step 4 successfully adds a new `### Feature: <title>` subsection to PRD/SDD.
2. `/bees-plan` Step 5 Path A delegates to `/bees-plan-from-specs <prd> <sdd>`.
3. `/bees-plan-from-specs` Step 1 reads both documents in full, extracts ALL features (including previously-planned ones with their own existing Plan Bees in the hive), and creates ONE Plan Bee covering whatever it interprets the cumulative spec to be.

There is no scoping argument or mechanism in `/bees-plan-from-specs` to focus on a single `### Feature:` subsection. The skill assumes the PRD describes a single feature.

Surfaced during `/bees-plan` invocation for the Ephemeral-Agent Orchestration feature on 2026-05-03. The PRD at `docs/prd.md` had two per-feature subsections at planning time: `Feature: Test strategy for the skills repo` (paused, with its own Plan Bee `b.gar`) and `Feature: Ephemeral-Agent Orchestration` (the new one being planned). Delegating would have re-planned both — duplicating or conflating with the existing `b.gar`.

The author worked around it by skipping the delegation and creating the Plan Bee + Epics inline in `/bees-plan`'s session.

## Expected behavior

One of:

(a) **Inline-only.** `/bees-plan` Step 5 Path A's delegation prose is replaced with the inline create-ticket logic from Path B, regardless of whether PRD/SDD already exist. The Plan Bee's `egg` points to the existing PRD/SDD as before — the only difference between Path A and Path B becomes whether `egg` is set.

(b) **Feature-scoping argument on `/bees-plan-from-specs`.** Add an optional `--feature "<title>"` argument that restricts `/bees-plan-from-specs` Step 1's read to a single `### Feature: <title>` subsection inside the PRD/SDD. `/bees-plan` Step 5 Path A's delegation passes the title from Step 3's scope statement.

(c) **Multi-feature detection.** `/bees-plan-from-specs` detects multiple `### Feature:` subsections at the start of Step 1 and either (i) hard-fails with `Multiple features detected in PRD; pass --feature "<title>" to scope`, or (ii) `AskUserQuestion`-prompts the user to pick one.

## Suggested fix

(a) is the simplest — eliminates the delegation entirely and unifies Path A / Path B behavior into one inline create flow. The "single source of truth for specs→Plan Bee logic" rationale that originally motivated delegation was sound but doesn't survive the cumulative-PRD pattern.

(b) is more invasive but preserves the standalone `/bees-plan-from-specs` use case (a user with a finalized cumulative PRD/SDD can re-plan one feature without re-deriving every previously-planned feature's spec). Worth doing if the standalone path is important.

(a) and (b) are not mutually exclusive — could ship (a) now to fix the immediate breakage and (b) later if standalone re-planning becomes a real need.

## Files to modify

- `skills/bees-plan/SKILL.md` — Step 5 Path A delegation prose. Replace with inline create logic (option a) or extend delegation to pass `--feature` (option b).
- `skills/bees-plan-from-specs/SKILL.md` — Step 1 read logic. Document multi-feature handling (option b or c).

## Severity

**Medium.** Surfaces silently as either a redundant Plan Bee for an already-planned feature, or as a Plan Bee that conflates multiple features. The author of this issue caught it before any tickets were created, but a less-attentive caller would miss it.

