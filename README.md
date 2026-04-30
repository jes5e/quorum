# <img src="assets/header.png" alt="" width="48" valign="middle"> bees-workflow

A portable [Claude Code](https://claude.com/claude-code) skill set for running an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Works on any project, any language, any POSIX or Windows shell, with no per-project skill-editing.

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
- **PRD/SDD-first or scope-first, your choice.** `/bees-plan` is the interactive entry point for an idea you haven't speced out; `/bees-plan-from-specs` is the express path when you already have a PRD and SDD on disk. Both produce the same Plan Bee shape and feed the same downstream chain.
- **Idempotent.** Every skill that mutates project state (`bees-setup` especially) detects existing configuration and only prompts where something is missing or you ask to change it. Re-runs are safe.

If you want the lightweight, ephemeral-spec, async-team-spawning experience of Apiary, use Apiary. If you want persistent docs that grow with your project across many features and contributors, bees-workflow is built for that.

## Requirements

- **Claude Code** ([install](https://claude.com/claude-code))
- **bees CLI** (`pipx install bees-md`) — see [bees](https://github.com/gabemahoney/bees) for documentation. Requires Python 3.10+.
- **POSIX shell** (bash/zsh on macOS/Linux/WSL) **or PowerShell** (native Windows). Either works; every shell snippet in the skills is provided in both forms.

## Strongly recommended: enable Agent Teams

`bees-execute` and `bees-fix-issue` get a major speedup when Claude Code's **Agent Teams** feature is enabled — instead of running Engineer → Test Writer → Doc Writer → PM in sequence, the team works concurrently on each Task. The skills detect whether Agent Teams is available at runtime and gracefully fall back to single-agent execution when it isn't, so the workflow works either way; with it enabled, it's noticeably faster and more parallel.

To enable, set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` to `"1"` in your Claude Code user-settings file:
- POSIX: `~/.claude/settings.json`
- Windows: `%USERPROFILE%\.claude\settings.json`

`/bees-setup` checks this for you on first run and offers to enable it if it isn't. You can also enable it manually any time.

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
| `/bees-setup` | One-time configuration: hives, CLAUDE.md sections, optional PRD/SDD bootstrap from existing codebase. Idempotent — safe to re-run. |
| `/bees-plan` | Interactive scope discovery for an idea, refactor, or feature without finalized specs. Produces a Plan Bee with Epics. |
| `/bees-plan-from-specs` | Express path for when you already have a finalized PRD and SDD on disk. Produces a Plan Bee with Epics. |
| `/bees-breakdown-epic` | Decompose a single Epic into Tasks and Subtasks with the mandatory description template applied. |
| `/bees-execute` | Execute a Plan Bee end-to-end — spawn the implementation team, walk every Epic in dependency order, commit per Task, review at Bee close. |
| `/bees-file-issue` | File a new issue ticket in the issues hive. Issues cover bugs, follow-ups, small features, tech debt — anything ticket-worthy that isn't planned upfront. |
| `/bees-fix-issue` | Fix one or more issue tickets. Single, list, or `all` modes. Spawns the same kind of team as `bees-execute` but at issue scope. |
| `/bees-status` | Show the workflow stages and current progress across all hives. Useful for "where am I?" |
| `/code-review` | Review changed files for substance — security, correctness, architecture, dead code. Returns a list of work items. |
| `/doc-review` | Review documentation completeness after changes land. Returns a list of work items. |
| `/test-review` | Review test files for quality, coverage, and bloat. Returns a list of work items. |

The three reviewers (`code-review`, `doc-review`, `test-review`) are general-purpose and don't depend on the bees workflow — useful standalone too.

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

Issues and PRs welcome. Two principles to keep in mind:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Don't hardcode language-specific commands or file paths in skill prose; use the CLAUDE.md `## Build Commands` and `## Documentation Locations` lookups instead. (See `bees-execute` and `bees-fix-issue` for examples of how to reference these.)
2. **Skills must work on POSIX and Windows.** Every shell snippet should be provided in OS-conditional blocks (POSIX bash + Windows PowerShell at minimum). Helper scripts should be Python or come in OS-paired implementations.

## License

MIT. See [LICENSE](LICENSE).

## Credits

Built on top of the [bees](https://github.com/gabemahoney/bees) ticket management system by Gabe Mahoney. The original [Apiary](https://github.com/gabemahoney/apiary) skill set inspired this one and remains a great alternative — bees-workflow exists alongside it, not as a replacement.
