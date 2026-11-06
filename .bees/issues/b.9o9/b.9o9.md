---
id: b.9o9
type: bee
title: Test review stops file-scanning tests growing into parsers; deferral timestamps read the clock
status: open
created_at: '2026-11-06T11:27:55.151837'
schema_version: '0.1'
reference_materials: null
guid: 9o91iy8wcyq33fpptuzm663tj3vogoc6
---

## Description

Two small defects from a live_edit `/quo-execute` run, plan b.f9p, Epic 2 (2026-11-05/06). The overseer's review is summarized here; the evidence is in container scratch, mirrored on the host at `~/.quorum-scratch`.

### 1. Tests that scan files grow into parsers

**What happens.** A guard test, one that scans project files to enforce a rule, grew over review rounds into a Cargo-manifest checker: an allowlist, single-quoted TOML, `[replace]`/`[patch]`, then scans of `Cargo.lock` and `.cargo/config.toml`.
- **The reviewer drove it.** Each round, the reviewer framed an unusual input format as a bypass defect and marked "extend the scanner" `[preferred]`. The orchestrator then followed `[preferred]` under Step 1, correctly.
- **The end-of-lane pass amplified it once.** The site enumeration (`quo-test-writer-review` `## Confirming pass`, "every site the unit's change introduced") was read as "every form the scanner could meet". Round 4 found 11 gaps; 6 were scanner coverage against unusual sources.

**Evidence:**
- Epic 2 Task 1: `compromises-20261105-2258-d352d2.md` C9, C10, C11, and manifest `run-state-quo-execute-b.f9p.md` :330-342.
- The same pattern in Epic 1: `compromises-20261104-1449-w8e1k7.md` C21–C22, where a `[preferred]` scanner extension was chosen over "document what it cannot see", and the next pass found an alias bypass of the extension.
- **Three questions:** twice in two Epics; silent (each round classifies legitimately as earned); not recovered (it took a decider rule). Earned.

**Fix (restructure; one goal sentence at most).** In `skills/quo-test-writer-review/SKILL.md`, where findings and their `[preferred]` paths are judged, so it covers both the regular rounds and the site enumeration, state the goal:
- a test that scans files to enforce a rule covers the forms the project uses;
- forms it doesn't read are named as not read in the test's own description, not parsed;
- the reason: each new form it reads opens more bypasses.

Also make the confirming pass's "sites the unit's change introduced" plainly mean sites in the source under change, if that's a reword of the existing sentence. Fix the class once: find every line that decides this (the memory `feedback_fix_the_class_at_round_one`). Project-neutral: no Cargo or TOML specifics in the prose.

### 2. A timestamp "from your own clock"

**What happens.** Both orchestrators' §9 `Encode in existing ticket` append `## Deferred from /quo-… run (<YYYY-MM-DD HH:MM>)`, "the timestamp authored from your own clock". The model has no clock, so this fails the executable-verb test (CLAUDE.md review criteria). In the Epic 2 run, six ticket headings got made-up times (manifest :17), which the run noticed itself later.

**Fix (a reword, not a new rule):** read the time once with `date -u` (PowerShell `Get-Date -AsUTC`), as Section 13 already does for the `**Cost**` line, in `skills/quo-execute/SKILL.md` ~296 and `skills/quo-fix-issue/SKILL.md` ~321 (a Tier-1 mirror).

## Not quorum's (recorded)

- **Estimates (Epic 2 ran ~2× its estimates, ~1.5–1.8× after removing the decider's interventions):** the planner's estimates; quorum sets none. The live_edit planner should re-base them on the measured phase costs.
- **Compromise 11's path choice:** mostly within Step 1. One gap (an undocumented `.cargo/config.toml`) was a judgment call.
- **The Analyst escalation** fired as designed.
- **The routing reference's "the pick is always one of the paths the reviewer enumerated"** was bent once, sensibly, with a mixed per-gap pick. One weak case, so no change yet.

## Process

One small hand-edit batch and one cold review under the exit rule, with no dedicated validation. Net prose ≈ 0.

