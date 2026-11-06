---
id: b.m68
type: bee
title: 'No customer doc change by default: planning and doc roles stop treating a customer-doc update as the expected result of a change'
parent: null
reference_materials: null
created_at: '2026-11-05T11:02:24.159438'
status: done
schema_version: '0.1'
guid: m683xwbg58sq962v7re6t9cpt46pwdk6
---

## Description

Quorum's planning and doc roles treat a customer-doc update as the expected result of most changes. The operator's standard is the opposite: customer doc changes should be somewhat rare, and agents are treating them as the standard case. Four lines push that way:
1. **`/quo-plan`, the Epic decomposition rules (~106):** "an Epic that changes config, behavior, or deployment carries its customer-facing doc update". Almost every Epic qualifies.
2. **`agents/doc-writer.md` job 1:** "Add the customer text its reader now needs". Added in b.pca so new behavior gets documented, it reads as an instruction to find something to add.
3. **The customer-text test,** carried verbatim by the Doc Writer and `/quo-doc-writer-review` and pinned: customer text "says only what its reader would act on or expect". "Or expect" covers almost any behavior change.
4. **The PRD/SDD line,** carried verbatim and pinned: "User-visible limitations go in the customer-facing docs and the SDD, and in the PRD only as non-goals." This pulls known bugs, rare failure modes and unfinished features into customer docs.

`/quo-breakdown-epic` gives every code-changing Task a doc-writer Subtask, but the Doc Writer decides whether any doc changes (often only the SDD), so that's neutral and not in scope.

## Evidence (live_edit, 2026-11-04/05)

- The operator: "it should be somewhat rare to be updating the customer docs as we do work … agents are thinking that it's the standard case".
- Customer pages kept growing. In one day the troubleshooting and monitoring pages each had their word ceilings raised twice. The project's guide now says "no customer doc change by default", and quorum's lines above push against it.
- The live_edit planner's report, item 6, asks to flip the default: Doc Writers start from "no customer doc change", and add one only when an operator or client developer must do or plan around something new in normal use. Known bugs, guessed or rare failure modes, and unfinished features go to tickets and the SDD, never to customer docs.

**Three questions:** every lane; silent (nothing flags growth, and reviews passed it); not recovered. Earned. It's also a gap between the plan and breakdown side and the project guide.

## Operator decision (2026-11-05)

Make "no customer doc change" quorum's default for every project. A project that wants more customer text says so in its doc writing guide, which already governs customer text (b.pca).

## Proposed change (restructure; target net ≈ 0)

- **`/quo-plan` ~106:** delete the "carries its customer-facing doc update" clause, keeping "documentation folds into the Epic whose work it covers".
- **Doc Writer job 1:** replace the add sentence with a default-no form, e.g. "Add customer text only when a reader must now do or plan around something new; most changes need none."
- **The customer-text test (both carriers and the pin):** "would act on or expect" becomes "must do or plan around", keeping "omits nothing they need to act".
- **The PRD/SDD line (both carriers and the pin):** narrow the limitations sentence to limitations users meet in normal use; known bugs, rare failures and unfinished features go to tickets and the SDD.
- **Readers:**
  - `/quo-setup`'s doc-guide brief, if it implies customer updates are routine;
  - README's role rows;
  - `docs/sdd.md`'s doc-role entries.

## Process

One small hand-edit batch and one cold review under the exit rule, with no dedicated validation. The next live_edit runs after a container rebuild are the check: customer pages stop growing on routine fixes, and the Doc Writer's return names the doc changes it judged unneeded.
## Closed (2026-11-06)

Merged at `cab25d4`, a fast-forward of `main` from `aeb8c01`, not pushed. Hand edits on branch `bm68-customer-default` (Worker 1).

**What changed.** The customer-text test is now the one place that decides whether customer text is written: "It says only what its reader must do or plan around in normal use, not known bugs or unfinished features, …". The test changed in both carriers, the pin and the post-completion PHASE 6. The other lines that made the same decision now point to it or are gone:
- the Doc Writer's job 1 now says "Add customer text only where the customer-text test asks for it (most changes need none)";
- the PRD/SDD line's limitations sentence is now "A limitation is the PRD's only as a non-goal";
- `/quo-plan`'s "carries its customer-facing doc update" and `/quo-plan-from-specs`' matching checklist line are deleted;
- `/quo-setup` now says customer docs are kept true.

Net shipped prose is −25.

**Review.** Four cold rounds. From round 2 on, each behavior finding came from the previous round's fix: several sentences each decided customer placement. The class closed once the test became the one home (the worker's lesson, saved as memory `feedback_fix_the_class_at_round_one`). Round 4's fix restored the ticket's own "in normal use". The overseer waived round 5 on its own trace of the four role-plays against the final text:
- an internal retry change gets no text;
- a required setting is added, and its absence is flagged;
- a known bug goes to a ticket, plus the SDD if it passes the SDD test;
- a hard limit met in normal use goes in the customer docs and the SDD, and in the PRD only as a non-goal.

The overseer read the diff and ran `Full test` (601 passed).

**Validation:** none dedicated. It takes effect in live_edit after the next container rebuild. The check: routine fixes stop adding customer text, and customer pages stop growing.
