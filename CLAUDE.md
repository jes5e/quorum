# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A portable Claude Code **skill set** that runs an end-to-end SDLC on top of [bees](https://github.com/gabemahoney/bees) tickets. There is no application to build: the artifacts are skills (markdown plus a few Python helpers), and the only code with its own tests and lint is the helpers (`tests/` via pytest, pyflakes — see `## Build Commands`). Work here is almost always a change to a `SKILL.md`, a role file, or a helper script.

End-user docs (install, usage, the skill catalog, the workflow diagram) live in [README.md](README.md); read it before changing user-facing behavior.

## Repo layout (only what isn't obvious)

- `skills/<name>/SKILL.md` — skill prose. Frontmatter `name` and `description` are what Claude Code shows the user (other honored keys: CONTRIBUTING.md `## Skill conventions`); the body is what Claude follows when the skill runs.
- `skills/<name>/scripts/` — cross-platform Python helpers: `quo-setup/scripts/detect_fast_path.py` (new-machine fast-path detection), `quo-breakdown-epic/scripts/scoped_marker_resolver.py` (Scoped-marker parser, also resolved by `quo-execute` and `quo-fix-issue`), `quo-execute/scripts/hive_commit.py` (hive-path resolution and deferral-encode commits), and `quo-setup/scripts/context_gauge.py` (context-usage gauge producer and reader, status-line install, opt-out marker).
- `agents/<role>.md` — the eight custom-subagent role contracts (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`), each with frontmatter (`name`, `description`, `model`, `effort`, `tools`) and the role's instructions. `quo-fix-issue` dispatches the Analyst on every Issue outside its `text` class, `quo-execute` only on escalation; `quo-breakdown-epic` dispatches the four implementer and PM roles; the two execution skills dispatch the reviewer roles.

The workflow chain (`quo-setup` → `quo-plan` | `quo-plan-from-specs` → `quo-breakdown-epic` → `quo-execute`, with `quo-file-issue` / `quo-fix-issue` alongside) is documented in the README; don't re-derive it from the skill files.

## The three non-negotiable design rules

These are the contributing principles the README calls out, and they drive every skill change:

1. **Skills must work on Rust, Node, Python, Go, Java, and unknown stacks.** Never hardcode a language-specific command, file extension, or manifest filename in skill prose; skills look up project commands in the *target* repo's CLAUDE.md under fixed contract keys. Tempted to write `cargo test` or `npm run lint` into a skill? Use the lookup-key pattern instead.
2. **Skills must work on POSIX and native Windows PowerShell.** Every shell snippet in a `SKILL.md` ships as labeled OS-conditional blocks (POSIX bash + Windows PowerShell at minimum; cmd.exe optional); there is no bash-only fallback. Helper scripts are Python (preferred) or OS-paired implementations.
3. **Skill prose must be project-neutral.** A `SKILL.md` (or any helper script) must not reference *this* repo's paths, ticket IDs, internal workflow specifics, or anything that wouldn't make sense in another project that installs the skills. Project-specific guidance for downstream users lives in the *target* repo's CLAUDE.md, which skills read at runtime. This file governs work done **on** the skills; nothing in it is baked **into** them.

## How skill prose is written

Skill prose — `skills/*/SKILL.md`, `agents/*.md`, and the shipped `references/` files — states goals with their reasons and leaves the procedure to the agent. Agents work out procedure well. What they cannot do is agree on an exact string with another agent, protect state from a loss they cannot see coming, reliably obey an instruction that stronger wording has already failed to enforce, or know a choice that is the operator's to make. So prose prescribes only:

1. **Contracts** — headings, return lines, manifest fields, gate labels, the ticket shapes and titles another agent keys on, and templates whose output another agent or the operator reads.
2. **State that must survive what the agent cannot observe** — a compaction, or the next session's blindness to this conversation.
3. **Structural guards where prose has already failed** — the manifest-fronted gate, read-only tool allowlists.
4. **Operator policy** — for example: never push, never `git add -A`, the commit format.
5. **A rule a run failure has earned** under the three questions below, stated as a goal with its reason.

The design rules above, and the scratch-file convention and contract keys below, are rules of these kinds; this section relaxes none of them. Prose is ambiguous only when an agent cannot tell what outcome satisfies it or what exact string a contract uses; a step whose procedure is left to the agent is not ambiguous (the definition `/quo-engineer-review` applies).

**External CLIs get orientation, not recipes.** For bees or any other external tool, a skill names the tool, where its help is (`bees <command> -h`, `bees sting`), and the facts that help does not make obvious or gets wrong. It does not spell out invocations, which go stale when the tool changes. An exact invocation stays only when its exact form is the point: a non-obvious fact (git's `--output=` must precede `--`) or a decision (which files count as in scope). When the help is missing or wrong about something, name the fact in skill prose, file an upstream report (or ask the operator to), and delete the fact once the help carries it. Orientation is not vague prose: "run the appropriate test command" leaves the agent guessing, while "run the `Full test` command from CLAUDE.md `## Build Commands`" names exactly where the answer is.

**How a skill improves.**

- When a run shows a failure, first fix the goal, contract, or state carrier that let it happen. Before adding a rule, ask three questions: how often does it happen, does it announce itself, and did the agent recover unaided? A failure that is rare, loud, and recovered gets one goal sentence or nothing; the more of those answers go the other way, the stronger the case for a rule.
- When a run shows an agent handling a case correctly without the rule written for it — the rule absent, not reached, or not what the agent followed — delete the rule. Contracts, state carriers, structural guards, and operator policy are deleted only when their reader or failure mode is gone, or the operator withdraws the policy.
- A rule added for a run failure, and any deleted rule, carries its evidence — three-question answers, run evidence, the reader that is gone, or the operator's withdrawal — in the ticket, the reviewer dispatch, or the commit message.
- Each validation run's triage lists what the agent improvised around and which rules it did not need; deletions come from that list.
- Text a change adds or edits meets this standard. Rewriting neighboring text is in scope only when the change needs it; nothing is rewritten in a sweep.
- Structural tests pin only text of the kinds above. Removing a test anchor on a spelled-out invocation or a how-to sentence that this standard retires is not loosening the test.
- `tests/test_prose_size.py` caps every shipped prose file, and this file, at its accepted word count. A change that grows one raises its cap in the same commit, with the growth's reason in the ticket, reviewer dispatch, or commit message; a change that shrinks one lowers its cap.

## Bash etiquette in this repo

Every Bash tool call in this repo is a **single literal command** — one binary plus its arguments — for every Claude instance: leads, workers, reviewers, ad-hoc sessions. Each forbidden shape below trips a Claude Code matcher and re-prompts the user, even on previously-approved repos. The role files carry their own `Shell-command etiquette` bullet for spawned workers; keep the two consistent.

**Forbidden:**

- Compound chains: `cmd1 && cmd2`, `cmd1 || cmd2`, `cmd1 ; cmd2`
- Pipes between commands (use `Grep` / `Read`, or a match-limit flag like `grep -m N`)
- Redirects mid-chain: `echo X > file && cmd` (use `Write`)
- Diagnostic tails: `; echo exit=$?`, `&& echo done` (the Bash tool already reports exit status)
- Shell variables and expansion: `$VAR`, `${VAR:-default}`, `$?`, `$(...)`, backticks
- Multi-line `-c` or inline heredocs
- `unset` / `export` mid-chain
- Backticks inside *double*-quoted strings: bash reads them as command substitution, and the safety matcher re-prompts even when `Bash(grep:*)` is allowlisted. Single-quote any literal that contains backticks.

**Instead:** one Bash call per command, in parallel where independent; env vars through a `VAR=value command` prefix; multi-step or variable-bearing logic as a Python script written with `Write` and run in one call; `Monitor` over polling loops, `Read` over `cat` / `head` / `tail`, `Grep` over `grep | head`, `Write` over `echo X > file`.

## Scratch-file convention

A skill or dispatched subagent that writes a transient file — a `--body-file` payload for `bees create-ticket` / `bees update-ticket`, a ticket-body extract for the Scoped-marker helper, anything that lives only until the next bees or helper call — follows this convention. It is a **fourth design rule** and a review criterion.

1. **Write under `<tempdir>/.quorum/`**, where `<tempdir>` is `/tmp` on POSIX and `%TEMP%` on Windows, creating `.quorum` if it does not exist. Helpers resolve it with Python's `tempfile.gettempdir()`. One named namespace, rather than random names directly in `<tempdir>`, lets users find every artifact a workflow made and lets reviewers spot stray writes.
2. **Never delete, on any OS.** Skill prose never tells a caller to `rm` / `Remove-Item` a scratch file: the footprint is small, the OS cleans `/tmp`, mid-run cleanup causes permission prompts, and leftovers help debug a crashed run.
3. **No `rm`-with-allowlist patterns.** Permission patterns prefix-match the literal command, so `Bash(rm /tmp/.quorum/**)` would also match `rm /tmp/.quorum/../../etc/something` — a path-traversal surface under prompt injection. Do not reintroduce a cleanup design.

When skill prose shows these steps as shell, use these shapes verbatim (paired POSIX + PowerShell, per design rule 2):

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

Prose may instead state these steps as a goal, which satisfies this convention equally, provided it names the directories literally (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows), since `<tempdir>` is defined only in this file, which does not ship.

Filenames inside the namespace are collision-resistant when concurrency is possible (for example `bees-body-<short-suffix>.md`). A deterministic name is a defect except for three documented exceptions, each of which has a writer and a reader that must compute the same path independently. Their rationale is in `docs/doc-writing-guide.md` `## Deterministic names in the scratch namespace` (the manifest's collision cases are in each skill's manifest section):

- **The orchestrators' run-state manifest** (`run-state-<skill>-<discriminator>.md`): its reader is the orchestrator itself after a compaction, so the path must be recomputable. Its lead statements mirror across three skills (see the review criteria). `/quo-plan` writes one too, keyed on the repo directory name, outside that mirror.
- **The per-session context-usage gauge** (`context-usage-<session_id>.json`), plus the installer's self-check file `context-usage-quo-setup-self-check.json`.
- **The context-guard opt-out marker** (`context-guard-opt-out`): it records an environment-wide standing choice, so it carries no discriminator.

The README tells users the directory is safe to delete **between** runs but not during one, since the run-state manifest it holds is not regenerated; deleting it at any time also clears the context-guard opt-out marker, so the operator is re-prompted on a later run. Don't duplicate that note in skill prose, and don't restate it here as an unqualified "safe to delete anytime".

## Review criteria for skill changes

When `quo-engineer-review`, `quo-test-writer-review`, or `quo-doc-writer-review` reviews a change in *this* repo, the criteria below are mandatory, layered on top of each skill's standard checks: they relax none of those checks, and they do not travel with the review skills to downstream projects. `quo-spec-review` is excluded because it reviews spec ticket bodies, not files in this repo. Flag any skill-prose or helper-script change that:

- Hardcodes a language-specific command, file extension, or manifest filename (rule 1).
- Introduces a shell snippet without paired POSIX bash + Windows PowerShell variants, or relies on a bash-only fallback (rule 2).
- References this repo's paths, ticket IDs, or internal workflow specifics in a way that would not make sense installed in another project or on another machine (rule 3). The install copies only `skills/*` and `agents/*`, so a shipped artifact — a `SKILL.md`, an `agents/*.md`, or a bundled helper — that cites a repo-only doc (`docs/*`, `CONTRIBUTING.md`, or a CLAUDE.md section such as `## Scratch-file convention` or `## AskUserQuestion usage`) dangles on a fresh install: inline the operative instruction at the site and drop the citation. Two carve-outs are legitimate and must not be flagged: citing `CLAUDE.md ## Documentation Locations` or `CLAUDE.md ## Build Commands`, the contract keys `/quo-setup` writes into the target repo (mirrored by `ALLOWED_SECTIONS` in `tests/test_shipped_artifact_portability.py`); and a `README.md` → `docs/*` link, since README is read in a checkout and never installed (e.g. README's `### The context-usage gauge file` → `docs/doc-writing-guide.md` `## The context-gauge file contract`).
- Edits a run-state manifest lead statement in one of `quo-execute`, `quo-fix-issue`, or `quo-breakdown-epic` without mirroring it to all three. The lead statements (pinned as `MANIFEST_LEAD_STATEMENTS` in `tests/test_orchestrator_structure.py`) stay byte-identical because the three skills share no file they could cite instead. The rest of each skill's `#### Write the run-state manifest` section legitimately differs and is not drift: its discriminator and collision cases, its third durable carrier (breakdown's `defer-*` TaskList where the execution skills name the compromise tracker), and its section cross-references.
- Writes a transient scratch file outside `<tempdir>/.quorum/`, omits the create-if-absent step (the `mkdir -p` / `New-Item -ItemType Directory -Force` snippet or the equivalent stated goal), or tells the caller to `rm` / `Remove-Item` it (scratch-file convention).
- Instructs the model to do something no model-invocable mechanism supports (**the executable-verb test**). Every instruction must name an action the model can take with its tools — read or write a file, run a command, query bees, dispatch an Agent, fire a gate, mark a TaskList task. A lever only the user or the harness owns (clearing or compacting its own context, measuring its own token usage, restarting its own session) can only be narrated, which is the narrate-instead-of-do failure (`CONTRIBUTING.md` `## Known limitations`); prose that describes such a mechanism as the skill's own is the same defect. State who owns the lever instead.
- Adds prescription outside the kinds in `## How skill prose is written` — a step-by-step procedure, a decision table, or a spelled-out external-CLI invocation whose exact form is not the point — where a goal with its reason would do; or adds a rule for a run failure, or deletes a rule, without its evidence recorded (per `## How skill prose is written`). A finding under this bullet says why the text fits none of the kinds and gives the replacement goal sentence. Flag only text the change adds or edits; untouched existing prose is not a finding. Also flag a raised cap in `tests/test_prose_size.py` with no stated reason for the growth.

## Contract keys that downstream skills depend on

These keys appear in the *target repo's* CLAUDE.md (not this one). `quo-setup` writes them and every other skill reads them by exact match. **Do not rename them in any skill** — they are a string contract.

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

**Bundled helper scripts are not contract keys.** Each skill resolves its own scripts at runtime from the base directory Claude Code shows in the skill invocation header, because per-machine paths committed to a tracked CLAUDE.md break multi-engineer repos (a `## Skill Paths` section was removed for that reason, b.963). The runtime-resolution conventions are in `docs/doc-writing-guide.md` `## Querying tickets` and `## The lookup-key pattern`.

`quo-execute`, `quo-fix-issue`, and `quo-breakdown-epic` hard-fail with `Run /quo-setup first.` if (i) either contract section, or any required key inside it, is missing from the target repo's CLAUDE.md, or (ii) any required hive (Plans, Issues, Specs) is missing from the target repo's bees workspace. Preserve that precondition in any edit to these skills.

## Hives and status vocabulary

The workflow uses three hives in the target repo:

- **Plans** (top-level — *not* nested in an Ideas hive). Tiers: t1 = Epic, t2 = Task, t3 = Subtask. Statuses: `drafted` → `ready` → `in_progress` → `done`.
- **Issues**. No children. Statuses: `open` → `done`.
- **Specs** (top-level). Tier: t1 = Doc/Docs (the PRD and SDD are `t1=Doc` children, differentiated by title). Statuses: `drafted` → `ready`.

When a Plan Bee's `reference_materials` is null or empty (no skill emits that shape today; older and hand-made Plan Bees carry it), the **Plan Bee body itself is the authoritative spec**. Several skills (`quo-execute`'s PM role, `quo-breakdown-epic`) substitute "the Plan Bee body" for "the PRD/SDD" in that case; keep that substitution prose intact when editing them.

## Querying tickets

The bees CLI has no `ls`, `search`, `list-tickets`, or hive-scoped enumeration command — anything that smells like one is a guess. To enumerate or filter tickets, use `bees execute-freeform-query --query-yaml '<yaml>'`. The shape, the filter and graph-stage vocabulary, and worked examples are in `docs/doc-writing-guide.md` `## Querying tickets`; consult it before composing a query rather than guessing a subcommand.

## Model assignment in execution skills

Pinned per role in `agents/<role>.md` frontmatter (`model` + `effort`) and honored at dispatch by `quo-execute`, `quo-fix-issue`, and `quo-breakdown-epic`; none of it is user-configurable at run time. **This section is the authoritative copy** of the table, the tiering rule, the reviewer invariant, and the "always Opus" clarification, and it is what agents read at run time. `docs/sdd.md` points here, so a retune touches exactly the eight frontmatter blocks and this section. Design rationale: `docs/sdd.md` `### Feature: Pin reasoning effort per role; drop the Sonnet downgrade prompt`.

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

**Tiering rule:** every role that produces or reviews work runs at `high` minimum, and the Analyst, which diagnoses root cause before any implementation, runs at `xhigh`. Effort pays most on open-ended diagnosis and least on well-specified work: `xhigh` everywhere was rejected on wall-clock, and the Code Reviewer came down from `xhigh` after its rounds showed about twice the wall clock with no gain in completeness.

**Reviewer invariant: never pin a reviewer below the role it reviews.** A gate weaker than the work it inspects is not a gate; raising an implementer's tier without at least matching its reviewer is a defect, not a tuning choice.

**"Always Opus" fixes the tier, not the version.** `model: opus` pins the tier; the version follows the operator's session. Nothing in this repo pins a specific Opus version.

Subagent effort overrides the session effort rather than capping it, so these pins hold whatever the operator's session is set to. The operator's own session setting stays **advisory**: a skill's frontmatter `effort` would override the operator's choice (forcing `medium` on someone who launched at `xhigh`) rather than set the floor a recommendation needs. So `quo-execute` and `quo-fix-issue` (floor `medium`) and `quo-breakdown-epic` (floor `high`) read `CLAUDE_EFFORT` at run start and prompt **only** when the session is strictly below their floor. The recommended session settings for every *user-invoked* skill — including the planning and spec-review skills, which deliberately have no gate — live in the README, their only user-visible carrier; the three orchestrator-only review skills (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) are absent from that table because they never run as the operator's own session.

Don't change these assignments without a concrete reason — they're load-bearing for output quality and users rely on them.

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

- Run the `Full test` command from `## Build Commands` before every commit in this repo. The structural and prose-size tests bind only if they run, and the orchestrators' close-out runs `Full test` only when CLAUDE.md requires it.
- The README's skill table is the single source of truth for the user-visible skill catalog. If you add, remove, or rename a skill, update README.md to match.
- The `description` field in a skill's frontmatter is what Claude Code uses to decide whether to invoke the skill. Keep it precise — vague descriptions cause mis-invocation.
- Don't introduce a tmux dependency in any of the 14 portable-core skills. Tmux-dependent skills (`bees-fleet`, `bees-worktree-add`, `bees-worktree-rm`) are out of scope for the cross-platform core and mentioned only as optional later installs.
- Avoid adding stack-specific helpers (changelog tooling, license attribution, etc.) to the core — the README declares those out of scope and routes users to companion repos.

## Working on the orchestrator skills

`skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md` were rewritten clean-room from `docs/inventory/` (the rule inventory, `DECISIONS.md`, and `REWRITE-BRIEF.md`), and changes to them follow their own process:

- **Structural changes are inventory-anchored hand edits with cold reviews, not `/quo-fix-issue` runs**, because the fix-issue loop on prose is the ratchet that grew the old bodies past any budget. Locate the rule in `docs/inventory/INVENTORY.md` (and the consolidated file it cites), edit the body or the shipped reference file that carries it, and get a cold `/quo-engineer-review` pass. Every reviewer dispatch embeds `docs/inventory/REWRITE-BRIEF.md` §5 (writing rules) and §6 (acceptance criteria), plus `## Review criteria for skill changes`.
- **Quorum runs remain appropriate** for helper scripts under `skills/*/scripts/`, for `tests/`, and for small, bounded prose fixes that touch one rule in one place.
- **Validate process changes on a code repo before this one.** A change to how the orchestrators route, gate, or close out is exercised on a real Issue in a code repository first; this repo is the worst place to discover it does not execute.
- **A finding whose fix adds a clause says why restructuring cannot close the gap.** The default fix to a routing or gate defect is to restructure the existing rule, not to add a sentence.
- **Line budget is a review criterion.** Each body targets 500 lines (hard cap 550), with Sections 1–5 (preconditions, manifest, post-compaction rule, loop skeleton, dispatch shape) inside the first 150 lines, because only about that much is re-injected after a compaction. `tests/test_orchestrator_structure.py` pins the cap, the ordering, the mirror map between the two bodies, and the gate labels; tripping it is a design change to argue for, not a test to loosen.
- **Define a dispatch condition, routing input, or name before writing it.** For a condition, enumerate its inputs and edge cases (where the inputs come from, what a compaction destroys, the empty list, a dirty working tree, an empty phase). For a name (a manifest column, heading, scope form, fixed line, or label), enumerate every reader (both bodies, the reference files, the role files, `docs/sdd.md`, the handoff note). Then write the rule once, edit every reader in the same pass, and have the reviewer trace those cases and readers. Patching such a rule round by round is the clause-append ratchet at small scale.
- **Cold-review exit rule for hand-edit batches.** Reviewer dispatches ask for a **behavior** or **wording** tag and a **contract** or **procedure** tag on each finding, alongside severity and fix depth; the implementer assesses and records both before fixing and before deciding on another round. A behavior finding (a dispatch condition, routing input, relay recipient, staging, commit, or gate) earns a fresh cold round whatever its severity. A round that returns only wording findings on sentences two or more earlier passes accepted unchanged closes the lane: the fixes are applied, not deferred, and recorded in the commit message. This is not a round cap; it stops paying a full round for wording variance between reviewers. A gap between two agents (a heading, a relay, a return line, a routing that sends work nowhere) is a finding; an undefined detail inside one agent's own step is not, because the agent resolves it, so leave the goal sentence alone. Batches stay small: split a batch that outgrows one validation report's worth of items.
- **Classify a run defect with the three questions (`## How skill prose is written`) during triage, before enumerating its cases**, because the enumeration will always find cases to cover.
- **A session handoff names every file to read and stops at a checkpoint before the first edit.** It lists the exact files by path — every memory file the memory index links (say how many, and say to `ls` the memory directory and open each, project and reference files included), the ticket and its sections by heading, the repo files — and states the expected `git log` head and a clean tree as facts to verify. The receiving agent then reports in its own words what the items are, which files each touches, and every file and section it has read in full, and waits for the operator's go; a thin or partial answer goes back to the reading step. A general "read everything" gets skimmed; a list and a read-back do not.
- **Gates in these two skills are manifest-fronted, not TaskList-fronted.** A gate is a manifest `Write` that fills the `## Open gate` section, then `AskUserQuestion` in the same turn; lanes, `defer-*` and `aborted-*` obligations, and round counts live in the manifest's `## Lanes`, `## Obligations`, and `## Rounds` sections. No rule in either body reads TaskList state. `/quo-plan` fronts its gates the same way; `/quo-breakdown-epic` still carries the older two-step `TaskCreate` contract below.

## AskUserQuestion usage

**`AskUserQuestion` is multi-choice only.** It auto-appends `Type something.` and `Chat about this`, so use it for a small finite set of meaningful choices. For free-text answers (paths, descriptions, names), ask in prose and let the user reply — never add fake "Use my own answer" / "Pick Other" options pointing at the auto-appended slot.

**Two-step gate-task contract.** In `/quo-breakdown-epic`, and any skill that does not front its gates another way, every `AskUserQuestion` fired as a workflow gate — whether a dispatched skill's routing trailer or orchestrator prose prescribes it — first creates a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, then calls `AskUserQuestion` in the same turn. `/quo-execute`, `/quo-fix-issue`, and `/quo-plan` front each gate with a run-state-manifest write instead, and solo `/quo-write-prd` / `/quo-write-sdd` with the write of the body the gate asks about: either way, a tool call in the gate's turn. It is a structural guard against the narrate-instead-of-do failure that prose-only counter-anchors did not close. The load-bearing specification, including the yield-control discipline that mirrors the `defer-*` rule, is `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`; `CONTRIBUTING.md` `## Known limitations` documents the residual failure surface it narrows but does not close.
