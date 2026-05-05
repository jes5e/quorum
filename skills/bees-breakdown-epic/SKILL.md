---
name: bees-breakdown-epic
description: Break down a single Epic into Tasks. User can provide Epic ID or a Bee ID and skill finds Epics that are ready
argument-hint: "[<epic-id> | <bee-id>]"
---

# Epic to Tasks

Your job is to break down an Epic ticket into Tasks and Subtasks.

## Workflow

### 0. Choose agent model preference

Before starting work, ask the user which model to use for the support roles spawned during breakdown (research teammates, Product Manager when applicable). Use `AskUserQuestion`:

- Question: "Which model should support agents (research teammates, PM, Doc Writer-equivalent) use?"
- Options:
  - **Opus (Recommended)** — highest quality, slower, more expensive
  - **Sonnet** — fast and cost-effective, good for straightforward tasks

The core implementation-shaping role (the team-lead — you) always uses **Opus**. Store the user's choice and apply it when spawning research teammates throughout this breakdown.

### 1. Determine Which Epic to Break Down

**If caller provides Epic ID**: Use that Epic ID directly.

**If caller provides a Bee ID**: Use the Bee ID to find workable Epics — see the "Once you have a Bee ID" recipe below.

**If caller provides no arguments**: Search for ready Plan Bees in the current repo by querying the Plans hive:
```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans, status=ready]
report: [title]'
```
If exactly one Bee is found, use it. If multiple, use `AskUserQuestion` to let the user pick which Bee to work on (the `report: [title]` clause gives you the titles to display). If none found, tell the user no Plan Bees are ready and suggest running `/bees-plan-from-specs`.

**Once you have a Bee ID**: Find Epic children of that Bee in the `drafted` state — those are Epics that are written but whose children (Tasks) have not been written yet:

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=drafted]
report: [title, up_dependencies]'
```

If there are multiple, use `AskUserQuestion` with `multiSelect: false` to let user pick ONE Epic. Review the 
dependency chain and recommend the one that makes the most sense:
- Question: "Which Epic do you want to break down?"
- Options:
  - Epic 1 (recommended)
  - Epic 2
  - etc

### 2. Fetch and Analyze Epic

Fetch full Epic details using the bees CLI to understand scope of total work.

- Get that Epic from the Bees server and read it.
- Parse Epic title, description, and requirements.
- Read the parent Bee
- Read the egg source material linked in the parent Bee. **If the egg is null/empty** (Plan Bees authored via `/bees-plan` for features without a separate PRD/SDD), the Plan Bee body itself is the authoritative scope document — read it carefully in place of the egg sources, and substitute "the Plan Bee body" wherever subsequent prose references "the PRD" or "the SDD".
- **Check for the Scoped-marker on the parent Bee.** If the parent Bee's body contains a line of the form `` Scoped to `### Feature: <title>` from <prd-path> and <sdd-path>. `` (emitted by `/bees-plan-from-specs --feature "<title>"`), the egg-resolved doc content must be restricted to the matching `### Feature: <title>` subsection in each named doc before treating it as the spec. Run the bundled parser/scoper to do the detection and scoping in one step:

  Extract the `body` field from the `bees show-ticket --ids <bee-id>` JSON output (the envelope's `tickets[0].body` markdown string), then write that body to a temp file via the `Write` tool under the namespaced workflow scratch dir (`/tmp/.bees-workflow/bees-bee-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-bee-body-<short-suffix>.md` on Windows). Create the `.bees-workflow` subdir if absent first:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.bees-workflow
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
  ```

  Do NOT dump the whole JSON envelope to the temp file — the marker line lives inside the body's markdown text, and JSON-encoded escapes (e.g., `\n`) prevent the parser's line-by-line scan from matching. Then invoke the helper. Resolve the helper at `<this skill's base directory>/scripts/scoped_marker_resolver.py` — the base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../bees-breakdown-epic`).

  ```bash
  # POSIX (bash / zsh):
  python3 "<this skill's base directory>/scripts/scoped_marker_resolver.py" "/tmp/.bees-workflow/bees-bee-body-<short-suffix>.md"
  ```

  ```powershell
  # Windows (PowerShell):
  python "<this skill's base directory>\scripts\scoped_marker_resolver.py" "$env:TEMP\.bees-workflow\bees-bee-body-<short-suffix>.md"
  ```

  The helper exits 0 with a JSON object on stdout. When `"scoped": false`, no marker was present — proceed with the full egg-resolved doc content as today. When `"scoped": true`, the JSON's `docs` array carries the scoped subsection content per egg-doc path; use that scoped content for all subsequent Task decomposition, sibling-overlap checks, and the Spec Traceability Review (cite `### Feature: <title>` subsection coordinates rather than the full PRD/SDD when the marker is present). The helper exits 2 with a clear error on stderr if the marker is present but malformed, names a doc that is missing on disk, or names a heading that does not exist in the doc — surface that error to the user and stop; do not silent-fallback to the full doc. The Scoped-marker grammar and the helper contract are documented in `docs/doc-writing-guide.md` `## The Scoped-marker contract`.

  Do **not** remove the temp file after the helper exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place; the OS / user reclaims them on their own cadence.
- **Check external-system contracts against authoritative docs.** When the Epic body references a third-party platform feature (a tool API, a CLI flag set, a harness behavior, an environment-variable contract), search the system's authoritative docs before authoring Tasks — `WebSearch` and `WebFetch` are available. Look for: canonical install paths, file shapes / frontmatter formats, lifecycle requirements (e.g., does a session restart load new files, or does a hot-reload command exist?), error-message vocabulary the rewrite needs to match. Two outcomes:
  - The docs answer the contract definitively → fold the answer into the spec; skip any "probe whether it works" Tasks the breakdown might otherwise create.
  - The docs leave specific behavior unspecified → keep the probe Task, but use what the docs *did* say to design tight assertions (`does the harness register this exact frontmatter shape at this exact path with this exact session-lifecycle behavior?`) rather than broad discovery probes (`does anything happen when I dispatch this?`). Tight probes distinguish failure causes; broad probes force a guess-and-check loop.

  Spending a few minutes on docs upfront often saves hours of probe-and-fix downstream, *and* makes any probes that do run far more diagnostic when they fail. See `CONTRIBUTING.md` `## Verifying external-system contracts` for the underlying principle.
- Identify what implementation work is needed as a list of Tasks.
- Find any Epics this Epic depends on (check `up_dependencies` field) and use `bees show-ticket --ids <id>` to read them
  - These Epics describe foundational work that will be complete before this Epic you are working on is done
  - So presume that foundational work is done and make a plan to build on top of it
- Check for sibling overlap: 
  - Read ALL sibling Epics under the same Bee. 
  - Before proposing any Task, verify it does not duplicate work scoped to another Epic. 
  - If a Task or Subtasks overlaps with a sibling Epic's scope, do NOT include it — that work belongs to the other Epic.


### 3. Break Epic into Tasks

#### Tasks
- Tasks should be discrete units of work - suitable for a single git commit.
- Do not include code snippets or file numbers. Code is going to change as execution proceeds. Assume the LLM working on the code will be capable of finding the code.
- Do not describe exactly how to implement the solution. The LLM working on the solution will be an expert. Just provide the scope of work and any requirements or acceptance criteria.

#### Cross-Task contract documentation

When a Task establishes, changes, or depends on an ordering, a resource-sharing pattern, an invariant, or an assumption that another Task in the same Epic (or a sibling Epic) needs to respect, **write the contract down in the Task body**. The PM reviewer during `/bees-execute` will use these statements to cross-check sibling Tasks. Implicit contracts carried in the author's head routinely slip past per-Task reviews and surface later as cross-Task issues.

Examples of contracts worth writing down:

- **Ordering contracts**: "this Task reorders the `auth_middleware` pipeline so user lookup happens before signature verification. Any caller that assumes signature-verified-first ordering ('by this point the request is verified') needs to be re-verified."
- **Resource-sharing contracts**: "this Task introduces a new `ExclusivePool` that will be acquired by both short-lived API request handlers (ms-scale) and a new long-lived background worker (minute-scale). Pool sizing must accommodate both lifetimes; sibling Tasks that add more consumers to this pool must account for the aggregate."
- **Invariant assumptions**: "this Task's new event handler assumes that on receipt of a `user-deleted` event, the cache entry for that user has already been invalidated. The sibling cache-invalidation Task must preserve that invariant."
- **Symmetric-lifecycle requirements**: "this Task adds a new cache key class `cache:user:{id}:permissions`. Cleanup paths in sibling Tasks (user-deletion path, periodic-purge job, role-change handler) must all DELETE this key class to avoid stale-permissions leaks."

Where the contract spans sibling Tasks in the same Epic, call out the specific sibling Task IDs the reviewer should cross-check. Where the contract spans sibling Epics, note the Epic ID.

Example task:
```
Task 1: Implement CSV export functionality                                                                              
                                                                                                                                         
  Context: Users need to export data to CSV format for analysis in spreadsheet applications. Currently, only JSON export is supported.
                                                                                                                                         
  What Needs to Change:                                                                                                                  
  - Add export_to_csv() function to src/export.py using csv.DictWriter
  - Add CSV format option to export CLI command
  - Update export service to route CSV requests to new function
                                                                                                                                         
  Why: Users frequently request spreadsheet-compatible exports for data analysis and reporting workflows.
                                                                                                                                         
  Success Criteria:                                                                                                                   
  - Users can run export command with --format=csv flag
  - CSV output contains proper headers and quoted fields
  - Exported CSV files open correctly in Excel/Google Sheets
```

### 4. Create Task Team to Break Task into Subtasks

Form a team to write the Subtasks for this Epic. Your responsibilities are:
  - Surface design questions back to the Caller
    - If the team proposes different approaches to a problem, surface this back up to the caller with an AskUserQuestion
  - Responsible for coordinating the team and ensuring all work is complete, but the Product Manager has final authority on quality and completeness
- Instructions:
    - Carrying forward architectural decisions:
      - If the caller provides architectural decisions or constraints (e.g., "make parameter X optional with fallback Y"), explicitly reference it in every affected subtask description. 
      - Do not paraphrase or partially apply — use the caller's exact specification.

#### Team
If source code needs to be changed, include the Engineer. If not, the Engineer is optional.
If unit test code needs to be changed, include the Test Writer. If not, the Test Writer is optional.
Always include the Doc Writer if the Epic changes source code, configuration, or deployment — the Doc Writer decides what docs need updating (README, architecture docs, etc.). Don't pre-judge whether docs need changes; that assessment is the Doc Writer's job. The Doc Writer is only optional for Epics that are purely research or planning with no code/config changes.
Always spawn the Product Manager.

**IMPORTANT**: You do not break Tasks into Subtasks. This is the job of the Team.

**CRITICAL — Subagent permissions**: Spawn ALL team members with `mode: "plan"`. Team members are read-only researchers. They must never create, update, or delete tickets. Only YOU (the team lead) run `bees create-ticket`, `bees update-ticket`, or `bees delete-ticket`.

**Authoring Task and Subtask bodies**: Task and Subtask bodies follow the mandatory template below (Context / What Needs to Change / Key Files / Acceptance Criteria) — they are multi-section markdown that trips Claude Code's command-injection guard if inlined as a `--body "..."` argument (any newline-followed-by-`#`-heading triggers the validator and forces a permission prompt), and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). For every `bees create-ticket` you run for a Task or Subtask, **author the body to a temp file via the `Write` tool and pass `--body-file <path>`** to `bees create-ticket`. Pick a temp path under the namespaced workflow scratch dir (`/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows), creating the `.bees-workflow` subdir if absent (`mkdir -p /tmp/.bees-workflow` on POSIX, `New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null` on Windows). Do **not** remove the file after the bees command exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so crashed runs leave debuggable artifacts in a known place. Status-only updates and genuinely single-line bodies can stay on inline `--body`.

When spawning team members, include the following restriction in each teammate's spawn prompt:

```prompt
You are a READ-ONLY researcher. You must NEVER run `bees create-ticket`, `bees update-ticket`, or `bees delete-ticket`.
Your job is to research the codebase and report your proposed subtasks back via SendMessage as text.
Only the team lead creates tickets.
```

Also include the following Subtasks guidance in each teammate's spawn prompt:

```prompt
Subtask represent discrete sets of work required to achieve the Task outcome.

- Do not include code snippets or file numbers. Code is going to change as execution proceeds. Assume the LLM working on the code will be capable of finding the code.
- Do not describe exactly how to implement the solution. The LLM working on the solution will be an expert. Just provide the scope of work and any requirements or acceptance criteria.
Examples include:
- Writing or updated a method
- Changing code to use a new method or method signature
- Updating a document
- Updating a test file

Sample subtask:
title: Modify test_api.py to include required changes
body: Update existing API test coverage to account for CSV export support. 
Ensure tests validate correct format selection, response structure, headers, and error handling without impacting existing JSON export behavior.
acceptance criteria:
- API tests cover successful CSV export responses.
- Tests validate presence of header row and correct row counts.
- Tests confirm JSON export behavior remains unchanged.
- All API tests pass after updates.
```


##### Team Composition

The team should consist of the following agents:

- Engineer
  - Model: Claude Opus
  - Responsibilities:
    - Writing implementation Subtasks for a task (if required)
      - Tasks that only involve research (no code or doc changes) may omit all of these subtasks.
  - Instructions:
    - Review any relevant internal architecture docs referenced in CLAUDE.md under "Documentation Locations"
    - Review the existing code to determine the current state
    - Review the engineering best practices guide referenced in CLAUDE.md under "Documentation Locations"
    - Write subtasks for each logical implementation step.
    - There may be one or many implementation subtasks
- Test Writer
  - Model: Claude Opus
  - Responsibilities:
    - Writing testing Subtasks for a task (if required)
  - Instructions:
    - Use the test writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Use the test review guide referenced in CLAUDE.md under "Documentation Locations"
    - Write or modify any required unit tests
    - Write or modify any required Integration tests
    - Add a subtask **for each test file or logical group of test file** that needs to be modified based on the work described by the Engineer
      - The substask will provide high level instructions to:
        - Update any tests that cover the work done in the parent Task
        - Delete any tests that are now made obsolete by work done in the parent Task
        - Add any tests to cover functionality that is currently not tested based on the work done in the parent Task
    - Add a final substask to run the full unit test suite and fix any failures. Integration tests will be handled by the calling function.
       - This subtask tells the agent to ensure 100% unit tests passing before completing, this means fixing broken tests
       - If for some reason the agent cannot get 100% unit tests passing it should report the failure to the Team Lead
- Doc Writer
  - Model: Claude Opus
  - Responsibilities:
    - Writing documentation Subtasks for a task (if required)
  - Instructions:
    - Use the doc writing guide referenced in CLAUDE.md under "Documentation Locations"
    - Readme:
      - If the Task modifies user-facing code or installation and setup:
        - Review the customer-facing docs referenced in CLAUDE.md under "Documentation Locations"
        - Write a subtask describing how the customer-facing docs should be updated based on the work done in this Task
    - Architecture Docs:
      - If the Task modifies source code:
        - Review the internal architecture docs referenced in CLAUDE.md under "Documentation Locations"
        - Write a subtask for each architecture doc that needs to be updated based on the work done in this Task
- Product Manager
  - Model: Claude Opus
  - Responsibilities:
    - Responsible for reviewing Tasks against the PRD and SDD
    - Ensures that the work being described meets the requirements
  - Instructions:
    - Read any source documents provided in the top level Bee
    - Review the Task and Subtasks to ensure that the work proposed: 
      - Aligns with the requirements
      - Does not introduce more functionality than asked for
        - e.g The PRD calls for no legacy support but the Engineers proposes a task for backwards compatibility.
        - Call this out as unacceptable
      - Review all Tasks once they are complete against the Epic to ensure that:
        - The work will meet the Acceptance Criteria
        - The work covers all functionality required by the Epic
        - The work does not introduce any functionality not required or explicitly disallowed in the Epic
    - Review the subtasks created by the Test Writer
      - Ensure they have done their best to create a subtask per test file that needs to be changed



#### Mandatory Subtask Description Template

Every subtask description MUST include all of the following sections. Do not omit any section. Do not use abbreviated or one-line descriptions.

```
## Context
Why this subtask exists and what preconditions are assumed.

## What Needs to Change
Specific files, functions, and changes required. Include line numbers where known.

## Key Files
- path/to/file.py — what changes here

## Acceptance Criteria
- Observable, testable conditions that confirm the subtask is complete
- Be specific: "function X returns Y" not "function works correctly"
```

#### Task Loop
Spawn one persistent team to handle all Tasks. Work through each Task sequentially with the same team, planning subtasks one Task at a time, **without asking the User for permission**. 
Only stop to review with the User once all Tasks are done.

### 5. Review Epic 

When all Tasks are complete,   
- Review quality of Task and Subtasks, make final decision when to present completed Task to caller
- You must defer to the Product Manager on whether a Task is final and complete

After Epic is complete, then create Tasks.
Each Task should be a Child of the Epic it is for (and the Epic should be marked as Parent).
If Tasks must be completed sequentially, add up and down dependencies to relevant tickets.

#### Set Status
- Set the Epic to `ready` (it is now written and its children — the Tasks — are written)
- Set each Task to `ready` (it is written and its children — the Subtasks — are written)
- Set each Subtask to `ready` (it is written and has no children)

Show the Tasks you just created to the User in detail and ask them if they want to make modifications.


#### Spec Traceability Review

**This step is mandatory after every Epic is broken down.** Before moving to the next Epic:

1. Re-read the Epic description, including its scope and acceptance criteria.
2. Identify every specific requirement the Epic depends on. **Source depends on whether the parent Plan Bee has eggs:**
   - **Eggs present (PRD/SDD on disk)**: requirements come from those documents — cite section numbers from the PRD and SDD.
   - **Eggs null/empty (no PRD/SDD)**: requirements come from the Plan Bee body itself (and the Epic body) — cite the Bee's relevant scope/acceptance-criteria bullets.
3. For each requirement, verify there is at least one subtask that explicitly covers it.
4. Report the results as a traceability table. Use the column header that matches the source:

```
| Spec Requirement    | Source           | Covered By Subtask | Status |
|---------------------|------------------|--------------------|--------|
| <requirement>       | PRD §X / Bee body| t3.xxx             | OK     |
| <requirement>       | SDD §Y           | MISSING            | GAP    |
```

5. If any requirement is marked GAP:
   - Create the missing subtask(s) immediately.
   - Set their status to `ready` and wire dependencies.
   - Re-report the updated table showing all gaps resolved.

6. Only proceed to the next Epic after all requirements show OK status.

This review ensures nothing from the spec is lost during the Task/Subtask decomposition. The subtask descriptions are what the executing agents will follow — if a requirement is not in a subtask, it will not be implemented. The review applies whether the spec source is a PRD/SDD pair on disk or the Plan Bee body itself.


#### Checklist Before Returning

- [ ] All Subtasks have parent set to task-id
- [ ] If Task modifies code, all mandatory subtasks created (implementation steps, architecture docs review, unit test review, run full test suite)
- [ ] Documentation subtasks have up_dependencies on implementation (implementation must complete first)
- [ ] Testing subtasks have up_dependencies on implementation/add-tests (implementation and test creation must complete first)
- [ ] All descriptions follow the mandatory template (see below)
- [ ] NO git commit subtasks created (commits handled automatically by executors)
- [ ] Testing subtasks support maximum parallelization on execution by making one subtask per test file to be modified
- [ ] Spec Traceability Review completed with all requirements at OK status (sources from PRD/SDD if eggs present, from the Plan Bee body otherwise)

### 6. Commit New Ticket Files

Before rendering the next-steps menu, stage and commit the ticket files this skill just produced (the new Tasks and Subtasks, plus the parent Epic's status update). The recommended next step in Step 7 is "open a fresh session", and ending the session with uncommitted ticket files leaves the next session to discover and reason about them — so commit now, while context is fresh.

**Do not hardcode the Plans-hive path.** `/bees-setup` lets users place hives in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/plans/` silently stages nothing when the user picked an out-of-repo location.

Resolve the Plans hive path via `bees list-hives`, check whether it lives inside the current git repo, and only `git add` if so. Mirrors `bees-file-issue` Step 5's pattern.

```bash
# POSIX (bash / zsh):
plans_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="plans"), None); print(p or "")')
repo_root=$(git rev-parse --show-toplevel)
case "$plans_path" in
  "$repo_root"|"$repo_root"/*)
    git add "$plans_path"
    git commit -m "Break down <epic-id>: <epic-title>"
    ;;
  *)
    # Plans hive lives outside the repo — skip git; surface the note in Step 7.
    ;;
esac
```

```powershell
# Windows (PowerShell):
$plansPath = (bees list-hives | ConvertFrom-Json).hives | Where-Object { $_.normalized_name -eq 'plans' } | Select-Object -ExpandProperty path
$repoRoot = git rev-parse --show-toplevel
# Normalize separators — git rev-parse returns forward slashes on Windows;
# bees list-hives may return backslashes. Compare both sides on the same form.
$plansNorm = if ($plansPath) { $plansPath.Replace('\','/') } else { '' }
$repoNorm = $repoRoot.Replace('\','/')
if ($plansNorm -and ($plansNorm -eq $repoNorm -or $plansNorm.StartsWith("$repoNorm/"))) {
  git add "$plansPath"
  git commit -m "Break down <epic-id>: <epic-title>"
} else {
  # Plans hive lives outside the repo — skip git; surface the note in Step 7.
}
```

Substitute the actual Epic ID and title into the commit message. Single literal `git commit` command, no compound chains.

If the Plans hive lives **outside** the repo, skip the git commands and remember to surface a one-line note in Step 7 so the user knows the new tickets are persisted by the bees CLI but not git-tracked here.

### 7. Offer Next Steps

After the Epic (or all Epics, if breaking down a whole Bee) is fully broken down and the new ticket files have been committed (or noted as out-of-repo), present the user with clear options. Use `AskUserQuestion`.

Note above the options: `/bees-execute` re-reads the Bee, Epics, and Tasks from the bees CLI and reads CLAUDE.md from disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives the executing agents full context budget for per-Task implementation, review cycles, and the team-lead's running judgment. Continuing to break down the next Epic in this session is lower-risk (same skill, similar context footprint), but a fresh session is still preferred for big Bees.

If Step 6 found the Plans hive lives outside the repo, also include a one-line note here: *"The new ticket files are persisted by the bees CLI but the Plans hive lives outside this git repo, so they were not committed by this skill."*

#### Pick the Recommended option

The "Recommended" badge depends on whether breaking down the *next* Epic right now risks rework. Specifically: when the just-broken-down Epic's implementation will lock contract details (new infrastructure, API surface, schema, framework, etc.) that drafted siblings consume, breaking those siblings down before that contract solidifies produces stale Tasks. To decide:

1. Query drafted sibling Epics under the same parent Bee:

   ```bash
   bees execute-freeform-query --query-yaml 'stages:
     - [parent=<bee-id>, type=t1, status=drafted]
   report: [title, up_dependencies]'
   ```

2. Filter to siblings whose `up_dependencies` includes the just-broken-down Epic's ID. If there are none, skip directly to the **No-reshape-risk case** branch in step 4.

3. For each such dependent sibling, fetch its body via `bees show-ticket --ids <sibling-epic-id>` and read it alongside the just-broken-down Epic's body. Judge — this is a team-lead call, not a hardcoded rule, treated the same as other judgment calls in this skill — whether the upstream Epic's implementation will materially reshape the contract the sibling consumes. Indicators of reshape risk:
   - Upstream Epic introduces new infrastructure, API surface, schema, framework, or subagent/tool definitions that the sibling explicitly rewrites-to-consume.
   - Sibling Epic's scope reads like "rewrite X to use the new Y" where Y is what the upstream Epic produces.
   - Contract details (signatures, file shapes, lifecycle, error vocabulary) the sibling would have to guess at are precisely what the upstream Epic locks in.

   Pure ordering coupling — sibling depends on upstream only because work must serialize, not because it consumes a still-in-flux contract — does **not** count as reshape risk.

4. Branch the Recommended badge:
   - **Reshape-risk case** (any dependent sibling judged to consume an in-flux contract): Recommended option is **"In a fresh session, execute this Epic first; defer downstream breakdown"**. Include a one-line rationale naming the at-risk siblings (by ID and short title) and the contract concern (e.g., *"siblings `<id-a>` and `<id-b>` rewrite-to-consume the new framework this Epic produces; breaking them down before implementation lands risks stale Tasks."*).
   - **No-reshape-risk case** (default — no dependent siblings, or dependencies are pure ordering): Recommended badge stays on the bulk-execute option as today. Do **not** surface an extra confirm-or-defer prompt the user can't meaningfully answer.

#### Menu options

Always include all six options below. The Recommended badge moves between the first two (whole-Bee execute vs. this-Epic-first execute) per the branch above. Each option carries a one-line "best when …" clause so the user can compare trade-offs without external context.

- **In a fresh session, execute the whole Bee** — run `/bees-execute <bee-id>` (e.g. `b.duy`) in a new Claude Code session. `/bees-execute` walks every Epic in the Bee in dependency order.
  - *Best when* the remaining drafted Epics either don't depend on this one, or their dependencies are pure ordering — no contract-reshape risk to defer for.
  - *Recommended in the no-reshape-risk case.*
- **In a fresh session, execute this Epic first; defer downstream breakdown** — run `/bees-execute <epic-id>` (e.g. `t1.duy.c9`) in a new session, scoped to the Epic just broken down. After it lands, return to break down the dependent siblings against the now-stable contract.
  - *Best when* drafted siblings rewrite-to-consume what this Epic produces and the contract is still in flux — execute now, then break down siblings against the locked-in contract.
  - *Recommended in the reshape-risk case.* Name the at-risk siblings inline.
- **In a fresh session, start at a specific Epic** — run `/bees-execute <epic-id>` in a new session. `/bees-execute` accepts an Epic ID; it finds the parent Bee automatically and starts from that Epic's position in the plan. All Epics still run — this just biases the entry point.
  - *Best when* the user wants the bulk-execute walk but with a specific entry point (e.g., the just-broken-down Epic, or an upstream foundational Epic).
- **In a fresh session, break down the next Epic** — run `/bees-breakdown-epic <next-epic-id>` in a new session if more Epics in this Bee remain in `drafted` state. Same-session continuation is also reasonable here since the skill is repeating with similar context growth per Epic.
  - *Best when* the user wants to finish planning before any execution starts and there's no contract-reshape risk that would make the next Epic's Tasks go stale.
- **Review first** — let the user review the plan before proceeding.
  - *Best when* the user wants to scan the new Tasks and Subtasks for shape/scope before committing to an execution path.
- **Done for now** — plan is saved; user will come back later.
  - *Best when* the user is at a natural stopping point and will return in a later session.

