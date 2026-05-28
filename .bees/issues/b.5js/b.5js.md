---
id: b.5js
type: bee
title: Replace deferral-hygiene Encode follow-up commit shell snippets with bundled Python helper
parent: null
reference_materials: null
created_at: '2026-05-28T19:41:53.553588'
status: done
schema_version: '0.1'
guid: 5jsn5dkq3i1f4fn6h1vwgtt9ebn1ibd3
---

## Description

The deferral-hygiene gates shipped in b.dgq (commit 63f75cc) added "Follow-up commit" sub-paragraphs inside the Encode-in-an-existing-ticket-body branch of three phase skills: `/quo-execute` Section 6.5, `/quo-fix-issue` Section 7.5, and `/quo-breakdown-epic` Section 6.5. Each ships paired POSIX + PowerShell shell snippets describing a multi-step git workflow (hive-path resolution via `bees list-hives`, in-repo scoping, conditional commit on `git diff --cached --quiet`, subject `Encode deferral: /<skill> — <N> ticket(s) updated`).

The snippets use compound shell shapes (`for ... do ... done`, `case ... in`, `$(...)`, `$VAR`, multi-line) that CLAUDE.md `## Bash etiquette in this repo` forbids when invoked as a single literal Bash tool call. Commit cb30bc5 added a clarifying note above each block ("This is prose program text describing the orchestrator's intent; decompose into individual Bash tool calls when actually running it"). The note shifts the failure mode from "compound call rejected by the harness" to "orchestrator correctly decomposes a multi-step illustrative snippet at runtime". Recoverable but adds turn-cost and re-prompt churn.

## Current behavior

Three skill files carry near-identical Follow-up commit prose snippets:

- `skills/quo-execute/SKILL.md` ~lines 540-575
- `skills/quo-fix-issue/SKILL.md` ~lines 555-590
- `skills/quo-breakdown-epic/SKILL.md` ~lines 615-650

Each block is ~30 lines of paired POSIX bash + Windows PowerShell describing the same workflow. Drift between the three is currently prevented only by the prose-only design discipline of keeping them in sync.

## Expected behavior

A single bundled Python helper (e.g. `skills/quo-execute/scripts/encode_deferral_commit.py`, sibling-resolved by the other two skills via `..` traversal — matching the `scoped_marker_resolver.py` precedent shared between `quo-breakdown-epic` and `quo-execute` / `quo-fix-issue`) encapsulates the multi-step git workflow. The three skill prose blocks shrink to a single Bash call invoking the helper with a `--skill <name> --count <N>` argument pair plus a one-line description.

The helper:

- Resolves hive paths via `bees list-hives` (in-process, no shell `$(...)` needed)
- Walks each in-repo hive and stages it via `git add`
- Additionally stages CLAUDE.md-resolved PRD/SDD paths if the Encode branch routed there
- Checks `git diff --cached --quiet` exit status programmatically
- Emits the commit with subject `Encode deferral: /<skill> — <N> ticket(s) updated`
- Reports success/skip via exit status + a one-line stdout summary

Matches the existing bundled-helper precedent (`detect_fast_path.py`, `scoped_marker_resolver.py`) — stdlib-only Python 3, cross-platform via `pathlib`, single executable file. Existing quorum users get the helper the same way they get SKILL.md updates (no new install step).

## Impact

- **Drift prevention.** Three near-identical prose blocks across three skills become one helper file.
- **Reduced turn-cost.** Orchestrator invokes a single Bash call instead of decomposing a 15-line snippet into per-step calls.
- **Cleaner prose.** Three skill files lose ~30 lines each of paired POSIX + PowerShell that's effectively a Python implementation expressed as shell.

## Suggested fix

1. Write `skills/<skill-name>/scripts/encode_deferral_commit.py` (pick the skill — likely `/quo-execute` since it owns the largest commit-step precedent, or factor to a shared sibling-resolvable location).
2. Replace each Follow-up commit prose block in the three skills with a single Bash call invoking the helper with `--skill <name> --count <N>`, plus the existing anti-pattern callout ("Do NOT blindly `git add -A`") retained inline.
3. Update the README's "Where docs live" / "Bundled Python helpers" surface to list the new helper alongside `detect_fast_path.py` and `scoped_marker_resolver.py`.
4. Remove the post-completion clarifying notes added by commit cb30bc5 — they become unnecessary when the prose isn't a multi-line illustrative shell snippet.

## Background and rationale

Filed as a follow-up to commit cb30bc5's post-completion fix. An external reviewer framed the Encode-snippet shape as a "prose-only contract just like b.fpm's failed approach" — which overstates the equivalence (b.fpm's failure mode is silent skip + yield, while a compound-Bash-call failure is noisy/visible at the harness layer). But the Python-helper refactor is genuinely durable on its own merits and matches the established bundled-helper precedent. Filed separately from the b.wii self-consistency framing so future readers see the durability argument cleanly.

## Decisions and rejected alternatives

- **Keep the inline snippet + clarifying note (status quo).** Acceptable but inferior — multi-skill drift risk and ~30 lines of prose program text per skill.
- **English prose instead of shell snippet.** Eliminates the misread-as-runnable risk but leaves the per-step orchestration entirely up to the orchestrator's load-state at runtime. The Python helper deterministically encodes the workflow.
- **One helper per skill (no sharing).** Acceptable if the workflows diverge meaningfully — but they don't today; the three blocks are near-identical. Shared helper sibling-resolved matches the `scoped_marker_resolver.py` precedent.
