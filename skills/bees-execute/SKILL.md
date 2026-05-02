---
name: bees-execute
description: Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.
argument-hint: "[<bee-id> | <epic-id>]"
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

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `"1"` in either `~/.claude/settings.json` or the shell environment. The skill spawns a team unconditionally; without Agent Teams enabled, team-creation tools are unavailable and the skill cannot proceed.
- The Plans hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `plans`.
- CLAUDE.md contains a `## Documentation Locations` section. Agents look up paths to architecture docs, customer docs, test guides, etc. by exact key from this section.
- CLAUDE.md contains a `## Build Commands` section, and that section has all five required bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. Agents look up build/test/format/lint commands by exact key from this section.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The Build Commands section is required, not optional.

Do not attempt to recover from a missing precondition by improvising commands or guessing paths — fail fast and direct the user to `/bees-setup` so the configuration is captured deliberately.

**Verifying the Agent Teams precondition.** Read `~/.claude/settings.json` (or `%USERPROFILE%\.claude\settings.json` on Windows) with the JSON parser, look up `.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. If it is `"1"`, the precondition is satisfied. If absent or any other value, fall back to the shell environment variable `$CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` (POSIX) / `$env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` (PowerShell). If neither resolves to `"1"`, hard-fail with `Run /bees-setup first.` and a one-line note that Agent Teams is not enabled.

```bash
# POSIX (bash / zsh):
python3 -c '
import json, os, sys
p = os.path.expanduser("~/.claude/settings.json")
val = ""
if os.path.exists(p):
    try:
        with open(p, encoding="utf-8") as f:
            val = (json.load(f).get("env") or {}).get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "")
    except (FileNotFoundError, IsADirectoryError):
        val = ""
    except (PermissionError, json.JSONDecodeError, OSError) as e:
        print(f"Warning: could not read {p}: {e!r} — falling back to environment check.", file=sys.stderr)
        val = ""
sys.exit(0 if val == "1" else 1)
' || test "${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}" = "1" || { echo "Run /bees-setup first. — CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is not '1' in settings.json or the environment."; exit 1; }
```

```powershell
# Windows (PowerShell):
$settingsPath = "$env:USERPROFILE\.claude\settings.json"
$fromFile = $null
if (Test-Path $settingsPath) {
    try {
        $fromFile = (Get-Content $settingsPath -Raw | ConvertFrom-Json).env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
    } catch {
        Write-Warning "could not read ${settingsPath}: $_ — falling back to environment check."
        $fromFile = $null
    }
}
if ($fromFile -ne "1" -and $env:CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS -ne "1") {
    Write-Error "Run /bees-setup first. — CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is not '1' in settings.json or the environment."
    exit 1
}
```

### 1. Find Bee to work on and validate

The user will either call without arguments, with a Bee id or with an Epic ID:

- **If called without arguments**, list all Plan Bees in this repo and ask the user which one to work on:

  ```bash
  bees execute-freeform-query --query-yaml 'stages:
    - [type=bee, hive=plans]
  report: [title, ticket_status]'
  ```

  Filter the result to Bees with status `ready` or `in_progress` (those are workable). If exactly one matches, use it. If multiple, present them via `AskUserQuestion`. If none, tell the user no Plan Bees are workable and suggest `/bees-plan` or `/bees-plan-from-specs`.

- **If called with a Bee ID**, find that Bee's `ready` Epic children and ask which one to start with:

  ```bash
  bees execute-freeform-query --query-yaml 'stages:
    - [parent=<bee-id>, type=t1, status=ready]
  report: [title, up_dependencies]'
  ```

  `up_dependencies` is returned as a list of ticket IDs only — not statuses. Collect the IDs across all candidate Epics, then batch-look-up their statuses:

  ```bash
  # After getting the Epic candidates, batch-look-up their up_dependencies' statuses:
  bees show-ticket --ids <dep-id-1> <dep-id-2> <...>
  ```

  For each candidate Epic, check the returned `ticket_status` of its dependencies. An Epic is workable only if all its `up_dependencies` are in `done` status (a dependency in `ready` state is a pending blocker, not satisfied). An Epic with no `up_dependencies` is unblocked by default. Present unblocked candidates via `AskUserQuestion` and recommend the one with the fewest downstream dependencies first.

- **If called with an Epic ID**, walk up to the parent Bee:

  ```bash
  bees execute-freeform-query --query-yaml 'stages:
    - [id=<epic-id>]
    - [parent]
  report: [title, ticket_status]'
  ```

  Use the parent Bee for the rest of the run.

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

**Scenario A — Already in a worktree.** You are in a git worktree whose directory name matches the Bee (e.g., `b_Wx7` for `b.Wx7`). This is the expected path when launched via the optional worktree skills (`/bees-worktree-add`, `/bees-fleet`) if the user has them installed. Proceed directly — no action needed.

**Scenario B — On an existing branch in the main repo.** You are in the main repo checkout but *not* on a worktree. This happens when the user invoked `/bees-execute` directly in their terminal. Present an AskUserQuestion with these options:

1. **Create a feature branch (Recommended)** — Create a new branch (e.g., `bee/b.Wx7`) from the current HEAD and do all work there. This keeps main clean and allows the user to review, squash-merge, or discard the work later. At the end, instruct the user to merge the branch or open a PR.
2. **Work on current branch** — Commit directly to whichever branch is checked out (tell the user the branch name). Appropriate if the user is already on a feature branch or intentionally wants commits on main.
3. **Set up a worktree instead** — If `/bees-worktree-add` is installed (it is not part of the portable core), suggest the user run it to create an isolated worktree and spawn an async agent. Right choice for fire-and-forget execution in a separate tmux session. Exit after giving this advice — do not proceed with work. Omit this option if the skill is not installed.

In the question, always state:
- The current working directory
- The current branch name
- That option 1 creates a local branch only (no remote push)

### 2. Find Epic to work on and validate

Find all Epics under the chosen Bee and recommend the best one to work on first:

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1]
report: [title, ticket_status, up_dependencies]'
```

From the result set, the Epic to work on must:
- Have a status of `ready` or `in_progress`
- Have all `up_dependencies` in `done` state

`up_dependencies` is returned as a list of ticket IDs only — not statuses. Collect the IDs across all candidate Epics, then batch-look-up their statuses:

```bash
# After getting the Epic candidates, batch-look-up their up_dependencies' statuses:
bees show-ticket --ids <dep-id-1> <dep-id-2> <...>
```

For each candidate Epic, check the returned `ticket_status` of its dependencies. An Epic is workable only if all its `up_dependencies` are in `done` status. An Epic with no `up_dependencies` is unblocked by default.


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
- Use `bees show-ticket --ids <epic-id>` to get the `children` array (Task IDs)
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
- **At Epic boundary**: Call `TeamDelete` to clean up the team. By this point all agents from the last Task have had ample time to terminate. If `TeamDelete` fails due to a stuck agent: (1) resolve the path to `force_clean_team.py` as `<this skill's base directory>/scripts/force_clean_team.py` — the base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../bees-execute`). Run it via the platform's Python 3 launcher (`python3 <path> <team-name>` on POSIX, `python <path> <team-name>` or `py -3 <path> <team-name>` on Windows), then (2) call `TeamDelete` again to clear session state. Then proceed to create the next team.

#### Team-lead message-flow choreography

Agent Teams is message-driven — a teammate that finishes processing one ping without a follow-up trigger idles silently, even when all preconditions for its next phase are met. There is no "teammate idle" event the team-lead can subscribe to. The team-lead must therefore proactively route work between teammates as subtask states transition. Workers do work; team-lead routes. Do NOT have workers ping each other directly — peer-to-peer messaging bakes in coupling, breaks when a Task has no Test Writer (research-only Tasks), and obscures the orchestration model.

Apply these rules whenever a teammate reports a state transition:

1. **Engineer reports a subtask is at `status=done`** → team-lead pings the Test Writer with "engineer subtask <id> done — start writing/updating tests for that subtask now". If the Task has no Test Writer (research-only), skip this rung. Re-fire this rung for each Engineer subtask that completes; do not wait for all Engineer subtasks to land before pinging.
2. **Test Writer reports a subtask is at `status=done`** → team-lead pings the PM with "test subtask <id> done — review the per-subtask diff". Re-fire per Test Writer subtask, same as rung 1.
3. **All child subtasks at `status=done`** → team-lead pings the PM with "all subtasks done, run reviews and produce the final Task report". This drives the per-Task PM reviews (`bees-code-review` + `bees-doc-review` per the PM Instructions block) and the per-Task summary.

If a teammate reports done and the next-rung teammate is in a known-not-spawned state for this Task, advance directly without an extra ping (e.g., research-only Task with no Test Writer: Engineer-done routes straight to PM).

#### Don't wait silently on idle teammates — graduated escalation

Pings can be missed. When a teammate has gone silent past the work it was asked for, the team-lead's job is to notice and escalate, NOT to keep printing "Waiting" turn after turn. Apply this ladder:

1. **First nudge (~10 min after ping):** light status check. "Just checking — any blockers on your <X> for this Task / Epic? If not, a one-line 'no blockers' is fine."
2. **Second nudge (~20 min in):** restate the specific deliverable + cite what's blocking. "Waiting on your <PM review report / test counts / doc list> before I can commit this Task. If you hit a snag, tell me specifically what."
3. **Third nudge (~30 min in):** firm deadline. "I'll proceed without your report in 5 min unless you respond."
4. **Proceed and log:** if no substantive response, run the missing work yourself if tractable (Narrow/Full test per CLAUDE.md, doc verify, code review skim) and commit. Note in the Task summary which review was pending. Do NOT block hours hoping someone wakes up.

When a teammate claims to be "waiting on" something async (a long-running test, an external service, etc.), **verify the claim** before accepting it. Use the platform's process-listing tool to confirm the process is actually running:

- POSIX (bash / zsh): `ps -ef | grep <process-name>`
- Windows (PowerShell): `Get-Process | Where-Object { $_.ProcessName -like '*<process-name>*' }`
- Windows (cmd): `tasklist | findstr <process-name>`

Also check the background process's output file if it has one. A claim of "waiting" with no underlying process running is the same as silence.

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
    - **Self-trigger:** at the top of every turn, check whether your gating precondition is met — for the Engineer, that's "an implementation Subtask exists at `status=ready` (or you have an `in_progress` one mid-flight)". If yes, you are unblocked; start your work now, do not wait for further pings from the team-lead.
    - Read the Subtask description using the bees CLI — it contains Context, What Needs to Change, Key Files, and Acceptance Criteria
    - Review any relevant internal architecture docs referenced in CLAUDE.md under "Documentation Locations"
    - Review the existing code to determine the current state
    - Review the engineering best practices guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute each implementation Subtask following the instructions in its description
    - There may be one or many implementation subtasks
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
    - **Compile-check discipline:** Look up the **Compile/type-check** command from CLAUDE.md `## Build Commands` and run it after each subtask. Fix errors before moving on. If the project's Compile/type-check entry is empty (interpreted languages without a static type-checker), skip this rung — the **Narrow test** rung still applies. Also run **Lint** at narrow scope after each subtask where supported.
    - **Scope your test/lint runs narrowly** while iterating — use the **Narrow test** and **Lint** commands from CLAUDE.md `## Build Commands` (e.g. for a Rust crate, **Narrow test** typically resolves to `cargo test -p <crate>`; for a Node project, to `vitest run <path>`). The full-suite run happens once at the Task's `.T` subtask. See "Testing discipline — avoid redundant full-workspace runs" above.
    - **Shell-command etiquette:** when running shell commands, prefer one literal command per invocation. Don't append diagnostic tails like `; echo exit=$?` or `&& echo done` — the Bash tool already reports exit status. Avoid embedded newlines, `$VAR` / `$?` / `$(...)`, and compound commands when a simple one works. If you need a multi-step script, write it to a file and run the file rather than passing it inline via `-c` or a heredoc.
- Test Writer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Executing testing Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - **Self-trigger:** at the top of every turn, check whether your gating precondition is met — for the Test Writer, that's "at least one Engineer subtask for this Task is at `status=done` and its corresponding test work has not yet been started". If yes, you are unblocked; start writing/updating tests for that subtask now, do not wait for a ping from the team-lead. (When the Task is test-only with no Engineer subtasks, treat your own ready Subtasks as the gating precondition.)
    - Use the test writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Use the test review guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute all test subtasks to change, add or delete tests
    - Review the work of the Engineer and see if any tests need to be added, deleted or updated based on that work
      - It is possible the testing subtasks were incomplete
      - Review the work of the Engineer to find any gaps, then add, delete or updated required tests
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
    - **Scope your test/lint runs narrowly** while iterating — use the **Narrow test** and **Lint** commands from CLAUDE.md `## Build Commands`. The authoritative workspace-wide run happens once at the Task's `.T` subtask. See "Testing discipline — avoid redundant full-workspace runs" above.
    - **Shell-command etiquette:** when running shell commands, prefer one literal command per invocation. Don't append diagnostic tails like `; echo exit=$?` or `&& echo done` — the Bash tool already reports exit status. Avoid embedded newlines, `$VAR` / `$?` / `$(...)`, and compound commands when a simple one works. If you need a multi-step script, write it to a file and run the file rather than passing it inline via `-c` or a heredoc.
- Doc Writer
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Note: this differs from `/bees-fix-issue`'s Doc Writer because `/bees-execute` Tasks have *pre-planned doc Subtasks* in the breakdown — the Doc Writer's primary job is to execute those, then review the Engineer's diff for additional gaps. `/bees-fix-issue` has no pre-planned subtasks, so its Doc Writer reviews ad-hoc only. The divergence is intentional.
  - Responsibilities:
    - Execute documentation Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - **Self-trigger:** at the top of every turn, check whether your gating precondition is met — for the Doc Writer, that's "a pre-planned doc Subtask is at `status=ready` (or `in_progress` mid-flight), OR all in-flight Engineer/Test Writer subtasks for this Task are at `status=done` so a diff-review pass is unblocked". If yes, you are unblocked; start your work now, do not wait for further pings from the team-lead.
    - Use the doc writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Execute any customer-facing docs subtasks
    - Execute any internal architecture docs subtasks
    - Review the work of the Engineer and see if any docs need to be updated based on that work
      - It is possible the doc subtasks were incomplete
      - Review the work of the Engineer to find any gaps, then update docs
    - Mark each Subtask as `status=in_progress` when starting it and `status=done` when done
    - **Shell-command etiquette:** when running shell commands, prefer one literal command per invocation. Don't append diagnostic tails like `; echo exit=$?` or `&& echo done` — the Bash tool already reports exit status. Avoid embedded newlines, `$VAR` / `$?` / `$(...)`, and compound commands when a simple one works. If you need a multi-step script, write it to a file and run the file rather than passing it inline via `-c` or a heredoc.
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
    - **Self-trigger:** at the top of every turn, check both PM gating preconditions: (a) at least one subtask has reached `status=done` from both the Engineer side and (where applicable) the Test Writer side, and you have not yet reviewed its per-subtask diff (per-subtask diff review is unblocked); (b) all child subtasks of the Task are at `status=done` (Step 5 reviews and the final Task report are unblocked). If either is met, you are unblocked for that lane; start it now, do not wait for further pings from the team-lead.
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
    - Uses the bees-code-review and bees-doc-review skill after work has been done for quality control
      - NOTE: These skills could infinitely return work items
      - Product Manager must use judgement when deciding whether to ask the Team to make the improvements or not
      - **Time budget — short-circuit when reviews run hot.** If a single `/bees-code-review` or `/bees-doc-review` invocation returns more than ~10 work items, OR runs more than ~5 turns of back-and-forth, stop iterating in that lane: triage the returned list down to blocker-severity items only (correctness bugs, spec violations, contract-key violations), ask the Team to address those, and defer suggestions / nits / style work to ignored-feedback for the Task summary. These thresholds are guidance, not a hard contract — pick the firmer side when the review is clearly thrashing on subjective feedback, the looser side when each item is high-signal.
      - If the Product Manager decides to ignore bees-code-review or bees-doc-review feedback, this MUST be included in the end of task summary report for review
    - **Trust the Task's `.T` subtask output** — do NOT re-run the full workspace test suite / clippy by default. The `.T` subtask is the authoritative workspace-wide validation run. Only re-run if you have a specific reason (engineer reported skipping something, stale `.bees/` state, etc.). See "Testing discipline — avoid redundant full-workspace runs" above.
    - **Cross-Task and cross-Epic interaction check** — per-Task code review naturally focuses on the Task's own diff. The PM is responsible for the wider view. Before approving a Task, explicitly verify:
      - **Contract consistency with sibling Tasks in the same Epic.** Read the other Tasks in this Epic. For each function/API this Task modifies, find sibling Tasks that call or assume behavior from it and verify those assumptions still hold. Example: if this Task reorders steps inside an `auth_middleware`, a sibling Task whose request-handler docstring says "by this point the request is signature-verified" must be cross-checked against the new ordering.
      - **Contract consistency with completed sibling Epics.** If prior Epics in this Bee already landed code that interacts with what this Task changes, re-read the relevant diffs (via `git log` / `git diff` on the branch) and verify the interactions.
      - **Cumulative resource accounting.** If this Task adds acquires from a bounded resource (connection pool, semaphore, queue slot, in-memory map, etc.), sum across all call sites — including call sites in sibling Tasks and sibling Epics — and flag lifetime mismatches or starvation scenarios. Example: a new long-lived consumer sharing a pool with short-lived transaction writers will starve writers at steady state.
      - **Symmetric lifecycle coverage.** If this Task introduces a new resource (persistent key, file, pool entry, in-memory entry, etc.), grep the codebase for every cleanup/teardown path for the adjacent resource class and verify this new resource is handled symmetrically. Example: adding a new `cache:user:{id}:permissions` key class in the write path requires the cache-invalidation path, the user-deletion path, and any periodic-purge job to all DELETE this key class — otherwise stale-permissions data leaks past role changes.
      - **New-pattern-exposes-old-code.** If this Task introduces a new call pattern for an *unchanged* function (new frequency, new argument combination, new temporal pattern), mentally run that unchanged function under the new pattern and flag any latent assumptions the new pattern breaks. Example: `get_user_profile(id)` is fine when called once per request from the request hot path, but a new batch endpoint that calls it for hundreds of IDs in a tight loop may miss the per-request memoization reset and leak stale data from the prior request into the next.
    - **Shell-command etiquette:** when running shell commands, prefer one literal command per invocation. Don't append diagnostic tails like `; echo exit=$?` or `&& echo done` — the Bash tool already reports exit status. Avoid embedded newlines, `$VAR` / `$?` / `$(...)`, and compound commands when a simple one works. If you need a multi-step script, write it to a file and run the file rather than passing it inline via `-c` or a heredoc.
    - Provide report when done. Must include:
      - Any ignored reviewer feedback
      - Any contentious topics between team members
      - Any design decisions that were made that conflicted with work described in tickets
      - Any incomplete work
      - Any cross-Task / cross-Epic interaction issues discovered during the wider-view check, and the resolution


### 4. Per-Task and Per-Epic Cleanup

#### 4.1 After Each Task

When a Task and all its Subtasks are done (all reviewer feedback addressed or ignored):

1. Mark the Task as `status=done` (Subtasks were marked done by each agent as they completed their work). **Do this before committing** so the `.bees/` status changes are included in the commit.
2. Create one git commit for the Task. **NEVER push to remote — committing only.** Use this staging procedure:
   1. Run the **Format** command from CLAUDE.md `## Build Commands` (e.g. `cargo fmt`, `prettier --write`, `gofmt -w`) to normalize formatting (agents may have triggered reformatting in files they didn't report). Do NOT re-run the test suite here — the `.T` subtask already validated, and the PM confirmed. Re-running wastes minutes per Task.
   2. Run `git status` to see the full set of modified and untracked files.
   3. Stage files that are related to this Task — include agent-reported files, formatting changes to files that were touched by this Task's agents, and (only if the Plans hive lives inside this repo) the resolved Plans hive path's contents. Use the same hive-path resolution as `/bees-plan` and `/bees-file-issue`:

      ```bash
      # POSIX (bash / zsh):
      plans_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="plans"), None); print(p or "")')
      repo_root=$(git rev-parse --show-toplevel)
      case "$plans_path" in
        "$repo_root"|"$repo_root"/*) git add "$plans_path" ;;
      esac
      ```

      ```powershell
      # Windows (PowerShell):
      $plansPath = (bees list-hives | ConvertFrom-Json).hives | Where-Object { $_.normalized_name -eq 'plans' } | Select-Object -ExpandProperty path
      $repoRoot = git rev-parse --show-toplevel
      $plansNorm = if ($plansPath) { $plansPath.Replace('\','/') } else { '' }
      $repoNorm = $repoRoot.Replace('\','/')
      if ($plansNorm -and ($plansNorm -eq $repoNorm -or $plansNorm.StartsWith("$repoNorm/"))) {
        git add $plansPath
      }
      ```

      **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this Task.
   4. Commit with a descriptive message per system/project git guidance.
3. Send shutdown requests to all current agents. Delete completed tasks from the task list.
4. Output the summary below to the screen and continue to the next Task (spawning new agents with new task-scoped names on the same team).

```
## Task [N] of [total] Complete: [task-title]

**Task ID**: <task-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Ignored Review Feedback**: [list items that were flagged by bees-code-review or bees-doc-review but Director chose not to address, or "None"]
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
2. Call `TeamDelete` to clean up the Epic's team. If it fails due to stuck agents: (1) run `force_clean_team.py` (located at `<this skill's base directory>/scripts/force_clean_team.py` — base directory shown in the skill invocation header) via the platform's Python 3 launcher (`python3` on POSIX, `python` or `py -3` on Windows) with `<team-name>` as the argument, then (2) call `TeamDelete` again to clear session state.
3. Clear your context window and go back to step 2 (which will create a new team for the next Epic).

If not, move to final Bee review.

### 5. Final Bee-level Code, Doc and Eng reviews

Once all Epics in the Bee are done:
- `TeamDelete` the last Epic's team (if it still exists). If stuck: (1) run `force_clean_team.py` (located at `<this skill's base directory>/scripts/force_clean_team.py`) via the platform's Python 3 launcher (`python3` POSIX / `python` Windows) with `<team-name>`, (2) `TeamDelete` again to clear session state.
- Form a new review Team (e.g., `bee-review-<bee-id>`) to check their work. Use bee-scoped agent names (e.g., `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`) — the reviews run at the Bee level (across the whole Bee, not per Task), so the scope suffix is the bee-id rather than a task-id.

If you invoked the Engineer in the first team, invoke the Code Reviewer in this team.
If you invoked the Test Writer in the first team, invoke the Test Reviewer in this team.
If you invoked the Doc Writer in the first team, invoke the Doc Reviewer in this team.

- Code Reviewer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Review the output of the Engineer
    - Provide feedback where the work of the Engineer was not up to standards
  - Instructions:
    - Invoke the /bees-code-review skill
- Test Reviewer
  - Model: Claude Opus (always)
  - Responsibilities:
    - Review the output of the Test Writer
    - Provide feedback where the work of the Test Writer was not up to standards
  - Instructions:
    - Invoke the /bees-test-review skill
- Doc Reviewer
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Responsibilities:
    - Review the output of the Doc Writer
    - Provide feedback where the work of the Doc Writer was not up to standards
  - Instructions:
    - Invoke the /bees-doc-review skill
- Get the feedback, and make a judgement call about whether that work must be done
  - If so, **reform or re-use the first team** to do the work
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** spawn the Product Manager on this iteration
    - Spawn any team members required to do the work you deem necessary from the reviewer team
  - If not, move on to Final Review but you MUST share the ignored feedback for review
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in Final Review


### 6. Post-Completion Review

After the review loop in step 5 is done and all fixable issues have been addressed by the team, run one final fresh-context generalist sweep across all changes made by this Bee. This is an independent quality gate — separate from the per-Task and per-Epic review cycles above.

**Anti-pattern callout — read before acting.** Do NOT invoke `/bees-code-review`, `/bees-doc-review`, or `/bees-test-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/bees-code-review` ignores natural-language documentation by design, which is unsafe for doc-heavy Bees). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, PM verdict, and per-Task reviewer verdicts from the whole Bee run; that context biases it toward "did the phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the Bee body and nothing else — that's the point.

1. Compute the pre-Bee diff scope. Capture `<pre-bee-sha>` as the HEAD that existed when work began on this Bee (use the SHA recorded at the start of the run, or `HEAD~M` where `M` is the number of Tasks committed in Step 4 — one commit per Task; if you've lost count, walk `git log` back to the commit before the first Task commit landed in Step 4 as a backup). Collect the Bee ID `<bee-id>` and, secondarily, the IDs of the Epics/Tasks under it as `<epic-id-1> <task-id-1> ...` (the Bee body is the primary spec; Epic/Task bodies are secondary context the reviewer can consult when something in the diff is ambiguous).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose`**. The agent will not see anything else from this run, so the prompt must be self-contained. Starting skeleton (substitute `<pre-bee-sha>`, `<bee-id>`, and the Epic/Task IDs before sending):

   ```
   You are an independent reviewer for a bees-workflow Bee that was just shipped.

   Scope: review the diff `git diff <pre-bee-sha>..HEAD` (compute it yourself
   via git) against the Bee body — read it via `bees show-ticket --ids
   <bee-id>`. The parent Epic/Task bodies are secondary spec sources; consult
   them via `bees show-ticket --ids <epic-id-1> <task-id-1> ...` only when the
   diff vs. the Bee body is ambiguous. The orchestrating team-lead has
   finished the work — your job is to give it a fresh-eyes review with no
   context of how the work was done.

   Flag anything that looks wrong: code defects, prose problems, spec drift
   between the change and the Bee, contract-key violations (do NOT allow
   renames of keys in CLAUDE.md `## Documentation Locations` or `## Build
   Commands`), cross-file inconsistencies, missing edits the Bee called for.
   One generalist pass covers code AND docs AND tests — do not lane-scope.

   Do NOT do a general repo audit. Stay focused on the diff.

   Do NOT invoke /bees-code-review, /bees-doc-review, or /bees-test-review at
   this stage. Those skills are designed as parallel lanes of an in-flight
   review; they each have lane-specific scope rules that make them wrong for a
   final generalist sweep.

   Return findings as a numbered list. For each item: `file:line`, what's
   wrong, severity (`blocker` / `suggestion` / `nit`). If clean, return
   exactly "no issues found".
   ```

   Wait for the agent's report.

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-Task PM verdict and per-Task code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and continue to Final Output.

5. If the agent flagged any issues, use `AskUserQuestion`:
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now before closing the Bee
     - **File as issue tickets** — create issue tickets via `/bees-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
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
```bash
bees update-ticket --ids <epic-id> --status done
```

2. Verify all Epics are now `done`, then mark the Bee itself:
```bash
bees update-ticket --ids <bee-id> --status done
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

- **Worktree** — If `/bees-worktree-rm` is installed (it is not part of the portable core), invoke it to merge the worktree branch and clean up the worktree directory. Otherwise, instruct the user to merge the worktree branch manually (`git merge <branch>` from the parent repo, then `git worktree remove <path>`).
- **Feature branch** — Instruct the user to merge the branch (e.g., `git merge bee/b.Wx7`) or open a PR. Do NOT push to remote unless the user asks.
- **Worked on main/current branch** — Commits are already on the branch. Remind the user that the work is committed locally and they can push when ready.