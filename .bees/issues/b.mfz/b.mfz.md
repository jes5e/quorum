---
id: b.mfz
type: bee
title: Measure the orchestrator context spent repeating ticket bodies per Task; if material, relay shared bodies by a per-Task scratch file
status: open
created_at: '2026-11-16T09:46:33.013886'
schema_version: '0.1'
reference_materials: null
guid: mfzqy7c6u5a2youm2b2o133fsgsiphxh
---

## Description

`/quo-execute` §5 embeds each ticket body verbatim in every dispatch: the Task body, the role's Subtask bodies, and, since b.86z, the Epic's `## Epic-wide contracts`. On large Tasks that text is repeated across a Task's dispatches, at a cost in the orchestrator's own context. Measure the cost first, then decide whether shared bodies should travel as a scratch file the orchestrator writes once per Task. Each role would read the file, and the role's own Subtask would stay verbatim in its prompt.

### Evidence (live_edit, Epic `t1.f9p.mh`, 2026-11-15/16)

- **Two orchestrators departed from the rule.** They sent the Task body and the Epic contracts by ticket pointer instead of verbatim, to save about 15k tokens per prompt set, about 30k for the two Phase B writers. One did it after passing the 675k resume bound. The decider refused to approve it as a departure.
  - Sources: `~/.quorum-scratch/run-state-t1.f9p.mh-history-w4.md` (departure 5) and the Task 5a manifest `run-state-quo-execute-t1.f9p.mh.md`.
- **Three questions:** twice in one Epic, loud (recorded as a departure), and the agents "recovered" by working around a rule. Under CLAUDE.md, an agent improvising around a rule is a signal that the rule costs more than it buys.

### Constraints the design must keep

- **Why the rule exists:** paraphrasing corrupts identifiers (`references/rationale.md`). A file the orchestrator writes from the ticket text verbatim keeps that guarantee.
- **Why b.86z chose to embed** (`~/.quorum-overseer/b86z-checkpoint-1.md`, "Embed or name?"):
  - the Doc Writer has no shell, so it can't read a ticket it is only told about;
  - neutrality: implementers reading tickets themselves would each need the bees CLI;
  - resumed implementers don't get the section again.

  A ticket pointer fails the first two. A scratch file path passes both: every role has `Read`, and §5 already passes the compromise tracker "the path, never the contents".
- **Staleness:** an Approve at the Analyst gate rewrites the ticket's `## Design revision (Analyst)`. Any per-Task file must stay current with the ticket.
- **Context bounds:** the orchestrator writes the file once, which costs the same tokens once. What's saved is the repeat across dispatches.

### Process

1. **Measure first.** From Epic 3 and Epic 4's manifests and ledgers, find how much of an orchestrator's context per Task goes to repeated ticket text, against its total. Is it a real share of what drives orchestrators to the 675k bound?
2. **If it's material,** a hand-edit batch: inventory-anchored, both bodies' §5, mirror map, cold reviews. Process change, so tried on a code repo first.
3. **If it isn't material,** close the ticket with the numbers, and tell live_edit to keep the bodies verbatim.

