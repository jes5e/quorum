---
id: b.6k2
type: bee
title: Runtime agents emit shell commands that defeat user Bash allow rules
status: open
created_at: '2026-05-01T17:02:29.489069'
schema_version: '0.1'
egg: null
guid: 6k2kd181r99xnv6aq48bjabzkng99yz3
---

## Description
Engineer (and other runtime agents spawned by `bees-execute` / `bees-fix-issue`) routinely generate shell commands that defeat the user's Bash allow rules in Claude Code's permission matcher, forcing the user to approve every run even when a broad rule like `Bash(python3 *)` is in place.

## Current behavior
Two recurring offenders observed in real sessions on this repo:

1. **Embedded newlines inside `-c '<multi-line script>'`.** Claude Code's matcher treats newlines as command separators (alongside `;`, `&&`, `||`, `|`, etc.) and requires each parsed subcommand to match an allow rule independently. So a multi-line script body splits the command into many "subcommands" and `Bash(python3 *)` only covers the first.

2. **Diagnostic tails like `; echo exit=$?`.** Two strikes at once:
   - The `;` is a separator, so `echo exit=$?` is treated as a separate subcommand outside the allow rule.
   - `$?` is a `simple_expansion`, which the matcher refuses to wildcard-match regardless of allow rules (undocumented but observable via the prompt's hint string).

   The Bash tool already surfaces exit status in its result, so the tail is pure cargo.

Real examples from observed sessions (all prompted despite `Bash(python3 *)` on the allow list):
- `python3 -c '<multi-line script with embedded newlines>'`
- `python3 -m pyflakes skills/*/scripts/*.py 2>&1; echo exit=$?`
- `python3 -m pyflakes <three explicit paths> 2>&1; echo exit=$?`

## Expected behavior
Runtime agents prefer one-literal-command invocations that match user allow rules. No diagnostic tails, no embedded newlines, no `$VAR` / `$?` / `$(…)` expansions, no compound commands when a single one works. Multi-step scripts go in a file that is then executed.

## Impact
- UX cost: the user is prompted for approval on nearly every command an agent runs, even with thoughtful allow rules in place. Friction compounds across a multi-Task Bee.
- Mitigation cost: the user has to either approve every command individually or write absurdly narrow allow rules to defeat the matcher's conservatism.
- Not a correctness bug — commands still execute correctly when approved — but a meaningful productivity drag during execution.

## Suggested fix
Append a short shell-command etiquette block to the role-instruction prompts for Engineer, Test Writer, Doc Writer, and PM in both `skills/bees-execute/SKILL.md` and `skills/bees-fix-issue/SKILL.md`. Suggested wording (cross-platform, language-agnostic, project-agnostic):

> When running shell commands, prefer one literal command per invocation. Don't append diagnostic tails like `; echo exit=$?` or `&& echo done` — the Bash tool already reports exit status. Avoid embedded newlines, `$VAR` / `$?` / `$(...)`, and compound commands when a simple one works. If you need a multi-step script, write it to a file and run the file rather than passing it inline via `-c` or a heredoc.

**Why runtime prompts and not `docs/doc-writing-guide.md`:** that guide is for skill authors editing this repo. Engineer and the other runtime agents never read it. The actual problem is at runtime, so the guidance has to live in the prompts those agents are spawned with.

**Constraints (must be preserved):**
- Cross-platform. Identical wording works for POSIX bash/zsh and Windows PowerShell — both shells use `;` as a separator and both have `$VAR`-style expansion. Don't introduce bash-only or PowerShell-only phrasing.
- Language-agnostic. The rule is about command shape, not what's invoked. No mention of `python3`, `cargo`, `npm`, etc.
- Project-agnostic. Don't reference this repo's specific Build Commands or paths.
- Don't add it to `docs/doc-writing-guide.md`. Runtime prompts only.

**Key files:**
- `skills/bees-execute/SKILL.md` — role-instruction sections for Engineer (~L243-258), Test Writer, Doc Writer, PM.
- `skills/bees-fix-issue/SKILL.md` — equivalent role-instruction sections.

**Acceptance:**
- Both SKILL.md files carry the etiquette block in the relevant agent role-instruction sections (Engineer, Test Writer, Doc Writer, PM).
- The block is identical (or near-identical) wording across both skills and across all four roles, since it's universal advice.
- No new helper scripts, no changes to `doc-writing-guide.md`, no changes to Build Commands or any contract keys.
- README.md does not need to change — this is internal agent-prompt copy, not part of the user-visible skill catalog.
