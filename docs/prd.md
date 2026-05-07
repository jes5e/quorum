# bees-workflow — Product Requirements

## Existing scope

bees-workflow is a portable Claude Code skill set for engineers who want an end-to-end SDLC running on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Distributed as markdown skills plus a small number of Python helpers and installed into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (per-project), the skills are invoked via `/<skill>` slash commands inside Claude Code. The project is open-source under MIT license and is in active maintenance.

## Why

bees-workflow exists as an alternative to [Apiary](https://github.com/gabemahoney/apiary), the original bees skill set. Apiary remains a great fit for many projects; bees-workflow is shaped by a different set of priorities:

- **Cumulative project-level docs.** PRD and SDD live as files in `docs/`, accumulate sections as features are planned, and become the source of truth that agents (`bees-execute`, `bees-fix-issue`) read for spec-drift detection. `/bees-setup` can bootstrap baseline docs from an existing codebase via guided Q&A; subsequent `/bees-plan` invocations extend them rather than overwrite.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md contract keys, then read by skills at runtime — no skill-editing needed when switching projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet in skill prose ships as labeled OS-conditional blocks; the helper scripts that need cross-platform filesystem behavior ship as Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`; spec-hive bees use `drafted` / `ready`. No translation layer or insect-metaphor jargon to remember.
- **Two entry points.** `/bees-plan` is the interactive scope-discovery path — used both for ideas without finalized specs and for new features being added to an already-cumulative PRD/SDD (it appends a new `### Feature:` subsection). `/bees-plan-from-specs` is the express path when a finalized **single-feature** PRD and SDD already exist on disk; it hard-fails on multi-feature cumulative docs to avoid re-planning previously-planned features. Experienced users with finalized cumulative specs can also pass `/bees-plan-from-specs --feature "<title>"` to scope an express re-plan to a single `### Feature:` subsection inside the cumulative docs. Both entry points produce the same Plan Bee shape.
- **Idempotent.** Every state-mutating skill (`bees-setup` especially) detects existing configuration and only prompts where something is missing or the user asks to change it. Re-runs are safe.

## Out of scope

- **tmux-dependent skills in the portable core.** Skills that need terminal session multiplexing (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and live elsewhere as optional later-installs.
- **Stack-specific helpers.** Changelog tooling, license attribution generation, dependency auditing, and similar single-stack utilities are routed to companion repos rather than added to the core.
- **Infrastructure-specific helpers.** Pastebin clients, cloud storage uploaders, and similar platform-coupled features stay out of the core.
- **Replacing Apiary.** bees-workflow lives alongside Apiary, not as a replacement. Users who want Apiary's lightweight, ephemeral-spec, async-team-spawning style should use Apiary.
- **Maintaining a translation layer to legacy bee-themed terminology.** The status rename from `larva` / `pupa` / `worker` / `finished` to `drafted` / `ready` / `in_progress` / `done` is permanent.

## Acceptance criteria (project-level)

- **End-to-end chain works on any supported stack.** On a fresh repo of any supported language (Rust, Node, Python, Go, Java, or unknown), the full chain `/bees-setup` → `/bees-plan` (or `/bees-plan-from-specs`) → `/bees-breakdown-epic` → `/bees-execute` runs to `done` status across all Epics without per-language skill edits.
- **Cumulative-PRD scoping holds end-to-end.** When a Plan Bee is authored via `/bees-plan-from-specs --feature "<title>"` against cumulative PRD/SDD docs, the single-feature scope is enforced through every downstream skill: `/bees-breakdown-epic` decomposes against only the matching `### Feature: <title>` subsection, and the per-Task PM in `/bees-execute` (and the PM role in `/bees-fix-issue` when an Issue derives from a scoped Plan Bee) compares implementation against the scoped subsection only. Other features in the same cumulative docs do not surface as spec drift.

## Per-feature scope

### Feature: Test strategy for the skills repo

**Status: paused as of 2026-05-03.** This feature remains paused; the Ephemeral-Agent Orchestration rewrite (Plan Bee `b.5tm`) shipping on `main` does not auto-unpause it. `b.gar`'s Plan Bee body has now been refreshed to reflect the post-orchestration, bees-only architecture (the "Optional beads backend" feature `b.9xr` and its `ticket_backend.py` dispatcher seam were abandoned, not gating Test strategy any longer), and Layer 2.5 — the backend-equivalence harness — is explicitly deferred there. The acceptance criteria below still describe the originally-planned dual-backend test strategy and will be re-scoped against the refreshed `b.gar` body when this feature resumes.

**What.** Add a layered test strategy for the bees-workflow repo itself. Three layers — Layer 1 (pytest unit tests on every bundled Python helper), Layer 2 (a structural linter validating each `SKILL.md` against the project's design rules), and Layer 2.5 (a backend-equivalence harness running the same dispatcher operations through both bees and beads and asserting equivalent state). All three layers wire to a single `make test` entrypoint. Layer 3 (live Claude Code end-to-end smoke) is explicitly out of scope.

**Why.** Today the only automated check is `python -m pyflakes` on helper scripts. Recent work (b.aic, b.ekz, b.c4z, b.veq) shows real regressions slipping in — design-rule drift in skill prose, helper bugs, contract changes nobody catches until a downstream skill fails. The dual-backend work in the previous feature substantially raises the cost of an undetected regression: divergence between the bees and beads adapter paths in `ticket_backend.py` would only surface end-to-end, far from the change site. A layered strategy is the cheapest way to catch the failure modes that actually bite (helper bugs, design-rule drift, backend divergence) without trying to fully test prose-driven LLM workflows.

**Acceptance criteria.**

- `pytest skills/` passes from a clean clone, exercising every bundled Python helper (5+ at execution time).
- A linter walks all 11 `SKILL.md` files and asserts the project's design rules; exits 0 on the current repo, 1 on a deliberate violation.
- A backend-equivalence harness runs the dispatcher's seven verbs through both bees and beads and asserts equivalent normalized state; skips cleanly if either backend CLI is unavailable.
- A top-level `make test` target runs all three layers and exits non-zero on any failure. A `tools/run_tests.py` fallback covers Windows users without `make`.
- CLAUDE.md gains a `## Test Commands` section (contributor-facing) documenting the entrypoints.
- README's Contributing section gains a short paragraph naming the three layers and pointing at the entrypoint.
- CI runs `make test` on every push and PR.

**Sequencing.** This feature blocks on the "Optional beads backend" feature (Plan Bee `b.9xr`) reaching `done`. Layer 2.5 needs the dispatcher to exist; Layer 1's pytest coverage of `ticket_backend.py` needs the file in place; Layer 2's linter needs to know about backend-conditional blocks.

**Out of scope.**

- Layer 3 — live Claude Code end-to-end smoke harness. May ship later as a separate Plan Bee.
- Testing LLM-generated content (PRD-bootstrap exploration, code-review judgment).
- Testing `AskUserQuestion` interactive flows directly.
- Snapshot testing of full skill output.
- Migration of existing skill patterns beyond what's needed for the new layers.
- A proxy / mock test harness — the equivalence harness uses real CLIs against temp directories.
