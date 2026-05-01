# Doc Writing Guide

Conventions for authoring and editing documentation in the bees-workflow repo. The artifacts here are skill markdown files (`skills/<name>/SKILL.md`), the README, CONTRIBUTING.md, CLAUDE.md, and these guides. There is no inline source-code documentation to maintain — skill prose *is* the documentation.

This guide is opinionated. When the rules here conflict with a "standard" markdown style guide, follow this guide. When they conflict with [CONTRIBUTING.md](../CONTRIBUTING.md)'s two non-negotiable design rules, follow CONTRIBUTING.md.

## Audience and stance

A skill is read by Claude at invocation time, not by a human at design time. Write for an instructable agent that has no memory of prior sessions and no access to context beyond what the skill prose provides.

- **Direct, imperative voice.** "Read CLAUDE.md" not "you should read CLAUDE.md". "Write the section as below" not "the section can be written as".
- **Code over prose.** A labeled shell block teaches more than a paragraph describing what the shell block would do.
- **Opinionated defaults, not exhaustive references.** A skill that lists six options for everything is a skill that makes Claude waffle. Pick one, mark it "(Recommended)", and let the user override via AskUserQuestion.
- **No headers-and-bullets-for-everything.** A two-sentence answer should be two sentences, not a "Summary" header followed by a one-bullet list.

## The frontmatter contract

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-name
description: One-line description used by Claude Code to decide whether to invoke this skill.
---
```

- The `name` field appears in `/<name>` invocations and in the README skill table. Hyphens, not underscores.
- The `description` field is what Claude Code shows the user *and* uses to decide invocation eligibility. Vague descriptions cause mis-invocation. Lead with the verb: "Configure a repo for the bees workflow" not "This skill configures…". State scope precisely — what the skill *does* and what it does *not* do.
- If a skill has triggering vs. skipping conditions worth being explicit about (e.g., "TRIGGER when X; SKIP when Y"), put them in the description. Several skills in this repo do.

When you add, remove, or rename a skill, the README's skill table is the single source of truth — update it in the same change.

## OS-conditional shell blocks

Every shell snippet in a `SKILL.md` ships labeled for at least POSIX bash and native Windows PowerShell. cmd.exe is optional. There is no bash-only fallback.

```markdown
# POSIX (bash / zsh — macOS, Linux, WSL):
which bees

# Windows (PowerShell):
Get-Command bees -ErrorAction SilentlyContinue
```

Rules:

- Always label the OS in a comment line above the snippet, even if the command happens to work in both shells. Future readers shouldn't have to guess intent.
- Quote variable expansion correctly per shell. PowerShell's `$env:USERPROFILE` is not the same as bash's `$HOME`.
- When a snippet embeds Python or another scripting language, use a single-quoted PowerShell here-string (`@'…'@`) so PowerShell doesn't pre-expand `$variables` in the script body before invoking the interpreter. The bees-setup skill has the canonical example.
- Don't carry shell variables across snippet boundaries. Each Bash tool invocation in Claude Code is a fresh shell, so a `VAR=...` set in one fenced block is empty when referenced from a later one. If a value is needed in multiple snippets (a resolver path, a hive ID, etc.), inline the literal at every site or pass it as a positional argument to the snippet's invocation. The bug surfaces silently — e.g., `--egg-resolver ""` reaches downstream commands and the failure manifests far from the cause.
- Helper logic that doesn't fit naturally as a shell one-liner belongs in a Python script under `skills/<name>/scripts/`, not as a wall of OS-paired shell.

## The lookup-key pattern (no hardcoded language commands)

Skills run on Rust, Node, Python, Go, Java, and unknown stacks. Never hardcode `cargo test`, `npm run lint`, or any other language-specific command in skill prose.

Instead, refer to the contract keys that `bees-setup` writes to the *target repo's* CLAUDE.md:

- `## Build Commands` keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`
- `## Documentation Locations` keys: `Project requirements doc (PRD)`, `Internal architecture docs (SDD)`, `Customer-facing docs`, `Engineering best practices`, `Test writing guide`, `Test review guide`, `Doc writing guide`

Bundled helper scripts (e.g., `force_clean_team.py`) are deliberately *not* on this list. Their paths are per-machine and would corrupt CLAUDE.md across contributors if persisted there. Each skill resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header (`Base directory for this skill: ...`). A skill using its own bundled script: `<base>/scripts/<name>.py`. A skill using a sibling's bundled script: `<base>/../<sibling>/scripts/<name>.py`.

A skill that needs to run the project's full test suite reads the value of the `Full test` key from CLAUDE.md and shell-executes that. The skill's job is to know *when* to run a full test, not *what* the command is.

These keys are a string contract. Don't rename them in any skill — every other skill looks them up by exact match.

## Querying tickets

Whenever a skill needs to find tickets in a hive — list open issues, find an Epic's children, trace a child up to its parent, etc. — the verb is always:

```bash
bees execute-freeform-query --query-yaml '<yaml>'
```

The bees CLI does not have a `list-tickets` command, a `search` command, or a hive-scoped enumeration command. Anything that smells like one is a guess; verify with `bees execute-freeform-query --help` before writing a new recipe.

**Prose rule.** When a skill tells Claude to "find", "search", "list", or "look up" tickets, ship the concrete recipe inline at that point. Vague prose ("search the issues hive for a duplicate") forces the agent to invent a CLI verb and is the same anti-pattern CONTRIBUTING.md flags under "Don't replace concrete shell snippets with vague prose."

The rule extends past the recipe itself. If a recipe's `report:` projection returns only part of what the prose-after-the-recipe instructs the agent to check (e.g., the projection reports `up_dependencies` as IDs and the prose then asks "verify each dependency is `done`"), ship the follow-up recipe inline too. `bees show-ticket --ids <id1> <id2> ...` is the canonical batch-lookup shape — use it explicitly rather than leaving the agent to derive it.

**Canonical YAML shape.**

```yaml
stages:
  - [<filters>]      # search stage 0: filter the full ticket set
  - [<traversal>]    # graph stage: traverse from previous stage's results
  - [<filters>]      # optional: re-filter after traversal
report: [<fields>]   # optional: add named fields to each returned ticket
```

**Filter terms** (AND logic within a stage; documented in `bees execute-freeform-query --help`):

- `type=bee`, `type=t1`, `type=t2`, `type=t3`
- `status=<value>` — exact match
- `hive=<name>` or `hive~<regex>` — restrict to one or more hives
- `id=<ticket_id>` — exact match
- `parent=<ticket_id>` — children of one specific ticket
- `guid=<guid>`
- `title~<regex>` — regex match on title (useful for duplicate-detection)
- `tag~<regex>` — regex match on any tag

**Graph stages** (traverse from current result set):

- `parent` — get the parent of each ticket in the working set
- `children` — get the children of each ticket
- `up_dependencies` — get upstream blockers
- `down_dependencies` — get downstream dependents

**The `report:` clause is real but undocumented in `--help`.** Without it, the response contains only `ticket_ids` (a flat list of IDs). With `report: [title, ticket_status, up_dependencies, ...]`, the response contains a `tickets` array where each ticket carries the requested fields. Use `report:` whenever the agent will display results to the user, pattern-match titles, or reason about status/dependencies. Omit `report:` when you only need IDs to traverse next.

**Worked examples.**

```bash
# All open issues — used by /bees-file-issue (duplicate check) and /bees-fix-issue (no-args / all modes):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues, status=open]
report: [title]'

# Ready Plan Bees — used by /bees-breakdown-epic and /bees-execute when called without args:
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans, status=ready]
report: [title]'

# Drafted Epic children of a specific Plan Bee — used by /bees-breakdown-epic when caller supplies a Bee ID:
bees execute-freeform-query --query-yaml 'stages:
  - [parent=<bee-id>, type=t1, status=drafted]
report: [title, up_dependencies]'

# Trace from an Epic up to its parent Bee — used by /bees-execute when caller supplies an Epic ID:
bees execute-freeform-query --query-yaml 'stages:
  - [id=<epic-id>]
  - [parent]
report: [title, ticket_status]'

# Status snapshot — all Plan Bees plus their children (two-stage traversal):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans]
  - [children]
report: [title, ticket_status, up_dependencies]'
```

**Cross-platform note.** The single-quoted YAML literal works identically in POSIX bash/zsh and Windows PowerShell single-quoted strings — embedded `$variables` are not expanded by either shell inside single quotes. So query recipes do not need OS-paired variants; one block covers both. (Exception: if a recipe interpolates a shell variable for the ticket ID, the interpolation syntax is shell-specific and the recipe needs OS-paired variants like every other shell snippet.)

## Hard-fail preconditions

Execution skills (`bees-execute`, `bees-fix-issue`) hard-fail with `Run /bees-setup first.` when the target CLAUDE.md is missing either of the two required sections (`Documentation Locations`, `Build Commands`) or any required key inside them. Preserve that precondition behavior in any edit to those skills.

When you add a new required key to one of those sections, update bees-setup to write it *and* update every downstream skill's precondition check in the same change.

## AskUserQuestion patterns

Skills use `AskUserQuestion` for decisions the user should drive. Patterns we follow:

- **Detect first, prompt second.** If a piece of configuration already exists, show the user the current value and ask whether to keep or change it — don't blindly re-prompt. Re-runs of `/bees-setup` should be near-no-ops when nothing has changed.
- **Recommended option first.** When you have a sensible default, make it the first option and append "(Recommended)" to the label. Users should be able to skim and accept.
- **Batch related questions.** AskUserQuestion supports up to 4 questions per call. Group related decisions (e.g., the seven Documentation Locations slots) so the user makes them in one mental context, not seven.
- **No "Other" option in your options list.** The runtime adds a free-text "Other" automatically.
- **Reframe when needed.** When a default-skip looks tempting but is actually wrong, lead with *why* the user should care. The Bootstrap PRD/SDD section in `bees-setup` is the canonical example: it explicitly reframes "I don't read PRDs" as "PRDs are read by *agents*, not by you".

## Inline style

- **No emojis** unless the user explicitly requests them. This applies to skill prose, generated docs, commit messages, and PR bodies.
- **Sentence case for headings**, not Title Case. "Build commands", not "Build Commands". (Exception: contract-key headings like `## Build Commands` are matched exactly by other skills, so those stay as-is.)
- **Backtick code, file paths, command names, contract keys, and CLI flags.** `bees colonize-hive`, not "bees colonize-hive". `~/.bees/config.json`, not ~/.bees/config.json.
- **Reference files with `path:line` when pointing at a specific location.** This lets readers navigate directly. `skills/bees-setup/SKILL.md:42` beats "around line 42 of the bees-setup skill".
- **Lists are for enumerable items**, not for narrative steps that should be paragraphs. Five bullets that each say "the system also …" is a paragraph in disguise — collapse it.
- **Tables are for grids of attributes.** A two-column table with one row is a sentence. Don't make a table out of two facts.

## What not to document

- **Don't explain WHAT the code does** when well-named identifiers already do that. Skill prose is the contract; restating the contract in a comment is duplication.
- **Don't reference the current task, fix, or callers** ("used by X", "added for the Y flow", "handles the case from issue #123"). Those belong in the PR description and rot as the codebase evolves.
- **Don't write multi-paragraph docstrings** in helper scripts. One short module-level summary, then code. Inline comments only when the *why* is non-obvious — a hidden constraint, a workaround, behavior that would surprise a reader.
- **Don't pre-document features that don't exist.** No "this skill will support X in a future release". When X exists, document it. Until then, don't.

## Project terminology

Use these terms consistently. Mixing synonyms forces readers (and Claude) to mentally re-map.

- **Skill** — one of the directories under `skills/<name>/`. Has a `SKILL.md` and optionally `scripts/`.
- **Hive** — a bees collection. The workflow uses two: **Plans** (top-level, with t1/t2/t3 = Epic/Task/Subtask) and **Issues** (no children).
- **Bee** — a ticket inside a hive. A "Plan Bee" is a top-level Bee in the Plans hive. An "Epic" is a t1 child of a Plan Bee.
- **Egg** — a Bee's `egg` field, which points at one or more on-disk source documents (PRD, SDD, etc.). Resolved by the egg resolver script. May be null/empty — when null on a Plan Bee, the **Plan Bee body itself becomes the authoritative spec**.
- **Target repo** — the repo a user runs `/bees-*` commands against. Distinct from this repo (the skill set itself).
- **Agent Teams** — Claude Code's experimental concurrent-agent feature, gated by `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. `bees-execute` and `bees-fix-issue` use it for parallel Engineer / Test Writer / Doc Writer / PM execution.

## When you're updating an existing skill

1. **Read the README's skill table first.** If your edit changes user-visible behavior (name, description, what the skill does), the table is part of the change.
2. **Read CLAUDE.md.** It captures project-internal guidance that applies to every skill edit (cross-platform rules, contract keys, model assignments, etc.).
3. **Agent Teams is required** for `bees-execute` and `bees-fix-issue`. Both skills spawn a team unconditionally — there is no single-agent fallback path. Don't introduce conditional "if-Teams-off" branches when editing those skills; rely on the precondition check to hard-fail when Agent Teams isn't enabled.
4. **Don't introduce stack-specific helpers** to the portable core (Rust changelogs, Node license tooling, etc.). Those route to companion repos per the README.
5. **Don't introduce a tmux dependency** to any of the 11 portable-core skills.
