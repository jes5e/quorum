---
id: b.nhw
type: bee
title: Name /quo-execute's manifest after the ID the run was started with, so runs on different Epics of one Bee don't share a file
parent: null
reference_materials: null
created_at: '2026-11-15T15:06:28.799231'
status: done
schema_version: '0.1'
guid: nhwz1yxqbrquc3koxhxgxmixp8u3fyig
---

## Description

`/quo-execute` names its run-state manifest `run-state-quo-execute-<bee-id>.md` and accepts that "two concurrent `/quo-execute` runs against the same Bee share one file". A real run has now shown that this is wrong.

### Evidence (live_edit, 2026-11-15; operator go)

- Plan Bee b.f9p's Epic 3 run is paused at a Task waiting for an operator-scheduled dev window. Its resume state is in `run-state-quo-execute-b.f9p.md`.
- The operator started Epic 4 with `/quo-execute t1.f9p.mh` in another worktree. Run start step 2 supports exactly that ("An Epic ID: use its parent Bee, and start at that Epic").
- Under §2, that run's manifest path is the paused run's file, and two things break:
  - §2's validation would read it as this run's own stopped run (same Bee scope, `Next unit` not `none`) and resume Epic 3's state;
  - a fresh write would truncate it.
- The planner improvised a different filename (`run-state-quo-execute-b.f9p-e4chain.md`), which the operator doesn't allow. It also isn't safe: after a compaction the orchestrator recomputes the path from the skill text and lands on Epic 3's file.
- The Epic 4 run is on hold until this lands.
- Evidence files (container `/tmp/.quorum/`, host `~/.quorum-scratch/`): `run-state-quo-execute-b.f9p.md`, `run-state-quo-execute-b.f9p-e4chain.md`.

Three questions: the first occurrence. It was loud, but the only recovery was an improvised name that isn't safe across a compaction, and a real run is blocked.

### The change

The discriminator is the ticket ID the run was started with: the Bee ID for a Bee-ID or no-argument run, and the Epic ID for an Epic-ID run.
- It's as recomputable after a compaction as the Bee ID is today, because it's the run's own argument.
- It still fits the mirrored lead statement ("the most re-derivable ticket ID their run has").
- Replace the "Accepted collision" sentence with what remains true: two runs started with the same ID still share one file.

### Constraints

- **Contract change; define before writing.** Name every reader of the manifest path and of `**Unit scope:**`, and edit each in the same pass:
  - §2's filename and validation;
  - §3's re-read;
  - every printed resume command (execute's hand-off and guard lines, and the delegated-gates reference), which must re-invoke with the same ID;
  - the README and docs, and any test that pins the name.
- **Keep the mirrored manifest lead statements byte-identical** across execute, fix-issue and breakdown (`MANIFEST_LEAD_STATEMENTS`). Only execute's own filename sentence and its collision note change.
- **Out of scope:**
  - Epic and Bee status writes. Bee-done already requires every Epic done.
  - Task-level parallelism (declined).
  - `/quo-fix-issue` and `/quo-breakdown-epic` naming.
- **Small:** a goal-level edit to the sentences that decide the name. No refusal gate, no lock files.

## Process

A small hand-edit batch, in a worktree:
1. **Checkpoint 1:** the design, with no edits. Every reader of the manifest path and unit scope, the wording, and the word deltas.
2. **The draft.**
3. **One cold review under the exit rule,** with role-plays:
   - (a) the live_edit case: Epic 3 paused under `b.f9p`, Epic 4 started with `t1.f9p.mh`. Separate files, and each resumes its own after a compaction;
   - (b) a Bee-ID run's printed resume command still re-finds its file;
   - (c) an Epic-ID run that carries on into the next Epic in multi-Epic mode keeps its own file.

Once merged, the operator's sync script can apply it mid-run. The Epic 4 run then renames its file to the new name and resumes.

## Closed (2026-11-15)

Merged by fast-forward to `00c2d71`, rebased onto `a6d7542`, with the operator's go:
- `faa91bd`: the draft;
- `bcf3e61`: cold round 1;
- `00c2d71`: cold round 2, with no behavior findings.

The work was Worker 1's, in worktree `quorum-worktrees/bnhw-manifest-name`, now removed. Its checkpoints are `~/.quorum-overseer/bnhw-checkpoint-1.md` and `-2.md`. Full test passes (601), run by the overseer, who also read the full shipped diff.

**Net shipped: +3 words.**

| File | Change |
|---|---|
| execute | +10 |
| `rationale.md` | −7 |

### What landed

- **The filename:** `run-state-quo-execute-<start-id>.md`, where `<start-id>` is the Epic ID for a run started with one, otherwise the Bee ID.
- **The collision note:** two runs started with the same ID share one file.
- **Unchanged:** `**Unit scope:**` stays `Bee <bee-id>`, so a renamed file still validates.
- **The tracker lookup:** "at this run's path".
- **Run start:** step 6 alone selects the Epic ("on the first pass unless it is `done`"), and step 2's duplicate is cut.
- **§8:** the resume command and the re-run print use `<start-id>`.
- **Also edited:** the rationale, the SDD, two test anchors, and a REWRITE-BRIEF amendment (A2/A3/A5).

### Cold rounds

- **Round 1, F2 (behavior):** "if it is workable" silently switched a fresh run off a drafted named Epic. It became "unless it is `done`".
- **Round 1, F1:** the cross-run Epic-selection gap was declined as a prediction that predates this change. Rationale L32 kept "against the same Bee".
- **Round 2:** wording only, including step 2's duplicate selection being cut.

### Caution, given to live_edit

An Epic-ID run that moves past its own Epic picks the first workable Epic, which can be one another run has paused. Live_edit's Epic 4 run is to start fresh after its re-plan, with no rename needed.
