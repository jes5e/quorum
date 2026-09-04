# <img src="assets/header.png" alt="" width="48" valign="middle"> quorum

**Parallel, high-throughput autonomous software engineering.**

**quorum** is a [Claude Code](https://claude.com/claude-code) skill set for running a multi-agent SDLC over a structured ticket system. It's built for shipping large features and full applications with LLMs. Plan, break down, execute, review, fix, repeat. Each step is picked up by a separate ephemeral agent — Engineer, Test Writer, Doc Writer, Product Manager, and three Reviewers — each running with role-isolated tools and handing off through ticket state, not chat history.

```
/quo-setup                           ← one-time per repo (safe to re-run)
        │
        ▼
/quo-plan  or  /quo-plan-from-specs  ← from an idea  /  from PRD+SDD on disk
        │
        ▼
/quo-breakdown-epic                  ← Epic → Tasks/Subtasks
        │
        ▼
/quo-execute                         ← do the work, with reviews

/quo-file-issue + /quo-fix-issue     ← anytime, for bugs/follow-ups
/quo-status                          ← anytime, "where am I?"
```

No special setup beyond Claude Code itself and the [bees](https://github.com/gabemahoney/bees) CLI — the supported ticket backend today, with [beads](https://github.com/gastownhall/beads) planned.

## Why this exists

Modern coding agents are excellent in tight scope and lossy in long ones. Hand a single agent a multi-day feature and the same failure modes recur: it accumulates a fog of in-session context that's hard to audit, it rubber-stamps its own diff during "review," it drifts silently from the spec you started with, and three hours in it has forgotten why a decision was made. Bigger context windows don't solve this — the underlying problem is **scope discipline**, not memory.

quorum's bet is that the way to ship agent-built features at production quality is to **decompose the work into ticketed units** and require **multiple independent agents to agree** on each unit before it ships. That's where the name comes from. In practice:

- **Specs and tickets are durable artifacts, not chat scrollback.** PRD and SDD live as docs under a Spec Bee; the Plan Bee decomposes into Epics, Tasks, and Subtasks. Each ticket carries Context, the change required, key files, and acceptance criteria — enough that a cold agent can do the work without ever reading the conversation that produced the ticket.
- **Each role is a separate ephemeral agent with locked-down tools.** Engineer, Test Writer, Doc Writer, Product Manager, and three Reviewers (code, test, doc). The Engineer can edit source but not tests; the Test Writer can edit tests but not source; the Reviewers can read and grep but not write. Fresh-eyes review is enforced at the tool layer, not the prompt — a reviewer literally cannot rubber-stamp the Engineer's diff because it isn't the same agent and never saw the implementation reasoning.
- **The PM is the spec-traceability gate.** After Engineer, Test Writer, and Doc Writer complete a Task, a PM agent reads the spec source, the Task ticket, the diff, and the sibling Tasks in the same Epic — and refuses to promote the Task if the diff drifted from spec, broke a sibling's assumption, or smuggled in unasked-for scope (e.g. backwards-compat scaffolding when the spec said no legacy support).
- **Handoffs are ticket state transitions, not messages.** A Subtask flipping `in_progress → done` is the load-bearing signal that the next role is unblocked. You can stop anywhere, restart any session, hand off to a teammate, or run multiple sessions in parallel — `/quo-status` tells you where the work currently sits.

A few design priorities fall out of this approach:

- **Parallel by construction, ordered where concurrency costs more than it saves.** Within a single run the orchestrator fans work out concurrently — sibling Subtasks get their own implementer Agents, and reviewers run as three simultaneous lanes. Where ordering costs less than redoing the work, lanes are serialized instead: in both execution skills, a review finding whose fix changes source is re-dispatched in order — Engineer, then code review, then the affected writer — so the next code-review round does not rewrite the tests and docs just written against the older diff. Throughput scales with how cleanly the work decomposes, not with one agent's serial pace.
- **Language- and stack-agnostic.** Skills read build, lint, and test commands from the target repo's `CLAUDE.md` instead of hardcoding `cargo`, `npm`, `pytest`, etc. Works on Rust, Node, Python, Go, Java, polyglot repos, or unknown stacks.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet ships in both POSIX bash and PowerShell forms; bundled helpers are cross-platform Python.
- **Idempotent.** Every state-mutating skill (`/quo-setup` especially) detects existing configuration and only prompts where something is missing. Re-runs are safe.
- **Plain-English statuses.** Plan tickets use `drafted` / `ready` / `in_progress` / `done`; issues use `open` / `done`. No bespoke vocabulary to memorize.
- **Cumulative project docs.** As features ship, the post-implementation Doc Writer folds them into the project-level PRD and SDD as `### Feature: <title>` subsections — old features stay documented; new features add to the record.

## Requirements

- **Claude Code** ([install](https://claude.com/claude-code))
- **bees CLI** (`pipx install bees-md`) — see [bees](https://github.com/gabemahoney/bees) for documentation. Requires Python 3.10+.
- **POSIX shell** (bash/zsh on macOS/Linux/WSL) **or PowerShell** (native Windows). Either works; every shell snippet in the skills is provided in both forms.

## Install

### Option A — global (recommended for single-user machines)

Copy the skills and subagent definitions into your user-level Claude Code directories so every repo can use them:

```bash
# POSIX (bash / zsh):
git clone https://github.com/jes5e/quorum ~/projects/quorum
cp -r ~/projects/quorum/skills/* ~/.claude/skills/
mkdir -p ~/.claude/agents
cp -r ~/projects/quorum/agents/* ~/.claude/agents/

# Windows (PowerShell):
git clone https://github.com/jes5e/quorum $HOME\projects\quorum
Copy-Item -Recurse $HOME\projects\quorum\skills\* $HOME\.claude\skills\
New-Item -ItemType Directory -Force -Path "$HOME\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\quorum\agents\* $HOME\.claude\agents\
```

### Option B — per-project install

If you want to try quorum on one repo without affecting others, copy the skills and subagent definitions into that repo's `.claude/skills/` and `.claude/agents/`:

```bash
# POSIX:
cp -r ~/projects/quorum/skills/* /path/to/your/repo/.claude/skills/
mkdir -p /path/to/your/repo/.claude/agents
cp -r ~/projects/quorum/agents/* /path/to/your/repo/.claude/agents/

# Windows (PowerShell):
Copy-Item -Recurse $HOME\projects\quorum\skills\* C:\path\to\your\repo\.claude\skills\
New-Item -ItemType Directory -Force -Path "C:\path\to\your\repo\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\quorum\agents\* C:\path\to\your\repo\.claude\agents\
```

### After install

If Claude Code is already running when you copy the files, the new subagent types from `~/.claude/agents/` (Option A) or `<repo>/.claude/agents/` (Option B) won't be registered yet — custom subagents are loaded at session start. You have two options to register them:

- **Run `/agents` in the session** — opens Claude Code's agents UI and hot-reloads the registry. Faster than a full restart; preserves the current session.
- **Restart Claude Code** — quit and relaunch. Always works.

Either way, until one of these is done, the quo-execute / quo-fix-issue / quo-breakdown-epic skills will fail with `Agent type 'engineer' not found` (or similar).

In any repo where you want to use the workflow, run:

```
/quo-setup
```

It will colonize hives (Plans + Issues + Specs), write a `## Documentation Locations` and `## Build Commands` section to CLAUDE.md, offer to bootstrap baseline PRD/SDD docs from your existing codebase, and offer to wire the optional status-line context-usage gauge producer into your status line. Safe to re-run if you skip a step and want to come back to it later.

## File and fix issues from a GitHub URL

Both `/quo-file-issue` and `/quo-fix-issue` accept a bug-tracker URL (GitHub Issue, Linear ticket, internal bug tracker, Slack archive) directly as an argument. The URL is auto-detected, a thin Issue ticket is filed with `reference_materials` pointing at the upstream resource, and the upstream body is fetched via `WebFetch` when the issue is picked up — no copy-pasting the report into a ticket body.

```
/quo-file-issue https://github.com/owner/repo/issues/123         # just file it
/quo-fix-issue  https://github.com/owner/repo/issues/123         # file and fix in one go
/quo-fix-issue  b.abc https://github.com/owner/repo/issues/456   # mix existing bees IDs and URLs
```

Re-running on the same URL dedupes against the existing Issue rather than creating a duplicate.

## The skills

### Skills you invoke

These are the entry points. Day-to-day, these are the only commands you type.

| Skill | What it does |
|---|---|
| `/quo-setup` | One-time configuration: hives, CLAUDE.md sections, optional PRD/SDD bootstrap from existing codebase, and an optional status-line [context-usage gauge producer](#enabling-the-gauge-producer) step. Idempotent — safe to re-run. On a new machine in an already-set-up repo, `/quo-setup` detects the existing hive markers and offers to just re-register them — and offers the producer step too — skipping the full walk-through. Pass `--configure-gauge-producer` to run only the [producer step](#enabling-the-gauge-producer): it skips the rest of setup and needs no configured repo. |
| `/quo-plan` | Interactive scope discovery for an idea, refactor, or feature without finalized specs. Authors per-feature PRD and SDD as `t1=Doc` children of a new Spec Bee in the Specs hive and links the Spec Bee from the Plan Bee's `reference_materials` — no project-doc mutation at plan time. Cumulative project-level PRD/SDD are updated after implementation by the `doc-writer` agent. Before handing off, a deferral-hygiene gate surfaces any "address later" items the run accumulated and routes each one to a durable carrier (`Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body`) so nothing is silently dropped at session boundary. Produces a Plan Bee with Epics. |
| `/quo-plan-from-specs` | Express path for when you already have a finalized PRD and SDD on disk. Default mode targets a **single-feature** PRD+SDD and hard-fails on PRDs **or SDDs** containing multiple `### Feature:` subsections. Pass `--feature "<title>"` to scope a single subsection inside a cumulative PRD+SDD — useful for re-planning one feature without going back through `/quo-plan`'s discovery loop. Produces a Plan Bee with Epics. |
| `/quo-breakdown-epic` | Decompose a single Epic into Tasks and Subtasks with the mandatory description template applied. Right-sizes the breakdown autonomously: an Epic whose entire scope is operational/sequencing work with no source, test, or doc changes (e.g. a manual-publish-and-verify gate) takes a lightweight path that skips the per-role research fan-out and the iterative PM gap-fill loop, collapsing to a single Epic-wide traceability pass — biasing toward the full path whenever the no-code classification is uncertain. Commits the new ticket files at end-of-skill (when the Plans hive lives in-repo) and presents a next-steps menu with per-option rationale. When more than one Epic remains in scope, surfaces a one-time multi-Epic run mode choice at the start of the run — Mode 1 (Stop after each Epic) or Mode 2 (Work through all Epics) — instead of re-prompting at every Epic boundary. Before yielding control, a deferral-hygiene gate closes out any "address later" items into durable carriers (existing ticket body, new Issue, or in-session fix). |
| `/quo-execute` | Execute a Plan Bee end-to-end — dispatch the ephemeral background subagents (Engineer, Test Writer, Doc Writer, PM, Code/Test/Doc Reviewer), walk every Epic in dependency order, commit per Task, review at Bee close. When more than one Epic is in scope, surfaces a one-time multi-Epic run mode choice at the start of the run — Mode 1 (Stop after each Epic) or Mode 2 (Work through all Epics) — instead of re-prompting at every Epic boundary. Before the final output, a deferral-hygiene gate closes out any "address later" items into durable carriers (existing ticket body, new Issue, or in-session fix). |
| `/quo-file-issue` | File a new issue ticket in the issues hive. Issues cover bugs, follow-ups, small features, tech debt — anything ticket-worthy that isn't planned upfront. Three invocation forms: (a) **in-conversation capture** — `/quo-file-issue` (interactive) or `/quo-file-issue <description>` produces an Issue whose body carries the full spec (Description / Current behavior / Expected behavior / Impact / Suggested fix); (b) **bare URL** — `/quo-file-issue <url>` auto-detects URL-shaped positional arguments (`^https?://`) and routes to the same external-reference branch as the flag forms — no flag required; (c) **external-reference flag forms** — `/quo-file-issue --reference <url>` (or its `--from-github <url>` alias) accepted as silent no-op aliases for backward compat. Both URL paths produce a thin Issue (2-3 sentence summary in the body) whose `reference_materials` points at an external resource (GitHub Issue, Linear ticket, Slack archive, internal bug tracker URL, etc.) under one of three canonical resolver names (`github-issue` / `linear-issue` / `url`, picked by the same URL-pattern resolver-name heuristic); `/quo-fix-issue` fetches the upstream content via `WebFetch` when picking the Issue up. Before filing, the skill dedupes by `reference_materials.value` against open Issues and surfaces `Use existing` / `File new` / `Cancel` on a match. Symmetric with `/quo-plan-from-specs` on the planning side. |
| `/quo-fix-issue` | Fix one or more issue tickets. Argument shapes: interactive (no args), `all`, single bees ID, list of bees IDs, single `<url>`, or a mixed `<id>` + `<url>` list. URL tokens (`^https?://`) trigger file-then-fix routing through `/quo-file-issue` (same dedupe and `WebFetch` fallback apply) and the resolved ticket IDs substitute the URLs *in place* in the working list, preserving the user-supplied prerequisite ordering. Dispatches the same ephemeral background subagents as `quo-execute` but at issue scope, plus an Analyst design-analysis gate that runs per Issue before the Engineer dispatch. Lanes are ordered rather than fanned out together: the Engineer and Code Reviewer loop until the code review comes back clean, then the Test Writer and Doc Writer run once against that settled diff, then the Test Reviewer, Doc Reviewer, and PM — and a later finding that changes source re-enters the Engineer loop before any writer is re-run, so docs and tests are not rewritten once per review round. A deferral-hygiene gate fires per-Issue (and again at end-of-batch in `all` / list mode) to close out any "address later" items into durable carriers (existing ticket body, new Issue, or in-session fix). At end-of-run, emits copy-paste-ready `gh issue close ...` recommendations for any fixed Issues whose `reference_materials` carry a `github-issue` resolver — the skill never runs `gh issue close` itself. |
| `/quo-status` | Show the workflow stages and current progress across all hives. Useful for "where am I?" |

### Skills used internally by the workflow

These are dispatched automatically by the entry-point skills above. You don't need to call them directly during normal use, but they show up in `/agents` and `/help`, and they're documented here so the workflow's behavior is fully traceable.

| Skill | Invoked by | What it does |
|---|---|---|
| `/quo-write-prd` | `/quo-plan` (inline) | Author or revise a PRD as a `t1=Doc` child titled `PRD` under a Spec Bee in the Specs hive. Also runs solo for revisions: `/quo-write-prd <spec-bee-id>`. |
| `/quo-write-sdd` | `/quo-plan` (inline) | Author or revise an SDD as a `t1=Doc` child titled `SDD` under a Spec Bee in the Specs hive. Also runs solo for revisions: `/quo-write-sdd <spec-bee-id>`. |
| `/quo-spec-review` | `/quo-plan`, `/quo-write-prd`, `/quo-write-sdd` | Fresh-eyes review of a Spec Bee's PRD and SDD children for clarity, completeness, and internal consistency. Gates Spec Bee promotion. Also runs solo: `/quo-spec-review <spec-bee-id>` (optionally `--doc PRD` or `--doc SDD`). |
| `/quo-engineer-review` | `/quo-execute`, `/quo-fix-issue` | Review the Engineer's diff during the review cycle. Returns improvement work items for the orchestrator. |
| `/quo-test-writer-review` | `/quo-execute`, `/quo-fix-issue` | Review the Test Writer's test code during the review cycle. Returns improvement work items for the orchestrator. |
| `/quo-doc-writer-review` | `/quo-execute`, `/quo-fix-issue` | Review the Doc Writer's documentation during the review cycle. Checks README and architecture docs are updated with new functionality. Returns improvement work items for the orchestrator. |

## Status vocabulary

| Hive | Statuses |
|---|---|
| **Plans** (Plan Bees, Epics, Tasks, Subtasks) | `drafted` → `ready` → `in_progress` → `done` |
| **Issues** (issue tickets) | `open` → `done` |
| **Specs** (Spec Bees, Docs) | `drafted` → `ready` |

`drafted` = written but children (next tier down) not yet broken down.
`ready` = fully planned and ready for the next stage.
`in_progress` = actively being worked on.
`done` = completed.

The **Specs** hive (display name `Specs`, normalized name `specs`) holds Spec Bees, each containing per-feature spec docs as `t1=Doc` children. PRD and SDD are both `t1=Doc` children differentiated by ticket title (`PRD` vs `SDD`), not by tier. The hive's allowed resolver is `bees`, so a Plan Bee's `reference_materials` can point at a Spec Bee.

## Recommended session settings

**Subagent effort is pinned per role and is not affected by your session setting.** Every role quorum dispatches carries its own model and reasoning effort in the frontmatter of its `agents/<role>.md` file, and those pins override the session effort rather than inheriting from it — a role pinned at `high` runs at `high` whether you launched at `low` or at `xhigh`. Roles run at `high` minimum, with the two adversarial roles one tier higher. You don't need to think about it.

What your session setting *does* govern is the skill you invoke and the orchestration it runs. Recommendations below, covering every skill you invoke yourself — the three orchestrator-only reviewers (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) are omitted deliberately, since they never run as your session:

| Surface | Recommended |
|---|---|
| Orchestrator (`/quo-execute`, `/quo-fix-issue`) | Opus / `medium` — it delegates all implementation rather than producing work, and its context is the longest in the run |
| `/quo-plan`, `/quo-plan-from-specs`, `/quo-write-prd`, `/quo-write-sdd`, `/quo-spec-review`, `/quo-breakdown-epic` | Opus / `high` — tiny fan-out, maximal blast radius; errors here propagate into every Epic downstream |
| `/quo-setup` | Opus / `high` — a one-time run, but it writes the CLAUDE.md contract keys every other skill reads; a wrong path or a missed key surfaces as a hard-fail much later |
| `/quo-status`, `/quo-file-issue` | Opus / `medium` — read-only reporting and a short interactive capture; neither produces work that downstream skills build on, so there is nothing to gain from running hotter |

These are recommendations, not settings quorum applies for you. It could pin an effort level on a skill, but only as an *override* — that would drag you down to the recommended level when you had deliberately launched hotter, which is the opposite of what a recommendation should do. What these rows describe is a floor, so quorum names it and leaves the setting to you. Three skills check the floor for you and stay quiet unless you are below it: `/quo-execute` and `/quo-fix-issue` prompt once at run start if your session is below `medium`, and `/quo-breakdown-epic` if it is below `high`. Running hotter than the recommendation is never prompted on — it costs wall-clock, not quality. The rest of the second row — `/quo-plan`, `/quo-plan-from-specs`, `/quo-write-prd`, `/quo-write-sdd`, `/quo-spec-review` — carries no prompt at all, and neither do `/quo-setup`, `/quo-status`, or `/quo-file-issue`, so this table is the only place their recommendation is written down. To change the setting, run `/model` (or launch with `--effort <level>`); the effort ladder is `low` < `medium` < `high` < `xhigh` < `max`.

**On long runs, the orchestrators guard against ill-timed auto-compaction.** Because `/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` carry the longest context in a run, they check context usage at each Epic or Issue boundary and, when it has climbed close to the point where the harness would auto-compact mid-unit, stop and recommend you begin the next Epic or Issue in a fresh session rather than press on. This depends on a context-usage reading being published for your session; when none is — because no producer is configured for your environment — the same boundary check instead offers to wire one up inline via `/quo-setup --configure-gauge-producer`, or to proceed unguarded. See [The context-usage gauge file](#the-context-usage-gauge-file) for how that reading is published and [Enabling the gauge producer](#enabling-the-gauge-producer) for configuring the producer and the opt-out.

## Where docs live

If you opt into doc creation (recommended — see [Why this exists](#why-this-exists) above), the workflow creates and maintains:

- `docs/prd.md` — project-level Product Requirements. Grows as features ship.
- `docs/sdd.md` — project-level Software Design. Grows as features ship.

Per-feature PRD/SDD content is authored at plan time as `t1=Doc` children of a Spec Bee in the Specs hive (PRD and SDD as separate Docs), not appended to the cumulative project-level docs. After implementation lands, the post-implementation `doc-writer` agent dispatched by `/quo-execute` and `/quo-fix-issue` folds the shipped feature into the cumulative project PRD and SDD (paths configured under CLAUDE.md `## Documentation Locations`) by adding a new `### Feature: <title>` subsection under the cumulative `## Per-feature scope` (PRD) and `## Per-feature design` (SDD) headers — never overwriting earlier content. Old features stay documented; new features add to the record only once they ship.

The skills detect doc paths from CLAUDE.md `## Documentation Locations`, so you can override the defaults if your project uses a different structure (e.g., `specs/` instead of `docs/`).

### Where bundled helper scripts live

A few skills ship Python helpers (e.g., `detect_fast_path.py`, `scoped_marker_resolver.py`, and `context_gauge.py` — the context-usage gauge producer/reader, which also inspects and updates the operator's status-line settings and writes the opt-out marker) in a `scripts/` directory alongside each skill. Where that lands depends on how you got the skills: in a quorum checkout they sit under `skills/<skill-name>/scripts/`, and in an install they sit under `<skill-name>/scripts/` inside your skills directory (`~/.claude/skills/` for a global install, `<repo>/.claude/skills/` for a per-project one), because the install step copies the *contents* of `skills/` rather than the `skills/` directory itself. You don't need to configure absolute paths to them — each skill resolves its own bundled scripts at runtime from its own base directory, and a sibling skill that needs another skill's helper resolves it relative to that same base. An earlier revision wrote a `## Skill Paths` section into CLAUDE.md listing absolute paths to these helpers, but per-machine paths could not be committed safely across contributors, so the skills now self-resolve instead. If a skill invocation surfaces an error mentioning one of these scripts, look under `<skill-name>/scripts/` in your skills install directory, or under `skills/<skill-name>/scripts/` in a quorum checkout.

### Scratch files

Skills write transient scratch files (e.g., body files passed to `bees create-ticket --body-file` or `bees update-ticket --body-file`, and the private copy a Test Writer takes of a source file before temporarily perturbing it to confirm a test really fails without the fix) under a single well-known directory, which also holds the per-session [context-usage gauge file](#the-context-usage-gauge-file) when a producer is configured for your environment, and a persistent context-guard opt-out marker if you [chose to run unguarded](#enabling-the-gauge-producer):

- POSIX (macOS, Linux, WSL): `/tmp/.quorum/`
- Windows: `%TEMP%\.quorum\`

The directory is safe to delete between runs — skills recreate it on demand. Avoid deleting it *during* a run: alongside the regenerable body files, the skills keep a small run-state manifest there holding values that have no other home (the multi-Epic run mode you picked at run start, and the ordered Issue batch you gave `/quo-fix-issue`), and those are not recreated on demand. The persistent context-guard opt-out marker (`context-guard-opt-out`, i.e. `/tmp/.quorum/context-guard-opt-out` on POSIX, `%TEMP%\.quorum\context-guard-opt-out` on Windows) is a second resident nothing recreates: deleting it silently clears a standing "run unguarded" choice, so setup will offer that step again, re-arming the missing-reading stop the marker would otherwise suppress. The gauge file is the one resident that heals itself: nothing in the workflow recreates it either, but the status-line producer rewrites it on its next refresh, so deleting it leaves no reading published until that refresh restores one. You may also find a `context-usage-quo-setup-self-check.json` there — a synthetic self-check artifact left by a successful producer install that looks like a per-session gauge but belongs to no session; it is overwritten on each install and harmless to delete. Skills do not clean up after themselves, by design: the footprint is small (KBs per run, low-MB after heavy use), and leaving artifacts in place gives you something to inspect when a run crashes. POSIX systems clean `/tmp` on a days-to-reboot cadence anyway; Windows users can clear `%TEMP%\.quorum\` between runs.

### The context-usage gauge file

Claude Code reports how much of the model's context window is in use to your status-line command and nowhere else, so quorum republishes that reading to a small per-session file that the rest of a run can read back. The bundled helper `skills/quo-setup/scripts/context_gauge.py` writes it, and any environment can publish the same file from a producer of its own — the location, fields, and freshness semantics below are the whole contract.

**Location.** One file per session, in the same `.quorum` namespace as the scratch files above, resolved through the same platform temporary directory:

- POSIX (macOS, Linux, WSL): `/tmp/.quorum/context-usage-<session_id>.json`
- Windows: `%TEMP%\.quorum\context-usage-<session_id>.json`

`<session_id>` is the Claude Code session id.

**Required fields.** A top-level `session_id` string and a `context_window` object:

```json
{"session_id": "<id>", "context_window": {"used_percentage": 37}}
```

`context_window.used_percentage` is the field consumers read. The whole `context_window` object is written as received from the status-line payload, so any extra keys it carries are preserved rather than filtered out.

**Overwrite and freshness.** There is one file per session id, so concurrent quorum sessions never collide and never consume each other's reading. Every status-line refresh truncates and rewrites that file — it is a live gauge, not a log, so nothing appends and nothing rotates — and the workflow never deletes it. The file carries no timestamp field: freshness is judged from its modification time, so a producer that stops refreshing goes stale on its own. The bundled helper trusts a reading written within the last 20 minutes, so a producer you write yourself should refresh at least that often. (That 20-minute window mirrors the helper's `FRESHNESS_WINDOW_SECONDS` constant in [`quo-setup/scripts/context_gauge.py`](skills/quo-setup/scripts/context_gauge.py); if that constant is ever retuned, move this number in the same change so the two never drift.)

**Wrapping an existing status line.** `produce --wrap-command "<your existing status-line command>"` runs your own command with the same status-line payload and re-emits its output verbatim, so the gauge is added to an existing status line rather than replacing it. A payload the producer cannot parse — including an empty one, or one whose shape the harness has changed — never blanks that wrapped display: the wrapped command still runs, and its output is still what appears on the status line. Such a payload surfaces instead as the gauge quietly going unrefreshed, so it reads as `stale` (or `missing`) when you check it back with the reader snippet below.

**Restricted or pinned status-line environments.** In some setups a higher-precedence configuration source owns the status-line slot — a session launched against an explicit `--settings` file, organization settings delivered at sign-in, MDM policy, or managed-hook restrictions — so a status-line command written at the user level never takes effect. The contract above is published so those environments can satisfy it themselves. Any process that writes a conforming file keeps the mechanism working, with no change on the quorum side and nothing in the workflow needing to know which producer wrote it: the environment's own status-line command, a wrapper around it, or anything else that can see the session's context-usage payload. The obligations are: write to the published path above, keyed to the current session id; include the required fields above; always write `context_window` as an object — an empty one when the payload carries no reading, never `null`, since a present-but-non-object `context_window` is rejected as malformed rather than read as "no reading"; and refresh at least as often as the freshness window above.

To confirm a producer conforms, read the file back with the bundled helper's reader. Resolve the helper's location in your own install per [Where bundled helper scripts live](#where-bundled-helper-scripts-live), substituting for `<skills-dir>` below the directory that contains `quo-setup/` — your skills install directory (e.g. `~/.claude/skills`, or `<repo>/.claude/skills` for a per-project install) or the `skills/` directory of a quorum checkout — and substitute the current session's id for `<id>`, which Claude Code exposes in the `CLAUDE_CODE_SESSION_ID` environment variable:

```bash
# POSIX (bash / zsh):
python3 <skills-dir>/quo-setup/scripts/context_gauge.py read --session-id <id>
```

```powershell
# Windows (PowerShell):
python <skills-dir>\quo-setup\scripts\context_gauge.py read --session-id <id>
```

It prints exactly one value: an integer percentage when a fresh reading is present, or `no-reading`, `stale`, or `missing` when there is no fresh number to report. A nonconforming file is the exception — rather than printing one of those four values, the reader exits non-zero and describes the malformation on stderr, which is how you tell a broken producer from a merely quiet one.

Everything you need to publish and verify a conforming file is above. If you want the reasoning behind it, the deeper contract lives in [the contributor-facing contract section](docs/doc-writing-guide.md#the-context-gauge-file-contract) of the doc-writing guide — optional depth, aimed at contributors working on the mechanism itself.

### Enabling the gauge producer

**What it is.** Near the end of its walk-through, `/quo-setup` offers — optionally — to configure the producer that publishes the reading described in [The context-usage gauge file](#the-context-usage-gauge-file) above. It is a standalone offer: declining it changes nothing else about setup, and every other part of the workflow behaves the same either way.

**How to enable it.** There are three entry points. Running `/quo-setup` normally reaches the step as part of the walk-through. On a machine that is new to an already-set-up repo, the fast path offers it too — the status line is unconfigured there because that setting is per-machine and never committed, so a repo that is otherwise fully set up still has no producer wired in on a fresh machine. And the direct path `/quo-setup --configure-gauge-producer` runs only this step: it needs neither the bees CLI nor a configured repo, and skips the rest of setup.

**The choices.** The offer is a gate with three options: configure it, not now (the offer returns on a future setup run), and run unguarded (don't ask again). There is no separate "wrap it" choice — when a status line already exists, configuring wraps and preserves it rather than replacing it, and re-running never nests one wrapper inside another. For exactly what is preserved when a payload cannot be parsed, see the **Wrapping an existing status line.** note under [The context-usage gauge file](#the-context-usage-gauge-file) above.

**Activation is next-session.** Status-line configuration is picked up when a session starts, so treat the producer as active from the *next* session — do not assume the run in progress is guarded, since it began before the setting existed.

**Pinned or restricted environments.** A user-level settings write can be outranked — by a session launched against an explicit settings file, by organization settings delivered at sign-in, by MDM policy, or by managed-hook restrictions. Setup names the higher-precedence sources it can detect before it asks, and drops the "recommended" framing from its first option when one is present; it also warns that some such sources cannot be seen from disk at all. Where a user-level write cannot take effect, the route for the environment owner is to satisfy the published [file contract](#the-context-usage-gauge-file) directly with a producer of their own.

**Opting out.** Choosing "run unguarded — don't ask again" writes a persistent marker at `/tmp/.quorum/context-guard-opt-out` (POSIX) or `%TEMP%\.quorum\context-guard-opt-out` (Windows). It suppresses only the stop that would fire when no reading is being published; it never suppresses a genuine over-threshold stop when a reading *is* present. Removing that file re-enables the automatic offer. You do not have to delete it to change your mind, though: invoking `/quo-setup --configure-gauge-producer` re-offers the step even when the marker is present — an explicit request to configure is itself the change of mind, so only the automatic slow-path and fast-path offers are the ones the marker silences.

**Re-running repairs a stale configuration.** If a configured producer goes stale — its interpreter moved or was upgraded — re-running setup rewrites the configuration to match without re-asking; this is the one unprompted settings rewrite to expect. An existing opt-out marker suppresses even that silent repair. Accepting the step also exercises the newly-composed command once, which runs any wrapped command once.

## Coming soon: optional skills

The current 14 skills are the portable core — they work on any project, any language, any platform with no extra tooling beyond the bees CLI and Claude Code. Optional skills are planned for users who want more — these will likely require additional tooling per skill, clearly labeled:

- **Async-worktree session management** — spawn an isolated git-worktree session for a Plan Bee, work on it in the background, merge cleanly when done.
- **Multi-repo orchestration** — survey ready work across multiple repos and launch concurrent execution sessions.

Stack-specific helpers (changelog management, license attribution generation, etc.) and infrastructure-specific helpers (pastebins, cloud storage) are out of scope for the cross-language core but can live in companion repos.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow design rationale, intentional asymmetries between skills, anti-patterns, and skill conventions. Two principles you'll see referenced everywhere:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Don't hardcode language-specific commands or file paths in skill prose; use the CLAUDE.md `## Build Commands` and `## Documentation Locations` lookups instead. (See `quo-execute` and `quo-fix-issue` for examples of how to reference these.)
2. **Skills must work on POSIX and Windows.** Every shell snippet should be provided in OS-conditional blocks (POSIX bash + Windows PowerShell at minimum). Helper scripts should be Python or come in OS-paired implementations.

## License

MIT. See [LICENSE](LICENSE).

## Credits

Built on top of the [bees](https://github.com/gabemahoney/bees) ticket management system by Gabe Mahoney.
