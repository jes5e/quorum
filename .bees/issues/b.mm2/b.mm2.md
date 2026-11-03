---
id: b.mm2
type: bee
title: A run's decider can hand its runs to a named successor, so a decider handoff needs no session renaming
status: open
created_at: '2026-11-03T11:43:32.471308'
schema_version: '0.1'
reference_materials: null
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

