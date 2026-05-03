# <img src="assets/header.png" alt="" width="48" valign="middle"> bees-workflow

A portable [Claude Code](https://claude.com/claude-code) skill set for running an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Works on any project, any language, any POSIX or Windows shell.

```
/bees-setup           ← one-time per repo (safe to re-run)
       │
       ├── /bees-plan              ← planning from an idea
       │       OR
       └── /bees-plan-from-specs   ← planning from a finalized PRD + SDD
                              │
                              ▼
                    /bees-breakdown-epic     ← Epic → Tasks/Subtasks
                              │
                              ▼
                       /bees-execute         ← do the work, with reviews
                              │
                              ▼
                    /bees-file-issue + /bees-fix-issue
                              ↑
                       (anytime, for bugs/follow-ups)
```

## Why this exists

[Apiary](https://github.com/gabemahoney/apiary), built by the bees creator, is the original bees skill set and remains a great fit for many projects. **bees-workflow is an alternative**, shaped by these priorities:

- **Cumulative project-level docs.** PRD/SDD live as files in `docs/`, accumulate sections as features are planned, and become the source of truth that agents (`bees-execute`, `bees-fix-issue`) read for spec-drift detection. The `bees-setup` skill can bootstrap baseline docs from an existing codebase via guided Q&A; subsequent `bees-plan` invocations extend them rather than overwrite.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md, then read by skills at runtime — no skill-editing needed when you switch projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet that runs is provided as a labeled OS-conditional block; the one helper script that does filesystem cleanup ships as cross-platform Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`. No translation layer, no insect-metaphor jargon to remember.
- **PRD/SDD-first or scope-first, your choice.** `/bees-plan` is the interactive entry point for an idea you haven't speced out, and is also the right path when your cumulative PRD/SDD already describe one or more prior features (it appends a new `### Feature:` subsection scoped to the new one). `/bees-plan-from-specs` is the express path when you already have a finalized **single-feature** PRD and SDD on disk; experienced users with finalized cumulative specs can also reach for `/bees-plan-from-specs --feature "<title>"` to re-plan one subsection without going back through `/bees-plan`'s discovery loop. The single-feature scope follows the Plan Bee end-to-end — `/bees-breakdown-epic`, `/bees-execute`, and `/bees-fix-issue` all detect the scoping marker on the Plan Bee body and restrict spec-compare logic to the matching `### Feature: <title>` subsection of the cumulative docs. Both entry points produce the same Plan Bee shape and feed the same downstream chain.
- **Idempotent.** Every skill that mutates project state (`bees-setup` especially) detects existing configuration and only prompts where something is missing or you ask to change it. Re-runs are safe.

If you want the lightweight, ephemeral-spec, async-team-spawning experience of Apiary, use Apiary. If you want persistent docs that grow with your project across many features and contributors, bees-workflow is built for that.

## Requirements

- **Claude Code** ([install](https://claude.com/claude-code))
- **bees CLI** (`pipx install bees-md`) — see [bees](https://github.com/gabemahoney/bees) for documentation. Requires Python 3.10+.
- **POSIX shell** (bash/zsh on macOS/Linux/WSL) **or PowerShell** (native Windows). Either works; every shell snippet in the skills is provided in both forms.

## Required: enable Agent Teams

`bees-execute` and `bees-fix-issue` use Claude Code's **Agent Teams** feature to run Engineer / Test Writer / Doc Writer / PM concurrently against each Task. Both skills spawn a team unconditionally — without Agent Teams enabled, neither can proceed.

`/bees-setup` configures this for you. It checks `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` in your Claude Code user-settings file (`~/.claude/settings.json` on POSIX, `%USERPROFILE%\.claude\settings.json` on Windows) and offers to set it to `"1"` if it isn't. Re-run `/bees-setup` any time you want to flip it on.

## Display backend

Agent Teams renders concurrent agent activity through one of three `teammateMode` values in `~/.claude/settings.json`:

- `"in-process"` — inline status panel inside the same Claude Code session. No terminal multiplexer required, no setup prompts, works on every terminal. **bees-workflow recommends this** for smooth onboarding.
- `"tmux"` — split-pane mode. Each teammate runs in its own pane via `tmux` (Linux, Terminal.app) or `it2` (iTerm2). Requires the relevant multiplexer to be installed and, on iTerm2, the Python API enabled. Unsupported in VS Code's integrated terminal, Windows Terminal, and Ghostty.
- `"auto"` — Claude Code's default. Picks split-pane on terminals it recognizes as supporting it, otherwise falls back to in-process.

`/bees-setup` configures this for you. If `teammateMode` is unset or `"auto"`, you'll be offered the choice with `"in-process"` as the recommended default.

**Why we don't recommend `"auto"`.** On macOS + iTerm2, the first team spawn under `"auto"` triggers an "iTerm2 Split Pane Setup" prompt. Picking Cancel aborts the team spawn entirely (returning `Teammate spawn cancelled - iTerm2 setup required`) — it does *not* simply decline a visual upgrade, and the calling skill stalls with no recovery. An upstream [Claude Code verification bug](https://github.com/anthropics/claude-code/issues/27413) compounds the problem: the prompt may re-appear even after `it2` is installed. `"in-process"` sidesteps both.

## Install

### Option A — global (recommended for single-user machines)

Copy the skills into your user-level Claude Code skills directory so every repo can use them:

```bash
# POSIX (bash / zsh):
git clone https://github.com/jes5e/bees-workflow ~/projects/bees-workflow
cp -r ~/projects/bees-workflow/skills/* ~/.claude/skills/

# Windows (PowerShell):
git clone https://github.com/jes5e/bees-workflow $HOME\projects\bees-workflow
Copy-Item -Recurse $HOME\projects\bees-workflow\skills\* $HOME\.claude\skills\
```

### Option B — per-project install

If you want to try bees-workflow on one repo without affecting others, copy the skills into that repo's `.claude/skills/`:

```bash
# POSIX:
cp -r ~/projects/bees-workflow/skills/* /path/to/your/repo/.claude/skills/

# Windows (PowerShell):
Copy-Item -Recurse $HOME\projects\bees-workflow\skills\* C:\path\to\your\repo\.claude\skills\
```

### After install

In any repo where you want to use the workflow, run:

```
/bees-setup
```

It will colonize hives (Plans + Issues), write a `## Documentation Locations` and `## Build Commands` section to CLAUDE.md, and offer to bootstrap baseline PRD/SDD docs from your existing codebase. Safe to re-run if you skip a step and want to come back to it later.

## The skills

| Skill | What it does |
|---|---|
| `/bees-setup` | One-time configuration: hives, CLAUDE.md sections, Agent Teams + display backend, optional PRD/SDD bootstrap from existing codebase. Idempotent — safe to re-run. On a new machine in an already-set-up repo, `/bees-setup` detects the existing hive markers and offers to just re-register them, skipping the full walk-through. |
| `/bees-plan` | Interactive scope discovery for an idea, refactor, or feature without finalized specs. Also the right entry point when your cumulative PRD/SDD already describe one or more prior features — appends a new `### Feature:` subsection scoped to the new one. Produces a Plan Bee with Epics. |
| `/bees-plan-from-specs` | Express path for when you already have a finalized PRD and SDD on disk. Default mode targets a **single-feature** PRD+SDD and hard-fails on PRDs **or SDDs** containing multiple `### Feature:` subsections. Pass `--feature "<title>"` to scope a single subsection inside a cumulative PRD+SDD — useful for re-planning one feature without going back through `/bees-plan`'s discovery loop. Produces a Plan Bee with Epics. |
| `/bees-breakdown-epic` | Decompose a single Epic into Tasks and Subtasks with the mandatory description template applied. |
| `/bees-execute` | Execute a Plan Bee end-to-end — spawn the implementation team, walk every Epic in dependency order, commit per Task, review at Bee close. |
| `/bees-file-issue` | File a new issue ticket in the issues hive. Issues cover bugs, follow-ups, small features, tech debt — anything ticket-worthy that isn't planned upfront. |
| `/bees-fix-issue` | Fix one or more issue tickets. Single, list, or `all` modes. Spawns the same kind of team as `bees-execute` but at issue scope. |
| `/bees-status` | Show the workflow stages and current progress across all hives. Useful for "where am I?" |
| `/bees-code-review` | Perform code review of a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc review of a diff, worktree, files, or bees ticket. Returns a simple list of improvement work items. |
| `/bees-doc-review` | Review documentation completeness for a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc doc review of a diff, worktree, files, or bees ticket. Checks README and architecture docs are updated with new functionality. Returns structured list of documentation work items. |
| `/bees-test-review` | Review test files for quality, coverage, and correctness across a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc test review of a diff, worktree, files, or bees ticket. Returns a simple list of improvement work items. |

The three reviewers (`bees-code-review`, `bees-doc-review`, `bees-test-review`) are dual-mode — primarily invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, but they also support standalone invocation if you want an ad-hoc review without the bees workflow.

## Status vocabulary

| Hive | Statuses |
|---|---|
| **Plans** (Plan Bees, Epics, Tasks, Subtasks) | `drafted` → `ready` → `in_progress` → `done` |
| **Issues** (issue tickets) | `open` → `done` |

`drafted` = written but children (next tier down) not yet broken down.
`ready` = fully planned and ready for the next stage.
`in_progress` = actively being worked on.
`done` = completed.

## Where docs live

If you opt into doc creation (recommended — see [Why this exists](#why-this-exists) above), the workflow creates and maintains:

- `docs/prd.md` — project-level Product Requirements. Grows as features are planned.
- `docs/sdd.md` — project-level Software Design. Grows as features are designed.

Each `bees-plan` invocation that produces docs adds a new `### Feature: <title>` subsection under the cumulative `## Per-feature scope` (PRD) and `## Per-feature design` (SDD) headers — never overwrites earlier content. Old features stay documented; new features add to the record.

The skills detect doc paths from CLAUDE.md `## Documentation Locations`, so you can override the defaults if your project uses a different structure (e.g., `specs/` instead of `docs/`).

## Coming soon: optional skills

The current 11 skills are the portable core — they work on any project, any language, any platform with no extra tooling beyond the bees CLI and Claude Code. Optional skills are planned for users who want more — these will likely require additional tooling per skill, clearly labeled:

- **Async-worktree session management** — spawn an isolated git-worktree session for a Plan Bee, work on it in the background, merge cleanly when done.
- **Multi-repo orchestration** — survey ready work across multiple repos and launch concurrent execution sessions.

If you need these capabilities today, the [Apiary](https://github.com/gabemahoney/apiary) project includes them and is fully compatible with the same `bees` CLI underneath.

Stack-specific helpers (changelog management, license attribution generation, etc.) and infrastructure-specific helpers (pastebins, cloud storage) are out of scope for the cross-language core but can live in companion repos.

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow design rationale, intentional asymmetries between skills, anti-patterns, and skill conventions. Two principles you'll see referenced everywhere:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Don't hardcode language-specific commands or file paths in skill prose; use the CLAUDE.md `## Build Commands` and `## Documentation Locations` lookups instead. (See `bees-execute` and `bees-fix-issue` for examples of how to reference these.)
2. **Skills must work on POSIX and Windows.** Every shell snippet should be provided in OS-conditional blocks (POSIX bash + Windows PowerShell at minimum). Helper scripts should be Python or come in OS-paired implementations.

## License

MIT. See [LICENSE](LICENSE).

## Credits

Built on top of the [bees](https://github.com/gabemahoney/bees) ticket management system by Gabe Mahoney. The original [Apiary](https://github.com/gabemahoney/apiary) skill set inspired this one and remains a great alternative — bees-workflow exists alongside it, not as a replacement.
