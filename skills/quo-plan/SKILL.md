---
name: quo-plan
description: Interactive feature planning — explore scope, author PRD/SDD as Spec Bee children (no project-doc mutation), create a Plan Bee with Epics ready for /quo-breakdown-epic and /quo-execute.
argument-hint: "[<description>]"
---

## Overview

This skill handles the full journey from "I have an idea" to "here's a broken-down plan ready for execution." It supports features of any size — from adding Helm charts to a new RPC endpoint.

> **Tip:** if you already have a finalized PRD and SDD on disk that describe a **single feature**, `/quo-plan-from-specs <prd-path> <sdd-path>` is the faster path — it skips the discovery and scope-iteration phases and goes straight to Plan Bee creation. If your PRD/SDD are cumulative (one or more prior `### Feature:` subsections already present) and you want to re-plan exactly one of those subsections, `/quo-plan-from-specs <prd-path> <sdd-path> --feature "<title>"` is the express scoped form — it bypasses the multi-feature guard and reads only the matching `### Feature: <title>` subsection from each doc. Use `/quo-plan` (this skill) when you're starting from an idea or rough notes, or when you're adding a brand-new feature to a cumulative PRD/SDD. `/quo-plan-from-specs` without `--feature` hard-fails on multi-feature docs to avoid re-planning previously-planned features.

### Usage

- `/quo-plan` — interactive: start a conversation about what you want to build
- `/quo-plan <description>` — start with a description and refine from there

## Workflow

### 0. Detect mid-conversation context

Before treating this invocation as a cold solo run, judge whether the current Claude Code session already contains substantive context about the feature this Plan Bee is meant to capture. The two downstream branches (distill vs restart) below are gated on this judgment.

**Indicative signals that the heuristic should fire (distill, don't restart):**

- Rich back-and-forth in the same session about the feature's scope, rationale, alternatives considered, users / personas, or success criteria.
- The user's invocation message (or `/quo-plan <description>` argument) contains substantive scope information beyond a one-line title — e.g., a paragraph or more describing the feature, including motivation, constraints, or rejected alternatives.
- An explicit hint that this is a continuation of a planning discussion (e.g., the user has been iterating on scope with the assistant before invoking the skill).

**Err toward distilling.** When the choice is ambiguous, tilt toward the distill branch rather than the restart branch — a wasted distill draft is cheaper for the user to revise or reject than restarting a 30-minute discovery conversation from scratch. Future maintainers must not tighten this heuristic into a stricter "only fire when X is unambiguously true" gate, which would defeat the design intent. The same err-toward-distill principle is mirrored in `/quo-write-prd`'s and `/quo-write-sdd`'s Step 0; keep this skill's phrasing in lockstep so users get a consistent distill-vs-restart experience across planning and spec authoring. (Step 4 of this skill invokes those writer skills inline via the Skill tool with the distilled scope, so a divergence here would mean the user gets asked discovery questions twice — once in this skill's restart branch and again when a writer skill mis-detects and runs its own restart branch.)

The heuristic's output feeds the two branches below:

- **Distill branch (0a)** — heuristic fires. Skip Steps 1 and 2 entirely, distill the prior conversation into a scope summary, present it for approval, then jump to Step 3 (final scope-approval gate) with the approved distillation as the scope statement.
- **Restart branch (0b)** — heuristic does not fire. Run Steps 1 and 2 as written, then proceed to Step 3 normally.

Steps 3, 4, 5, 6, and 7 run identically on both branches.

#### 0a — Distill branch (heuristic fires)

Skip Step 1's "Before I start researching, is there anything I should know?" prompt and Step 2's numbered clarifying-questions list — the prior conversation already contains the substance, and re-asking would force the user to repeat themselves. Instead:

1. Read the prior context (the in-session conversation, plus any `<description>` argument passed when the skill was invoked). Distill it into a scope summary covering, at minimum:

   - **Feature title** — a short noun phrase suitable for the Plan Bee title and the Spec Bee title.
   - **What** — one paragraph describing the feature (what it does, in user-observable terms).
   - **Why** — the motivation (what problem this solves, who has it, why it matters now).
   - **Acceptance criteria** — concrete, measurable, testable conditions for "done".
   - **Out of scope** — explicit exclusions surfaced during the planning conversation.
   - **Decisions** — key design or scope decisions the user made during the conversation.
   - **Rejected alternatives** — alternative approaches, scopes, or designs that were considered and rejected, with the reasoning for each.
   - **Constraints** — design constraints, technology preferences, timeline considerations, or related-work dependencies the user surfaced.

   Format the distilled scope as a markdown block with each of those eight items as a labeled `### <Section>` heading (or `**<Section>:**` bold-prefix line, whichever reads cleaner) so Step 4's Skill-tool invocations of `/quo-write-prd` and `/quo-write-sdd` can extract each section deterministically when they consume it as the `distilled-scope` payload. Multi-paragraph content under each heading is welcome. Sections with no content from the prior conversation should be rendered explicitly with `none` / `not applicable for this feature` rather than omitted, so the writer skills can tell apart `the planner forgot` from `there is genuinely nothing here`.

2. Present the distilled scope to the user via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` (it's multi-choice only). Finite choices:

   - **Approve** — the distilled scope is good as-is. Carry the distillation forward as the scope statement and proceed to Step 3 (the final scope-approval gate). Step 3's `AskUserQuestion` still fires as a final user-facing checkpoint — the Step 0a gate confirms the *distillation* is correct; Step 3's gate confirms the *scope statement built from the distillation* is correct before any tickets get created.
   - **Revise** — the distilled scope needs changes. Iterate in prose with the user on what to change, then re-present the revised distillation via `AskUserQuestion`.
   - **Cancel** — exit the skill cleanly without creating any tickets.

On approve, carry the distilled body forward to Step 3 as the starting material for the scope statement (the eight section headings map cleanly onto Step 3's What / Why / Acceptance criteria / Out-of-scope shape, with the Decisions / Rejected alternatives / Constraints content carried alongside for downstream consumption by the writer skills in Step 4).

#### 0b — Restart branch (heuristic does not fire)

Cold solo invocation from a fresh session, or `/quo-plan <description>` with only a one-line description and no rich preceding discussion. Run Steps 1 and 2 below as written — same "Before I start researching" prompt, same numbered clarifying-questions list, same "do not proceed until you and the user agree on what the feature is" gate — then continue to Step 3.

### 1. Gather Context from the User FIRST (restart branch only)

This step runs only on the restart branch (Step 0b). The distill branch (Step 0a) skips directly to Step 3 with the approved distillation as the scope statement.

**Before doing any research or asking pointed questions**, ask the user as plain prose (no tool call — this is an open-ended question, not a multi-choice one) if there's additional context you should know:

> Before I start researching, is there anything I should know? For example: reference implementations, existing services to look at, design constraints, related repos, prior art, or anything else that would help me plan this well.

Wait for the user's reply in their next turn. They may point you to:
- An existing deployed service to use as reference
- A specific repo, directory, or file with relevant patterns
- Design constraints or team preferences
- Prior discussions or decisions

Incorporate whatever they share into ALL subsequent research and questions.

### 2. Explore and Understand (restart branch only)

This step runs only on the restart branch (Step 0b). The distill branch (Step 0a) skips directly to Step 3.

Now research — informed by the user's context from step 1.

**If called with a description**, use it as the starting point.

**If called without arguments**, ask: "What feature or capability do you want to add?"

**Check for existing docs:** Look for a PRD and SDD in the repo (check CLAUDE.md for paths, or look in `docs/`). If they don't exist and CLAUDE.md doesn't reference them, ask the user:

- "Does this project have a PRD or SDD (Software Design Document)? It's totally fine if not — I can plan the feature without them."

If the user provides paths, read them so subsequent research and clarifying questions can reference the existing requirements. If they say no or the docs don't exist, no further branching is needed here — Step 4 always creates a Spec Bee with PRD and SDD `t1=Doc` children regardless of whether project-level PRD/SDD docs exist on disk, so there are no "doc-related steps later" to skip.

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

Step 4 anchors the feature's PRD and SDD as ticketed artifacts in the Specs hive rather than writing them directly to project docs at planning time. The flow is: (a) detect or create a **Spec Bee** that holds the PRD and SDD as `t1=Doc` children, (b) invoke `/quo-write-prd` and `/quo-write-sdd` via the Skill tool to author those children, (c) promote the Spec Bee from `drafted` to `ready` once both writers return successfully. The rationale: ticketed specs let `/quo-plan` run side-effect-free against project docs (planning a feature without executing it leaves `docs/prd.md` / `docs/sdd.md` untouched), and they let multiple unrelated features be planned in parallel without their spec edits stepping on each other.

#### 4a — Detect or create the Spec Bee

All `AskUserQuestion` gates in this sub-step (the ambiguous-heuristic candidate-confirmation gate, and the matched Spec-Bee reuse-or-create gate) fire through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Step 5g's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark each `gate-*` task `completed` the moment the user's answer is consumed.

**Detection.** Re-running `/quo-plan` for the same feature must reuse an existing Spec Bee rather than create a duplicate. Query the Specs hive for `bee`-tier tickets and inspect the result for one whose title matches the feature title from Step 3:

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
- `Cancel` — abort the run. The user can resume later by re-invoking `/quo-plan`.

**No match — create.** Author the Spec Bee body to a temp file under `<tempdir>/.quorum/` per the scratch-file convention (do not delete after; the OS reclaims `<tempdir>` on its own cadence), then call `bees create-ticket`. The body should be a brief 2-3 sentence summary of the feature scope, paraphrased from the Step 3 scope statement — substantive PRD/SDD content lands in the `t1=Doc` children, **not** the Spec Bee body itself. Do NOT dump full PRD or SDD content into the Spec Bee body.

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write the body to /tmp/.quorum/bees-spec-body-<short-suffix>.md via the Write tool
bees create-ticket --ticket-type bee --hive specs --status drafted --title "<feature title>" --body-file <path>
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write the body to $env:TEMP\.quorum\bees-spec-body-<short-suffix>.md via the Write tool
bees create-ticket --ticket-type bee --hive specs --status drafted --title "<feature title>" --body-file <path>
```

**Do not pass `--reference-materials` on the Spec Bee.** The Spec Bee's children — the PRD and SDD `t1=Doc` tickets — are themselves the reference materials. The Spec Bee is its own anchor for downstream `bees`-resolver lookups; downstream skills (Plan Bee creation in Step 5, `/quo-execute`'s PM role) trace from the Plan Bee's `reference_materials` array (which carries the Spec Bee ID via the `bees` resolver) into the Spec Bee and from there to its `t1=Doc` children.

Capture the Spec Bee ID returned by `bees create-ticket` (or the existing ID from the reuse branch) — it is consumed by the writer-skill invocations sub-step (4b) and the Spec Bee promotion sub-step (4c).

#### 4b — Author the PRD and SDD via the writer skills

With the Spec Bee ID in hand from sub-step 4a, delegate the actual PRD and SDD authoring to `/quo-write-prd` and `/quo-write-sdd`. Invoke both skills inline through the Skill tool — `/quo-plan` does not author PRD/SDD content directly, and it does not call `bees create-ticket` or `bees update-ticket` for the `t1=Doc` PRD/SDD child tickets. The writer skills handle child-ticket creation, body assembly, the user-facing approval gates, and the `drafted → ready` transition on their own children. Step 4 here only owns the Spec Bee parent.

**Args payload — identical for both writer skills.** The two writer skills publish a deliberately mirrored input contract (see `skills/quo-write-prd/SKILL.md` `## Inline invocation via the Skill tool` and the matching section in `skills/quo-write-sdd/SKILL.md`) so this sub-step can dispatch them with the same `args` string. Build the payload once and reuse it verbatim across both calls. **Divergence between the PRD and SDD `args` payloads is a defect** — keep them byte-identical; if the user clarifies scope between the two calls (e.g., during the PRD's approval gate), abort and re-author both rather than letting the SDD see a different payload than the PRD did. The byte-identical invariant applies to the **initial** PRD+SDD pair authored in this sub-step (4b); on the spec-review revise loop in 4c below, asymmetric writer re-invocations are the *intended* behavior — when `/quo-spec-review` surfaces PRD-only or SDD-only findings, only the affected writer is re-invoked, with that writer's `args` payload extended with a `findings:` field carrying just its findings. See 4c's revise-loop step for the asymmetric-revise carve-out and the `findings:` payload shape.

The `args` string is free-text, in the shape documented by both writer SKILL.md contract sections:

```
spec-bee-id: <spec-bee-id captured in 4a>

distilled-scope:
<markdown block carrying the conversation-distilled scope>
```

The `distilled-scope` block MUST cover, at minimum, the conversation-distilled scope statement from Step 3 (What / Why / Acceptance criteria / Out of scope) plus any prior-context the user shared in Step 1 (reference implementations, existing services, design constraints, related repos, prior art). Multi-paragraph markdown with headed sub-sections is welcome. The caller is encouraged to also include any rationale, rejected alternatives, or open questions that came up during the planning conversation, since the writer skills route that content into their respective rationale / decisions / open-questions sections.

**Step 1 — invoke `/quo-write-prd`.** Call the Skill tool with `skill="quo-write-prd"` and the `args` string built above. The writer skill parses the payload, takes its distill branch (guaranteed by the inline-invocation contract since this sub-step always passes substantive scope), surfaces its own user-facing approval gates, creates or updates the PRD `t1=Doc` child under the Spec Bee, and on success transitions the PRD child from `drafted` to `ready`. Capture from the writer's structured return message:

- `prd_ticket_id` — the PRD ticket ID (the `t1=Doc` child titled `PRD` under the Spec Bee).
- `prd_status` — the final status (`ready` on approve, `drafted` on cancel).
- `action` — `created` for a new PRD, `updated` for the idempotent reuse path.

**Step 2 — invoke `/quo-write-sdd`.** Only after `/quo-write-prd` returns successfully (i.e., `prd_status` is `ready`), call the Skill tool with `skill="quo-write-sdd"` and the **same** `args` string used for `/quo-write-prd`. Sequential, not parallel: both writer skills modify the same Spec Bee's children list, and the Skill tool's invocation model is single-shot rather than concurrent. Running them in parallel would race the children-list lookup and may produce duplicate PRD or SDD children. Capture from the writer's structured return message:

- `sdd_ticket_id` — the SDD ticket ID (the `t1=Doc` child titled `SDD` under the Spec Bee).
- `sdd_status` — the final status (`ready` on approve, `drafted` on cancel).
- `action` — `created` or `updated`, same semantics as the PRD writer.
- `research_needed` — a (possibly empty) list of `RESEARCH NEEDED: <question>` tags the SDD writer embedded after its codebase-research pass. Surface any non-empty list to the user so they know which open questions still need a follow-up pass before execution.

**Error handling.** If either Skill-tool call returns an error, or the writer reports a non-`ready` final status (i.e., the user cancelled at one of the writer's approval gates), surface the error to the user with the writer's failure detail and **abort Step 4** — do not proceed to the Spec Bee promotion sub-step or to Step 5. The Spec Bee parent remains in `drafted` so the user can re-run `/quo-plan` later and pick `Reuse existing Spec Bee` from sub-step 4a's heuristic prompt to resume from the Spec Bee that already exists. If `/quo-write-prd` succeeds but `/quo-write-sdd` fails, the PRD child remains `ready` and the SDD child either does not exist or remains `drafted` — re-running `/quo-plan` will pick up the partial state cleanly via the writer skills' own idempotency (Step 5's Branch B in each writer).

The captured `prd_ticket_id`, `prd_status`, `sdd_ticket_id`, and `sdd_status` values are consumed by the Spec Bee promotion sub-step (4c), which gates the Spec Bee's own `drafted → ready` transition on both child statuses being `ready`.

#### 4c — Run the spec-review gate, then promote the Spec Bee from drafted to ready

With both writer skills returned successfully, run an automatic spec-review quality gate over the PRD and SDD children, then transition the Spec Bee parent from `drafted` to `ready` so downstream consumers (the Plan Bee's `reference_materials` and any `bees`-resolver lookups) see a Spec Bee in `ready` state with `ready` PRD and SDD children underneath.

**Defensive status check.** Before doing anything else, confirm that both `prd_status` and `sdd_status` captured in 4b are `ready`. The writer skills' inline-invocation contracts (their respective `## Inline invocation via the Skill tool` sections) guarantee `ready` on successful return — a non-`ready` value here indicates a writer-contract regression, not a normal user-cancel path (cancels are caught by 4b's error-handling clause and abort Step 4 before reaching this sub-step). If either captured status is not `ready`, surface the discrepancy as an error, name which child failed the check, and do **not** run the spec-review gate or promote the Spec Bee. Do not paper over the mismatch by promoting anyway — the defensive check exists precisely so a regression in a writer-skill contract surfaces here rather than silently producing a `ready` Spec Bee with non-`ready` children.

**Spec-review gate.** When the defensive status check passes, run `/quo-spec-review` as an automatic quality gate before promoting the Spec Bee. The writer skills' inline-invocation contracts explicitly skip their own per-writer spec-review steps (`/quo-write-prd`'s Step 6a and `/quo-write-sdd`'s Step 7a) when invoked inline — Site 1 here is the single end-to-end review pass for the PRD child, the SDD child, and cross-document consistency.

**Pre-commitment.** When the Skill call returns, you MUST FIRST create a `gate-<kind>-<short-suffix>` TaskList task (per `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract` — `gate-askuserquestion-<short-suffix>` when findings are present, no gate-task needed for the no-findings `bees update-ticket --status ready` path because no user gate fires there), THEN call the prescribed tool (`AskUserQuestion` when findings are present, `bees update-ticket --status ready` when no findings) in the same turn. The dispatched skill's trailer will repeat this two-step obligation; treat the trailer as a confirmation, not a new instruction. A text-only response between the Skill return and that tool use is a defect.

1. Invoke `/quo-spec-review <spec-bee-id>` via the Skill tool, with **no `--doc` flag** so both children are reviewed plus the cross-document consistency pass runs. The `<spec-bee-id>` placeholder is the Spec Bee ID captured at the end of 4a (and confirmed `ready` after Step 4c's defensive status check just above — the writer skills already promoted the children to `ready`; this gate is the last quality check before the parent itself promotes).
2. Read the returned work-item list and apply the loop-back UX described under "Loop-back UX" below.
3. On approve (no findings, or the user explicitly accepted the surfaced findings), proceed to "Promote the Spec Bee" below.
4. On revise (the user asked to address findings), invoke the relevant writer skill(s) via the Skill tool with the findings included as the optional third `findings:` field in the `args` payload alongside the existing `spec-bee-id` and `distilled-scope` fields. Both writer skills' input-shape sections (`skills/quo-write-prd/SKILL.md` `## Inline invocation via the Skill tool` → `### Input shape` and the matching section in `skills/quo-write-sdd/SKILL.md`) document the `findings:` field as an optional third payload entry; pass through the relevant subset of `/quo-spec-review`'s numbered work-item list verbatim under that key. Asymmetric revises here are explicitly *carved out* of the byte-identical invariant declared in 4b — different findings legitimately go to different writers on the revise pass:
   - PRD-only findings — re-invoke `/quo-write-prd` with `findings:` populated from the PRD-tagged items only (it will route through Step 5's create-or-update Branch B against the existing PRD child, since 4a's detection has already identified the PRD child). The SDD writer is NOT re-invoked.
   - SDD-only findings — re-invoke `/quo-write-sdd` with `findings:` populated from the SDD-tagged items only (symmetric, against the existing SDD child). The PRD writer is NOT re-invoked.
   - Cross-document findings, or findings that span both PRD and SDD — re-invoke both writer skills sequentially (PRD first, then SDD), each with its own `findings:` slice (PRD-tagged items + cross-document items go to the PRD writer; SDD-tagged items + cross-document items go to the SDD writer). The two `args` payloads are intentionally non-identical on this branch — the `findings:` slice differs by writer — and that asymmetry is the intended shape, not a defect.

   After the writer(s) return successfully (re-confirming `prd_status`/`sdd_status` are `ready` per 4b's error-handling clause), re-invoke `/quo-spec-review <spec-bee-id>` for a re-check. Apply the time-budget short-circuit before looping indefinitely.

##### Loop-back UX

`/quo-spec-review` returns a numbered work-item list with severity tags (`blocker`, `suggestion`, `nit`) and — load-bearing — a second-person imperative routing trailer (`**Your next tool call MUST be …**` / `**Your next tool use MUST …**`) plus a counter-anchor clause at the bottom of its output, naming the precise routing this step must take. **Follow the trailer literally.** The trailer is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory. If the trailer and the prose ever diverge, the trailer wins (and that divergence is a bug in `/quo-spec-review` to file).

Quick-reference summary of what the three trailer shapes prescribe (the trailer text in `/quo-spec-review`'s output is the canonical source):

| Review output | Trailer-prescribed action |
| --- | --- |
| No findings | Promote the Spec Bee immediately; no user prompt. |
| Suggestions / nits only (no blockers) | `AskUserQuestion`: `Proceed (acknowledge findings)` / `Revise`. Do not produce a text response describing this gate — call the tool directly. |
| One or more blockers | `AskUserQuestion`: `Revise` (recommended) / `Proceed anyway (override blockers)`. Do not produce a text response describing this gate — call the tool directly. |

Behavioral details (apply after gating per the trailer):

- **Proceed (acknowledge findings)** — the user explicitly accepts the surfaced `suggestion`/`nit` findings; promote anyway. Record the acknowledged findings in Step 5f's end-of-skill report so the choice is visible.
- **Revise** — loop back to the writer-skill re-invocation path described in step 4 above, then re-invoke `/quo-spec-review <spec-bee-id>` for a re-check.
- **Proceed anyway (override blockers)** — the user takes explicit responsibility for promoting despite the blockers. Record the override (with the full list of overridden blocker findings) in the end-of-skill report so the choice is visible. The override path exists because spec quality is not a hard contract — there are legitimate cases where a `blocker`-tagged finding does not apply (e.g., greenfield work where a "Generic existing-behavior" flag is genuinely the right shape).

`blocker` severity is the primary gate — by default, blockers prevent the Spec Bee's `drafted → ready` transition until either addressed or explicitly overridden. `suggestion` and `nit` are informational — they surface but do not gate. The user can address them or proceed past them.

##### Time-budget short-circuit

Mirror the pattern in `agents/pm.md` for `/quo-engineer-review` and `/quo-doc-writer-review`: if a single `/quo-spec-review` invocation returns more than ~10 items OR the review-fix-review loop runs more than ~3 turns, stop iterating. Triage the returned list down to `blocker`-severity items only, ask the relevant writer(s) to address those (via the writer-skill re-invocation path described above), then proceed to "Promote the Spec Bee" (with explicit user acknowledgement of the deferred `suggestion`/`nit` items in the end-of-skill report). These thresholds are guidance, not a hard contract — pick the firmer side when the loop is clearly thrashing on subjective prose-quality nits, the looser side when each finding is high-signal. The 3-turn bound (vs pm.md's 5-turn bound for code/doc review) is intentional: spec content has a much smaller surface area than a Task-sized code diff, so 3 turns of revision usually converges; thrashing past 3 turns almost always means subjective-prose churn rather than missing-content correctness.

**Promote the Spec Bee.** When the spec-review gate returns control (either because no findings were surfaced, the user explicitly proceeded past surfaced findings, or the time-budget short-circuit was triggered), transition the Spec Bee:

```bash
# POSIX (bash / zsh):
bees update-ticket --ids <spec-bee-id> --status ready
```

```powershell
# Windows (PowerShell):
bees update-ticket --ids <spec-bee-id> --status ready
```

The `bees update-ticket` invocation is identical on both platforms here — there is no platform-specific syntax difference for this single-flag call. The paired snippets are kept anyway so the SKILL.md's structure stays uniform with the rest of Step 4.

**Idempotent re-runs.** If the Spec Bee is already in `ready` state when this sub-step begins (for example, a re-run of `/quo-plan` against the same feature where the Spec Bee was promoted in a prior run and the writer skills returned no-op `updated` actions on already-`ready` children), the `bees update-ticket --status ready` call is a harmless no-op — bees treats setting a status field to its existing value as a no-op write. The implementer may optionally short-circuit the promotion call when an already-`ready` Spec Bee is detected, but a defensive re-assert is equivalent in effect and is the simpler default.

**End-of-Step-4 summary — what the user should now see.** After 4c succeeds, the user has:

- A Spec Bee in the Specs hive titled `<feature title>`, status `ready`.
- A `t1=Doc` child of the Spec Bee titled `PRD`, status `ready`, with the PRD content the user approved during `/quo-write-prd`'s gate.
- A `t1=Doc` child of the Spec Bee titled `SDD`, status `ready`, with the SDD content the user approved during `/quo-write-sdd`'s gate (and any `RESEARCH NEEDED:` tags surfaced for follow-up).
- Any `/quo-spec-review` findings surfaced during the spec-review gate but not addressed before promotion — captured for inclusion in Step 5f's end-of-skill report. Specifically:
  - **Acknowledged findings** — `suggestion`/`nit` items the user explicitly accepted via "Proceed (acknowledge findings)".
  - **Overridden blockers** — `blocker` items the user explicitly overrode via "Proceed anyway (override blockers)".
  - **Deferred by time-budget short-circuit** — `suggestion`/`nit` items deferred when the ~10-item / ~3-turn budget triggered.

  If the spec-review gate ran with no findings, omit this bullet; the report stays clean.

Step 5 (Plan Bee creation) consumes this directly: the Plan Bee's `reference_materials` will be set to a single-element list containing a `bees`-resolver entry that points at the Spec Bee ID just promoted, so downstream skills (`/quo-breakdown-epic`, `/quo-execute`'s PM role) can trace from the Plan Bee through the Spec Bee to the PRD and SDD `t1=Doc` children at execution time.

### 5. Create Plan Bee with Epics

Create the Plan Bee inline in this session — do **not** delegate to `/quo-plan-from-specs`. That skill operates on PRD/SDD files on disk and serves the hand-authored cumulative-doc flow; this skill operates on the Spec Bee + `t1=Doc` children that Step 4 just created, and the Plan Bee's `reference_materials` points at the Spec Bee via the `bees` resolver. Inline creation here is the single supported path.

#### 5a — Detect or create the Plan Bee

All `AskUserQuestion` gates in this sub-step (the ambiguous-match candidate-confirmation gate when multiple candidate Plan Bees are found, and the matched Plan-Bee reuse-or-create gate) fire through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per Step 5g's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark each `gate-*` task `completed` the moment the user's answer is consumed.

**Detection.** Re-running `/quo-plan` for the same feature — e.g., after Cancelling at the Step 5e plan-review gate to revise the Epic decomposition — must reuse an existing `drafted` Plan Bee under the current Spec Bee rather than create a duplicate. Query the Plans hive for `drafted` `bee`-tier tickets and inspect each for a `reference_materials` entry whose `bees`-resolver value points at the Spec Bee captured at the end of sub-step 4a:

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans, status=drafted]
report: [ticket_id, title, reference_materials]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans, status=drafted]
report: [ticket_id, title, reference_materials]'
```

For each returned bee, parse `reference_materials` as a JSON array of `{value, resolver}` objects and match against the current Spec Bee ID — a hit is any bee whose array contains an entry with `resolver == "bees"` and `value == <spec-bee-id>`. **Err toward reuse:** if the match is ambiguous (multiple candidate `drafted` Plan Bees under the same Spec Bee, which should be rare and indicates a prior inconsistent state), surface the candidates to the user with `AskUserQuestion` rather than guessing. A duplicate Plan Bee is cheap to fix manually after the fact; a missed reuse silently fragments the Epic set across two Plan Bees.

**Match found — confirm with user.** When a candidate Plan Bee is found, fetch its child Epics via `bees show-ticket --ids <plan-bee-id>` (the `children` array enumerates the Epic ticket IDs), then present the situation via `AskUserQuestion` with these finite choices:

- `Reuse existing Plan Bee and Epics` (Recommended when returning after a Cancel-at-5e) — capture the existing Plan Bee ID and the list of Epic IDs. The current run's Step 5b/5c/5d-i operate on this existing state idempotently (see "Reuse-mode downstream behavior" below). Skips the **No match — create** branch entirely.
- `Create a new Plan Bee anyway` — fall through to the **No match — create** branch below. Use this when the user wants a fresh Plan Bee (e.g., the prior decomposition was for a superseded scope and they want to start clean). The orphan Plan Bee + its Epic children remain in `drafted` state for the user to clean up out-of-band via `bees delete-ticket --ids <id>`.
- `Cancel` — abort the run.

**Reuse-mode downstream behavior.** When the user picks `Reuse existing Plan Bee and Epics`, the orchestrator captures the existing Plan Bee ID and Epic-children list, then routes downstream sub-steps as follows:

- **Skip** the `bees create-ticket --hive plans` call in the **No match — create** branch below — the Plan Bee already exists.
- **Step 5b's "break the feature into Epics"** seeds from the existing Epic bodies (read each via `bees show-ticket --ids <epic-id>`), then iterates with the user as if proposing a fresh decomposition — the user MAY keep all Epics, modify some, add new ones, or drop existing ones. The Step 5b decomposition rules still apply against the resulting list.
- **Step 5c's "present Epics for review"** gates on the resulting (possibly modified) Epic list. Surface the reuse-vs-new origin per Epic in the presentation so the user sees which ones carried over.
- **Step 5d-i** routes as **update-or-create-or-delete** rather than blind create: for each Epic in the approved list that matches an existing child Epic by title (after the same normalization 4a uses for Spec Bee titles), `bees update-ticket --ids <epic-id> --body-file <path>` against the existing ticket; for each new Epic without a match, `bees create-ticket` as usual under the existing Plan Bee parent; for each existing child Epic that is NOT in the approved list, `bees delete-ticket --ids <epic-id>` (gated on a children-cascade-guard prompt when the Epic has child Tasks — see Step 5d-i). Dependency wiring runs against the final post-reconcile Epic set. The Plan Bee body itself stays as-is unless the user modified scope substantially enough to invalidate it — in which case re-author and `bees update-ticket --ids <plan-bee-id> --body-file <path>` it inline (same temp-file pattern as the create branch below).

After the reuse-mode downstream sub-steps complete, control resumes at Step 5e (plan-review gate) exactly as in the create-branch flow.

**No match — create.** Author the Plan Bee body to a temp file via the `Write` tool first, then pass `--body-file <path>` to bees. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt, and inlined markdown is fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both. Use a path under the namespaced workflow scratch dir (`/tmp/.quorum/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\.quorum\bees-body-<short-suffix>.md` on Windows). Create the `.quorum` subdir if absent (`mkdir -p /tmp/.quorum` on POSIX, `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null` on Windows). Do **not** remove the temp file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so crashed runs leave debuggable artifacts in a known place; the OS / user reclaims them on their own cadence.

**Plan Bee body shape.** Keep the body short — a brief 2-3 sentence summary of the feature and its high-level scope, plus an `## Anticipated doc impact` section. Substantive PRD/SDD content lives in the Spec Bee's `t1=Doc` children (created in Step 4), not in the Plan Bee body — downstream skills (`/quo-breakdown-epic`, `/quo-execute`'s PM role) read those via the `bees`-resolver entry in `reference_materials`. The `## Anticipated doc impact` section is a starting checklist for the post-implementation `doc-writer` pass, which appends/updates `### Feature:` subsections in the cumulative project PRD/SDD per the responsibility documented in `agents/doc-writer.md`: list which cumulative project docs the feature is expected to update once it lands. Reference the contract keys from the target repo's CLAUDE.md `## Documentation Locations` section (e.g., the `Project requirements doc (PRD)` entry, the `Internal architecture docs (SDD)` entry, the `Customer-facing docs` entry) rather than hardcoding paths like `docs/prd.md` — different projects route those keys to different files.
**Reference materials — single shape via the `bees` resolver.** Set `--reference-materials` to a single-element JSON array pointing at the Spec Bee created in Step 4 via the `bees` resolver. The `<spec-bee-id>` placeholder is the Spec Bee ID captured at the end of Step 4a (and confirmed `ready` after Step 4c):

```
[{"value":"<spec-bee-id>","resolver":"bees"}]
```

Downstream skills do a two-hop lookup: they read the Plan Bee's `reference_materials`, follow the `bees` resolver to the Spec Bee, and walk the Spec Bee's children to find the PRD and SDD `t1=Doc` tickets. The PRD/SDD-file-paths shape (passing repo-relative or absolute paths via the implicit `file-path` resolver) is no longer used by `/quo-plan` — that shape moves to `/quo-plan-from-specs` exclusively, which already supports it for hand-authored cumulative-doc flows. The previous body-as-spec branch (omitting `--reference-materials` when no PRD/SDD existed) also no longer applies on this skill's path: `/quo-plan` always creates a Spec Bee in Step 4 and always sets `reference_materials` to point at it, so there is no longer a "no PRD/SDD for this feature" branch here. Users still mid-run on a pre-redesign flow should re-run `/quo-plan` from the start to pick up Step 4's Spec Bee creation.

**Scoped-marker note.** `/quo-plan` does NOT emit a `Scoped to '### Feature: <title>' from <prd-path> and <sdd-path>.` marker line in the Plan Bee body. The Scoped-marker contract documented in `docs/doc-writing-guide.md` remains valid for `/quo-plan-from-specs --feature` only — that skill operates on cumulative project PRD/SDD docs where multiple `### Feature:` subsections coexist and downstream skills need a marker to identify the active subsection. `/quo-plan` no longer co-mingles per-feature content into shared cumulative docs (the Spec Bee + `reference_materials` redesign is precisely what removed that coupling), so the marker is unnecessary here.

```bash
# POSIX (bash / zsh):
bees create-ticket \
  --ticket-type bee \
  --hive plans \
  --status drafted \
  --title "<feature title>" \
  --body-file <path> \
  --reference-materials '[{"value":"<spec-bee-id>","resolver":"bees"}]'
```

```powershell
# Windows (PowerShell):
bees create-ticket `
  --ticket-type bee `
  --hive plans `
  --status drafted `
  --title "<feature title>" `
  --body-file <path> `
  --reference-materials '[{"value":"<spec-bee-id>","resolver":"bees"}]'
```

Mark the Plan Bee as `drafted` initially — its children (Epics) have not been written yet. Step 5d-ii below promotes it to `ready` once Epics exist and the fresh-eyes plan-review gate (Step 5e) has cleared.

#### 5b — Break the feature into Epics

**Reuse-mode note.** If 5a entered the reuse-mode branch (existing `drafted` Plan Bee found and the user picked `Reuse existing Plan Bee and Epics`), seed this step's decomposition from the existing Epic bodies (`bees show-ticket --ids <epic-id>` per captured child) rather than starting fresh. The user MAY keep all Epics, modify some, add new ones, or drop existing ones — the rules below still apply against the resulting list. Tracking which proposed Epic maps to which existing child (by title, after normalization) is what lets 5d-i route as `update-or-create-or-delete` later.

Use the same Epic-decomposition rules as `/quo-plan-from-specs` Step 3:

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

The Epic-approval `AskUserQuestion` in this sub-step fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this Epic-approval gate (per Step 5g's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` the moment the user's answer is consumed.

**Reuse-mode note.** If 5a entered reuse-mode, the "creating any Epic tickets" framing below also covers `bees update-ticket` and `bees delete-ticket` operations in 5d-i. Surface the reuse-vs-new origin per Epic in the presentation (e.g., tag each Epic as `(existing)`, `(modified)`, `(new)`, or call out dropped existing Epics that 5d-i will `bees delete-ticket`) so the user sees which ones carry over before they approve. For any dropped existing Epic whose `children` array (from the `bees show-ticket --ids <epic-id>` payload 5b already fetched per existing Epic) is non-empty, annotate it visibly — e.g., `(existing — to be deleted; has N child Task(s), cascade prompt will fire in 5d-i)` — so the user sees the cascade risk at this approval gate as well as at the 5d-i per-Epic prompt.

Before creating any Epic tickets, present the full proposed Epic list to the user as markdown — title, description, dependencies for each. Use `AskUserQuestion` with options:

- "Yes, create them"
- "Modify the Epics"
- "Cancel"

Wait for approval. If the user picks "Modify the Epics", iterate in prose until they approve, then re-prompt with `AskUserQuestion`.

#### 5d-i — Create Epics and wire dependencies (Plan Bee stays `drafted`)

The children-cascade guard `AskUserQuestion` fired in reuse-mode when a dropped Epic has non-empty `children` (from `b.9q3`) fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this children-cascade gate (per Step 5g's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` the moment the user's answer is consumed and the delete / keep / cancel branch is entered. The guard fires zero times in the dominant reuse-mode path (no dropped Epic has children), so the per-Epic `gate-*` overhead is zero on that path.

Epic creation and Plan Bee promotion are split across two sub-steps with the fresh-eyes plan-review gate (Step 5e) sandwiched between them. This sub-step (5d-i) creates the Epic tickets and wires their `up_dependencies` while the Plan Bee remains `drafted`; sibling sub-step 5d-ii transitions the Plan Bee from `drafted` to `ready`, and runs only after Step 5e has cleared. The split is load-bearing: the plan-review gate may surface findings whose Revise path re-authors Epic bodies or even re-wires dependencies, and routing the user through Revise after the Plan Bee has already promoted to `ready` would force a `ready → drafted` demotion of the Plan Bee — a transition the workflow has no clean precedent for. Splitting the promotion off into its own sub-step keeps the `drafted → ready` flip as the load-bearing "no more changes are expected" signal it already is across the rest of the workflow.

Create each approved Epic as a `t1` child of the Plan Bee with status `drafted`. Use the same temp-file + `--body-file` pattern as in 5a (author body to `<tempdir>/.quorum/`, pass path; do not delete after). **Do not pass `--reference-materials` on Epics** — the bees CLI accepts `--reference-materials` only on top-level Bees (`bees create-ticket --help`: "Only supported on bee (top-level) tickets") and hard-errors on child tiers. Downstream skills trace Epics back to PRD/SDD via the parent Plan Bee's `reference_materials`, not the Epic's.

**Reuse-mode routing.** If 5a entered reuse-mode, replace the blind-create flow with the `update-or-create-or-delete` reconcile described in 5a's "Reuse-mode downstream behavior" section: for each approved Epic that matches an existing child Epic by title (after the normalization 4a uses for Spec Bee titles), `bees update-ticket --ids <epic-id> --body-file <path>` against the existing ticket; for each approved Epic with no match, `bees create-ticket` as below; for each existing child Epic NOT in the approved list, `bees delete-ticket --ids <epic-id>` (subject to the children-cascade guard immediately below). Dependency wiring (further down this sub-step) runs against the final post-reconcile Epic set.

**Children-cascade guard.** Before issuing `bees delete-ticket --ids <epic-id>` against a dropped Epic, inspect the `children` array from the `bees show-ticket --ids <epic-id>` payload Step 5b already fetched per existing Epic — `bees delete-ticket` cascades to all descendants, so dropping an Epic that has been broken down into Tasks would silently destroy the authored Task work. When the array is empty (the dominant case — the user Cancelled at 5e before any Task breakdown), proceed with the delete as today. When the array is non-empty, the Epic has authored Task work underneath; surface the situation to the user via `AskUserQuestion` per CLAUDE.md `## AskUserQuestion usage` with finite choices `Delete Epic and N child Task(s)` / `Keep Epic in decomposition` / `Cancel reconcile` before the delete fires. On `Delete Epic and N child Task(s)`, proceed with the cascade (the user has explicitly consented). On `Keep Epic in decomposition`, add the Epic back to the approved post-reconcile Epic list and skip the delete — the rest of 5d-i's wiring (and the dependency-wiring pass below) runs against the updated list. On `Cancel reconcile`, exit the skill cleanly per Step 5a's existing Cancel semantics (the Plan Bee stays `drafted`; the user can re-run later). The guard fires zero times when no dropped Epic has children (which is the dominant reuse-mode path), so there is no UX regression on the flow the original reuse-mode fix was designed for.

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

Capture the comma-separated Epic ID list — Step 5e (the fresh-eyes plan-review gate) embeds it in the dispatch prompt. The Plan Bee stays `drafted` at the end of 5d-i; do **not** promote it to `ready` here. Promotion happens in 5d-ii after the plan-review gate clears.

#### 5e — Fresh-eyes plan review

With Epics created and dependencies wired but the Plan Bee still `drafted`, run a fresh-eyes plan-review gate before promoting the Plan Bee. The spec-review gate at 4c is a checklist review of PRD/SDD prose quality (section completeness, criterion measurability, codebase grounding, cross-doc consistency); it does NOT critique the overall plan as a coherent solution to the problem. This gate fills that gap — a cold-start Agent reads PRD + SDD + Plan Bee body + Epics and returns substantive critique on problem framing, approach correctness, Epic decomposition sensibility, and missing risks / alternatives.

**Anti-overlap rule.** This gate is explicitly NOT a re-run of `/quo-spec-review`. The dispatch prompt below names the prose-quality lane as out of scope so the reviewer does not re-litigate spec-review territory. If `/quo-spec-review` has already passed (which it has by construction — 4c is a precondition for reaching 5e), prose-quality findings should not appear here; if they do, they are out of scope and the orchestrator silently discards them when triaging.

**Pre-commitment.** When the dispatched Agent's completion notification fires, you MUST FIRST create a `gate-askuserquestion-<short-suffix>` TaskList task naming this plan-review user-approval gate (per `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`), THEN call `AskUserQuestion` (per the routing trailer the dispatch prompt embeds in its structured output, all three verdict-conditional shapes) in the same turn. The dispatched Agent's trailer will repeat this two-step obligation; treat the trailer as a confirmation, not a new instruction. A text-only response between the Agent return and that tool call is a defect — the same anti-narrate-instead-of-do discipline `/quo-spec-review`'s Step 4 trailer enforces applies here, with the structural two-step contract addressing the residual failure surface that prose-only counter-anchors did not close (see `b.wii`).

##### Dispatch the plan reviewer

Spawn a fresh generalist reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. No custom subagent under `agents/` — this gate is one-shot per `/quo-plan` run, read-only, and its instructions fit inline in the dispatch prompt. The reviewer sees only what the prompt embeds, so the prompt must be fully self-contained. Track the dispatch via a TaskList task named `plan-reviewer-<plan-bee-short-suffix>` (e.g., for Plan Bee `b.abc`, the task name is `plan-reviewer-abc`) with the usual `pending` → `in_progress` → `completed` lifecycle.

Starting skeleton (substitute the placeholders with the IDs captured in earlier steps before sending):

```
You are an independent fresh-eyes plan reviewer for a /quo-plan run that just
authored a Spec Bee (with PRD and SDD t1=Doc children), a Plan Bee, and a set
of Epics under the Plan Bee.

Read the following tickets via `bees show-ticket --ids <id>` (one call per ID):

- Spec Bee: <spec-bee-id>
- PRD child: <prd-ticket-id>
- SDD child: <sdd-ticket-id>
- Plan Bee: <plan-bee-id>
- Epics (comma-separated, one t1 child per ID): <epic-id-list>

Your lane is SUBSTANCE — critique the overall plan as a coherent solution to
the problem:

- Is the problem well understood and framed right?
- Is the approach (as captured in PRD goals + SDD requirements + Epic
  decomposition) sound?
- Are the Epics decomposed sensibly — each one a vertical slice, single
  coherent outcome, leaves the codebase green, testable / demo-able?
- Are there missing risks, missing alternatives, or load-bearing assumptions
  that haven't been examined?

EXPLICITLY OUT OF SCOPE: prose-quality nits — section completeness,
heading-level conventions, criterion measurability, codebase-grounding
citation density, cross-document consistency mechanics. /quo-spec-review has
already passed against the PRD and SDD children and covers that lane; do not
re-litigate it here. If you find a prose-quality issue, drop it.

Do NOT modify any tickets or files. You are a read-only reviewer.

Return findings as a numbered list. For each item include:

- A severity tag, exactly one of: `blocker`, `suggestion`, `nit`.
- A `target:` tag, exactly one of: `PRD`, `SDD`, `Plan-Bee-body`, or
  `Epic:<epic-id>` (the specific Epic ID, when an Epic-scoped finding).
- A one-or-two-sentence description of the substance issue, naming the
  concrete content the orchestrator and writer skills will need to address it.

Example:

  1. `blocker` target: SDD — Requirement SR-3 ("the routing layer caches by
     request hash") contradicts PRD goal G2 ("requests must be idempotent
     against retries with different request bodies"). Either narrow the
     caching key in SR-3 or relax G2 to body-stable idempotency.
  2. `suggestion` target: Epic:t1.abc.1 — Epic title "Wire UI" bundles three
     unrelated user-visible capabilities (login form, settings panel, error
     toasts). Split into three Epics so each leaves the codebase green and
     stands alone as a vertical slice.
  3. `nit` target: Plan-Bee-body — `## Anticipated doc impact` lists the SDD
     entry but not the customer-facing README, which Epic:t1.abc.2 modifies.

After the numbered findings, append exactly one verdict trailer line — pick
exactly one value:

  Plan-review verdict: <one of: approve | revise-recommended | escalate-to-user>

Verdict semantics:

- `approve` — the plan is coherent and well-decomposed; either no findings,
  or only `suggestion` / `nit` items the user can reasonably acknowledge
  and proceed past.
- `revise-recommended` — one or more `blocker` findings the reviewer
  believes should be addressed before downstream skills consume the plan.
- `escalate-to-user` — the reviewer found a substantive ambiguity that
  requires the user's input rather than a writer-skill revision pass (e.g.,
  the PRD's stated approach and the SDD's chosen technical strategy point at
  different problems and only the user can say which one is right).

If the plan is clean and you have no findings, return:

  No plan-review issues found.

  Plan-review verdict: approve

Then append a verdict-conditional routing trailer as the final block of your
response. Pick the trailer shape matching the verdict you just emitted —
emit exactly one shape, verbatim — so the Recommended marker tracks the
verdict (mirroring `/quo-spec-review`'s verdict-conditional Recommended
pattern in its Step 4 Shape 1 vs Shape 2 trailers):

**Shape A — used when verdict is `approve`:**

  **Your next two tool calls MUST be (1) `TaskCreate` for a
  `gate-askuserquestion-<short-suffix>` TaskList task naming this plan-review
  gate, then (2) `AskUserQuestion`** with finite choices
  `Approve & promote Plan Bee (acknowledge findings)` (Recommended) /
  `Approve anyway & promote Plan Bee (override blockers)` / `Revise` /
  `Cancel`. The two calls happen in the same turn — do not yield between
  them. Do not produce a text response describing this gate — fire
  `TaskCreate` and `AskUserQuestion` directly. The two-step contract is the
  structural mitigation for the narrate-instead-of-do failure mode (see
  `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool
  contract`). Mark the `gate-*` task `completed` once `AskUserQuestion`
  returns and the user's answer is consumed. The Plan Bee's `drafted →
  ready` promotion is gated on the user's answer.

**Shape B — used when verdict is `revise-recommended`:**

  **Your next two tool calls MUST be (1) `TaskCreate` for a
  `gate-askuserquestion-<short-suffix>` TaskList task naming this plan-review
  gate, then (2) `AskUserQuestion`** with finite choices
  `Approve & promote Plan Bee (acknowledge findings)` /
  `Approve anyway & promote Plan Bee (override blockers)` /
  `Revise` (Recommended) / `Cancel`. The two calls happen in the same turn
  — do not yield between them. Do not produce a text response describing
  this gate — fire `TaskCreate` and `AskUserQuestion` directly. The two-step
  contract is the structural mitigation for the narrate-instead-of-do
  failure mode (see `docs/doc-writing-guide.md` `## The two-step TaskCreate
  → prescribed-tool contract`). Mark the `gate-*` task `completed` once
  `AskUserQuestion` returns and the user's answer is consumed. The Plan
  Bee's `drafted → ready` promotion is gated on the user's answer.

**Shape C — used when verdict is `escalate-to-user`:**

  **Your next two tool calls MUST be (1) `TaskCreate` for a
  `gate-askuserquestion-<short-suffix>` TaskList task naming this plan-review
  gate, then (2) `AskUserQuestion`** with finite choices
  `Approve & promote Plan Bee (acknowledge findings)` /
  `Approve anyway & promote Plan Bee (override blockers)` / `Revise` /
  `Cancel`. The two calls happen in the same turn — do not yield between
  them. Do not produce a text response describing this gate — fire
  `TaskCreate` and `AskUserQuestion` directly. The two-step contract is the
  structural mitigation for the narrate-instead-of-do failure mode (see
  `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool
  contract`). Mark the `gate-*` task `completed` once `AskUserQuestion`
  returns and the user's answer is consumed. None of the choices carries a
  Recommended marker — the user must judge which path resolves the
  substantive ambiguity. The Plan Bee's `drafted → ready` promotion is
  gated on the user's answer.
```

Wait for the Agent's completion notification before proceeding.

##### Surface the findings and gate the user choice

When the Agent returns, parse the verdict trailer line (`Plan-review verdict: <value>`) and use it to shape a one-or-two-sentence prose preamble before surfacing the findings, mirroring the preamble-by-verdict pattern in `/quo-fix-issue` Section 3:

- **`approve`** — "The fresh-eyes plan reviewer found the plan coherent and well-decomposed. Findings below are acknowledge-and-proceed-grade. Review follows:"
- **`revise-recommended`** — "The fresh-eyes plan reviewer flagged one or more `blocker` findings against the plan. Read carefully before deciding how to proceed. Review follows:"
- **`escalate-to-user`** — "⚠️ The fresh-eyes plan reviewer surfaced a substantive ambiguity that needs your input rather than a writer-skill revision pass. Review follows:"

After the preamble, surface the numbered findings list verbatim as prose, then call `AskUserQuestion` per the routing trailer the Agent emitted. Finite choices (the trailer prescribes these literal options; the Recommended marker depends on the verdict per the dispatch-prompt Shape A/B/C trailers above):

- **Approve & promote Plan Bee (acknowledge findings)** — user accepts the plan as-is, treating any `suggestion` / `nit` items as acknowledge-and-proceed-grade. The intended path for verdicts `approve` (no blockers) and `escalate-to-user` once the user has read the surfaced ambiguity and judged it acceptable. Capture acknowledged findings for the Step 5f end-of-skill report's **Acknowledged plan-review findings** bucket, then proceed to Step 5d-ii (Plan Bee promotion).
- **Approve anyway & promote Plan Bee (override blockers)** — user takes explicit responsibility for promoting despite one or more `blocker` findings. Mirrors `/quo-spec-review`'s 4c "Proceed anyway (override blockers)" path. Capture the overridden blocker findings (full list) for the Step 5f end-of-skill report's **Overridden plan-review blockers** bucket, then proceed to Step 5d-ii. The override path exists because plan-level critique is not a hard contract — there are legitimate cases where a `blocker`-tagged finding does not apply (e.g., the reviewer flagged a "missing alternative" the user has already considered and dismissed out-of-band).
- **Revise** — route findings back through the affected writers / amendments per the routing branches below.
- **Cancel** — exit cleanly. Plan Bee stays `drafted`, Epics stay `drafted`, run ends. Re-invoking `/quo-plan` against the same Spec Bee picks the orphan state back up cleanly: Step 4a's Spec-Bee reuse detection finds the existing Spec Bee, and Step 5a's Plan-Bee reuse detection finds the existing `drafted` Plan Bee + its `drafted` Epic children — the user is prompted to either reuse them (and modify the Epic decomposition through Step 5b/5c/5d-i's idempotent reuse path) or create a fresh Plan Bee. No manual cleanup is required between Cancel and re-run.

Mark the `plan-reviewer-<plan-bee-short-suffix>` TaskList task `completed` once the Agent's findings are surfaced (regardless of which branch the user picks); the dispatch is one-shot and its work is done at this point.

##### Revise routing

When the user picks **Revise**, route each finding by its `target:` tag:

- **PRD-targeted findings** (`target: PRD`) — re-invoke `/quo-write-prd` via the `Skill` tool with the existing inline-invocation `args` payload extended with a `findings:` field. The writer skill's `findings:` field accepts both spec-review-shaped items (square-bracketed severity tag + PRD-section anchor) and plan-review-shaped items (backticked severity tag + `target:` tag) — see `skills/quo-write-prd/SKILL.md`'s `## Inline invocation via the Skill tool` → `### Input shape` section. Include the relevant subset of plan-review findings verbatim, preserving the severity tag (`blocker` / `suggestion` / `nit`), the `target:` tag, and the descriptive body. The writer routes through its Step 5 Branch B (update existing PRD child).
- **SDD-targeted findings** (`target: SDD`) — symmetric re-invocation of `/quo-write-sdd` with the SDD-tagged findings under the `findings:` field. `/quo-write-sdd`'s `findings:` field accepts the same two item shapes as `/quo-write-prd`'s. The writer routes through its Step 6 Branch B (update existing SDD child).
- **Plan-Bee-body-targeted findings** (`target: Plan-Bee-body`) — re-author the Plan Bee body in the orchestrator turn (no Skill tool — the orchestrator owns the Plan Bee). Use the same temp-file pattern Step 5a uses (write body via the `Write` tool to `/tmp/.quorum/bees-body-<short-suffix>.md` on POSIX or `$env:TEMP\.quorum\bees-body-<short-suffix>.md` on Windows; create the `.quorum` subdir first if absent). Then update via:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.quorum
  # then write the revised body to /tmp/.quorum/bees-body-<short-suffix>.md via the Write tool
  bees update-ticket --ids <plan-bee-id> --body-file <path>
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
  # then write the revised body to $env:TEMP\.quorum\bees-body-<short-suffix>.md via the Write tool
  bees update-ticket --ids <plan-bee-id> --body-file <path>
  ```

- **Epic-targeted findings** (`target: Epic:<epic-id>`) — re-author the named Epic's body in the orchestrator turn using the same temp-file + `--body-file` pattern as 5d-i, then `bees update-ticket --ids <epic-id> --body-file <path>`. If a decomposition-level finding implies re-wiring `up_dependencies` (e.g., splitting an Epic, merging two Epics, changing the blocking order), adjust dependencies as part of the same Revise pass.

**One-pass `/quo-spec-review` re-run cap on PRD/SDD revisions.** When the Revise branch re-invokes `/quo-write-prd` or `/quo-write-sdd` (PRD- or SDD-targeted findings), the writer skills change `ready` PRD/SDD children, so the existing 4c spec-review contract applies. Re-run `/quo-spec-review <spec-bee-id>` as a follow-up gate **once** before re-running the plan reviewer. Cap this re-run at one pass — if `/quo-spec-review` returns `blocker` findings on the post-Revise re-run, surface those to the user (do not auto-iterate the spec-review side and the plan-review side together). Surfacing means: read the spec-review findings to the user as prose, call `AskUserQuestion` with finite choices `Address spec-review blockers, then re-run plan reviewer` / `Skip remaining spec-review findings and re-run plan reviewer now` / `Cancel`. The cap exists to prevent a plan-review → writer → spec-review → writer → plan-review nesting that exceeds either gate's ~3-turn budget. When `/quo-spec-review` returns no blockers on the re-run (or only `suggestion` / `nit` items the user acknowledges through 4c's existing acknowledge gate), proceed to re-dispatch the plan reviewer.

When the Plan-Bee-body- or Epic-targeted Revise branches fire WITHOUT any PRD/SDD revisions, skip the `/quo-spec-review` re-run entirely — no Doc-child content has changed, so the spec-review gate has nothing new to evaluate.

##### Re-dispatch the plan reviewer after Revise

After Revise routing completes (writer skills returned successfully, in-place updates landed, and the optional `/quo-spec-review` re-run cleared), re-dispatch the plan reviewer with the same prompt template. Use a TaskList task name `plan-reviewer-<plan-bee-short-suffix>-rev<n>` where `<n>` is the 1-based revision count (e.g., `plan-reviewer-abc-rev1` for the first revision). Mark each prior plan-reviewer task `completed` before issuing the new dispatch. Loop back to "Surface the findings and gate the user choice" above.

##### Time-budget short-circuit

Mirror the `/quo-spec-review` time-budget bounds. If a single plan-review dispatch returns more than ~10 items OR the review-fix-review loop runs more than ~3 turns, stop iterating. Triage the returned list down to `blocker`-severity items only, route those through the Revise branches above, and capture deferred `suggestion` / `nit` items for the Step 5f end-of-skill report's deferred bucket. After this final triage-and-Revise pass, do not re-dispatch the plan reviewer — proceed directly to Step 5d-ii's promotion call. These thresholds are guidance, not a hard contract — pick the firmer side when the loop is thrashing on subjective decomposition-shape preferences, the looser side when each finding is high-signal. The 3-turn bound is intentional and mirrors `/quo-spec-review`'s rationale: plan-level substance has a small surface area relative to a Task-sized code diff, so 3 turns of revision is usually enough; thrashing past 3 turns almost always means subjective churn rather than missing-substance correctness.

#### 5d-ii — Promote the Plan Bee from `drafted` to `ready`

When the fresh-eyes plan-review gate (Step 5e) returns control via either of the two Approve choices (`Approve & promote Plan Bee (acknowledge findings)` or `Approve anyway & promote Plan Bee (override blockers)`), or via the time-budget short-circuit after blocker triage, transition the Plan Bee:

```bash
# POSIX (bash / zsh):
bees update-ticket --ids <plan-bee-id> --status ready
```

```powershell
# Windows (PowerShell):
bees update-ticket --ids <plan-bee-id> --status ready
```

The Plan Bee's `ready` transition is gated on the Spec Bee referenced in `reference_materials` already being `ready` — Step 4c (sibling sub-step) ensures that gate by promoting the Spec Bee to `ready` only after both its PRD and SDD `t1=Doc` children pass the writer-skill approval gates, so by the time control reaches this promotion call the gate is already satisfied. The Plan Bee's children — Epics — are now written, even though the Epics' children — Tasks — are not.

#### 5f — Report

Output a markdown summary listing the Plan Bee, each Epic (ID, title, status, dependencies), and any dependency relationships created. Also surface any spec-review **or** plan-review findings that were captured during the run but not addressed before the Plan Bee was promoted — split into the same three buckets for each gate:

**Spec-review findings (from 4c's gate):**

- **Acknowledged spec-review findings** — `suggestion`/`nit` items the user explicitly accepted via "Proceed (acknowledge findings)" during 4c's spec-review gate.
- **Overridden spec-review blockers** — `blocker` items the user explicitly overrode via "Proceed anyway (override blockers)" during 4c's spec-review gate.
- **Spec-review items deferred by the time-budget short-circuit** — `suggestion`/`nit` items that the ~10-item / ~3-turn budget set aside.

**Plan-review findings (from 5e's gate):**

- **Acknowledged plan-review findings** — `suggestion`/`nit` items the user explicitly accepted via "Approve & promote Plan Bee (acknowledge findings)" during 5e's plan-review gate.
- **Overridden plan-review blockers** — `blocker` items the user explicitly overrode via "Approve anyway & promote Plan Bee (override blockers)" during 5e's plan-review gate (rare; the Recommended path on blockers is Revise, but the user retains override authority).
- **Plan-review items deferred by the time-budget short-circuit** — `suggestion`/`nit` items that the ~10-item / ~3-turn budget set aside on 5e.

If a given gate ran with no findings (or no surfaced-but-unaddressed findings), omit its bucket sub-section entirely. If both gates ran clean, omit both buckets — the report stays clean. The point of surfacing them in one end-of-skill view is to give the user a single coherent picture of what was *intentionally not addressed* across both gates before the Plan Bee promoted, so they can decide whether to file follow-up Issues or revise the artifacts before downstream skills consume them.

#### 5g — Before handoff — deferral hygiene

Every `AskUserQuestion` firing in this gate (Step 2's initial Fix / File / Encode choice, plus any Step 3 re-fires when an earlier routing branch failed to close out a subset of the active `defer-*` set) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate (a distinct `<short-suffix>` per fire, so the Step 3 re-fires are not mistaken for the Step 2 first fire), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed.

`/quo-plan` uses a per-skill TaskList convention scoped to the dispatches it makes during a run (e.g., `plan-reviewer-<plan-bee-short-suffix>` for the Step 5e fresh-eyes reviewer, the dispatched-skill conventions belonging to `/quo-write-prd` / `/quo-write-sdd` / `/quo-spec-review` invoked inline from Step 4). This gate introduces an additional **deferral-ledger task** convention used by Step 5g exclusively, alongside a **gate-task** convention used at every `AskUserQuestion` gate-firing site:

- **Deferral-ledger tasks** — **Run scope**. Name: `defer-<short-suffix>` (e.g., `defer-1`, `defer-2`, or any collision-resistant suffix). Created when an inline-invoked writer/reviewer skill or the orchestrator itself surfaces an item with a destination annotation — `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` — that the orchestrator chose not to address inline this run, OR when Step 5f's three Step-4c spec-review buckets (acknowledged findings, overridden blockers, time-budget-deferred items) and three Step-5e plan-review buckets surface findings the user accepted at the gate without authoring an explicit destination. `metadata.activity` carries the deferral's one-line description so the gate prose below can surface the active set. Marked `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (in which case `metadata.activity` logs the resolution path). The pre-handoff gate below reads this ledger for active `defer-*` entries and refuses to yield control while any remain pending or in-progress.
- **Gate-task tasks** — **Turn scope**. Name: `gate-<kind>-<short-suffix>` (today the dominant `<kind>` is `askuserquestion`, e.g. `gate-askuserquestion-1` for an `AskUserQuestion` gate fired during Step 4a's Spec-Bee reuse-or-create gate, Step 4c's spec-review user-approval gate, Step 5a's Plan-Bee reuse-or-create gate, Step 5c's Epic-approval gate, Step 5d-i's children-cascade guard, Step 5e's plan-review user-approval gate, Step 5g's deferral-hygiene gate, or Step 6's Offer-Next-Steps menu). Created by the orchestrator via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract documented in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. The `<short-suffix>` MUST be unique per fire within the same run across every `gate-*` task regardless of `<kind>` — see the per-fire-uniqueness rule in that contract section for the two acceptable patterns (monotonic integers or gate-specific slugs encoding context like `gate-askuserquestion-cascade-veq`). The two-step contract applies at every gate this skill fires — both the trailer-driven gates surfaced by the dispatched skills (Step 4c's spec-review consumption per `/quo-spec-review`'s routing trailer, Step 5e's plan-reviewer Agent's routing trailer) and the trailer-less orchestrator-driven gates listed above. `metadata.activity` carries the gate's finite choices verbatim where applicable. Marked `completed` the moment the prescribed tool call returns and its result has been consumed (the user's answer routed, the next branch entered, etc.). Normally enters and exits within a single turn — the lifecycle is shorter than `defer-*` (which spans the whole run). The **yield-control discipline** mirrors `defer-*`: this skill MUST NOT yield control to the harness while any `gate-*` task is in `pending` or `in_progress` status. If a `gate-*` task is somehow left active when the orchestrator would yield, the next reconciliation tick walks the TaskList, surfaces the active `gate-*` task, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. The `gate-*` namespace coexists without overlap with `defer-*` and `plan-reviewer-<plan-bee-short-suffix>` (and its `-rev<n>` discriminator form).

**Retroactive ledger reconciliation against Step 5f's buckets.** Step 5f enumerates six categories of surfaced-but-unaddressed findings across the spec-review (4c) and plan-review (5e) gates. Before running the gate below, walk Step 5f's buckets and create a corresponding `defer-*` TaskList task for any item that does not already have one — these items were captured for the end-of-skill report but, prior to this gate, had no structural ledger to keep them from being silently dropped at session handoff. After the retroactive reconcile, every Step 5f bucket entry is represented in the active `defer-*` set and the gate below can enumerate the canonical view.

**Step 1 — Enumerate the active deferral ledger.** Scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. If the active set is empty, emit a one-line console message — recommended string: `Deferral hygiene: no deferred items.` — and proceed to Step 6 (Offer Next Steps).

**Step 2 — Surface the active set and gate the user choice.** When the active set is non-empty, surface the list to the user as numbered markdown (one bullet per `defer-*` task, the `metadata.activity` text as the bullet's body), then fire the user gate through the two-step `TaskCreate` → `AskUserQuestion` contract per CLAUDE.md `## AskUserQuestion usage` and `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Step 5g's TaskList naming convention's gate-task entry above), **then** call `AskUserQuestion` with the finite choices below in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the routing into Fix / File / Encode begins.

- **Fix in this session** — Re-invoke the relevant writer skill (`/quo-write-prd` / `/quo-write-sdd`) via the Skill tool against the Spec Bee's PRD or SDD `t1=Doc` child carrying the finding, re-dispatch the plan reviewer per Step 5e's dispatch shape, or do the orchestrator-owned Plan Bee body or Epic body update inline per Step 5e's Revise-routing prose, to resolve each deferred item now. After each item is resolved, mark its `defer-*` TaskList task `completed` (with `metadata.activity` updated to log the resolution path).
- **File as issue tickets** — For each item, invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body (the precedent for inline-Skill-tool dispatch lives in Step 4b's `/quo-write-prd` / `/quo-write-sdd` dispatches). Mark each `defer-*` TaskList task `completed` once the `/quo-file-issue` dispatch returns successfully and the created Issue ID is captured.
- **Encode in an existing ticket body** — For each item the user maps to an existing ticket (the Plan Bee just promoted in Step 5d-ii, one of its Epics, the Spec Bee or one of its `t1=Doc` PRD/SDD children, or the project PRD/SDD via a doc-writer pass), append a `## Deferred from /quo-plan run` section to the named ticket's body and run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update. Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir per CLAUDE.md `## Scratch-file convention`. **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode — e.g., for the encode triggered by `defer-3`, the scratch file is `bees-body-defer-3.md`. Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the scratch file directly back to its TaskList progenitor:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.quorum
  # then write the revised body to /tmp/.quorum/bees-body-<defer-N>.md via the Write tool
  # (e.g., /tmp/.quorum/bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
  # then write the revised body to $env:TEMP\.quorum\bees-body-<defer-N>.md via the Write tool
  # (e.g., $env:TEMP\.quorum\bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  Do NOT remove the temp file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. Mark each `defer-*` TaskList task `completed` once the update succeeds.

The three options are mutually-non-exclusive at the active-set level — the user may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., "fix items 1 and 2 now, file 3 as an Issue"). Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate.

**Step 3 — Hard-stop on a non-empty active set.** Until every `defer-*` task is `completed`, the skill cannot proceed to Step 6 (Offer Next Steps). This is the structural enforcement: a deferral that was important enough to surface during planning is important enough to encode in a durable carrier before the run ends — `/quo-breakdown-epic` and `/quo-execute` read bees tickets, CLAUDE.md, and source code in their fresh sessions and have zero visibility into this session's conversation. If the user picks options that fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or a `bees update-ticket` invocation errors), surface the still-active `defer-*` tasks back to the user with `AskUserQuestion` and re-run the gate until the active set is empty.

The fresh-session-per-phase recommendation at Step 6's menu is preserved verbatim — this gate sits before that handoff prose; it does not replace it.

### 6. Offer Next Steps

The Offer-Next-Steps `AskUserQuestion` menu in this step fires through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this Offer-Next-Steps gate (per Step 5g's TaskList naming convention's gate-task entry), then `AskUserQuestion` in the same turn (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` the moment the user's answer is consumed and the chosen branch is entered.

Present the user with options.

Note above the options: each downstream skill re-reads the Plan Bee, Epics, and CLAUDE.md from the bees CLI and disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives `/quo-breakdown-epic` (and later `/quo-execute`) full context budget for per-Task body authoring and review cycles. Same-session continuation is acceptable as an opt-in for small Bees with one or two Epics.

- **In a fresh session, break down now** (Recommended) — run `/quo-breakdown-epic <bee-id>` in a new Claude Code session to break Epics into Tasks/Subtasks
- **In a fresh session, execute now** — run `/quo-execute <bee-id>` in a new session to start building immediately
- **Continue in this session: break down now** — load `quo-breakdown-epic` and break Epics into Tasks/Subtasks now. Reasonable only for small Bees with one or two Epics
- **Continue in this session: execute now** — load `quo-execute` and start building now. Reasonable only for small Bees with one or two Epics
- **Review first** — let the user review the plan before proceeding
- **Done for now** — plan is saved, user will come back later

### 7. Commit

Stage and commit any in-repo changes from this run. **Do not hardcode the `.bees/plans/` or `.bees/specs/` paths.** `/quo-setup` lets the user choose where each hive lives — in-repo, sibling-to-repo, or anywhere else; the Plans hive and the Specs hive can be configured independently. A hardcoded `git add .bees/plans/ .bees/specs/` silently stages nothing for whichever hive lives at a sibling path. Likewise, **do not hardcode `docs/`** into the `add` list as a default — under this skill's current design, the doc paths configured via CLAUDE.md `## Documentation Locations` (PRD / SDD / customer-facing docs) are not modified during planning at all (Step 4 routes PRD/SDD authoring through ticketed Spec Bee children, not direct file writes), so the no-docs-changes case is the dominant path on every `/quo-plan` run.

**Note:** the docs-changes branch below effectively never fires for `/quo-plan` after Step 4's redesign — it remains as a defensive fallback for the rare case where a future skill change reintroduces planning-time doc edits, or where the user happened to manually edit a doc file in the same session before invoking `/quo-plan`. The `/quo-plan-from-specs` skill has its own commit logic and is out of scope here.

#### Dominant path — no docs changes

On a normal `/quo-plan` run, the artifacts touched in the working tree are the Plan Bee ticket file (and its Epic children) under the **Plans hive**, plus the Spec Bee ticket file (and its PRD + SDD `t1=Doc` children created in Step 4) under the **Specs hive** — and only for whichever of those hives live inside the repo. Resolve both the Plans and Specs hive paths via `bees list-hives`, check each independently for in-repo-ness, and stage the in-repo paths (could be zero, one, or both). When neither hive lives in the repo, the `add` list is empty — skip `git add` entirely and skip the commit, then report to the user:

> Plan stored in bees; no in-repo changes to commit.

The bees CLI has already persisted the Spec Bee, the Plan Bee, and their respective children to its own storage (which lives under the hive paths the user picked); when both hives are sibling-to-repo, no git-tracked artifacts changed in the current repo, so there is genuinely nothing to commit from this skill. The two hives are checked independently because `/quo-setup` lets the user configure each hive's storage location separately — Plans in-repo and Specs sibling-to-repo (or vice versa) is a legitimate configuration that this commit step handles cleanly.

```bash
# POSIX (bash / zsh):
plans_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="plans"), None); print(p or "")')
specs_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="specs"), None); print(p or "")')
repo_root=$(git rev-parse --show-toplevel)
git_add_args=""
case "$plans_path" in
  "$repo_root"|"$repo_root"/*) git_add_args="$plans_path" ;;
esac
case "$specs_path" in
  "$repo_root"|"$repo_root"/*) git_add_args="${git_add_args:+$git_add_args }$specs_path" ;;
esac
```

```powershell
# Windows (PowerShell):
$hives = (bees list-hives | ConvertFrom-Json).hives
$plansPath = $hives | Where-Object { $_.normalized_name -eq 'plans' } | Select-Object -ExpandProperty path
$specsPath = $hives | Where-Object { $_.normalized_name -eq 'specs' } | Select-Object -ExpandProperty path
$repoRoot = git rev-parse --show-toplevel
# Normalize separators — git rev-parse returns forward slashes on Windows;
# bees list-hives may return backslashes. Compare both sides on the same form.
$plansNorm = if ($plansPath) { $plansPath.Replace('\','/') } else { '' }
$specsNorm = if ($specsPath) { $specsPath.Replace('\','/') } else { '' }
$repoNorm = $repoRoot.Replace('\','/')
$addArgs = @()
if ($plansNorm -and ($plansNorm -eq $repoNorm -or $plansNorm.StartsWith("$repoNorm/"))) {
  $addArgs += $plansPath
}
if ($specsNorm -and ($specsNorm -eq $repoNorm -or $specsNorm.StartsWith("$repoNorm/"))) {
  $addArgs += $specsPath
}
```

Then branch on the resulting `add` list:

- **At least one hive in-repo** (`add` list non-empty) — stage all in-repo hive paths and commit:

  ```bash
  # POSIX (bash / zsh):
  git add $git_add_args
  ```

  ```powershell
  # Windows (PowerShell):
  git add @addArgs
  ```

  ```bash
  # POSIX (bash / zsh):
  git commit -m "Plan feature: <title>"
  ```

  ```powershell
  # Windows (PowerShell):
  git commit -m "Plan feature: <title>"
  ```

- **Both hives out-of-repo** (`add` list empty) — **do not** invoke `git add` with no arguments. `git add` with no positional arguments is rejected outright in modern git versions, but on older configurations or if the empty-list expansion ever resolved to a wildcard, it could stage the entire working tree by accident. PowerShell's `git add @addArgs` splats an empty array into a no-arg invocation, which carries the same risk. Skip the `git add` call entirely, skip the `git commit`, and surface the user-facing message above. The Spec Bee, Plan Bee, and their children are already persisted by the bees CLI under the user's configured hive paths; nothing else needs git tracking.

#### Defensive fallback — docs were modified this session

If, contrary to the dominant flow, a doc path configured under CLAUDE.md `## Documentation Locations` was modified in this session (e.g., the user manually edited a doc file outside of `/quo-plan`'s control before invoking the skill, or a future skill change reintroduces planning-time doc edits), prepend `docs/` to the `add` list before staging. The `docs/` literal is the conventional location `quo-setup` writes paths under and is safe to use in the snippet itself, but the prose above keeps to the contract keys so this remains project-neutral.

```bash
# POSIX (bash / zsh):
git_add_args="docs/ $git_add_args"
```

```powershell
# Windows (PowerShell):
$addArgs = @('docs/') + $addArgs
```

Then stage and commit using the same `git add` / `git commit` pair shown in the dominant-path branch above. If neither `docs/` was modified nor either of the Plans / Specs hives lives in the repo, fall back to the empty-`add`-list guard from the dominant path and skip both `git add` and `git commit`.

### Important Notes

- This skill is **interactive** — it's a conversation, not a batch process
- Do NOT skip the scope approval step — the user must confirm before creating tickets
- If the feature is simple enough to be a single Epic, that's fine — don't over-engineer the plan
- If the feature is actually an issue (something that should work but doesn't), suggest `/quo-file-issue` instead
- The Plan Bee body is intentionally brief — a 2-3 sentence summary plus an `## Anticipated doc impact` section. Substantive PRD/SDD content lives in the Spec Bee's `t1=Doc` children referenced via `reference_materials`.
