---
id: b.aic
type: bee
title: 'Extend b.6k2 etiquette bullet: prefer first-class tools over shell control flow'
status: open
created_at: '2026-05-01T18:01:25.663093'
schema_version: '0.1'
egg: null
guid: aicthwaa4x498qbwiqyimr1wcva9ihta
---

## Description

b.6k2 added a *Shell-command etiquette* bullet to all eight runtime worker roles in `skills/bees-execute/SKILL.md` and `skills/bees-fix-issue/SKILL.md` (Engineer, Test Writer, Doc Writer, Product Manager — four sites per skill). The bullet steers workers away from shell **shapes** (`$VAR`, `$(...)`, `$?`, compound `&&`/`||`, embedded newlines, diagnostic tails). It does not steer workers away from **reaching for shell at all when a first-class Claude Code tool would do the job**.

Observed symptom that motivated this ticket: a `pm-11f` agent (PM role inside a `bees-fix-issue` team working ticket b.11f) emitted a shell polling loop to watch for engineer file edits:

```
while true; do changed=$(git diff --name-only -- skills/bees-execute/SKILL.md skills/bees-fix-issue/SKILL.md 2>/dev/null); if [ -n \"\$changed\" ]; then echo \"engineer-edits-detected: \$changed\"; break; fi; sleep 15; done
```

This violates every clause of the existing b.6k2 bullet (`cd && while`, `\$(...)`, `\$VAR`, multi-step polling), and Claude Code blocked it with the matcher reason \"Unhandled node type: string\" — a parser-classification failure distinct from the allow-rule-defeating shapes b.6k2 named. But the deeper miss is that the PM had a `Monitor` tool available and chose to write a shell `while true; sleep` polling loop instead.

## Current behavior

The b.6k2 etiquette bullet teaches *how to write a shell command if you must*. It does not teach *when not to write a shell command at all*. Subagents reach for shell control-flow constructs (`while`, `if`, polling loops, multi-step pipelines glued with `&&`) when a first-class tool — `Monitor` for watching state, `Read` for file inspection, a single `Bash` invocation followed by another `Bash` invocation rather than a chained one — would be cleaner, allow-listable, and parser-friendly.

## Expected behavior

Extend the etiquette bullet with explicit guidance to prefer first-class Claude Code tools over shell control flow:

- Watching for state to change → use `Monitor`, not `while true; do … sleep N; done`.
- Reading a file → use `Read`, not `cat`/`head`/`tail` via `Bash`.
- Multi-step logic → write the steps as separate `Bash` calls (or a script file invoked by `Bash`), not as a single chained `&&`/`||` pipeline.
- Variable-bearing logic → put the logic in a Python helper resolved from the skill base dir (the `file_list_resolver.py` / `force_clean_team.py` precedent), not in shell with `\$VAR` plumbing.

The bullet must remain a single appended sentence-or-two per role (no structural rewrite) so it stays byte-identical across the eight insertion sites — the same shape b.6k2 used.

## Impact

- Closes the gap between b.6k2's intent (\"don't emit shell shapes that defeat allow rules\") and its actual reach (\"how to format a shell command you've already decided to write\").
- Reduces parser-classification failures like \"Unhandled node type: string\" that b.6k2 didn't address.
- Reduces user permission prompts mid-run, because tool calls (Monitor/Read/etc.) are first-class operations the user has already approved by approving the skill set, whereas novel shell shapes hit the Bash matcher fresh every time.
- Complementary to b.11f (PM agents idle mid-Task; bees-execute lacks team-lead orchestration) — b.11f gives the PM proper orchestration primitives so it stops needing to improvise; this ticket nudges *all* worker roles, not just PM, toward tool-first composition.

## Portability across the three axes

This change is portable across all three of CLAUDE.md's design rules — flagging explicitly as required:

1. **Language-agnostic (Rust / Node / Python / Go / Java / unknown).** Clean. The new guidance is purely about Claude Code tool-choice; it introduces no stack-specific commands, file extensions, or manifest filenames. Applies identically regardless of the target repo's stack.

2. **POSIX + Windows PowerShell.** Clean *if phrased tool-shape-first rather than shell-syntax-first.* The advice \"use `Monitor` instead of a polling loop\" applies symmetrically — a PowerShell `while (\$true) { Start-Sleep -Seconds N }` loop is just as bad as a bash `while true; do … sleep N; done` loop, and `Monitor` is the same Claude Code tool on both OSes. Implementation note: name the **shape** being avoided (\"polling loop\", \"file read\", \"multi-step pipeline\"), not the POSIX **syntax** (\"`while true`\", \"`cat`\", \"`&&`\"), so the bullet doesn't bake in a POSIX bias. The existing b.6k2 bullet already leans POSIX-flavored in its examples (`\$VAR`, `\$(...)`, `\$?`); a stretch goal is to revisit those examples so they read as shape descriptions rather than syntax fragments, but that's optional and can ship in a follow-up if it bloats this change.

3. **Project-neutral.** Clean. No reference to this repo's paths, ticket IDs, or workflow specifics. The advice is generic Claude Code tool-vs-shell etiquette that applies to any project that installs these skills.

## Suggested fix

1. In `skills/bees-execute/SKILL.md` and `skills/bees-fix-issue/SKILL.md`, locate each of the four runtime-worker *Shell-command etiquette* bullets (8 sites total — `bees-execute/SKILL.md:288, 304, 319, 360` and `bees-fix-issue/SKILL.md:216, 228, 240, 256` at the time of filing).
2. Append a tool-first sentence to each bullet, byte-identical across all eight sites. Draft wording (refine in implementation):

   > Before writing any shell command, check whether a first-class tool fits — `Monitor` for watching state to change, `Read` for inspecting a file, separate `Bash` calls for multi-step logic — and prefer that over shell control flow (`while`, `if`, chained `&&`/`||`, polling loops, command substitution). Reach for shell only when no tool fits.

3. Verify the new wording is phrased shape-first (not POSIX-syntax-first) so it applies symmetrically to PowerShell workers.
4. Re-run `bees-code-review` on the change with the three-rule portability criteria from `CLAUDE.md` `## Review criteria for skill changes` as mandatory checks.

## Acceptance criteria

- All eight worker-role *Shell-command etiquette* bullets in the two skills are updated with byte-identical new wording.
- New wording explicitly names the tool-vs-shell choice for at least three common cases (watching state, reading a file, multi-step logic).
- New wording is phrased in tool/shape terms rather than POSIX-syntax terms, so it reads correctly to a worker running on Windows PowerShell.
- No new shell snippets, no new helper scripts (this is a prose-only change).
- Honors the three design rules in `CLAUDE.md` — language-agnostic, POSIX + Windows PowerShell, project-neutral — confirmed by review.

## Out of scope

- Changing the existing POSIX-flavored examples in the b.6k2 bullet (`\$VAR`, `\$(...)`, `\$?`). Optional stretch follow-up; leave for a separate ticket if it would bloat this change.
- Touching the Agent Teams preflight check (b.ekz covers that — different code path, parent session not worker session).
- Implementing PM team-lead orchestration primitives (b.11f covers that — different layer; this ticket nudges worker behavior, b.11f gives PM the primitives so it stops needing to improvise).
