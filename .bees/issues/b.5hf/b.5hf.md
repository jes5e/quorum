---
id: b.5hf
type: bee
title: 'Epic-boundary review: scope sweeps in work merged from elsewhere; the reviewer spawned its own subagents'
parent: null
reference_materials: null
created_at: '2026-11-17T14:59:39.873550'
status: done
schema_version: '0.1'
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

## Closed (2026-11-17)

Merged by fast-forward from `badba83` to `7b1ef9d`, with the operator's go: "ok" at Checkpoint 1, which included the overseer's addition, then "merge please".

The work was Worker 2's. Its checkpoints are `~/.quorum-overseer/b5hf-checkpoint-1.md` and `-2.md`. There was one cold round, wording only. Full test passes on `main` (620), run by the overseer, who also read the full diff.

**Net shipped: −76 words.**

### What landed

- **One scope shape for both orchestrators' end-of-run review:** the commits the run made for its own units, each read as its own diff, plus uncommitted work and untracked files. In execute those are the Task commits found by their `(<task-id>)` subject tokens; in fix-issue, the commits `**Progress:**` records. The prompt states the reason: a range also takes in work merged onto the branch, which that work's own review covers.
- **Fix-issue had the same exposure.** About 11 live_edit fix-issue manifests worked around it, twice by rewriting `**Pre-session SHA:**`. Fix-issue's §2 drops "Section 11 reads it back".
- **The post-completion prompt** gains "Review it yourself and start no other agent: its results would arrive after you hand back, where nothing reads them."
- **"Subagents cannot spawn subagents"** is deleted from both §5 lead paragraphs. `rationale.md` and the SDD now state the design instead: only the orchestrator dispatches Agents.
- **The overseer's addition, same class:** fix-issue's `## Engineer's diff (path)` is `git diff HEAD`, so it holds this Issue's uncommitted work only.

### Residuals accepted

- Merge-step and other non-unit commits are out of scope, by design.
- A reviewer reading per-commit diffs sees intermediate states, and reads the files on disk for the final one.
- **live_edit-xd1:** a planner-ordered WIP commit mid-Issue means the Doc Writer's diff shows only the work since that commit. An off-skill commit caused it, and the old form was also wrong there.

### Watch

- A side lane's boundary review covers only its own work.
- No post-completion reviewer spawns agents.
- Fix-issue batches on merged branches review only their Issues.
