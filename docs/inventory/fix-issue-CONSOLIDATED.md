# Consolidated rule inventory — `skills/quo-fix-issue/SKILL.md`

Consolidation of the seven raw extracts `docs/inventory/fix-issue-01…07-*.md` (1,434 raw rows over SKILL.md L1–L1342). Every raw row is carried into exactly one deduped row below (its ID appears in that row's **Sources**); rows are merged only when an executing orchestrator would treat them as one instruction (same rule stated at several sites, or one rule split across sentences). Rows that merely share a topic stay separate. Where two source rows conflict, both are kept and listed under `## Inconsistencies noticed`.

Column key: **Sites** = SKILL.md line(s) + anchor (abbreviated: `ODR` = `### Orchestrator discipline: routing review findings`, `SBL` = its **Severity bounds the loop.** paragraph, `RL` = `#### Reconciliation loop`, `DP` = `##### Dispatch prompt: quote the issue body verbatim and embed the design directive`, `TNC` = `##### TaskList naming convention`, `CKPT` = `#### Issue-boundary state-externalization checkpoint`, `CWG` = `#### Context-window boundary guard`, `AIC` = `#### Aborted-Issue close-out`, `SCT` = `#### Session-scoped compromise tracker`, `CAT` = `#### Compromise-tracker append triggers`, `PC` = `### 8. Post-Completion Review`). **Env** = union of the sources' Env values (`Agent`, `bees`, `git`, `Bash`, `TaskList`, `AskUserQuestion`, `none`). **Mirror** = the extractors' cross-skill verdict (`yes` / `no` / `unknown`; where merged sources disagree the more permissive value is kept and noted in `## Mirror candidates`). **Class** = `procedure` / `rationale` / `example` / `failure-narrative`.

## Mechanism index

| # | Code | Mechanism | Rows |
|---|---|---|---|
| 1 | PRE | Preconditions & contract keys | 17 |
| 2 | EFF | Session-effort gate | 23 |
| 3 | ARG | Argument parsing & URL resolution | 56 |
| 4 | ISO | Isolation strategy | 15 |
| 5 | MAN | Run-state manifest | 45 |
| 6 | VAL | Issue validation (Section 2) | 11 |
| 7 | ANA | Analyst dispatch & design gate (Section 3) | 61 |
| 8 | DEFC | Deferred-refinements consumption | 19 |
| 9 | DIR | Design directive (composition & precedence) | 8 |
| 10 | LOOP | Reconciliation loop & Phase A/B/C ladder | 35 |
| 11 | RECOV | Post-compaction recovery / re-derivation | 37 |
| 12 | ENGPRE | Engineer-dispatch precondition | 20 |
| 13 | MOVE | Movement-report rung & `aborted-*` markers | 29 |
| 14 | UNEXP | Unexplained-movement gate | 14 |
| 15 | DQ | Design-question receiver & Analyst re-dispatch | 25 |
| 16 | PROMPT | Cold-dispatch shape & prompt contents | 46 |
| 17 | ROLES | Roles & lane boundaries | 29 |
| 18 | TASK | TaskList progress UI & naming convention | 31 |
| 19 | GATE | `gate-*` two-step contract | 12 |
| 20 | SCOPED | Scoped-marker PM wiring | 5 |
| 21 | ROUTE | Routing discipline (ODR parts (a)–(g), SBL) | 127 |
| 22 | REVIEW | Review loop & trailer consumption (Section 5) | 10 |
| 23 | LEDGER | Ignored-feedback / `defer-*` ledger | 12 |
| 24 | DOCV | Doc verification (Section 6) | 7 |
| 25 | CLOSE | Per-issue close-out & commit (Section 7 steps 1–3, 5) | 29 |
| 26 | SUM | Summary template (Section 7 step 4) | 26 |
| 27 | CKPT | Issue-boundary state-externalization checkpoint | 32 |
| 28 | GUARD | Context-window boundary guard | 39 |
| 29 | ABORT | Aborted-Issue close-out | 31 |
| 30 | HYG | Deferral-hygiene gate (Section 7.5 Steps 0–3, Fix/File/Encode, `hive_commit.py`) | 86 |
| 31 | TRACK | Compromise tracker (file, entry shape, Decision enum, Triggers A–D) | 81 |
| 32 | POSTC | Post-completion review (Section 8 scope, skeleton, disposition, postcomp lanes, commit) | 100 |
| 33 | SRGATE | Compromise-challenge recovery gates (SR-6.7 / SR-4.6) | 21 |
| 34 | GH | GitHub close recommendation (Section 9) | 33 |
| 35 | SHELL | Shell etiquette / scratch-file convention | 5 |

(Row counts verified by script against the tables below; totals in `## Totals`.)

---

## 1. PRE — Preconditions & contract keys

- **Purpose:** Refuse to run unless the target repo is quorum-configured (hives, CLAUDE.md contract sections, eight registered subagent types), so downstream skills never improvise commands or roles.
- **Failure it prevents:** Guessing build commands / doc paths on polyglot repos, or silently substituting `general-purpose` for a missing role and running an unreviewed workflow (F1-027, F1-032).
- **Env deps:** bees, Bash, Agent. **TaskList-dependent: no.**
- **Rows:** 17 (procedure 15, rationale 2, example 0).
- **Literals:** `Run /quo-setup first.`; hard-fail text `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`; `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`; subagent types `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`; `general-purpose`; `/agents`; `README.md` `## Install`; `bees list-hives`; `normalized_name` = `issues` / `specs`; `## Documentation Locations`; `## Build Commands`; keys `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`; Agent error shape `Agent type '<name>' not found`.
- **Edges:** Consumes target CLAUDE.md (contract keys, shared with PROMPT/ROLES readers `pm`, `doc-writer`, `engineer`); Produces run exit for every later mechanism; the dispatch-time check rides on ANA's first Agent dispatch.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-PRE-1 | Before anything else, verify the host repo is configured for quorum; on failure **Hard-fail** with `Run /quo-setup first.` plus a one-line note of what is missing. | precondition | L19 `## Preconditions` | F1-013 | hard-fail message | CLAUDE.md, bees hives, subagent registry | bees, Bash | yes | procedure |
| FX-PRE-2 | Require the eight custom subagent types registered in the session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`. | precondition | L21 | F1-014 | - | session subagent registry | Agent | unknown (quo-execute has no `analyst`) | procedure |
| FX-PRE-3 | Custom subagents load at session start; a fresh install needs a Claude Code restart or `/agents` hot-reload before dispatch works. | definition | L21 | F1-015 | - | - | none | yes | procedure |
| FX-PRE-4 | Subagent verification rides on the first dispatch: if any of the eight is missing (an `Agent type '<name>' not found`-style Agent-tool error), STOP, emit the hard-fail message, and exit the run. | gate | L21; L31 **Verifying the subagents precondition.** | F1-016, F1-030 | hard-fail message; run exit | Agent tool error | Agent | yes | procedure |
| FX-PRE-5 | On a missing subagent type: never fall back to `general-purpose`, never skip the dispatch, never improvise substitute roles. | invariant | L21; L31 | F1-017, F1-031 | - | - | Agent | yes | procedure |
| FX-PRE-6 | The subagent hard-fail message directs the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents`; example text: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` | field-or-template | L21 | F1-018, F1-019 | hard-fail message | `<missing-list>` | none | yes | procedure |
| FX-PRE-7 | Require the Issues hive colonized: `bees list-hives` must include a hive whose `normalized_name` is `issues`. | precondition | L22 | F1-020 | - | `bees list-hives` output | bees | yes | procedure |
| FX-PRE-8 | Require the Specs hive colonized: `bees list-hives` must include a hive whose `normalized_name` is `specs`. | precondition | L23 | F1-021 | - | `bees list-hives` output | bees | yes | procedure |
| FX-PRE-9 | If Specs is absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` | field-or-template | L23 | F1-022 | hard-fail message | FX-PRE-8 result | none | yes | procedure |
| FX-PRE-10 | Require CLAUDE.md to contain a `## Documentation Locations` section. | precondition | L24 | F1-023 | - | target CLAUDE.md | none | yes | procedure |
| FX-PRE-11 | The PM and Doc Writer read architecture/customer-doc paths from `## Documentation Locations` by exact key. | definition | L24 | F1-024 | - | `## Documentation Locations` | none | yes | procedure |
| FX-PRE-12 | Require CLAUDE.md to contain `## Build Commands` with all five keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. | precondition | L25 | F1-025 | - | target CLAUDE.md | none | yes | procedure |
| FX-PRE-13 | The Engineer reads compile/format/lint/test commands from `## Build Commands` by exact key. | definition | L25 | F1-026 | - | `## Build Commands` | none | yes | procedure |
| FX-PRE-14 | Rationale: commands and doc paths come from CLAUDE.md so the skill works on any stack; auto-detection is unsafe on polyglot/monorepo/custom builds. | rationale-only | L27 | F1-027 | - | - | none | yes | rationale |
| FX-PRE-15 | If any precondition is missing, stop with `Run /quo-setup first.` and direct the user there. | gate | L29 | F1-028 | hard-fail message; run exit | FX-PRE-1..13 | none | yes | procedure |
| FX-PRE-16 | Do not improvise commands or guess paths when a precondition is missing. | invariant | L29 | F1-029 | - | - | none | yes | procedure |
| FX-PRE-17 | Rationale: the dispatch-time gate is honest about session-load semantics and fires at the natural failure point, so token pressure or creativity cannot bypass it. | rationale-only | L31 | F1-032 | - | - | none | yes | rationale |

---

## 2. EFF — Session-effort gate

- **Purpose:** Warn (once, at run start) when the orchestrator's session effort is strictly below the skill's `medium` floor, without ever creating a stranded gate task.
- **Failure it prevents:** A phantom prompt fired later from a stranded `pending` `gate-*` task (F1-042); spurious prompts on every run when the variable is unset (F1-048); gate fatigue for operators running hotter (F1-051).
- **Env deps:** Bash, TaskList, AskUserQuestion. **TaskList-dependent: yes** (Step 3 gate task only).
- **Rows:** 23 (procedure 20, rationale 3, example 0).
- **Literals:** `CLAUDE_EFFORT`; `printenv CLAUDE_EFFORT`; `Write-Output $env:CLAUDE_EFFORT`; effort values `low` / `medium` / `high` / `xhigh` / `max`; floor `medium`; `/model`; `gate-askuserquestion-<short-suffix>`; options **Proceed anyway**, **Let me change it first**; question text opening `This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. …`; `#### Check session reasoning effort`.
- **Edges:** Runs before ARG's issue-pick gate and ISO; uses GATE's two-step contract; noted by POSTC (its `general-purpose` sweep inherits session effort).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-EFF-1 | Run the reasoning-effort check **first in Section 1**, ahead of the issue-pick gate (no-args mode) and the isolation-strategy gate. | ordering | L39 `#### Check session reasoning effort` | F1-033 | - | - | none | yes | procedure |
| FX-EFF-2 | Rationale: **Let me change it first** exits the run, so firing first means the user never re-answers a pick already made. | rationale-only | L39 | F1-034 | - | - | none | yes | rationale |
| FX-EFF-3 | Run the effort check once at run start — not per issue. | ordering | L39 | F1-035 | - | - | none | yes | procedure |
| FX-EFF-4 | The skill is tuned for an orchestrator session at **`medium`** effort or higher. | definition | L41 | F1-036 | - | - | none | yes | procedure |
| FX-EFF-5 | Every subagent dispatched from a role file (`agents/*.md`) has effort pinned in frontmatter and is **not** affected by the session setting. | definition | L41 | F1-037 | - | `agents/*.md` frontmatter | Agent | yes | procedure |
| FX-EFF-6 | The check concerns the orchestrator's seat plus any role-file-less dispatch — notably Section 8's `general-purpose` post-completion sweep, which inherits the session setting. | definition | L41 | F1-038 | - | - | Agent | yes | procedure |
| FX-EFF-7 | The skill cannot change session effort itself; at most it names the recommendation and lets the user apply it. | invariant | L41 | F1-039 | - | - | none | yes | procedure |
| FX-EFF-8 | **Ordering is load-bearing**: read the environment variable **first**, evaluate against the floor, and only then decide whether a gate fires. | ordering | L43 | F1-040 | - | `CLAUDE_EFFORT` | Bash | yes | procedure |
| FX-EFF-9 | **Step 1**: read the session's current effort with one literal command and no shell conditional — POSIX `printenv CLAUDE_EFFORT`; PowerShell `Write-Output $env:CLAUDE_EFFORT`; the comparison is your own reasoning. | command | L45-L55 **Step 1 — read the session's current effort.** | F1-043, F1-044, F1-045 | effort value | `CLAUDE_EFFORT` | Bash | yes | procedure |
| FX-EFF-10 | `CLAUDE_EFFORT` reports the session's **current** effort and tracks mid-session changes (e.g. `/model`), not a launch-time flag. | definition | L57 | F1-046 | - | `CLAUDE_EFFORT` | none | yes | procedure |
| FX-EFF-11 | If output is empty, exit is non-zero, or the value is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat as unset: **skip this check entirely and continue to the next sub-step, silently.** | recovery | L59 | F1-047 | - | Step 1 output | none | yes | procedure |
| FX-EFF-12 | Rationale: a spurious prompt on every run is worse than a missed advisory. | rationale-only | L59 | F1-048 | - | - | none | yes | rationale |
| FX-EFF-13 | **Step 2**: the floor is `medium`; the ordering is `low` < `medium` < `high` < `xhigh` < `max`. | definition | L61 **Step 2 — compare against this skill's floor, which is `medium`.** | F1-049 | comparison result | effort value | none | yes | procedure |
| FX-EFF-14 | Compare against the floor, never for equality. | invariant | L61 | F1-050 | - | effort value | none | yes | procedure |
| FX-EFF-15 | Rationale: an operator running hotter costs wall-clock, not quality; interrupting them is gate-fatigue noise. | rationale-only | L61 | F1-051 | - | - | none | yes | rationale |
| FX-EFF-16 | **At or above `medium`**: say nothing — no gate, no prompt, no output, **no `TaskCreate`**; continue. | gate | L63 | F1-052 | - | comparison result | none | yes | procedure |
| FX-EFF-17 | **Strictly below `medium`**: fire the gate in Step 3. | gate | L64 | F1-053 | gate | comparison result | TaskList, AskUserQuestion | yes | procedure |
| FX-EFF-18 | **Step 3**: honor the two-step contract — `TaskCreate` a `gate-askuserquestion-<short-suffix>` task naming this gate, then call `AskUserQuestion` in the same turn (this gate's instance of FX-GATE-1). | gate | L66 **Step 3 — fire the gate (this branch only).** | F1-054 | `gate-askuserquestion-<short-suffix>` task; prompt | comparison result | TaskList, AskUserQuestion | yes | procedure |
| FX-EFF-19 | Substitute the value read in Step 1 for `<current>` in the question text. | field-or-template | L66 | F1-055 | question text | effort value | AskUserQuestion | yes | procedure |
| FX-EFF-20 | Question text (verbatim): "This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation … Subagent effort is pinned per role and is NOT affected by this setting." | field-or-template | L68-L75 | F1-056 | question text | `<current>` | AskUserQuestion | yes | procedure |
| FX-EFF-21 | Option 1 **Proceed anyway**: run at current effort; mark the `gate-*` task `completed` and continue to the next sub-step. | choice-set | L79 | F1-057 | `gate-*` task `completed` | user answer | TaskList, AskUserQuestion | yes | procedure |
| FX-EFF-22 | Option 2 **Let me change it first**: exit without dispatching anything or fixing any issue; user runs `/model` then re-invokes; mark the `gate-*` task `completed`, then exit cleanly. | choice-set | L80 | F1-058 | `gate-*` task `completed`; run exit | user answer | TaskList, AskUserQuestion | yes | procedure |
| FX-EFF-23 | Ordering fragment carried here for locality: do NOT create the gate task before the floor comparison (generic form and rationale in FX-GATE-10/11). | invariant | L43 | F1-041 (also in FX-GATE-10) | - | - | TaskList | yes | procedure |

---

## 3. ARG — Argument parsing & URL resolution

- **Purpose:** Turn the invocation string into an ordered, validated working list of open Issue IDs — filing URL tokens as Issues in place via `/quo-file-issue` — and select the run mode (no-args / single / URL / list / `all`).
- **Failure it prevents:** Losing the user's intentional prerequisite ordering (F1-068, F1-121); aborting a whole run for one bad token (F1-127); pre-fetching upstream content the filing skill owns (F1-111).
- **Env deps:** bees, Agent (Skill tool), AskUserQuestion, TaskList (for `file-from-url-<n>` tracking). **TaskList-dependent: yes** (only the `file-from-url-<n>` progress entries; parsing itself is not).
- **Rows:** 56 (procedure 51, rationale 3, example 2).
- **Literals:** frontmatter `name: quo-fix-issue`, `argument-hint "[<issue-id> | <url> | <id-or-url> ... | all]"`; token `all`; URL test `^https?://`; **URL token** / **ticket-ID token**; `bees show-ticket --ids <id1> <id2> ...`; open-issues query `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'`; `/quo-file-issue`; `## Inline invocation via the Skill tool`; `args` payload `url: <url>`; `summary:`; return fields `issue_ticket_id`, `issue_status` (`open`), `action` (`created` / `reused-existing`); `### Output shape (this skill → caller)`; `### Behavioral guarantees`; announcement `Filing URL(s) as Issue(s) first, then fixing.`; display header `Post-resolution working list:` with lines `2. b.<new-id> (input: <url>, action: created)`; `Approve` / `Revise` / `Cancel` (file-issue distill gate), `Use existing`; TaskList names `file-from-url-<n>`; anchors `#### Parse the argument list and pick issues`, `#### Resolve URL tokens to Issue tickets via /quo-file-issue`, **Up-front validation**, **Notes for list mode**.
- **Edges:** Produces the ordered batch for MAN (`Unit scope`), VAL, LOOP; consumes EFF (runs after), ISO (isolation settled before URL resolution); `/quo-file-issue` Skill-tool precedent reused by ROUTE (Defer), HYG (File), GUARD (Configure now), SRGATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ARG-1 | Frontmatter `name` is `quo-fix-issue`. | definition | L2 | F1-001 | - | - | none | no | procedure |
| FX-ARG-2 | Frontmatter `description`: "Fix an issue described in a Bee ticket. Use '/quo-fix-issue all' … or '/quo-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset." | definition | L3 | F1-002 | - | - | none | no | procedure |
| FX-ARG-3 | Frontmatter `argument-hint` is `"[<issue-id> \| <url> \| <id-or-url> ... \| all]"`. | definition | L4 | F1-003 | - | - | none | no | procedure |
| FX-ARG-4 | The skill has exactly six invocation forms (FX-ARG-5..10). | definition | L9 `## Overview` | F1-004 | - | argument string | none | no | procedure |
| FX-ARG-5 | **Zero tokens** (`/quo-fix-issue`): query all open issues, present them, ask the user to pick one; fix that one issue and exit. | gate | L10; L86 | F1-005, F1-062 | issue-pick prompt; single fix | open-issues query | bees, AskUserQuestion | no | procedure |
| FX-ARG-6 | **Exactly one issue-ID token**: single-issue mode — fix that one issue and exit. | definition | L11; L88 | F1-006, F1-064 | - | token | none | no | procedure |
| FX-ARG-7 | **Two or more tokens** (list mode): an explicit user list of IDs and/or URLs (mixed allowed), separated by spaces, commas, or any mix; run the fix loop (steps 2-7) for each **in the order given**; do NOT sort. | ordering | L12; L90 | F1-007, F1-066, F1-067 | ordered working list | token list | none | no | procedure |
| FX-ARG-8 | **Exactly one URL token** (matches `^https?://`): URL mode — file it as an Issue via the URL-resolution sub-step, then fix the resulting Issue. | ordering | L13; L89 | F1-008, F1-065 | filed Issue, then fix | URL token | Agent (Skill tool), bees | no | procedure |
| FX-ARG-9 | **In-place substitution**: a URL token at position N becomes the resolved `issue_ticket_id` at position N; process mixed lists in input order; NEVER append at the tail, NEVER reorder surrounding tokens, NEVER deduplicate within the list. | invariant | L14; L90; L148 **In-place substitution semantics.** | F1-009, F1-069, F1-117, F1-118, F1-119, F1-120 | post-resolution working list | `issue_ticket_id` | Agent (Skill tool) | no | procedure |
| FX-ARG-10 | **Exactly one token equal to `all`**: `all` mode — query all open issues, sort by ticket_id, run the fix loop (steps 2-7) for each sequentially without user intervention. | ordering | L15; L87 | F1-010, F1-063 | sorted issue batch | open-issues query | bees | no | procedure |
| FX-ARG-11 | Example: `b.cnb,b.sgq b.xet`, `/quo-fix-issue b.cnb b.sgq b.xet`, `/quo-fix-issue b.cnb,b.sgq,b.xet`, `/quo-fix-issue b.cnb, b.sgq  b.xet` all parse to the same three-ID list. | example | L12; L93 | F1-011, F1-072 | - | - | none | no | example |
| FX-ARG-12 | Example URL invocations: `/quo-fix-issue https://github.com/example/repo/issues/123` and `/quo-fix-issue b.cnb https://github.com/example/repo/issues/123 b.xet`. | example | L13-L14 | F1-012 | - | - | none | no | example |
| FX-ARG-13 | Parse the argument string by splitting on any run of commas and/or whitespace; discard empty tokens. | command | L84 `#### Parse the argument list and pick issues` | F1-059 | token list | argument string | none | no | procedure |
| FX-ARG-14 | A token starting with `http://` or `https://` is a **URL token**; anything else is a **ticket-ID token** (validated downstream). | definition | L84 | F1-060 | token classification | token list | none | no | procedure |
| FX-ARG-15 | URL tokens delimit identically to ticket-ID tokens; tokenization is unchanged by URL support. | invariant | L84 | F1-061 | - | - | none | no | procedure |
| FX-ARG-16 | Rationale: the user's order is intentional; earlier issues may be prerequisites for later ones. | rationale-only | L90 | F1-068 | - | - | none | no | rationale |
| FX-ARG-17 | In list mode, do not query or fix issues outside the list. | invariant | L90 | F1-070 | - | working list | none | no | procedure |
| FX-ARG-18 | In list mode, no user confirmation between issues. | invariant | L90 | F1-071 | - | - | none | no | procedure |
| FX-ARG-19 | **Up-front validation**: after URL resolution but before any fix, run `bees show-ticket --ids <id1> <id2> ...` on the full post-resolution list. | command | L94 Notes for list mode | F1-073 | validation result | post-resolution list | bees | no | procedure |
| FX-ARG-20 | If any ID does not exist, is not in the `issues` hive, or is not `open`, report the problem IDs and continue with the valid open subset; do not abort the run. | recovery | L94 | F1-074 | user report; trimmed list | `bees show-ticket` output | bees | no | procedure |
| FX-ARG-21 | The failure check is cumulative across both gates: URL-resolution soft-fails AND `bees show-ticket` validation failures both count toward dropped tokens. | invariant | L94 | F1-075 | dropped-token count | FX-ARG-20, FX-ARG-40 | none | no | procedure |
| FX-ARG-22 | Only when *no* tokens remain valid after both gates does the run exit with an error; on the single-URL-token path a soft-fail on the only URL leaves the list empty and this rule fires. | recovery | L94; L156 **Soft-fail on dispatch failure.**; L156 **single-URL-token path** | F1-076, F1-126, F1-128 | run exit | dropped-token count | none | no | procedure |
| FX-ARG-23 | Query open issues only in no-args and `all` modes; list mode uses the user's explicit list. | invariant | L97 | F1-080 | - | mode | bees | no | procedure |
| FX-ARG-24 | Open-issues query (verbatim): `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'`. | command | L98-L102 | F1-081 | open-issue list | Issues hive | bees | no | procedure |
| FX-ARG-25 | If the working list has URL tokens, resolve each to an Issue ticket ID before the upfront `bees show-ticket --ids` validation pass. | ordering | L130 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | F1-101 | resolved IDs | URL tokens | Agent (Skill tool), bees | no | procedure |
| FX-ARG-26 | **File-then-fix transition announcement**: before the per-URL Skill-tool loop, print a short informational line — recommended `Filing URL(s) as Issue(s) first, then fixing.` | relay | L132 **File-then-fix transition announcement.** | F1-104 | console line | URL-token presence | none | no | procedure |
| FX-ARG-27 | The announcement is informational console output, NOT an `AskUserQuestion` gate; it does not block and the user is not asked to confirm. | invariant | L132 | F1-105 | - | - | none | no | procedure |
| FX-ARG-28 | Fire the announcement only when at least one URL token is present; on the all-IDs path suppress it entirely. | gate | L132 | F1-106 | - | URL-token presence | none | no | procedure |
| FX-ARG-29 | For each URL token, iterating in input order, dispatch `/quo-file-issue` inline through the Skill tool. | command | L134 | F1-107 | Skill dispatch per URL | URL tokens | Agent (Skill tool) | no | procedure |
| FX-ARG-30 | This consumes the `## Inline invocation via the Skill tool` contract section of `skills/quo-file-issue/SKILL.md`. | definition | L134 | F1-108 | - | - | none | no | procedure |
| FX-ARG-31 | The dispatch shape mirrors `skills/quo-plan/SKILL.md` sub-step 4b (Skill-tool dispatch of `/quo-write-prd` / `/quo-write-sdd` with free-text `args`, capturing structured return fields). | definition | L134 | F1-109 | - | - | none | no | procedure |
| FX-ARG-32 | Pass `args` as a free-text payload of exactly the shape `url: <url>`. | field-or-template | L134-L138 | F1-110 | Skill `args` | URL token | Agent (Skill tool) | no | procedure |
| FX-ARG-33 | Send only `url: <url>`; leave the OPTIONAL `summary:` field unset so `/quo-file-issue` performs its own `WebFetch` (this skill does not pre-fetch). | invariant | L140 | F1-111 | - | - | none | no | procedure |
| FX-ARG-34 | Capture three fields from `/quo-file-issue`'s structured return per its `### Output shape (this skill → caller)` block. | field-or-template | L142 | F1-112 | captured fields | Skill return | Agent (Skill tool) | no | procedure |
| FX-ARG-35 | **`issue_ticket_id`**: the Issue ticket ID to substitute into the working list. | field-or-template | L144 | F1-113 | working-list substitution | Skill return | none | no | procedure |
| FX-ARG-36 | **`issue_status`**: always `open` on success; the close-out flip to `done` is owned by Section 7, not `/quo-file-issue`. | field-or-template | L145 | F1-114 | - | Skill return | none | no | procedure |
| FX-ARG-37 | **`action`**: exactly `created` or `reused-existing`; informational (consumed by the post-resolution display), NOT load-bearing for substitution — both values yield a valid `issue_ticket_id`. | field-or-template | L146 | F1-115, F1-116 | display input | Skill return | none | no | procedure |
| FX-ARG-38 | Rationale: in-place substitution preserves the "do NOT sort" invariant so a prerequisite filed from an earlier URL is fixed first. | rationale-only | L148 | F1-121 | - | - | none | no | rationale |
| FX-ARG-39 | **Soft-fail on dispatch failure**: drop the failed URL token, report the failure, continue with the remaining tokens; a single dropped URL never aborts the run when other tokens remain. | recovery | L150; L156 | F1-122, F1-127 | user report; trimmed list | dispatch outcome | none | no | procedure |
| FX-ARG-40 | Dispatch failure = the Skill tool itself raises an error. | definition | L152 | F1-123 | - | Skill tool error | Agent (Skill tool) | no | procedure |
| FX-ARG-41 | Dispatch failure = user cancels at a `/quo-file-issue` gate — the distill `Approve` / `Revise` / `Cancel` gate, the External-reference body-confirmation step, or the dedupe disambiguation gate's `Cancel`. | definition | L153 | F1-124 | - | Skill return | AskUserQuestion | no | procedure |
| FX-ARG-42 | Dispatch failure = `/quo-file-issue` returns a non-success structured return. | definition | L154 | F1-125 | - | Skill return | none | no | procedure |
| FX-ARG-43 | **Post-resolution working-list display**: after every URL token is resolved or soft-failed, and BEFORE the upfront `bees show-ticket --ids` pass, display the working list as informational markdown. | relay | L158 **Post-resolution working-list display.** | F1-129 | console markdown | post-resolution list | none | no | procedure |
| FX-ARG-44 | Label each input position with the resolved ticket ID; call out URL positions as filed-from-URL with the captured `action` value. | field-or-template | L158 | F1-130 | display text | `issue_ticket_id`, `action` | none | no | procedure |
| FX-ARG-45 | Recommended display shape: `Post-resolution working list:` then numbered lines like `2. b.<new-id> (input: https://github.com/example/repo/issues/123, action: created)`. | field-or-template | L160-L165 | F1-131 | display text | - | none | no | procedure |
| FX-ARG-46 | The display is informational ONLY — NO `AskUserQuestion`, NO ability to re-order. | invariant | L167 | F1-132 | - | - | none | no | procedure |
| FX-ARG-47 | Rationale: the display lets the user confirm prerequisite ordering survived; if unhappy they `Ctrl-C` and re-run. | rationale-only | L167 | F1-133 | - | - | none | no | rationale |
| FX-ARG-48 | Fire the display only when at least one URL token was in the input; suppress on the all-IDs path. | gate | L167 | F1-134 | - | URL-token presence | none | no | procedure |
| FX-ARG-49 | **End of URL-resolution sub-step**: continue at the upfront `bees show-ticket --ids` validation pass, then `#### Write the run-state manifest`, then Step 2. | ordering | L169 | F1-135 | - | - | bees | no | procedure |
| FX-ARG-50 | The skill's steps are: 2 (Validate Issue), 3 (design analysis), 4 (per-issue Agent dispatch), 5 (review loop), 6 (doc verify), 7 (mark done + commit), 8 (post-completion review), 9 (GitHub close commands). | definition | L169 | F1-136 | - | - | none | no | procedure |
| FX-ARG-51 | The URL-resolution sub-step replaces nothing else in the flow. | invariant | L169 | F1-137 | - | - | none | no | procedure |
| FX-ARG-52 | Each `/quo-file-issue` structured return is a hand-off marker (per its `### Behavioral guarantees` "hand-off marker, not a workflow exit"), NOT a signal that the run has terminated. | invariant | L169 | F1-138 | - | Skill return | none | no | procedure |
| FX-ARG-53 | URL-resolution Skill-tool dispatches run before per-issue dispatch, so their TaskList entries use a positional-index discriminator instead of an Issue id. | name-class | L583 TNC | F3-253 | - | - | TaskList | no | procedure |
| FX-ARG-54 | TaskList name for URL-resolution dispatches: `file-from-url-<n>`, `<n>` the 1-based index of the URL token in the positional-argument list (`file-from-url-1`, `file-from-url-2`); index, not URL, gives determinism. | name-class | L590 TNC | F3-270 | TaskList task name | positional args | TaskList | no | procedure |
| FX-ARG-55 | `file-from-url-<n>` lifecycle: `pending` when deciding to dispatch; `in_progress` when the Skill dispatch lands; `completed` when `issue_ticket_id` is captured (`action` `created` or `reused-existing` via `Use existing`). | definition | L590 TNC | F3-271 | task status | Skill return | TaskList | no | procedure |
| FX-ARG-56 | On URL-resolution soft-fail or user-cancel, mark the `file-from-url-<n>` entry `completed` (failure reason in `metadata.activity` if useful) and clear it, so the cumulative failure check at validation sees a clean active set. | recovery | L590 TNC | F3-272 | task `completed` | - | TaskList, bees | no | procedure |

---

## 4. ISO — Isolation strategy

- **Purpose:** Before validating or fixing any Issue, settle where the run's one-commit-per-Issue lands (worktree / new local branch / current branch), prompting only where the mode makes surprise commits likely.
- **Failure it prevents:** Landing many fix commits on `main` (or a feature branch, in batch mode) without confirmation — hard to undo (F1-083, F1-088).
- **Env deps:** git, AskUserQuestion. **TaskList-dependent: no** (the isolation prompt is described without a gate task — see Inconsistencies).
- **Rows:** 15 (procedure 12, rationale 3).
- **Literals:** `#### Validate isolation strategy`; **Scenario A — Already in a worktree.**; **Scenario B — On an existing branch in the main repo.**; `main` / `master`; options **Create a feature branch (Recommended for `all` mode and list mode)**, **Work on current branch**, **Set up a worktree instead**; branch examples `fix/issues-<short-slug>`, `fix/<id1>-<id2>`; worktree name hints `fix-issues`, `bug-sweep`; `/bees-worktree-add`.
- **Edges:** Runs after ARG parsing and before ARG's URL resolution (F1-101/F1-102); Produces the `Isolation strategy` field for MAN; mirrors `/quo-execute`'s isolation block.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ISO-1 | After parsing/resolving which issues to fix, but **before** validating any Issue or dispatching any per-issue Agent, check whether you are in an isolated context. | ordering | L106 `#### Validate isolation strategy` | F1-082 | - | cwd, branch | git | yes | procedure |
| FX-ISO-2 | Rationale: fixes produce one commit per issue, so landing them on the wrong branch is hard to undo. | rationale-only | L106 | F1-083 | - | - | git | yes | rationale |
| FX-ISO-3 | Mirror `/quo-execute`'s isolation block. | invariant | L106 | F1-084 | - | - | none | yes | procedure |
| FX-ISO-4 | **Scenario A — Already in a worktree** whose directory name suggests issue-fix work (e.g. `fix-issues`, `bug-sweep`, a fix-issue slug): proceed directly, no action. | gate | L108 | F1-085 | - | worktree dir name | git | yes | procedure |
| FX-ISO-5 | **Scenario B — On an existing branch in the main repo** (not a worktree): behavior depends on mode and current branch. | definition | L110 | F1-086 | - | mode, branch | git | yes | procedure |
| FX-ISO-6 | If on `main` (or `master`), **always** prompt with `AskUserQuestion`, regardless of mode. | gate | L112 | F1-087 | isolation prompt | branch name | AskUserQuestion, git | yes | procedure |
| FX-ISO-7 | Rationale: landing many commits on main without confirmation is the surprise this prompt prevents. | rationale-only | L112 | F1-088 | - | - | none | yes | rationale |
| FX-ISO-8 | If on a feature branch in single-issue mode, proceed silently. | gate | L113 | F1-089 | - | branch, mode | git | yes | procedure |
| FX-ISO-9 | If on a feature branch in `all` mode or list mode, prompt with `AskUserQuestion`. | gate | L114 | F1-090 | isolation prompt | branch, mode | AskUserQuestion, git | yes | procedure |
| FX-ISO-10 | Option 1 **Create a feature branch (Recommended for `all` mode and list mode)**: create a local branch only (e.g. `fix/issues-<short-slug>` or `fix/<id1>-<id2>`) from current HEAD — no remote push; commit all fixes there. | choice-set | L118 | F1-091, F1-092 | new local branch | user answer | AskUserQuestion, git | yes | procedure |
| FX-ISO-11 | Option 2 **Work on current branch**: commit directly to the checked-out branch and tell the user the branch name. | choice-set | L119 | F1-093 | commits on current branch; branch-name relay | user answer | AskUserQuestion, git | yes | procedure |
| FX-ISO-12 | Option 3 **Set up a worktree instead**: offered only if `/bees-worktree-add` is installed (omit otherwise); suggest running it to spawn the session in an isolated worktree (fire-and-forget in a separate tmux session); on this choice exit after the advice — do not proceed. | choice-set | L120 | F1-094, F1-095, F1-096 | advice; run exit | installed-skill check; user answer | AskUserQuestion | yes | procedure |
| FX-ISO-13 | The isolation question must always state: the current working directory, the current branch name, that option 1 creates a local branch only (no remote push), and the number of issues queued (commit-volume implication). | field-or-template | L122-L126 | F1-097, F1-098, F1-099, F1-100 | question text | cwd, branch, working list length | AskUserQuestion, git | yes | procedure |
| FX-ISO-14 | The isolation-strategy choice applies to the entire run, including the file-then-fix transition the URL-resolution sub-step initiates. | invariant | L130 | F1-102 | - | isolation choice | git | no | procedure |
| FX-ISO-15 | Rationale: isolating before resolution lets the user opt into a fresh branch that scopes the file-from-URL commits. | rationale-only | L130 | F1-103 | - | - | none | no | rationale |

---

## 5. MAN — Run-state manifest

- **Purpose:** Persist, in one deterministic-named markdown file, the run-scoped values that live nowhere else on disk (ordered batch, isolation choice, pre-session SHA, tracker path, progress, next unit) so a harness compaction is survivable by re-reading rather than recalling.
- **Failure it prevents:** After compaction, trusting a summary; scoping Section 8's diff from a foreign checkout's SHA when two same-basename checkouts collide (F1-159, F7-024); growing a shadow ticket store that drifts (F1-167).
- **Env deps:** Bash, git, bees, TaskList (only in the "what the manifest does not hold" enumeration). **TaskList-dependent: no** (the manifest is a file; TaskList is named only as a sibling carrier).
- **Rows:** 45 (procedure 33, rationale 10, example 1, failure-narrative 1).
- **Literals:** `#### Write the run-state manifest`; path `<tempdir>/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md`; `git rev-parse --show-toplevel`; `git rev-parse HEAD`; title `# Run state — quo-fix-issue @ <repo-dir-name>`; fields `**Skill:** quo-fix-issue`, `**Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>`, `**Unit scope:** ordered Issue batch: …`, `**Isolation strategy:** <branch created: <name> | current branch: <name> | worktree: <path>>`, `**Pre-session SHA:** <pre-session-sha>`, `**Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`, `**Progress:**` lines `- <issue-id>: done — commit <sha>`, `**Next unit:** <next-issue-id | none>`; `HEAD~N` fallback; bolded lead statements **nowhere else on disk**, **The filename is deterministic — do NOT add a random suffix or timestamp.**, **Semantics: truncate at run start, rewrite at each boundary.**, **live snapshot, not an accumulating log**, **only values that have no other durable home**.
- **Edges:** Consumes ARG (batch), ISO (strategy), TRACK (tracker path generated here), CKPT (rewrites it each boundary), SHELL (path/dir/Write/no-delete conventions); Produces `Pre-session SHA` for POSTC step 1 and GH, `Unit scope` for its own validation in LOOP/CKPT/POSTC, tracker path recovery for SUM.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-MAN-1 | `#### Write the run-state manifest` is the **canonical definition site**; later sections refer to it by name. | definition | L173 | F1-139 | - | - | none | unknown | procedure |
| FX-MAN-2 | Write the manifest as the last step of Section 1 — after list parsing, URL resolution, upfront `bees show-ticket --ids` validation, and isolation settlement — before validating or fixing any Issue. | ordering | L173 | F1-140 | manifest file | working list, isolation choice | Bash, git | unknown | procedure |
| FX-MAN-3 | The manifest is a small markdown file holding the run-scoped values that live **nowhere else on disk**; it holds the ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress, and next unit. | definition | L175; L386 RL | F1-141, F3-012 | - | - | none | yes (lead) | procedure |
| FX-MAN-4 | bees holds ticket state, git the diff, the compromise tracker accepted compromises, the `defer-*` TaskList open deferrals; the manifest holds only what those four do not. | invariant | L175 | F1-142 | - | - | bees, git, TaskList | yes (lead; "four" is fix-issue/execute-specific) | procedure |
| FX-MAN-5 | After a harness compaction, re-read the manifest instead of trusting a summary — this is what makes compaction survivable. | recovery | L175 | F1-143 | - | manifest file | none | yes | procedure |
| FX-MAN-6 | Write the manifest under the scratch-file convention in `<tempdir>/.quorum/` (`/tmp/.quorum/` POSIX, `%TEMP%\.quorum` Windows). | definition | L177 **Path and filename.** | F1-144 | manifest path | tempdir | Bash | yes | procedure |
| FX-MAN-7 | Canonical filename: `run-state-quo-fix-issue-<repo-dir-name>.md`. | name-class | L177 | F1-145 | manifest filename | `<repo-dir-name>` | none | no | procedure |
| FX-MAN-8 | `<repo-dir-name>` is the **basename of this run's repository working directory** — the last path segment of the working tree root. | definition | L177 | F1-146 | `<repo-dir-name>` | working tree root | git | no | procedure |
| FX-MAN-9 | Example: a run inside `/home/dev/projects/widget-api` writes `run-state-quo-fix-issue-widget-api.md`. | example | L177 | F1-147 | - | - | none | no | example |
| FX-MAN-10 | Resolve the working tree root with one literal command `git rev-parse --show-toplevel` (identical on POSIX and PowerShell) and take its last path segment; the path is thus recomputable from the working directory alone — never remembered. | command | L177-L187; L386 RL; L1124 PC step 1 | F1-148, F3-014, F7-019 | working tree root | git repo | Bash, git | no | procedure |
| FX-MAN-11 | **The filename is deterministic — do NOT add a random suffix or timestamp.** | invariant | L203 | F1-151 | - | - | none | yes (lead) | procedure |
| FX-MAN-12 | Rationale: unlike the compromise tracker's `<short-suffix>` (reader is an Agent handed the path), the manifest's reader is the orchestrator post-compaction, so a random suffix would be unfindable. | rationale-only | L203 | F1-152 | - | - | none | yes (comparison omitted in breakdown-epic) | rationale |
| FX-MAN-13 | Rationale: the key must be recomputable from the working directory alone; **An Issue ID does not** qualify because batch membership is recorded only inside the manifest and commit subjects cannot recover the first Issue. | rationale-only | L205 **Why the key is skill name plus repo directory — and not an Issue ID.** | F1-153 | - | - | git | no | rationale |
| FX-MAN-14 | Rationale: the skill-name segment prevents collision with a sibling skill's manifest; the repo-directory segment keeps two projects from *normally* colliding in the machine-wide `<tempdir>/.quorum/`. | rationale-only | L205 | F1-154 | - | - | none | no | rationale |
| FX-MAN-15 | Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends. | invariant | L205 | F1-155 | - | - | none | yes (lead) | procedure |
| FX-MAN-16 | `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has; `/quo-fix-issue` appends the repository directory basename. | definition | L205 | F1-156 | - | - | none | no | procedure |
| FX-MAN-17 | Accepted collision: **Two concurrent `/quo-fix-issue` runs in the same working directory** share one filename; the later truncating write wins (such runs already collide over statuses and commits). | definition | L209 | F1-157 | - | - | none | no | rationale |
| FX-MAN-18 | Accepted collision: **Two different checkouts whose directories share a basename** land on one file; a live second run's truncating write replaces the first's manifest. | definition | L210 | F1-158 | - | - | none | no | rationale |
| FX-MAN-19 | Consequence of the basename collision: the other checkout's **Pre-session SHA** (possibly nonexistent here) reaches Section 8 and scopes its diff wrongly; a **Unit scope** mismatch is the stale/foreign-manifest tell. Sequential runs are unaffected. | failure-narrative | L210; L1124 PC step 1 | F1-159, F7-024 | - | **Pre-session SHA** | git | no | failure-narrative |
| FX-MAN-20 | **Validate the manifest before trusting any field**: compare its **Unit scope** ordered Issue batch against the batch this run is fixing (at every read: Read-state tick, checkpoint step 1, Section 8 step 1). | precondition | L386 RL; L847 CKPT; L1124 PC step 1 | F3-015, F5-164, F7-022 | - | manifest `Unit scope`; run batch | none | unknown | procedure |
| FX-MAN-21 | If the manifest names Issues this run is not working (or is missing), treat it as absent: never read a foreign `<pre-session-sha>`, isolation strategy, or tracker path; bound SHA-scoped checks with `HEAD~N` where N = Issues fixed so far this run (one commit per Issue per Section 7 step 2.4); let the next checkpoint rewrite the manifest from this run's batch. | recovery | L210; L386 RL; L847 CKPT; L1124 PC step 1 | F1-160, F3-016, F5-165, F7-021, F7-023 | `<pre-session-sha>` (fallback) | manifest comparison; fixed-Issue count | git | no | procedure |
| FX-MAN-22 | Rationale: alternative keys are worse — an absolute path is unwieldy and leaks directory structure into `<tempdir>`; an Issue ID is not recomputable. | rationale-only | L210 | F1-161 | - | - | none | no | rationale |
| FX-MAN-23 | **Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. | invariant | L212 | F1-162 | - | - | none | yes (lead) | procedure |
| FX-MAN-24 | Write the manifest fresh at run start, overwriting any manifest left by a previous `/quo-fix-issue` run in this repository directory. | ordering | L212 | F1-163 | manifest (truncated) | - | none | no | procedure |
| FX-MAN-25 | The manifest carries **only values that have no other durable home**; do not add Issue bodies, design directives, or review findings. | invariant | L214 **Contents — and an invariant that bounds them.** | F1-166 | - | - | none | yes | procedure |
| FX-MAN-26 | Rationale: duplicating bees/tracker/diff content would grow the manifest into a shadow ticket store that drifts. | rationale-only | L214 | F1-167 | - | - | none | yes | rationale |
| FX-MAN-27 | Title line: `# Run state — quo-fix-issue @ <repo-dir-name>`. | field-or-template | L217 | F1-168 | manifest field | `<repo-dir-name>` | none | no | procedure |
| FX-MAN-28 | Field `**Skill:** quo-fix-issue`. | field-or-template | L219 | F1-169 | manifest field | - | none | no | procedure |
| FX-MAN-29 | Field `**Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>`. | field-or-template | L220 | F1-170 | manifest field | clock | none | no | procedure |
| FX-MAN-30 | Field `**Unit scope:** ordered Issue batch: <issue-id-1>, <issue-id-2>, ...` — recorded verbatim in post-resolution order. | field-or-template | L221; L234 | F1-171, F1-184 | manifest field | post-resolution working list | none | no | procedure |
| FX-MAN-31 | Rationale: the batch order is user-supplied and intentional and cannot be re-derived from bees after compaction. | rationale-only | L234 | F1-185 | - | - | none | no | rationale |
| FX-MAN-32 | Field `**Isolation strategy:** <branch created: <name> \| current branch: <name> \| worktree: <path>>`. | field-or-template | L222 | F1-172 | manifest field | isolation choice | git | no | procedure |
| FX-MAN-33 | Field `**Pre-session SHA:** <pre-session-sha>`. | field-or-template | L223 | F1-173 | manifest field | `git rev-parse HEAD` | git | no | procedure |
| FX-MAN-34 | Field `**Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` — the tracker's full path *including* its random `<short-suffix>`. | field-or-template | L224; L230 | F1-174, F1-177 | manifest field | tracker path | none | no | procedure |
| FX-MAN-35 | Generate the tracker filename here, at run start, per Section 7.5 `#### Session-scoped compromise tracker`; timestamp and suffix are generated once per run. | ordering | L230 | F1-178 | tracker path | - | none | no | procedure |
| FX-MAN-36 | The manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. | definition | L230 | F1-179 | - | - | none | no | rationale |
| FX-MAN-37 | Recording the tracker path does not create the tracker file; it is created only when its first append trigger fires. | invariant | L230 | F1-180 | - | - | none | no | procedure |
| FX-MAN-38 | Field `**Progress:**` carries one line per Issue finished, in the order worked: `- <issue-id>: done — commit <sha>` on the fixed path. | field-or-template | L225-L226; L232 | F1-175, F1-181 | manifest field | issue outcomes; commit sha | git | no | procedure |
| FX-MAN-39 | Rationale: recording the aborted shape (FX-CKPT-28) keeps progress readable post-compaction — an Issue absent from Progress is indistinguishable from one not yet reached. | rationale-only | L232 | F1-183 | - | - | none | no | rationale |
| FX-MAN-40 | Field `**Next unit:** <next-issue-id \| none>`. | field-or-template | L227 | F1-176 | manifest field | working list position | none | no | procedure |
| FX-MAN-41 | Capture `<pre-session-sha>` here, at run start, with the one literal command `git rev-parse HEAD` (identical on POSIX and PowerShell); this is the **only** place the run records it. | command | L236-L246 | F1-186, F1-188 | `Pre-session SHA` field | HEAD | Bash, git | unknown | procedure |
| FX-MAN-42 | Section 8 step 1 reads `<pre-session-sha>` back by `Read`ing the manifest's **Pre-session SHA** field, and Section 9 reuses the value Section 8 captured. | definition | L236; L1124 PC step 1 | F1-187, F7-018, F7-020 | `<pre-session-sha>` | `Pre-session SHA` field | none | no | procedure |
| FX-MAN-43 | `Read` the manifest at `<tempdir>/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md` as one of the four Read-state sources on every tick. | command | L386 RL | F3-013 | - | manifest file | none | no | procedure |
| FX-MAN-44 | `<pre-session-sha>` step in Section 8: compute the pre-session diff scope by capturing `<pre-session-sha>` as the HEAD that existed when quo-fix-issue began (read from the manifest, FX-MAN-42). | command | L1124 PC step 1 | F7-017 | `<pre-session-sha>` | run-state manifest | none | unknown | procedure |
| FX-MAN-45 | Do not give the Design Proposal a manifest field (it lives only in the Analyst's returned message; recovery is re-derivation — see RECOV). | invariant | L388 RL | F3-023 | - | manifest | none | no | procedure |

---

## 6. VAL — Issue validation (Section 2)

- **Purpose:** Load the Issue, confirm it is `open` and unblocked (all `up_dependencies` `done`), and skip or exit otherwise.
- **Failure it prevents:** not stated (implicit: fixing a blocked or non-open Issue).
- **Env deps:** Bash, bees. **TaskList-dependent: no.**
- **Rows:** 11 (procedure 11).
- **Literals:** `### 2. Validate Issue`; `bees show-ticket --ids "<issue-id>"`; `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`; `up_dependencies`; `ticket_status`; `open` / `done`; message `Cannot start Issue. It is blocked by: [list]`.
- **Edges:** Consumes ARG's working list and mode; Produces the ticket JSON (body, `reference_materials`, `up_dependencies`) consumed by ANA, PROMPT, SCOPED; skipped Issues are excluded from GH's fixed-issue list.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-VAL-1 | Run `bees show-ticket --ids "<issue-id>"` to load the Issue before validating it. | command | L250-L252 `### 2. Validate Issue` | F2-001 | ticket JSON (body, `up_dependencies`, status) | `<issue-id>` | Bash, bees | unknown | procedure |
| FX-VAL-2 | Check the Issue has a status meaning ready to begin work — `open`. | precondition | L254-L255 | F2-002 | - | `ticket_status` | bees | unknown | procedure |
| FX-VAL-3 | Check the `up_dependencies` array for blockers; every blocker must be in a completed state. | precondition | L256 | F2-003 | - | `up_dependencies` | bees | unknown | procedure |
| FX-VAL-4 | `up_dependencies` is returned as a list of ticket IDs only — not statuses. | definition | L258 | F2-004 | - | `up_dependencies` | bees | unknown | procedure |
| FX-VAL-5 | Collect the dependency IDs and batch-look-up their statuses with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`. | command | L258-L263 | F2-005 | dependency ticket JSON | dependency IDs | Bash, bees | unknown | procedure |
| FX-VAL-6 | For each dependency check `ticket_status`; the Issue is unblocked only if all `up_dependencies` are `done`. | precondition | L265 | F2-006 | blocked/unblocked | `ticket_status` | bees | unknown | procedure |
| FX-VAL-7 | An Issue with no `up_dependencies` is unblocked by default. | precondition | L265 | F2-007 | unblocked | `up_dependencies` (empty) | none | unknown | procedure |
| FX-VAL-8 | If blocked, output the blocking IDs and titles. | relay | L267-L268 | F2-008 | user-visible message | FX-VAL-6 result | none | unknown | procedure |
| FX-VAL-9 | If blocked in batch mode (`all` or list), skip this Issue and continue to the next. | recovery | L269 | F2-009 | skip; advance batch | run mode | none | unknown | procedure |
| FX-VAL-10 | If blocked in single mode, exit with `Cannot start Issue. It is blocked by: [list]`. | recovery | L270 | F2-010 | exit message | run mode; blocker list | none | unknown | procedure |
| FX-VAL-11 | If not blocked, mark the Issue status to signal work has begun (if needed). (Conflicts with FX-CLOSE-29 — see Inconsistencies.) | command | L272-L273 | F2-011 | status flip (conditional) | unblocked result | Bash, bees | unknown | procedure |

---

## 7. ANA — Analyst dispatch & design gate (Section 3)

- **Purpose:** For every Issue, cold-dispatch one Analyst for codebase-grounded design analysis, surface its Design Proposal as prose with a verdict-keyed preamble, and gate implementation on the user's Approve / Revise / Cancel.
- **Failure it prevents:** Treating the Issue body's framing as authoritative design; skipping analysis on a fragile "well-researched enough" heuristic when the cleanest fix is often an option the body did not propose (F2-017, F2-126); paraphrase corrupting identifiers (F2-022); discovering divergence only by careful reading (F2-049).
- **Env deps:** Agent, AskUserQuestion, TaskList, bees. **TaskList-dependent: yes** (`analyst-<issue-id>` tracking, gate task).
- **Rows:** 61 (procedure 52, rationale 9).
- **Literals:** `### 3. Design analysis`; `#### Cold-dispatch the Analyst`; `#### Surface the proposal to the user`; `#### Branch on the user's choice`; `#### Anti-pattern: do not classify the body upfront`; `Agent(subagent_type=analyst, run_in_background=true, prompt=…)`; `analyst-<issue-id>`, `analyst-<issue-id>-rev<n>`; `agents/analyst.md` `## Structured-output contract`; proposal sections `### Problem` / `### Root cause` / `### Recommended approach` / `### Blast radius` / `### Policy decisions this change implies` / `### Why` / `### Alternatives considered` / `### Options the body did not consider` / `### Upstream-fetch status` / `### Deferred refinements`; trailer `Analyst verdict: <…>`; verdicts `recommend-as-stated`, `recommend-with-refinements`, `recommend-different-approach`, `escalate-to-user`; fixed empty lines `No invariant added, removed, or weakened.`, `None — the recommendation leaves no policy question open.`; four preamble templates (FX-ANA-27..30); gate question `How should I proceed with this design proposal?`; options `Approve & proceed to implementation (Recommended)`, `Revise`, `Cancel`; `## Prior proposal and user feedback`; `gate-askuserquestion-veq` example.
- **Edges:** Consumes VAL's ticket JSON; Produces the directive for DIR/PROMPT, the `### Deferred refinements` block for DEFC, the `### Blast radius` for PROMPT relays; Cancel routes to ABORT; re-fires from DQ (design question, `Re-dispatch the Analyst with this finding`) and RECOV (re-derivation); task naming in TASK; gate mechanics in GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ANA-1 | Between Section 2's validation gate and Section 4's implementer dispatch, dispatch a single **Analyst** Agent per Issue for codebase-grounded design analysis. | ordering | L277 `### 3. Design analysis` | F2-012 | Analyst dispatch | Section 2 pass | Agent | no | procedure |
| FX-ANA-2 | Treat the Issue body's framing as **problem-report context, not as authoritative design**. | invariant | L277 | F2-013 | - | Issue body | none | no | procedure |
| FX-ANA-3 | The Analyst returns a Design Proposal; surface it to the user for approval before any Engineer dispatch. | ordering | L277 | F2-014 | user-facing proposal | Analyst return | Agent, AskUserQuestion | no | procedure |
| FX-ANA-4 | Section 3 is **always run** for every Issue. | invariant | L279 | F2-015 | - | - | none | no | procedure |
| FX-ANA-5 | Do NOT pre-judge / short-circuit on a heuristic that the body is "well-researched enough" to skip the Analyst. | invariant | L279; L366 `#### Anti-pattern: do not classify the body upfront` | F2-016, F2-125 | - | - | none | no | procedure |
| FX-ANA-6 | Rationale: body-quality classification is a fragile heuristic (a body citing code paths may be a typo fix; a one-sentence body may sit behind a rich `reference_materials` URL); the cleanest fix is often an option the body did not propose; only the Analyst's research is reliable. | rationale-only | L279; L366 | F2-017, F2-126 | - | - | none | no | rationale |
| FX-ANA-7 | Spawn one fresh Analyst Agent per Issue, scoped per-issue, using the same cold-dispatch shape Section 4 uses for implementer roles. | command | L283 `#### Cold-dispatch the Analyst` | F2-018 | Analyst dispatch | Section 4 shape | Agent | no | procedure |
| FX-ANA-8 | Dispatch template: `Agent(subagent_type=analyst, run_in_background=true, prompt=<dispatch prompt with the issue body embedded verbatim and reference_materials JSON if non-empty>)`. | field-or-template | L285-L291 | F2-019 | Agent call | Issue body, `reference_materials` | Agent | no | procedure |
| FX-ANA-9 | The Analyst dispatch prompt must include the Issue ID. | field-or-template | L293-L295 | F2-020 | prompt field | `<issue-id>` | Agent | no | procedure |
| FX-ANA-10 | The prompt must include framing prose naming the Analyst's lane: codebase-grounded design proposal, structured output, never directly modifying files. | field-or-template | L298 | F2-025 | prompt field | - | Agent | no | procedure |
| FX-ANA-11 | The Analyst runs in the background like every other dispatched Agent in this skill. | definition | L302 | F2-029 | - | - | Agent | no | procedure |
| FX-ANA-12 | The orchestrator MUST wait for the Analyst's completion notification before proceeding to the approval gate. | ordering | L302 | F2-030 | - | Agent completion notification | Agent | no | procedure |
| FX-ANA-13 | Do not dispatch Section 4 implementer Agents until the Analyst has returned and the user has approved — Section 4 is gated on this approval. | ordering | L302 | F2-031 | - | Analyst return; Approve | Agent, AskUserQuestion | no | procedure |
| FX-ANA-14 | When the completion notification fires, read the Analyst's return — the structured Design Proposal per `agents/analyst.md` `## Structured-output contract`. | command | L306 `#### Surface the proposal to the user` | F2-032 | - | Agent return | Agent | no | procedure |
| FX-ANA-15 | Mark the `analyst-<issue-id>` (or `-rev<n>`) task `completed` the moment its return is read, before surfacing and before creating the gate task. On Approve or Revise there is therefore nothing to close out. | ordering | L306; L329; L333 | F2-033, F2-076, F2-084 | task `completed` | Analyst task | TaskList | no | procedure |
| FX-ANA-16 | Rationale: the Agent has exited; leaving its task active would strand a task no completion notification will ever clear. | rationale-only | L306 | F2-034 | - | - | none | no | rationale |
| FX-ANA-17 | The proposal is **free-form analysis**: Problem / Root cause / Recommended approach / Blast radius / Policy decisions this change implies / Why / Alternatives considered / Options the body did not consider / Upstream-fetch status / verdict trailer. | definition | L306 | F2-037 | - | Analyst return | none | no | procedure |
| FX-ANA-18 | Surface the proposal as prose, NOT as an `AskUserQuestion` body. | invariant | L306 | F2-038 | user-visible prose | Analyst return | none | no | procedure |
| FX-ANA-19 | Rationale: `AskUserQuestion` is for finite-multi-choice gates, not free-text design recommendations. | rationale-only | L306 | F2-039 | - | - | AskUserQuestion | no | rationale |
| FX-ANA-20 | **Unlike `### Deferred refinements`, the `### Blast radius` and `### Policy decisions this change implies` sections ARE surfaced** — in full. | relay | L306 | F2-040 | user-visible sections | Analyst sections | none | no | procedure |
| FX-ANA-21 | Surface their fixed empty lines (`No invariant added, removed, or weakened.` / `None — the recommendation leaves no policy question open.`) when the Analyst emitted them. | relay | L306 | F2-041 | user-visible lines | Analyst return | none | no | procedure |
| FX-ANA-22 | Rationale: surfacing the fixed empty lines lets the user tell "swept and found nothing" from "never swept". | rationale-only | L306 | F2-042 | - | - | none | no | rationale |
| FX-ANA-23 | **Extract the verdict**: before surfacing the body, read the `Analyst verdict: <…>` trailer line. | command | L308 | F2-046 | verdict value | trailer | none | no | procedure |
| FX-ANA-24 | Use the verdict to shape a one- or two-sentence prose preamble that precedes the proposal. | relay | L308 | F2-047 | preamble | verdict | none | no | procedure |
| FX-ANA-25 | Structural rule: divergent verdicts surface divergence prominently (phrasing may be adjusted to fit context). | invariant | L308 | F2-048 | preamble | verdict | none | no | procedure |
| FX-ANA-26 | Rationale: the verdict is a load-bearing framing signal — the user should encounter divergence up front. | rationale-only | L308 | F2-049 | - | - | none | no | rationale |
| FX-ANA-27 | Preamble for **`recommend-as-stated`**: "The Analyst's codebase research agrees with the Issue body's framing. The Recommended approach reflects the body's approach. Proposal follows:" | field-or-template | L310 | F2-050 | preamble | verdict | none | no | procedure |
| FX-ANA-28 | Preamble for **`recommend-with-refinements`**: "…broadly agrees with the Issue body, but the Recommended approach refines the body's framing. The refinements are called out in Why / Alternatives considered. Proposal follows:" | field-or-template | L311 | F2-051 | preamble | verdict | none | no | procedure |
| FX-ANA-29 | Preamble for **`recommend-different-approach`**: "⚠️ The Analyst's codebase research **diverged** from the Issue body's framing. The Recommended approach is an option the body did NOT propose; … Read carefully before approving. Proposal follows:" | field-or-template | L312 | F2-052 | preamble | verdict | none | no | procedure |
| FX-ANA-30 | Preamble for **`escalate-to-user`**: "⚠️ The Analyst could **not converge** on a single recommendation and is escalating the open question(s) to you. … Proposal follows:" | field-or-template | L313 | F2-053 | preamble | verdict | none | no | procedure |
| FX-ANA-31 | When `### Policy decisions this change implies` is non-empty (anything other than its fixed empty line), the preamble MUST name **how many** decisions and point at the section. | relay | L315 | F2-054 | preamble | policy section | none | no | procedure |
| FX-ANA-32 | Rationale: naming the count tells the user Approve ratifies the Analyst's recommended answers along with the design. | rationale-only | L315 | F2-055 | - | - | none | no | rationale |
| FX-ANA-33 | When `### Blast radius` carries a **scope-split recommendation**, the preamble says one is carried and points at that section. | relay | L315 | F2-056 | preamble | `### Blast radius` | none | no | procedure |
| FX-ANA-34 | A scope-split recommendation means: fold the distinct concern into this Issue, or file it separately and only document the property here. | definition | L315 | F2-057 | - | `### Blast radius` | none | no | procedure |
| FX-ANA-35 | Policy decisions and scope-split ride the existing preamble and the existing Approve / Revise / Cancel gate — do **not** add a second gate, extra option, or separate task. | invariant | L315 | F2-058 | - | - | AskUserQuestion, TaskList | no | procedure |
| FX-ANA-36 | The preamble is the orchestrator's responsibility, not the Analyst's; the Analyst returns the verdict, the orchestrator turns it into framing. | invariant | L317 | F2-059 | preamble | verdict | none | no | procedure |
| FX-ANA-37 | Rationale: the split keeps framing consistent across runs while the Analyst stays focused on design substance. | rationale-only | L317 | F2-060 | - | - | none | no | rationale |
| FX-ANA-38 | After preamble and body are surfaced, present a finite-multi-choice gate via `AskUserQuestion`. | gate | L319 | F2-061 | gate | preamble, prose | AskUserQuestion | no | procedure |
| FX-ANA-39 | **This gate is trailer-less** — the Analyst's return embeds no routing trailer; the orchestrator prose is the source of the prescription. | definition | L319 | F2-062 | - | - | none | no | procedure |
| FX-ANA-40 | Gate question text: "How should I proceed with this design proposal?" | field-or-template | L321 | F2-067 | question | - | AskUserQuestion | no | procedure |
| FX-ANA-41 | Option `Approve & proceed to implementation (Recommended)`: accept the Recommended approach as the authoritative design directive for this Issue. | choice-set | L322-L323 | F2-068 | option | - | AskUserQuestion | no | procedure |
| FX-ANA-42 | Approval covers the design, the Analyst's recommended answer to every question in `### Policy decisions this change implies`, and any scope-split recommendation in `### Blast radius`. | definition | L323 | F2-069 | - | proposal sections | none | no | procedure |
| FX-ANA-43 | Option `Revise`: user has feedback; iterate in prose (free-text reply), then optionally re-dispatch the Analyst with the feedback as context. | choice-set | L324 | F2-071 | option | - | AskUserQuestion, Agent | no | procedure |
| FX-ANA-44 | Option `Cancel`: exit cleanly without dispatching any implementer Agent; no commit is made; the Issue stays `open` (routing in ABORT). | choice-set | L325 | F2-072 | option | - | AskUserQuestion | no | procedure |
| FX-ANA-45 | After Approve processing, proceed to Section 4. | ordering | L329 `#### Branch on the user's choice` | F2-081 | - | - | none | no | procedure |
| FX-ANA-46 | On **Revise**, continue the conversation in prose and engage with feedback such as "I disagree with X because…" or "have you considered Y?". | relay | L331 | F2-082 | conversation | user feedback | none | no | procedure |
| FX-ANA-47 | When feedback warrants a fresh codebase pass (substantively different approach, specific code path to investigate), **re-dispatch the Analyst** as a fresh cold invocation. | command | L331 | F2-083 | new Analyst dispatch | user feedback | Agent | no | procedure |
| FX-ANA-48 | The re-dispatch prompt embeds the same Issue body verbatim and `reference_materials`, PLUS a clearly-labeled `## Prior proposal and user feedback` section; the design-question rung re-dispatches with exactly this shape under the next `analyst-<issue-id>-rev<n>` name. | field-or-template | L335; L452 RL | F2-086, F3-157 | prompt section | Issue body; `reference_materials`; prior proposal; feedback | Agent | no | procedure |
| FX-ANA-49 | `## Prior proposal and user feedback` quotes the prior Design Proposal in full and the user's revision feedback verbatim. | field-or-template | L335 | F2-087 | prompt content | prior return; feedback | Agent | no | procedure |
| FX-ANA-50 | **"In full" includes the prior proposal's `### Deferred refinements` block**, even though the surfacing step stripped it from user-facing prose (also on the design-question re-dispatch). | invariant | L335; L452 RL | F2-088, F3-158 | prompt content | prior `### Deferred refinements` | Agent | no | procedure |
| FX-ANA-51 | Rationale: the revising Analyst needs the prior deferrals to carry each forward or explicitly drop it; supersede-and-clear clears the superseded `defer-*` tasks, so an omitted deferral is dropped with no carrier. | rationale-only | L335 | F2-089 | - | - | none | no | rationale |
| FX-ANA-52 | When the re-dispatched Analyst returns, repeat the surface-and-gate flow. | ordering | L336 | F2-090 | re-fired gate | new return | Agent, AskUserQuestion, TaskList | no | procedure |
| FX-ANA-53 | No fixed cap on revision count; the user terminates the loop by picking Approve or Cancel. | invariant | L337 | F2-091 | - | user choice | AskUserQuestion | no | procedure |
| FX-ANA-54 | When feedback is light (wording tweak, terminology clarification, "yes please proceed with refinement X you mentioned in Alternatives"), carry it directly into the Approve branch without re-dispatching. | recovery | L339 | F2-092 | Approve-branch entry | user feedback | none | no | procedure |
| FX-ANA-55 | Always dispatch the Analyst; its verdict (`recommend-as-stated` / `recommend-with-refinements` / `recommend-different-approach` / `escalate-to-user`) IS the classification. | invariant | L366 | F2-127 | - | verdict | Agent | no | procedure |
| FX-ANA-56 | Rationale: when the body IS well-researched the Analyst converges cheaply (prompt-caching helps) and the Approve gate fires cheaply — overhead is bounded. | rationale-only | L366 | F2-128 | - | - | none | no | rationale |
| FX-ANA-57 | While the gate is open the pending decision is carried by the `gate-askuserquestion-*` task (`metadata.activity` holds the finite choices); once a branch is entered it is carried by the conversation — the state Section 4's Read-state step re-derives after compaction. | definition | L306 | F2-035, F2-036 | `metadata.activity` | gate task | TaskList | no | procedure |
| FX-ANA-58 | This gate's two-step instance: **first** create `gate-askuserquestion-<short-suffix>` naming the Analyst-proposal gate, **then** `AskUserQuestion` in the same turn; do not narrate; mark `completed` once the branch is entered (generic form FX-GATE-1/2/3). | ordering | L319 | F2-063, F2-065, F2-066 | gate task; AskUserQuestion | - | TaskList, AskUserQuestion | unknown | procedure |
| FX-ANA-59 | On **Approve**, capture the Analyst's Design Proposal as the run's authoritative design directive for this Issue (composition in DIR). | command | L329 | F2-073 | design directive | Analyst return | none | no | procedure |
| FX-ANA-60 | On Approve, carry the directive into Section 4's implementer dispatch — the Engineer prompt when source needs modification, Test Writer and Doc Writer dispatches otherwise per Section 4's conditional-dispatch rules (see Inconsistencies vs FX-PROMPT-12). | relay | L323; L329 | F2-070, F2-077 | directive in dispatch prompt | Approve | Agent | no | procedure |
| FX-ANA-61 | Light-revision Approve: capture the original directive sections plus the user's clarification in the directive flowing to Section 4. | command | L339 | F2-093 | directive (with clarification) | FX-DIR rows; clarification | none | no | procedure |

---

## 8. DEFC — Deferred-refinements consumption

- **Purpose:** Consume the Analyst's `### Deferred refinements` block (never shown to the user) at the moment of Approve into `defer-*` ledger tasks, superseding unapproved iterations' tasks and preserving earlier-Approve tasks.
- **Failure it prevents:** Refinements the Engineer will not implement being lost between sessions; a re-fire clearing banked refinements from an earlier approval (F2-114); the Analyst lane of the 7.5 gate firing empty (F2-116).
- **Env deps:** TaskList. **TaskList-dependent: yes.**
- **Rows:** 19 (procedure 14, rationale 5).
- **Literals:** `### Deferred refinements`; `#### Consume the Analyst's `### Deferred refinements` block`; `None`; destination annotations `defer-to-existing-ticket-body: <ticket-id>`, `defer-to-new-Issue`, `addressed-now-in-this-Issue`; `defer-<short-suffix>`; `metadata.activity`; supersede-and-clear.
- **Edges:** Consumes ANA's return and Approve event (incl. re-fires from DQ); Produces `defer-*` tasks for LEDGER/HYG (Step 0 surface 3, Step 1); on Cancel produces nothing (deferrals travel with the next Analyst pass).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-DEFC-1 | The Analyst's `### Deferred refinements` block is **consumed by the orchestrator and NOT surfaced to the user**. | invariant | L306 | F2-043 | - | block | none | no | procedure |
| FX-DEFC-2 | Strip the `### Deferred refinements` block from the surfaced proposal before rendering the user-visible prose. | command | L306 | F2-044 | stripped prose | Analyst return | none | no | procedure |
| FX-DEFC-3 | The paragraph "Consume the Analyst's `### Deferred refinements` block" is the load-bearing site for that consumption. | definition | L306 | F2-045 | - | - | none | no | rationale |
| FX-DEFC-4 | Independently of Approve / Revise / Cancel routing, the Analyst's return carries a `### Deferred refinements` block per `agents/analyst.md`'s return-shape contract. | definition | L345 | F2-101 | - | Analyst return | none | no | procedure |
| FX-DEFC-5 | On verdicts `recommend-as-stated` and `escalate-to-user` the block is structurally `None`; on `recommend-with-refinements` and `recommend-different-approach` it is a bulleted list of refinements. | definition | L345 | F2-102 | - | verdict; block | none | no | procedure |
| FX-DEFC-6 | Rationale: the block is the load-bearing inter-session carrier for refinements the Analyst surfaces but the Engineer will not implement in this fix. | rationale-only | L345 | F2-103 | - | - | none | no | rationale |
| FX-DEFC-7 | **At the moment of user approval** (original Approve, Approve after a Revise iteration, or Approve after a part (c)/(d) re-fire), walk the latest return's `### Deferred refinements` block. | ordering | L347 | F2-104 | - | Approve; latest return | none | no | procedure |
| FX-DEFC-8 | Create one `defer-<short-suffix>` task per non-`None` bullet whose destination annotation is `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. | command | L347 | F2-105 | `defer-*` tasks | annotated bullets | TaskList | no | procedure |
| FX-DEFC-9 | The `defer-*` task's `metadata.activity` carries the bullet's one-line description. | field-or-template | L347 | F2-106 | `metadata.activity` | bullet text | TaskList | no | procedure |
| FX-DEFC-10 | Bullets annotated `addressed-now-in-this-Issue` are NOT added to the `defer-*` ledger. | invariant | L347 | F2-107 | - | annotation | TaskList | no | procedure |
| FX-DEFC-11 | Rationale: `addressed-now-in-this-Issue` refinements roll into the `### Recommended approach` flowing into the Engineer dispatch and need no inter-session carrier. | rationale-only | L347 | F2-108 | - | - | none | no | rationale |
| FX-DEFC-12 | Bullets without a destination annotation are a contract violation; surface that to the user as a malformed return rather than guessing a destination. | recovery | L347 | F2-109 | malformed-return report | annotation | none | no | procedure |
| FX-DEFC-13 | On any re-dispatch (Revise iteration or part (c)/(d) re-fire), consume only the **latest** Analyst's block at Approve; prior blocks are superseded. | invariant | L349 | F2-110 | - | latest `-rev<n>` return | none | no | procedure |
| FX-DEFC-14 | **Supersession clears only the `defer-*` tasks of an iteration the user never approved** (a Revise chain's rejected iterations). | invariant | L349 | F2-111 | - | unapproved-iteration tasks | TaskList | no | procedure |
| FX-DEFC-15 | Mark superseded `defer-*` tasks `completed` with `metadata.activity` annotated as superseded before consuming the approved iteration's block. | ordering | L349 | F2-112 | `completed`; annotation | FX-DEFC-14 set | TaskList | no | procedure |
| FX-DEFC-16 | **`defer-*` tasks created at an earlier *Approve* survive a later re-fire** and stay in the active set. | invariant | L349 | F2-113 | - | earlier-Approve tasks | TaskList | no | procedure |
| FX-DEFC-17 | Rationale: the earlier approval still stands; the re-fired Analyst is briefed on the reviewer's finding so its block may be `None`; 7.5 Step 1 enumerates only active tasks and Step 0 walks only the latest block; clearing would destroy every banked refinement. | rationale-only | L349 | F2-114 | - | - | none | no | rationale |
| FX-DEFC-18 | On Cancel, create no `defer-*` tasks from the block; the Issue stays `open` and deferrals travel with the next Analyst pass when `/quo-fix-issue` is re-run. | invariant | L349 | F2-115 | - | Cancel | TaskList | no | procedure |
| FX-DEFC-19 | Rationale: this consumption paragraph is the load-bearing source for the Analyst-lane portion of the 7.5 deferral-hygiene gate; without it the gate fires empty for that lane. | rationale-only | L351 | F2-116 | - | - | none | no | rationale |

---

## 9. DIR — Design directive (composition & precedence)

- **Purpose:** Define what the approved directive consists of (three directive sections, three context sections, any light-revision clarification) and that it wins over the Issue body's framing.
- **Failure it prevents:** not stated (implicit: Engineer implementing the body's framing instead of the approved design).
- **Env deps:** none / Agent. **TaskList-dependent: no.**
- **Rows:** 8 (procedure 8).
- **Literals:** `#### Authoritative design directive (carried into Section 4)`; `### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies` (directive side); `### Why`, `### Alternatives considered`, `### Options the body did not consider` (context side); `agents/engineer.md` **Authoritative design directive (fix mode only)**.
- **Edges:** Consumes ANA's Approve; Produces the directive PROMPT embeds (FX-PROMPT-8..12) and ROUTE reads as "the approved design" for mechanism detection (FX-ROUTE-47).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-DIR-1 | The directive includes the Analyst's `### Recommended approach` section verbatim. | field-or-template | L329; L355-L357 | F2-074, F2-117 | directive component | Analyst return | none | no | procedure |
| FX-DIR-2 | The directive includes `### Blast radius` and `### Policy decisions this change implies` verbatim, on the **directive** side (enumerated site list; policy answers the user ratified) — all three directive, not context. | field-or-template | L329; L358 | F2-074, F2-118 | directive component | Analyst return | none | no | procedure |
| FX-DIR-3 | The directive also carries `### Why`, `### Alternatives considered`, and `### Options the body did not consider` as context the Engineer may consult for trade-offs and rejected alternatives. | field-or-template | L329; L359 | F2-075, F2-119 | directive component | Analyst return | none | no | procedure |
| FX-DIR-4 | The directive includes any user-supplied refinement captured on the Approve branch from a "light enough to incorporate without a fresh Analyst pass" revision. | field-or-template | L360 | F2-120 | directive component | FX-ANA-61 | none | no | procedure |
| FX-DIR-5 | Section 3's Design analysis gate produces the authoritative design directive; the Engineer dispatch carries it into the implementation pass. | relay | L370 `### 4.` | F3-004 | Engineer dispatch prompt | directive | Agent | no | procedure |
| FX-DIR-6 | Where the body's framing and the directive conflict, **the directive wins**; the body still flows verbatim for byte-accurate identifiers. | invariant | L362; L511 DP | F2-123, F3-194 | - | Issue body; directive | none | no | procedure |
| FX-DIR-7 | Section 4's dispatch-prompt prose documents the integration shape of directive plus body. | definition | L362 | F2-124 | - | - | none | no | procedure |
| FX-DIR-8 | `agents/engineer.md` carries the same directive-wins invariant in its **Authoritative design directive (fix mode only)** bullet, reloaded on every cold dispatch. | definition | L511 DP | F3-195 | - | - | none | no | procedure |

---

## 10. LOOP — Reconciliation loop & Phase A/B/C ladder

- **Purpose:** Drive each Issue through an event-driven Read-state → Reconcile → Yield loop of fresh, ephemeral background Agents, ordered into Phase A (Engineer ↔ Code Reviewer to clean), Phase B (writers once, in parallel), Phase C (remaining reviewers + PM).
- **Failure it prevents:** Writers reading a diff the pending code review is about to rewrite (ordered phases); polling / clock-driven ticks; acting on conversation memory instead of the four truth sources (F3-017).
- **Env deps:** Agent, TaskList, bees, git. **TaskList-dependent: yes** (task status is the in-flight signal).
- **Rows:** 35 (procedure 32, rationale 2, example 1).
- **Literals:** `### 4. Execute fix via per-issue Agent dispatch`; `#### Reconciliation loop`; **Read state.** / **Reconcile.** / **Yield.**; **Phase A — source to clean.**, **Phase B — writers once, in parallel.**, **Phase C — remaining reviewers plus PM.**; `bees show-ticket --ids <issue-id>`; `bees execute-freeform-query --query-yaml '<yaml>'` example `stages:\n- [id=<issue-id>]\nreport: [title, ticket_status]`; `No code issues found.`; `### Second-order effects`; `##### Anti-pattern: no clock primitives`; `/loop`, `ScheduleWakeup`, `CronCreate`; `run_in_background=true`; `### 5. Review Loop` = Phase C.
- **Edges:** Consumes DIR (directive), MAN (manifest as a Read-state source), ROUTE (SBL decides when Phase A / a lane closes; part (g) orders re-entry), MOVE (the `aborted-*` Phase C gate), ENGPRE, DQ (design-question exit), RECOV (compaction arms); Produces dispatches for PROMPT, REVIEW, and the `### Second-order effects` narrative for SUM.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-LOOP-1 | Drive each Issue's fix through a **reconciliation loop** that dispatches fresh, ephemeral background `Agent` invocations against subagent types in the sibling `agents/` directory. | invariant | L370 `### 4.` | F3-001 | dispatches | `agents/` role files | Agent | unknown | procedure |
| FX-LOOP-2 | Never keep a long-lived team, warmed Agents, or peer-to-peer messaging between workers. | invariant | L370 | F3-002 | - | - | Agent | unknown | procedure |
| FX-LOOP-3 | Dispatch scope is **per-issue**, not per-Subtask: one implementation pass per Issue, no Subtask breakdown, unlike `/quo-execute`. | definition | L370 | F3-003 | - | - | none | no | procedure |
| FX-LOOP-4 | Rationale: warm `SendMessage` dispatch (the SDD's original intent) needs the experimental teams substrate this skill set does not use; cold dispatch is a conscious trade-off tracked by a re-probe issue. | rationale-only | L497-L499 `##### Per-issue cold dispatch (vs SDD's warm-Agent intent)` | F3-185 | - | - | none | unknown | rationale |
| FX-LOOP-5 | The loop is **event-driven, not clock-driven**; each tick has exactly three phases: Read state, Reconcile, Yield. | ordering | L374 RL | F3-005 | - | - | none | unknown | procedure |
| FX-LOOP-6 | **Read state.** Pull current truth from four sources (bees, TaskList, git state, run-state manifest) before deciding what to do. | precondition | L376 RL | F3-006 | - | four sources | TaskList, bees, git | unknown | procedure |
| FX-LOOP-7 | Use `bees show-ticket --ids <issue-id>` for the Issue body and current `ticket_status`. | command | L377 RL | F3-007 | - | Issue id | bees | unknown | procedure |
| FX-LOOP-8 | Use `bees execute-freeform-query --query-yaml '<yaml>'` for any focused state query. | command | L377 RL | F3-008 | - | - | bees | unknown | procedure |
| FX-LOOP-9 | Example freeform query: `stages:` `- [id=<issue-id>]` `report: [title, ticket_status]`. | example | L379-L383 RL | F3-009 | - | - | bees | unknown | example |
| FX-LOOP-10 | The git diff on disk is the only authoritative record of what workers actually did. | invariant | L385 RL | F3-011 | - | git diff | git | unknown | procedure |
| FX-LOOP-11 | **Conversation memory is never a substitute for these four sources.** Re-read Issue status, landed commits, batch order, pre-session SHA on every tick; never recall. | invariant | L388 RL | F3-017 | - | four sources | TaskList, bees, git | unknown | procedure |
| FX-LOOP-12 | **Reconcile.** Compare current state to target state and act. | definition | L400 RL | F3-056 | - | - | none | unknown | procedure |
| FX-LOOP-13 | Dispatch is **ordered into three phases**; implementer lanes are NOT fanned out together, reviewers are not all held to the end; dispatch concurrently only *within* a phase. | ordering | L400 RL | F3-057 | - | - | Agent | unknown | procedure |
| FX-LOOP-14 | **Phase A — source to clean.** When the fix needs source changes, dispatch the **Engineer alone**. | ordering | L402 RL | F3-058 | Engineer dispatch | - | Agent | unknown | procedure |
| FX-LOOP-15 | On the Engineer's return, dispatch the **Code Reviewer alone** (Section 5 shape, `code-reviewer-<issue-id>`) unless that return carries a `## Design question`. | ordering | L402 RL | F3-059 | Code Reviewer dispatch | Engineer return | Agent | no | procedure |
| FX-LOOP-16 | Loop Engineer → Code Reviewer → Engineer until the Code Reviewer emits `No code issues found.` or every remaining finding is routed through `### Orchestrator discipline: routing review findings`. | ordering | L402 RL | F3-060 | dispatches | Code Reviewer return | Agent | unknown | procedure |
| FX-LOOP-17 | The design-question rung is a further exit from the Engineer step: it neither closes nor continues Phase A but **suspends** it pending a revised directive from Section 3. | definition | L402 RL | F3-064 | - | - | none | no | procedure |
| FX-LOOP-18 | When the Issue needs no source change, Phase A is empty and the loop proceeds directly to Phase B. | ordering | L402 RL | F3-066 | - | - | none | unknown | procedure |
| FX-LOOP-19 | **The Phase A exit test reads the numbered work-item list only.** | invariant | L404 RL | F3-067 | - | `/quo-engineer-review` output | none | unknown | procedure |
| FX-LOOP-20 | **A non-empty `### Second-order effects` narrative alongside a clean numbered list does NOT block Phase A closure.** | invariant | L404 RL | F3-068 | - | `### Second-order effects` | none | unknown | procedure |
| FX-LOOP-21 | `/quo-engineer-review` emits `### Second-order effects` on **every** review, clean ones included; actionable items are already in the numbered list. | definition | L404 RL | F3-070 | - | - | none | unknown | rationale |
| FX-LOOP-22 | **Phase B — writers once, in parallel.** Once Phase A has closed, dispatch the **Test Writer** (when tests need changing) and the **Doc Writer** (always) concurrently. | ordering | L405 RL | F3-071 | Test Writer, Doc Writer dispatches | Phase A closure | Agent | unknown | procedure |
| FX-LOOP-23 | Phase B is the **only** place the two writers are dispatched on the forward path, so they read a review-clean diff (or one clean apart from final `trivial-tweak` nit fixes). | invariant | L405 RL | F3-072 | - | - | Agent | unknown | procedure |
| FX-LOOP-24 | **Phase C — remaining reviewers plus PM** = Section 5. Advance to it when the Phase B writers have returned and the `aborted-*` gate (FX-MOVE-15) is clear. | ordering | L406 RL; L706 `### 5. Review Loop` | F3-073, F5-001 | - | TaskList | TaskList | unknown | procedure |
| FX-LOOP-25 | The Code Reviewer is NOT dispatched again in Phase C; it ran to closure in **Phase A**, alone, interleaved with the Engineer until the source is clean — its conditional spawn (if the Engineer ran) lives in Phase A, before Phase B begins. | invariant | L406 RL; L706; L713 | F3-075, F5-004, F5-015 | - | - | Agent | unknown | procedure |
| FX-LOOP-26 | **Re-entry from Phase C.** A Phase C finding whose chosen fix path changes **source** re-enters Phase A: dispatch the Engineer, then the Code Reviewer (elided only for a final `trivial-tweak` nit pass per part (g)), loop until Phase A re-closes. | ordering | L418 RL | F3-092 | Engineer, Code Reviewer dispatches | Phase C finding | Agent | unknown | procedure |
| FX-LOOP-27 | When Phase A re-closes, re-dispatch **only** the writer lanes the source change invalidated (Test Writer if pinned behavior moved, Doc Writer if documented diff moved), then the corresponding Phase C reviewers. | ordering | L418 RL | F3-093 | writer, reviewer dispatches | - | Agent | unknown | procedure |
| FX-LOOP-28 | A Phase C finding confined to a writer's own lane (changes no source file) re-dispatches that writer alone and does **not** re-enter Phase A. | ordering | L418 RL | F3-094 | writer dispatch | Phase C finding | Agent | unknown | procedure |
| FX-LOOP-29 | The ordering rule for any re-dispatch that touches source is part (g) of `### Orchestrator discipline: routing review findings`. | definition | L418 RL | F3-096 | - | - | none | unknown | procedure |
| FX-LOOP-30 | For every Agent that reported completion: confirm any bees transitions it committed to, mark its TaskList task `completed`, and unlock the next phase or lane per the ladder. | command | L448 RL | F3-151 | task `completed` | Agent return, bees | TaskList, bees | unknown | procedure |
| FX-LOOP-31 | **Yield.** Do not poll; after dispatching this tick's work, return control and wait for the **Agent completion notification** from the `run_in_background=true` substrate, which triggers the next tick; Section 5's dispatches yield the same way — there is no idle teammate to escalate to. | ordering | L460 RL; L725 `### 5.` | F3-169, F5-042, F5-043 | - | Agent notification | Agent | unknown | procedure |
| FX-LOOP-32 | Do **not** use clock primitives: **`/loop`** (repeats last turn on wall-clock cadence), **`ScheduleWakeup`** (fires after a delay), **`CronCreate`** (recurring schedule). | invariant | L466-L468 `##### Anti-pattern: no clock primitives` | F3-170, F3-171, F3-172 | - | - | none | unknown | procedure |
| FX-LOOP-33 | Do **not** poll: no re-reading bees / TaskList / git on a sleep-wait cycle without a triggering event. | invariant | L469 | F3-173 | - | - | none | unknown | procedure |
| FX-LOOP-34 | If this tick's work is dispatched and nothing else needs reconciling, yield; background Agents finishing is the only legitimate trigger for the next tick. | ordering | L471 | F3-174 | - | - | Agent | unknown | procedure |
| FX-LOOP-35 | The orchestrator does not pre-judge whether a PM pass is needed (always dispatched in Phase C — FX-REVIEW-4). | invariant | L406 RL | F3-076 | - | - | none | unknown | procedure |

---

## 11. RECOV — Post-compaction recovery / re-derivation

- **Purpose:** When a summarization marker is visible, re-read all four sources and re-derive anything with no durable carrier — above all the Design Proposal (re-dispatch the Analyst with the re-derivation shape) and the last Code Reviewer verdict (re-dispatch the Code Reviewer) — branching the resume only on TaskList-derivable state.
- **Failure it prevents:** Reconstructing the proposal from a summary; dispatching an Engineer or Code Reviewer against a proposal nobody can read; a `## Blast radius` relay heading going missing (F3-025); mis-completion after compaction (F3-052 accepts a wasted Code Reviewer round instead).
- **Env deps:** TaskList, bees, git, Agent, AskUserQuestion. **TaskList-dependent: yes** (every resume arm keys on task names/status).
- **Rows:** 37 (procedure 35, rationale 1, failure-narrative 1).
- **Literals:** **re-derivation shape** (three items); `## Files changed`; `git diff --name-only HEAD`; **Fallback when an Engineer return did not list files**; **Post-compaction recovery inside Phase A**; **Phase A has not begun** / **Phase B has not begun**; `analyst-<issue-id>` prefix match; `gate-askuserquestion-*`.
- **Edges:** Consumes MAN validation (FX-MAN-20/21), TASK names, ENGPRE's stranded-`pending` default (FX-ENGPRE-11); Produces Analyst dispatches into ANA's surface-and-gate flow, Code Reviewer dispatches into LOOP Phase A; DQ reuses the re-derivation shape when the proposal is unreadable.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-RECOV-1 | **If a summarization marker is visible in the conversation**, treat everything before it as non-authoritative and re-read all four sources in full before dispatching, starting with the Issue body from bees. | recovery | L388 RL | F3-018 | - | four sources | TaskList, bees, git | unknown | procedure |
| FX-RECOV-2 | The **Design Proposal** (`### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`) has no durable carrier by design; it lives only in the Analyst's returned message. | definition | L388 RL | F3-019 | - | Analyst return | none | no | procedure |
| FX-RECOV-3 | The proposal-recovery rule is **functional, not positional**: it fires **whenever the proposal is needed for this Issue** and is no longer readable. | precondition | L388 RL | F3-020 | - | Analyst return | none | no | procedure |
| FX-RECOV-4 | "Needed" = an Engineer dispatch (any round incl. Phase C re-entry), a Phase A Code Reviewer relay, a Phase C PM relay, a re-run of these, or Section 3's gate open on an unreadable proposal. | definition | L388 RL | F3-021 | - | - | none | no | procedure |
| FX-RECOV-5 | Do not reconstruct the Design Proposal from a summary. | invariant | L388 RL | F3-022 | - | - | none | no | procedure |
| FX-RECOV-6 | **Re-derive it through the Analyst. That is the only recovery for the proposal itself**; waiting on an in-flight Analyst is that same re-derivation. | recovery | L388 RL | F3-024 | Analyst dispatch | - | Agent | no | procedure |
| FX-RECOV-7 | No path in fix mode omits a downstream `## Blast radius` relay heading, because the proposal is re-derived before the dispatch that needs it. | invariant | L388 RL | F3-025 | - | - | none | no | procedure |
| FX-RECOV-8 | **Check first for an active `analyst-<issue-id>` task for this Issue**, matching on name **prefix** plus status so `-rev<n>` names are caught. | precondition | L390 RL | F3-026 | - | TaskList | TaskList | no | procedure |
| FX-RECOV-9 | An active `analyst-*` task means an Analyst is genuinely in flight (Section 3 marks it `completed` when the return is read); wait for it and run Section 3's gate on it. | recovery | L390 RL | F3-027 | - | TaskList | TaskList, Agent | no | procedure |
| FX-RECOV-10 | Wait only when the `analyst-*` task is `in_progress`, or `pending` with a dispatch already landed. | precondition | L390 RL | F3-028 | - | TaskList | TaskList | no | procedure |
| FX-RECOV-11 | When the `analyst-*` task is `pending` with no dispatch landed, do not wait: dispatch the Analyst now under that same task name using the **re-derivation shape**, and wait on that return. | recovery | L390 RL | F3-029 | Analyst dispatch | TaskList | TaskList, Agent | no | procedure |
| FX-RECOV-12 | Otherwise, when a `gate-askuserquestion-*` task for this Issue's Section 3 gate is active, mark it `completed`, recording in `metadata.activity` that a compaction abandoned the question. | recovery | L390 RL | F3-031 | gate task `completed`, `metadata.activity` | TaskList | TaskList | no | procedure |
| FX-RECOV-13 | The abandoned-question note in `metadata.activity` is informational context, never a routing input. | invariant | L390 RL | F3-032 | - | `metadata.activity` | TaskList | no | procedure |
| FX-RECOV-14 | Then re-dispatch the Analyst under the next `analyst-<issue-id>-rev<n>` name using the **re-derivation shape**. | recovery | L390 RL | F3-033 | Analyst dispatch, `-rev<n>` task | - | TaskList, Agent | no | procedure |
| FX-RECOV-15 | **For this one gate re-derivation takes precedence over the generic gate re-fire** the TaskList naming convention prescribes for active `gate-*` tasks. | ordering | L390 RL | F3-034 | - | - | TaskList | no | procedure |
| FX-RECOV-16 | Otherwise (no `analyst-*` task and no Section 3 `gate-*` task active), re-dispatch the Analyst under the next `analyst-<issue-id>-rev<n>` name using the **re-derivation shape**. | recovery | L390 RL | F3-035 | Analyst dispatch | TaskList | TaskList, Agent | no | procedure |
| FX-RECOV-17 | Re-derivation shape item 1: the **Issue body re-read from bees**, and the same `reference_materials` the first dispatch carried. | field-or-template | L392 RL | F3-036 | Analyst prompt | `bees show-ticket`, `reference_materials` | bees | no | procedure |
| FX-RECOV-18 | Re-derivation shape item 2: the **changed-file list of what is on disk for this Issue** — latest Engineer `## Files changed`, or the **Fallback when an Engineer return did not list files** derivation. | field-or-template | L393 RL | F3-037 | Analyst prompt | `## Files changed`, `git diff --name-only HEAD` | git | no | procedure |
| FX-RECOV-19 | An **empty** changed-file list is itself informative: no implementation has landed for this Issue yet. | definition | L393 RL | F3-038 | - | - | none | no | procedure |
| FX-RECOV-20 | Re-derivation shape item 3: state plainly that **the prior proposal was lost to a compaction**, the changed-file list is what was implemented, the Analyst re-derives from the codebase, and `### Blast radius` must cover the tree as it stands. | field-or-template | L394 RL | F3-039 | Analyst prompt | - | none | no | procedure |
| FX-RECOV-21 | When the re-dispatched pass is the **first** Section 3 pass (stranded task is undiscriminated `analyst-<issue-id>`), say instead that **no proposal has been produced yet** and the compaction landed before one returned. | field-or-template | L394 RL | F3-040 | Analyst prompt | task name | TaskList | no | procedure |
| FX-RECOV-22 | When the re-derivation Analyst returns, run Section 3's surface-and-gate flow unchanged and resume the in-progress phase with the re-derived directive. | recovery | L396 RL | F3-041 | - | Analyst return | AskUserQuestion, TaskList | no | procedure |
| FX-RECOV-23 | Branch the resume **only on TaskList-derivable state**, never on whether Phase A "still had findings". | invariant | L396 RL | F3-042 | - | TaskList | TaskList | no | procedure |
| FX-RECOV-24 | **Phase A has not begun** when no `engineer-<issue-id>` task exists (prefix-matched, catching `-r<n>`), or the only one is `pending` with no dispatch landed. | definition | L396 RL | F3-043 | - | TaskList | TaskList | no | procedure |
| FX-RECOV-25 | On Phase-A-not-begun, resume at **Phase A's entry**: the first Engineer dispatch, under the stranded task's own name when one exists, or straight to **Phase B** when the directive needs no source change. | recovery | L396 RL | F3-044 | Engineer dispatch | TaskList | TaskList, Agent | no | procedure |
| FX-RECOV-26 | Do **not** dispatch the Code Reviewer on the Phase-A-not-begun branch; no implementation has landed to review. | invariant | L396 RL | F3-045 | - | - | Agent | no | procedure |
| FX-RECOV-27 | **The "only one that does" qualifier is deliberate:** when a stranded `pending` `engineer-<issue-id>-r<n>` sits beside a `completed` earlier round, this arm does not fire; leave the stranded task as is. | recovery | L396 RL | F3-046 | - | TaskList | TaskList | no | procedure |
| FX-RECOV-28 | Section 7's close-out prefix sweep marks such a stranded task `completed` at the Issue boundary; the only cost is a skipped round number. | definition | L396 RL | F3-047 | - | - | TaskList | no | procedure |
| FX-RECOV-29 | When an `engineer-<issue-id>` task exists and **Phase B has not begun** (no `test-writer-<issue-id>` or `doc-writer-<issue-id>` task, prefix-matched), resume through the Phase A recovery rung: dispatch the **Code Reviewer** with the re-derived `## Blast radius`. | recovery | L396 RL | F3-048 | Code Reviewer dispatch | TaskList | TaskList, Agent | no | procedure |
| FX-RECOV-30 | Rationale: that rung's Analyst-active exception cannot fire here because Section 3's surfacing step marked the Analyst task `completed` when its return was read. | rationale-only | L396 RL | F3-049 | - | - | none | no | rationale |
| FX-RECOV-31 | Let the Code Reviewer's findings drive whether an Engineer round follows and what it addresses, under its next name per the naming convention. | recovery | L396 RL | F3-050 | Engineer dispatch | Code Reviewer return | Agent | no | procedure |
| FX-RECOV-32 | Otherwise resume with the **next dispatch** in the ladder, whose `## Blast radius` relay now has a list to carry. | recovery | L396 RL | F3-051 | next dispatch | - | Agent | no | procedure |
| FX-RECOV-33 | **One case the Phase-B-has-not-begun arm cannot tell apart by task-name set alone:** a `## Design question` round where compaction landed before the Analyst re-dispatch; cost is a Code Reviewer round on a partial diff, not a mis-completion. | failure-narrative | L396 RL | F3-052 | - | - | none | no | failure-narrative |
| FX-RECOV-34 | Where the re-derivation differs from the diff on disk, the Engineer round reconciles that difference rather than papering over it. | invariant | L396 RL | F3-053 | - | - | Agent | no | procedure |
| FX-RECOV-35 | **Post-compaction recovery inside Phase A.** "Did the last code review come back clean?" has **no durable carrier**; do NOT add a lane-phase field to the manifest. | invariant | L419 RL | F3-097 | - | manifest | none | unknown | procedure |
| FX-RECOV-36 | If a compaction lands mid-Phase-A and the Code Reviewer's last verdict is unreadable, **re-dispatch the Code Reviewer**; a cold pass over the current diff is idempotent and correct. | recovery | L419 RL | F3-098 | Code Reviewer dispatch | - | Agent | unknown | procedure |
| FX-RECOV-37 | Exception: if an `analyst-<issue-id>` task is active (prefix + status, catching `-rev<n>`), Phase A is suspended; wait for the Analyst's return and run Section 3's gate rather than reviewing the partial diff. | recovery | L419 RL | F3-099 | - | TaskList | TaskList | no | procedure |

---

## 12. ENGPRE — Engineer-dispatch precondition

- **Purpose:** Never dispatch an Engineer while any writer, Phase C reviewer, PM, or Analyst task for the Issue is `pending` or `in_progress` — checked by prefix + status before every Engineer dispatch, never remembered.
- **Failure it prevents:** A reviewer mid-read returning a stale verdict, a writer redoing work against a diff the Engineer rewrites, an Analyst mid-revision authoring a directive the Engineer is already implementing (F3-080, F3-081, F7-136).
- **Env deps:** TaskList, Agent. **TaskList-dependent: yes.**
- **Rows:** 20 (procedure 15, rationale 5).
- **Literals:** **Engineer-dispatch precondition (checkable, not a promise).**; prefixes `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, `analyst-<issue-id>`; post-completion prefixes `test-writer-postcomp-*`, `doc-writer-postcomp-*`; `aborted-` (distinct class, not matched); statuses `pending` / `in_progress`.
- **Edges:** Consumes TASK naming (prefix rule FX-TASK-15); gates LOOP Phase A entries and re-entries, ROUTE part (g) re-dispatches, DQ's post-Approve Engineer round (the close-out sweep in DQ exists to satisfy it), POSTC `engineer-postcomp-<n>` dispatches; RECOV cites its stranded-`pending` default.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ENGPRE-1 | **Engineer-dispatch precondition:** MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, or `analyst-<issue-id>` is `pending` or `in_progress`. | precondition | L407 RL; L489 `#### Per-issue cold dispatch`; L696 ODR (g) | F3-077, F3-180, F4-147 | - | TaskList | TaskList, Agent | no | procedure |
| FX-ENGPRE-2 | Match on name **prefix** plus status, never on an exact name, so `-r<n>` and other suffixes are caught. | invariant | L407 RL | F3-078 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-3 | It is a **precondition to check, not a state to remember**: before *every* Engineer dispatch (forward, re-entry, and every re-dispatch routed from ODR) walk the TaskList and confirm no matching task is active. | precondition | L407 RL; L696 ODR (g) | F3-079, F4-148 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-4 | Rationale (**Why the two Phase C reviewers and the PM are covered**): a reviewer mid-read when edits land returns a stale verdict; a Phase C finding re-entering Phase A waits for **all** Phase C returns. | rationale-only | L409 RL | F3-080 | - | - | none | unknown | rationale |
| FX-ENGPRE-5 | Rationale (**Why the Analyst is covered too**): an Analyst mid-revision authors the directive the next Engineer round implements; Section 3 marks the Analyst task `completed` before the approval gate, so the forward path is never blocked. | rationale-only | L411 RL | F3-081 | - | - | none | no | rationale |
| FX-ENGPRE-6 | **The Code Reviewer is the one deliberate exception, and is NOT in the prefix list**, because Phase A alternates Engineer and Code Reviewer by construction. | invariant | L413 RL | F3-082 | - | - | none | unknown | procedure |
| FX-ENGPRE-7 | The Code Reviewer exclusion is specific to this ladder; it does **not** generalize to a review site where the Code Reviewer runs concurrently with other reviewers. | invariant | L413 RL | F3-083 | - | - | none | unknown | procedure |
| FX-ENGPRE-8 | `pending` stays in the status test deliberately: it closes the race between task creation and the `Agent(...)` call landing. | invariant | L415 RL | F3-084 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-9 | When the blocking task is `in_progress`, or `pending` **with a dispatch already landed**, wait for its completion notification and re-check on the next tick. | precondition | L415 RL | F3-085 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-10 | When the blocking task is `pending` and **no dispatch has landed**, do not wait: dispatch that role now (if wanted) or mark the stale task `completed` and clear it, then re-check (carries over to post-completion names). | recovery | L415 RL; L1266 PC | F3-086, F7-137 | dispatch or task `completed` | TaskList | TaskList, Agent | unknown | procedure |
| FX-ENGPRE-11 | **Post-compaction, whether a dispatch landed is unreadable**; default to **not** landed and re-dispatch. Stated once at L415 and answering wherever the clause is cited (incl. the Analyst arm at L390). | recovery | L415 RL; L390 RL | F3-087, F3-030 | - | - | none | unknown | procedure |
| FX-ENGPRE-12 | Do **not** narrow the precondition to `in_progress` only; `pending` stays in the test. | invariant | L415 RL | F3-088 | - | - | TaskList | unknown | procedure |
| FX-ENGPRE-13 | **A writer that aborted on source movement does not block an Engineer round, and needs no exemption**: `aborted-` is a **distinct name class** the prefix test does not match; what the `aborted-*` task gates is **Phase C**, not the Engineer. | invariant | L417 RL; L432 RL; L589 TNC | F3-089, F3-091, F3-118, F3-269 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-14 | Never key an exemption on an abort annotation in `metadata.activity`; it is informational and not a routing input. | invariant | L417 RL | F3-090 | - | `metadata.activity` | TaskList | unknown | procedure |
| FX-ENGPRE-15 | Section 4 is authoritative for three qualifications ODR (g) does not restate: the prefix-match rule (catching `engineer-<issue-id>-r<n>`), the Code Reviewer's deliberate exclusion, and handling a `pending` task with no Agent behind it. | definition | L696 ODR (g) | F4-149 | - | - | none | no | procedure |
| FX-ENGPRE-16 | Rationale: the DQ close-out sweep (FX-DQ-19) exists because this precondition forbids a fresh Engineer while any listed task is active, and the Analyst re-dispatch gate can fire from a review phase where several are. | rationale-only | L662 ODR (c) | F4-072 | - | - | none | no | rationale |
| FX-ENGPRE-17 | Rationale: Section 4's precondition keys on issue-scoped names, which do not match post-completion names, so it is restated for the Section 8 branch. | rationale-only | L1266 PC | F7-133 | - | - | none | no | rationale |
| FX-ENGPRE-18 | The orchestrator MUST NOT dispatch an `engineer-postcomp-<n>` Agent while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` TaskList task is `pending` or `in_progress`. | precondition | L1266 PC | F7-134 | - | TaskList | TaskList, Agent | unknown | procedure |
| FX-ENGPRE-19 | The post-completion precondition matches on name prefix plus status at **every** finding index and every `-r<k>` re-dispatch round, not only the `<n>` being addressed. | invariant | L1266 PC | F7-135 | - | TaskList | TaskList | unknown | procedure |
| FX-ENGPRE-20 | Rationale: a writer handed a diff an Engineer is about to rewrite has to redo its work. | rationale-only | L1266 PC | F7-136 | - | - | none | unknown | rationale |

---

## 13. MOVE — Movement-report rung & `aborted-*` markers

- **Purpose:** Receive a Phase B writer's "source moved, I stopped" report, record the owed redelivery as a `pending` `aborted-<role>-<issue-id>` task that holds Phase C shut, attribute the movement (Engineer / sibling Test Writer perturbation / external actor), and re-dispatch the lane under its next `-r<n>` name once the tree settles.
- **Failure it prevents:** Marking the writer `completed`, advancing to Phase C, and reviewing unfinished work (F3-102); re-dispatching against a still-moving diff (F3-117); a blind re-dispatch loop (F3-132).
- **Env deps:** TaskList, Agent, git. **TaskList-dependent: yes** (the marker *is* the durable obligation).
- **Rows:** 29 (procedure 28, failure-narrative 1).
- **Literals:** **Movement report from a Phase B writer.**; **Recognising it.** / **What to do.**; `aborted-<role>-<issue-id>` (`aborted-test-writer-<issue-id>`, `aborted-doc-writer-<issue-id>`); `## Source paths to fingerprint`; `## Perturbations` (`None`); `git rev-parse HEAD` + `git hash-object` (Test Writer fingerprint); `Read` / `Grep` (Doc Writer); **When the mover was an Engineer** / **…the sibling Phase B Test Writer's discrimination experiment** / **…an external actor**; `-r<n>` (`test-writer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`).
- **Edges:** Consumes writer returns from LOOP Phase B and PROMPT's fingerprint list; Produces the Phase C gate LOOP honours, `aborted-*` tasks swept by CLOSE / ABORT, and the UNEXP gate trigger; the postcomp variant lives in POSTC (FX-POSTC-73..80).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-MOVE-1 | `agents/test-writer.md` and `agents/doc-writer.md` instruct the writer to **stop mid-run and report** when the source it worked against moved. | definition | L420 RL | F3-100 | - | writer return | none | unknown | procedure |
| FX-MOVE-2 | The Test Writer detects movement with a `git rev-parse HEAD` + `git hash-object` fingerprint taken at start and before finishing; the Doc Writer (no `Bash`) re-reads with `Read` / `Grep`. | definition | L420 RL | F3-101 | - | - | git | unknown | procedure |
| FX-MOVE-3 | This rung is the receiver of the movement report; without one the orchestrator would mark the task `completed`, advance to Phase C, and review unfinished work. | failure-narrative | L420 RL | F3-102 | - | - | none | unknown | failure-narrative |
| FX-MOVE-4 | **Recognising it.** Read the writer's return before persisting anything. | ordering | L422 RL | F3-103 | - | writer return | none | unknown | procedure |
| FX-MOVE-5 | A movement report says the source moved, names what moved (files, opening/closing HEAD when HEAD moved), and how far the work got, in place of or alongside a partial deliverable. | definition | L422 RL | F3-104 | - | writer return | none | unknown | procedure |
| FX-MOVE-6 | **Fix mode is the strict branch**: movement outside the writer's lane is anomalous, not expected concurrency; do not import the role files' softer execute-mode branch. | invariant | L422 RL | F3-105 | - | - | none | no | procedure |
| FX-MOVE-7 | **The two writers detect different things, and the receiver should not overstate either.** Test Writer trigger: any changed hash in its `## Source paths to fingerprint` set, a moved `HEAD`, or a path that no longer hashes. | definition | L422 RL | F3-106 | - | `## Source paths to fingerprint` | none | unknown | procedure |
| FX-MOVE-8 | The Doc Writer's trigger is narrower: it stops when the material it is documenting appears to have moved (a file it read no longer matches its prose). | definition | L422 RL | F3-107 | - | - | none | unknown | procedure |
| FX-MOVE-9 | Do not read a Doc Writer's silence as a clean-tree attestation over every source path. | invariant | L422 RL | F3-108 | - | - | none | unknown | procedure |
| FX-MOVE-10 | What marks either return as a movement report is that the writer **stopped**. | definition | L422 RL | F3-109 | - | writer return | none | unknown | procedure |
| FX-MOVE-11 | **What to do.** Do **NOT** unlock Phase C on that lane; record the owed redelivery as a durable TaskList entry (the obligation-as-pending-task pattern `defer-*` and `gate-*` use). | invariant | L424 RL | F3-110 | TaskList task | - | TaskList | unknown | procedure |
| FX-MOVE-12 | Step 1: **Mark the writer's own TaskList task `completed`** (`test-writer-<issue-id>` / `doc-writer-<issue-id>`, incl. any `-r<n>`); its Agent has exited. | command | L426 RL | F3-111 | task `completed` | TaskList | TaskList | unknown | procedure |
| FX-MOVE-13 | Step 2: **Create a new `aborted-<role>-<issue-id>` TaskList task** (`aborted-test-writer-<issue-id>` / `aborted-doc-writer-<issue-id>`) with status `pending` and the "how far I got" report as `metadata.activity`, after the writer's own task is `completed`. | command | L427 RL; L589 TNC | F3-112, F3-265 | `aborted-<role>-<issue-id>` task | writer return | TaskList | unknown | procedure |
| FX-MOVE-14 | The pending `aborted-*` task **is** the redelivery-owed marker, read off the TaskList each tick so it survives compaction. | definition | L427 RL | F3-113 | - | TaskList | TaskList | unknown | procedure |
| FX-MOVE-15 | **Phase C MUST NOT begin while any `aborted-*` task for this Issue is `pending`** — evaluate the conjunct by matching the `aborted-` name prefix plus status `pending`; the marker is an **obligation marker** like `defer-*` and `gate-*`. | gate | L406 RL; L428 RL; L589 TNC; L706 `### 5.` | F3-115, F3-267, F5-002, F5-003 | - | TaskList | TaskList | unknown | procedure |
| FX-MOVE-16 | Routing tests the `aborted-*` task's **name prefix and status**; `metadata.activity` is informational context for the re-dispatch prompt only. | invariant | L427 RL | F3-114 | - | TaskList | TaskList | unknown | procedure |
| FX-MOVE-17 | **When the mover was an Engineer** — **in fix mode this should not occur**; treat it as a **precondition breach**, recover through the ordering here, and note the breach rather than absorbing it silently. | recovery | L432 RL | F3-116 | breach note | - | none | no | procedure |
| FX-MOVE-18 | On an Engineer mover, Phase A must **re-close first** (finish Engineer → Code Reviewer loop); only then re-dispatch the writer — re-dispatching against a moving diff reproduces the abort. | ordering | L432 RL | F3-117 | dispatches | - | Agent | unknown | procedure |
| FX-MOVE-19 | **When the mover was the sibling Phase B Test Writer's discrimination experiment**: `agents/test-writer.md` sanctions in-place perturbation with `Edit` / `Write` (restored after) and requires a `## Perturbations` heading listing every perturbed path, `None` when none. | definition | L433 RL | F3-119 | - | `## Perturbations` | none | unknown | procedure |
| FX-MOVE-20 | Read the Test Writer's `## Perturbations`: when it lists **every** path the aborted writer reported, the movement is attributed; **re-dispatch the aborted lane once that sibling has returned, with no gate**. | recovery | L433 RL | F3-120 | writer re-dispatch | `## Perturbations` | Agent | unknown | procedure |
| FX-MOVE-21 | When `## Perturbations` covers only **some** of the moved paths, fall through to the external-actor case for the remainder. | recovery | L433 RL | F3-121 | - | `## Perturbations` | none | unknown | procedure |
| FX-MOVE-22 | **When a Test Writer was dispatched in Phase B and has not returned yet, do not classify and do not fire the gate**; wait for its completion notification, read `## Perturbations`, classify then. | ordering | L433 RL | F3-122 | - | Agent notification | Agent | unknown | procedure |
| FX-MOVE-23 | The perturbation case fails once every dispatched Test Writer has returned and none lists the moved path; fall through to the external-actor case. | recovery | L433 RL | F3-123 | - | `## Perturbations` | none | unknown | procedure |
| FX-MOVE-24 | The perturbation case **never applies when Phase B dispatched no Test Writer** (doc-only Issue); do not wait for a notification that is not coming; fall through to external-actor. | recovery | L433 RL | F3-124 | - | - | none | unknown | procedure |
| FX-MOVE-25 | **When the mover was an external actor** (user, second session, background process): re-dispatch the writer once the movement is understood — the current diff is read and the tree has settled. | recovery | L434 RL | F3-125 | writer re-dispatch | git diff | git, Agent | unknown | procedure |
| FX-MOVE-26 | Carry the writer's "how far I got" report (the `aborted-*` task's `metadata.activity`) into the re-dispatch prompt so the fresh Agent does not start from zero. | relay | L436 RL | F3-128 | re-dispatch prompt | `metadata.activity` | TaskList, Agent | unknown | procedure |
| FX-MOVE-27 | **When the re-dispatched lane (`<role>-<issue-id>-r<n>` or `<role>-postcomp-<n>-r<k>`) returns a normal deliverable, mark the `aborted-*` task `completed`** — that releases Phase C. | command | L436 RL; L589 TNC | F3-129, F3-268 | `aborted-*` `completed` | writer return | TaskList | unknown | procedure |
| FX-MOVE-28 | If the re-dispatched lane aborts again, repeat the rung: mark its `-r<n>` task `completed` and refresh the **existing** `aborted-*` task's `metadata.activity`; never create a second one — **the marker is not an Agent task**, so the one-task-per-Agent rule and `-r<n>` do not apply to it. | recovery | L436 RL; L589 TNC | F3-130, F3-266 | `metadata.activity` refresh | writer return | TaskList | unknown | procedure |
| FX-MOVE-29 | **A Phase B writer return that reports detected source movement is not a completion**; route it through this rung; it does not unlock the next phase. Its task is nonetheless set `completed` **without** landed deliverables — `completed` means "this Agent is gone", not "this work shipped" (the one exception to FX-TASK-6). | invariant | L448 RL; L575 `#### TaskList as progress UI` | F3-152, F3-249 | - | writer return | TaskList | unknown | procedure |

---

## 14. UNEXP — Unexplained-movement gate

- **Purpose:** When a writer's movement cannot be attributed to any dispatched actor, ask the operator (re-dispatch / wait / abort) instead of re-dispatching blindly.
- **Failure it prevents:** A blind re-dispatch loop into a tree something else is editing (F3-132); re-firing the gate on a sibling lane's completion (F3-142).
- **Env deps:** AskUserQuestion, TaskList, Agent. **TaskList-dependent: yes.**
- **Rows:** 14 (procedure 14).
- **Literals:** **Unexplained-movement gate.**; options **Re-dispatch the writer now**, **Wait**, **Abort this Issue**; one-line statement *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths … so it cannot attribute the movement.*
- **Edges:** Triggered from MOVE's external-actor case; uses GATE mechanics; **Abort this Issue** routes to ABORT; re-titled for post-completion lanes in POSTC (FX-POSTC-81..84).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-UNEXP-1 | Movement is unexplained when no Engineer was dispatched over the window, no returned Test Writer's `## Perturbations` covers the paths (including no Test Writer at all), no Test Writer is in flight, and no other account exists. | definition | L434; L438 RL | F3-126, F3-131 | gate trigger | TaskList, `## Perturbations` | TaskList, AskUserQuestion | unknown | procedure |
| FX-UNEXP-2 | Do not re-dispatch blindly; a blind re-dispatch loop is the failure mode this branch prevents. | invariant | L438 RL | F3-132 | - | - | none | unknown | procedure |
| FX-UNEXP-3 | Fire this gate through the two-step contract (**first** `gate-askuserquestion-<short-suffix>` naming the unexplained-movement gate, **then** `AskUserQuestion` same turn; do not narrate; honour yield-control) — this gate's instance of FX-GATE-1/2/6. | gate | L438 RL | F3-133, F3-134, F3-135 | gate task, gate | - | TaskList, AskUserQuestion | unknown | procedure |
| FX-UNEXP-4 | The question text carries the writer's movement report **verbatim** (files moved, opening/closing HEAD, how far the work got). | field-or-template | L440 RL | F3-136 | question text | writer return | AskUserQuestion | unknown | procedure |
| FX-UNEXP-5 | The question text adds the one-line statement: *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths … so it cannot attribute the movement.* | field-or-template | L440 RL | F3-137 | question text | - | AskUserQuestion | unknown | procedure |
| FX-UNEXP-6 | Offer exactly three options (multi-choice only — FX-GATE-5). | choice-set | L440 RL | F3-138 | gate options | - | AskUserQuestion | unknown | procedure |
| FX-UNEXP-7 | Option **Re-dispatch the writer now**: re-dispatch the lane under its next `-r<n>` name against the current tree. | choice-set | L442 RL | F3-139 | writer re-dispatch | gate answer | AskUserQuestion, Agent | unknown | procedure |
| FX-UNEXP-8 | Option **Wait**: yield control; re-fire this gate **only on the operator's reply** — that reply is the only trigger. | choice-set | L443 RL | F3-140 | - | gate answer | AskUserQuestion | unknown | procedure |
| FX-UNEXP-9 | Do **not** read Wait as "no Agent is in flight": the concurrently-dispatched sibling Phase B lane may complete seconds later. | invariant | L443 RL | F3-141 | - | - | Agent | unknown | procedure |
| FX-UNEXP-10 | **A sibling lane's completion notification is a tick that processes that lane normally** (persist result, mark task `completed`) and **MUST NOT** re-fire the gate. | invariant | L443 RL | F3-142 | task `completed` | Agent notification | TaskList, Agent | unknown | procedure |
| FX-UNEXP-11 | Do not record the Wait state in `metadata.activity` and route on it; the re-fire rule derives from the tick's trigger and needs no bookkeeping. During Wait the `aborted-*` task stays `pending`, so Phase C stays shut. | invariant | L443 RL | F3-143, F3-144 | - | `metadata.activity`; TaskList | TaskList | unknown | procedure |
| FX-UNEXP-12 | Option **Abort this Issue**: the Issue stays `open` and nothing is committed for it; routing per ABORT (FX-ABORT-30/31). | choice-set | L444 RL | F3-145 | - | gate answer | AskUserQuestion, bees | no | procedure |
| FX-UNEXP-13 | Mark the `gate-*` task `completed` the moment the answer is consumed and the branch entered, including on **Wait** (consuming means yielding). | command | L446 RL | F3-149 | gate task `completed` | gate answer | TaskList | unknown | procedure |
| FX-UNEXP-14 | A re-fire on a later tick creates a **fresh** `gate-askuserquestion-<short-suffix>` task rather than reusing the closed one. | name-class | L446 RL | F3-150 | new gate task | - | TaskList | unknown | procedure |

---

## 15. DQ — Design-question receiver & Analyst re-dispatch

- **Purpose:** Treat an Engineer's `## Design question` return (or a reviewer `blocker` showing the directive itself is wrong) as a Section 3 Revise by reference: mark the Engineer done, re-dispatch the Analyst with the question as feedback, re-fire the approval gate, sweep in-flight lanes, and resume Phase A on the working tree.
- **Failure it prevents:** The Engineer inventing an unenumerated mechanism; reviewing a partial diff; routing findings raised under a superseded directive (F4-074..076).
- **Env deps:** TaskList, Agent, AskUserQuestion, git. **TaskList-dependent: yes.**
- **Rows:** 25 (procedure 24, failure-narrative 1).
- **Literals:** `## Design question`; `## Files changed`; `## Prior proposal and user feedback`; `Re-dispatch the Analyst with this finding`; `analyst-<issue-id>-rev<n>`; `engineer-<issue-id>-r<n>`; **Section 3 Revise, by reference**; **The durable carrier is the Analyst task.**
- **Edges:** Entered from LOOP Phase A (Engineer return) and ROUTE gates (c)/(d); reuses ANA's Revise shape and surface-and-gate flow (FX-ANA-48..52); on Approve the sweep satisfies ENGPRE; Cancel routes to ABORT; DEFC supersede-and-clear applies; RECOV supplies the re-derivation shape when the proposal is unreadable.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-DQ-1 | **An Engineer return carrying a `## Design question` is not a Phase A completion.** | invariant | L450 RL | F3-153 | - | Engineer return | none | no | procedure |
| FX-DQ-2 | `agents/engineer.md` requires the Engineer to stop rather than invent an unenumerated mechanism; such a return means the proposal's `### Blast radius` **missed a mechanism** — a revision of that proposal, not a new decision point. | definition | L450 RL | F3-154 | - | Engineer return | none | no | procedure |
| FX-DQ-3 | On a `## Design question` return, mark the Engineer's task `completed` and do **not** dispatch the Code Reviewer against the partial diff. | command | L450 RL | F3-155 | task `completed` | Engineer return | TaskList | no | procedure |
| FX-DQ-4 | Route the question as a **Section 3 Revise, by reference**. | ordering | L450 RL | F3-156 | - | - | none | no | procedure |
| FX-DQ-5 | **In place of the user's revision feedback**, send the Engineer's `## Design question` verbatim (mechanism needed, why blocked, alternatives, which parts landed and which did not). | field-or-template | L452 RL | F3-159 | Analyst prompt | `## Design question` | none | no | procedure |
| FX-DQ-6 | The re-dispatch prompt MUST state a **partial implementation of the prior directive is already on disk**, naming the Engineer's `## Files changed` list, so the Analyst reads the tree as mid-change. | field-or-template | L452 RL | F3-160 | Analyst prompt | `## Files changed` | none | no | procedure |
| FX-DQ-7 | The re-dispatch prompt MUST state that the revised `### Blast radius` has to cover the lifecycle of whatever mechanism it now enumerates. | field-or-template | L452 RL | F3-161 | Analyst prompt | - | none | no | procedure |
| FX-DQ-8 | **When the approved Design Proposal is no longer readable**, use the **re-derivation shape** from the Read-state step, adding only the `## Design question` as the feedback in `## Prior proposal and user feedback`. | recovery | L454 RL | F3-162 | Analyst prompt | re-derivation shape | none | no | procedure |
| FX-DQ-9 | **When the Analyst returns, run Section 3's surface-and-gate flow unchanged**: verdict preamble, two-step gate, three options exactly as Section 3 defines. | ordering | L455 RL | F3-163 | gate | Analyst return | TaskList, AskUserQuestion | no | procedure |
| FX-DQ-10 | Branches are Section 3's own: **Approve** captures the revised directive (supersede-and-clear applies), **Revise** loops, **Cancel** routes through Section 7's **`#### Aborted-Issue close-out`**. | choice-set | L455 RL | F3-164 | - | gate answer | AskUserQuestion | no | procedure |
| FX-DQ-11 | After Approve, re-dispatch the Engineer under its next `-r<n>` name carrying the revised directive and a note that it continues from the partial diff on disk. | command | L455 RL | F3-165 | Engineer dispatch, `engineer-<issue-id>-r<n>` | revised directive | TaskList, Agent | no | procedure |
| FX-DQ-12 | **The durable carrier is the Analyst task**: the active `analyst-<issue-id>-rev<n>` task holds Phase A suspended; on return it is marked `completed` per Section 3 and the gate task carries the suspension until a branch is entered. | invariant | L456 RL | F3-166 | - | TaskList | TaskList | no | procedure |
| FX-DQ-13 | Once the re-dispatch lands, nothing about the question lives only in conversation; the residual window (Engineer return → re-dispatch) costs a Code Reviewer round on a partial diff, not a mis-completion. | failure-narrative | L456 RL | F3-167 | - | - | none | no | failure-narrative |
| FX-DQ-14 | The design-question receiver introduces no gate, option, task-name class, marker, or manifest field of its own; it is Section 3's Revise branch entered from Section 4. | invariant | L458 RL | F3-168 | - | - | none | no | procedure |
| FX-DQ-15 | `Re-dispatch the Analyst with this finding` (gates (c) and (d)) is for a `blocker` showing the approved design directive itself is wrong, not the implementation of it. | definition | L662 ODR (c) | F4-067 | - | finding | none | no | procedure |
| FX-DQ-16 | That choice reuses Section 3's Revise-branch shape: mark the prior Analyst task `completed`, issue a fresh cold `subagent_type=analyst` dispatch tracked as `analyst-<issue-id>-rev<n>`, carrying the finding verbatim as revision context — identical at gate (d). | command | L662 ODR (c); L678 ODR (d) | F4-068, F4-121 | Analyst dispatch, `-rev<n>` task | finding text | Agent, TaskList | no | procedure |
| FX-DQ-17 | When the re-dispatched Analyst returns, Section 3's Approve / Revise / Cancel gate re-fires over the new proposal, exactly as on the Revise branch. | gate | L662 ODR (c) | F4-069 | Section 3 gate | Analyst result | TaskList, AskUserQuestion | no | procedure |
| FX-DQ-18 | On `Approve`, re-enter Section 4 Phase A with the revised directive, but close out this Issue's open TaskList tasks first. | ordering | L662 ODR (c) | F4-070 | Phase A re-entry | `Approve` | TaskList | no | procedure |
| FX-DQ-19 | Close-out sweep (run **before** re-entering Section 4 on every Approve reached from that re-fire): by prefix, mark `completed` every active `test-writer-<issue-id>` / `doc-writer-<issue-id>` / `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` task and their `-r<n>` rounds — whichever are actually active (may be none on a Phase A finding) — and discard their findings. | command | L329 `#### Branch on the user's choice`; L662 ODR (c) | F2-078, F2-079, F4-071 | task statuses `completed`; findings discarded | TaskList | TaskList | no | procedure |
| FX-DQ-20 | The sweep holds on **every** Approve reached from that re-fire — including a later Approve after one or more Revise iterations on it. | invariant | L329 | F2-080 | - | re-fire origin | TaskList | no | procedure |
| FX-DQ-21 | A lane still in flight when the sweep fires is marked `completed` anyway (the orchestrator cannot terminate a dispatched background Agent) with `metadata.activity` recording it was in flight at the Analyst re-dispatch. | command | L662 ODR (c) | F4-073 | task flip, `metadata.activity` | in-flight Agent | TaskList | no | procedure |
| FX-DQ-22 | When an in-flight lane's completion notification arrives after the sweep, discard its findings rather than routing them. | invariant | L662 ODR (c) | F4-074 | - | Agent completion | Agent | no | procedure |
| FX-DQ-23 | The discard covers every finding raised under the superseded directive: sibling findings co-emitted with the gate-firing return, and any lane that returned between the gate answer and the sweep. | invariant | L662 ODR (c) | F4-075 | - | reviewer returns | none | no | procedure |
| FX-DQ-24 | Route none of the superseded findings; the revised directive is what the next round reviews against. | invariant | L662 ODR (c) | F4-076 | - | revised directive | none | no | procedure |
| FX-DQ-25 | The new Engineer works against the current working tree: landed edits stay in it uncommitted, and the revised directive is applied on top rather than to a clean base. | invariant | L662 ODR (c) | F4-077 | Engineer dispatch | working tree | Agent, git | no | procedure |

---

## 16. PROMPT — Cold-dispatch shape & prompt contents

- **Purpose:** Define the per-role cold `Agent(...)` call and what each dispatch prompt must carry: the Issue body verbatim, the directive (Engineer), `reference_materials`, the Engineer's completeness evidence and the Analyst's `## Blast radius` (Code Reviewer and PM), the fingerprint path list (Test Writer), and the orchestrator-side non-freeze statement (writers).
- **Failure it prevents:** Paraphrase corrupting identifiers the worker uses literally (F2-022, F3-186); a renamed relay heading silently dropping a review check (F3-206); an unnamed sweep silently losing the completeness check (F5-031); a "tree is frozen" promise the orchestrator cannot keep (F3-212).
- **Env deps:** Agent, bees, git, Bash, TaskList (compaction-artifact disposition). **TaskList-dependent: no** (except FX-PROMPT-20's `defer-*` disposition).
- **Rows:** 46 (procedure 42, rationale 4).
- **Literals:** `Agent(subagent_type=<role>, run_in_background=true, prompt=<...>)`; `subagent_type` ∈ `engineer` / `test-writer` / `doc-writer`; `Agent(name=...)` (forbidden); `SendMessage` (forbidden); `bees show-ticket --ids <issue-id>`; headings `## Authoritative design directive (from Section 3 Analyst pass)`, `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)`, `## Blast radius`, `## Engineer's completeness evidence`, `## Source paths to fingerprint`, `## Files changed`; fixed empty line `No invariant added, removed, or weakened.`; `git diff --name-only HEAD`; writer statement `"no Engineer Agent will be dispatched for this Issue while you are running"`; forbidden `"the source tree is frozen"`; `<scoped-marker-resolver-path>`, `<compromise-tracker-path>`; `##### Dispatch prompt: quote the issue body verbatim and embed the design directive`; `#### Per-issue cold dispatch`.
- **Edges:** Consumes VAL (body), DIR (directive), ANA (`### Blast radius`), Engineer returns (completeness list, `## Files changed`), TRACK (tracker path), SCOPED (resolver path); Produces prompts for LOOP/REVIEW dispatches; compaction-artifact finding → LEDGER; role-boundary anti-softening in ROLES.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-PROMPT-1 | For each Issue, spawn one fresh Agent per role at issue scope: `Agent(subagent_type=<role>, run_in_background=true, prompt=<...>)`. | command | L475-L483 `#### Per-issue cold dispatch` | F3-175 | Agent dispatch | - | Agent | unknown | procedure |
| FX-PROMPT-2 | Implementer `subagent_type` is one of `engineer`, `test-writer`, `doc-writer`. | choice-set | L479 | F3-176 | - | - | Agent | unknown | procedure |
| FX-PROMPT-3 | Each role gets its own Agent invocation; do **not** use `Agent(name=...)`; do **not** reuse an Agent across roles. | invariant | L485 | F3-178 | - | - | Agent | unknown | procedure |
| FX-PROMPT-4 | The dispatch prompt MUST embed the Issue body **verbatim** as a quoted block (read via `bees show-ticket --ids <issue-id>`); do not summarise, paraphrase, or "clean up" identifier spellings — byte-for-byte; framing prose around the block is fine. | invariant | L296 `#### Cold-dispatch the Analyst`; L362; L503-L509 DP | F2-021, F2-122, F3-186, F3-188 | dispatch prompt | Issue body | Agent | unknown | procedure |
| FX-PROMPT-5 | Rationale: paraphrasing silently corrupts identifier names (function, flag, type names) the Analyst's research keys against and the worker uses literally. | rationale-only | L296; L503 DP | F2-022 | - | - | none | no | rationale |
| FX-PROMPT-6 | Read the Issue via `bees show-ticket --ids <issue-id>` before composing the prompt. | command | L505-L507 DP | F3-187 | - | Issue id | bees | unknown | procedure |
| FX-PROMPT-7 | The dispatch prompt need not ask the worker to ping back; Agent completion notifications arrive automatically and TaskList is the progress signal. | invariant | L509 DP | F3-189 | - | - | Agent, TaskList | unknown | procedure |
| FX-PROMPT-8 | **Engineer dispatch** MUST embed the Section 3 Approve-branch directive as the **authoritative design source**: `### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`, plus `### Why`, `### Alternatives considered`, `### Options the body did not consider`, plus any user-supplied refinement. | field-or-template | L362; L481; L511 DP | F2-121, F3-177, F3-190 | Engineer prompt | Section 3 Approve output | Agent | no | procedure |
| FX-PROMPT-9 | Recommended labels: `## Authoritative design directive (from Section 3 Analyst pass)` for the three directive sections and `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)` for context. | field-or-template | L511 DP | F3-191 | Engineer prompt headings | - | Agent | no | procedure |
| FX-PROMPT-10 | **Relay the `### Blast radius` section under the heading `## Blast radius`** inside the Engineer's directive block; it is the **enumerated site list** `agents/engineer.md` reconciles its sweep against. | relay | L511 DP | F3-192 | `## Blast radius` heading | `### Blast radius` | Agent | no | procedure |
| FX-PROMPT-11 | **State in the prompt that the directive is the enumeration**: an unnamed mechanism is a design question the Engineer returns under `## Design question`, not a choice it makes. | field-or-template | L511 DP | F3-193 | Engineer prompt | - | Agent | no | procedure |
| FX-PROMPT-12 | Test Writer and Doc Writer prompts do NOT carry the design directive separately; they read the resulting diff per hub-and-spoke. (Conflicts with FX-ANA-60 — see Inconsistencies.) | invariant | L511 DP | F3-196 | - | - | Agent | no | procedure |
| FX-PROMPT-13 | **Code Reviewer and Phase C PM dispatch — relay the Engineer's completeness evidence verbatim:** when any Engineer return for this Issue carried a completeness list, embed it verbatim under a labelled heading, recommended `## Engineer's completeness evidence`. | relay | L513 DP; L721 `### 5.` | F3-197, F5-024, F5-026 | `## Engineer's completeness evidence` | Engineer completeness list | Agent | unknown | procedure |
| FX-PROMPT-14 | Embed the completeness list as text in the prompt (like the Issue body); do **not** write it to a scratch file and pass a path. | invariant | L513 DP; L721 | F3-198, F5-027 | - | - | Agent | unknown | procedure |
| FX-PROMPT-15 | `agents/code-reviewer.md` carries the Code-Reviewer-side half: pass the list through into its `/quo-engineer-review` invocation. | definition | L513 DP | F3-199 | - | - | none | unknown | procedure |
| FX-PROMPT-16 | **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was** — a fact known independently of whether a list came back. | field-or-template | L513 DP; L721 | F3-200, F5-029 | Code Reviewer / PM prompt | assignment shape | Agent | unknown | procedure |
| FX-PROMPT-17 | Sweep-shaped = a directive or Subtask body that directed a change at every site where some property holds. | definition | L721 | F5-030 | - | - | none | unknown | procedure |
| FX-PROMPT-18 | When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emit an empty one, but still state sweep-shaped when true. | field-or-template | L513 DP; L721 | F3-201, F5-032 | prompt | - | Agent | unknown | procedure |
| FX-PROMPT-19 | **Unlike the `## Blast radius` relay, this MUST is not satisfiable on every path**: a compaction after the Engineer returned destroys that round's list; on that resume omit the heading and state the sweep-shaped fact. | recovery | L513 DP; L721 | F3-202, F5-033 | - | - | none | unknown | procedure |
| FX-PROMPT-20 | **State the cost plainly:** on that dispatch `/quo-engineer-review` will report the completeness list as missing; that finding is a **compaction artifact, not an Engineer defect** — from the Code Reviewer or the PM's `/quo-engineer-review` alike. | definition | L513 DP; L721 | F3-203, F5-036 | - | `/quo-engineer-review` finding | none | unknown | procedure |
| FX-PROMPT-21 | Disposition the compaction-artifact finding as ignored feedback per Section 5's ignored-feedback rule: a `defer-<short-suffix>` task annotated `addressed-now-in-this-Issue`, left `pending`, listed in the per-Issue summary's `**Ignored Review Feedback**` field; do not auto-dispatch the Engineer per part (a)'s table. | recovery | L513 DP | F3-204 | `defer-*` task, summary field | finding | TaskList | unknown | procedure |
| FX-PROMPT-22 | Apply the compaction loss per round, not per Issue: embed every list still in hand, each attributed to its Phase A round when more than one round produced one; a destroyed round contributes nothing; omit the heading only when **no** list survives. | recovery | L721 | F5-028, F5-034, F5-035 | attribution labels | surviving lists | none | unknown | procedure |
| FX-PROMPT-23 | Rationale: the PM is a **second** `/quo-engineer-review` caller with no channel to the Phase A Code Reviewer and reviews a wider diff (includes Phase B changes). | rationale-only | L721 | F5-025 | - | - | none | unknown | rationale |
| FX-PROMPT-24 | Rationale: `/quo-engineer-review` reports a missing list only when the invocation named the assignment sweep-shaped; an unnamed sweep silently loses the check. | rationale-only | L721 | F5-031 | - | - | none | unknown | rationale |
| FX-PROMPT-25 | **Code Reviewer and Phase C PM dispatch — relay the Analyst's `### Blast radius` verbatim:** when Section 3's approved proposal carried `### Blast radius`, embed it **verbatim** under the heading `## Blast radius`. | relay | L515 DP; L723 `### 5.` | F3-205, F5-037, F5-038 | `## Blast radius` heading | `### Blast radius` | Agent | no | procedure |
| FX-PROMPT-26 | Use the one heading string `## Blast radius` at every hop; a renamed heading silently drops the review's check. | invariant | L515 DP; L723 | F3-206 | - | - | none | no | procedure |
| FX-PROMPT-27 | Embed `## Blast radius` as text in the prompt; do **not** write it to a scratch file and pass a path. | invariant | L515 DP; L723 | F3-207 | - | - | Agent | no | procedure |
| FX-PROMPT-28 | **Relay it even when the Analyst's section carried only its fixed empty line** (`No invariant added, removed, or weakened.`), so "nothing to verify" is distinguishable from "not supplied". | relay | L515 DP; L723 | F3-208, F5-039 | `## Blast radius` | `### Blast radius` | Agent | no | procedure |
| FX-PROMPT-29 | This `## Blast radius` MUST is satisfiable on every path: a compaction-stranded proposal is re-derived through the Analyst (Read-state step) before this dispatch. | invariant | L515 DP; L723 | F3-209, F5-040 | - | - | none | no | procedure |
| FX-PROMPT-30 | `agents/code-reviewer.md` and `agents/pm.md` forward the `## Blast radius` block into their `/quo-engineer-review` invocation under the same heading. | definition | L515 DP; L723 | F3-210, F5-041 | - | - | none | no | procedure |
| FX-PROMPT-31 | **Test Writer / Doc Writer dispatch** prompts MAY state **"no Engineer Agent will be dispatched for this Issue while you are running"**; keep the `for this Issue` qualifier (fix-mode wording the role files expect). | field-or-template | L517 DP | F3-211 | writer prompt | - | Agent | no | procedure |
| FX-PROMPT-32 | Writer prompts **MUST NOT** claim **"the source tree is frozen"** or any close paraphrase; the orchestrator holds no such lever. | invariant | L517 DP | F3-212 | - | - | Agent | unknown | procedure |
| FX-PROMPT-33 | `agents/test-writer.md` carries the writer-side half (capture tree state, re-check before finishing, stop and report), so recovery does not depend on prompt wording. | definition | L517 DP | F3-213 | - | - | none | unknown | procedure |
| FX-PROMPT-34 | **Test Writer dispatch — supply the fingerprint path list** by carrying forward the Engineer's `## Files changed`, **not by re-deriving from the tree**. | field-or-template | L519 DP | F3-214 | Test Writer prompt | `## Files changed` | Agent | unknown | procedure |
| FX-PROMPT-35 | **Union the lists across every Phase A round**, drop test paths, emit under `## Source paths to fingerprint`, one repository-relative path per line, non-test paths only. | field-or-template | L519 DP | F3-215 | `## Source paths to fingerprint` | `## Files changed` (all rounds) | Agent | unknown | procedure |
| FX-PROMPT-36 | **An explicitly-empty `## Files changed` list is a list, not a missing one**; it contributes nothing to the union and does **not** trigger the fallback. | invariant | L519 DP | F3-216 | - | `## Files changed` | none | unknown | procedure |
| FX-PROMPT-37 | When every round carried a list and the union is empty, **omit the `## Source paths to fingerprint` heading**; the writer's empty-path-set clause keys on the heading being absent. | field-or-template | L519 DP | F3-217 | Test Writer prompt | - | Agent | unknown | procedure |
| FX-PROMPT-38 | **Fallback when an Engineer return did not list files:** run `git diff --name-only HEAD` (identical on POSIX and PowerShell) and drop test paths. | command | L521-L531 DP | F3-218 | path list | working tree | git, Bash | unknown | procedure |
| FX-PROMPT-39 | Prefer the return-carried list; the fallback reads the **whole working tree** and picks up other actors' uncommitted edits, each of which the writer will stop on. | invariant | L533 DP | F3-219 | - | - | git | unknown | procedure |
| FX-PROMPT-40 | When Phase A was empty (no Engineer ran), omit the `## Source paths to fingerprint` heading; `agents/test-writer.md` handles that case. | field-or-template | L533 DP | F3-220 | Test Writer prompt | - | Agent | unknown | procedure |
| FX-PROMPT-41 | When the Issue's `reference_materials` is non-empty, embed the `reference_materials` JSON value alongside the thin body in every dispatch prompt (Analyst included) so the worker can read resolver name and URL. | relay | L297 `#### Cold-dispatch the Analyst`; L545 DP | F2-023, F3-229 | dispatch prompt | `reference_materials` | Agent, bees | no | procedure |
| FX-PROMPT-42 | Workers (Analyst in Section 3, Engineer in Section 4, PM in Section 5) fetch upstream content via `WebFetch` per their role contracts; the orchestrator does NOT pre-fetch the `reference_materials` URL. | invariant | L297; L545 DP | F2-024, F3-231 | - | `reference_materials` | Agent | no | procedure |
| FX-PROMPT-43 | The PM dispatch prompt must include the Issue ID, the Issue body verbatim, the Issue's `up_dependencies` array, and the resolved `<scoped-marker-resolver-path>`; the orchestrator's responsibility ends there (Path A/B selection is the PM's). | field-or-template | L616 `#### Scoped-marker PM dispatch wiring`; L719 `### 5.` | F3-293, F5-020 | PM prompt fields | bees ticket; resolver path | bees, Agent | no | procedure |
| FX-PROMPT-44 | Hub-and-spoke: the worker reads its prompt, edits files, exits; the diff is the handoff to the next role (Code Reviewer in Phase A; Test Writer, Doc Writer, or PM after Phase A closes); no `SendMessage` between roles — workers never message each other, the orchestrator is the hub. | invariant | L485; L549 `#### Hub-and-spoke via substrate` | F3-179, F3-232 | - | - | Agent | unknown | procedure |
| FX-PROMPT-45 | Rationale: hub-and-spoke is a **structural property** of ephemeral background Agents, not a rule to enforce; no inter-Agent channel exists. | rationale-only | L549 | F3-233 | - | - | none | unknown | rationale |
| FX-PROMPT-46 | "Subagents cannot spawn other subagents"; the skill ships **flat orchestration** — every Agent invocation originates from this reconciliation loop, never from a worker. | invariant | L553 `#### Recursive delegation: not supported` | F3-234 | - | - | Agent | unknown | procedure |

---

## 17. ROLES — Roles & lane boundaries

- **Purpose:** Name the eight roles the orchestrator dispatches, what each owns, and that dispatch framing never loosens a role file's lane boundaries; the orchestrator stays in delegate mode and does not carry role prose.
- **Failure it prevents:** A role exception written into a prompt ("you may also write tests") that no coordination channel can make safe (F3-227, F3-228); the orchestrator doing the work itself.
- **Env deps:** Agent, bees. **TaskList-dependent: no.**
- **Rows:** 29 (procedure 24, rationale 0, example 5).
- **Literals:** `agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`, `agents/analyst.md`; `Model: Opus (always)`; `### Feature: <title>`; `## Doc divergence noted`; `reference_materials` resolvers `github-issue`, `linear-issue`, `url`, `file-path`, `bees`; `t1=Doc`; `/quo-file-issue <url>`, `--reference <url>`, `--from-github <url>`; `WebFetch`; contract phrases "Does NOT modify source code, tests, or docs", "Does NOT review <other-lanes>"; `#### Roles dispatched by the orchestrator`.
- **Edges:** Constrains PROMPT and ANA framing; role definitions consumed by LOOP/REVIEW dispatch decisions; PM spec-source resolution feeds SCOPED; Doc Writer's `## Doc divergence noted` consumption feeds DOCV.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ROLES-1 | Framing prose MUST NOT loosen the role boundaries in the dispatched role's `agents/<role>.md`; this applies to **every** role, implementer and review-only alike (Analyst included). | invariant | L298 `#### Cold-dispatch the Analyst`; L535 DP | F2-026, F3-221 | - | `agents/<role>.md` | Agent | unknown | procedure |
| FX-ROLES-2 | Example: MUST NOT tell the Engineer it may also write tests or docs. | invariant | L537 DP | F3-222 | - | - | Agent | unknown | example |
| FX-ROLES-3 | Example: MUST NOT tell the Test Writer it may also modify source code. | invariant | L538 DP | F3-223 | - | - | Agent | unknown | example |
| FX-ROLES-4 | Example: MUST NOT tell the Doc Writer it may also modify source or test files. | invariant | L539 DP | F3-224 | - | - | Agent | unknown | example |
| FX-ROLES-5 | Example: MUST NOT tell the PM or any reviewer it may write source, tests, or docs; contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (reviewers). | invariant | L540 DP | F3-225 | - | - | Agent | unknown | example |
| FX-ROLES-6 | Example: MUST NOT tell one reviewer it may also review another reviewer's lane. | invariant | L541 DP | F3-226 | - | - | Agent | unknown | example |
| FX-ROLES-7 | A temptation to carve a role exception signals a need for orchestrator-level coordination (follow-up dispatch, Issue redirect), NOT a softening clause. | invariant | L543 DP | F3-227 | - | - | Agent | unknown | procedure |
| FX-ROLES-8 | The only handoff is worker → orchestrator (diff in execution mode, JSON return in research mode); "coordinate with the other role's diff" prose cannot make softening safe because that channel does not exist. | invariant | L543 DP | F3-228 | - | - | Agent | unknown | procedure |
| FX-ROLES-9 | The orchestrator dispatches three implementer roles per Issue; role contracts live in the role files; invoke the right role at the right time, do not carry the role's prose (dispatch roles; do not carry role prose). | definition | L559 `#### Roles dispatched by the orchestrator`; L727 `### 5.` | F3-237, F5-044 | - | - | Agent | unknown | procedure |
| FX-ROLES-10 | **Engineer** (`agents/engineer.md`) implements source-code changes for the fix; Model: Opus (always); does not write tests or docs. | definition | L561 | F3-238 | - | - | Agent | unknown | procedure |
| FX-ROLES-11 | **Test Writer** (`agents/test-writer.md`) writes/updates/deletes tests and ensures at least one test fails before the fix and passes after; Model: Opus (always). | definition | L562 | F3-239 | - | - | Agent | unknown | procedure |
| FX-ROLES-12 | **Doc Writer** (`agents/doc-writer.md`) reviews the diff for doc gaps, updates docs, and appends/updates the `### Feature: <title>` subsection in cumulative PRD/SDD per CLAUDE.md `## Documentation Locations`; Model: Opus (always). | definition | L563 | F3-240 | - | `## Documentation Locations` | Agent | unknown | procedure |
| FX-ROLES-13 | In fix mode the Doc Writer is dispatched once per Issue (not per Subtask), and the Plan Bee is discovered via the Issue's `up_dependencies`; `agents/doc-writer.md` is authoritative for that traversal. | definition | L563 | F3-241 | - | `up_dependencies` | none | no | procedure |
| FX-ROLES-14 | When the Issue body contains a `## Doc divergence noted` section (from `/quo-file-issue`), the Doc Writer treats it as an explicit doc-correction directive. | definition | L563 | F3-242 | - | `## Doc divergence noted` | none | no | procedure |
| FX-ROLES-15 | Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) and the PM (`agents/pm.md`) are introduced in Section 5; the PM is always dispatched alongside the reviewers. | definition | L565 | F3-243 | - | - | Agent | unknown | procedure |
| FX-ROLES-16 | **Code Reviewer** (`agents/code-reviewer.md`) reviews the Engineer's output against engineering standards; dispatched in **Phase A**, alone, looping with the Engineer. | definition | L729 `### 5.` | F5-045 | - | - | Agent | unknown | procedure |
| FX-ROLES-17 | **Test Reviewer** (`agents/test-reviewer.md`) reviews the Test Writer's output against test-quality standards. | definition | L730 | F5-046 | - | - | Agent | unknown | procedure |
| FX-ROLES-18 | **Doc Reviewer** (`agents/doc-reviewer.md`) reviews the Doc Writer's output against documentation standards. | definition | L731 | F5-047 | - | - | Agent | unknown | procedure |
| FX-ROLES-19 | **Product Manager** (`agents/pm.md`; Model: Opus (always)) reviews the fix against the spec source (Issue body plus PRD/SDD paths from CLAUDE.md `## Documentation Locations`, optionally Scoped-marker-narrowed via a Plan Bee in `up_dependencies`) and flags scope creep or divergence. | definition | L732 | F5-048, F5-054 | - | `## Documentation Locations`; `up_dependencies` | Agent | unknown | procedure |
| FX-ROLES-20 | Issues filed by `/quo-file-issue` in default in-conversation mode carry no `reference_materials`; the body itself is the spec. | definition | L732 | F5-049 | - | `reference_materials` | none | no | procedure |
| FX-ROLES-21 | Issues filed via `/quo-file-issue <url>`, `--reference <url>` / `--from-github <url>`, or this skill's URL-resolution sub-step all produce the same `reference_materials` shape: external-URL `value` and `resolver` ∈ {`github-issue`, `linear-issue`, `url`}; the PM fetches via `WebFetch`. | definition | L545 DP; L732 | F3-230, F5-050 | - | `reference_materials.value`, `.resolver` | none | no | procedure |
| FX-ROLES-22 | A Plan Bee reached through `up_dependencies` may resolve `reference_materials` via `file-path` (Scoped-marker narrowing applies) or `bees` (walk the Spec Bee's `t1=Doc` children). | definition | L732 | F5-051 | - | resolvers | bees | unknown | procedure |
| FX-ROLES-23 | `agents/pm.md` is the authoritative spec for the `file-path`, `bees`, and external-URL resolver paths; body-as-spec is the fallback when `reference_materials` is null/empty. | definition | L732 | F5-052 | - | - | none | unknown | procedure |
| FX-ROLES-24 | Do not pre-judge spec-drift risk; the PM reads the spec sources and self-short-circuits per `agents/pm.md` when the collective sources carry no substantive content / no spec-drift surface exists. | definition | L717; L732 | F5-019, F5-053 | - | - | Agent | unknown | procedure |
| FX-ROLES-25 | **IMPORTANT**: stay in delegate mode and do not do the work yourself — during the review loop and during post-completion fixes alike. | invariant | L736 `### 5.`; L1260 PC step 6 | F5-061, F7-097 | - | - | Agent | unknown | procedure |
| FX-ROLES-26 | Section 5 carries the Code Reviewer's dispatch shape and TaskList name for Phase A to use, but not its trigger. | definition | L706 `### 5.` | F5-005 | - | - | none | no | procedure |
| FX-ROLES-27 | Reviewer and PM Agents take dispatch shape and TaskList naming from Section 5; **Code Reviewer** in **Phase A** interleaved with the Engineer; **Test Reviewer**, **Doc Reviewer**, **PM** in **Phase C**. | ordering | L495 `#### Per-issue cold dispatch` | F3-184 | - | - | Agent | unknown | procedure |
| FX-ROLES-28 | The Product Manager is not an implementer-phase role; it is dispatched in **Phase C** alongside the remaining reviewers on every Issue. | ordering | L493 | F3-183 | PM dispatch | - | Agent | unknown | procedure |
| FX-ROLES-29 | **Engineer** is dispatched in **Phase A** when source needs modification (alone, looping with the Code Reviewer); **Test Writer** in **Phase B**, once, when tests need modification; **Doc Writer** in **Phase B**, once, always — it decides whether docs need updating; the orchestrator does not pre-judge. | ordering | L489-L491 | F3-181, F3-182 | Test Writer, Doc Writer dispatches | - | Agent | unknown | procedure |

---

## 18. TASK — TaskList progress UI & naming convention

- **Purpose:** Use Claude Code's native TaskList as the only progress UI — exactly one task per dispatched Agent, deterministic issue-scoped names with suffix discriminators, plus the non-Agent name classes (`aborted-*`, `defer-*`, `gate-*`, `file-from-url-*`, `*-postcomp-*`) — so every routing test can match on prefix + status.
- **Failure it prevents:** not stated directly (implicit: ambiguous names breaking prefix-matched preconditions and close-out sweeps; shared task names hiding concurrent lanes — F7-100).
- **Env deps:** TaskList, Agent, git, bees. **TaskList-dependent: yes** (the mechanism *is* TaskList).
- **Rows:** 31 (procedure 30, rationale 1).
- **Literals:** `#### TaskList as progress UI`; `##### TaskList naming convention`; statuses `pending` / `in_progress` / `completed`; `metadata.activity`; names `analyst-<issue-id>`, `analyst-<issue-id>-rev<n>` (`analyst-veq`, `analyst-veq-rev1`), `<role>-<issue-id>` (`engineer-veq`, `test-writer-veq`, `doc-writer-veq`), `-r<n>` (`engineer-veq-r1`, `code-reviewer-veq-r1`, `doc-writer-veq-r1`), `<reviewer>-<issue-id>` (`code-reviewer-veq`, `test-reviewer-veq`, `doc-reviewer-veq`), `pm-<issue-id>` (`pm-veq`), `aborted-<role>-<issue-id>`, `aborted-<role>-postcomp-<n>`, `gate-<kind>-<short-suffix>` (`gate-askuserquestion-veq`, `gate-askuserquestion-1`), `<role>-postcomp-<n>` (`engineer-postcomp-1`, `doc-writer-postcomp-2`), `<role>-postcomp-<n>-r<k>` (`test-writer-postcomp-2-r1`), `file-issue-postcomp-<n>`; scopes **Issue scope** / **Run scope** / **Turn scope** / **post-completion scope**.
- **Edges:** Consumed by every mechanism that creates or tests tasks (ANA, ENGPRE, MOVE, GATE, LEDGER, CLOSE, ABORT, POSTC); `file-from-url-<n>` lives in ARG, `defer-*` naming in LEDGER, `gate-*` mechanics in GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-TASK-1 | Use Claude Code's native **TaskList** as the visible progress UI; there is no separate display backend to configure. | invariant | L569 `#### TaskList as progress UI` | F3-244 | - | - | TaskList | unknown | procedure |
| FX-TASK-2 | For every dispatched Agent, create exactly **one** TaskList task; two findings needing Engineer follow-ups dispatch to distinct names (`engineer-postcomp-1`, `engineer-postcomp-3`), never a shared `engineer-postcomp`. | invariant | L571; L1260 PC step 6 | F3-245, F7-100 | TaskList task | - | TaskList | unknown | procedure |
| FX-TASK-3 | Each in-flight Agent's task `status` is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done); the lifecycle is `pending` → `in_progress` → `completed`. | definition | L384 RL; L300 `#### Cold-dispatch the Analyst` | F3-010, F2-028 | - | TaskList | TaskList | unknown | procedure |
| FX-TASK-4 | **`pending`** — created when the orchestrator decides the role is next for the current Issue, before the Agent invocation lands. | definition | L573 | F3-246 | task status | - | TaskList | unknown | procedure |
| FX-TASK-5 | **`in_progress`** — set the moment `Agent(...)` returns. | definition | L574 | F3-247 | task status | Agent dispatch | TaskList, Agent | unknown | procedure |
| FX-TASK-6 | **`completed`** — set when the completion notification is processed and deliverables are confirmed landed (`git status` / `git diff`, bees transitions on disk). (Exception: FX-MOVE-29.) | definition | L575 | F3-248 | task status | Agent notification, git, bees | TaskList, git, bees | unknown | procedure |
| FX-TASK-7 | Use `metadata.activity` for finer-grained progress from intermediate worker signal; update opportunistically; it is informational, not a routing input. | invariant | L577 | F3-250 | `metadata.activity` | - | TaskList | unknown | procedure |
| FX-TASK-8 | The naming convention is the **canonical cross-reference** for Section 5 (reviewer dispatches) and Section 7 (TaskList completion at close-out); it is deterministic and unambiguous. | definition | L581 TNC | F3-251 | - | - | TaskList | unknown | procedure |
| FX-TASK-9 | Naming is **issue-scoped** for every per-issue role; the scope suffix is always the Issue id. | invariant | L583 TNC | F3-252 | - | Issue id | TaskList | no | procedure |
| FX-TASK-10 | **Analyst Agents**: `analyst-<issue-id>` (e.g. `analyst-veq` for Issue `b.veq`); track the Section 3 dispatch under this name. | name-class | L300; L585 TNC | F2-027, F3-254 | task name | - | TaskList | no | procedure |
| FX-TASK-11 | On `Revise`, append `-rev<n>` with `<n>` the 1-based revision count (`analyst-veq-rev1`, `analyst-veq-rev2`); the same discriminator is used when the design-question rung re-dispatches the Analyst. | name-class | L334; L585 TNC | F2-085, F3-255, F3-256 | task name | gate answer `Revise` | Agent, TaskList | no | procedure |
| FX-TASK-12 | **Implementer Agents**: `<role>-<issue-id>` (`engineer-veq`, `test-writer-veq`, `doc-writer-veq`). | name-class | L586 TNC | F3-257 | task name | - | TaskList | unknown | procedure |
| FX-TASK-13 | **Round discriminator for repeat dispatches**: every dispatch after the first appends `-r<n>`, `<n>` the 1-based re-dispatch count (`engineer-veq-r1`, `engineer-veq-r2`, `doc-writer-veq-r1`; `code-reviewer-veq-r1` for the second Phase A review round); every Phase A round after the first and every movement re-dispatch takes the next `-r<n>` name. | name-class | L402 RL; L436 RL; L586-L587 TNC | F3-065, F3-127, F3-258, F3-262 | task names | - | TaskList | unknown | procedure |
| FX-TASK-14 | Rationale: `-r<n>` differs from `-rev<n>` because they count different things (review rounds vs Analyst revisions). | rationale-only | L586 TNC | F3-259 | - | - | none | no | rationale |
| FX-TASK-15 | Because the discriminator is a **suffix**, every name-testing rule (most importantly the Engineer-dispatch precondition) matches on name **prefix** plus status. | invariant | L586 TNC | F3-260 | - | TaskList | TaskList | unknown | procedure |
| FX-TASK-16 | **Reviewer Agents**: `<reviewer>-<issue-id>` — `code-reviewer-<issue-id>` (Phase A, `Agent(subagent_type="code-reviewer", run_in_background=true)`), `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>` (Phase C); dispatch shape from Section 5. | name-class | L587 TNC; L708 `### 5.` | F3-261, F5-010, F5-011 | task names; Agent dispatch | - | TaskList, Agent | unknown | procedure |
| FX-TASK-17 | **PM Agents**: `pm-<issue-id>` (`pm-veq`), dispatched per Issue in Section 5 alongside the reviewers. | name-class | L588 TNC; L708 | F3-263 | task name | - | TaskList | unknown | procedure |
| FX-TASK-18 | **Aborted-writer redelivery markers**: `aborted-<role>-<issue-id>` (`aborted-test-writer-veq`, `aborted-doc-writer-veq`) at **Issue scope**; `aborted-<role>-postcomp-<n>` at **post-completion scope** with `<n>` the same finding index as the lane it marks. | name-class | L589 TNC; L1260 PC | F3-264, F7-117 | task name | - | TaskList | unknown | procedure |
| FX-TASK-19 | **Gate-task tasks** — **Turn scope**: `gate-<kind>-<short-suffix>`; dominant `<kind>` is `askuserquestion` (`gate-askuserquestion-veq` for the Section 3 gate on `b.veq`, `gate-askuserquestion-1` otherwise); `<short-suffix>` may be the Issue's short-id slug or any collision-resistant suffix not colliding with `analyst-<issue-id>`. | name-class | L319; L592 TNC | F2-064, F3-279 | task name | - | TaskList | unknown | procedure |
| FX-TASK-20 | Post-completion names (`<role>-postcomp-<n>` / `file-issue-postcomp-<n>`) and `defer-*` names coexist without overlap; they track different lifecycles. | definition | L591 TNC | F3-278 | - | - | TaskList | unknown | procedure |
| FX-TASK-21 | The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<issue-id>`, `analyst-<issue-id>`, `pm-<issue-id>`, the three reviewer names, `file-from-url-<n>`, aborted markers, and Section 8 post-completion names, with or without `-r<n>`. | definition | L592 TNC | F3-287 | - | - | TaskList | unknown | procedure |
| FX-TASK-22 | Section 4's issue-scoped naming does not cover post-completion follow-up Agents; use the **post-completion-scoped** name `<role>-postcomp-<n>`. | name-class | L1260 PC step 6 | F7-098 | `<role>-postcomp-<n>` task | - | TaskList | yes | procedure |
| FX-TASK-23 | `<n>` in `<role>-postcomp-<n>` is the 1-based index of the finding in the fresh reviewer's numbered list (`engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`). | definition | L1260 | F7-099 | - | reviewer numbered list | TaskList | yes | procedure |
| FX-TASK-24 | Post-completion names take **no** issue-id suffix and normally no round discriminator — the per-finding index is the discriminator. | invariant | L1260 | F7-101 | - | - | TaskList | yes | procedure |
| FX-TASK-25 | Carve-out: a round discriminator IS permitted and required when a post-completion writer lane is re-dispatched after a movement abort — append `-r<k>`. | name-class | L1260 | F7-102 | `<role>-postcomp-<n>-r<k>` task | movement abort | TaskList | yes | procedure |
| FX-TASK-26 | `<k>` is the 1-based re-dispatch count for that role at that finding index (e.g., `test-writer-postcomp-2-r1`). | definition | L1260 | F7-103 | - | - | TaskList | yes | procedure |
| FX-TASK-27 | `/quo-execute`'s post-completion naming entry carries the identical `-r<k>` carve-out, so the two skills read as one convention. | invariant | L1260 | F7-104 | - | - | none | yes | procedure |
| FX-TASK-28 | Outside the movement-abort re-dispatch case, do not append a round discriminator to a post-completion name. | invariant | L1260 | F7-105 | - | - | TaskList | yes | procedure |
| FX-TASK-29 | TaskList entries for per-finding filing in Section 8 are named `file-issue-postcomp-<n>` (`<n>` = 1-based finding index); they are created by the "File as issue tickets" branch, which invokes `/quo-file-issue` per finding rather than dispatching an Agent. | name-class | L1246; L1269 PC step 6 | F7-086, F7-143 | `file-issue-postcomp-<n>` task | - | TaskList | unknown | procedure |
| FX-TASK-30 | If a tracking entry is created for a design-question filing in Section 8, reuse the existing `file-issue-postcomp-<n>` name at the same finding index. | name-class | L1260 | F7-114 | `file-issue-postcomp-<n>` task | - | TaskList | unknown | procedure |
| FX-TASK-31 | The orchestrator typically creates ad-hoc self-tracking TaskList tasks during Section 8 (e.g., "Get diff scope", per-issue "Verify <id>", "Synthesize findings"). | definition | L1246 PC | F7-082 | self-tracking tasks | - | TaskList | unknown | procedure |

---

## 19. GATE — `gate-*` two-step contract

- **Purpose:** Every workflow `AskUserQuestion` is preceded, in the same turn, by a `gate-askuserquestion-<short-suffix>` TaskList task, closed once the answer is consumed, never narrated, never yielded on while open — a structural mitigation for the narrate-instead-of-do failure mode.
- **Failure it prevents:** The orchestrator describing a gate in prose instead of firing it; a stranded `pending` `gate-*` task producing a phantom prompt later (F1-042); yielding with a decision still open.
- **Env deps:** TaskList, AskUserQuestion. **TaskList-dependent: yes.**
- **Rows:** 12 (procedure 10, rationale 2).
- **Literals:** `TaskCreate`; `AskUserQuestion`; `gate-askuserquestion-<short-suffix>`; `gate-*`; `metadata.activity`; auto-appended `Type something.` / `Chat about this`; **yield-control discipline**; **Two-step gate mechanics (parts (c) and (d)).**
- **Edges:** Instantiated by EFF, ANA, UNEXP, ROUTE (c)/(d), HYG Step 2/3, GUARD Step 5, POSTC step 5, SRGATE; naming in TASK (FX-TASK-19); RECOV overrides the generic re-fire for the Section 3 gate (FX-RECOV-15).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-GATE-1 | Two-step contract: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (via `TaskCreate`, immediately before the prescribed tool call), **then** call `AskUserQuestion` with the finite choices in the same turn. | gate | L592 TNC; L654/L676/L700 ODR; L930 CWG; L981/L1064 §7.5; L1250 PC; L1272 PC | F3-280, F4-062, F4-111, F4-151, F4-152, F4-153, F5-217, F6-001, F6-003, F6-005, F6-131, F6-132, F7-088, F7-089, F7-090, F7-154, F7-156 | gate task; question | - | TaskList, AskUserQuestion | yes | procedure |
| FX-GATE-2 | Do not produce a text response describing the gate — fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L700 ODR; L1250 PC; L1272 PC | F4-154, F7-091, F7-157 | - | - | TaskList, AskUserQuestion | yes | procedure |
| FX-GATE-3 | Mark the `gate-*` task `completed` the moment the prescribed tool call returns and its result is consumed (answer routed, branch entered); normally within a single turn. | command | L592 TNC; L700 ODR; L930 CWG; L981/L1064 §7.5; L1250/L1272 PC | F3-284, F4-155, F5-219, F6-006, F6-133, F7-092, F7-158 | task `completed` | tool result | TaskList | yes | procedure |
| FX-GATE-4 | The `<short-suffix>` MUST be unique per fire within the run across every `gate-*` task regardless of `<kind>` (monotonic integers or gate-specific slugs), so concurrent or repeated fires — e.g. a Step 3 re-fire vs the Step 2 first fire — do not collide. | invariant | L592 TNC; L981 §7.5; L1272 PC | F3-281, F6-004, F7-155 | - | - | TaskList | yes | procedure |
| FX-GATE-5 | Workflow gates are multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot. | invariant | L700 ODR; L930 CWG; L1272 PC | F4-156, F5-223, F7-159 | - | - | AskUserQuestion | yes | procedure |
| FX-GATE-6 | **Yield-control discipline**: MUST NOT yield control while any `gate-*` task is `pending` or `in_progress` (mirrors `defer-*`). | invariant | L592 TNC; L930 CWG | F3-285, F5-218 | - | TaskList | TaskList | yes | procedure |
| FX-GATE-7 | If a `gate-*` task is left active when the orchestrator would yield, the next tick walks the TaskList, surfaces it, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. | recovery | L592 TNC | F3-286 | re-fired gate | `metadata.activity` | TaskList, AskUserQuestion | unknown | procedure |
| FX-GATE-8 | `metadata.activity` on a gate task carries the gate's finite choices verbatim where applicable. | field-or-template | L592 TNC | F3-283 | `metadata.activity` | gate options | TaskList | unknown | procedure |
| FX-GATE-9 | The two-step contract applies at every gate: Section 5 escalation gates, Section 1's conditional session-effort gate, Section 3's approval gate, Section 4's **unexplained-movement gate**, Section 7.5's deferral-hygiene gate, Section 8's post-completion findings gate. | invariant | L592 TNC | F3-282 | - | - | TaskList, AskUserQuestion | unknown | procedure |
| FX-GATE-10 | Do NOT create a `gate-*` task before the condition that decides whether the gate fires has been evaluated (effort floor comparison; gauge reading in hand). | invariant | L43 `#### Check session reasoning effort`; L863 CWG | F1-041, F5-191 | - | - | TaskList | yes | procedure |
| FX-GATE-11 | Rationale: a stranded `pending` `gate-*` task violates yield-control discipline; the contract's recovery re-fires the tool from leftover `gate-*` tasks, producing a phantom prompt later. | rationale-only | L43 | F1-042 | - | - | TaskList | yes | rationale |
| FX-GATE-12 | These gates inherit a prose-adherence fragility — narrowed (not closed) by the two-step contract; an execution-time risk acknowledged at run time, not something the prose fixes; do not claim it is fixed. | rationale-only | L702 ODR; L1272 PC | F4-157, F7-162 | - | - | none | yes | rationale |

---

## 20. SCOPED — Scoped-marker PM wiring

- **Purpose:** Hand the PM the runtime-resolved path of the sibling `scoped_marker_resolver.py` helper (plus Issue ID and `up_dependencies`) so `agents/pm.md` can run its Path B Scoped-marker check; the orchestrator never inlines the grammar or the helper call.
- **Failure it prevents:** not stated.
- **Env deps:** Agent, none. **TaskList-dependent: no.**
- **Rows:** 5 (procedure 5).
- **Literals:** `#### Scoped-marker PM dispatch wiring`; `<scoped-marker-resolver-path>`; `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (POSIX) / `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py` (PowerShell); **Path B** / Path A; **no Grandparent Bee**.
- **Edges:** Feeds PROMPT's PM prompt (FX-PROMPT-43); sibling-resolution discipline shared with SHELL (FX-SHELL-5); consumed by ROLES' PM definition.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-SCOPED-1 | The Section 5 PM dispatch prompt must include the **resolved path** to the Scoped-marker helper as a `<scoped-marker-resolver-path>` substitution, filled at runtime so `agents/pm.md` can run its Scoped-marker check. | field-or-template | L596 `#### Scoped-marker PM dispatch wiring`; L719 `### 5.` | F3-288, F5-021 | PM prompt | resolved path | Agent | unknown | procedure |
| FX-SCOPED-2 | Resolve the helper at runtime from this skill's base directory: `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (POSIX) / `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py` (PowerShell). | command | L598-L612 | F3-289 | resolved path | skill base directory | none | yes | procedure |
| FX-SCOPED-3 | The PM prompt's context selects **Path B** of `agents/pm.md`'s Scoped-marker logic: it names an **Issue ID** and the Issue's **`up_dependencies`** array, with **no Grandparent Bee**. | definition | L614 | F3-291 | PM prompt | Issue ID, `up_dependencies` | Agent | no | procedure |
| FX-SCOPED-4 | Path B iterates `up_dependencies` for a Plan Bee with a Scoped marker, falling back best-effort to the unscoped spec; Path A (Grandparent Bee, hard-fail) is the `quo-execute` path and does not apply. | definition | L614 | F3-292 | - | - | none | no | procedure |
| FX-SCOPED-5 | Do **not** inline the Scoped-marker grammar, the temp-file recipe, or the helper invocation; `agents/pm.md` owns those and the Path A vs Path B selection. | invariant | L616 | F3-294 | - | - | none | unknown | procedure |

---

## 21. ROUTE — Routing discipline (ODR parts (a)–(g), Severity bounds the loop)

- **Purpose:** Turn each reviewer finding (severity + enumerated fix paths with depth tags) into exactly one routing decision: pick the highest-quality path, then route deterministically — ungated dispatch (row 6), scope-bounding gate (c), or routing-decision gate (d) — with severity bounding when a lane closes and part (g) ordering any source-changing re-dispatch.
- **Failure it prevents:** Silently narrowing a fix by inlining scope-bounds into a prompt (F4-055); building a mechanism the ticket never asked for inside this unit (F4-109); accepting or un-narrowed-deferring a `blocker`; a writer redoing work on a diff the pending code review rewrites (F4-145); infinite review loops over `trivial-tweak` nits.
- **Env deps:** AskUserQuestion, TaskList, Agent, bees, none. **TaskList-dependent: yes** (gate tasks, `defer-*` dispositions).
- **Rows:** 127 (procedure 118, rationale 8, example 1).
- **Literals:** `### Orchestrator discipline: routing review findings`; **Severity bounds the loop.**; severity tags `blocker` / `suggestion` / `nit`; depth tags `trivial-tweak` / `refactor-locally` / `re-architect`; `[preferred]`; `[introduces-mechanism]`; **(a) Pick the path, then route on it.** — **Step 1 — pick.** / **Step 2 — route on the path chosen in Step 1.**; rows 1–6; **What "highest-quality" means.**; **What "introduces a mechanism" means.**; **(b) ANTI-PATTERN — do not write this:** with forbidden phrasings `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`; **(c) Scope-bounding gate.** choices `Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`, `Re-dispatch the Analyst with this finding`; `(Recommended)`; **Recommended default on the mechanism row.**; **(d) Routing-decision gate.** choices one-per-fix-path, `Defer to follow-up Issue`, `Cancel`, `Re-dispatch the Analyst with this finding`; **(e) Backwards-compatibility shim.**; **(f) Edge-case handling.** (**Malformed tags.**, **Routing ambiguity.**, **`/quo-file-issue` failure at the Defer gate.**); **(g) Re-dispatch ordering when a fix path changes source.**; `Ctrl-C`; `## Authoritative design directive`; `N nits applied without re-review` / `count unavailable post-compaction` (rendered by SUM).
- **Edges:** Consumes reviewer returns from LOOP/REVIEW, DIR (approved design for mechanism detection), `agents/analyst.md` mechanism definition; Produces dispatches (PROMPT), tracker entries via TRACK Triggers A/B/C, `defer-*` tasks via LEDGER, Analyst re-dispatch via DQ, `Cancel` → ABORT, `/quo-file-issue` inline (ARG precedent); gates through GATE; nit counts to SUM.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ROUTE-1 | Each reviewer finding carries a severity tag that is exactly one of `blocker` / `suggestion` / `nit`. | definition | L620 ODR intro | F4-001 | - | reviewer finding | none | yes | procedure |
| FX-ROUTE-2 | Each fix path a finding proposes carries a depth tag `trivial-tweak` / `refactor-locally` / `re-architect`; the finding also carries the count of fix paths surfaced. | definition | L620 | F4-002 | - | reviewer finding | none | yes | procedure |
| FX-ROUTE-3 | Turn the reviewer's enumerated fix paths and depth tags into exactly one routing decision per finding. | invariant | L620 | F4-003 | routing decision | fix paths, depth tags | none | yes | procedure |
| FX-ROUTE-4 | Whether a gate fires is decided deterministically; which path is picked when no gate fires is the orchestrator's own judgment. | invariant | L620 | F4-004 | - | - | none | yes | procedure |
| FX-ROUTE-5 | Never re-classify or invent a reviewer's depth tag; read the depth of a path as emitted. | invariant | L620 | F4-005 | - | depth tag | none | yes | procedure |
| FX-ROUTE-6 | A review lane's loop (Engineer → code-review at any site; each writer → reviewer pair) is held open by `blocker` and `suggestion` findings and by any `nit` whose chosen path is deeper than `trivial-tweak`. | invariant | L622 SBL | F4-006 | - | severity, chosen depth | none | yes | procedure |
| FX-ROUTE-7 | A lane closes when no lane-holding finding remains outstanding. | invariant | L622 SBL | F4-007 | lane closure | FX-ROUTE-6 | none | yes | procedure |
| FX-ROUTE-8 | A lane-holding finding stays outstanding until a later cold pass no longer raises it or it reaches a disposition under which no fix lands against it. | invariant | L622 SBL | F4-008 | - | cold-pass result | Agent | yes | procedure |
| FX-ROUTE-9 | "Routed" / no-fix dispositions: accepted into the compromise tracker (Section 7.5), recorded as a `defer-*` task (Section 5 ignored-feedback rule), or closed by a gate answer `Accept the limitation`, `Cancel`, or `Defer to follow-up Issue` when nothing ships against the finding this round — gated **and settled by that gate's answer**. | definition | L402 RL; L622 SBL | F3-061, F4-009 | tracker entry, `defer-*` task, gate answer | - | TaskList, AskUserQuestion | yes | procedure |
| FX-ROUTE-10 | A dispatch settles nothing — ungated at row 6, chosen at a gate, or the soft fix / narrowing shipped alongside a deferral — until a later cold pass has read its result; the loop continues until a cold pass has read that dispatch. | invariant | L402 RL; L622 SBL | F3-062, F4-010 | - | dispatch, cold pass | Agent | yes | procedure |
| FX-ROUTE-11 | A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own. | invariant | L622 SBL | F4-011 | - | severity + depth | none | yes | procedure |
| FX-ROUTE-12 | When a lane-holding finding already forces another implementer round, `trivial-tweak` nits ride along in it and the next cold pass reads them with everything else. | ordering | L622 SBL | F4-012 | implementer dispatch | FX-ROUTE-6, -11 | Agent | yes | procedure |
| FX-ROUTE-13 | When only `trivial-tweak` nits remain (a return whose findings are all `nit`s with `trivial-tweak` paths, shipped as such, no gate substituting a deeper fix), apply them in one final implementer pass for that lane and dispatch no further reviewer round: this closes Phase A (Code Reviewer) or **that reviewer's lane** (writer lanes) after **one** pass. | ordering | L402 RL; L418 RL; L622 SBL; L739 `### 5.` | F3-063, F3-095, F4-013, F5-065 | final implementer dispatch; lane closure | FX-ROUTE-11 | Agent | yes | procedure |
| FX-ROUTE-14 | At a site where a review runs inside the PM's in-flight review passes, "no further reviewer round" means do not re-dispatch the PM for that lane. | ordering | L622 SBL | F4-014 | - | FX-ROUTE-13 | Agent | yes | procedure |
| FX-ROUTE-15 | `trivial-tweak` nits applied without re-review are finished work: never list them as ignored feedback and never make them `defer-*` tasks. | invariant | L622 SBL | F4-017 | - | FX-ROUTE-13 | TaskList | yes | procedure |
| FX-ROUTE-16 | A `nit` whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding. | invariant | L622 SBL | F4-018 | - | part (a) table | none | yes | procedure |
| FX-ROUTE-17 | The bound keys on what ships: when a gate answer ships anything other than the enumerated `trivial-tweak` path (`Fix properly now` on a row-2/-3/-4 fire, or a `Defer`'s soft fix / narrowing), the finding is lane-holding again, a cold pass must read that fix, and part (g)'s elision does not apply. | invariant | L622 SBL | F4-019 | - | gate answer | Agent | yes | procedure |
| FX-ROUTE-18 | When the final pass ships only `trivial-tweak` paths and changes source, part (g)'s ordering applies with its code-review rung elided; that rung is the one round this rule suppresses. | ordering | L622 SBL | F4-020 | Engineer + writer dispatch | FX-ROUTE-13 | Agent | yes | procedure |
| FX-ROUTE-19 | The bound is the reviewer's own depth tag, not a narrower reading of `nit`; severity means importance, orthogonal to depth. | invariant | L622 SBL | F4-021 | - | depth tag | none | yes | procedure |
| FX-ROUTE-20 | Rationale: the coverage given up is exactly the `trivial-tweak`-nit class — the raising cold pass already read the text, the fix is a `trivial-tweak` by the reviewer's tag, and the post-completion review reads the whole diff. | rationale-only | L622 SBL | F4-022 | - | - | none | yes | rationale |
| FX-ROUTE-21 | Routing is a two-step procedure: Step 1 (pick) is the orchestrator's judgment; Step 2 (route) is deterministic given the chosen path. | ordering | L624 ODR (a) | F4-023 | - | - | none | yes | procedure |
| FX-ROUTE-22 | Step 1: choose the highest-quality fix path among those the reviewer enumerated. | command | L626 (a) Step 1 | F4-024 | chosen path | enumerated fix paths | none | yes | procedure |
| FX-ROUTE-23 | Treat the reviewer's `[preferred]` token as an input, not a verdict: prefer it when it is also the most complete path. | invariant | L626 | F4-025 | - | `[preferred]` | none | yes | procedure |
| FX-ROUTE-24 | When `[preferred]` marks a narrowing and a fuller path is still the smallest internally-consistent complete change, take the fuller path. | invariant | L626 | F4-026 | chosen path | `[preferred]` | none | yes | procedure |
| FX-ROUTE-25 | The pick is always one of the paths the reviewer enumerated. | invariant | L626 | F4-027 | - | enumerated fix paths | none | yes | procedure |
| FX-ROUTE-26 | When no enumerated path is the smallest internally-consistent complete change, pick the most complete of them anyway. | recovery | L626 | F4-028 | chosen path | enumerated fix paths | none | yes | procedure |
| FX-ROUTE-27 | An incomplete pick routes via rows 2, 3, or 4 to gate (c), where `Fix properly now` dispatches the complete fix. | ordering | L626 | F4-029 | gate (c) fire | FX-ROUTE-26 | AskUserQuestion | yes | procedure |
| FX-ROUTE-28 | Exception: a finding whose depth tag is absent or malformed goes via row 1 to gate (d), which has no `Fix properly now`; the user picks among the paths as emitted. | ordering | L626 | F4-030 | gate (d) fire | depth tag | AskUserQuestion | yes | procedure |
| FX-ROUTE-29 | Rationale: an under-enumerated menu becomes visible in session — a gate fires where it otherwise would not, and the user sees the menu it fired on. | rationale-only | L626 | F4-031 | - | - | none | yes | rationale |
| FX-ROUTE-30 | A durable record of an incomplete menu reaches the post-completion review only via Trigger A (`Defer to follow-up Issue`) or Trigger B (`Accept the limitation`); `Fix properly now` writes none. | definition | L626 | F4-032 | tracker entry (A/B) | gate answer | none | unknown | procedure |
| FX-ROUTE-31 | The orchestrator does not absorb an enumeration gap by writing a fix path of its own. | invariant | L626 | F4-033 | - | - | none | yes | procedure |
| FX-ROUTE-32 | Step 2: evaluate the table conditions in order, taking the first that matches, so each finding yields exactly one routing decision. | ordering | L628 (a) Step 2 | F4-034 | routing decision | chosen path | none | yes | procedure |
| FX-ROUTE-33 | Row 1: the finding carries no depth tag, or a malformed severity/depth tag → treat as `re-architect` → gate (d). | ordering | L633 table | F4-035 | gate (d) fire | tags | AskUserQuestion | yes | procedure |
| FX-ROUTE-34 | Row 2: the chosen path carries the reviewer's `[introduces-mechanism]` tag, or introduces a mechanism by the orchestrator's own reading → scope-bounding gate (c). | ordering | L634-L635 table | F4-036 | gate (c) fire | `[introduces-mechanism]` | AskUserQuestion | yes | procedure |
| FX-ROUTE-35 | Row 3: the chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers → gate (c). | ordering | L636-L637 table | F4-037 | gate (c) fire | chosen path, ticket body | AskUserQuestion | yes | procedure |
| FX-ROUTE-36 | Row 4: the chosen path is narrower than the smallest internally-consistent complete fix (leaves the stated defect partly unfixed) → gate (c). | ordering | L638-L639 table | F4-038 | gate (c) fire | chosen path | AskUserQuestion | yes | procedure |
| FX-ROUTE-37 | Row 5: the chosen path's depth tag is `re-architect` → routing-decision gate (d). | ordering | L640 table | F4-039 | gate (d) fire | depth tag | AskUserQuestion | yes | procedure |
| FX-ROUTE-38 | Row 6: otherwise → dispatch the chosen path, no gate. | ordering | L641 table | F4-040 | implementer dispatch | chosen path | Agent | yes | procedure |
| FX-ROUTE-39 | Row 6 dispatches a fresh ephemeral implementer Agent (Engineer / Test Writer / Doc Writer per the finding's lane) per Section 4's dispatch shape with the chosen fix path and no user gate (and appends a Trigger C entry — FX-TRACK-53). | command | L644 (a) | F4-041 | Agent dispatch | chosen path, lane | Agent, TaskList | no | procedure |
| FX-ROUTE-40 | Rationale: rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of depth tag; row 1 comes first so parts (e) and (f) stay reachable. | rationale-only | L644 | F4-043 | - | - | none | yes | rationale |
| FX-ROUTE-41 | Whatever row fires, when the chosen path changes source the re-dispatch follows part (g)'s ordering: Engineer, then the code review for that site, then the affected writer. | ordering | L644 | F4-044 | dispatch sequence | chosen path | Agent | yes | procedure |
| FX-ROUTE-42 | "Highest-quality" = the smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names. | definition | L646 **What "highest-quality" means.** | F4-045 | - | ticket body | none | yes | procedure |
| FX-ROUTE-43 | Total-system complexity counts against a path. | invariant | L646 | F4-046 | - | - | none | yes | procedure |
| FX-ROUTE-44 | Effort is never the tiebreaker between paths of equal completeness. | invariant | L646 | F4-047 | - | - | none | yes | procedure |
| FX-ROUTE-45 | "Adds a mechanism" is a reason to route to gate (c), not a reason to build. | invariant | L646 | F4-048 | - | - | none | yes | procedure |
| FX-ROUTE-46 | For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently". | definition | L646 | F4-049 | - | - | none | yes | procedure |
| FX-ROUTE-47 | "Introduces a mechanism" = adds machinery per `agents/analyst.md`'s mechanism definition that the approved design (the `## Authoritative design directive` block from Section 3's Analyst gate) did not enumerate. | definition | L648 **What "introduces a mechanism" means.** | F4-050 | - | `## Authoritative design directive`, `agents/analyst.md` | none | no | procedure |
| FX-ROUTE-48 | The reviewer's `[introduces-mechanism]` tag is the primary signal for row 2: a tagged path routes to gate (c) with no further judgment. | invariant | L648 | F4-051 | gate (c) fire | `[introduces-mechanism]` | none | yes | procedure |
| FX-ROUTE-49 | Orchestrator-side mechanism detection is the fallback, used only when no tag is present: read the path's own description against the definition and route the same way. | invariant | L648 | F4-052 | gate (c) fire | fix path description | none | yes | procedure |
| FX-ROUTE-50 | **(b)** MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent (R2/R3 rounds). | invariant | L650 ODR (b) | F4-053 | - | dispatch prompt | Agent | yes | procedure |
| FX-ROUTE-51 | Forbidden dispatch-prompt phrasings (and close paraphrases): `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. | definition | L650 | F4-054 | - | dispatch prompt | none | yes | procedure |
| FX-ROUTE-52 | Rationale: inlining a scope-bound silently narrows the fix without the user ever seeing the decision. | rationale-only | L650 | F4-055 | - | - | none | yes | rationale |
| FX-ROUTE-53 | When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through the scope-bounding gate in part (c). | command | L650 | F4-056 | gate (c) fire | - | AskUserQuestion | yes | procedure |
| FX-ROUTE-54 | The prohibition targets narrowing language, not path selection: a dispatch prompt naming the part-(a) chosen path and carrying its fix in full is not a violation. | invariant | L652 | F4-057 | - | chosen path | none | yes | procedure |
| FX-ROUTE-55 | Instructing the implementer to do less than the chosen path is a violation of part (b). | invariant | L652 | F4-058 | - | dispatch prompt | none | yes | procedure |
| FX-ROUTE-56 | A path narrower than the smallest internally-consistent complete fix is never written into a prompt at all; it routes to gate (c) via row 4. | invariant | L652 | F4-059 | gate (c) fire | chosen path | none | yes | procedure |

| FX-ROUTE-57 | **(c) Scope-bounding gate** has four entry conditions: the would-otherwise-scope-bound case (replacing part (b)'s forbidden directives), and rows 2, 3, and 4 of part (a). | definition | L654 ODR (c) | F4-060 | - | FX-ROUTE-53, -34..36 | none | yes | procedure |
| FX-ROUTE-58 | Downstream, the part-(b) scope-bound condition is read as row 4; every rule enumerating "row 2, 3, or 4" covers it without naming it. | definition | L654 | F4-061 | - | - | none | yes | procedure |
| FX-ROUTE-59 | On any of the four entry conditions, fire an `AskUserQuestion` via the two-step contract with the finite choices below, filtered by the severity paragraph. | gate | L654 | F4-062 | gate task + question | finding severity | TaskList, AskUserQuestion | yes | procedure |
| FX-ROUTE-60 | Severity rules the choice set: a `blocker` can never be accepted, and can be deferred only with a narrowing. | invariant | L656 | F4-063 | - | severity | none | unknown | procedure |
| FX-ROUTE-61 | For a `blocker` at gate (c), `Accept the limitation` is unreachable unconditionally: do not offer it, do not mark it Recommended, do not route to it by any other path. | choice-set | L658 | F4-064 | - | severity | AskUserQuestion | unknown | procedure |
| FX-ROUTE-62 | A `blocker` at gate (c) is always offered the base pair `Fix properly now` and `Re-dispatch the Analyst with this finding`; when the two Defer conditions do not both hold, they are the whole set. | choice-set | L659 | F4-065 | choice set | severity | AskUserQuestion | no | procedure |
| FX-ROUTE-63 | Blocker `Fix properly now` behaves as the `suggestion`/`nit` `Fix properly now` bullet ("as below"). | choice-set | L661 | F4-066 | - | FX-ROUTE-83 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-64 | `Defer to follow-up Issue` is added as a third choice for a `blocker` only when both hold: (i) the needed fix path introduces a mechanism (`[introduces-mechanism]` tag or orchestrator reading against `agents/analyst.md`), and (ii) that mechanism serves a case outside this unit's stated defect. | choice-set | L664 | F4-078 | choice set | fix path, `[introduces-mechanism]` | AskUserQuestion | unknown | procedure |
| FX-ROUTE-65 | Condition (ii) means the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships. | definition | L664 | F4-079 | - | - | none | unknown | procedure |
| FX-ROUTE-66 | A narrowing may never reduce coverage of the stated defect (at gate (c) and at gate (d) alike). | invariant | L664; L678 | F4-080, F4-113 | - | narrowing | none | unknown | procedure |
| FX-ROUTE-67 | A `blocker` that cannot be made inapplicable to what ships without leaving the stated defect partly unfixed is in scope: it takes one of the base pair (or, at gate (d), one of the other choices), never `Defer`. | invariant | L664; L678 | F4-081 | - | FX-ROUTE-64 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-68 | The blocker deferral is paired with the narrowing, never shipped alone (at either gate; the bullet's "rather than picking a path now" describes only the non-blocker case). | invariant | L664; L678 | F4-082, F4-118 | narrowing dispatch | `Defer` answer | Agent | unknown | procedure |
| FX-ROUTE-69 | File the follow-up Issue first, carrying the reviewer's sketched design verbatim, and dispatch the narrowing only once `/quo-file-issue` has returned an Issue ID. | ordering | L664 | F4-083 | follow-up Issue, narrowing dispatch | reviewer's sketched design | bees, Agent | unknown | procedure |
| FX-ROUTE-70 | Part (f) forbids shipping the narrowing when the filing failed; Trigger A writes its tracker entry in that same window. | relay | L664 | F4-084 | tracker entry (A) | `/quo-file-issue` result | none | unknown | procedure |
| FX-ROUTE-71 | Dispatch the blocker narrowing directly, not by re-entering Step 2 with it (it would match row 4 and loop back to this gate). | invariant | L664 | F4-085 | narrowing dispatch | narrowing | Agent | unknown | procedure |
| FX-ROUTE-72 | The direct-dispatch terminality is one rule with the `Defer to follow-up Issue` bullet's soft-fix rule, applied to a blocker's narrowing and a non-blocker's soft fix. | definition | L664 | F4-086 | - | - | none | unknown | procedure |
| FX-ROUTE-73 | When the Defer-with-narrowing branch is open, it is the recommended default: mark the choice `(Recommended)` even on a `blocker`. | choice-set | L664 | F4-087 | `(Recommended)` | FX-ROUTE-64 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-74 | The blocker Defer branch applies whichever row fired the gate — 2, 3, or 4 — because condition (i) tests the fix path the finding needs, not the chosen path. | invariant | L664 | F4-088 | - | fix path the finding needs | none | unknown | procedure |
| FX-ROUTE-75 | A `suggestion` or `nit` keeps the narrower rule: its Defer default is row-2 only. | choice-set | L664 | F4-089 | - | severity, row | AskUserQuestion | unknown | procedure |
| FX-ROUTE-76 | The gate fires for a `blocker` like any other finding: the base pair is a real decision, three choices when the Defer-with-narrowing branch is open. | gate | L666 | F4-090 | gate fire | severity | AskUserQuestion | unknown | procedure |
| FX-ROUTE-77 | Neither of the `Defer to follow-up Issue` bullet's closing clauses applies to a blocker: its no-fix-this-round branch cannot arise, and its never-invent-a-narrowing prohibition concerns a non-blocker's empty soft-fix slot. | invariant | L666 | F4-091 | - | - | none | unknown | procedure |
| FX-ROUTE-78 | The Defer bullet's soft-fix identification does not apply to a blocker: what ships is the narrowing, not the most complete remaining enumerated path. | invariant | L666 | F4-092 | - | - | none | unknown | procedure |
| FX-ROUTE-79 | The three bulleted choices (`Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`) are the choice set for `suggestion`- and `nit`-severity findings. | choice-set | L666 | F4-093 | choice set | severity | AskUserQuestion | yes | procedure |
| FX-ROUTE-80 | `Fix properly now`: re-dispatch the appropriate implementer Agent per Section 4's dispatch shape to address the finding fully, no scope-bound. | choice-set | L668 | F4-096 | implementer dispatch | finding | Agent, TaskList | no | procedure |
| FX-ROUTE-81 | `Defer to follow-up Issue` (gate c): file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool, per Section 1's URL-resolution precedent) carrying the finding's description, and proceed with the soft fix this round. | choice-set | L669 | F4-097 | follow-up Issue, soft-fix dispatch | finding description | bees, Agent | no | procedure |
| FX-ROUTE-82 | The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside. | definition | L669 | F4-098 | soft fix | enumerated fix paths | none | yes | procedure |
| FX-ROUTE-83 | Dispatch the soft fix directly, not by re-entering Step 2 (a remaining path is narrower than the deferred one, so row 4 would loop it back). | invariant | L669 | F4-099 | soft-fix dispatch | FX-ROUTE-82 | Agent | yes | procedure |
| FX-ROUTE-84 | When the deferred path was the only one enumerated, ship no fix for this finding this round (same end state as `Accept the limitation`, with the follow-up Issue filed). | recovery | L669 | F4-100 | - | fix-path count | none | yes | procedure |
| FX-ROUTE-85 | Never invent a narrowing to fill the soft-fix slot; part (b) forbids it. | invariant | L669 | F4-101 | - | - | none | yes | procedure |
| FX-ROUTE-86 | `Accept the limitation`: record the limitation as an accepted compromise and proceed, via the session-scoped compromise tracker (`#### Session-scoped compromise tracker`, Section 7.5). | choice-set | L670 | F4-102 | tracker entry | finding | none | no | procedure |
| FX-ROUTE-87 | Gate (c)'s question text includes the finding verbatim plus a one-line context line stating which of the four entry conditions brought it here. | field-or-template | L672 | F4-103 | question text | finding, entry condition | AskUserQuestion | yes | procedure |
| FX-ROUTE-88 | There is no `Cancel` option at gate (c); the user retains `Ctrl-C` for run-level abort. | choice-set | L672 | F4-104 | - | - | AskUserQuestion | no | procedure |
| FX-ROUTE-89 | Rationale: scope-bounding is a per-finding decision, so a `Cancel` at gate (c) would be ambiguous. | rationale-only | L672 | F4-105 | - | - | none | no | rationale |
| FX-ROUTE-90 | **Recommended default on the mechanism row.** When gate (c) fires on row 2 (mechanism serving a case the ticket never mentions), `Defer to follow-up Issue` is the recommended default: mark it `(Recommended)`. | choice-set | L674 | F4-106 | `(Recommended)` | row 2 fire | AskUserQuestion | yes | procedure |
| FX-ROUTE-91 | The row-2 recommended default holds at every severity: `suggestion`/`nit` ships the soft fix; a `blocker` ships the narrowing, but only where the Defer-with-narrowing branch is open. | invariant | L674 | F4-107 | - | severity | AskUserQuestion | unknown | procedure |
| FX-ROUTE-92 | When the coverage guard withholds `Defer` (narrowing would leave the stated defect partly unfixed), there is no choice to mark, even on a row-2 fire. | invariant | L674 | F4-108 | - | FX-ROUTE-66 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-93 | Rationale: a mechanism the ticket never asked for has its own lifecycle to design; building it inside this unit turns one finding into several rounds. | rationale-only | L674 | F4-109 | - | - | none | yes | rationale |
| FX-ROUTE-94 | The follow-up Issue MUST carry the reviewer's sketched design verbatim so nothing about the proposed mechanism is lost by deferring. | field-or-template | L674 | F4-110 | follow-up Issue body | reviewer's sketched design | bees | yes | procedure |
| FX-ROUTE-95 | **(d) Routing-decision gate** fires when Step 2 routes a finding via row 1 or row 5 (depth unknown/malformed, or chosen path `re-architect`): fire `AskUserQuestion` via the two-step contract. | gate | L676 ODR (d) | F4-111 | gate task + question | rows 1, 5 | TaskList, AskUserQuestion | yes | procedure |
| FX-ROUTE-96 | For a `blocker` at gate (d), `Defer to follow-up Issue` is unreachable unless part (c)'s two conditions both hold. | choice-set | L678 | F4-112 | - | FX-ROUTE-64 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-97 | When the conditions hold at gate (d), offer `Defer` on part (c)'s terms: paired with the narrowing in the same round, `(Recommended)`, follow-up Issue carrying the sketched design verbatim. | choice-set | L678 | F4-114 | `Defer` choice, follow-up Issue, narrowing dispatch | FX-ROUTE-64 | AskUserQuestion, bees, Agent | unknown | procedure |
| FX-ROUTE-98 | Blocker-Defer `(Recommended)` takes precedence over the per-path marker: mark `Defer to follow-up Issue` Recommended and withhold the marker from every other choice (each Step-1 path marker and `Re-dispatch the Analyst with this finding`), so exactly one choice carries it. | choice-set | L678 | F4-115 | `(Recommended)` | FX-ROUTE-97 | AskUserQuestion | no | procedure |
| FX-ROUTE-99 | Example: a zero-path row-1 blocker whose Defer branch is open shows `(Recommended)` on `Defer` alone. | example | L678 | F4-116 | - | - | AskUserQuestion | unknown | example |
| FX-ROUTE-100 | When part (c)'s conditions do not hold for a blocker at gate (d), do not offer `Defer`, do not mark it Recommended, and do not route to it by any other path. | choice-set | L678 | F4-117 | - | FX-ROUTE-64 | AskUserQuestion | unknown | procedure |
| FX-ROUTE-101 | The choice set for a non-deferrable `blocker` at gate (d) is the one-choice-per-fix-path list (which may be empty) plus `Re-dispatch the Analyst with this finding` plus `Cancel`. | choice-set | L678 | F4-119 | choice set | fix paths | AskUserQuestion | no | procedure |
| FX-ROUTE-102 | A row-1 blocker with no fix path enumerated: mark `Re-dispatch the Analyst with this finding` `(Recommended)` (unless the Defer branch is open — FX-ROUTE-98). | choice-set | L678 | F4-120 | `(Recommended)` | fix-path count | AskUserQuestion | no | procedure |
| FX-ROUTE-103 | No `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing. | invariant | L678 | F4-122 | - | - | none | unknown | procedure |
| FX-ROUTE-104 | Gate (d) offers one choice per reviewer-surfaced fix path; each choice's description includes that path's depth tag (e.g., `re-architect`, `refactor-locally`). | choice-set | L680 | F4-124 | choice set | fix paths, depth tags | AskUserQuestion | yes | procedure |
| FX-ROUTE-105 | The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1. | choice-set | L680 | F4-125 | `(Recommended)` | Step 1 pick | AskUserQuestion | yes | procedure |
| FX-ROUTE-106 | Rationale: gate (d) asks the user to ratify or override a pick that has already been made, so the marker must name that pick. | rationale-only | L680 | F4-126 | - | - | none | yes | rationale |
| FX-ROUTE-107 | When `[preferred]` marks a narrowing and a fuller path is the smallest internally-consistent complete change, mark the fuller path Recommended and state in its description that the reviewer preferred the other path. | choice-set | L680 | F4-127 | choice description | `[preferred]`, Step 1 pick | AskUserQuestion | yes | procedure |
| FX-ROUTE-108 | Fallback: on a row-1 entry (no or malformed depth tag) no Step-1 pick was possible, so no path is marked Recommended. | choice-set | L680 | F4-128 | - | row 1 | AskUserQuestion | yes | procedure |
| FX-ROUTE-109 | `Defer to follow-up Issue` (gate d): file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now. | choice-set | L681 | F4-129 | follow-up Issue | finding description | bees | yes | procedure |
| FX-ROUTE-110 | `Cancel` (gate d): ends work on the current Issue without a fix landing (routing per ABORT — FX-ABORT-30/31). | choice-set | L682 | F4-130 | - | - | AskUserQuestion | no | procedure |
| FX-ROUTE-111 | `Ctrl-C` remains the unconditional run-level abort. | definition | L682 | F4-133 | - | - | none | yes | procedure |
| FX-ROUTE-112 | Gate (d)'s question text includes the finding verbatim. | field-or-template | L684 | F4-134 | question text | finding | AskUserQuestion | yes | procedure |
| FX-ROUTE-113 | **(e) Backwards-compatibility shim.** A finding emitted without a depth tag (legacy reviewer emission, or hand-authored from a future call site) MUST be treated as `re-architect` depth and routed to gate (d). | invariant | L686 ODR (e) | F4-135 | gate (d) fire | depth tag absence | AskUserQuestion | yes | procedure |
| FX-ROUTE-114 | When the orchestrator cannot determine a finding's depth, surface the decision to the user rather than dispatching its own pick ungated under row 6. | invariant | L686 | F4-136 | gate (d) fire | depth tag | AskUserQuestion | yes | procedure |
| FX-ROUTE-115 | A PM emission that `agents/pm.md`'s tracker-check bullet designates a report note (not a finding) is exempt from the shim and from part (f)'s malformed-tag bullet; that bullet defines the shape. | invariant | L686 | F4-137 | - | PM emission | none | yes | procedure |
| FX-ROUTE-116 | **(f) Malformed tags.** When a severity tag is not exactly `blocker` / `suggestion` / `nit`, or a depth tag not exactly `trivial-tweak` / `refactor-locally` / `re-architect`, treat the finding as `re-architect` depth (per part (e)) AND surface the parse failure to the user. | recovery | L690 ODR (f) | F4-138 | gate (d) fire, parse-failure report | tags | AskUserQuestion | yes | procedure |
| FX-ROUTE-117 | **Routing ambiguity.** If the routing table returns more than one decision (impossible by construction), default to gate (d) and surface the ambiguity to the user. | recovery | L691 | F4-139 | gate (d) fire | routing decisions | AskUserQuestion | yes | procedure |
| FX-ROUTE-118 | **`/quo-file-issue` failure at the Defer gate.** When the user picks `Defer to follow-up Issue` at either gate but the inline dispatch fails or the user cancels at one of its gates, MUST NOT silently ship the soft fix (or no fix). | recovery | L692 | F4-140 | - | `/quo-file-issue` result | bees | yes | procedure |
| FX-ROUTE-119 | On a filing failure, surface it and re-prompt with the same gate's choices so the user can re-attempt the defer, pick `Accept the limitation` where it exists (non-`blocker` only), pick a specific fix path explicitly, or (at gate (d)) `Cancel`. | recovery | L692 | F4-141 | re-fired gate | FX-ROUTE-118 | TaskList, AskUserQuestion | unknown | procedure |
| FX-ROUTE-120 | A `blocker` can reach the filing-failure bullet via the Defer-with-narrowing branch; do not ship the narrowing when the filing failed — re-prompt with the same gate's choices. | recovery | L692 | F4-142 | re-fired gate | `/quo-file-issue` result | AskUserQuestion | unknown | procedure |
| FX-ROUTE-121 | **(g)** Routing is settled by the orchestrator's own pick per part (a) or the user's pick at gate (c) or (d); the orchestrator then still decides how many lanes to dispatch at once. | definition | L694 ODR (g) | F4-143 | - | routing decision | none | yes | procedure |
| FX-ROUTE-122 | When the chosen fix path requires a source change, dispatch the Engineer first, then the Code Reviewer against the resulting diff, and only once that code review has closed dispatch the Test Writer and/or Doc Writer whose input the change invalidated — ordered, not concurrent. | ordering | L694 | F4-144 | dispatch sequence | chosen path | Agent, TaskList | yes | procedure |
| FX-ROUTE-123 | Rationale: dispatching the Engineer and a writer in the same round hands the writer a diff the pending code review is about to rewrite, forcing the writer's work to be redone. | rationale-only | L694 | F4-145 | - | - | none | yes | rationale |
| FX-ROUTE-124 | One elision: when the Engineer round is the final `trivial-tweak` nit pass SBL describes, skip the code-review rung and dispatch the affected writer once that Engineer returns; every other source-changing round keeps the rung. | ordering | L694 | F4-146 | dispatch sequence | FX-ROUTE-13 | Agent | yes | procedure |
| FX-ROUTE-125 | A finding whose chosen fix path changes no source file (test-quality nit, doc-wording gap) carries no ordering constraint: re-dispatch that single writer lane alone, no Engineer round, no code review. | ordering | L698 | F4-150 | writer dispatch | chosen path | Agent | yes | procedure |
| FX-ROUTE-126 | Section 5 re-dispatches are ordered, not concurrent, whenever a fix path changes source; see part (g) and Section 4's re-entry bullet. | ordering | L735 `### 5.` | F5-060 | - | - | Agent | unknown | procedure |
| FX-ROUTE-127 | Get the feedback and make a judgement call about whether that work must be done (the pick is the orchestrator's; the route is deterministic). | choice-set | L734 `### 5.` | F5-055 | routing decision | review skill outputs | none | unknown | procedure |

---

## 22. REVIEW — Review loop & trailer consumption (Section 5)

- **Purpose:** In Phase C dispatch the Test Reviewer / Doc Reviewer (only if their implementer ran) and the PM (always), concurrently; consume each review skill's routing trailer literally and dispatch fresh implementers or a PM re-pass as it prescribes.
- **Failure it prevents:** not stated directly (implicit: reviewing a lane whose implementer never ran; ignoring the trailer's prescription in favour of surrounding prose).
- **Env deps:** Agent, TaskList. **TaskList-dependent: yes** (tracking names via TASK).
- **Rows:** 10 (procedure 9, example 1).
- **Literals:** `### 5. Review Loop`; `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`, `Agent(subagent_type="pm", run_in_background=true)`; **PM is the exception to the conditional-spawn rules.**; review skills `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`; trailers `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`; **Follow the trailer literally**.
- **Edges:** Entered from LOOP Phase C (FX-LOOP-24); prompts from PROMPT/SCOPED; findings routed by ROUTE; ignored items → LEDGER; PM verdict → DOCV/SUM.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-REVIEW-1 | Dispatch three concurrent ephemeral Agents: `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`, `Agent(subagent_type="pm", run_in_background=true)`. | command | L708 `### 5. Review Loop` | F5-009 | three dispatches | Section 4 shape | Agent | unknown | procedure |
| FX-REVIEW-2 | Only dispatch a reviewer whose corresponding implementer ran during this issue's pass: Test Reviewer if the Test Writer ran in Phase B, Doc Reviewer if the Doc Writer ran in Phase B, and the PM always. | precondition | L406 RL; L710-L712 | F3-074, F5-012, F5-013, F5-014 | reviewer dispatches | which implementers ran | Agent | unknown | procedure |
| FX-REVIEW-3 | Example: a doc-only fix dispatches only the doc-reviewer (no Code Reviewer); a code+test fix without Doc Writer dispatches Code Reviewer in Phase A and only test-reviewer here. | example | L715 | F5-016 | - | - | none | unknown | example |
| FX-REVIEW-4 | Always dispatch the Product Manager per Issue regardless of which implementers ran (**PM is the exception to the conditional-spawn rules**), alongside the reviewers, not instead of any of them. | invariant | L717 | F5-017, F5-018 | pm dispatch | - | Agent | unknown | procedure |
| FX-REVIEW-5 | Each review skill (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a routing trailer (`**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`) plus a counter-anchor clause. | definition | L734 | F5-056 | - | review skill output | none | unknown | procedure |
| FX-REVIEW-6 | **Follow the trailer literally** — it is the authoritative routing prescription; the surrounding prose is reference context only. | invariant | L734 | F5-057 | - | routing trailer | none | unknown | procedure |
| FX-REVIEW-7 | Phase A borrows Section 5's feedback-consumption discipline in full — the "**Follow the trailer literally**" bullet and the ignored-feedback rule — applied to Code Reviewer Phase A returns exactly as to Phase C returns. | invariant | L706 | F5-006, F5-008 | - | Code Reviewer returns | none | no | procedure |
| FX-REVIEW-8 | If feedback requires action, dispatch fresh ephemeral implementer Agents (Engineer / Test Writer / Doc Writer as needed) per Section 4's dispatch shape. | command | L735 | F5-058 | implementer dispatches | findings | Agent | unknown | procedure |
| FX-REVIEW-9 | Re-dispatch the PM per this section's dispatch shape if spec-alignment review needs another pass against the updated diff. | command | L735 | F5-059 | pm dispatch | updated diff | Agent | unknown | procedure |
| FX-REVIEW-10 | If the feedback was minor enough, you may choose to **NOT** re-dispatch the Product Manager on this iteration. | choice-set | L737 | F5-062 | - | - | none | unknown | procedure |

---

## 23. LEDGER — Ignored-feedback / `defer-*` ledger

- **Purpose:** Every reviewer/PM item the orchestrator decides not to act on becomes, at ignore time, a `pending` `defer-<short-suffix>` task with a one-line description and a mandatory destination annotation, so the 7.5 gate can route it Fix / File / Encode.
- **Failure it prevents:** The 7.5 gate firing empty because ignore decisions were never recorded (F5-073); vague "defer to later" framings with no destination (F5-072).
- **Env deps:** TaskList. **TaskList-dependent: yes.**
- **Rows:** 12 (procedure 11, rationale 1).
- **Literals:** `defer-<short-suffix>` (`defer-1`, `defer-2`; **Run scope**); `metadata.activity`; destination labels `addressed-now-in-this-Task` (read as "addressed-now-in-this-Issue"), `defer-to-existing-ticket-body: <ticket-id>`, `defer-to-new-Issue`; `**Ignored Review Feedback**`; `agents/pm.md` Final report contract.
- **Edges:** Fed by REVIEW (ignored items), PROMPT (compaction-artifact finding), DEFC (Analyst bullets — its own rows); read by HYG Steps 0–3 and CKPT step 1; naming in TASK namespace; PM destination vocabulary from ROLES.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-LEDGER-1 | If feedback does not require action, move on but MUST include the ignored feedback in the summary. | invariant | L738 `### 5.` | F5-063 | `**Ignored Review Feedback**` content | ignored items | none | unknown | procedure |
| FX-LEDGER-2 | You may ignore feedback (to avoid an infinite loop) so long as you present it in the summary. | invariant | L739 | F5-064 | - | - | none | unknown | procedure |
| FX-LEDGER-3 | Record each ignored item as a `defer-<short-suffix>` TaskList task at the moment of the ignore decision (with destination annotation) — one of three ways Phase A may close with findings outstanding. | command | L706; L740 | F5-007, F5-067 | `defer-*` task | ignore decision | TaskList | unknown | procedure |
| FX-LEDGER-4 | Set the `defer-*` task's `metadata.activity` to the feedback's one-line description (so the 7.5 gate can surface the active set) and its status to `pending`. | field-or-template | L591 TNC; L740 | F3-275, F5-068 | `metadata.activity`; status `pending` | feedback text | TaskList | unknown | procedure |
| FX-LEDGER-5 | Record the PM's destination annotation — `addressed-now-in-this-Task` (read as "addressed-now-in-this-Issue"), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — in the same `metadata.activity` string. | field-or-template | L740 | F5-069 | `metadata.activity` destination | PM Final report | TaskList | unknown | procedure |
| FX-LEDGER-6 | For ignored reviewer-feedback items (code/test/doc-reviewer findings the Director chose to ignore), the Director MUST annotate `metadata.activity` with one of the three destination labels when creating the `defer-*` task. | invariant | L740 | F5-070 | `metadata.activity` destination | Director judgement | TaskList | unknown | procedure |
| FX-LEDGER-7 | The destination annotation is required, not optional; it lets Section 7.5's gate route reviewer and PM items uniformly through Fix / File / Encode. | invariant | L740 | F5-071 | - | - | TaskList | unknown | procedure |
| FX-LEDGER-8 | Vague framings without a named destination (e.g., "defer to later") are forbidden. | invariant | L740 | F5-072 | - | - | none | unknown | procedure |
| FX-LEDGER-9 | Rationale: this record-creating step is the load-bearing source for Section 7.5's gate; without it the gate fires empty. | rationale-only | L740 | F5-073 | - | - | none | unknown | rationale |
| FX-LEDGER-10 | **Deferral-ledger tasks** — **Run scope**: `defer-<short-suffix>` (`defer-1`, `defer-2`, or any collision-resistant suffix); record items not addressed inline as such per Section 4's naming convention. | name-class | L591 TNC; L1043 §7.5 | F3-273, F6-101 | task name | destination annotations | TaskList | yes | procedure |
| FX-LEDGER-11 | Create a `defer-*` task when a structured return (per `agents/pm.md` Final report or `agents/analyst.md` `### Deferred refinements`) names `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` not addressed inline. | command | L591 TNC | F3-274 | `defer-*` task | PM/Analyst return | TaskList | unknown | procedure |
| FX-LEDGER-12 | Mark a `defer-*` task `completed` the moment the deferral is encoded in a durable carrier (updated ticket body, new Issue, or in-session resolution logged in `metadata.activity`). | command | L591 TNC | F3-276 | task `completed` | - | TaskList, bees | unknown | procedure |

---

## 24. DOCV — Doc verification (Section 6)

- **Purpose:** Confirm (never perform) that the PM's spec-alignment verdict is captured in the per-issue summary and that any `## Doc divergence noted` was consumed by the Doc Writer pass.
- **Failure it prevents:** not stated (implicit: the orchestrator doing load-bearing doc edits outside the Doc Writer's lane).
- **Env deps:** none. **TaskList-dependent: no.**
- **Rows:** 7 (procedure 7).
- **Literals:** `### 6. Verify docs are still accurate`; **informational confirmation**; `no spec drift surface to review for this Issue`; `## Doc divergence noted`; `N/A`.
- **Edges:** Consumes REVIEW's PM verdict and ROLES' Doc Writer behaviour; Produces confirmation bullets feeding SUM's `**Doc Sync**` line.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-DOCV-1 | Section 6 is **informational confirmation** on every Issue — never load-bearing orchestrator-direct work. | invariant | L744 `### 6.` | F5-074 | - | - | none | unknown | procedure |
| FX-DOCV-2 | Confirm the PM's verdict has been captured in the per-issue summary and proceed to Section 7. | command | L744 | F5-075 | confirmation | PM verdict | none | unknown | procedure |
| FX-DOCV-3 | The PM verdict is either a deep review or the one-line short-circuit `no spec drift surface to review for this Issue`; either lands in the per-issue summary. | definition | L744 | F5-076 | - | PM Final report | none | unknown | procedure |
| FX-DOCV-4 | If the Issue body carried `## Doc divergence noted`, **confirm** the Section 4 Doc Writer pass consumed it (named file/section matches post-fix behavior); do not re-discover the divergence. | command | L746 | F5-077 | confirmation | Issue body; doc files | none | no | procedure |
| FX-DOCV-5 | Section 6 never performs orchestrator-direct doc updates; doc changes are the Doc Writer's lane per `agents/doc-writer.md`. | invariant | L748 | F5-078 | - | - | none | unknown | procedure |
| FX-DOCV-6 | Report: the PM's spec-alignment verdict (deep review or `no spec drift surface to review for this Issue`) and confirmation it is captured in the per-issue summary. | field-or-template | L750 | F5-079 | report bullet | PM verdict | none | unknown | procedure |
| FX-DOCV-7 | Report: when `## Doc divergence noted` was present, confirmation the Doc Writer pass consumed it; otherwise mark this bullet N/A. | field-or-template | L751 | F5-080 | report bullet | Issue body | none | no | procedure |

---

## 25. CLOSE — Per-issue close-out & commit (Section 7 steps 1–3, 5)

- **Purpose:** Flip the Issue `open → done` idempotently, format, stage only this Issue's files (plus its in-repo hive directory), commit once with the `Fix issue: <title> (<issue-id>)` subject, sweep every per-issue TaskList task by prefix, then branch on mode after the 7.5 gate and the checkpoint.
- **Failure it prevents:** Double-flipping or failing on a worker's own status flip (F5-083); sweeping other agents' in-flight changes with `git add -A` (F5-096); a `pending` `aborted-*` marker holding Phase C shut on a later re-entry (F5-108); Section 9's `--grep` SHA derivation breaking if the subject token drifts (F5-101).
- **Env deps:** bees, git, Bash, TaskList, Agent. **TaskList-dependent: yes** (step 3 sweep).
- **Rows:** 29 (procedure 24, rationale 5).
- **Literals:** `### 7. After Issue is fixed`; `bees show-ticket --ids <issue-id>`; `bees update-ticket --status done`; **Format** key; `git status`; `git add <emitted-issues-path>/<issue-id>`; **Do NOT blindly `git add -A`**; `hive_commit.py` `resolve-hive-paths --hive issues` (`python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues` / `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues`); commit subject `Fix issue: <title> (<issue-id>)` (e.g. `Fix issue: Tighten dispatch contract gap (b.abc)`); **NEVER push to remote — committing only.**; sweep names per TASK; `**Single mode**` / `**Batch mode (`all` or list mode) with the batch exhausted**` / `**Batch mode with a next Issue still remaining in the batch**`.
- **Edges:** Consumes PRE's `## Build Commands` `Format`, TASK names, HYG (`hive_commit.py` sibling helper), MOVE markers; Produces the per-issue commit CKPT verifies and GH keys on, the status flip VAL/ARG expect, and the mode branch into HYG → CKPT → GUARD / POSTC; the same sweep runs at ABORT's own site.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-CLOSE-1 | Step 1: mark the issue's bees ticket `status=done` before committing. | ordering | L757 `### 7.` | F5-081 | status flip | - | bees | unknown | procedure |
| FX-CLOSE-2 | **Re-read the Issue's current status first** (`bees show-ticket --ids <issue-id>`) and skip `bees update-ticket --status done` if already `done`. | precondition | L757 | F5-082 | idempotent flip | ticket status | bees | unknown | procedure |
| FX-CLOSE-3 | Rationale: workers occasionally flip the status themselves, so the close-out flip must be idempotent rather than fail or double-flip. | rationale-only | L757 | F5-083 | - | - | none | unknown | rationale |
| FX-CLOSE-4 | The bees CLI writes the status to the on-disk record under the resolved Issues hive path; when in-repo, that change is staged in the per-issue commit at step 2.3. | definition | L757 | F5-084 | working-tree change | Issues hive path | bees, git | unknown | procedure |
| FX-CLOSE-5 | Step 2: create one git commit for the Issue, including any doc updates. | command | L758 | F5-085 | git commit | - | git | yes | procedure |
| FX-CLOSE-6 | **NEVER push to remote — committing only.** | invariant | L758 | F5-086 | - | - | git | yes | procedure |
| FX-CLOSE-7 | Step 2.1: run the **Format** command from CLAUDE.md `## Build Commands` to normalize formatting. | command | L759 | F5-087 | formatted files | `Format` key | Bash | yes | procedure |
| FX-CLOSE-8 | Step 2.2: run `git status` to see all modified and untracked files. | command | L760 | F5-088 | file list | working tree | git | yes | procedure |
| FX-CLOSE-9 | Step 2.3: stage files related to this issue's code, test, and doc changes — agent-reported files plus formatting changes to files those agents touched. | command | L761 | F5-089 | staged files | agent reports; `git status` | git | yes | procedure |
| FX-CLOSE-10 | Only if the Issues hive lives inside this repo, also stage the per-issue directory under the resolved Issues hive path so the `open → done` flip and body updates land in the same commit. | command | L761 | F5-090 | staged hive directory | Issues hive path | git, bees | yes | procedure |
| FX-CLOSE-11 | Rationale: the Issues-hive scoping mirrors `quo-execute`'s Plans-hive scoping in its After-Task commit step. | rationale-only | L761 | F5-091 | - | - | none | yes | rationale |
| FX-CLOSE-12 | To learn the in-repo Issues hive path, run `hive_commit.py`'s NON-MUTATING `resolve-hive-paths` mode, resolving its sibling path as the 7.5 Encode step does — exactly: POSIX `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues`; PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues`, as a single literal Bash call. | command | L761-L771 | F5-092, F5-094 | hive path | skill base directory | Bash | yes | procedure |
| FX-CLOSE-13 | The helper emits the Issues hive's absolute path when it is inside this repo, or nothing when outside (stage no hive path then). | definition | L761 | F5-093 | - | helper stdout | Bash | yes | procedure |
| FX-CLOSE-14 | When the helper emits a path, append `/<issue-id>` and `git add <emitted-issues-path>/<issue-id>` alongside judgement-selected source files. | command | L773 | F5-095 | staged per-issue directory | helper output | git | yes | procedure |
| FX-CLOSE-15 | **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes. | invariant | L773 | F5-096 | - | - | git | yes | procedure |
| FX-CLOSE-16 | Review each modified file and stage it only if plausibly related to this issue. | command | L773 | F5-097 | staged files | `git status` | git | yes | procedure |
| FX-CLOSE-17 | Rationale: per-issue `<issue-id>` scoping on the `git add` path keeps other issues' record drift out; stale state is caught by the next `/quo-fix-issue` run. | rationale-only | L773 | F5-098 | - | - | none | no | rationale |
| FX-CLOSE-18 | Step 2.4: commit with a descriptive message per system/project git guidance. | command | L774 | F5-099 | git commit | - | git | yes | procedure |
| FX-CLOSE-19 | The commit subject line MUST follow the literal format `Fix issue: <title> (<issue-id>)` (e.g., `Fix issue: Tighten dispatch contract gap (b.abc)`). | field-or-template | L774 | F5-100 | commit subject | issue title/id | git | no | procedure |
| FX-CLOSE-20 | Rationale: Section 9's post-hoc SHA-derivation fallback `--grep`-filters on the literal `(<issue-id>)` token, so the suffix is a contract, not style. | rationale-only | L774 | F5-101 | - | - | none | no | rationale |
| FX-CLOSE-21 | Step 3: mark the per-issue TaskList tasks `completed` and clear them from the active set, sweeping by name **prefix** (not exact names, so no round is left behind), grouped by phase: Section 3 `analyst-<issue-id>` (+`-rev<n>`; already `completed`, a no-op); **Phase A** `engineer-<issue-id>`, `code-reviewer-<issue-id>`; **Phase B** `test-writer-<issue-id>`, `doc-writer-<issue-id>`; **Phase C** `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`; **aborted-writer redelivery markers** `aborted-test-writer-<issue-id>`, `aborted-doc-writer-<issue-id>`; and every `-r<n>`-suffixed round (`engineer-<issue-id>-r1`, `code-reviewer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`, …). | command | L775-L783 | F5-102, F5-103, F5-104, F5-105, F5-106, F5-107, F5-109, F5-110 | TaskList status flips | TaskList | TaskList | no | procedure |
| FX-CLOSE-22 | Rationale: a marker left `pending` past close-out would hold Phase C shut on a later re-entry into this Issue. | rationale-only | L781 | F5-108 | - | - | none | no | rationale |
| FX-CLOSE-23 | Perform no Agent shutdown / teardown ceremony — cold dispatches from Sections 3, 4, and 5 complete-and-exit on return; Section 7 just closes the per-issue TaskList tasks. | definition | L95 Notes for list mode; L783 | F1-077, F5-111 | - | - | Agent, TaskList | unknown | procedure |
| FX-CLOSE-24 | **The aborted path runs this same sweep at its own site** (`#### Aborted-Issue close-out`); any name added to this list belongs in that step's list too. | invariant | L785 | F5-112 | - | - | none | no | procedure |
| FX-CLOSE-25 | Step 5: continue to Section 7.5 first; once that gate closes, run the **Issue-boundary state-externalization checkpoint**; then branch on mode. | ordering | L822 | F5-144 | - | 7.5 gate result | none | unknown | procedure |
| FX-CLOSE-26 | **Single mode** — proceed to Section 8. | ordering | L823 | F5-145 | - | run mode | none | unknown | procedure |
| FX-CLOSE-27 | **Batch mode (`all` or list mode) with the batch exhausted** — proceed to Section 8. | ordering | L824 | F5-146 | - | run mode; batch | none | no | procedure |
| FX-CLOSE-28 | **Batch mode with a next Issue still remaining** — run the **Context-window boundary guard** (fires ONLY on this path); if it did not stop the run, go back to step 2 for the next issue. | ordering | L825 | F5-147 | - | run mode; guard result | none | unknown | procedure |
| FX-CLOSE-29 | The Issue ticket type supports only two statuses, `open` and `done`; there is no in-flight bees status to set — TaskList carries the in-flight signal; flip `open` → `done` only at issue close-out. (Conflicts with FX-VAL-11 — see Inconsistencies.) | ordering | L398 RL | F3-054, F3-055 | status flip | TaskList | bees, TaskList | no | procedure |

---

## 26. SUM — Summary template (Section 7 step 4)

- **Purpose:** Emit the fixed per-issue summary block, including the unconditional `**Second-order effects**` relay and the conditional `**Accepted compromises**` rendering read from the tracker file.
- **Failure it prevents:** not stated directly (implicit: a conditional field becoming unreliable — F5-128; truncating accepted compromises out of view — F5-141).
- **Env deps:** none (Read tool). **TaskList-dependent: no.**
- **Rows:** 26 (procedure 25, rationale 1).
- **Literals:** heading `## Issue [x] of [total] done: [issue-title]`; fields `**Issue**`, `**Files Changed**`, `**Reviews**` (`Code review: X issues found/None needed | Test review: … | Docs review: … | N nits applied without re-review` / `count unavailable post-compaction`), `**Doc Sync**` (`Docs verified accurate / Updated <doc path> §X — …`), `**Ignored Review Feedback**` (`None`), `**Second-order effects**` (`None identified.`), `**Accepted compromises**`; `No second-order effects identified.`; `## Compromise <n>`; tracker fields `Finding (verbatim)`, `Decision`, `Rationale`, `Follow-up Issue` (`none`), hidden `Fix paths surfaced by reviewer`; volume prologue "N compromises were accepted during this run:".
- **Edges:** Consumes LOOP (`### Second-order effects` narratives from Code Reviewer and PM), ROUTE (nit counts), LEDGER (ignored items), DOCV, TRACK (tracker file), MAN (tracker path recovery); read by HYG Step 0 surface 1 (`**Ignored Review Feedback**`).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-SUM-1 | Step 4: output the per-issue summary block in the given markdown template. | field-or-template | L786-L798 `### 7.` | F5-113 | summary block | fields below | none | unknown | procedure |
| FX-SUM-2 | Heading: `## Issue [x] of [total] done: [issue-title]`. | field-or-template | L789 | F5-114 | heading | batch position; title | none | no | procedure |
| FX-SUM-3 | Field `**Issue**: <issue-id>`. | field-or-template | L791 | F5-115 | field | issue id | none | no | procedure |
| FX-SUM-4 | Field `**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])`. | field-or-template | L792 | F5-116 | field | staged files | none | unknown | procedure |
| FX-SUM-5 | Field `**Reviews**: [Code review: X issues found/None needed \| Test review: Y … \| Docs review: Z … \| N nits applied without re-review (or "count unavailable post-compaction"), when any]` — record the count of `trivial-tweak` nits applied without re-review here for the scope that dispatched the review (never as ignored feedback); when compaction removed the count render `count unavailable post-compaction` rather than guessing. | field-or-template | L622 SBL; L739; L793 | F4-015, F4-016, F5-066, F5-117 | `**Reviews**` line | reviewer returns; nit count | none | unknown | procedure |
| FX-SUM-6 | Field `**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed]`, using the actual path from CLAUDE.md `## Documentation Locations`, not literal "SDD"/"PRD". | field-or-template | L794 | F5-118 | field | `## Documentation Locations` | none | unknown | procedure |
| FX-SUM-7 | Field `**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]`. | field-or-template | L795 | F5-119 | field | ignored items | none | unknown | procedure |
| FX-SUM-8 | Field `**Second-order effects**: [the relayed `### Second-order effects` narrative]` — the **destination** for `/quo-engineer-review`'s narrative via Code Reviewer (`agents/code-reviewer.md`) and/or PM (`agents/pm.md`); carry it here rather than re-dispatching the Engineer against it or holding Phase A open. | field-or-template | L404 RL; L796; L800 | F3-069, F5-120, F5-122 | field | relayed narratives | none | unknown | procedure |
| FX-SUM-9 | Field `[**Accepted compromises** — rendered per the "Accepted compromises" logic, or OMITTED ENTIRELY when the tracker is empty or absent]`. | field-or-template | L797 | F5-121 | field | compromise tracker | none | unknown | procedure |
| FX-SUM-10 | **Collect every relayed narrative for this Issue** — each Phase A Code Reviewer return (one per round) and the Phase C PM Final report's `### Second-order effects`. | command | L802 | F5-123 | collected bullets | Code Reviewer returns; PM Final report | none | unknown | procedure |
| FX-SUM-11 | Render the second-order bullets **verbatim**; do not re-summarize, re-rank, or merge them into the `**Reviews**` line. | invariant | L802 | F5-124 | - | - | none | unknown | procedure |
| FX-SUM-12 | **Attribute each block** when more than one source contributed, with a short scope label (round or relaying role) per `agents/pm.md`'s Final report shape. | command | L803 | F5-125 | attribution labels | - | none | unknown | procedure |
| FX-SUM-13 | **De-duplicate exact repeats** (keep the earliest attribution); keep near-duplicates that differ in substance separately. | command | L804 | F5-126 | - | - | none | unknown | procedure |
| FX-SUM-14 | When every source reported `No second-order effects identified.` or no emitting review ran, render the single line `None identified.`; do **not** omit the field. | field-or-template | L805 | F5-127 | `None identified.` | - | none | unknown | procedure |
| FX-SUM-15 | The `**Second-order effects**` field is unconditional, unlike `**Accepted compromises**`. | invariant | L805 | F5-128 | - | - | none | unknown | procedure |
| FX-SUM-16 | The `**Accepted compromises**` surface reflects the session-scoped compromise tracker's current contents at render time. | definition | L807 | F5-129 | - | tracker file | none | unknown | procedure |
| FX-SUM-17 | **Read the run's tracker file via the `Read` tool** at `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`/tmp/.quorum/...` POSIX, `%TEMP%\.quorum\...` Windows). | command | L809 | F5-130 | - | tracker path | none | unknown | procedure |
| FX-SUM-18 | If the tracker path is no longer in view, recover it from the run-state manifest's **Compromise tracker** field; use `Read`, no shell. | recovery | L809 | F5-131 | - | run-state manifest | none | unknown | procedure |
| FX-SUM-19 | **Omit the section entirely when there is nothing to show**: if the file does not exist OR has no `## Compromise <n>` entries, render no `**Accepted compromises**` line, no empty heading, no `N/A`, no placeholder. | invariant | L810 | F5-132 | - | `Read` result | none | unknown | procedure |
| FX-SUM-20 | Treat "file absent" and "file present but empty" identically: omit. | invariant | L810 | F5-133 | - | - | none | unknown | procedure |
| FX-SUM-21 | Rationale: an absent file is uncommon since ungated picks among ≥2 paths append an entry; Trigger C's lone-`trivial-tweak` carve-out is the only ungated route appending nothing. | rationale-only | L810 | F5-134 | - | - | none | unknown | rationale |
| FX-SUM-22 | **When entries exist, render one bullet per `## Compromise <n>` entry**, surfacing exactly four user-facing fields: the **finding** (`Finding (verbatim)`), the **chosen path** (`Decision`), the **rationale** (`Rationale`), and the **follow-up Issue ID** (`Follow-up Issue` — a ticket ID, or `none`). | field-or-template | L811-L815 | F5-135, F5-136, F5-137, F5-138, F5-139 | bullets | tracker entries | none | unknown | procedure |
| FX-SUM-23 | Do NOT surface the fifth entry field `Fix paths surfaced by reviewer`. | invariant | L817 | F5-140 | - | - | none | unknown | procedure |
| FX-SUM-24 | **Volume (>10 entries)**: surface ALL entries in full; do NOT truncate, summarize away, or elide any. | invariant | L818 | F5-141 | - | - | none | unknown | procedure |
| FX-SUM-25 | With >10 entries, precede the bullets with a short prologue noting the volume (e.g., "N compromises were accepted during this run:"). | field-or-template | L818 | F5-142 | prologue | entry count | none | unknown | procedure |
| FX-SUM-26 | This surface only **reads** the tracker — never writes, appends to, or deletes it; the write side is Section 7.5's append triggers. | invariant | L820 | F5-143 | - | - | none | unknown | procedure |

---

## 27. CKPT — Issue-boundary state-externalization checkpoint

- **Purpose:** At every Issue boundary (fixed or aborted), after the 7.5 gate closes: verify the five durable carriers (bees ticket, per-issue commit, tracker, `defer-*` ledger, manifest), fix any gap now, rewrite the manifest, and start the next Issue by re-reading rather than recalling.
- **Failure it prevents:** A compaction losing load-bearing facts that were only in conversation (F5-151, F3-236); an unscoped `--grep` matching an earlier run's commit (F5-167); a bare `git log -1` seeing an `Encode deferral:` commit instead of the per-issue one (F5-166); narrating a context clear the orchestrator cannot perform (F5-181).
- **Env deps:** bees, git, TaskList, Bash. **TaskList-dependent: yes** (carrier 4 and the task walk).
- **Rows:** 32 (procedure 30, rationale 2).
- **Literals:** `#### Issue-boundary state-externalization checkpoint`; **Verify the carriers.** / **Rewrite the run-state manifest** / **Re-read, do not recall, at every dispatch on the next Issue.**; **Aborted-path qualification.**; `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD`; `HEAD~N`; Progress line `<issue-id>: aborted — no commit; Issue left open`; `none`; **What this checkpoint does not do.**
- **Edges:** Invoked by CLOSE step 5 and ABORT step 3 (always after HYG); Consumes MAN (validation, `Pre-session SHA`, `Compromise tracker`), TRACK (Trigger C entry-less carve-out), LEDGER; Produces the manifest rewrite MAN describes and the clean state GUARD / POSTC start from; explicitly not a context-reclamation lever (GUARD owns the fresh-session recommendation).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-CKPT-1 | `#### Issue-boundary state-externalization checkpoint` is the canonical anchor name; **it is a definition, not a step in Section 7's linear flow** — do not run it because reading reached the heading. | definition | L829 CKPT | F5-148 | - | - | none | unknown | procedure |
| FX-CKPT-2 | Run the checkpoint only where Section 7 step 5 or `#### Aborted-Issue close-out` step 3 calls for it — always after Section 7.5's deferral-hygiene gate has closed and before the next Issue starts (the list-mode note at L95 is a pointer, not the definition). | ordering | L95 Notes for list mode; L829; L843 | F1-078, F1-079, F5-149, F5-157 | - | 7.5 gate closure | none | unknown | procedure |
| FX-CKPT-3 | On the aborted path the Issue is left `open` with no commit; an `open` ticket plus absent commit is the durable record that the Issue was not fixed. | definition | L831 | F5-150 | - | - | none | no | procedure |
| FX-CKPT-4 | The checkpoint's job is to **verify that invariant and refresh the durable carriers** so any harness compaction can be re-derived from disk. | definition | L831 | F5-151 | - | - | none | unknown | procedure |
| FX-CKPT-5 | Durable carrier 1: **the Issue's bees ticket**, flipped `open` → `done` at step 1; re-readable via `bees show-ticket`. | definition | L837 | F5-152 | - | - | bees | no | procedure |
| FX-CKPT-6 | Durable carrier 2: **the per-issue git commit** with the `(<issue-id>)` token in its subject; re-readable via `git log` / `git diff`. | definition | L838 | F5-153 | - | - | git | no | procedure |
| FX-CKPT-7 | Durable carrier 3: **the session-scoped compromise tracker**; re-readable via `Read`. | definition | L839 | F5-154 | - | - | none | yes | procedure |
| FX-CKPT-8 | Durable carrier 4: **the `defer-*` TaskList ledger**, emptied by Section 7.5's hard-stop gate before the checkpoint; re-readable by walking the TaskList. | definition | L840 | F5-155 | - | - | TaskList | yes | procedure |
| FX-CKPT-9 | Durable carrier 5: **the run-state manifest**, carrying ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress; re-readable via `Read`. | definition | L841 | F5-156 | - | - | none | yes | procedure |
| FX-CKPT-10 | Every checkpoint step is a tool call the orchestrator can actually make — bees query, git command, file read, TaskList walk, file write. | invariant | L843 | F5-158 | - | - | bees, git, TaskList | unknown | procedure |
| FX-CKPT-11 | Step 1 — **Verify the carriers.** Do all four verifications. | command | L845 | F5-159 | verification results | carriers | bees, git, TaskList | unknown | procedure |
| FX-CKPT-12 | **Aborted-path qualification**: when invoked from `#### Aborted-Issue close-out`, confirm the Issue reads **`open`** (not `done`) and expect **no** commit — skip the `(<issue-id>)` subject-token search entirely; tracker and TaskList checks run unchanged. | recovery | L845 | F5-160 | - | invoking site | bees | no | procedure |
| FX-CKPT-13 | Re-read the just-fixed Issue in bees and confirm it reads `done`. | command | L846 | F5-161 | - | bees ticket | bees | no | procedure |
| FX-CKPT-14 | Confirm the per-issue commit via `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (same form as Section 9 step 4's re-derive path; identical on POSIX and PowerShell). | command | L847 | F5-162 | - | `<pre-session-sha>`; commit subjects | git | no | procedure |
| FX-CKPT-15 | Resolve `<pre-session-sha>` by `Read`ing the run-state manifest's **Pre-session SHA** field — not from a value quoted earlier in the conversation (validate the manifest first — FX-MAN-20/21). | command | L847 | F5-163 | - | manifest **Pre-session SHA** | none | unknown | procedure |
| FX-CKPT-16 | **Do not use a bare `git log --oneline -1`** — Section 7.5's Encode branch may land an `Encode deferral: ...` commit on top of the per-issue commit. | invariant | L847 | F5-166 | - | - | git | unknown | procedure |
| FX-CKPT-17 | **Do not drop the `<pre-session-sha>..HEAD` bound** — an unscoped `--grep` can match a same-`(<issue-id>)` commit from an earlier run. | invariant | L847 | F5-167 | - | - | git | unknown | procedure |
| FX-CKPT-18 | An empty result from the ranged `--grep` is a real gap; a non-empty result is this run's per-issue commit wherever it sits. | definition | L847 | F5-168 | gap determination | git output | git | unknown | procedure |
| FX-CKPT-19 | `Read` the compromise-tracker file at the manifest's **Compromise tracker** path and confirm every compromise accepted on this Issue has an entry. | command | L848 | F5-169 | - | manifest field; tracker file | none | yes | procedure |
| FX-CKPT-20 | **A `Read` reporting that the file does not exist is not by itself a gap** — the tracker is created only on its first append trigger. | precondition | L848 | F5-170 | - | `Read` result | none | yes | procedure |
| FX-CKPT-21 | Do not read an absent tracker as the expected state; read it as "nothing was appended" and check that against what this Issue actually did. | command | L848 | F5-171 | - | routing history | none | unknown | procedure |
| FX-CKPT-22 | Treat absence as a gap only if a compromise **was accepted**, or an ungated path pick **that Trigger C requires an entry for** was dispatched, and no entry/file exists. | precondition | L848 | F5-172 | gap determination | Trigger C rules | none | unknown | procedure |
| FX-CKPT-23 | Rationale: a unit whose sole ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less; reporting a gap would contradict Trigger C. | rationale-only | L848 | F5-173 | - | - | none | unknown | rationale |
| FX-CKPT-24 | Walk the TaskList and confirm every per-issue role task and `gate-*` task is `completed` and the `defer-*` active set is empty. | command | L849 | F5-174 | - | TaskList | TaskList | yes | procedure |
| FX-CKPT-25 | Fix any verification gap **now** rather than carrying it forward in conversation. | invariant | L851 | F5-175 | gap fixes | verification results | bees, git, TaskList | yes | procedure |
| FX-CKPT-26 | Step 2 — **Rewrite the run-state manifest** in full per Section 1, recording the just-fixed Issue's ID and commit SHA under progress and the next Issue's ID as next unit (or `none` in single mode / batch exhausted). | command | L212; L852 | F1-164, F5-176 | run-state manifest | Issue id; commit SHA; batch | none | yes | procedure |
| FX-CKPT-27 | Step 3 — **Re-read, do not recall, at every dispatch on the next Issue**: `bees show-ticket` its body/status and `Read` the manifest for ordered batch, isolation strategy, tracker path, `<pre-session-sha>`. | invariant | L853 | F5-178 | - | bees ticket; manifest | bees | yes | procedure |
| FX-CKPT-28 | **On the aborted path**, record the Issue in Progress as `<issue-id>: aborted — no commit; Issue left open` and set the next unit by the same batch rule. | field-or-template | L232; L852 | F1-182, F5-177 | manifest **Progress** entry | abort outcome | none | no | procedure |
| FX-CKPT-29 | The next Issue's design directive comes from its own Section 3 Analyst pass, never from the previous Issue's. | invariant | L853 | F5-179 | - | - | Agent | no | procedure |
| FX-CKPT-30 | Carry **no** value forward from the prior Issue; if a needed fact is not readable from a carrier, stop and write it into one before dispatching anything. | invariant | L853 | F5-180 | carrier write | carriers | none | yes | procedure |
| FX-CKPT-31 | **What this checkpoint does not do**: it does not clear, compact, or reclaim the orchestrator's context and must never be narrated as if it did; orchestrator context grows **monotonically within a session** (across the batch in `all` / list mode), **nothing in this skill reclaims those tokens**, the harness owns compaction, and the skill has no model-invocable clear/compact. | invariant | L555 `#### Recursive delegation: not supported`; L855 | F3-235, F5-181 | - | - | none | yes | procedure |
| FX-CKPT-32 | Rationale: growth is **survivable** because this checkpoint keeps every load-bearing fact in a durable carrier, making any compaction lossless; the only reclamation lever is a **fresh session** per the fresh-session-per-phase recommendation. | rationale-only | L555; L855 | F3-236, F5-182 | - | - | none | yes | rationale |

---

## 28. GUARD — Context-window boundary guard

- **Purpose:** On the one continuing in-session path (batch mode with a next Issue), read an external gauge file via the sibling `context_gauge.py` helper and stop the batch at the clean Issue boundary — recommending a fresh session with the exact resume command — before auto-compaction fires mid-Issue.
- **Failure it prevents:** Auto-compaction partway through the next Issue (F5-189); trusting a stale (low-biased) reading as headroom (F5-208); a stranded gate task created before the reading is in hand (F5-191).
- **Env deps:** Bash, TaskList, AskUserQuestion, none. **TaskList-dependent: yes** (Step 5 gate only).
- **Rows:** 39 (procedure 36, rationale 3).
- **Literals:** `#### Context-window boundary guard`; `CLAUDE_CODE_SESSION_ID`; `printenv CLAUDE_CODE_SESSION_ID` / `Write-Output $env:CLAUDE_CODE_SESSION_ID`; helper `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (`\..\quo-setup\scripts\context_gauge.py`); modes `stop-threshold`, `read --session-id <trimmed-session-id>`, `write-opt-out`; `read` outputs integer percentage / `no-reading` / `stale` / `missing`, exit `0` / `2`; opt-out marker `<tempdir>/.quorum/context-guard-opt-out` (`test -f /tmp/.quorum/context-guard-opt-out` / `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"`); gauge file `<tempdir>/.quorum/context-usage-<session_id>.json` with `session_id`, `context_window.used_percentage`; options **Configure now**, **Proceed without the guard (this run)**, **Never guard me (persistent opt-out)**, **Stop here**; `/quo-setup --configure-gauge-producer`; resume commands `/quo-fix-issue all`, `/quo-fix-issue <remaining-ids>`.
- **Edges:** Invoked only by CLOSE step 5's batch-continuing branch, after CKPT; mirrors EFF's read-first ordering; uses GATE; sibling-resolution discipline in SHELL; never runs on run-ending paths (POSTC) or the ABORT stop.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-GUARD-1 | The guard is a **definition co-located with the Issue-boundary checkpoint**; run it only on the **one continuing, in-session path** (batch mode with a next Issue), after the checkpoint and before looping to step 2. | ordering | L859 CWG | F5-183 | - | run mode; checkpoint completion | none | yes | procedure |
| FX-GUARD-2 | The guard does **NOT** run on run-ending paths: single mode and batch-exhausted mode both proceed to Section 8 without it. | invariant | L859 | F5-184 | - | run mode | none | yes | procedure |
| FX-GUARD-3 | **`#### Aborted-Issue close-out` does not invoke it either** — an aborted Issue stops the batch at its step 4. | invariant | L859 | F5-185 | - | - | none | no | procedure |
| FX-GUARD-4 | Do not inherit the checkpoint's unconditionality; a single-Issue run crosses no boundary and never invokes the guard. | invariant | L859 | F5-186 | - | - | none | yes | procedure |
| FX-GUARD-5 | **What the guard reads**: an **external gauge file** from a separate status-line producer; it does not and cannot measure the orchestrator's own token usage. | definition | L861 | F5-187 | - | gauge file | none | yes | procedure |
| FX-GUARD-6 | The only reclamation lever is a **fresh session**; the guard never instructs the orchestrator to clear or compact its own context. | invariant | L861 | F5-188 | - | - | none | yes | procedure |
| FX-GUARD-7 | The guard's job is to stop the batch at this clean Issue boundary before auto-compaction fires partway through the next Issue. | definition | L861 | F5-189 | - | - | none | yes | rationale |
| FX-GUARD-8 | **Ordering is load-bearing**: read the session id **first**, evaluate it, and only then decide whether any gate task is created (mirror Section 1's `#### Check session reasoning effort`). | ordering | L863 | F5-190 | - | session id | Bash | yes | procedure |
| FX-GUARD-9 | **Step 1 — read the session id** with one literal command: POSIX `printenv CLAUDE_CODE_SESSION_ID`; PowerShell `Write-Output $env:CLAUDE_CODE_SESSION_ID`. | command | L865-L875 | F5-192 | session id | `CLAUDE_CODE_SESSION_ID` | Bash | yes | procedure |
| FX-GUARD-10 | **Trim any trailing whitespace or newline** from the session id before use (a trailing newline fails `--session-id` charset validation). | command | L877 | F5-193 | trimmed session id | session id | none | yes | procedure |
| FX-GUARD-11 | **Step 2 — session id unset or empty → skip the guard silently and continue** to the next Issue (back to Section 2); create no `gate-*` task, emit no output. | precondition | L879 | F5-194 | - | session id | none | yes | procedure |
| FX-GUARD-12 | The unset-session-id path is the ONLY silent-skip path (unsupported-CLI carve-out), matching Section 1's treatment of an unset `CLAUDE_EFFORT`. | invariant | L879 | F5-195 | - | - | none | yes | procedure |
| FX-GUARD-13 | **Step 3 — session id present**: resolve the gauge helper as `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (POSIX `/`, PowerShell `\`; base directory from the skill invocation header). | command | L881 | F5-196 | helper path | skill base directory | none | yes | procedure |
| FX-GUARD-14 | Obtain the stop threshold with one literal call: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold`; PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold`. | command | L883-L893 | F5-198 | threshold integer | helper | Bash | yes | procedure |
| FX-GUARD-15 | Compare the reading against whatever integer the `stop-threshold` seam prints; the helper is the single definition site and prose never restates the number. | invariant | L895 | F5-199 | - | threshold | none | yes | procedure |
| FX-GUARD-16 | Read the current reading with one literal call: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>`; PowerShell `python "...\context_gauge.py" read --session-id <trimmed-session-id>`. | command | L897-L907 | F5-200 | reading | trimmed session id | Bash | yes | procedure |
| FX-GUARD-17 | **Step 4 — branch on the `read` output and its exit status**: `read` prints exactly one of an integer percentage, `no-reading`, `stale`, `missing` (exit `0` for all four); it exits `2` on a malformed gauge OR an invalid `--session-id`. | definition | L909 | F5-201 | - | `read` stdout/exit | Bash | yes | procedure |
| FX-GUARD-18 | The fresh-session resume command is `/quo-fix-issue all` for an `all` run, or `/quo-fix-issue <remaining-ids>` listing the still-unfixed subset (Issues not yet `done`) for a list run. | field-or-template | L909 | F5-202 | resume command text | batch; ticket statuses | none | no | procedure |
| FX-GUARD-19 | **Integer ≥ threshold → STOP** at this boundary: report the percentage, recommend resuming in a **fresh session** naming the exact resume command, then exit the skill (do not loop to step 2). | gate | L911 | F5-203 | stop report | reading; threshold | none | yes | procedure |
| FX-GUARD-20 | **Integer < threshold → continue** to the next Issue (back to step 2) with no output. | ordering | L912 | F5-204 | - | reading | none | yes | procedure |
| FX-GUARD-21 | **`no-reading` → continue** to the next Issue with no output — the transient fresh-but-null state. | ordering | L913 | F5-205 | - | reading | none | yes | procedure |
| FX-GUARD-22 | **`stale` → STOP**: note the producer appears stalled, that recurring staleness means the operator should check their status-line producer, and recommend the fresh-session resume with the command. | gate | L914 | F5-206 | stop report | reading | none | yes | procedure |
| FX-GUARD-23 | Do NOT let `stale` fall through to continue. | invariant | L914 | F5-207 | - | - | none | yes | procedure |
| FX-GUARD-24 | Rationale: usage only grows within a session, so a stale number biases low and must not be trusted as headroom. | rationale-only | L914 | F5-208 | - | - | none | yes | rationale |
| FX-GUARD-25 | **Non-zero exit, or empty stdout → the same fail-safe stop-and-ask as `stale`** (an untrustworthy reading); never fall through to continue. | gate | L915 | F5-209, F5-211 | stop report | `read` exit/stdout | none | yes | procedure |
| FX-GUARD-26 | Do NOT assume exit `2` implies a corrupt file — it also means an invalid `--session-id`. | invariant | L915 | F5-210 | - | - | none | yes | procedure |
| FX-GUARD-27 | **`missing`** (no gauge file) → before stopping, check the persistent opt-out marker at `<tempdir>/.quorum/context-guard-opt-out` (`/tmp/.quorum/context-guard-opt-out` POSIX, `%TEMP%\.quorum\context-guard-opt-out` Windows). | command | L916 | F5-212 | - | opt-out marker | Bash | yes | procedure |
| FX-GUARD-28 | Existence check is one literal call: POSIX `test -f /tmp/.quorum/context-guard-opt-out`; PowerShell `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"`. | command | L918-L926 | F5-213 | marker presence | filesystem | Bash | yes | procedure |
| FX-GUARD-29 | **If the marker is present → skip the guard silently and continue** to the next Issue (back to step 2). | ordering | L928 | F5-214 | - | marker presence | none | yes | procedure |
| FX-GUARD-30 | **If absent → hard-stop via the two-step gate in step 5 below.** | gate | L928 | F5-215 | - | marker absence | none | yes | procedure |
| FX-GUARD-31 | **Step 5 — the missing-reading gate** is reached only from the `missing`-and-no-marker branch; fire it via the two-step contract naming this boundary context-guard gate (FX-GATE-1/3/5/6). | precondition | L930 | F5-216 | gate | - | TaskList, AskUserQuestion | yes | procedure |
| FX-GUARD-32 | Question text must (a) state that the environment may override the operator's user-level status-line config, so no reading is being published; (b) publish the gauge file contract: path `<tempdir>/.quorum/context-usage-<session_id>.json`, required `session_id` and `context_window.used_percentage` fields, and overwrite-per-refresh semantics; (c) state that **Configure now** runs `/quo-setup --configure-gauge-producer` inline. | field-or-template | L930 | F5-220, F5-221, F5-222 | question text | - | AskUserQuestion | yes | procedure |
| FX-GUARD-33 | Option **Configure now** — invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool (same inline-Skill precedent as Section 1's URL-resolution `/quo-file-issue`). | choice-set | L932 | F5-224 | Skill invocation | - | none | yes | procedure |
| FX-GUARD-34 | After a successful Configure now, **recommend resuming in a fresh session** with the resume command (the producer publishes only **next** session) rather than implying the run is now guarded, then exit. | ordering | L932 | F5-225 | recommendation; exit | - | none | yes | procedure |
| FX-GUARD-35 | Option **Proceed without the guard (this run)** — continue to the next Issue (back to step 2); write no marker. | choice-set | L933 | F5-226 | - | - | none | yes | procedure |
| FX-GUARD-36 | Option **Never guard me (persistent opt-out)** — write the marker via the helper's `write-opt-out` mode (one literal call), then continue to the next Issue. | choice-set | L934 | F5-227 | opt-out marker | - | Bash | yes | procedure |
| FX-GUARD-37 | Opt-out write command: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" write-opt-out`; PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" write-opt-out`. | command | L936-L944 | F5-228 | `context-guard-opt-out` file | helper | Bash | yes | procedure |
| FX-GUARD-38 | Option **Stop here** — exit the skill with the fresh-session resume command. | choice-set | L946 | F5-229 | stop report | resume command | none | yes | procedure |
| FX-GUARD-39 | Rationale: the helper path uses the same sibling-resolution discipline as `scoped_marker_resolver.py` and `hive_commit.py` (generic rule FX-SHELL-5). | rationale-only | L881 | F5-197 | - | - | none | yes | rationale |

---

## 29. ABORT — Aborted-Issue close-out

- **Purpose:** When an Issue ends without a fix landing (Analyst-gate `Cancel`, gate (d) `Cancel`, unexplained-movement `Abort this Issue`), still treat it as an Issue boundary: sweep its tasks by prefix, run the 7.5 gate, run the checkpoint's aborted path, read the working tree, and — in batch mode with Issues remaining — stop the run with a resume command rather than handing a dirty tree to the next Issue.
- **Failure it prevents:** An `aborted-*` marker holding Phase C shut on re-entry, stranded `defer-*` entries, a manifest naming a left Issue (F5-235); the next Issue's Doc Writer reading the dirty tree as "the Engineer's diff", the fingerprint fallback sweeping it in, staging absorbing it (F5-255).
- **Env deps:** TaskList, AskUserQuestion, git, bees, Agent. **TaskList-dependent: yes.**
- **Rows:** 31 (procedure 28, rationale 2, failure-narrative 1).
- **Literals:** `#### Aborted-Issue close-out`; **without a fix landing**; `git status --porcelain`; resume commands `/quo-fix-issue <remaining-ids>` / `/quo-fix-issue all`; **Batch mode with a next Issue still remaining in the batch — STOP the run here.**; **"clear from the active set" means mark the task `completed`**.
- **Edges:** Entered from ANA (`Cancel`), ROUTE gate (d) (`Cancel`), UNEXP (`Abort this Issue`), DQ (Cancel after re-fire); runs CLOSE's sweep at its own site, HYG (step 2), CKPT aborted path (step 3); never runs GUARD; single / batch-exhausted proceed to POSTC; explicitly NOT used by POSTC's own abort (FX-POSTC-82..84).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-ABORT-1 | `#### Aborted-Issue close-out` is the canonical anchor name for the path where an Issue ends **without a fix landing**. | definition | L950 AIC | F5-230 | - | - | none | no | procedure |
| FX-ABORT-2 | Three branches route here: Section 4's unexplained-movement gate's **Abort this Issue**, Section 3's Analyst-proposal gate's **Cancel**, and the routing-decision gate's **Cancel** (part (d) of ODR). | definition | L950 | F5-231 | - | gate answers | AskUserQuestion | no | procedure |
| FX-ABORT-3 | **This is a definition, not a step in Section 7's linear flow** — run it only where one of those three branches calls for it by name. | invariant | L950 | F5-232 | - | - | none | no | procedure |
| FX-ABORT-4 | An aborted Issue is still an Issue boundary; never leave it by simply "moving on" — the fixed path's close-outs (TaskList sweep, deferral-hygiene gate, checkpoint) must all run. | invariant | L952 | F5-233 | - | - | none | no | procedure |
| FX-ABORT-5 | In batch mode the aborted boundary ends the run rather than advancing to the next Issue (step 4). | ordering | L952 | F5-234 | - | run mode | none | no | procedure |
| FX-ABORT-6 | Failure narrative: skipping close-out lets an `aborted-*` marker hold Phase C shut on re-entry, strands `defer-*` entries, and leaves the manifest naming a left Issue. | rationale-only | L952 | F5-235 | - | - | none | no | failure-narrative |
| FX-ABORT-7 | Run the four aborted close-out steps in order. | ordering | L952 | F5-236 | - | - | none | no | procedure |
| FX-ABORT-8 | Step 1 — **Close out this Issue's TaskList tasks** by **prefix**: `analyst-<issue-id>` (+`-rev<n>`; already `completed`, so a no-op), `engineer-<issue-id>` / `code-reviewer-<issue-id>`, `test-writer-<issue-id>` / `doc-writer-<issue-id>`, `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>`, every `-r<n>` round, and the `gate-*` task that fired the branch. | command | L341 `#### Branch on the user's choice`; L954 | F2-096, F5-237 | TaskList status flips | TaskList | TaskList | no | procedure |
| FX-ABORT-9 | **Include every `aborted-<role>-<issue-id>` redelivery marker still `pending`, when one is open**, in the sweep. | command | L954 | F5-238 | TaskList status flips | TaskList | TaskList | no | procedure |
| FX-ABORT-10 | Run the aborted-marker clause on every branch rather than assuming it has nothing to sweep — a Section 3 `Cancel` re-fired from a Phase A round can land with a marker another lane opened. | invariant | L954 | F5-239 | - | TaskList | TaskList | no | procedure |
| FX-ABORT-11 | Mark each swept task `completed` with the abort reason recorded in `metadata.activity` — informational context, never a routing input. | field-or-template | L954 | F5-240 | `metadata.activity` | abort reason | TaskList | no | procedure |
| FX-ABORT-12 | **"clear from the active set" means mark the task `completed`** — never delete it, or the `-r<n>` round count derived by counting recorded rounds is lost. | invariant | L954 | F5-241 | - | - | TaskList | no | procedure |
| FX-ABORT-13 | **A sibling lane still in flight when this close-out fires**: the orchestrator cannot terminate a background Agent — mark its task `completed` anyway and record in `metadata.activity` that it was in flight at the abort. | command | L956 | F5-242 | TaskList flip; `metadata.activity` | live Agents | TaskList, Agent | no | procedure |
| FX-ABORT-14 | Which lanes may be live per branch: Abort-this-Issue → the non-aborting Phase B writer; Phase C routing `Cancel` → unreturned reviewers/PM; Section 3 `Cancel` re-fired from `Re-dispatch the Analyst with this finding` → whatever Phase A/C lanes were active (typically none on Phase A). | definition | L956 | F5-243 | - | - | Agent | no | procedure |
| FX-ABORT-15 | When a late completion notification arrives for a closed-out Issue: process nothing for that Issue, note an implementer lane may have partially landed work (review-only lanes land nothing), and continue with the current unit. | recovery | L956 | F5-244 | - | Agent notification | Agent | no | procedure |
| FX-ABORT-16 | Step 2 — **Run Section 7.5's deferral-hygiene gate** for this Issue over any deferral it already recorded. | command | L341; L444 RL; L682 ODR (d); L957 | F2-097, F5-245 | gate run | `defer-*` tasks | TaskList, AskUserQuestion | no | procedure |
| FX-ABORT-17 | The gate's hard-stop applies unchanged: do not advance while any `defer-*` task is `pending` or `in_progress`. | invariant | L957 | F5-246 | - | TaskList | TaskList | no | procedure |
| FX-ABORT-18 | Deferrals on an aborted Issue include the Analyst's `### Deferred refinements` bullets and any reviewer/PM feedback the Director ignored in whichever phases were reached. | definition | L957 | F5-247 | - | `### Deferred refinements`; `defer-*` | TaskList | no | procedure |
| FX-ABORT-19 | Step 3 — **Run the Issue-boundary state-externalization checkpoint** on its **aborted path** (inverted step-1 verifications; aborted **Progress** entry in step 2); everything else runs unchanged. | command | L341; L958 | F2-098, F5-248 | checkpoint run; manifest | - | bees, git, TaskList | no | procedure |
| FX-ABORT-20 | Step 4 — **Read the working tree, then branch on mode**: an aborted Issue lands no commit, so the phases' edits stay uncommitted and the run does **not** carry that tree into another Issue (unlike a fixed one). | ordering | L444 RL; L959 | F3-148, F5-249 | - | working tree | git | no | procedure |
| FX-ABORT-21 | Tree contents depend on the entering branch: an **initial** Section 3 `Cancel` typically leaves nothing; a `Cancel` re-fired from Phase A/C via `Re-dispatch the Analyst with this finding` leaves a Phase A round's edits or a full Phase A/B pass. | definition | L959 | F5-250 | - | - | none | no | rationale |
| FX-ABORT-22 | Read the tree with one literal command, `git status --porcelain` (identical on POSIX and PowerShell), so the messages can name the paths. | command | L961-L971 | F5-251 | uncommitted path list | working tree | git | no | procedure |
| FX-ABORT-23 | **Single-issue mode** — **Name the aborted Issue and the uncommitted paths**, then proceed to Section 8 over what the session did land; if no commit landed at all, say so plainly and exit rather than dispatching a sweep over an empty diff. (Section 3's phrasing "in single-issue mode the run ends there" — see Inconsistencies.) | ordering | L341; L975 | F2-099, F5-252 | operator message | `git status --porcelain` | none | no | procedure |
| FX-ABORT-24 | **Batch mode (`all` or list) with the batch exhausted** — name the aborted Issue and uncommitted paths, then proceed to Section 8. | ordering | L976 | F5-253 | operator message | `git status --porcelain` | none | no | procedure |
| FX-ABORT-25 | **Batch mode with a next Issue still remaining in the batch — STOP the run here.** Do **NOT** proceed to the next Issue; `Cancel` / Abort does not decide the run's fate — this mode branch does, because this Issue's edits are left uncommitted. | gate | L341; L444 RL; L682 ODR (d); L977 | F2-100, F3-147, F4-132, F5-254 | run stop | run mode; working tree | git | no | procedure |
| FX-ABORT-26 | Rationale: the next Issue would inherit a dirty tree — its Doc Writer would read it as "the Engineer's diff", the fingerprint fallback would sweep it into `## Source paths to fingerprint`, and staging could absorb it into an unrelated commit. | rationale-only | L977 | F5-255 | - | - | none | no | rationale |
| FX-ABORT-27 | Do **not** run the **Context-window boundary guard** on this aborted-batch stop — it is a run-ending path. | invariant | L977 | F5-256 | - | - | none | no | procedure |
| FX-ABORT-28 | Tell the operator **which Issue aborted**, the **uncommitted paths** `git status --porcelain` reported, and the **fresh-session resume command** (`/quo-fix-issue <remaining-ids>` for not-yet-`done` Issues, or `/quo-fix-issue all` on an `all` run). | relay | L977 | F5-257 | operator message | `git status --porcelain`; batch; ticket statuses | none | no | procedure |
| FX-ABORT-29 | Then exit the skill so the operator resolves the tree before the batch resumes. | ordering | L977 | F5-258 | exit | - | none | no | procedure |
| FX-ABORT-30 | Exit a cancelled / aborted Issue through `#### Aborted-Issue close-out` rather than closing out by hand or simply moving to the next Issue — from Section 3's `Cancel`, the unexplained-movement gate's **Abort this Issue**, gate (d)'s `Cancel`, and the design-question re-fire's `Cancel` alike. | ordering | L341; L444 RL; L455 RL; L682 ODR (d) | F2-095, F3-146, F4-131 | close-out sequence | Cancel / Abort answer | TaskList, git | no | procedure |
| FX-ABORT-31 | On Cancel / Abort, **NO commit is made; the Issue stays `open`** and nothing is committed for it. | invariant | L341; L444 RL | F2-094, F3-145 | - | Cancel / Abort answer | git, bees | no | procedure |

---

## 30. HYG — Deferral-hygiene gate (Section 7.5 Steps 0–3, Fix / File / Encode, `hive_commit.py`)

- **Purpose:** Before any handoff (per-Issue on both boundary paths, and once more at batch end), reconcile every deferred item into the `defer-*` ledger (Step 0), enumerate it (Step 1), surface it and gate the user's Fix / File / Encode routing (Step 2), land Encode writes with one follow-up commit via `hive_commit.py`, and hard-stop until the active set is empty (Step 3).
- **Failure it prevents:** Deferrals surfaced mid-run evaporating before they reach a durable carrier (F6-191); orchestrators that missed the upstream record-creating steps (F6-114); Encode writes leaving the working tree dirty at yield (F6-159); per-batch accumulation surprising the user (F6-122).
- **Env deps:** TaskList, AskUserQuestion, bees, git, Bash, Agent. **TaskList-dependent: yes.**
- **Rows:** 86 (procedure 75, rationale 9, example 2).
- **Literals:** `### 7.5 Before handoff — deferral hygiene`; **Step 0 — Retroactive ledger reconciliation (safety net).** / **Step 1 — Enumerate the active deferral ledger.** / **Step 2 — Surface the active set and gate the user choice.** / **Step 3 — Hard-stop on a non-empty active set.**; **Per-Issue firing.** (**Fixed path** / **Aborted path**) / **Batch end-of-run firing.**; messages `Deferral hygiene: no deferred items.`, `Deferral hygiene (batch close): no deferred items.`; choices `Fix in this session`, `File as issue tickets`, `Encode in an existing ticket body`; Encode heading `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)`; `bees update-ticket --ids <ticket-id> --body-file <path>`; scratch file `bees-body-<defer-N>.md` (`bees-body-defer-3.md`); commit subject `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded`; `hive_commit.py` (`<this skill's base directory>/../quo-execute/scripts/hive_commit.py`; `--skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`; `skipped: nothing staged`); `bees list-hives`; `git diff --cached`; destinations Plan Bee / Epic / Task / Subtask / Spec Bee `t1=Doc` child / PRD-SDD via doc-writer pass; `addressed-now-in-this-Task`.
- **Edges:** Consumes LEDGER (`defer-*` tasks), DEFC (Analyst block), SUM (`**Ignored Review Feedback**`), REVIEW (PM Final report), CLOSE (commit precedent, `hive_commit.py` sibling), SHELL (scratch conventions), ARG (`/quo-file-issue` inline precedent), GATE; invoked by CLOSE step 5, ABORT step 2, POSTC (end-of-batch); Produces empty ledger for CKPT.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-HYG-1 | The `AskUserQuestion` firings covered by the two-step contract here are Step 2's initial Fix / File / Encode choice plus any Step 3 re-fires for an unclosed `defer-*` subset. | definition | L981 §7.5 intro | F6-002 | - | active `defer-*` set | none | yes | procedure |
| FX-HYG-2 | Agents across Sections 3–6 may flag items as "address later", "defer to next phase", "pick up during a follow-up Issue", or similar inter-session deferrals. | definition | L1043 | F6-099 | - | agent reports | none | no | procedure |
| FX-HYG-3 | Each deferred item arrives with a destination annotation per `agents/pm.md`'s Final report contract and `agents/analyst.md`'s `### Deferred refinements` block. | definition | L1043 | F6-100 | - | PM Final report, Analyst block | none | no | procedure |
| FX-HYG-4 | The `defer-*` recording sites are the Section 3 Analyst-Approve / Analyst-Revise consumption sites and the Section 5 may-ignore-feedback site. | definition | L1043 | F6-102 | - | - | TaskList | no | procedure |
| FX-HYG-5 | This gate is the pre-handoff reconciliation that closes deferrals into durable inter-session carriers before yield (single), advance (batch), or Section 8. | definition | L1043 | F6-103 | durable carriers | active set | none | yes | procedure |
| FX-HYG-6 | **Step 0**: before Step 1's enumeration, walk three additional surfaces and **create a corresponding `defer-*` TaskList task for any item that does not already have one**. | command | L1045 | F6-104 | `defer-*` tasks | three surfaces | TaskList | unknown | procedure |
| FX-HYG-7 | Surface 1: **Section 5's per-Issue `**Ignored Review Feedback**` summary field**; each non-`None` bullet maps to a `defer-*` task. | definition | L1047 | F6-105 | `defer-*` tasks | `**Ignored Review Feedback**` | TaskList | unknown | procedure |
| FX-HYG-8 | **Surface 1 does not exist on the aborted path**: `#### Aborted-Issue close-out` invokes the gate without Section 7 step 4, so skip surface 1 there. | precondition | L1047 | F6-106 | - | invocation path | none | no | procedure |
| FX-HYG-9 | Do not treat surface 1's absence on the aborted path as an empty active set. | invariant | L1047 | F6-107 | - | - | none | no | procedure |
| FX-HYG-10 | Surfaces 2 and 3 still apply on the aborted path: the Analyst's block exists whenever Section 3 ran; a PM Final report exists whenever a Phase C PM returned before the abort. | precondition | L1047 | F6-108 | - | Analyst block, PM report | none | no | procedure |
| FX-HYG-11 | Surface 2: **PM Agent's Final report deferred items**; every item with `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task. | definition | L1048 | F6-109 | `defer-*` tasks | PM Final report | TaskList | yes | procedure |
| FX-HYG-12 | Skip PM items annotated `addressed-now-in-this-Task` because they were addressed inline. | precondition | L1048 | F6-110 | - | annotation | none | yes | procedure |
| FX-HYG-13 | Surface 3: **Analyst's `### Deferred refinements` block**; every non-`None` bullet with `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task. | definition | L1049 | F6-111 | `defer-*` tasks | Analyst return | TaskList | no | procedure |
| FX-HYG-14 | Skip Analyst bullets annotated `addressed-now-in-this-Issue`. | precondition | L1049 | F6-112 | - | annotation | none | no | procedure |
| FX-HYG-15 | Rationale: the Section 3 Approve / Revise consumption paragraph is the load-bearing source for Analyst items; the sweep is defense-in-depth. | rationale-only | L1049 | F6-113 | - | - | none | no | rationale |
| FX-HYG-16 | Rationale: the upstream record-creating instructions (Section 3 consumption paragraph, Section 5 may-ignore site) are load-bearing; Step 0 is the safety net for orchestrators that miss them. | rationale-only | L1051 | F6-114 | - | - | none | unknown | rationale |
| FX-HYG-17 | After the retroactive reconcile, every deferred item from the three surfaces is in the active `defer-*` set, so Step 1 sees the canonical view. | invariant | L1051 | F6-115 | canonical active set | Step 0 output | TaskList | unknown | procedure |
| FX-HYG-18 | **Per-Issue firing**: the gate fires at the end of every Issue on **both** boundary paths; it has two invocation sites, not one. | invariant | L1053 | F6-116 | gate fire | Issue boundary | none | no | procedure |
| FX-HYG-19 | **Fixed path**: fire between Section 7's mark-done-and-commit step and the per-Issue advance (next Issue in batch mode, Section 8 in single mode). | ordering | L1055 | F6-117 | gate fire | Section 7 commit | none | no | procedure |
| FX-HYG-20 | **Aborted path**: fire from `#### Aborted-Issue close-out` step 2, after that close-out's prefix sweep and before the Issue-boundary state-externalization checkpoint. | ordering | L1056 | F6-118 | gate fire | AIC step 2 | TaskList | no | procedure |
| FX-HYG-21 | On the aborted path the Issue stays `open` with no commit, but pre-abort deferrals are equally stranded and this gate moves each into a durable carrier. | definition | L1056 | F6-119 | durable carriers | pre-abort `defer-*` | none | no | procedure |
| FX-HYG-22 | The Step 3 hard-stop applies unchanged on the aborted path. | invariant | L1056 | F6-120 | - | - | none | no | procedure |
| FX-HYG-23 | The per-Issue firing scopes the active set to **deferrals surfaced during this Issue only**. | invariant | L1058 | F6-121 | scoped active set | `defer-*` tasks | TaskList | yes | procedure |
| FX-HYG-24 | Rationale: prior Issues' deferrals were closed at their own gate; per-batch accumulation would surprise the user and defeat per-Issue close-out discipline. | rationale-only | L1058 | F6-122 | - | - | none | yes | rationale |
| FX-HYG-25 | **Batch end-of-run firing**: in batch / `all` mode, re-fire the gate between the last Issue's Section 7.5 close-out and Section 8's fresh-context sweep, treating the invocation as the end-of-batch firing per this section's batch-firing semantics. | ordering | L1060; L1118 PC | F6-123, F7-004, F7-005 | gate fire | batch exhaustion | AskUserQuestion, TaskList | unknown | procedure |
| FX-HYG-26 | The end-of-batch firing catches deferrals surfaced *between* Issues (inter-Issue advance boundary, batch-level reconciliation) belonging to no per-Issue gate. | definition | L1060; L1118 PC | F6-124, F7-007 | - | between-Issue deferrals | none | unknown | procedure |
| FX-HYG-27 | Rationale: the end-of-batch active set should typically be empty; the firing exists as a defensive sweep against boundary / reconciliation deferrals. | rationale-only | L1060; L1118 PC | F7-009 | - | - | none | no | rationale |
| FX-HYG-28 | In single mode, skip the end-of-batch firing — the per-Issue firing already covered the active set; the batch-firing prose is a no-op there. | precondition | L1118 PC | F7-008 | - | run mode | none | no | procedure |
| FX-HYG-29 | **Step 1**: scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. | command | L1062 | F6-126 | active set | TaskList | TaskList | yes | procedure |
| FX-HYG-30 | If the active set is empty on a per-Issue firing, emit the one-line console message `Deferral hygiene: no deferred items.`. | field-or-template | L1062 | F6-127 | console line | active set | none | yes | procedure |
| FX-HYG-31 | If the active set is empty on an end-of-batch firing, emit `Deferral hygiene (batch close): no deferred items.` (not the per-Issue variant) — the expected output. | field-or-template | L1060; L1062; L1118 PC | F6-125, F6-128, F7-006 | console line | active set | none | unknown | procedure |
| FX-HYG-32 | After the empty-set message, advance per the firing-mode rules (per-Issue / end-of-batch). | ordering | L1062 | F6-129 | advance | firing mode | none | yes | procedure |
| FX-HYG-33 | **Step 2**: when the active set is non-empty, surface it as numbered markdown, one bullet per `defer-*` task with its `metadata.activity` text as the body. | relay | L1064 | F6-130 | numbered list | `metadata.activity` | TaskList | yes | procedure |
| FX-HYG-34 | The Step 2 choice set is `Fix in this session`, `File as issue tickets`, `Encode in an existing ticket body`. | choice-set | L1066-L1068 | F6-134 | - | - | AskUserQuestion | yes | procedure |
| FX-HYG-35 | `Fix in this session`: re-dispatch the appropriate implementer / reviewer Agents per Section 4's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch. | choice-set | L1066 | F6-135 | Agent dispatch or ticket-body update | deferred item | Agent, bees | yes | procedure |
| FX-HYG-36 | After each Fix item is resolved, mark its `defer-*` task `completed` with `metadata.activity` updated to log the resolution path. | ordering | L1066 | F6-136 | status flip + `metadata.activity` | resolution | TaskList | yes | procedure |
| FX-HYG-37 | `File as issue tickets`: for each item invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body. | choice-set | L1067 | F6-137 | Issue ticket | deferred item | bees | yes | procedure |
| FX-HYG-38 | Rationale: the precedent for inline-Skill-tool dispatch is Section 1's URL-resolution sub-step. | rationale-only | L1067 | F6-138 | - | - | none | no | rationale |
| FX-HYG-39 | Mark each File item's `defer-*` task `completed` once `/quo-file-issue` returns successfully and the created Issue ID is captured. | ordering | L1067 | F6-139 | status flip | `/quo-file-issue` result | TaskList | yes | procedure |
| FX-HYG-40 | `Encode in an existing ticket body`: valid destinations are a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass. | choice-set | L1068 | F6-140 | ticket-body update | user mapping | bees, Agent | yes | procedure |
| FX-HYG-41 | Append a `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body. | field-or-template | L1068 | F6-141 | ticket-body section | deferred item | none | no | procedure |
| FX-HYG-42 | Run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update. | command | L1068; L1075; L1083 | F6-142 | ticket update | body-file | bees, Bash | yes | procedure |
| FX-HYG-43 | `<YYYY-MM-DD HH:MM>` is the current local date and time authored into the body-file as a string from your own clock via the `Write` tool. | invariant | L1068 | F6-143 | heading timestamp | own clock | none | yes | procedure |
| FX-HYG-44 | Do not add a `date` / `Get-Date` snippet to compute the heading timestamp. | invariant | L1068 | F6-144 | - | - | none | yes | procedure |
| FX-HYG-45 | Keep the `## Deferred from /quo-fix-issue run` stem verbatim; only append the parenthesized timestamp suffix; do not simplify to a bare heading. | invariant | L1068 | F6-145 | heading text | - | none | no | procedure |
| FX-HYG-46 | Rationale: the suffix lets multiple Encodes to the same ticket body across runs sit side-by-side with distinguishable headings. | rationale-only | L1068 | F6-146 | - | - | none | yes | rationale |
| FX-HYG-47 | Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir. | command | L1068 | F6-147 | scratch body-file | revised body | none | yes | procedure |
| FX-HYG-48 | **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode, i.e. `bees-body-<defer-N>.md`. | name-class | L1068; L1073; L1081 | F6-148 | scratch filename | triggering task name | TaskList | yes | procedure |
| FX-HYG-49 | Example: the encode triggered by `defer-3` writes `bees-body-defer-3.md`. | example | L1068; L1074; L1082 | F6-149 | - | - | none | yes | example |
| FX-HYG-50 | Rationale: reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under the active `defer-*` set, and ties the file to its TaskList progenitor. | rationale-only | L1068 | F6-150 | - | - | none | yes | rationale |
| FX-HYG-51 | Encode snippets: POSIX `mkdir -p /tmp/.quorum`, write `/tmp/.quorum/bees-body-<defer-N>.md` via `Write`, then `bees update-ticket --ids <ticket-id> --body-file <path>`; Windows `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`, write `$env:TEMP\.quorum\bees-body-<defer-N>.md` via `Write`, then the same `bees update-ticket`. | command | L1070-L1084 | F6-151, F6-152 | directory, body-file, ticket update | - | Bash, bees | yes | procedure |
| FX-HYG-52 | Mark each Encode item's `defer-*` task `completed` once the `bees update-ticket` update succeeds. | ordering | L1086 | F6-155 | status flip | bees result | TaskList, bees | yes | procedure |
| FX-HYG-53 | **Follow-up commit** runs after all Encode writes in this gate firing have landed. | ordering | L1088 | F6-156 | commit | Encode writes | git | yes | procedure |
| FX-HYG-54 | On the **fixed** path a per-Issue commit already exists (Section 7 step 2); on the **aborted** path the Issue contributes **no** per-issue commit. | definition | L1088 | F6-157 | - | invocation path | git | no | procedure |
| FX-HYG-55 | Do not rest the follow-up commit on a per-Issue commit having landed; its premise is only that `bees update-ticket --body-file` writes persist on-disk changes not swept into any prior commit. | invariant | L1088 | F6-158 | - | hive / PRD-SDD changes | git, bees | no | procedure |
| FX-HYG-56 | Rationale: unswept Encode writes would leave the working tree dirty when the skill yields (per-Issue) or advances (end-of-batch). | rationale-only | L1088 | F6-159 | - | - | git | yes | rationale |
| FX-HYG-57 | The commit stages only the resolved in-repo hive paths and the explicit `--doc-path` arguments, committed **conditionally** on there being staged changes. | invariant | L1088 | F6-160 | staged set | hive paths, `--doc-path` | git | yes | procedure |
| FX-HYG-58 | An aborted Issue with no Encode writes stages nothing and produces no commit; this is the correct outcome, not a gap. | invariant | L1088 | F6-161 | - | - | git | no | procedure |
| FX-HYG-59 | The aborted Issue's uncommitted fix-in-progress is never swept in, since it is neither a hive path nor a `--doc-path`. | invariant | L1088 | F6-162 | - | - | git | no | procedure |
| FX-HYG-60 | Produce one follow-up commit per gate firing covering all Encode writes from that firing, not one per Encode item. | invariant | L1088 | F6-163 | one commit | Encode writes | git | yes | procedure |
| FX-HYG-61 | Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (same pattern as Section 7 step 2's commit step). | command | L1088 | F6-164 | hive paths | `bees list-hives` | bees | yes | procedure |
| FX-HYG-62 | `git add` each hive path that lives inside this repo. | command | L1088 | F6-165 | staged hive paths | resolved hive paths | git | yes | procedure |
| FX-HYG-63 | Additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations. | command | L1088 | F6-166 | staged doc paths | `## Documentation Locations` | git | yes | procedure |
| FX-HYG-64 | Commit only if `git diff --cached` shows staged changes; skip the commit rather than producing an empty one. | precondition | L1088 | F6-167 | commit or skip | `git diff --cached` | git | yes | procedure |
| FX-HYG-65 | Commit subject contract: `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded`. | field-or-template | L1088 | F6-168 | commit subject | `<N>` | git | no | procedure |
| FX-HYG-66 | **`<N>` counts deferral items, not tickets** — the count of `defer-*` items routed to Encode in this firing, the same value passed as the helper's `--count`. | invariant | L1088 | F6-169 | `<N>` | Encode routing | none | yes | procedure |
| FX-HYG-67 | The follow-up-commit workflow is encapsulated in the bundled helper `hive_commit.py`; run it as a single literal Bash tool call. | command | L1090 | F6-170 | commit | `hive_commit.py` | Bash, git, bees | yes | procedure |
| FX-HYG-68 | The helper resolves Plans/Specs/Issues hive paths, `git add`s in-repo hive paths and `--doc-path` paths, commits only if staged, and prints `skipped: nothing staged` otherwise. | definition | L1090 | F6-171 | commit or `skipped: nothing staged` | hive paths, `--doc-path` | Bash, git, bees | yes | procedure |
| FX-HYG-69 | Out-of-repo hives require no git action because `bees update-ticket` already persisted their update. | definition | L1090 | F6-172 | - | hive location | bees | yes | procedure |
| FX-HYG-70 | **Do NOT blindly `git add -A`**; other agents or processes may have in-flight working-tree changes (same anti-pattern as Section 7 step 2). | invariant | L1090 | F6-173 | - | - | git | yes | procedure |
| FX-HYG-71 | `hive_commit.py` is shipped by `/quo-execute`; this skill consumes it as a *sibling* bundled script. | definition | L1092 | F6-174 | - | - | none | no | procedure |
| FX-HYG-72 | Resolve the helper path at runtime as `<this skill's base directory>/../quo-execute/scripts/hive_commit.py` (POSIX) / `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py` (Windows). | command | L1092 | F6-175, F6-178 | helper path | skill base directory | none | no | procedure |
| FX-HYG-73 | Invoke the helper with `--skill quo-fix-issue`. | command | L1094 | F6-179 | helper arg | - | Bash | no | procedure |
| FX-HYG-74 | Invoke the helper with `--count <N>`, matching the commit-subject contract's `<N>`. | command | L1094 | F6-180 | helper arg | `<N>` | Bash | yes | procedure |
| FX-HYG-75 | Pass one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`); omit entirely when none. | command | L1094 | F6-181 | helper arg | `## Documentation Locations` | Bash | yes | procedure |
| FX-HYG-76 | Invocation: POSIX `python3 "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`; Windows `python "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`. | command | L1096-L1104 | F6-182, F6-183 | commit | helper path | Bash | no | procedure |
| FX-HYG-77 | After the helper lands the commit or prints `skipped: nothing staged`, proceed to Step 3. | ordering | L1106 | F6-184 | advance | helper output | Bash | yes | procedure |
| FX-HYG-78 | The three options are mutually-non-exclusive at the active-set level: the user may pick one overall or route different items to different options. | definition | L1108 | F6-185 | - | user reply | AskUserQuestion | yes | procedure |
| FX-HYG-79 | Example per-item routing reply: "fix items 1 and 2 now, file 3 as an Issue". | example | L1108 | F6-186 | - | - | none | yes | example |
| FX-HYG-80 | Every `defer-*` task in the active set **MUST** be `completed` by the end of this gate, whatever the routing. | invariant | L1108 | F6-187 | all `defer-*` `completed` | active set | TaskList | yes | procedure |
| FX-HYG-81 | For per-item routing the user selects `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`); the orchestrator parses the reply and closes out each `defer-*` task accordingly. | gate | L1108 | F6-188 | per-item routing | free-text reply | AskUserQuestion, TaskList | yes | procedure |
| FX-HYG-82 | **Step 3**: until every `defer-*` task is `completed`, the skill cannot advance past this gate — the pre-handoff gate reads the ledger and refuses to yield control while any `defer-*` entry is `pending` or `in_progress`. | invariant | L591 TNC; L1110 | F3-277, F6-189 | block | active set | TaskList | yes | procedure |
| FX-HYG-83 | On per-Issue firing the next Issue (batch) or Section 8 (single) is blocked; on end-of-batch firing Section 8 cannot proceed to the fresh-context sweep, until the active set is empty. | invariant | L1110; L1118 PC | F6-190, F7-010 | block | firing mode | none | yes | procedure |
| FX-HYG-84 | Rationale: a deferral important enough to surface during the run is important enough to encode in a durable carrier before the run ends. | rationale-only | L1110 | F6-191 | - | - | none | yes | rationale |
| FX-HYG-85 | If chosen options fail to close a subset (e.g. `/quo-file-issue` cancelled at a gate, or `bees update-ticket` errors), surface the still-active `defer-*` tasks via `AskUserQuestion` and re-run the gate until empty. | recovery | L1110 | F6-192 | re-fired gate | failed routing results | AskUserQuestion, TaskList, bees | yes | procedure |
| FX-HYG-86 | The fresh-session-per-phase recommendation at run close-out is preserved verbatim; this gate sits before that handoff prose and does not replace it. | invariant | L1112 | F6-193 | - | - | none | yes | procedure |

---

## 31. TRACK — Compromise tracker (file, entry shape, Decision enum, Triggers A–D)

- **Purpose:** Maintain one session-scoped markdown file that appends a five-field `## Compromise <n>` entry at each of four trigger moments (Defer / Accept at a gate, ungated pick at row 6, post-completion override), so every accepted compromise stays visible and challengeable rather than silently baked into the baseline.
- **Failure it prevents:** Compromises vanishing into the new baseline (F6-009); a bare rule name giving Section 8's challenge nothing to push against (F6-078); an entry recording a deferral that cannot distinguish soft-fixed from unfixed (F6-059); a blocker deferral without a narrowing record (F6-065).
- **Env deps:** none (Write/Read tools), AskUserQuestion, Agent, bees, Bash. **TaskList-dependent: no.**
- **Rows:** 81 (procedure 74, rationale 6, example 1).
- **Literals:** `#### Session-scoped compromise tracker`; `#### Compromise-tracker append triggers`; filename `compromises-YYYYMMDD-HHMM-<short-suffix>.md` (e.g. `20260520-1714`); `## Compromise <n>`; fields `**Finding (verbatim):**`, `**Fix paths surfaced by reviewer:**` (`(a) [depth:<depth>] <description>`… / `none`), `**Decision:**`, `**Rationale:**`, `**Follow-up Issue:**` (`none`); Decision enum `User picked path (a)`/`(b)`…, `User picked Defer to follow-up Issue`, `User picked Accept the limitation`, `Orchestrator picked path (x) — highest-quality`, `User overrode auto-route after post-completion challenge (depth misjudgment)`, `User accepted under-enumeration after post-completion challenge`; **Trigger A — Defer to follow-up Issue at either gate.** / **Trigger B — Accept the limitation at the scope-bounding gate.** / **Trigger C — ungated route (the orchestrator's own path pick).** / **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).**; SR-6.7 labels `Accept the misjudgment and proceed`, `File follow-up Issue to revisit the depth decision`, `Pause to discuss`; SR-4.6 labels `Accept the under-enumeration and proceed`, `File follow-up Issue to surface the missing path`, `Pause to discuss`; SDD `#### Compromise tracker entry shape`; `<compromise-tracker-path>`.
- **Edges:** Written by ROUTE (Triggers A/B/C) and SRGATE (Trigger D); path generated by MAN at run start; read by SUM (`**Accepted compromises**`), CKPT (carrier 3), PROMPT (PM prompt path), POSTC (PHASE 1–3 via `<compromise-tracker-path>`); file conventions in SHELL.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-TRACK-1 | Maintain a **session-scoped compromise tracker**: a single markdown file accumulating one entry per accepted compromise across this run. | definition | L985 SCT | F6-007 | tracker file | - | none | yes | procedure |
| FX-TRACK-2 | An accepted compromise is a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override. | definition | L985 | F6-008 | - | gate results | none | yes | procedure |
| FX-TRACK-3 | Rationale: the tracker exists so accepted compromises stay visible and challengeable rather than baked silently into the new baseline. | rationale-only | L985 | F6-009 | - | - | none | yes | rationale |
| FX-TRACK-4 | The four append triggers (A/B/C/D) are defined under `#### Compromise-tracker append triggers`. | definition | L985 | F6-010 | - | - | none | yes | procedure |
| FX-TRACK-5 | The post-completion review in Section 8 consumes the tracker as input. | relay | L985 | F6-011 | - | tracker file | none | yes | procedure |
| FX-TRACK-6 | `#### Session-scoped compromise tracker` is the **canonical definition site** that the trigger write-instructions reference by name. | definition | L985 | F6-012 | - | - | none | yes | procedure |
| FX-TRACK-7 | Canonical tracker filename is `compromises-YYYYMMDD-HHMM-<short-suffix>.md`. | name-class | L987 | F6-014 | tracker filename | - | none | yes | procedure |
| FX-TRACK-8 | `YYYYMMDD-HHMM` is a UTC timestamp generated **once at the start of the run**. | invariant | L987 | F6-015 | timestamp component | run start | none | yes | procedure |
| FX-TRACK-9 | Example timestamp value: `20260520-1714`. | example | L987 | F6-016 | - | - | none | yes | example |
| FX-TRACK-10 | `<short-suffix>` is a short collision-resistant random string. | name-class | L987 | F6-017 | suffix component | - | none | yes | procedure |
| FX-TRACK-11 | Rationale: the timestamp prefix makes tracker files debuggably identifiable across multiple runs accumulated in `<tempdir>/.quorum/`. | rationale-only | L987 | F6-018 | - | - | none | yes | rationale |
| FX-TRACK-12 | Each accepted compromise appends one `## Compromise <n>` section to the tracker. | field-or-template | L1001 | F6-023 | tracker entry | - | none | yes | procedure |
| FX-TRACK-13 | `<n>` is a **1-based counter scoped to the current run's tracker file**, NOT a globally unique identifier. | invariant | L1001 | F6-024 | entry counter | tracker file | none | yes | procedure |
| FX-TRACK-14 | The canonical entry shape is reproduced from the SDD Data models `#### Compromise tracker entry shape`. | definition | L1001 | F6-025 | - | - | none | yes | procedure |
| FX-TRACK-15 | Field `**Finding (verbatim):**` carries `<severity tag> <fix-path enumeration with depth tags> <description>`. | field-or-template | L1006; L1016 | F6-026 | entry field | reviewer finding | none | yes | procedure |
| FX-TRACK-16 | Field `**Fix paths surfaced by reviewer:**` lists `(a) [depth:<depth>] <description>`, `(b) [depth:<depth>] <description>`, … lines. | field-or-template | L1007-L1010; L1016 | F6-027 | entry field | fix-path enumeration | none | yes | procedure |
| FX-TRACK-17 | Field `**Decision:**` holds exactly one value from the Decision enum. | field-or-template | L1011; L1016 | F6-028 | entry field | gate result | none | yes | procedure |
| FX-TRACK-18 | Decision enum value: `User picked path (a)`, `User picked path (b)`, … (one per enumerated letter). | field-or-template | L1011 | F6-029 | Decision value | - | none | yes | procedure |
| FX-TRACK-19 | Decision enum value: `User picked Defer to follow-up Issue`. | field-or-template | L1011 | F6-030 | Decision value | - | none | yes | procedure |
| FX-TRACK-20 | Decision enum value: `User picked Accept the limitation`. | field-or-template | L1011 | F6-031 | Decision value | - | none | yes | procedure |
| FX-TRACK-21 | Decision enum value: `Orchestrator picked path (x) — highest-quality`. | field-or-template | L1011 | F6-032 | Decision value | - | none | yes | procedure |
| FX-TRACK-22 | Decision enum value: `User overrode auto-route after post-completion challenge (depth misjudgment)`. | field-or-template | L1011 | F6-033 | Decision value | - | none | yes | procedure |
| FX-TRACK-23 | Decision enum value: `User accepted under-enumeration after post-completion challenge`. | field-or-template | L1011 | F6-034 | Decision value | - | none | yes | procedure |
| FX-TRACK-24 | Field `**Rationale:**` holds the user's stated reason if surfaced via `AskUserQuestion`, or on an ungated pick the one-line reason that path was preferred. | field-or-template | L1012; L1016 | F6-035 | entry field | AskUserQuestion result or orchestrator reason | none | yes | procedure |
| FX-TRACK-25 | On a `Defer to follow-up Issue` entry, `Rationale` also names which remaining enumerated path shipped as the soft fix, or that none did. | field-or-template | L1012; L1016 | F6-036 | Rationale content | soft-fix dispatch | none | yes | procedure |
| FX-TRACK-26 | On a blocker deferral, `Rationale` carries the narrowing record in place of the soft-fix letter. | field-or-template | L1012; L1016 | F6-037 | Rationale content | narrowing | none | yes | procedure |
| FX-TRACK-27 | Field `**Follow-up Issue:**` holds the ticket ID if filed via `/quo-file-issue`, else `none`. | field-or-template | L1013; L1016 | F6-038 | entry field | `/quo-file-issue` result | none | yes | procedure |
| FX-TRACK-28 | The entry has exactly five fields: `Finding (verbatim)`, `Fix paths surfaced by reviewer`, `Decision`, `Rationale`, `Follow-up Issue`. | invariant | L1016 | F6-039 | - | - | none | yes | procedure |
| FX-TRACK-29 | The `Decision` enum carries **two** post-completion-override values: the SR-6.7 depth-misjudgment override and the SR-4.6 under-enumeration analog override. | definition | L1016 | F6-040 | - | - | none | yes | procedure |
| FX-TRACK-30 | Rationale: two override values exist because Trigger D is the single owner of all post-completion-override writes regardless of which kind fired. | rationale-only | L1016 | F6-041 | - | - | none | yes | rationale |
| FX-TRACK-31 | The tracker persists across orchestrator-yield events within a single run because it is a file-system artifact. | definition | L1018 | F6-042 | - | tracker file | none | yes | procedure |
| FX-TRACK-32 | Generate a fresh `YYYYMMDD-HHMM` timestamp + `<short-suffix>` at the **start of each run**. | invariant | L1018 | F6-043 | new tracker filename | run start | none | yes | procedure |
| FX-TRACK-33 | Previous-run tracker files are **NEVER appended to**; a new run always writes its own new file. | invariant | L1018 | F6-044 | - | prior tracker files | none | yes | procedure |
| FX-TRACK-34 | Four moments append a tracker entry: Triggers A–C fire from ODR's gates / ungated dispatch; Trigger D from Section 8's post-completion review. | definition | L1022 CAT | F6-046 | - | - | none | yes | procedure |
| FX-TRACK-35 | Each trigger anchors to its gate by name; the write fires from the branch named in the trigger. | invariant | L1022 | F6-047 | - | - | none | yes | procedure |
| FX-TRACK-36 | **Trigger A** fires at the scope-bounding gate (part (c)) when the user picks `Defer to follow-up Issue`; the write fires from that gate's `Defer to follow-up Issue` branch. | gate | L1024 | F6-048, F6-060 | tracker entry | AskUserQuestion result | AskUserQuestion | yes | procedure |
| FX-TRACK-37 | Append the Trigger A entry **IMMEDIATELY AFTER** `/quo-file-issue` returns successfully with the new Issue ID and **BEFORE** continuing with the soft-fix dispatch. | ordering | L1024 | F6-049 | tracker entry | `/quo-file-issue` result | none | yes | procedure |
| FX-TRACK-38 | Capture the follow-up Issue ID in the entry's `Follow-up Issue` field. | field-or-template | L1024 | F6-050 | `Follow-up Issue` | `/quo-file-issue` result | none | yes | procedure |
| FX-TRACK-39 | Set `Decision: User picked Defer to follow-up Issue`. | field-or-template | L1024 | F6-051 | `Decision` | - | none | yes | procedure |
| FX-TRACK-40 | Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all. | field-or-template | L1024 | F6-052 | field value | reviewer finding | none | yes | procedure |
| FX-TRACK-41 | The no-path case is reachable at the routing-decision gate, whose `Defer` choice is offered whatever the path count. | definition | L1024 | F6-053 | - | - | none | yes | procedure |
| FX-TRACK-42 | **Name in `Rationale` which remaining enumerated path shipped as the soft fix** by its letter, or that **none did**. | field-or-template | L1024 | F6-054 | `Rationale` | soft-fix dispatch | none | yes | procedure |
| FX-TRACK-43 | "None did" applies in the single-path case at the scope-bounding gate and to any deferral at the routing-decision gate. | definition | L1024 | F6-055 | - | - | none | yes | procedure |
| FX-TRACK-44 | The routing-decision gate's `Defer` bullet ships nothing against the finding regardless of how many paths the reviewer enumerated. | definition | L1024 | F6-056 | - | - | none | yes | procedure |
| FX-TRACK-45 | **On a `blocker` deferral the narrowing takes that slot**: record what was scoped down and why the blocker no longer describes what remains. | field-or-template | L1024 | F6-057 | `Rationale` | narrowing | none | yes | procedure |
| FX-TRACK-46 | A blocker's Defer branch ships a narrowing rather than one of the reviewer's other paths. | definition | L1024 | F6-058 | - | - | none | yes | procedure |
| FX-TRACK-47 | Rationale: the deferral and what shipped in its place are one decision; an entry recording only the deferral cannot distinguish soft-fixed from unfixed. | rationale-only | L1024 | F6-059 | - | - | none | yes | rationale |
| FX-TRACK-48 | **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger** on the same terms and entry shape; that gate offers `Defer` to any finding, and to a `blocker` when part (c)'s two Defer conditions hold. | gate | L1024 | F6-061, F6-062 | tracker entry | AskUserQuestion result | AskUserQuestion | yes | procedure |
| FX-TRACK-49 | **On a `blocker`-severity finding the Trigger A branch is reachable only as Defer-with-narrowing, at either gate** (part (c)'s severity rule, applied by part (d) on its own terms); its entry must carry the narrowing record. | precondition | L666 ODR (c); L1024 | F4-095, F6-063 | tracker entry (A) | finding severity | none | yes | procedure |
| FX-TRACK-50 | A blocker deferral entry MUST carry a **narrowing record** in `Rationale` (what was narrowed out and why the blocker no longer describes anything that ships); `User picked Defer to follow-up Issue` describes a `blocker` only when `Rationale` carries it; a blocker deferral without a narrowing record is read by every downstream consumer as a contract violation. | invariant | L678 ODR (d); L1024 | F4-123, F6-064, F6-065 | `Rationale` | narrowing | none | yes | procedure |
| FX-TRACK-51 | **Trigger B** fires at the scope-bounding gate's `Accept the limitation` branch when the user picks `Accept the limitation`. | gate | L1026 | F6-066 | tracker entry | AskUserQuestion result | AskUserQuestion | yes | procedure |
| FX-TRACK-52 | Append the Trigger B entry **IMMEDIATELY AFTER** the `AskUserQuestion` returns and **BEFORE** the orchestrator continues without a fix. | ordering | L1026 | F6-067 | tracker entry | AskUserQuestion result | AskUserQuestion | yes | procedure |
| FX-TRACK-53 | Set `Decision: User picked Accept the limitation` and `Follow-up Issue: none` on a Trigger B entry. | field-or-template | L1026 | F6-068, F6-069 | `Decision`, `Follow-up Issue` | - | none | yes | procedure |
| FX-TRACK-54 | Trigger B is **Unreachable for a `blocker`-severity finding** unconditionally; the gate's severity rule withholds the branch because accepting a blocker ships it; no tracker entry can record an accepted blocker (`User picked Accept the limitation` can never describe one). | precondition | L666 ODR (c); L1026 | F4-094, F6-070 | - | finding severity | none | yes | procedure |
| FX-TRACK-55 | **Trigger C** has **no gate**; the write is wired into the dispatch step itself. | invariant | L1028 | F6-071 | - | - | none | yes | procedure |
| FX-TRACK-56 | Trigger C fires at the **MOMENT of implementer dispatch** for any finding part (a) routed by **row 6** (ungated dispatch of the Step 1 orchestrator-picked path); row 6 appends this entry. | gate | L644 ODR (a); L1028 | F4-042, F6-072 | tracker entry | routing table row 6 | Agent | yes | procedure |
| FX-TRACK-57 | Append the Trigger C entry in the **SAME LOGICAL BLOCK as that dispatch**, not a separate post-gate block. | ordering | L1028 | F6-073 | tracker entry | dispatch | Agent | yes | procedure |
| FX-TRACK-58 | **One carve-out:** a finding whose only fix path is `trivial-tweak` appends nothing. | precondition | L1028 | F6-074 | - | fix-path depth tags | none | yes | procedure |
| FX-TRACK-59 | A pick among two or more paths always appends, even when every path is shallow. | invariant | L1028 | F6-075 | tracker entry | fix-path count | none | yes | procedure |
| FX-TRACK-60 | Set `Decision: Orchestrator picked path (x) — highest-quality`, where `(x)` is the chosen path's letter. | field-or-template | L1028 | F6-076 | `Decision` | chosen path | none | yes | procedure |
| FX-TRACK-61 | Set `Rationale:` to **the orchestrator's own one-line reason for preferring that path over the others** (why it is the smallest internally-consistent complete change), not merely the rule name. | field-or-template | L1028 | F6-077 | `Rationale` | orchestrator reasoning | none | yes | procedure |
| FX-TRACK-62 | Rationale: a bare rule name gives Section 8's challenge nothing to push against. | rationale-only | L1028 | F6-078 | - | - | none | yes | rationale |
| FX-TRACK-63 | Set `Follow-up Issue: none` on a Trigger C entry. | field-or-template | L1028 | F6-079 | `Follow-up Issue` | - | none | yes | procedure |
| FX-TRACK-64 | **Row 6 is this trigger's only firing site.** | invariant | L1030 | F6-080 | - | - | none | yes | procedure |
| FX-TRACK-65 | A `blocker` routed to the scope-bounding gate is user-picked, not an ungated route; write no Trigger C entry for it. | precondition | L1030 | F6-081 | - | finding severity | none | yes | procedure |
| FX-TRACK-66 | **Trigger D** is the single owner of all post-completion-override tracker writes, fired from Section 8's post-completion review; the SR gates' `Accept` steps FIRE this write — they do not author it. | invariant | L1032; L1276; L1280 PC | F6-082, F7-172, F7-180 | tracker entry or in-place update | Section 8 gate results | none | yes | procedure |
| FX-TRACK-67 | Trigger D covers **both** the SR-6.7 ungated-route recovery gate AND the SR-4.6 under-enumeration analog recovery gate. | definition | L1032 | F6-083 | - | - | none | yes | procedure |
| FX-TRACK-68 | Trigger D choice labels are byte-identical to the recovery-gate choices so they line up. | invariant | L1032 | F6-084 | - | - | none | yes | procedure |
| FX-TRACK-69 | SR-6.7 `Accept the misjudgment and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the post-completion flow continues, with `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` and `Rationale:` = the post-completion reviewer's challenge text. | choice-set | L1035; L1276 PC | F6-085, F6-086, F6-087, F7-171 | tracker entry | AskUserQuestion result; reviewer challenge text | AskUserQuestion | yes | procedure |
| FX-TRACK-70 | SR-6.7 `File follow-up Issue to revisit the depth decision` → **NO new entry is appended**; the **ORIGINAL Trigger C entry**'s `Follow-up Issue` field is **UPDATED in place** to the new Issue ID. | choice-set | L1036; L1275 PC | F6-088, F6-089, F7-170 | in-place update of `Follow-up Issue` | Trigger C entry, `/quo-file-issue` result | none | yes | procedure |
| FX-TRACK-71 | Rationale: an originating Trigger C entry always exists to amend because the depth misjudgment concerns a path routed without a gate. | rationale-only | L1036 | F6-090 | - | - | none | yes | rationale |
| FX-TRACK-72 | SR-6.7 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks `Accept` / `File` again (no write fires until a subsequent `Accept` / `File`). | choice-set | L1037; L1277 PC | F6-091, F7-174 | - | subsequent pick | AskUserQuestion | yes | procedure |
| FX-TRACK-73 | SR-4.6 `Accept the under-enumeration and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the flow continues, with `Decision: User accepted under-enumeration after post-completion challenge` and `Rationale:` = the reviewer's under-enumeration challenge text. | choice-set | L1039; L1280 PC | F6-092, F6-093, F6-094, F7-179 | tracker entry | AskUserQuestion result; reviewer challenge text | AskUserQuestion | yes | procedure |
| FX-TRACK-74 | SR-4.6 `File follow-up Issue to surface the missing path` → file the follow-up Issue and capture its ID. | choice-set | L1040 | F6-095 | Issue ticket | `/quo-file-issue` result | bees | yes | procedure |
| FX-TRACK-75 | On SR-4.6 File with **no original Trigger C entry to amend**, append a **new** entry with the under-enumeration `Decision` value and the new Issue ID in `Follow-up Issue`; if the under-enumeration relates to an existing ungated-route finding with a Trigger C entry, **UPDATE that entry's `Follow-up Issue` in place** instead. | recovery | L1040; L1279 PC | F6-096, F6-097, F7-178 | tracker entry or in-place update | Trigger C entry; Issue ID | none | yes | procedure |
| FX-TRACK-76 | SR-4.6 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again. | choice-set | L1041 | F6-098 | - | subsequent pick | AskUserQuestion | yes | procedure |
| FX-TRACK-77 | **Pass the tracker path, not its contents** — the PM prompt's `<compromise-tracker-path>` and the Section 8 reviewer's `<compromise-tracker-path>` carry this run's tracker path (the same value); the dispatched Agent reads the file itself via its own `Read` tool. | invariant | L719 `### 5.`; L1126 PC step 2 | F5-022, F5-023, F7-028, F7-029 | `<compromise-tracker-path>` | tracker path | Agent | unknown | procedure |
| FX-TRACK-78 | Write the tracker under `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows) — see FX-SHELL-1 for the shared convention. | invariant | L987 | F6-013 | tracker location | scratch-file convention | none | yes | procedure |
| FX-TRACK-79 | Create the `.quorum` directory if absent (POSIX `mkdir -p /tmp/.quorum`; Windows `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`), then write/append `/tmp/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` / `$env:TEMP\.quorum\compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` via `Write`. | command | L987-L999 | F6-019, F6-021, F6-022 | directory; tracker file | - | Bash | yes | procedure |
| FX-TRACK-80 | Author and append the tracker file via the `Write` tool, never a shell redirect. | command | L987 | F6-020 | tracker content | - | none | yes | procedure |
| FX-TRACK-81 | Never delete the tracker file; do NOT instruct any `rm` / `Remove-Item`. | invariant | L1018 | F6-045 | - | scratch-file convention | none | yes | procedure |

---

## 32. POSTC — Post-completion review (Section 8 scope, skeleton, disposition, postcomp lanes, commit)

- **Purpose:** After the last Issue, dispatch one fresh `general-purpose` reviewer with a self-contained six-PHASE prompt over `git diff <pre-session-sha>..HEAD` and the issue bodies (challenging tracked compromises first, discrete defects last), synthesize its findings, gate Fix / File / Skip, run follow-up lanes under `*-postcomp-<n>` names, and commit.
- **Failure it prevents:** The team-lead's accumulated framing biasing the review toward "did the phases run?" rather than "is this good?" (F7-015); lane-scoped review skills missing cross-lane defects (F7-012); accepted compromises rubber-stamped (F7-041); a dropped tracker hand-off going unnoticed (F7-040); mis-routing a follow-up-lane abort through the Issue-level close-out (F7-127).
- **Env deps:** Agent, git, Bash, bees, TaskList, AskUserQuestion. **TaskList-dependent: yes** (postcomp lane tasks, self-tracking close-out, disposition gate).
- **Rows:** 100 (procedure 93, rationale 6, example 1). Section 8's manifest read / `HEAD~N` fallback is homed in MAN (FX-MAN-20/21/42/44), the end-of-batch deferral-hygiene firing in HYG (FX-HYG-25..28, 31, 83), postcomp names in TASK (FX-TASK-22..31), the postcomp Engineer-dispatch precondition in ENGPRE (FX-ENGPRE-17..20), delegate mode in ROLES (FX-ROLES-25).
- **Literals:** `### 8. Post-Completion Review`; **Anti-pattern callout — read before acting.** / **Anti-pattern callout, second.**; `subagent_type=general-purpose`, `run_in_background=true`; `<pre-session-sha>`, `<compromise-tracker-path>`, `<issue-id-1> <issue-id-2> ...`; `git diff <pre-session-sha>..HEAD`; `bees show-ticket --ids <id>`; prompt opener "You are an independent reviewer for a quorum fix that was just shipped."; `PHASE 1 — Consume the compromise tracker (passed as a FILE PATH).` … `PHASE 6 — Discrete-defect sweep (the final phase).`; finding tags `[compromise-challenge]` / `[design]` / `[defect]`; `file:line`; `"no issues found"`; `Post-completion review: no issues found`; gate question `Post-completion review found [N] issues. How would you like to handle them?`; options **Fix in this session**, **File as issue tickets**, **Skip**; preamble `⚠️ The post-completion reviewer **challenged** [N] compromise(s) …`; `## Design question`; **Orchestrator self-tracking close-out (mandatory before yielding).**; **Close out the `aborted-*-postcomp-<n>` markers with the rest.**; mechanism definition list (state, configuration surface, persisted/wire field, background task, exception/error type, metric/log/trace attribute, name/identifier class, gate, retry/fallback path).
- **Edges:** Consumes MAN (`Pre-session SHA`, validation), TRACK (path; PHASE 1–3), HYG (end-of-batch firing first), ROLES (delegate mode), TASK (postcomp names), ENGPRE (postcomp variant), MOVE/UNEXP (postcomp variants re-titled here), ARG (`/quo-file-issue`); Produces `[compromise-challenge]` findings for SRGATE, the commit and clean state GH reads; EFF notes its session-effort inheritance.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-POSTC-1 | Section heading `### 8. Post-Completion Review` names this section. | definition | L1114 PC | F7-001 | - | - | none | unknown | procedure |
| FX-POSTC-2 | After all issues are fixed, run a final fresh-context generalist sweep across all changes made during this quo-fix-issue session. | ordering | L1116 | F7-002 | sweep dispatch | all session changes | Agent | unknown | procedure |
| FX-POSTC-3 | In batch mode the sweep runs after the final issue in the batch; in single mode after the one issue. | ordering | L1116 | F7-003 | - | run mode | none | no | procedure |
| FX-POSTC-4 | Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at the post-completion stage. | invariant | L1120 **Anti-pattern callout — read before acting.** | F7-011 | - | - | none | unknown | procedure |
| FX-POSTC-5 | Rationale: those skills are parallel lanes of an in-flight review with lane-specific scope (source / user-facing docs / test files), so none runs the cross-lane sweep. | rationale-only | L1120 | F7-012 | - | - | none | unknown | rationale |
| FX-POSTC-6 | Spawn a fresh general-purpose agent with a self-contained prompt instead of invoking the lane review skills. | command | L1120 | F7-013 | Agent dispatch | - | Agent | unknown | procedure |
| FX-POSTC-7 | The team-lead must NOT do the post-completion review directly. | invariant | L1122 **Anti-pattern callout, second.** | F7-014 | - | - | none | unknown | procedure |
| FX-POSTC-8 | Rationale: the team-lead's accumulated framing prompts, agent reports, and reviewer verdicts bias it toward "did the four phases get done correctly?" rather than "is this good?". | rationale-only | L1122 | F7-015 | - | - | none | unknown | rationale |
| FX-POSTC-9 | The fresh agent gets the diff and the issue body and nothing else. | invariant | L1122 | F7-016 | - | diff; issue body | Agent | unknown | procedure |
| FX-POSTC-10 | Step 1 also collects the issue ID list as `<issue-id-1> <issue-id-2> ...` (one ID in single-issue mode; the full session list in batch mode). | field-or-template | L1124 step 1 | F7-025 | issue ID list | fixed Issue list | none | no | procedure |
| FX-POSTC-11 | Step 2: spawn the fresh reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. | command | L1126 step 2 | F7-026 | reviewer dispatch | - | Agent | unknown | procedure |
| FX-POSTC-12 | The reviewer prompt must be self-contained because the agent sees nothing else from this session. | invariant | L1126 | F7-027 | - | - | Agent | unknown | procedure |
| FX-POSTC-13 | Substitute `<pre-session-sha>`, `<compromise-tracker-path>`, and the issue ID list into the skeleton before sending. | command | L1126 | F7-030 | reviewer prompt | substitutions | Agent | unknown | procedure |
| FX-POSTC-14 | Reviewer prompt opens: "You are an independent reviewer for a quorum fix that was just shipped." | field-or-template | L1129 skeleton | F7-031 | - | - | none | unknown | procedure |
| FX-POSTC-15 | Reviewer scope: review the diff `git diff <pre-session-sha>..HEAD`, computing it itself via git. | command | L1131-L1132 | F7-032 | diff | `<pre-session-sha>` | git, Bash | unknown | procedure |
| FX-POSTC-16 | Reviewer reads each issue body via `bees show-ticket --ids <id>` for the listed Issue IDs. | command | L1132-L1134 | F7-033 | - | issue ID list | bees, Bash | no | procedure |
| FX-POSTC-17 | Reviewer gives a fresh-eyes review with no context of how the work was done. | invariant | L1135-L1136 | F7-034 | - | - | none | unknown | procedure |
| FX-POSTC-18 | Reviewer performs the phases IN ORDER; Phases 1–5 lead with challenging accepted compromises; the discrete-defect sweep is the FINAL phase, not the first. | ordering | L1138-L1140 | F7-035 | - | - | none | unknown | procedure |
| FX-POSTC-19 | PHASE 1: consume the compromise tracker, passed as a FILE PATH at `<compromise-tracker-path>`, reading it via the Read tool. | command | L1142-L1148 PHASE 1 | F7-036 | - | tracker file | none | unknown | procedure |
| FX-POSTC-20 | The tracker records every compromise the run accepted: deferred-to-Issue findings, accepted limitations, ungated orchestrator path picks, post-completion overrides. | definition | L1143-L1145 | F7-037 | - | - | none | unknown | procedure |
| FX-POSTC-21 | Each `## Compromise <n>` entry carries: Finding (verbatim), Fix paths surfaced by reviewer (each with a `[depth:<...>]` tag), Decision, Rationale, Follow-up Issue. | definition | L1148-L1150 | F7-038 | - | tracker entry | none | unknown | procedure |
| FX-POSTC-22 | If the tracker file is MISSING or unreadable, the reviewer does NOT abort — it PROCEEDS with the remaining phases. | recovery | L1150-L1152 | F7-039 | - | tracker read result | none | unknown | procedure |
| FX-POSTC-23 | On a missing tracker, the reviewer flags it explicitly in its output so the dropped hand-off is visible rather than silent. | recovery | L1151-L1153 | F7-040 | finding (missing tracker) | tracker read result | none | unknown | procedure |
| FX-POSTC-24 | PHASE 2: challenge each tracked compromise on its merits; push back when the chosen path is not defensible; do not rubber-stamp a compromise because it was accepted. | command | L1155-L1157 PHASE 2 | F7-041 | findings | tracker entries | none | unknown | procedure |
| FX-POSTC-25 | PHASE 2 includes the deep-asked-but-cheap-shipped check: flag any mismatch between what the tracker records as asked/chosen and what the diff actually shipped. | command | L1157-L1161 | F7-042 | finding | tracker Decision; diff | none | unknown | procedure |
| FX-POSTC-26 | A tracker entry whose `Finding (verbatim)` carries the `blocker` severity tag and whose `Decision` is `User picked Accept the limitation` is a contract violation — a blocker can never be accepted. | invariant | L1161-L1164 | F7-043 | finding | tracker fields | none | unknown | procedure |
| FX-POSTC-27 | An entry whose `Decision` is `User picked Defer to follow-up Issue` and whose `Rationale` carries **no narrowing record** is a contract violation — a blocker may be deferred only paired with narrowing. | invariant | L1164-L1168 | F7-044 | finding | tracker fields | none | unknown | procedure |
| FX-POSTC-28 | A narrowing record is: what was narrowed out of the change, and why the blocker no longer describes anything that ships. | definition | L1165-L1167 | F7-045 | - | - | none | unknown | procedure |
| FX-POSTC-29 | An entry whose narrowing record shows the narrowing **left the unit's stated defect partly unfixed** is a contract violation — narrowing may never reduce coverage of the stated defect. | invariant | L1168-L1172 | F7-046 | finding | tracker `Rationale` | none | unknown | procedure |
| FX-POSTC-30 | Emit any PHASE 2 contract violation as a `[compromise-challenge]` finding at `blocker` severity, never lower. | field-or-template | L1172-L1173 | F7-047 | `[compromise-challenge]` `blocker` finding | violation detection | none | unknown | procedure |
| FX-POSTC-31 | PHASE 3: for every entry whose Decision is `Orchestrator picked path (<letter>) — highest-quality`, run the ungated-pick plausibility check on TWO axes. | command | L1175-L1179 PHASE 3 | F7-048 | findings | tracker `Decision` | none | unknown | procedure |
| FX-POSTC-32 | Match the ungated-pick Decision on the surrounding wording, not a literal letter, since the writing step substitutes the chosen path's own letter. | invariant | L1177-L1179 | F7-049 | - | tracker `Decision` | none | unknown | procedure |
| FX-POSTC-33 | Axis (i): evaluate whether the depth judgment was plausible, or whether the chosen path's true depth is `re-architect`. | command | L1179-L1180 | F7-050 | finding | tracker entry; diff | none | unknown | procedure |
| FX-POSTC-34 | Axis (ii): evaluate whether the chosen path introduced a mechanism the unit's approved design did not enumerate and, if so, whether it should have been deferred or put to the user. | command | L1180-L1187 | F7-051 | finding | tracker entry; diff; approved design | none | unknown | procedure |
| FX-POSTC-35 | "Mechanism" means: new state, configuration surface (flag, environment variable, setting), persisted or wire field, background task, exception or error type, metric / log / trace attribute, name or identifier class, gate, or retry / fallback path. | definition | L1181-L1185 | F7-052 | - | - | none | unknown | procedure |
| FX-POSTC-36 | Ask the two-axis question of every ungated-pick entry; emit a `[compromise-challenge]` finding on either axis. | command | L1187-L1188 | F7-053 | `[compromise-challenge]` finding | axis evaluations | none | unknown | procedure |
| FX-POSTC-37 | Axis (ii) is required, not optional: an ungated pick is an orchestrator judgment no gate reviewed, and PHASE 3 is the only place it gets challenged. | invariant | L1188-L1190 | F7-054 | - | - | none | unknown | procedure |
| FX-POSTC-38 | PHASE 4: for EVERY finding the in-flow reviewer surfaced (regardless of severity / depth / path-count), evaluate whether an additional plausible fix path should have been enumerated. | command | L1192-L1195 PHASE 4 | F7-055 | findings | in-flow reviewer findings | none | unknown | procedure |
| FX-POSTC-39 | On judged under-enumeration, emit a `[compromise-challenge]` finding naming the under-enumeration. | field-or-template | L1195-L1198 | F7-056 | `[compromise-challenge]` finding | judgment | none | unknown | procedure |
| FX-POSTC-40 | Under-enumeration means the reviewer surfaced fewer paths than existed, so the pick (orchestrator's or user's at a gate) was made from an incomplete menu. | definition | L1195-L1197 | F7-057 | - | - | none | unknown | procedure |
| FX-POSTC-41 | Rationale: PHASE 3 catches misjudged depth or unnoticed mechanism on a path that WAS surfaced; PHASE 4 catches a plausible path NOT surfaced at all. | rationale-only | L1198-L1201 | F7-058 | - | - | none | unknown | rationale |
| FX-POSTC-42 | PHASE 5: make a holistic solution-quality judgment beyond the logged compromises — is the shipped solution actually good, independent of any single tracked decision? | command | L1203-L1205 PHASE 5 | F7-059 | findings | diff | none | unknown | procedure |
| FX-POSTC-43 | PHASE 6 (final): discrete-defect sweep — flag code defects, prose problems, spec drift between the change and the issue, contract-key violations, cross-file inconsistencies, missing edits the issue called for. | command | L1207-L1211 PHASE 6 | F7-060 | findings | diff; issue body | none | unknown | procedure |
| FX-POSTC-44 | Do NOT allow renames of keys in CLAUDE.md `## Documentation Locations` or `## Build Commands`. | invariant | L1209-L1210 | F7-061 | finding | diff; contract keys | none | unknown | procedure |
| FX-POSTC-45 | One generalist pass covers code AND docs AND tests — do not lane-scope. | invariant | L1212 | F7-062 | - | - | none | unknown | procedure |
| FX-POSTC-46 | In skill repos (diff includes `skills/<name>/SKILL.md` or `agents/<name>.md`), treat those markdown files as skill / subagent program source code, not natural-language documentation. | invariant | L1214-L1216 | F7-063 | - | diff file paths | none | unknown | procedure |
| FX-POSTC-47 | Review skill / agent markdown with the same rigor as language-specific source: broken cross-references, drifted contracts, ambiguous prose, and CLAUDE.md design-rule violations are in scope. | command | L1216-L1219 | F7-064 | findings | skill / agent markdown | none | unknown | procedure |
| FX-POSTC-48 | Reviewer does NOT do a general repo audit; it stays focused on the diff. | invariant | L1221 | F7-065 | - | diff | none | unknown | procedure |
| FX-POSTC-49 | Reviewer does NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review`. | invariant | L1223-L1226 | F7-066 | - | - | none | unknown | procedure |
| FX-POSTC-50 | Reviewer returns findings as a numbered list. | field-or-template | L1228 | F7-067 | numbered findings list | - | none | unknown | procedure |
| FX-POSTC-51 | Tag EVERY finding with exactly one of `[compromise-challenge]` (challenge to an accepted compromise, from PHASE 2/3/4) / `[design]` (solution-quality concern) / `[defect]` (discrete defect). | field-or-template | L1228-L1231 | F7-068 | finding class tag | - | none | unknown | procedure |
| FX-POSTC-52 | Each finding also carries the severity tag: one of `blocker` / `suggestion` / `nit`. | field-or-template | L1231 | F7-069 | severity tag | - | none | unknown | procedure |
| FX-POSTC-53 | Each finding also carries the per-fix-path depth tag and the enumerated fix paths from the in-flight emission contract. | field-or-template | L1232-L1233 | F7-070 | depth tag; fix paths | in-flight emission contract | none | unknown | procedure |
| FX-POSTC-54 | The depth tag is informative here: the post-completion sweep is the final pre-merge gate, so any finding it emits is a gate candidate regardless of depth. | invariant | L1233-L1235 | F7-071 | - | - | none | unknown | procedure |
| FX-POSTC-55 | Preserve the `file:line` + severity shape — the new tags are additive to it. | field-or-template | L1235-L1236 | F7-072 | finding shape | - | none | unknown | procedure |
| FX-POSTC-56 | If clean, the reviewer returns exactly "no issues found". | field-or-template | L1236-L1237 | F7-073 | clean verdict string | - | none | unknown | procedure |
| FX-POSTC-57 | Wait for the reviewer agent's report before proceeding. | ordering | L1240 step 2 | F7-074 | - | Agent result | Agent | unknown | procedure |
| FX-POSTC-58 | Step 3: synthesize findings before presenting — compare the fresh reviewer's findings against the in-flight per-issue code/test/doc reviewer verdicts still in context. | command | L1242 step 3 | F7-075 | synthesis notes | reviewer report; in-flight verdicts | none | unknown | procedure |
| FX-POSTC-59 | Flag any disagreements explicitly, e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." | command | L1242 | F7-076 | synthesis notes | - | none | unknown | procedure |
| FX-POSTC-60 | Present the synthesized findings (fresh reviewer's list plus synthesis notes) to the user. | relay | L1242 | F7-077 | user-facing findings | synthesis | none | unknown | procedure |
| FX-POSTC-61 | When the reviewer returns one or more `[compromise-challenge]` findings, render a one-or-two-sentence prose preamble BEFORE the findings list naming this explicitly. | relay | L1244 **Compromise-challenge preamble** | F7-078 | preamble | `[compromise-challenge]` findings | none | unknown | procedure |
| FX-POSTC-62 | Mirror the verdict-keyed preamble pattern in `/quo-plan` Step 5e and this skill's Section 3 Analyst-verdict preamble — a short prose lead with the `⚠️`-led divergent-framing convention when a challenge is present. | field-or-template | L1244 | F7-079 | preamble | - | none | unknown | procedure |
| FX-POSTC-63 | Example preamble: "⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below." | example | L1244 | F7-080 | - | - | none | unknown | example |
| FX-POSTC-64 | When there are no `[compromise-challenge]` findings, no preamble is needed — present the findings directly. | precondition | L1244 | F7-081 | - | findings count | none | unknown | procedure |
| FX-POSTC-65 | Before yielding the turn at step 4 / step 5 (to deliver "no issues found" or to fire `AskUserQuestion`), mark every orchestrator self-tracking TaskList task `completed` and clear it from the active set. | ordering | L1246 **Orchestrator self-tracking close-out** | F7-083 | TaskList flips | self-tracking tasks | TaskList | unknown | procedure |
| FX-POSTC-66 | The yield is the close-out trigger: when the orchestrator stops responding, the TaskList must show no `in_progress` entries left over from synthesis steps. | invariant | L1246 | F7-084 | - | TaskList state | TaskList | unknown | procedure |
| FX-POSTC-67 | Rationale: this self-tracking close-out is the analog of step 6's per-finding close-out (scoped to `<role>-postcomp-<n>` Agents and `file-issue-postcomp-<n>` entries); the two scopes are complementary, not overlapping. | rationale-only | L1246 | F7-085 | - | - | TaskList | unknown | rationale |
| FX-POSTC-68 | Step 4: if the agent returned "no issues found", report "Post-completion review: no issues found" and exit. | relay | L1248 step 4 | F7-087 | console message | reviewer verdict | none | unknown | procedure |
| FX-POSTC-69 | Step 5: if the agent flagged issues, fire the user-facing gate through the two-step contract (FX-GATE-1/2/3), the gate task naming the post-completion findings gate. | gate | L1250 step 5 | F7-088 (also in FX-GATE-1) | gate firing | reviewer findings | TaskList, AskUserQuestion | unknown | procedure |
| FX-POSTC-70 | Gate question text: "Post-completion review found [N] issues. How would you like to handle them?" | field-or-template | L1251 | F7-093 | question text | findings count | AskUserQuestion | unknown | procedure |
| FX-POSTC-71 | Gate options are exactly: **Fix in this session** (address the issues now), **File as issue tickets** (create issue tickets via `/quo-file-issue` for each issue), **Skip** (acknowledge and move on without action). | choice-set | L1252-L1255 | F7-094 | - | - | AskUserQuestion | unknown | procedure |
| FX-POSTC-72 | When the reviewer returned a PHASE 2 contract-violation `[compromise-challenge]` finding (a `blocker`), the step 5 question text recommends **`Fix in this session`**. | relay | L1257; L1272 | F7-095, F7-150 | question text recommendation | PHASE 2 findings | AskUserQuestion | unknown | procedure |
| FX-POSTC-73 | Step 6 **Fix in this session**: dispatch fresh ephemeral Agents per Section 4's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. | command | L1260 step 6 | F7-096 | Agent dispatches | findings | Agent | unknown | procedure |
| FX-POSTC-74 | When each follow-up Agent returns, confirm any bees ticket transitions the worker committed to (as Section 4's reconcile-on-completion step does). | command | L1260 | F7-106 | - | Agent result | bees | unknown | procedure |
| FX-POSTC-75 | Then mark the corresponding `<role>-postcomp-<n>` task `completed` and clear it from the active set (mirroring Section 7 step 3's per-issue close-out). | ordering | L1260 | F7-107 | TaskList flip | Agent result | TaskList | unknown | procedure |
| FX-POSTC-76 | An `engineer-postcomp-<n>` return carrying a `## Design question` is NOT a completion of that finding — its diff is partial by construction. | invariant | L1260 | F7-108 | - | Engineer return | Agent | unknown | procedure |
| FX-POSTC-77 | `agents/engineer.md`'s stop-rather-than-invent rule is mode-independent. | definition | L1260 | F7-109 | - | - | none | unknown | rationale |
| FX-POSTC-78 | On a `## Design question` return: mark that task `completed` (Agent exited), dispatch no further lane for that finding, and route the finding to the **File as issue tickets** branch. | recovery | L1260 | F7-110 | TaskList flip; routing | Engineer return | TaskList | unknown | procedure |
| FX-POSTC-79 | The follow-up Issue for a design-question finding carries the finding, the Engineer's question verbatim, and its what-landed / what-did-not list. | field-or-template | L1260 | F7-111 | follow-up Issue body | Engineer return | bees | unknown | procedure |
| FX-POSTC-80 | Note in the final report which of the design-question finding's edits are already on disk. | relay | L1260 | F7-112 | final report note | Engineer return | none | unknown | procedure |
| FX-POSTC-81 | There is no Analyst in Section 8, so Section 4's Revise route does not apply to a post-completion design question. | invariant | L1260 | F7-113 | - | - | none | no | procedure |
| FX-POSTC-82 | Section 4's movement-report rung carries over: a `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` return that reports it *stopped* on detected source movement is not a completion. | invariant | L1260 | F7-115 | - | writer return | Agent | unknown | procedure |
| FX-POSTC-83 | On a movement stop: mark the writer's own `<role>-postcomp-<n>` task `completed` (Agent exited) and open an `aborted-<role>-postcomp-<n>` task `pending` in its place, its `metadata.activity` the writer's "how far I got" report. | recovery | L1260 | F7-116, F7-118 | `aborted-<role>-postcomp-<n>` task | writer return | TaskList | unknown | procedure |
| FX-POSTC-84 | Re-dispatch the aborted lane once the source has settled, per the rung's three mover branches, under `<role>-postcomp-<n>-r<k>`; mark the `aborted-*` task `completed` when the re-dispatch delivers. | recovery | L1260 | F7-119, F7-120 | dispatch; TaskList flip | source settled | Agent, TaskList | unknown | procedure |
| FX-POSTC-85 | While an `aborted-<role>-postcomp-<n>` task is `pending`, do **not** treat the Section 8 pass as finished and do **not** commit — the pending marker is the owed redelivery. | precondition | L1260 | F7-121 | - | TaskList state | TaskList, git | unknown | procedure |
| FX-POSTC-86 | The rung's unexplained-movement gate applies here; read its abort option's *whole body*, not just its title. | gate | L1262 | F7-122 | gate firing | - | AskUserQuestion | no | procedure |
| FX-POSTC-87 | The gate's third option is read as *abort this follow-up lane* rather than *abort this Issue* — the Issue is already `done` and its per-issue commit landed. | invariant | L1262 | F7-123 | - | - | AskUserQuestion | no | procedure |
| FX-POSTC-88 | The abort option's body routing through `#### Aborted-Issue close-out` does NOT apply on this branch; the abort closes out via **this branch's OWN prefix sweep** instead. | recovery | L1262 | F7-124, F7-125 | prefix sweep | - | TaskList | no | procedure |
| FX-POSTC-89 | `#### Aborted-Issue close-out` is scoped to an Issue abandoned *before* its fix landed. | definition | L1262 | F7-126 | - | - | none | no | procedure |
| FX-POSTC-90 | Rationale: running `#### Aborted-Issue close-out` from Section 8 would re-fire Section 7.5 for a closed deferral gate, run the checkpoint's aborted path against a `done` committed Issue, and in batch mode stop the run with a fresh-session resume command. | rationale-only | L1262 | F7-127 | - | - | none | no | rationale |
| FX-POSTC-91 | After this branch's sweep, **continue Section 8's own flow**: remaining findings' dispositions, then step 7's compromise-challenge recovery gates, then Section 9. | ordering | L1262 | F7-128 | - | - | none | no | procedure |
| FX-POSTC-92 | Once all follow-up lanes have delivered, commit. | command | L1262 | F7-129 | git commit | all `<role>-postcomp-*` lanes delivered | git | unknown | procedure |
| FX-POSTC-93 | Close out `aborted-*-postcomp-<n>` markers with the rest: the per-Agent close-out sentence covers them too; sweep by name **prefix** so both a marker and any `-r<k>` re-dispatch are closed alongside their first round, not left active when Section 8 exits. | ordering | L1264 | F7-130, F7-131 | TaskList flips | TaskList state | TaskList | unknown | procedure |
| FX-POSTC-94 | This prefix sweep is also the close-out the unexplained-movement gate's abort option routes to on this branch. | definition | L1264 | F7-132 | - | - | TaskList | no | procedure |
| FX-POSTC-95 | When one finding needs both a source change and a test/doc change, dispatch the **Engineer** (`engineer-postcomp-<n>`) first and let it return; only then dispatch the `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` lane whose input that source change determines. | ordering | L1268 | F7-138, F7-139 | Agent dispatches | finding; Engineer result | Agent | unknown | procedure |
| FX-POSTC-96 | Two findings independent of each other may be worked concurrently; the within-finding ordering and the cross-finding precondition are the only constraints. | invariant | L1268 | F7-140 | - | - | Agent | unknown | procedure |
| FX-POSTC-97 | Step 6 **File as issue tickets**: for each issue, invoke `/quo-file-issue` with the issue description. | command | L1269 | F7-141 | Issue tickets | findings | bees | unknown | procedure |
| FX-POSTC-98 | Report the created ticket IDs to the user. | relay | L1269 | F7-142 | user-facing report | created ticket IDs | none | unknown | procedure |
| FX-POSTC-99 | Mark `file-issue-postcomp-<n>` entries `completed` and clear them from the active set before exiting — same close-out discipline as "Fix in this session". | ordering | L1269 | F7-144 | TaskList flips | - | TaskList | unknown | procedure |
| FX-POSTC-100 | Step 6 **Skip**: Done. | command | L1270 | F7-145 | - | - | none | unknown | procedure |

---

## 33. SRGATE — Compromise-challenge recovery gates (SR-6.7 / SR-4.6)

- **Purpose:** For each PHASE 3 (ungated-pick) or PHASE 4 (under-enumeration) `[compromise-challenge]` finding, fire its own three-choice recovery gate — per finding, in emission order, before or alongside the step-6 disposition — whose labels byte-match Trigger D so the tracker write lines up.
- **Failure it prevents:** not stated directly (implicit: an orchestrator judgment no gate reviewed passing unchallenged into the baseline; inventing a fourth gate for the PHASE 2 violation — F7-153).
- **Env deps:** AskUserQuestion, TaskList, bees. **TaskList-dependent: yes.**
- **Rows:** 21 (procedure 21).
- **Literals:** **Compromise-challenge recovery gates.**; **SR-6.7 ungated-route recovery gate.** choices `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, `Pause to discuss`; **SR-4.6 under-enumeration recovery gate.** choices `File follow-up Issue to surface the missing path`, `Accept the under-enumeration and proceed`, `Pause to discuss`; **The pinned strings read generically across both axes:**.
- **Edges:** Consumes POSTC's `[compromise-challenge]` findings and tracker `Decision` values; fires TRACK Trigger D (FX-TRACK-66..76 own the write semantics); uses GATE; files via `/quo-file-issue` (ARG precedent); the PHASE 2 violation is dispositioned by POSTC's step 5 gate alone.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-SRGATE-1 | Step 7: a `[compromise-challenge]` finding from PHASE 3 or PHASE 4 is not handled by step 6's Fix / File / Skip alone — each triggers its own recovery gate. | gate | L1272 **Compromise-challenge recovery gates.** | F7-146 | recovery gate firing | PHASE 3 / 4 findings | AskUserQuestion, TaskList | unknown | procedure |
| FX-SRGATE-2 | Each recovery gate fires **before or alongside** the step-6 disposition for that finding. | ordering | L1272 | F7-147 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-3 | The PHASE 2 accepted-`blocker`-or-unnarrowed-deferral contract violation has NO recovery gate, by design. | invariant | L1272 | F7-148 | - | PHASE 2 findings | none | unknown | procedure |
| FX-SRGATE-4 | A PHASE 2 contract-violation finding is dispositioned by **step 5's Fix / File / Skip gate alone**; step 6 executes whatever that gate returns. | gate | L1272 | F7-149 | - | step 5 gate answer | AskUserQuestion | unknown | procedure |
| FX-SRGATE-5 | The step 5 gate is **aggregate** — one answer covers every finding — so the `Fix in this session` recommendation is stated once for the whole finding set. | invariant | L1272 | F7-151 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-6 | A `Skip` at the step 5 gate leaves the contract violation recorded in the reviewer's output and the compromise tracker and nowhere else. | definition | L1272 | F7-152 | - | step 5 answer | none | unknown | procedure |
| FX-SRGATE-7 | Do not invent a fourth gate for the PHASE 2 contract violation. | invariant | L1272 | F7-153 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-8 | Each recovery gate **fires per challenged finding** (three such findings ⇒ three gate firings), NOT aggregated into one gate. | invariant | L1272 | F7-160 | gate firings | `[compromise-challenge]` findings | AskUserQuestion | unknown | procedure |
| FX-SRGATE-9 | Recovery gate **firing order equals the reviewer's emission order** in its numbered list. | ordering | L1272 | F7-161 | - | reviewer numbered list | AskUserQuestion | unknown | procedure |
| FX-SRGATE-10 | **SR-6.7 ungated-route recovery gate** fires when a `[compromise-challenge]` finding flags an ungated orchestrator path pick (Decision `Orchestrator picked path (x) — highest-quality`) on either PHASE 3 axis. | gate | L1274 | F7-163 | three-choice AskUserQuestion | PHASE 3 finding; tracker `Decision` | AskUserQuestion, TaskList | unknown | procedure |
| FX-SRGATE-11 | SR-6.7 triggers cover both axes: a misjudged depth, or a chosen path that introduced a mechanism and should have routed to the scope-bounding gate. | definition | L1274 | F7-164 | - | PHASE 3 finding | none | unknown | procedure |
| FX-SRGATE-12 | SR-6.7 choice labels are byte-matched against Section 7.5's Trigger D branches; do not reword them. | invariant | L1274 | F7-165 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-13 | The pinned strings `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` read generically across both axes, naming **the routing misjudgment** — mechanism axis included. | invariant | L1274 | F7-166 | - | - | none | unknown | procedure |
| FX-SRGATE-14 | Read "depth decision" / "misjudgment" generically rather than concluding the mechanism axis has no gate. | invariant | L1274 | F7-167 | - | - | none | unknown | procedure |
| FX-SRGATE-15 | SR-6.7 choices are exactly: `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, `Pause to discuss`. | choice-set | L1274-L1277 | F7-168 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-16 | SR-6.7 `File follow-up Issue to revisit the depth decision`: dispatch `/quo-file-issue` via the Skill tool capturing the depth-mismatch finding plus the original compromise-tracker entry as context (tracker update per FX-TRACK-70). | command | L1275 | F7-169 | Issue ticket | finding; tracker entry | bees | unknown | procedure |
| FX-SRGATE-17 | SR-6.7 `Pause to discuss`: stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. | recovery | L1277 | F7-173 | prose discussion | - | none | unknown | procedure |
| FX-SRGATE-18 | **SR-4.6 under-enumeration recovery gate** fires when a `[compromise-challenge]` finding flags under-enumeration (the fix-path-enumeration plausibility check), with the **same three-choice gate shape** and relabeled choices. | gate | L1278 | F7-175 | three-choice AskUserQuestion | PHASE 4 finding | AskUserQuestion, TaskList | unknown | procedure |
| FX-SRGATE-19 | SR-4.6 choices are exactly: `File follow-up Issue to surface the missing path`, `Accept the under-enumeration and proceed`, `Pause to discuss`. | choice-set | L1278-L1281 | F7-176 | - | - | AskUserQuestion | unknown | procedure |
| FX-SRGATE-20 | SR-4.6 `File follow-up Issue to surface the missing path`: dispatch `/quo-file-issue` via the Skill tool capturing the under-enumeration finding as context (tracker update per FX-TRACK-75); `Pause to discuss` stops the flow and surfaces discussion with no tracker write until a subsequent `Accept` / `File`. | command | L1279; L1281 | F7-177, F7-181 | Issue ticket; prose discussion | finding | bees | unknown | procedure |
| FX-SRGATE-21 | The SR-4.6 gate's per-branch behavior mirrors SR-6.7 exactly (file follow-up Issue / append explicit-override entry via Trigger D / pause-and-resume) and likewise fires per challenged finding (non-aggregated) in reviewer emission order. | invariant | L1283 | F7-182, F7-183 | - | reviewer numbered list | AskUserQuestion | unknown | procedure |

---

## 34. GH — GitHub close recommendation (Section 9)

- **Purpose:** Before yielding, emit a copy-paste block of `gh issue close` commands — one per fixed Issue whose `reference_materials` carries a `github-issue` resolver — keyed on the per-issue commit SHA; never run them.
- **Failure it prevents:** Baking a `gh` auth assumption into the workflow (F7-188); positional mis-pairing of SHAs when Section 8 landed extra commits (F7-208).
- **Env deps:** bees, git, Bash, none. **TaskList-dependent: no.**
- **Rows:** 33 (procedure 29, rationale 4).
- **Literals:** `### 9. Recommend upstream GitHub close commands`; `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."`; header `Upstream GitHub Issues to consider closing:`; `reference_materials` `{value, resolver}`; resolver `github-issue` (not `linear-issue` / `url`); URL shape `https://github.com/<owner>/<repo>/issues/<n>`; `bees show-ticket --ids <issue-id>`; `git rev-parse --short <full-sha>`; `git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD`; **Track at commit time (preferred).** / **Re-derive post-hoc.**
- **Edges:** Consumes CLOSE's commit subject contract and `git commit` SHA, MAN's `<pre-session-sha>` (via POSTC step 1), VAL/ANA/PROMPT's `reference_materials` reads, POSTC completion; the fixed-issue list excludes VAL skips, ANA cancels, ARG soft-fails.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-GH-1 | Section heading `### 9. Recommend upstream GitHub close commands` names this section. | definition | L1285 | F7-184 | - | - | none | no | procedure |
| FX-GH-2 | After Section 8 either reports clean (step 4) or the step 6 per-finding follow-ups close out, and **before yielding the turn**, emit the GitHub close recommendation block. | ordering | L1287 | F7-185 | recommendation block | Section 8 outcome | none | no | procedure |
| FX-GH-3 | The block is a copy-paste-ready set of `gh issue close ...` commands, one for each fixed Issue whose `reference_materials` carries a `github-issue` resolver. | field-or-template | L1287 | F7-186 | recommendation block | `reference_materials` | none | no | procedure |
| FX-GH-4 | **Pure recommendation — the skill NEVER runs `gh issue close` itself.** | invariant | L1287 | F7-187 | - | - | none | no | procedure |
| FX-GH-5 | Rationale: no `gh` auth assumption is baked into the workflow; the user copies and runs the command(s) from an authenticated machine. | rationale-only | L1287 | F7-188 | - | - | none | no | rationale |
| FX-GH-6 | The recommendation is scoped to the `github-issue` resolver only; do **not** generalize it to `linear-issue` or `url` resolvers. | invariant | L1289 | F7-189 | - | resolver type | none | no | procedure |
| FX-GH-7 | Rationale: `linear-issue` close needs Linear's own CLI/API (not bundled); the generic `url` resolver has no close concept; adding either is a separate Issue. | rationale-only | L1289 | F7-190 | - | - | none | no | rationale |
| FX-GH-8 | Step 1: **Iterate the run's fixed-issue list** — IDs this run actually marked `done` via Section 7 (single-issue: one ID; list / `all` mode: full session list in fixed order). | command | L1293 | F7-191 | fixed-issue iteration | Section 7 done-flips | none | no | procedure |
| FX-GH-9 | Issues skipped (Section 2's blocked-issue handling), cancelled at Section 3's user-approval gate, or never reached (e.g., `bees show-ticket` validation soft-failed in Section 1) are NOT in the fixed-issue list. | invariant | L1293 | F7-192 | - | run history | none | no | procedure |
| FX-GH-10 | Step 2: for each fixed Issue, read its `reference_materials`, re-using the value captured in Section 2 / 3 / 4's dispatch reads if still in context. | command | L1295 | F7-193 | - | `reference_materials` | none | no | procedure |
| FX-GH-11 | If `reference_materials` is not in context, re-read via `bees show-ticket --ids <issue-id>` (identical POSIX and PowerShell forms). | command | L1295-L1305 | F7-194 | - | issue ID | bees, Bash | no | procedure |
| FX-GH-12 | `reference_materials` is a JSON array of `{value, resolver}` objects. | definition | L1307 | F7-195 | - | - | none | no | procedure |
| FX-GH-13 | An empty / null `reference_materials` means the Issue was filed via the in-conversation default capture mode (no upstream URL) and contributes nothing to the block. | precondition | L1307 | F7-196 | - | `reference_materials` | none | no | procedure |
| FX-GH-14 | Step 3: for each entry whose `resolver == "github-issue"`, parse `value` against `https://github.com/<owner>/<repo>/issues/<n>` to extract `<owner>`, `<repo>`, `<n>`. | command | L1309 | F7-197 | `<owner>`, `<repo>`, `<n>` | entry `value` | none | no | procedure |
| FX-GH-15 | HTTP and HTTPS are both acceptable; trailing slashes / fragments / query strings are ignored when matching. | definition | L1309 | F7-198 | - | URL | none | no | procedure |
| FX-GH-16 | If the URL does not match the canonical shape, skip the entry — a mismatch indicates a malformed entry, since `/quo-file-issue`'s `github-issue` resolver writes only canonical Issue URLs. | recovery | L1309 | F7-199 | - | URL match result | none | no | procedure |
| FX-GH-17 | Step 4: **Capture the per-issue commit SHA** from Section 7 step 2.4's commit step. | command | L1311 | F7-200 | per-issue SHA | Section 7 commit | git | no | procedure |
| FX-GH-18 | Preferred path — **Track at commit time**: record the commit SHA the moment Section 7 step 2.4's `git commit` returns, keyed by issue ID, and re-use it here. | command | L1312 | F7-201 | SHA keyed by issue ID | `git commit` result | git | no | procedure |
| FX-GH-19 | If the captured SHA is the full 40-char form, abbreviate it (e.g., `git rev-parse --short <full-sha>`) before emitting in step 5. | command | L1312 | F7-202 | short SHA | full SHA | git, Bash | no | procedure |
| FX-GH-20 | Fallback — **Re-derive post-hoc**: resolve the commit per Issue by `--grep`-filtering session commits against the per-issue commit-message contract (subject ends with literal `(<issue-id>)`). | recovery | L1313 | F7-203 | per-issue SHA | commit subjects | git | no | procedure |
| FX-GH-21 | Run once per fixed Issue: `git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (identical POSIX and PowerShell forms). | command | L1313-L1323 | F7-204 | abbreviated SHA | `<issue-id>`; `<pre-session-sha>` | git, Bash | no | procedure |
| FX-GH-22 | Substitute the literal Issue ID (e.g., `b.abc`) for `<issue-id>` and the session-start SHA captured at Section 8 step 1 for `<pre-session-sha>`. | command | L1325 | F7-205 | - | issue ID; `<pre-session-sha>` | none | no | procedure |
| FX-GH-23 | Rationale: `-F` (`--fixed-strings`) makes the grep pattern literal so `.` and `(` `)` match as themselves, removing regex-vs-literal ambiguity. | rationale-only | L1325 | F7-206 | - | - | none | no | rationale |
| FX-GH-24 | Each `git log` invocation returns at most one match — the per-issue commit — and `%h` emits the abbreviated SHA so no follow-up `git rev-parse --short` is needed. | definition | L1325 | F7-207 | - | - | git | no | procedure |
| FX-GH-25 | Rationale: scoping each lookup by the parenthesized `(<issue-id>)` token is load-bearing: it filters out extra commits Section 8 step 6's "Fix in this session" branch may have landed, avoiding positional mis-pairing. | rationale-only | L1325 | F7-208 | - | - | none | no | rationale |
| FX-GH-26 | Step 5: **Append a bullet** of the form `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` to the block, one bullet per matching `reference_materials` entry. | field-or-template | L1327 | F7-209 | recommendation bullet | `<n>`, `<owner>`, `<repo>`, `<sha>` | none | no | procedure |
| FX-GH-27 | Step 6: **Suppress the entire recommendation block** if zero bullets were collected. | precondition | L1329 | F7-210 | - | bullet count | none | no | procedure |
| FX-GH-28 | Equivalently, emit nothing when every fixed Issue's `reference_materials` is null/empty or carries only non-`github-issue` resolvers. | definition | L1329 | F7-211 | - | `reference_materials` | none | no | procedure |
| FX-GH-29 | Output shape: header line `Upstream GitHub Issues to consider closing:`, blank line, then `- gh issue close <n1> --repo <owner1>/<repo1> -c "Fixed in <commit-sha-1>."` bullets. | field-or-template | L1331-L1338 | F7-212 | recommendation block | bullets | none | no | procedure |
| FX-GH-30 | Bullet ordering matches the run's fixed-issue iteration order (single-issue: one bullet; list / `all` mode: fixed-list order). | ordering | L1340 | F7-213 | - | fixed-issue list | none | no | procedure |
| FX-GH-31 | When a single fixed Issue carries multiple `github-issue` entries in `reference_materials`, emit one bullet per matching entry, in array order. | ordering | L1340 | F7-214 | bullets | `reference_materials` array | none | no | procedure |
| FX-GH-32 | The recommendation block is informational console output — NOT an `AskUserQuestion` gate; the user is not asked to confirm. | invariant | L1342 | F7-215 | console output | - | none | no | procedure |
| FX-GH-33 | After emitting the block, the orchestrator yields. | ordering | L1342 | F7-216 | - | - | none | no | procedure |

---

## 35. SHELL — Shell etiquette / scratch-file convention

- **Purpose:** The cross-cutting file and helper conventions every scratch artifact obeys: write under `<tempdir>/.quorum/`, create the directory if absent, author via the `Write` tool, never delete, and resolve sibling-skill helpers from the invocation header's base directory with `..` traversal.
- **Failure it prevents:** Permission-prompt churn and lost debugging artifacts from mid-run cleanup (F6-154); helper paths hardcoded per machine.
- **Env deps:** Bash, none. **TaskList-dependent: no.**
- **Rows:** 5 (procedure 4, rationale 1). The per-artifact instances (manifest FX-MAN-6, tracker FX-TRACK-78..81, Encode body-file FX-HYG-47/51, opt-out marker FX-GUARD-27) are homed with their artifacts and cite these rows.
- **Literals:** `<tempdir>/.quorum/` (`/tmp/.quorum/`, `%TEMP%\.quorum`); `mkdir -p /tmp/.quorum`; `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null`; `Write` tool; `rm` / `Remove-Item` (forbidden); `Base directory for this skill: /Users/.../quo-fix-issue`; `..` traversal; `scoped_marker_resolver.py`, `hive_commit.py`, `context_gauge.py`.
- **Edges:** Consumed by MAN, TRACK, HYG (Encode), GUARD (opt-out marker), SCOPED / CLOSE / GUARD (sibling-helper resolution).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| FX-SHELL-1 | Create the `.quorum` directory if absent before writing any scratch artifact: POSIX `mkdir -p /tmp/.quorum`; PowerShell `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`. | command | L189-L201 `#### Write the run-state manifest` (and per-artifact sites L987-L999, L1070-L1084) | F1-149 | `.quorum` directory | tempdir | Bash | yes | procedure |
| FX-SHELL-2 | Author scratch artifacts via the `Write` tool — no shell redirect. | command | L189-L201 | F1-150 | file | - | none | yes | procedure |
| FX-SHELL-3 | Never delete a scratch artifact; do NOT instruct any `rm` / `Remove-Item` after the bees / helper command exits (scratch-file convention forbids cleanup) — the manifest and the Encode temp file alike. | invariant | L212; L1086 | F1-165, F6-153 | - | scratch-file convention | none | yes | procedure |
| FX-SHELL-4 | Rationale: files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. | rationale-only | L1086 | F6-154 | - | - | none | yes | rationale |
| FX-SHELL-5 | Sibling-helper resolution: the base directory is shown in the skill invocation header (e.g. `Base directory for this skill: /Users/.../quo-fix-issue`); use the `..` traversal pattern to reach the sibling skill's `scripts/` — the same discipline for `scoped_marker_resolver.py`, `hive_commit.py`, and `context_gauge.py`. | invariant | L602 `#### Scoped-marker PM dispatch wiring`; L881 CWG; L1092 §7.5 | F3-290, F6-176, F6-177 | helper path | skill invocation header | none | yes | procedure |

---

## Totals

Figures below were computed by a script over the tables in this file (every `| FX-` row parsed; every `F<n>-<nnn>` token in **Sources** matched against the seven extracts' ID ranges F1-001…188, F2-001…128, F3-001…294, F4-001…157, F5-001…258, F6-001…193, F7-001…216).

**Rows before / after dedupe:** 1,434 raw → **1,177** deduped (−257, 17.9%). Every one of the 1,434 raw IDs is homed in at least one deduped row (0 missing, 0 unknown IDs). Six raw IDs are homed in two rows because the source sentence was compound and its halves belong to different mechanisms: F1-041 (FX-EFF-23 / FX-GATE-10), F2-074 (FX-DIR-1 / FX-DIR-2), F3-145 (FX-UNEXP-12 / FX-ABORT-31), F4-062 (FX-GATE-1 / FX-ROUTE-59), F4-111 (FX-GATE-1 / FX-ROUTE-95), F7-088 (FX-GATE-1 / FX-POSTC-69). Distinct raw IDs = 1,434; source citations = 1,440.

**By Kind (deduped rows):** invariant 277 · definition 181 · command 136 · field-or-template 125 · ordering 113 · rationale-only 91 · recovery 61 · choice-set 57 · precondition 39 · gate 36 · relay 27 · name-class 20 · example 10 · failure-narrative 4.

**By Class:** procedure 1,059 (90.0%) · rationale 98 (8.3%) · example 15 (1.3%) · failure-narrative 5 (0.4%).

**TaskList-dependent rows** (Env contains `TaskList`): **194 of 1,177 = 16.5%.** By mechanism: TASK 29 · RECOV 19 · HYG 19 · POSTC 13 · ENGPRE 11 · ABORT 11 · MOVE 10 · DQ 10 · GATE 10 · ROUTE 8 · LEDGER 8 · DEFC 7 · UNEXP 6 · EFF 5 · ANA 5 · CKPT 5 · ARG 4 · LOOP 4 · CLOSE 3 · SRGATE 3 · PROMPT 2 · MAN 1 · GUARD 1. Mechanisms whose *machinery* is TaskList (would not function without it, per their header flag): TASK, GATE, LEDGER, DEFC, ENGPRE, MOVE, UNEXP, DQ, RECOV, HYG, ABORT, CKPT (carrier 4), REVIEW/ANA/LOOP/ROUTE/EFF/GUARD/SRGATE/POSTC/CLOSE (gate tasks or lane tracking only). Mechanisms with no TaskList dependency at all: PRE, ISO, MAN, VAL, DIR, ROLES, SCOPED, DOCV, SUM, TRACK, GH, SHELL.

**Mechanisms ranked by row count:**

| Rank | Mechanism | Rows | Rank | Mechanism | Rows |
|---|---|---|---|---|---|
| 1 | ROUTE | 127 | 19 | SUM | 26 |
| 2 | POSTC | 100 | 20 | DQ | 25 |
| 3 | HYG | 86 | 21 | EFF | 23 |
| 4 | TRACK | 81 | 22 | SRGATE | 21 |
| 5 | ANA | 61 | 23 | ENGPRE | 20 |
| 6 | ARG | 56 | 24 | DEFC | 19 |
| 7 | PROMPT | 46 | 25 | PRE | 17 |
| 8 | MAN | 45 | 26 | ISO | 15 |
| 9 | GUARD | 39 | 27 | UNEXP | 14 |
| 10 | RECOV | 37 | 28 | GATE | 12 |
| 11 | LOOP | 35 | 29 | LEDGER | 12 |
| 12 | GH | 33 | 30 | VAL | 11 |
| 13 | CKPT | 32 | 31 | REVIEW | 10 |
| 14 | TASK | 31 | 32 | DIR | 8 |
| 15 | ABORT | 31 | 33 | DOCV | 7 |
| 16 | MOVE | 29 | 34 | SCOPED | 5 |
| 17 | ROLES | 29 | 35 | SHELL | 5 |
| 18 | CLOSE | 29 | | | |

The five largest mechanisms (ROUTE, POSTC, HYG, TRACK, ANA) hold 455 rows = 38.7% of the inventory; the routing-and-compromise cluster (ROUTE + TRACK + SRGATE + the compromise-challenge half of POSTC) alone is ~260 rows.



## Literals index

Every verbatim name, label, heading, file name, command, and enum value the skill's prose depends on (the string contract), alphabetical by first significant character (markdown markers and leading `#`/`/`/`<` ignored), with the owning mechanism (secondary users in parentheses). Pipe characters inside literals are escaped.

| Literal | Owner |
|---|---|
| `#### Aborted-Issue close-out` | ABORT |
| `aborted-<role>-<issue-id>` / `aborted-test-writer-<issue-id>` / `aborted-doc-writer-<issue-id>` | MOVE (TASK, CLOSE, ABORT) |
| `aborted-<role>-postcomp-<n>` | TASK (POSTC) |
| **Abort this Issue** | UNEXP |
| `Accept the limitation` | ROUTE (TRACK) |
| `Accept the misjudgment and proceed` | SRGATE (TRACK) |
| `Accept the under-enumeration and proceed` | SRGATE (TRACK) |
| `**Accepted compromises**` | SUM |
| `action` = `created` / `reused-existing` | ARG |
| `addressed-now-in-this-Issue` | DEFC (HYG, PROMPT) |
| `addressed-now-in-this-Task` | LEDGER (HYG) |
| `agents/analyst.md`, `agents/engineer.md`, `agents/test-writer.md`, `agents/doc-writer.md`, `agents/pm.md`, `agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md` | ROLES |
| `/agents` | PRE |
| `Agent type '<name>' not found` | PRE |
| `Agent(name=...)` (forbidden) | PROMPT |
| `Agent(subagent_type=<role>, run_in_background=true, prompt=<...>)` | PROMPT |
| `Agent(subagent_type=analyst, run_in_background=true, prompt=…)` | ANA |
| `Agent(subagent_type="code-reviewer" \| "test-reviewer" \| "doc-reviewer" \| "pm", run_in_background=true)` | REVIEW (TASK) |
| `all` | ARG |
| `### Alternatives considered` | ANA (DIR, PROMPT) |
| `analyst` (subagent type) | PRE |
| `analyst-<issue-id>`, `analyst-<issue-id>-rev<n>` (`analyst-veq`, `analyst-veq-rev1`) | TASK (ANA, RECOV, ENGPRE, DQ) |
| `Analyst verdict: <…>` | ANA |
| `#### Anti-pattern: do not classify the body upfront` | ANA |
| `##### Anti-pattern: no clock primitives` | LOOP |
| **Anti-pattern callout — read before acting.** / **Anti-pattern callout, second.** | POSTC |
| `Approve & proceed to implementation (Recommended)` | ANA |
| `Approve` / `Revise` / `Cancel` (file-issue distill gate) | ARG |
| `argument-hint "[<issue-id> \| <url> \| <id-or-url> ... \| all]"` | ARG |
| `args` = `url: <url>` | ARG |
| `## Authoritative design directive (from Section 3 Analyst pass)` | PROMPT (ROUTE) |
| `#### Authoritative design directive (carried into Section 4)` | DIR |
| **Authoritative design directive (fix mode only)** (in `agents/engineer.md`) | DIR |
| `Base directory for this skill: /Users/.../quo-fix-issue` | SHELL |
| **Batch end-of-run firing.** | HYG |
| `bees execute-freeform-query --query-yaml '<yaml>'` | LOOP |
| `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'` | ARG |
| `bees list-hives` | PRE (HYG) |
| `bees show-ticket --ids "<issue-id>"` / `bees show-ticket --ids <id1> <id2> ...` | VAL (ARG, LOOP, PROMPT, CLOSE, GH, POSTC) |
| `bees update-ticket --ids <ticket-id> --body-file <path>` | HYG |
| `bees update-ticket --status done` | CLOSE |
| `bees-body-<defer-N>.md` (`bees-body-defer-3.md`) | HYG |
| `### Blast radius` | ANA (DIR, RECOV) |
| `## Blast radius` | PROMPT |
| `blocker` / `suggestion` / `nit` | ROUTE (POSTC, TRACK) |
| `## Build Commands` | PRE (CLOSE, POSTC) |
| `Cancel` (Section 3 gate) | ANA (ABORT) |
| `Cancel` (gate (d)) | ROUTE (ABORT) |
| `Cannot start Issue. It is blocked by: [list]` | VAL |
| `Chat about this` / `Type something.` (auto-appended) | GATE (HYG) |
| `#### Check session reasoning effort` | EFF |
| `CLAUDE_CODE_SESSION_ID` | GUARD |
| `CLAUDE_EFFORT` | EFF |
| `code-reviewer-<issue-id>` (`code-reviewer-veq`, `code-reviewer-veq-r1`) | TASK (LOOP, CLOSE) |
| `#### Cold-dispatch the Analyst` | ANA |
| `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test` | PRE (CLOSE) |
| `## Compromise <n>` | TRACK (SUM, POSTC) |
| `**Compromise tracker:**` (manifest field) | MAN |
| `[compromise-challenge]` / `[design]` / `[defect]` | POSTC (SRGATE) |
| **Compromise-challenge preamble (rendered before presenting the findings).** | POSTC |
| **Compromise-challenge recovery gates.** | SRGATE |
| `#### Compromise-tracker append triggers` | TRACK |
| `<compromise-tracker-path>` | TRACK (PROMPT, POSTC) |
| `compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`20260520-1714`) | TRACK (MAN, SUM) |
| **Configure now** | GUARD |
| `#### Consume the Analyst's `### Deferred refinements` block` | DEFC |
| `context-guard-opt-out` (`<tempdir>/.quorum/context-guard-opt-out`) | GUARD |
| `context-usage-<session_id>.json`; `session_id`; `context_window.used_percentage` | GUARD |
| `context_gauge.py` (`<this skill's base directory>/../quo-setup/scripts/context_gauge.py`) | GUARD (SHELL) |
| `#### Context-window boundary guard` | GUARD |
| `count unavailable post-compaction` | SUM (ROUTE) |
| **Create a feature branch (Recommended for `all` mode and list mode)** | ISO |
| `CronCreate` | LOOP |
| `Ctrl-C` | ROUTE (ARG) |
| `**Decision:**` | TRACK |
| Decision enum: `User picked path (a)`…; `User picked Defer to follow-up Issue`; `User picked Accept the limitation`; `Orchestrator picked path (x) — highest-quality`; `User overrode auto-route after post-completion challenge (depth misjudgment)`; `User accepted under-enumeration after post-completion challenge` | TRACK (POSTC, SRGATE) |
| `defer-<short-suffix>` (`defer-1`, `defer-2`, `defer-N`) | LEDGER (DEFC, HYG, TASK) |
| `defer-to-existing-ticket-body: <ticket-id>` / `defer-to-new-Issue` | DEFC (LEDGER, HYG) |
| `Defer to follow-up Issue` | ROUTE (TRACK) |
| `Deferral hygiene: no deferred items.` / `Deferral hygiene (batch close): no deferred items.` | HYG |
| `### Deferred refinements` | DEFC (ANA, HYG) |
| `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` | HYG |
| `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)` | PROMPT |
| `## Design question` | DQ (LOOP, POSTC) |
| `##### Dispatch prompt: quote the issue body verbatim and embed the design directive` | PROMPT |
| `## Doc divergence noted` | ROLES (DOCV) |
| `**Doc Sync**` | SUM |
| `doc-reviewer-<issue-id>` (`doc-reviewer-veq`) | TASK |
| `doc-writer-<issue-id>` (`doc-writer-veq`, `doc-writer-veq-r1`) | TASK |
| `## Documentation Locations` | PRE (ROLES, SUM, HYG, POSTC) |
| `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded` | HYG (CKPT) |
| `Encode in an existing ticket body` | HYG |
| `engineer-<issue-id>` (`engineer-veq`, `engineer-veq-r1`) | TASK |
| `engineer-postcomp-<n>` (`engineer-postcomp-1`, `engineer-postcomp-3`) | TASK (POSTC, ENGPRE) |
| **Engineer-dispatch precondition (checkable, not a promise).** | ENGPRE |
| `## Engineer's completeness evidence` | PROMPT |
| `escalate-to-user` | ANA |
| `### Feature: <title>` | ROLES |
| `file-from-url-<n>` (`file-from-url-1`) | ARG |
| `file-issue-postcomp-<n>` | TASK (POSTC) |
| `file-path` / `bees` (resolvers) | ROLES |
| `File as issue tickets` | HYG (POSTC) |
| `File follow-up Issue to revisit the depth decision` | SRGATE (TRACK) |
| `File follow-up Issue to surface the missing path` | SRGATE (TRACK) |
| **File-then-fix transition announcement.** / `Filing URL(s) as Issue(s) first, then fixing.` | ARG |
| `## Files changed` | PROMPT (RECOV, DQ) |
| `**Files Changed**` | SUM |
| `file:line` | POSTC |
| `**Finding (verbatim):**` | TRACK (SUM) |
| `Fix in this session` | HYG (POSTC) |
| `Fix issue: <title> (<issue-id>)` | CLOSE (CKPT, GH) |
| `**Fix paths surfaced by reviewer:**` (`(a) [depth:<depth>] <description>`; `none`) | TRACK (SUM) |
| `Fix properly now` | ROUTE |
| `fix-issues`, `bug-sweep` (worktree name hints); `fix/issues-<short-slug>`, `fix/<id1>-<id2>` | ISO |
| `**Follow-up Issue:**` (`none`) | TRACK (SUM) |
| **Follow the trailer literally** | REVIEW |
| `gate-<kind>-<short-suffix>` / `gate-askuserquestion-<short-suffix>` (`gate-askuserquestion-veq`, `gate-askuserquestion-1`) | TASK (GATE, all gate mechanisms) |
| `gate-*` | GATE |
| `general-purpose` | PRE (forbidden fallback); POSTC (`subagent_type=general-purpose`) |
| `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` | GH |
| `git add -A` (forbidden) | CLOSE (HYG) |
| `git add <emitted-issues-path>/<issue-id>` | CLOSE |
| `git diff --cached` | HYG |
| `git diff --name-only HEAD` | PROMPT (RECOV) |
| `git diff <pre-session-sha>..HEAD` | POSTC |
| `git hash-object` | MOVE |
| `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` | CKPT |
| `git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` | GH |
| `git rev-parse HEAD` | MAN (MOVE) |
| `git rev-parse --short <full-sha>` | GH |
| `git rev-parse --show-toplevel` | MAN |
| `git status` | CLOSE |
| `git status --porcelain` | ABORT |
| `github-issue` / `linear-issue` / `url` (resolvers) | ROLES (GH) |
| `HEAD~N` | MAN |
| `hive_commit.py` (`<this skill's base directory>/../quo-execute/scripts/hive_commit.py`) | HYG (CLOSE, SHELL) |
| `hive_commit.py resolve-hive-paths --hive issues` | CLOSE |
| `hive_commit.py --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]` | HYG |
| `How should I proceed with this design proposal?` | ANA |
| `#### Hub-and-spoke via substrate` | PROMPT |
| `## Inline invocation via the Skill tool` | ARG |
| **In-place substitution semantics.** | ARG |
| `[introduces-mechanism]` | ROUTE |
| `**Isolation strategy:**` (manifest field) | MAN |
| `**Issue**` | SUM |
| `## Issue [x] of [total] done: [issue-title]` | SUM |
| `#### Issue-boundary state-externalization checkpoint` | CKPT |
| `issue_status`, `issue_ticket_id` | ARG |
| `issues` / `specs` (`normalized_name`) | PRE |
| `**Ignored Review Feedback**` | SUM (LEDGER, HYG, PROMPT) |
| `/loop` | LOOP |
| **Let me change it first** | EFF |
| `low` < `medium` < `high` < `xhigh` < `max`; floor `medium` | EFF |
| `main` / `master` | ISO |
| `metadata.activity` | TASK (all TaskList users) |
| `missing` / `no-reading` / `stale` (`read` outputs); exit `0` / `2` | GUARD |
| `mkdir -p /tmp/.quorum` | SHELL (MAN, TRACK, HYG) |
| `/model` | EFF |
| **Movement report from a Phase B writer.** | MOVE |
| `name: quo-fix-issue` (frontmatter) | ARG |
| **Never guard me (persistent opt-out)** | GUARD |
| `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null` | SHELL (MAN, TRACK, HYG) |
| `**Next unit:**` | MAN |
| `No code issues found.` | LOOP |
| `No invariant added, removed, or weakened.` | ANA (PROMPT) |
| `No second-order effects identified.` / `None identified.` | SUM |
| `no spec drift surface to review for this Issue` | DOCV |
| `no issues found` / `Post-completion review: no issues found` | POSTC |
| `None` (Deferred refinements) | DEFC |
| `None — the recommendation leaves no policy question open.` | ANA |
| `### Options the body did not consider` | ANA (DIR, PROMPT) |
| **Orchestrator self-tracking close-out (mandatory before yielding).** | POSTC |
| `### Orchestrator discipline: routing review findings` | ROUTE |
| `open` / `done` | VAL (CLOSE, CKPT) |
| `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"` (forbidden) | ROUTE |
| `#### Parse the argument list and pick issues` | ARG |
| `Pause to discuss` | SRGATE (TRACK) |
| `pending` / `in_progress` / `completed` | TASK |
| `## Perturbations` (`None`) | MOVE (UNEXP) |
| **Per-Issue firing.** / **Fixed path** / **Aborted path** | HYG |
| `#### Per-issue cold dispatch` | PROMPT |
| `PHASE 1 — Consume the compromise tracker (passed as a FILE PATH).` … `PHASE 6 — Discrete-defect sweep (the final phase).` | POSTC |
| **Phase A — source to clean.** / **Phase B — writers once, in parallel.** / **Phase C — remaining reviewers plus PM.** | LOOP |
| `pm-<issue-id>` (`pm-veq`) | TASK |
| **PM is the exception to the conditional-spawn rules.** | REVIEW |
| `### Policy decisions this change implies` | ANA (DIR) |
| `Post-completion review found [N] issues. How would you like to handle them?` | POSTC |
| **Post-resolution working-list display.** / `Post-resolution working list:` | ARG |
| `**Pre-session SHA:**` / `<pre-session-sha>` | MAN (CKPT, POSTC, GH) |
| `[preferred]` | ROUTE |
| `printenv CLAUDE_CODE_SESSION_ID` / `Write-Output $env:CLAUDE_CODE_SESSION_ID` | GUARD |
| `printenv CLAUDE_EFFORT` / `Write-Output $env:CLAUDE_EFFORT` | EFF |
| `## Prior proposal and user feedback` | ANA (DQ) |
| `### Problem` / `### Root cause` / `### Upstream-fetch status` | ANA |
| **Proceed anyway** | EFF |
| **Proceed without the guard (this run)** | GUARD |
| `**Progress:**` (`- <issue-id>: done — commit <sha>`; `<issue-id>: aborted — no commit; Issue left open`) | MAN (CKPT) |
| `/quo-breakdown-epic`, `/quo-execute` (manifest siblings) | MAN |
| `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` | REVIEW (LOOP, PROMPT, POSTC) |
| `/quo-file-issue` | ARG (ROUTE, HYG, SRGATE, POSTC) |
| `/quo-fix-issue all`, `/quo-fix-issue <remaining-ids>` | GUARD (ABORT) |
| `/quo-setup` (`Run /quo-setup first.`) | PRE |
| `/quo-setup --configure-gauge-producer` | GUARD |
| `.quorum` / `<tempdir>/.quorum/` (`/tmp/.quorum/`, `%TEMP%\.quorum`) | SHELL (MAN, TRACK, HYG, GUARD, SUM) |
| `re-architect` / `refactor-locally` / `trivial-tweak` | ROUTE (POSTC, TRACK) |
| `Re-dispatch the Analyst with this finding` | ROUTE (DQ, ABORT) |
| **Re-dispatch the writer now** | UNEXP |
| `README.md` `## Install` | PRE |
| **Recommended default on the mechanism row.** / `(Recommended)` | ROUTE |
| `### Recommended approach` | ANA (DIR, RECOV) |
| `recommend-as-stated` / `recommend-with-refinements` / `recommend-different-approach` | ANA (DEFC) |
| `#### Reconciliation loop` | LOOP |
| `#### Recursive delegation: not supported` | PROMPT (CKPT) |
| `reference_materials` (`{value, resolver}`) | PROMPT (ANA, ROLES, GH) |
| `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | ARG |
| `**Reviews**` (`N nits applied without re-review`) | SUM (ROUTE) |
| `Revise` | ANA |
| `-r<n>` / `-rev<n>` / `-r<k>` | TASK |
| `#### Roles dispatched by the orchestrator` | ROLES |
| `run-state-quo-fix-issue-<repo-dir-name>.md` (`run-state-quo-fix-issue-widget-api.md`) | MAN |
| `# Run state — quo-fix-issue @ <repo-dir-name>` | MAN |
| `**Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>` | MAN |
| `run_in_background=true` | PROMPT (LOOP, POSTC) |
| `ScheduleWakeup` | LOOP |
| **Scenario A — Already in a worktree.** / **Scenario B — On an existing branch in the main repo.** | ISO |
| `<scoped-marker-resolver-path>` / `scoped_marker_resolver.py` (`<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py`) | SCOPED (PROMPT, SHELL) |
| `#### Scoped-marker PM dispatch wiring` | SCOPED |
| `### Second-order effects` / `**Second-order effects**` | LOOP / SUM |
| `SendMessage` (forbidden) | PROMPT |
| `#### Session-scoped compromise tracker` | TRACK |
| **Set up a worktree instead** / `/bees-worktree-add` | ISO |
| **Severity bounds the loop.** | ROUTE |
| `**Skill:** quo-fix-issue` | MAN |
| `Skip` | POSTC |
| `skipped: nothing staged` | HYG |
| `## Source paths to fingerprint` | PROMPT (MOVE, ABORT) |
| **SR-6.7 ungated-route recovery gate.** / **SR-4.6 under-enumeration recovery gate.** | SRGATE (TRACK) |
| **Step 0 — Retroactive ledger reconciliation (safety net).** … **Step 3 — Hard-stop on a non-empty active set.** | HYG |
| `stop-threshold` / `read --session-id <trimmed-session-id>` / `write-opt-out` | GUARD |
| **Stop here** | GUARD |
| `summary:` (unset) | ARG |
| `#### Surface the proposal to the user` | ANA |
| `t1=Doc` | ROLES (HYG) |
| `TaskCreate` | GATE |
| `#### TaskList as progress UI` / `##### TaskList naming convention` | TASK |
| `test -f /tmp/.quorum/context-guard-opt-out` / `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"` | GUARD |
| `test-reviewer-<issue-id>` (`test-reviewer-veq`) | TASK |
| `test-writer-<issue-id>` (`test-writer-veq`) | TASK |
| `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` (`test-writer-postcomp-2-r1`) | TASK (POSTC, ENGPRE) |
| `ticket_status` | VAL (LOOP) |
| **Trigger A — Defer to follow-up Issue at either gate.** / **Trigger B — Accept the limitation at the scope-bounding gate.** / **Trigger C — ungated route (the orchestrator's own path pick).** / **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).** | TRACK |
| **Two-step gate mechanics (parts (c) and (d)).** | GATE |
| `**Unit scope:** ordered Issue batch: …` | MAN |
| **Unexplained-movement gate.** | UNEXP |
| `up_dependencies` | VAL (ROLES, SCOPED, PROMPT) |
| `Upstream GitHub Issues to consider closing:` | GH |
| **URL token** / **ticket-ID token**; `^https?://` | ARG |
| `Use existing` | ARG |
| `#### Validate isolation strategy` | ISO |
| **Wait** | UNEXP |
| `WebFetch` | PROMPT (ROLES) |
| **What "highest-quality" means.** / **What "introduces a mechanism" means.** | ROUTE |
| `### Why` | ANA (DIR, PROMPT) |
| **Work on current branch** | ISO |
| `Write` tool (no shell redirect) | SHELL |
| `#### Write the run-state manifest` | MAN |
| `"You are an independent reviewer for a quorum fix that was just shipped."` | POSTC |
| `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**` | REVIEW |
| `"no Engineer Agent will be dispatched for this Issue while you are running"` (allowed) / `"the source tree is frozen"` (forbidden) | PROMPT |
| Section headings: `## Overview`, `## Preconditions`, `## Execution Flow`, `### 1. Determine which issues to fix`, `### 2. Validate Issue`, `### 3. Design analysis`, `### 4. Execute fix via per-issue Agent dispatch`, `### 5. Review Loop`, `### 6. Verify docs are still accurate`, `### 7. After Issue is fixed`, `### 7.5 Before handoff — deferral hygiene`, `### 8. Post-Completion Review`, `### 9. Recommend upstream GitHub close commands` | ARG / VAL / ANA / LOOP / REVIEW / DOCV / CLOSE / HYG / POSTC / GH |
| **(a) Pick the path, then route on it.** / **(b) ANTI-PATTERN — do not write this:** / **(c) Scope-bounding gate.** / **(d) Routing-decision gate.** / **(e) Backwards-compatibility shim.** / **(f) Edge-case handling.** / **(g) Re-dispatch ordering when a fix path changes source.**; rows 1–6 | ROUTE |
| `⚠️` divergent-framing preamble convention | ANA (POSTC) |



## Inconsistencies noticed

Contradictions, undefined referents, duplicate-with-difference statements, and enumeration gaps found while merging. Where two sources conflict, both rows are kept in the tables above. Numbered for citation.

1. **In-flight Issue status — contradiction.** F2-011 (FX-VAL-11) says "If not blocked, mark the Issue status to signal work has begun (if needed)". F3-054 / F3-055 (FX-CLOSE-29) say the Issue type "supports only two statuses, `open` and `done`; there is no in-flight bees status to set" and the flip happens only at close-out. Section 2's instruction has no status to set; the "(if needed)" hedge does not resolve it.
2. **Directive to writers — contradiction.** F2-070 (FX-ANA-60) carries the approved directive "into Section 4's implementer dispatch — the Engineer prompt when source code needs modification, Test Writer and Doc Writer dispatches otherwise per Section 4's conditional-dispatch rules". F3-196 (FX-PROMPT-12) says "Test Writer and Doc Writer prompts do NOT carry the design directive separately; they read the resulting diff". Also an **undefined referent**: no anchor named "conditional-dispatch rules" exists in Section 4.
3. **Single-mode Cancel — duplicate with difference.** F2-099 (in FX-ABORT-23): "in single-issue mode the run ends there". F5-252 (FX-ABORT-23): single-issue mode "proceed[s] to Section 8 over what the session did land; if no commit landed at all, say so plainly and exit". Section 3's summary of the close-out omits the Section 8 pass.
4. **Destination-label vocabulary — two spellings.** PM items use `addressed-now-in-this-Task` (F5-069, F6-110; read as "addressed-now-in-this-Issue"), Analyst bullets use `addressed-now-in-this-Issue` (F2-107, F6-112), and F3-204 tells the orchestrator to annotate a Code-Reviewer-derived `defer-*` task `addressed-now-in-this-Issue`. One label, two literal strings, three emitters.
5. **Compaction-artifact `defer-*` task — tension with the ledger rules.** F3-204 (FX-PROMPT-21) creates a `defer-*` task annotated `addressed-now-in-this-Issue`, "left `pending`", listed under `**Ignored Review Feedback**`. But F2-107 / F6-110 / F6-112 say `addressed-now-*` items are *not* added to / are skipped by the ledger, and F6-187 / F6-189 (FX-HYG-80/82) require every active `defer-*` task to be `completed` before the gate closes — so this task must be surfaced at Step 2 and routed Fix / File / Encode, none of which fits a "nothing to do" artifact.
6. **Gate-suffix uniqueness vs Issue-slug suffix.** F2-064 / F3-279 (FX-TASK-19) permit `gate-askuserquestion-veq` (Issue-slug suffix) for the Section 3 gate; F3-281 / F6-004 / F7-155 (FX-GATE-4) require `<short-suffix>` unique **per fire** within the run, and F3-150 (FX-UNEXP-14) says a re-fire creates a fresh task. A Revise → re-surface cycle re-fires the Section 3 gate for the same Issue, so the slug pattern collides with the per-fire rule unless the second fire picks a different suffix — unstated.
7. **Two-step-contract enumeration — incomplete / undefined referent.** F3-282 (FX-GATE-9) lists the gates the contract applies to as "Section 5 escalation gates, Section 1's conditional session-effort gate, Section 3's approval gate, Section 4's unexplained-movement gate, Section 7.5's deferral-hygiene gate, Section 8's post-completion findings gate". Section 5 defines no `AskUserQuestion` of its own (its gates are ODR (c)/(d), which the list does not name); the list also omits the compromise-challenge recovery gates (step 7) and the context-window guard's Step 5 gate, both of which state the contract locally.
8. **Isolation prompt outside the gate contract.** F1-087 / F1-090 (FX-ISO-6/9) fire `AskUserQuestion` with no `gate-askuserquestion-*` task, and F3-282 does not list the isolation prompt; the file-issue distill gate (F1-124) is likewise ungated on the fix-issue side. Either the isolation prompt is exempt (unstated) or it is a missing two-step instance.
9. **`HEAD~N` fallback assumption.** F7-021 / F5-165 (FX-MAN-21) bound the fallback with `HEAD~N` where N = Issues fixed, on the premise "one commit per issue per Section 7 step 2.4". F6-156..168 (Encode follow-up commits, `Encode deferral: …`) and F7-129 (Section 8 "Fix in this session" commit) both add commits, and F5-166 itself warns the Encode commit can sit on top of the per-issue one — so `HEAD~N` can under-scope the Section 8 diff whenever any Encode or postcomp commit landed.
10. **Step list omits 7.5.** F1-136 (FX-ARG-50) enumerates steps 2–9 and describes 7 as "mark Issue done + commit"; Section 7.5 (deferral hygiene), which the flow must pass through on every Issue, is absent from the list.
11. **Self-tracking task names — undefined class.** F7-082 (FX-TASK-31) has the orchestrator create ad-hoc self-tracking tasks ("Get diff scope", "Verify <id>", "Synthesize findings"); F3-287 (FX-TASK-21) enumerates every coexisting namespace and does not include them, and F3-245 (one task per Agent) does not cover non-Agent tasks — the class is used but never defined.
12. **Eight-role precondition vs sibling skill.** F1-014 requires `analyst` among the eight registered subagent types; the extractor notes quo-execute has no `analyst` (Mirror `unknown`). Not an internal contradiction, but the shared hard-fail message (`README.md '## Install'`) would list different required sets per skill.
13. **Per-fire firing count for SBL nits.** F4-015 / F5-066 (FX-SUM-5) record the nit count "on the **Reviews** line of the summary for the scope that dispatched the review"; the summary template (F5-117) has one **Reviews** line per Issue with three lane slots but a single `N nits applied without re-review` clause — how per-lane counts (Code / Test / Docs) are combined is unstated.
14. **Free-text at the deferral-hygiene gate.** F6-188 (FX-HYG-81) relies on the user choosing `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot for per-item routing, while FX-GATE-5 says gates are multi-choice only and forbids *adding* fake free-text options. Not a contradiction (the slot is auto-appended), but HYG is the one gate whose primary routing path is free text — worth a deliberate statement.
15. **Movement-report task completion.** F3-248 (FX-TASK-6) says `completed` means deliverables confirmed landed; F3-249 / F3-152 (FX-MOVE-29) carve out the movement report ("`completed` means this Agent is gone"). F3-111 marks the writer's task `completed` and F7-116 does likewise at postcomp. Consistent by carve-out, but the carve-out is stated in the TaskList section and relied on in three other places — flag for a rewrite that may relocate it.
16. **Extractor-flagged classification quirk.** F2-045 ("the consumption paragraph is the load-bearing site") is a definition-of-pointer classed `rationale` by its extractor; F5-019 and F3-070 are `definition`-Kind rows classed `rationale`. Kept as extracted; Class totals above inherit these.
17. **Duplicate-with-difference on the Engineer-dispatch prefix list.** F3-077 / F3-180 / F4-147 (FX-ENGPRE-1) agree on six prefixes; F7-134 (FX-ENGPRE-18) restates it for postcomp with two prefixes (`test-writer-postcomp-*`, `doc-writer-postcomp-*`) and F7-133 explains why. Consistent, but F4-149 says Section 4 is "authoritative for three qualifications not restated" while F7-137 restates one of them (the stranded-`pending` clause) for postcomp — the "single statement site" claim (F3-087: "stated once here") is not literally true.
18. **Ordinal drift in "Section 7 step 5".** F1-078, F1-164, F3-236, F5-144 refer to the checkpoint as "Section 7 step 5"; F5-148 says the checkpoint "is a definition, not a step in Section 7's linear flow" and step 5 merely *calls* it. Both readings appear; the anchor name is the checkpoint heading, not "step 5".


## Mirror candidates

Mechanisms carrying rows marked Mirror `yes` or `unknown`, for the cross-skill pass against `/quo-execute` (and `/quo-breakdown-epic` where the manifest lead statements are concerned). Counts are yes / unknown / no per mechanism from the script.

**Verified-shared (`yes`-dominant) — check byte-identity or deliberate divergence:**

| Mechanism | yes / unknown / no | What is shared |
|---|---|---|
| TRACK | 80 / 1 / 0 | Entire compromise-tracker contract (file name, entry shape, Decision enum, Triggers A–D, SR-6.7/SR-4.6 label byte-match). |
| ROUTE | 85 / 30 / 12 | Whole ODR section incl. the SBL paragraph (extractor verified SBL byte-identical at quo-execute L793). The 12 `no` rows are fix-issue-specific (Section 3 Analyst re-dispatch, `<issue-id>` names, `Cancel` → `#### Aborted-Issue close-out`, no-`Cancel`-at-(c)). The 30 `unknown` are the blocker-severity rules (F4-063…F4-123) — verify whether quo-execute carries the same blocker Defer-with-narrowing text. |
| HYG | 51 / 7 / 28 | Steps 0–3, Fix/File/Encode, `hive_commit.py` follow-up commit; `no` rows are the aborted-path and per-Issue-firing specifics and the `/quo-fix-issue` literals in the Encode heading / commit subject / `--skill`. |
| GUARD | 37 / 0 / 2 | Whole context-window guard except the two resume-command / aborted-path rows. |
| EFF | 23 / 0 / 0 | Whole session-effort gate (floor differs: fix-issue `medium`, breakdown-epic `high`). |
| PRE | 16 / 1 / 0 | Preconditions; the eight-role list differs (quo-execute has no `analyst`). |
| ISO | 13 / 0 / 2 | Isolation block (F1-084 says "mirror `/quo-execute`'s isolation block"). |
| CLOSE | 13 / 8 / 8 | Commit steps 2.1–2.4, `hive_commit.py resolve-hive-paths`, no-push, no-`git add -A`; `no` = Issues-hive scoping, `Fix issue:` subject, per-issue sweep names. |
| CKPT | 12 / 12 / 8 | Carriers 3–5, verify/fix/rewrite/re-read discipline, "does not clear context" statement. |
| MAN | 10 / 5 / 30 | Only the five **lead statements** (FX-MAN-3, -4, -11, -15, -23) are mirror-mandated per CLAUDE.md; the discriminator (`<repo-dir-name>`), collision cases, and field template are legitimately fix-issue-specific. |
| GATE | 9 / 3 / 0 | Two-step contract mechanics. |
| TASK | 7 / 20 / 4 | The `<role>-postcomp-<n>` / `-r<k>` post-completion naming (F7-104 says identical in quo-execute); the issue-scoped names are fix-issue-only. |
| SHELL | 5 / 0 / 0 | Scratch-file convention and sibling-helper resolution. |
| SCOPED | 1 / 2 / 2 | Helper path resolution shared; Path B vs Path A is the deliberate divergence. |
| LEDGER | 1 / 11 / 0 | `defer-*` naming shared; destination-label vocabulary (`addressed-now-in-this-Task` vs `-Issue`) needs a cross-skill check. |

**Unverified (`unknown`-dominant) — the extractors did not compare these against quo-execute; likely shared in substance with per-skill scope wording (Issue vs Subtask/Task):**

| Mechanism | yes / unknown / no | Note |
|---|---|---|
| POSTC | 0 / 89 / 11 | Section 8 skeleton (PHASE 1–6, tags, Fix/File/Skip gate, postcomp lanes) is almost certainly shared; `no` rows are the "no Analyst in Section 8" and Aborted-Issue-close-out exclusions. |
| LOOP | 0 / 32 / 3 | Reconciliation-loop skeleton and clock-primitive anti-pattern. |
| PROMPT | 0 / 30 / 16 | Cold-dispatch shape, completeness-evidence relay, fingerprint list; `no` rows are the Section 3 directive embedding and `## Blast radius` relay (fix-mode only). |
| MOVE | 0 / 27 / 2 | Movement-report rung; F3-105 says fix mode is the *strict* branch, so expect deliberate divergence from execute's softer branch. |
| ROLES | 0 / 24 / 5 | Role definitions and anti-softening examples. |
| SUM | 0 / 24 / 2 | Summary template — heading/field names differ per skill (`Issue` vs `Epic`/`Task`). |
| SRGATE | 0 / 21 / 0 | Recovery gates; labels are pinned to TRACK, so expect identical. |
| ENGPRE | 0 / 15 / 5 | Precondition prefix list (execute has no `analyst-*` prefix). |
| UNEXP | 0 / 13 / 1 | Unexplained-movement gate. |
| VAL | 0 / 11 / 0 | Validate-unit step (`open`/`done` vs Plans statuses). |
| REVIEW | 0 / 9 / 1 | Section 5 dispatch and trailer consumption. |
| DOCV | 0 / 5 / 2 | Section 6. |

**Not mirror candidates (`no`-only):** ARG, ANA, DEFC, DIR, DQ, RECOV, ABORT, GH — all fix-issue-specific (URL resolution, Analyst gate, design directive, aborted-Issue path, GitHub close).

Per CLAUDE.md `## Scratch-file convention`, only the manifest **lead statements** carry a hard mirror requirement; every other `yes` above is a drift *check*, not a byte-identity mandate.

