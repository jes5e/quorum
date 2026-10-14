---
id: b.pca
type: bee
title: 'Doc roles have no test for customer-facing text: it is checked for truth, never for its reader'
parent: null
reference_materials: null
created_at: '2026-10-14T12:12:59.897506'
status: done
schema_version: '0.1'
guid: pcaoxuocx5rui9ousowovt3g25exm9d3
---

## Description

Quorum's doc roles give internal docs precise tests for what belongs, the SDD test and the PRD/SDD line, which the Doc Writer and the review skill carry verbatim. Customer-facing text gets no equivalent:
- The Doc Writer's job 1 is "keep the docs true" and "add what a user or operator now needs to know".
- `/quo-doc-writer-review` checks customer docs for correctness, plus a README-only block: `### Readme` and the README bullets of step 3 (install, setup, CLI references; "no implementation details").

Nothing makes either role judge whether customer text is written for its reader. The README block doesn't fit a project whose customer docs are an operations guide plus a client-API guide. The `Where each fact lives` table's customer row also reads "install, commands, configuration" only, and sends the contract clients rely on to the SDD alone, so quorum doesn't recognize an API guide as customer docs.

Scope also keys on CLAUDE.md `## Documentation Locations` keys rather than on who reads the text. Customer-read text under another key (live_edit lists `CHANGELOG.md` under its own `Customer-facing changelog` key), and customer-read text in source (published API and configuration comments), fall outside the review's customer checks.

## Evidence (live_edit, 2026-10-14; container scratch, host `~/.quorum-scratch`)

Two `/quo-fix-issue` runs, both with decider "Performance Planner 4":
- **b.pa1** (full-store GC): docs closed after 2 Doc Writer passes and 2 doc reviews.
- **b.ua9** (CreateLayer failure paths): docs closed after 3 Doc Writer passes, 2 doc reviews, and a post-completion doc review.

The planner's cold audits afterwards found about ten customer-text violations of live_edit's `docs-internal/doc-writing-guide.md` § Customer docs, all past review:
- changelog sentences of 30–75 words using internal concepts ("commit claim", "the layer's mapping", "the replica holding maintenance leadership");
- "not yet verified on Amazon MemoryDB", observed-so-far scope the guide bans (§ Limits and caveats; § Published files rule (b));
- an internal name with no setting named;
- a client-API table row missing a qualifier that the proto, the client guide and the CHANGELOG all state;
- an operator claim stated for every store that holds for two;
- a client contract rule contradicting the exceptions on another client page.

Files:
- `planner-doc-audit-b.ua9-ua9w1.md`;
- `run-state-quo-fix-issue-live_edit-ua9.md` and `-pa1.md`;
- the review returns `doc-review-r1-b.ua9-ua9w1.md`, `doc-review-r2-…` and `doc-review-postcomp-1-r1-b.ua9-ua9w10.md`.

What the returns show:
- **The reviewer read the changelog and proto hunks, but only for truth.** r1 raised four true-vs-code findings on CHANGELOG lines. It never judged reader-fit, and its item 10 proposed adding "on an unverified store (Amazon MemoryDB) …", the banned wording.
- **Cross-copy agreement was checked only in places.** The postcomp review compared the proto with the client pages; the contradiction between two client pages was missed.
- **The guide's customer rules were present.** § Customer docs, with its own reviewer checklist, was on every run base (`d27756df`, `c62d51ae`, `8a3bb7f9`). So this is not missing input.
- **Confounder:** the docs rules changed mid-run. Docs MRs !104 and !107 merged during b.ua9, and some flagged text predates them. That explains some stale text, not a reviewer proposing banned wording.

**Three questions:** about ten occurrences across two runs; silent (all passed review); not recovered by quorum (an external audit caught them). Earned. It is also a gap between agents: the project guide states a customer standard that neither role applies to customer hunks.

The operator's framing: live_edit's customer docs grew into "how the sausage is made" when they should be a simple API guide and a deployment guide (run, configure, observe). Quorum has nothing that distinguishes customer-facing from internal engineering docs.

The live_edit planner asked for three things:
- explicit checklist items over every customer-facing hunk;
- a cross-page consistency check;
- consider a cold read of the customer-facing diff alone.

## Proposed change (one small batch; target net-neutral or smaller)

1. **A customer-text test, carried verbatim by the Doc Writer and by `/quo-doc-writer-review`** (pinned in CONTRACT_SURFACES like the SDD test). Draft: a sentence belongs in customer-facing text only if its reader (a user, an operator, or a developer calling the API) would do or expect something differently after reading it, and can act on it without the source. It is written in the reader's terms: no internal names, mechanism, history, or provenance. A project guide's stricter customer-text standard is part of the test. It replaces the README-only `### Readme` block and step 3's README bullets, which pays for it.
2. **Customer text is defined by its reader, not its key.** The test applies to every hunk of the change a customer reads: the customer-facing docs, changelog entries, and published API and configuration comments. Findings on source text route to the Engineer, as the b.ua9 run already routed proto findings.
3. **One consistency goal.** A fact the change touches that is stated in several places (proto, client page, changelog, SDD) reads the same in each. Prefer stating it once and pointing to it.
4. **Table customer row:** "what users and operators do: install, run, configure, observe; how clients call the API and handle its answers". Decide with the SDD row how the client contract splits: the SDD keeps the guarantees and the reasons; the customer docs say what a caller does.
5. **`/quo-setup`:**
   - the doc-writing-guide brief names the customer readers and carries the test;
   - the customer-docs question stops implying customer docs = a README (e.g. "an operations guide, an API guide, or a README").

**Operator decision (open): whole-doc review of customer docs.** The skill reviews customer docs whole "for correctness; users act on every line". The overseer recommends narrowing it to what the change touched, plus every other statement of the same fact. Whole review missed these issues, and live_edit's customer set is budgeted at ~25k words, so whole reads cost more and spread attention thin. The trade-off: pre-existing errors in untouched pages are no longer caught by unit reviews.

**Declined, with reasons:**
- **A separate cold customer-text pass:** another dispatch every round. Try the test first; if the next runs still miss reader problems, that is the evidence for it.
- **A project-specific line-by-line checklist in quorum** (e.g. a 22-word mean): those rules belong in the project guide. The test makes the reviewer apply that guide to every customer hunk.

## Process

A hand-edit batch (CLAUDE.md `## When editing skills`), one cold review under the exit rule, and no dedicated validation. The next live_edit doc stage is the check.

Readers to update (verify by grep):
- `agents/doc-writer.md` (jobs, table);
- `skills/quo-doc-writer-review/SKILL.md` (Overview tests, Scope, `### Readme`, step 3);
- `skills/quo-setup/SKILL.md` (customer-docs question ~458, guide brief ~488, "used for" ~499);
- `tests/` (CONTRACT_SURFACES pins, prose caps);
- README and CONTRIBUTING wherever they describe the doc roles.

## Check still open

The next live_edit doc stage. Customer hunks, including changelog entries and proto comments, are judged against the test, and no banned wording is proposed by a reviewer.
## Input from the live_edit planner (2026-10-14) and dispositions

Source: `~/.quorum-scratch/planner-reply-b.pca.md`, the planner's answer to the overseer's note (`~/.quorum-overseer/reply-live-edit-planner-b.pca.md`). The planner agrees with the diagnosis: the reviewer judged customer hunks for truth, never for their reader. Its points, judged on their merits:

1. **Make the test two-sided. Accepted, short form; the enumeration is declined.**
   - The planner's point: "belongs only if…" reads as an exclusion test, so a reviewer looks for text to remove. Two audit findings were missing text: a dropped qualifier, and a missing next step.
   - Quorum already treats missing information as a defect: the writer's job 1 "adds what a user or operator now needs to know", step 3 "Find Documentation Gaps", and the `suggestion` severity. But the new test must not read one-way. Add one short clause, e.g. "…and nothing the reader needs in order to act is missing."
   - Declined: the planner's enumeration, "for a refusal or limit: what happened, whether anything applied, next step". That is live_edit's client-API rule, already in its guide, and the test's last sentence makes the guide binding. In quorum it would be a project rule in neutral prose.
   - The dropped qualifier is also a consistency failure, which item 3 covers.
2. **Scope by reader. Accepted as a goal, with no list of surfaces in quorum.**
   - The planner would count gRPC status and error message text, and metric help text. It would exclude Helm template comments not rendered into values documentation, and runtime log lines, except those a customer doc tells operators to search or alert on, since logs legitimately carry internal identifiers for support.
   - Those are sound judgments. Quorum should state the goal ("text written for a customer to read"), not the list, which is the project's: live_edit's guide § Published files lists its surfaces. "Written for", not "visible to", is what keeps log lines out.
   - No run has shown a defect in error or metric-help text. They fall under the goal by definition; no rule is added for them.
   - Findings on source text route to the Engineer as `contract-text`, one confirming read.
3. **Whole-doc vs. touched-plus-copies.** The planner chooses touched plus every other statement of a changed fact. Two of its reasons are live_edit-specific: CI prose checks for untouched pages, and the docs agent's periodic whole-set review.
   - The general case, without those: it matches the SDD/PRD footprint scope (b.sb7), full reads did not catch these misses, and the cost grows with the doc set. For a small README, touched ≈ whole anyway.
   - Overseer recommends narrowing. **Operator decision.**
4. **Correction to the evidence above.**
   - b.pa1's hard violations were one CHANGELOG entry: observed-so-far scope, internal mechanics, long sentences. The final-tip audit's "3 more" were advisory; that audit passed 11/11 hunks.
   - The count is therefore about eight hard violations, mostly in b.ua9, plus soft ones. The three-question answers stand: several per lane, silent, not recovered by quorum.
5. **"Offer a once-per-lane cold read of the final customer-facing diff as an optional close-out step." Declined as a new step; the existing step gets the test instead.**
   - Quorum already runs exactly this: the post-completion review (`skills/quo-execute/references/post-completion-prompt.md`). It is a fresh agent that reads the whole final diff once per run (per Epic in execute), and its PHASE 6 covers code and docs, including cross-file inconsistencies.
   - In b.ua9 it ran (`postcomp-review-b.ua9-ua9w10.md`). It read the client pages and the PRD, and caught a cross-place contradiction (F3: writing-layers.md:70 vs. the shipped behavior). It judged nothing for the reader, and the planner's later cold audits still found reader violations.
   - So the missing piece is the test in that read, not another read. Fix the existing carrier: add one clause to the prompt's PHASE 6, so customer-facing hunks are judged by the customer-text test and the project guide's customer standard. The prompt is a shared reference, so this is an orchestrator-process edit: inventory-anchored, under the same cold review.
   - If runs after this still show the final read missing reader problems, revisit.
6. **live_edit-side asks:** the planner agrees with both. It would fold `CHANGELOG.md` into the `Customer-facing docs` bullet; that wording is the operator's. The guide line goes to live_edit's docs agent, which is also adding mechanical prose checks to live_edit's docs CI test.

**Batch scope after this input:** items 1–5 of `## Proposed change`, the two-sided clause, "written for a customer" as the scope wording, and the post-completion PHASE 6 clause. Add to the readers list: `skills/quo-execute/references/post-completion-prompt.md`, and its pins in `tests/`, if any.
## Operator decision and a second live_edit review (2026-10-14)

**Operator decision: narrow the customer-docs review.** Unit reviews read what the change touched, plus every other place that states a fact the change touched. This replaces "review the customer-facing docs whole". The decision follows the overseer's recommendation; the planner and live_edit's docs agent concur.

**Review by live_edit's docs agent** (pasted to the overseer; it checked quorum at `4e83c28`). It confirms the diagnosis and the three-key scope gap. Its points, judged on their merits:

1. **The draft test conflicts with a project guide that is more permissive. Accepted; this changes the wording.**
   - The draft bans "history" and "mechanism" outright. But a changelog entry is change history; live_edit's guide lets CHANGELOG entries carry ticket IDs (doc-writing-guide.md:335); and it allows rationale for behavior an operator observes, and key names an operator must inspect.
   - "A guide's stricter standard is part of the test" does not settle cases where the guide is looser.
   - Requirements for the final wording:
     - (a) where the project's guide sets a customer-text standard, it governs in either direction, matching the existing placement-precedence rule;
     - (b) "the reader's terms" is stated as a goal (terms the reader can act on), not as an absolute ban list;
     - (c) the test fits a changelog entry, which says what changed, for its reader.
   - This is the design of a new contract, so no run evidence is needed. It is also a gap between the role and the project guide.
2. **live_edit's CI does less than the planner said.** Its prose checks are on an unmerged branch, skip the CHANGELOG, are mechanical only, and would not have caught the internal names or the cross-page contradiction. No standing whole-set review exists.
   - This does not change the decision, whose reasons are general: it matches the SDD/PRD footprint scope, full reads missed these, and the cost grows with the set.
   - The gap it names is live_edit's: nothing reads its untouched customer pages. A periodic whole-set read (e.g. per release) is live_edit's process. Quorum has no release step to hang it on. Operator informed.
3. **The two live_edit asks are withdrawn.** Scoping by reader puts new changelog hunks in scope without any CLAUDE.md key. Where a project guide has no changelog standard, the generic test applies. Touched-only scope leaves an existing changelog backlog alone. That fits the operator's "ignore the changelog for now" in live_edit.
4. **It also backs the planner's optional close-out read and its log-line scope.** It brings no new argument: "that one pass is what caught these" is answered by the post-completion review being that pass, minus the test. The dispositions above stand: the PHASE 6 clause, and "written for a customer".
## Closed (2026-10-14)

Merged at `7eacfe0`, a fast-forward of `main` from `9caeabf`, not pushed. Hand edits on branch `bpca-customer-text` (Worker 1): a design checkpoint, a draft checkpoint, and two cold rounds.
- Round 1 had two behavior findings, both from the case where a guide is looser than the test:
  - the post-completion PHASE 6 sentence lacked the guide's precedence;
  - the review's ticket-ID deletion bullet reached changelog entries.
  Both fixed.
- Round 2 had no behavior findings, and one deletion: the review scope's "Customer text in a source file is the Engineer's to fix". The orchestrators route on what a fix changes (Phase C, part (g)), and b.ua9's reviewer named the Engineer unprompted.

The overseer audited the full diff (9 files, +34/−47) and ran `Full test`: 601 passed.

**What changed:**
- **A customer-text test,** carried verbatim by the Doc Writer and `/quo-doc-writer-review` and pinned in CONTRACT_SURFACES:
  > customer text is text written for a user, an operator, or an API caller to read, wherever it lives. It says only what its reader would act on or expect, in terms they can act on without the source, and omits nothing they need to act; a changelog entry says what changed for them. A customer-text standard in the project's doc writing guide governs, stricter or looser.
- **Scope by reader, not by key.** Customer text outside the keys, such as a changelog, is the Doc Writer's. Source-file customer text routes to the Engineer by what the fix changes.
- **One footprint for customer docs, SDD and PRD:** what the change touched, plus every other statement of a fact it touched (operator decision). Copies of a fact agree; one statement with a pointer is preferred. The Doc Writer's job 1 keeps an explicit "add the customer text its reader now needs".
- **The customer row** adds how clients call the API and handle its answers. The SDD row is unchanged.
- **The post-completion PHASE 6** holds customer text to the guide's standard, and where the guide is silent, to the test.
- **`/quo-setup`:** the customer-docs question names operations and API guides, and the doc-guide brief names the customer readers and their standard.
- **Deleted from the review:** the README-only `### Readme` floor, step 3's README checklist, the old step 4, and the Important/Not Important list.

Net shipped prose is +107; the test carried twice accounts for 138 of it. Caps are adjusted, with the reasons in the commit messages.

**Cleanup candidates (untouched):** the review's "Work item quality" list, and its README-era clean line ("README and architecture docs are up to date!").

**Validation:** none dedicated. The live_edit container picks this up only on rebuild. `## Check still open` (the next live_edit doc stage):
- customer hunks, including changelog entries and proto comments, are judged against the test and the guide;
- no reviewer proposes banned wording;
- copies of a changed fact agree;
- the doc share of agent time in the ledger stays near its usual 7–11%, since review reads less but may raise more findings.
