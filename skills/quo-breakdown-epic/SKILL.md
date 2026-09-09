---
name: quo-breakdown-epic
description: Break down a single Epic into Tasks. User can provide Epic ID or a Bee ID and skill finds Epics that are ready
argument-hint: "[<epic-id> | <bee-id>]"
---

# Epic to Tasks

Your job is to break down an Epic ticket into Tasks and Subtasks.

## Preconditions

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The seven required custom subagent types are registered in the running Claude Code session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. Custom subagents are loaded at Claude Code session start (from `~/.claude/agents/` for global installs and `<repo>/.claude/agents/` for per-project installs), so a fresh install requires a Claude Code restart (or `/agents` to hot-reload) before the skill can dispatch them. Although this skill only dispatches a subset of these roles in research mode, the precondition is uniform across the three execution skills (`/quo-execute`, `/quo-fix-issue`, `/quo-breakdown-epic`) so a "user forgot to restart Claude Code" misconfiguration is caught identically regardless of entry point. If any of the seven is missing at run-time, the orchestrator STOPS at the precondition gate and emits the hard-fail message — there is no fallback to `general-purpose`, no skipping the dispatch, and no improvising substitute roles. The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents` to hot-reload, e.g.: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`
- The Plans hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `plans`.
- The Specs hive is colonized for this repo. Check via `bees list-hives` — the output must include a hive whose `normalized_name` is `specs`. If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section. Agents look up paths to architecture docs, customer docs, test guides, etc. by exact key from this section.
- CLAUDE.md contains a `## Build Commands` section, and that section has all five required bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. Agents look up build/test/format/lint commands by exact key from this section.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The Build Commands section is required, not optional.

Do not attempt to recover from a missing precondition by improvising commands or guessing paths — fail fast and direct the user to `/quo-setup` so the configuration is captured deliberately.

**Verifying the subagents precondition.** Verification rides on the procedural gate at the first dispatch: if any dispatch in the run hits an `Agent type '<name>' not found`-style error from the Agent tool for any of the seven required subagent types (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`), the orchestrator STOPS, emits the hard-fail message above, and exits — no fallback to `general-purpose`, no skipping the dispatch, no substitute role. This gate is honest about Claude Code's session-load semantics (subagents are loaded at session start from `~/.claude/agents/` and `<repo>/.claude/agents/`; mid-session installs require a restart or `/agents` hot-reload) and cannot be bypassed by token-budget pressure or model creativity, because it fires at the natural failure point.

## Workflow

### 0. Check session reasoning effort

The session-effort `AskUserQuestion` in this section is **conditional** — it fires only when the session is below this skill's effort floor. When it fires, it goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate (per Section 4's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed. When the gate does **not** fire, **no `TaskCreate` fires for it either**.

This skill is tuned for an orchestrator session running at **`high`** reasoning effort or higher. Every dispatched subagent's effort is pinned per role in its own role-file frontmatter and is **not** affected by the orchestrator's session setting, so this check concerns only the seat you are running in. The skill cannot change the session setting itself — the most it can do is name the recommendation and let the user apply it.

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

If the output is empty, the command exits non-zero, or the value is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat it as unset (an older CLI, a launch path that does not export it, or a token this skill does not know how to order): **skip this check entirely and continue to Section 1, silently.** A spurious prompt on every run is worse than a missed advisory.

**Step 2 — compare against this skill's floor, which is `high`.** The ordering is `low` < `medium` < `high` < `xhigh` < `max`. Compare against the floor, never for equality — an operator running hotter than the recommendation costs wall-clock but not quality, and interrupting them is pure gate-fatigue noise.

- **At or above `high`** — say nothing at all. No gate, no prompt, no output, and **no `TaskCreate`**. Continue to Section 1.
- **Strictly below `high`** — fire the gate in step 3.

**Step 3 — fire the gate (this branch only).** This gate honors the two-step `TaskCreate` → `AskUserQuestion` contract stated at the top of this section: first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate (per Section 4's TaskList naming convention's gate-task entry), then call `AskUserQuestion` in the same turn. Substitute the value read in step 1 for `<current>`. Question text:

```
This session is running at `effort=<current>`, below the `high` floor this
skill is tuned for. Decomposition quality here sets Subtask granularity for
every downstream execution run.

Subagent effort is pinned per role and is NOT affected by this setting.
```

Present these options:

1. **Proceed anyway** — Run at the current effort level. Mark the `gate-*` task `completed` and continue to Section 1.
2. **Let me change it first** — Exits without dispatching anything; the user runs `/model`, then re-invokes. Mark the `gate-*` task `completed`, then exit cleanly.

### 1. Determine Which Epic to Break Down

All `AskUserQuestion` gates in this section (the Bee pick when no Bee was named, and the Epic pick when multiple drafted Epics remain under the chosen Bee) fire through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 4's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the user's answer is consumed.

**If caller provides Epic ID**: Use that Epic ID directly.

**If caller provides a Bee ID**: Use the Bee ID to find workable Epics — see the "Once you have a Bee ID" recipe below.

**If caller provides no arguments**: Search for ready Plan Bees in the current repo by querying the Plans hive:
```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans, status=ready]
report: [title]'
```
If exactly one Bee is found, use it. If multiple, use `AskUserQuestion` to let the user pick which Bee to work on (the `report: [title]` clause gives you the titles to display). If none found, tell the user no Plan Bees are ready and suggest running `/quo-plan-from-specs`.

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

### 1.5 Pick a multi-Epic run mode and write the run-state manifest

**This section has one conditional half and one unconditional half — run it on every invocation.** The multi-Epic run-mode gate below fires only when more than one drafted Epic remains; the `#### Write the run-state manifest` sub-section at the end of this section runs on **every** run, including single-Epic runs where the mode gate is skipped. Do not skip past this section because the mode gate does not apply — skipping it would leave the run with no manifest, and every later reader of run-scoped state depends on that file existing.

The multi-Epic run-mode `AskUserQuestion` gate in this section fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate (per Section 4's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed.

After the Epic-to-break-down has been picked but **before** any breakdown work begins, check the count of `drafted` Epics that remain under the parent Bee from the query already run above (the `[parent=<bee-id>, type=t1, status=drafted]` query).

**If the drafted-siblings query has not been run yet** — this happens on the `/quo-breakdown-epic <epic-id>` invocation form, where Section 1's first branch ("If caller provides Epic ID") uses the Epic ID directly without resolving the parent Bee or enumerating its drafted children — derive the parent Bee ID from the Epic by running `bees show-ticket --ids <epic-id>` and reading the response's parent field, then run the `[parent=<bee-id>, type=t1, status=drafted]` query before evaluating the gating predicate below. (On the Bee-ID and no-args paths in Section 1, the query has already been run and you can skip this derive-and-query step.)

```bash
# POSIX (bash / zsh):
bees show-ticket --ids <epic-id>
```

```powershell
# Windows (PowerShell):
bees show-ticket --ids <epic-id>
```

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=drafted]
report: [title, up_dependencies]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=drafted]
report: [title, up_dependencies]'
```

If two or more drafted Epics remain (i.e., there is at least one drafted sibling beyond the one just selected), present a one-time mode choice with `AskUserQuestion`:

- Question: "How should this run handle multiple Epics? (You will not be asked again this run.)"
- Options:
  - **Stop after each Epic** — pause at every Epic boundary so you can review and approve continuation. Today's per-Epic confirmation behavior — Section 7's full menu fires after each Epic is broken down.
  - **Work through all Epics** — auto-continue across Epics; only stop when proceeding without your input would risk concrete downstream cost. Specifically, Mode 2 still pauses on (a) Section 7's drafted-siblings-with-reshape-risk case (the *"execute this Epic first; defer downstream breakdown"* recommendation, which is a contract-stability concern) and (b) any final reviewer-surfaced blocker the orchestrator escalates.

Capture the user's choice once and store it as the **multi-Epic run mode** for the rest of this run. The choice persists across Epic boundaries — do not re-prompt at every Epic. Section 7's next-Epic loop branches on this captured value.

If only one drafted Epic remains under the Bee at the time this step runs, **skip the question entirely** — there is no sibling to chain to, and Section 7's menu still has the same six options for the user to pick from manually.

#### Write the run-state manifest

This is the **canonical definition site** for the run-state manifest; later sections refer to it by name. Write it as the last step of Section 1.5 — after the Epic is picked and the run mode is either captured or knowingly skipped — and before any breakdown work begins. Write it on **every** run, including single-Epic runs where the mode question was skipped.

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds ticket state, git holds the committed ticket files, and the `defer-*` TaskList holds open deferrals; the manifest holds only what those three do not. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `run-state-quo-breakdown-epic-<unit-id>.md` (e.g., `run-state-quo-breakdown-epic-b.abc.md`). `<unit-id>` is resolved in a fixed order so that a writer and a later reader always agree on the path:

1. The **Bee ID** — the parent Bee of the Epic being broken down. This is the key on every normal invocation.
2. The **Epic ID** — used only on an invocation where no parent Bee could be resolved at all.

**A reader applies the same order.** When re-locating the manifest (e.g., a reconciliation tick after a compaction), resolve the parent Bee first and try `run-state-quo-breakdown-epic-<bee-id>.md`; only if no parent Bee resolves, or that file does not exist, fall back to `run-state-quo-breakdown-epic-<epic-id>.md`. Recording *which* key was used is unnecessary precisely because the order is deterministic — do not add a key-discriminator field to the manifest.

Create the `.quorum` directory if it does not already exist, then author the manifest via the `Write` tool (no shell redirect):

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write the manifest to /tmp/.quorum/run-state-quo-breakdown-epic-<unit-id>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write the manifest to $env:TEMP\.quorum\run-state-quo-breakdown-epic-<unit-id>.md via the Write tool
```

**The filename is deterministic — do NOT add a random suffix or timestamp.** The manifest's reader is the orchestrator itself, possibly after a compaction that dropped the path from the conversation. A random suffix would be unfindable exactly when the manifest is needed most.

**Why the key is this skill's name plus a ticket ID.** The ticket-ID half of the key has to satisfy two properties, and a Bee/Epic ID satisfies both. It is **re-derivable without the conversation**: the Epic being broken down is this run's argument, and its parent Bee is one `bees show-ticket` away, so an orchestrator that has lost the conversation recomputes the filename from the Plans hive rather than from memory. And it is **discriminating across projects**: ticket IDs are minted per bees workspace, so two runs against two different projects do not normally land on the same filename in the machine-wide `<tempdir>/.quorum/`.

The **`quo-breakdown-epic` segment is what discriminates across sibling skills**, and it is not decorative: `/quo-execute` keys its own manifest on the *same* Bee ID, so without the skill-name segment a `/quo-execute` run started against this Bee would truncate this session's manifest out from under it — exactly the sequence Section 7's *"In a fresh session, execute this Epic first; defer downstream breakdown"* menu option invites, since that fresh `/quo-execute` session starts while this one is still live. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends: `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has, while `/quo-fix-issue` — whose batch membership is only recoverable from inside the manifest itself — appends the repository directory basename instead. See each skill's own manifest section for its rationale.

The remaining trade is against the scratch-file convention's collision-resistance guidance. What this key does **not** discriminate is two cases, both accepted knowingly rather than hidden:

- **Two concurrent `/quo-breakdown-epic` runs against the same unit.** They share one manifest filename and the later run's truncating write wins. That matches the layer below — two such runs already collide destructively over ticket creation and commits, so it is not a case the workflow supports.
- **Two concurrent runs breaking down *different* Epics under the same Bee.** Because the key is the Bee ID, these share one filename too — but unlike the case above they do *not* collide destructively anywhere else: each creates Tasks under its own Epic, and Section 7's *"In a fresh session, break down the next Epic"* menu option invites exactly this flow while the current run is still live. The later run's truncating write still wins, so a resumed earlier session reads its sibling's state (a different Epic under `Progress`, a different `Next unit`) — and two of the fields Section 7's Epic-boundary checkpoint reads back have **no re-derivation path from bees or git**: the **Multi-Epic run mode** (a user choice, per this section's closing note) and the **Pre-run SHA** (this manifest is the only place the run records it). The concrete consequence is a resumed session that inherits the sibling's mode — auto-continuing across Epics when the user asked to stop at each one, or the reverse — and the sibling's later Pre-run SHA, which under-scopes the checkpoint's commit-landed check. The trade is accepted rather than hidden, because the failure is detectable and each destroyed field has a real fallback: a manifest whose `Progress` names an Epic this session never broke down is the tell, and a reader that spots it recovers in three steps — (i) re-query bees for the Epic this run actually holds and rewrite the manifest from that; (ii) recover the run mode by **re-firing Section 1.5's `AskUserQuestion` mode gate above**, since asking the user again is the only honest source for a user choice — do not guess it from the manifest you just found to be a sibling's; (iii) accept a **weaker commit-landed check** in place of the lost Pre-run SHA, searching recent history for Section 6's commit-subject token with `git log --oneline -F --grep='(<epic-id>)'` and no lower bound. State that degradation plainly rather than papering over it: the unbounded form can match a same-`(<epic-id>)` commit from an earlier run against this Epic, so it is strictly weaker evidence than the ranged `<pre-run-sha>..HEAD` form — confirm the matched commit's ticket files are the Tasks this run created before treating the check as passed. Keying on the Epic ID instead would fix this case at the cost of the property the whole design rests on: a single run walks several Epics (Section 7's checkpoint rewrites the manifest at each Epic boundary and re-reads it at every next-Epic dispatch), so an Epic-keyed filename would change mid-run and stop being the one deterministic path a post-compaction reader can recompute.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it fresh here (overwriting any manifest left by a previous run against the same unit) and rewrite it in full at each Epic boundary per Section 7's Epic-boundary state-externalization checkpoint. Never delete it — the scratch-file convention forbids cleanup, so do NOT instruct any `rm` / `Remove-Item`.

**Contents — and an invariant that bounds them.** The manifest carries **only values that have no other durable home.** Do not add Epic bodies, proposed Subtask text, PM findings, or anything else already readable from bees, git, or the TaskList; duplicating them here would grow the manifest into a shadow ticket store that drifts. The fields are:

```markdown
# Run state — quo-breakdown-epic @ <unit-id>

- **Skill:** quo-breakdown-epic
- **Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>
- **Unit scope:** Bee <bee-id>; drafted Epics in scope: <epic-id-1>, <epic-id-2>, ...
- **Multi-Epic run mode:** <Mode 1 (Stop after each Epic) | Mode 2 (Work through all Epics) | not captured (one drafted Epic remained)>
- **Pre-run SHA:** <sha>
- **Progress:**
  - <epic-id>: broken down — Tasks created, status `ready`
- **Next unit:** <next-epic-id | none>
```

The **Unit scope** line above is the normal-invocation shape, where a parent Bee resolved. On the Epic-ID-fallback invocation — the second key in the resolution order above, used when no parent Bee could be resolved at all — there is no Bee ID to write and no drafted-siblings set to enumerate, so write `standalone Epic <epic-id>` as the whole value instead. Do not leave the `Bee <bee-id>` half blank or fill it with a placeholder: a reader validating the manifest against the unit in hand compares this line, and `standalone Epic <epic-id>` is the value that lets that comparison succeed on the fallback path.

Capture the **Pre-run SHA** here, at run start, with one literal command — it is the HEAD this run began from, and this is the **only** place the run records it. It has one concrete consumer: step 1 of Section 7's Epic-boundary state-externalization checkpoint reads it back from this file and runs `git log --oneline <pre-run-sha>..HEAD` to confirm Section 6's ticket-file commit actually landed. Without it, that verification has no lower bound to diff against once the conversation is gone.

```bash
# POSIX (bash / zsh):
git rev-parse HEAD
```

```powershell
# Windows (PowerShell):
git rev-parse HEAD
```

The **multi-Epic run mode** is a user choice with no re-derivation path — if it is lost, the run cannot know whether to auto-continue — which is precisely why it belongs here.

### 2. Fetch and Analyze Epic

Fetch full Epic details using the bees CLI to understand scope of total work.

- Get that Epic from the Bees server and read it.
- Parse Epic title, description, and requirements.
- Read the parent Bee
- Read the source material linked from the parent Bee's `reference_materials`. **If `reference_materials` is null/empty** (Plan Bees authored via `/quo-plan` for features without a separate PRD/SDD), the Plan Bee body itself is the authoritative scope document — read it carefully in place of the `reference_materials` sources, and substitute "the Plan Bee body" wherever subsequent prose references "the PRD" or "the SDD".

  **Resolving `reference_materials` entries.** When `reference_materials` is non-empty, iterate the array and dispatch on each entry's `resolver` field. This mirrors the canonical lookup logic in `agents/pm.md` `### Resolving reference_materials entries` — divergence is a defect; if you find yourself improvising a different shape here, stop and re-read `agents/pm.md`.

  - **`resolver` is `file-path` (or omitted — default).** Treat the entry's `value` as a path on disk and read the file. This is the existing behavior; nothing changes on this path. The Scoped-marker integration documented below applies on this path.
  - **`resolver` is `bees`.** Treat the entry's `value` as a Spec Bee ID in the `specs` hive, and walk the two-hop path `Spec Bee → t1=Doc children → PRD / SDD content`:

    1. Run `bees show-ticket --ids <spec-bee-id>` and read the response's `children` array — these are the Spec Bee's `t1=Doc` children.
    2. For each child ID, run `bees show-ticket --ids <child-id>` and read the response's `title` and `body` fields.
    3. Identify PRD vs SDD content by **exact-match (case-sensitive) on `title`**: a child whose `title` equals `PRD` carries the PRD content in its `body`; a child whose `title` equals `SDD` carries the SDD content. Use those bodies as the spec source in place of file content.

    The `PRD` and `SDD` title strings are a cross-Epic contract; do not lower-case, normalize, or fuzzy-match. The freeform-query route (`bees execute-freeform-query --query-yaml '<yaml>'`) is also acceptable and is preferable when you want title-filtered enumeration up-front.

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

  On the file-resolver path (or the body-as-spec fallback), if the parent Bee's body contains a line of the form `` Scoped to `### Feature: <title>` from <prd-path> and <sdd-path>. `` (emitted by `/quo-plan-from-specs --feature "<title>"`), the resolved doc content must be restricted to the matching `### Feature: <title>` subsection in each named doc before treating it as the spec. Run the bundled parser/scoper to do the detection and scoping in one step:

  Extract the `body` field from the `bees show-ticket --ids <bee-id>` JSON output (the envelope's `tickets[0].body` markdown string), then write that body to a temp file via the `Write` tool under the namespaced workflow scratch dir (`/tmp/.quorum/bees-bee-body-<short-suffix>.md` on POSIX, `$env:TEMP\.quorum\bees-bee-body-<short-suffix>.md` on Windows). Create the `.quorum` subdir if absent first:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.quorum
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
  ```

  Do NOT dump the whole JSON envelope to the temp file — the marker line lives inside the body's markdown text, and JSON-encoded escapes (e.g., `\n`) prevent the parser's line-by-line scan from matching. Then invoke the helper. Resolve the helper at `<this skill's base directory>/scripts/scoped_marker_resolver.py` — the base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-breakdown-epic`).

  ```bash
  # POSIX (bash / zsh):
  python3 "<this skill's base directory>/scripts/scoped_marker_resolver.py" "/tmp/.quorum/bees-bee-body-<short-suffix>.md"
  ```

  ```powershell
  # Windows (PowerShell):
  python "<this skill's base directory>\scripts\scoped_marker_resolver.py" "$env:TEMP\.quorum\bees-bee-body-<short-suffix>.md"
  ```

  The helper exits 0 with a JSON object on stdout. When `"scoped": false`, no marker was present — proceed with the full resolved doc content as today. When `"scoped": true`, the JSON's `docs` array carries the scoped subsection content per doc path; use that scoped content for all subsequent Task decomposition, sibling-overlap checks, and the Spec Traceability Review (cite `### Feature: <title>` subsection coordinates rather than the full PRD/SDD when the marker is present). The helper exits 2 with a clear error on stderr if the marker is present but malformed, names a doc that is missing on disk, or names a heading that does not exist in the doc — surface that error to the user and stop; do not silent-fallback to the full doc. The Scoped-marker grammar and the helper's exit-code contract are owned by the resolver helper this step invokes.

  Do **not** remove the temp file after the helper exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place; the OS / user reclaims them on their own cadence.
- **Check external-system contracts against authoritative docs.** When the Epic body references a third-party platform feature (a tool API, a CLI flag set, a harness behavior, an environment-variable contract), search the system's authoritative docs before authoring Tasks — `WebSearch` and `WebFetch` are available. Look for: canonical install paths, file shapes / frontmatter formats, lifecycle requirements (e.g., does a session restart load new files, or does a hot-reload command exist?), error-message vocabulary the rewrite needs to match. Two outcomes:
  - The docs answer the contract definitively → fold the answer into the spec; skip any "probe whether it works" Tasks the breakdown might otherwise create.
  - The docs leave specific behavior unspecified → keep the probe Task, but use what the docs *did* say to design tight assertions (`does the harness register this exact frontmatter shape at this exact path with this exact session-lifecycle behavior?`) rather than broad discovery probes (`does anything happen when I dispatch this?`). Tight probes distinguish failure causes; broad probes force a guess-and-check loop.

  Spending a few minutes on docs upfront often saves hours of probe-and-fix downstream, *and* makes any probes that do run far more diagnostic when they fail.
- Identify what implementation work is needed as a list of Tasks.
- Find any Epics this Epic depends on (check `up_dependencies` field) and use `bees show-ticket --ids <id>` to read them
  - These Epics describe foundational work that will be complete before this Epic you are working on is done
  - So presume that foundational work is done and make a plan to build on top of it
- Check for sibling overlap: 
  - Read ALL sibling Epics under the same Bee. 
  - Before proposing any Task, verify it does not duplicate work scoped to another Epic. 
  - If a Task or Subtasks overlaps with a sibling Epic's scope, do NOT include it — that work belongs to the other Epic.


### 2.5 Right-size the breakdown (autonomous triage)

After analyzing the Epic in Section 2 but before drafting Tasks, decide how heavy a breakdown this Epic actually warrants. This is an **orchestrator judgment call** — the same caliber of in-skill judgment as Section 7's reshape-risk assessment, not a hardcoded rule and **not a user-facing gate**. Quorum exists to let agents build autonomously; do **not** fire an `AskUserQuestion` here. Classify, announce the chosen path in one line, and proceed.

Two paths:

- **Lightweight path** — for an Epic whose *entire* scope is operational, sequencing, manual-gate, or research work that implies **no source-code, test-code, or documentation changes**, and whose work is small (estimable as roughly one or two Tasks). Cues: the Epic body explicitly states there is no application code; every acceptance criterion is about triggering, observing, verifying, or wiring external state rather than changing files; no file in the repo would be edited to satisfy the Epic.
- **Full path** — everything else: any Epic that will change source, tests, or docs, or that is large enough to benefit from per-role research and the full Spec Traceability gap-fill loop. This is the existing behavior.

**Bias toward the Full path whenever the classification is uncertain.** This is the safety valve that makes an autonomous (un-gated) decision safe: the cost of an unnecessary Full breakdown is only wasted time, whereas the cost of under-planning a real code Epic is stale or missing Subtasks that surface downstream during `/quo-execute`. Take the Lightweight path **only** when the no-code, small-scope evidence is clear and affirmative; if you find yourself reasoning "this is *probably* ops-only," that doubt is itself the signal to use the Full path.

When you select the Lightweight path, emit a one-line note naming the Epic and the reason, e.g.: `Right-sizing: <epic-id> is an operational gate with no code/test/doc changes — taking the lightweight breakdown path (no per-role research fan-out; single traceability pass).` Then carry the **lightweight-path** flag through the rest of this run; Sections 4 and 5 read it to skip the disproportionate machinery (see the Lightweight-path exceptions in those sections). Sections 6 (commit), 6.5 (deferral hygiene), and 7 (next steps) are unchanged on both paths.

### 3. Break Epic into Tasks

#### Tasks
- **Title each Task `Task N — <short title>`**, where `N` is its 1-based position among this Epic's Tasks. The ordinal-bearing title is the Task's human label everywhere downstream (commit subjects, per-Task progress summaries during `/quo-execute`), so a reader sees `Task 2 — <title>` rather than a bare ticket ID.
- Tasks should be discrete units of work - suitable for a single git commit.
- Do not include code snippets or file numbers. Code is going to change as execution proceeds. Assume the LLM working on the code will be capable of finding the code.
- Do not describe exactly how to implement the solution. The LLM working on the solution will be an expert. Just provide the scope of work and any requirements or acceptance criteria.

#### Cross-Task contract documentation

When a Task establishes, changes, or depends on an ordering, a resource-sharing pattern, an invariant, or an assumption that another Task in the same Epic (or a sibling Epic) needs to respect, **write the contract down in the Task body**. The PM reviewer during `/quo-execute` will use these statements to cross-check sibling Tasks. Implicit contracts carried in the author's head routinely slip past per-Task reviews and surface later as cross-Task issues.

Examples of contracts worth writing down:

- **Ordering contracts**: "this Task reorders the `auth_middleware` pipeline so user lookup happens before signature verification. Any caller that assumes signature-verified-first ordering ('by this point the request is verified') needs to be re-verified."
- **Resource-sharing contracts**: "this Task introduces a new `ExclusivePool` that will be acquired by both short-lived API request handlers (ms-scale) and a new long-lived background worker (minute-scale). Pool sizing must accommodate both lifetimes; sibling Tasks that add more consumers to this pool must account for the aggregate."
- **Invariant assumptions**: "this Task's new event handler assumes that on receipt of a `user-deleted` event, the cache entry for that user has already been invalidated. The sibling cache-invalidation Task must preserve that invariant."
- **Symmetric-lifecycle requirements**: "this Task adds a new cache key class `cache:user:{id}:permissions`. Cleanup paths in sibling Tasks (user-deletion path, periodic-purge job, role-change handler) must all DELETE this key class to avoid stale-permissions leaks."

Where the contract spans sibling Tasks in the same Epic, call out the specific sibling Task IDs the reviewer should cross-check. Where the contract spans sibling Epics, note the Epic ID.

Example task:
```
Task 1 — Implement CSV export functionality                                                                              
                                                                                                                                         
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

For each Task drafted in Step 3, the orchestrator (you) drives Subtask authorship through a **reconciliation loop** that dispatches **fresh, ephemeral background `Agent` invocations** against the custom subagent types defined in this skill set's sibling `agents/` directory. There is no long-lived team; there are no warmed Agents; there is no peer-to-peer messaging between workers. This mirrors the dispatch shape used by `/quo-execute` Section 3, scoped to **research-only mode** — workers read code and return JSON-structured findings as text, and only YOU run `bees create-ticket`, `bees update-ticket`, or `bees delete-ticket`.

Your responsibilities are:

- Surface design questions back to the Caller. If dispatched research Agents propose different approaches to the same problem, surface the divergence back up to the caller with an `AskUserQuestion`.
- Coordinate the dispatched research Agents and ensure all work is complete, **but the Product Manager has final authority on quality and completeness** of the proposed Subtask breakdown.
- **Carry forward architectural decisions.** If the caller provides architectural decisions or constraints (e.g., "make parameter X optional with fallback Y"), explicitly reference them in every affected subtask description. Do not paraphrase or partially apply — use the caller's exact specification.

**You do not author Subtasks yourself.** Subtask proposals come from the dispatched research Agents; the orchestrator's job is to invoke the right role at the right time, integrate the returned JSON findings, and create the actual bees tickets.

#### Lightweight-path exception (Section 2.5)

When Section 2.5 selected the **lightweight path**, this Epic has no source/test/doc work for the implementer roles to research, so the per-role fan-out and the per-Task PM review are disproportionate. On the lightweight path only:

- **Skip the per-role implementer research dispatch** (Engineer / Test Writer / Doc Writer) — there is no code, test, or doc lane for them to own.
- **The orchestrator authors the operational Subtask bodies directly**, following the mandatory Subtask Description Template below. This is the one place the "You do not author Subtasks yourself" rule above is lifted: with no implementer lane in play, there is no role to delegate authorship to, so the orchestrator writes the operational Subtasks itself.
- **Skip the per-Task PM dispatch.** Spec coverage is checked once, at Epic scope, by the single traceability pass in Section 5's lightweight-path exception — not per Task.
- With no implementer or per-Task PM dispatches, the event-driven reconciliation loop below has nothing to await on this path — author the Tasks and operational Subtasks directly, create the tickets via `bees create-ticket --body-file` (scratch-file convention unchanged), and advance to Section 5.

Everything else in Section 4 (the mandatory template, `bees create-ticket --body-file` authoring via the scratch-file convention, the TaskList progress UI, cross-Task contract documentation) applies unchanged. On the **full path**, ignore this exception and run Section 4 exactly as written below.

#### Reconciliation loop

The loop is **event-driven, not clock-driven**. Each tick has three phases:

1. **Read state.** Pull the current truth from four sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <epic-id>` to get the Epic's `children` array (Task IDs); for each Task, fetch its full body. Identify the next Task that still has no Subtasks proposed (or whose proposed-Subtasks set is incomplete pending PM review). Use the canonical freeform-query recipe (`bees execute-freeform-query --query-yaml '<yaml>'`) for any focused state query.
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight research Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done with its JSON findings).
   - **Returned findings** — the JSON-structured text each completed research Agent returned. These are the load-bearing handoff: the orchestrator consumes the JSON to compose `bees create-ticket --body-file` invocations.
   - **the run-state manifest** — the on-disk file defined in Section 1.5 `#### Write the run-state manifest`, holding the run-scoped values that have no other durable home (multi-Epic run mode, unit scope, pre-run SHA, per-Epic progress, next unit). `Read` it at `<tempdir>/.quorum/run-state-quo-breakdown-epic-<unit-id>.md`, resolving `<unit-id>` in Section 1.5's fixed order (parent Bee first, Epic ID only as fallback); the path is derived from this skill's name plus the unit ID, so it stays findable even when nothing about it survives in the conversation. **Validate it before consuming any field:** confirm its **Progress** names only Epics this session broke down and its **Unit scope** matches the unit in hand. A manifest naming an Epic this session never touched is the sibling-collision tell described at the definition site — apply Section 1.5's three-step recovery there rather than reading a sibling run's mode or Pre-run SHA into this tick.

   **Conversation memory is never a substitute for these four sources.** Whatever the orchestrator believes it remembers about which Tasks exist, which Subtasks were already created, or which run mode was captured, the four sources above are the truth and are re-read rather than recalled. This is unconditional — it holds on every tick, not only after something goes wrong. On top of it, one conditional rule for the observable case: **if a summarization marker is visible in the conversation** (the harness compacted mid-run), treat everything before it as non-authoritative and re-read all four sources in full before dispatching anything else. A returned-findings payload that was consumed before a compaction is recoverable the same way every other fact is — from the bees tickets the orchestrator created out of it, not from memory of the JSON.

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

The research-mode preamble in the dispatch prompt is what makes a research dispatch a research dispatch. The Implementation note on the parent Epic body explicitly states this is signaled via prompt rather than by introducing separate research-mode subagent types — trust the prompt; do **not** introduce `engineer-researcher`, `test-writer-researcher`, etc. The same `engineer` / `test-writer` / `doc-writer` / `pm` subagent types used by `/quo-execute` are reused here, gated to read-only behaviour by the preamble.

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
  and use `bees execute-freeform-query --query-yaml '<yaml>'` if you need to
  enumerate tickets. That is the full extent of your tool use.
```

##### Dispatch prompt: quote the ticket body verbatim

The dispatch prompt sent to each research Agent must embed the parent Task body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names, file paths) that the worker will then reason about literally. Read the Task via `bees show-ticket --ids <task-id>` and embed the returned body in the prompt as a quoted block immediately after the research-mode preamble. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "you are dispatched in research mode for this Task") is fine; the body itself stays untouched. The orchestrator's progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the dispatched role's contract file (`agents/<role>.md`). The rule applies to **every** dispatched role type — both the implementer roles (Engineer / Test Writer / Doc Writer) and the review-only roles (PM, Code Reviewer, Test Reviewer, Doc Reviewer). Concrete examples of forbidden softening (illustrative, not exhaustive):

- MUST NOT tell the Engineer it may also write tests or docs.
- MUST NOT tell the Test Writer it may also modify source code.
- MUST NOT tell the Doc Writer it may also modify source or test files.
- MUST NOT tell the PM or any reviewer (Code Reviewer / Test Reviewer / Doc Reviewer) it may write source, tests, or docs — these are review-only roles, and the contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (each reviewer) explicitly.
- MUST NOT tell one reviewer it may also review another reviewer's lane (e.g., Code Reviewer reviewing tests, or Test Reviewer reviewing documentation).

The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also propose this one cross-lane Subtask" / "you may also reason about this one out-of-lane file"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer research dispatch, a re-scoping of the Task, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other; the only handoff is from worker to orchestrator (the diff in execution mode, the JSON return in research mode), never worker-to-worker. So a softening clause cannot be made safe by adding "coordinate with the other role's findings" or similar coordination prose — that channel does not exist.

##### Procedural gate

If the first research dispatch (or any later dispatch) returns an `Agent type '<name>' not found`-style error from the Agent tool for any of the four research roles (`engineer`, `test-writer`, `doc-writer`, `pm`), STOP at the procedural gate and emit the hard-fail message defined in this skill's `## Preconditions` section — do not fall back to `general-purpose`, do not skip the dispatch, do not improvise a substitute role. This is the sole verification mechanism for the subagents precondition: the procedural gate is what enforces the contract honestly against Claude Code's session-load semantics, firing at the natural failure point.

#### Hub-and-spoke via substrate

Workers do not message each other. The orchestrator is the hub; each dispatched research Agent is a spoke that reads its prompt, returns findings as text, and exits. The JSON-structured findings text is the handoff to the orchestrator's next reconciliation tick — when an implementer-research Agent returns its proposed-Subtask JSON, the orchestrator parses it, authors body files, and runs `bees create-ticket`; when the PM research Agent returns its traceability findings, the orchestrator acts on them by dispatching gap-fill research Agents or transitioning tickets to `ready`. Hub-and-spoke is a **structural property** of ephemeral background research Agents, not a rule the orchestrator must remember to enforce: there is no inter-Agent channel for workers to even attempt peer-to-peer coupling on.

#### Recursive delegation: not supported

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every research Agent invocation originates from this skill's reconciliation loop, never from a worker.

A skill loads **inline into the caller's session**, so returning at Section 7 releases nothing — the context this run accumulated stays in the session it ran in, and nothing in this skill reclaims those tokens (the harness owns compaction). What bounds the growth is the **per-Epic scope of the loop itself**: one Epic's breakdown is the whole working set, and Section 7's fresh-session recommendation is the lever that actually reclaims context between Epics. Whenever the run continues in the same session — Mode 2's auto-continue, or the user taking the menu's same-session next-Epic continuation — Section 7's **Epic-boundary state-externalization checkpoint** is what keeps the growth survivable. It runs unconditionally at the end of Section 7 on every path, and it verifies that every load-bearing fact is already in a durable carrier, so whenever the harness compacts, the run can be re-derived rather than recalled.

#### Per-Task PM dispatch

When the implementer-research Agents (Engineer / Test Writer / Doc Writer, as applicable) have all returned for the current Task and the orchestrator has created the proposed Subtasks via `bees create-ticket`, dispatch a fresh PM research Agent. The dispatch prompt must include the Task ID, the list of proposed Subtask IDs the orchestrator just created, and the research-mode preamble — the PM, like the other roles, is read-only here. The PM's job is to review the proposed Subtask set against the Epic's spec source and return JSON findings flagging gaps, over-reach, or duplicated scope; the orchestrator is what acts on those findings (creating, updating, or deleting Subtasks per the PM's verdict).

The Epic's spec source can take three shapes, depending on what the parent Plan Bee's `reference_materials` carries:

- **`reference_materials` non-empty with `resolver: file-path` (or default)** — the spec source is the PRD/SDD file content read from disk (Scoped to the matching `### Feature: <title>` subsection when a Scoped-marker is present on the Bee body, per Section 2).
- **`reference_materials` non-empty with `resolver: bees`** — the spec source is the `body` of the parent Spec Bee's `t1=Doc` children (the children whose `title` is exactly `PRD` or `SDD`). The Scoped-marker pre-branch in Section 2 skips marker resolution on this path, since Spec Bees are already feature-scoped.
- **`reference_materials` null/empty** — the spec source is the Plan Bee body itself (existing fallback behavior).

Defer to `agents/pm.md` `### Resolving reference_materials entries` as the **authoritative spec for the resolution logic** — the PM Agent's own contract handles the per-entry resolver dispatch (file-path read vs. two-hop Spec Bee + `t1=Doc` children walk vs. body-as-spec fallback). Do NOT duplicate the title-match recipe or the children-enumeration walk in the dispatch prompt; the PM Agent already carries that logic and re-deriving it here risks divergence between the dispatch prompt and the agent contract.

**Record each PM-deferred item as a `defer-N` TaskList task at the moment of the PM verdict.** When the per-Task PM research Agent returns, walk its Final report deferred items (per `agents/pm.md`'s Final report contract). For every item the PM annotated with a destination of `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` (i.e., NOT `addressed-now`, which the orchestrator handles inline by dispatching a gap-fill research Agent), create a `defer-<short-suffix>` TaskList task (named per Section 4's "TaskList naming convention") with the deferral's one-line description as the `metadata.activity` string, status `pending`. Items annotated `addressed-now` are NOT added to the `defer-*` ledger — they are addressed by the orchestrator dispatching a gap-fill Agent in the next reconciliation tick. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when the PM surfaced deferrable items, defeating the gate's purpose.

#### Authoring Subtask bodies

Subtask bodies follow the mandatory template below (Context / What Needs to Change / Key Files / Acceptance Criteria) — they are multi-section markdown that trips Claude Code's command-injection guard if inlined as a `--body "..."` argument (any newline-followed-by-`#`-heading triggers the validator and forces a permission prompt), and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). For every `bees create-ticket` you run for a Task or Subtask, **author the body to a temp file via the `Write` tool and pass `--body-file <path>`** to `bees create-ticket`. Pick a temp path under the namespaced workflow scratch dir (`/tmp/.quorum/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.quorum\bees-body-<short-suffix>.md` on Windows), creating the `.quorum` subdir if absent:

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
```

Do **not** remove the file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so crashed runs leave debuggable artifacts in a known place. Status-only updates and genuinely single-line bodies can stay on inline `--body`.

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
- **Deferral-ledger tasks** — **Run scope**. Name: `defer-<short-suffix>` (e.g., `defer-1`, `defer-2`, or any collision-resistant suffix). Created when an agent's structured return (per `agents/pm.md`'s Final report contract — applied here to the PM research Agent's traceability-review output — or when the orchestrator surfaces an item it chose not to address inline this run) names a destination — `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. `metadata.activity` carries the deferral's one-line description so the gate prose (Section 6.5 below) can surface the active set. Marked `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (in which case `metadata.activity` logs the resolution path). The pre-handoff Section 6.5 gate reads this ledger for active `defer-*` entries and refuses to yield control while any remain pending or in-progress.
- **Gate-task tasks** — **Turn scope**. Name: `gate-<kind>-<short-suffix>` (today the dominant `<kind>` is `askuserquestion`, e.g. `gate-askuserquestion-1` for an `AskUserQuestion` gate fired during Section 0's conditional session-effort gate (fires only when the session is below the floor — see Section 0), Section 1's Bee or Epic pick gate, Section 1.5's multi-Epic run-mode gate, Section 5's Spec-Traceability gap-fill divergence escalation, Section 6.5's deferral-hygiene gate, or Section 7's Offer-Next-Steps menu). Created by the orchestrator via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract. The `<short-suffix>` MUST be unique per fire within the same run across every `gate-*` task regardless of `<kind>` — use one of the two acceptable patterns (monotonic integers or gate-specific slugs encoding context). The two-step contract applies at every gate this skill fires (the gates above are all trailer-less orchestrator-driven gates — this skill does not dispatch a review skill that returns a routing trailer). `metadata.activity` carries the gate's finite choices verbatim where applicable. Marked `completed` the moment the prescribed tool call returns and its result has been consumed (the user's answer routed, the next branch entered, etc.). Normally enters and exits within a single turn — the lifecycle is shorter than `defer-*` (which spans the whole run). The **yield-control discipline** mirrors `defer-*`: this skill MUST NOT yield control to the harness while any `gate-*` task is in `pending` or `in_progress` status. If a `gate-*` task is somehow left active when the orchestrator would yield, the next reconciliation tick walks the TaskList, surfaces the active `gate-*` task, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-research-<task-id>`, and `pm-research-<epic-id>`.

The `-research-` infix distinguishes these dispatches from the implementation-time dispatches in `/quo-execute` (which use `<role>-<subtask-id>` and `pm-<task-id>` per `quo-execute` Section 3's `##### TaskList naming convention`). A reader scanning a mixed TaskList can tell at a glance whether a given entry is breakdown-time research or execute-time implementation.

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

Any `AskUserQuestion` gate fired in this section (notably the Spec-Traceability gap-fill divergence escalation in the gap-fill loop, where a proposed gap-fill Subtask spans Tasks or does not belong to any existing Task) fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Section 4's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed.

When all Tasks have a per-Task PM-approved Subtask set from Section 4's reconciliation loop, run an **Epic-wide Spec Traceability Review** before any further `bees create-ticket` invocations and before any status transitions to `ready`. The review is the gate that catches spec coverage gaps the per-Task reviews could not see — a requirement that lives in the Epic-wide spec but does not naturally fall under any single Task can pass every per-Task PM review while still being absent from the proposed Subtask set as a whole.

Under research-only orchestration the Section 5 review is driven by a **fresh, ephemeral PM research Agent** — same dispatch shape as Section 4's `#### Per-Task PM dispatch`, scoped here to the whole Epic. The orchestrator (you) does not author the traceability table itself; the PM Agent returns it as JSON-structured findings, and the orchestrator consumes those findings to decide what to do next. If the PM flags GAP rows, the orchestrator dispatches additional research Agents to author the missing Subtask bodies, then re-dispatches the PM until all rows are OK. **Only after PM sign-off** does the orchestrator run `bees create-ticket` for any gap-fill Subtasks and transition Epic + Tasks + Subtasks to `ready`. Reviewing first and creating-or-amending tickets second avoids the delete-and-recreate churn that "create everything, then traceability-review, then patch" produces.

You must defer to the Product Manager on whether the Epic's Subtask coverage is final and complete. The orchestrator's role is to dispatch, integrate findings, and act on them — not to substitute its own judgment for the PM's verdict.

#### Lightweight-path exception (Section 2.5)

When Section 2.5 selected the **lightweight path**, replace the iterative gap-fill loop below with a **single Epic-wide traceability pass**: dispatch exactly one PM research Agent (same dispatch shape, one `pm-research-<epic-id>` TaskList task) to check that every Epic scope / acceptance-criteria requirement is covered by a Subtask. If it returns all-`OK`, proceed straight to Step 5 (create any gap-fill tickets — none expected — and transition to `ready`). If it flags a GAP, the orchestrator fills it directly (authoring the operational Subtask per Section 4's lightweight-path exception) and re-dispatches the PM **once** to confirm; do **not** enter the multi-round loop. Keeping one PM dispatch preserves the PM's authority and the "nothing dropped from spec" guarantee at a fraction of the full path's cost (no per-Task PMs, no unbounded gap-fill iteration). On the **full path**, ignore this exception and run the full gap-fill loop as written below.

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

Resolve the placeholder against **this skill's own base directory**: `<this skill's base directory>/scripts/scoped_marker_resolver.py`. The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-breakdown-epic`).

**This differs from `quo-execute` and `quo-fix-issue`.** Those two skills resolve the same helper as a *sibling* of their own base directory — `<base>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` — because the helper is shipped by `quo-breakdown-epic` and they consume it across skills. Here, in `quo-breakdown-epic` itself, the helper lives **inside this skill**, so resolution drops the `..` hop and points at this skill's own `scripts/` subdirectory. Do not copy `quo-execute` / `quo-fix-issue`'s sibling-resolution string into this skill — it would resolve to a path that does not exist on disk.

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

**Record each Epic-wide PM-deferred item as a `defer-N` TaskList task at the moment of the PM sign-off.** When the Epic-wide PM research Agent returns its final all-`OK` table, also walk its Final report deferred items (per `agents/pm.md`'s Final report contract — applied here to the Spec Traceability Review output). For every item the PM annotated with a destination of `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`, create a `defer-<short-suffix>` TaskList task (named per Section 4's "TaskList naming convention") with the deferral's one-line description as the `metadata.activity` string, status `pending`. Items annotated `addressed-now` are NOT added to the `defer-*` ledger — they were addressed during the gap-fill iteration above. This upstream record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it, the gate would fire empty even when the Epic-wide PM surfaced deferrable items, defeating the gate's purpose.

##### Step 5 — Create gap-fill tickets, then transition to `ready`

Only after PM sign-off (all rows `OK`):

1. For each gap-fill Subtask body the research Agents authored during Step 4, run `bees create-ticket --body-file <path>` against the appropriate parent Task — author bodies to temp files under `<tempdir>/.quorum/` per Section 4's `#### Authoring Subtask bodies` convention. Wire each new Subtask's `parent` to the owning Task ID, and add `up_dependencies` where another Subtask must complete first.
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

**Do not hardcode the Plans-hive path.** `/quo-setup` lets users place hives in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/plans/` silently stages nothing when the user picked an out-of-repo location.

To learn the in-repo Plans hive path, run the bundled helper's NON-MUTATING `resolve-hive-paths` mode (the same `hive_commit.py` helper this skill calls at its Section 6.5 Encode step — resolve its sibling path the same way). The helper emits the Plans hive's absolute path when it lives inside this repo, or nothing when it lives outside. Run it as a single literal Bash call:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive plans
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive plans
```

When the helper emits a Plans hive path, `git add` it, then commit with a single literal `git commit` command. Prefix the subject with the enclosing Plan Bee by its bare ID, then `Break down ` and the Epic's human label (its `<epic-title>`, which carries the `Epic N — ` ordinal), and append the bare Epic ID once in trailing parentheses (substitute the actual Plan Bee ID, Epic title, and Epic ID — e.g. `Plan b.bc7, Break down Epic 2 — Publish notification_common (t1.rwx.o4)`). You obtain the enclosing Plan Bee ID by walking the Epic's parent chain (Epic → Bee) — context you already hold from this run. If the Epic has no parent Plan Bee (a standalone Epic), omit the `Plan <bee-id>, ` prefix and lead with `Break down <epic-title> (<epic-id>)`:

```bash
# POSIX (bash / zsh):
git commit -m "Plan <bee-id>, Break down <epic-title> (<epic-id>)"
```

```powershell
# Windows (PowerShell):
git commit -m "Plan <bee-id>, Break down <epic-title> (<epic-id>)"
```

**Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this Epic breakdown.

If the helper emits nothing — the Plans hive lives **outside** the repo — skip the `git add` and `git commit` and remember to surface a one-line note in Step 7 so the user knows the new tickets are persisted by the bees CLI but not git-tracked here.

### 6.5 Before handoff — deferral hygiene

Every `AskUserQuestion` firing in this gate (Step 2's initial Fix / File / Encode choice, plus any Step 3 re-fires when an earlier routing branch failed to close out a subset of the active `defer-*` set) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate (a distinct `<short-suffix>` per fire, so the Step 3 re-fires are not mistaken for the Step 2 first fire), then `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed.

Throughout the Epic-breakdown loop (Section 4's per-Task implementer research dispatch and Section 5's Spec Traceability Review with its gap-fill iteration), the PM research Agent and the implementer research Agents may have flagged items as "address during /quo-execute", "defer to implementation", "pick up during a follow-up Issue", or similar inter-session deferrals. Per `agents/pm.md`'s Final report contract, each such item arrives with a destination annotation; the orchestrator records the items it chose not to address inline as `defer-<short-suffix>` TaskList tasks per Section 4's TaskList naming convention (at the per-Task PM dispatch site and at the Section 5 Spec Traceability Review sign-off site). This gate is the pre-handoff reconciliation step that closes them out into durable inter-session carriers before Section 7's next-Steps menu — which explicitly recommends a fresh Claude Code session for `/quo-execute` — yields control.

**Step 0 — Retroactive ledger reconciliation (safety net).** The per-Task PM dispatch site in Section 4 and the Section 5 Spec Traceability Review sign-off site each instruct the Director to create a `defer-<short-suffix>` TaskList task per PM-deferred item at the moment of the verdict. Before running Step 1's enumeration, walk every PM research Agent's Final report deferred items captured during the run (per-Task PM dispatches in Section 4 and the Epic-wide Spec Traceability Review PM dispatch in Section 5) and **create a corresponding `defer-*` TaskList task for any item that does not already have one**. Items annotated `addressed-now` are skipped — they were addressed inline by a gap-fill dispatch. The upstream record-creating instructions at the per-Task PM site and the Section 5 sign-off site are the load-bearing source; this retroactive sweep is the defense-in-depth safety net for orchestrators that miss the instruction. After the retroactive reconcile, every deferred item is represented in the active `defer-*` set and Step 1's enumeration sees the canonical view.

**Step 1 — Enumerate the active deferral ledger.** Scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. If the active set is empty, emit a one-line console message — recommended string: `Deferral hygiene: no deferred items.` — and proceed to Section 7 (Offer Next Steps).

**Step 2 — Surface the active set and gate the user choice.** When the active set is non-empty, surface the list to the user as numbered markdown (one bullet per `defer-*` task, the `metadata.activity` text as the bullet's body), then fire the user gate through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 4's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` with the finite choices below in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the routing into Fix / File / Encode begins.

- **Fix in this session** — Re-dispatch the appropriate implementer / PM research Agents per Section 4's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch below, to resolve each deferred item now. After each item is resolved, mark its `defer-*` TaskList task `completed` (with `metadata.activity` updated to log the resolution path).
- **File as issue tickets** — For each item, invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body (the precedent for inline-Skill-tool dispatch lives in `/quo-fix-issue` Section 1's URL-resolution sub-step and `/quo-plan` Step 4b). Mark each `defer-*` TaskList task `completed` once the `/quo-file-issue` dispatch returns successfully and the created Issue ID is captured.
- **Encode in an existing ticket body** — For each item the user maps to an existing ticket (a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass), append a `## Deferred from /quo-breakdown-epic run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body and run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update, where `<YYYY-MM-DD HH:MM>` is the current local date and time written into the heading from your own clock via the `Write` tool (it is a value you author into the body-file as a string, not a shell-computed substitution — do not add a `date` / `Get-Date` snippet for it). Keep the `## Deferred from /quo-breakdown-epic run` stem verbatim and only append the parenthesized timestamp suffix: the suffix exists so that multiple Encodes to the same ticket body across separate runs sit side-by-side with distinguishable headings rather than stacking identical ones — do not simplify it back to a bare heading. Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir. **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode — e.g., for the encode triggered by `defer-3`, the scratch file is `bees-body-defer-3.md`. Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the scratch file directly back to its TaskList progenitor:

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

  **Follow-up commit (after all Encode writes in this gate firing have landed).** This gate fires AFTER Section 6's commit step has already committed the Tasks and Subtasks this run created — so the `bees update-ticket --body-file` writes above persist new on-disk changes to the relevant hive's per-ticket directory (or to the project PRD/SDD file path), but those changes are NOT swept into Section 6's commit and would otherwise leave the working tree dirty when the skill yields to Section 7's next-Steps menu (which explicitly recommends a fresh Claude Code session for `/quo-execute` — a dirty working tree at that boundary forces the user to reconcile manually). Produce one follow-up commit per gate firing covering all Encode writes from this firing — not per Encode item — to keep commit churn proportional to the user's choice. Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (the same pattern Section 6 uses for Plans), `git add` each hive path that lives inside this repo, additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations, then commit only if `git diff --cached` shows staged changes (an out-of-repo hive plus no PRD/SDD encode routes would stage nothing — skip the commit in that case rather than producing an empty one). Commit subject contract: `Encode deferral: /quo-breakdown-epic — <N> deferral(s) encoded` where `<N>` is the count of `defer-*` items the user routed to Encode in this gate firing. **`<N>` counts deferral items, not tickets** — several items can be encoded into one ticket body, and one item can be encoded into several, so the item count is the honest number and is the same value passed as the helper's `--count` below.

  This workflow (hive-path resolution via `bees list-hives`, in-repo scoping, conditional commit on staged state) is encapsulated in a bundled Python helper, `hive_commit.py`, so the orchestrator runs it as a single literal Bash tool call rather than decomposing a multi-step shell snippet at runtime. The helper resolves the Plans/Specs/Issues hive paths, `git add`s each hive path that lives inside this repo (out-of-repo hives have already had their bees update persisted by `bees update-ticket` and require no git action), `git add`s any project PRD/SDD paths passed via `--doc-path`, then commits only if there are staged changes — printing `skipped: nothing staged` and making no commit when nothing is staged. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree (same anti-pattern as Section 6's commit step); the helper stages only the resolved hive paths and the explicit `--doc-path` arguments, never `-A`.

  **Resolving the helper path (sibling-skill resolution).** `hive_commit.py` is shipped by `/quo-execute`; this skill consumes it as a *sibling* bundled script. Resolve its path at runtime from this skill's own base directory: `<this skill's base directory>/../quo-execute/scripts/hive_commit.py`. The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-breakdown-epic`). Use the `..` traversal pattern to reach the sibling skill — this matches the same sibling-resolution discipline used elsewhere in the skill set (note: this skill *owns* `scoped_marker_resolver.py` but *consumes* `hive_commit.py`, so the two helpers resolve differently — own-skill `scripts/` for the former, sibling `../quo-execute/scripts/` for the latter). On Windows, use backslash separators: `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py`.

  Invoke it with `--skill quo-breakdown-epic`, `--count <N>` (the count of `defer-*` items the user routed to Encode in this gate firing — matching the commit-subject contract above), and one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`; omit entirely in the common case where no doc was routed):

  ```bash
  # POSIX (bash / zsh):
  python3 "<resolved-helper-path>" --skill quo-breakdown-epic --count <N> [--doc-path <abs-path> ...]
  ```

  ```powershell
  # Windows (PowerShell):
  python "<resolved-helper-path>" --skill quo-breakdown-epic --count <N> [--doc-path <abs-path> ...]
  ```

  After the helper lands the commit (or prints `skipped: nothing staged`), proceed to Step 3 below.

The three options are mutually-non-exclusive at the active-set level — the user may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., "fix items 1 and 2 now, file 3 as an Issue"). Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. When the user wants to route different items to different options, they select `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`) and type the per-item routing in free-form; the orchestrator parses the reply and closes out each `defer-*` task accordingly.

**Step 3 — Hard-stop on a non-empty active set.** Until every `defer-*` task is `completed`, the skill cannot proceed to Section 7 (Offer Next Steps). This is the structural enforcement: a deferral that was important enough to surface during the breakdown is important enough to encode in a durable carrier before the run ends — `/quo-execute` reads bees tickets, CLAUDE.md, and source code in its fresh session and has zero visibility into this session's conversation. If the user picks options that fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or a `bees update-ticket` invocation errors), surface the still-active `defer-*` tasks back to the user with `AskUserQuestion` and re-run the gate until the active set is empty.

The fresh-session-per-phase recommendation at Section 7's menu is preserved verbatim — this gate sits before that handoff prose; it does not replace it.

### 7. Offer Next Steps

The Offer-Next-Steps `AskUserQuestion` menu fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this Offer-Next-Steps gate (per Section 4's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the chosen branch is entered.

After the Epic (or all Epics, if breaking down a whole Bee) is fully broken down and the new ticket files have been committed (or noted as out-of-repo), present the user with clear options. Use `AskUserQuestion`.

Note above the options: `/quo-execute` re-reads the Bee, Epics, and Tasks from the bees CLI and reads CLAUDE.md from disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives the executing agents full context budget for per-Task implementation, review cycles, and the orchestrator's running judgment. Continuing to break down the next Epic in this session is lower-risk (same skill, similar context footprint), but a fresh session is still preferred for big Bees.

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

#### Branch on the captured multi-Epic run mode

Before rendering the menu in `#### Menu options` below, branch on the multi-Epic run mode captured in Section 1.5:

- **Mode 1 (Stop after each Epic), or Section 1.5 was skipped** (only one drafted Epic remained at run start): render the full six-option menu in `#### Menu options` verbatim with the Recommended badge placed per `#### Pick the Recommended option`. This is the existing per-Epic confirmation behavior.

- **Mode 2 (Work through all Epics)**: branch on which case the `#### Pick the Recommended option` logic identified for this Epic boundary:
  - **No-drafted-siblings case** — planning is done. Render the full menu so the user can pick what to do next (typically *"In a fresh session, execute the whole Bee"*); there is no auto-continue target since no drafted Epics remain.
  - **Drafted-siblings-remain, reshape-risk case** — this is one of Mode 2's mandatory pause cases. Render the full menu with *"In a fresh session, execute this Epic first; defer downstream breakdown"* as the Recommended pick exactly as it would in Mode 1. Mode 2 does not auto-continue past a contract-stability concern; the user must resolve the reshape risk explicitly.
  - **Drafted-siblings-remain, no-reshape-risk case** — auto-select *"In a fresh session, break down the next Epic"* (or the same-session continuation noted in that option's prose). Do not present the menu; surface a one-line note to the user announcing the auto-continue and naming the next Epic ID being broken down so they can interrupt if desired (e.g., *"Mode 2 (Work through all Epics): auto-continuing to break down `<next-epic-id>` — `<title>`."*), then fall through to the **Epic-boundary state-externalization checkpoint** at the end of this section — which runs on this path exactly as it does on the menu paths — then run the **Context-window boundary guard (same-session Epic continuation)** defined at the end of this section (this auto-continue path is one of the two same-session-continuation paths that guard fires on), and proceed to break down the next drafted Epic in this same session against the same captured Mode 2 choice **only if the guard does not stop the run.**

The Mode 2 auto-continue path still respects every other stop the orchestrator already enforces: any final Bee-level reviewer finding flagged as a blocker, any genuine red flag the orchestrator surfaces during the next Epic's breakdown, and any precondition or contract violation. Mode 2 is *"skip discretionary continue-or-not prompts"*, not *"skip every interactive prompt"*.

#### Menu options

Always include all six options below. The Recommended badge moves across three of the options (whole-Bee execute, this-Epic-first execute, break-down-the-next-Epic) per the three-way branch above. Each option carries a one-line "best when …" clause so the user can compare trade-offs without external context. When an option is the Recommended pick for the current run, replace its generic `Best when …` clause with the case-specific rationale called out in step 4 of *Pick the Recommended option* (which siblings are at risk / which siblings are still drafted with pure-ordering dependencies / etc.) — that subtitle is the only place the rationale is surfaced.

- **In a fresh session, execute the whole Bee** — run `/quo-execute <bee-id>` (e.g. `b.duy`) in a new Claude Code session. `/quo-execute` walks every Epic in the Bee in dependency order.
  - *Best when* every Epic in the Bee is already broken down and the plan is ready to ship.
  - *Recommended when no drafted Epics remain under the parent Bee.*
- **In a fresh session, execute this Epic first; defer downstream breakdown** — run `/quo-execute <epic-id>` (e.g. `t1.duy.c9`) in a new session, scoped to the Epic just broken down. After it lands, return to break down the dependent siblings against the now-stable contract.
  - *Best when* drafted siblings rewrite-to-consume what this Epic produces and the contract is still in flux — execute now, then break down siblings against the locked-in contract.
  - *Recommended when drafted siblings present reshape risk.* Name the at-risk siblings inline.
- **In a fresh session, start at a specific Epic** — run `/quo-execute <epic-id>` in a new session. `/quo-execute` accepts an Epic ID; it finds the parent Bee automatically and starts from that Epic's position in the plan. All Epics still run — this just biases the entry point.
  - *Best when* the user wants the bulk-execute walk but with a specific entry point (e.g., the just-broken-down Epic, or an upstream foundational Epic).
- **In a fresh session, break down the next Epic** — run `/quo-breakdown-epic <next-epic-id>` in a new session if more Epics in this Bee remain in `drafted` state. Same-session continuation is also reasonable here since the skill is repeating with similar context growth per Epic. When the user takes the **same-session** continuation, then after the **Epic-boundary state-externalization checkpoint** below has run (it runs unconditionally on every path) and before breaking down the next Epic in this same session, run the **Context-window boundary guard (same-session Epic continuation)** defined at the end of this section, and proceed to break down the next Epic in-session **only if the guard does not stop the run.** When the user instead launches the fresh-session command (`/quo-breakdown-epic <next-epic-id>` in a new session), the guard does **not** fire — the run ends here.
  - *Best when* the user wants to finish planning before any execution starts and there's no contract-reshape risk that would make the next Epic's Tasks go stale.
  - *Recommended when drafted siblings remain with no reshape risk.* Name the still-drafted siblings inline.
- **Review first** — let the user review the plan before proceeding.
  - *Best when* the user wants to scan the new Tasks and Subtasks for shape/scope before committing to an execution path.
- **Done for now** — plan is saved; user will come back later.
  - *Best when* the user is at a natural stopping point and will return in a later session.

#### Epic-boundary state-externalization checkpoint

**Run this checkpoint unconditionally, on every path, in every mode — it is the last *unconditional* step of Section 7, followed only by the conditional `#### Context-window boundary guard (same-session Epic continuation)` below on the two same-session-continuation paths that fire it.** It runs after the menu answer has been consumed (Mode 1, and every Mode 2 case that renders the menu) or immediately after the Mode 2 auto-continue note is surfaced (the case that skips the menu), and before control either returns to Section 2 for the next Epic or leaves the skill. Do **not** condition it on the captured run mode, on which menu option the user picked, or on whether the next Epic will be broken down in this session or a fresh one. Several of these paths continue in the same session — Mode 2's auto-continue skips the menu entirely, and the menu's own *"In a fresh session, break down the next Epic"* option explicitly blesses same-session continuation — and making the checkpoint unconditional removes the need to work out which case is in play before deciding whether to run it.

Its job is to verify that every load-bearing fact is already in a durable carrier and to refresh the ones this skill owns, so that whenever the harness compacts the conversation — at this boundary or partway through the next Epic — the run can be re-derived instead of reconstructed from memory. On the paths where the run ends here rather than continuing (*Done for now*, *Review first*, any fresh-session option), run it exactly the same way with `none` as the next unit: what it verifies and writes is precisely what has to outlive this session. This is the canonical anchor name; Section 4's `#### Recursive delegation: not supported` refers to it by name.

The durable carriers for this skill are:

- **the Tasks and Subtasks created in bees** for the just-broken-down Epic, and that Epic's own status transition to `ready`. Re-readable via `bees show-ticket` / `bees execute-freeform-query`.
- **the Section 6 commit of the new ticket files** (when the Plans hive lives inside this repo). Re-readable via `git log` / `git diff`.
- **the `defer-*` TaskList ledger** — already emptied by Section 6.5's hard-stop gate before control reaches Section 7. Re-readable by walking the TaskList.
- **the run-state manifest** — the on-disk file defined in Section 1.5 `#### Write the run-state manifest`, which carries the run-scoped values (multi-Epic run mode, unit scope, pre-run SHA, per-Epic progress) that have no other durable home. Re-readable via the `Read` tool.

This skill has **no compromise tracker** — that carrier belongs to the execution skills, not to breakdown. Do not look for one here.

Run these three steps. Every step below is a tool call the orchestrator can actually make — run a bees query, run a git command, walk the TaskList, read a file, write a file:

1. **Verify the carriers.** Do all four:
   - Re-query the just-broken-down Epic's children in bees and confirm every Task has its PM-approved Subtask set and the expected non-`drafted` statuses.
   - **Validate the run-state manifest is this session's before reading any field out of it.** `Read` it and confirm its **Progress** names only Epics this session actually broke down and its **Unit scope** matches the unit in hand. If it names an Epic this session never touched — the sibling-collision tell described at the definition site, Section 1.5 `#### Write the run-state manifest` — apply that section's three-step recovery (rewrite from bees, re-fire the mode gate, accept the weaker unbounded commit-landed check) instead of trusting the **Multi-Epic run mode** and **Pre-run SHA** it carries.
   - Confirm Section 6's ticket-file commit landed: take the validated manifest's **Pre-run SHA** field and run `git log --oneline <pre-run-sha>..HEAD` to see the commits this run produced. (If the Plans hive lives outside this repo there is no commit to find, and an empty log is the correct result — re-run Section 6's non-mutating `resolve-hive-paths` helper call to confirm which case applies rather than recalling it.)
   - Walk the TaskList and confirm every research-Agent, PM, and `gate-*` task from this Epic is `completed` and the `defer-*` active set is empty.

   Fix any gap **now** rather than carrying it forward in conversation.
2. **Rewrite the run-state manifest** per Section 1.5 `#### Write the run-state manifest`, recording the just-broken-down Epic's ID under progress and the next Epic's ID as the next unit (or `none` when the run is ending here).
3. **Re-read, do not recall, at every dispatch in the next Epic.** Concretely: before each research-Agent or PM dispatch in the next Epic, `bees show-ticket` that Epic's body and its parent Bee (including `reference_materials`) and `Read` the run-state manifest for the run-scoped values (captured mode, unit scope, pre-run SHA) — rather than reusing a value quoted earlier in the conversation. Carry **no** value forward from the prior Epic: if a fact the next Epic needs is not readable from one of the carriers above, stop and write it into one before dispatching anything.

**What this checkpoint does not do.** It does not clear, compact, or otherwise reclaim the orchestrator's context, and it must never be narrated as if it did. No model-invocable mechanism for self-clearing or self-compacting exists; token reclamation is owned by the harness, which compacts the conversation on its own once the window fills. The reclamation lever that does exist is the fresh-session recommendation already carried in this section's standing note and menu options — this checkpoint is what makes that lever, and any harness compaction whenever it fires, lossless.

#### Context-window boundary guard (same-session Epic continuation)

**Scope — this guard fires on the two same-session-continuation paths.** It runs on (a) the **Mode 2 (Work through all Epics), drafted-siblings-remain, no-reshape-risk auto-continue-to-next-Epic path** of `#### Branch on the captured multi-Epic run mode` above, and (b) the **menu's *"In a fresh session, break down the next Epic"* option when the user continues in the *same session*** rather than launching a fresh session — the two paths that continue in the *same session* without ending the run. It fires **after** the Epic-boundary state-externalization checkpoint has run (so all run-scoped state is already durable on disk and a fresh session could resume losslessly) and **before** the skill proceeds to break down the next drafted Epic. Do **not** run it on any fresh-session launch (including when the user takes that same menu option by launching `/quo-breakdown-epic <next-epic-id>` in a new session), on any menu-rendering path that ends the run in place (Mode 1's other options, the Mode 2 no-drafted-siblings case, the Mode 2 reshape-risk case's **other options**), or on any run-ending path (*Review first*, *Done for now*, the fresh-session menu options): those recommend a fresh session and end the skill rather than auto-continuing in place, so there is nothing to guard. Unlike the Epic-boundary checkpoint — which is unconditional on every path — this guard is deliberately conditional; do **not** inherit the checkpoint's unconditionality.

**What it reads, and what it is not.** The guard reads an **external gauge file** published by a separate status-line producer process — `context_gauge.py`, shipped by `/quo-setup`. It does **not** measure the orchestrator's own token usage and is **not** self-introspection: it consults another process's file and, if that file reports the context window is near the harness's auto-compaction point, stops the run at this clean Epic boundary so the next Epic starts fresh instead of mid-way into a compaction. The only context-reclamation lever this skill has is the **fresh-session recommendation**; the orchestrator has no model-invocable self-clear or self-compact, so this guard never claims to reclaim context — it stops and recommends, nothing more.

**Ordering is load-bearing (mirror Section 0's `### 0. Check session reasoning effort`).** Read the session id **first**, evaluate it, and only *then* decide whether a gate task fires. Do NOT `TaskCreate` a `gate-*` task before the branch below reaches the one case that fires one — on every path except the `missing`-without-opt-out case no gate fires at all, and a stranded `pending` `gate-*` task violates the two-step contract's yield-control discipline, whose recovery mechanism would re-fire the prescribed tool from the leftover task on a later run and produce a phantom prompt.

**Step 1 — read the session id.** One literal command:

```bash
# POSIX (bash / zsh):
printenv CLAUDE_CODE_SESSION_ID
```

```powershell
# Windows (PowerShell):
Write-Output $env:CLAUDE_CODE_SESSION_ID
```

**Trim any trailing whitespace/newline** from the value before using it — a trailing newline fails the helper's `--session-id` validation.

**Step 2 — session id unset or empty → skip the guard silently and continue** to break down the next Epic. This is the ONLY silent-skip path (the unsupported-CLI carve-out, matching Section 0's `CLAUDE_EFFORT`-unset handling): an older CLI or a launch path that does not export the session id cannot be guarded, and a spurious stop on every run is worse than a missed advisory.

**Step 3 — session id present.** Resolve the helper as a **sibling of this skill's base directory**: `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (POSIX `/`, PowerShell `\`). The base directory is shown in the skill invocation header at session start. This is the same sibling-resolution discipline this skill already uses for `hive_commit.py` (`../quo-execute/scripts/...`) — `context_gauge.py` is shipped by `/quo-setup`, so it resolves under `../quo-setup/scripts/`, not this skill's own `scripts/`.

a. **Obtain the stop threshold from the helper's threshold seam** — one literal call that prints a single integer to stdout. Read `context_gauge.py` at runtime to confirm the subcommand name (`stop-threshold`). **Never restate the numeric threshold in this prose** — always obtain it from this call.

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold
```

b. **Read the gauge for this session** — one literal call, substituting the trimmed session id from step 1:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-id>
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" read --session-id <trimmed-id>
```

c. **Branch on the read output and exit status.** `read` prints one of four values and exits 0 for all four; it exits non-zero (2) on a malformed gauge file OR an invalid `--session-id`:

- **An integer ≥ the threshold → STOP** at this boundary. Report the current percentage to the user and recommend resuming in a **fresh session**, naming the exact resume command — `/quo-breakdown-epic <bee-id>` (or `/quo-breakdown-epic <next-epic-id>` for the specific next drafted Epic). Then exit the skill; do NOT break down the next Epic in this session. The Epic-boundary checkpoint already externalized all run-scoped state, so the fresh session resumes losslessly.
- **An integer < the threshold → continue** silently to break down the next Epic. No output.
- **`no-reading` → continue** silently. The file exists and is fresh but carries no percentage yet (transient — a live producer early in a session or just after a compaction); the producer is alive, so this is not a stop signal.
- **`stale` → STOP** at this boundary. A stale gauge means the producer is not updating the file; because usage only grows within a session, a stale number biases low and cannot be trusted to have cleared the threshold. Note to the user that the status-line producer appears stalled, and that recurring staleness across fresh sessions means they should check their status-line producer configuration. Recommend the fresh-session resume with the `/quo-breakdown-epic <bee-id>` command. Do NOT let `stale` fall through to continue.
- **Non-zero exit, or empty stdout → the same fail-safe stop-and-ask as `stale`.** The reading is untrustworthy, so stop rather than continue. Note that `read` exits 2 on a malformed gauge OR an invalid `--session-id` — do NOT assume exit 2 implies a corrupt file. Recommend the fresh-session resume. Never fall through to continue.
- **`missing` → consult the opt-out marker, then branch.** First check the persistent opt-out marker via one literal existence check:

  ```bash
  # POSIX (bash / zsh):
  test -f /tmp/.quorum/context-guard-opt-out
  ```

  ```powershell
  # Windows (PowerShell):
  Test-Path "$env:TEMP\.quorum\context-guard-opt-out"
  ```

  **If the marker is present → skip the guard silently and continue** to break down the next Epic. If the marker is absent → **hard-stop via the two-step `TaskCreate` → `AskUserQuestion` gate** in step 4.

**Step 4 — the missing-reading gate (only on `missing` with no opt-out marker).** Honor the two-step `TaskCreate` → `AskUserQuestion` contract (per Section 4's TaskList naming convention's gate-task entry): first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task (distinct per-fire suffix) naming this boundary context-guard gate, then call `AskUserQuestion` in the **same turn**; do not yield control while that task is `pending`/`in_progress`, and mark it `completed` the moment the answer is consumed. The question text must (a) state that the environment may override the operator's user status-line config, so no gauge reading is being published for this session; (b) publish the gauge file contract — the per-session gauge file's path under `<tempdir>/.quorum/`, its required fields (the `session_id` and the `context_window.used_percentage` reading), and its overwrite-per-refresh semantics; (c) state that **Configure now** runs `/quo-setup --configure-gauge-producer` inline. Present these four options (multi-choice only — no fake free-text options):

- **Configure now** — invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool. Because a freshly-configured producer only begins publishing NEXT session, after a successful Configure now the gate **recommends resuming in a fresh session** (naming the `/quo-breakdown-epic <bee-id>` resume command) rather than implying this run is now guarded, then exit the skill.
- **Proceed without the guard (this run)** — continue to break down the next Epic; write no marker.
- **Never guard me (persistent opt-out)** — write the persistent marker via the sibling helper's `write-opt-out` subcommand (one literal call), then continue to break down the next Epic:

  ```bash
  # POSIX (bash / zsh):
  python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" write-opt-out
  ```

  ```powershell
  # Windows (PowerShell):
  python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" write-opt-out
  ```

- **Stop here** — exit the skill with the `/quo-breakdown-epic <bee-id>` fresh-session resume command.
