---
id: b.tsj
type: bee
title: Skills use vague 'search hive' prose without concrete query recipes, causing Claude to invent bees CLI verbs
status: open
created_at: '2026-04-30T21:19:44.483444'
schema_version: '0.1'
egg: null
guid: tsj4y2xj624fqef8o2rzsgk93nyo7p4r
---

## Description

Several skills tell Claude to "search the hive", "find the Bee", "find Epics in `ready` state", etc. — but don't give a concrete `bees` CLI command to run. Claude has to guess the verb. The bees CLI doesn't have an obvious "list tickets in a hive" command (the right answer is `bees execute-freeform-query --query-yaml '...'`), so the guess routinely lands on a non-existent verb like `bees list-tickets`. This was surfaced when running `/bees-file-issue` for the first time — Step 2 ("Check if there's already an issue ticket for this issue (search existing issues hive)") at `skills/bees-file-issue/SKILL.md:55` made the agent guess `bees list-tickets`, which exited 2 with the full subcommand-list dump.

This pattern is exactly what `CONTRIBUTING.md` flags under **Anti-patterns**: "Don't replace concrete shell snippets with vague prose ('run the appropriate test command')." And under **Reviewing changes**: "If you change a CLI invocation, run `bees <command> --help` and verify the flag still exists with the same name." Some skills follow that rule; others don't, and the inconsistency is the bug.

## Current behavior

Some skills DO ship concrete query recipes. These are the good templates:

- `skills/bees-status/SKILL.md:33,38,44` — three working recipes covering all-Plan-Bees, all-Epics-under-Plan-Bees, all-Issue-Bees. Use `report: [...]` clauses for tabular output.
- `skills/bees-fix-issue/SKILL.md:47` — concrete recipe for open-issue discovery in `all` and no-args modes: `[type=bee, hive=issues, status=open]` with `report: [title]`.
- `skills/bees-breakdown-epic/SKILL.md:31` — concrete recipe for finding ready Plan Bees in the no-args path: `[type=bee, hive=plans, status=ready]`.

Other skills DO NOT ship the recipe. These are the bug sites:

- `skills/bees-file-issue/SKILL.md:55` — Step 2 says "Check if there's already an issue ticket for this issue (search existing issues hive)" with no command. Likely Claude needs `[type=bee, hive=issues, status=open]` plus a title-regex filter.
- `skills/bees-plan/SKILL.md:51` — "Check if there's existing work that overlaps (search the plans and issues hives)" with no command. Skill has zero `execute-freeform-query` blocks anywhere.
- `skills/bees-execute/SKILL.md:42-44` — three `## 1. Find Bee to work on` sub-cases ("find all bees for this repo", "find all Epics in the `ready` state that are unblocked", "find the Bee that is a parent of that Epic") with no commands.
- `skills/bees-execute/SKILL.md:79-83` — `## 2. Find Epic to work on and validate` says "Find all Epics in the Bee and recommend the best one" with no command.
- `skills/bees-breakdown-epic/SKILL.md:27` — Bee-ID-given path: "Find workable Epics automatically (see below)" with no command at point of reference.
- `skills/bees-breakdown-epic/SKILL.md:36-37` — `## Once you have a Bee ID`: "Find workable Epics by querying with the `bees` CLI for any Epic children of that Bee in the `drafted` state" — describes the query but doesn't give the recipe.

The good-template recipes also use inconsistent shapes (whether to include `report:`, which fields to project, no canonical recipe template documented anywhere) — fixable as part of this same change.

## Expected behavior

Every ticket-discovery operation in skill prose should ship with a concrete `bees execute-freeform-query --query-yaml '...'` recipe inline at the point of use, in the same labeled OS-conditional shell-block style as the rest of the skill. Claude reads the prose, runs the command exactly, and proceeds — no guessing, no fallback to invented verbs.

A canonical recipe template should also be documented in either `CONTRIBUTING.md` (`Skill conventions` section) or `docs/doc-writing-guide.md` (the new bootstrap doc), with the shape:

```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=<bee|t1|t2|t3>, hive=<name>, status=<value>]
report: [title, ticket_status, ...]'
```

…so future skill authors have a reference and don't drift.

## Impact

**Correctness — agent reliability.** Claude inventing a non-existent CLI verb is a fast-fail in the best case (exit 2 with the help dump, as observed) and a silent wrong-answer in the worst case (e.g., guessing `bees query` and getting unexpected output that looks plausible). Either way, agent runs hit avoidable friction.

**Trust gradient.** Each invented-and-then-corrected command costs the user trust in the workflow. The same agent might later guess a flag that does exist but means the wrong thing — harder to catch.

**Per-skill drift.** Without a canonical recipe template, even skills that DO ship concrete recipes have done so independently and now use slightly different shapes. Future skill edits will continue drifting unless the template is documented.

**Cross-platform.** Vague prose is OS-agnostic, but concrete recipes need to ship as labeled OS-conditional blocks per the `## Cross-platform` rule. The `bees execute-freeform-query` invocation itself is identical on POSIX and PowerShell (single-line trivial), so the existing recipes correctly omit the PowerShell variant. The fix should preserve that — don't add ceremony where it isn't needed.

## Suggested fix

**Phase 1 — fill in the gaps.** For each bug site listed above, write the concrete recipe inline. Specifically:

| Site | Recipe sketch (verify against `bees execute-freeform-query --help` before writing) |
|---|---|
| `bees-file-issue:55` | `[type=bee, hive=issues, status=open]` with `report: [title]` — same shape as `bees-fix-issue:47`. The agent then matches the user's description against returned titles to detect duplicates. |
| `bees-plan:51` | Two queries: `[type=bee, hive=plans]` and `[type=bee, hive=issues, status=open]`, both with `report: [title]`. Agent scans both result sets for overlap with the user's idea. |
| `bees-execute:42-44` | Three recipes: (a) all Plan Bees in this repo: `[type=bee, hive=plans]`. (b) ready+unblocked Epics under a given Bee: needs traversal stage `[parent=<bee-id>, type=t1, status=ready]`, then filter unblocked. (c) parent-Bee-from-Epic: query `[id=<epic-id>]` then `[parent]` stage. |
| `bees-execute:79-83` | All Epics under the chosen Bee: `[parent=<bee-id>, type=t1]` with `report: [title, ticket_status, up_dependencies]`. Then filter in-prose for `ready`/`in_progress` and unblocked dependencies. |
| `bees-breakdown-epic:27,36-37` | All `drafted` Epic children of given Bee: `[parent=<bee-id>, type=t1, status=drafted]`. |

**Phase 2 — canonicalize the template.** Add a `## Querying tickets` (or similarly-named) subsection to `CONTRIBUTING.md` `Skill conventions`, or to `docs/doc-writing-guide.md`. Cover:

- The verb is always `bees execute-freeform-query --query-yaml '<yaml>'`.
- Multi-line YAML in shell is portable across POSIX and PowerShell single-quoted strings (verify on Windows).
- When to include `report:` (when the agent will display or pattern-match results) vs. omit (when the agent only needs ticket IDs to traverse).
- Reference the help text: `bees execute-freeform-query --help` lists all stage filters and graph stages; verify before writing a new recipe.

**Phase 3 — verify existing recipes.** As part of the same change, run each existing recipe (`bees-status:33,38,44`, `bees-fix-issue:47`, `bees-breakdown-epic:31`) against the current `bees` CLI in this repo and verify the output shape still matches what the surrounding prose expects. Recipes that depend on field names (`title`, `ticket_status`, `up_dependencies`, `children`) should be cross-checked against `bees execute-freeform-query --help` for any field renames since the recipes were written.

**Out of scope for this ticket** (potential follow-ups, do not bundle):

- Adding a `bees list-tickets` convenience verb to the upstream bees CLI. That's an upstream change and outside this repo's scope.
- Refactoring the four-skill inventory of recipes into a shared helper script. Each skill currently inlines its recipe; that's fine for now per CONTRIBUTING.md's "don't proliferate bundled scripts" anti-pattern.

## Adjacent finding (note, do not bundle)

`CONTRIBUTING.md` already calls this exact failure mode out under **Anti-patterns**:

> **Don't replace concrete shell snippets with vague prose** ("run the appropriate test command"). Concrete commands per OS keep agent reliability up — vague prose forces the agent to guess and often guesses wrong.

…and under **Reviewing changes**:

> If you change a CLI invocation, run `bees <command> --help` and verify the flag still exists with the same name.

The rules are documented; some skills just don't follow them. The fix is enforcement (Phase 1), not new rules. Phase 2 (canonical template) is a supplement, not a contradiction.
