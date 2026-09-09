# Rule inventory — `quo-fix-issue/SKILL.md` L248–L367 (Sections 2 and 3)

Source: `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md`, lines 248–367 (`### 2. Validate Issue` through `#### Anti-pattern: do not classify the body upfront`). Extracted verbatim-anchored; nothing summarized.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F2-001 | Run `bees show-ticket --ids "<issue-id>"` to load the Issue before validating it. | command | L250-L252, `### 2. Validate Issue` | ticket JSON (body, `up_dependencies`, status) | `<issue-id>` from Section 1 argument parsing | - | Bash, bees | unknown | procedure |
| F2-002 | Check the Issue has a status meaning ready to begin work — `open`. | precondition | L254-L255, `### 2. Validate Issue` | - | ticket `ticket_status` from F2-001 | - | bees | unknown | procedure |
| F2-003 | Check the `up_dependencies` array for blockers; every blocker must be in a completed state. | precondition | L256, `### 2. Validate Issue` | - | `up_dependencies` field from F2-001 | - | bees | unknown | procedure |
| F2-004 | `up_dependencies` is returned as a list of ticket IDs only — not statuses. | definition | L258, `### 2. Validate Issue` | - | `up_dependencies` field | - | bees | unknown | procedure |
| F2-005 | Collect the dependency IDs and batch-look-up their statuses with `bees show-ticket --ids <dep-id-1> <dep-id-2> <...>`. | command | L258-L263, `### 2. Validate Issue` | dependency ticket JSON | `up_dependencies` IDs | - | Bash, bees | unknown | procedure |
| F2-006 | For each up_dependency, check the returned `ticket_status`; the Issue is unblocked only if all `up_dependencies` are `done`. | precondition | L265, `### 2. Validate Issue` | blocked / unblocked determination | `ticket_status` from F2-005 | - | bees | unknown | procedure |
| F2-007 | An Issue with no `up_dependencies` is unblocked by default. | precondition | L265, `### 2. Validate Issue` | unblocked determination | `up_dependencies` (empty) | - | none | unknown | procedure |
| F2-008 | If blocked, output the blocking IDs and titles. | relay | L267-L268, `### 2. Validate Issue` | user-visible message | F2-006 result, dependency titles | - | none | unknown | procedure |
| F2-009 | If blocked in batch mode (`all` or list mode), skip this Issue and continue to the next one. | recovery | L269, `### 2. Validate Issue` | skip; advance batch | run mode from Section 1; F2-006 | - | none | unknown | procedure |
| F2-010 | If blocked in single mode, exit with message `Cannot start Issue. It is blocked by: [list]`. | recovery | L270, `### 2. Validate Issue` | exit message | run mode; F2-008 list | - | none | unknown | procedure |
| F2-011 | If not blocked, mark the Issue status to signal work has begun (if needed). | command | L272-L273, `### 2. Validate Issue` | status flip on the Issue (conditional) | F2-006 unblocked result | - | Bash, bees | unknown | procedure |
| F2-012 | Between Section 2's validation gate and Section 4's implementer dispatch, dispatch a single **Analyst** Agent per Issue for codebase-grounded design analysis. | ordering | L277, `### 3. Design analysis` | Analyst dispatch | Section 2 pass | Section 2, Section 4 | Agent | no | procedure |
| F2-013 | Treat the Issue body's framing as **problem-report context, not as authoritative design**. | invariant | L277, `### 3. Design analysis` | - | Issue body | - | none | no | procedure |
| F2-014 | The Analyst returns a Design Proposal; surface it to the user for approval before any Engineer dispatch happens. | ordering | L277, `### 3. Design analysis` | user-facing proposal | Analyst return | - | Agent, AskUserQuestion | no | procedure |
| F2-015 | Section 3 is **always run** for every Issue. | invariant | L279, `### 3. Design analysis` | - | - | - | none | no | procedure |
| F2-016 | Do NOT pre-judge whether the body is "well-researched enough" to skip the Analyst. | invariant | L279, `### 3. Design analysis` | - | - | `agents/analyst.md` "Why this role exists" | none | no | procedure |
| F2-017 | Classification of body quality is a fragile heuristic; the cleanest fix is often an option the body did not propose. | rationale-only | L279, `### 3. Design analysis` | - | - | `agents/analyst.md` "Why this role exists" | none | no | rationale |
| F2-018 | Spawn one fresh Analyst Agent per Issue, scoped per-issue, using the same cold-dispatch shape Section 4 uses for implementer roles. | command | L283, `#### Cold-dispatch the Analyst` | Analyst Agent dispatch | Section 4 cold-dispatch shape | Section 4 | Agent | no | procedure |
| F2-019 | Dispatch template: `Agent(subagent_type=analyst, run_in_background=true, prompt=<dispatch prompt with the issue body embedded verbatim and reference_materials JSON if non-empty>)`. | field-or-template | L285-L291, `#### Cold-dispatch the Analyst` | Agent call | Issue body, `reference_materials` | `agents/analyst.md` (via subagent type) | Agent | no | procedure |
| F2-020 | The dispatch prompt must include the Issue ID. | field-or-template | L293-L295, `#### Cold-dispatch the Analyst` | prompt field | `<issue-id>` | - | Agent | no | procedure |
| F2-021 | The dispatch prompt must include the Issue body **verbatim** — never paraphrase it. | invariant | L296, `#### Cold-dispatch the Analyst` | prompt field | Issue body from F2-001 | Section 4 "quote the issue body verbatim" | Agent | no | procedure |
| F2-022 | Paraphrasing silently corrupts identifier names (function, flag, type names) the Analyst's research keys against. | rationale-only | L296, `#### Cold-dispatch the Analyst` | - | - | - | none | no | rationale |
| F2-023 | The dispatch prompt must include the Issue's `reference_materials` JSON value when non-empty. | field-or-template | L297, `#### Cold-dispatch the Analyst` | prompt field | `reference_materials` from F2-001 | - | Agent | no | procedure |
| F2-024 | The Analyst owns the `WebFetch` step; the orchestrator does NOT pre-fetch the `reference_materials` URL. | invariant | L297, `#### Cold-dispatch the Analyst` | - | - | `agents/analyst.md` | none | no | procedure |
| F2-025 | The dispatch prompt must include framing prose naming the Analyst's lane: codebase-grounded design proposal, structured output, never directly modifying files. | field-or-template | L298, `#### Cold-dispatch the Analyst` | prompt field | - | `agents/analyst.md` | Agent | no | procedure |
| F2-026 | The framing MUST NOT loosen the role boundaries defined in `agents/analyst.md` (same anti-softening rule as Section 4's dispatch prompts). | invariant | L298, `#### Cold-dispatch the Analyst` | - | - | `agents/analyst.md`, Section 4 | none | no | procedure |
| F2-027 | Track the Analyst dispatch via a TaskList task named `analyst-<issue-id>` per Section 4's issue-scoped naming convention. | name-class | L300, `#### Cold-dispatch the Analyst` | TaskList task `analyst-<issue-id>` | F2-018 dispatch | Section 4 | TaskList | no | procedure |
| F2-028 | The `analyst-<issue-id>` task follows the `pending` → `in_progress` → `completed` lifecycle. | ordering | L300, `#### Cold-dispatch the Analyst` | task status transitions | F2-027 task | - | TaskList | no | procedure |
| F2-029 | The Analyst runs in the background like every other dispatched Agent in this skill. | definition | L302, `#### Cold-dispatch the Analyst` | - | - | - | Agent | no | procedure |
| F2-030 | The orchestrator MUST wait for the Analyst's completion notification before proceeding to the user-side approval gate. | ordering | L302, `#### Cold-dispatch the Analyst` | - | Agent completion notification | - | Agent | no | procedure |
| F2-031 | Do not dispatch Section 4 implementer Agents until the Analyst has returned and the user has approved — Section 4 is gated on this approval. | ordering | L302, `#### Cold-dispatch the Analyst` | - | Analyst return; Approve choice (F2-069) | Section 4 | Agent, AskUserQuestion | no | procedure |
| F2-032 | When the completion notification fires, read the Analyst's return — the structured Design Proposal per `agents/analyst.md` `## Structured-output contract`. | command | L306, `#### Surface the proposal to the user` | - | Agent return | `agents/analyst.md` `## Structured-output contract` | Agent | no | procedure |
| F2-033 | Mark the `analyst-<issue-id>` (or `-rev<n>`) TaskList task `completed` the moment its return is read, before surfacing and before creating the gate task. | ordering | L306, `#### Surface the proposal to the user` | task status `completed` | F2-027 / F2-081 task | - | TaskList | no | procedure |
| F2-034 | The Agent has exited; leaving its task active would strand a task no completion notification will ever clear. | rationale-only | L306, `#### Surface the proposal to the user` | - | - | - | none | no | rationale |
| F2-035 | While the gate is open, the pending decision is carried by the `gate-askuserquestion-*` task, its `metadata.activity` holding the finite choices. | definition | L306, `#### Surface the proposal to the user` | `metadata.activity` content | F2-057 gate task | Section 4 Read-state step | TaskList | no | procedure |
| F2-036 | Once a branch is entered, the pending decision is carried by the conversation — the state Section 4's Read-state step re-derives after compaction. | definition | L306, `#### Surface the proposal to the user` | - | - | Section 4 Read-state step | none | no | procedure |
| F2-037 | The proposal is **free-form analysis**: Problem / Root cause / Recommended approach / Blast radius / Policy decisions this change implies / Why / Alternatives considered / Options the body did not consider / Upstream-fetch status / verdict trailer. | definition | L306, `#### Surface the proposal to the user` | - | Analyst return | `agents/analyst.md` | none | no | procedure |
| F2-038 | Surface the proposal to the user as prose, NOT as an `AskUserQuestion` body. | invariant | L306, `#### Surface the proposal to the user` | user-visible prose | Analyst return | - | none | no | procedure |
| F2-039 | `AskUserQuestion` is for finite-multi-choice gates, not free-text design recommendations. | rationale-only | L306, `#### Surface the proposal to the user` | - | - | - | AskUserQuestion | no | rationale |
| F2-040 | **Unlike `### Deferred refinements`, the `### Blast radius` and `### Policy decisions this change implies` sections ARE surfaced** — in full. | relay | L306, `#### Surface the proposal to the user` | user-visible sections | Analyst return sections | - | none | no | procedure |
| F2-041 | Surface their fixed empty lines (`No invariant added, removed, or weakened.` / `None — the recommendation leaves no policy question open.`) when the Analyst emitted them. | relay | L306, `#### Surface the proposal to the user` | user-visible lines | Analyst return | - | none | no | procedure |
| F2-042 | Surfacing the fixed empty lines lets the user tell "swept and found nothing" from "never swept". | rationale-only | L306, `#### Surface the proposal to the user` | - | - | - | none | no | rationale |
| F2-043 | The Analyst's `### Deferred refinements` block is **consumed by the orchestrator and NOT surfaced to the user**. | invariant | L306, `#### Surface the proposal to the user` | - | `### Deferred refinements` block | Section 7.5 deferral-hygiene gate; `agents/analyst.md` | none | no | procedure |
| F2-044 | Strip the `### Deferred refinements` block from the surfaced proposal before rendering the user-visible prose. | command | L306, `#### Surface the proposal to the user` | stripped proposal prose | Analyst return | "Consume the Analyst's `### Deferred refinements` block" | none | no | procedure |
| F2-045 | The paragraph "Consume the Analyst's `### Deferred refinements` block" is the load-bearing site for that consumption. | definition | L306, `#### Surface the proposal to the user` | - | - | `#### Consume the Analyst's `### Deferred refinements` block` | none | no | rationale |
| F2-046 | **Extract the verdict**: before surfacing the proposal body, read the `Analyst verdict: <…>` trailer line from the Analyst's return. | command | L308, `#### Surface the proposal to the user` | verdict value | Analyst return trailer | - | none | no | procedure |
| F2-047 | Use the verdict to shape a one- or two-sentence prose preamble that precedes the proposal. | relay | L308, `#### Surface the proposal to the user` | preamble text | F2-046 verdict | - | none | no | procedure |
| F2-048 | Structural rule for preambles: divergent verdicts surface divergence prominently (phrasing may be adjusted to fit context). | invariant | L308, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-049 | The verdict is a load-bearing framing signal — the user should encounter divergence up front, not discover it by reading carefully. | rationale-only | L308, `#### Surface the proposal to the user` | - | - | - | none | no | rationale |
| F2-050 | Preamble for **`recommend-as-stated`**: "The Analyst's codebase research agrees with the Issue body's framing. The Recommended approach reflects the body's approach. Proposal follows:" | field-or-template | L310, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-051 | Preamble for **`recommend-with-refinements`**: "…broadly agrees with the Issue body, but the Recommended approach refines the body's framing. The refinements are called out in Why / Alternatives considered. Proposal follows:" | field-or-template | L311, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-052 | Preamble for **`recommend-different-approach`**: "⚠️ The Analyst's codebase research **diverged** from the Issue body's framing. The Recommended approach is an option the body did NOT propose; … Read carefully before approving. Proposal follows:" | field-or-template | L312, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-053 | Preamble for **`escalate-to-user`**: "⚠️ The Analyst could **not converge** on a single recommendation and is escalating the open question(s) to you. … Proposal follows:" | field-or-template | L313, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-054 | When `### Policy decisions this change implies` is non-empty (anything other than `None — the recommendation leaves no policy question open.`), the preamble MUST name **how many** decisions and point at the section. | relay | L315, `#### Surface the proposal to the user` | preamble text | `### Policy decisions this change implies` | - | none | no | procedure |
| F2-055 | Naming the count tells the user Approve ratifies the Analyst's recommended answers along with the design; the questions and answers ride the section itself. | rationale-only | L315, `#### Surface the proposal to the user` | - | - | - | none | no | rationale |
| F2-056 | When `### Blast radius` carries a **scope-split recommendation**, the preamble says one is carried and points at that section. | relay | L315, `#### Surface the proposal to the user` | preamble text | `### Blast radius` | - | none | no | procedure |
| F2-057 | A scope-split recommendation means: fold the distinct concern into this Issue, or file it separately and only document the property here. | definition | L315, `#### Surface the proposal to the user` | - | `### Blast radius` | - | none | no | procedure |
| F2-058 | Policy decisions and scope-split ride the existing preamble and the existing Approve / Revise / Cancel gate — do **not** add a second gate, extra option, or separate task. | invariant | L315, `#### Surface the proposal to the user` | - | - | - | AskUserQuestion, TaskList | no | procedure |
| F2-059 | The preamble is the orchestrator's responsibility, not the Analyst's; the Analyst returns the verdict, the orchestrator turns it into framing. | invariant | L317, `#### Surface the proposal to the user` | preamble text | verdict | - | none | no | procedure |
| F2-060 | The orchestrator/Analyst split keeps framing consistent across runs while the Analyst stays focused on design substance. | rationale-only | L317, `#### Surface the proposal to the user` | - | - | - | none | no | rationale |
| F2-061 | After the preamble and proposal body are surfaced, present a finite-multi-choice gate via `AskUserQuestion`. | gate | L319, `#### Surface the proposal to the user` | AskUserQuestion gate | F2-047 preamble, F2-038 prose | - | AskUserQuestion | no | procedure |
| F2-062 | **This gate is trailer-less** — the Analyst's return embeds no routing trailer; the orchestrator prose is the source of the prescription. | definition | L319, `#### Surface the proposal to the user` | - | - | - | none | no | procedure |
| F2-063 | Per the two-step contract, **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this Analyst-proposal gate, **then** call `AskUserQuestion`, in the same turn. | ordering | L319, `#### Surface the proposal to the user` | TaskList task `gate-askuserquestion-<short-suffix>`; AskUserQuestion call | - | two-step contract | TaskList, AskUserQuestion | unknown | procedure |
| F2-064 | `<short-suffix>` may be the Issue's short-id slug (e.g. `gate-askuserquestion-veq` for Issue `b.veq`) or any collision-resistant suffix not colliding with `analyst-<issue-id>`. | name-class | L319, `#### Surface the proposal to the user` | gate task name | Issue id | - | TaskList | no | procedure |
| F2-065 | Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. | invariant | L319, `#### Surface the proposal to the user` | - | - | - | TaskList, AskUserQuestion | unknown | procedure |
| F2-066 | Mark the `gate-*` task `completed` once `AskUserQuestion` returns and the routing branch is entered. | ordering | L319, `#### Surface the proposal to the user` | gate task status `completed` | AskUserQuestion result | - | TaskList, AskUserQuestion | unknown | procedure |
| F2-067 | Gate question text: "How should I proceed with this design proposal?" | field-or-template | L321, `#### Surface the proposal to the user` | AskUserQuestion question | - | - | AskUserQuestion | no | procedure |
| F2-068 | Gate option `Approve & proceed to implementation (Recommended)`: accept the Recommended approach as the authoritative design directive for this Issue. | choice-set | L322-L323, `#### Surface the proposal to the user` | AskUserQuestion option | - | Section 4 | AskUserQuestion | no | procedure |
| F2-069 | Approval covers the design, the Analyst's recommended answer to every question in `### Policy decisions this change implies`, and any scope-split recommendation in `### Blast radius`. | definition | L323, `#### Surface the proposal to the user` | - | proposal sections | - | none | no | procedure |
| F2-070 | On Approve, carry the directive into Section 4's implementer dispatch — the Engineer prompt when source code needs modification, Test Writer and Doc Writer dispatches otherwise per Section 4's conditional-dispatch rules. | relay | L323, `#### Surface the proposal to the user` | directive in dispatch prompt | Approve choice | Section 4 conditional-dispatch rules | Agent | no | procedure |
| F2-071 | Gate option `Revise`: user has feedback; iterate in prose (free-text reply), then optionally re-dispatch the Analyst with the feedback as context. | choice-set | L324, `#### Surface the proposal to the user` | AskUserQuestion option | - | - | AskUserQuestion, Agent | no | procedure |
| F2-072 | Gate option `Cancel`: exit cleanly without dispatching any implementer Agent; no commit is made; the Issue stays `open`. | choice-set | L325, `#### Surface the proposal to the user` | AskUserQuestion option | - | - | AskUserQuestion | no | procedure |
| F2-073 | On **Approve**, capture the Analyst's Design Proposal as the run's authoritative design directive for this Issue. | command | L329, `#### Branch on the user's choice` | design directive | Analyst return | - | none | no | procedure |
| F2-074 | The directive sections are `### Recommended approach`, `### Blast radius`, and `### Policy decisions this change implies` — all three directive, not context. | definition | L329, `#### Branch on the user's choice` | directive composition | Analyst return sections | - | none | no | procedure |
| F2-075 | The directive also carries `### Why` / `### Alternatives considered` / `### Options the body did not consider` as context the Engineer may consult. | definition | L329, `#### Branch on the user's choice` | directive composition | Analyst return sections | - | none | no | procedure |
| F2-076 | On Approve, `analyst-<issue-id>` (or `analyst-<issue-id>-rev<n>` when re-fired) was already `completed` on return-read — nothing to close out here. | invariant | L329, `#### Branch on the user's choice` | - | F2-033 | surfacing step above | TaskList | no | procedure |
| F2-077 | Pass the directive forward to Section 4's Engineer dispatch prompt per "Authoritative design directive" below. | relay | L329, `#### Branch on the user's choice` | directive in Engineer prompt | F2-073 | Section 4; `#### Authoritative design directive (carried into Section 4)` | Agent | no | procedure |
| F2-078 | **When this gate was re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice**, run that choice's in-flight-lane TaskList sweep **before** re-entering Section 4. | ordering | L329, `#### Branch on the user's choice` | swept TaskList | re-fire origin | part (c)/(d); `### Orchestrator discipline: routing review findings`; Section 4 | TaskList | no | procedure |
| F2-079 | The sweep marks every active `test-writer-<issue-id>` / `doc-writer-<issue-id>` / `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` task `completed` and discards their findings. | command | L329, `#### Branch on the user's choice` | task statuses `completed`; findings discarded | active lane tasks | `### Orchestrator discipline: routing review findings` (specification; this is only ordering) | TaskList | no | procedure |
| F2-080 | The sweep holds on **every** Approve reached from that re-fire — including a later Approve after one or more Revise iterations on it. | invariant | L329, `#### Branch on the user's choice` | - | re-fire origin; Revise history | - | TaskList | no | procedure |
| F2-081 | After Approve processing, proceed to Section 4. | ordering | L329, `#### Branch on the user's choice` | - | - | Section 4 | none | no | procedure |
| F2-082 | On **Revise**, continue the conversation with the user in prose and engage with feedback such as "I disagree with X because…" or "have you considered Y?". | relay | L331, `#### Branch on the user's choice` | conversation | user feedback | - | none | no | procedure |
| F2-083 | When feedback warrants a fresh codebase pass (substantively different approach, user wants a specific code path investigated), **re-dispatch the Analyst** as a fresh cold invocation. | command | L331, `#### Branch on the user's choice` | new Analyst dispatch | user feedback | - | Agent | no | procedure |
| F2-084 | The prior Analyst's task (`analyst-<issue-id>` on the first revision, `analyst-<issue-id>-rev<n-1>` afterwards) was already `completed` on return-read — nothing to close out before dispatching. | invariant | L333, `#### Branch on the user's choice` | - | F2-033 | surfacing step above | TaskList | no | procedure |
| F2-085 | Issue the re-dispatch with `subagent_type=analyst` and a new TaskList task named `analyst-<issue-id>-rev<n>`, `<n>` being the 1-based revision count (`-rev1`, `-rev2`, …). | name-class | L334, `#### Branch on the user's choice` | Agent dispatch; TaskList task `analyst-<issue-id>-rev<n>` | revision count | - | Agent, TaskList | no | procedure |
| F2-086 | The re-dispatch prompt embeds the same Issue body verbatim and `reference_materials`, PLUS a clearly-labeled `## Prior proposal and user feedback` section. | field-or-template | L335, `#### Branch on the user's choice` | prompt section `## Prior proposal and user feedback` | Issue body; `reference_materials`; prior proposal; user feedback | - | Agent | no | procedure |
| F2-087 | The `## Prior proposal and user feedback` section quotes the prior Design Proposal in full and the user's revision feedback verbatim. | field-or-template | L335, `#### Branch on the user's choice` | prompt content | prior Analyst return; user feedback | - | Agent | no | procedure |
| F2-088 | **"In full" includes the prior proposal's `### Deferred refinements` block**, even though the surfacing step stripped it from the user-facing prose. | invariant | L335, `#### Branch on the user's choice` | prompt content | prior `### Deferred refinements` block | surfacing step above; supersede-and-clear rule below | Agent | no | procedure |
| F2-089 | The revising Analyst needs the prior deferrals so it carries each forward or explicitly drops it; supersede-and-clear clears the superseded `defer-*` tasks, so an omitted deferral is dropped with no carrier. | rationale-only | L335, `#### Branch on the user's choice` | - | - | supersede-and-clear rule below | none | no | rationale |
| F2-090 | When the re-dispatched Analyst returns, repeat the surface-and-gate flow above. | ordering | L336, `#### Branch on the user's choice` | re-fired gate | new Analyst return | `#### Surface the proposal to the user` | Agent, AskUserQuestion, TaskList | no | procedure |
| F2-091 | There is no fixed cap on revision count; the user terminates the loop by picking Approve or Cancel. | invariant | L337, `#### Branch on the user's choice` | - | user choice | - | AskUserQuestion | no | procedure |
| F2-092 | When feedback is light enough (wording tweak, terminology clarification, "yes please proceed with refinement X you mentioned in Alternatives"), the orchestrator may carry it directly into the Approve branch without re-dispatching. | recovery | L339, `#### Branch on the user's choice` | Approve-branch entry | user feedback | Approve branch above | none | no | procedure |
| F2-093 | In that light-revision case, capture the original directive sections per the Approve branch plus the user's clarification in the directive flowing to Section 4. | command | L339, `#### Branch on the user's choice` | design directive (with clarification) | F2-074, F2-075, user clarification | Section 4 | none | no | procedure |
| F2-094 | On **Cancel**, **NO commit is made; the Issue stays `open`.** | invariant | L341, `#### Branch on the user's choice` | - | Cancel choice | - | git, bees | no | procedure |
| F2-095 | Exit a cancelled Issue through Section 7's **`#### Aborted-Issue close-out`** rather than closing out by hand here. | ordering | L341, `#### Branch on the user's choice` | - | Cancel choice | Section 7 `#### Aborted-Issue close-out` | none | no | procedure |
| F2-096 | The Aborted-Issue close-out sweeps every TaskList entry scoped to this Issue (the `analyst-<issue-id>` task is already `completed`, so the sweep is a no-op for it). | definition | L341, `#### Branch on the user's choice` | swept TaskList | Issue-scoped tasks | Section 7 `#### Aborted-Issue close-out` | TaskList | no | procedure |
| F2-097 | The Aborted-Issue close-out runs Section 7.5's deferral-hygiene gate over any deferral this Issue already recorded. | definition | L341, `#### Branch on the user's choice` | deferral-hygiene gate | `defer-*` tasks | Section 7.5 | TaskList | no | procedure |
| F2-098 | The Aborted-Issue close-out runs the **Issue-boundary state-externalization checkpoint** on its aborted path. | definition | L341, `#### Branch on the user's choice` | run-state checkpoint | - | Issue-boundary state-externalization checkpoint (Section 7) | none | no | procedure |
| F2-099 | The close-out carries the mode branch: in single-issue mode the run ends there. | ordering | L341, `#### Branch on the user's choice` | run end | run mode | Section 7 `#### Aborted-Issue close-out` | none | no | procedure |
| F2-100 | In list / `all` mode with Issues remaining, Cancel **stops the run** rather than continuing, naming the uncommitted working-tree state and the fresh-session resume command for the still-unfixed subset. | ordering | L341, `#### Branch on the user's choice` | stop message with resume command | run mode; remaining Issue list | Section 7 `#### Aborted-Issue close-out` step 4 | git | no | procedure |
| F2-101 | Independently of Approve / Revise / Cancel routing, the Analyst's return carries a `### Deferred refinements` block per `agents/analyst.md`'s return-shape contract. | definition | L345, `#### Consume the Analyst's `### Deferred refinements` block` | - | Analyst return | `agents/analyst.md` | none | no | procedure |
| F2-102 | On verdicts `recommend-as-stated` and `escalate-to-user` the block is structurally `None`; on `recommend-with-refinements` and `recommend-different-approach` it is a bulleted list of refinements. | definition | L345, `#### Consume the Analyst's `### Deferred refinements` block` | - | verdict; block | `agents/analyst.md` | none | no | procedure |
| F2-103 | The `### Deferred refinements` block is the load-bearing inter-session carrier for refinements the Analyst surfaces but the Engineer will not implement in this fix. | rationale-only | L345, `#### Consume the Analyst's `### Deferred refinements` block` | - | - | - | none | no | rationale |
| F2-104 | **At the moment of user approval** (original Approve, Approve after a Revise iteration, or Approve after a part (c)/(d) re-fire), walk the latest return's `### Deferred refinements` block. | ordering | L347, `#### Consume the Analyst's `### Deferred refinements` block` | - | Approve choice; latest Analyst return | part (c)/(d) `Re-dispatch the Analyst with this finding` | none | no | procedure |
| F2-105 | Create one `defer-<short-suffix>` TaskList task per non-`None` bullet whose destination annotation is `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. | command | L347, `#### Consume the Analyst's `### Deferred refinements` block` | TaskList task(s) `defer-<short-suffix>` | bullets with destination annotation | - | TaskList | no | procedure |
| F2-106 | The `defer-*` task's `metadata.activity` string carries the bullet's one-line description. | field-or-template | L347, `#### Consume the Analyst's `### Deferred refinements` block` | `metadata.activity` | bullet text | - | TaskList | no | procedure |
| F2-107 | Bullets annotated `addressed-now-in-this-Issue` are NOT added to the `defer-*` ledger. | invariant | L347, `#### Consume the Analyst's `### Deferred refinements` block` | - | bullet annotation | - | TaskList | no | procedure |
| F2-108 | `addressed-now-in-this-Issue` refinements roll into the `### Recommended approach` flowing into Section 4's Engineer dispatch and need no inter-session carrier. | rationale-only | L347, `#### Consume the Analyst's `### Deferred refinements` block` | - | - | Section 4 | none | no | rationale |
| F2-109 | Bullets without a destination annotation are a contract violation; surface that to the user as a malformed return rather than guessing a destination. | recovery | L347, `#### Consume the Analyst's `### Deferred refinements` block` | user-visible malformed-return report | bullet annotation | `agents/analyst.md` return-shape contract | none | no | procedure |
| F2-110 | On any re-dispatch (Revise iteration or part (c)/(d) re-fire), consume only the **latest** Analyst's `### Deferred refinements` block at Approve; prior blocks are superseded. | invariant | L349, `#### Consume the Analyst's `### Deferred refinements` block` | - | latest `-rev<n>` return | part (c)/(d) | none | no | procedure |
| F2-111 | **Supersession clears only the `defer-*` tasks of an iteration the user never approved** (a Revise chain's rejected iterations). | invariant | L349, `#### Consume the Analyst's `### Deferred refinements` block` | - | `defer-*` tasks from unapproved iterations | - | TaskList | no | procedure |
| F2-112 | Mark superseded `defer-*` tasks `completed` with `metadata.activity` annotated as superseded before consuming the approved iteration's block. | ordering | L349, `#### Consume the Analyst's `### Deferred refinements` block` | task status `completed`; `metadata.activity` annotation | F2-111 set | - | TaskList | no | procedure |
| F2-113 | **`defer-*` tasks created at an earlier *Approve* survive a later re-fire** and stay in the active set. | invariant | L349, `#### Consume the Analyst's `### Deferred refinements` block` | - | earlier-Approve `defer-*` tasks | - | TaskList | no | procedure |
| F2-114 | That earlier approval still stands; the re-fired Analyst is briefed on the reviewer's finding so its block may be `None`; Section 7.5 Step 1 enumerates only active tasks and Step 0 walks only the latest block; clearing would destroy every banked refinement. | rationale-only | L349, `#### Consume the Analyst's `### Deferred refinements` block` | - | - | Section 7.5 Step 0, Step 1 | none | no | rationale |
| F2-115 | On Cancel, create no `defer-*` tasks from the `### Deferred refinements` block; the Issue stays `open` and deferrals travel with the next Analyst pass when `/quo-fix-issue` is re-run. | invariant | L349, `#### Consume the Analyst's `### Deferred refinements` block` | - | Cancel choice | `/quo-fix-issue` | TaskList | no | procedure |
| F2-116 | This consumption paragraph is the load-bearing source for the Analyst-lane portion of Section 7.5's deferral-hygiene gate; without it the gate fires empty for that lane. | rationale-only | L351, `#### Consume the Analyst's `### Deferred refinements` block` | - | - | Section 7.5 | none | no | rationale |
| F2-117 | Once the user picks Approve, the directive flowing into Section 4's Engineer prompt includes the Analyst's `### Recommended approach` section verbatim. | field-or-template | L355-L357, `#### Authoritative design directive (carried into Section 4)` | directive component | Analyst return | Section 4 | none | no | procedure |
| F2-118 | The directive includes `### Blast radius` and `### Policy decisions this change implies` verbatim, on the **directive** side (enumerated site list; policy answers the user ratified). | field-or-template | L358, `#### Authoritative design directive (carried into Section 4)` | directive component | Analyst return | - | none | no | procedure |
| F2-119 | The directive includes `### Why`, `### Alternatives considered`, and `### Options the body did not consider` as context for trade-offs and rejected alternatives. | field-or-template | L359, `#### Authoritative design directive (carried into Section 4)` | directive component | Analyst return | - | none | no | procedure |
| F2-120 | The directive includes any user-supplied refinement captured on the Approve branch from a "light enough to incorporate without a fresh Analyst pass" revision. | field-or-template | L360, `#### Authoritative design directive (carried into Section 4)` | directive component | F2-093 clarification | Approve branch | none | no | procedure |
| F2-121 | Section 4's Engineer dispatch prompt embeds this directive as the **authoritative design source** for the fix. | relay | L362, `#### Authoritative design directive (carried into Section 4)` | Engineer prompt content | directive | Section 4 | Agent | no | procedure |
| F2-122 | The Issue body itself still flows into Section 4's prompt verbatim, byte-for-byte (identifier spellings, contract surfaces). | invariant | L362, `#### Authoritative design directive (carried into Section 4)` | Engineer prompt content | Issue body | Section 4 "quote the issue body verbatim" | Agent | no | procedure |
| F2-123 | Where the body's framing and the directive conflict, the directive wins. | invariant | L362, `#### Authoritative design directive (carried into Section 4)` | - | Issue body; directive | - | none | no | procedure |
| F2-124 | Section 4's dispatch-prompt prose documents the integration shape of directive plus body. | definition | L362, `#### Authoritative design directive (carried into Section 4)` | - | - | Section 4 | none | no | procedure |
| F2-125 | The orchestrator MUST NOT short-circuit Section 3 on a heuristic judgement that the Issue body is "well-researched enough." | invariant | L366, `#### Anti-pattern: do not classify the body upfront` | - | - | Section 3 | none | no | procedure |
| F2-126 | Body-quality classification is fragile: a body citing code paths may be a typo fix; a one-sentence body may sit behind a rich `reference_materials` URL; only the Analyst's research is reliable. | rationale-only | L366, `#### Anti-pattern: do not classify the body upfront` | - | - | - | none | no | rationale |
| F2-127 | Always dispatch the Analyst; its verdict (`recommend-as-stated` / `recommend-with-refinements` / `recommend-different-approach` / `escalate-to-user`) IS the classification. | invariant | L366, `#### Anti-pattern: do not classify the body upfront` | - | verdict | - | Agent | no | procedure |
| F2-128 | When the body IS well-researched the Analyst converges cheaply (prompt-caching helps) and the Approve gate fires cheaply — overhead is bounded. | rationale-only | L366, `#### Anti-pattern: do not classify the body upfront` | - | - | - | none | no | rationale |

## Anchors defined here

Headings:

- L248 `### 2. Validate Issue`
- L275 `### 3. Design analysis`
- L281 `#### Cold-dispatch the Analyst`
- L304 `#### Surface the proposal to the user`
- L327 `#### Branch on the user's choice`
- L343 `#### Consume the Analyst's `### Deferred refinements` block`
- L353 `#### Authoritative design directive (carried into Section 4)`
- L364 `#### Anti-pattern: do not classify the body upfront`

Bolded phrases:

- L277 **Analyst**
- L277 **problem-report context, not as authoritative design**
- L279 **always run**
- L296 **verbatim**
- L298 **MUST NOT**
- L302 **MUST**
- L306 **Mark that Analyst's `analyst-<issue-id>` (or `-rev<n>`) TaskList task `completed` the moment its return is read, before surfacing the proposal and before creating the gate task below**
- L306 **free-form analysis**
- L306 **Unlike `### Deferred refinements`, the `### Blast radius` and `### Policy decisions this change implies` sections ARE surfaced**
- L306 **consumed by the orchestrator and NOT surfaced to the user**
- L308 **Extract the verdict and frame the preamble.**
- L310 **`recommend-as-stated`**
- L311 **`recommend-with-refinements`**
- L312 **`recommend-different-approach`**
- L312 **diverged**
- L313 **`escalate-to-user`**
- L313 **not converge**
- L315 **The preamble also carries the policy decisions and any scope-split recommendation.**
- L315 **how many**
- L315 **scope-split recommendation**
- L315 **not** (in "do **not** add a second gate")
- L319 **This gate is trailer-less**
- L319 **first**
- L319 **then**
- L323 **Approve & proceed to implementation (Recommended)**
- L324 **Revise**
- L325 **Cancel**
- L329 **Approve**
- L329 **When this gate was re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice**
- L329 **before**
- L329 **every**
- L331 **Revise**
- L331 **re-dispatch the Analyst**
- L335 **"In full" includes the prior proposal's `### Deferred refinements` block**
- L341 **Cancel**
- L341 **NO commit is made; the Issue stays `open`.**
- L341 **`#### Aborted-Issue close-out`**
- L341 **Issue-boundary state-externalization checkpoint**
- L341 **stops the run**
- L347 **At the moment of user approval — i.e., when the user picks Approve on the original proposal, when the user picks Approve after a Revise iteration (re-dispatched Analyst's return), OR when the user picks Approve after this gate was re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice — walk the latest Analyst return's `### Deferred refinements` block and create one `defer-<short-suffix>` TaskList task per non-`None` bullet whose destination annotation is `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`.**
- L349 **latest**
- L349 **Supersession clears only the `defer-*` tasks of an iteration the user never approved**
- L349 **`defer-*` tasks created at an earlier *Approve* survive a later re-fire**
- L358 **directive**
- L362 **authoritative design source**

Other pointable identifiers (non-heading, non-bold, but named as anchors by the text):

- L306 "Consume the Analyst's `### Deferred refinements` block" (named as the load-bearing consumption site)
- L306 `## Structured-output contract` (in `agents/analyst.md`)
- L329 `### Orchestrator discipline: routing review findings` (elsewhere in this skill)
- L329 "Authoritative design directive" (forward pointer to L353 heading)
- L335 `## Prior proposal and user feedback` (dispatch-prompt section label)
- L335 "supersede-and-clear rule below" (points at L349)

## Rationale-only spans

Whole lines containing no rule:

- L351 (1 line) — consumption paragraph justifies 7.5 gate.

Intra-line rationale sentences embedded in rule-bearing lines (captured as `rationale-only` rows above; not whole-line spans): L279 second sentence (classification heuristic fragile), L296 second clause (paraphrase corrupts identifiers), L306 "its Agent has exited…" and "`AskUserQuestion` is for finite-multi-choice gates…" and "so the user can tell…", L308 "The verdict is a load-bearing framing signal…", L315 "so the user knows Approve ratifies…", L317 second and third sentences (framing consistency), L335 "which the revising Analyst needs in hand…", L345 last sentence (inter-session carrier), L347 "those refinements are rolled into…", L349 "That approval still stands… Clearing them would destroy…", L366 parenthetical and final sentence (fragility examples; bounded overhead).

Whole-line rationale total: 1 line (L351). Rationale rows in table: 15 (F2-017, 022, 034, 039, 042, 045, 049, 055, 060, 089, 103, 108, 114, 116, 126, 128 — 16 including F2-045 which is a definition-of-pointer classed as rationale).
