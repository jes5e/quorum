---
id: b.4wd
type: bee
title: Prune the code and test review skills by evidence, as b.tdq did for the doc review
status: open
created_at: '2026-11-09T22:15:22.543091'
schema_version: '0.1'
reference_materials: null
guid: 4wd9hpvf15ruwin6i1uonmtzga43pkvk
---

## Description

Prune `/quo-engineer-review` (about 6,500 words) and `/quo-test-writer-review` (about 3,800), and their wrappers `agents/code-reviewer.md` and `agents/test-reviewer.md`. Use the method b.tdq used on the doc review. That batch cut 608 words, every check that fired survived, and a replayed real review still found its defects. The operator agreed on 2026-11-09. The method is in the memory `feedback_prune_by_evidence` and in b.tdq's closing note.

### Method (as b.tdq)

1. **Catalog the checks.** List every check each skill and wrapper states.
2. **Tally the saved returns.** Subagents tally the saved live_edit code and test reviews in `~/.quorum-scratch` against that catalog, with a fixed schema: check ID, finding, severity, acted on. Use the newest as the main sample. Include the post-completion sweeps' code and test misses.
3. **Classify each check:**
   - (a) fires and works: keep it word for word and move it up;
   - (b) never fires: keep it if it's a protected kind, otherwise it's a candidate unless a run shows the case handled without it;
   - (c) duplicate;
   - (d) generic boilerplate.

   Every cut carries its evidence in the commit.
4. **Replay in the cold round.** Replay the newest saved code review and the newest saved test review that found real defects against the pruned skills. Check that the same defects are still found.

### Known candidates

These cuts already happened in the doc review, so check the same text here:
- the "infinite loop … be selective" text: its reader has been gone since b.vtw;
- "only return issues if very important", which contradicts the severity scale;
- step 0a's git recipe;
- generic "understand what changed" steps;
- duplicated worked examples;
- the wrappers' cold-start, responsibilities and intro restatements.

### Keep

- **Untouched:**
  - output contracts, trailers and pins;
  - the confirming pass;
  - the severity scale;
  - b.8m1's class sentences, b.9o9's scanning-test goal and b.9ar's text, which are recent and untried.
- **In step across all three review skills:** text they share, such as the severity paragraph and the section-4 trailer paragraph, stays identical. A cut there is made in all three, the doc review included, in the same batch.
- **Protected areas:** any cut inside the output-shape area goes to the operator as a separate call.

## Process

One hand-edit batch:
- **Checkpoint 1:** the evidence table and cut list for both skills, with no edits. The operator approves the cuts.
- **The draft.**
- **One cold review** under the exit rule, with the replays.

