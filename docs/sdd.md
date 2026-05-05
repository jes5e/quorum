# bees-workflow — Software Design

## Tech stack

- **Skill prose**: Markdown (`SKILL.md`) with YAML frontmatter (`name`, `description`). The body is the instructions Claude follows when the skill is invoked.
- **Helper scripts**: Python 3 (cross-platform). Three exist today — `bees-setup/scripts/file_list_resolver.py` (egg resolver), `bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection), and `bees-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser/scoper, sibling-resolved by `bees-execute` and `bees-fix-issue`).
- **External CLI**: [bees](https://github.com/gabemahoney/bees) (`bees-md` on pipx, Python 3.10+) for ticket management.
- **Runtime host**: [Claude Code](https://claude.com/claude-code) — skills are invoked via `/<skill>` slash commands. The execution skills (`bees-execute`, `bees-fix-issue`, `bees-breakdown-epic`) orchestrate parallel work by dispatching ephemeral background subagents via the stable `Agent` tool (`run_in_background=true`). Role contracts ship as seven custom-subagent definition files at `agents/<role>.md` in the repo root (`engineer.md`, `test-writer.md`, `doc-writer.md`, `pm.md`, `code-reviewer.md`, `doc-reviewer.md`, `test-reviewer.md`), installed alongside skills at `~/.claude/agents/` (global) or `<repo>/.claude/agents/` (per-project). No experimental feature flags or display-backend configuration are required.

## Architecture overview

The repo ships eleven portable-core skills under `skills/<name>/`, each self-contained as a `SKILL.md` plus optional `scripts/`. Skills are loaded by Claude Code from either `~/.claude/skills/` (global install) or `<repo>/.claude/skills/` (per-project install). When a skill needs a bundled helper script (its own or a sibling's), it resolves the absolute path at runtime from the skill's own base directory — which Claude Code provides in the skill invocation header. No per-machine paths are persisted to CLAUDE.md or any other tracked file.

The workflow chain is linear with two entry points:

- `/bees-setup` — one-time per repo (idempotent re-runs)
- `/bees-plan` *or* `/bees-plan-from-specs` — produces a Plan Bee with Epic children
- `/bees-breakdown-epic` — decomposes one Epic into Tasks/Subtasks, commits the new ticket files at end-of-skill
- `/bees-execute` — walks every Epic, runs the team per Task, commits
- `/bees-file-issue` *and* `/bees-fix-issue` — anytime, for bugs/follow-ups

Three review skills (`bees-code-review`, `bees-doc-review`, `bees-test-review`) are dual-mode — primarily invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, with standalone invocation also supported for ad-hoc reviews outside the workflow.

The workflow uses two hives in the target repo: **Plans** (top-level, with t1/t2/t3 = Epic/Task/Subtask) and **Issues** (no children). Plan Bees may carry one or more on-disk source documents (PRD, SDD, etc.) in their `egg` field, resolved by the bundled `file_list_resolver.py`. When a Plan Bee has a null/empty `egg`, the **Plan Bee body itself becomes the authoritative spec** — downstream skills explicitly substitute the Bee body for the PRD/SDD in that mode.

## Key components

- **`skills/bees-setup/`** — one-time configuration: hives, two required CLAUDE.md sections (`Documentation Locations`, `Build Commands`), optional PRD/SDD bootstrap from existing codebase. Detects the new-machine case (on-disk hive markers present, the repo's scope not registered in `~/.bees/config.json`, CLAUDE.md already populated) via the bundled `detect_fast_path.py` helper and offers a fast path that re-registers hives from canonical defaults without touching CLAUDE.md.
- **`skills/bees-plan/`** — interactive scope discovery for an idea or feature without finalized specs. Produces a Plan Bee with Epic children.
- **`skills/bees-plan-from-specs/`** — express path for a finalized PRD+SDD on disk. Same Plan Bee output as `/bees-plan`. Default (single-feature) mode hard-fails on PRDs/SDDs that contain more than one `### Feature: <title>` subsection (the cumulative-PRD pattern produced by repeated `/bees-plan` invocations) and routes the user back to `/bees-plan` to avoid re-planning previously-planned features. The optional `--feature "<title>"` flag bypasses the multi-feature guard and scopes the planning run to a single `### Feature: <title>` subsection extracted from each of the PRD and SDD (heading must exist in both docs); the egg still points at the canonical full PRD/SDD paths, and the Plan Bee body carries a `Scoped to ...` marker so downstream skills can tell the Bee covers a sub-region of a cumulative spec. **Marker producer.**
- **`skills/bees-breakdown-epic/`** — decompose one Epic into Tasks and Subtasks. The only skill where team members run in `mode: "plan"` (read-only researchers). At end-of-skill, stages and commits the new ticket files (Tasks, Subtasks, Epic status update) when the Plans hive lives inside the current git repo — resolved via `bees list-hives` in the same pattern `bees-file-issue` uses; when the hive lives outside the repo, the commit step is skipped and the next-steps menu carries a one-line note. The end-of-skill next-steps menu carries per-option "best when …" rationales and conditionally surfaces a "execute this Epic first; defer downstream breakdown" Recommended option when the team-lead judges that the just-broken-down Epic's implementation will reshape contracts consumed by drafted sibling Epics (foundation-then-rewrites pattern); when there is no contract reshape risk, the Recommended option is the default keep-going path. **Marker consumer** — Step 1 (read parent Bee) detects the `Scoped to ...` marker and restricts the egg-resolved doc content to the matching `### Feature: <title>` subsection before Task decomposition and Spec Traceability Review. Bundles the shared parser/scoper helper at `scripts/scoped_marker_resolver.py` (sibling-resolved by `bees-execute` and `bees-fix-issue`).
- **`skills/bees-execute/`** — execute a Plan Bee end-to-end. Walks Epics in dependency order, dispatches ephemeral background subagents per Task, commits per Task, reviews at Bee close. **Marker consumer** — Step 4 PM section detects the `Scoped to ...` marker on the Grandparent Bee and compares per-Task work against the scoped subsection only (sibling-resolves `bees-breakdown-epic`'s `scoped_marker_resolver.py`).
- **`skills/bees-fix-issue/`** — fix one or more issue tickets. Single, list, or `all` modes. Same orchestration shape as `bees-execute` but at issue scope. **Marker consumer (via up_dependencies-link)** — Issues live in the `issues` hive and have no canonical parent-Plan-Bee field in the bees ticket schema, so the PM discovers a scope-context Plan Bee opportunistically by iterating the Issue's `up_dependencies` array (a deliberate dual-use of that field — blocker AND optional scope-context source) and applying the marker from any entry that resolves to a Plan Bee. Best-effort: a missing marker, a non-`plans`-hive `up_dependencies` entry, or a parser hard-fail falls back to full-doc spec content; if multiple Plan Bees in `up_dependencies` carry markers, the first in `up_dependencies` iteration order wins.
- **`skills/bees-file-issue/`** — file a new issue ticket (bug, follow-up, small feature, tech debt).
- **`skills/bees-status/`** — show workflow stages and current progress across all hives.
- **`skills/bees-code-review/`**, **`skills/bees-doc-review/`**, **`skills/bees-test-review/`** — dual-mode reviewers. Primary use: invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, with bees-specific loop-bounding prose for that path. Secondary use: standalone ad-hoc review of a diff or worktree.
- **`agents/`** — top-level directory of seven custom-subagent definition files, one per role, installed alongside skills at `~/.claude/agents/` (global) or `<repo>/.claude/agents/` (per-project). Each file carries YAML frontmatter (`name`, `description`, `model`, `tools` allowlist) plus a markdown body capturing role-specific Instructions (what to read, what to do, what to return). The execution skills reference these by `subagent_type: "<role>"` rather than carrying inline role prose, which substantially reduces SKILL.md size and makes role customization a first-class operation.

  | File | Model | Purpose |
  |---|---|---|
  | `agents/engineer.md` | Opus (always) | Implements code changes for a Subtask or set of Subtasks |
  | `agents/test-writer.md` | Opus (always) | Writes/updates tests for completed Engineer work |
  | `agents/doc-writer.md` | User's choice (Opus or Sonnet) | Authors or updates documentation |
  | `agents/pm.md` | User's choice | Per-Task PM review (spec drift, scope creep, in-flight code/doc review invocations) |
  | `agents/code-reviewer.md` | Opus (always) | Wraps `/bees-code-review` skill invocation |
  | `agents/doc-reviewer.md` | User's choice | Wraps `/bees-doc-review` skill invocation |
  | `agents/test-reviewer.md` | Opus (always) | Wraps `/bees-test-review` skill invocation |

- **`skills/bees-setup/scripts/file_list_resolver.py`** — the egg resolver. Registered as each hive's `egg_resolver` so a Bee's `egg` field can point to one or more on-disk docs.
- **`skills/bees-setup/scripts/detect_fast_path.py`** — detect the new-machine fast-path scenario. Emits a JSON status payload (hive markers found, scope-already-registered check, CLAUDE.md sections populated, `fast_path_eligible` boolean) consumed by `/bees-setup`.
- **`skills/bees-breakdown-epic/scripts/scoped_marker_resolver.py`** — shared parser/scoper for the `Scoped to ...` marker emitted by `/bees-plan-from-specs --feature`. Takes one positional argument (path to a file containing the parent Bee body); prints `{"scoped": false}` when no marker is present, prints `{"scoped": true, "title": "...", "docs": [{"path": "...", "content": "..."}, ...]}` when the marker is present and well-formed, and exits 2 with a single human-readable line on stderr otherwise. Resolved as a sibling script by `bees-execute` and `bees-fix-issue`. Grammar and hard-fail rules documented in `docs/doc-writing-guide.md` `## The Scoped-marker contract`.

## Contract keys

The target repo's CLAUDE.md carries two sections that act as a string contract between skills. `bees-setup` writes them; every other skill reads them.

- `## Documentation Locations` — `Project requirements doc (PRD)`, `Internal architecture docs (SDD)`, `Customer-facing docs`, `Engineering best practices`, `Test writing guide`, `Test review guide`, `Doc writing guide`
- `## Build Commands` — `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`

`bees-execute` and `bees-fix-issue` hard-fail with `Run /bees-setup first.` if either section, or any required key inside them, is missing.

Bundled helper script paths (e.g., `scoped_marker_resolver.py`) are *not* part of the CLAUDE.md contract — each skill resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header. This keeps per-machine paths out of tracked files.

## Orchestration in execution skills

`bees-execute`, `bees-fix-issue`, and `bees-breakdown-epic` orchestrate work by dispatching ephemeral background subagents via the stable `Agent` tool (`run_in_background=true`). The main Claude Code session running the skill is the orchestrator — conceptually a team-lead, but mechanically a reconciliation-loop driver, not a chat hub.

- **Reconciliation loop (read state / reconcile / yield).** Each tick is purely event-driven — the harness wakes the orchestrator on Agent completion notifications, user input, and tool results. There is no clock primitive: no `/loop`, no `ScheduleWakeup`, no `CronCreate`, no polling loop. A tick reads ticket state (`bees execute-freeform-query`, `bees show-ticket`), reads the TaskList for active Agent invocations, reconciles the gap (dispatch a fresh Agent for any Subtask whose preconditions are met but no Agent is on it; persist results for any Subtask whose Agent has just returned; trigger PM review for completed Tasks; run inter-Epic checkpoints; spawn the post-Bee fresh-eyes review team when all Epics are done), then yields. This is a Kubernetes-controller shape applied to skill orchestration: declarative state goal (bees ticket statuses), continuous reconciliation against actual state, no hand-managed message queues.
- **Hub-and-spoke as a structural property of the substrate.** Workers do not communicate with each other. All routing is orchestrator → Agent. The artifact-based handoff (Engineer's commits become Test Writer's input; Test Writer's tests become PM's review material) replaces the message-based handoff. This is structurally identical to the prior hub-and-spoke prescription, but achieved through a substrate that doesn't permit peer comms rather than through a "do not message peers" rule the model can drop.
- **Cold dispatch for all roles.** Engineer, Test Writer, and Doc Writer are dispatched fresh per Subtask; PM, Code Reviewer, Doc Reviewer, and Test Reviewer are always fresh by design (fresh-eyes review). Coherence across dependent Subtasks is preserved through the diff: each later Engineer reads the prior Engineer's commit, matching the hub-and-spoke "diff is the handoff" pattern. Concurrent specialist work is preserved: Engineer-Subtask-N+1 runs in parallel with Test-Writer-Subtask-N once the orchestrator's reconciliation loop ticks past Engineer-Subtask-N's completion.
- **State-aware dispatch.** Before dispatching any Agent, the orchestrator re-reads the target ticket's current state via `bees execute-freeform-query` and skips the dispatch when the ticket is already `done`. This prevents redundant work caused by acting on stale memory.
- **Verbatim ticket-body quoting.** Agent dispatch prompts embed the ticket body exactly as `bees show-ticket` returns it — no paraphrasing. Identifier names (function/flag/type names) are preserved literally so workers do not invent or mis-spell them downstream. Framing prose stays outside the quoted block.
- **TaskList as progress UI.** The orchestrator creates one TaskList task per concurrent Agent invocation (e.g., `engineer-qf-subtask-1`, `test-writer-qf-subtask-1`, `pm-qf-subtask-1-review`). Status transitions (`pending → in_progress → completed`) are updated as Agents start and finish; `metadata.activity` carries finer-grained progress (e.g., `"running /bees-code-review (~5 min)"`). Claude Code's native TaskList UI renders these live, providing visual parallelism without an Agent Teams display backend.
- **Time-bounded review iteration.** In `bees-execute`, the PM short-circuits `/bees-code-review` and `/bees-doc-review` when a single invocation returns more than ~10 items or runs more than ~5 turns: triage to blocker-severity items only and defer the rest to the Task summary.

## Model assignment in execution skills

Hardcoded in `bees-execute` and `bees-fix-issue`:

- **Engineer, Test Writer, Code Reviewer, Test Reviewer**: always Opus. Not user-configurable.
- **Doc Writer, Product Manager, Doc Reviewer**: user picks Opus or Sonnet at the start of the run.

## External dependencies

- **bees CLI** (`bees-md` via pipx) — ticket management. Required.
- **Claude Code** — runtime host. Required.
- **Python 3** — helper scripts and JSON edits in skill prose. Required (already a dependency of bees).
- **tmux** — *only* required for the optional later-install skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`). The portable core does not need tmux.

## Deployment

- **Global install** (recommended for single-user machines): clone the repo, copy `skills/*` into `~/.claude/skills/`. POSIX `cp -r` or PowerShell `Copy-Item -Recurse`.
- **Per-project install**: copy `skills/*` into a single repo's `.claude/skills/`. Useful for trying the workflow on one repo without affecting others.
- **Live-edit symlink** (contributor pattern): symlink each `~/.claude/skills/<skill>` at `~/code/bees-workflow/skills/<skill>` so edits in the clone are immediately picked up by Claude Code. See CONTRIBUTING.md for the per-OS commands.

## Per-feature design

### Feature: Test strategy for the skills repo

**Status: paused as of 2026-05-03.** This feature remains paused; the Ephemeral-Agent Orchestration rewrite (Plan Bee `b.5tm`) shipping on `main` does not auto-unpause it. `b.gar`'s Plan Bee body has now been refreshed to reflect the post-orchestration, bees-only architecture (the "Optional beads backend" feature `b.9xr` and its `ticket_backend.py` dispatcher seam were abandoned, not gating Test strategy any longer), and Layer 2.5 — the backend-equivalence harness — is explicitly deferred there. The architecture below still describes the originally-planned dual-backend test strategy and will be re-scoped against the refreshed `b.gar` body when this feature resumes.

**Architecture.** Three independent test layers, each with its own entrypoint, unified under a top-level `make test` target. Test code lives in two locations: per-helper unit tests sit beside the helper they cover (`skills/<skill>/scripts/test_<helper>.py`); cross-cutting test infrastructure lives at `tests/` at the repo root.

**Layer 1 — Helper unit tests.** Per-helper pytest files at `skills/<skill>/scripts/test_<helper>.py` (and `skills/_shared/scripts/test_ticket_backend.py` for the dispatcher introduced in the previous feature). Tests use pytest's `tmp_path` fixture for filesystem isolation and `monkeypatch` for environment overrides. Coverage targets: every public function, every error path, every JSON contract field. The dispatcher's tests exercise both backend branches when the relevant CLI is present and skip cleanly when it isn't. Entrypoint: `pytest skills/`.

**Layer 2 — Structural SKILL.md linter.** A `tools/lint_skills.py` script (Python 3, no third-party deps) walks every `skills/*/SKILL.md`, parses YAML frontmatter, and asserts the design rules baked into CLAUDE.md:

- Frontmatter has `name` and `description`.
- Every fenced code block tagged `bash` (or labeled "POSIX") has a sibling block tagged `powershell` (or labeled "Windows") in the same section, and vice versa.
- No path starting with `/Users/`, `/home/`, or `C:\Users\`.
- No raw `cargo`, `npm`, `pip`, `pipx` commands outside sections explicitly marked as install instructions.
- All bundled-script references use the `<bees-setup-base-dir>` literal placeholder rather than absolute paths.
- All `bees ...` and `bd ...` subcommands in skill prose match an allow-list (catches typos and out-of-vocabulary subcommands).
- Backend-conditional sections come in matching pairs (every "if backend=bees" block has an "if backend=beads" sibling, where applicable).

Output is human-readable: `<file>:<line>: <rule>: <message>`. Exits non-zero on any rule violation. Entrypoint: `python tools/lint_skills.py`.

**Layer 2.5 — Backend-equivalence harness.** A pytest test suite at `tests/equivalence/test_dispatcher_equivalence.py`. Each test:

1. Spins up two temp directories — one initialized with `ticket_backend.py setup-spaces --backend bees`, the other with `--backend beads`.
2. Runs the same sequence of dispatcher verb calls against each (e.g., create Plan Bee → create Epic → set `up_dependencies` → query unblocked tickets → show ticket).
3. Captures resulting state via the dispatcher's read verbs (`query`, `show`).
4. Normalizes the responses — strips `id` (different formats per backend), `created_at` (timestamps), `guid`, and any other backend-specific noise — and asserts deep equality on the remaining structure.

The harness skips gracefully if either CLI is missing, with a `pytest.skip` message naming what's absent. Entrypoint: `pytest tests/equivalence/`.

**Top-level entrypoint.** A `Makefile` at the repo root:

```make
.PHONY: test test-helpers test-lint test-equivalence

test: test-lint test-helpers test-equivalence

test-helpers:
	pytest skills/

test-lint:
	python tools/lint_skills.py

test-equivalence:
	pytest tests/equivalence/
```

For Windows contributors without `make`, a `tools/run_tests.py` script (Python; invokes the same commands via subprocess) provides a portable fallback. Both are documented in CLAUDE.md `## Test Commands`.

**CLAUDE.md `## Test Commands`.** A new contract-style section, contributor-facing only (skills don't read it):

```markdown
## Test Commands

- **Run all tests**: `make test`
- **Helper unit tests only**: `pytest skills/`
- **SKILL.md linter only**: `python tools/lint_skills.py`
- **Backend-equivalence harness only**: `pytest tests/equivalence/`
- **Windows (without make)**: `python tools/run_tests.py`
```

**README Contributing section update.** A short paragraph immediately after the existing Contributing principles, naming the three layers and pointing at `make test` and CLAUDE.md `## Test Commands`.

**CI integration.** A `.github/workflows/test.yml` (or equivalent) runs `make test` on every push and PR. Both backend CLIs installed in the workflow image so Layer 2.5 doesn't skip. The workflow file lives in the repo so contributors can see what's gating their PR.

**Sequencing.** This feature blocks on the "Optional beads backend" feature (Plan Bee `b.9xr`) reaching `done`. Layer 1 covers `ticket_backend.py` (only exists post-b.9xr Epic A); Layer 2 needs to know about backend-conditional blocks (only exist post-b.9xr Epic B); Layer 2.5 explicitly requires both backends to be present.

**Decomposition.** Three Epics:

- Epic A — Layer 1: pytest infrastructure and unit tests for every bundled helper.
- Epic B — Layer 2: structural SKILL.md linter (independent of A; can be worked in parallel).
- Epic C — Layer 2.5 + integration: backend-equivalence harness, top-level `make test`, CLAUDE.md `## Test Commands`, README Contributing paragraph, CI workflow. Blocks on Epic A (uses pytest infrastructure) and Epic B (linter must already be wired to the make target).

### Feature: Ephemeral-Agent Orchestration

**Substrate change.** Three execution skills (`bees-execute`, `bees-fix-issue`, `bees-breakdown-epic`) currently invoke Claude Code's experimental Agent Teams feature (`TeamCreate`, named persistent workers, `SendMessage` between team-lead and workers, shared `TaskList`, `TeamDelete`). This is replaced with the stable `Agent` tool: each work unit is dispatched as a background `Agent(subagent_type=<role>, prompt=<task assignment>, run_in_background=true)` invocation that returns a final result on completion via a harness notification. The orchestrator is the main Claude Code session running the skill — it remains a "team-lead" conceptually but is now a reconciliation-loop driver, not a chat hub.

**Custom subagent types.** Seven role-specific subagent definitions ship at the repo root in `agents/` (matches Claude Code's canonical custom-subagents directory at `~/.claude/agents/` and `<repo>/.claude/agents/`):

| File | Model | Purpose |
|---|---|---|
| `agents/engineer.md` | Opus (always) | Implements code changes for a Subtask or set of Subtasks |
| `agents/test-writer.md` | Opus (always) | Writes/updates tests for completed Engineer work |
| `agents/doc-writer.md` | User's choice (Opus or Sonnet) | Authors or updates documentation |
| `agents/pm.md` | User's choice | Per-Task PM review (spec drift, scope creep, in-flight code/doc review invocations) |
| `agents/code-reviewer.md` | Opus (always) | Wraps `/bees-code-review` skill invocation |
| `agents/doc-reviewer.md` | User's choice | Wraps `/bees-doc-review` skill invocation |
| `agents/test-reviewer.md` | Opus (always) | Wraps `/bees-test-review` skill invocation |

Each definition file carries YAML frontmatter (`name`, `description`, `model`, `tools` allowlist) plus a markdown body capturing role-specific instructions (what to read, what to do, what to return). Skill prose in `bees-execute` etc. references subagent types by name (`subagent_type: "engineer"`) without inline role instructions — substantially reducing SKILL.md size.

**Reconciliation loop.** The orchestrator's tick is purely event-driven — it wakes on Agent completion notifications, user input, and tool results. No `/loop`, `ScheduleWakeup`, `CronCreate`, or polling loop. Each tick consists of:

1. **Read state.** Query bees ticket state for the current Epic / Task / Subtasks (`bees execute-freeform-query`); read TaskList for active Agent invocations; check git state if relevant.
2. **Reconcile.** For each Subtask whose preconditions are met but no Agent is currently working it: dispatch a fresh Agent (or send to a warm one). For each Subtask whose Agent has just returned: persist the result (mark bees ticket `done`, update TaskList task `completed`). For each completed Task: trigger PM review via a fresh PM Agent. For each completed Epic: run inter-Epic interaction checkpoint (orchestrator-direct, no Agent). When all Epics done: spawn the post-Bee review team (three reviewer Agents, all fresh).
3. **Yield.** No explicit wake scheduling; the harness fires the next tick on the next inbound event (Agent completion or user input).

This is a Kubernetes-controller shape applied to skill orchestration: declarative state goal (bees ticket statuses), continuous reconciliation against actual state, no hand-managed message queues.

**Hub-and-spoke specialist model preserved.** Workers do not communicate with each other. All routing is orchestrator→Agent. The artifact-based handoff (Engineer's commits become Test Writer's input; Test Writer's tests become PM's review material) replaces the message-based handoff. This is structurally identical to the current hub-and-spoke prescription (post-b.11f), achieved through a substrate that doesn't permit peer comms rather than through a "do not message peers" rule the model can drop.

**Cold-start hybrid (warm vs fresh Agents).** Per-Subtask lifecycle:

- Engineer, Test Writer, and Doc Writer are dispatched fresh per Subtask via `Agent(subagent_type=<role>, prompt=<task assignment>, run_in_background=true)`. Coherence across dependent Subtasks within a Task is preserved through the diff: each later Engineer reads the prior Engineer's commit, matching the hub-and-spoke "diff is the handoff" pattern. Concurrent specialist work is preserved: Engineer-Subtask-N+1 runs in parallel with Test-Writer-Subtask-N once the orchestrator's reconciliation loop ticks past Engineer-Subtask-N's completion. Token cost is bounded by Claude Code's prompt cache (5-min TTL), which absorbs the warm-start savings the previous warm-Agent design targeted.
- PM, Code Reviewer, Doc Reviewer, Test Reviewer always fresh. Reviewers must be fresh-eyes by design; PM's per-subtask reviews and final-Task review benefit from a clean slate.

The shipped per-Subtask cold-dispatch pattern diverges intentionally from the planning-stage design's named-warm-Agent + `SendMessage` pattern. `SendMessage` is unavailable without `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, which this feature removes; the warm-Agent token-cost optimization is therefore deferred. Issue **`b.x9w`** (`Re-probe SendMessage-without-Agent-Teams as warm-Agent token-cost optimization`) tracks the follow-up under "periodic re-test" semantics — closed only when (a) a future Claude Code release makes `SendMessage` available without Agent Teams and a follow-up Bee implements warm-Agent dispatch as a token-cost optimization, or (b) the optimization is dropped permanently.

**TaskList as progress UI.** The orchestrator creates one TaskList task per concurrent Agent invocation (e.g., `engineer-qf-subtask-1`, `test-writer-qf-subtask-1`, `pm-qf-subtask-1-review`). Status transitions (`pending → in_progress → completed`) are updated as Agents start and finish; `metadata.activity` carries finer-grained progress (e.g., `"running /bees-code-review (~5 min)"`). Claude Code's native TaskList UI renders these live, providing visual parallelism without an Agent Teams display backend. A one-line tick summary printed to stdout supports `tail -f`-style watching.

**Recursive delegation (probe-then-decide).** The data model (Bee → Epic → Task → Subtask) is naturally hierarchical and the architecture supports an Epic-level sub-orchestrator Agent that internally manages its Tasks via further Agent invocations. Whether the Claude Code harness permits an Agent to spawn further Agents is uncertain at planning time; the implementation will probe this early. If permitted, the Epic-level sub-orchestrator pattern is used as a context-management optimization. If not, the orchestrator runs flat — the existing Epic-boundary context-clear discipline (currently in `bees-execute/SKILL.md`) bounds growth at ~25-30% of the 1M context window per Epic, and the skill ships flat orchestration without functional regression.

**State sources.** Single source of truth for ticket state is bees (read via `bees execute-freeform-query` and `bees show-ticket`). TaskList carries transient orchestration state (which Agent is currently working what, with progress metadata) and is reset between Tasks. Conversation message history carries Agent invocation prompts and return values (subject to harness auto-compaction). The `blocked_on` metadata signal on TaskList tasks is removed — Agents either return with a "blocked" result that the orchestrator handles next tick, or escalate to the user via the orchestrator's prose. There is no idle-then-blocked transition to detect.

**Removed components.**

- `skills/bees-execute/scripts/check_agent_teams.py` — deleted along with all skill-prose references.
- `skills/bees-execute/scripts/force_clean_team.py` — deleted along with all skill-prose references.
- `bees-setup` Agent Teams precondition step — removed.
- `bees-setup` `teammateMode` configuration step — removed.
- `bees-setup` iTerm2 hard-prompt workaround prose — removed.
- README's "Required: enable Agent Teams" section — removed.
- README's "Display backend" section — removed.
- All `TeamCreate`, `TeamDelete`, named-team-scoped agent prose in `bees-execute`, `bees-fix-issue`, `bees-breakdown-epic` — removed.
- The `blocked_on` metadata convention in worker Instructions — removed (all three skills).
- The "graduated escalation when teammates go silent" four-rung ladder in `bees-execute` and `bees-fix-issue` — removed.
- The "Team-lead message-flow choreography" section in `bees-execute` — removed.

**Updated SDD sections (not in this Plan-stage edit; updated as part of implementation):**

- "Team orchestration in execution skills" — replaced by an "Orchestration in execution skills" section describing the reconciliation-loop pattern, hub-and-spoke via substrate, hybrid cold-start, TaskList progress UI.
- "Tech stack" — Agent Teams requirement removed; `Agent` tool background invocations and `agents/` definition files referenced.
- "Key components" — two helper scripts removed; `agents/<role>.md` files added.
- "External dependencies" — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` requirement dropped.

**Updated install layout.**

README install instructions extend to copy `agents/*` into `~/.claude/agents/` (global) or `<repo>/.claude/agents/` (per-project) alongside the existing `skills/*` copy. The two-tier paths parallel the existing skills install pattern. A future plugin packaging maps these directories one-to-one without restructuring.

**Subagent definition format.** Each `agents/<role>.md` carries YAML frontmatter (`name`, `description`, `model`, `tools`) plus a markdown body. The body is the role-specific Instructions block currently embedded inline in `bees-execute`'s SKILL.md (lines ~290-389). Lifting these blocks into definition files reduces SKILL.md prose by roughly 100-150 lines per file and makes role customization a first-class operation (a downstream user can edit `~/.claude/agents/engineer.md` to add project-specific guidance without forking the skill).

**Sequencing.** The work decomposes into Epics (final structure determined during /bees-breakdown-epic):

- **Epic A — Subagent definitions and infrastructure.** Author the seven `agents/*.md` files with role prose lifted from current SKILL.md inline blocks. Update install instructions in README. Probe whether subagents load correctly from `~/.claude/agents/`. No SKILL.md changes yet — old Agent Teams paths still in place.
- **Epic B — `bees-execute` rewrite.** Rewrite `bees-execute/SKILL.md` to use the reconciliation-loop pattern with background `Agent` invocations referencing the new subagent types. Drop the message-flow choreography, blocked_on signal, escalation ladder, and helper-script references. Probe recursive delegation; pick flat or nested based on result. Verify against a real Bee.
- **Epic C — `bees-fix-issue` rewrite.** Same pattern as Epic B at issue scope.
- **Epic D — `bees-breakdown-epic` rewrite.** Smallest of the three (read-only research team). Apply the same pattern.
- **Epic E — `bees-setup` cleanup.** Remove Agent Teams precondition step, `teammateMode` config, iTerm2 prose. Delete the two helper scripts.
- **Epic F — Doc cleanup and `b.gar` body update.** Update existing SDD sections (Tech stack, Key components, Team orchestration, External dependencies) to remove Agent Teams references. Update README. Update `b.gar`'s Plan Bee body to reflect new architecture.

Epic dependencies: B / C / D depend on A (subagent definitions must exist before skills reference them). E and F can land in parallel with B/C/D once A is done. F is last (depends on all preceding work being landed so the doc updates accurately reflect the implementation).
