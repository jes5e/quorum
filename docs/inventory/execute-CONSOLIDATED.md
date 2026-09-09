# Consolidated rule inventory — `/quo-execute` (skills/quo-execute/SKILL.md)

Built from the seven slice inventories `docs/inventory/execute-01…07-*.md` (raw prefixes E1–E7, 1,352 rows). Every raw row is accounted for exactly once in a `Sources` cell below. Rows were merged only when an executing orchestrator would treat them as a single instruction (same rule restated at another site, or one rule fragmented across sentences); rows that merely share a topic stay separate. Conflicting source rows are kept separately and listed under `## Inconsistencies noticed`.

Conventions: `Sites` are SKILL.md line anchors from the slice files (`L27 Preconditions` = line 27, under `## Preconditions`). `Env` is the union of the source rows' Env values (`none` = no tool dependency beyond reading/writing prose). `Mirror` reproduces the source value(s); where merged rows disagree, all values are listed. `TaskList-dependent` in each header is `yes` when any row in the mechanism carries `TaskList` in Env.

Mechanism codes: META, PRE, EFF, BEE, ISO, MAN, EPIC, LOOP, MOV, UMG, PCR, DPS, ROLES, PMD, TL, GATE, SMW, TEST, CLEAN, SOE, DEFER, NEXT, CKPT, CWG, ABORT, EDP, ROUTE, BEEREV, POST, DHG, TRK, FINAL, SUMM, MERGE, SHELL.

---

## M01. Frontmatter & overview (`EX-META`)

- **Purpose:** Declare the skill's identity to the loader and state the end-to-end flow in nine sentences.
- **Failure it prevents:** not stated.
- **Env deps:** bees, git, Agent, AskUserQuestion. TaskList-dependent: **no**.
- **Rows after dedupe:** 9 (procedure 9 · rationale 0 · example 0)
- **Literals:** `quo-execute` · `Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.` · `"[<bee-id> | <epic-id>]"`
- **Cross-mechanism edges:** Produces for → BEE (step 1), EPIC/NEXT (steps 2, loop), ROLES/LOOP (step 3 "Team"), CLEAN (one commit per Task), BEEREV/POST/FINAL/SUMM (post-Epics ordering). Consumes from → none.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-META-1 | Frontmatter `name` is `quo-execute`. | definition | L2 frontmatter | E1-001 | - | - | none | no | procedure |
| EX-META-2 | Frontmatter `description` is `Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.` (typo "therin" is in the shipped string). | definition | L3 frontmatter | E1-002 | - | - | none | no | procedure |
| EX-META-3 | Frontmatter `argument-hint` is `"[<bee-id> \| <epic-id>]"`. | definition | L4 frontmatter | E1-003 | - | - | none | no | procedure |
| EX-META-4 | Overview step 1: find the Bee to work on and validate it is ready. | ordering | L9-10 Overview | E1-004 | - | - | bees | no | procedure |
| EX-META-5 | Overview step 2: find the best Epic; validate it is unblocked; validate its description still makes sense after reviewing prior Epics' work. | ordering | L11-13 Overview | E1-005 | - | - | bees | no | procedure |
| EX-META-6 | Overview step 3: form a Team to complete the Epic's work; send questions/clarifications to the caller. | relay | L14-15 Overview | E1-006 | dispatches | - | Agent, AskUserQuestion | no | procedure |
| EX-META-7 | Create one git commit per Task including all changes for that Task (overview statement; operational rule is EX-CLEAN-5). | invariant | L16 Overview | E1-007 | git commit | - | git | no | procedure |
| EX-META-8 | Loop steps 2–3 until all Epics are done. | ordering | L17 Overview | E1-008 | - | - | none | no | procedure |
| EX-META-9 | After all Epics done, in order: disband execution Team, form Review Team, address Review findings, get User approval, mark Bee and children closed, output final summary. | ordering | L18-23 Overview | E1-009 | status flips, final summary | - | Agent, AskUserQuestion, bees | no | procedure |

---

## M02. Preconditions & contract keys (`EX-PRE`)

- **Purpose:** Verify the host repo is configured for quorum (seven subagent types, Plans + Specs hives, the two CLAUDE.md contract sections) and hard-fail with `Run /quo-setup first.` rather than improvise.
- **Failure it prevents:** Improvised build commands / guessed paths on polyglot or custom stacks, and silent `general-purpose` substitution for a missing role.
- **Env deps:** Agent, bees. TaskList-dependent: **no**.
- **Rows after dedupe:** 16 (procedure 12 · rationale 3 · example 1)
- **Literals:** `Run /quo-setup first.` · `engineer` · `test-writer` · `doc-writer` · `pm` · `code-reviewer` · `test-reviewer` · `doc-reviewer` · `general-purpose` · `/agents` · `README.md` `## Install` · `bees list-hives` · `normalized_name` · `plans` · `specs` · `## Documentation Locations` · `## Build Commands` · `Compile/type-check` · `Format` · `Lint` · `Narrow test` · `Full test` · `Agent type '<name>' not found` · `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` · `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`
- **Cross-mechanism edges:** Produces for → LOOP/DPS (registered role types), TEST/CLEAN (Build Commands keys), ROLES (Documentation Locations keys). Consumes from → none (first thing the run does).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-PRE-1 | Before anything else, verify the host repo is configured for quorum. | precondition | L27 Preconditions | E1-010 | - | - | none | yes | procedure |
| EX-PRE-2 | Hard-fail with `Run /quo-setup first.` plus a one-line note on what is missing if any precondition is absent. | precondition | L27 Preconditions | E1-011 | hard-fail message | precondition checks | none | yes | procedure |
| EX-PRE-3 | Require seven registered custom subagent types: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. | precondition | L29 Preconditions | E1-012 | - | session's registered subagents | Agent | unknown | procedure |
| EX-PRE-4 | Custom subagents load at session start; a fresh install needs a restart or `/agents` hot-reload before dispatch works. | definition | L29 Preconditions | E1-013 | - | - | Agent | yes | rationale |
| EX-PRE-5 | If any of the seven is missing at run time, STOP at the precondition gate, emit the hard-fail message, and exit — never fall back to `general-purpose`, never skip the dispatch, never improvise a substitute role. | precondition | L29 Preconditions; L39 Verifying the subagents precondition | E1-014, E1-015, E1-029 | hard-fail message, exit | EX-PRE-3, EX-PRE-8 | Agent | unknown | procedure |
| EX-PRE-6 | The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents`. | field-or-template | L29 Preconditions | E1-016 | hard-fail message | - | none | unknown | procedure |
| EX-PRE-7 | Example: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` | example | L29 Preconditions | E1-017 | hard-fail message | `<missing-list>` | none | unknown | example |
| EX-PRE-8 | Subagent verification rides on the first dispatch: an `Agent type '<name>' not found`-style Agent-tool error for any of the seven types is the trigger. | gate | L39 Verifying the subagents precondition | E1-028 | - | Agent tool error | Agent | unknown | procedure |
| EX-PRE-9 | Rationale: the gate matches session-load semantics and fires at the natural failure point, so token pressure or creativity cannot bypass it. | rationale-only | L39 Verifying the subagents precondition | E1-030 | - | - | none | unknown | rationale |
| EX-PRE-10 | Require the Plans hive colonized: `bees list-hives` must include a hive with `normalized_name` `plans`. | precondition | L30 Preconditions | E1-018 | - | `bees list-hives` output | bees | yes | procedure |
| EX-PRE-11 | Require the Specs hive colonized: `bees list-hives` must include a hive with `normalized_name` `specs`. | precondition | L31 Preconditions | E1-019 | - | `bees list-hives` output | bees | yes | procedure |
| EX-PRE-12 | If Specs hive absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` | field-or-template | L31 Preconditions | E1-020 | hard-fail message | EX-PRE-11 | none | yes | procedure |
| EX-PRE-13 | Require CLAUDE.md to contain a `## Documentation Locations` section; agents look up architecture-doc, customer-doc and test-guide paths by exact key from it. | precondition | L32 Preconditions | E1-021, E1-022 | - | target CLAUDE.md | none | yes | procedure |
| EX-PRE-14 | Require CLAUDE.md `## Build Commands` with all five keys `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`; agents look up commands by exact key. The section is required, not optional. | precondition | L33, L35 Preconditions | E1-023, E1-024, E1-026 | - | target CLAUDE.md | none | yes | procedure |
| EX-PRE-15 | Rationale: reading commands/doc paths from CLAUDE.md keeps the skill stack-neutral; auto-detection is unsafe on polyglot/monorepo/custom build systems. | rationale-only | L35 Preconditions | E1-025 | - | - | none | yes | rationale |
| EX-PRE-16 | Do not recover from a missing precondition by improvising commands or guessing paths; fail fast and direct the user to `/quo-setup`. | invariant | L37 Preconditions | E1-027 | - | - | none | yes | procedure |

---

## M03. Session-effort gate (`EX-EFF`)

- **Purpose:** Read `CLAUDE_EFFORT` first thing in Section 1 and prompt only when the orchestrator session is strictly below the `medium` floor.
- **Failure it prevents:** A stranded `pending` `gate-*` task (phantom re-prompt on a later run) and gate-fatigue noise from prompting sessions already at/above the floor.
- **Env deps:** Bash, TaskList, AskUserQuestion, Agent. TaskList-dependent: **yes**.
- **Rows after dedupe:** 21 (procedure 14 · rationale 7 · example 0)
- **Literals:** `CLAUDE_EFFORT` · `printenv CLAUDE_EFFORT` · `Write-Output $env:CLAUDE_EFFORT` · `medium` · `low` · `high` · `xhigh` · `max` · `/model` · `Proceed anyway` · `Let me change it first` · `<current>` · question text `This session is running at \`effort=<current>\`, below the \`medium\` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.` + `Subagent effort is pinned per role and is NOT affected by this setting.`
- **Cross-mechanism edges:** Produces for → GATE (a `gate-askuserquestion-*` fire), POST (the `general-purpose` sweep inherits session effort). Consumes from → GATE (two-step contract), CWG mirrors its read-before-TaskCreate ordering.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-EFF-1 | The session-effort gate is conditional; when it does not fire, no `TaskCreate` fires for it either. | invariant | L45 §1 | E1-035 | - | EX-EFF-9 | TaskList | yes | procedure |
| EX-EFF-2 | Run the session-effort check first in Section 1, ahead of the Bee-pick gate and Section 2's Epic-pick gate. | ordering | L49 Check session reasoning effort | E1-036 | - | - | none | yes | procedure |
| EX-EFF-3 | Rationale: `Let me change it first` exits the run, so firing first means the user never re-answers a pick already made. | rationale-only | L49 | E1-037 | - | - | none | yes | rationale |
| EX-EFF-4 | The skill is tuned for an orchestrator session at `medium` effort or higher. | definition | L51 | E1-038 | - | - | none | yes | procedure |
| EX-EFF-5 | Subagents dispatched from `agents/*.md` have effort pinned in frontmatter and are not affected by the session setting. | definition | L51 | E1-039 | - | `agents/*.md` frontmatter | Agent | yes | rationale |
| EX-EFF-6 | The check concerns the orchestrator seat plus role-file-less dispatches — notably Section 6's `general-purpose` post-completion sweep, which inherits the session setting. | definition | L51 | E1-040 | - | - | Agent | no | rationale |
| EX-EFF-7 | The skill cannot change the session setting; it may only name the recommendation and let the user apply it. | invariant | L51 | E1-041 | - | - | none | yes | procedure |
| EX-EFF-8 | Ordering is load-bearing: read the env var first, evaluate against the floor, only then decide whether a gate fires; do NOT create the gate task before the comparison. | ordering | L53 | E1-042, E1-043 | - | `CLAUDE_EFFORT` | Bash, TaskList | yes | procedure |
| EX-EFF-9 | Rationale: a stranded `pending` `gate-*` task breaks yield-control; the contract's recovery re-fires the tool, producing a phantom prompt on a later run. | rationale-only | L53 | E1-044 | - | - | TaskList | yes | rationale |
| EX-EFF-10 | Step 1: read current effort with one literal command, no shell conditional — `printenv CLAUDE_EFFORT` (POSIX) / `Write-Output $env:CLAUDE_EFFORT` (PowerShell); the comparison is reasoning, not shell logic. | command | L55-65 | E1-045, E1-046, E1-047 | effort value | `CLAUDE_EFFORT` | Bash | yes | procedure |
| EX-EFF-11 | `CLAUDE_EFFORT` reports the session's current effort and tracks mid-session changes (e.g. `/model`), not a launch-time flag. | definition | L67 | E1-048 | - | `CLAUDE_EFFORT` | none | yes | rationale |
| EX-EFF-12 | If output is empty, exits non-zero, or is not one of `low`/`medium`/`high`/`xhigh`/`max`, treat as unset and skip the check entirely, silently. | recovery | L69 | E1-049, E1-050 | - | EX-EFF-10 output | Bash | yes | procedure |
| EX-EFF-13 | Rationale: a spurious prompt on every run is worse than a missed advisory. | rationale-only | L69 | E1-051 | - | - | none | yes | rationale |
| EX-EFF-14 | Step 2: the floor is `medium`; ordering `low` < `medium` < `high` < `xhigh` < `max`; compare against the floor, never for equality. | definition | L71 | E1-052, E1-053 | - | effort value | none | yes | procedure |
| EX-EFF-15 | Rationale: running hotter than the recommendation costs wall-clock not quality; interrupting is gate-fatigue noise. | rationale-only | L71 | E1-054 | - | - | none | yes | rationale |
| EX-EFF-16 | At or above `medium`: say nothing — no gate, no prompt, no output, no `TaskCreate`; continue. | gate | L73 | E1-055 | - | EX-EFF-14 | none | yes | procedure |
| EX-EFF-17 | Strictly below `medium`: fire the gate (step 3) — `TaskCreate` a `gate-askuserquestion-<short-suffix>` task naming this gate, then `AskUserQuestion` in the same turn. | gate | L74, L76 | E1-056, E1-057 | `gate-askuserquestion-<short-suffix>` task | EX-EFF-14 | TaskList, AskUserQuestion | yes | procedure |
| EX-EFF-18 | Substitute the value read in step 1 for `<current>` in the question text. | field-or-template | L76 | E1-058 | question text | EX-EFF-10 output | AskUserQuestion | yes | procedure |
| EX-EFF-19 | Question text verbatim: `This session is running at \`effort=<current>\`, below the \`medium\` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.` + blank line + `Subagent effort is pinned per role and is NOT affected by this setting.` | field-or-template | L78-85 | E1-059 | question text | `<current>` | AskUserQuestion | yes | procedure |
| EX-EFF-20 | Option `Proceed anyway`: run at current effort; mark the `gate-*` task `completed`; continue. | choice-set | L89 | E1-060 | `gate-*` → `completed` | user answer | TaskList, AskUserQuestion | yes | procedure |
| EX-EFF-21 | Option `Let me change it first`: exit without dispatching anything (user runs `/model`, re-invokes); mark `gate-*` `completed`, then exit cleanly. | choice-set | L90 | E1-061 | `gate-*` → `completed`, clean exit | user answer | TaskList, AskUserQuestion | yes | procedure |

---

## M04. Bee selection & validation (`EX-BEE`)

- **Purpose:** Resolve the run's Bee from no-argument / Bee-ID / Epic-ID invocation paths and validate it is `ready` or `in_progress` with all `up_dependencies` `done`.
- **Failure it prevents:** not stated (implicit: working a blocked or non-workable Bee).
- **Env deps:** bees, AskUserQuestion, TaskList. TaskList-dependent: **yes** (via the Bee-pick gate's two-step contract).
- **Rows after dedupe:** 10 (procedure 10 · rationale 0 · example 0)
- **Literals:** `ready` · `in_progress` · `done` · `/quo-plan` · `/quo-plan-from-specs` · `bees execute-freeform-query --query-yaml` · `stages: - [type=bee, hive=plans] report: [title, ticket_status]` · `stages: - [parent=<bee-id>, type=t1, status=ready] report: [title, up_dependencies]` · `stages: - [id=<epic-id>] - [parent] report: [title, ticket_status]` · `up_dependencies` · `ticket_status`
- **Cross-mechanism edges:** Produces for → MAN (Bee ID keys the manifest), EPIC (candidate Epic list on the Bee-ID path), GATE (Bee-pick / Epic-pick fires). Consumes from → EPIC (dependency-workability rules EX-EPIC-5..7 apply on the Bee-ID path), GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-BEE-1 | The user calls with no arguments, a Bee id, or an Epic ID; each has its own path. | definition | L94 Pick the Bee | E1-062 | - | skill arguments | none | no | procedure |
| EX-BEE-2 | No arguments: list all Plan Bees and ask which to work on, via `bees execute-freeform-query --query-yaml 'stages: - [type=bee, hive=plans] report: [title, ticket_status]'`. | gate | L96-102 | E1-063, E1-064 | Bee list | - | bees, AskUserQuestion | no | procedure |
| EX-BEE-3 | Filter to Bees with status `ready` or `in_progress` (workable). | precondition | L104 | E1-065 | workable-Bee list | EX-BEE-2 output | none | no | procedure |
| EX-BEE-4 | Exactly one workable Bee → use it without asking; multiple → present via `AskUserQuestion`; none → tell the user no Plan Bees are workable and suggest `/quo-plan` or `/quo-plan-from-specs`. | gate | L104 | E1-066, E1-067, E1-068 | Bee ID / user message | EX-BEE-3 | AskUserQuestion, TaskList | no | procedure |
| EX-BEE-5 | Bee ID given: find that Bee's `ready` Epic children with `bees execute-freeform-query --query-yaml 'stages: - [parent=<bee-id>, type=t1, status=ready] report: [title, up_dependencies]'` and ask which to start with. | gate | L106-112 | E1-069, E1-070 | Epic candidate list | `<bee-id>` | bees, AskUserQuestion | no | procedure |
| EX-BEE-6 | Present unblocked candidate Epics via `AskUserQuestion`, recommending the one with the fewest downstream dependencies first (workability per EX-EPIC-5..7). | gate | L121 | E1-075 | Epic choice | EX-EPIC-5..7 | AskUserQuestion, TaskList | no | procedure |
| EX-BEE-7 | Epic ID given: walk up to the parent Bee with `bees execute-freeform-query --query-yaml 'stages: - [id=<epic-id>] - [parent] report: [title, ticket_status]'` and use that Bee for the rest of the run. | command | L123-132 | E1-076, E1-077 | Bee ID | `<epic-id>` | bees | no | procedure |
| EX-BEE-8 | Every path yields the Bee ID; validate it is ready for work. | precondition | L134-135 | E1-078 | validated Bee ID | Bee ID | bees | no | procedure |
| EX-BEE-9 | The Bee must have status `ready` or `in_progress`. | precondition | L136 | E1-079 | - | Bee `ticket_status` | bees | no | procedure |
| EX-BEE-10 | If the Bee has `up_dependencies`, they must be `done`; a `ready` dependency is a pending blocker, not satisfied. | precondition | L137 | E1-080 | - | Bee `up_dependencies` statuses | bees | no | procedure |

---

## M05. Isolation strategy (`EX-ISO`)

- **Purpose:** Decide where commits land — an existing worktree (Scenario A) or, on a branch in the main repo (Scenario B), a user-chosen feature branch / current branch / worktree hand-off.
- **Failure it prevents:** not stated (implicit: commits landing on main without the user's consent).
- **Env deps:** git, AskUserQuestion, TaskList. TaskList-dependent: **yes** (the Scenario B gate).
- **Rows after dedupe:** 10 (procedure 8 · rationale 2 · example 0)
- **Literals:** `Scenario A — Already in a worktree` · `Scenario B — On an existing branch in the main repo` · `b_Wx7` / `b.Wx7` · `bee/b.Wx7` · `Create a feature branch (Recommended)` · `Work on current branch` · `Set up a worktree instead` · `/bees-worktree-add` · `/bees-fleet`
- **Cross-mechanism edges:** Produces for → MAN (`Isolation strategy` field enum), MERGE (advice keyed on the chosen strategy), GATE. Consumes from → GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-ISO-1 | Check whether you are running in an isolated context for this Bee's work; the text says "three scenarios" but defines only A and B. | precondition | L141 Validate isolation strategy | E1-081 | - | cwd, git state | git | unknown | procedure |
| EX-ISO-2 | Scenario A — already in a worktree (directory name matches the Bee, e.g. `b_Wx7` for `b.Wx7`): proceed directly, no action. Expected path when launched via `/bees-worktree-add` / `/bees-fleet`, if installed. | gate | L143 | E1-082, E1-083 | isolation = worktree | cwd name, Bee ID | git | unknown | procedure |
| EX-ISO-3 | Scenario B — on an existing branch in the main repo (user invoked `/quo-execute` directly): present an `AskUserQuestion` with the three options below. | gate | L145 | E1-084 | `gate-*` task, isolation choice | cwd, branch | AskUserQuestion, TaskList, git | unknown | procedure |
| EX-ISO-4 | Option 1 `Create a feature branch (Recommended)`: create a new branch (e.g. `bee/b.Wx7`) from current HEAD and do all work there. | choice-set | L147 | E1-085 | git branch | user answer | git | unknown | procedure |
| EX-ISO-5 | Rationale for option 1: keeps main clean; user can review, squash-merge or discard later. | rationale-only | L147 | E1-086 | - | - | none | unknown | rationale |
| EX-ISO-6 | Option 2 `Work on current branch`: commit directly to the checked-out branch and tell the user the branch name. Appropriate when already on a feature branch or intentionally committing on main. | choice-set | L148 | E1-088, E1-089 | isolation = current branch | user answer, branch name | git | unknown | procedure |
| EX-ISO-7 | Option 3 `Set up a worktree instead`: if `/bees-worktree-add` is installed, suggest the user run it to create an isolated worktree and spawn an async agent; exit after giving this advice — do not proceed with work. | choice-set | L149 | E1-090, E1-091 | user advice, clean exit | user answer | none | unknown | procedure |
| EX-ISO-8 | Omit option 3 if `/bees-worktree-add` is not installed (not part of the portable core). | choice-set | L149 | E1-092 | - | installed-skill check | none | unknown | procedure |
| EX-ISO-9 | Rationale: option 3 is the right choice for fire-and-forget execution in a separate tmux session. | rationale-only | L149 | E1-093 | - | - | none | unknown | rationale |
| EX-ISO-10 | In the Scenario B question always state the current working directory, the current branch name, and that option 1 creates a local branch only (no remote push). | field-or-template | L151-154 | E1-094 | question text | cwd, branch name | AskUserQuestion, git | unknown | procedure |

---
## M06. Run-state manifest incl. placeholder resolution (`EX-MAN`)

- **Purpose:** Keep the handful of run-scoped values with no other durable home (run mode, isolation strategy, pre-Bee SHA, tracker path, per-Epic progress, next unit) in a deterministic file so the run survives harness compaction.
- **Failure it prevents:** Losing the user's run-mode choice (no re-derivation path) or the randomly-suffixed tracker path after compaction; a `/quo-execute` run truncating a live `/quo-breakdown-epic` manifest.
- **Env deps:** Bash (mkdir), git (`rev-parse`), bees (Bee-ID recovery), Read/Write tools. TaskList-dependent: **no**.
- **Rows after dedupe:** 48 (procedure 37 · rationale 11 · example 0)
- **Literals:** `#### Write the run-state manifest` · `run-state-quo-execute-<bee-id>.md` · `/tmp/.quorum/run-state-quo-execute-<bee-id>.md` · `$env:TEMP\.quorum\run-state-quo-execute-<bee-id>.md` · `# Run state — quo-execute @ <bee-id>` · `**Skill:**` · `**Run started (UTC):**` · `**Unit scope:**` · `**Multi-Epic run mode:**` · `**Isolation strategy:**` · `**Pre-Bee SHA:**` · `**Compromise tracker:**` · `**Progress:**` · `**Next unit:**` · `Mode 1 (Stop after each Epic)` · `Mode 2 (Work through all Epics)` · `not captured (single Epic in scope)` · `not captured (all Epics already done)` · `not captured` · `pending Section 2 query` · `branch created: <name>` · `current branch: <name>` · `worktree: <path>` · `<epic-id>: done — last commit <sha>` · `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>` · `<bee-id>: Bee-level review aborted — <what stopped it>` · `git rev-parse HEAD` · `<pre-bee-sha>` · `<previous-epic-last-commit>` · `#### Resolve the manifest placeholders` · `Epics in scope`
- **Cross-mechanism edges:** Produces for → LOOP (fourth read-state source), CKPT (step 2 rewrites it; step 1 reads Pre-Bee SHA/Progress), NEXT (interaction step 1 lower bound), POST (Pre-Bee SHA), SUMM/TRK (tracker-path recovery), PCR (post-compaction re-read). Consumes from → BEE (Bee ID), ISO (strategy enum), EPIC (Epic query + mode gate resolve placeholders), TRK (tracker filename), ABORT (aborted Progress shapes via CKPT step 2).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-MAN-1 | `#### Write the run-state manifest` is the canonical definition site; later sections refer to it by name. | definition | L158 | E1-095 | - | - | none | yes | procedure |
| EX-MAN-2 | Write the manifest as the last step of Section 1, once Bee ID and isolation strategy are known and before any Epic work begins. | ordering | L158 | E1-096 | manifest file | Bee ID, isolation strategy | none | unknown | procedure |
| EX-MAN-3 | The manifest holds only run-scoped values that live nowhere else on disk (bees holds ticket state, git the diff, the tracker compromises, the `defer-*` TaskList deferrals); it carries only values with no other durable home. | invariant | L160, L186 | E1-097, E1-118 | - | - | none | yes | procedure |
| EX-MAN-4 | Do not add ticket titles, Subtask bodies, review findings, or anything already readable from bees, git, the tracker, or the TaskList. | invariant | L186 | E1-119 | - | - | none | yes | procedure |
| EX-MAN-5 | Rationale: duplicating carried values would grow the manifest into a shadow ticket store that drifts. | rationale-only | L186 | E1-120 | - | - | none | yes | rationale |
| EX-MAN-6 | After a compaction the orchestrator re-reads the manifest instead of trusting a summary; the manifest, not the conversation, is where mode and scope are read back. | recovery | L160; L275 | E1-098, E2-045 | - | manifest file | none | yes, no | procedure |
| EX-MAN-7 | Write under `<tempdir>/.quorum/` (`/tmp/.quorum/` POSIX, `%TEMP%\.quorum` Windows) per the scratch-file convention; create the dir if absent (`mkdir -p /tmp/.quorum` / `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`), then author via the `Write` tool (no shell redirect). | command | L162-174 | E1-099, E1-101, E1-102, E1-103 | `.quorum` dir, manifest file | - | Bash | yes | procedure |
| EX-MAN-8 | Canonical filename `run-state-quo-execute-<bee-id>.md`, `<bee-id>` = this run's Bee ID (e.g. `run-state-quo-execute-b.abc.md`); the loop `Read`s it at that path. | name-class | L162; L307 | E1-100, E2-064 | manifest path | Bee ID | none | no | procedure |
| EX-MAN-9 | The filename is deterministic — do NOT add a random suffix or timestamp. | invariant | L176 | E1-104 | - | - | none | yes | procedure |
| EX-MAN-10 | Rationale: the tracker's `<short-suffix>` suits a reader handed the path in a prompt; the manifest's reader is the post-compaction orchestrator, so a suffix is unfindable. | rationale-only | L176 | E1-105 | - | - | none | yes | rationale |
| EX-MAN-11 | The Bee ID is re-derivable without the conversation (run argument, `parent` of every Epic, grandparent of every Task), so the skill-name + Bee-ID path stays findable when nothing survives in conversation. | definition | L178; L307 | E1-106, E2-065 | - | - | none | no | rationale |
| EX-MAN-12 | An orchestrator that lost the conversation recovers the Bee ID from any in-flight Plans-hive ticket with one `bees show-ticket` / `bees execute-freeform-query` call. | recovery | L178 | E1-107 | Bee ID | in-flight Plans ticket | bees | no | procedure |
| EX-MAN-13 | Rationale: the Bee ID discriminates across projects — ticket IDs are minted per bees workspace. | rationale-only | L178 | E1-108 | - | - | none | no | rationale |
| EX-MAN-14 | The `quo-execute` segment discriminates across sibling skills; `/quo-breakdown-epic` keys its manifest on the same Bee ID. Without it a `/quo-execute` run would truncate a live `/quo-breakdown-epic` manifest — the sequence its *"In a fresh session, execute this Epic first; defer downstream breakdown"* option invites. | definition | L180 | E1-109, E1-110 | - | - | none | no | rationale |
| EX-MAN-15 | Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends. | invariant | L180 | E1-111 | - | - | none | yes | procedure |
| EX-MAN-16 | `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID; `/quo-fix-issue` appends the repo directory basename because batch membership is only recoverable from inside the manifest. | definition | L180 | E1-112 | - | - | none | yes | rationale |
| EX-MAN-17 | Accepted trade: two concurrent `/quo-execute` runs against the same Bee already collide over statuses and commits, so that case is unsupported. | rationale-only | L182 | E1-113 | - | - | none | no | rationale |
| EX-MAN-18 | Semantics: truncate at run start, rewrite at each boundary — a live snapshot, not an accumulating log. Write fresh at run start, overwriting any manifest left by a previous run against the same Bee. | invariant | L184 | E1-114, E1-115 | manifest file | - | none | yes | procedure |
| EX-MAN-19 | Rewrite the manifest in full at each Epic boundary per Section 4.2's Epic-boundary state-externalization checkpoint. | ordering | L184 | E1-116 | manifest rewrite | - | none | no | procedure |
| EX-MAN-20 | Title line `# Run state — quo-execute @ <bee-id>`; field `**Skill:**` fixed to `quo-execute`. | field-or-template | L189-191 | E1-121, E1-122 | manifest heading, `Skill` field | Bee ID | none | no | procedure |
| EX-MAN-21 | Field `**Run started (UTC):**` holds `<YYYY-MM-DDTHH:MM:SSZ>`. | field-or-template | L192 | E1-123 | `Run started` field | clock | none | unknown | procedure |
| EX-MAN-22 | Field `**Unit scope:**` holds `Bee <bee-id>; Epics in scope: <epic-id-1, epic-id-2, ... \| pending Section 2 query>`. | field-or-template | L193 | E1-124 | `Unit scope` field | Bee ID, §2 Epic query | none | no | procedure |
| EX-MAN-23 | Field `**Multi-Epic run mode:**` enum: `Mode 1 (Stop after each Epic)` \| `Mode 2 (Work through all Epics)` \| `not captured (single Epic in scope)` \| `not captured (all Epics already done)` \| `not captured`. | field-or-template | L194 | E1-125 | `Multi-Epic run mode` field | §2 mode gate | none | no | procedure |
| EX-MAN-24 | Field `**Isolation strategy:**` enum: `branch created: <name>` \| `current branch: <name>` \| `worktree: <path>`. | field-or-template | L195 | E1-126 | `Isolation strategy` field | EX-ISO-2/4/6 | none | unknown | procedure |
| EX-MAN-25 | Field `**Pre-Bee SHA:**` holds `<pre-bee-sha>`; capture it here at run start with `git rev-parse HEAD` (same on POSIX and PowerShell) — the only place the run records it. | field-or-template | L196, L205-215 | E1-127, E1-134, E1-136 | `Pre-Bee SHA` field | HEAD | git | no, unknown | procedure |
| EX-MAN-26 | Section 6's post-completion review reads `<pre-bee-sha>` back from the manifest. | definition | L205 | E1-135 | - | `Pre-Bee SHA` field | none | no | procedure |
| EX-MAN-27 | Field `**Compromise tracker:**` holds `<tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` — the tracker's full path including its random suffix. | field-or-template | L197, L217 | E1-128, E1-137 | `Compromise tracker` field | tracker filename | none | unknown | procedure |
| EX-MAN-28 | Recording the tracker path does not create the file; it is created only at its first append trigger. | definition | L217 | E1-139 | - | - | none | unknown | procedure |
| EX-MAN-29 | Rationale: the manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. | rationale-only | L217 | E1-140 | - | - | none | unknown | rationale |
| EX-MAN-30 | Field `**Progress:**` holds one bullet per unit finished, in the order worked, normal shape `<epic-id>: done — last commit <sha>`. | field-or-template | L198-199, L219 | E1-129, E1-141 | `Progress` entries | Epic completion | git | no | procedure |
| EX-MAN-31 | Field `**Next unit:**` holds `<next-epic-id \| none>`. | field-or-template | L200 | E1-130 | `Next unit` field | §2 Epic order | none | no | procedure |
| EX-MAN-32 | Bare `not captured` and `pending Section 2 query` are first-write-only literals written only at run start (mode and scope are unknown then); they must never survive past Section 2 / into any Epic's work. | definition | L203, L226; L268 | E1-131, E1-133, E1-152, E2-031 | first-write placeholders | - | none | no | procedure |
| EX-MAN-33 | Rewrite the manifest as soon as Section 2's Epic query has returned and the mode gate has fired or been skipped; the rewrite is unconditional on all three gate paths (including where the gate never fires) and replaces both first-write literals. | ordering | L203, L226; L268 Resolve the manifest placeholders | E1-132, E1-153, E2-029, E2-030 | manifest rewrite | Epic query result, gate outcome | none | no | procedure |
| EX-MAN-34 | Write **Epics in scope** as the real Epic IDs returned by the `[parent=<bee-id>, type=t1]` query, on every path. | field-or-template | L270 | E2-032 | `Epics in scope` field | Epic query result | none | no | procedure |
| EX-MAN-35 | Write **Multi-Epic run mode** as the captured choice whenever the gate fired at any point in this run; on a loop re-entry pass the gate does not re-fire and the mode already in the manifest is written back unchanged. | field-or-template | L271 | E2-033, E2-034 | `Multi-Epic run mode` field | captured mode / manifest | none | no | procedure |
| EX-MAN-36 | Only when the gate has never fired does the field take a skip literal, by precedence: `not captured (all Epics already done)` whenever every Epic reads `done`; `not captured (single Epic in scope)` only for exactly one not-yet-`done` Epic. | field-or-template | L271 | E2-035, E2-036, E2-037 | `Multi-Epic run mode` literal | Epic count/statuses | none | no | procedure |
| EX-MAN-37 | When a Bee holds exactly one already-`done` Epic, the all-done literal wins so the same Bee state always yields the same literal. | invariant | L271 | E2-038 | - | Epic count/status | none | no | rationale |
| EX-MAN-38 | On loop re-entry, carry accumulated fields forward — do not re-emit Section 1's template: `Read` the current manifest first, write back **Progress**, **Next unit**, **Isolation strategy**, **Pre-Bee SHA**, **Compromise tracker** and captured **Multi-Epic run mode** unchanged; touch only `Epics in scope` and `Multi-Epic run mode` (a two-field refresh, not a run-start write). | invariant | L273 | E2-039, E2-041, E2-042, E2-043 | manifest rewrite | manifest fields | none | no | procedure |
| EX-MAN-39 | Section 4.2 branch 2 returns to Section 2 for each subsequent Epic, so the placeholder rewrite runs again on every pass after the first. | definition | L273 | E2-040 | - | - | none | no | procedure |
| EX-MAN-40 | Rationale: re-emitting the blank template would blank **Progress** and **Next unit**, destroying the `last commit <sha>` values the checkpoint's step 1 reads as lower bound. | rationale-only | L273 | E2-044 | - | `last commit <sha>` | none | no | rationale |
| EX-MAN-41 | Two aborted Progress shapes exist, written by `##### Aborted-run close-out` through checkpoint step 2; which applies depends on the scope close-out step 2 resolved (aborted lane's scope, or the review site the routing gate's `Cancel` fired from). | definition | L219 | E1-142, E1-143 | `Progress` entries | close-out step 2 scope | none | no | procedure |
| EX-MAN-42 | Mid-Epic abort (per-Task writer lane, or `Cancel` at the per-Task review site) writes `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`, replacing the `done` entry the Epic never earned. | field-or-template | L221; L648 | E1-144, E3-148 | `Progress` entry | task id, last commit | git | no | procedure |
| EX-MAN-43 | Bee-level-review abort (Section 5 Bee-scoped re-dispatch, or `Cancel` at Section 5's review) appends `<bee-id>: Bee-level review aborted — <what stopped it>`; `<what stopped it>` names the aborted lane (e.g. `test-writer-b.abc`) or, on `Cancel`, the review site plus the finding (the same pair close-out step 3 states). | field-or-template | L222; L649 | E1-145, E1-146, E3-149 | `Progress` entry | Bee ID, lane name / site + finding | none | no | procedure |
| EX-MAN-44 | The Bee-level shape keys on the Bee id because every Epic finished and each `done — last commit <sha>` entry is correct; never overwrite a legitimately-`done` Epic entry with an aborted one. | invariant | L222; L649 | E1-147, E1-148, E3-150 | - | - | none | no | procedure |
| EX-MAN-45 | Progress is an in-run, pre-compaction record, not cross-session: a resuming `/quo-execute <bee-id>` truncates the manifest at run start; the aborted entry serves this run's post-compaction reader, not the next session. | definition | L224; L620 | E1-149, E3-112 | - | EX-MAN-18 | none | no | procedure |
| EX-MAN-46 | Readers of a Progress entry are this run's later Epic boundaries (checkpoint step 1 resolves `<previous-epic-last-commit>` from it) and a post-compaction orchestrator inside this run. | definition | L224 | E1-150 | - | `Progress` field | none | no | procedure |
| EX-MAN-47 | A later session learns where an aborted run stopped from bees ticket state plus landed commits, not from the manifest. | recovery | L224; L620 | E1-151, E3-111 | - | bees, git | bees, git | no | procedure |
| EX-MAN-48 | Rationale: the run mode is a user choice with no re-derivation path; if lost, the run cannot know whether to auto-continue. | rationale-only | L226 | E1-154 | - | - | none | no | rationale |

---

## M07. Epic selection, run-mode gate (Mode 1/2), staleness, status flips (`EX-EPIC`)

- **Purpose:** Pick the next workable Epic under the Bee, capture the one-time multi-Epic run mode, refresh stale Task/Subtask descriptions against prior Epics' actual diff, and flip the Epic to `in_progress`.
- **Failure it prevents:** Re-prompting for run mode at every Epic; treating a `ready` dependency as satisfied; dispatching workers against ticket text that no longer matches the tree.
- **Env deps:** bees, git, AskUserQuestion, TaskList. TaskList-dependent: **yes** (mode gate two-step).
- **Rows after dedupe:** 17 (procedure 17 · rationale 0 · example 0)
- **Literals:** `### 2. Find Epic to work on and validate` · `#### Pick a multi-Epic run mode (only when more than one Epic is in scope)` · `How should this run handle multiple Epics? (You will not be asked again this run.)` · `Stop after each Epic` · `Work through all Epics` · `multi-Epic run mode` · `stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status, up_dependencies]` · `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>` · `#### Check if stale` · `#### Mark status when ready to start work` · `status=in_progress` · `drafted`
- **Cross-mechanism edges:** Produces for → MAN (mode + Epics in scope), NEXT (branch-2 mode dispatch; re-query shares the same query), CKPT (checkpoint runs in Mode 2 too), GATE. Consumes from → BEE (Bee ID), GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-EPIC-1 | Find all Epics under the Bee with `bees execute-freeform-query --query-yaml 'stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status, up_dependencies]'` (same query re-run at each Epic boundary in Section 4.2) and recommend the best Epic to work first. | command | L232-238 §2; L593-597 §4.2 | E2-004, E2-005, E3-080 | Epic candidate set, recommendation | `<bee-id>` | bees, Bash | no | procedure |
| EX-EPIC-2 | The Epic to work on must have status `ready` or `in_progress`. | precondition | L240-241 | E2-006 | - | `ticket_status` | bees | no | procedure |
| EX-EPIC-3 | `up_dependencies` is returned as a list of ticket IDs only — not statuses. | definition | L114 §1; L244 §2; L599 §4.2 | E1-071, E2-008, E3-081 | - | query result | bees | no | procedure |
| EX-EPIC-4 | Collect dependency IDs across all candidate (or `ready`) Epics, then batch-look-up their statuses with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`. | command | L114-119 §1; L244-249 §2; L599 §4.2 | E1-072, E2-009, E3-082 | dependency statuses | `up_dependencies` IDs | bees, Bash | no | procedure |
| EX-EPIC-5 | An Epic is workable only if all its `up_dependencies` have `ticket_status` `done`; a `ready` dependency is a pending blocker. | invariant | L121 §1; L240-242, L251 §2 | E1-073, E2-007, E2-010 | workable-Epic list | dependency statuses | bees | no | procedure |
| EX-EPIC-6 | An Epic with no `up_dependencies` is unblocked by default. | invariant | L121 §1; L251 §2 | E1-074, E2-011 | - | `up_dependencies` | none | no | procedure |
| EX-EPIC-7 | Before starting the first Epic, count the Epics returned by the `[parent=<bee-id>, type=t1]` query — the full set (`drafted`/`ready`/`in_progress` plus already `done`), not just the workable subset. | precondition | L255 Pick a multi-Epic run mode | E2-012, E2-013 | Epic count | Epic query result | bees | no | procedure |
| EX-EPIC-8 | If two or more Epics exist and at least one is workable (`ready`/`in_progress`) or `drafted`, present a one-time mode choice via `AskUserQuestion`. | gate | L255 | E2-014 | AskUserQuestion call | Epic count, statuses | AskUserQuestion, TaskList | no | procedure |
| EX-EPIC-9 | If every Epic is already `done`, or only one Epic exists, skip the mode question entirely. | precondition | L255, L264 | E2-015, E2-028 | - | Epic statuses/count | none | no | procedure |
| EX-EPIC-10 | Section 4.2 branch 3 exits the run with no Epic boundary crossed when all Epics are `done` (as stated in §2 — see Inconsistencies: branch 3 actually proceeds to final review). | definition | L255 | E2-016 | - | - | none | no | procedure |
| EX-EPIC-11 | Question text: `How should this run handle multiple Epics? (You will not be asked again this run.)` | field-or-template | L257 | E2-017 | question text | - | AskUserQuestion | no | procedure |
| EX-EPIC-12 | Option `Stop after each Epic`: pause at every Epic boundary for review and approval of continuation. | choice-set | L259 | E2-018 | choice label | - | AskUserQuestion | no | procedure |
| EX-EPIC-13 | Option `Work through all Epics`: auto-continue across Epics; stop only when proceeding without input risks concrete downstream cost. | choice-set | L260 | E2-020 | choice label | - | AskUserQuestion | no | procedure |
| EX-EPIC-14 | Capture the choice once and store it as the **multi-Epic run mode** for the rest of the run; it persists across Epic boundaries — do not re-prompt at every Epic. | field-or-template | L262 | E2-025, E2-026 | `multi-Epic run mode` value | AskUserQuestion result | AskUserQuestion | no | procedure |
| EX-EPIC-15 | If the Epic has completed `up_dependencies`, review the work actually done in those Epics to check whether this Epic's description is stale. | precondition | L278-279 Check if stale | E2-046 | - | prior Epic work | bees, git | no | procedure |
| EX-EPIC-16 | Staleness steps: (1) review the git diff to understand what was implemented; (2) read the upcoming Epic and its Tasks/Subtasks; (3) update any Task/Subtask descriptions now stale (paths changed, signatures differ, new modules). | ordering | L281-283 | E2-047, E2-048, E2-049 | updated ticket bodies | git diff, ticket bodies | bees, git | no | procedure |
| EX-EPIC-17 | If ready, mark the Epic `status=in_progress` to show work has started. | command | L287 Mark status when ready to start work | E2-050 | Epic status flip | Epic readiness | bees | no | procedure |

---
## M08. Reconciliation loop & per-Subtask fan-out (`EX-LOOP`)

- **Purpose:** Drive Tasks through an event-driven Read-state → Reconcile → Yield loop that dispatches fresh ephemeral background Agents per Subtask and never polls.
- **Failure it prevents:** Clock-driven polling and warm-Agent assumptions the harness does not support; acting on stale conversation memory instead of the four authoritative sources.
- **Env deps:** Agent, bees, TaskList, git, Bash. TaskList-dependent: **yes**.
- **Rows after dedupe:** 24 (procedure 22 · rationale 2 · example 0)
- **Literals:** `### 3. Execute Tasks via per-Subtask Agent dispatch` · `#### Reconciliation loop` · `Read state` · `Reconcile` · `Yield` · `bees show-ticket --ids <epic-id>` · `children` · `stages: - [id=<ticket-id>] report: [title, ticket_status]` · `status!=drafted` · `run_in_background=true` · `Agent(subagent_type=<role>, run_in_background=true, prompt=…)` · `##### Anti-pattern: no clock primitives` · `/loop` · `ScheduleWakeup` · `CronCreate` · `#### Per-Subtask cold dispatch` · `Agent(name=...)` · `SendMessage` · `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` · `#### Hub-and-spoke via substrate` · `#### Recursive delegation: not supported`
- **Cross-mechanism edges:** Produces for → TL (one task per Agent), MOV (writer returns routed to the rung), PMD (advance when Subtasks done), NEXT (advance to 4.2 when Tasks done), DPS (dispatch prompt content). Consumes from → MAN (fourth read source), PCR (re-read rule), EDP (forward fan-out is exempt from part (g)).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-LOOP-1 | The orchestrator (Director) drives Tasks through a reconciliation loop dispatching fresh, ephemeral background `Agent` invocations against the sibling `agents/` custom subagent types; there is no long-lived team, no warmed Agents, no peer-to-peer messaging. | definition | L291 §3 | E2-051, E2-052 | Agent dispatches | `agents/` | Agent | unknown | procedure |
| EX-LOOP-2 | The loop is event-driven, not clock-driven; each tick has three phases: Read state, Reconcile, Yield. | definition | L295 | E2-053 | - | - | Agent | unknown | procedure |
| EX-LOOP-3 | Phase 1 (Read state): pull current truth from four sources — bees, TaskList, git state, run-state manifest — before deciding anything. | ordering | L297 | E2-054 | - | bees, TaskList, git, manifest | bees, TaskList, git | unknown | procedure |
| EX-LOOP-4 | Use `bees show-ticket --ids <epic-id>` to get the Epic's `children` (Task IDs); for each Task fetch full details incl. its `children` (Subtasks). | command | L298 | E2-055, E2-056 | Task/Subtask ID lists | `children` | bees | no | procedure |
| EX-LOOP-5 | Read every Subtask body (Context, What Needs to Change, Key Files, Acceptance Criteria) — they carry the instructions the dispatched Agent follows. | ordering | L298 | E2-057 | - | Subtask bodies | bees | no | procedure |
| EX-LOOP-6 | Sort Tasks in dependency order via each Task's `up_dependencies`. | ordering | L298 | E2-058 | ordered Task list | `up_dependencies` | bees | no | procedure |
| EX-LOOP-7 | Verify at least one Task exists with at least one Subtask and all are non-drafted (`status!=drafted`). | precondition | L298 | E2-059 | - | Task/Subtask statuses | bees | no | procedure |
| EX-LOOP-8 | Use `bees execute-freeform-query --query-yaml 'stages: - [id=<ticket-id>] report: [title, ticket_status]'` for any focused state query. | command | L298-304 | E2-060 | ticket status | `<ticket-id>` | bees, Bash | unknown | procedure |
| EX-LOOP-9 | Each in-flight Agent has a TaskList task whose status is `pending` (queued), `in_progress` (running) or `completed` (Agent reported done). | definition | L305 | E2-061 | - | TaskList | TaskList | unknown | procedure |
| EX-LOOP-10 | Git state (the diff on disk) is the only authoritative record of what workers actually did. | invariant | L306 | E2-062 | - | git diff | git | unknown | procedure |
| EX-LOOP-11 | The run-state manifest holds run mode, isolation strategy, `<pre-bee-sha>`, tracker path, per-Epic progress and next unit (read-state source four). | definition | L307 | E2-063 | - | manifest | none | no | procedure |
| EX-LOOP-12 | Mark the current Task `status=in_progress` and the Bee `status=in_progress` (if not already) the first time a Task starts. | command | L311 | E2-069 | Task and Bee status flips | - | bees | no | procedure |
| EX-LOOP-13 | Phase 2 (Reconcile): for every Subtask whose dependencies are satisfied and has no Agent in flight, dispatch a fresh Agent. | ordering | L313-314 | E2-070 | Agent dispatch | Subtask deps, TaskList | Agent, TaskList | no | procedure |
| EX-LOOP-14 | For every Agent that reported completion: confirm the bees ticket transitioned to `status=done`, mark its TaskList task `completed`, unlock newly-eligible downstream Subtasks. | ordering | L315 | E2-071 | TaskList flip; unlocks | completion notification; bees status | bees, TaskList, Agent | unknown | procedure |
| EX-LOOP-15 | When all Tasks of the current Epic are `done`, advance to the inter-Epic interaction checkpoint in Section 4.2. | ordering | L358 | E2-142 | - | Task statuses | bees | no | procedure |
| EX-LOOP-16 | Phase 3 (Yield): do not poll; after dispatching this tick's work return control to the harness and wait for the Agent completion notification (`run_in_background=true`) — that notification is the only legitimate trigger for the next tick. | ordering | L360, L371 | E2-143, E2-144, E2-149 | yield | - | Agent | unknown | procedure |
| EX-LOOP-17 | No clock primitives: do not use `/loop`, `ScheduleWakeup`, or `CronCreate`, and do not poll bees/TaskList/git on a sleep-wait cycle without a triggering event. | invariant | L364-369 Anti-pattern: no clock primitives | E2-145, E2-146, E2-147, E2-148 | - | - | none | unknown | procedure |
| EX-LOOP-18 | For each ready implementer Subtask spawn a fresh Agent at Subtask scope: `Agent(subagent_type=<role>, run_in_background=true, prompt=<dispatch prompt with the Subtask body embedded verbatim>)`, `<role>` ∈ `engineer` / `test-writer` / `doc-writer`. | command | L375-383 Per-Subtask cold dispatch | E2-150, E2-151 | Agent dispatch | Subtask body | Agent | no | procedure |
| EX-LOOP-19 | Each Subtask gets its own Agent invocation; the orchestrator does not name Agents (`Agent(name=...)` unused) and does not reuse an Agent across Subtasks. | invariant | L385 | E2-152, E2-153 | Agent dispatch | - | Agent | no, unknown | procedure |
| EX-LOOP-20 | No `SendMessage` between Subtasks; workers do not message each other — the orchestrator is the hub, each Agent a spoke that reads its prompt, edits files, exits; the diff is the handoff. | invariant | L385; L430 Hub-and-spoke via substrate | E2-154, E2-200 | - | - | Agent | unknown | procedure |
| EX-LOOP-21 | Rationale: hub-and-spoke is a structural property of ephemeral background Agents, not a rule the orchestrator enforces. | rationale-only | L430 | E2-201 | - | - | Agent | unknown | rationale |
| EX-LOOP-22 | The PM gets a new Agent at every per-Task review boundary; reviewers get a new Agent at every Bee-level review. | invariant | L387 | E2-155 | Agent dispatch | - | Agent | unknown | procedure |
| EX-LOOP-23 | Rationale: warm `SendMessage` dispatch needs `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and is unavailable; the cold-dispatch divergence from the SDD is intentional and tracked by a re-probe issue. | rationale-only | L391 Per-Subtask cold dispatch (vs SDD's warm-Agent intent) | E2-156 | - | - | none | unknown | rationale |
| EX-LOOP-24 | Subagents cannot spawn subagents; only the top-level orchestrator dispatches Agents (flat orchestration); every Agent invocation originates from this loop, never from a worker. | invariant | L434 Recursive delegation: not supported | E2-202, E2-203 | - | - | Agent | unknown | procedure |

---

## M09. Post-compaction recovery & context ownership (`EX-PCR`)

- **Purpose:** State that conversation memory is never authoritative, what to do when a summarization marker appears, and who owns context reclamation (the harness, via a fresh session — never the skill).
- **Failure it prevents:** Acting on a compacted summary; narrating a self-clear/self-compact the model cannot perform; gating on a self-estimated context percentage.
- **Env deps:** bees, TaskList, git (re-read). TaskList-dependent: **yes** (TaskList is one of the four sources re-read).
- **Rows after dedupe:** 8 (procedure 6 · rationale 2 · example 0)
- **Literals:** `Conversation memory is never a substitute for these four sources.` · summarization marker · `~25-30% of a 1M context window` · `fresh session` · `What this checkpoint does not do.`
- **Cross-mechanism edges:** Produces for → LOOP (re-read rule), CKPT (durable carriers exist because of this), CWG (external gauge is the only permitted reading). Consumes from → MAN, TL, TRK (the carriers).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-PCR-1 | Conversation memory is never a substitute for the four sources; re-read rather than recall ticket status, landed commits, run mode, pre-run SHA — unconditionally, on every tick, not only after something goes wrong. | invariant | L309 | E2-066, E2-067 | - | bees, TaskList, git, manifest | bees, TaskList, git | unknown | procedure |
| EX-PCR-2 | If a summarization marker is visible in the conversation, treat everything before it as non-authoritative and re-read all four sources in full before dispatching anything else. | recovery | L309 | E2-068 | - | marker; four sources | bees, TaskList, git | unknown | procedure |
| EX-PCR-3 | Orchestrator context grows monotonically within a session; nothing in this skill reclaims those tokens; the skill has no model-invocable way to clear or compact its own context — reclamation is owned by the harness. | definition | L436; L654 | E2-204, E2-205, E3-156 | - | - | none | unknown, no | rationale |
| EX-PCR-4 | The only reclamation lever is starting a fresh session at an Epic boundary (branch 1 recommends exactly that); the checkpoint makes that lever and any harness compaction lossless. | definition | L436; L654 | E2-207, E3-162 | - | - | none | no | procedure |
| EX-PCR-5 | The checkpoint does not clear, compact, or reclaim the orchestrator's context and must never be narrated as if it did. | invariant | L654 What this checkpoint does not do | E3-155 | - | - | none | no | procedure |
| EX-PCR-6 | A single Epic's working-set footprint is estimated at roughly `~25-30% of a 1M context window`; treat it as an unverified working estimate — never describe it as observed/measured/benchmarked; it is not a budget the skill measures or enforces. | definition | L654 | E3-157, E3-158 | - | - | none | no | rationale |
| EX-PCR-7 | The orchestrator must not invent or estimate its own remaining context from memory, report a self-measured usage percentage, or gate any branch on such a self-estimate. | invariant | L654 | E3-159 | - | - | none | no | procedure |
| EX-PCR-8 | Reading an out-of-band, machine-written context-usage gauge produced by a separate status-line process, and stopping at a boundary on it, is permitted — it is not a self-estimate; neither the read nor the stop reclaims context. | definition | L654 | E3-160, E3-161 | - | gauge file | none | no | procedure |

---

## M10. Movement-report rung & `aborted-*` markers (`EX-MOV`)

- **Purpose:** Recognise a Test/Doc Writer return that *stopped* on source movement, withhold the unit's advance behind a `pending` `aborted-<role>-<id>` marker, and re-dispatch the lane once the mover (Engineer / concurrent Test Writer perturbation / external actor) has settled.
- **Failure it prevents:** Marking an aborted writer `completed` and unlocking a per-Task PM review over unfinished tests or docs; a blind re-dispatch loop into a still-moving diff.
- **Env deps:** Agent, TaskList, bees, git. TaskList-dependent: **yes** (the marker is the whole mechanism).
- **Rows after dedupe:** 33 (procedure 30 · rationale 3 · example 0)
- **Literals:** `aborted-<role>-<id>` · `aborted-test-writer-<subtask-id>` · `aborted-doc-writer-<subtask-id>` · `aborted-<role>-<bee-id>` · `aborted-<role>-<subtask-id>` · `aborted-<role>-postcomp-<n>` · `metadata.activity` · `test-writer-<subtask-id>` · `doc-writer-<subtask-id>` · `<role>-<bee-id>` · `-r<n>` · `bees update-ticket --ids <subtask-id> --status in_progress` · `## Perturbations` · `None` · `git rev-parse HEAD` · `git hash-object` · `Movement report from a Test Writer or Doc Writer.` · `Bee-scoped case — the bees corrective is a no-op.`
- **Cross-mechanism edges:** Produces for → PMD (advance guard), BEEREV (Bee-level loop-close guard), CLEAN/BEEREV/ABORT (markers swept by prefix), UMG (unexplained branch), TL (name class), POST (carry-over onto postcomp names). Consumes from → LOOP (writer returns), DPS (fingerprint list, `## Files changed`), EDP (ordering after movement), `agents/test-writer.md` / `agents/doc-writer.md` (writer-side half).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-MOV-1 | A Test Writer or Doc Writer return reporting it *stopped* on detected source movement is not a completion; route it through the movement-report rung; it unlocks nothing. | invariant | L315 | E2-072 | - | writer return | Agent | unknown | procedure |
| EX-MOV-2 | The rung closes the writer's own TaskList task but opens an `aborted-*` task in its place; the Task does not advance while that task is `pending`. | invariant | L315 | E2-073 | `aborted-*` task | - | TaskList | unknown | procedure |
| EX-MOV-3 | `agents/test-writer.md` / `agents/doc-writer.md` instruct the writer to stop mid-run and report when the source its work was pinned to moved; the Test Writer fingerprints with `git rev-parse HEAD` + `git hash-object` at start and before finishing; the Doc Writer (no `Bash`) re-reads with `Read`/`Grep`. | definition | L316 | E2-074, E2-075 | - | writer return | git | unknown | procedure |
| EX-MOV-4 | Rationale: without a receiver the orchestrator would mark the task `completed` and unlock a per-Task PM review over unfinished tests or docs. | rationale-only | L316 | E2-076 | - | - | none | unknown | rationale |
| EX-MOV-5 | Read the writer's return before persisting anything. | ordering | L318 | E2-077 | - | writer return | Agent | unknown | procedure |
| EX-MOV-6 | Execute-mode narrowing: movement confined to a sibling Subtask's own files is designed concurrency — the writer records it as an observation and finishes normally; persist that as a completed return and carry the observation into the Task summary. | definition | L318 | E2-078, E2-079 | Task summary entry | writer return | TaskList, bees | no | procedure |
| EX-MOV-7 | A movement report is the case where the writer *stopped* because the files its own Subtask pins moved; what distinguishes it from an observation is whether the writer stopped, not whether it mentioned movement. | definition | L318 | E2-080, E2-081 | - | writer return | none | unknown | procedure |
| EX-MOV-8 | Do NOT unlock anything downstream of an aborted writer lane — it has not delivered. | invariant | L320 | E2-082 | - | - | TaskList | unknown | procedure |
| EX-MOV-9 | Record the owed redelivery as a durable TaskList entry — the same obligation-as-pending-task pattern `defer-*` and `gate-*` use. | ordering | L320 | E2-083 | `aborted-*` task | - | TaskList | unknown | procedure |
| EX-MOV-10 | Rung step 1: mark the writer's own TaskList task `completed` — `test-writer-<subtask-id>` / `doc-writer-<subtask-id>` (or `<role>-<bee-id>` for a Section 5 re-dispatch), including any `-r<n>` suffix — without a `status=done`; the delivery obligation moves to the `aborted-*` task. | ordering | L322; L463; L882 | E2-084, E2-236, E4-196 | TaskList status flip | writer task name | TaskList | unknown, no | procedure |
| EX-MOV-11 | Rationale: the writer's Agent has exited, so an active task would strand a task no completion notification will ever clear. | rationale-only | L322 | E2-085 | - | - | TaskList | unknown | rationale |
| EX-MOV-12 | Rung step 2: create a new `aborted-<role>-<id>` task matching the aborted lane's scope — `aborted-<role>-<subtask-id>`, `aborted-<role>-<bee-id>`, or `aborted-<role>-postcomp-<n>` (e.g. `aborted-test-writer-t3.abc.def.ij`, `aborted-doc-writer-b.abc`) — status `pending`, with the writer's "how far I got" report as `metadata.activity`. | name-class | L323; L477 | E2-086, E2-087, E2-258, E2-260 | `aborted-*` task | writer return, lane scope | TaskList | unknown | procedure |
| EX-MOV-13 | The `pending` `aborted-*` task is the redelivery-owed marker; the orchestrator reads it off the TaskList next tick rather than holding it in conversation. | invariant | L323 | E2-088 | - | TaskList | TaskList | unknown | procedure |
| EX-MOV-14 | Routing tests the `aborted-*` task's name prefix and status; `metadata.activity` is informational only, never a routing input. | invariant | L323 | E2-089 | - | task name, status | TaskList | unknown | procedure |
| EX-MOV-15 | Rung step 3: the Task must not advance (to per-Task PM review) while any `aborted-*` task for it is `pending`; the guard matches on the `aborted-` prefix plus status. A Subtask-scoped marker holds its parent Task's advance; a Bee-scoped marker holds Section 5's loop from closing. | invariant | L324, L357; L477; L882 | E2-090, E2-141, E2-262, E4-199 | - | `aborted-*` status | TaskList | unknown, no | procedure |
| EX-MOV-16 | The aborted lane's bees Subtask must not reach `status=done`; a flip set by the writer or by the orchestrator per `agents/doc-writer.md`'s no-`Bash` routing is premature. | invariant | L324 | E2-091 | - | Subtask status | bees | unknown | procedure |
| EX-MOV-17 | When the premature `done` flip already landed, undo it with `bees update-ticket --ids <subtask-id> --status in_progress` (identical on POSIX and PowerShell). | recovery | L324-334 | E2-092 | Subtask status flip | Subtask status | bees, Bash | unknown | procedure |
| EX-MOV-18 | `agents/test-writer.md` orders its closing fingerprint before the `done` flip and forbids the flip on abort, so the correction is rare; run it when state says otherwise, do not assume. | precondition | L336 | E2-093 | - | Subtask status | bees | unknown | procedure |
| EX-MOV-19 | Bee-scoped case: when the aborted lane was a Section 5 re-dispatch (`test-writer-<bee-id>` / `doc-writer-<bee-id>`), the bees corrective is a no-op — skip it; such lanes answer a Bee-level finding spanning the whole diff and carry no `t3` ticket. | precondition | L338 | E2-094, E2-095 | - | lane scope | bees | unknown | procedure |
| EX-MOV-20 | On the Bee-scoped path do not hunt for a Subtask to demote, and do not demote a Task or Epic the Bee-level diff touches. | invariant | L338 | E2-096 | - | - | bees | unknown | procedure |
| EX-MOV-21 | The Bee-scoped `aborted-<role>-<bee-id>` marker holds Section 5's review loop from closing; the review loop has not closed while any such marker is `pending` — re-dispatch that lane and let it deliver before closing. That gate is TaskList-derived so the marker alone is the mechanism. | invariant | L338; L920 §5 | E2-097, E5-061, E5-062 | writer re-dispatch | `aborted-*` status | TaskList, Agent | unknown, no | procedure |
| EX-MOV-22 | Re-dispatch the aborted lane according to who moved the source: an Engineer, a concurrently-dispatched Test Writer, or an external actor. | ordering | L340 | E2-098 | re-dispatch | movement attribution | Agent | unknown | procedure |
| EX-MOV-23 | Mover = Engineer: let that Engineer's lane finish, and — when the movement came from a review-finding re-dispatch — let the code review for that site close per part (g)'s ordering (Clause 1: the per-Task PM's in-flight `/quo-engineer-review` pass; Clause 2: the Bee-level Code Reviewer over the whole Bee's diff) before re-dispatching the writer; the review-round wait is elided when that round was the final `trivial-tweak` nit pass. | ordering | L342; L884 Ordering after a movement report | E2-099, E2-100, E2-101, E2-102, E4-200, E4-201, E4-202, E4-203 | writer re-dispatch | Engineer return, review close | Agent, TaskList | unknown, no | procedure |
| EX-MOV-24 | Rationale: re-dispatching a writer into a still-moving diff reproduces the abort. | rationale-only | L342 | E2-103 | - | - | none | unknown | rationale |
| EX-MOV-25 | Section 3's Reconcile step carries the receiver (recognition, what is withheld); part (g) carries only the ordering of the following re-dispatch. | definition | L884 | E4-204 | - | - | none | no | procedure |
| EX-MOV-26 | The concurrently-dispatched Test Writer candidate set is any sibling Subtask's Test Writer, or the Bee-scoped `test-writer-<bee-id>` when the aborted lane is a Section 5 re-dispatch (Section 5 can run `test-writer-<bee-id>` and `doc-writer-<bee-id>` concurrently). | definition | L343 | E2-105, E2-106 | - | in-flight/returned Test Writers | Agent | unknown | procedure |
| EX-MOV-27 | `agents/test-writer.md` sanctions perturbing a source file in place with `Edit`/`Write` (restoring from a scratch copy) and requires its return to list every perturbed path under `## Perturbations`, `None` when none. | definition | L343 | E2-107 | - | Test Writer return | none | unknown | procedure |
| EX-MOV-28 | Read `## Perturbations` on the held Test Writer returns: when one lists every moved path, re-dispatch the aborted lane once that sibling has returned, with no gate; when it covers only some paths, fall through to the external-actor case for the remainder. | ordering | L343 | E2-108, E2-109 | re-dispatch | `## Perturbations` | Agent | unknown | procedure |
| EX-MOV-29 | When a concurrently-dispatched Test Writer has not returned yet, do not classify and do not fire the gate; wait for its completion notification and classify on that tick. Once all have returned and none lists the moved path, fall through to the external-actor case. | ordering | L343 | E2-110, E2-111 | - | in-flight status | Agent | unknown | procedure |
| EX-MOV-30 | Mover = external actor: re-dispatch the writer once the movement is understood — the orchestrator has read the current diff and sees the tree has settled; when unexplained, fire the unexplained-movement gate instead of re-dispatching into it. | ordering | L344 | E2-112, E2-113 | re-dispatch / gate | git diff, attribution | git, Agent, AskUserQuestion, TaskList | unknown | procedure |
| EX-MOV-31 | The writer re-dispatch takes the next `-r<n>` round-discriminated name per the naming convention; carry the "how far I got" report (the `aborted-*` task's `metadata.activity`) into the re-dispatch prompt. | name-class | L346 | E2-114, E2-115 | `<role>-<id>-r<n>` task, prompt content | `aborted-*` `metadata.activity` | Agent, TaskList | unknown | procedure |
| EX-MOV-32 | When the re-dispatched lane (`<role>-<subtask-id>-r<n>` / `<role>-<bee-id>-r<n>` / `<role>-postcomp-<n>-r<k>`) returns a normal deliverable, mark the `aborted-*` task `completed` — that releases the advance. | ordering | L346; L477 | E2-116, E2-263 | `aborted-*` flip | re-dispatched return | TaskList | unknown | procedure |
| EX-MOV-33 | If the re-dispatched lane aborts again, repeat the rung from the top: mark its own `-r<n>` task `completed` and refresh the existing `aborted-*` task's `metadata.activity`, never creating a second. An `aborted-*` marker is not an Agent task: the one-task-per-Agent rule and `-r<n>` do not apply to it. | recovery | L346; L477 | E2-117, E2-261 | TaskList updates | writer return | TaskList | unknown | procedure |

---

## M11. Unexplained-movement gate (`EX-UMG`)

- **Purpose:** When no dispatched Engineer, no returned Test Writer's `## Perturbations`, and nothing in flight accounts for a writer's reported movement, put the decision to the operator instead of re-dispatching blindly.
- **Failure it prevents:** A blind re-dispatch loop into unexplained movement; re-firing the gate on sibling-lane notifications during `Wait`.
- **Env deps:** AskUserQuestion, TaskList, Agent, bees. TaskList-dependent: **yes**.
- **Rows after dedupe:** 15 (procedure 15 · rationale 0 · example 0)
- **Literals:** `Unexplained-movement gate.` · `Re-dispatch the writer now` · `Wait` · `Abort this unit` · one-line statement `the orchestrator dispatched no Engineer for this unit while the writer was running, and no returned concurrently-dispatched Test Writer's \`## Perturbations\` list names the moved paths, so it cannot attribute the movement.` · `Type something.` · `Chat about this`
- **Cross-mechanism edges:** Produces for → ABORT (`Abort this unit` is one of its three entering branches), MOV (re-dispatch), GATE. Consumes from → MOV (attribution failure), POST (re-used with "abort this follow-up lane" reading).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-UMG-1 | Movement is unexplained when no dispatched Engineer's files overlap the writer's Subtask over the reported window, no returned Test Writer's `## Perturbations` covers the paths, none remain in flight, and the orchestrator cannot otherwise account for the change. | definition | L348 | E2-118 | - | dispatch history; `## Perturbations`; git diff | Agent, git | unknown | procedure |
| EX-UMG-2 | Do not re-dispatch blindly into unexplained movement — the blind re-dispatch loop is the failure mode this branch prevents. | invariant | L348 | E2-119 | - | - | none | unknown | procedure |
| EX-UMG-3 | Fire via the two-step contract (create `gate-askuserquestion-<short-suffix>` naming this gate, then `AskUserQuestion` in the same turn); do not narrate the gate; do not yield while the `gate-*` task is `pending`/`in_progress`. | gate | L348 | E2-120, E2-121, E2-122 | `gate-*` task; AskUserQuestion | - | TaskList, AskUserQuestion | unknown | procedure |
| EX-UMG-4 | Question text carries the writer's movement report verbatim (files moved, opening/closing HEAD when HEAD moved, how far the work got) plus the one-line statement that no Engineer was dispatched for this unit and no returned Test Writer's `## Perturbations` names the moved paths, so movement cannot be attributed. | field-or-template | L350 | E2-123, E2-124 | question text | writer movement report | AskUserQuestion | unknown | procedure |
| EX-UMG-5 | Offer exactly three options; multi-choice only — no fake free-text options duplicating `Type something.` / `Chat about this`. | choice-set | L350 | E2-125 | option list | - | AskUserQuestion | unknown | procedure |
| EX-UMG-6 | `Re-dispatch the writer now`: movement understood or accepted; re-dispatch under its next `-r<n>` name against the current tree. | choice-set | L352 | E2-126 | re-dispatch | answer | AskUserQuestion, Agent | unknown | procedure |
| EX-UMG-7 | `Wait`: operator resolves the external change first; the orchestrator yields control. | choice-set | L353 | E2-127 | yield | answer | AskUserQuestion | unknown | procedure |
| EX-UMG-8 | After `Wait`, re-fire this gate only on the operator's reply — never on an Agent notification; the rule derives from the tick's trigger and needs no bookkeeping. | invariant | L353 | E2-128, E2-131 | fresh gate | operator reply | AskUserQuestion, TaskList | unknown | procedure |
| EX-UMG-9 | Do not read `Wait` as "no Agent in flight": sibling lanes can return seconds later; such a notification is a tick that processes that lane normally through Reconcile (persist, mark `completed`, unlock) and MUST NOT re-fire this gate. | invariant | L353 | E2-129, E2-130 | normal lane processing | completion notification | Agent, TaskList | no | procedure |
| EX-UMG-10 | Do not record the Wait state in `metadata.activity` and route on it — informational only. | invariant | L353 | E2-132 | - | - | TaskList | unknown | procedure |
| EX-UMG-11 | During Wait the `aborted-*` task stays `pending`, so the Task's advance stays shut. | invariant | L353 | E2-133 | - | `aborted-*` status | TaskList | unknown | procedure |
| EX-UMG-12 | `Abort this unit`: leave every bees ticket at the status the abort found it at and do not advance; for a Subtask-scoped lane this holds back the Subtask and its Task; for a Section 5 Bee-scoped lane there is nothing to hold back (every ticket legitimately `done`) and the Bee-level review stops. | choice-set | L354 | E2-134, E2-135 | - | answer, lane scope | AskUserQuestion, bees | unknown | procedure |
| EX-UMG-13 | On Abort do not simply stop: route the exit through Section 4.2's `##### Aborted-run close-out`, which sweeps per-Task and (where Bee-scoped) Bee-level names incl. the `aborted-*` marker, runs the checkpoint on its aborted path, and stops naming `/quo-execute <bee-id>`. | ordering | L354 | E2-136, E2-137 | close-out | - | TaskList | no | procedure |
| EX-UMG-14 | Mark the `gate-*` task `completed` the moment the answer is consumed and the branch entered — including on Wait, where consuming means yielding. | ordering | L356 | E2-138 | `gate-*` flip | answer | TaskList | unknown | procedure |
| EX-UMG-15 | The re-fire after Wait creates a fresh `gate-askuserquestion-<short-suffix>` task rather than reusing the closed one. | name-class | L356 | E2-139 | fresh `gate-*` task | - | TaskList | unknown | procedure |

---
## M12. Dispatch prompt shape (`EX-DPS`)

- **Purpose:** Fix what every dispatch prompt carries — the ticket body verbatim, the Test Writer's `## Source paths to fingerprint` list, the orchestrator-side no-Engineer wording (never a freeze), and the Engineer's completeness evidence relayed to PM and Code Reviewer.
- **Failure it prevents:** Paraphrase corrupting identifiers the worker uses literally; a writer fingerprinting the wrong set (or an empty heading read as a supplied set); `/quo-engineer-review` silently losing its sweep-verification check when a sweep is not named.
- **Env deps:** Agent, bees, Bash, git, TaskList. TaskList-dependent: **yes** (one row only — EX-DPS-3 names TaskList as the progress signal; no dispatch-prompt rule reads TaskList state).
- **Rows after dedupe:** 32 (procedure 25 · rationale 7 · example 0)
- **Literals:** `##### Dispatch prompt: quote the ticket body verbatim` · `bees show-ticket --ids <ticket-id>` · `## Files changed` · `## Source paths to fingerprint` · `git diff --name-only HEAD` · `"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running"` · `"no Engineer Agent will be dispatched for this Bee while you are running"` · `"the source tree is frozen"` · `## Engineer's completeness evidence` · `sweep-shaped` · `existed but is unavailable post-compaction` · `engineer-<bee-id>`
- **Cross-mechanism edges:** Produces for → LOOP (prompt), MOV (fingerprint list drives the writer's stop rule), PMD/BEEREV (completeness relay). Consumes from → LOOP (Engineer returns held), `agents/engineer.md` / `agents/test-writer.md` / `agents/doc-writer.md` / `agents/code-reviewer.md` / `agents/pm.md`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-DPS-1 | Read the ticket via `bees show-ticket --ids <ticket-id>` and embed the returned body verbatim as a quoted block; do not summarise, paraphrase, or "clean up" identifier spellings — paraphrasing corrupts names the worker uses literally. | invariant | L395 | E2-157, E2-158, E2-159 | dispatch prompt | ticket body | Agent, bees, Bash | unknown | procedure |
| EX-DPS-2 | Framing prose around the quoted block (e.g. "your gating precondition is met — start now") is fine; the body stays untouched. | definition | L395 | E2-160 | - | - | Agent | unknown | procedure |
| EX-DPS-3 | The prompt need not ask the worker to ping back; completion notifications are automatic and TaskList is the progress signal. | definition | L395 | E2-161 | - | - | Agent, TaskList | unknown | procedure |
| EX-DPS-4 | Test Writer dispatch: supply the fingerprint path list by carrying forward the Engineer return's `## Files changed` list (which `agents/engineer.md` requires on every Engineer return), not by re-deriving from the tree. | relay | L397 | E2-162, E2-163 | prompt heading | Engineer return | Agent | unknown | procedure |
| EX-DPS-5 | Supply the paths under a labelled `## Source paths to fingerprint` heading, one repository-relative path per line, test paths dropped; scope the list to the lane being dispatched (Subtask- vs Bee-scoped). | field-or-template | L397 | E2-164, E2-165 | `## Source paths to fingerprint` | `## Files changed` | Agent | unknown | procedure |
| EX-DPS-6 | Subtask-scoped Test Writer: the list is resolved, never assumed (a test Subtask has no Engineer diff of its own). Primary rule = parent Task's union: `bees show-ticket --ids <subtask-id>` → `parent`; `bees show-ticket --ids <task-id>` → `children`; union the `## Files changed` lists from Engineer returns for that Task's implementation Subtasks. | command | L399 | E2-166, E2-167 | fingerprint list | `parent`, `children`, Engineer returns | bees, Bash | no | procedure |
| EX-DPS-7 | Narrow the union to the `up_dependencies`-named implementation Subtasks when — and only when — the test Subtask's own `up_dependencies` is non-empty; an empty `up_dependencies` is legal and yields the unnarrowed union, not an empty list and not the working-tree fallback. | precondition | L399 | E2-168, E2-169 | narrowed list | test Subtask `up_dependencies` | bees | no | procedure |
| EX-DPS-8 | Implementation Subtasks under other Tasks are designed sibling concurrency and stay out of the list either way. | invariant | L399 | E2-170 | - | - | none | no | procedure |
| EX-DPS-9 | Limitation: the union covers only the Engineer returns held at dispatch time; a same-Task implementation Subtask still in flight contributes nothing. | definition | L399 | E2-171 | - | held Engineer returns | Agent | no | procedure |
| EX-DPS-10 | Paths that entered the union from a same-Task sibling implementation Subtask are supplied, so movement in them is anomalous to the writer like any supplied path; treat a writer stop-report naming such a path as legitimate rather than dismissing it as sibling concurrency. | invariant | L399 | E2-172, E2-173 | - | writer return | none | no | procedure |
| EX-DPS-11 | Bee-scoped Test Writer (Section 5 re-dispatch): the list is the union of changed-file lists from every Engineer return behind the Bee-level diff, including Bee-scoped `engineer-<bee-id>` rounds. | field-or-template | L400 | E2-174 | fingerprint list | Engineer returns | Agent | unknown | procedure |
| EX-DPS-12 | Fallback when an Engineer return did not list files: derive the set with `git diff --name-only HEAD` (same on POSIX/PowerShell) and drop test paths. | recovery | L402-412 | E2-175 | fingerprint list | git working tree | git, Bash | unknown | procedure |
| EX-DPS-13 | The fallback is the last resort, applying only when the dispatched scope yields no usable Engineer-supplied list at all (no return, or every return omitted `## Files changed`); not because the `up_dependencies` narrowing selected nothing; and when only some in-scope returns carried a list, union those and do not fall back. | precondition | L414 | E2-176, E2-177, E2-178 | fingerprint list | Engineer returns | git | unknown, no | procedure |
| EX-DPS-14 | An explicitly-empty `## Files changed` list is a list, not a missing one; a research-only Engineer pass contributes nothing and does not trigger the fallback. | invariant | L414 | E2-179 | - | Engineer return | none | unknown | procedure |
| EX-DPS-15 | Rationale: in execute mode the fallback reads the whole working tree and can include a sibling Subtask's concurrent edits, which the writer may stop on. | rationale-only | L414 | E2-180 | - | - | git | no | rationale |
| EX-DPS-16 | Omit the `## Source paths to fingerprint` heading rather than emitting an empty one — both when no usable list exists and the fallback yields nothing outside the writer's own test files, and when every in-scope return carried a list but the union is empty. | invariant | L414 | E2-181, E2-182 | dispatch prompt | fingerprint list | Agent | unknown | procedure |
| EX-DPS-17 | Rationale: `agents/test-writer.md`'s empty-path-set clause keys on the heading being absent; an empty heading would read as a supplied set. | rationale-only | L414 | E2-183 | - | - | none | unknown | rationale |
| EX-DPS-18 | Writer prompts MAY state the orchestrator-side rule scoped to the lane — Subtask-scoped: `"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running"`; Bee-scoped (Section 5): `"no Engineer Agent will be dispatched for this Bee while you are running"`. Keep the scoping qualifier: the Subtask promise cannot be widened (a sibling-Subtask Engineer may run concurrently), and the role files' execute-mode branch expects these wordings. | field-or-template | L416 | E2-184, E2-185, E2-186, E2-187 | prompt text | lane scope | Agent | no, unknown | procedure |
| EX-DPS-19 | Prompts MUST NOT claim `"the source tree is frozen"` or any paraphrase promising files will not move. | invariant | L416 | E2-188 | - | - | Agent | unknown | procedure |
| EX-DPS-20 | Rationale: the orchestrator cannot prevent the user, a second session or a background process from editing the tree; a freeze phrasing promises a lever it does not hold. | rationale-only | L416 | E2-189 | - | - | none | unknown | rationale |
| EX-DPS-21 | The writer-side half (capture tree state, re-check, stop and report) lives in `agents/test-writer.md` / `agents/doc-writer.md`, so recovery does not depend on prompt wording. | definition | L416 | E2-190 | - | - | none | unknown | rationale |
| EX-DPS-22 | `agents/engineer.md` requires an Engineer return to carry a completeness check with evidence whenever its Subtask was sweep-shaped (directed a change at every site where some property holds); a completeness list = the search patterns run, every hit, and per hit the change made or the reason it is deliberately untouched. | definition | L453 §3; L898 §5 | E2-224, E5-008, E5-011 | - | Engineer return | Agent | unknown, yes | procedure |
| EX-DPS-23 | When any Engineer return for the scope carried a completeness list, the per-Task PM dispatch prompt and (widened to Bee scope) the Code Reviewer dispatch prompt MUST embed every list verbatim under a labelled heading — recommended/required label `## Engineer's completeness evidence` — attributing each list to its Subtask when more than one Engineer contributed. | relay | L453 §3; L898 §5 | E2-225, E2-227, E5-004, E5-005 | `## Engineer's completeness evidence` | Engineer completeness lists | Agent | unknown, yes | procedure |
| EX-DPS-24 | Embed the lists as text in the prompt — do NOT write them to a scratch file and pass a path. | invariant | L453; L898 | E2-226, E5-007 | - | - | Agent | unknown, yes | procedure |
| EX-DPS-25 | Embed the same lists verbatim in any `pm-<bee-id>` re-dispatch prompt under the same heading: the Bee-scoped PM needs its own copy because `agents/pm.md` drives `/quo-engineer-review` via the `Skill` tool; relaying to the Code Reviewer does not cover it. | relay | L898 | E5-006, E5-018 | PM prompt content | Engineer completeness lists | Agent | unknown | procedure |
| EX-DPS-26 | Separately from the lists, state in the prompt that the assignment was sweep-shaped whenever it was, list or no list; at Bee scope name every sweep-shaped Subtask assignment from the Epic loop. | relay | L453; L898 | E2-228, E5-010, E5-013 | prompt statement | Subtask body shape | Agent | unknown, yes, no | procedure |
| EX-DPS-27 | Rationale: `/quo-engineer-review` reports a missing list only when the invocation named the assignment sweep-shaped, so an unnamed sweep silently loses the check. | rationale-only | L453; L898 | E2-229, E5-012 | - | - | none | unknown, yes | rationale |
| EX-DPS-28 | When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one — but still state sweep-shapedness when it applies. | invariant | L453; L898 | E2-230, E5-019 | prompt | Engineer returns | Agent | unknown, yes | procedure |
| EX-DPS-29 | Rationale: the evidence has no other carrier once the Engineer Agent exits, and `/quo-engineer-review`'s sweep-verification check needs it. | rationale-only | L898 | E5-009 | - | - | none | yes | rationale |
| EX-DPS-30 | Post-compaction qualification (Bee-level relay only): state `sweep-shaped` on its own only when the list is in hand or the Engineer genuinely returned none; when a sweep-shaped Task's Engineer return is unreadable post-compaction, state that a completeness list existed but is unavailable post-compaction, naming the Subtask. | relay | L898 | E5-014, E5-015 | prompt statement | compaction state | Agent | no | procedure |
| EX-DPS-31 | Rationale: the per-Task PM dispatch needs no such qualification because it composes its prompt while the Engineer's return is in hand. | rationale-only | L898 | E5-016 | - | - | none | no | rationale |
| EX-DPS-32 | `agents/code-reviewer.md` carries the reviewer-side half: passing the list into its `/quo-engineer-review` invocation. | definition | L898 | E5-017 | - | - | none | yes | procedure |

---

## M13. Roles & lane boundaries (`EX-ROLES`)

- **Purpose:** Name the seven dispatched roles, point at their contract files as authoritative, and forbid dispatch prose that loosens a role's lane.
- **Failure it prevents:** A prompt-level "you may also write tests" carve-out that papers over a coordination gap the orchestrator should resolve by dispatch.
- **Env deps:** Agent, bees. TaskList-dependent: **no**.
- **Rows after dedupe:** 15 (procedure 13 · rationale 1 · example 1)
- **Literals:** `#### Roles dispatched by the orchestrator` · `agents/engineer.md` · `agents/test-writer.md` · `agents/doc-writer.md` · `agents/pm.md` · `agents/code-reviewer.md` · `agents/test-reviewer.md` · `agents/doc-reviewer.md` · `### Feature: <title>` · `## Cumulative project doc updates` · `### Resolving reference_materials entries` · `reference_materials` · `file-path` · `bees` resolver · `t1=Doc` · `Does NOT modify source code, tests, or docs` · `Does NOT review <other-lanes>` · `Opus (always)`
- **Cross-mechanism edges:** Produces for → DPS (no-loosening constraint on framing prose), BEEREV (reviewer roles). Consumes from → PRE (registered types), CLAUDE.md `## Documentation Locations`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-ROLES-1 | Framing prose MUST NOT loosen the role boundaries in the dispatched role's contract file (`agents/<role>.md`); applies to every dispatched role — implementers and review-only roles (PM, Code/Test/Doc Reviewer). | invariant | L418 | E2-191, E2-192 | - | `agents/<role>.md` | Agent | unknown | procedure |
| EX-ROLES-2 | Concretely: never tell the Engineer it may write tests or docs; the Test Writer it may modify source; the Doc Writer it may modify source or tests; the PM or any reviewer it may write source/tests/docs (contract files say `Does NOT modify source code, tests, or docs` / `Does NOT review <other-lanes>`); or one reviewer that it may review another's lane. | invariant | L420-424 | E2-193, E2-194, E2-195, E2-196, E2-197 | - | - | Agent | unknown | example |
| EX-ROLES-3 | Temptation to carve a role exception signals a need for orchestrator-level coordination (follow-up Test Writer dispatch, Subtask redirect/re-scope), NOT a softening clause. | invariant | L426 | E2-198 | - | - | Agent | unknown | procedure |
| EX-ROLES-4 | The only handoff is worker → orchestrator (diff in execution mode, JSON return in research mode), never worker-to-worker; "coordinate with the other role's diff" prose cannot make softening safe. | invariant | L426 | E2-199 | - | - | Agent | unknown | rationale |
| EX-ROLES-5 | The orchestrator dispatches four roles during a Task; role contracts live in the role files; the orchestrator invokes the right role at the right time rather than carrying role prose. | invariant | L440; L905 §5 | E2-208, E5-024 | - | `agents/<role>.md` | Agent | unknown | procedure |
| EX-ROLES-6 | **Engineer** (`agents/engineer.md`) implements source-code Subtasks; Model: Opus (always); does not write tests or docs. | definition | L442 | E2-209 | - | - | Agent | unknown | procedure |
| EX-ROLES-7 | **Test Writer** (`agents/test-writer.md`) implements test Subtasks and reviews the Engineer's diff for missing coverage; Opus (always). | definition | L443 | E2-210 | - | - | Agent | unknown | procedure |
| EX-ROLES-8 | **Doc Writer** (`agents/doc-writer.md`) implements doc Subtasks, reviews the Engineer's diff for doc gaps, and appends/updates a `### Feature: <title>` subsection in the cumulative PRD and SDD per its categorization heuristic; Opus (always). | definition | L444 | E2-211 | - | - | Agent | unknown | procedure |
| EX-ROLES-9 | `<title>` is the verbatim Plan Bee title at the top of the Subtask → Task → Epic → Plan Bee chain; the orchestrator surfaces it in the dispatch context. | relay | L444 | E2-212 | dispatch context `<title>` | Plan Bee title | Agent, bees | unknown | procedure |
| EX-ROLES-10 | `agents/doc-writer.md` is authoritative for the categorization table, `<title>` resolution, idempotency rule, and CLAUDE.md `## Documentation Locations` lookup-key recipe. | definition | L444 | E2-213 | - | - | none | unknown | procedure |
| EX-ROLES-11 | **Product Manager** (`agents/pm.md`) reviews the Task's work against the spec source from the Bee's `reference_materials` (`file-path` resolver or `bees` resolver Spec Bee `t1=Doc` children), or the Bee body when null/empty; Opus (always). | definition | L445 | E2-214 | - | `reference_materials` | Agent | unknown | procedure |
| EX-ROLES-12 | The PM drives `quo-engineer-review` and `quo-doc-writer-review` per Task and produces the per-Task summary report. | definition | L445 | E2-215 | per-Task summary | - | Agent | unknown | procedure |
| EX-ROLES-13 | The PM dispatch prompt does not duplicate resolver-branching logic; `agents/pm.md` `### Resolving reference_materials entries` is authoritative. | invariant | L445 | E2-216 | - | - | Agent | unknown | procedure |
| EX-ROLES-14 | Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) are introduced in Section 5. | definition | L447 | E2-217 | - | - | Agent | unknown | procedure |
| EX-ROLES-15 | **Code Reviewer** (`agents/code-reviewer.md`) reviews the Engineer's output against engineering standards; **Test Reviewer** (`agents/test-reviewer.md`) the Test Writer's output against test-quality standards; **Doc Reviewer** (`agents/doc-reviewer.md`) the Doc Writer's output against documentation standards. | definition | L907-909 §5 | E5-025, E5-026, E5-027 | - | - | none | unknown | procedure |

---

## M14. Per-Task PM dispatch (`EX-PMD`)

- **Purpose:** Dispatch a fresh PM Agent when a Task's Subtasks are all `done` and no `aborted-*` marker is pending, with the Task ID, Subtask IDs, resolver path and tracker path in the prompt.
- **Failure it prevents:** not stated (implicit: a PM review over an undelivered writer lane; PM lacking the tracker/resolver inputs `agents/pm.md` needs).
- **Env deps:** Agent, bees, TaskList. TaskList-dependent: **yes** (advance guard reads `aborted-*` status).
- **Rows after dedupe:** 4 (procedure 4 · rationale 0 · example 0)
- **Literals:** `##### Per-Task PM dispatch` · `<scoped-marker-resolver-path>` · `<compromise-tracker-path>` · `pm-<task-id>` · `pm-<bee-id>`
- **Cross-mechanism edges:** Produces for → CLEAN (PM Final report feeds summary), DEFER (PM-deferred items), SOE (relayed narrative). Consumes from → MOV (advance guard), SMW (resolver path), TRK/MAN (tracker path), DPS (completeness relay).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-PMD-1 | When all Subtasks of the current Task are `done` and no `aborted-*` TaskList task for this Task is `pending`, advance to the per-Task PM review by dispatching a fresh PM Agent. | ordering | L357; L451 | E2-140, E2-218 | PM dispatch | Subtask statuses; `aborted-*` status | bees, TaskList, Agent | no | procedure |
| EX-PMD-2 | The PM dispatch prompt must include the Task ID and the list of completed Subtask IDs. | field-or-template | L451 | E2-219 | prompt | Task ID, Subtask IDs | Agent | no | procedure |
| EX-PMD-3 | The PM prompt must include `<compromise-tracker-path>` — this run's tracker path, the same value Section 6 passes to the post-completion reviewer; pass the path, not its contents (`agents/pm.md` reads the file itself). | field-or-template | L451 | E2-221, E2-222 | prompt placeholder | tracker path (manifest) | Agent | unknown | procedure |
| EX-PMD-4 | The Bee-scoped PM re-dispatches in Section 5 carry the same two placeholders (`<scoped-marker-resolver-path>`, `<compromise-tracker-path>`). | invariant | L451 | E2-223 | prompt | - | Agent | unknown | procedure |

---

## M15. TaskList progress UI & naming convention (`EX-TL`)

- **Purpose:** Use the native TaskList as the only progress UI — exactly one task per Agent, lifecycle `pending`→`in_progress`→`completed` — and define the deterministic name classes every other section keys on.
- **Failure it prevents:** Name collisions between concurrent sibling Subtasks or repeat rounds; a deleted task making the next `-r<n>` reuse a spoken-for name.
- **Env deps:** TaskList, Agent, bees. TaskList-dependent: **yes** (this is the TaskList).
- **Rows after dedupe:** 24 (procedure 21 · rationale 3 · example 0)
- **Literals:** `#### TaskList as progress UI` · `##### TaskList naming convention` · `pending` · `in_progress` · `completed` · `metadata.activity` · `<role>-<subtask-id>` · `engineer-t3.abc.def.gh` · `test-writer-t3.abc.def.ij` · `doc-writer-t3.abc.def.kl` · `<role>-<bee-id>` · `engineer-b.abc` · `test-writer-b.abc` · `doc-writer-b.abc` · `pm-<task-id>` · `pm-t2.abc.def.gh` · `pm-<bee-id>` · `pm-b.abc` · `<reviewer>-<bee-id>` · `code-reviewer-b.abc` · `test-reviewer-b.abc` · `doc-reviewer-b.abc` · `-r<n>` · `engineer-b.abc-r1` · `engineer-b.abc-r2` · `code-reviewer-b.abc-r1` · `doc-writer-t3.abc.def.kl-r1` · `pm-t2.abc.def.gh-r1` · `engineer-<issue-id>-r<n>` · `<role>-postcomp-<n>` · `engineer-postcomp-1` · `doc-writer-postcomp-2` · `engineer-postcomp-3` · `<role>-postcomp-<n>-r<k>` · `test-writer-postcomp-2-r1` · `defer-<short-suffix>` · `defer-1` · `defer-2` · `gate-<kind>-<short-suffix>` · `gate-askuserquestion-1` · `aborted-*`
- **Cross-mechanism edges:** Produces for → every mechanism that sweeps or tests names (EDP, CLEAN, BEEREV, ABORT, POST, DEFER, GATE, MOV). Consumes from → LOOP (dispatch events), MOV (marker class), GATE/DEFER (obligation-marker classes).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-TL-1 | Use Claude Code's native TaskList as the visible progress UI; no separate display backend. | definition | L457 | E2-231 | - | - | TaskList | unknown | procedure |
| EX-TL-2 | For every Agent dispatched, create exactly one TaskList task (so two post-completion findings each needing an Engineer dispatch under distinct names, never a shared `engineer-postcomp`). | invariant | L459; L1089 §6 | E2-232, E5-159 | TaskList task | Agent dispatch | TaskList, Agent | unknown, yes | procedure |
| EX-TL-3 | Set `pending` when the orchestrator decides this Subtask is next, before the Agent invocation lands; `in_progress` the moment `Agent(...)` returns; `completed` when the completion notification is processed and the bees ticket is confirmed `status=done`. | ordering | L461-463 | E2-233, E2-234, E2-235 | task status | Agent dispatch/notification; bees status | TaskList, Agent, bees | unknown | procedure |
| EX-TL-4 | `completed` on an Agent task means "this Agent is gone", not "this work shipped". | definition | L463 | E2-237 | - | - | TaskList | unknown | procedure |
| EX-TL-5 | Use `metadata.activity` to surface finer-grained progress when a worker emits intermediate signal (e.g. `"running narrow tests on package X"`); update it opportunistically; it is informational, not a routing input. | field-or-template | L465 | E2-238, E2-239 | `metadata.activity` | worker signal | TaskList | unknown | procedure |
| EX-TL-6 | The naming convention is the canonical cross-reference for downstream Sections and other skills; names are deterministic (no collision) and unambiguous (map back to a bee ticket). | definition | L469 | E2-240 | - | - | TaskList | unknown | procedure |
| EX-TL-7 | Implementer Agents on the forward path use Subtask scope `<role>-<subtask-id>` (e.g. `engineer-t3.abc.def.gh`, `test-writer-t3.abc.def.ij`, `doc-writer-t3.abc.def.kl`); each Subtask gets its own Agent and task, so the subtask-id keeps names unique across concurrent siblings. PM names are Task-scoped `pm-<task-id>`. | name-class | L471; L869 | E2-241, E2-242, E4-176 | task name | `<subtask-id>` | TaskList | no | procedure |
| EX-TL-8 | Bee-level implementer Agents re-dispatched from Section 5 use Bee scope `<role>-<bee-id>` (e.g. `engineer-b.abc`, `test-writer-b.abc`, `doc-writer-b.abc`). | name-class | L472 | E2-243 | task name | `<bee-id>` | TaskList | unknown | procedure |
| EX-TL-9 | Rationale: Section 5 findings span the whole Bee's diff and are not attributable to one Subtask; Subtask and Bee ids are distinct token shapes and never overlap. | rationale-only | L472 | E2-244 | - | - | TaskList | unknown | rationale |
| EX-TL-10 | PM Agents on the forward path use `pm-<task-id>` (e.g. `pm-t2.abc.def.gh`); a PM re-dispatched from Section 5 takes `pm-<bee-id>` (e.g. `pm-b.abc`). | name-class | L473 | E2-245, E2-246 | task name | `<task-id>` / `<bee-id>` | TaskList | no, unknown | procedure |
| EX-TL-11 | Reviewer Agents use Bee scope `<reviewer>-<bee-id>` (`code-reviewer-b.abc`, `test-reviewer-b.abc`, `doc-reviewer-b.abc`); reviewers run once per Bee at the final Bee-level review. | name-class | L474 | E2-247, E2-248 | task name | `<bee-id>` | TaskList | unknown | procedure |
| EX-TL-12 | Round discriminator: every dispatch after the first of an already-named role at the same scope appends `-r<n>`, `<n>` = 1-based re-dispatch count for that role at that scope (e.g. `engineer-b.abc` → `engineer-b.abc-r1` → `engineer-b.abc-r2`; `code-reviewer-b.abc-r1`; `doc-writer-t3.abc.def.kl-r1`; `pm-t2.abc.def.gh-r1`). | name-class | L475 | E2-249, E2-250 | task name | re-dispatch count | TaskList | yes | procedure |
| EX-TL-13 | The `-r<n>` form is identical to `/quo-fix-issue`'s `engineer-<issue-id>-r<n>` so readers see one convention. | definition | L475 | E2-251 | - | - | TaskList | yes | rationale |
| EX-TL-14 | Because the discriminator is a suffix, every rule that tests these names — notably part (g)'s Engineer-dispatch preconditions — matches on name prefix plus status. | invariant | L475 | E2-252 | - | TaskList names | TaskList | yes | procedure |
| EX-TL-15 | Post-completion follow-up Agents (Section 6 step 6 `Fix in this session`) use `<role>-postcomp-<n>`, `<n>` = 1-based index of the finding in the reviewer's numbered list (e.g. `engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`). | name-class | L476; L1089 §6 | E2-253, E5-157, E5-158 | task name | finding index | TaskList | yes | procedure |
| EX-TL-16 | Post-completion names take no ticket-id suffix and normally no round discriminator; the per-finding index is the discriminator. | invariant | L476 | E2-254 | - | - | TaskList | yes | procedure |
| EX-TL-17 | Carve-out: `-r<k>` IS required when a post-completion writer lane is re-dispatched after a movement abort, `<k>` = 1-based re-dispatch count at that finding index (e.g. `test-writer-postcomp-2-r1`); outside that carve-out do not append a round discriminator to a post-completion name. | name-class | L476; L1093 | E2-255, E2-256, E5-168 | task name | re-dispatch count | TaskList, Agent | yes | procedure |
| EX-TL-18 | Section 6 step 6 is authoritative for post-completion dispatch ordering, freeze precondition and close-out; same form as `/quo-fix-issue` Section 8 step 6. | definition | L476 | E2-257 | - | - | none | yes | procedure |
| EX-TL-19 | For a post-completion `aborted-*` marker, `<n>` is the same finding index as the lane it marks so the marker reads back to its finding. | invariant | L477 | E2-259 | - | finding index | TaskList | unknown | procedure |
| EX-TL-20 | Deferral-ledger tasks have Run scope: `defer-<short-suffix>` (e.g. `defer-1`, `defer-2`, or any collision-resistant suffix). | name-class | L478 | E2-265 | task name | - | TaskList | unknown | procedure |
| EX-TL-21 | Gate tasks have Turn scope: `gate-<kind>-<short-suffix>`; the dominant `<kind>` is `askuserquestion` (e.g. `gate-askuserquestion-1`). | name-class | L479 | E2-270 | task name | - | TaskList | unknown | procedure |
| EX-TL-22 | The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<subtask-id>`, `pm-<task-id>`, `<role>-<bee-id>`, `pm-<bee-id>`, reviewer names, `<role>-postcomp-<n>` and `aborted-*`, with or without `-r<n>`. | invariant | L479 | E2-280 | - | - | TaskList | unknown | procedure |
| EX-TL-23 | "Clear from the active set" means mark the task `completed` — it never means delete it. | invariant | L926 §5; L1091 §6; L785 close-out | E5-068, E5-163, E3-233 | - | - | TaskList | yes, unknown | procedure |
| EX-TL-24 | Rationale: `-r<n>` is derived by counting recorded rounds, so deleting a task makes the next re-dispatch reuse a name already spoken for; closing by status keeps history readable and still removes the task from every `pending`/`in_progress` test part (g) runs. | rationale-only | L926; L785 | E5-069, E5-070, E3-234 | - | - | none | yes, unknown | rationale |

---

## M16. `gate-*` two-step contract (`EX-GATE`)

- **Purpose:** Every `AskUserQuestion` the skill fires is preceded, in the same turn, by a `TaskCreate` of a `gate-askuserquestion-<short-suffix>` task naming the gate, closed the moment the answer is consumed.
- **Failure it prevents:** The narrate-instead-of-do failure mode (describing a gate rather than firing it); yielding with an unanswered gate; phantom re-prompts from stranded gate tasks.
- **Env deps:** TaskList, AskUserQuestion. TaskList-dependent: **yes** (the contract is a TaskList task).
- **Rows after dedupe:** 14 (procedure 13 · rationale 1 · example 0)
- **Literals:** `TaskCreate` · `AskUserQuestion` · `gate-askuserquestion-<short-suffix>` · `gate-*` · `Type something.` · `Chat about this` · `Check session reasoning effort`
- **Cross-mechanism edges:** Produces for → every gate site (EFF, BEE, ISO, EPIC, UMG, NEXT, CWG, ROUTE gates (c)/(d), POST steps 5/7, DHG, FINAL). Consumes from → TL (name class), LOOP (recovery tick re-fires stranded gate).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-GATE-1 | Section 1 has three `AskUserQuestion` gates in this order: session-effort gate, Bee pick, worktree/isolation gate. | ordering | L43 §1 | E1-031 | - | - | AskUserQuestion | unknown | procedure |
| EX-GATE-2 | Every gate this skill fires goes through the two-step contract: first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate it fronts, then call `AskUserQuestion` with the finite choices in the same turn. Stated at: §1 gates, §2 mode gate, unexplained-movement gate, §4.2 continuation gate, context-guard gate, routing gates (c)/(d), post-completion findings gate, recovery gates, deferral-hygiene gate, §7 gates. | gate | L43; L230; L479; L575; L754; L825; L847; L890; L1077; L1103; L1118; L1188; L1245 | E1-032, E1-033, E2-001, E2-002, E2-271, E3-064, E3-201, E4-069, E4-120, E4-208, E4-209, E4-210, E5-149, E5-192, E6-001, E6-003, E6-005, E6-103, E7-004, E7-006, E7-008 | `gate-*` task; AskUserQuestion call | - | TaskList, AskUserQuestion | yes, no, unknown | procedure |
| EX-GATE-3 | Mark each `gate-*` task `completed` the moment the prescribed tool returns and its result is consumed (answer routed, next branch entered). | ordering | L43; L230; L479; L575; L754; L890; L1077; L1103; L1118; L1188; L1245 | E1-034, E2-003, E2-276, E3-065, E3-203, E4-212, E5-151, E5-194, E6-006, E6-105, E7-009 | `gate-*` → `completed` | tool result | TaskList | yes, unknown | procedure |
| EX-GATE-4 | The `<short-suffix>` MUST be unique per fire within the run across every `gate-*` task regardless of `<kind>` (monotonic integers or gate-specific slugs) — so re-fires are not mistaken for first fires and concurrent/repeated fires do not collide. | invariant | L479; L1118; L1245 | E2-272, E6-004, E7-007 | - | prior `gate-*` names | TaskList | unknown, yes | procedure |
| EX-GATE-5 | Do not produce a text response describing the gate; fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L890; L1077; L1103 | E4-211, E5-150, E5-193 | - | - | TaskList, AskUserQuestion | yes | procedure |
| EX-GATE-6 | Gates are multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot. | invariant | L754; L890; L1103 | E3-207, E4-213, E5-195 | - | - | AskUserQuestion | no, yes | procedure |
| EX-GATE-7 | Yield-control discipline: this skill MUST NOT yield to the harness while any `gate-*` task is `pending` or `in_progress` (mirrors `defer-*`). | invariant | L479; L754 | E2-278, E3-202 | - | `gate-*` statuses | TaskList | unknown, no | procedure |
| EX-GATE-8 | If a `gate-*` task is left active when the orchestrator would yield, the next reconciliation tick walks the TaskList, surfaces it, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. | recovery | L479 | E2-279 | re-fired tool call | `gate-*` task | TaskList, AskUserQuestion | unknown | procedure |
| EX-GATE-9 | A `gate-*` task's `metadata.activity` carries the gate's finite choices verbatim where applicable. | field-or-template | L479 | E2-275 | `metadata.activity` | gate choices | TaskList | unknown | procedure |
| EX-GATE-10 | A `gate-*` task normally enters and exits within a single turn — shorter than `defer-*`, which spans the run. | definition | L479 | E2-277 | - | - | TaskList | unknown | procedure |
| EX-GATE-11 | The contract applies at every gate — trailer-driven review-skill gates (Section 5 escalation) and trailer-less orchestrator-driven gates. | invariant | L479 | E2-273 | - | - | TaskList, AskUserQuestion | unknown | procedure |
| EX-GATE-12 | Trailer-less gates enumerated: §1 conditional session-effort gate (`Check session reasoning effort`), §3 unexplained-movement gate, §4.2 continue-or-stop multi-Epic gate (Mode 1), §6 post-completion findings gate, §6.5 deferral-hygiene gate, §7 Acceptance-Criteria sign-off and Bee close-out gates. | definition | L479 | E2-274 | - | - | AskUserQuestion | no | procedure |
| EX-GATE-13 | Section 7 has exactly three gates: ignored-feedback action gate, per-Acceptance-Criteria sign-off gate, final Bee-done gate. | definition | L1245 §7 | E7-005 | - | - | AskUserQuestion | no | procedure |
| EX-GATE-14 | Rationale: these gates inherit a prose-adherence fragility narrowed (not closed) by the two-step contract; it is an execution-time risk, not something this section fixes — do not claim it is fixed. | rationale-only | L892; L1103 | E4-214, E5-198 | - | - | none | yes | rationale |

---

## M17. Scoped-marker PM wiring (`EX-SMW`)

- **Purpose:** Hand `agents/pm.md` the runtime-resolved path of the sibling skill's `scoped_marker_resolver.py` so the PM can run its Scoped-marker check.
- **Failure it prevents:** not stated (implicit: baking per-machine paths into prose; duplicating the helper's grammar in the orchestrator).
- **Env deps:** Agent. TaskList-dependent: **no**.
- **Rows after dedupe:** 4 (procedure 4 · rationale 0 · example 0)
- **Literals:** `#### Scoped-marker PM dispatch wiring` · `<scoped-marker-resolver-path>` · `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` · `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py` · `Base directory for this skill: /Users/.../quo-execute`
- **Cross-mechanism edges:** Produces for → PMD (placeholder). Consumes from → skill invocation header (base directory); CWG and DHG reuse the same base-directory resolution idea.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-SMW-1 | The PM dispatch prompt must include the resolved path to the Scoped-marker helper as the `<scoped-marker-resolver-path>` substitution, filled at runtime so `agents/pm.md` can perform its Scoped-marker check. | field-or-template | L451; L483 | E2-220, E2-281 | prompt placeholder | resolved helper path | Agent | unknown | procedure |
| EX-SMW-2 | Resolve the helper at runtime from this skill's base directory via the `..` sibling traversal: `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (PowerShell `…\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py`). | command | L483-499 | E2-282 | resolved path | skill base directory | none | unknown | procedure |
| EX-SMW-3 | The base directory is shown in the skill invocation header at session start (e.g. `Base directory for this skill: /Users/.../quo-execute`). | definition | L489; L1216 §6.5 | E2-283, E6-138 | - | skill invocation header | none | unknown | procedure |
| EX-SMW-4 | The orchestrator's responsibility ends at passing the resolved path; it does not inline the Scoped-marker grammar, the temp-file staging recipe, or the helper invocation — `agents/pm.md` owns those. | invariant | L501 | E2-284 | - | - | Agent | unknown | procedure |

---

## M18. Testing discipline (five-rung ladder) & long commands (`EX-TEST`)

- **Purpose:** Keep test/lint/format runs on the lowest rung that catches the issue, with exactly one authoritative `Full test` at the Task's `.T` subtask, and run long commands via Bash `timeout` / background without polling.
- **Failure it prevents:** Redundant full-workspace suite runs (minutes per Task) and shell polling loops.
- **Env deps:** Bash. TaskList-dependent: **no**.
- **Rows after dedupe:** 12 (procedure 11 · rationale 1 · example 0)
- **Literals:** `#### Testing discipline — avoid redundant full-workspace runs` · `#### Running long commands` · `Compile/type-check` · `Format` · `Lint` · `Narrow test` · `Full test` · `.T` · `timeout` · `540000` · `600000` · `Bash(command: "<your project's test command per CLAUDE.md>", timeout: 540000)` · `Bash(run_in_background: true)`
- **Cross-mechanism edges:** Produces for → CLEAN (rung 5 = Format only before commit). Consumes from → PRE (Build Commands keys), CLAUDE.md `## Build Commands`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-TEST-1 | Test and lint commands form a ladder; stay on the lowest rung that catches the issue you might have introduced. | invariant | L505 | E2-285 | - | - | Bash | unknown | procedure |
| EX-TEST-2 | Look up actual commands from the project's CLAUDE.md `## Build Commands` using keys `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. | command | L505 | E2-286 | - | CLAUDE.md keys | Bash | unknown | procedure |
| EX-TEST-3 | Rung 1 (iterating on a file — Engineer, Test Writer): `Narrow test` + `Lint` at the same scope; do NOT run the full suite. | ordering | L507 | E2-287 | - | `Narrow test`, `Lint` | Bash | unknown | procedure |
| EX-TEST-4 | Rung 2 (subtask boundary): `Narrow test` + `Lint` for the touched file/package; do NOT run `Full test` yet. | ordering | L508 | E2-288 | - | `Narrow test`, `Lint` | Bash | unknown | procedure |
| EX-TEST-5 | Rung 3 (the Task's final `.T` or equivalent subtask): the single authoritative `Full test` run, plus workspace-scope `Lint`, plus a `Format` check — the only place the full suite must run. | ordering | L509 | E2-289 | - | `Full test`, `Lint`, `Format` | Bash | unknown | procedure |
| EX-TEST-6 | Rung 4 (PM review): trust the `.T` output; do not re-run the full suite by default unless there is a specific reason (skipped work reported, stale `.bees/` state). | invariant | L510 | E2-290 | - | `.T` output | Bash | unknown | procedure |
| EX-TEST-7 | Rung 5 (Director, before commit): run `Format` only; do NOT re-run tests. | ordering | L511; L529 §4.1 | E2-291, E3-008 | - | `Format` | Bash | unknown | procedure |
| EX-TEST-8 | Rationale: the `.T` subtask already validated and the PM confirmed; re-running wastes minutes per Task. | rationale-only | L529 | E3-009 | - | - | none | unknown | rationale |
| EX-TEST-9 | When a Task only touches one package's tests, do not invoke workspace-wide tests against unrelated packages. | invariant | L513 | E2-292 | - | - | Bash | unknown | procedure |
| EX-TEST-10 | Apply the same ladder to `Lint`, `Format` and any docs-build command: scope narrowly while iterating, run workspace-wide once at `.T`, trust downstream. | invariant | L515 | E2-293 | - | - | Bash | unknown | procedure |
| EX-TEST-11 | Use the Bash tool's `timeout` parameter (max `600000` ms = 10 min) for long commands; up to 10 min dispatch in the foreground: `Bash(command: "<your project's test command per CLAUDE.md>", timeout: 540000)`. | command | L519 | E2-294, E2-295 | - | CLAUDE.md test command | Bash | unknown | procedure |
| EX-TEST-12 | For runs legitimately exceeding 10 min use `Bash(run_in_background: true)`, wait silently for the completion notification, then Read the output file; do not write shell polling loops — the harness handles notification. | command | L519 | E2-296, E2-297 | - | output file | Bash | unknown | procedure |

---
## M19. Per-Task cleanup, Format & commit step, per-Task summary template (`EX-CLEAN`)

- **Purpose:** Close a Task: flip it `done` in bees, Format, stage judgement-selected files plus the in-repo Plans hive, commit once with the fixed subject shape, sweep the Task's TaskList names by prefix, print the summary block, and dispatch the next Task.
- **Failure it prevents:** Sweeping other agents' in-flight edits into the commit (`git add -A`); an `aborted-*` marker left `pending` past close-out holding a later advance shut; re-running the suite the `.T` subtask already ran.
- **Env deps:** bees, git, Bash, TaskList, Agent. TaskList-dependent: **yes**.
- **Rows after dedupe:** 31 (procedure 28 · rationale 2 · example 1)
- **Literals:** `#### 4.1 After Each Task` · `status=done` · `.bees/` · `git status` · `hive_commit.py` · `resolve-hive-paths` · `python3 "<this skill's base directory>/scripts/hive_commit.py" resolve-hive-paths --hive plans` · `python "<this skill's base directory>\scripts\hive_commit.py" resolve-hive-paths --hive plans` · `Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)` · `Epic N, Task M — …` · `Plan b.bc7, Epic 1, Task 7 — Document the new auth config surface (t2.rwx.fy.qq)` · `## Task [N] of [total] Complete: [task-title]` · `**Task ID**` · `**Files Changed**` · `**Reviews**` · `**Ignored Review Feedback**` · `**Second-order effects**` · `**Follow-up Tasks Created**` · `Proceeding to next Task: [next-task-title]` · `Final Task, moving on to Final Reviews` · `N nits applied without re-review` · `count unavailable post-compaction` · `"None"`
- **Cross-mechanism edges:** Produces for → CKPT (one commit per Task is carrier 2), SUMM (Bee-level analog), ABORT (the same prefix sweep at abort). Consumes from → TEST (rung 5), PMD (PM Final report), SOE (field content), DEFER (ignored items), DHG (helper path resolution shared with the Encode step), MOV (markers to sweep).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-CLEAN-1 | Run the 4.1 close-out only when a Task and all its Subtasks are done (all reviewer feedback addressed or ignored). | precondition | L525 | E3-001 | - | completion state; feedback disposition | none | unknown | procedure |
| EX-CLEAN-2 | Mark the Task `status=done` in bees before committing so `.bees/` status changes are included in the commit. | command | L527 | E3-002, E3-004 | Task status flip | Task ID | bees, git | unknown | procedure |
| EX-CLEAN-3 | Subtasks are already marked done by each agent, except doc Subtasks, which the orchestrator flips on behalf of the doc-writer (no `Bash`). | definition | L527 | E3-003 | doc-Subtask flip | `agents/doc-writer.md` routing | bees | unknown | procedure |
| EX-CLEAN-4 | Create exactly one git commit per Task. | command | L528 | E3-005 | git commit | staged files | git | unknown | procedure |
| EX-CLEAN-5 | Staging step 1: run the `Format` command from CLAUDE.md `## Build Commands` to normalize formatting. | command | L529 | E3-007 | reformatted tree | `Format` | Bash | unknown | procedure |
| EX-CLEAN-6 | When a final `trivial-tweak` nit pass landed after PM confirmation, the implementer's own lane rungs cover validation: Engineer `Compile/type-check`, `Lint`, `Narrow test`; Test Writer `Narrow test`, `Lint`; Doc Writer owes no rung. | definition | L529 | E3-010 | - | lane rungs | none | unknown | rationale |
| EX-CLEAN-7 | Staging step 2: run `git status` to see the full set of modified and untracked files. | command | L530 | E3-011 | - | working tree | git | unknown | procedure |
| EX-CLEAN-8 | Staging step 3: stage files related to this Task — agent-reported files, formatting changes to files this Task's agents touched, and (only if in-repo) the Plans hive path's contents. | command | L531 | E3-012 | staged index | agent reports; `git status` | git | unknown | procedure |
| EX-CLEAN-9 | Learn the in-repo Plans hive path with the bundled helper's non-mutating mode, one literal call: `python3 "<this skill's base directory>/scripts/hive_commit.py" resolve-hive-paths --hive plans` (PowerShell `python "<…>\scripts\hive_commit.py" resolve-hive-paths --hive plans`). | command | L531-541 | E3-013, E3-016 | Plans hive path (stdout) or nothing | skill base directory | Bash | unknown | procedure |
| EX-CLEAN-10 | Resolve `hive_commit.py` the same way as the Section 6.5 Encode step (own base directory); the helper emits the Plans hive's absolute path when it lives inside this repo, or nothing when outside — then stage no hive path. | definition | L531 | E3-014, E3-015 | - | helper output | Bash | unknown | procedure |
| EX-CLEAN-11 | `git add` the emitted Plans hive path (if any) alongside judgement-selected source files; review each modified file and stage it only if plausibly related to this Task. | command | L543 | E3-017, E3-019 | staged index | helper output; `git status` | git | unknown | procedure |
| EX-CLEAN-12 | Staging step 4: commit with a descriptive message per system/project git guidance. | command | L544 | E3-020 | git commit | staged index | git | unknown | procedure |
| EX-CLEAN-13 | Commit subject template `Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)`; the bare Task ID appears once, in trailing parentheses. | field-or-template | L544 | E3-021 | commit subject | Bee ID; ordinals; title; Task ID | git | no | procedure |
| EX-CLEAN-14 | Example subject: `Plan b.bc7, Epic 1, Task 7 — Document the new auth config surface (t2.rwx.fy.qq)`. | example | L544 | E3-022 | - | - | none | no | example |
| EX-CLEAN-15 | Source the Plan Bee ID and Epic ordinal from the run's invocation and the Task's parent chain (Task → Epic → Bee); `Epic N` / `Task M` ordinals come from ticket titles. | definition | L544 | E3-023 | - | run invocation; titles | bees | no | procedure |
| EX-CLEAN-16 | If the Epic has no parent Plan Bee (standalone Epic), omit the `Plan <bee-id>, ` prefix and lead with `Epic N, Task M — …`. | field-or-template | L544 | E3-024 | commit subject | Epic parent presence | git | no | procedure |
| EX-CLEAN-17 | Step 3: mark the per-Task TaskList tasks (named per Section 3's convention) `completed` and clear them from the active set, sweeping by name prefix, not exact name. | command | L545 | E3-025, E3-026 | tasks → `completed` | TaskList names | TaskList | unknown | procedure |
| EX-CLEAN-18 | The prefix sweep must close lanes re-dispatched under `-r<n>` (e.g. `doc-writer-<subtask-id>-r1`, `pm-<task-id>-r1`) alongside their first round. | invariant | L545 | E3-027 | round tasks → `completed` | `-r<n>` names | TaskList | unknown | procedure |
| EX-CLEAN-19 | The sweep includes any `aborted-<role>-<subtask-id>` redelivery markers the movement rung opened for this Task's Subtasks. | invariant | L545 | E3-028 | markers → `completed` | markers | TaskList | unknown | procedure |
| EX-CLEAN-20 | Rationale: reaching step 3 means the redelivery landed; a marker left `pending` past close-out would hold a later advance shut. | rationale-only | L545 | E3-029 | - | - | none | unknown | rationale |
| EX-CLEAN-21 | There is no Agent shutdown to perform — cold dispatches complete-and-exit when each Agent returns; close-out is bookkeeping on the progress UI and on part (g)'s state. | definition | L545; L928 §5 | E3-030, E5-072 | - | dispatch shape | Agent | unknown | procedure |
| EX-CLEAN-22 | The aborted path runs this same prefix sweep at its own site (Section 4.2 `##### Aborted-run close-out`) — keep the two sweeps in step. | invariant | L545 | E3-031 | - | EX-CLEAN-17..19 | TaskList | unknown | procedure |
| EX-CLEAN-23 | Step 4: output the per-Task summary block to the screen, then advance to the next Task by dispatching fresh ephemeral implementer Agents per Section 3's dispatch shape. | command | L546 | E3-032, E3-033 | printed summary; dispatches | next Task | Agent | unknown | procedure |
| EX-CLEAN-24 | Summary heading `## Task [N] of [total] Complete: [task-title]`. | field-or-template | L549 | E3-034 | summary line | ordinal, total, title | none | unknown | procedure |
| EX-CLEAN-25 | Field `**Task ID**: <task-id>`. | field-or-template | L551 | E3-035 | summary line | Task ID | none | unknown | procedure |
| EX-CLEAN-26 | Field `**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])`. | field-or-template | L552 | E3-036 | summary line | commit file set | none | unknown | procedure |
| EX-CLEAN-27 | Field `**Reviews**: [Code review: X issues found/None needed \| Docs review: Y issues found/None needed \| N nits applied without re-review (or "count unavailable post-compaction"), when any]`. | field-or-template | L553 | E3-037 | summary line | review results; nit count | none | unknown | procedure |
| EX-CLEAN-28 | Field `**Ignored Review Feedback**`: items flagged by `quo-engineer-review` / `quo-doc-writer-review` the Director chose not to address, or `"None"`. | field-or-template | L554 | E3-038 | summary line | ignored items | none | unknown | procedure |
| EX-CLEAN-29 | Field `**Second-order effects**`: the relayed `### Second-order effects` narrative, rendered per the Second-order-effects logic (EX-SOE). | field-or-template | L555 | E3-039 | summary line | PM Final report | none | unknown | procedure |
| EX-CLEAN-30 | Field `**Follow-up Tasks Created**: [count, if any] [list task-ids if created]`. | field-or-template | L556 | E3-040 | summary line | follow-up Task IDs | none | unknown | procedure |
| EX-CLEAN-31 | Closing line is exactly one of `Proceeding to next Task: [next-task-title]` or `Final Task, moving on to Final Reviews`. | choice-set | L557-559 | E3-041 | summary line | remaining-Task state | none | unknown | procedure |

---

## M20. Second-order-effects relay & destinations (`EX-SOE`)

- **Purpose:** Give `/quo-engineer-review`'s `### Second-order effects` narrative a named destination at each scope — the per-Task summary field (via the PM) and the `## Bee Execution Complete` field (via the Bee-level Code Reviewer / Bee-scoped PM) — and fix the four rendering rules.
- **Failure it prevents:** The narrative reaching the orchestrator and stopping there; a Bee-level effect landing in already-emitted per-Task output; a conditional section nobody can rely on.
- **Env deps:** Agent (relay chain). TaskList-dependent: **no**.
- **Rows after dedupe:** 14 (procedure 11 · rationale 3 · example 0)
- **Literals:** `### Second-order effects` · `#### <invocation scope>` · `**Second-order effects**` · `No second-order effects identified.` · `None identified.` · `Second-order effects (rendered into the summary block above).`
- **Cross-mechanism edges:** Produces for → CLEAN (per-Task field), SUMM (Bee-level field). Consumes from → PMD (PM Final report), BEEREV (Code Reviewer / Bee-scoped PM returns), `/quo-engineer-review`, `agents/pm.md`, `agents/code-reviewer.md`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-SOE-1 | The per-Task `**Second-order effects**` field is the destination for the narrative `/quo-engineer-review` emits under `### Second-order effects`, relayed by the per-Task PM (`agents/pm.md` relays into its Final report, one labelled sub-block per in-flight invocation). | relay | L562 §4.1 | E3-042, E3-043 | field content | PM Final report | Agent | unknown | procedure |
| EX-SOE-2 | Rationale: without a named destination the narrative reaches the orchestrator and stops there. | rationale-only | L562 | E3-044 | - | - | none | unknown | rationale |
| EX-SOE-3 | The Bee-level review has its own destination: the `**Second-order effects**` field of Section 9's `## Bee Execution Complete` block. | definition | L562; L1294 §9 | E3-045, E7-034 | - | Section 5 output | none | no, yes | procedure |
| EX-SOE-4 | The Bee-level Code Reviewer relays `/quo-engineer-review`'s `### Second-order effects` subsection verbatim on every return, clean ones included (`agents/code-reviewer.md`); a Bee-scoped PM re-dispatched by Section 5 relays it into its Final report (`agents/pm.md`). | definition | L913 §5; L1294 §9 | E5-039, E5-040, E7-035, E7-036 | - | reviewer / PM return | Agent | unknown, yes | procedure |
| EX-SOE-5 | Second-order effects are narrative, not routing input; they do not by themselves require a re-dispatch (anything actionable is already a numbered finding); do not let them terminate in this conversation. | invariant | L913 | E5-041, E5-045 | - | - | none | unknown | procedure |
| EX-SOE-6 | Render the relayed Bee-level effects into the `**Second-order effects**` field of `## Bee Execution Complete` (Section 9), with the same four steps Section 4.1 uses, at Bee scope. | relay | L913; L1288, L1294 | E5-042, E7-029, E7-038 | summary field | Code Reviewer / PM return | none | no, yes | procedure |
| EX-SOE-7 | Do NOT route Bee-level effects into Section 4.1's per-Task field — those summaries are already emitted and closed by the time Section 9 runs. | invariant | L913; L1294 | E5-043, E7-037 | - | - | none | no | procedure |
| EX-SOE-8 | Rationale: the per-Task field belongs to the per-Task PM's narrative, printed as each Task closed, so a Bee-level effect sent there lands in already-emitted output. | rationale-only | L913 | E5-044 | - | - | none | no | rationale |
| EX-SOE-9 | Rendering step 1: collect every relayed narrative for the scope — per Task: the PM Final report `### Second-order effects` incl. each `#### <invocation scope>` sub-block; per Bee: each Code Reviewer return (all rounds incl. `-r<n>`) and any Bee-scoped PM Final report section — and render bullets verbatim; do not re-summarize, re-rank, or fold them into the `**Reviews**` line. | relay | L564; L1296 | E3-046, E3-047, E7-039, E7-040 | field content | PM / reviewer returns | none | unknown, yes | procedure |
| EX-SOE-10 | Rendering step 2: keep the `#### <invocation scope>` sub-block labels the relaying source supplied, so a reader can tell which round or invocation surfaced which effect. | relay | L565; L1297 | E3-048, E7-041 | field content | sub-block labels | none | unknown, yes | procedure |
| EX-SOE-11 | Rendering step 3: de-duplicate exact repeats across sources (keep the earliest attribution); keep near-duplicates that differ in substance as separate entries. | relay | L566; L1298 | E3-049, E7-042, E7-043 | field content | relayed bullets | none | unknown, yes | procedure |
| EX-SOE-12 | Rendering step 4: when every source reported the fixed empty line `No second-order effects identified.`, or no emitting review ran for the scope, render the single line `None identified.`. | field-or-template | L567; L1299 | E3-050, E7-044 | field content | source reports | none | unknown, yes | procedure |
| EX-SOE-13 | Do not omit the `**Second-order effects**` field at either scope; it is unconditional (unlike `**Accepted compromises**`). | invariant | L567; L1299 | E3-051, E7-045 | - | - | none | unknown, yes | procedure |
| EX-SOE-14 | Rationale: a section that appears only when there is something to say degrades into one nobody can rely on being asked for. | rationale-only | L567; L1299 | E3-052, E7-046 | - | - | none | unknown, yes | rationale |

---

## M21. Ignored-feedback / `defer-*` ledger (`EX-DEFER`)

- **Purpose:** Record every review-feedback item the Director ignores and every PM-deferred item as a `pending` `defer-<short-suffix>` task at the moment of decision, annotated with exactly one destination, so the Section 6.5 gate has something to close out.
- **Failure it prevents:** The deferral-hygiene gate firing empty; vague "defer to later" framings with no named destination.
- **Env deps:** TaskList, bees. TaskList-dependent: **yes**.
- **Rows after dedupe:** 13 (procedure 9 · rationale 4 · example 0)
- **Literals:** `defer-<short-suffix>` · `defer-N` · `defer-*` · `addressed-now-in-this-Task` · `defer-to-existing-ticket-body: <ticket-id>` · `defer-to-new-Issue` · `### Deferred refinements` · `Record each ignored-feedback item as a \`defer-N\` TaskList task at the moment of decision.` · `Record each PM-deferred item as a \`defer-N\` TaskList task at the moment of the PM verdict.` · `Record each ignored item as a \`defer-N\` TaskList task at the moment of the ignore decision.`
- **Cross-mechanism edges:** Produces for → DHG (active set), CKPT (carrier 4), FINAL (ignored-feedback display). Consumes from → PMD (PM Final report contract), BEEREV (ignore decisions), TL (name class), ROUTE (batched nits are excluded).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-DEFER-1 | Whenever the Director ignores a review-feedback item rather than fix it now (per-Task or Bee-level), create a `defer-<short-suffix>` TaskList task at the moment of decision, with the feedback's one-line description as `metadata.activity`, status `pending`. | command | L569 §4.1; L918 §5; L478 | E3-053, E3-054, E5-052, E5-053, E2-267 | `defer-*` task | ignore decision | TaskList | unknown, yes | procedure |
| EX-DEFER-2 | The PM Final report contract (`agents/pm.md`) annotates each deferred item with a destination: `addressed-now-in-this-Task`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue`. | choice-set | L569 | E3-055 | - | PM Final report | none | unknown | procedure |
| EX-DEFER-3 | Annotate the `defer-*` task's `metadata.activity` with exactly one of those three destination values (the PM's annotation when relaying a PM item; the Director's own judgement call at the Section 5 ignore site) — the annotation is required, not optional. | field-or-template | L569; L918 | E3-056, E5-054, E5-055 | `metadata.activity` | destination vocabulary | TaskList | unknown, yes | procedure |
| EX-DEFER-4 | Vague framings without a named destination (e.g. "defer to later") are forbidden, by the same anti-pattern rule as the PM's annotations. | invariant | L918 | E5-057 | - | - | TaskList | yes | procedure |
| EX-DEFER-5 | Rationale: matching the PM contract keeps Section 6.5's gate able to route reviewer- and PM-feedback items through the same Fix / File / Encode branches. | rationale-only | L918 | E5-056 | - | - | none | yes | rationale |
| EX-DEFER-6 | Rationale: the record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it the gate fires empty. | rationale-only | L569; L918 | E3-057, E5-058 | - | - | none | unknown, yes | rationale |
| EX-DEFER-7 | Items the Director addressed inline / annotated `addressed-now-in-this-Task` do NOT get a `defer-*` task; the ledger tracks only items not addressed now. | invariant | L569, L571 | E3-058, E3-061 | - | annotations | TaskList | unknown | procedure |
| EX-DEFER-8 | When the per-Task PM returns, walk its Final report deferred items per `agents/pm.md`'s Final report contract. | command | L571 | E3-059 | - | PM Final report | none | unknown | procedure |
| EX-DEFER-9 | For every item an agent's structured return (`agents/pm.md` Final report, or `agents/analyst.md` `### Deferred refinements`) annotates `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` that the orchestrator does not address inline, create a `defer-<short-suffix>` task with the description as `metadata.activity`, `pending`. | command | L571; L478 | E3-060, E2-266 | `defer-*` task | destination annotations | TaskList | unknown | procedure |
| EX-DEFER-10 | Rationale: this pairs with the ignored-feedback instruction as the upstream source for 6.5's gate; otherwise PM deferrals reach the ledger only via Step 0's retroactive sweep. | rationale-only | L571 | E3-062 | - | - | none | unknown | rationale |
| EX-DEFER-11 | Rationale: walking the PM Final report here mirrors `/quo-breakdown-epic`'s per-Task PM-dispatch site, keeping the two-layer (upstream + Step 0) pattern symmetric. | rationale-only | L571 | E3-063 | - | - | none | unknown | rationale |
| EX-DEFER-12 | Mark a `defer-*` task `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (logged in `metadata.activity`). | ordering | L478 | E2-268 | `defer-*` flip | ticket update / Issue | TaskList, bees | unknown | procedure |
| EX-DEFER-13 | If Bee-level feedback does not require action, move on to Final Review but MUST share the ignored feedback there; feedback may be ignored (to avoid an infinite loop) so long as it is presented in Final Review. | relay | L916-917 §5 | E5-048, E5-049 | Final Review content | ignored findings | none | unknown | procedure |

---

## M22. Next-Epic routing & inter-Epic interaction checkpoint (`EX-NEXT`)

- **Purpose:** At each Epic boundary run the Director's own interaction check against prior Epics' code, flip the Epic `done`, re-query, and classify into exactly one of three branches (drafted-remain → stop; workable-remain → Mode 1 gate / Mode 2 auto-continue; all done → final review).
- **Failure it prevents:** `drafted` Epics falling through to final review; missing cross-Epic contract drift while context is fresh.
- **Env deps:** git, bees, Agent, TaskList, AskUserQuestion. TaskList-dependent: **yes** (Mode 1 gate).
- **Rows after dedupe:** 21 (procedure 19 · rationale 2 · example 0)
- **Literals:** `#### 4.2 Find next Epic or move to Final Review` · `inter-Epic interaction checkpoint` · `git log --oneline <previous-epic-last-commit>..HEAD` · `Contract drift` · `Resource compounding` · `Symmetric-change gaps` · `Drafted (or blocked-on-drafted) Epics remain` · `Workable Epic remains` · `All Epics under this Bee are \`done\`` · `Mode 1 (Stop after each Epic)` · `Mode 2 (Work through all Epics)` · `Mode 2 (Work through all Epics): auto-continuing to <next-epic-id> — <title>.` · branch-1 message `Epic \`<just-completed-epic-id>\` is complete, but Epics \`<drafted-or-blocked-ids>\` … are still \`drafted\` … Run \`/quo-breakdown-epic <bee-id>\` (a fresh session is reasonable …), then re-run \`/quo-execute <bee-id>\`.` · `drafted` → `ready` → `in_progress` → `done`
- **Cross-mechanism edges:** Produces for → CKPT (invoked on all five exit paths), CWG (two continuing paths), BEEREV (branch 3 / Mode 1 decline), EPIC (return to step 2), GATE. Consumes from → EPIC (run mode; shared query), MAN (`<previous-epic-last-commit>`), LOOP (all Tasks done).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-NEXT-1 | Before moving on from the just-completed Epic, perform the inter-Epic interaction checkpoint; the Director runs it directly — no new team. | ordering | L577-579 | E3-066, E3-068 | - | Epic completion | none | no | procedure |
| EX-NEXT-2 | Rationale: positioned at the Epic boundary (not final review) to catch this Epic's interactions with prior Epics' code while context is fresh. | rationale-only | L577 | E3-067 | - | - | none | no | rationale |
| EX-NEXT-3 | Interaction step 1: diff the Epic's landed commits with `git log --oneline <previous-epic-last-commit>..HEAD` (`<previous-epic-last-commit>` resolved per EX-CKPT-24). | command | L581 | E3-069 | commit list | `<previous-epic-last-commit>` | git | no | procedure |
| EX-NEXT-4 | Interaction step 2: for each file this Epic touched that a prior Epic also touched, scan for **Contract drift** (ordering contracts, docstring claims, "this should never happen" comments); **Resource compounding** (new acquires from a resource a prior Epic uses — model the aggregate); **Symmetric-change gaps** (a new resource class — search prior Epics' cleanup paths for missing handling). | command | L582-585 | E3-071, E3-072, E3-073 | findings | commit diffs | git | no | procedure |
| EX-NEXT-5 | Interaction step 3: if any issue is found, dispatch a fresh ephemeral Engineer per Section 3's dispatch shape to fix it before continuing; do not defer interaction fixes to the final Bee-level review. | command | L586 | E3-074, E3-075 | Engineer dispatch | findings | Agent | no | procedure |
| EX-NEXT-6 | Interaction step 4: record any fixes as additional, clearly labeled commits on the branch. | command | L587 | E3-076 | git commits | fix edits | git | no | procedure |
| EX-NEXT-7 | After the checkpoint passes (clean or fixed), mark the just-completed Epic `status=done`. | command | L589-591 | E3-077 | Epic status flip | EX-NEXT-1..6 | bees | no | procedure |
| EX-NEXT-8 | Then re-query all Epics under the Bee (EX-EPIC-1 query) to classify the post-Epic state; do not assume "no workable Epic remains" means "Bee is finished" — `status=drafted` Epics must not fall through to final review. | command | L591 | E3-078, E3-079 | Epic list | Bee ID | bees | no | procedure |
| EX-NEXT-9 | Classify into exactly one of three branches, evaluated in listed order; branch 1 takes precedence over branch 2 when both apply. | choice-set | L601 | E3-083, E3-085 | branch selection | Epic + dependency statuses | none | no | procedure |
| EX-NEXT-10 | The Plans hive status vocabulary `drafted` → `ready` → `in_progress` → `done` is canonical. | definition | L601 | E3-084 | - | - | none | no | procedure |
| EX-NEXT-11 | Rationale: any drafted Epic must stop the loop regardless of whether other Epics are workable. | rationale-only | L601 | E3-086 | - | - | none | no | rationale |
| EX-NEXT-12 | Branch 1 (**Drafted (or blocked-on-drafted) Epics remain**) — at least one Epic is `drafted`, or `ready` but blocked on a not-`done` dependency: stop the loop; do NOT proceed to Step 5 final review and do NOT offer to mark the Bee done. | command | L603 | E3-087, E3-088, E3-089 | run exit | Epic/dependency statuses | none | no | procedure |
| EX-NEXT-13 | Branch 1 message: `Epic \`<just-completed-epic-id>\` is complete, but Epics \`<drafted-or-blocked-ids>\` … are still \`drafted\` … Run \`/quo-breakdown-epic <bee-id>\` (a fresh session is reasonable …), then re-run \`/quo-execute <bee-id>\`.` | field-or-template | L605 | E3-090 | printed message | Epic IDs; Bee ID | none | no | procedure |
| EX-NEXT-14 | Branch 1: after the message, run the Epic-boundary state-externalization checkpoint (next unit `none`) and exit the skill. | ordering | L607 | E3-091 | checkpoint; exit | - | none | no | procedure |
| EX-NEXT-15 | Branch 2 (**Workable Epic remains**) — no drafted Epics and at least one Epic `ready`/`in_progress` with all `up_dependencies` `done`: branch on the multi-Epic run mode captured in Section 2. | ordering | L609; L262 | E3-092, E3-093, E2-027 | - | run mode | none | no | procedure |
| EX-NEXT-16 | Mode 1 (`Stop after each Epic`), or the mode prompt was skipped (single Epic in scope at run start): ask the user whether to continue with the next logical Epic (two-step gate). | gate | L611; L259 | E3-094, E2-019 | AskUserQuestion | run mode | TaskList, AskUserQuestion | no | procedure |
| EX-NEXT-17 | Mode 1 accept: run the state-externalization checkpoint (next unit = next Epic's ID), then the context-window guard (may stop the run), then return to step 2. | ordering | L611 | E3-095 | checkpoint; guard | answer | none | no | procedure |
| EX-NEXT-18 | Mode 1 decline: run the checkpoint (next unit `none`) but NOT the context-window guard, then move to final Bee review. | ordering | L611 | E3-096 | checkpoint | answer | none | no | procedure |
| EX-NEXT-19 | Mode 2 (`Work through all Epics`): auto-continue without a gate, surfacing a one-line note naming the next Epic, e.g. `Mode 2 (Work through all Epics): auto-continuing to <next-epic-id> — <title>.`; then run the checkpoint (next unit = next Epic), then the guard, then return to step 2. | command | L612 | E3-098, E3-099, E3-100 | printed note; checkpoint; guard | run mode | none | no | procedure |
| EX-NEXT-20 | Mode 2 still respects every other stop: branch 1's drafted-or-blocked stop takes precedence (the loop must exit so the user can run `/quo-breakdown-epic`), and any final reviewer-surfaced blocker the orchestrator escalates from Sections 5 and 6 halts the run. | invariant | L612; L260 | E3-101, E2-021, E2-022 | - | - | none | no | procedure |
| EX-NEXT-21 | Branch 3 (**All Epics under this Bee are `done`**): run the checkpoint (next unit `none`), then proceed to Step 5 final Bee review. | ordering | L614 | E3-102 | checkpoint | Epic statuses | none | no | procedure |

---

## M23. Epic-boundary state-externalization checkpoint (`EX-CKPT`)

- **Purpose:** At every exit from Section 4.2 (and from the aborted close-out) verify the five durable carriers — bees statuses, git commits, compromise tracker, `defer-*` ledger, run-state manifest — fix any gap, rewrite the manifest, and re-read (never recall) in the next Epic.
- **Failure it prevents:** A run that cannot be re-derived after harness compaction; inverted or masked verifications on the two aborted scopes.
- **Env deps:** bees, git, TaskList, Bash, Read/Write. TaskList-dependent: **yes** (carrier 4 and verification 4).
- **Rows after dedupe:** 32 (procedure 31 · rationale 1 · example 0)
- **Literals:** `##### Epic-boundary state-externalization checkpoint` · `Verify the carriers.` · `Rewrite the run-state manifest` · `Re-read, do not recall, at every dispatch in the next Epic.` · `Aborted-path qualification — mid-Epic scope.` · `Aborted-path qualification — Bee-level scope.` · `Exception — the all-Epics-already-done-at-run-start path.` · `git log --oneline <previous-epic-last-commit>..HEAD` · `Pre-Bee SHA` · `Progress` · `Compromise tracker` · `Epics in scope` · `Multi-Epic run mode` · `not captured (all Epics already done)` · `pending Section 2 query` · `not captured` · `none`
- **Cross-mechanism edges:** Produces for → MAN (step 2 rewrite), NEXT/ABORT (invoked by name), PCR. Consumes from → MAN, CLEAN (commits), TRK (tracker), DEFER (ledger), TL, ABORT (scope resolution), EPIC (placeholders resolved).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-CKPT-1 | `##### Epic-boundary state-externalization checkpoint` is the canonical anchor; other sections refer to it as the *Epic-boundary state-externalization checkpoint*. | definition | L616-618 | E3-103 | - | - | none | no | procedure |
| EX-CKPT-2 | Every path out of Section 4.2's three branches invokes the checkpoint by name on all five exit paths, and `##### Aborted-run close-out` invokes it on the run-aborting path (next unit `none`); there is no way to leave 4.2 without running it. | definition | L618, L656, L664 | E3-104, E3-163, E3-166 | - | - | none | no | procedure |
| EX-CKPT-3 | Exit paths: branch 2 Mode 1 accept and Mode 2 auto-continue (next unit = next Epic's ID); branch 2 Mode 1 decline, branch 1 breakdown exit, branch 3 final review (next unit `none`). The three `none` paths still run it in full — what it verifies and writes outlives the conversation. | definition | L658-662 | E3-164, E3-165 | - | - | none | no | procedure |
| EX-CKPT-4 | The checkpoint is a definition, not a step in 4.2's linear flow — do not run it because reading reached its heading; run it only when an invoking branch calls for it, always after branch classification (step 2's next unit is unknown until then). | invariant | L618 | E3-105, E3-106 | - | branch classification | none | no | procedure |
| EX-CKPT-5 | Mode 2 still performs the checkpoint at every Epic boundary; it is a set of verify-and-write steps the orchestrator runs itself, not a pause — it never prompts the user. | invariant | L260 §2 | E2-023, E2-024 | - | - | none | no | procedure |
| EX-CKPT-6 | Rationale: Section 3's flat orchestration makes orchestrator context grow monotonically across Epics; nothing reclaims it; the Epic boundary is where the run is most re-derivable. | rationale-only | L620 | E3-107 | - | - | none | no | rationale |
| EX-CKPT-7 | On the aborted path, what "re-derivable" means depends on the scope close-out step 2 resolved — read off the entering branch, since the routing-gate `Cancel` branch opens no marker. | definition | L620 | E3-108 | - | entering branch | none | no | procedure |
| EX-CKPT-8 | A **mid-Epic** abort (per-Task writer lane, or routing-gate `Cancel` at the per-Task review site) leaves the Epic deliberately incomplete with fewer commits than Tasks; a **Bee-level-review** abort (Section 5 Bee-scoped lane, or `Cancel` at Section 5's review) leaves every Epic/Task `done` and every per-Task commit landed, stopping short of final review. | definition | L620 | E3-109, E3-110 | - | - | none | no | procedure |
| EX-CKPT-9 | The checkpoint's job is to verify the re-derivability invariant and refresh the durable carriers so the run can be re-derived after any harness compaction. | definition | L620; L436 | E3-113, E2-206 | - | - | none | no | procedure |
| EX-CKPT-10 | Carrier 1 — bees ticket statuses: just-completed Epic, its Tasks and Subtasks `done`; the Bee `in_progress`; re-readable via `bees show-ticket` / `bees execute-freeform-query`. | definition | L624 | E3-114 | - | bees | bees | no | procedure |
| EX-CKPT-11 | Carrier 2 — git commits: one per Task (Section 4.1) plus any interaction-checkpoint fix commits; re-readable via `git log` / `git diff`. | definition | L625 | E3-115 | - | git history | git | no | procedure |
| EX-CKPT-12 | Carrier 3 — the session-scoped compromise tracker (Section 6.5); re-readable via `Read`. | definition | L626 | E3-116 | - | tracker file | none | unknown | procedure |
| EX-CKPT-13 | Carrier 4 — the `defer-*` TaskList ledger Section 6.5's gate reads; re-readable by walking the TaskList. | definition | L627 | E3-117 | - | TaskList | TaskList | unknown | procedure |
| EX-CKPT-14 | Carrier 5 — the run-state manifest (Section 1): run mode, isolation strategy, `<pre-bee-sha>`, tracker path, per-Epic progress; re-readable via `Read`. | definition | L628 | E3-118 | - | manifest | none | yes | procedure |
| EX-CKPT-15 | When invoked, run the three steps before the invoking branch does whatever it does next (return to step 2, final review, or exit). | ordering | L630 | E3-119 | - | - | none | no | procedure |
| EX-CKPT-16 | Every checkpoint step is a tool call the orchestrator can actually make — read a file, run a bees query, run a git command, walk the TaskList, write a file. | invariant | L630 | E3-120 | - | - | Bash, bees, git, TaskList | no | procedure |
| EX-CKPT-17 | Step 1 **Verify the carriers**: do all four verifications, subject to three qualifications each applying only on the path it names; on every other path all four run as written. | command | L632 | E3-121 | verification results | - | bees, git, TaskList | no | procedure |
| EX-CKPT-18 | Mid-Epic qualification (invoked from close-out at mid-Epic scope): the first two verifications invert rather than fail — confirm the current Epic and its Tasks read the status the abort left them at (not all `done`, not to be flipped); verify only that every completed Task has its commit, not reporting the aborted Task's missing commit as a gap; tracker and TaskList verifications run unchanged. | precondition | L634 | E3-122, E3-123, E3-124, E3-125 | - | close-out scope | bees, git, TaskList | no | procedure |
| EX-CKPT-19 | Bee-level qualification (aborted Section 5 lane `aborted-<role>-<bee-id>`, or `Cancel` at Section 5's review): nothing inverts; run all four normally; treat any genuine status or one-commit-per-Task shortfall as a real gap (subject to the precedence carve-out); do not import the mid-Epic qualification (it would mask a real gap); "just-completed Epic" = the last Epic this run completed, so re-verifying is idempotent whenever this session completed an Epic. | precondition | L635 | E3-126, E3-127, E3-128, E3-129 | - | close-out scope | bees, git, TaskList | no | procedure |
| EX-CKPT-20 | Precedence: when the run started with every Epic `done`, went straight to Section 5, and a Bee-scoped abort or `Cancel` occurred there, the all-Epics-already-done exception governs over the Bee-level qualification — the four verifications stay vacuous and are skipped; verify only that Section 2's placeholders resolved; only step 2's Bee-level **Progress** append applies and no `done` Epic entry is touched. | ordering | L635 | E3-130, E3-131 | manifest Progress append | run history | none | no | procedure |
| EX-CKPT-21 | Exception — all-Epics-already-done-at-run-start: when branch 3 is entered because Section 2's query found every Epic `done` and this session completed none, skip the four verifications; verify only that `#### Resolve the manifest placeholders` resolved both placeholders (real Epic IDs under **Epics in scope**, `not captured (all Epics already done)` under **Multi-Epic run mode** — never `pending Section 2 query` or bare `not captured`); then go to step 2 and write next unit `none`. | precondition | L636 | E3-132, E3-133, E3-134, E3-135 | manifest next unit `none` | Section 2 result; manifest | none | no | procedure |
| EX-CKPT-22 | Verification 1: re-query the just-completed Epic and its Task/Subtask children in bees and confirm every one reads `done`. | command | L640 | E3-136 | result | bees | bees | no | procedure |
| EX-CKPT-23 | Verification 2: run `git log --oneline <previous-epic-last-commit>..HEAD` and confirm one commit exists per completed Task. | command | L641 | E3-137 | result | `<previous-epic-last-commit>` | git | no | procedure |
| EX-CKPT-24 | `<previous-epic-last-commit>` resolves from the run-state manifest, not memory: **Pre-Bee SHA** at the run's first Epic boundary; the previous Epic's `last commit <sha>` under **Progress** at every later boundary. | definition | L581; L641 | E3-070, E3-138 | - | manifest fields | none | no | procedure |
| EX-CKPT-25 | Verification 3: `Read` the tracker at the path in the manifest's **Compromise tracker** field and confirm every compromise accepted during this Epic has an entry. | command | L642 | E3-139 | result | manifest; tracker file | none | unknown | procedure |
| EX-CKPT-26 | A `Read` reporting the tracker does not exist is not by itself a gap ("nothing was appended"); treat an absent entry as a gap only if a compromise was accepted, or an ungated pick Trigger C requires an entry for was dispatched, during this Epic; a unit whose sole ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less. | invariant | L642 | E3-140, E3-141, E3-142 | - | `Read` result; Epic history | none | unknown | procedure |
| EX-CKPT-27 | Verification 4: walk the TaskList and confirm every per-Subtask, per-Task and `gate-*` task from this Epic is `completed`. | command | L643 | E3-143 | result | TaskList | TaskList | no | procedure |
| EX-CKPT-28 | Fix any gap now — flip the missed status, land the missed commit, append the missed tracker entry, close the stale TaskList task — rather than carrying it forward in conversation. | recovery | L645 | E3-144 | fixes | verification results | bees, git, TaskList | no | procedure |
| EX-CKPT-29 | Step 2 **Rewrite the run-state manifest** per Section 1, recording the just-completed Epic's ID and last commit SHA under Progress, and the next unit: the next Epic's ID on paths that pick one up, or `none` on branch 1's exit, Mode 1 decline, branch 3's final review, and both aborted scopes. | command | L646, L651 | E3-145, E3-146, E3-151 | manifest rewrite | Epic ID; SHA; branch | none | yes, no | procedure |
| EX-CKPT-30 | On the aborted path the Progress write branches on the scope close-out step 2 resolved, read off the entering branch (shapes per EX-MAN-42/43). | ordering | L646 | E3-147 | manifest Progress | entering branch | none | no | procedure |
| EX-CKPT-31 | Step 3 **Re-read, do not recall**: before each Agent dispatch in the next Epic, `bees show-ticket` the Epic/Task/Subtask body and `Read` the manifest for run-scoped values (mode, isolation strategy, tracker path, `<pre-bee-sha>`); carry no value forward from the prior Epic; never reuse a value quoted earlier in the conversation. | command | L652 | E3-152, E3-153 | - | bees bodies; manifest | bees | no | procedure |
| EX-CKPT-32 | If a fact the next Epic needs is not readable from one of the five carriers, stop and write it into one before dispatching anything. | recovery | L652 | E3-154 | carrier write | five carriers | none | no | procedure |

---
## M24. Epic-boundary context-window guard (`EX-CWG`)

- **Purpose:** On the two continuing in-session paths only, read the external status-line gauge via `context_gauge.py` and stop for a fresh session when usage is at/over the helper's threshold, is stale, or is unreadable; on `missing`, ask (or honor the persistent opt-out).
- **Failure it prevents:** Continuing into the next Epic on a context window that will compact mid-Epic; a stranded `pending` gate task; the skill carrying a second definition of the threshold.
- **Env deps:** Bash, TaskList, AskUserQuestion, Skill tool. TaskList-dependent: **yes** (missing-reading gate).
- **Rows after dedupe:** 28 (procedure 26 · rationale 2 · example 0)
- **Literals:** `##### Epic-boundary context-window guard` · `What this guard is (and is not).` · `CLAUDE_CODE_SESSION_ID` · `printenv CLAUDE_CODE_SESSION_ID` · `Write-Output $env:CLAUDE_CODE_SESSION_ID` · `context_gauge.py` · `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` · `<this skill's base directory>\..\quo-setup\scripts\context_gauge.py` · `stop-threshold` · `read --session-id <trimmed-session-id>` · `write-opt-out` · `no-reading` · `stale` · `missing` · `<tempdir>/.quorum/context-guard-opt-out` · `test -f /tmp/.quorum/context-guard-opt-out` · `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"` · `<tempdir>/.quorum/context-usage-<session_id>.json` · `session_id` · `context_window` · `used_percentage` · `Configure now` · `Proceed without the guard (this run)` · `Never guard me (persistent opt-out)` · `Stop here` · `/quo-setup --configure-gauge-producer` · `/quo-execute <bee-id>`
- **Cross-mechanism edges:** Produces for → NEXT (may stop the run), GATE. Consumes from → CKPT (runs after it), EFF (mirrors read-before-TaskCreate ordering), PCR (external gauge is the permitted reading), SMW (sibling-resolution pattern), `quo-setup`'s `context_gauge.py`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-CWG-1 | The guard is a definition, not a step in 4.2's linear flow; run it only where an invoking branch calls for it by name. | invariant | L666-668 | E3-168 | - | - | none | no | procedure |
| EX-CWG-2 | Exactly two paths invoke it: branch 2's Mode 1 accept and Mode 2 auto-continue (next unit = next Epic's ID on both). | definition | L668-671 | E3-169 | - | - | none | no | procedure |
| EX-CWG-3 | The guard runs after the state-externalization checkpoint completes and before control returns to step 2. | ordering | L673 | E3-170 | - | checkpoint completion | none | no | procedure |
| EX-CWG-4 | The guard never runs on a `next unit: none` run-ending path — not branch 1's exit, not Mode 1 decline, not branch 3's final review, not the aborted close-out. | invariant | L611; L673; L787 | E3-097, E3-171, E3-247 | - | - | none | no | procedure |
| EX-CWG-5 | Rationale: on a run ending in-session a fresh-session stop is noise, and a missing-reading gate would fire `AskUserQuestion` right before final review. | rationale-only | L673 | E3-172 | - | - | none | no | rationale |
| EX-CWG-6 | A single-Epic run that crosses no Epic boundary never reaches the guard. | definition | L673 | E3-173 | - | - | none | no | procedure |
| EX-CWG-7 | The checkpoint is unconditional on every exit path; the guard deliberately is not — do not inherit its unconditionality. | invariant | L673 | E3-174 | - | - | none | no | procedure |
| EX-CWG-8 | The guard reads an external gauge a separate status-line producer wrote to a file (the `context_gauge.py` producer/reader contract); it does not measure the orchestrator's own token usage. | definition | L675 | E3-175 | - | gauge file | Bash | no | procedure |
| EX-CWG-9 | Neither the read nor the boundary stop reclaims context; the only lever is a fresh session, which every guard stop recommends; do not add any "clear your working context" instruction — no self-clear/self-compact lever exists. | invariant | L675 | E3-176, E3-177 | - | - | none | no | procedure |
| EX-CWG-10 | Step 1: read the session id first and evaluate it before creating any gate task (mirroring `#### Check session reasoning effort`); do NOT `TaskCreate` before the evaluation — a stranded `pending` `gate-*` task violates yield-control. | ordering | L679 | E3-178, E3-179 | - | `CLAUDE_CODE_SESSION_ID` | Bash, TaskList | no | procedure |
| EX-CWG-11 | Session-id read: `printenv CLAUDE_CODE_SESSION_ID` (POSIX) / `Write-Output $env:CLAUDE_CODE_SESSION_ID` (PowerShell); trim trailing whitespace/newline before use (a trailing newline fails the helper's `--session-id` validation). | command | L681-691 | E3-180, E3-181 | trimmed session id | environment | Bash | no | procedure |
| EX-CWG-12 | Step 2: session id unset or empty → skip the guard silently and continue to step 2 of branch 2 — no gate, no `TaskCreate`, no output; this is the only silent-skip path (the unsupported-CLI carve-out). | precondition | L693 | E3-182, E3-183 | - | session id | none | no | procedure |
| EX-CWG-13 | Step 3a: resolve the gauge helper as a sibling of this skill's base directory: `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (PowerShell `…\..\quo-setup\scripts\context_gauge.py`). | command | L697-707 | E3-184 | helper path | base directory | none | no | procedure |
| EX-CWG-14 | Step 3b: obtain the stop threshold with one literal call `python3 "<…>/context_gauge.py" stop-threshold` (PowerShell `python …\context_gauge.py stop-threshold`) — prints one integer percentage; NEVER restate the threshold in prose, so the skill carries no second definition site. | command | L709-719 | E3-185, E3-186 | threshold integer | helper path | Bash | no | procedure |
| EX-CWG-15 | Step 3c: read the current reading with `python3 "<…>/context_gauge.py" read --session-id <trimmed-session-id>` (PowerShell `python …`). | command | L721-731 | E3-187 | reading (stdout + exit) | trimmed session id | Bash | no | procedure |
| EX-CWG-16 | Step 3d: branch on stdout and exit status. `read` prints exactly one of an integer percentage, `no-reading`, `stale`, `missing` and exits `0` for all four; it exits non-zero on a malformed gauge OR an invalid `--session-id` — do NOT assume non-zero implies a corrupt file. | ordering | L733 | E3-188, E3-189, E3-190 | - | reading | Bash | no | procedure |
| EX-CWG-17 | Integer ≥ threshold → STOP at this boundary: report the current percentage, recommend resuming in a fresh session with `/quo-execute <bee-id>`, exit the skill. | choice-set | L735 | E3-191 | report; exit | reading; threshold | none | no | procedure |
| EX-CWG-18 | Integer < threshold, or `no-reading` (transient fresh-but-null reading; producer alive) → continue to step 2 of branch 2, no output. | choice-set | L736-737 | E3-192, E3-193 | - | reading | none | no | procedure |
| EX-CWG-19 | `stale` → STOP; note the producer appears stalled and that recurring staleness across fresh sessions means the operator should check their status-line producer; recommend `/quo-execute <bee-id>` fresh-session resume. Do NOT let `stale` fall through to continue. | choice-set | L738 | E3-194, E3-195 | report; exit | reading | none | no | procedure |
| EX-CWG-20 | Non-zero exit or empty stdout → the same fail-safe stop-and-ask as `stale`; never fall through to continue. | choice-set | L739 | E3-196 | report; exit | exit status | none | no | procedure |
| EX-CWG-21 | `missing` → first check the persistent opt-out marker `<tempdir>/.quorum/context-guard-opt-out` with one literal existence check: `test -f /tmp/.quorum/context-guard-opt-out` (POSIX) / `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"` (PowerShell). | command | L740-750 | E3-197, E3-198 | marker presence | filesystem | Bash | no | procedure |
| EX-CWG-22 | Marker present → skip the guard silently and continue (operator's standing choice); marker absent → hard-stop via the two-step gate in step 4. | choice-set | L752 | E3-199, E3-200 | - | marker presence | TaskList, AskUserQuestion | no | procedure |
| EX-CWG-23 | Step 4 — missing-reading gate (two-step contract per EX-GATE-2/3/6/7). Question text: (a) the environment may override the operator's user-level status-line config, so no reading is being published; (b) the gauge file contract — path `<tempdir>/.quorum/context-usage-<session_id>.json`, required fields `session_id` and a `context_window` object carrying `used_percentage`, overwrite-per-refresh; (c) `Configure now` runs `/quo-setup --configure-gauge-producer` inline. | field-or-template | L754 | E3-204, E3-205, E3-206 | question text | - | AskUserQuestion | no | procedure |
| EX-CWG-24 | Option 1 `Configure now`: invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool; on success recommend resuming in a fresh session with `/quo-execute <bee-id>` rather than implying this run is now guarded, then exit. | choice-set | L756 | E3-208, E3-209 | Skill invocation; exit | answer | none | no | procedure |
| EX-CWG-25 | Rationale: a freshly-configured producer only begins publishing next session. | rationale-only | L756 | E3-210 | - | - | none | no | rationale |
| EX-CWG-26 | Option 2 `Proceed without the guard (this run)`: continue to step 2 of branch 2; write no marker. | choice-set | L757 | E3-211 | - | answer | none | no | procedure |
| EX-CWG-27 | Option 3 `Never guard me (persistent opt-out)`: write the marker via `python3 "<…>/context_gauge.py" write-opt-out` (PowerShell `python …\context_gauge.py write-opt-out`), then continue. | choice-set | L758-768 | E3-212 | opt-out marker | answer | Bash | no | procedure |
| EX-CWG-28 | Option 4 `Stop here`: exit the skill with the `/quo-execute <bee-id>` fresh-session resume command. | choice-set | L770 | E3-213 | exit | answer | none | no | procedure |

---

## M25. Aborted-run close-out (`EX-ABORT`)

- **Purpose:** When the run stops without its unit advancing (unexplained-movement `Abort this unit`, or `Cancel` at either routing gate), sweep the TaskList at the right scope, run the checkpoint on its aborted path, and stop naming the working-tree state and `/quo-execute <bee-id>`.
- **Failure it prevents:** An `aborted-*` marker and half-swept TaskList surviving into the next session, where part (g)'s Clause 2 wedges the first Engineer dispatch, and a manifest claiming a next unit never picked up.
- **Env deps:** TaskList, bees, git, Agent. TaskList-dependent: **yes**.
- **Rows after dedupe:** 20 (procedure 16 · rationale 3 · example 0 · failure-narrative 1)
- **Literals:** `##### Aborted-run close-out` · `Abort this unit` · `Cancel` · `Per-Task scope` · `Bee scope` · `Close out the TaskList, sweeping by name prefix.` · `Stop the run and name the resume command.` · `mid-Epic` · `Bee-level` · `/quo-execute <bee-id>` · `Ctrl-C`
- **Cross-mechanism edges:** Produces for → CKPT (aborted path + scope), MAN (aborted Progress shapes), TL. Consumes from → UMG (Abort), ROUTE (Cancel at (c)/(d)), CLEAN (per-Task sweep list), BEEREV (Bee-level close-out list), MOV (markers).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-ABORT-1 | `##### Aborted-run close-out` is the canonical anchor for the path where the run stops without the unit it was working advancing. | definition | L772-774 | E3-214 | - | - | none | unknown | procedure |
| EX-ABORT-2 | Three branches route here: Section 3's unexplained-movement gate `Abort this unit`; the routing-decision gate's `Cancel` (part (d)); the scope-bounding gate's `Cancel` (part (c), offered only in a `blocker`'s choice set). | definition | L664; L774 | E3-167, E3-215 | - | gate answers | none | unknown | procedure |
| EX-ABORT-3 | The two `Cancel` branches behave identically here; wherever this skill branches on the routing-gate `Cancel`, read it as covering either gate's `Cancel`. | invariant | L774 | E3-216 | - | - | none | unknown | procedure |
| EX-ABORT-4 | The close-out is a definition, not a step in 4.2's linear flow; run it only where a branch calls for it by name. | invariant | L774 | E3-217 | - | - | none | unknown | procedure |
| EX-ABORT-5 | Failure narrative: simply stopping lets an `aborted-*` marker and half-swept TaskList survive into the next session, where Clause 2 wedges the first Engineer dispatch, and leaves the manifest claiming a next unit never picked up. | rationale-only | L776 | E3-218 | - | - | none | unknown | failure-narrative |
| EX-ABORT-6 | Run the close-out's three steps in order. | ordering | L776 | E3-219 | - | - | none | unknown | procedure |
| EX-ABORT-7 | Step 1 — close out the TaskList sweeping by name prefix, at the scope of the aborted lane or, on a routing-gate `Cancel`, the review site the gate fired from. | command | L778; L833; L853 | E3-220, E4-078, E4-145 | tasks → `completed` | aborted lane / review site | TaskList | unknown, diverges | procedure |
| EX-ABORT-8 | Per-Task scope: every `<role>-<subtask-id>` implementer task under the affected Task, that Task's `pm-<task-id>`, every `-r<n>` round of any of them, and the `gate-*` task that fired the branch routing here — Section 4.1 step 3's sweep run at an abort instead of a Task completion. | name-class | L780 | E3-221, E3-222 | tasks → `completed` | TaskList names | TaskList | unknown | procedure |
| EX-ABORT-9 | Bee scope (aborted Section 5 Bee-scoped lane, or `Cancel` at Section 5's review site): every `*-<bee-id>` name Section 5's Bee-level close-out enumerates (three reviewers, four implementer/PM names, their `-r<n>` rounds), plus the `gate-*` task that fired the branch. | name-class | L781 | E3-223, E3-224 | tasks → `completed` | TaskList names | TaskList | no | procedure |
| EX-ABORT-10 | Rationale: Section 5's enumeration carries no `gate-*` name, so a `Cancel` there would otherwise strand its own gate task `pending`. | rationale-only | L781 | E3-225 | - | - | none | no | rationale |
| EX-ABORT-11 | The orchestrator cannot terminate a dispatched background Agent; an `in_progress` task may still have a live Agent — mark an in-flight sibling lane's task `completed` anyway (the run is ending; no tick will consume its notification), recording in `metadata.activity` that it was in flight at the abort so a resuming session re-checks the lane's work instead of trusting ticket state. | command | L783 | E3-226, E3-227, E3-228 | task → `completed`; `metadata.activity` | in-flight task | TaskList, Agent | unknown | procedure |
| EX-ABORT-12 | In both scopes mark every `aborted-<role>-<id>` marker still `pending` as `completed` when one is open (the movement-gate branch arrives with a marker open; a routing-gate `Cancel` opens none), recording the abort reason in its `metadata.activity` — informational, never a routing input. | command | L785 | E3-229, E3-230, E3-232 | marker → `completed` | open markers | TaskList | unknown | procedure |
| EX-ABORT-13 | Rationale: a marker left `pending` blocks the unit's advance in a later session. | rationale-only | L785 | E3-231 | - | - | none | unknown | rationale |
| EX-ABORT-14 | Step 2 — run the Epic-boundary state-externalization checkpoint on its aborted path (step 1 with the matching aborted-path qualification, step 2 with the scope-branched aborted Progress entry and next unit `none`); pick the qualification for the scope this close-out was entered at, read off the entering branch, not off a marker; everything else in the checkpoint runs unchanged. | command | L786; L833; L853 | E3-235, E3-236, E3-239, E4-079 | checkpoint; manifest rewrite | close-out scope | bees, git, TaskList | no | procedure |
| EX-ABORT-15 | Scope resolution — movement-gate branch: an `aborted-<role>-<subtask-id>` marker ⇒ mid-Epic; a Section 5 Bee-scoped lane ⇒ Bee-level. Routing-gate `Cancel` branch: the per-Task review site ⇒ mid-Epic; Section 5's review ⇒ Bee-level. | definition | L786 | E3-237, E3-238 | resolved scope | aborted lane / review site | none | no | procedure |
| EX-ABORT-16 | Step 3 — stop the run and tell the user it stopped without the unit advancing: for a per-Task lane abort name which Subtask and Task; for a Section 5 Bee-scoped lane name the lane (`test-writer-<bee-id>` / `doc-writer-<bee-id>`) and say the run stopped in the Bee-level review (every Subtask/Task `done`); on a routing-gate `Cancel` name the review site and the finding it fired on, in place of a lane name. | command | L787 | E3-240, E3-241, E3-242, E3-243 | printed message | scope; lane / site; finding | none | unknown, no | procedure |
| EX-ABORT-17 | Also name the uncommitted working-tree state the exit leaves behind: at mid-Epic scope the in-flight Task's edits; at Bee-level scope any Bee-level Engineer round's edits since the last per-Task commit. | field-or-template | L787; L833; L853 | E3-244, E4-080, E4-146 | printed message | working tree | git | no | procedure |
| EX-ABORT-18 | Rationale: a resuming session inherits that tree either way, so say what is in it rather than leaving it to be discovered. | rationale-only | L787 | E3-245 | - | - | none | unknown | rationale |
| EX-ABORT-19 | Then name the literal resume command `/quo-execute <bee-id>` — the same command every other stop site names — and exit the skill. | command | L787 | E3-246 | resume command; exit | Bee ID | none | no | procedure |
| EX-ABORT-20 | Execute mode has no Issue concept and its abort always ends the run, so a routing-gate `Cancel` does not proceed to the next Task; `Ctrl-C` remains the unconditional run-level abort. | invariant | L833; L853 | E4-082, E4-083, E4-147 | - | - | none | diverges, yes | procedure |

---

## M26. Engineer-dispatch precondition (Clause 1 / Clause 2) (`EX-EDP`)

- **Purpose:** Never dispatch an Engineer for a review-finding re-dispatch while any writer or reviewer/PM lane at that site is `pending`/`in_progress`, keyed on TaskList name prefix plus status.
- **Failure it prevents:** Handing a writer a diff a pending code review is about to rewrite; a deadlock on a `pending` task that never notifies.
- **Env deps:** TaskList, Agent, bees. TaskList-dependent: **yes** (the precondition is a TaskList lookup).
- **Rows after dedupe:** 20 (procedure 15 · rationale 5 · example 0)
- **Literals:** `Clause 1 — the per-Task review site` · `Clause 2 — the Bee-level review site` · `test-writer-<subtask-id>` · `doc-writer-<subtask-id>` · `pm-<task-id>` · `engineer-<bee-id>` · `test-writer-<bee-id>` · `doc-writer-<bee-id>` · `code-reviewer-<bee-id>` · `test-reviewer-<bee-id>` · `doc-reviewer-<bee-id>` · `pm-<bee-id>` · `doc-writer-<subtask-id>-r1` · `code-reviewer-<bee-id>-r1` · `pm-<bee-id>-r2` · `aborted-` · `bees show-ticket --ids <subtask-id>` · `Scope limit — this part governs the review-finding re-dispatch path only.`
- **Cross-mechanism edges:** Produces for → ROUTE part (g) (checkability), MOV (ordering after movement), POST (freeze restated on postcomp names). Consumes from → TL (name classes, prefix rule), LOOP (no clock primitives), BEEREV (Clause 2 applies to Section 5 findings), MOV (aborted markers exempt by name class).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-EDP-1 | The Engineer-dispatch precondition that makes part (g) checkable is TaskList-derived. | definition | L867 | E4-170 | - | TaskList | TaskList | diverges | procedure |
| EX-EDP-2 | It has two clauses because findings come from two review sites with different diff extents; apply the clause for the site the finding came from. | precondition | L867 | E4-171 | - | finding's review site | TaskList | no | procedure |
| EX-EDP-3 | In both clauses match on TaskList name prefix plus status, not exact name, so any `-r<n>` a re-dispatch appends is caught (`doc-writer-<subtask-id>-r1`, `code-reviewer-<bee-id>-r1`, `pm-<bee-id>-r2`, …). | precondition | L867; L869; L878 | E4-172, E4-178, E4-186 | - | TaskList names | TaskList | yes, no | procedure |
| EX-EDP-4 | Rationale: TaskList is one of the four authoritative read-state sources read every tick, so either clause is a state lookup, not a rule held across compaction. | rationale-only | L867 | E4-173 | - | - | TaskList | no | rationale |
| EX-EDP-5 | Clause 1 applies to findings from the per-Task PM Agent (driving `/quo-engineer-review` and `/quo-doc-writer-review` in flight per `agents/pm.md`); its scope is the Task under review. | definition | L869 | E4-174 | - | finding origin | none | no | procedure |
| EX-EDP-6 | Clause 1: MUST NOT dispatch an Engineer for a Task while any TaskList task named `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` (Subtask of that Task) or that Task's `pm-<task-id>` is `pending` or `in_progress`. | precondition | L869 | E4-175 | Engineer dispatch (gated) | TaskList | TaskList, Agent | no | procedure |
| EX-EDP-7 | Resolve each active writer task's Subtask to its parent Task via `bees show-ticket --ids <subtask-id>` (read `parent`) before comparing against the Task under review. | command | L869 | E4-177 | parent Task id | subtask id in task name | bees, TaskList | no | procedure |
| EX-EDP-8 | Rationale: the PM is in Clause 1's list because it runs the review — Engineer edits landing under an in-flight `pm-<task-id>` invalidate the review whose findings are being routed. | rationale-only | L869 | E4-179 | - | - | none | no | rationale |
| EX-EDP-9 | Clause 2 applies to Section 5's Bee-level review, where reviewers are Bee-scoped (`<reviewer>-<bee-id>`) and the diff spans every Task; its scope is the whole Bee; findings routed from Section 5 take it. | definition | L871; L912 §5 | E4-180, E5-038 | - | finding origin | none | no | procedure |
| EX-EDP-10 | Clause 2: MUST NOT re-dispatch an Engineer — Bee-scoped (`engineer-<bee-id>`) or Subtask-scoped — while any TaskList task beginning with a listed prefix is `pending` or `in_progress`. | precondition | L871 | E4-181 | Engineer dispatch (gated) | TaskList | TaskList, Agent | no | procedure |
| EX-EDP-11 | Clause 2 prefix list: `test-writer-<subtask-id>` / `doc-writer-<subtask-id>` for any Subtask anywhere in the Bee; the Bee-scoped writers `test-writer-<bee-id>`, `doc-writer-<bee-id>`; the Bee-level reviewers `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`; any `pm-<task-id>` and the Bee-scoped `pm-<bee-id>`. | name-class | L873-876 | E4-182, E4-183, E4-184, E4-185 | - | TaskList names | TaskList | no | procedure |
| EX-EDP-12 | Rationale: the Bee-level Code Reviewer is in Clause 2's list (unlike Clause 1's PM-only coverage) because Section 5 dispatches the three reviewers concurrently; an Engineer re-entering waits for all live reviewer returns, which notify, so the wait ends — no deadlock. | rationale-only | L878 | E4-187, E4-188 | - | - | Agent | diverges, no | rationale |
| EX-EDP-13 | In both clauses, when a blocking task is `in_progress` (or `pending` with a dispatch already landed), wait for its completion notification and re-check next tick rather than dispatching. | precondition | L880 | E4-189 | - | TaskList status, dispatch state | TaskList, Agent | yes | procedure |
| EX-EDP-14 | When a blocking task is `pending` and no dispatch has landed for it, do not wait (it never notifies; no clock primitives): either dispatch that role now, or mark the stale task `completed` and clear it, then re-check. | recovery | L880 | E4-190, E4-191 | dispatch or `completed` flip | stale task | TaskList, Agent | yes | procedure |
| EX-EDP-15 | Post-compaction, whether a dispatch landed is unreadable (the `Agent(...)` call is gone; TaskList records nothing), so default to not landed. | recovery | L880 | E4-192 | - | conversation state | TaskList | unknown | procedure |
| EX-EDP-16 | Rationale: a duplicate dispatch costs one pass; a dispatch wrongly assumed landed deadlocks the run on a notification that never comes. | rationale-only | L880 | E4-193 | - | - | none | unknown | rationale |
| EX-EDP-17 | Do not narrow either clause to `in_progress` only; `pending` is in the test deliberately to close the race where the task exists but `Agent(...)` has not landed. | invariant | L880 | E4-194 | - | TaskList status | TaskList | yes | procedure |
| EX-EDP-18 | A writer that aborted on source movement does not block an Engineer round and needs no exemption: `aborted-` is a distinct name class no clause prefix matches, so the Engineer can be dispatched while the redelivery stays owed; the marker holds the Task's advance shut, not the Engineer round. | invariant | L882; L342; L477 | E4-195, E4-197, E2-104, E2-264 | - | `aborted-*` tasks | TaskList | no, unknown | procedure |
| EX-EDP-19 | Rationale: an exemption keyed on an abort annotation would make Engineer dispatch depend on `metadata.activity`, which is informational and never a routing input. | rationale-only | L882 | E4-198 | - | - | none | no | rationale |
| EX-EDP-20 | Scope limit: part (g) governs the review-finding re-dispatch path only, not the forward per-Subtask fan-out; an Engineer on one Subtask may run concurrently with a writer on a different Subtask of the same Task — only re-dispatch rounds are ordered. | invariant | L886 | E4-205, E4-206 | - | - | Agent | no | procedure |

---
## M27. Routing discipline — Severity bounds the loop; pick-then-route table; gates (c)/(d); shims (e)/(f); part (g) (`EX-ROUTE`)

- **Purpose:** Turn each reviewer finding's severity tag, depth-tagged fix paths and path count into exactly one routing decision — pick the highest-quality path by judgement, then route deterministically (ungated row 6, scope-bounding gate (c), or routing-decision gate (d)) — and order source-changing re-dispatches Engineer → code review → writer.
- **Failure it prevents:** Silent scope-narrowing inside a re-dispatch prompt the user never sees; accepting or unnarrowed-deferring a `blocker`; review loops that never terminate on `trivial-tweak` nits; handing a writer a diff a pending review will rewrite.
- **Env deps:** AskUserQuestion, TaskList, Agent, bees. TaskList-dependent: **yes** (gates (c)/(d) fire two-step; part (g) precondition is TaskList-derived).
- **Rows after dedupe:** 94 (procedure 83 · rationale 11 · example 0)
- **Literals:** `### Orchestrator discipline: routing review findings` · `blocker` · `suggestion` · `nit` · `trivial-tweak` · `refactor-locally` · `re-architect` · `[preferred]` · `[introduces-mechanism]` · `Severity bounds the loop.` · `(a) Pick the path, then route on it.` · `Step 1 — pick.` · `Step 2 — route on the path chosen in Step 1.` · `What "highest-quality" means.` · `What "introduces a mechanism" means.` · `(b) ANTI-PATTERN — do not write this:` · `"out of scope for this issue"` · `"out of scope for <id>"` · `"prefer option (a)"` · `"prefer (a)"` · `"Do NOT add X — out of scope"` · `(c) Scope-bounding gate.` · `(d) Routing-decision gate.` · `(e) Backwards-compatibility shim.` · `(f) Edge-case handling.` · `(g) Re-dispatch ordering when a fix path changes source.` · `Fix properly now` · `Defer to follow-up Issue` · `Accept the limitation` · `Cancel` · `(Recommended)` · `Recommended default on the mechanism row.` · `Re-dispatch the Analyst with this finding` · `N nits applied without re-review` · `count unavailable post-compaction` · `/quo-file-issue` · `Trigger A` · `Trigger B` · `Trigger C`
- **Cross-mechanism edges:** Produces for → TRK (Triggers A/B/C fire from here), ABORT (`Cancel`), EDP (part (g) precondition), DEFER (batched nits excluded), CLEAN/SUMM (`**Reviews**` nit count), MOV (ordering after movement). Consumes from → BEEREV/PMD (findings), `agents/analyst.md` (mechanism definition), `agents/pm.md` (report-note exemption), GATE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-ROUTE-1 | `### Orchestrator discipline: routing review findings` governs how the orchestrator routes depth-tagged findings from the in-flow review skills. | definition | L789-791 | E4-001 | - | reviewer findings | none | yes | procedure |
| EX-ROUTE-2 | Every reviewer finding carries a severity tag (exactly one of `blocker` / `suggestion` / `nit`), a depth tag per proposed fix path (exactly one of `trivial-tweak` / `refactor-locally` / `re-architect`), and the count of fix paths surfaced. | definition | L791 | E4-002, E4-003, E4-004 | - | reviewer finding | none | yes | procedure |
| EX-ROUTE-3 | Turn the enumerated fix paths and depth tags into exactly one routing decision per finding: whether a gate fires is deterministic (Step 2 table), never judgement; which path is picked when no gate fires is the orchestrator's judgement (Step 1). | invariant | L791 | E4-005, E4-006, E4-007 | routing decision | fix paths, depth tags | none | yes | procedure |
| EX-ROUTE-4 | Never re-classify the reviewer's depth tags; read a path's depth exactly as emitted. | invariant | L791 | E4-008 | - | depth tags | none | yes | procedure |
| EX-ROUTE-5 | A "review lane's loop" is the Engineer → code-review loop at any review site, and each writer → reviewer pair. | definition | L793 Severity bounds the loop | E4-009 | - | - | none | yes | procedure |
| EX-ROUTE-6 | A lane is held open by `blocker`- and `suggestion`-severity findings and by any `nit` whose chosen fix path is deeper than `trivial-tweak`; it closes when no lane-holding finding remains outstanding. | invariant | L793 | E4-010, E4-011 | lane closure | severity, chosen depth | none | yes | procedure |
| EX-ROUTE-7 | A lane-holding finding stays outstanding until a later cold pass no longer raises it or it reaches a no-fix-lands disposition: accepted into the compromise tracker, recorded as a `defer-*` task, or gate answer `Accept the limitation` / `Cancel` / `Defer to follow-up Issue` when nothing ships. | invariant | L793 | E4-012, E4-013 | - | cold-pass result; tracker; `defer-*`; gate answer | Agent, TaskList, AskUserQuestion | yes | procedure |
| EX-ROUTE-8 | A dispatch settles nothing — ungated at row 6, chosen at a gate, or a deferral's soft fix / narrowing — until a later cold pass reads its result. | invariant | L793 | E4-014 | - | dispatch, cold pass | Agent | yes | procedure |
| EX-ROUTE-9 | A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own; when a lane-holding finding already forces another implementer round, `trivial-tweak` nits ride along in it and the next cold pass reads them. | invariant | L793 | E4-015, E4-016 | implementer dispatch | severity + depth | Agent | yes | procedure |
| EX-ROUTE-10 | When only `trivial-tweak` nits remain, apply them in one final implementer pass for that lane and dispatch no further reviewer round for it — at a site where the review runs inside the PM's in-flight passes, that means do not re-dispatch the PM; a reviewer return whose findings are all `trivial-tweak` nits, shipped as such, closes that lane after one implementer pass. | ordering | L793; L917 §5 | E4-017, E4-018, E5-050 | final implementer dispatch; lane closure | remaining nits | Agent | yes, unknown | procedure |
| EX-ROUTE-11 | Record the batched-nit count on the `**Reviews**` line of the summary for the scope that dispatched the review, as `N nits applied without re-review`; when compaction removed the count render `count unavailable post-compaction` rather than guessing; nits applied that way are counted there, not listed as ignored feedback. | field-or-template | L793; L917 | E4-019, E4-020, E5-051 | `**Reviews**` line | nit count | none | yes, unknown | procedure |
| EX-ROUTE-12 | Batched `trivial-tweak` nits are finished work: never list them as ignored feedback and never turn them into `defer-*` tasks. | invariant | L793 | E4-021 | - | - | TaskList | yes | procedure |
| EX-ROUTE-13 | A `nit` whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding. | invariant | L793 | E4-022 | - | Step 2 table | none | yes | procedure |
| EX-ROUTE-14 | When a gate answer ships anything other than the enumerated `trivial-tweak` path (`Fix properly now` on rows 2/3/4, or a Defer's soft fix/narrowing), the finding is lane-holding again: a cold pass must read the fix, and part (g)'s elision does not apply. | invariant | L793 | E4-023, E4-024 | reviewer dispatch | gate answer | AskUserQuestion, Agent | yes | procedure |
| EX-ROUTE-15 | When the final pass ships only `trivial-tweak` paths and changes source, apply part (g)'s ordering with its code-review rung elided. | ordering | L793 | E4-025 | Engineer → writer dispatch | EX-ROUTE-10 | Agent | yes | procedure |
| EX-ROUTE-16 | The bound keys on the reviewer's own depth tag, not on a narrower reading of `nit`; severity stays orthogonal to depth. | invariant | L793 | E4-026 | - | depth tag | none | yes | procedure |
| EX-ROUTE-17 | Rationale: the coverage given up is exactly the `trivial-tweak`-nit class — the raising pass already read the text, and the post-completion review reads the whole diff. | rationale-only | L793 | E4-027 | - | - | none | yes | rationale |
| EX-ROUTE-18 | Routing is two-step: Step 1 is the orchestrator's judgement; Step 2 is deterministic given the path Step 1 chose. | ordering | L795 (a) | E4-028 | - | - | none | yes | procedure |
| EX-ROUTE-19 | Step 1: choose the highest-quality fix path among those the reviewer enumerated. | command | L797 Step 1 | E4-029 | path pick | enumerated paths | none | yes | procedure |
| EX-ROUTE-20 | Treat the reviewer's `[preferred]` token as an input, not a verdict; prefer it only when it is also the most complete — when `[preferred]` marks a narrowing and a fuller path is still the smallest internally-consistent complete change, take the fuller path. | invariant | L797 | E4-030, E4-031 | path pick | `[preferred]` | none | yes | procedure |
| EX-ROUTE-21 | The pick is always one of the paths the reviewer enumerated; when none is the smallest internally-consistent complete change, pick the most complete anyway. | invariant | L797 | E4-032, E4-033 | path pick | enumerated paths | none | yes | procedure |
| EX-ROUTE-22 | An under-enumerated pick routes via rows 2/3/4 to gate (c), where `Fix properly now` dispatches the complete fix; exception: an under-enumerated finding with absent/malformed depth tag goes via row 1 to gate (d), which has no `Fix properly now` — the user picks among paths as emitted. | ordering | L797 | E4-034, E4-035 | gate (c)/(d) | tags | AskUserQuestion | yes | procedure |
| EX-ROUTE-23 | Rationale: an incomplete menu becomes visible in session because a gate fires where it otherwise would not have. | rationale-only | L797 | E4-036 | - | - | none | yes | rationale |
| EX-ROUTE-24 | A durable record of an under-enumerated finding reaches the post-completion review only via Trigger A (`Defer to follow-up Issue`) or Trigger B (`Accept the limitation`); `Fix properly now` writes none. | invariant | L797 | E4-037 | tracker entry (conditional) | gate answer | none | yes | procedure |
| EX-ROUTE-25 | The orchestrator does not absorb an under-enumeration gap by writing a fix path of its own. | invariant | L797 | E4-038 | - | - | none | yes | procedure |
| EX-ROUTE-26 | Step 2: evaluate the table conditions in order, taking the first that matches, so each finding yields exactly one decision. | ordering | L799 Step 2 | E4-039 | routing decision | chosen path | none | yes | procedure |
| EX-ROUTE-27 | Row 1: no depth tag, or malformed severity/depth tag → treat as `re-architect` → gate (d). | ordering | L804 | E4-040 | gate (d) | tags | AskUserQuestion | yes | procedure |
| EX-ROUTE-28 | Row 2: the chosen path carries `[introduces-mechanism]`, or introduces a mechanism by the orchestrator's own reading → gate (c). | ordering | L805-806 | E4-041 | gate (c) | tag | AskUserQuestion | yes | procedure |
| EX-ROUTE-29 | Row 3: the chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers → gate (c). | ordering | L807-808 | E4-042 | gate (c) | unit's ticket | AskUserQuestion | yes | procedure |
| EX-ROUTE-30 | Row 4: the chosen path is narrower than the smallest internally-consistent complete fix (leaves the stated defect partly unfixed) → gate (c). | ordering | L809-810 | E4-043 | gate (c) | chosen path | AskUserQuestion | yes | procedure |
| EX-ROUTE-31 | Row 5: the chosen path's depth tag is `re-architect` → gate (d). | ordering | L811 | E4-044 | gate (d) | depth tag | AskUserQuestion | yes | procedure |
| EX-ROUTE-32 | Row 6: otherwise → dispatch a fresh ephemeral implementer (Engineer / Test Writer / Doc Writer per the finding's lane) per Section 3's dispatch shape with the chosen path, no user gate, and append a tracker entry per Section 6.5 Trigger C. | command | L812-815 | E4-045, E4-046, E4-047 | implementer dispatch; tracker entry | chosen path, lane | Agent, TaskList | yes (section refs differ) | procedure |
| EX-ROUTE-33 | Rationale: rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of depth; row 1 comes first so parts (e)/(f) stay reachable unchanged. | rationale-only | L815 | E4-048, E4-049 | - | - | none | yes | rationale |
| EX-ROUTE-34 | Whatever row fires, when the chosen path changes source the re-dispatch follows part (g): Engineer, then the code review for that site, then the affected writer. | ordering | L815 | E4-050 | ordered dispatches | chosen path | Agent | yes | procedure |
| EX-ROUTE-35 | "Highest-quality" = the smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names; total-system complexity counts against a path; effort is never the tiebreaker between equally complete paths; for a docs/prose-only change set the test degenerates to "every surface that states the invariant states it consistently". | definition | L817 | E4-051, E4-052, E4-053, E4-055 | - | unit's ticket | none | yes | procedure |
| EX-ROUTE-36 | "Adds a mechanism" is a reason to route to gate (c), not a reason to build. | invariant | L817 | E4-054 | - | - | none | yes | procedure |
| EX-ROUTE-37 | "Introduces a mechanism" = the path adds machinery per `agents/analyst.md`'s mechanism definition that the approved design for this unit did not enumerate; the approved design = the Subtask body, its parent Task body, plus the PRD/SDD the Plan Bee's `reference_materials` resolves to (or the Plan Bee body when null/empty). | definition | L819 | E4-056, E4-057 | - | bodies, `reference_materials` | bees | yes; diverges (fix-issue uses the `## Authoritative design directive` block) | procedure |
| EX-ROUTE-38 | The reviewer's `[introduces-mechanism]` tag is the primary signal for row 2 — a tagged path routes to gate (c) with no further judgement; orchestrator-side detection is the fallback used only when no tag is present, reading the path against the definition and routing the same way. | invariant | L819 | E4-058, E4-059 | gate (c) | tag / path description | AskUserQuestion | yes | procedure |
| EX-ROUTE-39 | (b) ANTI-PATTERN: the orchestrator MUST NOT inline scope-bounding directives into a re-dispatched implementer's prompt (R2/R3 rounds). Forbidden phrasings and close paraphrases: `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. | invariant | L821 | E4-060, E4-061 | - | dispatch prompt | Agent | yes | procedure |
| EX-ROUTE-40 | Rationale: inlining a scope-bound silently narrows the fix without the user ever seeing the decision. | rationale-only | L821 | E4-062 | - | - | none | yes | rationale |
| EX-ROUTE-41 | When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through gate (c) instead. | gate | L821 | E4-063 | gate (c) | scope-bound intent | AskUserQuestion | yes | procedure |
| EX-ROUTE-42 | The prohibition targets narrowing language, not path selection: a prompt naming the chosen path and carrying its fix in full is not a violation; instructing the implementer to do less than the chosen path is; a path itself narrower than the complete fix is never written into a prompt — it routes to gate (c) via row 4. | invariant | L823 | E4-064, E4-065, E4-066 | gate (c) | dispatch prompt | Agent, AskUserQuestion | yes | procedure |
| EX-ROUTE-43 | Gate (c) has four entry conditions: would-otherwise-scope-bound (part (b)) and rows 2, 3, 4; downstream the part-(b) condition is read as row 4, so every rule enumerating "row 2, 3, or 4" covers it. | gate | L825 (c) | E4-067, E4-068 | gate (c) fire | Step 2 result | AskUserQuestion | yes | procedure |
| EX-ROUTE-44 | The finding's severity determines which of gate (c)'s choices are available: a `blocker` can never be accepted, and can be deferred only with a narrowing. | choice-set | L825-827 | E4-070, E4-071 | choice set | severity | AskUserQuestion | yes | procedure |
| EX-ROUTE-45 | On a `blocker`, `Accept the limitation` is unreachable unconditionally: do not offer it, do not mark it Recommended, do not route to it by any other path. | choice-set | L829 | E4-072 | - | severity | AskUserQuestion | yes | procedure |
| EX-ROUTE-46 | Rationale: accepting a blocker ships the blocker. | rationale-only | L829 | E4-073 | - | - | none | yes | rationale |
| EX-ROUTE-47 | A `blocker` always gets the base pair `Fix properly now` and `Cancel` (its floor); when the two Defer conditions do not both hold, the base pair is the whole choice set. | choice-set | L830 | E4-074, E4-075 | choice set | Defer conditions | AskUserQuestion | diverges (fix-issue base pair = `Fix properly now` + `Re-dispatch the Analyst with this finding`) | procedure |
| EX-ROUTE-48 | Blocker `Fix properly now`: same behaviour as the `suggestion`/`nit` bullet (EX-ROUTE-58). | choice-set | L832 | E4-076 | implementer dispatch | - | Agent | yes | procedure |
| EX-ROUTE-49 | Blocker `Cancel`: ends work on the unit under review without the chosen fix landing and ends the run, exactly as part (d)'s `Cancel` does (close-out per EX-ABORT-7/14/17/19). | choice-set | L833 | E4-077 | run stop | - | none | diverges (fix-issue has no `Cancel` at (c)) | procedure |
| EX-ROUTE-50 | Rationale: `Cancel` is execute mode's analog of `/quo-fix-issue`'s `Re-dispatch the Analyst with this finding` — a stop-and-re-plan answer, not a narrowing; this skill has no Analyst, so `Cancel` carries that answer at both gates. | rationale-only | L833; L849 | E4-081, E4-129 | - | - | none | diverges (execute has no Analyst) | rationale |
| EX-ROUTE-51 | Add `Defer to follow-up Issue` as a third blocker choice only when both hold: (i) the fix path the finding needs introduces a mechanism; (ii) that mechanism serves a case outside this unit's stated defect — i.e. the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships. | choice-set | L835 | E4-084, E4-085 | choice set | tag / reading, stated defect | AskUserQuestion | yes | procedure |
| EX-ROUTE-52 | A narrowing may never reduce coverage of the stated defect; when the blocker cannot be made inapplicable without leaving the defect partly unfixed it is in scope and takes one of the base pair, never `Defer`; on a blocker the deferral is paired with the narrowing, never shipped alone. | invariant | L835 | E4-086, E4-087, E4-088 | choice set | condition (ii) | AskUserQuestion | yes | procedure |
| EX-ROUTE-53 | File the follow-up Issue first (carrying the reviewer's sketched design verbatim); dispatch the narrowing (remove or scope down the mechanism-needing part) only once `/quo-file-issue` has returned an Issue ID; part (f) forbids shipping the narrowing when filing failed, and Trigger A writes its entry in that same window. | ordering | L835 | E4-089, E4-090, E4-091 | follow-up Issue; narrowing dispatch; tracker entry | Issue ID | bees, Agent | yes | procedure |
| EX-ROUTE-54 | Dispatch the blocker's narrowing directly, not by re-entering Step 2 (which would match row 4 and route back to this gate). | invariant | L835 | E4-092 | narrowing dispatch | - | Agent | yes | procedure |
| EX-ROUTE-55 | Rationale: the blocker-narrowing terminality and the Defer bullet's soft-fix terminality are one rule applied to two cases. | rationale-only | L835 | E4-093 | - | - | none | yes | rationale |
| EX-ROUTE-56 | When Defer-with-narrowing is available on a blocker, mark that choice `(Recommended)` (per **Recommended default on the mechanism row.**); the blocker Defer branch applies whichever row fired gate (c) — 2, 3 or 4 — because condition (i) tests the path the finding needs, not the chosen path; a `suggestion`/`nit` keeps the narrower rule: its Defer default is row-2 only. | choice-set | L835 | E4-094, E4-095, E4-096 | `(Recommended)` marker | conditions (i)/(ii) | AskUserQuestion | yes | procedure |
| EX-ROUTE-57 | Gate (c) fires for a `blocker` like any other finding: the base pair is a real decision, three choices when Defer-with-narrowing is open. The Defer bullet's closing clauses do not apply to a blocker: its no-fix-this-round branch cannot arise (condition (ii) guarantees a narrowing exists and ships); its never-invent-a-narrowing prohibition concerns an empty soft-fix slot on a non-blocker; its soft-fix identification does not apply (what ships is the required narrowing). | gate | L837 | E4-097, E4-098, E4-099, E4-100 | gate (c) fire | severity | AskUserQuestion | yes | procedure |
| EX-ROUTE-58 | The three bulleted choices `Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation` are the choice set for `suggestion`- and `nit`-severity findings. | choice-set | L837 | E4-101 | choice set | severity | AskUserQuestion | yes | procedure |
| EX-ROUTE-59 | Section 6.5's Trigger B is unreachable for `blocker` findings — no tracker entry can record an accepted blocker; Trigger A is reachable for a blocker on gate (c)'s Defer-with-narrowing branch and part (d)'s Defer branch, and its entry must carry the narrowing record. | invariant | L837 | E4-102, E4-103 | tracker `Rationale` | Defer branch | none | yes (section refs differ) | procedure |
| EX-ROUTE-60 | `Fix properly now`: re-dispatch the appropriate implementer per Section 3's dispatch shape to address the finding fully, no scope-bound. | choice-set | L839 | E4-104 | implementer dispatch | finding | Agent, TaskList | yes (section refs differ) | procedure |
| EX-ROUTE-61 | `Defer to follow-up Issue`: file a follow-up Issue via `/quo-file-issue` inline via the Skill tool, carrying the finding's description, and proceed with the soft fix this round — the most complete of the enumerated paths that remain once the deferred one is set aside — dispatched directly, not by re-entering Step 2 (a remaining path is narrower by definition and would match row 4). | choice-set | L840 | E4-105, E4-106, E4-107 | follow-up Issue; soft-fix dispatch | finding description | bees, Agent | diverges (precedent cross-ref cites `/quo-fix-issue` Section 1) | procedure |
| EX-ROUTE-62 | When the deferred path was the only one enumerated, ship no fix for this finding this round (same end state as `Accept the limitation`, with the Issue filed); never invent a narrowing to fill the soft-fix slot — part (b) forbids it. | choice-set | L840 | E4-108, E4-109 | - | path count | none | yes | procedure |
| EX-ROUTE-63 | `Accept the limitation`: record the limitation as an accepted compromise via `#### Session-scoped compromise tracker` (Section 6.5) and proceed. | choice-set | L841 | E4-110 | tracker entry | finding | none | yes (section refs differ) | procedure |
| EX-ROUTE-64 | Gate (c)'s question text includes the finding verbatim plus a one-line context line stating which of the four entry conditions fired. | field-or-template | L843 | E4-111 | question text | finding, condition | AskUserQuestion | yes | procedure |
| EX-ROUTE-65 | There is no `Cancel` option on the `suggestion`/`nit` choice set at gate (c); `Cancel` appears only in the `blocker` set, where it means stop the run and re-plan, never "shelve this finding". | choice-set | L843 | E4-112, E4-114 | choice set | severity | AskUserQuestion | diverges (fix-issue: no `Cancel` at (c) at all) | procedure |
| EX-ROUTE-66 | Rationale: scope-bounding a `suggestion`/`nit` is per-finding and a `Cancel` there would be ambiguous; the user retains `Ctrl-C`. | rationale-only | L843 | E4-113 | - | - | none | yes | rationale |
| EX-ROUTE-67 | Recommended default on the mechanism row: when gate (c) fires on row 2, `Defer to follow-up Issue` is the recommended default — mark it `(Recommended)` — at every severity (on `suggestion`/`nit` the deferral ships the soft fix; on `blocker` the required narrowing); on a blocker only where Defer-with-narrowing is open — when the coverage guard withholds `Defer` there is no choice to mark. | choice-set | L845 | E4-115, E4-116, E4-117 | `(Recommended)` marker | row 2, severity | AskUserQuestion | yes | procedure |
| EX-ROUTE-68 | Rationale: a mechanism the ticket never asked for has its own lifecycle; building it inside this unit turns one finding into several rounds. | rationale-only | L845 | E4-118 | - | - | none | yes | rationale |
| EX-ROUTE-69 | The follow-up Issue MUST carry the reviewer's sketched design verbatim. | invariant | L845 | E4-119 | follow-up Issue body | sketched design | bees | yes | procedure |
| EX-ROUTE-70 | At gate (d), a `blocker`'s `Defer to follow-up Issue` is unreachable unless part (c)'s two conditions both hold; a narrowing may never reduce coverage; a blocker that cannot be made inapplicable is in scope and takes one of the listed choices rather than `Defer`. | choice-set | L849 (d) | E4-121, E4-122 | choice set | severity, conditions | AskUserQuestion | yes | procedure |
| EX-ROUTE-71 | When both conditions hold at gate (d), offer Defer on part (c)'s terms: paired with the narrowing dispatched in the same round (never shipped alone), `(Recommended)`, Issue carrying the sketched design verbatim; the Defer bullet's "rather than picking a path now" describes the non-blocker case where nothing ships this round. | choice-set | L849 | E4-123, E4-126, E4-127 | Defer choice; follow-up Issue; narrowing dispatch | conditions | AskUserQuestion, bees, Agent | yes | procedure |
| EX-ROUTE-72 | A blocker's Defer `(Recommended)` takes precedence over the per-path marker: withhold the marker from every other choice so exactly one carries it. | invariant | L849 | E4-124 | `(Recommended)` marker | - | AskUserQuestion | yes (fix-issue also withholds from the Analyst choice) | procedure |
| EX-ROUTE-73 | When the two conditions do not hold at gate (d): do not offer `Defer`, do not mark it Recommended, do not route to it by any other path. | choice-set | L849 | E4-125 | choice set | conditions | AskUserQuestion | yes | procedure |
| EX-ROUTE-74 | The choice set for a non-deferrable `blocker` at gate (d) is the one-choice-per-fix-path list plus `Cancel` (no Analyst counterpart in this skill). | choice-set | L849 | E4-128 | choice set | enumerated paths | AskUserQuestion | diverges (fix-issue adds `Re-dispatch the Analyst with this finding`) | procedure |
| EX-ROUTE-75 | A row-1 non-deferrable finding can arrive with no fix path enumerated; gate (d) still fires with an empty per-path list, so the listed choices are `Cancel` alone; a zero-path blocker whose two Defer conditions do hold still gets `Defer to follow-up Issue`, marked `(Recommended)` per the precedence rule. | choice-set | L849 | E4-130, E4-131 | choice set | fix-path count | AskUserQuestion | diverges (fix-issue marks the Analyst re-dispatch `(Recommended)` in the empty-list case); yes | procedure |
| EX-ROUTE-76 | On a zero-path fire the question text says the reviewer enumerated no fix path; the user directs the fix through the auto-appended free-text slot or cancels; a prose direction is dispatched per Section 3's shape carrying that direction as the fix; it is not an ungated route, so Trigger C writes nothing; when the user gives no direction (neither prose nor `Cancel`) do not invent a dispatch for a shapeless emission — re-fire the gate. | field-or-template | L849 | E4-132, E4-133, E4-134, E4-135 | question text; implementer dispatch; gate re-fire | user answer | AskUserQuestion, Agent, TaskList | no | procedure |
| EX-ROUTE-77 | No `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing. | invariant | L849 | E4-136 | - | - | none | yes | procedure |
| EX-ROUTE-78 | Gate (d) offers one choice per reviewer-surfaced fix path; each description includes that path's depth tag (e.g. `re-architect`, `refactor-locally`). | choice-set | L851 | E4-139 | choice set | paths, depth tags | AskUserQuestion | yes | procedure |
| EX-ROUTE-79 | The `(Recommended)` marker goes on the path chosen at Step 1 (the gate asks the user to ratify or override); when `[preferred]` marks a narrowing and a fuller path is the complete change, mark the fuller path Recommended and say in its description that the reviewer preferred the other; fallback: on a row-1 entry no Step-1 pick was possible, so no path is marked Recommended. | choice-set | L851 | E4-140, E4-141, E4-142 | `(Recommended)` marker; descriptions | Step 1 pick, `[preferred]` | AskUserQuestion | yes | procedure |
| EX-ROUTE-80 | Gate (d) `Defer to follow-up Issue`: file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now. | choice-set | L852 | E4-143 | follow-up Issue | finding description | bees | yes | procedure |
| EX-ROUTE-81 | Gate (d) `Cancel`: ends work on the unit under review without the chosen fix landing, and ends the run (close-out per EX-ABORT). | choice-set | L853 | E4-144 | run stop | - | none | diverges (fix-issue `Cancel` ends the current Issue; close-out mode branch decides the run) | procedure |
| EX-ROUTE-82 | Gate (d)'s question text includes the finding verbatim. | field-or-template | L855 | E4-148 | question text | finding | AskUserQuestion | yes | procedure |
| EX-ROUTE-83 | (e) Backwards-compatibility shim: a finding emitted without a depth tag (legacy or hand-authored) MUST be treated as `re-architect` depth and routed to gate (d); when the orchestrator cannot determine a finding's depth, surface the decision rather than dispatching its own pick ungated under row 6. | invariant | L857 (e) | E4-149, E4-150 | gate (d) | depth tag | AskUserQuestion | yes | procedure |
| EX-ROUTE-84 | A PM emission that `agents/pm.md`'s tracker-check bullet designates a report note (not a finding) is exempt from the shim and from part (f)'s malformed-tag bullet. | invariant | L857 | E4-151 | - | PM report note | none | yes | procedure |
| EX-ROUTE-85 | (f) Malformed tags: a severity not exactly `blocker`/`suggestion`/`nit`, or a depth not exactly `trivial-tweak`/`refactor-locally`/`re-architect`, is treated as `re-architect` per part (e); also surface the parse failure to the user so the reviewer emission can be corrected. | recovery | L861 (f) | E4-152, E4-153 | gate (d); user message | tags | AskUserQuestion | yes | procedure |
| EX-ROUTE-86 | (f) Routing ambiguity: if the table returns more than one decision (impossible by construction), default to gate (d) and surface the ambiguity. | recovery | L862 | E4-154 | gate (d) | Step 2 result | AskUserQuestion | yes | procedure |
| EX-ROUTE-87 | (f) `/quo-file-issue` failure at the Defer gate: when the user picks `Defer to follow-up Issue` at (c) or (d) but the inline filing fails or the user cancels inside it, MUST NOT silently ship the soft fix or no fix; surface the failure and re-prompt with the same gate's choices — re-attempt the defer, `Accept the limitation` where it exists (non-`blocker` only), a specific fix path, or Cancel; Cancel is available at either gate on a `blocker` (part (c)'s base pair) and at the routing gate only otherwise. | recovery | L863 | E4-155, E4-156, E4-157, E4-158 | gate re-fire; choice set | filing result, severity | bees, TaskList, AskUserQuestion | yes; diverges (fix-issue offers Cancel at the routing gate only) | procedure |
| EX-ROUTE-88 | A `blocker` can reach the filing-failure bullet via Defer-with-narrowing; do not ship the narrowing when the filing failed; re-prompt so the user re-attempts the filing or picks a non-deferring choice. | invariant | L863 | E4-159, E4-160 | gate re-fire | filing result | TaskList, AskUserQuestion | yes | procedure |
| EX-ROUTE-89 | Rationale: the narrowing is legitimate only paired with the follow-up Issue that carries the deferred design. | rationale-only | L863 | E4-161 | - | - | none | yes | rationale |
| EX-ROUTE-90 | (g) Once routing is settled (own pick per (a), or user pick at (c)/(d)), decide how many lanes to dispatch at once: when the chosen path requires a source change, the Engineer re-dispatch and the affected writer re-dispatch are ordered, not concurrent. | ordering | L865 (g); L912 §5 | E4-162, E4-163, E5-037 | - | routing decision | Agent, TaskList | yes, unknown | procedure |
| EX-ROUTE-91 | Dispatch the Engineer first, then the code review for that site against the resulting diff, and only once that review has closed dispatch the Test Writer and/or Doc Writer invalidated. "The code review for that site" = the Bee-level Code Reviewer at Section 5 (Clause 2) and the per-Task PM's in-flight `/quo-engineer-review` pass at the per-Task site (Clause 1) — the per-Task site's only code-review coverage; this skill dispatches no per-Task Code Reviewer. | ordering | L865 | E4-164, E4-165, E4-166 | Engineer, reviewer, writer dispatches | source change | Agent, TaskList | diverges (fix-issue names the Code Reviewer as the sole rung); no | procedure |
| EX-ROUTE-92 | Rationale: dispatching the Engineer and a writer in the same round hands the writer a diff the pending code review is about to rewrite, forcing redo. | rationale-only | L865 | E4-167 | - | - | none | yes | rationale |
| EX-ROUTE-93 | One elision: when the Engineer round is the final `trivial-tweak` nit pass, skip the code-review rung and dispatch the affected writer once that Engineer returns; every other source-changing round keeps the rung. | ordering | L865 | E4-168, E4-169 | writer / reviewer dispatch | EX-ROUTE-10 | Agent | yes | procedure |
| EX-ROUTE-94 | A finding whose chosen fix path changes no source file carries no ordering constraint: re-dispatch that single writer lane alone — no Engineer round, no code review. | ordering | L888 | E4-207 | writer dispatch | chosen path | Agent | yes | procedure |

---
## M28. Bee-level reviews (Section 5) & Bee-level close-out (`EX-BEEREV`)

- **Purpose:** Once every Epic is `done`, dispatch the three Bee-scoped reviewers concurrently (only for lanes actually used), follow each review skill's routing trailer literally, re-dispatch implementers under `<role>-<bee-id>` names, and close every Bee-scoped TaskList name exactly once after the loop closes.
- **Failure it prevents:** An unclosed Bee-scoped name that keeps matching part (g)'s Clause 2 and wedges every later Engineer dispatch; the orchestrator doing implementation work itself.
- **Env deps:** Agent, TaskList. TaskList-dependent: **yes**.
- **Rows after dedupe:** 15 (procedure 12 · rationale 3 · example 0)
- **Literals:** `### 5. Final Bee-level Code, Doc and Eng reviews` · `Agent(subagent_type="code-reviewer", run_in_background=true)` · `Agent(subagent_type="test-reviewer", run_in_background=true)` · `Agent(subagent_type="doc-reviewer", run_in_background=true)` · `code-reviewer-<bee-id>` · `test-reviewer-<bee-id>` · `doc-reviewer-<bee-id>` · `engineer-<bee-id>` · `test-writer-<bee-id>` · `doc-writer-<bee-id>` · `pm-<bee-id>` · `engineer-<bee-id>-r1` · `code-reviewer-<bee-id>-r1` · `aborted-test-writer-<bee-id>` · `aborted-doc-writer-<bee-id>` · `**Your next tool use MUST address these findings now.**` · `**Your next tool use MUST advance the workflow.**` · `Follow the trailer literally` · `Bee-level TaskList close-out (runs once, after the review loop above has closed).` · `IMPORTANT`
- **Cross-mechanism edges:** Produces for → ROUTE (findings; Clause 2), DEFER (ignore decisions), SOE (Bee-level narrative), POST (runs after loop closes), ABORT (Bee-scope sweep list), DPS (completeness relay). Consumes from → NEXT (branch 3 / Mode 1 decline), TL (names), MOV (`aborted-<role>-<bee-id>` guard), LOOP (dispatch shape).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-BEEREV-1 | Once all Epics are `done`, dispatch three concurrent ephemeral reviewer Agents per Section 3's dispatch shape, exactly `Agent(subagent_type="code-reviewer", run_in_background=true)`, `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`. | command | L896 | E5-001, E5-002 | 3 dispatches | Epic statuses | Agent, TaskList | no | procedure |
| EX-BEEREV-2 | Track each reviewer via a TaskList task in the Bee-scoped form `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`. | name-class | L896 | E5-003 | 3 tasks | naming convention | TaskList | no | procedure |
| EX-BEEREV-3 | Conditional spawn: dispatch a reviewer only when its implementer was used during the Epic loop — code-reviewer if Engineers were dispatched, test-reviewer if Test Writers, doc-reviewer if Doc Writers. | precondition | L900-903 | E5-020, E5-021, E5-022, E5-023 | reviewer dispatches | dispatch history | Agent | no | procedure |
| EX-BEEREV-4 | Get the reviewer feedback and make a judgement call about whether that work must be done. | gate | L911 | E5-028 | disposition | reviewer returns | none | unknown | procedure |
| EX-BEEREV-5 | Each of `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` emits a routing trailer — `**Your next tool use MUST address these findings now.**` or `**Your next tool use MUST advance the workflow.**` plus a counter-anchor clause; follow the trailer literally — it is the authoritative routing prescription for this step. | invariant | L911 | E5-029, E5-030 | routing | trailer | none | unknown | procedure |
| EX-BEEREV-6 | Rationale: the prose below the trailer rule is reference context, not a load-bearing rule to recall from memory. | rationale-only | L911 | E5-031 | - | - | none | unknown | rationale |
| EX-BEEREV-7 | If feedback requires action, dispatch fresh ephemeral implementers per Section 3's shape (Engineer / Test Writer / Doc Writer / PM as needed), tracked under `engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>`, appending `-r<n>` on every dispatch after the first (e.g. `engineer-<bee-id>-r1`, second code review `code-reviewer-<bee-id>-r1`); Bee-level findings span the whole diff and never borrow a Subtask- or Task-scoped name. | command | L912 | E5-032, E5-033, E5-034, E5-035 | dispatches; tasks | trailer; round count | Agent, TaskList | no | procedure |
| EX-BEEREV-8 | IMPORTANT: stay in delegate mode during Bee-level re-dispatch — do not do the work yourself. | invariant | L912, L914 | E5-036, E5-046 | - | - | Agent | unknown | procedure |
| EX-BEEREV-9 | If the feedback was minor enough, the orchestrator may choose NOT to spawn the PM on this iteration. | precondition | L915 | E5-047 | - | feedback severity | Agent | unknown | procedure |
| EX-BEEREV-10 | Run the Bee-level TaskList close-out once, after the review loop has closed. | ordering | L920 | E5-059 | status flips | loop state | TaskList | no | procedure |
| EX-BEEREV-11 | Rationale: Bee-scoped names have no per-Task close-out site; an unclosed one keeps matching Clause 2 and wedges every later Engineer dispatch. | rationale-only | L920 | E5-060 | - | - | none | no | rationale |
| EX-BEEREV-12 | Once the loop has closed and every Bee-level dispatch has returned, and before advancing to Section 6, mark the listed names `completed`, sweeping by prefix so `-r<n>` rounds go with their first round. | ordering | L920 | E5-063 | status flips | all Bee-level returns | TaskList | no | procedure |
| EX-BEEREV-13 | Sweep list: the three reviewers (`code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>` + `-r1`…), the four implementer/PM names (`engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>` + rounds), and any Bee-scoped markers `aborted-test-writer-<bee-id>` / `aborted-doc-writer-<bee-id>` the movement rung opened for a lane this section dispatched. | name-class | L922-924 | E5-064, E5-065, E5-066 | status flips | - | TaskList | no | procedure |
| EX-BEEREV-14 | Rationale: reaching close-out means the redelivery landed — the loop cannot close over a lane that never delivered. | rationale-only | L924 | E5-067 | - | - | none | no | rationale |
| EX-BEEREV-15 | The Bee-level close-out runs exactly once per Bee. | invariant | L928 | E5-071 | - | - | TaskList | no | procedure |

---

## M29. Post-completion review (`EX-POST`)

- **Purpose:** After Section 5, dispatch one fresh `general-purpose` reviewer with a self-contained six-PHASE prompt (challenge tracked compromises first, discrete-defect sweep last) over `git diff <pre-bee-sha>` plus untracked files; synthesize, gate disposition (Fix / File / Skip), fire per-finding recovery gates SR-6.7 / SR-4.6, then commit.
- **Failure it prevents:** The run-biased team-lead rubber-stamping its own work; lane-scoped review skills missing cross-lane defects; an accepted `blocker` or unnarrowed deferral going unchallenged.
- **Env deps:** Agent, git, Bash, bees, TaskList, AskUserQuestion, Read. TaskList-dependent: **yes**.
- **Rows after dedupe:** 75 (procedure 63 · rationale 10 · example 2)
- **Literals:** `### 6. Post-Completion Review` · `Anti-pattern callout — read before acting.` · `Anti-pattern callout, second.` · `subagent_type=general-purpose` · `HEAD~M` · `<pre-bee-sha>` · `<compromise-tracker-path>` · `You are an independent reviewer for a quorum Bee that was just shipped.` · `git diff <pre-bee-sha>` · `git ls-files --others --exclude-standard` · `bees show-ticket --ids <bee-id>` · `bees show-ticket --ids <epic-id-1> <task-id-1> ...` · `PHASE 1` · `PHASE 2` · `PHASE 3` · `PHASE 4` · `PHASE 5` · `PHASE 6` · `[compromise-challenge]` · `[design]` · `[defect]` · `file:line` · `no issues found` · `Post-completion review: no issues found` · `Post-completion review found [N] issues. How would you like to handle them?` · `Fix in this session` · `File as issue tickets` · `Skip` · `Compromise-challenge preamble (rendered before presenting the findings).` · `⚠️` · `Orchestrator self-tracking close-out (mandatory before yielding).` · `<role>-postcomp-<n>` · `engineer-postcomp-<n>` · `test-writer-postcomp-<n>` · `doc-writer-postcomp-<n>` · `aborted-<role>-postcomp-<n>` · `<role>-postcomp-<n>-r<k>` · `SR-6.7 ungated-route recovery gate.` · `SR-4.6 under-enumeration recovery gate.` · `File follow-up Issue to revisit the depth decision` · `Accept the misjudgment and proceed` · `Pause to discuss` · `File follow-up Issue to surface the missing path` · `Accept the under-enumeration and proceed` · `Orchestrator picked path (<letter>) — highest-quality` · `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` · `Decision: User accepted under-enumeration after post-completion challenge`
- **Cross-mechanism edges:** Produces for → TRK (Trigger D writes; `Follow-up Issue` in-place updates), DHG (continues to 6.5), FINAL. Consumes from → MAN (Pre-Bee SHA), TRK (tracker path/contents), BEEREV (loop closed), MOV/UMG/EDP (carried over onto postcomp names), TL (postcomp name class), GATE, EFF (inherits session effort).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-POST-1 | After step 5's review loop is done and all fixable issues addressed, run one final fresh-context generalist sweep across all changes made by this Bee — an independent quality gate separate from the per-Task and per-Epic cycles. | ordering | L933 | E5-073, E5-074 | reviewer dispatch | step 5 completion | Agent | yes | procedure |
| EX-POST-2 | Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at the post-completion stage (orchestrator and reviewer alike); spawn a fresh general-purpose agent with a self-contained prompt instead. | invariant | L935; L1050-1053 skeleton | E5-075, E5-077, E5-126 | Agent dispatch | - | Agent | yes | procedure |
| EX-POST-3 | Rationale: those three skills are lane-scoped (source / user-facing docs / tests) and none runs the cross-lane sweep this step needs. | rationale-only | L935 | E5-076 | - | - | none | yes | rationale |
| EX-POST-4 | The team-lead must NOT do the post-completion review directly; the fresh agent gets the diff and the Bee body and nothing else. | invariant | L937 | E5-078, E5-080 | - | - | Agent | yes | procedure |
| EX-POST-5 | Rationale: the team-lead's accumulated run context biases it toward "did the phases get done correctly?" rather than "is this good?". | rationale-only | L937 | E5-079 | - | - | none | yes | rationale |
| EX-POST-6 | Step 1: compute the pre-Bee diff scope — `Read` the manifest at `<tempdir>/.quorum/run-state-quo-execute-<bee-id>.md` and take its **Pre-Bee SHA** as `<pre-bee-sha>`. | command | L939 | E5-081 | `<pre-bee-sha>` | manifest | none | no | procedure |
| EX-POST-7 | If the manifest is missing, fall back to `HEAD~M` (M = Tasks committed in Step 4, one commit each); if the Task count is lost, walk `git log` back to the commit before the first Task commit. | recovery | L939 | E5-082, E5-083 | `<pre-bee-sha>` | commit count; `git log` | git, Bash | no | procedure |
| EX-POST-8 | Collect `<bee-id>` and, secondarily, the Epic/Task IDs under it as `<epic-id-1> <task-id-1> ...`; the Bee body is the primary spec, Epic/Task bodies secondary context consulted only when the diff is ambiguous. | command | L939 | E5-084, E5-085 | IDs | Bee tree | bees | no | procedure |
| EX-POST-9 | Step 2: spawn the reviewer with the Agent tool, `subagent_type=general-purpose`, `run_in_background=true`; the prompt must be self-contained because the agent sees nothing else. | command | L941 | E5-086, E5-087 | Agent dispatch | - | Agent | yes | procedure |
| EX-POST-10 | Pass the compromise-tracker path (Section 6.5's `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`) as `<compromise-tracker-path>` — the path, NOT the inlined contents. | invariant | L941 | E5-088 | prompt value | tracker file | Agent | yes | procedure |
| EX-POST-11 | Substitute `<pre-bee-sha>`, `<compromise-tracker-path>`, `<bee-id>` and the Epic/Task IDs into the skeleton before sending. | command | L941 | E5-089 | prompt | step 1 outputs | Agent | yes | procedure |
| EX-POST-12 | Skeleton opens with `You are an independent reviewer for a quorum Bee that was just shipped.` | field-or-template | L944 | E5-090 | prompt text | - | none | yes | procedure |
| EX-POST-13 | Reviewer scope is `git diff <pre-bee-sha>` (no `..HEAD` — working tree against the pre-Bee commit) plus every untracked file `git ls-files --others --exclude-standard` lists, read from disk. | command | L946-950 | E5-091, E5-092 | reviewer scope | `<pre-bee-sha>` | git, Bash | yes | procedure |
| EX-POST-14 | Rationale: Bee-level review-round edits sit uncommitted at this point, so a commit-to-commit range alone misses them. | rationale-only | L949-950 | E5-093 | - | - | none | yes | rationale |
| EX-POST-15 | When a finding concerns a change no Bee/Epic/Task body asks for, the reviewer says it is likely pre-existing or an unticketed in-run edit, as an inference, naming that basis. | relay | L951-956 | E5-094 | finding text | ticket bodies | none | yes | procedure |
| EX-POST-16 | Review the scope against the Bee body via `bees show-ticket --ids <bee-id>`; consult Epic/Task bodies via `bees show-ticket --ids <epic-id-1> <task-id-1> ...` only when the diff vs. the Bee body is ambiguous. | command | L956-959 | E5-095, E5-096 | - | ticket bodies | bees, Bash | yes | procedure |
| EX-POST-17 | Rationale: the reviewer's job is a fresh-eyes review with no context of how the work was done. | rationale-only | L959-961 | E5-097 | - | - | none | yes | rationale |
| EX-POST-18 | Perform the phases IN ORDER; PHASES 1–5 lead with challenging accepted compromises; the discrete-defect sweep is the FINAL phase. | ordering | L963-965 | E5-098 | - | - | none | yes | procedure |
| EX-POST-19 | PHASE 1: consume the tracker passed as a FILE PATH at `<compromise-tracker-path>` via the Read tool; it records every compromise the run accepted (deferred-to-Issue findings, accepted limitations, ungated path picks, post-completion overrides); each `## Compromise <n>` entry carries Finding (verbatim), Fix paths surfaced by reviewer (each `[depth:<...>]`-tagged), Decision, Rationale, Follow-up Issue. | command | L967-975 | E5-099, E5-100, E5-101 | - | tracker file | none | yes | procedure |
| EX-POST-20 | If the tracker is MISSING or unreadable, do NOT abort — PROCEED with the remaining phases and flag the missing tracker explicitly in the output. | recovery | L975-978 | E5-102 | missing-tracker flag | tracker presence | none | yes | procedure |
| EX-POST-21 | PHASE 2: challenge each tracked compromise on its merits — push back when the chosen path is not defensible, do not rubber-stamp — including the deep-asked-but-cheap-shipped check: flag any mismatch between what the tracker records as chosen and what the diff shipped. | command | L980-986 | E5-103, E5-104 | findings | tracker vs diff | none | yes | procedure |
| EX-POST-22 | PHASE 2 contract violations: an entry whose `Finding (verbatim)` carries `blocker` and whose `Decision` is `User picked Accept the limitation` (a blocker can never be accepted); an entry whose `Decision` is `User picked Defer to follow-up Issue` and whose `Rationale` carries no narrowing record (a narrowing record states what was narrowed out and why the blocker no longer describes anything that ships); an entry whose narrowing record shows the narrowing left the unit's stated defect partly unfixed. | invariant | L986-997 | E5-105, E5-106, E5-107, E5-108 | findings | tracker fields | none | yes | procedure |
| EX-POST-23 | Emit every PHASE 2 contract violation as a `[compromise-challenge]` finding at `blocker` severity, never lower. | command | L997-998 | E5-109 | `[compromise-challenge]` `blocker` | - | none | yes | procedure |
| EX-POST-24 | PHASE 3 applies to every entry whose Decision is `Orchestrator picked path (<letter>) — highest-quality` (match on surrounding wording, not a literal letter); evaluate (i) whether the depth judgement was plausible or the true depth is `re-architect`, and (ii) whether the chosen path introduced a mechanism the approved design did not enumerate and should have been deferred or put to the user; emit a `[compromise-challenge]` on either axis; axis (ii) is required, not optional. | command | L1000-1015 | E5-110, E5-111, E5-112, E5-114, E5-115 | `[compromise-challenge]` | tracker Decision, diff | none | yes | procedure |
| EX-POST-25 | "Mechanism" = a new state, configuration surface (flag, env var, setting), persisted or wire field, background task, exception/error type, metric/log/trace attribute, name or identifier class, gate, or retry/fallback path. | definition | L1006-1010 | E5-113 | - | - | none | yes | procedure |
| EX-POST-26 | Rationale: an ungated pick is an orchestrator judgement no gate reviewed, and PHASE 3 is the only place it gets challenged. | rationale-only | L1014-1015 | E5-116 | - | - | none | yes | rationale |
| EX-POST-27 | PHASE 4: for EVERY finding the in-flow reviewer surfaced, regardless of severity/depth/path-count, evaluate whether an additional plausible fix path should have been enumerated; when under-enumeration is judged, emit a `[compromise-challenge]` naming it. | command | L1017-1023 | E5-117, E5-118 | `[compromise-challenge]` | in-flow findings | none | yes | procedure |
| EX-POST-28 | Rationale: PHASE 3 catches misjudged depth or an unnoticed mechanism on a surfaced path; PHASE 4 catches a plausible path not surfaced at all. | rationale-only | L1023-1026 | E5-119 | - | - | none | yes | rationale |
| EX-POST-29 | PHASE 5: judge holistic solution quality beyond the logged compromises — is the shipped solution actually good independent of any single tracked decision? | command | L1028-1030 | E5-120 | `[design]` findings | diff, Bee body | none | yes | procedure |
| EX-POST-30 | PHASE 6 (final): flag code defects, prose problems, spec drift vs the Bee, contract-key violations, cross-file inconsistencies, and missing edits the Bee called for; one generalist pass covers code AND docs AND tests — do not lane-scope. | command | L1032-1037 | E5-121, E5-123 | `[defect]` findings | diff, Bee body | none | yes | procedure |
| EX-POST-31 | Do NOT allow renames of keys in CLAUDE.md `## Documentation Locations` or `## Build Commands`. | invariant | L1034-1035 | E5-122 | finding | contract keys | none | yes | procedure |
| EX-POST-32 | In skill repos, `skills/<name>/SKILL.md` and `agents/<name>.md` files in the diff are program source; review them with source-level rigor for broken cross-references, drifted contracts, ambiguous prose, and CLAUDE.md design-rule violations. | invariant | L1039-1044 | E5-124 | - | diff contents | none | yes | procedure |
| EX-POST-33 | Do NOT do a general repo audit; stay focused on the diff against the pre-Bee commit and the untracked files. | invariant | L1046-1048 | E5-125 | - | - | none | yes | procedure |
| EX-POST-34 | Return findings as a numbered list; tag EVERY finding with exactly one of `[compromise-challenge]` (PHASE 2/3/4), `[design]`, `[defect]`; a severity tag `blocker`/`suggestion`/`nit`; and the per-fix-path depth tag plus enumerated fix paths from the in-flight emission contract. | field-or-template | L1055-1060 | E5-127, E5-128, E5-129, E5-130 | findings list | - | none | yes | procedure |
| EX-POST-35 | The depth tag is informative here — the sweep is the final pre-merge gate, so any finding is a gate candidate regardless of depth; preserve the `file:line` + severity shape; the new tags are additive. | invariant | L1060-1063 | E5-131, E5-132 | - | - | none | yes | procedure |
| EX-POST-36 | If clean, the reviewer returns exactly `no issues found`. | field-or-template | L1063-1064 | E5-133 | return | - | none | yes | procedure |
| EX-POST-37 | Wait for the agent's report before proceeding. | ordering | L1067 | E5-134 | - | Agent return | Agent | yes | procedure |
| EX-POST-38 | Step 3: synthesize before presenting — compare the fresh reviewer's findings against the in-flight PM and per-Task reviewer verdicts, flag disagreements explicitly (e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean"), and present the list plus synthesis notes to the user. | command | L1069 | E5-135, E5-136, E5-137 | synthesis; user-facing findings | reviewer return; verdicts | none | yes | procedure |
| EX-POST-39 | When one or more `[compromise-challenge]` findings return, render a one-or-two-sentence prose preamble BEFORE the list naming this explicitly, mirroring the verdict-keyed preamble of `/quo-plan` Step 5e and `/quo-fix-issue` Section 3 with the `⚠️`-led divergent-framing convention; when there are none, render no preamble. | relay | L1071 | E5-138, E5-139, E5-141 | preamble | `[compromise-challenge]` findings | none | yes | procedure |
| EX-POST-40 | Example preamble: `⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below.` | example | L1071 | E5-140 | - | - | none | yes | example |
| EX-POST-41 | Orchestrator self-tracking close-out: before yielding at step 4/5, mark every self-tracking TaskList task created during Section 6 `completed` and clear it; the yield is the trigger — when the orchestrator stops responding the TaskList must show no `in_progress` synthesis leftovers. | ordering | L1073 | E5-142, E5-144 | status flips | ad-hoc tasks | TaskList | yes | procedure |
| EX-POST-42 | Example self-tracking tasks: "Get diff scope", per-ticket "Verify <id>", "Synthesize findings". | example | L1073 | E5-143 | - | - | TaskList | yes | example |
| EX-POST-43 | Section 5's Bee-level close-out is authoritative for every `*-<bee-id>` task Section 5 dispatched (the self-tracking close-out adds nothing to it); neither covers the `<role>-postcomp-<n>` names step 6's `Fix in this session` branch dispatches — that branch closes them itself; the self-tracking close-out and step 6's per-finding close-out (`<role>-postcomp-<n>`, `-r<k>` re-dispatches, `aborted-<role>-postcomp-<n>`) are complementary, not overlapping. | definition | L1073 | E5-145, E5-146, E5-147 | - | - | TaskList | no, yes | procedure |
| EX-POST-44 | Step 4: if the agent returned `no issues found`, report `Post-completion review: no issues found` and continue to Final Output. | relay | L1075 | E5-148 | user line | reviewer return | none | yes | procedure |
| EX-POST-45 | Step 5: if issues were flagged, fire the post-completion findings gate (two-step per EX-GATE) with question `Post-completion review found [N] issues. How would you like to handle them?` and options exactly `Fix in this session` (address now before closing the Bee), `File as issue tickets` (create tickets via `/quo-file-issue` for each), `Skip` (acknowledge and move on). | gate | L1077-1082 | E5-152, E5-153 | question text; choices | finding count | AskUserQuestion, TaskList | yes | procedure |
| EX-POST-46 | When the reviewer returned a PHASE 2 contract-violation `[compromise-challenge]` (a `blocker`), the step-5 question text recommends `Fix in this session`; the step-5 gate is aggregate — one answer covers every finding — so the recommendation is stated once for the whole set. | gate | L1084; L1103 | E5-154, E5-188, E5-189 | recommendation | PHASE 2 finding | AskUserQuestion | yes | procedure |
| EX-POST-47 | Step 6 `Fix in this session`: dispatch fresh ephemeral Agents per Section 3's shape (Engineer / Test Writer / Doc Writer as needed); stay in delegate mode — do not do the work yourself. | command | L1087 | E5-155, E5-156 | dispatches | user choice | Agent | yes | procedure |
| EX-POST-48 | Rationale: Section 3's Subtask-, Task-, and Bee-scoped names do not fit a follow-up answering one finding of a whole-Bee sweep, hence the post-completion scope. | rationale-only | L1089 | E5-160 | - | - | none | yes | rationale |
| EX-POST-49 | Close-out: when each follow-up Agent returns, persist as Section 3's reconcile-on-completion does (confirm any bees transitions the worker committed to), then mark its `<role>-postcomp-<n>` task `completed` and clear it; sweep post-completion names by prefix before the branch exits so none is left active. | ordering | L1091 | E5-161, E5-162, E5-164 | ticket confirmations; status flips | Agent return | bees, TaskList | yes | procedure |
| EX-POST-50 | Section 3's movement rung carries over onto post-completion names: a `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` return that stopped on movement is NOT a completion — mark its task `completed`, open `aborted-<role>-postcomp-<n>` `pending` (same `<n>`) with the "how far I got" report as `metadata.activity`. | command | L1093 | E5-165, E5-166, E5-167 | `aborted-<role>-postcomp-<n>` | writer return | TaskList | yes | procedure |
| EX-POST-51 | Re-dispatch the aborted lane once source has settled, per the rung's three mover branches, under `<role>-postcomp-<n>-r<k>`; mark the `aborted-*` task `completed` when the re-dispatch delivers. | ordering | L1093 | E5-169 | status flip | re-dispatch return | TaskList | yes | procedure |
| EX-POST-52 | While an `aborted-<role>-postcomp-<n>` task is `pending`, do not treat this Section 6 pass as finished and do not commit. | precondition | L1093 | E5-170 | - | `aborted-*` status | TaskList, git | yes | procedure |
| EX-POST-53 | The unexplained-movement gate applies unchanged, its third option read as *abort this follow-up lane* rather than *abort this unit*; its close-out here is this branch's own prefix sweep, not Section 4.2's `##### Aborted-run close-out`. | gate | L1093 | E5-171, E5-172 | AskUserQuestion | movement report | AskUserQuestion, TaskList | yes | procedure |
| EX-POST-54 | Rationale: the aborted-run close-out is scoped to a run that stops without its unit advancing, which no post-completion lane does — every Epic is `done` and every per-Task commit landed. | rationale-only | L1093 | E5-173 | - | - | none | yes | rationale |
| EX-POST-55 | After the sweep closes out an aborted lane's names, continue Section 6's own flow — remaining dispositions, step 7's recovery gates, then Section 6.5 — rather than exiting the run. | ordering | L1093 | E5-174 | - | - | none | yes | procedure |
| EX-POST-56 | The Engineer-dispatch freeze applies on post-completion names: MUST NOT dispatch `engineer-postcomp-<n>` while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` task is `pending`/`in_progress`, matching prefix plus status at every index and every `-r<k>`. | precondition | L1095 | E5-175 | - | active TaskList | TaskList, Agent | yes | procedure |
| EX-POST-57 | Rationale: part (g)'s clauses key on Subtask-, Task-, Bee-scoped names, none matching postcomp names, so the freeze is restated; a writer handed a diff an Engineer is about to rewrite has to redo its work. | rationale-only | L1095 | E5-176, E5-177 | - | - | none | yes | rationale |
| EX-POST-58 | Part (g)'s `pending`-with-no-Agent clause carries over: dispatch the stalled role, or mark the stale task `completed` and clear it, rather than waiting on a notification that never arrives. | recovery | L1095 | E5-178 | dispatch or flip | stale task | TaskList, Agent | yes | procedure |
| EX-POST-59 | When one finding needs both a source change and a test/doc change, dispatch `engineer-postcomp-<n>` first and let it return; only then dispatch `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>`; independent findings may be worked concurrently — the within-finding ordering and cross-finding freeze are the only constraints. | ordering | L1097 | E5-179, E5-180 | dispatch sequence | finding shape | Agent, TaskList | yes | procedure |
| EX-POST-60 | After every follow-up lane has delivered, commit and continue to Section 6.5. | ordering | L1099 | E5-181 | git commit | returns | git | yes | procedure |
| EX-POST-61 | `File as issue tickets`: invoke `/quo-file-issue` with each issue's description, report the created ticket IDs, continue to 6.5. `Skip`: continue to 6.5. | command | L1100-1101 | E5-182, E5-183 | Issue tickets; report | findings | bees | yes | procedure |
| EX-POST-62 | Step 7: a `[compromise-challenge]` from PHASE 3 or PHASE 4 triggers its own recovery gate, fired before or alongside the step-6 disposition for that finding. | gate | L1103 | E5-184 | AskUserQuestion | PHASE 3/4 findings | AskUserQuestion, TaskList | yes | procedure |
| EX-POST-63 | One challenge class has no recovery gate by design — PHASE 2's accepted-`blocker`-or-unnarrowed-deferral contract violation: it is dispositioned by step 5's Fix / File / Skip gate alone (step 6 executes what it returns); a `Skip` leaves it recorded only in the reviewer's output and the tracker; do not invent a fourth gate for it. | invariant | L1103 | E5-185, E5-187, E5-190, E5-191 | - | PHASE 2 finding | AskUserQuestion | yes | procedure |
| EX-POST-64 | Rationale: there is nothing to recover from a PHASE 2 violation — it records an acceptance the gates should never have offered, an unnarrowed deferral, or a narrowing that left the defect partly unfixed. | rationale-only | L1103 | E5-186 | - | - | none | yes | rationale |
| EX-POST-65 | Both recovery gates fire per challenged finding (three findings ⇒ three firings), NOT aggregated, in the reviewer's emission order. | invariant | L1103; L1114 | E5-196, E5-197, E5-216 | one gate per finding | numbered list | AskUserQuestion | yes | procedure |
| EX-POST-66 | After the recovery gates resolve for every challenged finding, continue to Section 6.5. | ordering | L1103 | E5-199 | - | - | none | yes | procedure |
| EX-POST-67 | SR-6.7 ungated-route recovery gate: a three-choice `AskUserQuestion` fired when a `[compromise-challenge]` flags an ungated pick (Decision `Orchestrator picked path (x) — highest-quality`) on either PHASE 3 axis; choice labels are byte-matched against Trigger D — do not reword. | gate | L1105 | E5-200, E5-201 | AskUserQuestion | PHASE 3 finding | AskUserQuestion, TaskList | yes | procedure |
| EX-POST-68 | The pinned strings `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` name the routing misjudgment on either axis, mechanism axis included; read "depth decision"/"misjudgment" generically rather than concluding the mechanism axis has no gate. | definition | L1105 | E5-202, E5-203 | - | - | none | yes | procedure |
| EX-POST-69 | SR-6.7 `File follow-up Issue to revisit the depth decision`: dispatch `/quo-file-issue` via the Skill tool capturing the depth-mismatch finding plus the original tracker entry as context; update the original Trigger C entry's `Follow-up Issue` field in place with the new Issue ID — NO new tracker entry. | choice-set | L1106 | E5-204, E5-205 | Issue; tracker field update | finding, entry | AskUserQuestion, bees | yes | procedure |
| EX-POST-70 | SR-6.7 `Accept the misjudgment and proceed`: fire Trigger D's append — a NEW entry with `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` and the reviewer's challenge text as Rationale; the branch FIRES the write, it does not author it (Trigger D owns the mechanism). | choice-set | L1107 | E5-206, E5-207 | tracker entry | challenge text | AskUserQuestion | yes | procedure |
| EX-POST-71 | SR-6.7 `Pause to discuss`: stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward; no tracker write fires until a subsequent `Accept` / `File` pick. | choice-set | L1108, L1112 | E5-208, E5-209 | prose discussion | - | AskUserQuestion | yes | procedure |
| EX-POST-72 | SR-4.6 under-enumeration recovery gate: the same three-choice shape with relabeled choices, fired when a `[compromise-challenge]` flags under-enumeration; per-branch behaviour mirrors SR-6.7 exactly (file / append explicit-override entry via Trigger D / pause-and-resume). | gate | L1109; L1114 | E5-210, E5-215 | AskUserQuestion | PHASE 4 finding | AskUserQuestion, TaskList | yes | procedure |
| EX-POST-73 | SR-4.6 `File follow-up Issue to surface the missing path`: dispatch `/quo-file-issue` via the Skill tool capturing the under-enumeration finding; the tracker write follows Trigger D's `File`-branch under-enumeration note — append a new entry, or update an existing originating Trigger C entry's `Follow-up Issue` in place when one exists. | choice-set | L1110 | E5-211, E5-212 | Issue; tracker entry/update | finding | AskUserQuestion, bees | yes | procedure |
| EX-POST-74 | SR-4.6 `Accept the under-enumeration and proceed`: fire Trigger D's append — a NEW entry with `Decision: User accepted under-enumeration after post-completion challenge` and the challenge text as Rationale (fires, not authors). | choice-set | L1111 | E5-213 | tracker entry | challenge text | AskUserQuestion | yes | procedure |
| EX-POST-75 | SR-4.6 `Pause to discuss`: stop the flow, surface a prose discussion; the user can re-issue any of the three choices afterward. | choice-set | L1112 | E5-214 | prose discussion | - | AskUserQuestion | yes | procedure |

---
## M30. Deferral-hygiene gate (Step 0–3, Fix / File / Encode, `hive_commit.py`) (`EX-DHG`)

- **Purpose:** Before handoff, reconcile every ignored/deferred item into the `defer-*` ledger (Step 0), enumerate it (Step 1), route each item to Fix / File / Encode (Step 2, with a follow-up commit via `hive_commit.py`), and hard-stop until the active set is empty (Step 3).
- **Failure it prevents:** An inter-session deferral leaving the run only in conversation; a dirty tree at yield from Encode writes made after the per-Task commits.
- **Env deps:** TaskList, AskUserQuestion, bees, Bash, git, Agent. TaskList-dependent: **yes**.
- **Rows after dedupe:** 37 (procedure 31 · rationale 6 · example 0)
- **Literals:** `### 6.5 Before handoff — deferral hygiene` · `Step 0 — Retroactive ledger reconciliation (safety net).` · `Step 1 — Enumerate the active deferral ledger.` · `Step 2 — Surface the active set and gate the user choice.` · `Step 3 — Hard-stop on a non-empty active set.` · `Deferral hygiene: no deferred items.` · `Fix in this session` · `File as issue tickets` · `Encode in an existing ticket body` · `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` · `## Deferred from /quo-execute run` · `bees update-ticket --ids <ticket-id> --body-file <path>` · `bees-body-<defer-N>.md` · `bees-body-defer-3.md` · `Encode deferral: /quo-execute — <N> deferral(s) encoded` · `hive_commit.py` · `--skill quo-execute` · `--count <N>` · `--doc-path <abs-path>` · `skipped: nothing staged` · `python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]` · `python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]` · `<this skill's base directory>/scripts/hive_commit.py` · `git diff --cached` · `bees list-hives`
- **Cross-mechanism edges:** Produces for → FINAL (Section 7 only after the set is empty), git (follow-up commit). Consumes from → DEFER (ledger), PMD/CLEAN (PM Final reports, per-Task summaries), GATE, SHELL (scratch file), CLAUDE.md `## Documentation Locations` (PRD/SDD paths), `/quo-file-issue`.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-DHG-1 | The gate's `AskUserQuestion` firings are Step 2's initial Fix / File / Encode choice plus any Step 3 re-fires when a branch failed to close out a subset of the active set (all two-step per EX-GATE-2/3/4). | definition | L1118 | E6-002 | - | active `defer-*` set | none | unknown | procedure |
| EX-DHG-2 | Section 6's Fix / File / Skip gate handles only the fresh-eyes sweep's findings; every inter-session deferral ("address later", "defer to next phase", "pick up during a follow-up Issue", or similar) not addressed inline MUST have been recorded as a `defer-<short-suffix>` task. | invariant | L1180 | E6-087, E6-088 | - | `defer-*` tasks | TaskList | unknown | procedure |
| EX-DHG-3 | This gate is the pre-handoff reconciliation step that closes `defer-*` items out into durable inter-session carriers; Section 7's "show ignored feedback" prose stays the display layer — this gate ensures the active set is empty before that display fires. | definition | L1180-1182 | E6-089, E6-090 | - | active set | none | unknown | procedure |
| EX-DHG-4 | Section 4.1's `**Ignored Review Feedback**` field and Section 5's may-ignore site each instruct creating a `defer-<short-suffix>` task at the moment an item is ignored (upstream sources). | definition | L1184 | E6-091 | - | - | TaskList | unknown | procedure |
| EX-DHG-5 | Step 0 (before Step 1): walk every per-Task summary produced this run, every PM Final report's deferred items (per `agents/pm.md`), and any orchestrator-side ignored item that did not flow through those two surfaces. | command | L1184 | E6-092, E6-093, E6-096 | - | summaries; PM reports | none | unknown | procedure |
| EX-DHG-6 | Every item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task; skip items annotated `addressed-now-in-this-Task`. | definition | L1184 | E6-094, E6-095 | `defer-*` task | annotations | TaskList | unknown | procedure |
| EX-DHG-7 | Create a corresponding `defer-*` task for any item that does not already have one. | command | L1184 | E6-097 | `defer-*` task | walk results | TaskList | unknown | procedure |
| EX-DHG-8 | Rationale: the Section 4.1 / Section 5 record-creating instructions are the load-bearing source; Step 0 is the defense-in-depth net for missed instructions or off-site ignores. | rationale-only | L1184 | E6-098 | - | - | none | unknown | rationale |
| EX-DHG-9 | After the retroactive reconcile every ignored item is represented in the active `defer-*` set and Step 1 sees the canonical view. | invariant | L1184 | E6-099 | - | active set | TaskList | unknown | procedure |
| EX-DHG-10 | Step 1: scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. | command | L1186 | E6-100 | active set | TaskList | TaskList | unknown | procedure |
| EX-DHG-11 | If the active set is empty, emit one console line — recommended `Deferral hygiene: no deferred items.` — and proceed to Section 7 (Final Output). | relay | L1186 | E6-101 | console message | empty set | none | unknown | procedure |
| EX-DHG-12 | Step 2: when non-empty, surface the active set as numbered markdown, one bullet per `defer-*` task with its `metadata.activity` as the body. | relay | L1188 | E6-102 | numbered list | `metadata.activity` | TaskList | unknown | procedure |
| EX-DHG-13 | Then fire the gate with the finite choices `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body`. | gate | L1188-1192 | E6-104 | AskUserQuestion | - | AskUserQuestion | unknown | procedure |
| EX-DHG-14 | `Fix in this session`: re-dispatch implementer/reviewer Agents per Section 3's shape, or do the orchestrator-owned ticket-body update inline per the Encode branch; after each item resolves mark its `defer-*` task `completed` with `metadata.activity` updated to log the resolution path. | choice-set | L1190 | E6-106, E6-107 | dispatches / updates; `defer-*` flip | deferred items | Agent, bees, TaskList | unknown | procedure |
| EX-DHG-15 | `File as issue tickets`: for each item invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the body; mark the task `completed` once `/quo-file-issue` returns and the Issue ID is captured. | choice-set | L1191 | E6-108, E6-110 | Issue per item; `defer-*` flip | description | bees, TaskList | unknown | procedure |
| EX-DHG-16 | Rationale: the precedent for inline Skill-tool dispatch is `/quo-fix-issue` Section 1's URL-resolution sub-step and `/quo-plan` Step 4b. | rationale-only | L1191 | E6-109 | - | - | none | unknown | rationale |
| EX-DHG-17 | `Encode in an existing ticket body`: for each item the user maps to a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD (via a doc-writer pass), append a `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body. | choice-set | L1192 | E6-111, E6-112 | body section | user mapping | bees, Agent | unknown, no | procedure |
| EX-DHG-18 | `<YYYY-MM-DD HH:MM>` is the current local time authored as a string via the `Write` tool from your own clock — no `date` / `Get-Date` snippet; keep the `## Deferred from /quo-execute run` stem verbatim and only append the parenthesized suffix. | field-or-template | L1192 | E6-114, E6-115 | heading | own clock | none | unknown, no | procedure |
| EX-DHG-19 | Rationale: the timestamp suffix lets multiple Encodes to the same body across runs sit side-by-side with distinguishable headings. | rationale-only | L1192 | E6-116 | - | - | none | unknown | rationale |
| EX-DHG-20 | Author the revised body to a scratch file via `Write` under `<tempdir>/.quorum/` (create first if absent), named by re-using the triggering `defer-N` task's suffix — `bees-body-<defer-N>.md`, e.g. `bees-body-defer-3.md`. | command | L1192-1208 | E6-117, E6-118 | scratch body file | revised body; `defer-N` name | Bash, TaskList | yes, unknown | procedure |
| EX-DHG-21 | Rationale: re-using the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active set, and ties the file to its TaskList progenitor. | rationale-only | L1192 | E6-119 | - | - | none | unknown | rationale |
| EX-DHG-22 | Snippet order: `mkdir -p /tmp/.quorum` (or `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`), Write the body file, then `bees update-ticket --ids <ticket-id> --body-file <path>`. | ordering | L1192-1208 | E6-113, E6-120 | dir; file; ticket update | - | Bash, bees | yes | procedure |
| EX-DHG-23 | Mark each Encode-routed `defer-*` task `completed` once the `bees update-ticket` update succeeds. | ordering | L1210 | E6-123 | `defer-*` flip | bees result | TaskList, bees | unknown | procedure |
| EX-DHG-24 | Follow-up commit: after all Encode writes in this gate firing have landed, produce exactly one follow-up commit per firing covering all of them — not one per item. | ordering | L1212 | E6-124, E6-126 | git commit | Encode writes | git | yes | procedure |
| EX-DHG-25 | Rationale: this gate fires AFTER Section 4.1's per-Task commits, so `--body-file` writes are not swept into any prior commit and would leave the tree dirty at yield. | rationale-only | L1212 | E6-125 | - | - | none | unknown | rationale |
| EX-DHG-26 | Stage: resolve the Plans, Specs and Issues hive paths via `bees list-hives` (same pattern as 4.1's Plans step), `git add` each in-repo hive path, and additionally the project PRD/SDD paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode there; commit only if `git diff --cached` shows staged changes — otherwise skip rather than produce an empty commit; out-of-repo hives need no git action (`bees update-ticket` already persisted). | command | L1212-1214 | E6-127, E6-128, E6-129, E6-130, E6-135 | staged paths; conditional commit | hive paths; doc paths | bees, git | yes | procedure |
| EX-DHG-27 | Commit subject `Encode deferral: /quo-execute — <N> deferral(s) encoded`; `<N>` counts deferral items, not tickets — the `defer-*` items routed to Encode in this firing, the same value passed as `--count`. | field-or-template | L1212, L1218 | E6-131, E6-132 | commit subject | `<N>` | git | no, yes | procedure |
| EX-DHG-28 | Run the bundled `hive_commit.py` as a single literal Bash call instead of decomposing the commit into shell steps; it resolves hive paths, `git add`s in-repo hive paths and `--doc-path` paths, and commits only if staged — printing `skipped: nothing staged` otherwise. | command | L1214 | E6-133, E6-134 | commit or `skipped: nothing staged` | helper path | Bash, bees, git | yes | procedure |
| EX-DHG-29 | Resolve the helper path against this skill's own base directory — `<this skill's base directory>/scripts/hive_commit.py`, no `..` hop; this differs from `/quo-fix-issue` and `/quo-breakdown-epic`, which resolve the same helper as a sibling (cross-skill consumers). | command | L1216 | E6-137, E6-139 | helper path | base directory | none | no | procedure |
| EX-DHG-30 | Invoke with `--skill quo-execute`, `--count <N>` (matching the subject contract), and one `--doc-path <abs-path>` per PRD/SDD file routed to (omit when none): POSIX `python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]`; PowerShell `python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]`. | command | L1218-1228 | E6-140, E6-141, E6-142, E6-143 | helper invocation | `<N>`, doc paths | Bash | no, yes | procedure |
| EX-DHG-31 | After the helper lands the commit (or prints `skipped: nothing staged`), proceed to Step 3. | ordering | L1230 | E6-144 | - | helper output | Bash | yes | procedure |
| EX-DHG-32 | The three options are non-exclusive at the active-set level: the user may pick one overall or direct different items to different options via the auto-appended free-text slot; the orchestrator parses the reply and closes each `defer-*` task accordingly. | choice-set | L1232 | E6-145, E6-147 | per-item routing | free-text reply | AskUserQuestion, TaskList | unknown | procedure |
| EX-DHG-33 | Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. | invariant | L1232 | E6-146 | all `defer-*` → `completed` | active set | TaskList | unknown | procedure |
| EX-DHG-34 | Step 3: until every `defer-*` task is `completed`, the skill cannot proceed to Section 7 and cannot mark the Bee `done`; the gate refuses to yield while any remain pending or in progress. | invariant | L1234; L478 | E6-148, E2-269 | - | active set | TaskList, bees | unknown | procedure |
| EX-DHG-35 | Rationale: a deferral important enough to surface during the run is important enough to encode in a durable carrier before the run ends. | rationale-only | L1234 | E6-149 | - | - | none | unknown | rationale |
| EX-DHG-36 | If picked options fail to close out a subset (e.g. `/quo-file-issue` cancelled at one of its gates, or `bees update-ticket` errors), surface the still-active tasks via `AskUserQuestion` and re-run the gate until the set is empty. | recovery | L1234 | E6-150 | re-fired gate | failures | AskUserQuestion, TaskList, bees | unknown | procedure |
| EX-DHG-37 | The fresh-session-per-phase recommendation at Bee close-out (Section 7 / Section 10) is preserved verbatim; this gate sits before that handoff prose and does not replace it. | ordering | L1236 | E6-151 | - | - | none | unknown | procedure |

---

## M31. Compromise tracker (file, entry shape, Decision enum, Triggers A–D) (`EX-TRK`)

- **Purpose:** Keep one run-scoped markdown file with a `## Compromise <n>` entry for every accepted compromise — deferred finding, accepted limitation, ungated path pick, post-completion override — so each stays visible and challengeable at the post-completion review.
- **Failure it prevents:** A compromise baked silently into the new baseline; a Trigger A entry that cannot distinguish a soft-fixed finding from an unfixed one; a blocker deferral without its narrowing record.
- **Env deps:** Bash (mkdir), Write tool, AskUserQuestion (gate answers). TaskList-dependent: **no**.
- **Rows after dedupe:** 40 (procedure 32 · rationale 8 · example 0)
- **Literals:** `#### Session-scoped compromise tracker` · `#### Compromise-tracker append triggers` · `compromises-YYYYMMDD-HHMM-<short-suffix>.md` · `20260520-1714` · `## Compromise <n>` · `- **Finding (verbatim):**` · `- **Fix paths surfaced by reviewer:**` · `(a) [depth:<depth>] <description>` · `[depth:<...>]` · `- **Decision:**` · `- **Rationale:**` · `- **Follow-up Issue:**` · `User picked path (a)` · `User picked Defer to follow-up Issue` · `User picked Accept the limitation` · `Orchestrator picked path (x) — highest-quality` · `User overrode auto-route after post-completion challenge (depth misjudgment)` · `User accepted under-enumeration after post-completion challenge` · `Fix paths surfaced by reviewer: none` · `Follow-up Issue: none` · `Trigger A — Defer to follow-up Issue at either gate.` · `Trigger B — Accept the limitation at the scope-bounding gate.` · `Trigger C — ungated route (the orchestrator's own path pick).` · `Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).` · `#### Compromise tracker entry shape`
- **Cross-mechanism edges:** Produces for → POST (PHASE 1–3 input), SUMM (`**Accepted compromises**`), CKPT (carrier 3), PMD (path passed to PM). Consumes from → ROUTE (Triggers A/B/C), POST (Trigger D), MAN (path recorded at run start), SHELL (scratch convention).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-TRK-1 | Maintain a session-scoped compromise tracker: a single markdown file accumulating one entry per accepted compromise across this run — a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override. | definition | L1122 | E6-007, E6-008 | tracker file | - | none | yes | procedure |
| EX-TRK-2 | Rationale: the tracker exists so an accepted compromise stays visible and challengeable rather than baked silently into the new baseline. | rationale-only | L1122 | E6-009 | - | - | none | yes | rationale |
| EX-TRK-3 | The four append triggers (A–D) are defined under `#### Compromise-tracker append triggers`; Section 6's post-completion review consumes the tracker; `#### Session-scoped compromise tracker` is the canonical definition site the trigger write-instructions reference by name. | definition | L1122 | E6-010, E6-011 | - | - | none | unknown | procedure |
| EX-TRK-4 | Write the tracker under `<tempdir>/.quorum/` (`/tmp/.quorum/` POSIX, `%TEMP%\.quorum` Windows) per the scratch-file convention; create the dir if absent (`mkdir -p /tmp/.quorum` / `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`); author and append via the `Write` tool — no shell redirect. | command | L1124-1136 | E6-012, E6-017, E6-018 | tracker location; `.quorum` dir | - | Bash | yes | procedure |
| EX-TRK-5 | Canonical filename `compromises-YYYYMMDD-HHMM-<short-suffix>.md`: `YYYYMMDD-HHMM` a UTC timestamp (e.g. `20260520-1714`) generated once at the start of the run (at the manifest write, per Section 1), `<short-suffix>` a short collision-resistant random string. | name-class | L1124; L217 §1 | E6-013, E6-014, E6-015, E1-138 | tracker filename | run start | none | yes, unknown | procedure |
| EX-TRK-6 | Rationale: the timestamp prefix makes tracker files debuggably identifiable across runs accumulated in `<tempdir>/.quorum/`; without it the user cannot map a file to a session. | rationale-only | L1124 | E6-016 | - | - | none | yes | rationale |
| EX-TRK-7 | Each accepted compromise appends one `## Compromise <n>` section; `<n>` is a 1-based counter scoped to the current run's tracker file, NOT a globally unique identifier. | field-or-template | L1138-1141 | E6-019, E6-020 | `## Compromise <n>` | entry count | none | yes | procedure |
| EX-TRK-8 | The canonical entry shape is reproduced from the SDD Data models `#### Compromise tracker entry shape`. | definition | L1138 | E6-021 | - | - | none | yes | rationale |
| EX-TRK-9 | Field `- **Finding (verbatim):**` carries `<severity tag> <fix-path enumeration with depth tags> <description>`. | field-or-template | L1143, L1153 | E6-022 | field | reviewer finding | none | yes | procedure |
| EX-TRK-10 | Field `- **Fix paths surfaced by reviewer:**` lists `(a) [depth:<depth>] <description>`, `(b) …`, each with its `[depth:<...>]` tag. | field-or-template | L1144-1147 | E6-023 | field | reviewer enumeration | none | yes | procedure |
| EX-TRK-11 | Field `- **Decision:**` takes exactly one value from the enum: `User picked path (a)` / `(b)` / … (one per letter); `User picked Defer to follow-up Issue` (Trigger A); `User picked Accept the limitation` (Trigger B); `Orchestrator picked path (x) — highest-quality` (Trigger C); `User overrode auto-route after post-completion challenge (depth misjudgment)` (SR-6.7 / Trigger D); `User accepted under-enumeration after post-completion challenge` (SR-4.6 / Trigger D). | field-or-template | L1148, L1153 | E6-024, E6-025, E6-026, E6-027, E6-028, E6-029, E6-030 | `Decision` value | - | none | yes | procedure |
| EX-TRK-12 | Field `- **Rationale:**` carries the user's stated reason if surfaced via `AskUserQuestion`, or on an ungated pick the one-line reason that path was preferred; on a `Defer to follow-up Issue` entry it also names which remaining enumerated path shipped as the soft fix, or that none did; on a blocker deferral it carries the narrowing record in place of the shipped-path statement. | field-or-template | L1149, L1153 | E6-031, E6-032, E6-033 | `Rationale` | answer / reason / narrowing | none | yes | procedure |
| EX-TRK-13 | Field `- **Follow-up Issue:**` carries the ticket ID if filed via `/quo-file-issue`, else `none`. | field-or-template | L1150 | E6-034 | field | filing result | none | yes | procedure |
| EX-TRK-14 | The entry has exactly five fields: Finding (verbatim), Fix paths surfaced by reviewer, Decision, Rationale, Follow-up Issue. | definition | L1153 | E6-035 | - | - | none | yes | procedure |
| EX-TRK-15 | Rationale: the enum carries two post-completion-override values because Trigger D is the single owner of all post-completion-override writes regardless of which gate fired. | rationale-only | L1153 | E6-036 | - | - | none | yes | rationale |
| EX-TRK-16 | The tracker, a file-system artifact, persists across orchestrator-yield events within a run inherently. | invariant | L1155 | E6-037 | - | tracker file | none | yes | rationale |
| EX-TRK-17 | Generate a fresh timestamp + suffix at the start of each run; previous-run tracker files are NEVER appended to — each run writes its own new file. | invariant | L1155 | E6-038 | new file per run | - | none | yes | procedure |
| EX-TRK-18 | Four moments append entries: Triggers A–C fire from the routing section's gates / ungated dispatch, Trigger D from Section 6; each trigger anchors to its gate by name and the write fires from the branch named in the trigger. | definition | L1159 | E6-040, E6-041 | - | - | none | unknown | procedure |
| EX-TRK-19 | Trigger A fires at the scope-bounding gate (part (c)) when the user picks `Defer to follow-up Issue`; append IMMEDIATELY AFTER `/quo-file-issue` returns the new Issue ID and BEFORE the soft-fix dispatch. | gate | L1161 | E6-042, E6-043 | tracker entry | Issue ID | AskUserQuestion | unknown | procedure |
| EX-TRK-20 | Trigger A entry: `Follow-up Issue` = the new Issue ID; `Decision: User picked Defer to follow-up Issue`; `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all (reachable at the routing-decision gate, whose `Defer` is offered whatever the path count). | field-or-template | L1161 | E6-044, E6-045, E6-046 | fields | filing result; path count | none | unknown | procedure |
| EX-TRK-21 | Name in `Rationale` which remaining enumerated path shipped as the soft fix — by letter — or that none did ("none did" applies in the single-path case at gate (c) and to any deferral at gate (d), whose Defer ships nothing regardless of path count). | field-or-template | L1161 | E6-047, E6-048 | `Rationale` | soft-fix outcome | none | unknown | procedure |
| EX-TRK-22 | On a `blocker` deferral the narrowing takes that slot — record what was scoped down and why the blocker no longer describes what remains; a blocker-deferral entry MUST carry a narrowing record (what was narrowed out; why the blocker no longer describes anything that ships); one without is the shape every downstream consumer reads as a contract violation. | invariant | L1161 | E6-049, E6-054, E6-055 | `Rationale` narrowing record | narrowing decision | none | unknown | procedure |
| EX-TRK-23 | Rationale: the deferral and what shipped in its place are one decision; an entry recording only the deferral cannot distinguish a soft-fixed finding from an unfixed one. | rationale-only | L1161 | E6-050 | - | - | none | unknown | rationale |
| EX-TRK-24 | The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger on the same terms and entry shape; that gate offers `Defer` to any finding, and to a `blocker` only when part (c)'s two conditions hold. | gate | L1161 | E6-051, E6-052 | tracker entry | gate (d) Defer | AskUserQuestion | unknown | procedure |
| EX-TRK-25 | On a `blocker` this branch is reachable only as Defer-with-narrowing, at either gate (part (c)'s severity rule, applied by part (d) on its own terms). | precondition | L1161 | E6-053 | - | severity | none | unknown | procedure |
| EX-TRK-26 | Trigger B fires at gate (c)'s `Accept the limitation` branch; append IMMEDIATELY AFTER `AskUserQuestion` returns the choice and BEFORE continuing without a fix; `Decision: User picked Accept the limitation`; `Follow-up Issue: none`. | gate | L1163 | E6-056, E6-057, E6-058, E6-059 | tracker entry | answer | AskUserQuestion | unknown | procedure |
| EX-TRK-27 | Trigger B is unreachable for a `blocker`-severity finding, unconditionally — the gate's severity rule withholds the branch since accepting a blocker ships it. | precondition | L1163 | E6-060 | - | severity | none | unknown | procedure |
| EX-TRK-28 | Trigger C has no gate — its write is wired into the dispatch step: at the MOMENT of implementer dispatch for any finding routed by row 6, append the entry in the SAME LOGICAL BLOCK as that dispatch, not a separate post-gate block. | ordering | L1165 | E6-061, E6-062 | tracker entry | row 6 routing | Agent | unknown | procedure |
| EX-TRK-29 | One carve-out: a finding whose only fix path is `trivial-tweak` appends nothing; a pick among two or more paths always appends, even when every path is shallow. | precondition | L1165 | E6-063, E6-064 | - | path count/depth | none | unknown | procedure |
| EX-TRK-30 | Trigger C entry: `Decision: Orchestrator picked path (x) — highest-quality` (`(x)` = chosen letter); `Rationale:` = the orchestrator's own one-line reason for preferring that path over the others — why it is the smallest internally-consistent complete change — not merely the fired rule's name; `Follow-up Issue: none`. | field-or-template | L1165 | E6-065, E6-066, E6-068 | fields | chosen letter; judgement | none | unknown | procedure |
| EX-TRK-31 | Rationale: a bare rule name gives Section 6's challenge nothing to push against. | rationale-only | L1165 | E6-067 | - | - | none | unknown | rationale |
| EX-TRK-32 | Row 6 is Trigger C's only firing site; a `blocker` routed to gate (c) still fires that gate, and a user-picked path is not an ungated route, so no Trigger C entry is written for it. | invariant | L1167 | E6-069, E6-070 | - | - | none | unknown | procedure |
| EX-TRK-33 | Trigger D is the single owner of all post-completion-override writes, fired from Section 6; it covers BOTH SR-6.7 and SR-4.6; its choice labels are byte-identical to the recovery-gate choices. | invariant | L1169 | E6-071, E6-072, E6-073 | tracker entry / in-place update | Section 6 gate results | none | unknown | procedure |
| EX-TRK-34 | SR-6.7 `Accept the misjudgment and proceed` → append a NEW entry IMMEDIATELY AFTER the pick, BEFORE the flow continues: `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)`; `Rationale:` = the post-completion reviewer's challenge text. | ordering | L1171-1172 | E6-074, E6-075, E6-076 | new entry | choice; challenge text | AskUserQuestion | unknown | procedure |
| EX-TRK-35 | SR-6.7 `File follow-up Issue to revisit the depth decision` → NO new entry; UPDATE the ORIGINAL Trigger C entry's `Follow-up Issue` in place to the new Issue ID. | recovery | L1173 | E6-077 | in-place update | Issue ID; Trigger C entry | none | unknown | procedure |
| EX-TRK-36 | Rationale: an originating Trigger C entry always exists to amend, because the depth misjudgment concerns a path the in-flow reviewer surfaced and the orchestrator routed ungated. | rationale-only | L1173 | E6-078 | - | - | none | unknown | rationale |
| EX-TRK-37 | SR-6.7 / SR-4.6 `Pause to discuss` → DEFER any tracker write until the discussion resolves and the user picks again. | ordering | L1174, L1178 | E6-079, E6-086 | - | discussion outcome | none | unknown | procedure |
| EX-TRK-38 | SR-4.6 `Accept the under-enumeration and proceed` → append a NEW entry IMMEDIATELY AFTER the pick, BEFORE the flow continues: `Decision: User accepted under-enumeration after post-completion challenge`; `Rationale:` = the reviewer's under-enumeration challenge text. | ordering | L1175-1176 | E6-080, E6-081, E6-082 | new entry | choice; challenge text | AskUserQuestion | unknown | procedure |
| EX-TRK-39 | SR-4.6 `File follow-up Issue to surface the missing path` → file the Issue and capture its ID; since generally no original Trigger C entry exists to amend, append a new entry with the under-enumeration `Decision` and the Issue ID in `Follow-up Issue`; if the under-enumeration relates to an existing ungated-route finding (originating Trigger C entry exists), mirror the SR-6.7 File branch and UPDATE that entry's `Follow-up Issue` in place instead. | recovery | L1177 | E6-083, E6-084, E6-085 | Issue; new entry or in-place update | Issue ID; Trigger C entry | bees | unknown | procedure |
| EX-TRK-40 | The tracker's `User picked Accept the limitation` `Decision` can never describe a `blocker` finding; `User picked Defer to follow-up Issue` describes a blocker only when that entry's `Rationale` carries the narrowing record Trigger A requires. | invariant | L849 routing (d) | E4-137, E4-138 | - | tracker fields | none | yes | procedure |

---
## M32. Final output & Bee status flip (`EX-FINAL`)

- **Purpose:** Show ignored feedback, demonstrate or hand off each Acceptance Criterion, get sign-off, and — after a defense-in-depth re-check that every Epic is `done` — flip the Bee `done`.
- **Failure it prevents:** Bulk-flipping Epics in Section 8 and silently marking `drafted` work `done`.
- **Env deps:** AskUserQuestion, TaskList, bees, Bash. TaskList-dependent: **yes** (three §7 gates).
- **Rows after dedupe:** 11 (procedure 9 · rationale 2 · example 0)
- **Literals:** `### 7. Final Output` · `### 8. Mark Bee Complete` · `Precondition check (defense-in-depth).` · `"Are you ready to mark this Bee as done?"` · `"Yes, mark as done"` · `"No, we have more work to do"` · `stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status]` · `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.` · `bees update-ticket --ids <bee-id> --status done`
- **Cross-mechanism edges:** Produces for → SUMM (runs after the flip), MERGE. Consumes from → DHG (active set empty), DEFER (ignored list), TRK (surfaced only in §9), GATE, NEXT (Epic statuses should already be `done`).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-FINAL-1 | When all Epics are done, show the User the full list of Reviewer feedback the orchestrator chose to ignore, then use `AskUserQuestion` to ask whether to act on any of it or continue. | gate | L1240-1241 §7 | E7-001, E7-002 | ignored-feedback display; gate | ignored-feedback record | AskUserQuestion | unknown | procedure |
| EX-FINAL-2 | Surface the compromise tracker's entries only in Section 9's `## Bee Execution Complete:` block via its "Accepted compromises" logic, never in the ignored-feedback display. | ordering | L1243 | E7-003 | - | tracker entries | none | no | procedure |
| EX-FINAL-3 | For each Acceptance Criterion, either demonstrate it directly (test or script) or instruct the user how to validate it manually; then use `AskUserQuestion` to get official sign-off. | gate | L1247 | E7-010, E7-011 | demonstration; sign-off gate | Bee's Acceptance Criteria | Bash, AskUserQuestion | no | procedure |
| EX-FINAL-4 | Final Bee-done gate: question `"Are you ready to mark this Bee as done?"`, options exactly `"Yes, mark as done"` and `"No, we have more work to do"`. | field-or-template | L1249-1253 | E7-012, E7-013 | gate | - | AskUserQuestion | no | procedure |
| EX-FINAL-5 | Enter Section 8 only once the user approves the Bee as done. | precondition | L1257 §8 | E7-014 | - | `"Yes, mark as done"` | none | no | procedure |
| EX-FINAL-6 | Rationale: in a healthy flow every Epic was already `status=done` at the end of its 4.2 iteration, so nothing should need a status change here. | rationale-only | L1259 | E7-015 | - | - | none | no | rationale |
| EX-FINAL-7 | Do not bulk-flip Epic statuses in Section 8 (it would silently mark `drafted` work `done`); do not silently update non-`done` Epics. | invariant | L1259, L1271 | E7-016, E7-019 | - | - | bees | no | procedure |
| EX-FINAL-8 | Re-query and verify Epic statuses with `bees execute-freeform-query --query-yaml 'stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status]'`. | command | L1259-1265 | E7-017 | query result | `<bee-id>` | Bash, bees | no | procedure |
| EX-FINAL-9 | If any Epic's `ticket_status` is other than `done`, abort with `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.` | recovery | L1267-1269 | E7-018 | abort message | query result | none | no | procedure |
| EX-FINAL-10 | Rationale: reaching the abort branch indicates an upstream bug — the 4.2 classifier should have stopped the run before Step 7 asked the user to close the Bee. | rationale-only | L1271 | E7-020 | - | - | none | no | rationale |
| EX-FINAL-11 | With all Epics confirmed `done`, mark the Bee with `bees update-ticket --ids <bee-id> --status done`. | command | L1273-1276 | E7-021 | Bee status flip | all-`done` result | Bash, bees | no | procedure |

---

## M33. Bee Execution Complete summary & render rules (`EX-SUMM`)

- **Purpose:** Print the `## Bee Execution Complete: [bee-title]` block with fixed fields, the unconditional Second-order-effects field, the conditional Accepted-compromises field read from the tracker, and the uncommitted-tree sentence.
- **Failure it prevents:** Truncating or eliding accepted compromises; rendering an empty "no compromises" placeholder; writing to the tracker from the read-only surface.
- **Env deps:** git, Bash, Read. TaskList-dependent: **no**.
- **Rows after dedupe:** 14 (procedure 12 · rationale 2 · example 0)
- **Literals:** `### 9. Output Final Summary` · `## Bee Execution Complete: [bee-title]` · `**Bee ID**` · `**Epics Completed**` · `**Tasks Completed**` · `**Bee Status**: Finished` · `**Reviews**` · `Bee-level code review: X issues found/None needed | Test review: Y issues found/None needed | Docs review: Z issues found/None needed` · `**Second-order effects**` · `**Accepted compromises**` · `All per-Task work has been committed.` · `git status --porcelain` · `Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing.` · `Accepted compromises (rendered into the summary block above).` · `N compromises were accepted during this run:` · `Volume (>10 entries).`
- **Cross-mechanism edges:** Produces for → MERGE (the porcelain list). Consumes from → TRK (tracker file), MAN (tracker path recovery), SOE (field content), ROUTE (nit count), BEEREV (review results).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-SUMM-1 | Output the final summary as a markdown block headed `## Bee Execution Complete: [bee-title]`. | field-or-template | L1280-1281 §9 | E7-022 | heading | Bee title | none | no | procedure |
| EX-SUMM-2 | Fixed fields: `**Bee ID**: <bee-id>`; `**Epics Completed**: [count]`; `**Tasks Completed**: [count]`; `**Bee Status**: Finished`. | field-or-template | L1283-1286 | E7-023, E7-024, E7-025, E7-026 | fields | Bee ID; counts | none | no | procedure |
| EX-SUMM-3 | `**Reviews**` renders `Bee-level code review: X issues found/None needed \| Test review: Y issues found/None needed \| Docs review: Z issues found/None needed`, appending `N nits applied without re-review` (or `"count unavailable post-compaction"`) only when any nits were applied. | field-or-template | L1287 | E7-027, E7-028 | field | review results; nit count | none | unknown | procedure |
| EX-SUMM-4 | Render `**Accepted compromises**` per the Accepted-compromises logic, or OMIT IT ENTIRELY when the tracker is empty or absent. | field-or-template | L1289 | E7-030 | conditional field | tracker file | none | yes | procedure |
| EX-SUMM-5 | Closing line `All per-Task work has been committed.`; run `git status --porcelain` and, when it lists anything, add `Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing.`; omit that sentence when the tree is clean. | command | L1291 | E7-031, E7-032, E7-033 | closing lines | `git status --porcelain` | Bash, git | unknown | procedure |
| EX-SUMM-6 | The tracker accumulates one entry per accepted compromise across the whole run; the summary reflects the file's contents at render time. | definition | L1301 | E7-047 | - | tracker file | none | yes | procedure |
| EX-SUMM-7 | Step 1: `Read` the run's tracker at `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (generated once at run start); if the path is no longer in view, recover it from the manifest's **Compromise tracker** field; use no shell to locate or test the file — just `Read` it. | command | L1303 | E7-048, E7-049, E7-050 | tracker contents | tracker path; manifest | none | yes | procedure |
| EX-SUMM-8 | Step 2: omit the section entirely when there is nothing to show — `Read` reports no file OR the file has no `## Compromise <n>` entries; emit no empty heading, no `N/A`, no "no compromises" placeholder; treat absent and empty identically. | invariant | L1304 | E7-051, E7-052, E7-053 | - | `Read` result | none | yes | procedure |
| EX-SUMM-9 | Rationale: file absence is uncommon because an ungated pick among two or more paths appends an entry; Trigger C's lone-`trivial-tweak` carve-out is the only ungated route that appends nothing. | rationale-only | L1304 | E7-054 | - | - | none | yes | rationale |
| EX-SUMM-10 | Step 3: when entries exist, render one bullet per `## Compromise <n>` surfacing exactly four fields — the finding (`Finding (verbatim)`), the chosen path (`Decision`), the rationale (`Rationale`), the follow-up Issue ID (`Follow-up Issue`, a ticket ID or `none`). | field-or-template | L1305-1309 | E7-055, E7-056, E7-057, E7-058, E7-059 | bullets | entry fields | none | yes | procedure |
| EX-SUMM-11 | Do NOT surface the fifth field `Fix paths surfaced by reviewer`. | invariant | L1311 | E7-060 | - | - | none | yes | procedure |
| EX-SUMM-12 | Rationale: the surface shows the path that was chosen, not the full menu the reviewer offered. | rationale-only | L1311 | E7-061 | - | - | none | yes | rationale |
| EX-SUMM-13 | Step 4 — volume (>10 entries): surface them ALL in full — do NOT truncate, summarize away, or elide — preceded by a short prologue noting the volume (e.g. `N compromises were accepted during this run:`). | invariant | L1312 | E7-062, E7-063 | full list; prologue | entry count | none | yes | procedure |
| EX-SUMM-14 | The Accepted-compromises surface only reads the tracker — never write, append to, or delete it; the write side is owned by Section 6.5's append triggers. | invariant | L1314 | E7-064, E7-065 | - | tracker file | none | yes | procedure |

---

## M34. Merge advice per isolation strategy (`EX-MERGE`)

- **Purpose:** After the user has committed what belongs to the Bee, advise on merging according to the Section 1 isolation choice.
- **Failure it prevents:** not stated (implicit: pushing without the user's request).
- **Env deps:** git. TaskList-dependent: **no**.
- **Rows after dedupe:** 5 (procedure 5 · rationale 0 · example 0)
- **Literals:** `### 10. Further testing and merging` · `Worktree` · `Feature branch` · `Worked on main/current branch` · `/bees-worktree-rm` · `git merge <branch>` · `git worktree remove <path>` · `git merge bee/b.Wx7`
- **Cross-mechanism edges:** Consumes from → ISO (strategy), SUMM (porcelain list), MAN (`Isolation strategy` field).

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-MERGE-1 | Instruct the user to perform whatever further testing they want to do. | relay | L1318 §10 | E7-066 | user instruction | - | none | no | procedure |
| EX-MERGE-2 | After the user commits whatever of the summary's `git status --porcelain` list belongs to this Bee (it may include pre-run changes), advise on merging based on the step-1 isolation strategy; every strategy below assumes a clean tree. | ordering | L1318 | E7-067, E7-068 | merging advice | porcelain list; strategy | git | no | procedure |
| EX-MERGE-3 | Worktree: if `/bees-worktree-rm` is installed (not portable core), invoke it to merge the worktree branch and clean up the worktree directory; otherwise instruct the user to merge manually — `git merge <branch>` from the parent repo, then `git worktree remove <path>`. | command | L1320 | E7-069, E7-070 | merged branch / instruction | worktree branch and path | git | no | procedure |
| EX-MERGE-4 | Feature branch: instruct the user to merge the branch (e.g. `git merge bee/b.Wx7`) or open a PR. | relay | L1321; L147 §1 | E7-071, E1-087 | user instruction | branch name | git | no, unknown | procedure |
| EX-MERGE-5 | Worked on main/current branch: per-Task commits are already on the branch; remind the user the work is committed locally and they can push when ready. | relay | L1322 | E7-073 | user reminder | per-Task commits | git | no | procedure |

---

## M35. Shell etiquette, git hygiene & scratch-file convention (`EX-SHELL`)

- **Purpose:** The cross-cutting rules every file-writing and git-touching step obeys: never push, never `git add -A`, write scratch files under `<tempdir>/.quorum/` via the `Write` tool, never delete them.
- **Failure it prevents:** Sweeping other agents' in-flight edits into a commit; permission-prompt churn and lost debugging artifacts from mid-run cleanup.
- **Env deps:** git, Bash. TaskList-dependent: **no**.
- **Rows after dedupe:** 4 (procedure 3 · rationale 1 · example 0)
- **Literals:** `NEVER push to remote — committing only.` · `git add -A` · `rm` · `Remove-Item` · `<tempdir>/.quorum/` · `/tmp/.quorum/` · `%TEMP%\.quorum` · `mkdir -p /tmp/.quorum` · `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null`
- **Cross-mechanism edges:** Consumed by → MAN (EX-MAN-7), TRK (EX-TRK-4), DHG (EX-DHG-20/22), CLEAN (EX-CLEAN-11), MERGE.

| ID | Rule | Kind | Sites | Sources | Produces | Consumes | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| EX-SHELL-1 | NEVER push to remote — committing only; do not push unless the user asks. | invariant | L528 §4.1; L1321 §10 | E3-006, E7-072 | - | - | git | unknown, no | procedure |
| EX-SHELL-2 | Do NOT blindly `git add -A` — other agents or processes may have in-flight changes in the working tree; stage only judgement-selected files, resolved hive paths and explicit `--doc-path` arguments. | invariant | L543 §4.1; L1214 §6.5 | E3-018, E6-136 | - | - | git | unknown, yes | procedure |
| EX-SHELL-3 | Never delete a scratch file (manifest, tracker, `bees-body-*`) — do NOT instruct any `rm` / `Remove-Item` after the bees/helper command exits (scratch-file convention). | invariant | L184 §1; L1155, L1210 §6.5 | E1-117, E6-039, E6-121 | - | - | none | yes | procedure |
| EX-SHELL-4 | Rationale: files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. | rationale-only | L1210 | E6-122 | - | - | none | yes | rationale |

---

## Totals

- **Rows before dedupe:** 1352 (E1 154 · E2 297 · E3 247 · E4 214 · E5 216 · E6 151 · E7 73).
- **Rows after dedupe:** 790 across 35 mechanisms (reduction 562 rows, 41.6%). Every raw ID appears in exactly one `Sources` cell (verified mechanically at assembly: 0 missing, 0 duplicated).

### By Kind (before → after)

| Kind | Raw rows | Deduped rows |
|---|---|---|
| invariant | 329 | 149 |
| definition | 191 | 108 |
| ordering | 151 | 89 |
| command | 141 | 90 |
| field-or-template | 138 | 68 |
| rationale-only | 106 | 93 |
| choice-set | 69 | 57 |
| precondition | 60 | 40 |
| gate | 43 | 29 |
| name-class | 42 | 19 |
| recovery | 38 | 23 |
| relay | 36 | 21 |
| example | 7 | 4 |
| procedure/relay | 1 | 0 |

Note: the single raw `procedure/relay` row (E2-005) is classed `command` after merging into EX-EPIC-1.

### By Class (before → after)

| Class | Raw rows | Deduped rows |
|---|---|---|
| procedure | 1208 | 676 |
| rationale | 131 | 108 |
| example | 12 | 5 |
| failure-narrative | 1 | 1 |

### TaskList dependence

- Raw rows with `TaskList` in Env: **265 / 1352 (19.6%)**.
- Deduped rows with `TaskList` in Env: **158 / 790 (20.0%)**.
- Mechanisms flagged `TaskList-dependent: yes` (any row carries TaskList): 23 of 35 — ABORT, BEE, BEEREV, CKPT, CLEAN, CWG, DEFER, DHG, DPS, EDP, EFF, EPIC, GATE, ISO, LOOP, MOV, NEXT, PCR, PMD, POST, ROUTE, TL, UMG.
- Mechanisms with no TaskList dependence at all: META, PRE, MAN, ROLES, SMW, TEST, SOE, TRK, FINAL, SUMM, MERGE, SHELL.

### Mechanisms ranked by deduped row count

| Rank | Mechanism | Code | Rows | procedure | rationale | example | TaskList rows |
|---|---|---|---|---|---|---|---|
| 1 | Routing discipline — Severity bounds the loop; pick-then-route table; gates (c)/(d); shims (e)/(f); part (g) | `EX-ROUTE` | 94 | 83 | 11 | 0 | 9 |
| 2 | Post-completion review | `EX-POST` | 75 | 63 | 10 | 2 | 15 |
| 3 | Run-state manifest incl. placeholder resolution | `EX-MAN` | 48 | 37 | 11 | 0 | 0 |
| 4 | Compromise tracker (file, entry shape, Decision enum, Triggers A–D) | `EX-TRK` | 40 | 32 | 8 | 0 | 0 |
| 5 | Deferral-hygiene gate (Step 0–3, Fix / File / Encode, `hive_commit.py`) | `EX-DHG` | 37 | 31 | 6 | 0 | 15 |
| 6 | Movement-report rung & `aborted-*` markers | `EX-MOV` | 33 | 30 | 3 | 0 | 16 |
| 7 | Dispatch prompt shape | `EX-DPS` | 32 | 25 | 7 | 0 | 1 |
| 8 | Epic-boundary state-externalization checkpoint | `EX-CKPT` | 32 | 31 | 1 | 0 | 7 |
| 9 | Per-Task cleanup, Format & commit step, per-Task summary template | `EX-CLEAN` | 31 | 28 | 2 | 1 | 4 |
| 10 | Epic-boundary context-window guard | `EX-CWG` | 28 | 26 | 2 | 0 | 2 |
| 11 | Reconciliation loop & per-Subtask fan-out | `EX-LOOP` | 24 | 22 | 2 | 0 | 4 |
| 12 | TaskList progress UI & naming convention | `EX-TL` | 24 | 21 | 3 | 0 | 22 |
| 13 | Session-effort gate | `EX-EFF` | 21 | 14 | 7 | 0 | 6 |
| 14 | Next-Epic routing & inter-Epic interaction checkpoint | `EX-NEXT` | 21 | 19 | 2 | 0 | 1 |
| 15 | Aborted-run close-out | `EX-ABORT` | 20 | 16 | 3 | 1 | 6 |
| 16 | Engineer-dispatch precondition (Clause 1 / Clause 2) | `EX-EDP` | 20 | 15 | 5 | 0 | 13 |
| 17 | Epic selection, run-mode gate (Mode 1/2), staleness, status flips | `EX-EPIC` | 17 | 17 | 0 | 0 | 1 |
| 18 | Preconditions & contract keys | `EX-PRE` | 16 | 12 | 3 | 1 | 0 |
| 19 | Unexplained-movement gate | `EX-UMG` | 15 | 15 | 0 | 0 | 8 |
| 20 | Roles & lane boundaries | `EX-ROLES` | 15 | 13 | 1 | 1 | 0 |
| 21 | Bee-level reviews (Section 5) & Bee-level close-out | `EX-BEEREV` | 15 | 12 | 3 | 0 | 7 |
| 22 | `gate-*` two-step contract | `EX-GATE` | 14 | 13 | 1 | 0 | 9 |
| 23 | Second-order-effects relay & destinations | `EX-SOE` | 14 | 11 | 3 | 0 | 0 |
| 24 | Bee Execution Complete summary & render rules | `EX-SUMM` | 14 | 12 | 2 | 0 | 0 |
| 25 | Ignored-feedback / `defer-*` ledger | `EX-DEFER` | 13 | 9 | 4 | 0 | 6 |
| 26 | Testing discipline (five-rung ladder) & long commands | `EX-TEST` | 12 | 11 | 1 | 0 | 0 |
| 27 | Final output & Bee status flip | `EX-FINAL` | 11 | 9 | 2 | 0 | 0 |
| 28 | Bee selection & validation | `EX-BEE` | 10 | 10 | 0 | 0 | 2 |
| 29 | Isolation strategy | `EX-ISO` | 10 | 8 | 2 | 0 | 1 |
| 30 | Frontmatter & overview | `EX-META` | 9 | 9 | 0 | 0 | 0 |
| 31 | Post-compaction recovery & context ownership | `EX-PCR` | 8 | 6 | 2 | 0 | 2 |
| 32 | Merge advice per isolation strategy | `EX-MERGE` | 5 | 5 | 0 | 0 | 0 |
| 33 | Per-Task PM dispatch | `EX-PMD` | 4 | 4 | 0 | 0 | 1 |
| 34 | Scoped-marker PM wiring | `EX-SMW` | 4 | 4 | 0 | 0 | 0 |
| 35 | Shell etiquette, git hygiene & scratch-file convention | `EX-SHELL` | 4 | 3 | 1 | 0 | 0 |

## Literals index

528 distinct verbatim strings (names, labels, headings, file names, commands, enum values) owned by the mechanisms above, alphabetical (case-insensitive). A literal listed under two mechanisms is used by both; the first-listed owns the definition site.

- `"[<bee-id> \| <epic-id>]"` — META
- `"Are you ready to mark this Bee as done?"` — FINAL
- `"Do NOT add X — out of scope"` — ROUTE
- `"no Engineer Agent will be dispatched for this Bee while you are running"` — DPS
- `"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running"` — DPS
- `"No, we have more work to do"` — FINAL
- `"None"` — CLEAN
- `"out of scope for <id>"` — ROUTE
- `"out of scope for this issue"` — ROUTE
- `"prefer (a)"` — ROUTE
- `"prefer option (a)"` — ROUTE
- `"the source tree is frozen"` — DPS
- `"Yes, mark as done"` — FINAL
- `# Run state — quo-execute @ <bee-id>` — MAN
- `## Bee Execution Complete: [bee-title]` — SUMM
- `## Build Commands` — PRE
- `## Compromise <n>` — TRK
- `## Cumulative project doc updates` — ROLES
- `## Deferred from /quo-execute run` — DHG
- `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` — DHG
- `## Documentation Locations` — PRE
- `## Engineer's completeness evidence` — DPS
- `## Files changed` — DPS
- `## Install` — PRE
- `## Perturbations` — MOV
- `## Source paths to fingerprint` — DPS
- `## Task [N] of [total] Complete: [task-title]` — CLEAN
- `### 10. Further testing and merging` — MERGE
- `### 2. Find Epic to work on and validate` — EPIC
- `### 3. Execute Tasks via per-Subtask Agent dispatch` — LOOP
- `### 5. Final Bee-level Code, Doc and Eng reviews` — BEEREV
- `### 6. Post-Completion Review` — POST
- `### 6.5 Before handoff — deferral hygiene` — DHG
- `### 7. Final Output` — FINAL
- `### 8. Mark Bee Complete` — FINAL
- `### 9. Output Final Summary` — SUMM
- `### Deferred refinements` — DEFER
- `### Feature: <title>` — ROLES
- `### Orchestrator discipline: routing review findings` — ROUTE
- `### Resolving reference_materials entries` — ROLES
- `### Second-order effects` — SOE
- `#### 4.1 After Each Task` — CLEAN
- `#### 4.2 Find next Epic or move to Final Review` — NEXT
- `#### <invocation scope>` — SOE
- `#### Check if stale` — EPIC
- `#### Compromise tracker entry shape` — TRK
- `#### Compromise-tracker append triggers` — TRK
- `#### Hub-and-spoke via substrate` — LOOP
- `#### Mark status when ready to start work` — EPIC
- `#### Per-Subtask cold dispatch` — LOOP
- `#### Pick a multi-Epic run mode (only when more than one Epic is in scope)` — EPIC
- `#### Reconciliation loop` — LOOP
- `#### Recursive delegation: not supported` — LOOP
- `#### Resolve the manifest placeholders` — MAN
- `#### Roles dispatched by the orchestrator` — ROLES
- `#### Running long commands` — TEST
- `#### Scoped-marker PM dispatch wiring` — SMW
- `#### Session-scoped compromise tracker` — TRK
- `#### TaskList as progress UI` — TL
- `#### Testing discipline — avoid redundant full-workspace runs` — TEST
- `#### Write the run-state manifest` — MAN
- `##### Aborted-run close-out` — ABORT
- `##### Anti-pattern: no clock primitives` — LOOP
- `##### Dispatch prompt: quote the ticket body verbatim` — DPS
- `##### Epic-boundary context-window guard` — CWG
- `##### Epic-boundary state-externalization checkpoint` — CKPT
- `##### Per-Task PM dispatch` — PMD
- `##### TaskList naming convention` — TL
- `$env:TEMP\.quorum\run-state-quo-execute-<bee-id>.md` — MAN
- `%TEMP%\.quorum` — SHELL
- `(a) [depth:<depth>] <description>` — TRK
- `(a) Pick the path, then route on it.` — ROUTE
- `(b) ANTI-PATTERN — do not write this:` — ROUTE
- `(c) Scope-bounding gate.` — ROUTE
- `(d) Routing-decision gate.` — ROUTE
- `(e) Backwards-compatibility shim.` — ROUTE
- `(f) Edge-case handling.` — ROUTE
- `(g) Re-dispatch ordering when a fix path changes source.` — ROUTE
- `(Recommended)` — ROUTE
- `**Accepted compromises**` — SUMM
- `**Bee ID**` — SUMM
- `**Bee Status**: Finished` — SUMM
- `**Compromise tracker:**` — MAN
- `**Epics Completed**` — SUMM
- `**Files Changed**` — CLEAN
- `**Follow-up Tasks Created**` — CLEAN
- `**Ignored Review Feedback**` — CLEAN
- `**Isolation strategy:**` — MAN
- `**Multi-Epic run mode:**` — MAN
- `**Next unit:**` — MAN
- `**Pre-Bee SHA:**` — MAN
- `**Progress:**` — MAN
- `**Reviews**` — CLEAN, SUMM
- `**Run started (UTC):**` — MAN
- `**Second-order effects**` — CLEAN, SOE, SUMM
- `**Skill:**` — MAN
- `**Task ID**` — CLEAN
- `**Tasks Completed**` — SUMM
- `**Unit scope:**` — MAN
- `**Your next tool use MUST address these findings now.**` — BEEREV
- `**Your next tool use MUST advance the workflow.**` — BEEREV
- `- **Decision:**` — TRK
- `- **Finding (verbatim):**` — TRK
- `- **Fix paths surfaced by reviewer:**` — TRK
- `- **Follow-up Issue:**` — TRK
- `- **Rationale:**` — TRK
- `--count <N>` — DHG
- `--doc-path <abs-path>` — DHG
- `--skill quo-execute` — DHG
- `-r<n>` — MOV, TL
- `.bees/` — CLEAN
- `.T` — TEST
- `/agents` — PRE
- `/bees-fleet` — ISO
- `/bees-worktree-add` — ISO
- `/bees-worktree-rm` — MERGE
- `/loop` — LOOP
- `/model` — EFF
- `/quo-execute <bee-id>` — ABORT, CWG
- `/quo-file-issue` — ROUTE
- `/quo-plan` — BEE
- `/quo-plan-from-specs` — BEE
- `/quo-setup --configure-gauge-producer` — CWG
- `/tmp/.quorum/` — SHELL
- `/tmp/.quorum/run-state-quo-execute-<bee-id>.md` — MAN
- `20260520-1714` — TRK
- `540000` — TEST
- `600000` — TEST
- `<bee-id>: Bee-level review aborted — <what stopped it>` — MAN
- `<compromise-tracker-path>` — PMD, POST
- `<current>` — EFF
- `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>` — MAN
- `<epic-id>: done — last commit <sha>` — MAN
- `<pre-bee-sha>` — MAN, POST
- `<previous-epic-last-commit>` — MAN
- `<reviewer>-<bee-id>` — TL
- `<role>-<bee-id>` — MOV, TL
- `<role>-<subtask-id>` — TL
- `<role>-postcomp-<n>` — POST, TL
- `<role>-postcomp-<n>-r<k>` — POST, TL
- `<scoped-marker-resolver-path>` — PMD, SMW
- `<tempdir>/.quorum/` — SHELL
- `<tempdir>/.quorum/context-guard-opt-out` — CWG
- `<tempdir>/.quorum/context-usage-<session_id>.json` — CWG
- `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` — SMW
- `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` — CWG
- `<this skill's base directory>/scripts/hive_commit.py` — DHG
- `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py` — SMW
- `<this skill's base directory>\..\quo-setup\scripts\context_gauge.py` — CWG
- `[compromise-challenge]` — POST
- `[defect]` — POST
- `[depth:<...>]` — TRK
- `[design]` — POST
- `[introduces-mechanism]` — ROUTE
- `[preferred]` — ROUTE
- `Abort this unit` — ABORT, UMG
- `aborted-` — EDP
- `aborted-*` — TL
- `aborted-<role>-<bee-id>` — MOV
- `aborted-<role>-<id>` — MOV
- `aborted-<role>-<subtask-id>` — MOV
- `aborted-<role>-postcomp-<n>` — MOV, POST
- `aborted-doc-writer-<bee-id>` — BEEREV
- `aborted-doc-writer-<subtask-id>` — MOV
- `Aborted-path qualification — Bee-level scope.` — CKPT
- `Aborted-path qualification — mid-Epic scope.` — CKPT
- `aborted-test-writer-<bee-id>` — BEEREV
- `aborted-test-writer-<subtask-id>` — MOV
- `Accept the limitation` — ROUTE
- `Accept the misjudgment and proceed` — POST
- `Accept the under-enumeration and proceed` — POST
- `Accepted compromises (rendered into the summary block above).` — SUMM
- `addressed-now-in-this-Task` — DEFER
- `Agent type '<name>' not found` — PRE
- `Agent(name=...)` — LOOP
- `Agent(subagent_type="code-reviewer", run_in_background=true)` — BEEREV
- `Agent(subagent_type="doc-reviewer", run_in_background=true)` — BEEREV
- `Agent(subagent_type="test-reviewer", run_in_background=true)` — BEEREV
- `Agent(subagent_type=<role>, run_in_background=true, prompt=…)` — LOOP
- `agents/code-reviewer.md` — ROLES
- `agents/doc-reviewer.md` — ROLES
- `agents/doc-writer.md` — ROLES
- `agents/engineer.md` — ROLES
- `agents/pm.md` — ROLES
- `agents/test-reviewer.md` — ROLES
- `agents/test-writer.md` — ROLES
- `All Epics under this Bee are `done`` — NEXT
- `All per-Task work has been committed.` — SUMM
- `Anti-pattern callout — read before acting.` — POST
- `Anti-pattern callout, second.` — POST
- `AskUserQuestion` — GATE
- `b.Wx7` — ISO
- `b_Wx7` — ISO
- `Base directory for this skill: /Users/.../quo-execute` — SMW
- `Bash(command: "<your project's test command per CLAUDE.md>", timeout: 540000)` — TEST
- `Bash(run_in_background: true)` — TEST
- `Bee scope` — ABORT
- `Bee-level` — ABORT
- `Bee-level code review: X issues found/None needed \| Test review: Y issues found/None needed \| Docs review: Z issues found/None needed` — SUMM
- `Bee-level TaskList close-out (runs once, after the review loop above has closed).` — BEEREV
- `Bee-scoped case — the bees corrective is a no-op.` — MOV
- `bee/b.Wx7` — ISO
- `bees` — ROLES
- `bees execute-freeform-query --query-yaml` — BEE
- `bees list-hives` — DHG, PRE
- `bees show-ticket --ids <bee-id>` — POST
- `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>` — EPIC
- `bees show-ticket --ids <epic-id-1> <task-id-1> ...` — POST
- `bees show-ticket --ids <epic-id>` — LOOP
- `bees show-ticket --ids <subtask-id>` — EDP
- `bees show-ticket --ids <ticket-id>` — DPS
- `bees update-ticket --ids <bee-id> --status done` — FINAL
- `bees update-ticket --ids <subtask-id> --status in_progress` — MOV
- `bees update-ticket --ids <ticket-id> --body-file <path>` — DHG
- `bees-body-<defer-N>.md` — DHG
- `bees-body-defer-3.md` — DHG
- `blocker` — ROUTE
- `branch created: <name>` — MAN
- `Cancel` — ABORT, ROUTE
- `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.` — FINAL
- `Chat about this` — GATE, UMG
- `Check session reasoning effort` — GATE
- `children` — LOOP
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` — LOOP
- `CLAUDE_CODE_SESSION_ID` — CWG
- `CLAUDE_EFFORT` — EFF
- `Clause 1 — the per-Task review site` — EDP
- `Clause 2 — the Bee-level review site` — EDP
- `Close out the TaskList, sweeping by name prefix.` — ABORT
- `code-reviewer` — PRE
- `code-reviewer-<bee-id>` — BEEREV, EDP
- `code-reviewer-<bee-id>-r1` — BEEREV, EDP
- `code-reviewer-b.abc` — TL
- `code-reviewer-b.abc-r1` — TL
- `Compile/type-check` — PRE, TEST
- `completed` — TL
- `Compromise tracker` — CKPT
- `Compromise-challenge preamble (rendered before presenting the findings).` — POST
- `compromises-YYYYMMDD-HHMM-<short-suffix>.md` — TRK
- `Configure now` — CWG
- `context_gauge.py` — CWG
- `context_window` — CWG
- `Contract drift` — NEXT
- `Conversation memory is never a substitute for these four sources.` — PCR
- `count unavailable post-compaction` — CLEAN, ROUTE
- `Create a feature branch (Recommended)` — ISO
- `CronCreate` — LOOP
- `Ctrl-C` — ABORT
- `current branch: <name>` — MAN
- `Decision: User accepted under-enumeration after post-completion challenge` — POST
- `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` — POST
- `Defer to follow-up Issue` — ROUTE
- `defer-*` — DEFER
- `defer-1` — TL
- `defer-2` — TL
- `defer-<short-suffix>` — DEFER, TL
- `defer-N` — DEFER
- `defer-to-existing-ticket-body: <ticket-id>` — DEFER
- `defer-to-new-Issue` — DEFER
- `Deferral hygiene: no deferred items.` — DHG
- `doc-reviewer` — PRE
- `doc-reviewer-<bee-id>` — BEEREV, EDP
- `doc-reviewer-b.abc` — TL
- `doc-writer` — PRE
- `doc-writer-<bee-id>` — BEEREV, EDP
- `doc-writer-<subtask-id>` — EDP, MOV
- `doc-writer-<subtask-id>-r1` — EDP
- `doc-writer-b.abc` — TL
- `doc-writer-postcomp-2` — TL
- `doc-writer-postcomp-<n>` — POST
- `doc-writer-t3.abc.def.kl` — TL
- `doc-writer-t3.abc.def.kl-r1` — TL
- `Does NOT modify source code, tests, or docs` — ROLES
- `Does NOT review <other-lanes>` — ROLES
- `done` — BEE, NEXT
- `drafted` — EPIC, NEXT
- `Drafted (or blocked-on-drafted) Epics remain` — NEXT
- `Encode deferral: /quo-execute — <N> deferral(s) encoded` — DHG
- `Encode in an existing ticket body` — DHG
- `engineer` — PRE
- `engineer-<bee-id>` — BEEREV, DPS, EDP
- `engineer-<bee-id>-r1` — BEEREV
- `engineer-<issue-id>-r<n>` — TL
- `engineer-b.abc` — TL
- `engineer-b.abc-r1` — TL
- `engineer-b.abc-r2` — TL
- `engineer-postcomp-1` — TL
- `engineer-postcomp-3` — TL
- `engineer-postcomp-<n>` — POST
- `engineer-t3.abc.def.gh` — TL
- `Epic `<just-completed-epic-id>` is complete, but Epics `<drafted-or-blocked-ids>` … are still `drafted` … Run `/quo-breakdown-epic <bee-id>` (a fresh session is reasonable …), then re-run `/quo-execute <bee-id>`.` — NEXT
- `Epic N, Task M — …` — CLEAN
- `Epics in scope` — CKPT, MAN
- `Exception — the all-Epics-already-done-at-run-start path.` — CKPT
- `existed but is unavailable post-compaction` — DPS
- `Feature branch` — MERGE
- `File as issue tickets` — DHG, POST
- `File follow-up Issue to revisit the depth decision` — POST
- `File follow-up Issue to surface the missing path` — POST
- `file-path` — ROLES
- `file:line` — POST
- `Final Task, moving on to Final Reviews` — CLEAN
- `Fix in this session` — DHG, POST
- `Fix paths surfaced by reviewer: none` — TRK
- `Fix properly now` — ROUTE
- `Follow the trailer literally` — BEEREV
- `Follow-up Issue: none` — TRK
- `Format` — PRE, TEST
- `fresh session` — PCR
- `Full test` — PRE, TEST
- `gate-*` — GATE
- `gate-<kind>-<short-suffix>` — TL
- `gate-askuserquestion-1` — TL
- `gate-askuserquestion-<short-suffix>` — GATE
- `general-purpose` — PRE
- `git add -A` — SHELL
- `git diff --cached` — DHG
- `git diff --name-only HEAD` — DPS
- `git diff <pre-bee-sha>` — POST
- `git hash-object` — MOV
- `git log --oneline <previous-epic-last-commit>..HEAD` — CKPT, NEXT
- `git ls-files --others --exclude-standard` — POST
- `git merge <branch>` — MERGE
- `git merge bee/b.Wx7` — MERGE
- `git rev-parse HEAD` — MAN, MOV
- `git status` — CLEAN
- `git status --porcelain` — SUMM
- `git worktree remove <path>` — MERGE
- `HEAD~M` — POST
- `high` — EFF
- `hive_commit.py` — CLEAN, DHG
- `How should this run handle multiple Epics? (You will not be asked again this run.)` — EPIC
- `IMPORTANT` — BEEREV
- `in_progress` — BEE, NEXT, TL
- `inter-Epic interaction checkpoint` — NEXT
- `Let me change it first` — EFF
- `Lint` — PRE, TEST
- `low` — EFF
- `max` — EFF
- `medium` — EFF
- `metadata.activity` — MOV, TL
- `mid-Epic` — ABORT
- `missing` — CWG
- `mkdir -p /tmp/.quorum` — SHELL
- `Mode 1 (Stop after each Epic)` — MAN, NEXT
- `Mode 2 (Work through all Epics)` — MAN, NEXT
- `Mode 2 (Work through all Epics): auto-continuing to <next-epic-id> — <title>.` — NEXT
- `Movement report from a Test Writer or Doc Writer.` — MOV
- `multi-Epic run mode` — EPIC
- `Multi-Epic run mode` — CKPT
- `N compromises were accepted during this run:` — SUMM
- `N nits applied without re-review` — CLEAN, ROUTE
- `Narrow test` — PRE, TEST
- `Never guard me (persistent opt-out)` — CWG
- `NEVER push to remote — committing only.` — SHELL
- `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null` — SHELL
- `nit` — ROUTE
- `no issues found` — POST
- `No second-order effects identified.` — SOE
- `no-reading` — CWG
- `None` — MOV
- `none` — CKPT
- `None identified.` — SOE
- `normalized_name` — PRE
- `not captured` — CKPT, MAN
- `not captured (all Epics already done)` — CKPT, MAN
- `not captured (single Epic in scope)` — MAN
- `Opus (always)` — ROLES
- `Orchestrator picked path (<letter>) — highest-quality` — POST
- `Orchestrator picked path (x) — highest-quality` — TRK
- `Orchestrator self-tracking close-out (mandatory before yielding).` — POST
- `Pause to discuss` — POST
- `pending` — TL
- `pending Section 2 query` — CKPT, MAN
- `Per-Task scope` — ABORT
- `PHASE 1` — POST
- `PHASE 2` — POST
- `PHASE 3` — POST
- `PHASE 4` — POST
- `PHASE 5` — POST
- `PHASE 6` — POST
- `Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)` — CLEAN
- `Plan b.bc7, Epic 1, Task 7 — Document the new auth config surface (t2.rwx.fy.qq)` — CLEAN
- `plans` — PRE
- `pm` — PRE
- `pm-<bee-id>` — BEEREV, EDP, PMD, TL
- `pm-<bee-id>-r2` — EDP
- `pm-<task-id>` — EDP, PMD, TL
- `pm-b.abc` — TL
- `pm-t2.abc.def.gh` — TL
- `pm-t2.abc.def.gh-r1` — TL
- `Post-completion review found [N] issues. How would you like to handle them?` — POST
- `Post-completion review: no issues found` — POST
- `Pre-Bee SHA` — CKPT
- `Precondition check (defense-in-depth).` — FINAL
- `printenv CLAUDE_CODE_SESSION_ID` — CWG
- `printenv CLAUDE_EFFORT` — EFF
- `Proceed anyway` — EFF
- `Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.` — META
- `Proceed without the guard (this run)` — CWG
- `Proceeding to next Task: [next-task-title]` — CLEAN
- `Progress` — CKPT
- `python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]` — DHG
- `python "<this skill's base directory>\scripts\hive_commit.py" resolve-hive-paths --hive plans` — CLEAN
- `python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]` — DHG
- `python3 "<this skill's base directory>/scripts/hive_commit.py" resolve-hive-paths --hive plans` — CLEAN
- `quo-execute` — META
- `re-architect` — ROUTE
- `Re-dispatch the Analyst with this finding` — ROUTE
- `Re-dispatch the writer now` — UMG
- `Re-read, do not recall, at every dispatch in the next Epic.` — CKPT
- `read --session-id <trimmed-session-id>` — CWG
- `Read state` — LOOP
- `README.md` — PRE
- `ready` — BEE, NEXT
- `Recommended default on the mechanism row.` — ROUTE
- `Reconcile` — LOOP
- `Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.` — DEFER
- `Record each ignored-feedback item as a `defer-N` TaskList task at the moment of decision.` — DEFER
- `Record each PM-deferred item as a `defer-N` TaskList task at the moment of the PM verdict.` — DEFER
- `refactor-locally` — ROUTE
- `reference_materials` — ROLES
- `Remove-Item` — SHELL
- `resolve-hive-paths` — CLEAN
- `Resource compounding` — NEXT
- `Rewrite the run-state manifest` — CKPT
- `rm` — SHELL
- `Run /quo-setup first.` — PRE
- `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` — PRE
- `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` — PRE
- `run-state-quo-execute-<bee-id>.md` — MAN
- `run_in_background=true` — LOOP
- `Scenario A — Already in a worktree` — ISO
- `Scenario B — On an existing branch in the main repo` — ISO
- `ScheduleWakeup` — LOOP
- `Scope limit — this part governs the review-finding re-dispatch path only.` — EDP
- `Second-order effects (rendered into the summary block above).` — SOE
- `SendMessage` — LOOP
- `session_id` — CWG
- `Set up a worktree instead` — ISO
- `Severity bounds the loop.` — ROUTE
- `Skip` — POST
- `skipped: nothing staged` — DHG
- `specs` — PRE
- `SR-4.6 under-enumeration recovery gate.` — POST
- `SR-6.7 ungated-route recovery gate.` — POST
- `stages: - [id=<epic-id>] - [parent] report: [title, ticket_status]` — BEE
- `stages: - [id=<ticket-id>] report: [title, ticket_status]` — LOOP
- `stages: - [parent=<bee-id>, type=t1, status=ready] report: [title, up_dependencies]` — BEE
- `stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status, up_dependencies]` — EPIC
- `stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status]` — FINAL
- `stages: - [type=bee, hive=plans] report: [title, ticket_status]` — BEE
- `stale` — CWG
- `status!=drafted` — LOOP
- `status=done` — CLEAN
- `status=in_progress` — EPIC
- `Step 0 — Retroactive ledger reconciliation (safety net).` — DHG
- `Step 1 — Enumerate the active deferral ledger.` — DHG
- `Step 1 — pick.` — ROUTE
- `Step 2 — route on the path chosen in Step 1.` — ROUTE
- `Step 2 — Surface the active set and gate the user choice.` — DHG
- `Step 3 — Hard-stop on a non-empty active set.` — DHG
- `Stop after each Epic` — EPIC
- `Stop here` — CWG
- `Stop the run and name the resume command.` — ABORT
- `stop-threshold` — CWG
- `Subagent effort is pinned per role and is NOT affected by this setting.` — EFF
- `subagent_type=general-purpose` — POST
- `suggestion` — ROUTE
- `sweep-shaped` — DPS
- `Symmetric-change gaps` — NEXT
- `t1=Doc` — ROLES
- `TaskCreate` — GATE
- `test -f /tmp/.quorum/context-guard-opt-out` — CWG
- `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"` — CWG
- `test-reviewer` — PRE
- `test-reviewer-<bee-id>` — BEEREV, EDP
- `test-reviewer-b.abc` — TL
- `test-writer` — PRE
- `test-writer-<bee-id>` — BEEREV, EDP
- `test-writer-<subtask-id>` — EDP, MOV
- `test-writer-b.abc` — TL
- `test-writer-postcomp-2-r1` — TL
- `test-writer-postcomp-<n>` — POST
- `test-writer-t3.abc.def.ij` — TL
- `the orchestrator dispatched no Engineer for this unit while the writer was running, and no returned concurrently-dispatched Test Writer's `## Perturbations` list names the moved paths, so it cannot attribute the movement.` — UMG
- `This session is running at `effort=<current>`, below the `medium` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.` — EFF
- `ticket_status` — BEE
- `timeout` — TEST
- `Trigger A` — ROUTE
- `Trigger A — Defer to follow-up Issue at either gate.` — TRK
- `Trigger B` — ROUTE
- `Trigger B — Accept the limitation at the scope-bounding gate.` — TRK
- `Trigger C` — ROUTE
- `Trigger C — ungated route (the orchestrator's own path pick).` — TRK
- `Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).` — TRK
- `trivial-tweak` — ROUTE
- `Type something.` — GATE, UMG
- `Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing.` — SUMM
- `Unexplained-movement gate.` — UMG
- `up_dependencies` — BEE
- `used_percentage` — CWG
- `User accepted under-enumeration after post-completion challenge` — TRK
- `User overrode auto-route after post-completion challenge (depth misjudgment)` — TRK
- `User picked Accept the limitation` — TRK
- `User picked Defer to follow-up Issue` — TRK
- `User picked path (a)` — TRK
- `Verify the carriers.` — CKPT
- `Volume (>10 entries).` — SUMM
- `Wait` — UMG
- `What "highest-quality" means.` — ROUTE
- `What "introduces a mechanism" means.` — ROUTE
- `What this checkpoint does not do.` — PCR
- `What this guard is (and is not).` — CWG
- `Work on current branch` — ISO
- `Work through all Epics` — EPIC
- `Workable Epic remains` — NEXT
- `Worked on main/current branch` — MERGE
- `Worktree` — MERGE
- `worktree: <path>` — MAN
- `write-opt-out` — CWG
- `Write-Output $env:CLAUDE_CODE_SESSION_ID` — CWG
- `Write-Output $env:CLAUDE_EFFORT` — EFF
- `xhigh` — EFF
- `Yield` — LOOP
- `You are an independent reviewer for a quorum Bee that was just shipped.` — POST
- `~25-30% of a 1M context window` — PCR
- `⚠️` — POST

## Inconsistencies noticed

Each item cites the raw Sources. Where two rows conflict, both are retained in the tables above.

1. **Undefined referent — "three scenarios" with two defined.** `#### Validate isolation strategy` says it names three scenarios, but only Scenario A (worktree) and Scenario B (branch in main repo) exist. — E1-081 (kept as EX-ISO-1).
2. **Branch 3 described two ways.** Section 2 says branch 3 "exits the run with no Epic boundary crossed" when all Epics are `done`; Section 4.2 says branch 3 runs the state-externalization checkpoint (next unit `none`) and *proceeds to Step 5 final Bee review*, and the checkpoint's own exception paragraph confirms branch 3 is entered on the all-done path. — E2-016 vs E3-102, E3-132 (kept as EX-EPIC-10 vs EX-NEXT-21 / EX-CKPT-21).
3. **Trailer-less gate enumeration is incomplete.** The naming convention lists the trailer-less gates as: §1 session-effort, §3 unexplained-movement, §4.2 Mode 1 continuation, §6 findings gate, §6.5 deferral hygiene, §7 Acceptance-Criteria sign-off and Bee close-out. It omits §1's Bee-pick and isolation gates (E1-031), §7's ignored-feedback action gate (E7-002, E7-005 says §7 has *three* gates), the context-window guard's missing-reading gate (E3-201), the routing gates (c)/(d) (E4-069, E4-120), and the SR-6.7 / SR-4.6 recovery gates (E5-184). — E2-274 vs E1-031, E7-005, E3-201, E4-069, E4-120, E5-184.
4. **Completeness-evidence heading: "recommended" vs "MUST", conditional vs unconditional attribution.** Section 3 says the label `## Engineer's completeness evidence` is *recommended* and to name the source Subtask only *when more than one Engineer contributed*; Section 5 says the heading is required and each list is attributed to its Subtask unconditionally. — E2-225, E2-227 vs E5-004, E5-005 (merged with both wordings retained in EX-DPS-23).
5. **4.1's hive-path source misdescribed by 6.5.** Section 6.5 says to resolve hive paths "via `bees list-hives` (same pattern as Section 4.1's commit step for Plans)", but Section 4.1 resolves the Plans path with `hive_commit.py resolve-hive-paths --hive plans`, not `bees list-hives`. — E6-127 vs E3-013, E3-016.
6. **6.5 gives both a manual staging recipe and says to use the helper instead.** The prose instructs `bees list-hives` → `git add` in-repo hives → `git add` PRD/SDD paths → commit only if `git diff --cached` is non-empty, then says to run `hive_commit.py` as a single literal call "instead of decomposing the commit workflow into shell steps". Under this repo's bash-etiquette rule the decomposed recipe cannot be executed as written. — E6-127, E6-128, E6-129, E6-130 vs E6-133, E6-134.
7. **`HEAD~M` fallback ignores non-Task commits.** The post-completion fallback for a missing manifest takes `HEAD~M` where M = Tasks committed, but the inter-Epic interaction checkpoint records fix commits as *additional* commits on the branch, so M under-counts. — E5-082 vs E3-076.
8. **Shared gate labels across two different gates.** `Fix in this session` and `File as issue tickets` are the first two options of both the §6 post-completion gate (third option `Skip`) and the §6.5 deferral-hygiene gate (third option `Encode in an existing ticket body`); recovery from a stranded `gate-*` task via `metadata.activity` choices (E2-279) cannot distinguish them by label alone. — E5-153 vs E6-104.
9. **Stale "Team" vocabulary in the Overview.** The Overview says "form a Team", "disband execution Team", "form Review Team", while Section 3 states there is no long-lived team, no warmed Agents, and cold per-Subtask dispatch is the intended shape. — E1-006, E1-009 vs E2-051, E2-052, E2-156.
10. **Tracker filename notation drift.** The tracker file is written `compromises-YYYYMMDD-HHMM-<short-suffix>.md` at its definition site but `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` in the manifest field and the post-completion prompt. — E6-013, E7-048 vs E1-128, E5-088.
11. **"Step N" vs "Section N" naming.** The same units are called "Step 4" / "Step 4.2" / "Step 5" / "Step 7" in some places and "Section 4.2" / "Section 5" / "Section 7" in others. — E3-089, E5-082, E7-015, E7-020 vs E3-102, E2-142, E6-101.
12. **`general-purpose` both forbidden and required.** The precondition forbids ever falling back to `general-purpose` for a missing role; Section 6 requires `subagent_type=general-purpose` for the post-completion reviewer. Not a contradiction (different purposes) but the two rules read as opposed without the qualifier "as a substitute role". — E1-015, E1-029 vs E5-086.
13. **Mode 1 gate on a "single Epic in scope" run.** Branch 2 fires the continue-or-stop gate when "Section 2's mode prompt was skipped (only one Epic in scope at run start)", yet with one Epic in scope branch 2 (another workable Epic remains) is reachable only if Epics were added mid-run; the manifest literal `not captured (single Epic in scope)` then coexists with a fired continuation gate. — E3-094 vs E2-028, E2-037.
14. **Frontmatter typo.** `description` reads "described therin". — E1-002.
15. **Row 6 tracker append stated unconditionally in the routing section but carved out in 6.5.** The routing table says row 6 "appends a tracker entry per Section 6.5's Trigger C"; Trigger C exempts a finding whose only path is `trivial-tweak`. Consistent by reference, but a reader of the routing section alone would append on every row-6 dispatch. — E4-047 vs E6-063.

## Mirror candidates

Mechanisms whose rows are marked Mirror `yes` or `unknown` (i.e. candidates for a shared carrier with `/quo-fix-issue` and/or `/quo-breakdown-epic`), and the explicit divergences the E4 extractor recorded against `/quo-fix-issue` L618–L702.

**Marked `yes` (byte-identical or section-refs-only differences expected):**
- EX-PRE (E1-010..027: hard-fail, hives, contract keys) — the three orchestrators share the `Run /quo-setup first.` precondition.
- EX-EFF (E1-035..061) — the session-effort gate is shared; only the floor differs (`medium` here and in `/quo-fix-issue`; `high` in `/quo-breakdown-epic`).
- EX-MAN lead statements (E1-095, E1-097, E1-098, E1-099, E1-101..104, E1-111, E1-112, E1-114, E1-115, E1-117..120) — the `#### Write the run-state manifest` shared lead sentences; discriminator and Progress-shape rows are `no` by design.
- EX-GATE (all rows) — the two-step contract text.
- EX-ROUTE (E4-001..169 except the divergences below) — `### Orchestrator discipline: routing review findings`.
- EX-TRK definition/entry-shape rows (E6-007..039) — `#### Session-scoped compromise tracker`; trigger rows (E6-040..086) are `unknown`.
- EX-POST (E5-073..216) — `### 6. Post-Completion Review` mirrors `/quo-fix-issue` Section 8.
- EX-SUMM Accepted-compromises rows (E7-030, E7-047..065) and EX-SOE Bee-level rendering rows (E7-029, E7-034..046).
- EX-DEFER Section-5 rows (E5-052..058), EX-TL `-r<n>` / postcomp rows (E2-249..257), EX-DPS completeness-relay rows (E5-004..019), EX-SHELL (E1-117, E6-039, E6-121, E6-122, E6-136).

**Marked `unknown` (extractor could not compare; verify before assuming shared):** EX-LOOP, EX-PCR, EX-MOV, EX-UMG, EX-DPS fingerprint rows (E2-162..190), EX-ROLES, EX-PMD, EX-TL core rows, EX-SMW, EX-TEST, EX-CLEAN, EX-DHG (E6-087..151), EX-TRK triggers (E6-040..086), EX-ABORT (E3-214..246 partially), EX-ISO, EX-FINAL (E7-001, E7-002), EX-BEEREV trailer rows (E5-028..031, E5-036, E5-046..049).

**Explicit divergences from `/quo-fix-issue` recorded by the E4 extractor (and two from E6/E2):**
- Approved-design source: execute = Subtask body + Task body + PRD/SDD via `reference_materials` (or Plan Bee body); fix-issue = the `## Authoritative design directive` block from Section 3's Analyst gate. — E4-057.
- Blocker base pair at gate (c): execute = `Fix properly now` + `Cancel`; fix-issue = `Fix properly now` + `Re-dispatch the Analyst with this finding`. — E4-074.
- `Cancel` at gate (c): execute offers it in the blocker set; fix-issue has no `Cancel` at (c) at all (Analyst re-dispatch instead). — E4-077, E4-112, E4-114.
- Abort routing: execute → `##### Aborted-run close-out` (Section 4.2), then the Epic-boundary checkpoint; fix-issue → `#### Aborted-Issue close-out` (Section 7) with a deferral-hygiene gate. — E4-078, E4-145.
- `Cancel` semantics: execute has no Issue concept, abort always ends the run, never proceeds to the next Task; fix-issue's `Cancel` ends the current Issue and the close-out's mode branch decides the run (batch mode may advance). — E4-082, E4-144, E4-147.
- Analyst: execute has none, so `Cancel` carries the stop-and-re-plan answer at both gates. — E4-081, E4-129.
- Gate (d) non-deferrable blocker set: execute = per-path list + `Cancel`; fix-issue adds `Re-dispatch the Analyst with this finding`, marks it `(Recommended)` in the zero-path case, and withholds `(Recommended)` from the Analyst choice under blocker-Defer precedence. — E4-128, E4-130, E4-124.
- Filing-failure re-prompt: execute offers Cancel at either gate on a blocker; fix-issue offers Cancel at the routing gate only. — E4-158.
- Part (g) code-review rung: execute names the Bee-level Code Reviewer (Clause 2) or the per-Task PM's in-flight `/quo-engineer-review` pass (Clause 1); fix-issue names the Code Reviewer as the sole rung. — E4-164.
- Engineer-dispatch precondition: execute carries two clauses inline; fix-issue defers to Section 4's Reconcile-step precondition with `<issue-id>` prefixes and deliberately excludes the Code Reviewer from its list. — E4-170, E4-187.
- Defer-bullet precedent cross-reference points at `/quo-fix-issue` Section 1 (fix-issue cites its own Section 1). — E4-105.
- `hive_commit.py` resolution: execute resolves against its own base directory; fix-issue and breakdown-epic resolve it as a sibling. — E6-139.
- Manifest discriminator: execute/breakdown-epic append the Bee ID; fix-issue appends the repository directory basename. — E1-112.
