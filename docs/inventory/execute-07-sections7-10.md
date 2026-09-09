# Rule inventory — `skills/quo-execute/SKILL.md` L1238–L1322 (Sections 7–10)

Source slice: `### 7. Final Output` through `### 10. Further testing and merging`. Every row is one extracted rule, named artifact, or rationale span. IDs are prefixed `E7`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| E7-001 | When **all** Epics in the Bee are done, show the User the full list of all Reviewer feedback the orchestrator chose to ignore. | relay | L1240 · `### 7. Final Output` | ignored-feedback display (user-facing list) | the run's record of ignored Reviewer feedback | - | none | unknown | procedure |
| E7-002 | Use `AskUserQuestion` to ask the User whether to act on any ignored feedback or just continue. | gate | L1241 · `### 7. Final Output` | ignored-feedback action gate | E7-001 list | - | AskUserQuestion | unknown | procedure |
| E7-003 | Surface the session-scoped compromise tracker's accepted-compromise entries only in Section 9's `## Bee Execution Complete:` block via its "Accepted compromises" logic, never in the ignored-feedback display. | ordering | L1243 · `### 7. Final Output` | - | compromise tracker entries | Section 9; `## Bee Execution Complete:`; "Accepted compromises" logic | none | no | procedure |
| E7-004 | Every `AskUserQuestion` invocation in Section 7 MUST go through the two-step `TaskCreate` → `AskUserQuestion` contract. | invariant | L1245 · `### 7. Final Output` | - | - | two-step `TaskCreate` → `AskUserQuestion` contract | TaskList, AskUserQuestion | yes | procedure |
| E7-005 | Section 7 has exactly three gates: the ignored-feedback action gate, the per-Acceptance-Criteria sign-off gate, and the final Bee-done gate. | definition | L1245 · `### 7. Final Output` | - | - | - | AskUserQuestion | no | procedure |
| E7-006 | For each gate, **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, per Section 3's TaskList naming convention's gate-task entry. | name-class | L1245 · `### 7. Final Output` | TaskList task `gate-askuserquestion-<short-suffix>` | Section 3 TaskList naming convention | Section 3's TaskList naming convention (gate-task entry) | TaskList | yes | procedure |
| E7-007 | Use a distinct suffix per distinct gate. | name-class | L1245 · `### 7. Final Output` | - | E7-006 | - | TaskList | yes | procedure |
| E7-008 | **Then** call `AskUserQuestion` in the same turn as the gate-task creation. | ordering | L1245 · `### 7. Final Output` | AskUserQuestion call | E7-006 task | - | TaskList, AskUserQuestion | yes | procedure |
| E7-009 | Mark each `gate-*` task `completed` the moment the user's answer is consumed. | ordering | L1245 · `### 7. Final Output` | TaskList status flip to `completed` | user's gate answer | - | TaskList | yes | procedure |
| E7-010 | For each Acceptance Criteria, either demonstrate it directly (via test or script) or instruct the user how to validate it manually. | relay | L1247 · `### 7. Final Output` | demonstration or manual-validation instructions | Bee's Acceptance Criteria | - | Bash | no | procedure |
| E7-011 | Then use `AskUserQuestion` to get official sign-off on the Acceptance Criteria. | gate | L1247 · `### 7. Final Output` | per-Acceptance-Criteria sign-off gate | E7-010 output | - | AskUserQuestion | no | procedure |
| E7-012 | The final Bee-done gate's Question text is `"Are you ready to mark this Bee as done?"`. | field-or-template | L1249-L1250 · `### 7. Final Output` | final Bee-done gate | - | - | AskUserQuestion | no | procedure |
| E7-013 | The final Bee-done gate's Options are exactly `"Yes, mark as done"` and `"No, we have more work to do"`. | choice-set | L1251-L1253 · `### 7. Final Output` | - | - | - | AskUserQuestion | no | procedure |
| E7-014 | Enter Section 8 only once the user approves the Bee as done. | precondition | L1257 · `### 8. Mark Bee Complete` | - | E7-012/E7-013 answer `"Yes, mark as done"` | - | none | no | procedure |
| E7-015 | In a healthy flow every Epic was already transitioned to `status=done` at the end of its iteration in Step 4.2, so nothing should require a status change here. | rationale-only | L1259 · `### 8. Mark Bee Complete` · **Precondition check (defense-in-depth).** | - | Epic `status` | Step 4.2 | none | no | rationale |
| E7-016 | Do not bulk-flip Epic statuses in Section 8 — that would silently mark `drafted` work as `done`. | invariant | L1259 · `### 8. Mark Bee Complete` · **Precondition check (defense-in-depth).** | - | - | - | bees | no | procedure |
| E7-017 | Re-query and verify Epic statuses with `bees execute-freeform-query --query-yaml 'stages: - [parent=<bee-id>, type=t1] report: [title, ticket_status]'`. | command | L1259-L1265 · `### 8. Mark Bee Complete` · **Precondition check (defense-in-depth).** | query result (`title`, `ticket_status` per Epic) | `<bee-id>` | - | Bash, bees | no | procedure |
| E7-018 | If any Epic returns `ticket_status` other than `done`, abort with: `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.` | recovery | L1267-L1269 · `### 8. Mark Bee Complete` | abort message (template) | E7-017 result | `/quo-breakdown-epic`; `/quo-execute` | none | no | procedure |
| E7-019 | Do not silently update non-`done` Epics. | invariant | L1271 · `### 8. Mark Bee Complete` | - | E7-017 result | - | bees | no | procedure |
| E7-020 | Reaching the abort branch indicates an upstream bug — the Step 4.2 classifier should have stopped the run before Step 7 asked the user to close the Bee. | rationale-only | L1271 · `### 8. Mark Bee Complete` | - | - | Step 4.2 classifier; Step 7 | none | no | rationale |
| E7-021 | With all Epics confirmed `done`, mark the Bee with `bees update-ticket --ids <bee-id> --status done`. | command | L1273-L1276 · `### 8. Mark Bee Complete` | Bee status flip to `done` | E7-017 all-`done` result; `<bee-id>` | - | Bash, bees | no | procedure |
| E7-022 | Output the final summary as a markdown block headed `## Bee Execution Complete: [bee-title]`. | field-or-template | L1280-L1281 · `### 9. Output Final Summary` | summary block heading | Bee title | - | none | no | procedure |
| E7-023 | Render the field `**Bee ID**: <bee-id>`. | field-or-template | L1283 · `### 9. Output Final Summary` | summary field | `<bee-id>` | - | none | no | procedure |
| E7-024 | Render the field `**Epics Completed**: [count]`. | field-or-template | L1284 · `### 9. Output Final Summary` | summary field | count of completed Epics | - | none | no | procedure |
| E7-025 | Render the field `**Tasks Completed**: [count]`. | field-or-template | L1285 · `### 9. Output Final Summary` | summary field | count of completed Tasks | - | none | no | procedure |
| E7-026 | Render the fixed field `**Bee Status**: Finished`. | field-or-template | L1286 · `### 9. Output Final Summary` | summary field | - | - | none | no | procedure |
| E7-027 | Render `**Reviews**` as `Bee-level code review: X issues found/None needed \| Test review: Y issues found/None needed \| Docs review: Z issues found/None needed`. | field-or-template | L1287 · `### 9. Output Final Summary` | summary field | Bee-level review results (code, test, docs) | - | none | unknown | procedure |
| E7-028 | Append to `**Reviews**` `N nits applied without re-review` (or `"count unavailable post-compaction"`) only when any nits were applied. | field-or-template | L1287 · `### 9. Output Final Summary` | summary field suffix | nit count from review rounds (or post-compaction state) | - | none | unknown | procedure |
| E7-029 | Render `**Second-order effects**` as the relayed `### Second-order effects` narrative from the Bee-level review, per the "Second-order effects" logic below. | field-or-template | L1288 · `### 9. Output Final Summary` | summary field | relayed `### Second-order effects` narrative | "Second-order effects" logic (L1294-L1299) | none | yes | procedure |
| E7-030 | Render `**Accepted compromises**` per the "Accepted compromises" logic below, or OMIT IT ENTIRELY when the tracker is empty or absent. | field-or-template | L1289 · `### 9. Output Final Summary` | summary field (conditional) | compromise tracker file | "Accepted compromises" logic (L1301-L1314) | none | yes | procedure |
| E7-031 | Render the closing line `All per-Task work has been committed.` | field-or-template | L1291 · `### 9. Output Final Summary` | summary closing line | - | - | none | unknown | procedure |
| E7-032 | Run `git status --porcelain`; when it lists anything, add: `Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing.` | command | L1291 · `### 9. Output Final Summary` | uncommitted-paths sentence | `git status --porcelain` output | - | Bash, git | unknown | procedure |
| E7-033 | Omit the uncommitted-paths sentence when the tree is clean. | invariant | L1291 · `### 9. Output Final Summary` | - | `git status --porcelain` output | - | git | unknown | procedure |
| E7-034 | The `**Second-order effects**` field is the **destination** for the narrative relayed out of the **Bee-level** review in Section 5. | definition | L1294 · **Second-order effects (rendered into the summary block above).** | - | Section 5 Bee-level review output | Section 5 | none | yes | procedure |
| E7-035 | The Bee-level Code Reviewer relays `/quo-engineer-review`'s `### Second-order effects` subsection verbatim on every return (`agents/code-reviewer.md`). | relay | L1294 · **Second-order effects (rendered into the summary block above).** | - | Code Reviewer return | `/quo-engineer-review`; `### Second-order effects`; `agents/code-reviewer.md` | Agent | yes | procedure |
| E7-036 | A Bee-scoped PM re-dispatched by Section 5 relays the `### Second-order effects` narrative into its Final report (`agents/pm.md`). | relay | L1294 · **Second-order effects (rendered into the summary block above).** | - | Bee-scoped PM Final report | Section 5; `agents/pm.md` | Agent | yes | procedure |
| E7-037 | Never route the Bee-level narrative to Section 4.1's **per-Task** field — that field's summaries are already emitted and closed by the time Section 9 runs. | invariant | L1294 · **Second-order effects (rendered into the summary block above).** | - | - | Section 4.1 | none | no | procedure |
| E7-038 | Render the Bee-level narrative with the same four steps Section 4.1 uses, at Bee scope. | ordering | L1294 · **Second-order effects (rendered into the summary block above).** | - | - | Section 4.1 | none | no | procedure |
| E7-039 | Step 1: **Collect every relayed narrative from the Bee-level review** — each Bee-level Code Reviewer return (one per round, including `-r<n>` rounds) and any Bee-scoped PM Final report `### Second-order effects` section, including each `#### <invocation scope>` sub-block. | ordering | L1296 · **Second-order effects (rendered into the summary block above).** | collected narrative set | Code Reviewer returns (all rounds); PM Final report `### Second-order effects`; `#### <invocation scope>` sub-blocks | `-r<n>` rounds | none | yes | procedure |
| E7-040 | Render collected bullets **verbatim**; do not re-summarize or re-rank them. | invariant | L1296 · **Second-order effects (rendered into the summary block above).** | rendered bullets | E7-039 set | - | none | yes | procedure |
| E7-041 | Step 2: **Keep the sub-block labels** the relaying source supplied so a reader can tell which round or invocation surfaced which effect. | invariant | L1297 · **Second-order effects (rendered into the summary block above).** | labeled sub-blocks | E7-039 set | - | none | yes | procedure |
| E7-042 | Step 3: **De-duplicate exact repeats** across sources — one effect relayed twice is one effect; keep the earliest attribution. | invariant | L1298 · **Second-order effects (rendered into the summary block above).** | de-duplicated list | E7-039 set | - | none | yes | procedure |
| E7-043 | Keep near-duplicates that differ in substance as separate entries. | invariant | L1298 · **Second-order effects (rendered into the summary block above).** | - | E7-042 | - | none | yes | procedure |
| E7-044 | Step 4: **When every source reported the fixed empty line** `No second-order effects identified.`, or no Bee-level review that emits the subsection ran, render the single line `None identified.` | field-or-template | L1299 · **Second-order effects (rendered into the summary block above).** | `None identified.` line | E7-039 set; whether any emitting Bee-level review ran | - | none | yes | procedure |
| E7-045 | Do **not** omit the `**Second-order effects**` field — unlike `**Accepted compromises**`, it is unconditional. | invariant | L1299 · **Second-order effects (rendered into the summary block above).** | - | - | `**Accepted compromises**` | none | yes | procedure |
| E7-046 | A section that appears only when there was something to say degrades into one nobody can rely on being asked for. | rationale-only | L1299 · **Second-order effects (rendered into the summary block above).** | - | - | - | none | yes | rationale |
| E7-047 | The session-scoped compromise tracker (Section 6.5 `#### Session-scoped compromise tracker`) accumulates one entry per accepted compromise across the whole run; the summary reflects the file's contents at render time. | definition | L1301 · **Accepted compromises (rendered into the summary block above).** | - | compromise tracker file | Section 6.5 `#### Session-scoped compromise tracker` | none | yes | procedure |
| E7-048 | Step 1: **Read the run's tracker file via the `Read` tool** at `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`/tmp/.quorum/...` POSIX, `%TEMP%\.quorum\...` Windows), generated once at run start per Section 6.5's path convention. | command | L1303 · **Accepted compromises (rendered into the summary block above).** | tracker contents in context | tracker path from run start | Section 6.5 path convention | none | yes | procedure |
| E7-049 | If the tracker path is no longer in view, recover it from the run-state manifest's **Compromise tracker** field (Section 1 `#### Write the run-state manifest`). | recovery | L1303 · **Accepted compromises (rendered into the summary block above).** | recovered tracker path | run-state manifest **Compromise tracker** field | Section 1 `#### Write the run-state manifest` | none | yes | procedure |
| E7-050 | Use no shell to locate or test the tracker file — just `Read` it. | invariant | L1303 · **Accepted compromises (rendered into the summary block above).** | - | - | - | none | yes | procedure |
| E7-051 | Step 2: **Omit the section entirely when there is nothing to show** — if `Read` reports the file does not exist OR the file contains no `## Compromise <n>` entries, do NOT render the `**Accepted compromises**` line. | invariant | L1304 · **Accepted compromises (rendered into the summary block above).** | - | E7-048 `Read` result | - | none | yes | procedure |
| E7-052 | When omitting, emit no empty heading, no `N/A`, and no "no compromises" placeholder. | invariant | L1304 · **Accepted compromises (rendered into the summary block above).** | - | E7-051 | - | none | yes | procedure |
| E7-053 | Treat "file absent" and "file present but empty" identically: omit. | invariant | L1304 · **Accepted compromises (rendered into the summary block above).** | - | E7-048 `Read` result | - | none | yes | procedure |
| E7-054 | File absence is uncommon because an ungated path pick appends an entry whenever the pick was among two or more paths; Trigger C's lone-`trivial-tweak` carve-out is the only ungated route that appends nothing. | rationale-only | L1304 · **Accepted compromises (rendered into the summary block above).** | - | - | Trigger C; `trivial-tweak` carve-out | none | yes | rationale |
| E7-055 | Step 3: **When entries exist, render one bullet per `## Compromise <n>` entry**, surfacing exactly four user-facing fields. | field-or-template | L1305 · **Accepted compromises (rendered into the summary block above).** | one bullet per entry | `## Compromise <n>` entries | - | none | yes | procedure |
| E7-056 | Surface the **finding** — the entry's `Finding (verbatim)` field. | field-or-template | L1306 · **Accepted compromises (rendered into the summary block above).** | bullet sub-field | entry `Finding (verbatim)` | - | none | yes | procedure |
| E7-057 | Surface the **chosen path** — the entry's `Decision` field. | field-or-template | L1307 · **Accepted compromises (rendered into the summary block above).** | bullet sub-field | entry `Decision` | - | none | yes | procedure |
| E7-058 | Surface the **rationale** — the entry's `Rationale` field. | field-or-template | L1308 · **Accepted compromises (rendered into the summary block above).** | bullet sub-field | entry `Rationale` | - | none | yes | procedure |
| E7-059 | Surface the **follow-up Issue ID** — the entry's `Follow-up Issue` field (a ticket ID, or `none`). | field-or-template | L1309 · **Accepted compromises (rendered into the summary block above).** | bullet sub-field | entry `Follow-up Issue` | - | none | yes | procedure |
| E7-060 | Do NOT surface the fifth entry field `Fix paths surfaced by reviewer`. | invariant | L1311 · **Accepted compromises (rendered into the summary block above).** | - | entry `Fix paths surfaced by reviewer` | - | none | yes | procedure |
| E7-061 | The surface shows the path that was chosen, not the full menu of paths the reviewer offered. | rationale-only | L1311 · **Accepted compromises (rendered into the summary block above).** | - | - | - | none | yes | rationale |
| E7-062 | Step 4: **Volume (>10 entries).** When the tracker has more than ~10 entries, surface them ALL in full — do NOT truncate, summarize away, or elide any entry. | invariant | L1312 · **Accepted compromises (rendered into the summary block above).** | full bullet list | entry count | - | none | yes | procedure |
| E7-063 | When volume exceeds ~10, precede the bullets with a short prologue noting the volume (e.g., `N compromises were accepted during this run:`). | field-or-template | L1312 · **Accepted compromises (rendered into the summary block above).** | volume prologue line | entry count | - | none | yes | procedure |
| E7-064 | The Accepted-compromises surface only **reads** the tracker — never write, append to, or delete it. | invariant | L1314 · **Accepted compromises (rendered into the summary block above).** | - | tracker file | - | none | yes | procedure |
| E7-065 | The tracker's write side is owned by Section 6.5's append triggers. | definition | L1314 · **Accepted compromises (rendered into the summary block above).** | - | - | Section 6.5 append triggers | none | yes | procedure |
| E7-066 | Instruct the user to perform whatever further testing they want to do. | relay | L1318 · `### 10. Further testing and merging` | user instruction | - | - | none | no | procedure |
| E7-067 | After the user commits whatever of the summary's `git status --porcelain` list belongs to this Bee (the list may include pre-run changes), advise on merging based on the isolation strategy chosen in step 1. | ordering | L1318 · `### 10. Further testing and merging` | merging advice | E7-032 list; isolation strategy from step 1 | step 1 | git | no | procedure |
| E7-068 | Every merging strategy below assumes a clean tree. | precondition | L1318 · `### 10. Further testing and merging` | - | working-tree state | - | git | no | procedure |
| E7-069 | **Worktree**: if `/bees-worktree-rm` is installed (not part of the portable core), invoke it to merge the worktree branch and clean up the worktree directory. | command | L1320 · `### 10. Further testing and merging` | merged branch; removed worktree | `/bees-worktree-rm` availability | `/bees-worktree-rm` | git | no | procedure |
| E7-070 | **Worktree** otherwise: instruct the user to merge manually — `git merge <branch>` from the parent repo, then `git worktree remove <path>`. | relay | L1320 · `### 10. Further testing and merging` | user instruction | worktree branch and path | - | git | no | procedure |
| E7-071 | **Feature branch**: instruct the user to merge the branch (e.g., `git merge bee/b.Wx7`) or open a PR. | relay | L1321 · `### 10. Further testing and merging` | user instruction | feature branch name | - | git | no | procedure |
| E7-072 | Do NOT push to remote unless the user asks. | invariant | L1321 · `### 10. Further testing and merging` | - | - | - | git | no | procedure |
| E7-073 | **Worked on main/current branch**: per-Task commits are already on the branch; remind the user the work is committed locally and they can push when ready. | relay | L1322 · `### 10. Further testing and merging` | user reminder | per-Task commits | - | git | no | procedure |

## Anchors defined here

- L1238 `### 7. Final Output`
- L1240 **all**
- L1243 `## Bee Execution Complete:` (referenced as Section 9's summary block heading)
- L1245 **first**
- L1245 **then**
- L1245 `gate-askuserquestion-<short-suffix>` (TaskList name pattern)
- L1245 `gate-*` (TaskList name class)
- L1250 `"Are you ready to mark this Bee as done?"` (gate question)
- L1252 `"Yes, mark as done"` (choice label)
- L1253 `"No, we have more work to do"` (choice label)
- L1255 `### 8. Mark Bee Complete`
- L1259 **Precondition check (defense-in-depth).**
- L1269 `Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.` (abort message template)
- L1278 `### 9. Output Final Summary`
- L1281 `## Bee Execution Complete: [bee-title]` (summary block heading)
- L1283 **Bee ID**
- L1284 **Epics Completed**
- L1285 **Tasks Completed**
- L1286 **Bee Status**
- L1287 **Reviews**
- L1288 **Second-order effects** (summary field)
- L1289 **Accepted compromises** (summary field)
- L1291 `All per-Task work has been committed.` (closing line)
- L1291 `Uncommitted in the working tree: <the listed paths> — these may include changes that predate this run; commit the ones belonging to this Bee before pushing.` (conditional sentence template)
- L1294 **Second-order effects (rendered into the summary block above).**
- L1294 **destination**
- L1294 **Bee-level**
- L1294 **per-Task**
- L1296 **Collect every relayed narrative from the Bee-level review**
- L1296 **verbatim**
- L1297 **Keep the sub-block labels**
- L1298 **De-duplicate exact repeats**
- L1299 **When every source reported the fixed empty line**
- L1299 `No second-order effects identified.` (fixed empty line)
- L1299 `None identified.` (fixed rendered line)
- L1299 **not**
- L1301 **Accepted compromises (rendered into the summary block above).**
- L1303 **Read the run's tracker file via the `Read` tool**
- L1303 `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (tracker path pattern)
- L1303 **Compromise tracker** (run-state manifest field)
- L1304 **Omit the section entirely when there is nothing to show.**
- L1304 `## Compromise <n>` (tracker entry heading)
- L1305 **When entries exist, render one bullet per `## Compromise <n>` entry**
- L1306 **finding**
- L1307 **chosen path**
- L1308 **rationale**
- L1309 **follow-up Issue ID**
- L1306 `Finding (verbatim)` (tracker entry field)
- L1307 `Decision` (tracker entry field)
- L1308 `Rationale` (tracker entry field)
- L1309 `Follow-up Issue` (tracker entry field)
- L1311 `Fix paths surfaced by reviewer` (tracker entry field, not surfaced)
- L1312 **Volume (>10 entries).**
- L1312 `N compromises were accepted during this run:` (example prologue)
- L1314 **reads**
- L1316 `### 10. Further testing and merging`
- L1320 **Worktree**
- L1321 **Feature branch**
- L1322 **Worked on main/current branch**

## Rationale-only spans

No whole line in L1238–L1322 is purely rationale; every prose line carries at least one rule. The rationale content is confined to intra-line clauses, listed here so a rewrite can drop or relocate them without losing a rule:

- L1259 (second sentence only) — healthy flow already flipped Epics
- L1271 (parenthetical only) — abort branch means upstream bug
- L1294 (third sentence only) — per-Task field already printed, closed
- L1299 (final clause only) — conditional sections become unreliable
- L1304 (parenthetical only) — file absence uncommon; Trigger C
- L1311 (clause after dash) — shows chosen path, not menu

Total whole-line rationale-only span: 0 lines (6 intra-line clauses, each captured as a `rationale-only` row above: E7-015, E7-020, E7-046, E7-054, E7-061, plus the L1294 clause folded into E7-037).
