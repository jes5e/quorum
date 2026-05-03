# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portable Claude Code **skill set** that runs an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets. The artifacts here are skills (markdown + a few Python helpers) — there is no application to build, no test suite, and no lint config for this repo itself. Your job, when editing here, is almost always to modify a `SKILL.md` or one of the helper scripts.

End-user docs (install, usage, the skill catalog, the workflow diagram) live in [README.md](README.md) — read it before changing user-facing behavior.

## Repo layout (only what isn't obvious)

- `skills/<name>/SKILL.md` — the skill prose. The frontmatter `name` and `description` are what Claude Code shows the user; the body is the instructions Claude follows when the skill is invoked.
- `skills/<name>/scripts/` — optional cross-platform Python helpers. Four exist today: `bees-setup/scripts/file_list_resolver.py` (the egg resolver), `bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection), `bees-execute/scripts/force_clean_team.py` (force-clean stuck Claude Code teams), and `bees-execute/scripts/check_agent_teams.py` (Agent Teams precondition check, sibling-resolved by `bees-fix-issue`).

The full workflow chain — `bees-setup` → (`bees-plan` | `bees-plan-from-specs`) → `bees-breakdown-epic` → `bees-execute` → `bees-file-issue` / `bees-fix-issue` — is documented in the README; don't re-derive it from the skill files.

## The three non-negotiable design rules

These are the contributing principles called out in the README, and they should drive every change you make to a skill:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Never hardcode a language-specific command, file extension, or manifest filename in skill prose. Downstream skills look up project commands from CLAUDE.md (in the *target* repo, not this one) under fixed contract keys.
2. **Skills must work on POSIX and native Windows PowerShell.** Every shell snippet in a `SKILL.md` ships as labeled OS-conditional blocks (POSIX bash + Windows PowerShell at minimum; cmd.exe optional). Helper scripts should be Python (preferred) or come in OS-paired implementations. There is no bash-only fallback.
3. **Skill prose must be project-neutral.** A `SKILL.md` (or any helper script) must not reference *this* repo's paths, ticket IDs, internal workflow specifics, or anything that wouldn't make sense in a different project that installs the skills. Project-specific guidance for downstream users lives in the *target repo's* `CLAUDE.md`, which the skills read at runtime — never baked into the skills themselves. (This file you're reading now is *this* repo's `CLAUDE.md` — guidance here governs work done **on** the skills, but does not get baked **into** them.)

If you're tempted to write `cargo test` or `npm run lint` directly into a skill, stop — use the lookup-key pattern below instead.

## Bash etiquette in this repo

Every Bash tool call in this repo must be a **single literal command** — one binary plus its arguments, nothing else. This applies to *every* Claude instance — team-leads, spawned workers, reviewers, ad-hoc invocations. The `Shell-command etiquette` bullet inside the execution-skill worker prompts (b.6k2 / b.aic) only covers spawned workers; this section covers everyone else.

**Forbidden shapes** (each one trips a different Claude Code matcher and re-prompts the user even on previously-approved repos):

- Compound chains: `cmd1 && cmd2`, `cmd1 || cmd2`, `cmd1 ; cmd2`
- Pipes between commands: `cmd1 | cmd2` (use first-class `Grep` / `Read` tools, or pass match-limit flags like `grep -m N`)
- Redirects mid-chain: `echo X > file && cmd` (use the `Write` tool to create files)
- Diagnostic tails: `; echo exit=$?`, `&& echo done` (the Bash tool already reports exit status)
- Shell variables and expansion: `$VAR`, `${VAR:-default}`, `$?`, `$(...)`, backticks
- Multi-line `-c` or inline heredocs: `python3 -c '<line1>\n<line2>'`
- `unset` / `export` mid-chain

**Required shapes:**

- One Bash call per command. Sequence multiple commands as multiple Bash calls (in parallel where independent).
- Pre-set env vars via the shell's `VAR=value command` prefix — still a single literal command, fine.
- For multi-step or variable-bearing logic, write a Python script to a file (use the `Write` tool) and run the file with one Bash call. Bundled-helper precedent: `file_list_resolver.py`, `detect_fast_path.py`, `force_clean_team.py`, `check_agent_teams.py`.
- For watching state, prefer `Monitor` over polling loops. For reading a file, prefer `Read` over `cat` / `head` / `tail`. For searching files, prefer the first-class `Grep` tool over `grep | head` / `grep | xargs`. For writing files, prefer `Write` over `echo X > file`.

If you find yourself wanting a compound shell shape, the Python-helper-file path or a first-class tool is almost always the right answer.

## Backend dispatcher

Skill prose and helper scripts must talk to the ticket backend through the bundled dispatcher at `skills/_shared/scripts/ticket_backend.py` rather than shelling out to `bees ...` directly. Each skill resolves the dispatcher at runtime from its own base directory (which Claude Code provides in the skill invocation header) using the standard sibling-resolution shape:

```
python3 "<base-dir>/../_shared/scripts/ticket_backend.py" <verb> ...
```

This is the same `<base>/../<sibling>/scripts/<name>.py` convention `docs/doc-writing-guide.md` `## The lookup-key pattern` already documents — no absolute paths in skill prose, no per-machine breakage.

The dispatcher exposes seven verbs: `query`, `create`, `update`, `show`, `list-spaces`, `setup-spaces`, `resolve-spec`. The dispatcher's module docstring (top of `skills/_shared/scripts/ticket_backend.py`) is the authoritative source for each verb's argv shape and JSON output shape — **do not restate them here or inside any `SKILL.md`**, since the contract is single-sourced and Task 2 of Plan Bee b.9xr migrates skill prose against exactly that docstring.

**Direct `bees ...` calls are forbidden** in both `SKILL.md` prose and any helper script under `skills/<name>/scripts/` — that includes `subprocess.run(["bees", ...])` inside Python helpers. Rationale: skill prose stays backend-neutral, and sibling Epic B (`t1.9xr.4e`) extends the dispatcher with a beads branch that is invisible to skill prose because the routing is absorbed inside the dispatcher. Epic A wires the bees branch only; Epic B adds beads behind the same verb interface.

The dispatcher invocation is itself a single literal command, so `## Bash etiquette in this repo` still governs how you call it — no compounds, no pipes, no shell expansions, no diagnostic tails. For ticket-querying recipes (the `query` verb), see `## Querying tickets` and the dispatcher-shaped recipes in `docs/doc-writing-guide.md`.

## Review criteria for skill changes

When `bees-code-review`, `bees-test-review`, or `bees-doc-review` runs against changes in *this* repo, the three design rules above are mandatory review criteria layered on top of each skill's standard checks. Flag any skill-prose or helper-script change that:

- Hardcodes a language-specific command, file extension, or manifest filename (rule 1).
- Introduces a shell snippet without paired POSIX bash + Windows PowerShell variants, or relies on a bash-only fallback (rule 2).
- References this repo's specific paths, ticket IDs, or internal workflow specifics in a way that would not make sense when the skill is installed in a different project or on a different machine (rule 3).
- Calls `bees <subcommand>` directly from `SKILL.md` prose or from a helper script under `skills/<name>/scripts/`, or restates dispatcher verb argv or JSON output shapes inline rather than delegating to the dispatcher's module docstring (rule: backend dispatcher).

These criteria are additive — they do not replace, relax, or exempt any of the standard checks each review skill performs by default. They apply *only* to changes inside this repo; when the same review skills run against work in a downstream project, this section does not travel with them.

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

**Bundled helper scripts are NOT contract keys.** Earlier revisions wrote a `## Skill Paths` section to CLAUDE.md containing absolute paths to `bees-execute/scripts/force_clean_team.py` and `bees-setup/scripts/file_list_resolver.py`. That section was removed (b.963) because committing per-machine paths to a tracked file broke multi-engineer collaboration. Each skill now resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header. See `## Querying tickets` and `## The lookup-key pattern` in `docs/doc-writing-guide.md` for the runtime-resolution conventions skills must follow.

`bees-execute` and `bees-fix-issue` hard-fail with `Run /bees-setup first.` if either of the two contract sections (`Documentation Locations`, `Build Commands`), or any required key inside them, is missing from the target repo's CLAUDE.md. Preserve that precondition behavior in any edit to those skills.

## Hives and status vocabulary

The workflow uses two hives in the target repo:

- **Plans** (top-level — *not* nested in an Ideas hive). Tier ladder: t1 = Epic, t2 = Task, t3 = Subtask. Statuses: `drafted` → `ready` → `in_progress` → `done`.
- **Issues**. No children. Statuses: `open` → `done`.

When a Plan Bee is authored via `/bees-plan` for a feature with no separate PRD/SDD, the Bee's `egg` is null/empty and the **Plan Bee body itself becomes the authoritative spec**. Several skills (`bees-execute`'s PM role, `bees-breakdown-epic`) explicitly substitute "the Plan Bee body" for "the PRD/SDD" in that case — keep the substitution prose intact when editing those skills.

## Querying tickets

The bees CLI has no `ls`, `search`, `list-tickets`, or hive-scoped enumeration command — anything that smells like one is a guess. To enumerate or filter tickets (e.g., "what open issues exist?", "which Epics under this Bee are ready?"), use `bees execute-freeform-query --query-yaml '<yaml>'`. Recipes and the full filter/graph-stage vocabulary live in `docs/doc-writing-guide.md` `## Querying tickets`; consult it before composing a query rather than guessing subcommands.

## Egg resolver

`skills/bees-setup/scripts/file_list_resolver.py` is the egg resolver bundled with the skills. Hives in the target repo are colonized with this script's absolute path as their `egg_resolver`, so a Bee's `egg` field can point to one or more on-disk docs (PRD, SDD, etc.). If you change the resolver's contract (input/output shape), `bees-setup` must also be updated to migrate existing hive configs in `~/.bees/config.json`.

## Agent Teams

`bees-execute` and `bees-fix-issue` use Claude Code's experimental **Agent Teams** feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`) to run Engineer / Test Writer / Doc Writer / PM concurrently. Agent Teams is **required** for both skills — they spawn a team unconditionally and hard-fail without it. `/bees-setup` configures the env var, plus the `teammateMode` display backend (see the README's "Display backend" section for the user-facing explanation). Agent naming inside a team uses task-scoped suffixes (e.g., `engineer-xb`, `pm-xb`) to avoid collision with not-yet-shut-down agents from the previous Task; reuse the same scheme when extending team logic.

## Model assignment in execution skills

Hardcoded in `bees-execute` and `bees-fix-issue`:
- **Engineer, Test Writer, Code Reviewer, Test Reviewer**: always Opus. Not user-configurable.
- **Doc Writer, Product Manager, Doc Reviewer**: user picks Opus or Sonnet at the start of the run.

Don't change these assignments without a concrete reason — they're load-bearing for output quality and are referenced by users in their workflows.

## Documentation Locations

- **Project requirements doc (PRD)**: docs/prd.md
- **Internal architecture docs (SDD)**: docs/sdd.md
- **Customer-facing docs**: README.md
- **Engineering best practices**: CONTRIBUTING.md
- **Test writing guide**:
- **Test review guide**:
- **Doc writing guide**: docs/doc-writing-guide.md

## Build Commands

- **Compile/type-check**:
- **Format**: echo 'no formatter configured for this repo'
- **Lint**: python -m pyflakes skills/*/scripts/*.py
- **Narrow test**: echo 'no test suite for this repo'
- **Full test**: echo 'no test suite for this repo'

## When editing skills

- The README's skill table is the single source of truth for the user-visible skill catalog. If you add, remove, or rename a skill, update README.md to match.
- The `description` field in a skill's frontmatter is what Claude Code uses to decide whether to invoke the skill. Keep it precise — vague descriptions cause mis-invocation.
- Don't introduce a tmux dependency in any of the 11 portable-core skills. Tmux-dependent skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and are mentioned only as optional later-installs.
- Avoid adding stack-specific helpers (changelog tooling, license attribution, etc.) to the core — the README declares those out of scope and routes users to companion repos.

## AskUserQuestion usage

**`AskUserQuestion` is multi-choice only.** It auto-appends `Type something.` and `Chat about this`. Use it when there is a small finite set of meaningful choices. For free-text answers (paths, descriptions, names), ask in prose and let the user reply normally — do NOT add fake "Use my own answer" / "Pick Other" options that point at the auto-appended slot.
