---
name: quo-execute
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

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The seven required custom subagent types are registered in the running Claude Code session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. Custom subagents are loaded at Claude Code session start, so a fresh install requires a Claude Code restart (or `/agents` to hot-reload) before the skill can dispatch them. If any of the seven is missing at run-time, the orchestrator STOPS at the precondition gate and emits the hard-fail message — there is no fallback to `general-purpose`, no skipping the dispatch, and no improvising substitute roles. The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents` to hot-reload, e.g.: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`
- The Plans hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `plans`.
- The Specs hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section. Agents look up paths to architecture docs, customer docs, test guides, etc. by exact key from this section.
- CLAUDE.md contains a `## Build Commands` section, and that section has all five required bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. Agents look up build/test/format/lint commands by exact key from this section.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The Build Commands section is required, not optional.

Do not attempt to recover from a missing precondition by improvising commands or guessing paths — fail fast and direct the user to `/quo-setup` so the configuration is captured deliberately.

**Verifying the subagents precondition.** Verification rides on the procedural gate at the first dispatch: if any dispatch in the run hits an `Agent type '<name>' not found`-style error from the Agent tool for any of the seven required subagent types (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`), the orchestrator STOPS, emits the hard-fail message above, and exits — no fallback to `general-purpose`, no skipping the dispatch, no substitute role. This gate is honest about Claude Code's session-load semantics (subagents are loaded at session start; mid-session installs require a restart or `/agents` hot-reload) and cannot be bypassed by token-budget pressure or model creativity, because it fires at the natural failure point.

### 1. Find Bee to work on and validate

All `AskUserQuestion` gates in this section (the Bee pick, the agent model preference under `#### Choose agent model preference`, and the worktree / isolation-strategy gate under `#### Validate isolation strategy`) fire through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark each `gate-*` task `completed` the moment `AskUserQuestion` returns and the user's answer is consumed.

The user will either call without arguments, with a Bee id or with an Epic ID:

- **If called without arguments**, list all Plan Bees in this repo and ask the user which one to work on:

  ```bash
  bees execute-freeform-query --query-yaml 'stages:
    - [type=bee, hive=plans]
  report: [title, ticket_status]'
  ```

  Filter the result to Bees with status `ready` or `in_progress` (those are workable). If exactly one matches, use it. If multiple, present them via `AskUserQuestion`. If none, tell the user no Plan Bees are workable and suggest `/quo-plan` or `/quo-plan-from-specs`.

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

**Scenario B — On an existing branch in the main repo.** You are in the main repo checkout but *not* on a worktree. This happens when the user invoked `/quo-execute` directly in their terminal. Present an AskUserQuestion with these options:

1. **Create a feature branch (Recommended)** — Create a new branch (e.g., `bee/b.Wx7`) from the current HEAD and do all work there. This keeps main clean and allows the user to review, squash-merge, or discard the work later. At the end, instruct the user to merge the branch or open a PR.
2. **Work on current branch** — Commit directly to whichever branch is checked out (tell the user the branch name). Appropriate if the user is already on a feature branch or intentionally wants commits on main.
3. **Set up a worktree instead** — If `/bees-worktree-add` is installed (it is not part of the portable core), suggest the user run it to create an isolated worktree and spawn an async agent. Right choice for fire-and-forget execution in a separate tmux session. Exit after giving this advice — do not proceed with work. Omit this option if the skill is not installed.

In the question, always state:
- The current working directory
- The current branch name
- That option 1 creates a local branch only (no remote push)

### 2. Find Epic to work on and validate

The multi-Epic run-mode gate in this section (under `#### Pick a multi-Epic run mode (only when more than one Epic is in scope)`) fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` the moment the user's answer is consumed.

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

#### Pick a multi-Epic run mode (only when more than one Epic is in scope)

Before starting work on the first Epic, count the Epics returned by the `[parent=<bee-id>, type=t1]` query above (the full set under the Bee, not just the workable subset — Epics in `drafted`/`ready`/`in_progress` plus any in `done` that already shipped count toward "scope"). If two or more Epics exist under the Bee **and at least one of them is workable (`ready` / `in_progress`) or `drafted`** — i.e., the run will cross at least one Epic boundary — present a one-time mode choice with `AskUserQuestion`. If every Epic under the Bee is already `done`, **skip the question entirely** — Section 4.2 branch 3 will exit the run with no Epic boundary crossed.

- Question: "How should this run handle multiple Epics? (You will not be asked again this run.)"
- Options:
  - **Stop after each Epic** — pause at every Epic boundary so you can review and approve continuation. Today's per-Epic confirmation behavior — Section 4.2 branch 2 asks *"do you want to continue with the next logical Epic?"* between each Epic.
  - **Work through all Epics** — auto-continue across Epics; only stop when proceeding without your input would risk concrete downstream cost. Specifically, Mode 2 still pauses on (a) Section 4.2 branch 1's drafted-or-blocked-on-drafted Epic stop (no auto-continue across un-broken-down Epics — the loop must exit so the user can run `/quo-breakdown-epic`), (b) the Epic-boundary context-clear discipline before the next Epic begins, and (c) any final reviewer-surfaced blocker the orchestrator escalates from Sections 5 and 6.

Capture the user's choice once and store it as the **multi-Epic run mode** for the rest of this run. The choice persists across Epic boundaries — do not re-prompt at every Epic. Section 4.2's branch-2 logic branches on this captured value.

If only one Epic exists under the Bee at the time this step runs, **skip the question entirely** — there is no Epic boundary to chain across.

#### Check if stale
Be aware that the Epic was written before coding started. If the Epic has `up_dependencies` that have been completed then
you must review the work actually done in those Epics to see if this current Epic description is stale:

1. Review the git diff to understand what was actually implemented
2. Read the upcoming Epic and its Tasks/Subtasks
3. Update any Task or Subtask descriptions that are now stale given what was actually built in those prior Epics (e.g., file paths changed, function signatures differ, new modules were created)

#### Mark status when ready to start work

If ready, mark the Epic status with `status=in_progress` to show work has started on the Epic

### 3. Execute Tasks via per-Subtask Agent dispatch

The orchestrator (you, the Director) drives Tasks through a **reconciliation loop** that dispatches **fresh, ephemeral background `Agent` invocations** against the custom subagent types defined in this skill set's sibling `agents/` directory. There is no long-lived team; there are no warmed Agents; there is no peer-to-peer messaging between workers.

#### Reconciliation loop

The loop is **event-driven, not clock-driven**. Each tick has three phases:

1. **Read state.** Pull the current truth from three sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <epic-id>` to get the Epic's `children` array (Task IDs); for each Task, fetch its full details including its own `children` array (Subtasks); read every Subtask body, since these carry the detailed instructions (Context, What Needs to Change, Key Files, Acceptance Criteria) the dispatched Agent will follow. Sort Tasks in dependency order (check each Task's `up_dependencies`). Verify at least one Task exists with at least one Subtask and all are non-drafted (`status!=drafted`). Use the canonical querying recipe (see `docs/doc-writing-guide.md` `## Querying tickets`) for any focused state query, e.g.:

     ```bash
     bees execute-freeform-query --query-yaml 'stages:
       - [id=<ticket-id>]
     report: [title, ticket_status]'
     ```
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done).
   - **git state** — the actual diff on disk. Workers communicate by editing files; the diff is the only authoritative record of what they actually did.

   Mark the current Task `status=in_progress` and the Bee `status=in_progress` (if not already set) the first time a Task starts.

2. **Reconcile.** Compare current state to target state and act:
   - For every Subtask whose dependencies are satisfied and which has no Agent already in flight for it, dispatch a fresh Agent (see "Per-Subtask cold dispatch" below).
   - For every Agent that has reported completion, persist the result: confirm the bees ticket transitioned to `status=done`, mark the corresponding TaskList task `completed`, and unlock any newly-eligible downstream Subtask.
   - When all Subtasks of the current Task are `done`, advance to the per-Task PM review by dispatching a fresh PM Agent (see "Per-Task PM dispatch" below).
   - When all Tasks of the current Epic are `done`, advance to the inter-Epic interaction checkpoint described in Section 4.2.

3. **Yield.** The orchestrator does not poll. After dispatching the work this tick uncovered, return control to the harness and wait for the **Agent completion notification** delivered by the `run_in_background=true` substrate. The notification is what triggers the next tick.

##### Anti-pattern: no clock primitives

The reconciliation loop is driven exclusively by Agent completion notifications. Do **not** use any of:

- **`/loop`** — repeats the orchestrator's last turn on a wall-clock cadence.
- **`ScheduleWakeup`** — fires the orchestrator after a delay.
- **`CronCreate`** — fires the orchestrator on a recurring schedule.
- **Polling** — re-reading bees / TaskList / git on a sleep-wait cycle without a triggering event.

If the work for this tick is dispatched and there is nothing else to reconcile, the correct action is to yield. Background Agents will wake the orchestrator when they finish; that is the only legitimate trigger for the next tick.

#### Per-Subtask cold dispatch

For each ready implementer Subtask, the orchestrator spawns a fresh Agent at Subtask scope:

```
Agent(
  subagent_type=<role>,            # one of: engineer, test-writer, doc-writer
  run_in_background=true,
  prompt=<dispatch prompt with the Subtask body embedded verbatim>,
)
```

Each Subtask gets its own Agent invocation. The orchestrator does **not** name Agents (`Agent(name=...)` is not used) and does **not** reuse an Agent across Subtasks. There is no `SendMessage` between Subtasks — the worker reads its assignment from the dispatch prompt, edits files, and exits. The diff is the handoff to the next role.

The PM and the reviewers (introduced in Section 5) are also dispatched fresh: the PM gets a new Agent at every per-Task review boundary, and reviewers get a new Agent at every Bee-level review.

##### Per-Subtask cold dispatch (vs SDD's warm-Agent intent)

The original SDD intent was warm Agents that would receive `SendMessage` pings between Subtasks, amortizing context-load cost across a Task. That path requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents) — and Epic 8s removes that substrate entirely, so `SendMessage`-based warm dispatch is no longer available. The trade-off is conscious: each cold-dispatched Agent re-loads its role file and any referenced docs, which is more tokens than a warm ping, but the architectural simplification (no team lifecycle, no shutdown choreography, no peer-to-peer coupling) is worth it; in practice prompt caching mitigates most of the cold-load cost. The divergence from the SDD's warm-Agent intent is intentional and is captured by Issue **`b.x9w`** ("Re-probe SendMessage-without-Agent-Teams as warm-Agent token-cost optimization") and a divergence note recorded in the SDD; revisit if the constraint changes.

##### Dispatch prompt: quote the ticket body verbatim

The dispatch prompt sent to each Agent must embed the ticket body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names) that the worker will then use literally. Read the ticket via `bees show-ticket --ids <ticket-id>` and embed the returned body in the prompt as a quoted block. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "your gating precondition is met — start now") is fine; the body itself stays untouched. The orchestrator's own progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the dispatched role's contract file (`agents/<role>.md`). The rule applies to **every** dispatched role type — both the implementer roles (Engineer / Test Writer / Doc Writer) and the review-only roles (PM, Code Reviewer, Test Reviewer, Doc Reviewer). Concrete examples of forbidden softening (illustrative, not exhaustive):

- MUST NOT tell the Engineer it may also write tests or docs.
- MUST NOT tell the Test Writer it may also modify source code.
- MUST NOT tell the Doc Writer it may also modify source or test files.
- MUST NOT tell the PM or any reviewer (Code Reviewer / Test Reviewer / Doc Reviewer) it may write source, tests, or docs — these are review-only roles, and the contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (each reviewer) explicitly.
- MUST NOT tell one reviewer it may also review another reviewer's lane (e.g., Code Reviewer reviewing tests, or Test Reviewer reviewing documentation).

The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also add this one test file" / "you may also touch this one source line"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer dispatch, a redirect or re-scoping of the Subtask, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other; the only handoff is from worker to orchestrator (the diff in execution mode, the JSON return in research mode), never worker-to-worker. So a softening clause cannot be made safe by adding "coordinate with the other role's diff" or similar coordination prose — that channel does not exist.

#### Hub-and-spoke via substrate

Workers do not message each other. The orchestrator is the hub; each dispatched Agent is a spoke that reads its prompt, edits files, and exits. The diff is the handoff between roles — when the Engineer finishes a Subtask, the next role (Test Writer, Doc Writer, or PM) reads the resulting diff to do its work. Hub-and-spoke is a **structural property** of ephemeral background Agents, not a rule the orchestrator must remember to enforce: there is no inter-Agent channel for workers to even attempt peer-to-peer coupling on.

#### Recursive delegation: not supported

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every Agent invocation originates from this skill's reconciliation loop, never from a worker. The bound on flat-orchestration context growth is **Section 4.2's Epic-boundary context-clear discipline**, which clears the orchestrator's context window between Epics so the loop's working set stays bounded across long Bees.

#### Roles dispatched by the orchestrator

The orchestrator dispatches the following four roles during a Task. The full role contracts (responsibilities, gating preconditions, instructions, shell-command etiquette) live in the role files; the orchestrator's job is to invoke the right role at the right time, not to carry the role's prose.

- **Engineer** (`agents/engineer.md`) — implements source-code Subtasks. Model: Opus (always). Does not write tests or docs.
- **Test Writer** (`agents/test-writer.md`) — implements test Subtasks and reviews the Engineer's diff for missing test coverage. Model: Opus (always).
- **Doc Writer** (`agents/doc-writer.md`) — implements documentation Subtasks, reviews the Engineer's diff for documentation gaps, and after the Engineer's diff has landed appends or updates a `### Feature: <title>` subsection in the project's cumulative PRD and SDD per the categorization heuristic (pure-refactor / architecture-only / deployment-CI / user-facing) defined in `agents/doc-writer.md` `## Cumulative project doc updates`. The `<title>` is the verbatim title of the Plan Bee at the top of the Subtask → Task → Epic → Plan Bee chain; the orchestrator surfaces it to the subagent in the dispatch context. See `agents/doc-writer.md` for the authoritative spec — including the categorization table, the `<title>` resolution rule, the idempotency rule, and the CLAUDE.md `## Documentation Locations` lookup-key recipe used to resolve the PRD and SDD paths. Model: user's choice (Opus or Sonnet, selected at the start of the run).
- **Product Manager** (`agents/pm.md`) — reviews the Task's work against the spec source resolved from the Bee's `reference_materials` (PRD/SDD files on disk via the `file-path` resolver, or the PRD/SDD `t1=Doc` children of a Spec Bee via the `bees` resolver), or the Bee body itself when `reference_materials` is null/empty; drives `quo-engineer-review` and `quo-doc-writer-review` per Task; and produces the per-Task summary report. See `agents/pm.md` `### Resolving reference_materials entries` for the authoritative resolver-branching logic — this dispatch prompt does not duplicate it. Model: user's choice (Opus or Sonnet, selected at the start of the run).

Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) are introduced in Section 5 (final Bee-level reviews).

##### Per-Task PM dispatch

When all child Subtasks of the current Task are `status=done`, dispatch a fresh PM Agent to do the per-Task review and produce the Task summary. The dispatch prompt must include the Task ID, the list of completed Subtask IDs, and `<scoped-marker-resolver-path>` — a placeholder the orchestrator fills in at runtime so `agents/pm.md` can perform its Scoped-marker check (see "Scoped-marker PM dispatch wiring" below).

#### TaskList as progress UI

The orchestrator uses Claude Code's native **TaskList** as the visible progress UI for the run. There is no separate display backend to configure — TaskList renders in the harness automatically, replacing the team-display surface a prior message-bus substrate would have required.

For every Agent the orchestrator dispatches, it creates exactly **one** TaskList task:

- **`pending`** — created when the orchestrator decides this Subtask is next but before the Agent invocation lands.
- **`in_progress`** — set the moment the Agent invocation is dispatched (`Agent(...)` returns).
- **`completed`** — set when the orchestrator processes the Agent's completion notification and confirms the bees ticket transitioned to `status=done`.

Use `metadata.activity` on the TaskList task to surface finer-grained progress when a worker emits intermediate signal (e.g., `"running narrow tests on package X"`, `"resolving Scoped-marker for grandparent bee"`). The orchestrator updates this string opportunistically; it is informational, not a routing input.

##### TaskList naming convention

The naming convention is the **canonical cross-reference** for downstream Tasks (later Sections of this SKILL.md and other skills in the workflow consume these names). It is deterministic so two concurrent invocations cannot collide and unambiguous so any reader can map a TaskList entry back to its bee ticket:

- **Implementer Agents** (Engineer, Test Writer, Doc Writer) — **Subtask scope**. Name: `<role>-<subtask-id>` (e.g., `engineer-t3.abc.def.gh`, `test-writer-t3.abc.def.ij`, `doc-writer-t3.abc.def.kl`). Each Subtask gets its own implementer Agent and its own TaskList task; subtask-id makes the name unique even when sibling Subtasks of the same Task run concurrently.
- **PM Agents** — **Task scope**. Name: `pm-<task-id>` (e.g., `pm-t2.abc.def.gh`). The PM reviews the whole Task at once, so its scope suffix is the parent Task's id.
- **Reviewer Agents** (Code Reviewer, Test Reviewer, Doc Reviewer — see Section 5) — **Bee scope**. Name: `<reviewer>-<bee-id>` (e.g., `code-reviewer-b.abc`, `test-reviewer-b.abc`, `doc-reviewer-b.abc`). Reviewers run once per Bee at the final Bee-level review, so the scope suffix is the Bee id.
- **Deferral-ledger tasks** — **Run scope**. Name: `defer-<short-suffix>` (e.g., `defer-1`, `defer-2`, or any collision-resistant suffix). Created when an agent's structured return (per `agents/pm.md`'s Final report contract or `agents/analyst.md`'s `### Deferred refinements` block) names a destination the orchestrator chose not to address inline this run — `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. `metadata.activity` carries the deferral's one-line description so the gate prose (Section 6.5 below) can surface the active set. Marked `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (in which case `metadata.activity` logs the resolution path). The pre-handoff Section 6.5 gate reads this ledger for active `defer-*` entries and refuses to yield control while any remain pending or in-progress.
- **Gate-task tasks** — **Turn scope**. Name: `gate-<kind>-<short-suffix>` (today the dominant `<kind>` is `askuserquestion`, e.g. `gate-askuserquestion-1` for an `AskUserQuestion` gate fired during Section 5's review loop, Section 6's post-completion findings gate, or Section 6.5's deferral-hygiene gate). Created by the orchestrator via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract documented in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. The `<short-suffix>` MUST be unique per fire within the same run across every `gate-*` task regardless of `<kind>` — see the per-fire-uniqueness rule in that contract section for the two acceptable patterns (monotonic integers or gate-specific slugs encoding context). The two-step contract applies at every gate this skill fires — both the trailer-driven gates surfaced by the review skills (Section 5's review-loop's escalation gates when the orchestrator escalates a contested finding to the user) and the trailer-less orchestrator-driven gates (Section 4.2's continue-or-stop multi-Epic gate when Mode 1 is selected, Section 6's post-completion findings gate, Section 6.5's deferral-hygiene gate, Section 7's Acceptance-Criteria sign-off and Bee close-out gates). `metadata.activity` carries the gate's finite choices verbatim where applicable. Marked `completed` the moment the prescribed tool call returns and its result has been consumed (the user's answer routed, the next branch entered, etc.). Normally enters and exits within a single turn — the lifecycle is shorter than `defer-*` (which spans the whole run). The **yield-control discipline** mirrors `defer-*`: this skill MUST NOT yield control to the harness while any `gate-*` task is in `pending` or `in_progress` status. If a `gate-*` task is somehow left active when the orchestrator would yield (e.g., a bug fired the prescribed tool call without the paired `TaskCreate`, or the orchestrator hit an error between the two), the next reconciliation tick walks the TaskList, surfaces the active `gate-*` task, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<subtask-id>`, `pm-<task-id>`, and the Bee-scoped reviewer names (`code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`).

#### Scoped-marker PM dispatch wiring

When the orchestrator dispatches the per-Task PM Agent (per "Per-Task PM dispatch" above), the dispatch prompt must include the **resolved path** to the Scoped-marker helper as a `<scoped-marker-resolver-path>` substitution. The helper is a sibling-skill bundled script; resolve its path at runtime from this skill's own base directory:

```
<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py
```

The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-execute`). Use the `..` traversal pattern to reach the sibling skill — this matches the same sibling-resolution discipline already used elsewhere in the skill set.

```bash
# POSIX (bash / zsh): the path the orchestrator embeds in the PM dispatch prompt
<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py
```

```powershell
# Windows (PowerShell): the path the orchestrator embeds in the PM dispatch prompt
<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py
```

The orchestrator's responsibility ends at passing the resolved path placeholder to the PM. The orchestrator does **not** inline the Scoped-marker grammar, the temp-file recipe for staging the Bee body, or the helper invocation itself — `agents/pm.md` owns those. That separation lets `agents/pm.md` evolve the marker contract without dragging this SKILL.md along.

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

### 4. Per-Task and Per-Epic Cleanup

#### 4.1 After Each Task

When a Task and all its Subtasks are done (all reviewer feedback addressed or ignored):

1. Mark the Task as `status=done` (Subtasks were marked done by each agent as they completed their work, except doc Subtasks where the orchestrator does the flip on behalf of the doc-writer per `agents/doc-writer.md`'s no-`Bash` routing). **Do this before committing** so the `.bees/` status changes are included in the commit.
2. Create one git commit for the Task. **NEVER push to remote — committing only.** Use this staging procedure:
   1. Run the **Format** command from CLAUDE.md `## Build Commands` (e.g. `cargo fmt`, `prettier --write`, `gofmt -w`) to normalize formatting (agents may have triggered reformatting in files they didn't report). Do NOT re-run the test suite here — the `.T` subtask already validated, and the PM confirmed. Re-running wastes minutes per Task.
   2. Run `git status` to see the full set of modified and untracked files.
   3. Stage files that are related to this Task — include agent-reported files, formatting changes to files that were touched by this Task's agents, and (only if the Plans hive lives inside this repo) the resolved Plans hive path's contents. Use the same hive-path resolution as `/quo-plan` and `/quo-file-issue`:

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
3. Mark the per-Task TaskList tasks (named per the convention established in Section 3 — see "TaskList naming convention") as `completed` and clear them from the active set. There is no Agent shutdown to perform — the per-Subtask cold dispatches established in Section 3 already complete-and-exit when each Agent returns.
4. Output the summary below to the screen and advance to the next Task by dispatching fresh ephemeral implementer Agents per the dispatch shape in Section 3.

```
## Task [N] of [total] Complete: [task-title]

**Task ID**: <task-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Ignored Review Feedback**: [list items that were flagged by quo-engineer-review or quo-doc-writer-review but Director chose not to address, or "None"]
**Follow-up Tasks Created**: [count, if any] [list task-ids if created]
One of:
- Proceeding to next Task <task-id>
- Final Task, moving on to Final Reviews 
```

**Record each ignored-feedback item as a `defer-N` TaskList task at the moment of decision.** Whenever the Director chooses to ignore a review-feedback item rather than fix it now, create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the feedback's one-line description as the `metadata.activity` string, status `pending`. The PM Agent's Final report contract (`agents/pm.md`) requires the PM to annotate each deferred item with a destination — `addressed-now-in-this-Task` (no carrier needed), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — that the orchestrator records in the same `metadata.activity` string. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when items were ignored, defeating the gate's purpose. Items the Director addressed inline this Task (no ignored feedback surfaced) do **not** get a `defer-*` task — the `defer-*` ledger only tracks items not addressed now.

**Record each PM-deferred item as a `defer-N` TaskList task at the moment of the PM verdict.** When the per-Task PM Agent returns, walk its Final report deferred items (per `agents/pm.md`'s Final report contract). For every item the PM annotated with a destination of `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` (i.e., NOT `addressed-now-in-this-Task`, which is the PM's signal that the Director already addressed the item inline this Task and no inter-session carrier is needed), create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the deferral's one-line description as the `metadata.activity` string, status `pending`. Items annotated `addressed-now-in-this-Task` are NOT added to the `defer-*` ledger — they were addressed inline. This upstream record-creating step is the load-bearing source (paired with the ignored-feedback instruction above) for Section 6.5's deferral-hygiene gate; without it, PM-surfaced deferrals would only reach the active `defer-*` set via Section 6.5's Step 0 retroactive sweep, leaving the gate single-layered for PM-Final-report items where the peer skill `/quo-breakdown-epic` (per its per-Task PM dispatch site) is two-layered. Walking the PM Final report's deferred items here mirrors `/quo-breakdown-epic`'s per-Task PM-dispatch site and keeps the two-layer pattern (upstream + Step 0 sweep) symmetric across the two execution-skill peers.

#### 4.2 Find next Epic or move to Final Review

The Mode 1 continue-or-stop `AskUserQuestion` gate fired in branch 2 below fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this inter-Epic continuation gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` the moment the user's answer is consumed.

Before moving on from the just-completed Epic, perform an **inter-Epic interaction checkpoint**. This is a lightweight check deliberately positioned here (not at the final Bee-level review) so that issues introduced by this Epic's code interacting with *prior* Epics' landed code are caught while the context is fresh, before the next Epic compounds the problem.

The Director (you) runs this check directly — no new team:

1. Diff the Epic's landed commits against the previous Epic's end-state: `git log --oneline <previous-epic-last-commit>..HEAD`.
2. For each file this Epic touched that a prior Epic also touched, scan for:
   - **Contract drift** between what this Epic's code assumes and what a prior Epic's code actually does (especially ordering contracts, docstring claims, and "this should never happen" comments).
   - **Resource compounding** across Epics: if this Epic adds acquires from a resource that a prior Epic already uses, model the aggregate.
   - **Symmetric-change gaps**: if this Epic added a new resource class (key pattern, pool, queue, etc.), search prior Epics' cleanup paths for missing handling.
3. If any issue is found, dispatch a fresh ephemeral Engineer Agent per Section 3's dispatch shape to fix it before continuing to the next Epic. Do not defer to the Final Bee-level review — fixing at the Epic boundary keeps the scope local to the two Epics involved.
4. Record any fixes as additional commits on the branch, clearly labeled.

After the checkpoint passes (clean or fixed):

Mark the just-completed Epic as `status=done`, then re-query *all* Epics under the Bee to classify the post-Epic state. Do not assume "no workable Epic remains" means "Bee is finished" — Epics in `status=drafted` (still need `/quo-breakdown-epic`) must not fall through to final review.

**Epic-boundary context-clear discipline.** Because Section 3 ships flat orchestration (no recursive delegation), the orchestrator's working context grows monotonically across Epics — every Subtask dispatch, every PM review, and every reconciliation tick adds to the loop's running set. The Epic boundary is the natural reset point: at this point all child Tasks are complete, all per-Task commits are landed, and the only state worth carrying into the next Epic is the bees ticket store (which is on-disk and re-queryable). The discipline that bounds flat-orchestration context growth is therefore: **at each Epic boundary, before continuing to the next workable Epic, clear the orchestrator's working context**. This keeps the loop's running set bounded at roughly **~25-30% of the 1M context window per Epic**, which is the budget Section 3's "Recursive delegation: not supported" subsection refers to. The branch-2 "continue" path below explicitly invokes this discipline; treat it as the canonical pre-step-2 reset across all long Bees.

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1]
report: [title, ticket_status, up_dependencies]'
```

`up_dependencies` is returned as a list of ticket IDs only — not statuses. If any Epic is in `ready` state with non-empty `up_dependencies`, batch-look-up those dependency IDs via `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>` to determine whether each `ready` Epic is actually workable or blocked.

Classify the result into exactly one of three branches (the status vocabulary `drafted` → `ready` → `in_progress` → `done` is canonical for the Plans hive). Evaluate the branches in the order listed — branch 1 takes precedence over branch 2 when both apply, because any drafted Epic must stop the loop regardless of whether other Epics happen to be workable:

1. **Drafted (or blocked-on-drafted) Epics remain** — at least one Epic has `status=drafted`, OR has `status=ready` blocked on a dependency that is not `done` (typically a sibling Epic still in `drafted`). **Stop the loop. Do NOT proceed to Step 5 final review and do NOT offer to mark the Bee done.** Tell the user:

   > Epic `<just-completed-epic-id>` is complete, but Epics `<drafted-or-blocked-ids>` in this Bee are still `drafted` (or blocked on drafted dependencies) and need breakdown before this Bee can be closed. Run `/quo-breakdown-epic <bee-id>` (a fresh session is reasonable to keep context clean) to break down the remaining Epics, then re-run `/quo-execute <bee-id>`.

   Then exit the skill.

2. **Workable Epic remains** (and no drafted Epics exist) — at least one Epic has `status` in `{ready, in_progress}` AND all its `up_dependencies` are `done`. Branch on the **multi-Epic run mode** captured in Section 2:

   - **Mode 1 (Stop after each Epic), or Section 2's mode prompt was skipped** (only one Epic existed in scope at run start): ask the user if they want to continue with the next logical Epic. If they accept, clear your working context per the Epic-boundary context-clear discipline established above in this Section 4.2, then return to step 2. If they decline, move to final Bee review.
   - **Mode 2 (Work through all Epics)**: auto-continue. Surface a one-line note announcing the auto-continue and naming the next Epic ID being picked up so the user can interrupt if desired (e.g., *"Mode 2 (Work through all Epics): auto-continuing to `<next-epic-id>` — `<title>`."*). Then clear your working context per the Epic-boundary context-clear discipline established above and return to step 2. The Mode 2 auto-continue path still respects every other stop the orchestrator already enforces — branch 1's drafted-or-blocked-on-drafted Epic stop above takes precedence (the order-of-evaluation rule already requires evaluating branch 1 first), and any final reviewer-surfaced blocker from Sections 5 and 6 still halts the run.

3. **All Epics under this Bee are `done`** — proceed to Step 5 final Bee review.

### 5. Final Bee-level Code, Doc and Eng reviews

Once all Epics in the Bee are done, dispatch three concurrent ephemeral reviewer Agents per Section 3's dispatch shape, one per reviewer role: `Agent(subagent_type="code-reviewer", run_in_background=true)`, `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`. Track each via a TaskList task per Section 3's naming convention (bee-scoped form: `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`).

Conditional spawn — only dispatch a reviewer whose corresponding implementer was used during the Epic loop:
- If Engineer Agents were dispatched during the Epic loop, dispatch the code-reviewer Agent now.
- If Test Writer Agents were dispatched during the Epic loop, dispatch the test-reviewer Agent now.
- If Doc Writer Agents were dispatched during the Epic loop, dispatch the doc-reviewer Agent now.

Reviewer role contracts (responsibilities, model assignment, gating, instructions) live in the role files; the orchestrator's job is to dispatch, not to carry the role's prose.

- **Code Reviewer** (`agents/code-reviewer.md`) — reviews the Engineer's output and surfaces gaps against engineering standards.
- **Test Reviewer** (`agents/test-reviewer.md`) — reviews the Test Writer's output and surfaces gaps against test-quality standards.
- **Doc Reviewer** (`agents/doc-reviewer.md`) — reviews the Doc Writer's output and surfaces gaps against documentation standards.

- Get the feedback, and make a judgement call about whether that work must be done. Each of the three review skills above (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a second-person imperative routing trailer (`**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`) plus a counter-anchor clause at the bottom of its output, naming the precise routing this step must take after consuming the findings. **Follow the trailer literally** — it is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory.
  - If feedback requires action, dispatch fresh ephemeral implementer Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer / PM as needed). Stay in delegate mode.
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** spawn the Product Manager on this iteration
  - If not, move on to Final Review but you MUST share the ignored feedback for review
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in Final Review
  - **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.** Whenever the Director chooses to ignore Bee-level reviewer feedback rather than re-dispatch implementers to address it, create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the feedback's one-line description as the `metadata.activity` string, status `pending`. Where the reviewer's framing suggests a destination (e.g., "file follow-up Issue", "update <ticket-id> body"), record the destination annotation alongside the description in `metadata.activity`; otherwise, mark it as pending-destination so Section 6.5's gate will surface the bullet for the user to map. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when items were ignored at this site, defeating the gate's purpose.


### 6. Post-Completion Review

After the review loop in step 5 is done and all fixable issues have been addressed by the team, run one final fresh-context generalist sweep across all changes made by this Bee. This is an independent quality gate — separate from the per-Task and per-Epic review cycles above.

**Anti-pattern callout — read before acting.** Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/quo-engineer-review` is scoped to source code, `/quo-doc-writer-review` to user-facing docs, `/quo-test-writer-review` to test files — none of them runs the cross-lane sweep this step needs). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, PM verdict, and per-Task reviewer verdicts from the whole Bee run; that context biases it toward "did the phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the Bee body and nothing else — that's the point.

1. Compute the pre-Bee diff scope. Capture `<pre-bee-sha>` as the HEAD that existed when work began on this Bee (use the SHA recorded at the start of the run, or `HEAD~M` where `M` is the number of Tasks committed in Step 4 — one commit per Task; if you've lost count, walk `git log` back to the commit before the first Task commit landed in Step 4 as a backup). Collect the Bee ID `<bee-id>` and, secondarily, the IDs of the Epics/Tasks under it as `<epic-id-1> <task-id-1> ...` (the Bee body is the primary spec; Epic/Task bodies are secondary context the reviewer can consult when something in the diff is ambiguous).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. The agent will not see anything else from this run, so the prompt must be self-contained. Starting skeleton (substitute `<pre-bee-sha>`, `<bee-id>`, and the Epic/Task IDs before sending):

   ```
   You are an independent reviewer for a quorum Bee that was just shipped.

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

   Note: in skill repos (where the diff includes `skills/<name>/SKILL.md` or
   `agents/<name>.md` files), those markdown files are skill / subagent program
   source code, not natural-language documentation. Review them with the same
   rigor as language-specific source — broken cross-references, drifted
   contracts, ambiguous prose, and CLAUDE.md design-rule violations are all
   in scope.

   Do NOT do a general repo audit. Stay focused on the diff.

   Do NOT invoke /quo-engineer-review, /quo-doc-writer-review, or /quo-test-writer-review at
   this stage. Those skills are designed as parallel lanes of an in-flight
   review; they each have lane-specific scope rules that make them wrong for a
   final generalist sweep.

   Return findings as a numbered list. For each item: `file:line`, what's
   wrong, severity (`blocker` / `suggestion` / `nit`). If clean, return
   exactly "no issues found".
   ```

   Wait for the agent's report.

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-Task PM verdict and per-Task code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

   **Orchestrator self-tracking close-out (mandatory before yielding).** Independent of the per-Task TaskList tasks already closed in Section 4.1 step 3 and the Bee-scoped reviewer TaskList tasks (`code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`) dispatched in Section 5, the orchestrator typically creates additional ad-hoc TaskList tasks during this Section 6 pass to break the post-completion review into discrete steps (e.g., "Get diff scope", per-ticket "Verify <id>" entries, "Synthesize findings"). Before presenting the synthesized findings to the user — i.e., before yielding the turn at step 4 / step 5 below, whether to deliver "no issues found" or to ask the user how to handle flagged issues via `AskUserQuestion` — mark every such orchestrator self-tracking TaskList task `completed` and clear them from the active set. The yield is the close-out trigger: when the orchestrator stops responding (either at end-of-flow or to wait on the user's reply), the TaskList must show no `in_progress` entries left over from these synthesis steps. This discipline is the orchestrator-self-tracking analog of Section 7 step 6's per-finding follow-up close-out in `quo-fix-issue` (which scopes to dispatched `<role>-postcomp-<n>` Agents and `file-issue-postcomp-<n>` per-finding tracking entries); the two are complementary, not overlapping.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and continue to Final Output.

5. If the agent flagged any issues, fire the user-facing gate through the two-step `TaskCreate` → `AskUserQuestion` contract documented in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this post-completion findings gate (per Section 3's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` in the same turn. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch in step 6 is entered.
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now before closing the Bee
     - **File as issue tickets** — create issue tickets via `/quo-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
   - **Fix in this session**: Reform the implementation team and delegate the fixes. Stay in delegate mode. After fixes are done, commit and continue to Section 6.5 (deferral hygiene).
   - **File as issue tickets**: For each issue, invoke `/quo-file-issue` with the issue description. Report the created ticket IDs to the user. Continue to Section 6.5.
   - **Skip**: Continue to Section 6.5.

### 6.5 Before handoff — deferral hygiene

Every `AskUserQuestion` firing in this gate (Step 2's initial Fix / File / Encode choice, plus any Step 3 re-fires when an earlier routing branch failed to close out a subset of the active `defer-*` set) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate (a distinct `<short-suffix>` per fire, so the Step 3 re-fires are not mistaken for the Step 2 first fire), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed.

Section 6's Fix / File / Skip gate handles only the fresh-eyes generalist sweep's findings. Throughout the Epic loop (Sections 3–4) and the in-flight reviewer loops (Section 5), the PM Agent's per-Task reports and any earlier orchestrator-side judgement calls may have flagged additional items as "address later", "defer to next phase", "pick up during a follow-up Issue", or similar inter-session deferrals. Each such item that the orchestrator chose not to address inline MUST have been recorded as a `defer-<short-suffix>` TaskList task per Section 3's TaskList naming convention (at the per-Task site in Section 4.1 and at the may-ignore-feedback site in Section 5); this gate is the pre-handoff reconciliation step that closes them out into durable inter-session carriers.

Section 7's existing "show ignored feedback" prose at Bee close-out stays as the display layer — it surfaces the now-closed-out deferrals to the user one last time. This gate is the structural step that ensures the active set is empty before that display fires.

**Step 0 — Retroactive ledger reconciliation (safety net).** Section 4.1's `**Ignored Review Feedback**` summary field on each per-Task report and Section 5's may-ignore-feedback site each instruct the Director to create a `defer-<short-suffix>` TaskList task at the moment the item is ignored. Before running Step 1's enumeration, walk every per-Task summary the orchestrator produced during this run, every PM Final report's deferred items (per `agents/pm.md`'s Final report contract — every item with a `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` destination annotation maps to a `defer-*` task; items annotated `addressed-now-in-this-Task` are skipped because they were addressed inline), and any orchestrator-side ignored item that did not flow through those two surfaces, and **create a corresponding `defer-*` TaskList task for any item that does not already have one**. The upstream record-creating instructions at Section 4.1 and Section 5 are the load-bearing source; this retroactive sweep is the defense-in-depth safety net for orchestrators that miss the instruction (or for runs where an item was ignored outside the documented sites). After the retroactive reconcile, every ignored item is represented in the active `defer-*` set and Step 1's enumeration sees the canonical view.

**Step 1 — Enumerate the active deferral ledger.** Scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. If the active set is empty, emit a one-line console message — recommended string: `Deferral hygiene: no deferred items.` — and proceed to Section 7 (Final Output).

**Step 2 — Surface the active set and gate the user choice.** When the active set is non-empty, surface the list to the user as numbered markdown (one bullet per `defer-*` task, the `metadata.activity` text as the bullet's body), then fire the user gate through the two-step `TaskCreate` → `AskUserQuestion` contract per CLAUDE.md `## AskUserQuestion usage` and `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 3's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` with the finite choices below in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the routing into Fix / File / Encode begins.

- **Fix in this session** — Re-dispatch the appropriate implementer / reviewer Agents per Section 3's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch below, to resolve each deferred item now. After each item is resolved, mark its `defer-*` TaskList task `completed` (with `metadata.activity` updated to log the resolution path).
- **File as issue tickets** — For each item, invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body (the precedent for inline-Skill-tool dispatch lives in `/quo-fix-issue` Section 1's URL-resolution sub-step and `/quo-plan` Step 4b). Mark each `defer-*` TaskList task `completed` once the `/quo-file-issue` dispatch returns successfully and the created Issue ID is captured.
- **Encode in an existing ticket body** — For each item the user maps to an existing ticket (a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass), append a `## Deferred from /quo-execute run` section to the named ticket's body and run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update. Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir per CLAUDE.md `## Scratch-file convention`. **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode — e.g., for the encode triggered by `defer-3`, the scratch file is `bees-body-defer-3.md`. Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the scratch file directly back to its TaskList progenitor:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.quorum
  # then write the revised body to /tmp/.quorum/bees-body-<defer-N>.md via the Write tool
  # (e.g., /tmp/.quorum/bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
  # then write the revised body to $env:TEMP\.quorum\bees-body-<defer-N>.md via the Write tool
  # (e.g., $env:TEMP\.quorum\bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  Do NOT remove the temp file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. Mark each `defer-*` TaskList task `completed` once the update succeeds.

  **Follow-up commit (after all Encode writes in this gate firing have landed).** This gate fires AFTER Section 4.1's per-Task commit step has already produced one commit per Task in this run — so the `bees update-ticket --body-file` writes above persist new on-disk changes to the relevant hive's per-ticket directory (or to the project PRD/SDD file path), but those changes are NOT swept into any prior per-Task commit and would otherwise leave the working tree dirty when the skill yields. Produce one follow-up commit per gate firing covering all Encode writes from this firing — not per Encode item — to keep commit churn proportional to the user's choice. Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (the same pattern Section 4.1's commit step uses for Plans), `git add` each hive path that lives inside this repo, additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations, then commit only if `git diff --cached` shows staged changes (an out-of-repo hive plus no PRD/SDD encode routes would stage nothing — skip the commit in that case rather than producing an empty one). Commit subject contract: `Encode deferral: /quo-execute — <N> ticket(s) updated` where `<N>` is the count of `defer-*` items the user routed to Encode in this gate firing.

  This workflow (hive-path resolution via `bees list-hives`, in-repo scoping, conditional commit on staged state) is encapsulated in a bundled Python helper, `encode_deferral_commit.py`, so the orchestrator runs it as a single literal Bash tool call rather than decomposing a multi-step shell snippet at runtime. The helper resolves the Plans/Specs/Issues hive paths, `git add`s each hive path that lives inside this repo (out-of-repo hives have already had their bees update persisted by `bees update-ticket` and require no git action), `git add`s any project PRD/SDD paths passed via `--doc-path`, then commits only if there are staged changes — printing `skipped: nothing staged` and making no commit when nothing is staged. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree (same anti-pattern as Section 4.1's per-Task commit step); the helper stages only the resolved hive paths and the explicit `--doc-path` arguments, never `-A`.

  **Resolving the helper path (own-skill resolution).** `encode_deferral_commit.py` is shipped by this skill (`/quo-execute`); resolve it against **this skill's own base directory**: `<this skill's base directory>/scripts/encode_deferral_commit.py` (no `..` hop). The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-execute`). **This differs from `/quo-fix-issue` and `/quo-breakdown-epic`,** which resolve the same helper as a *sibling* of their own base directory because they consume it across skills; here, in `/quo-execute` itself, the helper lives inside this skill, so resolution drops the `..` hop.

  Invoke it with `--skill quo-execute`, `--count <N>` (the count of `defer-*` items the user routed to Encode in this gate firing — matching the commit-subject contract above), and one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`; omit entirely in the common case where no doc was routed):

  ```bash
  # POSIX (bash / zsh):
  python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]
  ```

  ```powershell
  # Windows (PowerShell):
  python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]
  ```

  After the helper lands the commit (or prints `skipped: nothing staged`), proceed to Step 3 below.

The three options are mutually-non-exclusive at the active-set level — the user may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., "fix items 1 and 2 now, file 3 as an Issue"). Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. When the user wants to route different items to different options, they select `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`) and type the per-item routing in free-form; the orchestrator parses the reply and closes out each `defer-*` task accordingly, per `docs/doc-writing-guide.md` `## AskUserQuestion patterns`.

**Step 3 — Hard-stop on a non-empty active set.** Until every `defer-*` task is `completed`, the skill cannot proceed to Section 7 (Final Output) and cannot mark the Bee `done`. This is the structural enforcement: a deferral that was important enough to surface during the run is important enough to encode in a durable carrier before the run ends. If the user picks options that fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or a `bees update-ticket` invocation errors), surface the still-active `defer-*` tasks back to the user with `AskUserQuestion` and re-run the gate until the active set is empty.

The fresh-session-per-phase recommendation at Bee close-out (Section 7 / Section 10) is preserved verbatim — this gate sits before that handoff prose; it does not replace it.

### 7. Final Output

When **all** Epics in the Bee are done, you must show the User the full list of all Reviewer feedback you chose to ignore.
- Use the AskUserQuestion tool to ask the User if they want you to act on any of these, or just continue.

Every `AskUserQuestion` invocation in this section MUST go through the two-step `TaskCreate` → `AskUserQuestion` contract documented in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. For each gate (the ignored-feedback action gate, the per-Acceptance-Criteria sign-off gate, the final Bee-done gate below), **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry — distinct suffix per distinct gate), **then** call `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the user's answer is consumed.

For each Acceptance Criteria, either demonstrate it directly (via test or script) or instruct the user how to validate it manually. Then use `AskUserQuestion` to get official sign-off on the Acceptance Criteria.

Then use `AskUserQuestion` with:
- Question: "Are you ready to mark this Bee as done?"
- Options:
  - "Yes, mark as done"
  - "No, we have more work to do"

### 8. Mark Bee Complete

Once the user approves the Bee as done:

1. **Precondition check (defense-in-depth).** In a healthy flow every Epic under this Bee was already transitioned to `status=done` at the end of its iteration in Step 4.2, so by the time you reach this step nothing should require a status change. Do not bulk-flip Epic statuses here — that would silently mark `drafted` work as `done`. Instead, re-query and verify:

   ```bash
   bees execute-freeform-query --query-yaml 'stages:
     - [parent=<bee-id>, type=t1]
   report: [title, ticket_status]'
   ```

   If any Epic returns with `ticket_status` other than `done`, abort with:

   > Cannot mark Bee complete — Epics `<ids>` are still `<status>`. Run `/quo-breakdown-epic` and `/quo-execute` on them first.

   Do not silently update them. (Reaching this branch indicates a bug upstream — the Step 4.2 classifier should have stopped the run before Step 7 ever asked the user to close the Bee.)

2. All Epics confirmed `done` — mark the Bee itself:
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