---
id: b.eid
type: bee
title: 'Plan path needs b.q3f''s up-front enumeration: SDD lifecycle/policy sections, spec-review checks, per-Task site lists, execute PM verification'
status: open
created_at: '2026-09-04T03:04:46.237777'
schema_version: '0.1'
reference_materials: null
guid: eidko77f6x63deu7wmqza26pqwnxhbj6
---

## Description

Issue b.q3f gives `/quo-fix-issue` an up-front design pass that enumerates blast radius (every site an invariant touches, with grep evidence), the lifecycle of every new mechanism (create / consume / close-out in every scope and exit path), the policy decisions the change implies, and scope-split recommendations. The **plan path** — `/quo-plan` → `/quo-write-sdd` → `/quo-breakdown-epic` → `/quo-execute` — has no equivalent requirement anywhere, even though the same churn appears there.

## Current behavior

- `/quo-write-sdd`'s `## Codebase exploration findings` covers architecture, affected modules, patterns, data models, fixtures, and configuration; its `## Requirements` are SR-groups. Neither section requires lifecycle enumeration for new mechanisms or a list of implied policy decisions.
- `/quo-spec-review`'s SDD checklist checks codebase grounding and contract-key impacts (item 9) but not lifecycle completeness or implied policy decisions.
- `/quo-breakdown-epic` dispatches research Agents and a PM to author Task/Subtask bodies; the Task body contract does not require a per-Task site list or the lifecycle legs a Task owns.
- `/quo-execute` has no Analyst; the PM checks traceability against the PRD/SDD but has no site list to verify the Engineer's diff against, so reviewers rediscover sites one per round exactly as `/quo-fix-issue` did before b.q3f.
- b.q3f's Suggested fix item 3 says only "Consider the same for `/quo-execute`'s design inputs" and does not mention breakdown or the SDD.

## Evidence

- Plan b.jp2's own fresh-eyes review (2026-09-03) found, as blockers, a missing lifecycle leg (the manifest rewrite the guard's recording needed did not exist on the stop paths) and a broken intermediate state between Epics (installed skills calling a deleted subcommand) — both are lifecycle/scope enumeration gaps of exactly the kind b.q3f's amendment 3 targets, surfaced only because a reviewer happened to look.
- Plan b.55r's execution history shows the same tail churn: post-completion fixes ("overwrite-per-session → overwrite-per-refresh"; "align missing-reading Configure-now branch"), DEFER-encoded extensions, and a follow-up Issue (b.8x3) for a path the design never enumerated.
- Issue b.5ux (from the b.pdq run) is two `/quo-execute` ordering gaps that a lifecycle enumeration of the writer-abort mechanism would have named at design time.

## Expected behavior

The plan path carries the same up-front content as b.q3f, placed at the three existing upstream checkpoints rather than by adding a per-Subtask Analyst dispatch:

1. **`/quo-write-sdd`** — `## Codebase exploration findings` (or a new required subsection) enumerates, for every mechanism the design introduces, its lifecycle legs per scope and exit path; `## Requirements` (or `## Decisions and rejected alternatives`) lists the policy decisions the design implies with the recommended answer, grounded in the actual request/data pipeline (b.q3f Amendment 2). Same vocabulary and shape as b.q3f's Analyst sections so reviewers learn one contract.
2. **`/quo-spec-review`** — SDD checklist items for lifecycle completeness (a new mechanism with a missing leg in any scope is a `blocker`) and for implied policy decisions left implicit (a `suggestion`); `/quo-plan`'s fresh-eyes reviewer prompt names both as in-scope substance checks.
3. **`/quo-breakdown-epic`** — each Task body carries a **site list** (the blast-radius entries and lifecycle legs this Task owns, cited from the SDD) so the Engineer implements against a list and the reviewers verify against it.
4. **`/quo-execute`** — the PM's per-Task traceability verifies the diff against the Task's site list (a site on the list not addressed is a finding; a site not on the list is a finding against breakdown, not a new fix round), mirroring how b.q3f's reviewers verify against the Analyst's list; Engineers return sweep-completeness evidence in execute mode as b.pdq Amendment 2 already requires.

## Impact

Churn in `/quo-execute` runs (the largest quorum workloads) and in plan quality generally. Without this, b.q3f fixes the small path and leaves the big one to rediscovery-by-review.

## Suggested fix

Sequence after b.q3f lands so the vocabulary is copied, not invented twice. Touches `skills/quo-write-sdd/SKILL.md`, `skills/quo-spec-review/SKILL.md`, `skills/quo-plan/SKILL.md` (plan-reviewer prompt), `skills/quo-breakdown-epic/SKILL.md`, `skills/quo-execute/SKILL.md`, `agents/pm.md`, `agents/engineer.md`. Because it spans five skills and two agent contracts, the Analyst should say at the gate whether this is one Issue or should be re-filed as a Plan with two Epics (spec-side: SDD + reviews; execution-side: breakdown + execute PM). Do **not** add a per-Subtask Analyst dispatch: the plan path already has three upstream checkpoints (SDD authoring, spec review, plan review) where this content belongs; a fourth cold dispatch per Subtask would add latency without new information.

## Background and rationale

Raised 2026-09-04 while reviewing whether b.q3f's Analyst improvements have a counterpart on the plan path. Stack-neutral: "mechanism" and "lifecycle" are defined as in b.q3f's clarification amendment (state, config surface, persisted/wire field, background task, exception type, observability attribute, identifier class, gate, retry path; created / read / mutated / torn down / observed / documented across every surface).

