---
name: quo-file-issue
description: File a new issue ticket in the issues hive
argument-hint: "[<description> | <url> | --reference <url> | --from-github <url>]"
---

## Overview

Create a new issue ticket in the issues hive. The user describes the issue and this skill creates a well-structured ticket.

## House style: bundle related issues

When filing issues, **default to bundling related items into fewer tickets** rather than splitting them along human-triage lines. Quorum is optimized for agent work efficiency: per-ticket overhead — read scope, load context, write tests, commit — is the cost to minimize, not human-triage legibility.

Split into separate tickets only when:

- Issues are truly independent (no shared code paths, no shared tests, no shared mental model required to fix them)
- Different status / priority lifecycles are needed
- One genuinely blocks another and they need separate tracking

Don't split along categorical lines (e.g. "memory leak vs correctness vs doc fix") if the fixes touch the same module or can share a single pass through the code. A bundled ticket with clearly-labeled sub-findings inside the body is the right shape.

This is workflow-level house style. Projects that disagree (e.g., projects with human triage workflows) can override in their CLAUDE.md or via project-specific instructions to the agent calling this skill.

## Usage

The user can call this skill in several ways:

- `/quo-file-issue` — interactive: ask the user to describe the issue
- `/quo-file-issue Some description of the problem` — create directly from the description
- `/quo-file-issue <url>` — bare-URL shorthand for external-reference mode: routes to the same External-reference branch as `--reference <url>`. A positional token starting with `http://` or `https://` is auto-detected; URLs inside a quoted description string are not. Example: `/quo-file-issue https://github.com/owner/repo/issues/123`.
- `/quo-file-issue --reference <url>` — external-reference mode: file a thin Issue whose `reference_materials` points at an external resource (GitHub Issue, Linear ticket, internal bug tracker URL, Slack archive link, etc.) instead of capturing the spec content in the body. Symmetric with `/quo-plan-from-specs` on the planning side.
- `/quo-file-issue --from-github <url>` — friendlier alias for the GitHub Issues case (selects the same external-reference path as `--reference`).

The two paths produce different Issue shapes:

- **In-conversation capture** (no `--reference` flag) — the Issue body is the authoritative spec, populated from the user's description or a distilled prior conversation per the body-template in Step 3a.
- **External-reference mode** (`--reference` / `--from-github`) — the Issue body is a thin 2-3 sentence summary, and `reference_materials` carries `[{"value":"<url>","resolver":"<resolver-name>"}]` pointing at the external source. `/quo-fix-issue`'s PM and Engineer fetch the upstream content from the URL when they pick the Issue up.

## Preconditions

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. The "Create the ticket" step's body authoring reads architecture/customer-doc paths from this section by exact key so the optional `## Doc divergence noted` capture can point at the right file when the issue surfaces a doc claim that's wrong (or a doc gap).

Note: quo-file-issue does **not** require CLAUDE.md `## Build Commands`. quo-file-issue only files a ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/quo-fix-issue` and `/quo-execute` when they actually execute the work, not at filing time.

If the precondition is missing, stop with `Run /quo-setup first.` and direct the user there.

## Steps

### Mode fork — in-conversation capture vs external-reference

Before any other step, parse the argument string for an external-reference signal and route accordingly. Three input shapes route to the External-reference branch:

- `--reference <url>` — generic external-reference mode.
- `--from-github <url>` — friendlier alias for the GitHub Issues case; same code path as `--reference`. Any future per-source aliases (`--from-linear`, `--from-jira`, etc.) are folded into this same branch — the resolver-name selection in the External-reference branch (below) is what differentiates them downstream. The alias does **not** pin the resolver name to `github-issue`: sub-step C's URL-pattern heuristic still runs unconditionally, so a non-GitHub URL passed via `--from-github` (e.g., a Linear or generic URL) will pick up `linear-issue` or `url` per the pattern table, not `github-issue`. The alias controls argument parsing, not resolver selection.
- **Bare-URL positional** — a positional argument token that begins with `http://` or `https://` after argument tokenization is treated as the URL value and routed to the External-reference branch, identical in effect to `--reference <url>`. Detection is anchored at the start of the token (`^https?://`); only standalone tokens are URL-shaped. The flag forms above remain accepted as silent no-op aliases — they are not deprecated, do not warn, and are still useful for discoverability — but on the bare-URL path no flag is required.

**Tokenization happens before URL detection.** A URL embedded inside a quoted free-text token (e.g., `/quo-file-issue "Fix the bug at https://example.com/foo"`) is **not** auto-detected — the entire quoted string is a single description token, and the `^https?://` test is applied to the start of the token, which begins with `Fix`, not `http`. Such invocations continue to route to the in-conversation capture flow with the URL preserved verbatim inside the description. Only standalone positional tokens that themselves begin with `http://` or `https://` are URL-shaped positionals.

If any external-reference flag is present, OR the positional argument is a URL-shaped token (begins with `http://` or `https://`), capture the URL value and route to the **External-reference branch** at the end of this Steps section; skip Step 0's discrete-step gate and Step 1's distill-vs-restart fork — though Step 0's err-toward-distilling principle still informs sub-step B.1's body authoring (see the External-reference branch below). The external-reference path has its own thin-body authoring and its own `bees create-ticket` invocation — Steps 1, 2, 3a, 3b, 3c, and the inner sub-steps of Step 3 are not reached on this path. Steps 4 (commit) and 5 (report back) are shared with the in-conversation capture flow.

If no external-reference flag is present and the positional argument is not URL-shaped, proceed to Step 0 below and the standard in-conversation capture flow (Steps 0 → 1 → 2 → 3 → 4 → 5).

### 0. Detect mid-conversation context

Before treating this invocation as cold, judge whether the current Claude Code session already contains substantive context about the issue being filed. The two downstream branches in the "Gather issue information" step (distill vs restart) are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the bug or its scope, root cause, or alternatives considered.
- The user's invocation message (or `/quo-file-issue <description>` argument) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the symptom, repro, suspected root cause, or impact.
- An explicit hint that this is a continuation of a debugging or analytical discussion (e.g., the user has been investigating the bug with the assistant before invoking the skill).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a substantive debugging conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/quo-plan`'s detection step and in the inline-invocation paths of `/quo-write-prd` and `/quo-write-sdd`; keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning, filing, and PRD/SDD authoring.

The heuristic's output feeds the "Gather issue information" step below: distill branch when it fires, restart branch when it does not.

### 1. Gather issue information

Two branches based on the "Detect mid-conversation context" step's heuristic. Use the distill branch when the heuristic fires; use the restart branch otherwise (solo invocation from a fresh session, or `/quo-file-issue <description>` with only a one-line description and no rich preceding discussion).

#### 1a — Distill branch (heuristic fires)

Skip the "What's the issue?" prompt entirely — the prior conversation already contains the substance. Instead:

1. Distill the prior session into a draft Issue body that matches the body-template shape defined in the "Create the ticket" step — Description / Current behavior / Expected behavior / Impact / Suggested fix, plus the OPTIONAL sections defined in that body-template block when the conversation supplies the relevant content. Specifically:
   - **`## Background and rationale`** — populate when the prior conversation includes substantive root-cause analysis, alternative-cause ruling, or trade-off discussion. Capture *why* this is a bug, *which root causes were ruled out and why*, and any *trade-offs* surfaced during analysis. Omit the section entirely if the conversation has none of that content.
   - **`## Decisions and rejected alternatives`** — populate when the prior conversation discussed alternative fixes and the user chose one path over others. Capture the alternatives considered and the reasoning for choosing the suggested fix, so `/quo-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Omit the section entirely if the conversation didn't weigh alternative fixes.
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
<OPTIONAL — populated when the suggested-fix path was chosen over alternatives that were considered; omitted entirely otherwise. Captures the alternatives considered and the reasoning for choosing the suggested fix, so `/quo-fix-issue`'s engineer doesn't re-litigate decisions the user has already made. Distilled from the prior conversation by the distill branch (1a) of the "Gather issue information" step when the "Detect mid-conversation context" heuristic fires; absent on the restart branch (1b).>

## Doc divergence noted
<OPTIONAL — populated when the issue surfaces a doc claim that's wrong (or a doc gap); omitted otherwise. Plain prose pointing at the file/section that's wrong and what's wrong about it. Use the canonical doc paths from CLAUDE.md "Documentation Locations" — `Internal architecture docs (SDD)`, `Customer-facing docs`, and the PRD-equivalent if the project has one — as the pointers. `/quo-fix-issue`'s doc-writer pass consumes this section during fix execution; do NOT edit project docs from this skill.>
```

**OPTIONAL-section contract.** The three sections marked OPTIONAL above — `## Background and rationale`, `## Decisions and rejected alternatives`, and `## Doc divergence noted` — are **omitted entirely** from the Issue body when the issue does not have content for them. Do **not** render them as stub headings followed by empty bodies, "N/A", or "TBD" — leave the section heading out of the markdown completely.

This is intentionally different from the `/quo-write-prd` and `/quo-write-sdd` skills' mandatory-always-present rule. PRD/SDD docs use a fixed contract where every section is always rendered (even when empty) so downstream readers can rely on the shape. Issues, by contrast, come in many sizes — one-line bug reports filed via `/quo-file-issue "<description>"` vs deep analytical sessions distilled into a rich Issue body. Requiring the rationale sections always-present would force noise (empty stubs, "N/A" placeholders) into casual issues without adding value. Casual one-line invocations produce Issues without these sections; analytical issues populate them with substance.

#### 3b. Doc-divergence review (decides whether `## Doc divergence noted` is included)

Before writing the body to the temp file, review whether the issue description implies the project's spec docs contain incorrect information. The outcome of this review decides whether the OPTIONAL `## Doc divergence noted` section appears in the body composed in 3a.

This review is **observation-only** — do NOT edit any of the project documentation files configured under CLAUDE.md `## Documentation Locations`, the README, or any other project documentation file. The remediation belongs to `/quo-fix-issue`'s doc-writer pass, which consumes the `## Doc divergence noted` section during fix execution.

Use the paths configured in CLAUDE.md `## Documentation Locations` — specifically `Internal architecture docs (SDD)` and `Customer-facing docs` (the README-equivalent). The Documentation Locations section has no canonical "PRD" key; if the project has a PRD-equivalent at a known path, include it in the review, otherwise skip the PRD pointer.

Examples of doc divergence to watch for:
- Documenting behavior that is now known to be wrong
- Missing config variables or wrong defaults
- Wrong API contracts or field names
- Incorrect architecture descriptions

If divergence is observed, include a `## Doc divergence noted` section in the body composed in 3a. Format: plain prose pointing at the file/section that's wrong and what's wrong about it; reference the file by the path from CLAUDE.md `## Documentation Locations`. If no divergence is observed, omit the section entirely.

When the distill branch (1a) of the "Gather issue information" step has already populated `## Doc divergence noted` from the prior conversation, this review either confirms the existing capture or refines it; it does not add a duplicate section.

#### 3c. Write the body to a temp file and run `bees create-ticket`

1. Pick a temp path under the namespaced workflow scratch dir: `/tmp/.quorum/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.quorum\bees-body-<short-suffix>.md` on Windows. Create the `.quorum` subdir if it does not yet exist:

   ```bash
   # POSIX (bash / zsh):
   mkdir -p /tmp/.quorum
   ```

   ```powershell
   # Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
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

   The scratch file is **not** removed after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. The OS / the user reclaims them on their own cadence.

### External-reference branch (reached when `--reference` / `--from-github` is set, or when the positional argument is a URL)

This branch handles the external-reference invocation modes parsed by the "Mode fork" step above. When this branch runs, Steps 1, 2, 3a, 3b, and 3c are **not** reached — this branch produces the Issue body and runs `bees create-ticket` itself. Flow rejoins the standard path at Step 4 (commit) and Step 5 (report back).

The dedupe sub-step (A) below runs **first**, before any body authoring or ticket creation. The dedupe behavior applies uniformly to every entry surface that converges on this branch: bare-URL positional (e.g. `/quo-file-issue https://example.com/...`), `--reference <url>`, `--from-github <url>`, any future `--from-<source>` aliases, and the inline-invocation `url:` payload from the Skill tool. A future maintainer adding another alias must NOT introduce a code path that bypasses Sub-step A.

#### A. Dedupe check against existing open Issues

Before authoring a body or running `bees create-ticket`, query the Issues hive for any open Issue whose `reference_materials` already points at the same URL. The dedupe gate fires unconditionally on this branch — both on the user-typed slash-command path AND on the inline-Skill-tool dispatch path. Do NOT short-circuit the gate when invoked programmatically; the dedupe `AskUserQuestion` is the user's only opportunity to disambiguate, and programmatic callers honor it identically to user-typed invocations (per the `## Inline invocation via the Skill tool` contract section's behavioral-guarantees block).

**Status scope.** The query filters on `status=open` only. Closed-and-archived Issues MUST NOT trigger the dedupe prompt — those are already-fixed bugs, and surfacing them on a re-file would confuse the user into choosing "Use existing" against a closed ticket.

**Match semantics.** Match is **exact-string** on `reference_materials[*].value` against the captured URL. Iterate the `reference_materials` array entries on each candidate ticket (a Bee may carry multiple) and consider the ticket a match if ANY entry's `value` equals the URL byte-for-byte. Do NOT introduce trailing-slash normalization, host-case normalization, query-string stripping, or any other fuzzy-match heuristic — exact-string is intentional and matches what sub-step D (`--reference-materials`) writes today.

##### A.1. Run the bees query (two-step canonical path)

The query path defaults to a **two-step canonical fallback**. The implementer MAY substitute a single freeform-query that places `reference_materials` in a stage-filter clause if and only if the installed bees CLI supports `reference_materials` as a stage-filter term — verify against `bees execute-freeform-query --help` at implementation time. As of this skill's authoring time, `reference_materials` is NOT a supported stage-filter term (the supported terms are `type`, `status`, `title~`, `tag~`, `id`, `parent`, `guid`, `hive`, `hive~` plus the four graph stages), and the `report:` clause likewise rejects `reference_materials`, so a single freeform-query that *reports* `reference_materials` is also not viable. Both reads of `reference_materials` therefore go through `bees show-ticket`. If a future bees CLI version adds `reference_materials` to the stage-filter vocabulary, the one-step path becomes viable — preserve the same observable contract (`status=open` scope, exact-string match on `reference_materials[*].value`, three-way `AskUserQuestion` on hit) when switching paths.

Step 1 — enumerate all open Issues by ID, title, and status. The single-quoted YAML literal works identically on POSIX bash/zsh and Windows PowerShell, so a single labeled block covers both:

```bash
# POSIX (bash / zsh) and Windows (PowerShell) — single-quoted YAML literal works identically:
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues, status=open]
report: [title, ticket_status]'
```

Step 2 — batch-read the candidate tickets' bodies (which include `reference_materials`) and filter client-side. The `bees show-ticket --ids <id1> <id2> ...` invocation is OS-agnostic but the labeled comment line is required per design rule 2:

```bash
# POSIX (bash / zsh):
bees show-ticket --ids <id1> <id2> ...
```

```powershell
# Windows (PowerShell):
bees show-ticket --ids <id1> <id2> ...
```

Parse the JSON result, iterate each ticket's `reference_materials` array, and keep tickets where any entry's `value` equals the captured URL exactly. The result is a (possibly empty) list of matching open Issue tickets, each with its `ticket_id`, `title`, and `ticket_status` already in hand from Step 1's `report:` projection.

##### A.2. Disambiguate via `AskUserQuestion`

Three branches based on the match-list size:

- **Zero matches.** Skip the prompt and continue to Sub-step B (Author a thin Issue body). The skill behaves exactly as it did before this dedupe check existed.
- **Exactly one match.** Issue an `AskUserQuestion` with exactly three finite choices (`AskUserQuestion` is multi-choice only — no fake free-text option per CLAUDE.md `## AskUserQuestion usage`):
  - **`Use existing`** — return the matched ticket ID without invoking `bees create-ticket`. The inline-invocation return shape carries `action=reused-existing` (lowercase, hyphenated — exact spelling, matching the `## Inline invocation via the Skill tool` contract). Skip Sub-steps B, C, D **and** skip Step 4 (commit) — no new ticket file was created and no `git add` / `git commit` runs on this path, which would either fail with "nothing to commit" or silently fold unrelated staged changes into a misleading `File issue: <title>` commit. Proceed directly to Step 5 (report back), which surfaces "Reusing existing Issue <id>" per Step 5's dedupe-reuse clause.
  - **`File new`** — proceed with Sub-steps B, C, D as if no match existed. The return shape carries `action=created`.
  - **`Cancel`** — exit the skill cleanly. See "Cancel exit hygiene" below.

  The prompt body MUST include the matched ticket's ID, title, and status so the user can decide intelligently. Example prompt-body shape (literal — adjust the values to the matched ticket):

  ```
  An open Issue already references this URL:

    ID:     b.<id>
    Title:  <matched ticket title>
    Status: open

  Use the existing Issue, file a new one anyway, or cancel?
  ```

- **More than one match** (rare, but possible from prior partial runs). Issue a single `AskUserQuestion` with one option per candidate plus `File new` and `Cancel`. `AskUserQuestion` permits up to 4 questions per call but does not bound option count per question, so any reasonable candidate set fits. Use a short option-label format like `Use existing (b.<id>)` so each label fits the option-label budget; surface the long-form ID/title/status for every candidate in the prompt body. Picking any `Use existing (b.<id>)` returns that ticket's ID with `action=reused-existing` and follows the same dedupe-reuse skip-Step-4 path as the single-match `Use existing` branch above (no `git add` / `git commit`, proceed directly to Step 5); `File new` and `Cancel` behave as in the single-match branch.

##### A.3. Cancel exit hygiene

When the user picks `Cancel`, exit the skill cleanly **before any mutation**:

- Do NOT invoke `bees create-ticket` (or any other mutating bees command).
- Do NOT write a scratch body file under `<tempdir>/.quorum/` — Sub-step D's `--body-file` fallback is not reached on this path; create no file the OS will inherit.
- Do NOT proceed to Step 4 (commit) — there is nothing to commit.
- Do NOT proceed to Step 5 (report back) — Cancel is a clean abort, not a successful filing.

The Cancel branch leaves the bees workspace and the host repo byte-for-byte unchanged from before the skill ran.

#### B. Author a thin Issue body (2-3 sentences)

The Issue body in external-reference mode is a thin summary, **not** the full body-template from Step 3a. Two sources for the summary, in order of preference:

1. **Mid-conversation context.** If the surrounding conversation already explains what's at the URL — the user has been discussing the bug, has linked the URL inline, or has asked the assistant to read the URL — distill 2-3 sentences from that context. Mid-conversation awareness still applies on this path; the err-toward-distilling principle from Step 0 carries over.
2. **Fetch the URL via `WebFetch`.** If the conversation does not explain what's at the URL but the URL is fetchable (public web page, reachable from the current network), use `WebFetch` to read it and distill 2-3 sentences from the upstream content. This is optional — the authoritative spec content stays at the URL and `/quo-fix-issue` fetches it again at fix time; the body summary is for human readers of the Issue, not for downstream agents.
3. **Ask the user.** If neither prior context nor `WebFetch` produces a useful summary (e.g., the URL is auth-gated or otherwise unreadable), ask in prose for a one- or two-sentence summary of what quorum needs to know about the referenced source. Use prose rather than `AskUserQuestion` — per CLAUDE.md `## AskUserQuestion usage`, that tool is multi-choice only and is wrong for free-text answers.

The body shape is intentionally **flat** — no `## Description` / `## Current behavior` / `## Expected behavior` / `## Impact` / `## Suggested fix` headings. Those sections exist to extract structure from in-conversation capture; on this path the structure lives at the URL, and forcing the headings into a thin body would either duplicate URL content or render mostly-empty stubs. The OPTIONAL `## Doc divergence noted` section from Step 3a may still be appended on this path **only when** the user (or the surrounding conversation) explicitly flags a doc-divergence observation that the external source does not already capture; in routine external-reference filings the section is omitted. Step 3b's automatic doc-divergence review does **not** run on this path — consistent with the Mode fork's "Steps 1, 2, 3a, 3b, 3c, and the inner sub-steps of Step 3 are not reached on this path" — so the section is appended only when the user or the surrounding conversation initiates it, never as the result of an automatic review pass.

The thin body should also include a single line near the top naming the referenced source and the URL, so a reader of the Issue body alone can tell where to look — for example:

```markdown
External reference: GitHub Issue https://github.com/owner/repo/issues/123

<2-3 sentence summary distilled from the URL or user description>
```

The `external reference` line is a convention, not a contract — `reference_materials` is the load-bearing signal that downstream `/quo-fix-issue` reads.

**Title.** Pick a concise title (under 80 characters) that names what the upstream issue is about, not just the URL slug. If the user supplied a title or the conversation distilled to one, prefer that; otherwise summarize from the upstream content (or ask the user in prose for a title if neither source is available).

#### C. Pick a resolver name (URL-pattern heuristic)

The resolver name written into `reference_materials` is selected by URL pattern matching. The bees CLI may not yet have a concrete resolver implementation registered for these names — that is intentional and out of scope for this skill (concrete resolvers are tracked separately as their owners materialize). The skill writes the canonical resolver name regardless; downstream `/quo-fix-issue`'s PM and Engineer fall back to fetching the URL via `WebFetch` until a real resolver lands.

The pattern table:

| URL shape | Resolver name |
|---|---|
| `https://github.com/<owner>/<repo>/issues/<n>` (and similar GitHub Issue URLs) | `github-issue` |
| `https://linear.app/<workspace>/issue/<id>` (and similar Linear ticket URLs) | `linear-issue` |
| Anything else (Slack archive link, internal bug tracker, generic web page) | `url` |

The URL host and path determine the resolver name — match on host first, then path-shape. When in doubt, fall back to `url`. The match is best-effort and informational; it primarily helps human readers and future resolver implementations identify the source class.

**Concrete-resolver gap (intentional).** No concrete `github-issue`, `linear-issue`, or `url` resolver exists in the bees CLI today. That is a separate piece of work, owned by whoever builds each resolver. Until those land, the workflow falls back to `WebFetch` on the URL whenever the upstream content is needed — see `agents/pm.md` and `agents/engineer.md` for the fetch convention. Writing the canonical resolver name now (rather than e.g. always writing `url`) future-proofs existing Issue tickets so they do not need to be migrated when concrete resolvers ship.

#### D. Run `bees create-ticket` with `--reference-materials`

Unlike the in-conversation capture path, the external-reference branch passes the body inline (it is short, one-line-ish) and the URL as a `--reference-materials` JSON argument. No temp body file is written on this path.

The exception: if the thin body authored in (B) contains anything that would trip Claude Code's command-injection guard — a newline followed by a `#` heading, backticks, or shell-special characters — fall back to the temp-file convention from Step 3c (write the body under `<tempdir>/.quorum/bees-body-<short-suffix>.md` after creating the namespaced subdir, then pass `--body-file <path>`). Most thin bodies will fit on `--body` cleanly; the temp-file fallback is the safety valve.

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

After the ticket is created, proceed to Step 4 (commit) and Step 5 (report back). The Step 5 summary should call out that this Issue was filed in external-reference mode and name the referenced URL, so the user knows `/quo-fix-issue` will fetch upstream content rather than read the body as-spec.

### 4. Commit the ticket

Stage and commit the ticket file. **Do not hardcode the `.bees/issues/` path.** `/quo-setup` lets the user choose where each hive lives — in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/issues/` silently stages nothing when the user picked a sibling path.

To learn the in-repo Issues hive path, run the bundled helper's NON-MUTATING `resolve-hive-paths` mode. The helper emits the Issues hive's absolute path when it lives inside this repo, or nothing when it lives outside (in which case you stage no hive path here). Run it as a single literal Bash call:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues
```

**Resolving the helper path (sibling-skill resolution).** `hive_commit.py` is shipped by `/quo-execute`; this skill consumes it as a *sibling* bundled script. Resolve its path at runtime from this skill's own base directory: `<this skill's base directory>/../quo-execute/scripts/hive_commit.py`. The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-file-issue`). Use the `..` traversal pattern to reach the sibling skill — this matches the same sibling-resolution discipline used elsewhere in the skill set (e.g., `/quo-fix-issue`'s §7 commit step). On Windows, use backslash separators: `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py`. The resolve mode does NOT validate a `--skill` slug (only the helper's encode-commit mode does), so this consumer needs no addition to the helper's set of recognized skills.

When the helper emits an Issues hive path, `git add` it alongside the ticket body file you just authored, then commit. **Stage only files related to this filing** — the resolved Issues hive path's contents plus the scratch body file under `<tempdir>/.quorum/` (if it was tracked). **Do NOT `git add -A`** — other agents or processes may have in-flight changes in the working tree, and a blanket add would sweep them into this commit. The commit subject is `File issue: <title>`:

```bash
# POSIX (bash / zsh):
git commit -m "File issue: <title>"
```

```powershell
# Windows (PowerShell):
git commit -m "File issue: <title>"
```

If the Issues hive lives outside the repo, the helper emits nothing — no git commit is needed here, the bees CLI has already persisted the ticket. Remind the user that the issue ticket is stored separately (the bees CLI persists it; no git tracking needed for the ticket file itself).

### 5. Report back

Two report shapes based on which path produced the result:

**Happy path — newly-filed Issue (`action=created`).** Show the user:
- The ticket ID
- The title
- A one-line summary of what was filed
- Whether the issue captured a doc-divergence observation (the `## Doc divergence noted` section in the body) so the user knows `/quo-fix-issue`'s doc-sync pass will consume it.
- If the issue was filed in external-reference mode (bare URL, `--reference`, or `--from-github`): the referenced URL and the resolver name written into `reference_materials` (see sub-step C for how the resolver name is selected from the URL pattern), so the user knows `/quo-fix-issue` will fetch upstream content rather than treat the body as the spec.

**Dedupe-reuse path — matched existing Issue (`action=reused-existing`).** When the External-reference branch's Sub-step A.2 disambiguation returned `Use existing` (single-match) or any `Use existing (b.<id>)` (multi-match), surface the reuse explicitly rather than the file-a-new-ticket bullet list. Show the user:
- A `Reusing existing Issue <id>` headline naming the matched ticket ID.
- The matched ticket's title and status (`open`).
- The dedupe match — i.e. the URL that matched the existing ticket's `reference_materials[*].value`, so the user can confirm the reuse decision was made against the right ticket.

The dedupe-reuse report-back replaces the happy-path bullets; do not also render the file-a-new-ticket summary on this path (no new ticket was filed, and no doc-divergence section was authored on this run).

When invoked inline via the Skill tool, the report shape is structured per the contract section below — return the new (or matched-existing) Issue's ticket ID and final status as the load-bearing payload so the caller can wire its own follow-up state (e.g., kicking off a fix run against the freshly-filed Issue without prompting the user for the ticket ID). On the inline-dispatch path, any human-readable bullet list this skill emits alongside the structured payload is **supplemental** to that payload and does NOT signify run completion of the calling skill — the caller skill's flow continues at its next step after the structured return per the `### Behavioral guarantees` block's "hand-off marker, not a workflow exit" guarantee. The user-typed slash-command path's report-and-exit semantics (the bullet shapes above) are unchanged.

## Inline invocation via the Skill tool

This section is the stable contract for callers that invoke `/quo-file-issue` through the Skill tool rather than as a user-typed slash command. The canonical caller is `/quo-fix-issue`, which dispatches `/quo-file-issue` when it encounters a URL form requiring a freshly-filed Issue (the user pointed `/quo-fix-issue` at a URL rather than a known Issue ticket ID, and the workflow needs to mint — or reuse — an Issue ticket before the fix path can run). Other future callers MAY also invoke this skill via the Skill tool; whatever they pass and consume must match the shape documented here.

### Input shape (caller → this skill)

The Skill-tool caller passes a single free-text `args` string carrying the URL as a positional `url:` field. Recommended shape (project-neutral; the angle-bracketed placeholder is filled by the caller at runtime):

```
url: <url>

summary:
<OPTIONAL — pre-distilled 2-3 sentence summary of the upstream source. When present, the External-reference branch's sub-step B.2 `WebFetch` step is skipped and the supplied summary is used directly as the thin body's summary content.>
```

Any additional context fields the caller may supply — e.g., the OPTIONAL `summary:` block above, or a future caller-supplied title hint — are OPTIONAL. The skill parses the `args` string, captures the URL, and routes execution through the Mode fork's External-reference branch (an inline-invocation `url:` payload is treated as equivalent to `/quo-file-issue --reference <url>`). The resolver-name selection in sub-step C still runs unconditionally on this path; the caller does not pass the resolver name.

### Output shape (this skill → caller)

When the workflow completes, the skill returns to the caller a structured final assistant message naming at least:

- **`issue_ticket_id`** — the Issue ticket ID. On the freshly-filed path this is the ID returned by `bees create-ticket`. On the dedupe-reuse path (when the dedupe disambiguation gate's `Use existing` branch is taken), this is the matched existing ticket ID rather than a freshly-minted one.
- **`issue_status`** — `open` on success. The Issues hive only supports `open` and `done`, so this field is always `open` when the skill returns successfully. The close-out flip to `done` is owned by `/quo-fix-issue` (per its Section 6 close-out), not by this skill.
- **`action`** — exactly one of two values: `created` for a freshly-filed Issue, `reused-existing` when the dedupe path returned an existing ticket. The vocabulary is exactly `created` and `reused-existing` (lowercase, hyphenated). This vocabulary is published here and consumed by the dedupe path; the two MUST agree on the exact spelling.

The caller (e.g., `/quo-fix-issue`) consumes `issue_ticket_id` to dispatch the fix run against the right ticket without prompting the user for the ID, and reads `action` to tell whether a duplicate was deduped (so it can surface "reusing existing Issue <id>" rather than "filed new Issue <id>" to the user).

### Behavioral guarantees

The inline path is functionally identical to the user-typed slash-command path from the Issues hive's perspective; the only difference is how the URL arrives (`args` payload vs `--reference <url>` / bare-URL positional). Specifically:

- **The structured return is a hand-off marker, not a workflow exit.** On the Skill-tool inline-dispatch path, the `issue_ticket_id` / `issue_status` / `action` payload returned to the caller is a hand-off signal for the caller to consume — it does NOT terminate the run. The "caller" on this path is the same conversation orchestrator that invoked the Skill tool (Skill-tool inline dispatch runs in-process, not as a separate process or session), so when the structured return fires, control returns to the caller skill's next step (e.g., `/quo-fix-issue`'s post-resolution working-list display, then its upfront `bees show-ticket --ids` validation pass, then Step 2 onward), not to the user. This is distinct from the user-typed `/quo-file-issue` slash-command path, where Step 5's "Report back" bullet list IS the run's terminal output and the skill exits after rendering it. Inline callers that mistake the structured return for a workflow exit will silently file the Issue and stop, dropping the rest of their flow on the floor; this guarantee exists to prevent that failure mode.
- **User-facing AskUserQuestion gates still fire on the inline path.** The Skill-tool caller does NOT short-circuit any user-facing approval. The user owns the approval, not the caller. The gates that still fire are, at minimum:
  - The in-conversation capture path's distilled-draft `Approve` / `Revise` / `Cancel` gate (Step 1a of the "Gather issue information" step). Note: although a Skill-tool `url:` payload routes through the External-reference branch (which does not reach Step 1a in normal operation), the gate is named here for completeness — if a future inline path drops the URL flag and lands on the in-conversation capture flow, the distill gate is still expected to fire.
  - The External-reference branch's body-confirmation step (sub-step B.3) — the path where the user is asked in prose for a one- or two-sentence summary when neither prior conversation nor `WebFetch` produces a useful summary. When the caller supplies the OPTIONAL `summary:` block in the `args` payload, sub-step B.2's `WebFetch` is skipped and the supplied summary is used directly, which routinely satisfies sub-step B's summary need without reaching the prose ask in B.3 — but the branching logic itself is not bypassed by the inline path.
  - The dedupe disambiguation gate. When the External-reference branch's Sub-step A.2 dedupe disambiguation matches an existing open Issue with the same URL or near-duplicate scope, the user is asked via `AskUserQuestion` whether to use the existing ticket, file anyway, or cancel. The inline path does not bypass this gate; the caller waits for the user's choice and then receives the appropriate `action` value (`reused-existing` on `Use existing`, `created` on `File anyway`) in the output payload.
- **Idempotency.** Re-running the skill against the same URL produces an idempotent result — a duplicate file does NOT create a duplicate ticket. The dedupe path returns the existing ticket ID with `action=reused-existing`. This is the observable behavior callers and reviewers can verify by invoking the skill twice in a row against the same URL.
- **Lifecycle.** The Issue ticket is created at `status=open` (the only status the Issues hive supports for new tickets). The inline path does NOT flip the Issue to `done` — the close-out flip is owned by `/quo-fix-issue` per its Section 6 close-out, not by this skill or its callers. `issue_status` in the output payload is therefore always `open` on a successful return.
- **Scratch-file convention.** When the External-reference branch falls back to the `--body-file` path (sub-step D's safety valve for thin bodies that contain `#` or shell-special characters), the scratch file is written under `<tempdir>/.quorum/` with create-if-absent, and is never removed. Identical to the user-typed path.

### Cross-reference

The gate set named under "User-facing AskUserQuestion gates still fire on the inline path" is keyed off the gates that fire in the existing skill flow — Step 1a's distill gate, sub-step B.3's prose confirmation, and the dedupe disambiguation gate (sub-step A.2). If a future Task adds, removes, or renames a user-facing gate in this skill, this contract section MUST be revised in lockstep so callers' expectations match the skill's actual behavior. Likewise, the `action` vocabulary (`created` / `reused-existing`) is a published string contract — changing the spelling on either side without updating the other will silently break dedupe-aware callers.
