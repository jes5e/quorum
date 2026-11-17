---
id: b.5hf
type: bee
title: 'Epic-boundary review: scope sweeps in work merged from elsewhere; the reviewer spawned its own subagents'
status: open
created_at: '2026-11-17T14:59:39.873550'
schema_version: '0.1'
reference_materials: null
guid: 5hfgzuaic2k8c69mp8czodounpiv8qdz
---

## Description

Two defects in `/quo-execute`'s Epic-boundary (post-completion) review, both seen in live_edit's Epic 4 side lanes. Both are quorum's.

### 1. Its scope sweeps in work merged from elsewhere

- **The rule.** §11 scopes the review as `git diff <epic-base-sha>` plus untracked files, where the base is the commit before the Epic's first Task commit.
- **The failure.** A side lane that merges or fast-forwards its trunk partway through an Epic gets the trunk's work in scope:
  - lane M's Epic 4M: 439 files, +31,357/−11,729, against about 70 files of its own;
  - lane C earlier.
- **Why it's waste.** The trunk's own Epic boundary already reviews that work.
- **Evidence:** `~/.quorum-scratch/gate-e4laneM-postcomp-scope-w1p7.md` and `gate-68m-4c-postcomp-scope-p5x2.md`. The planner ruled "literal scope" both times, because narrowing it was a skill departure.
- **Three questions:** twice, loud (gated both times), and not recovered unaided: the planner had to rule. Side plans, the pattern this comes from, are a pattern quorum recommended.
- **Interim:** the operator sanctioned scoping to the Epic's own Task commits plus untracked files on 2026-11-17.

### 2. The reviewer spawned its own background reviewers

- **What happened.** Faced with that scope, lane M's `general-purpose` post-completion reviewer started two background reviewers on the trunk code. It could neither collect nor stop them, and handed back with only a spot check of that code. Their findings (10–19) reached the orchestrator later as unsolicited addenda.
- **Evidence:** `~/.quorum-scratch/postcomp-e4laneM-r1.md` (the "Scope note", "Addendum" and "Second addendum" sections) and `run-state-quo-execute-b.9nd.md`.
- **A false claim in execute §5:** "Subagents cannot spawn subagents, so every dispatch originates here." It is false in this build: the `general-purpose` reviewer has the Agent tool. Find every carrier of that claim.
- **Three questions:** once, half-loud (the results arrived late and unsolicited), and not recovered; the trunk got no full sweep.

### Goal and constraints

- **The scope** is the work this Epic's Tasks committed, plus uncommitted and untracked files, not work merged in from elsewhere. State it as a goal and leave the git mechanics to the orchestrator, unless an exact form is the point. Check whether `/quo-fix-issue`'s pre-session-SHA scope can sweep in merged work too. If no run shows it, say so and leave it.
- **The reviewer does its own review.** One goal sentence with its reason in the post-completion prompt reference, or a structural guard, such as dispatching a type that has no Agent tool, if that is simpler. Fix the false "cannot spawn" claim wherever it lives.
- **No wide-scope procedure.** Once the scope is right, the pressure that caused item 2 is gone. Splitting large scopes would be a predicted case.
- **Process:** orchestrator hand edit, inventory-anchored, with cold reviews under the exit rule. Checkpoint 1 is the design, for operator approval.

