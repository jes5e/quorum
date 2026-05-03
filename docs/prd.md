# bees-workflow — Product Requirements

## Existing scope

bees-workflow is a portable Claude Code skill set for engineers who want an end-to-end SDLC running on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Distributed as markdown skills plus a small number of Python helpers and installed into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (per-project), the skills are invoked via `/<skill>` slash commands inside Claude Code. The project is open-source under MIT license and is in active maintenance.

## Why

bees-workflow exists as an alternative to [Apiary](https://github.com/gabemahoney/apiary), the original bees skill set. Apiary remains a great fit for many projects; bees-workflow is shaped by a different set of priorities:

- **Cumulative project-level docs.** PRD and SDD live as files in `docs/`, accumulate sections as features are planned, and become the source of truth that agents (`bees-execute`, `bees-fix-issue`) read for spec-drift detection. `/bees-setup` can bootstrap baseline docs from an existing codebase via guided Q&A; subsequent `/bees-plan` invocations extend them rather than overwrite.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md contract keys, then read by skills at runtime — no skill-editing needed when switching projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet in skill prose ships as labeled OS-conditional blocks; the helper scripts that need cross-platform filesystem behavior ship as Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`. No translation layer or insect-metaphor jargon to remember.
- **Two entry points.** `/bees-plan` is the interactive scope-discovery path for an idea without finalized specs; `/bees-plan-from-specs` is the express path when a PRD and SDD already exist on disk. Both produce the same Plan Bee shape.
- **Idempotent.** Every state-mutating skill (`bees-setup` especially) detects existing configuration and only prompts where something is missing or the user asks to change it. Re-runs are safe.

## Out of scope

- **tmux-dependent skills in the portable core.** Skills that need terminal session multiplexing (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and live elsewhere as optional later-installs.
- **Stack-specific helpers.** Changelog tooling, license attribution generation, dependency auditing, and similar single-stack utilities are routed to companion repos rather than added to the core.
- **Infrastructure-specific helpers.** Pastebin clients, cloud storage uploaders, and similar platform-coupled features stay out of the core.
- **Replacing Apiary.** bees-workflow lives alongside Apiary, not as a replacement. Users who want Apiary's lightweight, ephemeral-spec, async-team-spawning style should use Apiary.
- **Maintaining a translation layer to legacy bee-themed terminology.** The status rename from `larva` / `pupa` / `worker` / `finished` to `drafted` / `ready` / `in_progress` / `done` is permanent.

## Acceptance criteria (project-level)

- **End-to-end chain works on any supported stack.** On a fresh repo of any supported language (Rust, Node, Python, Go, Java, or unknown), the full chain `/bees-setup` → `/bees-plan` (or `/bees-plan-from-specs`) → `/bees-breakdown-epic` → `/bees-execute` runs to `done` status across all Epics without per-language skill edits.

## Per-feature scope

### Feature: Test strategy for the skills repo

**Status: paused as of 2026-05-03.** This feature was sequenced after the "Optional beads backend" feature (Plan Bee `b.9xr`), which is itself paused — see `b.9xr`'s Plan Bee body for context. `b.gar`'s Plan Bee body is updated at the conclusion of the Ephemeral-Agent Orchestration feature (currently in active planning) to reflect the new bees-only, post-orchestration architecture before this feature resumes. The acceptance criteria below describe the originally-planned dual-backend test strategy and may be re-scoped on resume.

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

### Feature: Ephemeral-Agent Orchestration

**What.** Replace the experimental Agent Teams orchestration substrate used by `bees-execute`, `bees-fix-issue`, and `bees-breakdown-epic` with ephemeral background invocations of Claude Code's stable `Agent` tool. Each role (engineer, test-writer, doc-writer, pm, code-reviewer, doc-reviewer, test-reviewer) becomes a custom subagent type defined as a markdown file in a top-level `subagents/` directory of this repo, installed alongside skills (and packageable as a future plugin). The team-lead in each execution skill becomes a reconciliation-loop orchestrator that dispatches Agents on demand, reads return values on completion, and tracks state via bees tickets + Claude Code's TaskList. Per-Task warm-Agent reuse via named Agents + SendMessage preserves cold-start efficiency for Engineer and Test Writer roles; reviewers always run cold for fresh-eyes review. TaskList replaces Agent Teams' display backend as the visual progress UI. The `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` env var, the `teammateMode` display backend setup, the iTerm2-prompt workaround prose, and the `force_clean_team.py` / `check_agent_teams.py` helper scripts are removed entirely. The Plan Bee `b.gar` (Test strategy) gets a body update at the end so it can resume coherently against the new architecture.

**Why.** The current architecture has produced four orchestration-failure tickets in three days (b.11f, b.hf8, b.aic, plus a stuck-PM report on 2026-05-02), each layering more rules onto the same long-lived-worker + event-driven-team-lead substrate. The pattern is structural: workers idle silently with no completion signal, the team-lead has no clock to fire wall-clock nudge ladders, state lives in three places (bees, TaskList, message history) that drift, and lifecycle ceremony around team creation/teardown introduces its own failure modes. Each prior fix added a rule the model can drop under load. Switching to ephemeral background subagents eliminates the architectural mismatch at the substrate level: Agents either return or are still running, the harness wakes the team-lead on every completion, state has a single source of truth (bees), and there is no lifecycle to babysit. The substrate also moves from experimental to stable. End-user experience is preserved at the high-level UX — every feature a user notices today (interactive entry, model choice, isolation handling, per-Task commits, in-flight reviews, cross-Task interaction checks, final fresh-eyes review, spec traceability) is preserved — but the failure modes that produced repeated babysitting tickets stop occurring at the architectural level rather than at the rule-layer level.

**Acceptance criteria.**

- All three execution skills (`bees-execute`, `bees-fix-issue`, `bees-breakdown-epic`) run without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. No Agent Teams setup is required and no skill fails for lack of it.
- A multi-Epic Bee (4+ Epics, 12+ Tasks, 60+ Subtasks) completes end-to-end unattended without a stuck-silence stall — no graduated escalation ladder firing, no user prods required.
- Concurrent specialist work is preserved: multiple Engineer Agents on different subtasks run in parallel; Engineer + Test Writer + Doc Writer can run side-by-side. Verified by overlapping Agent invocation lifecycles in the TaskList UI.
- All current user-visible features survive at the high-level UX: model choice for support roles (Doc Writer / PM / Doc Reviewer), worktree-vs-branch isolation prompt, scope confirmation, one-commit-per-Task / one-commit-per-issue, in-flight reviews with iteration loops and time-budget short-circuiting, cross-Task and cross-Epic interaction checks, final post-Bee fresh-eyes review, spec-traceability verification in `bees-breakdown-epic`, per-Task summary report including ignored review feedback.
- `bees-setup` no longer prompts about Agent Teams or `teammateMode`. The skill still bootstraps hives, CLAUDE.md sections, and optional PRD/SDD; the Agent Teams + display backend prompts are gone.
- `force_clean_team.py` and `check_agent_teams.py` are deleted; all references in skill prose are removed.
- `README.md` removes the "Required: enable Agent Teams" section and the "Display backend" section. A single sentence near the workflow diagram replaces them with: "The skills orchestrate work via Claude Code's ephemeral background subagents — no special setup is required beyond the bees CLI and Claude Code itself."
- A new top-level `subagents/` directory ships seven role-definition files (engineer.md, test-writer.md, doc-writer.md, pm.md, code-reviewer.md, doc-reviewer.md, test-reviewer.md). README install instructions cover both manual copy (current pattern) and the future plugin-packaging shape.
- `b.gar`'s body is updated at the end of this work to reflect the new architecture so it can resume coherently.
- All three CLAUDE.md design rules still hold: language-agnostic, POSIX + Windows PowerShell, project-neutral.
- Skills still talk to bees via the existing `bees ...` CLI commands. No `ticket_backend.py` dispatcher seam (that work was on the abandoned beads branch).

**Out of scope.**

- The beads backend. Deferred; this rewrite is bees-only and targets the existing `bees ...` CLI patterns directly. The "Optional beads backend" Plan Bee (`b.9xr`) holds the recovered spec for revival; see its body.
- The dispatcher seam (`ticket_backend.py`). Removed by abandoning the bee/b.9xr branch; not coming back here.
- Executing `b.gar`'s test strategy. Only its body gets a content update; the actual test-strategy work happens later under `b.gar` itself.
- New skills. The 11 portable-core skills stay 11.
- Performance tuning beyond the cold-start hybrid model. No prompt-caching engineering, no MCP integration, no token-budget instrumentation.
- Optional skills. `bees-fleet`, `bees-worktree-add`, `bees-worktree-rm` stay outside the portable core.
- Changes to bees ticket schema. Status vocabulary, hive layout, dependency model unchanged.
- Cron / `/loop` / scheduled-wake mechanisms. The reconciliation loop wakes on Agent completion notifications + user input; no clock primitives are needed.
- Recursive delegation beyond a probe. If the harness allows it we use it as an optimization in one well-defined spot; otherwise we proceed flat. We do not redesign around it.
- Modifications to the three review skills (`bees-code-review`, `bees-doc-review`, `bees-test-review`) beyond ensuring they invoke cleanly from a subagent context. Their prose stays as-is unless a regression demands change.
