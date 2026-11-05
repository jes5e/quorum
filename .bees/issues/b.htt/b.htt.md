---
id: b.htt
type: bee
title: Doc review checks customer text per statement; deferral-encode scratch file gets a unique name
parent: null
reference_materials: null
created_at: '2026-11-05T10:46:35.471734'
status: done
schema_version: '0.1'
guid: httmtmt298re4rpm2bbr6k38d4gu5zqm
---

## Description

Two small defects, both seen in live_edit runs on 2026-11-04/05 (evidence in container scratch, mirrored on the host at `~/.quorum-scratch`).

### 1. The doc review doesn't apply the customer-text test sentence by sentence

`skills/quo-doc-writer-review/SKILL.md` step 3 checks the SDD and PRD per statement ("Does every statement the Doc Writer added or edited in the SDD pass the SDD test…"). It checks customer text only in bulk: "Does the customer text in scope pass the customer-text test?".

**Evidence.** In two lanes the Doc Reviewer passed customer sentences that the project guide's "no customer change by default" standard rejects. The planner's push-time cold audit caught them:
- docs-simplify lane (`doc-review-docsimplify-r1.md`):
  - monitoring.md "each line names up to 10 sessions in session_ids_sample", a sampling detail;
  - "the service restores it, then deletes it", internal mechanism.
- token-docs lane (`doc-review-q3x-r1.md`, `-r2.md`, `-r3.md`):
  - authentication.md "a trial call, every 5 to 7.5 seconds", timing that reads a configurable value as fixed;
  - a touched `values.yaml` paragraph quoting `AuthError::InvalidResponse(...)`, an internal type name.

The reviews checked truth, and even checked the guide's own rules for consistency, but never put each added sentence to the reader test. The one lane that did (`doc-review-epic1-t6-r1.md`, "it says which histogram absorbs which internal wait, which is mechanism") did so only because a CI word-budget failure forced it to look for cuts.

**Three questions:** four sentences in two lanes; silent; not recovered by quorum, since the planner caught them. Earned.

**Fix (a restructure, not a new rule):** make the customer bullet per statement, parallel to the SDD bullet: every customer statement the change added or edited passes the customer-text test. Say "the change", not "the Doc Writer", because customer text in source (a `values.yaml` comment, a proto comment) is in scope since b.pca. Keep it to a reword of the existing bullet.

**Declined:** project-specific flags (internal type names, numbers describing sampling or timing). Those belong in the project's guide, which the test already makes govern.

### 2. The deferral-encode scratch file has a deterministic name

`/quo-execute` §9 (~296) and `/quo-fix-issue` §9 (~321), the `Encode in existing ticket` bullet, write the revised body to `/tmp/.quorum/bees-body-<defer-N>.md`, e.g. `bees-body-defer-3.md`. The scratch-file convention (CLAUDE.md `## Scratch-file convention`) requires collision-resistant names when concurrency is possible, except for the three documented exceptions, and this isn't one of them.

**Evidence:** a live_edit orchestrator encoding a deferral picked up `/tmp/.quorum/bees-body-defer-20.md`, left by another run (an 866-line SDD draft), and appended it to an Epic ticket. It noticed and reverted before committing. Several runs share one scratch directory, so this recurs.

**Fix:** add the random `<short-suffix>`, e.g. `bees-body-<defer-N>-<short-suffix>.md`. This is a Tier-1 mirrored edit in both bodies. `/quo-file-issue` and `/quo-plan-from-specs` already use `bees-body-<short-suffix>`.

## Process

One small hand-edit batch and one cold review under the exit rule, with no dedicated validation; the next live_edit doc stage and deferral encode are the check. Net prose should be near zero.

## Not quorum's (recorded)

The same report noted three more items:
- **bees hives aren't visible from a git worktree,** so an orchestrator hand-wrote ticket files. That's a bees matter, reported upstream; live_edit files tickets from the main checkout meanwhile.
- **A Claude Code "Security Test Removal" warning was a false positive.** Once, loud, recovered; no change.
- **Mid-Task handoffs at clean sub-steps worked four times with no rule written for them.** Evidence against adding one.
## Closed (2026-11-05)

Merged at `d4eb046`, a fast-forward of `main` from `ede7cb1`, not pushed. Hand edits on branch `bhtt-small-fixes` (Worker 1): a draft checkpoint, then one cold round with no behavior findings and one wording nit, so the lane closed.

**What changed:**
- `/quo-doc-writer-review` step 3: "Does the customer text in scope pass the customer-text test?" became "Does every customer-text statement the change added or edited pass the customer-text test?", parallel to the SDD bullet. The Mission says "what the change added or edited" in place of "the Doc Writer". "The change" covers customer text the Engineer writes in source.
- `/quo-execute` and `/quo-fix-issue` §9 `Encode in existing ticket`: the scratch file is `bees-body-<short-suffix>.md`, its suffix random because runs share the directory. This matches `/quo-file-issue` and `/quo-plan-from-specs`. The mirror pin was updated.
- Readers: a `docs/sdd.md` sentence on the b.pca entry, and a REWRITE-BRIEF amendment of 2026-11-05.
- Net shipped prose +14.

**Role-play (cold round):**
- (a) The docs-simplify sampling sentence is flagged under a guide that rejects sampling detail.
- (b) A changed `values.yaml` comment quoting an internal type is flagged and routed to the Engineer.
- (c) Two concurrent deferral encodes write different scratch files.

The overseer read the diff and ran `Full test` (601 passed).

**Validation:** none dedicated. It takes effect in live_edit after the next container rebuild. The checks:
- the next doc stages: a customer sentence that fails the guide's default-no rule is flagged by the lane's Doc Reviewer, not first by the planner's audit;
- the next deferral encode uses a unique scratch file.

**Upstream:** the bees worktree item from the same report is https://github.com/gabemahoney/bees/issues/30.
