# Rule inventory — quo-fix-issue SKILL.md L618–L703 (`### Orchestrator discipline: routing review findings`)

Source: `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md`, lines 618–703. Heading abbreviations used in Site: `ODR` = `### Orchestrator discipline: routing review findings`; `SBL` = the **Severity bounds the loop.** paragraph; `(a)`…`(g)` = the bolded part labels; `2SGM` = **Two-step gate mechanics (parts (c) and (d)).**

Mirror column: `yes` = the same statement appears in `/quo-execute`'s section of the same name (verified for the SBL paragraph, which is byte-identical at quo-execute L793; the section heading exists at quo-execute L789); `no` = fix-issue-specific (references Section 3 Analyst gate, `<issue-id>` task names, Phase A, `#### Aborted-Issue close-out`, or diverges from quo-execute's text); `unknown` = not verified against quo-execute.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F4-001 | Each reviewer finding carries a severity tag that is exactly one of `blocker` / `suggestion` / `nit`. | definition | L620, ODR intro | - | reviewer finding emission | in-flow review skills | none | yes | procedure |
| F4-002 | Each fix path a finding proposes carries a depth tag `trivial-tweak` / `refactor-locally` / `re-architect`; the finding also carries the count of fix paths surfaced. | definition | L620, ODR intro | - | reviewer finding emission | - | none | yes | procedure |
| F4-003 | Turn the reviewer's enumerated fix paths and depth tags into exactly one routing decision per finding. | invariant | L620, ODR intro | routing decision | fix paths, depth tags | - | none | yes | procedure |
| F4-004 | Whether a gate fires is decided deterministically; which path is picked when no gate fires is the orchestrator's own judgment. | invariant | L620, ODR intro | - | - | - | none | yes | procedure |
| F4-005 | Never re-classify or invent a reviewer's depth tag; read the depth of a path as emitted. | invariant | L620, ODR intro | - | depth tag | - | none | yes | procedure |
| F4-006 | A review lane's loop (Engineer → code-review at any site; each writer → reviewer pair) is held open by `blocker` and `suggestion` findings and by any `nit` whose chosen path is deeper than `trivial-tweak`. | invariant | L622, SBL | - | severity tag, chosen path depth | - | none | yes | procedure |
| F4-007 | A lane closes when no lane-holding finding remains outstanding. | invariant | L622, SBL | lane closure | F4-006 | - | none | yes | procedure |
| F4-008 | A lane-holding finding stays outstanding until a later cold pass no longer raises it or it reaches a disposition under which no fix lands against it. | invariant | L622, SBL | - | cold-pass result | - | Agent | yes | procedure |
| F4-009 | The no-fix dispositions are: accepted into the compromise tracker, recorded as a `defer-*` task, or closed by `Accept the limitation`, `Cancel`, or `Defer to follow-up Issue` when nothing ships against the finding this round. | definition | L622, SBL | - | tracker entry, `defer-*` task, gate answer | compromise tracker | TaskList, AskUserQuestion | yes | procedure |
| F4-010 | A dispatch settles nothing — ungated at row 6, chosen at a gate, or the soft fix / narrowing shipped alongside a deferral — until a later cold pass has read its result. | invariant | L622, SBL | - | dispatch, cold pass | row 6 | Agent | yes | procedure |
| F4-011 | A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own. | invariant | L622, SBL | - | severity + depth | - | none | yes | procedure |
| F4-012 | When a lane-holding finding already forces another implementer round, `trivial-tweak` nits ride along in it and the next cold pass reads them with everything else. | ordering | L622, SBL | implementer dispatch | F4-006, F4-011 | - | Agent | yes | procedure |
| F4-013 | When only `trivial-tweak` nits remain, apply them in one final implementer pass for that lane and dispatch no further reviewer round for it. | ordering | L622, SBL | final implementer dispatch | F4-011 | - | Agent | yes | procedure |
| F4-014 | At a site where a review runs inside the PM's in-flight review passes, "no further reviewer round" means do not re-dispatch the PM for that lane. | ordering | L622, SBL | - | F4-013 | PM in-flight review passes | Agent | yes | procedure |
| F4-015 | Record the count of nits so applied on the **Reviews** line of the summary for the scope that dispatched the review, as `N nits applied without re-review`. | field-or-template | L622, SBL | summary **Reviews** line | nit count (conversation only) | summary | none | yes | procedure |
| F4-016 | When a compaction has removed the nit count, render `count unavailable post-compaction` rather than guessing. | recovery | L622, SBL | summary **Reviews** line | conversation state | - | none | yes | procedure |
| F4-017 | `trivial-tweak` nits applied without re-review are finished work: never list them as ignored feedback and never make them `defer-*` tasks. | invariant | L622, SBL | - | F4-013 | `defer-*` tasks, ignored-feedback list | TaskList | yes | procedure |
| F4-018 | A `nit` whose chosen fix path would fire a gate under part (a) still routes through the table like any other finding. | invariant | L622, SBL | - | part (a) table | part (a) | none | yes | procedure |
| F4-019 | The bound keys on what ships: when a gate answer ships anything other than the enumerated `trivial-tweak` path (`Fix properly now` on a row-2/-3/-4 fire, or a `Defer`'s soft fix / narrowing), the finding is lane-holding again, a cold pass must read that fix, and part (g)'s elision does not apply. | invariant | L622, SBL | - | gate answer | part (g) | Agent | yes | procedure |
| F4-020 | When the final pass ships only `trivial-tweak` paths and changes source, part (g)'s ordering applies with its code-review rung elided; that rung is the one round this rule suppresses. | ordering | L622, SBL | Engineer + writer dispatch | F4-013 | part (g) | Agent | yes | procedure |
| F4-021 | The bound is the reviewer's own depth tag, not a narrower reading of `nit`; severity means importance, orthogonal to depth. | invariant | L622, SBL | - | depth tag | - | none | yes | procedure |
| F4-022 | The coverage given up is exactly the `trivial-tweak`-nit class: the raising cold pass already read the text, the fix is a `trivial-tweak` by the reviewer's tag, and the post-completion review reads the whole diff. | rationale-only | L622, SBL | - | - | post-completion review | none | yes | rationale |
| F4-023 | Routing is a two-step procedure: Step 1 (pick) is the orchestrator's judgment; Step 2 (route) is deterministic given the chosen path. | ordering | L624, (a) | - | - | - | none | yes | procedure |
| F4-024 | Step 1: choose the highest-quality fix path among those the reviewer enumerated. | command | L626, (a) Step 1 | chosen path | enumerated fix paths, F4-045 | **What "highest-quality" means.** | none | yes | procedure |
| F4-025 | Treat the reviewer's `[preferred]` token as an input, not a verdict: prefer it when it is also the most complete path. | invariant | L626, (a) Step 1 | - | `[preferred]` token | - | none | yes | procedure |
| F4-026 | When `[preferred]` marks a narrowing and a fuller path is still the smallest internally-consistent complete change, take the fuller path. | invariant | L626, (a) Step 1 | chosen path | `[preferred]` token | - | none | yes | procedure |
| F4-027 | The pick is always one of the paths the reviewer enumerated. | invariant | L626, (a) Step 1 | - | enumerated fix paths | - | none | yes | procedure |
| F4-028 | When no enumerated path is the smallest internally-consistent complete change, pick the most complete of them anyway. | recovery | L626, (a) Step 1 | chosen path | enumerated fix paths | - | none | yes | procedure |
| F4-029 | An incomplete pick routes via rows 2, 3, or 4 to gate (c), where `Fix properly now` dispatches the complete fix. | ordering | L626, (a) Step 1 | gate (c) fire | F4-028 | gate (c), rows 2–4 | AskUserQuestion | yes | procedure |
| F4-030 | Exception: a finding whose depth tag is absent or malformed goes via row 1 to gate (d), which has no `Fix properly now`; the user picks among the paths as emitted. | ordering | L626, (a) Step 1 | gate (d) fire | depth tag | row 1, gate (d) | AskUserQuestion | yes | procedure |
| F4-031 | An under-enumerated menu becomes visible in session: a gate fires where it otherwise would not, and the user sees the menu it fired on. | rationale-only | L626, (a) Step 1 | - | - | - | none | yes | rationale |
| F4-032 | A durable record of an incomplete menu reaches the post-completion review only via Trigger A (`Defer to follow-up Issue`) or Trigger B (`Accept the limitation`); `Fix properly now` writes none. | definition | L626, (a) Step 1 | tracker entry (Trigger A/B) | gate answer | Trigger A, Trigger B, post-completion review | none | unknown | procedure |
| F4-033 | The orchestrator does not absorb an enumeration gap by writing a fix path of its own. | invariant | L626, (a) Step 1 | - | - | - | none | yes | procedure |
| F4-034 | Step 2: evaluate the table conditions in order, taking the first that matches, so each finding yields exactly one routing decision. | ordering | L628, (a) Step 2 | routing decision | chosen path | - | none | yes | procedure |
| F4-035 | Row 1: the finding carries no depth tag, or a malformed severity/depth tag → treat as `re-architect` → gate (d). | ordering | L633, (a) Step 2 table | gate (d) fire | severity/depth tags | gate (d), parts (e)/(f) | AskUserQuestion | yes | procedure |
| F4-036 | Row 2: the chosen path carries the reviewer's `[introduces-mechanism]` tag, or introduces a mechanism by the orchestrator's own reading → scope-bounding gate (c). | ordering | L634-L635, (a) Step 2 table | gate (c) fire | `[introduces-mechanism]` tag, F4-050 | gate (c) | AskUserQuestion | yes | procedure |
| F4-037 | Row 3: the chosen path moves a published contract surface beyond what this unit's ticket states, or is breaking for existing consumers → scope-bounding gate (c). | ordering | L636-L637, (a) Step 2 table | gate (c) fire | chosen path, ticket body | gate (c) | AskUserQuestion | yes | procedure |
| F4-038 | Row 4: the chosen path is narrower than the smallest internally-consistent complete fix (leaves the stated defect partly unfixed) → scope-bounding gate (c). | ordering | L638-L639, (a) Step 2 table | gate (c) fire | chosen path | gate (c) | AskUserQuestion | yes | procedure |
| F4-039 | Row 5: the chosen path's depth tag is `re-architect` → routing-decision gate (d). | ordering | L640, (a) Step 2 table | gate (d) fire | depth tag | gate (d) | AskUserQuestion | yes | procedure |
| F4-040 | Row 6: otherwise → dispatch the chosen path, no gate. | ordering | L641, (a) Step 2 table | implementer dispatch | chosen path | - | Agent | yes | procedure |
| F4-041 | Row 6 dispatches a fresh ephemeral implementer Agent (Engineer / Test Writer / Doc Writer per the finding's lane) per Section 4's dispatch shape with the chosen fix path and no user gate. | command | L644, (a) | Agent dispatch | chosen path, lane | Section 4 | Agent, TaskList | no | procedure |
| F4-042 | Row 6 appends a compromise-tracker entry per Section 7.5's **Trigger C**. | relay | L644, (a) | tracker entry | row 6 dispatch | Section 7.5, **Trigger C** | none | no | procedure |
| F4-043 | Rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of depth tag; row 1 comes first so parts (e) and (f) stay reachable. | rationale-only | L644, (a) | - | - | parts (e), (f) | none | yes | rationale |
| F4-044 | Whatever row fires, when the chosen path changes source the re-dispatch follows part (g)'s ordering: Engineer, then the code review for that site, then the affected writer. | ordering | L644, (a) | dispatch sequence | chosen path | part (g) | Agent | yes | procedure |
| F4-045 | "Highest-quality" = the smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names. | definition | L646, **What "highest-quality" means.** | - | ticket body | - | none | yes | procedure |
| F4-046 | Total-system complexity counts against a path. | invariant | L646, **What "highest-quality" means.** | - | - | - | none | yes | procedure |
| F4-047 | Effort is never the tiebreaker between paths of equal completeness. | invariant | L646, **What "highest-quality" means.** | - | - | - | none | yes | procedure |
| F4-048 | "Adds a mechanism" is a reason to route to gate (c), not a reason to build. | invariant | L646, **What "highest-quality" means.** | - | - | gate (c) | none | yes | procedure |
| F4-049 | For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently". | definition | L646, **What "highest-quality" means.** | - | - | - | none | yes | procedure |
| F4-050 | "Introduces a mechanism" = adds machinery per `agents/analyst.md`'s mechanism definition that the approved design (the `## Authoritative design directive` block from Section 3's Analyst gate) did not enumerate. | definition | L648, **What "introduces a mechanism" means.** | - | `## Authoritative design directive`, `agents/analyst.md` | `agents/analyst.md`, Section 3 | none | no | procedure |
| F4-051 | The reviewer's `[introduces-mechanism]` tag is the primary signal for row 2: a tagged path routes to gate (c) with no further judgment. | invariant | L648, **What "introduces a mechanism" means.** | gate (c) fire | `[introduces-mechanism]` tag | row 2 | none | yes | procedure |
| F4-052 | Orchestrator-side mechanism detection is the fallback, used only when no tag is present: read the path's own description against the definition and route the same way. | invariant | L648, **What "introduces a mechanism" means.** | gate (c) fire | fix path description, F4-050 | - | none | yes | procedure |
| F4-053 | MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent (R2/R3 rounds). | invariant | L650, (b) | - | dispatch prompt | - | Agent | yes | procedure |
| F4-054 | Forbidden dispatch-prompt phrasings (and close paraphrases): `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. | definition | L650, (b) | - | dispatch prompt | - | none | yes | procedure |
| F4-055 | Inlining a scope-bound silently narrows the fix without the user ever seeing the decision. | rationale-only | L650, (b) | - | - | - | none | yes | rationale |
| F4-056 | When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through the scope-bounding gate in part (c). | command | L650, (b) | gate (c) fire | - | part (c) | AskUserQuestion | yes | procedure |
| F4-057 | The prohibition targets narrowing language, not path selection: a dispatch prompt naming the part-(a) chosen path and carrying its fix in full is not a violation. | invariant | L652, (b) | - | chosen path | part (a) | none | yes | procedure |
| F4-058 | Instructing the implementer to do less than the chosen path is a violation of part (b). | invariant | L652, (b) | - | dispatch prompt | - | none | yes | procedure |
| F4-059 | A path narrower than the smallest internally-consistent complete fix is never written into a prompt at all; it routes to gate (c) via row 4. | invariant | L652, (b) | gate (c) fire | chosen path | row 4 | none | yes | procedure |
| F4-060 | Gate (c) has four entry conditions: the would-otherwise-scope-bound case (replacing part (b)'s forbidden directives), and rows 2, 3, and 4 of part (a). | definition | L654, (c) | - | F4-056, F4-036–F4-038 | part (b), part (a) | none | yes | procedure |
| F4-061 | Downstream, the part-(b) scope-bound condition is read as row 4; every rule enumerating "row 2, 3, or 4" covers it without naming it. | definition | L654, (c) | - | - | part (b), row 4 | none | yes | procedure |
| F4-062 | On any of the four entry conditions, fire an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract with the finite choices below, filtered by the severity paragraph. | gate | L654, (c) | gate task + question | finding severity | 2SGM | TaskList, AskUserQuestion | yes | procedure |
| F4-063 | Severity rules the choice set: a `blocker` can never be accepted, and can be deferred only with a narrowing. | invariant | L656, (c) | - | severity tag | - | none | unknown | procedure |
| F4-064 | For a `blocker` at gate (c), `Accept the limitation` is unreachable unconditionally: do not offer it, do not mark it Recommended, do not route to it by any other path. | choice-set | L658, (c) | - | severity tag | - | AskUserQuestion | unknown | procedure |
| F4-065 | A `blocker` at gate (c) is always offered the base pair `Fix properly now` and `Re-dispatch the Analyst with this finding`; when the two Defer conditions do not both hold, they are the whole set. | choice-set | L659, (c) | choice set | severity tag | - | AskUserQuestion | no | procedure |
| F4-066 | Blocker `Fix properly now` behaves as the `suggestion`/`nit` `Fix properly now` bullet ("as below"). | choice-set | L661, (c) | - | F4-092 | - | AskUserQuestion | unknown | procedure |
| F4-067 | `Re-dispatch the Analyst with this finding` is for a `blocker` showing the approved design directive itself is wrong, not the implementation of it. | definition | L662, (c) | - | finding | Section 3 | none | no | procedure |
| F4-068 | Analyst re-dispatch reuses Section 3's Revise-branch shape: mark the prior Analyst task `completed`, issue a fresh cold `subagent_type=analyst` dispatch tracked as `analyst-<issue-id>-rev<n>`, carrying the finding verbatim as revision context. | command | L662, (c) | Analyst dispatch, `analyst-<issue-id>-rev<n>` task | finding text | Section 3 Revise branch, `agents/analyst.md` | Agent, TaskList | no | procedure |
| F4-069 | When the re-dispatched Analyst returns, Section 3's Approve / Revise / Cancel approval gate re-fires over the new proposal, exactly as on the Revise branch. | gate | L662, (c) | Section 3 approval gate | Analyst result | Section 3 | TaskList, AskUserQuestion | no | procedure |
| F4-070 | On `Approve`, re-enter Section 4 Phase A with the revised directive, but close out this Issue's open TaskList tasks first. | ordering | L662, (c) | Phase A re-entry | `Approve` answer | Section 4 Phase A | TaskList | no | procedure |
| F4-071 | Close-out sweep: by prefix, mark `completed` every active `test-writer-<issue-id>` / `doc-writer-<issue-id>` / `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` task and their `-r<n>` rounds — whichever are actually active (may be none on a Phase A finding). | command | L662, (c) | task status flips | TaskList | Section 4 Engineer-dispatch precondition | TaskList | no | procedure |
| F4-072 | The sweep is needed because Section 4's Engineer-dispatch precondition forbids a fresh Engineer while any of those tasks is `pending` or `in_progress`, and this gate can fire from a review phase where several are. | rationale-only | L662, (c) | - | - | Section 4 | none | no | rationale |
| F4-073 | A lane still in flight when the sweep fires is marked `completed` anyway (the orchestrator cannot terminate a dispatched background Agent) with `metadata.activity` recording it was in flight at the Analyst re-dispatch. | command | L662, (c) | task status flip, `metadata.activity` | in-flight Agent | - | TaskList | no | procedure |
| F4-074 | When an in-flight lane's completion notification arrives after the sweep, discard its findings rather than routing them. | invariant | L662, (c) | - | Agent completion | - | Agent | no | procedure |
| F4-075 | The discard covers every finding raised under the superseded directive: sibling findings co-emitted with the gate-firing return, and any lane that returned between the gate answer and the sweep. | invariant | L662, (c) | - | reviewer returns | - | none | no | procedure |
| F4-076 | Route none of the superseded findings; the revised directive is what the next round reviews against. | invariant | L662, (c) | - | revised directive | - | none | no | procedure |
| F4-077 | The new Engineer works against the current working tree: landed edits stay in it uncommitted, and the revised directive is applied on top rather than to a clean base. | invariant | L662, (c) | Engineer dispatch | working tree | - | Agent, git | no | procedure |
| F4-078 | `Defer to follow-up Issue` is added as a third choice for a `blocker` only when both hold: (i) the needed fix path introduces a mechanism (`[introduces-mechanism]` tag or orchestrator reading against `agents/analyst.md`), and (ii) that mechanism serves a case outside this unit's stated defect. | choice-set | L664, (c) | choice set | fix path, `[introduces-mechanism]`, F4-050 | `agents/analyst.md` | AskUserQuestion | unknown | procedure |
| F4-079 | Condition (ii) means the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships. | definition | L664, (c) | - | - | - | none | unknown | procedure |
| F4-080 | A narrowing may never reduce coverage of the stated defect. | invariant | L664, (c) | - | narrowing | - | none | unknown | procedure |
| F4-081 | A `blocker` that cannot be made inapplicable to what ships without leaving the stated defect partly unfixed is in scope: it takes one of the base pair, never `Defer`. | invariant | L664, (c) | - | F4-078 | - | AskUserQuestion | unknown | procedure |
| F4-082 | The blocker deferral is paired with the narrowing, never shipped alone. | invariant | L664, (c) | narrowing dispatch | `Defer` answer | - | Agent | unknown | procedure |
| F4-083 | File the follow-up Issue first, carrying the reviewer's sketched design verbatim, and dispatch the narrowing only once `/quo-file-issue` has returned an Issue ID. | ordering | L664, (c) | follow-up Issue, narrowing dispatch | reviewer's sketched design | `/quo-file-issue`, part (f) | bees, Agent | unknown | procedure |
| F4-084 | Part (f) forbids shipping the narrowing when the filing failed; Trigger A writes its tracker entry in that same window. | relay | L664, (c) | tracker entry (Trigger A) | `/quo-file-issue` result | part (f), Trigger A | none | unknown | procedure |
| F4-085 | Dispatch the blocker narrowing directly, not by re-entering Step 2 with it (it would match row 4 and loop back to this gate). | invariant | L664, (c) | narrowing dispatch | narrowing | row 4 | Agent | unknown | procedure |
| F4-086 | The direct-dispatch terminality is one rule with the `Defer to follow-up Issue` bullet's soft-fix rule, applied to a blocker's narrowing and a non-blocker's soft fix. | definition | L664, (c) | - | - | F4-095 | none | unknown | procedure |
| F4-087 | When the Defer-with-narrowing branch is open, it is the recommended default: mark the choice `(Recommended)` even on a `blocker`. | choice-set | L664, (c) | `(Recommended)` marker | F4-078 | **Recommended default on the mechanism row.** | AskUserQuestion | unknown | procedure |
| F4-088 | The blocker Defer branch applies whichever row fired the gate — 2, 3, or 4 — because condition (i) tests the fix path the finding needs, not the chosen path. | invariant | L664, (c) | - | fix path the finding needs | rows 2–4 | none | unknown | procedure |
| F4-089 | A `suggestion` or `nit` keeps the narrower rule: its Defer default is row-2 only. | choice-set | L664, (c) | - | severity, row | **Recommended default on the mechanism row.** | AskUserQuestion | unknown | procedure |
| F4-090 | The gate fires for a `blocker` like any other finding: the base pair is a real decision, three choices when the Defer-with-narrowing branch is open. | gate | L666, (c) | gate fire | severity | - | AskUserQuestion | unknown | procedure |
| F4-091 | Neither of the `Defer to follow-up Issue` bullet's closing clauses applies to a blocker: its no-fix-this-round branch cannot arise, and its never-invent-a-narrowing prohibition concerns a non-blocker's empty soft-fix slot. | invariant | L666, (c) | - | - | F4-096, F4-097 | none | unknown | procedure |
| F4-092 | The Defer bullet's soft-fix identification does not apply to a blocker: what ships is the narrowing, not the most complete remaining enumerated path. | invariant | L666, (c) | - | - | F4-094 | none | unknown | procedure |
| F4-093 | The three bulleted choices (`Fix properly now`, `Defer to follow-up Issue`, `Accept the limitation`) are the choice set for `suggestion`- and `nit`-severity findings. | choice-set | L666, (c) | choice set | severity | - | AskUserQuestion | yes | procedure |
| F4-094 | Section 7.5's **Trigger B** is unreachable for `blocker` findings; no tracker entry can record an accepted blocker. | invariant | L666, (c) | - | - | Section 7.5, **Trigger B** | none | no | procedure |
| F4-095 | **Trigger A** is reachable for a `blocker` on the Defer-with-narrowing branch here and on part (d)'s Defer branch; its entry must carry the narrowing record. | invariant | L666, (c) | tracker entry (Trigger A) with narrowing record | `Defer` answer | Trigger A, part (d) | none | unknown | procedure |
| F4-096 | `Fix properly now`: re-dispatch the appropriate implementer Agent per Section 4's dispatch shape to address the finding fully, no scope-bound. | choice-set | L668, (c) | implementer dispatch | finding | Section 4 | Agent, TaskList | no | procedure |
| F4-097 | `Defer to follow-up Issue`: file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool, per Section 1's URL-resolution sub-step precedent) carrying the finding's description, and proceed with the soft fix this round. | choice-set | L669, (c) | follow-up Issue, soft-fix dispatch | finding description | `/quo-file-issue`, Section 1 | bees, Agent | no | procedure |
| F4-098 | The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside. | definition | L669, (c) | soft fix | enumerated fix paths | - | none | yes | procedure |
| F4-099 | Dispatch the soft fix directly, not by re-entering Step 2 (a remaining path is narrower than the deferred one, so row 4 would loop it back). | invariant | L669, (c) | soft-fix dispatch | F4-098 | row 4 | Agent | yes | procedure |
| F4-100 | When the deferred path was the only one enumerated, ship no fix for this finding this round (same end state as `Accept the limitation`, with the follow-up Issue filed). | recovery | L669, (c) | - | fix-path count | - | none | yes | procedure |
| F4-101 | Never invent a narrowing to fill the soft-fix slot; part (b) forbids it. | invariant | L669, (c) | - | - | part (b) | none | yes | procedure |
| F4-102 | `Accept the limitation`: record the limitation as an accepted compromise and proceed, via the session-scoped compromise tracker (`#### Session-scoped compromise tracker` block in Section 7.5). | choice-set | L670, (c) | tracker entry | finding | `#### Session-scoped compromise tracker`, Section 7.5 | none | no | procedure |
| F4-103 | Gate (c)'s question text includes the finding verbatim plus a one-line context line stating which of the four entry conditions brought it here. | field-or-template | L672, (c) | question text | finding, entry condition | - | AskUserQuestion | yes | procedure |
| F4-104 | There is no `Cancel` option at gate (c); the user retains `Ctrl-C` for run-level abort. | choice-set | L672, (c) | - | - | - | AskUserQuestion | no | procedure |
| F4-105 | Scope-bounding is a per-finding decision, so a `Cancel` at gate (c) would be ambiguous. | rationale-only | L672, (c) | - | - | - | none | no | rationale |
| F4-106 | When gate (c) fires on row 2 (mechanism serving a case the ticket never mentions), `Defer to follow-up Issue` is the recommended default: mark it `(Recommended)`. | choice-set | L674, **Recommended default on the mechanism row.** | `(Recommended)` marker | row 2 fire | - | AskUserQuestion | yes | procedure |
| F4-107 | The row-2 recommended default holds at every severity: `suggestion`/`nit` ships the soft fix; a `blocker` ships the narrowing, but only where the Defer-with-narrowing branch is open. | invariant | L674, **Recommended default on the mechanism row.** | - | severity | F4-078 | AskUserQuestion | unknown | procedure |
| F4-108 | When the coverage guard withholds `Defer` (narrowing would leave the stated defect partly unfixed), there is no choice to mark, even on a row-2 fire. | invariant | L674, **Recommended default on the mechanism row.** | - | F4-080 | - | AskUserQuestion | unknown | procedure |
| F4-109 | A mechanism the ticket never asked for has its own lifecycle to design; building it inside this unit turns one finding into several rounds. | rationale-only | L674, **Recommended default on the mechanism row.** | - | - | - | none | yes | rationale |
| F4-110 | The follow-up Issue MUST carry the reviewer's sketched design verbatim so nothing about the proposed mechanism is lost by deferring. | field-or-template | L674, **Recommended default on the mechanism row.** | follow-up Issue body | reviewer's sketched design | `/quo-file-issue` | bees | yes | procedure |
| F4-111 | Gate (d) fires when Step 2 routes a finding via row 1 or row 5 (depth unknown/malformed, or chosen path `re-architect`): fire `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L676, (d) | gate task + question | rows 1, 5 | 2SGM | TaskList, AskUserQuestion | yes | procedure |
| F4-112 | For a `blocker` at gate (d), `Defer to follow-up Issue` is unreachable unless part (c)'s two conditions both hold (needed path introduces a mechanism serving a case outside the stated defect). | choice-set | L678, (d) | - | F4-078 | part (c) | AskUserQuestion | unknown | procedure |
| F4-113 | At gate (d) too, a narrowing may never reduce coverage of the stated defect; such a blocker is in scope and takes one of the other choices rather than `Defer`. | invariant | L678, (d) | - | narrowing | - | AskUserQuestion | unknown | procedure |
| F4-114 | When the conditions hold at gate (d), offer `Defer` on part (c)'s terms: paired with the narrowing in the same round, `(Recommended)`, follow-up Issue carrying the sketched design verbatim. | choice-set | L678, (d) | `Defer` choice, follow-up Issue, narrowing dispatch | F4-078 | part (c) | AskUserQuestion, bees, Agent | unknown | procedure |
| F4-115 | Blocker-Defer `(Recommended)` takes precedence over the per-path marker: mark `Defer to follow-up Issue` Recommended and withhold the marker from every other choice (each Step-1 path marker and `Re-dispatch the Analyst with this finding`), so exactly one choice carries it. | choice-set | L678, (d) | `(Recommended)` marker | F4-114 | part (c) | AskUserQuestion | no | procedure |
| F4-116 | A zero-path row-1 blocker whose Defer branch is open shows `(Recommended)` on `Defer` alone. | example | L678, (d) | - | - | - | AskUserQuestion | unknown | example |
| F4-117 | When part (c)'s conditions do not hold for a blocker at gate (d), do not offer `Defer`, do not mark it Recommended, and do not route to it by any other path. | choice-set | L678, (d) | - | F4-078 | - | AskUserQuestion | unknown | procedure |
| F4-118 | When `Defer` is offered to a blocker at gate (d), the deferral is paired with a narrowing dispatched this round, never shipped alone; the bullet's "rather than picking a path now" describes only the non-blocker case. | invariant | L678, (d) | narrowing dispatch | `Defer` answer | F4-124 | Agent | unknown | procedure |
| F4-119 | The choice set for a non-deferrable `blocker` at gate (d) is the one-choice-per-fix-path list (which may be empty) plus `Re-dispatch the Analyst with this finding` plus `Cancel`. | choice-set | L678, (d) | choice set | fix paths | - | AskUserQuestion | no | procedure |
| F4-120 | A row-1 blocker with no fix path enumerated: mark `Re-dispatch the Analyst with this finding` `(Recommended)` (unless the Defer branch is open — see F4-115). | choice-set | L678, (d) | `(Recommended)` marker | fix-path count | - | AskUserQuestion | no | procedure |
| F4-121 | Gate (d)'s `Re-dispatch the Analyst with this finding` is the same choice part (c) defines: Section 3's Revise-branch shape, fresh cold `subagent_type=analyst` tracked as `analyst-<issue-id>-rev<n>`, finding carried verbatim, Section 3's approval gate re-fires. | definition | L678, (d) | Analyst dispatch | finding | Section 3, part (c) | Agent, TaskList | no | procedure |
| F4-122 | No `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing. | invariant | L678, (d) | - | - | parts (c), (d) | none | unknown | procedure |
| F4-123 | The tracker's `Decision` value `User picked Accept the limitation` can never describe a `blocker`; `User picked Defer to follow-up Issue` describes one only when the entry's `Rationale` carries Trigger A's narrowing record. | invariant | L678, (d) | - | tracker `Decision`, `Rationale` fields | Trigger A, compromise tracker | none | unknown | procedure |
| F4-124 | Gate (d) offers one choice per reviewer-surfaced fix path; each choice's description includes that path's depth tag (e.g., `re-architect`, `refactor-locally`). | choice-set | L680, (d) | choice set | fix paths, depth tags | - | AskUserQuestion | yes | procedure |
| F4-125 | The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1. | choice-set | L680, (d) | `(Recommended)` marker | Step 1 pick | part (a) Step 1 | AskUserQuestion | yes | procedure |
| F4-126 | Gate (d) asks the user to ratify or override a pick that has already been made, so the marker must name that pick. | rationale-only | L680, (d) | - | - | - | none | yes | rationale |
| F4-127 | When `[preferred]` marks a narrowing and a fuller path is the smallest internally-consistent complete change, mark the fuller path Recommended and state in its description that the reviewer preferred the other path. | choice-set | L680, (d) | choice description | `[preferred]` token, Step 1 pick | - | AskUserQuestion | yes | procedure |
| F4-128 | Fallback: on a row-1 entry (no or malformed depth tag) no Step-1 pick was possible, so no path is marked Recommended. | choice-set | L680, (d) | - | row 1 | - | AskUserQuestion | yes | procedure |
| F4-129 | `Defer to follow-up Issue` (gate d): file a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now. | choice-set | L681, (d) | follow-up Issue | finding description | `/quo-file-issue` | bees | yes | procedure |
| F4-130 | `Cancel` (gate d): ends work on the current Issue without a fix landing. | choice-set | L682, (d) | - | - | - | AskUserQuestion | no | procedure |
| F4-131 | `Cancel` routes through `#### Aborted-Issue close-out` (Section 7): sweep this Issue's TaskList tasks by prefix, run Section 7.5's deferral-hygiene gate, run the Issue-boundary state-externalization checkpoint on its aborted path, then read the working tree and branch on mode. | ordering | L682, (d) | close-out sequence | `Cancel` answer | `#### Aborted-Issue close-out`, Section 7, Section 7.5 | TaskList, git | no | procedure |
| F4-132 | `Cancel` does not decide the run's fate; the close-out's mode branch does, and in batch mode with Issues remaining it stops the run because this Issue's edits are left uncommitted. | invariant | L682, (d) | - | run mode, working tree | `#### Aborted-Issue close-out` | git | no | procedure |
| F4-133 | `Ctrl-C` remains the unconditional run-level abort. | definition | L682, (d) | - | - | - | none | yes | procedure |
| F4-134 | Gate (d)'s question text includes the finding verbatim. | field-or-template | L684, (d) | question text | finding | - | AskUserQuestion | yes | procedure |
| F4-135 | A finding emitted without a depth tag (legacy reviewer emission, or hand-authored from a future call site) MUST be treated as `re-architect` depth and routed to gate (d). | invariant | L686, (e) | gate (d) fire | depth tag absence | part (d), row 1 | AskUserQuestion | yes | procedure |
| F4-136 | When the orchestrator cannot determine a finding's depth, surface the decision to the user rather than dispatching its own pick ungated under row 6. | invariant | L686, (e) | gate (d) fire | depth tag | row 6 | AskUserQuestion | yes | procedure |
| F4-137 | A PM emission that `agents/pm.md`'s tracker-check bullet designates a report note (not a finding) is exempt from the shim and from part (f)'s malformed-tag bullet; that bullet defines the shape. | invariant | L686, (e) | - | PM emission | `agents/pm.md`, part (f) | none | yes | procedure |
| F4-138 | Malformed tags: when a severity tag is not exactly `blocker` / `suggestion` / `nit`, or a depth tag not exactly `trivial-tweak` / `refactor-locally` / `re-architect`, treat the finding as `re-architect` depth (per part (e)) AND surface the parse failure to the user. | recovery | L690, (f) | gate (d) fire, user-facing parse-failure report | severity/depth tags | part (e) | AskUserQuestion | yes | procedure |
| F4-139 | Routing ambiguity: if the routing table returns more than one decision (impossible by construction), default to gate (d) and surface the ambiguity to the user. | recovery | L691, (f) | gate (d) fire | routing decisions | part (d) | AskUserQuestion | yes | procedure |
| F4-140 | When the user picks `Defer to follow-up Issue` at either gate but the inline `/quo-file-issue` dispatch fails or the user cancels at one of its gates, MUST NOT silently ship the soft fix (or no fix). | recovery | L692, (f) | - | `/quo-file-issue` result | parts (c), (d), `/quo-file-issue` | bees | yes | procedure |
| F4-141 | On a filing failure, surface it and re-prompt with the same gate's choices so the user can re-attempt the defer, pick `Accept the limitation` where it exists (non-`blocker` only), pick a specific fix path explicitly, or (at gate (d)) `Cancel`. | recovery | L692, (f) | re-fired gate | F4-140 | parts (c), (d) | TaskList, AskUserQuestion | unknown | procedure |
| F4-142 | A `blocker` can reach the filing-failure bullet via the Defer-with-narrowing branch; do not ship the narrowing when the filing failed — re-prompt with the same gate's choices. | recovery | L692, (f) | re-fired gate | `/quo-file-issue` result | F4-078 | AskUserQuestion | unknown | procedure |
| F4-143 | Routing is settled by the orchestrator's own pick per part (a) or the user's pick at gate (c) or (d); the orchestrator then still decides how many lanes to dispatch at once. | definition | L694, (g) | - | routing decision | parts (a), (c), (d) | none | yes | procedure |
| F4-144 | When the chosen fix path requires a source change, dispatch the Engineer first, then the Code Reviewer against the resulting diff, and only once that code review has closed dispatch the Test Writer and/or Doc Writer whose input the change invalidated — ordered, not concurrent. | ordering | L694, (g) | dispatch sequence | chosen path | - | Agent, TaskList | yes | procedure |
| F4-145 | Dispatching the Engineer and a writer in the same round hands the writer a diff the pending code review is about to rewrite, forcing the writer's work to be redone. | rationale-only | L694, (g) | - | - | - | none | yes | rationale |
| F4-146 | One elision: when the Engineer round is the final `trivial-tweak` nit pass **Severity bounds the loop** describes, skip the code-review rung and dispatch the affected writer once that Engineer returns; every other source-changing round keeps the rung. | ordering | L694, (g) | dispatch sequence | F4-013 | **Severity bounds the loop** | Agent | yes | procedure |
| F4-147 | Engineer-dispatch precondition: MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, or `analyst-<issue-id>` is `pending` or `in_progress`. | precondition | L696, (g) | - | TaskList | Section 4 Reconcile step | TaskList, Agent | no | procedure |
| F4-148 | Walk the TaskList before every Engineer dispatch, including every re-dispatch routed from this section, and confirm no task matching those prefixes is active. | command | L696, (g) | - | TaskList | Section 4 | TaskList | yes | procedure |
| F4-149 | Section 4 is authoritative for three qualifications not restated here: the prefix-match rule (catching `engineer-<issue-id>-r<n>`), the Code Reviewer's deliberate exclusion from the list, and handling a `pending` task with no Agent behind it. | definition | L696, (g) | - | - | Section 4 | none | no | procedure |
| F4-150 | A finding whose chosen fix path changes no source file (test-quality nit, doc-wording gap) carries no ordering constraint: re-dispatch that single writer lane alone, no Engineer round, no code review. | ordering | L698, (g) | writer dispatch | chosen path | - | Agent | yes | procedure |
| F4-151 | Both gates (c) and (d) fire through the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L700, 2SGM | - | - | parts (c), (d) | TaskList, AskUserQuestion | yes | procedure |
| F4-152 | First create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate, with a distinct per-fire `<short-suffix>` so concurrent or repeated fires do not collide (per Section 4 / Section 3 naming convention's gate-task entry). | name-class | L700, 2SGM | `gate-askuserquestion-<short-suffix>` task | - | Section 4 / Section 3 TaskList naming convention | TaskList | yes | procedure |
| F4-153 | Then call `AskUserQuestion` with the finite choices above in the same turn. | gate | L700, 2SGM | question | F4-152 | - | AskUserQuestion | yes | procedure |
| F4-154 | Do not produce a text response describing the gate; fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L700, 2SGM | - | - | - | TaskList, AskUserQuestion | yes | procedure |
| F4-155 | Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. | command | L700, 2SGM | task status flip | gate answer | - | TaskList | yes | procedure |
| F4-156 | These gates are multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot. | invariant | L700, 2SGM | - | - | - | AskUserQuestion | yes | procedure |
| F4-157 | These gates inherit a prose-adherence fragility — an execution-time risk acknowledged at run time, not something this section fixes. | rationale-only | L702, ODR closing | - | - | - | none | yes | rationale |

## Anchors defined here

Headings and bolded phrases (verbatim), one per line with line number.

- L618 `### Orchestrator discipline: routing review findings`
- L620 **enumerated fix paths and their depth tags**
- L620 **deterministically for whether a gate fires**
- L620 **by its own judgment for which path it picks when no gate fires**
- L622 **Severity bounds the loop.**
- L622 **no fix lands against it**
- L622 **A `nit` whose chosen path is a `trivial-tweak` never reopens a lane on its own.**
- L622 **one** (final implementer pass)
- L622 **no** (further reviewer round)
- L622 **Reviews** (summary line)
- L622 **the bound keys on what ships**
- L624 **(a) Pick the path, then route on it.**
- L626 **Step 1 — pick.**
- L626 **input**
- L626 **The pick is always one of the paths the reviewer enumerated.**
- L626 **in session**
- L626 **durable**
- L628 **Step 2 — route on the path chosen in Step 1.**
- L628 **in order**
- L644 **Trigger C**
- L644 **regardless of its depth tag**
- L644 **when the chosen path changes source the re-dispatch follows part (g)'s ordering**
- L646 **What "highest-quality" means.**
- L646 **smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names**
- L648 **What "introduces a mechanism" means.**
- L648 **the approved design for this unit did not enumerate**
- L648 **The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2**
- L648 **fallback**
- L650 **(b) ANTI-PATTERN — do not write this:**
- L652 **The prohibition targets *narrowing* language, not path selection.**
- L652 **is** / **in full**
- L654 **(c) Scope-bounding gate.**
- L654 **four**
- L654 **Downstream, the part-(b) scope-bound condition is read as row 4**
- L656 **Severity rules the choice set — a `blocker` can never be accepted, and can be deferred only with a narrowing.**
- L658 **`Accept the limitation` is unreachable, unconditionally**
- L659 **The base pair is always offered.**
- L659 **both**
- L661 **Fix properly now** (blocker bullet)
- L662 **Re-dispatch the Analyst with this finding**
- L662 **approved design directive itself is wrong**
- L662 **verbatim**
- L662 **On `Approve`, re-enter Section 4 Phase A with the revised directive — but close out this Issue's open TaskList tasks first**
- L662 **in flight**
- L662 **discard its findings rather than routing them**
- L662 **That discard covers every finding raised under the superseded directive, not only the lanes this sweep caught in flight**
- L662 **against the current working tree**
- L664 **`Defer to follow-up Issue` is added as a third choice *only when both* of these hold:**
- L664 **introduces a mechanism**
- L664 **and**
- L664 **outside this unit's stated defect**
- L664 **narrowed to the stated defect**
- L664 **A narrowing may never reduce coverage of the stated defect.**
- L664 **in scope**
- L664 **the deferral is paired with the narrowing, never shipped alone**
- L664 **file the follow-up Issue first**
- L664 **Dispatch that narrowing directly, not by re-entering Step 2 with it**
- L664 **recommended default**
- L664 **Recommended default on the mechanism row.** (cross-reference to L674)
- L664 **It applies whichever row fired this gate on a blocker — 2, 3 or 4.**
- L666 **Neither of the `Defer to follow-up Issue` bullet's closing clauses applies to one:**
- L666 **Trigger B**
- L666 **Trigger A is reachable for one**
- L668 **Fix properly now**
- L669 **Defer to follow-up Issue**
- L669 **The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside**
- L669 **directly**
- L670 **Accept the limitation**
- L672 **There is no `Cancel` option at this gate**
- L674 **Recommended default on the mechanism row.**
- L674 **introduces a mechanism**
- L674 **recommended default**
- L674 **at every severity**
- L674 **verbatim**
- L676 **(d) Routing-decision gate.**
- L678 **Severity rules the choice set here too — a `blocker`'s Defer route is conditional.**
- L678 **unreachable unless part (c)'s two conditions both hold**
- L678 **A narrowing may never reduce coverage of the stated defect**
- L678 **paired with the narrowing in the same round**
- L678 **That `(Recommended)` takes precedence over the per-path marker**
- L678 **every other choice**
- L678 **When it is offered to a blocker here, the deferral is paired with a narrowing dispatched this round, never shipped alone**
- L678 **which may be empty**
- L678 **Re-dispatch the Analyst with this finding**
- L678 **verbatim**
- L678 **Cancel**
- L678 **no `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing**
- L680 **One choice per reviewer-surfaced fix path**
- L680 **The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1**
- L680 **input**
- L680 **fuller**
- L680 **Fallback:**
- L681 **Defer to follow-up Issue**
- L682 **Cancel**
- L682 **not** (does **not** decide the run's fate)
- L682 **stops the run**
- L686 **(e) Backwards-compatibility shim.**
- L686 **without a depth tag**
- L686 **One emission is out of the shim's reach:**
- L688 **(f) Edge-case handling.**
- L690 **Malformed tags.**
- L691 **Routing ambiguity.**
- L692 **`/quo-file-issue` failure at the Defer gate.**
- L692 **A `blocker` can reach this bullet**
- L692 **do not ship the narrowing when the filing failed**
- L694 **(g) Re-dispatch ordering when a fix path changes source.**
- L694 **the orchestrator's own path pick per part (a), or the user's pick at the gate in part (c) or (d)**
- L694 **source change**
- L694 **ordered, not concurrent**
- L694 **Engineer** / **Code Reviewer** / **Test Writer** / **Doc Writer**
- L694 **One elision:**
- L694 **Severity bounds the loop** (back-reference to L622)
- L696 **Engineer-dispatch precondition**
- L696 **the orchestrator MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`, or `analyst-<issue-id>` is `pending` or `in_progress`.**
- L696 **prefix**
- L698 **no source file**
- L700 **Two-step gate mechanics (parts (c) and (d)).**
- L700 **First** / **then**

Anchors count: 118 lines above (counting slash-grouped bold pairs as one line each).

## Rationale-only spans

Whole lines that carry no rule:

- L702–L702 (1 line): gates inherit prose-adherence fragility.

Partial-line rationale (each paragraph is one physical line, so these are sentence spans inside a rule-bearing line; listed so a rewrite can drop them without losing a rule):

- L622, final two sentences: severity orthogonal to depth; coverage given up is bounded.
- L626, "Either way the incomplete menu becomes visible **in session** … the user sees the menu it fired on.": under-enumeration surfaces in session.
- L644, "The evaluation order is load-bearing: …": why rows 2–4 precede 5.
- L650, "Inlining a scope-bound silently narrows …": why inlined scope-bounds are forbidden.
- L662, "because Section 4's Engineer-dispatch precondition forbids … may be none.": why the close-out sweep exists.
- L664, "This is the same terminality … for the same reason": narrowing and soft fix share terminality.
- L672, "scope-bounding is a per-finding decision and a `Cancel` here would be ambiguous": why no Cancel at (c).
- L674, "A mechanism the ticket never asked for … several rounds.": why defer mechanisms by default.
- L680, "this gate asks the user to ratify or override a pick that has already been made": why Recommended names the pick.
- L686, "The shim errs toward user input when uncertain": why untagged goes to gate (d).
- L694, "Dispatching the Engineer and a writer in the same round … redone.": why ordered not concurrent.

Rationale-span total: 1 whole line (L702) plus 11 partial-line sentence spans.
