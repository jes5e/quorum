---
id: b.w74
type: bee
title: Commit steps stage whole hive directories, including .hive/identity.json; stage only the ticket directories a run changed
parent: null
reference_materials: null
created_at: '2026-11-17T09:55:00.568147'
status: done
schema_version: '0.1'
guid: w74xauanw1e7da4184zqtzoysech8ws2
---

## Description

Quorum's commit steps stage whole hive directories, so a hive's own configuration (`.hive/identity.json`) is committed along with the tickets. In a repo that tracks that file, and whose worktree registration modifies it locally, a run would commit one worktree's local configuration over the shared file. Quorum should stage only the ticket directories a run changed, and never a hive's `.hive/` configuration.

### Evidence (live_edit, 2026-11-17 overnight)

- **Three runs stopped at a deferral-hygiene Encode gate** rather than let `hive_commit.py` encode-commit run: an Epic 4 chain Task under `/quo-execute`, a `/quo-fix-issue` run, and one lane's Task. Each would have staged `.bees/specs/.hive/identity.json`, which is modified locally after the lane worktree's hives are registered (`/quo-setup` or `bees colonize-hive --scope`).
- **live_edit tracks the three `identity.json` files.** Its worker rules forbid committing them. Nothing wrong was committed; the encode edits rode each unit's own commit.
- **Three questions:** three times in one night, loud (each run stopped), and not recovered unaided: each needed the planner, then the operator.
- **Interim workaround, sanctioned by the operator 2026-11-17:** after `bees update-ticket … --body-file`, stage only the edited ticket's directory and commit with the helper's exact subject.

### Where quorum stages whole hives (to confirm at Checkpoint 1)

- `skills/quo-execute/scripts/hive_commit.py`, encode-commit mode, which `git add`s every in-repo hive path. Callers: `/quo-execute`, `/quo-fix-issue` and `/quo-breakdown-epic` deferral hygiene.
- `/quo-execute` §8 close-out step 3: stages the resolved Plans hive path.
- `/quo-breakdown-epic`'s per-Epic commit and its "Fix in this session" commit: stage resolved hive paths.
- `/quo-plan`'s commit: stages the Plans and Specs hive paths.
- **Already right:** `/quo-fix-issue` §8 stages `<issues-path>/<issue-id>`. Check `/quo-file-issue` too.

### Goal and constraints

- **One rule, one home where possible:** a commit stages the ticket directories the run changed, never a hive's `.hive/` configuration. Prefer fixing the helper so callers inherit it, over rewording each caller. Fix the class: every caller above at once.
- **Contracts kept:** the encode commit subject (`Encode deferral: /<skill> — <N> deferral(s) encoded`), and `skipped: nothing staged`. A hive outside the repo still stages nothing. Never `git add -A`.
- **Design rules:** no new shell recipe without paired POSIX and PowerShell forms. The helper stays plain Python with tests in `tests/test_hive_commit.py`.
- **Neutral:** no live_edit names. The reason (tracked hive configuration a worktree modifies) goes in the helper's docstring or commit, not in skill prose.
- **Out of scope:** whether bees registration should modify `identity.json`. That's an upstream bees question for the operator.

## Closed (2026-11-17)

Merged by fast-forward from `8cab092` to `83f7fdf`, with the operator's go: "yes" at Checkpoint 1, with the overseer's scope change, then "yes" to merge.

**Commits:**
- `f507c4b`: the draft and tests;
- `83f7fdf`: cold round 1 (three wording nits).

The work was Worker 1's. Its checkpoints are `~/.quorum-overseer/bw74-checkpoint-1.md` and `-2.md`. Full test passes on `main` (608), run by the overseer, who also read the diff.

**Net shipped prose: −162 words** (`/quo-file-issue` −145).

### What landed

- **`hive_commit.py` gains a `stage` mode.** It `git add`s each named in-repo hive except its `.hive/` configuration directory, using the pathspec `:(exclude)<hive>/.hive`, then prints each staged hive's path. It never commits. `encode-commit` stages through the same function. `resolve-hive-paths` is unchanged.
- **The reason** is in the helper, beside `HIVE_CONFIG_DIR`: a repo may track hive configuration that a worktree's hive registration rewrites locally.
- **Every site that staged a whole hive now calls `stage`:** execute §8 step 3, breakdown's commit and its Fix in this session, `/quo-plan`'s commit, and `/quo-file-issue` §4. The three Encode callers inherit the exclusion with no prose change.
- **Unchanged:** `/quo-fix-issue` §8's per-Issue staging.
- **The scope stays the whole hive.** The overseer changed the design at Checkpoint 1, because 5m's Analyst Approve wrote into other Plan Bees' Tasks (`run-state-quo-execute-b.9nd-history.md`:9), and b.txn sanctions that pattern. Bee-directory staging would have left those edits uncommitted.
- **Seven tests.** Five of them fail on the old code.

### Watch

- live_edit's Encode commits run through the helper again, with no stop, and never carry `identity.json`.
- The interim explicit-path workaround is retired once this is synced.
- The upstream bees question is still open, for the operator: should worktree registration modify a tracked `identity.json` at all?
