---
name: bees-plan
description: Interactive feature planning — explore scope, update docs if needed, create a Plan Bee with Epics ready for /bees-breakdown-epic and /bees-execute.
argument-hint: "[<description>]"
---

## Overview

This skill handles the full journey from "I have an idea" to "here's a broken-down plan ready for execution." It supports features of any size — from adding Helm charts to a new RPC endpoint.

> **Tip:** if you already have a finalized PRD and SDD on disk that describe a **single feature**, `/bees-plan-from-specs <prd-path> <sdd-path>` is the faster path — it skips the discovery and scope-iteration phases and goes straight to Plan Bee creation. If your PRD/SDD are cumulative (one or more prior `### Feature:` subsections already present) and you want to re-plan exactly one of those subsections, `/bees-plan-from-specs <prd-path> <sdd-path> --feature "<title>"` is the express scoped form — it bypasses the multi-feature guard and reads only the matching `### Feature: <title>` subsection from each doc. Use `/bees-plan` (this skill) when you're starting from an idea or rough notes, or when you're adding a brand-new feature to a cumulative PRD/SDD. `/bees-plan-from-specs` without `--feature` hard-fails on multi-feature docs to avoid re-planning previously-planned features.

### Usage

- `/bees-plan` — interactive: start a conversation about what you want to build
- `/bees-plan <description>` — start with a description and refine from there

## Workflow

### 1. Gather Context from the User FIRST

**Before doing any research or asking pointed questions**, ask the user as plain prose (no tool call — this is an open-ended question, not a multi-choice one) if there's additional context you should know:

> Before I start researching, is there anything I should know? For example: reference implementations, existing services to look at, design constraints, related repos, prior art, or anything else that would help me plan this well.

Wait for the user's reply in their next turn. They may point you to:
- An existing deployed service to use as reference
- A specific repo, directory, or file with relevant patterns
- Design constraints or team preferences
- Prior discussions or decisions

Incorporate whatever they share into ALL subsequent research and questions.

### 2. Explore and Understand

Now research — informed by the user's context from step 1.

**If called with a description**, use it as the starting point.

**If called without arguments**, ask: "What feature or capability do you want to add?"

**Check for existing docs:** Look for a PRD and SDD in the repo (check CLAUDE.md for paths, or look in `docs/`). If they don't exist and CLAUDE.md doesn't reference them, ask the user:

- "Does this project have a PRD or SDD (Software Design Document)? It's totally fine if not — I can plan the feature without them. The scope will live in the Plan Bee itself."

If the user provides paths, read them. If they say no or the docs don't exist, skip all doc-related steps later (step 4) and note that the Plan Bee body is the authoritative scope document.

Research (incorporating the user's context):
- Read CLAUDE.md to understand the project structure and conventions
- Read relevant source code to understand the current state
- If the user pointed to reference implementations, read those
- Check if there's existing work that overlaps. Query both hives and scan returned titles for related scope:

  ```bash
  # All Plan Bees in the plans hive (any status — overlap may be planned, in-progress, or done):
  bees execute-freeform-query --query-yaml 'stages:
    - [type=bee, hive=plans]
  report: [title, ticket_status]'

  # All open issues:
  bees execute-freeform-query --query-yaml 'stages:
    - [type=bee, hive=issues, status=open]
  report: [title]'
  ```

  If overlap looks meaningful, `bees show-ticket --ids <id>` on the candidate(s) and discuss with the user whether to extend an existing Bee, depend on it, or proceed with a separate Plan.
- If PRD/SDD exist, read them to understand if this feature relates to existing requirements

Then ask the following clarifying questions as a numbered prose list in a single message — no `AskUserQuestion` call; these are open-ended and the user will answer them in their reply:

1. What problem does this solve?
2. What's the scope? (minimum viable vs full vision)
3. Are there constraints or preferences? (technology choices, timeline, etc.)
4. Any dependencies on other work?

**Do not proceed until you and the user agree on what the feature is.**

### 3. Define Scope

Write a clear scope statement that includes:
- **What**: one paragraph describing the feature
- **Why**: the motivation
- **Acceptance criteria**: concrete, testable conditions for "done"
- **Out of scope**: explicitly list what this does NOT include

Present the scope to the user with `AskUserQuestion`:
- "Does this scope look right?"
- Options: "Yes, proceed" / "Needs changes" / "Let's discuss more"

Iterate until the user approves.

### 4. Determine Doc Updates

First, check whether the project has PRD/SDD configured in CLAUDE.md `## Documentation Locations` (rows "Project requirements doc (PRD)" and "Internal architecture docs (SDD)"). The two paths from there determine which branch you take below.

#### 4a — If PRD/SDD exist

Categorize the feature and determine what needs updating:

| Feature type | PRD update? | SDD update? | README update? | Example |
|---|---|---|---|---|
| **Product feature** (new endpoint, behavior change, user-facing) | Yes | Yes | Yes — if it changes user-facing behavior, config, or setup | "Add CSV export" |
| **Architecture/reliability** (perf, caching, retry logic) | No | Yes | Only if it changes config or operational behavior | "Add auth retries" |
| **Deployment/infra** (Helm, CI, monitoring) | No | SDD deployment section only | Yes — if it changes setup, config, or deployment instructions | "Add Helm charts" |
| **CI/testing infra** (smoke tests, test helpers) | No | No | No | "Add K8s smoke tests" |
| **Internal refactor** (code quality, dedup) | No | No | No | "Extract shared test helpers" |

**Always check the README.** Even when PRD/SDD updates are not needed, review the customer-facing docs (referenced in CLAUDE.md under "Documentation Locations") for any Getting Started, Configuration, or Deployment sections affected by the feature. Missing a README update means users hit outdated instructions.

If updates are needed:
1. Draft the updates (PRD, SDD, and/or README) — for PRD/SDD, **add a new "Feature: <title>" subsection under the existing "Per-feature scope" / "Per-feature design" headers** rather than overwriting earlier content. The docs are cumulative across features.
2. Show them to the user for approval
3. Apply them to the doc files
4. The Plan Bee's `egg` field will reference the updated docs

If no doc updates are needed:
- The PM in `/bees-execute` will still reference the existing PRD/SDD as the spec source for drift detection.

#### 4b — If PRD/SDD don't exist

This typically means the user picked "Defer" or "Skip permanently" during `/bees-setup`'s bootstrap question. You have two options to surface to the user via `AskUserQuestion`:

1. **Create PRD and SDD now from this feature's scope** *(recommended for projects you expect to grow)*. Seed the PRD from the scope statement (Step 3); seed the SDD with a "Current architecture" section drawn from what you learned exploring the codebase in Step 2 (or a stub on greenfield) plus a "Feature: <title>" design section. Write `docs/prd.md` and `docs/sdd.md`, update CLAUDE.md `## Documentation Locations` to point at them, then continue with Step 5.

   *If you'd prefer comprehensive baseline docs covering the whole project rather than just this feature*, suggest the user run `/bees-setup` first — its bootstrap subsection does a deep codebase exploration and structured Q&A to produce starter docs that describe the project as a whole. Then re-invoke `/bees-plan`.

2. **Skip — body-as-spec for this feature** — Plan Bee body becomes the authoritative scope document; `egg` stays null. Note honestly: this means the Plan Bee is its own island. Future features won't have a cumulative project spec to anchor against; PMs in `/bees-execute` and `/bees-fix-issue` won't see what this feature established. Fine for one-off features or throwaway work; risky for multi-feature projects.

Use this content for the seeded PRD if option 1 is chosen (write to `docs/prd.md`):

```markdown
# <Project name> — Product Requirements

## Existing scope

<One-paragraph summary of what the project currently does, drawn from
Step 2's codebase exploration. On greenfield, write "(this is a new
project; the first feature below is its initial scope)".>

## Per-feature scope

### Feature: <feature title>

<From Step 3's scope statement: What, Why, Acceptance criteria, Out of scope.>
```

Use this content for the seeded SDD (write to `docs/sdd.md`):

```markdown
# <Project name> — Software Design

## Current architecture

<Paragraph(s) describing what Step 2 learned about the codebase: stack,
key components, patterns. On greenfield, write "(this is a new project
with no existing code; architecture decisions will be added as features
are designed)".>

## Per-feature design

### Feature: <feature title>

<Architectural decisions for this feature: how it fits into the existing
architecture (or establishes new structure on greenfield), key components
introduced or modified, external dependencies added.>
```

Create `docs/` if it doesn't exist:

```bash
# POSIX (bash / zsh):
mkdir -p docs

# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path docs | Out-Null
```

After writing the files, update CLAUDE.md `## Documentation Locations`:
- Set "Project requirements doc (PRD)": `docs/prd.md`
- Set "Internal architecture docs (SDD)": `docs/sdd.md`

### 5. Create Plan Bee with Epics

Create the Plan Bee inline in this session — do **not** delegate to `/bees-plan-from-specs`. That skill assumes the PRD/SDD describe exactly one feature; this skill drives the cumulative-PRD pattern where each invocation appends a new `### Feature:` subsection, so delegating after Step 4 would re-plan every previously-planned feature in the cumulative docs. Inline creation here is the single supported path regardless of whether PRD/SDD exist — the only difference is whether the Plan Bee's `egg` field is populated (PRD/SDD exist) or omitted (no PRD/SDD).

#### 5a — Create the Plan Bee

Author the scope statement to a temp file via the `Write` tool first, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt, and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both. Use a path under the OS temp dir (`/tmp/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\bees-body-<short-suffix>.md` on Windows), and remove the temp file after the bees command exits.

The body should be a brief 2-3 sentence summary of the goal and scope. When `egg` is set, do not dump PRD/SDD content into the body — downstream skills read the linked docs via the egg resolver.

**If PRD/SDD exist for this feature** (Step 4a, or Step 4b option 1 where you just drafted them), set `--egg` to a JSON array containing the absolute PRD and SDD paths in that order:

```
["<absolute path to PRD>", "<absolute path to SDD>"]
```

The egg resolver configured by `/bees-setup` validates these paths downstream. If it is not configured, direct the user to run `/bees-setup` first.

```bash
# POSIX (bash / zsh) — with PRD/SDD egg:
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status drafted \
  --title "<feature title>" \
  --body-file <path> \
  --egg '["<absolute prd path>", "<absolute sdd path>"]'

# Windows (PowerShell) — with PRD/SDD egg:
bees create-ticket `
  --ticket-type bee `
  --hive plans `
  --status drafted `
  --title "<feature title>" `
  --body-file <path> `
  --egg '["<absolute prd path>", "<absolute sdd path>"]'
```

**If no PRD/SDD exist for this feature** (Step 4b option 2 — body-as-spec), omit `--egg` entirely. The Plan Bee body becomes the authoritative scope document, so make it detailed enough that the PM in `/bees-execute` can use it for drift detection.

```bash
# POSIX (bash / zsh) — no egg:
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status drafted \
  --title "<feature title>" \
  --body-file <path>

# Windows (PowerShell) — no egg:
bees create-ticket `
  --ticket-type bee `
  --hive plans `
  --status drafted `
  --title "<feature title>" `
  --body-file <path>
```

Mark the Plan Bee as `drafted` initially — its children (Epics) have not been written yet. Step 5d below promotes it to `ready` once Epics exist.

#### 5b — Break the feature into Epics

Use the same Epic-decomposition rules as `/bees-plan-from-specs` Step 3:

- **Every Epic must leave the codebase green.** All existing tests must still pass after the Epic is complete. Non-negotiable.
- **One Epic = one outcome.** A single coherent user- or system-visible capability. Avoid Epics organized by system layer (no "Database Epic", "API Epic", "UI Epic", "Documentation Epic", "Testing Epic"). Prefer capability slices like "User performs action and receives feedback" or "System handles error and retry behavior".
- **Decompose vertically by capability.** Each Epic delivers end-to-end behavior and is independently testable and demo-able.
  - *Exception — technical refactors.* For pure infrastructure or refactor work, strict vertical slicing may not apply. Pure-tech Epics are allowed provided they leave the codebase green. Go vertical as soon as possible: after foundational Epics, each subsequent Epic should add a demonstrable capability. Bundle infrastructure each slice needs into that slice rather than separating into layer Epics.
- **Granularity.** Make Epics as granular as possible while preserving a single coherent outcome and a vertical slice per Epic. It's OK to have many Epics — each one should be small enough to celebrate when it lands.
- **Acceptance Criteria.** Each Epic needs concrete, testable acceptance criteria. Either describe the artifact the user can interact with and the steps they take to validate, or describe how the agent itself will demonstrate completion. "Server starts on http://localhost:8000" is good; "Server is available for use" is bad.

**Epic Viability Checklist** (apply to each Epic before creating it):

- [ ] No standalone testing Epic — testing is folded into the Epic where the work is done.
- [ ] No standalone documentation Epic — documentation is folded into the Epic where the work is done.
- [ ] Epics that change config, behavior, or deployment include README/customer-facing doc updates in their scope (not deferred to a separate doc Epic).

**Anti-patterns to detect:**

- Epic chain where intermediate states are untestable.
- Mixing pervasive refactor with feature work in one Epic.

If the plan is small, one Epic is fine — don't pad the plan with more.

#### 5c — Present Epics for review

Before creating any Epic tickets, present the full proposed Epic list to the user as markdown — title, description, dependencies for each. Use `AskUserQuestion` with options:

- "Yes, create them"
- "Modify the Epics"
- "Cancel"

Wait for approval. If the user picks "Modify the Epics", iterate in prose until they approve, then re-prompt with `AskUserQuestion`.

#### 5d — Create Epic tickets and wire dependencies

Create each approved Epic as a `t1` child of the Plan Bee with status `drafted`. Use the same temp-file + `--body-file` pattern as in 5a (author body, pass path, remove temp file). **Do not pass `--egg` on Epics** — the bees CLI accepts `--egg` only on top-level Bees and hard-errors on child tiers. Downstream skills trace Epics back to PRD/SDD via the parent Plan Bee's egg, not the Epic's.

```bash
# POSIX (bash / zsh):
bees create-ticket \
  --ticket-type t1 \
  --hive plans \
  --parent <bee-id> \
  --status drafted \
  --title "<epic title>" \
  --body-file <path>

# Windows (PowerShell):
bees create-ticket `
  --ticket-type t1 `
  --hive plans `
  --parent <bee-id> `
  --status drafted `
  --title "<epic title>" `
  --body-file <path>
```

After all Epics exist, analyze blocking relationships and set `up_dependencies` between them. Common patterns:

- Infrastructure blocks features (backend API must exist before features that use it).
- Foundation blocks UI (data models/services block UI components that display them).
- Data input blocks processing (upload/import blocks features that process the data).
- Auth blocks protected features.

For each Epic, ask: "What must be completed before this Epic can be worked on?"

Once dependencies are wired, promote the Plan Bee from `drafted` to `ready` (its children — Epics — are now written, even though the Epics' children — Tasks — are not).

#### 5e — Report

Output a markdown summary listing the Plan Bee, each Epic (ID, title, status, dependencies), and any dependency relationships created.

### 6. Offer Next Steps

Present the user with options.

Note above the options: each downstream skill re-reads the Plan Bee, Epics, and CLAUDE.md from the bees CLI and disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives `/bees-breakdown-epic` (and later `/bees-execute`) full context budget for per-Task body authoring and review cycles. Same-session continuation is acceptable as an opt-in for small Bees with one or two Epics.

- **In a fresh session, break down now** (Recommended) — run `/bees-breakdown-epic <bee-id>` in a new Claude Code session to break Epics into Tasks/Subtasks
- **In a fresh session, execute now** — run `/bees-execute <bee-id>` in a new session to start building immediately
- **Continue in this session: break down now** — load `bees-breakdown-epic` and break Epics into Tasks/Subtasks now. Reasonable only for small Bees with one or two Epics
- **Continue in this session: execute now** — load `bees-execute` and start building now. Reasonable only for small Bees with one or two Epics
- **Review first** — let the user review the plan before proceeding
- **Done for now** — plan is saved, user will come back later

### 7. Commit

Stage and commit all changes — doc updates and the Plans hive's ticket files. **Do not hardcode the `.bees/plans/` path.** `/bees-setup` lets the user choose where each hive lives — in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/plans/` silently stages nothing when the user picked a sibling path.

Resolve the Plans hive path via `bees list-hives`, check whether it lives inside the current git repo, and only stage it if it does:

```bash
# POSIX (bash / zsh):
plans_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="plans"), None); print(p or "")')
repo_root=$(git rev-parse --show-toplevel)
git_add_args="docs/"
case "$plans_path" in
  "$repo_root"|"$repo_root"/*) git_add_args="$git_add_args $plans_path" ;;
esac
git add $git_add_args
git commit -m "Plan feature: <title>"
```

```powershell
# Windows (PowerShell):
$plansPath = (bees list-hives | ConvertFrom-Json).hives | Where-Object { $_.normalized_name -eq 'plans' } | Select-Object -ExpandProperty path
$repoRoot = git rev-parse --show-toplevel
# Normalize separators — git rev-parse returns forward slashes on Windows;
# bees list-hives may return backslashes. Compare both sides on the same form.
$plansNorm = if ($plansPath) { $plansPath.Replace('\','/') } else { '' }
$repoNorm = $repoRoot.Replace('\','/')
$addArgs = @('docs/')
if ($plansNorm -and ($plansNorm -eq $repoNorm -or $plansNorm.StartsWith("$repoNorm/"))) {
  $addArgs += $plansPath
}
git add @addArgs
git commit -m "Plan feature: <title>"
```

If the Plans hive lives outside the repo, commit the doc/ changes here and remind the user that the Plan Bee ticket is stored separately (the bees CLI persists it; no git tracking needed for the ticket file itself). If `docs/` was not modified during this run, drop it from the `add` list as well.

### Important Notes

- This skill is **interactive** — it's a conversation, not a batch process
- Do NOT skip the scope approval step — the user must confirm before creating tickets
- If the feature is simple enough to be a single Epic with no doc changes, that's fine — don't over-engineer the plan
- If the feature is actually an issue (something that should work but doesn't), suggest `/bees-file-issue` instead
- The Plan Bee body IS the spec for features that don't warrant PRD/SDD updates — make it detailed enough that the PM in /bees-execute can use it for drift detection
