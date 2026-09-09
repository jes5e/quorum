# INVENTORY — mechanism-level unification of `/quo-fix-issue` and `/quo-execute`

Inputs: `fix-issue-CONSOLIDATED.md` (1,177 rules, 35 mechanisms, FX-* IDs), `execute-CONSOLIDATED.md` (790 rules, 35 mechanisms, EX-* IDs), `agents-roles.md` (494 rules, R-* IDs; its `## Contract surface` is reproduced in EDGES.md). This file does not reproduce rule rows; every count below references the consolidated files by ID.

**Dedupe method.** The two skills' mechanism sets were paired by function (28 pairs incl. one split: fix-issue's SRGATE = execute's EX-POST-62..75). Inside a pair, an EX rule that states the same instruction as one or more FX rules (Mirror `yes` in either extract, or textually identical up to the unit noun Issue/Task/Bee) counts ONCE; the pairing is enumerated in `## Mirror map` and the combined count is `FX + EX − EX rules covered by the map`. Fix-issue's extract is finer-grained than execute's, so combined counts sit near the FX count for fully-mirrored mechanisms. Counts marked ≈ are computed from the mirror map below and carry ±3 uncertainty where the two extracts merged sentences differently. Literal counts are the distinct verbatim strings in the two header `Literals` bullets after cross-skill union (skill-name variants such as `Encode deferral: /quo-fix-issue …` / `… /quo-execute …` count once). Class split = procedure/rationale/example/failure-narrative.

## Unified mechanism table

| # | Unified mechanism | Scope | FX rules | EX rules | FX n | EX n | Combined ≈ | Literals ≈ | TaskList rows FX / EX | Class split FX · EX | Divergence / notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Preconditions & contract keys | shared | FX-PRE-1..17 | EX-PRE-1..16 | 17 | 16 | 21 | 26 | 0 / 0 | 15/2/0/0 · 12/3/1/0 | Eight roles (incl. `analyst`) vs seven; Issues hive vs Plans hive. Hard-fail strings identical. |
| 2 | Session-effort gate | shared | FX-EFF-1..23 | EX-EFF-1..21 | 23 | 21 | 24 | 15 | 5 / 6 | 20/3/0/0 · 14/7/0/0 | Floor `medium` in both. Fully mirrored except section-ordinal references. |
| 3 | Isolation strategy | shared | FX-ISO-1..15 | EX-ISO-1..10 | 15 | 10 | 17 | 16 | 0 / 1 | 12/3/0/0 · 8/2/0/0 | Fix prompts by mode + `main`; exec always prompts in Scenario B. Fix fires no `gate-*` task (FX inconsistency 8). Option-1 label differs. |
| 4 | Run-state manifest | shared (lead statements only) | FX-MAN-1..45 | EX-MAN-1..48 | 45 | 48 | 77 | 50 | 1 / 0 | 33/10/1/1 · 37/11/0/0 | Discriminator `<repo-dir-name>` vs `<bee-id>`; exec adds placeholder resolution (EX-MAN-32..40) and `Multi-Epic run mode`; fix adds `Unit scope` validation (FX-MAN-20/21). Only the five lead statements are byte-mandated (CLAUDE.md). |
| 5 | Reconciliation loop | shared skeleton | FX-LOOP-1..35 | EX-LOOP-1..24 | 35 | 24 | 47 | 30 | 4 / 4 | 32/2/1/0 · 22/2/0/0 | Fix: Phase A/B/C ladder (FX-LOOP-13..29). Exec: per-Subtask fan-out (EX-LOOP-4..7, 12..15). Cold-dispatch shape rows EX-LOOP-18..21,24 are paired under #10. |
| 6 | Post-compaction recovery | shared core, fix-heavy | FX-RECOV-1..37 | EX-PCR-1..8 | 37 | 8 | 44 | 13 | 19 / 2 | 35/1/0/1 · 6/2/0/0 | Fix adds Analyst re-derivation shape and TaskList-derived resume arms (FX-RECOV-8..34). Both: no self-clear/compact lever. |
| 7 | Engineer-dispatch precondition | shared | FX-ENGPRE-1..20 | EX-EDP-1..20 | 20 | 20 | 31 | 28 | 11 / 13 | 15/5/0/0 · 15/5/0/0 | Prefix lists differ; fix excludes Code Reviewer, exec Clause 2 includes it; exec has two clauses + `bees show-ticket` parent resolution. |
| 8 | Movement rung & `aborted-*` markers | shared | FX-MOVE-1..29 | EX-MOV-1..33 | 29 | 33 | 40 | 24 | 10 / 16 | 28/0/0/1 · 30/3/0/0 | Fix = strict branch (any movement anomalous; Engineer mover = breach). Exec = sibling-concurrency observation + bees `in_progress` corrective (EX-MOV-16..21). |
| 9 | Unexplained-movement gate | shared | FX-UNEXP-1..14 | EX-UMG-1..15 | 14 | 15 | 17 | 8 | 6 / 8 | 14/0/0/0 · 15/0/0/0 | Third option `Abort this Issue` vs `Abort this unit`; routes to different close-outs. |
| 10 | Dispatch prompt shape | shared | FX-PROMPT-1..46 | EX-DPS-1..32 + EX-LOOP-18..21,24 | 46 | 37 | 56 | 26 | 2 / 1 | 42/4/0/0 · 25/7/0/0 | Fix-only: directive embedding (8..12), `## Blast radius` relay (25..30), `reference_materials` (41..43). Exec-only: Subtask-scoped fingerprint union (EX-DPS-6..11), lane-scoped no-Engineer wording, post-compaction qualification (30/31). |
| 11 | Roles & lane boundaries | shared | FX-ROLES-1..29 | EX-ROLES-1..15 | 29 | 15 | 29 | 25 | 0 / 0 | 24/0/5/0 · 13/1/1/0 | Fix adds Analyst and `reference_materials` resolver enumeration (20..24); exec adds `<title>` relay (EX-ROLES-9). |
| 12 | TaskList progress UI & naming | shared | FX-TASK-1..31 | EX-TL-1..24 | 31 | 24 | 37 | 55 | 29 / 22 | 30/1/0/0 · 21/3/0/0 | Scope suffixes differ (`<issue-id>` vs `<subtask-id>`/`<task-id>`/`<bee-id>`); `-r<n>`, `-rev<n>` (fix), postcomp `-r<k>`, `defer-*`, `gate-*` identical. |
| 13 | `gate-*` two-step contract | shared | FX-GATE-1..12 | EX-GATE-1..14 | 12 | 14 | 14 | 9 | 10 / 9 | 10/2/0/0 · 13/1/0/0 | Gate enumerations both incomplete (FX inc. 7, EX inc. 3). |
| 14 | Scoped-marker PM wiring | shared | FX-SCOPED-1..5 | EX-SMW-1..4 | 5 | 4 | 6 | 6 | 0 / 0 | 5/0/0/0 · 4/0/0/0 | Path B (fix) vs Path A (exec) — deliberate. |
| 15 | Routing discipline (ODR + SBL) | shared | FX-ROUTE-1..127 | EX-ROUTE-1..94 | 127 | 94 | 139 | 48 | 8 / 9 | 118/8/1/0 · 83/11/0/0 | SBL byte-identical (verified). Nine documented divergences: approved-design source (FX-47 / EX-37), blocker base pair (FX-62 / EX-47), `Cancel` at (c) (FX-88 / EX-49,65), gate-(d) blocker set (FX-101,102 / EX-74,75), gate-(d) `Cancel` semantics (FX-110 / EX-81), filing-failure Cancel (FX-119 / EX-87), part-(g) rung (FX-122 / EX-91), zero-path free-text (EX-76 only), Defer precedent cross-ref (EX-61). |
| 16 | Review loop & trailer consumption | shared | FX-REVIEW-1..10 | EX-BEEREV-1..15 | 10 | 15 | 18 | 24 | 0 / 7 | 9/0/1/0 · 12/3/0/0 | Fix: Phase C per Issue, PM always (FX-REVIEW-4). Exec: three reviewers once per Bee, PM optional (EX-BEEREV-9), Bee-level close-out (10..15). |
| 17 | Ignored-feedback / `defer-*` ledger | shared | FX-LEDGER-1..12 | EX-DEFER-1..13 | 12 | 13 | 14 | 12 | 8 / 6 | 11/1/0/0 · 9/4/0/0 | Label spelling `addressed-now-in-this-Task` (both, PM) vs `-Issue` (fix, Analyst). |
| 18 | Per-unit close-out & commit | shared | FX-CLOSE-1..29 | EX-CLEAN-1..31 | 29 | 31 | 46 | 38 | 3 / 4 | 24/5/0/0 · 28/2/1/0 | Commit subject `Fix issue: <title> (<issue-id>)` vs `Plan <bee-id>, Epic N, Task M — … (<task-id>)`; Issues vs Plans hive; `hive_commit.py` sibling vs own dir; fix idempotent flip (FX-CLOSE-2/3); exec summary rows 24..31 pair under #19. |
| 19 | Summary templates & second-order relay | shared | FX-SUM-1..26 | EX-SUMM-1..14, EX-SOE-1..14 | 26 | 28 | 34 | 35 | 0 / 0 | 25/1/0/0 · 12/2/0/0 + 11/3/0/0 | Headings/fields differ per unit; `**Second-order effects**` unconditional and `**Accepted compromises**` conditional in both. |
| 20 | Boundary state-externalization checkpoint | shared | FX-CKPT-1..32 | EX-CKPT-1..32 | 32 | 32 | 46 | 22 | 5 / 7 | 30/2/0/0 · 31/1/0/0 | Fix verifies commit by `--grep '(<issue-id>)' <pre-session-sha>..HEAD`; exec by `git log <previous-epic-last-commit>..HEAD` one-per-Task; exec has two aborted-scope qualifications + all-done exception (EX-CKPT-18..21). |
| 21 | Context-window boundary guard | shared | FX-GUARD-1..39 | EX-CWG-1..28 | 39 | 28 | 41 | 34 | 1 / 2 | 36/3/0/0 · 26/2/0/0 | Resume command text; fix's aborted-path exclusion (FX-GUARD-3) and `<remaining-ids>` derivation (FX-GUARD-18). |
| 22 | Aborted close-out | shared | FX-ABORT-1..31 | EX-ABORT-1..20 | 31 | 20 | 40 | 15 | 11 / 6 | 28/2/0/1 · 16/3/0/1 | Fix: 4 steps incl. HYG step 2, mode branch (single/batch-exhausted → Section 8; batch-remaining → stop). Exec: 3 steps, always ends run, two scopes (mid-Epic / Bee-level). |
| 23 | Deferral-hygiene gate | shared | FX-HYG-1..86 | EX-DHG-1..37 | 86 | 37 | 90 | 30 | 19 / 15 | 75/9/2/0 · 31/6/0/0 | Skill-name literals in heading/subject/`--skill`; fix has three firings (fixed, aborted, batch-end) with surface-1 carve-out; `hive_commit.py` resolution differs (FX-HYG-72 / EX-DHG-29). |
| 24 | Compromise tracker | shared | FX-TRACK-1..81 | EX-TRK-1..40 | 81 | 40 | 81 | 32 | 0 / 0 | 74/6/1/0 · 32/8/0/0 | Fully mirrored (file, entry shape, Decision enum, Triggers A–D). Notation drift `YYYYMMDD-HHMM` vs `<YYYYMMDD-HHMM>` (EX inc. 10). |
| 25 | Post-completion review | shared | FX-POSTC-1..100 | EX-POST-1..61 | 100 | 61 | 111 | 55 | 13 / 15 | 93/6/1/0 · ≈50/9/2/0 | Diff scope: `git diff <pre-session-sha>..HEAD` vs `git diff <pre-bee-sha>` + untracked files (EX-POST-13); fix-only `## Design question` route (FX-POSTC-76..81); prompt opener noun; `HEAD~N` vs `HEAD~M` fallback. |
| 26 | Compromise-challenge recovery gates | shared | FX-SRGATE-1..21 | EX-POST-62..75 | 21 | 14 | 21 | 10 | 3 / (in #25) | 21/0/0/0 · 13/1/0/0 | Fully mirrored; labels pinned to #24 Trigger D. |
| 27 | Shell etiquette & scratch convention | shared | FX-SHELL-1..5 | EX-SHELL-1..4 | 5 | 4 | 7 | 10 | 0 / 0 | 4/1/0/0 · 3/1/0/0 | Exec homes never-push and no-`git add -A` here; fix homes them in CLOSE (FX-CLOSE-6/15). |
| 28 | Argument parsing & URL resolution | fix-issue-only | FX-ARG-1..56 | — | 56 | — | 56 | 35 | 4 / — | 51/3/2/0 | Six invocation forms; `/quo-file-issue` inline Skill precedent reused by #15, #21, #23, #26. |
| 29 | Issue validation | fix-issue-only | FX-VAL-1..11 | — | 11 | — | 11 | 8 | 0 / — | 11/0/0/0 | FX-VAL-11 conflicts with FX-CLOSE-29 (FX inc. 1). |
| 30 | Analyst dispatch & design gate | fix-issue-only | FX-ANA-1..61 | — | 61 | — | 61 | 35 | 5 / — | 52/9/0/0 | Four verdict-keyed preamble templates (27..30). |
| 31 | Deferred-refinements consumption | fix-issue-only | FX-DEFC-1..19 | — | 19 | — | 19 | 8 | 7 / — | 14/5/0/0 | Supersede-and-clear (13..17). |
| 32 | Design directive | fix-issue-only | FX-DIR-1..8 | — | 8 | — | 8 | 8 | 0 / — | 8/0/0/0 | |
| 33 | Design-question receiver & Analyst re-dispatch | fix-issue-only | FX-DQ-1..25 | — | 25 | — | 25 | 8 | 10 / — | 24/0/0/1 | Section 3 Revise by reference; close-out sweep (19..24). |
| 34 | Doc verification | fix-issue-only | FX-DOCV-1..7 | — | 7 | — | 7 | 5 | 0 / — | 7/0/0/0 | Informational only. |
| 35 | GitHub close recommendation | fix-issue-only | FX-GH-1..33 | — | 33 | — | 33 | 12 | 0 / — | 29/4/0/0 | Keys on `(<issue-id>)` subject token. |
| 36 | Frontmatter & overview | execute-only | — | EX-META-1..9 | — | 9 | 9 | 3 | — / 0 | 9/0/0/0 | Stale "Team" vocabulary (EX inc. 9); typo "therin". |
| 37 | Bee selection & validation | execute-only | — | EX-BEE-1..10 | — | 10 | 10 | 10 | — / 2 | 10/0/0/0 | |
| 38 | Epic selection, run-mode gate, staleness | execute-only | — | EX-EPIC-1..17 | — | 17 | 17 | 12 | — / 1 | 17/0/0/0 | Mode 1/2 captured once. |
| 39 | Per-Task PM dispatch | execute-only | — | EX-PMD-1..4 | — | 4 | 4 | 5 | — / 1 | 4/0/0/0 | |
| 40 | Testing discipline (five-rung ladder) | execute-only | — | EX-TEST-1..12 | — | 12 | 12 | 12 | — / 0 | 11/1/0/0 | Rungs 1–4 restate role-file rules (R-173..179, R-238..242, R-409). |
| 41 | Next-Epic routing & inter-Epic checkpoint | execute-only | — | EX-NEXT-1..21 | — | 21 | 21 | 15 | — / 1 | 19/2/0/0 | Director-direct interaction check (EX-NEXT-1); branch-3 contradiction (EX inc. 2). |
| 42 | Final output & Bee flip | execute-only | — | EX-FINAL-1..11 | — | 11 | 11 | 9 | — / 0 | 9/2/0/0 | Three §7 gates. |
| 43 | Merge advice | execute-only | — | EX-MERGE-1..5 | — | 5 | 5 | 8 | — / 0 | 5/0/0/0 | |

## Totals

- Raw deduped inputs: FX 1,177 + EX 790 = 1,967 rules. **Unified after cross-skill dedupe ≈ 1,457** (≈ 510 EX rules collapse onto FX rules via the Mirror map: shared ≈ 1,148; fix-issue-only 220; execute-only 89).
- Mirror pairs enumerated below: **≈ 505 EX rules ↔ FX rules** (Tier 1 byte-identical ≈ 260; Tier 2 identical-modulo-unit-noun ≈ 245). 27 documented divergence pairs are listed separately and are NOT to be pinned.
- TaskList-dependent: FX 194 (16.5%), EX 158 (20.0%); unified ≈ 240 after collapsing paired TaskList rows (≈ 16% of unified). Mechanisms whose *machinery* is TaskList (would not function without it): #6 (resume arms), #7, #8, #9, #12, #13, #17, #22, #23 (Steps 0–3 and hard-stop), #31, #33, plus the gate-task step of every gate site and the lane-tracking of #5, #16, #18, #25.
- Class: FX 1,059 / 98 / 15 / 5; EX 676 / 108 / 5 / 1. Unified rationale ≈ 150 rules (≈ 10%) — candidates for a reference file.
- Literals: fix-issue index ≈ 270 rows (several multi-literal); execute index 528 distinct strings; cross-skill union ≈ 600 distinct strings, of which ≈ 330 are shared (same string in both skills) and ≈ 80 are unit-noun variants of a shared string.
- Current text: fix-issue SKILL.md ≈ 1,342 lines; execute SKILL.md ≈ 1,322 lines. Largest sites: fix ROUTE L620–702 (83 very long lines), POSTC L1114–1270 (157), HYG+TRACK L981–1112 (130), GUARD L859–946 (88), LOOP/RECOV/MOVE/DQ L370–471 (100); exec POST L933–1114 (182), DHG+TRK L1118–1236 (120), CWG L666–770 (105), LOOP L291–436 (100), ROUTE L789–865 (77).

## Mirror map

One row per EX rule (or contiguous EX group) that must stay identical with the listed FX rule(s). **Tier 1** = byte-identical text (literals, labels, enum values, fixed lines, the CLAUDE.md-mandated manifest lead statements). **Tier 2** = identical modulo the unit noun (`Issue` ↔ `Task`/`Subtask`/`Bee`), the section ordinal, or the skill name inside a literal. The rewrite's mirror test should pin Tier 1 byte-for-byte and Tier 2 after a fixed noun/ordinal substitution. Rows in `### Documented divergences` must NOT be pinned.

### #1 Preconditions
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-PRE-1, FX-PRE-15 | EX-PRE-1, EX-PRE-2, EX-PRE-16 | 1 | `Run /quo-setup first.` + one-line note |
| FX-PRE-3 | EX-PRE-4 | 1 | session-load semantics |
| FX-PRE-4, FX-PRE-5 | EX-PRE-5, EX-PRE-8 | 2 | trigger `Agent type '<name>' not found`; role count differs |
| FX-PRE-6 | EX-PRE-6, EX-PRE-7 | 1 | hard-fail message text |
| FX-PRE-8, FX-PRE-9 | EX-PRE-11, EX-PRE-12 | 1 | Specs hive + message |
| FX-PRE-10, FX-PRE-11 | EX-PRE-13 | 1 | `## Documentation Locations` |
| FX-PRE-12, FX-PRE-13 | EX-PRE-14 | 1 | `## Build Commands` five keys |
| FX-PRE-14, FX-PRE-16, FX-PRE-17 | EX-PRE-15, EX-PRE-16, EX-PRE-9 | 2 | rationale |

### #2 Session-effort gate
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-EFF-1, -2, -3 | EX-EFF-2, -3 | 2 | ordering vs other §1 gates |
| FX-EFF-4..7 | EX-EFF-4..7 | 1 | |
| FX-EFF-8, -23 | EX-EFF-8 | 1 | read-before-TaskCreate |
| FX-EFF-9, -10, -11, -12 | EX-EFF-10, -11, -12, -13 | 1 | commands, unset handling |
| FX-EFF-13, -14, -15 | EX-EFF-14, -15 | 1 | floor, ordering, rationale |
| FX-EFF-16, -17, -18 | EX-EFF-1, -16, -17 | 1 | |
| FX-EFF-19, -20 | EX-EFF-18, -19 | 1 | question text verbatim |
| FX-EFF-21, -22 | EX-EFF-20, -21 | 1 | `Proceed anyway` / `Let me change it first` |
| FX-GATE-11 | EX-EFF-9 | 1 | stranded-gate rationale |

### #3 Isolation
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-ISO-1, -3 | EX-ISO-1 | 2 | |
| FX-ISO-4 | EX-ISO-2 | 2 | Scenario A |
| FX-ISO-5 | EX-ISO-3 | 2 | Scenario B |
| FX-ISO-10 | EX-ISO-4, -5 | 2 | option 1 body (label differs — divergence) |
| FX-ISO-11 | EX-ISO-6 | 1 | `Work on current branch` |
| FX-ISO-12 | EX-ISO-7, -8, -9 | 1 | `Set up a worktree instead` + omit rule |
| FX-ISO-13 | EX-ISO-10 | 2 | question must state cwd/branch/local-only |

### #4 Run-state manifest (lead statements = Tier 1 mandated by CLAUDE.md)
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-MAN-1 | EX-MAN-1 | 1 | canonical anchor `#### Write the run-state manifest` |
| FX-MAN-3 | EX-MAN-3 | 1 | "values that live **nowhere else on disk**" |
| FX-MAN-4 | EX-MAN-3 | 1 | four-carrier enumeration ("those four") |
| FX-MAN-5 | EX-MAN-6 | 1 | "makes compaction survivable" |
| FX-MAN-6 | EX-MAN-7 | 1 | `<tempdir>/.quorum/` path boilerplate |
| FX-MAN-11 | EX-MAN-9 | 1 | **deterministic — do NOT add a random suffix or timestamp** |
| FX-MAN-12 | EX-MAN-10 | 2 | tracker-suffix comparison rationale |
| FX-MAN-15 | EX-MAN-15 | 1 | "Every skill … own name in the leading position" |
| FX-MAN-16 | EX-MAN-16 | 1 | discriminator rationale sentence |
| FX-MAN-23, -24 | EX-MAN-18 | 1 | **truncate at run start, rewrite at each boundary** / live snapshot |
| FX-MAN-25, -26 | EX-MAN-4, -5 | 1 | only values with no other durable home; shadow-store rationale |
| FX-MAN-28, -29 | EX-MAN-20, -21 | 2 | `**Skill:**`, `**Run started (UTC):**` |
| FX-MAN-32 | EX-MAN-24 | 1 | `**Isolation strategy:**` enum |
| FX-MAN-34, -35, -36, -37 | EX-MAN-27, -28, -29 | 1 | `**Compromise tracker:**` path incl. suffix; not created at record time |
| FX-MAN-40 | EX-MAN-31 | 2 | `**Next unit:**` |
| FX-MAN-41, -42 | EX-MAN-25, -26 | 2 | `git rev-parse HEAD` once at run start; read back by post-completion |

### #5 Reconciliation loop
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-LOOP-1, -2 | EX-LOOP-1 | 1 | fresh ephemeral background Agents; no team |
| FX-LOOP-4 | EX-LOOP-23 | 1 | warm-dispatch rationale |
| FX-LOOP-5 | EX-LOOP-2 | 1 | Read state / Reconcile / Yield |
| FX-LOOP-6 | EX-LOOP-3 | 1 | four sources |
| FX-LOOP-8, -9 | EX-LOOP-8 | 2 | freeform query |
| FX-LOOP-10 | EX-LOOP-10 | 1 | git diff is the only authoritative record |
| FX-LOOP-11 | EX-PCR-1 | 1 | "Conversation memory is never a substitute…" |
| FX-LOOP-12 | EX-LOOP-13 | 2 | Reconcile |
| FX-LOOP-30 | EX-LOOP-14 | 2 | on completion: confirm bees, mark task, unlock |
| FX-LOOP-31, -34 | EX-LOOP-16 | 1 | Yield; notification is the only trigger |
| FX-LOOP-32, -33 | EX-LOOP-17 | 1 | no `/loop`, `ScheduleWakeup`, `CronCreate`, no polling |
| FX-TASK-3 | EX-LOOP-9 | 1 | task status lifecycle |
| FX-MAN-43 | EX-LOOP-11 | 2 | manifest = fourth source |

### #6 Post-compaction recovery
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-RECOV-1 | EX-PCR-2 | 1 | summarization marker → re-read all four |
| FX-CKPT-31 | EX-PCR-3, -5 | 1 | does not clear/compact; harness owns reclamation |
| FX-CKPT-32 | EX-PCR-4 | 1 | fresh session is the only lever |
| FX-GUARD-5 | EX-PCR-8 | 1 | external gauge is not a self-estimate |

### #7 Engineer-dispatch precondition
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-ENGPRE-2, -15 | EX-EDP-3 | 1 | prefix + status match |
| FX-ENGPRE-3 | EX-EDP-4 | 2 | check, don't remember |
| FX-ENGPRE-8, -12 | EX-EDP-17 | 1 | `pending` stays in the test |
| FX-ENGPRE-9 | EX-EDP-13 | 1 | wait when in_progress / landed |
| FX-ENGPRE-10 | EX-EDP-14 | 1 | pending with no dispatch → act |
| FX-ENGPRE-11 | EX-EDP-15, -16 | 1 | post-compaction default: not landed |
| FX-ENGPRE-13, -14 | EX-EDP-18, -19 | 1 | `aborted-` distinct class; no metadata routing |
| FX-ENGPRE-18, -19, -20 | EX-POST-56, -57 | 1 | postcomp restatement |

### #8 Movement rung
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-MOVE-1, -2 | EX-MOV-3 | 1 | writer-side half in role files |
| FX-MOVE-3 | EX-MOV-4 | 2 | receiver rationale |
| FX-MOVE-4 | EX-MOV-5 | 1 | read return before persisting |
| FX-MOVE-5, -10 | EX-MOV-7 | 1 | "stopped" is the marker |
| FX-MOVE-11 | EX-MOV-8, -9 | 1 | obligation-as-pending-task pattern |
| FX-MOVE-12 | EX-MOV-10, -11 | 2 | step 1 mark own task completed |
| FX-MOVE-13, -14 | EX-MOV-12, -13 | 2 | step 2 `aborted-<role>-<id>` pending + metadata |
| FX-MOVE-15 | EX-MOV-15 | 2 | advance gate on `aborted-` prefix + pending |
| FX-MOVE-16 | EX-MOV-14 | 1 | metadata informational |
| FX-MOVE-18 | EX-MOV-23, -24 | 2 | Engineer mover: let review close first |
| FX-MOVE-19 | EX-MOV-27 | 1 | `## Perturbations` contract |
| FX-MOVE-20, -21 | EX-MOV-28 | 1 | full vs partial coverage |
| FX-MOVE-22, -23 | EX-MOV-29 | 1 | wait for in-flight Test Writer |
| FX-MOVE-25 | EX-MOV-30 | 1 | external actor |
| FX-MOVE-26 | EX-MOV-31 | 1 | carry "how far I got" |
| FX-MOVE-27 | EX-MOV-32 | 2 | completion releases gate |
| FX-MOVE-28 | EX-MOV-33 | 1 | repeat rung, never second marker |
| FX-MOVE-29 | EX-MOV-1, -2 | 1 | movement report ≠ completion |

### #9 Unexplained-movement gate
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-UNEXP-1, -2 | EX-UMG-1, -2 | 2 | |
| FX-UNEXP-3 | EX-UMG-3 | 1 | two-step |
| FX-UNEXP-4, -5 | EX-UMG-4 | 2 | question text (unit noun) |
| FX-UNEXP-6 | EX-UMG-5 | 1 | three options |
| FX-UNEXP-7 | EX-UMG-6 | 1 | `Re-dispatch the writer now` |
| FX-UNEXP-8, -9, -10, -11 | EX-UMG-7, -8, -9, -10, -11 | 1 | `Wait` semantics |
| FX-UNEXP-13, -14 | EX-UMG-14, -15 | 1 | close gate task; fresh task on re-fire |

### #10 Dispatch prompt shape
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-PROMPT-1, -2 | EX-LOOP-18 | 2 | `Agent(subagent_type=<role>, run_in_background=true, prompt=…)` |
| FX-PROMPT-3 | EX-LOOP-19 | 1 | no `Agent(name=...)`, no reuse |
| FX-PROMPT-4, -5, -6 | EX-DPS-1, -2 | 1 | body verbatim; framing prose fine |
| FX-PROMPT-7 | EX-DPS-3 | 1 | no ping-back |
| FX-PROMPT-13, -14 | EX-DPS-23, -24 | 1 | `## Engineer's completeness evidence`, inline not file |
| FX-PROMPT-15 | EX-DPS-32 | 1 | code-reviewer forwards |
| FX-PROMPT-16, -17 | EX-DPS-22, -26 | 1 | sweep-shaped statement |
| FX-PROMPT-18 | EX-DPS-28 | 1 | omit heading when no list |
| FX-PROMPT-24 | EX-DPS-27 | 1 | unnamed sweep loses check |
| FX-PROMPT-31 | EX-DPS-18 | 2 | no-Engineer wording (scope qualifier differs) |
| FX-PROMPT-32, -33 | EX-DPS-19, -20, -21 | 1 | never "frozen" |
| FX-PROMPT-34, -35 | EX-DPS-4, -5 | 1 | `## Source paths to fingerprint` from `## Files changed` |
| FX-PROMPT-36 | EX-DPS-14 | 1 | empty list is a list |
| FX-PROMPT-37, -40 | EX-DPS-16, -17 | 1 | omit heading when empty |
| FX-PROMPT-38, -39 | EX-DPS-12, -13, -15 | 2 | `git diff --name-only HEAD` fallback |
| FX-PROMPT-44, -45 | EX-LOOP-20, -21 | 1 | hub-and-spoke; no `SendMessage` |
| FX-PROMPT-46 | EX-LOOP-24 | 1 | flat orchestration |

### #11 Roles
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-ROLES-1 | EX-ROLES-1 | 1 | never loosen role boundaries |
| FX-ROLES-2..6 | EX-ROLES-2 | 1 | five forbidden softenings |
| FX-ROLES-7, -8 | EX-ROLES-3, -4 | 1 | |
| FX-ROLES-9 | EX-ROLES-5 | 2 | dispatch roles, don't carry prose |
| FX-ROLES-10, -11, -12 | EX-ROLES-6, -7, -8 | 2 | Engineer / Test Writer / Doc Writer |
| FX-ROLES-19, -23 | EX-ROLES-11, -13 | 2 | PM; `agents/pm.md` authoritative |
| FX-ROLES-15, -16, -17, -18 | EX-ROLES-14, -15 | 2 | reviewers |
| FX-ROLES-25 | EX-BEEREV-8 | 1 | stay in delegate mode |

### #12 TaskList naming
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-TASK-1, -2 | EX-TL-1, -2 | 1 | one task per Agent |
| FX-TASK-3..6 | EX-TL-3, -4 | 2 | lifecycle; `completed` = Agent gone |
| FX-TASK-7 | EX-TL-5 | 1 | `metadata.activity` informational |
| FX-TASK-8 | EX-TL-6 | 2 | canonical cross-reference |
| FX-TASK-13, -14, -15 | EX-TL-12, -13, -14 | 1 | `-r<n>`; prefix matching |
| FX-TASK-20, -21 | EX-TL-22 | 2 | namespace coexistence |
| FX-TASK-22..28 | EX-TL-15, -16, -17, -18 | 1 | `<role>-postcomp-<n>`, `-r<k>` carve-out |
| FX-LEDGER-10 | EX-TL-20 | 1 | `defer-<short-suffix>` run scope |
| FX-TASK-19 | EX-TL-21 | 1 | `gate-<kind>-<short-suffix>` |
| FX-ABORT-12 | EX-TL-23, -24 | 1 | "clear" = mark completed, never delete |

### #13 gate-* contract
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-GATE-1 | EX-GATE-2 | 1 | TaskCreate then AskUserQuestion, same turn |
| FX-GATE-2 | EX-GATE-5 | 1 | do not narrate |
| FX-GATE-3 | EX-GATE-3 | 1 | mark completed on consume |
| FX-GATE-4 | EX-GATE-4 | 1 | suffix unique per fire |
| FX-GATE-5 | EX-GATE-6 | 1 | multi-choice only |
| FX-GATE-6, -7, -8 | EX-GATE-7, -8, -9 | 1 | yield-control; re-fire from metadata |
| FX-GATE-10 | EX-EFF-8, EX-CWG-10 | 1 | evaluate before TaskCreate |
| FX-GATE-12 | EX-GATE-14 | 1 | prose-adherence fragility |

### #14 Scoped-marker wiring
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-SCOPED-1, -2, -5 | EX-SMW-1, -2, -4 | 1 | placeholder, sibling path, no inlining |
| FX-SHELL-5 | EX-SMW-3 | 1 | base directory from invocation header |

### #15 Routing discipline (SBL paragraph byte-identical, verified by the E4 extractor)
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-ROUTE-1, -2, -3, -4, -5 | EX-ROUTE-1, -2, -3, -4 | 1 | tags; one decision; never reclassify |
| FX-ROUTE-6, -7 | EX-ROUTE-5, -6 | 1 | SBL: lane held open / closes |
| FX-ROUTE-8, -9, -10 | EX-ROUTE-7, -8 | 1 | outstanding until cold pass; dispatch settles nothing |
| FX-ROUTE-11, -12 | EX-ROUTE-9 | 1 | trivial-tweak nit rides along |
| FX-ROUTE-13, -14 | EX-ROUTE-10 | 1 | final nit pass closes lane |
| FX-SUM-5 (nit clause), FX-ROUTE-15 | EX-ROUTE-11, -12 | 1 | `N nits applied without re-review` / `count unavailable post-compaction` |
| FX-ROUTE-16, -17, -18, -19, -20 | EX-ROUTE-13, -14, -15, -16, -17 | 1 | |
| FX-ROUTE-21..31 | EX-ROUTE-18..25 | 1 | Step 1 pick, `[preferred]`, under-enumeration |
| FX-ROUTE-32..38 | EX-ROUTE-26..32 | 1 | rows 1–6 (EX-32 adds Trigger C ref — FX-ROUTE-39) |
| FX-ROUTE-39, -40, -41 | EX-ROUTE-32, -33, -34 | 2 | row-6 dispatch; row-order rationale; part (g) hook |
| FX-ROUTE-42..46 | EX-ROUTE-35, -36 | 1 | "highest-quality"; "adds a mechanism" |
| FX-ROUTE-48, -49 | EX-ROUTE-38 | 1 | `[introduces-mechanism]` primary; fallback reading |
| FX-ROUTE-50..56 | EX-ROUTE-39..42 | 1 | (b) anti-pattern + forbidden phrasings |
| FX-ROUTE-57, -58, -59 | EX-ROUTE-43 | 1 | (c) four entry conditions |
| FX-ROUTE-60, -61 | EX-ROUTE-44, -45, -46 | 1 | blocker never accepted |
| FX-ROUTE-63 | EX-ROUTE-48 | 1 | blocker `Fix properly now` |
| FX-ROUTE-64..78 | EX-ROUTE-51..57 | 1 | Defer-with-narrowing conditions, coverage guard, file-first, direct dispatch, `(Recommended)` |
| FX-ROUTE-79..86 | EX-ROUTE-58, -60, -61, -62, -63 | 2 | suggestion/nit choice set (section refs differ) |
| FX-ROUTE-87, -89 | EX-ROUTE-64, -66 | 1 | question text; `Ctrl-C` rationale |
| FX-ROUTE-90..94 | EX-ROUTE-67, -68, -69 | 1 | mechanism-row default; sketched design verbatim |
| FX-ROUTE-95..98, -100, -103 | EX-ROUTE-70..73, -77 | 1 | gate (d) blocker Defer rules |
| FX-ROUTE-104..109, -112 | EX-ROUTE-78, -79, -80, -82 | 1 | per-path choices; marker; Defer |
| FX-ROUTE-111 | EX-ABORT-20 | 1 | `Ctrl-C` unconditional |
| FX-ROUTE-113..117 | EX-ROUTE-83..86 | 1 | (e) shim; (f) malformed tags, ambiguity, PM report-note exemption |
| FX-ROUTE-118, -120 | EX-ROUTE-87, -88, -89 | 2 | filing failure (re-prompt set differs — see divergences) |
| FX-ROUTE-121, -123, -124, -125, -126 | EX-ROUTE-90, -92, -93, -94 | 1 | (g) ordering, rationale, elision, no-source case |

### #16 Review loop
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-REVIEW-2 | EX-BEEREV-3 | 2 | conditional spawn |
| FX-REVIEW-5, -6, -7 | EX-BEEREV-5, -6 | 1 | trailers; follow literally |
| FX-REVIEW-8, -9 | EX-BEEREV-7 | 2 | dispatch fresh implementers / PM |
| FX-REVIEW-10 | EX-BEEREV-9 | 1 | may not re-dispatch PM |
| FX-ROUTE-127 | EX-BEEREV-4 | 1 | judgement call |

### #17 defer-* ledger
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-LEDGER-1, -2 | EX-DEFER-13 | 2 | ignored feedback must reach summary/Final Review |
| FX-LEDGER-3, -4 | EX-DEFER-1 | 1 | create at moment of decision; metadata; pending |
| FX-LEDGER-5, -6, -7, -8 | EX-DEFER-3, -4, -5 | 1 | destination annotation required; vague framings forbidden |
| FX-LEDGER-9 | EX-DEFER-6 | 1 | load-bearing source rationale |
| FX-LEDGER-11 | EX-DEFER-9 | 1 | structured-return items |
| FX-LEDGER-12 | EX-DEFER-12 | 1 | completed when encoded |

### #18 Close-out & commit
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-CLOSE-5 | EX-CLEAN-4 | 2 | one commit per unit |
| FX-CLOSE-6 | EX-SHELL-1 | 1 | NEVER push |
| FX-CLOSE-7, -8, -9 | EX-CLEAN-5, -7, -8 | 1 | Format; git status; stage related |
| FX-CLOSE-10, -13, -14 | EX-CLEAN-8, -10, -11 | 2 | in-repo hive staging via helper |
| FX-CLOSE-15, -16 | EX-SHELL-2, EX-CLEAN-11 | 1 | no `git add -A`; judgement-select |
| FX-CLOSE-18 | EX-CLEAN-12 | 1 | descriptive message |
| FX-CLOSE-21, -22 | EX-CLEAN-17, -18, -19, -20 | 2 | prefix sweep incl. `-r<n>` and markers |
| FX-CLOSE-23 | EX-CLEAN-21 | 1 | no Agent shutdown ceremony |
| FX-CLOSE-24 | EX-CLEAN-22 | 1 | aborted path runs same sweep |

### #19 Summaries & second-order relay
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-SUM-4 | EX-CLEAN-26 | 1 | `**Files Changed**` |
| FX-SUM-5 | EX-CLEAN-27, EX-SUMM-3 | 2 | `**Reviews**` (lane slots differ) |
| FX-SUM-7 | EX-CLEAN-28 | 1 | `**Ignored Review Feedback**` |
| FX-SUM-8, -10 | EX-SOE-1, -3, -4, -5, -9 | 2 | destination; collect; narrative not routing |
| FX-SUM-11, -12, -13 | EX-SOE-9, -10, -11 | 1 | verbatim; attribute; de-dupe |
| FX-SUM-14, -15 | EX-SOE-12, -13, -14 | 1 | `None identified.`; unconditional |
| FX-SUM-9, -16 | EX-SUMM-4, -6 | 1 | `**Accepted compromises**` conditional |
| FX-SUM-17, -18 | EX-SUMM-7 | 1 | Read tracker; recover path from manifest |
| FX-SUM-19, -20, -21 | EX-SUMM-8, -9 | 1 | omit when absent/empty |
| FX-SUM-22, -23 | EX-SUMM-10, -11, -12 | 1 | four fields; hide fifth |
| FX-SUM-24, -25 | EX-SUMM-13 | 1 | volume >10 |
| FX-SUM-26 | EX-SUMM-14 | 1 | read-only surface |

### #20 Checkpoint
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-CKPT-1, -2 | EX-CKPT-1, -2, -4 | 2 | definition not step; invoked by name |
| FX-CKPT-4 | EX-CKPT-9 | 1 | verify invariant, refresh carriers |
| FX-CKPT-7, -8, -9 | EX-CKPT-12, -13, -14 | 1 | carriers 3–5 |
| FX-CKPT-10 | EX-CKPT-16 | 1 | every step is a real tool call |
| FX-CKPT-11 | EX-CKPT-17 | 2 | do all four verifications |
| FX-CKPT-19..23 | EX-CKPT-25, -26 | 1 | tracker absent ≠ gap; Trigger C carve-out |
| FX-CKPT-24 | EX-CKPT-27 | 2 | TaskList walk |
| FX-CKPT-25 | EX-CKPT-28 | 1 | fix gaps now |
| FX-CKPT-26 | EX-CKPT-29 | 2 | rewrite manifest |
| FX-CKPT-27, -30 | EX-CKPT-31, -32 | 1 | re-read, do not recall; write missing fact into a carrier |
| FX-CKPT-31, -32 | EX-CKPT-6, EX-PCR-3, -4, -5 | 1 | does not reclaim context |

### #21 Context guard
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-GUARD-1, -4 | EX-CWG-1, -3, -7 | 2 | definition; after checkpoint; not unconditional |
| FX-GUARD-2 | EX-CWG-4, -5, -6 | 2 | never on run-ending paths |
| FX-GUARD-5, -6, -7 | EX-CWG-8, -9 | 1 | external gauge; no self-clear |
| FX-GUARD-8, -9, -10 | EX-CWG-10, -11 | 1 | read session id first; trim |
| FX-GUARD-11, -12 | EX-CWG-12 | 1 | unset → silent skip |
| FX-GUARD-13, -14, -15 | EX-CWG-13, -14 | 1 | helper path; `stop-threshold` never restated |
| FX-GUARD-16, -17, -26 | EX-CWG-15, -16 | 1 | `read`; four outputs; exit non-zero |
| FX-GUARD-19, -20, -21 | EX-CWG-17, -18 | 2 | ≥ threshold stop (resume command differs) |
| FX-GUARD-22, -23, -24, -25 | EX-CWG-19, -20 | 1 | `stale` / non-zero → stop |
| FX-GUARD-27, -28, -29, -30 | EX-CWG-21, -22 | 1 | opt-out marker check |
| FX-GUARD-31, -32 | EX-CWG-23 | 1 | missing-reading gate text |
| FX-GUARD-33, -34, -35, -36, -37, -38 | EX-CWG-24..28 | 2 | four options (resume command differs) |
| FX-GUARD-39 | EX-SMW-3 | 1 | sibling-resolution discipline |

### #22 Aborted close-out
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-ABORT-1, -3 | EX-ABORT-1, -4 | 2 | canonical anchor; definition not step |
| FX-ABORT-2 | EX-ABORT-2 | 2 | entering branches |
| FX-ABORT-6 | EX-ABORT-5 | 2 | failure narrative |
| FX-ABORT-8, -9, -10, -11 | EX-ABORT-7, -8, -12 | 2 | prefix sweep incl. markers + gate task |
| FX-ABORT-13 | EX-ABORT-11 | 1 | cannot terminate background Agent |
| FX-ABORT-19 | EX-ABORT-14 | 2 | checkpoint aborted path |
| FX-ABORT-28 | EX-ABORT-16, -17, -18, -19 | 2 | name unit, uncommitted paths, resume command |

### #23 Deferral-hygiene gate
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-HYG-1 | EX-DHG-1 | 1 | which firings are two-step |
| FX-HYG-2, -5 | EX-DHG-2, -3 | 2 | inter-session deferral framings; pre-handoff reconciliation |
| FX-HYG-4, -6, -7, -11, -12, -16, -17 | EX-DHG-4, -5, -6, -7, -8, -9 | 2 | Step 0 surfaces (fix has three; exec two) |
| FX-HYG-29, -30, -32 | EX-DHG-10, -11 | 1 | Step 1; `Deferral hygiene: no deferred items.` |
| FX-HYG-33, -34 | EX-DHG-12, -13 | 1 | Step 2; three labels |
| FX-HYG-35, -36 | EX-DHG-14 | 1 | Fix branch |
| FX-HYG-37, -38, -39 | EX-DHG-15, -16 | 1 | File branch |
| FX-HYG-40, -41, -45, -46 | EX-DHG-17, -18, -19 | 2 | Encode destinations; heading (skill name inside) |
| FX-HYG-42, -43, -44, -51 | EX-DHG-18, -22 | 1 | `bees update-ticket --body-file`; own-clock timestamp; snippet order |
| FX-HYG-47, -48, -49, -50 | EX-DHG-20, -21 | 1 | `bees-body-<defer-N>.md` |
| FX-HYG-52 | EX-DHG-23 | 1 | mark completed on success |
| FX-HYG-53, -56, -57, -60, -61, -62, -63, -64, -69 | EX-DHG-24, -25, -26 | 2 | follow-up commit; staging; conditional |
| FX-HYG-65, -66 | EX-DHG-27 | 2 | subject (skill name inside); `<N>` counts items |
| FX-HYG-67, -68, -70 | EX-DHG-28, EX-SHELL-2 | 1 | helper as single call; no `git add -A` |
| FX-HYG-74, -75, -76 | EX-DHG-30 | 2 | `--count`, `--doc-path` (`--skill` differs) |
| FX-HYG-77 | EX-DHG-31 | 1 | proceed to Step 3 |
| FX-HYG-78, -79, -80, -81 | EX-DHG-32, -33 | 1 | per-item routing via free-text; all completed |
| FX-HYG-82, -83, -84, -85 | EX-DHG-34, -35, -36 | 2 | hard-stop; re-run until empty |
| FX-HYG-86 | EX-DHG-37 | 1 | fresh-session recommendation preserved |

### #24 Compromise tracker (all Tier 1)
| FX | EX | Note |
|---|---|---|
| FX-TRACK-1, -2, -3 | EX-TRK-1, -2 | definition; four compromise kinds; rationale |
| FX-TRACK-4, -5, -6 | EX-TRK-3 | anchors |
| FX-TRACK-7..11 | EX-TRK-5, -6 | filename; UTC once; suffix; rationale |
| FX-TRACK-12, -13, -14 | EX-TRK-7, -8 | `## Compromise <n>`; SDD shape |
| FX-TRACK-15, -16 | EX-TRK-9, -10 | Finding; Fix paths fields |
| FX-TRACK-17..23, -29, -30 | EX-TRK-11, -15 | Decision enum (six values) |
| FX-TRACK-24, -25, -26 | EX-TRK-12 | Rationale field |
| FX-TRACK-27, -28 | EX-TRK-13, -14 | Follow-up Issue; five fields |
| FX-TRACK-31, -32, -33 | EX-TRK-16, -17 | persists; new file per run |
| FX-TRACK-34, -35 | EX-TRK-18 | four moments |
| FX-TRACK-36..47 | EX-TRK-19..23 | Trigger A |
| FX-TRACK-48, -49, -50 | EX-TRK-24, -25, -22, -40 | gate (d) Defer; blocker narrowing record |
| FX-TRACK-51..54 | EX-TRK-26, -27 | Trigger B |
| FX-TRACK-55..65 | EX-TRK-28..32 | Trigger C |
| FX-TRACK-66, -67, -68 | EX-TRK-33 | Trigger D owner; labels byte-identical |
| FX-TRACK-69, -70, -71, -72 | EX-TRK-34, -35, -36, -37 | SR-6.7 branches |
| FX-TRACK-73, -74, -75, -76 | EX-TRK-38, -39, -37 | SR-4.6 branches |
| FX-TRACK-77 | EX-PMD-3, EX-POST-10 | pass path, not contents |
| FX-TRACK-78, -79, -80, -81 | EX-TRK-4, EX-SHELL-3 | scratch convention |

### #25 Post-completion review
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-POSTC-2, -3 | EX-POST-1 | 2 | fresh generalist sweep |
| FX-POSTC-4, -5, -6, -49 | EX-POST-2, -3 | 1 | do not invoke lane skills |
| FX-POSTC-7, -8, -9 | EX-POST-4, -5 | 1 | team-lead must not review |
| FX-POSTC-11, -12, -13 | EX-POST-9, -11 | 2 | `general-purpose`, self-contained, substitutions |
| FX-POSTC-14 | EX-POST-12 | 2 | opener ("fix" / "Bee") |
| FX-POSTC-17 | EX-POST-17 | 1 | fresh eyes |
| FX-POSTC-18 | EX-POST-18 | 1 | phases in order |
| FX-POSTC-19, -20, -21 | EX-POST-19 | 1 | PHASE 1 |
| FX-POSTC-22, -23 | EX-POST-20 | 1 | missing tracker → proceed + flag |
| FX-POSTC-24, -25 | EX-POST-21 | 1 | PHASE 2 |
| FX-POSTC-26..30 | EX-POST-22, -23 | 1 | contract violations → `[compromise-challenge]` blocker |
| FX-POSTC-31..37 | EX-POST-24, -25, -26 | 1 | PHASE 3 two axes; mechanism definition |
| FX-POSTC-38..41 | EX-POST-27, -28 | 1 | PHASE 4 |
| FX-POSTC-42 | EX-POST-29 | 1 | PHASE 5 |
| FX-POSTC-43, -44, -45 | EX-POST-30, -31 | 2 | PHASE 6 (spec noun) |
| FX-POSTC-46, -47, -48 | EX-POST-32, -33 | 1 | skill repos; no repo audit |
| FX-POSTC-50..56 | EX-POST-34, -35, -36 | 1 | tags; shape; `no issues found` |
| FX-POSTC-57..60 | EX-POST-37, -38 | 1 | wait; synthesize |
| FX-POSTC-61..64 | EX-POST-39, -40 | 1 | challenge preamble |
| FX-POSTC-65, -66, -67 | EX-POST-41, -42, -43 | 1 | self-tracking close-out |
| FX-POSTC-68 | EX-POST-44 | 1 | `Post-completion review: no issues found` |
| FX-POSTC-69, -70, -71, -72 | EX-POST-45, -46 | 1 | gate text; three options; recommend Fix on PHASE 2 |
| FX-POSTC-73, -74, -75, -99 | EX-POST-47, -49 | 1 | Fix branch dispatch/close-out |
| FX-POSTC-82, -83, -84, -85 | EX-POST-50, -51, -52 | 1 | postcomp movement rung |
| FX-POSTC-86, -87, -88, -89, -90, -91, -94 | EX-POST-53, -54, -55 | 1 | abort-this-lane reading; own sweep |
| FX-POSTC-92 | EX-POST-60 | 1 | commit after lanes deliver |
| FX-POSTC-95, -96 | EX-POST-59 | 1 | within-finding ordering |
| FX-POSTC-97, -98, -100 | EX-POST-61 | 1 | File / Skip |

### #26 Recovery gates (all Tier 1)
| FX | EX | Note |
|---|---|---|
| FX-SRGATE-1, -2 | EX-POST-62 | per PHASE 3/4 finding |
| FX-SRGATE-3, -4, -6, -7 | EX-POST-63, -64 | PHASE 2 has no recovery gate |
| FX-SRGATE-5 | EX-POST-46 | aggregate step-5 gate |
| FX-SRGATE-8, -9 | EX-POST-65 | per finding, emission order |
| FX-SRGATE-10..15 | EX-POST-67, -68 | SR-6.7 labels |
| FX-SRGATE-16, -17 | EX-POST-69, -70, -71 | SR-6.7 branches |
| FX-SRGATE-18..21 | EX-POST-72..75 | SR-4.6 |

### #27 Shell & scratch
| FX | EX | Tier | Note |
|---|---|---|---|
| FX-SHELL-1, -2 | EX-MAN-7, EX-TRK-4 | 1 | mkdir / New-Item; Write tool |
| FX-SHELL-3, -4 | EX-SHELL-3, -4 | 1 | never delete; rationale |

### Documented divergences (do NOT pin)
| Topic | FX | EX |
|---|---|---|
| Required subagent set (eight incl. `analyst` vs seven) | FX-PRE-2 | EX-PRE-3 |
| Hive precondition (Issues vs Plans) | FX-PRE-7 | EX-PRE-10 |
| Isolation option-1 label and prompt trigger | FX-ISO-6, -8, -9, -10, -14 | EX-ISO-3, -4 |
| Manifest discriminator, collision cases, Progress shapes | FX-MAN-7..10, -13, -14, -17..22, -30, -31, -38, -39 | EX-MAN-8, -11..14, -17, -22, -23, -30, -32..48 |
| Movement branch strictness; Engineer mover | FX-MOVE-6, -17 | EX-MOV-6, -16..21, -23 |
| Abort option and routing | FX-UNEXP-12 | EX-UMG-12, -13 |
| Engineer-dispatch prefix lists and Code Reviewer coverage | FX-ENGPRE-1, -4..7 | EX-EDP-2, -5..12, -20 |
| Approved-design source for mechanism detection | FX-ROUTE-47 | EX-ROUTE-37 |
| Blocker base pair at gate (c) | FX-ROUTE-62 | EX-ROUTE-47 |
| `Cancel` at gate (c) | FX-ROUTE-88 | EX-ROUTE-49, -50, -65 |
| Gate (d) non-deferrable blocker set; zero-path handling | FX-ROUTE-101, -102 | EX-ROUTE-74, -75, -76 |
| Gate (d) `Cancel` semantics | FX-ROUTE-110 | EX-ROUTE-81 |
| Filing-failure re-prompt Cancel availability | FX-ROUTE-119 | EX-ROUTE-87 |
| Part (g) code-review rung | FX-ROUTE-122 | EX-ROUTE-91 |
| Phase C / Bee-level reviewer set and PM optionality | FX-REVIEW-1, -4 | EX-BEEREV-1, -7, -9..15 |
| Commit subject contract | FX-CLOSE-19, -20 | EX-CLEAN-13..16 |
| Hive staging target and helper resolution | FX-CLOSE-12, -17 | EX-CLEAN-9 |
| Close-out mode branch vs always-end-run | FX-ABORT-5, -20..29 | EX-ABORT-15, -20 |
| Checkpoint commit verification form | FX-CKPT-12..18 | EX-CKPT-18..24 |
| Guard resume command | FX-GUARD-18 | EX-CWG-17 |
| HYG firings and surface-1 carve-out | FX-HYG-8..10, -18..28 | — |
| `hive_commit.py` path and `--skill` value | FX-HYG-71, -72, -73 | EX-DHG-29, -30 |
| Post-completion diff scope and fallback | FX-POSTC-15, FX-MAN-21 | EX-POST-6, -7, -13, -14 |
| Post-completion design-question route | FX-POSTC-76..81 | — |
| Destination label spelling | FX-DEFC-10 (`-Issue`) | EX-DEFER-7 (`-Task`) |
| Summary headings and lane slots | FX-SUM-2, -3, -6 | EX-CLEAN-24, -25, -31; EX-SUMM-1, -2, -5 |
| Second-order destination per scope | FX-SUM-8 | EX-SOE-3, -6, -7, -8 |

