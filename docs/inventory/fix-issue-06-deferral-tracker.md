# Rule inventory — quo-fix-issue Section 7.5 (deferral hygiene + compromise tracker)

Source: `/Users/jesseg/code/quorum/skills/quo-fix-issue/SKILL.md` lines 979–1113.

Headings in this slice: `### 7.5 Before handoff — deferral hygiene` (L979), `#### Session-scoped compromise tracker` (L983), `#### Compromise-tracker append triggers` (L1020). Bolded step leads (`Step 0`–`Step 3`, `Per-Issue firing`, `Batch end-of-run firing`, `Follow-up commit`, `Resolving the helper path`) are given in parentheses in the Site column for locality.

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| F6-001 | Every `AskUserQuestion` firing in this gate goes through the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L981 (7.5 intro) | `gate-askuserquestion-<short-suffix>` task + AskUserQuestion | - | Step 2, Step 3 | TaskList, AskUserQuestion | yes | procedure |
| F6-002 | The firings covered are Step 2's initial Fix / File / Encode choice plus any Step 3 re-fires for an unclosed `defer-*` subset. | definition | L981 (7.5 intro) | - | active `defer-*` set | Step 2, Step 3 | none | yes | procedure |
| F6-003 | First `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate. | name-class | L981 (7.5 intro) | `gate-askuserquestion-<short-suffix>` task | - | - | TaskList | yes | procedure |
| F6-004 | Use a distinct `<short-suffix>` per fire so Step 3 re-fires are not mistaken for the Step 2 first fire. | invariant | L981 (7.5 intro) | distinct task names | - | Step 2, Step 3 | TaskList | yes | procedure |
| F6-005 | Call `AskUserQuestion` in the same turn as the `TaskCreate`. | ordering | L981 (7.5 intro) | AskUserQuestion fire | F6-003 | - | AskUserQuestion, TaskList | yes | procedure |
| F6-006 | Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed. | ordering | L981 (7.5 intro) | status flip `completed` | AskUserQuestion result | - | TaskList, AskUserQuestion | yes | procedure |
| F6-007 | Maintain a **session-scoped compromise tracker**: a single markdown file accumulating one entry per accepted compromise across this run. | definition | L985 (Session-scoped compromise tracker) | tracker file | - | - | none | yes | procedure |
| F6-008 | An accepted compromise is a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override. | definition | L985 (Session-scoped compromise tracker) | - | gate results | - | none | yes | procedure |
| F6-009 | Tracker exists so accepted compromises stay visible and challengeable rather than baked silently into the new baseline. | rationale-only | L985 (Session-scoped compromise tracker) | - | - | - | none | yes | rationale |
| F6-010 | The four append triggers (A/B/C/D) are defined under "Compromise-tracker append triggers" below. | definition | L985 (Session-scoped compromise tracker) | - | - | `Compromise-tracker append triggers` | none | yes | procedure |
| F6-011 | The post-completion review in Section 8 consumes the tracker as input. | relay | L985 (Session-scoped compromise tracker) | - | tracker file | Section 8 | none | yes | procedure |
| F6-012 | This subsection is the **canonical definition site** that the trigger write-instructions reference by name. | definition | L985 (Session-scoped compromise tracker) | - | - | `Compromise-tracker append triggers` | none | yes | procedure |
| F6-013 | Write the tracker under `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). | invariant | L987 (Tracker file path and naming) | tracker file location | scratch-file convention | - | none | yes | procedure |
| F6-014 | Canonical tracker filename is `compromises-YYYYMMDD-HHMM-<short-suffix>.md`. | name-class | L987 (Tracker file path and naming) | tracker filename | - | - | none | yes | procedure |
| F6-015 | `YYYYMMDD-HHMM` is a UTC timestamp generated **once at the start of the run**. | invariant | L987 (Tracker file path and naming) | timestamp component | run start | - | none | yes | procedure |
| F6-016 | Example timestamp value: `20260520-1714`. | example | L987 (Tracker file path and naming) | - | - | - | none | yes | example |
| F6-017 | `<short-suffix>` is a short collision-resistant random string. | name-class | L987 (Tracker file path and naming) | suffix component | - | - | none | yes | procedure |
| F6-018 | The timestamp prefix makes tracker files debuggably identifiable across multiple runs accumulated in `<tempdir>/.quorum/`. | rationale-only | L987 (Tracker file path and naming) | - | - | - | none | yes | rationale |
| F6-019 | Create the `.quorum` directory if it does not already exist. | command | L987 (Tracker file path and naming) | directory | - | - | Bash | yes | procedure |
| F6-020 | Author and append the tracker file via the `Write` tool, never a shell redirect. | command | L987 (Tracker file path and naming) | tracker file content | - | bash-etiquette, scratch-file conventions | none | yes | procedure |
| F6-021 | POSIX directory snippet: `mkdir -p /tmp/.quorum`, then write/append `/tmp/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` via `Write`. | command | L989-L993 (Tracker file path and naming) | directory | - | - | Bash | yes | procedure |
| F6-022 | Windows directory snippet: `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`, then write `$env:TEMP\.quorum\compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` via `Write`. | command | L995-L999 (Tracker file path and naming) | directory | - | - | Bash | yes | procedure |
| F6-023 | Each accepted compromise appends one `## Compromise <n>` section to the tracker. | field-or-template | L1001 (Entry shape) | tracker entry | - | - | none | yes | procedure |
| F6-024 | `<n>` is a **1-based counter scoped to the current run's tracker file**, NOT a globally unique identifier. | invariant | L1001 (Entry shape) | entry counter | tracker file | - | none | yes | procedure |
| F6-025 | The canonical entry shape is reproduced from the SDD Data models `#### Compromise tracker entry shape`. | definition | L1001 (Entry shape) | - | - | SDD `#### Compromise tracker entry shape` | none | yes | procedure |
| F6-026 | Field `**Finding (verbatim):**` carries `<severity tag> <fix-path enumeration with depth tags> <description>`. | field-or-template | L1006, L1016 (Entry shape) | entry field | reviewer finding | - | none | yes | procedure |
| F6-027 | Field `**Fix paths surfaced by reviewer:**` lists `(a) [depth:<depth>] <description>`, `(b) [depth:<depth>] <description>`, … lines. | field-or-template | L1007-L1010, L1016 (Entry shape) | entry field | reviewer fix-path enumeration | - | none | yes | procedure |
| F6-028 | Field `**Decision:**` holds exactly one value from the Decision enum. | field-or-template | L1011, L1016 (Entry shape) | entry field | gate result | - | none | yes | procedure |
| F6-029 | Decision enum value: `User picked path (a)`, `User picked path (b)`, … (one per enumerated letter). | field-or-template | L1011 (Entry shape) | Decision value | - | - | none | yes | procedure |
| F6-030 | Decision enum value: `User picked Defer to follow-up Issue`. | field-or-template | L1011 (Entry shape) | Decision value | - | Trigger A | none | yes | procedure |
| F6-031 | Decision enum value: `User picked Accept the limitation`. | field-or-template | L1011 (Entry shape) | Decision value | - | Trigger B | none | yes | procedure |
| F6-032 | Decision enum value: `Orchestrator picked path (x) — highest-quality`. | field-or-template | L1011 (Entry shape) | Decision value | - | Trigger C | none | yes | procedure |
| F6-033 | Decision enum value: `User overrode auto-route after post-completion challenge (depth misjudgment)`. | field-or-template | L1011 (Entry shape) | Decision value | - | Trigger D, SR-6.7 | none | yes | procedure |
| F6-034 | Decision enum value: `User accepted under-enumeration after post-completion challenge`. | field-or-template | L1011 (Entry shape) | Decision value | - | Trigger D, SR-4.6 | none | yes | procedure |
| F6-035 | Field `**Rationale:**` holds the user's stated reason if surfaced via `AskUserQuestion`, or on an ungated pick the one-line reason that path was preferred. | field-or-template | L1012, L1016 (Entry shape) | entry field | AskUserQuestion result or orchestrator reason | - | none | yes | procedure |
| F6-036 | On a `Defer to follow-up Issue` entry, `Rationale` also names which remaining enumerated path shipped as the soft fix, or that none did. | field-or-template | L1012, L1016 (Entry shape) | Rationale content | soft-fix dispatch | Trigger A | none | yes | procedure |
| F6-037 | On a blocker deferral, `Rationale` carries the narrowing record in place of the soft-fix letter. | field-or-template | L1012, L1016 (Entry shape) | Rationale content | narrowing | Trigger A | none | yes | procedure |
| F6-038 | Field `**Follow-up Issue:**` holds the ticket ID if filed via `/quo-file-issue`, else `none`. | field-or-template | L1013, L1016 (Entry shape) | entry field | `/quo-file-issue` result | `/quo-file-issue` | none | yes | procedure |
| F6-039 | The entry has exactly five fields: `Finding (verbatim)`, `Fix paths surfaced by reviewer`, `Decision`, `Rationale`, `Follow-up Issue`. | invariant | L1016 (Entry shape) | - | - | - | none | yes | procedure |
| F6-040 | The `Decision` enum carries **two** post-completion-override values: the SR-6.7 depth-misjudgment override and the SR-4.6 under-enumeration analog override. | definition | L1016 (Entry shape) | - | - | SR-6.7, SR-4.6, Trigger D | none | yes | procedure |
| F6-041 | Two override values exist because Trigger D is the single owner of all post-completion-override writes regardless of which kind fired. | rationale-only | L1016 (Entry shape) | - | - | Trigger D | none | yes | rationale |
| F6-042 | The tracker persists across orchestrator-yield events within a single run because it is a file-system artifact. | definition | L1018 (Persistence) | - | tracker file | - | none | yes | procedure |
| F6-043 | Generate a fresh `YYYYMMDD-HHMM` timestamp + `<short-suffix>` at the **start of each run**. | invariant | L1018 (Persistence) | new tracker filename | run start | - | none | yes | procedure |
| F6-044 | Previous-run tracker files are **NEVER appended to**; a new run always writes its own new file. | invariant | L1018 (Persistence) | - | prior tracker files | - | none | yes | procedure |
| F6-045 | Never delete the tracker file; do NOT instruct any `rm` / `Remove-Item`. | invariant | L1018 (Persistence) | - | scratch-file convention | - | none | yes | procedure |
| F6-046 | Four moments append a tracker entry: Triggers A–C fire from the "Orchestrator discipline: routing review findings" gates / ungated dispatch; Trigger D from Section 8's post-completion review. | definition | L1022 (Compromise-tracker append triggers) | - | - | `Orchestrator discipline: routing review findings`, Section 8 | none | yes | procedure |
| F6-047 | Each trigger anchors to its gate by name; the write fires from the branch named in the trigger. | invariant | L1022 (Compromise-tracker append triggers) | - | - | - | none | yes | procedure |
| F6-048 | Trigger A fires at the scope-bounding gate (part (c) of `### Orchestrator discipline: routing review findings`) when the user picks `Defer to follow-up Issue`. | gate | L1024 (Trigger A) | tracker entry | AskUserQuestion result | part (c), `### Orchestrator discipline: routing review findings` | AskUserQuestion | yes | procedure |
| F6-049 | Append the Trigger A entry **IMMEDIATELY AFTER** `/quo-file-issue` returns successfully with the new Issue ID and **BEFORE** continuing with the soft-fix dispatch. | ordering | L1024 (Trigger A) | tracker entry | `/quo-file-issue` result | `/quo-file-issue` | none | yes | procedure |
| F6-050 | Capture the follow-up Issue ID in the entry's `Follow-up Issue` field. | field-or-template | L1024 (Trigger A) | `Follow-up Issue` value | `/quo-file-issue` result | - | none | yes | procedure |
| F6-051 | Set `Decision: User picked Defer to follow-up Issue`. | field-or-template | L1024 (Trigger A) | `Decision` value | - | - | none | yes | procedure |
| F6-052 | Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all. | field-or-template | L1024 (Trigger A) | field value | reviewer finding | routing-decision gate | none | yes | procedure |
| F6-053 | The no-path case is reachable at the routing-decision gate, whose `Defer` choice is offered whatever the path count. | definition | L1024 (Trigger A) | - | - | routing-decision gate | none | yes | procedure |
| F6-054 | **Name in `Rationale` which remaining enumerated path shipped as the soft fix** by its letter, or that **none did**. | field-or-template | L1024 (Trigger A) | `Rationale` content | soft-fix dispatch | - | none | yes | procedure |
| F6-055 | "None did" applies in the single-path case at the scope-bounding gate and to any deferral at the routing-decision gate. | definition | L1024 (Trigger A) | - | - | scope-bounding gate, routing-decision gate | none | yes | procedure |
| F6-056 | The routing-decision gate's `Defer` bullet ships nothing against the finding regardless of how many paths the reviewer enumerated. | definition | L1024 (Trigger A) | - | - | routing-decision gate | none | yes | procedure |
| F6-057 | **On a `blocker` deferral the narrowing takes that slot**: record what was scoped down and why the blocker no longer describes what remains. | field-or-template | L1024 (Trigger A) | `Rationale` content | narrowing | - | none | yes | procedure |
| F6-058 | A blocker's Defer branch ships a narrowing rather than one of the reviewer's other paths. | definition | L1024 (Trigger A) | - | - | - | none | yes | procedure |
| F6-059 | The deferral and what shipped in its place are one decision; an entry recording only the deferral cannot distinguish soft-fixed from unfixed. | rationale-only | L1024 (Trigger A) | - | - | - | none | yes | rationale |
| F6-060 | The Trigger A write fires from the scope-bounding gate's `Defer to follow-up Issue` branch. | invariant | L1024 (Trigger A) | tracker entry | - | scope-bounding gate | none | yes | procedure |
| F6-061 | **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger** on the same terms and entry shape. | gate | L1024 (Trigger A) | tracker entry | AskUserQuestion result | routing-decision gate | AskUserQuestion | yes | procedure |
| F6-062 | The routing-decision gate offers `Defer` to any finding, and to a `blocker` when part (c)'s two Defer conditions hold. | definition | L1024 (Trigger A) | - | - | part (c), routing-decision gate | none | yes | procedure |
| F6-063 | **On a `blocker`-severity finding this branch is reachable only as Defer-with-narrowing, at either gate** (part (c)'s severity rule, applied by part (d) on its own terms). | precondition | L1024 (Trigger A) | - | finding severity | part (c), part (d) | none | yes | procedure |
| F6-064 | A blocker deferral entry MUST carry a **narrowing record** in `Rationale`: what was narrowed out and why the blocker no longer describes anything that ships. | invariant | L1024 (Trigger A) | `Rationale` content | narrowing | - | none | yes | procedure |
| F6-065 | A blocker deferral without a narrowing record is read by every downstream consumer as a contract violation. | invariant | L1024 (Trigger A) | - | - | - | none | yes | procedure |
| F6-066 | Trigger B fires at the scope-bounding gate's `Accept the limitation` branch when the user picks `Accept the limitation`. | gate | L1026 (Trigger B) | tracker entry | AskUserQuestion result | scope-bounding gate | AskUserQuestion | yes | procedure |
| F6-067 | Append the Trigger B entry **IMMEDIATELY AFTER** the `AskUserQuestion` returns and **BEFORE** the orchestrator continues without a fix. | ordering | L1026 (Trigger B) | tracker entry | AskUserQuestion result | - | AskUserQuestion | yes | procedure |
| F6-068 | Set `Decision: User picked Accept the limitation`. | field-or-template | L1026 (Trigger B) | `Decision` value | - | - | none | yes | procedure |
| F6-069 | Set `Follow-up Issue: none` on a Trigger B entry. | field-or-template | L1026 (Trigger B) | `Follow-up Issue` value | - | - | none | yes | procedure |
| F6-070 | Trigger B is **Unreachable for a `blocker`-severity finding** unconditionally; the gate's severity rule withholds the branch because accepting a blocker ships it. | precondition | L1026 (Trigger B) | - | finding severity | scope-bounding gate severity rule | none | yes | procedure |
| F6-071 | Trigger C has **no gate**; the write is wired into the dispatch step itself. | invariant | L1028 (Trigger C) | - | - | - | none | yes | procedure |
| F6-072 | Trigger C fires at the **MOMENT of implementer dispatch** for any finding part (a) routed by **row 6** (ungated dispatch of the Step 1 orchestrator-picked path). | gate | L1028 (Trigger C) | tracker entry | routing table row 6 | row 6, Step 1, part (a) | Agent | yes | procedure |
| F6-073 | Append the Trigger C entry in the **SAME LOGICAL BLOCK as that dispatch**, not a separate post-gate block. | ordering | L1028 (Trigger C) | tracker entry | dispatch | - | Agent | yes | procedure |
| F6-074 | **One carve-out:** a finding whose only fix path is `trivial-tweak` appends nothing. | precondition | L1028 (Trigger C) | - | fix-path depth tags | - | none | yes | procedure |
| F6-075 | A pick among two or more paths always appends, even when every path is shallow. | invariant | L1028 (Trigger C) | tracker entry | fix-path count | - | none | yes | procedure |
| F6-076 | Set `Decision: Orchestrator picked path (x) — highest-quality`, where `(x)` is the chosen path's letter. | field-or-template | L1028 (Trigger C) | `Decision` value | chosen path | - | none | yes | procedure |
| F6-077 | Set `Rationale:` to **the orchestrator's own one-line reason for preferring that path over the others** (why it is the smallest internally-consistent complete change), not merely the rule name. | field-or-template | L1028 (Trigger C) | `Rationale` content | orchestrator reasoning | - | none | yes | procedure |
| F6-078 | A bare rule name gives Section 8's challenge nothing to push against. | rationale-only | L1028 (Trigger C) | - | - | Section 8 | none | yes | rationale |
| F6-079 | Set `Follow-up Issue: none` on a Trigger C entry. | field-or-template | L1028 (Trigger C) | `Follow-up Issue` value | - | - | none | yes | procedure |
| F6-080 | **Row 6 is this trigger's only firing site.** | invariant | L1030 (Trigger C) | - | - | row 6 | none | yes | procedure |
| F6-081 | A `blocker` routed to the scope-bounding gate is user-picked, not an ungated route; write no Trigger C entry for it. | precondition | L1030 (Trigger C) | - | finding severity | scope-bounding gate | none | yes | procedure |
| F6-082 | Trigger D is the single owner of all post-completion-override tracker writes, fired from Section 8's post-completion review. | invariant | L1032 (Trigger D) | tracker entry or in-place update | Section 8 gate results | Section 8 | none | yes | procedure |
| F6-083 | Trigger D covers **both** the SR-6.7 ungated-route recovery gate AND the SR-4.6 under-enumeration analog recovery gate. | definition | L1032 (Trigger D) | - | - | SR-6.7, SR-4.6 | none | yes | procedure |
| F6-084 | Trigger D choice labels are byte-identical to the recovery-gate choices so they line up. | invariant | L1032 (Trigger D) | - | - | SR-6.7, SR-4.6 | none | yes | procedure |
| F6-085 | SR-6.7 `Accept the misjudgment and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the post-completion flow continues. | choice-set | L1035 (Trigger D, SR-6.7) | tracker entry | AskUserQuestion result | SR-6.7 | AskUserQuestion | yes | procedure |
| F6-086 | On SR-6.7 Accept, set `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)`. | field-or-template | L1035 (Trigger D, SR-6.7) | `Decision` value | - | - | none | yes | procedure |
| F6-087 | On SR-6.7 Accept, set `Rationale:` to the post-completion reviewer's challenge text. | field-or-template | L1035 (Trigger D, SR-6.7) | `Rationale` content | reviewer challenge text | - | none | yes | procedure |
| F6-088 | SR-6.7 `File follow-up Issue to revisit the depth decision` → **NO new entry is appended.** | choice-set | L1036 (Trigger D, SR-6.7) | - | - | SR-6.7 | none | yes | procedure |
| F6-089 | On SR-6.7 File, the **ORIGINAL Trigger C entry**'s `Follow-up Issue` field is **UPDATED in place** to the new Issue ID. | field-or-template | L1036 (Trigger D, SR-6.7) | in-place update of `Follow-up Issue` | Trigger C entry, `/quo-file-issue` result | Trigger C | none | yes | procedure |
| F6-090 | An originating Trigger C entry always exists to amend because the depth misjudgment concerns a path routed without a gate. | rationale-only | L1036 (Trigger D, SR-6.7) | - | - | Trigger C | none | yes | rationale |
| F6-091 | SR-6.7 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks `Accept` / `File` again. | choice-set | L1037 (Trigger D, SR-6.7) | - | subsequent pick | SR-6.7 | AskUserQuestion | yes | procedure |
| F6-092 | SR-4.6 `Accept the under-enumeration and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the post-completion flow continues. | choice-set | L1039 (Trigger D, SR-4.6) | tracker entry | AskUserQuestion result | SR-4.6 | AskUserQuestion | yes | procedure |
| F6-093 | On SR-4.6 Accept, set `Decision: User accepted under-enumeration after post-completion challenge`. | field-or-template | L1039 (Trigger D, SR-4.6) | `Decision` value | - | - | none | yes | procedure |
| F6-094 | On SR-4.6 Accept, set `Rationale:` to the post-completion reviewer's under-enumeration challenge text. | field-or-template | L1039 (Trigger D, SR-4.6) | `Rationale` content | reviewer challenge text | - | none | yes | procedure |
| F6-095 | SR-4.6 `File follow-up Issue to surface the missing path` → file the follow-up Issue and capture its ID. | choice-set | L1040 (Trigger D, SR-4.6) | Issue ticket | `/quo-file-issue` result | SR-4.6, `/quo-file-issue` | bees | yes | procedure |
| F6-096 | On SR-4.6 File with **no original Trigger C entry to amend**, append a **new** entry with the under-enumeration `Decision` value and the new Issue ID in `Follow-up Issue`. | field-or-template | L1040 (Trigger D, SR-4.6) | tracker entry | Issue ID | Trigger C | none | yes | procedure |
| F6-097 | If the under-enumeration relates to an existing ungated-route finding with a Trigger C entry, **UPDATE that entry's `Follow-up Issue` in place** instead; append otherwise. | recovery | L1040 (Trigger D, SR-4.6) | in-place update or new entry | Trigger C entry | Trigger C, SR-6.7 File-branch | none | yes | procedure |
| F6-098 | SR-4.6 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again. | choice-set | L1041 (Trigger D, SR-4.6) | - | subsequent pick | SR-4.6 | AskUserQuestion | yes | procedure |
| F6-099 | Agents across Sections 3–6 may flag items as "address later", "defer to next phase", "pick up during a follow-up Issue", or similar inter-session deferrals. | definition | L1043 (7.5 gate intro) | - | agent reports | Section 3, Section 4, Section 5, Section 6 | none | no | procedure |
| F6-100 | Each deferred item arrives with a destination annotation per `agents/pm.md`'s Final report contract and `agents/analyst.md`'s `### Deferred refinements` block. | definition | L1043 (7.5 gate intro) | - | PM Final report, Analyst `### Deferred refinements` | `agents/pm.md`, `agents/analyst.md` | none | no | procedure |
| F6-101 | Record items not addressed inline as `defer-<short-suffix>` TaskList tasks per Section 4's TaskList naming convention. | name-class | L1043 (7.5 gate intro) | `defer-<short-suffix>` task | destination annotations | Section 4 TaskList naming convention | TaskList | yes | procedure |
| F6-102 | The `defer-*` recording sites are the Section 3 Analyst-Approve / Analyst-Revise consumption sites and the Section 5 may-ignore-feedback site. | definition | L1043 (7.5 gate intro) | - | - | Section 3 `### Deferred refinements` consumption paragraph, Section 5 | TaskList | no | procedure |
| F6-103 | This gate is the pre-handoff reconciliation that closes deferrals into durable inter-session carriers before yield (single), advance (batch), or Section 8. | definition | L1043 (7.5 gate intro) | durable carriers | active `defer-*` set | Section 8 | none | yes | procedure |
| F6-104 | **Step 0**: before Step 1's enumeration, walk three additional surfaces and **create a corresponding `defer-*` TaskList task for any item that does not already have one**. | command | L1045 (Step 0) | `defer-*` tasks | three surfaces | Step 1, Section 3, Section 5 | TaskList | unknown | procedure |
| F6-105 | Surface 1: **Section 5's per-Issue `**Ignored Review Feedback**` summary field**; each non-`None` bullet maps to a `defer-*` task. | definition | L1047 (Step 0) | `defer-*` tasks | `**Ignored Review Feedback**` field | Section 5, Section 7 per-Issue summary | TaskList | unknown | procedure |
| F6-106 | **This surface does not exist on the aborted path**: `#### Aborted-Issue close-out` invokes the gate without Section 7 step 4, so skip surface 1 there. | precondition | L1047 (Step 0) | - | invocation path | `#### Aborted-Issue close-out`, Section 7 step 4 | none | no | procedure |
| F6-107 | Do not treat surface 1's absence on the aborted path as an empty active set. | invariant | L1047 (Step 0) | - | - | - | none | no | procedure |
| F6-108 | Surfaces 2 and 3 still apply on the aborted path: the Analyst's block exists whenever Section 3 ran; a PM Final report exists whenever a Phase C PM returned before the abort. | precondition | L1047 (Step 0) | - | Analyst block, PM Final report | Section 3, Phase C | none | no | procedure |
| F6-109 | Surface 2: **PM Agent's Final report deferred items**; every item with `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task. | definition | L1048 (Step 0) | `defer-*` tasks | PM Final report | `agents/pm.md` Final report contract | TaskList | yes | procedure |
| F6-110 | Skip PM items annotated `addressed-now-in-this-Task` because they were addressed inline. | precondition | L1048 (Step 0) | - | destination annotation | - | none | yes | procedure |
| F6-111 | Surface 3: **Analyst's `### Deferred refinements` block**; every non-`None` bullet with `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task. | definition | L1049 (Step 0) | `defer-*` tasks | Analyst structured return | `agents/analyst.md` | TaskList | no | procedure |
| F6-112 | Skip Analyst bullets annotated `addressed-now-in-this-Issue`. | precondition | L1049 (Step 0) | - | destination annotation | - | none | no | procedure |
| F6-113 | The Section 3 Approve / Revise consumption paragraph is the load-bearing source for Analyst items; the sweep is defense-in-depth. | rationale-only | L1049 (Step 0) | - | - | Section 3 | none | no | rationale |
| F6-114 | The upstream record-creating instructions (Section 3 consumption paragraph, Section 5 may-ignore site) are load-bearing; Step 0 is the safety net for orchestrators that miss them. | rationale-only | L1051 (Step 0) | - | - | Section 3, Section 5 | none | unknown | rationale |
| F6-115 | After the retroactive reconcile, every deferred item from the three surfaces is in the active `defer-*` set, so Step 1 sees the canonical view. | invariant | L1051 (Step 0) | canonical active set | Step 0 output | Step 1 | TaskList | unknown | procedure |
| F6-116 | **Per-Issue firing**: the gate fires at the end of every Issue on **both** boundary paths; it has two invocation sites, not one. | invariant | L1053 (Per-Issue firing) | gate fire | Issue boundary | - | none | no | procedure |
| F6-117 | **Fixed path**: fire between Section 7's mark-done-and-commit step and the per-Issue advance (next Issue in batch mode, Section 8 in single mode). | ordering | L1055 (Per-Issue firing) | gate fire | Section 7 mark-done-and-commit | Section 7, Section 8 | none | no | procedure |
| F6-118 | **Aborted path**: fire from `#### Aborted-Issue close-out` step 2, after that close-out's prefix sweep of this Issue's TaskList tasks and before the Issue-boundary state-externalization checkpoint. | ordering | L1056 (Per-Issue firing) | gate fire | `#### Aborted-Issue close-out` step 2 | `#### Aborted-Issue close-out`, Issue-boundary state-externalization checkpoint | TaskList | no | procedure |
| F6-119 | On the aborted path the Issue stays `open` with no commit, but pre-abort deferrals are equally stranded and this gate moves each into a durable carrier. | definition | L1056 (Per-Issue firing) | durable carriers | pre-abort `defer-*` tasks | - | none | no | procedure |
| F6-120 | The Step 3 hard-stop applies unchanged on the aborted path. | invariant | L1056 (Per-Issue firing) | - | - | Step 3 | none | no | procedure |
| F6-121 | The per-Issue firing scopes the active set to **deferrals surfaced during this Issue only**. | invariant | L1058 (Per-Issue firing) | scoped active set | `defer-*` tasks | - | TaskList | yes | procedure |
| F6-122 | Prior Issues' deferrals were closed at their own gate; per-batch accumulation would surprise the user and defeat per-Issue close-out discipline. | rationale-only | L1058 (Per-Issue firing) | - | - | - | none | yes | rationale |
| F6-123 | **Batch end-of-run firing**: in batch / `all` mode, fire the gate again between the last Issue's Section 7.5 close-out and Section 8. | ordering | L1060 (Batch end-of-run firing) | gate fire | batch exhaustion | Section 7.5, Section 8 | none | unknown | procedure |
| F6-124 | The end-of-batch firing catches deferrals surfaced *between* Issues (inter-Issue advance boundary, batch-level reconciliation) belonging to no per-Issue gate. | definition | L1060 (Batch end-of-run firing) | - | between-Issue deferrals | - | none | unknown | procedure |
| F6-125 | The end-of-batch active set is typically empty; the firing is a defensive sweep, and `Deferral hygiene (batch close): no deferred items.` is the expected output. | field-or-template | L1060 (Batch end-of-run firing) | console line | active set | - | none | unknown | procedure |
| F6-126 | **Step 1**: scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. | command | L1062 (Step 1) | active set | TaskList | - | TaskList | yes | procedure |
| F6-127 | If the active set is empty on a per-Issue firing, emit the one-line console message `Deferral hygiene: no deferred items.`. | field-or-template | L1062 (Step 1) | console line | active set | - | none | yes | procedure |
| F6-128 | If the active set is empty on an end-of-batch firing, emit `Deferral hygiene (batch close): no deferred items.`. | field-or-template | L1062 (Step 1) | console line | active set | - | none | unknown | procedure |
| F6-129 | After the empty-set message, advance per the firing-mode rules (per-Issue / end-of-batch). | ordering | L1062 (Step 1) | advance | firing mode | Per-Issue firing, Batch end-of-run firing | none | yes | procedure |
| F6-130 | **Step 2**: when the active set is non-empty, surface it as numbered markdown, one bullet per `defer-*` task with its `metadata.activity` text as the body. | relay | L1064 (Step 2) | numbered list to user | `defer-*` tasks' `metadata.activity` | - | TaskList | yes | procedure |
| F6-131 | **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 4's TaskList naming convention's gate-task entry). | ordering | L1064 (Step 2) | `gate-askuserquestion-<short-suffix>` task | - | Section 4 TaskList naming convention | TaskList | yes | procedure |
| F6-132 | **Then** call `AskUserQuestion` with the finite choices in the same turn. | gate | L1064 (Step 2) | AskUserQuestion fire | F6-131 | - | AskUserQuestion | yes | procedure |
| F6-133 | Mark the `gate-*` task `completed` the moment the answer is consumed and routing into Fix / File / Encode begins. | ordering | L1064 (Step 2) | status flip `completed` | AskUserQuestion result | - | TaskList | yes | procedure |
| F6-134 | The Step 2 choice set is `Fix in this session`, `File as issue tickets`, `Encode in an existing ticket body`. | choice-set | L1066-L1068 (Step 2) | - | - | - | AskUserQuestion | yes | procedure |
| F6-135 | `Fix in this session`: re-dispatch the appropriate implementer / reviewer Agents per Section 4's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch. | choice-set | L1066 (Step 2, Fix) | Agent dispatch or ticket-body update | deferred item | Section 4 dispatch shape, Encode branch | Agent, bees | yes | procedure |
| F6-136 | After each Fix item is resolved, mark its `defer-*` task `completed` with `metadata.activity` updated to log the resolution path. | ordering | L1066 (Step 2, Fix) | status flip + `metadata.activity` | resolution | - | TaskList | yes | procedure |
| F6-137 | `File as issue tickets`: for each item invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body. | choice-set | L1067 (Step 2, File) | Issue ticket | deferred item description | `/quo-file-issue` | bees | yes | procedure |
| F6-138 | The precedent for inline-Skill-tool dispatch is Section 1's URL-resolution sub-step. | rationale-only | L1067 (Step 2, File) | - | - | Section 1 URL-resolution sub-step | none | no | rationale |
| F6-139 | Mark each File item's `defer-*` task `completed` once `/quo-file-issue` returns successfully and the created Issue ID is captured. | ordering | L1067 (Step 2, File) | status flip `completed` | `/quo-file-issue` result | `/quo-file-issue` | TaskList | yes | procedure |
| F6-140 | `Encode in an existing ticket body`: valid destinations are a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass. | choice-set | L1068 (Step 2, Encode) | ticket-body update | user mapping | - | bees, Agent | yes | procedure |
| F6-141 | Append a `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body. | field-or-template | L1068 (Step 2, Encode) | ticket-body section | deferred item | - | none | no | procedure |
| F6-142 | Run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update. | command | L1068, L1075, L1083 (Step 2, Encode) | ticket update | body-file | - | bees, Bash | yes | procedure |
| F6-143 | `<YYYY-MM-DD HH:MM>` is the current local date and time authored into the body-file as a string from your own clock via the `Write` tool. | invariant | L1068 (Step 2, Encode) | heading timestamp | own clock | - | none | yes | procedure |
| F6-144 | Do not add a `date` / `Get-Date` snippet to compute the heading timestamp. | invariant | L1068 (Step 2, Encode) | - | - | - | none | yes | procedure |
| F6-145 | Keep the `## Deferred from /quo-fix-issue run` stem verbatim; only append the parenthesized timestamp suffix; do not simplify to a bare heading. | invariant | L1068 (Step 2, Encode) | heading text | - | - | none | no | procedure |
| F6-146 | The suffix lets multiple Encodes to the same ticket body across runs sit side-by-side with distinguishable headings. | rationale-only | L1068 (Step 2, Encode) | - | - | - | none | yes | rationale |
| F6-147 | Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir. | command | L1068 (Step 2, Encode) | scratch body-file | revised body | scratch-file convention | none | yes | procedure |
| F6-148 | **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode, i.e. `bees-body-<defer-N>.md`. | name-class | L1068, L1073, L1081 (Step 2, Encode) | scratch filename | triggering `defer-N` task name | - | TaskList | yes | procedure |
| F6-149 | Example: the encode triggered by `defer-3` writes `bees-body-defer-3.md`. | example | L1068, L1074, L1082 (Step 2, Encode) | - | - | - | none | yes | example |
| F6-150 | Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under the active `defer-*` set, and ties the file to its TaskList progenitor. | rationale-only | L1068 (Step 2, Encode) | - | - | - | none | yes | rationale |
| F6-151 | POSIX Encode snippet: `mkdir -p /tmp/.quorum`, write `/tmp/.quorum/bees-body-<defer-N>.md` via `Write`, then `bees update-ticket --ids <ticket-id> --body-file <path>`. | command | L1070-L1076 (Step 2, Encode) | directory, body-file, ticket update | - | - | Bash, bees | yes | procedure |
| F6-152 | Windows Encode snippet: `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`, write `$env:TEMP\.quorum\bees-body-<defer-N>.md` via `Write`, then `bees update-ticket --ids <ticket-id> --body-file <path>`. | command | L1078-L1084 (Step 2, Encode) | directory, body-file, ticket update | - | - | Bash, bees | yes | procedure |
| F6-153 | Do NOT remove the temp file after the bees command exits. | invariant | L1086 (Step 2, Encode) | - | scratch-file convention | - | none | yes | procedure |
| F6-154 | Files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. | rationale-only | L1086 (Step 2, Encode) | - | - | - | none | yes | rationale |
| F6-155 | Mark each Encode item's `defer-*` task `completed` once the `bees update-ticket` update succeeds. | ordering | L1086 (Step 2, Encode) | status flip `completed` | bees result | - | TaskList, bees | yes | procedure |
| F6-156 | **Follow-up commit** runs after all Encode writes in this gate firing have landed. | ordering | L1088 (Follow-up commit) | commit | Encode writes | - | git | yes | procedure |
| F6-157 | On the **fixed** path a per-Issue commit already exists (Section 7 step 2); on the **aborted** path the Issue contributes **no** per-issue commit. | definition | L1088 (Follow-up commit) | - | invocation path | Section 7 step 2, `#### Aborted-Issue close-out` | git | no | procedure |
| F6-158 | Do not rest the follow-up commit on a per-Issue commit having landed; its premise is only that `bees update-ticket --body-file` writes persist on-disk changes not swept into any prior commit. | invariant | L1088 (Follow-up commit) | - | hive-directory / PRD/SDD changes | - | git, bees | no | procedure |
| F6-159 | Unswept Encode writes would leave the working tree dirty when the skill yields (per-Issue) or advances (end-of-batch). | rationale-only | L1088 (Follow-up commit) | - | - | - | git | yes | rationale |
| F6-160 | The commit stages only the resolved in-repo hive paths and the explicit `--doc-path` arguments, committed **conditionally** on there being staged changes. | invariant | L1088 (Follow-up commit) | staged set | hive paths, `--doc-path` | - | git | yes | procedure |
| F6-161 | An aborted Issue with no Encode writes stages nothing and produces no commit; this is the correct outcome, not a gap. | invariant | L1088 (Follow-up commit) | - | - | - | git | no | procedure |
| F6-162 | The aborted Issue's uncommitted fix-in-progress is never swept in, since it is neither a hive path nor a `--doc-path`. | invariant | L1088 (Follow-up commit) | - | - | - | git | no | procedure |
| F6-163 | Produce one follow-up commit per gate firing covering all Encode writes from that firing, not one per Encode item. | invariant | L1088 (Follow-up commit) | one commit | Encode writes | - | git | yes | procedure |
| F6-164 | Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (same pattern as Section 7 step 2's commit step). | command | L1088 (Follow-up commit) | hive paths | `bees list-hives` output | Section 7 step 2 | bees | yes | procedure |
| F6-165 | `git add` each hive path that lives inside this repo. | command | L1088 (Follow-up commit) | staged hive paths | resolved hive paths | - | git | yes | procedure |
| F6-166 | Additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations. | command | L1088 (Follow-up commit) | staged doc paths | CLAUDE.md `## Documentation Locations` | CLAUDE.md `## Documentation Locations` | git | yes | procedure |
| F6-167 | Commit only if `git diff --cached` shows staged changes; skip the commit rather than producing an empty one. | precondition | L1088 (Follow-up commit) | commit or skip | `git diff --cached` | - | git | yes | procedure |
| F6-168 | Commit subject contract: `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded`. | field-or-template | L1088 (Follow-up commit) | commit subject | `<N>` | - | git | no | procedure |
| F6-169 | **`<N>` counts deferral items, not tickets** — the count of `defer-*` items routed to Encode in this firing, the same value passed as the helper's `--count`. | invariant | L1088 (Follow-up commit) | `<N>` | Encode routing | `--count` | none | yes | procedure |
| F6-170 | The follow-up-commit workflow is encapsulated in the bundled helper `hive_commit.py`; run it as a single literal Bash tool call. | command | L1090 (Follow-up commit) | commit | `hive_commit.py` | - | Bash, git, bees | yes | procedure |
| F6-171 | The helper resolves Plans/Specs/Issues hive paths, `git add`s in-repo hive paths and `--doc-path` paths, commits only if staged, and prints `skipped: nothing staged` otherwise. | definition | L1090 (Follow-up commit) | commit or `skipped: nothing staged` | hive paths, `--doc-path` | - | Bash, git, bees | yes | procedure |
| F6-172 | Out-of-repo hives require no git action because `bees update-ticket` already persisted their update. | definition | L1090 (Follow-up commit) | - | hive location | - | bees | yes | procedure |
| F6-173 | **Do NOT blindly `git add -A`**; other agents or processes may have in-flight working-tree changes (same anti-pattern as Section 7 step 2). | invariant | L1090 (Follow-up commit) | - | - | Section 7 step 2 | git | yes | procedure |
| F6-174 | `hive_commit.py` is shipped by `/quo-execute`; this skill consumes it as a *sibling* bundled script. | definition | L1092 (Resolving the helper path) | - | - | `/quo-execute` | none | no | procedure |
| F6-175 | Resolve the helper path at runtime as `<this skill's base directory>/../quo-execute/scripts/hive_commit.py`. | command | L1092 (Resolving the helper path) | helper path | skill base directory | `/quo-execute` | none | no | procedure |
| F6-176 | The base directory is shown in the skill invocation header (e.g. `Base directory for this skill: /Users/.../quo-fix-issue`). | definition | L1092 (Resolving the helper path) | - | skill invocation header | - | none | no | procedure |
| F6-177 | Use the `..` traversal pattern to reach the sibling skill, matching the sibling-resolution discipline used for `scoped_marker_resolver.py`. | invariant | L1092 (Resolving the helper path) | - | - | `scoped_marker_resolver.py` | none | no | procedure |
| F6-178 | On Windows the helper path is `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py`. | command | L1092 (Resolving the helper path) | helper path | skill base directory | `/quo-execute` | none | no | procedure |
| F6-179 | Invoke the helper with `--skill quo-fix-issue`. | command | L1094 (Resolving the helper path) | helper arg | - | - | Bash | no | procedure |
| F6-180 | Invoke the helper with `--count <N>`, matching the commit-subject contract's `<N>`. | command | L1094 (Resolving the helper path) | helper arg | `<N>` | F6-168 | Bash | yes | procedure |
| F6-181 | Pass one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`); omit entirely when none. | command | L1094 (Resolving the helper path) | helper arg | CLAUDE.md `## Documentation Locations` | CLAUDE.md `## Documentation Locations` | Bash | yes | procedure |
| F6-182 | POSIX invocation: `python3 "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`. | command | L1096-L1099 (Resolving the helper path) | commit | helper path | - | Bash | no | procedure |
| F6-183 | Windows invocation: `python "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]`. | command | L1101-L1104 (Resolving the helper path) | commit | helper path | - | Bash | no | procedure |
| F6-184 | After the helper lands the commit or prints `skipped: nothing staged`, proceed to Step 3. | ordering | L1106 (Resolving the helper path) | advance | helper output | Step 3 | Bash | yes | procedure |
| F6-185 | The three options are mutually-non-exclusive at the active-set level: the user may pick one overall or route different items to different options. | definition | L1108 (Step 2) | - | user reply | - | AskUserQuestion | yes | procedure |
| F6-186 | Example per-item routing reply: "fix items 1 and 2 now, file 3 as an Issue". | example | L1108 (Step 2) | - | - | - | none | yes | example |
| F6-187 | Every `defer-*` task in the active set **MUST** be `completed` by the end of this gate, whatever the routing. | invariant | L1108 (Step 2) | all `defer-*` `completed` | active set | Step 3 | TaskList | yes | procedure |
| F6-188 | For per-item routing the user selects `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`); the orchestrator parses the reply and closes out each `defer-*` task accordingly. | gate | L1108 (Step 2) | per-item routing | free-text reply | - | AskUserQuestion, TaskList | yes | procedure |
| F6-189 | **Step 3**: until every `defer-*` task is `completed`, the skill cannot advance past this gate. | invariant | L1110 (Step 3) | block | active set | - | TaskList | yes | procedure |
| F6-190 | On per-Issue firing the next Issue (batch) or Section 8 (single) is blocked; on end-of-batch firing Section 8 is blocked, until the active set is empty. | invariant | L1110 (Step 3) | block | firing mode | Section 8 | none | yes | procedure |
| F6-191 | A deferral important enough to surface during the run is important enough to encode in a durable carrier before the run ends. | rationale-only | L1110 (Step 3) | - | - | - | none | yes | rationale |
| F6-192 | If chosen options fail to close a subset (e.g. `/quo-file-issue` cancelled at a gate, or `bees update-ticket` errors), surface the still-active `defer-*` tasks via `AskUserQuestion` and re-run the gate until empty. | recovery | L1110 (Step 3) | re-fired gate | failed routing results | `/quo-file-issue` | AskUserQuestion, TaskList, bees | yes | procedure |
| F6-193 | The fresh-session-per-phase recommendation at run close-out is preserved verbatim; this gate sits before that handoff prose and does not replace it. | invariant | L1112 (7.5 close) | - | - | run close-out handoff prose | none | yes | procedure |

## Anchors defined here

Headings:

- L979 `### 7.5 Before handoff — deferral hygiene`
- L983 `#### Session-scoped compromise tracker`
- L1020 `#### Compromise-tracker append triggers`

Bolded phrases (verbatim):

- L985 **session-scoped compromise tracker**
- L985 **canonical definition site**
- L987 **Tracker file path and naming.**
- L987 **once at the start of the run**
- L1001 **Entry shape.**
- L1001 **1-based counter scoped to the current run's tracker file**
- L1006 **Finding (verbatim):**
- L1007 **Fix paths surfaced by reviewer:**
- L1011 **Decision:**
- L1012 **Rationale:**
- L1013 **Follow-up Issue:**
- L1016 **Finding (verbatim)**
- L1016 **Fix paths surfaced by reviewer**
- L1016 **Decision**
- L1016 **Rationale**
- L1016 **Follow-up Issue**
- L1016 **two**
- L1018 **Persistence.**
- L1018 **start of each run**
- L1018 **NEVER appended to**
- L1024 **Trigger A — Defer to follow-up Issue at either gate.**
- L1024 **IMMEDIATELY AFTER**
- L1024 **BEFORE**
- L1024 **Name in `Rationale` which remaining enumerated path shipped as the soft fix**
- L1024 **none did**
- L1024 **On a `blocker` deferral the narrowing takes that slot**
- L1024 **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger**
- L1024 **On a `blocker`-severity finding this branch is reachable only as Defer-with-narrowing, at either gate**
- L1024 **narrowing record**
- L1026 **Trigger B — Accept the limitation at the scope-bounding gate.**
- L1026 **IMMEDIATELY AFTER**
- L1026 **BEFORE**
- L1026 **Unreachable for a `blocker`-severity finding**
- L1028 **Trigger C — ungated route (the orchestrator's own path pick).**
- L1028 **no gate**
- L1028 **MOMENT of implementer dispatch**
- L1028 **row 6**
- L1028 **SAME LOGICAL BLOCK as that dispatch**
- L1028 **One carve-out:**
- L1028 **the orchestrator's own one-line reason for preferring that path over the others**
- L1030 **Row 6 is this trigger's only firing site.**
- L1032 **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).**
- L1032 **both**
- L1034 **SR-6.7 ungated-route recovery gate:**
- L1035 **NEW**
- L1035 **IMMEDIATELY AFTER**
- L1035 **BEFORE**
- L1036 **NO new entry is appended.**
- L1036 **ORIGINAL Trigger C entry**
- L1036 **UPDATED in place**
- L1037 **DEFER**
- L1038 **SR-4.6 under-enumeration analog recovery gate (same Trigger D mechanism, under-enumeration variant):**
- L1039 **NEW**
- L1039 **IMMEDIATELY AFTER**
- L1039 **BEFORE**
- L1040 **no original Trigger C entry to amend**
- L1040 **new**
- L1040 **UPDATE that entry's `Follow-up Issue` in place**
- L1041 **DEFER**
- L1045 **Step 0 — Retroactive ledger reconciliation (safety net).**
- L1045 **create a corresponding `defer-*` TaskList task for any item that does not already have one**
- L1047 **Section 5's per-Issue `**Ignored Review Feedback**` summary field**
- L1047 **This surface does not exist on the aborted path:**
- L1048 **PM Agent's Final report deferred items**
- L1049 **Analyst's `### Deferred refinements` block**
- L1053 **Per-Issue firing.**
- L1053 **both**
- L1055 **Fixed path**
- L1056 **Aborted path**
- L1058 **deferrals surfaced during this Issue only**
- L1060 **Batch end-of-run firing.**
- L1062 **Step 1 — Enumerate the active deferral ledger.**
- L1064 **Step 2 — Surface the active set and gate the user choice.**
- L1064 **First**
- L1064 **then**
- L1066 **Fix in this session**
- L1067 **File as issue tickets**
- L1068 **Encode in an existing ticket body**
- L1068 **Filename**
- L1088 **Follow-up commit (after all Encode writes in this gate firing have landed).**
- L1088 **fixed**
- L1088 **aborted**
- L1088 **no**
- L1088 **conditionally**
- L1088 **`<N>` counts deferral items, not tickets**
- L1090 **Do NOT blindly `git add -A`**
- L1092 **Resolving the helper path (sibling-skill resolution).**
- L1108 **MUST**
- L1110 **Step 3 — Hard-stop on a non-empty active set.**

Other referenceable literals (not bold, but named by other text): `compromises-YYYYMMDD-HHMM-<short-suffix>.md` (L987); `## Compromise <n>` (L1004); `Deferral hygiene: no deferred items.` and `Deferral hygiene (batch close): no deferred items.` (L1060, L1062); `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` (L1068); `bees-body-<defer-N>.md` (L1068); `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded` (L1088); `hive_commit.py` (L1090); `skipped: nothing staged` (L1090, L1106).

## Rationale-only spans

No whole line in this slice is rule-free (every paragraph is a single long line that mixes rules with justification). Rationale-only sub-spans within lines:

- L985 (second half of first sentence, "so a legitimately-accepted compromise … new baseline") — why the tracker exists.
- L987 ("The timestamp prefix makes … specific session.") — why timestamp prefix.
- L1016 (final clause, "because Trigger D … which kind fired") — why two override values.
- L1024 ("Either way, the deferral … unfixed one.") — deferral plus shipped is one decision.
- L1028 ("since the rule name … push against") — why rationale, not rule name.
- L1036 (parenthetical) — why Trigger C entry always exists.
- L1049 (final sentence) — Section 3 source is load-bearing.
- L1051 (first sentence) — Step 0 is defense-in-depth.
- L1058 (second sentence) — why per-Issue scoping.
- L1067 (parenthetical) — precedent for inline Skill dispatch.
- L1068 ("Reusing the triggering task's suffix … progenitor") — why reuse defer-N suffix.
- L1086 ("files under … known place") — why no cleanup.
- L1088 ("they would otherwise leave the working tree dirty …") — why commit is needed.
- L1110 ("This is the structural enforcement … run ends.") — why hard-stop.

Approximate total: 14 partial-line spans; zero full rationale-only lines.
