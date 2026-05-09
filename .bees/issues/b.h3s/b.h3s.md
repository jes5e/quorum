---
id: b.h3s
type: bee
title: Recommend gh issue close at end of /quo-fix-issue for github-issue resolver
parent: null
reference_materials: null
created_at: '2026-05-08T22:53:08.904680'
status: done
schema_version: '0.1'
guid: h3s3hv5hkb61hnafroz2qn8uyajbmnc5
---

## Description
At the end of `/quo-fix-issue`, emit copy-paste-ready `gh issue close ...` lines for each fixed Issue whose `reference_materials` carries a `github-issue` resolver, so the user can close the upstream GitHub Issue. Pure recommendation — the skill never runs `gh issue close` itself.

## Current behavior
`/quo-fix-issue` Section 6's close-out flips the bees ticket `open → done` and creates the per-issue commit. Section 7 runs the post-completion review and exits. There is no upstream-close step. A user who runs `/quo-fix-issue <gh-url>` (or `/quo-fix-issue` against bees Issue IDs whose `reference_materials` points at GitHub) gets the bug fixed, the bees ticket marked `done`, the commit landed — but the upstream GitHub Issue stays `open` and has to be closed manually with no prompt or syntax reminder.

## Expected behavior
At the very end of `/quo-fix-issue`'s run (after Section 7's post-completion review either reports clean or finishes follow-ups, before the orchestrator yields the turn), emit a recommendation block:

```
Upstream GitHub Issues to consider closing:

- gh issue close <n1> --repo <owner1>/<repo1> -c "Fixed in <commit-sha-1>."
- gh issue close <n2> --repo <owner2>/<repo2> -c "Fixed in <commit-sha-2>."
```

One bullet per fixed Issue whose `reference_materials[*].resolver == "github-issue"`. Suppress the entire block on runs where zero fixed Issues carry a `github-issue` resolver (keeps the trace clean for users who never use the URL path).

## Impact
- **Closes the URL-mode loop.** `/quo-fix-issue <url>` filed and fixed the bug; without the recommendation, the upstream ticket stays open in a different state from the bees ticket, leading to silent lag and forgotten cleanups.
- **Reduces friction for batch runs.** In `all` or list mode, users who fix several `github-issue`-backed Issues in one round get one consolidated block of close commands at the end rather than having to remember each.
- **Portable across users / machines.** The skill emits commands; users with `gh` installed and authenticated copy/run; users without `gh` see the same suggestion and can map it to their own tooling.

## Suggested fix
Add a small prose block at the end of Section 7 in `skills/quo-fix-issue/SKILL.md`. Pseudocode:

```
At end of Section 7 (after the post-completion reviewer either reports clean
or the per-finding follow-ups in step 6 close out):

For each issue ID in the run's fixed-issue list:
  Read its reference_materials (already captured from the Section 2 / Section
  3 dispatch reads — no new query needed).
  For each entry whose resolver == "github-issue":
    Parse `value` into <owner>/<repo>/<issue-number> via the GitHub URL
    pattern (https://github.com/<owner>/<repo>/issues/<n>).
    Capture the per-issue commit SHA from Section 6's commit step.
    Append: `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."`
Suppress the entire recommendation block if no lines were collected.
```

The skill never runs `gh issue close` itself. No `gh` auth assumption baked into the workflow. No shared-state-safety violation (the user takes the action themselves). No new query against bees (`reference_materials` is already in hand).

## Background and rationale
Surfaced during the same `/quo-fix-issue` session that produced `b.6z8` (and the `b.v4g` handoff-prose follow-up) on 2026-05-08. The user invoked `/quo-fix-issue https://github.com/jes5e/quorum/issues/1`. The orchestrator filed the bees Issue (`b.6z8`), fixed the underlying bug, marked `b.6z8` `done`, committed (`a619cd7`), and ran Section 7's post-completion review (clean) — but the upstream GitHub Issue stayed `open`. The user pointed out the gap and asked for a minimal-scope solution: a recommendation, not auto-close.

Why not auto-close? Three reasons surfaced during the design discussion and were ruled out:
- **Shared-state-safety.** Closing an upstream issue is visible to collaborators (`gh issue close` fires notifications) and warrants user confirmation per the system-level "Executing actions with care" guidance. A pure-recommendation block lets the user retain the action without a confirmation gate inside the skill.
- **Resolver-portability.** Full close-out support would need per-resolver logic (`linear-issue` close via Linear's API, generic `url` with no close concept) but the concrete-resolver implementations don't exist yet — intentionally, per `/quo-file-issue` sub-step C's "Concrete-resolver gap (intentional)" note. Adding github-only auto-close now and per-resolver logic later would introduce inconsistent close-out semantics across resolver kinds.
- **Auth assumptions.** `gh` may not be installed or authenticated on every workflow machine. A hard auto-close dependency would break portability across installed projects (per CLAUDE.md design rule 1: skills must work on Rust/Node/Python/Go/Java/unknown stacks). A recommendation prose block sidesteps that — the user runs the command from a machine where they're authenticated.

Why `github-issue` only in v1? `linear-issue` close requires Linear's own CLI/API which isn't bundled with the workflow; generic `url` has no close concept. Adding `linear-issue` (and any other resolver-with-close concept) to the same recommendation block is a separate Issue once the corresponding CLI/API integration is decided.

Why end of Section 7, not end of Section 6? Section 6 is per-issue and runs once per Issue in batch mode (`all` or list mode). Per-issue recommendations would scatter `gh issue close` commands throughout the run trace. End of Section 7 consolidates the recommendation block as the final session output, which matches user expectations from the inspiring session.

## Decisions and rejected alternatives
**Chosen path:** prose-only recommendation block at the end of Section 7 in `skills/quo-fix-issue/SKILL.md`. `github-issue` resolver only in v1. No code helpers, no auto-close, no auth assumptions, no resolver-specific logic.

**Rejected alternative — full resolver-aware automatic close-out, gated on user confirmation.** Tempting because it's "complete" but mixes three orthogonal concerns (close-out hook, per-resolver logic, confirmation gate) into one Issue, requires concrete-resolver implementations that don't exist yet (intentional gap per `/quo-file-issue` sub-step C), and assumes `gh` auth on every machine. Future-proofing without adding scope today is the better trade.

**Rejected alternative — extend to `linear-issue` and `url` resolvers in v1.** Out of scope. `linear-issue` close requires Linear CLI/API integration; generic `url` has no close concept. Adding those later as a follow-up Issue against the same prose block is the right path — keeps v1 small and testable.

**Rejected alternative — emit the recommendation per-issue inside Section 6 instead of once at end of Section 7.** Per-issue makes the run noisy in batch mode (many fixed Issues → many `gh close` commands scattered through the trace). End-of-run consolidates the block as the final session output, matching the user expectations from the inspiring session.

**Rejected alternative — auto-close after explicit user confirmation via `AskUserQuestion` at end of Section 7.** Tempting because it preserves user control while reducing friction. Rejected because (a) it still requires `gh` auth assumption on every workflow machine; (b) it adds an `AskUserQuestion` gate to every batch run, which is friction for users who already know they want to close upstream; (c) a pure recommendation block is a strict superset of the auto-close path (the user can copy/run the command, OR not). Lighter touch wins.
