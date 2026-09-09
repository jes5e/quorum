# Rule inventory — quo-execute SKILL.md lines 1–227 (frontmatter, Overview, Preconditions, Section 1)

Source: `/Users/jesseg/code/quorum/skills/quo-execute/SKILL.md` L1–L227. Prefix `E1`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| E1-001 | Skill frontmatter `name` is `quo-execute`. | definition | L2 · frontmatter | - | - | - | none | no | procedure |
| E1-002 | Skill frontmatter `description` is `Proceed through each Epic in a Bee, doing the work described therin. Report questions and status back to caller.` | definition | L3 · frontmatter | - | - | - | none | no | procedure |
| E1-003 | Skill frontmatter `argument-hint` is `"[<bee-id> \| <epic-id>]"`. | definition | L4 · frontmatter | - | - | - | none | no | procedure |
| E1-004 | Overview step 1: find the Bee to work on and validate it is ready. | ordering | L9-L10 · ## Overview | - | - | - | bees | no | procedure |
| E1-005 | Overview step 2: find the best Epic; validate it is unblocked; validate its description still makes sense after reviewing prior Epics' work. | ordering | L11-L13 · ## Overview | - | - | - | bees | no | procedure |
| E1-006 | Overview step 3: form a Team to complete the Epic's work; send questions and clarification requests to the caller. | relay | L14-L15 · ## Overview | dispatches | - | - | Agent, AskUserQuestion | no | procedure |
| E1-007 | Create one git commit per Task that includes all changes for that Task. | invariant | L16 · ## Overview | git commit | - | - | git | no | procedure |
| E1-008 | Loop steps 2–3 until all Epics are done. | ordering | L17 · ## Overview | - | - | - | none | no | procedure |
| E1-009 | After all Epics done: disband execution Team, form Review Team, address Review findings, get User approval, mark Bee and children closed, output final summary — in that order. | ordering | L18-L23 · ## Overview | status flips, final summary | - | - | Agent, AskUserQuestion, bees | no | procedure |
| E1-010 | Before doing anything else, verify the host repo is configured for quorum. | precondition | L27 · ## Preconditions | - | - | - | none | yes | procedure |
| E1-011 | **Hard-fail** with message `Run /quo-setup first.` plus a one-line note about what is missing if any precondition is absent. | precondition | L27 · ## Preconditions | hard-fail message | precondition checks | `/quo-setup` | none | yes | procedure |
| E1-012 | Require seven registered custom subagent types: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`. | precondition | L29 · ## Preconditions | - | running session's registered subagents | - | Agent | unknown | procedure |
| E1-013 | Custom subagents load at Claude Code session start; a fresh install requires a restart or `/agents` hot-reload before dispatch works. | definition | L29 · ## Preconditions | - | - | `/agents` | Agent | yes | rationale |
| E1-014 | If any of the seven is missing at run-time, STOP at the precondition gate and emit the hard-fail message. | precondition | L29 · ## Preconditions | hard-fail message | E1-012 | - | Agent | unknown | procedure |
| E1-015 | Never fall back to `general-purpose`, never skip the dispatch, never improvise substitute roles when a required subagent is missing. | invariant | L29 · ## Preconditions | - | E1-014 | - | Agent | unknown | procedure |
| E1-016 | The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents`. | field-or-template | L29 · ## Preconditions | hard-fail message | - | `README.md` `## Install`, `/agents` | none | unknown | procedure |
| E1-017 | Example hard-fail text: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.` | example | L29 · ## Preconditions | hard-fail message | `<missing-list>` | `README.md` `## Install` | none | unknown | example |
| E1-018 | Require the Plans hive colonized: `bees list-hives` output must include a hive whose `normalized_name` is `plans`. | precondition | L30 · ## Preconditions | - | `bees list-hives` output | - | bees | yes | procedure |
| E1-019 | Require the Specs hive colonized: `bees list-hives` output must include a hive whose `normalized_name` is `specs`. | precondition | L31 · ## Preconditions | - | `bees list-hives` output | - | bees | yes | procedure |
| E1-020 | If Specs hive absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).` | field-or-template | L31 · ## Preconditions | hard-fail message | E1-019 | `/quo-setup` | none | yes | procedure |
| E1-021 | Require CLAUDE.md to contain a `## Documentation Locations` section. | precondition | L32 · ## Preconditions | - | target CLAUDE.md | `## Documentation Locations` | none | yes | procedure |
| E1-022 | Agents look up architecture-doc, customer-doc, and test-guide paths by exact key from `## Documentation Locations`. | definition | L32 · ## Preconditions | - | `## Documentation Locations` keys | - | none | yes | procedure |
| E1-023 | Require CLAUDE.md `## Build Commands` with all five bullet keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. | precondition | L33 · ## Preconditions | - | target CLAUDE.md | `## Build Commands` | none | yes | procedure |
| E1-024 | Agents look up build/test/format/lint commands by exact key from `## Build Commands`. | definition | L33 · ## Preconditions | - | `## Build Commands` keys | - | none | yes | procedure |
| E1-025 | Rationale: reading commands/doc paths from CLAUDE.md keeps the skill stack-neutral; auto-detection is unsafe on polyglot/monorepo/custom build systems. | rationale-only | L35 · ## Preconditions | - | - | - | none | yes | rationale |
| E1-026 | The `## Build Commands` section is required, not optional. | invariant | L35 · ## Preconditions | - | - | `## Build Commands` | none | yes | procedure |
| E1-027 | Do not recover from a missing precondition by improvising commands or guessing paths; fail fast and direct the user to `/quo-setup`. | invariant | L37 · ## Preconditions | - | - | `/quo-setup` | none | yes | procedure |
| E1-028 | Subagent-precondition verification rides on the first dispatch: an `Agent type '<name>' not found`-style Agent-tool error for any of the seven types is the trigger. | gate | L39 · **Verifying the subagents precondition.** | - | Agent tool error | - | Agent | unknown | procedure |
| E1-029 | On that error, STOP, emit the hard-fail message above, and exit — no `general-purpose` fallback, no skipped dispatch, no substitute role. | recovery | L39 · **Verifying the subagents precondition.** | hard-fail message, exit | E1-028 | - | Agent | unknown | procedure |
| E1-030 | Rationale: the gate matches session-load semantics and fires at the natural failure point, so token pressure or creativity cannot bypass it. | rationale-only | L39 · **Verifying the subagents precondition.** | - | - | `/agents` | none | unknown | rationale |
| E1-031 | Section 1 has three `AskUserQuestion` gates in this order: session-effort gate, Bee pick, worktree/isolation gate. | ordering | L43 · ### 1. Find Bee to work on and validate | - | - | `#### Check session reasoning effort`, `#### Pick the Bee`, `#### Validate isolation strategy` | AskUserQuestion | unknown | procedure |
| E1-032 | Every Section 1 gate fires through the two-step `TaskCreate` → `AskUserQuestion` contract: `TaskCreate` first, then `AskUserQuestion` in the same turn. | gate | L43 · ### 1. Find Bee to work on and validate | `gate-*` TaskList task | - | Section 3's TaskList naming convention gate-task entry | TaskList, AskUserQuestion | yes | procedure |
| E1-033 | The gate task is named `gate-askuserquestion-<short-suffix>` and names the gate it fronts. | name-class | L43 · ### 1. Find Bee to work on and validate | `gate-askuserquestion-<short-suffix>` task | - | Section 3 TaskList naming convention | TaskList | yes | procedure |
| E1-034 | Mark each `gate-*` task `completed` the moment `AskUserQuestion` returns and the answer is consumed. | ordering | L43 · ### 1. Find Bee to work on and validate | `gate-*` task → `completed` | AskUserQuestion result | - | TaskList, AskUserQuestion | yes | procedure |
| E1-035 | The session-effort gate is **conditional**; when it does not fire, **no `TaskCreate` fires for it either**. | invariant | L45 · ### 1. Find Bee to work on and validate | - | E1-053 | `#### Check session reasoning effort` | TaskList | yes | procedure |
| E1-036 | Run the session-effort check **first in this section**, ahead of the Bee-pick gate and Section 2's Epic-pick gate. | ordering | L49 · #### Check session reasoning effort | - | - | Section 2 | none | yes | procedure |
| E1-037 | Rationale: **Let me change it first** exits the run, so firing first means the user never re-answers a pick already made. | rationale-only | L49 · #### Check session reasoning effort | - | - | - | none | yes | rationale |
| E1-038 | This skill is tuned for an orchestrator session at **`medium`** reasoning effort or higher. | definition | L51 · #### Check session reasoning effort | - | - | - | none | yes | procedure |
| E1-039 | Subagents dispatched from `agents/*.md` have effort pinned in frontmatter and are **not** affected by the session setting. | definition | L51 · #### Check session reasoning effort | - | `agents/*.md` frontmatter | `agents/*.md` | Agent | yes | rationale |
| E1-040 | The check concerns the orchestrator seat plus role-file-less dispatches — notably Section 6's `general-purpose` post-completion review sweep, which inherits the session setting. | definition | L51 · #### Check session reasoning effort | - | - | Section 6 | Agent | no | rationale |
| E1-041 | The skill cannot change the session setting itself; it may only name the recommendation and let the user apply it. | invariant | L51 · #### Check session reasoning effort | - | - | - | none | yes | procedure |
| E1-042 | **Ordering is load-bearing.** Read the environment variable **first**, evaluate against the floor, and only then decide whether a gate fires. | ordering | L53 · #### Check session reasoning effort | - | `CLAUDE_EFFORT` | - | Bash | yes | procedure |
| E1-043 | Do NOT create the gate task before the comparison. | invariant | L53 · #### Check session reasoning effort | - | - | - | TaskList | yes | procedure |
| E1-044 | Rationale: a stranded `pending` `gate-*` task breaks yield-control; the contract's recovery re-fires the tool, producing a phantom prompt on a later run. | rationale-only | L53 · #### Check session reasoning effort | - | - | two-step contract recovery mechanism | TaskList | yes | rationale |
| E1-045 | **Step 1**: read the session's current effort with one literal command, no shell conditional; the comparison is reasoning, not shell logic. | command | L55 · #### Check session reasoning effort | - | - | - | Bash | yes | procedure |
| E1-046 | POSIX command is `printenv CLAUDE_EFFORT`. | command | L57-L60 · #### Check session reasoning effort | effort value | `CLAUDE_EFFORT` | - | Bash | yes | procedure |
| E1-047 | Windows PowerShell command is `Write-Output $env:CLAUDE_EFFORT`. | command | L62-L65 · #### Check session reasoning effort | effort value | `CLAUDE_EFFORT` | - | Bash | yes | procedure |
| E1-048 | `CLAUDE_EFFORT` reports the session's **current** effort and tracks mid-session changes (e.g. `/model`), not a launch-time flag. | definition | L67 · #### Check session reasoning effort | - | `CLAUDE_EFFORT` | `/model` | none | yes | rationale |
| E1-049 | If output is empty, exits non-zero, or is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat as unset. | recovery | L69 · #### Check session reasoning effort | - | E1-046 / E1-047 output | - | Bash | yes | procedure |
| E1-050 | When treated as unset, **skip this check entirely and continue to the next step, silently.** | recovery | L69 · #### Check session reasoning effort | - | E1-049 | - | none | yes | procedure |
| E1-051 | Rationale: a spurious prompt on every run is worse than a missed advisory. | rationale-only | L69 · #### Check session reasoning effort | - | - | - | none | yes | rationale |
| E1-052 | **Step 2**: the floor is `medium`; the ordering is `low` < `medium` < `high` < `xhigh` < `max`. | definition | L71 · #### Check session reasoning effort | - | effort value | - | none | yes | procedure |
| E1-053 | Compare against the floor, never for equality. | invariant | L71 · #### Check session reasoning effort | - | effort value | - | none | yes | procedure |
| E1-054 | Rationale: running hotter than the recommendation costs wall-clock not quality; interrupting is gate-fatigue noise. | rationale-only | L71 · #### Check session reasoning effort | - | - | - | none | yes | rationale |
| E1-055 | **At or above `medium`**: say nothing — no gate, no prompt, no output, **no `TaskCreate`**; continue to the next step. | gate | L73 · #### Check session reasoning effort | - | E1-052 | - | none | yes | procedure |
| E1-056 | **Strictly below `medium`**: fire the gate in step 3. | gate | L74 · #### Check session reasoning effort | - | E1-052 | - | TaskList, AskUserQuestion | yes | procedure |
| E1-057 | **Step 3** (this branch only): `TaskCreate` a `gate-askuserquestion-<short-suffix>` task naming this gate, then `AskUserQuestion` in the same turn. | gate | L76 · #### Check session reasoning effort | `gate-askuserquestion-<short-suffix>` task | E1-056 | two-step contract at top of Section 1 | TaskList, AskUserQuestion | yes | procedure |
| E1-058 | Substitute the value read in step 1 for `<current>` in the question text. | field-or-template | L76 · #### Check session reasoning effort | question text | E1-046 / E1-047 output | - | AskUserQuestion | yes | procedure |
| E1-059 | Question text verbatim: `This session is running at \`effort=<current>\`, below the \`medium\` floor this skill is tuned for. This skill delegates implementation rather than producing work itself, but it still owns ticket state, dispatch ordering, gate handling and the review loop.` + blank line + `Subagent effort is pinned per role and is NOT affected by this setting.` | field-or-template | L78-L85 · #### Check session reasoning effort | question text | `<current>` | - | AskUserQuestion | yes | procedure |
| E1-060 | Option 1 **Proceed anyway** — run at the current effort; mark the `gate-*` task `completed`; continue to the next step. | choice-set | L89 · #### Check session reasoning effort | `gate-*` → `completed` | user answer | - | TaskList, AskUserQuestion | yes | procedure |
| E1-061 | Option 2 **Let me change it first** — exit without dispatching anything; user runs `/model` then re-invokes; mark `gate-*` `completed`, then exit cleanly. | choice-set | L90 · #### Check session reasoning effort | `gate-*` → `completed`, clean exit | user answer | `/model` | TaskList, AskUserQuestion | yes | procedure |
| E1-062 | The user calls with no arguments, a Bee id, or an Epic ID; each has its own path. | definition | L94 · #### Pick the Bee | - | skill arguments | - | none | no | procedure |
| E1-063 | **If called without arguments**, list all Plan Bees in this repo and ask the user which one to work on. | gate | L96 · #### Pick the Bee | - | - | - | bees, AskUserQuestion | no | procedure |
| E1-064 | No-argument listing query is `bees execute-freeform-query --query-yaml 'stages:` / `  - [type=bee, hive=plans]` / `report: [title, ticket_status]'`. | command | L98-L102 · #### Pick the Bee | Bee list | - | - | bees | no | procedure |
| E1-065 | Filter the result to Bees with status `ready` or `in_progress` (those are workable). | precondition | L104 · #### Pick the Bee | workable-Bee list | E1-064 output | - | none | no | procedure |
| E1-066 | If exactly one workable Bee matches, use it without asking. | gate | L104 · #### Pick the Bee | Bee ID | E1-065 | - | none | no | procedure |
| E1-067 | If multiple workable Bees match, present them via `AskUserQuestion`. | gate | L104 · #### Pick the Bee | Bee ID | E1-065 | - | AskUserQuestion, TaskList | no | procedure |
| E1-068 | If none match, tell the user no Plan Bees are workable and suggest `/quo-plan` or `/quo-plan-from-specs`. | recovery | L104 · #### Pick the Bee | user message | E1-065 | `/quo-plan`, `/quo-plan-from-specs` | none | no | procedure |
| E1-069 | **If called with a Bee ID**, find that Bee's `ready` Epic children and ask which one to start with. | gate | L106 · #### Pick the Bee | - | `<bee-id>` | - | bees, AskUserQuestion | no | procedure |
| E1-070 | Bee-ID Epic query is `bees execute-freeform-query --query-yaml 'stages:` / `  - [parent=<bee-id>, type=t1, status=ready]` / `report: [title, up_dependencies]'`. | command | L108-L112 · #### Pick the Bee | Epic candidate list | `<bee-id>` | - | bees | no | procedure |
| E1-071 | `up_dependencies` is returned as a list of ticket IDs only — not statuses. | definition | L114 · #### Pick the Bee | - | E1-070 output | - | bees | no | procedure |
| E1-072 | Collect dependency IDs across all candidate Epics, then batch-look-up their statuses with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`. | command | L114-L119 · #### Pick the Bee | dependency statuses | `up_dependencies` IDs | - | bees | no | procedure |
| E1-073 | An Epic is workable only if all its `up_dependencies` have `ticket_status` `done`; a `ready` dependency is a pending blocker. | invariant | L121 · #### Pick the Bee | workable-Epic list | E1-072 output | - | none | no | procedure |
| E1-074 | An Epic with no `up_dependencies` is unblocked by default. | invariant | L121 · #### Pick the Bee | - | E1-070 output | - | none | no | procedure |
| E1-075 | Present unblocked candidate Epics via `AskUserQuestion` and recommend the one with the fewest downstream dependencies first. | gate | L121 · #### Pick the Bee | Epic choice | E1-073 / E1-074 | - | AskUserQuestion, TaskList | no | procedure |
| E1-076 | **If called with an Epic ID**, walk up to the parent Bee with `bees execute-freeform-query --query-yaml 'stages:` / `  - [id=<epic-id>]` / `  - [parent]` / `report: [title, ticket_status]'`. | command | L123-L130 · #### Pick the Bee | parent Bee | `<epic-id>` | - | bees | no | procedure |
| E1-077 | Use the parent Bee for the rest of the run. | ordering | L132 · #### Pick the Bee | Bee ID | E1-076 output | - | none | no | procedure |
| E1-078 | Every path yields the Bee ID to work on; validate it is ready for work. | precondition | L134-L135 · #### Pick the Bee | validated Bee ID | Bee ID | - | bees | no | procedure |
| E1-079 | The Bee must have status `ready` or `in_progress`. | precondition | L136 · #### Pick the Bee | - | Bee `ticket_status` | - | bees | no | procedure |
| E1-080 | If the Bee has `up_dependencies`, they must be in `done` state; a `ready` dependency is a pending blocker, not satisfied. | precondition | L137 · #### Pick the Bee | - | Bee `up_dependencies` statuses | - | bees | no | procedure |
| E1-081 | Check whether you are running in an isolated context for this Bee's work; the text names three scenarios (only A and B are defined in this slice). | precondition | L141 · #### Validate isolation strategy | - | cwd, git state | - | git | unknown | procedure |
| E1-082 | **Scenario A — Already in a worktree**: directory name matches the Bee (e.g. `b_Wx7` for `b.Wx7`); proceed directly, no action needed. | gate | L143 · #### Validate isolation strategy | isolation = worktree | cwd name, Bee ID | `/bees-worktree-add`, `/bees-fleet` | git | unknown | procedure |
| E1-083 | Scenario A is the expected path when launched via the optional worktree skills `/bees-worktree-add` / `/bees-fleet`, if installed. | definition | L143 · #### Validate isolation strategy | - | - | `/bees-worktree-add`, `/bees-fleet` | none | unknown | rationale |
| E1-084 | **Scenario B — On an existing branch in the main repo** (user invoked `/quo-execute` directly): present an `AskUserQuestion` with the three options below. | gate | L145 · #### Validate isolation strategy | `gate-*` task, isolation choice | cwd, branch | `/quo-execute` | AskUserQuestion, TaskList, git | unknown | procedure |
| E1-085 | Option 1 **Create a feature branch (Recommended)** — create a new branch (e.g. `bee/b.Wx7`) from current HEAD and do all work there. | choice-set | L147 · #### Validate isolation strategy | git branch | user answer | - | git | unknown | procedure |
| E1-086 | Rationale for option 1: keeps main clean; user can review, squash-merge, or discard later. | rationale-only | L147 · #### Validate isolation strategy | - | - | - | none | unknown | rationale |
| E1-087 | Under option 1, at the end instruct the user to merge the branch or open a PR. | relay | L147 · #### Validate isolation strategy | user message | E1-085 | - | none | unknown | procedure |
| E1-088 | Option 2 **Work on current branch** — commit directly to the checked-out branch and tell the user the branch name. | choice-set | L148 · #### Validate isolation strategy | isolation = current branch | user answer, branch name | - | git | unknown | procedure |
| E1-089 | Option 2 is appropriate when the user is already on a feature branch or intentionally wants commits on main. | rationale-only | L148 · #### Validate isolation strategy | - | - | - | none | unknown | rationale |
| E1-090 | Option 3 **Set up a worktree instead** — if `/bees-worktree-add` is installed, suggest the user run it to create an isolated worktree and spawn an async agent. | choice-set | L149 · #### Validate isolation strategy | user advice | user answer | `/bees-worktree-add` | none | unknown | procedure |
| E1-091 | Under option 3, exit after giving this advice — do not proceed with work. | ordering | L149 · #### Validate isolation strategy | clean exit | E1-090 | - | none | unknown | procedure |
| E1-092 | Omit option 3 if `/bees-worktree-add` is not installed (it is not part of the portable core). | choice-set | L149 · #### Validate isolation strategy | - | installed-skill check | `/bees-worktree-add` | none | unknown | procedure |
| E1-093 | Option 3 is the right choice for fire-and-forget execution in a separate tmux session. | rationale-only | L149 · #### Validate isolation strategy | - | - | - | none | unknown | rationale |
| E1-094 | In the Scenario B question, always state the current working directory, the current branch name, and that option 1 creates a local branch only (no remote push). | field-or-template | L151-L154 · #### Validate isolation strategy | question text | cwd, branch name | - | AskUserQuestion, git | unknown | procedure |
| E1-095 | `#### Write the run-state manifest` is the **canonical definition site** for the run-state manifest; later sections refer to it by name. | definition | L158 · #### Write the run-state manifest | - | - | - | none | yes | procedure |
| E1-096 | Write the manifest as the last step of Section 1, once Bee ID and isolation strategy are both known and before any Epic work begins. | ordering | L158 · #### Write the run-state manifest | manifest file | Bee ID, isolation strategy | Section 1 | none | unknown | procedure |
| E1-097 | The manifest holds only run-scoped values that live **nowhere else on disk**; bees holds ticket state, git the diff, the compromise tracker compromises, the `defer-*` TaskList deferrals. | invariant | L160 · #### Write the run-state manifest | - | - | `defer-*` TaskList | none | yes | procedure |
| E1-098 | After a compaction the orchestrator re-reads the manifest instead of trusting a summary. | recovery | L160 · #### Write the run-state manifest | - | manifest file | - | none | yes | procedure |
| E1-099 | Write the manifest under `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows) per the scratch-file convention. | name-class | L162 · **Path and filename.** | manifest path | - | scratch-file convention | none | yes | procedure |
| E1-100 | Canonical filename is `run-state-quo-execute-<bee-id>.md`, where `<bee-id>` is the **Bee ID** for this run (e.g. `run-state-quo-execute-b.abc.md`). | name-class | L162 · **Path and filename.** | manifest path | Bee ID | - | none | no | procedure |
| E1-101 | Create the `.quorum` directory if it does not already exist, then author the manifest via the `Write` tool (no shell redirect). | command | L162 · **Path and filename.** | `.quorum` dir, manifest file | - | - | Bash | yes | procedure |
| E1-102 | POSIX directory command is `mkdir -p /tmp/.quorum`; then write to `/tmp/.quorum/run-state-quo-execute-<bee-id>.md` via the Write tool. | command | L164-L168 · **Path and filename.** | `.quorum` dir | - | - | Bash | yes | procedure |
| E1-103 | PowerShell directory command is `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`; then write to `$env:TEMP\.quorum\run-state-quo-execute-<bee-id>.md` via the Write tool. | command | L170-L174 · **Path and filename.** | `.quorum` dir | - | - | Bash | yes | procedure |
| E1-104 | **The filename is deterministic — do NOT add a random suffix or timestamp.** | invariant | L176 · #### Write the run-state manifest | - | - | - | none | yes | procedure |
| E1-105 | Rationale: the compromise tracker's `<short-suffix>` suits a reader handed the path in a prompt; the manifest's reader is the post-compaction orchestrator, so a suffix is unfindable. | rationale-only | L176 · #### Write the run-state manifest | - | - | compromise tracker | none | yes | rationale |
| E1-106 | The Bee ID is **re-derivable without the conversation**: it is the run's argument, `parent` of every Epic, and grandparent of every Task. | definition | L178 · **Why the key is this skill's name plus the Bee ID.** | - | - | - | none | no | rationale |
| E1-107 | An orchestrator that lost the conversation recovers the Bee ID from any in-flight Plans-hive ticket with one `bees show-ticket` / `bees execute-freeform-query` call. | recovery | L178 · **Why the key is this skill's name plus the Bee ID.** | Bee ID | in-flight Plans ticket | - | bees | no | procedure |
| E1-108 | The Bee ID is **discriminating across projects**: ticket IDs are minted per bees workspace, so different projects do not normally share a filename in `<tempdir>/.quorum/`. | rationale-only | L178 · **Why the key is this skill's name plus the Bee ID.** | - | - | - | none | no | rationale |
| E1-109 | The **`quo-execute` segment is what discriminates across sibling skills**; `/quo-breakdown-epic` keys its manifest on the same Bee ID (Bee-ID-first resolution order). | definition | L180 · #### Write the run-state manifest | - | - | `/quo-breakdown-epic` | none | no | rationale |
| E1-110 | Without the skill-name segment, a `/quo-execute` run would truncate a live `/quo-breakdown-epic` session's manifest — the sequence its *"In a fresh session, execute this Epic first; defer downstream breakdown"* option invites. | rationale-only | L180 · #### Write the run-state manifest | - | - | `/quo-breakdown-epic` menu option *"In a fresh session, execute this Epic first; defer downstream breakdown"* | none | no | rationale |
| E1-111 | Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends. | invariant | L180 · #### Write the run-state manifest | - | - | `/quo-execute`, `/quo-breakdown-epic`, `/quo-fix-issue` | none | yes | procedure |
| E1-112 | `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID; `/quo-fix-issue` appends the repository directory basename because batch membership is only recoverable from inside the manifest. | definition | L180 · #### Write the run-state manifest | - | - | `/quo-fix-issue`, each skill's own manifest section | none | yes | rationale |
| E1-113 | Accepted trade: two concurrent `/quo-execute` runs against the same Bee already collide over ticket statuses and commits, so that case is unsupported. | rationale-only | L182 · #### Write the run-state manifest | - | - | scratch-file convention collision-resistance guidance | none | no | rationale |
| E1-114 | **Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. | invariant | L184 · #### Write the run-state manifest | - | - | - | none | yes | procedure |
| E1-115 | Write the manifest fresh at run start, overwriting any manifest left by a previous `/quo-execute` run against the same Bee. | ordering | L184 · #### Write the run-state manifest | manifest file | - | - | none | yes | procedure |
| E1-116 | Rewrite the manifest in full at each Epic boundary per Section 4.2's Epic-boundary state-externalization checkpoint. | ordering | L184 · #### Write the run-state manifest | manifest rewrite | - | Section 4.2 Epic-boundary state-externalization checkpoint | none | no | procedure |
| E1-117 | Never delete the manifest; do NOT instruct any `rm` / `Remove-Item` (scratch-file convention forbids cleanup). | invariant | L184 · #### Write the run-state manifest | - | - | scratch-file convention | none | yes | procedure |
| E1-118 | The manifest carries **only values that have no other durable home.** | invariant | L186 · **Contents — and an invariant that bounds them.** | - | - | - | none | yes | procedure |
| E1-119 | Do not add ticket titles, Subtask bodies, review findings, or anything already readable from bees, git, the tracker, or the TaskList. | invariant | L186 · **Contents — and an invariant that bounds them.** | - | - | - | none | yes | procedure |
| E1-120 | Rationale: duplicating carried values would grow the manifest into a shadow ticket store that drifts. | rationale-only | L186 · **Contents — and an invariant that bounds them.** | - | - | - | none | yes | rationale |
| E1-121 | Manifest title line is `# Run state — quo-execute @ <bee-id>`. | field-or-template | L189 · manifest template | manifest heading | Bee ID | - | none | no | procedure |
| E1-122 | Manifest field `**Skill:**` is fixed to `quo-execute`. | field-or-template | L191 · manifest template | `Skill` field | - | - | none | no | procedure |
| E1-123 | Manifest field `**Run started (UTC):**` holds `<YYYY-MM-DDTHH:MM:SSZ>`. | field-or-template | L192 · manifest template | `Run started (UTC)` field | clock | - | none | unknown | procedure |
| E1-124 | Manifest field `**Unit scope:**` holds `Bee <bee-id>; Epics in scope: <epic-id-1, epic-id-2, ... \| pending Section 2 query>`. | field-or-template | L193 · manifest template | `Unit scope` field | Bee ID, Section 2 Epic query | Section 2 | none | no | procedure |
| E1-125 | Manifest field `**Multi-Epic run mode:**` enum: `Mode 1 (Stop after each Epic)` \| `Mode 2 (Work through all Epics)` \| `not captured (single Epic in scope)` \| `not captured (all Epics already done)` \| `not captured`. | field-or-template | L194 · manifest template | `Multi-Epic run mode` field | Section 2 mode gate | Section 2 | none | no | procedure |
| E1-126 | Manifest field `**Isolation strategy:**` enum: `branch created: <name>` \| `current branch: <name>` \| `worktree: <path>`. | field-or-template | L195 · manifest template | `Isolation strategy` field | E1-082 / E1-085 / E1-088 | `#### Validate isolation strategy` | none | unknown | procedure |
| E1-127 | Manifest field `**Pre-Bee SHA:**` holds `<pre-bee-sha>`. | field-or-template | L196 · manifest template | `Pre-Bee SHA` field | E1-134 | - | git | no | procedure |
| E1-128 | Manifest field `**Compromise tracker:**` holds `<tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`. | field-or-template | L197 · manifest template | `Compromise tracker` field | E1-135 | Section 6.5 `#### Session-scoped compromise tracker` | none | unknown | procedure |
| E1-129 | Manifest field `**Progress:**` holds one bullet per unit in the shape `<epic-id>: done — last commit <sha>`. | field-or-template | L198-L199 · manifest template | `Progress` field | Epic boundary | - | git | no | procedure |
| E1-130 | Manifest field `**Next unit:**` holds `<next-epic-id \| none>`. | field-or-template | L200 · manifest template | `Next unit` field | Section 2 Epic order | - | none | no | procedure |
| E1-131 | Bare `not captured` (run mode) and `pending Section 2 query` (Epics in scope) are **first-write-only** literals used only by the run-start write. | definition | L203 · #### Write the run-state manifest | - | - | Section 2 | none | no | procedure |
| E1-132 | Section 2's unconditional rewrite replaces those two first-write literals. | ordering | L203 · #### Write the run-state manifest | manifest rewrite | E1-131 | Section 2 | none | no | procedure |
| E1-133 | The first-write literals must never survive past Section 2. | invariant | L203 · #### Write the run-state manifest | - | E1-131 | Section 2 | none | no | procedure |
| E1-134 | Capture `<pre-bee-sha>` here at run start with one literal command; this is the **only** place the run records it. | command | L205 · #### Write the run-state manifest | `Pre-Bee SHA` value | HEAD | - | git | unknown | procedure |
| E1-135 | Section 6's post-completion review reads `<pre-bee-sha>` back from the manifest file. | definition | L205 · #### Write the run-state manifest | - | `Pre-Bee SHA` field | Section 6 | none | no | procedure |
| E1-136 | Pre-Bee SHA command on both POSIX and PowerShell is `git rev-parse HEAD`. | command | L207-L215 · #### Write the run-state manifest | SHA | HEAD | - | git | unknown | procedure |
| E1-137 | The **compromise tracker** field records the tracker's full path *including* its random `<short-suffix>`. | field-or-template | L217 · #### Write the run-state manifest | `Compromise tracker` field | tracker filename | - | none | unknown | procedure |
| E1-138 | Generate the tracker filename here at run start per Section 6.5 `#### Session-scoped compromise tracker`; timestamp and suffix are generated once per run. | ordering | L217 · #### Write the run-state manifest | tracker path | - | Section 6.5 `#### Session-scoped compromise tracker` | none | unknown | procedure |
| E1-139 | The tracker file itself is not created until its first append trigger fires; recording the path does not create it. | definition | L217 · #### Write the run-state manifest | - | - | Section 6.5 | none | unknown | procedure |
| E1-140 | Rationale: the manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. | rationale-only | L217 · #### Write the run-state manifest | - | - | - | none | unknown | rationale |
| E1-141 | **Progress** carries one line per unit this run has finished with, in the order worked; normal shape is `<epic-id>: done — last commit <sha>`. | field-or-template | L219 · #### Write the run-state manifest | `Progress` entries | Epic completion | - | git | no | procedure |
| E1-142 | Two **aborted** Progress shapes exist, both written by Section 4.2's `##### Aborted-run close-out` through the Epic-boundary checkpoint's step 2. | definition | L219 · #### Write the run-state manifest | `Progress` entries | close-out step 2 | Section 4.2 `##### Aborted-run close-out`, Epic-boundary checkpoint step 2 | none | no | procedure |
| E1-143 | Which aborted shape applies depends on **the scope that close-out's step 2 resolved**: the aborted lane's scope, or the review site the routing gate's `Cancel` fired from. | ordering | L219 · #### Write the run-state manifest | - | close-out step 2 scope | routing gate `Cancel` | none | no | procedure |
| E1-144 | **Mid-Epic abort** (per-Task writer lane, or `Cancel` at the per-Task review site) writes `<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`, replacing the `done` entry the Epic never earned. | field-or-template | L221 · #### Write the run-state manifest | `Progress` entry | task id, last commit | per-Task review site | git | no | procedure |
| E1-145 | **Bee-level-review abort** (Section 5 Bee-scoped re-dispatch, or `Cancel` at Section 5's Bee-level review) writes `<bee-id>: Bee-level review aborted — <what stopped it>`. | field-or-template | L222 · #### Write the run-state manifest | `Progress` entry | Bee ID | Section 5 Bee-level review | none | no | procedure |
| E1-146 | `<what stopped it>` names the aborted lane (e.g. `test-writer-b.abc`) when a lane aborted, or on the `Cancel` route the review site plus the finding the gate fired on (same pair close-out step 3 states). | field-or-template | L222 · #### Write the run-state manifest | `Progress` entry | lane name or review site + finding | close-out step 3 | none | no | procedure |
| E1-147 | The Bee-level shape keys on the **Bee** id because every Epic finished and each `done — last commit <sha>` entry is correct and stays untouched. | rationale-only | L222 · #### Write the run-state manifest | - | - | - | none | no | rationale |
| E1-148 | Do **not** overwrite a `done` Epic entry with an aborted one on the Bee-level-review-abort path. | invariant | L222 · #### Write the run-state manifest | - | E1-145 | - | none | no | procedure |
| E1-149 | Progress is an **in-run, pre-compaction** record, not cross-session: a resuming `/quo-execute <bee-id>` truncates the manifest at run start. | definition | L224 · #### Write the run-state manifest | - | E1-114 | - | none | no | procedure |
| E1-150 | Readers of a Progress entry are this run's later Epic boundaries — checkpoint step 1 resolves `<previous-epic-last-commit>` from it — and a post-compaction orchestrator inside this run. | definition | L224 · #### Write the run-state manifest | - | `Progress` field | Epic-boundary checkpoint step 1, `<previous-epic-last-commit>` | none | no | procedure |
| E1-151 | A later session learns where an aborted run stopped from bees and git, not the manifest. | recovery | L224 · #### Write the run-state manifest | - | bees, git | - | bees, git | no | procedure |
| E1-152 | Multi-Epic run mode and Epics in scope are unknown at this point; write `not captured` and `pending Section 2 query` respectively on the first write. | field-or-template | L226 · #### Write the run-state manifest | first-write placeholders | - | Section 2 Epic query and mode gate | none | no | procedure |
| E1-153 | Section 2 resolves both placeholders in a single unconditional rewrite once its Epic query has returned, on **every** path including those where the mode gate never fires. | ordering | L226 · #### Write the run-state manifest | manifest rewrite | Section 2 Epic query | Section 2 `#### Resolve the manifest placeholders` | none | no | procedure |
| E1-154 | Rationale: the run mode is a user choice with no re-derivation path; if lost, the run cannot know whether to auto-continue. | rationale-only | L226 · #### Write the run-state manifest | - | - | - | none | no | rationale |

## Anchors defined here

- L7 `## Overview`
- L25 `## Preconditions`
- L27 **Hard-fail**
- L39 **Verifying the subagents precondition.**
- L41 `### 1. Find Bee to work on and validate`
- L45 **conditional**
- L45 **no `TaskCreate` fires for it either**
- L47 `#### Check session reasoning effort`
- L49 **first in this section**
- L49 **Let me change it first**
- L51 **`medium`**
- L51 **not**
- L53 **Ordering is load-bearing.**
- L53 **first**
- L55 **Step 1 — read the session's current effort.**
- L67 **current**
- L69 **skip this check entirely and continue to the next step, silently.**
- L71 **Step 2 — compare against this skill's floor, which is `medium`.**
- L73 **At or above `medium`**
- L73 **no `TaskCreate`**
- L74 **Strictly below `medium`**
- L76 **Step 3 — fire the gate (this branch only).**
- L89 **Proceed anyway**
- L90 **Let me change it first**
- L92 `#### Pick the Bee`
- L96 **If called without arguments**
- L106 **If called with a Bee ID**
- L123 **If called with an Epic ID**
- L139 `#### Validate isolation strategy`
- L143 **Scenario A — Already in a worktree.**
- L145 **Scenario B — On an existing branch in the main repo.**
- L147 **Create a feature branch (Recommended)**
- L148 **Work on current branch**
- L149 **Set up a worktree instead**
- L156 `#### Write the run-state manifest`
- L158 **canonical definition site**
- L160 **nowhere else on disk**
- L162 **Path and filename.**
- L162 **Bee ID**
- L176 **The filename is deterministic — do NOT add a random suffix or timestamp.**
- L178 **Why the key is this skill's name plus the Bee ID.**
- L178 **re-derivable without the conversation**
- L178 **discriminating across projects**
- L180 **`quo-execute` segment is what discriminates across sibling skills**
- L184 **Semantics: truncate at run start, rewrite at each boundary.**
- L184 **live snapshot, not an accumulating log**
- L186 **Contents — and an invariant that bounds them.**
- L186 **only values that have no other durable home.**
- L191 **Skill:**
- L192 **Run started (UTC):**
- L193 **Unit scope:**
- L194 **Multi-Epic run mode:**
- L195 **Isolation strategy:**
- L196 **Pre-Bee SHA:**
- L197 **Compromise tracker:**
- L198 **Progress:**
- L200 **Next unit:**
- L203 **first-write-only**
- L205 **only**
- L217 **compromise tracker**
- L219 **Progress**
- L219 **aborted**
- L219 **the scope that close-out's step 2 resolved**
- L221 **Mid-Epic abort**
- L222 **Bee-level-review abort**
- L222 **Bee**
- L222 **not**
- L224 **in-run, pre-compaction**
- L226 **multi-Epic run mode**
- L226 **Epics in scope**
- L226 **every**

## Rationale-only spans

- L35 (1 line) — why CLAUDE.md-driven commands, not auto-detection
- L178 (1 line) — why Bee ID keys manifest
- L182 (1 line) — accepted concurrent-run collision trade-off

Total rationale-only lines: 3. (Many other lines mix a rule with a trailing rationale clause; those clauses are captured as `rationale-only` rows rather than as spans.)
