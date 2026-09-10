---
name: quo-fix-issue
description: Fix an issue described in a Bee ticket. Use '/quo-fix-issue all' to fix all open issues sequentially, or '/quo-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset.
argument-hint: "[<issue-id> | <url> | <id-or-url> ... | all]"
---

## 1. Preconditions

Before anything else, verify the host repo is configured for quorum. **Hard-fail** with `Run /quo-setup first.` plus a one-line note of what is missing if any item below is absent. Do not improvise commands or guess paths.

- The eight custom subagent types are registered in this session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`. Custom subagents load at session start; a fresh install needs a Claude Code restart or `/agents` to hot-reload. Verification rides on the first dispatch: an `Agent type '<name>' not found` error from the Agent tool for any of the eight STOPS the run with `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` Never fall back to `general-purpose` as a substitute for a missing role, never skip the dispatch, never improvise a substitute role.
- The Issues hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `issues`.
- The Specs hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section; roles read doc paths from it by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`; roles read commands from it by exact key.

## 2. Run-state manifest

#### Write the run-state manifest

This is the canonical definition site for the run-state manifest; later sections refer to it by name. Write it at the end of run start (Section 4), once the working list is validated and the isolation strategy is settled and before any Issue is validated or fixed.

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds ticket state, git holds the diff, and the compromise tracker holds accepted compromises; the manifest holds only what those three do not — including the run's lanes, obligations, rounds, and open gate. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `run-state-quo-fix-issue-<repo-dir-name>.md`, where `<repo-dir-name>` is the basename of the working tree root from `git rev-parse --show-toplevel` (identical on POSIX and PowerShell); a run inside `/home/dev/projects/widget-api` writes `run-state-quo-fix-issue-widget-api.md`. Create the `.quorum` directory if it does not exist, then author the manifest via the `Write` tool, never a shell redirect, and never delete it.

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write the manifest to /tmp/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write the manifest to $env:TEMP\.quorum\run-state-quo-fix-issue-<repo-dir-name>.md via the Write tool
```

**The filename is deterministic — do NOT add a random suffix or timestamp.** The manifest's reader is the orchestrator itself after a possible compaction, so the path must be recomputable, not remembered. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends: `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has, while `/quo-fix-issue` — whose batch membership is only recoverable from inside the manifest itself — appends the repository directory basename instead. Accepted collisions: two concurrent runs in the same working directory share one file, as do two checkouts whose directories share a basename; a `**Unit scope:**` naming Issues this run is not fixing is the foreign-manifest tell.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it fresh at run start, rewrite it at every boundary checkpoint, and rewrite the `## Lanes`, `## Obligations`, `## Rounds`, and `## Open gate` sections at the moment each changes. The manifest carries **only values that have no other durable home**; do not add Issue bodies, design directives, review findings, or anything readable from bees, git, or the tracker.

```markdown
# Run state — quo-fix-issue @ <repo-dir-name>

- **Skill:** quo-fix-issue
- **Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>
- **Unit scope:** ordered Issue batch: <issue-id-1>, <issue-id-2>, ...
- **Isolation strategy:** <branch created: <name> | current branch: <name> | worktree: <path>>
- **Pre-session SHA:** <pre-session-sha>
- **Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md
- **Context guard:** <no reading | <integer>% at <issue-id>>
- **Progress:**
  - <issue-id>: done — commit <sha>
- **Next unit:** <next-issue-id | none>

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

- `**Pre-session SHA:**` is captured once, here, with `git rev-parse HEAD` (identical on POSIX and PowerShell); Section 11 reads it back from this file.
- `**Compromise tracker:**` records the tracker's full path including its random `<short-suffix>`, generated here per Section 10; recording the path does not create the file.
- `**Context guard:**` is written only by the guard (Section 8); omit the line until then. Its percentage is an operator-facing record, not a routing input.
- `**Unit scope:**` records the post-resolution working list verbatim, in the user's order; that order is intentional and cannot be re-derived from bees.
- `**Progress:**` carries one line per finished Issue in the order worked: `<issue-id>: done — commit <sha>` or `<issue-id>: aborted — no commit; Issue left open`.
- `## Lanes` holds one row per dispatched Agent: `role` is the subagent type, `scope` is the Issue ID it works (`postcomp-<n>` for a post-completion lane), `round` is the 1-based dispatch count for that role at that scope, `dispatched` is `no` until the `Agent(...)` call returns and `yes` after, and `status` is `open` or `closed`. A lane is `closed` when its Agent is gone — a completion notification was processed, a movement report was received, or the run ended — whether or not its work shipped. An `open` row with `dispatched: yes` will notify — wait for it; an `open` row with `dispatched: no` has no Agent behind it — dispatch it now or mark it `closed`; a row that is absent or whose `dispatched` value is unreadable reads as `no`. Never dispatch a role at a scope that already has an `open` row for it.
- `## Obligations` holds one row per owed action: kind `defer-*` (id `defer-<n>`, detail = one-line description plus destination), and kind `aborted-*` (id `aborted-<role>`, detail = the writer's "how far I got" report). Status is `open` or `closed`. Detail is informational; routing reads only kind, scope, and status.
- `## Rounds` holds one row per lane (scope and role) carrying the count of `trivial-tweak` nits applied in that lane's final implementer pass without a further reviewer round (Section 7); `round` in `## Lanes` counts dispatches, `## Rounds` counts nits.
- `## Open gate` names the gate about to fire, its scope, and its choice labels verbatim, or `none`.
- The manifest carries lane phase and obligations; an earlier rule forbade the manifest a lane-phase field, and that rule is withdrawn.
- Validate the manifest before trusting any field: its `**Unit scope:**` must match this run's batch. A manifest naming other Issues is treated as absent: trust no field in it. If this run's own `**Pre-session SHA:**` or `**Compromise tracker:**` value is no longer readable, stop and tell the user before touching the file. Otherwise rewrite every field — `**Unit scope:**`, `**Isolation strategy:**`, `**Pre-session SHA:**`, `**Compromise tracker:**`, `**Progress:**`, and `**Next unit:**` — from this run's own state, and empty `## Lanes`, `## Obligations`, `## Rounds`, and `## Open gate`.

## 3. After a compaction

If a summarization marker is visible in the conversation, treat everything before it as non-authoritative. `Read` the manifest and re-read bees and git in full before dispatching anything. Before routing a finding, `Read` the routing reference; before dispatching the post-completion reviewer, `Read` the post-completion prompt reference. Never act on the summary. Conversation memory is never a substitute for these sources, on every tick, not only after a compaction. If `## Open gate` is not `none`, re-fire that gate from its recorded choices before anything else.

One exception: when `## Open gate` names the Analyst gate, the proposal it asks about is gone, so rewrite `## Open gate` to `none` and re-derive the proposal per Section 4 instead of re-firing; the abandoned question is asked again at the re-derived gate. The Design Proposal has no durable carrier by design; when it is needed and no longer readable, re-derive it through the Analyst (Section 4), never from a summary.

`<this skill's base directory>` is the path shown in the skill invocation header; sibling skills' `references/` and `scripts/` are reached from it through `..`.

| Reference | Path (POSIX; PowerShell uses `\`) |
|---|---|
| routing | `<this skill's base directory>/../quo-execute/references/routing.md` |
| post-completion prompt | `<this skill's base directory>/../quo-execute/references/post-completion-prompt.md` |
| compromise tracker | `<this skill's base directory>/../quo-execute/references/compromise-tracker.md` |
| context guard | `<this skill's base directory>/../quo-execute/references/context-guard.md` |
| rationale | `<this skill's base directory>/../quo-execute/references/rationale.md` |
| URL resolution | `<this skill's base directory>/references/url-resolution.md` |
| GitHub close | `<this skill's base directory>/references/github-close.md` |

## 4. The loop

The orchestrator performs mechanical steps that produce a tool artifact directly — git queries, manifest reads and writes, bees status flips, helper invocations; it dispatches every step that is a judgment over file contents or a review. Dispatch is by fresh, ephemeral background `Agent` invocations against the sibling `agents/` subagent types; there is no long-lived team, no warmed Agent, and no peer-to-peer messaging.

### Run start

1. Run the session-effort gate (Section 6) first, once.
2. Parse the argument string: split on any run of commas and/or whitespace and discard empty tokens. A token starting with `http://` or `https://` is a **URL token**; anything else is a **ticket-ID token**. Six forms: zero tokens → query open Issues, fire the Issue-pick gate (Section 6), fix that one Issue and exit; exactly `all` → query open Issues, sort by ticket_id, fix each in turn without confirmation; one ticket-ID token → single-issue mode; one URL token → file it via the URL-resolution reference, then fix the resulting Issue; two or more tokens → list mode, fixed **in the order given**, never sorted, never deduplicated, no confirmation between Issues. Open-Issue query: `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'`.
3. Run the isolation gate (Section 6).
4. When any URL token is present, run the URL-resolution reference's procedure; it substitutes each resolved `issue_ticket_id` in place.
5. Validate the post-resolution list with `bees show-ticket --ids <id1> <id2> ...`. Drop any ID that does not exist, is not in the `issues` hive, or is not `open`, report it, and continue with the valid subset. Only when no token remains valid after URL resolution and this pass does the run exit with an error.
6. Write the run-state manifest (Section 2).
7. **Take the next Issue in order and validate it** (the Issue boundary returns here): `bees show-ticket --ids "<issue-id>"`; status must be `open`; every `up_dependencies` entry must be `done`, batch-looked-up with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`; no `up_dependencies` means unblocked. If blocked, print the blocking IDs and titles; in batch mode skip to the next Issue; in single mode exit with `Cannot start Issue. It is blocked by: [list]`. Issues have only `open` and `done`; set no status here.

### Tick

Each tick is event-driven, never clock-driven, and has three phases.

1. **Read state.** Pull the truth from three sources: bees (`bees show-ticket --ids <issue-id>` for the body and `ticket_status`; `bees execute-freeform-query --query-yaml '<yaml>'` for any focused query, e.g. `stages:\n  - [id=<issue-id>]\nreport: [title, ticket_status]`), git (the diff on disk is the only authoritative record of what workers did), and the manifest (`Read` it; its `## Lanes` and `## Obligations` are the in-flight state).
2. **Reconcile.** Compare current state to the target state and act per the phase ladder below. For every Agent that reported completion: read its return before persisting anything, confirm any bees transitions it committed to, mark its lane `closed`, and unlock what its return unlocks. A writer return that reports it *stopped* on source movement is not a completion; route it through the movement rung in Section 6. An Engineer return carrying `## Design question` is not a completion; route it through the design-question rung below.
3. **Yield.** After dispatching this tick's work, return control and wait for the Agent completion notification the `run_in_background=true` substrate delivers; that notification is the only trigger for the next tick. Never use `/loop`, `ScheduleWakeup`, or `CronCreate`, and never poll bees, git, or the manifest on a sleep-wait cycle.

### Phase ladder

- **Analyst.** Always, for every Issue, dispatch one `Agent(subagent_type=analyst, run_in_background=true, prompt=…)` carrying the Issue ID, the body verbatim, and the `reference_materials` JSON when non-empty; the Analyst fetches upstream content itself. Never pre-judge a body as "well-researched enough" to skip it. Wait for its return, mark its lane `closed`, then run the Analyst gate (Section 6).
- **Phase A — source to clean.** When the approved directive needs source changes, dispatch the Engineer alone. On its return dispatch the Code Reviewer alone against the diff, unless the return carries `## Design question`. Loop Engineer → Code Reviewer until the Code Reviewer emits `No code issues found.` with an empty numbered list, or every remaining finding is dispositioned per Section 7. A non-empty `### Second-order effects` narrative beside a clean list does not hold Phase A open; carry it to the summary. When no source change is needed, Phase A is empty.
- **Phase B — writers once, in parallel.** After Phase A closes, dispatch the Test Writer (when tests need changing) and the Doc Writer (always) concurrently. This is the only forward-path dispatch of the writers.
- **Phase C — remaining reviewers plus PM.** When the Phase B writers have returned and no `aborted-*` obligation at this Issue is `open`, dispatch concurrently: `Agent(subagent_type="test-reviewer", run_in_background=true)` if the Test Writer ran, `Agent(subagent_type="doc-reviewer", run_in_background=true)` if the Doc Writer ran, and `Agent(subagent_type="pm", run_in_background=true)` always — **PM is the exception to the conditional-spawn rules.** The Code Reviewer is not dispatched again here. Follow each review skill's routing trailer literally. A Phase C finding that changes source re-enters Phase A per part (g), then re-dispatches only the writer lanes the change invalidated and their reviewers, plus the PM when spec alignment needs another pass against the updated diff (on a minor iteration you may choose not to re-dispatch it); a finding confined to a writer's lane re-dispatches that writer alone.
- **Design-question rung.** On an Engineer return carrying `## Design question`: mark the lane `closed`, dispatch no Code Reviewer, and re-dispatch the Analyst with the Revise shape carrying the question verbatim in place of user feedback, a statement that a partial implementation is on disk naming the Engineer's `## Files changed`, and that the revised `### Blast radius` must cover the new mechanism's lifecycle. Then run the Analyst gate unchanged; on Approve, re-dispatch the Engineer against the current working tree with the revised directive.
- **Re-derivation shape.** When the proposal is needed and unreadable, dispatch the Analyst with: the body re-read from bees and the same `reference_materials`; the changed-file list on disk — the latest `## Files changed`, or `git diff --name-only HEAD` minus test paths — an empty list meaning nothing has landed; and a plain statement that the prior proposal was lost to a compaction and the Analyst re-derives from the codebase as it stands, or that no proposal was produced yet when this is the first pass. Resume the ladder from the manifest's lanes: an `open` analyst lane → wait for its return and run the Analyst gate, reviewing nothing meanwhile; no Engineer lane → Phase A's entry; Engineer lane but no writer lane → re-dispatch the Code Reviewer with the re-derived `## Blast radius`; otherwise the next dispatch.

## 5. Dispatch shape

Dispatch every role as `Agent(subagent_type=<role>, run_in_background=true, prompt=…)`. Never use `Agent(name=...)`, never reuse an Agent across scopes, never `SendMessage` between roles; the diff is the handoff. Subagents cannot spawn subagents, so every dispatch originates here. Before each dispatch add an `open` lane row with `dispatched: no`; set `dispatched: yes` when the call returns; the `## Lanes` rule (Section 2) governs an `open` row already there.

Read the ticket via `bees show-ticket --ids <issue-id>` and embed the body **verbatim** as a quoted block; never paraphrase or clean up identifier spellings. Framing prose around the block is fine, and it MUST NOT loosen the dispatched role's lane as `agents/<role>.md` states it. Embed the `reference_materials` JSON when non-empty; workers fetch upstream content themselves. Surface the Plan Bee `title` found via `up_dependencies` to the Doc Writer, or an explicit fallback title. Pass the PM the Issue ID, the body verbatim, the `up_dependencies` array, `<scoped-marker-resolver-path>` resolved as `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (PowerShell `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py`) — this context selects Path B of `agents/pm.md` — and `<compromise-tracker-path>` — the path, never the contents. Give every reviewer its scope: a diff range, a ticket ID, or both. The Engineer prompt embeds the approved directive under `## Authoritative design directive (from the Analyst gate)` — the Analyst's `### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`, plus any light-revision clarification — and its context under `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)`, and states that the directive is the enumeration: an unnamed mechanism is a `## Design question`, not a choice. Where the body and the directive conflict, the directive wins; the body still travels verbatim. Writers never receive the directive.

| Heading | Source | Recipients | Fixed empty line |
|---|---|---|---|
| `## Blast radius` | the approved proposal's `### Blast radius`, verbatim and inline, never as a file path | Engineer, PM, Code Reviewer | relay `No invariant added, removed, or weakened.` when that is all the section carries; never omit — a stranded proposal is re-derived before the dispatch that needs it |
| `## Source paths to fingerprint` | union of Engineer returns' `## Files changed` across every Phase A round, test paths dropped | Test Writer | omit the heading when the union is empty or Phase A was empty; when no return carried a list use `git diff --name-only HEAD` (the last-resort fallback, minus test paths) |
| `## Engineer's completeness evidence` | every Engineer completeness list for the scope, verbatim and inline, never as a file path, each attributed to its round | PM, Code Reviewer | omit the heading when no list arrived; always state separately that the assignment was sweep-shaped — a directive or ticket body that directed a change at every site where some property holds — when it was |

- An explicitly-empty `## Files changed` is a list, not a missing one; it contributes nothing to the union and does not trigger the fallback. The fallback fires only when no return in scope carried a list.
- Writer prompts MAY state `"no Engineer Agent will be dispatched for this Issue while you are running"`. They MUST NOT claim `"the source tree is frozen"`.
- Roles: `agents/analyst.md`, `agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`. Role contracts live there; dispatch roles, do not carry their prose.

## 6. Gates

Every `AskUserQuestion` this skill fires is a gate. A gate is a manifest `Write` that fills `## Open gate` with the gate's name, scope, and choice labels verbatim, followed by `AskUserQuestion` in the same turn; this contract substitutes for the two-step gate contract a dispatched skill's routing trailer prescribes. The run-start gates that precede the manifest write — session effort, the pick gate that precedes it, and isolation — fire `AskUserQuestion` directly; the `## Open gate` discipline begins at the manifest write.

Do not narrate a gate; fire both calls. Gates are multi-choice only; never add fake free-text options duplicating the auto-appended `Type something.` / `Chat about this` slot. Evaluate a gate's condition before writing `## Open gate`. When the answer is consumed and the branch entered, rewrite `## Open gate` to `none`. Never end a turn with `## Open gate` filled but no question fired.

- **Session effort.** Read `printenv CLAUDE_EFFORT` (PowerShell `Write-Output $env:CLAUDE_EFFORT`). If empty, non-zero, or not one of `low` / `medium` / `high` / `xhigh` / `max`, skip silently. The floor is `medium`; the order is `low` < `medium` < `high` < `xhigh` < `max`; compare against the floor, never for equality. At or above: no gate, no output. Strictly below: question text: ``This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.`` then a blank line then `Subagent effort is pinned per role and is NOT affected by this setting.` Options: **Proceed anyway** — continue; **Let me change it first** — exit cleanly without dispatching anything; the user runs `/model` and re-invokes.
- **Issue pick** (no arguments): one option per open Issue.
- **Isolation.** Two scenarios. **Scenario A — Already in a worktree** whose name suggests issue-fix work (e.g. `fix-issues`, `bug-sweep`): proceed, no action. **Scenario B — On an existing branch in the main repo**: on `main` or `master` always fire the gate; on a feature branch fire it in `all` or list mode and proceed silently in single mode. The question states the current working directory, the current branch name, that option 1 creates a local branch only (no remote push), and the number of Issues queued. Options: **Create a feature branch (Recommended for `all` mode and list mode)** — create `fix/issues-<short-slug>` or `fix/<id1>-<id2>` from HEAD; **Work on current branch** — commit to the checked-out branch and tell the user its name; **Set up a worktree instead** — offered only when `/bees-worktree-add` is installed; advise running it and exit without working.
- **Analyst.** Strip `### Deferred refinements` from the return, then surface the proposal as prose. Include `### Blast radius` and `### Policy decisions this change implies` in full, with their fixed lines `No invariant added, removed, or weakened.` and `None — the recommendation leaves no policy question open.` Precede it with a one- or two-sentence preamble keyed on `Analyst verdict:`. The preamble names the verdict — one of `recommend-as-stated`, `recommend-with-refinements`, `recommend-different-approach`, `escalate-to-user`. It leads with `⚠️` on `recommend-different-approach` and `escalate-to-user`. It names how many policy decisions the section carries when it is non-empty. It says when `### Blast radius` carries a scope-split recommendation. Then fire the gate. Question: `How should I proceed with this design proposal?` Options:
  - **Approve & proceed to implementation (Recommended)** — the directive is the `### Recommended approach`, `### Blast radius`, and `### Policy decisions this change implies` verbatim plus `### Why`, `### Alternatives considered`, `### Options the body did not consider` as context. Approval covers the design, every policy answer, and any scope split. On Approve, consume the latest return's `### Deferred refinements`: each bullet annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` becomes a `defer-*` obligation; `addressed-now` bullets enter no ledger; a bullet with no destination is a malformed return, surface it. Superseded Revise iterations' obligations are closed; obligations from an earlier Approve survive a later re-fire.
  - **Revise** — discuss in prose; for a substantive change re-dispatch the Analyst with the same body and `reference_materials` plus `## Prior proposal and user feedback` quoting the prior proposal in full, `### Deferred refinements` included, and the feedback verbatim, then re-run this gate; light feedback is folded into the Approve branch; no cap on revisions.
  - **Cancel** — no commit, the Issue stays `open`, route through Section 12.
  - `Re-dispatch the Analyst with this finding` (gates (c) and (d)) is for a `blocker` showing the approved directive itself is wrong: re-dispatch the Analyst with the Revise shape carrying the finding verbatim as the feedback, then run this gate again; the new Engineer works against the current working tree. On an Approve reached from that re-fire, first mark every open writer, reviewer, and PM lane at this Issue `closed` and discard every finding raised under the superseded directive.
- **Unexplained movement.** Fires from the movement rung below when the movement cannot be attributed. The question carries the writer's movement report verbatim. It adds the statement *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths, so it cannot attribute the movement.* Options: **Re-dispatch the writer now** — next round against the current tree; **Wait** — yield; re-fire only on the operator's reply, never on a sibling lane's notification, which is processed normally; **Abort this Issue** — the Issue stays `open`, nothing is committed, route through Section 12.
- **Routing (c)** and **routing (d)** — Section 7.
- **Deferral hygiene** — Section 9. **Post-completion disposition**, **SR-6.7**, **SR-4.6** — Section 11. The context guard (Section 8) fires no gate; an over-threshold reading stops the run.

**Movement rung.** A Test Writer or Doc Writer return that reports it *stopped* on detected source movement is not a completion; fix mode is the strict branch, so any movement outside the writer's lane is anomalous. On a movement report: mark the writer's lane `closed`; open an `aborted-*` obligation at this Issue with the "how far I got" report as detail. Phase C does not begin while that obligation is `open`. Then attribute the mover:

- an Engineer → a precondition breach in fix mode; note it, let Phase A re-close, then re-dispatch;
- the sibling Phase B Test Writer whose `## Perturbations` lists every moved path → re-dispatch once it has returned, no gate (do not classify while a dispatched Test Writer is still in flight; when Phase B dispatched none, `None`, or a partial list falls through);
- an external actor → re-dispatch once the tree has settled;
- unexplained → fire the gate.

The re-dispatch is the next round at the same scope and carries the "how far I got" detail. A normal deliverable from the re-dispatched lane closes the obligation; a second abort refreshes the same obligation's detail, never opens another.

**Engineer-dispatch precondition.** Never dispatch an Engineer for an Issue while a `## Lanes` row is `open` at that Issue for `test-writer`, `doc-writer`, `test-reviewer`, `doc-reviewer`, `pm`, or `analyst`. The Code Reviewer is the deliberate exception; Phase A alternates the two by construction. Resolve any `open` row per the `## Lanes` rule (Section 2), then re-check. An `aborted-*` obligation never blocks an Engineer round; it holds Phase C shut.

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

**(c) Scope-bounding gate.** Fires on rows 2, 3, and 4, and whenever the orchestrator would otherwise scope-bound a finding. The question carries the finding verbatim plus one line naming the entry condition.

- For a `suggestion` or `nit` the choices are `Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`; on a row-2 fire mark `Defer to follow-up Issue` `(Recommended)`.
- **Blocker rules:** `Accept the limitation` is never offered to a `blocker`. A `blocker` always gets its base pair. `Defer to follow-up Issue` is added only when the needed fix path introduces a mechanism AND that mechanism serves a case outside the stated defect; it is then paired with a narrowing dispatched after `/quo-file-issue` returns an Issue ID, and marked `(Recommended)`.
- `Fix properly now` re-dispatches the implementer to address the finding fully.
- `Defer to follow-up Issue` files via `/quo-file-issue` inline through the Skill tool, carrying the reviewer's sketched design verbatim, then ships the soft fix (Trigger A).
- `Accept the limitation` records the compromise (Trigger B) and proceeds.

**(d) Routing-decision gate.** Fires on rows 1 and 5. The question carries the finding verbatim. Choices: one per reviewer-surfaced fix path, its description carrying the path's depth tag, `(Recommended)` on the Step-1 pick; `Defer to follow-up Issue` — file via `/quo-file-issue` inline through the Skill tool carrying the finding verbatim, and ship no path this round (Trigger A); `Cancel`. A `blocker`'s `Defer` is offered only under gate (c)'s two conditions, on gate (c)'s terms.

| Divergence | `/quo-fix-issue` | `/quo-execute` |
|---|---|---|
| Approved-design source for "introduces a mechanism" | the `## Authoritative design directive` block from the Analyst gate | the Subtask body, its parent Task body, and the PRD/SDD the Plan Bee's `reference_materials` resolves to, or the Plan Bee body when null/empty |
| Blocker base pair at gate (c) | `Fix properly now` + `Re-dispatch the Analyst with this finding` | `Fix properly now` + `Cancel` |
| `Cancel` at gate (c) | none; `Ctrl-C` remains the run-level abort | in the `blocker` set only; ends the run via Section 12 |
| Gate (d) non-deferrable `blocker` set | per-path list + `Re-dispatch the Analyst with this finding` + `Cancel`; on an empty list mark the Analyst choice `(Recommended)` | per-path list + `Cancel`; on an empty list the question says the reviewer enumerated no fix path and the user directs the fix in free text or cancels |
| Gate (d) `Cancel` semantics | ends the current Issue; Section 12's mode branch decides the run | ends the run via Section 12 |
| Filing-failure re-prompt `Cancel` | at gate (d) only | at either gate on a `blocker`, at gate (d) otherwise |
| Part (g) code-review rung | the Code Reviewer, one clause | Clause 1: the per-Task PM's in-flight `/quo-engineer-review` pass; Clause 2: the Bee-level Code Reviewer, or at the Epic boundary the inter-Epic reviewer |
| Close-out target on `Cancel` / abort | `#### Aborted-Issue close-out` | `#### Aborted-run close-out` |

**(g) Re-dispatch ordering when a fix path changes source.** Dispatch the Engineer first, then the code review for that site against the resulting diff. Only once that review has closed, dispatch the Test Writer and/or Doc Writer the change invalidated. The rounds are ordered, not concurrent, and gated by the Engineer-dispatch precondition (Section 6). One elision: on the final `trivial-tweak` nit pass, skip the code-review rung and dispatch the affected writer once the Engineer returns. A path that changes no source file re-dispatches that single writer lane alone.

Follow the review skills' routing trailer literally — `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`. When you ignore a finding, record it at that moment as a `defer-*` obligation with exactly one destination: `addressed-now`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue`; an `addressed-now` item enters no ledger. A PM report note with no severity and no fix path is not a finding and is not routed. A missing-completeness-list finding on a dispatch whose list a compaction destroyed is a compaction artifact: list it under `**Ignored Review Feedback**`, create no obligation, dispatch nothing.

## 8. Per-unit close-out

**After each Issue.** When every finding is dispositioned and no lane at this Issue is `open`:

1. Re-read the status with `bees show-ticket --ids <issue-id>` and run `bees update-ticket --ids <issue-id> --status done` only if it is not already `done`.
2. Run the `Format` command from `## Build Commands` — the only rung the orchestrator runs, never the test suite, and with the Bash `timeout` parameter (max `600000` ms) when long; past that, `Bash(run_in_background: true)` and wait for the completion notification.
3. Run `git status`; stage agent-reported files plus formatting changes to files this Issue's agents touched. Resolve the in-repo Issues hive path with `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues` (PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues`) and when it prints one run `git add <emitted-issues-path>/<issue-id>`. **Do NOT blindly `git add -A`**.
4. Commit once with subject `Fix issue: <title> (<issue-id>)`, e.g. `Fix issue: Tighten dispatch contract gap (b.abc)`. **NEVER push to remote — committing only.** Record the commit SHA under `**Progress:**`.
5. Mark every lane and `aborted-*` obligation at this Issue `closed` — bookkeeping only; a returned Agent has already exited and there is no shutdown to perform. Output:

```markdown
## Issue [x] of [total] done: [issue-title]

**Issue**: <issue-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Test review: Y issues found/None needed | Docs review: Z issues found/None needed — each slot carrying its own `N nits applied without re-review` (or "count unavailable post-compaction") when any]
**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed, using the path from CLAUDE.md `## Documentation Locations`]
**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]
**Second-order effects**: [the relayed `### Second-order effects` narrative]
[**Accepted compromises** — rendered when the tracker has entries, or OMITTED ENTIRELY]
```

- `**Doc Sync**` confirms the PM's verdict — a deep review or `no spec drift surface to review for this Issue` — and, when the body carried `## Doc divergence noted`, that the Doc Writer consumed it; the orchestrator performs no doc edit itself.
- `**Second-order effects**` is unconditional and is narrative, not routing input: it never holds a lane open, never becomes a finding, and is never re-ranked or merged into the `**Reviews**` line.
  - Collect every Phase A Code Reviewer return and the PM Final report's `### Second-order effects` with its `#### <invocation scope>` sub-blocks.
  - Render bullets verbatim; keep the sub-block labels the relaying source supplied and attribute each Code Reviewer block by round; de-duplicate exact repeats.
  - Render `None identified.` when every source said `No second-order effects identified.` or none ran.
  - When a source's return is no longer readable, render the sources in hand and say that source's narrative is unavailable post-compaction.
- `**Accepted compromises**`: `Read` the tracker at the manifest's path; this surface only reads the tracker, never writes it. When it has `## Compromise <n>` entries, render one bullet per entry with `Finding (verbatim)`, `Decision`, `Rationale`, and `Follow-up Issue`, never `Fix paths surfaced by reviewer`. Render all entries in full, prefaced by `N compromises were accepted during this run:` when more than ten; otherwise omit the line.
- Record every PM-deferred item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` as a `defer-*` obligation now.

**Issue boundary.** Run the deferral-hygiene gate (Section 9), then the checkpoint, then branch: single mode → Section 11; batch exhausted → the batch-close deferral-hygiene firing (Section 9), then Section 11; a next Issue remains → the guard, then Section 4 step 7 for the next Issue.

#### Issue-boundary state-externalization checkpoint

A definition, not a step; run it only where the boundary above, or Section 12, calls for it, always after the deferral-hygiene gate (Section 9) has closed. It verifies that every load-bearing fact lives in a durable carrier and refreshes them; it does not clear, compact, or reclaim context, and must never be narrated as if it did.

1. Verify:
   - (a) the Issue reads `done` in bees;
   - (b) `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (identical on POSIX and PowerShell) is non-empty, `<pre-session-sha>` read from the manifest — never a bare `git log -1`, never an unbounded `--grep`;
   - (c) `Read` the tracker at the manifest's `**Compromise tracker:**` path and confirm every compromise accepted this Issue has an entry — an absent file is a gap only when an entry was owed;
   - (d) every `## Lanes` row at this Issue is `closed`, no `defer-*` obligation is `open`, and `## Open gate` reads `none`;
   - (e) the manifest's `**Unit scope:**` matches this run's batch.
   Fix any gap now. On the aborted path, (a) and (b) invert: confirm the Issue reads `open` and skip the commit search.
2. Rewrite the manifest per Section 2: the Issue's `**Progress:**` line and `**Next unit:**`; prune `## Lanes` and `## Obligations` to rows still `open`, and `## Rounds` to rows not yet rendered on a summary line.
3. Re-read, do not recall, at every dispatch on the next Issue: `bees show-ticket` the ticket and `Read` the manifest. The next Issue's directive comes from its own Analyst pass. If a needed fact is not in a carrier, write it into one before dispatching.

#### Context-window boundary guard

Runs only on the continuing path (a next Issue remains), after the checkpoint and before the next Issue; never in single mode, on a batch exhausted, or from Section 12. Rationale and the gauge contract live in the context-guard reference (Section 3). The resume command is `/quo-fix-issue all` on an `all` run, or `/quo-fix-issue <remaining-ids>` listing the Issues not yet `done`.

1. Read `printenv CLAUDE_CODE_SESSION_ID` (PowerShell `Write-Output $env:CLAUDE_CODE_SESSION_ID`); trim trailing whitespace. Unset or empty → skip silently.
2. Obtain the threshold: `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold` (PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold`). Never restate the number in prose.
3. Read: `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>` (PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" read --session-id <trimmed-session-id>`).
4. Branch. Integer ≥ threshold → record `<integer>% at <issue-id>`, then STOP: report the percentage, state the run is at a clean boundary with every carrier on disk, name the resume command, and exit the skill. Integer < threshold → record `<integer>% at <issue-id>`, continue. `no-reading` → record `no reading`, continue. `stale`, non-zero exit, or empty stdout → STOP: report that the producer appears stalled or the reading is untrustworthy, recommend a fresh session with the resume command, exit. `missing` → record `no reading`, continue silently, whether or not `<tempdir>/.quorum/context-guard-opt-out` exists.

## 9. Deferral hygiene

Fires at every Issue boundary on both paths, fixed and aborted, over the deferrals surfaced during that Issue. The batch-exhausted branch (Sections 8 and 12) fires it once more in `all` or list mode over anything surfaced between Issues; that batch-close firing prints `Deferral hygiene (batch close): no deferred items.` when empty. In single mode the per-Issue firing is the only one. Every `AskUserQuestion` here is a gate per Section 6.

- **Step 0 — Retroactive ledger reconciliation (safety net).** Walk this Issue's `**Ignored Review Feedback**` (absent on the aborted path), the PM Final report's deferred items, and the Analyst's `### Deferred refinements`. Create a `defer-*` obligation for any item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` that lacks one; skip `addressed-now` items.
- **Step 1 — Enumerate the active deferral ledger.** The active set is every `defer-*` obligation with status `open`. Empty → print `Deferral hygiene: no deferred items.` and proceed.
- **Step 2 — Surface the active set and gate the user choice.** Print the set as a numbered list, one bullet per obligation with its detail, then fire the gate: `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body`. Per-item routing uses the auto-appended free-text slot; this is the one gate where free text is the primary path.
- `Fix in this session`: dispatch the implementer or reviewer per Section 5, or update the ticket body inline; close each obligation with its resolution in detail.
- `File as issue tickets`: invoke `/quo-file-issue` inline through the Skill tool per item with the description as the body; close the obligation when an Issue ID returns.
- `Encode in an existing ticket body`: destinations are a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass. Append `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` to the body, the timestamp authored from your own clock, the stem kept verbatim. `mkdir -p /tmp/.quorum` (PowerShell `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null`), `Write` the revised body to `/tmp/.quorum/bees-body-<defer-N>.md` (`$env:TEMP\.quorum\bees-body-<defer-N>.md`), e.g. `bees-body-defer-3.md`, then `bees update-ticket --ids <ticket-id> --body-file <path>`. Never delete the scratch file. Close the obligation when the update succeeds.
- After all Encode writes, one follow-up commit per firing, with `<resolved-helper-path>` = `<this skill's base directory>/../quo-execute/scripts/hive_commit.py` (PowerShell `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py`): `python3 "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]` (PowerShell `python "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`); `<N>` counts items, one `--doc-path` per PRD/SDD file routed to, each path resolved from CLAUDE.md `## Documentation Locations`. It commits `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded` or prints `skipped: nothing staged`.
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

Scope: `git diff <pre-session-sha>` (the working tree against the pre-session commit) plus every untracked file from `git ls-files --others --exclude-standard`; a change no ticket body asks for is reported as likely pre-existing or an unticketed in-run edit, as an inference. `Read` the manifest for `<pre-session-sha>` and `<compromise-tracker-path>`; if the manifest is missing or names another batch, stop and tell the user rather than guessing the scope. When the session landed no commit at all, say so and skip the sweep.

1. `Read` the post-completion prompt reference (Section 3), fill its parameters (`<unit-noun>` = `fix`), and dispatch one fresh `Agent(subagent_type=general-purpose, run_in_background=true, prompt=…)` with the skeleton verbatim. Do not review the run yourself; do not invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review`. Wait for its report.
2. Synthesize: compare its findings against the in-flight PM and reviewer verdicts and flag disagreements explicitly. When any `[compromise-challenge]` finding is present, lead with a `⚠️` preamble, e.g. `⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below.`
3. `no issues found` → print `Post-completion review: no issues found`; this section is complete.
4. Otherwise fire the disposition gate: `Post-completion review found [N] issues. How would you like to handle them?` Options: **Fix in this session**, **File as issue tickets**, **Skip**. Recommend `Fix in this session` when a PHASE 2 contract-violation `blocker` is present; that class has no recovery gate.
5. For each PHASE 3 or PHASE 4 `[compromise-challenge]`, in the reviewer's emission order, fire its recovery gate before or alongside the disposition. **SR-6.7 ungated-route recovery gate.** Choices: `File follow-up Issue to revisit the depth decision` — `/quo-file-issue` via the Skill tool with the finding and the tracker entry, then Trigger D's in-place update; `Accept the misjudgment and proceed` — Trigger D append; `Pause to discuss` — stop and discuss; the user re-issues a choice. **SR-4.6 under-enumeration recovery gate.** Choices: `File follow-up Issue to surface the missing path`; `Accept the under-enumeration and proceed`; `Pause to discuss`; same branch behavior.
6. Dispose per the answer:
   - **Fix in this session**: per-unit rules apply with `postcomp-<n>` as the unit, `<n>` the finding's 1-based index: lanes at scope `postcomp-<n>`, the movement rung, the Engineer-dispatch precondition across every `postcomp-*` scope, part (g) ordering within a finding, independent findings concurrent. An abort of a post-completion lane closes its rows here and continues this section; it never enters Section 12. When every lane is `closed` and no `aborted-*` obligation at a `postcomp-*` scope is `open`, commit.
   - **File as issue tickets**: `/quo-file-issue` per finding; report the IDs.
   - **Skip**: continue.

An Engineer at `postcomp-<n>` returning `## Design question` is not a completion; there is no Analyst here. Mark its lane `closed`, dispatch no further lane for that finding, and route the finding to **File as issue tickets** carrying the question verbatim and its what-landed list. Note in the final report which of that finding's edits are already on disk.

When this section is complete, proceed to Section 13.

## 12. Aborted-unit close-out

#### Aborted-Issue close-out

Entered from **Abort this Issue**, from the Analyst gate's `Cancel`, or from gate (d)'s `Cancel`. A definition, not a step; run it only when a branch names it. The Issue ends without a fix landing: no commit, the Issue stays `open`.

1. Mark `closed` every lane and `aborted-*` obligation at this Issue, recording the abort reason in each `aborted-*` obligation's detail. An in-flight sibling lane cannot be terminated; mark it `closed` anyway and discard its late return. Note in the abort's `aborted-*` obligation detail that it was in flight, so a resuming session re-checks its work instead of trusting ticket state; on a gate `Cancel`, which opens no obligation, step 3's uncommitted-paths list is that record.
2. Run the deferral-hygiene gate (Section 9), then the checkpoint (Section 8) on its aborted path with `**Progress:**` `<issue-id>: aborted — no commit; Issue left open`.
3. Run `git status --porcelain` and branch on mode. Single mode, or batch exhausted: name the aborted Issue and the uncommitted paths, then (batch exhausted only) the batch-close deferral-hygiene firing (Section 9), then Section 11 over whatever landed. A next Issue remains: **STOP the run here** — name the aborted Issue, the uncommitted paths, and the resume command `/quo-fix-issue <remaining-ids>` or `/quo-fix-issue all`; do not run the context guard; exit. `Ctrl-C` remains the unconditional run-level abort.

## 13. Final output

Before yielding, follow the GitHub close reference (Section 3): emit `Upstream GitHub Issues to consider closing:` with one `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` bullet per fixed Issue whose `reference_materials` carries a `github-issue` resolver, or nothing when none does. The skill never runs `gh issue close` itself. Then yield.
