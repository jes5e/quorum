---
id: b.sb7
type: bee
title: Internal docs as map + register with single fact ownership; retire the per-feature PRD/SDD fold-in; archive the PRD
status: open
created_at: '2026-09-10T20:39:45.896745'
schema_version: '0.1'
reference_materials: null
guid: sb7ntrreicsvjt89uqrzqrvp4ydmbdgd
---

## Description

The Doc Writer is instructed to describe "what was actually built" from the Engineer's diff and to append or rewrite a `### Feature: <title>` subsection in the project PRD and SDD on every run, in both execute and fix mode. The Doc Reviewer is instructed to grade the result as a current-state cheat sheet with no design decisions and no history, and to hunt for completeness gaps and duplication. The two contracts contradict each other, and neither assigns any kind of fact a single owning document. The result across every repo using quorum is an SDD that restates mechanism already in the code, carries ticket-keyed history, and duplicates facts across three to six carriers, so every fix pays a doc tax and every doc-review round finds something.

Measured on the four downstream repos plus this one (2026-09-10):

| Repo | SDD | Per-feature share | Ticket-id lines | Commits since June touching SDD/PRD |
|---|---|---|---|---|
| live_edit | 7,313 lines / 276k words | 143 lines | 607 | 133 of 349 |
| event_consumer_service | 744 lines / 32k words | 654 lines | 17 | 64 of 403 |
| event_aggregation_service | 783 lines / 6.6k words | (not measured) | | |
| notification_common | 715 lines / 6.5k words | (not measured) | | |
| quorum | 847 lines / 51k words | 742 lines | 86 | 41 of 132 |

live_edit's SDD was 547 KB when first committed on 2026-07-23 and is 1,958 KB today: 72 percent of it is post-plan accretion written by the Doc Writer, not the original seed. Its per-feature bullets contain "superseded later in this same unreleased set by Issue b.7td, retained here as the record of what b.d6b shipped", against the repo's own doc-writing guide, which routes ticket attribution to the changelog and says to remove outdated text rather than annotate it. Its b.is1 entry records that resizing one re-auth interval was declined partly because it meant "eight doc sites". event_consumer_service and quorum show the other shape: the same defect as a per-feature ledger that is 88 percent of the document.

Five independent agent sessions across these repos agreed on what earned its keep: recorded invariants, decisions with rejected alternatives, and verified facts about the outside world with their source (the Contour readiness-selection fact, the WatchGuard slot-pinning rule, the b.f1v log-level lesson). All agreed the PRD contributed nothing after planning and that the cost was concentrated in doc-review rounds spent on descriptive prose.

## Current behavior

- `agents/doc-writer.md` `## Cumulative project doc updates` mandates a `### Feature: <title>` subsection per run in both PRD and SDD, keyed on the Plan Bee title or an Issue-title fallback, replaced idempotently at every Epic. Its categorization table routes every row except pure refactor to the SDD and has no bug-fix row, so every Issue becomes a "Feature".
- `skills/quo-doc-writer-review/SKILL.md` house style forbids design decisions, trade-offs, and history in architecture docs, while its steps 3 and 5 ask for completeness and duplication findings over the whole document. Completeness over a 276k-word document never converges.
- `skills/quo-setup/SKILL.md` seeds `## Per-feature scope` / `## Per-feature design` headers, tells the user "/quo-plan adds a Feature subsection to both docs", and tells the user the PRD is "used by the Product Manager agent to detect spec drift". In the `/quo-plan` flow the PM reads Spec Bee children, and in fix mode it reads the on-disk PRD only when the Issue cites it, so that claim is stale.
- `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md` §5 surface the Plan Bee title to the Doc Writer for the fold-in, and their §1 hard-fails when the `Project requirements doc (PRD)` key is missing. Writers never receive the Analyst's ratified policy decisions, so the Doc Writer infers what matters from the diff.
- `README.md` promises "Cumulative project docs" as a feature (lines 43, 125, 185).

## Expected behavior

Every kind of fact has exactly one owning carrier, and the Doc Writer routes facts to owners instead of updating every doc the diff touches:

| Kind of fact | Owner | Never in |
|---|---|---|
| Mechanism: what the code does, constant values, enum arms, field and metric names, step-by-step algorithms | the code and its doc comments | SDD, README |
| Current-state invariants, contracts, decisions with rejected alternatives, verified external facts with their source | the SDD register, in the subsystem's section, stated as the rule with a pointer to the code and to the test that pins it | changelog, per-feature narrative |
| Component boundaries, interactions, data flow, where schemas and API surfaces live | the SDD map | duplicated elsewhere |
| History: what changed, when, why, ticket ids, superseded claims | the commit message and the bees ticket (already written, never re-reviewed); a project changelog only if the target CLAUDE.md names one | SDD, PRD, README, CLAUDE.md |
| Operator and user-facing behavior, config surface | README or the configured customer docs | duplicated tables elsewhere |
| Product scope, non-goals, acceptance criteria, contract statements | Spec Bee `t1=Doc` children and Issue bodies; the on-disk PRD is an archived starting point, not maintained | per-Issue entries |

The maintained SDD is two parts, the map and the register, under a size cap (default 500 lines; the target repo's doc-writing guide may override) so that the Analyst reads it whole on every dispatch. The admission test for a line: would an agent that skipped it make a worse design decision or reintroduce a fixed bug?

Register entries are transcribed from ratified sources, not inferred from the diff: in fix mode the approved Analyst directive's `### Policy decisions this change implies` and the invariant delta in `### Blast radius`; in execute mode the Spec Bee SDD child's `## Decisions and rejected alternatives`. The Doc Writer adds, replaces, or deletes the corresponding register entry, deleting superseded statements rather than annotating them.

The Doc Reviewer checks four finite things: README claims are true against the diff; each register entry is normative (a rule, not a description), has a code pointer, and carries no ticket id; the SDD is under the cap; no fact appears in two owners. A fact in the wrong owner or in two owners is a `suggestion` with a move-and-pointer fix path. Wording inside the right owner is a `nit` unless the statement is false.

## Impact

Wall-clock and token cost on every `/quo-fix-issue` and `/quo-execute` run in every downstream repo: five to eight doc-review rounds per Issue were reported, most spent on descriptive prose and multi-carrier drift. Correctness risk: descriptive SDD claims drift and are then trusted by cold agents (§17.2 "OMPF parse failures log at ERROR" was never true; the "Delete refused pre-MULTI" claim was unreachable). A frozen-but-consulted doc would make that permanent, which is why the PRD is archived and taken out of the agents' authoritative read set rather than frozen in place.

## Suggested fix

Hand edits plus cold reviews per CLAUDE.md `## Working on the orchestrator skills`; not a `/quo-fix-issue` run.

1. `agents/doc-writer.md`: replace `## Cumulative project doc updates` (categorization table, title resolution, idempotency rule, path resolution) with a `## Fact ownership` section carrying the table above and three duties: README diff-review (unchanged), register transcription from the ratified sources named in the dispatch prompt, map update when a boundary moves. State the size cap and the admission test. Drop the PRD as a write target.
2. `skills/quo-doc-writer-review/SKILL.md`: replace the architecture-docs house-style block with the ownership rules and the four checks; make step 5 an ownership check (fact in two owners) rather than a general duplication hunt; add the cap check; keep README checks, the trailer, severity/depth tags, and the loop-bounding prose unchanged.
3. `skills/quo-setup/SKILL.md`: drop `## Per-feature scope` / `## Per-feature design` from both skeletons; add a `## Register` section to the SDD skeleton; rewrite the "how the docs grow" note and the PRD/SDD usage notes to match the ownership table; the bootstrap PRD becomes an explicitly labelled starting-point document; the generated doc-writing guide states the ownership table and cap.
4. `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md`: §1 makes `Project requirements doc (PRD)` the second key allowed to be empty; §5 drops "Surface the Plan Bee title to the Doc Writer" and instead passes the Doc Writer a `## Ratified decisions` heading carrying the approved directive's `### Policy decisions this change implies` and the invariant lines of `### Blast radius` (fix mode) or the Spec Bee SDD child's `## Decisions and rejected alternatives` (execute mode). This is a deliberate, narrow exception to "Writers never receive the directive": those two sections only, never the `### Recommended approach`. Cite b.ag8, which asks for the same relay to Phase B writers. Deferral Encode destinations drop "the project PRD".
5. `skills/quo-breakdown-epic/SKILL.md` §1: same PRD-key allowance. `skills/quo-plan/SKILL.md` Plan Bee body note: `## Anticipated doc impact` names the map/register/README, not a Feature subsection. `agents/pm.md` and `agents/analyst.md`: PRD reads become optional-when-present; the Analyst treats an archived PRD/SDD as problem-report context, not authority, and promotes any load-bearing fact it finds there into its proposal's policy decisions so the register captures it.
6. `README.md`: replace the three cumulative-docs sentences with the ownership model and a short "what the SDD is" paragraph. This repo's `CLAUDE.md`: `Project requirements doc (PRD)` joins `Compile/type-check` as an allowed-empty key; the precondition paragraph is updated to match.
7. `tests/`: extend `test_orchestrator_structure.py` or the portability test to pin the two allowed-empty keys and the absence of `### Feature:` prose in shipped artifacts.
8. Write two copy-paste migration prompts (stored under `docs/`, not shipped) for the downstream repos: archive-and-rebuild for all four (live_edit, event_consumer_service, event_aggregation_service, notification_common). Procedure: move the current SDD and PRD to an archive path with a "historical, not maintained, verify against code" header; write the new SDD as map plus register, seeding the register from the repo's CLAUDE.md invariant bullets where present and from the old SDD's headings otherwise; point `## Documentation Locations` at the new file and empty the PRD key; run a cold `/quo-doc-writer-review`. Order: quorum first, then event_consumer_service as the validation run, then the two small repos, then live_edit.

## Background and rationale

Three truths, and code owns only one. Code is the truth for what the system does; tests are the truth for what it must keep doing; specs are the truth for what it should do for users. A doc sentence describing what the code does is a second copy and drifts. A doc sentence stating what the code must do is normative: when it disagrees with the code, the code is wrong. That is the line between the register and everything that leaves.

The churn decomposes into four kinds: drift corrections on descriptive claims (eliminated when mechanism leaves the docs), multi-carrier edits (eliminated by single ownership), wording rounds (shrunk by a convergent reviewer criterion), and genuine README defects (kept; they are product defects). Round caps, delta-only rounds, and skipped lanes were rejected as speed levers on 2026-09-04 and are not proposed here; this change shrinks what there is to review, not how hard it is reviewed.

The live_edit CLAUDE.md invariant section (one-line rules with SDD section pointers) is already register-shaped and was grown by hand because agents needed it; the SDD behind it is the encyclopedia nobody can read whole. Both downstream repos already carry an IMPLEMENTATION_CHANGELOG (155k and 18k words); moving history there would relocate the churn, since the Doc Reviewer reviews it too, so history's owner is the commit and the ticket.

## Decisions and rejected alternatives

- **Retire the per-feature fold-in entirely** rather than narrow the Doc Writer's question (Agent 1's proposal). Rejected because live_edit proves the fold-in is not the only growth surface; the topical sections grew the same way. The ownership table addresses both shapes; retiring the fold-in follows from it because a per-feature subsection is a history carrier under a design heading.
- **Archive the PRD, do not freeze it in place.** A frozen doc still on the agents' read list is read as authority (Analyst: "consistent with the SDD's invariants"; PM: PRD when cited). Freezing institutionalizes the stale-claim failure. Archive plus removal from `## Documentation Locations` is the honest form. Per-feature requirements already live in Spec Bee children and Issue bodies.
- **Transcribe register entries from the ratified directive rather than infer from the diff.** Removes the Doc Writer's judgment call, which is where inflation of mechanism into pseudo-invariants would come from. Requires the narrow writers-see-the-directive exception (policy decisions and invariant delta only).
- **Size cap as a review criterion.** live_edit's guide said "keep it factual and current" and reached 276k words; this repo's own guide reached 51k. Rules without a bound erode. Precedent: the orchestrator bodies' line budget is already a review criterion here. A project-overridable default rather than a fixed number, since docs differ across stacks.
- **History to commit plus ticket, not to a reviewed changelog.** See rationale above.
- **Archive-and-rebuild for every downstream repo, not prune-in-place for the small ones.** One procedure; the small repos just finish faster. Anything the extraction misses is recovered lazily by the Analyst promotion rule the first time it matters.
- **Cap rounds / batch nits / skip the PRD check by Issue shape** (Agents 2, 3, 4). Rejected: the first two by the 2026-09-04 decision; the third because `agents/pm.md` rejects shape-based short-circuits for good reason.

## Doc divergence noted

- `README.md` line 43 ("Cumulative project docs"), line 125 (`/quo-plan` row), line 185 (per-feature fold-in description) describe the mechanism this Issue retires; rewrite per Suggested fix item 6.
- `skills/quo-setup/SKILL.md` line 489 states the PRD is "used by the Product Manager agent in quo-execute and quo-fix-issue to detect spec drift". In the `/quo-plan` flow the PM's spec source is the Spec Bee children; in fix mode it reads the on-disk PRD only when the Issue cites it. Stale since the Specs-hive redesign.
- `docs/sdd.md` and `docs/prd.md` in this repo are themselves per-feature ledgers (742 of 847 and 493 of 524 lines) and are the last repo to migrate, after the downstream validation runs; not part of this Issue's diff.

