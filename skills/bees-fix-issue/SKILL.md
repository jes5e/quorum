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

- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. The PM and Doc Writer roles read architecture/customer-doc paths from this section by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five required keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. The Engineer reads compile/format/lint/test commands from this section by exact key.
- CLAUDE.md contains a `## Skill Paths` section with the `Force clean team script` key. This is the absolute path to `force_clean_team.py` — used as the recovery step when `TeamDelete` fails. `/bees-setup` writes this section based on whether the bees-workflow skills are installed globally or per-project.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems — silently running the wrong commands would mask real failures.

If any precondition is missing, stop with `Run /bees-setup first.` and direct the user there. Do not improvise commands or guess paths.

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

### 2. Validate Issue

```bash
bees show-ticket --ids "<issue-id>"
```

Check:
- Issue has a status which means it is ready to begin work (`open`)
- Check `up_dependencies` array for any blockers. They must be in a completed state.

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
  3. If `TeamDelete` fails due to stuck agents: (a) read the absolute path to `force_clean_team.py` from CLAUDE.md `## Skill Paths` (key: `Force clean team script`) and run `python3 <that-path> <team-name>` to remove directories, then (b) call `TeamDelete` again to clear session state
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
  - Model: Claude Opus
  - Responsibilities:
    - Updating documentation if the issue fix changes behavior
  - Instructions:
    - Use the doc writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Review the customer-facing docs referenced in CLAUDE.md under "Documentation Locations" and see if they need any updates
    - Review the internal architecture docs referenced in CLAUDE.md under "Documentation Locations" and see if they need any updates
    - Review the work of the Engineer and see if any docs need to be updated based on that work
    - Update any docs that require updating
- Product Manager (complex fixes only)
  - Model: Claude Opus
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
    - Invoke the /code-review skill
- Test Reviewer
  - Model: Claude Opus
  - Responsibilities:
    - Review the output of the Test Writer
    - Provide feedback where the work of the Test Writer was not up to standards
  - Instructions:
    - Invoke the /test-review skill
- Doc Reviewer
  - Model: Claude Opus
  - Responsibilities:
    - Review the output of the Doc Writer
    - Provide feedback where the work of the Doc Writer was not up to standards
  - Instructions:
    - Invoke the /doc-review skill

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
4. Call `TeamDelete` to clean up the team. If it fails: (a) `python3 <path-from-CLAUDE.md-Skill-Paths-Force-clean-team-script> <team-name>`, (b) `TeamDelete` again.
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

### 8. Post-Completion Code Review

After all issues are fixed (in batch mode: after the final issue in the batch; in single mode: after the one issue), run a final `/code-review` across all changes made during this bees-fix-issue session.

1. Invoke the `/code-review` skill against all changes made during this session (diff against the branch state before bees-fix-issue started)
2. Present the findings to the user
3. If there are no issues, report "Code review: no issues found" and exit
4. If there are issues, use `AskUserQuestion` to ask:
   - Question: "Post-completion code review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now
     - **File as issue tickets** — create issue tickets via `/bees-file-issue` for each issue
     - **Skip** — acknowledge and move on without action
5. Execute the user's choice:
   - **Fix in this session**: Form a new team and delegate the fixes. Stay in delegate mode. After fixes are done, commit.
   - **File as issue tickets**: For each issue, invoke `/bees-file-issue` with the issue description. Report the created ticket IDs to the user.
   - **Skip**: Done.
