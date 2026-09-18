# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portable Claude Code **skill set** that runs an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets. The artifacts here are skills (markdown + a few Python helpers) — there is no application to build; the only code with its own tests and lint is the bundled helper scripts (`tests/` via pytest, pyflakes — see `## Build Commands`). Your job, when editing here, is almost always to modify a `SKILL.md` or one of the helper scripts.

End-user docs (install, usage, the skill catalog, the workflow diagram) live in [README.md](README.md) — read it before changing user-facing behavior.

## Repo layout (only what isn't obvious)

- `skills/<name>/SKILL.md` — the skill prose. The frontmatter `name` and `description` are what Claude Code shows the user (some skills also set `argument-hint`, and the loader honors further keys — see CONTRIBUTING.md `## Skill conventions`); the body is the instructions Claude follows when the skill is invoked.
- `skills/<name>/scripts/` — optional cross-platform Python helpers: `quo-setup/scripts/detect_fast_path.py` (new-machine fast-path detection), `quo-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser/scoper, sibling-resolved by `quo-execute` and `quo-fix-issue`), `quo-execute/scripts/hive_commit.py` (hive-path resolution and deferral-encode staging/commit), and `quo-setup/scripts/context_gauge.py` (context-usage gauge producer/reader, plus status-line settings inspection/installation and the opt-out-marker writer).
- `agents/<role>.md` — Claude Code custom-subagents directory. Eight role contracts (`engineer.md`, `test-writer.md`, `doc-writer.md`, `pm.md`, `code-reviewer.md`, `test-reviewer.md`, `doc-reviewer.md`, `analyst.md`) dispatched as ephemeral background Agents by `quo-execute`, `quo-fix-issue`, and `quo-breakdown-epic`. Each file carries YAML frontmatter (`name`, `description`, `model`, `effort`, `tools`) plus the role's Instructions block. (`analyst.md` is dispatched by `quo-fix-issue` on every Issue and by `quo-execute` only on escalation — a design question, a premise check, or an earned chain; `quo-breakdown-epic` dispatches the four implementer/PM roles; the three reviewer roles are dispatched by the two execution skills.)

The full workflow chain — `quo-setup` → (`quo-plan` | `quo-plan-from-specs`) → `quo-breakdown-epic` → `quo-execute` → `quo-file-issue` / `quo-fix-issue` — is documented in the README; don't re-derive it from the skill files.

## The three non-negotiable design rules

These are the contributing principles called out in the README, and they should drive every change you make to a skill:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Never hardcode a language-specific command, file extension, or manifest filename in skill prose. Downstream skills look up project commands from CLAUDE.md (in the *target* repo, not this one) under fixed contract keys.
2. **Skills must work on POSIX and native Windows PowerShell.** Every shell snippet in a `SKILL.md` ships as labeled OS-conditional blocks (POSIX bash + Windows PowerShell at minimum; cmd.exe optional). Helper scripts should be Python (preferred) or come in OS-paired implementations. There is no bash-only fallback.
3. **Skill prose must be project-neutral.** A `SKILL.md` (or any helper script) must not reference *this* repo's paths, ticket IDs, internal workflow specifics, or anything that wouldn't make sense in a different project that installs the skills. Project-specific guidance for downstream users lives in the *target repo's* `CLAUDE.md`, which the skills read at runtime — never baked into the skills themselves. (This file you're reading now is *this* repo's `CLAUDE.md` — guidance here governs work done **on** the skills, but does not get baked **into** them.)

If you're tempted to write `cargo test` or `npm run lint` directly into a skill, stop — use the lookup-key pattern below instead.

## Bash etiquette in this repo

Every Bash tool call in this repo must be a **single literal command** — one binary plus its arguments, nothing else. This applies to *every* Claude instance — team-leads, spawned workers, reviewers, ad-hoc invocations. The `Shell-command etiquette` bullet inside the execution-skill worker prompts (b.6k2 / b.aic) only covers spawned workers; this section covers everyone else.

**Forbidden shapes** (each one trips a different Claude Code matcher and re-prompts the user even on previously-approved repos):

- Compound chains: `cmd1 && cmd2`, `cmd1 || cmd2`, `cmd1 ; cmd2`
- Pipes between commands: `cmd1 | cmd2` (use first-class `Grep` / `Read` tools, or pass match-limit flags like `grep -m N`)
- Redirects mid-chain: `echo X > file && cmd` (use the `Write` tool to create files)
- Diagnostic tails: `; echo exit=$?`, `&& echo done` (the Bash tool already reports exit status)
- Shell variables and expansion: `$VAR`, `${VAR:-default}`, `$?`, `$(...)`, backticks
- Multi-line `-c` or inline heredocs: `python3 -c '<line1>\n<line2>'`
- `unset` / `export` mid-chain
- Backticks inside *double*-quoted strings — bash treats them as command substitution even when they're "obviously" data (e.g., backticks inside a regex like `grep -nE "... \`my_var\` ..."`). The harness's safety matcher reads this as arbitrary-code execution and re-prompts even when `Bash(grep:*)` is allowlisted. Use **single quotes** for any string literal that contains backticks, or escape them as `\` `\``.

**Required shapes:**

- One Bash call per command. Sequence multiple commands as multiple Bash calls (in parallel where independent).
- Pre-set env vars via the shell's `VAR=value command` prefix — still a single literal command, fine.
- For multi-step or variable-bearing logic, write a Python script to a file (use the `Write` tool) and run the file with one Bash call. Bundled-helper precedent: `detect_fast_path.py`, `scoped_marker_resolver.py`.
- For watching state, prefer `Monitor` over polling loops. For reading a file, prefer `Read` over `cat` / `head` / `tail`. For searching files, prefer the first-class `Grep` tool over `grep | head` / `grep | xargs`. For writing files, prefer `Write` over `echo X > file`.

If you find yourself wanting a compound shell shape, the Python-helper-file path or a first-class tool is almost always the right answer.

## Scratch-file convention

When a skill (or a dispatched subagent) needs to author a transient file — `--body-file` payloads for `bees create-ticket` / `bees update-ticket`, ticket-body extracts staged for the Scoped-marker helper, anything else that lives only across the next bees / helper invocation — it MUST follow this convention. This is a **fourth design rule** alongside the three above and is enforceable as a review criterion.

1. **Always write under `<tempdir>/.quorum/`**, where `<tempdir>` is `/tmp` on POSIX and `%TEMP%` on Windows. Resolve via Python's `tempfile.gettempdir()` when a helper is involved, or paired POSIX-bash + PowerShell snippets when inline. **Create the `.quorum` subdirectory if it does not exist** (`mkdir -p` on POSIX, `New-Item -ItemType Directory -Force` on Windows). Picking a literal namespaced subdir (rather than `tempfile.NamedTemporaryFile` with random suffixes inside `<tempdir>` directly) is load-bearing — it lets users find every artifact a workflow created in one well-known place, and it lets reviewers spot stray writes outside the namespace at audit time.
2. **Never delete on any OS.** Skill prose MUST NOT instruct callers to `rm` / `Remove-Item` the scratch file after the bees / helper command exits. The footprint is small (KBs per run, low-MB after heavy use); Linux/macOS clean `/tmp` on a days-to-reboot cadence; Windows users can clean `%TEMP%\.quorum` manually between runs. Eliminating mid-run cleanup avoids permission-prompt churn and leaves artifacts around for debugging when a run crashes.
3. **No `rm`-with-allowlist patterns.** Claude Code permission patterns are prefix-matched against the literal command string, so an allowlist entry like `Bash(rm /tmp/.quorum/**)` would also match `rm /tmp/.quorum/../../etc/something` — a path-traversal-shaped failure surface under prompt injection. Skipping cleanup entirely sidesteps the security question; do not reintroduce a cleanup-with-allowlist design.

Snippet shapes to use verbatim in skill prose (paired POSIX + PowerShell, per design rule 2):

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write to /tmp/.quorum/<name>.md (or similar)
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write to $env:TEMP\.quorum\<name>.md (or similar)
```

Filenames inside the namespace should still be collision-resistant when concurrency is possible (e.g., the existing `bees-body-<short-suffix>.md` and `bees-bee-body-<short-suffix>.md` patterns are fine — just under the new prefix).

**Documented exception — the orchestrators' run-state manifest** (`run-state-*.md`). Its filename is deliberately deterministic (no random suffix, no timestamp) because its reader is the orchestrator itself after a possible compaction, so the path must be recomputable rather than remembered; every such filename leads with the writing skill's own name (so sibling orchestrators never share a manifest even when they key on the same ticket), and each orchestrator skill's `#### Write the run-state manifest` section states the discriminator it appends after that name, why that discriminator is re-derivable, and the collision cases it knowingly accepts. The genuinely-shared **lead statements** of these three sections (the "values that live nowhere else on disk / makes harness compaction survivable" framing sentences, the `<tempdir>/.quorum/` path-boilerplate sentence, the bolded deterministic-filename rule, the bolded snapshot-semantics sentence, and the cross-skill discriminator-rationale sentence) are kept byte-identical across all three because there is no shared downstream carrier, and an edit to any of *those* must be mirrored to all three. The surrounding skill-specific portions legitimately vary and are exempt — most notably the durable-carrier enumeration, which differs in its third carrier because `quo-breakdown-epic` has no compromise tracker, and the per-skill section cross-references (e.g. `quo-breakdown-epic` points its boundary checkpoint at "Section 7", while the two execution skills point their pre-run SHA at "Section 11"). See the fuller manifest-mirror criterion under `## Review criteria for skill changes`.

**Documented exception — the per-session context-usage gauge** (`context-usage-<session_id>.json`, written by `skills/quo-setup/scripts/context_gauge.py`). Its filename is deliberately deterministic because its producer (a status-line command) and its consumer (an execution skill's boundary check, in a different process with no channel to the producer) must compute the same path independently; the `session_id` discriminator is re-derivable on both sides (the status-line payload's `session_id` on the produce side, the session-id environment variable on the read side — live-verified equal), and session-keying is itself the collision guard between concurrent sessions. The accepted collision case is two producers configured for the same session, which would overwrite each other harmlessly (overwrite-per-refresh is the file's normal write mode). One further gauge file rides this same exception: `install-statusline`'s post-write self-check writes `context-usage-quo-setup-self-check.json`, keyed by the reserved literal session id `quo-setup-self-check` (defined once as `SELF_CHECK_SESSION_ID` in `context_gauge.py`) rather than a real session id — the installer needs a synthetic session to exercise the freshly-composed status-line command once and confirm it produces a reading. The id is a fixed literal, not session-derived, because there is no live session to key on at install time; it can never collide with a real session id (no live session is ever named `quo-setup-self-check`); and the file is overwritten on each install run and never deleted by skill prose, exactly like the per-session gauge.

**Documented exception — the context-guard opt-out marker** (`context-guard-opt-out`, written by `/quo-setup`'s optional statusline-producer step when the operator picks the run-unguarded choice). Its filename is deliberately deterministic (no random suffix, no timestamp) for the same reason the gauge-file exception records: the writer (`/quo-setup`, in one session) and the reader (a consumer in a different session and process, with no channel to the writer) must compute the same path independently, and a collision-resistant name would defeat the marker's whole purpose of recording a standing choice. Unlike the gauge's `session_id`, this marker carries **no discriminator at all**, because it records an environment-scoped standing choice rather than a per-session reading — keying it per-session would re-ask the operator every session, which is precisely the friction the opt-out exists to prevent. The accepted collision case is two operators sharing one `<tempdir>`, who then share one opt-out; the accepted durability caveat is that the marker is persistent only within the environment's tempdir lifetime (recorded explicitly in the SDD). The marker is written once and never deleted by skill prose, consistent with the convention's no-cleanup rule — so deleting `<tempdir>/.quorum/` clears the opt-out.

Treat a deterministic name as a defect anywhere else in the namespace.

The customer-facing README documents the per-OS location and tells users the directory is safe to delete **between** runs, with the caveat that deleting it *during* a run destroys the run-state manifest — a carrier of values (the captured run mode, the ordered Issue batch) that nothing regenerates. Deleting the directory also clears any persistent context-guard opt-out marker, which nothing regenerates either — the operator is re-prompted on a subsequent run. Do not duplicate that user-level note inside skill prose, and do not restate it here as an unqualified "safe to delete anytime".

## Review criteria for skill changes

When `quo-engineer-review`, `quo-test-writer-review`, or `quo-doc-writer-review` runs against changes in *this* repo, the three design rules above, the scratch-file convention, and the executable-verb test are mandatory review criteria layered on top of each skill's standard checks. Note: `quo-spec-review` is intentionally excluded from this section because it reviews PRD/SDD bee ticket bodies, not source files in this repo, so the rules below (which target skill-prose and helper-script diffs) do not apply to it. Flag any skill-prose or helper-script change that:

- Hardcodes a language-specific command, file extension, or manifest filename (rule 1).
- Introduces a shell snippet without paired POSIX bash + Windows PowerShell variants, or relies on a bash-only fallback (rule 2).
- References this repo's specific paths, ticket IDs, or internal workflow specifics in a way that would not make sense when the skill is installed in a different project or on a different machine (rule 3). **The shipping boundary is load-bearing here:** the install procedure copies only `skills/*` and `agents/*`, so a *shipped-artifact* reference — from a `skills/*/SKILL.md`, an `agents/*.md`, or a bundled helper script — to a repo-only doc that never ships (`docs/*`, `CONTRIBUTING.md`, or a `CLAUDE.md ## <section>` such as `## Scratch-file convention` or `## AskUserQuestion usage`) DANGLES on a fresh install and is a rule-3 violation; flag it. The fix is to confirm the operative instruction is inlined at the site and sever the dangling cross-repo path, or inline the needed content when it is not. **Contract-key carve-out:** a shipped-artifact reference to `CLAUDE.md ## Documentation Locations` or `CLAUDE.md ## Build Commands` is LEGITIMATE and must NOT be flagged — unlike the repo-only `## <section>` references above (`## Scratch-file convention`, `## AskUserQuestion usage`), these two are the downstream string-contract keys `/quo-setup` writes into the *installing (target)* project's own CLAUDE.md, so they resolve in the target repo after a fresh install rather than dangling. This mirrors the companion test's `ALLOWED_SECTIONS = {Documentation Locations, Build Commands}` allowlist in `tests/test_shipped_artifact_portability.py`, so the human criterion and the mechanical guard agree. **README carve-out:** a `README.md` → `docs/*` link is LEGITIMATE and must NOT be flagged — README is read on GitHub or in a checkout where `docs/` sits alongside it, and README is not installed via `cp -r skills/*`. The concrete accepted instance is README's `### The context-usage gauge file` section pointing to `docs/doc-writing-guide.md` `## The context-gauge file contract`.
- Edits the genuinely-shared **lead statements** of the `#### Write the run-state manifest` section in any one of the three execution skills (`quo-execute`, `quo-fix-issue`, `quo-breakdown-epic`) without mirroring the change to all three. These lead statements are byte-identical across all three sections because there is no shared downstream carrier, and they are: the "small markdown file … values that live **nowhere else on disk**" framing sentence and the "what makes harness compaction survivable" sentence; the `<tempdir>/.quorum/` path-boilerplate sentence (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows); the bolded "The filename is deterministic — do NOT add a random suffix or timestamp." rule; the bolded "Semantics: truncate at run start, rewrite at each boundary." / "live snapshot, not an accumulating log" sentence; and the cross-skill "Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends" rationale. A change to one of *these* sentences that is not mirrored to the other two is drift, and a defect. What is **exempt** — legitimately varying per skill, so do NOT flag a difference there as drift or force it identical — is: (i) the discriminator derivation and the collision-case discussion each section carries for its own key; (ii) **durable-carrier membership** — all three enumerate three sources ("those three"), but `quo-breakdown-epic` has no compromise tracker and names the `defer-*` TaskList as its third carrier where `quo-execute` / `quo-fix-issue` name the compromise tracker; and (iii) **per-skill section cross-references** (e.g. `quo-breakdown-epic` points its boundary checkpoint at "Section 7", while the two execution skills point their pre-run SHA at "Section 11"). Only the shared lead statements must mirror.
- Writes a transient `--body-file` (or similar) scratch file outside `<tempdir>/.quorum/`, omits the `mkdir -p` / `New-Item -ItemType Directory -Force` create-if-absent step, or instructs the caller to `rm` / `Remove-Item` the scratch file after the bees / helper command exits (scratch-file convention).
- Instructs the model to perform an action that no model-invocable mechanism supports (**the executable-verb test**). Every instruction in skill prose must name an action the model can actually take with its tools — read a file, write a file, run a command, query bees, dispatch an Agent, fire a gate, mark a TaskList task. An instruction that reaches for a lever only the user or the harness owns (clearing or compacting its own context, measuring its own token usage, restarting its own session) cannot be executed at all, so the only available "compliance" is narrating it — the narrate-instead-of-do failure mode documented in `CONTRIBUTING.md` `## Known limitations`. Prose that *describes* such a mechanism as something the skill does is the same defect in declarative form; state honestly who owns the lever instead.

These criteria are additive — they do not replace, relax, or exempt any of the standard checks each review skill performs by default. They apply *only* to changes inside this repo; when the same review skills run against work in a downstream project, this section does not travel with them.

## Contract keys that downstream skills depend on

These keys appear in the *target repo's* CLAUDE.md (not this one). `quo-setup` writes them; every other skill reads them. **Do not rename them in any skill** — they are a string contract.

`## Documentation Locations` bullet keys:
- `Project requirements doc (PRD)`
- `Internal architecture docs (SDD)`
- `Customer-facing docs`
- `Engineering best practices`
- `Test writing guide`
- `Test review guide`
- `Doc writing guide`

`## Build Commands` bullet keys:
- `Compile/type-check` (may be empty for interpreted languages without a static type-checker — the only key allowed to be empty)
- `Format`
- `Lint`
- `Narrow test`
- `Full test`

**Bundled helper scripts are NOT contract keys.** Earlier revisions wrote a `## Skill Paths` section to CLAUDE.md containing absolute paths to bundled helper scripts. That section was removed (b.963) because committing per-machine paths to a tracked file broke multi-engineer collaboration. Each skill now resolves its own bundled scripts at runtime from its own base directory, which Claude Code provides in the skill invocation header. See `## Querying tickets` and `## The lookup-key pattern` in `docs/doc-writing-guide.md` for the runtime-resolution conventions skills must follow.

`quo-execute`, `quo-fix-issue`, and `quo-breakdown-epic` hard-fail with `Run /quo-setup first.` if either (i) one of the two contract sections (`Documentation Locations`, `Build Commands`), or any required key inside them, is missing from the target repo's CLAUDE.md, or (ii) any of the required hives (Plans, Issues, Specs) is missing from the target repo's bees workspace. Preserve that precondition behavior in any edit to these skills.

## Hives and status vocabulary

The workflow uses three hives in the target repo:

- **Plans** (top-level — *not* nested in an Ideas hive). Tier ladder: t1 = Epic, t2 = Task, t3 = Subtask. Statuses: `drafted` → `ready` → `in_progress` → `done`.
- **Issues**. No children. Statuses: `open` → `done`.
- **Specs** (top-level). Tier: t1 = Doc/Docs (PRD and SDD as `t1=Doc` children differentiated by title). Statuses: `drafted` → `ready`.

When a Plan Bee is authored via `/quo-plan` for a feature with no separate PRD/SDD, the Bee's `reference_materials` is null/empty and the **Plan Bee body itself becomes the authoritative spec**. Several skills (`quo-execute`'s PM role, `quo-breakdown-epic`) explicitly substitute "the Plan Bee body" for "the PRD/SDD" in that case — keep the substitution prose intact when editing those skills.

## Querying tickets

The bees CLI has no `ls`, `search`, `list-tickets`, or hive-scoped enumeration command — anything that smells like one is a guess. To enumerate or filter tickets (e.g., "what open issues exist?", "which Epics under this Bee are ready?"), use `bees execute-freeform-query --query-yaml '<yaml>'`. Recipes and the full filter/graph-stage vocabulary live in `docs/doc-writing-guide.md` `## Querying tickets`; consult it before composing a query rather than guessing subcommands.

## Model assignment in execution skills

Pinned per role in `agents/<role>.md` frontmatter (`model` + `effort`) and honored by `quo-execute`, `quo-fix-issue`, and `quo-breakdown-epic` at dispatch. All eight roles are always Opus; none of this is user-configurable at run time.

**This section is the authoritative copy** of the table, the tiering rule, the reviewer invariant, and the "always Opus" clarification — it is what agents read at run time. `docs/sdd.md` points here rather than restating them, so a retune touches exactly two places: the eight `agents/<role>.md` frontmatter blocks and this section. The design rationale behind the tiers is in `docs/sdd.md` `### Feature: Pin reasoning effort per role; drop the Sonnet downgrade prompt`.

| Role | Model | Effort |
|---|---|---|
| Analyst (`agents/analyst.md`) | Opus (always) | `xhigh` |
| Code Reviewer (`agents/code-reviewer.md`) | Opus (always) | `high` |
| Engineer (`agents/engineer.md`) | Opus (always) | `high` |
| Product Manager (`agents/pm.md`) | Opus (always) | `high` |
| Test Writer (`agents/test-writer.md`) | Opus (always) | `high` |
| Test Reviewer (`agents/test-reviewer.md`) | Opus (always) | `high` |
| Doc Writer (`agents/doc-writer.md`) | Opus (always) | `high` |
| Doc Reviewer (`agents/doc-reviewer.md`) | Opus (always) | `high` |

The tiering rule: every role that produces or reviews work runs at `high` minimum, and the Analyst — which diagnoses root cause before any implementation — runs at `xhigh`. The Code Reviewer also ran at `xhigh` until 2026-09-16, when the first full-run cost ledger (Issue `b.vtw`) showed its `xhigh` rounds at roughly twice the wall clock of the `high` reviewers with no gain in completeness (two `late` rounds followed an `xhigh` first pass); it now runs at `high`. `xhigh` everywhere was rejected on wall-clock; effort helps most on open-ended search and diagnosis and least on well-specified mechanical work.

**Reviewer invariant: never pin a reviewer below the role it reviews.** A gate weaker than the work it inspects is not a gate. The invariant holds across the table today — Engineer `high` / Code Reviewer `high`, Test Writer `high` / Test Reviewer `high`, Doc Writer `high` / Doc Reviewer `high` — and must be preserved by any future retune. Raising an implementer's tier without at least matching it on that implementer's reviewer is a defect, not a tuning choice.

**"Always Opus" fixes the tier, not the version.** Frontmatter `model: opus` pins the model *tier*; the *version* tracks the operator's session — a session on Opus 4.8 dispatches workers on Opus 4.8, a session on Opus 5 dispatches Opus 5. Don't read "always Opus" as a claim that a specific Opus version is pinned anywhere in this repo.

Subagent effort is an override of the session effort, not a cap on it, so these pins apply regardless of what the operator's session is set to. The operator's own session setting stays **advisory** — not because the repo has no lever (a skill's frontmatter can carry `effort`), but because that lever is an override rather than a floor: pinning `effort: medium` on a skill would force `medium` on an operator who deliberately launched at `xhigh`. What the recommendation needs is a floor, which frontmatter cannot express, so `quo-execute` and `quo-fix-issue` (floor `medium`) and `quo-breakdown-epic` (floor `high`) read `CLAUDE_EFFORT` at run start and prompt **only** when the session is strictly below their floor, staying silent otherwise. The recommended session settings for every *user-invoked* skill — including the planning and spec-review skills that deliberately have no gate — live in the README, which is their only user-visible carrier. The three orchestrator-only reviewers (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) are deliberately absent from that table: they never run as the operator's own session, so a session recommendation has nothing to attach to.

Don't change these assignments without a concrete reason — they're load-bearing for output quality and are referenced by users in their workflows.

## Documentation Locations

- **Project requirements doc (PRD)**: docs/prd.md
- **Internal architecture docs (SDD)**: docs/sdd.md
- **Customer-facing docs**: README.md
- **Engineering best practices**: CONTRIBUTING.md
- **Test writing guide**: docs/test-writing-guide.md
- **Test review guide**: docs/test-writing-guide.md
- **Doc writing guide**: docs/doc-writing-guide.md

## Build Commands

- **Compile/type-check**:
- **Format**: echo 'no formatter configured for this repo'
- **Lint**: python -m pyflakes skills/*/scripts/*.py
- **Narrow test**: python -m pytest tests/
- **Full test**: python -m pytest tests/

## When editing skills

- The README's skill table is the single source of truth for the user-visible skill catalog. If you add, remove, or rename a skill, update README.md to match.
- The `description` field in a skill's frontmatter is what Claude Code uses to decide whether to invoke the skill. Keep it precise — vague descriptions cause mis-invocation.
- Don't introduce a tmux dependency in any of the 14 portable-core skills. Tmux-dependent skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are explicitly out-of-scope for the cross-platform core and are mentioned only as optional later-installs.
- Avoid adding stack-specific helpers (changelog tooling, license attribution, etc.) to the core — the README declares those out of scope and routes users to companion repos.

## Working on the orchestrator skills

`skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md` were rewritten clean-room from `docs/inventory/` (the rule inventory, `DECISIONS.md`, and `REWRITE-BRIEF.md`). Changes to them follow a different process from the rest of the repo:

- **Structural changes go through inventory-anchored hand edits with cold reviews, not `/quo-fix-issue`.** Locate the rule in `docs/inventory/INVENTORY.md` (and the consolidated file it cites), edit the body or the shipped reference file that carries it, and get a cold `/quo-engineer-review` pass. Every reviewer dispatch embeds `docs/inventory/REWRITE-BRIEF.md` §5 (writing rules) and §6 (acceptance criteria), plus this file's `## Review criteria for skill changes`. The fix-issue loop on prose is the ratchet that grew the previous bodies past any budget.
- **Quorum runs remain appropriate** for helper scripts under `skills/*/scripts/`, for `tests/`, and for small, bounded prose fixes whose fix touches one rule in one place.
- **Validate process changes on a code repo before this one.** A change to how the orchestrators route, gate, or close out is exercised on a real Issue in a code repository first; this repo is the worst place to discover it does not execute.
- **A finding whose fix adds a clause must say why restructuring cannot do it.** The default fix to a routing or gate defect is to restructure the existing rule, not to add a sentence; a review finding that proposes an added clause states, in the finding, why no restructuring closes the gap.
- **Line budget is a review criterion.** Each body targets 500 lines with a hard cap of 550, and Sections 1–5 (preconditions, manifest, post-compaction rule, loop skeleton, dispatch shape) sit within the first 150 lines, because only roughly that much is re-injected after a compaction. `tests/test_orchestrator_structure.py` pins the cap, the ordering, the mirror map between the two bodies, and the gate labels; a change that trips it is a design change to argue for, not a test to loosen.
- **An edit that adds or changes a dispatch condition, routing input, or any name (a manifest column, heading, scope form, fixed line, or label) is defined before it is written.** Enumerate the condition's inputs and edge cases first (where the inputs come from, what a compaction destroys, the empty-list case, a dirty working tree, an empty phase), and for a name enumerate every reader (both bodies, the reference files, the role files, `docs/sdd.md`, the handoff note), then write the rule once and edit every reader in the same pass. The reviewer dispatch names the enumerated cases and readers as things to trace. Patching such a rule round by round is the clause-append ratchet at small scale; the second validation-run batch (2026-09-11) spent twelve of its eighteen cold rounds on three edits made without this step.
- **Cold-review exit rule for hand-edit batches.** Reviewer dispatches must ask the reviewer to classify each finding as **behavior** or **wording**, alongside severity and fix depth; the implementer must assess and record that classification before deciding whether another round is earned. A finding that changes behavior (a dispatch condition, routing input, relay recipient, staging, commit, or gate) earns a fresh cold round regardless of its severity tag. A round that returns only wording findings on sentences two or more earlier cold passes accepted unchanged closes the lane: the fixes are applied, not deferred, and the findings are recorded in the commit message as applied without a further round. This mirrors the shipped loop's rule since Issue `b.vtw` — text fixes are applied and the lane closes when no code or test finding remains — and is not a round cap; it reviews nothing less, it stops paying a full round for reviewer-to-reviewer wording variance. Batches stay small: a hand-edit batch that grows past one validation report's worth of items is split and committed in pieces. Reviewer dispatches also ask for a **contract** or **procedure** tag on each finding, and the implementer applies it before fixing: a gap between two agents — a heading, a relay, a return line, a routing that sends work nowhere — is a finding; an undefined detail inside one agent's own step is not, because the agent resolves it, and the fix is to leave the goal sentence alone. On 2026-09-18 six of thirteen findings on one batch were procedural edge cases of a single sentence the author had elaborated; each fix added a clause and each clause drew the next finding.
- **Before writing a rule for a run defect, ask three questions: how often does it happen, does it announce itself, and did the orchestrator recover unaided?** A defect that is rare, loud when it occurs, and one the agent already handled without a rule gets one goal sentence or nothing, never a mechanism. On 2026-09-18 an accidental Ctrl-C on a reviewer mid-perturbation (once, in one run; self-announcing, because a perturbation makes tests fail; recovered by the orchestrator on its own) grew across three cold rounds into a ledger value with six readers, an obligation with three close-out guards, and a two-record verification with restore-and-stop arms, at roughly 550k tokens, before the operator asked what each piece prevented; all of it came out again. The structural fix that remained — read-only review roles — was one sentence per role file. Classify the item this way in the triage, before the enumeration, because the enumeration will always find cases to cover.
- **Gates in these two skills are manifest-fronted, not TaskList-fronted.** A gate is a manifest `Write` that fills the `## Open gate` section, then `AskUserQuestion` in the same turn; lanes, `defer-*` and `aborted-*` obligations, and round counts live in the manifest's `## Lanes`, `## Obligations`, and `## Rounds` sections. No rule in either body reads TaskList state. `/quo-breakdown-epic` still carries the older two-step `TaskCreate` contract described below.

## AskUserQuestion usage

**`AskUserQuestion` is multi-choice only.** It auto-appends `Type something.` and `Chat about this`. Use it when there is a small finite set of meaningful choices. For free-text answers (paths, descriptions, names), ask in prose and let the user reply normally — do NOT add fake "Use my own answer" / "Pick Other" options that point at the auto-appended slot.

**Two-step gate-task contract.** In `/quo-breakdown-epic` (and any skill other than the two rewritten orchestrators, which front gates with a manifest write per `## Working on the orchestrator skills`), every `AskUserQuestion` invocation the orchestrator fires as a workflow gate (whether prescribed by a dispatched skill's routing trailer or by orchestrator-side prose) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, then call `AskUserQuestion` in the same turn. The contract and the rationale (it is a structural mitigation for the narrate-instead-of-do failure mode that prose-only counter-anchors did not close) live in `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`; consuming skills honor a yield-control discipline that mirrors the existing `defer-*` rule. See the doc-writing guide for the load-bearing specification; `CONTRIBUTING.md`'s known-limitations section documents the residual failure surface this contract narrows but does not close.
