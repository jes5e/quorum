---
name: bees-breakdown-epic
description: Break down a single Epic into Tasks. User can provide Epic ID or a Bee ID and skill finds Epics that are ready
argument-hint: "[<epic-id> | <bee-id>]"
---

# Epic to Tasks

Your job is to break down an Epic ticket into Tasks and Subtasks.

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The seven required custom subagent types are registered in the running Claude Code session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. Custom subagents are loaded at Claude Code session start (from `~/.claude/agents/` for global installs and `<repo>/.claude/agents/` for per-project installs), so a fresh install requires a Claude Code restart (or `/agents` to hot-reload) before the skill can dispatch them. Although this skill only dispatches a subset of these roles in research mode, the precondition is uniform across the three execution skills (`/bees-execute`, `/bees-fix-issue`, `/bees-breakdown-epic`) so a "user forgot to restart Claude Code" misconfiguration is caught identically regardless of entry point. If any of the seven is missing at run-time, the orchestrator STOPS at the precondition gate and emits the hard-fail message — there is no fallback to `general-purpose`, no skipping the dispatch, and no improvising substitute roles. The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents` to hot-reload, e.g.: `Run /bees-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`
- The Plans hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `plans`.
- The Specs hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /bees-setup first. — Specs hive is not colonized for this repo. Re-run /bees-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section. Agents look up paths to architecture docs, customer docs, test guides, etc. by exact key from this section.
- CLAUDE.md contains a `## Build Commands` section, and that section has all five required bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. Agents look up build/test/format/lint commands by exact key from this section.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The Build Commands section is required, not optional.

Do not attempt to recover from a missing precondition by improvising commands or guessing paths — fail fast and direct the user to `/bees-setup` so the configuration is captured deliberately.

**Verifying the subagents precondition.** Verification is a hybrid of two complementary mechanisms:

- **Procedural gate (load-bearing primary).** If a dispatch later in the run hits an `Agent type '<name>' not found`-style error from the Agent tool for any of the seven required subagent types, the orchestrator STOPS, emits the hard-fail message above, and exits — no fallback to `general-purpose`, no skipping the dispatch, no substitute role. This gate is honest about Claude Code's session-load semantics (subagents are loaded at session start from `~/.claude/agents/` and `<repo>/.claude/agents/`; mid-session installs require a restart or `/agents` hot-reload) and cannot be bypassed by token-budget pressure or model creativity, because it fires at the natural failure point.
- **Upfront fast-fail (opportunistic, belt-and-braces).** Before any dispatch is attempted, run `claude agents` to enumerate registered subagents and verify each of the seven literal names (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`) is present. The command prints one line per agent in the form `  <name> · <model>` under a `User agents:` heading, exits cleanly without spawning an interactive UI, and is safe to invoke from inside a running Claude Code session. If any of the seven names is absent from the output, hard-fail per the message above. This catches the missing-restart case upfront and saves the user one wasted dispatch turn.

```bash
# POSIX (bash / zsh):
claude agents
```

```powershell
# Windows (PowerShell):
claude agents
```

After running the command, scan its output for the seven required names; hard-fail if any are missing. If `claude agents` itself is unavailable (older Claude Code build, etc.), skip the upfront check — the procedural gate still catches the failure at first dispatch.

## Workflow

### 0. Choose agent model preference

Before starting work, ask the user which model to use for the support roles spawned during breakdown (research Agents, Product Manager when applicable). Use `AskUserQuestion`:

- Question: "Which model should support agents (research Agents, PM, Doc Writer-equivalent) use?"
- Options:
  - **Opus (Recommended)** — highest quality, slower, more expensive
  - **Sonnet** — fast and cost-effective, good for straightforward tasks

The core implementation-shaping role (the orchestrator — you) always uses **Opus**. Store the user's choice and apply it when spawning research Agents throughout this breakdown.

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
- Read the source material linked from the parent Bee's `reference_materials`. **If `reference_materials` is null/empty** (Plan Bees authored via `/bees-plan` for features without a separate PRD/SDD), the Plan Bee body itself is the authoritative scope document — read it carefully in place of the `reference_materials` sources, and substitute "the Plan Bee body" wherever subsequent prose references "the PRD" or "the SDD".

  **Resolving `reference_materials` entries.** When `reference_materials` is non-empty, iterate the array and dispatch on each entry's `resolver` field. This mirrors the canonical lookup logic in `agents/pm.md` `### Resolving reference_materials entries` — divergence is a defect; if you find yourself improvising a different shape here, stop and re-read `agents/pm.md`.

  - **`resolver` is `file-path` (or omitted — default).** Treat the entry's `value` as a path on disk and read the file. This is the existing behavior; nothing changes on this path. The Scoped-marker integration documented below applies on this path.
  - **`resolver` is `bees`.** Treat the entry's `value` as a Spec Bee ID in the `specs` hive, and walk the two-hop path `Spec Bee → t1=Doc children → PRD / SDD content`:

    1. Run `bees show-ticket --ids <spec-bee-id>` and read the response's `children` array — these are the Spec Bee's `t1=Doc` children.
    2. For each child ID, run `bees show-ticket --ids <child-id>` and read the response's `title` and `body` fields.
    3. Identify PRD vs SDD content by **exact-match (case-sensitive) on `title`**: a child whose `title` equals `PRD` carries the PRD content in its `body`; a child whose `title` equals `SDD` carries the SDD content. Use those bodies as the spec source in place of file content.

    The `PRD` and `SDD` title strings are a cross-Epic contract; do not lower-case, normalize, or fuzzy-match. The freeform-query route (`bees execute-freeform-query --query-yaml '<yaml>'`) is also acceptable and is preferable when you want title-filtered enumeration up-front; see `docs/doc-writing-guide.md` `## Querying tickets` for the recipe vocabulary.

    ```bash
    # POSIX (bash / zsh):
    bees show-ticket --ids <spec-bee-id>
    ```

    ```powershell
    # Windows (PowerShell):
    bees show-ticket --ids <spec-bee-id>
    ```

    ```bash
    # POSIX (bash / zsh):
    bees show-ticket --ids <child-id>
    ```

    ```powershell
    # Windows (PowerShell):
    bees show-ticket --ids <child-id>
    ```

- **Check for the Scoped-marker on the parent Bee.** **Skip-on-bees pre-branch.** If any `reference_materials` entry that supplied spec content for this Epic resolved via `resolver: bees` (the two-hop Spec Bee + `t1=Doc` children walk above), **skip Scoped-marker resolution entirely** for that content: do not write a temp file, do not invoke the helper, do not parse exit codes. Spec Bees are already feature-scoped (one Spec Bee per feature), so marker-based subsection narrowing is irrelevant on that path — the `body` of the `PRD`/`SDD` child tickets is already the authoritative scoped spec content. The remainder of this bullet (helper invocation, exit-code handling, hard-fail on malformed marker) applies **only** to the file-resolver path and the body-as-spec fallback path; nothing in those subsections is relaxed by this pre-branch.

  On the file-resolver path (or the body-as-spec fallback), if the parent Bee's body contains a line of the form `` Scoped to `### Feature: <title>` from <prd-path> and <sdd-path>. `` (emitted by `/bees-plan-from-specs --feature "<title>"`), the resolved doc content must be restricted to the matching `### Feature: <title>` subsection in each named doc before treating it as the spec. Run the bundled parser/scoper to do the detection and scoping in one step:

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

  The helper exits 0 with a JSON object on stdout. When `"scoped": false`, no marker was present — proceed with the full resolved doc content as today. When `"scoped": true`, the JSON's `docs` array carries the scoped subsection content per doc path; use that scoped content for all subsequent Task decomposition, sibling-overlap checks, and the Spec Traceability Review (cite `### Feature: <title>` subsection coordinates rather than the full PRD/SDD when the marker is present). The helper exits 2 with a clear error on stderr if the marker is present but malformed, names a doc that is missing on disk, or names a heading that does not exist in the doc — surface that error to the user and stop; do not silent-fallback to the full doc. The Scoped-marker grammar and the helper contract are documented in `docs/doc-writing-guide.md` `## The Scoped-marker contract`.

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

### 4. Break each Task into Subtasks via per-Task ephemeral research Agent dispatch

For each Task drafted in Step 3, the orchestrator (you) drives Subtask authorship through a **reconciliation loop** that dispatches **fresh, ephemeral background `Agent` invocations** against the custom subagent types defined in this skill set's sibling `agents/` directory. There is no long-lived team; there are no warmed Agents; there is no peer-to-peer messaging between workers. This mirrors the dispatch shape used by `/bees-execute` Section 3, scoped to **research-only mode** — workers read code and return JSON-structured findings as text, and only YOU run `bees create-ticket`, `bees update-ticket`, or `bees delete-ticket`.

Your responsibilities are:

- Surface design questions back to the Caller. If dispatched research Agents propose different approaches to the same problem, surface the divergence back up to the caller with an `AskUserQuestion`.
- Coordinate the dispatched research Agents and ensure all work is complete, **but the Product Manager has final authority on quality and completeness** of the proposed Subtask breakdown.
- **Carry forward architectural decisions.** If the caller provides architectural decisions or constraints (e.g., "make parameter X optional with fallback Y"), explicitly reference them in every affected subtask description. Do not paraphrase or partially apply — use the caller's exact specification.

**You do not author Subtasks yourself.** Subtask proposals come from the dispatched research Agents; the orchestrator's job is to invoke the right role at the right time, integrate the returned JSON findings, and create the actual bees tickets.

#### Reconciliation loop

The loop is **event-driven, not clock-driven**. Each tick has three phases:

1. **Read state.** Pull the current truth from the relevant sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <epic-id>` to get the Epic's `children` array (Task IDs); for each Task, fetch its full body. Identify the next Task that still has no Subtasks proposed (or whose proposed-Subtasks set is incomplete pending PM review). Use the canonical querying recipe (see `docs/doc-writing-guide.md` `## Querying tickets`) for any focused state query.
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight research Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done with its JSON findings).
   - **Returned findings** — the JSON-structured text each completed research Agent returned. These are the load-bearing handoff: the orchestrator consumes the JSON to compose `bees create-ticket --body-file` invocations.

2. **Reconcile.** Compare current state to target state and act:
   - For the current Task, dispatch the relevant subset of research Agents (Engineer / Test Writer / Doc Writer) per the role-selection rules below. PM dispatch is reserved for the Task-level review boundary.
   - For every research Agent that has reported completion, persist the result: parse the returned JSON, author Subtask body files via the `Write` tool, run `bees create-ticket --body-file <path>` for each proposed Subtask (the orchestrator is the only thing that mutates bees state), and mark the corresponding TaskList task `completed`.
   - When all implementer-research Agents for the current Task have returned and the orchestrator has created the proposed Subtasks, dispatch a fresh PM research Agent for the per-Task PM review (see "Per-Task PM dispatch" below).
   - When the PM signs off on the Task's Subtask set, advance to the next Task.
   - When all Tasks of the current Epic have a PM-approved Subtask set, advance to Section 5.

3. **Yield.** The orchestrator does not poll. After dispatching the work this tick uncovered, return control to the harness and wait for the **Agent completion notification** delivered by the `run_in_background=true` substrate. The notification is what triggers the next tick.

##### Anti-pattern: no clock primitives

The reconciliation loop is driven exclusively by Agent completion notifications. Do **not** use any of:

- **`/loop`** — repeats the orchestrator's last turn on a wall-clock cadence.
- **`ScheduleWakeup`** — fires the orchestrator after a delay.
- **`CronCreate`** — fires the orchestrator on a recurring schedule.
- **Polling** — re-reading bees / TaskList / returned findings on a sleep-wait cycle without a triggering event.

If the work for this tick is dispatched and there is nothing else to reconcile, the correct action is to yield. Background research Agents will wake the orchestrator when they finish; that is the only legitimate trigger for the next tick.

#### Per-Task cold dispatch (research-only)

For each Task, the orchestrator spawns one fresh research Agent per applicable role at Task scope:

```
Agent(
  subagent_type=<role>,            # one of: engineer, test-writer, doc-writer, pm
  run_in_background=true,
  prompt=<research-mode preamble + ticket body verbatim>,
)
```

Role selection per Task:

- If source code needs to be changed, dispatch `subagent_type: "engineer"`. If not, the Engineer is optional.
- If unit-test code needs to be changed, dispatch `subagent_type: "test-writer"`. If not, the Test Writer is optional.
- If the Task changes source code, configuration, or deployment, dispatch `subagent_type: "doc-writer"` — the Doc Writer decides what docs need updating (customer-facing docs, internal architecture docs, etc.). Do not pre-judge whether docs need changes; that assessment is the Doc Writer's job. The Doc Writer is only optional for Tasks that are purely research or planning with no code/config changes.
- Always dispatch `subagent_type: "pm"` at the per-Task review boundary, after the implementer roles have returned and the orchestrator has created their proposed Subtasks.

The full role contracts (responsibilities, gating preconditions, instructions) live in the role files; the orchestrator's job is to invoke the right role at the right time, not to carry the role's prose. Each `subagent_type` name above corresponds to a contract file:

- **`subagent_type: "engineer"`** → `agents/engineer.md`
- **`subagent_type: "test-writer"`** → `agents/test-writer.md`
- **`subagent_type: "doc-writer"`** → `agents/doc-writer.md`
- **`subagent_type: "pm"`** → `agents/pm.md`

Each Task gets its own per-role Agent invocation. The orchestrator does **not** name Agents (`Agent(name=...)` is not used) and does **not** reuse an Agent across Tasks. There is no `SendMessage` between research Agents — each worker reads its assignment from the dispatch prompt, returns its JSON findings, and exits.

##### Research-mode preamble

The research-mode preamble in the dispatch prompt is what makes a research dispatch a research dispatch. The Implementation note on the parent Epic body explicitly states this is signaled via prompt rather than by introducing separate research-mode subagent types — trust the prompt; do **not** introduce `engineer-researcher`, `test-writer-researcher`, etc. The same `engineer` / `test-writer` / `doc-writer` / `pm` subagent types used by `/bees-execute` are reused here, gated to read-only behaviour by the preamble.

The preamble must include the following research-mode instructions verbatim:

```prompt
You are operating in READ-ONLY RESEARCH MODE.

- You MUST NOT modify any files. Do not invoke `Edit`, `Write`, or any
  file-mutating tool against project sources or docs.
- You MUST NOT mutate bees state. Do not run `bees create-ticket`,
  `bees update-ticket`, or `bees delete-ticket`. Only the orchestrator
  creates and updates tickets.
- You MUST return your findings as JSON-structured text — a single JSON
  object describing the proposed Subtasks (one entry per proposed Subtask,
  each with a title, body following the mandatory Subtask Description
  Template, and any up_dependencies on sibling proposed Subtasks). Return
  the JSON as your final assistant message; do not write it to a file.
- Read code, read docs referenced in CLAUDE.md `## Documentation Locations`,
  and consult `docs/doc-writing-guide.md` for query recipes if you need to
  enumerate tickets. That is the full extent of your tool use.
```

##### Dispatch prompt: quote the ticket body verbatim

The dispatch prompt sent to each research Agent must embed the parent Task body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names, file paths) that the worker will then reason about literally. Read the Task via `bees show-ticket --ids <task-id>` and embed the returned body in the prompt as a quoted block immediately after the research-mode preamble. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "you are dispatched in research mode for this Task") is fine; the body itself stays untouched. The orchestrator's progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

##### Procedural-gate fallback

If the first research dispatch (or any later dispatch) returns an `Agent type '<name>' not found`-style error from the Agent tool for any of the four research roles (`engineer`, `test-writer`, `doc-writer`, `pm`), STOP at the procedural gate and emit the hard-fail message defined in this skill's `## Preconditions` section — do not fall back to `general-purpose`, do not skip the dispatch, do not improvise a substitute role. This is the load-bearing primary verification mechanism for the subagents precondition: the `claude agents` upfront fast-fail catches most cases before the first dispatch, but the procedural gate is what ultimately enforces the contract honestly against Claude Code's session-load semantics.

#### Hub-and-spoke via substrate

Workers do not message each other. The orchestrator is the hub; each dispatched research Agent is a spoke that reads its prompt, returns findings as text, and exits. The JSON-structured findings text is the handoff to the orchestrator's next reconciliation tick — when an implementer-research Agent returns its proposed-Subtask JSON, the orchestrator parses it, authors body files, and runs `bees create-ticket`; when the PM research Agent returns its traceability findings, the orchestrator acts on them by dispatching gap-fill research Agents or transitioning tickets to `ready`. Hub-and-spoke is a **structural property** of ephemeral background research Agents, not a rule the orchestrator must remember to enforce: there is no inter-Agent channel for workers to even attempt peer-to-peer coupling on.

#### Recursive delegation: not supported

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every research Agent invocation originates from this skill's reconciliation loop, never from a worker. The bound on flat-orchestration context growth in this skill is the per-Epic scope of the loop itself — when this skill returns at Section 7, the orchestrator's working context is released back to the caller's session, so the loop's running set stays bounded by a single Epic's breakdown.

#### Per-Task PM dispatch

When the implementer-research Agents (Engineer / Test Writer / Doc Writer, as applicable) have all returned for the current Task and the orchestrator has created the proposed Subtasks via `bees create-ticket`, dispatch a fresh PM research Agent. The dispatch prompt must include the Task ID, the list of proposed Subtask IDs the orchestrator just created, and the research-mode preamble — the PM, like the other roles, is read-only here. The PM's job is to review the proposed Subtask set against the Epic's spec source and return JSON findings flagging gaps, over-reach, or duplicated scope; the orchestrator is what acts on those findings (creating, updating, or deleting Subtasks per the PM's verdict).

The Epic's spec source can take three shapes, depending on what the parent Plan Bee's `reference_materials` carries:

- **`reference_materials` non-empty with `resolver: file-path` (or default)** — the spec source is the PRD/SDD file content read from disk (Scoped to the matching `### Feature: <title>` subsection when a Scoped-marker is present on the Bee body, per Section 2).
- **`reference_materials` non-empty with `resolver: bees`** — the spec source is the `body` of the parent Spec Bee's `t1=Doc` children (the children whose `title` is exactly `PRD` or `SDD`). The Scoped-marker pre-branch in Section 2 skips marker resolution on this path, since Spec Bees are already feature-scoped.
- **`reference_materials` null/empty** — the spec source is the Plan Bee body itself (existing fallback behavior).

Defer to `agents/pm.md` `### Resolving reference_materials entries` as the **authoritative spec for the resolution logic** — the PM Agent's own contract handles the per-entry resolver dispatch (file-path read vs. two-hop Spec Bee + `t1=Doc` children walk vs. body-as-spec fallback). Do NOT duplicate the title-match recipe or the children-enumeration walk in the dispatch prompt; the PM Agent already carries that logic and re-deriving it here risks divergence between the dispatch prompt and the agent contract.

#### Authoring Subtask bodies

Subtask bodies follow the mandatory template below (Context / What Needs to Change / Key Files / Acceptance Criteria) — they are multi-section markdown that trips Claude Code's command-injection guard if inlined as a `--body "..."` argument (any newline-followed-by-`#`-heading triggers the validator and forces a permission prompt), and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). For every `bees create-ticket` you run for a Task or Subtask, **author the body to a temp file via the `Write` tool and pass `--body-file <path>`** to `bees create-ticket`. Pick a temp path under the namespaced workflow scratch dir (`/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows), creating the `.bees-workflow` subdir if absent:

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.bees-workflow
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
```

Do **not** remove the file after the bees command exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so crashed runs leave debuggable artifacts in a known place. Status-only updates and genuinely single-line bodies can stay on inline `--body`.

#### TaskList as progress UI

The orchestrator uses Claude Code's native **TaskList** as the visible progress UI for the run. There is no separate display backend to configure — TaskList renders in the harness automatically.

For every research Agent the orchestrator dispatches, it creates exactly **one** TaskList task:

- **`pending`** — created when the orchestrator decides this research dispatch is next but before the Agent invocation lands.
- **`in_progress`** — set the moment the Agent invocation is dispatched (`Agent(...)` returns).
- **`completed`** — set when the orchestrator processes the Agent's completion notification, parses the returned JSON, and (for implementer roles) creates the proposed Subtasks.

##### TaskList naming convention

The naming convention is the **canonical cross-reference** for downstream Tasks (later Sections of this SKILL.md and other skills in the workflow consume these names). It is deterministic so two concurrent invocations cannot collide and unambiguous so any reader can map a TaskList entry back to its bees ticket:

- **Implementer research Agents** (Engineer, Test Writer, Doc Writer) — **Task scope**. Name: `<role>-research-<task-id>` — concretely, `engineer-research-<task-id>`, `test-writer-research-<task-id>`, `doc-writer-research-<task-id>` (e.g., `engineer-research-t2.abc.def`, `test-writer-research-t2.abc.def`, `doc-writer-research-t2.abc.def`). Each Task gets its own implementer research Agent per applicable role; the `task-id` suffix makes the name unique even when sibling Tasks of the same Epic are processed back-to-back.
- **PM research Agents** — **Epic scope**. Name: `pm-research-<epic-id>` (e.g., `pm-research-t1.abc`). The PM reviews each proposed Subtask set within the context of the whole Epic, so its scope suffix is the parent Epic id; the orchestrator creates a new PM research Agent per Task-level review boundary, but the TaskList name disambiguates by Epic.

The `-research-` infix distinguishes these dispatches from the implementation-time dispatches in `/bees-execute` (which use `<role>-<subtask-id>` and `pm-<task-id>` per `bees-execute` Section 3's `##### TaskList naming convention`). A reader scanning a mixed TaskList can tell at a glance whether a given entry is breakdown-time research or execute-time implementation.

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

Work through each Task in the Epic sequentially via the reconciliation loop above. Each Task gets its own per-role research dispatches and its own PM review boundary; do **not** ask the User for permission between Tasks. Only stop to review with the User once all Tasks in the Epic have a PM-approved Subtask set, then proceed to Section 5.

### 5. Review Epic

When all Tasks have a per-Task PM-approved Subtask set from Section 4's reconciliation loop, run an **Epic-wide Spec Traceability Review** before any further `bees create-ticket` invocations and before any status transitions to `ready`. The review is the gate that catches spec coverage gaps the per-Task reviews could not see — a requirement that lives in the Epic-wide spec but does not naturally fall under any single Task can pass every per-Task PM review while still being absent from the proposed Subtask set as a whole.

Under research-only orchestration the Section 5 review is driven by a **fresh, ephemeral PM research Agent** — same dispatch shape as Section 4's `#### Per-Task PM dispatch`, scoped here to the whole Epic. The orchestrator (you) does not author the traceability table itself; the PM Agent returns it as JSON-structured findings, and the orchestrator consumes those findings to decide what to do next. If the PM flags GAP rows, the orchestrator dispatches additional research Agents to author the missing Subtask bodies, then re-dispatches the PM until all rows are OK. **Only after PM sign-off** does the orchestrator run `bees create-ticket` for any gap-fill Subtasks and transition Epic + Tasks + Subtasks to `ready`. Reviewing first and creating-or-amending tickets second avoids the delete-and-recreate churn that "create everything, then traceability-review, then patch" produces.

You must defer to the Product Manager on whether the Epic's Subtask coverage is final and complete. The orchestrator's role is to dispatch, integrate findings, and act on them — not to substitute its own judgment for the PM's verdict.

#### Spec Traceability Review (PM dispatch, gap-fill loop)

**This step is mandatory after every Epic is broken down.** It runs **before** any further `bees create-ticket` invocations in this section and **before** any status transitions to `ready`.

##### Step 1 — Dispatch a fresh PM research Agent

Spawn a fresh PM Agent in research mode at Epic scope. Use the same dispatch shape as Section 4's `#### Per-Task PM dispatch`:

```
Agent(
  subagent_type="pm",
  run_in_background=true,
  prompt=<research-mode preamble + Epic-wide review prompt below>,
)
```

Create exactly one TaskList task for this dispatch, named `pm-research-<epic-id>` per Section 4's `##### TaskList naming convention` (Epic-scope PM naming). Mark it `in_progress` when the `Agent(...)` invocation lands and `completed` when the orchestrator processes the Agent's returned JSON.

The dispatch prompt must include:

- The research-mode preamble verbatim (see Section 4's `##### Research-mode preamble`).
- The Epic ID and the full set of Task IDs + Subtask IDs the orchestrator created in Section 4.
- The Epic body verbatim (read via `bees show-ticket --ids <epic-id>`).
- The parent Bee body verbatim (read via `bees show-ticket --ids <bee-id>`) so the PM can see `reference_materials` and detect the Scoped-marker.
- The literal placeholder `<scoped-marker-resolver-path>`, **substituted by the orchestrator** to the resolved helper path before dispatch — the PM Agent uses it to detect and apply any Scoped-marker on the parent Bee, just as the orchestrator did in Section 2.
- The Spec Traceability Review prose below (verbatim — it is the PM's review contract).

##### Step 2 — Resolving `<scoped-marker-resolver-path>` (own-skill resolution)

Resolve the placeholder against **this skill's own base directory**: `<this skill's base directory>/scripts/scoped_marker_resolver.py`. The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../bees-breakdown-epic`).

**This differs from `bees-execute` and `bees-fix-issue`.** Those two skills resolve the same helper as a *sibling* of their own base directory — `<base>/../bees-breakdown-epic/scripts/scoped_marker_resolver.py` — because the helper is shipped by `bees-breakdown-epic` and they consume it across skills. Here, in `bees-breakdown-epic` itself, the helper lives **inside this skill**, so resolution drops the `..` hop and points at this skill's own `scripts/` subdirectory. Do not copy `bees-execute` / `bees-fix-issue`'s sibling-resolution string into this skill — it would resolve to a path that does not exist on disk.

##### Step 3 — Spec Traceability Review prose (embedded in PM dispatch prompt)

The following prose is the PM's review contract. Embed it verbatim in the PM dispatch prompt; do not paraphrase.

1. Re-read the Epic description, including its scope and acceptance criteria.
2. Identify every specific requirement the Epic depends on. **Source depends on the parent Plan Bee's `reference_materials` — branch on the entry's `resolver` field, mirroring the resolution logic in `agents/pm.md` `### Resolving reference_materials entries`:**
   - **`reference_materials` non-empty with `resolver: file-path` (or default — PRD/SDD on disk)**: requirements come from the file content (Scoped to the matching `### Feature: <title>` subsection when a Scoped-marker is present, per Section 2). Cite section numbers from the docs — `PRD §X` and `SDD §Y`.
   - **`reference_materials` non-empty with `resolver: bees` (Spec Bee in the `specs` hive)**: requirements come from the `body` of the parent Spec Bee's `t1=Doc` children — the child whose `title` equals `PRD` carries PRD content, the child whose `title` equals `SDD` carries SDD content. Cite the Spec Bee child ticket ID together with the section/bullet within that ticket — for example, `<prd-child-ticket-id> §<section>` for PRD content and `<sdd-child-ticket-id> §<section>` for SDD content. Substitute the actual child ticket IDs (e.g., `t1.xyz.ab`) and the actual section header text or bullet identifier in the table; the placeholder shape `<prd-child-ticket-id> §<section>` is documented here so the citation format is unambiguous across PM agents executing this review.
   - **`reference_materials` null/empty (no PRD/SDD)**: requirements come from the Plan Bee body itself (and the Epic body) — cite the Bee's relevant scope/acceptance-criteria bullets, e.g., `Bee body` or `Bee body §<bullet-or-section>`.
3. For each requirement, verify there is at least one subtask that explicitly covers it.
4. Report the results as a traceability table. The `Source` column carries the citation in the shape that matches the resolver branch above. The example below illustrates all three citation forms — file-path (`PRD §X`, `SDD §Y`), bees-resolver (`<prd-child-ticket-id> §<section>`, `<sdd-child-ticket-id> §<section>`), and body-as-spec (`Bee body`):

```
| Spec Requirement    | Source                          | Covered By Subtask | Status |
|---------------------|---------------------------------|--------------------|--------|
| <requirement>       | PRD §X                          | t3.xxx             | OK     |
| <requirement>       | SDD §Y                          | MISSING            | GAP    |
| <requirement>       | <prd-child-ticket-id> §<section>| t3.yyy             | OK     |
| <requirement>       | <sdd-child-ticket-id> §<section>| MISSING            | GAP    |
| <requirement>       | Bee body                        | t3.zzz             | OK     |
```

Use only the rows whose source shape matches the actual resolver branch for this Epic — the table above is illustrative, showing all three forms together for format clarity.

5. If any requirement is marked GAP, return the table flagging the GAP rows and a brief description of each missing requirement. Do not create tickets — research mode is read-only; the orchestrator handles ticket creation.

6. Sign off only when every row's `Status` is `OK`.

This review ensures nothing from the spec is lost during the Task/Subtask decomposition. The subtask descriptions are what the executing agents will follow — if a requirement is not in a subtask, it will not be implemented. The review applies whether the spec source is a PRD/SDD pair on disk, a Spec Bee's `t1=Doc` children in the `specs` hive, or the Plan Bee body itself.

##### Step 4 — Gap-fill iteration loop

When the PM Agent returns its JSON findings, the orchestrator consumes the traceability table:

- **All rows `OK`** → PM signed off. Skip to Step 5.
- **One or more `GAP` rows** → for each gap, dispatch a fresh research Agent in the appropriate role to author the missing Subtask body:
  - Code change required → `subagent_type: "engineer"` in research mode.
  - Test code change required → `subagent_type: "test-writer"` in research mode.
  - Documentation change required → `subagent_type: "doc-writer"` in research mode.
  - Use the same dispatch shape as Section 4 (`run_in_background=true`, research-mode preamble, ticket-body verbatim quoting). Name each TaskList task `<role>-research-<task-id>` against whichever Task the gap-fill Subtask will live under (per Section 4's naming convention). If the gap-fill Subtask spans Tasks or does not belong to any existing Task, surface that back to the caller via `AskUserQuestion` rather than guessing.
- When all gap-fill research Agents have returned, **re-dispatch a fresh PM research Agent** (new TaskList task, new `pm-research-<epic-id>` entry — the previous one is already `completed`) with the updated proposed-Subtask set. Loop back to Step 4's first bullet.

The loop terminates when the PM returns a traceability table with every row at `OK`. Do **not** short-circuit the loop by trusting the orchestrator's own read of the table — the PM is the authority on sign-off.

##### Step 5 — Create gap-fill tickets, then transition to `ready`

Only after PM sign-off (all rows `OK`):

1. For each gap-fill Subtask body the research Agents authored during Step 4, run `bees create-ticket --body-file <path>` against the appropriate parent Task — author bodies to temp files under `<tempdir>/.bees-workflow/` per Section 4's `#### Authoring Subtask bodies` convention. Wire each new Subtask's `parent` to the owning Task ID, and add `up_dependencies` where another Subtask must complete first.
2. Set the Epic to `ready` (it is now written and its children — the Tasks — are written).
3. Set each Task to `ready` (it is written and its children — the Subtasks — are written).
4. Set each Subtask to `ready` (it is written and has no children).

Show the Tasks you just created (Section 4's per-Task Subtasks plus any gap-fill Subtasks created in Step 5.1) to the User in detail and ask them if they want to make modifications.

#### Checklist Before Returning

- [ ] All Subtasks have parent set to task-id
- [ ] If Task modifies code, all mandatory subtasks created (implementation steps, architecture docs review, unit test review, run full test suite)
- [ ] Documentation subtasks have up_dependencies on implementation (implementation must complete first)
- [ ] Testing subtasks have up_dependencies on implementation/add-tests (implementation and test creation must complete first)
- [ ] All descriptions follow the mandatory template (see `#### Mandatory Subtask Description Template` above)
- [ ] NO git commit subtasks created (commits handled automatically by executors)
- [ ] Testing subtasks support maximum parallelization on execution by making one subtask per test file to be modified
- [ ] Spec Traceability Review completed (PM Agent dispatched, gap-fill loop converged, all rows at OK status, sources cited per the resolver branch — file-resolver `reference_materials` cite `PRD §X` / `SDD §Y`, bees-resolver `reference_materials` cite `<prd-child-ticket-id> §<section>` / `<sdd-child-ticket-id> §<section>`, null/empty `reference_materials` cite `Bee body`) **before** the gap-fill `bees create-ticket` invocations and **before** the status transitions to `ready`

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

Note above the options: `/bees-execute` re-reads the Bee, Epics, and Tasks from the bees CLI and reads CLAUDE.md from disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives the executing agents full context budget for per-Task implementation, review cycles, and the orchestrator's running judgment. Continuing to break down the next Epic in this session is lower-risk (same skill, similar context footprint), but a fresh session is still preferred for big Bees.

If Step 6 found the Plans hive lives outside the repo, also include a one-line note here: *"The new ticket files are persisted by the bees CLI but the Plans hive lives outside this git repo, so they were not committed by this skill."*

#### Pick the Recommended option

The "Recommended" badge depends on two facts about the parent Bee: whether any drafted sibling Epics remain, and — if they do — whether breaking down the *next* Epic right now risks rework. Specifically: when the just-broken-down Epic's implementation will lock contract details (new infrastructure, API surface, schema, framework, etc.) that drafted siblings consume, breaking those siblings down before that contract solidifies produces stale Tasks. If no drafted siblings remain at all, planning is done and the natural next move is bulk execution; if drafted siblings remain with pure-ordering dependencies only, the natural next move is to keep breaking down. To decide:

1. Query drafted sibling Epics under the same parent Bee:

   ```bash
   bees execute-freeform-query --query-yaml 'stages:
     - [parent=<bee-id>, type=t1, status=drafted]
   report: [title, up_dependencies]'
   ```

2. If the query in step 1 returned no drafted siblings at all, skip directly to the **No-drafted-siblings case** branch in step 4. Otherwise, filter to siblings whose `up_dependencies` includes the just-broken-down Epic's ID. If there are drafted siblings but none depend on the just-broken-down Epic, treat that as the **Drafted-siblings-remain, no reshape risk** case in step 4 and skip step 3.

3. For each such dependent sibling, fetch its body via `bees show-ticket --ids <sibling-epic-id>` and read it alongside the just-broken-down Epic's body. Judge — this is an orchestrator call, not a hardcoded rule, treated the same as other judgment calls in this skill — whether the upstream Epic's implementation will materially reshape the contract the sibling consumes. Indicators of reshape risk:
   - Upstream Epic introduces new infrastructure, API surface, schema, framework, or subagent/tool definitions that the sibling explicitly rewrites-to-consume.
   - Sibling Epic's scope reads like "rewrite X to use the new Y" where Y is what the upstream Epic produces.
   - Contract details (signatures, file shapes, lifecycle, error vocabulary) the sibling would have to guess at are precisely what the upstream Epic locks in.

   Pure ordering coupling — sibling depends on upstream only because work must serialize, not because it consumes a still-in-flux contract — does **not** count as reshape risk.

4. Branch the Recommended badge across three cases:
   - **No-drafted-siblings case** (the query in step 1 returned zero drafted siblings under this Bee): Recommended option is **"In a fresh session, execute the whole Bee"**. Rationale (for the option's `Best when …` subtitle): planning is done — every Epic in this Bee is broken down and ready to ship.
   - **Drafted-siblings-remain, reshape-risk case** (drafted siblings exist and at least one dependent sibling is judged to consume an in-flux contract): Recommended option is **"In a fresh session, execute this Epic first; defer downstream breakdown"**. Rationale (for the option's `Best when …` subtitle): name the at-risk siblings (by ID and short title) and the contract concern in one short sentence (e.g., *"siblings `<id-a>` / `<id-b>` rewrite-to-consume the new framework this Epic produces; breaking them down before implementation lands risks stale Tasks."*).
   - **Drafted-siblings-remain, no-reshape-risk case** (drafted siblings exist; either none depend on the just-broken-down Epic, or every dependency is pure ordering coupling): Recommended option is **"In a fresh session, break down the next Epic"**. Rationale (for the option's `Best when …` subtitle): name which siblings are still drafted (by ID) and note that their Tasks won't go stale because the dependency is pure ordering, not contract reshape.

5. Surface the rationale **only** as the Recommended option's `Best when …` subtitle (one short sentence, ≤ ~150 chars so it fits the option-card UI). Do **not** emit a freestanding rationale paragraph above the `AskUserQuestion` menu — the Claude Code UI does not render long header prose reliably and has been observed truncating mid-sentence, leaving the user unable to read the reasoning. Keep any prose above the menu limited to the standing notes from the parent Step 7 section (the fresh-session note and, if applicable, the out-of-repo Plans-hive note); do not add a new paragraph that explains the Recommended pick. Do **not** surface an extra confirm-or-defer prompt the user can't meaningfully answer.

#### Menu options

Always include all six options below. The Recommended badge moves across three of the options (whole-Bee execute, this-Epic-first execute, break-down-the-next-Epic) per the three-way branch above. Each option carries a one-line "best when …" clause so the user can compare trade-offs without external context. When an option is the Recommended pick for the current run, replace its generic `Best when …` clause with the case-specific rationale called out in step 4 of *Pick the Recommended option* (which siblings are at risk / which siblings are still drafted with pure-ordering dependencies / etc.) — that subtitle is the only place the rationale is surfaced.

- **In a fresh session, execute the whole Bee** — run `/bees-execute <bee-id>` (e.g. `b.duy`) in a new Claude Code session. `/bees-execute` walks every Epic in the Bee in dependency order.
  - *Best when* every Epic in the Bee is already broken down and the plan is ready to ship.
  - *Recommended when no drafted Epics remain under the parent Bee.*
- **In a fresh session, execute this Epic first; defer downstream breakdown** — run `/bees-execute <epic-id>` (e.g. `t1.duy.c9`) in a new session, scoped to the Epic just broken down. After it lands, return to break down the dependent siblings against the now-stable contract.
  - *Best when* drafted siblings rewrite-to-consume what this Epic produces and the contract is still in flux — execute now, then break down siblings against the locked-in contract.
  - *Recommended when drafted siblings present reshape risk.* Name the at-risk siblings inline.
- **In a fresh session, start at a specific Epic** — run `/bees-execute <epic-id>` in a new session. `/bees-execute` accepts an Epic ID; it finds the parent Bee automatically and starts from that Epic's position in the plan. All Epics still run — this just biases the entry point.
  - *Best when* the user wants the bulk-execute walk but with a specific entry point (e.g., the just-broken-down Epic, or an upstream foundational Epic).
- **In a fresh session, break down the next Epic** — run `/bees-breakdown-epic <next-epic-id>` in a new session if more Epics in this Bee remain in `drafted` state. Same-session continuation is also reasonable here since the skill is repeating with similar context growth per Epic.
  - *Best when* the user wants to finish planning before any execution starts and there's no contract-reshape risk that would make the next Epic's Tasks go stale.
  - *Recommended when drafted siblings remain with no reshape risk.* Name the still-drafted siblings inline.
- **Review first** — let the user review the plan before proceeding.
  - *Best when* the user wants to scan the new Tasks and Subtasks for shape/scope before committing to an execution path.
- **Done for now** — plan is saved; user will come back later.
  - *Best when* the user is at a natural stopping point and will return in a later session.

