# Failure inventory — `/quo-breakdown-epic` (ticket b.pcc)

Repo-only working document for the minimal rewrite of `skills/quo-breakdown-epic/SKILL.md`. Nothing here ships. It is the input to the draft and the anchor for its cold reviews.

Standard: CLAUDE.md `## How skill prose is written`. A rule survives when it is one of the five kinds (contract, state carrier, structural guard, operator policy, earned rule) or when a run failure earns it under the three questions (how often, does it announce itself, did the agent recover unaided). Everything else goes, or becomes a goal sentence with its reason. The overseer's three questions apply to every row: is this procedure the agent could work out; does it have a real run behind it; is it more machinery than the job needs.

Line numbers are those of the body at commit `12e3d7a` (966 lines, 18,423 words).

## 1. The shape the dispositions assume

These eight choices decide many dispositions below. They are proposals for Checkpoint 2, not settled.

- **S1 — One author, read-only research, one cold review.** The orchestrator drafts every Task and Subtask of the Epic itself, grounded by read-only research agents it dispatches over the code the Epic touches. One cold `pm` dispatch then reviews the whole draft for spec traceability, which is the review the operator's original design gave the PM "final authority" over (0b69f1a), and which b.vtw's 2026-09-24 cross-track contract keeps the PM able to run.
  - **Goes:** the per-Task fan-out of research-mode `engineer` / `test-writer` / `doc-writer` agents (about 3 fresh dispatches per Task); the per-Task PM; the gap-fill loop's re-dispatch of role agents; the TaskList progress machinery that tracked them.
  - **Evidence, both ways.** The fan-out came from the initial design's team (0b69f1a) and was ported, not re-earned, when Agent Teams went (8c0df9f).
    - One record shows a role researcher surfacing something: b.8x3's gap was first flagged by the Task 3 engineer researcher, then confirmed by the per-Task PM. No record shows a Subtask that a single author, followed by a cold review of the whole draft, would have missed.
    - What runs do show: fresh dispatches cost 159k–245k tokens each (F24), and operational Epics paid the full fan-out for nothing (F21).
    - The PM review keeps both kinds of catch in F14: a scope gap inside a Task (b.8x3), and cross-Epic integration deferrals (b.11z). So the one review asks for traceability and for the PM's own cross-Task and cross-Epic interaction check (BV12). The author raises scope questions itself, as the researcher did.
    - The PM review stays; the fan-out is procedure.
  - **Research agents are `Explore`.**
    - They hold no `Edit` or `Write`, so they cannot change files the way today's research-mode `engineer` and `test-writer` can; those are held back only by a preamble (Checkpoint 1, observation 3). They do hold `Bash`, so bees and git mutation remain prose-guarded. That is strictly narrower than today, not a full structural guard.
    - `/quo-write-sdd` already grounds its SDD with an Explore pass.
    - `Explore` is absent from CLAUDE.md's model table on purpose: it only locates code, and the drafting is done by the orchestrator, which the effort gate already covers.
  - **Preconditions follow.** Breakdown dispatches only `pm` and the built-in `Explore`, so the seven-type registry list goes. The hard-fail message on `Agent type '<name>' not found` stays. Under S1 the first `pm` dispatch comes after drafting, so a missing `pm` costs the draft. The draft survives on disk, and the hard-fail names its path: one clause, since the cost is predicted.
- **S2 — Draft, review, then create.** The Tasks and Subtasks are drafted to one scratch file, reviewed, and fixed there. Tickets are created only after the review signs off. This is b.7ib's S3 applied here. Today the per-Task Subtasks are created as each research agent returns and the Epic-wide gap-fill tickets after sign-off, a mix that 8c0df9f's own Task body called churn-prone. The draft file is also the one piece of work a compaction would otherwise lose before the tickets exist, so the manifest records its path.
  - **The draft's labels are a contract with the PM** (plan-failures SV9 settled the same thing). The draft has one heading per ticket: `# Task N — <title>`, and under it one `## <role>: <subtask title>` per Subtask. The PM cites those labels, because no ticket IDs exist at review time. An item that belongs in this Epic's own draft is `addressed-now`: the author fixes the draft.
- **S3 — The manifest keeps the minimum.**
  - Keyed on the Bee ID, with the six lead statements byte-identical (overseer ruling 1). The Epic-ID fallback key and the standalone-Epic forms go, because they cover no case: bees requires `--parent` for a child tier, so every Epic has a Bee.
  - Fields: the unit scope, the run mode, the draft path of the Epic in progress, the Epics broken down this run (read by the run-end report, since bees cannot tell this run's `ready` Epics from an earlier run's), `## Obligations` (deferrals), `## Open gate`.
  - Truncated at run start, as the lead statement says; no resume gate. A crashed run's state is in bees (its Epic is still `drafted`, or its tickets exist and say so).
  - One recovery goal: after a compaction, re-read the manifest and reconcile it with bees and the working tree before acting.
  - **Goes:** the Pre-run SHA, whose one reader (the checkpoint's commit-landed check) goes; per-Epic progress and next unit, which bees re-derives; the 480-word sibling-collision essay and its three-step recovery (F-less, review-predicted).
- **S4 — Gates only at real decisions, each fronted by the `## Open gate` write in the same turn as `AskUserQuestion`** (b.7ib's shape, F2). Six gates: session effort (policy, O3), Bee pick, Epic pick, run mode (O5), deferral hygiene (F3), next steps (F5). The effort, Bee-pick, and Epic-pick gates fire before the manifest exists and go straight to `AskUserQuestion`, as `/quo-execute`'s run-start gates do. **Gone:** the gap-fill divergence gate (no run; S1 has one author) and the guard's missing-reading gate (S6). Labels five words or fewer (F26).
- **S5 — The output contract, with three additions and one removal.**
  - Tasks titled `Task N — <title>`, commit-sized, with `up_dependencies`.
  - **Task bodies get a named shape.** They use the Subtask template's headings (`## Context`, `## What Needs to Change`, `## Key Files`, `## Acceptance Criteria`) plus `## Sites` when applicable. Today only Subtasks have a template, but `agents/doc-writer.md:66` reads a Task's `## What Needs to Change` and `## Acceptance Criteria`, and b.87t's Engineer receives the Task body.
  - Subtasks follow the Mandatory Subtask Description Template.
  - Everything is `drafted` at creation and `ready` once the Epic's children all exist.
  - The Plan Bee's Scoped marker is read as today.
  - **`## Anticipated doc impact` is a new read** (the current body never reads it). It seeds each Task's `doc-writer` Subtask.
  - **Every Task that changes code, configuration, or deployment gets a `doc-writer` Subtask.** The Doc Writer decides what changes (B85's "don't pre-judge"). b.sb7's relay design and b.87t's Phase B both assume one per code-changing Task.
  - **Role tag (decision 1).** Each Subtask carries exactly one *role* tag naming who executes it: `engineer`, `test-writer`, or `doc-writer`. Other tags a project uses are allowed. An operator-run step (a host-only probe, a manual publish) is tagged `engineer`, and its body says the implementer stops and asks the operator to run it, matching b.87t's 2026-09-25 note.
  - **Site list (b.eid item 3).** A Task that implements entries of the SDD's `### Mechanism lifecycle` or `### Policy decisions this design implies` lists them under `## Sites`, so the Engineer implements against a list (F23).
  - **No "Verify the Task" Subtasks, no one-test-Subtask-per-file split, no implementation-first edges (decision 2).**
    - These are output contract today (B118, B119, B122), and their readers are today's `/quo-execute` and `agents/pm.md:227`:
      - the forward fan-out orders by `up_dependencies`;
      - the Test Writer's fingerprint set narrows by them;
      - the PM trusts `.T` as the full-suite run.
    - The readers move to b.87t. Its close-out runs Format, and Full test when the target repo requires it; b.87t already decided that, and dropping `.T` removes the unconditional per-Task suite run in repos that don't require one.
    - **Sequencing constraint:** today's `/quo-execute` must not run on b.pcc's output before b.87t lands. The serial order already has it so (b.87t's first run is the smoke Bee after b.pcc), and no other execute run is planned. This goes on b.87t as a ticket note.
- **S6 — The context guard converges on D4 (decision 3).** At a same-session Epic continuation the guard reads the gauge and stops on a reading at or above the helper's threshold, on `stale`, or on an error; `missing` and `no-reading` continue. The missing-reading gate, its four choices, and the opt-out-marker check go.
- **S7 — Deferral hygiene once, when the run ends,** however it ends (b.7ib's F12 correction).
  - It fires before the next-steps gate, as in `/quo-plan`, and before a guard stop. Those are the two places a run can end.
  - Mode 2 continuing to the next Epic is not a run end, so it asks nothing between Epics. A **Break down next in this session** answer after hygiene finds the rows already closed.
  - Obligations collect in the manifest from the PM's Final report at the moment it returns.
  - The PM prompt limits destinations to tickets and new Issues. Breakdown writes no project docs; a doc change the feature owes is the Doc Writer's, after it ships. `agents/pm.md:253` still offers a PRD/SDD destination, so this is a b.87t note, and b.sb7 item 6 makes Encode tickets-only anyway.
- **S8 — The next-steps gate fits one `AskUserQuestion`** (2–4 choices, F25): execute in a fresh session, break down the next Epic in a fresh session, break down the next Epic in this session, done for now. The Recommended pick keeps the three-case rule (F5), and its reason goes in the recommended choice's description, never a paragraph above the question (F6). "Execute this Epic first" and "execute the whole Bee" are one command: `/quo-execute` runs every workable Epic in dependency order and stops at `drafted` ones. "Start at a specific Epic" goes: execute's own Epic-pick gate does that. "Review first" goes: the report precedes the gate, and **Done for now** covers it.

## 2. Failure evidence register

"Observed" means a real run showed the failure. "Predicted" means a reviewer or designer anticipated it and no run is recorded showing it.

| ID | Failure | Source | Observed? | How often | Announces itself? | Recovered unaided? |
|---|---|---|---|---|---|---|
| F1 | The skill runs only with `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`: every gate, the deferral ledger, and the progress UI use TaskList tools that are off by default | b.pcc (2026-09-11, 2026-09-17); the 2026-09-16 chain run | Observed | Every run without the env var | Partly: the tools are simply absent | No |
| F2 | The orchestrator narrates a gate and yields without calling `AskUserQuestion` | b.sfy, b.fpm, b.wii; b.7ib T1 | Observed four times, all at `/quo-plan`'s review-return point; none recorded in breakdown | Common at that shape | No (the run stalls) | No |
| F3 | Items deferred during a run vanish at the session boundary | b.dgq (a `/quo-plan` run); b.11z (two PM-deferred items from `/quo-breakdown-epic` runs of `t1.ut9.jn` and `t1.ut9.29`, 2026-05-29, carried to an Issue by the deferral gate) | Observed; breakdown produces real deferrals | Occasional | No | No |
| F4 | Vague "search the hive" prose makes the agent invent bees verbs | b.tsj | Observed in `/quo-file-issue`; breakdown sites by audit | Common with no verb named | Yes (exit 2) | Mostly |
| F5 | The next-steps Recommended pick points the wrong way | b.ehy (after `t1.5tm.27`); b.yy9 (two `b.5tm` runs) | Observed three times | Every run of the affected shape | No: the user has to override | No: the agent followed the prose |
| F6 | A rationale paragraph above the `AskUserQuestion` menu is truncated by the UI | b.yy9 | Observed twice | Every long paragraph | Yes, to the user | No |
| F7 | The run ends with the new ticket files uncommitted | b.ehy (B) | Observed: the skill had no commit step | Every run with an in-repo hive | No | No |
| F8 | A hardcoded hive path stages nothing when the hive lives elsewhere | b.dp2 (plan inventory F8); b.ehy (B) | Observed | Every out-of-repo run | No | No |
| F9 | An inline multi-paragraph `--body` trips Claude Code's command-injection guard | b.c4z | Observed | Every multi-paragraph body | Yes | Only with the user approving |
| F10 | Same-session continuation into the next heavy skill burns context | b.wc4 | Observed | Common on big features | No | No |
| F11 | Custom subagents load at session start, so a fresh install fails at the first dispatch | b.5tm Epic A probes; t2.5tm.o1.4d | Observed | Every fresh install before a restart | Yes (`Agent type ... not found`) | With the restart the message names |
| F12 | A dispatch prompt loosened a role boundary and two roles wrote one file | b.kd2 | Observed once, in execution mode; breakdown's research-mode variant predicted | Rare | No | No |
| F13 | Breakdown claimed that returning "releases the orchestrator's working context" | b.ja9 (c) | A false claim; no run failure recorded | — | — | — |
| F14 | A PM review at breakdown catches real gaps and real deferrals | b.8x3 (a scope gap inside `b.55r` Epic 3's Task 3, flagged by the engineer researcher and confirmed real by the per-Task PM); b.11z (two cross-Epic integration items, deferred by per-Task PMs) | Observed value, three recorded catches, all by per-Task PMs, none a traceability GAP | Occasional | The gaps it prevents do not announce themselves | Not without the review |
| F15 | The guard did not fire on the menu's same-session continuation | b.8x3; landed in 2ab84d5 | Found in review; the ill-timed compaction it prevents is predicted | — | — | — |
| F16 | Downstream skills ignored the Plan Bee's Scoped marker | b.51d | Predicted ("one step removed from a real incident") | — | — | — |
| F17 | Writing the JSON envelope instead of the body breaks the marker scan | 21af5c2 | Predicted by a post-completion reviewer | — | — | — |
| F18 | Two runs Encoding into one ticket body stack identical headings | b.r3x | Predicted ("forward-looking") | — | — | — |
| F19 | Users don't know they can route deferral items differently | b.17n | Predicted by review | — | — | — |
| F20 | On an Epic-ID invocation the mode gate had no parent Bee | f50e6a2, finding 1 | Found by a post-completion review | — | — | — |
| F21 | Operational Epics paid the full research fan-out for nothing | 1d132eb (the commit states it; no run is named) | A commit's claim, taken as observed cost | Every no-code Epic | As wall-clock | n/a |
| F22 | Probes ran against the wrong install directory because the docs were not checked first | f50a656 (b.5tm Epic A AC#2) | Observed once | Rare | Yes (the probe failed) | Yes, after a cycle |
| F23 | Execute churn because Tasks carry no site list; reviewers rediscover sites one round at a time | b.eid (b.jp2, b.55r, b.5ux) | Observed three times | Occasional | No | Only when a reviewer happened to look |
| F24 | Fresh dispatches are expensive: first passes of 159k–245k tokens each | b.vtw (b.sao ledger, execute); b.7wb (dispatch count as the wall-clock lever, a hypothesis) | Observed cost figures | Every fresh dispatch | As tokens and wall-clock | n/a |
| F25 | A next-steps gate with more than four choices cannot be asked as written | b.7ib cold round 5 (the same defect in `/quo-plan`) | Found in review; a tool limit | Every run with the six-option menu | — | The agent improvises |
| F26 | Gate labels over five words | b.7ib T5 (the `b.v9c` run: the agent shortened the pinned labels itself) | Observed once | Every long label | No | Yes |
| F27 | Users worked around the per-Epic prompt with personal memory entries | b.m7f | Observed usage | Every multi-Epic run for those users | Yes: a prompt at every Epic boundary | By hack |

**Operator decisions that stand as policy (kind O):**
- **O1** the scratch-file convention (b.dkw);
- **O2** `Task N — <title>` labels and the breakdown commit subject (9ca6234, ccd6b55);
- **O3** the session-effort gate, breakdown floor `high`, prompting only below it (b.ajk; CLAUDE.md `## Model assignment in execution skills`);
- **O4** the PM's spec-traceability review gates the breakdown before tickets are final (0b69f1a; b.vtw 2026-09-24 keeps the PM able to run it);
- **O5** the one-time run-mode choice with identical labels across breakdown and execute (b.m7f);
- **O6** free-text questions in prose, never `AskUserQuestion`;
- **O7** heavy-to-heavy boundaries default to a fresh session (b.wc4);
- **O8** never push, never stage beyond the run's own paths;
- **O9** the context guard at unit boundaries (b.55r), with D4's silent continue on `missing` for the orchestrators (REWRITE-BRIEF D4, 2026-09-09);
- **O10** b.pcc's minimal-rewrite decisions (2026-09-24): keep the Subtask layer, 250/350 lines, no TaskList, b.7ib's gate shape; a Bee-keyed manifest with the lead statements unchanged (overseer, 2026-09-25);
- **O11** the precondition contract (CLAUDE.md: hard-fail on a missing contract section, key, or hive).

## 3. Rule inventory

Kinds: **C** contract · **S** state carrier · **G** structural guard · **O** operator policy · **E** earned by a run failure · **P** procedure or how-to · **X** rationale or explanation · **D** duplicate or restatement · **K** external-CLI recipe · **T** TaskList machinery · **A** counter-anchor or pre-commitment prose.

Dispositions: **Keep → BVn** (carried as a contract or guard), **Goal → BVn** (carried as a goal sentence with its reason), **Go** (with the reason). BV groups are in §4.

| ID | Lines | Rule | Kind | Evidence | Disposition |
|---|---|---|---|---|---|
| B1 | L1-5 | Frontmatter `name`, `description`, `argument-hint` | C | 11fc49f | Keep → BV1 (description names the draft-review-create flow) |
| B2 | L6-9 | "Your job is to break down an Epic" | X | 0b69f1a | Go: the description carries it |
| B3 | L10-13 | Hard-fail `Run /quo-setup first.` plus a note of what is missing | C | 7b2c6de; O11 | Keep → BV2 |
| B4 | L14-15 | Seven subagent types registered; restart or `/agents`; the exact hard-fail message; no `general-purpose` fallback | C + A | 7b2c6de, de8e044; F11 | Keep → BV2: the exact message on `Agent type '<name>' not found` for the roles it dispatches. The seven-name uniformity list and the counter-anchors go (S1: it dispatches `pm` and `Explore`) |
| B5 | L16 | Plans hive colonized | C | 7b2c6de; O11 | Keep → BV2 |
| B6 | L17 | Specs hive colonized, with its message | C | 746c67d; O11 | Keep → BV2. **Addition:** the Issues hive too. CLAUDE.md's contract names all three hives, and **File as issue tickets** writes there |
| B7 | L18 | `## Documentation Locations` present | C | 7b2c6de; O11 | Keep → BV2 |
| B8 | L19 | `## Build Commands` with the five keys | C | 7b2c6de; O11 | Keep → BV2 |
| B9 | L20-21 | Rationale: contract keys over auto-detection | X | 7b2c6de | Go |
| B10 | L22-23 | Don't recover by improvising; fail fast | D | 7b2c6de | Go: B3 says it |
| B11 | L24-25 | Verifying the subagent precondition at first dispatch | D + A | de8e044, fccee3c | Go: restates B4 |
| B12 | L26-31 | The effort gate's two-step `TaskCreate` contract | T | ff31f65, 2c7d3ef | Go: F1 |
| B13 | L32-33 | Tuned for `high`; subagent effort is pinned; the skill cannot change the setting | O + X | ff31f65; O3 | Keep → BV6 (the pinned-effort line stays in the question) |
| B14 | L34-35 | Read before comparing so no `TaskCreate` is stranded | T | ff31f65 | Go: F1; nothing is created before the comparison |
| B15 | L36-47 | Read `CLAUDE_EFFORT`; paired snippets | C + K | ff31f65 | Keep → BV6 (the variable is the contract; one inline pair) |
| B16 | L48-49 | `CLAUDE_EFFORT` tracks the current setting | X | b.ajk | Go |
| B17 | L50-51 | Unset, empty, or unknown value → skip silently | O | ff31f65; O3 | Keep → BV6 |
| B18 | L52-56 | Compare against the floor; silent at or above; gate strictly below | O | ff31f65; O3 | Keep → BV6 |
| B19 | L57-58 | Fire the gate through the two-step contract | T | 2c7d3ef, ca5a2f0 | Go: F1; it fires directly, before the manifest exists (S4) |
| B20 | L59-66 | Question text | C | ff31f65, ca5a2f0 | Keep → BV6 |
| B21 | L67-71 | **Proceed anyway** / **Let me change it first** | C | ff31f65 | Keep → BV6 |
| B22 | L72-75 | Section 1 gates go through the two-step contract | T | 2c7d3ef | Go: F1 |
| B23 | L76-79 | An Epic ID is used directly; a Bee ID finds its Epics | P | 0b69f1a | Goal → BV7 |
| B24 | L80-87 | No arguments: query `ready` Plan Bees; one → use it, several → gate, none → suggest a planning skill; the recipe | K + P | 0b69f1a, 1a88dc1; F4 | Goal → BV7 / BV3 (bees orientation; the recipe goes) |
| B25 | L88-95 | Find the Bee's `drafted` Epics; the recipe | K | 1a88dc1 | Goal → BV7 |
| B26 | L96-103 | Epic-pick gate; recommend by the dependency chain | C | 0b69f1a | Keep → BV7 (the option list shape goes) |
| B27 | L104-107 | This section runs on every invocation (conditional half, unconditional half) | A | 888fa46 | Go: the restructure removes the trap |
| B28 | L108-109 | The mode gate goes through the two-step contract | T | 2c7d3ef | Go: F1 |
| B29 | L110-111 | Count the `drafted` Epics left | P | d03a1d7 | Goal → BV8 |
| B30 | L112-137 | On an Epic-ID invocation, derive the parent Bee and query its drafted Epics; four snippets | P + K | f50e6a2; F20 | Goal → BV7 (one clause: an Epic argument resolves its Bee) |
| B31 | L138-144 | Two or more drafted Epics → the mode gate, its question, **Stop after each Epic** / **Work through all Epics** | C + O | d03a1d7; O5, F27 | Keep → BV8 |
| B32 | L145-146 | Capture the mode once; persist it for the run | S | d03a1d7 | Keep → BV4 (a manifest field) |
| B33 | L147-148 | One drafted Epic → skip the question | O | d03a1d7 | Keep → BV8 |
| B34 | L149-152 | The manifest's definition site; write it on every run | S | 27382dd, 888fa46 | Keep → BV4 |
| B35 | L153-154 | Lead statements 1–2, and what bees, git, and the TaskList hold | C | 9a513d3 | Keep → BV4 (lead statements byte-identical; the carrier sentence rewritten without the TaskList) |
| B36 | L155-161 | Path lead statement; key order Bee ID then Epic ID; the reader applies the same order | C + S | 27382dd, 888fa46 | Keep → BV4 (the lead statement and the Bee-ID key; the Epic-ID fallback goes, since every Epic has a Bee) |
| B37 | L162-175 | Create `.quorum`, write with `Write`; snippets | O + K | O1 | Keep → BV3 (the scratch rule stated once) |
| B38 | L176-177 | Lead statement: the filename is deterministic | C | 9a513d3 | Keep → BV4 |
| B39 | L178-179 | Why the key is the skill name plus a ticket ID | X | 27382dd | Go |
| B40 | L180-181 | The skill-name segment; lead statement "Every skill in this set carries its own name…" | C + X | 9a513d3 | Keep → BV4 (the lead statement; the essay around it goes) |
| B41 | L182-185 | Accepted collision: two concurrent runs on one unit | X | 27382dd | Goal → BV4 (one sentence) |
| B42 | L186 | Different Epics under one Bee: collision essay and three-step recovery | P + X | 888fa46 | Go: review-predicted; the recovery goal covers a foreign manifest |
| B43 | L187-188 | Lead statement: truncate at run start, rewrite at each boundary; never delete | C + O | 9a513d3; O1 | Keep → BV4 |
| B44 | L189-190 | Only values with no other durable home | S | 27382dd | Goal → BV4 |
| B45 | L191-203 | The manifest template | S | 27382dd, 888fa46 | Keep → BV4 (fields per S3) |
| B46 | L204-205 | `standalone Epic <epic-id>` Unit scope | S | 888fa46 | Go: the Epic-ID key already names it |
| B47 | L206-217 | Capture the Pre-run SHA; snippets | S | 27382dd | Go: its one reader, the checkpoint's commit-landed check, goes |
| B48 | L218-219 | The run mode has no re-derivation path | X | 27382dd | Go (BV4's field list carries the reason in a clause) |
| B49 | L220-227 | Fetch and read the Epic and its parent Bee | P | 0b69f1a | Goal → BV9 |
| B50 | L228 | Null `reference_materials` → the Plan Bee body is the spec (stale `/quo-plan` attribution) | C | 0b69f1a, 94d54b7 | Keep → BV9 (attribution dropped) |
| B51 | L229-230 | Dispatch on each entry's `resolver`, mirroring `agents/pm.md` | C + A | dd92d36 | Goal → BV9 (the divergence counter-anchor goes) |
| B52 | L231-232 | `file-path` (or omitted) → read the file | C | dd92d36 | Keep → BV9 |
| B53 | L233-260 | `bees` → the Spec Bee's children titled exactly `PRD` and `SDD`; the walk; four snippets | C + K | dd92d36; b.31f | Keep → BV9 (exact titles; walk as a goal; snippets go) |
| B54 | L261 | Skip the Scoped marker on the `bees` path | C | dd92d36 | Keep → BV9 (one clause) |
| B55 | L262-263 | On the file path, a Scoped marker restricts the spec to its subsection | C | 4c762cc; F16 | Keep → BV9 |
| B56 | L264-276 | Write the Bee body to a scratch file; create `.quorum` | O + P | 4c762cc, c13b5b9 | Goal → BV9 / BV3 |
| B57 | L277-288 | Not the JSON envelope; resolve the helper from this skill's base directory; invoke it | C + K | 4c762cc, 21af5c2, fd18011; F17 | Keep → BV9 (the helper path; "the body, not the JSON" as a clause) |
| B58 | L289 | Helper exit semantics; exit 2 stops the run, no fallback to the full doc | C | 4c762cc | Keep → BV9 |
| B59 | L290-291 | Don't remove the scratch file | O | c13b5b9 | Go: BV3 states it once |
| B60 | L292-296 | Check an external system's docs before planning a probe | E | f50a656; F22 | Goal → BV10 (one clause: rare, loud, recovered) |
| B61 | L297 | Identify the work as a list of Tasks | P | 0b69f1a | Go: the section's purpose |
| B62 | L298-300 | Dependency Epics are done by then; build on them | P | 0b69f1a, 298e13c | Goal → BV9 |
| B63 | L301-306 | Don't duplicate a sibling Epic's scope | P | 0b69f1a | Goal → BV9 |
| B64 | L307-318 | Right-size: lightweight versus full path | P | 1d132eb; F21 | Go: under S1 research scales to the Epic, and no fan-out remains to skip |
| B65 | L319-323 | Title each Task `Task N — <short title>` | C + O | 9ca6234; O2 | Keep → BV11 |
| B66 | L324 | A Task is one commit's worth of work | C | 0b69f1a | Keep → BV11 (execute commits per Task) |
| B67 | L325-327 | No code snippets; scope, not implementation | P | 0b69f1a | Goal → BV11 |
| B68 | L328-339 | Write cross-Task contracts in the Task body; four examples | P | 0b69f1a | Goal → BV11 (one sentence with its reason; examples go) |
| B69 | L340-359 | Example Task | P | 0b69f1a, 9ca6234 | Go: the template and goals carry it |
| B70 | L360-362 | Reconciliation loop of research-mode dispatches | P | 8c0df9f, 70ec165 | Go: S1 |
| B71 | L363-366 | Surface divergent approaches to the caller | P | 0b69f1a | Goal → BV11 (one author, so no divergence; a design choice the spec leaves open is asked in prose) |
| B72 | L367 | The PM has final authority on coverage | O | 0b69f1a; O4 | Keep → BV12 |
| B73 | L368 | Carry the caller's architectural decisions verbatim into every affected Subtask | O | 0b69f1a | Goal → BV11 |
| B74 | L369-370 | You do not author Subtasks | P | 0b69f1a | Go: S1 reverses it |
| B75 | L371-381 | Lightweight-path exception to Section 4 | P | 1d132eb | Go: S1 |
| B76 | L382-385 | The loop is event-driven | P | 8c0df9f | Go: S1 |
| B77 | L386-389 | Read state: bees, the TaskList | P + T | 8c0df9f | Go: S1, F1 |
| B78 | L390 | Returned findings as a source | P | 8c0df9f | Go: S1 |
| B79 | L391 | The manifest as a source; validate it against a sibling collision | S + P | 888fa46 | Goal → BV4 (the recovery goal) |
| B80 | L392-393 | Memory never substitutes; after a summarization marker re-read everything | S | 27382dd | Goal → BV4 (the one recovery goal) |
| B81 | L394-400 | Reconcile: dispatch, persist, PM, advance | P + T | 8c0df9f | Go: S1 |
| B82 | L401-402 | Yield until the completion notification | P | 8c0df9f | Go: S1 |
| B83 | L403-413 | No `/loop`, `ScheduleWakeup`, `CronCreate`, polling | P | 8c0df9f | Go: no run recorded; nothing in S1 waits on a clock |
| B84 | L414-425 | The `Agent(...)` dispatch shape | P | 8c0df9f | Go: S1 |
| B85 | L426-432 | Role selection per Task; the Doc Writer is included for any code, config, or deployment change and decides what docs change | P + C | 0b69f1a | Goal → BV11 (every code, config, or deployment Task gets a `doc-writer` Subtask, which b.sb7 and b.87t's Phase B assume; dispatching the roles goes with S1) |
| B86 | L433-441 | Role-file mapping; unnamed Agents; no `SendMessage` | P | 8c0df9f | Go: S1 |
| B87 | L442-465 | The research-mode preamble, verbatim | P | 8c0df9f | Go: S1; `Explore` is read-only by tool allowlist |
| B88 | L466-469 | Quote the ticket body verbatim in the dispatch | P | 8c0df9f | Go: no run is recorded behind it here. The PM reads bees itself, and an `Explore` agent receives a research question, not a ticket to implement |
| B89 | L470-479 | Framing must not loosen a role boundary; five examples | E | 3ea757d; F12 | Go: breakdown dispatches no implementer role; execute and fix-issue keep the rule where F12 was observed |
| B90 | L480-483 | Procedural gate on `Agent type not found` | D | 8c0df9f, de8e044, fccee3c | Go: B4 carries it |
| B91 | L484-487 | Hub-and-spoke via the substrate | X | 8c0df9f | Go |
| B92 | L488-493 | Subagents cannot spawn subagents; returning releases nothing | X | 8c0df9f, 27382dd; F13 | Go |
| B93 | L494-497 | Per-Task PM dispatch | P | 8c0df9f; F14 | Go: S1 folds it into the one review of the whole draft. That review asks for the PM's interaction checks as well as traceability, which covers the kinds of catch F14 records (a scope gap inside a Task, cross-Epic deferrals) |
| B94 | L498-505 | The spec's three shapes; defer to `agents/pm.md` for resolution | C | dd92d36 | Keep → BV12 (the PM resolves the spec per its role; one clause) |
| B95 | L506-507 | Record each PM-deferred item at the moment of the verdict | T + E | 63f75cc, 3048c28; F3 | Goal → BV12 (an `## Obligations` row at once) |
| B96 | L508-523 | `--body-file` from `.quorum`; snippets; don't remove; single-line bodies may be inline | E + O | bf4103e, c13b5b9; F9, O1 | Keep → BV3 |
| B97 | L524-533 | The TaskList progress UI | T | 8c0df9f | Go: F1 |
| B98 | L534-544 | TaskList naming convention | T | 8c0df9f, 2c7d3ef, cb30bc5 | Go: F1 |
| B99 | L545-563 | The Mandatory Subtask Description Template | C | 0b69f1a | Keep → BV11 |
| B100 | L564-567 | Tasks one after another, no permission asked between them | P | 0b69f1a | Go: S1 drafts the Epic whole; S4 lists every gate |
| B101 | L568-571 | Section 5 gates go through the two-step contract | T | 2c7d3ef | Go: F1 |
| B102 | L572-573 | An Epic-wide traceability review before tickets are final | O | 0b69f1a, 8c0df9f; O4 | Keep → BV12 |
| B103 | L574-575 | A PM agent drives it; gap-fill; create after sign-off | P | 8c0df9f | Goal → BV12 |
| B104 | L576-577 | Defer to the PM | O | 0b69f1a; O4 | Keep → BV12 |
| B105 | L578-581 | Lightweight single pass | P | 1d132eb | Go: S1 always runs one pass |
| B106 | L582-585 | Mandatory after every Epic | O | 0b69f1a; O4 | Keep → BV12 |
| B107 | L586-599 | Spawn the PM in the background; its TaskList task | P + T | 8c0df9f | Goal → BV12 (the dispatch; the task goes, F1) |
| B108 | L600-608 | What the PM prompt carries | C | 8c0df9f | Keep → BV12. The prompt carries the Epic ID, Bee ID, draft path, and `<scoped-marker-resolver-path>`; the PM reads the bodies itself. It also states the breakdown case: review the draft, not a diff; run traceability and the role's interaction checks; invoke no review skill; change nothing; cite draft labels; destinations are tickets or new Issues |
| B109 | L609-615 | Resolve the placeholder from this skill's own `scripts/`; the contrast with execute | C + X | 8c0df9f | Keep → BV12 (the path; the contrast goes) |
| B110 | L616-627 | The review contract: requirements, each resolver's citation form | C | 0b69f1a, dd92d36 | Keep → BV12 (condensed: every requirement mapped, source cited where it lives) |
| B111 | L628-638 | The traceability table | C | 0b69f1a, dd92d36 | Keep → BV12 (header row and `OK` / `GAP`; the "covered by" column cites draft labels, S2) |
| B112 | L639-644 | Return GAP rows; sign off only when all are `OK`; why | C + X | 0b69f1a | Keep → BV12 |
| B113 | L645-658 | Gap-fill loop: role agents per GAP; a spans-Tasks gate; re-dispatch the PM | P | 8c0df9f | Goal → BV12 (the author fixes each GAP in the draft; re-review until none; the gate goes) |
| B114 | L659-660 | Record the Epic-wide deferrals | T + E | 63f75cc, 3048c28; F3 | Goal → BV12 (merged with B95) |
| B115 | L661-669 | Create after sign-off; wire parents and dependencies; Epic, Tasks, Subtasks to `ready` | C | 0b69f1a | Keep → BV13 |
| B116 | L670-671 | Show the Tasks and ask about modifications | P | 0b69f1a | Goal → BV19 (the report; a modification comes through the next-steps gate's free-text slot) |
| B117 | L672-675 | Checklist: every Subtask's parent is its Task | C | 0b69f1a | Keep → BV13 |
| B118 | L676 | Checklist: mandatory Subtasks for a code Task, including "run full test suite" | C | 0b69f1a | Go: decision 2. Its reader (`agents/pm.md:227`'s trust in `.T`; today's execute) moves to b.87t, whose close-out runs Format, and Full test when the target repo requires it. The unconditional per-Task suite run is dropped knowingly (S5) |
| B119 | L677-678 | Checklist: doc and test Subtasks depend on implementation | C | 0b69f1a | Go: decision 2. Its readers (today's forward fan-out and fingerprint narrowing) move to b.87t, which orders the roles itself; the role tag carries what these edges encoded |
| B120 | L679 | Checklist: every body follows the template | D | 0b69f1a | Go: B99 |
| B121 | L680 | Checklist: no git-commit Subtasks | P | 0b69f1a | Goal → BV11 (commits are execute's) |
| B122 | L681 | Checklist: one test Subtask per test file | C | 0b69f1a | Go: decision 2. Its reader (today's per-Subtask fan-out) moves to b.87t, which runs one Test Writer per Task, so the split parallelizes nothing |
| B123 | L682-683 | Checklist: traceability review completed | D | 0b69f1a | Go: BV12 |
| B124 | L684-686 | Commit the new ticket files before the next-steps gate | E | b376887; F7 | Keep → BV14 |
| B125 | L687-688 | Don't hardcode the Plans-hive path | E | b376887, 0c69cc7; F8 | Keep → BV14 |
| B126 | L689-700 | `hive_commit.py resolve-hive-paths --hive plans`; snippets | C | a170f5b | Keep → BV14 (one pair) |
| B127 | L701-712 | Stage it; subject `Plan <bee-id>, Break down <epic-title> (<epic-id>)`; standalone form | C + O | 9ca6234, ccd6b55; O2 | Keep → BV14 (the standalone form goes: every Epic has a Bee) |
| B128 | L713-714 | Never `git add -A` | O | b376887; O8 | Keep → BV14 |
| B129 | L715-716 | Hive outside the repo → no commit, note it | C | b376887 | Keep → BV14 |
| B130 | L717-720 | The hygiene gate's two-step contract | T | 2c7d3ef | Go: F1 |
| B131 | L721-722 | Where deferrals come from | X | 63f75cc | Go |
| B132 | L723-724 | Step 0: retroactive sweep of PM reports | P | 63f75cc, 3048c28 | Go: predicted defense-in-depth; S7 records each obligation at the verdict |
| B133 | L725-726 | Step 1: enumerate; empty → `Deferral hygiene: no deferred items.` | C | 63f75cc | Keep → BV17 |
| B134 | L727-728 | Step 2: list the set and gate it | C + T | 63f75cc | Keep → BV17 (the `TaskCreate` goes) |
| B135 | L729-730 | **Fix in this session** | C | 63f75cc | Keep → BV17 |
| B136 | L731 | **File as issue tickets** through `/quo-file-issue` (stale "`/quo-plan` Step 4b" precedent) | C | 63f75cc, 70ec165 | Keep → BV17 (the stale citation goes) |
| B137 | L732-749 | **Encode**: heading, stem, timestamp, destinations (tickets, or the project PRD/SDD via a doc-writer pass), `defer-N` scratch name, snippets | C + K | 63f75cc, 6c52033; F18 | Keep → BV17 (renamed label; stem and timestamp as `/quo-plan` has them; destinations are tickets, S7; the name and snippets go) |
| B138 | L750 | Don't remove the file; mark the task completed | O + T | 63f75cc | Go: BV3, F1 |
| B139 | L751-752 | The Encode follow-up commit and its subject | C | 63f75cc, 888fa46 | Keep → BV17 (the helper produces the subject) |
| B140 | L753-754 | The helper encapsulates staging; never `-A` | X + O | 8409499 | Goal → BV17 |
| B141 | L755-756 | Resolve `hive_commit.py` as a sibling | C | 8409499, 8ad5aa8 | Keep → BV17 |
| B142 | L757-769 | Invoke with `--skill`, `--count`, `--doc-path`; snippets | C | 8409499 | Keep → BV17 (`--doc-path` goes: Encode targets tickets only, per b.sb7 item 6) |
| B143 | L770 | Proceed to Step 3 | P | 8409499 | Go |
| B144 | L771-772 | The options are non-exclusive; per-item routing through the free-text slot | O | 1e54340; F19 | Goal → BV17 (one clause, as in `/quo-plan`) |
| B145 | L773-774 | Step 3: hard stop until every deferral closes; ask again on a failed route | E | 63f75cc; F3 | Keep → BV17 |
| B146 | L775-776 | The fresh-session recommendation is preserved | D | 63f75cc | Go |
| B147 | L777-780 | The menu's two-step contract | T | 2c7d3ef | Go: F1 |
| B148 | L781-782 | Offer next steps with `AskUserQuestion` | C | 0b69f1a | Keep → BV18 |
| B149 | L783-784 | A fresh session is the recommended default, and why | E | 43a1415; F10, O7 | Keep → BV18 |
| B150 | L785-786 | Out-of-repo hive note | C | b376887 | Keep → BV14 |
| B151 | L787-790 | The two facts behind the Recommended pick | E | b376887; F5 | Keep → BV18 |
| B152 | L791-800 | Query the drafted siblings; filter to dependents | K + P | b376887, d45a93b | Goal → BV18 |
| B153 | L801-807 | Judge reshape risk; its indicators; pure ordering does not count | E | b376887; F5 | Goal → BV18 (one sentence) |
| B154 | L808-812 | Three cases for the Recommended pick | E | d45a93b; F5 | Keep → BV18 |
| B155 | L813-814 | The reason goes on the recommended choice, never above the menu | E | d45a93b; F6 | Keep → BV18 (one clause) |
| B156 | L815-820 | Branch on the run mode; Mode 1 renders the menu | O | d03a1d7; O5 | Keep → BV15 |
| B157 | L821-826 | Mode 2: auto-continue on no reshape risk with a note; pause on reshape risk | O + C | d03a1d7, 2ab84d5; O5 | Keep → BV15 |
| B158 | L827 | Mode 2 respects every other stop | D | d03a1d7 | Go |
| B159 | L828-831 | Always six options; rationale in the subtitle | C | b376887 | Goal → BV18 (four at most, F25) |
| B160 | L832-835 | **In a fresh session, execute the whole Bee** | C | 0b69f1a | Keep → BV18 (one execute choice) |
| B161 | L836-838 | **Execute this Epic first; defer downstream breakdown** | C | b376887 | Keep → BV18 (merged: the same `/quo-execute` command) |
| B162 | L839-840 | **Start at a specific Epic** | C | 0b69f1a | Go: `/quo-execute`'s Epic-pick gate does it |
| B163 | L841-843 | **Break down the next Epic** in a fresh session or this one; the guard on the same-session path | C | 43a1415, 2ab84d5 | Keep → BV18 (two choices) |
| B164 | L844-845 | **Review first** | C | 0b69f1a | Go: the four-choice bound; the report precedes the gate and **Done for now** covers it |
| B165 | L846-847 | **Done for now** | C | 0b69f1a | Keep → BV18 |
| B166 | L848-853 | The Epic-boundary checkpoint runs on every path | S + P | 27382dd | Goal → BV4 (rewrite the manifest at each Epic boundary) |
| B167 | L854-862 | The durable carriers; no compromise tracker | X | 27382dd | Go |
| B168 | L863-874 | Verify, rewrite, re-read, don't recall | P + T | 27382dd, 888fa46 | Go: the recovery goal covers it |
| B169 | L875-876 | What the checkpoint does not do (no context clearing) | A | 27382dd | Go: a disclaimer against a claim the file no longer makes (b.pcc evidence) |
| B170 | L877-880 | The guard fires on same-session continuations only, never on a run-ending path | C | 913f8b5, 2ab84d5; F15 | Keep → BV16 (every same-session continuation) |
| B171 | L881-882 | The guard reads an external gauge; not self-introspection | X | 913f8b5 | Go |
| B172 | L883-884 | Read the session id before any `TaskCreate` | T | 913f8b5 | Go: F1 |
| B173 | L885-898 | Read `CLAUDE_CODE_SESSION_ID`; snippets; trim it | C | 913f8b5 | Keep → BV16 |
| B174 | L899-900 | Unset session id → skip silently | O | 913f8b5; O9 | Keep → BV16 |
| B175 | L901-902 | Resolve `context_gauge.py` as a sibling | C | 913f8b5 | Keep → BV16 |
| B176 | L903-926 | `stop-threshold`, then `read --session-id`; snippets | C | 913f8b5 | Keep → BV16 (inline pairs, as execute has them) |
| B177 | L927-934 | At or above the threshold, `stale`, or an error stops; below or `no-reading` continues | O | 913f8b5; O9 | Keep → BV16 |
| B178 | L935-947 | `missing` → check the opt-out marker; snippets | O | 913f8b5 | Go: decision 3 (D4: `missing` continues) |
| B179 | L948-966 | The missing-reading gate: four choices, `write-opt-out` snippets | O | 913f8b5, 229fd68 | Go: decision 3; no run earned it |

## 4. What survives: the BV groups the draft must carry

Each group is one place in the draft. Checkpoint 3 maps each to its draft location.

- **BV1 Frontmatter** (B1): `name` and `argument-hint` unchanged; the description names the flow.
- **BV2 Preconditions** (B3, B4, B5, B6, B7, B8): hard-fail `Run /quo-setup first.` with a one-line reason when the Plans, Issues, or Specs hive is missing, or CLAUDE.md lacks `## Documentation Locations` or `## Build Commands` with its five keys; `Agent type '<name>' not found` stops the run with the same message and the restart remedy.
- **BV3 Working rules** (B24, B37, B56, B96): bees orientation (no list verb; one-line flow-style YAML; `report:`), scratch files under `/tmp/.quorum/` created if absent and never deleted, `--body-file` for multi-paragraph bodies, one literal command per shell call, free-text questions in prose.
- **BV4 Run-state manifest** (B32, B34, B35, B36, B38, B40, B41, B43, B44, B45, B79, B80, B166): the six lead statements byte-identical; `run-state-quo-breakdown-epic-<bee-id>.md` (the Epic ID when no parent Bee resolves); fields per S3; rewritten when a value changes and at each Epic boundary; one accepted collision; one recovery goal.
- **BV5 Gates** (new: F2, F26, O10): each gate is the `## Open gate` write, then `AskUserQuestion` in the same turn; the six gates listed once; labels of five words or fewer.
- **BV6 Session effort** (B13, B15, B17, B18, B20, B21): read `CLAUDE_EFFORT`; unknown → skip; strictly below `high` → the question and its two choices.
- **BV7 Pick the Epic** (B23, B24, B25, B26, B30): an Epic ID, a Bee ID, or nothing; the Bee pick; the Epic pick recommending by the dependency chain; an Epic argument resolves its Bee.
- **BV8 Run mode** (B29, B31, B33): two or more `drafted` Epics → the question and its two labels, identical to `/quo-execute`'s.
- **BV9 Read the Epic and its spec** (B49, B50, B51, B52, B53, B54, B55, B56, B57, B58, B62, B63): the Epic, its Bee, the Epics it depends on (assume them done), its siblings (don't duplicate them); the spec by resolver, exact `PRD`/`SDD` titles, the Scoped marker through the bundled resolver (file path only, exit 2 stops), the Bee body when `reference_materials` is empty.
- **BV10 Research** (B60): read-only `Explore` agents over the code the Epic touches, in proportion to it; check an external system's docs before planning a probe of it.
- **BV11 Draft the Tasks and Subtasks** (B65, B66, B67, B68, B71, B73, B85, B99, B121): to one draft file, labelled per S2. It covers:
  - `Task N — <title>`, one commit each, with `up_dependencies`, in the template's headings plus `## Sites`;
  - scope, not implementation;
  - cross-Task contracts written down;
  - the caller's decisions carried verbatim, and an open design choice asked in prose;
  - Subtasks in the template, each with one role tag;
  - a `doc-writer` Subtask for every code, config, or deployment Task, seeded from `## Anticipated doc impact`;
  - no commit or verify Subtasks.
- **BV12 Traceability review** (B72, B94, B95, B102, B103, B104, B106, B107, B108, B109, B110, B111, B112, B113, B114):
  - one cold `pm` dispatch over the draft, for traceability and the role's cross-Task and cross-Epic interaction checks;
  - its prompt (B108);
  - the table with `OK` / `GAP`, citing draft labels;
  - the author fixes each GAP and each in-draft finding, and re-dispatches until no GAP remains;
  - deferred items become `## Obligations` rows at once.
- **BV13 Create the tickets** (B115, B117): after sign-off, Tasks under the Epic and Subtasks under their Tasks, `drafted` with tags and dependencies; then Subtasks, Tasks, and the Epic to `ready`; record the IDs.
- **BV14 Commit** (B124, B125, B126, B127, B128, B129, B150): the in-repo Plans-hive path the helper prints, the subject contract, never `-A`, never push; an out-of-repo hive gets a note instead.
- **BV15 Epic boundary** (B156, B157): Mode 1 → the next-steps gate; Mode 2 → continue to the next Epic in this session, with a one-line note, unless reshape risk pauses it.
- **BV16 Context guard** (B170, B173, B174, B175, B176, B177): on every same-session continuation; the D4 branch set.
- **BV17 Deferral hygiene** (B133, B134, B135, B136, B137, B139, B140, B141, B142, B144, B145): whenever the run ends; the three choices under the renamed label; the Encode heading; the helper commit; no end while a row is open.
- **BV18 Next steps** (B148, B149, B151, B152, B153, B154, B155, B159, B160, B161, B163, B165): four choices at most; the three-case recommendation; the reason on the recommended choice; the fresh-session note.
- **BV19 Report** (B116): each Epic's Tasks and Subtasks by label, with statuses and dependencies, and the GAPs the review found.

## 5. b.eid disposition

b.eid item 3 (per-Task site lists in breakdown) is in scope; item 4 (the execute PM verifying against them) is b.87t's. Three questions on F23: **how often**, three recorded instances; **announces itself**, no, it shows up as late review rounds; **recovered unaided**, only when a reviewer happened to look. That earns a rule.

**Recommendation:** a Task that implements entries of the SDD's `### Mechanism lifecycle` or `### Policy decisions this design implies` lists them in its body under `## Sites`, citing the SDD child's ID and the entry.
- **Consumers.** b.87t's Engineer receives the Task body (Phase A), so consumption starts with b.87t. Today's Engineer reads only its Subtask. The fixed heading gives b.87t's PM (item 4) a string to key on.
- **Evidence bar.** It is a new contract, so the bar does not apply to its design.
- **When the spec has no such subsections** (a `file-path` or body-as-spec plan), the Task's `## What Needs to Change` carries whatever sites the draft knows, and no `## Sites` heading is emitted.

Ticket note for the overseer: b.eid item 3 lands here as `## Sites`; item 4 stays open for b.87t, whose Engineer and PM are its readers.

## 6. The context guard, and b.8x3

**Decision (recommended):** converge on D4. At a same-session Epic continuation, the guard reads the gauge.
- A reading at or above the helper's threshold, `stale`, a non-zero exit, or empty output stops the run with the fresh-session resume command.
- Below the threshold, `no-reading`, and `missing` continue.
- An unset session id skips the guard.

**What goes:** the missing-reading gate (**Configure now** / **Proceed without the guard (this run)** / **Never guard me (persistent opt-out)** / **Stop here**) and the opt-out-marker check.

**Evidence.** No run recorded the missing-reading gate helping. The operator decided D4 for the two orchestrators on 2026-09-09 because the gate "interrupted every unit boundary of every unguarded run for a question whose answer never changed within a run" (`skills/quo-execute/references/context-guard.md`). Breakdown was left out only because it was not being rewritten then (`docs/sdd.md`, orchestrator-rewrite Governance: "One follow-up is recorded rather than absorbed").

**Readers updated in the same change** (the ticket requires it):
- `/quo-setup`'s run-unguarded choice: the marker now only silences setup's own automatic offer;
- CLAUDE.md `## Scratch-file convention`, the opt-out-marker exception: its reader is `/quo-setup`;
- `docs/doc-writing-guide.md` `## Deterministic names in the scratch namespace` and `## The context-gauge file contract`'s opt-out paragraph;
- README `## Recommended session settings`, `### Scratch files`, and `### Enabling the gauge producer`;
- `docs/prd.md` and `docs/sdd.md` context-guard entries: a "Superseded in part (b.pcc)" note.

**b.8x3 disposition.** b.8x3 asked whether the menu's same-session "break down the next Epic" path should also run the guard. 2ab84d5 guarded it, and the rewrite keeps the rule general: the guard runs on every same-session continuation (BV16). Nothing is left open. **Close b.8x3** as resolved by 2ab84d5 and carried by b.pcc.

## 7. TaskList dependence removed

Every TaskList use in the body goes: B12, B14, B19, B22, B28, B77, B95 and B114 (their carrier), B97, B98, B101, B107 (its task), B130, B134 (its task), B138, B147, B168, B172. What they carried moves:
- gates → `## Open gate`;
- deferrals → `## Obligations`;
- per-Agent progress → nothing: S1 dispatches a handful of agents, and the harness reports each one.

## 8. Readers of what the rewrite changes

- **`skills/quo-breakdown-epic/SKILL.md`:** the rewrite itself.
- **The Encode label rename, one pass:**
  - `skills/quo-plan/SKILL.md`, `skills/quo-execute/SKILL.md`, `skills/quo-fix-issue/SKILL.md` (the label only);
  - `tests/test_planning_structure.py`, `tests/test_orchestrator_structure.py`;
  - README (`/quo-plan` row), `docs/prd.md`, `docs/sdd.md`;
  - any other hit a grep finds.
- **Tests:**
  - `tests/test_prose_size.py` (breakdown's cap lowered; CLAUDE.md's if it changes);
  - a new `tests/test_breakdown_structure.py` (line cap, no TaskList tokens, the manifest-fronted gate statement, gate labels, output-contract anchors);
  - `tests/test_orchestrator_structure.py` (the lead-statement test stays green; `addressed-now`'s consumer list still names breakdown only if the PM's annotations are read there, which S7 keeps).
- **CLAUDE.md:**
  - `## Repo layout` ("`quo-breakdown-epic` dispatches the four implementer and PM roles");
  - `## AskUserQuestion usage` (the two-step contract is scoped to `/quo-breakdown-epic`, which no longer uses it: no caller remains);
  - `## Working on the orchestrator skills` last bullet ("`/quo-breakdown-epic` still carries the older two-step `TaskCreate` contract");
  - `## Scratch-file convention` (opt-out-marker readers);
  - its word cap.
- **CONTRIBUTING.md:**
  - `## Skill conventions` "TaskList name classes" (breakdown routes on TaskList names);
  - `## Intentional asymmetries` "`mode: "plan"`" bullet (false since 8c0df9f; also b.3hv);
  - `## Known limitations` (the two post-compaction rules citing breakdown's TaskList; the design-consequence paragraph's carrier list).
- **`docs/doc-writing-guide.md`:**
  - `## The two-step TaskCreate → prescribed-tool contract` (its consumption-site list names breakdown Section 5; after this change no skill uses the contract);
  - `## Deterministic names in the scratch namespace` (the opt-out marker's readers);
  - `## The context-gauge file contract`'s opt-out paragraph;
  - `## When you're updating an existing skill` item 3 ("`/quo-execute` and `/quo-breakdown-epic` continue to require only the original seven").
- **README:**
  - the `/quo-breakdown-epic` row (right-sizing, deferral wording);
  - `### After install` (the `Agent type 'engineer' not found` example still holds for the other two);
  - `## Recommended session settings`;
  - `### Scratch files`;
  - `### Enabling the gauge producer`.
- **`skills/quo-setup/SKILL.md`:** the run-unguarded choice and every sentence naming breakdown's missing-reading gate as the marker's consumer.
- **`docs/sdd.md`:**
  - `## Key components` (the breakdown bullet's `mode: "plan"` claim);
  - `## Orchestration in execution skills` (the TaskList bullet; the reconciliation-loop and flat-orchestration carrier lists);
  - "Superseded in part (b.pcc)" notes on the Mode 1/Mode 2, b.dgq, b.wii, b.5js (helper consumer), b.ja9, b.bq4 manifest-mirror, and context-guard entries;
  - a new feature entry.
- **`docs/prd.md`:** "Superseded in part (b.pcc)" notes on the Mode 1/Mode 2, b.dgq, b.wii, and context-guard entries; a new feature entry.
- **CLAUDE.md `## Review criteria for skill changes`:** the manifest-mirror bullet names "breakdown's `defer-*` TaskList" as its third carrier.
- **`skills/quo-setup/scripts/context_gauge.py`:**
  - the docstrings at `:185` and `:208` and the `write-opt-out` help at `:1494` name breakdown's missing-reading stop;
  - the marker body at `:422`–`:440` names the "missing-reading hard-stop" scope.
- **`tests/test_context_gauge.py:3372`–`:3377`** asserts that scope, so it changes with the marker body; `:1431` has a comment on the same point.
- **`skills/quo-execute/scripts/hive_commit.py:5`, `:44`:** the docstrings cite breakdown "Section 6.5" / "Section 6".
- **`docs/doc-writing-guide.md` `## Project terminology`:** its two-hop entry points at `skills/quo-breakdown-epic/SKILL.md` "for the canonical recipe", and the recipe goes. It should point at `agents/pm.md` alone.
- **Out of bounds, carried as ticket notes for b.87t:**
  - `agents/pm.md:26`: the stale `/quo-plan` attribution;
  - `agents/pm.md:227`: trusts the Task's `.T` Subtask, which decision 2 stops emitting;
  - `agents/pm.md:253`: offers a PRD/SDD deferral destination, which breakdown's prompt now excludes;
  - the PM's instructions assume a diff and per-Task review. Breakdown's dispatch prompt states its own case (review the draft; run traceability and interaction checks; invoke no review skill; change nothing; cite draft labels), a relay contract b.87t should keep compatible;
  - `agents/doc-writer.md:66`: reads Task/Subtask `## What Needs to Change` / `## Why` / `## Acceptance Criteria`. Tasks now carry the template's headings; `## Why` is not one of them;
  - what b.87t consumes:
    - the role tag and its vocabulary (operator-run steps tagged `engineer`);
    - no `.T` Subtasks, although b.87t `### Defaults` says "flipped on the implementer's behalf";
    - no implementation-first edges;
    - `## Sites`;
  - the sequencing constraint (S5): today's `/quo-execute` must not run on b.pcc output.

## 9. Commit coverage

49 commits touched the skill's directory: `git log -- skills/quo-breakdown-epic skills/bees-breakdown-epic` (the rename `001c314` appears once). 47 touched the body; `fd18011` and `8cebe4e` touched only `scripts/`. Each maps to the rules it shaped, or to "no rule".

| Commit | Subject (short) | Rules shaped |
|---|---|---|
| 0b69f1a | Initial commit | B2, B23–B26, B49, B50, B61–B63, B66–B69, B71–B74, B85, B99, B100, B102, B104, B106, B110–B112, B115–B123, B148, B160, B162, B164, B165 |
| 298e13c | b.qw2 portable-core pass | B62 |
| 9d03db5 | b.bp5 cross-skill UX polish | no rule (its Opus/Sonnet prompt was removed by ff31f65) |
| 1a88dc1 | b.tsj query recipes | B24, B25 |
| 11fc49f | argument-hint frontmatter | B1 |
| 43a1415 | b.wc4 fresh-session default | B149, B163 |
| bf4103e | b.c4z body-file | B96 |
| 4c762cc | b.51d Scoped marker | B55, B57, B58 |
| 21af5c2 | b.51d review polish | B56 |
| f50a656 | check docs before probing | B60 |
| c13b5b9 | b.dkw scratch convention | B37, B59 |
| b376887 | b.ehy end-of-skill gaps | B124, B128, B129, B150, B151, B153, B159, B161 |
| 7b2c6de | add Preconditions | B3–B10 |
| 8c0df9f | research-Agent orchestration | B70, B76–B78, B81–B84, B86–B88, B91, B93, B97, B103, B107–B109, B113 |
| d45a93b | b.yy9 recommendation direction | B152, B154, B155 |
| 94d54b7 | egg → reference_materials | B50 |
| fd18011 | Scoped marker relative paths | no rule (helper only) |
| 8cebe4e | Scoped marker repo-root detection | no rule (helper only) |
| 746c67d | Specs hive precondition | B6 |
| dd92d36 | two-hop reference_materials | B51–B54, B94 |
| 0c69cc7 | b.iv4 file-issue fold | B125 |
| 1e72130 | quorum rename | no rule |
| 001c314 | quo-* rename | no rule |
| d03a1d7 | b.m7f run mode | B29, B31–B33, B156, B158 |
| f50e6a2 | post-completion findings | B30 |
| 3ea757d | b.kd2 role boundaries | B89 |
| de8e044 | b.vh4 drop the claude-agents check | B11 |
| fccee3c | heading cleanup | B90 |
| 63f75cc | b.dgq deferral hygiene | B131, B133–B135, B137, B138, B145, B146 |
| 2c7d3ef | b.wii two-step contract | B12, B19, B22, B28, B101, B130, B147 |
| cb30bc5 | b.9q3/b.dgq/b.wii post-completion | B98 |
| 1e54340 | b.17n per-item routing | B144 |
| 8409499 | b.5js helper | B140, B142, B143 |
| a170f5b | helper resolve mode | B126 |
| 8ad5aa8 | helper rename | B141 |
| 6c52033 | b.r3x timestamp | B137 |
| 1d132eb | right-sizing | B64, B75, B105 |
| 9ca6234 | human labels | B65 |
| ccd6b55 | parent chain in subjects | B127 |
| ff31f65 | b.ajk effort gate | B13–B18, B20, B21 |
| ca5a2f0 | b.ajk post-completion | B19, B20 |
| 27382dd | b.ja9 state externalization | B34, B39, B41, B44, B45, B47, B48, B80, B92, B166–B169 |
| 888fa46 | b.ja9 post-completion | B27, B42, B46, B79, B139 |
| 9a513d3 | b.bq4 reference architecture | B35, B36, B38, B40, B43 |
| 913f8b5 | guard wiring | B170–B178 |
| 229fd68 | Configure-now exit | B179 |
| 2ab84d5 | guard on the menu path | B157 |
| 3048c28 | orchestrator rewrite | B95, B114, B132 |
| 70ec165 | Section-pointer sweep | B136 |

## 10. Coverage checks

Both checks are mechanical, run by `/tmp/.quorum/bpcc-check-inventory.py` against this file and the body at `12e3d7a`:

1. **Every rule exactly once.** The line ranges in §3 tile every non-blank, non-heading line of the body (fenced lines included) with no overlap, and every Keep/Goal row's BV group lists it, and vice versa.
2. **Every commit exactly once.** Each of the 49 commits appears exactly once in §9, citing only known rules.

Check report (2026-09-25, after the cold-review fixes):

```
skills/quo-breakdown-epic/SKILL.md: 965 lines, 613 counted, 179 rules, uncovered [] (0), rules covering nothing []
commits in log: 49; in table: 49; missing []; extra []; duplicated []
ALL CHECKS PASS
```

## 11. Cold review record

One cold review (2026-09-25, general-purpose reviewer, ~265k tokens). The brief carried the operator's three questions, the evidence bar, and the gap-between-agents sentence as binding.

It found no Go row that deletes a rule earned by an observed failure while leaving that failure possible. It confirmed S8's merge claim against `/quo-execute` run-start step 6. It returned 14 findings: 0 blocker, 7 suggestion, 7 nit; 7 behavior, 7 wording. Verdict: sound-with-fixes. All 14 are applied.

- **Applied as shape changes (behavior):**
  1. every code, config, or deployment Task gets a `doc-writer` Subtask, seeded from `## Anticipated doc impact` (a new read; S5, B85, BV11);
  2. B118, B119, and B122 relabelled as contract whose readers move to b.87t, with the dropped unconditional suite run and the sequencing constraint stated (S5);
  3. the one PM review adds the role's interaction checks, and F14, B93, and S1 now say the catches were per-Task (S1, F14, B93, B108, BV12);
  4. draft labels become a contract the PM cites, and an in-draft item is `addressed-now` (S2, B111);
  5. Task bodies get the template's headings plus `## Sites`, and `## Sites` consumption is dated to b.87t (S5, §5);
  6. role-tag vocabulary covers operator-run steps, and "exactly one role tag" leaves other tags free (S5);
  7. deferral destinations are limited to tickets and new Issues, with a pm.md note (S7, B137, §8).
- **Applied as bookkeeping (wording):**
  8. readers added to §8;
  9. Explore's guard stated accurately, and its model's absence explained (S1);
  10. the Epic-ID fallback key and standalone forms dropped, and the "Epics broken down" field's reader named (S3, B36, B127);
  11. the O deletions B178/B179 wait for Checkpoint 2's ratification, recorded below;
  12. commit and evidence bookkeeping (§9, §10, F21, F27, B88);
  13. deferral hygiene placed before the next-steps gate and a guard stop (S7);
  14. the draft path is named in the hard-fail (S1).

No second round was run on the inventory. The behavior findings change the draft, which gets its own cold rounds, and the edits here were verified by re-running the coverage check.

**Pending ratification at Checkpoint 2:** decisions 1–3, and S1–S8 as a whole. B178 and B179 are operator policy (O9), so their deletion rests on the operator's ratification of decision 3, which will be recorded here.
