# quorum — Product Requirements

## Existing scope

quorum is a portable Claude Code skill set for engineers who want an end-to-end SDLC running on top of [bees](https://github.com/gabemahoney/bees) tickets — plan, break down, execute, review, fix, repeat. Distributed as markdown skills plus a small number of Python helpers and installed into `~/.claude/skills/` (global) or `<repo>/.claude/skills/` (per-project), the skills are invoked via `/<skill>` slash commands inside Claude Code. The project is open-source under MIT license and is in active maintenance.

## Why

quorum exists as an alternative to [Apiary](https://github.com/gabemahoney/apiary), the original bees skill set. Apiary remains a great fit for many projects; quorum is shaped by a different set of priorities:

- **Cumulative project-level docs.** The project requirements doc (PRD) and internal architecture docs (SDD) named under CLAUDE.md `## Documentation Locations` accumulate sections as features ship, and become the source of truth that agents (`quo-execute`, `quo-fix-issue`) read for spec-drift detection. `/quo-setup` can bootstrap baseline docs from an existing codebase via guided Q&A. At plan time, `/quo-plan` does not mutate the project-level PRD/SDD — per-feature spec content lives as Spec Bee `t1=Doc` children referenced from the Plan Bee. Cumulative project-level entries are appended post-implementation by the `doc-writer` agent so the on-disk docs reflect what actually shipped. `/quo-plan-from-specs --feature "<title>"` retains an express path for users who already maintain finalized cumulative PRD/SDD files on disk.
- **Language-agnostic.** Works on Rust, Node, Python, Go, Java, polyglot, or unknown stacks. Stack-specific commands (compile, format, lint, narrow test, full test) are detected at setup and stored in CLAUDE.md contract keys, then read by skills at runtime — no skill-editing needed when switching projects.
- **Cross-platform.** Native macOS, Linux, and Windows PowerShell (or WSL/Git Bash). Every shell snippet in skill prose ships as labeled OS-conditional blocks; the helper scripts that need cross-platform filesystem behavior ship as Python.
- **Plain-English statuses.** Plan-hive bees use `drafted` / `ready` / `in_progress` / `done`; issue-hive bees use `open` / `done`; spec-hive bees use `drafted` / `ready`. No translation layer or insect-metaphor jargon to remember.
- **Two entry points.** `/quo-plan` is the interactive scope-discovery path — used both for ideas without finalized specs and for new features being added to an already-cumulative PRD/SDD. It authors per-feature PRD and SDD content as Spec Bee `t1=Doc` children attached to the Plan Bee rather than mutating the project-level docs at plan time; the cumulative on-disk entries are appended post-implementation by the `doc-writer` agent. `/quo-plan-from-specs` is the express path when a finalized **single-feature** PRD and SDD already exist on disk; it hard-fails on multi-feature cumulative docs to avoid re-planning previously-planned features. Experienced users with finalized cumulative specs can also pass `/quo-plan-from-specs --feature "<title>"` to scope an express re-plan to a single `### Feature:` subsection inside the cumulative docs. Both entry points produce the same Plan Bee shape.
- **Idempotent.** Every state-mutating skill (`quo-setup` especially) detects existing configuration and only prompts where something is missing or the user asks to change it. Re-runs are safe.

## Out of scope

- **tmux-dependent skills in the portable core.** Skills that need terminal session multiplexing (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and live elsewhere as optional later-installs.
- **Stack-specific helpers.** Changelog tooling, license attribution generation, dependency auditing, and similar single-stack utilities are routed to companion repos rather than added to the core.
- **Infrastructure-specific helpers.** Pastebin clients, cloud storage uploaders, and similar platform-coupled features stay out of the core.
- **Replacing Apiary.** quorum lives alongside Apiary, not as a replacement. Users who want Apiary's lightweight, ephemeral-spec, async-team-spawning style should use Apiary.
- **Maintaining a translation layer to legacy bee-themed terminology.** The status rename from `larva` / `pupa` / `worker` / `finished` to `drafted` / `ready` / `in_progress` / `done` is permanent.

## Acceptance criteria (project-level)

- **End-to-end chain works on any supported stack.** On a fresh repo of any supported language (Rust, Node, Python, Go, Java, or unknown), the full chain `/quo-setup` → `/quo-plan` (or `/quo-plan-from-specs`) → `/quo-breakdown-epic` → `/quo-execute` runs to `done` status across all Epics without per-language skill edits.
- **Cumulative-PRD scoping holds end-to-end.** When a Plan Bee is authored via `/quo-plan-from-specs --feature "<title>"` against cumulative PRD/SDD docs, the single-feature scope is enforced through every downstream skill: `/quo-breakdown-epic` decomposes against only the matching `### Feature: <title>` subsection, and the per-Task PM in `/quo-execute` (and the PM role in `/quo-fix-issue` when an Issue derives from a scoped Plan Bee) compares implementation against the scoped subsection only. Other features in the same cumulative docs do not surface as spec drift.

## Per-feature scope

### Feature: Test strategy for the skills repo

**Status: paused as of 2026-05-03.** This feature remains paused; the Ephemeral-Agent Orchestration rewrite (Plan Bee `b.5tm`) shipping on `main` does not auto-unpause it. `b.gar`'s Plan Bee body has now been refreshed to reflect the post-orchestration, bees-only architecture (the "Optional beads backend" feature `b.9xr` and its `ticket_backend.py` dispatcher seam were abandoned, not gating Test strategy any longer), and Layer 2.5 — the backend-equivalence harness — is explicitly deferred there. The acceptance criteria below still describe the originally-planned dual-backend test strategy and will be re-scoped against the refreshed `b.gar` body when this feature resumes.

**What.** Add a layered test strategy for the quorum repo itself. Three layers — Layer 1 (pytest unit tests on every bundled Python helper), Layer 2 (a structural linter validating each `SKILL.md` against the project's design rules), and Layer 2.5 (a backend-equivalence harness running the same dispatcher operations through both bees and beads and asserting equivalent state). All three layers wire to a single `make test` entrypoint. Layer 3 (live Claude Code end-to-end smoke) is explicitly out of scope.

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

### Feature: Side-effect-free /quo-plan and /quo-file-issue with preserved context

**What.** Redesign `/quo-plan` and `/quo-file-issue` so that neither skill mutates the project's cumulative PRD, SDD, or README at plan time or filing time, and so that the rich context of pre-skill-invocation conversations is preserved end-to-end through downstream execution agents. Per-feature spec content is now authored as `t1=Doc` children (PRD and SDD, differentiated by exact title-match) of a new top-level Spec Bee in a new **Specs** hive; the Plan Bee's `reference_materials` field points at the Spec Bee via a new `bees` resolver of the form `[{"value":"<spec-bee-id>","resolver":"bees"}]`. Two new composable sub-skills — `/quo-write-prd` and `/quo-write-sdd` — author and revise the per-feature PRD/SDD ticket bodies; `/quo-plan` invokes them inline via the Skill tool when initial specs are being authored, and they remain solo-invokable for later revisions (`/quo-write-prd <spec-bee-id>`). The cumulative project-level PRD/SDD continue to exist but are appended to *after-the-fact* by the `doc-writer` agent during execution, reflecting what was actually built rather than forward intent. `/quo-file-issue` is mid-conversation aware (no re-asking discovery questions when context already exists) and supports optional `## Background and rationale` and `## Decisions and rejected alternatives` sections in the body template; doc-divergence observations are now captured in a `## Doc divergence noted` section in the Issue body for `/quo-fix-issue`'s doc-writer to act on, rather than mutating docs at filing time.

**Why.** Three classes of problem motivated the redesign. (1) Drafting a plan that may never execute — or won't execute for weeks — was writing future-state design into project docs that nominally describe current behavior, with manual and error-prone reverts; parallel planning compounded the problem by layering future state for two unbuilt features on top of one another. (2) The "every session is cold" principle forced thorough planning conversations through a "2-3 sentence summary" funnel into the Plan Bee body, losing rationale, rejected alternatives, and constraints; downstream PM agents and engineers re-litigated decisions or re-introduced rejected approaches because no record survived. (3) `/quo-file-issue` had a smaller analog of both — the former filing-time doc-mutation step (since folded into the body-authoring step's optional `## Doc divergence noted` capture) mutated `docs/prd.md` / `docs/sdd.md` when an issue surfaced doc divergence, and the body's shallow template lost the analytical depth of the originating discussion.

**Acceptance criteria.**

- `/quo-plan` no longer writes to the cumulative PRD, SDD, or README. Running it on a Plan that's never executed leaves project docs untouched.
- `/quo-plan` creates a Spec Bee with PRD and SDD `t1=Doc` child tickets, plus a Plan Bee with Epic children whose `reference_materials` is `[{"value":"<spec-bee-id>","resolver":"bees"}]`.
- `/quo-write-prd` and `/quo-write-sdd` exist as composable sub-skills — invokable solo for spec revisions and inline by `/quo-plan` for initial authoring.
- `/quo-plan` distills pre-invocation conversation context into the PRD/SDD child tickets when invoked mid-conversation, instead of restarting discovery from scratch.
- PRD and SDD child-ticket bodies include explicit sections for decisions, rejected alternatives, and rationale — not just requirements.
- `agents/pm.md` and `skills/quo-breakdown-epic/SKILL.md` perform two-hop lookup: read `reference_materials`, follow the `bees` resolver to the Spec Bee, walk the Spec Bee's `t1=Doc` children for PRD/SDD content. The existing `file-path` resolver path and the body-as-spec fallback (when `reference_materials` is null/empty) remain functional.
- `agents/doc-writer.md` is responsible for appending or updating `### Feature: <title>` subsections in the cumulative project PRD and SDD post-implementation, reflecting what was actually built.
- The doc-divergence step in `/quo-file-issue` that previously mutated `docs/prd.md` / `docs/sdd.md` at filing time no longer mutates docs (in the post-redesign flow it is folded into the body-authoring step's optional `## Doc divergence noted` capture); doc-divergence observations are captured in a `## Doc divergence noted` section in the Issue body for `/quo-fix-issue`'s doc-writer to act on.
- `/quo-file-issue` is mid-conversation aware and supports optional `## Background and rationale` / `## Decisions and rejected alternatives` body sections.
- `/quo-setup` colonizes the Specs hive on new repos and detect-and-adds it on existing repos; `/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` hard-fail with `Run /quo-setup first.` (with a trailing `— Specs hive is not colonized for this repo.` clause) when the Specs hive is missing.
- `/quo-plan-from-specs` continues to work unchanged for the file-based PRD/SDD path, including the `--feature "<title>"` cumulative-spec scoping flow. The Scoped-marker / `scoped_marker_resolver.py` infrastructure is retained — only `/quo-plan` no longer emits markers (because it no longer co-mingles feature content into shared cumulative docs).

**Out of scope.**

- A `/quo-spec-review` quality-review pass over PRD/SDD ticket bodies, parallel to `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`. Useful eventually, but separable from the bug fix this feature delivers — deferred to a follow-up Issue.
- A `/quo-file-issue --from-github <url>` (or generic `--reference <url>`) external-reference mode symmetric with `/quo-plan-from-specs`. Real gap, but separable from this feature — deferred to a follow-up Issue.
- Migrating the existing Plan Bees `b.5tm`, `b.9xr`, `b.gar`, `b.kw3` to the new Spec Bee structure. They remain on the old shape; the new flow applies forward.
- Building a GitHub-issue resolver or any other new resolver. The design accommodates them via the existing `reference_materials` abstraction; concrete resolvers are separate work.
- A formal Issue-to-Plan promotion path. The manual workaround (close the Issue, file a Plan referencing it) remains.

### Feature: Add /quo-spec-review skill (apiary /req-review analog)

**What.** Add a `/quo-spec-review` skill that performs a fresh-eyes review pass over the PRD and SDD ticket bodies authored by `/quo-write-prd` and `/quo-write-sdd` under a Spec Bee. Mirrors the shape of the existing `/quo-engineer-review`, `/quo-doc-writer-review`, and `/quo-test-writer-review` skills (severity-tagged work-item list shape; the existing three are now orchestrator-only while `/quo-spec-review` remains dual-mode). Apiary's `/req-review` is the conceptual analog. Default scope reviews both the PRD `t1=Doc` child and the SDD `t1=Doc` child; `--doc PRD` or `--doc SDD` narrows to one child. The skill does not mutate any ticket — it returns a list of improvement work items for the caller (human or orchestrator) to act on.

**Why.** The "Side-effect-free /quo-plan and /quo-file-issue with preserved context" feature (`b.31f`) deferred this work to observe real failure modes from `/quo-write-prd` and `/quo-write-sdd` output before building the reviewer. With those skills now in steady use, this skill closes the four-reviewer parallel (`/quo-engineer-review`, `/quo-doc-writer-review`, `/quo-test-writer-review`, `/quo-spec-review`) and provides a quality gate for Spec Bee `drafted → ready` transitions when spec-authoring or planning skills wire it in as a post-write hook. Standalone use also serves ad-hoc spec-review needs after revisions.

**Acceptance criteria.**

- `skills/quo-spec-review/SKILL.md` exists with frontmatter `name: quo-spec-review` and a precise `description` covering both standalone and orchestrator-invoked modes.
- The skill takes one positional argument `<spec-bee-id>` and one optional flag `--doc PRD|SDD`.
- The skill resolves the Spec Bee's PRD and/or SDD `t1=Doc` children via `bees execute-freeform-query` (regex-anchored exact title match), reads each child's body via `bees show-ticket`, and returns a numbered list of work items in the same severity-tagged shape as the other three review skills (`blocker` / `suggestion` / `nit`).
- The skill carries explicit per-document checklists (PRD: 8 categories tied to the twelve `/quo-write-prd` sections; SDD: 10 categories tied to the seven `/quo-write-sdd` sections) plus a cross-document consistency pass run when both PRD and SDD are in scope.
- The skill does not mutate any ticket; output is text-only.
- The skill hard-fails with `Run /quo-setup first.` when the Specs hive is not colonized.
- README.md skill catalog lists the skill in a row parallel to the other three reviewers, the surrounding "three reviewers" prose is updated to "four reviewers", and the running portable-core skill count is bumped to reflect the new total.

**Out of scope.**

- Wiring `/quo-spec-review` into `/quo-write-prd`, `/quo-write-sdd`, or `/quo-plan` as a post-write gate. The skill is invokable standalone today; orchestrator integration is a separate change those skills can adopt when the integration shape is settled.
- A `## Spec review guide` doc under CLAUDE.md `## Documentation Locations` (parallel to the Test review guide and Doc writing guide entries). The skill's checklists live inline in its `SKILL.md` for now; if a separate guide is warranted later, that's a follow-up.
- Auto-fix or auto-revise behavior — the skill returns findings only, never edits PRD or SDD bodies. The caller decides whether and how to address each finding.
- Spec review of the cumulative project-level PRD/SDD on disk — `/quo-doc-writer-review`'s territory. This skill scopes strictly to Spec Bee `t1=Doc` children.

### Feature: /quo-file-issue: add --reference URL mode for external sources (GitHub, Linear, etc.)

**What.** Add an external-reference invocation mode to `/quo-file-issue` symmetric with `/quo-plan-from-specs` on the planning side. The skill now accepts `--reference <url>` (generic) or `--from-github <url>` (friendlier alias for the GitHub Issues case) alongside the existing in-conversation capture path. In external-reference mode, the Issue body is a thin 2-3 sentence summary and `reference_materials` carries `[{"value":"<url>","resolver":"<name>"}]`, where `<name>` is selected by URL pattern (`github-issue` for GitHub Issue URLs, `linear-issue` for Linear ticket URLs, `url` otherwise). Downstream, `/quo-fix-issue`'s Engineer and PM fetch the upstream content via `WebFetch` and treat it as the spec source — the bees CLI does not yet ship concrete resolver implementations for these names, so the canonical resolver name is written regardless and a real resolver can land later without migrating existing Issue tickets.

**Why.** Today's `/quo-file-issue` only supports the in-conversation capture path: the user describes a bug interactively, the skill creates an Issue with body-as-spec content. This is right for in-conversation discoveries, but it's a gap when the user already has the bug described elsewhere — a GitHub Issue, a Linear ticket, a Slack thread, an internal bug tracker — and just wants quorum to point at it. The redesign work shipped under `b.31f` ("Side-effect-free /quo-plan and /quo-file-issue with preserved context") explicitly deferred this external-reference capability to a follow-up Issue because folding it in would have expanded scope without addressing the original problem any better. This Issue closes that gap, completing the symmetry between the planning side (`/quo-plan` for in-conversation, `/quo-plan-from-specs` for external-reference) and the issue side (`/quo-file-issue` default for in-conversation, `/quo-file-issue --reference` for external-reference).

**Acceptance criteria.**

- `/quo-file-issue --reference <url>` and `/quo-file-issue --from-github <url>` are first-class invocation modes alongside the default in-conversation capture path; the `argument-hint` advertises all three forms (`[<description> | --reference <url> | --from-github <url>]`).
- When an external-reference flag is present, the skill skips the body-template authoring step (Description / Current behavior / Expected behavior / Impact / Suggested fix) and instead writes a thin body containing a single `External reference: <source-class> <url>` convention line plus a 2-3 sentence summary distilled from prior conversation, `WebFetch`-fetched URL content, or — as a last resort — a user-supplied prose summary.
- The skill writes `reference_materials` as `[{"value":"<url>","resolver":"<name>"}]` where `<name>` is `github-issue` for GitHub Issue URLs, `linear-issue` for Linear ticket URLs, and `url` otherwise (URL-pattern heuristic, host-then-path).
- `/quo-fix-issue`'s dispatch prompt embeds the Issue's `reference_materials` JSON value alongside the (thin) body when the field is non-empty, so the worker can read the resolver name and URL.
- The Engineer and PM subagents (`agents/engineer.md`, `agents/pm.md`) fetch the upstream content via `WebFetch` when `reference_materials` carries an external-URL resolver and treat the fetched content as the spec source; both have `WebFetch` in their tool allowlists.
- The README skill catalog row for `/quo-file-issue` documents both invocation modes and explicitly names the external-URL resolvers and the `WebFetch` fallback.
- The `Reference materials` entry in `docs/doc-writing-guide.md` `## Project terminology` lists external-URL resolvers as a third resolver class alongside `file-path` and `bees`.

**Out of scope.**

- Building specific external resolvers (a real `github-issue` resolver, a real `linear-issue` resolver, a generic `url` resolver) in the bees CLI — those are separate Issues filed against `bees` itself or `quorum` as their owners materialize. This Issue establishes the canonical resolver names and the `WebFetch` fallback path; concrete resolver implementations land independently.
- Migrating existing in-conversation-filed Issues to external-reference mode.
- Promoting an Issue to a Plan Bee — the manual workaround (close Issue, file Plan referencing it) remains for now.
- An `--from-linear` / `--from-jira` / per-source CLI alias for every external bug tracker. The current set is `--reference` (generic) plus `--from-github` (alias). Any future per-source aliases fold into the same code path; the resolver-name selection in the URL-pattern heuristic is what differentiates them downstream.

### Feature: Wire /quo-spec-review into /quo-plan, /quo-write-prd, /quo-write-sdd as automatic quality gate

**What.** Wire the previously-standalone `/quo-spec-review` skill into the spec-authoring flow as an automatic quality gate at three sites: `/quo-plan` (post both writer-skill invocations, pre Spec Bee promotion), `/quo-write-prd` invoked solo (post the Step 6 user-approval gate, pre the PRD child's `drafted → ready` promotion), and `/quo-write-sdd` invoked solo (post the Step 7 user-approval gate, pre the SDD child's `drafted → ready` promotion). When a writer is invoked inline from `/quo-plan` it skips its own per-writer review — Site 1 covers both children plus the cross-document consistency pass end-to-end. The skill's frontmatter description and SKILL.md prose now name orchestrator-invoked use as the primary path; standalone use remains supported for ad-hoc spec audits.

**Why.** The "Add /quo-spec-review skill" feature shipped the reviewer as standalone-only — its `## Out of scope` list explicitly deferred orchestrator integration to a separate change "when the integration shape is settled". In practice that meant the quality gate only fired when humans remembered to type `/quo-spec-review` after authoring or revising specs, which is half a feature: PRDs and SDDs were promoting `drafted → ready` (and being consumed by downstream `/quo-breakdown-epic`, `/quo-execute`, and `/quo-fix-issue`) without any fresh-eyes review pass. Auto-invocation closes that gap and brings the spec side into line with the code/doc/test side, where `/quo-execute` and `/quo-fix-issue` already auto-run their reviewers.

**Acceptance criteria.**

- `/quo-plan` invokes `/quo-spec-review <spec-bee-id>` (no `--doc` flag) after Step 4b's writer-skill invocations and before Step 4c's Spec Bee `drafted → ready` promotion. Both children plus the cross-document consistency pass run in this single end-to-end review.
- `/quo-write-prd <spec-bee-id>` invoked solo runs `/quo-spec-review <spec-bee-id> --doc PRD` after Step 6's user approval and before the PRD child's `drafted → ready` promotion.
- `/quo-write-sdd <spec-bee-id>` invoked solo runs `/quo-spec-review <spec-bee-id> --doc SDD` after Step 7's user approval and before the SDD child's `drafted → ready` promotion.
- `/quo-write-prd` and `/quo-write-sdd` invoked inline from `/quo-plan` skip the per-writer review (Site 1 in `/quo-plan` covers it end-to-end) so a single planning run does not pay for two redundant reviews.
- Findings are surfaced to the user via `AskUserQuestion` with severity-aware default options (Revise / Proceed (acknowledge findings) / Proceed anyway (override blockers)). The Recommended option flips with severity — `blocker`-only findings recommend Revise; `suggestion`/`nit`-only findings recommend Proceed.
- Blockers gate `drafted → ready` by default; the override path is supported but recorded in the end-of-skill report so the user has a single view of what was intentionally not addressed before promotion.
- The review-fix-review loop applies a time-budget short-circuit after roughly 10 surfaced items or 3 review turns, mirroring the bound the other three reviewers already enforce in `/quo-execute` / `/quo-fix-issue`.
- `/quo-spec-review`'s frontmatter description and SKILL.md prose reflect that orchestrator-invoked use is now the primary path; standalone use is documented as the secondary path.
- README.md skill-table row for `/quo-spec-review` and the surrounding "four reviewers" prose are updated to drop the "once those wire it in" qualifier and name the three orchestrators that auto-invoke the skill. The workflow diagram annotates the auto-gate inline in the `/quo-plan` branch.

**Out of scope.**

- Wiring `/quo-spec-review` into `/quo-plan-from-specs`. The express path consumes finalized PRD/SDD content from on-disk files, not a Spec Bee's `t1=Doc` children — there is no Spec Bee parent for `/quo-spec-review` to scope to. Spec quality on that path is the user's responsibility before invoking the skill.
- Auto-revising PRD or SDD bodies in response to findings. The reviewer remains text-only; the writer-skill loop-back path is the mechanism for applying findings.
- Persisting overridden-blocker decisions to the PRD or SDD bodies. The end-of-skill report captures them for the user; downstream skills do not read this metadata.
- Changing the severity ladder, checklist contents, or output shape of `/quo-spec-review` itself. The skill's review logic is unchanged — only the invocation surface is.

### Feature: Auto-detect URLs in /quo-file-issue and /quo-fix-issue (no flag required)

**What.** Bare URL tokens (`^https?://`) are now accepted as first-class positional arguments to both `/quo-file-issue` and `/quo-fix-issue`, alongside the existing flag-based forms. URL detection is automatic at argument tokenization — no `--reference` or `--from-github` flag required. `/quo-file-issue <url>` routes to the existing External-reference branch and produces an Issue identical in shape to today's `/quo-file-issue --reference <url>` (thin body with the `External reference:` convention line, `reference_materials: [{"value":"<url>","resolver":"<name>"}]` where `<name>` comes from the existing URL-pattern resolver-name table — `github-issue` / `linear-issue` / `url`). `/quo-fix-issue <url>` files the URL via `/quo-file-issue` (Skill-tool dispatch) and runs the per-issue fix flow against the resolved ticket; `/quo-fix-issue` list mode supports mixed `<id>` + `<url>` argument lists and substitutes URL tokens *in place* in the working list so the user-supplied prerequisite ordering survives. Existing flag forms (`--reference <url>`, `--from-github <url>`) continue to work unchanged as silent no-op aliases on top of detection. A new dedupe path queries open Issues by `reference_materials.value` before filing and surfaces a `Use existing` / `File new` / `Cancel` `AskUserQuestion` on a hit, so re-running `/quo-fix-issue <url>` after a failed run does not silently mint a duplicate Issue.

**Why.** The flag-required model from the previous `/quo-file-issue` external-reference feature was friction: a URL in argument position is unambiguous, no other plausible interpretation exists, and forcing the user to remember `--reference` or `--from-github` is documentation noise. The two-step manual workflow when starting from a URL (file the Issue first, capture the ID, then invoke `/quo-fix-issue <id>`) was the dominant friction point as quorum is adopted into projects with external trackers (GitHub Issues, Linear tickets, Slack archive links, internal bug-tracker URLs) — the URL is the natural artifact to hand to the workflow, and any friction at that boundary translated directly into adoption friction. This feature closes that gap and makes URL-tracker entry points first-class on both issue-side skills.

**Acceptance criteria.**

- `/quo-file-issue https://github.com/owner/repo/issues/123` (no flag) produces an Issue identical in shape to today's `/quo-file-issue --reference <url>`: thin body with the `External reference:` line, `reference_materials` set to `[{"value":"https://github.com/owner/repo/issues/123","resolver":"github-issue"}]`, status=`open`.
- `/quo-file-issue --reference <url>` and `/quo-file-issue --from-github <url>` continue to work — flags accepted as backward-compat no-ops, producing identical Issue shapes to the bare-URL path.
- `/quo-fix-issue https://github.com/owner/repo/issues/123` (no flag) files the Issue (or reuses an existing match per dedupe), then runs the per-issue fix flow end-to-end, producing one git commit on the chosen branch.
- `/quo-fix-issue b.cnb https://github.com/owner/repo/issues/123 b.xet` processes three items in the user-supplied order. The URL token at position 2 becomes a new ticket ID (call it `b.<new>`); the working list resolves to `[b.cnb, b.<new>, b.xet]` and is processed sequentially.
- Before filing a URL, the skill queries open Issues for one whose `reference_materials.value` matches the URL. On a hit, the skill surfaces the existing ticket via `AskUserQuestion` with `Use existing` / `File new` / `Cancel` choices. The matched ticket's ID, title, and status appear in the prompt body so the user can decide intelligently. On multiple matches, all candidates are surfaced with one `Use existing (b.<id>)` option per candidate plus `File new` and `Cancel`.
- Resolver name selection uses the existing URL-pattern table in `quo-file-issue/SKILL.md` — no copy of the table appears in `quo-fix-issue/SKILL.md`. `/quo-fix-issue` delegates URL filing to `/quo-file-issue` via the published `## Inline invocation via the Skill tool` contract section.
- README skill-table rows for both `/quo-file-issue` and `/quo-fix-issue` mention URL mode in the description column.
- Existing `/quo-file-issue` / `/quo-fix-issue` invocation forms (against bees IDs, against `all` mode, against `--reference` and `--from-github` flags, against in-conversation `<description>` strings) continue to work without modification.

**Out of scope.**

- Implementing concrete bees-CLI resolvers for `github-issue`, `linear-issue`, or `url`. The agent-side `WebFetch` fallback in `agents/engineer.md` and `agents/pm.md` already covers it and remains the canonical fetch path.
- Changes to agent role contracts (`engineer.md`, `pm.md`, `doc-writer.md`, etc.) — they already handle external-URL `reference_materials` end-to-end.
- Adding URL handling to other skills (`/quo-plan`, `/quo-plan-from-specs`, `/quo-execute`, `/quo-breakdown-epic`). This feature is scoped to the issue-filing-and-fixing pair only.
- Removing the `--reference` and `--from-github` flag literals from skill prose. They remain documented as accepted alias forms.
- Changes to the external-reference Issue body shape (thin 2-3 sentence summary, optional `## Doc divergence noted`, `External reference:` convention line, `reference_materials` JSON shape).
- Authentication-gated URL handling (private GitHub Issues, Linear tickets behind SSO). The `WebFetch` fallback path already covers public URLs; auth-gated URLs continue to fall back to the "Ask the user" branch in `/quo-file-issue`'s external-reference flow.
