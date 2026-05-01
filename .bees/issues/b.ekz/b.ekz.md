---
id: b.ekz
type: bee
title: Agent Teams preflight in bees-execute / bees-fix-issue trips Bash expansion-obfuscation matcher
status: open
created_at: '2026-05-01T17:56:24.800729'
schema_version: '0.1'
egg: null
guid: ekzs71i4pbhkzxs1wdw8n5xq8vm6zt5y
---

## Description

The Agent Teams precondition check at the top of `bees-execute` and `bees-fix-issue` runs in the **parent** Claude Code session — before any team is spawned — and uses shell shapes that defeat user Bash allow rules. b.6k2 added a \"Shell-command etiquette\" bullet to each runtime worker role's Instructions to steer spawned agents away from these exact patterns, but the bullet only travels with worker prompts. The preflight, two screens up in the same `SKILL.md`, was not touched and still uses the offending shapes.

## Current behavior

Invoking `/bees-execute` or `/bees-fix-issue` on a properly-configured machine triggers a Claude Code permission prompt with the matcher reason \"Contains brace with quote character (expansion obfuscation)\", even when the user has previously allowed the skill set. The triggering command is the preflight check itself.

Locations:

- `skills/bees-execute/SKILL.md:38-72` — *Verifying the Agent Teams precondition* section, POSIX bash block (lines 39-56) and Windows PowerShell block (lines 60-72).
- `skills/bees-fix-issue/SKILL.md:28-62` — same section, same two blocks.

Patterns the current preflight uses that b.6k2 explicitly calls out as defeating allow rules:

- `python3 -c '<multi-line script>'` — embedded newlines in `-c`.
- `... || test \"\${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-}\" = \"1\" || { echo ... ; exit 1; }` — compound `||` chain plus brace+default expansion.
- POSIX block is bash-only; the PowerShell block is a hand-maintained parallel reimplementation of the same JSON read, which is its own portability and drift hazard.

## Expected behavior

The preflight should run as a single stable invocation line per OS that the user can allow-list once and never re-prompt on. Per `CONTRIBUTING.md` design rule 2 (POSIX + Windows PowerShell) and the bundled-helper precedent established by `bees-setup/scripts/file_list_resolver.py` and `bees-execute/scripts/force_clean_team.py`, the logic belongs in a Python helper, not inline in `SKILL.md`.

## Impact

- Every fresh `/bees-execute` and `/bees-fix-issue` invocation prompts the user, even after the skill set is approved — a UX regression that erodes the value of allow-listing.
- The POSIX and PowerShell blocks are parallel implementations of the same JSON read; future changes to the precondition logic require keeping both in sync by hand.
- Internally inconsistent with b.6k2: the same `SKILL.md` files now tell their workers to avoid these shapes while the parent session uses them.

## Suggested fix

Extract the precondition logic into a bundled Python helper and invoke it from `SKILL.md` as a single line per OS.

1. Add `skills/bees-execute/scripts/check_agent_teams.py` (and the same for `bees-fix-issue`, or one shared helper that both skills resolve at runtime — pick whichever matches the existing helper-resolution conventions in `docs/doc-writing-guide.md` `## Querying tickets` and `## The lookup-key pattern`).
2. Helper reads `~/.claude/settings.json` (or `%USERPROFILE%\\.claude\\settings.json` on Windows), looks up `.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, falls back to the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` environment variable, exits 0 if either is `\"1\"`, exits 1 with the existing `Run /bees-setup first.` message otherwise. Behavior and error wording must be byte-identical to today's preflight.
3. Replace the POSIX bash block with: `python3 \"\$SKILL_DIR/scripts/check_agent_teams.py\"`
4. Replace the PowerShell block with: `python \"\$env:SKILL_DIR\\scripts\\check_agent_teams.py\"`
5. Apply the same change to both `skills/bees-execute/SKILL.md` and `skills/bees-fix-issue/SKILL.md`.

## Acceptance criteria

- Preflight no longer triggers Claude Code's expansion-obfuscation matcher on either OS.
- Single source of truth for the precondition logic — no parallel POSIX/PowerShell reimplementations of the JSON read.
- Both `bees-execute` and `bees-fix-issue` are updated identically; preflight error message and exit semantics unchanged.
- Honors the three design rules in `CLAUDE.md` (language-agnostic for the target repo, POSIX + Windows PowerShell paired invocation lines, project-neutral).
- Helper is resolved at runtime from the skill's base directory using the same conventions as `file_list_resolver.py` and `force_clean_team.py`.

## Out of scope

- Changing *what* the preflight checks or the failure message wording.
- Touching the runtime worker etiquette bullet added in b.6k2 (that fix is correct for its scope; this ticket fills the parent-session gap).
