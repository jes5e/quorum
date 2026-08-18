---
id: b.bq4
type: bee
title: Installed skills reference docs that never ship; pick a reference architecture
parent: null
reference_materials: null
created_at: '2026-08-18T14:45:07.705619'
status: open
schema_version: '0.1'
guid: bq46xmk856ebaa136gaur5hrmrtpwjbe
---

## Description

Skill prose shipped to downstream machines references guidance that exists only in this repo, so the references dangle on a fresh install; and the run-state-manifest contract is triplicated across the three execution skills as a workaround for having no shared downstream carrier. Four interlocked defects, bundled because the first three hinge on one design decision — how installed skills may reference shared guidance at all — and the fourth is the same portability-rule class caught by the same sweep.

## Current behavior

1. **74 literal `docs/doc-writing-guide.md` references across 13 of the 14 skills** (verified 2026-08-17 by grep: quo-breakdown-epic 17, quo-plan 16, quo-execute 15, quo-fix-issue 11, quo-spec-review 4, quo-engineer-review 2, quo-test-writer-review 2, quo-doc-writer-review 2, quo-file-issue 1, quo-write-prd 1, quo-write-sdd 1, quo-plan-from-specs 1, quo-setup 1; only quo-status has none). These cite load-bearing contract sections (querying-tickets recipes, the two-step TaskCreate → prescribed-tool contract, the Scoped-marker contract, ticket-naming conventions). The README install procedure copies only `skills/*` and `agents/*`, so the guide never ships: verified on an installed machine that `~/.claude/skills/` contains the referencing prose and no docs directory. Downstream the references dangle — or silently resolve to the *target project's own* `docs/doc-writing-guide.md` if one exists, which is worse. The references only resolve today when the working directory happens to be the quorum repo itself.
2. Skill prose cross-references `CLAUDE.md ## Scratch-file convention` (~10 sites across quo-execute, quo-breakdown-epic, quo-fix-issue, quo-plan; a section that exists only in THIS repo's CLAUDE.md — it is not among the contract sections /quo-setup writes to a target repo). Downstream the reference resolves to nothing. Most sites pre-existed the b.ja9 fix; that fix's manifest prose added ~3 more.
3. The ~40-line run-state-manifest definition (path convention, key derivation, truncate/rewrite semantics, contents invariant) is triplicated nearly verbatim across the three execution skills' `#### Write the run-state manifest` sections — a proven drift surface (multiple b.ja9 review rounds caught cross-copy drift between the copies).
4. This-repo ticket IDs survive as citations in installable prose: `b.wii` (quo-execute, quo-fix-issue ×2, and the three quo-*-review routing-trailer sections), `b.fpm` (the three quo-*-review files plus quo-spec-review), `b.9q3` (quo-plan). Each is a bare ID citing *why* a contract exists — meaningless in a downstream project. (The `b.x9w` / "Epic 8s" / "this Bee" instances of the same class were already fixed inline during the b.ja9 close-out; placeholder-style IDs in examples like `b.abc` are fine and out of scope.)

**Nuance that partly explains how defect 1 went unnoticed:** CLAUDE.md `## Documentation Locations` has a `Doc writing guide` contract key, so "the doc writing guide" sounds resolvable downstream — but in a target repo that key points at the TARGET's own doc-writing guide (often empty), not at quorum's internal contracts doc. This repo's `docs/doc-writing-guide.md` plays double duty: the value of this repo's `Doc writing guide` key, AND the skill set's cross-skill contract carrier. Any fix must not conflate the two roles.

## Expected behavior

One deliberate reference architecture, applied consistently: installed skills either carry everything they need, or reference a carrier that verifiably exists downstream. The manifest contract is defined once in whatever shared carrier the decision produces. No this-repo ticket IDs, paths, or work-item references remain in installable prose (design rule 3 holds uniformly).

## Impact

On a fresh downstream install, Claude following a skill hits dangling references and must guess at conventions (query recipes, gate contract, scratch-file rules) the prose promises are written down — or worse, reads an unrelated same-named file in the target repo. The triplicated manifest contract will drift as soon as one copy is edited without the others. The ticket-ID citations are noise downstream and leak this repo's internals.

## Suggested fix

Design-analyze before editing (the candidate directions for defects 1-3 are mutually exclusive and change different files): (a) ship the guide in the install procedure — e.g. as a skill-adjacent shared document under `~/.claude/skills/` — and keep references as-is; (b) have /quo-setup write the load-bearing conventions (scratch-file convention, potentially the manifest contract) into the target repo's CLAUDE.md as new contract sections; (c) inline everything each skill needs and drop cross-repo references, accepting the duplication defect 3 wants to remove. Defect 4 is direction-independent (reword each bare-ID citation to carry the information without the ID, per the pattern already applied to `b.x9w`). Key files depend on the direction: README + install docs (a), quo-setup + the contract-keys section (b), or all fourteen SKILL.md files (c).

## Background and rationale

Surfaced during the b.ja9 fix review (2026-08-17): the Analyst found defect 1's execution-skill instances; the PM found defects 2 and 3; the close-out Engineer's verification grep found defect 4; a full grep sweep during Issue filing established defect 1's true blast radius (74 references, 13 skills). Defect 3's natural fix (hoist the manifest contract into the doc-writing guide alongside the Scoped-marker and two-step-gate contracts) only works if defect 1's answer makes the guide available downstream — which is why these must be decided together, not filed as independent tickets.

## Decisions and rejected alternatives

- **Rejected: fixing these inline during the b.ja9 run.** The install-vs-setup-vs-inline choice is a real design decision deserving an Analyst pass, and ad-hoc edits would have churned prose the b.55r breakdown reads as its anchor.
- **Rejected: filing separate Issues per defect.** Per the bundling house style, defects 1-3 share one design decision and largely the same files; defect 4 shares the sweep and the portability rule. Splitting would force the design decision to be made multiple times.

## Quantified reference inventory (2026-08-18 sweep)

A full grep of the shipped trees (`skills/`, `agents/`) during the t1.55r.ec breakdown run, so the fix run starts from data rather than rediscovery.

**Repo-only doc references** (`docs/doc-writing-guide.md`, `docs/sdd.md`, `docs/prd.md`, `CONTRIBUTING.md`, `docs/test-writing-guide.md`) — 86 total, per file:

| Shipped file | Count |
|---|---|
| skills/quo-plan/SKILL.md | 18 |
| skills/quo-breakdown-epic/SKILL.md | 18 |
| skills/quo-execute/SKILL.md | 15 |
| skills/quo-fix-issue/SKILL.md | 11 |
| skills/quo-setup/SKILL.md | 6 |
| skills/quo-doc-writer-review/SKILL.md | 4 |
| skills/quo-spec-review/SKILL.md | 4 |
| skills/quo-engineer-review/SKILL.md | 2 |
| skills/quo-test-writer-review/SKILL.md | 2 |
| skills/quo-file-issue/SKILL.md | 1 |
| skills/quo-write-prd/SKILL.md | 1 |
| skills/quo-write-sdd/SKILL.md | 1 |
| skills/quo-status/SKILL.md | 1 |
| skills/quo-plan-from-specs/SKILL.md | 1 |
| agents/pm.md | 3 |
| agents/doc-writer.md | 1 |

All three bundled helper scripts (`detect_fast_path.py`, `scoped_marker_resolver.py`, `hive_commit.py`) are clean, as are the other six agents files. The dominant reference targets are `docs/doc-writing-guide.md` sections that are genuinely load-bearing at run time — `## Querying tickets` (freeform-query recipes), `## The two-step TaskCreate → prescribed-tool contract`, `## The Scoped-marker contract`, `## Naming tickets in user-facing output and commits` — so the reference architecture must give these a home installed users actually receive (ship the guide alongside the skills, inline the load-bearing sections into the consuming SKILL.md files, or split the guide into a shipped runtime-contract half and a repo-only contributor half).

**Ticket-ID-shaped references** (`b.xxx` / `t1.xxx...` patterns) — ~48 matches concentrated in quo-fix-issue (14), quo-breakdown-epic (10), quo-execute (7), quo-status (6), quo-plan (5), plus 1-per-file elsewhere including agents/pm.md and agents/analyst.md. These need case-by-case classification during the fix: some are harmless illustrative placeholders (`e.g. b.duy`), others are real this-repo ticket references that mean nothing in an installed context (e.g. the `b.6k2` / `b.aic` worker-prompt references CLAUDE.md's bash-etiquette section itself points at).

**Forward-guard already in place:** Plan Bee b.55r's body carries a `## Review criterion — no shipped-artifact references to unshipped docs` section binding every review cycle of the context-window-guard feature, so the count above should not grow while this Issue waits.

## Deferred from /quo-execute run (2026-08-18 21:18)

From the b.55r Epic 1 review cycles: the reference architecture should carry an explicit **README carve-out** for the shipped-artifact doc-reference criterion. README.md is read on GitHub or in a checkout — installed users do not receive it via `cp -r skills/*`, and its readers DO have the repo's `docs/` directory alongside it — so a README→`docs/doc-writing-guide.md` cross-link is legitimate where the same reference inside `skills/*/SKILL.md`, `agents/*.md`, or a bundled helper script would dangle. Concrete instance judged acceptable during that review: the README `### The context-usage gauge file` section's pointer to `docs/doc-writing-guide.md` `## The context-gauge file contract`. Without the carve-out, the systemic fix (or the b.55r review criterion applied verbatim) would over-trigger on such links.

