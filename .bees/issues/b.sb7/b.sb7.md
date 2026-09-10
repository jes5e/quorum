---
id: b.sb7
type: bee
title: Internal docs as map + register with single fact ownership; retire the per-feature PRD/SDD fold-in; archive the PRD
parent: null
reference_materials: null
created_at: '2026-09-10T20:39:45.896745'
status: open
schema_version: '0.1'
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
| Mechanism: what the code does, constant values, enum arms, field and metric names, step-by-step algorithms | the code and its doc comments | the SDD |
| Current-state invariants, contracts, decisions with rejected alternatives, verified external facts with their source | the SDD register, in the subsystem's section, stated as the rule with a pointer to the code and to the test that pins it | changelogs, per-feature narrative |
| Component boundaries, interactions, data flow, where schemas and API surfaces live | the SDD map | duplicated elsewhere |
| History: what changed, when, why, ticket ids, superseded claims | the commit message and the bees ticket (already written, never re-reviewed); a project changelog only if the target CLAUDE.md names one | SDD, README, CLAUDE.md |
| Operator and user-facing behavior, install, commands, configuration surface and defaults | README or the configured customer docs | duplicated tables elsewhere |
| Product scope, non-goals, acceptance criteria, contract statements | Spec Bee `t1=Doc` children and Issue bodies; the on-disk PRD is an archived starting-point document, not maintained and never a write target | per-Issue entries |

The table lives in exactly one shipped place, `agents/doc-writer.md` `## Fact ownership`; the review skill, the setup skill's generated guide, README, and CONTRIBUTING carry the principle in one sentence and a pointer, never a second copy of the rows.

The maintained SDD is two parts, the map and the register, under a size cap (default 500 lines; the target repo's doc-writing guide may override) so that the Analyst reads it whole on every dispatch. The admission test for a line: would an agent that skipped it make a worse design decision or reintroduce a fixed bug?

Register entries are transcribed from ratified sources the orchestrator relays under a `## Ratified decisions` dispatch heading, not inferred from the diff:

- **Fix mode:** the approved Analyst directive's `### Policy decisions this change implies` plus the invariant lines of its `### Blast radius`. The Analyst promotes a load-bearing rule or verified external fact it finds in the code or in an archived doc **only** through `### Policy decisions this change implies` (framed as "should this rule enter the register?" with a recommended answer), never through `### Blast radius`, whose contract stays "invariants the change adds, removes, or weakens" so the Code Reviewer's sweep verification is not fed spurious sites.
- **Execute mode:** the `## Decisions and rejected alternatives` section of the spec source's SDD (Spec Bee `SDD` child, or a `file-path` SDD when it has one). The row is relayed **only** to Doc Writers dispatched for a pre-planned internal-architecture doc Subtask or at Bee scope, never to a customer-docs Subtask. A hand-written on-disk SDD without a decisions section, and a body-as-spec Plan Bee, relay the fixed none-line; on those paths the register grows only through the Doc Writer's bounded unratified entries and later fix runs, which is accepted.
- **Both modes:** the Doc Writer records an entry when the diff in scope implements the decision; a ratified decision the diff has not implemented yet is listed in the return as not-yet-landed (an observation, not a defect, since at Subtask 1 of 6 most decisions are pending by design); a decision the diff **contradicts** is reported to the orchestrator. The Doc Writer MAY add an entry the diff plainly establishes on its own (a new test that pins a rule, a comment recording a verified external fact) when it passes the admission test, marked `unratified` in its return. This is a deliberate, bounded exception to transcription-only, kept because it is reviewer-checked.
- The Issue body's `## Doc divergence noted` items are ratified by the Validate-Issue gate and are routed to their owners inside the existing customer-docs and register duties; the `**Doc Sync**` summary line and `/quo-file-issue`'s remediation sentence stay true.

The Doc Reviewer receives the same `## Ratified decisions` relay (both orchestrators name it as a recipient of that row) and checks four finite things: README claims are true against the diff; each relayed decision the diff implements has a normative register entry with a code pointer and no ticket id, and any register entry the diff touched that is not on the relayed list is treated as unratified and checked against the code and its test; the SDD is under the cap; no fact appears in two owners. A false claim is a `blocker`; a fact in the wrong owner or in two owners is a `suggestion` with a move-and-pointer fix path; wording inside the right owner is a `nit` unless false.

## Impact

Wall-clock and token cost on every `/quo-fix-issue` and `/quo-execute` run in every downstream repo: five to eight doc-review rounds per Issue were reported, most spent on descriptive prose and multi-carrier drift. Correctness risk: descriptive SDD claims drift and are then trusted by cold agents (§17.2 "OMPF parse failures log at ERROR" was never true; the "Delete refused pre-MULTI" claim was unreachable). A frozen-but-consulted doc would make that permanent, which is why the PRD is archived and taken out of the agents' authoritative read set rather than frozen in place.

## Suggested fix

Hand edits plus cold reviews per CLAUDE.md `## Working on the orchestrator skills`; not a `/quo-fix-issue` run. Ship the skill change first; downstream doc migrations follow separately (item 9).

1. `agents/doc-writer.md`: replace `## Cumulative project doc updates` with `## Fact ownership` (the table above, the single carrier) and three duties: customer-facing docs diff review, register transcription from `## Ratified decisions` with the not-yet-landed / contradicted / unratified rules, map update when a boundary moves. `## Doc divergence noted` items named inside the sources of duties 1 and 2. State the size cap and the admission test. Drop the PRD as a write target. Mechanism's never-in cell names the SDD only (documented defaults are README behavior); History's never-in cell omits the PRD (an archived PRD is made of history and no role may edit it).
2. `skills/quo-doc-writer-review/SKILL.md`: replace the house-style block with a one-paragraph statement of the map-plus-register contract and a pointer to the ownership table; replace step 3's architecture bullets with the four checks; make step 5 an ownership check; add the severity mapping; keep README checks, trailer, severity/depth tags, and loop-bounding prose unchanged.
3. `skills/quo-setup/SKILL.md`: drop `## Per-feature scope` / `## Per-feature design` from both skeletons; add `## Register` to the SDD skeleton and label the PRD skeleton a starting point; rewrite the "how the docs grow" note naming both relay sources; the generated doc-writing guide states the principle, points at the table, and carries the cap. Fix the stale "PM detects spec drift from the PRD" note.
4. `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md`: §1 makes `Project requirements doc (PRD)` allowed-empty; §5 drops "Surface the Plan Bee title to the Doc Writer" and adds one `## Ratified decisions` dispatch-table row with recipients Doc Writer **and Doc Reviewer**, fix-mode source = policy decisions plus Blast-radius invariant lines, execute-mode source = the spec source's decisions section relayed only to doc-Subtask and Bee-scoped Doc Writers. Narrow "Writers never receive the directive" to its `### Recommended approach`. Encode-deferral destinations and `--doc-path` prose name the SDD only.
5. `agents/analyst.md`: SDD read as map and register; an archived or starting-point PRD is problem-report context; promotion of rules only through `### Policy decisions this change implies`. `agents/pm.md`: an archived PRD is background even when cited. `agents/doc-reviewer.md`: name `## Ratified decisions` among what the orchestrator passes and forward it verbatim into the review skill, as `agents/code-reviewer.md` already does for completeness evidence.
6. `skills/quo-plan/SKILL.md` `## Anticipated doc impact` names the map, register, and README. `skills/quo-plan-from-specs/SKILL.md` hard-fail message no longer claims `/quo-plan` adds feature sections to cumulative docs. `skills/quo-breakdown-epic/SKILL.md` Encode prose and `hive_commit.py` docstring name the SDD only. `skills/quo-spec-review/SKILL.md` and `skills/quo-write-sdd/SKILL.md` `## Documentation` guidance names SDD and README, never the PRD.
7. `README.md`: replace the three cumulative-docs sentences with the principle and a pointer; name both relay sources; trim the `/quo-plan-from-specs --feature` row so it no longer advertises the cumulative shape. `CONTRIBUTING.md`: principle 5 becomes one sentence plus pointer; the intentional-asymmetries bullet describes the three duties, not diff hunting. This repo's `CLAUDE.md`: PRD joins `Compile/type-check` as allowed-empty; precondition paragraph updated; `docs/doc-writing-guide.md` records the cap and this repo's own pending migration.
8. `tests/`: `test_doc_ownership.py` pins the retired vocabulary in every artifact the sweep touched (not only three), the `## Ratified decisions` row in both bodies with the Doc Reviewer recipient, and the Analyst's Blast-radius scope sentence unchanged. Produce and attach the sweep completeness list (patterns run, every hit, edit or reason untouched).
9. `docs/migration-map-and-register.md` (repo-only): archive-and-rebuild procedure and a copy-paste prompt for the five repos in order — event_consumer_service (validation run), event_aggregation_service, notification_common, live_edit, then quorum itself. The prompt names the installed agents directory generically, not a hardcoded path. Sequence the validation run after the b.zi3 and b.pgj runs of the current rebuild so one repo is not validating two rewrites at once.
10. Follow-ups to file when this lands: (a) retire the `### Feature:` scoping machinery (`/quo-plan-from-specs --feature`, `scoped_marker_resolver.py`, PM Path A/B), which under this model has no legitimate document to scope into; (b) migrate this repo's own `docs/sdd.md` and `docs/prd.md` last; (c) annotate b.ag8 and b.c4v that the Doc Writer / Doc Reviewer relay is named `## Ratified decisions` and any Code Reviewer / PM relay of the same section reuses that name.

## Background and rationale

Three truths, and code owns only one. Code is the truth for what the system does; tests are the truth for what it must keep doing; specs are the truth for what it should do for users. A doc sentence describing what the code does is a second copy and drifts. A doc sentence stating what the code must do is normative: when it disagrees with the code, the code is wrong. That is the line between the register and everything that leaves.

The churn decomposes into four kinds: drift corrections on descriptive claims (eliminated when mechanism leaves the docs), multi-carrier edits (eliminated by single ownership), wording rounds (shrunk by a convergent reviewer criterion), and genuine README defects (kept; they are product defects). Round caps, delta-only rounds, and skipped lanes were rejected as speed levers on 2026-09-04 and are not proposed here; this change shrinks what there is to review, not how hard it is reviewed.

The live_edit CLAUDE.md invariant section (one-line rules with SDD section pointers) is already register-shaped and was grown by hand because agents needed it; the SDD behind it is the encyclopedia nobody can read whole. Both downstream repos already carry an IMPLEMENTATION_CHANGELOG (155k and 18k words); moving history there would relocate the churn, since the Doc Reviewer reviews it too, so history's owner is the commit and the ticket.

## Decisions and rejected alternatives

- **Retire the per-feature fold-in entirely** rather than narrow the Doc Writer's question. Rejected because live_edit proves the fold-in is not the only growth surface; the topical sections grew the same way. The ownership table addresses both shapes.
- **Archive the PRD, do not freeze it in place.** A frozen doc still on the agents' read list is read as authority. Archive plus a starting-point header and a background-only reading rule in the Analyst and PM contracts is the honest form.
- **Transcribe register entries from ratified sources; allow one bounded, reviewer-checked exception.** Transcription removes the judgment call that inflated the old SDDs. The `unratified` entry for a rule the diff plainly establishes (a pinning test, a sourced external fact) is kept deliberately, because on the body-as-spec and hand-written-SDD paths it is the only way the register grows during execute; it is bounded by the admission test and checked by the Doc Reviewer, which is why the reviewer must receive the relay.
- **Execute-mode relay to doc Subtasks and Bee scope only; not-yet-landed is an observation.** Relaying to every Subtask would report every pending decision as unimplemented at Subtask 1 of 6. Moving transcription to the per-Task PM boundary was rejected because the PM does not write docs and adding a Doc Writer dispatch there is new machinery; the doc Subtask, which `/quo-breakdown-epic` already orders after the code Subtasks, is the existing site.
- **Promote rules through `### Policy decisions this change implies`, not `### Blast radius`.** Blast radius is scoped to invariants the change adds, removes, or weakens and feeds the Code Reviewer's sweep verification; a relied-upon-but-unchanged invariant listed there would produce a finding against the Engineer at every unchanged site. A yes/no "enter the register?" question fits the policy-decisions contract exactly and needs no new marker.
- **One heading, `## Ratified decisions`, for every relay of post-gate decisions.** b.ag8's sketch used `## Policy decisions` for the Code Reviewer and PM; the Doc Writer relay carries two sections, so the broader name wins and b.ag8 / b.c4v are annotated (follow-up 10c) rather than a third name landing later.
- **Doc Reviewer receives the relay rather than a second `## Register entries written` heading.** The second heading is a new name class; deriving unratified entries as "touched but not on the relayed list" needs no second relay.
- **The ownership table has one shipped carrier.** The first cold review found two mirrors diverged on day one (Mechanism's never-in cell, History's PRD entry). Every other artifact states the principle in a sentence and points at `agents/doc-writer.md`.
- **Size cap as a review criterion**, project-overridable, default 500 lines. live_edit's guide said "keep it factual and current" and reached 276k words; rules without a bound erode. Precedent: the orchestrator bodies' line budget.
- **History to commit plus ticket, not to a reviewed changelog.** See rationale above.
- **Archive-and-rebuild for every downstream repo**, not prune-in-place for the small ones. One procedure; anything the extraction misses is recovered lazily when the Analyst promotes it.
- **Leave the `### Feature:` scoping machinery in place in this change and retire it in a follow-up**, rather than delete it here. It is orthogonal code with its own tests; this change is already a contract change across nine files. The README stops advertising it now.
- **Cap rounds / batch nits / skip the PRD check by Issue shape.** Rejected: the first two by the 2026-09-04 decision; the third because `agents/pm.md` rejects shape-based short-circuits for good reason.

## Review dispositions (2026-09-10, two cold reviews of the first worktree diff)

Doc review: (1) CONTRIBUTING asymmetries bullet described diff-hunting — fix per item 7. (2) README attributed execute-mode register content to a gate — fix per item 7, both sources named. (3) Ownership list in three carriers — fix: single carrier, item 1 and the Expected-behavior paragraph. (4) This repo's own docs exceed the cap — follow-up 10b, and the guide records it. (5) "creates and maintains" lead-in — fix. (6) README line 43 repeats line 183 — fix.

Engineer review: (1) Doc Reviewer cannot verify transcription — fix path (a): Doc Reviewer added as relay recipient, unratified defined as touched-but-not-relayed. (2) Analyst promotion through Blast radius contradicts its contract — fix path (a): policy-decisions section only. (3) `## Doc divergence noted` severed — fix path (a): items named inside duties 1 and 2. (4) History never-in PRD — fix. (5) Mechanism never-in README vs defaults — fix path (a). (6) `/quo-plan-from-specs` hard-fail message — fix per item 6. (7) Sweep completeness list owed — item 8. (8) Breakdown Encode prose and helper docstring — fix per item 6.

Second-agent ticket review: execute-mode noise — decided above. Orphaned scoping machinery — follow-up 10a plus README trim. Mechanical invariant-line marker — moot once promotion goes through policy decisions only; Blast-radius invariant lines already open each entry per the Analyst contract and are relayed as-is. Heading name — decided above. Ticket/diff inference disagreement — recorded. Plan-from-specs register growth — acknowledged in Expected behavior. "Quorum first" wording — corrected. Hardcoded install path in the migration prompt — item 9.

## Doc divergence noted

- `README.md` lines 43, 125, 185 describe the retired mechanism; rewrite per item 7.
- `skills/quo-setup/SKILL.md` line 489 states the PRD is "used by the Product Manager agent to detect spec drift"; stale since the Specs-hive redesign.
- `skills/quo-plan-from-specs/SKILL.md` hard-fail message claims `/quo-plan` adds feature sections to cumulative docs; it has not since the Specs-hive redesign.
- `docs/sdd.md` and `docs/prd.md` in this repo are per-feature ledgers over the cap; migrate last (follow-up 10b).

