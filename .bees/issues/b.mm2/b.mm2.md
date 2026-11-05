---
id: b.mm2
type: bee
title: A run's decider can hand its runs to a named successor, so a decider handoff needs no session renaming
parent: null
reference_materials: null
created_at: '2026-11-03T11:43:32.471308'
status: done
schema_version: '0.1'
guid: mm21fpup7tuo8xyb5jp2uur7o284esgf
---

## Description

A run launched with `--decider "<name>"` fixes its decider at launch (`**Decider:**` in the run-state manifest) and sends every later question to that name. Nothing lets the decider hand its runs to a successor. When the decider session fills up and hands off to a fresh one, the new session must end up with the old name, or every run falls back to asking the operator.

Today that costs the operator a manual dance at every decider handoff (live_edit, about every few days): open another terminal, resume the old session there, start the successor in the original terminal, rename both, have them interrogate each other, close the old one. The renaming exists only to keep the name. Automating it would need Claude Code-specific session-rename mechanics, which runs against the harness-independence principle (CLAUDE.md `## How skill prose is written`).

## Expected behavior

A run's current decider can name a successor, and the run switches to it:
- **Only the current decider can do it.** Accept the change only from a message whose sender is the session `**Decider:**` names. Otherwise any session could take over a run's questions.
- **The successor must be live.** Check it the way the launch check does. If it isn't there, keep the current decider and say so to it.
- **Nothing in flight is lost.** A delegated gate still open goes to the successor, with the same gate file. The successor gets the introduction the reference defines.
- **It survives compactions and resumes.** The new name is recorded in `**Decider:**`, so a compaction, and a resume command the run prints, use it.
- **Every skill that takes `--decider` honours it:** `/quo-execute`, `/quo-fix-issue`, `/quo-breakdown-epic` and `/quo-plan`, plus `/quo-file-issue` inline under a caller's delegation. The shared carrier is `skills/quo-execute/references/delegated-gates.md`.

The decider side (a decider telling its runs the successor's name) is the operator's own process, outside quorum. The README's decider section should say a decider can hand off this way.

## Notes for the design

- This is a new feature's contract (the message shape and the switch condition), so the evidence bar for kind-5 rules doesn't apply. The need is the operator's, recorded above. Keep it small: the natural home is one short section of the delegated-gates reference, plus whatever each skill's `**Decider:**` description needs so the field may change mid-run.
- **Reconcile with existing rules:**
  - fix-issue §2: "`**Decider:**` alone comes from the invocation, as at every launch";
  - quo-plan: "set from this invocation's `--decider` on a fresh manifest and on Resume";
  - the reference's `## The answer` (only a reply from the decider counts) and `## Fallback`.

  A resume in a fresh session still takes `--decider` from its invocation, and the printed resume command names the current decider.
- **Don't add SendMessage-only machinery beyond what the reference already uses.** A file-only decider channel is parked until quorum works with Codex (overseer note); this change must not make that harder.
- **No ticket-system coupling.** Quorum will need to support trackers other than bees.

## Process

A hand-edit batch (CLAUDE.md `## When editing skills` and `## Working on the orchestrator skills`), one cold review under the exit rule, and the manifest lead statements mirrored where touched. The check is the operator's next live_edit decider handoff, done with this in place and without renaming.
## Closed (2026-11-04)

Merged at `7aa5e44`, a fast-forward of `main` from `ef9f0aa`, not pushed. Hand edits on branch `bmm2-decider-successor` (Worker 1).

**What changed:**
- The delegated-gates reference gains `## A successor`, two sentences: "The decider can hand the run to another session by telling it so. Record that session in `**Decider:**`, send it the introduction, and send it any question still waiting; from then on it is the decider."
- The introduction's line 2 no longer says the operator named the decider. A new last line reads "To hand this run to another session, tell the sender its name."
- `/quo-execute`'s resume command now carries `--decider "<name>"` when `**Decider:**` names one. The guard, Mode 1 and abort stops print it, as `/quo-fix-issue`'s already did. This was a pre-existing gap: a fresh-session execute resume dropped its decider.
- README, `docs/prd.md`, `docs/sdd.md` and a REWRITE-BRIEF amendment follow.

Net shipped prose: +67.

**How it got small.** The first version (three cold rounds, +173) carried:
- a fixed handoff line and a fixed confirmation line;
- a live check on the successor;
- a no-reply rule for non-deciders;
- "the handoff message answers no gate";
- a clause in each skill.

The operator called it solving for predicted failures. The overseer agreed: two of those additions were its own, and the rest were reviewer predictions accepted as gaps between two agents. The new-feature-contract exemption had been stretched to cover edge-case handling. The cut keeps only the contract the ticket needs, because the agents work out the rest. The one failure that matters, a successor that isn't there, is caught by the existing `## Fallback`: the next send fails and the operator is asked. The overseer traced the four cases against the short version (handoff with a gate open, dead successor, non-decider sender, fresh-session resume) and ran `Full test` (601 passed), with no further cold round.

**Validation:** none dedicated. The check is the operator's next live_edit decider handoff, done without renaming:
- every run switches;
- a waiting question reaches the successor;
- the resume commands printed afterward name the successor.

**Recorded:**
- fix-issue's run-start print of the resume command comes before any switch, so it matters only after an unclean end, and fails loud;
- a stale `docs/sdd.md` sentence about execute's Analyst-gate compaction exception predates this change and is owed to this repo's doc cleanup (b.7qb).
