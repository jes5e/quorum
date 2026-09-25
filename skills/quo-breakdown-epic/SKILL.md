---
name: quo-breakdown-epic
description: Break down a Plan Bee's drafted Epics into Tasks and role-tagged Subtasks, drafted against the spec, checked by a cold PM traceability review, then created as tickets. Pass an Epic ID or a Bee ID, or nothing to pick a Plan Bee with drafted Epics.
argument-hint: "[<epic-id> | <bee-id>]"
---

Turn each drafted Epic of a Plan Bee into Tasks and Subtasks that `/quo-execute` can run: draft them against the spec, have a cold PM check the draft covers the spec, then create the tickets and commit them.

## 1. Preconditions

Hard-fail with `Run /quo-setup first.` plus a one-line reason when `bees list-hives` lacks the `plans`, `issues`, or `specs` hive (by `normalized_name`), or the target repo's CLAUDE.md lacks `## Documentation Locations` or a `## Build Commands` section carrying `Compile/type-check`, `Format`, `Lint`, `Narrow test`, and `Full test`. If a dispatch fails with `Agent type '<name>' not found`, stop with `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` and name the draft file, which survives on disk.

**Working rules for every step.**

- bees is the ticket store; `bees <command> -h` and `bees sting` document it. It has no ticket list or search verb: enumerate with `bees execute-freeform-query`, pass the query on one line in YAML flow style (`{stages: [[...]], report: [...]}`), and name the fields you need in `report:`.
- Write every file this run creates (the manifest, the draft, body files) under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), creating the directory if absent. Never delete them: they are the record of a crashed run. Give each a collision-resistant name, except the manifest (Section 2).
- Pass every multi-paragraph ticket body with `--body-file`, never inline, because a newline followed by `#` trips Claude Code's command-injection guard.
- Run each shell command as one literal command, with no pipes, chains, or `$` substitution, because those shapes re-prompt the user for permission; put multi-step logic in a Python script instead.
- Ask free-text questions in prose. `AskUserQuestion` is multi-choice only and appends its own free-text slot, so never add an option that points at it.

## 2. Run-state manifest

#### Write the run-state manifest

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds the tickets and git holds the commits; the manifest holds the rest. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Its name is `run-state-quo-breakdown-epic-<bee-id>.md`, keyed on the Plan Bee every Epic belongs to. **The filename is deterministic — do NOT add a random suffix or timestamp.** After a compaction you recompute the path from the Bee ID rather than remember it. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends, so a `/quo-execute` run on the same Bee never touches this file. Accepted collision: two breakdown runs on one Bee at once share it, and they already collide over tickets.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it as soon as the Bee is known, rewrite it whenever a value changes, and never delete it.

```markdown
# Run state — quo-breakdown-epic @ <bee-id>

**Run mode:** <Stop after each Epic | Work through all Epics | one Epic | pending>
**Draft:** <epic-id> at <draft-path>, or none
**Broken down:** <Epic N = <epic-id>, …, or none>

## Obligations

| item | destination | status |
|---|---|---|

## Open gate

none
```

The run mode is a user choice nothing else records, and **Broken down** lets the run-end report tell this run's Epics from earlier ones. Conversation memory is never a substitute for the manifest, the draft, and bees, because the harness can drop old tool results without a marker. After a compaction, re-read them and reconcile with the working tree before acting: an Epic that is `ready` with Tasks is done, and the recorded **Draft** is the Epic in progress.

## 3. Gates

A gate is the manifest `Write` that fills `## Open gate` with the gate's name, question, and choices, then `AskUserQuestion` in the same turn. The tool call in the same turn is what keeps a gate from being described and left unasked, which stronger wording has not prevented. Set `## Open gate` back to `none` once the answer is consumed. Keep every choice label to five words or fewer.

Gates fire only where the user holds the decision:

- **Session effort** — first, before the manifest exists, so it goes straight to `AskUserQuestion`. Read `printenv CLAUDE_EFFORT` (PowerShell `Write-Output $env:CLAUDE_EFFORT`). If it is empty or not one of `low` < `medium` < `high` < `xhigh` < `max`, skip silently. At or above `high`, say nothing. Below it, ask ``This session is running at `effort=<current>`, below the `high` floor this skill is tuned for. Decomposition quality here sets Subtask granularity for every downstream execution run.`` then a blank line then `Subagent effort is pinned per role and is NOT affected by this setting.` Choices: **Proceed anyway**, or **Let me change it first** (exit; the user runs `/model` and re-invokes).
- **Bee pick** — with no argument and several Plan Bees that have a `drafted` Epic, before the manifest exists: one choice per Bee, up to four; the free-text slot takes any other.
- **Run mode** — when two or more `drafted` Epics remain: question `How should this run handle multiple Epics? (You will not be asked again this run.)`; choices **Stop after each Epic** and **Work through all Epics**. The labels match `/quo-execute`'s, so the choice reads the same in both skills.
- **Deferral hygiene**, only when obligations are open — Section 9.
- **Next steps** — Section 9.

## 4. Pick the Epic

- **An Epic ID** starts at that Epic; its parent is the Plan Bee.
- **A Bee ID** starts at its first `drafted` Epic in dependency order.
- **No argument** takes the one Plan Bee with a `drafted` Epic, or fires the Bee pick when there are several. With none, suggest `/quo-execute <bee-id>` for a `ready` or `in_progress` Plan Bee, else `/quo-plan` or `/quo-plan-from-specs`.

When the Bee has no `drafted` Epic, say so and suggest `/quo-execute <bee-id>`. Otherwise write the manifest, then fire the run-mode gate when it applies and record the answer.

## 5. Read the Epic and its spec

Read the Epic, its Plan Bee, the Epics it depends on, and its sibling Epics. Treat the dependencies as done and build on them. Leave a sibling's scope to that sibling.

The spec is what the Plan Bee's `reference_materials` names:

- **A `bees` entry** names a Spec Bee. Its `t1=Doc` children titled exactly `PRD` and `SDD` are the spec; match those titles exactly, never loosely.
- **A `file-path` entry, or one with no `resolver`,** is a doc on disk. When the Plan Bee body carries a `Scoped to` marker, write the body text (not the `bees show-ticket` JSON) to a scratch file and run the bundled resolver: `python3 "<this skill's base directory>/scripts/scoped_marker_resolver.py" <body-file>` (PowerShell `python "<this skill's base directory>\scripts\scoped_marker_resolver.py" <body-file>`). Its `"scoped": true` output restricts the spec to the named `### Feature:` subsection. Exit 2 means the marker is broken: report its stderr and stop, never falling back to the whole doc. The marker applies only to this path.
- **No entry** means the Plan Bee body is the spec.

Also read `## Anticipated doc impact` in the Plan Bee body; it names the docs the feature changes.

## 6. Draft the Tasks and Subtasks

**Research.** Before drafting, dispatch read-only `Explore` agents in the background over the code the Epic touches, in proportion to the Epic, and wait for their notifications. Code reading goes to them, and they return findings rather than file contents, because your context has to hold the spec and the draft for the whole Epic.

**Draft to one file**, recorded as the manifest's **Draft**, with one heading per ticket: `# Task N — <short title>` for each Task, and under it `## <role>: <short title>` for each Subtask. The review cites these labels, because no ticket IDs exist yet. Keep the template's headings at `##` inside each ticket's text, as its ticket will carry them.

**Tasks.** N is the Task's 1-based position in the Epic, and the title is its label in every later status line and commit.

- Each Task is one commit's worth of work, since `/quo-execute` commits per Task. Give it `up_dependencies` on the Tasks that must land first.
- A Task body states the Task's purpose and any contract a sibling Task or Epic must respect: an ordering, a shared resource, an invariant, or a cleanup path every sibling must follow. Reviewers check sibling Tasks against these statements, and a contract left in the author's head surfaces later as a cross-Task defect.
- When the spec's SDD has `### Mechanism lifecycle` or `### Policy decisions this design implies`, list under `## Sites` each entry the Task implements, citing the SDD child's ID and the entry, so the implementer works against a list.
- Acceptance criteria and per-role work live in the Subtasks, not the Task.

**Subtasks.** Each body uses this template:

```
## Context
Why this Subtask exists and what it assumes.

## What Needs to Change
The files, functions, and changes, with line numbers where known.

## Key Files
- path/to/file — what changes here

## Acceptance Criteria
- Observable, testable conditions, e.g. "function X returns Y", not "function works correctly"
```

- Give each Subtask exactly one role tag — `engineer`, `test-writer`, or `doc-writer` — for the role that executes it; `/quo-execute` dispatches by that tag. A step only the operator can run is tagged `engineer`, and its body says the implementer stops and asks the operator to run it.
- Every Task that changes code, configuration, or deployment gets a `doc-writer` Subtask, seeded from `## Anticipated doc impact`: the Doc Writer decides which docs change, so do not judge that no doc does.
- State scope and acceptance, not implementation; paste no code. The implementer is an expert, and the code will move before it runs.
- Carry any design decision the user gave you verbatim into every Subtask it affects. When the spec leaves open a choice the Tasks must commit to, ask in prose before drafting past it.
- Emit no Subtask for committing, formatting, or running the full test suite. `/quo-execute` does those itself.
- Give a Subtask `up_dependencies` only on a same-role Subtask it builds on; `/quo-execute` orders the roles itself.

## 7. Traceability review

Dispatch one `pm` agent in the background with this prompt, IDs and paths filled in, and wait for its notification. The operator's design gives the PM final authority on whether the breakdown covers the spec, and the review runs before any ticket exists, so a fix changes the draft, not tickets.

```
You are reviewing a draft breakdown of Epic <epic-id> under Plan Bee <bee-id>,
before any of its tickets exist. There is no diff: do not invoke
/quo-engineer-review or /quo-doc-writer-review, and change no ticket and no
file outside the .quorum scratch directory (/tmp/.quorum/, or %TEMP%\.quorum
on Windows).
The draft is <draft-path>: one `# Task N — <title>` heading per Task, and one
`## <role>: <title>` heading per Subtask under it. Cite those labels.

Resolve the spec from the Plan Bee's reference_materials as your role file
describes, with the Plan Bee as the Grandparent Bee, so its Path A
Scoped-marker check applies; the helper is at <scoped-marker-resolver-path>.

1. Map every requirement the spec places in this Epic's scope, and each of the
   Epic's acceptance criteria, to the Subtasks that cover it, in this table:

   | Spec Requirement | Source | Covered By Subtask | Status |

   Source cites where the requirement lives in the spec. Status is `OK` or `GAP`.
2. Run your role's cross-Task and cross-Epic interaction checks over the draft,
   and flag work the spec does not ask for.
3. Report every other finding in your Final report shape. A finding the draft
   should fix is `addressed-now`. A deferral names
   `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`; no
   project-doc destination.
```

`<scoped-marker-resolver-path>` is `<this skill's base directory>/scripts/scoped_marker_resolver.py`. Fix every `GAP` and every `addressed-now` finding in the draft, and dispatch the review again only when the pass reported a `GAP`. Add each deferred item not already in `## Obligations` as the review returns it: the next session reads only tickets, so a deferral held in this conversation is lost.

## 8. Create, commit, and move on

**Create** the tickets from the reviewed draft. Each Task is a `t2` child of the Epic and each Subtask a `t3` child of its Task, created `drafted` with its title, body, role tag, and `up_dependencies`. Once all exist, set the Subtasks, then the Tasks, then the Epic to `ready`. Add the Epic to **Broken down** and set **Draft** to `none`.

**Commit.** Stage only the in-repo Plans-hive path the sibling helper prints, never the whole tree, because the hive may live outside the repo and the working tree may hold unrelated changes: `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive plans` (PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive plans`). Commit with the subject `Plan <bee-id>, Break down <epic-title> (<epic-id>)`, where `<epic-title>` is the Epic's `Epic N — <title>`. When the helper prints nothing, commit nothing and note in the report that the tickets live outside the repo. Never push.

**Move on.** Under **Work through all Epics**, when a `drafted` Epic remains and none of them consumes a contract an Epic broken down this run will reshape (Section 9), print `Mode 2 (Work through all Epics): continuing to <Epic N — title>.`, run the context guard, and return to Section 5 for the next `drafted` Epic in dependency order. Otherwise the run ends: go to Section 9.

**Context guard.** It runs before every Epic broken down in the same session after the first. Read `printenv CLAUDE_CODE_SESSION_ID` (PowerShell `Write-Output $env:CLAUDE_CODE_SESSION_ID`) and trim it; unset or empty → skip. Get the threshold from `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold` and the reading from `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-id>` (PowerShell: `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py"` with the same arguments). A reading at or above it, `stale`, a non-zero exit, or empty output ends the run through Section 9, recommending `/quo-breakdown-epic <bee-id>` in a fresh session, so the next Epic starts fresh rather than being compacted mid-draft. Below the threshold, `no-reading`, or `missing` → continue.

## 9. End of run

**Report** each Epic broken down this run: its Tasks by label with their Subtasks' roles, statuses, and dependencies, and the `GAP`s the review found and how the draft closed them.

**Deferral hygiene.** When `## Obligations` has no open row, print `Deferral hygiene: no deferred items.` Otherwise list the open rows and fire the deferral-hygiene gate. The user can route different items differently by writing that in the free-text slot.

- `Fix in this session` — do the work now, and commit the ticket files it changed, staging the in-repo path of each hive it touched (the helper's `resolve-hive-paths` with that `--hive`).
- `File as issue tickets` — invoke `/quo-file-issue` through the Skill tool with the item as its description.
- `Encode in existing ticket` — append a `## Deferred from /quo-breakdown-epic run (<YYYY-MM-DD HH:MM>)` section to the named ticket, keeping its existing body. The timestamp keeps several runs' sections apart. You have no clock, so take it from `date +'%Y-%m-%d %H:%M'` (POSIX) or `Get-Date -Format 'yyyy-MM-dd HH:mm'` (PowerShell). Then commit the encodes with `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" --skill quo-breakdown-epic --count <N>` (PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" --skill quo-breakdown-epic --count <N>`), where `<N>` counts the items encoded.

Close each row as its item lands. Do not end the run while a row is open; when a route fails, show the remaining rows and ask again.

**Next steps.** Skip this gate when the context guard ended the run. Before firing it, say in one line that each next skill re-reads everything from bees and disk, so a fresh session gives it the full context budget. Fire the next-steps gate with these choices, the two break-down choices only when a `drafted` Epic remains:

- **Execute in fresh session** — run `/quo-execute <bee-id>` in a new session. It runs every workable Epic in dependency order and stops at `drafted` ones.
- **Next Epic, fresh session** — run `/quo-breakdown-epic <bee-id>` in a new session.
- **Next Epic, this session** — run the context guard, then return to Section 5 for the next `drafted` Epic.
- **Done for now** — the plan is saved.

Recommend **Execute in fresh session** when no `drafted` Epic remains, or when an Epic broken down this run will reshape a contract a remaining sibling consumes: new infrastructure, API surface, schema, or framework that the sibling is written to use. Breaking that sibling down now would produce Tasks that go stale. Pure ordering between Epics is not reshape risk; then recommend **Next Epic, fresh session**. Put the reason in the recommended choice's description, naming the sibling Epics, and never in a paragraph above the question, which the UI truncates.
