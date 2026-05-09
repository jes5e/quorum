# <img src="assets/header.png" alt="" width="48" valign="middle"> quorum

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

It will colonize hives (Plans + Issues + Specs), write a `## Documentation Locations` and `## Build Commands` section to CLAUDE.md, and offer to bootstrap baseline PRD/SDD docs from your existing codebase. Safe to re-run if you skip a step and want to come back to it later.

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
| `/quo-setup` | One-time configuration: hives, CLAUDE.md sections, optional PRD/SDD bootstrap from existing codebase. Idempotent — safe to re-run. On a new machine in an already-set-up repo, `/quo-setup` detects the existing hive markers and offers to just re-register them, skipping the full walk-through. |
| `/quo-plan` | Interactive scope discovery for an idea, refactor, or feature without finalized specs. Authors per-feature PRD and SDD as `t1=Doc` children of a new Spec Bee in the Specs hive and links the Spec Bee from the Plan Bee's `reference_materials` — no project-doc mutation at plan time. Cumulative project-level PRD/SDD are updated after implementation by the `doc-writer` agent. Produces a Plan Bee with Epics. |
| `/quo-plan-from-specs` | Express path for when you already have a finalized PRD and SDD on disk. Default mode targets a **single-feature** PRD+SDD and hard-fails on PRDs **or SDDs** containing multiple `### Feature:` subsections. Pass `--feature "<title>"` to scope a single subsection inside a cumulative PRD+SDD — useful for re-planning one feature without going back through `/quo-plan`'s discovery loop. Produces a Plan Bee with Epics. |
| `/quo-breakdown-epic` | Decompose a single Epic into Tasks and Subtasks with the mandatory description template applied. Commits the new ticket files at end-of-skill (when the Plans hive lives in-repo) and presents a next-steps menu with per-option rationale. |
| `/quo-execute` | Execute a Plan Bee end-to-end — dispatch the ephemeral background subagents (Engineer, Test Writer, Doc Writer, PM, Code/Test/Doc Reviewer), walk every Epic in dependency order, commit per Task, review at Bee close. |
| `/quo-file-issue` | File a new issue ticket in the issues hive. Issues cover bugs, follow-ups, small features, tech debt — anything ticket-worthy that isn't planned upfront. Three invocation forms: (a) **in-conversation capture** — `/quo-file-issue` (interactive) or `/quo-file-issue <description>` produces an Issue whose body carries the full spec (Description / Current behavior / Expected behavior / Impact / Suggested fix); (b) **bare URL** — `/quo-file-issue <url>` auto-detects URL-shaped positional arguments (`^https?://`) and routes to the same external-reference branch as the flag forms — no flag required; (c) **external-reference flag forms** — `/quo-file-issue --reference <url>` (or its `--from-github <url>` alias) accepted as silent no-op aliases for backward compat. Both URL paths produce a thin Issue (2-3 sentence summary in the body) whose `reference_materials` points at an external resource (GitHub Issue, Linear ticket, Slack archive, internal bug tracker URL, etc.) under one of three canonical resolver names (`github-issue` / `linear-issue` / `url`, picked by the same URL-pattern resolver-name heuristic); `/quo-fix-issue` fetches the upstream content via `WebFetch` when picking the Issue up. Before filing, the skill dedupes by `reference_materials.value` against open Issues and surfaces `Use existing` / `File new` / `Cancel` on a match. Symmetric with `/quo-plan-from-specs` on the planning side. |
| `/quo-fix-issue` | Fix one or more issue tickets. Argument shapes: interactive (no args), `all`, single bees ID, list of bees IDs, single `<url>`, or a mixed `<id>` + `<url>` list. URL tokens (`^https?://`) trigger file-then-fix routing through `/quo-file-issue` (same dedupe and `WebFetch` fallback apply) and the resolved ticket IDs substitute the URLs *in place* in the working list, preserving the user-supplied prerequisite ordering. Dispatches the same ephemeral background subagents as `quo-execute` but at issue scope. At end-of-run, emits copy-paste-ready `gh issue close ...` recommendations for any fixed Issues whose `reference_materials` carry a `github-issue` resolver — the skill never runs `gh issue close` itself. |
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

## Where docs live

If you opt into doc creation (recommended — see [Why this exists](#why-this-exists) above), the workflow creates and maintains:

- `docs/prd.md` — project-level Product Requirements. Grows as features ship.
- `docs/sdd.md` — project-level Software Design. Grows as features ship.

Per-feature PRD/SDD content is authored at plan time as `t1=Doc` children of a Spec Bee in the Specs hive (PRD and SDD as separate Docs), not appended to the cumulative project-level docs. After implementation lands, the post-implementation `doc-writer` agent dispatched by `/quo-execute` and `/quo-fix-issue` folds the shipped feature into the cumulative project PRD and SDD (paths configured under CLAUDE.md `## Documentation Locations`) by adding a new `### Feature: <title>` subsection under the cumulative `## Per-feature scope` (PRD) and `## Per-feature design` (SDD) headers — never overwriting earlier content. Old features stay documented; new features add to the record only once they ship.

The skills detect doc paths from CLAUDE.md `## Documentation Locations`, so you can override the defaults if your project uses a different structure (e.g., `specs/` instead of `docs/`).

### Where bundled helper scripts live

A few skills ship Python helpers (e.g., `detect_fast_path.py`, `scoped_marker_resolver.py`) under `skills/<skill-name>/scripts/` inside the quorum install. You don't need to configure absolute paths to them — each skill resolves its own bundled scripts at runtime from its own base directory, and a sibling skill that needs another skill's helper resolves it relative to that same base. An earlier revision wrote a `## Skill Paths` section into CLAUDE.md listing absolute paths to these helpers, but per-machine paths could not be committed safely across contributors, so the skills now self-resolve instead. If a skill invocation surfaces an error mentioning one of these scripts, look under `skills/<skill-name>/scripts/` in your quorum checkout.

### Scratch files

Skills write transient scratch files (e.g., body files passed to `bees create-ticket --body-file` or `bees update-ticket --body-file`) under a single well-known directory:

- POSIX (macOS, Linux, WSL): `/tmp/.quorum/`
- Windows: `%TEMP%\.quorum\`

The directory is safe to delete anytime — skills recreate it on demand. Skills do not clean up after themselves, by design: the footprint is small (KBs per run, low-MB after heavy use), and leaving artifacts in place gives you something to inspect when a run crashes. POSIX systems clean `/tmp` on a days-to-reboot cadence anyway; Windows users can clear `%TEMP%\.quorum\` whenever they want.

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
