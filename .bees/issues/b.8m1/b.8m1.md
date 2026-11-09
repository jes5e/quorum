---
id: b.8m1
type: bee
title: Engineer asks design questions before building; review findings close a class at once; the ledger records UTC completion time
parent: null
reference_materials: null
created_at: '2026-11-09T10:29:28.099269'
status: done
schema_version: '0.1'
guid: 8m1o4m8uoy7qxh94x58m1udno99p7uih
---

## Description

Three small changes from the live_edit `/quo-execute` run of plan b.f9p, Epic 2: 14 Tasks, 87.7 h, 197 implementer dispatches. The evidence is the live_edit agent's pace diagnosis, `diag-epic2-pace-p4.md`, in container scratch (on the host, `~/.quorum-scratch`). The overseer checked it against the current skill text on 2026-11-09.

### 1. The Engineer builds first and asks the design question afterwards

**What happens.** `agents/engineer.md`'s design-question bullet says: "implement the rest of the assignment, stop at the undecided part, and return the open question". When the undecided part shapes the rest of the work, that order builds work which the answer then discards.
- Ten Analyst dispatches ran in 9 Tasks. About 517 engineer-minutes were superseded or redone after a design question.
- The worst case: T12 r1 built for 127 min, then asked, then a fresh r2 redid it in 121 min. T3 r1 built for 65 min first.
- On T13a and T14 the decider told the engineer to ask first. The question came back in 7–8 min, and T13a's gate was approved 35 min into the Task.
- **Three questions:** several Tasks in one Epic; silent (each return is legitimate); recovered, at hours of cost. Earned.

**Fix (restructure the existing sentence, no new rule).** The order follows the goal: when the open point would change how the rest is built, return the question before building. Otherwise, land the independent parts and stop at the open one. Keep the `## Design question` contract and the partial-return and status wording unchanged.

### 2. A kind of problem surfaces one instance per round

**What happens.** A finding names some instances of a class. The fix covers the cited sites. The confirming pass checks only those fixes ("Do not hunt beyond that"), so the next instance of the same class surfaces a round later.
- T13a test lane: tests over the 120 s budget, in TR r1, r2 and r3.
- T6 test lane: TR r2 through r5, each "confirming 1/1 plus 1 new item".
- T8 test lane: r3 through r5, on the CI change-gate enumeration.
- T9 code lane: one wording class ran C50 → C51 → C52.
- The diagnosis estimates about 2–3 h over the Epic.
- **Three questions:** five lanes in one Epic; silent; recovered slowly. Earned.

**Fix (a goal, fixing the class once).** A finding whose defect is a class names the class and lists every instance in the change set. The fix closes the class. The confirming pass checks the class within the files it already reads, not only the cited sites.
- Both review skills, `/quo-engineer-review` and `/quo-test-writer-review`, and their `## Confirming pass`.
- `/quo-test-writer-review` Step 2 already says this for site enumeration ("Report every unpinned site in ONE finding … closes the class in one pass"). Give the rule one home per skill, and don't add a second copy.
- Check that `routing.md`'s "a class of sites the finding names" reading still holds.

### 3. The cost ledger has no clock time (operator decision: yes, 2026-11-09)

**What happens.** The ledger header (`/quo-execute` :66 and `/quo-fix-issue` :79, a Tier-1 mirror) has a duration but no time. Orchestrators wrote made-up clock times anyway, one about 1 h off, and the pace diagnosis had to use file mtimes.

**Fix.** One column, the completion time in UTC read with one shell command when the row is written. Its start is that time minus the duration. This applies the same rule as b.9o9: the model has no clock.

## Not quorum's, or no change (recorded)

- **The resume bound looks only backward** (fresh only above 675k). Twice, orchestrators went fresh below it (622k, 669k) because the next pass would overflow. They judged it well without a rule, so nothing is added.
- **Mid-Task hand-offs lose the implementers** (5 fresh dispatches). They came from live_edit's own hand-off thresholds. A session change losing its Agents is designed; the diagnosis's own advice, to hand off at Task boundaries, is live_edit's.
- **Resumed usage reads `unknown`** (13b rows 338–355). The harness didn't carry it, and the skill already handles `unknown`.
- **The manifest reached 238 KB.** live_edit's hand-off wrote a RESUME HERE block per session into it, against `/quo-execute` :29 ("a live snapshot, not an accumulating log"). The fix is live_edit's: replace the block, and keep history in its own file.
- **Task bodies grew to 72 KB.** That's about 18k tokens, a small part of the ~200k a fresh agent spends getting oriented; the 3.6 MB SDD and monolith source files dominate. The appended revisions are the approved design.
- **Watch:** the breakdown left design open in 9 of 15 Tasks (about 14% of the Epic). If Epic 3 repeats it, look at `/quo-breakdown-epic`.

## Process

One small hand-edit batch with one cold review under the exit rule, and no dedicated validation. Net prose ≈ 0 for items 1 and 2. Item 3 adds a column to a Tier-1 mirror and its pin.

## Closed (2026-11-09)

Merged by fast-forward to `2c19d02`. The commits are `83bd2fb` (the draft), `0d63f6a` (the overseer's Checkpoint 1 change), `dc51ecf` (cold round 1), `4b3cff2` (the operator's SDD trim) and `2c19d02` (cold round 2). The lane closed under the exit rule. The work was Worker 1's; its checkpoints are `~/.quorum-overseer/b8m1-checkpoint-1.md` and `-2.md`. Full test: 601 pass, run by the overseer. Net shipped prose is +62, inside the operator's +65 budget, and the doc roles are untouched.

### What shipped

1. **`agents/engineer.md`:** "Look for such points before you build; on finding one, implement only what the answer cannot change — nothing, when it shapes how the rest is built — then stop and return the open question …" (+14).
2. **Both review skills** (+16 net):
   - The Overview says: "A finding whose defect is a class names the class and lists every instance in the change set, so one pass closes it."
   - The confirming pass's question 1 says a class finding "is closed only when no instance remains in the change set".
   - Four restatements of the same reason are cut.
3. **Both orchestrators' ledgers** (+32, a Tier-1 mirror):
   - a `completed (UTC)` column, "read with one shell command as the row is written";
   - the header is pinned in `SHARED_ANCHORS`.

Repo-only: `docs/sdd.md` :755 and :896 are now true.

### Findings

- **Round 1:**
  - A `suggestion` (behavior): the Overview's confirming-pass clause disagreed with the pass's "nothing else". It was restructured into question 1, and engineer-review's scope lines went back to "run only it".
  - A `nit`: the ledger rule got its own sentence.
  - A missed SDD reader.
- **Round 2:** no behavior findings. A REWRITE-BRIEF amendment was declined: nothing breaks without it, and the operator asked for no doc growth. A stale SDD sentence was made true.
- **Declined as predictions:**
  - an empty diff after an ask-first return (the Analyst reads the tree);
  - the design-question rule firing only on a mechanism;
  - the ledger time lagging behind an open gate.

### Check still open

At the next live_edit run after a rebuild, three things to check:
- Engineers ask open design questions within minutes, not after building.
- Class findings arrive as one list, and confirming passes close the class.
- Ledger rows carry real UTC times.
