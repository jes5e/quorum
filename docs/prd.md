# bees-workflow — Product Requirements

## Existing scope

bees-workflow is a portable Claude Code skill set for engineers who want an end-to-end SDLC running on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Distributed as markdown skills plus a small number of Python helpers and installed into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (per-project), the skills are invoked via `/<skill>` slash commands inside Claude Code. The project is open-source under MIT license and is in active maintenance.

## Why

bees-workflow exists as an alternative to [Apiary](https://github.com/gabemahoney/apiary), the original bees skill set. Apiary remains a great fit for many projects; bees-workflow is shaped by a different set of priorities:

- **Cumulative project-level docs.** The project requirements doc (PRD) and internal architecture docs (SDD) named under CLAUDE.md `## Documentation Locations` accumulate sections as features ship, and become the source of truth that agents (`bees-execute`, `bees-fix-issue`) read for spec-drift detection. `/bees-setup` can bootstrap baseline docs from an existing codebase via guided Q&A. At plan time, `/bees-plan` does not mutate the project-level PRD/SDD — per-feature spec content lives as Spec Bee `t1=Doc` children referenced from the Plan Bee. Cumulative project-level entries are appended post-implementation by the `doc-writer` agent so the on-disk docs reflect what actually shipped. `/bees-plan-from-specs --feature "<title>"` retains an express path for users who already maintain finalized cumulative PRD/SDD files on disk.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md contract keys, then read by skills at runtime — no skill-editing needed when switching projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet in skill prose ships as labeled OS-conditional blocks; the helper scripts that need cross-platform filesystem behavior ship as Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`; spec-hive bees use `drafted` / `ready`. No translation layer or insect-metaphor jargon to remember.
- **Two entry points.** `/bees-plan` is the interactive scope-discovery path — used both for ideas without finalized specs and for new features being added to an already-cumulative PRD/SDD. It authors per-feature PRD and SDD content as Spec Bee `t1=Doc` children attached to the Plan Bee rather than mutating the project-level docs at plan time; the cumulative on-disk entries are appended post-implementation by the `doc-writer` agent. `/bees-plan-from-specs` is the express path when a finalized **single-feature** PRD and SDD already exist on disk; it hard-fails on multi-feature cumulative docs to avoid re-planning previously-planned features. Experienced users with finalized cumulative specs can also pass `/bees-plan-from-specs --feature "<title>"` to scope an express re-plan to a single `### Feature:` subsection inside the cumulative docs. Both entry points produce the same Plan Bee shape.
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

### Feature: Side-effect-free /bees-plan and /bees-file-issue with preserved context

**What.** Redesign `/bees-plan` and `/bees-file-issue` so that neither skill mutates the project's cumulative PRD, SDD, or README at plan time or filing time, and so that the rich context of pre-skill-invocation conversations is preserved end-to-end through downstream execution agents. Per-feature spec content is now authored as `t1=Doc` children (PRD and SDD, differentiated by exact title-match) of a new top-level Spec Bee in a new **Specs** hive; the Plan Bee's `reference_materials` field points at the Spec Bee via a new `bees` resolver of the form `[{"value":"<spec-bee-id>","resolver":"bees"}]`. Two new composable sub-skills — `/bees-write-prd` and `/bees-write-sdd` — author and revise the per-feature PRD/SDD ticket bodies; `/bees-plan` invokes them inline via the Skill tool when initial specs are being authored, and they remain solo-invokable for later revisions (`/bees-write-prd <spec-bee-id>`). The cumulative project-level PRD/SDD continue to exist but are appended to *after-the-fact* by the `doc-writer` agent during execution, reflecting what was actually built rather than forward intent. `/bees-file-issue` is mid-conversation aware (no re-asking discovery questions when context already exists) and supports optional `## Background and rationale` and `## Decisions and rejected alternatives` sections in the body template; doc-divergence observations are now captured in a `## Doc divergence noted` section in the Issue body for `/bees-fix-issue`'s doc-writer to act on, rather than mutating docs at filing time.

**Why.** Three classes of problem motivated the redesign. (1) Drafting a plan that may never execute — or won't execute for weeks — was writing future-state design into project docs that nominally describe current behavior, with manual and error-prone reverts; parallel planning compounded the problem by layering future state for two unbuilt features on top of one another. (2) The "every session is cold" principle forced thorough planning conversations through a "2-3 sentence summary" funnel into the Plan Bee body, losing rationale, rejected alternatives, and constraints; downstream PM agents and engineers re-litigated decisions or re-introduced rejected approaches because no record survived. (3) `/bees-file-issue` had a smaller analog of both — Step 4 mutated docs at filing time when an issue surfaced doc divergence, and the body's shallow template lost the analytical depth of the originating discussion.

**Acceptance criteria.**

- `/bees-plan` no longer writes to the cumulative PRD, SDD, or README. Running it on a Plan that's never executed leaves project docs untouched.
- `/bees-plan` creates a Spec Bee with PRD and SDD `t1=Doc` child tickets, plus a Plan Bee with Epic children whose `reference_materials` is `[{"value":"<spec-bee-id>","resolver":"bees"}]`.
- `/bees-write-prd` and `/bees-write-sdd` exist as composable sub-skills — invokable solo for spec revisions and inline by `/bees-plan` for initial authoring.
- `/bees-plan` distills pre-invocation conversation context into the PRD/SDD child tickets when invoked mid-conversation, instead of restarting discovery from scratch.
- PRD and SDD child-ticket bodies include explicit sections for decisions, rejected alternatives, and rationale — not just requirements.
- `agents/pm.md` and `skills/bees-breakdown-epic/SKILL.md` perform two-hop lookup: read `reference_materials`, follow the `bees` resolver to the Spec Bee, walk the Spec Bee's `t1=Doc` children for PRD/SDD content. The existing `file-path` resolver path and the body-as-spec fallback (when `reference_materials` is null/empty) remain functional.
- `agents/doc-writer.md` is responsible for appending or updating `### Feature: <title>` subsections in the cumulative project PRD and SDD post-implementation, reflecting what was actually built.
- `/bees-file-issue` Step 4 no longer mutates docs; doc-divergence observations are captured in a `## Doc divergence noted` section in the Issue body for `/bees-fix-issue`'s doc-writer to act on.
- `/bees-file-issue` is mid-conversation aware and supports optional `## Background and rationale` / `## Decisions and rejected alternatives` body sections.
- `/bees-setup` colonizes the Specs hive on new repos and detect-and-adds it on existing repos; `/bees-execute`, `/bees-fix-issue`, and `/bees-breakdown-epic` hard-fail with `Run /bees-setup first.` (with a trailing `— Specs hive is not colonized for this repo.` clause) when the Specs hive is missing.
- `/bees-plan-from-specs` continues to work unchanged for the file-based PRD/SDD path, including the `--feature "<title>"` cumulative-spec scoping flow. The Scoped-marker / `scoped_marker_resolver.py` infrastructure is retained — only `/bees-plan` no longer emits markers (because it no longer co-mingles feature content into shared cumulative docs).

**Out of scope.**

- A `/bees-spec-review` quality-review pass over PRD/SDD ticket bodies, parallel to `/bees-code-review`, `/bees-test-review`, `/bees-doc-review`. Useful eventually, but separable from the bug fix this feature delivers — deferred to a follow-up Issue.
- A `/bees-file-issue --from-github <url>` (or generic `--reference <url>`) external-reference mode symmetric with `/bees-plan-from-specs`. Real gap, but separable from this feature — deferred to a follow-up Issue.
- Migrating the existing Plan Bees `b.5tm`, `b.9xr`, `b.gar`, `b.kw3` to the new Spec Bee structure. They remain on the old shape; the new flow applies forward.
- Building a GitHub-issue resolver or any other new resolver. The design accommodates them via the existing `reference_materials` abstraction; concrete resolvers are separate work.
- A formal Issue-to-Plan promotion path. The manual workaround (close the Issue, file a Plan referencing it) remains.

### Feature: Add /bees-spec-review skill (apiary /req-review analog)

**What.** Add a `/bees-spec-review` skill that performs a fresh-eyes review pass over the PRD and SDD ticket bodies authored by `/bees-write-prd` and `/bees-write-sdd` under a Spec Bee. Mirrors the shape of the existing `/bees-code-review`, `/bees-doc-review`, and `/bees-test-review` skills (severity-tagged work-item list, dual-mode standalone vs orchestrator-invoked). Apiary's `/req-review` is the conceptual analog. Default scope reviews both the PRD `t1=Doc` child and the SDD `t1=Doc` child; `--doc PRD` or `--doc SDD` narrows to one child. The skill does not mutate any ticket — it returns a list of improvement work items for the caller (human or orchestrator) to act on.

**Why.** The "Side-effect-free /bees-plan and /bees-file-issue with preserved context" feature (`b.31f`) deferred this work to observe real failure modes from `/bees-write-prd` and `/bees-write-sdd` output before building the reviewer. With those skills now in steady use, this skill closes the four-reviewer parallel (`/bees-code-review`, `/bees-doc-review`, `/bees-test-review`, `/bees-spec-review`) and provides a quality gate for Spec Bee `drafted → ready` transitions when spec-authoring or planning skills wire it in as a post-write hook. Standalone use also serves ad-hoc spec-review needs after revisions.

**Acceptance criteria.**

- `skills/bees-spec-review/SKILL.md` exists with frontmatter `name: bees-spec-review` and a precise `description` covering both standalone and orchestrator-invoked modes.
- The skill takes one positional argument `<spec-bee-id>` and one optional flag `--doc PRD|SDD`.
- The skill resolves the Spec Bee's PRD and/or SDD `t1=Doc` children via `bees execute-freeform-query` (regex-anchored exact title match), reads each child's body via `bees show-ticket`, and returns a numbered list of work items in the same severity-tagged shape as the other three review skills (`blocker` / `suggestion` / `nit`).
- The skill carries explicit per-document checklists (PRD: 8 categories tied to the twelve `/bees-write-prd` sections; SDD: 10 categories tied to the seven `/bees-write-sdd` sections) plus a cross-document consistency pass run when both PRD and SDD are in scope.
- The skill does not mutate any ticket; output is text-only.
- The skill hard-fails with `Run /bees-setup first.` when the Specs hive is not colonized.
- README.md skill catalog lists the skill in a row parallel to the other three reviewers, the surrounding "three reviewers" prose is updated to "four reviewers", and the running portable-core skill count is bumped to reflect the new total.

**Out of scope.**

- Wiring `/bees-spec-review` into `/bees-write-prd`, `/bees-write-sdd`, or `/bees-plan` as a post-write gate. The skill is invokable standalone today; orchestrator integration is a separate change those skills can adopt when the integration shape is settled.
- A `## Spec review guide` doc under CLAUDE.md `## Documentation Locations` (parallel to the Test review guide and Doc writing guide entries). The skill's checklists live inline in its `SKILL.md` for now; if a separate guide is warranted later, that's a follow-up.
- Auto-fix or auto-revise behavior — the skill returns findings only, never edits PRD or SDD bodies. The caller decides whether and how to address each finding.
- Spec review of the cumulative project-level PRD/SDD on disk — `/bees-doc-review`'s territory. This skill scopes strictly to Spec Bee `t1=Doc` children.
