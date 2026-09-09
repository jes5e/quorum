# Rule inventory — `skills/quo-execute/SKILL.md` L894–L1115 (Section 5 and Section 6)

Site key: `§5` = heading `### 5. Final Bee-level Code, Doc and Eng reviews` (L894); `§6` = heading `### 6. Post-Completion Review` (L931). Sub-anchors (bolded lead phrases, numbered steps, PHASE blocks) are named after the `·`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| E5-001 | Once all Epics in the Bee are `done`, dispatch three concurrent ephemeral reviewer Agents, one per reviewer role, per Section 3's dispatch shape. | ordering | L896 · §5 | 3 Agent dispatches | Epic statuses (all `done`) | Section 3 | Agent, TaskList | no | procedure |
| E5-002 | Use exactly `Agent(subagent_type="code-reviewer", run_in_background=true)`, `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`. | command | L896 · §5 | 3 Agent dispatches | - | - | Agent | no | procedure |
| E5-003 | Track each reviewer via a TaskList task in the bee-scoped form `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`. | name-class | L896 · §5 | 3 TaskList tasks | Section 3 naming convention | Section 3 | TaskList | no | procedure |
| E5-004 | The Code Reviewer dispatch prompt MUST relay the Engineers' completeness evidence verbatim, widened to Bee scope from Section 3's per-Task PM dispatch rule. | relay | L898 · §5 · **The Code Reviewer dispatch prompt must relay the Engineers' completeness evidence verbatim.** | prompt content | Engineer returns carrying a **completeness check with evidence** | Section 3, "Per-Task PM dispatch" | Agent | yes | procedure |
| E5-005 | Embed every completeness list verbatim under a heading labelled `## Engineer's completeness evidence`, attributing each list to its Subtask. | field-or-template | L898 · §5 | `## Engineer's completeness evidence` prompt heading | Engineer completeness lists | - | Agent | yes | procedure |
| E5-006 | Embed the same lists verbatim in any `pm-<bee-id>` re-dispatch prompt under the same heading. | relay | L898 · §5 | PM prompt content | Engineer completeness lists | `agents/pm.md` | Agent | unknown | procedure |
| E5-007 | Embed the lists as text in the prompt; do NOT write them to a scratch file and pass a path. | invariant | L898 · §5 | - | - | - | Agent | yes | procedure |
| E5-008 | A completeness list is defined as: the search patterns run, every hit, and per hit either the change made or the reason it is deliberately untouched. | definition | L898 · §5 | - | - | - | none | yes | procedure |
| E5-009 | The evidence has no other carrier once the Engineer Agent exits, and `/quo-engineer-review`'s sweep-verification check needs it to verify against. | rationale-only | L898 · §5 | - | - | `/quo-engineer-review` | none | yes | rationale |
| E5-010 | Separately from the lists, state in the prompt that the assignment was sweep-shaped whenever it was, list or no list. | relay | L898 · §5 | prompt statement `sweep-shaped` | Subtask body / directive shape | `/quo-engineer-review` | Agent | yes | procedure |
| E5-011 | "Sweep-shaped" means a directive or Subtask body that directed a change at every site where some property holds. | definition | L898 · §5 | - | - | - | none | yes | procedure |
| E5-012 | `/quo-engineer-review` reports a missing list only when the invocation named the assignment sweep-shaped, so an unnamed sweep silently loses the check. | rationale-only | L898 · §5 | - | - | `/quo-engineer-review` | none | yes | rationale |
| E5-013 | At Bee scope, name every sweep-shaped Subtask assignment from the Epic loop in the prompt. | relay | L898 · §5 | prompt content | Epic-loop Subtask bodies | - | Agent | no | procedure |
| E5-014 | State `sweep-shaped` on its own only when the list is actually in hand or the Engineer genuinely returned none. | invariant | L898 · §5 · **One post-compaction qualification applies at this Bee-level relay only:** | - | Engineer return readability | - | none | no | procedure |
| E5-015 | When a sweep-shaped Task's Engineer return is unreadable post-compaction, state that a completeness list **existed but is unavailable post-compaction**, naming the Subtask. | relay | L898 · §5 | prompt statement | compaction state | - | Agent | no | procedure |
| E5-016 | Section 3's per-Task PM dispatch needs no post-compaction qualification because it composes its prompt while the Engineer's return is in hand. | rationale-only | L898 · §5 | - | - | Section 3 | none | no | rationale |
| E5-017 | `agents/code-reviewer.md` carries the Code-Reviewer-side half: passing the list into its `/quo-engineer-review` invocation. | definition | L898 · §5 | - | - | `agents/code-reviewer.md`, `/quo-engineer-review` | none | yes | procedure |
| E5-018 | The Bee-scoped PM needs its own copy of the list because `agents/pm.md` drives `/quo-engineer-review` via the `Skill` tool; relaying to the Code Reviewer does not cover it. | relay | L898 · §5 · **The Bee-scoped PM needs its own copy:** | PM prompt content | - | `agents/pm.md`, `/quo-engineer-review` | Agent | unknown | procedure |
| E5-019 | When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one. | invariant | L898 · §5 | - | absence of lists | - | Agent | yes | procedure |
| E5-020 | Only dispatch a reviewer whose corresponding implementer was used during the Epic loop. | precondition | L900 · §5 · Conditional spawn | - | Epic-loop dispatch history | - | Agent | no | procedure |
| E5-021 | If Engineer Agents were dispatched during the Epic loop, dispatch the code-reviewer Agent now. | precondition | L901 · §5 | code-reviewer dispatch | Engineer dispatch history | - | Agent | no | procedure |
| E5-022 | If Test Writer Agents were dispatched during the Epic loop, dispatch the test-reviewer Agent now. | precondition | L902 · §5 | test-reviewer dispatch | Test Writer dispatch history | - | Agent | no | procedure |
| E5-023 | If Doc Writer Agents were dispatched during the Epic loop, dispatch the doc-reviewer Agent now. | precondition | L903 · §5 | doc-reviewer dispatch | Doc Writer dispatch history | - | Agent | no | procedure |
| E5-024 | Reviewer role contracts live in the role files; the orchestrator dispatches and does not carry the role's prose. | invariant | L905 · §5 | - | role files | - | none | unknown | procedure |
| E5-025 | **Code Reviewer** (`agents/code-reviewer.md`) reviews the Engineer's output and surfaces gaps against engineering standards. | definition | L907 · §5 | - | - | `agents/code-reviewer.md` | none | unknown | procedure |
| E5-026 | **Test Reviewer** (`agents/test-reviewer.md`) reviews the Test Writer's output and surfaces gaps against test-quality standards. | definition | L908 · §5 | - | - | `agents/test-reviewer.md` | none | unknown | procedure |
| E5-027 | **Doc Reviewer** (`agents/doc-reviewer.md`) reviews the Doc Writer's output and surfaces gaps against documentation standards. | definition | L909 · §5 | - | - | `agents/doc-reviewer.md` | none | unknown | procedure |
| E5-028 | Get the reviewer feedback and make a judgement call about whether that work must be done. | gate | L911 · §5 | disposition decision | reviewer returns | - | none | unknown | procedure |
| E5-029 | Each of `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` emits a routing trailer `**Your next tool use MUST address these findings now.**` or `**Your next tool use MUST advance the workflow.**` plus a counter-anchor clause. | definition | L911 · §5 | - | reviewer output | `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` | none | unknown | procedure |
| E5-030 | **Follow the trailer literally** — it is the authoritative routing prescription for this step. | invariant | L911 · §5 | routing | routing trailer | - | none | unknown | procedure |
| E5-031 | The prose below the trailer rule is reference context, not a load-bearing rule the orchestrator must recall from memory. | rationale-only | L911 · §5 | - | - | - | none | unknown | rationale |
| E5-032 | If feedback requires action, dispatch fresh ephemeral implementer Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer / PM as needed). | command | L912 · §5 | implementer dispatches | routing trailer | Section 3 | Agent | no | procedure |
| E5-033 | Track each re-dispatch under the Bee-scoped names `engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>`. | name-class | L912 · §5 | TaskList tasks | Section 3 naming convention | Section 3 | TaskList | no | procedure |
| E5-034 | Append the `-r<n>` round discriminator on every dispatch after the first (e.g. `engineer-<bee-id>-r1`), including a second Bee-level code review `code-reviewer-<bee-id>-r1`. | name-class | L912 · §5 | TaskList tasks | round count | Section 3 | TaskList | no | procedure |
| E5-035 | Bee-level findings span the whole Bee's diff and never borrow a Subtask-scoped or Task-scoped name. | invariant | L912 · §5 | - | - | - | TaskList | no | procedure |
| E5-036 | Stay in delegate mode during Bee-level re-dispatch. | invariant | L912 · §5 | - | - | - | Agent | unknown | procedure |
| E5-037 | When a finding's chosen fix path changes source, re-dispatches are ordered, not concurrent: Engineer, then Code Reviewer, then the affected writer. | ordering | L912 · §5 · **When a finding's chosen fix path changes source, these re-dispatches are ordered, not concurrent** | dispatch sequence | fix-path kind | part (g) of `### Orchestrator discipline: routing review findings` | Agent, TaskList | unknown | procedure |
| E5-038 | Findings routed from Section 5 take part (g)'s precondition **Clause 2 (Bee-level)**, which scopes to the whole Bee and enumerates exactly the `-<bee-id>` prefixes. | precondition | L912 · §5 | - | active TaskList set | part (g), **Clause 2 (Bee-level)** | TaskList | no | procedure |
| E5-039 | The Bee-level Code Reviewer relays `/quo-engineer-review`'s `### Second-order effects` subsection verbatim on every return, clean ones included. | definition | L913 · §5 · **Second-order effects have a destination.** | - | reviewer return | `agents/code-reviewer.md`, `/quo-engineer-review` | none | unknown | procedure |
| E5-040 | A Bee-scoped PM re-dispatched here relays `### Second-order effects` into its Final report. | definition | L913 · §5 | - | - | `agents/pm.md` | none | unknown | procedure |
| E5-041 | Second-order effects are narrative, not routing input; they do not by themselves require a re-dispatch because anything actionable is already a numbered finding. | invariant | L913 · §5 | - | - | - | none | unknown | procedure |
| E5-042 | Render the relayed second-order effects into the `**Second-order effects**` field of the `## Bee Execution Complete` summary (Section 9's template). | relay | L913 · §5 | `**Second-order effects**` summary field | Code Reviewer / PM return | Section 9, `## Bee Execution Complete` | none | no | procedure |
| E5-043 | Do NOT route Bee-level second-order effects into Section 4.1's per-Task field. | invariant | L913 · §5 | - | - | Section 4.1 | none | no | procedure |
| E5-044 | Section 4.1's per-Task field belongs to the per-Task PM's narrative and was already printed as each Task closed, so a Bee-level effect sent there lands in already-emitted output. | rationale-only | L913 · §5 | - | - | Section 4.1 | none | no | rationale |
| E5-045 | Do not let second-order effects terminate in this conversation. | invariant | L913 · §5 | - | - | - | none | unknown | procedure |
| E5-046 | **IMPORTANT** Stay in delegate mode and do not do the work yourself. | invariant | L914 · §5 | - | - | - | Agent | unknown | procedure |
| E5-047 | If the feedback was minor enough, the orchestrator may choose to **NOT** spawn the Product Manager on this iteration. | precondition | L915 · §5 | - | feedback severity | - | Agent | unknown | procedure |
| E5-048 | If feedback does not require action, move on to Final Review but MUST share the ignored feedback for review. | relay | L916 · §5 | Final Review content | ignored findings | Final Review | none | unknown | procedure |
| E5-049 | Feedback may be ignored (to avoid an infinite loop) so long as it is presented in Final Review. | invariant | L917 · §5 | - | - | Final Review | none | unknown | procedure |
| E5-050 | A reviewer return whose findings are all `nit`s with `trivial-tweak` paths, shipped as such, closes **that reviewer's lane** after **one** implementer pass with no further review round. | invariant | L917 · §5 | lane closure | severity + fix-path tags | **Severity bounds the loop** in `### Orchestrator discipline: routing review findings` | none | unknown | procedure |
| E5-051 | Nits applied that way are counted on the summary's **Reviews** line, not listed as ignored feedback. | relay | L917 · §5 | **Reviews** summary line | applied nits | - | none | unknown | procedure |
| E5-052 | **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.** | command | L918 · §5 | `defer-*` TaskList task | ignore decision | - | TaskList | yes | procedure |
| E5-053 | Name each such task `defer-<short-suffix>` per Section 3's "TaskList naming convention", with the feedback's one-line description as `metadata.activity`, status `pending`. | field-or-template | L918 · §5 | `defer-<short-suffix>` task, `metadata.activity` | Section 3 naming convention | Section 3, "TaskList naming convention" | TaskList | yes | procedure |
| E5-054 | The Director MUST annotate the `defer-*` task's `metadata.activity` with exactly one of `addressed-now-in-this-Task`, `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` at creation. | choice-set | L918 · §5 | destination annotation | PM destination vocabulary | `agents/pm.md` | TaskList | yes | procedure |
| E5-055 | The destination is the Director's judgement call, but the annotation itself is required, not optional. | invariant | L918 · §5 | - | - | - | TaskList | yes | procedure |
| E5-056 | Matching the PM Agent's contract keeps Section 6.5's deferral-hygiene gate able to route reviewer- and PM-feedback items through the same Fix / File / Encode branches. | rationale-only | L918 · §5 | - | - | Section 6.5 | none | yes | rationale |
| E5-057 | Vague framings without a named destination (e.g. "defer to later") are forbidden, by the same anti-pattern rule as the PM Agent's annotations. | invariant | L918 · §5 | - | - | `agents/pm.md` | TaskList | yes | procedure |
| E5-058 | This record-creating step is the load-bearing source for Section 6.5's deferral-hygiene gate; without it the gate fires empty. | rationale-only | L918 · §5 | - | - | Section 6.5 | none | yes | rationale |
| E5-059 | Run the **Bee-level TaskList close-out** once, after the review loop above has closed. | ordering | L920 · §5 · **Bee-level TaskList close-out (runs once, after the review loop above has closed).** | status flips | review-loop state | Section 4.1 step 3 | TaskList | no | procedure |
| E5-060 | Bee-scoped names have no per-Task close-out site; an unclosed one keeps matching part (g)'s **Clause 2** and wedges every later Engineer dispatch. | rationale-only | L920 · §5 | - | - | Section 4.1 step 3, part (g), **Clause 2** | none | no | rationale |
| E5-061 | **The review loop has not closed while any `aborted-<role>-<bee-id>` task is `pending`.** | precondition | L920 · §5 | - | `aborted-<role>-<bee-id>` task status | Section 3's movement-report rung | TaskList | no | procedure |
| E5-062 | When an `aborted-<role>-<bee-id>` task is `pending`, re-dispatch that lane and let it deliver before closing the loop. | command | L920 · §5 | writer re-dispatch | `aborted-*` marker | Section 3's movement-report rung | Agent, TaskList | no | procedure |
| E5-063 | Once the loop has closed and **every** Bee-level dispatch has returned, and before advancing to Section 6, mark the listed names `completed`, **sweeping by name prefix** so `-r<n>` rounds go with their first round. | ordering | L920 · §5 | status flips | all Bee-level returns | Section 6 | TaskList | no | procedure |
| E5-064 | Sweep the three Bee-scoped reviewer names `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>` plus `code-reviewer-<bee-id>-r1` and so on. | name-class | L922 · §5 | status flips | - | - | TaskList | no | procedure |
| E5-065 | Sweep the four Bee-scoped implementer and PM names `engineer-<bee-id>`, `test-writer-<bee-id>`, `doc-writer-<bee-id>`, `pm-<bee-id>` plus their `-r<n>` rounds. | name-class | L923 · §5 | status flips | - | - | TaskList | no | procedure |
| E5-066 | Sweep any Bee-scoped aborted-writer markers `aborted-test-writer-<bee-id>`, `aborted-doc-writer-<bee-id>` opened by Section 3's movement-report rung for a lane this section dispatched. | name-class | L924 · §5 | status flips | - | Section 3's movement-report rung | TaskList | no | procedure |
| E5-067 | Reaching the close-out step means the redelivery landed, since the review loop cannot close over a lane that never delivered. | rationale-only | L924 · §5 | - | - | - | none | no | rationale |
| E5-068 | **"Clear from the active set" means mark the task `completed` — it never means delete it.** | invariant | L926 · §5 | - | - | - | TaskList | yes | procedure |
| E5-069 | The `-r<n>` discriminator is derived by counting recorded rounds, so deleting a task makes the next re-dispatch reuse a name already spoken for. | rationale-only | L926 · §5 | - | - | Section 3's naming convention | none | yes | rationale |
| E5-070 | Closing by status keeps history readable and still removes the task from every `pending`/`in_progress` test part (g) runs. | rationale-only | L926 · §5 | - | - | part (g) | none | yes | rationale |
| E5-071 | The Bee-level close-out step runs **exactly once per Bee**. | invariant | L928 · §5 | - | - | - | TaskList | no | procedure |
| E5-072 | There is no Agent shutdown to perform; cold dispatches complete-and-exit, so close-out is bookkeeping on the progress UI and on part (g)'s state. | rationale-only | L928 · §5 | - | - | part (g) | none | unknown | rationale |
| E5-073 | After step 5's review loop is done and all fixable issues addressed, run one final fresh-context generalist sweep across all changes made by this Bee. | ordering | L933 · §6 | reviewer dispatch | step 5 completion | step 5 | Agent | yes | procedure |
| E5-074 | The post-completion review is an independent quality gate, separate from the per-Task and per-Epic review cycles. | definition | L933 · §6 | - | - | - | none | yes | procedure |
| E5-075 | Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at the post-completion stage. | invariant | L935 · §6 · **Anti-pattern callout — read before acting.** | - | - | `/quo-engineer-review`, `/quo-doc-writer-review`, `/quo-test-writer-review` | none | yes | procedure |
| E5-076 | Those three skills are lane-scoped (source code / user-facing docs / test files) and none runs the cross-lane sweep this step needs. | rationale-only | L935 · §6 | - | - | - | none | yes | rationale |
| E5-077 | Spawn a fresh general-purpose agent with a self-contained prompt instead of the lane reviewers. | command | L935 · §6 | Agent dispatch | - | - | Agent | yes | procedure |
| E5-078 | The team-lead must NOT do the post-completion review directly. | invariant | L937 · §6 · **Anti-pattern callout, second.** | - | - | - | none | yes | procedure |
| E5-079 | The team-lead's accumulated run context biases it toward "did the phases get done correctly?" rather than "is this good?". | rationale-only | L937 · §6 | - | - | - | none | yes | rationale |
| E5-080 | The fresh agent gets the diff and the Bee body and nothing else. | invariant | L937 · §6 | - | - | - | Agent | yes | procedure |
| E5-081 | Compute the pre-Bee diff scope: `Read` the run-state manifest at `<tempdir>/.quorum/run-state-quo-execute-<bee-id>.md` and take its **Pre-Bee SHA** field as `<pre-bee-sha>`. | command | L939 · §6 step 1 | `<pre-bee-sha>` | run-state manifest **Pre-Bee SHA** field | Section 1's run-start step | none | no | procedure |
| E5-082 | If the manifest is missing, fall back to `HEAD~M` where `M` is the number of Tasks committed in Step 4 (one commit per Task). | recovery | L939 · §6 step 1 | `<pre-bee-sha>` | Task commit count | Step 4 | git | no | procedure |
| E5-083 | If the Task count is lost, walk `git log` back to the commit before the first Task commit landed in Step 4. | recovery | L939 · §6 step 1 | `<pre-bee-sha>` | `git log` | Step 4 | git, Bash | no | procedure |
| E5-084 | Collect the Bee ID `<bee-id>` and, secondarily, the Epic/Task IDs under it as `<epic-id-1> <task-id-1> ...`. | command | L939 · §6 step 1 | `<bee-id>`, Epic/Task ID list | Bee tree | - | bees | no | procedure |
| E5-085 | The Bee body is the primary spec; Epic/Task bodies are secondary context the reviewer consults only when the diff is ambiguous. | definition | L939 · §6 step 1 | - | - | - | none | no | procedure |
| E5-086 | Spawn the fresh reviewer with the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. | command | L941 · §6 step 2 | Agent dispatch | - | - | Agent | yes | procedure |
| E5-087 | The reviewer prompt must be self-contained because the agent sees nothing else from this run. | invariant | L941 · §6 step 2 | - | - | - | Agent | yes | procedure |
| E5-088 | Pass the compromise-tracker path (Section 6.5's `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`) as `<compromise-tracker-path>` — the path, NOT the inlined contents. | invariant | L941 · §6 step 2 | `<compromise-tracker-path>` prompt value | compromise tracker file | Section 6.5 | Agent | yes | procedure |
| E5-089 | Substitute `<pre-bee-sha>`, `<compromise-tracker-path>`, `<bee-id>`, and the Epic/Task IDs into the skeleton before sending. | command | L941 · §6 step 2 | prompt | step 1 outputs | - | Agent | yes | procedure |
| E5-090 | The prompt opens with the role line `You are an independent reviewer for a quorum Bee that was just shipped.` | field-or-template | L944 · §6 step 2 skeleton | prompt text | - | - | none | yes | procedure |
| E5-091 | Reviewer scope is `git diff <pre-bee-sha>` — no `..HEAD` — i.e. the working tree against the pre-Bee commit, computed by the reviewer via git. | command | L946-L950 · §6 step 2 skeleton | reviewer scope | `<pre-bee-sha>` | - | git, Bash | yes | procedure |
| E5-092 | Reviewer scope also includes every untracked file `git ls-files --others --exclude-standard` lists, read from disk. | command | L946-L950 · §6 step 2 skeleton | reviewer scope | untracked files | - | git, Bash | yes | procedure |
| E5-093 | Bee-level review-round edits sit uncommitted at this point, so a commit-to-commit range alone misses them. | rationale-only | L949-L950 · §6 step 2 skeleton | - | - | - | none | yes | rationale |
| E5-094 | When a finding concerns a change no Bee, Epic, or Task body asks for, the reviewer says it is likely pre-existing or an unticketed in-run edit, as an inference, naming that basis. | relay | L951-L956 · §6 step 2 skeleton | finding text | ticket bodies | - | none | yes | procedure |
| E5-095 | Review the scope against the Bee body, read via `bees show-ticket --ids <bee-id>`. | command | L956-L957 · §6 step 2 skeleton | - | Bee body | - | bees, Bash | yes | procedure |
| E5-096 | Consult Epic/Task bodies via `bees show-ticket --ids <epic-id-1> <task-id-1> ...` only when the diff vs. the Bee body is ambiguous. | precondition | L957-L959 · §6 step 2 skeleton | - | Epic/Task bodies | - | bees, Bash | yes | procedure |
| E5-097 | The reviewer's job is a fresh-eyes review with no context of how the work was done. | definition | L959-L961 · §6 step 2 skeleton | - | - | - | none | yes | rationale |
| E5-098 | Perform the phases IN ORDER; Phases 1–5 lead with challenging accepted compromises, and the discrete-defect sweep is the FINAL phase. | ordering | L963-L965 · §6 step 2 skeleton | - | - | - | none | yes | procedure |
| E5-099 | PHASE 1: consume the compromise tracker passed as a FILE PATH at `<compromise-tracker-path>`, reading it via the Read tool. | command | L967-L972 · §6 skeleton PHASE 1 | - | compromise tracker file | - | none | yes | procedure |
| E5-100 | The tracker records every compromise the run accepted: deferred-to-Issue findings, accepted limitations, ungated orchestrator path picks, post-completion overrides. | definition | L968-L970 · §6 skeleton PHASE 1 | - | - | Section 6.5 | none | yes | procedure |
| E5-101 | Each `## Compromise <n>` entry carries Finding (verbatim), Fix paths surfaced by reviewer (each with a `[depth:<...>]` tag), Decision, Rationale, Follow-up Issue. | field-or-template | L973-L975 · §6 skeleton PHASE 1 | - | tracker entries | Section 6.5 | none | yes | procedure |
| E5-102 | If the tracker file is MISSING or unreadable, do NOT abort — PROCEED with the remaining phases and flag the missing tracker explicitly in the output. | recovery | L975-L978 · §6 skeleton PHASE 1 | missing-tracker flag | tracker file presence | - | none | yes | procedure |
| E5-103 | PHASE 2: challenge each tracked compromise on its merits; push back when the chosen path is not defensible; do not rubber-stamp. | command | L980-L982 · §6 skeleton PHASE 2 | findings | tracker entries | - | none | yes | procedure |
| E5-104 | PHASE 2 includes the deep-asked-but-cheap-shipped check: flag any mismatch between what the tracker records as chosen and what the diff actually shipped. | command | L982-L986 · §6 skeleton PHASE 2 | findings | tracker Decision vs diff | - | none | yes | procedure |
| E5-105 | An entry whose `Finding (verbatim)` carries the `blocker` severity tag and whose `Decision` is `User picked Accept the limitation` is a contract violation — a blocker can never be accepted. | invariant | L986-L989 · §6 skeleton PHASE 2 | finding | tracker entry fields | - | none | yes | procedure |
| E5-106 | An entry whose `Decision` is `User picked Defer to follow-up Issue` and whose `Rationale` carries **no narrowing record** is a contract violation. | invariant | L989-L993 · §6 skeleton PHASE 2 | finding | tracker entry fields | - | none | yes | procedure |
| E5-107 | A narrowing record states what was narrowed out of the change and why the blocker no longer describes anything that ships. | definition | L990-L992 · §6 skeleton PHASE 2 | - | - | - | none | yes | procedure |
| E5-108 | An entry whose narrowing record shows the narrowing **left the unit's stated defect partly unfixed** is a contract violation; a narrowing may never reduce coverage of the stated defect. | invariant | L993-L997 · §6 skeleton PHASE 2 | finding | tracker Rationale | - | none | yes | procedure |
| E5-109 | Emit every PHASE 2 contract violation as a `[compromise-challenge]` finding at `blocker` severity, never lower. | command | L997-L998 · §6 skeleton PHASE 2 | `[compromise-challenge]` `blocker` finding | - | - | none | yes | procedure |
| E5-110 | PHASE 3 applies to every entry whose Decision is `Orchestrator picked path (<letter>) — highest-quality`, matching on surrounding wording rather than a literal letter. | precondition | L1000-L1004 · §6 skeleton PHASE 3 | - | tracker Decision | - | none | yes | procedure |
| E5-111 | PHASE 3 axis (i): evaluate whether the depth judgment was plausible or the chosen path's true depth is `re-architect`. | command | L1004-L1005 · §6 skeleton PHASE 3 | finding | tracker entry, diff | - | none | yes | procedure |
| E5-112 | PHASE 3 axis (ii): evaluate whether the chosen path introduced a mechanism the unit's approved design did not enumerate, and whether it should have been deferred or put to the user. | command | L1006-L1012 · §6 skeleton PHASE 3 | finding | tracker entry, diff | - | none | yes | procedure |
| E5-113 | "Mechanism" means a new state, configuration surface (flag, environment variable, setting), persisted or wire field, background task, exception or error type, metric / log / trace attribute, name or identifier class, gate, or retry / fallback path. | definition | L1006-L1010 · §6 skeleton PHASE 3 | - | - | - | none | yes | procedure |
| E5-114 | Emit a `[compromise-challenge]` finding on either PHASE 3 axis. | command | L1012-L1013 · §6 skeleton PHASE 3 | `[compromise-challenge]` finding | - | - | none | yes | procedure |
| E5-115 | PHASE 3 axis (ii) is required, not optional. | invariant | L1013-L1015 · §6 skeleton PHASE 3 | - | - | - | none | yes | procedure |
| E5-116 | An ungated pick is an orchestrator judgment no gate reviewed, and PHASE 3 is the only place it gets challenged. | rationale-only | L1014-L1015 · §6 skeleton PHASE 3 | - | - | - | none | yes | rationale |
| E5-117 | PHASE 4: for EVERY finding the in-flow reviewer surfaced, regardless of severity / depth / path-count, evaluate whether an additional plausible fix path should have been enumerated. | command | L1017-L1020 · §6 skeleton PHASE 4 | - | in-flow reviewer findings | - | none | yes | procedure |
| E5-118 | When under-enumeration is judged, emit a `[compromise-challenge]` finding naming the under-enumeration. | command | L1020-L1023 · §6 skeleton PHASE 4 | `[compromise-challenge]` finding | - | - | none | yes | procedure |
| E5-119 | PHASE 3 catches misjudged depth or an unnoticed mechanism on a surfaced path; PHASE 4 catches a plausible path that was not surfaced at all. | rationale-only | L1023-L1026 · §6 skeleton PHASE 4 | - | - | - | none | yes | rationale |
| E5-120 | PHASE 5: judge holistic solution quality beyond the logged compromises — is the shipped solution actually good independent of any single tracked decision? | command | L1028-L1030 · §6 skeleton PHASE 5 | `[design]` findings | diff, Bee body | - | none | yes | procedure |
| E5-121 | PHASE 6 (final): flag code defects, prose problems, spec drift between the change and the Bee, contract-key violations, cross-file inconsistencies, and missing edits the Bee called for. | command | L1032-L1036 · §6 skeleton PHASE 6 | `[defect]` findings | diff, Bee body | - | none | yes | procedure |
| E5-122 | Do NOT allow renames of keys in CLAUDE.md `## Documentation Locations` or `## Build Commands`. | invariant | L1034-L1035 · §6 skeleton PHASE 6 | finding | CLAUDE.md contract keys | CLAUDE.md `## Documentation Locations`, `## Build Commands` | none | yes | procedure |
| E5-123 | One generalist pass covers code AND docs AND tests — do not lane-scope. | invariant | L1037 · §6 skeleton PHASE 6 | - | - | - | none | yes | procedure |
| E5-124 | In skill repos, `skills/<name>/SKILL.md` and `agents/<name>.md` files in the diff are program source code; review them with source-level rigor for broken cross-references, drifted contracts, ambiguous prose, and CLAUDE.md design-rule violations. | invariant | L1039-L1044 · §6 skeleton PHASE 6 | - | diff contents | - | none | yes | procedure |
| E5-125 | Do NOT do a general repo audit; stay focused on the diff against the pre-Bee commit and the untracked files. | invariant | L1046-L1048 · §6 skeleton | - | - | - | none | yes | procedure |
| E5-126 | The reviewer must NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review`. | invariant | L1050-L1053 · §6 skeleton | - | - | `/quo-engineer-review`, `/quo-doc-writer-review`, `/quo-test-writer-review` | none | yes | procedure |
| E5-127 | Return findings as a numbered list. | field-or-template | L1055 · §6 skeleton | numbered findings list | - | - | none | yes | procedure |
| E5-128 | Tag EVERY finding with exactly one of `[compromise-challenge]` (from PHASE 2/3/4), `[design]`, or `[defect]`. | field-or-template | L1055-L1058 · §6 skeleton | class tag | - | - | none | yes | procedure |
| E5-129 | Tag EVERY finding with a severity tag: `blocker` / `suggestion` / `nit`. | field-or-template | L1058 · §6 skeleton | severity tag | - | - | none | yes | procedure |
| E5-130 | Tag EVERY finding with the per-fix-path depth tag and the enumerated fix paths from the in-flight emission contract. | field-or-template | L1059-L1060 · §6 skeleton | depth tag, fix paths | in-flight emission contract | - | none | yes | procedure |
| E5-131 | The depth tag is informative here: the post-completion sweep is the final pre-merge gate, so any finding is a gate candidate regardless of depth. | invariant | L1060-L1062 · §6 skeleton | - | - | - | none | yes | procedure |
| E5-132 | Preserve the `file:line` + severity finding shape; the new tags are additive. | invariant | L1062-L1063 · §6 skeleton | - | - | - | none | yes | procedure |
| E5-133 | If clean, the reviewer returns exactly `no issues found`. | field-or-template | L1063-L1064 · §6 skeleton | `no issues found` return | - | - | none | yes | procedure |
| E5-134 | Wait for the agent's report before proceeding. | ordering | L1067 · §6 step 2 | - | Agent return | - | Agent | yes | procedure |
| E5-135 | Synthesize before presenting: compare the fresh reviewer's findings against the in-flight per-Task PM verdict and per-Task reviewer verdicts and flag disagreements explicitly. | command | L1069 · §6 step 3 | synthesis notes | reviewer return, in-context verdicts | - | none | yes | procedure |
| E5-136 | Example disagreement note: "fresh reviewer flagged X but in-flight code reviewer judged X clean." | example | L1069 · §6 step 3 | - | - | - | none | yes | example |
| E5-137 | Present the synthesized findings (fresh reviewer's list plus synthesis notes) to the user. | relay | L1069 · §6 step 3 | user-facing findings | synthesis | - | none | yes | procedure |
| E5-138 | When the reviewer returns one or more `[compromise-challenge]` findings, render a one-or-two-sentence prose preamble BEFORE the findings list naming this explicitly. | relay | L1071 · §6 step 3 · **Compromise-challenge preamble (rendered before presenting the findings).** | preamble text | `[compromise-challenge]` findings | - | none | yes | procedure |
| E5-139 | The preamble mirrors the verdict-keyed preamble pattern in `/quo-plan` Step 5e and `/quo-fix-issue` Section 3's Analyst-verdict preamble, using the `⚠️`-led divergent-framing convention. | field-or-template | L1071 · §6 step 3 | preamble shape | - | `/quo-plan` Step 5e, `/quo-fix-issue` Section 3 | none | yes | procedure |
| E5-140 | Example preamble: "⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below." | example | L1071 · §6 step 3 | - | - | - | none | yes | example |
| E5-141 | When there are no `[compromise-challenge]` findings, render no preamble; present the findings directly. | invariant | L1071 · §6 step 3 | - | - | - | none | yes | procedure |
| E5-142 | Before yielding at step 4 / step 5, mark every orchestrator self-tracking TaskList task created during Section 6 `completed` and clear it from the active set. | ordering | L1073 · §6 step 3 · **Orchestrator self-tracking close-out (mandatory before yielding).** | status flips | ad-hoc TaskList tasks | Section 4.1 step 3, Section 5's **Bee-level TaskList close-out** | TaskList | yes | procedure |
| E5-143 | Example self-tracking tasks: "Get diff scope", per-ticket "Verify <id>" entries, "Synthesize findings". | example | L1073 · §6 step 3 | - | - | - | TaskList | yes | example |
| E5-144 | The yield is the close-out trigger: when the orchestrator stops responding, the TaskList must show no `in_progress` entries left over from synthesis steps. | invariant | L1073 · §6 step 3 | - | TaskList state | - | TaskList | yes | procedure |
| E5-145 | Section 5's **Bee-level TaskList close-out** is authoritative for every `*-<bee-id>` task **dispatched by Section 5**; the self-tracking close-out adds nothing to it. | definition | L1073 · §6 step 3 | - | - | Section 5 | TaskList | no | procedure |
| E5-146 | Neither close-out covers the post-completion-scoped names step 6's `Fix in this session` branch dispatches; that branch closes them out itself. | definition | L1073 · §6 step 3 | - | - | step 6 | TaskList | yes | procedure |
| E5-147 | The self-tracking close-out is the analog of step 6's per-finding close-out (`<role>-postcomp-<n>` Agents, their `-r<k>` re-dispatches, `aborted-<role>-postcomp-<n>` markers); the two are complementary, not overlapping. | definition | L1073 · §6 step 3 | - | - | step 6 | TaskList | yes | procedure |
| E5-148 | If the agent returned `no issues found`, report `Post-completion review: no issues found` and continue to Final Output. | relay | L1075 · §6 step 4 | user-facing line | reviewer return | Final Output | none | yes | procedure |
| E5-149 | If the agent flagged issues, first create a `gate-askuserquestion-<short-suffix>` TaskList task naming the post-completion findings gate, then call `AskUserQuestion` in the same turn. | gate | L1077 · §6 step 5 | `gate-askuserquestion-<short-suffix>` task, AskUserQuestion | reviewer findings | Section 3's TaskList naming convention gate-task entry | TaskList, AskUserQuestion | yes | procedure |
| E5-150 | Do not produce a text response describing the post-completion gate; fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L1077 · §6 step 5 | - | - | - | TaskList, AskUserQuestion | yes | procedure |
| E5-151 | Mark the `gate-*` task `completed` once the user's answer is consumed and the step-6 routing branch is entered. | ordering | L1077 · §6 step 5 | status flip | user answer | step 6 | TaskList | yes | procedure |
| E5-152 | Gate question text: `Post-completion review found [N] issues. How would you like to handle them?` | field-or-template | L1078 · §6 step 5 | question text | finding count | - | AskUserQuestion | yes | procedure |
| E5-153 | Gate options are exactly `Fix in this session` (address now before closing the Bee), `File as issue tickets` (create tickets via `/quo-file-issue` for each), `Skip` (acknowledge and move on). | choice-set | L1080-L1082 · §6 step 5 | choice labels | - | `/quo-file-issue` | AskUserQuestion | yes | procedure |
| E5-154 | When the reviewer returned a PHASE 2 contract-violation `[compromise-challenge]` finding, the question text recommends `Fix in this session`. | gate | L1084 · §6 step 5 | recommendation in question text | PHASE 2 finding | step 7 | AskUserQuestion | yes | procedure |
| E5-155 | On `Fix in this session`, dispatch fresh ephemeral Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. | command | L1087 · §6 step 6 · **Fix in this session** | Agent dispatches | user choice | Section 3 | Agent | yes | procedure |
| E5-156 | Stay in delegate mode during post-completion fixes — do not do the work yourself. | invariant | L1087 · §6 step 6 | - | - | - | Agent | yes | procedure |
| E5-157 | Name post-completion follow-up tasks `<role>-postcomp-<n>`, where `<n>` is the 1-based index of the finding in the reviewer's numbered list. | name-class | L1089 · §6 step 6 · **Naming.** | TaskList tasks | finding index | `/quo-fix-issue` Section 8 step 6 | TaskList | yes | procedure |
| E5-158 | Example post-completion names: `engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`. | example | L1089 · §6 step 6 | - | - | - | TaskList | yes | example |
| E5-159 | Section 3's "exactly one TaskList task per Agent" rule applies: two findings each needing an Engineer dispatch under distinct names, never colliding on a shared `engineer-postcomp`. | invariant | L1089 · §6 step 6 | - | - | Section 3 | TaskList | yes | procedure |
| E5-160 | Section 3's Subtask-, Task-, and Bee-scoped names do not fit a follow-up answering one finding of a whole-Bee sweep, hence the post-completion scope. | rationale-only | L1089 · §6 step 6 | - | - | Section 3 | none | yes | rationale |
| E5-161 | When each follow-up Agent returns, persist the result as Section 3's reconcile-on-completion step does — confirm any bees ticket transitions the worker committed to. | command | L1091 · §6 step 6 · **Close-out.** | ticket confirmations | Agent return | Section 3 reconcile-on-completion | bees | yes | procedure |
| E5-162 | Then mark the corresponding `<role>-postcomp-<n>` task `completed` and clear it from the active set. | ordering | L1091 · §6 step 6 | status flip | Agent return | - | TaskList | yes | procedure |
| E5-163 | In the post-completion close-out, "clear" means mark `completed`, never delete (same rule as Section 5's Bee-level close-out). | invariant | L1091 · §6 step 6 | - | - | Section 5 | TaskList | yes | procedure |
| E5-164 | Sweep post-completion names by **prefix** before the `Fix in this session` branch exits, so no post-completion-scoped task is left active. | ordering | L1091 · §6 step 6 | status flips | active TaskList set | - | TaskList | yes | procedure |
| E5-165 | A `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` return reporting it stopped on detected source movement is NOT a completion. | invariant | L1093 · §6 step 6 · **Section 3's movement-report rung carries over onto the post-completion names.** | - | writer return | Section 3's movement-report rung | TaskList | yes | procedure |
| E5-166 | On such a return, mark the writer's `<role>-postcomp-<n>` task `completed` and open an `aborted-<role>-postcomp-<n>` task `pending` in its place, carrying the same `<n>`. | command | L1093 · §6 step 6 | `aborted-<role>-postcomp-<n>` task | writer return | Section 3's movement-report rung | TaskList | yes | procedure |
| E5-167 | Set the `aborted-<role>-postcomp-<n>` task's `metadata.activity` to the writer's "how far I got" report. | field-or-template | L1093 · §6 step 6 | `metadata.activity` | writer report | - | TaskList | yes | procedure |
| E5-168 | Re-dispatch the aborted lane once source has settled, per the rung's three mover branches, under `<role>-postcomp-<n>-r<k>` (e.g. `test-writer-postcomp-2-r1`) with the same `<n>`. | name-class | L1093 · §6 step 6 | re-dispatch, TaskList task | `aborted-*` marker | Section 3's movement-report rung, naming convention's abort carve-out | Agent, TaskList | yes | procedure |
| E5-169 | Mark the `aborted-*` task `completed` when the re-dispatch delivers. | ordering | L1093 · §6 step 6 | status flip | re-dispatch return | - | TaskList | yes | procedure |
| E5-170 | **While an `aborted-<role>-postcomp-<n>` task is `pending`, do not treat this Section 6 pass as finished and do not commit.** | precondition | L1093 · §6 step 6 | - | `aborted-*` task status | Section 3 | TaskList, git | yes | procedure |
| E5-171 | The rung's **unexplained-movement gate** applies unchanged, with its third option read as *abort this follow-up lane* rather than *abort this unit*. | gate | L1093 · §6 step 6 | AskUserQuestion | movement report | Section 3's unexplained-movement gate | AskUserQuestion, TaskList | yes | procedure |
| E5-172 | The unexplained-movement gate's close-out here is this branch's own prefix sweep, not Section 4.2's `##### Aborted-run close-out`. | invariant | L1093 · §6 step 6 | - | - | Section 4.2 `##### Aborted-run close-out` | TaskList | yes | procedure |
| E5-173 | Section 4.2's aborted-run close-out is scoped to a run that stops without its unit advancing, which no post-completion lane does since every Epic is `done` and every per-Task commit has landed. | rationale-only | L1093 · §6 step 6 | - | - | Section 4.2 | none | yes | rationale |
| E5-174 | After the sweep closes out an aborted lane's names, continue Section 6's own flow — remaining findings' dispositions, step 7's recovery gates, then Section 6.5 — rather than exiting the run. | ordering | L1093 · §6 step 6 | - | - | step 7, Section 6.5 | none | yes | procedure |
| E5-175 | **The orchestrator MUST NOT dispatch an `engineer-postcomp-<n>` Agent while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` TaskList task is `pending` or `in_progress`**, matching on name prefix plus status at every finding index and every `-r<k>` round. | precondition | L1095 · §6 step 6 · **The Engineer-dispatch freeze precondition applies here too, on the post-completion names.** | - | active TaskList set | part (g) | TaskList, Agent | yes | procedure |
| E5-176 | Part (g)'s two clauses key on Subtask-, Task-, and Bee-scoped names, none of which match post-completion names, so the freeze is restated explicitly here. | rationale-only | L1095 · §6 step 6 | - | - | part (g) | none | yes | rationale |
| E5-177 | A writer handed a diff an Engineer is about to rewrite has to redo its work. | rationale-only | L1095 · §6 step 6 | - | - | part (g) | none | yes | rationale |
| E5-178 | Part (g)'s `pending`-with-no-Agent-behind-it clause carries over: dispatch the stalled role, or mark the stale task `completed` and clear it, rather than waiting on a notification that will never arrive. | recovery | L1095 · §6 step 6 | dispatch or status flip | stale TaskList task | part (g) | TaskList, Agent | yes | procedure |
| E5-179 | When one finding needs both a source change and a test/doc change, dispatch the **Engineer** (`engineer-postcomp-<n>`) first and let it return; only then dispatch the `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` lane. | ordering | L1097 · §6 step 6 · **Order the lanes when one finding needs both a source change and a test/doc change.** | dispatch sequence | finding shape | - | Agent, TaskList | yes | procedure |
| E5-180 | Two findings independent of one another may be worked concurrently; the within-finding ordering and the cross-finding freeze are the only constraints. | invariant | L1097 · §6 step 6 | - | - | - | Agent | yes | procedure |
| E5-181 | After every follow-up lane has delivered, commit and continue to Section 6.5 (deferral hygiene). | ordering | L1099 · §6 step 6 | git commit | all follow-up returns | Section 6.5 | git | yes | procedure |
| E5-182 | On `File as issue tickets`, invoke `/quo-file-issue` with each issue's description, report the created ticket IDs to the user, and continue to Section 6.5. | command | L1100 · §6 step 6 · **File as issue tickets** | Issue tickets, user report | reviewer findings | `/quo-file-issue`, Section 6.5 | bees | yes | procedure |
| E5-183 | On `Skip`, continue to Section 6.5. | ordering | L1101 · §6 step 6 · **Skip** | - | user choice | Section 6.5 | none | yes | procedure |
| E5-184 | A `[compromise-challenge]` finding from PHASE 3 or PHASE 4 triggers its own recovery gate, fired **before or alongside** the step-6 disposition for that finding. | gate | L1103 · §6 step 7 · **Compromise-challenge recovery gates.** | AskUserQuestion | PHASE 3/4 findings | step 6 | AskUserQuestion, TaskList | yes | procedure |
| E5-185 | **One challenge class has no recovery gate, by design: the accepted-`blocker`-or-unnarrowed-deferral contract violation PHASE 2 emits.** | invariant | L1103 · §6 step 7 | - | PHASE 2 finding class | - | none | yes | procedure |
| E5-186 | There is nothing to recover from a PHASE 2 violation — it records an acceptance the gates should never have offered, an unnarrowed deferral, or a narrowing that left the defect partly unfixed. | rationale-only | L1103 · §6 step 7 | - | - | - | none | yes | rationale |
| E5-187 | A PHASE 2 violation is dispositioned by **step 5's Fix / File / Skip gate alone**, and step 6 executes whatever that gate returns. | gate | L1103 · §6 step 7 | - | step 5 answer | step 5, step 6 | AskUserQuestion | yes | procedure |
| E5-188 | Because a PHASE 2 violation is a `blocker`, the orchestrator recommends **`Fix in this session`** in the step-5 gate's question text. | gate | L1103 · §6 step 7 | question-text recommendation | PHASE 2 finding | step 5 | AskUserQuestion | yes | procedure |
| E5-189 | The step-5 gate is **aggregate** — one answer covers every finding — so the recommendation is stated once for the whole finding set. | invariant | L1103 · §6 step 7 | - | - | step 5 | AskUserQuestion | yes | procedure |
| E5-190 | A `Skip` at the step-5 gate leaves a PHASE 2 contract violation recorded only in the reviewer's output and the compromise tracker. | definition | L1103 · §6 step 7 | - | - | - | none | yes | procedure |
| E5-191 | Do not invent a fourth gate for the PHASE 2 contract-violation class. | invariant | L1103 · §6 step 7 | - | - | - | none | yes | procedure |
| E5-192 | Both recovery gates use the two-step contract: first create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, with a distinct collision-resistant `<short-suffix>` per fire, then call `AskUserQuestion` with the finite choices in the same turn. | gate | L1103 · §6 step 7 | `gate-askuserquestion-<short-suffix>` task, AskUserQuestion | - | per-fire-uniqueness rule | TaskList, AskUserQuestion | yes | procedure |
| E5-193 | Do not produce a text response describing a recovery gate; fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L1103 · §6 step 7 | - | - | - | TaskList, AskUserQuestion | yes | procedure |
| E5-194 | Mark each recovery gate's `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. | ordering | L1103 · §6 step 7 | status flip | user answer | - | TaskList | yes | procedure |
| E5-195 | Recovery gates are multi-choice only — do not add fake free-text options. | invariant | L1103 · §6 step 7 | - | - | - | AskUserQuestion | yes | procedure |
| E5-196 | Each recovery gate **fires per challenged finding** (three such findings ⇒ three firings), NOT aggregated into one gate. | invariant | L1103 · §6 step 7 | one AskUserQuestion per finding | `[compromise-challenge]` findings | - | AskUserQuestion | yes | procedure |
| E5-197 | The recovery gates' **firing order equals the reviewer's emission order** in its numbered list. | ordering | L1103 · §6 step 7 | - | reviewer numbered list | - | AskUserQuestion | yes | procedure |
| E5-198 | The recovery gates inherit a prose-adherence fragility narrowed (not closed) by the two-step contract; do not claim it is fixed. | invariant | L1103 · §6 step 7 | - | - | - | none | yes | rationale |
| E5-199 | After the recovery gates resolve for every challenged finding, continue to Section 6.5. | ordering | L1103 · §6 step 7 | - | - | Section 6.5 | none | yes | procedure |
| E5-200 | Fire the **SR-6.7 ungated-route recovery gate** — a three-choice `AskUserQuestion` — when a `[compromise-challenge]` flags an ungated pick (Decision `Orchestrator picked path (x) — highest-quality`) on either PHASE 3 axis. | gate | L1105 · §6 step 7 · **SR-6.7 ungated-route recovery gate.** | AskUserQuestion | PHASE 3 finding | Section 6.5 Trigger D | AskUserQuestion, TaskList | yes | procedure |
| E5-201 | SR-6.7 choice labels are byte-matched against Section 6.5's Trigger D branches; do not reword them. | invariant | L1105 · §6 step 7 | - | - | Section 6.5 Trigger D | AskUserQuestion | yes | procedure |
| E5-202 | The pinned strings `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` name **the routing misjudgment** on either axis, mechanism axis included. | definition | L1105 · §6 step 7 · **The pinned strings read generically across both axes:** | - | - | Trigger D | none | yes | procedure |
| E5-203 | Read "depth decision" / "misjudgment" generically rather than concluding the mechanism axis has no gate. | invariant | L1105 · §6 step 7 | - | - | - | none | yes | procedure |
| E5-204 | SR-6.7 choice `File follow-up Issue to revisit the depth decision`: dispatch `/quo-file-issue` via the Skill tool capturing the depth-mismatch finding plus the original compromise-tracker entry as context. | choice-set | L1106 · §6 step 7 | Issue ticket | finding, tracker entry | `/quo-file-issue` | AskUserQuestion, bees | yes | procedure |
| E5-205 | On that `File` branch, update the **original Trigger C tracker entry's `Follow-up Issue` field in place** with the new Issue ID — NO new tracker entry. | command | L1106 · §6 step 7 | tracker field update | new Issue ID | Section 6.5 Trigger D `File`-branch note | none | yes | procedure |
| E5-206 | SR-6.7 choice `Accept the misjudgment and proceed`: fire Section 6.5's **Trigger D** append — a NEW tracker entry with `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` and the reviewer's challenge text as Rationale. | choice-set | L1107 · §6 step 7 | tracker entry | reviewer challenge text | Section 6.5 Trigger D | AskUserQuestion | yes | procedure |
| E5-207 | The `Accept` branch FIRES Trigger D's write; it does not author it — the write mechanism is owned by Section 6.5's Trigger D. | invariant | L1107 · §6 step 7 | - | - | Section 6.5 Trigger D | none | yes | procedure |
| E5-208 | SR-6.7 choice `Pause to discuss`: stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. | choice-set | L1108 · §6 step 7 | prose discussion | - | Trigger D `Pause` note | AskUserQuestion | yes | procedure |
| E5-209 | No tracker write fires on the `Pause to discuss` branch until a subsequent `Accept` / `File` pick. | invariant | L1108, L1112 · §6 step 7 | - | - | Trigger D `Pause` note | none | yes | procedure |
| E5-210 | Fire the **SR-4.6 under-enumeration recovery gate** — the same three-choice gate shape with relabeled choices — when a `[compromise-challenge]` flags under-enumeration. | gate | L1109 · §6 step 7 · **SR-4.6 under-enumeration recovery gate.** | AskUserQuestion | PHASE 4 finding | - | AskUserQuestion, TaskList | yes | procedure |
| E5-211 | SR-4.6 choice `File follow-up Issue to surface the missing path`: dispatch `/quo-file-issue` via the Skill tool capturing the under-enumeration finding as context. | choice-set | L1110 · §6 step 7 | Issue ticket | finding | `/quo-file-issue` | AskUserQuestion, bees | yes | procedure |
| E5-212 | On that `File` branch, the tracker write follows Section 6.5's Trigger D `File`-branch under-enumeration note: append a new entry, or update an existing originating Trigger C entry's `Follow-up Issue` in place when one exists. | command | L1110 · §6 step 7 | tracker entry or field update | new Issue ID | Section 6.5 Trigger D | none | yes | procedure |
| E5-213 | SR-4.6 choice `Accept the under-enumeration and proceed`: fire Trigger D's append — a NEW tracker entry with `Decision: User accepted under-enumeration after post-completion challenge` and the challenge text as Rationale; this FIRES, not authors, the write. | choice-set | L1111 · §6 step 7 | tracker entry | reviewer challenge text | Section 6.5 Trigger D | AskUserQuestion | yes | procedure |
| E5-214 | SR-4.6 choice `Pause to discuss`: stop the flow, surface a prose discussion; the user can re-issue any of the three choices afterward. | choice-set | L1112 · §6 step 7 | prose discussion | - | - | AskUserQuestion | yes | procedure |
| E5-215 | The SR-4.6 gate's per-branch behavior mirrors SR-6.7 exactly (file follow-up Issue / append explicit-override tracker entry via Trigger D / pause-and-resume). | invariant | L1114 · §6 step 7 | - | - | Section 6.5 Trigger D | none | yes | procedure |
| E5-216 | Like SR-6.7, SR-4.6 fires per challenged finding (non-aggregated) in reviewer emission order. | invariant | L1114 · §6 step 7 | - | - | - | AskUserQuestion | yes | procedure |

## Anchors defined here

Headings:

- L894 — `### 5. Final Bee-level Code, Doc and Eng reviews`
- L931 — `### 6. Post-Completion Review`

Bolded phrases (verbatim) that other text could point at:

- L898 — **The Code Reviewer dispatch prompt must relay the Engineers' completeness evidence verbatim.**
- L898 — **completeness check with evidence**
- L898 — **and in any `pm-<bee-id>` re-dispatch prompt**
- L898 — **Separately from the lists, state in the prompt that the assignment was sweep-shaped whenever it was**
- L898 — **One post-compaction qualification applies at this Bee-level relay only:**
- L898 — **only when the list is actually in hand, or the Engineer genuinely returned none**
- L898 — **existed but is unavailable post-compaction**
- L898 — **The Bee-scoped PM needs its own copy:**
- L907 — **Code Reviewer**
- L908 — **Test Reviewer**
- L909 — **Doc Reviewer**
- L911 — **Follow the trailer literally**
- L912 — **Track each under the Bee-scoped names from Section 3's TaskList naming convention**
- L912 — **When a finding's chosen fix path changes source, these re-dispatches are ordered, not concurrent**
- L912 — **Clause 2 (Bee-level)**
- L913 — **Second-order effects have a destination.**
- L913 — **`**Second-order effects**` field of the `## Bee Execution Complete` summary**
- L914 — **IMPORTANT**
- L917 — **that reviewer's lane** / **one** / **Severity bounds the loop** / **Reviews**
- L918 — **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.**
- L920 — **Bee-level TaskList close-out (runs once, after the review loop above has closed).**
- L920 — **The review loop has not closed while any `aborted-<role>-<bee-id>` task is `pending`**
- L920 — **sweeping by name prefix**
- L926 — **"Clear from the active set" means mark the task `completed` — it never means delete it.**
- L928 — **exactly once per Bee**
- L935 — **Anti-pattern callout — read before acting.**
- L937 — **Anti-pattern callout, second.**
- L939 — **Pre-Bee SHA**
- L941 — **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**
- L990-L991 (skeleton) — **no narrowing record**
- L994-L995 (skeleton) — **left the unit's stated defect partly unfixed**
- L1071 — **Compromise-challenge preamble (rendered before presenting the findings).**
- L1073 — **Orchestrator self-tracking close-out (mandatory before yielding).**
- L1073 — **Bee-level TaskList close-out** (back-reference to L920) / **dispatched by Section 5** / **step 6's**
- L1080 — **Fix in this session**
- L1081 — **File as issue tickets**
- L1082 — **Skip**
- L1084 — **`Fix in this session`**
- L1089 — **Naming.** / **post-completion-scoped**
- L1091 — **Close-out.** / **"clear" means mark `completed`, never delete** / **prefix**
- L1093 — **Section 3's movement-report rung carries over onto the post-completion names.**
- L1093 — **not** a completion / **the marker carries the same `<n>` as the lane it marks**
- L1093 — **While an `aborted-<role>-postcomp-<n>` task is `pending`, do not treat this Section 6 pass as finished and do not commit**
- L1093 — **unexplained-movement gate** / **this branch's own prefix sweep above** / **without the unit it was working advancing**
- L1095 — **The Engineer-dispatch freeze precondition applies here too, on the post-completion names.**
- L1095 — **the orchestrator MUST NOT dispatch an `engineer-postcomp-<n>` Agent while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` TaskList task is `pending` or `in_progress`**
- L1097 — **Order the lanes when one finding needs both a source change and a test/doc change.** / **Engineer**
- L1103 — **Compromise-challenge recovery gates.**
- L1103 — **before or alongside**
- L1103 — **One challenge class has no recovery gate, by design: the accepted-`blocker`-or-unnarrowed-deferral contract violation PHASE 2 emits.**
- L1103 — **step 5's Fix / File / Skip gate alone** / **`Fix in this session`** / **aggregate**
- L1103 — **fires per challenged finding** / **firing order equals the reviewer's emission order**
- L1105 — **SR-6.7 ungated-route recovery gate.**
- L1105 — **The pinned strings read generically across both axes:** / **the routing misjudgment**
- L1106 — **original Trigger C tracker entry's `Follow-up Issue` field is updated in place**
- L1107 — **Trigger D**
- L1109 — **SR-4.6 under-enumeration recovery gate.** / **same three-choice gate shape**
- L1111 — **Trigger D**

Skeleton-internal labels other text points at (PHASE names, tags, sentinel strings):

- L967 `PHASE 1`, L980 `PHASE 2`, L1000 `PHASE 3`, L1017 `PHASE 4`, L1028 `PHASE 5`, L1032 `PHASE 6`
- L998/L1013/L1023/L1056 `[compromise-challenge]`; L1057 `[design]`; L1057 `[defect]`
- L1064 `no issues found`; L1075 `Post-completion review: no issues found`
- L1078 `Post-completion review found [N] issues. How would you like to handle them?`

## Rationale-only spans

Whole lines (or near-whole lines) with no executable rule:

- L905 (second clause only): orchestrator dispatches, not carries prose — borderline; first clause is a definition.
- L928 (second sentence): no Agent shutdown; bookkeeping only.
- L933 (second sentence): independent gate, separate from cycles.
- L959-L961 (skeleton): fresh-eyes review, no run context.
- L1014-L1015 (skeleton): why axis (ii) is required.
- L1023-L1026 (skeleton): PHASE 3 vs PHASE 4 complementarity.
- L1060-L1062 (skeleton, partial): depth tag informative here.
- L1114 (first sentence): SR-4.6 mirrors SR-6.7 shape.

Embedded rationale clauses inside rule-bearing lines (not separable by line range): L898 (no-other-carrier, missing-list-check reachability, Section 3 needs no qualification), L912 (findings span whole Bee), L913 (per-Task field already printed), L918 (uniform Fix / File / Encode routing; gate fires empty), L920 (wedging Clause 2), L924 (redelivery landed), L926 (round-count derivation), L935 (lane-scoped skills), L937 (team-lead bias), L1089 (scopes don't fit), L1093 (Section 4.2 scope), L1095 (writer redo), L1103 (nothing to recover; prose-adherence fragility).

Approximate rationale-only total: ~14 whole or near-whole lines; the remainder is interleaved in dense paragraph lines.
