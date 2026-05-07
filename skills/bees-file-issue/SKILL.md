---
name: bees-file-issue
description: File a new issue ticket in the issues hive
argument-hint: "[<description> | --reference <url> | --from-github <url>]"
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
- `/bees-file-issue --reference <url>` — external-reference mode: file a thin Issue whose `reference_materials` points at an external resource (GitHub Issue, Linear ticket, internal bug tracker URL, Slack archive link, etc.) instead of capturing the spec content in the body. Symmetric with `/bees-plan-from-specs` on the planning side.
- `/bees-file-issue --from-github <url>` — friendlier alias for the GitHub Issues case (selects the same external-reference path as `--reference`).

The two paths produce different Issue shapes:

- **In-conversation capture** (no `--reference` flag) — the Issue body is the authoritative spec, populated from the user's description or a distilled prior conversation per the body-template in Step 3a.
- **External-reference mode** (`--reference` / `--from-github`) — the Issue body is a thin 2-3 sentence summary, and `reference_materials` carries `[{"value":"<url>","resolver":"<resolver-name>"}]` pointing at the external source. `/bees-fix-issue`'s PM and Engineer fetch the upstream content from the URL when they pick the Issue up.

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. The "Create the ticket" step's body authoring reads architecture/customer-doc paths from this section by exact key so the optional `## Doc divergence noted` capture can point at the right file when the issue surfaces a doc claim that's wrong (or a doc gap).

Note: bees-file-issue does **not** require CLAUDE.md `## Build Commands`. bees-file-issue only files a ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/bees-fix-issue` and `/bees-execute` when they actually execute the work, not at filing time.

If the precondition is missing, stop with `Run /bees-setup first.` and direct the user there.

## Steps

### Mode fork — in-conversation capture vs external-reference

Before any other step, parse the argument string for an external-reference flag and route accordingly:

- `--reference <url>` — generic external-reference mode.
- `--from-github <url>` — friendlier alias for the GitHub Issues case; same code path as `--reference`. Any future per-source aliases (`--from-linear`, `--from-jira`, etc.) are folded into this same branch — the resolver-name selection in the External-reference branch (below) is what differentiates them downstream. The alias does **not** pin the resolver name to `github-issue`: sub-step B's URL-pattern heuristic still runs unconditionally, so a non-GitHub URL passed via `--from-github` (e.g., a Linear or generic URL) will pick up `linear-issue` or `url` per the pattern table, not `github-issue`. The alias controls argument parsing, not resolver selection.

If any external-reference flag is present, capture the URL value and route to the **External-reference branch** at the end of this Steps section; skip Step 0 (mid-conversation context detection) and Step 1 (distill-vs-restart fork) entirely. The external-reference path has its own thin-body authoring and its own `bees create-ticket` invocation — Steps 1, 2, 3a, 3b, 3c, and the inner sub-steps of Step 3 are not reached on this path. Steps 4 (commit) and 5 (report back) are shared with the in-conversation capture flow.

If no external-reference flag is present, proceed to Step 0 below and the standard in-conversation capture flow (Steps 0 → 1 → 2 → 3 → 4 → 5).

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

### External-reference branch (reached only when `--reference` / `--from-github` is set)

This branch handles the external-reference invocation modes parsed by the "Mode fork" step above. When this branch runs, Steps 1, 2, 3a, 3b, and 3c are **not** reached — this branch produces the Issue body and runs `bees create-ticket` itself. Flow rejoins the standard path at Step 4 (commit) and Step 5 (report back).

#### A. Author a thin Issue body (2-3 sentences)

The Issue body in external-reference mode is a thin summary, **not** the full body-template from Step 3a. Two sources for the summary, in order of preference:

1. **Mid-conversation context.** If the surrounding conversation already explains what's at the URL — the user has been discussing the bug, has linked the URL inline, or has asked the assistant to read the URL — distill 2-3 sentences from that context. Mid-conversation awareness still applies on this path; the err-toward-distilling principle from Step 0 carries over.
2. **Fetch the URL via `WebFetch`.** If the conversation does not explain what's at the URL but the URL is fetchable (public web page, reachable from the current network), use `WebFetch` to read it and distill 2-3 sentences from the upstream content. This is optional — the authoritative spec content stays at the URL and `/bees-fix-issue` fetches it again at fix time; the body summary is for human readers of the Issue, not for downstream agents.
3. **Ask the user.** If neither prior context nor `WebFetch` produces a useful summary (e.g., the URL is auth-gated or otherwise unreadable), ask in prose for a one- or two-sentence summary of what the bees workflow needs to know about the referenced source. Use prose rather than `AskUserQuestion` — per CLAUDE.md `## AskUserQuestion usage`, that tool is multi-choice only and is wrong for free-text answers.

The body shape is intentionally **flat** — no `## Description` / `## Current behavior` / `## Expected behavior` / `## Impact` / `## Suggested fix` headings. Those sections exist to extract structure from in-conversation capture; on this path the structure lives at the URL, and forcing the headings into a thin body would either duplicate URL content or render mostly-empty stubs. The OPTIONAL `## Doc divergence noted` section from Step 3a may still be appended on this path **only when** the user (or the surrounding conversation) explicitly flags a doc-divergence observation that the external source does not already capture; in routine external-reference filings the section is omitted. Step 3b's automatic doc-divergence review does **not** run on this path — consistent with the Mode fork's "Steps 1, 2, 3a, 3b, 3c, and the inner sub-steps of Step 3 are not reached on this path" — so the section is appended only when the user or the surrounding conversation initiates it, never as the result of an automatic review pass.

The thin body should also include a single line near the top naming the referenced source and the URL, so a reader of the Issue body alone can tell where to look — for example:

```markdown
External reference: GitHub Issue https://github.com/owner/repo/issues/123

<2-3 sentence summary distilled from the URL or user description>
```

The `external reference` line is a convention, not a contract — `reference_materials` is the load-bearing signal that downstream `/bees-fix-issue` reads.

**Title.** Pick a concise title (under 80 characters) that names what the upstream issue is about, not just the URL slug. If the user supplied a title or the conversation distilled to one, prefer that; otherwise summarize from the upstream content (or ask the user in prose for a title if neither source is available).

#### B. Pick a resolver name (URL-pattern heuristic)

The resolver name written into `reference_materials` is selected by URL pattern matching. The bees CLI may not yet have a concrete resolver implementation registered for these names — that is intentional and out of scope for this skill (concrete resolvers are tracked separately as their owners materialize). The skill writes the canonical resolver name regardless; downstream `/bees-fix-issue`'s PM and Engineer fall back to fetching the URL via `WebFetch` until a real resolver lands.

The pattern table:

| URL shape | Resolver name |
|---|---|
| `https://github.com/<owner>/<repo>/issues/<n>` (and similar GitHub Issue URLs) | `github-issue` |
| `https://linear.app/<workspace>/issue/<id>` (and similar Linear ticket URLs) | `linear-issue` |
| Anything else (Slack archive link, internal bug tracker, generic web page) | `url` |

The URL host and path determine the resolver name — match on host first, then path-shape. When in doubt, fall back to `url`. The match is best-effort and informational; it primarily helps human readers and future resolver implementations identify the source class.

**Concrete-resolver gap (intentional).** No concrete `github-issue`, `linear-issue`, or `url` resolver exists in the bees CLI today. That is a separate piece of work, owned by whoever builds each resolver. Until those land, the workflow falls back to `WebFetch` on the URL whenever the upstream content is needed — see `agents/pm.md` and `agents/engineer.md` for the fetch convention. Writing the canonical resolver name now (rather than e.g. always writing `url`) future-proofs existing Issue tickets so they do not need to be migrated when concrete resolvers ship.

#### C. Run `bees create-ticket` with `--reference-materials`

Unlike the in-conversation capture path, the external-reference branch passes the body inline (it is short, one-line-ish) and the URL as a `--reference-materials` JSON argument. No temp body file is written on this path.

The exception: if the thin body authored in (A) contains anything that would trip Claude Code's command-injection guard — a newline followed by a `#` heading, backticks, or shell-special characters — fall back to the temp-file convention from Step 3c (write the body under `<tempdir>/.bees-workflow/bees-body-<short-suffix>.md` after creating the namespaced subdir, then pass `--body-file <path>`). Most thin bodies will fit on `--body` cleanly; the temp-file fallback is the safety valve.

```bash
# POSIX (bash / zsh) — inline-body path:
bees create-ticket \
  --ticket-type bee \
  --hive issues \
  --status open \
  --title "<concise title>" \
  --body "<thin 2-3 sentence body>" \
  --reference-materials '[{"value":"<url>","resolver":"<resolver-name>"}]'
```

```powershell
# Windows (PowerShell) — inline-body path:
bees create-ticket `
  --ticket-type bee `
  --hive issues `
  --status open `
  --title "<concise title>" `
  --body "<thin 2-3 sentence body>" `
  --reference-materials '[{"value":"<url>","resolver":"<resolver-name>"}]'
```

If the thin body needs the temp-file fallback, replace `--body "<...>"` with `--body-file <path>` per Step 3c's snippet shape (including the `mkdir -p` / `New-Item -ItemType Directory -Force` create-if-absent step) and keep the `--reference-materials` argument unchanged.

After the ticket is created, proceed to Step 4 (commit) and Step 5 (report back). The Step 5 summary should call out that this Issue was filed in external-reference mode and name the referenced URL, so the user knows `/bees-fix-issue` will fetch upstream content rather than read the body as-spec.

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
- If the issue was filed in external-reference mode (`--reference` / `--from-github`): the referenced URL and the resolver name written into `reference_materials` (see sub-step B for how the resolver name is selected from the URL pattern), so the user knows `/bees-fix-issue` will fetch upstream content rather than treat the body as the spec.
