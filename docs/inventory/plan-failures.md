# Failure inventory — `/quo-plan` and its three sub-skills (ticket b.7ib)

Repo-only working document for the minimal rewrite of `skills/quo-plan/SKILL.md`, `skills/quo-write-prd/SKILL.md`, `skills/quo-write-sdd/SKILL.md`, and `skills/quo-spec-review/SKILL.md`. Nothing here ships. It is the input to the draft and the anchor for its cold reviews (A1/A2 in the adapted REWRITE-BRIEF §6).

Standard: CLAUDE.md `## How skill prose is written`. A rule survives when it is one of the five kinds (contract, state carrier, structural guard, operator policy, earned rule) or when a run failure earns it under the three questions (how often, does it announce itself, did the agent recover unaided). Everything else goes, or becomes a goal sentence with its reason.

Line numbers are those of the four bodies at commit `e15efe2`.

## 1. The shape the dispositions assume

These six design choices decide many dispositions below. They are proposals for Checkpoint 2, not settled.

- **S1 — One run-state manifest per `/quo-plan` run.**
  - Path: `<tempdir>/.quorum/run-state-quo-plan-<repo-dir-name>.md`. The discriminator is fixed at run start (overseer note, 2026-09-24).
  - It sits under the existing run-state-manifest exception, outside the lead-statement mirror.
  - Contents: the feature title; the approved scope's path; the Epic-draft and Plan-Bee-body-draft paths; the Spec Bee and Doc child IDs; the Plan Bee and Epic IDs as each is created; the phase; `## Obligations` (deferrals); and `## Open gate`.
  - **Lifecycle.** At run start the skill reads any existing manifest.
    - If it is absent, or its phase is `complete`, the skill overwrites it.
    - If it records an unfinished run, the skill gates **Resume** (continue from the recorded phase and IDs) or **Start fresh** (overwrite; the old tickets stay as they are). That is a real decision, because only the user knows whether the old run is abandoned.
  - This covers what S3 does not: a crash or session loss between Plan Bee creation and the last Epic. The old 5a detection caught that window; now the manifest carries it (cold review, finding 1).
  - Accepted collision: two `/quo-plan` runs in one repo at the same time.
- **S2 — Gates only at real decisions**, each fronted by the manifest `## Open gate` write:
  - resume or start fresh (only when an unfinished manifest exists);
  - scope approval (one gate, replacing the 0a distill gate and the Step 3 scope gate);
  - Spec Bee reuse (only when a candidate matches);
  - plan approval (one per review round);
  - deferral hygiene (only when obligations are open);
  - next steps.

  Writers invoked inline fire no gates.
- **S3 — Plan tickets are created after approval.** The Epic decomposition and the Plan Bee body are drafted to scratch files, reviewed, and approved. Only then are they written as the Plan Bee and its Epics. A cancelled run leaves no Plan Bee or Epics. That removes the Cancel-at-gate failure the Plan-Bee reuse machinery was built for, and narrows the remaining risk to the post-approval creation window, which the S1 manifest carries.
- **S3a — Approved Spec Bees are immutable to `/quo-plan`; Doc children stay `drafted` until approval.**
  - `/quo-plan` reuses a matching Spec Bee only while it is still `drafted`. A `ready` match gets a new Spec Bee, and revising an approved spec in place stays with the solo writers (`/quo-write-prd <spec-bee-id>`, `/quo-write-sdd <spec-bee-id>`).
  - An inline writer that updates an existing child sets it back to `drafted`. On approval `/quo-plan` promotes the children, then the Spec Bee (SV12).
  - This replaces the Checkpoint 3 draft's ready → drafted demotion (overseer, 2026-09-24; F22). That demotion let a re-plan against a `ready` Spec Bee overwrite approved PRD/SDD bodies before any gate. A Cancel then lost them, and any existing Plan Bee referencing the Spec Bee read drafts.
- **S4 — Both reviews run together, once per round, before the approval gate.** `/quo-spec-review` reviews PRD+SDD; the cold plan reviewer reviews PRD+SDD plus the drafted Epics and Plan Bee body. Both see the same state, which settles the 2026-09-16 ordering defect (item 10). A revision round re-runs only the reviewer whose input changed. **Trade-off:** b.7ib proposed a substance review of PRD/SDD before the Epics, then a short decomposition check. S4 instead drafts the Epics on a spec that may still carry the design errors the plan reviewer catches, so a spec-level fix can force an Epic redraft. The gain is one review pass, one gate, and no reopen loop between two sequential reviews. This is a Checkpoint 2 decision.
- **S5 — Findings route by where the fix lands, and trivial fixes skip the writer.**
  - For each finding, the orchestrator picks the smallest enumerated fix path that fully fixes it. The reviewer's `[preferred]` is an input to that pick, as on the execution side.
  - When the chosen path is `trivial-tweak`, the orchestrator applies it directly: a Doc-child body update, or an edit to the Epic or Plan-Bee-body draft.
  - Otherwise the fix goes to the one writer whose document it changes, or to the orchestrator for the drafts.
  - This gives the depth tag its first reader on the planning side.
- **S6 — The sub-skills keep a solo path, and every gate there is manifest-fronted too.**
  - Solo `/quo-write-prd` and `/quo-write-sdd` run `/quo-spec-review --doc` before a single approval gate, and promote on approve.
  - F10's failure point, a review returning and then the gate, is exactly that shape. So each solo writer writes its own run-state manifest (`run-state-quo-write-prd-<repo-dir-name>.md`, `run-state-quo-write-sdd-<repo-dir-name>.md`) under the same exception, and fills `## Open gate` before its gate. Recommendation for Checkpoint 2; the alternative, an unguarded solo gate, repeats F10.
  - Solo `/quo-spec-review` returns findings and stops. It fires no gate.

## 2. Failure evidence register

Each earned or evidence-backed rule cites one of these. "Observed" means a real run showed the failure; "predicted" means a reviewer or designer anticipated it and no run is recorded showing it.

| ID | Failure | Source | Observed? | How often | Announces itself? | Recovered unaided? |
|---|---|---|---|---|---|---|
| F1 | Planning discovery re-asks what the conversation already settled; rationale and rejected alternatives lost across the planning boundary | b.31f Problem 2 | Observed | Every mid-conversation run | Partly: the user sees re-asking, not the later loss | No |
| F2 | Planning mutates project PRD/SDD at plan time | b.31f Problem 1 | Observed | Every run under the old design | No | No |
| F3 | `/quo-plan` delegated Plan Bee creation to `/quo-plan-from-specs`, which re-plans every feature in cumulative docs | b.mu9 | Observed once | Rare | No: b.mu9 says it "surfaces silently"; an attentive author caught it | Yes: the author worked around it |
| F4 | Vague "search the hive" prose makes the agent invent bees verbs (`bees list-tickets`) | b.tsj | Observed in `/quo-file-issue`; `/quo-plan` site found by audit | Common when no verb is named | Yes (exit 2) | Mostly, after a retry |
| F5 | `AskUserQuestion` used for free-text answers renders a confusing UI | b.iaz | Observed in `/quo-setup`; `/quo-plan` sites by audit | Per affected prompt | Yes | With user confusion |
| F6 | Same-session continuation into the next heavy skill burns context | b.wc4 | Observed | Common on big features | No | No |
| F7 | Inline multi-paragraph `--body` trips Claude Code's command-injection guard | b.c4z | Observed | Every multi-paragraph body | Yes (permission prompt) | Only with the user approving |
| F8 | Hardcoded `.bees/plans/` stages nothing when the hive lives elsewhere | b.dp2 (8b43ae2) | Observed | Every run with an out-of-repo hive | No | No |
| F9 | Specs-hive ticket files left uncommitted | db011e1 | Observed | Every run with an in-repo Specs hive | No | Yes: db011e1 says the agent worked around the gap pragmatically; the rule makes the fix reliable |
| F10 | Orchestrator narrates the gate after a review returns and yields without calling `AskUserQuestion` | b.sfy, b.fpm, b.wii | Observed three times, all at `/quo-plan` Step 4c (b.sfy's planning session; b.fpm "verified — this is the reported failure site"; b.wii "during `/quo-plan` for b.tip") | Common | No (the run stalls) | No |
| F11 | Plan-level substance errors (framing, approach, decomposition) pass a checklist spec review | b.bjp; 2026-09-16 run (the plan reviewer caught three real design errors) | Observed | Common | No | No |
| F12 | Items the run defers "to later" vanish at the session boundary | b.dgq | Observed in a `/quo-plan` run | Occasional | No | No (the user's question caught it) |
| F13 | Stale `in_progress` self-tracking TaskList tasks after a standalone review | b.61t | Observed | Common with TaskList on | Yes (UI) | n/a. The reader is gone: the TaskList tools are off by default |
| F14 | Inline-path detection keyed on the distill heuristic would skip the solo spec-review gate | 3cd8a25 | Predicted by review | — | — | — |
| F15 | Re-running after Cancel at the plan-review gate duplicates the Plan Bee and Epics; the reconcile's cascade delete destroys Task work; a kept Epic's Tasks carry dangling deps | f0abfdf, b.9q3, b.bbw | Predicted by review ("has likely not yet manifested") | — | — | — |
| F16 | Two runs Encoding into one ticket body stack identical headings | b.r3x | Predicted ("forward-looking") | — | — | — |
| F17 | Users don't know they can route deferral items differently | b.17n | Predicted by review | — | — | — |
| F18 | Specs promote without any review | b.uxa, b.49g | Design gap, closed by operator decision | — | — | — |
| F19 | Depth and `[preferred]` emission shape drifts across reviewers | b.11z, b.94j, t2.ut9.* | Predicted; the planning side had no reader for either tag until S5 gives it one | — | — | — |
| F20 | 2026-09-16 planning run defects 1–11 (b.7ib `## Evidence…`), including ~25 gates with ~9 real choices | b.7ib | Observed | One run | Mixed | Mixed |
| F21 | b.eid: plan path lacks lifecycle / policy-decision enumeration; reviewers rediscover sites | b.eid (b.jp2, b.55r, b.5ux) | Observed three times | Occasional | No, it shows up as late review churn | Only when a reviewer happened to look |
| F22 | Re-planning against a reused `ready` Spec Bee overwrites approved specs before any gate; a Cancel loses them, and existing Plan Bees that reference them silently read drafts | Overseer review of the Checkpoint 3 draft (2026-09-24) | Found in design review, not in a run | Often enough: every re-plan of a feature whose Spec Bee was approved | No | No |

Operator decisions that stand as policy (kind O): O1 the scratch-file convention, rule 4 (b.dkw); O2 the commit subject and `Epic N — <title>` labels (9ca6234); O3 the warning marker on divergent-verdict preambles (6a806a2 restored it after 2c9b604 dropped it); O4 a spec review gates spec promotion and a cold plan review gates plan promotion (b.49g, b.bjp, and b.7ib "keep the cold plan reviewer"); O5 idempotent re-runs (CONTRIBUTING principle 3). For `/quo-plan` this now means an unfinished run's `drafted` Spec Bee is reused; an approved (`ready`) Spec Bee is never reused or changed by `/quo-plan`, per F22; O6 free-text questions in prose, never `AskUserQuestion` (CLAUDE.md `## AskUserQuestion usage`); O7 heavy-to-heavy boundaries default to a fresh session (b.wc4); O8 never push, never stage beyond the run's own paths.

## 3. Rule inventory

Kinds: **C** contract · **S** state carrier · **G** structural guard · **O** operator policy · **E** earned by a run failure · **P** procedure or how-to · **X** rationale or explanation · **D** duplicate or restatement · **K** external-CLI recipe · **T** TaskList machinery · **A** counter-anchor or pre-commitment prose.

Dispositions: **Keep → SVn** (carried as written, contract or guard), **Goal → SVn** (carried as a goal sentence with its reason), **Go** (with the reason). SV groups are listed in §4.

### 3.1 `skills/quo-plan/SKILL.md` (896 lines)

| ID | Lines | Rule | Kind | Evidence | Disposition |
|---|---|---|---|---|---|
| P1 | L1-5 | Frontmatter `name`, `description`, `argument-hint` | C | 11fc49f, 2cafbda | Keep → SV1 (description revised for the new flow) |
| P2 | L9 | Overview: idea → broken-down plan, any size | X | — | Go: describes, prescribes nothing |
| P3 | L11 | Tip routing single-feature on-disk specs to `/quo-plan-from-specs`, incl. `--feature` | X | b.mu9 (ec055ed) | Go: user orientation README already carries; F3's cause is gone (specs no longer live in cumulative docs) |
| P4 | L15-16 | Usage lines | D | — | Go: the `argument-hint` carries it |
| P5 | L22 | Judge whether the session already holds the feature's context | E | F1 | Goal → SV3 |
| P6 | L24-28 | Signals that should fire the distill branch | P | F1 | Goal → SV3 (one clause: substantive scope in the conversation or argument) |
| P7 | L30 | Err toward distilling; future maintainers must not tighten; keep in lockstep with the writers | E + A | F1 | Goal → SV3 for "err toward distilling". The counter-anchor and the lockstep clause go: the inline writers no longer run their own distill branch |
| P8 | L32-35 | Heuristic output feeds branches 0a/0b | P | — | Go: SV3 states one flow |
| P9 | L37 | Steps 3–7 identical on both branches | D | — | Go |
| P10 | L41 | Distill branch skips the Step 1 prompt and the Step 2 questions | E | F1 | Goal → SV3 |
| P11 | L43-52 | Distilled scope covers eight named items | C | F1 | Keep → SV3 (the approved-scope sections are what both writers read) |
| P12 | L54 | Render each item under a heading; empty items say `none` explicitly | C | F1 | Keep → SV3 |
| P13 | L56-60 | Distill gate: Approve / Revise / Cancel | P | F20 defect 2 | Go: merged into the single scope gate (SV4) |
| P14 | L62 | On approve, carry the distillation into Step 3 | P | — | Go: one flow |
| P15 | L66 | Restart branch runs Steps 1–2 | P | — | Go: SV3 |
| P16 | L70 | Step 1 is restart-only | D | — | Go |
| P17 | L72-74 | Ask for prior context in prose, not `AskUserQuestion` | O | F5, O6 | Goal → SV3 (prose questions stated once) |
| P18 | L76-82 | Wait for the reply; use what the user points to | P | — | Goal → SV3 |
| P19 | L86 | Step 2 is restart-only | D | — | Go |
| P20 | L88-92 | Start from the description; with no arguments, ask what to build | P | — | Goal → SV3 |
| P21 | L94-98 | Check for project PRD/SDD; ask if unknown; read them if given | P | c014d8d | Goal → SV5 |
| P22 | L100-103 | Research CLAUDE.md, source, references | P | — | Goal → SV5 |
| P23 | L104-118 | Check overlapping Plan Bees and open Issues; two query recipes; discuss overlap | K + E | F4 | Goal → SV5, with bees orientation (enumeration is `bees execute-freeform-query`; `report:` adds fields; one-line flow-style YAML). The recipes go |
| P24 | L119 | If PRD/SDD exist, relate the feature to them | D | — | Go: P21 |
| P25 | L121-126 | Four clarifying questions as a prose list | O | F5, O6 | Goal → SV3 |
| P26 | L128 | Don't proceed until you and the user agree what the feature is | E | F1 | Goal → SV4 (the scope gate is that agreement) |
| P27 | L132-136 | Scope statement: What / Why / Acceptance criteria / Out of scope | C | — | Keep → SV3 (folded into the approved-scope sections, P11) |
| P28 | L138-142 | Scope gate "Does this scope look right?"; iterate | E | F20 defect 2 | Keep → SV4 as the single scope gate |
| P29 | L146 | Step 4 flow and why specs are tickets: side-effect-free, parallel-safe | X | F2 | Goal → SV6 (one reason clause) |
| P30 | L150 | 4a gates go through two-step `TaskCreate` | T | F10 | Go: TaskList tools are off by default; replaced by the manifest-fronted gate (SV19) |
| P31 | L152-166 | Detect an existing Spec Bee by title; query recipe | O + K | O5 | Goal → SV6; recipe goes |
| P32 | L168 | Normalized title match; err toward reuse; ask when ambiguous; maintainers must not tighten | O + A | O5, F22 | Goal → SV6, narrowed: err toward reuse among `drafted` Spec Bees only; a `ready` match is never reused (F22). Counter-anchor goes |
| P33 | L170-174 | Reuse gate: `Reuse existing Spec Bee` / `Create a new Spec Bee anyway` / `Cancel` | C | O5, F22 | Keep → SV6 (fires only on a `drafted` candidate) |
| P34 | L176 | Create: brief body to scratch, never deleted; no PRD/SDD content in the Spec Bee body | O + C | O1 | Keep → SV6 / SV18 |
| P35 | L178-190 | Create snippets | K | — | Go: orientation, not recipes |
| P36 | L192 | No `--reference-materials` on the Spec Bee; the two-hop explained | C + X | — | Go: nothing tells the agent to set one; the explanation belongs to readers |
| P37 | L194 | Capture the Spec Bee ID for later steps | S | — | Keep → SV19 (the manifest carries it) |
| P38 | L198 | Delegate PRD/SDD authoring to the writers; `/quo-plan` never creates the Doc children | C | b.31f | Keep → SV7 |
| P39 | L200 | One byte-identical `args` payload for both writers; abort and re-author on a mid-run scope change; asymmetric revise carve-out | P | — | Goal → SV7 ("both writers read the same approved scope"); the byte-identity and carve-out prose go: the scope file is the one payload |
| P40 | L202-209 | `args` shape: `spec-bee-id:` / `distilled-scope:` | C | — | Keep → SV7 (inline contract; scope passed by path or inline, settled at draft) |
| P41 | L211 | Payload covers the approved scope plus prior context and rationale | C | F1 | Keep → SV7 |
| P42 | L213-217 | Invoke `/quo-write-prd`; capture `prd_ticket_id`, `prd_status`, `action` | C | — | Keep → SV7 (return fields) |
| P43 | L219-224 | Then `/quo-write-sdd`, sequentially (children-list race); capture fields incl. `research_needed` | C | — | Keep → SV7 (sequential; return fields; the race is a stated reason, not a recorded failure) |
| P44 | L226 | Writer error or cancel aborts Step 4; re-run resumes via idempotency | P | O5 | Goal → SV7 (the manifest records progress; re-run is idempotent) |
| P45 | L228 | Captured statuses gate Spec Bee promotion | D | — | Go |
| P46 | L232 | Run spec review, then promote the Spec Bee | O | O4 | Keep → SV8 / SV12 |
| P47 | L234 | Defensive check that both children are `ready` | P | — | Go: no failure recorded; under S2 `/quo-plan` promotes the children itself after approval |
| P48 | L236 | Spec review is the single end-to-end pass; writers skip theirs inline | O | O4, F14 | Keep → SV8 |
| P49 | L238 | Pre-commitment: `TaskCreate` first, then the prescribed tool | A + T | F10 | Go: prose pre-commitment exhausted (b.wii); the manifest-fronted gate replaces it |
| P50 | L240-242 | Invoke `/quo-spec-review <id>` with no `--doc`; read findings; approve path | C | O4 | Keep → SV8 |
| P51 | L243-248 | Revise: route PRD-only / SDD-only / cross-doc findings to writers | P | F20 defect 5 | Goal → SV10 (route by where the fix lands; cross-doc findings no longer go to both writers) |
| P52 | L252 | Follow the spec-review routing trailer literally; trailer wins over prose | G | F10 | Go: the trailer was a prose guard that did not hold; SV19 replaces it |
| P53 | L254-260 | Quick-reference table of the three trailer shapes | D | F10 | Go |
| P54 | L262-266 | Proceed-acknowledge / Revise / Proceed-anyway semantics; record overrides | C | 1324593 | Goal → SV11 (the approval gate offers approve-over-findings, recorded in the report) |
| P55 | L268 | Blockers gate promotion by default; suggestion/nit inform | C | — | Goal → SV11 (blockers make Revise the recommended choice) |
| P56 | L272 | Time-budget short-circuit (~10 items / ~3 turns) | P | predicted (b.49g) | Go: S2/S4 bound the loop (every round ends at a user gate; the confirming run re-reviews changed inputs only) |
| P57 | L274-286 | Promote the Spec Bee to `ready`; paired snippets for an identical command | C + K | — | Keep → SV12 (status transition); snippets go |
| P58 | L288 | Re-asserting `ready` is a harmless no-op | X | — | Go |
| P59 | L290-300 | End-of-Step-4 summary and findings buckets | D | — | Go: SV15 reports once |
| P60 | L302 | Step 5 uses the Spec Bee for `reference_materials` | D | — | Go: SV12 |
| P61 | L306 | Create the Plan Bee inline; never delegate to `/quo-plan-from-specs` | E | F3 | Go: F3 was rare and recovered, and its cause is gone (the spec is in bees, which `/quo-plan-from-specs` cannot read) |
| P62 | L310 | 5a gates go through two-step `TaskCreate` | T | F10 | Go (SV19) |
| P63 | L312-326 | Detect a `drafted` Plan Bee under the Spec Bee; query with `report: [..., reference_materials]` | K | F15; F20 defect 7 (the CLI rejects that `report` field) | Go: S3 removes the case; the recipe is also wrong |
| P64 | L328 | Parse `reference_materials`; err toward reuse | P | F15 | Go: S3 |
| P65 | L330-334 | Plan-Bee reuse gate | C | F15 | Go: S3 |
| P66 | L336-343 | Reuse-mode downstream behavior (update-or-create-or-delete) | P | F15 | Go: S3 |
| P67 | L345 | Body to a scratch file via `--body-file` (injection guard); never delete | E + O | F7, O1 | Keep → SV18 (stated once for every body) |
| P68 | L347 | Plan Bee body: short summary plus `## Anticipated doc impact` naming docs by contract key | C | 7c5d1ed, b.31f | Keep → SV12 |
| P69 | L348-352 | `reference_materials` = `[{"value":"<spec-bee-id>","resolver":"bees"}]` | C | b.31f | Keep → SV12 |
| P70 | L354 | Two-hop explanation; file-path shape moved to `/quo-plan-from-specs`; no body-as-spec branch | X | b.31f | Go: consumers own the explanation (operator: no body-as-spec mode) |
| P71 | L356 | `/quo-plan` emits no Scoped marker | X | b.31f | Go: nothing instructs emitting one |
| P72 | L358-378 | Plan Bee create snippets | K | 298e13c | Go |
| P73 | L380 | Plan Bee starts `drafted`; promoted after review clears | C | ec055ed, 5eab6af | Goal → SV12. Under S3 the Plan Bee is created after approval; the contract that remains is "`ready` only once the Epics exist and the plan is approved" |
| P74 | L384 | Reuse-mode note for 5b | P | F15 | Go: S3 |
| P75 | L386-393 | Epic decomposition rules: green, one outcome, vertical, refactor exception, granularity, testable AC | C | 0b69f1a, ec055ed | Goal → SV13 |
| P76 | L395-399 | Epic viability checklist: no testing / docs Epic; doc updates in scope | C | — | Goal → SV13 |
| P77 | L401-404 | Anti-patterns: untestable intermediate states; refactor mixed with feature | C | — | Goal → SV13 |
| P78 | L406 | One Epic is fine for a small plan | C | — | Goal → SV13 |
| P79 | L410 | 5c gate goes through two-step `TaskCreate` | T | F10 | Go (SV19) |
| P80 | L412 | Reuse-mode origin tags and cascade annotations in the Epic list | P | F15 | Go: S3 |
| P81 | L414-420 | Epic-approval gate: `Yes, create them` / `Modify the Epics` / `Cancel` | C | ec055ed | Go: merged into the plan-approval gate (SV11), which shows the Epic list alongside the reviews |
| P82 | L424 | Cascade gate goes through two-step `TaskCreate` | T | F15 | Go |
| P83 | L426 | Split Epic creation from promotion around the review (no `ready → drafted` demotion) | X | 1324593 | Go: S3 creates tickets after approval, so the split's reason is gone |
| P84 | L428 | Create Epics `drafted` via `--body-file`; no `--reference-materials` on Epics (CLI rejects it) | C + K | 94d54b7, bf4103e | Keep → SV12 for `drafted`. The CLI fact goes: `bees create-ticket --help` states it, and a misuse is rare, loud, and recovered |
| P85 | L430 | Reuse-mode routing | P | F15 | Go: S3 |
| P86 | L432 | Children-cascade guard and tier-homogeneous deps note | P | F15 | Go: S3 |
| P87 | L434-452 | Epic create snippets | K | 298e13c | Go |
| P88 | L454 | Title each Epic `Epic N — <short title>`; ordinal kept on reuse | C + O | O2 | Keep → SV12 (the reuse clause goes with S3) |
| P89 | L456-463 | Wire Epic `up_dependencies`; common blocking patterns; "what must be done first?" | C + P | 0b69f1a | Goal → SV12 (Epic↔Epic dependencies); pattern list goes |
| P90 | L465 | Capture the Epic ID list; the Plan Bee stays `drafted` | S | — | Keep → SV19 (the manifest carries created IDs) |
| P91 | L469 | Plan review fills the substance gap the checklist review leaves | E + O | F11, O4 | Keep → SV8 |
| P92 | L471 | Anti-overlap: prose-quality findings are out of the plan reviewer's lane and are dropped | C | F11 | Goal → SV8 |
| P93 | L473 | Pre-commitment before the reviewer's return | A + T | F10 | Go (SV19) |
| P94 | L477 | Dispatch a `general-purpose` background Agent; self-contained prompt; track in TaskList | C + T | F11 | Keep → SV8 (cold, read-only, self-contained); TaskList tracking goes |
| P95 | L479 | "Starting skeleton" intro | D | — | Go |
| P96 | L481-492 | Prompt: read the Spec Bee, PRD, SDD, Plan Bee, Epics by ID | C | — | Keep → SV8 (under S3 it reads the Epic draft file, not tickets) |
| P97 | L494-503 | Prompt: substance lane (framing, approach, decomposition, missing risks) | C | F11 | Keep → SV8 |
| P98 | L505-509 | Prompt: prose quality out of scope | C | F11 | Keep → SV8 (one sentence) |
| P99 | L511 | Prompt: read-only | C | — | Keep → SV8 (a prompt line, not a tool-level guard: the `general-purpose` agent has write tools) |
| P100 | L513-526 | Finding fields: severity, `target:`, fix paths with depth; severity and depth orthogonal | C | bfaecae | Keep → SV9 (severity, `target:`, depth-tagged fix paths; depth now has a reader under S5) |
| P101 | L528-545 | Finding and fix-path line shapes; optional `[preferred]` | C | bfaecae, 21d6b43, 6fc1c28 | Keep → SV9, including `[preferred]`, which S5's pick now reads (cold review, finding 3) |
| P102 | L547-557 | Depth bucket calibration | C | bfaecae | Keep → SV9 (condensed; S5 keys on `trivial-tweak`) |
| P103 | L559-574 | Worked example | C | bfaecae, 21d6b43 | Keep → SV9 (one short example as template) |
| P104 | L576-591 | Verdict line `Plan-review verdict: <approve \| revise-recommended \| escalate-to-user>` and semantics | C | 5eab6af | Keep → SV9 |
| P105 | L593-597 | Clean shape: `No plan-review issues found.` plus verdict | C | 5eab6af | Keep → SV9 |
| P106 | L599-651 | Three routing trailers with two-step `TaskCreate`; `(Recommended)` placement keyed to the verdict | G + T | F10 | Go: the trailers were a prose guard; SV19 replaces them. The recommendation-by-verdict survives as a goal in SV11 |
| P107 | L653 | Wait for the completion notification | P | — | Go: the harness wakes the orchestrator on completion |
| P108 | L657-661 | Preamble by verdict; warning marker on `escalate-to-user` | O | O3 | Keep → SV11 |
| P109 | L663-668 | Plan-review gate: `Approve & promote Plan Bee (acknowledge findings)` / `Approve anyway & promote Plan Bee (override blockers)` / `Revise` / `Cancel`; Cancel leaves drafted tickets for reuse | C | 5eab6af, 1324593, f0abfdf | Keep → SV11 as the plan-approval gate; labels re-cut at draft. The Cancel clause changes under S3: nothing was created |
| P110 | L670 | Mark the plan-reviewer TaskList task completed | T | — | Go |
| P111 | L674-694 | Revise routing by `target:` (PRD / SDD writer; Plan-Bee body and Epics by the orchestrator); snippets | C + K | f0abfdf | Keep → SV10 (by target, plus S5's direct trivial edits); snippets go |
| P112 | L696 | One-pass spec-review re-run cap after a writer revision; three-choice gate on re-run blockers | P | predicted | Go: S4 re-runs the changed reviewer once per round, and the plan-approval gate is the only gate |
| P113 | L698 | Skip the spec-review re-run when only the Plan Bee or Epics changed | P | — | Goal → SV10 (re-run only the reviewer whose input changed) |
| P114 | L702 | Re-dispatch the plan reviewer with `-rev<n>` task names | T | — | Goal → SV10 for the re-dispatch; naming goes |
| P115 | L706 | Plan-review time-budget short-circuit | P | predicted | Go: as P56 |
| P116 | L710-720 | Promote the Plan Bee on either Approve; snippets | C + K | 1324593 | Keep → SV12 (status transition); snippets go |
| P117 | L722 | Plan Bee `ready` presupposes a `ready` Spec Bee | C | — | Keep → SV12 |
| P118 | L726 | Report: Plan Bee, Epics with status and deps | C | ec055ed | Goal → SV15 |
| P119 | L728-740 | Six findings buckets across the two gates | P | 1324593 | Goal → SV15 (report accepted and overridden findings once) |
| P120 | L744 | 5g gates go through two-step `TaskCreate` | T | F10 | Go (SV19) |
| P121 | L746 | Per-skill TaskList convention intro | T | — | Go |
| P122 | L748 | `defer-*` ledger tasks: created, carried, completed | T + E | F12 | Goal → SV14; the carrier moves to the manifest's `## Obligations` |
| P123 | L749 | `gate-*` task convention, per-fire uniqueness, yield discipline | T | F10; F20 defect 1 | Go: replaced by SV19 |
| P124 | L751 | Retroactively turn every report-bucket finding into a `defer-*` task | P | predicted (b.dgq) | Go as a sweep. Its intent moves to SV11: at the plan-approval gate, approving over a finding means won't-fix, and any finding the user wants fixed later becomes an `## Obligations` row there, so acknowledgement cannot silently absorb a deferral (cold review, finding 10) |
| P125 | L753 | Step 1: empty set → `Deferral hygiene: no deferred items.` | C | F12 | Keep → SV14 |
| P126 | L755-758 | Step 2: list the set; gate `Fix in this session` / `File as issue tickets` (inline `/quo-file-issue`) | C + E | F12 | Keep → SV14 |
| P127 | L759-777 | `Encode in an existing ticket body` with `## Deferred from /quo-plan run (<YYYY-MM-DD HH:MM>)`; body-file named after `defer-N`; snippets | C + K | F12, F16 | Keep → SV14 for the label and heading stem (the same stem the execution skills use), and the timestamp. Encode targets narrow to Plans- and Specs-hive tickets, since planning never writes project docs and SV17 stages only those hives (cold review, finding 4). `defer-N` filenames and snippets go |
| P128 | L779 | Options are non-exclusive per item via the auto-appended free-text slot | O | F17 | Goal → SV14 (one clause) |
| P129 | L781 | Hard stop until every deferral has a durable carrier; re-fire on failed routing | E | F12 | Keep → SV14 |
| P130 | L783 | Fresh-session recommendation preserved | D | — | Go |
| P131 | L787 | Step 6 gate goes through two-step `TaskCreate` | T | F10 | Go (SV19) |
| P132 | L789-798 | Next-steps menu: fresh session recommended; same-session opt-in for one or two Epics | O + C | F6, O7 | Keep → SV16 |
| P133 | L802 | Stage in-repo hive paths only; never hardcode `.bees/…` or `docs/` | E | F8, F9 | Keep → SV17 |
| P134 | L804 | The docs-changed branch effectively never fires | X | — | Go |
| P135 | L808-812 | Resolve both hives; stage whichever live in-repo; nothing to commit → `Plan stored in bees; no in-repo changes to commit.` | E + C | F8, F9 | Keep → SV17 (via `hive_commit.py resolve-hive-paths`, as the b.7ib evidence notes) |
| P136 | L814-846 | Multi-line hive-resolution snippets (`$(...)`, `case`, pipes) | K | 8b43ae2, 1302aeb, db011e1 | Go: they break the single-literal-command etiquette; the helper does the job |
| P137 | L848-872 | Commit subject `Plan feature: <title> (<plan-bee-id>)`; never `git add` with no arguments | O + E | O2, F8 | Keep → SV17 |
| P138 | L876-888 | Defensive fallback: stage `docs/` if a doc changed | P | — | Go: no failure; `/quo-plan` writes no project docs |
| P139 | L892-896 | Important notes: interactive; don't skip scope approval; one Epic fine; suggest `/quo-file-issue` for issues; body brief | D | — | Go: each restates SV4, SV13, or SV12. The file-issue suggestion is one clause in SV3 |

### 3.2 `skills/quo-write-prd/SKILL.md` (372 lines)

| ID | Lines | Rule | Kind | Evidence | Disposition |
|---|---|---|---|---|---|
| W1 | L1-5 | Frontmatter | C | 0721824 | Keep → SV1 |
| W2 | L9 | PRD is a `t1` child titled exactly `PRD`; twelve fixed sections | C | b.31f | Keep → SV20 |
| W3 | L11-14 | Two invocation paths | C | — | Keep → SV22 (solo and inline) |
| W4 | L16 | Shared flow summary | D | — | Go |
| W5 | L20-23 | Hard-fail `Run /quo-setup first.` without the Specs hive or `## Documentation Locations` | C | — | Keep → SV2 |
| W6 | L25 | Build Commands not required | X | — | Go |
| W7 | L27 | Stop and direct to `/quo-setup` | D | — | Go |
| W8 | L31 | Solo lands cold, inline distills | D | — | Go |
| W9 | L33 | Doesn't create the Spec Bee; ask for a missing ID in prose | C + O | O6 | Keep → SV22 |
| W10 | L37 | Detect prior context | E | F1 | Goal → SV22 (solo only; inline always has the approved scope) |
| W11 | L39-43 | Distill signals | P | F1 | Go: SV3's goal sentence |
| W12 | L45 | Err toward distilling; maintainers must not tighten; lockstep with `/quo-file-issue` | E + A | F1 | Goal → SV22; counter-anchor and lockstep go (reader `/quo-file-issue:77` updated) |
| W13 | L47 | Heuristic feeds Step 3 | D | — | Go |
| W14 | L51-61 | Read the Spec Bee; snippets | P + K | — | Goal → SV22; snippets go |
| W15 | L63 | Missing Spec Bee: stop; never create one | C | — | Keep → SV22 |
| W16 | L65 | Read architecture/customer docs by contract key when relevant | P | — | Goal → SV20 |
| W17 | L69-85 | Detect an existing `PRD` child (exact title, parent); query recipe | O + K | O5, 2cafbda | Goal → SV22 (idempotent by exact title); recipe goes |
| W18 | L87-91 | Zero → create; one → update; more → stop and ask | C | O5 | Keep → SV22 |
| W19 | L95 | Two branches | D | — | Go |
| W20 | L99 | Distill branch skips discovery | D | F1 | Go: W10 |
| W21 | L101 | Cross-check the distillation against the Spec Bee | P | — | Go: covered by SV22's read of the Spec Bee |
| W22 | L103-106 | Populate the twelve sections; rationale and decisions rarely `none` on distill; don't fabricate | C + E | F1 | Goal → SV20 |
| W23 | L108-111 | Draft gate Approve / Revise / Cancel | P | F20 defect 3 | Go: inline fires no gates; the solo path has one gate (SV23) |
| W24 | L113 | Why the draft gate and final gate both exist | X | F20 defect 3 | Go |
| W25 | L117 | Restart needs discovery; don't hallucinate | P | — | Goal → SV22 (a goal with its reason; no recorded failure) |
| W26 | L119-130 | Discovery question reference set | P | — | Go: SV22 asks for what the sections need, in prose |
| W27 | L132 | `AskUserQuestion` only for finite choices; no fake options | O | F5, O6 | Goal → SV22 (stated once) |
| W28 | L134 | Restart: rationale and decisions usually `none` | D | — | Go |
| W29 | L138 | Every section always rendered; explicit none when empty | C | b.31f | Keep → SV20 |
| W30 | L140-153 | The twelve section headings, in order, with the two mandatory `none` phrases | C | b.31f | Keep → SV20 (headings verbatim; exact `none` phrases go, `none — <reason>` stays) |
| W31 | L155 | Why sections 11–12 always appear | X | F1 | Goal → SV20 (one reason clause) |
| W32 | L159-163 | Quality bar: no implementation, no vague language, measurable AC | C | — | Goal → SV20 |
| W33 | L167-170 | What not to include | D | — | Go: W32 |
| W34 | L174 | `--body-file`, not inline `--body` (injection guard, quoting) | E | F7 | Keep → SV18 |
| W35 | L176-190 | Create the scratch dir; collision-resistant name; never delete | O | O1 | Keep → SV18 |
| W36 | L192-218 | Branch A: create `t1` child titled `PRD`, `drafted`, no `--reference-materials`; snippets | C + K | — | Keep → SV22 (title, parent, status); snippets and the CLI fact go |
| W37 | L220-236 | Branch B: replace the body in full; append only on request; snippets | C + K | — | Keep → SV22 (replace, not append); snippets go |
| W38 | L240-244 | Confirm gate Approve / Revise / Cancel | C | F20 defect 3 | Keep → SV23 (solo only, one gate) |
| W39 | L248 | 6a solo only; inline detected by the contract-shaped `args`, not the distill heuristic | C | F14 | Keep → SV22 (the inline contract identifies the path) |
| W40 | L250 | Run the gate on solo | D | — | Go |
| W41 | L252 | Pre-commitment `TaskCreate` | A + T | F10 | Go |
| W42 | L254-257 | Invoke `/quo-spec-review <id> --doc PRD`; loop on revise | C | O4 | Keep → SV23 |
| W43 | L261 | Follow the trailer literally | G | F10 | Go (SV19) |
| W44 | L263-268 | Findings semantics: none / acknowledge / revise / override, recorded | C | 1324593 | Goal → SV23 |
| W45 | L270 | Blockers gate promotion | C | — | Goal → SV23 |
| W46 | L274 | Time-budget short-circuit | P | predicted | Go: SV23 has one gate per round |
| W47 | L278-288 | Promote the PRD child to `ready`; snippets | C + K | — | Keep → SV22 (solo promotes; inline leaves promotion to the caller); snippets go |
| W48 | L290 | The caller owns the Spec Bee's promotion | C | — | Keep → SV22 |
| W49 | L294 | Idempotency via Step 2 | D | O5 | Go: W17/W18 |
| W50 | L296 | Re-invoking on a `ready` PRD re-asserts `ready` | X | — | Go |
| W51 | L300-312 | Solo report fields and findings buckets | C | — | Goal → SV23 |
| W52 | L314 | Inline returns the structured payload | D | — | Go: W58 |
| W53 | L318 | Stable inline contract for Skill-tool callers | C | — | Keep → SV22 |
| W54 | L320 | Inline always distills; restart never fires inline | C | F1 | Keep → SV22 |
| W55 | L324-333 | Input: Spec Bee ID, distilled scope, optional `findings:` in two item shapes | C | f0abfdf | Keep → SV22 (one findings shape: the verbatim finding lines, whatever the source) |
| W56 | L335-345 | Recommended `args` template | C | — | Keep → SV22 |
| W57 | L347 | Route order; both gates still fire inline | P | F20 defect 3 | Go: inline fires no gates (S2) |
| W58 | L351-355 | Output `prd_ticket_id`, `prd_status`, `action` | C | — | Keep → SV22 |
| W59 | L357 | How the caller consumes them | D | — | Go |
| W60 | L361-368 | Behavioral guarantees (idempotency, twelve sections, lifecycle, scratch, gates, skip 6a inline) | D | — | Go: restated where each rule lives |
| W61 | L372 | Future callers must keep the inline-distills invariant | A | — | Go |

### 3.3 `skills/quo-write-sdd/SKILL.md` (400 lines)

| ID | Lines | Rule | Kind | Evidence | Disposition |
|---|---|---|---|---|---|
| D1 | L1-5 | Frontmatter | C | 5ad4c5f | Keep → SV1 |
| D2 | L9 | SDD is a `t1` child titled exactly `SDD`; seven fixed sections | C | b.31f | Keep → SV21 |
| D3 | L11 | Why "SDD" not "SRD" | X | 1e72130 | Go |
| D4 | L13-16 | Two invocation paths | C | — | Keep → SV22 |
| D5 | L18 | Shared flow summary | D | — | Go |
| D6 | L22-25 | Hard-fail `Run /quo-setup first.` | C | — | Keep → SV2 |
| D7 | L27 | Build Commands not required | X | — | Go |
| D8 | L29 | Stop and direct to `/quo-setup` | D | — | Go |
| D9 | L33 | Explore research runs on both paths; distill replaces only the interview | C | F20 defect 6 | Keep → SV21 (research on first authoring; on a revise only when a finding questions the grounding) |
| D10 | L35 | Ask for a missing Spec Bee ID in prose | O | O6 | Keep → SV22 |
| D11 | L39 | Detect prior context | E | F1 | Goal → SV22 |
| D12 | L41-45 | Distill signals | P | — | Go |
| D13 | L47 | Err toward distilling; lockstep | E + A | F1 | Goal → SV22; lockstep goes |
| D14 | L49 | Heuristic feeds Step 4; Explore on both | D | — | Go |
| D15 | L53-63 | Read the Spec Bee; snippets | P + K | — | Goal → SV22 |
| D16 | L65 | Missing Spec Bee: stop | C | — | Keep → SV22 |
| D17 | L67 | Read docs by contract key for the Explore agent | P | — | Goal → SV21 |
| D18 | L71-87 | Detect an existing `SDD` child; recipe | O + K | O5, 2cafbda | Goal → SV22 |
| D19 | L89-93 | Zero / one / more handling | C | O5 | Keep → SV22 |
| D20 | L97 | Codebase findings must come from real research by an Explore agent | E | b.31f; b.eid evidence | Keep → SV21 |
| D21 | L99-106 | What to ask Explore: architecture, modules, patterns, data models, fixtures, config | P | — | Goal → SV21 (one list sentence) |
| D22 | L108 | Give Explore the architecture-doc paths | P | — | Goal → SV21 |
| D23 | L110 | Cite real names from Explore; never fabricate | C | — | Keep → SV21 (the grounding goal spec review checks; no recorded failure) |
| D24 | L112-116 | `RESEARCH NEEDED: <question>` inline tag | C | — | Keep → SV21 (reader: `research_needed` output and spec review) |
| D25 | L118 | Never smooth over ambiguity | D | — | Go: D24 |
| D26 | L122 | Two branches, same assembly | D | — | Go |
| D27 | L126 | Distill skips discovery | D | — | Go |
| D28 | L128 | Cross-check against the Spec Bee and Explore | P | — | Go |
| D29 | L130-135 | Populate the seven sections from the conversation and Explore; mark gaps | C | F1 | Goal → SV21 |
| D30 | L137-140 | Draft gate | P | F20 defect 3 | Go (S2) |
| D31 | L142 | Why two gates | X | — | Go |
| D32 | L146 | Restart needs discovery | P | — | Goal → SV22 |
| D33 | L148-155 | Discovery question set | P | — | Go |
| D34 | L157 | `AskUserQuestion` finite choices only | O | O6 | Goal → SV22 (stated once) |
| D35 | L159 | Restart: rationale and decisions usually `none` | D | — | Go |
| D36 | L163 | Every section always rendered | C | b.31f | Keep → SV21 |
| D37 | L165-179 | The seven section headings, in order, with their `none` phrases | C | b.31f | Keep → SV21 (headings verbatim) |
| D38 | L181 | Why every section is mandatory | X | F1 | Goal → SV21 (one clause) |
| D39 | L185-190 | Quality bar: real names, fixtures named, decisions traceable, SDD not PRD content | C | — | Goal → SV21 |
| D40 | L194 | `--body-file` reason | E | F7 | Keep → SV18 |
| D41 | L196-210 | Scratch dir, never delete | O | O1 | Keep → SV18 |
| D42 | L212-238 | Branch A create `t1` `SDD` `drafted`; snippets | C + K | — | Keep → SV22 |
| D43 | L240-256 | Branch B replace body; snippets | C + K | — | Keep → SV22 |
| D44 | L260-264 | Confirm gate | C | F20 defect 3 | Keep → SV23 (solo only) |
| D45 | L268 | 7a solo only; inline detected by `args` | C | F14 | Keep → SV22 |
| D46 | L270 | Run the gate on solo | D | — | Go |
| D47 | L272 | Pre-commitment `TaskCreate` | A + T | F10 | Go |
| D48 | L274-277 | Invoke `--doc SDD`; revise re-grounds research when needed | C | O4; F20 defect 6 | Keep → SV23 |
| D49 | L281 | Follow the trailer | G | F10 | Go |
| D50 | L283-288 | Findings semantics | C | — | Goal → SV23 |
| D51 | L290 | Blockers gate promotion | C | — | Goal → SV23 |
| D52 | L294 | Time-budget | P | predicted | Go |
| D53 | L298-308 | Promote the SDD child; snippets | C + K | — | Keep → SV22 |
| D54 | L310 | The caller owns the Spec Bee | C | — | Keep → SV22 |
| D55 | L314 | Idempotency | D | — | Go |
| D56 | L316 | `ready` re-assert | X | — | Go |
| D57 | L320-333 | Solo report incl. `RESEARCH NEEDED` list | C | — | Goal → SV23 |
| D58 | L335 | Inline returns structured payload | D | — | Go |
| D59 | L339 | Stable inline contract | C | — | Keep → SV22 |
| D60 | L341 | Keep in lockstep with `/quo-write-prd` | A | — | Go: one contract, stated in both, pinned by a test (§8) |
| D61 | L343 | Inline always distills; Explore still runs | C | F20 defect 6 | Keep → SV22 / SV21 |
| D62 | L347-356 | Input shape incl. `findings:` | C | f0abfdf | Keep → SV22 |
| D63 | L358-368 | `args` template | C | — | Keep → SV22 |
| D64 | L370 | Route order; gates still fire inline | P | F20 defect 3 | Go |
| D65 | L374-379 | Output incl. `research_needed` | C | — | Keep → SV22 |
| D66 | L381 | How the caller consumes | D | — | Go |
| D67 | L385-394 | Behavioral guarantees | D | — | Go |
| D68 | L398 | Future callers must keep the invariant | A | — | Go |
| D69 | L400 | Mirror `/quo-write-prd` in lockstep | A | — | Go (as D60) |

### 3.4 `skills/quo-spec-review/SKILL.md` (276 lines)

| ID | Lines | Rule | Kind | Evidence | Disposition |
|---|---|---|---|---|---|
| R1 | L1-5 | Frontmatter incl. `argument-hint` `<spec-bee-id> [--doc PRD\|SDD]` | C | 2301f3b, d962595 | Keep → SV1 (description revised) |
| R2 | L9 | Fresh-eyes review of a Spec Bee's `PRD`/`SDD` children; returns work items | C | F18 | Keep → SV24 |
| R3 | L11 | Both children by default; `--doc` scopes to one | C | — | Keep → SV24 |
| R4 | L13 | Orchestrator-invoked use; the callers own surfacing, loop-back, and the budget | C | d962595 | Goal → SV24 (callers named; budget clause goes) |
| R5 | L15 | Standalone use: output and stop | C | — | Keep → SV24 |
| R6 | L17 | Returns findings; never edits the PRD/SDD | C | — | Keep → SV24 |
| R7 | L21 | Hard-fail without the Specs hive | C | — | Keep → SV2 |
| R8 | L23 | Build Commands not required | X | — | Go |
| R9 | L27-30 | Parameters | C | — | Keep → SV24 |
| R10 | L32 | Ask for a missing ID in prose | O | O6 | Keep → SV24 |
| R11 | L36 | Findings carry a severity and a description | C | — | Keep → SV24 / SV9 |
| R12 | L38 | Thorough, not pedantic | P | — | Goal → SV24 (merged with R48–R50) |
| R13 | L42-46 | In scope: the two bodies and their consistency | C | — | Keep → SV24 |
| R14 | L48-53 | Out of scope: code, tests, project docs, the Spec Bee body | C | c970095 | Goal → SV24 (one clause) |
| R15 | L55 | No children → `No spec content to review` | C | — | Keep → SV24 |
| R16 | L61-69 | Resolve children by exact title; recipe | K | 06b7dcd | Goal → SV24 (exact titles `PRD`/`SDD`); recipe goes |
| R17 | L71 | `--doc` narrows the title match | D | — | Go |
| R18 | L73 | Zero → no content; more than one per title → stop | C | — | Keep → SV24 |
| R19 | L77-81 | The bees body is the source of truth, not any file on disk | C | 06b7dcd | Keep → SV24 |
| R20 | L85 | A missing section (not an explicit none) is a `blocker` | C | — | Keep → SV24 |
| R21 | L89 | Cite the section heading | C | — | Keep → SV9 (the finding line cites doc + section) |
| R22 | L91-93 | PRD 1: sections complete; placeholders explicit | C | — | Goal → SV24 |
| R23 | L95-97 | PRD 2: problem names who has it and why now | C | — | Goal → SV24 |
| R24 | L99-101 | PRD 3: acceptance criteria measurable, traced to goals | C | — | Goal → SV24 |
| R25 | L103-105 | PRD 4: specific non-goals, no contradictions | C | — | Goal → SV24 |
| R26 | L107-108 | PRD 5: no implementation detail | C | — | Goal → SV24 |
| R27 | L110-111 | PRD 6: no vague language | C | — | Goal → SV24 |
| R28 | L113-115 | PRD 7: rationale and decisions captured with alternatives | C | F1 | Goal → SV24 |
| R29 | L117-118 | PRD 8: open questions owned | C | — | Goal → SV24 |
| R30 | L122 | Cite the section heading | D | — | Go: R21 |
| R31 | L124-126 | SDD 1: sections complete | C | — | Goal → SV24 |
| R32 | L128-130 | SDD 2: real names; surface every `RESEARCH NEEDED` tag | C | — | Goal → SV24 |
| R33 | L132-134 | SDD 3: `SR-` requirements grouped, observable | C | — | Goal → SV24 |
| R34 | L136-138 | SDD 4: architecture and component coverage | C | — | Goal → SV24 |
| R35 | L140-142 | SDD 5: specific existing-behavior contracts | C | — | Goal → SV24 |
| R36 | L144-145 | SDD 6: named fixtures | C | — | Goal → SV24 |
| R37 | L147-149 | SDD 7: docs by contract-key path, full coverage | C | — | Goal → SV24 |
| R38 | L151-152 | SDD 8: decomposition signal for breakdown | C | — | Goal → SV24 |
| R39 | L154-156 | SDD 9: data-model and contract-key impacts | C | — | Goal → SV24 |
| R40 | L158-159 | SDD 10: rationale and decisions | C | — | Goal → SV24 |
| R41 | L163 | Cross-document checks when both are in scope | C | — | Keep → SV24 |
| R42 | L165-167 | X1: goals ↔ `SR-` requirements | C | — | Goal → SV24 |
| R43 | L169-170 | X2: acceptance criteria covered by the design | C | — | Goal → SV24 |
| R44 | L172-173 | X3: no out-of-scope leakage | C | — | Goal → SV24 |
| R45 | L175-176 | X4: SDD doesn't decide PRD open questions | C | — | Goal → SV24 |
| R46 | L178-179 | X5: decision histories agree | C | — | Goal → SV24 |
| R47 | L183-187 | Severity ladder `blocker` / `suggestion` / `nit` defined by downstream consequence | C | — | Keep → SV9 (the caller recommends Revise on a `blocker`) |
| R48 | L189-194 | Work items actionable, specific, important, concise | C | — | Goal → SV24 |
| R49 | L196 | Often there are no important issues; that's fine | P | — | Goal → SV24 |
| R50 | L198 | Under an orchestrator, trivia each pass makes an infinite loop; be selective | E | b.bix precedent (execution side) | Goal → SV24 |
| R51 | L200 | Caller-side time budget restated | D | predicted | Go |
| R52 | L204 | Mandatory second-person routing trailer, counter-anchor, two-step `TaskCreate` | G + T + A | F10 | Go: prose guards exhausted; the caller's manifest-fronted gate replaces them (SV19). The three code/test/doc reviewers keep theirs (out of scope) |
| R53 | L206 | Emit trailer phrasings verbatim | D | — | Go |
| R54 | L208-213 | Severity and per-path depth are orthogonal | C | 4e9505c | Keep → SV9 (depth has a reader under S5) |
| R55 | L215 | Bracket vs backtick severity asymmetry note | X | 6fc1c28 | Go: severity switches to backticks. `quo-engineer-review:183`, `quo-test-writer-review:162`, and `quo-doc-writer-review:118` already say severity is "backticked the way `/quo-spec-review`'s findings are", which is false today and becomes true. It also gives the writers one findings shape (cold review, finding 6) |
| R56 | L217-220 | Finding line and fix-path line shapes; `[preferred]` | C | 4e9505c, 0f95244, 21d6b43, 6fc1c28 | Keep → SV9, backticked severity, `[preferred]` kept (S5 reads it) |
| R57 | L222-230 | Worked examples per depth bucket | C | 4e9505c | Keep → SV9 (one short template) |
| R58 | L232-244 | Shape 1 (blockers): `## Spec Review Work Items` + list + trailer | C + G | F10 | Keep → SV24 for the `## Spec Review Work Items` heading; trailer goes |
| R59 | L246-258 | Shape 2 (suggestions / nits) + trailer | C + G | F10 | Keep → SV24 (heading only) |
| R60 | L260-268 | Shape 3 clean: `No spec issues found. …` + `bees update-ticket` trailer | C + G | F10 | Keep → SV24 for the clean line; trailer goes |
| R61 | L270 | The trailer emits standalone too | G | — | Go |
| R62 | L272 | Close out self-tracking TaskList tasks before yielding | T | F13 | Go: the reader is gone (TaskList tools off by default) |
| R63 | L276 | Idempotency: reads only, same findings on re-run | X | — | Go: R6 says it mutates nothing |

## 4. What survives: the SV groups the draft must carry

Each group is one place in the draft. Checkpoint 3 maps each to its draft location.

- **SV1 Frontmatter** (P1, W1, D1, R1): `name` unchanged; descriptions revised to the new flow; `argument-hint` unchanged.
- **SV2 Preconditions** (W5, D6, R7): hard-fail `Run /quo-setup first.` with a one-line reason when the Specs hive or CLAUDE.md `## Documentation Locations` is missing. **Addition, recorded per A2:** `/quo-plan` has no up-front check today. Under S3 its first Plans-hive write moves to after approval, so a missing Plans hive would fail at the very end of the run. `/quo-plan` therefore checks the Plans and Specs hives at run start, in one line (cold review, finding 14).
- **SV3 Scope from the conversation** (P5–P7, P10–P12, P17–P18, P20, P25, P27): use the conversation or argument when it carries substance, erring toward distilling (F1); otherwise ask in prose (O6). Write the approved scope to one file with fixed sections: title, What, Why, Acceptance criteria, Out of scope, Decisions, Rejected alternatives, Constraints, each explicit `none` when empty. If the thing is really a defect, suggest `/quo-file-issue`.
- **SV4 Scope gate** (P26, P28): one gate on the scope before any ticket is created.
- **SV5 Research** (P21–P23): read CLAUDE.md, source, references, and existing project PRD/SDD; check overlapping Plan Bees and open Issues with bees orientation (F4).
- **SV6 Spec Bee** (P29, P31–P34): reuse a `drafted` Spec Bee by normalized title, with a gate only on a `drafted` candidate (O5). A `ready` match is never reused or changed: create a new Spec Bee and point to the solo writers for in-place revision (F22). Otherwise create `drafted` with a short body. Specs live in tickets so planning never touches project docs (F2).
- **SV7 Writers inline** (P38–P44): the same approved scope to both; PRD then SDD, never in parallel; inline writers fire no gates; capture the return fields; progress lives in the manifest so a re-run resumes.
- **SV8 Two reviews before approval** (P46, P48, P50, P91–P92, P94, P96–P99): `/quo-spec-review` on both children with no `--doc`, and a cold, read-only, self-contained reviewer agent on PRD+SDD+the Epic draft. Substance is its lane and prose quality is not (F11, O4).
- **SV9 Finding and verdict contracts** (P100–P105, R11, R21, R47, R54, R56–R57): spec review keeps `<n>. [<severity>] <doc + section> …` with `(<letter>) [depth:<…>]` fix paths. The plan reviewer keeps `` `<severity>` target: <PRD|SDD|Plan-Bee-body|Epic:<n>> `` with the same fix-path lines, `Plan-review verdict: <approve | revise-recommended | escalate-to-user>`, and `No plan-review issues found.` Spec review switches its severity to backticks, so both reviewers share one finding shape and the writers' `findings:` accepts one shape. `[preferred]` stays an optional fix-path token (S5 reads it). Under S3, `Epic:<n>` names the draft's ordinal, not a ticket ID.
- **SV10 Routing findings** (P51, P111, P113–P114):
  - Pick the smallest enumerated path that fully fixes the finding, with `[preferred]` as an input.
  - A `trivial-tweak` pick is applied directly.
  - Otherwise the fix goes to the one writer whose document it changes (with `findings:`), or to the orchestrator for the Plan Bee body or Epic draft.
  - The user's own requested changes, given in prose at the plan-approval gate's Revise, route the same way (cold review, finding 9).
  - After fixes, re-run only the reviewer whose input changed.
- **SV11 Plan-approval gate** (P54–P55, P108–P109):
  - Lead with the verdict, with a warning marker on `escalate-to-user` (O3).
  - Show the PRD and SDD summaries with their ticket IDs (so the user can read the bodies, which no other gate now shows), the Plan Bee body draft, the Epic list, and the findings.
  - Choices: approve, approve over blockers (recorded), revise (the user's own changes welcome), or cancel. Revise is recommended when a `blocker` is open.
  - Approving over a finding means won't-fix. A finding the user wants fixed later becomes an `## Obligations` row (SV14).
- **SV12 Plan output contract** (P46, P57, P68–P69, P73, P84, P88–P89, P116–P117): on approval, promote the PRD/SDD children and then the Spec Bee to `ready`. Until then they stay `drafted`, per S3a; create the Plan Bee (short body plus `## Anticipated doc impact` by contract key; `reference_materials` `[{"value":"<spec-bee-id>","resolver":"bees"}]`); create each Epic `drafted`, titled `Epic N — <short title>`, with Epic↔Epic `up_dependencies`; then promote the Plan Bee to `ready`.
- **SV13 Epic decomposition goals** (P75–P78): green after every Epic, one outcome, vertical slices (refactor exception), no testing or docs Epic, testable acceptance criteria, one Epic fine for a small plan.
- **SV14 Deferral hygiene** (P122, P125–P129): every item deferred during the run is an `## Obligations` row. Before handoff an empty set prints `Deferral hygiene: no deferred items.`; otherwise gate `Fix in this session` / `File as issue tickets` / `Encode in an existing ticket body` (per-item routing through the free-text slot), with `## Deferred from /quo-plan run (<YYYY-MM-DD HH:MM>)` for Encode (targets: this run's Plans- and Specs-hive tickets), and no handoff until every row is closed (F12).
- **SV15 Report** (P118–P119): Plan Bee and Epics with status and deps; findings accepted or overridden at the gates.
- **SV16 Next steps** (P132): fresh session recommended; same-session opt-in for one or two Epics (F6, O7).
- **SV17 Commit** (P133, P135, P137): stage only the in-repo Plans and Specs hive paths `hive_commit.py resolve-hive-paths` emits; none → `Plan stored in bees; no in-repo changes to commit.`; subject `Plan feature: <title> (<plan-bee-id>)`; never `git add` with no path, never push (F8, F9, O2, O8). A commit an inline `/quo-file-issue` made mid-run is expected (F20 defect 11).
- **SV18 Bodies and scratch files** (P34, P67, W34–W35, D40–D41): every multi-paragraph body goes through `--body-file` from `/tmp/.quorum/` (`%TEMP%\.quorum`), created if absent, never deleted (F7, O1).
- **SV19 Gate guard and state** (P37, P90, plus every T/A/G row that goes):
  - `/quo-plan`'s manifest records IDs, draft paths, and phase, with the start-of-run lifecycle in S1.
  - Every gate in `/quo-plan` and in the solo writers writes `## Open gate` to its skill's manifest and then calls `AskUserQuestion` in the same turn (F10: all three observed incidents were at the review-return-then-gate point). This supersedes the TaskList two-step for these skills.
  - Governance edits it needs (§8): CLAUDE.md `## AskUserQuestion usage`, `## Scratch-file convention`, `## Working on the orchestrator skills`; the doc-writing guide's `## Deterministic names in the scratch namespace` and `## The two-step TaskCreate → prescribed-tool contract`.
- **SV20 PRD shape** (W2, W16, W22, W29–W32): `PRD` child; the twelve headings in order, always present, `none — <reason>` when empty; rationale and decisions carried from the conversation (F1); what and why, not how; measurable criteria.
- **SV21 SDD shape** (D2, D9, D17, D20–D24, D29, D36–D39, D61): `SDD` child; the seven headings in order, always present; codebase findings from a real Explore research pass, real names only, `RESEARCH NEEDED: <question>` where unsure; research on first authoring, and on a revise only when a finding questions the grounding (F20 defect 6). Plus the b.eid addition (§6): two required subsections under `## Requirements`, `### Mechanism lifecycle` and `### Policy decisions this design implies`, each with an explicit `none` line when empty.
- **SV22 Writer mechanics** (W3, W9–W10, W12, W14–W15, W17–W18, W25, W27, W36–W37, W39, W47–W48, W53–W56, W58; D4, D10–D11, D13, D15–D16, D18–D19, D32, D34, D42–D43, D45, D53–D54, D59, D61, D62–D63, D65): inline versus solo identified by the contract-shaped `args`; never create the Spec Bee; create-or-update by exact title (one → update, several → stop); body replaced, not appended; status `drafted` on create, and set back to `drafted` on an inline update (S3a; inline updates only ever reach a `drafted` Spec Bee's children); inline returns `prd_ticket_id` / `sdd_ticket_id`, status, `action`, and for SDD `research_needed`; the caller owns promotion inline and the Spec Bee always.
- **SV23 Writer solo path** (W38, W42, W44–W45, W51; D44, D48, D50–D51, D57): draft, run `/quo-spec-review --doc`, one approval gate showing both, promote on approve, report.
- **SV24 Spec review** (R2–R6, R9–R11, R12–R16, R18–R20, R22–R29, R31–R46, R48–R50, R58–R60): purpose and modes; parameters; scope; exact-title resolution; the bees body is the truth; the criteria condensed to one line each (a missing section is a `blocker`), plus the b.eid lifecycle and policy-decision check (§6); selectivity; output under `## Spec Review Work Items`, or `No spec issues found.` and nothing further.

## 5. The 2026-09-16 defect list (b.7ib `## Evidence from the first planning-chain validation run`)

| # | Defect | Disposition |
|---|---|---|
| 1 | The 5g gate list omits the 0a and 3 gates | Gone with P123: no gate list; every gate is manifest-fronted (SV19) |
| 2 | The scope gate repeats the distill gate | P13 merged into SV4 |
| 3 | Inline writers bracket a file write with two gates, six times a run | W23/W38/D30/D44 inline: no gates (S2); solo: one (SV23) |
| 4 | Findings payload is the only revise path; depth never routed | SV10 / S5: `trivial-tweak` applied directly |
| 5 | Cross-document findings go to both writers | P51 → SV10: route by where the fix lands |
| 6 | SDD research "every invocation" vs "where appropriate" | SV21: first authoring always; revise only when grounding is questioned |
| 7 | Plan Bee detection uses a `report:` field the CLI rejects | P63 goes with S3 |
| 8 | The time-budget short-circuit still pays full writer passes | P115 goes; S5 direct edits |
| 9 | The plan reviewer suggested a cross-hive Epic → Bee dependency the CLI rejects | Rare, loud, recovered: one clause in the plan reviewer's prompt, "Epic dependencies link sibling Epics only" (SV8) |
| 10 | Review ordering reopens the PRD in a loop | S4: both reviews see the same state before one gate |
| 11 | `/quo-file-issue` commits mid-run; Step 7 doesn't expect it | One clause in SV17 |

Cost goal: the 2026-09-16 run answered about 25 gates, about 9 of them real choices. Under S2 a clean run asks 3–4 (scope, plan approval, next steps, plus Spec Bee reuse or deferral hygiene only when they apply), and each revise round adds one.

## 6. b.eid disposition

b.eid asks the plan path for b.q3f's up-front enumeration at four places. Items 3 (per-Task site lists in breakdown) and 4 (the execute PM verifying against them) belong to b.pcc and b.87t, which own those files.

Items 1–2 are in scope. Item 1: the SDD enumerates each new mechanism's lifecycle legs and the policy decisions the design implies. Item 2: spec review checks for both. Three questions: **how often** — three recorded instances (b.jp2's plan review caught a missing lifecycle leg and a broken intermediate state; b.55r's post-completion churn; b.5ux's two ordering gaps); **does it announce itself** — no, it surfaces as late review rounds; **recovered unaided** — only when a reviewer happened to look. That earns a rule.

**Recommendation: fold items 1–2 in with a named location; keep b.eid open for items 3–4.**

- **Item 1, as an SDD contract** (SV21). `## Requirements` gains two required subsections:
  - `### Mechanism lifecycle`: for each mechanism the design introduces, where it is created, consumed, and torn down, across every scope and exit path;
  - `### Policy decisions this design implies`: each decision the design forces, with its recommended answer.

  Each has an explicit `none` line when empty. As drafted, the vocabulary pointed at `agents/analyst.md`. Cold round 1 found that a writer in a downstream repo cannot open that path, so it became an inline, non-normative gloss ("new state, configuration, persisted or wire field, background task, gate, retry path, and the like"). `agents/analyst.md` itself allows such a recognition gloss. A named heading gives b.pcc something to cite when it builds per-Task site lists (cold review, finding 8). The SDD keeps its seven top-level sections, so spec review's section count and the existing readers don't change.
- **Item 2, in both reviewers.** One criterion line in `/quo-spec-review`'s SDD criteria (SV24) checks that both subsections are present and complete. That covers solo `/quo-write-sdd` revisions, which the plan reviewer never sees. One sentence in the plan reviewer's lane (SV8) makes a missing lifecycle leg, or an implied decision left open, a substance finding. That is where the b.jp2 catch actually happened.

Ticket note for the overseer: retitle b.eid to its items 3–4 and record that items 1–2 landed here, with the two subsection headings as the contract b.pcc consumes.

## 7. TaskList dependence removed

Every TaskList use in the four bodies goes: P30, P49, P62, P79, P82, P93, P94 (tracking), P110, P114 (naming), P120–P124, P131, W41, D47, R52, R62. The TaskList tools are off by default (`CLAUDE_CODE_ENABLE_TODO_TOOLS` unset everywhere), so these rules cannot execute as shipped. What they carried moves to the manifest: gates to `## Open gate` (SV19), deferrals to `## Obligations` (SV14), and IDs and phase to the manifest fields (SV19).

## 8. Readers of the survivors the draft must keep in step

- `/quo-breakdown-epic` `### 1.`/`### 2.`, `agents/pm.md`, `agents/analyst.md`, `agents/doc-writer.md` (out of bounds; unchanged): SV12's strings (`Epic N —`, `drafted`/`ready`, the `bees` entry, exact `PRD`/`SDD` titles, `## Anticipated doc impact`).
- `/quo-engineer-review:183`, `/quo-test-writer-review:162`, `/quo-doc-writer-review:118` (out of scope): say severity is "backticked the way `/quo-spec-review`'s findings are". That is false today, and becomes true when spec review switches to backticks (R55).
- `/quo-test-writer-review:160`, `/quo-doc-writer-review:116` (out of scope): cite "`/quo-spec-review`'s three" trailer shapes, which R52 removes. One-clause reader repair ("…rather than `/quo-spec-review`'s severity-keyed output"). Edited only as reader repair.
- `/quo-breakdown-epic:731` (out of bounds): cites "`/quo-plan` Step 4b" as the inline-Skill precedent. Ticket note for b.pcc.
- `/quo-breakdown-epic:228` and `agents/pm.md:26` (out of bounds): still attribute null `reference_materials` to "Plan Bees authored via `/quo-plan` for features without a separate PRD/SDD", which CLAUDE.md `## Hives and status vocabulary` no longer says. Ticket note for b.pcc.
- `/quo-plan-from-specs:25,54` and `docs/sdd.md:30` (out of bounds or outside this change): still say `/quo-plan` adds feature sections to cumulative docs, false since b.31f. `/quo-plan-from-specs`'s next-steps gate (`:234–238`) lists five choices, one past `AskUserQuestion`'s four. Ticket note for the plan-from-specs owner.
- `/quo-file-issue:77,167` (outside the four-skill scope): the lockstep note and the mandatory-sections contrast. Edited only as reader repair.
- `/quo-setup` `:14`, `:530`, `:538`, `:613`/`:649`, `:664`, `:672`, `:892–897`: the stale `/quo-plan` descriptions from Checkpoint 1.
- CLAUDE.md:
  - `## AskUserQuestion usage`: the two-step contract's scope ("any skill other than the two manifest-fronted orchestrators") must stop covering `/quo-plan` and the solo writers;
  - `## Scratch-file convention`: the manifest exception names `/quo-plan` and the two solo writers, outside the lead-statement mirror;
  - `## Working on the orchestrator skills`: the gates bullet;
  - `## Hives and status vocabulary`: the stale body-as-spec attribution;
  - its word cap.
- `docs/doc-writing-guide.md`: `## Deterministic names in the scratch namespace`; `## Review skills emit a routing trailer` and `## The two-step TaskCreate → prescribed-tool contract` (their site lists name `/quo-plan` 4c/5e and the writers' 6a/7a); `## Project terminology` if needed.
- `CONTRIBUTING.md` `:36–37` (principles 4–5), `:46` (TaskList name classes), `:104` and `:122–127` (the narrate-instead-of-do layers and the scope bullets citing Shape 3).
- `README.md`: the `/quo-plan` row, the three internal-skill rows, and `### Scratch files` (a new manifest resident).
- `docs/sdd.md` and `docs/prd.md`: the features Checkpoint 1 listed, plus a new feature entry.
- A new structure test pins the writer inline contract (`spec-bee-id:`, `distilled-scope:`, `findings:`, return fields) in all three skills, which replaces D60/D69's lockstep prose.

## 9. Commit coverage

54 commits touched the four skills: `git log -- skills/quo-plan skills/quo-write-prd skills/quo-write-sdd skills/quo-spec-review` (24) plus the same for the pre-rename `skills/bees-*` paths (30; `001c314` is in both logs and counted once). Each maps to the rules it shaped, or to "no rule".

| Commit | Subject (short) | Rules shaped |
|---|---|---|
| 0b69f1a | Initial commit | P17, P18, P20, P22, P26, P27, P28, P75, P89, P132, P139 |
| 8b43ae2 | b.dp2 CLI/correctness fixes | P133, P135, P136, P137 |
| 298e13c | b.qw2 portable-core pass | P72, P87 |
| 1302aeb | post-review: 15 findings | P136 |
| 1a88dc1 | b.tsj query recipes | P23 |
| 11fc49f | argument-hint frontmatter | P1 |
| fff554f | b.iaz prose questions | P17, P25 |
| 43a1415 | b.wc4 fresh-session default | P132 |
| 1619146 | post-completion b.11f/b.6e6/b.wc4 | P132 |
| bf4103e | b.c4z `--body-file` | P67, P84 |
| ec055ed | b.mu9 inline-only | P3, P61, P73, P75, P76, P77, P78, P81, P89, P118 |
| c13b5b9 | b.dkw scratch convention | P34, P67, P84 |
| 94d54b7 | egg → `reference_materials` | P69, P84 |
| 85b6c46 | prefer relative paths | no rule (the file-path shape left `/quo-plan` at b.31f) |
| 5300f1b | b.31f Step 4 Spec Bee + writers | P29, P31, P32, P33, P34, P36, P37, P38, P39, P40, P41, P42, P43, P44, P45, P57 |
| 40b943b | b.31f Steps 0–2 distill | P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P19 |
| b115058 | b.31f Step 5/7 bees resolver | P68, P69, P70, P71, P133, P134 |
| 0721824 | add write-prd | W2, W3, W5, W9, W10, W12, W17, W18, W22, W29, W30, W31, W32, W33, W36, W37, W38, W49, W53, W54, W55, W58 |
| 5ad4c5f | add write-sdd | D2, D4, D6, D9, D18, D19, D20, D21, D23, D24, D29, D36, D37, D38, D39, D42, D43, D59, D61, D62, D65 |
| c014d8d | drop stale Plan-Bee-scope assertion | P21 |
| 2cafbda | b.31f Bee-level review fix-ups | P1, W17, D18 |
| 7c5d1ed | b.31f post-completion fix-ups | P68 |
| 728a2cd | b.tak consistency cleanup | P29, P37, P45 (wording of cross-references only) |
| 2301f3b | b.uxa add spec-review | R2, R3, R5, R6, R7, R9, R11, R13, R14, R15, R16, R19, R20, R22–R50, R63 |
| 06b7dcd | post-completion b.tak/b.uxa… | R16, R19 |
| d962595 | b.49g wire spec-review | P46, P48, P50, P51, P54, P55, P56, P59, W39, W42, W44, W45, W46, W47, D45, D48, D50, D51, D52, D53, R4, R51 |
| ae111c3 | b.61t self-tracking close-out | R62 |
| 3cd8a25 | cross-reference precision | W39, W42, W60, D45, D48, D67 |
| c970095 | b.mak review-skill rename | R14 |
| 1e72130 | bees-workflow → quorum rename | D3 |
| 001c314 | bees-* → quo-* rename | no rule |
| 3af384b | b.sfy routing trailer | P52, P53, W43, D49, R52, R53, R58, R59, R60, R61 |
| 7bfbb1b | b.fpm second-person + pre-commitment | P49, W41, D47, R52 |
| 5eab6af | b.bjp plan-review gate | P83, P91, P92, P93, P94, P95, P96, P97, P98, P99, P100, P104, P105, P106, P107, P108, P109, P110, P111, P112, P113, P114, P115, P116, P117, P119 |
| 1324593 | b.bjp post-completion | P54, P83, P106, P109, P115, P116, P119 |
| 2c9b604 | drop warning emoji | P108 |
| 6a806a2 | restore warning emojis | P108 |
| f0abfdf | b.bjp external review | P63, P64, P65, P66, P74, P80, P85, P109, P111, W55, D62 |
| db011e1 | stage the Specs hive too | P133, P135, P136, P137 |
| 3896b01 | b.9q3 cascade guard | P66, P80, P85, P86 |
| 63f75cc | b.dgq deferral hygiene | P120, P121, P122, P124, P125, P126, P127, P129, P130 |
| 2c7d3ef | b.wii two-step contract | P30, P49, P62, P79, P82, P93, P106, P120, P123, P131, W41, D47, R52, R58, R59, R60 |
| cb30bc5 | post-completion b.9q3/b.dgq/b.wii | P123 |
| 1e54340 | b.17n per-item routing | P128 |
| 14c8aaa | b.bbw tier-homogeneous deps | P86 |
| 6c52033 | b.r3x Encode timestamp | P127 |
| bfaecae | t2.ut9.53.64 plan-review depth | P100, P101, P102, P103 |
| 4e9505c | t2.ut9.29.4g spec-review depth | R54, R56, R57 |
| 0f95244 | b.11z emission cross-check | R56 |
| 21d6b43 | b.94j `[preferred]` | P101, P103, R56, R57 |
| 9ca6234 | human labels | P88, P137 |
| 9a513d3 | b.bq4 repo-only citations removed | no rule (citations inlined or dropped; no rule added or removed) |
| 6fc1c28 | b.nn8 `[preferred]` closing clause | P101, R55, R56 |
| 70ec165 | Section-pointer sweep | P108 (pointer wording only) |

## 10. Coverage checks

Both checks are mechanical, run by `/tmp/.quorum/b7ib-check-inventory.py` against this file and the four bodies at `e15efe2`:

1. **Every rule exactly once.** The line ranges in §3 tile every non-blank, non-heading line of each body (fenced lines included) with no overlap. Result: see the report below.
2. **Every commit exactly once.** Each of the 54 commits from the two logs appears exactly once in §9. Result: see the report below.

Check report (2026-09-24):

```
skills/quo-plan/SKILL.md: 896 lines, 602 counted, 139 rules, uncovered 0, rules covering nothing 0
skills/quo-write-prd/SKILL.md: 372 lines, 225 counted, 61 rules, uncovered 0, rules covering nothing 0
skills/quo-write-sdd/SKILL.md: 400 lines, 237 counted, 69 rules, uncovered 0, rules covering nothing 0
skills/quo-spec-review/SKILL.md: 276 lines, 140 counted, 63 rules, uncovered 0, rules covering nothing 0
commits in logs: 54; in table: 54; missing none; extra none; duplicated none
every Keep/Goal disposition's SV group lists the rule, and every §4 group member points at it
```

## 11. Cold review record

One cold review (2026-09-24, general-purpose reviewer, ~262k tokens). It found no Go row that deletes a rule earned by a real run failure while leaving that failure possible. It returned 15 findings: 10 behavior, 5 wording; 0 blocker, 11 suggestion, 4 nit.

- **Applied as design-frame changes:** 1 (manifest lifecycle; S3 narrows rather than removes the crash window), 2 (S3a: Doc children back to `drafted` until approval), 3 (`[preferred]` kept, because S5 reads it), 4 (Encode targets limited to Plans/Specs tickets), 5 (solo writers manifest-fronted; governance edits listed), 8 (b.eid item 1 given named SDD subsections; item 2 in both reviewers), 9 (user revisions routed; gate shows the Doc IDs and summaries; Plan Bee body drafted), 10 (acknowledge means won't-fix; defer-later goes to Obligations), 14 (up-front hive check).
- **Applied as evidence and bookkeeping:** 6 (spec review switches to backticked severity, which makes three readers true), 7 (reader list), 11 (F3, F9, F10 evidence corrected), 12 (S4 trade-off recorded), 13 (kind labels), 15 (728a2cd mapping).

No second round was run on the inventory. Every fix is an inventory edit or a proposal carried to Checkpoint 2, and the behavior findings change the draft, which gets its own cold rounds.

## 12. Amendments after the checkpoints

- **Checkpoint 2, D3 revised by the overseer (2026-09-24).** The solo writers keep no manifest. A solo run keeps nothing that can't be re-derived: the Spec Bee ID is its argument, the child comes from an exact-title query, and the body is in the ticket. So its gate is fronted by writing the current body to a fresh body file in the same turn as `AskUserQuestion`. This supersedes S6's per-writer manifests and the "solo writers manifest-fronted" part of cold-review finding 5. S1 stands for `/quo-plan`.
- **Checkpoint 3, overseer (2026-09-24): F22 earns a rule.** An approved Spec Bee is immutable to `/quo-plan`; see S3a, O5, P32, P33, and SV6.
  - Three questions: frequent enough (every re-plan of a feature whose specs were approved); silent (nothing announces that a Plan Bee now reads drafts); not self-recovering (a Cancel loses the approved bodies).
  - Readers changed with the rule:
    - `skills/quo-plan/SKILL.md` §3 (the gate's trigger) and §5;
    - this inventory's S3a, O5, P32, P33, SV6, and SV22;
    - `docs/sdd.md`'s b.7ib feature entry, flow step 2;
    - `docs/prd.md`'s b.7ib acceptance criteria.

  The writers' inline "set back to `drafted` on update" stays: inline writers now only ever touch a `drafted` Spec Bee's children.
- **Cold round 1 on the draft (2026-09-24, two reviewers: contracts/fidelity and executability).** 25 findings across the two reports, 1 blocker, 14 behavior. The disposition of each is in the Checkpoint 4 record. The rules the fixes add or keep, with evidence:
  - **Solo Cancel restores the saved body and status** (W/D step 2 and the Cancel choice). This is F22 on the path F22's fix routes revisions to. Both reviewers found it independently; the three questions are the same as F22's. A clause is unavoidable, because spec review reads only the ticket body, so the write must precede the gate.
  - **The gate's content lives in `## Open gate`, and approved-over findings become closed `won't-fix` rows in `## Obligations`.** Without this, a compaction at the plan-approval gate or during Section 9 loses the findings and the won't-fix list. The existing carriers are reused.
  - **Query before creating a ticket the manifest does not list.** A crash between a create and its record would otherwise duplicate the Plan Bee or an Epic. Rare, silent, not recovered.
  - **Start fresh carries open `## Obligations` rows.** Otherwise the stopped run's deferrals vanish, which is F12.
  - **The plan draft uses one `#` heading per ticket**, so extracting the Plan Bee body keeps its `## Anticipated doc impact`, which the output contract requires.
  - **A post-approval `Fix in this session` spec change goes through the solo writer**, which reviews and gates it. Specs are `ready` by then, and the inline path would leave a child `drafted` with nothing to promote it.
  - **`/quo-spec-review` returns to its caller and stops only when standalone.** "Then stop" sat at F10's review-return-then-gate point.
  - **User-requested changes on Revise reach the writer as `findings:` lines**, and a scope change rewrites the scope file first. This closes a relay with no channel.
  - **The Encode timestamp comes from `date` / `Get-Date`**, because the model has no clock (the executable-verb test).
  - **The scratch-file rule covers every file the run writes** (rule 4).
- **Rules the round-1 reviewers found carried by no SV group, now recorded:**
  - "a release gate on other work belongs in the Epic body as prose": the other half of 2026-09-16 defect 9;
  - "a fuller path taken only to prevent recurrence is not a fuller fix": the b.vtw C2 pick rule, which S5's pick consumes;
  - the single-literal-command bullet: b.7ib `## Minimal rewrite` asks for Bash etiquette "stated once, as a goal";
  - the solo writers applying trivial fixes themselves: the operator's "trivial fixes applied without re-invoking a writer";
  - `quo-write-sdd` reading the `PRD` child first: a goal with its reason (the design answers the PRD), no failure claimed.
  - the scope file's ninth section, `### Prior context` (what the user pointed to): a goal with its reason. Both writers and the SDD's research need it, and the old `distilled-scope` payload carried the same content (P41).
- **Cold round 2 (2026-09-24, one reviewer, both lanes).** 11 findings: 1 blocker, 4 behavior suggestions, 1 wording suggestion, 5 nits. The blocker and the four behavior findings all came from round 1's own fixes. Each was classified by the three questions before it was fixed, then fixed by restructuring the existing rule:
  - **Query-before-create adopted unrelated tickets** (blocker). On a re-plan with the same title it would record an old Plan Bee. How often: every same-titled re-plan; announces itself: no; recovered: no. It is restructured to run only at phase `approved`, and to look only for what this run could have created: a `drafted` Plan Bee naming this run's Spec Bee, or an Epic with the same title under the recorded Plan Bee.
  - **The Resume gate's write overwrote the gate it resumes.** Rare; it announces itself (the run re-reviews); the run recovers by redoing the step. So it gets no new state: on resume, a gate the stopped run left open is asked again after redoing the step that produced it.
  - **Revise routing had no carrier after a compaction.** The writer passes are the heaviest step; the loss is silent and not recovered. Restructured the gate-reset rule: the answer is recorded in `## Open gate`, and the section resets only once that answer's work has landed.
  - **Cancel dropped open obligations.** Rare, silent, not recovered (F12). Restructured the Cancel sentence: Cancel routes open rows through deferral hygiene first.
  - **The solo saved copy could not be found after a compaction.** The fix is a naming rule: `saved-<child-id>-<short-suffix>.md`, status on the first line. The collision-resistant suffix keeps it inside the scratch convention, so no new deterministic name is needed. This amends D3's premise above: a solo revision does hold one piece of state, the saved copy, and the child's ID makes it re-derivable.
- **Cold round 3 (2026-09-24, confirming pass).** It confirmed the round-1 and round-2 fixes, including the blocker. It found 3 behavior findings and 1 wording finding, all from round 2's changes meeting paths no round had traced. All three need a compaction or crash plus a particular user choice (rare); two are silent and unrecovered. Each was fixed by narrowing or reordering an existing rule:
  - **Resume versus kept answers.** Section 2's compaction and resume sentences merge into one rule keyed on whether the gate record has an answer. The Resume gate shows the stopped run's `## Open gate` record, so writing it keeps that record under the general gate definition, with no new mechanism.
  - **Cancel inherited Section 10's `handoff` phase.** Cancel now sets `complete` first and fires the deferral-hygiene gate itself. The `Fix in this session` bullet drops its "specs are approved by now" premise.
  - **A repeated solo run saved the draft.** The copy is saved only when the child is `ready`, and Cancel restores the newest saved copy for that child's ID.
- **Cold round 4 (2026-09-24): discarded.** It returned two findings, both procedure details inside one agent's own steps, with no gap between agents. Both are discarded under the re-triage below, which also replaces the text they were about.
- **Re-triage against one evidence bar (overseer, 2026-09-24).** This supersedes the round-1 to round-3 entries above wherever they conflict. The review → fix cycle had drifted from the standard: `/quo-plan` grew from 2,989 to 3,353 words, mostly on crash and compaction rules. This inventory dropped rules whose failures were only predicted (F14–F19). A scenario a reviewer role-plays is a prediction too, not a run failure, so it earns one goal sentence at most, never a mechanism. Gaps between agents (contracts, relays, headings) are still findings. Details inside one agent's own steps are not (CLAUDE.md's contract/procedure rule).
  - **Kept, as contract fixes:**
    - one `#` heading per ticket in the plan draft (the Plan Bee body keeps `## Anticipated doc impact`, which breakdown and the Doc Writer read);
    - the user-change relay to the writers as `findings:` lines;
    - `/quo-spec-review` returning to its caller;
    - the `date` / `Get-Date` timestamp in the Encode heading;
    - the scratch-file rule covering every file each skill writes.
  - **Replaced with minimum state plus one goal.** The removed mechanisms:
    - the gate's content and `won't-fix` rows in the manifest;
    - query-before-create;
    - the Resume re-ask rule;
    - the Revise-routing carrier;
    - Start fresh carrying obligations;
    - the solo writers' saved-copy naming scheme.

    The manifest now keeps the phase, the feature title (the resume question names it), what the run has created (the scope file and plan draft paths, and the ticket IDs), the open gate (name, question, choices), and the open obligations. The scope file and plan draft paths are kept because the reviewed draft exists nowhere else. One sentence covers recovery: "After a compaction or a crash, re-read the manifest and reconcile it with bees before acting." The review-round counter is gone, since nothing read it. The second accepted collision (two repos with the same directory name) is dropped with the machinery that listed it.
  - **Solo Cancel** is one goal sentence: "keep the prior body until the user approves; on Cancel, put it back." The Cancel choice reads "put the prior body and status back; a PRD/SDD this run created stays `drafted`".
  - **Cancel with open obligations.** Instead of routing them through deferral hygiene, the Cancel sentence now reports them: one goal clause, since the failure was predicted.
  - **Unchanged by the re-triage:** the round-1 post-approval `Fix in this session` route through the solo writer (a relay between agents), and the `escalate-to-user` recommendation precedence.
  - **Result:** `/quo-plan` is 227 lines and 3,110 words; the growth over the draft's 2,989 is the kept contract fixes.
- **Overseer's correction to the re-triage (2026-09-24): F12 holds wherever the run can end.** Deferrals vanishing at a session end is F12, observed in b.dgq, so its earned rule is not a predicted-failure clause. "Cancel reports open deferrals" does not meet it, because a chat report is not durable. The re-triage's removal of "Start fresh carries obligations" was wrong for the same reason. Both are replaced by one sentence on the existing deferral-hygiene step, with no new state or mechanism: "However the run ends (completion, Cancel, or Start fresh over an unfinished run), open deferrals go through deferral hygiene first." This supersedes the re-triage's "Cancel with open obligations" entry. Readers: `skills/quo-plan/SKILL.md` §3 and the `docs/sdd.md` b.7ib entry.
- **Cold round 5 (2026-09-24, on the re-triaged text; two reviewers, contracts/fidelity and executability, under the evidence bar).** 17 findings, 3 of them behavior, none a blocker; one executability finding and the contracts finding 1 are the same defect. Each fix restructures or replaces existing text.
  - **Behavior:**
    - **The next-steps gate had six choices.** `AskUserQuestion` takes 2–4 options per question, so the gate could not be asked as written; it was inherited from the base. The two execute-now choices are gone, because `/quo-execute` exits at once on a Bee whose Epics are all `drafted` (its Epic query step). Four choices remain: **In a fresh session, break down now** (Recommended), **Continue in this session: break down now**, **Review first**, **Done for now**. A structure test now pins the 2–4 bound.
    - **The Revise relay dropped the picked fix path** (a gap between agents). `/quo-plan` picks a path, but the `findings:` relay carried only the finding lines, and the writers treat those as required fixes. The relay now carries each finding line with the fix-path line picked for it, in `/quo-plan` §7 and both writers' `findings:` placeholders; the approval gate shows the pick too.
    - **The solo writers' gates lost the blocker recommendation** (A1 partial on W45/D51, SV23, and O4). They now mark **Revise** (Recommended) when a `blocker` is open, as `/quo-plan` does.
  - **Wording, applied:**
    - the precondition reads "lacks either the `plans` or the `specs` hive";
    - the manifest phase is set as each section starts;
    - the collision "two repos whose directories share a name" is restored as a statement, in `/quo-plan` §2 and the doc-writing guide, since the convention requires each manifest to state its accepted collisions (the re-triage dropped it with the removed machinery, but the collision itself remained);
    - the Spec Bee title match is stated as a goal instead of a normalization recipe;
    - Epic N is "its 1-based position in the draft", the base's meaning;
    - the writers' return fields are named exactly (`prd_status` / `sdd_status`);
    - the plan reviewer is dispatched as "a `general-purpose` agent in the background", not a spelled-out tool call;
    - staging names "the in-repo hive paths the helper prints";
    - the writers keep "a copy of the prior body and status", the overseer's sentence with its misreading removed;
    - the SDD's claim that breakdown cites the two subsections is dropped, since no breakdown text reads them yet (b.eid items 3–4);
    - the writers' 43-word Choices sentences are split;
    - `docs/prd.md` (resume "reconciling with bees") and `docs/sdd.md` (word total) are corrected.
  - **Carried to ticket notes** (out of bounds here): see §8.
  - **Caps raised, with reasons:**
    - `/quo-plan` 3,109 → 3,141: the F12 sentence (observed failure), the fix-path relay (a gap between agents), and the restored collision statement (a contract), net of the two removed choices;
    - `quo-write-prd` 942 → 962 and `quo-write-sdd` 1,131 → 1,141: the fix-path relay (a gap between agents) and the restored blocker recommendation (a lost inventory survivor).
  - **Exit rule:** three behavior findings earn a fresh cold round. It should cover only this round's fixes and the F12 correction.
- **Checkpoint 4 (overseer, 2026-09-24).** Accepted. The confirming round is skipped: the smoke-Bee validation is the next cold read.
- **Operator, before validation (2026-09-24): the SDD's mechanism gloss goes.** `### Mechanism lifecycle` now says "(as the `analyst` role defines the term)" instead of restating the list. The definition has a single home in the analyst role, and `agents/engineer.md` points there the same way. The pointer names the installed role, not a repo path, which answers cold round 1's concern that a downstream writer cannot open `agents/analyst.md`. This supersedes the gloss described in §6.
- **Validation run (2026-09-24, live_edit, smoke Bee `b.v9c`; Checkpoint 5 accepted by the overseer).**
  - The output contract held on every item.
  - The run asked nine gates, all real decisions.
  - Review rounds converged on their own (blockers per round: 2, 2, 1, 0), so no cap or stopping rule is earned.
  - The triage is in the Checkpoint 5 report. The fixes below are applied without a cold review, on the overseer's direction: a deleted sentence, shorter labels, and one word.
  - **T1: F10 recurred at the solo writer's review-return point.** `/quo-plan` called the solo `/quo-write-sdd`, which called `/quo-spec-review`; the review returned, and the turn ended before the writer's gate. By the three questions: F10 is observed, now four times; it announced itself as a stall; the agent did not recover unaided, but a bare `continue` was enough. `/quo-spec-review` step 4 drops "Standalone, stop there": a standalone run ends anyway, and "stop" was the one instruction the agent could follow at that moment. This is a hypothesis about the cause, to be confirmed on the next solo-writer run.
  - **T5: gate labels are five words or fewer**, matching `AskUserQuestion`'s label guidance. The agent had shortened the pinned seven-word next-steps labels itself.
    - The next-steps labels become **Break down in fresh session** (Recommended) and **Break down in this session**.
    - The reuse label becomes `Create a new Spec Bee`.
    - `Encode in an existing ticket body` is held. It labels the same deferral-hygiene gate in `/quo-execute`, `/quo-fix-issue` (pinned by `tests/test_orchestrator_structure.py`) and `/quo-breakdown-epic` (out of bounds), so renaming it in `/quo-plan` alone would give one gate two names. The rename is a cross-skill ticket note.
  - **T13:** Section 8 recommends **Approve** "on an `approve` verdict", replacing "a clean `approve` verdict", which was ambiguous when suggestions stayed open.
  - **T2, a candidate change, not applied:** `/quo-spec-review` runs through the Skill tool in the author's own context, so in this run only the cold plan reviewer was independent. That was true of the base skill too. Making spec review a dispatched cold agent would be a design change. Record the reviews' independence on the next planning runs before deciding.
