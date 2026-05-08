---
name: bees-write-prd
description: Author or revise a PRD as a `t1=Doc` child titled `PRD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/bees-write-prd <spec-bee-id>`), or inline from `/bees-plan` via the Skill tool when initial specs are being authored.
argument-hint: "<spec-bee-id>"
---

## Overview

This skill authors or revises a PRD (Product Requirements Document) as a child ticket under an existing Spec Bee in the Specs hive. The PRD ticket is a `t1=Doc` child with title exactly `PRD` (case-sensitive — downstream skills key off this exact title to differentiate the PRD from the SDD child of the same Spec Bee). The PRD body always contains the same twelve sections in the same order; downstream cold-session agents rely on that fixed shape.

The skill has two invocation paths:

1. **Solo invocation** — `/bees-write-prd <spec-bee-id>` from a Claude Code prompt. Used when revising an existing PRD or authoring one against a Spec Bee whose context lives in the bees ticket rather than the current conversation. The full workflow below covers this path.
2. **Inline invocation via the Skill tool** — invoked by another skill (canonically `/bees-plan` while it is authoring a new Spec Bee) through the Skill tool, with the Spec Bee ID and conversation-distilled scope passed as arguments. The handoff contract — input shape, output shape, behavioral guarantees — is documented in the dedicated `## Inline invocation via the Skill tool` section below the workflow.

Both paths share the same underlying flow: detect prior context, gather or distill scope, write the twelve required sections, create-or-update the PRD child, promote `drafted → ready` on approval. Inline invocation is just the canonical case where the mid-conversation detection branch (Step 0 below) fires.

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Specs hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`).
- CLAUDE.md contains a `## Documentation Locations` section. Step 1 below reads architecture-doc paths from this section as supporting context when the PRD touches existing system behavior.

Note: bees-write-prd does **not** require CLAUDE.md `## Build Commands`. This skill authors a PRD ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/bees-execute` and `/bees-fix-issue` when they actually execute the work, not at PRD-authoring time.

If the precondition is missing, stop with `Run /bees-setup first.` and direct the user there.

## Workflow

This workflow covers both invocation paths. Solo invocation (`/bees-write-prd <spec-bee-id>`) lands at Step 0 with a likely-cold prompt window and typically routes through the discovery branch in Step 3. Inline invocation via the Skill tool (e.g., from `/bees-plan`) lands at Step 0 with substantive prior context already in the prompt window and routes through the distill branch in Step 3. Steps 1, 2, 4, 5, 6, 7, and 8 run identically on both paths.

The skill assumes the Spec Bee already exists; it does not create one. If the user invokes `/bees-write-prd` solo with no `<spec-bee-id>` argument, ask them in prose for the Spec Bee ID and let them reply in their next turn — do NOT use `AskUserQuestion`, since ticket IDs are free-text answers, not a finite set of choices. (Inline callers always pass the Spec Bee ID per the contract section below, so this prompt only fires on the solo path.)

### 0. Detect mid-conversation context

Before treating this invocation as a cold solo run, judge whether the current Claude Code session already contains substantive context about the feature this PRD is meant to capture. The two downstream branches in Step 3 (distill vs restart) are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the feature's scope, rationale, alternatives considered, users / personas, or success criteria.
- The user's invocation message (or `/bees-write-prd <spec-bee-id>` arguments / Skill-tool args) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the problem, users, goals, non-goals, or open questions.
- An explicit hint that this is a continuation of a planning or design discussion (e.g., the user has been planning the feature with the assistant before invoking the skill, or the Skill-tool caller — canonically `/bees-plan` — passes distilled scope alongside the Spec Bee ID per the contract section below).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a 30-minute discovery conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/bees-file-issue`'s Step 0; keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning, filing, and PRD authoring.

The heuristic's output feeds Step 3 below: distill branch when it fires, restart branch when it does not. Steps 1 and 2 run identically on both branches.

### 1. Read the Spec Bee

Fetch the Spec Bee body for context. The Spec Bee's body, title, and any prior children all inform what the PRD needs to capture.

```bash
# POSIX (bash / zsh):
bees show-ticket --ids <spec-bee-id>
```

```powershell
# Windows (PowerShell):
bees show-ticket --ids <spec-bee-id>
```

If the Spec Bee does not exist or is not in the Specs hive, surface the error and stop — do not attempt to fall back to creating a Spec Bee from scratch (that is `/bees-plan`'s responsibility).

Also read any architecture/customer docs configured in CLAUDE.md `## Documentation Locations` if the PRD plausibly touches existing system behavior. Use the canonical contract keys (`Internal architecture docs (SDD)`, `Customer-facing docs`) to resolve the paths.

### 2. Detect existing PRD child

Determine whether a PRD child already exists under this Spec Bee. The skill is idempotent — re-running `/bees-write-prd <same-spec-bee-id>` updates the existing PRD ticket rather than creating a duplicate.

Use `bees execute-freeform-query` with a `parent=<spec-bee-id>` + exact-title filter. The query is regex-based on title; pin both ends so the match is exact and case-sensitive (the PRD child title is exactly `PRD`):

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^PRD$]
report: [ticket_id, title, ticket_status]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^PRD$]
report: [ticket_id, title, ticket_status]'
```

Interpret the result:

- **Zero matches** — no existing PRD child. Step 5 below will use `bees create-ticket` to create one.
- **Exactly one match** — capture the matched ticket ID; Step 5 will use `bees update-ticket --ids <prd-id>` to update it in place.
- **More than one match** — should not happen given the exact-title filter. Surface the anomaly to the user and stop; the user must decide which ticket is the canonical PRD before this skill can proceed.

### 3. Gather scope (distill or restart)

Two branches based on Step 0's heuristic. Use the distill branch when the heuristic fires; use the restart branch otherwise (cold solo invocation against a Spec Bee with no substantive prior conversation context).

#### 3a — Distill branch (heuristic fires)

Skip the apiary-style discovery questions entirely — the prior conversation (or the distilled scope passed by the Skill-tool caller per the contract section below) already contains the substance. Instead:

1. Read the prior context (the in-session conversation, any `Description` / scope content passed as a skill argument, and — on inline invocation — the distilled scope payload supplied by the caller). Cross-reference the Spec Bee body fetched in Step 1 to make sure the distilled draft is consistent with what the Spec Bee already says about the feature.

2. Distill the prior context into a draft populating the twelve required PRD sections defined in Step 4. Pay particular attention to:
   - **`## Background and rationale`** — populate with substance distilled from the prior conversation: prior-conversation context, root-cause framing, why-now justification, and any scoping / framing discussion that informed what made it into the PRD vs what was deliberately left out. This is precisely where prior-conversation richness should land — when the heuristic fires, this section should almost never be the explicit-`none` placeholder, because the heuristic firing means there *is* rationale content to capture.
   - **`## Decisions and rejected alternatives`** — populate when the prior conversation weighed alternatives (alternative scopes, alternative goals, alternative success metrics, alternative non-goals). Capture each decision and the alternatives considered alongside the reasoning, so downstream agents (`/bees-execute`'s Engineer, PM, breakdown) don't re-litigate decisions the user has already made. Same as section 11: when the heuristic fires, this section should almost never be the explicit-`none` placeholder.
   - The other ten sections — populate from the prior context where it covers them; mark the remaining as `not applicable for this PRD` / `none at this time` per Step 4's empty-section rendering rules. Do not fabricate content for sections the prior conversation does not cover.

3. Present the distilled draft to the user for review via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:
   - **Approve** — the distilled draft is good as-is. Proceed to Step 4 / Step 5 with the distilled body as the starting draft for the create-or-update branch.
   - **Revise** — iterate in prose with the user on what to change, then re-present the revised draft via `AskUserQuestion`.
   - **Cancel** — exit the skill cleanly without creating or updating the PRD ticket.

On approve, carry the distilled body forward as the starting material for Step 4 (the body assembly proceeds against the same twelve-section template, with the distilled content already populated). The Step 6 approval gate at the end of the workflow is **not** a duplicate of this gate — Step 3a's gate confirms the distilled scope is correct *before* writing it into a ticket; Step 6's gate confirms the final body (after Step 4's quality-bar checks and Step 5's create-or-update) is good before promoting `drafted → ready`. Both gates are necessary on the distill branch.

#### 3b — Restart branch (heuristic does not fire)

Cold solo invocation against a Spec Bee with no substantive prior conversation context requires discovery — the skill must gather enough material to populate every required section in Step 4 without hallucinating. Apiary's PRD-discovery flow is the spirit to mirror: ask focused, finite-choice questions where possible, and ask prose questions for free-text answers.

Discovery question shape (the exact list is the skill author's call at runtime; below is the reference set):

- **What problem are we solving?** — prose. Captures `## Problem Statement`.
- **Who is the user?** — prose. Captures user/persona detail for `## Problem Statement` and `## Goals`.
- **What does success look like?** — prose. Captures measurable outcomes for `## Goals` and `## Acceptance Criteria`.
- **What is explicitly out of scope?** — prose. Captures `## Non-Goals / Out of Scope`.
- **What functional behaviors are required?** — prose. Captures `## Functional Requirements`.
- **What edge cases or failure modes matter?** — prose. Captures `## Edge Cases and Error Handling`.
- **Are there NFRs (performance, security, availability)?** — prose. Captures `## Non-Functional Requirements`. If the user replies "none", mark the section `not applicable for this PRD` rather than omitting it.
- **Is there UI/UX scope?** — `AskUserQuestion` with finite choices `Yes / No / Partial`. If `No`, mark `## UI/UX Requirements` as `not applicable for this PRD`. Otherwise prompt for detail in prose.
- **What assumptions is this PRD making?** — prose. Captures `## Assumptions`.
- **What questions are still open?** — prose. Captures `## Open Questions`. An empty answer is fine — render the section with `none at this time` rather than omitting it.

Use `AskUserQuestion` only for genuinely finite choices (per CLAUDE.md `## AskUserQuestion usage`); use prose for free-text answers. Do not invent fake "Use my own answer" / "Pick Other" options on `AskUserQuestion` calls.

On the restart branch, sections 11 (`## Background and rationale`) and 12 (`## Decisions and rejected alternatives`) typically render with their explicit-`none` placeholders defined in Step 4 — there's no captured rationale or decision history when the heuristic does not fire. That's the correct shape; do not invent content to fill those sections.

### 4. Author the PRD body

Produce a single markdown body containing the twelve required sections in this exact order. **Every section is always rendered** — never silently omit. When a section has no content, fill it with explicit "not applicable" / "none" / "none at this time" prose so a downstream cold-session reader can tell apart `the author forgot to populate this section` from `the author considered it and there is genuinely nothing here`.

The twelve required sections, in order:

1. `## Problem Statement` — what problem this PRD addresses, who has it, and why it matters now.
2. `## Goals` — measurable outcomes the work must achieve.
3. `## Non-Goals / Out of Scope` — explicit exclusions to prevent scope creep.
4. `## Functional Requirements` — what the system must do, in user-observable terms (not implementation).
5. `## Edge Cases and Error Handling` — failure modes, boundary conditions, and required system responses.
6. `## Non-Functional Requirements` — performance, security, availability, accessibility, etc. Mark `(if applicable)` in the heading or note explicitly when not applicable.
7. `## UI/UX Requirements` — user-facing surface requirements. Mark `(if applicable)` in the heading or note explicitly when not applicable.
8. `## Acceptance Criteria` — concrete, measurable conditions that determine whether the work is complete.
9. `## Assumptions` — assumptions the PRD is making about users, systems, or context.
10. `## Open Questions` — questions not yet answered, including who is expected to answer them.
11. `## Background and rationale` — captures *why* this PRD looks the way it does, including prior-conversation context, root-cause analysis, or framing that informed the scope. **Mandatory.** When there is genuinely no captured rationale, render the section with the explicit phrase `none — this PRD has no captured rationale from prior conversation`.
12. `## Decisions and rejected alternatives` — captures the decisions that were made and the alternatives that were considered and rejected, with the reasoning for each. **Mandatory.** When there is genuinely no captured decision history, render the section with the explicit phrase `none — this PRD has no captured decision history from prior conversation`.

**Why sections 11 and 12 are mandatory-always-present.** Downstream cold-session agents (Engineer, PM, Doc Writer dispatched by `/bees-execute`) read the PRD without the conversation that produced it. If sections 11 and 12 are silently omitted, a cold-session reader cannot disambiguate `the author forgot` from `there is no rationale to capture`. Always rendering them — with explicit "none" placeholders when empty — eliminates that ambiguity. This is intentionally different from `/bees-file-issue`'s OPTIONAL-section policy for issues: PRDs are fixed-shape documents that downstream agents rely on; issues come in many sizes from one-line bug reports to deep analytical distillations.

#### Quality bar

Apply these quality checks while authoring (adapt the spirit of apiary's PRD quality bar):

- **Reject implementation details.** PRDs describe *what* and *why*, not *how*. Architecture choices, library selections, data structures, and code-shape decisions belong to the SDD (`/bees-write-sdd`), not the PRD. If you find yourself writing about classes, modules, or specific API call sequences, move that content out.
- **Reject vague language.** "Should be fast", "good user experience", "scales well" are not requirements — they are aspirations. Replace with measurable thresholds (latency targets, error budgets, supported throughput) or explicitly mark them `## Open Questions` if no measurable target is yet known.
- **Require measurable acceptance criteria.** Every entry under `## Acceptance Criteria` must be objectively verifiable — either the user can interact with an artifact and observe the criterion, or an automated check can decide pass/fail. Subjective criteria ("the experience feels polished") do not belong here.

#### What NOT to include

- Implementation details, architecture diagrams, library or framework choices.
- Test plans, deployment plans, or rollout schedules (those live elsewhere).
- Code snippets, schemas, or API specifications (SDD content).
- Project-management artifacts (estimates, sprint plans, owners).

### 5. Write body to scratch file and create-or-update the PRD ticket

Author the body to a scratch file under the namespaced workflow scratch dir, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt regardless of the user's allowlist, and inlined markdown is also fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both problems.

Steps:

1. Create the `.bees-workflow` subdir if it does not yet exist:

   ```bash
   # POSIX (bash / zsh):
   mkdir -p /tmp/.bees-workflow
   ```

   ```powershell
   # Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path "$env:TEMP\.bees-workflow" | Out-Null
   ```

2. Use the `Write` tool to write the PRD body to a path under that namespaced scratch dir. Use a collision-resistant filename like `bees-body-<short-suffix>.md` (`/tmp/.bees-workflow/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.bees-workflow\bees-body-<short-suffix>.md` on Windows). Do **not** remove the scratch file after the bees command exits — files under `<tempdir>/.bees-workflow/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. The OS / the user reclaims them on their own cadence.

3. Branch on Step 2's detection result (the file-flag carries no shell-quoting surface — only the line-continuation character differs between OSes):

   **Branch A — no existing PRD child** (Step 2 returned zero matches). Create the ticket at `status=drafted`:

   ```bash
   # POSIX (bash / zsh):
   bees create-ticket \
     --hive specs \
     --ticket-type t1 \
     --parent <spec-bee-id> \
     --title PRD \
     --body-file <path> \
     --status drafted
   ```

   ```powershell
   # Windows (PowerShell):
   bees create-ticket `
     --hive specs `
     --ticket-type t1 `
     --parent <spec-bee-id> `
     --title PRD `
     --body-file <path> `
     --status drafted
   ```

   The title is exactly `PRD` (case-sensitive). Do NOT pass `--reference-materials` — it is bee-only and child-tier tickets reject it.

   **Branch B — existing PRD child** (Step 2 returned exactly one match — its ticket ID is `<prd-id>`). Update the body in place:

   ```bash
   # POSIX (bash / zsh):
   bees update-ticket \
     --ids <prd-id> \
     --body-file <path>
   ```

   ```powershell
   # Windows (PowerShell):
   bees update-ticket `
     --ids <prd-id> `
     --body-file <path>
   ```

   `bees update-ticket --body-file` replaces the body in full (rewrite semantics). This is the default for body coherence — a PRD revision typically restructures sections rather than appends to them, so a clean rewrite is the right shape. The bees CLI also exposes `bees append-ticket-body --ticket-id <prd-id> --chunk-file <path>` for explicit append-only revisions, but it is NOT the default for this skill — use it only when the user explicitly asks to append rather than rewrite.

### 6. Confirm with the user, run the spec-review gate, then promote to `ready`

After the create-or-update succeeds, present the resulting PRD ticket ID and a brief summary of what was authored to the user. Use `AskUserQuestion` with finite choices:

- **Approve** — the draft is good as-is. Proceed to the spec-review gate below.
- **Revise** — the user wants changes. Iterate in prose, re-author the body to the same scratch path (or a new one), and re-run Branch B's `bees update-ticket --body-file <path>` against the same `<prd-id>`. Then re-present.
- **Cancel** — leave the ticket at `status=drafted` and exit. The user can re-invoke the skill later to continue.

#### 6a — Spec-review gate (solo path only; skip on inline path)

After the user approves the PRD body in 6's main `AskUserQuestion`, but **before** issuing the `drafted → ready` promotion, invoke `/bees-spec-review` as an automatic quality gate. This step fires only on the solo path (the user invoked `/bees-write-prd <spec-bee-id>` directly from the prompt). On the inline-from-`/bees-plan` path, **skip Step 6a entirely** — the orchestrating `/bees-plan` skill runs its own end-to-end `/bees-spec-review` invocation in its Step 4c after both writers complete, and re-running per-writer review here would double-cost the budget for no added signal. Detection: the inline path is identified by the presence of a Skill-tool `args` payload conforming to the inline-invocation contract documented in `## Inline invocation via the Skill tool` below — i.e., a parsed `spec-bee-id:` + `distilled-scope:` block from the Skill-tool caller. This is **not** the same as Step 0's mid-conversation heuristic (which fires on solo runs whenever the prompt window already contains substantive prior context, per the err-toward-distilling principle); using Step 0's heuristic here would silently skip the gate on solo runs with rich prior conversation context, which is wrong. When you detect the inline path via the contract-shaped `args` payload, jump straight from Step 6's main `Approve` answer to Step 6b's promotion call.

On the solo path, run the gate:

1. Invoke `/bees-spec-review <spec-bee-id> --doc PRD` via the Skill tool. The `--doc PRD` flag scopes the review to the PRD child only — the SDD child may not exist yet at this point (the user may be authoring the PRD before the SDD), and even if it does exist, a standalone PRD revision should not block on or surface SDD-side findings.
2. Read the returned work-item list and apply the loop-back UX described under "Loop-back UX" below.
3. On approve (no findings, or the user explicitly accepted the surfaced findings), proceed to Step 6b's promotion call.
4. On revise (the user asked to address findings), loop back to Step 4's body authoring with the findings supplied as additional context to the revision pass, then re-run Step 5's write-and-update path: re-write the body to the scratch file and re-run Branch B's `bees update-ticket --body-file <path>`, and re-invoke `/bees-spec-review <spec-bee-id> --doc PRD` for a re-check. Apply the time-budget short-circuit before looping indefinitely.

##### Loop-back UX

`/bees-spec-review` returns a numbered work-item list with severity tags (`blocker`, `suggestion`, `nit`). Handle the findings as follows:

- **No findings** — proceed to Step 6b's promotion immediately. No user prompt needed.
- **Only `suggestion` and/or `nit` items, no `blocker`** — surface the full work-item list to the user via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:
  - **Proceed (acknowledge findings)** — the user explicitly accepts the surfaced findings; promote anyway. Record the acknowledged findings in the Step 8 end-of-skill report so the choice is visible.
  - **Revise** — loop back to Step 4's body authoring with the findings included as revision context, then re-run Step 5's write-and-update path and re-invoke `/bees-spec-review <spec-bee-id> --doc PRD` for a re-check.
- **One or more `blocker` items** — surface the full work-item list to the user via `AskUserQuestion` with finite choices:
  - **Revise** (recommended) — loop back to Step 4's body authoring with the findings, then re-run Step 5's write-and-update path and re-invoke `/bees-spec-review <spec-bee-id> --doc PRD` for a re-check.
  - **Proceed anyway (override blockers)** — the user takes explicit responsibility for promoting despite the blockers. Record the override (with the full list of overridden blocker findings) in the Step 8 end-of-skill report so the choice is visible. The override path exists because spec quality is not a hard contract — there are legitimate cases where a `blocker`-tagged finding does not apply (e.g., greenfield work where a "Generic existing-behavior" flag is genuinely the right shape).

`blocker` severity is the primary gate — by default, blockers prevent the PRD child's `drafted → ready` transition until either addressed or explicitly overridden. `suggestion` and `nit` are informational — they surface but do not gate. The user can address them or proceed past them.

##### Time-budget short-circuit

Mirror the pattern in `agents/pm.md` for `/bees-engineer-review` and `/bees-doc-writer-review`: if a single `/bees-spec-review` invocation returns more than ~10 items OR the review-fix-review loop runs more than ~3 turns, stop iterating. Triage the returned list down to `blocker`-severity items only, ask the writer (i.e., this skill's Step 4 body re-authoring path, followed by Step 5's write-and-update path) to address those, then proceed to Step 6b's promotion (with explicit user acknowledgement of the deferred `suggestion`/`nit` items in Step 8's end-of-skill report). These thresholds are guidance, not a hard contract — pick the firmer side when the loop is clearly thrashing on subjective prose-quality nits, the looser side when each finding is high-signal. The 3-turn bound (vs pm.md's 5-turn bound for code/doc review) is intentional: spec content has a much smaller surface area than a Task-sized code diff, so 3 turns of revision usually converges; thrashing past 3 turns almost always means subjective-prose churn rather than missing-content correctness.

#### 6b — Promote the PRD child to `ready`

When the spec-review gate returns control (either because no findings were surfaced, the user explicitly proceeded past surfaced findings, or the time-budget short-circuit was triggered), transition the PRD ticket from `drafted` to `ready`:

```bash
# POSIX (bash / zsh):
bees update-ticket --ids <prd-id> --status ready
```

```powershell
# Windows (PowerShell):
bees update-ticket --ids <prd-id> --status ready
```

The Spec Bee's own `drafted → ready` transition is owned by the caller (e.g., `/bees-plan` after both PRD and SDD children are `ready`). This skill is responsible only for the PRD child.

### 7. Idempotency

Re-running `/bees-write-prd <same-spec-bee-id>` on the same Spec Bee updates the existing PRD ticket rather than creating a duplicate. The detection step (Step 2) is the load-bearing mechanism: it finds the existing PRD child by `parent=<spec-bee-id> + title~^PRD$` and routes the run into Branch B (`update-ticket --body-file`) instead of Branch A (`create-ticket`). This is the observable behavior callers and reviewers can verify by invoking the skill twice in a row against the same Spec Bee.

If the existing PRD is already at `status=ready` when the user re-invokes the skill, the rewrite is still allowed — Step 6's promotion step then re-issues `bees update-ticket --status ready` (idempotent no-op when the status is already `ready`).

### 8. Report back

Show the user:

- The Spec Bee ID.
- The PRD ticket ID (whether created or updated).
- A one-line summary of what the PRD covers.
- The final status (`ready` on approve, `drafted` on cancel).
- Whether this run created a new PRD or revised an existing one (so the user can confirm the idempotency behavior).
- Any spec-review findings that were surfaced during Step 6a but not addressed before promotion — split into:
  - **Acknowledged findings** — `suggestion`/`nit` items the user explicitly accepted via "Proceed (acknowledge findings)".
  - **Overridden blockers** — `blocker` items the user explicitly overrode via "Proceed anyway (override blockers)".
  - **Deferred by time-budget short-circuit** — `suggestion`/`nit` items that were deferred when the ~10-item / ~3-turn budget triggered.

  If Step 6a was skipped (inline-from-`/bees-plan` path), state that explicitly so the report is unambiguous about whether the gate ran. If Step 6a ran with no findings, omit the section entirely.

When invoked inline via the Skill tool, the report shape is structured per the contract section below — return the PRD ticket ID and final status as the load-bearing payload so the caller can wire its own follow-up state (e.g., a Plan Bee's `reference_materials`).

## Inline invocation via the Skill tool

This section is the stable contract for callers that invoke `/bees-write-prd` through the Skill tool rather than as a user-typed slash command. The canonical caller is `/bees-plan` while it is authoring a new Spec Bee and needs to delegate PRD authoring to this skill mid-conversation. Other future callers MAY also invoke this skill via the Skill tool; whatever they pass and consume must match the shape documented here.

Mid-conversation detection (Step 0 above) is the load-bearing precondition for this path: inline invocation always carries substantive prior context — that's the entire point of delegating from a planning conversation rather than restarting discovery — so the distill branch (Step 3a) always fires on inline invocation. The restart branch (Step 3b) is reserved for cold solo runs and does not fire on the inline path.

### Input shape (caller → this skill)

The Skill-tool caller passes a single free-text `args` string that contains, in order:

1. **The Spec Bee ID.** The ticket ID (e.g., the value the caller obtained from its own `bees create-ticket --hive specs --ticket-type bee` call) the new PRD child will hang off of. This skill does NOT create the Spec Bee; the caller does.
2. **The distilled scope payload.** A markdown-formatted block containing the conversation-distilled scope material the caller has gathered with the user. The block SHOULD cover, at minimum, the problem being solved, the users / personas, the goals, and any non-goals or open questions surfaced during the planning conversation. The caller is encouraged to also supply rationale and decision content (the substance behind sections 11 and 12 of Step 4) when the planning conversation produced it.
3. **(Optional) Spec-review findings to address.** A `findings:` block carrying a numbered list of `/bees-spec-review` work items the caller wants this skill to address on the revise pass. Used canonically by `/bees-plan`'s Step 4c spec-review revise loop when `/bees-spec-review` surfaces PRD-tagged findings (or PRD-relevant cross-document findings); omitted on the initial PRD-authoring invocation. Each entry preserves the verbatim severity tag (`[blocker]`, `[suggestion]`, or `[nit]`) and one-line description from the spec-review output, e.g., `1. [blocker] PRD ## Acceptance Criteria — criterion "smooth experience" is subjective; replace with a measurable threshold or move to ## Open Questions.`. When this field is present, the skill routes the findings into Step 4's body re-authoring path (followed by Step 5's write-and-update path) as additional revision context (the same way Step 6a's revise loop on the solo path consumes them) — the load-bearing effect is that Step 4's authoring pass treats the listed findings as required fixes against the existing PRD body. The field is OPTIONAL; absent or empty `findings:` means no spec-review findings to address (the normal initial-authoring shape).

Recommended shape for the `args` string the caller passes (project-neutral; the angle-bracketed placeholders are filled by the caller at runtime):

```
spec-bee-id: <spec-bee-id>

distilled-scope:
<markdown block — multi-paragraph, headed sections welcome>

findings:
<numbered list of `/bees-spec-review` work items, each preserving its [severity] tag and one-line description; omit this field entirely on the initial authoring pass>
```

The skill parses the `args` string, captures the Spec Bee ID, the distilled scope payload, and (when present) the spec-review findings, and routes execution through Step 0 → Step 1 → Step 2 → Step 3a (distill branch always fires here) → Step 4 → Step 5 → Step 6 → Step 6b → Step 7 → Step 8 of the workflow (Step 6a is skipped on the inline path; see "Behavioral guarantees" below). The user-facing approval gates in Step 3a (distilled-scope review) and Step 6's main gate (final-body review) still fire on the inline path — the user owns the approval, not the caller.

### Output shape (this skill → caller)

When the workflow completes (whether the Step 3a or Step 6 gate ends in `Approve` or `Cancel`), the skill returns to the caller a structured final message with at least:

- **`prd_ticket_id`** — the PRD ticket ID the skill created or updated (the `t1=Doc` child titled `PRD` under the Spec Bee).
- **`prd_status`** — the final status of the PRD ticket (`ready` on approve, `drafted` on cancel or unfinished revision).
- **`action`** — `created` if Step 5's Branch A ran, `updated` if Step 5's Branch B ran. Lets the caller confirm the idempotency behavior matches its expectations.

The caller (e.g., `/bees-plan`) consumes `prd_ticket_id` to wire the Plan Bee's `reference_materials` (or equivalent state) at the Spec Bee that owns the new PRD child, and consumes `prd_status` to gate its own Spec Bee `drafted → ready` transition (which gates on both PRD and SDD children being `ready`).

### Behavioral guarantees

The inline path is functionally identical to the solo path from the Spec Bee's perspective; only the Step 3 distill-vs-restart branch differs and the Step 6a spec-review gate is skipped. Specifically:

- **Idempotency.** Step 2's existing-PRD-child detection runs identically. Re-invoking via the Skill tool against the same Spec Bee updates the existing PRD ticket rather than creating a duplicate (Branch B in Step 5).
- **Twelve required sections.** Step 4's body assembly always produces all twelve sections. Sections 11 and 12 receive substantive content distilled from the caller's payload (the distill branch should rarely emit the explicit-`none` placeholders for these sections on the inline path, because the caller passing distilled scope is exactly the signal that there *is* rationale and decision content to capture).
- **Lifecycle.** PRD ticket created at `drafted`, transitioned to `ready` on the user's `Approve` in Step 6. Identical to solo.
- **Scratch-file convention.** `--body-file` payloads written under `<tempdir>/.bees-workflow/` with create-if-absent; never removed. Identical to solo.
- **User approval gates.** Both gates (Step 3a's distilled-scope review and Step 6's final-body review) still fire on the inline path. The Skill-tool caller does NOT short-circuit either gate.
- **Spec-review gate (Step 6a) skipped on the inline path.** The orchestrating `/bees-plan` skill runs its own end-to-end `/bees-spec-review` invocation in its Step 4c after both writers complete (covering the PRD and SDD children plus the cross-document consistency pass), so this skill MUST skip its own per-writer Step 6a review when invoked inline. Re-running per-writer review here would double-cost the budget without adding signal — the cross-document pass that `/bees-plan`'s Step 4c invocation runs is strictly more powerful than two single-doc invocations chained together. Detection: the inline path is identified by the presence of an `args` payload conforming to this section's input shape (a parsed `spec-bee-id:` + `distilled-scope:` block from the Skill-tool caller), NOT by Step 0's mid-conversation heuristic — Step 0's heuristic also fires on solo invocations with rich prior conversation context (the err-toward-distilling principle), so using it as the inline-path signal would silently skip the gate on solo runs that legitimately need it. Solo invocations always run Step 6a; inline invocations (recognised by the contract-shaped `args` payload) always skip it.

### Cross-reference

Step 0 (mid-conversation context detection) is the hinge: solo invocations *may or may not* land on the distill branch depending on whether the prompt window contains substantive prior context, but inline invocations *always* land on the distill branch because the caller's contract guarantees substantive distilled scope is supplied. Future maintainers extending this skill MUST keep that invariant true — if a future caller wants to invoke the skill via the Skill tool *without* substantive distilled scope, that is a new use case requiring its own contract section, not a relaxation of this one.
