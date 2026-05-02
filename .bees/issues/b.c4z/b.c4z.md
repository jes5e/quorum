---
id: b.c4z
type: bee
title: Adopt --body-file / --chunk-file across this repo's ticket-creation skills
status: open
created_at: '2026-05-02T10:17:53.837748'
schema_version: '0.1'
egg: null
guid: c4zjrn6q4trz8ffz2sozho4eqp44sfsv
---

## Description

Upstream bees shipped file-input variants for every body-text CLI flag (gabemahoney/bees PR #6, closes #2):

- `bees create-ticket --body-file PATH`
- `bees update-ticket --body-file PATH`
- `bees append-ticket-body --chunk-file PATH`

Each new flag is mutually exclusive with its inline counterpart (`--body` or `--chunk`); path `-` reads from stdin; UTF-8 only; same 10000-character cap. The append-ticket-body mutex is `required=True` (caller must supply one of `--chunk` or `--chunk-file`).

This eliminates two long-standing problems with multi-paragraph markdown bodies:

1. **Permission friction**: inline `--body "<markdown>"` arguments containing `
#` (newline followed by a markdown heading) trigger Claude Code's command-injection guard, which forces a permission prompt regardless of how broad the user's allowlist is. The new flag sidesteps that — the path argument is short, contains no markdown, and clears the validator.
2. **Quoting fragility**: bodies containing backticks, dollar signs, or quotes are easy to mangle when inlined or passed through `$(cat …)` substitution. Reading from a file removes the shell-quoting surface entirely.

This issue tracks updating every skill in this repo that authors multi-paragraph ticket bodies (or chunks) to use the new flags.

## Current behavior

Skills today inline ticket bodies as quoted-string placeholders, e.g. `--body "<structured body>"`, with the agent expected to substitute the literal markdown at invocation time. This means every multi-section ticket creation hits the validator's `
#` heuristic, and the skill prose ships paired POSIX/PowerShell snippets that differ only in shell-quoting.

Note: this repo never adopted a `$(cat …)` workaround — we waited for upstream `--body-file` / `--chunk-file` instead. So the migration is "introduce a temp-file authoring step + use the file flag," not "swap one flag for another."

## Expected behavior

For each skill that creates or updates tickets with multi-paragraph bodies, or appends multi-paragraph chunks:

1. Skill prose tells Claude to write the body/chunk to a temp file via the `Write` tool (path chosen by the agent — e.g. a short random suffix under the OS temp dir).
2. The `bees create-ticket` / `bees update-ticket` invocation passes `--body-file <that-same-path>`. The `bees append-ticket-body` invocation passes `--chunk-file <that-same-path>`.
3. Claude removes the temp file after the bees command exits.

Because the helper handles the file read internally, the POSIX/PowerShell shell snippets can collapse to one labeled block (or stay split if other args differ) — no `$(cat …)` vs `Get-Content -Raw` divergence needed.

## Migration sites

Anchored on section names so this list survives line-number drift:

- **skills/bees-file-issue/SKILL.md** — Step 3 ("Create the ticket"). Has explicit POSIX + PowerShell snippets with `--body "<structured body>"` placeholders; rewrite both to use `--body-file`.
- **skills/bees-plan/SKILL.md** — Step 5 Path B. Two snippet pairs: the Plan Bee creation (`--ticket-type bee`) and the per-Epic creation (`--ticket-type t1`). Migrate both to `--body-file`.
- **skills/bees-plan-from-specs/SKILL.md** — Step 4 ("Create Shell Epics"). No shell snippet exists; the skill controls Epic creation through prose. Add a sentence telling the agent to author each Epic body via the temp-file + `--body-file` pattern.
- **skills/bees-breakdown-epic/SKILL.md** — Section 4/5 where the team-lead creates Tasks and Subtasks. Same prose-only situation as bees-plan-from-specs; add the `--body-file` directive next to the existing "Only YOU (the team lead) run `bees create-ticket`" prose. Task/Subtask bodies are the most heading-dense markdown in the workflow (Context / What Needs to Change / Key Files / Acceptance Criteria), so this is the highest-frequency offender.
- **Any skill that uses `bees update-ticket --body "<structured body>"`** for multi-paragraph body rewrites — migrate to `--body-file`. (Audit during the migration; many skills only `update-ticket --status …` and don't trigger this.)
- **Any skill that uses `bees append-ticket-body --chunk "<paragraph>"`** for multi-paragraph chunks — migrate to `--chunk-file`.

Short single-line bodies / chunks (titles only, single-line summaries, status-only updates) can stay on inline `--body BODY` / `--chunk TEXT` — the migration is for the multi-paragraph case only.

## Suggested fix

1. Add a centralized note in `docs/doc-writing-guide.md` (a new "Authoring ticket bodies" section, alongside the existing "OS-conditional shell blocks" and "Querying tickets" sections) that documents the temp-file + file-flag pattern once. Each skill links to it instead of repeating the prose. The note should cover both `--body-file` (create/update) and `--chunk-file` (append) since the temp-file mechanics are identical.
2. At each migration site listed above, replace inline `--body "..."` / `--chunk "..."` with the appropriate file flag and add a Write-tool step authoring the body/chunk to that path.
3. Where the only OS divergence in a snippet was the body-quoting style, collapse to a single block.

## Out of scope

- `--egg-file` for `--egg JSON` — JSON args aren't affected by the validator heuristic in the same way; upstream issue #2 explicitly deferred this.
- Curl-style `--body @PATH` spelling — the flag uses a separate name (`--body-file`).
- Bumping a minimum-bees-version pin in CLAUDE.md or README — bees-workflow has no version manifest today; track separately.
- Binary file support — the new helper enforces UTF-8.

## Impact

- One fewer permission prompt per multi-paragraph ticket creation/update/append under Claude Code, across every skill that files tickets.
- Eliminates shell-quoting fragility for bodies/chunks containing backticks, quotes, dollar signs, etc.
- Shrinks skill prose: many OS-paired shell snippets collapse to one block.
- Makes the temp-file authoring step explicit, which is also clearer for human contributors reading the skill.

