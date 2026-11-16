---
id: b.2xb
type: bee
title: Test review lists every new site and its covering test in round 1, so a partial enumeration shows
status: open
created_at: '2026-11-16T09:46:32.384541'
schema_version: '0.1'
reference_materials: null
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

