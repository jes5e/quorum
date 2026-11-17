---
id: b.mfz
type: bee
title: Measure the orchestrator context spent repeating ticket bodies per Task; if material, relay shared bodies by a per-Task scratch file
parent: null
reference_materials: null
created_at: '2026-11-16T09:46:33.013886'
status: done
schema_version: '0.1'
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

## Closed (2026-11-17)

Merged by fast-forward from `9859fce` to `2cb0587`, with the operator's go: "ok" to start, "yes" to widen the scope, "yes" at Checkpoint 1, then "merge".

**Commits:**
- `1abd835`: the draft;
- `13b55f8`: cold round 1;
- `2cb0587`: the SDD carrier for round 1's F4.

The work was Worker 2's. Its checkpoints are `~/.quorum-overseer/bmfz-checkpoint-1.md` (the measurement) through `-3.md`. Full test passes on `main` (619), run by the overseer, who also read the full diff, the helper included. CLAUDE.md's repo-layout list gained the helper, added by the overseer with the operator's yes. The CLAUDE.md cap went 4,743 → 4,750 for that clause.

**Net shipped: +61 words** in `skills/quo-execute/SKILL.md` (cap 11,889), plus `skills/quo-execute/scripts/ticket_bodies.py` and its tests.

### Measurement

- **Bytes per token.** Ticket text runs about 2.6 bytes per token, not 4.
- **The cost of pasting.** An orchestrator pays about twice each pasted prompt, once to read it and once to emit it. Lane M's 252 KB Engineer dispatch was about 97k tokens; read plus emit came to about 19 of its 27 points.
- **The share.** Across Epic 4's Tasks, repeated ticket text was 11–27% of the orchestrator's per-Task context counting emits alone, and up to 55% when each paste was read first. Enough to change how many sessions a Task needs.
- **Where Task 7's five revisions came from.** Two were written in by measure Tasks under the Analyst-revision heading. Task 7's own Approves appended rather than replaced, because replacing would have deleted those decisions.
- **Pointer evidence.** The one claimed "pointer caused a miss" was two reviewers judging the same line differently, not a read failure. So no read confirmation.

### What landed

- **E1 (execute §5).** Each implementer gets the Task body, its role's Subtask bodies and the Epic's `## Epic-wide contracts` as a file, which `ticket_bodies.py` writes just before each fresh dispatch. The orchestrator passes the path, and the implementer reads the whole file first.
- **E2 (execute §6, Approve).** A decision for another Task is written into that Task's body text, not as a revision, so each ticket holds one revision, its own.
- **The helper.** It copies bytes straight from the ticket store and exits 2 with one line on failure. Its `fetch` function is the one adapter to replace for another tracker. `CONTRACT_SURFACES` lists it as a reader of `## Epic-wide contracts`.

### Follow-ups noted, for later triage

- **The directive arrives twice.** An Engineer gets the approved revision in its bodies file and again under `## Authoritative design directive`. That paste is now the largest remaining one, and removing it touches a heading `agents/engineer.md` keys on.
- **A stale sentence in execute §5:** "Writers receive the revision's `## Blast radius` and `## Design decisions for writers` only". It has been false since revisions moved into the Task body.

### Watch (this is the code-repo trial)

- The next live_edit fresh implementer dispatches cost the orchestrator a few points, not about 27.
- Implementers act on the file's text.
- No revision piles up across Tasks.
- live_edit's own reviewer and PM over-relay (other Epics' contracts, past revisions' blocks) is theirs to drop. After Task 7's revisions were merged, its code-review prompt was still 124 KB.
