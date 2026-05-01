---
id: b.ap8
type: bee
title: 'bees-setup post-b.963: $RESOLVER lost across shell calls; ## Skill Paths deletion has no concrete procedure'
status: open
created_at: '2026-04-30T21:56:50.855421'
schema_version: '0.1'
egg: null
guid: ap8e4xtx9q63b6bijdkxo3dzuu2mr5yc
---

## Description

Two follow-up findings on the b.963 fix (commit f2cbba7) in `skills/bees-setup/SKILL.md`. Both surfaced during code review of f2cbba7. Bundled per the workflow's house style (same file, same commit, same migration-from-`## Skill Paths` theme).

---

## Finding A — `$RESOLVER` shell variable doesn't survive across separate Bash tool invocations

### Current behavior

`skills/bees-setup/SKILL.md` `### Egg Resolver` (line 152, plus a sibling PowerShell block ~160) sets `$RESOLVER` to the egg-resolver script path:

```bash
RESOLVER=\"<bees-setup-base-dir>/scripts/file_list_resolver.py\"
test -f \"\$RESOLVER\" || { echo \"...\"; exit 1; }
```

Then 60+ lines later, in `### Hive Configuration / #### Create or validate` (lines 215, 217), the colonize-hive call references `--egg-resolver \"\$RESOLVER\"`:

```bash
bees colonize-hive --name <name> --path <path> --scope \"<scope>\" --egg-resolver \"\$RESOLVER\"
```

Each Bash tool call in Claude Code is a fresh shell — environment variables do not persist between calls (CONTRIBUTING.md and the harness docs both note this). The agent typically runs:

1. \"Set RESOLVER\" snippet (Bash call #1).
2. Python one-liner that updates `~/.bees/config.json` for existing hives (Bash call #2 — uses `\$RESOLVER` from arg).
3. `bees colonize-hive` for each missing hive (Bash call #3+ — `\$RESOLVER` is empty here).

### Expected behavior

`bees colonize-hive` receives the actual resolved path to `file_list_resolver.py`, regardless of shell-call boundaries.

### Impact

**Silent regression.** `bees colonize-hive ... --egg-resolver \"\"` runs successfully and registers the hive with `egg_resolver = \"\"`. The break only manifests later when `/bees-execute` or `/bees-breakdown-epic` tries to resolve a Plan Bee's `egg` field — at which point eggs return nothing and downstream skills silently miss their PRD/SDD inputs. Symptoms appear far from the cause.

Pre-b.963, the egg-resolver path was hardcoded into the colonize-hive snippet via CLAUDE.md lookup — load-bearing. The b.963 fix removed the lookup but didn't substitute anything that survives shell-call boundaries.

### Suggested fix

Pick one (implementer's call):

1. **Inline the literal path.** Substitute `<bees-setup-base-dir>/scripts/file_list_resolver.py` directly into the colonize-hive snippet — matches how `bees-execute` and `bees-fix-issue` reference `force_clean_team.py` (literal `<base>/scripts/...` path the agent fills in from the skill invocation header). No shell variable.
2. **Set RESOLVER inline.** Add `RESOLVER=\"<bees-setup-base-dir>/scripts/file_list_resolver.py\"` immediately above each colonize-hive call, in the same code fence.
3. **Combine the call.** Restructure so the colonize-hive call and the `$RESOLVER` set share one fenced block (single Bash tool invocation).

Approach #1 is most consistent with the pattern that b.963 introduced everywhere else.

### Files to modify

- `skills/bees-setup/SKILL.md:215` (prose mentioning `--egg-resolver \"\$RESOLVER\"`)
- `skills/bees-setup/SKILL.md:217` (the colonize-hive bash snippet)

**Cross-platform.** The colonize-hive snippet is currently bash-only — no PowerShell variant. Single-line `bees ...` commands are technically allowed to omit the PowerShell variant per CONTRIBUTING.md (\"if and only if the syntax is identical\"), but the new `\"\$RESOLVER\"` coupling makes the syntax PowerShell-incompatible across shell-call boundaries the same way. Add a PowerShell variant as part of the same fix.

---

## Finding B — Migration prose deletes legacy `## Skill Paths` from CLAUDE.md with no concrete deletion procedure

### Current behavior

`skills/bees-setup/SKILL.md:137`:

> If the target repo's CLAUDE.md still has a `## Skill Paths` section from an earlier setup run, delete it as part of this run — the section is no longer used by any skill, and leaving it behind keeps the broken paths in git history. After deletion, mention to the user: \"Removed obsolete `## Skill Paths` section from CLAUDE.md — paths are now resolved at runtime per-machine. Consider squashing this change with other in-flight work; don't push the delete on its own if the section was already pushed earlier.\"

No shell snippet. No Python one-liner. No boundary specification. The agent has to invent its own deletion approach.

This is the exact \"vague prose forces the agent to guess\" anti-pattern that b.tsj was filed for and the b.tsj fix (commit 861e49f) just landed against — except b.tsj covered query recipes, and this is the same class of bug on a file-edit operation.

### Expected behavior

The skill ships a concrete, safe deletion procedure (POSIX + Windows variants per project convention) that the agent can run verbatim.

### Impact

**Risk of clobbering adjacent CLAUDE.md content.** Common failure modes for an agent-invented deletion:

- A `## ` heading inside a fenced code block (e.g., this issue ticket itself) gets treated as a real section boundary, and the deletion eats more or less than intended.
- A user with non-standard section ordering has content between `## Skill Paths` and the next major heading that gets removed along with the section.
- The deletion uses `sed -i` on POSIX (works on GNU sed) vs. `sed -i ''` on macOS (BSD sed) — wrong flag silently writes a backup file or corrupts the source.
- The agent uses a regex without `re.MULTILINE` and matches `^## ` only at the start of the file.

The b.963 issue body explicitly called for safe deletion under \"Migration concern\":

> On re-run, detect a pre-existing `## Skill Paths` with absolute paths and either delete the section ... or rewrite it. Surface a one-line note to the user ... Don't auto-rewrite git history.

The current prose has the user-note part right, but skipped the safe-deletion part.

### Suggested fix

Ship a Python one-liner (POSIX + Windows variants per the project pattern) that:

1. Reads CLAUDE.md.
2. Splits the file on `^## ` boundaries (regex with `re.MULTILINE`).
3. Drops the block whose heading is exactly `## Skill Paths`.
4. Writes the result back atomically (tempfile + rename, not in-place edit).

Matches the JSON-edit pattern already used elsewhere in the same skill and codified in CONTRIBUTING.md (\"Use a Python one-liner with json.load/json.dump, not prose-text-edit instructions ... Direct text editing has no atomicity story and corrupts the file on a wrong escape\").

### Files to modify

- `skills/bees-setup/SKILL.md:137` (replace the one-line \"delete it\" prose with a labeled OS-conditional snippet pair).

---

## Common context

Both findings landed in the same b.963 fix (commit f2cbba7) and live in `skills/bees-setup/SKILL.md`. Both are about the migration logic that replaced the pre-b.963 `## Skill Paths` mechanism. A single agent fixing them shares the same context (CONTRIBUTING.md anti-patterns, the b.963 issue body, the Python-one-liner JSON-edit pattern), so bundling avoids the per-ticket re-load cost.

Out of scope (do not bundle): any of the prose touching `bees-execute` / `bees-fix-issue` `force_clean_team.py` resolution. Those sites also use `<base>/...` literal paths and don't suffer the variable-scoping bug — verified during the same review.
