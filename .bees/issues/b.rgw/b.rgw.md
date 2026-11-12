---
id: b.rgw
type: bee
title: A revision replaces the ticket text it supersedes, so a ticket body holds the current spec
status: open
created_at: '2026-11-11T21:58:06.739477'
schema_version: '0.1'
reference_materials: null
guid: rgwjhphv22xa43qvepmquhkpvmuceqsx
---

## Description

When the design of a Task changes mid-run, quorum appends the new design to the ticket and leaves the superseded one in place. Every later agent (PM, writers, reviewers, the next session) reads the tickets as the spec, so it reads every revision and has to work out which one holds. Bodies grow without bound, and stale text sits beside current text. The operator agreed on 2026-11-11 to fix this: a revision replaces the text it supersedes.

### Evidence

live_edit's root-cause report, `~/.quorum-scratch/rootcause-bloat-p4.md` §5 and root cause 6:
- **Task `t2.dkt.5o.3v` grew from 4.3 KB to 172 KB (40×).** It carries **three** appended `## Design revision (Analyst)` sections, each marked "SUPERSEDES revision N where they differ", with the superseded text still in place. It also carries eight decider-ruling sections and a pasted 50 KB Design Proposal.
- **`.bees/` grew from 3.24 to 15.75 MB.** 63 of 2,449 bodies are over 25 KB, and the largest is 227 KB.
- **Every fresh agent re-reads all of it,** which feeds the roughly 200k-token re-ground floor.

Three questions: continuous, silent, never recovered unaided.

### The quorum text that causes it (to verify)

- **`/quo-execute` §6, Analyst gate Approve:** "Record the directive in the ticket at the escalation's scope under `## Design revision (Analyst)`, because the PM and every later role read the tickets as the spec." This doesn't say what happens to an earlier revision section, so each escalation adds another.
- **Check `/quo-fix-issue`** for the same, and for where its directive lives.
- **Deferral encodes** (`## Deferred from … run (<timestamp>)` in execute, fix-issue, breakdown and plan) append by design. Each one adds work, so it supersedes nothing. They are probably right as they are; confirm before touching them.

### The goal

A ticket body holds the current spec. When a design revision, or anything else quorum writes into a ticket, supersedes earlier text, it replaces that text rather than sitting beside it. The superseded version stays recoverable through git history and the proposal file, so nothing is lost.

### Constraints

- **State it as a goal** where the write happens. No archive machinery, no size caps, no consolidation step: git history already holds every earlier version.
- **The ticket body's original problem statement stays.** Only quorum's own superseded additions are replaced. The body is what the PM checks the diff against ("the body stays the problem statement").
- **Readers:** the PM's directive handling (`agents/pm.md`), the per-Task writers, and the post-compaction re-read. Each must still find the current directive after the change. Define-before-write for the section heading, which is a contract another agent reads.
- **Ticket-system neutral:** say "the ticket", not bees mechanics.
- **Out of scope:**
  - decider-ruling sections, which are live_edit's decider practice, not quorum text (tell live_edit separately);
  - the pasted 50 KB proposal, unless the quorum text causes it (check).
- **Orchestrator process:** inventory-anchored hand edits, mirrors in step, line budget, a cold review with REWRITE-BRIEF §5/§6 and CLAUDE.md's review criteria.

## Process

One hand-edit batch:
1. **Checkpoint 1:** the design, with no edits. Every sentence that writes into a ticket body mid-run, which of them supersede and which add, the wording, the readers, and the expected word deltas.
2. **The draft.**
3. **One cold review under the exit rule,** with role-plays:
   - (a) a second and third Analyst revision on the same Task: the body ends with one current revision section, and the PM traces against it;
   - (b) a compaction mid-Task: the orchestrator re-reads the ticket and finds the current directive;
   - (c) a deferral encoded into a ticket that already holds an earlier deferral: both stay, because they add work rather than supersede.

Live_edit picks the change up at its next rebuild.

