---
name: bees-plan
description: Interactive feature planning — explore scope, update docs if needed, create a Plan Bee with Epics ready for /bees-breakdown-epic and /bees-execute.
argument-hint: "[<description>]"
---

## Overview

This skill handles the full journey from "I have an idea" to "here's a broken-down plan ready for execution." It supports features of any size — from adding Helm charts to a new RPC endpoint.

> **Tip:** if you already have a finalized PRD and SDD on disk, `/bees-plan-from-specs <prd-path> <sdd-path>` is the faster path — it skips the discovery and scope-iteration phases and goes straight to Plan Bee creation. Use `/bees-plan` (this skill) when you're starting from an idea, rough notes, or anything earlier than a finalized spec.

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

There are two paths depending on whether docs got drafted in Step 4. Pick the one that matches your state.

**Path A — PRD and SDD got drafted/updated in Step 4 (or already existed at the start).**

Delegate to `/bees-plan-from-specs <absolute-prd-path> <absolute-sdd-path>`. That skill handles the Plan Bee creation, the full Epic decomposition rules (vertical slicing, Epic Viability Checklist, anti-patterns), the dependency wiring, and chains into `/bees-breakdown-epic` automatically. It produces the same artifact (Plan Bee + Epics in the Plans hive) you'd build by hand here.

Why delegate: `/bees-plan-from-specs` is the canonical home for the "specs → Plan Bee" logic. Delegating keeps a single source of truth and gives you the better Epic-decomposition guidance for free.

After it returns, skip directly to Step 7 (commit) below — Step 6 (Offer Next Steps) is also handled by `/bees-plan-from-specs`'s chain into `/bees-breakdown-epic`.

**Path B — no PRD/SDD exist for this feature (the Plan Bee body is the authoritative spec).**

Create the Plan Bee directly in the Plans hive with `egg=null`:

```bash
# POSIX (bash / zsh):
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status ready \
  --title "<feature title>" \
  --body "<scope statement with acceptance criteria>"
  # no --egg flag; egg stays null

# Windows (PowerShell):
bees create-ticket `
  --ticket-type bee `
  --hive plans `
  --status ready `
  --title "<feature title>" `
  --body "<scope statement with acceptance criteria>"
  # no --egg flag; egg stays null
```

Then break the feature into Epics. Use the **same Epic-decomposition rules** as `/bees-plan-from-specs` Step 3:
- Every Epic must leave the codebase green (all existing tests still pass).
- One Epic = one outcome (a single coherent user-or-system-visible capability; not a layer like "DB Epic" / "API Epic").
- Decompose vertically by capability — each Epic delivers end-to-end behavior. Pure-tech refactors are an exception but should go vertical as soon as possible.
- Make Epics as granular as possible while preserving a single coherent outcome per Epic.
- Each Epic needs concrete, testable Acceptance Criteria a user can verify or an agent can demonstrate.

Create each Epic as a child of the Plan Bee:

```bash
# POSIX (bash / zsh):
bees create-ticket \
  --ticket-type t1 \
  --hive plans \
  --parent <bee-id> \
  --status drafted \
  --title "<epic title>" \
  --body "<epic scope and acceptance criteria>"

# Windows (PowerShell):
bees create-ticket `
  --ticket-type t1 `
  --hive plans `
  --parent <bee-id> `
  --status drafted `
  --title "<epic title>" `
  --body "<epic scope and acceptance criteria>"
```

After all Epics exist, set `up_dependencies` between them where blocking relationships apply, then mark the Plan Bee `ready` (its children — the Epics — are now written, even though the Epics' children — Tasks — are not).

### 6. Offer Next Steps

Present the user with options.

Note above the options: each downstream skill re-reads the Plan Bee, Epics, and CLAUDE.md from the bees CLI and disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives `/bees-breakdown-epic` (and later `/bees-execute`) full context budget for per-Task body authoring and review cycles. Same-session continuation is acceptable as an opt-in for small Bees with one or two Epics.

- **In a fresh session, break down now** (Recommended) — run `/bees-breakdown-epic <bee-id>` in a new Claude Code session to break Epics into Tasks/Subtasks
- **In a fresh session, execute now** — run `/bees-execute <bee-id>` in a new session to start building immediately
- **Continue in this session: break down now** — load `bees-breakdown-epic` and break Epics into Tasks/Subtasks now. Reasonable only for small Bees with one or two Epics
- **Continue in this session: execute now** — load `bees-execute <bee-id>` and start building now. Reasonable only for small Bees with one or two Epics
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
