# bees-workflow — Software Design

## Tech stack

- **Skill prose**: Markdown (`SKILL.md`) with YAML frontmatter (`name`, `description`). The body is the instructions Claude follows when the skill is invoked.
- **Helper scripts**: Python 3 (cross-platform). Four exist today — `bees-setup/scripts/file_list_resolver.py` (egg resolver), `bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection), `bees-execute/scripts/force_clean_team.py` (force-clean stuck Claude Code teams), and `bees-execute/scripts/check_agent_teams.py` (Agent Teams precondition check, sibling-resolved by `bees-fix-issue`).
- **External CLI**: [bees](https://github.com/gabemahoney/bees) (`bees-md` on pipx, Python 3.10+) for ticket management.
- **Runtime host**: [Claude Code](https://claude.com/claude-code) — skills are invoked via `/<skill>` slash commands. The execution skills (`bees-execute`, `bees-fix-issue`) require Claude Code's experimental Agent Teams feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`) for parallel Engineer/Test Writer/Doc Writer/PM execution; they spawn a team unconditionally and hard-fail without it. `/bees-setup` configures both the env var and the `teammateMode` display backend.

## Architecture overview

The repo ships eleven portable-core skills under `skills/<name>/`, each self-contained as a `SKILL.md` plus optional `scripts/`. Skills are loaded by Claude Code from either `~/.claude/skills/` (global install) or `<repo>/.claude/skills/` (per-project install). When a skill needs a bundled helper script (its own or a sibling's), it resolves the absolute path at runtime from the skill's own base directory — which Claude Code provides in the skill invocation header. No per-machine paths are persisted to CLAUDE.md or any other tracked file.

The workflow chain is linear with two entry points:

- `/bees-setup` — one-time per repo (idempotent re-runs)
- `/bees-plan` *or* `/bees-plan-from-specs` — produces a Plan Bee with Epic children
- `/bees-breakdown-epic` — decomposes one Epic into Tasks/Subtasks
- `/bees-execute` — walks every Epic, runs the team per Task, commits
- `/bees-file-issue` *and* `/bees-fix-issue` — anytime, for bugs/follow-ups

Three review skills (`bees-code-review`, `bees-doc-review`, `bees-test-review`) are dual-mode — primarily invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, with standalone invocation also supported for ad-hoc reviews outside the workflow.

The workflow uses two hives in the target repo: **Plans** (top-level, with t1/t2/t3 = Epic/Task/Subtask) and **Issues** (no children). Plan Bees may carry one or more on-disk source documents (PRD, SDD, etc.) in their `egg` field, resolved by the bundled `file_list_resolver.py`. When a Plan Bee has a null/empty `egg`, the **Plan Bee body itself becomes the authoritative spec** — downstream skills explicitly substitute the Bee body for the PRD/SDD in that mode.

## Key components

- **`skills/bees-setup/`** — one-time configuration: hives, two required CLAUDE.md sections (`Documentation Locations`, `Build Commands`), optional PRD/SDD bootstrap from existing codebase. Detects the new-machine case (on-disk hive markers present, the repo's scope not registered in `~/.bees/config.json`, CLAUDE.md already populated) via the bundled `detect_fast_path.py` helper and offers a fast path that re-registers hives from canonical defaults without touching CLAUDE.md.
- **`skills/bees-plan/`** — interactive scope discovery for an idea or feature without finalized specs. Produces a Plan Bee with Epic children.
- **`skills/bees-plan-from-specs/`** — express path for finalized PRD+SDD on disk. Same Plan Bee output as `/bees-plan`.
- **`skills/bees-breakdown-epic/`** — decompose one Epic into Tasks and Subtasks. The only skill where team members run in `mode: "plan"` (read-only researchers).
- **`skills/bees-execute/`** — execute a Plan Bee end-to-end. Spawns the implementation team, walks Epics in dependency order, commits per Task, reviews at Bee close.
- **`skills/bees-fix-issue/`** — fix one or more issue tickets. Single, list, or `all` modes. Same kind of team as `bees-execute` but at issue scope.
- **`skills/bees-file-issue/`** — file a new issue ticket (bug, follow-up, small feature, tech debt).
- **`skills/bees-status/`** — show workflow stages and current progress across all hives.
- **`skills/bees-code-review/`**, **`skills/bees-doc-review/`**, **`skills/bees-test-review/`** — dual-mode reviewers. Primary use: invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, with bees-specific loop-bounding prose for that path. Secondary use: standalone ad-hoc review of a diff or worktree.
- **`skills/bees-execute/scripts/force_clean_team.py`** — force-clean stuck Claude Code teams. Used as the `TeamDelete` recovery step.
- **`skills/bees-execute/scripts/check_agent_teams.py`** — Agent Teams precondition check. Reads `~/.claude/settings.json` `.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, falls back to the same-name environment variable, exits 0 silently when either is `"1"` and exits 1 with a stable error message otherwise. Run by the parent session at the top of `/bees-execute` and `/bees-fix-issue` (`bees-fix-issue` resolves it as a sibling skill's bundled script).
- **`skills/bees-setup/scripts/file_list_resolver.py`** — the egg resolver. Registered as each hive's `egg_resolver` so a Bee's `egg` field can point to one or more on-disk docs.
- **`skills/bees-setup/scripts/detect_fast_path.py`** — detect the new-machine fast-path scenario. Emits a JSON status payload (hive markers found, scope-already-registered check, CLAUDE.md sections populated, `fast_path_eligible` boolean) consumed by `/bees-setup`.

## Contract keys

The target repo's CLAUDE.md carries two sections that act as a string contract between skills. `bees-setup` writes them; every other skill reads them.

- `## Documentation Locations` — `Project requirements doc (PRD)`, `Internal architecture docs (SDD)`, `Customer-facing docs`, `Engineering best practices`, `Test writing guide`, `Test review guide`, `Doc writing guide`
- `## Build Commands` — `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`

`bees-execute` and `bees-fix-issue` hard-fail with `Run /bees-setup first.` if either section, or any required key inside them, is missing.

Bundled helper script paths (e.g., `force_clean_team.py`) are *not* part of the CLAUDE.md contract — each skill resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header. This keeps per-machine paths out of tracked files.

## Team orchestration in execution skills

Agent Teams is message-driven — a teammate that finishes processing a ping without a follow-up trigger idles silently. There is no "teammate idle" event. `bees-execute` and `bees-fix-issue` therefore prescribe team-lead choreography rather than peer-to-peer messaging:

- **Team-lead routes; workers do work.** When a teammate reports a state transition (Engineer subtask done, Test Writer Phase A done, all subtasks at `status=done`), the team-lead pings the next-rung teammate. Workers do not message each other directly — peer-to-peer coupling breaks down on Tasks/fixes that omit a role (research-only, test-only, doc-only).
- **State-aware dispatch.** Before sending any `task_assignment`, the team-lead re-reads the target ticket's current state via `bees execute-freeform-query` and skips the dispatch when the ticket is already `done`, or when the intended assignee is already on it `in_progress`. This prevents redundant pings and accidental rework caused by acting on stale memory.
- **Verbatim ticket-body quoting.** `task_assignment` messages embed the ticket body exactly as `bees show-ticket` returns it — no paraphrasing. Identifier names (function/flag/type names) are preserved literally so workers do not invent or mis-spell them downstream. Framing prose stays outside the quoted block.
- **Self-trigger as backstop.** Each worker role's Instructions include a top-of-turn precondition check; if the gating condition is met, the worker starts without waiting for a ping. This guards against missed routes.
- **`blocked_on` metadata as the worker→team-lead block signal.** When a worker cannot make progress, it sets `metadata.blocked_on: "<short description>"` on its TaskList task via TaskUpdate; the team-lead scans this signal at the top of each tick and either dispatches the unblocker or escalates to the human caller. The worker clears the field (sets it to `null`) once it resumes. This is the protocol — workers do not invent ad-hoc out-of-band messages.
- **Graduated escalation when teammates go silent.** Both execution skills carry a four-rung idle ladder (~10 min light nudge, ~20 min specific-deliverable nudge, ~30 min firm deadline, then proceed-and-log). The team-lead does not loop "Waiting" turns indefinitely.
- **Time-bounded review iteration.** In `bees-execute`, the PM short-circuits `/bees-code-review` and `/bees-doc-review` when a single invocation returns more than ~10 items or runs more than ~5 turns: triage to blocker-severity items only and defer the rest to the Task summary.

## Model assignment in execution skills

Hardcoded in `bees-execute` and `bees-fix-issue`:

- **Engineer, Test Writer, Code Reviewer, Test Reviewer**: always Opus. Not user-configurable.
- **Doc Writer, Product Manager, Doc Reviewer**: user picks Opus or Sonnet at the start of the run.

## External dependencies

- **bees CLI** (`bees-md` via pipx) — ticket management. Required.
- **Claude Code** — runtime host. Required.
- **Python 3** — helper scripts and JSON edits in skill prose. Required (already a dependency of bees).
- **tmux** — *only* required for the optional later-install skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`). The portable core does not need tmux.

## Deployment

- **Global install** (recommended for single-user machines): clone the repo, copy `skills/*` into `~/.claude/skills/`. POSIX `cp -r` or PowerShell `Copy-Item -Recurse`.
- **Per-project install**: copy `skills/*` into a single repo's `.claude/skills/`. Useful for trying the workflow on one repo without affecting others.
- **Live-edit symlink** (contributor pattern): symlink each `~/.claude/skills/<skill>` at `~/code/bees-workflow/skills/<skill>` so edits in the clone are immediately picked up by Claude Code. See CONTRIBUTING.md for the per-OS commands.

## Per-feature design

(Empty — `/bees-plan` invocations append `### Feature: <title>` subsections here as features are designed.)
