# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portable Claude Code **skill set** that runs an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets. The artifacts here are skills (markdown + a few Python helpers) — there is no application to build, no test suite, and no lint config for this repo itself. Your job, when editing here, is almost always to modify a `SKILL.md` or one of the helper scripts.

End-user docs (install, usage, the skill catalog, the workflow diagram) live in [README.md](README.md) — read it before changing user-facing behavior.

## Repo layout (only what isn't obvious)

- `skills/<name>/SKILL.md` — the skill prose. The frontmatter `name` and `description` are what Claude Code shows the user; the body is the instructions Claude follows when the skill is invoked.
- `skills/<name>/scripts/` — optional cross-platform Python helpers. Two exist today: `bees-setup/scripts/file_list_resolver.py` (the egg resolver) and `bees-execute/scripts/force_clean_team.py` (force-clean stuck Claude Code teams).

The full workflow chain — `bees-setup` → (`bees-plan` | `bees-plan-from-specs`) → `bees-breakdown-epic` → `bees-execute` → `bees-file-issue` / `bees-fix-issue` — is documented in the README; don't re-derive it from the skill files.

## The two non-negotiable design rules

These are the contributing principles called out in the README, and they should drive every change you make to a skill:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Never hardcode a language-specific command, file extension, or manifest filename in skill prose. Downstream skills look up project commands from CLAUDE.md (in the *target* repo, not this one) under fixed contract keys.
2. **Skills must work on POSIX and native Windows PowerShell.** Every shell snippet in a `SKILL.md` ships as labeled OS-conditional blocks (POSIX bash + Windows PowerShell at minimum; cmd.exe optional). Helper scripts should be Python (preferred) or come in OS-paired implementations. There is no bash-only fallback.

If you're tempted to write `cargo test` or `npm run lint` directly into a skill, stop — use the lookup-key pattern below instead.

## Contract keys that downstream skills depend on

These keys appear in the *target repo's* CLAUDE.md (not this one). `bees-setup` writes them; every other skill reads them. **Do not rename them in any skill** — they are a string contract.

`## Documentation Locations` bullet keys:
- `Project requirements doc (PRD)`
- `Internal architecture docs (SDD)`
- `Customer-facing docs`
- `Engineering best practices`
- `Test writing guide`
- `Test review guide`
- `Doc writing guide`

`## Build Commands` bullet keys:
- `Compile/type-check` (may be empty for interpreted languages without a static type-checker — the only key allowed to be empty)
- `Format`
- `Lint`
- `Narrow test`
- `Full test`

`bees-execute` and `bees-fix-issue` hard-fail with `Run /bees-setup first.` if either section, or any required key in `## Build Commands`, is missing from the target repo's CLAUDE.md. Preserve that precondition behavior in any edit to those skills.

## Hives and status vocabulary

The workflow uses two hives in the target repo:

- **Plans** (top-level — *not* nested in an Ideas hive). Tier ladder: t1 = Epic, t2 = Task, t3 = Subtask. Statuses: `drafted` → `ready` → `in_progress` → `done`.
- **Issues**. No children. Statuses: `open` → `done`.

When a Plan Bee is authored via `/bees-plan` for a feature with no separate PRD/SDD, the Bee's `egg` is null/empty and the **Plan Bee body itself becomes the authoritative spec**. Several skills (`bees-execute`'s PM role, `bees-breakdown-epic`) explicitly substitute "the Plan Bee body" for "the PRD/SDD" in that case — keep the substitution prose intact when editing those skills.

## Egg resolver

`skills/bees-setup/scripts/file_list_resolver.py` is the egg resolver bundled with the skills. Hives in the target repo are colonized with this script's absolute path as their `egg_resolver`, so a Bee's `egg` field can point to one or more on-disk docs (PRD, SDD, etc.). If you change the resolver's contract (input/output shape), `bees-setup` must also be updated to migrate existing hive configs in `~/.bees/config.json`.

## Agent Teams

`bees-execute` and `bees-fix-issue` use Claude Code's experimental **Agent Teams** feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`) to run Engineer / Test Writer / Doc Writer / PM concurrently. The skills detect at runtime and fall back to single-agent execution when it's off — so any edit to those skills must keep both code paths working, not just the Teams-enabled one. Agent naming inside a team uses task-scoped suffixes (e.g., `engineer-xb`, `pm-xb`) to avoid collision with not-yet-shut-down agents from the previous Task; reuse the same scheme when extending team logic.

## Model assignment in execution skills

Hardcoded in `bees-execute` and `bees-fix-issue`:
- **Engineer, Test Writer, Code Reviewer, Test Reviewer**: always Opus. Not user-configurable.
- **Doc Writer, Product Manager, Doc Reviewer**: user picks Opus or Sonnet at the start of the run.

Don't change these assignments without a concrete reason — they're load-bearing for output quality and are referenced by users in their workflows.

## When editing skills

- The README's skill table is the single source of truth for the user-visible skill catalog. If you add, remove, or rename a skill, update README.md to match.
- The `description` field in a skill's frontmatter is what Claude Code uses to decide whether to invoke the skill. Keep it precise — vague descriptions cause mis-invocation.
- Don't introduce a tmux dependency in any of the 11 portable-core skills. Tmux-dependent skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and are mentioned only as optional later-installs.
- Avoid adding stack-specific helpers (changelog tooling, license attribution, etc.) to the core — the README declares those out of scope and routes users to companion repos.
