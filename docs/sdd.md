# bees-workflow — Software Design

## Tech stack

- **Skill prose**: Markdown (`SKILL.md`) with YAML frontmatter (`name`, `description`). The body is the instructions Claude follows when the skill is invoked.
- **Helper scripts**: Python 3 (cross-platform). Two exist today — `bees-setup/scripts/detect_fast_path.py` (new-machine fast-path detection) and `bees-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser/scoper, sibling-resolved by `bees-execute` and `bees-fix-issue`).
- **External CLI**: [bees](https://github.com/gabemahoney/bees) (`bees-md` on pipx, Python 3.10+) for ticket management.
- **Runtime host**: [Claude Code](https://claude.com/claude-code) — skills are invoked via `/<skill>` slash commands. The execution skills (`bees-execute`, `bees-fix-issue`, `bees-breakdown-epic`) orchestrate parallel work by dispatching ephemeral background subagents via the stable `Agent` tool (`run_in_background=true`). Role contracts ship as seven custom-subagent definition files at `agents/<role>.md` in the repo root (`engineer.md`, `test-writer.md`, `doc-writer.md`, `pm.md`, `code-reviewer.md`, `doc-reviewer.md`, `test-reviewer.md`), installed alongside skills at `~/.claude/agents/` (global) or `<repo>/.claude/agents/` (per-project). No experimental feature flags or display-backend configuration are required.

## Architecture overview

The repo ships 14 portable-core skills under `skills/<name>/`, each self-contained as a `SKILL.md` plus optional `scripts/`. Skills are loaded by Claude Code from either `~/.claude/skills/` (global install) or `<repo>/.claude/skills/` (per-project install). When a skill needs a bundled helper script (its own or a sibling's), it resolves the absolute path at runtime from the skill's own base directory — which Claude Code provides in the skill invocation header. No per-machine paths are persisted to CLAUDE.md or any other tracked file.

The workflow chain is linear with two entry points:

- `/bees-setup` — one-time per repo (idempotent re-runs)
- `/bees-plan` *or* `/bees-plan-from-specs` — produces a Plan Bee with Epic children
- `/bees-breakdown-epic` — decomposes one Epic into Tasks/Subtasks, commits the new ticket files at end-of-skill
- `/bees-execute` — walks every Epic, dispatches subagents per Task, commits
- `/bees-file-issue` *and* `/bees-fix-issue` — anytime, for bugs/follow-ups

Four review skills (`bees-code-review`, `bees-doc-review`, `bees-test-review`, `bees-spec-review`) are dual-mode — primarily invoked by orchestrating skills (`/bees-execute` and `/bees-fix-issue` for the first three; `/bees-write-prd`, `/bees-write-sdd`, or `/bees-plan` for `bees-spec-review` once those wire it in) during their review cycles, with standalone invocation also supported for ad-hoc reviews outside the workflow.

The workflow uses three hives in the target repo: **Plans** (top-level, with t1/t2/t3 = Epic/Task/Subtask, statuses `drafted`/`ready`/`in_progress`/`done`), **Issues** (no children, statuses `open`/`done`), and **Specs** (top-level Spec Bees with `t1=Doc/Docs` children, statuses `drafted`/`ready`). The Specs hive is colonized by `/bees-setup` as a placeholder for future Spec content; the `t1=Doc` children themselves are authored by other skills and are not produced by `/bees-setup`. Plan Bees may carry one or more spec sources in their `reference_materials` field, resolved per-item by one of two resolvers the bees CLI supports: the **`file-path` resolver** (the default) treats each entry as a path to an on-disk source document (PRD, SDD, etc.) — used by `/bees-plan-from-specs`; the **`bees` resolver** treats each entry as a ticket ID — used by `/bees-plan` to point at a Spec Bee whose body and `t1=Doc` children (PRD + SDD, differentiated by exact title-match) hold the authoritative spec content. When a Plan Bee has null/empty `reference_materials`, the **Plan Bee body itself becomes the authoritative spec** — downstream skills explicitly substitute the Bee body for the PRD/SDD in that mode. The full resolver-contract phrasing lives in `docs/doc-writing-guide.md` `## Project terminology`.

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
- **`skills/bees-spec-review/`** — dual-mode reviewer for Spec Bee content (PRD and SDD `t1=Doc` children). Primary use: gates a Spec Bee's `drafted → ready` transition when invoked by spec-authoring or planning skills (`/bees-write-prd`, `/bees-write-sdd`, `/bees-plan`) once they wire it in. Secondary use: standalone ad-hoc spec review (`/bees-spec-review <spec-bee-id> [--doc PRD|SDD]`). Returns a list of improvement work items in the same severity-tagged shape as the other three reviewers; does not mutate any ticket. Conceptual analog of upstream apiary's `/req-review`.
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

### Feature: Side-effect-free /bees-plan and /bees-file-issue with preserved context

**Architecture.** The redesign is structured around four architectural moves: a new **Specs hive**, a polymorphic `reference_materials` field with a `bees` resolver, two new composable spec-authoring skills, and an expansion of the `doc-writer` agent's responsibility to own post-implementation cumulative-doc updates. Together these decouple per-feature spec authoring from cumulative project-doc mutation: per-feature PRD/SDD content lives in queryable bees tickets and is folded into the cumulative on-disk docs only after implementation lands.

**Specs hive.** A third top-level hive joins Plans and Issues. Spec Bees are top-level Bees in the Specs hive with `t1=Doc/Docs` children — PRD and SDD as separate `t1=Doc` tickets, differentiated by exact title-match (`PRD` vs `SDD`), not by tier. The hive's allowed resolver is `bees`, so a Plan Bee's `reference_materials` can point at a Spec Bee. Status vocabulary is two-state — `drafted` (being written) and `ready` (referenceable) — distinct from the four-state Plans ladder and the two-state Issues ladder; `worker`/`finished` semantics are conformance-driven for spec docs and do not add meaning, so the shorter ladder is intentional. `/bees-setup` colonizes the Specs hive at first-run and detect-and-adds it on existing repos that pre-date the hive; `/bees-execute`, `/bees-fix-issue`, and `/bees-breakdown-epic` hard-fail with `Run /bees-setup first. — Specs hive is not colonized for this repo.` when the hive is missing.

**Reference materials with `bees` resolver.** The bees CLI's `reference_materials` field accepts arbitrary resolvers per entry. Two are now in use across the workflow: the **`file-path` resolver** (the default) treats each entry as a path to an on-disk source document — used by `/bees-plan-from-specs`; the **`bees` resolver** treats each entry as a ticket ID of the shape `[{"value":"<bee-id>","resolver":"bees"}]` — used by `/bees-plan` to point at a Spec Bee whose body and `t1=Doc` children hold the authoritative spec content. When `reference_materials` is null/empty (e.g., the bootstrap-mode case), the **Plan Bee body itself becomes the authoritative spec** and downstream skills explicitly substitute the Bee body for the PRD/SDD. This three-source-mode design (path on disk / referenced Bee + children / own Bee body) preserves polymorphism for future GitHub-issue, Linear, or external-doc resolvers without skill changes.

**Two-hop lookup.** `agents/pm.md` and `skills/bees-breakdown-epic/SKILL.md` resolve `bees`-resolver entries via a two-hop pattern: hop 1 reads the entry's `value` from the parent Bee's `reference_materials`; hop 2 runs `bees show-ticket --ids <bee-id>` and treats the resolved Bee's body (or, for Spec Bees, its `t1=Doc` children enumerated by exact title-match) as the spec source. The `file-path` resolver path and the body-as-spec fallback remain functional and untouched. Canonical recipes for the two-hop pattern live in `docs/doc-writing-guide.md` `## Project terminology` under the `Reference materials` entry.

**`/bees-write-prd` and `/bees-write-sdd` skills.** Spec-authoring logic factors out of `/bees-plan` into two new composable sub-skills, each owning the quality-bar prose for its respective doc type. Default user experience is unchanged — typing `/bees-plan` still produces a Plan Bee with PRD and SDD content authored — because `/bees-plan` invokes them inline via the Skill tool. They are also solo-invokable for revisions (`/bees-write-prd <spec-bee-id>`, `/bees-write-sdd <spec-bee-id>`), which is a real use case (revising a PRD after learning something during execution). The factoring shrinks `/bees-plan` substantially and gives mental-model parity with apiary's `/write-prd` + `/write-srd`. PRD and SDD child-ticket bodies include explicit sections for decisions, rejected alternatives, and rationale — not just requirements.

**`doc-writer` agent expanded responsibility.** The `agents/doc-writer.md` contract now owns appending or updating `### Feature: <title>` subsections in the cumulative project PRD (`## Per-feature scope` header) and SDD (`## Per-feature design` header) post-implementation, reflecting what was actually built. The redundancy that previously had `/bees-plan` writing speculative SDD content AND `doc-writer` updating SDD from the actual diff is resolved: the speculative write is gone; the post-implementation write (anchored to what shipped) remains. The doc-writer's categorization heuristic (user-facing feature vs architecture-only vs deployment vs pure-refactor) governs which cumulative doc(s) get an entry on a given run; the diff is the primary signal, with the dispatched Task/Subtask body as a secondary signal. Idempotency is enforced by exact-match on the verbatim Plan Bee title — `### Feature: <title>` heading text is matched case-sensitively, and an existing subsection is replaced in place rather than duplicated.

**`/bees-file-issue` redesign.** Step 4 no longer mutates project docs when an Issue surfaces doc divergence. Instead, divergence observations are captured in a `## Doc divergence noted` section in the Issue body for `/bees-fix-issue`'s doc-writer to act on at fix time. The Issue body template gains optional `## Background and rationale` and `## Decisions and rejected alternatives` sections so that the analytical depth of the originating discussion survives into the Issue (the Issue body is the spec source for `/bees-fix-issue` — there is no `reference_materials`, no children, no PRD/SDD pointer). The skill is mid-conversation aware: when invoked from a substantive preceding discussion, it does not re-ask discovery questions that the conversation already answered.

**Scoped-marker machinery retained.** The `Scoped to ...` marker, the `skills/bees-breakdown-epic/scripts/scoped_marker_resolver.py` parser, and the asymmetric Path A vs Path B handling in `agents/pm.md` are all retained. `/bees-plan-from-specs --feature "<title>"` remains the marker producer; `/bees-breakdown-epic`, `/bees-execute`, and `/bees-fix-issue` remain marker consumers (the `bees-fix-issue` consumer iterates the Issue's `up_dependencies` array opportunistically, since Issues have no canonical parent-Plan-Bee field). What changed is only that `/bees-plan` no longer emits markers — because it no longer co-mingles per-feature content into shared cumulative docs, there is nothing to scope inside.

**Decomposition.** The feature shipped as eight Epics under Plan Bee `b.31f`: Epic 1 (Specs hive setup in `/bees-setup`); Epic 2 (`/bees-write-prd` skill); Epic 3 (`/bees-write-sdd` skill); Epic 4 (`/bees-plan` redesign with Spec Bee + `reference_materials` + `bees` resolver, including mid-conversation context awareness in Steps 0-2); Epic 5 (PM/breakdown two-hop lookup updates); Epic 6 (`doc-writer` cumulative-doc responsibility expansion); Epic 7 (`/bees-plan-from-specs` regression check + Overview prose positioning vs `/bees-plan`); Epic 8 (`/bees-file-issue` redesign — no doc mutation, `## Doc divergence noted` capture, optional discussion-derived body sections, mid-conversation awareness). Epic 6 was self-referential (it edited the doc-writer that the cumulative-doc write was meant to use) so the cumulative `### Feature: <title>` entries for `b.31f` itself were backfilled manually under Issue `b.2w1` after the Bee was `done`. The originally-deferred `/bees-spec-review` follow-up (named in the b.31f PRD's `## Out of scope` list) shipped separately under Issue `b.uxa` — see the dedicated `### Feature:` subsection below.

### Feature: Add /bees-spec-review skill (apiary /req-review analog)

**Architecture.** A new dual-mode review skill mirroring the structural shape of `/bees-code-review`, `/bees-doc-review`, and `/bees-test-review`. Lives at `skills/bees-spec-review/SKILL.md` (no bundled scripts — the skill is prose-only, dispatching through `bees execute-freeform-query` and `bees show-ticket` for ticket I/O). No new contract keys; no new agents; no changes to the seven role files in `agents/`.

**Inputs and resolution.** One positional argument `<spec-bee-id>` (the Spec Bee whose PRD and/or SDD `t1=Doc` children are under review) and one optional `--doc PRD|SDD` flag scoping to a single child. Doc resolution uses a freeform query stage `[hive=specs, parent=<spec-bee-id>, title~^(PRD|SDD)$]` (or the narrowed single-title regex when `--doc` is passed); the title regex is anchored on both ends so the match is exact and case-sensitive against the canonical `PRD` / `SDD` titles produced by `/bees-write-prd` and `/bees-write-sdd`. Each resolved child's body is fetched via `bees show-ticket --ids <doc-ticket-id>` and treated as the source of truth — no on-disk file is read as a substitute, since downstream skills (`/bees-breakdown-epic`, `/bees-execute`'s Engineer / PM, `/bees-fix-issue`) consume the bees ticket body, not any artifact on disk.

**Checklists.** The skill carries three checklist passes inline in its prose:

1. **PRD checklist** — eight categories tied to the twelve required sections imposed by `/bees-write-prd` Step 4: section completeness, problem-statement clarity, acceptance-criteria measurability, scope clarity (`## Non-Goals / Out of Scope`), implementation-detail leakage (PRD covers what/why, not how), vague-language detection, rationale-and-decisions substance, and open-questions discipline.
2. **SDD checklist** — ten categories tied to the seven required sections imposed by `/bees-write-sdd` Step 5: section completeness, codebase-grounding (real module/file/function names, `RESEARCH NEEDED:` tag surfacing), requirements structure (`SR-` prefix, domain grouping, observable-behavior framing), architecture coverage (top-level framing plus component-by-component coverage), existing-behavior preservation (greenfield placeholder vs explicit contracts), test-fixture conventions, documentation coverage (canonical CLAUDE.md `## Documentation Locations` paths), decomposition signal for downstream Epic breakdown, data-model and contract-key impact callouts, and rationale-and-decisions substance.
3. **Cross-document consistency pass** — five categories run only when both PRD and SDD are in scope: goal-to-requirement coverage (every PRD `## Goals` entry maps to at least one SDD `SR-` requirement), acceptance-criterion-to-design coverage (every PRD `## Acceptance Criteria` entry has SDD coverage), out-of-scope alignment (no SDD design element implements anything PRD `## Non-Goals / Out of Scope` excludes), open-question alignment (no SDD section confidently decides a question PRD `## Open Questions` lists as still open), and rationale alignment (PRD and SDD `## Decisions and rejected alternatives` sections agree on rejected alternatives when both have substantive content).

**Output contract.** The skill returns a numbered markdown list under a `## Spec Review Work Items` heading. Each item carries a severity tag (`blocker`, `suggestion`, `nit`) matching the ladder used by the other three reviewers, cites the document (`PRD` or `SDD`) and section heading, and gives a one-line description of the finding. When there are no important findings, the skill says so explicitly rather than padding the list with trivia. The skill does not mutate any ticket — output is text-only, returned to the caller (human or orchestrating skill).

**Dual-mode invocation.** Standalone use is `/bees-spec-review <spec-bee-id> [--doc PRD|SDD]` from the prompt — the caller is a human or another standalone tool, output the work-item list and stop. Orchestrator-invoked use (when `/bees-write-prd`, `/bees-write-sdd`, or `/bees-plan` later wires this skill in as a post-write gate on the Spec Bee's `drafted → ready` transition) applies the same loop-bounding discipline the other three reviewers carry: be selective, do not report trivial-but-not-important items each pass, say "no important findings" when applicable to avoid infinite review-fix-review loops.

**Preconditions.** Hard-fail with `Run /bees-setup first.` (plus a one-line note naming the missing piece) if the Specs hive is not colonized for the host repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`). The skill does not require CLAUDE.md `## Build Commands` since it produces text findings, not build/test/lint output.

**Catalog and prose updates.** README.md skill table gets a new row parallel to the existing review-skill rows; the surrounding "three reviewers" sentence becomes "four reviewers" and lists `/bees-spec-review` alongside the existing three. The portable-core skill count (referenced in README.md's "Coming soon" preamble, this SDD's `## Architecture overview`, CLAUDE.md's tmux-dependency rule, and `docs/doc-writing-guide.md`'s contributing principles) bumps from 13 to 14. The SDD `## Architecture overview` "Three review skills" sentence becomes "Four review skills" and adds `bees-spec-review` to the parenthetical list; the SDD `## Key components` review-skill entry stays as-is and a new `bees-spec-review/` entry follows it.

**Decomposition.** Shipped as a single Issue (`b.uxa`) rather than a multi-Epic Plan Bee, on the reasoning that the skill is small (one new `SKILL.md`, no new helpers, no contract changes, no agent changes) and the analogs already exist for the Engineer to model from. The `up_dependencies: [b.31f]` on the Issue is a blocker dep, not a scope-context Plan Bee — the new skill stands on its own and is not scoped to any subsection of `b.31f`'s spec content.
