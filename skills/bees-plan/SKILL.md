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

### 4. Author Specs

Step 4 anchors the feature's PRD and SDD as ticketed artifacts in the Specs hive rather than writing them directly to project docs at planning time. The flow is: (a) detect or create a **Spec Bee** that holds the PRD and SDD as `t1=Doc` children, (b) invoke `/bees-write-prd` and `/bees-write-sdd` via the Skill tool to author those children (sibling Subtask), (c) promote the Spec Bee from `drafted` to `ready` once both writers return successfully (sibling Subtask). The rationale: ticketed specs let `/bees-plan` run side-effect-free against project docs (planning a feature without executing it leaves `docs/prd.md` / `docs/sdd.md` untouched), and they let multiple unrelated features be planned in parallel without their spec edits stepping on each other.

#### 4a — Detect or create the Spec Bee

**Detection.** Re-running `/bees-plan` for the same feature must reuse an existing Spec Bee rather than create a duplicate. Query the Specs hive for `bee`-tier tickets and inspect the result for one whose title matches the feature title from Step 3:

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=specs]
report: [ticket_id, title, ticket_status]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=specs]
report: [ticket_id, title, ticket_status]'
```

Match the feature title against the returned `title` field. Exact-equal-after-normalization (lowercase, collapse whitespace, strip leading/trailing punctuation) is the recommended default; you may tighten or loosen the heuristic so long as it does not silently create a duplicate. **Err toward reuse:** if the heuristic is ambiguous — close-but-not-exact title, prior Spec Bee that might cover this feature, etc. — surface the candidate to the user with `AskUserQuestion` rather than skipping detection. A duplicate Spec Bee is cheap to fix manually after the fact; a missed reuse opportunity is silent corruption that fragments the PRD/SDD across two Spec Bees and is easy to overlook. Future maintainers should not tighten this heuristic into something stricter without preserving the user-facing reuse-or-create prompt.

**Match found — confirm with user.** When a candidate Spec Bee is found, present it via `AskUserQuestion` with these finite choices:

- `Reuse existing Spec Bee` — capture the existing Spec Bee ID from the freeform-query result and proceed to the writer-skill invocations sub-step. The PRD/SDD writer skills are themselves idempotent against existing `t1=Doc` children under the Spec Bee, so reuse cleanly cascades into update-rather-than-duplicate behavior on the children.
- `Create a new Spec Bee anyway` — fall through to the create branch below. Use this when the user really does want a fresh ticket (e.g., the prior Spec Bee was for a superseded scope and they want to start clean).
- `Cancel` — abort the run. The user can resume later by re-invoking `/bees-plan`.

**No match — create.** Author the Spec Bee body to a temp file under `<tempdir>/.bees-workflow/` per the scratch-file convention (do not delete after; the OS reclaims `<tempdir>` on its own cadence), then call `bees create-ticket`. The body should be a brief 2-3 sentence summary of the feature scope, paraphrased from the Step 3 scope statement — substantive PRD/SDD content lands in the `t1=Doc` children, **not** the Spec Bee body itself. Do NOT dump full PRD or SDD content into the Spec Bee body.

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.bees-workflow
# then write the body to /tmp/.bees-workflow/bees-spec-body-<short-suffix>.md via the Write tool
bees create-ticket --ticket-type bee --hive specs --status drafted --title "<feature title>" --body-file <path>
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
# then write the body to $env:TEMP\.bees-workflow\bees-spec-body-<short-suffix>.md via the Write tool
bees create-ticket --ticket-type bee --hive specs --status drafted --title "<feature title>" --body-file <path>
```

**Do not pass `--reference-materials` on the Spec Bee.** The Spec Bee's children — the PRD and SDD `t1=Doc` tickets — are themselves the reference materials. The Spec Bee is its own anchor for downstream `bees`-resolver lookups; downstream skills (Plan Bee creation in Step 5, `/bees-execute`'s PM role) trace from the Plan Bee's `reference_materials` array (which carries the Spec Bee ID via the `bees` resolver) into the Spec Bee and from there to its `t1=Doc` children.

Capture the Spec Bee ID returned by `bees create-ticket` (or the existing ID from the reuse branch) — it is consumed by the writer-skill invocations sub-step (next sibling Subtask) and the Spec Bee promotion sub-step (final sibling Subtask).

#### 4b — Author the PRD and SDD via the writer skills

With the Spec Bee ID in hand from sub-step 4a, delegate the actual PRD and SDD authoring to `/bees-write-prd` and `/bees-write-sdd`. Invoke both skills inline through the Skill tool — `/bees-plan` does not author PRD/SDD content directly, and it does not call `bees create-ticket` or `bees update-ticket` for the `t1=Doc` PRD/SDD child tickets. The writer skills handle child-ticket creation, body assembly, the user-facing approval gates, and the `drafted → ready` transition on their own children. Step 4 here only owns the Spec Bee parent.

**Args payload — identical for both writer skills.** The two writer skills publish a deliberately mirrored input contract (see `skills/bees-write-prd/SKILL.md` `## Inline invocation via the Skill tool` and the matching section in `skills/bees-write-sdd/SKILL.md`) so this sub-step can dispatch them with the same `args` string. Build the payload once and reuse it verbatim across both calls. **Divergence between the PRD and SDD `args` payloads is a defect** — keep them byte-identical; if the user clarifies scope between the two calls (e.g., during the PRD's approval gate), abort and re-author both rather than letting the SDD see a different payload than the PRD did.

The `args` string is free-text, in the shape documented by both writer SKILL.md contract sections:

```
spec-bee-id: <spec-bee-id captured in 4a>

distilled-scope:
<markdown block carrying the conversation-distilled scope>
```

The `distilled-scope` block MUST cover, at minimum, the conversation-distilled scope statement from Step 3 (What / Why / Acceptance criteria / Out of scope) plus any prior-context the user shared in Step 1 (reference implementations, existing services, design constraints, related repos, prior art). Multi-paragraph markdown with headed sub-sections is welcome. The caller is encouraged to also include any rationale, rejected alternatives, or open questions that came up during the planning conversation, since the writer skills route that content into their respective rationale / decisions / open-questions sections.

**Step 1 — invoke `/bees-write-prd`.** Call the Skill tool with `skill="bees-write-prd"` and the `args` string built above. The writer skill parses the payload, takes its distill branch (guaranteed by the inline-invocation contract since this sub-step always passes substantive scope), surfaces its own user-facing approval gates, creates or updates the PRD `t1=Doc` child under the Spec Bee, and on success transitions the PRD child from `drafted` to `ready`. Capture from the writer's structured return message:

- `prd_ticket_id` — the PRD ticket ID (the `t1=Doc` child titled `PRD` under the Spec Bee).
- `prd_status` — the final status (`ready` on approve, `drafted` on cancel).
- `action` — `created` for a new PRD, `updated` for the idempotent reuse path.

**Step 2 — invoke `/bees-write-sdd`.** Only after `/bees-write-prd` returns successfully (i.e., `prd_status` is `ready`), call the Skill tool with `skill="bees-write-sdd"` and the **same** `args` string used for `/bees-write-prd`. Sequential, not parallel: both writer skills modify the same Spec Bee's children list, and the Skill tool's invocation model is single-shot rather than concurrent. Running them in parallel would race the children-list lookup and may produce duplicate PRD or SDD children. Capture from the writer's structured return message:

- `sdd_ticket_id` — the SDD ticket ID (the `t1=Doc` child titled `SDD` under the Spec Bee).
- `sdd_status` — the final status (`ready` on approve, `drafted` on cancel).
- `action` — `created` or `updated`, same semantics as the PRD writer.
- `research_needed` — a (possibly empty) list of `RESEARCH NEEDED: <question>` tags the SDD writer embedded after its codebase-research pass. Surface any non-empty list to the user so they know which open questions still need a follow-up pass before execution.

**Error handling.** If either Skill-tool call returns an error, or the writer reports a non-`ready` final status (i.e., the user cancelled at one of the writer's approval gates), surface the error to the user with the writer's failure detail and **abort Step 4** — do not proceed to the Spec Bee promotion sub-step or to Step 5. The Spec Bee parent remains in `drafted` so the user can re-run `/bees-plan` later and pick `Reuse existing Spec Bee` from sub-step 4a's heuristic prompt to resume from the Spec Bee that already exists. If `/bees-write-prd` succeeds but `/bees-write-sdd` fails, the PRD child remains `ready` and the SDD child either does not exist or remains `drafted` — re-running `/bees-plan` will pick up the partial state cleanly via the writer skills' own idempotency (Step 5's Branch B in each writer).

The captured `prd_ticket_id`, `prd_status`, `sdd_ticket_id`, and `sdd_status` values are consumed by the Spec Bee promotion sub-step (final sibling Subtask), which gates the Spec Bee's own `drafted → ready` transition on both child statuses being `ready`.

#### 4c — Promote the Spec Bee from drafted to ready

With both writer skills returned successfully, transition the Spec Bee parent from `drafted` to `ready` so downstream consumers (the Plan Bee's `reference_materials` and any `bees`-resolver lookups) see a Spec Bee in `ready` state with `ready` PRD and SDD children underneath.

**Defensive status check.** Before issuing the promotion call, confirm that both `prd_status` and `sdd_status` captured in 4b are `ready`. The writer skills' inline-invocation contracts (their respective `## Inline invocation via the Skill tool` sections) guarantee `ready` on successful return — a non-`ready` value here indicates a writer-contract regression, not a normal user-cancel path (cancels are caught by 4b's error-handling clause and abort Step 4 before reaching this sub-step). If either captured status is not `ready`, surface the discrepancy as an error, name which child failed the check, and do **not** promote the Spec Bee. Do not paper over the mismatch by promoting anyway — the defensive check exists precisely so a regression in a writer-skill contract surfaces here rather than silently producing a `ready` Spec Bee with non-`ready` children.

**Promote the Spec Bee.** When both child statuses pass the check, transition the Spec Bee:

```bash
# POSIX (bash / zsh):
bees update-ticket --ids <spec-bee-id> --status ready
```

```powershell
# Windows (PowerShell):
bees update-ticket --ids <spec-bee-id> --status ready
```

The `bees update-ticket` invocation is identical on both platforms here — there is no platform-specific syntax difference for this single-flag call. The paired snippets are kept anyway so the SKILL.md's structure stays uniform with the rest of Step 4.

**Idempotent re-runs.** If the Spec Bee is already in `ready` state when this sub-step begins (for example, a re-run of `/bees-plan` against the same feature where the Spec Bee was promoted in a prior run and the writer skills returned no-op `updated` actions on already-`ready` children), the `bees update-ticket --status ready` call is a harmless no-op — bees treats setting a status field to its existing value as a no-op write. The implementer may optionally short-circuit the promotion call when an already-`ready` Spec Bee is detected, but a defensive re-assert is equivalent in effect and is the simpler default.

**End-of-Step-4 summary — what the user should now see.** After 4c succeeds, the user has:

- A Spec Bee in the Specs hive titled `<feature title>`, status `ready`.
- A `t1=Doc` child of the Spec Bee titled `PRD`, status `ready`, with the PRD content the user approved during `/bees-write-prd`'s gate.
- A `t1=Doc` child of the Spec Bee titled `SDD`, status `ready`, with the SDD content the user approved during `/bees-write-sdd`'s gate (and any `RESEARCH NEEDED:` tags surfaced for follow-up).

Step 5 (Plan Bee creation) consumes this directly: the Plan Bee's `reference_materials` will be set to a single-element list containing a `bees`-resolver entry that points at the Spec Bee ID just promoted, so downstream skills (`/bees-breakdown-epic`, `/bees-execute`'s PM role) can trace from the Plan Bee through the Spec Bee to the PRD and SDD `t1=Doc` children at execution time.

### 5. Create Plan Bee with Epics

Create the Plan Bee inline in this session — do **not** delegate to `/bees-plan-from-specs`. That skill assumes the PRD/SDD describe exactly one feature; this skill drives the cumulative-PRD pattern where each invocation appends a new `### Feature:` subsection, so delegating after Step 4 would re-plan every previously-planned feature in the cumulative docs. Inline creation here is the single supported path regardless of whether PRD/SDD exist — the only difference is whether the Plan Bee's `reference_materials` is populated (PRD/SDD exist) or omitted (no PRD/SDD).

#### 5a — Create the Plan Bee

Author the scope statement to a temp file via the `Write` tool first, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt, and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both. Use a path under the namespaced workflow scratch dir (`/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows). Create the `.bees-workflow` subdir if absent (`mkdir -p /tmp/.bees-workflow` on POSIX, `New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null` on Windows). Do **not** remove the temp file after the bees command exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so crashed runs leave debuggable artifacts in a known place; the OS / user reclaims them on their own cadence.

The body should be a brief 2-3 sentence summary of the goal and scope. When `reference_materials` is set, do not dump PRD/SDD content into the body — downstream skills read the linked docs from `reference_materials`.

**If PRD/SDD exist for this feature** (Step 4a, or Step 4b option 1 where you just drafted them), set `--reference-materials` to a JSON array of one dict per file, each with a single `value` key holding the path. **Prefer paths relative to the repo root** (e.g., `docs/prd.md`) when the doc lives inside the repo — relative paths stay portable across machines and contributors. The bees CLI's built-in `file-path` resolver handles them via the repo root. Use absolute paths only for docs that live outside the repo. Pass the paths in PRD-then-SDD order so downstream consumers can rely on the positional convention:

```
[{"value": "<path to PRD>"}, {"value": "<path to SDD>"}]
```

```bash
# POSIX (bash / zsh) — with PRD/SDD reference_materials:
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status drafted \
  --title "<feature title>" \
  --body-file <path> \
  --reference-materials '[{"value":"<prd path>"},{"value":"<sdd path>"}]'

# Windows (PowerShell) — with PRD/SDD reference_materials:
bees create-ticket `
  --ticket-type bee `
  --hive plans `
  --status drafted `
  --title "<feature title>" `
  --body-file <path> `
  --reference-materials '[{"value":"<prd path>"},{"value":"<sdd path>"}]'
```

**If no PRD/SDD exist for this feature** (Step 4b option 2 — body-as-spec), omit `--reference-materials` entirely. The Plan Bee body becomes the authoritative scope document, so make it detailed enough that the PM in `/bees-execute` can use it for drift detection.

```bash
# POSIX (bash / zsh) — no reference_materials:
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status drafted \
  --title "<feature title>" \
  --body-file <path>

# Windows (PowerShell) — no reference_materials:
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

Create each approved Epic as a `t1` child of the Plan Bee with status `drafted`. Use the same temp-file + `--body-file` pattern as in 5a (author body to `<tempdir>/.bees-workflow/`, pass path; do not delete after). **Do not pass `--reference-materials` on Epics** — the bees CLI accepts `--reference-materials` only on top-level Bees (`bees create-ticket --help`: "Only supported on bee (top-level) tickets") and hard-errors on child tiers. Downstream skills trace Epics back to PRD/SDD via the parent Plan Bee's `reference_materials`, not the Epic's.

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
