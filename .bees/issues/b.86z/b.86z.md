---
id: b.86z
type: bee
title: Epic-wide contracts live once in the Epic and reach every implementer; breakdown sizes Tasks by the change, not by ticket text
status: open
created_at: '2026-11-15T15:21:45.581654'
schema_version: '0.1'
reference_materials: null
guid: 86z4w82bq8fnr35u42ayot2q1tc6zmns
---

## Description

Epic-wide contracts and rulings get copied into every Task's tickets. Breakdown then splits Tasks whose text grows too large, and every extra Task pays /quo-execute's fixed per-Task cost. Two quorum design points drive the copying:
- `/quo-breakdown-epic`'s Task-body rule ("A Task body states the Task's purpose and any contract a sibling Task or Epic must respect") asks each Task body to state "any contract a sibling Task or Epic must respect";
- `/quo-execute` §5 hands an implementer only "the Task body and its own role's Subtask bodies", never the Epic's text.

So a contract every Task must respect has to be copied into every Task. Quorum also says nothing about how finely to cut Tasks beyond "one commit's worth of work". The operator agreed on 2026-11-15 to fix both.

### Evidence (live_edit, 2026-11-15)

**Epic 4 of Plan Bee b.f9p** (`t1.f9p.mh`) was broken down into 41 Tasks and 113 Subtasks, up from a 23-Task skeleton. All 18 extra Tasks came from splitting sets over the project's 25–30 KB ticket-text cap.

An audit of the 41 Tasks (1.07 MB) found:
- the work descriptions are dense, about 50–57% of each set;
- 40–50% of each set is repeated overhead: rulings and decisions pasted verbatim (27 KB, several times within one Task), planner stops, size and test boilerplate in 40–41 Tasks, and a doc-writer Subtask in every Task, 11 of them expecting no doc change;
- the Epic's own breakdown section says "Every Task cites this section instead of carrying a copy", but the project's drafting brief required verbatim copies, partly because implementers never see the Epic's text.

The overhead is what pushed sets over the cap.

**Per-Task execution cost**, from 136 mapped Tasks across 27 execute ledgers:
- a fixed floor of about 60–100 agent-minutes and 7–13 dispatches per Task, plus about 30 min per 1,000 changed lines;
- under 1k lines: about 144 min per 1k lines;
- 2–6k lines: 56–64 min per 1k;
- 6k+ lines: rework rises to 53% of the time, half the Tasks need the Analyst, and agents restart about 2.6 times per Task.

So over-splitting costs a full floor per extra Task, and over-sized Tasks cost rework.

The overseer's analysis files are in its session scratchpad. The figures are recorded here. Three questions: it recurs at every breakdown under a size rule, it's silent (each split looks reasonable), and the run did not recover by itself.

### The change (goals; the design is Checkpoint 1's)

1. **One home for Epic-wide contracts and rulings: the Epic's text.** Breakdown records them there once, under a section heading that both skills key on, and Tasks cite them by label. A Task body states only what is specific to it, including a contract between two particular sibling Tasks.
2. **`/quo-execute` gives every implementer, and every reviewer or PM that checks against the spec, that Epic section beside its Task.** Define how: embed it, or name it for the agent to read. Weigh the relay table's existing rules and size.
3. **One goal sentence on Task size in breakdown, with its reason:**
   - every Task pays a fixed execution cost, so cut Tasks by the change, not by ticket text;
   - prefer one coherent change with its design settled;
   - a doc-writer Subtask only where docs change.

   No project numbers: the per-line figures above are live_edit's, and stay out of skill text.

### Constraints

- **Define-before-write** for the section heading (a contract between breakdown and execute). Name every reader: breakdown's drafting and PM review, execute §5's relay, the PM role file (spec traceability), the Analyst (already reads the Epic), post-completion, and docs.
- **Restructure; don't append.** Reword breakdown's Task-body contract sentence and execute §5's "Each implementer receives…" rather than adding beside them.
- **Mirrors:** `/quo-fix-issue` has no Epic, so check whether any Tier-1/Tier-2 mirrored text changes. If it does, keep the mirror honest.
- **Ticket-system neutral:** "the Epic's text", not bees mechanics.
- **Out of scope:**
  - project size caps and drafting briefs (live_edit's);
  - Task-level parallelism (declined);
  - measure-first (a separate batch).

## Process

A hand-edit batch in a worktree. It starts after b.nhw merges.
1. **Checkpoint 1:** the design, with no edits. The heading, the relay, the readers, the wording, the word deltas, and any routing or relay change listed for the operator.
2. **The draft.**
3. **One cold review under the exit rule,** with role-plays:
   - (a) Epic 4's case: a ruling every Task must respect reaches each Task's implementer and PM without being copied into the Task;
   - (b) a contract between two specific sibling Tasks still sits in those Tasks;
   - (c) breakdown of a 23-Task skeleton under the new size goal doesn't split for text size;
   - (d) a Task whose docs don't change gets no doc-writer Subtask, and execute still handles it.

