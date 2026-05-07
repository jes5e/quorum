# bees-workflow — Software Design

## Tech stack

- **Skill prose**: Markdown (`SKILL.md`) with YAML frontmatter (`name`, `description`). The body is the instructions Claude follows when the skill is invoked.
- **Helper scripts**: Python 3 (cross-platform). Two exist today — `bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection) and `bees-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser/scoper, sibling-resolved by `bees-execute` and `bees-fix-issue`).
- **External CLI**: [bees](https://github.com/gabemahoney/bees) (`bees-md` on pipx, Python 3.10+) for ticket management.
- **Runtime host**: [Claude Code](https://claude.com/claude-code) — skills are invoked via `/<skill>` slash commands. The execution skills (`bees-execute`, `bees-fix-issue`, `bees-breakdown-epic`) orchestrate parallel work by dispatching ephemeral background subagents via the stable `Agent` tool (`run_in_background=true`). Role contracts ship as seven custom-subagent definition files at `agents/<role>.md` in the repo root (`engineer.md`, `test-writer.md`, `doc-writer.md`, `pm.md`, `code-reviewer.md`, `doc-reviewer.md`, `test-reviewer.md`), installed alongside skills at `~/.claude/agents/` (global) or `<repo>/.claude/agents/` (per-project). No experimental feature flags or display-backend configuration are required.

## Architecture overview

The repo ships eleven portable-core skills under `skills/<name>/`, each self-contained as a `SKILL.md` plus optional `scripts/`. Skills are loaded by Claude Code from either `~/.claude/skills/` (global install) or `<repo>/.claude/skills/` (per-project install). When a skill needs a bundled helper script (its own or a sibling's), it resolves the absolute path at runtime from the skill's own base directory — which Claude Code provides in the skill invocation header. No per-machine paths are persisted to CLAUDE.md or any other tracked file.

The workflow chain is linear with two entry points:

- `/bees-setup` — one-time per repo (idempotent re-runs)
- `/bees-plan` *or* `/bees-plan-from-specs` — produces a Plan Bee with Epic children
- `/bees-breakdown-epic` — decomposes one Epic into Tasks/Subtasks, commits the new ticket files at end-of-skill
- `/bees-execute` — walks every Epic, dispatches subagents per Task, commits
- `/bees-file-issue` *and* `/bees-fix-issue` — anytime, for bugs/follow-ups

Three review skills (`bees-code-review`, `bees-doc-review`, `bees-test-review`) are dual-mode — primarily invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, with standalone invocation also supported for ad-hoc reviews outside the workflow.

The workflow uses three hives in the target repo: **Plans** (top-level, with t1/t2/t3 = Epic/Task/Subtask, statuses `drafted`/`ready`/`in_progress`/`done`), **Issues** (no children, statuses `open`/`done`), and **Specs** (top-level Spec Bees with `t1=Doc/Docs` children, statuses `drafted`/`ready`). The Specs hive is colonized by `/bees-setup` as a placeholder for future Spec content; the `t1=Doc` children themselves are authored by other skills and are not produced by `/bees-setup`. Plan Bees may carry one or more on-disk source documents (PRD, SDD, etc.) in their `reference_materials` field, resolved per-item by the bees CLI's built-in `file-path` resolver. When a Plan Bee has null/empty `reference_materials`, the **Plan Bee body itself becomes the authoritative spec** — downstream skills explicitly substitute the Bee body for the PRD/SDD in that mode.

## Key components

- **`skills/bees-setup/`** — one-time configuration: colonizes three hives (**Plans** — top-level, t1/t2/t3 = Epic/Task/Subtask, statuses `drafted`/`ready`/`in_progress`/`done`; **Issues** — no children, statuses `open`/`done`; **Specs** — top-level Spec Bees with `t1=Doc/Docs` children, statuses `drafted`/`ready`, colonized by `/bees-setup` for use by future skills, no content is authored here at setup time), writes the two required CLAUDE.md sections (`Documentation Locations`, `Build Commands`), optional PRD/SDD bootstrap from existing codebase. Detects the new-machine case (on-disk hive markers present, the repo's scope not registered in `~/.bees/config.json`, CLAUDE.md already populated) via the bundled `detect_fast_path.py` helper and offers a fast path that re-registers hives from canonical defaults without touching CLAUDE.md.
- **`skills/bees-plan/`** — interactive scope discovery for an idea or feature without finalized specs. Produces a Plan Bee with Epic children.
- **`skills/bees-plan-from-specs/`** — express path for a finalized PRD+SDD on disk. Same Plan Bee output as `/bees-plan`. Default (single-feature) mode hard-fails on PRDs/SDDs that contain more than one `### Feature: <title>` subsection (the cumulative-PRD pattern produced by repeated `/bees-plan` invocations) and routes the user back to `/bees-plan` to avoid re-planning previously-planned features. The optional `--feature "<title>"` flag bypasses the multi-feature guard and scopes the planning run to a single `### Feature: <title>` subsection extracted from each of the PRD and SDD (heading must exist in both docs); `reference_materials` still points at the canonical full PRD/SDD paths, and the Plan Bee body carries a `Scoped to ...` marker so downstream skills can tell the Bee covers a sub-region of a cumulative spec. **Marker producer.**
- **`skills/bees-breakdown-epic/`** — decompose one Epic into Tasks and Subtasks. The only skill where dispatched subagents run in `mode: "plan"` (read-only researchers). At end-of-skill, stages and commits the new ticket files (Tasks, Subtasks, Epic status update) when the Plans hive lives inside the current git repo — resolved via `bees list-hives` in the same pattern `bees-file-issue` uses; when the hive lives outside the repo, the commit step is skipped and the next-steps menu carries a one-line note. The end-of-skill next-steps menu carries per-option "best when …" rationales and moves the Recommended badge across three cases keyed on (a) whether any drafted sibling Epics remain under the parent Bee and (b) whether breaking down the next Epic right now risks rework: when no drafted siblings remain, the Recommended option is "execute the whole Bee"; when drafted siblings remain and the orchestrator judges that the just-broken-down Epic's implementation will reshape contracts consumed by them (foundation-then-rewrites pattern), the Recommended option is "execute this Epic first; defer downstream breakdown"; when drafted siblings remain with pure-ordering dependencies only (no reshape risk), the Recommended option is "break down the next Epic". The case-specific rationale is surfaced only as the Recommended option's `Best when …` subtitle — a freestanding rationale paragraph above the menu is forbidden because the Claude Code UI has been observed truncating long header prose mid-sentence. **Marker consumer** — Step 1 (read parent Bee) detects the `Scoped to ...` marker and restricts the resolved doc content to the matching `### Feature: <title>` subsection before Task decomposition and Spec Traceability Review. Bundles the shared parser/scoper helper at `scripts/scoped_marker_resolver.py` (sibling-resolved by `bees-execute` and `bees-fix-issue`).
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

- **`skills/bees-setup/scripts/detect_fast_path.py`** — detect the new-machine fast-path scenario. Emits a JSON status payload (hive markers found, scope-already-registered check, CLAUDE.md sections populated, `fast_path_eligible` boolean) consumed by `/bees-setup`.
- **`skills/bees-breakdown-epic/scripts/scoped_marker_resolver.py`** — shared parser/scoper for the `Scoped to ...` marker emitted by `/bees-plan-from-specs --feature`. Takes one positional argument (path to a file containing the parent Bee body); prints `{"scoped": false}` when no marker is present, prints `{"scoped": true, "title": "...", "docs": [{"path": "...", "content": "..."}, ...]}` when the marker is present and well-formed, and exits 2 with a single human-readable line on stderr otherwise. Resolved as a sibling script by `bees-execute` and `bees-fix-issue`. Grammar and hard-fail rules documented in `docs/doc-writing-guide.md` `## The Scoped-marker contract`.

## Contract keys

The target repo's CLAUDE.md carries two sections that act as a string contract between skills. `bees-setup` writes them; every other skill reads them.

- `## Documentation Locations` — `Project requirements doc (PRD)`, `Internal architecture docs (SDD)`, `Customer-facing docs`, `Engineering best practices`, `Test writing guide`, `Test review guide`, `Doc writing guide`
- `## Build Commands` — `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`

`bees-execute`, `bees-fix-issue`, and `bees-breakdown-epic` hard-fail with `Run /bees-setup first.` (with a trailing `— <reason>` clause naming the specific gap, e.g., `Run /bees-setup first. — Specs hive is not colonized for this repo.`) if either of the two required CLAUDE.md sections, any required key inside them, or any of the three required hives (Plans, Issues, Specs) is missing.

Bundled helper script paths (e.g., `scoped_marker_resolver.py`) are *not* part of the CLAUDE.md contract — each skill resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header. This keeps per-machine paths out of tracked files.

## Orchestration in execution skills

`bees-execute`, `bees-fix-issue`, and `bees-breakdown-epic` orchestrate work by dispatching ephemeral background subagents via the stable `Agent` tool (`run_in_background=true`). The main Claude Code session running the skill is the orchestrator — mechanically a reconciliation-loop driver, not a chat hub.

- **Reconciliation loop (read state / reconcile / yield).** Each tick is purely event-driven — the harness wakes the orchestrator on Agent completion notifications, user input, and tool results. There is no clock primitive: no `/loop`, no `ScheduleWakeup`, no `CronCreate`, no polling loop. A tick reads ticket state (`bees execute-freeform-query`, `bees show-ticket`), reads the TaskList for active Agent invocations, reconciles the gap (dispatch a fresh Agent for any Subtask whose preconditions are met but no Agent is on it; persist results for any Subtask whose Agent has just returned; trigger PM review for completed Tasks; run inter-Epic checkpoints; dispatch the post-Bee fresh-eyes reviewers when all Epics are done), then yields. This is a Kubernetes-controller shape applied to skill orchestration: declarative state goal (bees ticket statuses), continuous reconciliation against actual state, no hand-managed message queues.
- **Hub-and-spoke as a structural property of the substrate.** Workers do not communicate with each other. All routing is orchestrator → Agent. The artifact-based handoff (Engineer's commits become Test Writer's input; Test Writer's tests become PM's review material) replaces the message-based handoff. This is structurally identical to the prior hub-and-spoke prescription, but achieved through a substrate that doesn't permit peer comms rather than through a "do not message peers" rule the model can drop.
- **Flat orchestration.** Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), subagents cannot dispatch other subagents — only the top-level orchestrator may dispatch Agents. The orchestrator's working-set growth is bounded by the Epic-boundary context-clear discipline (defined in `bees-execute/SKILL.md` Section 4.2).
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
