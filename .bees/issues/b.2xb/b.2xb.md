---
id: b.2xb
type: bee
title: Test review lists every new site and its covering test in round 1, so a partial enumeration shows
parent: null
reference_materials: null
created_at: '2026-11-16T09:46:32.384541'
status: done
schema_version: '0.1'
guid: 2xbn8rp7ix1anbd9dqzmmo68admfrye9
---

## Description

The test review's first-round site enumeration returns only the gaps it found, so an enumeration that covers part of the change looks the same as a complete one. Make its result visible: list every site the change introduced, and the test that fails without each one. A skipped site then shows up in round 1, not in the late-chain enumeration three rounds later.

### Evidence (live_edit, Epic `t1.f9p.mh`, Task 1b `t2.f9p.mh.rg`, 2026-11-15/16)

- **The diff:** about 56 new branch sites. The test Subtask, written before the code existed, named 25 cases. After the Test Writer's first pass, 27 sites had no failing test.
- **Round 1** (`~/.quorum-scratch/test-review-t1b-r1-w7k4.md`, finding 7) applied `/quo-test-writer-review`'s "New-mechanism site enumeration" and listed 11 untested branches.
- **Rounds 2 and 3** were `earned`. **Round 4** was the late-chain enumeration (`quo-execute` §7). It listed 16 more uncovered sites, plus 3 tested sites with no recorded red run.
- **Cost:** each instalment took a writer pass plus a review. The test lane's fix loop ran about 105 minutes after the first review, plus a final pass (`~/.quorum-scratch/diag-t1b-pace-size-pp4k.md`).
- **Three questions:** once clearly, and Task 2 is the same kind of Task. Silent until the late-chain rule fired. Recovered by design, but late and at the price of extra rounds.
- **Several missed sites were error and shutdown paths the Engineer added while implementing.** No ticket could have named them in advance. So the site list has to come from the diff, not the ticket.

### The likely fix (to confirm at Checkpoint 1)

- **Reword the existing first-review check** (`skills/quo-test-writer-review/SKILL.md`, "New-mechanism site enumeration") so it lists every site with its covering test or "none", not only the unpinned ones. This is the same shape as the doc review's SDD list, "so a skipped check shows".
- **Check the late-chain enumeration** (`quo-execute` §7, the `## Site enumeration requested` line and step 3 of the test review's confirming pass) for what it still adds. If the first round already lists every site, the late-chain trigger may be cut or narrowed. Prefer a cut to keeping both.
- **The Test Writer side:** `agents/test-writer.md` covers the Blast radius and the design decisions. Whether it should also cover every new branch in the diff is a question for Checkpoint 1, with the evidence.

### Constraints

- Restructure existing sentences; don't add a parallel check. Watch the word count.
- The orchestrator side (§7's late-chain rule) is an orchestrator hand edit: inventory-anchored, mirrored in fix-issue, with cold reviews under the exit rule.
- Neutral: no language-specific notion of "branch". Sites are the hooks, branches and error paths the skill already names.

## Closed (2026-11-16)

Merged by fast-forward to `5553313`, rebased onto `08ffbe9` (b.txn). The operator's go was "ok to your recommendations" at Checkpoint 1 and "merge", both in the overseer's tab.

**Commits:**
- `6a49ae2`: the draft;
- `ef6a386`: cold round 1;
- `c3d350f`: cold round 2.

The work was Worker 1's. Its checkpoints are `~/.quorum-overseer/b2xb-checkpoint-1.md` (the evidence table) through `-3.md`. Full test passes on `main` after the merge (601), run by the overseer, who also read the full diff.

**Net shipped: −839 words,** across both orchestrator bodies, three review skills, three reviewer wrappers and the routing reference.

### Evidence

- **Task 1b:** round 1 listed 11 gaps and round 4's late chain listed 16 more. Round 1's output was gaps-only.
- **The late chain** fired 23 times since 2026-09-17: 21 on the test lane, 2 on the code lane, 0 on docs.
  - On the test lane it found real gaps in at least 15. Every round-1 list a later round showed incomplete was gaps-only.
  - Its trigger (two `earned` rounds) has nothing to do with coverage, and it missed 7 lanes.
  - On the code lane it found nothing to show either time. The docs reader never fired.

### What landed

- **The test review's "Site list".** Ahead of the work items, one line per site the change introduced (each hook, branch and error path the diff adds or changes, plus each owed test), with the test that fails without it or `none`. A one-line empty form. One finding returns every `none`. The wrapper carries the list.
- **The late chain is cut:**
  - the `## Site enumeration requested` relay;
  - the `enumerated` classification and the `close — enumerated` decision;
  - the earned-chain test and docs clause (now code-lane only);
  - three confirming-pass third steps;
  - three wrapper relay sentences;
  - the pins.
- **Re-homed readers.** The cut left two relays without a reader, a gap between two agents caught by the tests. The doc review's scope now names the doc sites a relayed `## Blast radius` or `## Design decisions for writers` names. The test review's Site list reads both. CONTRACT_SURFACES now pins all three review skills for both headings.

### Operator decisions

- **The cut,** not the narrow alternative.
- **Accepted residuals:**
  - sites added after round 1, by a source change, get no new list in the lane;
  - an incomplete round-1 list has no in-lane backstop. **Audit one saved round-1 list against the diff on the next live_edit run.**
- **D12:** the operator decided this is no net loss of review coverage. It's recorded in REWRITE-BRIEF's 2026-11-16 amendment.

### Sync

Old manifests read sensibly (role-play e):
- an `enumerated` value only falls into the render's remainder;
- `close — enumerated` sits on a closed lane;
- a lane left at `another round` gets at most one extra confirming pass.

Safe to sync at a convenient point. A lane mid-flight at the sync may lose its late listing once, which is within the accepted residual.

### Watch

- Round-1 site lists are complete against the diff (the audit above).
- Test lanes with fix chains close without the late chain.
- The doc review checks the owed doc sites.
- Each `none` gets a test or a reasoned "not covered".
