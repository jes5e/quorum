---
id: b.d7o
type: bee
title: Find why the Doc Reviewer missed 63 of 72 failing doc statements in live_edit's Epic 3, then fix the checks the evidence points at
parent: null
reference_materials: null
created_at: '2026-11-15T16:22:22.396649'
status: done
schema_version: '0.1'
guid: d7oorsw3couhaxcksv6aefoow36yaatv
---

## Description

In live_edit's Epic 3, the Doc Reviewer missed most of the documentation text that fails quorum's own tests. Find out why, check by check, before changing any rule. The operator agreed on 2026-11-15.

### Evidence

An audit of every doc statement Epic 3 added or changed in live_edit (`bee/b.f9p`, `11bb456f5..b7580dd4e`) is at `~/.quorum-scratch/epic3-doc-audit.md` (container `/tmp/.quorum/`). It judged each statement against the Doc Writer's SDD test and customer-text test, quoted verbatim, plus live_edit's doc writing guide:
- 523 statements judged, 72 failing (13.5 KB). Its own breakdown:
  - the internal changelog: 45 of 142 (35 of those in bug-fix entries merged during the Epic: test lists, code mechanism, story);
  - the SDD: 25 of 368 (10 are figures and derivations with no pointer to a validation record, 13 are restatements of rules homed elsewhere or test names and method);
  - customer text: 2 of 13. Separately, 3 statements are false at tip and one customer-visible change is undocumented.
- **The Doc Reviewer never flagged 63 of the 72,** flagged 6 that were only partly fixed, and 3 have no saved review. In several cases the reviewer asked for the failing text.

Three questions: continuous across the Epic, silent, and not recovered by the run. A later audit found it.

Before this, a tally of 66 saved Doc Writer returns since 2026-11-09 found customer-doc bias largely gone (customer touches from about 70% to about 15% of passes). The SDD residual is about one first review in six, cut when flagged. So the problem is concentrated in what the reviewer doesn't catch.

### What to find out first (Checkpoint 1, no edits)

For each of the 72 failures (the audit's working verdicts may be gone; rebuild from the audit's tables and the saved `doc-writer-*` and `doc-review-*` returns in `~/.quorum-scratch`), work out:
- which of the Doc Reviewer's checks (`skills/quo-doc-writer-review/SKILL.md`, `agents/doc-reviewer.md`) should have caught it;
- why it didn't. For example:
  - the SDD list covers only paragraphs "added or grew", and an in-place figure re-pin neither adds nor grows a paragraph;
  - a restatement in another section isn't compared with its home;
  - the internal changelog has no check beyond its size cap;
  - the reviewer's own requests for text conflicted with the test;
  - or the check is there and was misapplied.
- Then group the misses by cause, and propose the smallest restructure of the existing checks that would have caught each group. Add no check for a group the evidence doesn't show.

### Constraints

- **Kind 5:** earned by this evidence, so fix the cause the evidence shows. Restructure existing checks; don't append parallel ones. Watch the word count.
- **Project-neutral:** live_edit's internal changelog is its own artifact. Quorum's checks can apply "the project's doc writing guide's rule for that doc" but never name it.
- **Readers:**
  - the doc review skill and its wrapper `agents/doc-reviewer.md`;
  - `agents/doc-writer.md`, where the tests live, both copies pinned;
  - the orchestrators' doc-lane relay;
  - the SDD.
- **Out of scope:**
  - whether a Task has a doc-writer Subtask (kept on every behavior-changing Task, decided 2026-11-15);
  - live_edit's own guide and changelog cleanup.

## Process

A hand-edit batch in a worktree:
1. **Checkpoint 1:** the miss-by-miss diagnosis and the proposed restructure, with no edits. The operator approves.
2. **The draft.**
3. **One cold review under the exit rule.** It replays a sample of the 63 misses, plus a few audited statements that passed, through the revised review. The misses should now be flagged, and the passes not.
## Closed (2026-11-15)

Merged by fast-forward from `2968ce4` to `cbe1357`, with the operator's go: "go" at Checkpoint 1 and "merge" at Checkpoint 2, both given in the overseer's tab.

**Commits:**
- `a378bd4`: the draft;
- `3c8e754`: cold round 1;
- `4bb822e`: round 2;
- `cbe1357`: round 3, which closed the lane.

The work was Worker 1's. Its checkpoints are `~/.quorum-overseer/bd7o-checkpoint-1.md` (the diagnosis and miss table) and `-2.md`. Full test passes (602). The overseer ran it and read the full diff.

**Net shipped: +49 words.**
- `skills/quo-doc-writer-review/SKILL.md`: +50, cap 2,595 → 2,645.
- `agents/doc-reviewer.md`: −1.

### Diagnosis

Epic 3 ran the doc review as it stood after the prune. The prune cut no check that bears on any of these misses. Of the 63 misses:
- **A (41): other docs were judged only for truth.** The internal changelog had no test beyond truth, and 16 of its failing statements were requested by the reviewer.
- **B (12): edited SDD paragraphs were never listed.** In-place figure re-pins, rewords and trims never "grew", so the SDD list skipped them.
- **C (3): a ticket's request overrode placement.** The Doc Writer's "the table governs over a ticket" had no counterpart in the review.
- **D (about 18, overlapping A–C): reviewer-proposed text went untested.** It was confirmed against its finding only.
- **E (3): one verdict per paragraph hid a failing sentence.**
- **Declined:**
  - F (1): a customer row that a later Task made false. Once, and the goal is already stated.
  - H (2): the check was present and applied with the wrong verdict.

### What landed

Each change rewords an existing sentence:
- Scope adds "any other doc the Doc Writer edited". The Overview judges those docs by "the project's doc writing guide's rule for that doc". Step 3's heading becomes "The docs in scope".
- The placement bullet covers facts "made or edited", placed "where the Overview puts it, whatever a ticket or relayed decision asks".
- The SDD list covers paragraphs "added or edited", judged "as it now reads", returning "each added or edited sentence that fails".
- Confirming-pass question 1 also checks that the fix "passes what the Overview judges its doc by".
- The site enumeration places each statement "where the Overview puts it".

**Yield.** Against live_edit's guide as it read at `b7580dd4e`, the change catches about 33 of the 63 misses. The rest of group A (test lists and fix stories) depends on live_edit's guide. live_edit then decided (2026-11-15, Performance Planner 4):
- a fix's story goes in the commit message only;
- changelog entries carry no Tests, Design or Rulings bullets;
- the guide wins over tickets and rulings;
- test-only fixes get no entry.

### Operator decisions

- Approved: Checkpoint 1, after asking for, and getting, a check that this batch wasn't over-engineering.
- The lane closed after round 3, with no round 4. Round 3's two behavior findings were declined, so no text changed for them.
- **Residual (round 3, F1):** the post-completion PHASE 6 flags "missing edits the ticket called for". It could ask to restore a restatement the lane review removed. No run shows it. It would surface at a gate.
- **Round 3, F2, offered for filing:** `/quo-execute` has no reader for the Doc Writer's declined-requests list, which `/quo-fix-issue` renders in Doc Sync. Filing awaits the operator.

### Watch on the next live_edit runs

- Changelog findings made by the guide's rule.
- Edited SDD paragraphs listed, with verdicts per sentence.
- Reviewer-proposed text tested at the confirming pass.
- No run of false findings on text that should pass.
