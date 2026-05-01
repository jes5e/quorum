---
id: b.963
type: bee
title: bees-setup writes machine-local paths to committed CLAUDE.md (## Skill Paths)
status: open
created_at: '2026-04-30T21:14:25.887691'
schema_version: '0.1'
egg: null
guid: 963k6c881x2dj99aaxupsrrx9vdh9jq9
---

## Description

`/bees-setup` resolves the absolute filesystem paths to bundled helper scripts and writes them into a `## Skill Paths` section of the target repo's CLAUDE.md. CLAUDE.md is committed to git, so the absolute paths — which are necessarily machine-local — get pushed to the remote. Any other engineer who clones the repo gets paths under `/Users/<original-author>/.claude/skills/...` (or the equivalent on the original author's OS), which won't exist on their machine.

This was surfaced when `/bees-setup` on this repo wrote:

- **Force clean team script**: /Users/jesseg/.claude/skills/bees-execute/scripts/force_clean_team.py
- **File list resolver script**: /Users/jesseg/.claude/skills/bees-setup/scripts/file_list_resolver.py

into `CLAUDE.md`. Anyone else collaborating on this repo would either (a) hit `Run /bees-setup first.` from the precondition check (because the file paths in their clone don't exist) or (b) see Claude attempt to invoke a path that resolves to nothing and silently no-op.

## Current behavior

1. `/bees-setup` probes `~/.claude/skills/` and `<repo>/.claude/skills/` for the bundled scripts, picks whichever is present, and writes the resolved absolute path verbatim to a `## Skill Paths` section of CLAUDE.md (`skills/bees-setup/SKILL.md:148–172`).
2. `/bees-execute` and `/bees-fix-issue` read the `Force clean team script` value from that section and shell-execute it (`skills/bees-execute/SKILL.md:115,310,318`; `skills/bees-fix-issue/SKILL.md:141,274`).
3. Both skills hard-fail with `Run /bees-setup first.` when the section or its required keys are missing (per project CLAUDE.md `Contract keys` policy).
4. CLAUDE.md is a tracked file. `git add CLAUDE.md` stages the absolute paths; `git push` propagates them.

## Expected behavior

`/bees-setup` should not write any committed file with paths that are valid only on the running machine. The two helper-script lookups should resolve at runtime per-machine, or be persisted in a per-user / gitignored location.

Any path written into a tracked file should either be (a) a relative path within the repo, (b) a `~`-prefixed path that gets expanded at use time, or (c) a portable identifier that downstream skills can resolve themselves.

This isn't covered by the current `docs/sdd.md` or CONTRIBUTING.md commitments (both currently document the broken design as if it's correct — those will need to change as part of the fix; not updated at filing time because the correct design isn't yet decided).

## Impact

**Correctness — multi-engineer.** Any contributor who clones a repo configured by another engineer's `/bees-setup` run gets paths that don't resolve. Worst case the precondition check still passes (paths happen to look syntactically valid) and a `Force clean team script` invocation silently no-ops, leaving stuck Claude Code teams un-cleaned during recovery. Best case the precondition check fails fast with `Run /bees-setup first.` — annoying but recoverable.

**Correctness — single-engineer cross-machine.** Same author working on the same repo from a second machine (e.g., laptop ↔ desktop) hits the same break.

**Privacy / hygiene.** Committing absolute paths leaks the original author's home directory layout to anyone reading the repo (mild — it's just `/Users/<username>/`).

**Recovery friction.** Re-running `/bees-setup` on the broken clone fixes the local file but introduces a meaningless commit (`Skill Paths`-only diff) on every machine swap. With multiple contributors, the file thrashes back and forth in commit history.

## Suggested fix

The fix has multiple plausible shapes; pick one that preserves the design intent (downstream skills can find helper scripts without skill-editing per project) without persisting per-machine state in committed files.

**Candidate approaches** (not ranked — implementer decides):

1. **Runtime probe in each consumer.** Lift the `~/.claude/skills/` vs `<repo>/.claude/skills/` probe code currently in `bees-setup/SKILL.md` (lines around 138–146 in the current revision) into a small preamble that `/bees-execute` and `/bees-fix-issue` run at invocation time, and remove the `## Skill Paths` section from CLAUDE.md entirely. Pros: zero committed per-machine state, single canonical resolver, matches the fact that the path is machine-derived anyway. Cons: every consumer skill duplicates the probe (Python helper script could centralize it).

2. **Per-user override file.** Write Skill Paths to `~/.claude/bees-workflow/skill-paths.json` instead of CLAUDE.md. Pros: per-user by construction. Cons: third state file to reason about; out-of-band from CLAUDE.md contract.

3. **Gitignored side file inside the repo.** Write to `.bees/skill-paths.local` or `.claude/skill-paths.local` and add the file to `.gitignore`. Each contributor runs `/bees-setup` once on clone. Pros: keeps state near the project. Cons: requires modifying `.gitignore` (which `bees-setup` doesn't do today) and risks a contributor accidentally committing the file.

4. **Tilde-prefixed path with shell expansion.** Write `~/.claude/skills/...` (literal tilde) to CLAUDE.md instead of the expanded path; have consumer skills expand `~` / `$HOME` / `$env:USERPROFILE` at use time. Pros: minimal change. Cons: only works if every contributor uses the global install — breaks the per-project install mode.

**Files to modify under any of the above:**

- `skills/bees-setup/SKILL.md` — the section that writes Skill Paths (and the `--egg-resolver` invocation that reuses the resolved path; verify whether that still needs to live in `~/.bees/config.json`, which is per-user and not a leak).
- `skills/bees-execute/SKILL.md` — the four sites that read `Force clean team script` (lines 31, 37, 115, 310, 318).
- `skills/bees-fix-issue/SKILL.md` — the four sites that read `Force clean team script` (lines 21, 27, 141, 274).
- This repo's `CLAUDE.md` — `Contract keys` and the `## Skill Paths` description.
- This repo's `CONTRIBUTING.md` — `Helper scripts` bullet under `Skill conventions`.
- `docs/sdd.md` — `Contract keys` section.
- `docs/doc-writing-guide.md` — `The lookup-key pattern (no hardcoded language commands)` section, which lists `## Skill Paths` keys.

**Migration concern.** Repos already configured by an earlier `/bees-setup` have the broken `## Skill Paths` section already committed. The fix should:

- On re-run, detect a pre-existing `## Skill Paths` with absolute paths and either delete the section (if approach 1 or 2) or rewrite it (if approach 3 or 4).
- Surface a one-line note to the user: "the previous Skill Paths block is being removed/migrated; consider squashing the resulting commit if it lands alongside other work." Don't auto-rewrite git history.

**Adjacent finding (in scope only if cheap):** `/bees-setup` calls `bees colonize-hive --egg-resolver <ABSOLUTE_PATH>` and persists that path in `~/.bees/config.json`. That file is per-user and not committed, so it's not the same leak — but the same root cause means a contributor cloning a repo with in-repo hives still has to re-run `/bees-setup` to register the hive on their machine. Worth a note in the README/CONTRIBUTING.md as part of the fix, even if the underlying behavior doesn't change.
