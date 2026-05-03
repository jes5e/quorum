---
id: b.9xr
type: bee
title: Optional beads backend
down_dependencies:
- b.gar
parent: null
children:
- t1.9xr.p6
- t1.9xr.4e
egg:
- /Users/jesseg/code/bees-workflow/docs/prd.md
- /Users/jesseg/code/bees-workflow/docs/sdd.md
created_at: '2026-05-02T14:09:41.628044'
status: ready
schema_version: '0.1'
guid: 9xr3vcmmpgympucy7314ji7dt5z2otz4
---

Add optional support for the beads ticket backend (https://github.com/gastownhall/beads) alongside the existing bees backend. A repo picks one at /bees-setup time; the choice persists in CLAUDE.md ## Ticket Backend. All 11 portable-core skills work transparently on either backend via a new skills/_shared/scripts/ticket_backend.py dispatcher. Both backends cannot coexist in a single repo.

**Status: paused as of 2026-05-03.** The implementation branch (`bee/b.9xr`) was abandoned to prioritize the Ephemeral-Agent Orchestration rewrite, which targets stability of the bees-only workflow on `main`. The PRD and SDD subsections that previously described this feature were reverted from `docs/prd.md` and `docs/sdd.md` to keep `main`'s docs consistent with the bees-only state. Their content is preserved verbatim below so this Plan Bee can be revived later without re-deriving the spec — when work resumes, copy each section back into the corresponding PRD/SDD per-feature block (`## Per-feature scope` and `## Per-feature design` respectively) and proceed.

The abandoned implementation branch on origin (`origin/bee/b.9xr`) carries the Epic A dispatcher refactor as a reference point; do not merge it as-is — start fresh against the post-orchestration `main`. Note also that the dispatcher rule added to CLAUDE.md on the abandoned branch (the `## Backend dispatcher` section that mandated routing through `ticket_backend.py`) is NOT on `main`; that rule will need to be re-introduced when this Plan Bee is revived, and skill prose will need re-migrating off direct `bees ...` calls onto the dispatcher.

## Recovered PRD content

Was at `docs/prd.md` `## Per-feature scope` `### Feature: Optional beads backend` before being reverted on 2026-05-03:

---

### Feature: Optional beads backend

**What.** Add optional support for the [beads](https://github.com/gastownhall/beads) ticket backend alongside the existing bees backend. A repo picks one at `/bees-setup` time; the choice persists in CLAUDE.md `## Ticket Backend`. All 11 portable-core skills work transparently on either backend without per-backend skill edits. Both backends cannot coexist in a single repo.

**Why.** Beads is Dolt-backed (version-controlled SQL, native multi-writer, designed for distributed AI agents) — structurally different from bees' file-based ticket model. Some users prefer one, some the other, depending on their concurrency and sync needs. Backend-pluggable extends the project's existing language-agnostic and OS-agnostic portability principles to ticket-system-agnostic. Forcing a single backend forecloses on a real audience.

**Acceptance criteria.**

- Both bees and beads work as backends. The chain `/bees-setup` → `/bees-plan` → `/bees-breakdown-epic` → `/bees-execute` → `/bees-fix-issue` runs end-to-end to `done` on each.
- CLAUDE.md `## Ticket Backend` is a new contract section with values `bees` or `beads`. Skills hard-fail with `Run /bees-setup first.` when the section is missing — matching the existing pattern for `## Documentation Locations` and `## Build Commands`.
- Status vocabulary preserved verbatim on both backends: `drafted` / `ready` / `in_progress` / `done` for plans; `open` / `done` for issues.
- Spec pointer (PRD/SDD egg) preserved on both backends. On beads, the resolver runs skill-side rather than CLI-registered.
- README updated: intro, Requirements, Why-this-exists bullets, Status-vocabulary column header, `/bees-setup` description, plus a new "Ticket backend" section between "After install" and "The skills."

**Out of scope.**

- Migration of an existing bees-set-up repo to beads (or vice versa). Greenfield-only.
- Modifications to beads itself, or to bees solely for dual-backend users.
- Beads' multi-repo / cross-repo aggregation features (`repos.additional`, `routing.mode auto`).
- Running both backends in the same repo simultaneously.

## Recovered SDD content

Was at `docs/sdd.md` `## Per-feature design` `### Feature: Optional beads backend` before being reverted on 2026-05-03:

---

### Feature: Optional beads backend

**Architecture.** A new `skills/_shared/scripts/ticket_backend.py` dispatcher is the single point of contact between skill prose and a backend CLI. It exposes verb-shaped subcommands — `query`, `create`, `update`, `show`, `list-spaces`, `setup-spaces`, `resolve-spec` — and dispatches to either bees or beads based on the `## Ticket Backend` value in CLAUDE.md. The dispatcher emits stable JSON regardless of backend; skills consume that JSON directly.

**New contract section.** CLAUDE.md gains a third contract section, `## Ticket Backend`, with values `bees` or `beads`. `/bees-setup` writes it; every other skill reads it as the first step of any ticket operation. Missing section produces the same `Run /bees-setup first.` hard-fail as the existing two contract sections.

**Backend-specific topology.**

- **bees backend** preserves the current model: two on-disk hives (`Plans`, `Issues`) registered in `~/.bees/config.json`, each with the `file_list_resolver.py` egg-resolver path and the existing tier/status vocabularies set via `bees set-types` / `bees set-status-values`.
- **beads backend** uses two beads databases under the repo: `.beads-plans/dolt/` with `issue_prefix=plan-` and `.beads-issues/dolt/` with `issue_prefix=iss-`. Skills address them via the dispatcher, which composes `bd --db <path> ...` calls. Per-database `config.yaml` carries the custom status vocabulary (`drafted:active,ready:active,done:done` on plans; `done:done` on issues — `open` and `in_progress` are built-in). Tier semantics live in labels: every ticket gets `tier:bee` / `tier:t1` / `tier:t2` / `tier:t3` at create-time, used in queries that bees-side use `type=` for.

**Egg resolver location shift.** Bees registers `file_list_resolver.py` as a hive's `egg_resolver` and the bees CLI invokes it on every read. Beads has no such hook. The dispatcher's `resolve-spec` verb runs `file_list_resolver.py` skill-side when the backend is beads. The resolver script itself doesn't change; only its invocation path does.

**`bees-setup` SKILL.md structure.** Retains its overall flow but gains a backend-pick step at the top (auto-detect from on-disk markers if present; prompt otherwise) and backend-conditional sections for prerequisites, fast-path detection, and ticket-space creation. The egg-resolver subsection runs only when backend=bees. Roughly 40% of the skill body becomes backend-conditional (mostly delegated to the dispatcher's `setup-spaces` verb to keep prose lean); the remaining 60% (Agent Teams, teammateMode, Documentation Locations, PRD/SDD bootstrap, Build Commands) is unchanged.

**Skill prose pattern.** Skills currently shell out to `bees ...` directly in OS-paired POSIX/PowerShell snippets. Post-refactor, every backend-touching command becomes a single `python3 "<base-dir>/.../_shared/scripts/ticket_backend.py" <verb> ...` call. The verb arguments and JSON output shape are stable across backends. Skill prose stays thinner; the dispatcher absorbs the backend-specific shell composition.

**Helper script directory.** A new `skills/_shared/scripts/` directory holds cross-skill helpers — `ticket_backend.py` plus any backend-specific submodules. Resolved at runtime from the invoking skill's base directory plus a `../_shared/scripts/` relative jump, consistent with the existing per-skill scripts pattern.

**Sequencing.** The work decomposes into two Epics. Epic A introduces the dispatcher and routes all skill bees-CLI calls through it as a pure refactor — bees remains the only supported backend, no user-visible change. Epic B adds the beads adapter inside the dispatcher, the backend-pick step in `bees-setup`, the `## Ticket Backend` contract section, the new README content, and the `tier:bee`/`tier:t1`/etc. labeling at create-time on both backends.
