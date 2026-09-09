# Rule inventory — /quo-execute slice 04: `### Orchestrator discipline: routing review findings`

Source: `/Users/jesseg/code/quorum/skills/quo-execute/SKILL.md` L789–L893. Mirror column compared against `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md` L618–L702 (same-named section). Where the only difference is section numbering (execute: Section 3 dispatch shape / Section 6.5 triggers / Section 4.2 close-out; fix-issue: Section 4 / Section 7.5 / Section 7), Mirror reads `yes (section refs differ)`.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| E4-001 | The section `### Orchestrator discipline: routing review findings` governs how the orchestrator routes depth-tagged findings emitted by the in-flow review skills. | definition | L789-L791 — ### Orchestrator discipline: routing review findings | - | reviewer findings | in-flow review skills | none | yes | procedure |
| E4-002 | Every reviewer finding carries a severity tag that is exactly one of `blocker` / `suggestion` / `nit`. | definition | L791 — intro | - | reviewer finding | - | none | yes | procedure |
| E4-003 | Every proposed fix path carries a depth tag that is exactly one of `trivial-tweak` / `refactor-locally` / `re-architect`. | definition | L791 — intro | - | reviewer finding | - | none | yes | procedure |
| E4-004 | Every reviewer finding carries the count of fix paths it surfaced. | definition | L791 — intro | - | reviewer finding | - | none | yes | procedure |
| E4-005 | Turn the reviewer's enumerated fix paths and depth tags into exactly one routing decision per finding. | invariant | L791 — intro | routing decision | fix paths, depth tags | - | none | yes | procedure |
| E4-006 | Whether a gate fires is determined deterministically (by the Step 2 table), never by judgment. | invariant | L791 — intro | - | Step 2 table | part (a) | none | yes | procedure |
| E4-007 | Which path is picked when no gate fires is the orchestrator's own judgment (Step 1). | invariant | L791 — intro | path pick | enumerated paths | part (a) Step 1 | none | yes | procedure |
| E4-008 | Never re-classify the reviewer's depth tags; read the depth of a path exactly as emitted. | invariant | L791 — intro | - | depth tags | - | none | yes | procedure |
| E4-009 | A "review lane's loop" is the Engineer → code-review loop at any review site, and each writer → reviewer pair. | definition | L793 — Severity bounds the loop | - | - | - | none | yes | procedure |
| E4-010 | A lane is held open by `blocker`- and `suggestion`-severity findings and by any `nit` whose chosen fix path is deeper than `trivial-tweak`. | invariant | L793 — Severity bounds the loop | - | severity tag, chosen path depth | - | none | yes | procedure |
| E4-011 | A lane closes when no lane-holding finding remains outstanding. | invariant | L793 — Severity bounds the loop | lane closure | outstanding findings | - | none | yes | procedure |
| E4-012 | A lane-holding finding stays outstanding until a later cold pass no longer raises it or it reaches a no-fix-lands disposition. | invariant | L793 — Severity bounds the loop | - | cold-pass result | - | Agent | yes | procedure |
| E4-013 | No-fix-lands dispositions are: accepted into the compromise tracker, recorded as a `defer-*` task, or gate answer `Accept the limitation` / `Cancel` / `Defer to follow-up Issue` when nothing ships. | definition | L793 — Severity bounds the loop | - | tracker entry, `defer-*` task, gate answer | compromise tracker | TaskList, AskUserQuestion | yes | procedure |
| E4-014 | A dispatch settles nothing — ungated at row 6, chosen at a gate, or a deferral's soft fix / narrowing — until a later cold pass reads its result. | invariant | L793 — Severity bounds the loop | - | dispatch, cold pass | row 6 | Agent | yes | procedure |
| E4-015 | A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own. | invariant | L793 — Severity bounds the loop | - | severity + depth tag | - | none | yes | procedure |
| E4-016 | When a lane-holding finding already forces another implementer round, `trivial-tweak` nits ride along in it and the next cold pass reads them. | ordering | L793 — Severity bounds the loop | implementer dispatch | lane-holding finding | - | Agent | yes | procedure |
| E4-017 | When only `trivial-tweak` nits remain, apply them in one final implementer pass for that lane and dispatch no further reviewer round for it. | ordering | L793 — Severity bounds the loop | final implementer dispatch | remaining nits | - | Agent | yes | procedure |
| E4-018 | At a site where the review runs inside the PM's in-flight passes, "no further reviewer round" means do not re-dispatch the PM for that lane. | ordering | L793 — Severity bounds the loop | - | review site type | PM in-flight review | Agent | yes | procedure |
| E4-019 | Record the batched-nit count on the **Reviews** line of the summary for the scope that dispatched the review, as `N nits applied without re-review`. | field-or-template | L793 — Severity bounds the loop | **Reviews** summary line | nit count | summary | none | yes | procedure |
| E4-020 | When compaction has removed the nit count, render `count unavailable post-compaction` on the **Reviews** line rather than guessing. | recovery | L793 — Severity bounds the loop | **Reviews** summary line | conversation state | - | none | yes | procedure |
| E4-021 | Batched `trivial-tweak` nits are finished work: never list them as ignored feedback and never turn them into `defer-*` tasks. | invariant | L793 — Severity bounds the loop | - | - | `defer-*` tasks | TaskList | yes | procedure |
| E4-022 | A `nit` whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding. | invariant | L793 — Severity bounds the loop | - | Step 2 table | part (a) | none | yes | procedure |
| E4-023 | When a gate answer ships anything other than the enumerated `trivial-tweak` path (`Fix properly now` on row 2/3/4, or a Defer's soft fix/narrowing), the finding is lane-holding again. | invariant | L793 — Severity bounds the loop | - | gate answer | part (g) | AskUserQuestion | yes | procedure |
| E4-024 | For such a re-opened finding a cold pass must read the fix, and part (g)'s elision does not apply. | invariant | L793 — Severity bounds the loop | reviewer dispatch | E4-023 | part (g) | Agent | yes | procedure |
| E4-025 | When the final pass ships only `trivial-tweak` paths and changes source, apply part (g)'s ordering with its code-review rung elided. | ordering | L793 — Severity bounds the loop | Engineer → writer dispatch | E4-017 | part (g) | Agent | yes | procedure |
| E4-026 | The bound keys on the reviewer's own depth tag, not on a narrower reading of `nit`; severity stays orthogonal to depth. | invariant | L793 — Severity bounds the loop | - | depth tag | - | none | yes | procedure |
| E4-027 | The coverage given up is exactly the `trivial-tweak`-nit class: the raising pass already read the text, and the post-completion review reads the whole diff. | rationale-only | L793 — Severity bounds the loop | - | - | post-completion review | none | yes | rationale |
| E4-028 | Routing is a two-step procedure: Step 1 is the orchestrator's own judgment; Step 2 is deterministic given the path Step 1 chose. | ordering | L795 — (a) Pick the path, then route on it | - | - | - | none | yes | procedure |
| E4-029 | Step 1: choose the highest-quality fix path among those the reviewer enumerated. | command | L797 — Step 1 — pick | path pick | enumerated paths | "What highest-quality means" | none | yes | procedure |
| E4-030 | Treat the reviewer's `[preferred]` token as an input, not a verdict; prefer it only when it is also the most complete. | invariant | L797 — Step 1 — pick | - | `[preferred]` token | - | none | yes | procedure |
| E4-031 | When `[preferred]` marks a narrowing and a fuller path is still the smallest internally-consistent complete change, take the fuller path. | invariant | L797 — Step 1 — pick | path pick | `[preferred]` token | - | none | yes | procedure |
| E4-032 | The pick is always one of the paths the reviewer enumerated. | invariant | L797 — Step 1 — pick | - | enumerated paths | - | none | yes | procedure |
| E4-033 | When no enumerated path is the smallest internally-consistent complete change, pick the most complete of them anyway. | invariant | L797 — Step 1 — pick | path pick | enumerated paths | - | none | yes | procedure |
| E4-034 | An under-enumerated pick routes via rows 2, 3, 4 to gate (c), where `Fix properly now` dispatches the complete fix. | ordering | L797 — Step 1 — pick | gate (c) | E4-033 | gate (c), rows 2-4 | AskUserQuestion | yes | procedure |
| E4-035 | Exception: an under-enumerated finding with absent/malformed depth tag goes via row 1 to gate (d), which has no `Fix properly now`; the user picks among paths as emitted. | ordering | L797 — Step 1 — pick | gate (d) | depth tag | gate (d), row 1 | AskUserQuestion | yes | procedure |
| E4-036 | An incomplete menu becomes visible in session because a gate fires where it otherwise would not have. | rationale-only | L797 — Step 1 — pick | - | - | - | none | yes | rationale |
| E4-037 | A durable record of an under-enumerated finding reaches the post-completion review only via Trigger A (`Defer to follow-up Issue`) or Trigger B (`Accept the limitation`); `Fix properly now` writes none. | invariant | L797 — Step 1 — pick | tracker entry (conditional) | gate answer | Trigger A, Trigger B, post-completion review | none | yes | procedure |
| E4-038 | The orchestrator does not absorb an under-enumeration gap by writing a fix path of its own. | invariant | L797 — Step 1 — pick | - | - | - | none | yes | procedure |
| E4-039 | Step 2: evaluate the table conditions in order, taking the first that matches, so each finding yields exactly one routing decision. | ordering | L799 — Step 2 — route on the path chosen in Step 1 | routing decision | chosen path | - | none | yes | procedure |
| E4-040 | Row 1: the finding carries no depth tag, or a malformed severity/depth tag → treat as `re-architect` → gate (d). | ordering | L804 — Step 2 table | gate (d) | tags | gate (d) | AskUserQuestion | yes | procedure |
| E4-041 | Row 2: the chosen path carries the reviewer's `[introduces-mechanism]` tag, or introduces a mechanism by the orchestrator's own reading → Scope-bounding gate (c). | ordering | L805-L806 — Step 2 table | gate (c) | `[introduces-mechanism]` tag | gate (c), "What introduces a mechanism means" | AskUserQuestion | yes | procedure |
| E4-042 | Row 3: the chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers → Scope-bounding gate (c). | ordering | L807-L808 — Step 2 table | gate (c) | unit's ticket | gate (c) | AskUserQuestion | yes | procedure |
| E4-043 | Row 4: the chosen path is narrower than the smallest internally-consistent complete fix (leaves the stated defect partly unfixed) → Scope-bounding gate (c). | ordering | L809-L810 — Step 2 table | gate (c) | chosen path | gate (c) | AskUserQuestion | yes | procedure |
| E4-044 | Row 5: the chosen path's depth tag is `re-architect` → Routing-decision gate (d). | ordering | L811 — Step 2 table | gate (d) | depth tag | gate (d) | AskUserQuestion | yes | procedure |
| E4-045 | Row 6: otherwise → dispatch the chosen path, no gate. | ordering | L812 — Step 2 table | implementer dispatch | chosen path | - | Agent | yes | procedure |
| E4-046 | Row 6 dispatches a fresh ephemeral implementer Agent (Engineer / Test Writer / Doc Writer per the finding's lane) per Section 3's dispatch shape with the chosen fix path, no user gate. | command | L815 — after Step 2 table | implementer Agent dispatch | chosen path, finding's lane | Section 3 dispatch shape | Agent, TaskList | yes (section refs differ) | procedure |
| E4-047 | Row 6 appends a tracker entry per Section 6.5's **Trigger C**. | command | L815 — after Step 2 table | compromise-tracker entry | row-6 dispatch | Section 6.5 **Trigger C** | none | yes (section refs differ) | procedure |
| E4-048 | Rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of its depth tag. | rationale-only | L815 — after Step 2 table | - | - | gate (c) | none | yes | rationale |
| E4-049 | Row 1 comes first so parts (e) and (f) stay reachable unchanged. | rationale-only | L815 — after Step 2 table | - | - | parts (e), (f) | none | yes | rationale |
| E4-050 | Whatever row fires, when the chosen path changes source the re-dispatch follows part (g)'s ordering: Engineer, then the code review for that site, then the affected writer. | ordering | L815 — after Step 2 table | ordered dispatches | chosen path | part (g) | Agent | yes | procedure |
| E4-051 | "Highest-quality" = the smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names. | definition | L817 — What "highest-quality" means | - | unit's ticket | - | none | yes | procedure |
| E4-052 | Total-system complexity counts against a path. | invariant | L817 — What "highest-quality" means | - | - | - | none | yes | procedure |
| E4-053 | Effort is never the tiebreaker between paths of equal completeness. | invariant | L817 — What "highest-quality" means | - | - | - | none | yes | procedure |
| E4-054 | "Adds a mechanism" is a reason to route to gate (c), not a reason to build. | invariant | L817 — What "highest-quality" means | - | - | gate (c) | none | yes | procedure |
| E4-055 | For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently". | definition | L817 — What "highest-quality" means | - | change-set type | - | none | yes | procedure |
| E4-056 | "Introduces a mechanism" = the path adds machinery per the mechanism definition in `agents/analyst.md` that the approved design for this unit did not enumerate. | definition | L819 — What "introduces a mechanism" means | - | `agents/analyst.md` mechanism definition | `agents/analyst.md` | none | yes | procedure |
| E4-057 | The approved design for this unit is the Subtask body, its parent Task body, plus the PRD/SDD the Plan Bee's `reference_materials` resolves to (or the Plan Bee body when null/empty). | definition | L819 — What "introduces a mechanism" means | - | Subtask body, Task body, `reference_materials`, Plan Bee body | - | bees | diverges: fix-issue uses the `## Authoritative design directive` block from Section 3's Analyst gate | procedure |
| E4-058 | The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2; a tagged path routes to gate (c) with no further judgment. | invariant | L819 — What "introduces a mechanism" means | gate (c) | `[introduces-mechanism]` tag | row 2, gate (c) | AskUserQuestion | yes | procedure |
| E4-059 | Orchestrator-side mechanism detection is the fallback, used only when no tag is present: read the fix path's description against the definition and route the same way. | invariant | L819 — What "introduces a mechanism" means | gate (c) | fix path description | `agents/analyst.md` | none | yes | procedure |
| E4-060 | The orchestrator MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent (R2/R3 rounds). | invariant | L821 — (b) ANTI-PATTERN | - | dispatch prompt | - | Agent | yes | procedure |
| E4-061 | Forbidden dispatch-prompt phrasings (and close paraphrases): `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. | definition | L821 — (b) ANTI-PATTERN | - | dispatch prompt | - | Agent | yes | procedure |
| E4-062 | Inlining a scope-bound silently narrows the fix without the user ever seeing the decision. | rationale-only | L821 — (b) ANTI-PATTERN | - | - | - | none | yes | rationale |
| E4-063 | When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through the scope-bounding gate in part (c) instead. | gate | L821 — (b) ANTI-PATTERN | gate (c) | scope-bound intent | part (c) | AskUserQuestion | yes | procedure |
| E4-064 | The prohibition targets narrowing language, not path selection: a prompt naming the part-(a) chosen path and carrying its fix in full is not a violation. | invariant | L823 — The prohibition targets narrowing language | - | dispatch prompt | part (a) | Agent | yes | procedure |
| E4-065 | Instructing the implementer to do less than the chosen path is a violation of part (b). | invariant | L823 — The prohibition targets narrowing language | - | dispatch prompt | part (b) | Agent | yes | procedure |
| E4-066 | A path itself narrower than the smallest internally-consistent complete fix is never written into a prompt; it routes to gate (c) via row 4. | invariant | L823 — The prohibition targets narrowing language | gate (c) | chosen path | row 4, gate (c) | AskUserQuestion | yes | procedure |
| E4-067 | Gate (c) has four entry conditions: would-otherwise-scope-bound (part (b)), and rows 2, 3, and 4 of part (a). | gate | L825 — (c) Scope-bounding gate | gate (c) fire | Step 2 result, scope-bound intent | part (b), part (a) rows 2-4 | AskUserQuestion | yes | procedure |
| E4-068 | Downstream, the part-(b) scope-bound condition is read as row 4; every rule enumerating "row 2, 3, or 4" covers it without naming it. | definition | L825 — (c) Scope-bounding gate | - | - | part (b), row 4 | none | yes | procedure |
| E4-069 | On any of the four conditions, fire an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract with the finite choices below. | gate | L825 — (c) Scope-bounding gate | `gate-askuserquestion-<short-suffix>` task, `AskUserQuestion` | entry condition | Two-step gate mechanics | TaskList, AskUserQuestion | yes | procedure |
| E4-070 | The finding's severity determines which of gate (c)'s choices are available. | choice-set | L825-L827 — (c) Scope-bounding gate | choice set | severity tag | - | AskUserQuestion | yes | procedure |
| E4-071 | A `blocker` can never be accepted, and can be deferred only with a narrowing. | invariant | L827 — Severity rules the choice set | - | severity tag | - | none | yes | procedure |
| E4-072 | On a `blocker`, `Accept the limitation` is unreachable unconditionally: do not offer it, do not mark it Recommended, do not route to it by any other path. | choice-set | L829 — Severity rules the choice set | - | severity tag | - | AskUserQuestion | yes | procedure |
| E4-073 | Accepting a blocker ships the blocker. | rationale-only | L829 — Severity rules the choice set | - | - | - | none | yes | rationale |
| E4-074 | A `blocker` always gets the base pair `Fix properly now` and `Cancel`; these two are its floor. | choice-set | L830 — Severity rules the choice set | choice set | severity tag | - | AskUserQuestion | diverges: fix-issue base pair is `Fix properly now` + `Re-dispatch the Analyst with this finding` | procedure |
| E4-075 | When the two Defer conditions do not both hold, the base pair is the whole `blocker` choice set. | choice-set | L830 — Severity rules the choice set | choice set | Defer conditions (i), (ii) | - | AskUserQuestion | yes | procedure |
| E4-076 | Blocker choice `Fix properly now` — same behavior as the `suggestion`/`nit` bullet below. | choice-set | L832 — Severity rules the choice set | implementer dispatch | - | E4-097 | Agent | yes | procedure |
| E4-077 | Blocker choice `Cancel` ends work on the unit under review without the chosen fix landing, and ends the run, exactly as part (d)'s `Cancel` does. | choice-set | L833 — Severity rules the choice set | run stop | - | part (d) `Cancel` | none | diverges: fix-issue has no `Cancel` at gate (c); Analyst re-dispatch instead | procedure |
| E4-078 | `Cancel` routes through `##### Aborted-run close-out` (Section 4.2), sweeping the TaskList by prefix at the scope of the review site the gate fired from. | recovery | L833 — Severity rules the choice set | TaskList sweep | review site scope | `##### Aborted-run close-out`, Section 4.2 | TaskList | diverges: fix-issue routes to `#### Aborted-Issue close-out` (Section 7) | procedure |
| E4-079 | The close-out then runs the Epic-boundary state-externalization checkpoint on its aborted path. | recovery | L833 — Severity rules the choice set | run-state manifest rewrite | - | Epic-boundary state-externalization checkpoint | none | no | procedure |
| E4-080 | The close-out then stops the run naming the uncommitted working-tree state and the `/quo-execute <bee-id>` resume command. | recovery | L833 — Severity rules the choice set | stop message | working tree | `/quo-execute <bee-id>` | git | no | procedure |
| E4-081 | `Cancel` is execute mode's analog of `/quo-fix-issue`'s `Re-dispatch the Analyst with this finding`: a stop-and-re-plan answer, not a narrowing. | rationale-only | L833 — Severity rules the choice set | - | - | `/quo-fix-issue`, `Re-dispatch the Analyst with this finding` | none | diverges: execute has no Analyst | rationale |
| E4-082 | Execute mode has no Issue concept and its abort always ends the run, so blocker `Cancel` does not proceed to the next Task. | invariant | L833 — Severity rules the choice set | - | - | - | none | diverges: fix-issue Cancel branches on mode in close-out | procedure |
| E4-083 | `Ctrl-C` remains the unconditional run-level abort. | definition | L833 — Severity rules the choice set | - | - | - | none | yes | procedure |
| E4-084 | Add `Defer to follow-up Issue` as a third blocker choice only when both hold: (i) the fix path the finding needs introduces a mechanism; (ii) that mechanism serves a case outside this unit's stated defect. | choice-set | L835 — Severity rules the choice set | choice set | `[introduces-mechanism]` tag or orchestrator reading, stated defect | `agents/analyst.md` | AskUserQuestion | yes | procedure |
| E4-085 | Condition (ii) means the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships. | definition | L835 — Severity rules the choice set | - | - | - | none | yes | procedure |
| E4-086 | A narrowing may never reduce coverage of the stated defect. | invariant | L835 — Severity rules the choice set | - | stated defect | - | none | yes | procedure |
| E4-087 | When the blocker cannot be made inapplicable without leaving the stated defect partly unfixed, it is in scope: it takes one of the base pair, never `Defer`. | invariant | L835 — Severity rules the choice set | choice set | condition (ii) | - | AskUserQuestion | yes | procedure |
| E4-088 | On a blocker, the deferral is paired with the narrowing, never shipped alone. | invariant | L835 — Severity rules the choice set | - | - | - | none | yes | procedure |
| E4-089 | File the follow-up Issue first, carrying the reviewer's sketched design verbatim. | ordering | L835 — Severity rules the choice set | follow-up Issue | reviewer's sketched design | `/quo-file-issue` | bees | yes | procedure |
| E4-090 | Dispatch the narrowing (remove or scope down the mechanism-needing part) only once `/quo-file-issue` has returned an Issue ID. | ordering | L835 — Severity rules the choice set | narrowing dispatch | Issue ID | `/quo-file-issue`, part (f) | Agent, bees | yes | procedure |
| E4-091 | Part (f) forbids shipping the narrowing when the filing failed; Trigger A writes its entry in that same window. | invariant | L835 — Severity rules the choice set | tracker entry (Trigger A) | filing result | part (f), Trigger A | none | yes | procedure |
| E4-092 | Dispatch the blocker's narrowing directly, not by re-entering Step 2 (which would match row 4 and route back to this gate). | invariant | L835 — Severity rules the choice set | narrowing dispatch | - | Step 2, row 4 | Agent | yes | procedure |
| E4-093 | The blocker-narrowing terminality and the `Defer to follow-up Issue` bullet's soft-fix terminality are one rule applied to two cases. | rationale-only | L835 — Severity rules the choice set | - | - | E4-100 | none | yes | rationale |
| E4-094 | When the Defer-with-narrowing pairing is available on a blocker, mark that choice `(Recommended)`, on the reasoning of **Recommended default on the mechanism row.** | choice-set | L835 — Severity rules the choice set | `(Recommended)` marker | conditions (i), (ii) | **Recommended default on the mechanism row.** | AskUserQuestion | yes | procedure |
| E4-095 | The blocker Defer branch applies whichever row fired gate (c) — 2, 3 or 4 — because condition (i) tests the path the finding needs, not the chosen path. | invariant | L835 — Severity rules the choice set | - | needed fix path | rows 2-4 | none | yes | procedure |
| E4-096 | A `suggestion` or `nit` keeps the narrower rule: its Defer default is row-2 only. | invariant | L835 — Severity rules the choice set | - | severity tag | **Recommended default on the mechanism row.** | none | yes | procedure |
| E4-097 | Gate (c) fires for a `blocker` like any other finding: the base pair is a real decision, three choices when the Defer-with-narrowing branch is open. | gate | L837 — Severity rules the choice set | gate (c) fire | severity tag | - | AskUserQuestion | yes | procedure |
| E4-098 | The Defer bullet's no-fix-this-round branch cannot arise for a blocker: condition (ii) guarantees a narrowing exists and it always ships. | invariant | L837 — Severity rules the choice set | - | - | E4-105 | none | yes | procedure |
| E4-099 | The Defer bullet's never-invent-a-narrowing prohibition concerns an empty soft-fix slot on a non-blocker, not the narrowing a blocker's Defer requires. | invariant | L837 — Severity rules the choice set | - | - | E4-106 | none | yes | procedure |
| E4-100 | The Defer bullet's soft-fix identification does not apply to a blocker: what ships is the required narrowing, not the most complete remaining path. | invariant | L837 — Severity rules the choice set | - | - | E4-103 | none | yes | procedure |
| E4-101 | The three bulleted choices (`Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`) are the choice set for `suggestion`- and `nit`-severity findings. | choice-set | L837 — Severity rules the choice set | choice set | severity tag | - | AskUserQuestion | yes | procedure |
| E4-102 | Section 6.5's **Trigger B** is unreachable for `blocker` findings; no tracker entry can record an accepted blocker. | invariant | L837 — Severity rules the choice set | - | - | Section 6.5 **Trigger B** | none | yes (section refs differ) | procedure |
| E4-103 | **Trigger A** is reachable for a blocker on gate (c)'s Defer-with-narrowing branch and part (d)'s Defer branch; its entry must carry the narrowing record. | invariant | L837 — Severity rules the choice set | tracker entry `Rationale` | Defer branch | Trigger A, part (d) | none | yes | procedure |
| E4-104 | `Fix properly now` — re-dispatch the appropriate implementer Agent per Section 3's dispatch shape to address the finding fully, no scope-bound. | choice-set | L839 — (c) choices | implementer Agent dispatch | finding | Section 3 dispatch shape | Agent, TaskList | yes (section refs differ) | procedure |
| E4-105 | `Defer to follow-up Issue` — file a follow-up Issue via `/quo-file-issue` inline via the Skill tool, carrying the finding's description, and proceed with the soft fix this round. | choice-set | L840 — (c) choices | follow-up Issue, soft-fix dispatch | finding description | `/quo-file-issue`, `/quo-fix-issue` Section 1's URL-resolution sub-step | bees, Agent | diverges: precedent cross-ref points at `/quo-fix-issue` Section 1 (fix-issue cites its own Section 1) | procedure |
| E4-106 | The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside. | definition | L840 — (c) choices | - | enumerated paths | - | none | yes | procedure |
| E4-107 | Dispatch the soft fix directly, not by re-entering Step 2 (a remaining path is narrower by definition and would match row 4). | invariant | L840 — (c) choices | soft-fix dispatch | - | Step 2, row 4 | Agent | yes | procedure |
| E4-108 | When the deferred path was the only one enumerated, ship no fix for this finding this round (same end state as `Accept the limitation`, with the Issue filed). | choice-set | L840 — (c) choices | - | path count | - | none | yes | procedure |
| E4-109 | Never invent a narrowing to fill the soft-fix slot; part (b) forbids it. | invariant | L840 — (c) choices | - | - | part (b) | none | yes | procedure |
| E4-110 | `Accept the limitation` — record the limitation as an accepted compromise via the `#### Session-scoped compromise tracker` block in Section 6.5, and proceed. | choice-set | L841 — (c) choices | compromise-tracker entry | finding | `#### Session-scoped compromise tracker`, Section 6.5 | none | yes (section refs differ) | procedure |
| E4-111 | Gate (c)'s question text includes the finding verbatim plus a one-line context line stating which of the four entry conditions fired. | field-or-template | L843 — (c) question text | `AskUserQuestion` text | finding, entry condition | - | AskUserQuestion | yes | procedure |
| E4-112 | There is no `Cancel` option on the `suggestion` / `nit` choice set at gate (c). | choice-set | L843 — (c) question text | choice set | severity tag | - | AskUserQuestion | diverges: fix-issue says no `Cancel` at gate (c) at all | procedure |
| E4-113 | Scope-bounding a `suggestion`/`nit` is per-finding and a `Cancel` there would be ambiguous; the user retains `Ctrl-C`. | rationale-only | L843 — (c) question text | - | - | - | none | yes | rationale |
| E4-114 | `Cancel` appears only in the `blocker` choice set, where it means stop the run and re-plan, never "shelve this finding". | choice-set | L843 — (c) question text | - | severity tag | - | AskUserQuestion | diverges: execute-only | procedure |
| E4-115 | When gate (c) fires on row 2 (mechanism serving a case the ticket never mentions), `Defer to follow-up Issue` is the recommended default — mark it `(Recommended)`. | choice-set | L845 — Recommended default on the mechanism row | `(Recommended)` marker | row 2 | - | AskUserQuestion | yes | procedure |
| E4-116 | The row-2 recommended default holds at every severity: on `suggestion`/`nit` the deferral ships the soft fix; on `blocker` it ships the required narrowing. | invariant | L845 — Recommended default on the mechanism row | - | severity tag | E4-084 | none | yes | procedure |
| E4-117 | On a blocker, the row-2 default applies only where the Defer-with-narrowing branch is open; when the coverage guard withholds `Defer`, there is no choice to mark. | invariant | L845 — Recommended default on the mechanism row | - | conditions (i), (ii) | - | AskUserQuestion | yes | procedure |
| E4-118 | A mechanism the ticket never asked for has its own lifecycle; building it inside this unit turns one finding into several rounds. | rationale-only | L845 — Recommended default on the mechanism row | - | - | - | none | yes | rationale |
| E4-119 | The follow-up Issue MUST carry the reviewer's sketched design verbatim. | invariant | L845 — Recommended default on the mechanism row | follow-up Issue body | reviewer's sketched design | `/quo-file-issue` | bees | yes | procedure |
| E4-120 | When Step 2 routes a finding to gate (d) (row 1 or row 5), fire an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L847 — (d) Routing-decision gate | `gate-askuserquestion-<short-suffix>` task, `AskUserQuestion` | Step 2 rows 1, 5 | Two-step gate mechanics | TaskList, AskUserQuestion | yes | procedure |
| E4-121 | At gate (d), a `blocker`'s `Defer to follow-up Issue` is unreachable unless part (c)'s two conditions both hold. | choice-set | L849 — Severity rules the choice set here too | choice set | severity tag, conditions (i), (ii) | part (c) | AskUserQuestion | yes | procedure |
| E4-122 | At gate (d) a narrowing may never reduce coverage; a blocker that cannot be made inapplicable is in scope and takes one of the listed choices rather than `Defer`. | invariant | L849 — Severity rules the choice set here too | - | stated defect | - | none | yes | procedure |
| E4-123 | When both conditions hold at gate (d), offer Defer on part (c)'s terms: paired with the narrowing in the same round, `(Recommended)`, Issue carrying the sketched design verbatim. | choice-set | L849 — Severity rules the choice set here too | `Defer` choice, follow-up Issue | conditions (i), (ii) | part (c) | AskUserQuestion, bees | yes | procedure |
| E4-124 | A blocker's Defer `(Recommended)` takes precedence over the per-path marker: withhold the marker from every other choice so exactly one choice carries it. | invariant | L849 — Severity rules the choice set here too | `(Recommended)` marker | - | part (c), E4-130 | AskUserQuestion | yes (fix-issue also names the Analyst choice as one to withhold from) | procedure |
| E4-125 | When the two conditions do not hold at gate (d), do not offer `Defer`, do not mark it Recommended, do not route to it by any other path. | choice-set | L849 — Severity rules the choice set here too | choice set | conditions (i), (ii) | - | AskUserQuestion | yes | procedure |
| E4-126 | When Defer is offered to a blocker at gate (d), the deferral is paired with a narrowing dispatched this round, never shipped alone. | invariant | L849 — Severity rules the choice set here too | narrowing dispatch | - | E4-133 | Agent | yes | procedure |
| E4-127 | The Defer bullet's "rather than picking a path now" describes the non-blocker case, where nothing ships against the finding this round. | definition | L849 — Severity rules the choice set here too | - | - | E4-133 | none | yes | procedure |
| E4-128 | The choice set for a non-deferrable `blocker` at gate (d) is the one-choice-per-fix-path list plus **Cancel**. | choice-set | L849 — Severity rules the choice set here too | choice set | enumerated paths | - | AskUserQuestion | diverges: fix-issue adds `Re-dispatch the Analyst with this finding` | procedure |
| E4-129 | This skill has no Analyst, so `/quo-fix-issue`'s `Re-dispatch the Analyst with this finding` has no counterpart; `Cancel` carries that answer, as at gate (c). | definition | L849 — Severity rules the choice set here too | - | - | `/quo-fix-issue`, `Re-dispatch the Analyst with this finding` | none | diverges: execute-only | procedure |
| E4-130 | A row-1 non-deferrable finding can arrive with no fix path enumerated; gate (d) still fires with an empty per-path list, so the listed choices are `Cancel` alone. | choice-set | L849 — Severity rules the choice set here too | choice set | fix-path count | row 1 | AskUserQuestion | diverges: fix-issue marks the Analyst re-dispatch `(Recommended)` in the empty-list case | procedure |
| E4-131 | A zero-path blocker whose two Defer conditions do hold still gets `Defer to follow-up Issue`, marked `(Recommended)` per the precedence rule. | choice-set | L849 — Severity rules the choice set here too | choice set | conditions (i), (ii) | E4-124 | AskUserQuestion | yes | procedure |
| E4-132 | On a zero-path fire the question text says the reviewer enumerated no fix path; the user directs the fix through `AskUserQuestion`'s auto-appended free-text slot or cancels. | field-or-template | L849 — Severity rules the choice set here too | `AskUserQuestion` text | fix-path count | - | AskUserQuestion | no | procedure |
| E4-133 | When the user gives a prose direction, dispatch it per Section 3's dispatch shape, carrying that direction as the fix. | command | L849 — Severity rules the choice set here too | implementer Agent dispatch | user prose answer | Section 3 dispatch shape | Agent, TaskList | no | procedure |
| E4-134 | A user-directed fix is not an ungated route, so Section 6.5's **Trigger C** writes nothing for it. | invariant | L849 — Severity rules the choice set here too | - | user prose answer | Section 6.5 **Trigger C** | none | no | procedure |
| E4-135 | When the user gives no direction — neither prose nor `Cancel` — do not invent a dispatch for a shapeless emission; re-fire the gate. | recovery | L849 — Severity rules the choice set here too | gate (d) re-fire | gate answer | - | TaskList, AskUserQuestion | no | procedure |
| E4-136 | No `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing. | invariant | L849 — Severity rules the choice set here too | - | - | part (c) | none | yes | procedure |
| E4-137 | The tracker's `User picked Accept the limitation` `Decision` value can never describe a `blocker` finding. | invariant | L849 — Severity rules the choice set here too | - | tracker `Decision` field | compromise tracker | none | yes | procedure |
| E4-138 | The tracker's `User picked Defer to follow-up Issue` value describes a blocker only when that entry's `Rationale` carries the narrowing record Trigger A requires. | invariant | L849 — Severity rules the choice set here too | tracker `Rationale` field | Trigger A entry | Trigger A | none | yes | procedure |
| E4-139 | Gate (d) offers one choice per reviewer-surfaced fix path; each description includes that path's depth tag (e.g., `re-architect`, `refactor-locally`). | choice-set | L851 — (d) choices | choice set | enumerated paths, depth tags | - | AskUserQuestion | yes | procedure |
| E4-140 | The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1; the gate asks the user to ratify or override that pick. | choice-set | L851 — (d) choices | `(Recommended)` marker | Step 1 pick | part (a) Step 1 | AskUserQuestion | yes | procedure |
| E4-141 | When `[preferred]` marks a narrowing and a fuller path is the complete change, mark the fuller path Recommended and say in its description that the reviewer preferred the other. | choice-set | L851 — (d) choices | choice description | `[preferred]` token | Step 1 | AskUserQuestion | yes | procedure |
| E4-142 | Fallback: on a row-1 entry (no or malformed depth tag) no Step-1 pick was possible, so no path is marked Recommended. | choice-set | L851 — (d) choices | - | row 1 | - | AskUserQuestion | yes | procedure |
| E4-143 | Gate (d) `Defer to follow-up Issue` — file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now. | choice-set | L852 — (d) choices | follow-up Issue | finding description | `/quo-file-issue` | bees | yes | procedure |
| E4-144 | Gate (d) `Cancel` ends work on the unit under review without the chosen fix landing, and ends the run. | choice-set | L853 — (d) choices | run stop | - | - | none | diverges: fix-issue `Cancel` ends the current Issue and the close-out's mode branch decides the run | procedure |
| E4-145 | Gate (d) `Cancel` routes through `##### Aborted-run close-out` (Section 4.2), sweeping the TaskList by prefix at the scope of the site the finding came from. | recovery | L853 — (d) choices | TaskList sweep | finding's review site | `##### Aborted-run close-out`, Section 4.2 | TaskList | diverges: fix-issue routes to `#### Aborted-Issue close-out` (Section 7) with a deferral-hygiene gate | procedure |
| E4-146 | The gate (d) `Cancel` close-out runs the Epic-boundary state-externalization checkpoint on its aborted path, then stops naming the uncommitted tree and `/quo-execute <bee-id>`. | recovery | L853 — (d) choices | manifest rewrite, stop message | working tree | Epic-boundary state-externalization checkpoint, `/quo-execute <bee-id>` | git | no | procedure |
| E4-147 | Gate (d) `Cancel` does not proceed to the next Task; `Ctrl-C` remains the unconditional run-level abort. | invariant | L853 — (d) choices | - | - | - | none | diverges: fix-issue batch mode may advance via mode branch | procedure |
| E4-148 | Gate (d)'s question text includes the finding verbatim. | field-or-template | L855 — (d) question text | `AskUserQuestion` text | finding | - | AskUserQuestion | yes | procedure |
| E4-149 | A finding emitted without a depth tag (legacy or hand-authored) MUST be treated as `re-architect` depth and routed to gate (d). | invariant | L857 — (e) Backwards-compatibility shim | gate (d) | depth tag absence | part (d) | AskUserQuestion | yes | procedure |
| E4-150 | When the orchestrator cannot determine a finding's depth, surface the decision to the user rather than dispatching its own pick ungated under row 6. | invariant | L857 — (e) Backwards-compatibility shim | gate (d) | depth tag | row 6 | AskUserQuestion | yes | procedure |
| E4-151 | A PM emission that `agents/pm.md`'s tracker-check bullet designates a report note (not a finding) is exempt from the shim and from part (f)'s malformed-tag bullet. | invariant | L857 — (e) Backwards-compatibility shim | - | PM report note | `agents/pm.md` tracker-check bullet, part (f) | none | yes | procedure |
| E4-152 | Malformed tags: a severity not exactly `blocker`/`suggestion`/`nit`, or depth not exactly `trivial-tweak`/`refactor-locally`/`re-architect`, is treated as `re-architect` depth per part (e). | recovery | L861 — (f) Edge-case handling — Malformed tags | gate (d) | tags | part (e) | AskUserQuestion | yes | procedure |
| E4-153 | On a malformed tag, also surface the parse failure to the user so the reviewer emission can be corrected. | recovery | L861 — (f) Edge-case handling — Malformed tags | user-facing message | tags | - | none | yes | procedure |
| E4-154 | Routing ambiguity: if the table returns more than one decision (impossible by construction), default to gate (d) and surface the ambiguity to the user. | recovery | L862 — (f) Edge-case handling — Routing ambiguity | gate (d) | Step 2 result | part (d) | AskUserQuestion | yes | procedure |
| E4-155 | When the user picks `Defer to follow-up Issue` at gate (c) or (d) but the inline `/quo-file-issue` fails or the user cancels inside it, MUST NOT silently ship the soft fix or no fix. | invariant | L863 — (f) Edge-case handling — `/quo-file-issue` failure | - | `/quo-file-issue` result | `/quo-file-issue`, parts (c), (d) | bees | yes | procedure |
| E4-156 | On a filing failure, surface the failure to the user and re-prompt with the same gate's choices. | recovery | L863 — (f) Edge-case handling — `/quo-file-issue` failure | gate re-fire | filing failure | - | TaskList, AskUserQuestion | yes | procedure |
| E4-157 | The re-prompt lets the user re-attempt the defer, pick `Accept the limitation` where it exists (non-`blocker` only), pick a specific fix path, or Cancel. | choice-set | L863 — (f) Edge-case handling — `/quo-file-issue` failure | choice set | severity tag | parts (c), (d) | AskUserQuestion | yes | procedure |
| E4-158 | On the re-prompt, Cancel is available at either gate on a `blocker` (part (c) offers it in a blocker's base pair) and at the routing gate only otherwise. | choice-set | L863 — (f) Edge-case handling — `/quo-file-issue` failure | choice set | severity tag | part (c) | AskUserQuestion | diverges: fix-issue offers Cancel at the routing gate only | procedure |
| E4-159 | A `blocker` can reach the filing-failure bullet via the Defer-with-narrowing branch; do not ship the narrowing when the filing failed. | invariant | L863 — (f) Edge-case handling — `/quo-file-issue` failure | - | filing result | E4-084 | none | yes | procedure |
| E4-160 | On a blocker's failed filing, re-prompt with the same gate's choices so the user re-attempts the filing or picks a non-deferring choice. | recovery | L863 — (f) Edge-case handling — `/quo-file-issue` failure | gate re-fire | filing failure | - | TaskList, AskUserQuestion | yes | procedure |
| E4-161 | The narrowing is legitimate only paired with the follow-up Issue that carries the deferred design. | rationale-only | L863 — (f) Edge-case handling — `/quo-file-issue` failure | - | - | - | none | yes | rationale |
| E4-162 | Once routing is settled (own pick per part (a), or user pick at gate (c)/(d)), decide how many lanes to dispatch at once. | ordering | L865 — (g) Re-dispatch ordering | - | routing decision | parts (a), (c), (d) | Agent | yes | procedure |
| E4-163 | When the chosen fix path requires a source change, the Engineer re-dispatch and the affected writer re-dispatch are ordered, not concurrent. | ordering | L865 — (g) Re-dispatch ordering | - | chosen path | - | Agent | yes | procedure |
| E4-164 | Dispatch the **Engineer** first, then the code review for that site against the resulting diff, and only once that review has closed dispatch the **Test Writer** and/or **Doc Writer** invalidated. | ordering | L865 — (g) Re-dispatch ordering | Engineer, reviewer, writer dispatches | source change | - | Agent, TaskList | diverges: fix-issue names the **Code Reviewer** as the sole review rung | procedure |
| E4-165 | "The code review for that site" is the **Bee-level Code Reviewer** at Section 5's site (Clause 2) and the **per-Task PM's in-flight `/quo-engineer-review` pass** at the per-Task site (Clause 1). | definition | L865 — (g) Re-dispatch ordering | - | review site | Section 5, Clause 1, Clause 2, `/quo-engineer-review` | none | no | procedure |
| E4-166 | The per-Task PM's `/quo-engineer-review` pass is the per-Task site's only code-review coverage; this skill dispatches no per-Task Code Reviewer. | definition | L865 — (g) Re-dispatch ordering | - | - | `/quo-engineer-review` | none | no | procedure |
| E4-167 | Dispatching the Engineer and a writer in the same round hands the writer a diff the pending code review is about to rewrite, forcing redo. | rationale-only | L865 — (g) Re-dispatch ordering | - | - | - | none | yes | rationale |
| E4-168 | One elision: when the Engineer round is the final `trivial-tweak` nit pass per **Severity bounds the loop**, skip the code-review rung and dispatch the affected writer once that Engineer returns. | ordering | L865 — (g) Re-dispatch ordering | writer dispatch | E4-017 | **Severity bounds the loop** | Agent | yes | procedure |
| E4-169 | Every source-changing round other than the final `trivial-tweak` nit pass keeps the code-review rung. | ordering | L865 — (g) Re-dispatch ordering | reviewer dispatch | - | - | Agent | yes | procedure |
| E4-170 | The Engineer-dispatch precondition that makes part (g) checkable is TaskList-derived. | definition | L867 — (g) precondition preamble | - | TaskList | - | TaskList | diverges: fix-issue defers to Section 4's Reconcile-step **Engineer-dispatch precondition** with `<issue-id>` prefixes | procedure |
| E4-171 | The precondition has two clauses because this section routes findings from two review sites with different diff extents; apply the clause for the site the finding came from. | precondition | L867 — (g) precondition preamble | - | finding's review site | Clause 1, Clause 2 | TaskList | no | procedure |
| E4-172 | In both clauses, match on the TaskList name prefix plus status, not an exact name, so any discriminator a re-dispatch appends is caught. | precondition | L867 — (g) precondition preamble | - | TaskList task names, statuses | - | TaskList | yes (fix-issue states the prefix rule via Section 4) | procedure |
| E4-173 | TaskList is one of the four authoritative read-state sources the reconciliation loop reads every tick, so either clause is a state lookup, not a rule held across compaction. | rationale-only | L867 — (g) precondition preamble | - | - | reconciliation loop | TaskList | no | rationale |
| E4-174 | **Clause 1** applies to findings from the per-Task PM Agent (driving `/quo-engineer-review` and `/quo-doc-writer-review` in flight per `agents/pm.md`); its scope is the Task under review. | definition | L869 — Clause 1 — the per-Task review site | - | finding's origin | `/quo-engineer-review`, `/quo-doc-writer-review`, `agents/pm.md` | none | no | procedure |
| E4-175 | Clause 1: MUST NOT dispatch an Engineer for a Task while any TaskList task named `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` (Subtask of that Task) or that Task's `pm-<task-id>` is `pending` or `in_progress`. | precondition | L869 — Clause 1 — the per-Task review site | Engineer dispatch (gated) | TaskList tasks, statuses | Section 3 naming convention | TaskList, Agent | no | procedure |
| E4-176 | Implementer TaskList names are Subtask-scoped (`<role>-<subtask-id>` per Section 3's naming convention); the PM's is Task-scoped (`pm-<task-id>`). | name-class | L869 — Clause 1 — the per-Task review site | - | - | Section 3 naming convention | TaskList | no | procedure |
| E4-177 | Resolve each active writer task's Subtask to its parent Task via `bees show-ticket --ids <subtask-id>`, reading its `parent`, before comparing against the Task under review. | command | L869 — Clause 1 — the per-Task review site | parent Task id | subtask id embedded in task name | - | bees, TaskList | no | procedure |
| E4-178 | Prefix matching in Clause 1 is what catches a re-dispatched lane's `-r<n>` name (`doc-writer-<subtask-id>-r1` and so on). | precondition | L869 — Clause 1 — the per-Task review site | - | TaskList names | - | TaskList | no | procedure |
| E4-179 | The PM is in Clause 1's list because it runs the review: Engineer edits landing under an in-flight `pm-<task-id>` invalidate the review whose findings are being routed. | rationale-only | L869 — Clause 1 — the per-Task review site | - | - | - | none | no | rationale |
| E4-180 | **Clause 2** applies to Section 5's Bee-level review, where reviewers are Bee-scoped (`<reviewer>-<bee-id>`) and the diff spans every Task; its scope is the whole Bee. | definition | L871 — Clause 2 — the Bee-level review site | - | finding's origin | Section 5 | none | no | procedure |
| E4-181 | Clause 2: MUST NOT re-dispatch an Engineer — Bee-scoped (`engineer-<bee-id>`) or Subtask-scoped — while any TaskList task beginning with a listed prefix is `pending` or `in_progress`. | precondition | L871 — Clause 2 — the Bee-level review site | Engineer dispatch (gated) | TaskList tasks, statuses | - | TaskList, Agent | no | procedure |
| E4-182 | Clause 2 prefix: `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` for any Subtask anywhere in this Bee. | name-class | L873 — Clause 2 prefix list | - | TaskList names | - | TaskList | no | procedure |
| E4-183 | Clause 2 prefix: the Bee-scoped writer names `test-writer-<bee-id>` and `doc-writer-<bee-id>` (Section 5's own re-dispatches, per Section 3's naming convention). | name-class | L874 — Clause 2 prefix list | - | TaskList names | Section 5, Section 3 naming convention | TaskList | no | procedure |
| E4-184 | Clause 2 prefix: the Bee-level reviewer names `code-reviewer-<bee-id>`, `test-reviewer-<bee-id>`, `doc-reviewer-<bee-id>`. | name-class | L875 — Clause 2 prefix list | - | TaskList names | - | TaskList | no | procedure |
| E4-185 | Clause 2 prefix: any `pm-<task-id>` task, and the Bee-scoped `pm-<bee-id>`. | name-class | L876 — Clause 2 prefix list | - | TaskList names | - | TaskList | no | procedure |
| E4-186 | In Clause 2 match on prefix plus status in every case, so `-r<n>` names (`code-reviewer-<bee-id>-r1`, `pm-<bee-id>-r2`, …) are still caught. | precondition | L878 — Clause 2 | - | TaskList names | - | TaskList | no | procedure |
| E4-187 | The Bee-level Code Reviewer is in Clause 2's list (unlike Clause 1's PM-only coverage) because Section 5 dispatches the three reviewers concurrently. | rationale-only | L878 — Clause 2 | - | - | Section 5 | none | diverges: fix-issue deliberately excludes the Code Reviewer from its list | rationale |
| E4-188 | An Engineer re-entering the lane waits for all concurrently-dispatched Bee-level reviewer returns; these are live dispatches that notify, so the wait ends — no deadlock. | rationale-only | L878 — Clause 2 | - | - | - | Agent | no | rationale |
| E4-189 | In both clauses, when a blocking task is `in_progress` (or `pending` with a dispatch already landed), wait for its completion notification and re-check next tick rather than dispatching. | precondition | L880 — both clauses | - | TaskList status, dispatch state | - | TaskList, Agent | yes (fix-issue via Section 4) | procedure |
| E4-190 | When a blocking task is `pending` and no dispatch has landed for it, do not wait — it never notifies and there are no clock primitives ("Anti-pattern: no clock primitives", Section 3). | recovery | L880 — both clauses | - | TaskList status, dispatch state | "Anti-pattern: no clock primitives", Section 3 | TaskList | yes (fix-issue via Section 4) | procedure |
| E4-191 | For a never-dispatched `pending` blocker, either dispatch that role now, or mark the stale task `completed` and clear it from the active set, then re-check. | recovery | L880 — both clauses | dispatch or `completed` status flip | stale TaskList task | - | TaskList, Agent | yes (fix-issue via Section 4) | procedure |
| E4-192 | Post-compaction, whether a dispatch landed is unreadable (the `Agent(...)` call is gone; TaskList records nothing), so default to not landed. | recovery | L880 — both clauses | - | conversation state, TaskList | - | TaskList | unknown | procedure |
| E4-193 | A duplicate dispatch costs one pass, while a dispatch wrongly assumed landed deadlocks the run on a notification that never comes. | rationale-only | L880 — both clauses | - | - | - | none | unknown | rationale |
| E4-194 | Do not narrow either clause to `in_progress` only; `pending` is in the test deliberately to close the race where the task exists but `Agent(...)` has not landed. | invariant | L880 — both clauses | - | TaskList status | - | TaskList | yes (fix-issue via Section 4) | procedure |
| E4-195 | A writer that aborted on source movement does not block an Engineer round, and needs no exemption from either clause. | invariant | L882 — writer aborted on source movement | - | movement report | - | TaskList | no | procedure |
| E4-196 | The movement-report rung in Section 3's Reconcile step marks the aborted writer's `test-writer-<id>` / `doc-writer-<id>` task `completed` and records the owed redelivery as a separate `aborted-<role>-<id>` task. | relay | L882 — writer aborted on source movement | `aborted-<role>-<id>` task, `completed` flip | movement report | Section 3 Reconcile step, movement-report rung | TaskList | no | procedure |
| E4-197 | `aborted-` is a distinct name class, so neither clause's prefix list matches it; the Engineer can be dispatched while the redelivery stays owed. | name-class | L882 — writer aborted on source movement | - | `aborted-*` tasks | - | TaskList | no | procedure |
| E4-198 | An exemption keyed on an abort annotation would make Engineer dispatch depend on `metadata.activity`, which is informational and never a routing input. | rationale-only | L882 — writer aborted on source movement | - | `metadata.activity` | - | none | no | rationale |
| E4-199 | What an `aborted-*` task gates is the unit's advance (the parent Task's per-Task PM review, or Section 5's Bee-level review loop closing), not the Engineer. | invariant | L882 — writer aborted on source movement | - | `aborted-*` tasks | movement-report rung, Section 5 | TaskList | no | procedure |
| E4-200 | After a movement report, re-dispatch ordering is part (g)'s ordering scoped by the clause governing the finding in play. | ordering | L884 — Ordering after a movement report | - | movement report, mover's site | Clause 1, Clause 2 | Agent | no | procedure |
| E4-201 | Clause 1 mover (Engineer re-dispatched from the per-Task site): let that Engineer and its per-Task review round finish, then re-dispatch the writer for that Subtask. | ordering | L884 — Ordering after a movement report | writer re-dispatch | Engineer return, PM review close | Clause 1 | Agent, TaskList | no | procedure |
| E4-202 | Clause 2 mover (Engineer re-dispatched from Section 5): let the Engineer → Code Reviewer ordering close over the whole Bee's diff, then re-dispatch the affected writer lanes. | ordering | L884 — Ordering after a movement report | writer re-dispatch | Engineer return, Code Reviewer close | Clause 2, Section 5 | Agent, TaskList | no | procedure |
| E4-203 | In either clause, elide the review rung when the moving Engineer round was the final `trivial-tweak` nit pass. | ordering | L884 — Ordering after a movement report | - | E4-168 | E4-168 | Agent | no | procedure |
| E4-204 | Section 3's Reconcile step carries the movement-report receiver (recognition, what is withheld); this part carries only the ordering of the following re-dispatch. | definition | L884 — Ordering after a movement report | - | - | Section 3 Reconcile step | none | no | procedure |
| E4-205 | Part (g) governs the review-finding re-dispatch path only; it does NOT apply to the forward per-Subtask fan-out in Section 3's reconciliation loop. | invariant | L886 — Scope limit | - | - | Section 3 reconciliation loop | Agent | no | procedure |
| E4-206 | An Engineer on one Subtask may run concurrently with a Test Writer or Doc Writer on a different Subtask of the same Task; only re-dispatch rounds are ordered. | invariant | L886 — Scope limit | - | - | - | Agent | no | procedure |
| E4-207 | A finding whose chosen fix path changes no source file carries no ordering constraint: re-dispatch that single writer lane alone, no Engineer round, no code review. | ordering | L888 — no-source-change findings | writer dispatch | chosen path | - | Agent | yes | procedure |
| E4-208 | Both gates (c) and (d) fire through the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L890 — Two-step gate mechanics | - | - | parts (c), (d) | TaskList, AskUserQuestion | yes | procedure |
| E4-209 | First create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, with a distinct per-fire `<short-suffix>` so concurrent or repeated fires do not collide. | name-class | L890 — Two-step gate mechanics | `gate-askuserquestion-<short-suffix>` task | - | Section 4 / Section 3 TaskList naming convention's gate-task entry | TaskList | yes | procedure |
| E4-210 | Then call `AskUserQuestion` with the finite choices in the same turn as the `TaskCreate`. | ordering | L890 — Two-step gate mechanics | `AskUserQuestion` | E4-209 | - | AskUserQuestion | yes | procedure |
| E4-211 | Do not produce a text response describing the gate; fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L890 — Two-step gate mechanics | - | - | - | TaskList, AskUserQuestion | yes | procedure |
| E4-212 | Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. | command | L890 — Two-step gate mechanics | `completed` status flip | gate answer | - | TaskList | yes | procedure |
| E4-213 | Gates are multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot. | invariant | L890 — Two-step gate mechanics | - | - | - | AskUserQuestion | yes | procedure |
| E4-214 | These gates inherit a prose-adherence fragility; it is an execution-time risk acknowledged at run time, not fixed by this section. | rationale-only | L892 — closing | - | - | - | none | yes | rationale |

## Anchors defined here

Headings and bolded phrases (verbatim), with line number.

- L789 `### Orchestrator discipline: routing review findings`
- L791 **enumerated fix paths and their depth tags**
- L791 **deterministically for whether a gate fires**
- L791 **by its own judgment for which path it picks when no gate fires**
- L793 **Severity bounds the loop.**
- L793 **no fix lands against it**
- L793 **A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own.**
- L793 **one** (final implementer pass)
- L793 **no** (further reviewer round)
- L793 **Reviews**
- L793 **the bound keys on what ships**
- L795 **(a) Pick the path, then route on it.**
- L797 **Step 1 — pick.**
- L797 **input**
- L797 **The pick is always one of the paths the reviewer enumerated.**
- L797 **in session**
- L797 **durable**
- L799 **Step 2 — route on the path chosen in Step 1.**
- L799 **in order**
- L815 **Trigger C**
- L815 **regardless of its depth tag**
- L815 **when the chosen path changes source the re-dispatch follows part (g)'s ordering**
- L817 **What "highest-quality" means.**
- L817 **smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names**
- L819 **What "introduces a mechanism" means.**
- L819 **the approved design for this unit did not enumerate**
- L819 **The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2**
- L819 **fallback**
- L821 **(b) ANTI-PATTERN — do not write this:**
- L823 **The prohibition targets *narrowing* language, not path selection.**
- L823 **is** / **in full**
- L825 **(c) Scope-bounding gate.**
- L825 **four**
- L825 **Downstream, the part-(b) scope-bound condition is read as row 4**
- L827 **Severity rules the choice set — a `blocker` can never be accepted, and can be deferred only with a narrowing.**
- L829 **`Accept the limitation` is unreachable, unconditionally**
- L830 **The base pair is always offered.**
- L830 **both**
- L832 **Fix properly now**
- L833 **Cancel**
- L833 **ends the run**
- L833 **not**
- L835 **`Defer to follow-up Issue` is added as a third choice *only when both* of these hold:**
- L835 **introduces a mechanism**
- L835 **and**
- L835 **outside this unit's stated defect**
- L835 **narrowed to the stated defect**
- L835 **A narrowing may never reduce coverage of the stated defect.**
- L835 **in scope**
- L835 **the deferral is paired with the narrowing, never shipped alone**
- L835 **file the follow-up Issue first**
- L835 **verbatim**
- L835 **Dispatch that narrowing directly, not by re-entering Step 2 with it**
- L835 **recommended default**
- L835 **Recommended default on the mechanism row.** (forward reference)
- L835 **It applies whichever row fired this gate on a blocker — 2, 3 or 4.**
- L837 **Neither of the `Defer to follow-up Issue` bullet's closing clauses applies to one:**
- L837 **Trigger B**
- L837 **Trigger A is reachable for one**
- L839 **Fix properly now**
- L840 **Defer to follow-up Issue**
- L840 **The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside**
- L840 **directly**
- L841 **Accept the limitation**
- L843 **There is no `Cancel` option on the `suggestion` / `nit` choice set**
- L845 **Recommended default on the mechanism row.**
- L845 **introduces a mechanism**
- L845 **recommended default**
- L845 **at every severity**
- L845 **verbatim**
- L847 **(d) Routing-decision gate.**
- L849 **Severity rules the choice set here too — a `blocker`'s Defer route is conditional.**
- L849 **unreachable unless part (c)'s two conditions both hold**
- L849 **A narrowing may never reduce coverage of the stated defect**
- L849 **paired with the narrowing in the same round**
- L849 **That `(Recommended)` takes precedence over the per-path marker**
- L849 **every other choice**
- L849 **When it is offered to a blocker here, the deferral is paired with a narrowing dispatched this round, never shipped alone**
- L849 **Cancel**
- L849 **A row-1 finding *that also cannot be deferred* can arrive with no fix path enumerated at all**
- L849 **question text says the reviewer enumerated no fix path**
- L849 **When the user gives a prose direction, dispatch it**
- L849 **Trigger C**
- L849 **no** / **not**
- L849 **no `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing**
- L851 **One choice per reviewer-surfaced fix path**
- L851 **The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1**
- L851 **input**
- L851 **fuller**
- L851 **Fallback:**
- L852 **Defer to follow-up Issue**
- L853 **Cancel**
- L853 **ends the run**
- L853 **not**
- L857 **(e) Backwards-compatibility shim.**
- L857 **without a depth tag**
- L857 **One emission is out of the shim's reach:**
- L859 **(f) Edge-case handling.**
- L861 **Malformed tags.**
- L862 **Routing ambiguity.**
- L863 **`/quo-file-issue` failure at the Defer gate.**
- L863 **A `blocker` can reach this bullet**
- L863 **do not ship the narrowing when the filing failed**
- L865 **(g) Re-dispatch ordering when a fix path changes source.**
- L865 **the orchestrator's own path pick per part (a), or the user's pick at the gate in part (c) or (d)**
- L865 **source change**
- L865 **ordered, not concurrent**
- L865 **Engineer**
- L865 **Bee-level Code Reviewer**
- L865 **per-Task PM's in-flight `/quo-engineer-review` pass**
- L865 **Test Writer**
- L865 **Doc Writer**
- L865 **One elision:**
- L865 **Severity bounds the loop** (back-reference)
- L867 **two**
- L867 **two clauses**
- L867 **prefix**
- L869 **Clause 1 — the per-Task review site**
- L869 **the Task under review**
- L869 **the orchestrator MUST NOT dispatch an Engineer Agent for a Task while any TaskList task whose name begins with `test-writer-<subtask-id>` or `doc-writer-<subtask-id>` for a Subtask of that same Task, or with that Task's own `pm-<task-id>`, is `pending` or `in_progress`.**
- L869 **prefix**
- L871 **Clause 2 — the Bee-level review site**
- L871 **the whole Bee**
- L871 **The orchestrator MUST NOT re-dispatch an Engineer Agent — Bee-scoped (`engineer-<bee-id>`) or Subtask-scoped — while any TaskList task whose name begins with one of the following prefixes is `pending` or `in_progress`:**
- L873 **any**
- L878 **prefix**
- L878 **is**
- L878 **concurrently**
- L878 **all**
- L880 **no dispatch has landed for it**
- L880 **Post-compaction, whether a dispatch landed is unreadable**
- L880 **not**
- L882 **A writer that aborted on source movement does not block an Engineer round, and needs no exemption from either clause.**
- L882 **distinct name class**
- L882 **unit's advance**
- L884 **Ordering after a movement report.**
- L884 **Clause 1**
- L884 **Clause 2**
- L886 **Scope limit — this part governs the review-finding re-dispatch path only.**
- L888 **no source file**
- L890 **Two-step gate mechanics (parts (c) and (d)).**
- L890 **First**
- L890 **then**

## Rationale-only spans

Whole-line spans containing no rule:

- L892–L892 — prose-adherence fragility acknowledged (1 line)

Intra-line rationale sentences (the enclosing line also carries rules, so these are sub-line spans, not line ranges; listed so a rewrite can drop them without losing a rule):

- L793 (final three sentences) — severity orthogonal; coverage-given-up justification
- L797 ("Either way the incomplete menu becomes visible…") — gate makes under-enumeration visible
- L815 ("The evaluation order is load-bearing…") — why rows are ordered so
- L821 ("Inlining a scope-bound silently narrows…") — why inlining is forbidden
- L829 ("Accepting a blocker ships the blocker.") — why Accept is unreachable
- L833 ("This is execute mode's analog…") — Cancel as Analyst-re-dispatch analog
- L835 ("This is the same terminality…one rule") — narrowing/soft-fix terminality unified
- L843 ("scope-bounding a suggestion or nit is a per-finding decision…") — why no Cancel there
- L845 ("A mechanism the ticket never asked for…") — why defer mechanisms
- L863 ("the narrowing is only legitimate paired…") — why not ship narrowing
- L865 ("Dispatching the Engineer and a writer in the same round…") — why ordering avoids redo
- L867 (last sentence) — TaskList is authoritative read-state
- L869 (last sentence) — why PM is in list
- L878 (sentences 2–3) — why Code Reviewer listed; no deadlock
- L880 ("a duplicate dispatch costs one pass…") — default-not-landed cost argument
- L882 ("This is deliberate — an exemption keyed…") — why no abort exemption
- L886 (second sentence) — cross-Subtask overlap is designed
