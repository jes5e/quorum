---
name: quo-write-prd
description: Author or revise a PRD as a `t1=Doc` child titled `PRD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/quo-write-prd <spec-bee-id>`), or inline from `/quo-plan` via the Skill tool when initial specs are being authored.
argument-hint: "<spec-bee-id>"
---

Author the PRD of one feature as a child ticket of its Spec Bee: a `t1` child titled exactly `PRD` (case-sensitive), because downstream skills tell the PRD from the SDD by that title alone. Its body always carries the same twelve sections in the same order, because the agents that read it later have no access to the conversation that produced it.

## Preconditions

Hard-fail with `Run /quo-setup first.` plus a one-line reason when `bees list-hives` has no hive whose `normalized_name` is `specs`, or the target repo's CLAUDE.md has no `## Documentation Locations` section.

## Solo or inline

- **Inline** — another skill (canonically `/quo-plan`) invokes this one through the Skill tool with `args` in this shape:

  ```
  spec-bee-id: <spec-bee-id>
  distilled-scope: <path to the approved scope file>
  findings:
  <on a revise pass only: each finding line with the fix-path line picked for it, verbatim, and each change the user asked for as one line>
  ```

  The `args` shape, not how rich the conversation is, identifies the inline path: a solo run after a long discussion still owes the user its gate. Inline, the caller has already approved the scope and runs the reviews and gates itself, so fire no gate, leave the child `drafted`, and return:

  ```
  prd_ticket_id: <id>
  prd_status: drafted
  action: <created | updated>
  ```

- **Solo** — `/quo-write-prd <spec-bee-id>`, typically a revision after planning. Ask for a missing ID in prose. The solo run reviews its own draft and ends at one approval gate (Step 6).

## Steps

1. **Read the Spec Bee** with `bees show-ticket`. When it is missing or not in the `specs` hive, stop and say so; creating Spec Bees is `/quo-plan`'s job. Read the docs at the `Internal architecture docs (SDD)` and `Customer-facing docs` keys of `## Documentation Locations` when the feature touches existing behavior.
2. **Find the existing PRD.** Query the Spec Bee's children for one titled exactly `PRD`. None → you will create it. One → you will update it, so re-runs never duplicate it. On a solo run, keep a copy of the prior body and status until the user approves; on Cancel, put it back. More than one → stop and ask the user which is canonical.
3. **Gather the content.** Inline, read the scope file and treat any `findings:` lines as required fixes to the existing body. Solo, use the conversation when it already carries substantive scope, erring toward distilling because re-asking what the user settled costs them a repetition. Otherwise ask in prose for what the twelve sections need: the problem and who has it, success, exclusions, required behavior, failure modes, non-functional and UI needs, assumptions, open questions. Never invent content the sources do not support.
4. **Author the body** with these twelve sections, in this order, every one present. An empty section reads `none — <why>`, so a reader can tell "nothing here" from "forgotten":

   1. `## Problem Statement` — the problem, who has it, and why now.
   2. `## Goals` — measurable outcomes.
   3. `## Non-Goals / Out of Scope` — explicit exclusions.
   4. `## Functional Requirements` — what the system must do, in user-observable terms.
   5. `## Edge Cases and Error Handling` — failure modes and required responses.
   6. `## Non-Functional Requirements` — performance, security, availability, accessibility.
   7. `## UI/UX Requirements` — user-facing surface requirements.
   8. `## Acceptance Criteria` — objectively verifiable conditions for done.
   9. `## Assumptions`.
   10. `## Open Questions` — each with who should answer it.
   11. `## Background and rationale` — why the PRD looks this way.
   12. `## Decisions and rejected alternatives` — each decision with the alternatives weighed and why they lost.

   Sections 11 and 12 carry what the conversation settled, so downstream agents do not re-litigate it; after a real discussion they are rarely `none`. A PRD says what and why, never how: architecture, libraries, data structures, and API sequences belong in the SDD. Replace vague aspirations ("fast", "user-friendly") with measurable thresholds, or move them to `## Open Questions`.
5. **Write the ticket.** Put the body in a file. Every file this skill writes goes under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), creating the directory if absent, with a collision-resistant name, and is never deleted. Pass it with `--body-file`, because an inline body with a newline before `#` trips Claude Code's command-injection guard. With no PRD, create a `t1` child of the Spec Bee in the `specs` hive, titled `PRD`, status `drafted`. With one, replace its body and set it to `drafted`: a revised PRD is unapproved until its gate passes.
6. **Solo only: review and approve.**
   - Invoke `/quo-spec-review <spec-bee-id> --doc PRD` through the Skill tool.
   - Apply each finding whose smallest complete fix path is `trivial-tweak` yourself, rewriting the ticket body.
   - Then write the current body to a fresh body file and, in the same turn, call `AskUserQuestion` with the body's summary and the remaining findings. The file write in that turn is what keeps the gate from being described and left unasked.
   - Choices: **Approve** sets the PRD `ready`, and the report records any `blocker` approved over. **Revise** applies the remaining findings and the user's changes, then reviews again. **Cancel** puts the prior body and status back; a PRD this run created stays `drafted`. Mark **Revise** (Recommended) when a `blocker` is open.
7. **Finish.** Inline, return `prd_ticket_id`, `prd_status`, and `action`. Solo, report the Spec Bee, the PRD ID, whether it was created or updated, its status, and any findings approved over. The Spec Bee's own status belongs to the caller.
