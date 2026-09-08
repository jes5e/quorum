---
id: b.eid
type: bee
title: 'Plan path needs b.q3f''s up-front enumeration: SDD lifecycle/policy sections, spec-review checks, per-Task site lists, execute PM verification'
parent: null
reference_materials: null
created_at: '2026-09-04T03:04:46.237777'
status: open
schema_version: '0.1'
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

## Deferred from /quo-fix-issue run (2026-09-08 04:30)

**From b.q3f (landed): the execute-mode consumer seams b.q3f left inert, and one new receiver gap.** b.q3f landed the producer (`agents/analyst.md` `### Blast radius`, with a lifecycle axis whose paragraph is the single canonical home of the "mechanism" definition — reference it, do not restate it) and the fix-mode consumers. It deliberately did **not** touch `/quo-execute` or `/quo-breakdown-epic`, because nothing on the plan path produces an enumerated site list yet. Three things for this Issue to pick up, beyond its own Expected behavior:

1. **Execute-mode relay sites are already shaped for the list.** b.q3f phrased `/quo-engineer-review` check #8 mode-agnostically ("an upstream enumerated site list, relayed under a labelled heading such as `## Blast radius`") and made `agents/code-reviewer.md` / `agents/pm.md` forward any `## Blast radius` block verbatim into the review (forwarding no heading when none was supplied). So when `/quo-breakdown-epic` starts writing a per-Task site list into Task bodies, the execute-mode wiring is only two relay sentences: the per-Task PM dispatch and the Bee-level Code Reviewer / `pm-<bee-id>` dispatch in `skills/quo-execute/SKILL.md` embed the Task's site list under the same `## Blast radius` heading (one heading string at every hop; relay it even when it is explicitly empty so "swept and found nothing" stays distinguishable from "not supplied"). `agents/engineer.md` already reconciles its completeness evidence against any `## Blast radius` block it is handed, on every dispatch shape, so the Engineer side needs nothing.
2. **Execute mode needs a receiver for the Engineer's `## Design question` return.** b.q3f's `agents/engineer.md` rule is mode-independent: when an assignment needs a mechanism the approved design (or Task body) did not enumerate, the Engineer implements the rest, stops, returns the question under `## Design question`, and in execute mode leaves the Subtask at `in_progress` (does not run `status=done`). `/quo-fix-issue` has two receivers: Section 4 routes a forward-path return into Section 3 as a Revise (re-dispatch the Analyst; the active Analyst task is the carrier; no gate fires inside Phase A), and Section 8's post-completion pass, which has no Analyst, routes an `engineer-postcomp-<n>` return to its **File as issue tickets** branch (the follow-up Issue carries the finding, the question verbatim, and the what-landed / what-did-not list). `/quo-execute` has no receiver: its Reconcile step persists every Engineer return as a completion by confirming the `status=done` transition, so today the only tell is a Subtask that stays `in_progress`. **Section 8's filing shape is the template to copy for execute mode**, per the b.q3f SDD entry: `/quo-execute` likewise has no Analyst, so a proposal to revise is not available to it either, and filing the question as a follow-up Issue is the routing that presupposes neither an Analyst nor a per-Subtask dispatch — consistent with this Issue's own "do not add a per-Subtask Analyst dispatch" rule. Design that receiver alongside the site list so both land with one vocabulary; the execute-mode post-completion pass needs the same leg.
3. **The `## Blast radius` empty form and the lane rule travel with the list.** The fixed empty line `No invariant added, removed, or weakened.` is emitted only when the change adds, removes, and weakens no invariant **and introduces no mechanism**; check #8 treats an explicitly-empty list as supplied (nothing to verify) rather than missing. Entries in the tests / customer docs / internal docs kind-groups are dispositioned to the writer lanes and are never a finding against the Engineer, with the lane resolved by the consuming lane's own scope definition rather than the upstream label. Any per-Task site list should use the same kind-group vocabulary so the same rules apply unchanged.

Related follow-up filed from the same run: **b.ag8** — relaying `### Policy decisions this change implies` to the two `/quo-engineer-review` callers, and relaying `## Blast radius` / policy decisions to the Phase B writers and their review skills (`/quo-test-writer-review`, `/quo-doc-writer-review`) — fix-mode gaps b.q3f's reviewers surfaced; if this Issue lands a per-Task site list, the writer-lane relay should be designed once for both modes.

