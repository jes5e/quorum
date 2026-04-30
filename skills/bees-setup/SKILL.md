---
name: bees-setup
description: Configure hives for the bees workflow
---

## Overview

Configure a repo for the bees workflow. Sets up hives, writes a `## Documentation Locations` section and a `## Build Commands` section in CLAUDE.md, and (optionally) bootstraps baseline PRD/SDD docs by exploring the existing codebase.

**This skill is safe to re-run.** Each section detects existing configuration and only prompts where something is missing, stale, or you ask to change it. If you skipped doc bootstrap on the first run and want to add docs later, re-running setup re-offers the bootstrap option.

The bees workflow has two entry points for new work, both supported by this setup:
- **`/bees-plan`** — interactive scope discovery for an idea, refactor, or feature without finalized specs
- **`/bees-plan-from-specs`** — express path when you already have a finalized PRD and SDD on disk

## Valid configuration

The repo must have the following hives available and configured with these child tiers and valid status values:

### Issues Hive
Child tiers:
none

Status values:
- open — open issue
- done — completed

### Plans Hive
Child tiers:
- t1 — Epic / Epics
- t2 — Task / Tasks
- t3 — Subtask / Subtasks

Status values:
- drafted — not fully documented, not ready to work
- ready — fully documented, ready to work
- in_progress — actively being worked on
- done — completed

The Plans hive is a **top-level** hive. It is not nested inside an Ideas hive.

## Instructions

### Prerequisites

#### 1. bees CLI

Verify bees is available on PATH. The exact lookup command depends on the host shell:

```bash
# POSIX (bash / zsh — macOS, Linux, WSL):
which bees

# Windows (PowerShell):
Get-Command bees -ErrorAction SilentlyContinue

# Windows (cmd.exe):
where bees
```

If bees is not present, install it:

```bash
pipx install bees-md
```

`pipx` itself can be installed several ways:

```bash
# macOS:
brew install pipx

# Linux (Debian/Ubuntu):
sudo apt install pipx

# Linux (Fedora):
sudo dnf install pipx

# Windows (scoop):
scoop install pipx

# Windows (or any platform via Python):
python -m pip install --user pipx
```

bees-md requires Python 3.10+. After install, the bees binary lives under the user's local-binary directory: `~/.local/bin/bees` on POSIX, `%USERPROFILE%\.local\bin\bees.exe` (or wherever pipx put it) on Windows. Documentation: https://github.com/gabemahoney/bees

#### 2. Claude Code Agent Teams (strongly recommended)

`bees-execute` and `bees-fix-issue` use Claude Code's **Agent Teams** feature to run Engineer + Test Writer + Doc Writer + PM concurrently on each Task instead of in sequence. With it enabled, the workflow is noticeably faster and more parallel; without it, the skills fall back to single-agent execution and still work end-to-end.

**Detect current state.** Read the user's Claude Code settings file:

- POSIX: `~/.claude/settings.json`
- Windows: `%USERPROFILE%\.claude\settings.json`

Check whether `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `"1"`.

**If already enabled**: confirm to the user ("Agent Teams is enabled — `bees-execute` and `bees-fix-issue` will run their teams in parallel.") and move on.

**If not enabled (or the settings file doesn't exist)**: don't silently skip. Explain the upgrade and offer to enable it via `AskUserQuestion`:

> "Agent Teams is currently disabled. Enabling it makes `bees-execute` and `bees-fix-issue` run their team agents (Engineer / Test Writer / Doc Writer / PM) in parallel instead of sequentially — typically a 2-3x speedup on each Task. The setting is `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = '1'` in your Claude Code user settings file. Want me to enable it now?"
>
> Options:
> 1. **Yes, enable it (Recommended)** — I'll add the setting to your settings file (creating it if it doesn't exist). Takes effect on your next Claude Code session.
> 2. **Skip for now** — `bees-execute` and `bees-fix-issue` fall back to single-agent execution; still fully functional.
> 3. **Show me what to add and I'll do it myself** — print the JSON snippet and file path, then continue.

If option 1: read the existing JSON (or `{}` if the file is missing), merge in the new key without disturbing other settings, show the user a before/after diff, then write the file. Remind the user: "This takes effect on your next Claude Code session — restart Claude Code when you have a moment."

If option 2: continue setup; Agent Teams remains disabled. The user can enable it later by re-running `/bees-setup` (which will re-detect and re-offer) or by editing the settings file by hand.

If option 3: print the exact addition (`"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"`) and the file path, then continue setup.

> **Optional later-installs not needed for the core portable workflow:**
> The skills `bees-fleet`, `bees-worktree-add`, and `bees-worktree-rm` require **tmux** for terminal session management. If you do not plan to use those skills, you do not need tmux. If you later install or invoke any of them, install tmux at that point (`brew install tmux` on macOS / `sudo apt install tmux` on Debian-Ubuntu Linux / install via WSL on Windows — tmux has no native Windows port). The core flow — `/bees-plan` or `/bees-plan-from-specs` → `/bees-breakdown-epic` → `/bees-execute` → `/bees-fix-issue` — does not need tmux and works on native Windows PowerShell.

---

### Egg Resolver

Before configuring hives, set up the egg resolver. This resolver lets a Plan Bee's `egg` field point at one or more source documents on disk (PRD, SDD, etc.). Downstream skills (`/bees-execute`, `/bees-breakdown-epic`) read these files as the authoritative source for the work.

The resolver ships bundled with this skill at `.claude/skills/bees-setup/scripts/file_list_resolver.py` (relative to the repo root where the skill is installed). It takes a JSON array of absolute file paths as the egg value and returns a validated JSON array of resolved paths.

Compute the absolute path to the resolver at invocation time and verify it exists:

```bash
# POSIX (bash / zsh):
RESOLVER="$(pwd)/.claude/skills/bees-setup/scripts/file_list_resolver.py"
test -f "$RESOLVER" && echo "OK" || echo "Missing"

# Windows (PowerShell):
$RESOLVER = "$(Get-Location)\.claude\skills\bees-setup\scripts\file_list_resolver.py"
if (Test-Path $RESOLVER) { "OK" } else { "Missing" }
```

If missing, the skill installation is incomplete — direct the user to re-copy the `.claude/skills/` tree.

When colonizing hives, pass the absolute resolver path as the `egg_resolver` parameter to `bees colonize-hive`. If hives already exist and have a stale `egg_resolver` from an earlier installation, update their configuration to point to this file. The bees CLI user config file lives at:

- POSIX: `~/.bees/config.json`
- Windows: `%USERPROFILE%\.bees\config.json`

Edit it directly to set the `egg_resolver` field on the hive entry, then verify with a `bees show-ticket` on a Plan Bee that has eggs.

### Hive Configuration

All bees CLI commands must be run from inside the target repo directory.

#### Scope requirement

When calling `bees colonize-hive`, **always pass an explicit scope** specific to the target project. The default scope overlaps with other projects' hives and bees will reject the creation if any other project has a hive with the same name.

Pick the narrowest scope glob that covers the entire project directory tree — typically the project root with a trailing `/**`.

#### Create or validate

Check for the existence of the above hives using `bees list-hives` and validate their configs with `bees get-types` and `bees get-status-values`.

If any hives are missing:
- **Use `AskUserQuestion` to ask the user where each missing hive should live.** Do not assume a default path. Suggest sensible options (e.g., `<repo>/.bees/issues` in-repo, or `<project-parent>/issues` sibling-to-repo) but always let the user pick.
- Once the user chooses, create the hive using the bees CLI:
  ```bash
  bees colonize-hive --name <name> --path <path> --scope "<scope>"
  ```
- After colonization, set child tiers and status values:
  ```bash
  bees set-types --scope hive --hive <name> --types '<json>'
  bees set-status-values --scope hive --hive <name> --status-values '<json>'
  ```

If a hive exists:
- Validate its child tiers and status values.
- If they differ from above, ask user if you may change them.

**Important:** This workflow has no Ideas hive. If the target repo already has an Ideas hive from a prior setup, do not remove it — but note that bees-workflow skills will not use it.

### Documentation Locations

After hives are configured, set up the `## Documentation Locations` section in CLAUDE.md.

**First, detect existing configuration.** Read the project's CLAUDE.md (create it if it doesn't exist). If a `## Documentation Locations` section already exists, parse the current values for each of the six doc types below. For each row that's already set, **show the current value to the user and ask whether to keep or change it** — do not blindly re-prompt for paths that are already configured. Only prompt fully for rows that are missing or that the user opts to change.

If the section doesn't exist at all, ask whether to configure it now: "Would you like to configure documentation locations in CLAUDE.md now? The bees workflow uses these docs as the **machine-readable source of truth** that downstream agents (`bees-execute`, `bees-fix-issue`) read during work to detect spec drift and align with project standards. For each doc type, you can point to an existing file or have one generated for you. You may also skip this step entirely."
- Options: "Yes" / "Skip for now"

If yes (or for any individual rows the user opted to change), walk through each of the six doc types below **one at a time**. For each, use AskUserQuestion to ask the user what they'd like to do:

| Doc type | Question | Options |
|----------|----------|---------|
| Project requirements doc (PRD) | "Do you have a project-level PRD?" | "Yes, here's the path: ___" / "Skip (offer bootstrap below)" |
| Internal architecture docs (SDD) | "Do you have internal architecture docs (e.g., an SDD)?" | "Yes, here's the path: ___" / "Skip (offer bootstrap below)" |
| Customer-facing docs | "Do you have customer-facing docs (e.g., a README)?" | "Yes, here's the path: ___" / "Use README.md (will be created during execution)" / "Skip" |
| Engineering best practices | "Do you have an engineering best practices guide?" | "Yes, here's the path: ___" / "Generate one for me" / "Skip" |
| Test writing guide | "Do you have a test writing guide?" | "Yes, here's the path: ___" / "Generate one for me" / "Skip" |
| Test review guide | "Do you have a test review guide?" | "Yes, here's the path: ___" / "Generate one for me" / "Skip" |
| Doc writing guide | "Do you have a doc writing guide?" | "Yes, here's the path: ___" / "Generate one for me" / "Skip" |

Notes:
- **PRD and Internal architecture docs (SDD)** describe what the project is and how it's designed. If skipped here, the **Bootstrap PRD/SDD from existing codebase** subsection below offers to create them by exploring the repo. Don't auto-generate from a static template — they need real content drawn from the project.
- **Customer-facing docs** should not be generated during setup — offer to point to `README.md` which the Doc Writer agent will create during execution.
- The four boilerplate guides (engineering, test writing, test review, doc writing) can each independently be provided by the user or generated from a template tailored to the detected stack.
- You may batch multiple questions into a single AskUserQuestion if it reads clearly, but the user must be able to give a different answer per doc type.

#### Generating docs

Before generating any docs, determine the project's technology stack from CLAUDE.md, the SDD, `Cargo.toml`, `package.json`, `go.mod`, or similar manifest files. Then generate each requested doc tailored to that stack:

- **Engineering best practices** (`docs/engineering-best-practices.md`) — coding standards, error handling conventions, module/package boundary rules, async/concurrency patterns, type design, API conventions, observability, storage patterns, security, code style, and dependency management. Ground every recommendation in the project's actual stack (e.g., for a Rust/tonic/tokio project: thiserror for errors, tracing for observability, dashmap for concurrency, clippy/fmt for style).

- **Test writing guide** (`docs/test-writing-guide.md`) — test organization (unit vs integration), naming conventions, async test patterns, integration test isolation strategies, mocking approach (prefer hand-written trait mocks over frameworks where applicable), test data construction, assertion patterns, property-based testing, and what not to test.

- **Test review guide** (`docs/test-review-guide.md`) — checklist format covering: correctness (behavior not implementation), isolation (no cross-test dependencies), coverage (happy path + error paths + boundaries), robustness (no sleeps for sync, timeouts on hangs), readability (arrange-act-assert, named constants), performance, and anti-patterns to flag.

- **Doc writing guide** (`docs/doc-writing-guide.md`) — inline doc conventions (e.g., rustdoc, JSDoc, godoc), when to update architecture docs vs README, writing style (active voice, direct, code over prose), project-specific terminology to use consistently, formatting rules, and what not to document.

Each guide should be comprehensive but practical — opinionated defaults, not exhaustive references. Use the project's own technology choices as concrete examples throughout.

After generating, ask the user to review the generated docs and confirm before proceeding.

#### Writing the CLAUDE.md section

Do NOT volunteer the following context unless the user asks what a location is for:
- **Project requirements doc (PRD)**: Used by the Product Manager agent in `bees-execute` and `bees-fix-issue` to detect spec drift — does the work the Engineer landed match what the project says it does? Project-level cumulative spec; new features add sections, never overwrite.
- **Internal architecture docs (SDD)**: Used by the Engineer to understand existing system design, by the Product Manager for architectural drift detection, and by the Doc Writer to update architecture documentation after code changes.
- **Customer-facing docs**: Used by the Doc Writer to update user-facing documentation when user-visible behavior changes.
- **Engineering best practices**: Used by the Engineer agent in bees-fix-issue, bees-breakdown-epic, and bees-execute to follow project coding standards when writing or modifying source code.
- **Test writing guide**: Used by the Test Writer to follow project testing conventions when writing or modifying tests.
- **Test review guide**: Used by the Test Writer to self-review test quality before completing work.
- **Doc writing guide**: Used by the Doc Writer to follow project documentation style and format conventions.

Then write or update a `## Documentation Locations` section in the project's CLAUDE.md with the provided paths, using this format:

```markdown
## Documentation Locations

- **Project requirements doc (PRD)**: <path>
- **Internal architecture docs (SDD)**: <path>
- **Customer-facing docs**: <path>
- **Engineering best practices**: <path>
- **Test writing guide**: <path>
- **Test review guide**: <path>
- **Doc writing guide**: <path>
```

### Bootstrap PRD/SDD from existing codebase (optional)

This subsection runs **only if** the PRD or SDD (or both) were skipped during the Documentation Locations walkthrough above (or are still missing on a re-run). If both are already configured and present on disk, skip this subsection entirely.

**Why this matters.** Use the following framing when posing the question to the user — verbatim or close to it. The natural inclination of an engineer is to think "I don't care about reading PRD/SDD documents, I'll skip this." Reframe it:

> Your project doesn't have a PRD or SDD configured. Note: these docs aren't primarily for you to read. They're the **machine-readable source of truth that bees-workflow agents (`bees-execute`, `bees-fix-issue`) read during work** to detect spec drift, verify the Engineer hasn't built something different from what was planned, and keep multi-feature projects coherent over time. Without them, each agent has less context to anchor against and may make inconsistent assumptions across features.

Then offer three options via AskUserQuestion:

1. **Bootstrap baseline docs now** *(recommended for established projects with existing code)* — I'll explore your codebase, ask you a few short questions about the project's purpose, and produce starter `docs/prd.md` and `docs/sdd.md`.
2. **Defer** — `/bees-plan` will offer to create docs seeded from your first feature's scope when you plan something new. Best for greenfield projects with little or no code yet.
3. **Skip permanently — body-as-spec** — I won't create any docs. Each Plan Bee body becomes the spec for that feature. Each Issue Bee body is the spec for that issue. Works for one-off features or throwaway projects, but does not accumulate a project-level spec across features.

#### Detect repo state before showing the question

Run a quick heuristic to decide what the question should default to:

- **Established project** (more than ~3 source files in the repo, or a non-trivial README, or any of: existing test directory, existing CI config, existing manifest like `Cargo.toml` / `package.json` / `go.mod` / `pyproject.toml` with declared dependencies) → option 1 ("Bootstrap baseline docs now") is the default and recommended option.
- **Near-greenfield** (empty repo, hello-world only, no real source) → skip the bootstrap question entirely. Tell the user: "This looks like a new/empty project. `/bees-plan` will offer to create your initial PRD/SDD seeded from your first feature's scope. No bootstrap to do here." Skip ahead to Build Commands.

#### If the user picks option 1 (Bootstrap)

##### Step A: Explore the codebase

Read the project broadly. The goal isn't to write the PRD/SDD yet — it's to gather enough context that the docs aren't fabricated:

- The README (or whatever Customer-facing docs path was set, or `README.md` if present)
- The CLAUDE.md (already partially populated by setup at this point)
- Top-level project structure: directories, source files, test files
- Manifest files: `Cargo.toml`, `package.json`, `go.mod`, `pyproject.toml`, etc. — for dependencies and stack
- A handful of representative source files: the entry point if there is one, a couple of core modules
- Any `Dockerfile`, CI config (`.github/workflows/`, `.gitlab-ci.yml`, etc.)
- Any existing `docs/` content even if not formal PRD/SDD

Capture: the tech stack, the deployment model (CLI / library / web service / etc.), the major components and how they relate, key external dependencies, anything observable about code style and conventions.

##### Step B: Ask the user the questions code can't answer

The codebase tells you *what* and *how*; it doesn't tell you *why* or *for whom*. Ask the following batch — group the multiple-choice questions into one `AskUserQuestion` call (it supports multiple questions per call), then ask the open-ended ones in a follow-up `AskUserQuestion` call.

**Multiple-choice questions** (single-select, free-text "Other" always available):

- **Primary audience:** End users (consumer-facing) / Developers (dev tool or library) / Internal team (internal tool) / Mixed audience / Other
- **Deployment model:** CLI tool / Web service or API / Library or SDK / Desktop app / Mobile app / Browser extension / Other
- **Maturity:** Production-shipping / Active maintenance / Early-stage prototype / Research or experiment / Other
- **Project type:** Open-source / Proprietary product / Internal-only tool / Side project / Other

**Open-ended questions** (free-text, ≤ 2-3 sentences each is ideal):

- "In one or two sentences, what does this project do for its users? (the elevator pitch)"
- "What's the main reason this project exists — what problem is it solving?"
- "Are there explicit non-goals — things this project *deliberately* doesn't try to do? (Skip if none come to mind.)"
- "What's one observable behavior you'd point at to say 'this project is working correctly'? (Becomes a baseline acceptance criterion.)"

##### Step C: Generate the seed docs

Create `docs/` if it doesn't exist:

```bash
# POSIX (bash / zsh):
mkdir -p docs

# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path docs | Out-Null
```

Write `docs/prd.md` with this skeleton, filling in from the answers (Step B) and the codebase exploration (Step A):

```markdown
# <Project name> — Product Requirements

## Existing scope

<One-paragraph elevator pitch from Step B's "what does it do" + audience and
deployment model from MC. Synthesize so it reads like a single coherent
project description, not a bulleted list of answers.>

## Why

<From Step B's "why does this project exist". 1-2 paragraphs.>

## Out of scope

<From Step B's non-goals, or "(none specified at bootstrap; will be filled
in as features are planned)" if user skipped.>

## Acceptance criteria (project-level)

<From Step B's "observable behavior". Phrased as a measurable check the
user could perform.>

## Per-feature scope

<Empty section header for now. Each /bees-plan invocation that produces
docs adds a "### Feature: <title>" subsection here.>
```

Write `docs/sdd.md` with this skeleton, filling in from Step A (codebase exploration). On greenfield (we won't get here per the skip-rule above, but if for any reason we do): leave sections as stub placeholders. On established projects, populate as much as the codebase reveals:

```markdown
# <Project name> — Software Design

## Tech stack

<Languages, frameworks, key libraries — pulled from manifest files.>

## Architecture overview

<2-3 paragraphs describing the major components and how they interact.
Drawn from top-level directory structure + entry point + a couple of
core modules.>

## Key components

<Bulleted list, one per major module/package/directory. One sentence each
describing what it does.>

## External dependencies

<Storage, queues, external services, auth providers — anything observable
in the code.>

## Deployment

<From Dockerfile, CI config, README install instructions. If not detectable,
mark as "(not yet documented)".>

## Per-feature design

<Empty section header for now. Each /bees-plan invocation that produces
docs adds a "### Feature: <title>" subsection here.>
```

##### Step D: Show drafts and apply

Show both files to the user before writing. Use `AskUserQuestion`: "Here are the bootstrap docs I'd write. Apply them as-is, edit before applying, or cancel the bootstrap?"

If applied, write the files to disk and update the `## Documentation Locations` section in CLAUDE.md so the PRD and SDD rows point at the new files.

##### Step E: Tell the user how the docs grow from here

After the bootstrap completes, leave the user with this note:

> The docs you just bootstrapped are starter content. They'll grow incrementally as you use the workflow:
> - **`/bees-plan`** for new features adds a "Feature: <title>" subsection to both `docs/prd.md` and `docs/sdd.md`.
> - **`/bees-fix-issue`** for bug fixes that change documented behavior updates the relevant section.
> - **`/bees-execute`** Doc Writer keeps the architecture sections in sync with what the Engineer actually built.
>
> You don't need to maintain the docs by hand — the workflow handles it. You just need to keep using it.

#### If the user picks option 2 (Defer)

Don't bootstrap. Continue to Build Commands. Make sure CLAUDE.md `## Documentation Locations` has empty values for PRD and Internal architecture docs (so a future `/bees-plan` invocation will detect missing docs and offer Path 2 there).

#### If the user picks option 3 (Skip permanently — body-as-spec)

Don't bootstrap. Continue to Build Commands. Same CLAUDE.md state as Defer.

### Build Commands

After Documentation Locations is set, walk the user through the project's build/test/format/lint commands. The bees workflow's downstream skills (`bees-execute`, `bees-fix-issue`) read these commands from CLAUDE.md instead of hardcoding language-specific tooling, so the workflow works on Rust, Node, Python, Go, and other stacks without per-skill editing.

**First, detect existing configuration.** Read CLAUDE.md. If a `## Build Commands` section already exists with all five required keys (Compile/type-check, Format, Lint, Narrow test, Full test) populated, show the user the current values and ask whether to keep or change each one. **Do not blindly re-prompt the user for commands that are already set** — only prompt for slots that are missing or that the user explicitly wants to change. If every slot is already set and the user wants to keep all of them, this section is a no-op on this run.

**This section is required.** Unlike Documentation Locations, the user cannot skip the Build Commands walkthrough on first-time setup. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The walkthrough must complete before setup is considered complete.

#### Detect the stack

Inspect the repo for one or more of these manifest files to identify the stack and propose sensible defaults:

| Manifest | Stack | Proposed defaults |
|---|---|---|
| `Cargo.toml` (with `[workspace]`) | Rust workspace | `cargo check --workspace` / `cargo fmt` / `cargo clippy --workspace --all-targets -- -D warnings` / `cargo test -p <crate>` / `cargo test --workspace` |
| `Cargo.toml` (single crate) | Rust crate | `cargo check` / `cargo fmt` / `cargo clippy --all-targets -- -D warnings` / `cargo test --lib` / `cargo test` |
| `package.json` + `tsconfig.json` | Node/TypeScript | `tsc --noEmit` / `prettier --write .` / `eslint .` / `vitest run <path>` / `vitest run` |
| `package.json` (no tsconfig) | Node/JavaScript | (skip Compile/type-check or use empty default) / `prettier --write .` / `eslint .` / `vitest run <path>` / `vitest run` |
| `package.json` + `jest.config.*` | Node + jest | substitute `jest <path>` / `jest` for the test slots above |
| `pyproject.toml` or `setup.py` | Python | `mypy .` / `black .` / `ruff check .` / `pytest <path>` / `pytest` |
| `pyproject.toml` + `poetry.lock` | Python (Poetry) | prefix the Python defaults with `poetry run` |
| `go.mod` | Go | `go build ./...` / `gofmt -w .` / `golangci-lint run` / `go test ./<pkg>/...` / `go test ./...` |
| `pom.xml` or `build.gradle` | Java | `mvn compile` (or `gradle build`) / no format default — ask user / no lint default — ask user / `mvn test -Dtest=<name>` / `mvn test` |
| (none of the above) | Other / unknown | No defaults — prompt the user to fill each command manually. |

If multiple manifests are present (polyglot repo or monorepo), surface this to the user and ask which stack the workflow should target. Polyglot projects may need to wrap commands in a per-package script — that's the user's choice, not the skill's.

#### Walk through each command slot

Use `AskUserQuestion` once per command slot, surfacing the detected default as the recommended option. Walk all five slots in order:

1. **Compile/type-check** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command" / (for interpreted languages with no static type-checker) "This project has no type-check step — leave empty".
2. **Format** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
3. **Lint** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
4. **Narrow test** (single file or package) — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
5. **Full test** (whole suite) — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".

For the Compile/type-check slot, an empty value is acceptable for interpreted languages without a static type-checker. For all four other slots, an empty value is **not** acceptable — re-prompt with the recommended default and a note that downstream skills require a value.

You may batch related questions into a single `AskUserQuestion` call if the proposed defaults are clearly correct (e.g., for an obviously-Rust workspace project) — but the user must always be able to override any individual command.

#### Writing the CLAUDE.md section

Do NOT volunteer the following context unless the user asks what each command slot is for:
- **Compile/type-check**: Used by the Engineer agent in `bees-execute` and `bees-fix-issue` after each significant change to catch errors early before moving to the next subtask. May be empty for interpreted languages.
- **Format**: Used by `bees-execute` and `bees-fix-issue` to normalize formatting at commit time, so agent-induced reformatting in unrelated files is consistent.
- **Lint**: Used by the Engineer agent in `bees-execute` and `bees-fix-issue` at subtask boundary, and by the Code Reviewer during quality gates.
- **Narrow test**: Used by Engineer / Test Writer agents while iterating on a single file or package, to keep feedback loops fast.
- **Full test**: Used at the Task's authoritative final-validation subtask in `bees-execute`, and at the end of `bees-fix-issue` after the Engineer completes the fix.

Then write or update a `## Build Commands` section in the project's CLAUDE.md, using this exact format:

```markdown
## Build Commands

- **Compile/type-check**: <command>
- **Format**: <command>
- **Lint**: <command>
- **Narrow test**: <command>
- **Full test**: <command>
```

The bullet keys (`Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`) are a contract — downstream skills look up commands by these exact strings. Do not rename them.

### Next Steps

After setup is complete, tell the user that the bees workflow is ready to use. CLAUDE.md now contains both a `## Documentation Locations` section (consumed by Doc Writer / Engineer / Test Writer agents during execution) and a `## Build Commands` section (consumed by Engineer agents in `bees-execute` and `bees-fix-issue` for compile/format/lint/test invocations). Both are precondition checks for the downstream workflow skills — running `/bees-execute`, `/bees-fix-issue`, `/bees-plan-from-specs`, or `/bees-file-issue` against a repo missing either section will hard-fail with `Run /bees-setup first.`

The next-step recommendation depends on whether the user already has spec docs (a PRD and SDD, or equivalent) on disk. Use `AskUserQuestion` to find out, then surface the matching path:

- **Yes, the user has finalized PRD and SDD documents** → recommend:

  ```
  /bees-plan-from-specs <path-to-PRD> <path-to-SDD>
  ```

  `/bees-plan-from-specs` reads both documents, creates a Plan Bee in the Plans hive with the two paths as its `egg`, decomposes the work into Epics, and chains into `/bees-breakdown-epic`. This is the right choice when scope and design are already nailed down and just need to be turned into a plan.

- **No PRD/SDD yet, or the user wants to start from "I have an idea"** → recommend:

  ```
  /bees-plan [optional one-line description]
  ```

  `/bees-plan` is interactive — it asks clarifying questions to define scope, optionally drafts PRD/SDD updates if the project has those docs, then creates a Plan Bee with Epics. The Plan Bee body itself becomes the authoritative scope document when no PRD/SDD exist (the Bee's `egg` field stays empty), and downstream skills (`/bees-breakdown-epic`, `/bees-execute`) will use the Bee body as the spec source. This is the right choice for fresh ideas, refactors, infra work, or any feature that doesn't yet have a written spec.

Both paths converge on the same Plan Bee shape (top-level Bee in the Plans hive with Epic children). The downstream chain — `/bees-breakdown-epic` → `/bees-execute` → `/bees-fix-issue` for any issues — works the same way for either entry point.
