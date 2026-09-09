# EDGES — dependency structure of the two orchestrators

Mechanism names are the unified names/numbers from `INVENTORY.md`. Edges are derived from the consolidated files' header `Edges` / `Cross-mechanism edges` bullets and the `Produces` / `Consumes` columns; role-side edges from `agents-roles.md`. Scope tags: (both) unless marked (fix) or (exec).

## (a) Mechanism → mechanism edge table

| # | Producer | Artifact / literal carried | Consumer |
|---|---|---|---|
| E1 | #1 Preconditions | run exit `Run /quo-setup first.`; validated `## Documentation Locations` / `## Build Commands` keys | every later mechanism; #10 Dispatch prompt, #11 Roles, #18 Close-out (`Format`), #40 Testing |
| E2 | #2 Effort gate | `gate-askuserquestion-*` fire (Step 3 only) | #13 gate contract |
| E3 | #2 Effort gate | session effort inherited by `general-purpose` sweep (informational) | #25 Post-completion |
| E4 | #28 ARG (fix) | ordered post-resolution working list | #4 Manifest (`**Unit scope:**`), #29 Issue validation, #5 Loop, #35 GH (fixed-issue list excludes soft-fails) |
| E5 | #28 ARG (fix) | `/quo-file-issue` inline-Skill precedent (`url: <url>`, `issue_ticket_id`) | #15 Routing (Defer), #23 Deferral gate (File), #21 Guard (Configure now), #26 Recovery gates |
| E6 | #3 Isolation | `**Isolation strategy:**` enum value | #4 Manifest; #43 Merge (exec) |
| E7 | #37 Bee selection (exec) | Bee ID | #4 Manifest filename discriminator; #38 Epic selection |
| E8 | #38 Epic selection (exec) | `Multi-Epic run mode`, `Epics in scope`, Epic `in_progress` flip | #4 Manifest placeholders; #41 Next-Epic (Mode 1/2 branch); #5 Loop |
| E9 | #24 Tracker | tracker filename generated at run start | #4 Manifest `**Compromise tracker:**` |
| E10 | #4 Manifest | fourth Read-state source | #5 Loop; #6 Recovery |
| E11 | #4 Manifest | `**Pre-session SHA:**` / `**Pre-Bee SHA:**` | #20 Checkpoint (ranged `--grep`), #25 Post-completion (`git diff <sha>`), #35 GH (fix), #41 Next-Epic `<previous-epic-last-commit>` (exec) |
| E12 | #4 Manifest | `**Compromise tracker:**` path | #19 Summaries (`**Accepted compromises**` read), #20 Checkpoint carrier 3, #10/#39 PM dispatch `<compromise-tracker-path>`, #25 reviewer prompt |
| E13 | #4 Manifest | `**Unit scope:**` batch (fix) / `Multi-Epic run mode` (exec) | #5 Loop validation (FX-MAN-20), #20 Checkpoint, #25 step 1, #41 branch 2 |
| E14 | #20 Checkpoint | manifest rewrite (`**Progress:**`, `**Next unit:**`) | #4 Manifest; next-unit reader after compaction |
| E15 | #22 Aborted close-out | aborted `**Progress:**` shapes | #20 Checkpoint step 2 → #4 Manifest |
| E16 | #29 Validation (fix) | ticket JSON (body, `reference_materials`, `up_dependencies`, status) | #30 Analyst, #10 Dispatch prompt, #14 Scoped-marker (Path B), #35 GH |
| E17 | #30 Analyst (fix) | `## Design Proposal for <issue-id>` with `### Recommended approach`, `### Blast radius`, `### Policy decisions this change implies`, `### Why`, `### Alternatives considered`, `### Options the body did not consider`, `Analyst verdict:` | #32 Directive (on Approve), #10 relay `## Blast radius`, user (prose + preamble) |
| E18 | #30 Analyst (fix) | `### Deferred refinements` bullets with destination annotations | #31 DEFC → #17 Ledger → #23 Deferral gate Step 0 surface 3 |
| E19 | #30 Analyst gate `Cancel` (fix) | abort branch | #22 Aborted close-out |
| E20 | #30 Analyst (fix) | `analyst-<issue-id>` / `-rev<n>` task | #12 TaskList; #7 Engineer precondition prefix; #6 Recovery arms |
| E21 | #33 Design-question receiver (fix) | Analyst re-dispatch prompt (`## Prior proposal and user feedback` carrying `## Design question` + `## Files changed`) | #30 Analyst surface-and-gate flow |
| E22 | #5 Loop Phase A (fix) | Engineer return with `## Design question` | #33 DQ (not a completion) |
| E23 | #15 Routing gates (c)/(d) (fix) | `Re-dispatch the Analyst with this finding` | #33 DQ → #30 Analyst |
| E24 | #33 DQ Approve (fix) | close-out prefix sweep; discard superseded findings | #7 Engineer precondition satisfied; #12 TaskList |
| E25 | #6 Recovery (fix) | re-derivation-shape Analyst dispatch; Code Reviewer re-dispatch | #30 Analyst; #5 Phase A |
| E26 | #7 Engineer precondition | stranded-`pending` default (not landed) | #6 Recovery arms |
| E27 | #32 Directive (fix) | `## Authoritative design directive (from Section 3 Analyst pass)` + `## Design context (…)` + `## Blast radius` | #10 Engineer prompt; `agents/engineer.md` (R-126..131) |
| E28 | #32 Directive (fix) / ticket bodies + spec (exec) | "approved design" for mechanism detection | #15 Routing row 2 fallback (FX-ROUTE-47 / EX-ROUTE-37) |
| E29 | #10 Dispatch prompt | per-role `Agent(subagent_type=<role>, run_in_background=true, prompt=…)` | #5 Loop, #16 Review loop, #25 postcomp lanes |
| E30 | Engineer return (R-156) | `## Files changed` | #10 → `## Source paths to fingerprint` → Test Writer (R-209) → #8 Movement rung (fingerprint set) |
| E31 | Engineer return (R-160) | completeness evidence | #10 → `## Engineer's completeness evidence` + sweep-shaped statement → code-reviewer (R-464) / pm (R-400) → `/quo-engineer-review` |
| E32 | #10 (post-compaction) | compaction-artifact missing-list finding | #17 Ledger (`defer-*` annotated addressed-now) → #19 `**Ignored Review Feedback**` (FX-PROMPT-21; see DECISIONS inconsistency 5) |
| E33 | #14 Scoped-marker wiring | `<scoped-marker-resolver-path>` | #10 PM prompt (fix) / #39 PM dispatch (exec) → pm (R-358) → `scoped_marker_resolver.py` |
| E34 | #11 Roles | no-loosening constraint; `agents/<role>.md` authoritative | #10 framing prose; #30 Analyst framing |
| E35 | #11 Roles (fix) | `## Doc divergence noted` consumption by Doc Writer | #34 Doc verification |
| E36 | #5 Loop Phase B / per-Subtask (exec) | writer returns (movement report vs deliverable) | #8 Movement rung |
| E37 | #8 Movement rung | `pending` `aborted-<role>-<id>` marker | #5 Phase C gate (fix) / #39 PM advance & #16 Bee-level loop close (exec); #18/#22/#16 sweeps; #25 postcomp variant; #12 name class |
| E38 | #8 Movement rung | unattributed movement | #9 Unexplained-movement gate |
| E39 | #9 Unexplained gate | `Re-dispatch the writer now` / `Wait` / `Abort this Issue|unit` | #8 re-dispatch; yield; #22 Aborted close-out |
| E40 | Test Writer return (R-235) | `## Perturbations` (`None`) | #8 attribution (FX-MOVE-19..24 / EX-MOV-27..29) |
| E41 | #7 Engineer precondition | `aborted-` excluded from prefix list | #8 (Engineer round allowed while redelivery owed) |
| E42 | #15 Routing part (g) | ordering Engineer → code review → writer after movement | #8 re-dispatch ordering (EX-MOV-23) |
| E43 | #12 TaskList naming | name classes + prefix rule | #7, #8, #13, #17, #18, #22, #25, #6, #16 |
| E44 | #13 gate contract | two-step `TaskCreate` → `AskUserQuestion`; yield-control | #2, #30, #9, #15 (c)/(d), #23 Step 2/3, #21 Step 5, #25 step 5, #26; exec also #3, #37, #38, #41, #42 |
| E45 | #6 Recovery (fix) | re-derivation overrides generic gate re-fire for the Section 3 gate | #13 (FX-RECOV-15) |
| E46 | reviewer roles (code/test/doc-reviewer, pm) | routing trailer `**Your next tool use MUST address these findings now.**` / `**… MUST advance the workflow.**` + counter-anchor | #16 Review loop ("follow literally") |
| E47 | reviewer roles | findings: `blocker`/`suggestion`/`nit`, `[depth:…]`, `[preferred]`, `[introduces-mechanism]`, path count | #15 Routing Step 1/2 |
| E48 | #15 Routing row 6 | implementer dispatch (chosen path, full fix) + Trigger C entry | #10 → #5/#16; #24 Tracker |
| E49 | #15 Routing rows 2/3/4 | gate (c) fire; `Defer to follow-up Issue` / `Accept the limitation` / `Fix properly now` (+ `Re-dispatch the Analyst…` fix; `Cancel` exec) | #13; #24 Trigger A/B; `/quo-file-issue`; #33 DQ (fix); #22 (exec Cancel) |
| E50 | #15 Routing rows 1/5 | gate (d) fire; per-path choices, `Defer`, `Cancel` | #13; #24 Trigger A; #22 Aborted close-out |
| E51 | #15 Routing SBL | lane-closure decision; batched-nit count | #5 Phase A / writer lanes closure (fix), #16 Bee-level loop (exec); #19 `**Reviews**` `N nits applied without re-review` |
| E52 | #15 Routing part (g) | Engineer-dispatch precondition invoked before every source-changing re-dispatch | #7 Engineer precondition |
| E53 | #15 Routing / #16 Review | ignore decision | #17 Ledger (`defer-*` with destination) |
| E54 | pm Final report (R-420..454) | ignored feedback; deferred items with `addressed-now-in-this-Task` / `defer-to-existing-ticket-body: <id>` / `defer-to-new-Issue`; tracker-blocker findings / report notes; `### Second-order effects` | #17 Ledger; #23 Step 0 surface 2; #15 Routing (blocker finding with fix path) or exempt report note (FX-ROUTE-115); #19 Summaries |
| E55 | pm (R-344) | `no spec drift surface to review for this Issue` | #34 Doc verification → #19 per-issue summary (fix) |
| E56 | code-reviewer / pm (R-473, R-440) | `### Second-order effects` body | #19 `**Second-order effects**` field (per-Issue / per-Task / `## Bee Execution Complete`) |
| E57 | #17 Ledger | active `pending` `defer-*` set with `metadata.activity` | #23 Deferral gate Steps 1–3; #20 Checkpoint carrier 4 |
| E58 | #19 Summaries (fix) | `**Ignored Review Feedback**` field | #23 Step 0 surface 1 |
| E59 | #23 Deferral gate | empty ledger | #20 Checkpoint (precondition); #42 Final (exec) |
| E60 | #23 Deferral gate Encode | `bees update-ticket --body-file`; `hive_commit.py --skill … --count <N>` → commit `Encode deferral: … — <N> deferral(s) encoded` / `skipped: nothing staged` | git history; #20 Checkpoint (FX-CKPT-16 warns bare `git log -1`) |
| E61 | #23 Deferral gate File | `/quo-file-issue` per item → Issue ID | #17 mark completed |
| E62 | #18 Close-out | per-unit commit with `(<issue-id>)` / `(<task-id>)` subject token | #20 Checkpoint verify; #35 GH `--grep '(<issue-id>)'` (fix); #41 `<previous-epic-last-commit>` (exec) |
| E63 | #18 Close-out | `open→done` / `status=done` flip | #20 Checkpoint carrier 1; #29/#35 fixed-issue list |
| E64 | #18 Close-out step 5 (fix) / #41 Next-Epic (exec) | invocation order: #23 → #20 → (#21 on continuing path) → next unit / #25 | #23, #20, #21, #25 |
| E65 | #18 Close-out | `hive_commit.py resolve-hive-paths --hive issues|plans` | staging of in-repo hive dir |
| E66 | #20 Checkpoint | "re-read, do not recall" at next unit; write missing fact into a carrier | #5 next-unit dispatches |
| E67 | #21 Guard | STOP + fresh-session resume command (`/quo-fix-issue all|<remaining-ids>` / `/quo-execute <bee-id>`) or continue | run exit / #5 step 2 |
| E68 | `context_gauge.py` (quo-setup) | `stop-threshold` integer; `read` → integer / `no-reading` / `stale` / `missing`; `write-opt-out`; marker `context-guard-opt-out` | #21 Guard |
| E69 | #21 Guard `Configure now` | `/quo-setup --configure-gauge-producer` inline | quo-setup |
| E70 | #22 Aborted close-out | same prefix sweep as #18; HYG step 2 (fix); checkpoint aborted path; `git status --porcelain` paths; run stop + resume command | #12, #23, #20, operator |
| E71 | #24 Tracker | `## Compromise <n>` entries (five fields, Decision enum) | #19 `**Accepted compromises**`; #20 carrier 3; pm tracker check (R-425..439); #25 PHASE 1–3 |
| E72 | #15 Routing | Triggers A (Defer at (c)/(d)), B (Accept at (c)), C (row 6) | #24 Tracker append |
| E73 | #26 Recovery gates | Trigger D append / in-place `Follow-up Issue` update | #24 Tracker |
| E74 | #25 Post-completion | `[compromise-challenge]` PHASE 3/4 findings | #26 Recovery gates (per finding, emission order) |
| E75 | #25 Post-completion | PHASE 2 `[compromise-challenge]` `blocker` | #25 step 5 aggregate gate only (`Fix in this session` recommended) — no recovery gate |
| E76 | #25 Post-completion | `Fix in this session` → `<role>-postcomp-<n>` lanes; `File as issue tickets` → `/quo-file-issue`; commit | #10, #7 (postcomp variant), #8 (postcomp variant), #12; #35 GH (fix) / #23 → #42 (exec) |
| E77 | #23 Deferral gate end-of-batch firing (fix) | must close before Section 8 | #25 Post-completion |
| E78 | #41 Next-Epic (exec) | branch 1 stop / branch 2 Mode gate / branch 3 final review; interaction-fix commits | #20 Checkpoint (all exits), #21 Guard (continuing paths), #16 Bee-level review, #38 (return to step 2) |
| E79 | #40 Testing (exec) | rung 5 = `Format` only before commit | #18 Close-out |
| E80 | #39 PM dispatch (exec) | PM Final report | #18 summary, #17 Ledger, #19 second-order |
| E81 | #42 Final (exec) | Bee `done` flip after all-Epics-`done` re-check | #19 `## Bee Execution Complete` → #43 Merge |
| E82 | #27 Shell/scratch | `<tempdir>/.quorum/` create-if-absent, `Write` tool, never delete; sibling-helper `..` resolution | #4, #24, #23 (Encode body-file), #21 (opt-out marker), #14, #18, #21 helpers |
| E83 | doc-writer (R-287..303) | `### Feature: <title>` under `## Per-feature scope` / `## Per-feature design` | later doc-writer passes; `/quo-plan-from-specs --feature`; `scoped_marker_resolver.py` |
| E84 | orchestrator | Plan Bee `title` (verbatim) in dispatch context | doc-writer (R-293..298) |
| E85 | orchestrator | `<compromise-tracker-path>` | pm (R-425, R-426, R-439) |

Edge count: 85 mechanism-level edges (≈ 110 when the shared edges are split by skill).

## (b) Load-bearing chains

**Chain 1 — Reviewer trailer → orchestrator loop → routing table → gates → tracker triggers → post-completion PHASE checks**
1. A review skill (`/quo-engineer-review` etc.) emits findings tagged `blocker`/`suggestion`/`nit`, fix paths with `[depth:…]`, optional `[preferred]` and `[introduces-mechanism]`, plus the routing trailer `**Your next tool use MUST address these findings now.**` / `**… MUST advance the workflow.**` (R-469, R-471, R-485, R-494; FX-REVIEW-5 / EX-BEEREV-5).
2. The reviewer role relays tokens intact (R-471/R-472; pm R-396..398) → orchestrator "follows the trailer literally" (FX-REVIEW-6 / EX-BEEREV-5).
3. Per finding: Step 1 pick highest-quality path (FX-ROUTE-22..31 / EX-ROUTE-19..25); Step 2 table rows 1–6 (FX-ROUTE-32..38 / EX-ROUTE-26..32). SBL decides whether the lane stays open (FX-ROUTE-6..20 / EX-ROUTE-5..17).
4. Row 6 → ungated dispatch **and Trigger C entry** in the same block (`Decision: Orchestrator picked path (x) — highest-quality`, one-line Rationale) — carve-out: lone `trivial-tweak` appends nothing (FX-TRACK-55..65 / EX-TRK-28..32). Rows 2/3/4 → gate (c): `Defer to follow-up Issue` → file first, then Trigger A (Rationale names shipped soft fix or narrowing) — `Accept the limitation` → Trigger B (never on a `blocker`) — `Fix properly now` → no entry. Rows 1/5 → gate (d): `Defer` → Trigger A with `Fix paths surfaced by reviewer: none` allowed.
5. Part (g) orders any source-changing re-dispatch Engineer → code review → affected writer, gated by the Engineer-dispatch precondition (#7); elided only for the final `trivial-tweak` nit pass.
6. At run end the post-completion reviewer reads the tracker via `<compromise-tracker-path>`: PHASE 1 consume; PHASE 2 challenge each entry, flag `blocker`+`User picked Accept the limitation`, `User picked Defer to follow-up Issue` without narrowing record, narrowing that left the defect partly unfixed → `[compromise-challenge]` `blocker`; PHASE 3 two-axis check on every `Orchestrator picked path (…) — highest-quality` entry; PHASE 4 under-enumeration on every in-flow finding (FX-POSTC-19..41 / EX-POST-19..28). PM's Final report runs the same blocker check per unit (R-425..439).
7. PHASE 3/4 challenges fire SR-6.7 / SR-4.6 per finding (labels byte-matched to Trigger D) → Trigger D appends or updates `Follow-up Issue` in place; PHASE 2 violations go only to the aggregate Fix/File/Skip gate (#26).

**Chain 2 — Ignored review feedback → defer-* ledger → deferral-hygiene gate → Encode/File commits**
1. Ignore decision (Phase C / Bee-level) or PM/Analyst structured item with `defer-to-existing-ticket-body: <id>` / `defer-to-new-Issue` → create `defer-<short-suffix>` task `pending`, `metadata.activity` = one-line description + destination (FX-LEDGER-3..8 / EX-DEFER-1..4; FX-DEFC-7..12). `addressed-now-in-this-Task|Issue` items are excluded.
2. Ignored items also render in the unit summary `**Ignored Review Feedback**` (FX-SUM-7 / EX-CLEAN-28).
3. Deferral gate Step 0 re-walks surfaces (summary field, PM Final report, Analyst block) and back-fills missing `defer-*` tasks (FX-HYG-6..17 / EX-DHG-5..9).
4. Step 1 scans `defer-` prefix + `pending|in_progress`; empty → `Deferral hygiene: no deferred items.` (batch-close variant in fix). Step 2 surfaces numbered list; two-step gate `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body`; per-item routing via the auto-appended free-text slot.
5. Encode: `Write` body to `<tempdir>/.quorum/bees-body-<defer-N>.md`, `bees update-ticket --ids <id> --body-file <path>` appending `## Deferred from /quo-<skill> run (<YYYY-MM-DD HH:MM>)`; then one `hive_commit.py --skill <skill> --count <N> [--doc-path …]` follow-up commit `Encode deferral: /quo-<skill> — <N> deferral(s) encoded` or `skipped: nothing staged`. File: `/quo-file-issue` per item.
6. Step 3 hard-stop until every `defer-*` is `completed`; then checkpoint (carrier 4 empty) → next unit / post-completion / Final.

**Chain 3 — Run-state manifest → checkpoints → context guard → post-compaction recovery**
1. Section 1 writes `<tempdir>/.quorum/run-state-<skill>-<discriminator>.md` (truncate) with `**Unit scope:**`, run mode (exec), `**Isolation strategy:**`, `**Pre-session SHA:**`/`**Pre-Bee SHA:**` (`git rev-parse HEAD`, only capture site), `**Compromise tracker:**` (path incl. suffix, generated here), `**Progress:**`, `**Next unit:**` (FX-MAN-2..42 / EX-MAN-2..31). Exec rewrites placeholders after the Section 2 query (EX-MAN-32..40).
2. Every Read-state tick reads the manifest as the fourth source; fix validates `**Unit scope:**` against the live batch, treating a foreign manifest as absent and bounding SHA checks with `HEAD~N` (FX-MAN-20/21).
3. At each unit boundary (fixed or aborted), after the deferral gate: checkpoint verifies five carriers (bees status; commit via ranged `--grep '(<issue-id>)'` or `git log <previous-epic-last-commit>..HEAD`; tracker entries vs accepted compromises; TaskList all `completed`, `defer-*` empty; manifest), fixes gaps now, rewrites the manifest (`**Progress:**` line incl. aborted shapes, `**Next unit:**`), and mandates re-read-not-recall for the next unit (FX-CKPT-11..30 / EX-CKPT-17..32).
4. Only on the continuing in-session path (batch with next Issue / Mode 1 accept or Mode 2): guard reads `CLAUDE_CODE_SESSION_ID`, calls `context_gauge.py stop-threshold` and `read --session-id`, branches integer/`no-reading`/`stale`/`missing`/non-zero; `missing` checks `context-guard-opt-out` then fires the four-option gate; stops name the fresh-session resume command (FX-GUARD / EX-CWG).
5. After a summarization marker: treat prior context as non-authoritative, re-read all four sources; fix re-derives the Design Proposal through the Analyst (re-derivation shape: body from bees, `## Files changed` or `git diff --name-only HEAD`, "prior proposal lost" statement) and branches the resume on TaskList-derivable state; Code Reviewer verdict has no carrier → re-dispatch (FX-RECOV-1..37 / EX-PCR-1..8). The checkpoint never reclaims context; the fresh session is the only lever.

**Chain 4 — Analyst return headings → design directive → Engineer dispatch → completeness evidence / Blast radius relay → check #8**
1. Analyst emits `## Design Proposal for <issue-id>` with unconditional `### Blast radius` (fixed line `No invariant added, removed, or weakened.`), unconditional `### Policy decisions this change implies` (fixed line `None — the recommendation leaves no policy question open.`), `### Recommended approach`, `### Why`, `### Alternatives considered`, `### Options the body did not consider`, conditional `### Upstream-fetch status`, trailer `Analyst verdict: <…>`, `### Deferred refinements` (R-039..093).
2. Orchestrator reads the verdict → preamble template (FX-ANA-23..37), surfaces body minus `### Deferred refinements`, fires Approve/Revise/Cancel (FX-ANA-38..44).
3. Approve → directive = `### Recommended approach` + `### Blast radius` + `### Policy decisions this change implies` (directive side) + Why/Alternatives/Options (context) + light-revision clarification (FX-DIR-1..4); `### Deferred refinements` → `defer-*` tasks (FX-DEFC-7..12).
4. Engineer prompt embeds body verbatim + `## Authoritative design directive (from Section 3 Analyst pass)` + `## Design context (…)` + `## Blast radius` and states the directive is the enumeration (FX-PROMPT-8..11); `agents/engineer.md` makes the directive win over the body (R-126..131) and reconciles its sweep against `## Blast radius` (R-165..172).
5. Engineer returns `## Files changed` (→ fingerprint chain) and completeness evidence when sweep-shaped (R-156..161); an unenumerated mechanism → `## Design question` (R-148..152) → DQ re-dispatches the Analyst (Chain 4a: FX-DQ-1..25).
6. Code Reviewer and Phase C PM prompts relay `## Engineer's completeness evidence` (verbatim, inline, per round) + sweep-shaped statement, and `## Blast radius` verbatim under the same heading even when it is the fixed line (FX-PROMPT-13..30); code-reviewer / pm forward both into `/quo-engineer-review` under the same headings (R-400..404, R-464..468). This is what enables `/quo-engineer-review`'s completeness check ("check #8"): an unnamed sweep silently loses it (FX-PROMPT-24 / EX-DPS-27). After compaction the list may be gone (heading omitted, sweep-shaped still stated, resulting finding treated as a compaction artifact); `## Blast radius` is always re-derivable via Chain 3 step 5.

**Chain 5 — Movement report → aborted-* marker → Phase C gate → part (g) ordering**
1. Test Writer fingerprints `git rev-parse HEAD` + `git hash-object <## Source paths to fingerprint>` at start and end; Doc Writer re-reads with `Read`/`Grep`; on movement the writer stops, withholds the `done` flip (exec), and reports files/HEADs/progress (R-198..227, R-262..265).
2. Orchestrator reads the return before persisting; "stopped" marks it a movement report, not a completion (FX-MOVE-4..10 / EX-MOV-5..7). Exec: sibling-Subtask movement is an observation → finish normally (EX-MOV-6).
3. Mark the writer's own task `completed`; create `aborted-<role>-<id>` `pending` with the "how far I got" report in `metadata.activity` (FX-MOVE-12..14 / EX-MOV-10..13). Exec: undo a premature `done` with `bees update-ticket … --status in_progress`; Bee-scoped lanes skip the corrective (EX-MOV-16..21).
4. Gate: Phase C MUST NOT begin (fix) / Task MUST NOT advance to PM, Bee-level loop MUST NOT close (exec) while any `aborted-` prefix task is `pending` (FX-MOVE-15 / EX-MOV-15, -21). The Engineer-dispatch precondition does NOT match `aborted-` (FX-ENGPRE-13 / EX-EDP-18).
5. Attribution: Engineer mover → Phase A must re-close first (fix treats as precondition breach); sibling Test Writer's `## Perturbations` lists every moved path → re-dispatch with no gate once it returns; wait for in-flight Test Writers; otherwise external actor → re-dispatch once the tree settled, or unexplained → gate (`Re-dispatch the writer now` / `Wait` / `Abort this Issue|unit`).
6. Re-dispatch under the next `-r<n>` name carrying `metadata.activity`; a normal deliverable marks `aborted-*` `completed` and releases the gate; a second abort refreshes the existing marker (FX-MOVE-26..28 / EX-MOV-31..33). When the movement came from a review-finding re-dispatch, part (g) orders the writer re-dispatch after the code review for that site closes (EX-MOV-23; FX-MOVE-18). `Abort` → aborted close-out sweeps the marker (FX-ABORT-9 / EX-ABORT-12). Postcomp lanes reuse the rung under `aborted-<role>-postcomp-<n>` with "abort this follow-up lane" reading and their own sweep (FX-POSTC-82..94 / EX-POST-50..55).

**Chain 6 — Per-unit commit subject → checkpoint verification → GitHub close block (fix) / inter-Epic diff (exec)**
`Fix issue: <title> (<issue-id>)` (FX-CLOSE-19) → `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (FX-CKPT-14) → `git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` → `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` for `github-issue` resolvers (FX-GH-14..29). Exec: `Plan <bee-id>, Epic N, Task M — … (<task-id>)` → one-commit-per-Task count against `<previous-epic-last-commit>..HEAD` (EX-CKPT-23) → interaction checkpoint `git log --oneline <previous-epic-last-commit>..HEAD` (EX-NEXT-3).

## (c) Contract surface between orchestrators and roles

Reproduced from `agents-roles.md` `## Contract surface` (56 surfaces). Emitter → Consumer.

**Role → orchestrator (34)**
| Surface string | Emits | Consumes |
|---|---|---|
| `## Design Proposal for <issue-id>` | analyst | fix orchestrator (surfaces body) |
| `### Problem`, `### Root cause`, `### Why`, `### Alternatives considered`, `### Options the body did not consider` | analyst | fix orchestrator → user prose; Why/Alternatives/Options also → Engineer `## Design context` |
| `### Recommended approach` | analyst | fix → Engineer `## Authoritative design directive` |
| `### Blast radius` (unconditional; `No invariant added, removed, or weakened.`) | analyst | fix → `## Blast radius` to engineer, code-reviewer, pm |
| `### Policy decisions this change implies` (unconditional; `None — the recommendation leaves no policy question open.`) | analyst | fix approval gate; preamble count; directive |
| `### Upstream-fetch status` (conditional) | analyst | fix (proceed / escalate) |
| `Analyst verdict: recommend-as-stated|recommend-with-refinements|recommend-different-approach|escalate-to-user` | analyst | fix preamble framing |
| `### Deferred refinements` (`None` or bullets with `addressed-now-in-this-Issue` / `defer-to-existing-ticket-body: <id>` / `defer-to-new-Issue`) | analyst | fix → `defer-*` ledger at Approve |
| `## Design question` (literal) | engineer | fix DQ receiver (any other heading = completion); postcomp: route to File |
| `## Files changed` | engineer | both → `## Source paths to fingerprint`; fix re-derivation shape |
| Completeness evidence (patterns verbatim, hits, disposition) | engineer | both → `## Engineer's completeness evidence` |
| Subtask `status=in_progress` / `status=done` (exec) | engineer, test-writer (doc-writer via orchestrator) | exec loop handoff; premature-flip detection |
| Partial-return statement (Subtask left `in_progress`) | engineer, test-writer | both |
| `## Perturbations` (paths or `None`) | test-writer | both movement attribution |
| Movement report (files, opening/closing HEAD, progress) | test-writer, doc-writer | both movement rung |
| "content-hash reading not taken because the path set was empty" | test-writer | both |
| Missing Plan Bee linkage / setup-gap report | doc-writer | both |
| Divergence note (diff vs Task body) | doc-writer | exec |
| `### Feature: <title>` under `## Per-feature scope` / `## Per-feature design` | doc-writer (file) | later doc-writer passes; `/quo-plan-from-specs --feature`; `scoped_marker_resolver.py` |
| `no spec drift surface to review for this Issue` | pm | fix per-issue summary |
| PM Final report (ignored feedback, contentious topics, conflicting decisions, incomplete work, cross-Task/Epic issues, tracker blockers) | pm | both |
| `### Second-order effects` (exactly one) with `#### <invocation scope>` sub-blocks | pm | `**Second-order effects**` field |
| `### Second-order effects` body (no heading line) | code-reviewer | `**Second-order effects**` field (`## Bee Execution Complete` / per-issue summary) |
| Fix-path lines with `[depth:…]`, `[preferred]`, `[introduces-mechanism]` | pm, code-reviewer | routing scope-bounding gate |
| Findings: `blocker`/`suggestion`/`nit`; `trivial-tweak`/`refactor-locally`/`re-architect`; file:line; verdict | code-reviewer, test-reviewer, doc-reviewer, pm | routing discipline |
| `blocker` finding with lettered `(a) [depth:…]` fix path for in-scope tracker violation | pm | routing |
| One-line report note (no severity, no fix path) for earlier-unit violation / resolved blocker / skipped check | pm | orchestrator must NOT route (shim-exempt) |
| Deferred items with `addressed-now-in-this-Task` / `defer-to-existing-ticket-body: <id>` / `defer-to-new-Issue` | pm | `defer-*` ledger; deferral gate |
| Helper-fallback warning; tie-break note; helper stderr | pm | orchestrator / user |
| Design question (team proposes alternatives) | pm | orchestrator |

**Orchestrator → role (14)**
| Surface | Emits | Consumes |
|---|---|---|
| Issue ID + verbatim body | fix | analyst, engineer, pm |
| Revision feedback / `## Prior proposal and user feedback` (Design question + partial-implementation notice) | fix | analyst |
| `## Authoritative design directive` (MAY) | fix | engineer |
| `## Blast radius` (incl. fixed "no sites" line) | both | engineer (reconcile), pm, code-reviewer (forward) |
| Subtask / Issue ticket ID and body | both | engineer, test-writer, doc-writer, pm |
| `## Source paths to fingerprint` | both | test-writer |
| Bee-scoped dispatch (no Subtask id) | exec | test-writer, doc-writer, pm |
| Plan Bee `title` (or pre-resolved fallback) | both | doc-writer |
| Grandparent Bee ID (Path A) / Issue ID + `up_dependencies` (Path B) | exec / fix | pm |
| `<scoped-marker-resolver-path>` | both | pm |
| Compromise-tracker path (`<compromise-tracker-path>`) | both | pm |
| `## Engineer's completeness evidence` + sweep-shaped statement | both | code-reviewer (forward); pm |
| Review scope (diff range, ticket ID, or both) | both | code-reviewer, test-reviewer, doc-reviewer |
| Source-tree-stability promise (mode-scoped; never "frozen") | both | test-writer, doc-writer |

**Role → wrapped skill (3):** `## Engineer's completeness evidence` + sweep-shaped statement (pm, code-reviewer → `/quo-engineer-review`); `## Blast radius` (pm, code-reviewer → `/quo-engineer-review`); review scope (reviewers, pm → the three review skills).

**Role → external artifact (5):** `/tmp/.quorum/bees-bee-body-<short-suffix>.md` (pm → `scoped_marker_resolver.py`, exit 0 `"scoped": true|false` + `docs` / exit 2 + stderr); `/tmp/.quorum/test-writer-<short-suffix>-<original-filename>` (test-writer scratch copy); CLAUDE.md `## Documentation Locations` seven keys (quo-setup → analyst, engineer, test-writer, doc-writer, pm); CLAUDE.md `## Build Commands` five keys (quo-setup → engineer, test-writer, pm); Spec Bee `t1=Doc` children titled exactly `PRD` / `SDD` (quo-plan, quo-write-prd/sdd → pm).

## (d) Single points of failure

A literal or heading that, if renamed on one side only, silently breaks a chain (no error surfaces; the consumer simply stops matching). Ordered by blast radius.

| # | Literal / heading | Chain broken if renamed | Where it is defined vs consumed |
|---|---|---|---|
| S1 | `## Design question` | Chain 4 step 5 / 4a: any other heading is persisted as a completion and the partial diff goes to review | `agents/engineer.md` R-148/149 ↔ FX-DQ-1, FX-POSTC-76 |
| S2 | `## Files changed` → `## Source paths to fingerprint` | Chain 5 step 1: writer falls back to `git diff --name-only HEAD` and stops on unrelated edits; empty heading reads as a supplied set | R-156, R-209/210 ↔ FX-PROMPT-34..40 / EX-DPS-4..17 |
| S3 | `## Blast radius` (one string at every hop) | Chain 4 step 6: `/quo-engineer-review` loses its site-reconciliation check; explicitly called out (FX-PROMPT-26) | analyst `### Blast radius` → orchestrator → engineer R-165 / pm R-403 / code-reviewer R-467 |
| S4 | `## Engineer's completeness evidence` + the phrase "sweep-shaped" | Chain 4 step 6: an unnamed sweep silently loses the completeness check (FX-PROMPT-24) | R-400..402, R-464..466 |
| S5 | `### Deferred refinements`, `None`, and the three destination annotations (`addressed-now-in-this-Issue|Task`, `defer-to-existing-ticket-body: <id>`, `defer-to-new-Issue`) | Chain 2: bullets not parsed → deferral gate fires empty; already two spellings exist (FX inc. 4) | R-085..093, R-445..454 ↔ FX-DEFC, FX/EX ledger + gate |
| S6 | `Analyst verdict:` + four values | Chain 4 step 2 preamble; `recommend-as-stated`/`escalate-to-user` also gate the `None` shape of S5 | R-084, R-097..100 ↔ FX-ANA-23..30, FX-DEFC-5 |
| S7 | Fixed lines `No invariant added, removed, or weakened.` and `None — the recommendation leaves no policy question open.` | Chain 4: "swept and found nothing" becomes indistinguishable from "never swept"; preamble count rule keys on the second | R-047, R-071 ↔ FX-ANA-21, FX-ANA-31, FX-PROMPT-28, R-167 |
| S8 | Routing trailers `**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**` | Chain 1 step 2: orchestrator has no authoritative prescription to follow literally | review skills ↔ FX-REVIEW-5/6, EX-BEEREV-5 |
| S9 | `blocker` / `suggestion` / `nit`; `trivial-tweak` / `refactor-locally` / `re-architect`; `[preferred]`; `[introduces-mechanism]` | Chain 1 steps 3–4: malformed tags collapse to row 1 → gate (d) on everything; a dropped `[introduces-mechanism]` demotes row 2 to orchestrator judgement (R-472) | review skills / R-469 ↔ FX-ROUTE-1..5, -33..38, -48, -116 |
| S10 | `### Second-order effects` / `#### <invocation scope>` / `No second-order effects identified.` / `None identified.` | Chain 1 side-channel: narrative nests inside the field or is dropped; unconditional field renders wrong | R-392..395, R-440..444, R-473..476 ↔ FX-SUM-8..15 / EX-SOE |
| S11 | `## Perturbations` / `None` | Chain 5 step 5: sibling perturbation cannot be attributed → every such movement hits the unexplained gate | R-235..237 ↔ FX-MOVE-19..24 / EX-MOV-27..29 |
| S12 | `## Compromise <n>`, the five field labels, and Decision values `User picked Accept the limitation`, `User picked Defer to follow-up Issue`, `Orchestrator picked path (x) — highest-quality`, `User overrode auto-route after post-completion challenge (depth misjudgment)`, `User accepted under-enumeration after post-completion challenge` | Chain 1 steps 6–7: PHASE 2/3 checks, PM tracker check, and `**Accepted compromises**` rendering all pattern-match these | FX-TRACK-12..30 / EX-TRK-7..15 ↔ FX-POSTC-26..33, R-427..429, FX-SUM-22 |
| S13 | SR gate labels `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, `File follow-up Issue to surface the missing path`, `Accept the under-enumeration and proceed`, `Pause to discuss` | Chain 1 step 7: Trigger D branches byte-match these | FX-SRGATE-12..15, -19 ↔ FX-TRACK-66..76 |
| S14 | `[compromise-challenge]` / `[design]` / `[defect]` | Chain 1 step 7: recovery gates fire only on `[compromise-challenge]`; preamble keys on it | FX-POSTC-51, -61 ↔ FX-SRGATE-1 |
| S15 | Commit subject token `(<issue-id>)` in `Fix issue: <title> (<issue-id>)` (fix); `(<task-id>)` (exec) | Chain 6: checkpoint `--grep` and GH `--grep` return nothing; one-per-Task count breaks | FX-CLOSE-19/20 ↔ FX-CKPT-14, FX-GH-20/21; EX-CLEAN-13 |
| S16 | Manifest filename `run-state-quo-fix-issue-<repo-dir-name>.md` / `run-state-quo-execute-<bee-id>.md` and field labels `**Unit scope:**`, `**Pre-session SHA:**`/`**Pre-Bee SHA:**`, `**Compromise tracker:**`, `**Progress:**`, `**Next unit:**`, `**Multi-Epic run mode:**` | Chain 3: post-compaction reader cannot find/parse the manifest; SHA scoping and tracker path lost | FX-MAN-7, -27..40 / EX-MAN-8, -20..31 ↔ FX-CKPT-15, -19; FX-SUM-18; EX-CKPT-24; EX-POST-6 |
| S17 | Tracker filename `compromises-YYYYMMDD-HHMM-<short-suffix>.md` (notation already drifts, EX inc. 10) | Chain 1 step 6 and Chain 3: path recorded in manifest must match what is written | FX-TRACK-7 / EX-TRK-5 ↔ FX-MAN-34 / EX-MAN-27 |
| S18 | TaskList name classes/prefixes `analyst-`, `engineer-`, `test-writer-`, `doc-writer-`, `code-reviewer-`, `test-reviewer-`, `doc-reviewer-`, `pm-`, `aborted-`, `defer-`, `gate-`, `*-postcomp-<n>`, suffixes `-r<n>` / `-rev<n>` / `-r<k>` | Chains 2, 3 step 5, 5: Engineer precondition, Phase C gate, deferral Step 1, close-out sweeps, recovery arms all prefix-match these — and the whole class currently has no carrier where TaskList is disabled | FX-TASK / EX-TL ↔ FX-ENGPRE-1, FX-MOVE-15, FX-HYG-29, FX-CLOSE-21, FX-RECOV-8..29 |
| S19 | `context_gauge.py` outputs `no-reading` / `stale` / `missing`, exit `2`, modes `stop-threshold` / `read --session-id` / `write-opt-out`, marker `context-guard-opt-out`, gauge file `context-usage-<session_id>.json` with `session_id`, `context_window.used_percentage` | Chain 3 step 4: a renamed output falls into the "unexpected stdout → stop" branch every boundary | quo-setup helper ↔ FX-GUARD-14..37 / EX-CWG-14..27 |
| S20 | `Run /quo-setup first.`; contract keys `## Documentation Locations` / `## Build Commands` and the twelve bullet keys | Every chain's precondition; five roles read the keys directly | FX-PRE / EX-PRE ↔ R-024, R-132, R-173..179, R-192/193, R-253/254, R-288, R-304/305, R-410 |
| S21 | `## Doc divergence noted` | Doc Writer treats the section as a correction directive; Section 6 confirms consumption | `/quo-file-issue` ↔ FX-ROLES-14, FX-DOCV-4 |
| S22 | `### Feature: <title>` / `## Per-feature scope` / `## Per-feature design`; Spec child titles `PRD` / `SDD` | Doc-writer idempotency; `/quo-plan-from-specs --feature`; scoped-marker scoping; PM spec-source walk | R-287..303, R-329/330 |
| S23 | `<scoped-marker-resolver-path>`, `<compromise-tracker-path>` placeholders; helper exit `0`/`2` and `"scoped"` JSON key | PM cannot run its Path A/B check or tracker check; Path A hard-fails vs Path B falls back | FX-SCOPED / EX-SMW ↔ R-358, R-366..370, R-426 |
| S24 | `## Authoritative design directive` (label the Engineer keys on) and `## Prior proposal and user feedback` | Chain 4 steps 3–4 and 4a: engineer.md's directive-wins rule keys on the heading; Analyst revise shape keys on the section | R-126 ↔ FX-PROMPT-9; FX-ANA-48..50 ↔ R-018 |
| S25 | `reference_materials` `{value, resolver}` and resolver names `github-issue` / `linear-issue` / `url` / `file-path` / `bees` | PM spec-source resolution; GH block scoping | R-325..334 ↔ FX-ROLES-20..23, FX-GH-13..16 |
| S26 | `no issues found` / `Post-completion review: no issues found`; `no spec drift surface to review for this Issue` | Post-completion step 4 branch; Section 6 / summary confirmation | FX-POSTC-56, -68 / EX-POST-36, -44; R-344 ↔ FX-DOCV-3 |
| S27 | `Encode deferral: /quo-<skill> — <N> deferral(s) encoded`; `## Deferred from /quo-<skill> run (<YYYY-MM-DD HH:MM>)`; `skipped: nothing staged` | Chain 2 step 5: checkpoint's bare-`git log -1` warning and the helper's success test key on these | FX-HYG-41, -65, -68 / EX-DHG-17, -27, -28 |
| S28 | `No code issues found.` (Phase A exit literal) | Chain 1 in fix Phase A: only fix-issue cites this string; no review skill or role row in the inventory emits it — verify it exists upstream or the exit test degrades to the numbered-list-empty reading (FX-LOOP-19) | FX-LOOP-16 (no emitter row) |
| S29 | Gate option labels shared across two gates: `Fix in this session` / `File as issue tickets` (+ `Skip` vs `Encode in an existing ticket body`) | Recovery from a stranded `gate-*` task via `metadata.activity` cannot tell the gates apart (EX inc. 8) | FX-HYG-34 / FX-POSTC-71 |
| S30 | Writer wording `"no Engineer Agent will be dispatched for this Issue|your Subtask's implementation dependency|this Bee while you are running"` vs forbidden `"the source tree is frozen"` | Role files' execute-mode branch expects these exact scopings (R-201..206) | FX-PROMPT-31/32 / EX-DPS-18/19 |

SPOF count: 30 (S18 is a class of ~14 prefixes; S12 a class of ~10 strings).
