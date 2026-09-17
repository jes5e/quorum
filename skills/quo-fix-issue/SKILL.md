---
name: quo-fix-issue
description: Fix an issue described in a Bee ticket. Use '/quo-fix-issue all' to fix all open issues sequentially, or '/quo-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset.
argument-hint: "[<issue-id> | <url> | <id-or-url> ... | all]"
---

## 1. Preconditions

Before anything else, verify the host repo is configured for quorum. **Hard-fail** with `Run /quo-setup first.` plus a one-line note of what is missing if any item below is absent. Do not improvise commands or guess paths. In a fresh worktree or clone, `bees list-hives` can report no hives even though `.bees/` is committed; `/quo-setup`'s fast path re-registers them, and that is the expected remedy rather than a defect.

- The eight custom subagent types are registered in this session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`. Custom subagents load at session start; a fresh install needs a Claude Code restart or `/agents` to hot-reload. Verification rides on the first dispatch: an `Agent type '<name>' not found` error from the Agent tool for any of the eight STOPS the run with `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` Never fall back to `general-purpose` as a substitute for a missing role, never skip the dispatch, never improvise a substitute role.
- The Issues hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `issues`.
- The Specs hive is colonized: `bees list-hives` includes a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section; roles read doc paths from it by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`; roles read commands from it by exact key. `Compile/type-check` may be present with an empty value; the other four must be non-empty.

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
- **Ledger:** <tempdir>/.quorum/ledger-<YYYYMMDD-HHMM>-<short-suffix>.md
- **Cost:** dispatches <n>; subagent tokens <t>
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
| scope | review | classification | decision | text fixes applied without re-review |
|---|---|---|---|---|

## Open gate
none
```

- `**Pre-session SHA:**` is captured once, here, with `git rev-parse HEAD` (identical on POSIX and PowerShell); Section 11 reads it back from this file.
- `**Compromise tracker:**` records the tracker's full path including its random `<short-suffix>`, generated here per Section 10; recording the path does not create the file.
- `**Ledger:**` records the cost record's full path, generated here like the tracker's; recording the path does not create the file. On every Agent completion notification, `Read` the ledger — create it with the header row `| # | role | scope | round | tokens | tool uses | duration | notes |` when absent — append one row from the notification's usage (`subagent_tokens`, `tool_uses`, `duration_ms` rendered as minutes and seconds), and rewrite `**Cost:**` as the row count and the token total. A usage field the notification does not carry is written `unknown`, and an `unknown` token cell counts as 0 toward `**Cost:**`'s total and Section 5's resume bound. `notes` carries `full pass` (Section 7) and `fresh` (Section 5), and is otherwise empty; a completion whose dispatch is not known to have been fresh — the fact was lost to a compaction — leaves `notes` empty, which at worst retires the implementer early. A resumed Agent's completion is a row. The ledger is never pruned within a run; it is an operator-facing record and the input to Section 5's resume bound, never a review-routing input.
- `**Context guard:**` is written only by the guard (Section 8); omit the line until then. Its percentage is an operator-facing record, not a routing input.
- `**Unit scope:**` records the post-resolution working list verbatim, in the user's order; that order is intentional and cannot be re-derived from bees.
- `**Progress:**` carries one line per finished Issue in the order worked: `<issue-id>: done — commit <sha>` or `<issue-id>: aborted — no commit; Issue left open`.
- `## Lanes` holds one row per dispatched Agent: `role` is the subagent type, `scope` is the Issue ID it works, `round` is the 1-based dispatch count for that role at that scope, `dispatched` is `no` until the `Agent(...)` call returns and `yes` after, and `status` is `open` or `closed`. A post-completion lane's scope is `postcomp-<n>`; the post-completion reviewer's own row is role `general-purpose` at scope `postcomp`. A lane is `closed` when its Agent is gone — a completion notification was processed, a movement report was received, or the run ended — whether or not its work shipped. An `open` row with `dispatched: yes` will notify — wait for it; an `open` row with `dispatched: no` has no Agent behind it — dispatch it now or mark it `closed`; a row that is absent or whose `dispatched` value is unreadable reads as `no`. Never dispatch a role at a scope that already has an `open` row for it.
- `## Obligations` holds one row per owed action: kind `defer-*` (id `defer-<n>`, detail = one-line description plus destination), and kind `aborted-*` (id `aborted-<role>`, detail = the writer's "how far I got" report). Status is `open` or `closed`. Detail is informational; routing reads only kind, scope, and status.
- `## Rounds` holds one row per review lane, keyed by the scope and the **Reviews**-line slot (`review`) the row belongs to. `classification` lists one value per round after the first, in round order — `earned`, `late`, `text`, `clean`, `enumerated`, or `unavailable post-compaction` — and is empty until a second round is dispositioned. `decision` is the lane's latest exit decision: `another round`; `to the escalation target` (a premise check or an earned-chain escalation is in flight with this skill's escalation target, Section 7; a premise check fired by a PM finding is recorded on the Code review row at that scope, the return it is checked against); or, when the lane closes, `close — clean` (the last read raised nothing, or every finding settled with nothing applied), `close — text` (only text fixes applied, no further read owed), or `close — enumerated` (the late-chain enumeration's gaps are closed, no further read owed). The count is the text fixes applied in the lane's final implementer pass without a further reviewer round (Section 7). Rewrite the row when a round's findings are routed, before the action the decision names. `round` in `## Lanes` counts dispatches; `## Rounds` records decisions and counts.
- `## Open gate` names the gate about to fire, its scope, and its choice labels verbatim, or `none`.
- The manifest carries lane phase and obligations; an earlier rule forbade the manifest a lane-phase field, and that rule is withdrawn.
- Validate the manifest before trusting any field: its `**Unit scope:**` must match this run's batch. A manifest naming other Issues is treated as absent: trust no field in it. If this run's own `**Pre-session SHA:**`, `**Compromise tracker:**`, or `**Ledger:**` value is no longer readable, stop and tell the user before touching the file. Otherwise rewrite every field — `**Unit scope:**`, `**Isolation strategy:**`, `**Pre-session SHA:**`, `**Compromise tracker:**`, `**Ledger:**`, `**Progress:**`, and `**Next unit:**` — from this run's own state, and empty `## Lanes`, `## Obligations`, `## Rounds`, and `## Open gate`.

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

The orchestrator performs mechanical steps that produce a tool artifact directly — git queries, manifest reads and writes, bees status flips, helper invocations; it dispatches every step that is a judgment over file contents or a review. Dispatch is by background `Agent` invocations against the sibling `agents/` subagent types: reviewers, the Analyst, the PM, and the post-completion reviewer are fresh on every dispatch; an implementer is dispatched once per scope and resumed for its fix rounds there (Section 5). There is no long-lived team and no peer-to-peer messaging.

### Run start

1. Run the session-effort gate (Section 6) first, once.
2. Parse the argument string: split on any run of commas and/or whitespace and discard empty tokens. A token starting with `http://` or `https://` is a **URL token**; anything else is a **ticket-ID token**. Five forms: zero tokens → query open Issues, fire the Issue-pick gate (Section 6), fix that one Issue and exit; exactly `all` → query open Issues, sort by ticket_id, fix each in turn without confirmation; one ticket-ID token → single-issue mode; one URL token → file it via the URL-resolution reference, then fix the resulting Issue; two or more tokens → list mode, fixed **in the order given**, never sorted, never deduplicated, no confirmation between Issues. Open-Issue query: `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'`.
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
- **Phase A — source to clean.** When the approved directive needs source changes, dispatch the Engineer alone. On its return dispatch the Code Reviewer alone against the diff, unless the return carries `## Design question`. Loop Engineer → Code Reviewer until the Code Reviewer emits `No code issues found.` with an empty numbered list, or until Section 7's hold set releases the lane: an Engineer pass whose `Kinds changed` names only `comments` or `contract-text` closes Phase A after the single confirming read that rule owes, when it owes one. A non-empty `### Second-order effects` narrative beside a clean list does not hold Phase A open; carry it to the summary. When no source change is needed, Phase A is empty.
- **Phase B — writers once, in parallel.** After Phase A closes, dispatch the writers concurrently: the Doc Writer always, the Test Writer when the approved directive calls for a test change or Section 5 emits a non-empty `## Source paths to fingerprint` heading. The Issue body alone does not decide. This is the only forward-path dispatch of the writers.
- **Phase C — remaining reviewers plus PM.** When the Phase B writers have returned and no `aborted-*` obligation at this Issue is `open`, dispatch concurrently: `Agent(subagent_type="test-reviewer", run_in_background=true)` if the Test Writer ran, `Agent(subagent_type="doc-reviewer", run_in_background=true)` if the Doc Writer ran, and `Agent(subagent_type="pm", run_in_background=true)` always — **PM is the exception to the conditional-spawn rules.** In this skill the PM reviews spec traceability, scope, and the compromise tracker only: its dispatch prompt states that it invokes neither `/quo-engineer-review` nor `/quo-doc-writer-review`, because Phase A's Code Reviewer and this phase's Doc Reviewer are those reads. The Code Reviewer is not dispatched again here. Follow each review skill's routing trailer literally, but dispatch no implementer for a Phase C finding until every Phase C lane at this Issue has returned, so no lane reads a moving tree. A Phase C finding that changes source re-enters Phase A per part (g), then re-dispatches only the writer lanes the change invalidated and their reviewers, plus the PM when spec alignment needs another pass against the updated diff (on a minor iteration you may choose not to re-dispatch it); a finding confined to a writer's lane re-dispatches that writer alone.
- **Design-question rung.** On an Engineer return carrying `## Design question`: mark the lane `closed`, dispatch no Code Reviewer, and re-dispatch the Analyst with the Revise shape carrying the question verbatim in place of user feedback — or, when the prior proposal is no longer readable, the re-derivation shape below with the question as its feedback — a statement that a partial implementation is on disk naming the Engineer's `## Files changed`, and that the revised `### Blast radius` must cover the new mechanism's lifecycle. Then run the Analyst gate unchanged; on Approve, dispatch a fresh Engineer (Section 5) against the current working tree with the revised directive.
- **Premise and chain rungs.** A premise check or an earned-chain escalation (Section 7) dispatches the Analyst with the Revise shape carrying the finding, or the chain, verbatim in place of user feedback, plus the union of `## Files changed` across every return at this Issue as a statement of what is on disk. For a premise check the dispatch prompt carries the heading `## Premise check`, every finding of the round that meets the condition, and the directive section or prior Code Reviewer return each contradicts, verbatim; the Analyst's return leads with `Premise check: premise-holds` or `Premise check: premise-false` and a one-line reason, and no gate fires on it. Any `### Blast radius` entries that return carries replace the matching entries of the `## Blast radius` block the Section 5 table relays on later dispatches. For a chain, run the Analyst gate unchanged; on Approve, dispatch a fresh implementer (Section 5) against the current working tree with the revised directive.
- **Re-derivation shape.** When the proposal is needed and unreadable, first check the manifest's lanes: an `open` analyst lane → wait for its return and run the Analyst gate, reviewing nothing meanwhile. Otherwise dispatch the Analyst with: the body re-read from bees and the same `reference_materials`; the changed-file list on disk — the latest Engineer `## Files changed`, or `git diff --name-only HEAD` minus test paths — an empty list meaning nothing has landed; and a plain statement that the prior proposal was lost to a compaction and the Analyst re-derives from the codebase as it stands, or that no proposal was produced yet when this is the first pass. Once its gate is answered, resume the ladder from the lanes: no Engineer lane → Phase A's entry; Engineer lane but no writer lane → re-dispatch the Code Reviewer with the re-derived `## Blast radius`; otherwise the next dispatch.

## 5. Dispatch shape

Dispatch every role as `Agent(subagent_type=<role>, run_in_background=true, prompt=…)`; an implementer — `engineer`, `test-writer`, `doc-writer` — also carries `name=<role>-<scope>`. An implementer's fix round at a scope it already worked is a resume, `SendMessage(to=<role>-<scope>, message=…)`, carrying the routed findings and the chosen path in full, the relay headings the round owes, and the return contract for this pass — `## Files changed` and `Kinds changed:` for this pass only, the Test Writer re-taking its opening fingerprint. Dispatch a fresh named Agent instead, superseding the old one, when the escalation target revised the directive (an Approve after a Revise at the Analyst gate, or **Continue** at the escalation gate), when `ListAgents` does not list the name, or when the send fails. Every named dispatch that is not a resume writes `fresh` in its ledger row's `notes` cell; dispatch fresh also when the ledger's token total for that name since its latest `fresh` row exceeds 600,000 — a first setting, to be tuned from the ledger. Reviewers, the Analyst, the PM, and the post-completion reviewer are never named and never resumed. Never reuse an Agent across scopes, never `SendMessage` between roles; the diff is the handoff. A resume is a dispatch for every lane rule and precondition. Subagents cannot spawn subagents, so every dispatch originates here. Before each dispatch add an `open` lane row with `dispatched: no`; set `dispatched: yes` when the call returns; the `## Lanes` rule (Section 2) governs an `open` row already there.

Read the ticket via `bees show-ticket --ids <issue-id>` and embed the body **verbatim** as a quoted block; never paraphrase or clean up identifier spellings. Framing prose around the block is fine, and it MUST NOT loosen the dispatched role's lane as `agents/<role>.md` states it. Embed the `reference_materials` JSON when non-empty; workers fetch upstream content themselves. Surface the Plan Bee `title` found via `up_dependencies` to the Doc Writer, or an explicit fallback title. Pass the PM the Issue ID, the body verbatim, and the `up_dependencies` array; this context selects Path B of `agents/pm.md`. Also pass `<scoped-marker-resolver-path>` resolved as `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (PowerShell `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py`) and `<compromise-tracker-path>` — the path, never the contents. Give every reviewer its scope: a diff range, a ticket ID, or both. The Engineer prompt embeds the approved directive under `## Authoritative design directive (from the Analyst gate)` — the Analyst's `### Recommended approach` and `### Policy decisions this change implies`, plus any light-revision clarification — and its context under `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)`, and states that the directive is the enumeration: an unnamed mechanism is a `## Design question`, not a choice. The directive comprises all three sections; its `### Blast radius` is relayed under the `## Blast radius` heading rather than repeated inside the block. Where the body and the directive conflict, the directive wins; the body still travels verbatim. Writers receive the directive's `## Blast radius` and `## Design decisions for writers` only, never the rest of it.

| Heading | Source | Recipients | Fixed empty line |
|---|---|---|---|
| `## Blast radius` | the approved proposal's `### Blast radius`, as amended by any premise-check return (Section 4), verbatim and inline, never as a file path | Engineer, Code Reviewer, Test Writer, Doc Writer, Test Reviewer, Doc Reviewer | relay `No invariant added, removed, or weakened.` when that is all the section carries; never omit — a stranded proposal is re-derived before the dispatch that needs it |
| `## Source paths to fingerprint` | union of Engineer returns' `## Files changed` across every Phase A round, test paths dropped | Test Writer | when no return carried a list use `git diff --name-only HEAD` (the last-resort fallback, minus test paths); omit the heading only when the resulting set is empty or Phase A was empty |
| `## Engineer's completeness evidence` | every Engineer completeness list for the scope, verbatim and inline, never as a file path, each attributed to its round | Code Reviewer | omit the heading when no list arrived; always state separately that the assignment was sweep-shaped — a directive or ticket body that directed a change at every site where some property holds — when it was |
| `## Design decisions for writers` | the approved proposal's `### Decisions for writers`, verbatim | Test Writer, Doc Writer, Doc Reviewer | relay `None — the approach leaves no test or doc decision to the writers.` when that is all the section carries; never omit while a proposal exists |
| `## Engineer's diff (path)` | the path of a file written just before the dispatch with `git diff <pre-session-sha> --output=/tmp/.quorum/diff-<issue-id>-<short-suffix>.md` (PowerShell `git diff <pre-session-sha> --output="$env:TEMP\.quorum\diff-<issue-id>-<short-suffix>.md"`) — one literal command, run once the `.quorum` directory exists per Section 2 | Doc Writer | omit when Phase A was empty |
| `## Confirming pass` | the findings the implementer was asked to fix, and that pass's `## Files changed` and `Kinds changed:` lines, verbatim | every reviewer at round 2 or later of its lane, and every `postcomp-*` reviewer | omit when the previous implementer return is unreadable — that round is a full pass |
| `## Site enumeration requested` | the fixed line `List every site this unit's change introduced and whether the artifact under review covers it; return the gaps as one finding.` | the reviewer of a lane whose `## Rounds` row shows two consecutive `late` classifications and no `enumerated` one (Section 7) | omit otherwise |

- An explicitly-empty `## Files changed` is a list, not a missing one; it contributes nothing to the union and does not trigger the fallback. The fallback fires only when no return in scope carried a list.
- Writer prompts MAY state `"no Engineer Agent will be dispatched for this Issue while you are running"`. They MUST NOT claim `"the source tree is frozen"`. Every implementer return carries `## Files changed` and one line `Kinds changed:` naming one or more of `code`, `tests`, `contract-text`, `comments` (definitions in the routing reference, Section 3). Section 7's hold set reads that line and checks it against the same return's `## Files changed`; it is never relayed downstream.
- Roles: `agents/analyst.md`, `agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`. Role contracts live there; dispatch roles, do not carry their prose.

## 6. Gates

Every `AskUserQuestion` this skill fires is a gate. A gate is a manifest `Write` that fills `## Open gate` with the gate's name, scope, and choice labels verbatim, followed by `AskUserQuestion` in the same turn. This is the gate contract a dispatched skill's routing trailer names for this skill, in place of the two-step contract it names for other callers. The run-start gates that precede the manifest write — session effort, the pick gate that precedes it, and isolation — fire `AskUserQuestion` directly; the `## Open gate` discipline begins at the manifest write.

Do not narrate a gate; fire both calls. Gates are multi-choice only; never add fake free-text options duplicating the auto-appended `Type something.` / `Chat about this` slot. Evaluate a gate's condition before writing `## Open gate`. When the answer is consumed and the branch entered, rewrite `## Open gate` to `none`. Never end a turn with `## Open gate` filled but no question fired.

- **Session effort.** Read `printenv CLAUDE_EFFORT` (PowerShell `Write-Output $env:CLAUDE_EFFORT`). If empty, non-zero, or not one of `low` / `medium` / `high` / `xhigh` / `max`, skip silently. The floor is `medium`; the order is `low` < `medium` < `high` < `xhigh` < `max`; compare against the floor, never for equality. At or above: no gate, no output. Strictly below: question text: ``This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.`` then a blank line then `Subagent effort is pinned per role and is NOT affected by this setting.` Options: **Proceed anyway** — continue; **Let me change it first** — exit cleanly without dispatching anything; the user runs `/model` and re-invokes.
- **Issue pick** (no arguments): one option per open Issue.
- **Isolation.** Two scenarios. **Scenario A — Already in a worktree** whose name suggests issue-fix work (e.g. `fix-issues`, `bug-sweep`): proceed, no action. **Scenario B — On an existing branch in the main repo**: on `main` or `master` always fire the gate; on a feature branch fire it in `all` or list mode and proceed silently in single mode. The question states the current working directory, the current branch name, that option 1 creates a local branch only (no remote push), and the number of Issues queued. Options: **Create a feature branch (Recommended for `all` mode and list mode)** — create `fix/issues-<short-slug>` or `fix/<id1>-<id2>` from HEAD. **Work on current branch** — commit to the checked-out branch and tell the user its name. **Set up a worktree instead** — offered only when `/bees-worktree-add` is installed; advise running it and exit without working.
- **Analyst.** Strip `### Deferred refinements` from the return, then surface the proposal as prose. Include `### Blast radius`, `### Decisions for writers`, and `### Policy decisions this change implies` in full, with their fixed lines `No invariant added, removed, or weakened.`, `None — the approach leaves no test or doc decision to the writers.`, and `None — the recommendation leaves no policy question open.` Precede it with a one- or two-sentence preamble keyed on `Analyst verdict:`. The preamble names the verdict — one of `recommend-as-stated`, `recommend-with-refinements`, `recommend-different-approach`, `escalate-to-user`. It leads with `⚠️` on `recommend-different-approach` and `escalate-to-user`. It names how many policy decisions the section carries when it is non-empty. It says when `### Blast radius` carries a scope-split recommendation. Then fire the gate. Question: `How should I proceed with this design proposal?` Options:
  - **Approve & proceed to implementation (Recommended)** — the directive is the `### Recommended approach`, `### Blast radius`, `### Decisions for writers`, and `### Policy decisions this change implies` verbatim plus `### Why`, `### Alternatives considered`, `### Options the body did not consider` as context. Approval covers the design, every policy answer, and any scope split. On Approve, consume the latest return's `### Deferred refinements`: each bullet annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` becomes a `defer-*` obligation; `addressed-now` bullets enter no ledger; a bullet with no destination is a malformed return, surface it. Superseded Revise iterations' obligations are closed; obligations from an earlier Approve survive a later re-fire.
  - **Revise** — discuss in prose; for a substantive change re-dispatch the Analyst with the same body and `reference_materials` plus `## Prior proposal and user feedback` quoting the prior proposal in full, `### Deferred refinements` included, and the feedback verbatim, then re-run this gate; light feedback is folded into the Approve branch; no cap on revisions.
  - **Cancel** — no commit, the Issue stays `open`, route through Section 12.
  - `Re-dispatch the Analyst with this finding` (gates (c) and (d)) is for a `blocker` showing the approved directive itself is wrong: re-dispatch the Analyst with the Revise shape carrying the finding verbatim as the feedback, then run this gate again; the new Engineer works against the current working tree. On an Approve reached from that re-fire, first mark every open writer, reviewer, and PM lane at this Issue `closed` and discard every finding raised under the superseded directive.
- **Unexplained movement.** Fires from the movement rung below when the movement cannot be attributed. The question carries the writer's movement report verbatim. It adds the statement *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths, so it cannot attribute the movement.* Options: **Re-dispatch the writer now** — next round against the current tree; **Wait** — yield; re-fire only on the operator's reply, never on a sibling lane's notification, which is processed normally; **Abort this Issue** — the Issue stays `open`, nothing is committed, route through Section 12.
- **Routing (c)** and **routing (d)** — Section 7.
- **Deferral hygiene** — Section 9. **Post-completion disposition**, **SR-6.7**, **SR-4.6** — Section 11. The context guard (Section 8) fires no gate; an over-threshold reading stops the run.

**Movement rung.** A Test Writer or Doc Writer return that reports it *stopped* on detected source movement is not a completion; fix mode is the strict branch, so any movement outside the writer's lane is anomalous. On a movement report: mark the writer's lane `closed`; open an `aborted-*` obligation at this Issue with the "how far I got" report as detail. Phase C does not begin while that obligation is `open`. Then attribute the mover:

- an Engineer → a precondition breach in fix mode; note it, let Phase A re-close, then re-dispatch;
- the sibling Phase B Test Writer whose `## Perturbations` lists every moved path → re-dispatch once it has returned, no gate. Do not classify while a dispatched Test Writer is still in flight; when Phase B dispatched none, `None`, or a partial list falls through;
- an external actor → re-dispatch once the tree has settled;
- unexplained → fire the gate.

The re-dispatch is the next round at the same scope and carries the "how far I got" detail. A normal deliverable from the re-dispatched lane closes the obligation; a second abort refreshes the same obligation's detail, never opens another.

**Engineer-dispatch precondition.** Never dispatch an Engineer for an Issue while a `## Lanes` row is `open` at that Issue for `test-writer`, `doc-writer`, `test-reviewer`, `doc-reviewer`, `pm`, or `analyst`. The Code Reviewer is the deliberate exception in that direction; Phase A alternates the two by construction. Resolve any `open` row per the `## Lanes` rule (Section 2), then re-check. An `aborted-*` obligation never blocks an Engineer round; it holds Phase C shut. The rule is symmetric at the Issue: never dispatch any other role while an Engineer lane is `open` there — disjoint files do not exempt it. Part (g) and the movement rung assume the source is settled when a writer reads it.

## 7. Routing discipline

### Orchestrator discipline: routing review findings

Each finding carries a severity tag, exactly one of `blocker` / `suggestion` / `nit`, and a depth tag on each fix path, exactly one of `trivial-tweak` / `refactor-locally` / `re-architect`, plus the count of fix paths. Turn them into exactly one routing decision per finding; never re-classify a depth tag. Definitions, shims (e) and (f), the anti-pattern (b), and all rationale live in the routing reference (Section 3); read it before routing when this section is not in view.

**Severity bounds the loop.** Severity decides what must be fixed before the unit ships: every `blocker`, `suggestion`, and `nit` a review raises is applied unless a gate or the premise check below dispositions it otherwise, and a `blocker` is never accepted. Whether a further reviewer round follows is decided by the kind of the fix, not by the finding's tag. Severity is consequence, orthogonal to depth; the levels and their one-line tests live in the routing reference (Section 3) and in the review skills, and the four kinds of change in the routing reference.

- Every implementer return carries `Kinds changed:` naming one or more of `code`, `tests`, `contract-text`, `comments` (Section 5). Confirm the line is plausible against the files the return lists: add a kind a listed file plainly requires, never remove one, and when the report is missing or you cannot tell, treat the pass as `code`. A comment edit inside a source file cannot be told from a code edit by its path; the implementer's report is the guard there and the sweep the backstop.
- **Hold set by kind.** A lane's first review is unconditional; this bullet governs every implementer pass that a review round's findings produced. If that pass changed `code` or `tests`, the lane stays open and its next cold pass reads the whole diff. Otherwise, if it changed `contract-text`, the pass gets one confirming read — a lane owes at most one — whose findings are applied in one final implementer pass before the lane closes. Otherwise it changed only `comments`: the lane closes, and the post-completion sweep (Section 11) is its reader. A row already written `close — text` whose final pass returns `code` or `tests` is rewritten to `another round` and the confirming pass is dispatched. Every review after a lane's first, and every `postcomp-*` reviewer, is dispatched as a confirming pass (Section 5): it reads the whole diff and answers two questions — is each fix correct, and did the pass falsify anything adjacent. The line `Confirming pass: <n> fixes checked` heads what the orchestrator reads for that lane — the reviewer's return, or that invocation's findings in a PM Final report; when it is absent the pass ran full — record `full pass` in that dispatch's ledger `notes` cell.
- A `code` or `tests` finding stays outstanding until a later cold pass no longer raises it, or it reaches a disposition under which **no fix lands against it**: accepted into the compromise tracker; recorded as a `defer-*` obligation; closed by `Accept the limitation`, `Cancel`, or a `Defer to follow-up Issue` that ships nothing this round; or closed `premise-false` by the premise check. A dispatch settles nothing — ungated at row 6, chosen at a gate, or the soft fix or narrowing a deferral ships alongside itself — until a later cold pass has read its result.
- **Apply, never defer, text findings.** A finding whose fix is `contract-text` or `comments` is applied in the lane's next implementer pass whatever its severity or depth. It is never filed as a follow-up for being text, never listed as ignored feedback, and never a `defer-*` obligation. At a site where the review runs inside the PM's in-flight passes, a pass the hold set closes the lane on means do not re-dispatch the PM for that lane; a `contract-text` pass's one owed read is a PM re-dispatch there.
- **Premise check.** In a skill whose escalation target (divergence table) is a design authority, a `blocker` or `suggestion` whose claim contradicts the approved design named there — or, for a PM finding, contradicts a prior clean Code Reviewer return that covered the same site — goes to that target before it is routed, with the finding verbatim, the contradicted text or return, and no implementer. Judge "contradicts" over the finding text and those returns, never over file contents; when the approved design or a prior return is unreadable, or the target is the operator, the check does not fire and the finding routes normally. `Premise check: premise-holds` → route the finding; `Premise check: premise-false` → list it under **Ignored Review Feedback** with the returned reason and dispatch nothing for it. Every finding of a round that meets the condition goes in one premise-check dispatch; the round's other findings wait for its return and route against the amended `## Blast radius`.
- **Earned-chain escalation.** When the lane's `## Rounds` row shows two consecutive `earned` classifications, the chain — every finding and fix since its first finding — goes to the escalation target instead of another implementer. When the chain is unreadable, the re-derivation shape (Section 4) applies where the target is the Analyst.
- **Late-chain enumeration.** When the lane's `## Rounds` row shows two consecutive `late` classifications and no `enumerated` one, its next review is the confirming pass plus `## Site enumeration requested` (Section 5): the reviewer lists every site the unit's change introduced and whether the artifact under review covers each, and returns the gaps as one finding. That round is classified `enumerated`, whatever it raised, so the enumeration fires at most once per lane. One implementer pass closes every listed gap. When that pass changed only `tests` or text, the lane closes with decision `close — enumerated` and the post-completion review reads it. When it changed `code`, the hold set owes one ordinary confirming pass, after which the lane closes `close — enumerated` unless that pass raises a `code` or `tests` finding, which routes normally. An empty gap list closes the lane `close — clean`; an unreadable enumeration return is a full pass.
- **Exit decision per round.** When a round's findings are routed, rewrite the lane's `## Rounds` row (Section 2) — classification, decision, count — before the action the decision names: the re-dispatch, the escalation, the final implementer pass, or marking the lane `closed`. Classify a round after the first by the first match in this list. A return that is itself unreadable is re-dispatched at the same round, never decided from a summary.
  - `enumerated` — the round was the late-chain enumeration (above), whatever it raised.
  - `clean` — the round raised no finding, or every finding it raised settled with no fix landing.
  - `text` — every finding it raised has a `contract-text` or `comments` fix.
  - `unavailable post-compaction` — the prior returns or dispatch prompts are gone.
  - `earned` — an outstanding `code` or `tests` finding, one no disposition settled, targets the previous round's fix.
  - `late` — otherwise: such a finding sits on older work no prior pass flagged.
- Render per lane, in its slot on the **Reviews** line of the summary for the scope that dispatched the review. Render `N rounds (earned/late/text/unavailable = a/b/c/d)` when the lane ran more than once, then `N text fixes applied without re-review`. `N` is the lane's round count and `d` counts rounds classified `unavailable post-compaction`; the remainder is the first round plus the `clean` and `enumerated` rounds, and an unavailable round is never rendered as `clean`. When a lane that ran carries no row in the manifest render `count unavailable post-compaction` rather than guessing.
- A finding whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding, and **what ships decides the hold**: a gate answer that ships `code` or `tests` — `Fix properly now`, or the soft fix or narrowing a `Defer` ships alongside itself — earns the confirming pass. When the final pass ships only text and changes source files, part (g)'s ordering applies with its code-review rung elided — that rung is the one round this rule suppresses.
- The post-completion review (Section 11) reads the whole diff, text fixes included; it is the cold pass those items receive, and the run's backstop.

**(a) Pick the path, then route on it.** **Step 1 — pick.** Choose the smallest enumerated fix path that fully fixes the stated defect as the finding describes it; take a deeper path only when every shallower one leaves that defect partly unfixed. A deeper path that changes code the stated defect does not touch — recurrence prevention, centralizing, restructuring — is not a fuller fix of the defect: pick the shallower path and record the deeper one as a `defer-*` obligation with destination `defer-to-new-Issue`, carrying the reviewer's sketch — the obligation records the unchosen path, not the finding, so the text-findings rule below is untouched. A `[preferred]` deeper path that covers, in the same artifact, a class of sites the finding names is the complete fix of that defect, not recurrence prevention. `[preferred]` on the shallower path confirms it; effort is a legitimate tiebreaker between paths that both fully fix the defect. The pick is always one of the enumerated paths. **Step 2 — route on the path chosen in Step 1.** Evaluate in order; first match wins.

| # | Condition (evaluated in order, first match wins) | Routing |
|---|---|---|
| 1 | The finding carries no depth tag, or a malformed severity/depth tag | Treat as `re-architect` → gate (d) |
| 2 | The chosen path carries the reviewer's `[introduces-mechanism]` tag, or introduces a mechanism by the orchestrator's own reading | Scope-bounding gate (c) |
| 3 | The chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers | Scope-bounding gate (c) |
| 4 | The chosen path is narrower than the smallest internally-consistent complete fix — it leaves the stated defect partly unfixed | Scope-bounding gate (c) |
| 5 | The chosen path's depth tag is `re-architect` | Routing-decision gate (d) |
| 6 | Otherwise | Dispatch the chosen path, no gate |

Row 6 dispatches the implementer per Section 5 — a resume at a scope it already worked — with the chosen path in full and appends a Trigger C entry (Section 10) in the same block. The one exception is a finding for which the reviewer enumerated exactly one path and it is `trivial-tweak`; a pick among two or more paths is always recorded, even when every path is shallow.

**(c) Scope-bounding gate.** Fires on rows 2, 3, and 4, and whenever the orchestrator would otherwise scope-bound a finding. The question carries the finding verbatim plus one line naming the entry condition.

- For a `suggestion` or `nit` the choices are `Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`; on a row-2 fire mark `Defer to follow-up Issue` `(Recommended)`.
- **Blocker rules:** `Accept the limitation` is never offered to a `blocker`. A `blocker` always gets its base pair. `Defer to follow-up Issue` is added only when the needed fix path introduces a mechanism AND that mechanism serves a case outside the stated defect; it is then paired with a narrowing dispatched after `/quo-file-issue` returns an Issue ID, and marked `(Recommended)`.
- `Fix properly now` re-dispatches the implementer to address the finding fully.
- `Defer to follow-up Issue` files via `/quo-file-issue` inline through the Skill tool, carrying the reviewer's sketched design verbatim, then ships the soft fix (Trigger A).
- `Accept the limitation` records the compromise (Trigger B) and proceeds.

**(d) Routing-decision gate.** Fires on rows 1 and 5. The question carries the finding verbatim. Choices: one per reviewer-surfaced fix path, its description carrying the path's depth tag, `(Recommended)` on the Step-1 pick; `Defer to follow-up Issue` — file via `/quo-file-issue` inline through the Skill tool carrying the finding verbatim, and ship no path this round (Trigger A); `Cancel`. A `blocker`'s `Defer` is offered only under gate (c)'s two conditions, on gate (c)'s terms.

| Divergence | `/quo-fix-issue` | `/quo-execute` |
|---|---|---|
| Approved-design source for "introduces a mechanism" | the approved directive from the Analyst gate — `### Recommended approach`, `### Blast radius`, and `### Policy decisions this change implies` | the Subtask body, its parent Task body, and the PRD/SDD the Plan Bee's `reference_materials` resolves to, or the Plan Bee body when null/empty |
| Blocker base pair at gate (c) | `Fix properly now` + `Re-dispatch the Analyst with this finding` | `Fix properly now` + `Cancel` |
| `Cancel` at gate (c) | none; `Ctrl-C` remains the run-level abort | in the `blocker` set only; ends the run via Section 12 |
| Gate (d) non-deferrable `blocker` set | per-path list + `Re-dispatch the Analyst with this finding` + `Cancel`; on an empty list mark the Analyst choice `(Recommended)` | per-path list + `Cancel`; on an empty list the question says the reviewer enumerated no fix path and the user directs the fix in free text or cancels |
| Gate (d) `Cancel` semantics | ends the current Issue; Section 12's mode branch decides the run | ends the run via Section 12 |
| Filing-failure re-prompt `Cancel` | at gate (d) only | at either gate on a `blocker`, at gate (d) otherwise |
| Part (g) code-review rung | the Code Reviewer, one clause | Clause 1: the per-Task PM's in-flight `/quo-engineer-review` pass; Clause 2: the Bee-level Code Reviewer, or at the Epic boundary the inter-Epic reviewer |
| Close-out target on `Cancel` / abort | `#### Aborted-Issue close-out` | `#### Aborted-run close-out` |
| Escalation target for the premise check and the earned-chain escalation | the Analyst, via the premise and chain rungs (Section 4); the premise check fires | the operator: the premise check does not fire (the finding routes normally); an earned chain fires the escalation gate (Section 6) |

**(g) Re-dispatch ordering when a fix path changes source.** Dispatch the Engineer first, then the code review for that site against the resulting diff. Only once that review has closed, dispatch the Test Writer and/or Doc Writer the change invalidated. The rounds are ordered, not concurrent, and gated by the Engineer-dispatch precondition (Section 6). One elision: on a final pass that ships only text, skip the code-review rung and dispatch the affected writer once the Engineer returns. A path that changes no source file re-dispatches that single writer lane alone. A finding raised at a review scope where no implementer worked — a Task or Bee finding in `/quo-execute` — routes to the implementer at the scope whose `## Files changed` names the finding's files, as a resume there; when none does, it is a fresh named dispatch at the finding's scope. A `postcomp-<n>` finding is dispatched by Section 11, not by this sentence.

Follow the review skills' routing trailer literally — `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`. When you ignore a finding, record it at that moment as a `defer-*` obligation with exactly one destination: `addressed-now`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue`; an `addressed-now` item enters no ledger. A finding closed `premise-false` is listed under **Ignored Review Feedback** with the returned reason and creates no obligation. A PM report note with no severity and no fix path is not a finding and is not routed. A missing-completeness-list finding on a dispatch whose list a compaction destroyed is a compaction artifact: list it under `**Ignored Review Feedback**`, create no obligation, dispatch nothing.

## 8. Per-unit close-out

**After each Issue.** When every finding is dispositioned and no lane at this Issue is `open`:

1. Re-read the status with `bees show-ticket --ids <issue-id>` and run `bees update-ticket --ids <issue-id> --status done` only if it is not already `done`.
2. Run the `Format` command from `## Build Commands`. Run the `Full test` command from `## Build Commands` only when the target project's CLAUDE.md requires a test run before a commit; the orchestrator runs no other rung on its own initiative. Give either command the Bash `timeout` parameter (max `600000` ms) when long; past that, `Bash(run_in_background: true)` and wait for the completion notification.
3. Run `git status`; stage agent-reported files plus formatting changes to files this Issue's agents touched. Resolve the in-repo Issues hive path with `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues` (PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues`) and when it prints one run `git add <emitted-issues-path>/<issue-id>`. **Do NOT blindly `git add -A`**.
4. Commit once with subject `Fix issue: <title> (<issue-id>)`, e.g. `Fix issue: Tighten dispatch contract gap (b.abc)`. **NEVER push to remote — committing only.** Record the commit SHA under `**Progress:**`.
5. Mark every lane and `aborted-*` obligation at this Issue `closed` — bookkeeping only; a returned Agent has already exited and there is no shutdown to perform. Output:

```markdown
## Issue [x] of [total] done: [issue-title]

**Issue**: <issue-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Test review: Y issues found/None needed | Docs review: Z issues found/None needed — each slot carrying its own `N rounds (earned/late/text/unavailable = a/b/c/d)` when the lane ran more than once, and its `N text fixes applied without re-review` when any (or "count unavailable post-compaction"), attributed by review site where a slot has more than one]
**Cost**: [N dispatches, T subagent tokens — the ledger rows at this Issue's scopes]
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
| **Trigger C — ungated route (the orchestrator's own path pick).** | in the same block as a row-6 dispatch; nothing when exactly one path was enumerated and it is `trivial-tweak` | `Orchestrator picked path (x) — highest-quality` | the orchestrator's one-line reason, not a rule name | `none` |
| **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).** | `Accept …` → append a new entry immediately after the pick; `File …` → update the originating Trigger C entry's `Follow-up Issue` in place, or append when none exists (SR-4.6); `Pause to discuss` → no write | `User overrode auto-route after post-completion challenge (depth misjudgment)` (SR-6.7) or `User accepted under-enumeration after post-completion challenge` (SR-4.6) | the reviewer's challenge text | the new Issue ID on `File …` |

## 11. Post-completion review

Scope: `git diff <pre-session-sha>` (the working tree against the pre-session commit) plus every untracked file from `git ls-files --others --exclude-standard`; a change no ticket body asks for is reported as likely pre-existing or an unticketed in-run edit, as an inference. `Read` the manifest for `<pre-session-sha>` and `<compromise-tracker-path>`; if the manifest is missing or names another batch, stop and tell the user rather than guessing the scope. Skip the sweep only when `git diff <pre-session-sha>` is empty and `git ls-files --others --exclude-standard` lists nothing, and say so; a landed commit is not the test, because an aborted Issue's uncommitted work is in scope.

1. `Read` the post-completion prompt reference (Section 3), fill its parameters (`<unit-noun>` = `fix`), add its lane row (role `general-purpose`, scope `postcomp`) per Section 5, and dispatch one fresh `Agent(subagent_type=general-purpose, run_in_background=true, prompt=…)` with the skeleton verbatim. Do not review the run yourself; do not invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review`. Wait for its report, then mark its lane `closed`.
2. Synthesize: compare its findings against the in-flight PM and reviewer verdicts and flag disagreements explicitly. When any `[compromise-challenge]` finding is present, lead with a `⚠️` preamble, e.g. `⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below.`
3. `no issues found` → print `Post-completion review: no issues found`; this section is complete.
4. Otherwise fire the disposition gate: `Post-completion review found [N] issues. How would you like to handle them?` Options: **Fix in this session**, **File as issue tickets**, **Skip**. Recommend `Fix in this session` when a PHASE 2 contract-violation `blocker` is present; that class has no recovery gate.
5. For each `[compromise-challenge]`, in the reviewer's emission order, fire the recovery gate its first line's phase names (PHASE 3 → SR-6.7, PHASE 4 → SR-4.6), before or alongside the disposition. Every other `[compromise-challenge]`, including one naming PHASE 2 or naming no phase, gets no recovery gate and rides the disposition gate. **SR-6.7 ungated-route recovery gate.** Choices: `File follow-up Issue to revisit the depth decision` — `/quo-file-issue` via the Skill tool with the finding and the tracker entry, then Trigger D's in-place update; `Accept the misjudgment and proceed` — Trigger D append; `Pause to discuss` — stop and discuss; the user re-issues a choice. **SR-4.6 under-enumeration recovery gate.** Choices: `File follow-up Issue to surface the missing path`; `Accept the under-enumeration and proceed`; `Pause to discuss`; same branch behavior.
6. Dispose per the answer:
   - **Fix in this session**: group the findings by implementer role — every finding whose fix is text or `trivial-tweak` joins one group per role, and every other finding is its own group. Each group is dispatched as one implementer pass at scope `postcomp-<n>`, `<n>` the group's lowest 1-based finding index, its prompt listing every finding in the group. Per-unit rules apply with each group's `postcomp-<n>` as the unit: lanes at that scope, the movement rung, and part (g) ordering. Groups whose fixes touch provably disjoint files run concurrently; all others run one at a time, in index order. The Engineer-dispatch precondition holds across every `postcomp-*` scope: a writer, reviewer, or PM lane waits for every `open` Engineer lane regardless of file overlap. An abort of a post-completion lane closes its rows here and continues this section; it never enters Section 12. A group's `Kinds changed` decides its reader under Section 7's hold set: `code` or `tests` is read by the reviewer lane its implementer maps to (Engineer → Code Reviewer, Test Writer → Test Reviewer, Doc Writer → Doc Reviewer) at scope `postcomp-<n>` with its own `## Rounds` row; `contract-text` only gets that mapped reviewer's one confirming read; `comments` only gets its implementer pass and no reviewer.
     - Close-out: when every finding's lanes have run and are `closed` and no `aborted-*` obligation at a `postcomp-*` scope is `open`, run the close-out `Format` rung (Section 8). Stage the files the `postcomp-*` lanes reported plus formatting changes to them, never `git add -A`. When anything is staged, commit once with subject `Post-completion review fixes for <issue-ids>`, the batch's Issue IDs from `**Unit scope:**`, unparenthesised because the parenthesised `(<ticket-id>)` token marks per-unit commits only; never push. Then print one `**Reviews**` line over the `postcomp-*` rows, one slot per reviewer lane, in the slot format of Section 8.
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

Before yielding, follow the GitHub close reference (Section 3): emit `Upstream GitHub Issues to consider closing:` with one `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` bullet per fixed Issue whose `reference_materials` carries a `github-issue` resolver, or nothing when none does. The skill never runs `gh issue close` itself. Print `**Cost**: <dispatches> dispatches, <tokens> subagent tokens, <wall clock>` over every ledger row, the wall clock running from `**Run started (UTC):**` to the current UTC time read once with `date -u +%Y-%m-%dT%H:%M:%SZ` (PowerShell `Get-Date -AsUTC -Format yyyy-MM-ddTHH:mm:ssZ`). Then yield.
