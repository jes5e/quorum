---
id: b.d7o
type: bee
title: Find why the Doc Reviewer missed 63 of 72 failing doc statements in live_edit's Epic 3, then fix the checks the evidence points at
status: open
created_at: '2026-11-15T16:22:22.396649'
schema_version: '0.1'
reference_materials: null
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

