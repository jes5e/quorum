---
name: quo-plan
description: Interactive feature planning — agree the scope, author the PRD and SDD as Spec Bee children (no project-doc mutation), review the specs and the Epic decomposition, and create a Plan Bee with Epics ready for /quo-breakdown-epic and /quo-execute.
argument-hint: "[<description>]"
---

Turn an idea into a reviewed plan: a Spec Bee holding the PRD and SDD, and a Plan Bee whose Epics `/quo-breakdown-epic` can break down. Planning never writes the project's own docs; the post-implementation Doc Writer does that once the feature ships.

## 1. Preconditions

Hard-fail with `Run /quo-setup first.` plus a one-line reason when `bees list-hives` has no hive whose `normalized_name` is `plans` or `specs`, or the target repo's CLAUDE.md has no `## Documentation Locations` section. Check at run start: the plan tickets are written last, so a missing hive found then would cost the whole planning conversation.

**Working rules for every step.**

- bees is the ticket store; `bees <command> -h` and `bees sting` document it. It has no ticket list or search verb: enumerate with `bees execute-freeform-query`, pass the query on one line in YAML flow style (`{stages: [[...]], report: [...]}`), and name the fields you need in `report:`.
- Write every file this run creates (the manifest, the scope file, the plan draft, body files) under `/tmp/.quorum/` (`%TEMP%\.quorum` on Windows), creating the directory if absent. Never delete them: they are the record of a crashed run. Give each a collision-resistant name, except the manifest (Section 2).
- Pass every multi-paragraph ticket body with `--body-file`, never inline, because a newline followed by `#` trips Claude Code's command-injection guard.
- Run each shell command as one literal command, with no pipes, chains, or `$` substitution, because those shapes re-prompt the user for permission; put multi-step logic in a Python script instead.
- Ask free-text questions in prose and let the user answer in their next turn. `AskUserQuestion` is multi-choice only and appends its own free-text slot, so never add an option that points at it.

## 2. Run-state manifest

The manifest holds what the run needs and bees does not: its phase, what it has created, the open gate, and the open deferrals.

**Path.** `/tmp/.quorum/run-state-quo-plan-<repo-dir-name>.md` (`%TEMP%\.quorum\run-state-quo-plan-<repo-dir-name>.md` on Windows), where `<repo-dir-name>` is the last path segment of `git rev-parse --show-toplevel`. The name is deterministic, with no suffix or timestamp, because after a compaction you must recompute the path rather than remember it. Accepted collision: two `/quo-plan` runs in one repo at the same time.

**Lifecycle.** At run start, read the manifest. When it is absent or reads `**Phase:** complete`, write a fresh one. Otherwise an earlier run stopped partway: fire the resume gate (Section 3), because only the user knows whether that run is abandoned. Rewrite the manifest whenever a value changes, and record each ticket ID as its create returns.

```markdown
# Run state — quo-plan @ <repo-dir-name>

**Phase:** <scope | specs | draft | review | approved | created | handoff | complete>
**Feature:** <title, or pending>
**Scope file:** <path, or pending> · **Plan draft:** <path, or pending>
**Spec Bee:** <id, or pending> · **PRD:** <id, or pending> · **SDD:** <id, or pending>
**Plan Bee:** <id, or pending> · **Epics:** <Epic N = <id>, …, or pending>

## Obligations

| item | destination | status |
|---|---|---|

## Open gate

none
```

After a compaction or a crash, re-read the manifest and reconcile it with bees before acting.

## 3. Gates

A gate is the manifest `Write` that fills `## Open gate` with the gate's name, question, and choices, then `AskUserQuestion` in the same turn. The tool call in the same turn is what keeps a gate from being described and left unasked: that happened three times at this skill's review gate, and stronger wording did not stop it. Set `## Open gate` back to `none` once the answer is consumed.

Gates fire only where the user holds the decision:

- **Resume** — question `An unfinished /quo-plan run for "<feature>" stopped at phase <phase>. Resume it?`; choices **Resume** (continue from the recorded phase) and **Start fresh** (overwrite the manifest; tickets already created stay as they are).
- **Scope** — choices **Approve**, **Revise**, **Cancel** (Section 4).
- **Spec Bee reuse**, only when a `drafted` candidate matches — choices `Reuse existing Spec Bee`, `Create a new Spec Bee anyway`, `Cancel` (Section 5).
- **Plan approval**, once per review round — choices **Approve**, **Approve over blockers**, **Revise**, **Cancel** (Section 8).
- **Deferral hygiene**, only when obligations are open — choices `Fix in this session`, `File as issue tickets`, `Encode in an existing ticket body` (Section 10).
- **Next steps** — Section 10.

A `Cancel` at any gate sets `**Phase:** complete`, reports what exists and any open obligations, and stops. Nothing is ever written to the Plans hive before plan approval, so a cancelled run leaves no Plan Bee to clean up.

## 4. Scope

Agree what is being built before any ticket exists.

When the conversation or the `<description>` argument already carries substantive scope (the problem, who has it, goals, decisions, rejected alternatives), distill it rather than ask again. Err toward distilling: re-asking what the user already settled costs them a repetition, while a draft they correct costs one reply. Otherwise ask in prose, first for context you should know (reference implementations, services to look at, constraints, prior art), then, after researching, for the problem, the scope (minimum or full), constraints, and dependencies.

Research before you draft: the target CLAUDE.md, the relevant source, anything the user pointed to, and the project PRD/SDD at the `Project requirements doc (PRD)` and `Internal architecture docs (SDD)` keys of `## Documentation Locations`. Query Plan Bees of any status and open Issues for overlapping work, and discuss with the user whether to extend, depend on, or stay separate from any overlap. When the request is really a defect in existing behavior, suggest `/quo-file-issue` instead.

Write the scope to a scope file and record its path. Render an empty section as `none`, so a reader can tell "nothing here" from "forgotten". The sections: `# <feature title>`, `### What`, `### Why`, `### Acceptance criteria`, `### Out of scope`, `### Decisions`, `### Rejected alternatives`, `### Constraints`, and `### Prior context` (what the user pointed you to). Both writers read this file, and the decisions and rejected alternatives are what downstream agents otherwise re-litigate.

Fire the scope gate, showing the scope. **Approve** moves to Section 5. **Revise** means iterate in prose, rewrite the file, and ask again. **Cancel** stops the run.

## 5. Spec Bee and specs

**Spec Bee.** A re-run for the same unfinished feature must reuse its Spec Bee, because a duplicate fragments the PRD and SDD silently.

- Query the `specs` hive's Bees and compare titles after normalizing: lowercase, whitespace collapsed, surrounding punctuation trimmed.
- Only a `drafted` Spec Bee is a candidate. A `ready` one holds approved specs that existing Plan Bees may read, and the writers would overwrite them before any gate, so never reuse or change it. When a `ready` Spec Bee matches, say so and create a new one; revising an approved spec in place is the solo writers' job (`/quo-write-prd <spec-bee-id>`, `/quo-write-sdd <spec-bee-id>`).
- On a `drafted` match, or a near match you cannot rule out, fire the Spec Bee reuse gate. `Reuse existing Spec Bee` takes its ID; `Create a new Spec Bee anyway` falls through to creating one; `Cancel` stops the run.
- Otherwise create a `bee` in the `specs` hive, status `drafted`, titled with the feature title, with a two-to-three-sentence body from the scope. The PRD and SDD content belongs in its children, never in this body. Record the ID.

**Writers.** Invoke `/quo-write-prd`, then `/quo-write-sdd`, through the Skill tool, never in parallel, since both add children to one Spec Bee. Pass each the same `args`:

```
spec-bee-id: <spec-bee-id>
distilled-scope: <scope file path>
```

Invoked this way the writers fire no gates, leave their child `drafted`, and return `prd_ticket_id` / `sdd_ticket_id`, the status, `action`, and for the SDD `research_needed`. Record both IDs. A writer error stops the run with the error reported; the manifest lets a re-run resume, and the writers update rather than duplicate.

## 6. Plan draft

Draft the plan into one file and record its path. Draft it before creating any Plans-hive ticket, so the review and any revision change a file, not tickets. The file has one `#` heading per ticket: `# Plan Bee body`, then `# Epic N — <short title>` for each Epic. Each ticket's body is everything under its heading, down to the next `#` heading, without the heading line itself.

**The Plan Bee body** is a two-to-three-sentence summary of the feature, then `## Anticipated doc impact`. That section lists which cumulative project docs the feature should update once it ships, named by their CLAUDE.md `## Documentation Locations` keys (for example `Project requirements doc (PRD)`, `Internal architecture docs (SDD)`, `Customer-facing docs`). It names keys rather than paths because projects route those keys to different files. It is the Doc Writer's starting checklist.

**Each Epic body** gives its outcome, scope, acceptance criteria, and the earlier Epics it depends on; N runs from 1 in dependency order. Decompose so that:

- every Epic leaves the codebase green, with all existing tests passing;
- each Epic is one coherent user- or system-visible outcome, sliced vertically by capability, never a layer (no "API Epic"); pure refactors may be foundational Epics but go vertical as soon as possible;
- testing and documentation fold into the Epic whose work they cover, never a separate Epic, and an Epic that changes config, behavior, or deployment carries its customer-facing doc update;
- no chain of Epics leaves an untestable intermediate state, and no Epic mixes a pervasive refactor with feature work;
- acceptance criteria name what the user interacts with and how they check it, or how the agent demonstrates it ("Server starts on http://localhost:8000", not "Server is available");
- Epics are as small as a single coherent outcome allows; one Epic is fine for a small feature.

Dependencies link sibling Epics only. A dependency on a Bee is not expressible, so a release gate on other work belongs in the Epic body as prose.

## 7. Reviews

The first round runs both reviews on the same state, before the plan-approval gate. `/quo-spec-review` checks the specs against their contract. A cold reviewer checks whether the plan is a sound solution; it exists because a checklist review let plan-level design errors through, and on its first real run it caught three.

Dispatch the plan reviewer as `Agent(subagent_type=general-purpose, run_in_background=true, prompt=…)` with this section's prompt, IDs and path filled in. While it works, invoke `/quo-spec-review <spec-bee-id>` through the Skill tool with no `--doc`. Then wait for the reviewer's completion notification.

```
You are an independent, read-only reviewer of a feature plan. Do not modify any
ticket or file. Read the PRD (<prd-id>) and SDD (<sdd-id>) with
`bees show-ticket --ids <id>`, and the plan draft at <plan-draft-path>, which
holds the Plan Bee body and the proposed Epics.

Your lane is substance: is the problem understood and framed right; is the
approach sound; is each Epic one vertical, testable outcome that leaves the
codebase green; are dependencies right; what risks, alternatives, or load-bearing
assumptions went unexamined. A new mechanism whose lifecycle (created, consumed,
torn down, in every scope and exit path) the SDD leaves incomplete, or a policy
decision the design implies but leaves open, is a substance finding. Prose quality
(section completeness, wording, citation density) is another reviewer's lane:
leave it out.

Return a numbered list, each finding in this shape:

1. `<blocker|suggestion|nit>` target: <PRD|SDD|Plan-Bee-body|Epic:<N>> — <what is wrong and what must change>
   (a) [depth:<trivial-tweak|refactor-locally|re-architect>] <one fix path>
   (b) [depth:<...>] [preferred] <another fix path, if there is one>

Severity is the consequence of leaving it: `blocker` means the plan as written
builds the wrong thing or cannot be built; `suggestion` means it is right but
leaves a case uncovered; `nit` means the fix only improves it. Depth is the size
of a fix path: `trivial-tweak` is one local wording or value edit,
`refactor-locally` restructures one document or one Epic, `re-architect` changes
several Epics or the core approach. Mark `[preferred]` on at most one path, only
when you hold a real preference. Epic dependencies can link sibling Epics only.

End with exactly one line:

Plan-review verdict: <approve | revise-recommended | escalate-to-user>

`approve`: coherent, with at most suggestions or nits. `revise-recommended`: at
least one blocker. `escalate-to-user`: an ambiguity only the user can settle.
With no findings, return `No plan-review issues found.` and then the verdict line.
```

Route each finding by where its fix lands:

- Pick the smallest enumerated fix path that fully fixes the finding as stated. `[preferred]` is an input; a fuller path taken only to prevent recurrence is not a fuller fix.
- When the pick is `trivial-tweak`, apply it yourself without asking: rewrite the PRD or SDD child's body (it stays `drafted`), or edit the plan draft.
- Other picks wait for the gate. After **Revise**, a PRD or SDD fix goes to that writer alone, re-invoked with the usual `args` plus a `findings:` key carrying the finding lines verbatim. The user's own requested changes go the same way, one line each; a change of scope rewrites the scope file first. A Plan Bee body or Epic fix is yours to make in the draft.
- Drop a plan-review finding about prose quality.
- After a revision, re-run only the reviews whose input changed: spec review when a child changed, the plan reviewer whenever anything did.

## 8. Plan approval

Lead with the verdict in a sentence: the plan reads as coherent (`approve`), it has blockers (`revise-recommended`), or, prefixed with ⚠️, the reviewer found an ambiguity only the user can settle (`escalate-to-user`). Then show:

- the PRD and SDD summaries with their ticket IDs, so the user can open the bodies, which no earlier gate shows;
- any `RESEARCH NEEDED` questions;
- the Plan Bee body draft and the Epic list;
- the trivial fixes you applied;
- the remaining findings verbatim.

Fire the plan-approval gate. Offer **Approve** when no `blocker` is open, and **Approve over blockers** in its place when one is. On `escalate-to-user`, mark no choice (Recommended): the call is the user's. Otherwise mark **Revise** (Recommended) when a `blocker` is open, and **Approve** (Recommended) on a clean `approve` verdict.

- **Approve** or **Approve over blockers** → Section 9. A finding approved over is a won't-fix, listed in the report with any overridden blockers. A finding the user wants fixed later becomes an open `## Obligations` row with its intended destination.
- **Revise** → route the remaining findings and the user's own changes (Section 7), then run the next round.
- **Cancel** → the Spec Bee and its children stay `drafted`; a re-run reuses them.

Whenever the user or a reviewer defers something to later, anywhere in the run, add an open `## Obligations` row at once: the next session reads only tickets, so a deferral that exists only in this conversation is lost.

## 9. Create the plan

Set `**Phase:** approved`, then write in this order, recording each ID in the manifest:

1. Set the PRD and SDD children to `ready`, then the Spec Bee.
2. Create the Plan Bee in the `plans` hive, status `drafted`, titled with the feature title, with its drafted body and `reference_materials` exactly `[{"value":"<spec-bee-id>","resolver":"bees"}]`. Downstream skills follow that entry to the Spec Bee and read its children titled `PRD` and `SDD`.
3. Create each Epic as a `t1` child of the Plan Bee, status `drafted`, titled `Epic N — <short title>` exactly as drafted, with its drafted body. The ordinal title is the Epic's human label in every later status line and commit.
4. Set each Epic's `up_dependencies` to the Epics it depends on.
5. Set the Plan Bee to `ready`. `/quo-breakdown-epic` picks `ready` Plan Bees and breaks down their `drafted` Epics.

Set `**Phase:** created`.

## 10. Handoff

**Deferral hygiene.** Set `**Phase:** handoff`. When `## Obligations` has no open row, print `Deferral hygiene: no deferred items.` Otherwise list the open rows and fire the deferral-hygiene gate. The user can route different items differently by writing that in the free-text slot.

- `Fix in this session` — do the work now. A spec change goes through the solo writer: invoke `/quo-write-prd <spec-bee-id>` or `/quo-write-sdd <spec-bee-id>` through the Skill tool with no other `args`. It reviews and gates the change, and the row closes on its **Approve**.
- `File as issue tickets` — invoke `/quo-file-issue` through the Skill tool with the item as its description.
- `Encode in an existing ticket body` — append a `## Deferred from /quo-plan run (<YYYY-MM-DD HH:MM>)` section to one of this run's Plans- or Specs-hive tickets, keeping its existing body. The timestamp keeps several runs' sections apart. You have no clock, so take it from `date +'%Y-%m-%d %H:%M'` (POSIX) or `Get-Date -Format 'yyyy-MM-dd HH:mm'` (PowerShell).

Close each row as its item lands. Do not hand off while a row is open. When a route fails, show the remaining rows and ask again.

**Report.** List the Spec Bee and its PRD and SDD, the Plan Bee, and each Epic by label with its ID, status, and dependencies. Add any `RESEARCH NEEDED` questions, the findings approved over (overridden blockers marked), and where each obligation went.

**Commit.** Stage only this run's hive files, never the whole tree, because a hive may live outside the repo and the working tree may hold unrelated changes. The sibling helper prints each in-repo hive path, one per line:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive plans --hive specs
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive plans --hive specs
```

Stage the printed paths and commit with the subject `Plan feature: <title> (<plan-bee-id>)`. When it prints nothing, commit nothing and say `Plan stored in bees; no in-repo changes to commit.` An earlier commit by an inline `/quo-file-issue` is expected. Never push. Set `**Phase:** complete`.

**Next steps.** Above the choices, say that the next skill re-reads everything from bees and disk, so a fresh session gives it the full context budget; same-session work fits only a Bee with one or two Epics. Fire the next-steps gate:

- **In a fresh session, break down now** (Recommended) — run `/quo-breakdown-epic <bee-id>` in a new session.
- **In a fresh session, execute now** — run `/quo-execute <bee-id>` in a new session.
- **Continue in this session: break down now** — load `quo-breakdown-epic` now.
- **Continue in this session: execute now** — load `quo-execute` now.
- **Review first** — the user reviews the plan before going on.
- **Done for now** — the plan is saved.
