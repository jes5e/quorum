---
name: quo-spec-review
description: Fresh-eyes review of a Spec Bee's PRD and SDD `t1=Doc` children for clarity, completeness, and internal consistency. Primary use — invoked automatically by `/quo-plan` (after both writers complete, before Spec Bee promotion) and by `/quo-write-prd` / `/quo-write-sdd` on their solo path (after the user-approval gate, before the PRD/SDD child's `drafted → ready` promotion); skipped on the inline path from `/quo-plan` to avoid double-cost. Standalone use — ad-hoc spec review of a Spec Bee, scoped optionally to one Doc child via `--doc PRD` or `--doc SDD`. Returns a simple list of improvement work items.
argument-hint: "<spec-bee-id> [--doc PRD|SDD]"
---

## Overview

This skill performs a fresh-eyes review of the spec content authored under a Spec Bee in the Specs hive — the PRD and SDD `t1=Doc` children produced by `/quo-write-prd` and `/quo-write-sdd`. It returns a list of improvement work items for the caller to act on. The quorum analogs in shape are `/quo-engineer-review`, `/quo-test-writer-review`, and `/quo-doc-writer-review`.

By default the skill reviews **both** the PRD child and the SDD child of the named Spec Bee, applying a checklist tailored to each document type plus a cross-document consistency pass. Pass `--doc PRD` or `--doc SDD` to scope the review to a single child (useful when only one of the two has been revised, or when an orchestrating writer skill has only authored / revised one of the two children — `/quo-write-prd` invokes this skill with `--doc PRD`, `/quo-write-sdd` with `--doc SDD`).

**Primary use — orchestrator-invoked.** The three orchestrating skills `/quo-plan`, `/quo-write-prd`, and `/quo-write-sdd` invoke this skill automatically as a quality gate before any Spec Bee or Doc-child `drafted → ready` promotion. `/quo-plan` invokes the skill once with no `--doc` flag (after both writer skills complete, before the Spec Bee parent's promotion); `/quo-write-prd` (when invoked solo, not inline from `/quo-plan`) invokes the skill with `--doc PRD` after its own user-approval gate, before the PRD child's promotion; `/quo-write-sdd` (when invoked solo) does the symmetric thing with `--doc SDD`. The orchestrating skills are responsible for surfacing this skill's findings to the user, looping back to the relevant writer skill when the user picks `Revise`, and applying the time-budget short-circuit described under Step 3.

**Standalone use — ad-hoc.** When the user invokes `/quo-spec-review <spec-bee-id>` directly from the prompt with no orchestrating skill above (e.g., to spot-check an existing Spec Bee outside a planning or revision flow), output the work-item list and stop. Skip the "infinite loop" concern below — that only applies inside an orchestrator's review-fix-review cycle. The standalone path remains supported precisely because there are legitimate ad-hoc-review use cases (auditing a Spec Bee from a prior planning run, reviewing a Spec Bee whose PRD/SDD were edited out-of-band, etc.) that should not require re-invoking a writer skill just to trigger a review.

This skill **returns work items** — it does not edit the PRD or SDD itself. The caller (or human) decides whether and how to address each finding.

## Preconditions

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if the Specs hive is not colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`).

This skill does not require CLAUDE.md `## Build Commands` — spec review reads ticket bodies via the bees CLI and produces findings as text; no build/test/lint command runs.

## Parameters

The skill takes one positional argument and one optional flag:

- **`<spec-bee-id>`** (required) — the Spec Bee ticket ID whose PRD and/or SDD children should be reviewed.
- **`--doc PRD`** or **`--doc SDD`** (optional) — scope the review to a single Doc child. If omitted, both children are reviewed.

If the user invokes `/quo-spec-review` with no `<spec-bee-id>`, ask them in prose for the Spec Bee ID and let them reply in their next turn — do NOT use `AskUserQuestion`, since ticket IDs are free-text answers, not a finite set of choices.

## Your Mission

Read the PRD and/or SDD bodies hanging off the named Spec Bee, then return a focused list of actionable improvement work items. Each finding carries a `severity` (`blocker`, `suggestion`, or `nit`) and a one-line description, mirroring the shape used by the other three review skills.

Be thorough but not pedantic — focus on substance over style.

### Scope: what counts as "spec content" for this review

In scope:

- The body of the **PRD** child (`t1=Doc` child titled exactly `PRD` under the Spec Bee). Twelve required sections — see `/quo-write-prd`'s Step 4.
- The body of the **SDD** child (`t1=Doc` child titled exactly `SDD` under the Spec Bee). Seven required sections — see `/quo-write-sdd`'s Step 5.
- Internal consistency between the two: any contradiction or unexplained mismatch between PRD and SDD content for the same feature.

Out of scope:

- Source code under `skills/`, `agents/`, or any other repo path — `/quo-engineer-review`'s territory.
- Test files — `/quo-test-writer-review`'s territory.
- User-facing project docs (`README.md`, the cumulative project PRD/SDD on disk) — `/quo-doc-writer-review`'s territory.
- The Spec Bee body itself (the parent ticket). Spec Bee bodies are typically short scope notes; the spec content under review lives in the Doc children, not the Bee body.

If the named Spec Bee has neither a PRD nor an SDD child (or only the one excluded by `--doc`), output `No spec content to review` and exit.

## Workflow

### Step 0: Resolve the Doc children

Locate the PRD and/or SDD children of the named Spec Bee using a freeform query. The query is regex-based on title; pin both ends so the match is exact and case-sensitive.

If the user did not pass `--doc`, query for both children. The single-quoted YAML literal works identically in POSIX bash/zsh and Windows PowerShell — one block covers both shells:

```
bees execute-freeform-query --query-yaml 'stages:
  - [hive=specs, parent=<spec-bee-id>, title~^(PRD|SDD)$]
report: [ticket_id, title, ticket_status]'
```

If `--doc PRD` was passed, narrow the title regex to `^PRD$`; if `--doc SDD`, narrow to `^SDD$`.

Capture the ticket IDs returned. If zero matches were returned for the requested scope, output `No spec content to review` and exit. If more than one match per title was returned (should not happen given the exact-title filter), surface the anomaly to the user and stop — the user must resolve which Doc is canonical before review can proceed.

### Step 1: Fetch each Doc body

For each resolved Doc child, fetch the body via `bees show-ticket --ids <doc-ticket-id>`. Read the body as the source-of-truth content for the review — do not read any on-disk file as a substitute. The Doc body in bees is what downstream skills (`/quo-breakdown-epic`, `/quo-execute`'s Engineer / PM, `/quo-fix-issue`) consume; if there is a mismatch between the bees ticket body and any on-disk artifact, the bees body wins for review purposes. The invocation has no shell-variable interpolation, so one block covers both POSIX bash/zsh and Windows PowerShell:

```
bees show-ticket --ids <doc-ticket-id>
```

### Step 2: Review each Doc — Critical Eye

Apply the appropriate checklist based on the Doc's title. Both checklists assume familiarity with the section structure imposed by `/quo-write-prd` and `/quo-write-sdd`; if a required section is missing entirely (rather than rendered with an explicit-`none` placeholder), flag that as a `blocker` regardless of the rest of the content.

#### PRD checklist

Apply these checks to the PRD body. Cite the section heading in each finding so the caller knows where to look.

##### 1. Section completeness
- Are all twelve required sections present? Missing a section entirely is a `blocker`. (See `/quo-write-prd` Step 4 for the canonical list.)
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
- Are all seven required sections present? Missing a section entirely is a `blocker`. (See `/quo-write-sdd` Step 5 for the canonical list.)
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
- Does the SDD give downstream readers (`/quo-breakdown-epic`, `/quo-plan`, the Engineer dispatched by `/quo-execute`) enough material to identify the natural Epic boundaries — i.e., is the design decomposable into a small number of independent-ish work units, or does it read as a single monolith? Lack of decomposition signal is a `suggestion`. (This is not a hard requirement — some features are genuinely monolithic — but flag it so the user can confirm intent.)

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

**Time-budget short-circuit (caller side).** The orchestrating skills (`/quo-plan` Step 4c, `/quo-write-prd` Step 6a, `/quo-write-sdd` Step 7a) bound the review-fix-review loop with a budget mirroring the pattern in `agents/pm.md` for `/quo-engineer-review` and `/quo-doc-writer-review`: if a single `/quo-spec-review` invocation returns more than ~10 work items, OR the review-fix-review loop runs more than ~3 turns of back-and-forth, the orchestrator stops iterating, triages the returned list down to `blocker`-severity items only, asks the writer to address those, and defers `suggestion`/`nit` items to the end-of-skill report. These thresholds are guidance, not a hard contract — pick the firmer side when the review is clearly thrashing on subjective prose-quality nits, the looser side when each item is high-signal. The 3-turn bound (vs pm.md's 5-turn bound for code/doc review) is intentional: spec content has a much smaller surface area than a Task-sized code diff, so 3 turns of revision is usually enough to converge on the substantive fixes; thrashing past 3 turns almost always means subjective-prose churn rather than missing-content correctness. This skill itself does not enforce the budget — it just emits findings — but is aware of it so the per-pass output stays selective.

### Step 4: Generate Work Item List

Output a simple numbered list directly in your response. **Always append a routing trailer in the second-person imperative form** — `**Your next tool call MUST be …**` (or `**Your next tool use MUST …**` where no single tool is named) — that names the precise routing the calling orchestrator (`/quo-plan`'s Step 4c, `/quo-write-prd`'s Step 6a, `/quo-write-sdd`'s Step 7a, or a standalone user invocation) must take after consuming this output, and **always end the trailer with a counter-anchor clause** — `Do not produce a text response describing this gate — call the tool directly.` for `AskUserQuestion` shapes, or `… describing this transition …` for the `bees update-ticket --status ready` shape — that explicitly forbids the narrate-instead-of-do failure mode. **The trailer MUST instruct the orchestrator to perform the two-step `TaskCreate` → prescribed-tool contract** documented in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract` — first create a `gate-<kind>-<short-suffix>` TaskList task, then call the prescribed tool in the same turn — so the prescription is structurally robust against the narrate-instead-of-do failure mode (a missed `TaskCreate` is recoverable; a silent prose yield of the trailer is only recoverable by the user noticing). The trailer is the load-bearing routing prescription — by emitting it as part of the tool output rather than relying on the orchestrator skill to recall a nested rule three levels deep, the prescription is structurally robust against orchestrator-side attention decay. The second-person imperative form, the counter-anchor clause, and the two-step gate-task instruction are required components, not stylistic preferences (see `b.fpm` for the prose-only counter-anchor's failure to close the failure mode, and `b.wii` for the structural two-step contract that narrows but does not close the residual failure surface); third-person framing (e.g., `**Next action for the orchestrator:**`) is a known failure mode where orchestrators emit the descriptive text and yield the turn without firing the prescribed tool call. The orchestrator skills' Loop-back UX sections downgrade to "follow the routing trailer in this skill's output literally"; the exact phrasings live here.

The trailer wording depends on which of the three output shapes applies. Use these phrasings verbatim (only the work-item content above the trailer varies).

Each finding here carries tags along two orthogonal dimensions (the trailer still collapses to three shapes: blockers-present versus suggestions/nits-only versus no-findings):

- A **severity** dimension — every finding carries exactly one severity tag, kept in this skill's pre-existing **bracket** form: `[blocker]` / `[suggestion]` / `[nit]`. Severity describes *how important fixing-at-all is* (the ladder defined in Step 3 above).
- A **depth** dimension carried *per fix path* — every finding enumerates one or more fix paths, and each fix path carries its own depth tag: `trivial-tweak` / `refactor-locally` / `re-architect`. Depth describes *what fixing costs* (the size of the change a given fix path entails).

The two dimensions are orthogonal: a `[blocker]` might be fixable by a `trivial-tweak`, and a `[nit]` might only be addressable by a `re-architect` — knowing one tells you nothing about the other, which is why both are emitted. (The depth tags are emitted here for downstream consumers; no routing rule in this skill consumes them yet.)

**Severity-rendering asymmetry note.** This skill renders severity in `[blocker]` / `[suggestion]` / `[nit]` **bracket** form, whereas `/quo-engineer-review`, `/quo-doc-writer-review`, and `/quo-test-writer-review` render the same three severities in backtick form (`` `blocker` `` / `` `suggestion` `` / `` `nit` ``). This asymmetry is intentional and pre-existing — bracket severity was this skill's original shape — and is SDD-acknowledged. It is benign for the Phase-2 routing parser, which derives its `(num-paths, max-depth)` tuple from the `(<letter>) [depth:...]` fix-path lines (shared byte-for-byte across all four review skills), not from severity rendering. The fix-path enumeration and depth tags below match the shape used by `/quo-engineer-review`, `/quo-doc-writer-review`, and `/quo-test-writer-review` exactly; only the severity bracket-vs-backtick rendering differs.

Line shapes — emit findings exactly in this form:

- finding line: `<n>. [<severity>] <doc + section anchor> <one or more fix-path lines> — <description>` — `[<severity>]` is the bracket-form severity tag; the `<n>.` is the work-item number; the `<doc + section anchor>` cites `PRD` or `SDD` and the section heading; the fix-path line(s) sit between the anchor and the ` — <description>`.
- fix-path line: `(<letter>) [depth:<trivial-tweak|refactor-locally|re-architect>] <description of that fix path>` — lettered `(a)`, `(b)`, … and indented under the finding when there is more than one. A finding with a single fix path emits one fix-path line; a finding with multiple viable fix paths emits one lettered line per path. The shape is uniform whether the reviewer enumerated 1 path or 4, which simplifies the orchestrator's parser.

Worked examples covering every depth bucket, plus both single-path and multi-path emission (spec-review-flavored — PRD/SDD section gaps, measurability, cross-document consistency):

```markdown
1. [nit] SDD `## Test Fixtures` (a) [depth:trivial-tweak] Drop the redundant "no fixtures apply" sentence that restates the `none — ...` placeholder — single fix path, trivially deletable.
2. [suggestion] PRD `## Open Questions` (a) [depth:refactor-locally] Assign each of the three unowned entries a named owner — change confined to one section.
3. [blocker] Cross-document — PRD goal G3 has no corresponding SDD `## Requirements` entry
   (a) [depth:refactor-locally] Add a single `SR-` requirement under the matching SDD domain heading to cover G3.
   (b) [depth:re-architect] Re-derive the SDD requirements structure so every PRD goal traces to a numbered requirement and orphans are eliminated. — multi-path finding: the local patch and the durable structural fix are both viable; the user chooses.
```

**Shape 1 — Blockers present** (one or more `[blocker]` items in the list):

```markdown
## Spec Review Work Items

1. [blocker] PRD `## Acceptance Criteria` (a) [depth:trivial-tweak] Replace the subjective "smooth experience" criterion with a measurable threshold, or move it to `## Open Questions` — criterion is subjective and cannot gate Bee close-out.
2. [blocker] SDD `## Codebase exploration findings`
   (a) [depth:trivial-tweak] Replace the generic "the routing layer" phrase with the actual module path so the Engineer has a starting point.
   (b) [depth:refactor-locally] Rework the section to cite real module/file/function names throughout, not just at this one spot. — generic-only findings defeat the section's purpose.
3. [suggestion] PRD `## Open Questions` (a) [depth:refactor-locally] Assign each of the three unowned entries a named owner or role — change confined to one section.

**Your next two tool calls MUST be (1) `TaskCreate` for a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate, then (2) `AskUserQuestion`** with finite choices `Revise` (recommended) / `Proceed anyway (override blockers)`. The two calls happen in the same turn — do not yield between them. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. The two-step contract is the structural mitigation for the narrate-instead-of-do failure mode (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` once `AskUserQuestion` returns and the user's answer is consumed. The Spec Bee's `drafted → ready` promotion is gated on the user's answer.
```

**Shape 2 — Suggestions / nits only** (no `[blocker]` items, but one or more `[suggestion]` or `[nit]` items):

```markdown
## Spec Review Work Items

1. [suggestion] PRD `## Open Questions` (a) [depth:refactor-locally] Assign each of the three unowned entries a named owner or role — change confined to one section.
2. [suggestion] Cross-document — PRD goal G3 has no corresponding SDD requirement under `## Requirements`
   (a) [depth:refactor-locally] Add a single `SR-` entry under the matching SDD domain heading to cover G3.
   (b) [depth:trivial-tweak] Downgrade G3 to a non-goal in PRD `## Non-Goals / Out of Scope`. — either alignment resolves the mismatch; the user chooses.
3. [nit] SDD `## Test Fixtures` (a) [depth:trivial-tweak] Drop the redundant "no fixtures apply" sentence that restates the prescribed `none — ...` placeholder.

**Your next two tool calls MUST be (1) `TaskCreate` for a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate, then (2) `AskUserQuestion`** with finite choices `Proceed (acknowledge findings)` / `Revise`. The two calls happen in the same turn — do not yield between them. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. The two-step contract is the structural mitigation for the narrate-instead-of-do failure mode (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). Mark the `gate-*` task `completed` once `AskUserQuestion` returns and the user's answer is consumed. The Spec Bee's `drafted → ready` promotion is gated on the user's answer.
```

**Shape 3 — No findings** (clean review):

```markdown
## Spec Review Work Items

No spec issues found. PRD and SDD are clear, complete, and internally consistent.

**Your next tool call MUST be `bees update-ticket --status ready`** against the Spec Bee (or the scoped Doc child, when invoked with `--doc PRD` / `--doc SDD`). Do not produce a text response describing this transition — call the tool directly. The two-step `TaskCreate` → prescribed-tool contract does NOT apply on this shape — per the contract's scoping (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`, `**Scope — user-facing gate prescriptions only**` paragraph), the contract triggers only when the prescribed tool call is a user-facing gate like `AskUserQuestion` whose silent yield would stall the workflow on an invisible prompt; `bees update-ticket --status ready` is a non-user-facing state mutation with no user prompt to silently yield, so it runs without a paired `gate-*` task. The findings-present Shapes 1 and 2 above DO carry the two-step contract because their `AskUserQuestion` prescription is user-facing.
```

**Standalone-invocation note.** When this skill is invoked standalone by a user (not by an orchestrating skill), the second-person `Your next tool call MUST be …` trailer addresses the assistant turn presenting the findings to the user — you are still the orchestrator for this purpose, and the user is still the human in the gate prompt. The trailer still emits in all three shapes; do not suppress it on the standalone path — its presence is also useful as a self-check that the skill considered the routing question, and the imperative form is exactly as load-bearing standalone as it is when an orchestrating skill is reading the output.

**Orchestrator self-tracking close-out (mandatory before yielding, standalone invocation).** When this skill is invoked standalone (not inline from `/quo-plan`, `/quo-write-prd`, or `/quo-write-sdd`), the orchestrator may have created ad-hoc TaskList tasks to break the review into discrete steps (e.g., "Resolve Doc children", "Fetch each Doc body", "Review per checklist", "Synthesize findings"). Before yielding the turn back to the user — either at end-of-flow after presenting the work-item list, or at any question-the-user pause that may follow — mark every such orchestrator self-tracking TaskList task `completed` and clear them from the active set. The yield is the close-out trigger: when the orchestrator stops responding, the TaskList must show no `in_progress` entries left over from these synthesis steps. (When this skill is invoked inline from a parent skill, the parent skill owns its own TaskList close-out discipline per its own Section prose; this paragraph applies only to the standalone path.)

## Idempotency

This skill reads tickets and writes findings to stdout — it does not mutate any ticket. Re-running `/quo-spec-review <same-spec-bee-id>` against the same spec content produces the same findings (subject to LLM determinism). If the user revises the PRD or SDD between runs, the findings update to reflect the revised content.
