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
- CLAUDE.md contains a `## Documentation Locations` section. The "Create the ticket" step's body authoring reads architecture/customer-doc paths from this section by exact key so the optional `## Doc divergence noted` capture can point at the right file when the issue surfaces a doc claim that's wrong (or a doc gap).

Note: bees-file-issue does **not** require CLAUDE.md `## Build Commands`. bees-file-issue only files a ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/bees-fix-issue` and `/bees-execute` when they actually execute the work, not at filing time.

If the precondition is missing, stop with `Run /bees-setup first.` and direct the user there.

## Steps

### 0. Detect mid-conversation context

Before treating this invocation as cold, judge whether the current Claude Code session already contains substantive context about the issue being filed. The two downstream branches in the "Gather issue information" step (distill vs restart) are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the bug or its scope, root cause, or alternatives considered.
- The user's invocation message (or `/bees-file-issue <description>` argument) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the symptom, repro, suspected root cause, or impact.
- An explicit hint that this is a continuation of a debugging or analytical discussion (e.g., the user has been investigating the bug with the assistant before invoking the skill).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a substantive debugging conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/bees-plan`'s detection step and in the inline-invocation paths of `/bees-write-prd` and `/bees-write-sdd`; keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning, filing, and PRD/SDD authoring.

The heuristic's output feeds the "Gather issue information" step below: distill branch when it fires, restart branch when it does not.

### 1. Gather issue information

Two branches based on the "Detect mid-conversation context" step's heuristic. Use the distill branch when the heuristic fires; use the restart branch otherwise (solo invocation from a fresh session, or `/bees-file-issue <description>` with only a one-line description and no rich preceding discussion).

#### 1a — Distill branch (heuristic fires)

Skip the "What's the issue?" prompt entirely — the prior conversation already contains the substance. Instead:

1. Distill the prior session into a draft Issue body that matches the body-template shape defined in the "Create the ticket" step — Description / Current behavior / Expected behavior / Impact / Suggested fix, plus the OPTIONAL sections defined in that body-template block when the conversation supplies the relevant content. Specifically:
   - **`## Background and rationale`** — populate when the prior conversation includes substantive root-cause analysis, alternative-cause ruling, or trade-off discussion. Capture *why* this is a bug, *which root causes were ruled out and why*, and any *trade-offs* surfaced during analysis. Omit the section entirely if the conversation has none of that content.
   - **`## Decisions and rejected alternatives`** — populate when the prior conversation discussed alternative fixes and the user chose one path over others. Capture the alternatives considered and the reasoning for choosing the suggested fix, so `/bees-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Omit the section entirely if the conversation didn't weigh alternative fixes.
   - **`## Doc divergence noted`** — populate when the conversation surfaced a doc claim that's wrong (or a doc gap). Omit otherwise. (The "Create the ticket" step's doc-divergence review still runs and may append or refine this section after the user approves the distilled draft.)
2. Present the distilled Issue body to the user via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:
   - **Approve** — proceed to the "Research the issue" step (research / duplicate check) and the "Create the ticket" step with the distilled body as the starting draft.
   - **Revise** — iterate in prose with the user on what to change, then re-present the revised draft via `AskUserQuestion`.
   - **Cancel** — exit the skill cleanly without filing.

On approve, carry the distilled body forward as the seed for the "Create the ticket" step's body authoring — that step's doc-divergence review still runs and may append (or refine) a `## Doc divergence noted` section, and the "Research the issue" step's duplicate check still runs against the distilled scope.

#### 1b — Restart branch (cold invocation)

If called without arguments, use AskUserQuestion to ask:
- "What's the issue?" (free text description)

If called with arguments, use those as the description.

The restart branch produces a body matching today's shape — Description / Current behavior / Expected behavior / Impact / Suggested fix — without the OPTIONAL `## Background and rationale` or `## Decisions and rejected alternatives` sections. There's no analytical content to capture from a one-line description, so omitting those sections (rather than rendering empty stubs) is correct. The OPTIONAL `## Doc divergence noted` section may still be appended by the "Create the ticket" step's doc-divergence review when applicable.

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

This step is the single locus of "decide what goes in the body, then file." Compose the full Issue body — including any optional sections — into a temp file, then run `bees create-ticket` once with the complete body. Do **not** create the ticket first and then update the body afterward; everything that belongs in the body goes in before the bees command runs.

Use a temp file plus `--body-file <path>` rather than an inline `--body "..."` argument. Bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt regardless of the user's allowlist, and inlined markdown is also fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both problems. Status-only updates with no body (e.g. `bees update-ticket --ids <id> --status done`) and genuinely single-line bodies can stay on inline `--body`.

#### 3a. Compose the body

The body is structured markdown with five **required** sections and three **optional** sections.

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
<OPTIONAL — populated when the issue came out of substantive analysis (root-cause investigation, alternative-cause ruling, trade-off discussion); omitted entirely on casual one-line bug reports. Captures *why* this is a bug, *which root causes were ruled out and why*, and *trade-offs* surfaced during analysis. Distilled from the prior conversation by the distill branch (1a) of the "Gather issue information" step when the "Detect mid-conversation context" heuristic fires; absent on the restart branch (1b).>

## Decisions and rejected alternatives
<OPTIONAL — populated when the suggested-fix path was chosen over alternatives that were considered; omitted entirely otherwise. Captures the alternatives considered and the reasoning for choosing the suggested fix, so `/bees-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Distilled from the prior conversation by the distill branch (1a) of the "Gather issue information" step when the "Detect mid-conversation context" heuristic fires; absent on the restart branch (1b).>

## Doc divergence noted
<OPTIONAL — populated when the issue surfaces a doc claim that's wrong (or a doc gap); omitted otherwise. Plain prose pointing at the file/section that's wrong and what's wrong about it. Use the canonical doc paths from CLAUDE.md "Documentation Locations" — `Internal architecture docs (SDD)`, `Customer-facing docs`, and the PRD-equivalent if the project has one — as the pointers. `/bees-fix-issue`'s doc-writer pass consumes this section during fix execution; do NOT edit project docs from this skill.>
```

**OPTIONAL-section contract.** The three sections marked OPTIONAL above — `## Background and rationale`, `## Decisions and rejected alternatives`, and `## Doc divergence noted` — are **omitted entirely** from the Issue body when the issue does not have content for them. Do **not** render them as stub headings followed by empty bodies, "N/A", or "TBD" — leave the section heading out of the markdown completely.

This is intentionally different from the `/bees-write-prd` and `/bees-write-sdd` skills' mandatory-always-present rule. PRD/SDD docs use a fixed contract where every section is always rendered (even when empty) so downstream readers can rely on the shape. Issues, by contrast, come in many sizes — one-line bug reports filed via `/bees-file-issue "<description>"` vs deep analytical sessions distilled into a rich Issue body. Requiring the rationale sections always-present would force noise (empty stubs, "N/A" placeholders) into casual issues without adding value. Casual one-line invocations produce Issues without these sections; analytical issues populate them with substance.

#### 3b. Doc-divergence review (decides whether `## Doc divergence noted` is included)

Before writing the body to the temp file, review whether the issue description implies the project's spec docs contain incorrect information. The outcome of this review decides whether the OPTIONAL `## Doc divergence noted` section appears in the body composed in 3a.

This review is **observation-only** — do NOT edit any of the project documentation files configured under CLAUDE.md `## Documentation Locations`, the README, or any other project documentation file. The remediation belongs to `/bees-fix-issue`'s doc-writer pass, which consumes the `## Doc divergence noted` section during fix execution.

Use the paths configured in CLAUDE.md `## Documentation Locations` — specifically `Internal architecture docs (SDD)` and `Customer-facing docs` (the README-equivalent). The Documentation Locations section has no canonical "PRD" key; if the project has a PRD-equivalent at a known path, include it in the review, otherwise skip the PRD pointer.

Examples of doc divergence to watch for:
- Documenting behavior that is now known to be wrong
- Missing config variables or wrong defaults
- Wrong API contracts or field names
- Incorrect architecture descriptions

If divergence is observed, include a `## Doc divergence noted` section in the body composed in 3a. Format: plain prose pointing at the file/section that's wrong and what's wrong about it; reference the file by the path from CLAUDE.md `## Documentation Locations`. If no divergence is observed, omit the section entirely.

When the distill branch (1a) of the "Gather issue information" step has already populated `## Doc divergence noted` from the prior conversation, this review either confirms the existing capture or refines it; it does not add a duplicate section.

#### 3c. Write the body to a temp file and run `bees create-ticket`

1. Pick a temp path under the namespaced workflow scratch dir: `/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows. Create the `.bees-workflow` subdir if it does not yet exist:

   ```bash
   # POSIX (bash / zsh):
   mkdir -p /tmp/.bees-workflow
   ```

   ```powershell
   # Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
   ```
2. Use the `Write` tool to write the structured body — including any `## Doc divergence noted` section determined in 3b — to that path.
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

### 4. Commit the ticket

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

### 5. Report back

Show the user:
- The ticket ID
- The title
- A one-line summary of what was filed
- Whether the issue captured a doc-divergence observation (the `## Doc divergence noted` section in the body) so the user knows `/bees-fix-issue`'s doc-sync pass will consume it.
