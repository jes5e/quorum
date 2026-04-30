---
name: bees-execute
description: Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.
---

## Overview

This skill orchestrates the work for a complete Bee ticket by:
1. Finding the Bee to work on and validating it is ready
2. Finding the best Epic to work on
   2.1. Validating the Epic is unblocked
   2.2. Validating the Epic description still makes sense after reviewing work completed in previous Epics
3. Forming a Team to complete the work described in the Epic
   3.1. Sending questions and requests for clarification or guidance to the caller
   3.2. Creating one git commit per Task that includes all changes for that Task
4. Looping 2-3 until all Epics are done, then:
   4.1. Disbanding the execution Team
   4.2. Forming a new Review Team
   4.3. Addressing issues found by the Review Team
   4.4. Getting User approval
   4.5. Marking Bee and all child tickets as closed
   4.6. Outputting a final summary

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Plans hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `plans`.
- CLAUDE.md contains a `## Documentation Locations` section. Agents look up paths to architecture docs, customer docs, test guides, etc. by exact key from this section.
- CLAUDE.md contains a `## Build Commands` section, and that section has all five required bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. Agents look up build/test/format/lint commands by exact key from this section.
- CLAUDE.md contains a `## Skill Paths` section with the `Force clean team script` key. This is the absolute path to `force_clean_team.py` — used as the recovery step when `TeamDelete` fails. `/bees-setup` writes this section based on whether the bees-workflow skills are installed globally or per-project.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The Build Commands section is required, not optional.

Do not attempt to recover from a missing precondition by improvising commands or guessing paths — fail fast and direct the user to `/bees-setup` so the configuration is captured deliberately.

### 1. Find Bee to work on and validate

The user will either call without arguments, with a Bee id or with an Epic ID:
- If called without arguments, find all bees for this repo and ask the user which one they want to work on
- If called with a Bee id, find all Epics in the `ready` state that are unblocked and ask which one they want to work on
- If called with an Epic id, find the Bee that is a parent of that Epic and use that Bee

You will ultimately get the Bee ID you need to work on.
Validate it is ready for work:
- Must have a status of `ready` or `in_progress`
- If it has `up_dependencies` they must be in `done` state (a dependency in `ready` state is fully planned but not yet worked — that's a pending blocker, not a satisfied one)

#### Choose agent model preference

Before starting work, ask the user which model to use for the support roles (Doc Writer, Product Manager, Doc Reviewer). Use `AskUserQuestion`:

- Question: "Which model should support agents (Doc Writer, Product Manager, Doc Reviewer) use?"
- Options:
  - **Opus (Recommended)** — highest quality, slower, more expensive
  - **Sonnet** — fast and cost-effective, good for straightforward tasks

The core implementation roles (Engineer, Test Writer, Code Reviewer, Test Reviewer) always use **Opus** — this is not configurable. Store the user's choice and apply it when spawning agents throughout this Bee.

#### Validate isolation strategy

Check whether you are running in an isolated context for this Bee's work. There are three scenarios:

**Scenario A — Already in a worktree.** You are in a git worktree whose directory name matches the Bee (e.g., `b_Wx7` for `b.Wx7`). This is the expected path when launched via `/bees-worktree-add` or `/bees-fleet`. Proceed directly — no action needed.

**Scenario B — On an existing branch in the main repo.** You are in the main repo checkout but *not* on a worktree. This happens when the user invoked `/bees-execute` directly in their terminal. Present an AskUserQuestion with these options:

1. **Create a feature branch (Recommended)** — Create a new branch (e.g., `bee/b.Wx7`) from the current HEAD and do all work there. This keeps main clean and allows the user to review, squash-merge, or discard the work later. At the end, instruct the user to merge the branch or open a PR — `/bees-worktree-rm` does not apply.
2. **Work on current branch** — Commit directly to whichever branch is checked out (tell the user the branch name). Appropriate if the user is already on a feature branch or intentionally wants commits on main.
3. **Set up a worktree instead** — Suggest the user run `/bees-worktree-add` to create an isolated worktree and spawn an async agent. This is the right choice when the user wants fire-and-forget execution in a separate tmux session. Exit after giving this advice — do not proceed with work.

In the question, always state:
- The current working directory
- The current branch name
- That option 1 creates a local branch only (no remote push)

### 2. Find Epic to work on and validate

Find all Epics in the Bee and recommend the best one to work on first:
- Must have a status of `ready` or `in_progress`
- If it has `up_dependencies` they must be in `done` state


#### Check if stale
Be aware that the Epic was written before coding started. If the Epic has `up_dependencies` that have been completed then
you must review the work actually done in those Epics to see if this current Epic description is stale:

1. Review the git diff to understand what was actually implemented
2. Read the upcoming Epic and its Tasks/Subtasks
3. Update any Task or Subtask descriptions that are now stale given what was actually built in those prior Epics (e.g., file paths changed, function signatures differ, new modules were created)

#### Mark status when ready to start work

If ready, mark the Epic status with `status=in_progress` to show work has started on the Epic

### 3. Form Team to Execute Tasks

Before forming the Team, load all Tasks and Subtasks for the Epic:
- Use `show_ticket()` on the Epic to get the `children` array (Task IDs)
- For each Task, fetch its full details including its own `children` array (Subtasks)
- Read every Subtask — these contain the detailed instructions (Context, What Needs to Change, Key Files, Acceptance Criteria) that the team must follow
- Sort Tasks in dependency order (check each Task's `up_dependencies`) to ensure no Task is blocked when executed
- Verify at least 1 Task exists with at least 1 Subtask, and all are ready for work: `status!=drafted`
- Mark the current Task with `status=in_progress` to show work has started
- Mark the Bee with `status=in_progress` to show work has started (if not already set)

#### Team lifecycle

Create **one team per Epic** (e.g., `epic-9v`) and reuse it across all Tasks in that Epic. This avoids repeated team creation/deletion and the shutdown-timing issues that come with it.

- **Agent naming**: Use task-scoped names to avoid collision with agents that haven't fully shut down yet. For example, for Task `xb`: `engineer-xb`, `test-writer-xb`, `pm-xb`. This ensures unique routing regardless of shutdown timing.
- **Between Tasks**: Send shutdown requests to current agents, delete completed tasks from the task list, then spawn new agents with new task-scoped names. Do NOT call `TeamDelete` between Tasks.
- **At Epic boundary**: Call `TeamDelete` to clean up the team. By this point all agents from the last Task have had ample time to terminate. If `TeamDelete` fails due to a stuck agent: (1) read the absolute path to `force_clean_team.py` from CLAUDE.md `## Skill Paths` (key: `Force clean team script`) and run `python3 <that-path> <team-name>` to remove directories, then (2) call `TeamDelete` again to clear session state. Then proceed to create the next team.

Create agents on the team to work on an individual Task.
**IMPORTANT: You must stay in `delegate` mode. Do not take on work, delegate work to Team members.**

Choose which Team members are required.
- If source code is being modified or created, spawn the Engineer.
  - **The Engineer is responsible for source code. It does *not* know how to update unit tests or docs!**
- If test code is being modified or created, spawn one or more Test Writers.
  - **The Test Writer is responsible for unit tests. It does *not* know how to update source doe or docs!**
  - If there are multiple files that need updating, the Task should have one Subtask per file
  - If so, spawn multiple Test Writers to work on each Subtask and File in parallel
  - It might be necessary to order them so that the first one creates or modifies any shared fixtures
- If docs need to be modified or created, spawn the Doc Writer.
- If this is the first time forming the team, **always** spawn the Product Manager.
  - If you are re-forming the team to address Code, Doc and Test Reviewer feedback you may **optionally** choose to not spawn the Product Manager, if the work is minor enough and will not impact Product functionality

The team may consist of any of the following agents, but the Product Manager must always be spawned.
**Use task-scoped names** when spawning (e.g., for Task `xb`: `engineer-xb`, `test-writer-xb`, `pm-xb`):

#### Testing discipline — avoid redundant full-workspace runs

Test and lint commands form a ladder; each rung is more expensive than the last. Stay on the lowest rung that catches the issue you might have introduced. Look up the actual commands from the project's `## Build Commands` section in CLAUDE.md — the lookup keys (`Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`) are referenced throughout this skill.

1. **While iterating on a file** (Engineer, Test Writer): use the **Narrow test** command (single file or package), and the **Lint** command at the same scope when supported. Do NOT run the full suite while iterating.
2. **At subtask boundary**: run **Narrow test** + **Lint** for the file/package you touched. Do NOT run the **Full test** yet.
3. **At the Task's final `.T` (or equivalent) subtask**: this is the single **authoritative** **Full test** run, plus **Lint** at workspace scope, plus a **Format** check. It is the only place the full suite must run.
4. **Product Manager review**: trust the `.T` subtask's output unless you have a specific reason to re-run (e.g., the engineer reported skipping something, or you can see stale `.bees/` state). Do not re-run the full workspace suite by default — repeating it adds minutes per Task for no new signal.
5. **Director (before commit)**: run **Format** only. Do not re-run tests — the team has already validated.

**When a Task only touches one package's tests** (e.g., adding files under that package's `tests/` directory), that package's own test binary is the only thing that can regress. Do not invoke workspace-wide tests against unrelated packages — they cannot fail from a test-only change in another package.

Apply the same principle to **Lint**, **Format**, and any docs-build command: scope narrowly while iterating; run workspace-wide once at `.T`; trust the result downstream.

#### Running long commands

Use the Bash tool's `timeout` parameter (max 600000 ms = 10 min). For test invocations of any length up to that, dispatch in the foreground: `Bash(command: "<your project's test command per CLAUDE.md>", timeout: 540000)`. The harness blocks until the command exits and returns the output; if the command hangs, the harness kills it at the timeout boundary. For runs that legitimately exceed 10 min, use `Bash(run_in_background: true)` and wait silently for the task-completion notification — Read the output file when it arrives. Do not write shell polling loops to wait for completion; the harness handles notification on its own.

- Engineer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Executing implementation Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - Read the Subtask description using the bees CLI — it contains Context, What Needs to Change, Key Files, and Acceptance Criteria
    - Review any relevant internal architecture docs referenced in CLAUDE.md under "Documentation Locations"
    - Review the existing code to determine the current state
    - Review the engineering best practices guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute each implementation Subtask following the instructions in its description
    - There may be one or many implementation subtasks
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
    - **Compile-check discipline:** Look up the **Compile/type-check** command from CLAUDE.md `## Build Commands` and run it after each subtask. Fix errors before moving on. If the project's Compile/type-check entry is empty (interpreted languages without a static type-checker), skip this rung — the **Narrow test** rung still applies. Also run **Lint** at narrow scope after each subtask where supported.
    - **Scope your test/lint runs narrowly** while iterating — use the **Narrow test** and **Lint** commands from CLAUDE.md `## Build Commands` (e.g. for a Rust crate, **Narrow test** typically resolves to `cargo test -p <crate>`; for a Node project, to `vitest run <path>`). The full-suite run happens once at the Task's `.T` subtask. See "Testing discipline — avoid redundant full-workspace runs" above.
- Test Writer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Executing testing Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - Use the test writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Use the test review guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute all test subtasks to change, add or delete tests
    - Review the work of the Engineer and see if any tests need to be added, deleted or updated based on that work
      - It is possible the testing subtasks were incomplete
      - Review the work of the Engineer to find any gaps, then add, delete or updated required tests
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
    - **Scope your test/lint runs narrowly** while iterating — use the **Narrow test** and **Lint** commands from CLAUDE.md `## Build Commands`. The authoritative workspace-wide run happens once at the Task's `.T` subtask. See "Testing discipline — avoid redundant full-workspace runs" above.
- Doc Writer
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Responsibilities:
    - Execute documentation Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - Use the doc writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute any customer-facing docs subtasks
    - Execute any internal architecture docs subtasks
    - Review the work of the Engineer and see if any docs need to be updated based on that work
      - It is possible the doc subtasks were incomplete
      - Review the work of the Engineer to find any gaps, then update docs
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
- Product Manager
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Responsibilities:
    - Responsible for reviewing Task work against the spec source — either the PRD/SDD linked from the Grandparent Bee's egg, or the Grandparent Bee body itself when the egg is null/empty
    - Ensures that the work that was done meets the requirements
    - Surface design questions back to the Caller
      - If the team proposes different approaches to a problem, surface this back up to the caller with an AskUserQuestion
    - Responsible for providing report to share back up to calling Agent
    - Ultimately responsible for the quality of the Task work and correctness of the output of the Team
  - Instructions:
    - Get the Task using the bees CLI and read it.
    - Read all Subtasks (children of the Task) — these contain the detailed work instructions.
    - Read the Parent Epic.
    - Read the Grandparent Bee.
    - Read the source material linked in the Grandparent Bee. **If the Grandparent Bee's egg is null/empty** (Plan Bees authored via `/bees-plan` for features without a separate PRD/SDD), the Bee body itself is the authoritative spec source — read it carefully in place of the egg sources, and substitute "the Plan Bee body" wherever subsequent prose references "the PRD" or "the SDD".
    - Make sure the Test Writer and Doc Writer review the work of the Engineer
      - The Engineer's output needs review by the rest of the team
    - Review quality of Task and Subtasks efforts, make final decision when to present completed Task to caller
    - Review the Task and Subtasks execution to ensure that the work:
      - Aligns with the requirements
      - Does not introduce more functionality than asked for
        - e.g The PRD calls for no legacy support but the Engineers proposes a task for backwards compatibility.
        - Call this out as unacceptable
      - Review all Tasks once they are complete against the Epic to ensure that:
        - The work will meet the Acceptance Criteria
        - The work covers all functionality required by the Epic
        - The work does not introduce any functionality not required or explicitly disallowed in the Epic
    - Uses the code-review and doc-review skill after work has been done for quality control
      - NOTE: These skills could infinitely return work items
      - Product Manager must use judgement when deciding whether to ask the Team to make the improvements or not
      - If the Product Manager decides to ignore code-review or doc-review feedback, this MUST be included in the end of task summary report for review
    - **Trust the Task's `.T` subtask output** — do NOT re-run the full workspace test suite / clippy by default. The `.T` subtask is the authoritative workspace-wide validation run. Only re-run if you have a specific reason (engineer reported skipping something, stale `.bees/` state, etc.). See "Testing discipline — avoid redundant full-workspace runs" above.
    - **Cross-Task and cross-Epic interaction check** — per-Task code review naturally focuses on the Task's own diff. The PM is responsible for the wider view. Before approving a Task, explicitly verify:
      - **Contract consistency with sibling Tasks in the same Epic.** Read the other Tasks in this Epic. For each function/API this Task modifies, find sibling Tasks that call or assume behavior from it and verify those assumptions still hold. Example: if this Task reorders steps inside an `auth_middleware`, a sibling Task whose request-handler docstring says "by this point the request is signature-verified" must be cross-checked against the new ordering.
      - **Contract consistency with completed sibling Epics.** If prior Epics in this Bee already landed code that interacts with what this Task changes, re-read the relevant diffs (via `git log` / `git diff` on the branch) and verify the interactions.
      - **Cumulative resource accounting.** If this Task adds acquires from a bounded resource (connection pool, semaphore, queue slot, in-memory map, etc.), sum across all call sites — including call sites in sibling Tasks and sibling Epics — and flag lifetime mismatches or starvation scenarios. Example: a new long-lived consumer sharing a pool with short-lived transaction writers will starve writers at steady state.
      - **Symmetric lifecycle coverage.** If this Task introduces a new resource (persistent key, file, pool entry, in-memory entry, etc.), grep the codebase for every cleanup/teardown path for the adjacent resource class and verify this new resource is handled symmetrically. Example: adding a new `cache:user:{id}:permissions` key class in the write path requires the cache-invalidation path, the user-deletion path, and any periodic-purge job to all DELETE this key class — otherwise stale-permissions data leaks past role changes.
      - **New-pattern-exposes-old-code.** If this Task introduces a new call pattern for an *unchanged* function (new frequency, new argument combination, new temporal pattern), mentally run that unchanged function under the new pattern and flag any latent assumptions the new pattern breaks. Example: `get_user_profile(id)` is fine when called once per request from the request hot path, but a new batch endpoint that calls it for hundreds of IDs in a tight loop may miss the per-request memoization reset and leak stale data from the prior request into the next.
    - Provide report when done. Must include:
      - Any ignored reviewer feedback
      - Any contentious topics between team members
      - Any design decisions that were made that conflicted with work described in tickets
      - Any incomplete work
      - Any cross-Task / cross-Epic interaction issues discovered during the wider-view check, and the resolution


#### 4.1 After Each Task

When a Task and all its Subtasks are done (all reviewer feedback addressed or ignored):

1. Mark the Task as `status=done` (Subtasks were marked done by each agent as they completed their work). **Do this before committing** so the `.bees/` status changes are included in the commit.
2. Create one git commit for the Task. **NEVER push to remote — committing only.** Use this staging procedure:
   1. Run the **Format** command from CLAUDE.md `## Build Commands` (e.g. `cargo fmt`, `prettier --write`, `gofmt -w`) to normalize formatting (agents may have triggered reformatting in files they didn't report). Do NOT re-run the test suite here — the `.T` subtask already validated, and the PM confirmed. Re-running wastes minutes per Task.
   2. Run `git status` to see the full set of modified and untracked files.
   3. Stage files that are related to this Task — include agent-reported files, `.bees/` ticket changes, and any formatting changes to files that were touched by this Task's agents. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this Task.
   4. Commit with a descriptive message per system/project git guidance.
3. Send shutdown requests to all current agents. Delete completed tasks from the task list.
4. Output the summary below to the screen and continue to the next Task (spawning new agents with new task-scoped names on the same team).

```
## Task [N] of [total] Complete: [task-title]

**Task ID**: <task-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Ignored Review Feedback**: [list items that were flagged by code-review or doc-review but Director chose not to address, or "None"]
**Follow-up Tasks Created**: [count, if any] [list task-ids if created]
One of:
- Proceeding to next Task <task-id>
- Final Task, moving on to Final Reviews 
```

#### 4.2 Find next Epic or move to Final Review

Before moving on from the just-completed Epic, perform an **inter-Epic interaction checkpoint**. This is a lightweight check deliberately positioned here (not at the final Bee-level review) so that issues introduced by this Epic's code interacting with *prior* Epics' landed code are caught while the context is fresh, before the next Epic compounds the problem.

The Director (you) runs this check directly — no new team:

1. Diff the Epic's landed commits against the previous Epic's end-state: `git log --oneline <previous-epic-last-commit>..HEAD`.
2. For each file this Epic touched that a prior Epic also touched, scan for:
   - **Contract drift** between what this Epic's code assumes and what a prior Epic's code actually does (especially ordering contracts, docstring claims, and "this should never happen" comments).
   - **Resource compounding** across Epics: if this Epic adds acquires from a resource that a prior Epic already uses, model the aggregate.
   - **Symmetric-change gaps**: if this Epic added a new resource class (key pattern, pool, queue, etc.), search prior Epics' cleanup paths for missing handling.
3. If any issue is found, spin up the Engineer (via a fresh team using the just-disbanded pattern) to fix it before continuing to the next Epic. Do not defer to the Final Bee-level review — fixing at the Epic boundary keeps the scope local to the two Epics involved.
4. Record any fixes as additional commits on the branch, clearly labeled.

After the checkpoint passes (clean or fixed):

If there are more Epics to work on, ask the user if they want to continue with the next logical one. If so:
1. Mark the Epic as `status=done`
2. Call `TeamDelete` to clean up the Epic's team. If it fails due to stuck agents: (1) run `python3 <path-from-CLAUDE.md-Skill-Paths-Force-clean-team-script> <team-name>`, then (2) call `TeamDelete` again to clear session state.
3. Clear your context window and go back to step 2 (which will create a new team for the next Epic).

If not, move to final Bee review.

### 5. Final Bee-level Code, Doc and Eng reviews

Once all Epics in the Bee are done:
- `TeamDelete` the last Epic's team (if it still exists). If stuck: (1) `python3 <path-from-CLAUDE.md-Skill-Paths-Force-clean-team-script> <team-name>`, (2) `TeamDelete` again to clear session state.
- Form a new review Team (e.g., `bee-review-<bee-id>`) to check their work. Use task-scoped agent names (e.g., `code-reviewer`, `test-reviewer`, `doc-reviewer`).

If you invoked the Engineer in the first team, invoke the Code Reviewer in this team.
If you invoked the Test Writer in the first team, invoke the Test Review in this team.
If you invoked the Doc Writer in the first team, invoke the Doc Reviewer in this team.

- Code Reviewer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Review the output of the Engineer
    - Provide feedback where the work of the Engineer was not up to standards
  - Instructions:
    - Invoke the /code-review skill
- Test Reviewer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Review the output of the Test Writer
    - Provide feedback where the work of the Test Writer was not up to standards
  - Instructions:
    - Invoke the /test-review skill
- Doc Reviewer
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Responsibilities:
    - Review the output of the Doc Writer
    - Provide feedback where the work of the Doc Writer was not up to standards
  - Instructions:
    - Invoke the /doc-review skill
- Get the feedback, and make a judgement call about whether that work must be done
  - If so, **reform or re-use the first team** to do the work
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** spawn the Product Manager on this iteration
    - Spawn any team members required to do the work you deem necessary from the reviewer team
  - If not, move on to Final Review but you MUST share the ignored feedback for review
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in Final Review


### 6. Post-Completion Code Review

After the review loop in step 5 is done and all fixable issues have been addressed by the team, run one final `/code-review` across all changes made by this Bee (diff against the base branch or the state before work began). This is an independent quality gate — separate from the per-Task and per-Epic review cycles above.

1. Invoke the `/code-review` skill against all changes in this Bee
2. Present the findings to the user
3. If there are no issues, report "Code review: no issues found" and continue to Final Output
4. If there are issues, use `AskUserQuestion` to ask:
   - Question: "Post-completion code review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now before closing the Bee
     - **File as issue tickets** — create issue tickets via `/bees-file-issue` for each issue
     - **Skip** — acknowledge and move on without action
5. Execute the user's choice:
   - **Fix in this session**: Reform the implementation team and delegate the fixes. Stay in delegate mode. After fixes are done, commit and continue to Final Output.
   - **File as issue tickets**: For each issue, invoke `/bees-file-issue` with the issue description. Report the created ticket IDs to the user.
   - **Skip**: Continue to Final Output.

### 7. Final Output

When **all** Epics in the Bee are done, you must show the User the full list of all Reviewer feedback you chose to ignore.
- Use the AskUserQuestion tool to ask the User if they want you to act on any of these, or just continue.

For each Acceptance Criteria, either demonstrate it directly (via test or script) or instruct the user how to validate it manually. Then use `AskUserQuestion` to get official sign-off on the Acceptance Criteria.

Then use `AskUserQuestion` with:
- Question: "Are you ready to mark this Bee as done?"
- Options:
  - "Yes, mark as done"
  - "No, we have more work to do"

### 8. Mark Bee Complete

Once the user approves the Bee as done:

1. Mark all Epics in the Bee as `status=done`:
```bees
update_ticket(ticket_id="<epic-id>", status="done")
```

2. Verify all Epics are now `done`, then mark the Bee itself:
```bees
update_ticket(ticket_id="<bee-id>", status="done")
```

### 9. Output Final Summary

```markdown
## Bee Execution Complete: [bee-title]

**Bee ID**: <bee-id>
**Epics Completed**: [count]
**Tasks Completed**: [count]
**Bee Status**: Finished

All work has been synced to git.
```

### 10. Further testing and merging

Instruct the user to perform whatever further testing they want to do, then advise on merging based on the isolation strategy chosen in step 1:

- **Worktree** — Invoke the `/bees-worktree-rm` skill to merge the worktree branch and clean up the worktree directory.
- **Feature branch** — Instruct the user to merge the branch (e.g., `git merge bee/b.Wx7`) or open a PR. Do NOT push to remote unless the user asks.
- **Worked on main/current branch** — Commits are already on the branch. Remind the user that the work is committed locally and they can push when ready.