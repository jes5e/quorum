---
id: b.bix
type: bee
title: Review loops have no termination on nit-severity findings; nits batch into one final implementer pass and never reopen a lane
tags:
- process
- quo-fix-issue
- quo-execute
- review-loop
parent: null
reference_materials: null
created_at: '2026-09-08T23:02:38.259753'
status: done
schema_version: '0.1'
guid: bix6efnkycyye24kzmvqwzqbwbsp4p19
---

## Description

The review loops in `/quo-fix-issue` and `/quo-execute` (Phase A's Engineer → Code Reviewer loop, each Phase C writer → reviewer pair, and the execute-mode mirrors) close only when a cold review returns clean or every finding has been routed. In practice orchestrators read that as "re-review the whole diff after every implementer round, at every severity," so a `nit`-severity wording finding triggers a full writer round plus a full cold review, and each fresh cold pass finds the next wording nit. The loop has no natural end on `nit`s.

## Reference runs

- `/quo-fix-issue b.nn8` (this repo, 2026-09-08): 15 test-review rounds, of which rounds 9–15 and 17 were comment and docstring accuracy only; none changed an assertion.
- `/quo-fix-issue b.q3f` (this repo, 2026-09-08): 13 test-review rounds; every finding after round 4 was "one more clause unpinned", none a test defect.
- A `/quo-fix-issue` run on a Python service (2026-09-08): five of eight code-review rounds were doc-comment wording; the orchestrator reported "the workflow tells me to re-review after every engineer round."

The reviewer skills already say "be selective — if you keep reporting trivial items each pass, you create an infinite loop," and the orchestrators already permit recording a finding as ignored feedback. Neither has held: the default an orchestrator lands on is fix-then-re-review.

## Expected behavior

A termination rule, stated once in `### Orchestrator discipline: routing review findings` in both orchestrators and referenced from the Phase A and Phase C loop text:

- A lane's loop is held open only by `blocker`- and `suggestion`-severity findings and closes when none remains unrouted.
- `nit`-severity findings never reopen a lane on their own. When a `blocker` or `suggestion` in the same return forces another implementer round, nits ride along in it. When nothing above `nit` remains, the nits are applied in one final implementer pass for that lane with no further reviewer round, and each is listed under the unit summary's **Ignored Review Feedback** field annotated `applied without re-review`.
- A `nit` whose chosen fix path would fire a gate still routes through the table.

The three review skills' selectivity paragraphs gain one sentence: tag an item `nit` only when it would not, on its own, justify another review round.

## Why this loses no coverage

Nits are still reported and still fixed. The cold pass that raised a nit already read the text it corrects, and the Section 8 post-completion review reads the whole diff, nit fixes included. What is removed is the dedicated cold round whose only job was to bless a wording fix.

## Files

`skills/quo-fix-issue/SKILL.md`, `skills/quo-execute/SKILL.md`, `skills/quo-engineer-review/SKILL.md`, `skills/quo-test-writer-review/SKILL.md`, `skills/quo-doc-writer-review/SKILL.md`.

## Process note

Landed as a hand edit on main with one cold code review, not through a `/quo-fix-issue` run: the orchestrator skills are over the size budget and the fix-issue loop on prose is the ratchet this rule exists to stop. Recorded here so the change is traceable and so the rule enters the consolidation inventory.

## Amendment (2026-09-08, from the cold review of the hand edit)

The first draft routed applied nits into **Ignored Review Feedback**. The cold `/quo-engineer-review` pass caught that this wedges the run: every bullet in that field maps to a `defer-*` task, and the deferral-hygiene gate then hard-stops until the user routes each through Fix / File / Encode, all three wrong for work already applied. It also found that `/quo-execute`'s `## Bee Execution Complete` block had no such field at its only Code Reviewer site. Shipped instead: applied nits are counted on the summary's **Reviews** line (`N nits applied without re-review`) at every scope, the Bee-level block gains a **Reviews** line, Phase B's "source already review-clean" rationale is qualified for a final nit-only pass, `/quo-execute`'s Section 5 feedback bullets gained the pointer `/quo-fix-issue`'s Phase A and Phase C already had, and the reviewer-side sentence defines `nit` by the item rather than by the reviewer's comfort so it does not create up-tag pressure.

## Amendment 2 (2026-09-08, from the second cold review)

The second pass found that the first amendment redefined `nit` by substance (wording, comments, formatting), contradicting the review skills' own orthogonality contract (a `nit` may need a `re-architect` fix) and the gates' `suggestion`/`nit` choice sets, and that the rule conflicted with part (g)'s Engineer → code review → writer ordering for a source-changing final pass. Shipped instead: the bound is the reviewer's own depth tag, not a redefinition of severity — only a `nit` whose chosen fix path is a `trivial-tweak` skips the round; any deeper `nit` holds the lane open like a `suggestion`. Part (g) states the one elision (that final pass has no code-review rung; the affected writer follows the Engineer). The referencing clauses name the lane rather than the loop, `/quo-fix-issue`'s Section 5 note gained the pointer its `/quo-execute` twin had, the per-Task site's lever is named (no PM re-dispatch), and the Bee-level **Reviews** line's segments are uniform.

## Amendment 3 (2026-09-08, from the third cold review)

Two blockers. (1) The rule's backstop claim ("the post-completion review reads the whole diff") was false at `/quo-execute`'s Bee-level site: Section 6's sweep diffed `<pre-bee-sha>..HEAD`, but Bee-level review-round edits are uncommitted at that point, so no Bee-level fix of any severity reached the sweep. Pre-existing gap; closed here by widening the sweep's dispatch-prompt scope to combine the commit range with `git diff HEAD`, matching `/quo-engineer-review`'s own both-views rule. (2) "closes when none remains unrouted" could be read as closing a lane on a blocker that had merely been dispatched (row 6 is a routing); the closure test now names terminal dispositions and says a dispatch alone does not settle a finding. Also: "chosen" inserted in all seven restatements so the bound keys on the orchestrator's pick rather than any offered path; the in-PM clause covers all of the PM's in-flight review passes; the applied-nit count is declared conversation-carried and renders as unavailable after compaction rather than being guessed; the per-Task commit step's "the PM confirmed" premise is qualified for a final nit pass; the Phase C re-entry sentence carries the part (g) elision inline.

## Amendment 4 (2026-09-08, from the fourth cold review)

No blockers. The widened Section 6 sweep scope is now `git diff <pre-bee-sha>` (the net of committed and uncommitted change in one command) plus any untracked file the working tree holds, since neither diff view shows a new file a Bee-level round created. The reviewer-side sentence guards both directions: demoting a `suggestion` to `nit` to close a lane is named as illegitimate alongside promoting to buy a round. Part (g)'s movement-report paragraph in `/quo-execute` carries the elision qualifier. The SDD entry's enumeration of referencing sites was completed.

## Amendment 5 (2026-09-08, from the fifth cold review)

One blocker: "answered by the user at a gate" as a settling disposition would have let a gate answer of `Fix properly now` (or a path pick at gate (d)) close a lane with the fix never re-reviewed. The closure test now names only dispositions under which no fix lands (tracker acceptance, `defer-*` record, or a gate answer of Accept / Defer / Cancel), and says a dispatch settles nothing, ungated or gate-chosen, until a cold pass has read its result. Also: untracked files enumerated with `git ls-files --others --exclude-standard` (porcelain collapses new directories); the sweep gloss no longer claims "since the Bee began" and tells the reviewer to name pre-existing dirty-tree changes as such, with the "stay focused" instruction pointed at the stated scope; the per-Task commit qualification names whichever implementer ran the final pass and its own lane's rungs; Sections 9 and 10 stop asserting all work is committed and name the uncommitted Bee-level edits (pre-existing gap the widened scope made explicit); the three **Reviews** templates carry the post-compaction placeholder; `/quo-fix-issue`'s per-Issue **Reviews** line gains the Test review slot.

## Amendment 6 (2026-09-09, from the sixth cold review)

One blocker: `/quo-fix-issue`'s pre-existing Phase A exit clause "or gated to the user" contradicted the new closure test, since a gate answer of `Fix properly now` dispatches a fix; the clause now reads "gated to the user and settled by that gate's answer", with the dispatch caveat. Two suggestions: `Defer to follow-up Issue` ships a soft fix or narrowing, so it settles a finding only when nothing ships against it this round, and the closure test says so; the Section 9 summary's uncommitted-edits sentence now derives from `git status --porcelain` at that moment rather than from a proxy about whether Bee-level rounds ran.

## Amendment 7 (2026-09-09, from the seventh cold review)

One blocker: a `trivial-tweak` nit that fires a gate (rows 2–4) and receives `Fix properly now` ships a fix deeper than the tag the closure test measured, and as written the lane still closed with part (g)'s rung elided — new machinery could ship unreviewed under a `nit` tag. The bound now keys on what ships: a gate answer that substitutes anything other than the enumerated `trivial-tweak` path makes the finding lane-holding again and the elision does not apply; the four restatements say "shipped as such". Also: the post-completion reviewer is told it cannot see the run-start tree and must state pre-existing attribution as an inference with its basis; Section 10's clean-tree caveat moved to the lead sentence so it covers all three isolation strategies; the per-Task commit rationale names the Doc Writer as owing no rung.

Observation for the consolidation inventory, not fixed here (adds a commit step): Section 8's `bees update-ticket --status done` writes the Plans hive after the last commit site, so with an in-repo hive the Section 9 `git status --porcelain` check will name `.bees/` as uncommitted on essentially every run.

## Amendment 8 (2026-09-09, from the eighth cold review — no blockers)

The post-completion reviewer's attribution heuristic said an unticketed change is "likely pre-existing", which would mislabel Bee-level review-round fixes — the class the widened sweep exists to reach; it now says "likely either pre-existing or an unticketed in-run edit (a Bee-level review-round fix, or a formatter pass)". The Phase A bullet's "third way … those two exit conditions" ordinal, made false by the added closure route, now reads "further way … those exit conditions".

## Amendment 9 (2026-09-09, from the ninth cold review)

One blocker, and the most important finding of the series: the three review skills' routing trailer ("dispatch a fresh Agent and re-invoke this skill") is declared authoritative by both orchestrators over their own prose, and the new rule lived only in that demoted prose — so a literal orchestrator would never have fired it. The trailer's dispatch-and-re-invoke conjunct now carries the carve-out ("unless every finding is a `nit` whose chosen fix path is a `trivial-tweak`, in which case apply them in one implementer pass and do not re-invoke"), identically in all three skills. Two consistency gaps: `/quo-execute`'s movement-report receiver rung carries the part (g) elision qualifier; Sections 9 and 10 hedge the `git status --porcelain` list as possibly including changes that predate the run and tell the user to commit the Bee's own.

## Amendment 10 (2026-09-09, tenth cold review — verdict sound)

One `nit` with a `trivial-tweak` path: a stale clause in `/quo-execute` Section 6 claimed every Epic is "done and committed" by then, contradicting the same section's new statement that Bee-level review-round edits are uncommitted; it now reads "every per-Task commit has landed". Applied in one pass with no further review round, per the rule this Issue ships — the first exercise of it. Landed on main.

Ten cold reviews in total. Real defects found by round: 1 (deferral-gate wedge), 2 (severity/depth contradiction; part (g) conflict), 3 (Bee-level sweep gap, pre-existing; dispatch-as-settled), 4 (untracked files; down-tag guard), 5 (gate-answer-as-settled), 6 (Phase A exit clause; Defer ships a fix), 7 (gate substituting a deeper fix), 8 (attribution heuristic), 9 (rule unreachable because the trailer is authoritative), 10 (nit). Recorded as evidence for the consolidation inventory: every one was an interaction with text hundreds of lines from the edit site.
