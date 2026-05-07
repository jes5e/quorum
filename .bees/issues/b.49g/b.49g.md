---
id: b.49g
type: bee
title: Wire /bees-spec-review into /bees-plan, /bees-write-prd, /bees-write-sdd as automatic quality gate
parent: null
reference_materials: null
created_at: '2026-05-07T16:22:04.388017'
status: done
schema_version: '0.1'
guid: 49g6zadjoat78b5bnud21m7z7zehf1pi
---

## Description

Wire `/bees-spec-review` into the spec-authoring flow as an automatic
quality gate, completing the b.uxa Suggested fix step 3. Three wire-up
sites: `/bees-plan` (post both-writers, pre-Spec-Bee-promotion), and
`/bees-write-prd` and `/bees-write-sdd` (post-user-approval, pre-status-
promotion in standalone invocation). Today the skill exists and works
standalone, but no orchestrator invokes it automatically — that means
in practice the quality gate only fires when humans remember to type
`/bees-spec-review`, which is half a feature.

## Background and rationale

`/bees-spec-review` shipped under Issue `b.uxa` with skill body and
checklists complete (PRD: 8 categories tied to /bees-write-prd's 12
sections; SDD: 10 categories tied to /bees-write-sdd's 7 sections;
plus 5 cross-document consistency categories). The b.uxa commit
explicitly deferred suggested-fix step 3 ("post-write hook /
/bees-plan integration") to a follow-up Issue, citing a
"ship + observe failure modes first" rationale inherited from the
original b.uxa Issue body.

Stepping back: the "observe failure modes first" rationale made sense
*before* the checklists existed (when we'd be guessing at what to
check). Now that the checklists are authored and grounded in the
fixed-shape PRD/SDD section structure produced by /bees-write-prd
and /bees-write-sdd, waiting to observe production failures before
integrating buys very little. The checklists target structural and
correctness issues (missing sections, vague language, implementation-
detail leakage, generic codebase references, contract-key impact gaps,
cross-doc inconsistency) — these are not failure modes that need
empirical observation to identify; they're failures the checklists
are already designed to catch by construction.

Without the wire-up, `/bees-spec-review` is a standalone tool a human
has to remember to invoke. With the wire-up, every Spec Bee
`drafted → ready` transition gets a quality gate. The reviewer skill
exists precisely to be that gate; running it manually post-hoc misses
the entire point of the four-reviewer-skill parallel
(`/bees-code-review`, `/bees-test-review`, `/bees-doc-review`,
`/bees-spec-review`).

## Suggested fix

Wire `/bees-spec-review` into three sites, each with consistent
loop-back UX, severity-based promotion gating, and a time-budget
short-circuit matching the pattern PM uses with `/bees-code-review`
and `/bees-doc-review`.

### Site 1: `/bees-plan` Step 4c

After both `/bees-write-prd` and `/bees-write-sdd` have returned with
`prd_status=ready` and `sdd_status=ready` (per their inline-invocation
output contracts), and after the defensive status-check passes but
*before* the `bees update-ticket --ids <spec-bee-id> --status ready`
call:

1. Invoke `/bees-spec-review <spec-bee-id>` (no `--doc` flag — both
   children get reviewed plus cross-document consistency pass) via
   the Skill tool.
2. Apply the loop-back UX (see "Loop-back UX" below).
3. On approval (no blockers, or blockers acknowledged by user as
   acceptable), proceed with the Spec Bee promotion call.
4. On revision (user asks to address findings), invoke the relevant
   writer skill(s) — `/bees-write-prd` if the findings are PRD-side,
   `/bees-write-sdd` if SDD-side, both if cross-doc — with the
   findings included in the args payload so the writer can revise
   targeted sections, then re-invoke `/bees-spec-review` for a
   re-check. Apply the time-budget short-circuit (see below) so this
   does not loop indefinitely.

### Site 2: `/bees-write-prd` Step 6

When `/bees-write-prd <spec-bee-id>` is invoked standalone (not
inline from `/bees-plan`), after the user-approval gate in Step 6 but
*before* the `bees update-ticket --status ready` promotion:

1. Invoke `/bees-spec-review <spec-bee-id> --doc PRD` via the Skill
   tool (PRD-only — the SDD child may not exist yet, and standalone
   PRD revision should not block on SDD review).
2. Apply the loop-back UX.
3. On approval, proceed with the PRD `drafted → ready` promotion.
4. On revision, loop back to Step 5's body authoring with findings
   passed through, then re-invoke /bees-spec-review.

The inline-from-/bees-plan path skips this site (Site 1 covers it
end-to-end). Detection: the inline path passes substantive scope via
the Skill-tool `args` payload; the standalone path is invoked from
the user's prompt directly. The skill should be able to tell which
path it is on (it already does this in Step 0's mid-conversation
heuristic) and skip Site 2 review when running inline.

### Site 3: `/bees-write-sdd` Step 7

Symmetric to Site 2 with `--doc SDD`. Same skip-on-inline-path logic.

### Loop-back UX (consistent across all three sites)

`/bees-spec-review` returns a numbered work-item list with severity
tags (`blocker`, `suggestion`, `nit`). The orchestrating skill (or
writer skill) handles findings as follows:

- **No findings** — proceed to status promotion immediately.
- **Only suggestions and/or nits** — surface findings to user via
  `AskUserQuestion` with options:
  - "Proceed (acknowledge findings)" — promote anyway; user
    explicitly accepts.
  - "Revise" — loop back to writer skill(s) with findings; re-review
    after revision.
- **One or more blockers** — surface findings via `AskUserQuestion`
  with options:
  - "Revise" (recommended) — loop back to writer skill(s).
  - "Proceed anyway (override blockers)" — proceed with promotion
    despite blockers; user takes explicit responsibility. The
    orchestrating skill records the override in the report shown to
    the user at end-of-skill so the choice is visible.

### Severity-based promotion gating

`blocker` severity is the primary gate — by default, blockers prevent
the Spec Bee `drafted → ready` (or PRD/SDD child `drafted → ready`)
transition until either addressed or explicitly overridden. The
override path exists because spec quality is not a hard contract
(unlike code correctness) — there are legitimate cases where a
blocker-tagged finding doesn't apply (e.g., greenfield work where
"Generic existing-behavior" gets flagged but is genuinely the right
shape).

`suggestion` and `nit` are informational — they surface but do not
gate. The user can address them or proceed past them.

### Time-budget short-circuit

Mirror the pattern in `agents/pm.md` for `/bees-code-review` and
`/bees-doc-review`: if a single `/bees-spec-review` invocation
returns more than ~10 items OR the review-fix-review loop runs more
than ~3 turns, stop iterating. Triage the returned list down to
blocker-severity items only, ask the writer to address those, then
proceed (with explicit user acknowledgement of the deferred
suggestions/nits in the end-of-skill report).

This prevents the review-fix-review loop from thrashing on subjective
prose-quality nits when the user just wants to plan and move on.

## Acceptance criteria

- `/bees-plan` invokes `/bees-spec-review <spec-bee-id>` after Step
  4b's writer-skill invocations and before Step 4c's Spec Bee
  promotion. Verifiable by running `/bees-plan` end-to-end and
  inspecting the resulting flow.
- `/bees-write-prd <spec-bee-id>` invoked solo runs
  `/bees-spec-review <spec-bee-id> --doc PRD` after Step 6's user
  approval and before the PRD child's `drafted → ready` promotion.
  Verifiable by running `/bees-write-prd` standalone.
- `/bees-write-sdd <spec-bee-id>` invoked solo runs
  `/bees-spec-review <spec-bee-id> --doc SDD` after Step 7's user
  approval and before the SDD child's `drafted → ready` promotion.
  Verifiable by running `/bees-write-sdd` standalone.
- `/bees-write-prd` and `/bees-write-sdd` invoked inline from
  `/bees-plan` skip the per-writer review (Site 1 covers it
  end-to-end); Site 1 fires once after both writers complete.
- The loop-back UX surfaces findings to the user with the documented
  `AskUserQuestion` options on every review pass.
- Blockers gate Spec Bee / PRD child / SDD child `drafted → ready`
  promotion by default; the explicit override path is available and
  records the override in the end-of-skill report.
- The time-budget short-circuit triggers after ~10 items in a single
  pass or ~3 review-fix-review turns; deferred items are listed in
  the end-of-skill report.
- `/bees-spec-review`'s frontmatter description and SKILL.md prose
  are updated to reflect that orchestrator-invoked use is now the
  primary path (not deferred-future); standalone use remains
  supported for ad-hoc revisions outside the orchestrating-skill flow.

## Out of scope

- Changes to `/bees-spec-review`'s checklists themselves. The current
  checklists are well-targeted and can be calibrated post-deployment
  if real failure modes emerge that they don't catch (or if they
  generate false-positive noise). This Issue is purely about wiring
  the existing reviewer in, not refining what it checks.
- A `## Spec review guide` doc-key in CLAUDE.md `## Documentation
  Locations` (parallel to the Test review guide and Doc writing
  guide entries). Tracked separately if/when warranted; checklists
  live inline in `/bees-spec-review`'s SKILL.md for now.
- Auto-fix or auto-revise behavior — the writer skills + their
  user-approval gates remain the only path that mutates PRD/SDD
  bodies. `/bees-spec-review` continues to return findings only.

## Dependencies

None. `b.uxa` (the original `/bees-spec-review` skill) is `done`,
and the wire-up is purely additive — it adds new Skill-tool calls
inside the orchestrating skills without changing their existing
behavior on the no-findings path.
