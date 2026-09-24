---
name: quo-write-sdd
description: Author or revise an SDD as a `t1=Doc` child titled `SDD` under a Spec Bee in the Specs hive. Composable — runs solo for revisions (`/quo-write-sdd <spec-bee-id>`), or inline from `/quo-plan` via the Skill tool when initial specs are being authored.
argument-hint: "<spec-bee-id>"
---

Author the SDD (Software Design Document) of one feature as a child ticket of its Spec Bee: a `t1` child titled exactly `SDD` (case-sensitive), because downstream skills tell the SDD from the PRD by that title alone. Its body always carries the same seven sections in the same order, grounded in real codebase research, because the Engineer and reviewers who read it later have no access to the conversation that produced it.

## Preconditions

Hard-fail with `Run /quo-setup first.` plus a one-line reason when `bees list-hives` has no hive whose `normalized_name` is `specs`, or the target repo's CLAUDE.md has no `## Documentation Locations` section.

## Solo or inline

- **Inline** — another skill (canonically `/quo-plan`) invokes this one through the Skill tool with `args` in this shape:

  ```
  spec-bee-id: <spec-bee-id>
  distilled-scope: <path to the approved scope file>
  findings:
  <on a revise pass only: finding lines verbatim, and each change the user asked for as one line>
  ```

  The `args` shape, not how rich the conversation is, identifies the inline path: a solo run after a long discussion still owes the user its gate. Inline, the caller has already approved the scope and runs the reviews and gates itself, so fire no gate, leave the child `drafted`, and return:

  ```
  sdd_ticket_id: <id>
  sdd_status: drafted
  action: <created | updated>
  research_needed: <each RESEARCH NEEDED question, or none>
  ```

- **Solo** — `/quo-write-sdd <spec-bee-id>`, typically a revision after planning. Ask for a missing ID in prose. The solo run reviews its own draft and ends at one approval gate (Step 7).

## Steps

1. **Read the Spec Bee** with `bees show-ticket`. When it is missing or not in the `specs` hive, stop and say so; creating Spec Bees is `/quo-plan`'s job. Read its `PRD` child when there is one, since the design answers it.
2. **Find the existing SDD.** Query the Spec Bee's children for one titled exactly `SDD`. None → you will create it. One → you will update it, so re-runs never duplicate it. On a solo run, keep the prior body until the user approves; on Cancel, put it back. More than one → stop and ask the user which is canonical.
3. **Research the codebase.** The design must cite real modules, files, functions, and fixtures, never plausible guesses, and a planning conversation rarely names them. So on first authoring, dispatch an `Explore` agent with the feature scope and the docs at the `Internal architecture docs (SDD)`, `Customer-facing docs`, and `Engineering best practices` keys of `## Documentation Locations`. Ask it for:
   - the subsystems and modules the feature touches;
   - the conventions new code should follow;
   - the data models;
   - the test-fixture helpers;
   - the configuration involved.

   On a revise pass, research again only when a finding questions the grounding. Where research leaves a question open, write `RESEARCH NEEDED: <question>` inline at that spot rather than a confident-sounding sentence.
4. **Gather the rest.** Inline, read the scope file and treat any `findings:` lines as required fixes to the existing body. Solo, use the conversation when it already carries substantive design discussion, erring toward distilling because re-asking what the user settled costs them a repetition. Otherwise ask in prose for what research cannot supply: the requirements, the behavior that must not change, fixture conventions it missed, the docs to update, and the rationale and decisions.
5. **Author the body** with these seven sections, in this order, every one present. An empty section reads `none — <why>`, so a reader can tell "nothing here" from "forgotten":

   1. `## Codebase exploration findings` — architecture, affected modules, patterns, data models, fixtures, configuration, from the research.
   2. `## Requirements` — `SR-1`, `SR-1.1`, … grouped under one heading per domain, each an observable behavior. It always ends with two subsections:
      - `### Mechanism lifecycle` — for each mechanism the design introduces (new state, configuration, persisted or wire field, background task, gate, retry path, and the like), where it is created, consumed, and torn down in every scope and exit path;
      - `### Policy decisions this design implies` — each yes/no question the design forces, with the recommended answer.

      Each reads `none — <why>` when empty. They are what breakdown cites when it lists the sites a Task owns, and a missing lifecycle leg otherwise surfaces only as late review churn.
   3. `## Test Fixtures` — the helpers, factories, sample data, and mocks to reuse, by real name.
   4. `## Existing Behavior` — the contracts that must not change: API shapes, persisted data, wire fields, configuration meaning.
   5. `## Documentation` — the docs to update after implementation, by their `## Documentation Locations` paths.
   6. `## Background and rationale` — why the design looks this way.
   7. `## Decisions and rejected alternatives` — each decision with the alternatives weighed and why they lost.

   Sections 6 and 7 carry what the conversation settled, so downstream agents do not re-litigate it. An SDD says how the system is built; user stories and business goals belong in the PRD.
6. **Write the ticket.** Put the body in a file. Every file this skill writes goes under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), creating the directory if absent, with a collision-resistant name, and is never deleted. Pass it with `--body-file`, because an inline body with a newline before `#` trips Claude Code's command-injection guard. With no SDD, create a `t1` child of the Spec Bee in the `specs` hive, titled `SDD`, status `drafted`. With one, replace its body and set it to `drafted`: a revised SDD is unapproved until its gate passes.
7. **Solo only: review and approve.**
   - Invoke `/quo-spec-review <spec-bee-id> --doc SDD` through the Skill tool.
   - Apply each finding whose smallest complete fix path is `trivial-tweak` yourself, rewriting the ticket body.
   - Then write the current body to a fresh body file and, in the same turn, call `AskUserQuestion` with the body's summary, the `RESEARCH NEEDED` questions, and the remaining findings. The file write in that turn is what keeps the gate from being described and left unasked.
   - Choices: **Approve** (set the SDD `ready`; a `blocker` approved over is recorded in the report), **Revise** (apply the remaining findings and the user's changes, then review again), **Cancel** (put the prior body and status back; an SDD this run created stays `drafted`).
8. **Finish.** Inline, return `sdd_ticket_id`, `sdd_status`, `action`, and `research_needed`. Solo, report the Spec Bee, the SDD ID, whether it was created or updated, its status, the `RESEARCH NEEDED` questions, and any findings approved over. The Spec Bee's own status belongs to the caller.
