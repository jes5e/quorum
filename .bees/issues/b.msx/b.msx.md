---
id: b.msx
type: bee
title: 'Execute surfaces every implementer''s operator-facing return: operator steps from any role, and the Doc Writer''s declined requests'
parent: null
reference_materials: null
created_at: '2026-11-16T00:18:07.487773'
status: open
schema_version: '0.1'
guid: msxweoad9sa2b51f7rncsy8q8yzx2dip
---

## Description

Two gaps in what `/quo-execute` does with an implementer's return that is meant for the operator, plus breakdown's half of the first. The operator said yes to filing both on 2026-11-15, as one small batch.

### 1. Operator steps go to the role whose work needs them, and execute routes any implementer's request for one

- **Breakdown:** a step only the operator can take belongs in the Subtask of the role whose work needs it, not wherever the drafter happened to put it.
- **Execute:** the Operator-action rung (§4, and its gate in §6) reads `## Operator action needed` only from an Engineer's return. A Test Writer or Doc Writer can need an operator step too.
- **Evidence:** live_edit's Epic 3 Task 3 (T-E). A Test Writer needed an operator step. Execute's text routes only an Engineer's, and the orchestrator handled it unaided. live_edit suggested the change on 2026-11-15 (suggestion 5), and Overseer 6 assessed it then: UPDATE 10 of the overseer state.

### 2. Execute has no reader for the Doc Writer's declined requests

- **The gap:**
  - `agents/doc-writer.md:39` tells the Doc Writer to name each request it declined, and why, in its return. A request is declined when a ticket or relayed decision asks for a fact somewhere the table or the project's guide doesn't put it.
  - `/quo-fix-issue` shows those requests in its `**Doc Sync**` summary line (`SKILL.md:263`), "so the operator can refile it".
  - `/quo-execute` has no matching reader, so in an execute run a planner's request disappears without a trace.

  This is a return line with no reader in one of the two orchestrators: a gap between two agents.
- **Why now:** b.d7o (merged at `cbe1357`) made the Doc Reviewer hold placement "whatever a ticket or relayed decision asks", so declines will be more common. live_edit has also adopted "the guide wins over any ticket, Subtask or ruling".
- **Evidence:** b.d7o round 3, F2, found by reading the skill files (`bd7o-checkpoint-2.md`). No run has yet shown a lost request doing harm. The fix is earned as a gap between two agents, not as a run failure.

### Constraints

- **Mirror, don't invent.** Execute's reader should match fix-issue's existing sentence, wherever execute reports Task or Epic results to the operator. Keep the mirror map and the inventory in step.
- **Fix the class once.** Item 1 and item 2 are the same kind of gap: execute surfacing what an implementer returns for the operator. Find every rule in both orchestrators that reads an implementer's operator-facing return, and give each kind one home.
- **No predicted cases.** Add nothing beyond what these two pieces of evidence earn. Watch the word count. Execute's body is near its line budget.
- **Process:** a hand-edit batch in a worktree, inventory-anchored, with cold reviews under the exit rule. Checkpoint 1 is the design: the readers, the wording and the word deltas, for operator approval.

## Amendment (2026-11-16, overseer)

**Item 1 goes to the three questions before anything is drafted.** Its only evidence, Epic 3 Task 3 T-E, is the orchestrator routing a Test Writer's operator step correctly with no rule written for it. That is rare, loud and recovered unaided. By CLAUDE.md `**How a skill improves.**`, it earns one goal sentence at most, and maybe nothing. The overseer folded it into this ticket without applying that test.

**What's left is likely item 2 alone:** one sentence in execute, mirroring fix-issue's Doc Sync line. That's small enough to ride along with the next batch that edits `/quo-execute`. It doesn't need a batch of its own.

