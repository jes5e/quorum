---
id: b.pca
type: bee
title: 'Doc roles have no test for customer-facing text: it is checked for truth, never for its reader'
status: open
created_at: '2026-10-14T12:12:59.897506'
schema_version: '0.1'
reference_materials: null
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

