# Rule inventory — `skills/quo-execute/SKILL.md` Section 6.5 (L1116–L1237)

Slice: `### 6.5 Before handoff — deferral hygiene` — gate-contract preamble, `#### Session-scoped compromise tracker`, `#### Compromise-tracker append triggers` (A–D), the deferral-hygiene Steps 0–3 with Fix / File / Encode branches, scratch-file + `hive_commit.py` follow-up commit, and the handoff-preservation sentence.

Heading shorthand used in `Site`: `6.5` = `### 6.5 Before handoff — deferral hygiene`; `6.5/Tracker` = `#### Session-scoped compromise tracker`; `6.5/Triggers` = `#### Compromise-tracker append triggers`; `6.5/Step N` = the bolded `**Step N — …**` label under `### 6.5` (Steps are bold labels, not headings — nearest true heading is `### 6.5`).

| ID | Rule | Kind | Site | Produces | Consumes | Cross-refs | Env | Mirror | Class |
|---|---|---|---|---|---|---|---|---|---|
| E6-001 | Every `AskUserQuestion` firing in this gate goes through the two-step `TaskCreate` → `AskUserQuestion` contract. | gate | L1118 · 6.5 | `gate-askuserquestion-<short-suffix>` TaskList task | - | two-step `TaskCreate` → `AskUserQuestion` contract | TaskList, AskUserQuestion | unknown | procedure |
| E6-002 | The firings covered are Step 2's initial Fix / File / Encode choice plus any Step 3 re-fires when a routing branch failed to close out a subset of the active `defer-*` set. | definition | L1118 · 6.5 | - | active `defer-*` set | Step 2, Step 3 | none | unknown | procedure |
| E6-003 | First `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate. | name-class | L1118 · 6.5 | `gate-askuserquestion-<short-suffix>` task | - | - | TaskList | unknown | procedure |
| E6-004 | Use a distinct `<short-suffix>` per fire so Step 3 re-fires are not mistaken for the Step 2 first fire. | name-class | L1118 · 6.5 | distinct suffix per `gate-*` task | - | Step 2, Step 3 | TaskList | unknown | procedure |
| E6-005 | Then call `AskUserQuestion` in the same turn as the `TaskCreate`. | ordering | L1118 · 6.5 | AskUserQuestion dispatch | E6-003 task | - | AskUserQuestion, TaskList | unknown | procedure |
| E6-006 | Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed. | ordering | L1118 · 6.5 | `gate-*` status flip to `completed` | AskUserQuestion result | - | TaskList, AskUserQuestion | unknown | procedure |
| E6-007 | Maintain a **session-scoped compromise tracker**: a single markdown file accumulating one entry per accepted compromise across this run. | definition | L1122 · 6.5/Tracker | tracker file | - | - | none | yes | procedure |
| E6-008 | An accepted compromise is a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override. | definition | L1122 · 6.5/Tracker | - | - | - | none | yes | procedure |
| E6-009 | The tracker exists so an accepted compromise stays visible and challengeable rather than baked silently into the new baseline. | rationale-only | L1122 · 6.5/Tracker | - | - | - | none | yes | rationale |
| E6-010 | The four append triggers (A/B/C/D) are defined under "Compromise-tracker append triggers"; Section 6's post-completion review consumes the tracker as input. | definition | L1122 · 6.5/Tracker | - | tracker file | "Compromise-tracker append triggers", Section 6 | none | unknown | procedure |
| E6-011 | This subsection is the **canonical definition site** the trigger write-instructions reference by name. | definition | L1122 · 6.5/Tracker | - | - | - | none | unknown | procedure |
| E6-012 | Write the tracker under `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows) per the scratch-file convention. | command | L1124 · 6.5/Tracker | tracker file location | - | scratch-file convention | Bash | yes | procedure |
| E6-013 | Canonical tracker filename is `compromises-YYYYMMDD-HHMM-<short-suffix>.md`. | name-class | L1124 · 6.5/Tracker | tracker filename | - | - | none | yes | procedure |
| E6-014 | `YYYYMMDD-HHMM` is a UTC timestamp (e.g., `20260520-1714`) generated **once at the start of the run**. | name-class | L1124 · 6.5/Tracker | timestamp component | run start | - | none | yes | procedure |
| E6-015 | `<short-suffix>` is a short collision-resistant random string. | name-class | L1124 · 6.5/Tracker | suffix component | - | - | none | yes | procedure |
| E6-016 | The timestamp prefix makes tracker files debuggably identifiable across runs accumulated in `<tempdir>/.quorum/`; without it the user cannot map a file to a session. | rationale-only | L1124 · 6.5/Tracker | - | - | - | none | yes | rationale |
| E6-017 | Create the `.quorum` directory if absent: `mkdir -p /tmp/.quorum` (POSIX) / `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null` (PowerShell). | command | L1124-L1136 · 6.5/Tracker | `.quorum` dir | - | bash-etiquette, scratch-file conventions | Bash | yes | procedure |
| E6-018 | Author and append the tracker file via the `Write` tool — no shell redirect. | command | L1124-L1136 · 6.5/Tracker | tracker file contents | - | bash-etiquette convention | none | yes | procedure |
| E6-019 | Each accepted compromise appends one `## Compromise <n>` section to the tracker. | field-or-template | L1138-L1141 · 6.5/Tracker | `## Compromise <n>` section | - | - | none | yes | procedure |
| E6-020 | `<n>` is a **1-based counter scoped to the current run's tracker file**, NOT a globally unique identifier. | field-or-template | L1138 · 6.5/Tracker | `<n>` value | tracker file entry count | - | none | yes | procedure |
| E6-021 | The canonical entry shape is reproduced from the SDD Data models `#### Compromise tracker entry shape`. | definition | L1138 · 6.5/Tracker | - | - | SDD Data models `#### Compromise tracker entry shape` | none | yes | rationale |
| E6-022 | Field `- **Finding (verbatim):**` carries `<severity tag> <fix-path enumeration with depth tags> <description>`. | field-or-template | L1143, L1153 · 6.5/Tracker | `Finding (verbatim)` field | reviewer finding | - | none | yes | procedure |
| E6-023 | Field `- **Fix paths surfaced by reviewer:**` lists `(a) [depth:<depth>] <description>`, `(b) [depth:<depth>] <description>`, … each carrying its `[depth:<...>]` tag. | field-or-template | L1144-L1147, L1153 · 6.5/Tracker | `Fix paths surfaced by reviewer` field | reviewer enumeration | - | none | yes | procedure |
| E6-024 | Field `- **Decision:**` takes exactly one value from the `Decision` enum (E6-025–E6-030). | field-or-template | L1148, L1153 · 6.5/Tracker | `Decision` field | - | - | none | yes | procedure |
| E6-025 | `Decision` enum value: `User picked path (a)`, `User picked path (b)`, … (one per enumerated letter). | field-or-template | L1148 · 6.5/Tracker | `Decision` value | - | - | none | yes | procedure |
| E6-026 | `Decision` enum value: `User picked Defer to follow-up Issue`. | field-or-template | L1148 · 6.5/Tracker | `Decision` value | - | Trigger A | none | yes | procedure |
| E6-027 | `Decision` enum value: `User picked Accept the limitation`. | field-or-template | L1148 · 6.5/Tracker | `Decision` value | - | Trigger B | none | yes | procedure |
| E6-028 | `Decision` enum value: `Orchestrator picked path (x) — highest-quality`. | field-or-template | L1148 · 6.5/Tracker | `Decision` value | - | Trigger C | none | yes | procedure |
| E6-029 | `Decision` enum value: `User overrode auto-route after post-completion challenge (depth misjudgment)` (the SR-6.7 depth-misjudgment override). | field-or-template | L1148, L1153 · 6.5/Tracker | `Decision` value | - | SR-6.7, Trigger D | none | yes | procedure |
| E6-030 | `Decision` enum value: `User accepted under-enumeration after post-completion challenge` (the SR-4.6 under-enumeration analog override). | field-or-template | L1148, L1153 · 6.5/Tracker | `Decision` value | - | SR-4.6, Trigger D | none | yes | procedure |
| E6-031 | Field `- **Rationale:**` carries the user's stated reason if surfaced via `AskUserQuestion`, or on an ungated orchestrator pick the one-line reason that path was preferred. | field-or-template | L1149, L1153 · 6.5/Tracker | `Rationale` field | AskUserQuestion result or orchestrator reason | - | none | yes | procedure |
| E6-032 | On a `Defer to follow-up Issue` entry, `Rationale` also names which remaining enumerated path shipped as the soft fix, or that none did. | field-or-template | L1149, L1153 · 6.5/Tracker | `Rationale` content | soft-fix dispatch outcome | - | none | yes | procedure |
| E6-033 | On a blocker deferral, `Rationale` carries the narrowing record in place of the shipped-path statement. | field-or-template | L1149, L1153 · 6.5/Tracker | `Rationale` content | narrowing decision | - | none | yes | procedure |
| E6-034 | Field `- **Follow-up Issue:**` carries the ticket ID if filed via `/quo-file-issue`, else `none`. | field-or-template | L1150, L1153 · 6.5/Tracker | `Follow-up Issue` field | `/quo-file-issue` result | `/quo-file-issue` | none | yes | procedure |
| E6-035 | The entry has exactly five fields: **Finding (verbatim)**, **Fix paths surfaced by reviewer**, **Decision**, **Rationale**, **Follow-up Issue**. | definition | L1153 · 6.5/Tracker | - | - | - | none | yes | procedure |
| E6-036 | The `Decision` enum carries **two** post-completion-override values because Trigger D is the single owner of all post-completion-override writes regardless of which gate fired. | rationale-only | L1153 · 6.5/Tracker | - | - | Trigger D, SR-6.7, SR-4.6 | none | yes | rationale |
| E6-037 | The tracker, being a file-system artifact, persists across orchestrator-yield events within a single run inherently. | invariant | L1155 · 6.5/Tracker | - | tracker file | - | none | yes | rationale |
| E6-038 | Generate a fresh `YYYYMMDD-HHMM` + `<short-suffix>` at the **start of each run**; previous-run tracker files are **NEVER appended to** — each run writes its own new file. | invariant | L1155 · 6.5/Tracker | new tracker file per run | - | - | none | yes | procedure |
| E6-039 | Never delete the tracker file — do NOT instruct any `rm` / `Remove-Item` (scratch-file convention). | invariant | L1155 · 6.5/Tracker | - | - | scratch-file convention | none | yes | procedure |
| E6-040 | Four moments append tracker entries: Triggers A–C fire from the "Orchestrator discipline: routing review findings" section's gates / ungated dispatch; Trigger D fires from Section 6's post-completion review. | definition | L1159 · 6.5/Triggers | - | - | "Orchestrator discipline: routing review findings", Section 6 | none | unknown | procedure |
| E6-041 | Each trigger anchors to its gate by name; the write fires from the branch named in the trigger. | invariant | L1159 · 6.5/Triggers | - | - | - | none | unknown | procedure |
| E6-042 | **Trigger A** fires at the scope-bounding gate (part (c) of "### Orchestrator discipline: routing review findings") when the user picks `Defer to follow-up Issue`. | gate | L1161 · 6.5/Triggers | tracker entry | `Defer to follow-up Issue` choice | part (c), "### Orchestrator discipline: routing review findings" | AskUserQuestion | unknown | procedure |
| E6-043 | Append the Trigger A entry **IMMEDIATELY AFTER** `/quo-file-issue` returns successfully with the new Issue ID and **BEFORE** continuing with this round's soft-fix dispatch. | ordering | L1161 · 6.5/Triggers | tracker entry | `/quo-file-issue` return (Issue ID) | `/quo-file-issue` | none | unknown | procedure |
| E6-044 | Capture the follow-up Issue ID in the entry's `Follow-up Issue` field. | field-or-template | L1161 · 6.5/Triggers | `Follow-up Issue` value | `/quo-file-issue` Issue ID | - | none | unknown | procedure |
| E6-045 | Set `Decision: User picked Defer to follow-up Issue` on a Trigger A entry. | field-or-template | L1161 · 6.5/Triggers | `Decision` value | - | - | none | unknown | procedure |
| E6-046 | Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all (reachable at the routing-decision gate, whose `Defer` is offered whatever the path count). | field-or-template | L1161 · 6.5/Triggers | `Fix paths surfaced by reviewer` value | reviewer path count | routing-decision gate | none | unknown | procedure |
| E6-047 | **Name in `Rationale` which remaining enumerated path shipped as the soft fix** — by its letter — or that **none did**. | field-or-template | L1161 · 6.5/Triggers | `Rationale` content | soft-fix dispatch | - | none | unknown | procedure |
| E6-048 | "None did" applies in the single-path case at the scope-bounding gate and to any deferral at the routing-decision gate, whose `Defer` bullet ships nothing regardless of path count. | definition | L1161 · 6.5/Triggers | - | gate site, path count | scope-bounding gate, routing-decision gate | none | unknown | procedure |
| E6-049 | **On a `blocker` deferral the narrowing takes that slot**: record what was scoped down and why the blocker no longer describes what remains, in place of a letter or `none did`. | field-or-template | L1161 · 6.5/Triggers | `Rationale` narrowing record | narrowing decision | - | none | unknown | procedure |
| E6-050 | The deferral and what shipped in its place are one decision; an entry recording only the deferral cannot distinguish a soft-fixed finding from an unfixed one. | rationale-only | L1161 · 6.5/Triggers | - | - | - | none | unknown | rationale |
| E6-051 | **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger** on the same terms and with the same entry shape. | gate | L1161 · 6.5/Triggers | tracker entry | `Defer to follow-up Issue` choice at routing-decision gate | routing-decision gate | AskUserQuestion | unknown | procedure |
| E6-052 | The routing-decision gate offers `Defer` to any finding, and to a `blocker` only when part (c)'s two Defer conditions hold. | precondition | L1161 · 6.5/Triggers | - | severity, part (c) Defer conditions | part (c) | none | unknown | procedure |
| E6-053 | **On a `blocker`-severity finding this branch is reachable only as Defer-with-narrowing, at either gate** (part (c)'s severity rule, applied by part (d) on its own terms). | precondition | L1161 · 6.5/Triggers | - | severity | part (c), part (d) | none | unknown | procedure |
| E6-054 | A blocker-deferral entry MUST carry a **narrowing record** in `Rationale`: what was narrowed out of the change, and why the blocker no longer describes anything that ships. | invariant | L1161 · 6.5/Triggers | `Rationale` narrowing record | narrowing decision | - | none | unknown | procedure |
| E6-055 | A blocker deferral without a narrowing record is the shape every downstream consumer reads as a contract violation. | invariant | L1161 · 6.5/Triggers | - | - | - | none | unknown | rationale |
| E6-056 | **Trigger B** fires at the scope-bounding gate's `Accept the limitation` branch when the user picks `Accept the limitation`. | gate | L1163 · 6.5/Triggers | tracker entry | `Accept the limitation` choice | scope-bounding gate | AskUserQuestion | unknown | procedure |
| E6-057 | Append the Trigger B entry **IMMEDIATELY AFTER** `AskUserQuestion` returns the choice and **BEFORE** continuing without a fix. | ordering | L1163 · 6.5/Triggers | tracker entry | AskUserQuestion result | - | AskUserQuestion | unknown | procedure |
| E6-058 | Set `Decision: User picked Accept the limitation` on a Trigger B entry. | field-or-template | L1163 · 6.5/Triggers | `Decision` value | - | - | none | unknown | procedure |
| E6-059 | Set `Follow-up Issue: none` on a Trigger B entry. | field-or-template | L1163 · 6.5/Triggers | `Follow-up Issue` value | - | - | none | unknown | procedure |
| E6-060 | Trigger B is **Unreachable for a `blocker`-severity finding**, unconditionally — the gate's severity rule withholds this branch from blockers since accepting a blocker ships it. | precondition | L1163 · 6.5/Triggers | - | severity | scope-bounding gate severity rule | none | unknown | procedure |
| E6-061 | **Trigger C** has **no gate** — its write is wired into the dispatch step itself. | definition | L1165 · 6.5/Triggers | - | - | - | none | unknown | procedure |
| E6-062 | At the **MOMENT of implementer dispatch** for any finding part (a) routed by **row 6**, append the entry in the **SAME LOGICAL BLOCK as that dispatch** — not a separate post-gate block. | ordering | L1165 · 6.5/Triggers | tracker entry | row 6 routing, Step 1 path pick | part (a), row 6, Step 1 | Agent | unknown | procedure |
| E6-063 | **One carve-out:** a finding whose *only* fix path is `trivial-tweak` appends nothing. | precondition | L1165 · 6.5/Triggers | - | fix-path depth tags | - | none | unknown | procedure |
| E6-064 | A pick among two or more paths always appends a Trigger C entry, even when every path is shallow. | precondition | L1165 · 6.5/Triggers | tracker entry | path count | - | none | unknown | procedure |
| E6-065 | Set `Decision: Orchestrator picked path (x) — highest-quality`, where `(x)` is the chosen path's letter. | field-or-template | L1165 · 6.5/Triggers | `Decision` value | chosen path letter | - | none | unknown | procedure |
| E6-066 | Set `Rationale:` to **the orchestrator's own one-line reason for preferring that path over the others** — why it is the smallest internally-consistent complete change — not merely the fired rule's name. | field-or-template | L1165 · 6.5/Triggers | `Rationale` content | orchestrator judgement | - | none | unknown | procedure |
| E6-067 | A bare rule name gives Section 6's challenge nothing to push against. | rationale-only | L1165 · 6.5/Triggers | - | - | Section 6 | none | unknown | rationale |
| E6-068 | Set `Follow-up Issue: none` on a Trigger C entry. | field-or-template | L1165 · 6.5/Triggers | `Follow-up Issue` value | - | - | none | unknown | procedure |
| E6-069 | **Row 6 is this trigger's only firing site.** | invariant | L1167 · 6.5/Triggers | - | - | row 6 | none | unknown | procedure |
| E6-070 | A `blocker` routed to the scope-bounding gate still fires that gate; a user-picked path is not an ungated route, so no Trigger C entry is written for it. | precondition | L1167 · 6.5/Triggers | - | severity, user pick | scope-bounding gate | none | unknown | procedure |
| E6-071 | **Trigger D** is the single owner of all post-completion-override tracker writes, fired from Section 6's post-completion review. | invariant | L1169 · 6.5/Triggers | tracker entry / in-place update | Section 6 gate results | Section 6 | none | unknown | procedure |
| E6-072 | Trigger D covers **both** the SR-6.7 ungated-route recovery gate AND the SR-4.6 under-enumeration analog recovery gate. | definition | L1169 · 6.5/Triggers | - | - | SR-6.7, SR-4.6 | none | unknown | procedure |
| E6-073 | Trigger D's choice labels are byte-identical to the recovery-gate choices so they line up. | invariant | L1169 · 6.5/Triggers | - | - | SR-6.7, SR-4.6 gates | none | unknown | procedure |
| E6-074 | SR-6.7 `Accept the misjudgment and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the post-completion flow continues. | ordering | L1171-L1172 · 6.5/Triggers | new tracker entry | `Accept the misjudgment and proceed` choice | **SR-6.7 ungated-route recovery gate** | AskUserQuestion | unknown | procedure |
| E6-075 | On that entry set `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)`. | field-or-template | L1172 · 6.5/Triggers | `Decision` value | - | SR-6.7 | none | unknown | procedure |
| E6-076 | On that entry set `Rationale:` to the post-completion reviewer's challenge text. | field-or-template | L1172 · 6.5/Triggers | `Rationale` content | post-completion reviewer challenge | SR-6.7 | none | unknown | procedure |
| E6-077 | SR-6.7 `File follow-up Issue to revisit the depth decision` → **NO new entry is appended.**; UPDATE the **ORIGINAL Trigger C entry**'s `Follow-up Issue` field in place to the new Issue ID. | recovery | L1173 · 6.5/Triggers | in-place `Follow-up Issue` update | new Issue ID, originating Trigger C entry | Trigger C, SR-6.7 | none | unknown | procedure |
| E6-078 | An originating Trigger C entry always exists to amend, because the depth misjudgment concerns a path the in-flow reviewer surfaced and the orchestrator routed ungated. | rationale-only | L1173 · 6.5/Triggers | - | - | Trigger C | none | unknown | rationale |
| E6-079 | SR-6.7 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again; no write until a subsequent `Accept` / `File` pick. | ordering | L1174 · 6.5/Triggers | - | discussion outcome | SR-6.7 | none | unknown | procedure |
| E6-080 | SR-4.6 `Accept the under-enumeration and proceed` → append a **NEW** entry **IMMEDIATELY AFTER** the pick, **BEFORE** the post-completion flow continues. | ordering | L1175-L1176 · 6.5/Triggers | new tracker entry | `Accept the under-enumeration and proceed` choice | **SR-4.6 under-enumeration analog recovery gate** | AskUserQuestion | unknown | procedure |
| E6-081 | On that entry set `Decision: User accepted under-enumeration after post-completion challenge`. | field-or-template | L1176 · 6.5/Triggers | `Decision` value | - | SR-4.6 | none | unknown | procedure |
| E6-082 | On that entry set `Rationale:` to the post-completion reviewer's under-enumeration challenge text. | field-or-template | L1176 · 6.5/Triggers | `Rationale` content | reviewer challenge text | SR-4.6 | none | unknown | procedure |
| E6-083 | SR-4.6 `File follow-up Issue to surface the missing path` → file the follow-up Issue and capture its ID. | command | L1177 · 6.5/Triggers | Issue ticket, Issue ID | - | `/quo-file-issue` (implied), SR-4.6 | bees | unknown | procedure |
| E6-084 | Since generally **no original Trigger C entry to amend** exists, append a **new** entry with the under-enumeration `Decision` value and the new Issue ID in `Follow-up Issue`. | field-or-template | L1177 · 6.5/Triggers | new tracker entry | Issue ID | SR-4.6, Trigger C | none | unknown | procedure |
| E6-085 | If the under-enumeration relates to an existing ungated-route finding (originating Trigger C entry exists), mirror the SR-6.7 File-branch and **UPDATE that entry's `Follow-up Issue` in place**; append otherwise. | recovery | L1177 · 6.5/Triggers | in-place `Follow-up Issue` update | originating Trigger C entry | SR-6.7 File-branch, Trigger C | none | unknown | procedure |
| E6-086 | SR-4.6 `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again. | ordering | L1178 · 6.5/Triggers | - | discussion outcome | SR-4.6 | none | unknown | procedure |
| E6-087 | Section 6's Fix / File / Skip gate handles only the fresh-eyes generalist sweep's findings. | definition | L1180 · 6.5 | - | - | Section 6 | none | unknown | procedure |
| E6-088 | Every inter-session deferral ("address later", "defer to next phase", "pick up during a follow-up Issue", or similar) not addressed inline MUST have been recorded as a `defer-<short-suffix>` TaskList task. | invariant | L1180 · 6.5 | - | `defer-<short-suffix>` tasks | Sections 3–4, Section 5, Section 3's TaskList naming convention, Section 4.1, PM Agent | TaskList | unknown | procedure |
| E6-089 | This gate is the pre-handoff reconciliation step that closes `defer-*` items out into durable inter-session carriers. | definition | L1180 · 6.5 | - | active `defer-*` set | - | none | unknown | procedure |
| E6-090 | Section 7's "show ignored feedback" prose stays as the display layer; this gate ensures the active set is empty before that display fires. | ordering | L1182 · 6.5 | - | - | Section 7 | none | unknown | procedure |
| E6-091 | Section 4.1's `**Ignored Review Feedback**` field and Section 5's may-ignore-feedback site each instruct creating a `defer-<short-suffix>` task at the moment an item is ignored. | definition | L1184 · 6.5/Step 0 | - | - | Section 4.1, Section 5, `**Ignored Review Feedback**` | TaskList | unknown | procedure |
| E6-092 | **Step 0**: before Step 1's enumeration, walk every per-Task summary the orchestrator produced during this run. | command | L1184 · 6.5/Step 0 | - | per-Task summaries | Step 1 | none | unknown | procedure |
| E6-093 | Walk every PM Final report's deferred items per `agents/pm.md`'s Final report contract. | command | L1184 · 6.5/Step 0 | - | PM Final reports | `agents/pm.md` Final report contract | none | unknown | procedure |
| E6-094 | Every item annotated `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` maps to a `defer-*` task. | definition | L1184 · 6.5/Step 0 | `defer-*` task | PM destination annotations | `agents/pm.md` | TaskList | unknown | procedure |
| E6-095 | Skip items annotated `addressed-now-in-this-Task` — they were addressed inline. | precondition | L1184 · 6.5/Step 0 | - | PM destination annotations | `agents/pm.md` | none | unknown | procedure |
| E6-096 | Also walk any orchestrator-side ignored item that did not flow through those two surfaces. | command | L1184 · 6.5/Step 0 | - | orchestrator-side ignored items | Section 4.1, Section 5 | none | unknown | procedure |
| E6-097 | **Create a corresponding `defer-*` TaskList task for any item that does not already have one.** | command | L1184 · 6.5/Step 0 | `defer-*` TaskList task | walk results | - | TaskList | unknown | procedure |
| E6-098 | Section 4.1 / Section 5 record-creating instructions are the load-bearing source; Step 0 is the defense-in-depth safety net for missed instructions or off-site ignores. | rationale-only | L1184 · 6.5/Step 0 | - | - | Section 4.1, Section 5 | none | unknown | rationale |
| E6-099 | After the retroactive reconcile, every ignored item is represented in the active `defer-*` set and Step 1 sees the canonical view. | invariant | L1184 · 6.5/Step 0 | - | active `defer-*` set | Step 1 | TaskList | unknown | procedure |
| E6-100 | **Step 1**: scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. | command | L1186 · 6.5/Step 1 | active `defer-*` set | TaskList | - | TaskList | unknown | procedure |
| E6-101 | If the active set is empty, emit a one-line console message — recommended `Deferral hygiene: no deferred items.` — and proceed to Section 7 (Final Output). | relay | L1186 · 6.5/Step 1 | console message | active set (empty) | Section 7 (Final Output) | none | unknown | procedure |
| E6-102 | **Step 2**: when non-empty, surface the active set as numbered markdown, one bullet per `defer-*` task with its `metadata.activity` text as the body. | relay | L1188 · 6.5/Step 2 | numbered list to user | `defer-*` tasks' `metadata.activity` | - | TaskList | unknown | procedure |
| E6-103 | **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 3's TaskList naming convention's gate-task entry). | gate | L1188 · 6.5/Step 2 | `gate-askuserquestion-<short-suffix>` task | - | Section 3's TaskList naming convention | TaskList | unknown | procedure |
| E6-104 | **then** call `AskUserQuestion` with the finite choices `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body` in the same turn. | gate | L1188-L1192 · 6.5/Step 2 | AskUserQuestion dispatch | E6-103 task | - | AskUserQuestion | unknown | procedure |
| E6-105 | Mark the `gate-*` task `completed` the moment the user's answer is consumed and routing into Fix / File / Encode begins. | ordering | L1188 · 6.5/Step 2 | `gate-*` status flip | AskUserQuestion result | - | TaskList | unknown | procedure |
| E6-106 | Choice `Fix in this session`: re-dispatch implementer / reviewer Agents per Section 3's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch, resolving each item now. | choice-set | L1190 · 6.5/Step 2 | Agent dispatches / ticket updates | deferred items | Section 3's dispatch shape, Encode branch | Agent, bees | unknown | procedure |
| E6-107 | After each Fix item resolves, mark its `defer-*` task `completed` with `metadata.activity` updated to log the resolution path. | ordering | L1190 · 6.5/Step 2 | `defer-*` status flip + `metadata.activity` | resolution outcome | - | TaskList | unknown | procedure |
| E6-108 | Choice `File as issue tickets`: for each item invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body. | choice-set | L1191 · 6.5/Step 2 | Issue ticket per item | deferral description | `/quo-file-issue` | bees | unknown | procedure |
| E6-109 | The precedent for inline-Skill-tool dispatch is `/quo-fix-issue` Section 1's URL-resolution sub-step and `/quo-plan` Step 4b. | rationale-only | L1191 · 6.5/Step 2 | - | - | `/quo-fix-issue` Section 1, `/quo-plan` Step 4b | none | unknown | rationale |
| E6-110 | Mark each File-routed `defer-*` task `completed` once `/quo-file-issue` returns successfully and the created Issue ID is captured. | ordering | L1191 · 6.5/Step 2 | `defer-*` status flip | `/quo-file-issue` result | `/quo-file-issue` | TaskList | unknown | procedure |
| E6-111 | Choice `Encode in an existing ticket body`: for each item the user maps to a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass. | choice-set | L1192 · 6.5/Step 2 | ticket-body update | user's ticket mapping | - | bees, Agent | unknown | procedure |
| E6-112 | Append a `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body. | field-or-template | L1192 · 6.5/Step 2 | body section | ticket body | - | none | no | procedure |
| E6-113 | Land the update with `bees update-ticket --ids <ticket-id> --body-file <path>`. | command | L1192, L1199, L1207 · 6.5/Step 2 | ticket-body update | scratch body file | - | Bash, bees | yes | procedure |
| E6-114 | `<YYYY-MM-DD HH:MM>` is the current local date/time authored as a string via the `Write` tool from your own clock — do not add a `date` / `Get-Date` snippet. | field-or-template | L1192 · 6.5/Step 2 | heading timestamp | own clock | - | none | unknown | procedure |
| E6-115 | Keep the `## Deferred from /quo-execute run` stem verbatim and only append the parenthesized timestamp suffix; do not simplify back to a bare heading. | invariant | L1192 · 6.5/Step 2 | heading text | - | - | none | no | procedure |
| E6-116 | The timestamp suffix lets multiple Encodes to the same ticket body across runs sit side-by-side with distinguishable headings. | rationale-only | L1192 · 6.5/Step 2 | - | - | - | none | unknown | rationale |
| E6-117 | Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir (`/tmp/.quorum/` / `$env:TEMP\.quorum`), creating it first if absent. | command | L1192-L1208 · 6.5/Step 2 | scratch body file | revised ticket body | scratch-file convention | Bash | yes | procedure |
| E6-118 | **Filename**: re-use the triggering `defer-N` task's suffix — `bees-body-<defer-N>.md`, e.g. `bees-body-defer-3.md` for the encode triggered by `defer-3`. | name-class | L1192, L1197-L1198, L1205-L1206 · 6.5/Step 2 | scratch filename | triggering `defer-N` task name | - | TaskList | unknown | procedure |
| E6-119 | Re-using the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the file to its TaskList progenitor. | rationale-only | L1192 · 6.5/Step 2 | - | - | - | none | unknown | rationale |
| E6-120 | Snippet order: `mkdir -p /tmp/.quorum` (or `New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" \| Out-Null`), Write the body file, then `bees update-ticket --ids <ticket-id> --body-file <path>`. | ordering | L1194-L1208 · 6.5/Step 2 | dir, body file, ticket update | - | - | Bash, bees | yes | procedure |
| E6-121 | Do NOT remove the temp file after the bees command exits. | invariant | L1210 · 6.5/Step 2 | - | - | scratch-file convention | none | yes | procedure |
| E6-122 | Files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. | rationale-only | L1210 · 6.5/Step 2 | - | - | - | none | yes | rationale |
| E6-123 | Mark each Encode-routed `defer-*` task `completed` once the `bees update-ticket` update succeeds. | ordering | L1210 · 6.5/Step 2 | `defer-*` status flip | bees result | - | TaskList, bees | unknown | procedure |
| E6-124 | **Follow-up commit**: after all Encode writes in this gate firing have landed, produce a follow-up commit. | ordering | L1212 · 6.5/Step 2 | git commit | Encode writes | Section 4.1 per-Task commit step | git | yes | procedure |
| E6-125 | This gate fires AFTER Section 4.1's per-Task commits, so `bees update-ticket --body-file` writes are not swept into any prior commit and would leave the tree dirty at yield. | rationale-only | L1212 · 6.5/Step 2 | - | - | Section 4.1 | none | unknown | rationale |
| E6-126 | Produce exactly one follow-up commit per gate firing covering all Encode writes from that firing — not one per Encode item. | invariant | L1212 · 6.5/Step 2 | one git commit | Encode writes | - | git | yes | procedure |
| E6-127 | Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (same pattern as Section 4.1's commit step for Plans). | command | L1212 · 6.5/Step 2 | hive paths | `bees list-hives` output | Section 4.1 commit step | bees | yes | procedure |
| E6-128 | `git add` each hive path that lives inside this repo. | command | L1212 · 6.5/Step 2 | staged hive paths | resolved hive paths | - | git | yes | procedure |
| E6-129 | Additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations. | command | L1212 · 6.5/Step 2 | staged doc paths | CLAUDE.md `## Documentation Locations` (PRD/SDD keys) | CLAUDE.md `## Documentation Locations` | git | yes | procedure |
| E6-130 | Commit only if `git diff --cached` shows staged changes; when nothing is staged (out-of-repo hive, no PRD/SDD routes) skip the commit rather than produce an empty one. | precondition | L1212 · 6.5/Step 2 | conditional git commit | `git diff --cached` | - | git | yes | procedure |
| E6-131 | Commit subject contract: `Encode deferral: /quo-execute — <N> deferral(s) encoded`. | field-or-template | L1212 · 6.5/Step 2 | commit subject | `<N>` | - | git | no | procedure |
| E6-132 | **`<N>` counts deferral items, not tickets** — the count of `defer-*` items routed to Encode in this firing, and the same value passed as the helper's `--count`. | field-or-template | L1212, L1218 · 6.5/Step 2 | `<N>` value | Encode routing | - | none | yes | procedure |
| E6-133 | Run the bundled Python helper `hive_commit.py` as a single literal Bash tool call instead of decomposing the commit workflow into shell steps at runtime. | command | L1214 · 6.5/Step 2 | git commit (via helper) | resolved helper path | `hive_commit.py` | Bash, bees, git | yes | procedure |
| E6-134 | The helper resolves Plans/Specs/Issues hive paths, `git add`s in-repo hive paths and `--doc-path` paths, and commits only if staged — printing `skipped: nothing staged` and making no commit otherwise. | definition | L1214 · 6.5/Step 2 | commit or `skipped: nothing staged` | hives, `--doc-path` args | `hive_commit.py` | Bash, bees, git | yes | procedure |
| E6-135 | Out-of-repo hives require no git action — `bees update-ticket` already persisted their update. | definition | L1214 · 6.5/Step 2 | - | hive location | - | none | yes | procedure |
| E6-136 | **Do NOT blindly `git add -A`** — other agents may have in-flight changes; stage only resolved hive paths and explicit `--doc-path` arguments. | invariant | L1214 · 6.5/Step 2 | - | - | Section 4.1's per-Task commit step | git | yes | procedure |
| E6-137 | **Resolve the helper path (own-skill resolution)**: `<this skill's base directory>/scripts/hive_commit.py` — against **this skill's own base directory**, no `..` hop. | command | L1216 · 6.5/Step 2 | resolved helper path | skill base directory | `hive_commit.py`, `/quo-execute` | none | no | procedure |
| E6-138 | The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-execute`). | definition | L1216 · 6.5/Step 2 | - | skill invocation header | - | none | unknown | procedure |
| E6-139 | **This differs from `/quo-fix-issue` and `/quo-breakdown-epic`,** which resolve the same helper as a *sibling* of their own base directory (cross-skill consumers). | definition | L1216 · 6.5/Step 2 | - | - | `/quo-fix-issue`, `/quo-breakdown-epic` | none | no | rationale |
| E6-140 | Invoke the helper with `--skill quo-execute`. | command | L1218, L1222, L1227 · 6.5/Step 2 | helper arg | - | - | Bash | no | procedure |
| E6-141 | Invoke the helper with `--count <N>` — the Encode-routed `defer-*` item count, matching the commit-subject contract. | command | L1218 · 6.5/Step 2 | helper arg | `<N>` | commit-subject contract (E6-131) | Bash | yes | procedure |
| E6-142 | Pass one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`); omit entirely when none was routed. | command | L1218 · 6.5/Step 2 | helper arg(s) | CLAUDE.md `## Documentation Locations` | CLAUDE.md `## Documentation Locations` | Bash | yes | procedure |
| E6-143 | Command forms: POSIX `python3 "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]`; PowerShell `python "<resolved-helper-path>" --skill quo-execute --count <N> [--doc-path <abs-path> ...]`. | command | L1220-L1228 · 6.5/Step 2 | helper invocation | resolved helper path | - | Bash | no | procedure |
| E6-144 | After the helper lands the commit (or prints `skipped: nothing staged`), proceed to Step 3. | ordering | L1230 · 6.5/Step 2 | - | helper output | Step 3 | Bash | yes | procedure |
| E6-145 | The three options are mutually-non-exclusive at the active-set level: the user may pick one overall, or direct different items to different options (e.g., "fix items 1 and 2 now, file 3 as an Issue"). | choice-set | L1232 · 6.5 | per-item routing | user reply | - | AskUserQuestion | unknown | procedure |
| E6-146 | Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. | invariant | L1232 · 6.5 | all `defer-*` → `completed` | active `defer-*` set | - | TaskList | unknown | procedure |
| E6-147 | For per-item routing the user uses `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`); the orchestrator parses the reply and closes each `defer-*` task accordingly. | relay | L1232 · 6.5 | per-item close-outs | free-text reply | - | AskUserQuestion, TaskList | unknown | procedure |
| E6-148 | **Step 3**: until every `defer-*` task is `completed`, the skill cannot proceed to Section 7 (Final Output) and cannot mark the Bee `done`. | invariant | L1234 · 6.5/Step 3 | - | active `defer-*` set | Section 7 (Final Output) | TaskList, bees | unknown | procedure |
| E6-149 | A deferral important enough to surface during the run is important enough to encode in a durable carrier before the run ends. | rationale-only | L1234 · 6.5/Step 3 | - | - | - | none | unknown | rationale |
| E6-150 | If picked options fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or `bees update-ticket` errors), surface the still-active `defer-*` tasks via `AskUserQuestion` and re-run the gate until the active set is empty. | recovery | L1234 · 6.5/Step 3 | re-fired gate (see E6-001–E6-006) | `/quo-file-issue` / `bees update-ticket` failures | `/quo-file-issue` | AskUserQuestion, TaskList, bees | unknown | procedure |
| E6-151 | The fresh-session-per-phase recommendation at Bee close-out (Section 7 / Section 10) is preserved verbatim; this gate sits before that handoff prose and does not replace it. | ordering | L1236 · 6.5 | - | - | Section 7, Section 10 | none | unknown | procedure |

## Anchors defined here

Headings:

- L1116 — `### 6.5 Before handoff — deferral hygiene`
- L1120 — `#### Session-scoped compromise tracker`
- L1157 — `#### Compromise-tracker append triggers`
- L1141 — `## Compromise <n>` (entry-shape heading inside the template code block)
- L1192 — `## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)` (ticket-body section heading; stem `## Deferred from /quo-execute run`)

Bolded phrases (verbatim):

- L1122 — **session-scoped compromise tracker**
- L1122 — **canonical definition site**
- L1124 — **Tracker file path and naming.**
- L1124 — **once at the start of the run**
- L1138 — **Entry shape.**
- L1138 — **1-based counter scoped to the current run's tracker file**
- L1143 — **Finding (verbatim):**
- L1144 — **Fix paths surfaced by reviewer:**
- L1148 — **Decision:**
- L1149 — **Rationale:**
- L1150 — **Follow-up Issue:**
- L1153 — **Finding (verbatim)**
- L1153 — **Fix paths surfaced by reviewer**
- L1153 — **Decision**
- L1153 — **Rationale**
- L1153 — **Follow-up Issue**
- L1153 — **two**
- L1155 — **Persistence.**
- L1155 — **start of each run**
- L1155 — **NEVER appended to**
- L1161 — **Trigger A — Defer to follow-up Issue at either gate.**
- L1161 — **IMMEDIATELY AFTER**
- L1161 — **BEFORE**
- L1161 — **Name in `Rationale` which remaining enumerated path shipped as the soft fix**
- L1161 — **none did**
- L1161 — **On a `blocker` deferral the narrowing takes that slot**
- L1161 — **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger**
- L1161 — **On a `blocker`-severity finding this branch is reachable only as Defer-with-narrowing, at either gate**
- L1161 — **narrowing record**
- L1163 — **Trigger B — Accept the limitation at the scope-bounding gate.**
- L1163 — **IMMEDIATELY AFTER**
- L1163 — **BEFORE**
- L1163 — **Unreachable for a `blocker`-severity finding**
- L1165 — **Trigger C — ungated route (the orchestrator's own path pick).**
- L1165 — **no gate**
- L1165 — **MOMENT of implementer dispatch**
- L1165 — **row 6**
- L1165 — **SAME LOGICAL BLOCK as that dispatch**
- L1165 — **One carve-out:**
- L1165 — **the orchestrator's own one-line reason for preferring that path over the others**
- L1167 — **Row 6 is this trigger's only firing site.**
- L1169 — **Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).**
- L1169 — **both**
- L1171 — **SR-6.7 ungated-route recovery gate:**
- L1172 — **NEW**
- L1172 — **IMMEDIATELY AFTER**
- L1172 — **BEFORE**
- L1173 — **NO new entry is appended.**
- L1173 — **ORIGINAL Trigger C entry**
- L1173 — **UPDATED in place**
- L1174 — **DEFER**
- L1175 — **SR-4.6 under-enumeration analog recovery gate (same Trigger D mechanism, under-enumeration variant):**
- L1176 — **NEW**
- L1176 — **IMMEDIATELY AFTER**
- L1176 — **BEFORE**
- L1177 — **no original Trigger C entry to amend**
- L1177 — **new**
- L1177 — **UPDATE that entry's `Follow-up Issue` in place**
- L1178 — **DEFER**
- L1184 — **Step 0 — Retroactive ledger reconciliation (safety net).**
- L1184 — **create a corresponding `defer-*` TaskList task for any item that does not already have one**
- L1186 — **Step 1 — Enumerate the active deferral ledger.**
- L1188 — **Step 2 — Surface the active set and gate the user choice.**
- L1188 — **First**
- L1188 — **then**
- L1190 — **Fix in this session**
- L1191 — **File as issue tickets**
- L1192 — **Encode in an existing ticket body**
- L1192 — **Filename**
- L1212 — **Follow-up commit (after all Encode writes in this gate firing have landed).**
- L1212 — **`<N>` counts deferral items, not tickets**
- L1214 — **Do NOT blindly `git add -A`**
- L1216 — **Resolving the helper path (own-skill resolution).**
- L1216 — **this skill's own base directory**
- L1216 — **This differs from `/quo-fix-issue` and `/quo-breakdown-epic`,**
- L1234 — **Step 3 — Hard-stop on a non-empty active set.**

Other referable literals (not headings/bold, but named artifacts other text points at): `compromises-YYYYMMDD-HHMM-<short-suffix>.md` (L1124); `gate-askuserquestion-<short-suffix>` (L1118, L1188); `defer-<short-suffix>` / `defer-*` (L1180 ff.); `bees-body-<defer-N>.md` (L1197, L1205); `Deferral hygiene: no deferred items.` (L1186); `Encode deferral: /quo-execute — <N> deferral(s) encoded` (L1212); `hive_commit.py` (L1214, L1216); `skipped: nothing staged` (L1214, L1230); `--skill quo-execute` / `--count <N>` / `--doc-path <abs-path>` (L1218–L1228); Step 0 / Step 1 / Step 2 / Step 3 (L1184, L1186, L1188, L1234).

## Rationale-only spans

No whole line in this slice is rule-free (every paragraph line carries at least one rule), so the spans below are sub-line clauses inside long paragraph lines. Approximate line-equivalents given in parentheses.

- L1122 (clause, ~0.2 line) — why tracker: visible, challengeable, not baked-in.
- L1124 (sentence, ~0.3 line) — timestamp prefix aids cross-run debuggability.
- L1153 (final sentence, ~0.3 line) — why Decision has two override values.
- L1155 (parenthetical, ~0.1 line) — yield does not lose file state.
- L1161 (sentence "Either way…unfixed one.", ~0.2 line) — deferral and shipped fix are one decision.
- L1161 (clause "since a blocker's Defer branch ships a narrowing", ~0.1 line) — why narrowing replaces path letter.
- L1163 (clause "since accepting a blocker ships it", ~0.05 line) — why Accept is blocker-unreachable.
- L1165 (clauses "a single trivially-deletable path…"; "since the rule name gives…", ~0.2 line) — carve-out and Rationale-content justification.
- L1173 (parenthetical, ~0.2 line) — originating Trigger C entry always exists.
- L1184 (sentence "The upstream record-creating…documented sites).", ~0.3 line) — Step 0 is defense-in-depth net.
- L1191 (parenthetical, ~0.15 line) — precedent for inline Skill dispatch.
- L1192 (two sentences: "the suffix exists so that…"; "Reusing the triggering task's suffix is…", ~0.4 line) — heading-suffix and filename-suffix justification.
- L1210 (clause after the dash, ~0.1 line) — scratch files accumulate for debugging.
- L1212 (first sentence "This gate fires AFTER…yields.", ~0.3 line) — why a follow-up commit is needed.
- L1214 (parenthetical "out-of-repo hives have already…", and "other agents or processes may have in-flight changes", ~0.2 line) — helper design justification.
- L1216 (clause "because they consume it across skills", ~0.05 line) — why sibling resolution elsewhere.
- L1234 (sentence "This is the structural enforcement…before the run ends.", ~0.2 line) — why the hard-stop exists.

Estimated rationale-only total: ~3.4 line-equivalents spread across 17 sub-line spans; 0 whole lines.
