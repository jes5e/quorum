---
name: quo-spec-review
description: Fresh-eyes review of a Spec Bee's PRD and SDD `t1=Doc` children for clarity, completeness, and internal consistency. Invoked by `/quo-plan` (both children, before its plan-approval gate) and by `/quo-write-prd` / `/quo-write-sdd` on their solo path (`--doc PRD` / `--doc SDD`); also runs standalone as an ad-hoc spec audit. Returns a list of findings and edits nothing.
argument-hint: "<spec-bee-id> [--doc PRD|SDD]"
---

Review the PRD and SDD of one Spec Bee — its `t1` children titled exactly `PRD` and `SDD` — and return findings for the caller to act on. This skill never edits a ticket; the caller, or the user when it runs standalone, decides what to fix. It reviews the specs against their contract. Whether the plan is a sound solution is the plan reviewer's lane in `/quo-plan`.

## Preconditions

Hard-fail with `Run /quo-setup first.` plus a one-line reason when `bees list-hives` has no hive whose `normalized_name` is `specs`.

## Parameters

- `<spec-bee-id>` (required). Ask for a missing one in prose.
- `--doc PRD` or `--doc SDD` (optional) scopes the review to one child. Without it, both children are reviewed and then checked against each other.

## Steps

1. **Resolve the children.** Query the Spec Bee's children for the titles `PRD` and `SDD`, matched exactly. With none in scope, output `No spec content to review` and stop. With more than one per title, stop and ask the user which is canonical.
2. **Read each body** with `bees show-ticket`. The ticket body is the spec downstream skills consume, so review it and never a file on disk. The Spec Bee's own body, source code, tests, and project docs are other reviewers' lanes.
3. **Review against `## Criteria`**, citing the document and section in every finding.
4. **Return the findings** in the `## Output` shape. An invoking skill continues at its own next step, usually its gate. Standalone, stop there: the user reads the list and decides, and there is no gate.

## Criteria

A section missing entirely (not rendered as `none — <why>`) is a `blocker`. A vague placeholder such as "TBD" is a finding.

**PRD** (twelve sections, `## Problem Statement` through `## Decisions and rejected alternatives`):

- The problem names who has it and why now.
- Goals are measurable.
- Every acceptance criterion is objectively verifiable and traces to a goal or requirement; goals with no criterion are gaps.
- Non-goals are specific, and nothing else contradicts them.
- No implementation detail (modules, libraries, API sequences), which belongs in the SDD.
- No vague language ("fast", "user-friendly", unqualified "always").
- Rationale and decisions are captured with the alternatives weighed.
- Open questions name who answers them.

**SDD** (seven sections, `## Codebase exploration findings` through `## Decisions and rejected alternatives`):

- Codebase findings cite real names, not "the routing layer".
- Every `RESEARCH NEEDED:` tag is surfaced so the user can decide whether to resolve it now.
- `SR-` requirements are grouped by domain and each is an observable behavior.
- `## Requirements` ends with `### Mechanism lifecycle` and `### Policy decisions this design implies`. A new mechanism missing a lifecycle leg in any scope is a `blocker`.
- The architecture is framed at subsystem and component level.
- `## Existing Behavior` names specific contracts (generic "preserve compatibility" is a `blocker` when the work touches a public surface).
- Fixtures are named.
- Docs are named by their `## Documentation Locations` paths.
- New data models are described.
- Any change to a contract surface (CLAUDE.md contract keys, the bees command surface, ticket fields, hive names) is called out.
- The design splits into a few independent units that breakdown can separate.
- Rationale and decisions are captured.

**Cross-document**, when both are in scope:

- Every PRD goal and acceptance criterion is covered by the SDD.
- Every `SR-` requirement traces to the PRD.
- Nothing the PRD excludes is designed.
- The SDD does not decide what the PRD lists as open.
- The two agree on rejected alternatives.

## Output

```markdown
## Spec Review Work Items

1. `<blocker|suggestion|nit>` target: <PRD|SDD|Cross-document> `<## Section>` — <what is wrong and what must change>
   (a) [depth:<trivial-tweak|refactor-locally|re-architect>] <one fix path>
   (b) [depth:<...>] [preferred] <another fix path, if there is one>
```

With nothing to report, the list is the single line `No spec issues found.`

**Severity** is the consequence of leaving the finding as it stands. `blocker`: a downstream agent builds the wrong thing, breakdown mis-shapes the Epics, or the Doc Writer misses a required update. `suggestion`: the spec is right but a reader goes wrong in a case it does not cover. `nit`: the fix only improves it.

**Depth** is per fix path: `trivial-tweak` is one local wording or value edit, `refactor-locally` restructures one section or document, and `re-architect` changes the core approach. The caller applies a `trivial-tweak` fix without re-running the writer. Mark `[preferred]` on at most one path, and only when you hold a real preference; the caller still makes its own pick.

Report what matters and nothing more. A caller loops review → fix → review, and trivia each pass keeps that loop from ending. Often a spec has no important issue; say so.
