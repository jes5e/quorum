---
id: b.4wd
type: bee
title: Prune the code and test review skills by evidence, as b.tdq did for the doc review
parent: null
reference_materials: null
created_at: '2026-11-09T22:15:22.543091'
status: done
schema_version: '0.1'
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

## Closed (2026-11-10)

Merged by fast-forward to `cceec15`:
- `b870277`: the prune (C1–C9, W1–W5, K11);
- `c71b4c8`: cold round 1, with no behavior findings;
- `cceec15`: K10, approved by the operator.

The lane closed under the exit rule. The work was Worker 1's, in a fresh session. Its checkpoints are `~/.quorum-overseer/b4wd-checkpoint-1.md` through `-3.md`. Full test passes (601), run by the overseer.

**Net shipped: −2368 words.**

| File | Change |
|---|---|
| Engineer review | −991 |
| Test review | −971 |
| Doc review | −144 (K11) |
| `code-reviewer.md` | −166 |
| `test-reviewer.md` | −96 |

### Evidence

- **Saved live_edit returns read:** 84 code reviews, 80 test reviews and 23 post-completion sweeps.
- **Code reviews:** 218 findings. The checks that do the work are stale comments, security and correctness, error handling, and second-order effects.
- **Test reviews:** 332 findings. The checks that do the work are stale comments, owed tests, test correctness, and redundancy.
- **Post-completion misses:** these fall under existing checks, so nothing was added.
- **Per-cut evidence:** in `b870277`'s message.

### What was cut

- Generic lines, the obsolete loop-bounding text, and "only report if important" (which the severity scale and the runs contradict).
- The Include/Exclude list.
- Step 0a's git recipe, now the same goal paragraph as the doc review.
- The test review's glob recipe, now its goal.
- The human-addressed tip.
- The Python Black-25 check: it fired 0 times, the case was handled without it, and the form it flags is legal since Python 3.14.
- The duplicate convergence-brief half.
- The wrappers' restatements.
- K11: the trailer rationale, removed from all three review skills. It lives in `docs/doc-writing-guide.md`, and every emitted string is kept.
- K10: the duplicate worked examples.

### Kept

- **Untouched:** contracts, pins, the confirming passes, the severity scale, and the b.8m1, b.9o9 and b.9ar text.
- **Identical across all three skills:** the shared text.

### Validation

The cold round replayed the newest real reviews:
- `code-review-redisrs-e2-postcomp-1-r1.md`: all five defects still asked for;
- `test-review-redisrs-e2-postcomp-1-r1.md`: all three still asked for.

### Noted for later

- The orchestrator prune batch: the never-fired sweep rules (missing-list, explicitly-empty list), which are wired through both orchestrators.
- b.7qb: the stale `docs/sdd.md:182` time-budget short-circuit.
