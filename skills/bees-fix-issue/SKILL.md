---
name: bees-fix-issue
description: Fix an issue described in a Bee ticket. Use '/bees-fix-issue all' to fix all open issues sequentially, or '/bees-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset.
---

## Overview

The user can call this skill in four ways:
- `/bees-fix-issue` — list all open issues, ask user which one to fix
- `/bees-fix-issue <issue-id>` — fix a specific issue
- `/bees-fix-issue <id1> <id2> <id3>` — fix an explicit list of issues, sequentially, in the order given. IDs may be separated by spaces, commas, or any mix (e.g. `b.cnb,b.sgq b.xet` is valid)
- `/bees-fix-issue all` — fix ALL open issues sequentially without user intervention

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `"1"` in either `~/.claude/settings.json` or the shell environment. The skill spawns a team unconditionally; without Agent Teams enabled, team-creation tools are unavailable and the skill cannot proceed.
- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. The PM and Doc Writer roles read architecture/customer-doc paths from this section by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five required keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. The Engineer reads compile/format/lint/test commands from this section by exact key.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems — silently running the wrong commands would mask real failures.

If any precondition is missing, stop with `Run /bees-setup first.` and direct the user there. Do not improvise commands or guess paths.

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

## Execution Flow

### 1. Determine which issues to fix

Parse the argument string. Split on any run of commas and/or whitespace; discard empty tokens. The resulting tokens determine the mode:

- **Zero tokens** (no arguments): Query all open issues, present them, ask user to pick one. Fix that one issue and exit.
- **Exactly one token equal to `all`**: `all` mode — query all open issues, sort by ticket_id, then execute the fix loop (step 2-7) for each sequentially.
- **Exactly one token that is an issue ID**: single-issue mode — fix that one issue and exit.
- **Two or more tokens** (list mode): treat as an explicit, user-provided list of issue IDs. Execute the fix loop (step 2-7) for each issue **in the order given** (do NOT sort — the user's order is intentional; earlier issues may be prerequisites for later ones). Do not query or fix issues outside the list. No user confirmation between issues.

Notes for list mode:
- `/bees-fix-issue b.cnb b.sgq b.xet`, `/bees-fix-issue b.cnb,b.sgq,b.xet`, and `/bees-fix-issue b.cnb, b.sgq  b.xet` all parse to the same three-ID list.
- Up-front validation: before starting any fixes, `bees show-ticket --ids <id1> <id2> ...` on the full list. If any ID does not exist, is not in the `issues` hive, or is not in `open` status, report the problem IDs to the user and continue with the subset that is valid and open (do not abort the whole run). If *no* IDs are valid, exit with an error.
- Between issues, follow the same team-lifecycle cleanup as `all` mode.

To query open issues (used only in no-args and `all` modes — list mode uses the user's explicit list instead):
```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues, status=open]
report: [title]'
```

#### Choose agent model preference

Before iterating through the issue list, ask the user which model to use for the support roles (Doc Writer, Product Manager, Doc Reviewer). Use `AskUserQuestion`:

- Question: "Which model should support agents (Doc Writer, Product Manager, Doc Reviewer) use?"
- Options:
  - **Opus (Recommended)** — highest quality, slower, more expensive
  - **Sonnet** — fast and cost-effective, good for straightforward tasks

The core implementation roles (Engineer, Test Writer, Code Reviewer, Test Reviewer) always use **Opus** — this is not configurable. Store the user's choice and apply it when spawning agents for every issue in the run (single-issue, list, or `all` mode). Ask once at the start, not per issue.

#### Validate isolation strategy

After parsing the argument list and resolving which issues to fix, but **before** validating any individual issue or forming a team, check whether you are running in an isolated context — fixes will produce one git commit per issue, so landing them on the wrong branch is hard to undo. Mirror `/bees-execute`'s isolation block:

**Scenario A — Already in a worktree.** You are in a git worktree whose directory name suggests issue-fix work (e.g., `fix-issues`, `bug-sweep`, or contains a fix-issue-related slug). Proceed directly — no action needed.

**Scenario B — On an existing branch in the main repo.** You are in the main repo checkout (not a worktree). Behavior depends on mode and current branch:

- If on `main` (or `master`) — **always** prompt with `AskUserQuestion`, regardless of mode. Landing many commits on main without confirmation is the surprise this prompt prevents.
- If on a feature branch in single-issue mode — proceed silently. The user is intentionally on a feature branch and a single commit there is the obvious choice.
- If on a feature branch in `all` mode or list mode — prompt with `AskUserQuestion`. Many commits on a single feature branch may not be what the user wants; they might prefer a fresh branch per fix-issue session.

When prompting, present these options:

1. **Create a feature branch (Recommended for `all` mode and list mode)** — Create a new branch (e.g., `fix/issues-<short-slug>` or `fix/<id1>-<id2>` for a small list) from the current HEAD and commit all fixes there. Keeps main clean; lets the user review/squash/discard later. Local branch only — no remote push.
2. **Work on current branch** — Commit directly to whichever branch is checked out (tell the user the branch name). Appropriate when the user is already on a feature branch and intentionally wants the commits there.
3. **Set up a worktree instead** — If `/bees-worktree-add` is installed, suggest running it to spawn the fix-issue session in an isolated worktree (fire-and-forget in a separate tmux session). If the skill is not installed, omit this option. Exit after giving this advice — do not proceed with work.

In the question, always state:
- The current working directory
- The current branch name
- That option 1 creates a local branch only (no remote push)
- The number of issues queued (so the user understands the commit volume implication)

### 2. Validate Issue

```bash
bees show-ticket --ids "<issue-id>"
```

Check:
- Issue has a status which means it is ready to begin work (`open`)
- Check `up_dependencies` array for any blockers. They must be in a completed state.

`up_dependencies` is returned as a list of ticket IDs only — not statuses. Collect the IDs and batch-look-up their statuses:

```bash
# After reading the issue, batch-look-up its up_dependencies' statuses:
bees show-ticket --ids <dep-id-1> <dep-id-2> <...>
```

For each up_dependency, check the returned `ticket_status`. The issue is unblocked only if all its `up_dependencies` are in `done` status. An issue with no `up_dependencies` is unblocked by default.

If blocked:
- Output blocking IDs and titles
- In batch mode (`all` or list mode): skip this issue and continue to the next one
- In single mode: exit with message: "Cannot start Issue. It is blocked by: [list]"

If not blocked:
- Mark issue status to signal work has begun (if needed)

### 3. Assess Complexity and Form Team

First, analyze the issue and the relevant source code to assess complexity:

**Simple fix** — one of:
- Single file change (rename, config tweak, delete dead code)
- Mechanical refactor (extract helper, move code between files)
- Test-only change (add tests, fix flaky test)
- Doc-only change

**Complex fix** — any of:
- Changes span 3+ source files
- Modifies public API, proto definitions, or storage schema
- Changes auth, security, or concurrency behavior
- Alters behavior described in PRD or SDD
- Could have non-obvious side effects on other modules

Then form the team based on complexity:

- If source code needs modification → spawn **Engineer**
- If tests need modification → spawn **Test Writer**
- Always spawn **Doc Writer** to check if docs need updating
- **If complex** → also spawn **Product Manager** to review changes against PRD/SDD in real-time and flag scope creep or spec divergence before it gets committed

Do not ask for confirmation.

**IMPORTANT: You must stay in `delegate` mode. Do not take on work, delegate work to Team members.**

#### Team lifecycle

Create **one team per issue** (e.g., `issue-xfm`). Use task-scoped agent names (e.g., `engineer-xfm`, `test-writer-xfm`, `doc-writer-xfm`).

- **Within an issue**: Send shutdown requests to agents when their work is done. Do NOT call `TeamDelete` until the issue is fully resolved.
- **Between issues** (in batch mode — `all` or list mode):
  1. Send shutdown requests to all remaining agents
  2. Call `TeamDelete` to clean up the team
  3. If `TeamDelete` fails due to stuck agents: (a) resolve the path to `force_clean_team.py` as `<this skill's base directory>/../bees-execute/scripts/force_clean_team.py` — the base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../bees-fix-issue`), and the script is bundled with sibling skill `bees-execute`. Run it via the platform's Python 3 launcher (`python3 <path> <team-name>` on POSIX, `python <path> <team-name>` or `py -3 <path> <team-name>` on Windows), then (b) call `TeamDelete` again to clear session state
  4. Create a new team for the next issue

The team may consist of any of the following agents:
- Engineer
  - Model: Claude Opus
  - Responsibilities:
    - Executing implementation changes to fix the issue
  - Instructions:
    - Read the Issue description using the bees CLI
    - Review any relevant internal architecture docs referenced in CLAUDE.md under "Documentation Locations"
    - Review the existing code to determine the current state
    - Review the engineering best practices guide referenced in CLAUDE.md under "Documentation Locations"
    - Modify any source code required to fix the issue
    - **Compile-check discipline:** Look up the **Compile/type-check** command from CLAUDE.md `## Build Commands` and run it after each significant change. Fix errors before moving on. Run the **Lint** command when the implementation is done. If the project's Compile/type-check entry is empty (interpreted languages without a static type-checker), skip that rung — narrow tests still apply.
- Test Writer
  - Model: Claude Opus
  - Responsibilities:
    - Writing tests that verify the issue fix
  - Instructions:
    - Use the test writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Use the test review guide referenced in CLAUDE.md under "Documentation Locations"
    - Review the work of the Engineer and see if any tests need to be added, deleted or updated based on that work
    - Review the work of the Engineer to find any gaps, then add, delete or update required tests
    - **Running long commands (test suites, builds, etc.):** use the Bash tool's `timeout` parameter (max 600000 ms = 10 min). For test invocations of any length up to that, dispatch in the foreground: `Bash(command: "<your project's test command per CLAUDE.md>", timeout: 540000)`. The harness blocks until the command exits and returns the output; if the command hangs, the harness kills it at the timeout boundary. For runs that legitimately exceed 10 min, use `Bash(run_in_background: true)` and **wait silently** for the task-completion notification — read the output file when it arrives. Do not write shell polling loops to wait for completion; the harness handles notification on its own.
- Doc Writer
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Note: this differs from `/bees-execute`'s Doc Writer because `/bees-fix-issue` issues have *no pre-planned doc Subtasks* — the Doc Writer reviews the Engineer's diff for doc gaps and updates ad-hoc. `/bees-execute` has pre-planned doc Subtasks that get executed first. The divergence is intentional.
  - Responsibilities:
    - Updating documentation if the issue fix changes behavior
  - Instructions:
    - Use the doc writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Review the customer-facing docs referenced in CLAUDE.md under "Documentation Locations" and see if they need any updates
    - Review the internal architecture docs referenced in CLAUDE.md under "Documentation Locations" and see if they need any updates
    - Review the work of the Engineer and see if any docs need to be updated based on that work
    - Update any docs that require updating
- Product Manager (complex fixes only)
  - Model: User's choice (Opus or Sonnet, selected at start)
  - Responsibilities:
    - Reviews the Engineer's changes against the PRD and SDD in real-time
    - Flags scope creep — changes beyond what the issue requires
    - Flags spec divergence — code that contradicts the PRD or SDD
    - Makes final call on whether the fix is ready for review
  - Instructions:
    - Read the Issue description using the bees CLI
    - Read the project's spec docs relevant to the issue. Use the paths configured in CLAUDE.md `## Documentation Locations` — specifically `Internal architecture docs` (the SDD-equivalent path) and `Customer-facing docs` (the README-equivalent path). The Documentation Locations section has no canonical "PRD" key — if the project has a PRD-equivalent at a known path, use it; otherwise the Issue ticket body itself is the authoritative spec source for bees-fix-issue, and the parent Plan Bee body (if the issue derives from one) is secondary. Do NOT hardcode `docs/prd.md` or `docs/sdd.md` — those names are project-specific.
    - Review the Engineer's code changes against the spec
    - If the Engineer changes something not required by the issue, flag it
    - If the changes contradict the PRD or SDD, determine if the docs or code are wrong
    - Send a report to the team lead when review is complete


### 4. Review Loop

Once the Team is done, form a review Team to check their work.
If you invoked the Engineer in the first team, invoke the Code Reviewer in this team.
If you invoked the Test Writer in the first team, invoke the Test Reviewer in this team.
If you invoked the Doc Writer in the first team, invoke the Doc Reviewer in this team.

#### Don't wait silently on idle teammates — graduated escalation

Reviewers (and writers) sometimes go idle right after receiving a "ready for X" ping without producing their report. The team-lead's job is to notice and escalate, NOT to keep printing "Waiting" turn after turn. Apply this ladder when a teammate is silent past the work they were asked for:

1. **First nudge (~10 min after ping):** light status check. "Just checking — any blockers on your <X> for b.Y? If not, a one-line 'no blockers' is fine."
2. **Second nudge (~20 min in):** restate the specific deliverable + cite what's blocking. "Waiting on your <PM review report / test counts / doc list> before I can commit b.Y. If you hit a snag, tell me specifically what."
3. **Third nudge (~30 min in):** firm deadline. "I'll proceed without your report in 5 min unless you respond."
4. **Proceed and log:** if no substantive response, run the missing work yourself if tractable (cargo test, doc verify, code review skim) and commit. Note in the commit summary which review was pending. Do NOT block 6 hours hoping someone wakes up.

When a teammate claims to be "waiting on" something async (a long-running test, an external service, etc.), **verify the claim** before accepting it. Use the platform's process-listing tool to confirm the process is actually running:

- POSIX (bash / zsh): `ps -ef | grep <process-name>`
- Windows (PowerShell): `Get-Process | Where-Object { $_.ProcessName -like '*<process-name>*' }`
- Windows (cmd): `tasklist | findstr <process-name>`

Also check the background process's output file if it has one. A claim of "waiting" with no underlying process running is the same as silence.

- Code Reviewer
  - Model: Claude Opus
  - Responsibilities:
    - Review the output of the Engineer
    - Provide feedback where the work of the Engineer was not up to standards
  - Instructions:
    - Invoke the /bees-code-review skill
- Test Reviewer
  - Model: Claude Opus
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
  - If so, **reform the first team** to do the work
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - Spawn any team members required to do the work you deem necessary from the reviewer team
  - If not, move on but you MUST include the ignored feedback in the summary
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in the summary

### 5. Testing the issue
- Ensure there is at least one test that fails before the issue fix and passes after
  - This ensures we will not introduce this particular regression again in the future

### 6. Verify docs are still accurate

After the fix is implemented, review the changes against the project's spec docs — the path configured under `Internal architecture docs` in CLAUDE.md `## Documentation Locations` (the SDD-equivalent), and any project PRD-equivalent if present. If the fix diverges from what the docs describe, determine whether:

1. **The docs are correct and the fix is wrong** → fix the code
2. **The docs are outdated and the fix is correct** → update the docs

Either way, docs and code must be in sync when the issue is closed. Include any doc updates in the commit.

Report what was found:
- "Docs verified accurate — no changes needed"
- OR "Updated [doc path] §X.Y to reflect [change]" — name the actual file (e.g. the configured Internal architecture docs path) rather than a generic "SDD §20".

### 7. After Issue is fixed

Once the issue is fixed:

1. Send shutdown requests to all agents on the team.
2. Mark the issue status as `done`.
3. Create one git commit for the Issue (including any doc updates). **NEVER push to remote — committing only.** Use this staging procedure:
   1. Run the **Format** command from CLAUDE.md `## Build Commands` (e.g. `cargo fmt`, `prettier --write`, `gofmt -w`) to normalize formatting (agents may have triggered reformatting in files they didn't report).
   2. Run `git status` to see the full set of modified and untracked files.
   3. Stage files that are related to this issue — include agent-reported files, `.bees/` ticket changes, and any formatting changes to files that were touched by this issue's agents. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this issue.
   4. Commit with a descriptive message per system/project git guidance.
4. Call `TeamDelete` to clean up the team. If it fails: (a) run `force_clean_team.py` (located at `<this skill's base directory>/../bees-execute/scripts/force_clean_team.py` — bundled with sibling skill `bees-execute`) via the platform's Python 3 launcher (`python3` POSIX / `python` Windows) with `<team-name>`, (b) `TeamDelete` again.
5. Output the summary:

```markdown
## Issue [x] of [total] done: [issue-title]

**Issue**: <issue-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed (use the actual path from CLAUDE.md "Documentation Locations", not literal "SDD"/"PRD")]
**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]
```

6. In batch mode (`all` or list mode): proceed to the next issue in the batch (go back to step 2). In single mode: continue to step 8.

### 8. Post-Completion Review

After all issues are fixed (in batch mode: after the final issue in the batch; in single mode: after the one issue), run a final fresh-context generalist sweep across all changes made during this bees-fix-issue session.

**Anti-pattern callout — read before acting.** Do NOT invoke `/bees-code-review`, `/bees-doc-review`, or `/bees-test-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/bees-code-review` ignores natural-language documentation by design, which is unsafe for doc-heavy fixes). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, and reviewer verdicts from the whole run; that context biases it toward "did the four phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the issue body and nothing else — that's the point.

1. Compute the pre-session diff scope. Capture `<pre-session-sha>` as the HEAD that existed when bees-fix-issue began (use the SHA recorded at the start of the run, or `HEAD~N` where `N` is the number of issues actually fixed in this session — one commit per issue per Step 7.3). Collect the issue ID list as `<issue-id-1> <issue-id-2> ...` (one ID in single-issue mode; the full session list in batch mode).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose`**. The agent will not see anything else from this session, so the prompt must be self-contained. Starting skeleton (substitute `<pre-session-sha>` and the issue ID list before sending):

   ```
   You are an independent reviewer for a bees-workflow fix that was just shipped.

   Scope: review the diff `git diff <pre-session-sha>..HEAD` (compute it
   yourself via git) against the issue body, or bodies in batch mode — read
   each via `bees show-ticket --ids <id>`. Issue IDs in this session:
   <issue-id-1> <issue-id-2> ...
   The orchestrating team-lead has finished the work — your job is to give it a
   fresh-eyes review with no context of how the work was done.

   Flag anything that looks wrong: code defects, prose problems, spec drift
   between the change and the issue, contract-key violations (do NOT allow
   renames of keys in CLAUDE.md `## Documentation Locations` or `## Build
   Commands`), cross-file inconsistencies, missing edits the issue called for.
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

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-issue code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and exit.

5. If the agent flagged any issues, use `AskUserQuestion`:
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now
     - **File as issue tickets** — create issue tickets via `/bees-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
   - **Fix in this session**: Form a new team and delegate the fixes. Stay in delegate mode. After fixes are done, commit.
   - **File as issue tickets**: For each issue, invoke `/bees-file-issue` with the issue description. Report the created ticket IDs to the user.
   - **Skip**: Done.
