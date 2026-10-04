---
id: b.gmg
type: bee
title: 'Doc roles: a stale code-level SDD statement is corrected in place and kept; check placement before correcting, and review edits as well as additions'
status: open
created_at: '2026-10-03T23:11:09.348667'
schema_version: '0.1'
reference_materials: null
guid: gmg4sjv4ykpbvhn5etm3kd3uxfo5diwg
---

## Description

The docs rewrite (b.sb7) stopped the Doc Writer from adding per-feature sections, but the SDD still regrows code narration through edits. When a change makes an existing code-level SDD statement false (a renamed constant, type, or function; a changed size), the Doc Writer corrects it in place and keeps it, and the Doc Reviewer checks only that it is accurate. The table puts that kind of fact in the code, so the right move is to delete it, or leave a pointer to the code.

## Evidence (live_edit, `/quo-execute` b.dkt Epic 6, 2026-10-03/04)

The skills in the container were the post-b.sb7 ones: the doc-role files are dated 2026-09-30 15:51 on the container clock, after `dfc16d9` (15:46 UTC). The operator had a read-only audit run on the SDD's flow sections, then had the run's orchestrator trace the passages this session wrote. Both reports are on the overseer host under `~/.quorum-scratch/`: `sdd-code-narration-audit-2026-10-04.md` (about 55 flagged passages in all) and `sdd-narration-evidence.md`.
- Seven flagged passages were written in this run, in Tasks 12, 2 and 3: script argument slot numbers, a "which function wraps which" chain, a function's return variants, a struct's semaphores and container type, and a per-entry byte size.
- **All seven were edits of text that already carried the same kind of detail.** The Doc Writer swapped in the new names rather than moving the detail out.
- **The requests were framed as accuracy fixes.** They were relayed stale-name lists from the code reviewer and engineer, plus the orchestrator's own "re-derive that figure from the types; do not guess". One doc Subtask (`t3.dkt.5o.c9.am`) and the spec named the type for its SDD section.
- No Doc Writer declined a request or invoked the "where each fact lives" table to move code detail out. No Doc Reviewer finding in any of the four Tasks was about the level of detail; all were about accuracy, staleness, or placement.
- **What worked:** the new decision text went in as intended. Task 2 recorded why structural edits queue, with the rejected alternative; Task 3 recorded a metric label rule with its rejected alternative.

**Three questions:** 7 times in one run; silent (found only by an operator-requested audit); not recovered unaided.

## Root cause

- **Doc Writer, job 1:** "correct each statement the Engineer's diff makes false, or delete it when the table below puts that fact elsewhere". The two actions sit side by side as alternatives, so a request framed as "fix this stale name" reads as "correct", and the placement question never comes up.
- **Doc Reviewer:** the level-of-detail check is step 3's third bullet, "Does everything the Doc Writer added pass the SDD test …". An edit to an existing statement is not an addition, so no reviewer applied the test to it. This is a gap between two agents: the writer's delete rule has no check behind it.

## Expected behavior

- For each statement a change makes false, the placement question comes first: correct it only if the table keeps that fact in this doc; otherwise delete it, with a pointer to the code if useful. This holds even when the request asks only for accuracy.
- The review applies the SDD test, and in the PRD the line, to every statement the Doc Writer added or edited.

## Suggested fix

A restructure of the two existing sentences, not a new rule:
- `agents/doc-writer.md` job 1;
- `skills/quo-doc-writer-review/SKILL.md` step 3's bullets.

Keep the writer and reviewer wording aligned (pin it if a shared phrase emerges). Aim to be word-neutral. One cold review under the exit rule; no dedicated validation. The next execute Task that renames something the SDD names is the check.

## Not in scope

- A rule for the orchestrator's relays (stale-name lists). The table already governs over relayed requests; the writer applying placement first covers them.
- The breakdown's doc Subtasks naming code identifiers: one occurrence, so it is a prediction.
- live_edit's SDD cleanup of the older flagged passages. That is the repo's own job, best run after this fix lands so later Tasks don't re-correct the detail in place.

