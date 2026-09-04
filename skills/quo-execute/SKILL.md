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

All `AskUserQuestion` gates in this section (the conditional session-effort gate under `#### Check session reasoning effort`, the Bee pick under `#### Pick the Bee`, and the worktree / isolation-strategy gate under `#### Validate isolation strategy`, in that order) fire through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment `AskUserQuestion` returns and the user's answer is consumed.

The session-effort gate is **conditional** — it fires only when its precondition is met, and when it does not fire **no `TaskCreate` fires for it either**. See the sub-step immediately below for the load-bearing ordering rule.

#### Check session reasoning effort

Run this check **first in this section**, ahead of the Bee-pick gate below and the Epic-pick gate in Section 2. Its **Let me change it first** option exits the run, so firing it before any other gate means the user never re-answers a pick they already made.

This skill is tuned for an orchestrator session running at **`medium`** reasoning effort or higher. Every subagent dispatched from a role file (`agents/*.md`) has its effort pinned in that file's frontmatter and is **not** affected by the orchestrator's session setting, so this check concerns the seat you are running in plus any dispatch that has no role file — notably Section 6's `general-purpose` post-completion review sweep, which inherits the session setting. The skill cannot change the session setting itself — the most it can do is name the recommendation and let the user apply it.

**Ordering is load-bearing.** Read the environment variable **first**, evaluate it against the floor, and only *then* decide whether a gate fires. Do NOT create the gate task before the comparison: on the common path no gate fires at all, and a stranded `pending` `gate-*` task violates the yield-control discipline of the two-step contract — whose recovery mechanism re-fires the prescribed tool from any leftover `gate-*` task, producing a phantom prompt on a later run.

**Step 1 — read the session's current effort.** One literal command, no shell conditional (the comparison below is your own reasoning, not shell logic):

```bash
# POSIX (bash / zsh):
printenv CLAUDE_EFFORT
```

```powershell
# Windows (PowerShell):
Write-Output $env:CLAUDE_EFFORT
```

`CLAUDE_EFFORT` reports the session's **current** effort level and tracks mid-session changes (e.g. via `/model`) rather than echoing a launch-time flag, so the floor comparison reflects the level the session is actually running at when you read it.

If the output is empty, the command exits non-zero, or the value is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat it as unset (an older CLI, a launch path that does not export it, or a token this skill does not know how to order): **skip this check entirely and continue to the next step, silently.** A spurious prompt on every run is worse than a missed advisory.

**Step 2 — compare against this skill's floor, which is `medium`.** The ordering is `low` < `medium` < `high` < `xhigh` < `max`. Compare against the floor, never for equality — an operator running hotter than the recommendation costs wall-clock but not quality, and interrupting them is pure gate-fatigue noise.

- **At or above `medium`** — say nothing at all. No gate, no prompt, no output, and **no `TaskCreate`**. Continue to the next step.
- **Strictly below `medium`** — fire the gate in step 3.

**Step 3 — fire the gate (this branch only).** Per the two-step `TaskCreate` → `AskUserQuestion` contract stated at the top of this Section 1, first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate, then call `AskUserQuestion` in the same turn. Substitute the value read in step 1 for `<current>`. Question text:

```
This session is running at `effort=<current>`, below the `medium` floor this
skill is tuned for. This skill delegates implementation rather than producing
work itself, but it still owns ticket state, dispatch ordering, gate handling
and the review loop.

Subagent effort is pinned per role and is NOT affected by this setting.
```

Present these options:

1. **Proceed anyway** — Run at the current effort level. Mark the `gate-*` task `completed` and continue to the next step.
2. **Let me change it first** — Exits without dispatching anything; the user runs `/model`, then re-invokes. Mark the `gate-*` task `completed`, then exit cleanly.

#### Pick the Bee

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

#### Write the run-state manifest

This is the **canonical definition site** for the run-state manifest; later sections refer to it by name. Write it as the last step of Section 1, once the Bee ID and the isolation strategy are both known and before any Epic work begins.

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds ticket state, git holds the diff, the compromise tracker holds accepted compromises, and the `defer-*` TaskList holds open deferrals; the manifest holds only what those four do not. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `run-state-quo-execute-<bee-id>.md`, where `<bee-id>` is the **Bee ID** for this run (e.g., `run-state-quo-execute-b.abc.md`). Create the `.quorum` directory if it does not already exist, then author the manifest via the `Write` tool (no shell redirect):

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write the manifest to /tmp/.quorum/run-state-quo-execute-<bee-id>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write the manifest to $env:TEMP\.quorum\run-state-quo-execute-<bee-id>.md via the Write tool
```

**The filename is deterministic — do NOT add a random suffix or timestamp.** This deliberately differs from the compromise tracker's `<short-suffix>` naming, and the difference is load-bearing: the tracker's reader is a dispatched Agent that is handed the path in its prompt, while the manifest's reader is the orchestrator itself, possibly after a compaction that dropped the path from the conversation. A random suffix would be unfindable exactly when the manifest is needed most.

**Why the key is this skill's name plus the Bee ID.** The ticket-ID half of the key has to satisfy two properties, and the Bee ID satisfies both. It is **re-derivable without the conversation**: the Bee ID is this run's argument, and it is the `parent` of every Epic and the grandparent of every Task the run touches, so an orchestrator that has lost the conversation recovers it from any in-flight Plans-hive ticket with a single `bees show-ticket` / `bees execute-freeform-query` call. And it is **discriminating across projects**: ticket IDs are minted per bees workspace, so two runs against two different projects do not normally land on the same filename in the machine-wide `<tempdir>/.quorum/`.

The **`quo-execute` segment is what discriminates across sibling skills**, and it is not decorative: `/quo-breakdown-epic` keys its own manifest on the *same* Bee ID (its Bee-ID-first resolution order), so without the skill-name segment a `/quo-execute` run started against a Bee that a `/quo-breakdown-epic` session is still working would truncate that session's manifest out from under it — exactly the sequence `/quo-breakdown-epic`'s *"In a fresh session, execute this Epic first; defer downstream breakdown"* menu option invites, since that fresh `/quo-execute` session starts while the breakdown session is still live. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends: `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has, while `/quo-fix-issue` — whose batch membership is only recoverable from inside the manifest itself — appends the repository directory basename instead. See each skill's own manifest section for its rationale.

The remaining trade is against the scratch-file convention's collision-resistance guidance, and it is accepted knowingly: two concurrent `/quo-execute` runs against the same Bee already collide destructively over ticket statuses and commits, so that is not a case the workflow supports.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it fresh at run start (overwriting any manifest left by a previous `/quo-execute` run against the same Bee) and rewrite it in full at each Epic boundary per Section 4.2's Epic-boundary state-externalization checkpoint. Never delete it — the scratch-file convention forbids cleanup, so do NOT instruct any `rm` / `Remove-Item`.

**Contents — and an invariant that bounds them.** The manifest carries **only values that have no other durable home.** Do not add ticket titles, Subtask bodies, review findings, or anything else already readable from bees, git, the tracker, or the TaskList; those have carriers of their own and duplicating them here would grow the manifest into a shadow ticket store that drifts. The fields are:

```markdown
# Run state — quo-execute @ <bee-id>

- **Skill:** quo-execute
- **Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>
- **Unit scope:** Bee <bee-id>; Epics in scope: <epic-id-1, epic-id-2, ... | pending Section 2 query>
- **Multi-Epic run mode:** <Mode 1 (Stop after each Epic) | Mode 2 (Work through all Epics) | not captured (single Epic in scope) | not captured (all Epics already done) | not captured>
- **Isolation strategy:** <branch created: <name> | current branch: <name> | worktree: <path>>
- **Pre-Bee SHA:** <pre-bee-sha>
- **Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md
- **Progress:**
  - <epic-id>: done — last commit <sha>
- **Next unit:** <next-epic-id | none>
```

Two of those enums carry a **first-write-only** value: the bare `not captured` for the run mode, and `pending Section 2 query` for the Epics-in-scope list. They are the literals the run-start write uses (see below) and the ones Section 2's unconditional rewrite replaces — they are listed here so that a first-write manifest contains only template-legal values. They must never survive past Section 2.

Capture `<pre-bee-sha>` here, at run start, with one literal command — this is the **only** place the run records it, and Section 6's post-completion review reads it back from this file:

```bash
# POSIX (bash / zsh):
git rev-parse HEAD
```

```powershell
# Windows (PowerShell):
git rev-parse HEAD
```

The **compromise tracker** field records the tracker's full path *including* its random `<short-suffix>`. Generate that filename here, at run start, per Section 6.5 `#### Session-scoped compromise tracker` (the timestamp and suffix are generated once per run), and record it in this field — the manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. The tracker file itself is not created until its first append trigger fires; recording the path here does not create it.

The **Progress** field carries one line per unit this run has finished with, in the order they were worked. The normal shape is the template's `<epic-id>: done — last commit <sha>`. Two **aborted** shapes also exist, both written by Section 4.2's `##### Aborted-run close-out` through the Epic-boundary checkpoint's step 2, and which one applies depends on **the scope that close-out's step 2 resolved** — the aborted lane's scope when a lane aborted, or the review site the routing-decision gate's `Cancel` fired from when that is what routed there:

- **Mid-Epic abort** (a per-Task writer lane, or a `Cancel` at the per-Task review site) — `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`, replacing the `done` entry the Epic never earned.
- **Bee-level-review abort** (a Section 5 Bee-scoped re-dispatch, or a `Cancel` at Section 5's Bee-level review) — `<bee-id>: Bee-level review aborted — <what stopped it>`, naming the aborted lane (e.g. `test-writer-b.abc`) when a lane aborted, or — on the `Cancel` route, where there is no lane to name — the review site plus the finding the gate fired on, which is the same pair close-out step 3 already tells the orchestrator to state. This shape keys on the **Bee** id rather than an Epic id precisely because no Epic is in a non-`done` state to name: every Epic finished, and its `done — last commit <sha>` entry is correct and stays untouched. Do **not** overwrite a `done` Epic entry with an aborted one on this path.

This field is an **in-run, pre-compaction** record, not a cross-session one: a resuming `/quo-execute <bee-id>` truncates the manifest at run start (per the semantics rule above), so the readers of a Progress entry are this run's own later Epic boundaries — the checkpoint's step 1 resolves `<previous-epic-last-commit>` from it — and a post-compaction orchestrator still inside this run. What a *later* session reads to learn where an aborted run stopped is bees and git.

The **multi-Epic run mode** and the **Epics in scope** list are not known yet at this point (Section 2's Epic query and mode gate produce them), so write `not captured` and `pending Section 2 query` respectively on the first write. Section 2 resolves both placeholders in a single unconditional rewrite once its Epic query has returned — on **every** path through that section, including the ones where the mode gate never fires (see Section 2's `#### Resolve the manifest placeholders` step). The mode is a user choice with no re-derivation path — if it is lost, the run cannot know whether to auto-continue — which is precisely why it belongs here.

### 2. Find Epic to work on and validate

The multi-Epic run-mode gate in this section (under `#### Pick a multi-Epic run mode (only when more than one Epic is in scope)`) fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed.

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
  - **Work through all Epics** — auto-continue across Epics; only stop when proceeding without your input would risk concrete downstream cost. Specifically, Mode 2 still pauses on (a) Section 4.2 branch 1's drafted-or-blocked-on-drafted Epic stop (no auto-continue across un-broken-down Epics — the loop must exit so the user can run `/quo-breakdown-epic`) and (b) any final reviewer-surfaced blocker the orchestrator escalates from Sections 5 and 6. Mode 2 also still **performs** Section 4.2's **Epic-boundary state-externalization checkpoint** at every Epic boundary — the checkpoint is a set of verify-and-write steps the orchestrator runs itself, not a pause, so it never prompts the user and is not one of Mode 2's stops.

Capture the user's choice once and store it as the **multi-Epic run mode** for the rest of this run. The choice persists across Epic boundaries — do not re-prompt at every Epic. Section 4.2's branch-2 logic branches on this captured value.

If only one Epic exists under the Bee at the time this step runs, **skip the question entirely** — there is no Epic boundary to chain across.

#### Resolve the manifest placeholders

**Rewrite the run-state manifest** (Section 1 `#### Write the run-state manifest`) as soon as this section's Epic query has returned and the mode gate above has either fired or been skipped. **This rewrite is unconditional — it runs on all three paths through the gate**, not only the one where a mode was captured, because Section 1 wrote the literal placeholder `pending Section 2 query` into `Epics in scope` and that placeholder must not survive into any Epic's work. Write:

- **Epics in scope** — the real Epic IDs returned by the `[parent=<bee-id>, type=t1]` query above, on every path.
- **Multi-Epic run mode** — the captured choice whenever the gate fired *at any point in this run*, not only on this pass. Section 2's gate is one-time, so on a loop-re-entry pass (below) it does not re-fire; the mode already recorded in the manifest **is** the captured choice and is written back unchanged. Only when the gate has never fired in this run does the field take one of two skip literals, chosen by this precedence rule: write `not captured (all Epics already done)` whenever **every** Epic under the Bee reads `done`, and reserve `not captured (single Epic in scope)` for the remaining skip case — exactly one Epic under the Bee, and it is **not** yet `done`. The precedence matters because a Bee holding exactly one already-`done` Epic satisfies both descriptions; the all-done literal wins there, so the same Bee state always produces the same literal.

**On loop re-entry, carry the accumulated fields forward — do not re-emit Section 1's template.** Section 4.2 branch 2 returns to this section for each subsequent Epic, so this rewrite runs again on every pass after the first. On those passes it is a **two-field refresh, not a fresh run-start write**: `Read` the current manifest first and write back its **Progress**, **Next unit**, **Isolation strategy**, **Pre-Bee SHA**, **Compromise tracker**, and already-captured **Multi-Epic run mode** unchanged, touching only the two fields named above (and in practice only `Epics in scope`, since the mode is already captured by then). Re-emitting Section 1's blank template here would blank the per-Epic **Progress** and **Next unit** that Section 4.2's Epic-boundary checkpoint recorded — destroying the `last commit <sha>` values that checkpoint's own step 1 reads back as its lower bound at the *next* Epic boundary.

The manifest is where this run reads the mode and the scope back after a compaction, not the conversation — a manifest still reading `pending Section 2 query` tells a post-compaction reader nothing about what this run is working on.

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

1. **Read state.** Pull the current truth from four sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <epic-id>` to get the Epic's `children` array (Task IDs); for each Task, fetch its full details including its own `children` array (Subtasks); read every Subtask body, since these carry the detailed instructions (Context, What Needs to Change, Key Files, Acceptance Criteria) the dispatched Agent will follow. Sort Tasks in dependency order (check each Task's `up_dependencies`). Verify at least one Task exists with at least one Subtask and all are non-drafted (`status!=drafted`). Use the canonical freeform-query recipe (`bees execute-freeform-query --query-yaml '<yaml>'`) for any focused state query, e.g.:

     ```bash
     bees execute-freeform-query --query-yaml 'stages:
       - [id=<ticket-id>]
     report: [title, ticket_status]'
     ```
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done).
   - **git state** — the actual diff on disk. Workers communicate by editing files; the diff is the only authoritative record of what they actually did.
   - **the run-state manifest** — the on-disk file defined in Section 1 `#### Write the run-state manifest`, holding the run-scoped values that have no other durable home (multi-Epic run mode, isolation strategy, `<pre-bee-sha>`, compromise-tracker path, per-Epic progress, next unit). `Read` it at `<tempdir>/.quorum/run-state-quo-execute-<bee-id>.md`; the path is derived from this skill's name plus the Bee ID, so it stays findable even when nothing about it survives in the conversation.

   **Conversation memory is never a substitute for these four sources.** Whatever the orchestrator believes it remembers about ticket status, landed commits, the captured run mode, or the pre-run SHA, the four sources above are the truth and are re-read rather than recalled. This is unconditional — it holds on every tick, not only after something goes wrong. On top of it, one conditional rule for the observable case: **if a summarization marker is visible in the conversation** (the harness compacted mid-run), treat everything before it as non-authoritative and re-read all four sources in full before dispatching anything else.

   Mark the current Task `status=in_progress` and the Bee `status=in_progress` (if not already set) the first time a Task starts.

2. **Reconcile.** Compare current state to target state and act:
   - For every Subtask whose dependencies are satisfied and which has no Agent already in flight for it, dispatch a fresh Agent (see "Per-Subtask cold dispatch" below).
   - For every Agent that has reported completion, persist the result: confirm the bees ticket transitioned to `status=done`, mark the corresponding TaskList task `completed`, and unlock any newly-eligible downstream Subtask. **A Test Writer or Doc Writer return that reports it *stopped* on detected source movement is not a completion** — route it through the movement-report rung below instead: it unlocks nothing. That rung does close out the writer's own TaskList task (the Agent has exited), but it opens an `aborted-*` task in its place, and the Task does not advance while that task is `pending`.
   - **Movement report from a Test Writer or Doc Writer.** `agents/test-writer.md` and `agents/doc-writer.md` both instruct the writer to **stop mid-run and report** when the source its work was pinned to moved underneath it (the Test Writer detects this with a `git rev-parse HEAD` + `git hash-object` fingerprint taken at start and again before finishing; the Doc Writer, which has no `Bash`, re-reads with `Read` / `Grep`). That report is a distinct return shape and this rung is its receiver — without one, the orchestrator marks the task `completed` and unlocks a per-Task PM review over tests or docs the writer never finished writing.

     **Recognising it, and the execute-mode narrowing.** Read the writer's return before persisting anything. Both role files scope the obligation per mode: in execute mode, movement confined to a **sibling Subtask's** own files is the designed concurrency of this skill's dependency-ordered fan-out, and the writer is told to record it as an *observation* and finish normally. That is a completed return — persist it as one and carry the observation into the Task summary. A **movement report** is the other case: the writer stopped, because the files **its own** Subtask pins moved. What distinguishes the two is whether the writer stopped, not whether it mentioned movement.

     **What to do.** Do **NOT** unlock anything downstream of that lane — it has not delivered. Record the owed redelivery as a durable TaskList entry instead, the same obligation-as-pending-task pattern `defer-*` and `gate-*` already use:

     1. **Mark the writer's own TaskList task `completed`** — `test-writer-<subtask-id>` / `doc-writer-<subtask-id>` (or the Bee-scoped `<role>-<bee-id>` form when the aborted lane was a Section 5 re-dispatch), including any `-r<n>` suffix it carries. Its Agent **has** exited, so leaving it active would strand a task no completion notification will ever clear.
     2. **Create a new `aborted-<role>-<id>` TaskList task** — `aborted-test-writer-<subtask-id>` / `aborted-doc-writer-<subtask-id>`, or `aborted-<role>-<bee-id>` when the aborted lane was Bee-scoped, matching the scope of the lane that aborted (per the naming convention below) — with status `pending` and the writer's "how far I got" report as its `metadata.activity` string. That pending task **is** the redelivery-owed marker: the orchestrator reads it off the TaskList on the next tick rather than holding it in conversation, so it survives a compaction. What routing tests is the task's **name prefix and status**; the `metadata.activity` string is informational context for the re-dispatch prompt, consistent with `metadata.activity` never being a routing input.
     3. **The Task must not advance while any `aborted-*` task for it is `pending`.** The "all Subtasks `done`" test below is what advances the Task to its per-Task PM review; an aborted lane must not satisfy it. So the aborted lane's bees Subtask must not reach `status=done` either — if the writer set it, or the orchestrator was about to flip it on the writer's behalf per `agents/doc-writer.md`'s no-`Bash` routing, that flip is premature. When the flip already landed, undo it with one literal command before proceeding:

        ```bash
        # POSIX (bash / zsh):
        bees update-ticket --ids <subtask-id> --status in_progress
        ```

        ```powershell
        # Windows (PowerShell):
        bees update-ticket --ids <subtask-id> --status in_progress
        ```

        `agents/test-writer.md` orders its closing movement-fingerprint reading **before** the `done` flip and forbids the flip on an abort, so this correction should be rare — run it when the state says otherwise, do not assume it.

        **Bee-scoped case — the bees corrective is a no-op.** When the aborted lane was a **Section 5 Bee-scoped re-dispatch** (`test-writer-<bee-id>` / `doc-writer-<bee-id>`), there is no Subtask behind it to un-flip: those re-dispatches answer a Bee-level finding that spans the whole Bee's diff and carry no `t3` ticket of their own (per the naming convention below). So skip this bees step entirely on that path — do **not** hunt for a Subtask to demote, and do **not** demote a Task or Epic the Bee-level diff happens to touch, which would reopen work that is legitimately `done`. What the Bee-scoped `aborted-<role>-<bee-id>` marker holds shut is Section 5's Bee-level review loop closing, and that gate is TaskList-derived, so the marker by itself is the whole mechanism.

     Then re-dispatch the lane, per who moved the source:

     - **When the mover was an Engineer** — a re-dispatch round routed from a review site, or a forward Subtask dispatch that turned out to share files with the writer's Subtask: the source must reach a settled state **first**. Let that Engineer's own lane finish and, when the movement came from a review-finding re-dispatch, let the code review round for that site close per part (g)'s ordering — the **Bee-level Code Reviewer** when the finding came from Section 5's site (Clause 2), the **per-Task PM's in-flight `/quo-engineer-review` pass** when it came from the per-Task site (Clause 1); only then re-dispatch the writer. Re-dispatching into a still-moving diff reproduces the abort. The `aborted-*` task holds the Task's advance shut throughout, and does not block that Engineer round: it is a different name class from the prefixes part (g)'s two clauses enumerate.
     - **When the mover was a concurrently-dispatched Test Writer's discrimination experiment** — the second **attributable** in-workflow mover, and one that is easy to misread as an external edit. The candidate set is **any concurrently-dispatched Test Writer** — a **sibling Subtask's**, or the Bee-scoped `test-writer-<bee-id>` when the aborted lane is a Section 5 re-dispatch (Section 5 can re-dispatch `test-writer-<bee-id>` and `doc-writer-<bee-id>` concurrently). `agents/test-writer.md` sanctions perturbing a source file **in place** with `Edit` / `Write` (restoring afterwards from a scratch copy) to confirm a test really fails without the fix, and requires that Test Writer's return to list every perturbed path under a `## Perturbations` heading, `None` when there were none. Read that heading on the Test Writer returns you hold: when one lists **every** path the aborted writer reported as moved, the movement is attributed — self-inflicted by the workflow and already restored — so **re-dispatch the aborted lane once that sibling has returned, with no gate**; when it covers only **some** of them, fall through to the external-actor case below for the remainder. **When a concurrently-dispatched Test Writer has not returned yet, do not classify and do not fire the gate**: it is a live dispatch that *will* notify, so wait for its completion notification, read its `## Perturbations` heading on that tick, and classify then. This case fails to apply once every concurrently-dispatched Test Writer has returned and none of them lists the moved path — then fall through to the external-actor case below.
     - **When the mover was an external actor** (the user, a second session, a background process — nothing this orchestrator dispatched): re-dispatch the writer once the movement is understood, i.e. once the orchestrator has read the current diff and can see the tree has settled. When the movement is **unexplained**, fire the **unexplained-movement gate** below instead of re-dispatching into it.

     The re-dispatch is a repeat dispatch of an already-named role, so it takes the next `-r<n>` round-discriminated TaskList name per the naming convention below. Carry the writer's "how far I got" report — the `metadata.activity` string on the `aborted-*` task — into the re-dispatch prompt so the fresh Agent does not start from zero. **When the re-dispatched lane returns a normal deliverable, mark the `aborted-*` task `completed`** — that is what releases the Task's advance. If the re-dispatched lane aborts on movement again, repeat this rung from the top: mark its own `-r<n>` task `completed` and refresh the **existing** `aborted-*` task's `metadata.activity` with the newer report rather than creating a second one — it is the same obligation, still owed.

     **Unexplained-movement gate.** The movement is unexplained when the orchestrator dispatched **no** Engineer whose files overlap the writer's Subtask over the window the writer reports, **no returned concurrently-dispatched Test Writer's `## Perturbations` list covers the moved paths** — the same candidate set the case above names, a sibling Subtask's Test Writer or the Bee-scoped `test-writer-<bee-id>` — with the remainder still uncovered when one list covers only some of them, and none of that set still in flight, and it cannot otherwise account for who changed the source or whether more is coming. Do not re-dispatch blindly — a blind re-dispatch loop is the failure mode this branch exists to prevent. Fire this gate through the two-step `TaskCreate` → `AskUserQuestion` contract: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this unexplained-movement gate (per the TaskList naming convention below), **then** call `AskUserQuestion` in the same turn. Do not produce a text response describing the gate — fire the two calls. The yield-control discipline applies: do not yield to the harness while the `gate-*` task is `pending` or `in_progress`.

     The question text carries the writer's movement report **verbatim** — which files moved, the opening and closing HEAD when HEAD moved, and how far the writer's work got — plus this one-line statement: *the orchestrator dispatched no Engineer for this unit while the writer was running, and no returned concurrently-dispatched Test Writer's `## Perturbations` list names the moved paths, so it cannot attribute the movement.* Offer exactly these three options. The gate is multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot:

     - **Re-dispatch the writer now** — the movement is understood or accepted. Re-dispatch the lane under its next `-r<n>` name against the current tree, per the paragraph above.
     - **Wait** — the operator resolves the external change first. The orchestrator yields control and re-fires this gate **only on the operator's reply** — that reply is the trigger, and it is the only one. Do **not** read this as "no Agent is in flight": execute mode's forward fan-out dispatches every dependency-satisfied Subtask concurrently, so a sibling Subtask's Engineer, Test Writer, or Doc Writer can return its completion notification seconds after the operator picked Wait. **A sibling lane's completion notification is a tick that processes that lane normally** through the Reconcile step above — persist its result, mark its task `completed`, unlock what it unlocks — and it **MUST NOT** re-fire this gate. The rule is derivable from the tick's trigger and needs no bookkeeping: re-fire on the operator's reply, never on an Agent notification. (Do not record the Wait state in `metadata.activity` and route on it — that string is informational and is never a routing input.) The `aborted-*` task stays `pending`, so the Task's advance stays shut across the wait.
     - **Abort this unit** — leave every bees ticket at the status the abort found it at and do not advance. For a Subtask-scoped writer lane that means the writer's Subtask and its parent Task; for a Section 5 Bee-scoped lane there is no Subtask or Task to hold back — every one of them is legitimately `done`, and what stops is the Bee-level review. Do **not** simply stop here: route the exit through Section 4.2's **`##### Aborted-run close-out`**, which sweeps the per-Task and (where the aborted lane was Bee-scoped) Bee-level TaskList names — including the `aborted-*` marker this rung just created — runs the **Epic-boundary state-externalization checkpoint** on its aborted path, and stops the run naming the literal resume command `/quo-execute <bee-id>`.

     Mark the `gate-*` task `completed` the moment the answer is consumed and the chosen branch is entered — including on **Wait**, where consuming the answer means yielding; the re-fire on the next tick creates a **fresh** `gate-askuserquestion-<short-suffix>` task rather than reusing the closed one.
   - When all Subtasks of the current Task are `done` **and no `aborted-*` TaskList task for this Task is `pending`**, advance to the per-Task PM review by dispatching a fresh PM Agent (see "Per-Task PM dispatch" below). The second conjunct is the aborted-lane guard from the movement-report rung above; match on the `aborted-` name prefix plus the status.
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

The original SDD intent was warm Agents that would receive `SendMessage` pings between Subtasks, amortizing context-load cost across a Task. That path requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents) — and this skill set does not use that substrate at all, so `SendMessage`-based warm dispatch is not available. The trade-off is conscious: each cold-dispatched Agent re-loads its role file and any referenced docs, which is more tokens than a warm ping, but the architectural simplification (no team lifecycle, no shutdown choreography, no peer-to-peer coupling) is worth it; in practice prompt caching mitigates most of the cold-load cost. The divergence from the SDD's warm-Agent intent is intentional and is tracked by a re-probe issue in this skill set's own backlog ("Re-probe SendMessage-without-Agent-Teams as warm-Agent token-cost optimization") plus a divergence note recorded in the SDD; revisit if the upstream constraint changes.

##### Dispatch prompt: quote the ticket body verbatim

The dispatch prompt sent to each Agent must embed the ticket body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names) that the worker will then use literally. Read the ticket via `bees show-ticket --ids <ticket-id>` and embed the returned body in the prompt as a quoted block. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "your gating precondition is met — start now") is fine; the body itself stays untouched. The orchestrator's own progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

**Test Writer dispatch — supply the fingerprint path list.** `agents/test-writer.md`'s movement fingerprint hashes a set of non-test source paths, and the orchestrator already knows that set — **not by re-deriving it from the tree, but by carrying forward the changed-file list the Engineer's own return supplied.** `agents/engineer.md` requires every Engineer return to carry a `## Files changed` list. Supply it under a labelled `## Source paths to fingerprint` heading, one path per line, repository-relative, with test paths dropped. Scope the list to the lane being dispatched:

- **Subtask-scoped Test Writer** — a test Subtask carries one role of its own and therefore has no Engineer diff of its own, so this list is **resolved, never assumed**. **The primary rule is the parent Task's union.** Run `bees show-ticket --ids <subtask-id>` and read its `parent` to get the Task; run `bees show-ticket --ids <task-id>` and read its `children` to get that Task's Subtasks; the list is the **union of the `## Files changed` lists from the Engineer returns for that Task's implementation Subtasks**. **Then narrow that union to just the `up_dependencies`-named implementation Subtasks when — and only when — the test Subtask's own `up_dependencies` is non-empty**, which is the more precise scoping whenever the breakdown supplied it. An **empty `up_dependencies` on a test Subtask is legal** and must not be read as "no implementation Subtask to resolve": the unnarrowed parent-Task union is the answer in that case, not an empty list and not the working-tree fallback below. Implementation Subtasks under *other* Tasks are the designed sibling concurrency and stay out of the list either way. **A limitation worth naming rather than papering over:** what actually supplies the paths is **possession of an Engineer return** — the `children` read only scopes the union to this one Task — so the union covers only the Engineer returns the orchestrator holds **at dispatch time**. A same-Task implementation Subtask still in flight contributes nothing, and any movement it lands afterwards falls outside the writer's fingerprint set, so the writer will not report it even though the movement rung above names "a forward Subtask dispatch that turned out to share files with the writer's Subtask" as a mover. Paths that entered the union from a **same-Task sibling** implementation Subtask are supplied so the writer knows the full set its own Subtask pins, and movement in them is anomalous to the writer exactly as movement in any other supplied path is — `agents/test-writer.md`'s execute-mode stop rule applies, so treat a stop-report naming one of them as legitimate rather than dismissing it as sibling concurrency; the union rule above is unchanged.
- **Bee-scoped Test Writer** re-dispatched from Section 5 — the union of the changed-file lists from every Engineer return behind the Bee-level diff the finding came from, including the Bee-scoped `engineer-<bee-id>` rounds Section 5 itself dispatched.

**Fallback when an Engineer return did not list files.** Derive the set with one literal command and drop the test paths from the result:

```bash
# POSIX (bash / zsh):
git diff --name-only HEAD
```

```powershell
# Windows (PowerShell):
git diff --name-only HEAD
```

**This derivation is the last resort, and its trigger is narrow:** it applies only when the scope being dispatched yields **no usable Engineer-supplied list at all** — either no Engineer return exists for that scope (no implementation Subtask under the parent Task produced one, at Subtask scope; no Engineer ran behind the Bee-level diff, at Bee scope), or every return that does exist omitted its `## Files changed` heading. It does **not** apply merely because the `up_dependencies` narrowing selected nothing; that case is already answered by the parent-Task union above. And when only *some* of the returns in scope carried a list, union those and do **not** fall back — a partial return-carried list beats the whole working tree. **An explicitly-empty `## Files changed` list is a list, not a missing one:** a research-only Engineer pass that changed nothing contributes nothing to the union and does **not** trigger this fallback either. In execute mode this fallback is materially worse than in a serialized flow: it reads the **whole working tree**, so it can include a sibling Subtask's concurrent edits — movement that is expected concurrency rather than a fault, but which the writer, seeing those paths in its fingerprint set, may stop on. **Omit the `## Source paths to fingerprint` heading rather than emitting an empty one in either of the two ways the set can come out empty:** when no usable Engineer-supplied list exists for that scope **and** this derivation also produces nothing outside the writer's own test files, and when every return in scope carried a list but the union across them is empty (so the fallback never fires). `agents/test-writer.md`'s empty-path-set clause keys on the heading being *absent* — it carries the fallback derivation and the empty-set handling for that case — so an empty heading would read to the writer as a supplied set rather than as none.

**Test Writer / Doc Writer dispatch — state the orchestrator-side rule, never a freeze guarantee.** The writer dispatch prompts MAY state the rule the orchestrator actually controls, scoped to the lane being dispatched: for a **Subtask-scoped** writer, **"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running"** — an Engineer working a *sibling* Subtask may legitimately be running concurrently, so the promise cannot be widened past that Subtask; for a **Bee-scoped** writer re-dispatched from Section 5, **"no Engineer Agent will be dispatched for this Bee while you are running"**, which holds because every Subtask is finished by then. Both are decisions about the orchestrator's own dispatches, so both are claims the orchestrator can keep. Keep the scoping qualifier: `agents/test-writer.md` and `agents/doc-writer.md` scope the guarantee per mode, and these are the execute-mode wordings their execute-mode branch expects. The prompts **MUST NOT** claim that **"the source tree is frozen"**, or any close paraphrase promising the files will not move. The orchestrator cannot prevent the user, a second session, or a background process from editing the tree, so that phrasing promises a lever the orchestrator does not hold — an unkeepable guarantee, not a dispatch instruction. `agents/test-writer.md` and `agents/doc-writer.md` carry the writer-side half (capture the tree's state at start, re-check before finishing, stop and report movement outside the writer's own lane — with sibling-Subtask movement treated as expected concurrency in this mode), so the writer's recovery path does not depend on the dispatch prompt getting the wording right.

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

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every Agent invocation originates from this skill's reconciliation loop, never from a worker.

Flat orchestration means the orchestrator's working context grows **monotonically within a session** — every Subtask dispatch, every PM review, and every reconciliation tick adds to the loop's running set — and **nothing in this skill reclaims those tokens.** Token reclamation is owned by the harness, which compacts the conversation on its own once the window fills; the skill has no model-invocable way to clear or compact its own context. What the skill does guarantee is that the growth is **survivable**: Section 4.2's **Epic-boundary state-externalization checkpoint** keeps every load-bearing fact in a durable carrier the orchestrator can re-read, so whenever the harness compacts — at an Epic boundary or in the middle of one — the run can be re-derived rather than reconstructed from memory. The actual reclamation lever is starting a **fresh session** at an Epic boundary, which Section 4.2 branch 1 recommends when the loop exits for breakdown work; the checkpoint is what makes that lever safe to pull at any point.

#### Roles dispatched by the orchestrator

The orchestrator dispatches the following four roles during a Task. The full role contracts (responsibilities, gating preconditions, instructions, shell-command etiquette) live in the role files; the orchestrator's job is to invoke the right role at the right time, not to carry the role's prose.

- **Engineer** (`agents/engineer.md`) — implements source-code Subtasks. Model: Opus (always). Does not write tests or docs.
- **Test Writer** (`agents/test-writer.md`) — implements test Subtasks and reviews the Engineer's diff for missing test coverage. Model: Opus (always).
- **Doc Writer** (`agents/doc-writer.md`) — implements documentation Subtasks, reviews the Engineer's diff for documentation gaps, and after the Engineer's diff has landed appends or updates a `### Feature: <title>` subsection in the project's cumulative PRD and SDD per the categorization heuristic (pure-refactor / architecture-only / deployment-CI / user-facing) defined in `agents/doc-writer.md` `## Cumulative project doc updates`. The `<title>` is the verbatim title of the Plan Bee at the top of the Subtask → Task → Epic → Plan Bee chain; the orchestrator surfaces it to the subagent in the dispatch context. See `agents/doc-writer.md` for the authoritative spec — including the categorization table, the `<title>` resolution rule, the idempotency rule, and the CLAUDE.md `## Documentation Locations` lookup-key recipe used to resolve the PRD and SDD paths. Model: Opus (always).
- **Product Manager** (`agents/pm.md`) — reviews the Task's work against the spec source resolved from the Bee's `reference_materials` (PRD/SDD files on disk via the `file-path` resolver, or the PRD/SDD `t1=Doc` children of a Spec Bee via the `bees` resolver), or the Bee body itself when `reference_materials` is null/empty; drives `quo-engineer-review` and `quo-doc-writer-review` per Task; and produces the per-Task summary report. See `agents/pm.md` `### Resolving reference_materials entries` for the authoritative resolver-branching logic — this dispatch prompt does not duplicate it. Model: Opus (always).

Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) are introduced in Section 5 (final Bee-level reviews).

##### Per-Task PM dispatch

When all child Subtasks of the current Task are `status=done` **and no `aborted-*` TaskList task for this Task is `pending`** (the aborted-lane guard from Section 3's Reconcile-step movement-report rung), dispatch a fresh PM Agent to do the per-Task review and produce the Task summary. The dispatch prompt must include the Task ID, the list of completed Subtask IDs, `<scoped-marker-resolver-path>` — a placeholder the orchestrator fills in at runtime so `agents/pm.md` can perform its Scoped-marker check (see "Scoped-marker PM dispatch wiring" below) — and `<compromise-tracker-path>`, this run's compromise-tracker path (the same value Section 6 passes to the post-completion reviewer). **Pass the tracker path, not its contents**, exactly as Section 6 does; `agents/pm.md` reads the file itself and carries the deferred-blocker check that path enables. The Bee-scoped PM re-dispatches in Section 5 carry the same two placeholders.

**Relay the Engineer's completeness evidence into the PM dispatch prompt.** `agents/engineer.md` requires an Engineer's return to carry a **completeness check with evidence** whenever its Subtask directed a change at *every site* where some property holds (the search patterns run, every hit, and per hit either the change made or the reason it is deliberately untouched). That evidence has no other carrier — the Engineer Agent has exited and its return lives only in this conversation — and the PM is `/quo-engineer-review`'s caller on this lane (it drives the review in flight via the `Skill` tool per `agents/pm.md`). So **when any Engineer return for this Task carried a completeness list, the per-Task PM dispatch prompt MUST embed that list verbatim** under a clearly labelled heading; the recommended label is `## Engineer's completeness evidence`. Embed it as text in the prompt — do **not** write it to a scratch file and pass a path. Say which Subtask each list came from when more than one Engineer contributed. **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was** — that is a fact about the assignment that was dispatched (a directive or Subtask body that directed a change at *every site* where some property holds), known independently of whether a list came back. `/quo-engineer-review`'s sweep-verification check only reports a *missing* list as a finding when the invocation itself named the assignment that way, so an unnamed sweep silently loses the check — and the case that most needs the check is precisely a sweep-shaped assignment whose Engineer returned no list. `agents/pm.md` carries the PM-side half (pass the list through into its `/quo-engineer-review` invocation). When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one — but still state that the assignment was sweep-shaped when it was, so `/quo-engineer-review`'s missing-list check stays reachable.

#### TaskList as progress UI

The orchestrator uses Claude Code's native **TaskList** as the visible progress UI for the run. There is no separate display backend to configure — TaskList renders in the harness automatically, replacing the team-display surface a prior message-bus substrate would have required.

For every Agent the orchestrator dispatches, it creates exactly **one** TaskList task:

- **`pending`** — created when the orchestrator decides this Subtask is next but before the Agent invocation lands.
- **`in_progress`** — set the moment the Agent invocation is dispatched (`Agent(...)` returns).
- **`completed`** — set when the orchestrator processes the Agent's completion notification and confirms the bees ticket transitioned to `status=done`. **One exception:** a writer lane that returned a movement report has its task set `completed` **without** a `status=done` — the Agent exited, which is what this status tracks, while the delivery obligation moves to an `aborted-*` task (see Section 3's Reconcile-step movement-report rung). `completed` on an Agent task means "this Agent is gone", not "this work shipped".

Use `metadata.activity` on the TaskList task to surface finer-grained progress when a worker emits intermediate signal (e.g., `"running narrow tests on package X"`, `"resolving Scoped-marker for grandparent bee"`). The orchestrator updates this string opportunistically; it is informational, not a routing input.

##### TaskList naming convention

The naming convention is the **canonical cross-reference** for downstream Tasks (later Sections of this SKILL.md and other skills in the workflow consume these names). It is deterministic so two concurrent invocations cannot collide and unambiguous so any reader can map a TaskList entry back to its bee ticket:

- **Implementer Agents** (Engineer, Test Writer, Doc Writer) — **Subtask scope** on the forward path. Name: `<role>-<subtask-id>` (e.g., `engineer-t3.abc.def.gh`, `test-writer-t3.abc.def.ij`, `doc-writer-t3.abc.def.kl`). Each Subtask gets its own implementer Agent and its own TaskList task; subtask-id makes the name unique even when sibling Subtasks of the same Task run concurrently.
- **Bee-level implementer Agents** (Engineer, Test Writer, Doc Writer re-dispatched from Section 5's Bee-level review) — **Bee scope**. Name: `<role>-<bee-id>` (e.g., `engineer-b.abc`, `test-writer-b.abc`, `doc-writer-b.abc`). Section 5's findings span the whole Bee's diff and are not attributable to one Subtask, so these re-dispatches take the Bee id as their scope suffix rather than borrowing a Subtask's. The Subtask-scoped and Bee-scoped forms coexist without overlap — a Subtask id and a Bee id are distinct token shapes.
- **PM Agents** — **Task scope** on the forward path. Name: `pm-<task-id>` (e.g., `pm-t2.abc.def.gh`). The PM reviews the whole Task at once, so its scope suffix is the parent Task's id. A PM re-dispatched from Section 5's Bee-level review takes the **Bee-scoped** form `pm-<bee-id>` (e.g., `pm-b.abc`), for the same reason as the Bee-level implementers above.
- **Reviewer Agents** (Code Reviewer, Test Reviewer, Doc Reviewer — see Section 5) — **Bee scope**. Name: `<reviewer>-<bee-id>` (e.g., `code-reviewer-b.abc`, `test-reviewer-b.abc`, `doc-reviewer-b.abc`). Reviewers run once per Bee at the final Bee-level review, so the scope suffix is the Bee id.
- **Round discriminator for every repeat dispatch of an already-named role.** The "exactly one TaskList task per Agent" rule above holds, so a role dispatched a second time against the same scope cannot reuse its first task's name. **Every dispatch after the first appends `-r<n>`, where `<n>` is the 1-based re-dispatch count for that role at that scope** — `engineer-b.abc` for the first Bee-level Engineer, `engineer-b.abc-r1` for the second, `engineer-b.abc-r2` for the third, and likewise `code-reviewer-b.abc-r1` for a second Bee-level code review, `doc-writer-t3.abc.def.kl-r1` for a re-dispatched Subtask-scoped Doc Writer, `pm-t2.abc.def.gh-r1` for a re-dispatched per-Task PM. This is the same form `/quo-fix-issue`'s issue-scoped naming convention uses (`engineer-<issue-id>-r<n>`); the two skills' forms are identical so a reader moving between them reads one convention, not two. Because the discriminator is a **suffix**, every rule that tests these names — most importantly the Engineer-dispatch preconditions in part (g) of `### Orchestrator discipline: routing review findings` — matches on the name **prefix** plus status, so discriminated names are caught alongside undiscriminated ones.
- **Post-completion follow-up Agents** (Engineer, Test Writer, Doc Writer dispatched by Section 6 step 6's `Fix in this session` branch) — **post-completion scope**. Name: `<role>-postcomp-<n>`, where `<n>` is the 1-based index of the finding being addressed in the post-completion reviewer's numbered list (e.g., `engineer-postcomp-1`, `doc-writer-postcomp-2`). These follow-ups answer a finding of a whole-Bee sweep and belong to no single Subtask, Task, or review round, so they take **no ticket-id suffix**, and normally no round discriminator either — the per-finding index **is** the discriminator, and two findings needing the same role dispatch under distinct `<n>`. **One carve-out: a round discriminator IS permitted, and required, when a post-completion writer lane is re-dispatched after a movement abort** (Section 6 step 6's carry-over of Section 3's movement-report rung). That re-dispatch is a *second* Agent answering the *same* finding, so the "exactly one TaskList task per Agent" rule needs a fresh name and the finding index alone cannot supply one: append `-r<k>`, where `<k>` is the 1-based re-dispatch count for that role at that finding index — `test-writer-postcomp-2-r1` for the first re-dispatch of the Test Writer lane on finding 2. Outside that case, do not append a round discriminator to a post-completion name. Section 6 step 6 is authoritative for their dispatch ordering, their Engineer-dispatch freeze precondition, and their close-out. This is the same form `/quo-fix-issue`'s Section 8 step 6 uses.
- **Aborted-writer redelivery markers** — **scope of the lane that aborted**. Name: `aborted-<role>-<subtask-id>` for a Subtask-scoped writer lane (e.g., `aborted-test-writer-t3.abc.def.ij`), `aborted-<role>-<bee-id>` for a Bee-scoped one (e.g., `aborted-doc-writer-b.abc`), and `aborted-<role>-postcomp-<n>` for a Section 6 post-completion lane — where `<n>` is **the same finding index as the lane it marks**, so the marker reads back to its finding. Created by Section 3's Reconcile-step **movement-report rung** when a Test Writer or Doc Writer stops mid-run on detected source movement: the writer's own task is marked `completed` (its Agent has exited) and this task is created `pending` in its place, with the writer's "how far I got" report as its `metadata.activity` string. **This is not an Agent task** — no Agent is behind it, so the "exactly one TaskList task per Agent" rule and the `-r<n>` round discriminator do not apply to it; a lane that aborts a second time refreshes this task's `metadata.activity` rather than opening another. It is an **obligation marker**, the same pattern `defer-*` and `gate-*` use: while it is `pending`, the unit it names does not advance — a Subtask-scoped marker holds its parent Task's advance to the per-Task PM review, and a Bee-scoped marker holds Section 5's Bee-level review loop from closing. Marked `completed` when the re-dispatched lane returns a normal deliverable — that lane is `<role>-<subtask-id>-r<n>` / `<role>-<bee-id>-r<n>` for a ticket-scoped marker, and `<role>-postcomp-<n>-r<k>` for a post-completion one, per the round-discriminator carve-out in the post-completion entry above. The `aborted-` prefix is a distinct name class from `<role>-<subtask-id>` / `<role>-<bee-id>`, which is what keeps these markers out of part (g)'s two Engineer-dispatch clauses without needing an exemption clause there.
- **Deferral-ledger tasks** — **Run scope**. Name: `defer-<short-suffix>` (e.g., `defer-1`, `defer-2`, or any collision-resistant suffix). Created when an agent's structured return (per `agents/pm.md`'s Final report contract or `agents/analyst.md`'s `### Deferred refinements` block) names a destination the orchestrator chose not to address inline this run — `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. `metadata.activity` carries the deferral's one-line description so the gate prose (Section 6.5 below) can surface the active set. Marked `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (in which case `metadata.activity` logs the resolution path). The pre-handoff Section 6.5 gate reads this ledger for active `defer-*` entries and refuses to yield control while any remain pending or in-progress.
- **Gate-task tasks** — **Turn scope**. Name: `gate-<kind>-<short-suffix>` (today the dominant `<kind>` is `askuserquestion`, e.g. `gate-askuserquestion-1` for an `AskUserQuestion` gate fired during Section 5's review loop, Section 6's post-completion findings gate, or Section 6.5's deferral-hygiene gate). Created by the orchestrator via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract. The `<short-suffix>` MUST be unique per fire within the same run across every `gate-*` task regardless of `<kind>` — use one of the two acceptable patterns (monotonic integers or gate-specific slugs encoding context). The two-step contract applies at every gate this skill fires — both the trailer-driven gates surfaced by the review skills (Section 5's review-loop's escalation gates when the orchestrator escalates a contested finding to the user) and the trailer-less orchestrator-driven gates (Section 1's conditional session-effort gate — fires only when the session is below the floor, see Section 1's `Check session reasoning effort` sub-step — Section 3's Reconcile-step **unexplained-movement gate** in the movement-report rung, Section 4.2's continue-or-stop multi-Epic gate when Mode 1 is selected, Section 6's post-completion findings gate, Section 6.5's deferral-hygiene gate, Section 7's Acceptance-Criteria sign-off and Bee close-out gates). `metadata.activity` carries the gate's finite choices verbatim where applicable. Marked `completed` the moment the prescribed tool call returns and its result has been consumed (the user's answer routed, the next branch entered, etc.). Normally enters and exits within a single turn — the lifecycle is shorter than `defer-*` (which spans the whole run). The **yield-control discipline** mirrors `defer-*`: this skill MUST NOT yield control to the harness while any `gate-*` task is in `pending` or `in_progress` status. If a `gate-*` task is somehow left active when the orchestrator would yield (e.g., a bug fired the prescribed tool call without the paired `TaskCreate`, or the orchestrator hit an error between the two), the next reconciliation tick walks the TaskList, surfaces the active `gate-*` task, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<subtask-id>`, `pm-<task-id>`, the Bee-scoped implementer and PM names (`<role>-<bee-id>`, `pm-<bee-id>`), the Bee-scoped reviewer names (`code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`), the post-completion follow-up names (`<role>-postcomp-<n>`), and the aborted-writer markers (`aborted-<role>-<subtask-id>` / `aborted-<role>-<bee-id>` / `aborted-<role>-postcomp-<n>`) — with or without an `-r<n>` round discriminator.

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
   3. Stage files that are related to this Task — include agent-reported files, formatting changes to files that were touched by this Task's agents, and (only if the Plans hive lives inside this repo) the resolved Plans hive path's contents. To learn the in-repo Plans hive path, run the bundled helper's NON-MUTATING `resolve-hive-paths` mode (the same `hive_commit.py` helper this skill calls at its Section 6.5 Encode step — resolve its path the same way). The helper emits the Plans hive's absolute path when it lives inside this repo, or nothing when it lives outside (in which case you stage no hive path here). Run it as a single literal Bash call:

      ```bash
      # POSIX (bash / zsh):
      python3 "<this skill's base directory>/scripts/hive_commit.py" resolve-hive-paths --hive plans
      ```

      ```powershell
      # Windows (PowerShell):
      python "<this skill's base directory>\scripts\hive_commit.py" resolve-hive-paths --hive plans
      ```

      `git add` the emitted Plans hive path (if any) alongside your judgement-selected source files. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this Task.
   4. Commit with a descriptive message per system/project git guidance. Prefix the subject with the enclosing parent chain — the Plan Bee by its bare ID and the Epic by its ordinal — then the Task's human label, and append the bare Task ID once in trailing parentheses: `Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)` — e.g. `Plan b.bc7, Epic 1, Task 7 — Document the new auth config surface (t2.rwx.fy.qq)`. You already hold the enclosing Plan Bee ID and Epic ordinal from the run's top-level invocation and the Task's parent chain (Task → Epic → Bee); the `Epic N` / `Task M` ordinals come from the ticket titles. If the Epic has no parent Plan Bee (a standalone Epic), omit the `Plan <bee-id>, ` prefix and lead with `Epic N, Task M — …`.
3. Mark the per-Task TaskList tasks (named per the convention established in Section 3 — see "TaskList naming convention") as `completed` and clear them from the active set. **Sweep by name prefix, not by exact name**, so a lane re-dispatched under the `-r<n>` round discriminator (`doc-writer-<subtask-id>-r1`, `pm-<task-id>-r1`, …) is closed out alongside its first round rather than left behind. **The sweep includes any `aborted-<role>-<subtask-id>` redelivery markers** the movement-report rung opened for this Task's Subtasks: reaching this step means the redelivery landed (the Task could not have advanced otherwise), and a marker left `pending` past close-out would hold a later advance shut. There is no Agent shutdown to perform — the per-Subtask cold dispatches established in Section 3 already complete-and-exit when each Agent returns. **The aborted path runs this same sweep at its own site:** a Task that never advances — because a lane aborted, or because a routing-gate `Cancel` ended the run at a review of it — does not reach this step, so Section 4.2's `##### Aborted-run close-out` performs the identical prefix sweep at that boundary — keep the two in step.
4. Output the summary below to the screen and advance to the next Task by dispatching fresh ephemeral implementer Agents per the dispatch shape in Section 3.

```
## Task [N] of [total] Complete: [task-title]

**Task ID**: <task-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Ignored Review Feedback**: [list items that were flagged by quo-engineer-review or quo-doc-writer-review but Director chose not to address, or "None"]
**Second-order effects**: [the relayed `### Second-order effects` narrative — rendered per the "Second-order effects" logic below]
**Follow-up Tasks Created**: [count, if any] [list task-ids if created]
One of:
- Proceeding to next Task: [next-task-title]
- Final Task, moving on to Final Reviews 
```

**Second-order effects (rendered into the summary block above).** This field is the **destination** for the narrative `/quo-engineer-review` emits under its `### Second-order effects` heading on every review, as relayed by the **per-Task** PM — the relay chain that carries it here is `/quo-engineer-review` → the per-Task PM Agent (`agents/pm.md` relays it into its Final report, one labelled sub-block per in-flight invocation) → this field. Without a named destination the narrative reaches the orchestrator and stops there, which is the whole point of asking for it. The **Bee-level** review in Section 5 has its own destination — the `**Second-order effects**` field of Section 9's `## Bee Execution Complete` block — because these per-Task summaries have already been printed by the time that review runs. Render it as follows:

1. **Collect every relayed narrative attaching to this Task** — the per-Task PM's Final report `### Second-order effects` section, including each `#### <invocation scope>` sub-block it carries. Render the bullets **verbatim**; do not re-summarize, re-rank, or fold them into the `**Reviews**` line.
2. **Keep the sub-block labels** the PM supplied, so a reader can tell which invocation surfaced which effect.
3. **De-duplicate exact repeats** across sources — one effect relayed twice is one effect; keep the earliest attribution. Near-duplicates that differ in substance are kept separately.
4. **When every source reported the fixed empty line** (`No second-order effects identified.`), or no `/quo-engineer-review` invocation was made for this Task, render the single line `None identified.` — do **not** omit the field. It is unconditional: a section that appears only when there was something to say degrades into one nobody can rely on being asked for.

**Record each ignored-feedback item as a `defer-N` TaskList task at the moment of decision.** Whenever the Director chooses to ignore a review-feedback item rather than fix it now, create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the feedback's one-line description as the `metadata.activity` string, status `pending`. The PM Agent's Final report contract (`agents/pm.md`) requires the PM to annotate each deferred item with a destination — `addressed-now-in-this-Task` (no carrier needed), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — that the orchestrator records in the same `metadata.activity` string. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when items were ignored, defeating the gate's purpose. Items the Director addressed inline this Task (no ignored feedback surfaced) do **not** get a `defer-*` task — the `defer-*` ledger only tracks items not addressed now.

**Record each PM-deferred item as a `defer-N` TaskList task at the moment of the PM verdict.** When the per-Task PM Agent returns, walk its Final report deferred items (per `agents/pm.md`'s Final report contract). For every item the PM annotated with a destination of `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` (i.e., NOT `addressed-now-in-this-Task`, which is the PM's signal that the Director already addressed the item inline this Task and no inter-session carrier is needed), create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the deferral's one-line description as the `metadata.activity` string, status `pending`. Items annotated `addressed-now-in-this-Task` are NOT added to the `defer-*` ledger — they were addressed inline. This upstream record-creating step is the load-bearing source (paired with the ignored-feedback instruction above) for Section 6.5's deferral-hygiene gate; without it, PM-surfaced deferrals would only reach the active `defer-*` set via Section 6.5's Step 0 retroactive sweep, leaving the gate single-layered for PM-Final-report items where the peer skill `/quo-breakdown-epic` (per its per-Task PM dispatch site) is two-layered. Walking the PM Final report's deferred items here mirrors `/quo-breakdown-epic`'s per-Task PM-dispatch site and keeps the two-layer pattern (upstream + Step 0 sweep) symmetric across the two execution-skill peers.

#### 4.2 Find next Epic or move to Final Review

The Mode 1 continue-or-stop `AskUserQuestion` gate fired in branch 2 below fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this inter-Epic continuation gate (per Section 3's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed.

Before moving on from the just-completed Epic, perform an **inter-Epic interaction checkpoint**. This is a lightweight check deliberately positioned here (not at the final Bee-level review) so that issues introduced by this Epic's code interacting with *prior* Epics' landed code are caught while the context is fresh, before the next Epic compounds the problem.

The Director (you) runs this check directly — no new team:

1. Diff the Epic's landed commits against the previous Epic's end-state: `git log --oneline <previous-epic-last-commit>..HEAD`. Resolve `<previous-epic-last-commit>` from the run-state manifest per the rule spelled out in step 1 of the **Epic-boundary state-externalization checkpoint** below (the **Pre-Bee SHA** at the run's first Epic boundary; the previous Epic's `last commit <sha>` from **Progress** thereafter).
2. For each file this Epic touched that a prior Epic also touched, scan for:
   - **Contract drift** between what this Epic's code assumes and what a prior Epic's code actually does (especially ordering contracts, docstring claims, and "this should never happen" comments).
   - **Resource compounding** across Epics: if this Epic adds acquires from a resource that a prior Epic already uses, model the aggregate.
   - **Symmetric-change gaps**: if this Epic added a new resource class (key pattern, pool, queue, etc.), search prior Epics' cleanup paths for missing handling.
3. If any issue is found, dispatch a fresh ephemeral Engineer Agent per Section 3's dispatch shape to fix it before continuing to the next Epic. Do not defer to the Final Bee-level review — fixing at the Epic boundary keeps the scope local to the two Epics involved.
4. Record any fixes as additional commits on the branch, clearly labeled.

After the checkpoint passes (clean or fixed):

Mark the just-completed Epic as `status=done`, then re-query *all* Epics under the Bee to classify the post-Epic state. Do not assume "no workable Epic remains" means "Bee is finished" — Epics in `status=drafted` (still need `/quo-breakdown-epic`) must not fall through to final review.

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1]
report: [title, ticket_status, up_dependencies]'
```

`up_dependencies` is returned as a list of ticket IDs only — not statuses. If any Epic is in `ready` state with non-empty `up_dependencies`, batch-look-up those dependency IDs via `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>` to determine whether each `ready` Epic is actually workable or blocked.

Classify the result into exactly one of three branches (the status vocabulary `drafted` → `ready` → `in_progress` → `done` is canonical for the Plans hive). Evaluate the branches in the order listed — branch 1 takes precedence over branch 2 when both apply, because any drafted Epic must stop the loop regardless of whether other Epics happen to be workable:

1. **Drafted (or blocked-on-drafted) Epics remain** — at least one Epic has `status=drafted`, OR has `status=ready` blocked on a dependency that is not `done` (typically a sibling Epic still in `drafted`). **Stop the loop. Do NOT proceed to Step 5 final review and do NOT offer to mark the Bee done.** Tell the user:

   > Epic `<just-completed-epic-id>` is complete, but Epics `<drafted-or-blocked-ids>` in this Bee are still `drafted` (or blocked on drafted dependencies) and need breakdown before this Bee can be closed. Run `/quo-breakdown-epic <bee-id>` (a fresh session is reasonable to keep context clean) to break down the remaining Epics, then re-run `/quo-execute <bee-id>`.

   Then run the **Epic-boundary state-externalization checkpoint** defined below (next unit: `none`) and exit the skill.

2. **Workable Epic remains** (and no drafted Epics exist) — at least one Epic has `status` in `{ready, in_progress}` AND all its `up_dependencies` are `done`. Branch on the **multi-Epic run mode** captured in Section 2:

   - **Mode 1 (Stop after each Epic), or Section 2's mode prompt was skipped** (only one Epic existed in scope at run start): ask the user if they want to continue with the next logical Epic. If they accept, run the **Epic-boundary state-externalization checkpoint** defined below (next unit: the next Epic's ID), then run the **Epic-boundary context-window guard** defined below (which may stop the run at this clean boundary), then return to step 2. If they decline, run that same checkpoint (next unit: `none`, since no further Epic is picked up in this run) — but **not** the context-window guard, which never runs on a run-ending path — then move to final Bee review.
   - **Mode 2 (Work through all Epics)**: auto-continue. Surface a one-line note announcing the auto-continue and naming the next Epic ID being picked up so the user can interrupt if desired (e.g., *"Mode 2 (Work through all Epics): auto-continuing to `<next-epic-id>` — `<title>`."*). Then run the **Epic-boundary state-externalization checkpoint** defined below (next unit: the next Epic's ID), then run the **Epic-boundary context-window guard** defined below (which may stop the run at this clean boundary), and return to step 2. The Mode 2 auto-continue path still respects every other stop the orchestrator already enforces — branch 1's drafted-or-blocked-on-drafted Epic stop above takes precedence (the order-of-evaluation rule already requires evaluating branch 1 first), and any final reviewer-surfaced blocker from Sections 5 and 6 still halts the run.

3. **All Epics under this Bee are `done`** — run the **Epic-boundary state-externalization checkpoint** defined below (next unit: `none`), then proceed to Step 5 final Bee review.

##### Epic-boundary state-externalization checkpoint

This is the canonical anchor name; other sections refer to it as the *Epic-boundary state-externalization checkpoint*, and the three branches above invoke it by name on all five of their exit paths (enumerated in full at the end of this sub-section), as does `##### Aborted-run close-out` below on the run-aborting path. **It is a definition, not a step in Section 4.2's linear flow** — do not run it merely because reading reached this heading. Run it only at the point an invoking branch calls for it, which is always *after* the branch classification above has resolved: step 2 below records the next unit, and that value is unknown until the classification is done.

Because Section 3 ships flat orchestration (no recursive delegation), the orchestrator's working context grows monotonically across Epics — every Subtask dispatch, every PM review, and every reconciliation tick adds to the loop's running set — and nothing in this skill reclaims it. The Epic boundary is where the run is at its most re-derivable: on the normal path all child Tasks are complete and all per-Task commits are landed, and every fact the next Epic needs is already carried by something on disk rather than by the conversation. **On the aborted path** (`##### Aborted-run close-out` below), what "re-derivable" means depends on the **scope that close-out's step 2 resolved** — read off the entering branch, since one of them opens no marker to read a scope from. A **mid-Epic** abort (a per-Task writer lane, or a routing-gate `Cancel` fired at the per-Task review site) leaves the Epic deliberately *not* complete, with fewer commits than Tasks. A **Bee-level-review** abort (a Section 5 Bee-scoped lane, or a routing-gate `Cancel` fired at Section 5's Bee-level review) leaves every Epic and Task `done` and every per-Task commit landed, and stops the Bee short of its final review instead. In both cases the record a **later session** reads to see exactly where the run stopped is the **bees ticket state plus the landed commits** — that pair is the cross-session carrier. The manifest's aborted **Progress** entry records the same fact for this run's own post-compaction reader rather than for the next session, since a resuming `/quo-execute <bee-id>` truncates the manifest at run start. This checkpoint's job is to **verify that invariant and refresh the durable carriers**, so that whenever the harness compacts the conversation — at this boundary or partway through the next Epic — the run can be re-derived instead of reconstructed from memory.

The durable carriers are:

- **bees ticket statuses** — the just-completed Epic, its Tasks, and their Subtasks in `done`; the Bee in `in_progress`. Re-readable at any time via `bees show-ticket` / `bees execute-freeform-query`.
- **git commits** — one commit per Task per Section 4.1's after-Task commit step, plus any fix commits Section 4.2's inter-Epic interaction checkpoint landed. Re-readable via `git log` / `git diff`.
- **the session-scoped compromise tracker** — the on-disk file defined in Section 6.5 `#### Session-scoped compromise tracker`. Re-readable via the `Read` tool.
- **the `defer-*` TaskList ledger** — the active deferral set Section 6.5's gate reads. Re-readable by walking the TaskList.
- **the run-state manifest** — the on-disk file defined in Section 1 `#### Write the run-state manifest`, which carries the run-scoped values (multi-Epic run mode, isolation strategy, `<pre-bee-sha>`, compromise-tracker path, per-Epic progress) that have no other durable home. Re-readable via the `Read` tool.

At the point an invoking branch calls for it, run these three steps — before that branch does whatever it does next (return to step 2, move to final Bee review, or exit the skill). Every step below is a tool call the orchestrator can actually make — read a file, run a bees query, run a git command, walk the TaskList, write a file:

1. **Verify the carriers.** Do all four of the verifications listed below, subject to the three qualifications that come first — each applies only on the path it names; on every other path all four run exactly as written:

   - **Aborted-path qualification — mid-Epic scope.** When this checkpoint is invoked from `##### Aborted-run close-out` below **and that close-out's step 2 resolved mid-Epic scope** — an aborted per-Task writer lane (`aborted-<role>-<subtask-id>`), or a routing-gate `Cancel` fired at the per-Task review site — the first two verifications invert rather than fail: the current Epic and its Tasks are **not** all `done` and are not to be flipped — confirm instead that each reads the status the abort left it at — and **fewer commits exist than completed Tasks**, so verify only that every Task that *did* complete has its commit, and do not report the missing one for the aborted Task as a gap. The tracker and TaskList verifications run unchanged.
   - **Aborted-path qualification — Bee-level scope.** When that close-out's step 2 resolved **Bee-level** scope instead — an aborted **Section 5 Bee-scoped re-dispatch** (`aborted-<role>-<bee-id>`), or a routing-gate `Cancel` fired at Section 5's Bee-level review — **nothing inverts**: Section 5 does not run until every Epic is `done`, so at that point every Epic, Task and Subtask legitimately reads `done` and every per-Task commit has landed. Run **all four verifications on their normal path** — the Epic/Task/Subtask status re-query and the one-commit-per-completed-Task check included — and treat any genuine shortfall in either as a real gap to fix, subject to the precedence carve-out at the end of this qualification. Do **not** import the mid-Epic qualification here: asserting a not-all-`done` Epic and a commit shortfall against this state would invert two checks that are correct as written and would mask a real gap. The "just-completed Epic" the bullets below name resolves to the **last Epic this run completed** — the checkpoint already verified it once at branch 3's exit to final review, so re-verifying it here is idempotent and passes **whenever this session completed an Epic of its own**. **Precedence when it did not** — the run started with every Epic already `done`, went straight to Section 5, and a Bee-scoped writer lane aborted there (or a routing-gate `Cancel` fired at that review), so both this qualification and the all-Epics-already-done exception below are reachable at once: **the exception governs.** There is no last-completed Epic for the four verifications to name, so they stay vacuous and are skipped exactly as that exception directs (verify instead only that Section 2's placeholders resolved, as it says), and only step 2's Bee-level **Progress** append applies. What differs on this path is step 2 alone — Progress takes the Bee-level shape and no `done` Epic entry is touched.
   - **Exception — the all-Epics-already-done-at-run-start path.** When branch 3 is entered because Section 2's query found every Epic under the Bee already `done` and this session completed no Epic of its own, there is no "just-completed Epic" for the four verifications below to name and they are vacuous — skip them. Verify instead only that Section 2's `#### Resolve the manifest placeholders` step actually resolved both placeholders — the manifest must read real Epic IDs under **Epics in scope** and `not captured (all Epics already done)` under **Multi-Epic run mode**, never `pending Section 2 query` or a bare `not captured` — then go to step 2 and write next unit `none`.

   The four verifications:

   - Re-query the just-completed Epic and its Task/Subtask children in bees and confirm every one reads `done`.
   - Run `git log --oneline <previous-epic-last-commit>..HEAD` and confirm one commit exists per completed Task. **`<previous-epic-last-commit>` resolves from the run-state manifest**, not from memory: at the *first* Epic boundary of the run, use the manifest's **Pre-Bee SHA** (no prior Epic has landed yet, so the run's starting HEAD is the correct lower bound); at every later boundary, use the `last commit <sha>` recorded for the previous Epic under the manifest's **Progress** field. The same resolution rule applies to Section 4.2's inter-Epic interaction checkpoint step 1, which uses the same placeholder.
   - `Read` the compromise-tracker file at the path in the manifest's **Compromise tracker** field and confirm every compromise accepted during this Epic has an entry. **A `Read` reporting that the file does not exist is not by itself a gap** — the tracker is not created until its first append trigger fires, and an Epic records nothing when every finding it routed was answered by the user at a gate, or when its only ungated routes hit Trigger C's lone-`trivial-tweak` carve-out. That combination is less common than it once was, so do not read an absent file as the expected state; read it as "nothing was appended", and check that against what this Epic actually did. Only treat it as a gap if a compromise **was accepted**, or an ungated path pick **that Trigger C requires an entry for** was dispatched, during this Epic and no entry (or no file) exists for it. That qualifier is what keeps this check from contradicting the trigger it verifies: a unit whose sole ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less, and reporting it as a gap would tell the orchestrator to append the very entry Trigger C says not to write.
   - Walk the TaskList and confirm every per-Subtask, per-Task, and `gate-*` task from this Epic is `completed`.

   Fix any gap **now** — flip the missed status, land the missed commit, append the missed tracker entry, close the stale TaskList task — rather than carrying it forward in conversation.
2. **Rewrite the run-state manifest** per Section 1 `#### Write the run-state manifest`, recording the just-completed Epic's ID and last commit SHA under progress, and the next unit: the next Epic's ID on the paths that pick one up, or `none` on all three paths where this run picks up no further Epic (branch 1's exit for breakdown work, branch 2's Mode 1 decline, and branch 3's move to final Bee review). **On the aborted path**, the Progress write branches on the **scope `##### Aborted-run close-out`'s step 2 resolved** — read it off the entering branch, not off a marker, since the routing-gate `Cancel` branch opens none (both shapes are specified in Section 1's Progress note):

   - **Mid-Epic** (an `aborted-<role>-<subtask-id>` lane, or a `Cancel` at the per-Task review site) — there is no just-completed Epic to record: write the current Epic's **Progress** entry as aborted mid-Epic, naming the last commit that did land and the Task the run stopped in, e.g. `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`.
   - **Bee-level** (an `aborted-<role>-<bee-id>` Section 5 lane, or a `Cancel` at Section 5's Bee-level review) — every Epic's Progress entry already reads `done — last commit <sha>` and every one of them is **correct**. Leave them all exactly as they stand and **append** a Bee-level line naming what stopped the review instead — the aborted lane, e.g. `<bee-id>: Bee-level review aborted — test-writer-<bee-id>`, or on the `Cancel` route the review site plus the finding the gate fired on. Overwriting a legitimately-`done` Epic's entry with an aborted one here would record a state that never happened.

   On both, write next unit `none`.
3. **Re-read, do not recall, at every dispatch in the next Epic.** Concretely: before each Agent dispatch in the next Epic, `bees show-ticket` the Epic / Task / Subtask body being dispatched against and `Read` the run-state manifest for the run-scoped values (mode, isolation strategy, tracker path, `<pre-bee-sha>`) — rather than reusing a value quoted earlier in the conversation. Carry **no** value forward from the prior Epic: if a fact the next Epic needs is not readable from one of the five carriers above, stop and write it into one before dispatching anything.

**What this checkpoint does not do.** It does not clear, compact, or otherwise reclaim the orchestrator's context, and it must never be narrated as if it did. No model-invocable mechanism for self-clearing or self-compacting exists; token reclamation is owned by the harness, which compacts the conversation on its own once the window fills. A single Epic's working-set footprint is estimated at roughly **~25-30% of a 1M context window**. Treat that figure as an **unverified working estimate carried over from this discipline's original design note** — no measurement of it exists, and nothing in this skill produces one, so it must not be described as observed, measured, or benchmarked. It is recorded only to give downstream tooling a starting number to size against; it is **not** a budget this skill measures or enforces. The orchestrator cannot introspect its own token usage: it must not invent or estimate a number for its own remaining context from memory, report a self-measured usage percentage, or gate any branch on such a self-estimate. That prohibition targets the model *pretending to know its own usage without an external source* — it does **not** forbid reading an out-of-band, machine-written context-usage reading that a separate status-line producer process computed and wrote to a file. Reading such an externally-produced gauge via the `Read`/helper path, and stopping at a boundary on the reading it carries, is an external measurement consumed like any other on-disk carrier: both the read and the boundary-stop are model-invocable actions, so both are permitted. What stays forbidden is the self-estimate — consuming a gauge a different process wrote is not that, and neither the read nor the stop reclaims any context (see the reclamation prohibition above, which is unaffected). The reclamation lever that does exist is starting a **fresh session** at an Epic boundary (Section 4.2 branch 1 recommends exactly that when the loop exits for breakdown work); this checkpoint is what makes that lever — and any harness compaction, whenever it fires — lossless.

Every path out of Section 4.2's branches invokes this checkpoint by name — there is no way to leave that section without running it. Enumerated in full:

- branch 2's Mode 1 **accept** path and branch 2's Mode 2 auto-continue path, each before returning to step 2 (next unit: the next Epic's ID);
- branch 2's Mode 1 **decline** path, before moving to final Bee review (next unit: `none`);
- branch 1 before the loop exits for breakdown work, and branch 3 before proceeding to final Bee review (next unit: `none` on both).

The three `none` paths still run the checkpoint in full: the run is ending in this session either way, and the point of the checkpoint is that what it verifies and writes outlives the conversation.

One further invoker sits **outside** Section 4.2's branches and is therefore not in the list above: `##### Aborted-run close-out` below (next unit: `none`, on its aborted path). Both of that close-out's entering branches reach the checkpoint through it — Section 3's Reconcile-step unexplained-movement gate's **Abort this unit** choice, and the routing-decision gate's **Cancel** choice (part (d) of `### Orchestrator discipline: routing review findings`).

##### Epic-boundary context-window guard

Like the checkpoint above, this is a **definition, not a step in Section 4.2's linear flow** — do not run it merely because reading reached this heading; run it only where an invoking branch calls for it by name. Exactly **two** paths invoke it, both continuing in-session paths in branch 2:

- branch 2's Mode 1 **accept** path (next unit: the next Epic's ID);
- branch 2's Mode 2 auto-continue path (next unit: the next Epic's ID).

On each, the guard runs **after** the Epic-boundary state-externalization checkpoint has completed (so all run state is already durable on disk and a fresh session can resume cleanly) and **before** control returns to step 2. It runs on **no** `next unit: none` run-ending path — not branch 1's exit for breakdown work, not branch 2's Mode 1 decline, and not branch 3's move to final Bee review — because on a run that is ending in this session a fresh-session stop recommendation is noise, and a missing-reading gate would fire an `AskUserQuestion` immediately before final review. A single-Epic run that crosses no Epic boundary never reaches this guard at all. The state-externalization checkpoint is unconditional on every exit path; **this guard deliberately is not — do not inherit its unconditionality.**

**What this guard is (and is not).** It reads an **external** context-window gauge that a separate status-line producer process computed and wrote to a file (the `context_gauge.py` producer/reader contract). It does **not** measure the orchestrator's own token usage and is not self-introspection; consuming that on-disk reading and stopping the run at a clean boundary on it is an external measurement consumed like any other durable carrier, exactly as the checkpoint's *What this checkpoint does not do* paragraph permits. Neither the read nor the boundary-stop reclaims any context — the only reclamation lever is starting a **fresh session**, which every stop below recommends. Do not add any "clear your working context" instruction: no model-invocable self-clear or self-compact lever exists.

Run these steps:

**Step 1 — read the session id first, and evaluate it before creating any gate task.** Mirror Section 1's `#### Check session reasoning effort` ordering rule: read the environment variable with one literal command, evaluate it, and only *then* decide whether a gate fires. Do NOT `TaskCreate` before the evaluation — a stranded `pending` `gate-*` task violates the two-step contract's yield-control discipline.

```bash
# POSIX (bash / zsh):
printenv CLAUDE_CODE_SESSION_ID
```

```powershell
# Windows (PowerShell):
Write-Output $env:CLAUDE_CODE_SESSION_ID
```

**Trim any trailing whitespace/newline** from the value before use — a trailing newline fails the helper's `--session-id` validation.

**Step 2 — session id unset or empty → skip the guard silently and continue** to step 2 of branch 2. This is the **only** silent-skip path (the unsupported-CLI carve-out), matching Section 1's `CLAUDE_EFFORT`-unset handling: no gate, no `TaskCreate`, no output.

**Step 3 — session id present.**

a. Resolve the gauge helper as a sibling of this skill's base directory — the same sibling-resolution discipline used for `scoped_marker_resolver.py` in Section 3; the base directory is shown in the skill invocation header at session start:

```bash
# POSIX (bash / zsh):
<this skill's base directory>/../quo-setup/scripts/context_gauge.py
```

```powershell
# Windows (PowerShell):
<this skill's base directory>\..\quo-setup\scripts\context_gauge.py
```

b. **Obtain the stop threshold from the helper** with one literal call — the helper prints a single integer percentage. **NEVER restate that number in prose**; read it from the helper each time so this skill carries no second definition site:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold
```

c. **Read the current reading** with one literal call, substituting the trimmed session id from step 1:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" read --session-id <trimmed-session-id>
```

d. Branch on the reading's stdout and exit status. `read` prints exactly one of four values — an integer percentage, `no-reading`, `stale`, or `missing` — and exits `0` for all four; it exits non-zero on a malformed gauge **or** an invalid `--session-id`, so do NOT assume a non-zero exit implies a corrupt file:

- **integer ≥ threshold → STOP** at this boundary. Report the current percentage and recommend resuming in a **fresh session**, naming the exact resume command `/quo-execute <bee-id>`. Then exit the skill.
- **integer < threshold → continue** to step 2 of branch 2, no output.
- **`no-reading` → continue** to step 2 of branch 2, no output (a transient fresh-but-null reading — the producer is alive, the number is just not populated yet).
- **`stale` → STOP** at this boundary. Note that the producer appears to have stalled, and that recurring staleness across fresh sessions means the operator should check their status-line producer. Recommend the fresh-session resume, naming `/quo-execute <bee-id>`. Do NOT let `stale` fall through to continue.
- **non-zero exit or empty stdout → the same fail-safe stop-and-ask as `stale`** — an untrustworthy reading is treated exactly like a stalled one: STOP at this boundary and recommend the fresh-session resume with `/quo-execute <bee-id>`. Never fall through to continue.
- **`missing`** → first check the persistent opt-out marker at `<tempdir>/.quorum/context-guard-opt-out` with one literal existence check:

  ```bash
  # POSIX (bash / zsh):
  test -f /tmp/.quorum/context-guard-opt-out
  ```

  ```powershell
  # Windows (PowerShell):
  Test-Path "$env:TEMP\.quorum\context-guard-opt-out"
  ```

  **If the marker is present → skip the guard silently and continue** to step 2 of branch 2 (the operator has recorded a standing choice to run unguarded). If it is absent → **hard-stop via the two-step gate** in step 4.

**Step 4 — the missing-reading gate.** Per the two-step `TaskCreate` → `AskUserQuestion` contract (Section 3's TaskList naming convention's gate-task entry), **first** `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this boundary context-guard gate (a distinct per-fire `<short-suffix>`; honor the yield-control discipline — do not yield control while it is `pending`/`in_progress`), **then** call `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the answer is consumed. The question text should: (a) state that the environment may override the operator's user-level status-line config, so no reading is being published; (b) publish the gauge file contract — its path (`<tempdir>/.quorum/context-usage-<session_id>.json`), its required fields (a `session_id` and a `context_window` object carrying `used_percentage`), and its overwrite-per-refresh semantics; (c) state that **Configure now** runs `/quo-setup --configure-gauge-producer` inline. Present these options (multi-choice only — do not add fake free-text options that duplicate `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot):

1. **Configure now** — invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool. Because a freshly-configured producer only begins publishing **next** session, after a successful Configure now the gate **recommends resuming in a fresh session** with the `/quo-execute <bee-id>` resume command rather than implying this run is now guarded, then exit the skill.
2. **Proceed without the guard (this run)** — continue to step 2 of branch 2; write no marker.
3. **Never guard me (persistent opt-out)** — write the persistent opt-out marker via the sibling helper with one literal call, then continue to step 2 of branch 2:

   ```bash
   # POSIX (bash / zsh):
   python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" write-opt-out
   ```

   ```powershell
   # Windows (PowerShell):
   python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" write-opt-out
   ```

4. **Stop here** — exit the skill with the `/quo-execute <bee-id>` fresh-session resume command.

##### Aborted-run close-out

This is the canonical anchor name for the path where the run stops **without the unit it was working advancing**. Two branches route here: Section 3's Reconcile-step unexplained-movement gate's **Abort this unit** choice, and the routing-decision gate's **Cancel** choice (part (d) of `### Orchestrator discipline: routing review findings`). Like the two definitions above it, **it is a definition, not a step in Section 4.2's linear flow** — do not run it merely because reading reached this heading; run it only where a branch calls for it by name.

An aborted run still crosses a boundary, and exiting by simply stopping skips every close-out a normal boundary runs. That is how an `aborted-*` marker (when the entering branch opened one) and a half-swept TaskList survive into the next session — where part (g)'s **Clause 2** reads those names off the TaskList and wedges the first Engineer dispatch on a task nothing will ever clear — and how the manifest is left claiming a next unit this run never picked up. Run these three steps in order:

1. **Close out the TaskList, sweeping by name prefix.** Two scopes apply; sweep each as applicable to the lane that aborted — or, on a routing-gate `Cancel`, to the review site the gate fired from:

   - **Per-Task scope** — every `<role>-<subtask-id>` implementer task under the Task the aborted writer's Subtask belongs to, or the Task under review when a routing-gate `Cancel` routed here, that Task's own `pm-<task-id>`, every `-r<n>`-discriminated round of any of them, and the `gate-*` task that fired the branch routing here. This is Section 4.1 step 3's sweep, run at an abort instead of at a Task completion.
   - **Bee scope** — when the aborted lane was a Section 5 Bee-scoped re-dispatch, **or when a routing-gate `Cancel` fired at Section 5's Bee-level review site**, every `*-<bee-id>` name Section 5's **Bee-level TaskList close-out** enumerates (the three Bee-scoped reviewers, the four Bee-scoped implementer/PM names, and their `-r<n>` rounds). A `Cancel` at that site leaves the same Bee-scoped names active as an aborted Bee-scoped lane does, so the sweep is the same.

   **A sibling lane still in flight when this close-out fires.** The orchestrator cannot terminate a dispatched background Agent, so — whichever branch routed here — an `in_progress` task in either scope may still have a live Agent behind it. Mark it `completed` anyway — the run is ending, and no tick will consume its notification — and record in its `metadata.activity` that it was in flight at the abort, so a resuming session treats that lane's work as possibly half-landed in the tree and re-checks it instead of trusting the ticket state.

   In both scopes, also mark **every `aborted-<role>-<id>` redelivery marker still `pending`** as `completed` **when one is open** — the movement-gate branch is reached *with* one open, since the abort is what created it, while a routing-gate `Cancel` opens none — and a marker left `pending` blocks the unit's advance in a later session. Record the abort reason in `metadata.activity`; that string is informational context for whoever resumes and is never a routing input. Throughout this step, **"clear from the active set" means mark the task `completed`** — never delete it; a deleted task takes the `-r<n>` round history with it, and the next round's discriminator is derived by counting the rounds already on the list.
2. **Run the Epic-boundary state-externalization checkpoint** defined above, on its **aborted path** — its step 1 carries the two aborted-path qualifications (the **mid-Epic** one, under which two verifications invert; the **Bee-level** one, under which all four run on their normal path), and its step 2 the scope-branched aborted **Progress** entry and next unit `none`. **Pick the qualification matching the scope this close-out was entered at** — read that scope off the entering branch, not off a marker, since one branch opens none: on the movement-gate branch it is the aborted writer lane's scope (an `aborted-<role>-<subtask-id>` marker ⇒ **mid-Epic**; a Section 5 Bee-scoped lane ⇒ **Bee-level**), and on the routing-gate `Cancel` branch it is the review site the gate fired from (the per-Task review site ⇒ **mid-Epic**; Section 5's Bee-level review ⇒ **Bee-level**). Everything else in the checkpoint runs unchanged: verify the compromise tracker, verify the TaskList is clear, rewrite the manifest, and re-read rather than recall on any later dispatch.
3. **Stop the run and name the resume command.** Tell the user the run stopped without the unit it was working advancing, and name what it stopped in — **branching on the scope step 2 resolved**: for a per-Task lane, name **which Subtask and which Task** it stopped in; for a Section 5 Bee-scoped lane, name **which Bee-level lane** aborted (`test-writer-<bee-id>` / `doc-writer-<bee-id>`) and say the run stopped in the Bee-level review, since there is no partially-done Subtask or Task to name — every one of them is `done`. When a routing-gate `Cancel` routed here rather than an aborted lane, name **which review site the `Cancel` fired from** (the per-Task review site, or Section 5's Bee-level review) and the finding it fired on, in place of a lane name. **Also name the uncommitted working-tree state the exit leaves behind**, branching on the same scope step 2 resolved: at **mid-Epic** scope that is the in-flight Task's edits, which no per-Task commit swept up; at **Bee-level** scope it is any Bee-level Engineer round's edits, sitting uncommitted since the last per-Task commit. A resuming session inherits that tree either way, so say what is in it rather than leaving it to be discovered. Then name the literal resume command **`/quo-execute <bee-id>`** — the same command every other stop site in this skill names. Then exit the skill. Do **NOT** run the **Epic-boundary context-window guard** here: that guard runs only on the two continuing in-session paths in branch 2, and this is a run-ending path, exactly as its own "runs on no `next unit: none` run-ending path" rule states.

### Orchestrator discipline: routing review findings

This section governs how the orchestrator routes the depth-tagged findings the in-flow review skills emit. Each reviewer finding the review skills surface carries a severity tag (`blocker` / `suggestion` / `nit`) and a depth tag (`trivial-tweak` / `refactor-locally` / `re-architect`) on each fix path it proposes, plus the count of fix paths it surfaced. The orchestrator's job here is to turn the reviewer's **enumerated fix paths and their depth tags** into exactly one routing decision — **deterministically for whether a gate fires**, and **by its own judgment for which path it picks when no gate fires**. It does NOT re-classify the reviewer's depth tags: the depth of a path the reviewer enumerated is the reviewer's call, read as emitted, and is the one classification the orchestrator must never invent. **One carve-out, and only one:** a path the orchestrator **composes** at Step 1 carries no reviewer depth tag because no reviewer ever saw it, so the orchestrator assigns that path a depth itself (Step 1 below). That is origination, not re-classification — no tag the reviewer emitted is ever overwritten.

**(a) Pick the path, then route on it.** Routing is a two-step procedure — Step 1 is the orchestrator's own judgment; Step 2 is deterministic given the path Step 1 chose.

**Step 1 — pick.** Choose the highest-quality fix path among those the reviewer enumerated (definition below). The reviewer's `[preferred]` token is an **input** to this choice, not a verdict: prefer it when it is also the most complete; when `[preferred]` marks a narrowing and a fuller path exists that is still the smallest internally-consistent complete change, take the fuller path. **The enumeration is the menu, not a ceiling.** When *no* enumerated path is the smallest internally-consistent complete change — every one of them leaves the stated defect partly unfixed — the orchestrator may **compose** the complete fix itself and pick that composed path, rather than picking the least-bad enumerated one and routing it to gate (c) as a narrowing. A composed path is the Step-1 pick like any other and routes through Step 2 unchanged; Section 6.5's **Trigger C** records how it was composed. **Assign the composed path a depth** from the reviewer's own three-value vocabulary — `trivial-tweak` / `refactor-locally` / `re-architect` — judging it as a reviewer would; this is the one case where the orchestrator originates a depth rather than reading one, precisely because no reviewer emitted a tag for a path no reviewer proposed. Step 2's rows 5 and 6 read that assigned value wherever they say "the chosen path's depth tag", so a composed path the orchestrator judges `re-architect` gates at row 5 exactly as an enumerated one would.

**Step 2 — route on the path chosen in Step 1.** Evaluate these conditions **in order**, taking the first that matches, so each finding yields exactly one routing decision:

```
| # | Condition (evaluated in order, first match wins)                      | Routing                            |
|---|----------------------------------------------------------------------|------------------------------------|
| 1 | The finding carries no depth tag, or a malformed severity/depth tag  | Treat as `re-architect` → gate (d) |
| 2 | The chosen path carries the reviewer's `[introduces-mechanism]` tag, | Scope-bounding gate (c)            |
|   | or introduces a mechanism by the orchestrator's own reading (below)  |                                    |
| 3 | The chosen path moves a published contract surface beyond what this  | Scope-bounding gate (c)            |
|   | unit's ticket states, or is breaking for existing consumers          |                                    |
| 4 | The chosen path is narrower than the smallest internally-consistent  | Scope-bounding gate (c)            |
|   | complete fix — it leaves the stated defect partly unfixed            |                                    |
| 5 | The chosen path's depth tag is `re-architect`                        | Routing-decision gate (d)          |
| 6 | Otherwise                                                            | Dispatch the chosen path, no gate  |
```

Row 6 dispatches a fresh ephemeral implementer Agent (Engineer / Test Writer / Doc Writer as the finding's lane dictates) per Section 3's dispatch shape with the chosen fix path, no user gate, and appends a tracker entry per Section 6.5's **Trigger C**. The evaluation order is load-bearing: rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) **regardless of its depth tag**, and row 1 comes first so parts (e) and (f) stay reachable unchanged. Whatever row fires, **when the chosen path changes source the re-dispatch follows part (g)'s ordering** — Engineer, then the code review for that site, then the affected writer.

**What "highest-quality" means.** The **smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names** — internal consistency across surfaces, not merely local correctness. Total-system complexity counts *against* a path. Effort is never the tiebreaker between paths of equal completeness. "Adds a mechanism" is a reason to route to gate (c), not a reason to build. For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently". **This definition is what a composed path is composed to**: a path the orchestrator writes because no enumerated one met it, so a composed path never satisfies row 4 by construction — row 4 fires on a chosen path that is *narrower* than the complete fix, and composing is the alternative to picking one that is.

**What "introduces a mechanism" means.** The path adds machinery per the mechanism definition in `agents/analyst.md` that **the approved design for this unit did not enumerate** — here, the Subtask body and its parent Task body, plus the PRD/SDD the Plan Bee's `reference_materials` resolves to (or the Plan Bee body itself when that field is null/empty). **The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2** — a tagged path routes to gate (c) with no further judgment. Orchestrator-side detection is the **fallback**, used only when no tag is present: read the fix path's own description against that definition and route it the same way.

**(b) ANTI-PATTERN — do not write this:** The orchestrator MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent (R2/R3 rounds). The following phrasings, and any close paraphrase, are forbidden inside a dispatch prompt: `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. Inlining a scope-bound silently narrows the fix without the user ever seeing the decision. When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through the scope-bounding gate in part (c) instead of writing it into the dispatch prompt.

**The prohibition targets *narrowing* language, not path selection.** Under part (a) the orchestrator's job **is** to pick a fix path and dispatch it, so a dispatch prompt that names the path chosen per part (a) and carries that path's fix **in full** is not a violation of this part. Instructing the implementer to do *less* than the chosen path is — and a path that is itself narrower than the smallest internally-consistent complete fix does not get written into a prompt at all: it routes to gate (c) via row 4.

**(c) Scope-bounding gate.** This gate has **four** entry conditions: when the orchestrator would otherwise scope-bound a finding (the behavior that REPLACES the forbidden directives in part (b)), and rows 2, 3, and 4 of part (a) — the chosen path introduces a mechanism, moves a published contract surface beyond what this unit's ticket states or breaks existing consumers, or is narrower than the smallest internally-consistent complete fix. **Downstream, the part-(b) scope-bound condition is read as row 4** — it is the same condition stated twice (the orchestrator was about to dispatch something narrower than the smallest internally-consistent complete fix), so every rule below that enumerates "row 2, 3, or 4" covers it without naming it separately. On any of the four, it fires an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract with the finite choices below — the severity paragraph that follows establishes which of them the finding's severity makes available, and whether the gate fires at all:

**Severity rules the choice set — a `blocker` can be neither deferred nor accepted, and fires no gate here.** When the finding reaching this gate carries the `blocker` severity tag, the `Defer to follow-up Issue` and `Accept the limitation` choices below are **unreachable**: do not offer them, and do not route to them by any other path. That leaves `Fix properly now` as the only remaining choice, and a single option is not a decision to ask about — so **no gate fires at all**: re-dispatch the appropriate implementer Agent per Section 3's dispatch shape with the full fix, and say in the round's narrative that the gate was skipped because the finding was a `blocker` — **naming the entry condition that brought it here (row 2, 3, or 4) and what the chosen path does that triggered that row**: the mechanism it builds on row 2, the published contract surface it moves on row 3, the part of the stated defect it leaves unfixed on row 4. A path that skipped its gate is at least visible in the round. **That dispatch appends a Section 6.5 Trigger C entry** (this is Trigger C's second firing site): the orchestrator did pick the path at Step 1, and the pick reached an implementer with no user gate between, which is exactly what Trigger C records. Without the entry the pick would be invisible to Section 6's PHASE 3, which is the only surface that challenges an ungated judgment. **This is a legitimate execute-mode divergence** from `/quo-fix-issue`, whose blocker choice set has a second member — re-dispatching its Analyst — that has no counterpart here: execute mode has no Analyst. Because a `blocker` never reaches the `Defer to follow-up Issue` or `Accept the limitation` branches, Section 6.5's **Trigger A** and **Trigger B** are unreachable for `blocker` findings — no tracker entry can record a deferred or accepted blocker.

The three choices below are the choice set for `suggestion`- and `nit`-severity findings.

- **Fix properly now** — Re-dispatch the appropriate implementer Agent per Section 3's dispatch shape to address the finding fully, no scope-bound.
- **Defer to follow-up Issue** — File a follow-up Issue via `/quo-file-issue` (inline via the Skill tool, per the precedent in `/quo-fix-issue` Section 1's URL-resolution sub-step) carrying the finding's description, and proceed with the soft fix this round. **The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside** — dispatch it **directly**, not by re-entering Step 2 with it: a remaining path is by definition narrower than the one just deferred, so Step 2 would match row 4 and route it straight back to this gate. Or, when the deferred path was the only one enumerated, with no fix for this finding this round (the same end state as `Accept the limitation`, with the follow-up Issue filed). Never invent a narrowing to fill the slot; part (b) forbids it.
- **Accept the limitation** — Record the limitation as an accepted compromise and proceed. (Recorded by the session-scoped compromise tracker — see the `#### Session-scoped compromise tracker` block in Section 6.5.)

The question text includes the finding verbatim plus a one-line context line stating why the gate is firing (which of the four entry conditions above brought it here). **When the Step-1 pick was a composed path**, that context line also describes it — its letter, the depth Step 1 assigned it, and what it does — because a composed path appears nowhere in the reviewer's emission the finding-verbatim text reproduces, so a user reading only that text would be answering about a path they cannot see. This is the same rule part (d)'s composed-path clause carries at its own gate. **There is no `Cancel` option at this gate** — scope-bounding is a per-finding decision and a `Cancel` here would be ambiguous; the user retains `Ctrl-C` for run-level abort.

**Recommended default on the mechanism row.** When this gate fires on a **non-`blocker`** finding because the chosen path **introduces a mechanism** (row 2) serving a case this unit's ticket never mentions, `Defer to follow-up Issue` is the **recommended default** — mark that choice `(Recommended)`. (On a `blocker` the gate does not fire at all, per the severity rule above.) A mechanism the ticket never asked for has its own lifecycle to design, and building it inside this unit is what turns one finding into several rounds. The follow-up Issue MUST carry the reviewer's sketched design **verbatim**, so nothing about the proposed mechanism is lost by deferring it.

**(d) Routing-decision gate.** When part (a)'s Step 2 routes a finding here (row 1 or row 5 — a finding whose depth is unknown or malformed, or whose chosen path is `re-architect`), fire an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract whose choices are:

**Severity rules the choice set here too — a `blocker` has no Defer route.** When the finding reaching this gate carries the `blocker` severity tag, the `Defer to follow-up Issue` choice below is **unreachable**: do not offer it, do not mark it Recommended, and do not route to it by any other path. The choice set for a `blocker` is then the one-choice-per-fix-path list below plus **Cancel** — this skill has no Analyst, so the second blocker choice `/quo-fix-issue` offers at its gates has no counterpart here, the same legitimate execute-mode divergence part (c) records. Unlike part (c), the gate normally still fires: when the reviewer enumerated **one or more** fix paths, a `blocker` here has those paths plus `Cancel` to choose between, which is a real decision to ask about. **Zero-path carve-out.** A row-1 finding can arrive with **no** fix path enumerated at all (that is what a malformed or absent tag emission looks like), and with the Defer choice withheld the set collapses to `Cancel` alone — which ends the run. Part (c)'s own principle governs: a single option is not a decision to ask about, and offering `Cancel` as the sole answer to a `blocker` turns a shapeless emission into a run abort. So on a **`blocker` with zero enumerated fix paths, no gate fires**: dispatch the full fix of the finding **as the finding describes it** per Section 3's dispatch shape, and record it per Section 6.5's **Trigger C site (2)**, whose `Rationale` notes that zero paths were enumerated and the gate was skipped. Together with part (c)'s severity rule this means **no `blocker` reaches a Defer or Accept branch at either gate** — so the tracker's `User picked Defer to follow-up Issue` and `User picked Accept the limitation` `Decision` values can never describe a `blocker` finding.

- **One choice per reviewer-surfaced fix path** — each choice's description includes that path's depth tag (e.g., `re-architect`, `refactor-locally`). **The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1** — this gate asks the user to ratify or override a pick that has already been made, so the marker must name that pick. The reviewer's `[preferred]` token is an **input** to Step 1 and usually coincides with the pick; when it does not — the shape Step 1 exists for, where `[preferred]` marks a narrowing and a fuller path is the smallest internally-consistent complete change — mark the **fuller** path Recommended, not the `[preferred]` one, and say in that choice's description that the reviewer preferred the other path so the user can see the divergence. **When the Step-1 pick was a composed path** routed here by row 5, present that composed path as a choice of its own alongside the reviewer's — under the next unused letter, described in full — and mark **it** `(Recommended)` per the rule above; a gate that offers only the paths the orchestrator already rejected as incomplete is not offering the pick it is asking the user to ratify. **Fallback:** on a row-1 entry (no depth tag, or a malformed one) no Step-1 pick was possible, so no path is marked Recommended.
- **Defer to follow-up Issue** — File a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now.
- **Cancel** — Ends work on the unit under review without the chosen fix landing, and **ends the run**. Route through `##### Aborted-run close-out` (Section 4.2), which sweeps the TaskList by prefix at the scope of the site the finding came from, runs the Epic-boundary state-externalization checkpoint on its aborted path, then stops the run naming the uncommitted working-tree state and the `/quo-execute <bee-id>` resume command. Execute mode has no Issue concept and its abort always ends the run, so this choice does **not** proceed to the next Task. `Ctrl-C` remains the unconditional run-level abort.

The question text includes the finding verbatim.

**(e) Backwards-compatibility shim.** A finding emitted **without a depth tag** — a legacy reviewer emission during rollout, or a hand-authored finding from a future call site — MUST be treated by the routing table as if it carried `re-architect` depth, i.e., it routes to the user gate in part (d). The shim errs toward user input when uncertain: when the orchestrator cannot determine a finding's depth, it surfaces the decision to the user rather than dispatching its own pick ungated under row 6.

**(f) Edge-case handling.**

- **Malformed tags.** When a severity tag is not exactly `blocker` / `suggestion` / `nit`, or a depth tag is not exactly `trivial-tweak` / `refactor-locally` / `re-architect`, the orchestrator treats the finding as `re-architect` depth (per the shim in part (e)) AND surfaces the parse failure to the user so the reviewer emission can be corrected.
- **Routing ambiguity.** If the routing table somehow returns more than one decision (impossible by construction), default to the user gate in part (d) and surface the ambiguity to the user.
- **`/quo-file-issue` failure at the Defer gate.** When the user picks `Defer to follow-up Issue` (at either the scope-bounding gate in part (c) or the routing-decision gate in part (d)) but the inline `/quo-file-issue` dispatch fails or the user cancels at one of its gates, the orchestrator MUST NOT silently ship the soft fix (or no fix). Instead it surfaces the failure to the user and re-prompts with the same gate's choices, so the user can re-attempt the defer, pick `Accept the limitation` where that choice exists (non-`blocker` findings only — per the severity rules in parts (c) and (d), a `blocker` never had either that choice or the Defer choice, so this whole bullet is moot for one) / a specific fix path explicitly, or (at the routing gate) Cancel.

**(g) Re-dispatch ordering when a fix path changes source.** Once a finding's routing is settled (**the orchestrator's own path pick per part (a), or the user's pick at the gate in part (c) or (d)**), the orchestrator still has to decide *how many lanes to dispatch at once*. When the chosen fix path requires a **source change**, the Engineer re-dispatch and the affected writer re-dispatch are **ordered, not concurrent**: dispatch the **Engineer** first, then the code review for that site — the **Bee-level Code Reviewer** at Section 5's site (Clause 2), and the **per-Task PM's in-flight `/quo-engineer-review` pass** at the per-Task site (Clause 1), which is that site's only code-review coverage since this skill dispatches no per-Task Code Reviewer — against the resulting diff, and only once that code review has closed dispatch the **Test Writer** and/or **Doc Writer** whose input the source change invalidated. Dispatching the Engineer and a writer in the same round hands the writer a diff that the pending code review is about to rewrite, which is what forces the writer's work to be redone.

The precondition that makes this checkable rather than remembered is TaskList-derived. This section routes findings from **two** review sites whose diffs have different extents, so the precondition has **two clauses** with their own scoping rules. Apply the clause belonging to the site the finding came from. In both clauses, match on the TaskList name **prefix** plus the status, not on an exact name, so any discriminator a re-dispatch appends is still caught. TaskList is already one of the four authoritative read-state sources the reconciliation loop reads on every tick, so either clause is a state lookup rather than a rule the orchestrator has to hold across a compaction.

**Clause 1 — the per-Task review site** (findings from the per-Task PM Agent, which drives `/quo-engineer-review` and `/quo-doc-writer-review` in flight per `agents/pm.md`). Scope is **the Task under review**: **the orchestrator MUST NOT dispatch an Engineer Agent for a Task while any TaskList task whose name begins with `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` for a Subtask of that same Task, or with that Task's own `pm-<task-id>`, is `pending` or `in_progress`.** Implementer TaskList names are Subtask-scoped (`<role>-<subtask-id>` per Section 3's naming convention) while the PM's is Task-scoped (`pm-<task-id>`), so resolve each active writer task's Subtask to its parent Task — a `bees show-ticket --ids <subtask-id>` lookup on the subtask id embedded in the task name, reading its `parent` — before comparing. Matching on the **prefix** is what catches a re-dispatched lane's `-r<n>` name (`doc-writer-<subtask-id>-r1` and so on). The PM is in the list because it is the actor *running* the review: Engineer edits landing under an in-flight `pm-<task-id>` invalidate the very review whose findings are being routed.

**Clause 2 — the Bee-level review site** (Section 5's final review). No single Task is "under review" there: the reviewers are Bee-scoped (`<reviewer>-<bee-id>`) and the diff spans every Task in the Bee, so a Task-scoped test would leave most of the diff unguarded. Scope is therefore **the whole Bee**. **The orchestrator MUST NOT re-dispatch an Engineer Agent — Bee-scoped (`engineer-<bee-id>`) or Subtask-scoped — while any TaskList task whose name begins with one of the following prefixes is `pending` or `in_progress`:**

- `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` for **any** Subtask anywhere in this Bee;
- the Bee-scoped writer names `test-writer-<bee-id>` and `doc-writer-<bee-id>` (Section 5's own re-dispatches, per Section 3's naming convention);
- the Bee-level reviewer names `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`;
- any `pm-<task-id>` task, and the Bee-scoped `pm-<bee-id>`.

Match on the **prefix** plus the status in every case, so the `-r<n>` round discriminator a repeat dispatch appends (`code-reviewer-<bee-id>-r1`, `pm-<bee-id>-r2`, …) is still caught. The Bee-level Code Reviewer **is** in this list, unlike in the per-Task clause's PM-only reviewer coverage, because Section 5 dispatches the three reviewers **concurrently** — a Doc Reviewer finding can route to an Engineer while the Code Reviewer is still reading the same diff, and edits landing under it spend that review for nothing. No deadlock follows: a finding that re-enters the Engineer lane waits for **all** concurrently-dispatched Bee-level reviewer returns before the Engineer is dispatched, and those are live dispatches that will each notify, so this is a wait with a guaranteed end, not a cycle.

In both clauses, when a blocking task is `in_progress` (or `pending` with a dispatch already landed), wait for its completion notification and re-check on the next tick rather than dispatching. When a blocking task is `pending` and **no dispatch has landed for it**, do not wait — it will never produce a completion notification and there are no clock primitives to time it out (see "Anti-pattern: no clock primitives" in Section 3). Either dispatch that role now, or mark the stale task `completed` and clear it from the active set, then re-check. Do not narrow either clause to `in_progress` only: `pending` is in the test deliberately, to close the race where the task exists but the `Agent(...)` call has not landed yet.

**A writer that aborted on source movement does not block an Engineer round, and needs no exemption from either clause.** When a writer returns a movement report, the movement-report rung in Section 3's Reconcile step marks that writer's own `test-writer-<id>` / `doc-writer-<id>` task `completed` — its Agent has exited — and records the owed redelivery as a separate `aborted-<role>-<id>` task. `aborted-` is a **distinct name class**, so neither clause's prefix list matches it and no exemption is needed: the Engineer can be dispatched to settle the source while the redelivery stays owed. This is deliberate — an exemption keyed on an abort annotation would make the Engineer's dispatch depend on `metadata.activity`, which is informational and not a routing input. What the `aborted-*` task gates is the **unit's advance** (the parent Task's per-Task PM review, or Section 5's Bee-level review loop closing), not the Engineer; see the movement-report rung.

**Ordering after a movement report.** When a writer aborted because an Engineer moved the source, the re-dispatch ordering is this part's ordering, scoped by the clause that governs the finding in play: **Clause 1** when the mover was an Engineer re-dispatched from the per-Task review site (let that Engineer and its per-Task review round finish, then re-dispatch the writer for that Subtask), **Clause 2** when the mover was an Engineer re-dispatched from Section 5's Bee-level review (let the Engineer → Code Reviewer ordering above close over the whole Bee's diff, then re-dispatch the affected writer lanes). Section 3's Reconcile step carries the receiver — how the report is recognised and what is withheld; this part carries only the ordering of the re-dispatch that follows.

**Scope limit — this part governs the review-finding re-dispatch path only.** It does NOT apply to the forward per-Subtask fan-out in Section 3's reconciliation loop, where an Engineer on one Subtask legitimately runs concurrently with a Test Writer or Doc Writer on a different Subtask of the same Task. That cross-Subtask overlap is a designed property of execute mode's dependency-ordered dispatch, not an accident to be serialized away; only the re-dispatch rounds this section routes are ordered.

A finding whose chosen fix path changes **no source file** — a test-quality nit, a doc-wording gap — carries no ordering constraint: re-dispatch that single writer lane on its own, no Engineer round, no code review.

**Two-step gate mechanics (parts (c) and (d)).** Both gates above fire through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per each file's Section 4 / Section 3 TaskList naming convention's gate-task entry, with a distinct per-fire `<short-suffix>` so concurrent or repeated fires do not collide), **then** call `AskUserQuestion` with the finite choices above in the same turn. Do not produce a text response describing the gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. These gates are multi-choice only — do not add fake free-text options that duplicate `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot.

These new gates inherit a prose-adherence fragility — that is an execution-time risk acknowledged at run time, not something this section fixes.

### 5. Final Bee-level Code, Doc and Eng reviews

Once all Epics in the Bee are done, dispatch three concurrent ephemeral reviewer Agents per Section 3's dispatch shape, one per reviewer role: `Agent(subagent_type="code-reviewer", run_in_background=true)`, `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`. Track each via a TaskList task per Section 3's naming convention (bee-scoped form: `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`).

**The Code Reviewer dispatch prompt must relay the Engineers' completeness evidence verbatim.** Same rule as the per-Task PM dispatch in Section 3 (see "Per-Task PM dispatch"), widened to Bee scope: when any Engineer return during the Epic loop carried a **completeness check with evidence** for a sweep-shaped Subtask (the search patterns run, every hit, and per hit either the change made or the reason it is deliberately untouched), embed every such list **verbatim** in the Code Reviewer's dispatch prompt **and in any `pm-<bee-id>` re-dispatch prompt** under a clearly labelled `## Engineer's completeness evidence` heading, attributing each list to its Subtask. Embed the lists as text in the prompt — do **not** write them to a scratch file and pass a path. The evidence has no other carrier once the Engineer Agent has exited, and `/quo-engineer-review`'s sweep-verification check needs the list to verify against. **Separately from the lists, state in the prompt that the assignment was sweep-shaped whenever it was** — that is a fact about the assignment that was dispatched (a directive or Subtask body that directed a change at *every site* where some property holds), known independently of whether a list came back. `/quo-engineer-review`'s sweep-verification check only reports a *missing* list as a finding when the invocation itself named the assignment that way, so an unnamed sweep silently loses the check — and the case that most needs the check is precisely a sweep-shaped assignment whose Engineer returned no list. At Bee scope that means naming every sweep-shaped Subtask assignment from the Epic loop, list or no list. **One post-compaction qualification applies at this Bee-level relay only:** sweep-shapedness stays re-derivable from a Subtask body long after the Engineer's return has dropped out of this conversation, so a bare `sweep-shaped` statement here can outlive the list it was meant to accompany — and `/quo-engineer-review` would then report a missing list against an Engineer who produced one. So state `sweep-shaped` on its own **only when the list is actually in hand, or the Engineer genuinely returned none**; when a Task's assignment was sweep-shaped and its Engineer return is no longer readable (a compaction across Epic boundaries), say in the prompt that a completeness list **existed but is unavailable post-compaction**, naming the Subtask, so the reviewer does not report it as missing. Section 3's per-Task PM dispatch needs no such qualification — it composes its prompt while the Engineer's return is still in hand. `agents/code-reviewer.md` carries the Code-Reviewer-side half (pass the list through into its `/quo-engineer-review` invocation). **The Bee-scoped PM needs its own copy:** it is a *second* `/quo-engineer-review` caller on this diff — `agents/pm.md` drives that skill in flight via the `Skill` tool, and its PM-side bullet requires it to pass a completeness list into that invocation, a list it can only pass on if this dispatch prompt gave it one. Relaying to the Code Reviewer does not cover it: those are different Agents with no channel between them. When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one — but still state that the assignment was sweep-shaped when it was, so `/quo-engineer-review`'s missing-list check stays reachable.

Conditional spawn — only dispatch a reviewer whose corresponding implementer was used during the Epic loop:
- If Engineer Agents were dispatched during the Epic loop, dispatch the code-reviewer Agent now.
- If Test Writer Agents were dispatched during the Epic loop, dispatch the test-reviewer Agent now.
- If Doc Writer Agents were dispatched during the Epic loop, dispatch the doc-reviewer Agent now.

Reviewer role contracts (responsibilities, model assignment, gating, instructions) live in the role files; the orchestrator's job is to dispatch, not to carry the role's prose.

- **Code Reviewer** (`agents/code-reviewer.md`) — reviews the Engineer's output and surfaces gaps against engineering standards.
- **Test Reviewer** (`agents/test-reviewer.md`) — reviews the Test Writer's output and surfaces gaps against test-quality standards.
- **Doc Reviewer** (`agents/doc-reviewer.md`) — reviews the Doc Writer's output and surfaces gaps against documentation standards.

- Get the feedback, and make a judgement call about whether that work must be done. Each of the three review skills above (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a second-person imperative routing trailer (`**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`) plus a counter-anchor clause at the bottom of its output, naming the precise routing this step must take after consuming the findings. **Follow the trailer literally** — it is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory.
  - If feedback requires action, dispatch fresh ephemeral implementer Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer / PM as needed). **Track each under the Bee-scoped names from Section 3's TaskList naming convention** — `engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>` — with the `-r<n>` round discriminator on every dispatch after the first (`engineer-<bee-id>-r1`, and so on), including a second Bee-level code review (`code-reviewer-<bee-id>-r1`). These findings span the whole Bee's diff and are not attributable to one Subtask, so they do not borrow a Subtask-scoped or Task-scoped name. Stay in delegate mode. **When a finding's chosen fix path changes source, these re-dispatches are ordered, not concurrent** — Engineer, then Code Reviewer, then the affected writer. See part (g) of `### Orchestrator discipline: routing review findings` for the ordering rule and the TaskList precondition it rests on; findings routed from **this** section take that precondition's **Clause 2 (Bee-level)**, which scopes to the whole Bee rather than to one Task and enumerates exactly these prefixes.
  - **Second-order effects have a destination.** The Bee-level Code Reviewer relays `/quo-engineer-review`'s `### Second-order effects` subsection verbatim on every return, clean ones included (`agents/code-reviewer.md`), and a Bee-scoped PM re-dispatched here relays it into its Final report (`agents/pm.md`). It is narrative rather than routing input — anything actionable in it is already a numbered finding, so it does not by itself require a re-dispatch. Render it into the **`**Second-order effects**` field of the `## Bee Execution Complete` summary** (Section 9's summary template), which is the destination for everything relayed at this Bee-level site. Do **not** route it into Section 4.1's per-Task field: that field belongs to the per-Task PM's relayed narrative, and those summaries were printed as each Task closed, so a Bee-level effect sent there lands in output the run has already emitted. Do not let it terminate in this conversation.
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** spawn the Product Manager on this iteration
  - If not, move on to Final Review but you MUST share the ignored feedback for review
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in Final Review
  - **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.** Whenever the Director chooses to ignore Bee-level reviewer feedback rather than re-dispatch implementers to address it, create a `defer-<short-suffix>` TaskList task (named per Section 3's "TaskList naming convention") with the feedback's one-line description as the `metadata.activity` string, status `pending`. The Director MUST annotate the `defer-*` task's `metadata.activity` with one of the three destination labels from the PM Agent's destination vocabulary (`agents/pm.md`) — `addressed-now-in-this-Task`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — when creating the task. The destination is the Director's judgement call captured at ignore time, but the annotation itself is required, not optional; matching the PM Agent's contract here keeps Section 6.5's deferral-hygiene gate able to route reviewer-feedback and PM-feedback items through the same Fix / File / Encode branches uniformly. Vague framings without a named destination (e.g., "defer to later") are forbidden by the same anti-pattern rule that applies to the PM Agent's annotations. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when items were ignored at this site, defeating the gate's purpose.

**Bee-level TaskList close-out (runs once, after the review loop above has closed).** Section 4.1 step 3 closes out the Subtask- and Task-scoped names as each Task finishes, but every name this section dispatches is **Bee-scoped** and has no such site — an unclosed one stays in the active set and keeps matching part (g)'s **Clause 2**, wedging every later Engineer dispatch on a task nothing will ever clear. **The review loop has not closed while any `aborted-<role>-<bee-id>` task is `pending`**: a writer this section re-dispatched that aborted on source movement still owes its delivery (Section 3's movement-report rung), so re-dispatch that lane and let it deliver first. Once the loop has closed on that test and **every** Bee-level dispatch has returned — before advancing to Section 6 — mark the following `completed` and clear them from the active set, **sweeping by name prefix** so `-r<n>`-discriminated rounds go with their first round:

- the three Bee-scoped reviewer names — `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>` (plus `code-reviewer-<bee-id>-r1`, and so on);
- the four Bee-scoped implementer and PM names this section re-dispatches — `engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>` (plus their `-r<n>` rounds);
- any Bee-scoped aborted-writer redelivery markers — `aborted-test-writer-<bee-id>`, `aborted-doc-writer-<bee-id>` — opened by Section 3's movement-report rung for a lane this section dispatched. Reaching this step means the redelivery landed, since the review loop cannot close over a lane that never delivered.

**"Clear from the active set" means mark the task `completed` — it never means delete it.** The `-r<n>` round discriminator is derived by counting the rounds already recorded for that role at that scope (per Section 3's naming convention), so a deleted task takes its round out of that count and the next re-dispatch reuses a name that is already spoken for. Closing a task by status leaves the history readable and still removes it from every `pending`/`in_progress` test part (g) runs.

This step runs **exactly once per Bee**. There is no Agent shutdown to perform — the cold dispatches complete-and-exit when each Agent returns; this is bookkeeping on the progress UI, and on the state part (g) reads.


### 6. Post-Completion Review

After the review loop in step 5 is done and all fixable issues have been addressed by the team, run one final fresh-context generalist sweep across all changes made by this Bee. This is an independent quality gate — separate from the per-Task and per-Epic review cycles above.

**Anti-pattern callout — read before acting.** Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/quo-engineer-review` is scoped to source code, `/quo-doc-writer-review` to user-facing docs, `/quo-test-writer-review` to test files — none of them runs the cross-lane sweep this step needs). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, PM verdict, and per-Task reviewer verdicts from the whole Bee run; that context biases it toward "did the phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the Bee body and nothing else — that's the point.

1. Compute the pre-Bee diff scope. Capture `<pre-bee-sha>` as the HEAD that existed when work began on this Bee (`Read` the run-state manifest at `<tempdir>/.quorum/run-state-quo-execute-<bee-id>.md` and take its **Pre-Bee SHA** field — that is where Section 1's run-start step recorded it; as a fallback if the manifest is missing, use `HEAD~M` where `M` is the number of Tasks committed in Step 4 — one commit per Task; if you've lost count, walk `git log` back to the commit before the first Task commit landed in Step 4 as a backup). Collect the Bee ID `<bee-id>` and, secondarily, the IDs of the Epics/Tasks under it as `<epic-id-1> <task-id-1> ...` (the Bee body is the primary spec; Epic/Task bodies are secondary context the reviewer can consult when something in the diff is ambiguous).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. The agent will not see anything else from this run, so the prompt must be self-contained. Pass the compromise-tracker file path (Section 6.5's `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`) as `<compromise-tracker-path>` — the path, NOT the inlined contents; the dispatched Agent reads the file itself via its own `Read` tool. Starting skeleton (substitute `<pre-bee-sha>`, `<compromise-tracker-path>`, `<bee-id>`, and the Epic/Task IDs before sending):

   ```
   You are an independent reviewer for a quorum Bee that was just shipped.

   Scope: review the diff `git diff <pre-bee-sha>..HEAD` (compute it yourself
   via git) against the Bee body — read it via `bees show-ticket --ids
   <bee-id>`. The parent Epic/Task bodies are secondary spec sources; consult
   them via `bees show-ticket --ids <epic-id-1> <task-id-1> ...` only when the
   diff vs. the Bee body is ambiguous. The orchestrating team-lead has
   finished the work — your job is to give it a fresh-eyes review with no
   context of how the work was done.

   Perform these phases IN ORDER. Phases 1–5 lead with challenging the
   compromises that were accepted during the run; the discrete-defect sweep is
   the FINAL phase, not the first.

   PHASE 1 — Consume the compromise tracker (passed as a FILE PATH).
   The session-scoped compromise tracker records every compromise the run
   accepted (deferred-to-Issue findings, accepted limitations, ungated
   orchestrator path picks, post-completion overrides). Its path is:
   <compromise-tracker-path>
   Read that file yourself via your Read tool — it is passed as a path, not
   inlined. Each `## Compromise <n>` entry carries: Finding (verbatim), Fix
   paths surfaced by reviewer (each with a `[depth:<...>]` tag), Decision,
   Rationale, Follow-up Issue. If the tracker file is MISSING or unreadable,
   do NOT abort — PROCEED with the remaining phases and flag the missing
   tracker explicitly in your output (so the dropped hand-off is visible
   rather than silent).

   PHASE 2 — Challenge each tracked compromise on its merits. For every entry,
   push back when the chosen path is not defensible; do not rubber-stamp a
   compromise just because it was accepted. Include the deep-asked-but-cheap-
   shipped check: the tracker records what the user asked for (or, on an
   ungated pick, what the orchestrator chose), the diff is what actually
   shipped — flag any mismatch (e.g., the user picked a deep fix path but the
   implementer's diff implemented the cheap path). ALSO: any entry whose
   `Finding (verbatim)` carries the `blocker` severity tag and whose
   `Decision` is `User picked Defer to follow-up Issue` or `User picked
   Accept the limitation` is a contract violation — a blocker can be neither
   deferred nor accepted. Emit it as a `[compromise-challenge]` finding at
   `blocker` severity, never lower.

   PHASE 3 — Ungated-pick plausibility check, on TWO axes. For every tracker
   entry whose Decision is `Orchestrator picked path (<letter>) —
   highest-quality` — the `<letter>` varies per entry, since the writing step
   substitutes the chosen path's own letter, so match on the surrounding
   wording rather than on a literal letter — evaluate BOTH: (i) was the depth
   judgment plausible, or is the chosen path's true depth `re-architect`; and
   (ii) did the chosen path in fact introduce a mechanism — a new state,
   configuration surface (flag, environment variable, setting), persisted or
   wire field, background task, exception or error type, metric / log / trace
   attribute, name or identifier class, gate, or retry / fallback path that
   the unit's approved design did not enumerate — and, if so, should that
   machinery have been deferred to a follow-up ticket or put to the user
   rather than built here? Ask that of every such entry regardless of which
   site recorded it, and regardless of whether a gate was reached: an entry
   can record a path that never routed to a gate, and one that did but was
   dispatched because the gate declined to fire. Emit a
   `[compromise-challenge]` finding on either axis. Axis (ii) is required, not
   optional: an ungated pick is an orchestrator judgment no gate reviewed, and
   this phase is the only place it gets challenged.

   PHASE 4 — Fix-path-enumeration plausibility check. For EVERY finding the
   in-flow reviewer surfaced (regardless of severity / depth / path-count),
   evaluate whether the in-flow reviewer should have enumerated an additional
   plausible fix path. When you judge under-enumeration — the reviewer
   surfaced fewer paths than existed, so the pick (the orchestrator's, or the
   user's at a gate) was made from an incomplete menu — emit a
   `[compromise-challenge]` finding naming the under-enumeration. These two
   checks are complementary: PHASE 3 catches misjudged depth or an unnoticed
   mechanism on a path that WAS surfaced; PHASE 4 catches a plausible path
   that was NOT surfaced at all.

   PHASE 5 — Holistic solution-quality judgment beyond the logged compromises:
   is the shipped solution actually good, independent of any single tracked
   decision?

   PHASE 6 — Discrete-defect sweep (the final phase). Flag anything that looks
   wrong: code defects, prose problems, spec drift between the change and the
   Bee, contract-key violations (do NOT allow renames of keys in CLAUDE.md
   `## Documentation Locations` or `## Build Commands`), cross-file
   inconsistencies, missing edits the Bee called for.
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

   Return findings as a numbered list. Tag EVERY finding with exactly one of
   `[compromise-challenge]` (a challenge to an accepted compromise, from
   PHASE 2/3/4) / `[design]` (a solution-quality concern) / `[defect]` (a
   discrete defect), PLUS the severity tag (`blocker` / `suggestion` / `nit`),
   PLUS the per-fix-path depth tag and the enumerated fix paths from the
   in-flight emission contract. The depth tag is informative here: this
   post-completion sweep is the final pre-merge gate, so any finding it emits
   is a gate candidate regardless of depth. Preserve the `file:line` +
   severity shape — the new tags are additive to it. If clean, return exactly
   "no issues found".
   ```

   Wait for the agent's report.

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-Task PM verdict and per-Task code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

   **Compromise-challenge preamble (rendered before presenting the findings).** When the post-completion reviewer returns one or more `[compromise-challenge]` findings, render a one-or-two-sentence prose preamble BEFORE the findings list that names this explicitly, so the user reads the section with the right framing. Mirror the verdict-keyed preamble pattern in `/quo-plan` Step 5e and `/quo-fix-issue` Section 3's Analyst-verdict preamble — a short prose lead with the `⚠️`-led divergent-framing convention used when a challenge is present, e.g. "⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below." When there are no `[compromise-challenge]` findings, no preamble is needed (present the findings directly).

   **Orchestrator self-tracking close-out (mandatory before yielding).** Independent of the per-Task TaskList tasks already closed in Section 4.1 step 3 and of **every** Bee-scoped task — reviewer, implementer, PM, and aborted-writer marker alike — already closed by Section 5's **Bee-level TaskList close-out** (that step is authoritative for every `*-<bee-id>` task **dispatched by Section 5**; this one adds nothing to it, and neither covers the post-completion-scoped names step 6's `Fix in this session` branch dispatches under, which that branch closes out itself), the orchestrator typically creates additional ad-hoc TaskList tasks during this Section 6 pass to break the post-completion review into discrete steps (e.g., "Get diff scope", per-ticket "Verify <id>" entries, "Synthesize findings"). Before presenting the synthesized findings to the user — i.e., before yielding the turn at step 4 / step 5 below, whether to deliver "no issues found" or to ask the user how to handle flagged issues via `AskUserQuestion` — mark every such orchestrator self-tracking TaskList task `completed` and clear them from the active set. The yield is the close-out trigger: when the orchestrator stops responding (either at end-of-flow or to wait on the user's reply), the TaskList must show no `in_progress` entries left over from these synthesis steps. This discipline is the orchestrator-self-tracking analog of **step 6's** per-finding follow-up close-out below (which scopes to the `<role>-postcomp-<n>` Agents that branch dispatches, their `-r<k>` movement-abort re-dispatches, and any `aborted-<role>-postcomp-<n>` marker they open); the two are complementary, not overlapping.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and continue to Final Output.

5. If the agent flagged any issues, fire the user-facing gate through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this post-completion findings gate (per Section 3's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` in the same turn. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch in step 6 is entered.
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now before closing the Bee
     - **File as issue tickets** — create issue tickets via `/quo-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
   - **Fix in this session**: Dispatch fresh ephemeral Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. Stay in delegate mode — do not do the work yourself.

     **Naming.** Section 3's TaskList naming convention is Subtask-, Task-, and Bee-scoped, and none of those scopes fits a post-completion follow-up that answers one finding of a whole-Bee sweep. Use the **post-completion-scoped** name `<role>-postcomp-<n>`, where `<n>` is the 1-based index of the finding being addressed in the fresh reviewer's numbered list (e.g. `engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`) — the same form `/quo-fix-issue` Section 8 step 6 uses, so a reader moving between the two skills reads one convention. The per-finding discriminator is load-bearing: Section 3's "exactly one TaskList task per Agent" rule still applies, so two findings that each need an Engineer follow-up dispatch under distinct names rather than colliding on a shared `engineer-postcomp`.

     **Close-out.** When each follow-up Agent returns, persist the result the way Section 3's reconcile-on-completion step does — confirm any bees ticket transitions the worker committed to — then mark the corresponding `<role>-postcomp-<n>` task `completed` and clear it from the active set, where **"clear" means mark `completed`, never delete** (same rule as Section 5's Bee-level close-out). Sweep by name **prefix** before this branch exits, so no post-completion-scoped task is left active.

     **Section 3's movement-report rung carries over onto the post-completion names.** A `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` return that reports it *stopped* on detected source movement is **not** a completion. Apply that rung here: mark the writer's own `<role>-postcomp-<n>` task `completed` (its Agent has exited) and open an `aborted-<role>-postcomp-<n>` task `pending` in its place — **the marker carries the same `<n>` as the lane it marks** — with the writer's "how far I got" report as its `metadata.activity` string. Re-dispatch the lane once the source has settled, per that rung's three mover branches, under the round-discriminated post-completion name the naming convention's abort carve-out permits: `<role>-postcomp-<n>-r<k>` (e.g. `test-writer-postcomp-2-r1`), with the same `<n>` as the aborted lane. Mark the `aborted-*` task `completed` when that re-dispatch delivers. **While an `aborted-<role>-postcomp-<n>` task is `pending`, do not treat this Section 6 pass as finished and do not commit** — that pending marker is the owed redelivery, exactly as in Section 3. The rung's **unexplained-movement gate** applies unchanged, with its third option read as *abort this follow-up lane* rather than *abort this unit* (every Epic is already `done` by this point), and its close-out is **this branch's own prefix sweep above**, not Section 4.2's `##### Aborted-run close-out` — that close-out is scoped to a run that stops **without the unit it was working advancing**, which no post-completion follow-up lane does (every Epic is `done` and committed by the time Section 6 runs). After the sweep closes out that lane's names, continue Section 6's own flow — the remaining findings' dispositions, then step 7's compromise-challenge recovery gates, then Section 6.5 — rather than exiting the run.

     **The Engineer-dispatch freeze precondition applies here too, on the post-completion names.** Part (g)'s two clauses key on Subtask-, Task-, and Bee-scoped names, none of which match these, so state it explicitly for this branch: **the orchestrator MUST NOT dispatch an `engineer-postcomp-<n>` Agent while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` TaskList task is `pending` or `in_progress`** — matching on the name **prefix** plus status, at **every** finding index and every `-r<k>` re-dispatch round, not only the `<n>` of the finding being addressed. The reason is part (g)'s own: a writer handed a diff an Engineer is about to rewrite has to redo its work. Part (g)'s `pending`-with-no-Agent-behind-it clause carries over unchanged — dispatch the stalled role, or mark the stale task `completed` and clear it, rather than waiting on a notification that will never arrive.

     **Order the lanes when one finding needs both a source change and a test/doc change.** Dispatch the **Engineer** (`engineer-postcomp-<n>`) first and let it return; only then dispatch the `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` lane whose input that source change determines. Two findings independent of one another may still be worked concurrently — the within-finding ordering here and the cross-finding precondition above are the only constraints.

     After every follow-up lane has delivered, commit and continue to Section 6.5 (deferral hygiene).
   - **File as issue tickets**: For each issue, invoke `/quo-file-issue` with the issue description. Report the created ticket IDs to the user. Continue to Section 6.5.
   - **Skip**: Continue to Section 6.5.

7. **Compromise-challenge recovery gates.** A `[compromise-challenge]` finding from PHASE 3 or PHASE 4 is not handled by step 6's generic Fix / File / Skip disposition alone — each such finding triggers its own recovery gate, fired **before or alongside** the step-6 disposition for that finding. **One challenge class has no recovery gate, by design: the deferred-or-accepted-`blocker` contract violation PHASE 2 emits.** There is nothing to recover — the entry records a choice the gates should never have offered — so that finding is dispositioned by **step 6's Fix / File / Skip gate alone**, and because it is a `blocker`, the orchestrator recommends **`Fix in this session`** in that gate's question text. Do not invent a fourth gate for it. Both gates below use the two-step `TaskCreate` → `AskUserQuestion` contract: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (a distinct collision-resistant `<short-suffix>` per fire, per the per-fire-uniqueness rule), **then** call `AskUserQuestion` with the finite choices in the same turn. Do not produce a text response describing the gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. These are multi-choice only — do not add fake free-text options. Each gate **fires per challenged finding** (once per such `[compromise-challenge]` finding — three such findings ⇒ three gate firings), NOT aggregated into one gate; the **firing order equals the reviewer's emission order** in its numbered list. These gates inherit a prose-adherence fragility — an execution-time risk narrowed (not closed) by the two-step contract; do not claim it is fixed. After the recovery gates resolve for every challenged finding, continue to Section 6.5.

   - **SR-6.7 ungated-route recovery gate.** When a `[compromise-challenge]` finding flags an ungated orchestrator path pick (Decision `Orchestrator picked path (x) — highest-quality`) on either of PHASE 3's two axes — a misjudged depth, or a chosen path that introduced a mechanism and should have routed to the scope-bounding gate — fire a three-choice `AskUserQuestion` (the choice labels below are byte-matched against Section 6.5's Trigger D branches; do not reword them). **The pinned strings read generically across both axes:** `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and Trigger D's `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` all name **the routing misjudgment** the challenge landed on — the mechanism axis included, not the depth axis only. Read "depth decision" / "misjudgment" that way rather than concluding the mechanism axis has no gate; the choices are:
     - `File follow-up Issue to revisit the depth decision` — dispatch `/quo-file-issue` via the Skill tool capturing the depth-mismatch finding plus the original compromise-tracker entry as context; the **original Trigger C tracker entry's `Follow-up Issue` field is updated in place** with the new Issue ID (NO new tracker entry — per Section 6.5's Trigger D `File`-branch note).
     - `Accept the misjudgment and proceed` — fires Section 6.5's **Trigger D** append (a NEW tracker entry with `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` and the reviewer's challenge text as Rationale). This step FIRES Trigger D's write — it does not author it; the write mechanism is owned by Section 6.5's Trigger D.
     - `Pause to discuss` — stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. No tracker write fires on this branch until a subsequent `Accept` / `File` pick (per Trigger D's `Pause` note).
   - **SR-4.6 under-enumeration recovery gate.** When a `[compromise-challenge]` finding flags under-enumeration (the reviewer's fix-path-enumeration plausibility check), fire the **same three-choice gate shape** with relabeled choices:
     - `File follow-up Issue to surface the missing path` — dispatch `/quo-file-issue` via the Skill tool capturing the under-enumeration finding as context; the tracker write follows Section 6.5's Trigger D `File`-branch under-enumeration note (append a new entry, or update an existing originating Trigger C entry's `Follow-up Issue` in place when one exists).
     - `Accept the under-enumeration and proceed` — fires Section 6.5's **Trigger D** append (a NEW tracker entry with `Decision: User accepted under-enumeration after post-completion challenge` and the reviewer's under-enumeration challenge text as Rationale). This step FIRES Trigger D's write — it does not author it.
     - `Pause to discuss` — stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. No tracker write fires on this branch until a subsequent `Accept` / `File` pick.

   The SR-4.6 gate's per-branch behavior shape mirrors the SR-6.7 gate exactly (file follow-up Issue / append explicit-override tracker entry via Section 6.5's Trigger D mechanism / pause-and-resume). Like the SR-6.7 gate, it fires per challenged finding (non-aggregated) in reviewer emission order.

### 6.5 Before handoff — deferral hygiene

Every `AskUserQuestion` firing in this gate (Step 2's initial Fix / File / Encode choice, plus any Step 3 re-fires when an earlier routing branch failed to close out a subset of the active `defer-*` set) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate (a distinct `<short-suffix>` per fire, so the Step 3 re-fires are not mistaken for the Step 2 first fire), then `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed.

#### Session-scoped compromise tracker

The orchestrator maintains a **session-scoped compromise tracker** — a single markdown file that accumulates one entry per accepted compromise across this run, so a legitimately-accepted compromise (a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override) stays visible and challengeable rather than being baked silently into the new baseline. The four append triggers (A/B/C/D) are defined under "Compromise-tracker append triggers" below; the post-completion review in Section 6 consumes the tracker as input. This subsection is the **canonical definition site** that those trigger write-instructions reference by name.

**Tracker file path and naming.** The tracker is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `compromises-YYYYMMDD-HHMM-<short-suffix>.md`, where `YYYYMMDD-HHMM` is a UTC timestamp (e.g., `20260520-1714`) generated **once at the start of the run** and `<short-suffix>` is a short collision-resistant random string. The timestamp prefix makes tracker files debuggably identifiable across multiple runs accumulated in `<tempdir>/.quorum/` over time — without it, the user has no easy way to map an old tracker file back to a specific session. Create the `.quorum` directory if it does not already exist, then author and append the tracker file itself via the `Write` tool (no shell redirect), consistent with the bash-etiquette and scratch-file conventions:

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write / append the tracker to /tmp/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write / append the tracker to $env:TEMP\.quorum\compromises-<YYYYMMDD-HHMM>-<short-suffix>.md via the Write tool
```

**Entry shape.** Each accepted compromise appends one `## Compromise <n>` section, where `<n>` is a **1-based counter scoped to the current run's tracker file** (NOT a globally unique identifier). The canonical shape (reproduced from the SDD Data models `#### Compromise tracker entry shape`) is:

```markdown
## Compromise <n>

- **Finding (verbatim):** <severity tag> <fix-path enumeration with depth tags> <description>
- **Fix paths surfaced by reviewer:**
  - (a) [depth:<depth>] <description>
  - (b) [depth:<depth>] <description>
  - ...
- **Decision:** <one of: User picked path (a) | User picked path (b) | ... | User picked Defer to follow-up Issue | User picked Accept the limitation | Orchestrator picked path (x) — highest-quality | User overrode auto-route after post-completion challenge (depth misjudgment) | User accepted under-enumeration after post-completion challenge>
- **Rationale:** <user's stated reason if surfaced via AskUserQuestion, or — on an ungated orchestrator pick — the one-line reason that path was preferred over the others>
- **Follow-up Issue:** <ticket ID if filed via /quo-file-issue, else `none`>
```

The five fields are **Finding (verbatim)** (the severity tag + fix-path enumeration with depth tags + description), **Fix paths surfaced by reviewer** (the `(a)/(b)/...` lines, each carrying its `[depth:<...>]` tag), **Decision** (one of the enum values above), **Rationale** (the user's stated reason if surfaced via `AskUserQuestion`, or — on an ungated orchestrator path pick — the one-line reason that path was preferred over the others), and **Follow-up Issue** (a ticket ID, else `none`). The `Decision` enum carries **two** post-completion-override values — `User overrode auto-route after post-completion challenge (depth misjudgment)` (the SR-6.7 depth-misjudgment override) and `User accepted under-enumeration after post-completion challenge` (the SR-4.6 under-enumeration analog override) — because Trigger D (below) is the single owner of all post-completion-override writes regardless of which kind fired.

**Persistence.** The tracker is a file-system artifact, so it persists across orchestrator-yield events within a single run inherently (a yield does not lose file state). A fresh `YYYYMMDD-HHMM` timestamp + `<short-suffix>` is generated at the **start of each run**, so previous-run tracker files remain visible in `<tempdir>/.quorum/` but are **NEVER appended to** — a new run always writes its own new file. Never delete the tracker file (scratch-file convention) — do NOT instruct any `rm` / `Remove-Item`.

#### Compromise-tracker append triggers

Four moments append an entry to the session-scoped compromise tracker defined above. The first three fire from the "Orchestrator discipline: routing review findings" section's gates / ungated dispatch; the fourth fires from Section 6's post-completion review. Each trigger anchors to its gate by name; the write fires from the branch named here.

**Trigger A — Defer to follow-up Issue at the scope-bounding gate.** At the scope-bounding gate (the `Fix properly now` / `Defer to follow-up Issue` / `Accept the limitation` gate in the "### Orchestrator discipline: routing review findings" section above), when the user picks `Defer to follow-up Issue`: append a tracker entry **IMMEDIATELY AFTER** `/quo-file-issue` returns successfully with the new Issue ticket ID, and **BEFORE** the orchestrator continues with the soft-fix dispatch this round. Capture the follow-up Issue ID in the entry's `Follow-up Issue` field; set `Decision: User picked Defer to follow-up Issue`. **Name in `Rationale` which remaining enumerated path shipped as the soft fix** — by its letter — or that **none did**, on the single-path case where deferring leaves no fix this round; the deferral and what shipped in its place are one decision, and an entry recording only the deferral leaves the reader unable to tell a soft-fixed finding from an unfixed one. (This write fires from that gate's `Defer to follow-up Issue` branch.) **Unreachable for a `blocker`-severity finding** — that gate's severity rule withholds this branch from blockers entirely (in this skill a blocker fires no gate there at all), so no Trigger A entry can exist for one.

**Trigger B — Accept the limitation at the scope-bounding gate.** At the same scope-bounding gate's `Accept the limitation` branch, when the user picks `Accept the limitation`: append a tracker entry **IMMEDIATELY AFTER** the `AskUserQuestion` returns the user's choice, and **BEFORE** the orchestrator continues without a fix. Set `Decision: User picked Accept the limitation`; set `Follow-up Issue: none`. **Unreachable for a `blocker`-severity finding**, for the same reason as Trigger A — that gate's severity rule withholds this branch from blockers entirely.

**Trigger C — ungated route (the orchestrator's own path pick).** This trigger has **no gate** — the write is wired into the dispatch step itself. It fires at **two** sites, both of which dispatch **ungated**, with no user gate in between: (1) any finding part (a) routed by **row 6**, and (2) a **gateless `blocker` dispatch**, in either of the two places a gate declines to fire on a blocker because one option is not a decision to ask about — at the scope-bounding gate (c), where the severity rule leaves `Fix properly now` alone, and at the routing-decision gate (d)'s **zero-path carve-out**, where a row-1 blocker enumerated no fix path and only `Cancel` would remain. Both are one site class: a blocker dispatched on the orchestrator's own reading with no user gate between. At the **MOMENT of implementer dispatch** on either site, append a tracker entry in the **SAME LOGICAL BLOCK as that dispatch** — not a separate post-gate block. **One carve-out (site (1) only — see the site-(2) exception at the end of this trigger):** a finding whose *only* fix path is `trivial-tweak` appends nothing — a single trivially-deletable path is not a decision worth tracking. A pick among two or more paths always is, even when every path is shallow. **The carve-out is evaluated on the reviewer's enumeration alone, and never applies when the Step-1 pick was composed:** composing is itself a pick between what the reviewer enumerated and a path no reviewer proposed, so a composed entry always appends however few — or however shallow — the enumerated paths were. Set `Decision: Orchestrator picked path (x) — highest-quality`, where `(x)` is the chosen path's letter; set `Rationale:` to **the orchestrator's own one-line reason for preferring that path over the others** — why it is the smallest internally-consistent complete change — not merely the name of the rule that fired, since the rule name gives Section 6's challenge nothing to push against; set `Follow-up Issue: none`. **On site (2)**, add to that same `Rationale` a note that the finding was a `blocker` and which gate was skipped rather than answered — for a gate-(c) entry, the entry condition that routed it there (row 2, 3, or 4) and what the chosen path does that triggered it; for a gate-(d) zero-path entry, that the reviewer enumerated no fix path. The entry otherwise reads as an ordinary row-6 pick and the challenge loses both the fact that no gate was ever offered and the reason it was not.

**Field substitution on site (2)'s two sub-cases where no enumerated path was dispatched as written.** The `Decision` prefix stays byte-identical in every case — `Orchestrator picked path ` … ` — highest-quality` — so PHASE 3's match still hits; only the `(x)` slot and the paths field vary:

- **Gate-(d) zero-path entry** — there is no letter to substitute, so write `(none)` in the `(x)` slot (`Decision: Orchestrator picked path (none) — highest-quality`) and `Fix paths surfaced by reviewer: none`. The `Rationale` carries what was dispatched, since the finding's own description is all there was.
- **Gate-(c) row-4 entry** — keep the Step-1 path's letter in the `(x)` slot and the reviewer's enumerated paths in the paths field, but state in `Rationale` that what reached the implementer was **the complete fix**, not that path as the reviewer wrote it: row 4 fires precisely because the chosen path was narrower than the smallest internally-consistent complete fix, and an entry naming the letter alone would misreport what shipped.

The same substitution pattern covers one further case, on **either** site:

- **A composed path** (Step 1's "the enumeration is the menu, not a ceiling" branch) — write the **next unused letter** after the reviewer's own in the `(x)` slot (`(c)` when the reviewer enumerated `(a)` and `(b)`), list the reviewer's enumerated paths unchanged in the paths field, and add the composed path to that list under its new letter so the menu and the pick read together — **carrying the depth Step 1 assigned it**, in the same `[depth:<...>]` shape the reviewer's own lines use, so Section 6's PHASE 3 axis (i) has a depth to challenge on a composed path rather than a blank where every other entry has one. **Mark that line inline as orchestrator-composed** — append `(orchestrator-composed — not enumerated by the reviewer)` after its description — so the field stays a faithful record of what the reviewer actually surfaced: PHASE 4 reads it as the reviewer's menu when judging under-enumeration, and an unmarked composed line makes the reviewer look *less* under-enumerating in precisely the case where the composition is the evidence that it was. The marker lets PHASE 4 count the reviewer's own paths without reading the `Rationale`. State in `Rationale` that **the reviewer did not enumerate this path** and **what the enumerated paths lacked** — which part of the stated defect each of them left unfixed. That is the whole record of a path no reviewer proposed, and it is what PHASE 3 pushes against.

**The lone-`trivial-tweak` carve-out applies on site (1) only.** A gateless `blocker` dispatch always appends, even when the finding surfaced a single `trivial-tweak` path: it is exactly the pick with no gate behind it that PHASE 3 exists to challenge, and suppressing the entry would leave that judgment with no record anywhere. On site (1) the carve-out stands as written above — a lone trivially-deletable path is not a decision worth tracking.

**Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).** Trigger D is the single owner of all post-completion-override tracker writes, fired from Section 6's post-completion review. It covers **both** post-completion-override gates present in Section 6 — the SR-6.7 depth-misjudgment recovery gate AND the SR-4.6 under-enumeration analog recovery gate. The write logic here anchors to those gates by name, with choice labels byte-identical to the recovery-gate choices so they line up.

- **SR-6.7 depth-misjudgment recovery gate:**
  - `Accept the misjudgment and proceed` → append a **NEW** tracker entry **IMMEDIATELY AFTER** the user picks this choice, **BEFORE** the post-completion flow continues. Set `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)`; set `Rationale:` to the post-completion reviewer's challenge text.
  - `File follow-up Issue to revisit the depth decision` → **NO new entry is appended.** Instead, the **ORIGINAL Trigger C entry** (already written at dispatch time for this ungated-route finding) has its `Follow-up Issue` field **UPDATED in place** to the new Issue ID. (The depth misjudgment concerns a path the in-flow reviewer already surfaced and the orchestrator routed without a gate, so an originating Trigger C entry always exists to amend.)
  - `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again — no write fires on this branch until a subsequent `Accept` / `File` pick.
- **SR-4.6 under-enumeration analog recovery gate (same Trigger D mechanism, under-enumeration variant):**
  - `Accept the under-enumeration and proceed` → append a **NEW** tracker entry **IMMEDIATELY AFTER** the user picks this choice, **BEFORE** the post-completion flow continues. Set `Decision: User accepted under-enumeration after post-completion challenge`; set `Rationale:` to the post-completion reviewer's under-enumeration challenge text.
  - `File follow-up Issue to surface the missing path` → file the follow-up Issue and capture its ID. This branch concerns a missing path the in-flow reviewer never surfaced, so there is generally **no original Trigger C entry to amend** — append a **new** entry with the under-enumeration `Decision` value and the new Issue ID in `Follow-up Issue`. If the under-enumeration relates to an existing ungated-route finding (an originating Trigger C entry does exist), mirror the SR-6.7 File-branch's behavior instead and **UPDATE that entry's `Follow-up Issue` in place**; append otherwise.
  - `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again.

Section 6's Fix / File / Skip gate handles only the fresh-eyes generalist sweep's findings. Throughout the Epic loop (Sections 3–4) and the in-flight reviewer loops (Section 5), the PM Agent's per-Task reports and any earlier orchestrator-side judgement calls may have flagged additional items as "address later", "defer to next phase", "pick up during a follow-up Issue", or similar inter-session deferrals. Each such item that the orchestrator chose not to address inline MUST have been recorded as a `defer-<short-suffix>` TaskList task per Section 3's TaskList naming convention (at the per-Task site in Section 4.1 and at the may-ignore-feedback site in Section 5); this gate is the pre-handoff reconciliation step that closes them out into durable inter-session carriers.

Section 7's existing "show ignored feedback" prose at Bee close-out stays as the display layer — it surfaces the now-closed-out deferrals to the user one last time. This gate is the structural step that ensures the active set is empty before that display fires.

**Step 0 — Retroactive ledger reconciliation (safety net).** Section 4.1's `**Ignored Review Feedback**` summary field on each per-Task report and Section 5's may-ignore-feedback site each instruct the Director to create a `defer-<short-suffix>` TaskList task at the moment the item is ignored. Before running Step 1's enumeration, walk every per-Task summary the orchestrator produced during this run, every PM Final report's deferred items (per `agents/pm.md`'s Final report contract — every item with a `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` destination annotation maps to a `defer-*` task; items annotated `addressed-now-in-this-Task` are skipped because they were addressed inline), and any orchestrator-side ignored item that did not flow through those two surfaces, and **create a corresponding `defer-*` TaskList task for any item that does not already have one**. The upstream record-creating instructions at Section 4.1 and Section 5 are the load-bearing source; this retroactive sweep is the defense-in-depth safety net for orchestrators that miss the instruction (or for runs where an item was ignored outside the documented sites). After the retroactive reconcile, every ignored item is represented in the active `defer-*` set and Step 1's enumeration sees the canonical view.

**Step 1 — Enumerate the active deferral ledger.** Scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. If the active set is empty, emit a one-line console message — recommended string: `Deferral hygiene: no deferred items.` — and proceed to Section 7 (Final Output).

**Step 2 — Surface the active set and gate the user choice.** When the active set is non-empty, surface the list to the user as numbered markdown (one bullet per `defer-*` task, the `metadata.activity` text as the bullet's body), then fire the user gate through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 3's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` with the finite choices below in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the routing into Fix / File / Encode begins.

- **Fix in this session** — Re-dispatch the appropriate implementer / reviewer Agents per Section 3's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch below, to resolve each deferred item now. After each item is resolved, mark its `defer-*` TaskList task `completed` (with `metadata.activity` updated to log the resolution path).
- **File as issue tickets** — For each item, invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body (the precedent for inline-Skill-tool dispatch lives in `/quo-fix-issue` Section 1's URL-resolution sub-step and `/quo-plan` Step 4b). Mark each `defer-*` TaskList task `completed` once the `/quo-file-issue` dispatch returns successfully and the created Issue ID is captured.
- **Encode in an existing ticket body** — For each item the user maps to an existing ticket (a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass), append a `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body and run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update, where `<YYYY-MM-DD HH:MM>` is the current local date and time written into the heading from your own clock via the `Write` tool (it is a value you author into the body-file as a string, not a shell-computed substitution — do not add a `date` / `Get-Date` snippet for it). Keep the `## Deferred from /quo-execute run` stem verbatim and only append the parenthesized timestamp suffix: the suffix exists so that multiple Encodes to the same ticket body across separate runs sit side-by-side with distinguishable headings rather than stacking identical ones — do not simplify it back to a bare heading. Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir. **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode — e.g., for the encode triggered by `defer-3`, the scratch file is `bees-body-defer-3.md`. Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the scratch file directly back to its TaskList progenitor:

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

  **Follow-up commit (after all Encode writes in this gate firing have landed).** This gate fires AFTER Section 4.1's per-Task commit step has already produced one commit per Task in this run — so the `bees update-ticket --body-file` writes above persist new on-disk changes to the relevant hive's per-ticket directory (or to the project PRD/SDD file path), but those changes are NOT swept into any prior per-Task commit and would otherwise leave the working tree dirty when the skill yields. Produce one follow-up commit per gate firing covering all Encode writes from this firing — not per Encode item — to keep commit churn proportional to the user's choice. Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (the same pattern Section 4.1's commit step uses for Plans), `git add` each hive path that lives inside this repo, additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations, then commit only if `git diff --cached` shows staged changes (an out-of-repo hive plus no PRD/SDD encode routes would stage nothing — skip the commit in that case rather than producing an empty one). Commit subject contract: `Encode deferral: /quo-execute — <N> deferral(s) encoded` where `<N>` is the count of `defer-*` items the user routed to Encode in this gate firing. **`<N>` counts deferral items, not tickets** — several items can be encoded into one ticket body, and one item can be encoded into several, so the item count is the honest number and is the same value passed as the helper's `--count` below.

  This workflow (hive-path resolution via `bees list-hives`, in-repo scoping, conditional commit on staged state) is encapsulated in a bundled Python helper, `hive_commit.py`, so the orchestrator runs it as a single literal Bash tool call rather than decomposing a multi-step shell snippet at runtime. The helper resolves the Plans/Specs/Issues hive paths, `git add`s each hive path that lives inside this repo (out-of-repo hives have already had their bees update persisted by `bees update-ticket` and require no git action), `git add`s any project PRD/SDD paths passed via `--doc-path`, then commits only if there are staged changes — printing `skipped: nothing staged` and making no commit when nothing is staged. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree (same anti-pattern as Section 4.1's per-Task commit step); the helper stages only the resolved hive paths and the explicit `--doc-path` arguments, never `-A`.

  **Resolving the helper path (own-skill resolution).** `hive_commit.py` is shipped by this skill (`/quo-execute`); resolve it against **this skill's own base directory**: `<this skill's base directory>/scripts/hive_commit.py` (no `..` hop). The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-execute`). **This differs from `/quo-fix-issue` and `/quo-breakdown-epic`,** which resolve the same helper as a *sibling* of their own base directory because they consume it across skills; here, in `/quo-execute` itself, the helper lives inside this skill, so resolution drops the `..` hop.

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

The three options are mutually-non-exclusive at the active-set level — the user may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., "fix items 1 and 2 now, file 3 as an Issue"). Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. When the user wants to route different items to different options, they select `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`) and type the per-item routing in free-form; the orchestrator parses the reply and closes out each `defer-*` task accordingly.

**Step 3 — Hard-stop on a non-empty active set.** Until every `defer-*` task is `completed`, the skill cannot proceed to Section 7 (Final Output) and cannot mark the Bee `done`. This is the structural enforcement: a deferral that was important enough to surface during the run is important enough to encode in a durable carrier before the run ends. If the user picks options that fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or a `bees update-ticket` invocation errors), surface the still-active `defer-*` tasks back to the user with `AskUserQuestion` and re-run the gate until the active set is empty.

The fresh-session-per-phase recommendation at Bee close-out (Section 7 / Section 10) is preserved verbatim — this gate sits before that handoff prose; it does not replace it.

### 7. Final Output

When **all** Epics in the Bee are done, you must show the User the full list of all Reviewer feedback you chose to ignore.
- Use the AskUserQuestion tool to ask the User if they want you to act on any of these, or just continue.

The session-scoped compromise tracker's accepted-compromise entries are surfaced separately, in Section 9's `## Bee Execution Complete:` summary block via that section's "Accepted compromises" logic — they sit alongside the other rendered run-end summary fields there rather than in this ignored-feedback display.

Every `AskUserQuestion` invocation in this section MUST go through the two-step `TaskCreate` → `AskUserQuestion` contract. For each gate (the ignored-feedback action gate, the per-Acceptance-Criteria sign-off gate, the final Bee-done gate below), **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 3's TaskList naming convention's gate-task entry — distinct suffix per distinct gate), **then** call `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the user's answer is consumed.

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
**Second-order effects**: [the relayed `### Second-order effects` narrative from the Bee-level review — rendered per the "Second-order effects" logic below]
[**Accepted compromises** — rendered per the "Accepted compromises" logic below, or OMITTED ENTIRELY when the tracker is empty or absent]

All work has been synced to git.
```

**Second-order effects (rendered into the summary block above).** This field is the **destination** for the narrative relayed out of the **Bee-level** review in Section 5 — the Bee-level Code Reviewer relays `/quo-engineer-review`'s `### Second-order effects` subsection verbatim on every return (`agents/code-reviewer.md`), and a Bee-scoped PM re-dispatched by that section relays it into its Final report (`agents/pm.md`). Section 4.1's per-Task field is the destination for the **per-Task** PM's relayed narrative and is already printed by the time this section runs, so routing the Bee-level narrative there would aim it at summaries the run has emitted and closed. Render it as follows — the same four steps Section 4.1 uses, at Bee scope:

1. **Collect every relayed narrative from the Bee-level review** — each Bee-level Code Reviewer return (one per round, including `-r<n>` rounds) and any Bee-scoped PM's Final report `### Second-order effects` section, including each `#### <invocation scope>` sub-block it carries. Render the bullets **verbatim**; do not re-summarize or re-rank them.
2. **Keep the sub-block labels** the relaying source supplied, so a reader can tell which round or invocation surfaced which effect.
3. **De-duplicate exact repeats** across sources — one effect relayed twice is one effect; keep the earliest attribution. Near-duplicates that differ in substance are kept separately.
4. **When every source reported the fixed empty line** (`No second-order effects identified.`), or no Bee-level review that emits the subsection ran at all, render the single line `None identified.` — do **not** omit the field. Unlike `**Accepted compromises**`, this field is unconditional: a section that appears only when there was something to say degrades into one nobody can rely on being asked for.

**Accepted compromises (rendered into the summary block above).** The session-scoped compromise tracker (defined in Section 6.5 `#### Session-scoped compromise tracker`) accumulates one entry per accepted compromise across the whole run, so this surface reflects the tracker file's current contents at the moment the summary renders. Render it as follows:

1. **Read the run's tracker file via the `Read` tool** at the path generated once at the start of this run per Section 6.5's path convention — `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`/tmp/.quorum/...` on POSIX, `%TEMP%\.quorum\...` on Windows). The path is already known from run start, and if it is no longer in view it is recoverable from the run-state manifest's **Compromise tracker** field (Section 1 `#### Write the run-state manifest`); no shell is needed to locate or test it — just `Read` it.
2. **Omit the section entirely when there is nothing to show.** If the `Read` reports the file does not exist (an uncommon state now that an ungated path pick appends an entry whenever the pick was among two or more paths, or was composed — Trigger C's lone-`trivial-tweak` carve-out (which applies on its row-6 site only, never on a gateless blocker dispatch) is the only ungated route that appends nothing, so expect most runs with a tracked pick to have at least one entry), OR the file exists but contains no `## Compromise <n>` entries, do NOT render the `**Accepted compromises**` line at all — no empty heading, no `N/A`, no "no compromises" placeholder. Treat "file absent" and "file present but empty" identically: omit.
3. **When entries exist, render one bullet per `## Compromise <n>` entry**, surfacing exactly these four user-facing fields from the entry:
   - the **finding** — the entry's `Finding (verbatim)`,
   - the **chosen path** — the entry's `Decision`,
   - the **rationale** — the entry's `Rationale`,
   - the **follow-up Issue ID** — the entry's `Follow-up Issue` (a ticket ID, or `none`).

   Do NOT surface the fifth entry field (`Fix paths surfaced by reviewer`) — this surface shows the path that was chosen, not the full menu of paths the reviewer offered.
4. **Volume (>10 entries).** When the tracker has accumulated more than ~10 entries, surface them ALL in full — do NOT truncate, summarize away, or elide any entry; the tracker exists precisely to preserve this signal. Precede the bullets with a short prologue noting the volume (e.g., "N compromises were accepted during this run:").

This surface only **reads** the tracker — it never writes, appends to, or deletes it (the write side is owned by Section 6.5's append triggers).

### 10. Further testing and merging

Instruct the user to perform whatever further testing they want to do, then advise on merging based on the isolation strategy chosen in step 1:

- **Worktree** — If `/bees-worktree-rm` is installed (it is not part of the portable core), invoke it to merge the worktree branch and clean up the worktree directory. Otherwise, instruct the user to merge the worktree branch manually (`git merge <branch>` from the parent repo, then `git worktree remove <path>`).
- **Feature branch** — Instruct the user to merge the branch (e.g., `git merge bee/b.Wx7`) or open a PR. Do NOT push to remote unless the user asks.
- **Worked on main/current branch** — Commits are already on the branch. Remind the user that the work is committed locally and they can push when ready.