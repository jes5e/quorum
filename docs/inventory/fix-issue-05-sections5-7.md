# Rule inventory — `skills/quo-fix-issue/SKILL.md` lines 704–978 (Sections 5, 6, 7 incl. checkpoint, guard, aborted close-out)

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F5-001 | Section 5 is **Phase C** of the Reconcile step's phase ladder defined in Section 4. | definition | L706 `### 5. Review Loop` | - | Section 4 phase ladder | Section 4 | none | unknown | procedure |
| F5-002 | Run Section 5 only when the Phase B writers have returned AND no `aborted-*` TaskList task for this Issue is `pending`. | precondition | L706 `### 5. Review Loop` | - | Phase B writer returns; TaskList `aborted-*` tasks | Section 4 Phase C bullet | TaskList | no | procedure |
| F5-003 | Evaluate the aborted-marker conjunct by matching the `aborted-` name prefix plus status `pending`. | precondition | L706 `### 5. Review Loop` | - | TaskList | - | TaskList | no | procedure |
| F5-004 | Never dispatch the Code Reviewer in Phase C; it is dispatched in **Phase A**, alone, interleaved with the Engineer until the source is clean. | invariant | L706 `### 5. Review Loop` | - | - | Phase A, Section 4 | Agent | unknown | procedure |
| F5-005 | Section 5 carries the Code Reviewer's dispatch shape and TaskList name for Phase A to use, but not its trigger. | definition | L706 `### 5. Review Loop` | - | - | Phase A | none | no | procedure |
| F5-006 | Phase A borrows Section 5's feedback-consumption discipline in full — the "**Follow the trailer literally**" bullet and the ignored-feedback rule. | invariant | L706 `### 5. Review Loop` | - | F5-057, F5-067 | Phase A, "**Follow the trailer literally**" | none | no | procedure |
| F5-007 | The ignored-feedback rule (record each ignored item as a `defer-<short-suffix>` TaskList task with destination annotation at ignore time) is one of three ways Phase A may close with findings outstanding. | definition | L706 `### 5. Review Loop` | - | - | Phase A | TaskList | no | procedure |
| F5-008 | Apply the trailer bullet and the ignored-feedback rule to Code Reviewer Phase A returns exactly as to Phase C returns. | invariant | L706 `### 5. Review Loop` | - | Code Reviewer returns | Phase A, Phase C | none | no | procedure |
| F5-009 | Dispatch three concurrent ephemeral Agents: `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`, `Agent(subagent_type="pm", run_in_background=true)`. | command | L708 `### 5. Review Loop` | three Agent dispatches | Section 4 dispatch shape | Section 4 | Agent | unknown | procedure |
| F5-010 | Track each Phase C Agent via a TaskList task named `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`. | name-class | L708 `### 5. Review Loop` | TaskList tasks | Section 4 issue-scoped naming convention | Section 4 | TaskList | no | procedure |
| F5-011 | Dispatch the Phase A Code Reviewer as `Agent(subagent_type="code-reviewer", run_in_background=true)`, tracked as `code-reviewer-<issue-id>`. | command | L708 `### 5. Review Loop` | Agent dispatch; TaskList task | - | Phase A | Agent, TaskList | no | procedure |
| F5-012 | Only dispatch a reviewer whose corresponding implementer ran during this issue's implementation pass. | precondition | L710 `### 5. Review Loop` | - | which implementers ran | - | Agent | unknown | procedure |
| F5-013 | If the Test Writer Agent ran in Phase B, dispatch the test-reviewer Agent now. | precondition | L711 `### 5. Review Loop` | test-reviewer dispatch | Phase B Test Writer ran | Phase B | Agent | unknown | procedure |
| F5-014 | If the Doc Writer Agent ran in Phase B, dispatch the doc-reviewer Agent now. | precondition | L712 `### 5. Review Loop` | doc-reviewer dispatch | Phase B Doc Writer ran | Phase B | Agent | unknown | procedure |
| F5-015 | The Code Reviewer's conditional spawn lives in Phase A: if the Engineer Agent ran, run the Code Reviewer against its diff there before Phase B begins. | precondition | L713 `### 5. Review Loop` | code-reviewer dispatch | Engineer ran | Phase A, Phase B | Agent | no | procedure |
| F5-016 | Example: a doc-only fix dispatches only the doc-reviewer (no Code Reviewer); a code+test fix without Doc Writer dispatches Code Reviewer in Phase A and only test-reviewer here. | example | L715 `### 5. Review Loop` | - | - | Phase A | none | unknown | example |
| F5-017 | Always dispatch the Product Manager Agent per Issue regardless of which implementers ran (**PM is the exception to the conditional-spawn rules**). | invariant | L717 `### 5. Review Loop` | pm dispatch | - | Section 4 (Doc Writer always-dispatched pattern) | Agent | unknown | procedure |
| F5-018 | Dispatch the PM alongside the reviewers, not instead of any of them. | ordering | L717 `### 5. Review Loop` | - | - | - | Agent | unknown | procedure |
| F5-019 | Do not pre-judge spec-drift risk; the PM reads spec sources and short-circuits in `agents/pm.md` when no spec-drift surface exists. | invariant | L717 `### 5. Review Loop` | - | - | `agents/pm.md` | Agent | unknown | rationale |
| F5-020 | The PM dispatch prompt must include the Issue ID, the Issue body verbatim, and the Issue's `up_dependencies` array. | field-or-template | L719 `### 5. Review Loop` | PM prompt fields | bees ticket | - | bees | no | procedure |
| F5-021 | The PM dispatch prompt must include `<scoped-marker-resolver-path>`, filled at runtime so `agents/pm.md` can run its Scoped-marker check. | field-or-template | L719 `### 5. Review Loop` | PM prompt field | resolver path | "Scoped-marker PM dispatch wiring" in Section 4; `agents/pm.md` | none | unknown | procedure |
| F5-022 | The PM dispatch prompt must include `<compromise-tracker-path>`, this run's compromise-tracker path (same value Section 8 passes to the post-completion reviewer). | field-or-template | L719 `### 5. Review Loop` | PM prompt field | compromise-tracker path | Section 8 | none | unknown | procedure |
| F5-023 | **Pass the tracker path, not its contents**; `agents/pm.md` reads the file itself. | invariant | L719 `### 5. Review Loop` | - | tracker path | Section 8; `agents/pm.md` | none | unknown | procedure |
| F5-024 | The Phase C PM dispatch prompt must relay the Engineer's completeness evidence verbatim. | relay | L721 `### 5. Review Loop` | PM prompt section | Engineer return completeness list | "Code Reviewer dispatch — relay the Engineer's completeness evidence verbatim" in Section 4 | none | unknown | procedure |
| F5-025 | Rationale: the PM is a **second** `/quo-engineer-review` caller with no channel to the Phase A Code Reviewer and reviews a wider diff (includes Phase B changes). | rationale-only | L721 `### 5. Review Loop` | - | - | `/quo-engineer-review`; `agents/pm.md`; `Skill` tool | none | unknown | rationale |
| F5-026 | When any Engineer return for this Issue carried a completeness list, embed it verbatim under a labelled heading; recommended label `## Engineer's completeness evidence`. | field-or-template | L721 `### 5. Review Loop` | `## Engineer's completeness evidence` heading in PM prompt | Engineer completeness list | - | none | unknown | procedure |
| F5-027 | Embed the completeness list as text in the prompt like the Issue body; do not write it to a scratch file and pass a path. | invariant | L721 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-028 | Attribute each completeness list to its Phase A round when more than one Engineer round produced one. | relay | L721 `### 5. Review Loop` | attribution labels | Phase A round numbers | - | none | unknown | procedure |
| F5-029 | Separately from the list, state in the PM prompt that the assignment was sweep-shaped whenever it was. | relay | L721 `### 5. Review Loop` | sweep-shaped statement | assignment shape | `/quo-engineer-review` sweep-verification check | none | unknown | procedure |
| F5-030 | Sweep-shaped means a directive or Subtask body that directed a change at every site where some property holds. | definition | L721 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-031 | Rationale: `/quo-engineer-review` reports a missing list only when the invocation named the assignment sweep-shaped; an unnamed sweep silently loses the check. | rationale-only | L721 `### 5. Review Loop` | - | - | `/quo-engineer-review` | none | unknown | rationale |
| F5-032 | When no completeness list arrived, omit the `## Engineer's completeness evidence` heading (never emit an empty one) but still state sweep-shaped when it was. | relay | L721 `### 5. Review Loop` | - | - | `/quo-engineer-review` missing-list check | none | unknown | procedure |
| F5-033 | This relay MUST is not satisfiable on every path: a compaction landing after an Engineer return destroys that round's list. | recovery | L721 `### 5. Review Loop` | - | - | Code Reviewer dispatch (Section 4) | none | unknown | procedure |
| F5-034 | Apply the compaction loss per round, not per Issue: embed every list still in hand, each attributed; a destroyed round contributes nothing. | recovery | L721 `### 5. Review Loop` | - | surviving lists | - | none | unknown | procedure |
| F5-035 | Omit the `## Engineer's completeness evidence` heading only when **no** list survives. | recovery | L721 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-036 | When a list is missing due to compaction, any missing-list finding from the PM's `/quo-engineer-review` takes the compaction-artifact disposition stated at the Code Reviewer dispatch. | recovery | L721 `### 5. Review Loop` | - | PM findings | Code Reviewer dispatch (Section 4) | none | unknown | procedure |
| F5-037 | The Phase C PM dispatch prompt must relay the Analyst's `### Blast radius` verbatim. | relay | L723 `### 5. Review Loop` | `## Blast radius` in PM prompt | Section 3 approved proposal | "Code Reviewer dispatch — relay the Analyst's `### Blast radius` verbatim" in Section 4 | none | no | procedure |
| F5-038 | When Section 3's approved proposal carried `### Blast radius`, embed it verbatim under heading `## Blast radius` — one heading string at every hop, as text, never a scratch-file path. | relay | L723 `### 5. Review Loop` | `## Blast radius` heading | `### Blast radius` section | Section 3 | none | no | procedure |
| F5-039 | Relay `### Blast radius` even when it carries only the fixed empty line `No invariant added, removed, or weakened.`. | relay | L723 `### 5. Review Loop` | - | - | - | none | no | procedure |
| F5-040 | This Blast-radius relay MUST is satisfiable on every path: a compaction-stranded proposal is recovered by Section 4's Read-state step re-derivation before this dispatch. | rationale-only | L723 `### 5. Review Loop` | - | - | Section 4 Read-state step | none | no | rationale |
| F5-041 | `agents/pm.md` carries the PM-side half: forwarding the block into its `/quo-engineer-review` invocation under the same heading. | definition | L723 `### 5. Review Loop` | - | - | `agents/pm.md`; `/quo-engineer-review` | none | no | procedure |
| F5-042 | Yield after dispatching the reviewer Agents and the PM Agent; the harness fires the next tick on the `run_in_background=true` completion notification. | ordering | L725 `### 5. Review Loop` | - | Agent completion notification | Section 4 reconciliation-loop tick | Agent | unknown | procedure |
| F5-043 | The Section 4 reconciliation-loop tick covers Agent completion; there is no idle teammate to escalate to. | definition | L725 `### 5. Review Loop` | - | - | Section 4 | Agent | unknown | procedure |
| F5-044 | Dispatch roles; do not carry role prose — role contracts live in the role files. | invariant | L727 `### 5. Review Loop` | - | - | role files | none | unknown | procedure |
| F5-045 | **Code Reviewer** (`agents/code-reviewer.md`) reviews the Engineer's output against engineering standards; dispatched in **Phase A**, alone, looping with the Engineer. | definition | L729 `### 5. Review Loop` | - | - | `agents/code-reviewer.md`; Phase A | Agent | unknown | procedure |
| F5-046 | **Test Reviewer** (`agents/test-reviewer.md`) reviews the Test Writer's output against test-quality standards. | definition | L730 `### 5. Review Loop` | - | - | `agents/test-reviewer.md` | Agent | unknown | procedure |
| F5-047 | **Doc Reviewer** (`agents/doc-reviewer.md`) reviews the Doc Writer's output against documentation standards. | definition | L731 `### 5. Review Loop` | - | - | `agents/doc-reviewer.md` | Agent | unknown | procedure |
| F5-048 | **Product Manager** (`agents/pm.md`) reviews the fix against the spec source (Issue body plus PRD/SDD paths from CLAUDE.md `## Documentation Locations`, optionally Scoped-marker-narrowed via a Plan Bee in `up_dependencies`) and flags scope creep or divergence. | definition | L732 `### 5. Review Loop` | - | CLAUDE.md `## Documentation Locations`; `up_dependencies` | `agents/pm.md` | Agent | unknown | procedure |
| F5-049 | Issues filed by `/quo-file-issue` in default in-conversation mode carry no `reference_materials`; the body itself is the spec. | definition | L732 `### 5. Review Loop` | - | `reference_materials` | `/quo-file-issue` | none | no | procedure |
| F5-050 | Issues filed via `/quo-file-issue <url>`, `--reference <url>` / `--from-github <url>`, or this skill's URL-resolution sub-step carry `reference_materials` with external-URL `value` and `resolver` in {`github-issue`, `linear-issue`, `url`}; the PM fetches via `WebFetch`. | definition | L732 `### 5. Review Loop` | - | `reference_materials.value`, `.resolver` | `/quo-file-issue`; URL-resolution sub-step | none | no | procedure |
| F5-051 | A Plan Bee reached through `up_dependencies` may resolve `reference_materials` via `file-path` (Scoped-marker narrowing applies) or `bees` (walk the Spec Bee's `t1=Doc` children). | definition | L732 `### 5. Review Loop` | - | `reference_materials` resolvers | - | bees | unknown | procedure |
| F5-052 | `agents/pm.md` is the authoritative spec for the `file-path`, `bees`, and external-URL resolver paths; body-as-spec is the fallback when `reference_materials` is null/empty. | definition | L732 `### 5. Review Loop` | - | - | `agents/pm.md` | none | unknown | procedure |
| F5-053 | The PM self-short-circuits per `agents/pm.md` when the collective spec sources carry no substantive content. | definition | L732 `### 5. Review Loop` | - | - | `agents/pm.md` | none | unknown | procedure |
| F5-054 | PM model is Opus (always). | definition | L732 `### 5. Review Loop` | - | - | - | Agent | yes | procedure |
| F5-055 | Get the feedback and make a judgement call about whether that work must be done. | choice-set | L734 `### 5. Review Loop` | routing decision | review skill outputs | - | none | unknown | procedure |
| F5-056 | Each review skill (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a routing trailer (`**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`) plus a counter-anchor clause. | definition | L734 `### 5. Review Loop` | - | review skill output | `/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review` | none | unknown | procedure |
| F5-057 | **Follow the trailer literally** — it is the authoritative routing prescription; the surrounding prose is reference context only. | invariant | L734 `### 5. Review Loop` | - | routing trailer | - | none | unknown | procedure |
| F5-058 | If feedback requires action, dispatch fresh ephemeral implementer Agents (Engineer / Test Writer / Doc Writer as needed) per Section 4's dispatch shape. | command | L735 `### 5. Review Loop` | implementer dispatches | findings | Section 4 | Agent | unknown | procedure |
| F5-059 | Re-dispatch the PM Agent per this section's dispatch shape if spec-alignment review needs another pass against the updated diff. | command | L735 `### 5. Review Loop` | pm dispatch | updated diff | - | Agent | unknown | procedure |
| F5-060 | Re-dispatches are ordered, not concurrent, whenever a fix path changes source; see part (g) of `### Orchestrator discipline: routing review findings` and Section 4's re-entry bullet. | ordering | L735 `### 5. Review Loop` | - | - | part (g) of `### Orchestrator discipline: routing review findings`; Section 4 Reconcile re-entry bullet; Phase A | Agent | unknown | procedure |
| F5-061 | **IMPORTANT**: stay in delegate mode and do not do the work yourself. | invariant | L736 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-062 | If the feedback was minor enough, you may choose to **NOT** re-dispatch the Product Manager on this iteration. | choice-set | L737 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-063 | If feedback does not require action, move on but MUST include the ignored feedback in the summary. | invariant | L738 `### 5. Review Loop` | summary `**Ignored Review Feedback**` content | ignored items | - | none | unknown | procedure |
| F5-064 | You may ignore feedback (to avoid an infinite loop) so long as you present it in the summary. | invariant | L739 `### 5. Review Loop` | - | - | - | none | unknown | procedure |
| F5-065 | A reviewer return whose findings are all `nit`s with chosen paths `trivial-tweak`s, shipped as such, closes **that reviewer's lane** after **one** implementer pass with no further review round. | ordering | L739 `### 5. Review Loop` | lane closure | finding severities/paths | **Severity bounds the loop** in `### Orchestrator discipline: routing review findings` | none | unknown | procedure |
| F5-066 | Count nits applied that way on the summary's **Reviews** line; do not list them as ignored feedback. | field-or-template | L739 `### 5. Review Loop` | `**Reviews**` line | nit count | - | none | unknown | procedure |
| F5-067 | Record each ignored item as a `defer-<short-suffix>` TaskList task at the moment of the ignore decision. | command | L740 `### 5. Review Loop` | `defer-*` TaskList task | ignore decision | Section 4 "TaskList naming convention" | TaskList | unknown | procedure |
| F5-068 | Set the `defer-*` task's `metadata.activity` to the feedback's one-line description and its status to `pending`. | field-or-template | L740 `### 5. Review Loop` | `metadata.activity`; status `pending` | feedback text | - | TaskList | unknown | procedure |
| F5-069 | Record the PM's destination annotation — `addressed-now-in-this-Task` (read as "addressed-now-in-this-Issue"), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — in the same `metadata.activity` string. | field-or-template | L740 `### 5. Review Loop` | `metadata.activity` destination | PM Final report | `agents/pm.md` Final report contract; generic-naming note | TaskList | unknown | procedure |
| F5-070 | For ignored reviewer-feedback items, the Director MUST annotate `metadata.activity` with one of the three destination labels when creating the `defer-*` task. | invariant | L740 `### 5. Review Loop` | `metadata.activity` destination | Director judgement | `agents/pm.md` destination vocabulary | TaskList | unknown | procedure |
| F5-071 | The destination annotation is required, not optional; it lets Section 7.5's deferral-hygiene gate route reviewer and PM items uniformly through Fix / File / Encode. | invariant | L740 `### 5. Review Loop` | - | - | Section 7.5 | TaskList | unknown | procedure |
| F5-072 | Vague framings without a named destination (e.g., "defer to later") are forbidden. | invariant | L740 `### 5. Review Loop` | - | - | `agents/pm.md` anti-pattern rule | none | unknown | procedure |
| F5-073 | Rationale: this record-creating step is the load-bearing source for Section 7.5's gate; without it the gate fires empty. | rationale-only | L740 `### 5. Review Loop` | - | - | Section 7.5 | none | unknown | rationale |
| F5-074 | Section 6 is **informational confirmation** on every Issue — never load-bearing orchestrator-direct work. | invariant | L744 `### 6. Verify docs are still accurate` | - | - | Section 5, Section 7 | none | unknown | procedure |
| F5-075 | Confirm the PM's verdict has been captured in the per-issue summary and proceed to Section 7. | command | L744 `### 6. Verify docs are still accurate` | confirmation | PM verdict | Section 7 | none | unknown | procedure |
| F5-076 | The PM verdict is either a deep review or the one-line short-circuit `no spec drift surface to review for this Issue`; either lands in the per-issue summary. | definition | L744 `### 6. Verify docs are still accurate` | - | PM Final report | `agents/pm.md` | none | unknown | procedure |
| F5-077 | If the Issue body carried `## Doc divergence noted`, **confirm** the Section 4 Doc Writer pass consumed it (named file/section matches post-fix behavior); do not re-discover the divergence. | command | L746 `### 6. Verify docs are still accurate` | confirmation | Issue body `## Doc divergence noted`; doc files | Section 4 | none | no | procedure |
| F5-078 | Section 6 never performs orchestrator-direct doc updates; doc changes are the Doc Writer's lane per `agents/doc-writer.md`. | invariant | L748 `### 6. Verify docs are still accurate` | - | - | `agents/doc-writer.md`; Section 4 | none | unknown | procedure |
| F5-079 | Report: the PM's spec-alignment verdict (deep review or `no spec drift surface to review for this Issue`) and confirmation it is captured in the per-issue summary. | field-or-template | L750 `### 6. Verify docs are still accurate` | report bullet | PM verdict | Section 5; `agents/pm.md` | none | unknown | procedure |
| F5-080 | Report: when `## Doc divergence noted` was present, confirmation the Doc Writer pass consumed it; otherwise mark this bullet N/A. | field-or-template | L751 `### 6. Verify docs are still accurate` | report bullet | Issue body | Section 4 | none | no | procedure |
| F5-081 | Step 1: mark the issue's bees ticket `status=done` before committing. | ordering | L757 `### 7. After Issue is fixed` | status flip | - | - | bees | unknown | procedure |
| F5-082 | **Re-read the Issue's current status first** (`bees show-ticket --ids <issue-id>`) and skip `bees update-ticket --status done` if already `done`. | precondition | L757 `### 7. After Issue is fixed` | idempotent status flip | ticket status | - | bees | unknown | procedure |
| F5-083 | Rationale: workers occasionally flip the status themselves, so the close-out flip must be idempotent rather than fail or double-flip. | rationale-only | L757 `### 7. After Issue is fixed` | - | - | - | none | unknown | rationale |
| F5-084 | The bees CLI writes the status to the on-disk record under the resolved Issues hive path; when in-repo, that change is staged in the per-issue commit at step 2.3. | definition | L757 `### 7. After Issue is fixed` | working-tree change | Issues hive path | step 2.3 | bees, git | unknown | procedure |
| F5-085 | Step 2: create one git commit for the Issue, including any doc updates. | command | L758 `### 7. After Issue is fixed` | git commit | - | - | git | yes | procedure |
| F5-086 | **NEVER push to remote — committing only.** | invariant | L758 `### 7. After Issue is fixed` | - | - | - | git | yes | procedure |
| F5-087 | Step 2.1: run the **Format** command from CLAUDE.md `## Build Commands` to normalize formatting. | command | L759 `### 7. After Issue is fixed` | formatted files | CLAUDE.md `## Build Commands` `Format` | - | Bash | yes | procedure |
| F5-088 | Step 2.2: run `git status` to see all modified and untracked files. | command | L760 `### 7. After Issue is fixed` | file list | working tree | - | git | yes | procedure |
| F5-089 | Step 2.3: stage files related to this issue's code, test, and doc changes — agent-reported files plus formatting changes to files those agents touched. | command | L761 `### 7. After Issue is fixed` | staged files | agent reports; `git status` | - | git | yes | procedure |
| F5-090 | Only if the Issues hive lives inside this repo, also stage the per-issue directory under the resolved Issues hive path so the `open → done` flip and body updates land in the same commit. | command | L761 `### 7. After Issue is fixed` | staged hive directory | Issues hive path | - | git, bees | yes | procedure |
| F5-091 | The Issues-hive scoping mirrors `quo-execute`'s Plans-hive scoping in its After-Task commit step. | rationale-only | L761 `### 7. After Issue is fixed` | - | - | `quo-execute` After-Task commit step | none | yes | rationale |
| F5-092 | To learn the in-repo Issues hive path, run `hive_commit.py`'s NON-MUTATING `resolve-hive-paths` mode, resolving its sibling path as the Section 7.5 Encode step does. | command | L761 `### 7. After Issue is fixed` | hive path | skill base directory | Section 7.5 Encode step; `hive_commit.py` | Bash | yes | procedure |
| F5-093 | The helper emits the Issues hive's absolute path when it is inside this repo, or nothing when outside (stage no hive path then). | definition | L761 `### 7. After Issue is fixed` | - | helper stdout | - | Bash | yes | procedure |
| F5-094 | Run exactly: POSIX `python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues`; PowerShell `python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues`, as a single literal Bash call. | command | L763-L771 `### 7. After Issue is fixed` | hive path | skill base directory | `hive_commit.py` | Bash | yes | procedure |
| F5-095 | When the helper emits a path, append `/<issue-id>` and `git add <emitted-issues-path>/<issue-id>` alongside judgement-selected source files. | command | L773 `### 7. After Issue is fixed` | staged per-issue directory | helper output | - | git | yes | procedure |
| F5-096 | **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes. | invariant | L773 `### 7. After Issue is fixed` | - | - | - | git | yes | procedure |
| F5-097 | Review each modified file and stage it only if plausibly related to this issue. | command | L773 `### 7. After Issue is fixed` | staged files | `git status` | - | git | yes | procedure |
| F5-098 | Rationale: per-issue `<issue-id>` scoping on the `git add` path keeps other issues' record drift out; stale state is caught by the next `/quo-fix-issue` run. | rationale-only | L773 `### 7. After Issue is fixed` | - | - | `/quo-fix-issue` | none | no | rationale |
| F5-099 | Step 2.4: commit with a descriptive message per system/project git guidance. | command | L774 `### 7. After Issue is fixed` | git commit | - | - | git | yes | procedure |
| F5-100 | The commit subject line MUST follow the literal format `Fix issue: <title> (<issue-id>)` (e.g., `Fix issue: Tighten dispatch contract gap (b.abc)`). | field-or-template | L774 `### 7. After Issue is fixed` | commit subject | issue title/id | Section 9 | git | no | procedure |
| F5-101 | Rationale: Section 9's post-hoc SHA-derivation fallback `--grep`-filters on the literal `(<issue-id>)` token, so the suffix is a contract, not style. | rationale-only | L774 `### 7. After Issue is fixed` | - | - | Section 9 | none | no | rationale |
| F5-102 | Step 3: mark the per-issue TaskList tasks `completed` and clear them from the active set, grouped by dispatching phase. | command | L775 `### 7. After Issue is fixed` | TaskList status flips | Section 4 issue-scoped naming | Section 4 | TaskList | unknown | procedure |
| F5-103 | Sweep the Section 3 Analyst task `analyst-<issue-id>` (plus `analyst-<issue-id>-rev<n>` revisions) — already `completed` on return, so a no-op. | name-class | L777 `### 7. After Issue is fixed` | - | TaskList | Section 3 | TaskList | no | procedure |
| F5-104 | Sweep the **Phase A** tasks `engineer-<issue-id>` and `code-reviewer-<issue-id>`. | name-class | L778 `### 7. After Issue is fixed` | TaskList status flips | TaskList | Section 4 Reconcile step; Section 5 | TaskList | no | procedure |
| F5-105 | Sweep the **Phase B** tasks `test-writer-<issue-id>` and `doc-writer-<issue-id>`. | name-class | L779 `### 7. After Issue is fixed` | TaskList status flips | TaskList | - | TaskList | no | procedure |
| F5-106 | Sweep the **Phase C** tasks `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`. | name-class | L780 `### 7. After Issue is fixed` | TaskList status flips | TaskList | Section 5 | TaskList | no | procedure |
| F5-107 | Sweep any **aborted-writer redelivery markers** `aborted-test-writer-<issue-id>`, `aborted-doc-writer-<issue-id>` and mark them `completed`. | name-class | L781 `### 7. After Issue is fixed` | TaskList status flips | TaskList | movement-report rung | TaskList | no | procedure |
| F5-108 | Rationale: a marker left `pending` past close-out would hold Phase C shut on a later re-entry into this Issue. | rationale-only | L781 `### 7. After Issue is fixed` | - | - | Phase C | none | no | rationale |
| F5-109 | **Close out round-discriminated names too**: `-r<n>`-suffixed tasks (`engineer-<issue-id>-r1`, `code-reviewer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`, …). | name-class | L783 `### 7. After Issue is fixed` | TaskList status flips | TaskList | - | TaskList | no | procedure |
| F5-110 | Sweep by name **prefix**, not by the exact names listed, so no round is left behind. | invariant | L783 `### 7. After Issue is fixed` | - | TaskList | - | TaskList | unknown | procedure |
| F5-111 | Perform no Agent shutdown — cold dispatches from Sections 3, 4, and 5 complete-and-exit on return. | definition | L783 `### 7. After Issue is fixed` | - | - | Sections 3, 4, 5 | Agent | unknown | procedure |
| F5-112 | **The aborted path runs this same sweep at its own site** (`#### Aborted-Issue close-out`); any name added to this list belongs in that step's list too. | invariant | L785 `### 7. After Issue is fixed` | - | - | `#### Aborted-Issue close-out` | none | no | procedure |
| F5-113 | Step 4: output the per-issue summary block in the markdown template given. | field-or-template | L786-L798 `### 7. After Issue is fixed` | summary block | all fields below | - | none | unknown | procedure |
| F5-114 | Summary heading: `## Issue [x] of [total] done: [issue-title]`. | field-or-template | L789 `### 7. After Issue is fixed` | heading | batch position; title | - | none | no | procedure |
| F5-115 | Summary field: `**Issue**: <issue-id>`. | field-or-template | L791 `### 7. After Issue is fixed` | field | issue id | - | none | no | procedure |
| F5-116 | Summary field: `**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])`. | field-or-template | L792 `### 7. After Issue is fixed` | field | staged files | - | none | unknown | procedure |
| F5-117 | Summary field: `**Reviews**: [Code review: X issues found/None needed \| Test review: Y issues found/None needed \| Docs review: Z issues found/None needed \| N nits applied without re-review (or "count unavailable post-compaction"), when any]`. | field-or-template | L793 `### 7. After Issue is fixed` | field | reviewer returns; nit count | - | none | unknown | procedure |
| F5-118 | Summary field: `**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed]`, using the actual path from CLAUDE.md "Documentation Locations", not literal "SDD"/"PRD". | field-or-template | L794 `### 7. After Issue is fixed` | field | CLAUDE.md `## Documentation Locations` | - | none | unknown | procedure |
| F5-119 | Summary field: `**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]`. | field-or-template | L795 `### 7. After Issue is fixed` | field | ignored items | - | none | unknown | procedure |
| F5-120 | Summary field: `**Second-order effects**: [the relayed `### Second-order effects` narrative]`, rendered per the "Second-order effects" logic. | field-or-template | L796 `### 7. After Issue is fixed` | field | relayed narratives | - | none | unknown | procedure |
| F5-121 | Summary field: `[**Accepted compromises** — rendered per the "Accepted compromises" logic, or OMITTED ENTIRELY when the tracker is empty or absent]`. | field-or-template | L797 `### 7. After Issue is fixed` | field | compromise tracker | - | none | unknown | procedure |
| F5-122 | The `**Second-order effects**` field is the **destination** for `/quo-engineer-review`'s `### Second-order effects` narrative via the chain `/quo-engineer-review` → Code Reviewer (`agents/code-reviewer.md`) and/or PM (`agents/pm.md`) → this field. | relay | L800 `### 7. After Issue is fixed` | field | Code Reviewer / PM returns | `/quo-engineer-review`; `agents/code-reviewer.md`; `agents/pm.md` | none | unknown | procedure |
| F5-123 | **Collect every relayed narrative for this Issue** — each Phase A Code Reviewer return (one per round) and the Phase C PM Final report's `### Second-order effects`. | command | L802 `### 7. After Issue is fixed` | collected bullets | Code Reviewer returns; PM Final report | Phase A, Phase C | none | unknown | procedure |
| F5-124 | Render the second-order bullets **verbatim**; do not re-summarize, re-rank, or merge them into the `**Reviews**` line. | invariant | L802 `### 7. After Issue is fixed` | - | - | - | none | unknown | procedure |
| F5-125 | **Attribute each block** when more than one source contributed, with a short scope label (round or relaying role) per `agents/pm.md`'s Final report shape. | command | L803 `### 7. After Issue is fixed` | attribution labels | - | `agents/pm.md` | none | unknown | procedure |
| F5-126 | **De-duplicate exact repeats** (keep the earliest attribution); keep near-duplicates that differ in substance separately. | command | L804 `### 7. After Issue is fixed` | - | - | `/quo-engineer-review` | none | unknown | procedure |
| F5-127 | When every source reported `No second-order effects identified.` or no emitting review ran, render the single line `None identified.`; do **not** omit the field. | field-or-template | L805 `### 7. After Issue is fixed` | `None identified.` | - | - | none | unknown | procedure |
| F5-128 | The `**Second-order effects**` field is unconditional, unlike `**Accepted compromises**`. | invariant | L805 `### 7. After Issue is fixed` | - | - | - | none | unknown | procedure |
| F5-129 | The `**Accepted compromises**` surface reflects the session-scoped compromise tracker's (Section 7.5 `#### Session-scoped compromise tracker`) current contents at render time. | definition | L807 `### 7. After Issue is fixed` | - | tracker file | Section 7.5 `#### Session-scoped compromise tracker` | none | unknown | procedure |
| F5-130 | **Read the run's tracker file via the `Read` tool** at `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`/tmp/.quorum/...` POSIX, `%TEMP%\.quorum\...` Windows). | command | L809 `### 7. After Issue is fixed` | - | tracker path | Section 7.5 path convention | none | unknown | procedure |
| F5-131 | If the tracker path is no longer in view, recover it from the run-state manifest's **Compromise tracker** field (Section 1 `#### Write the run-state manifest`); use `Read`, no shell. | recovery | L809 `### 7. After Issue is fixed` | - | run-state manifest | Section 1 `#### Write the run-state manifest` | none | unknown | procedure |
| F5-132 | **Omit the section entirely when there is nothing to show**: if the file does not exist OR has no `## Compromise <n>` entries, render no `**Accepted compromises**` line, no empty heading, no `N/A`, no placeholder. | invariant | L810 `### 7. After Issue is fixed` | - | `Read` result | - | none | unknown | procedure |
| F5-133 | Treat "file absent" and "file present but empty" identically: omit. | invariant | L810 `### 7. After Issue is fixed` | - | - | - | none | unknown | procedure |
| F5-134 | Rationale: an absent file is uncommon since ungated picks among ≥2 paths append an entry; Trigger C's lone-`trivial-tweak` carve-out is the only ungated route appending nothing. | rationale-only | L810 `### 7. After Issue is fixed` | - | - | Trigger C | none | unknown | rationale |
| F5-135 | **When entries exist, render one bullet per `## Compromise <n>` entry**, surfacing exactly four user-facing fields. | field-or-template | L811 `### 7. After Issue is fixed` | bullets | tracker entries | - | none | unknown | procedure |
| F5-136 | Bullet field: the **finding** — the entry's `Finding (verbatim)`. | field-or-template | L812 `### 7. After Issue is fixed` | field | tracker entry | - | none | unknown | procedure |
| F5-137 | Bullet field: the **chosen path** — the entry's `Decision`. | field-or-template | L813 `### 7. After Issue is fixed` | field | tracker entry | - | none | unknown | procedure |
| F5-138 | Bullet field: the **rationale** — the entry's `Rationale`. | field-or-template | L814 `### 7. After Issue is fixed` | field | tracker entry | - | none | unknown | procedure |
| F5-139 | Bullet field: the **follow-up Issue ID** — the entry's `Follow-up Issue` (a ticket ID, or `none`). | field-or-template | L815 `### 7. After Issue is fixed` | field | tracker entry | - | none | unknown | procedure |
| F5-140 | Do NOT surface the fifth entry field `Fix paths surfaced by reviewer`. | invariant | L817 `### 7. After Issue is fixed` | - | - | - | none | unknown | procedure |
| F5-141 | **Volume (>10 entries)**: surface ALL entries in full; do NOT truncate, summarize away, or elide any. | invariant | L818 `### 7. After Issue is fixed` | - | - | - | none | unknown | procedure |
| F5-142 | With >10 entries, precede the bullets with a short prologue noting the volume (e.g., "N compromises were accepted during this run:"). | field-or-template | L818 `### 7. After Issue is fixed` | prologue | entry count | - | none | unknown | procedure |
| F5-143 | This surface only **reads** the tracker — never writes, appends to, or deletes it; the write side is Section 7.5's append triggers. | invariant | L820 `### 7. After Issue is fixed` | - | - | Section 7.5 | none | unknown | procedure |
| F5-144 | Step 5: continue to Section 7.5 first; once that gate closes, run the **Issue-boundary state-externalization checkpoint**; then branch on mode. | ordering | L822 `### 7. After Issue is fixed` | - | Section 7.5 gate result | Section 7.5; `#### Issue-boundary state-externalization checkpoint` | none | unknown | procedure |
| F5-145 | **Single mode** — proceed to Section 8. | ordering | L823 `### 7. After Issue is fixed` | - | run mode | Section 8 | none | unknown | procedure |
| F5-146 | **Batch mode (`all` or list mode) with the batch exhausted** — proceed to Section 8. | ordering | L824 `### 7. After Issue is fixed` | - | run mode; batch | Section 8 | none | no | procedure |
| F5-147 | **Batch mode with a next Issue still remaining** — run the **Context-window boundary guard** (fires ONLY on this path); if it did not stop the run, go back to step 2 for the next issue. | ordering | L825 `### 7. After Issue is fixed` | - | run mode; guard result | `#### Context-window boundary guard`; step 2 | none | unknown | procedure |
| F5-148 | `#### Issue-boundary state-externalization checkpoint` is the canonical anchor name; **it is a definition, not a step in Section 7's linear flow** — do not run it because reading reached the heading. | definition | L829 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 7 step 5; `#### Aborted-Issue close-out` | none | unknown | procedure |
| F5-149 | Run the checkpoint only where step 5 or `#### Aborted-Issue close-out` calls for it, always after Section 7.5's deferral-hygiene gate has closed. | ordering | L829 `#### Issue-boundary state-externalization checkpoint` | - | Section 7.5 gate closure | Section 7.5 | none | unknown | procedure |
| F5-150 | On the aborted path the Issue is left `open` with no commit; an `open` ticket plus absent commit is the durable record that the Issue was not fixed. | definition | L831 `#### Issue-boundary state-externalization checkpoint` | - | - | `#### Aborted-Issue close-out` | none | no | procedure |
| F5-151 | The checkpoint's job is to **verify that invariant and refresh the durable carriers** so any harness compaction can be re-derived from disk. | definition | L831 `#### Issue-boundary state-externalization checkpoint` | - | - | - | none | unknown | procedure |
| F5-152 | Durable carrier: **the Issue's bees ticket**, flipped `open` → `done` at step 1; re-readable via `bees show-ticket`. | definition | L837 `#### Issue-boundary state-externalization checkpoint` | - | - | step 1 | bees | no | procedure |
| F5-153 | Durable carrier: **the per-issue git commit** with the `(<issue-id>)` token in its subject; re-readable via `git log` / `git diff`. | definition | L838 `#### Issue-boundary state-externalization checkpoint` | - | - | step 2 | git | no | procedure |
| F5-154 | Durable carrier: **the session-scoped compromise tracker** (Section 7.5 `#### Session-scoped compromise tracker`); re-readable via `Read`. | definition | L839 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 7.5 `#### Session-scoped compromise tracker` | none | yes | procedure |
| F5-155 | Durable carrier: **the `defer-*` TaskList ledger**, emptied by Section 7.5's hard-stop gate before the checkpoint; re-readable by walking the TaskList. | definition | L840 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 7.5 | TaskList | yes | procedure |
| F5-156 | Durable carrier: **the run-state manifest** (Section 1 `#### Write the run-state manifest`), carrying ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress; re-readable via `Read`. | definition | L841 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 1 `#### Write the run-state manifest` | none | yes | procedure |
| F5-157 | Run the three checkpoint steps only when step 5 or `#### Aborted-Issue close-out` step 3 calls for it, ahead of whatever the invoking site does next. | ordering | L843 `#### Issue-boundary state-externalization checkpoint` | - | - | step 5; `#### Aborted-Issue close-out` step 3; Section 8 | none | unknown | procedure |
| F5-158 | Every checkpoint step is a tool call the orchestrator can actually make — bees query, git command, file read, TaskList walk, file write. | invariant | L843 `#### Issue-boundary state-externalization checkpoint` | - | - | - | bees, git, TaskList | unknown | procedure |
| F5-159 | Step 1 — **Verify the carriers.** Do all four verifications. | command | L845 `#### Issue-boundary state-externalization checkpoint` | verification results | carriers | - | bees, git, TaskList | unknown | procedure |
| F5-160 | **Aborted-path qualification**: when invoked from `#### Aborted-Issue close-out`, confirm the Issue reads **`open`** (not `done`) and expect **no** commit — skip the `(<issue-id>)` subject-token search entirely; tracker and TaskList checks run unchanged. | recovery | L845 `#### Issue-boundary state-externalization checkpoint` | - | invoking site | `#### Aborted-Issue close-out` | bees | no | procedure |
| F5-161 | Re-read the just-fixed Issue in bees and confirm it reads `done`. | command | L846 `#### Issue-boundary state-externalization checkpoint` | - | bees ticket | - | bees | no | procedure |
| F5-162 | Confirm the per-issue commit via `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (same form as Section 9 step 4's re-derive path; identical on POSIX and PowerShell). | command | L847 `#### Issue-boundary state-externalization checkpoint` | - | `<pre-session-sha>`; commit subjects | Section 9 step 4 | git | no | procedure |
| F5-163 | Resolve `<pre-session-sha>` by `Read`ing the run-state manifest's **Pre-session SHA** field — not from a value quoted earlier in the conversation. | command | L847 `#### Issue-boundary state-externalization checkpoint` | - | run-state manifest **Pre-session SHA** | - | none | unknown | procedure |
| F5-164 | **Validate the manifest before trusting that field**: compare its **Unit scope** ordered Issue batch against this run's batch; if it names Issues this run is not working, treat the manifest as absent. | precondition | L847 `#### Issue-boundary state-externalization checkpoint` | - | manifest **Unit scope**; run batch | Section 1 `#### Write the run-state manifest` | none | unknown | procedure |
| F5-165 | On a stale/foreign manifest, ignore **Pre-session SHA**, bound the check with `HEAD~N` where N = Issues fixed so far this run, then let step 2 rewrite the manifest from this run's batch. | recovery | L847 `#### Issue-boundary state-externalization checkpoint` | - | fixed-Issue count | step 2 | git | unknown | procedure |
| F5-166 | **Do not use a bare `git log --oneline -1`** — Section 7.5's Encode branch may land an `Encode deferral: ...` commit on top of the per-issue commit. | invariant | L847 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 7.5 Encode branch | git | unknown | procedure |
| F5-167 | **Do not drop the `<pre-session-sha>..HEAD` bound** — an unscoped `--grep` can match a same-`(<issue-id>)` commit from an earlier run. | invariant | L847 `#### Issue-boundary state-externalization checkpoint` | - | - | - | git | unknown | procedure |
| F5-168 | An empty result from the ranged `--grep` is a real gap; a non-empty result is this run's per-issue commit wherever it sits. | definition | L847 `#### Issue-boundary state-externalization checkpoint` | gap determination | git output | - | git | unknown | procedure |
| F5-169 | `Read` the compromise-tracker file at the manifest's **Compromise tracker** path and confirm every compromise accepted on this Issue has an entry. | command | L848 `#### Issue-boundary state-externalization checkpoint` | - | manifest **Compromise tracker**; tracker file | - | none | yes | procedure |
| F5-170 | **A `Read` reporting that the file does not exist is not by itself a gap** — the tracker is created only on its first append trigger. | precondition | L848 `#### Issue-boundary state-externalization checkpoint` | - | `Read` result | - | none | yes | procedure |
| F5-171 | Do not read an absent tracker as the expected state; read it as "nothing was appended" and check that against what this Issue actually did. | command | L848 `#### Issue-boundary state-externalization checkpoint` | - | Issue's routing history | - | none | unknown | procedure |
| F5-172 | Treat absence as a gap only if a compromise **was accepted**, or an ungated path pick **that Trigger C requires an entry for** was dispatched, and no entry/file exists. | precondition | L848 `#### Issue-boundary state-externalization checkpoint` | gap determination | Trigger C rules | Trigger C | none | unknown | procedure |
| F5-173 | Rationale: a unit whose sole ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less; reporting a gap would contradict Trigger C. | rationale-only | L848 `#### Issue-boundary state-externalization checkpoint` | - | - | Trigger C | none | unknown | rationale |
| F5-174 | Walk the TaskList and confirm every per-issue role task and `gate-*` task is `completed` and the `defer-*` active set is empty. | command | L849 `#### Issue-boundary state-externalization checkpoint` | - | TaskList | - | TaskList | yes | procedure |
| F5-175 | Fix any verification gap **now** rather than carrying it forward in conversation. | invariant | L851 `#### Issue-boundary state-externalization checkpoint` | gap fixes | verification results | - | bees, git, TaskList | yes | procedure |
| F5-176 | Step 2 — **Rewrite the run-state manifest** per Section 1, recording the just-fixed Issue's ID and commit SHA under progress and the next Issue's ID as next unit (or `none` in single mode / batch exhausted). | command | L852 `#### Issue-boundary state-externalization checkpoint` | run-state manifest | Issue id; commit SHA; batch | Section 1 `#### Write the run-state manifest` | none | yes | procedure |
| F5-177 | **On the aborted path**, record the Issue as `<issue-id>: aborted — no commit; Issue left open` and set the next unit by the same batch rule. | field-or-template | L852 `#### Issue-boundary state-externalization checkpoint` | manifest **Progress** entry | - | `#### Aborted-Issue close-out` | none | no | procedure |
| F5-178 | Step 3 — **Re-read, do not recall, at every dispatch on the next Issue**: `bees show-ticket` its body/status and `Read` the manifest for ordered batch, isolation strategy, tracker path, `<pre-session-sha>`. | invariant | L853 `#### Issue-boundary state-externalization checkpoint` | - | bees ticket; run-state manifest | - | bees | yes | procedure |
| F5-179 | The next Issue's design directive comes from its own Section 3 Analyst pass, never from the previous Issue's. | invariant | L853 `#### Issue-boundary state-externalization checkpoint` | - | - | Section 3 | Agent | no | procedure |
| F5-180 | Carry **no** value forward from the prior Issue; if a needed fact is not readable from a carrier, stop and write it into one before dispatching anything. | invariant | L853 `#### Issue-boundary state-externalization checkpoint` | carrier write | carriers | - | none | yes | procedure |
| F5-181 | **What this checkpoint does not do**: it does not clear, compact, or reclaim the orchestrator's context and must never be narrated as if it did. | invariant | L855 `#### Issue-boundary state-externalization checkpoint` | - | - | - | none | yes | procedure |
| F5-182 | Rationale: no model-invocable self-clearing exists; the harness compacts on its own; the checkpoint makes any compaction lossless. | rationale-only | L855 `#### Issue-boundary state-externalization checkpoint` | - | - | - | none | yes | rationale |
| F5-183 | The guard is a **definition co-located with the Issue-boundary checkpoint above**; run it only on the **one continuing, in-session path** (batch mode with a next Issue), after the checkpoint and before looping to step 2. | ordering | L859 `#### Context-window boundary guard` | - | run mode; checkpoint completion | step 5; step 2 | none | yes | procedure |
| F5-184 | The guard does **NOT** run on run-ending paths: single mode and batch-exhausted mode both proceed to Section 8 without it. | invariant | L859 `#### Context-window boundary guard` | - | run mode | Section 8 | none | yes | procedure |
| F5-185 | **`#### Aborted-Issue close-out` below does not invoke it either** — an aborted Issue stops the batch at its step 4. | invariant | L859 `#### Context-window boundary guard` | - | - | `#### Aborted-Issue close-out` step 4 | none | no | procedure |
| F5-186 | Do not inherit the checkpoint's unconditionality; a single-Issue run crosses no boundary and never invokes the guard. | invariant | L859 `#### Context-window boundary guard` | - | - | - | none | yes | procedure |
| F5-187 | **What the guard reads**: an **external gauge file** from a separate status-line producer; it does not and cannot measure the orchestrator's own token usage. | definition | L861 `#### Context-window boundary guard` | - | gauge file | - | none | yes | procedure |
| F5-188 | The only reclamation lever is a **fresh session**; the guard never instructs the orchestrator to clear or compact its own context. | invariant | L861 `#### Context-window boundary guard` | - | - | fresh-session-per-phase recommendation at run close-out | none | yes | procedure |
| F5-189 | The guard's job is to stop the batch at this clean Issue boundary before auto-compaction fires partway through the next Issue. | definition | L861 `#### Context-window boundary guard` | - | - | - | none | yes | rationale |
| F5-190 | **Ordering is load-bearing**: read the session id **first**, evaluate it, and only then decide whether any gate task is created (mirror Section 1's `#### Check session reasoning effort`). | ordering | L863 `#### Context-window boundary guard` | - | session id | Section 1 `#### Check session reasoning effort` | Bash | yes | procedure |
| F5-191 | Do NOT create a `gate-*` task before the reading is in hand; a stranded `pending` `gate-*` violates the two-step contract's yield-control discipline. | invariant | L863 `#### Context-window boundary guard` | - | - | two-step contract | TaskList | yes | procedure |
| F5-192 | **Step 1 — read the session id** with one literal command: POSIX `printenv CLAUDE_CODE_SESSION_ID`; PowerShell `Write-Output $env:CLAUDE_CODE_SESSION_ID`. | command | L865-L875 `#### Context-window boundary guard` | session id | `CLAUDE_CODE_SESSION_ID` | - | Bash | yes | procedure |
| F5-193 | **Trim any trailing whitespace or newline** from the session id before use (a trailing newline fails `--session-id` charset validation). | command | L877 `#### Context-window boundary guard` | trimmed session id | session id | - | none | yes | procedure |
| F5-194 | **Step 2 — session id unset or empty → skip the guard silently and continue** to the next Issue (back to Section 2); create no `gate-*` task, emit no output. | precondition | L879 `#### Context-window boundary guard` | - | session id | Section 2 | none | yes | procedure |
| F5-195 | The unset-session-id path is the ONLY silent-skip path (unsupported-CLI carve-out), matching Section 1's treatment of an unset `CLAUDE_EFFORT`. | invariant | L879 `#### Context-window boundary guard` | - | - | Section 1; `CLAUDE_EFFORT` | none | yes | procedure |
| F5-196 | **Step 3 — session id present**: resolve the gauge helper as `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (POSIX `/`, PowerShell `\`; base directory from the skill invocation header). | command | L881 `#### Context-window boundary guard` | helper path | skill base directory | `context_gauge.py` | none | yes | procedure |
| F5-197 | This is the same sibling-resolution discipline used for `scoped_marker_resolver.py` and `hive_commit.py`. | rationale-only | L881 `#### Context-window boundary guard` | - | - | `scoped_marker_resolver.py`; `hive_commit.py` | none | yes | rationale |
| F5-198 | Obtain the stop threshold with one literal call: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold`; PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold`. | command | L883-L893 `#### Context-window boundary guard` | threshold integer | helper | `context_gauge.py` | Bash | yes | procedure |
| F5-199 | Compare the reading against whatever integer the `stop-threshold` seam prints; the helper is the single definition site and prose never restates the number. | invariant | L895 `#### Context-window boundary guard` | - | threshold | - | none | yes | procedure |
| F5-200 | Read the current reading with one literal call: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>`; PowerShell `python "...\context_gauge.py" read --session-id <trimmed-session-id>`. | command | L897-L907 `#### Context-window boundary guard` | reading | trimmed session id | `context_gauge.py` | Bash | yes | procedure |
| F5-201 | **Step 4 — branch on the `read` output and its exit status**: `read` prints exactly one of an integer percentage, `no-reading`, `stale`, `missing` (exit `0` for all four); it exits `2` on a malformed gauge OR an invalid `--session-id`. | definition | L909 `#### Context-window boundary guard` | - | `read` stdout/exit | - | Bash | yes | procedure |
| F5-202 | The fresh-session resume command is `/quo-fix-issue all` for an `all` run, or `/quo-fix-issue <remaining-ids>` listing the still-unfixed subset (Issues not yet `done`) for a list run. | field-or-template | L909 `#### Context-window boundary guard` | resume command text | batch; ticket statuses | - | none | no | procedure |
| F5-203 | **Integer ≥ threshold → STOP** at this boundary: report the percentage, recommend resuming in a **fresh session** naming the exact resume command, then exit the skill (do not loop to step 2). | gate | L911 `#### Context-window boundary guard` | stop report | reading; threshold | - | none | yes | procedure |
| F5-204 | **Integer < threshold → continue** to the next Issue (back to step 2) with no output. | ordering | L912 `#### Context-window boundary guard` | - | reading | step 2 | none | yes | procedure |
| F5-205 | **`no-reading` → continue** to the next Issue (back to step 2) with no output — the transient fresh-but-null state. | ordering | L913 `#### Context-window boundary guard` | - | reading | step 2 | none | yes | procedure |
| F5-206 | **`stale` → STOP**: note the producer appears stalled, that recurring staleness means the operator should check their status-line producer, and recommend the fresh-session resume with the command. | gate | L914 `#### Context-window boundary guard` | stop report | reading | - | none | yes | procedure |
| F5-207 | Do NOT let `stale` fall through to continue. | invariant | L914 `#### Context-window boundary guard` | - | - | - | none | yes | procedure |
| F5-208 | Rationale: usage only grows within a session, so a stale number biases low and must not be trusted as headroom. | rationale-only | L914 `#### Context-window boundary guard` | - | - | - | none | yes | rationale |
| F5-209 | **Non-zero exit, or empty stdout → the same fail-safe stop-and-ask as `stale`** (an untrustworthy reading). | gate | L915 `#### Context-window boundary guard` | stop report | `read` exit/stdout | - | none | yes | procedure |
| F5-210 | Do NOT assume exit `2` implies a corrupt file — it also means an invalid `--session-id`. | invariant | L915 `#### Context-window boundary guard` | - | - | - | none | yes | procedure |
| F5-211 | Never fall through to continue on non-zero exit or empty stdout. | invariant | L915 `#### Context-window boundary guard` | - | - | - | none | yes | procedure |
| F5-212 | **`missing`** (no gauge file) → before stopping, check the persistent opt-out marker at `<tempdir>/.quorum/context-guard-opt-out` (`/tmp/.quorum/context-guard-opt-out` POSIX, `%TEMP%\.quorum\context-guard-opt-out` Windows). | command | L916 `#### Context-window boundary guard` | - | opt-out marker | - | Bash | yes | procedure |
| F5-213 | Existence check is one literal call: POSIX `test -f /tmp/.quorum/context-guard-opt-out`; PowerShell `Test-Path "$env:TEMP\.quorum\context-guard-opt-out"`. | command | L918-L926 `#### Context-window boundary guard` | marker presence | filesystem | - | Bash | yes | procedure |
| F5-214 | **If the marker is present → skip the guard silently and continue** to the next Issue (back to step 2). | ordering | L928 `#### Context-window boundary guard` | - | marker presence | step 2 | none | yes | procedure |
| F5-215 | **If absent → hard-stop via the two-step gate in step 5 below.** | gate | L928 `#### Context-window boundary guard` | - | marker absence | step 5 | none | yes | procedure |
| F5-216 | **Step 5 — the missing-reading gate** is reached only from the `missing`-and-no-marker branch. | precondition | L930 `#### Context-window boundary guard` | - | - | - | none | yes | procedure |
| F5-217 | Honor the two-step contract: **first** `TaskCreate` a `gate-askuserquestion-<short-suffix>` task naming this boundary context-guard gate (distinct suffix per fire, per Section 4's naming convention), **then** call `AskUserQuestion` in the same turn. | gate | L930 `#### Context-window boundary guard` | `gate-askuserquestion-<short-suffix>` task; AskUserQuestion | - | Section 4 TaskList naming convention gate-task entry | TaskList, AskUserQuestion | yes | procedure |
| F5-218 | Honor the yield-control discipline — do not yield while the gate task is `pending`/`in_progress`. | invariant | L930 `#### Context-window boundary guard` | - | - | - | TaskList | yes | procedure |
| F5-219 | Mark the `gate-*` task `completed` once the answer is consumed. | command | L930 `#### Context-window boundary guard` | TaskList status flip | AskUserQuestion answer | - | TaskList | yes | procedure |
| F5-220 | Question text must (a) state that the environment may override the operator's user-level status-line config, so no reading is being published. | field-or-template | L930 `#### Context-window boundary guard` | question text | - | - | AskUserQuestion | yes | procedure |
| F5-221 | Question text must (b) publish the gauge file contract: path `<tempdir>/.quorum/context-usage-<session_id>.json`, required `session_id` and `context_window.used_percentage` fields, and overwrite-per-refresh semantics. | field-or-template | L930 `#### Context-window boundary guard` | question text | - | - | AskUserQuestion | yes | procedure |
| F5-222 | Question text must (c) state that **Configure now** runs `/quo-setup --configure-gauge-producer` inline. | field-or-template | L930 `#### Context-window boundary guard` | question text | - | `/quo-setup --configure-gauge-producer` | AskUserQuestion | yes | procedure |
| F5-223 | Present the options multi-choice only — no fake free-text options. | invariant | L930 `#### Context-window boundary guard` | - | - | - | AskUserQuestion | yes | procedure |
| F5-224 | Option **Configure now** — invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool (same inline-Skill precedent as Section 1's URL-resolution sub-step's `/quo-file-issue`). | choice-set | L932 `#### Context-window boundary guard` | Skill invocation | - | Section 1 URL-resolution sub-step; `/quo-file-issue`; `/quo-setup` | none | yes | procedure |
| F5-225 | After a successful Configure now, **recommend resuming in a fresh session** with the resume command (producer publishes only **next** session) rather than implying the run is now guarded, then exit. | ordering | L932 `#### Context-window boundary guard` | recommendation; exit | - | - | none | yes | procedure |
| F5-226 | Option **Proceed without the guard (this run)** — continue to the next Issue (back to step 2); write no marker. | choice-set | L933 `#### Context-window boundary guard` | - | - | step 2 | none | yes | procedure |
| F5-227 | Option **Never guard me (persistent opt-out)** — write the marker via the helper's `write-opt-out` mode (one literal call), then continue to the next Issue (back to step 2). | choice-set | L934 `#### Context-window boundary guard` | opt-out marker | - | step 2 | Bash | yes | procedure |
| F5-228 | Opt-out write command: POSIX `python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" write-opt-out`; PowerShell `python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" write-opt-out`. | command | L936-L944 `#### Context-window boundary guard` | `context-guard-opt-out` file | helper | `context_gauge.py` | Bash | yes | procedure |
| F5-229 | Option **Stop here** — exit the skill with the fresh-session resume command. | choice-set | L946 `#### Context-window boundary guard` | stop report | resume command | - | none | yes | procedure |
| F5-230 | `#### Aborted-Issue close-out` is the canonical anchor name for the path where an Issue ends **without a fix landing**. | definition | L950 `#### Aborted-Issue close-out` | - | - | - | none | no | procedure |
| F5-231 | Three branches route here: Section 4's unexplained-movement gate's **Abort this Issue**, Section 3's Analyst-proposal gate's **Cancel**, and the routing-decision gate's **Cancel** (part (d) of `### Orchestrator discipline: routing review findings`). | definition | L950 `#### Aborted-Issue close-out` | - | gate answers | Section 4 Reconcile-step unexplained-movement gate; Section 3 Analyst-proposal gate; part (d) of `### Orchestrator discipline: routing review findings` | AskUserQuestion | no | procedure |
| F5-232 | **This is a definition, not a step in Section 7's linear flow** — run it only where one of those three branches calls for it by name. | invariant | L950 `#### Aborted-Issue close-out` | - | - | - | none | no | procedure |
| F5-233 | An aborted Issue is still an Issue boundary; never leave it by simply "moving on" — the fixed path's close-outs (TaskList sweep, deferral-hygiene gate, checkpoint) must all run. | invariant | L952 `#### Aborted-Issue close-out` | - | - | - | none | no | procedure |
| F5-234 | In batch mode the aborted boundary ends the run rather than advancing to the next Issue (step 4). | ordering | L952 `#### Aborted-Issue close-out` | - | run mode | step 4 | none | no | procedure |
| F5-235 | Failure narrative: skipping close-out lets an `aborted-*` marker hold Phase C shut on re-entry, strands `defer-*` entries, and leaves the manifest naming a left Issue. | rationale-only | L952 `#### Aborted-Issue close-out` | - | - | Phase C | none | no | failure-narrative |
| F5-236 | Run the four aborted close-out steps in order. | ordering | L952 `#### Aborted-Issue close-out` | - | - | - | none | no | procedure |
| F5-237 | Step 1 — **Close out this Issue's TaskList tasks** by **prefix**: `analyst-<issue-id>` (+`-rev<n>`), `engineer-<issue-id>` / `code-reviewer-<issue-id>`, `test-writer-<issue-id>` / `doc-writer-<issue-id>`, `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>`, every `-r<n>` round, and the `gate-*` task that fired the branch. | command | L954 `#### Aborted-Issue close-out` | TaskList status flips | TaskList | Section 7 step 3; Section 3; Phase A/B/C | TaskList | no | procedure |
| F5-238 | **Include every `aborted-<role>-<issue-id>` redelivery marker still `pending`, when one is open**, in the sweep. | command | L954 `#### Aborted-Issue close-out` | TaskList status flips | TaskList | Abort-this-Issue branch | TaskList | no | procedure |
| F5-239 | Run the aborted-marker clause on every branch rather than assuming it has nothing to sweep — a Section 3 `Cancel` re-fired from a Phase A round can land with a marker another lane opened. | invariant | L954 `#### Aborted-Issue close-out` | - | TaskList | Section 3 `Cancel`; part (d) | TaskList | no | procedure |
| F5-240 | Mark each swept task `completed` with the abort reason recorded in `metadata.activity` — informational context, never a routing input. | field-or-template | L954 `#### Aborted-Issue close-out` | `metadata.activity` | abort reason | - | TaskList | no | procedure |
| F5-241 | **"clear from the active set" means mark the task `completed`** — never delete it, or the `-r<n>` round count derived by counting recorded rounds is lost. | invariant | L954 `#### Aborted-Issue close-out` | - | - | naming convention | TaskList | no | procedure |
| F5-242 | **A sibling lane still in flight when this close-out fires**: the orchestrator cannot terminate a background Agent — mark its task `completed` anyway and record in `metadata.activity` that it was in flight at the abort. | command | L956 `#### Aborted-Issue close-out` | TaskList status flip; `metadata.activity` | live Agents | - | TaskList, Agent | no | procedure |
| F5-243 | Which lanes may be live per branch: Abort-this-Issue → the non-aborting Phase B writer; Phase C routing `Cancel` → unreturned reviewers/PM; Section 3 `Cancel` re-fired from `Re-dispatch the Analyst with this finding` → whatever Phase A/C lanes were active (typically none on Phase A). | definition | L956 `#### Aborted-Issue close-out` | - | - | part (c)/(d) `Re-dispatch the Analyst with this finding`; Phase A/B/C | Agent | no | procedure |
| F5-244 | When a late completion notification arrives for a closed-out Issue: process nothing for that Issue, note an implementer lane may have partially landed work (review-only lanes land nothing), and continue with the current unit. | recovery | L956 `#### Aborted-Issue close-out` | - | Agent completion notification | - | Agent | no | procedure |
| F5-245 | Step 2 — **Run Section 7.5's deferral-hygiene gate** for this Issue. | command | L957 `#### Aborted-Issue close-out` | gate run | `defer-*` tasks | Section 7.5 | TaskList, AskUserQuestion | no | procedure |
| F5-246 | The gate's hard-stop applies unchanged: do not advance while any `defer-*` task is `pending` or `in_progress`. | invariant | L957 `#### Aborted-Issue close-out` | - | TaskList | Section 7.5 | TaskList | no | procedure |
| F5-247 | Deferrals on an aborted Issue include the Analyst's `### Deferred refinements` bullets and any reviewer/PM feedback the Director ignored in whichever phases were reached. | definition | L957 `#### Aborted-Issue close-out` | - | `### Deferred refinements`; `defer-*` tasks | - | TaskList | no | procedure |
| F5-248 | Step 3 — **Run the Issue-boundary state-externalization checkpoint** on its **aborted path** (inverted step-1 verifications; aborted **Progress** entry in step 2); everything else runs unchanged. | command | L958 `#### Aborted-Issue close-out` | checkpoint run; manifest | - | `#### Issue-boundary state-externalization checkpoint` | bees, git, TaskList | no | procedure |
| F5-249 | Step 4 — **Read the working tree, then branch on mode**: an aborted Issue lands no commit, so the phases' edits stay uncommitted and the run does **not** carry that tree into another Issue. | ordering | L959 `#### Aborted-Issue close-out` | - | working tree | Section 7 step 5 | git | no | procedure |
| F5-250 | Tree contents depend on the entering branch: an **initial** Section 3 `Cancel` typically leaves nothing; a `Cancel` re-fired from Phase A/C via `Re-dispatch the Analyst with this finding` leaves a Phase A round's edits or a full Phase A/B pass. | definition | L959 `#### Aborted-Issue close-out` | - | - | Section 3; part (c)/(d) | none | no | rationale |
| F5-251 | Read the tree with one literal command, `git status --porcelain` (identical on POSIX and PowerShell), so the messages can name the paths. | command | L961-L971 `#### Aborted-Issue close-out` | uncommitted path list | working tree | - | git | no | procedure |
| F5-252 | **Single-issue mode** — **Name the aborted Issue and the uncommitted paths**, then proceed to Section 8 over what the session did land; if no commit landed at all, say so plainly and exit rather than dispatching a sweep over an empty diff. | ordering | L975 `#### Aborted-Issue close-out` | operator message | `git status --porcelain` output | Section 8 | none | no | procedure |
| F5-253 | **Batch mode (`all` or list) with the batch exhausted** — name the aborted Issue and uncommitted paths, then proceed to Section 8. | ordering | L976 `#### Aborted-Issue close-out` | operator message | `git status --porcelain` output | Section 8 | none | no | procedure |
| F5-254 | **Batch mode with a next Issue still remaining in the batch — STOP the run here.** Do **NOT** proceed to the next Issue. | gate | L977 `#### Aborted-Issue close-out` | run stop | run mode | - | none | no | procedure |
| F5-255 | Rationale: the next Issue would inherit a dirty tree — its Doc Writer would read it as "the Engineer's diff", the fingerprint fallback would sweep it into `## Source paths to fingerprint`, and staging could absorb it into an unrelated commit. | rationale-only | L977 `#### Aborted-Issue close-out` | - | - | `## Source paths to fingerprint` | none | no | rationale |
| F5-256 | Do **not** run the **Context-window boundary guard** on this aborted-batch stop — it is a run-ending path. | invariant | L977 `#### Aborted-Issue close-out` | - | - | `#### Context-window boundary guard` | none | no | procedure |
| F5-257 | Tell the operator **which Issue aborted**, the **uncommitted paths** `git status --porcelain` reported, and the **fresh-session resume command** (`/quo-fix-issue <remaining-ids>` for not-yet-`done` Issues, or `/quo-fix-issue all` on an `all` run). | relay | L977 `#### Aborted-Issue close-out` | operator message | `git status --porcelain`; batch; ticket statuses | - | none | no | procedure |
| F5-258 | Then exit the skill so the operator resolves the tree before the batch resumes. | ordering | L977 `#### Aborted-Issue close-out` | exit | - | - | none | no | procedure |

## Anchors defined here

Headings:

- L704 `### 5. Review Loop`
- L742 `### 6. Verify docs are still accurate`
- L753 `### 7. After Issue is fixed`
- L827 `#### Issue-boundary state-externalization checkpoint`
- L857 `#### Context-window boundary guard`
- L948 `#### Aborted-Issue close-out`

Bolded phrases (verbatim, in order of appearance):

- L706 **Phase C**
- L706 **and no `aborted-*` TaskList task for this Issue is `pending`**
- L706 **Code Reviewer is not dispatched here**
- L706 **Phase A**
- L706 **Phase A also borrows this section's feedback-consumption discipline in full**
- L706 **Follow the trailer literally**
- L717 **PM is the exception to the conditional-spawn rules.**
- L717 **always dispatched**
- L719 **Pass the tracker path, not its contents**
- L721 **The Phase C PM dispatch prompt must also relay the Engineer's completeness evidence verbatim.**
- L721 **second**
- L721 **wider**
- L721 **when any Engineer return for this Issue carried a completeness list**
- L721 **verbatim**
- L721 **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was**
- L721 **This MUST is not satisfiable on every path**
- L721 **Apply that per round, not per Issue:**
- L721 **no**
- L723 **The Phase C PM dispatch prompt must also relay the Analyst's `### Blast radius` verbatim.**
- L723 **second**
- L723 **verbatim**
- L723 **Relay it even when the Analyst's section carried only its fixed empty line**
- L729 **Code Reviewer**
- L729 **Phase A**
- L730 **Test Reviewer**
- L731 **Doc Reviewer**
- L732 **Product Manager**
- L734 `**Your next tool use MUST address these findings now.**`
- L734 `**Your next tool use MUST advance the workflow.**`
- L734 **Follow the trailer literally**
- L735 **These re-dispatches are ordered, not concurrent, whenever a fix path changes source**
- L736 **IMPORTANT**
- L737 **NOT**
- L739 **that reviewer's lane**
- L739 **one**
- L739 **Severity bounds the loop**
- L739 **Reviews**
- L740 **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.**
- L740 **For reviewer-feedback items (code/test/doc-reviewer findings the Director chose to ignore), the Director MUST annotate the `metadata.activity` with one of the three destination labels from the PM Agent's destination vocabulary — `addressed-now-in-this-Task` (read as "addressed-now-in-this-Issue"), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — when creating the `defer-*` task.**
- L744 **informational confirmation**
- L746 **confirm**
- L757 **Re-read the Issue's current status first**
- L758 **NEVER push to remote — committing only.**
- L759 **Format**
- L773 **Do NOT blindly `git add -A`**
- L778 **Phase A**
- L779 **Phase B**
- L780 **Phase C**
- L781 **aborted-writer redelivery markers**
- L783 **Close out round-discriminated names too.**
- L783 **prefix**
- L785 **The aborted path runs this same sweep at its own site.**
- L791 **Issue**
- L792 **Files Changed**
- L793 **Reviews**
- L794 **Doc Sync**
- L795 **Ignored Review Feedback**
- L796 **Second-order effects**
- L797 **Accepted compromises**
- L800 **Second-order effects (rendered into the summary block above).**
- L800 **destination**
- L802 **Collect every relayed narrative for this Issue**
- L802 **verbatim**
- L803 **Attribute each block**
- L804 **De-duplicate exact repeats.**
- L805 **When every source reported the fixed empty line**
- L805 **not**
- L807 **Accepted compromises (rendered into the summary block above).**
- L809 **Read the run's tracker file via the `Read` tool**
- L809 **Compromise tracker**
- L810 **Omit the section entirely when there is nothing to show.**
- L811 **When entries exist, render one bullet per `## Compromise <n>` entry**
- L812 **finding**
- L813 **chosen path**
- L814 **rationale**
- L815 **follow-up Issue ID**
- L818 **Volume (>10 entries).**
- L820 **reads**
- L822 **Issue-boundary state-externalization checkpoint**
- L823 **Single mode**
- L824 **Batch mode (`all` or list mode) with the batch exhausted**
- L825 **Batch mode with a next Issue still remaining in the batch**
- L825 **Context-window boundary guard**
- L829 **It is a definition, not a step in Section 7's linear flow**
- L831 **on the aborted path**
- L831 **verify that invariant and refresh the durable carriers**
- L837 **the Issue's bees ticket**
- L838 **the per-issue git commit**
- L839 **the session-scoped compromise tracker**
- L840 **the `defer-*` TaskList ledger**
- L841 **the run-state manifest**
- L845 **Verify the carriers.**
- L845 **Aborted-path qualification.**
- L845 **`open`**
- L845 **no**
- L847 **Pre-session SHA**
- L847 **Validate the manifest before trusting that field:**
- L847 **Unit scope**
- L847 **Pre-session SHA** (second occurrence)
- L847 **do not use a bare `git log --oneline -1`**
- L847 **do not drop the `<pre-session-sha>..HEAD` bound**
- L848 **Compromise tracker**
- L848 **A `Read` reporting that the file does not exist is not by itself a gap**
- L848 **was accepted**
- L848 **that Trigger C requires an entry for**
- L851 **now**
- L852 **Rewrite the run-state manifest**
- L852 **On the aborted path**
- L853 **Re-read, do not recall, at every dispatch on the next Issue.**
- L853 **no**
- L855 **What this checkpoint does not do.**
- L859 **definition co-located with the Issue-boundary checkpoint above**
- L859 **one continuing, in-session path**
- L859 **NOT**
- L859 **`#### Aborted-Issue close-out` below does not invoke it either**
- L861 **What the guard reads, and what it does not.**
- L861 **external gauge file**
- L861 **fresh session**
- L863 **Ordering is load-bearing (mirror Section 1's `#### Check session reasoning effort`).**
- L863 **first**
- L865 **Step 1 — read the session id.**
- L877 **Trim any trailing whitespace or newline**
- L879 **Step 2 — session id unset or empty → skip the guard silently and continue**
- L881 **Step 3 — session id present.**
- L909 **Step 4 — branch on the `read` output and its exit status.**
- L911 **Integer ≥ threshold → STOP**
- L911 **fresh session**
- L912 **Integer < threshold → continue**
- L913 **`no-reading` → continue**
- L914 **`stale` → STOP**
- L915 **Non-zero exit, or empty stdout → the same fail-safe stop-and-ask as `stale`**
- L916 **`missing`**
- L928 **If the marker is present → skip the guard silently and continue**
- L928 **If absent → hard-stop via the two-step gate in step 5 below.**
- L930 **Step 5 — the missing-reading gate (reached only from the `missing`-and-no-marker branch above).**
- L930 **first**
- L930 **then**
- L930 **Configure now**
- L932 **Configure now**
- L932 **next**
- L932 **recommend resuming in a fresh session**
- L933 **Proceed without the guard (this run)**
- L934 **Never guard me (persistent opt-out)**
- L946 **Stop here**
- L950 **without a fix landing**
- L950 **Abort this Issue**
- L950 **Cancel** (two occurrences)
- L950 **this is a definition, not a step in Section 7's linear flow**
- L954 **Close out this Issue's TaskList tasks**
- L954 **prefix**
- L954 **Include every `aborted-<role>-<issue-id>` redelivery marker still `pending`, when one is open**
- L954 **"clear from the active set" means mark the task `completed`**
- L956 **A sibling lane still in flight when this close-out fires.**
- L956 **re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice**
- L957 **Run Section 7.5's deferral-hygiene gate**
- L958 **Run the Issue-boundary state-externalization checkpoint**
- L958 **aborted path**
- L958 **Progress**
- L959 **Read the working tree, then branch on mode.**
- L959 **diverges**
- L959 **not**
- L959 **initial**
- L975 **Single-issue mode**
- L975 **Name the aborted Issue and the uncommitted paths**
- L976 **Batch mode (`all` or list) with the batch exhausted**
- L977 **Batch mode with a next Issue still remaining in the batch — STOP the run here.**
- L977 **NOT**
- L977 **Context-window boundary guard**
- L977 **not**
- L977 **which Issue aborted**
- L977 **uncommitted paths**
- L977 **fresh-session resume command**

## Rationale-only spans

Whole-line spans containing no rule:

- L727 — role prose lives in role files (arguably a delegation invariant; kept as F5-044)
- L833 — checkpoint mostly structurally enforced already

Sub-line rationale clauses embedded in rule-bearing lines (line, gist):

- L717 (last two sentences) — PM judges spec drift itself
- L721 (mid) — second caller, no channel, wider diff
- L721 (mid) — unnamed sweep silently loses check
- L740 (last sentence) — gate would fire empty otherwise
- L757 (clause) — workers occasionally overstep status flip
- L761 (clause) — mirrors quo-execute Plans-hive scoping
- L773 (last sentence) — other issues' drift caught later
- L774 (clause) — Section 9 grep depends on token
- L781 (last clause) — pending marker holds Phase C shut
- L805 (last sentence) — conditional field becomes unreliable
- L810 (parenthetical) — absent file now uncommon
- L831 (middle) — Issue boundary is most re-derivable
- L848 (last sentence) — carve-out correctly entry-less
- L855 (second sentence) — harness owns token reclamation
- L861 (last sentence) — stop before auto-compaction fires
- L881 (last sentence) — same sibling-resolution as other helpers
- L914 (clause) — stale number biases low
- L952 (sentences 2–3) — consequences of skipping close-out
- L959 (parenthetical) — tree contents depend on branch
- L977 (middle) — dirty-tree inheritance consequences

Total whole rationale-only lines: 2 (L727, L833). Rationale clauses embedded in rule-bearing lines: 20 (all captured as `rationale-only` / `failure-narrative` rows above).
