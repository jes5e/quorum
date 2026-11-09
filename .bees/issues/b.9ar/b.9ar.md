---
id: b.9ar
type: bee
title: 'Doc roles stop SDD regrowth: the table''s kind decides placement first, and each pass shows its SDD growth'
parent: null
reference_materials: null
created_at: '2026-11-09T10:53:28.394144'
status: done
schema_version: '0.1'
guid: 9ar289xq12uv8tkvym8uoukz612gd7t1
---

## Description

The evidence is from the overseer's subagent audit of 2026-11-09 against live_edit `main` 8b4d878dc, and from the live_edit agent's root-cause report, `rootcause-bloat-p4.md` in container scratch (`~/.quorum-scratch` on the host). The operator approved this batch on 2026-11-09, as the first of three: the doc lane, then code placement, then ticket bodies.


live_edit's SDD (`docs-internal/sdd.md`) was pruned to 0.75 MB on 2026-09-30, after b.sb7 and b.gmg. It was back at its pre-prune size, 2.4 MB, by 10-14, and is 3.44 MB on 11-07, about 860k tokens. Most of the growth is code mechanism that quorum's Doc Writer adds during quorum runs and the Doc Reviewer doesn't flag. Both quorum's table and live_edit's own guide send that material to code comments.

### Evidence

**Size on `main`:**

| Date | Size | Note |
|---|---|---|
| 09-29 | 2.41 MB | |
| 10-01 | 0.80 MB | |
| 10-06 | 1.51 MB | |
| 10-14 | 2.41 MB | |
| 10-22 | 2.90 MB | |
| 11-07 | 3.44 MB | |

**Who wrote it.** Net growth since 10-14 is +1.10 MB:
- fix-issue close-outs: 56%
- execute Task commits: 21%
- quorum WIP checkpoints: 11%
- post-completion fixes: 7%
- other: 4%

So about 90% comes from quorum runs. Transcripts weren't read, so the Doc Writer can't be told apart from the run lead inside a commit.

**What it is.** A sample of 22 passages added after 10-14 classified as:
- 10 SDD-proper;
- 9 code mechanism;
- 3 history or measurement.

A parallel live_edit audit (`~/.quorum-scratch/audit-sdd-size-p4.md`) finds about 40–45% mechanism by bytes. Mechanism example, at `sdd.md:4271`: "1. **Length probe** (`ExternalValueStore::probe_value_lengths`): one `STRLEN le:ext:data:{hash_hex}` per hash, and an `EXISTS` for one that reads 0 …". Lines naming functions, code paths or `.rs` files went from 348 to 983, and measurement words from 39 to 427.

**The project guide agrees with the table on mechanism.** live_edit guide l.11 says: "How the code works (mechanism, constants, names, step-by-step flow, including flows across files): the code, its comments, and its module-level docs". CLAUDE.md l.59 says the same. So the precedence rule didn't cause the mechanism share. The guide does send these to the SDD, about 20–30% of growth:
- measurements (l.285);
- provenance-scoped claims (l.286, l.380);
- customer detail it cuts (l.132, l.150, l.126 "Everything else goes to the SDD, or nowhere");
- known bugs and unfinished features (l.127, since 11-05);
- the full env-var and per-key references (l.13).

**Reviewers.** About 95 doc reviews were saved after 10-14:
- None flagged code restatement or SDD growth. Step 3's "a restatement of the code, however accurate … return its deletion" was never used.
- They did police history narrative, and those fixes were acted on.
- Several asked for more SDD text: `b2d8-r1-docreview-w10.md` ("It passes the SDD test"), and `doc-review-b.ouo-r1-w2.md` ("Restate why caching stays acceptable… Say that").

**Three questions.** On most quorum commits; silent; not recovered, since it regrew past the pre-prune size within two weeks of a prune. Earned. The prose fixes b.sb7 and b.gmg have already failed once against this.

### Quorum text that pulls toward the SDD (candidates, to be traced at design)

1. **The SDD test is applied alone.** The writer's job 2 gates on "a fact of a kind the table's SDD row names, and the fact passes the SDD test". But the test sentence, and the review's copy at `quo-doc-writer-review` :11, state the test without the kind condition. In a correctness-heavy codebase almost any mechanism "would make a worse design decision" if missing, so it passes.
2. **The review's bullet** (:70) "Does each fact the change made appear once where the SDD test … puts it" reads as a request to add, and reviewers asked for more SDD text.
3. **The PRD/SDD line** ("one that names a field, code, metric name, or env var, or states an exception or limit … is the SDD's") was meant to split PRD from SDD. It may be read as sending code-level sentences to the SDD.
4. **Customer text cut by the customer-text test** may default to the SDD. That's live_edit's l.132, l.150 and l.126. Check whether a quorum line implies it.
5. **The writer is on every Task.** `quo-breakdown-epic` :113 gives every code Task a `doc-writer` Subtask ("do not judge that no doc does"). The writer decides what changes, so this is neutral only if "nothing" is a normal outcome of job 2. Check that job 2 reads that way.
6. **Nothing measures growth.** The SDD test claims it "keeps the SDD from growing", but nothing measures that. Since the prune: +2.68 MB added, 24 KB removed (the root-cause report §3). In live_edit, every budgeted artifact held or shrank, and every unbudgeted one grew 3–7× (§3's table).

### Direction (for design, not decided)

- **One home for placement.** The table's kind decides first. The SDD test only filters SDD-kind facts. Mechanism is the code's even when it would pass the test. Fix the class: the writer, the review, the PRD/SDD line, and the PHASE 6 paraphrase.
- **A structural guard, since prose has failed twice.** Growth becomes visible in every pass. The operator approved this direction on 2026-11-09; the live_edit agent proposes the same thing. For example:
  - the Doc Writer's return states the SDD's net change (`+N / −M` bytes or lines);
  - it lists each SDD paragraph added or grown, with its table row and what it replaces;
  - the Doc Reviewer checks that list, so a skipped check is visible.

  Prefer the smallest guard that does this.
- **"Nothing" is a normal outcome** for job 2, and the reviewer also asks what older text a change makes redundant.
- **Not quorum's:** a size ceiling with a check is per-project, which is live_edit's plan. The re-prune is live_edit's. So are its guide lines l.126, l.127 and l.132.

## Process

This is a design batch on the doc roles, with cold reviews under the exit rule and a fresh worker:
- `agents/doc-writer.md`;
- `quo-doc-writer-review`;
- `quo-breakdown-epic` :113;
- the post-completion prompt's PHASE 6, which today has no SDD placement check: decide whether it needs one, or whether the per-unit review is enough.

Net prose should be about zero or lower, apart from the guard's contract. Validation is the next live_edit runs after a rebuild, with Doc Writer and Doc Reviewer returns saved to scratch (asked of live_edit 2026-11-09).

## Closed (2026-11-09)

Merged by fast-forward to `7c66b9b`. It took two design checkpoints, a draft, and two cold rounds. The lane closed under the exit rule. The work is Worker 1's, and its checkpoints are `~/.quorum-overseer/b9ar-checkpoint-1.md` to `-3.md`. Full test passes (601), run by the overseer. Net shipped prose is +60:

| File | Change |
|---|---|
| doc-writer | −9 |
| doc review | +64 |
| doc-reviewer wrapper | +9 |
| breakdown | −4 |

### What shipped

- **One home for SDD placement: the SDD test.** It is pinned in the writer and in the review. It now reads: "a fact goes in the SDD only if the SDD holds its kind and an agent that lacked it would make a worse design decision or reintroduce a fixed bug. How the code works stays in the code however much an agent would miss it: the SDD states the rule the code keeps, not the steps, names, or constants that keep it." Job 2 defers to it. Sentences it made redundant were cut.
- **The guard is on the reviewer side.** The doc review lists, from the SDD's diff, every paragraph the change added or grew. Each entry gives the kind, what it replaces, and pass or fail ("code mechanism, history, and ticket IDs fail"). If nothing grew, the review says so in one line. One finding returns the deletion of everything that fails. The doc-reviewer wrapper carries these lines even when nothing fails.
- **Breakdown:** "the Doc Writer, not you, decides which docs change, often none".

### Decisions

- **The writer-side growth list was weighed and set aside at Checkpoint 1.** The observed silent failure was the reviewer, and the writer's misreading is fixed at its cause, so the reviewer-only guard is about +50 rather than about +170. If runs show writers still adding mechanism despite the review's list, the writer-side list is the next step.
- **Declined:**
  - a byte count (the writer has no shell, and nothing reads a number);
  - a PHASE 6 sentence;
  - round 1's PRD/SDD-line scoping and guide qualifier, both predictions.

### Check still open

At the next live_edit runs after a container rebuild, with Doc Writer and Doc Reviewer returns saved to scratch, check:
- Does each doc review carry the growth list, or its "grew none" line?
- Do mechanism paragraphs show as failing and get deleted?
- Is history still policed?

live_edit is pruning its SDD and adding per-unit size ceilings in its guard tests, which is the project side of this fix.
