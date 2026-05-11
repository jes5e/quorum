---
name: quo-write-sdd
description: Author or revise an SDD as a `t1=Doc` child titled `SDD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/quo-write-sdd <spec-bee-id>`), or inline from `/quo-plan` via the Skill tool when initial specs are being authored.
argument-hint: "<spec-bee-id>"
---

## Overview

This skill authors or revises an SDD (Software Design Document) as a child ticket under an existing Spec Bee in the Specs hive. The SDD ticket is a `t1=Doc` child with title exactly `SDD` (case-sensitive — downstream skills key off this exact title to differentiate the SDD from the PRD child of the same Spec Bee). The SDD body always contains the same seven sections in the same order; downstream cold-session agents rely on that fixed shape.

We call it an SDD (Software Design Document) rather than SRD because the document captures architectural design and existing-behavior contracts as much as requirement statements.

The skill has two invocation paths:

1. **Solo invocation** — `/quo-write-sdd <spec-bee-id>` from a Claude Code prompt. Used when revising an existing SDD or authoring one against a Spec Bee whose context lives in the bees ticket rather than the current conversation. The full workflow below covers this path.
2. **Inline invocation via the Skill tool** — invoked by another skill (canonically `/quo-plan` while it is authoring a new Spec Bee) through the Skill tool, with the Spec Bee ID and conversation-distilled scope passed as arguments. The handoff contract — input shape, output shape, behavioral guarantees — is documented in the dedicated `## Inline invocation via the Skill tool` section below the workflow.

Both paths share the same underlying flow: detect prior context, read the Spec Bee, detect any existing SDD child, gather codebase research from the Explore agent, then either distill prior context or run cold-discovery questions to fill in the requirement / fixture / behavior detail the codebase research cannot supply, write the seven required sections, create-or-update the SDD child, promote `drafted → ready` on approval. Inline invocation is just the canonical case where the mid-conversation detection branch (Step 0 below) fires.

## Preconditions

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Specs hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`).
- CLAUDE.md contains a `## Documentation Locations` section. The codebase-exploration step below reads architecture-doc paths from this section as supporting context for the Explore agent's research, and the `## Documentation` section of the SDD body lists the docs the doc-writer agent will need to update post-implementation.

Note: quo-write-sdd does **not** require CLAUDE.md `## Build Commands`. This skill authors an SDD ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/quo-execute` and `/quo-fix-issue` when they actually execute the work, not at SDD-authoring time.

If the precondition is missing, stop with `Run /quo-setup first.` and direct the user there.

## Workflow

This workflow covers both invocation paths. Solo invocation (`/quo-write-sdd <spec-bee-id>`) lands at Step 0 with a likely-cold prompt window and typically routes through the discovery branch in Step 4. Inline invocation via the Skill tool (e.g., from `/quo-plan`) lands at Step 0 with substantive prior context already in the prompt window and routes through the distill branch in Step 4. Steps 1, 2, 3, 5, 6, 7, 8, and 9 run identically on both paths. The Explore-agent codebase-research dispatch in Step 3 runs on both branches — the conversation rarely supplies real module names or test-fixture conventions, so the distill branch replaces only the user-interview discovery step in Step 4, not the codebase research in Step 3.

The skill assumes the Spec Bee already exists; it does not create one. If the user invokes `/quo-write-sdd` solo with no `<spec-bee-id>` argument, ask them in prose for the Spec Bee ID and let them reply in their next turn — do NOT use `AskUserQuestion`, since ticket IDs are free-text answers, not a finite set of choices. (Inline callers always pass the Spec Bee ID per the contract section below, so this prompt only fires on the solo path.)

### 0. Detect mid-conversation context

Before treating this invocation as a cold solo run, judge whether the current Claude Code session already contains substantive context about the feature this SDD is meant to capture. The two downstream branches in Step 4 (distill vs restart) are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the feature's design, architectural constraints, affected modules, data models, or alternatives considered.
- The user's invocation message (or `/quo-write-sdd <spec-bee-id>` arguments / Skill-tool args) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the design, contracts, fixtures, or open architectural questions.
- An explicit hint that this is a continuation of a planning or design discussion (e.g., the user has been planning the feature with the assistant before invoking the skill, or the Skill-tool caller — canonically `/quo-plan` — passes distilled scope alongside the Spec Bee ID per the contract section below).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a 30-minute discovery conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/quo-write-prd`'s Step 0 and `/quo-file-issue`'s Step 0; keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning, filing, PRD authoring, and SDD authoring.

The heuristic's output feeds Step 4 below: distill branch when it fires, restart branch when it does not. Steps 1, 2, and 3 run identically on both branches — including the Explore-agent codebase-research dispatch in Step 3, which is necessary on both paths because the conversation rarely supplies real module names, file paths, or test-fixture conventions.

### 1. Read the Spec Bee

Fetch the Spec Bee body for context. The Spec Bee's body, title, and any prior children all inform what the SDD needs to capture.

```bash
# POSIX (bash / zsh):
bees show-ticket --ids <spec-bee-id>
```

```powershell
# Windows (PowerShell):
bees show-ticket --ids <spec-bee-id>
```

If the Spec Bee does not exist or is not in the Specs hive, surface the error and stop — do not attempt to fall back to creating a Spec Bee from scratch (that is `/quo-plan`'s responsibility).

Also read any architecture/customer docs configured in CLAUDE.md `## Documentation Locations` so the Explore agent in Step 3 has accurate pointers to the existing-system context. Use the canonical contract keys (`Internal architecture docs (SDD)`, `Customer-facing docs`, `Engineering best practices`) to resolve the paths.

### 2. Detect existing SDD child

Determine whether an SDD child already exists under this Spec Bee. The skill is idempotent — re-running `/quo-write-sdd <same-spec-bee-id>` updates the existing SDD ticket rather than creating a duplicate.

Use `bees execute-freeform-query` with a `parent=<spec-bee-id>` + exact-title filter. The query is regex-based on title; pin both ends so the match is exact and case-sensitive (the SDD child title is exactly `SDD`):

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^SDD$]
report: [ticket_id, title, ticket_status]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^SDD$]
report: [ticket_id, title, ticket_status]'
```

Interpret the result:

- **Zero matches** — no existing SDD child. Step 6 below will use `bees create-ticket` to create one.
- **Exactly one match** — capture the matched ticket ID; Step 6 will use `bees update-ticket --ids <sdd-id>` to update it in place.
- **More than one match** — should not happen given the exact-title filter. Surface the anomaly to the user and stop; the user must decide which ticket is the canonical SDD before this skill can proceed.

### 3. Codebase exploration via the Explore agent

The SDD's `## Codebase exploration findings` section (defined in Step 5) must be sourced from real, verified codebase research — not guessed. Dispatch the **Explore** subagent (`subagent_type=Explore`) to gather the material.

**What to ask the Explore agent.** Construct the prompt around the feature scope you read from the Spec Bee in Step 1, and ask the agent to investigate (at minimum):

- **Architecture.** Which top-level subsystems / packages / modules are touched by this feature? How do they fit into the existing architecture?
- **Affected modules.** What specific files, classes, functions, or routes will the implementation likely change or extend? Cite real names from the actual repo.
- **Existing patterns.** What in-repo conventions, idioms, or design patterns is the new code expected to follow (e.g., how similar features are wired today, how errors are surfaced, how config flows through)?
- **Data models.** What schemas, types, or persistent entities are involved? Where are they defined?
- **Test fixtures.** What test-fixture conventions exist in the repo (helpers, factories, sample data files, mocking utilities) that engineers should reuse rather than reinvent? Cite file paths.
- **Configuration.** What configuration knobs (env vars, settings files, feature flags) are involved? Where do they live and how are they read?

Provide the agent with the architecture-doc paths from CLAUDE.md `## Documentation Locations` so it can ground its research in the project's stated design intent rather than spelunking blind.

**How to consume the agent's findings.** The Explore agent returns a structured response describing what it found. Use that response as the source material for the SDD's `## Codebase exploration findings` section. Cite real module / file / function names from the agent's output — do **not** fabricate names. If the agent reports it could not find a definitive answer to one of the prompts, that is the signal to use the `RESEARCH NEEDED` flag described next, not the signal to invent a plausible-sounding answer.

**`RESEARCH NEEDED` flag.** When the Explore agent surfaces ambiguity that needs follow-up rather than a confident answer (e.g., "the routing layer is split between two modules and I could not determine which one owns this concern"), mark the affected spot in the SDD body inline as:

```
RESEARCH NEEDED: <one-line question describing what still needs to be investigated>
```

This convention lets downstream readers (the Engineer dispatched by `/quo-execute`, the doc-writer agent) see at a glance which spots are confidently grounded versus which need a follow-up pass. Never silently smooth over an ambiguity by writing a confident-sounding sentence; always tag it with `RESEARCH NEEDED`.

### 4. Gather requirement / fixture / behavior detail (distill or restart)

Two branches based on Step 0's heuristic. Use the distill branch when the heuristic fires; use the restart branch otherwise (cold solo invocation against a Spec Bee with no substantive prior conversation context). Both branches feed the same downstream Step 5 body assembly — they differ only in *how* the requirement / fixture / existing-behavior / rationale / decision content is sourced. Step 3's Explore-agent codebase-research dispatch has already run before this step on both branches, so the codebase context is in hand by the time Step 4 starts.

#### 4a — Distill branch (heuristic fires)

Skip the discovery questions entirely — the prior conversation (or the distilled scope passed by the Skill-tool caller per the contract section below) already contains the substance for the user-interview half of the SDD. Instead:

1. Read the prior context (the in-session conversation, any `Description` / scope content passed as a skill argument, and — on inline invocation — the distilled scope payload supplied by the caller). Cross-reference the Spec Bee body fetched in Step 1 and the Explore agent's findings from Step 3 to make sure the distilled draft is consistent with what the Spec Bee already says about the feature and with the real codebase context the agent surfaced.

2. Distill the prior context into a draft populating the seven required SDD sections defined in Step 5. Pay particular attention to:
   - **`## Background and rationale`** — populate with substance distilled from the prior conversation: prior-conversation context, root-cause framing, design constraints, why-now justification, and any architectural framing that informed what shape the design takes. This is precisely where prior-conversation richness should land — when the heuristic fires, this section should almost never be the explicit-`none` placeholder, because the heuristic firing means there *is* rationale content to capture.
   - **`## Decisions and rejected alternatives`** — populate when the prior conversation weighed alternatives (alternative architectures, alternative module boundaries, alternative data models, alternative contracts). Capture each decision and the alternatives considered alongside the reasoning, so downstream agents (`/quo-execute`'s Engineer, PM, breakdown) don't re-litigate decisions the user has already made. Same as `## Background and rationale`: when the heuristic fires, this section should almost never be the explicit-`none` placeholder.
   - **`## Requirements`** — populate the SR-style requirement groups from the functional behaviors the prior conversation covered. Probe for groupings (e.g., "API behavior", "data validation", "logging / observability") so the requirement IDs in Step 5 can be organized by domain. The prior conversation typically covers the high-level requirements; if a particular SR group is partially covered, capture what is there and mark gaps explicitly rather than fabricating filler.
   - **`## Existing Behavior`** — populate the high-level scope from the prior conversation's discussion of contracts that must NOT change (existing API shapes, persisted-data layouts, on-the-wire protocol fields, configuration knobs whose meaning external callers depend on). The Explore agent's findings from Step 3 ground the specific module names and file paths; the prior conversation grounds the high-level "must preserve" intent.
   - The remaining sections (`## Codebase exploration findings`, `## Test Fixtures`, `## Documentation`) — populate primarily from the Explore agent's findings (Step 3) and from CLAUDE.md `## Documentation Locations`. The prior conversation rarely contains real module names or test-fixture conventions; the Explore agent's output is the load-bearing source for those sections. Mark anything the prior context does not cover and the agent did not surface as `RESEARCH NEEDED: <question>` per Step 3's flag pattern, rather than fabricating content.

3. Present the distilled draft to the user for review via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:
   - **Approve** — the distilled draft is good as-is. Proceed to Step 5 / Step 6 with the distilled body as the starting draft for the create-or-update branch.
   - **Revise** — iterate in prose with the user on what to change, then re-present the revised draft via `AskUserQuestion`.
   - **Cancel** — exit the skill cleanly without creating or updating the SDD ticket.

On approve, carry the distilled body forward as the starting material for Step 5 (the body assembly proceeds against the same seven-section template, with the distilled content already populated). The Step 7 approval gate at the end of the workflow is **not** a duplicate of this gate — Step 4a's gate confirms the distilled scope is correct *before* writing it into a ticket; Step 7's gate confirms the final body (after Step 5's quality-bar checks and Step 6's create-or-update) is good before promoting `drafted → ready`. Both gates are necessary on the distill branch.

#### 4b — Restart branch (heuristic does not fire)

Cold solo invocation against a Spec Bee with no substantive prior conversation context requires discovery — the skill must gather enough material to populate the requirement / fixture / behavior / rationale / decision sections in Step 5 that the Explore agent's codebase findings cannot answer alone.

The exact question list is the skill author's call at runtime; below is a reference set covering the sections in Step 5 that the Explore agent's output does not fully populate.

- **What functional requirements must the implementation satisfy?** — prose. Captures the substance for `## Requirements`. Probe for groupings (e.g., "API behavior", "data validation", "logging / observability") so the requirement IDs in Step 5 can be organized by domain.
- **What behavior must NOT change?** — prose. Captures `## Existing Behavior`. Probe for contracts the implementation must preserve: existing API shapes, persisted-data layouts, on-the-wire protocol fields, configuration knobs whose meaning callers depend on.
- **Which test-fixture conventions apply, beyond what the Explore agent surfaced?** — prose. Captures `## Test Fixtures`. The Explore agent's output likely lists existing fixtures; the user's answer here either confirms those are the relevant ones or names additional conventions the agent missed (e.g., "always use the `make_fake_user` factory rather than constructing dicts inline").
- **Which docs must be updated when this lands?** — prose. Captures `## Documentation`. The default expectation is that the cumulative project docs at the paths configured in CLAUDE.md `## Documentation Locations` (PRD, SDD, README) will need updates; ask whether any other docs (engineering best practices, customer-facing release notes, internal runbooks) also need post-implementation passes.
- **What background / rationale should be captured?** — prose. Captures `## Background and rationale`. Empty answer is fine — Step 5 renders the explicit-`none` placeholder when this is empty.
- **What decisions and rejected alternatives should be captured?** — prose. Captures `## Decisions and rejected alternatives`. Empty answer is fine — same explicit-`none` treatment.

Use `AskUserQuestion` only for genuinely finite-choice prompts (e.g., yes / no / partial questions); use prose questions for free-text answers, per CLAUDE.md `## AskUserQuestion usage`. Do not invent fake "Use my own answer" / "Pick Other" options on `AskUserQuestion` calls — the harness auto-appends `Type something.` and `Chat about this`, so finite-choice prompts must list only the meaningful alternatives.

On the restart branch, sections `## Background and rationale` and `## Decisions and rejected alternatives` typically render with their explicit-`none` placeholders defined in Step 5 — there's no captured rationale or decision history when the heuristic does not fire. That's the correct shape; do not invent content to fill those sections.

### 5. Author the SDD body

Produce a single markdown body containing the seven required sections in this exact order. **Every section is always rendered** — never silently omit. When a section has no content, fill it with explicit "not applicable" / "none" prose so a downstream cold-session reader can tell apart `the author forgot to populate this section` from `the author considered it and there is genuinely nothing here`.

The seven required sections, in order:

1. `## Codebase exploration findings` — architecture, affected modules, existing patterns, data models, test fixtures, configuration. Content sourced from the Explore agent's output in Step 3. Cite real module / file / function names from the actual repo. Use the `RESEARCH NEEDED: <question>` inline tag wherever the Explore agent surfaced ambiguity that needs follow-up rather than a confident answer. **Mandatory.** If the agent's research turned up genuinely no relevant codebase context (e.g., a brand-new feature in an empty repo), render the section with the explicit phrase `none — Explore agent found no relevant existing codebase context for this feature`.

2. `## Requirements` — numbered SR-style requirement groups documenting what the implementation must do. Use the prefix `SR-` (Software Requirement) followed by a positive integer, organized by domain / concern: `SR-1`, `SR-2`, `SR-3`, etc., with each top-level group optionally subdivided as `SR-1.1`, `SR-1.2` for subordinate requirements within the same domain. Group requirements by domain (e.g., one group per affected subsystem or per cross-cutting concern such as logging or error handling) so a downstream reader can cite a domain's requirements as a unit. Document the chosen groupings with a short heading per group so cold-session agents reading the SDD downstream can cite groups consistently. **Mandatory.** If the feature has genuinely no functional requirements beyond what the PRD states (rare — usually a sign Step 4's discovery did not probe deeply enough), render the section with the explicit phrase `none — see PRD for the full functional requirement set; this SDD adds no SR-style requirements beyond what the PRD already states`.

3. `## Test Fixtures` — test-fixture conventions the implementation must use. Document existing fixture helpers, factories, sample-data file paths, and mocking utilities that engineers should reuse rather than reinvent. Cite real names from the repo (sourced from the Explore agent in Step 3 plus any conventions surfaced in Step 4's discovery). **Mandatory.** If genuinely no test-fixture conventions apply (e.g., the feature has no test surface — rare and usually a sign of underscoping), render the section with the explicit phrase `none — no test-fixture conventions apply to this feature`. Never silently omit this section: a missing `## Test Fixtures` heading is indistinguishable from "the author forgot to think about fixtures", and the most common failure mode that an SDD prevents is engineers hardcoding magic-number test data past existing helper conventions.

4. `## Existing Behavior` — what must NOT change. Document the contracts the implementation must preserve: API shapes, persisted-data layouts, on-the-wire protocol fields, configuration knobs whose meaning external callers depend on. **Mandatory.** If the feature is greenfield and there is genuinely no pre-existing behavior to preserve, render the section with the explicit phrase `none — this is greenfield work; no pre-existing behavior contracts apply`.

5. `## Documentation` — what docs must be written or updated after the implementation lands. List the cumulative project docs (PRD, SDD, README, and any other engineering or customer-facing docs configured in CLAUDE.md `## Documentation Locations`) that the doc-writer agent dispatched by `/quo-execute` will need to update post-implementation. Reference the docs by the canonical path from CLAUDE.md, not by guessed names. **Mandatory.** If the feature is purely internal and genuinely requires no doc updates, render the section with the explicit phrase `none — this feature has no user-visible or architecturally-visible surface and requires no doc updates`.

6. `## Background and rationale` — captures *why* this SDD looks the way it does, including prior-conversation context, root-cause framing, or design constraints that informed the architecture decisions. **Mandatory.** When there is genuinely no captured rationale, render the section with the explicit phrase `none — this SDD has no captured rationale from prior conversation`.

7. `## Decisions and rejected alternatives` — captures the architectural decisions that were made and the alternatives that were considered and rejected, with the reasoning for each. **Mandatory.** When there is genuinely no captured decision history, render the section with the explicit phrase `none — this SDD has no captured decision history from prior conversation`.

**Why every section — including `## Test Fixtures`, `## Background and rationale`, and `## Decisions and rejected alternatives` — is mandatory-always-present.** Downstream cold-session agents (Engineer, PM, Doc Writer dispatched by `/quo-execute`) read the SDD without the conversation that produced it. If a section is silently omitted, a cold-session reader cannot disambiguate `the author forgot to think about this` from `the author considered it and there is nothing to say`. Always rendering each section — with an explicit "none — <reason>" placeholder when the section is genuinely empty — eliminates that ambiguity. This is intentionally different from `/quo-file-issue`'s OPTIONAL-section policy: SDDs are fixed-shape documents that downstream agents rely on; issues come in many sizes from one-line bug reports to deep analytical distillations.

#### Quality bar

Apply these quality checks while authoring:

- **Cite real module names.** Every reference in `## Codebase exploration findings`, `## Test Fixtures`, and `## Existing Behavior` to a module / file / function / fixture must be a real name sourced from the Explore agent's findings (Step 3) or from the user's answers in Step 4. Do not fabricate plausible-sounding names. When the Explore agent could not confidently identify a name, use the `RESEARCH NEEDED: <question>` tag instead.
- **Include test-fixture conventions explicitly.** `## Test Fixtures` is the section that prevents engineers from hardcoding magic-number test data past existing helper conventions. Be specific: name the helpers, name the sample-data files, name the factories.
- **Make architectural decisions traceable.** `## Decisions and rejected alternatives` should let a cold-session agent see *why* the design landed where it did without re-litigating the trade-offs. Capture each decision with the alternatives considered and the reasoning chosen.
- **Prefer SDD-shape over PRD-shape content.** SDDs cover *how the system is built* (architecture, modules, contracts, fixtures); PRDs cover *what users need and why*. If a passage reads like a user story or a business goal, it belongs in the PRD (`/quo-write-prd`), not here. Move it.

### 6. Write body to scratch file and create-or-update the SDD ticket

Author the body to a scratch file under the namespaced workflow scratch dir, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt regardless of the user's allowlist, and inlined markdown is also fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both problems.

Steps:

1. Create the `.quorum` subdir if it does not yet exist:

   ```bash
   # POSIX (bash / zsh):
   mkdir -p /tmp/.quorum
   ```

   ```powershell
   # Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
   ```

2. Use the `Write` tool to write the SDD body to a path under that namespaced scratch dir. Use a collision-resistant filename like `bees-body-<short-suffix>.md` (`/tmp/.quorum/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.quorum\bees-body-<short-suffix>.md` on Windows). Do **not** remove the scratch file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. The OS / the user reclaims them on their own cadence.

3. Branch on Step 2's detection result (the file-flag carries no shell-quoting surface — only the line-continuation character differs between OSes):

   **Branch A — no existing SDD child** (Step 2 returned zero matches). Create the ticket at `status=drafted`:

   ```bash
   # POSIX (bash / zsh):
   bees create-ticket \
     --hive specs \
     --ticket-type t1 \
     --parent <spec-bee-id> \
     --title SDD \
     --body-file <path> \
     --status drafted
   ```

   ```powershell
   # Windows (PowerShell):
   bees create-ticket `
     --hive specs `
     --ticket-type t1 `
     --parent <spec-bee-id> `
     --title SDD `
     --body-file <path> `
     --status drafted
   ```

   The title is exactly `SDD` (case-sensitive). Do NOT pass `--reference-materials` — it is bee-only and child-tier tickets reject it.

   **Branch B — existing SDD child** (Step 2 returned exactly one match — its ticket ID is `<sdd-id>`). Update the body in place:

   ```bash
   # POSIX (bash / zsh):
   bees update-ticket \
     --ids <sdd-id> \
     --body-file <path>
   ```

   ```powershell
   # Windows (PowerShell):
   bees update-ticket `
     --ids <sdd-id> `
     --body-file <path>
   ```

   `bees update-ticket --body-file` replaces the body in full (rewrite semantics). This is the default for body coherence — an SDD revision typically restructures sections rather than appends to them, so a clean rewrite is the right shape. The bees CLI also exposes `bees append-ticket-body --ticket-id <sdd-id> --chunk-file <path>` for explicit append-only revisions, but it is NOT the default for this skill — use it only when the user explicitly asks to append rather than rewrite.

### 7. Confirm with the user, run the spec-review gate, then promote to `ready`

After the create-or-update succeeds, present the resulting SDD ticket ID and a brief summary of what was authored to the user. Use `AskUserQuestion` with finite choices:

- **Approve** — the draft is good as-is. Proceed to the spec-review gate below.
- **Revise** — the user wants changes. Iterate in prose, re-author the body to the same scratch path (or a new one), and re-run Branch B's `bees update-ticket --body-file <path>` against the same `<sdd-id>`. Then re-present.
- **Cancel** — leave the ticket at `status=drafted` and exit. The user can re-invoke the skill later to continue.

#### 7a — Spec-review gate (solo path only; skip on inline path)

After the user approves the SDD body in 7's main `AskUserQuestion`, but **before** issuing the `drafted → ready` promotion, invoke `/quo-spec-review` as an automatic quality gate. This step fires only on the solo path (the user invoked `/quo-write-sdd <spec-bee-id>` directly from the prompt). On the inline-from-`/quo-plan` path, **skip Step 7a entirely** — the orchestrating `/quo-plan` skill runs its own end-to-end `/quo-spec-review` invocation in its Step 4c after both writers complete, and re-running per-writer review here would double-cost the budget for no added signal. Detection: the inline path is identified by the presence of a Skill-tool `args` payload conforming to the inline-invocation contract documented in `## Inline invocation via the Skill tool` below — i.e., a parsed `spec-bee-id:` + `distilled-scope:` block from the Skill-tool caller. This is **not** the same as Step 0's mid-conversation heuristic (which fires on solo runs whenever the prompt window already contains substantive prior context, per the err-toward-distilling principle); using Step 0's heuristic here would silently skip the gate on solo runs with rich prior conversation context, which is wrong. When you detect the inline path via the contract-shaped `args` payload, jump straight from Step 7's main `Approve` answer to Step 7b's promotion call.

On the solo path, run the gate:

1. Invoke `/quo-spec-review <spec-bee-id> --doc SDD` via the Skill tool. The `--doc SDD` flag scopes the review to the SDD child only — the PRD child may be at any state at this point (still `drafted`, already `ready`, or absent), and a standalone SDD revision should not block on or surface PRD-side findings.
2. Read the returned work-item list and apply the loop-back UX described under "Loop-back UX" below.
3. On approve (no findings, or the user explicitly accepted the surfaced findings), proceed to Step 7b's promotion call.
4. On revise (the user asked to address findings), loop back to Step 5's body authoring with the findings supplied as additional context to the revision pass — including, where appropriate, re-dispatching Step 3's Explore-agent codebase research if a finding indicates the cited module names or fixture conventions need re-grounding — then re-run Step 6's write-and-update path: re-write the body to the scratch file and re-run Branch B's `bees update-ticket --body-file <path>`, and re-invoke `/quo-spec-review <spec-bee-id> --doc SDD` for a re-check. Apply the time-budget short-circuit before looping indefinitely.

##### Loop-back UX

`/quo-spec-review` returns a numbered work-item list with severity tags (`blocker`, `suggestion`, `nit`) and — load-bearing — a `**Next action for the orchestrator:**` trailer line that names the precise routing this step must take. **Follow the trailer literally.** The trailer is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory. If the trailer and the prose ever diverge, the trailer wins (and that divergence is a bug in `/quo-spec-review` to file).

Behavioral details (apply after gating per the trailer):

- **No findings** — proceed to Step 7b's promotion immediately. No user prompt needed.
- **Proceed (acknowledge findings)** — the user explicitly accepts the surfaced `suggestion`/`nit` findings; promote anyway. Record the acknowledged findings in the Step 9 end-of-skill report so the choice is visible.
- **Revise** — loop back to Step 5's body authoring with the findings included as revision context, then re-run Step 6's write-and-update path and re-invoke `/quo-spec-review <spec-bee-id> --doc SDD` for a re-check.
- **Proceed anyway (override blockers)** — the user takes explicit responsibility for promoting despite the blockers. Record the override (with the full list of overridden blocker findings) in the Step 9 end-of-skill report so the choice is visible. The override path exists because spec quality is not a hard contract — there are legitimate cases where a `blocker`-tagged finding does not apply (e.g., greenfield work where a "Generic existing-behavior" flag is genuinely the right shape, or work that genuinely touches no contract-key surface despite a "Missing contract-key impact callouts" flag).

`blocker` severity is the primary gate — by default, blockers prevent the SDD child's `drafted → ready` transition until either addressed or explicitly overridden. `suggestion` and `nit` are informational — they surface but do not gate. The user can address them or proceed past them.

##### Time-budget short-circuit

Mirror the pattern in `agents/pm.md` for `/quo-engineer-review` and `/quo-doc-writer-review`: if a single `/quo-spec-review` invocation returns more than ~10 items OR the review-fix-review loop runs more than ~3 turns, stop iterating. Triage the returned list down to `blocker`-severity items only, ask the writer (i.e., this skill's Step 5 body re-authoring path, followed by Step 6's write-and-update path) to address those, then proceed to Step 7b's promotion (with explicit user acknowledgement of the deferred `suggestion`/`nit` items in Step 9's end-of-skill report). These thresholds are guidance, not a hard contract — pick the firmer side when the loop is clearly thrashing on subjective prose-quality nits, the looser side when each finding is high-signal. The 3-turn bound (vs pm.md's 5-turn bound for code/doc review) is intentional: spec content has a much smaller surface area than a Task-sized code diff, so 3 turns of revision usually converges; thrashing past 3 turns almost always means subjective-prose churn rather than missing-content correctness.

#### 7b — Promote the SDD child to `ready`

When the spec-review gate returns control (either because no findings were surfaced, the user explicitly proceeded past surfaced findings, or the time-budget short-circuit was triggered), transition the SDD ticket from `drafted` to `ready`:

```bash
# POSIX (bash / zsh):
bees update-ticket --ids <sdd-id> --status ready
```

```powershell
# Windows (PowerShell):
bees update-ticket --ids <sdd-id> --status ready
```

The Spec Bee's own `drafted → ready` transition is owned by the caller (e.g., `/quo-plan` after both PRD and SDD children are `ready`). This skill is responsible only for the SDD child.

### 8. Idempotency

Re-running `/quo-write-sdd <same-spec-bee-id>` on the same Spec Bee updates the existing SDD ticket rather than creating a duplicate. The detection step (Step 2) is the load-bearing mechanism: it finds the existing SDD child by `parent=<spec-bee-id> + title~^SDD$` and routes the run into Branch B (`update-ticket --body-file`) instead of Branch A (`create-ticket`). This is the observable behavior callers and reviewers can verify by invoking the skill twice in a row against the same Spec Bee.

If the existing SDD is already at `status=ready` when the user re-invokes the skill, the rewrite is still allowed — Step 7's promotion step then re-issues `bees update-ticket --status ready` (idempotent no-op when the status is already `ready`).

### 9. Report back

Show the user:

- The Spec Bee ID.
- The SDD ticket ID (whether created or updated).
- A one-line summary of what the SDD covers.
- The final status (`ready` on approve, `drafted` on cancel).
- Whether this run created a new SDD or revised an existing one (so the user can confirm the idempotency behavior).
- Whether any `RESEARCH NEEDED` tags were embedded in the body — if so, list them so the user knows which open questions still need a follow-up pass.
- Any spec-review findings that were surfaced during Step 7a but not addressed before promotion — split into:
  - **Acknowledged findings** — `suggestion`/`nit` items the user explicitly accepted via "Proceed (acknowledge findings)".
  - **Overridden blockers** — `blocker` items the user explicitly overrode via "Proceed anyway (override blockers)".
  - **Deferred by time-budget short-circuit** — `suggestion`/`nit` items that were deferred when the ~10-item / ~3-turn budget triggered.

  If Step 7a was skipped (inline-from-`/quo-plan` path), state that explicitly so the report is unambiguous about whether the gate ran. If Step 7a ran with no findings, omit the section entirely.

When invoked inline via the Skill tool, the report shape is structured per the contract section below — return the SDD ticket ID and final status as the load-bearing payload so the caller can wire its own follow-up state (e.g., a Plan Bee's `reference_materials`, or the caller's own Spec Bee `drafted → ready` gate).

## Inline invocation via the Skill tool

This section is the stable contract for callers that invoke `/quo-write-sdd` through the Skill tool rather than as a user-typed slash command. The canonical caller is `/quo-plan` while it is authoring a new Spec Bee and needs to delegate SDD authoring to this skill mid-conversation. Other future callers MAY also invoke this skill via the Skill tool; whatever they pass and consume must match the shape documented here.

The contract shape mirrors `/quo-write-prd`'s `## Inline invocation via the Skill tool` section deliberately, so `/quo-plan` can dispatch both writers with the same shape. Any future change to one writer's contract must be applied to the other writer's contract in lockstep — divergence would force `/quo-plan` to maintain two separate dispatch shapes for what should be a symmetric pair of sub-skill calls.

Mid-conversation detection (Step 0 above) is the load-bearing precondition for this path: inline invocation always carries substantive prior context — that's the entire point of delegating from a planning conversation rather than restarting discovery — so the distill branch (Step 4a) always fires on inline invocation. The restart branch (Step 4b) is reserved for cold solo runs and does not fire on the inline path. Step 3's Explore-agent codebase-research dispatch *does* run on the inline path because the planning conversation rarely supplies real module names, file paths, or test-fixture conventions — the codebase research is necessary on every invocation regardless of how rich the prior context is.

### Input shape (caller → this skill)

The Skill-tool caller passes a single free-text `args` string that contains, in order:

1. **The Spec Bee ID.** The ticket ID (e.g., the value the caller obtained from its own `bees create-ticket --hive specs --ticket-type bee` call) the new SDD child will hang off of. This skill does NOT create the Spec Bee; the caller does.
2. **The distilled scope payload.** A markdown-formatted block containing the conversation-distilled scope material the caller has gathered with the user. The block SHOULD cover, at minimum, the high-level architectural framing of the feature (which subsystems are touched, what new contracts are introduced), any existing-behavior constraints surfaced in the planning conversation, and any rationale or rejected alternatives that came up. The caller is encouraged to also supply requirement-shaped content (the substance behind the SR-style requirement groups in Step 5) when the planning conversation produced it. The caller is NOT expected to supply real module names, file paths, or test-fixture conventions — those are sourced by this skill's own Step 3 Explore-agent dispatch.
3. **(Optional) Spec-review findings to address.** A `findings:` block carrying a numbered list of `/quo-spec-review` work items the caller wants this skill to address on the revise pass. Used canonically by `/quo-plan`'s Step 4c spec-review revise loop when `/quo-spec-review` surfaces SDD-tagged findings (or SDD-relevant cross-document findings); omitted on the initial SDD-authoring invocation. Each entry preserves the verbatim severity tag (`[blocker]`, `[suggestion]`, or `[nit]`) and one-line description from the spec-review output, e.g., `1. [blocker] SDD ## Codebase exploration findings — generic "the routing layer" reference; cite the actual module path so the Engineer has a starting point.`. When this field is present, the skill routes the findings into Step 5's body re-authoring path (followed by Step 6's write-and-update path) as additional revision context (the same way Step 7a's revise loop on the solo path consumes them) — the load-bearing effect is that Step 5's authoring pass treats the listed findings as required fixes against the existing SDD body, including (where appropriate) re-dispatching Step 3's Explore-agent codebase research if a finding indicates the cited module names or fixture conventions need re-grounding. The field is OPTIONAL; absent or empty `findings:` means no spec-review findings to address (the normal initial-authoring shape). The shape mirrors `/quo-write-prd`'s `findings:` field exactly so `/quo-plan` can build per-writer payloads with the same template.

Recommended shape for the `args` string the caller passes (project-neutral; the angle-bracketed placeholders are filled by the caller at runtime):

```
spec-bee-id: <spec-bee-id>

distilled-scope:
<markdown block — multi-paragraph, headed sections welcome>

findings:
<numbered list of `/quo-spec-review` work items, each preserving its [severity] tag and one-line description; omit this field entirely on the initial authoring pass>
```

The skill parses the `args` string, captures the Spec Bee ID, the distilled scope payload, and (when present) the spec-review findings, and routes execution through Step 0 → Step 1 → Step 2 → Step 3 → Step 4a (distill branch always fires here) → Step 5 → Step 6 → Step 7 → Step 7b → Step 8 → Step 9 of the workflow (Step 7a is skipped on the inline path; see "Behavioral guarantees" below). The user-facing approval gates in Step 4a (distilled-scope review) and Step 7's main gate (final-body review) still fire on the inline path — the user owns the approval, not the caller.

### Output shape (this skill → caller)

When the workflow completes (whether the Step 4a or Step 7 gate ends in `Approve` or `Cancel`), the skill returns to the caller a structured final message with at least:

- **`sdd_ticket_id`** — the SDD ticket ID the skill created or updated (the `t1=Doc` child titled `SDD` under the Spec Bee).
- **`sdd_status`** — the final status of the SDD ticket (`ready` on approve, `drafted` on cancel or unfinished revision).
- **`action`** — `created` if Step 6's Branch A ran, `updated` if Step 6's Branch B ran. Lets the caller confirm the idempotency behavior matches its expectations.
- **`research_needed`** — a list (possibly empty) of the `RESEARCH NEEDED: <question>` tags embedded in the body, so the caller can surface any unresolved codebase ambiguities to the user before proceeding. This field is specific to SDD output (PRDs do not embed `RESEARCH NEEDED` tags) and is the only intentional departure from `/quo-write-prd`'s output shape — every other field is named and shaped identically (with `prd_*` substituted for `sdd_*`).

The caller (e.g., `/quo-plan`) consumes `sdd_ticket_id` to wire the Plan Bee's `reference_materials` (or equivalent state) at the Spec Bee that owns the new SDD child, and consumes `sdd_status` to gate its own Spec Bee `drafted → ready` transition (which gates on both PRD and SDD children being `ready`).

### Behavioral guarantees

The inline path is functionally identical to the solo path from the Spec Bee's perspective; only the Step 4 distill-vs-restart branch differs and the Step 7a spec-review gate is skipped. Specifically:

- **Idempotency.** Step 2's existing-SDD-child detection runs identically. Re-invoking via the Skill tool against the same Spec Bee updates the existing SDD ticket rather than creating a duplicate (Branch B in Step 6).
- **Seven required sections.** Step 5's body assembly always produces all seven sections. `## Background and rationale` and `## Decisions and rejected alternatives` receive substantive content distilled from the caller's payload (the distill branch should rarely emit the explicit-`none` placeholders for these sections on the inline path, because the caller passing distilled scope is exactly the signal that there *is* rationale and decision content to capture).
- **Codebase research.** Step 3's Explore-agent dispatch runs on every invocation, inline or solo. The planning conversation does not substitute for codebase research — it supplements it.
- **`RESEARCH NEEDED` flag pattern.** The flag pattern from Step 3 / Step 5 still applies on the inline path. If the Explore agent surfaces ambiguity that needs follow-up, the corresponding spot in the SDD body is tagged `RESEARCH NEEDED: <question>`, and the caller is informed via the `research_needed` output field.
- **Lifecycle.** SDD ticket created at `drafted`, transitioned to `ready` on the user's `Approve` in Step 7. Identical to solo.
- **Scratch-file convention.** `--body-file` payloads written under `<tempdir>/.quorum/` with create-if-absent; never removed. Identical to solo.
- **User approval gates.** Both gates (Step 4a's distilled-scope review and Step 7's final-body review) still fire on the inline path. The Skill-tool caller does NOT short-circuit either gate.
- **Spec-review gate (Step 7a) skipped on the inline path.** The orchestrating `/quo-plan` skill runs its own end-to-end `/quo-spec-review` invocation in its Step 4c after both writers complete (covering the PRD and SDD children plus the cross-document consistency pass), so this skill MUST skip its own per-writer Step 7a review when invoked inline. Re-running per-writer review here would double-cost the budget without adding signal — the cross-document pass that `/quo-plan`'s Step 4c invocation runs is strictly more powerful than two single-doc invocations chained together. Detection: the inline path is identified by the presence of an `args` payload conforming to this section's input shape (a parsed `spec-bee-id:` + `distilled-scope:` block from the Skill-tool caller), NOT by Step 0's mid-conversation heuristic — Step 0's heuristic also fires on solo invocations with rich prior conversation context (the err-toward-distilling principle), so using it as the inline-path signal would silently skip the gate on solo runs that legitimately need it. Solo invocations always run Step 7a; inline invocations (recognised by the contract-shaped `args` payload) always skip it.

### Cross-reference

Step 0 (mid-conversation context detection) is the hinge: solo invocations *may or may not* land on the distill branch depending on whether the prompt window contains substantive prior context, but inline invocations *always* land on the distill branch because the caller's contract guarantees substantive distilled scope is supplied. Future maintainers extending this skill MUST keep that invariant true — if a future caller wants to invoke the skill via the Skill tool *without* substantive distilled scope, that is a new use case requiring its own contract section, not a relaxation of this one.

The contract shape here mirrors `/quo-write-prd`'s `## Inline invocation via the Skill tool` section deliberately. When `/quo-plan` dispatches both writers in sequence on the same Spec Bee, the symmetric input/output shape lets `/quo-plan` reuse the same dispatch logic for both calls — only the skill name and the ticket-ID field name change. Keep the two skills' contract sections in lockstep on any future revision.
