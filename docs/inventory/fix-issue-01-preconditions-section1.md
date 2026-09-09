# Rule inventory — `skills/quo-fix-issue/SKILL.md` L1–L247 (frontmatter, Overview, Preconditions, Section 1)

Source slice: `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md` lines 1–247. Row IDs are prefixed `F1-`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F1-001 | Skill frontmatter `name` is `quo-fix-issue`. | definition | L2 (frontmatter) | - | - | - | none | no | procedure |
| F1-002 | Frontmatter `description`: "Fix an issue described in a Bee ticket. Use '/quo-fix-issue all' … or '/quo-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset." | definition | L3 (frontmatter) | - | - | - | none | no | procedure |
| F1-003 | Frontmatter `argument-hint` is `"[<issue-id> \| <url> \| <id-or-url> ... \| all]"`. | definition | L4 (frontmatter) | - | - | - | none | no | procedure |
| F1-004 | The skill has exactly six invocation forms (listed in F1-005..F1-010). | definition | L9 `## Overview` | - | argument string | - | none | no | procedure |
| F1-005 | `/quo-fix-issue` (no args): list all open issues, ask the user which one to fix. | choice-set | L10 `## Overview` | issue-pick prompt | open-issues query | - | bees, AskUserQuestion | no | procedure |
| F1-006 | `/quo-fix-issue <issue-id>`: fix that specific issue. | definition | L11 `## Overview` | - | `<issue-id>` | - | none | no | procedure |
| F1-007 | `/quo-fix-issue <id1> <id2> <id3>`: fix the explicit list sequentially, in the order given; IDs may be separated by spaces, commas, or any mix. | ordering | L12 `## Overview` | ordered issue list | argument string | - | none | no | procedure |
| F1-008 | `/quo-fix-issue <url>`: file the URL as an Issue first via `/quo-file-issue`, then fix the resulting Issue. | ordering | L13 `## Overview` | Issue ticket, then fix | URL token | `/quo-file-issue` | Agent (Skill tool), bees | no | procedure |
| F1-009 | `/quo-fix-issue <id-or-url> ...`: mixed IDs and URLs processed in the order given; each URL is filed first and substituted in place. | ordering | L14 `## Overview` | substituted working list | mixed token list | `/quo-file-issue` | Agent (Skill tool), bees | no | procedure |
| F1-010 | `/quo-fix-issue all`: fix ALL open issues sequentially without user intervention. | invariant | L15 `## Overview` | - | open-issues query | - | bees | no | procedure |
| F1-011 | Example: `b.cnb,b.sgq b.xet` is a valid mixed-delimiter list. | example | L12 `## Overview` | - | - | - | none | no | example |
| F1-012 | Example URL invocations: `/quo-fix-issue https://github.com/example/repo/issues/123` and `/quo-fix-issue b.cnb https://github.com/example/repo/issues/123 b.xet`. | example | L13-L14 `## Overview` | - | - | - | none | no | example |
| F1-013 | Before doing anything else, verify the host repo is configured for quorum; on failure **Hard-fail** with `Run /quo-setup first.` plus a one-line note of what is missing. | precondition | L19 `## Preconditions` | hard-fail message | CLAUDE.md, bees hives, subagent registry | `/quo-setup` | bees, Bash | yes | procedure |
| F1-014 | Require the eight custom subagent types registered in the session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`. | precondition | L21 `## Preconditions` | - | session subagent registry | `agents/*.md` | Agent | unknown (quo-execute has no `analyst`) | procedure |
| F1-015 | Custom subagents load at Claude Code session start; a fresh install needs a Claude Code restart or `/agents` hot-reload before dispatch works. | definition | L21 `## Preconditions` | - | - | `/agents` | none | yes | procedure |
| F1-016 | If any of the eight is missing at run-time, STOP at the precondition gate and emit the hard-fail message. | gate | L21 `## Preconditions` | hard-fail message; run exit | F1-014 result | - | none | yes | procedure |
| F1-017 | Never fall back to `general-purpose`, never skip the dispatch, never improvise substitute roles when a subagent type is missing. | invariant | L21 `## Preconditions` | - | - | - | Agent | yes | procedure |
| F1-018 | The subagent hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents` to hot-reload. | field-or-template | L21 `## Preconditions` | hard-fail message | missing-list | `README.md` `## Install`, `/agents` | none | yes | procedure |
| F1-019 | Example hard-fail text: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` | field-or-template | L21 `## Preconditions` | hard-fail message | `<missing-list>` | `README.md` `## Install` | none | yes | procedure |
| F1-020 | Require the Issues hive colonized: `bees list-hives` must include a hive whose `normalized_name` is `issues`. | precondition | L22 `## Preconditions` | - | `bees list-hives` output | - | bees | yes | procedure |
| F1-021 | Require the Specs hive colonized: `bees list-hives` must include a hive whose `normalized_name` is `specs`. | precondition | L23 `## Preconditions` | - | `bees list-hives` output | - | bees | yes | procedure |
| F1-022 | If Specs is absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` | field-or-template | L23 `## Preconditions` | hard-fail message | F1-021 result | `/quo-setup` | none | yes | procedure |
| F1-023 | Require CLAUDE.md to contain a `## Documentation Locations` section. | precondition | L24 `## Preconditions` | - | target CLAUDE.md | CLAUDE.md `## Documentation Locations` | none | yes | procedure |
| F1-024 | The PM and Doc Writer roles read architecture/customer-doc paths from `## Documentation Locations` by exact key. | definition | L24 `## Preconditions` | - | CLAUDE.md `## Documentation Locations` | `pm`, `doc-writer` | none | yes | procedure |
| F1-025 | Require CLAUDE.md to contain `## Build Commands` with all five keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. | precondition | L25 `## Preconditions` | - | target CLAUDE.md | CLAUDE.md `## Build Commands` | none | yes | procedure |
| F1-026 | The Engineer reads compile/format/lint/test commands from `## Build Commands` by exact key. | definition | L25 `## Preconditions` | - | CLAUDE.md `## Build Commands` | `engineer` | none | yes | procedure |
| F1-027 | Rationale: commands and doc paths come from CLAUDE.md so the skill works on Rust, Node, Python, Go, etc.; auto-detection is unsafe on polyglot/monorepo/custom builds. | rationale-only | L27 `## Preconditions` | - | - | - | none | yes | rationale |
| F1-028 | If any precondition is missing, stop with `Run /quo-setup first.` and direct the user there. | gate | L29 `## Preconditions` | hard-fail message; run exit | F1-013..F1-025 results | `/quo-setup` | none | yes | procedure |
| F1-029 | Do not improvise commands or guess paths when a precondition is missing. | invariant | L29 `## Preconditions` | - | - | - | none | yes | procedure |
| F1-030 | Subagent verification rides on the first dispatch: any `Agent type '<name>' not found`-style Agent-tool error for one of the eight types makes the orchestrator STOP, emit the hard-fail message, and exit. | gate | L31 **Verifying the subagents precondition.** | hard-fail message; run exit | Agent tool error | F1-019 message | Agent | yes | procedure |
| F1-031 | On that dispatch error: no fallback to `general-purpose`, no skipping the dispatch, no substitute role. | invariant | L31 **Verifying the subagents precondition.** | - | - | - | Agent | yes | procedure |
| F1-032 | Rationale: the dispatch-time gate is honest about session-load semantics and fires at the natural failure point, so token pressure or creativity cannot bypass it. | rationale-only | L31 **Verifying the subagents precondition.** | - | - | `/agents` | none | yes | rationale |
| F1-033 | Run the reasoning-effort check **first in this section**, ahead of the issue-pick gate (no-args mode) and the isolation-strategy gate. | ordering | L39 `#### Check session reasoning effort` | - | - | issue-pick gate; `#### Validate isolation strategy` | none | yes | procedure |
| F1-034 | Rationale: the **Let me change it first** option exits the run, so firing first means the user never re-answers a pick already made. | rationale-only | L39 `#### Check session reasoning effort` | - | - | - | none | yes | rationale |
| F1-035 | Run the effort check once at the start of the run — not per issue. | ordering | L39 `#### Check session reasoning effort` | - | - | - | none | yes | procedure |
| F1-036 | The skill is tuned for an orchestrator session at **`medium`** reasoning effort or higher. | definition | L41 `#### Check session reasoning effort` | - | - | - | none | yes | procedure |
| F1-037 | Every subagent dispatched from a role file (`agents/*.md`) has effort pinned in frontmatter and is **not** affected by the session setting. | definition | L41 `#### Check session reasoning effort` | - | `agents/*.md` frontmatter | `agents/*.md` | Agent | yes | procedure |
| F1-038 | The check concerns the orchestrator's seat plus any role-file-less dispatch — notably Section 8's `general-purpose` post-completion review sweep, which inherits the session setting. | definition | L41 `#### Check session reasoning effort` | - | - | Section 8 | Agent | yes | procedure |
| F1-039 | The skill cannot change the session effort itself; at most it names the recommendation and lets the user apply it. | invariant | L41 `#### Check session reasoning effort` | - | - | - | none | yes | procedure |
| F1-040 | **Ordering is load-bearing**: read the environment variable **first**, evaluate against the floor, and only then decide whether a gate fires. | ordering | L43 `#### Check session reasoning effort` | - | `CLAUDE_EFFORT` | - | Bash | yes | procedure |
| F1-041 | Do NOT create the gate task before the floor comparison. | invariant | L43 `#### Check session reasoning effort` | - | - | two-step contract | TaskList | yes | procedure |
| F1-042 | Rationale: a stranded `pending` `gate-*` task violates yield-control discipline; the two-step contract's recovery re-fires the tool from leftover `gate-*` tasks, producing a phantom prompt later. | rationale-only | L43 `#### Check session reasoning effort` | - | - | two-step contract | TaskList | yes | rationale |
| F1-043 | **Step 1**: read the session's current effort with one literal command and no shell conditional; the comparison is your own reasoning. | command | L45 **Step 1 — read the session's current effort.** | effort value | `CLAUDE_EFFORT` | - | Bash | yes | procedure |
| F1-044 | POSIX command: `printenv CLAUDE_EFFORT`. | command | L47-L50 **Step 1 — read the session's current effort.** | effort value | env | - | Bash | yes | procedure |
| F1-045 | PowerShell command: `Write-Output $env:CLAUDE_EFFORT`. | command | L52-L55 **Step 1 — read the session's current effort.** | effort value | env | - | Bash | yes | procedure |
| F1-046 | `CLAUDE_EFFORT` reports the session's **current** effort and tracks mid-session changes (e.g. via `/model`), not a launch-time flag. | definition | L57 `#### Check session reasoning effort` | - | `CLAUDE_EFFORT` | `/model` | none | yes | procedure |
| F1-047 | If output is empty, exit is non-zero, or value is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat as unset: **skip this check entirely and continue to the next sub-step, silently.** | recovery | L59 `#### Check session reasoning effort` | - | F1-043 output | - | none | yes | procedure |
| F1-048 | Rationale: a spurious prompt on every run is worse than a missed advisory. | rationale-only | L59 `#### Check session reasoning effort` | - | - | - | none | yes | rationale |
| F1-049 | **Step 2**: the floor is `medium`; the ordering is `low` < `medium` < `high` < `xhigh` < `max`. | definition | L61 **Step 2 — compare against this skill's floor, which is `medium`.** | comparison result | effort value | - | none | yes | procedure |
| F1-050 | Compare against the floor, never for equality. | invariant | L61 **Step 2 — compare against this skill's floor, which is `medium`.** | - | effort value | - | none | yes | procedure |
| F1-051 | Rationale: an operator running hotter costs wall-clock, not quality; interrupting them is gate-fatigue noise. | rationale-only | L61 **Step 2 — compare against this skill's floor, which is `medium`.** | - | - | - | none | yes | rationale |
| F1-052 | **At or above `medium`**: say nothing — no gate, no prompt, no output, **no `TaskCreate`**; continue to the next sub-step. | gate | L63 `#### Check session reasoning effort` | - | comparison result | - | none | yes | procedure |
| F1-053 | **Strictly below `medium`**: fire the gate in step 3. | gate | L64 `#### Check session reasoning effort` | gate | comparison result | Step 3 | TaskList, AskUserQuestion | yes | procedure |
| F1-054 | **Step 3**: honor the two-step contract — `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate, then call `AskUserQuestion` in the same turn. | gate | L66 **Step 3 — fire the gate (this branch only).** | `gate-askuserquestion-<short-suffix>` task; prompt | comparison result | Section 4's TaskList naming convention (gate-task entry) | TaskList, AskUserQuestion | yes | procedure |
| F1-055 | Substitute the value read in step 1 for `<current>` in the question text. | field-or-template | L66 **Step 3 — fire the gate (this branch only).** | question text | effort value | - | AskUserQuestion | yes | procedure |
| F1-056 | Question text (verbatim): "This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation … Subagent effort is pinned per role and is NOT affected by this setting." | field-or-template | L68-L75 **Step 3 — fire the gate (this branch only).** | question text | `<current>` | - | AskUserQuestion | yes | procedure |
| F1-057 | Option 1 **Proceed anyway**: run at current effort; mark the `gate-*` task `completed` and continue to the next sub-step. | choice-set | L79 **Step 3 — fire the gate (this branch only).** | `gate-*` task `completed` | user answer | - | TaskList, AskUserQuestion | yes | procedure |
| F1-058 | Option 2 **Let me change it first**: exit without dispatching anything and without fixing any issue; user runs `/model` then re-invokes; mark the `gate-*` task `completed`, then exit cleanly. | choice-set | L80 **Step 3 — fire the gate (this branch only).** | `gate-*` task `completed`; run exit | user answer | `/model` | TaskList, AskUserQuestion | yes | procedure |
| F1-059 | Parse the argument string by splitting on any run of commas and/or whitespace; discard empty tokens. | command | L84 `#### Parse the argument list and pick issues` | token list | argument string | - | none | no | procedure |
| F1-060 | A token starting with `http://` or `https://` is a **URL token**; anything else is a **ticket-ID token** (validated downstream). | definition | L84 `#### Parse the argument list and pick issues` | token classification | token list | - | none | no | procedure |
| F1-061 | URL tokens delimit identically to ticket-ID tokens; tokenization itself is unchanged by URL support. | invariant | L84 `#### Parse the argument list and pick issues` | - | - | - | none | no | procedure |
| F1-062 | **Zero tokens**: query all open issues, present them, ask the user to pick one; fix that one issue and exit. | gate | L86 `#### Parse the argument list and pick issues` | issue-pick prompt; single fix | F1-081 query | - | bees, AskUserQuestion | no | procedure |
| F1-063 | **Exactly one token equal to `all`**: `all` mode — query all open issues, sort by ticket_id, run the fix loop (step 2-7) for each sequentially. | ordering | L87 `#### Parse the argument list and pick issues` | sorted issue batch | F1-081 query | steps 2-7 | bees | no | procedure |
| F1-064 | **Exactly one token that is an issue ID**: single-issue mode — fix that one issue and exit. | definition | L88 `#### Parse the argument list and pick issues` | - | token | - | none | no | procedure |
| F1-065 | **Exactly one token that is a URL** (matches `^https?://`): URL mode — file via the URL-resolution sub-step, then fix the resulting Issue. | ordering | L89 `#### Parse the argument list and pick issues` | filed Issue | URL token | `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | Agent (Skill tool), bees | no | procedure |
| F1-066 | **Two or more tokens** (list mode): treat as an explicit user list where each token is an issue ID or URL; mixed lists are allowed. | definition | L90 `#### Parse the argument list and pick issues` | working list | token list | - | none | no | procedure |
| F1-067 | In list mode, execute the fix loop (step 2-7) for each issue **in the order given**; do NOT sort. | ordering | L90 `#### Parse the argument list and pick issues` | - | working list | steps 2-7 | none | no | procedure |
| F1-068 | Rationale: the user's order is intentional; earlier issues may be prerequisites for later ones. | rationale-only | L90 `#### Parse the argument list and pick issues` | - | - | - | none | no | rationale |
| F1-069 | In list mode, URL tokens are resolved by the URL-resolution sub-step and substituted *in place* with the resulting Issue ID before the fix loop runs. | ordering | L90 `#### Parse the argument list and pick issues` | substituted working list | URL tokens | `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | Agent (Skill tool) | no | procedure |
| F1-070 | In list mode, do not query or fix issues outside the list. | invariant | L90 `#### Parse the argument list and pick issues` | - | working list | - | none | no | procedure |
| F1-071 | In list mode, no user confirmation between issues. | invariant | L90 `#### Parse the argument list and pick issues` | - | - | - | none | no | procedure |
| F1-072 | Example: `/quo-fix-issue b.cnb b.sgq b.xet`, `/quo-fix-issue b.cnb,b.sgq,b.xet`, and `/quo-fix-issue b.cnb, b.sgq  b.xet` all parse to the same three-ID list. | example | L93 Notes for list mode | - | - | - | none | no | example |
| F1-073 | Up-front validation: after URL resolution but before starting any fixes, run `bees show-ticket --ids <id1> <id2> ...` on the full post-resolution list. | command | L94 Notes for list mode | validation result | post-resolution working list | `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | bees | no | procedure |
| F1-074 | If any ID does not exist, is not in the `issues` hive, or is not `open`, report the problem IDs and continue with the valid open subset; do not abort the run. | recovery | L94 Notes for list mode | user report; trimmed list | `bees show-ticket` output | - | bees | no | procedure |
| F1-075 | The failure check is cumulative across both gates: URL-resolution soft-fails AND `bees show-ticket` validation failures both count toward dropped tokens. | invariant | L94 Notes for list mode | dropped-token count | F1-074, F1-122 | URL-resolution sub-step soft-fail handling | none | no | procedure |
| F1-076 | If *no* tokens remain valid after both gates, exit with an error. | recovery | L94 Notes for list mode | run exit | dropped-token count | - | none | no | procedure |
| F1-077 | Between issues there is no Agent-teardown ceremony: per-issue cold dispatches (Section 4) complete-and-exit on return, and Section 7 closes per-issue TaskList tasks at close-out. | definition | L95 Notes for list mode | - | - | Section 4, Section 7 | Agent, TaskList | no | procedure |
| F1-078 | Section 7 step 5 runs the **Issue-boundary state-externalization checkpoint** after Section 7.5's deferral-hygiene gate and before the next issue starts. | ordering | L95 Notes for list mode | - | - | Section 7 step 5, Section 7.5 deferral-hygiene gate | none | no | procedure |
| F1-079 | This list-mode bullet is an argument-parsing note and does not define the checkpoint; Section 7 step 5 is the definition. | definition | L95 Notes for list mode | - | - | Section 7 step 5 | none | no | procedure |
| F1-080 | Query open issues only in no-args and `all` modes; list mode uses the user's explicit list instead. | invariant | L97 `#### Parse the argument list and pick issues` | - | mode | - | bees | no | procedure |
| F1-081 | Open-issues query (verbatim): `bees execute-freeform-query --query-yaml 'stages:\n  - [type=bee, hive=issues, status=open]\nreport: [title]'`. | command | L98-L102 `#### Parse the argument list and pick issues` | open-issue list | Issues hive | - | bees | no | procedure |
| F1-082 | After parsing and resolving which issues to fix, but **before** validating any individual issue or dispatching any per-issue Agent, check whether you are in an isolated context. | ordering | L106 `#### Validate isolation strategy` | - | cwd, branch | - | git | yes | procedure |
| F1-083 | Rationale: fixes produce one git commit per issue, so landing them on the wrong branch is hard to undo. | rationale-only | L106 `#### Validate isolation strategy` | - | - | - | git | yes | rationale |
| F1-084 | Mirror `/quo-execute`'s isolation block. | invariant | L106 `#### Validate isolation strategy` | - | - | `/quo-execute` | none | yes | procedure |
| F1-085 | **Scenario A — Already in a worktree** whose directory name suggests issue-fix work (e.g. `fix-issues`, `bug-sweep`, or a fix-issue slug): proceed directly, no action. | gate | L108 **Scenario A — Already in a worktree.** | - | worktree dir name | - | git | yes | procedure |
| F1-086 | **Scenario B — On an existing branch in the main repo** (not a worktree): behavior depends on mode and current branch. | definition | L110 **Scenario B — On an existing branch in the main repo.** | - | mode, branch | - | git | yes | procedure |
| F1-087 | If on `main` (or `master`), **always** prompt with `AskUserQuestion`, regardless of mode. | gate | L112 **Scenario B — On an existing branch in the main repo.** | isolation prompt | branch name | - | AskUserQuestion, git | yes | procedure |
| F1-088 | Rationale: landing many commits on main without confirmation is the surprise this prompt prevents. | rationale-only | L112 **Scenario B — On an existing branch in the main repo.** | - | - | - | none | yes | rationale |
| F1-089 | If on a feature branch in single-issue mode, proceed silently. | gate | L113 **Scenario B — On an existing branch in the main repo.** | - | branch, mode | - | git | yes | procedure |
| F1-090 | If on a feature branch in `all` mode or list mode, prompt with `AskUserQuestion`. | gate | L114 **Scenario B — On an existing branch in the main repo.** | isolation prompt | branch, mode | - | AskUserQuestion, git | yes | procedure |
| F1-091 | Option 1 **Create a feature branch (Recommended for `all` mode and list mode)**: create a branch (e.g. `fix/issues-<short-slug>` or `fix/<id1>-<id2>`) from current HEAD; commit all fixes there. | choice-set | L118 `#### Validate isolation strategy` | new local branch | user answer | - | AskUserQuestion, git | yes | procedure |
| F1-092 | Option 1 creates a local branch only — no remote push. | invariant | L118 `#### Validate isolation strategy` | - | - | - | git | yes | procedure |
| F1-093 | Option 2 **Work on current branch**: commit directly to the checked-out branch and tell the user the branch name. | choice-set | L119 `#### Validate isolation strategy` | commits on current branch; branch-name relay | user answer | - | AskUserQuestion, git | yes | procedure |
| F1-094 | Option 3 **Set up a worktree instead**: if `/bees-worktree-add` is installed, suggest running it to spawn the session in an isolated worktree (fire-and-forget in a separate tmux session). | choice-set | L120 `#### Validate isolation strategy` | advice | installed-skill check | `/bees-worktree-add` | AskUserQuestion | yes | procedure |
| F1-095 | If `/bees-worktree-add` is not installed, omit option 3. | choice-set | L120 `#### Validate isolation strategy` | - | installed-skill check | `/bees-worktree-add` | none | yes | procedure |
| F1-096 | On option 3, exit after giving the advice — do not proceed with work. | choice-set | L120 `#### Validate isolation strategy` | run exit | user answer | - | none | yes | procedure |
| F1-097 | The isolation question must always state the current working directory. | field-or-template | L122-L123 `#### Validate isolation strategy` | question text | cwd | - | AskUserQuestion | yes | procedure |
| F1-098 | The isolation question must always state the current branch name. | field-or-template | L122-L124 `#### Validate isolation strategy` | question text | branch name | - | AskUserQuestion, git | yes | procedure |
| F1-099 | The isolation question must always state that option 1 creates a local branch only (no remote push). | field-or-template | L122-L125 `#### Validate isolation strategy` | question text | - | - | AskUserQuestion | yes | procedure |
| F1-100 | The isolation question must always state the number of issues queued (commit-volume implication). | field-or-template | L122-L126 `#### Validate isolation strategy` | question text | working list length | - | AskUserQuestion | yes | procedure |
| F1-101 | If the working list has URL tokens (`^https?://`), resolve each to an Issue ticket ID before the upfront `bees show-ticket --ids` validation pass. | ordering | L130 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | resolved IDs | URL tokens | bullet list at top of Section 1; F1-073 | Agent (Skill tool), bees | no | procedure |
| F1-102 | The isolation-strategy choice applies to the entire run, including the file-then-fix transition this sub-step initiates. | invariant | L130 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | isolation choice | `#### Validate isolation strategy` | git | no | procedure |
| F1-103 | Rationale: isolating before resolution lets the user opt into a fresh branch that scopes the file-from-URL commits. | rationale-only | L130 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | - | - | none | no | rationale |
| F1-104 | **File-then-fix transition announcement**: before the per-URL Skill-tool loop, print a short informational line — recommended `Filing URL(s) as Issue(s) first, then fixing.` | relay | L132 **File-then-fix transition announcement.** | console line | URL-token presence | - | none | no | procedure |
| F1-105 | The announcement is informational console output, NOT an `AskUserQuestion` gate; it does not block and the user is not asked to confirm. | invariant | L132 **File-then-fix transition announcement.** | - | - | - | none | no | procedure |
| F1-106 | Fire the announcement only when at least one URL token is present; on the all-IDs path suppress it entirely. | gate | L132 **File-then-fix transition announcement.** | - | URL-token presence | - | none | no | procedure |
| F1-107 | For each URL token in the working list, iterating in input order, dispatch `/quo-file-issue` inline through the Skill tool. | command | L134 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | Skill dispatch per URL | URL tokens | `/quo-file-issue` | Agent (Skill tool) | no | procedure |
| F1-108 | This consumes the `## Inline invocation via the Skill tool` contract section in `skills/quo-file-issue/SKILL.md`. | definition | L134 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | - | `skills/quo-file-issue/SKILL.md` `## Inline invocation via the Skill tool` | none | no | procedure |
| F1-109 | The dispatch shape mirrors `skills/quo-plan/SKILL.md` sub-step 4b (Skill-tool dispatch of `/quo-write-prd` / `/quo-write-sdd` with free-text `args`, capturing structured return fields). | definition | L134 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | - | `skills/quo-plan/SKILL.md` sub-step 4b, `/quo-write-prd`, `/quo-write-sdd` | none | no | procedure |
| F1-110 | Pass `args` as a free-text payload of exactly the shape `url: <url>`. | field-or-template | L134-L138 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | Skill `args` | URL token | - | Agent (Skill tool) | no | procedure |
| F1-111 | Send only `url: <url>`; leave the contract's OPTIONAL `summary:` field unset so `/quo-file-issue` performs its own `WebFetch` (this skill does not pre-fetch). | invariant | L140 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | - | `/quo-file-issue` External-reference branch | none | no | procedure |
| F1-112 | Capture three fields from `/quo-file-issue`'s structured return, per the contract's `### Output shape (this skill → caller)` block. | field-or-template | L142 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | captured fields | Skill return | `### Output shape (this skill → caller)` | Agent (Skill tool) | no | procedure |
| F1-113 | **`issue_ticket_id`**: the Issue ticket ID to substitute into the working list. | field-or-template | L144 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | working-list substitution | Skill return | - | none | no | procedure |
| F1-114 | **`issue_status`**: always `open` on a successful return; the close-out flip to `done` is owned by Section 7 of this skill, not `/quo-file-issue`. | field-or-template | L145 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | Skill return | Section 7 | none | no | procedure |
| F1-115 | **`action`**: exactly `created` for a freshly-filed Issue or `reused-existing` for a dedupe match. | field-or-template | L146 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | display input | Skill return | - | none | no | procedure |
| F1-116 | `action` is informational (consumed by the post-resolution display) and NOT load-bearing for substitution; both values yield a valid `issue_ticket_id`. | definition | L146 `#### Resolve URL tokens to Issue tickets via /quo-file-issue` | - | `action` | **Post-resolution working-list display.** | none | no | procedure |
| F1-117 | **In-place substitution**: a URL token at position N becomes the resolved `issue_ticket_id` at position N in the post-resolution working list. | invariant | L148 **In-place substitution semantics.** | post-resolution working list | `issue_ticket_id` | - | none | no | procedure |
| F1-118 | NEVER append the resolved ID at the tail of the list. | invariant | L148 **In-place substitution semantics.** | - | - | - | none | no | procedure |
| F1-119 | NEVER reorder the surrounding tokens. | invariant | L148 **In-place substitution semantics.** | - | - | - | none | no | procedure |
| F1-120 | NEVER deduplicate within the list. | invariant | L148 **In-place substitution semantics.** | - | - | - | none | no | procedure |
| F1-121 | Rationale: in-place substitution preserves the "do NOT sort — the user's order is intentional" invariant so a prerequisite filed from an earlier URL is fixed first. | rationale-only | L148 **In-place substitution semantics.** | - | - | bullet list at top of Section 1 | none | no | rationale |
| F1-122 | **Soft-fail on dispatch failure**: drop the failed URL token, report the failure to the user, continue with the remaining tokens (per the list-mode "Up-front validation" pattern). | recovery | L150 **Soft-fail on dispatch failure.** | user report; trimmed list | dispatch outcome | "Notes for list mode" Up-front validation | none | no | procedure |
| F1-123 | Dispatch failure includes: the Skill tool itself raises an error. | definition | L152 **Soft-fail on dispatch failure.** | - | Skill tool error | - | Agent (Skill tool) | no | procedure |
| F1-124 | Dispatch failure includes: user cancels at a `/quo-file-issue` gate — the distill `Approve` / `Revise` / `Cancel` gate, the External-reference body-confirmation step, or the dedupe disambiguation gate's `Cancel`. | definition | L153 **Soft-fail on dispatch failure.** | - | Skill return | `/quo-file-issue` behavioral-guarantees block | AskUserQuestion | no | procedure |
| F1-125 | Dispatch failure includes: `/quo-file-issue` returns a non-success structured return. | definition | L154 **Soft-fail on dispatch failure.** | - | Skill return | - | none | no | procedure |
| F1-126 | Only when no valid tokens remain after both gates (URL-resolution soft-fails AND `bees show-ticket --ids` failures) does the run exit with an error. | invariant | L156 **Soft-fail on dispatch failure.** | run exit | dropped-token count | "Notes for list mode" | none | no | procedure |
| F1-127 | A single dropped URL never aborts the whole run when other tokens remain. | invariant | L156 **Soft-fail on dispatch failure.** | - | - | - | none | no | procedure |
| F1-128 | On the **single-URL-token path** (URL mode), a soft-fail on the only URL leaves the list empty; the cumulative-failure rule fires and the run exits with an error. | recovery | L156 **Soft-fail on dispatch failure.** | run exit | dispatch outcome | bullet list at top of Section 1 | none | no | procedure |
| F1-129 | **Post-resolution working-list display**: after every URL token is resolved or soft-failed, and BEFORE the upfront `bees show-ticket --ids` pass, display the working list as informational markdown. | relay | L158 **Post-resolution working-list display.** | console markdown | post-resolution working list | F1-073 | none | no | procedure |
| F1-130 | Label each input position with the resolved ticket ID; call out URL positions as filed-from-URL with the captured `action` value (`created` / `reused-existing`). | field-or-template | L158 **Post-resolution working-list display.** | display text | `issue_ticket_id`, `action` | - | none | no | procedure |
| F1-131 | Recommended display shape: `Post-resolution working list:` then numbered lines like `2. b.<new-id> (input: https://github.com/example/repo/issues/123, action: created)`. | field-or-template | L160-L165 **Post-resolution working-list display.** | display text | - | - | none | no | procedure |
| F1-132 | The display is informational ONLY — NO `AskUserQuestion`, NO ability to re-order. | invariant | L167 **Post-resolution working-list display.** | - | - | - | none | no | procedure |
| F1-133 | Rationale: the display lets the user confirm prerequisite ordering survived; if unhappy they `Ctrl-C` and re-run with corrected order. | rationale-only | L167 **Post-resolution working-list display.** | - | - | - | none | no | rationale |
| F1-134 | Fire the display only when at least one URL token was in the input; on the all-IDs path suppress it entirely. | gate | L167 **Post-resolution working-list display.** | - | URL-token presence | - | none | no | procedure |
| F1-135 | **End of URL-resolution sub-step**: continue Section 1 at the upfront `bees show-ticket --ids` validation pass, then `#### Write the run-state manifest`, then proceed to Step 2. | ordering | L169 **End of URL-resolution sub-step — continue Section 1 and then Step 2.** | - | - | "Notes for list mode", `#### Write the run-state manifest`, Step 2 | bees | no | procedure |
| F1-136 | The skill's steps are: 2 (Validate Issue), 3 (design analysis), 4 (per-issue Agent dispatch), 5 (review loop), 6 (doc verify), 7 (mark Issue done + commit), 8 (post-completion review), 9 (upstream GitHub close commands). | definition | L169 **End of URL-resolution sub-step — continue Section 1 and then Step 2.** | - | - | Steps 2–9 | none | no | procedure |
| F1-137 | The URL-resolution sub-step replaces nothing else in `/quo-fix-issue`'s flow. | invariant | L169 **End of URL-resolution sub-step — continue Section 1 and then Step 2.** | - | - | - | none | no | procedure |
| F1-138 | Each `/quo-file-issue` structured return is a hand-off marker (per `skills/quo-file-issue/SKILL.md` `### Behavioral guarantees` "hand-off marker, not a workflow exit"), NOT a signal that the run has terminated. | invariant | L169 **End of URL-resolution sub-step — continue Section 1 and then Step 2.** | - | Skill return | `skills/quo-file-issue/SKILL.md` `### Behavioral guarantees` | none | no | procedure |
| F1-139 | `#### Write the run-state manifest` is the **canonical definition site** for the manifest; later sections refer to it by name. | definition | L173 `#### Write the run-state manifest` | - | - | - | none | unknown | procedure |
| F1-140 | Write the manifest as the last step of Section 1 — after list parsing, URL resolution, upfront `bees show-ticket --ids` validation, and isolation settlement — before validating or fixing any Issue. | ordering | L173 `#### Write the run-state manifest` | manifest file | working list, isolation choice | Section 1 sub-steps | Bash, git | unknown | procedure |
| F1-141 | The manifest is a small markdown file holding the run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. | definition | L175 `#### Write the run-state manifest` | - | - | - | none | yes | procedure |
| F1-142 | bees holds ticket state, git the diff, the compromise tracker accepted compromises, the `defer-*` TaskList open deferrals; the manifest holds only what those four do not. | invariant | L175 `#### Write the run-state manifest` | - | - | compromise tracker, `defer-*` TaskList | bees, git, TaskList | yes (lead statement; "four" is fix-issue/execute-specific) | procedure |
| F1-143 | After a harness compaction, re-read the manifest instead of trusting a summary — this is what makes compaction survivable. | recovery | L175 `#### Write the run-state manifest` | - | manifest file | - | none | yes | procedure |
| F1-144 | Write the manifest under the scratch-file convention in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). | definition | L177 **Path and filename.** | manifest path | tempdir | - | Bash | yes | procedure |
| F1-145 | Canonical filename: `run-state-quo-fix-issue-<repo-dir-name>.md`. | name-class | L177 **Path and filename.** | manifest filename | `<repo-dir-name>` | - | none | no | procedure |
| F1-146 | `<repo-dir-name>` is the **basename of this run's repository working directory** — the last path segment of the working tree root. | definition | L177 **Path and filename.** | `<repo-dir-name>` | working tree root | - | git | no | procedure |
| F1-147 | Example: a run inside `/home/dev/projects/widget-api` writes `run-state-quo-fix-issue-widget-api.md`. | example | L177 **Path and filename.** | - | - | - | none | no | example |
| F1-148 | Resolve the working tree root with one literal command `git rev-parse --show-toplevel` (identical on POSIX and PowerShell), then take its last path segment. | command | L177-L187 **Path and filename.** | working tree root | git repo | - | Bash, git | no | procedure |
| F1-149 | Create the `.quorum` directory if absent: POSIX `mkdir -p /tmp/.quorum`; PowerShell `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`. | command | L189-L201 **Path and filename.** | `.quorum` directory | tempdir | - | Bash | yes | procedure |
| F1-150 | Author the manifest via the `Write` tool — no shell redirect. | command | L189-L201 **Path and filename.** | manifest file | - | - | none | yes | procedure |
| F1-151 | **The filename is deterministic — do NOT add a random suffix or timestamp.** | invariant | L203 `#### Write the run-state manifest` | - | - | - | none | yes | procedure |
| F1-152 | Rationale: unlike the compromise tracker's `<short-suffix>` (reader is an Agent handed the path), the manifest's reader is the orchestrator post-compaction, so a random suffix would be unfindable. | rationale-only | L203 `#### Write the run-state manifest` | - | - | compromise tracker | none | yes (comparison omitted in breakdown-epic) | rationale |
| F1-153 | Rationale: the key must be recomputable from the working directory alone (`git rev-parse --show-toplevel`); **An Issue ID does not** qualify because batch membership is recorded only inside the manifest and commit subjects cannot recover the first Issue. | rationale-only | L205 **Why the key is skill name plus repo directory — and not an Issue ID.** | - | - | - | git | no | rationale |
| F1-154 | Rationale: the skill-name segment prevents collision with a sibling skill's manifest; the repo-directory segment keeps two projects from *normally* colliding in the machine-wide `<tempdir>/.quorum/`. | rationale-only | L205 **Why the key is skill name plus repo directory — and not an Issue ID.** | - | - | - | none | no | rationale |
| F1-155 | Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends. | invariant | L205 **Why the key is skill name plus repo directory — and not an Issue ID.** | - | - | `/quo-execute`, `/quo-breakdown-epic` | none | yes | procedure |
| F1-156 | `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has; `/quo-fix-issue` appends the repository directory basename; see each skill's manifest section. | definition | L205 **Why the key is skill name plus repo directory — and not an Issue ID.** | - | - | `/quo-execute`, `/quo-breakdown-epic` manifest sections | none | no | procedure |
| F1-157 | Accepted collision: **Two concurrent `/quo-fix-issue` runs in the same working directory** share one filename; the later truncating write wins (such runs already collide over statuses and commits). | definition | L209 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-158 | Accepted collision: **Two different checkouts whose directories share a basename** land on one file; a live second run's truncating write replaces the first's manifest. | definition | L210 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-159 | Consequence of the basename collision: the other checkout's **Pre-session SHA** (possibly nonexistent here) reaches Section 8's post-completion review and scopes its diff wrongly; sequential runs are unaffected. | definition | L210 `#### Write the run-state manifest` | - | **Pre-session SHA** | Section 8 | git | no | failure-narrative |
| F1-160 | Recovery: a manifest whose Issue batch does not match the run in hand is the tell; ignore the manifest and take the `HEAD~N` fallback Section 8 defines for a missing manifest. | recovery | L210 `#### Write the run-state manifest` | - | manifest `Unit scope` | Section 8 `HEAD~N` fallback | git | no | procedure |
| F1-161 | Rationale: alternative keys are worse — an absolute path is unwieldy and leaks directory structure into `<tempdir>`; an Issue ID is not recomputable. | rationale-only | L210 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-162 | **Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. | invariant | L212 `#### Write the run-state manifest` | - | - | - | none | yes | procedure |
| F1-163 | Write the manifest fresh here, overwriting any manifest left by a previous `/quo-fix-issue` run in this repository directory. | ordering | L212 `#### Write the run-state manifest` | manifest file (truncated) | - | - | none | no | procedure |
| F1-164 | Rewrite the manifest in full at each Issue boundary per Section 7 step 5's Issue-boundary state-externalization checkpoint. | ordering | L212 `#### Write the run-state manifest` | manifest rewrite | - | Section 7 step 5 | none | no | procedure |
| F1-165 | Never delete the manifest; do NOT instruct any `rm` / `Remove-Item` (scratch-file convention forbids cleanup). | invariant | L212 `#### Write the run-state manifest` | - | - | scratch-file convention | none | yes | procedure |
| F1-166 | The manifest carries **only values that have no other durable home**; do not add Issue bodies, design directives, or review findings. | invariant | L214 **Contents — and an invariant that bounds them.** | - | - | bees, tracker, diff | none | yes | procedure |
| F1-167 | Rationale: duplicating bees/tracker/diff content would grow the manifest into a shadow ticket store that drifts. | rationale-only | L214 **Contents — and an invariant that bounds them.** | - | - | - | none | yes | rationale |
| F1-168 | Manifest title line: `# Run state — quo-fix-issue @ <repo-dir-name>`. | field-or-template | L217 manifest template | manifest field | `<repo-dir-name>` | - | none | no | procedure |
| F1-169 | Manifest field `**Skill:** quo-fix-issue`. | field-or-template | L219 manifest template | manifest field | - | - | none | no | procedure |
| F1-170 | Manifest field `**Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>`. | field-or-template | L220 manifest template | manifest field | clock | - | none | no | procedure |
| F1-171 | Manifest field `**Unit scope:** ordered Issue batch: <issue-id-1>, <issue-id-2>, ...`. | field-or-template | L221 manifest template | manifest field | post-resolution working list | - | none | no | procedure |
| F1-172 | Manifest field `**Isolation strategy:** <branch created: <name> \| current branch: <name> \| worktree: <path>>`. | field-or-template | L222 manifest template | manifest field | isolation choice | `#### Validate isolation strategy` | git | no | procedure |
| F1-173 | Manifest field `**Pre-session SHA:** <pre-session-sha>`. | field-or-template | L223 manifest template | manifest field | `git rev-parse HEAD` | - | git | no | procedure |
| F1-174 | Manifest field `**Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`. | field-or-template | L224 manifest template | manifest field | tracker path | Section 7.5 | none | no | procedure |
| F1-175 | Manifest field `**Progress:**` with sub-lines `- <issue-id>: done — commit <sha>`. | field-or-template | L225-L226 manifest template | manifest field | issue outcomes | - | none | no | procedure |
| F1-176 | Manifest field `**Next unit:** <next-issue-id \| none>`. | field-or-template | L227 manifest template | manifest field | working list position | - | none | no | procedure |
| F1-177 | The **compromise tracker** field records the tracker's full path *including* its random `<short-suffix>`. | field-or-template | L230 `#### Write the run-state manifest` | manifest field | tracker filename | - | none | no | procedure |
| F1-178 | Generate the tracker filename here, at run start, per Section 7.5 `#### Session-scoped compromise tracker`; the timestamp and suffix are generated once per run. | ordering | L230 `#### Write the run-state manifest` | tracker path | - | Section 7.5 `#### Session-scoped compromise tracker` | none | no | procedure |
| F1-179 | The manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. | definition | L230 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-180 | Recording the tracker path in the manifest does not create the tracker file; it is created only when its first append trigger fires. | invariant | L230 `#### Write the run-state manifest` | - | - | Section 7.5 | none | no | procedure |
| F1-181 | **Progress** carries one line per Issue finished, in the order worked: `<issue-id>: done — commit <sha>` on the fixed path. | field-or-template | L232 `#### Write the run-state manifest` | manifest field | commit sha | - | git | no | procedure |
| F1-182 | On the aborted path, Progress records `<issue-id>: aborted — no commit; Issue left open` (Section 7 `#### Aborted-Issue close-out`). | field-or-template | L232 `#### Write the run-state manifest` | manifest field | abort outcome | Section 7 `#### Aborted-Issue close-out` | none | no | procedure |
| F1-183 | Rationale: recording the aborted shape keeps progress readable post-compaction — an Issue absent from Progress is indistinguishable from one not yet reached. | rationale-only | L232 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-184 | Record the **ordered Issue batch** verbatim in post-resolution order. | field-or-template | L234 `#### Write the run-state manifest` | `Unit scope` field | post-resolution working list | - | none | no | procedure |
| F1-185 | Rationale: the batch order is user-supplied and intentional and cannot be re-derived from bees after compaction. | rationale-only | L234 `#### Write the run-state manifest` | - | - | - | none | no | rationale |
| F1-186 | Capture `<pre-session-sha>` here, at run start, with one literal command; this is the **only** place the run records it. | command | L236 `#### Write the run-state manifest` | `Pre-session SHA` field | HEAD | - | Bash, git | unknown | procedure |
| F1-187 | Section 8 step 1 reads `<pre-session-sha>` back from the manifest, and Section 9 reuses the value Section 8 captured. | definition | L236 `#### Write the run-state manifest` | - | `Pre-session SHA` field | Section 8 step 1, Section 9 | none | no | procedure |
| F1-188 | Pre-session SHA command: `git rev-parse HEAD` (identical on POSIX and PowerShell). | command | L238-L246 `#### Write the run-state manifest` | `<pre-session-sha>` | git repo | - | Bash, git | unknown | procedure |

## Anchors defined here

- L7 `## Overview`
- L17 `## Preconditions`
- L19 **Hard-fail**
- L31 **Verifying the subagents precondition.**
- L33 `## Execution Flow`
- L35 `### 1. Determine which issues to fix`
- L37 `#### Check session reasoning effort`
- L39 **first in this section**
- L39 **Let me change it first**
- L41 **`medium`**
- L41 **not**
- L43 **Ordering is load-bearing.**
- L43 **first**
- L45 **Step 1 — read the session's current effort.**
- L57 **current**
- L59 **skip this check entirely and continue to the next sub-step, silently.**
- L61 **Step 2 — compare against this skill's floor, which is `medium`.**
- L63 **At or above `medium`**
- L63 **no `TaskCreate`**
- L64 **Strictly below `medium`**
- L66 **Step 3 — fire the gate (this branch only).**
- L79 **Proceed anyway**
- L80 **Let me change it first**
- L82 `#### Parse the argument list and pick issues`
- L84 **URL token**
- L84 **ticket-ID token**
- L86 **Zero tokens**
- L87 **Exactly one token equal to `all`**
- L88 **Exactly one token that is an issue ID**
- L89 **Exactly one token that is a URL**
- L90 **Two or more tokens**
- L90 **in the order given**
- L92 Notes for list mode (unbolded run-in label)
- L94 Up-front validation (unbolded run-in label, referenced by name at L150)
- L95 **Issue-boundary state-externalization checkpoint**
- L104 `#### Validate isolation strategy`
- L106 **before**
- L108 **Scenario A — Already in a worktree.**
- L110 **Scenario B — On an existing branch in the main repo.**
- L112 **always**
- L118 **Create a feature branch (Recommended for `all` mode and list mode)**
- L119 **Work on current branch**
- L120 **Set up a worktree instead**
- L128 `#### Resolve URL tokens to Issue tickets via /quo-file-issue`
- L132 **File-then-fix transition announcement.**
- L144 **`issue_ticket_id`**
- L145 **`issue_status`**
- L146 **`action`**
- L148 **In-place substitution semantics.**
- L150 **Soft-fail on dispatch failure.**
- L156 **single-URL-token path**
- L158 **Post-resolution working-list display.**
- L169 **End of URL-resolution sub-step — continue Section 1 and then Step 2.**
- L171 `#### Write the run-state manifest`
- L173 **canonical definition site**
- L175 **nowhere else on disk**
- L177 **Path and filename.**
- L177 **basename of this run's repository working directory**
- L203 **The filename is deterministic — do NOT add a random suffix or timestamp.**
- L205 **Why the key is skill name plus repo directory — and not an Issue ID.**
- L205 **An Issue ID does not.**
- L207 **not**
- L209 **Two concurrent `/quo-fix-issue` runs in the same working directory.**
- L210 **Two different checkouts whose directories share a basename**
- L210 **Pre-session SHA**
- L212 **Semantics: truncate at run start, rewrite at each boundary.**
- L212 **live snapshot, not an accumulating log**
- L214 **Contents — and an invariant that bounds them.**
- L214 **only values that have no other durable home.**
- L219 **Skill:**
- L220 **Run started (UTC):**
- L221 **Unit scope:**
- L222 **Isolation strategy:**
- L223 **Pre-session SHA:**
- L224 **Compromise tracker:**
- L225 **Progress:**
- L227 **Next unit:**
- L230 **compromise tracker**
- L232 **Progress**
- L234 **ordered Issue batch**
- L236 **only**

## Rationale-only spans

- L27 — CLAUDE.md lookup beats auto-detection (1 line)
- L209 — concurrent same-dir runs collide anyway (1 line)

Mixed lines (rule plus rationale on the same line, so not counted as pure rationale spans): L31 (final sentence), L39 (second sentence), L43 (final clause), L59 (final sentence), L61 (final clause), L90 (parenthetical), L106 (first sentence's "so" clause), L112 (second sentence), L130 (final sentence), L148 (final sentence), L167 (second sentence), L203 (after the bolded rule), L205 (all but the "Every skill in this set…" and discriminator sentences), L210 (all but the detect-and-recover sentence), L214 (second sentence), L230 (third sentence), L232 (second sentence), L234 (parenthetical and "which is exactly why").
