---
id: b.fpm
type: bee
title: Orchestrator yields after spec-review trailer, skipping AskUserQuestion gate
status: open
created_at: '2026-05-19T21:45:19.408705'
schema_version: '0.1'
reference_materials: null
guid: fpmmqzdmcwfwjwn5mtu1dpagfaecgnxs
---

## Description

`/quo-spec-review`'s trailer prescribes a follow-up `AskUserQuestion` (Shape 1 / Shape 2) or a `bees update-ticket --status ready` (Shape 3) as the orchestrator's next tool call. The three consuming skills — `/quo-plan` Step 4c, `/quo-write-prd` Step 6a, `/quo-write-sdd` Step 7a — defer to the trailer ("follow the trailer literally") but the orchestrator routinely emits the trailer text and yields the turn without firing the prescribed tool call. The user has to nudge the workflow back into motion before the gate fires.

## Current behavior

After the consuming skill invokes `/quo-spec-review` via the Skill tool:

1. The skill returns its work-item list followed by a trailer line like `**Next action for the orchestrator:** findings present with no blockers — gate the user via AskUserQuestion with finite choices (Proceed (acknowledge findings) / Revise) before promoting. Do not yield without doing this.`
2. The orchestrator emits that text and yields the turn — no `AskUserQuestion` call.
3. The user sends an arbitrary nudge (in the observed run, just the prompt `huh?`).
4. On the next turn the orchestrator re-engages: explains the workflow, walks through findings, and finally fires `AskUserQuestion` with the prescribed choices.

The recovery on the second turn works fully — Proceed/Revise gate fires, the loop-back UX is honored. The bug is purely the premature yield on the first turn.

## Expected behavior

After `/quo-spec-review` returns, the orchestrator's next tool use is immediate and matches the trailer prescription:

- Shape 1 (one or more `[blocker]` items) — call `AskUserQuestion` with `Revise` (recommended) / `Proceed anyway (override blockers)`.
- Shape 2 (only `[suggestion]` / `[nit]` items) — call `AskUserQuestion` with `Proceed (acknowledge findings)` / `Revise`.
- Shape 3 (no findings) — call `bees update-ticket --status ready` against the Spec Bee (or scoped Doc child).

No text-only assistant turn between the Skill return and that tool call.

## Impact

- Visible failure surface at four entry points:
  - `/quo-plan` Step 4c (verified — this is the reported failure site).
  - `/quo-write-prd` Step 6a (solo path; skipped when called inline from `/quo-plan`).
  - `/quo-write-sdd` Step 7a (solo path; skipped when called inline from `/quo-plan`).
  - Standalone `/quo-spec-review <id>` invocation (per `skills/quo-spec-review/SKILL.md:242`, the trailer addresses the assistant turn presenting findings to the user).
- The same third-person trailer architecture exists in `/quo-engineer-review`, `/quo-test-writer-review`, and `/quo-doc-writer-review` (see `## Affected sites` below). Their trailers prescribe agent re-dispatch rather than `AskUserQuestion`; a premature yield there is also a bug but is less visible (no missing user prompt to make it obvious).
- User-facing: every run that surfaces spec-review findings (the common case for Shape 1 / Shape 2 outputs) makes the user feel the workflow is broken and requires a manual nudge to continue. The recovery path looks workflow-consistent, so the user can't tell the workflow is wedged vs intentionally yielding.

## Suggested fix

Two complementary edits (A + B). Extend Edit A to the engineer/test/doc-review skills as Edit C if you want architectural consistency; that decision is left to the engineer.

**Edit A — Imperative second-person trailer phrasing in `/quo-spec-review`.** Rewrite the three trailer shapes at `skills/quo-spec-review/SKILL.md:217` (Shape 1), `:229` (Shape 2), and `:239` (Shape 3) from third-person prescription ("**Next action for the orchestrator:** ... gate the user via AskUserQuestion ... Do not yield without doing this.") to second-person imperative. Example for Shape 2:

- After: `**Your next tool call MUST be AskUserQuestion** with finite choices `Proceed (acknowledge findings)` / `Revise`. Do not produce a text response describing this gate — call the tool directly. The Spec Bee's drafted → ready promotion is gated on the user's answer.`

The "do not produce a text response describing this gate — call the tool directly" clause is the specific counter-anchor to the narrate-instead-of-do failure mode.

**Edit B — Pre-commitment line at each consumer call site.** Add one sentence to `/quo-plan` Step 4c immediately before invoking `/quo-spec-review`, and corresponding lines in `/quo-write-prd` 6a and `/quo-write-sdd` 7a:

> When the Skill call returns, your next tool use MUST be either `AskUserQuestion` (findings present) or `bees update-ticket --status ready` (no findings). A text-only response between the Skill return and that tool use is a defect.

Setting up the obligation *before* the Skill call (rather than relying on the trailer to deliver it at end-of-response, when attentional drift is strongest) is the structural counter-measure.

**Optional Edit C — Extend Edit A to the other three review skills** (`skills/quo-engineer-review/SKILL.md:164`, `skills/quo-test-writer-review/SKILL.md:167`, `skills/quo-doc-writer-review/SKILL.md:125`) for architectural consistency. Their trailers prescribe agent re-dispatch rather than `AskUserQuestion`, but the third-person framing carries the same yield risk and the same fix shape applies. The user's report did not cite a failure at these sites, but the failure mode is structurally identical and worth pre-empting in the same pass.

Key files in scope:

- `skills/quo-spec-review/SKILL.md` (trailer phrasings — Edit A)
- `skills/quo-plan/SKILL.md` Step 4c (pre-commitment — Edit B)
- `skills/quo-write-prd/SKILL.md` Step 6a (pre-commitment — Edit B)
- `skills/quo-write-sdd/SKILL.md` Step 7a (pre-commitment — Edit B)
- `skills/quo-engineer-review/SKILL.md`, `skills/quo-test-writer-review/SKILL.md`, `skills/quo-doc-writer-review/SKILL.md` (optional Edit C)

## Affected sites

User-visible `AskUserQuestion`-gate failures:

- `skills/quo-plan/SKILL.md` Step 4c (lines ~228–298) — the verified report site.
- `skills/quo-write-prd/SKILL.md` Step 6a (lines ~246–272) — solo path only; skipped on inline-from-`/quo-plan`.
- `skills/quo-write-sdd/SKILL.md` Step 7a (lines ~266–292) — solo path only; skipped on inline-from-`/quo-plan`.
- Standalone `/quo-spec-review <id>` invocation — `skills/quo-spec-review/SKILL.md:242` calls out that the trailer addresses "the assistant turn presenting the findings to the user" with the user as the human in the gate prompt.

Same-architecture, lower-visibility risk (optional Edit C scope):

- `skills/quo-engineer-review/SKILL.md:164` — third-person trailer prescribing agent re-dispatch.
- `skills/quo-test-writer-review/SKILL.md:167` — same.
- `skills/quo-doc-writer-review/SKILL.md:125` — same.

## Background and rationale

Three reinforcing factors produce the premature yield:

1. **Third-person framing.** The trailer at `skills/quo-spec-review/SKILL.md:217` (Shape 1) and `:229` (Shape 2) reads `**Next action for the orchestrator:** ... gate the user via AskUserQuestion ... Do not yield without doing this.` — written *about* an "orchestrator" rather than *to* the model. When the model emits this text as its own response, it parses as documentation of what some other entity should do, not as an imperative to itself. The model narrates the action instead of performing it.

2. **End-of-response attentional drift.** The trailer is the last line of a long output (the work-item list). The model has already done the substantive work — running the review checklists — by the time the trailer renders; the "yield" pull is strongest at end-of-response. "Do not yield without doing this" is the trailer's last sentence but the trailer is itself the last thing — nothing further reinforces the obligation before the model decides to yield.

3. **No pre-commitment at the call site.** The three orchestrator skills that consume `/quo-spec-review`'s trailer (`skills/quo-plan/SKILL.md:248`, `skills/quo-write-prd/SKILL.md:259`, `skills/quo-write-sdd/SKILL.md:279`) all carry identical prose: "Follow the trailer literally. The trailer is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory." None of them tell the orchestrator *before* the Skill call that an `AskUserQuestion` is required after the call returns. The gating obligation is learned only from the trailer itself, in the worst possible position.

The mitigations that already exist in the codebase — repeated "Do not yield without doing this" phrasing, the Loop-back UX quick-reference tables, the explicit "follow the trailer literally" direction at the consumers — didn't bite. The fix shape under "Suggested fix" addresses each of the three factors directly (Edit A → factor 1, Edit B → factor 3, both → factor 2 by shifting the obligation away from the end-of-response position).

Root causes ruled out:

- **Not a `/quo-spec-review` content issue.** The skill's review output is correct — three valid `[suggestion]` items, no blockers — and the trailer phrasing matches the documented Shape 2 template. The bug is not in what is being said, but in how the model treats what it has just said.
- **Not a permission / harness issue.** No tool was blocked. The model could have called `AskUserQuestion` immediately; it chose to yield.
- **Not a /quo-plan-specific issue.** The same trailer architecture exists in `/quo-engineer-review`, `/quo-test-writer-review`, and `/quo-doc-writer-review`. The fact that the visible failure surfaces at `/quo-spec-review`'s callers reflects the higher visibility of a missing user prompt vs a missing agent dispatch, not a `/quo-plan`-specific code path.

## Decisions and rejected alternatives

The user weighed three options before filing this ticket:

- **File issue via `/quo-file-issue`** — chosen. Track the bug through the standard quorum workflow so analyst-engineer-reviewer review the fix.
- **Fix directly now** — rejected. The user preferred to capture the diagnosis as an Issue and let the standard fix workflow run rather than skip review.
- **Diagnose deeper first** — partially done (this Issue body carries the deeper diagnosis), then user picked file-issue.

The user did NOT explicitly pick between fix scopes A+B (spec-review only) vs A+B+C (extend to all four review skills). Both shapes are documented in "Suggested fix" with the trade-off named (visibility vs architectural consistency). The engineer working this ticket should pick the scope they think is right and surface the choice in their Design Proposal — A+B alone fully closes the reported failure surface; adding C is a structural pre-emption of the same failure mode at three lower-visibility sites.

