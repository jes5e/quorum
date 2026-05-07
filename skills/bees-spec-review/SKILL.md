---
name: bees-spec-review
description: Fresh-eyes review of a Spec Bee's PRD and SDD `t1=Doc` children for clarity, completeness, and internal consistency. Primary use - invoked by `/bees-write-prd` and `/bees-write-sdd` (or `/bees-plan`) to gate a Spec Bee's `drafted → ready` transition. Standalone use - ad-hoc spec review of a Spec Bee, scoped optionally to one Doc child via `--doc PRD` or `--doc SDD`. Returns a simple list of improvement work items.
argument-hint: "<spec-bee-id> [--doc PRD|SDD]"
---

## Overview

This skill performs a fresh-eyes review of the spec content authored under a Spec Bee in the Specs hive — the PRD and SDD `t1=Doc` children produced by `/bees-write-prd` and `/bees-write-sdd`. It returns a list of improvement work items for the caller to act on. The conceptual analog is upstream apiary's `/req-review`; the bees-workflow analogs in shape are `/bees-code-review`, `/bees-test-review`, and `/bees-doc-review`.

By default the skill reviews **both** the PRD child and the SDD child of the named Spec Bee, applying a checklist tailored to each document type plus a cross-document consistency pass. Pass `--doc PRD` or `--doc SDD` to scope the review to a single child (useful when only one of the two has been revised).

**When invoked standalone** (`/bees-spec-review <spec-bee-id>` from the prompt with no orchestrating skill above), the caller is a human or another standalone tool. Output the work-item list and stop. Skip the "infinite loop" concern below — that only applies inside an orchestrator's review-fix-review cycle.

**When invoked by an orchestrating skill** (e.g., `/bees-plan`, `/bees-write-prd`, or `/bees-write-sdd` post-write hook, when those wire in spec review), the caller may loop back with revised content for re-review. Apply the loop-bounding guidance under Step 3.

This skill **returns work items** — it does not edit the PRD or SDD itself. The caller (or human) decides whether and how to address each finding.

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if the Specs hive is not colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`).

This skill does not require CLAUDE.md `## Build Commands` — spec review reads ticket bodies via the bees CLI and produces findings as text; no build/test/lint command runs.

## Parameters

The skill takes one positional argument and one optional flag:

- **`<spec-bee-id>`** (required) — the Spec Bee ticket ID whose PRD and/or SDD children should be reviewed.
- **`--doc PRD`** or **`--doc SDD`** (optional) — scope the review to a single Doc child. If omitted, both children are reviewed.

If the user invokes `/bees-spec-review` with no `<spec-bee-id>`, ask them in prose for the Spec Bee ID and let them reply in their next turn — do NOT use `AskUserQuestion`, since ticket IDs are free-text answers, not a finite set of choices.

## Your Mission

Read the PRD and/or SDD bodies hanging off the named Spec Bee, then return a focused list of actionable improvement work items. Each finding carries a `severity` (`blocker`, `suggestion`, or `nit`) and a one-line description, mirroring the shape used by the other three review skills.

Be thorough but not pedantic — focus on substance over style.

### Scope: what counts as "spec content" for this review

In scope:

- The body of the **PRD** child (`t1=Doc` child titled exactly `PRD` under the Spec Bee). Twelve required sections — see `/bees-write-prd`'s Step 4.
- The body of the **SDD** child (`t1=Doc` child titled exactly `SDD` under the Spec Bee). Seven required sections — see `/bees-write-sdd`'s Step 5.
- Internal consistency between the two: any contradiction or unexplained mismatch between PRD and SDD content for the same feature.

Out of scope:

- Source code under `skills/`, `agents/`, or any other repo path — `/bees-code-review`'s territory.
- Test files — `/bees-test-review`'s territory.
- User-facing project docs (`README.md`, the cumulative project PRD/SDD on disk) — `/bees-doc-review`'s territory.
- The Spec Bee body itself (the parent ticket). Spec Bee bodies are typically short scope notes; the spec content under review lives in the Doc children, not the Bee body.

If the named Spec Bee has neither a PRD nor an SDD child (or only the one excluded by `--doc`), output `No spec content to review` and exit.

## Workflow

### Step 0: Resolve the Doc children

Locate the PRD and/or SDD children of the named Spec Bee using a freeform query. The query is regex-based on title; pin both ends so the match is exact and case-sensitive.

If the user did not pass `--doc`, query for both children:

```bash
# POSIX (bash / zsh):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^(PRD|SDD)$]
report: [ticket_id, title, ticket_status]'
```

```powershell
# Windows (PowerShell):
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^(PRD|SDD)$]
report: [ticket_id, title, ticket_status]'
```

If `--doc PRD` was passed, narrow the title regex to `^PRD$`; if `--doc SDD`, narrow to `^SDD$`.

Capture the ticket IDs returned. If zero matches were returned for the requested scope, output `No spec content to review` and exit. If more than one match per title was returned (should not happen given the exact-title filter), surface the anomaly to the user and stop — the user must resolve which Doc is canonical before review can proceed.

### Step 1: Fetch each Doc body

For each resolved Doc child, fetch the body via `bees show-ticket --ids <doc-ticket-id>`. Read the body as the source-of-truth content for the review — do not read any on-disk file as a substitute. The Doc body in bees is what downstream skills (`/bees-breakdown-epic`, `/bees-execute`'s Engineer / PM, `/bees-fix-issue`) consume; if there is a mismatch between the bees ticket body and any on-disk artifact, the bees body wins for review purposes.

```bash
# POSIX (bash / zsh):
bees show-ticket --ids <doc-ticket-id>
```

```powershell
# Windows (PowerShell):
bees show-ticket --ids <doc-ticket-id>
```

### Step 2: Review each Doc — Critical Eye

Apply the appropriate checklist based on the Doc's title. Both checklists assume familiarity with the section structure imposed by `/bees-write-prd` and `/bees-write-sdd`; if a required section is missing entirely (rather than rendered with an explicit-`none` placeholder), flag that as a `blocker` regardless of the rest of the content.

#### PRD checklist

Apply these checks to the PRD body. Cite the section heading in each finding so the caller knows where to look.

##### 1. Section completeness
- Are all twelve required sections present? Missing a section entirely is a `blocker`. (See `/bees-write-prd` Step 4 for the canonical list.)
- For sections rendered with the explicit-`none` placeholder, does the placeholder use the prescribed phrase rather than a vague "TBD" or empty heading? Vague placeholders are a `suggestion`.

##### 2. Problem statement clarity
- Does `## Problem Statement` describe a concrete problem with named users / personas, or is it a generic "users want X" sentence with no actor? Generic problem statements are a `blocker` — downstream agents need to know who the work is for.
- Does the problem statement explain *why now*, or is the timing implicit? Missing why-now is a `suggestion`.

##### 3. Acceptance criteria measurability
- Is every entry under `## Acceptance Criteria` objectively verifiable (an artifact a user can interact with, or an automated check that decides pass/fail)? Subjective criteria ("the experience feels polished", "performance is good") are a `blocker` — they cannot be used to gate Bee close-out.
- Does each criterion correspond to a goal in `## Goals` or a requirement in `## Functional Requirements`? Orphan criteria (no upstream goal) and orphan goals (no downstream criterion) are a `suggestion`.

##### 4. Scope clarity
- Does `## Non-Goals / Out of Scope` list specific exclusions, or is it empty / hand-wavy ("anything not above")? Hand-wavy non-goals are a `suggestion` — downstream scope creep is the failure mode this section exists to prevent.
- Does any goal or requirement contradict an entry in `## Non-Goals / Out of Scope`? Internal contradictions are a `blocker`.

##### 5. Implementation-detail leakage
- Does the PRD body name specific classes, modules, libraries, or API call sequences? PRDs cover *what* and *why*, not *how*; implementation-detail content belongs in the SDD. Flag as a `suggestion` and recommend moving the content to the SDD.

##### 6. Vague language
- Look for absolutes ("always", "never", "all users") that lack qualification, and for soft language ("should be fast", "scales well", "user-friendly") with no measurable threshold. Both are a `suggestion` — ask for measurable thresholds or explicit `## Open Questions` entries.

##### 7. Rationale and decisions
- Do `## Background and rationale` and `## Decisions and rejected alternatives` each have substantive content, or do both render the explicit-`none` placeholder despite the surrounding sections looking heavily-discussed? Suspiciously-empty rationale on a substantive PRD is a `suggestion` — ask whether the planning conversation produced rationale that should have been captured.
- Are decisions in `## Decisions and rejected alternatives` written with both the chosen path AND the rejected alternatives, with reasoning for each? Decisions captured without alternatives are a `suggestion`.

##### 8. Open questions discipline
- Are entries in `## Open Questions` actionable (named owner, named decision needed), or are they free-floating uncertainty? Unowned open questions are a `nit`.

#### SDD checklist

Apply these checks to the SDD body. Cite the section heading in each finding.

##### 1. Section completeness
- Are all seven required sections present? Missing a section entirely is a `blocker`. (See `/bees-write-sdd` Step 5 for the canonical list.)
- For sections rendered with the explicit-`none` placeholder, does the placeholder use the prescribed phrase rather than a vague "TBD"? Vague placeholders are a `suggestion`.

##### 2. Codebase grounding
- Does `## Codebase exploration findings` cite real module / file / function names from the actual repo, or does it use generic placeholders ("the routing layer", "the data access layer")? Generic-only findings are a `blocker` — the section's purpose is to give the Engineer concrete starting points.
- Are any `RESEARCH NEEDED: <question>` tags present? Each one is a `suggestion` reminding the user that an open codebase question still needs follow-up before implementation begins. (Tags are not a defect in themselves — they are the prescribed shape for honest ambiguity — but each tag should be surfaced so the user can decide whether to resolve it now or carry it into implementation.)

##### 3. Requirements structure
- Are entries in `## Requirements` numbered with the `SR-` prefix and grouped by domain with at least one heading per group? Unstructured requirement lists are a `suggestion`.
- Does each `SR-` entry describe an observable system behavior (input → behavior → output / state change), or is it a vague aspiration ("the system handles errors well")? Aspirational requirements are a `blocker`.

##### 4. Architecture coverage
- Does the SDD identify the affected subsystems / packages / modules at a top-level (architectural) granularity, or does it dive straight into low-level details without the architectural framing? Missing top-level framing is a `suggestion`.
- Does the SDD cover the new component(s) being introduced (or modified) at component-by-component granularity — what each component does and how the components interact? Coverage that names files but not components is a `suggestion`.

##### 5. Existing-behavior preservation
- Does `## Existing Behavior` enumerate specific contracts that must NOT change (API shapes, persisted-data layouts, on-the-wire protocol fields, configuration knobs whose meaning external callers depend on), or is it generic ("preserve backwards compatibility")? Generic existing-behavior is a `suggestion` for greenfield-adjacent work and a `blocker` for work that touches a public surface.
- For greenfield work, is the section rendered with the prescribed `none — this is greenfield work` placeholder rather than left empty? Empty/missing is a `suggestion`.

##### 6. Test fixture conventions
- Does `## Test Fixtures` name specific helpers, factories, sample-data file paths, or mocking utilities the implementation should reuse? Generic content ("use existing fixtures") is a `suggestion` — the section's purpose is to prevent engineers from hardcoding magic-number test data past existing helper conventions.

##### 7. Documentation coverage
- Does `## Documentation` reference docs by the canonical path from CLAUDE.md `## Documentation Locations`, or does it use guessed names ("the readme", "the architecture doc")? Guessed names are a `suggestion`.
- Does the section identify which docs (cumulative project PRD, SDD, README, engineering best practices) the doc-writer agent will need to update post-implementation, or is it a single-line "update the docs" pointer? Single-line coverage is a `suggestion`.

##### 8. Decomposition signal for downstream Epic breakdown
- Does the SDD give downstream readers (`/bees-breakdown-epic`, `/bees-plan`, the Engineer dispatched by `/bees-execute`) enough material to identify the natural Epic boundaries — i.e., is the design decomposable into a small number of independent-ish work units, or does it read as a single monolith? Lack of decomposition signal is a `suggestion`. (This is not a hard requirement — some features are genuinely monolithic — but flag it so the user can confirm intent.)

##### 9. Data-model and contract-key impacts
- If the design introduces new schemas, persistent entities, or types, are they described in `## Codebase exploration findings` or `## Requirements` with field names and shape? Missing data-model detail when the design clearly affects data is a `suggestion`.
- If the design changes any contract-key surface (downstream skills' lookup keys in CLAUDE.md `## Documentation Locations` or `## Build Commands`, the bees CLI command surface, ticket schema fields, hive names), is the impact called out explicitly? Missing contract-key impact callouts are a `blocker` for any design that touches a contract surface.

##### 10. Rationale and decisions
- Do `## Background and rationale` and `## Decisions and rejected alternatives` each have substantive content when the surrounding sections look heavily-discussed, or do both render the explicit-`none` placeholder? Same shape as the PRD checklist's item 7: suspiciously-empty rationale is a `suggestion`.

#### Cross-document consistency checks

If both PRD and SDD were resolved for review (i.e., `--doc` was not passed), apply these cross-document checks after the per-document passes:

##### 1. Goal-to-requirement coverage
- Does every goal in PRD `## Goals` map to at least one requirement in SDD `## Requirements`? Goals with no SDD requirement are a `blocker` — the design has not addressed a stated goal.
- Does every SDD `SR-` requirement trace back to a PRD goal or functional requirement? Orphan SDD requirements (no PRD upstream) are a `suggestion` — the SDD may have introduced scope the PRD did not authorize.

##### 2. Acceptance-criterion-to-design coverage
- Does the SDD design address every entry under PRD `## Acceptance Criteria`? Acceptance criteria with no SDD coverage are a `blocker`.

##### 3. Out-of-scope alignment
- Does any SDD requirement, fixture, or design element implement something the PRD `## Non-Goals / Out of Scope` explicitly excludes? Out-of-scope leakage is a `blocker`.

##### 4. Open-question alignment
- Does any SDD section confidently make a decision on a question that PRD `## Open Questions` lists as still open? Confident-where-PRD-is-uncertain is a `suggestion` — the user may want to either resolve the open question in the PRD, or downgrade the SDD to a `RESEARCH NEEDED` tag.

##### 5. Rationale alignment
- If both PRD and SDD have substantive `## Decisions and rejected alternatives` content, do the captured decisions agree on the rejected alternatives? Contradictory decision history is a `blocker`.

### Step 3: Prioritize and Filter

Focus on important issues only. The severity ladder:

- **`blocker`** — content gap or contradiction that will cause downstream confusion (Engineer building the wrong thing, breakdown producing wrong-shaped Epics, doc-writer missing required updates). Must be fixed before the Spec Bee transitions `drafted → ready`.
- **`suggestion`** — content quality issue that does not block downstream agents but would make the spec materially clearer if addressed. The user decides whether to address before promotion.
- **`nit`** — minor wording or formatting observation. Mention sparingly.

Each work item should be:

1. Actionable as a standalone follow-up.
2. Specific (cite the document — `PRD` or `SDD` — and the section heading).
3. Important (not trivial).
4. Concise (one-line description).

NOTE: It is expected that many times you will return no important issues. This is OK. Don't feel obliged to report things. Only report if there is something important.

**When invoked from an orchestrating skill** specifically: keep in mind that the orchestrator will loop back with revisions and re-invoke this skill. If you keep reporting trivial-but-not-important items each pass, you create an infinite loop. Be selective. If you have nothing important, say so.

### Step 4: Generate Work Item List

Output a simple numbered list directly in your response:

```markdown
## Spec Review Work Items

1. [blocker] PRD `## Acceptance Criteria` — criterion "smooth experience" is subjective; replace with a measurable threshold or move to `## Open Questions`.
2. [blocker] SDD `## Codebase exploration findings` — generic "the routing layer" reference; cite the actual module path so the Engineer has a starting point.
3. [suggestion] PRD `## Open Questions` — three entries with no named owner; assign each to a person or role.
4. [suggestion] Cross-document — PRD goal G3 has no corresponding SDD requirement under `## Requirements`; either add an SR entry or downgrade G3 to a non-goal.
5. [nit] SDD `## Test Fixtures` — heading uses the prescribed `none — ...` placeholder but the surrounding text re-states "no fixtures apply"; redundant wording.
```

Or if no issues:

```markdown
## Spec Review Work Items

No spec issues found. PRD and SDD are clear, complete, and internally consistent.
```

## Idempotency

This skill reads tickets and writes findings to stdout — it does not mutate any ticket. Re-running `/bees-spec-review <same-spec-bee-id>` against the same spec content produces the same findings (subject to LLM determinism). If the user revises the PRD or SDD between runs, the findings update to reflect the revised content.
