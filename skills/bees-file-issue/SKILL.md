---
name: bees-file-issue
description: File a new issue ticket in the issues hive
argument-hint: "[<description>]"
---

## Overview

Create a new issue ticket in the issues hive. The user describes the issue and this skill creates a well-structured ticket.

## House style: bundle related issues

When filing issues, **default to bundling related items into fewer tickets** rather than splitting them along human-triage lines. The bees workflow is optimized for agent work efficiency: per-ticket overhead — read scope, load context, write tests, commit — is the cost to minimize, not human-triage legibility.

Split into separate tickets only when:

- Issues are truly independent (no shared code paths, no shared tests, no shared mental model required to fix them)
- Different status / priority lifecycles are needed
- One genuinely blocks another and they need separate tracking

Don't split along categorical lines (e.g. "memory leak vs correctness vs doc fix") if the fixes touch the same module or can share a single pass through the code. A bundled ticket with clearly-labeled sub-findings inside the body is the right shape.

This is workflow-level house style. Projects that disagree (e.g., projects with human triage workflows) can override in their CLAUDE.md or via project-specific instructions to the agent calling this skill.

## Usage

The user can call this skill in several ways:

- `/bees-file-issue` — interactive: ask the user to describe the issue
- `/bees-file-issue Some description of the problem` — create directly from the description

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. Step 3's body authoring reads architecture/customer-doc paths from this section by exact key so the optional `## Doc divergence noted` capture can point at the right file when the issue surfaces a doc claim that's wrong (or a doc gap).

Note: bees-file-issue does **not** require CLAUDE.md `## Build Commands`. bees-file-issue only files a ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/bees-fix-issue` and `/bees-execute` when they actually execute the work, not at filing time.

If the precondition is missing, stop with `Run /bees-setup first.` and direct the user there.

## Steps

### 0. Detect mid-conversation context

Before treating this invocation as cold, judge whether the current Claude Code session already contains substantive context about the issue being filed. The two downstream branches in Step 1 (distill vs restart) are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the bug or its scope, root cause, or alternatives considered.
- The user's invocation message (or `/bees-file-issue <description>` argument) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the symptom, repro, suspected root cause, or impact.
- An explicit hint that this is a continuation of a debugging or analytical discussion (e.g., the user has been investigating the bug with the assistant before invoking the skill).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a substantive debugging conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/bees-plan`'s detection step (sibling skill `bees-plan` Subtask `t3.31f.y2.o7.qn` will land the equivalent prose there); keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning and filing.

The heuristic's output feeds Step 1 below: distill branch when it fires, restart branch when it does not.

### 1. Gather issue information

Two branches based on Step 0's heuristic. Use the distill branch when the heuristic fires; use the restart branch otherwise (solo invocation from a fresh session, or `/bees-file-issue <description>` with only a one-line description and no rich preceding discussion).

#### 1a — Distill branch (heuristic fires)

Skip the "What's the issue?" prompt entirely — the prior conversation already contains the substance. Instead:

1. Distill the prior session into a draft Issue body that matches the Step 3 body-template shape — Description / Current behavior / Expected behavior / Impact / Suggested fix, plus the OPTIONAL sections defined in Step 3's body-template block when the conversation supplies the relevant content. Specifically:
   - **`## Background and rationale`** — populate when the prior conversation includes substantive root-cause analysis, alternative-cause ruling, or trade-off discussion. Capture *why* this is a bug, *which root causes were ruled out and why*, and any *trade-offs* surfaced during analysis. Omit the section entirely if the conversation has none of that content.
   - **`## Decisions and rejected alternatives`** — populate when the prior conversation discussed alternative fixes and the user chose one path over others. Capture the alternatives considered and the reasoning for choosing the suggested fix, so `/bees-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Omit the section entirely if the conversation didn't weigh alternative fixes.
   - **`## Doc divergence noted`** — populate when the conversation surfaced a doc claim that's wrong (or a doc gap). Omit otherwise. (Step 4's doc-divergence review still runs and may append or refine this section after the user approves the distilled draft.)
2. Present the distilled Issue body to the user via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:
   - **Approve** — proceed to Step 2 (research / duplicate check) and Step 3 (create the ticket) with the distilled body as the starting draft.
   - **Revise** — iterate in prose with the user on what to change, then re-present the revised draft via `AskUserQuestion`.
   - **Cancel** — exit the skill cleanly without filing.

On approve, carry the distilled body forward as the seed for Step 3's body authoring — Step 4's doc-divergence review still runs and may append (or refine) a `## Doc divergence noted` section, and Step 2's duplicate check still runs against the distilled scope.

#### 1b — Restart branch (cold invocation)

If called without arguments, use AskUserQuestion to ask:
- "What's the issue?" (free text description)

If called with arguments, use those as the description.

The restart branch produces a body matching today's shape — Description / Current behavior / Expected behavior / Impact / Suggested fix — without the OPTIONAL `## Background and rationale` or `## Decisions and rejected alternatives` sections. There's no analytical content to capture from a one-line description, so omitting those sections (rather than rendering empty stubs) is correct. The OPTIONAL `## Doc divergence noted` section may still be appended by Step 4's doc-divergence review when applicable.

### 2. Research the issue (optional)

If the description references specific code, files, or behavior:
- Read the relevant source files to understand the current state
- Check if there's already an issue ticket for the same problem. Query the open issues in the issues hive and scan returned titles for overlap with the user's description:

  ```bash
  bees execute-freeform-query --query-yaml 'stages:
    - [type=bee, hive=issues, status=open]
  report: [title]'
  ```

  If a clear duplicate exists, surface it to the user and ask whether to file anyway (sometimes a near-duplicate captures a different angle), append to the existing ticket, or stop.

### 3. Create the ticket

Author the structured body to a temp file via the `Write` tool, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt regardless of the user's allowlist, and inlined markdown is also fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both problems. Status-only updates with no body (e.g. `bees update-ticket --ids <id> --status done`) and genuinely single-line bodies can stay on inline `--body`. Steps:

1. Pick a temp path under the namespaced workflow scratch dir: `/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows. Create the `.bees-workflow` subdir if it does not yet exist:

   ```bash
   # POSIX (bash / zsh):
   mkdir -p /tmp/.bees-workflow
   ```

   ```powershell
   # Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
   ```
2. Use the `Write` tool to write the structured body to that path.
3. Run the bees command (the file-flag carries no shell-quoting surface — only the line-continuation character differs between OSes):

   ```bash
   # POSIX (bash / zsh):
   bees create-ticket \
     --ticket-type bee \
     --hive issues \
     --status open \
     --title "<concise title>" \
     --body-file <path>

   # Windows (PowerShell):
   bees create-ticket `
     --ticket-type bee `
     --hive issues `
     --status open `
     --title "<concise title>" `
     --body-file <path>
   ```

   The scratch file is **not** removed after the bees command exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. The OS / the user reclaims them on their own cadence.

**Title guidelines:**
- Under 80 characters
- Starts with a verb or describes the symptom
- Include a spec-doc section reference if the issue ties to a documented requirement (use the actual doc name from CLAUDE.md "Documentation Locations")

**Body structure:**
```markdown
## Description
<What's wrong — the symptom or deviation from expected behavior>

## Current behavior
<What happens now>

## Expected behavior
<What should happen, with a spec-doc reference if applicable (use the doc paths from CLAUDE.md "Documentation Locations")>

## Impact
<Correctness, performance, or UX impact>

## Suggested fix
<Brief description of what needs to change, key files involved>

## Background and rationale
<OPTIONAL — populated when the issue came out of substantive analysis (root-cause investigation, alternative-cause ruling, trade-off discussion); omitted entirely on casual one-line bug reports. Captures *why* this is a bug, *which root causes were ruled out and why*, and *trade-offs* surfaced during analysis. Distilled from the prior conversation by Step 1a's distill branch when the heuristic in Step 0 fires; absent on Step 1b's restart branch.>

## Decisions and rejected alternatives
<OPTIONAL — populated when the suggested-fix path was chosen over alternatives that were considered; omitted entirely otherwise. Captures the alternatives considered and the reasoning for choosing the suggested fix, so `/bees-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Distilled from the prior conversation by Step 1a's distill branch when the heuristic in Step 0 fires; absent on Step 1b's restart branch.>

## Doc divergence noted
<OPTIONAL — populated when the issue surfaces a doc claim that's wrong (or a doc gap); omitted otherwise. Plain prose pointing at the file/section that's wrong and what's wrong about it. Use the canonical doc paths from CLAUDE.md "Documentation Locations" — `Internal architecture docs (SDD)`, `Customer-facing docs`, and the PRD-equivalent if the project has one — as the pointers. `/bees-fix-issue`'s doc-writer pass consumes this section during fix execution; do NOT edit project docs from this skill.>
```

**OPTIONAL-section contract.** The three sections marked OPTIONAL above — `## Background and rationale`, `## Decisions and rejected alternatives`, and `## Doc divergence noted` — are **omitted entirely** from the Issue body when the issue does not have content for them. Do **not** render them as stub headings followed by empty bodies, "N/A", or "TBD" — leave the section heading out of the markdown completely.

This is intentionally different from the `/bees-write-prd` and `/bees-write-sdd` skills' mandatory-always-present rule. PRD/SDD docs use a fixed contract where every section is always rendered (even when empty) so downstream readers can rely on the shape. Issues, by contrast, come in many sizes — one-line bug reports filed via `/bees-file-issue "<description>"` vs deep analytical sessions distilled into a rich Issue body. Requiring the rationale sections always-present would force noise (empty stubs, "N/A" placeholders) into casual issues without adding value. Casual one-line invocations produce Issues without these sections; analytical issues populate them with substance.

### 4. Capture any doc-divergence observation in the Issue body

This step is **observation-only** — do NOT edit any of the project documentation files configured under CLAUDE.md `## Documentation Locations`, the README, or any other project documentation file. The remediation belongs to `/bees-fix-issue`'s doc-writer pass, which consumes the `## Doc divergence noted` section during fix execution.

This step runs **interleaved with Step 3** — it edits the scratch body file before Step 3's `bees create-ticket` executes. The only valid orderings are (i) divergence captured *during* Step 3 body authoring or (ii) divergence captured *after* Step 3 authors the scratch file but *before* `bees create-ticket` runs; never after `bees create-ticket`.

Review whether the issue description implies the project's spec docs contain incorrect information. Use the paths configured in CLAUDE.md `## Documentation Locations` — specifically `Internal architecture docs (SDD)` and `Customer-facing docs` (the README-equivalent). The Documentation Locations section has no canonical "PRD" key; if the project has a PRD-equivalent at a known path, include it in the review, otherwise skip the PRD pointer.

Examples of doc divergence to watch for:
- Documenting behavior that is now known to be wrong
- Missing config variables or wrong defaults
- Wrong API contracts or field names
- Incorrect architecture descriptions

If divergence is observed, append a `## Doc divergence noted` section to the Issue body **before** running `bees create-ticket` — that is, edit the scratch body file authored in Step 3 (under `<tempdir>/.bees-workflow/`) to add the section, then proceed with the bees command. Format: plain prose pointing at the file/section that's wrong and what's wrong about it; reference the file by the path from CLAUDE.md `## Documentation Locations`. (Equivalently, if the divergence is obvious during Step 3 body authoring, fold the section directly into that initial write — either shape is fine as long as the resulting Issue body contains the section.)

If no divergence is observed, omit the section entirely and proceed to Step 5.

### 5. Commit the ticket

Stage and commit the ticket file. **Do not hardcode the `.bees/issues/` path.** `/bees-setup` lets the user choose where each hive lives — in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/issues/` silently stages nothing when the user picked a sibling path.

Resolve the Issues hive path via `bees list-hives`, check whether it lives inside the current git repo, and only stage it if it does:

```bash
# POSIX (bash / zsh):
issues_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="issues"), None); print(p or "")')
repo_root=$(git rev-parse --show-toplevel)
git_add_args=""
case "$issues_path" in
  "$repo_root"|"$repo_root"/*) git_add_args="$issues_path" ;;
esac
if [ -n "$git_add_args" ]; then
  git add $git_add_args
  git commit -m "File issue: <title>"
fi
```

```powershell
# Windows (PowerShell):
$issuesPath = (bees list-hives | ConvertFrom-Json).hives | Where-Object { $_.normalized_name -eq 'issues' } | Select-Object -ExpandProperty path
$repoRoot = git rev-parse --show-toplevel
# Normalize separators — git rev-parse returns forward slashes on Windows;
# bees list-hives may return backslashes. Compare both sides on the same form.
$issuesNorm = if ($issuesPath) { $issuesPath.Replace('\','/') } else { '' }
$repoNorm = $repoRoot.Replace('\','/')
$addArgs = @()
if ($issuesNorm -and ($issuesNorm -eq $repoNorm -or $issuesNorm.StartsWith("$repoNorm/"))) {
  $addArgs += $issuesPath
}
if ($addArgs.Count -gt 0) {
  git add @addArgs
  git commit -m "File issue: <title>"
}
```

If the Issues hive lives outside the repo, no git commit is needed here — the bees CLI has already persisted the ticket. Remind the user that the issue ticket is stored separately (the bees CLI persists it; no git tracking needed for the ticket file itself).

### 6. Report back

Show the user:
- The ticket ID
- The title
- A one-line summary of what was filed
- Whether the issue captured a doc-divergence observation (the `## Doc divergence noted` section in the body) so the user knows `/bees-fix-issue`'s doc-sync pass will consume it.
