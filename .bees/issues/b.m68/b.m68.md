---
id: b.m68
type: bee
title: 'No customer doc change by default: planning and doc roles stop treating a customer-doc update as the expected result of a change'
status: open
created_at: '2026-11-05T11:02:24.159438'
schema_version: '0.1'
reference_materials: null
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

