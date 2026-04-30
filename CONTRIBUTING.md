# Contributing to bees-workflow

This file captures workflow design rationale, intentional asymmetries, and anti-patterns. External reviewers and future agents working on these skills don't have access to the conversation history, commit messages, or ticket bodies that informed many non-obvious choices. This is the durable record so design decisions don't have to be re-litigated each time someone touches a skill.

## This is the canonical source

All skill edits happen in this repository. Per-project copies (e.g., `~/.claude/skills/<skill>/` or `<repo>/.claude/skills/<skill>/`) are install artifacts. Editing them directly creates drift; future re-installs will overwrite the edits.

If you have a clone at `~/code/bees-workflow/` and want live editing, symlink your global install at it:

```bash
# POSIX (bash / zsh):
for s in bees-breakdown-epic bees-execute bees-file-issue bees-fix-issue \
         bees-plan bees-plan-from-specs bees-setup bees-status \
         code-review doc-review test-review; do
  ln -sfn "$HOME/code/bees-workflow/skills/$s" "$HOME/.claude/skills/$s"
done

# Windows (PowerShell, run as Administrator for symlinks):
$skills = 'bees-breakdown-epic','bees-execute','bees-file-issue','bees-fix-issue',
          'bees-plan','bees-plan-from-specs','bees-setup','bees-status',
          'code-review','doc-review','test-review'
foreach ($s in $skills) {
  New-Item -ItemType SymbolicLink -Force -Path "$HOME\.claude\skills\$s" `
    -Target "$HOME\code\bees-workflow\skills\$s"
}
```

After this, edits in `~/code/bees-workflow/skills/<skill>/SKILL.md` are immediately picked up by Claude Code without re-installing.

## Workflow principles

1. **Language-agnostic.** Skills must work on Rust, Node, Python, Go, Java, C/C++, and unknown stacks. The pattern is: a project's `CLAUDE.md` declares `## Build Commands` and `## Documentation Locations` sections; skills look up commands and paths from there by exact key. Never hardcode `cargo`, `npm`, `cargo test`, `pytest`, etc. in skill prose.
2. **Cross-platform.** POSIX (bash/zsh on macOS and Linux) and native Windows PowerShell both work. Every multi-line shell snippet ships as labeled OS-conditional blocks. Helper scripts are Python (cross-platform) or come in OS-paired implementations.
3. **Idempotent.** Re-running `/bees-setup`, `/bees-plan`, etc. on an already-configured project should be a no-op or surface "already configured, change anything?" prompts — never blow away existing config.
4. **Body-as-spec is a supported mode.** When a Plan Bee is created via `/bees-plan` for a feature without a separate PRD/SDD, its `egg` is null and the Plan Bee body itself is the authoritative spec. Downstream skills (`/bees-breakdown-epic`, `/bees-execute`, `/bees-fix-issue`) all have explicit prose for this — don't simplify it away on a future refactor.
5. **Cumulative docs preferred but not required.** When `/bees-plan` updates docs, it adds a new `### Feature: <title>` subsection under cumulative `## Per-feature scope` / `## Per-feature design` headers; old features stay documented. But the workflow does not enforce this — projects with monolithic specs work fine too.

## Skill conventions

- **Frontmatter:** Only `name` and `description` are honored by Claude Code's skill loader. `triggers:` and `disable-model-invocation:` are silently ignored. Don't add them to new skills; remove them from existing skills if you spot them.
- **Shell snippets:** OS-conditional labeled blocks (POSIX bash + Windows PowerShell at minimum). Single-line trivial snippets can omit the PowerShell variant if and only if the syntax is identical (e.g., `bees show-ticket --ids b.xyz`).
- **Helper scripts:** Ship inside the skill's `scripts/` directory (e.g., `bees-execute/scripts/force_clean_team.py`). Get their absolute path via the `## Skill Paths` section in CLAUDE.md (resolved by `/bees-setup`).
- **JSON file edits:** Use a Python one-liner with `json.load` / `json.dump`, not prose-text-edit instructions. Direct text editing has no atomicity story and corrupts the file on a wrong escape.
- **CLI invocation form:** Use the shell-form `bees show-ticket --ids <id>`, not the function-call form `show_ticket(ticket_id="<id>")`. None of the skills bootstrap the MCP server, so the CLI form is the right one. (The function-call form is what the bees MCP server exposes, but skills don't run that path.)

## Intentional asymmetries

These look like inconsistencies if you compare two skills side-by-side without context. They're deliberate.

- **`/bees-execute`'s Doc Writer executes pre-planned doc Subtasks; `/bees-fix-issue`'s Doc Writer reviews the Engineer's diff for ad-hoc gaps.** `/bees-execute` Tasks have a planned subtask breakdown (from `/bees-breakdown-epic`); the Doc Writer's primary job is to execute the doc subtasks and then review for gaps. `/bees-fix-issue` has no pre-planned subtasks — the Doc Writer reviews the diff and updates ad-hoc. Different work shapes need different postures. Both blocks have an inline note pointing at the other.
- **`/bees-plan` (interactive scope-shaping) vs `/bees-plan-from-specs` (express path with finalized PRD+SDD on disk).** Two entry points to the same Plan Bee + Epics output. `/bees-plan` is the discovery path; `/bees-plan-from-specs` is the "I already nailed the scope" path. Keep both — collapsing them into one pushes too much complexity into a single skill.
- **Language-conditional examples in `/bees-setup`.** The stack-detection table IS supposed to be Rust/Node/Python/Go specific — it's defining what the user's `## Build Commands` section should resolve to in each stack. Generalizing it to "the appropriate command for your language" defeats the point.
- **Egg lives on the Plan Bee, not on Epics.** The bees CLI accepts `--egg` only on top-level Bees, not on child-tier tickets. Every Epic in a Plan Bee can trace back to the same PRD/SDD by reading the parent's egg. Don't try to set egg on Epics.
- **`/bees-breakdown-epic` is the only skill where team members run in `mode: "plan"`.** Subagents during breakdown are read-only researchers; only the team-lead runs ticket-mutating commands. Other execution skills (`/bees-execute`, `/bees-fix-issue`) let team members create commits, not tickets — different scope of authority.

## Anti-patterns

- **Don't proliferate bundled scripts.** Each new helper in `scripts/` is install-mode coupling and maintenance burden. Use a Python one-liner in skill prose for one-off operations (JSON edits, simple file ops). Add a script only when the operation is non-trivial AND used in 2+ places.
- **Don't add frontmatter keys Claude Code ignores.** Keeps the skill source honest about what's actually consumed.
- **Don't hardcode hive paths or doc paths.** `/bees-setup` lets the user pick where each hive lives (in-repo, sibling-to-repo, or anywhere). Skills must resolve paths at runtime via `bees list-hives` or CLAUDE.md `## Documentation Locations`.
- **Don't replace concrete shell snippets with vague prose** ("run the appropriate test command"). Concrete commands per OS keep agent reliability up — vague prose forces the agent to guess and often guesses wrong.
- **Don't categorize-and-split issue tickets.** Default to bundling related issues into a single ticket with sub-task labels. The bees workflow optimizes for agent work efficiency (per-ticket overhead is the cost), not human triage. See `/bees-file-issue`'s "House style" section for the rule.
- **Don't skip verification before recommending paths or flags.** When prose says `bees set-types --child-tiers ...`, that flag must exist. Verify with `--help` before writing it. CLI-flag drift is a recurring source of P0 bugs (see issue tracking history).

## Status / type renames history

These renames happened in this order with specific reasons. A future "simplification" that reverses any of them would re-introduce the issue it solved.

- **Hive name `bugs` → `issues`.** "Bugs" is a subset of what gets filed. "Issues" covers bugs, wishlist items, doc fixes, and meta-tasks. The skill prose was updated; some legacy projects still have a `bugs` hive — those should be `bees colonize-hive` migrated.
- **Status names `larva` / `pupa` / `worker` / `finished` → `drafted` / `ready` / `in_progress` / `done`.** The bee-themed names obscured what state a ticket was in. The current names line up with how every other ticket system describes status, which makes the workflow accessible to people new to bees.
- **Skill prefix: `bees-*`.** All workflow skills are prefixed `bees-` so a project with multiple skill providers can tell at a glance what comes from this repo.

## Where things live

- **Issues / bugs in this repo** — file in the issues hive of whichever project surfaced them, then reference them in PRs/commits here. The issues hive in `live_edit` was the first home for the validation reports that drove this workflow's design (b.622 and the b.sjz / b.dp2 / b.nyv / b.4xw / b.qw2 / b.ewe / b.bp5 / b.obn set that followed).
- **Discussion** — GitHub issues on this repo are fine for "what should the skill do?" questions. Use issue tickets in your bees workflow for "fix X in skill Y" findings — those become the agent-fixable input set.

## Reviewing changes

A change to skill prose touches behavior that may not surface until a downstream skill executes. Before merging a non-trivial change:

1. Re-read both skills if you change cross-skill prose (e.g., a precondition the other skill relies on).
2. If you change a skill's required CLAUDE.md section keys, update `/bees-setup` so it writes the new keys, AND update every consumer skill's precondition list.
3. If you change a CLI invocation, run `bees <command> --help` and verify the flag still exists with the same name.
4. If you change a multi-line shell snippet, verify both POSIX and PowerShell variants still produce the same effect.
