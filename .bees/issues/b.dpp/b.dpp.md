---
id: b.dpp
type: bee
title: '/quo-fix-issue: a new session cannot resume an interrupted run, and no context guard runs before the post-completion review'
parent: null
reference_materials: null
created_at: '2026-09-28T23:38:21.366539'
status: done
schema_version: '0.1'
guid: dppckhp3n2zyq6k4sp7ijfsea12yvohg
---

## Description

`/quo-fix-issue` cannot pick up an interrupted run in a new session, and it runs no context guard before its post-completion review. So a batch that fills its context late can only be finished by resuming the same conversation, or by a human-written prompt that tells a fresh session to skip run start.

## Current behavior

- **Run start resets the run.** It validates the manifest, then rewrites every field from the new run's own state and empties `## Lanes`, `## Obligations`, `## Rounds`, and `## Open gate`. It also drops every Issue that is no longer `open`, and exits with an error when none remains. A fresh session therefore cannot continue:
  - a mid-Issue run: its open `defer-*` obligations and lanes are lost;
  - a run in its post-completion review: every Issue is `done`, so the run exits.
- **The context guard runs only between Issues** ("never … on a batch exhausted"). `/quo-execute` runs its guard before each Epic-boundary review too. A long post-completion fix round can fill the context with no clean stop.

## Evidence (live_edit, delegated-gates validation run cvei2, 2026-09-28/29)

- **A machine restart mid-b.e1h.** It was survived only because the same conversation was resumed (`claude --resume`). A re-run would have emptied `## Obligations`, which held two open deferrals (defer-7 and defer-8).
- **A context-full stop during the post-completion "Fix in this session" round,** after both Issues were done. The run could only be continued because the decider wrote a recovery plan (`postcomp-plan-cvei2.md`) and a new-session prompt, and the overseer added "skip Run start; don't rewrite the manifest".
- **Three questions:** it happened once in this run, twice counting the restart. It announces itself (the run stops, and a re-run exits or loses state). The agent did not recover unaided: it needed operator and decider help. A state carrier and a guard earn the change.

## Expected behavior

- **A new session can continue an interrupted fix-issue run from its manifest:** mid-Issue, or in the post-completion review. It keeps open obligations, closes killed lanes per the Killed-lane rule, re-enters at the recorded phase, and never re-runs finished Issues. `/quo-execute`'s resume (keep the tracker and count when its Bee has an `in_progress` Epic) is the precedent to borrow from.
- **The context guard also runs before the post-completion review,** as execute's does, with a resume command that continues into that review.
- **Delegated gates (b.d7t):** a resumed run re-sends the decider introduction only when the decider may not have seen it (a different decider, or one restarted fresh rather than resumed). One sentence at most.

## Suggested fix

Hand edits plus one cold review per CLAUDE.md `## Working on the orchestrator skills`. Start with a design checkpoint that defines:
- the resume condition's inputs (the manifest's `**Unit scope:**`, `**Progress:**`, `**Next unit:**`, and the Issues' statuses);
- where a fresh session re-enters;
- which fields survive.

Enumerate readers: fix-issue §2 and §4 run start, §8's guard and checkpoint, §11, the context-guard reference, README, and tests. The mirror with execute is Tier 2 at most: execute's resume keys on its Bee and differs. Keep it small, since the evidence is two events in one run. Validate on a real fix-issue batch that is stopped on purpose mid-Issue and before its post-completion review.

## Closed (2026-09-29)

Merged to main by fast-forward, head `0c52efb` (commits `3a66ec0`..`0c52efb`), not pushed.

**What changed:**
- Run start resumes a manifest that records the invocation's batch and whose `**Next unit:**` is not `none`. It keeps every field and section, skips run-start steps 3–6, recovers as after a compaction, treats `open` lanes as killed, and re-enters at `**Next unit:**`. Each Issue step 7 takes re-enters its ladder from its lane rows.
- `**Next unit:**` gains `post-completion review`, which §11 rewrites to `none` when complete.
- One resume command, `/quo-fix-issue <batch-ids>` (plus `--decider`), is printed at the manifest write and at every stop.
- The guard also runs before the post-completion review, in every mode.
- A single-mode run checks its Issue's dependencies before the manifest write.
- A resumed session re-fires an unanswered delegated gate.
- §3 gains one goal sentence: a review whose findings are no longer readable is dispatched again.
- Size: fix-issue +169 words; context-guard.md lost a bullet.

**Operator decisions (2026-09-29):**
1. An aborted-Issue STOP resumes after the aborted Issue.
2. The guard runs before the review in single mode too.
3. `**Decider:**` comes from the resume invocation, so a fresh-session resume re-introduces the run. This deviates from the ticket's "introduce only when the decider may not have seen it".

The overseer kept the delegated-gate re-send at Checkpoint 2.

**Review:** four cold rounds with no blockers; findings are in the commit messages. Round 5 was waived: round 4's one-sentence fix was traced by the overseer across four cases (mid-Issue resume; a skip with the next Issue in flight; `post-completion review`; mid post-completion fix round).

**Recorded, not changed:**
- the directory to resume from (a prediction);
- a skipped Issue whose dependency closes between a crash and the resume (stacked predictions);
- `docs/sdd.md:701`'s historical wording;
- a resume straight into §11 does not re-run the guard (a fresh session).

**Validation deferred (operator, 2026-09-29).** The dedicated two-stop test (the runbook in `~/.quorum-overseer/bdpp-checkpoint-4.md`) waits until the operator has time. Until then, the check is the next real fix-issue run that stops early and is relaunched with its printed resume command.
## Check still open

Confirm on the first real resume:
- obligations, rounds, `**Proposal:**`, tracker, and review base are kept;
- open lanes are closed as killed and re-dispatched;
- no finished Issue is re-run;
- `post-completion review` routes to §11.
