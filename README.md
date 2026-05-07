# <img src="assets/header.png" alt="" width="48" valign="middle"> bees-workflow

A portable [Claude Code](https://claude.com/claude-code) skill set for running an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Works on any project, any language, any POSIX or Windows shell.

```
/bees-setup                  ← one-time per repo (safe to re-run)
       │
       ├──────────────────────────────────────────┐
       ▼                                          ▼
/bees-plan                            /bees-plan-from-specs
(planning from an idea)               (PRD + SDD already on disk)
       │                                          │
       ▼                                          │
Spec Bee  (Specs hive, top-level)                 │
  ├── PRD  (t1=Doc, via /bees-write-prd)          │
  └── SDD  (t1=Doc, via /bees-write-sdd)          │
       │                                          │
       │ /bees-spec-review (auto quality gate)    │
       │   gates Spec Bee drafted → ready         │
       │                                          │
       │ reference_materials                      │ reference_materials
       │   → Spec Bee (resolver: bees)            │   → on-disk PRD/SDD
       │                                          │     (resolver: file-path)
       ▼                                          ▼
          Plan Bee  (Plans hive, top-level)
                          │
                          ▼
              /bees-breakdown-epic    ← Epic → Tasks/Subtasks
                          │
                          ▼
              /bees-execute           ← do the work, with reviews
                          │
                          ▼
              /bees-file-issue + /bees-fix-issue
                          ↑
                   (anytime, for bugs/follow-ups)
```

The skills orchestrate work via Claude Code's ephemeral background subagents — no special setup is required beyond the bees CLI and Claude Code itself.

## Why this exists

[Apiary](https://github.com/gabemahoney/apiary), built by the bees creator, is the original bees skill set and remains a great fit for many projects. **bees-workflow is an alternative**, shaped by these priorities:

- **Cumulative project-level docs.** Project-level PRD and SDD (paths configured under CLAUDE.md `## Documentation Locations`) accumulate `### Feature:` subsections as features ship, and become the source of truth that agents (`bees-execute`, `bees-fix-issue`) read for spec-drift detection. The `bees-setup` skill can bootstrap baseline docs from an existing codebase via guided Q&A. Per-feature specs are authored as Spec Bee children at plan time and folded back into the cumulative project docs after implementation lands, by the post-implementation `doc-writer` agent dispatched by `/bees-execute` and `/bees-fix-issue`.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md, then read by skills at runtime — no skill-editing needed when you switch projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet that runs is provided as a labeled OS-conditional block; the bundled helper scripts (fast-path detector, scoped-marker parser) ship as cross-platform Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`. No translation layer, no insect-metaphor jargon to remember.
- **PRD/SDD-first or scope-first, your choice.** `/bees-plan` is the interactive entry point for an idea you haven't speced out — it authors per-feature PRD and SDD as `t1=Doc` children of a new Spec Bee in the Specs hive and links the Spec Bee from the resulting Plan Bee's `reference_materials` (no project-doc mutation at plan time). `/bees-plan-from-specs` is the express path when you already have a finalized **single-feature** PRD and SDD on disk; experienced users with finalized cumulative specs can also reach for `/bees-plan-from-specs --feature "<title>"` to scope one `### Feature:` subsection of the cumulative docs without going back through `/bees-plan`'s discovery loop. The single-feature scope follows the Plan Bee end-to-end — `/bees-breakdown-epic`, `/bees-execute`, and `/bees-fix-issue` all detect the scoping marker on the Plan Bee body and restrict spec-compare logic to the matching feature. Both entry points produce the same Plan Bee shape and feed the same downstream chain. Cumulative project-level PRD/SDD are updated after implementation by the `doc-writer` agent, not at plan time.
- **Idempotent.** Every skill that mutates project state (`bees-setup` especially) detects existing configuration and only prompts where something is missing or you ask to change it. Re-runs are safe.

If you want the lightweight, ephemeral-spec, async-team-spawning experience of Apiary, use Apiary. If you want persistent docs that grow with your project across many features and contributors, bees-workflow is built for that.

## Requirements

- **Claude Code** ([install](https://claude.com/claude-code))
- **bees CLI** (`pipx install bees-md`) — see [bees](https://github.com/gabemahoney/bees) for documentation. Requires Python 3.10+.
- **POSIX shell** (bash/zsh on macOS/Linux/WSL) **or PowerShell** (native Windows). Either works; every shell snippet in the skills is provided in both forms.

## Install

### Option A — global (recommended for single-user machines)

Copy the skills and subagent definitions into your user-level Claude Code directories so every repo can use them:

```bash
# POSIX (bash / zsh):
git clone https://github.com/jes5e/bees-workflow ~/projects/bees-workflow
cp -r ~/projects/bees-workflow/skills/* ~/.claude/skills/
mkdir -p ~/.claude/agents
cp -r ~/projects/bees-workflow/agents/* ~/.claude/agents/

# Windows (PowerShell):
git clone https://github.com/jes5e/bees-workflow $HOME\projects\bees-workflow
Copy-Item -Recurse $HOME\projects\bees-workflow\skills\* $HOME\.claude\skills\
New-Item -ItemType Directory -Force -Path "$HOME\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\bees-workflow\agents\* $HOME\.claude\agents\
```

### Option B — per-project install

If you want to try bees-workflow on one repo without affecting others, copy the skills and subagent definitions into that repo's `.claude/skills/` and `.claude/agents/`:

```bash
# POSIX:
cp -r ~/projects/bees-workflow/skills/* /path/to/your/repo/.claude/skills/
mkdir -p /path/to/your/repo/.claude/agents
cp -r ~/projects/bees-workflow/agents/* /path/to/your/repo/.claude/agents/

# Windows (PowerShell):
Copy-Item -Recurse $HOME\projects\bees-workflow\skills\* C:\path\to\your\repo\.claude\skills\
New-Item -ItemType Directory -Force -Path "C:\path\to\your\repo\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\bees-workflow\agents\* C:\path\to\your\repo\.claude\agents\
```

### After install

If Claude Code is already running when you copy the files, the new subagent types from `~/.claude/agents/` (Option A) or `<repo>/.claude/agents/` (Option B) won't be registered yet — custom subagents are loaded at session start. You have two options to register them:

- **Run `/agents` in the session** — opens Claude Code's agents UI and hot-reloads the registry. Faster than a full restart; preserves the current session.
- **Restart Claude Code** — quit and relaunch. Always works.

Either way, until one of these is done, the bees-execute / bees-fix-issue / bees-breakdown-epic skills will fail with `Agent type 'engineer' not found` (or similar).

In any repo where you want to use the workflow, run:

```
/bees-setup
```

It will colonize hives (Plans + Issues + Specs), write a `## Documentation Locations` and `## Build Commands` section to CLAUDE.md, and offer to bootstrap baseline PRD/SDD docs from your existing codebase. Safe to re-run if you skip a step and want to come back to it later.

### Upgrading from older bees-workflow versions

Earlier revisions of bees-workflow registered a custom egg resolver (`file_list_resolver.py`) and stored spec-doc pointers in a per-ticket `egg` field. The bees CLI has since replaced both with a built-in `file-path` resolver and a per-ticket `reference_materials` field; the workflow now uses those exclusively, and the custom resolver has been removed.

If you have existing tickets created under the old schema, run `bees update-config` once before using the upgraded skills:

```bash
bees update-config
```

The migration converts each ticket's old `egg` array into one `reference_materials` entry per file and clears the obsolete custom-resolver registration from `~/.bees/config.json`. New repos and machines that never ran an older version are unaffected.

If your repo was set up before the `Specs` hive existed, re-run `/bees-setup` — it detects the missing `Specs` hive, prompts for its path, and leaves your existing `Plans` and `Issues` hives untouched.

## The skills

| Skill | What it does |
|---|---|
| `/bees-setup` | One-time configuration: hives, CLAUDE.md sections, optional PRD/SDD bootstrap from existing codebase. Idempotent — safe to re-run. On a new machine in an already-set-up repo, `/bees-setup` detects the existing hive markers and offers to just re-register them, skipping the full walk-through. |
| `/bees-plan` | Interactive scope discovery for an idea, refactor, or feature without finalized specs. Authors per-feature PRD and SDD as `t1=Doc` children of a new Spec Bee in the Specs hive and links the Spec Bee from the Plan Bee's `reference_materials` — no project-doc mutation at plan time. Cumulative project-level PRD/SDD are updated after implementation by the `doc-writer` agent. Produces a Plan Bee with Epics. |
| `/bees-plan-from-specs` | Express path for when you already have a finalized PRD and SDD on disk. Default mode targets a **single-feature** PRD+SDD and hard-fails on PRDs **or SDDs** containing multiple `### Feature:` subsections. Pass `--feature "<title>"` to scope a single subsection inside a cumulative PRD+SDD — useful for re-planning one feature without going back through `/bees-plan`'s discovery loop. Produces a Plan Bee with Epics. |
| `/bees-write-prd` | Author or revise a PRD as a `t1=Doc` child titled `PRD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/bees-write-prd <spec-bee-id>`), or inline from `/bees-plan` via the Skill tool when initial specs are being authored. |
| `/bees-write-sdd` | Author or revise an SDD as a `t1=Doc` child titled `SDD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/bees-write-sdd <spec-bee-id>`), or inline from `/bees-plan` via the Skill tool when initial specs are being authored. |
| `/bees-breakdown-epic` | Decompose a single Epic into Tasks and Subtasks with the mandatory description template applied. Commits the new ticket files at end-of-skill (when the Plans hive lives in-repo) and presents a next-steps menu with per-option rationale. |
| `/bees-execute` | Execute a Plan Bee end-to-end — dispatch the ephemeral background subagents (Engineer, Test Writer, Doc Writer, PM, Code/Test/Doc Reviewer), walk every Epic in dependency order, commit per Task, review at Bee close. |
| `/bees-file-issue` | File a new issue ticket in the issues hive. Issues cover bugs, follow-ups, small features, tech debt — anything ticket-worthy that isn't planned upfront. Two invocation modes: (a) **in-conversation capture** — `/bees-file-issue` (interactive) or `/bees-file-issue <description>` produces an Issue whose body carries the full spec (Description / Current behavior / Expected behavior / Impact / Suggested fix); (b) **external-reference mode** — `/bees-file-issue --reference <url>` (or its `--from-github <url>` alias) produces a thin Issue (2-3 sentence summary in the body) whose `reference_materials` points at an external resource (GitHub Issue, Linear ticket, Slack archive, internal bug tracker URL, etc.) under one of three canonical resolver names (`github-issue` / `linear-issue` / `url`, picked by URL pattern); `/bees-fix-issue` fetches the upstream content via `WebFetch` when picking the Issue up. Symmetric with `/bees-plan-from-specs` on the planning side. |
| `/bees-fix-issue` | Fix one or more issue tickets. Single, list, or `all` modes. Dispatches the same ephemeral background subagents as `bees-execute` but at issue scope. |
| `/bees-status` | Show the workflow stages and current progress across all hives. Useful for "where am I?" |
| `/bees-code-review` | Perform code review of a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc review of a diff, worktree, files, or bees ticket. Returns a simple list of improvement work items. |
| `/bees-doc-review` | Review documentation completeness for a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc doc review of a diff, worktree, files, or bees ticket. Checks README and architecture docs are updated with new functionality. Returns structured list of documentation work items. |
| `/bees-test-review` | Review test files for quality, coverage, and correctness across a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc test review of a diff, worktree, files, or bees ticket. Returns a simple list of improvement work items. |
| `/bees-spec-review` | Fresh-eyes review of a Spec Bee's PRD and SDD `t1=Doc` children for clarity, completeness, and internal consistency. Primary use - invoked automatically by `/bees-plan` (after both writers complete, before Spec Bee promotion) and by `/bees-write-prd` / `/bees-write-sdd` (after the user-approval gate, before the PRD/SDD child's `drafted → ready` promotion) as a quality gate over the spec content. Standalone use - ad-hoc spec review of a Spec Bee, scoped optionally to one Doc child via `--doc PRD` or `--doc SDD`. Returns a simple list of improvement work items. |

The four reviewers (`bees-code-review`, `bees-doc-review`, `bees-test-review`, `bees-spec-review`) are dual-mode — primarily invoked by orchestrating skills (`/bees-execute` and `/bees-fix-issue` for the first three; `/bees-write-prd`, `/bees-write-sdd`, and `/bees-plan` for `bees-spec-review`) during their review cycles, but they also support standalone invocation if you want an ad-hoc review without the bees workflow.

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

Per-feature PRD/SDD content is authored at plan time as `t1=Doc` children of a Spec Bee in the Specs hive (PRD and SDD as separate Docs), not appended to the cumulative project-level docs. After implementation lands, the post-implementation `doc-writer` agent dispatched by `/bees-execute` and `/bees-fix-issue` folds the shipped feature into the cumulative project PRD and SDD (paths configured under CLAUDE.md `## Documentation Locations`) by adding a new `### Feature: <title>` subsection under the cumulative `## Per-feature scope` (PRD) and `## Per-feature design` (SDD) headers — never overwriting earlier content. Old features stay documented; new features add to the record only once they ship.

The skills detect doc paths from CLAUDE.md `## Documentation Locations`, so you can override the defaults if your project uses a different structure (e.g., `specs/` instead of `docs/`).

### Where bundled helper scripts live

A few skills ship Python helpers (e.g., `detect_fast_path.py`, `scoped_marker_resolver.py`) under `skills/<skill-name>/scripts/` inside the bees-workflow install. You don't need to configure absolute paths to them — each skill resolves its own bundled scripts at runtime from its own base directory, and a sibling skill that needs another skill's helper resolves it relative to that same base. An earlier revision wrote a `## Skill Paths` section into CLAUDE.md listing absolute paths to these helpers, but per-machine paths could not be committed safely across contributors, so the skills now self-resolve instead. If a skill invocation surfaces an error mentioning one of these scripts, look under `skills/<skill-name>/scripts/` in your bees-workflow checkout.

### Scratch files

Skills write transient scratch files (e.g., body files passed to `bees create-ticket --body-file` or `bees update-ticket --body-file`) under a single well-known directory:

- POSIX (macOS, Linux, WSL): `/tmp/.bees-workflow/`
- Windows: `%TEMP%\.bees-workflow\`

The directory is safe to delete anytime — skills recreate it on demand. Skills do not clean up after themselves, by design: the footprint is small (KBs per run, low-MB after heavy use), and leaving artifacts in place gives you something to inspect when a run crashes. POSIX systems clean `/tmp` on a days-to-reboot cadence anyway; Windows users can clear `%TEMP%\.bees-workflow\` whenever they want.

## Coming soon: optional skills

The current 14 skills are the portable core — they work on any project, any language, any platform with no extra tooling beyond the bees CLI and Claude Code. Optional skills are planned for users who want more — these will likely require additional tooling per skill, clearly labeled:

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
