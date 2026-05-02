---
name: bees-plan-from-specs
description: Read a PRD and SDD from disk and create a Plan Bee with Epics in the Plans hive to describe the work that needs to be done.
argument-hint: "<prd-path> <sdd-path>"
---

# PRD + SDD to Plan

## Input

This skill takes two absolute file paths as input:

1. A **PRD** — a Product Requirements Document describing the user/customer outcome, business goal, scope, and acceptance criteria.
2. An **SDD** — a Software Design Document describing non-negotiable constraints, architectural boundaries, and what must be true about the software.

Both documents are expected to already be finalized on disk. This workflow does not author these documents — it takes them as given and turns them into a plan.

If the caller does not provide both paths, ask in prose for the missing path(s) and let the user reply in their next turn — do not use `AskUserQuestion`, since file paths are free-text answers, not a finite set of choices. Both paths must resolve to existing files before proceeding.

## Workflow

### Setup

**Preconditions** — hard-fail with `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Plans hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `plans`). The Plans hive is a **top-level** hive (not nested under Ideas) with child tiers `t1` (Epic / Epics), `t2` (Task / Tasks), `t3` (Subtask / Subtasks).
- CLAUDE.md contains a `## Documentation Locations` section. Step 1 below reads architecture-doc paths from this section to understand existing design constraints.

Note: bees-plan-from-specs does **not** require CLAUDE.md `## Build Commands`. bees-plan-from-specs creates Plan Bees and Epics — it does not run build/test/lint/format commands. The Build Commands section is a prerequisite for `/bees-execute` and `/bees-fix-issue` when they execute the work, not for planning.

### 1. Read PRD and SDD

- Read both documents in full.
- Extract features, requirements, acceptance criteria, and constraints.
- Look in the repo and read any architectural documents referenced in `CLAUDE.md` under "Documentation Locations" to understand existing design constraints.
- Before decomposition, align on the outcome. If you cannot clearly state what changes for the user or system when the work is complete, stop and surface questions to the user rather than guessing.
  - From the PRD: user or customer outcome, business goal or KPI, scope and constraints.
  - From the SDD: non-negotiable requirements (security, latency, availability), architectural boundaries, external dependencies.

### 2. Create the Plan Bee

Goal: Create one top-level Bee ticket in the Plans hive to track the work.

- Body contains a brief summary of the goal and scope (2-3 sentences max).
- Do **not** dump the PRD or SDD content into the body — they are accessible via the egg.
- There is no `up_deps` to set (this workflow has no Idea Bees).

**Setting the `egg` field:**

The egg value must be a JSON array containing the absolute paths to the PRD and SDD, in that order:

```
["<absolute path to PRD>", "<absolute path to SDD>"]
```

Set the Plan Bee's `egg` to the JSON array above, with both paths resolved to their absolute form. The egg resolver configured by `/bees-setup` validates these paths downstream. If it is not configured, direct the user to run `/bees-setup` first.

Mark the Plan Bee as `drafted` (its children — the Epics — have not been written yet).

### 3. Break Plan Bee down into Epics

#### Every Epic Must Leave the Codebase Green
Every Epic must leave the codebase in a working state with all existing tests passing. This is the non-negotiable constraint for all Epics.

#### One Epic = One Outcome
- An Epic represents a single, coherent, user- or system-visible capability.
- Avoid Epics organized by system layers (e.g., backend, frontend).
- Prefer Epics defined by observable outcomes.
- An Epic may span multiple systems but must have one measurable success condition.

#### Decompose Vertically by Capability
Break Epics into stories that deliver end-to-end behavior.

Avoid technology layer stories:
- Database Epic ❌
- API Epic ❌
- UI Epic ❌
- Documentation Epic ❌
- Testing Epic ❌

Prefer capability slices:
- Epic: User performs action and receives feedback ✅
- Epic: System handles error and retry behavior ✅
- Epic: Metrics and logging are emitted ✅

Each Epic should be independently testable and demo-able.

##### Exception: Technical Refactors

For pure infrastructure or refactor work, strict vertical slicing may not apply. Pure-tech Epics are allowed provided they leave the codebase green (see above).

- **Go vertical as soon as possible.** After foundational Epics, each subsequent Epic should add a demonstrable capability. Bundle infrastructure each slice needs into that slice rather than separating into layer Epics.

**Anti-Patterns to Detect:**
- Epic chain where intermediate states are untestable
- Mixing pervasive refactor with feature work in one Epic

##### Granularity
Make Epics as granular as possible while adhering to the above constraints of one outcome and vertical decomposition.
It's OK to have a lot of Epics as long as:
- logical outcomes and acceptance criteria are still contained in one Epic
- Epics still represent a vertical slice of end-to-end behavior (unless the technical refactor exception applies)
Imagine that we will celebrate the completion of each new Epic with a birthday party! It's ok to have a lot!

##### Acceptance Criteria
Provide clear actionable Acceptance Criteria that the user can use to objectively evaluate success.
Is there some artifact the User can interact with to test the Epic? If so, detail the steps they will take to do so.
If not, explain how the agent itself can demonstrate that the Epic was completed successfully.
The Acceptance Criteria should be a detailed description of what a "sprint demo" of the Epic would entail.

Good examples:
- Server starts on http://localhost:8000
  - Good because it explains how the user can validate
- Agent builds unit tests that validate the API endpoints respond to HTTP requests
  - Good because it explains how the agent will demonstrate success

Bad examples:
- Server is available for use
  - Bad because it does not explain how the user can validate
- API endpoints respond to HTTP requests
  - Bad because the user cannot validate themselves, and does not explain how the agent itself will demonstrate success

#### Present All Epics for User Review
When all Epics are complete, present them to the user for final review.
- Output as markdown: title, description, dependencies for each Epic
- **Use AskUserQuestion tool** to ask: proceed with creation, modify Epics, or cancel
- **Wait for approval.** Allow modifications if requested.

### 4. Create Shell Epics in Plan Bee

#### Creating Epics with the bees CLI

Create T1 type child tickets in the Plan Bee with status `drafted` (their children — Tasks — have not been written yet).

**Do not pass `--egg` when creating Epics.** The bees CLI accepts `--egg` only on top-level Bees, not on child-tier tickets (`bees create-ticket --help`: "Only supported on bee (top-level) tickets"). Trying to set it on an Epic hard-errors. The egg lives on the parent Plan Bee — downstream skills (bees-breakdown-epic, bees-execute, bees-fix-issue) trace Epics back to the PRD/SDD by reading the parent's egg, not the Epic's.

**NOTE**: If the plan is small, there may only be one Epic. You don't need to make multiple.

##### Epic Viability Checklist
[ ] No testing Epic — testing is folded into the Epics where the work is done
[ ] No documentation Epic — documentation is folded into the Epics where the work is done
[ ] Epics that change config, behavior, or deployment include README/customer-facing doc updates in their scope (not deferred to a separate doc Epic)

#### Setup dependencies
- After all Epics are created, analyze and set up blocking relationships.
- Common Dependency Patterns:
  - **Infrastructure blocks features**: Backend API must exist before frontend/features can use it
  - **Foundation blocks UI**: Data models/services block UI components that display them
  - **Data input blocks processing**: Upload/import features block features that process that data
  - **Auth blocks protected features**: Authentication blocks features requiring authorization

For each Epic, ask: "What must be completed before this Epic can be worked on?"

#### Set Status
- Set the Plan Bee to `ready` (it is written and its children — the Epics — are now written)
- Each Epic should already be `drafted` from creation (they are written but their children — Tasks — are not yet written)

### 5. Report

Output markdown summary:
- Plan Bee and Epics created
- Each Epic: ID, title, status, dependencies (if any)
- Dependency relationships created

### 6. Offer Next Steps

After the Plan Bee and its Epics exist, present the user with clear options. Use `AskUserQuestion`.

Note above the options: each downstream skill re-reads the Plan Bee, Epics, and CLAUDE.md from the bees CLI and disk, so prior conversation context is not load-bearing across the boundary. A fresh Claude Code session is the recommended default — it gives `/bees-breakdown-epic` (and later `/bees-execute`) full context budget for per-Task body authoring and review cycles. Same-session continuation is acceptable as an opt-in for small Bees with one or two Epics.

- **In a fresh session, break down all Epics** (Recommended) — run `/bees-breakdown-epic <bee-id>` in a new Claude Code session. The skill walks every `drafted` Epic in the Bee.
- **In a fresh session, break down a specific Epic** — run `/bees-breakdown-epic <epic-id>` in a new session.
- **Continue in this session** — load `bees-breakdown-epic` now and break down each Epic in dependency order. Reasonable only for small Bees with one or two Epics, since each Epic decomposition adds non-trivial context.
- **Review first** — let the user review the plan before proceeding.
- **Done for now** — plan is saved; user will come back later.
