# Rule inventory — quo-fix-issue SKILL.md, Section 4 (L368–L617)

Source: `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md` lines 368–617 (`### 4. Execute fix via per-issue Agent dispatch` through `#### Scoped-marker PM dispatch wiring`). Prefix `F3`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F3-001 | Drive each Issue's fix through a **reconciliation loop** that dispatches fresh, ephemeral background `Agent` invocations against subagent types in the sibling `agents/` directory. | invariant | L370 `### 4. Execute fix via per-issue Agent dispatch` | dispatches | `agents/` role files | `agents/` | Agent | unknown | procedure |
| F3-002 | Never keep a long-lived team, warmed Agents, or peer-to-peer messaging between workers. | invariant | L370 `### 4.` | - | - | - | Agent | unknown | procedure |
| F3-003 | Dispatch scope is **per-issue**, not per-Subtask: one implementation pass per Issue, no Subtask breakdown, unlike `/quo-execute`. | definition | L370 `### 4.` | - | - | `/quo-execute` | none | no | procedure |
| F3-004 | Section 3's Design analysis gate produces the authoritative design directive; the Engineer dispatch carries it into the implementation pass. | relay | L370 `### 4.` | Engineer dispatch prompt | Section 3 design directive | Section 3 | Agent | no | procedure |
| F3-005 | The loop is **event-driven, not clock-driven**; each tick has exactly three phases: Read state, Reconcile, Yield. | ordering | L374 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-006 | **Read state.** Pull current truth from four sources (bees, TaskList, git state, run-state manifest) before deciding what to do. | precondition | L376 `#### Reconciliation loop` | - | bees, TaskList, git, manifest | - | TaskList, bees, git | unknown | procedure |
| F3-007 | Use `bees show-ticket --ids <issue-id>` to get the Issue body and current `ticket_status`. | command | L377 `#### Reconciliation loop` | - | Issue id | - | bees | unknown | procedure |
| F3-008 | Use `bees execute-freeform-query --query-yaml '<yaml>'` for any focused state query. | command | L377 `#### Reconciliation loop` | - | - | - | bees | unknown | procedure |
| F3-009 | Example freeform query: `stages:` `- [id=<issue-id>]` `report: [title, ticket_status]`. | example | L379-L383 `#### Reconciliation loop` | - | - | - | bees | unknown | example |
| F3-010 | Each in-flight Agent has a TaskList task whose `status` is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done). | definition | L384 `#### Reconciliation loop` | - | TaskList | "TaskList as progress UI" | TaskList | unknown | procedure |
| F3-011 | The git diff on disk is the only authoritative record of what workers actually did. | invariant | L385 `#### Reconciliation loop` | - | git diff | - | git | unknown | procedure |
| F3-012 | The run-state manifest holds the ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress, and next unit. | definition | L386 `#### Reconciliation loop` | - | manifest | Section 1 `#### Write the run-state manifest` | none | no | procedure |
| F3-013 | `Read` the manifest at `<tempdir>/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md`. | command | L386 `#### Reconciliation loop` | - | manifest file | Section 1 `#### Write the run-state manifest` | none | no | procedure |
| F3-014 | The manifest path derives from this skill's name plus the basename of `git rev-parse --show-toplevel`, so it is recomputable from the working directory. | definition | L386 `#### Reconciliation loop` | - | working tree root | - | git | no | procedure |
| F3-015 | **Validate it before trusting any field:** compare the manifest's **Unit scope** ordered Issue batch against the batch this run is fixing. | precondition | L386 `#### Reconciliation loop` | - | manifest `Unit scope` | Section 1 `#### Write the run-state manifest` | none | unknown | procedure |
| F3-016 | If the manifest names Issues this run is not working, treat it as absent and recover per Section 1; never read a foreign `<pre-session-sha>`, isolation strategy, or tracker path. | recovery | L386 `#### Reconciliation loop` | - | manifest | Section 1 `#### Write the run-state manifest` | none | unknown | procedure |
| F3-017 | **Conversation memory is never a substitute for these four sources.** Re-read Issue status, landed commits, batch order, pre-session SHA on every tick; never recall. | invariant | L388 `#### Reconciliation loop` | - | four sources | - | TaskList, bees, git | unknown | procedure |
| F3-018 | **If a summarization marker is visible in the conversation**, treat everything before it as non-authoritative and re-read all four sources in full before dispatching, starting with the Issue body from bees. | recovery | L388 `#### Reconciliation loop` | - | four sources | - | TaskList, bees, git | unknown | procedure |
| F3-019 | The **Design Proposal** (`### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`) has no durable carrier by design; it lives only in the Analyst's returned message. | definition | L388 `#### Reconciliation loop` | - | Analyst return | Section 3 | none | no | procedure |
| F3-020 | The proposal-recovery rule is **functional, not positional**: it fires **whenever the proposal is needed for this Issue** and it is no longer readable. | precondition | L388 `#### Reconciliation loop` | - | Analyst return | - | none | no | procedure |
| F3-021 | "Needed" means: an Engineer dispatch (any round incl. Phase C re-entry), a Phase A Code Reviewer relay, a Phase C PM relay, a re-run of these, or Section 3's gate open on an unreadable proposal. | definition | L388 `#### Reconciliation loop` | - | - | Section 3 | none | no | procedure |
| F3-022 | Do not reconstruct the Design Proposal from a summary. | invariant | L388 `#### Reconciliation loop` | - | - | - | none | no | procedure |
| F3-023 | Do not give the Design Proposal a manifest field. | invariant | L388 `#### Reconciliation loop` | - | manifest | - | none | no | procedure |
| F3-024 | **Re-derive it through the Analyst. That is the only recovery for the proposal itself**; waiting on an in-flight Analyst is that same re-derivation. | recovery | L388 `#### Reconciliation loop` | Analyst dispatch | - | - | Agent | no | procedure |
| F3-025 | No path in fix mode omits a downstream `## Blast radius` relay heading, because the proposal is re-derived before the dispatch that needs it. | invariant | L388 `#### Reconciliation loop` | - | - | - | none | no | procedure |
| F3-026 | **Check first for an active `analyst-<issue-id>` task for this Issue**, matching on name **prefix** plus status so `-rev<n>` names are caught. | precondition | L390 `#### Reconciliation loop` | - | TaskList | Section 3 | TaskList | no | procedure |
| F3-027 | An active `analyst-*` task means an Analyst is genuinely in flight (Section 3 marks it `completed` when the return is read); wait for it and run Section 3's gate on it. | recovery | L390 `#### Reconciliation loop` | - | TaskList | Section 3 | TaskList, Agent | no | procedure |
| F3-028 | Wait only when the `analyst-*` task is `in_progress`, or `pending` with a dispatch already landed. | precondition | L390 `#### Reconciliation loop` | - | TaskList | "Anti-pattern: no clock primitives" | TaskList | no | procedure |
| F3-029 | When the `analyst-*` task is `pending` with no dispatch landed, do not wait: dispatch the Analyst now under that same task name using the **re-derivation shape**, and wait on that return. | recovery | L390 `#### Reconciliation loop` | Analyst dispatch | TaskList | - | TaskList, Agent | no | procedure |
| F3-030 | **Post-compaction, whether the dispatch landed is itself unreadable**; treat it as **not** landed and re-dispatch. | recovery | L390 `#### Reconciliation loop` | Analyst dispatch | - | Engineer-dispatch precondition stranded-`pending` clause | Agent | no | procedure |
| F3-031 | Otherwise, when a `gate-askuserquestion-*` task for this Issue's Section 3 gate is active, mark it `completed`, recording in `metadata.activity` that a compaction abandoned the question. | recovery | L390 `#### Reconciliation loop` | gate task `completed`, `metadata.activity` | TaskList | Section 3 | TaskList | no | procedure |
| F3-032 | The abandoned-question note in `metadata.activity` is informational context, never a routing input. | invariant | L390 `#### Reconciliation loop` | - | `metadata.activity` | - | TaskList | no | procedure |
| F3-033 | Then re-dispatch the Analyst under the next `analyst-<issue-id>-rev<n>` name using the **re-derivation shape**. | recovery | L390 `#### Reconciliation loop` | Analyst dispatch, `analyst-<issue-id>-rev<n>` task | - | - | TaskList, Agent | no | procedure |
| F3-034 | **For this one gate that re-derivation takes precedence over the generic gate re-fire** the TaskList naming convention prescribes for active `gate-*` tasks. | ordering | L390 `#### Reconciliation loop` | - | - | TaskList naming convention | TaskList | no | procedure |
| F3-035 | Otherwise (no `analyst-*` task and no Section 3 `gate-*` task active), re-dispatch the Analyst under the next `analyst-<issue-id>-rev<n>` name using the **re-derivation shape**. | recovery | L390 `#### Reconciliation loop` | Analyst dispatch | TaskList | - | TaskList, Agent | no | procedure |
| F3-036 | Re-derivation shape item 1: the **Issue body re-read from bees**, and the same `reference_materials` the first dispatch carried. | field-or-template | L392 `#### Reconciliation loop` | Analyst prompt | `bees show-ticket`, `reference_materials` | - | bees | no | procedure |
| F3-037 | Re-derivation shape item 2: the **changed-file list of what is on disk for this Issue** — latest Engineer `## Files changed`, or the **Fallback when an Engineer return did not list files** derivation. | field-or-template | L393 `#### Reconciliation loop` | Analyst prompt | `## Files changed`, `git diff --name-only HEAD` | Test Writer dispatch **Fallback when an Engineer return did not list files** | git | no | procedure |
| F3-038 | An **empty** changed-file list is itself informative: it says no implementation has landed for this Issue yet. | definition | L393 `#### Reconciliation loop` | - | - | - | none | no | procedure |
| F3-039 | Re-derivation shape item 3: state plainly that **the prior proposal was lost to a compaction**, the changed-file list is what was implemented, the Analyst re-derives from the codebase, and `### Blast radius` must cover the tree as it stands. | field-or-template | L394 `#### Reconciliation loop` | Analyst prompt | - | - | none | no | procedure |
| F3-040 | When the re-dispatched pass is the **first** Section 3 pass (stranded task is undiscriminated `analyst-<issue-id>`), say instead that **no proposal has been produced yet** and the compaction landed before one returned. | field-or-template | L394 `#### Reconciliation loop` | Analyst prompt | TaskList task name | Section 3 | TaskList | no | procedure |
| F3-041 | When the re-derivation Analyst returns, run Section 3's surface-and-gate flow unchanged and resume the in-progress phase with the re-derived directive. | recovery | L396 `#### Reconciliation loop` | - | Analyst return | Section 3 | AskUserQuestion, TaskList | no | procedure |
| F3-042 | Branch the resume **only on TaskList-derivable state**, never on whether Phase A "still had findings". | invariant | L396 `#### Reconciliation loop` | - | TaskList | **Post-compaction recovery inside Phase A** | TaskList | no | procedure |
| F3-043 | **Phase A has not begun** when no `engineer-<issue-id>` task exists (prefix-matched, catching `-r<n>`), or the only one is `pending` with no dispatch landed. | definition | L396 `#### Reconciliation loop` | - | TaskList | Engineer-dispatch precondition stranded-`pending` clause | TaskList | no | procedure |
| F3-044 | On Phase-A-not-begun, resume at **Phase A's entry**: the first Engineer dispatch, under the stranded task's own name when one exists, or straight to **Phase B** when the directive needs no source change. | recovery | L396 `#### Reconciliation loop` | Engineer dispatch | TaskList | - | TaskList, Agent | no | procedure |
| F3-045 | Do **not** dispatch the Code Reviewer on the Phase-A-not-begun branch; no implementation has landed to review. | invariant | L396 `#### Reconciliation loop` | - | - | - | Agent | no | procedure |
| F3-046 | **The "only one that does" qualifier is deliberate:** when a stranded `pending` `engineer-<issue-id>-r<n>` sits beside a `completed` earlier round, this arm does not fire; leave the stranded task as is. | recovery | L396 `#### Reconciliation loop` | - | TaskList | Section 7 close-out prefix sweep | TaskList | no | procedure |
| F3-047 | Section 7's close-out prefix sweep marks such a stranded task `completed` at the Issue boundary; the only cost is a skipped round number. | definition | L396 `#### Reconciliation loop` | - | - | Section 7 | TaskList | no | procedure |
| F3-048 | When an `engineer-<issue-id>` task exists and **Phase B has not begun** (no `test-writer-<issue-id>` or `doc-writer-<issue-id>` task, prefix-matched), resume through the Phase A recovery rung: dispatch the **Code Reviewer** with the re-derived `## Blast radius`. | recovery | L396 `#### Reconciliation loop` | Code Reviewer dispatch | TaskList | **Post-compaction recovery inside Phase A** | TaskList, Agent | no | procedure |
| F3-049 | That rung's Analyst-active exception cannot fire at this point because Section 3's surfacing step marked the Analyst task `completed` when its return was read. | rationale-only | L396 `#### Reconciliation loop` | - | - | Section 3 | none | no | rationale |
| F3-050 | Let the Code Reviewer's findings drive whether an Engineer round follows and what it addresses, under its next name per the naming convention. | recovery | L396 `#### Reconciliation loop` | Engineer dispatch | Code Reviewer return | TaskList naming convention | Agent | no | procedure |
| F3-051 | Otherwise resume with the **next dispatch** in the ladder, whose `## Blast radius` relay now has a list to carry. | recovery | L396 `#### Reconciliation loop` | next dispatch | - | - | Agent | no | procedure |
| F3-052 | **One case the Phase-B-has-not-begun arm cannot tell apart by task-name set alone:** a `## Design question` round where compaction landed before the Analyst re-dispatch; cost is a Code Reviewer round on a partial diff, not a mis-completion. | failure-narrative | L396 `#### Reconciliation loop` | - | - | design-question rung | none | no | failure-narrative |
| F3-053 | Where the re-derivation differs from the diff on disk, the Engineer round reconciles that difference rather than papering over it. | invariant | L396 `#### Reconciliation loop` | - | - | - | Agent | no | procedure |
| F3-054 | The Issue ticket type supports only two statuses, `open` and `done`; there is no in-flight bees status to set. | definition | L398 `#### Reconciliation loop` | - | bees | - | bees | no | procedure |
| F3-055 | TaskList carries the in-flight signal; flip the Issue from `open` to `done` only at issue close-out per Section 7. | ordering | L398 `#### Reconciliation loop` | status flip `open`→`done` | TaskList | Section 7 | bees, TaskList | no | procedure |
| F3-056 | **Reconcile.** Compare current state to target state and act. | definition | L400 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-057 | Dispatch is **ordered into three phases**; implementer lanes are NOT fanned out together, reviewers are not all held to the end; dispatch concurrently only *within* a phase. | ordering | L400 `#### Reconciliation loop` | - | - | - | Agent | unknown | procedure |
| F3-058 | **Phase A — source to clean.** When the fix needs source changes, dispatch the **Engineer alone**. | ordering | L402 `#### Reconciliation loop` | Engineer dispatch | - | "Per-issue cold dispatch" | Agent | unknown | procedure |
| F3-059 | On the Engineer's return, dispatch the **Code Reviewer alone** (Section 5 shape, `code-reviewer-<issue-id>` naming) unless that return carries a `## Design question`. | ordering | L402 `#### Reconciliation loop` | Code Reviewer dispatch | Engineer return | Section 5, design-question rung | Agent | no | procedure |
| F3-060 | Loop Engineer → Code Reviewer → Engineer until the Code Reviewer emits `No code issues found.` or every remaining finding is routed through `### Orchestrator discipline: routing review findings`. | ordering | L402 `#### Reconciliation loop` | dispatches | Code Reviewer return | `### Orchestrator discipline: routing review findings` | Agent | unknown | procedure |
| F3-061 | Routed means: accepted into the compromise tracker (Section 7.5), recorded as a `defer-*` task (Section 5 ignored-feedback rule), or gated to the user **and settled by that gate's answer** per **Severity bounds the loop**. | definition | L402 `#### Reconciliation loop` | tracker entry, `defer-*` task, gate | - | Section 7.5, Section 5, **Severity bounds the loop** | TaskList, AskUserQuestion | unknown | procedure |
| F3-062 | A gate answer that dispatches a fix settles nothing; the loop continues until a cold pass has read that dispatch. | invariant | L402 `#### Reconciliation loop` | - | gate answer | **Severity bounds the loop** | Agent | unknown | procedure |
| F3-063 | A Code Reviewer return whose findings are all `nit`s with `trivial-tweak` paths (shipped as such, no gate substituting a deeper fix) closes Phase A after **one** Engineer pass with no further review round. | ordering | L402 `#### Reconciliation loop` | Phase A closure | Code Reviewer return | **Severity bounds the loop** | Agent | unknown | procedure |
| F3-064 | The design-question rung is a further exit from the Engineer step: it neither closes nor continues Phase A but **suspends** it pending a revised directive from Section 3. | definition | L402 `#### Reconciliation loop` | - | - | Section 3 | none | no | procedure |
| F3-065 | Every Phase A round after the first uses `engineer-<issue-id>-r<n>` / `code-reviewer-<issue-id>-r<n>`. | name-class | L402 `#### Reconciliation loop` | TaskList tasks | - | TaskList naming convention | TaskList | unknown | procedure |
| F3-066 | When the Issue needs no source change, Phase A is empty and the loop proceeds directly to Phase B. | ordering | L402 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-067 | **The Phase A exit test reads the numbered work-item list only.** | invariant | L404 `#### Reconciliation loop` | - | `/quo-engineer-review` output | `/quo-engineer-review` | none | unknown | procedure |
| F3-068 | **A non-empty `### Second-order effects` narrative alongside a clean numbered list does NOT block Phase A closure.** | invariant | L404 `#### Reconciliation loop` | - | `### Second-order effects` | `/quo-engineer-review` double-emission rule | none | unknown | procedure |
| F3-069 | Carry the `### Second-order effects` narrative into the per-issue summary's `**Second-order effects**` field (Section 7 step 4); do not re-dispatch the Engineer against it or hold Phase A open. | relay | L404 `#### Reconciliation loop` | summary field `**Second-order effects**` | `### Second-order effects` | Section 7 step 4 | none | unknown | procedure |
| F3-070 | `/quo-engineer-review` emits `### Second-order effects` on **every** review, clean ones included; actionable items are already in the numbered list. | definition | L404 `#### Reconciliation loop` | - | - | `/quo-engineer-review` | none | unknown | rationale |
| F3-071 | **Phase B — writers once, in parallel.** Once Phase A has closed, dispatch the **Test Writer** (when tests need changing) and the **Doc Writer** (always) concurrently. | ordering | L405 `#### Reconciliation loop` | Test Writer, Doc Writer dispatches | Phase A closure | - | Agent | unknown | procedure |
| F3-072 | Phase B is the **only** place the two writers are dispatched on the forward path, so they read a review-clean diff (or one clean apart from final `trivial-tweak` nit fixes). | invariant | L405 `#### Reconciliation loop` | - | - | **Severity bounds the loop** | Agent | unknown | procedure |
| F3-073 | **Phase C — remaining reviewers plus PM.** When Phase B writers have returned and no `aborted-*` task for this Issue is `pending` (prefix `aborted-` + status), advance to Section 5. | ordering | L406 `#### Reconciliation loop` | - | TaskList | Section 5, movement-report rung | TaskList | unknown | procedure |
| F3-074 | In Phase C dispatch the **Test Reviewer** (if the Test Writer ran), the **Doc Reviewer** (if the Doc Writer ran), and the **PM** (always). | ordering | L406 `#### Reconciliation loop` | reviewer, PM dispatches | - | Section 5 | Agent | unknown | procedure |
| F3-075 | The Code Reviewer is NOT dispatched again in Phase C; it ran to closure in Phase A. | invariant | L406 `#### Reconciliation loop` | - | - | - | Agent | unknown | procedure |
| F3-076 | The orchestrator does not pre-judge whether a PM pass is needed. | invariant | L406 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-077 | **Engineer-dispatch precondition:** MUST NOT dispatch an Engineer while any task named with prefix `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, or `analyst-<issue-id>` is `pending` or `in_progress`. | precondition | L407 `#### Reconciliation loop` | - | TaskList | - | TaskList, Agent | no | procedure |
| F3-078 | Match the precondition on name **prefix** plus status, never on an exact name, so `-r<n>` and other suffixes are caught. | invariant | L407 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-079 | It is a **precondition to check, not a state to remember**: before *every* Engineer dispatch (forward and re-entry) walk the TaskList and confirm no matching task is active. | precondition | L407 `#### Reconciliation loop` | - | TaskList | "Conversation memory is never a substitute for these four sources" | TaskList | unknown | procedure |
| F3-080 | **Why the two Phase C reviewers and the PM are covered:** a reviewer mid-read when edits land returns a stale verdict; a Phase C finding re-entering Phase A waits for **all** Phase C returns. | rationale-only | L409 `#### Reconciliation loop` | - | - | - | none | unknown | rationale |
| F3-081 | **Why the Analyst is covered too:** an Analyst mid-revision authors the directive the next Engineer round implements; Section 3 marks the Analyst task `completed` before the approval gate, so the forward path is never blocked. | rationale-only | L411 `#### Reconciliation loop` | - | - | Section 3, design-question rung | none | no | rationale |
| F3-082 | **The Code Reviewer is the one deliberate exception, and is NOT in the prefix list**, because Phase A alternates Engineer and Code Reviewer by construction. | invariant | L413 `#### Reconciliation loop` | - | - | design-question rung | none | unknown | procedure |
| F3-083 | The Code Reviewer exclusion is specific to this ladder; it does **not** generalize to a review site where the Code Reviewer runs concurrently with other reviewers. | invariant | L413 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-084 | `pending` stays in the precondition's status test deliberately: it closes the race between task creation and the `Agent(...)` call landing. | invariant | L415 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-085 | When the blocking task is `in_progress`, or `pending` **with a dispatch already landed**, wait for its completion notification and re-check on the next tick. | precondition | L415 `#### Reconciliation loop` | - | TaskList | "Anti-pattern: no clock primitives" | TaskList | unknown | procedure |
| F3-086 | When the blocking task is `pending` and **no dispatch has landed**, do not wait: dispatch that role now (if wanted) or mark the stale task `completed` and clear it, then re-check. | recovery | L415 `#### Reconciliation loop` | dispatch or task `completed` | TaskList | - | TaskList, Agent | unknown | procedure |
| F3-087 | **Post-compaction, whether a dispatch landed is unreadable**; default to **not** landed. This default is stated once here and answers wherever the clause is cited. | recovery | L415 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-088 | Do **not** narrow the precondition to `in_progress` only; `pending` stays in the test. | invariant | L415 `#### Reconciliation loop` | - | - | - | TaskList | unknown | procedure |
| F3-089 | **A writer that aborted on source movement does not block an Engineer round, and needs no exemption**: `aborted-` is a **distinct name class** the prefix test does not match. | invariant | L417 `#### Reconciliation loop` | - | TaskList | movement-report rung | TaskList | unknown | procedure |
| F3-090 | Never key an exemption on an abort annotation in `metadata.activity`; it is informational and not a routing input. | invariant | L417 `#### Reconciliation loop` | - | `metadata.activity` | - | TaskList | unknown | procedure |
| F3-091 | What the `aborted-*` task gates is **Phase C**, not the Engineer. | invariant | L417 `#### Reconciliation loop` | - | - | movement-report rung | TaskList | unknown | procedure |
| F3-092 | **Re-entry from Phase C.** A Phase C finding whose chosen fix path changes **source** re-enters Phase A: dispatch the Engineer, then the Code Reviewer (elided only for a final `trivial-tweak` nit pass per part (g)), loop until Phase A re-closes. | ordering | L418 `#### Reconciliation loop` | Engineer, Code Reviewer dispatches | Phase C finding | part (g) of `### Orchestrator discipline: routing review findings` | Agent | unknown | procedure |
| F3-093 | When Phase A re-closes, re-dispatch **only** the writer lanes the source change invalidated (Test Writer if pinned behavior moved, Doc Writer if documented diff moved), then the corresponding Phase C reviewers. | ordering | L418 `#### Reconciliation loop` | writer, reviewer dispatches | - | - | Agent | unknown | procedure |
| F3-094 | A Phase C finding confined to a writer's own lane (changes no source file) re-dispatches that writer alone and does **not** re-enter Phase A. | ordering | L418 `#### Reconciliation loop` | writer dispatch | Phase C finding | - | Agent | unknown | procedure |
| F3-095 | When the reviewer's findings are all `nit`s with `trivial-tweak` paths, shipped as such, that single writer pass closes the lane with no further reviewer round. | ordering | L418 `#### Reconciliation loop` | lane closure | reviewer return | **Severity bounds the loop** in `### Orchestrator discipline: routing review findings` | Agent | unknown | procedure |
| F3-096 | The ordering rule for any re-dispatch that touches source is part (g) of `### Orchestrator discipline: routing review findings`. | definition | L418 `#### Reconciliation loop` | - | - | part (g) of `### Orchestrator discipline: routing review findings` | none | unknown | procedure |
| F3-097 | **Post-compaction recovery inside Phase A.** "Did the last code review come back clean?" has **no durable carrier**; do NOT add a lane-phase field to the manifest. | invariant | L419 `#### Reconciliation loop` | - | manifest | - | none | unknown | procedure |
| F3-098 | If a compaction lands mid-Phase-A and the Code Reviewer's last verdict is unreadable, **re-dispatch the Code Reviewer**; a cold pass over the current diff is idempotent and correct. | recovery | L419 `#### Reconciliation loop` | Code Reviewer dispatch | - | - | Agent | unknown | procedure |
| F3-099 | Exception: if an `analyst-<issue-id>` task is active (prefix + status, catching `-rev<n>`), Phase A is suspended; wait for the Analyst's return and run Section 3's gate rather than reviewing the partial diff. | recovery | L419 `#### Reconciliation loop` | - | TaskList | Section 3, design-question rung, Engineer-dispatch precondition | TaskList | no | procedure |
| F3-100 | **Movement report from a Phase B writer.** `agents/test-writer.md` and `agents/doc-writer.md` instruct the writer to **stop mid-run and report** when the source it worked against moved. | definition | L420 `#### Reconciliation loop` | - | writer return | `agents/test-writer.md`, `agents/doc-writer.md` | none | unknown | procedure |
| F3-101 | The Test Writer detects movement with a `git rev-parse HEAD` + `git hash-object` fingerprint taken at start and before finishing; the Doc Writer (no `Bash`) re-reads with `Read` / `Grep`. | definition | L420 `#### Reconciliation loop` | - | - | `agents/test-writer.md`, `agents/doc-writer.md` | git | unknown | procedure |
| F3-102 | This rung is the receiver of the movement report; without one the orchestrator would mark the task `completed`, advance to Phase C, and review unfinished work. | definition | L420 `#### Reconciliation loop` | - | - | - | none | unknown | failure-narrative |
| F3-103 | **Recognising it.** Read the writer's return before persisting anything. | ordering | L422 `#### Reconciliation loop` | - | writer return | - | none | unknown | procedure |
| F3-104 | A movement report says the source moved, names what moved (files, opening/closing HEAD when HEAD moved), and how far the work got, in place of or alongside a partial deliverable. | definition | L422 `#### Reconciliation loop` | - | writer return | - | none | unknown | procedure |
| F3-105 | **Fix mode is the strict branch**: movement outside the writer's lane is anomalous, not expected concurrency; do not import the role files' softer execute-mode branch. | invariant | L422 `#### Reconciliation loop` | - | - | `agents/test-writer.md`, `agents/doc-writer.md` | none | no | procedure |
| F3-106 | **The two writers detect different things, and the receiver should not overstate either.** Test Writer trigger: any changed hash in its `## Source paths to fingerprint` set, a moved `HEAD`, or a path that no longer hashes. | definition | L422 `#### Reconciliation loop` | - | `## Source paths to fingerprint` | `agents/test-writer.md` | none | unknown | procedure |
| F3-107 | The Doc Writer's trigger is narrower: it stops when the material it is documenting appears to have moved (a file it read no longer matches its prose), per `agents/doc-writer.md`. | definition | L422 `#### Reconciliation loop` | - | - | `agents/doc-writer.md` | none | unknown | procedure |
| F3-108 | Do not read a Doc Writer's silence as a clean-tree attestation over every source path. | invariant | L422 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-109 | What marks either return as a movement report is that the writer **stopped**. | definition | L422 `#### Reconciliation loop` | - | writer return | - | none | unknown | procedure |
| F3-110 | **What to do.** Do **NOT** unlock Phase C on that lane; record the owed redelivery as a durable TaskList entry (the obligation-as-pending-task pattern `defer-*` and `gate-*` use). | invariant | L424 `#### Reconciliation loop` | TaskList task | - | `defer-*`, `gate-*` | TaskList | unknown | procedure |
| F3-111 | Step 1: **Mark the writer's own TaskList task `completed`** (`test-writer-<issue-id>` / `doc-writer-<issue-id>`, including any `-r<n>` suffix); its Agent has exited. | command | L426 `#### Reconciliation loop` | task `completed` | TaskList | - | TaskList | unknown | procedure |
| F3-112 | Step 2: **Create a new `aborted-<role>-<issue-id>` TaskList task** (`aborted-test-writer-<issue-id>` / `aborted-doc-writer-<issue-id>`) with status `pending` and the "how far I got" report as `metadata.activity`. | command | L427 `#### Reconciliation loop` | `aborted-<role>-<issue-id>` task | writer return | TaskList naming convention | TaskList | unknown | procedure |
| F3-113 | The pending `aborted-*` task **is** the redelivery-owed marker, read off the TaskList each tick so it survives compaction. | definition | L427 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-114 | Routing tests the `aborted-*` task's **name prefix and status**; `metadata.activity` is informational context for the re-dispatch prompt only. | invariant | L427 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-115 | Step 3: **Phase C MUST NOT begin while any `aborted-*` task for this Issue is `pending`.** | gate | L428 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-116 | **When the mover was an Engineer** — **in fix mode this should not occur**; treat it as a **precondition breach**, recover through the ordering here, and note the breach rather than absorbing it silently. | recovery | L432 `#### Reconciliation loop` | breach note | - | Engineer-dispatch precondition | none | no | procedure |
| F3-117 | On an Engineer mover, Phase A must **re-close first** (finish Engineer → Code Reviewer loop); only then re-dispatch the writer. Re-dispatching against a moving diff reproduces the abort. | ordering | L432 `#### Reconciliation loop` | dispatches | - | Phase A | Agent | unknown | procedure |
| F3-118 | The `aborted-*` task holds Phase C shut throughout and does not block that Engineer round (different name class from the precondition's prefixes). | invariant | L432 `#### Reconciliation loop` | - | TaskList | Engineer-dispatch precondition | TaskList | unknown | procedure |
| F3-119 | **When the mover was the sibling Phase B Test Writer's discrimination experiment**: `agents/test-writer.md` sanctions in-place perturbation with `Edit` / `Write` (restored after) and requires a `## Perturbations` heading listing every perturbed path, `None` when none. | definition | L433 `#### Reconciliation loop` | - | `## Perturbations` | `agents/test-writer.md` | none | unknown | procedure |
| F3-120 | Read the Test Writer's `## Perturbations`: when it lists **every** path the aborted writer reported, the movement is attributed; **re-dispatch the aborted lane once that sibling has returned, with no gate**. | recovery | L433 `#### Reconciliation loop` | writer re-dispatch | `## Perturbations` | - | Agent | unknown | procedure |
| F3-121 | When `## Perturbations` covers only **some** of the moved paths, fall through to the external-actor case for the remainder. | recovery | L433 `#### Reconciliation loop` | - | `## Perturbations` | external-actor case | none | unknown | procedure |
| F3-122 | **When a Test Writer was dispatched in Phase B and has not returned yet, do not classify and do not fire the gate**; wait for its completion notification, read `## Perturbations`, classify then. | ordering | L433 `#### Reconciliation loop` | - | Agent notification | - | Agent | unknown | procedure |
| F3-123 | The perturbation case fails once every dispatched Test Writer has returned and none lists the moved path; fall through to the external-actor case. | recovery | L433 `#### Reconciliation loop` | - | `## Perturbations` | external-actor case | none | unknown | procedure |
| F3-124 | The perturbation case **never applies when Phase B dispatched no Test Writer** (doc-only Issue); do not wait for a notification that is not coming; fall through to external-actor. | recovery | L433 `#### Reconciliation loop` | - | - | external-actor case | none | unknown | procedure |
| F3-125 | **When the mover was an external actor** (user, second session, background process): re-dispatch the writer once the movement is understood, i.e. the current diff is read and the tree has settled. | recovery | L434 `#### Reconciliation loop` | writer re-dispatch | git diff | - | git, Agent | unknown | procedure |
| F3-126 | When the movement is **unexplained**, fire the **unexplained-movement gate** instead of re-dispatching into it. | gate | L434 `#### Reconciliation loop` | gate | - | **Unexplained-movement gate** | AskUserQuestion, TaskList | unknown | procedure |
| F3-127 | Every movement re-dispatch is a repeat dispatch and takes the next `-r<n>` name (`test-writer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`, …). | name-class | L436 `#### Reconciliation loop` | TaskList task | - | TaskList naming convention | TaskList | unknown | procedure |
| F3-128 | Carry the writer's "how far I got" report (the `aborted-*` task's `metadata.activity`) into the re-dispatch prompt so the fresh Agent does not start from zero. | relay | L436 `#### Reconciliation loop` | re-dispatch prompt | `metadata.activity` | - | TaskList, Agent | unknown | procedure |
| F3-129 | **When the re-dispatched lane returns a normal deliverable, mark the `aborted-*` task `completed`** — that releases Phase C. | command | L436 `#### Reconciliation loop` | `aborted-*` `completed` | writer return | - | TaskList | unknown | procedure |
| F3-130 | If the re-dispatched lane aborts again, repeat the rung: mark its `-r<n>` task `completed` and refresh the **existing** `aborted-*` task's `metadata.activity`; never create a second one. | recovery | L436 `#### Reconciliation loop` | `metadata.activity` refresh | writer return | - | TaskList | unknown | procedure |
| F3-131 | **Unexplained-movement gate.** Movement is unexplained when no Engineer was dispatched over the window, no returned Test Writer's `## Perturbations` covers the paths (including no Test Writer at all), no Test Writer is in flight, and no other account exists. | definition | L438 `#### Reconciliation loop` | - | TaskList, `## Perturbations` | - | TaskList | unknown | procedure |
| F3-132 | Do not re-dispatch blindly; a blind re-dispatch loop is the failure mode this branch prevents. | invariant | L438 `#### Reconciliation loop` | - | - | - | none | unknown | procedure |
| F3-133 | Fire the gate via the two-step contract: **first** create a `gate-askuserquestion-<short-suffix>` task naming the unexplained-movement gate, **then** call `AskUserQuestion` in the same turn. | gate | L438 `#### Reconciliation loop` | `gate-askuserquestion-<short-suffix>` task, gate | - | TaskList naming convention | TaskList, AskUserQuestion | unknown | procedure |
| F3-134 | Do not produce a text response describing the gate; fire the two calls. | invariant | L438 `#### Reconciliation loop` | - | - | - | TaskList, AskUserQuestion | unknown | procedure |
| F3-135 | Do not yield to the harness while the `gate-*` task is `pending` or `in_progress` (yield-control discipline). | invariant | L438 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-136 | The question text carries the writer's movement report **verbatim** (files moved, opening/closing HEAD, how far the work got). | field-or-template | L440 `#### Reconciliation loop` | gate question text | writer return | - | AskUserQuestion | unknown | procedure |
| F3-137 | The question text adds the one-line statement: *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths … so it cannot attribute the movement.* | field-or-template | L440 `#### Reconciliation loop` | gate question text | - | - | AskUserQuestion | unknown | procedure |
| F3-138 | Offer exactly three options; the gate is multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` and `Chat about this`. | choice-set | L440 `#### Reconciliation loop` | gate options | - | - | AskUserQuestion | unknown | procedure |
| F3-139 | Option **Re-dispatch the writer now**: re-dispatch the lane under its next `-r<n>` name against the current tree. | choice-set | L442 `#### Reconciliation loop` | writer re-dispatch | gate answer | - | AskUserQuestion, Agent | unknown | procedure |
| F3-140 | Option **Wait**: yield control; re-fire this gate **only on the operator's reply** — that reply is the only trigger. | choice-set | L443 `#### Reconciliation loop` | - | gate answer | - | AskUserQuestion | unknown | procedure |
| F3-141 | Do **not** read Wait as "no Agent is in flight": the concurrently-dispatched sibling Phase B lane may complete seconds later. | invariant | L443 `#### Reconciliation loop` | - | - | - | Agent | unknown | procedure |
| F3-142 | **A sibling lane's completion notification is a tick that processes that lane normally** (persist result, mark task `completed`) and **MUST NOT** re-fire the gate. | invariant | L443 `#### Reconciliation loop` | task `completed` | Agent notification | Reconcile step | TaskList, Agent | unknown | procedure |
| F3-143 | Do not record the Wait state in `metadata.activity` and route on it; the re-fire rule derives from the tick's trigger and needs no bookkeeping. | invariant | L443 `#### Reconciliation loop` | - | `metadata.activity` | - | TaskList | unknown | procedure |
| F3-144 | During Wait the `aborted-*` task stays `pending`, so Phase C stays shut. | invariant | L443 `#### Reconciliation loop` | - | TaskList | - | TaskList | unknown | procedure |
| F3-145 | Option **Abort this Issue**: the Issue stays `open` and nothing is committed for it. | choice-set | L444 `#### Reconciliation loop` | - | gate answer | - | AskUserQuestion, bees | no | procedure |
| F3-146 | On Abort, do **not** simply move to the next Issue; route through Section 7's **`#### Aborted-Issue close-out`** (prefix sweep of this Issue's tasks incl. the `aborted-*` marker, Section 7.5 deferral-hygiene gate, **Issue-boundary state-externalization checkpoint** aborted path). | recovery | L444 `#### Reconciliation loop` | - | - | Section 7 `#### Aborted-Issue close-out`, Section 7.5 | TaskList | no | procedure |
| F3-147 | In batch mode with a next Issue remaining, Abort **stops the run**, naming the uncommitted working-tree state and the fresh-session resume command for the unfixed subset (that sub-step's step 4). | recovery | L444 `#### Reconciliation loop` | stop-run message | - | Section 7 `#### Aborted-Issue close-out` step 4 | none | no | procedure |
| F3-148 | An aborted Issue does not hand its dirty tree to the next Issue in the batch, unlike a fixed one. | invariant | L444 `#### Reconciliation loop` | - | - | - | git | no | procedure |
| F3-149 | Mark the `gate-*` task `completed` the moment the answer is consumed and the branch entered, including on **Wait** (consuming means yielding). | command | L446 `#### Reconciliation loop` | gate task `completed` | gate answer | - | TaskList | unknown | procedure |
| F3-150 | A re-fire on a later tick creates a **fresh** `gate-askuserquestion-<short-suffix>` task rather than reusing the closed one. | name-class | L446 `#### Reconciliation loop` | new gate task | - | - | TaskList | unknown | procedure |
| F3-151 | For every Agent that reported completion: confirm any bees transitions it committed to, mark its TaskList task `completed`, and unlock the next phase or lane per the ladder. | command | L448 `#### Reconciliation loop` | task `completed` | Agent return, bees | phase ladder | TaskList, bees | unknown | procedure |
| F3-152 | **A Phase B writer return that reports detected source movement is not a completion**; route it through the movement-report rung; it does not unlock the next phase. | invariant | L448 `#### Reconciliation loop` | - | writer return | movement-report rung | TaskList | unknown | procedure |
| F3-153 | **An Engineer return carrying a `## Design question` is not a Phase A completion either.** | invariant | L450 `#### Reconciliation loop` | - | Engineer return | `agents/engineer.md` | none | no | procedure |
| F3-154 | `agents/engineer.md` requires the Engineer to stop rather than invent an unenumerated mechanism; such a return means the proposal's `### Blast radius` **missed a mechanism** — a revision of that proposal, not a new decision point. | definition | L450 `#### Reconciliation loop` | - | Engineer return | `agents/engineer.md` | none | no | procedure |
| F3-155 | On a `## Design question` return, mark the Engineer's task `completed` and do **not** dispatch the Code Reviewer against the partial diff. | command | L450 `#### Reconciliation loop` | task `completed` | Engineer return | - | TaskList | no | procedure |
| F3-156 | Route the question as a **Section 3 Revise, by reference**. | ordering | L450 `#### Reconciliation loop` | - | - | Section 3 Revise | none | no | procedure |
| F3-157 | **Re-dispatch the Analyst exactly as Section 3's Revise branch prescribes**: next `analyst-<issue-id>-rev<n>` name, same Issue body verbatim, same `reference_materials`, and a `## Prior proposal and user feedback` section quoting the approved proposal in full. | field-or-template | L452 `#### Reconciliation loop` | Analyst dispatch, `analyst-<issue-id>-rev<n>` task | Design Proposal, `reference_materials` | Section 3 Revise branch | TaskList, Agent | no | procedure |
| F3-158 | **"In full" includes its `### Deferred refinements` block** (which Section 3 strips from user-facing prose) so the revising Analyst carries forward or explicitly drops each deferral. | field-or-template | L452 `#### Reconciliation loop` | Analyst prompt | `### Deferred refinements` | Section 3 supersede-and-clear rule, `defer-*` | none | no | procedure |
| F3-159 | **In place of the user's revision feedback**, send the Engineer's `## Design question` verbatim (mechanism needed, why blocked, alternatives, which parts landed and which did not). | field-or-template | L452 `#### Reconciliation loop` | Analyst prompt | `## Design question` | - | none | no | procedure |
| F3-160 | The re-dispatch prompt MUST state a **partial implementation of the prior directive is already on disk**, naming the Engineer's `## Files changed` list, so the Analyst reads the tree as mid-change. | field-or-template | L452 `#### Reconciliation loop` | Analyst prompt | `## Files changed` | - | none | no | procedure |
| F3-161 | The re-dispatch prompt MUST state that the revised `### Blast radius` has to cover the lifecycle of whatever mechanism it now enumerates. | field-or-template | L452 `#### Reconciliation loop` | Analyst prompt | - | - | none | no | procedure |
| F3-162 | **When the approved Design Proposal is no longer readable**, use the **re-derivation shape** from the Read-state step, adding only the `## Design question` as the feedback in `## Prior proposal and user feedback`. | recovery | L454 `#### Reconciliation loop` | Analyst prompt | re-derivation shape | Read-state step | none | no | procedure |
| F3-163 | **When the Analyst returns, run Section 3's surface-and-gate flow unchanged**: verdict preamble, two-step gate, three options exactly as Section 3 defines. | ordering | L455 `#### Reconciliation loop` | gate | Analyst return | Section 3 | TaskList, AskUserQuestion | no | procedure |
| F3-164 | Branches are Section 3's own: **Approve** captures the revised directive (supersede-and-clear applies), **Revise** loops, **Cancel** routes through Section 7's **`#### Aborted-Issue close-out`**. | choice-set | L455 `#### Reconciliation loop` | - | gate answer | Section 3, Section 7 `#### Aborted-Issue close-out` | AskUserQuestion | no | procedure |
| F3-165 | After Approve, re-dispatch the Engineer under its next `-r<n>` name carrying the revised directive and a note that it continues from the partial diff on disk. | command | L455 `#### Reconciliation loop` | Engineer dispatch, `engineer-<issue-id>-r<n>` task | revised directive | TaskList naming convention | TaskList, Agent | no | procedure |
| F3-166 | **The durable carrier is the Analyst task**: the active `analyst-<issue-id>-rev<n>` task holds Phase A suspended; on return it is marked `completed` per Section 3 and the gate task carries the suspension until a branch is entered. | invariant | L456 `#### Reconciliation loop` | - | TaskList | Section 3 | TaskList | no | procedure |
| F3-167 | Once the re-dispatch lands, nothing about the question lives only in conversation; the residual window (Engineer return to re-dispatch) costs a Code Reviewer round on a partial diff, not a mis-completion. | failure-narrative | L456 `#### Reconciliation loop` | - | - | Read-state step resume arms | none | no | failure-narrative |
| F3-168 | The design-question receiver introduces no gate, option, task-name class, marker, or manifest field of its own; it is Section 3's Revise branch entered from Section 4. | invariant | L458 `#### Reconciliation loop` | - | - | Section 3, Section 4 | none | no | procedure |
| F3-169 | **Yield.** Do not poll; after dispatching this tick's work, return control and wait for the **Agent completion notification** from the `run_in_background=true` substrate, which triggers the next tick. | ordering | L460 `#### Reconciliation loop` | - | Agent notification | - | Agent | unknown | procedure |
| F3-170 | Do **not** use **`/loop`** (repeats last turn on wall-clock cadence). | invariant | L466 `##### Anti-pattern: no clock primitives` | - | - | - | none | unknown | procedure |
| F3-171 | Do **not** use **`ScheduleWakeup`** (fires after a delay). | invariant | L467 `##### Anti-pattern: no clock primitives` | - | - | - | none | unknown | procedure |
| F3-172 | Do **not** use **`CronCreate`** (fires on a recurring schedule). | invariant | L468 `##### Anti-pattern: no clock primitives` | - | - | - | none | unknown | procedure |
| F3-173 | Do **not** poll: no re-reading bees / TaskList / git on a sleep-wait cycle without a triggering event. | invariant | L469 `##### Anti-pattern: no clock primitives` | - | - | - | none | unknown | procedure |
| F3-174 | If this tick's work is dispatched and nothing else needs reconciling, yield; background Agents finishing is the only legitimate trigger for the next tick. | ordering | L471 `##### Anti-pattern: no clock primitives` | - | - | - | Agent | unknown | procedure |
| F3-175 | For each Issue, spawn one fresh Agent per role at issue scope: `Agent(subagent_type=<role>, run_in_background=true, prompt=<...>)`. | command | L475-L483 `#### Per-issue cold dispatch` | Agent dispatch | - | - | Agent | unknown | procedure |
| F3-176 | Implementer `subagent_type` is one of `engineer`, `test-writer`, `doc-writer`. | choice-set | L479 `#### Per-issue cold dispatch` | - | - | - | Agent | unknown | procedure |
| F3-177 | The dispatch prompt embeds the issue body verbatim and Section 3's design directive as the authoritative design source. | field-or-template | L481 `#### Per-issue cold dispatch` | dispatch prompt | Issue body, design directive | Section 3 | Agent | no | procedure |
| F3-178 | Each role gets its own Agent invocation; do **not** use `Agent(name=...)`; do **not** reuse an Agent across roles. | invariant | L485 `#### Per-issue cold dispatch` | - | - | - | Agent | unknown | procedure |
| F3-179 | No `SendMessage` between roles; the worker reads its prompt, edits files, exits; the diff is the handoff to the next role. | invariant | L485 `#### Per-issue cold dispatch` | - | - | - | Agent | unknown | procedure |
| F3-180 | **Engineer** is dispatched in **Phase A** when source needs modification, alone, looping with the Code Reviewer; never while a task prefixed `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, or `analyst-<issue-id>` is active. | ordering | L489 `#### Per-issue cold dispatch` | Engineer dispatch | TaskList | **Engineer-dispatch precondition** | TaskList, Agent | no | procedure |
| F3-181 | **Test Writer** is dispatched in **Phase B**, once, when tests need modification. | ordering | L490 `#### Per-issue cold dispatch` | Test Writer dispatch | - | - | Agent | unknown | procedure |
| F3-182 | **Doc Writer** is dispatched in **Phase B**, once, always; it decides whether docs need updating; the orchestrator does not pre-judge. | ordering | L491 `#### Per-issue cold dispatch` | Doc Writer dispatch | - | - | Agent | unknown | procedure |
| F3-183 | The Product Manager is not an implementer-phase role; it is dispatched in **Phase C** alongside the remaining reviewers on every Issue (Section 5). | ordering | L493 `#### Per-issue cold dispatch` | PM dispatch | - | Section 5 | Agent | unknown | procedure |
| F3-184 | Reviewer and PM Agents take dispatch shape and TaskList naming from Section 5; **Code Reviewer** in **Phase A** interleaved with the Engineer; **Test Reviewer**, **Doc Reviewer**, **PM** in **Phase C**. | ordering | L495 `#### Per-issue cold dispatch` | - | - | Section 5 | Agent | unknown | procedure |
| F3-185 | Warm `SendMessage` dispatch (the SDD's original intent) requires the experimental teams substrate this skill set does not use; cold dispatch is a conscious trade-off tracked by a re-probe issue. | rationale-only | L497-L499 `##### Per-issue cold dispatch (vs SDD's warm-Agent intent)` | - | - | Claude Code sub-agents docs | none | unknown | rationale |
| F3-186 | The dispatch prompt must embed the Issue body **verbatim**; paraphrasing corrupts identifier names the worker uses literally. | invariant | L503 `##### Dispatch prompt: quote the issue body verbatim and embed the design directive` | dispatch prompt | Issue body | - | Agent | unknown | procedure |
| F3-187 | Read the Issue via `bees show-ticket --ids <issue-id>`. | command | L505-L507 `##### Dispatch prompt` | - | Issue id | - | bees | unknown | procedure |
| F3-188 | Embed the returned body as a quoted block; do not summarise, paraphrase, or "clean up" identifier spellings; framing prose around the block is fine. | invariant | L509 `##### Dispatch prompt` | dispatch prompt | Issue body | - | Agent | unknown | procedure |
| F3-189 | The dispatch prompt need not ask the worker to ping back; Agent completion notifications arrive automatically and TaskList is the progress signal. | invariant | L509 `##### Dispatch prompt` | - | - | "TaskList as progress UI" | Agent, TaskList | unknown | procedure |
| F3-190 | **Engineer dispatch** MUST embed the Section 3 Approve-branch directive: `### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`, plus `### Why`, `### Alternatives considered`, `### Options the body did not consider`, plus user-supplied refinement. | field-or-template | L511 `##### Dispatch prompt` | Engineer prompt | Section 3 Approve output | Section 3 | Agent | no | procedure |
| F3-191 | Recommended labels: `## Authoritative design directive (from Section 3 Analyst pass)` for the three directive sections and `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)` for context. | field-or-template | L511 `##### Dispatch prompt` | Engineer prompt headings | - | - | Agent | no | procedure |
| F3-192 | **Relay the `### Blast radius` section under the heading `## Blast radius`** inside the directive block; it is the **enumerated site list** `agents/engineer.md` reconciles its sweep against. | relay | L511 `##### Dispatch prompt` | `## Blast radius` heading | `### Blast radius` | `agents/engineer.md` | Agent | no | procedure |
| F3-193 | **State in the prompt that the directive is the enumeration**: an unnamed mechanism is a design question the Engineer returns under `## Design question`, not a choice it makes. | field-or-template | L511 `##### Dispatch prompt` | Engineer prompt | - | `agents/engineer.md`, design-question rung | Agent | no | procedure |
| F3-194 | Where the Issue body's framing and the directive conflict, **the directive wins**; the body still flows verbatim for byte-accurate identifiers. | invariant | L511 `##### Dispatch prompt` | - | Issue body, directive | - | none | no | procedure |
| F3-195 | `agents/engineer.md` carries the same directive-wins invariant in its **Authoritative design directive (fix mode only)** bullet, reloaded on every cold dispatch. | definition | L511 `##### Dispatch prompt` | - | - | `agents/engineer.md` **Authoritative design directive (fix mode only)** | none | no | procedure |
| F3-196 | Test Writer and Doc Writer prompts do NOT carry the design directive separately; they read the resulting diff per hub-and-spoke. | invariant | L511 `##### Dispatch prompt` | - | - | hub-and-spoke | Agent | no | procedure |
| F3-197 | **Code Reviewer dispatch:** when an Engineer's return carried a completeness list, the Phase A Code Reviewer prompt MUST embed it verbatim under `## Engineer's completeness evidence`. | relay | L513 `##### Dispatch prompt` | `## Engineer's completeness evidence` | Engineer completeness evidence | `agents/engineer.md`, `agents/code-reviewer.md` | Agent | unknown | procedure |
| F3-198 | Embed the completeness list as text in the prompt; do **not** write it to a scratch file and pass a path. | invariant | L513 `##### Dispatch prompt` | - | - | - | Agent | unknown | procedure |
| F3-199 | `agents/code-reviewer.md` carries the Code-Reviewer-side half: pass the list through into its `/quo-engineer-review` invocation. | definition | L513 `##### Dispatch prompt` | - | - | `agents/code-reviewer.md`, `/quo-engineer-review` | none | unknown | procedure |
| F3-200 | **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was** — a fact known independently of whether a list came back. | field-or-template | L513 `##### Dispatch prompt` | Code Reviewer prompt | assignment shape | `/quo-engineer-review` sweep-verification check | Agent | unknown | procedure |
| F3-201 | When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emit an empty one, but still state sweep-shaped when true. | field-or-template | L513 `##### Dispatch prompt` | Code Reviewer prompt | - | - | Agent | unknown | procedure |
| F3-202 | **Unlike the `### Blast radius` relay, this MUST is not satisfiable on every path**: a compaction after the Engineer returned destroys the list; on that resume omit the heading and state the sweep-shaped fact. | recovery | L513 `##### Dispatch prompt` | - | - | - | none | unknown | procedure |
| F3-203 | **State the cost plainly:** on that dispatch `/quo-engineer-review` will report the completeness list as missing; that finding is a **compaction artifact, not an Engineer defect**. | definition | L513 `##### Dispatch prompt` | - | `/quo-engineer-review` finding | `/quo-engineer-review` | none | unknown | procedure |
| F3-204 | Disposition the compaction-artifact finding as ignored feedback per **Section 5's ignored-feedback rule**: a `defer-<short-suffix>` task annotated `addressed-now-in-this-Issue`, left `pending`, listed in the per-Issue summary's `**Ignored Review Feedback**` field; do not auto-dispatch the Engineer per part (a)'s table. | recovery | L513 `##### Dispatch prompt` | `defer-<short-suffix>` task, summary field | finding | Section 5 ignored-feedback rule, Section 7.5, part (a) of `### Orchestrator discipline: routing review findings` | TaskList | unknown | procedure |
| F3-205 | **Code Reviewer dispatch:** when Section 3's approved proposal carried `### Blast radius`, the Phase A Code Reviewer prompt MUST embed it **verbatim** under the heading `## Blast radius`. | relay | L515 `##### Dispatch prompt` | `## Blast radius` heading | `### Blast radius` | Section 3 | Agent | no | procedure |
| F3-206 | Use the one heading string `## Blast radius` at every hop; a renamed heading silently drops the review's check. | invariant | L515 `##### Dispatch prompt` | - | - | completeness-evidence chain | none | no | procedure |
| F3-207 | Embed `## Blast radius` as text in the prompt; do **not** write it to a scratch file and pass a path. | invariant | L515 `##### Dispatch prompt` | - | - | - | Agent | no | procedure |
| F3-208 | **Relay it even when the Analyst's section carried only its fixed empty line** (`No invariant added, removed, or weakened.`), so "nothing to verify" is distinguishable from "not supplied". | relay | L515 `##### Dispatch prompt` | `## Blast radius` | `### Blast radius` | - | Agent | no | procedure |
| F3-209 | This `## Blast radius` MUST is satisfiable on every path: a compaction-stranded proposal is re-derived through the Analyst before this dispatch. | invariant | L515 `##### Dispatch prompt` | - | - | Read-state step | none | no | procedure |
| F3-210 | `agents/code-reviewer.md` forwards the `## Blast radius` block into its `/quo-engineer-review` invocation under the same heading. | definition | L515 `##### Dispatch prompt` | - | - | `agents/code-reviewer.md`, `/quo-engineer-review` | none | no | procedure |
| F3-211 | **Test Writer / Doc Writer dispatch** prompts MAY state **"no Engineer Agent will be dispatched for this Issue while you are running"**; keep the `for this Issue` qualifier (fix-mode wording the role files expect). | field-or-template | L517 `##### Dispatch prompt` | writer prompt | - | Engineer-dispatch precondition, `agents/test-writer.md`, `agents/doc-writer.md` | Agent | no | procedure |
| F3-212 | Writer prompts **MUST NOT** claim **"the source tree is frozen"** or any close paraphrase; the orchestrator holds no such lever. | invariant | L517 `##### Dispatch prompt` | - | - | - | Agent | unknown | procedure |
| F3-213 | `agents/test-writer.md` carries the writer-side half (capture tree state, re-check before finishing, stop and report), so recovery does not depend on prompt wording. | definition | L517 `##### Dispatch prompt` | - | - | `agents/test-writer.md` | none | unknown | procedure |
| F3-214 | **Test Writer dispatch — supply the fingerprint path list** by carrying forward the Engineer's `## Files changed`, **not by re-deriving from the tree**. | field-or-template | L519 `##### Dispatch prompt` | Test Writer prompt | `## Files changed` | `agents/test-writer.md`, `agents/engineer.md` | Agent | unknown | procedure |
| F3-215 | **Union the lists across every Phase A round**, drop test paths, emit under `## Source paths to fingerprint`, one repository-relative path per line, non-test paths only. | field-or-template | L519 `##### Dispatch prompt` | `## Source paths to fingerprint` | `## Files changed` (all rounds) | - | Agent | unknown | procedure |
| F3-216 | **An explicitly-empty `## Files changed` list is a list, not a missing one**; it contributes nothing to the union and does **not** trigger the fallback. | invariant | L519 `##### Dispatch prompt` | - | `## Files changed` | - | none | unknown | procedure |
| F3-217 | When every round carried a list and the union is empty, **omit the `## Source paths to fingerprint` heading**; the writer's empty-path-set clause keys on the heading being absent. | field-or-template | L519 `##### Dispatch prompt` | Test Writer prompt | - | `agents/test-writer.md` | Agent | unknown | procedure |
| F3-218 | **Fallback when an Engineer return did not list files:** run `git diff --name-only HEAD` (identical on POSIX and PowerShell) and drop test paths. | command | L521-L531 `##### Dispatch prompt` | path list | working tree | - | git, Bash | unknown | procedure |
| F3-219 | Prefer the return-carried list; the fallback reads the **whole working tree** and picks up other actors' uncommitted edits, each of which the writer will stop on. | invariant | L533 `##### Dispatch prompt` | - | - | - | git | unknown | procedure |
| F3-220 | When Phase A was empty (no Engineer ran), omit the `## Source paths to fingerprint` heading; `agents/test-writer.md` handles that case. | field-or-template | L533 `##### Dispatch prompt` | Test Writer prompt | - | `agents/test-writer.md` | Agent | unknown | procedure |
| F3-221 | Framing prose MUST NOT loosen the role boundaries in the dispatched role's `agents/<role>.md`; this applies to **every** role, implementer and review-only alike. | invariant | L535 `##### Dispatch prompt` | - | `agents/<role>.md` | `agents/<role>.md` | Agent | unknown | procedure |
| F3-222 | MUST NOT tell the Engineer it may also write tests or docs. | invariant | L537 `##### Dispatch prompt` | - | - | - | Agent | unknown | example |
| F3-223 | MUST NOT tell the Test Writer it may also modify source code. | invariant | L538 `##### Dispatch prompt` | - | - | - | Agent | unknown | example |
| F3-224 | MUST NOT tell the Doc Writer it may also modify source or test files. | invariant | L539 `##### Dispatch prompt` | - | - | - | Agent | unknown | example |
| F3-225 | MUST NOT tell the PM or any reviewer it may write source, tests, or docs; contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (reviewers). | invariant | L540 `##### Dispatch prompt` | - | - | `agents/pm.md`, reviewer role files | Agent | unknown | example |
| F3-226 | MUST NOT tell one reviewer it may also review another reviewer's lane. | invariant | L541 `##### Dispatch prompt` | - | - | - | Agent | unknown | example |
| F3-227 | A temptation to carve a role exception signals a need for orchestrator-level coordination (follow-up dispatch, Issue redirect), NOT a softening clause. | invariant | L543 `##### Dispatch prompt` | - | - | - | Agent | unknown | procedure |
| F3-228 | The only handoff is worker to orchestrator (diff in execution mode, JSON return in research mode); "coordinate with the other role's diff" prose cannot make softening safe because that channel does not exist. | invariant | L543 `##### Dispatch prompt` | - | - | - | Agent | unknown | procedure |
| F3-229 | When the Issue's `reference_materials` is non-empty, embed the `reference_materials` JSON value alongside the thin body in the dispatch prompt so the worker can read resolver name and URL. | relay | L545 `##### Dispatch prompt` | dispatch prompt | `reference_materials` | `/quo-file-issue` | Agent, bees | no | procedure |
| F3-230 | All URL entry surfaces (`/quo-file-issue <url>`, `--reference <url>`, `--from-github <url>`, this skill's URL-resolution sub-step inline Skill dispatch) produce the same `reference_materials` shape. | definition | L545 `##### Dispatch prompt` | - | - | `/quo-file-issue`, URL-resolution sub-step | none | no | procedure |
| F3-231 | Workers (Analyst in Section 3, Engineer in Section 4, PM in Section 5) fetch upstream content via `WebFetch` per their role contracts; the orchestrator does not pre-fetch the URL. | invariant | L545 `##### Dispatch prompt` | - | `reference_materials` | `agents/analyst.md`, `agents/engineer.md`, `agents/pm.md` | Agent | no | procedure |
| F3-232 | Hub-and-spoke: workers do not message each other; the orchestrator is the hub; the diff is the handoff (Code Reviewer in Phase A; Test Writer, Doc Writer, or PM after Phase A closes). | invariant | L549 `#### Hub-and-spoke via substrate` | - | - | - | Agent | unknown | procedure |
| F3-233 | Hub-and-spoke is a **structural property** of ephemeral background Agents, not a rule to enforce; no inter-Agent channel exists. | rationale-only | L549 `#### Hub-and-spoke via substrate` | - | - | - | none | unknown | rationale |
| F3-234 | "Subagents cannot spawn other subagents"; the skill ships **flat orchestration** — every Agent invocation originates from this reconciliation loop, never from a worker. | invariant | L553 `#### Recursive delegation: not supported` | - | - | Claude Code sub-agents docs | Agent | unknown | procedure |
| F3-235 | Orchestrator context grows **monotonically within a session** (across the batch in `all` / list mode); **nothing in this skill reclaims those tokens**; the harness owns compaction; the skill has no model-invocable clear/compact. | definition | L555 `#### Recursive delegation: not supported` | - | - | - | none | unknown | rationale |
| F3-236 | Growth is **survivable** because Section 7 step 5's **Issue-boundary state-externalization checkpoint** keeps every load-bearing fact in a durable carrier; the reclamation lever is a **fresh session** per the fresh-session-per-phase recommendation. | definition | L555 `#### Recursive delegation: not supported` | - | - | Section 7 step 5, run close-out | none | unknown | procedure |
| F3-237 | The orchestrator dispatches three implementer roles per Issue; the role contracts live in the role files; the orchestrator invokes the right role at the right time, not carry the role's prose. | definition | L559 `#### Roles dispatched by the orchestrator` | - | - | role files | Agent | unknown | procedure |
| F3-238 | **Engineer** (`agents/engineer.md`) implements source-code changes for the fix; Model: Opus (always); does not write tests or docs. | definition | L561 `#### Roles dispatched by the orchestrator` | - | - | `agents/engineer.md` | Agent | unknown | procedure |
| F3-239 | **Test Writer** (`agents/test-writer.md`) writes/updates/deletes tests and ensures at least one test fails before the fix and passes after; Model: Opus (always). | definition | L562 `#### Roles dispatched by the orchestrator` | - | - | `agents/test-writer.md` | Agent | unknown | procedure |
| F3-240 | **Doc Writer** (`agents/doc-writer.md`) reviews the diff for doc gaps, updates docs, and appends/updates the `### Feature: <title>` subsection in cumulative PRD/SDD per CLAUDE.md `## Documentation Locations`; Model: Opus (always). | definition | L563 `#### Roles dispatched by the orchestrator` | - | CLAUDE.md `## Documentation Locations` | `agents/doc-writer.md` | Agent | unknown | procedure |
| F3-241 | In fix mode the Doc Writer is dispatched once per Issue (not per Subtask), and the Plan Bee is discovered via the Issue's `up_dependencies`; `agents/doc-writer.md` is authoritative for that traversal. | definition | L563 `#### Roles dispatched by the orchestrator` | - | `up_dependencies` | `agents/doc-writer.md` | none | no | procedure |
| F3-242 | When the Issue body contains a `## Doc divergence noted` section (from `/quo-file-issue`), the Doc Writer treats it as an explicit doc-correction directive. | definition | L563 `#### Roles dispatched by the orchestrator` | - | `## Doc divergence noted` | `/quo-file-issue`, `agents/doc-writer.md` | none | no | procedure |
| F3-243 | Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) and the PM (`agents/pm.md`) are introduced in Section 5; the PM is always dispatched alongside the reviewers. | definition | L565 `#### Roles dispatched by the orchestrator` | - | - | Section 5, four role files | Agent | unknown | procedure |
| F3-244 | Use Claude Code's native **TaskList** as the visible progress UI; there is no separate display backend to configure. | invariant | L569 `#### TaskList as progress UI` | - | - | - | TaskList | unknown | procedure |
| F3-245 | For every dispatched Agent, create exactly **one** TaskList task. | invariant | L571 `#### TaskList as progress UI` | TaskList task | - | - | TaskList | unknown | procedure |
| F3-246 | **`pending`** — created when the orchestrator decides the role is next for the current Issue, before the Agent invocation lands. | definition | L573 `#### TaskList as progress UI` | task status | - | - | TaskList | unknown | procedure |
| F3-247 | **`in_progress`** — set the moment `Agent(...)` returns. | definition | L574 `#### TaskList as progress UI` | task status | Agent dispatch | - | TaskList, Agent | unknown | procedure |
| F3-248 | **`completed`** — set when the completion notification is processed and deliverables are confirmed landed (`git status` / `git diff`, bees transitions on disk). | definition | L575 `#### TaskList as progress UI` | task status | Agent notification, git, bees | - | TaskList, git, bees | unknown | procedure |
| F3-249 | **One exception:** a writer lane returning a movement report is set `completed` **without** landed deliverables; `completed` means "this Agent is gone", not "this work shipped". | definition | L575 `#### TaskList as progress UI` | task status | - | Section 4 movement-report rung, `aborted-*` | TaskList | unknown | procedure |
| F3-250 | Use `metadata.activity` for finer-grained progress from intermediate worker signal; update opportunistically; it is informational, not a routing input. | invariant | L577 `#### TaskList as progress UI` | `metadata.activity` | - | - | TaskList | unknown | procedure |
| F3-251 | The naming convention is the **canonical cross-reference** for Section 5 (reviewer dispatches) and Section 7 (TaskList completion at close-out); it is deterministic and unambiguous. | definition | L581 `##### TaskList naming convention` | - | - | Section 5, Section 7 | TaskList | unknown | procedure |
| F3-252 | Naming is **issue-scoped** for every per-issue role; the scope suffix is always the Issue id. | invariant | L583 `##### TaskList naming convention` | - | Issue id | - | TaskList | no | procedure |
| F3-253 | URL-resolution Skill-tool dispatches run before per-issue dispatch, so they use a positional-index discriminator instead of an Issue id. | name-class | L583 `##### TaskList naming convention` | - | - | Section 1 URL-resolution sub-step | TaskList | no | procedure |
| F3-254 | **Analyst Agents**: `analyst-<issue-id>` (e.g. `analyst-veq` for Issue `b.veq`). | name-class | L585 `##### TaskList naming convention` | TaskList task name | - | Section 3 | TaskList | no | procedure |
| F3-255 | On `Revise`, append `-rev<n>` with `<n>` the 1-based revision count (`analyst-veq-rev1`, `analyst-veq-rev2`), per Section 3's Revise branch. | name-class | L585 `##### TaskList naming convention` | TaskList task name | gate answer `Revise` | Section 3 Revise branch | TaskList | no | procedure |
| F3-256 | The same `-rev<n>` discriminator is used when Section 4's **design-question rung** re-dispatches the Analyst. | name-class | L585 `##### TaskList naming convention` | TaskList task name | - | design-question rung | TaskList | no | procedure |
| F3-257 | **Implementer Agents**: `<role>-<issue-id>` (`engineer-veq`, `test-writer-veq`, `doc-writer-veq`). | name-class | L586 `##### TaskList naming convention` | TaskList task name | - | - | TaskList | unknown | procedure |
| F3-258 | **Round discriminator for repeat dispatches**: every dispatch after the first appends `-r<n>`, `<n>` the 1-based re-dispatch count (`engineer-veq`, `engineer-veq-r1`, `engineer-veq-r2`, `doc-writer-veq-r1`). | name-class | L586 `##### TaskList naming convention` | TaskList task name | - | - | TaskList | unknown | procedure |
| F3-259 | `-r<n>` differs from `-rev<n>` because they count different things (review rounds vs Analyst revisions). | rationale-only | L586 `##### TaskList naming convention` | - | - | - | none | no | rationale |
| F3-260 | Because the discriminator is a **suffix**, every name-testing rule (most importantly the Engineer-dispatch precondition) matches on name **prefix** plus status. | invariant | L586 `##### TaskList naming convention` | - | TaskList | Engineer-dispatch precondition | TaskList | unknown | procedure |
| F3-261 | **Reviewer Agents**: `<reviewer>-<issue-id>` (`code-reviewer-veq`, `test-reviewer-veq`, `doc-reviewer-veq`); dispatch shape from Section 5. | name-class | L587 `##### TaskList naming convention` | TaskList task name | - | Section 5 | TaskList | unknown | procedure |
| F3-262 | Reviewer repeat dispatches take `-r<n>` (`code-reviewer-veq-r1` for the second Phase A review round), `<n>` the 1-based re-dispatch count. | name-class | L587 `##### TaskList naming convention` | TaskList task name | - | - | TaskList | unknown | procedure |
| F3-263 | **PM Agents**: `pm-<issue-id>` (`pm-veq`), dispatched per Issue in Section 5 alongside the reviewers. | name-class | L588 `##### TaskList naming convention` | TaskList task name | - | Section 5 | TaskList | unknown | procedure |
| F3-264 | **Aborted-writer redelivery markers**: `aborted-<role>-<issue-id>` (`aborted-test-writer-veq`, `aborted-doc-writer-veq`) at **Issue scope**; `aborted-<role>-postcomp-<n>` at **post-completion scope** with `<n>` the same finding index as the lane. | name-class | L589 `##### TaskList naming convention` | TaskList task name | - | Section 8 | TaskList | unknown | procedure |
| F3-265 | The aborted marker is created `pending` by the **movement-report rung** with the writer's "how far I got" report as `metadata.activity`, after the writer's own task is marked `completed`. | definition | L589 `##### TaskList naming convention` | `aborted-*` task | writer return | movement-report rung | TaskList | unknown | procedure |
| F3-266 | **This is not an Agent task**: the one-task-per-Agent rule and `-r<n>` do not apply; a second abort refreshes `metadata.activity` rather than opening another. | invariant | L589 `##### TaskList naming convention` | - | - | - | TaskList | unknown | procedure |
| F3-267 | It is an **obligation marker** like `defer-*` and `gate-*`: while `pending`, **Phase C must not begin** for this Issue. | gate | L589 `##### TaskList naming convention` | - | TaskList | `defer-*`, `gate-*` | TaskList | unknown | procedure |
| F3-268 | Mark the aborted marker `completed` when the re-dispatched lane (`<role>-<issue-id>-r<n>` or `<role>-postcomp-<n>-r<k>` per Section 8 step 6) returns a normal deliverable. | command | L589 `##### TaskList naming convention` | task `completed` | writer return | Section 8 step 6 | TaskList | unknown | procedure |
| F3-269 | The `aborted-` prefix is a distinct name class from `<role>-<issue-id>`, keeping markers out of the Engineer-dispatch precondition without an exemption clause. | rationale-only | L589 `##### TaskList naming convention` | - | - | Engineer-dispatch precondition | none | unknown | rationale |
| F3-270 | **URL-resolution Skill-tool dispatches**: `file-from-url-<n>`, `<n>` the 1-based index of the URL token in the positional-argument list (`file-from-url-1`, `file-from-url-2`); index, not URL, gives determinism. | name-class | L590 `##### TaskList naming convention` | TaskList task name | positional args | Section 1 URL-resolution sub-step | TaskList | no | procedure |
| F3-271 | `file-from-url-<n>` lifecycle: `pending` when deciding to dispatch `/quo-file-issue`; `in_progress` when the Skill dispatch lands; `completed` when `issue_ticket_id` is captured (`action` `created` or `reused-existing` via `Use existing`). | definition | L590 `##### TaskList naming convention` | task status | Skill return `issue_ticket_id`, `action` | `/quo-file-issue` | TaskList | no | procedure |
| F3-272 | On URL-resolution soft-fail or user-cancel, mark the entry `completed` (failure reason in `metadata.activity` if useful) and clear it, so the cumulative failure check at the upfront `bees show-ticket --ids` validation sees a clean active set. | recovery | L590 `##### TaskList naming convention` | task `completed` | - | Section 1 URL-resolution sub-step | TaskList, bees | no | procedure |
| F3-273 | **Deferral-ledger tasks** — **Run scope**: `defer-<short-suffix>` (`defer-1`, `defer-2`, or any collision-resistant suffix). | name-class | L591 `##### TaskList naming convention` | TaskList task name | - | - | TaskList | unknown | procedure |
| F3-274 | Create a `defer-*` task when a structured return (per `agents/pm.md` Final report or `agents/analyst.md` `### Deferred refinements`) names `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` not addressed inline. | command | L591 `##### TaskList naming convention` | `defer-*` task | PM/Analyst return | `agents/pm.md`, `agents/analyst.md` | TaskList | unknown | procedure |
| F3-275 | `metadata.activity` on a `defer-*` task carries the deferral's one-line description so the Section 7.5 gate can surface the active set. | field-or-template | L591 `##### TaskList naming convention` | `metadata.activity` | - | Section 7.5 | TaskList | unknown | procedure |
| F3-276 | Mark a `defer-*` task `completed` the moment the deferral is encoded in a durable carrier (updated ticket body, new Issue, or in-session resolution logged in `metadata.activity`). | command | L591 `##### TaskList naming convention` | task `completed` | - | - | TaskList, bees | unknown | procedure |
| F3-277 | The pre-handoff Section 7.5 gate reads the ledger and refuses to yield control while any `defer-*` entry is pending or in-progress. | gate | L591 `##### TaskList naming convention` | - | TaskList | Section 7.5 | TaskList | unknown | procedure |
| F3-278 | Post-completion names (`<role>-postcomp-<n>` / `file-issue-postcomp-<n>` per Section 8 step 6) and `defer-*` names coexist without overlap; they track different lifecycles. | definition | L591 `##### TaskList naming convention` | - | - | Section 8 step 6 | TaskList | unknown | procedure |
| F3-279 | **Gate-task tasks** — **Turn scope**: `gate-<kind>-<short-suffix>`; dominant `<kind>` is `askuserquestion` (`gate-askuserquestion-veq` for the Section 3 gate on `b.veq`, `gate-askuserquestion-1` otherwise). | name-class | L592 `##### TaskList naming convention` | TaskList task name | - | Section 3 | TaskList | unknown | procedure |
| F3-280 | Create the gate task via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract. | command | L592 `##### TaskList naming convention` | `gate-*` task | - | two-step contract | TaskList, AskUserQuestion | unknown | procedure |
| F3-281 | The `<short-suffix>` MUST be unique per fire within the run across every `gate-*` task regardless of `<kind>`; use monotonic integers or gate-specific slugs (Issue-ID-suffixed slugs are the slug pattern). | invariant | L592 `##### TaskList naming convention` | - | - | - | TaskList | unknown | procedure |
| F3-282 | The two-step contract applies at every gate: Section 5 escalation gates, Section 1's conditional session-effort gate (`Check session reasoning effort`), Section 3's approval gate, Section 4's **unexplained-movement gate**, Section 7.5's deferral-hygiene gate, Section 8's post-completion findings gate. | invariant | L592 `##### TaskList naming convention` | - | - | Sections 1, 3, 4, 5, 7.5, 8 | TaskList, AskUserQuestion | unknown | procedure |
| F3-283 | `metadata.activity` on a gate task carries the gate's finite choices verbatim where applicable. | field-or-template | L592 `##### TaskList naming convention` | `metadata.activity` | gate options | - | TaskList | unknown | procedure |
| F3-284 | Mark the gate task `completed` the moment the prescribed tool call returns and its result is consumed (answer routed, branch entered); normally within a single turn. | command | L592 `##### TaskList naming convention` | task `completed` | tool result | - | TaskList | unknown | procedure |
| F3-285 | **Yield-control discipline**: this skill MUST NOT yield control while any `gate-*` task is `pending` or `in_progress` (mirrors `defer-*`). | invariant | L592 `##### TaskList naming convention` | - | TaskList | `defer-*` | TaskList | unknown | procedure |
| F3-286 | If a `gate-*` task is left active when the orchestrator would yield, the next tick walks the TaskList, surfaces it, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. | recovery | L592 `##### TaskList naming convention` | re-fired gate | `metadata.activity` | - | TaskList, AskUserQuestion | unknown | procedure |
| F3-287 | The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<issue-id>`, `analyst-<issue-id>`, `pm-<issue-id>`, the three reviewer names, `file-from-url-<n>`, aborted markers, and Section 8 post-completion names, with or without `-r<n>`. | definition | L592 `##### TaskList naming convention` | - | - | Section 8 | TaskList | unknown | procedure |
| F3-288 | The Section 5 PM dispatch prompt must include the **resolved path** to the Scoped-marker helper as a `<scoped-marker-resolver-path>` substitution. | field-or-template | L596 `#### Scoped-marker PM dispatch wiring` | PM prompt | resolved path | Section 5 | Agent | unknown | procedure |
| F3-289 | Resolve the helper at runtime from this skill's base directory: `<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py` (POSIX) / `<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py` (PowerShell). | command | L598-L612 `#### Scoped-marker PM dispatch wiring` | resolved path | skill base directory | `quo-breakdown-epic` | none | yes | procedure |
| F3-290 | The base directory is shown in the skill invocation header (`Base directory for this skill: /Users/.../quo-fix-issue`); use the `..` traversal to reach the sibling skill. | definition | L602 `#### Scoped-marker PM dispatch wiring` | - | skill invocation header | - | none | yes | procedure |
| F3-291 | The PM prompt's context selects **Path B** of `agents/pm.md`'s Scoped-marker logic: it names an **Issue ID** and the Issue's **`up_dependencies`** array, with **no Grandparent Bee**. | definition | L614 `#### Scoped-marker PM dispatch wiring` | PM prompt | Issue ID, `up_dependencies` | `agents/pm.md` | Agent | no | procedure |
| F3-292 | Path B iterates `up_dependencies` for a Plan Bee with a Scoped marker, falling back best-effort to the unscoped spec; Path A (Grandparent Bee, hard-fail) is the `quo-execute` path and does not apply. | definition | L614 `#### Scoped-marker PM dispatch wiring` | - | - | `agents/pm.md`, `quo-execute` | none | no | procedure |
| F3-293 | The orchestrator's responsibility ends at passing the resolved path placeholder, the Issue ID, the Issue body verbatim, and the Issue's `up_dependencies` to the PM. | invariant | L616 `#### Scoped-marker PM dispatch wiring` | PM prompt | Issue body, `up_dependencies` | - | Agent | no | procedure |
| F3-294 | Do **not** inline the Scoped-marker grammar, the temp-file recipe, or the helper invocation; `agents/pm.md` owns those and the Path A vs Path B selection. | invariant | L616 `#### Scoped-marker PM dispatch wiring` | - | - | `agents/pm.md` | none | unknown | procedure |

## Anchors defined here

Headings:

- L368 `### 4. Execute fix via per-issue Agent dispatch`
- L372 `#### Reconciliation loop`
- L462 `##### Anti-pattern: no clock primitives`
- L473 `#### Per-issue cold dispatch`
- L497 `##### Per-issue cold dispatch (vs SDD's warm-Agent intent)`
- L501 `##### Dispatch prompt: quote the issue body verbatim and embed the design directive`
- L547 `#### Hub-and-spoke via substrate`
- L551 `#### Recursive delegation: not supported`
- L557 `#### Roles dispatched by the orchestrator`
- L567 `#### TaskList as progress UI`
- L579 `##### TaskList naming convention`
- L594 `#### Scoped-marker PM dispatch wiring`

Bolded phrases:

- L370 **reconciliation loop**
- L370 **fresh, ephemeral background `Agent` invocations**
- L370 **per-issue**
- L374 **event-driven, not clock-driven**
- L376 **Read state.**
- L377 **bees**
- L384 **TaskList**
- L385 **git state**
- L386 **the run-state manifest**
- L386 **Validate it before trusting any field:**
- L386 **Unit scope**
- L388 **Conversation memory is never a substitute for these four sources.**
- L388 **if a summarization marker is visible in the conversation**
- L388 **Design Proposal**
- L388 **functional, not positional**
- L388 **whenever the proposal is needed for this Issue**
- L388 **or Section 3's own gate for this Issue is open on a proposal no reader can see**
- L388 **and it is no longer readable**
- L388 **Re-derive it through the Analyst. That is the only recovery *for the proposal itself***
- L390 **Check first for an active `analyst-<issue-id>` task for this Issue**
- L390 **prefix**
- L390 **genuinely in flight**
- L390 **wait for it**
- L390 **Except when the active task is `pending` with no Agent behind it.**
- L390 **no dispatch has landed**
- L390 **with a dispatch already landed**
- L390 **re-derivation shape**
- L390 **Post-compaction, whether the dispatch landed is itself unreadable**
- L390 **Otherwise, when a `gate-askuserquestion-*` task for this Issue's Section 3 gate is active**
- L390 **For this one gate that re-derivation takes precedence over the generic gate re-fire**
- L390 **Otherwise**
- L392 **Issue body re-read from bees**
- L393 **changed-file list of what is on disk for this Issue**
- L393 **Fallback when an Engineer return did not list files**
- L393 **empty**
- L394 **the prior proposal was lost to a compaction**
- L394 **re-derives**
- L394 **first**
- L394 **no proposal has been produced yet**
- L396 **branching only on TaskList-derivable state**
- L396 **Post-compaction recovery inside Phase A**
- L396 **Phase A has not begun**
- L396 **or the only one that does is `pending` with no dispatch landed for it**
- L396 **Phase A's entry**
- L396 **Phase B**
- L396 **The "only one that does" qualifier is deliberate:**
- L396 **Phase B has not begun**
- L396 **Code Reviewer**
- L396 **next dispatch**
- L396 **One case the Phase-B-has-not-begun arm cannot tell apart by task-name set alone:**
- L400 **Reconcile.**
- L400 **ordered into three phases**
- L402 **Phase A — source to clean.**
- L402 **Engineer alone**
- L402 **Code Reviewer alone**
- L402 **unless that return carries a `## Design question`**
- L402 **and settled by that gate's answer**
- L402 **Severity bounds the loop**
- L402 **one**
- L402 **further way out of the Engineer step**
- L402 **suspends**
- L404 **The Phase A exit test reads the numbered work-item list only.**
- L404 **every**
- L404 **A non-empty `### Second-order effects` narrative alongside a clean numbered list does NOT block Phase A closure.**
- L405 **Phase B — writers once, in parallel.**
- L405 **Test Writer**
- L405 **Doc Writer**
- L405 **only**
- L406 **Phase C — remaining reviewers plus PM.**
- L406 **and no `aborted-*` TaskList task for this Issue is `pending`**
- L406 **Test Reviewer**
- L406 **Doc Reviewer**
- L406 **PM**
- L407 **Engineer-dispatch precondition (checkable, not a promise).**
- L407 **MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with …**
- L407 **precondition to check, not a state to remember**
- L409 **Why the two Phase C reviewers and the PM are covered, not just the writers.**
- L409 **reviewer or PM**
- L409 **all**
- L411 **Why the Analyst is covered too.**
- L413 **The Code Reviewer is the one deliberate exception, and is NOT in the prefix list.**
- L415 **When the blocking task is `pending` with no Agent behind it.**
- L415 **with a dispatch already landed**
- L415 **no dispatch has landed for it**
- L415 **Post-compaction, whether a dispatch landed is unreadable**
- L415 **not**
- L417 **A writer that aborted on source movement does not block an Engineer round, and needs no exemption.**
- L417 **movement-report rung**
- L417 **distinct name class**
- L417 **Phase C**
- L418 **Re-entry from Phase C.**
- L418 **source**
- L418 **only**
- L419 **Post-compaction recovery inside Phase A.**
- L419 **no durable carrier**
- L419 **re-derivable at any moment by asking the Code Reviewer again**
- L419 **re-dispatch the Code Reviewer**
- L420 **Movement report from a Phase B writer.**
- L420 **stop mid-run and report**
- L422 **Recognising it.**
- L422 **fix mode is the strict branch**
- L422 **The two writers detect different things, and the receiver should not overstate either.**
- L422 **the material it is documenting appears to have moved — a file it read earlier no longer matches the prose it wrote against it**
- L422 **stopped**
- L424 **What to do.**
- L424 **NOT**
- L426 **Mark the writer's own TaskList task `completed`**
- L427 **Create a new `aborted-<role>-<issue-id>` TaskList task**
- L427 **is**
- L427 **name prefix and status**
- L428 **Phase C MUST NOT begin while any `aborted-*` task for this Issue is `pending`.**
- L432 **When the mover was an Engineer**
- L432 **in fix mode this should not occur**
- L432 **precondition breach**
- L432 **re-close first**
- L433 **When the mover was the sibling Phase B Test Writer's discrimination experiment**
- L433 **attributable**
- L433 **in place**
- L433 **only when tests need modification**
- L433 **every**
- L433 **re-dispatch the aborted lane once that sibling has returned, with no gate**
- L433 **some**
- L433 **When a Test Writer was dispatched in Phase B and has not returned yet, do not classify and do not fire the gate**
- L433 **never applies at all when Phase B dispatched no Test Writer**
- L434 **When the mover was an external actor**
- L434 **unexplained**
- L434 **unexplained-movement gate**
- L436 **When the re-dispatched lane returns a normal deliverable, mark the `aborted-*` task `completed`**
- L436 **existing**
- L438 **Unexplained-movement gate.**
- L438 **no**
- L438 **no returned Phase B Test Writer's `## Perturbations` list covers the moved paths**
- L438 **including the case where Phase B dispatched no Test Writer at all**
- L438 **no dispatched Test Writer is still in flight**
- L438 **first**
- L438 **then**
- L440 **verbatim**
- L442 **Re-dispatch the writer now**
- L443 **Wait**
- L443 **only on the operator's reply**
- L443 **concurrently**
- L443 **A sibling lane's completion notification is a tick that processes that lane normally**
- L443 **MUST NOT**
- L444 **Abort this Issue**
- L444 **`#### Aborted-Issue close-out`**
- L444 **Issue-boundary state-externalization checkpoint**
- L444 **stops the run**
- L446 **Wait**
- L446 **fresh**
- L448 **A Phase B writer return that reports detected source movement is not a completion**
- L450 **An Engineer return carrying a `## Design question` is not a Phase A completion either.**
- L450 **missed a mechanism**
- L450 **Section 3 Revise, by reference**
- L452 **Re-dispatch the Analyst exactly as Section 3's Revise branch prescribes**
- L452 **"in full" includes its `### Deferred refinements` block**
- L452 **in place of the user's revision feedback**
- L452 **partial implementation of the prior directive is already on disk**
- L452 **mid-change**
- L454 **When the approved Design Proposal is no longer readable**
- L454 **re-derivation shape**
- L455 **When the Analyst returns, run Section 3's surface-and-gate flow unchanged.**
- L455 **Approve**
- L455 **Revise**
- L455 **Cancel**
- L455 **`#### Aborted-Issue close-out`**
- L456 **The durable carrier is the Analyst task.**
- L456 **once that re-dispatch lands**
- L460 **Yield.**
- L460 **Agent completion notification**
- L464 **not**
- L466 **`/loop`**
- L467 **`ScheduleWakeup`**
- L468 **`CronCreate`**
- L469 **Polling**
- L485 **not** (×2)
- L487 **when**
- L489 **Engineer**
- L489 **Phase A**
- L489 **Engineer-dispatch precondition**
- L490 **Test Writer**
- L490 **Phase B**
- L491 **Doc Writer**
- L491 **Phase B**
- L493 **Phase C**
- L495 **Code Reviewer**
- L495 **Phase A**
- L495 **Test Reviewer**
- L495 **Doc Reviewer**
- L495 **PM**
- L495 **Phase C**
- L503 **verbatim**
- L511 **Engineer dispatch — embed the Section 3 design directive as the authoritative design source.**
- L511 **Relay the `### Blast radius` section under the heading `## Blast radius`**
- L511 **enumerated site list**
- L511 **every**
- L511 **State in the prompt that the directive is the enumeration**
- L511 **the directive wins**
- L511 **Authoritative design directive (fix mode only)**
- L513 **Code Reviewer dispatch — relay the Engineer's completeness evidence verbatim.**
- L513 **completeness check with evidence**
- L513 **when an Engineer's return for this Issue carried a completeness list, the Phase A Code Reviewer dispatch prompt MUST embed that list verbatim**
- L513 **not**
- L513 **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was**
- L513 **Unlike the `### Blast radius` relay below, this MUST is not satisfiable on every path:**
- L513 **State the cost plainly rather than dressing it up:**
- L513 **compaction artifact, not an Engineer defect**
- L513 **Section 5's ignored-feedback rule**
- L513 **Ignored Review Feedback**
- L515 **Code Reviewer dispatch — relay the Analyst's `### Blast radius` verbatim.**
- L515 **verbatim**
- L515 **Relay it even when the Analyst's section carried only its fixed empty line**
- L517 **Test Writer / Doc Writer dispatch — state the orchestrator-side rule, never a freeze guarantee.**
- L517 **"no Engineer Agent will be dispatched for this Issue while you are running"**
- L517 **MUST NOT**
- L517 **"the source tree is frozen"**
- L519 **Test Writer dispatch — supply the fingerprint path list.**
- L519 **not by re-deriving it from the tree, but by carrying forward the changed-file list the Engineer's own return supplied.**
- L519 **union the lists across every Phase A round**
- L519 **An explicitly-empty `## Files changed` list is a list, not a missing one:**
- L519 **omit the `## Source paths to fingerprint` heading**
- L521 **Fallback when an Engineer return did not list files.**
- L533 **whole working tree**
- L535 **every**
- L549 **structural property**
- L553 **flat orchestration**
- L555 **monotonically within a session**
- L555 **nothing in this skill reclaims those tokens.**
- L555 **survivable**
- L555 **Issue-boundary state-externalization checkpoint**
- L555 **fresh session**
- L561 **Engineer**
- L562 **Test Writer**
- L563 **Doc Writer**
- L569 **TaskList**
- L571 **one**
- L573 **`pending`**
- L574 **`in_progress`**
- L575 **`completed`**
- L575 **One exception:**
- L575 **without**
- L581 **canonical cross-reference**
- L583 **issue-scoped**
- L585 **Analyst Agents**
- L586 **Implementer Agents**
- L586 **Round discriminator for repeat dispatches.**
- L586 **re**
- L586 **suffix**
- L586 **prefix**
- L587 **Reviewer Agents**
- L587 **Code Reviewer**
- L587 **Phase A**
- L587 **Test Reviewer**
- L587 **Doc Reviewer**
- L587 **Phase C**
- L588 **PM Agents**
- L589 **Aborted-writer redelivery markers**
- L589 **Issue scope**
- L589 **post-completion scope**
- L589 **the same finding index as the lane it marks**
- L589 **movement-report rung**
- L589 **This is not an Agent task**
- L589 **obligation marker**
- L589 **Phase C must not begin**
- L590 **URL-resolution Skill-tool dispatches**
- L591 **Deferral-ledger tasks**
- L591 **Run scope**
- L592 **Gate-task tasks**
- L592 **Turn scope**
- L592 **unexplained-movement gate**
- L592 **yield-control discipline**
- L596 **resolved path**
- L614 **Path B**
- L614 **Issue ID**
- L614 **`up_dependencies`**
- L614 **no Grandparent Bee**

## Rationale-only spans

- L409-L409 — why reviewers/PM block Engineer (1 line)
- L411-L411 — why Analyst prefix blocks Engineer (1 line; second sentence is factual but restates Section 3)
- L497-L499 — SDD warm-Agent intent trade-off (3 lines)
- L543-L543 — why softening clauses cannot be made safe (1 line; contains one restated invariant)
- L549-L549 — hub-and-spoke is structural, not enforced (1 line; contains one restated invariant)
- L555-L555 — monotonic context growth, harness owns compaction (1 line; last sentence points at Section 7 step 5)

Total rationale-only lines: 8.
