---
name: quo-execute
description: Proceed through each Epic in a Bee, doing the work described therein. Report questions and status back to caller.
argument-hint: "[<bee-id> | <epic-id>]"
---

## 1. Preconditions

Before anything else, verify the host repo is configured for quorum. **Hard-fail** with `Run /quo-setup first.` plus a one-line note of what is missing if any item below is absent. Do not improvise commands or guess paths.

- The seven custom subagent types are registered in this session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. Custom subagents load at session start; a fresh install needs a Claude Code restart or `/agents` to hot-reload. Verification rides on the first dispatch: an `Agent type '<name>' not found` error from the Agent tool for any of the seven STOPS the run with `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` Never fall back to `general-purpose` as a substitute for a missing role, never skip the dispatch, never improvise a substitute role.
- The Plans hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `plans`.
- The Specs hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section; roles read doc paths from it by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`; roles read commands from it by exact key.

## 2. Run-state manifest

#### Write the run-state manifest

This is the canonical definition site for the run-state manifest; later sections refer to it by name. Write it at run-start step 5 (Section 4), once the Bee ID and the isolation strategy are known and before any Epic work begins; step 8 refreshes two of its fields.

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds ticket state, git holds the diff, and the compromise tracker holds accepted compromises; the manifest holds only what those three do not — including the run's lanes, obligations, rounds, and open gate. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `run-state-quo-execute-<bee-id>.md`, where `<bee-id>` is this run's Bee ID. Create the `.quorum` directory if it does not exist, then author the manifest via the `Write` tool, never a shell redirect, and never delete it.

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

**The filename is deterministic — do NOT add a random suffix or timestamp.** The manifest's reader is the orchestrator itself after a possible compaction, so the path must be recomputable, not remembered. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends: `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has, while `/quo-fix-issue` — whose batch membership is only recoverable from inside the manifest itself — appends the repository directory basename instead. Accepted collision: two concurrent `/quo-execute` runs against the same Bee share one file, and already collide over statuses and commits.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it fresh at run start, rewrite it at every boundary checkpoint, and rewrite the `## Lanes`, `## Obligations`, `## Rounds`, and `## Open gate` sections at the moment each changes. The manifest carries **only values that have no other durable home**; do not add ticket bodies, review findings, or anything readable from bees, git, or the tracker.

```markdown
# Run state — quo-execute @ <bee-id>

- **Skill:** quo-execute
- **Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>
- **Unit scope:** Bee <bee-id>; Epics in scope: <epic-id-1, epic-id-2, ... | pending Section 4 query>
- **Multi-Epic run mode:** <Mode 1 (Stop after each Epic) | Mode 2 (Work through all Epics) | not captured (single Epic in scope) | not captured (all Epics already done) | not captured | captured late>
- **Isolation strategy:** <branch created: <name> | current branch: <name> | worktree: <path>>
- **Pre-Bee SHA:** <pre-bee-sha>
- **Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md
- **Context guard:** <not run | no reading | <integer>% at <epic-id>>
- **Progress:**
  - <epic-id>: done — last commit <sha>
- **Next unit:** <next-epic-id | none>

## Lanes
| role | scope | round | dispatched | status |
|---|---|---|---|---|

## Obligations
| kind | id | scope | detail | status |
|---|---|---|---|---|

## Rounds
| scope | role | nits applied without re-review |
|---|---|---|

## Open gate
none
```

- `**Pre-Bee SHA:**` is captured once, here, with `git rev-parse HEAD` (identical on POSIX and PowerShell); Section 11 reads it back from this file.
- `**Compromise tracker:**` records the tracker's full path including its random `<short-suffix>`, generated here per Section 10; recording the path does not create the file.
- `**Progress:**` carries one line per finished unit in the order worked: `<epic-id>: done — last commit <sha>`; `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`; `<epic-id>: aborted at the inter-Epic checkpoint — last commit <sha>`; or `<bee-id>: Bee-level review aborted — <what stopped it>`. Never overwrite a legitimately-`done` Epic entry with an aborted one.
- `## Lanes` holds one row per dispatched Agent: `role` is the subagent type, `scope` is the Subtask, Task, Epic, or Bee ID it works (`postcomp-<n>` for a post-completion lane), `round` is the 1-based dispatch count for that role at that scope, `dispatched` is `no` until the `Agent(...)` call returns and `yes` after, and `status` is `open` or `closed`. A lane is `closed` when its Agent is gone — a completion notification was processed, a movement report was received, or the run ended — whether or not its work shipped.
- `## Obligations` holds one row per owed action: kind `defer-*` (id `defer-<n>`, detail = one-line description plus destination), and kind `aborted-*` (id `aborted-<role>`, detail = the writer's "how far I got" report). Status is `open` or `closed`. Detail is informational; routing reads only kind, scope, and status.
- `## Rounds` holds one row per lane (scope and role) carrying the count of `trivial-tweak` nits applied in that lane's final implementer pass without a further reviewer round (Section 7); `round` in `## Lanes` counts dispatches, `## Rounds` counts nits.
- `## Open gate` names the gate about to fire, its scope, and its choice labels verbatim, or `none`.
- The manifest carries lane phase and obligations; an earlier rule forbade the manifest a lane-phase field, and that rule is withdrawn.
- Validate the manifest before trusting any field: its `**Unit scope:**` must name this run's Bee. A manifest naming another unit is treated as absent.

## 3. After a compaction

If a summarization marker is visible in the conversation, treat everything before it as non-authoritative. `Read` the manifest and re-read bees and git in full before dispatching anything. Before routing a finding, `Read` the routing reference; before dispatching the post-completion reviewer, `Read` the post-completion prompt reference. Never act on the summary. Conversation memory is never a substitute for these sources, on every tick, not only after a compaction. If `## Open gate` is not `none`, re-fire that gate from its recorded choices before anything else.

`<this skill's base directory>` is the path shown in the skill invocation header; sibling skills' `references/` and `scripts/` are reached from it through `..`.

| Reference | Path (POSIX; PowerShell uses `\`) |
|---|---|
| routing | `<this skill's base directory>/references/routing.md` |
| post-completion prompt | `<this skill's base directory>/references/post-completion-prompt.md` |
| compromise tracker | `<this skill's base directory>/references/compromise-tracker.md` |
| context guard | `<this skill's base directory>/references/context-guard.md` |
| rationale | `<this skill's base directory>/references/rationale.md` |

## 4. The loop

The orchestrator performs mechanical steps that produce a tool artifact directly — git queries, manifest reads and writes, bees status flips, helper invocations; it dispatches every step that is a judgment over file contents or a review. Dispatch is by fresh, ephemeral background `Agent` invocations against the sibling `agents/` subagent types; there is no long-lived team, no warmed Agent, and no peer-to-peer messaging.

### Run start

1. Run the session-effort gate (Section 6) first, once.
2. Pick the Bee. No arguments: list Plan Bees with `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=plans]\nreport: [title, ticket_status]'`, keep those with status `ready` or `in_progress`; one match → use it; several → fire the Bee-pick gate (Section 6); none → say no Plan Bee is workable and suggest `/quo-plan` or `/quo-plan-from-specs`. A Bee ID: use it. An Epic ID: walk up with `bees execute-freeform-query --query-yaml 'stages:\n  - [id=<epic-id>]\n  - [parent]\nreport: [title, ticket_status]'` and use the parent Bee.
3. Validate the Bee: status `ready` or `in_progress`, and every `up_dependencies` entry `done`; a `ready` dependency is a pending blocker. `up_dependencies` returns IDs only; batch-look-up statuses with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`.
4. Run the isolation gate (Section 6).
5. Write the run-state manifest (Section 2) with `pending Section 4 query` and `not captured` as first-write placeholders.
6. Query every Epic under the Bee: `bees execute-freeform-query --query-yaml 'stages:\n  - [parent=<bee-id>, type=t1]\nreport: [title, ticket_status, up_dependencies]'`. An Epic is workable when its status is `ready` or `in_progress` and every `up_dependencies` entry is `done`; batch-look-up statuses as in step 3. Select the Epic to work: exactly one workable Epic → take it; several → recommend the one with the fewest downstream dependencies and fire the Epic-pick gate (Section 6). The selected Epic is the one step 9 stale-checks and flips.
7. When two or more Epics exist and at least one is workable or `drafted`, fire the run-mode gate (Section 6) once. Skip it when one Epic exists or every Epic is `done`.
8. Rewrite the manifest: `**Unit scope:**` with the real Epic IDs, and `**Multi-Epic run mode:**` with the captured choice, or `not captured (all Epics already done)` when every Epic is `done`, or `not captured (single Epic in scope)` for exactly one not-yet-`done` Epic. On a loop re-entry, `Read` the manifest first and carry every other field forward unchanged; this is a two-field refresh, never a fresh run-start write.
9. If the selected Epic has completed `up_dependencies`, check staleness: read the git diff of what those Epics built, read this Epic and its Tasks and Subtasks, and update any Task or Subtask description that is now stale (paths changed, signatures differ, new modules). Then mark the Epic `status=in_progress`.

### Tick

Each tick is event-driven, never clock-driven, and has three phases.

1. **Read state.** Pull the truth from three sources: bees (`bees show-ticket --ids <epic-id>` for the Epic's `children`, then each Task's `children`; `bees execute-freeform-query --query-yaml '<yaml>'` for any focused query, e.g. `stages:\n  - [id=<ticket-id>]\nreport: [title, ticket_status]`), git (the diff on disk is the only authoritative record of what workers did), and the manifest (`Read` it; its `## Lanes` and `## Obligations` are the in-flight state). Verify at least one Task with at least one Subtask exists and all are `status!=drafted`. The first time a Task starts, mark it and the Bee `status=in_progress`.
2. **Reconcile.** Compare current state to the target state and act per the phase ladder below. For every Agent that reported completion: read its return before persisting anything, confirm any bees transitions it committed to, mark its lane `closed`, and unlock what its return unlocks. A writer return that reports it *stopped* on source movement is not a completion; route it through the movement rung in Section 6.
3. **Yield.** After dispatching this tick's work, return control and wait for the Agent completion notification the `run_in_background=true` substrate delivers; that notification is the only trigger for the next tick. Never use `/loop`, `ScheduleWakeup`, or `CronCreate`, and never poll bees, git, or the manifest on a sleep-wait cycle.

### Phase ladder

- **Per-Subtask fan-out.** Sort Tasks by `up_dependencies`. For every Subtask whose dependencies are satisfied and which has no `open` lane, dispatch a fresh implementer Agent at Subtask scope (Section 5). Sibling Subtasks run concurrently by design.
- **Per-Task PM.** When every Subtask of a Task is `done` and no `aborted-*` obligation at that Task's Subtask scopes is `open`, dispatch a fresh PM Agent at Task scope. The PM's Final report drives the routing table (Section 7); findings routed from it take Clause 1 of part (g).
- **Per-Task close-out.** When the Task's findings are all dispositioned, run Section 8.
- **Epic boundary.** When every Task of the Epic is `done`, run the inter-Epic interaction checkpoint, flip the Epic, classify the next branch, and run the boundary checkpoint (all in Section 8).
- **Bee-level reviews.** When every Epic is `done`, dispatch up to three concurrent reviewer Agents at Bee scope: `Agent(subagent_type="code-reviewer", run_in_background=true)` if any Engineer ran, `Agent(subagent_type="test-reviewer", run_in_background=true)` if any Test Writer ran, `Agent(subagent_type="doc-reviewer", run_in_background=true)` if any Doc Writer ran. Follow each review skill's routing trailer literally. Re-dispatch implementers and, when needed, a PM at Bee scope; you may choose NOT to spawn the PM on a minor iteration. Findings routed from this site take Clause 2 of part (g). The loop has not closed while any Bee-scoped `aborted-*` obligation is `open`. When the loop closes and every Bee-scoped lane is `closed`, proceed to Section 11.

## 5. Dispatch shape

Dispatch every role as `Agent(subagent_type=<role>, run_in_background=true, prompt=…)`. Never use `Agent(name=...)`, never reuse an Agent across scopes, never `SendMessage` between roles; the diff is the handoff. Subagents cannot spawn subagents, so every dispatch originates here. Before each dispatch add an `open` lane row with `dispatched: no`; set `dispatched: yes` when the call returns; never dispatch a role at a scope that already has an `open` row for it — wait when that row reads `dispatched: yes`, dispatch under that row when it reads `dispatched: no`.

Read the ticket via `bees show-ticket --ids <ticket-id>` and embed the body **verbatim** as a quoted block; never paraphrase or clean up identifier spellings. Framing prose around the block is fine, and it MUST NOT loosen the dispatched role's lane as `agents/<role>.md` states it. Surface the Plan Bee `title` verbatim to the Doc Writer. Pass the PM the Task ID, the completed Subtask IDs, the Grandparent Bee ID (on a Bee-scoped re-dispatch: the Bee ID and the Bee-level diff range in place of the Task and Subtask IDs), `<scoped-marker-resolver-path>` resolved as `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (PowerShell `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py`), and `<compromise-tracker-path>` — the path, never the contents. Give every reviewer its scope: a diff range, a ticket ID, or both.

| Heading | Source | Recipients | Fixed empty line |
|---|---|---|---|
| `## Source paths to fingerprint` | union of Engineer returns' `## Files changed` for the scope, test paths dropped | Test Writer | omit the heading when the union is empty or no list exists and `git diff --name-only HEAD` (the last-resort fallback, minus test paths) yields nothing |
| `## Engineer's completeness evidence` | every Engineer completeness list for the scope, verbatim, each attributed to its Subtask | PM (per-Task and Bee-scoped), Code Reviewer | omit the heading when no list arrived; always state separately that the assignment was sweep-shaped when it was; at Bee scope say a list `existed but is unavailable post-compaction` when that is so |

- Subtask-scoped Test Writer: the fingerprint set is the parent Task's union (`bees show-ticket --ids <subtask-id>` → `parent`; `bees show-ticket --ids <task-id>` → `children`), narrowed to the `up_dependencies`-named Subtasks only when the test Subtask's `up_dependencies` is non-empty. An explicitly-empty `## Files changed` is a list, not a missing one. The fallback fires only when no return in scope carried a list. Bee-scoped Test Writer: the union across every Engineer return behind the Bee-level diff.
- Writer prompts MAY state `"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running"` (Subtask scope) or `"no Engineer Agent will be dispatched for this Bee while you are running"` (Bee scope). They MUST NOT claim `"the source tree is frozen"`.
- Roles: `agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`. Role contracts live there; dispatch roles, do not carry their prose.

## 6. Gates

Every `AskUserQuestion` this skill fires is a gate. A gate is a manifest `Write` that fills `## Open gate` with the gate's name, scope, and choice labels verbatim, followed by `AskUserQuestion` in the same turn; this contract substitutes for the two-step gate contract a dispatched skill's routing trailer prescribes. The run-start gates that precede the manifest write — session effort, the pick gate, and isolation — fire `AskUserQuestion` directly; the `## Open gate` discipline begins at the manifest write. Do not narrate a gate; fire both calls. Gates are multi-choice only; never add fake free-text options duplicating the auto-appended `Type something.` / `Chat about this` slot. When the answer is consumed and the branch entered, rewrite `## Open gate` to `none`. Never end a turn with `## Open gate` filled but no question fired. Evaluate a gate's condition before writing `## Open gate`.

- **Session effort.** Read `printenv CLAUDE_EFFORT` (PowerShell `Write-Output $env:CLAUDE_EFFORT`). If empty, non-zero, or not one of `low` / `medium` / `high` / `xhigh` / `max`, skip silently. The floor is `medium`; the order is `low` < `medium` < `high` < `xhigh` < `max`; compare against the floor, never for equality. At or above: no gate, no output. Strictly below: question text: ``This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.`` then a blank line then `Subagent effort is pinned per role and is NOT affected by this setting.` Options: **Proceed anyway** — continue; **Let me change it first** — exit cleanly without dispatching anything; the user runs `/model` and re-invokes.
- **Bee pick.** Fires when several Bees are workable; one option per Bee. **Epic pick.** Fires from Section 4 step 6 when several Epics are workable: present the unblocked candidate Epics, one option per Epic, recommending the one with the fewest downstream dependencies.
- **Isolation.** Two scenarios. **Scenario A — Already in a worktree** whose directory name matches the Bee (e.g. `b_Wx7` for `b.Wx7`): proceed, no action. **Scenario B — On an existing branch in the main repo**: fire the gate. The question states the current working directory, the current branch name, and that option 1 creates a local branch only (no remote push). Options: **Create a feature branch (Recommended)** — create `bee/<bee-id>` from HEAD and work there; **Work on current branch** — commit to the checked-out branch and tell the user its name; **Set up a worktree instead** — offered only when `/bees-worktree-add` is installed; advise running it and exit without working.
- **Run mode.** Question: `How should this run handle multiple Epics? (You will not be asked again this run.)` Options: **Stop after each Epic** — Mode 1; **Work through all Epics** — Mode 2. Capture once for the run.
- **Inter-Epic continuation** (Mode 1 only). Question: `Epic <just-completed-epic-id> is done. Continue with the next logical Epic?` Options: **Continue** — checkpoint, guard, then the next Epic; **Stop here** — checkpoint, then the Bee-level reviews.
- **Unexplained movement.** Fires from the movement rung below when the movement cannot be attributed. The question carries the writer's movement report verbatim plus the statement *the orchestrator dispatched no Engineer for this unit while the writer was running, and no returned concurrently-dispatched Test Writer's `## Perturbations` list names the moved paths, so it cannot attribute the movement.* Options: **Re-dispatch the writer now** — next round against the current tree; **Wait** — yield; re-fire only on the operator's reply, never on a sibling lane's notification, which is processed normally; **Abort this unit** — leave every ticket at its current status and route through Section 12.
- **Routing (c)** and **routing (d)** — Section 7.
- **Deferral hygiene** — Section 9. **Post-completion disposition**, **SR-6.7**, **SR-4.6** — Section 11. **Context guard** — Section 8.
- **Final output.** Three gates: the ignored-feedback action gate (act on any item, or continue); per-Acceptance-Criterion sign-off; and the Bee-done gate, question `"Are you ready to mark this Bee as done?"`, options `"Yes, mark as done"` and `"No, we have more work to do"`.

**Movement rung.** A Test Writer or Doc Writer return that reports it *stopped* on detected source movement is not a completion; movement confined to a sibling Subtask's files is an observation the writer finishes on, and is persisted as a completion. On a movement report: mark the writer's lane `closed`; open an `aborted-*` obligation at the lane's scope with the "how far I got" report as detail; if the writer's Subtask was flipped `done` prematurely, run `bees update-ticket --ids <subtask-id> --status in_progress` (skip on a Bee-scoped lane, which has no Subtask). The unit does not advance while that obligation is `open`. Then attribute the mover: an Engineer → let its lane and, on a review-round mover, its code review close per part (g), then re-dispatch; a concurrently-dispatched Test Writer whose `## Perturbations` lists every moved path → re-dispatch once it has returned, no gate (do not classify while any dispatched Test Writer is still in flight; `None` or a partial list falls through); an external actor → re-dispatch once the tree has settled; unexplained → fire the gate. The re-dispatch is the next round at the same scope and carries the "how far I got" detail. A normal deliverable from the re-dispatched lane closes the obligation; a second abort refreshes the same obligation's detail, never opens another.

**Engineer-dispatch precondition.** Never dispatch an Engineer while a `## Lanes` row is `open` for a role and scope the applicable clause names. Clause 1 (per-Task site): `test-writer` or `doc-writer` at any Subtask of that Task (resolve a Subtask's parent with `bees show-ticket --ids <subtask-id>`), or `pm` at that Task. Clause 2 (Bee-level site): `test-writer` or `doc-writer` at any scope in the Bee, `code-reviewer`, `test-reviewer`, `doc-reviewer`, or `pm` at any scope. An `open` lane with `dispatched: yes` will notify — wait; an `open` lane with `dispatched: no` will not — dispatch it now or mark it `closed`, then re-check. When a row is absent or its `dispatched` value is unreadable, treat it as `no`. An `aborted-*` obligation never blocks an Engineer round. The forward per-Subtask fan-out is exempt; only re-dispatch rounds are ordered.

## 7. Routing discipline

### Orchestrator discipline: routing review findings

Each finding carries a severity tag, exactly one of `blocker` / `suggestion` / `nit`, and a depth tag on each fix path, exactly one of `trivial-tweak` / `refactor-locally` / `re-architect`, plus the count of fix paths. Turn them into exactly one routing decision per finding; never re-classify a depth tag. Definitions, shims (e) and (f), the anti-pattern (b), and all rationale live in the routing reference (Section 3); read it before routing when this section is not in view.

**Severity bounds the loop.** A review lane's loop — the Engineer → code-review loop at any review site, and each writer → reviewer pair — is held open by `blocker`- and `suggestion`-severity findings and by any `nit` whose chosen fix path is deeper than `trivial-tweak`; it closes when no such finding remains outstanding. A lane-holding finding stays outstanding until a later cold pass no longer raises it or it reaches a disposition under which **no fix lands against it** — accepted into the compromise tracker, recorded as a `defer-*` obligation, or closed by a gate answer of `Accept the limitation`, `Cancel`, or `Defer to follow-up Issue` when nothing ships against the finding this round; a dispatch settles nothing — whether ungated at row 6, chosen at a gate, or the soft fix or narrowing a deferral ships alongside itself — until a later cold pass has read its result. **A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own.** Batch those: when a finding that holds the lane open already forces another implementer round, they ride along in it and the next cold pass reads them with everything else; when only such nits remain, apply them in **one** final implementer pass for that lane and dispatch **no** further reviewer round for it — at a site where a review runs inside the PM's in-flight review passes rather than as a reviewer Agent of its own, that means do not re-dispatch the PM for that lane. Record the count per lane in the manifest's `## Rounds` and inside that lane's slot on the **Reviews** line of the summary for the scope that dispatched the review, as `N nits applied without re-review`; when the manifest carries no count for the lane render `count unavailable post-compaction` rather than guessing. These are finished work, so they are never listed as ignored feedback and never become `defer-*` obligations. A `nit` whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding — and **the bound keys on what ships**: when the gate's answer ships anything other than the enumerated `trivial-tweak` path (`Fix properly now` on a row-2, -3, or -4 fire, or the soft fix or narrowing a `Defer` ships alongside itself), the finding is lane-holding again, a cold pass must read that fix, and part (g)'s elision does not apply to it. When the final pass ships only such `trivial-tweak` paths and changes source, part (g)'s ordering applies with its code-review rung elided — that rung is the one round this rule suppresses. Severity keeps its meaning here — importance, orthogonal to depth — so the bound is the reviewer's own depth tag, not a narrower reading of `nit`. The coverage given up is exactly that class and no more: the cold pass that raised the nit already read the text it corrects, the fix is a `trivial-tweak` by the reviewer's own tag, and the post-completion review reads the whole diff, nit fixes included.

**(a) Pick the path, then route on it.** **Step 1 — pick.** Choose the highest-quality fix path among those the reviewer enumerated; `[preferred]` is an input, not a verdict, and when it marks a narrowing take the fuller complete path. The pick is always one of the enumerated paths. **Step 2 — route on the path chosen in Step 1.** Evaluate in order; first match wins.

| # | Condition (evaluated in order, first match wins) | Routing |
|---|---|---|
| 1 | The finding carries no depth tag, or a malformed severity/depth tag | Treat as `re-architect` → gate (d) |
| 2 | The chosen path carries the reviewer's `[introduces-mechanism]` tag, or introduces a mechanism by the orchestrator's own reading | Scope-bounding gate (c) |
| 3 | The chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers | Scope-bounding gate (c) |
| 4 | The chosen path is narrower than the smallest internally-consistent complete fix — it leaves the stated defect partly unfixed | Scope-bounding gate (c) |
| 5 | The chosen path's depth tag is `re-architect` | Routing-decision gate (d) |
| 6 | Otherwise | Dispatch the chosen path, no gate |

Row 6 dispatches a fresh implementer per Section 5 with the chosen path in full and appends a Trigger C entry (Section 10) in the same block, except when the finding's only path is `trivial-tweak`.

**(c) Scope-bounding gate.** Fires on rows 2, 3, and 4, and whenever the orchestrator would otherwise scope-bound a finding. The question carries the finding verbatim plus one line naming the entry condition. For a `suggestion` or `nit` the choices are `Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`; on a row-2 fire mark `Defer to follow-up Issue` `(Recommended)`. **Blocker rules:** `Accept the limitation` is never offered to a `blocker`. A `blocker` always gets its base pair; `Defer to follow-up Issue` is added only when the needed fix path introduces a mechanism AND that mechanism serves a case outside the stated defect, and then only paired with a narrowing dispatched after `/quo-file-issue` returns an Issue ID, marked `(Recommended)`. `Fix properly now` re-dispatches the implementer to address the finding fully. `Defer to follow-up Issue` files via `/quo-file-issue` inline through the Skill tool, carrying the reviewer's sketched design verbatim, then ships the soft fix (Trigger A). `Accept the limitation` records the compromise (Trigger B) and proceeds.

**(d) Routing-decision gate.** Fires on rows 1 and 5. The question carries the finding verbatim. Choices: one per reviewer-surfaced fix path, its description carrying the path's depth tag, `(Recommended)` on the Step-1 pick; `Defer to follow-up Issue` — file via `/quo-file-issue` inline through the Skill tool carrying the finding verbatim, and ship no path this round (Trigger A); `Cancel`. A `blocker`'s `Defer` is offered only under gate (c)'s two conditions, on gate (c)'s terms.

| Divergence | `/quo-fix-issue` | `/quo-execute` |
|---|---|---|
| Approved-design source for "introduces a mechanism" | the `## Authoritative design directive` block from the Analyst gate | the Subtask body, its parent Task body, and the PRD/SDD the Plan Bee's `reference_materials` resolves to, or the Plan Bee body when null/empty |
| Blocker base pair at gate (c) | `Fix properly now` + `Re-dispatch the Analyst with this finding` | `Fix properly now` + `Cancel` |
| `Cancel` at gate (c) | none; `Ctrl-C` remains the run-level abort | in the `blocker` set only; ends the run via Section 12 |
| Gate (d) non-deferrable `blocker` set | per-path list + `Re-dispatch the Analyst with this finding` + `Cancel`; on an empty list mark the Analyst choice `(Recommended)` | per-path list + `Cancel`; on an empty list the question says the reviewer enumerated no fix path and the user directs the fix in free text or cancels |
| Gate (d) `Cancel` semantics | ends the current Issue; Section 12's mode branch decides the run | ends the run via Section 12 |
| Filing-failure re-prompt `Cancel` | at gate (d) only | at either gate on a `blocker`, at gate (d) otherwise |
| Part (g) code-review rung | the Code Reviewer, one clause | Clause 1: the per-Task PM's in-flight `/quo-engineer-review` pass; Clause 2: the Bee-level Code Reviewer |
| Close-out target on `Cancel` / abort | `#### Aborted-Issue close-out` | `#### Aborted-run close-out` |

**(g) Re-dispatch ordering when a fix path changes source.** Dispatch the Engineer first, then the code review for that site against the resulting diff, and only once that review has closed dispatch the Test Writer and/or Doc Writer the change invalidated — ordered, not concurrent, and gated by the Engineer-dispatch precondition (Section 6). One elision: on the final `trivial-tweak` nit pass, skip the code-review rung and dispatch the affected writer once the Engineer returns. A path that changes no source file re-dispatches that single writer lane alone.

Follow the review skills' routing trailer literally — `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`. When you ignore a finding, record it at that moment as a `defer-*` obligation with exactly one destination: `addressed-now`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue`; an `addressed-now` item enters no ledger. A PM report note with no severity and no fix path is not a finding and is not routed. A missing-completeness-list finding on a dispatch whose list a compaction destroyed is a compaction artifact: list it under `**Ignored Review Feedback**`, create no obligation, dispatch nothing.

## 8. Per-unit close-out

**After each Task.** When the Task's Subtasks are `done` and every finding is dispositioned: mark the Task `status=done` (flip doc Subtasks on the Doc Writer's behalf); run the `Format` command from `## Build Commands` — the only rung the orchestrator runs, never the test suite, and with the Bash `timeout` parameter when long; run `git status`; stage agent-reported files plus formatting changes to files this Task's agents touched; resolve the in-repo Plans hive path with `python3 "<this skill's base directory>/scripts/hive_commit.py" resolve-hive-paths --hive plans` (PowerShell `python "<this skill's base directory>\scripts\hive_commit.py" resolve-hive-paths --hive plans`) and stage it when it prints one; **Do NOT blindly `git add -A`**; commit once with subject `Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)` (the `N` and `M` ordinals come from the ticket titles; omit `Plan <bee-id>, ` for a standalone Epic). **NEVER push to remote — committing only.** Mark every lane and `aborted-*` obligation at this Task's scopes `closed`. Output:

```markdown
## Task [N] of [total] Complete: [task-title]

**Task ID**: <task-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed — each slot carrying its own `N nits applied without re-review` (or "count unavailable post-compaction") when any]
**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]
**Second-order effects**: [the relayed `### Second-order effects` narrative]
**Follow-up Tasks Created**: [count, if any] [list task-ids if created]
One of:
- Proceeding to next Task: [next-task-title]
- Final Task, moving on to Final Reviews
```

`**Second-order effects**` is unconditional and is narrative, not routing input — it never holds a lane open and never becomes a finding: collect the PM Final report's `### Second-order effects` with its `#### <invocation scope>` sub-blocks, render bullets verbatim, keep the labels, de-duplicate exact repeats, and render `None identified.` when every source said `No second-order effects identified.` or none ran. Record every PM-deferred item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` as a `defer-*` obligation now.

**Epic boundary.** When every Task of the Epic is `done`:

1. **Inter-Epic interaction checkpoint.** Resolve `<previous-epic-last-commit>` from the manifest: `**Pre-Bee SHA:**` at the first boundary, the previous Epic's `last commit <sha>` under `**Progress:**` after. Run `git log --oneline <previous-epic-last-commit>..HEAD`. Compute the overlap-file list: files in `git diff --name-only <previous-epic-last-commit> HEAD` that also appear in `git diff --name-only <pre-bee-sha> <previous-epic-last-commit>`. When the overlap list is non-empty, dispatch a fresh `code-reviewer` Agent at Epic scope whose review scope is the commit range plus the overlap-file list, asking it to check **Contract drift**, **Resource compounding**, and **Symmetric-change gaps** against the prior Epics' code. Route its findings through Section 7: they take Clause 2 of part (g), this reviewer is that site's code-review rung, and the Engineer-dispatch precondition applies with Clause 2's roles; fixes land as additional commits on the branch. This lane's batched-nit count and its relayed `### Second-order effects` render in the Bee-level code review slot of `## Bee Execution Complete` (Section 13); a `Cancel` routed from it enters Section 12 at Epic scope. At the first boundary, or with an empty overlap list, there is nothing to dispatch.
2. Mark the Epic `status=done`, re-query every Epic with the Section 4 step 6 query, and classify in order:
   - **Drafted (or blocked-on-drafted) Epics remain** → print `Epic <just-completed-epic-id> is complete, but Epics <drafted-or-blocked-ids> in this Bee are still drafted (or blocked on drafted dependencies) and need breakdown before this Bee can be closed. Run /quo-breakdown-epic <bee-id> (a fresh session is reasonable to keep context clean) to break down the remaining Epics, then re-run /quo-execute <bee-id>.`, run the checkpoint with next unit `none`, and exit.
   - **Workable Epic remains** → select the next Epic by the Section 4 step 6 rule (in Mode 2 take the recommended Epic without the Epic-pick gate). When no mode was captured, record `**Multi-Epic run mode:**` as `captured late` and take the Mode 1 arm. Mode 1: fire the continuation gate; Mode 2: print `Mode 2 (Work through all Epics): auto-continuing to <next-epic-id> — <title>.` Mode 2 skips only the continuation gate; the drafted-or-blocked stop above and a `Cancel` at a routing gate (Section 12) still halt the run. Then the checkpoint with next unit = the selected Epic, then the guard, then Section 4 step 8.
   - **All Epics under this Bee are `done`** → checkpoint with next unit `none`, then the Bee-level reviews.

#### Epic-boundary state-externalization checkpoint

A definition, not a step; run it only where a branch above, or Section 12, calls for it, always after the branch classification above has resolved. It verifies that every load-bearing fact lives in a durable carrier and refreshes them; it does not clear, compact, or reclaim context, and must never be narrated as if it did.

1. Verify: (a) the just-completed Epic and its Tasks and Subtasks read `done` in bees; (b) `git log --oneline <previous-epic-last-commit>..HEAD` shows one commit per completed Task; (c) `Read` the tracker at the manifest's `**Compromise tracker:**` path and confirm every compromise accepted this Epic has an entry — an absent file is a gap only when an entry was owed; (d) every `## Lanes` row from this Epic is `closed` and `## Open gate` reads `none`; (e) the manifest's `**Unit scope:**` names this Bee. Fix any gap now. On the aborted path at mid-Epic scope, (a) and (b) invert: confirm the statuses the abort left and count only completed Tasks' commits; at Epic-boundary scope only the Epic's own status inverts — it stays `in_progress` while its Tasks are `done` and committed; at Bee-level scope nothing inverts. When the run started with every Epic `done`, skip (a)–(d) and verify only that the placeholders were resolved.
2. Rewrite the manifest per Section 2: the Epic's `**Progress:**` line and `**Next unit:**`.
3. Re-read, do not recall, at every dispatch in the next Epic: `bees show-ticket` the ticket and `Read` the manifest. If a needed fact is not in a carrier, write it into one before dispatching.

#### Epic-boundary context-window guard

Runs only on the two continuing paths (Mode 1 **Continue**, Mode 2 auto-continue), after the checkpoint and before the next Epic. Rationale and the gauge contract live in the context-guard reference (Section 3). The resume command is `/quo-execute <bee-id>`.

1. Read `printenv CLAUDE_CODE_SESSION_ID` (PowerShell `Write-Output $env:CLAUDE_CODE_SESSION_ID`); trim trailing whitespace. Unset or empty → skip silently, record `**Context guard:** not run`.
2. Obtain the threshold: `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold` (PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold`). Never restate the number in prose.
3. Read: `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>` (PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" read --session-id <trimmed-session-id>`).
4. Branch. Integer ≥ threshold → record `<integer>% at <epic-id>` and fire the context-guard gate: the question reports the percentage, states the run is at a clean boundary with every carrier on disk, and names the resume command; options **Stop here** (Recommended) — exit the skill with that resume command; **Proceed without the guard (this run)** — continue. Integer < threshold → record `<integer>% at <epic-id>`, continue. `no-reading` → record `no reading`, continue. `stale`, non-zero exit, or empty stdout → STOP: report that the producer appears stalled or the reading is untrustworthy, recommend a fresh session with the resume command, exit. `missing` → record `no reading`, continue silently, whether or not `<tempdir>/.quorum/context-guard-opt-out` exists.

## 9. Deferral hygiene

Fires once, after Section 11's post-completion review is complete and before Section 13. Every `AskUserQuestion` here is a gate per Section 6.

- **Step 0 — Retroactive ledger reconciliation (safety net).** Walk every per-Task summary's `**Ignored Review Feedback**`, every PM Final report's deferred items, and any orchestrator-side ignore; create a `defer-*` obligation for any item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` that lacks one; skip `addressed-now` items.
- **Step 1 — Enumerate the active deferral ledger.** The active set is every `defer-*` obligation with status `open`. Empty → print `Deferral hygiene: no deferred items.` and proceed.
- **Step 2 — Surface the active set and gate the user choice.** Print the set as a numbered list, one bullet per obligation with its detail, then fire the gate: `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body`. Per-item routing uses the auto-appended free-text slot; this is the one gate where free text is the primary path.
- `Fix in this session`: dispatch the implementer or reviewer per Section 5, or update the ticket body inline; close each obligation with its resolution in detail.
- `File as issue tickets`: invoke `/quo-file-issue` inline through the Skill tool per item with the description as the body; close the obligation when an Issue ID returns.
- `Encode in an existing ticket body`: destinations are a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass. Append `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` to the body, the timestamp authored from your own clock, the stem kept verbatim. `mkdir -p /tmp/.quorum` (PowerShell `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null`), `Write` the revised body to `/tmp/.quorum/bees-body-<defer-N>.md` (`$env:TEMP\.quorum\bees-body-<defer-N>.md`), e.g. `bees-body-defer-3.md`, then `bees update-ticket --ids <ticket-id> --body-file <path>`. Never delete the scratch file. Close the obligation when the update succeeds.
- After all Encode writes, one follow-up commit per firing, with `<resolved-helper-path>` = `<this skill's base directory>/scripts/hive_commit.py` (PowerShell `<this skill's base directory>\scripts\hive_commit.py`): `python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]` (PowerShell `python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]`); `<N>` counts items, one `--doc-path` per PRD/SDD file routed to, each path resolved from CLAUDE.md `## Documentation Locations`. It commits `Encode deferral: /quo-execute — <N> deferral(s) encoded` or prints `skipped: nothing staged`.
- **Step 3 — Hard-stop on a non-empty active set.** Do not advance while any `defer-*` obligation is `open`. If a branch fails to close a subset, surface the remainder with a fresh gate and repeat.

## 10. Compromise tracker

#### Session-scoped compromise tracker

One markdown file per run at `<tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` (`/tmp/.quorum/` POSIX, `%TEMP%\.quorum` Windows), the UTC timestamp and random suffix generated once at run start and recorded in the manifest. Create `.quorum` if absent (`mkdir -p /tmp/.quorum`; PowerShell `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null`), author and append via `Write`, never delete, never append to a previous run's file. Each accepted compromise appends one entry; `<n>` is a 1-based counter within this file. Rationale and edge cases live in the compromise-tracker reference (Section 3).

```markdown
## Compromise <n>

- **Finding (verbatim):** <severity tag> <fix-path enumeration with depth tags> <description>
- **Fix paths surfaced by reviewer:**
  - (a) [depth:<depth>] <description>
  - (b) [depth:<depth>] <description>
- **Decision:** <one of: User picked path (a) | User picked path (b) | ... | User picked Defer to follow-up Issue | User picked Accept the limitation | Orchestrator picked path (x) — highest-quality | User overrode auto-route after post-completion challenge (depth misjudgment) | User accepted under-enumeration after post-completion challenge>
- **Rationale:** <the user's stated reason, or on an ungated pick the orchestrator's one-line reason; on a deferral which path shipped as the soft fix, or none did, or the narrowing record on a blocker>
- **Follow-up Issue:** <ticket ID if filed via /quo-file-issue, else `none`>
```

#### Compromise-tracker append triggers

| Trigger | Moment | Decision | Rationale content | Follow-up Issue |
|---|---|---|---|---|
| **Trigger A — Defer to follow-up Issue at either gate.** | immediately after `/quo-file-issue` returns, before the soft-fix or narrowing dispatch | `User picked Defer to follow-up Issue` | which remaining path shipped, or none did; on a `blocker` the narrowing record | the new Issue ID |
| **Trigger B — Accept the limitation at the scope-bounding gate.** | immediately after the answer, before continuing without a fix; unreachable for a `blocker` | `User picked Accept the limitation` | the user's reason | `none` |
| **Trigger C — ungated route (the orchestrator's own path pick).** | in the same block as a row-6 dispatch; nothing when the only path is `trivial-tweak` | `Orchestrator picked path (x) — highest-quality` | the orchestrator's one-line reason, not a rule name | `none` |
| **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).** | `Accept …` → append a new entry immediately after the pick; `File …` → update the originating Trigger C entry's `Follow-up Issue` in place, or append when none exists (SR-4.6); `Pause to discuss` → no write | `User overrode auto-route after post-completion challenge (depth misjudgment)` (SR-6.7) or `User accepted under-enumeration after post-completion challenge` (SR-4.6) | the reviewer's challenge text | the new Issue ID on `File …` |

## 11. Post-completion review

Scope: `git diff <pre-bee-sha>` (the working tree against the pre-Bee commit) plus every untracked file from `git ls-files --others --exclude-standard`; a change no ticket body asks for is reported as likely pre-existing or an unticketed in-run edit, as an inference. `Read` the manifest for `<pre-bee-sha>` and `<compromise-tracker-path>`; if the manifest is missing or names another unit, stop and tell the user rather than guessing the scope.

1. `Read` the post-completion prompt reference (Section 3), fill its parameters (`<unit-noun>` = `Bee`), and dispatch one fresh `Agent(subagent_type=general-purpose, run_in_background=true, prompt=…)` with the skeleton verbatim. Do not review the run yourself; do not invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review`. Wait for its report.
2. Synthesize: compare its findings against the in-flight PM and reviewer verdicts and flag disagreements explicitly. When any `[compromise-challenge]` finding is present, lead with a `⚠️` preamble, e.g. `⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below.`
3. `no issues found` → print `Post-completion review: no issues found`; this section is complete.
4. Otherwise fire the disposition gate: `Post-completion review found [N] issues. How would you like to handle them?` Options: **Fix in this session**, **File as issue tickets**, **Skip**. Recommend `Fix in this session` when a PHASE 2 contract-violation `blocker` is present; that class has no recovery gate.
5. For each PHASE 3 or PHASE 4 `[compromise-challenge]`, in the reviewer's emission order, fire its recovery gate before or alongside the disposition. **SR-6.7 ungated-route recovery gate.** Choices: `File follow-up Issue to revisit the depth decision` — `/quo-file-issue` via the Skill tool with the finding and the tracker entry, then Trigger D's in-place update; `Accept the misjudgment and proceed` — Trigger D append; `Pause to discuss` — stop and discuss; the user re-issues a choice. **SR-4.6 under-enumeration recovery gate.** Choices: `File follow-up Issue to surface the missing path`; `Accept the under-enumeration and proceed`; `Pause to discuss`; same branch behavior.
6. **Fix in this session**: per-unit rules apply with `postcomp-<n>` as the unit, `<n>` the finding's 1-based index: lanes at scope `postcomp-<n>`, the movement rung, the Engineer-dispatch precondition across every `postcomp-*` scope, part (g) ordering within a finding, independent findings concurrent. An abort of a post-completion lane closes its rows here and continues this section; it never enters Section 12. When every lane is `closed` and no `aborted-*` obligation at a `postcomp-*` scope is `open`, commit. **File as issue tickets**: `/quo-file-issue` per finding; report the IDs. **Skip**: continue.

When this section is complete, proceed to Section 9, then Section 13.

## 12. Aborted-unit close-out

#### Aborted-run close-out

Entered from **Abort this unit** or from `Cancel` at either routing gate. A definition, not a step; run it only when a branch names it. The run stops without the unit advancing.

1. Mark `closed` every lane and `aborted-*` obligation at the aborted scope — the Task and its Subtask scopes on a mid-Epic abort, the Epic scope on an inter-Epic-checkpoint abort, every Bee scope on a Bee-level abort — recording the abort reason in each `aborted-*` obligation's detail. An in-flight sibling lane cannot be terminated; mark it `closed` anyway.
2. Run the checkpoint (Section 8) on its aborted path with `**Progress:**` `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`, `<epic-id>: aborted at the inter-Epic checkpoint — last commit <sha>`, or `<bee-id>: Bee-level review aborted — <what stopped it>`, and next unit `none`.
3. Run `git status --porcelain`. Tell the user which Subtask and Task, which inter-Epic-checkpoint finding, or which Bee-level lane or review site and finding, the run stopped in; name the uncommitted paths; name the resume command `/quo-execute <bee-id>`; exit. Do not run the context guard here. `Ctrl-C` remains the unconditional run-level abort.

## 13. Final output

1. Show the user every reviewer finding you ignored and fire the ignored-feedback action gate. Demonstrate each Acceptance Criterion or say how to validate it, and fire the sign-off gate. Fire the Bee-done gate; on `"No, we have more work to do"` stop here.
2. Re-query the Epics with `bees execute-freeform-query --query-yaml 'stages:\n  - [parent=<bee-id>, type=t1]\nreport: [title, ticket_status]'`. If any is not `done`, abort with `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.`; never bulk-flip. Otherwise `bees update-ticket --ids <bee-id> --status done`.
3. Print the summary. `**Second-order effects**` is unconditional, rendered from every Bee-scoped and Epic-boundary Code Reviewer return and any Bee-scoped PM as in Section 8. `**Accepted compromises**` is rendered only when the tracker has `## Compromise <n>` entries — `Read` it at the manifest's path; this surface only reads the tracker, never writes it: one bullet per entry with `Finding (verbatim)`, `Decision`, `Rationale`, and `Follow-up Issue`, never `Fix paths surfaced by reviewer`, all entries in full, prefaced by `N compromises were accepted during this run:` when more than ten. Run `git status --porcelain` and add the uncommitted sentence only when it lists something.

```markdown
## Bee Execution Complete: [bee-title]

**Bee ID**: <bee-id>
**Epics Completed**: [count]
**Tasks Completed**: [count]
**Bee Status**: Finished
**Reviews**: [Bee-level code review: X issues found/None needed | Test review: Y issues found/None needed | Docs review: Z issues found/None needed — each slot carrying its own `N nits applied without re-review` (or "count unavailable post-compaction") when any]
**Second-order effects**: [the relayed `### Second-order effects` narrative from the Bee-level and Epic-boundary reviews]
[**Accepted compromises** — rendered when the tracker has entries, or OMITTED ENTIRELY]

All per-Task work has been committed. [When `git status --porcelain` lists anything: "Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing."]
```

4. Invite the user to perform whatever further testing they want, then give merge advice per the isolation strategy, after the user commits what belongs to this Bee: **Worktree** — `/bees-worktree-rm` if installed, else `git merge <branch>` from the parent repo then `git worktree remove <path>`; **Feature branch** — `git merge bee/b.Wx7` or open a PR; **Worked on main/current branch** — the work is committed locally; push when ready. Never push.
