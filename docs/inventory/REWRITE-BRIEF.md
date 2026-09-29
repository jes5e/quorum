# Rewrite brief — the two orchestrator skill bodies

Status: decisions taken 2026-09-09 by the operator (delegated to the orchestrator session). This brief is the
prompt for a FRESH implementing session and the checklist every cold review of its output is anchored to.
Repo-only document; nothing here ships.

## 1. What is being rewritten, and what is not

Rewrite from scratch (clean-room; do not edit down, write new):
- `skills/quo-fix-issue/SKILL.md` body
- `skills/quo-execute/SKILL.md` body
- new shipped reference files under `skills/quo-fix-issue/references/` and `skills/quo-execute/references/`
- the test suite for the two skills (delete the prose-pin modules; write the structural suite in §7)

Keep unchanged unless a decision below names them:
- all eight `agents/*.md` role files (one exception: trim `agents/pm.md`'s 1,600-word paragraph; unify the
  destination label per D8), all helper scripts and their unit tests, the review and planning skills (the
  post-validation exceptions are enumerated in the D9 amendment), README,
  the contract keys in `## Documentation Locations` / `## Build Commands`, the hive vocabulary.
- Frontmatter `name`/`description` of both skills (mis-invocation risk).

## 2. Spec sources (read these first, in this order)

1. `docs/inventory/DECISIONS.md` — the 12 cards and the decisions in §3 below.
2. `docs/inventory/INVENTORY.md` — 43 mechanisms; the `## Mirror map` is the identity test.
3. `docs/inventory/EDGES.md` — chains, the 56-heading contract surface, 30 single points of failure.
4. `docs/inventory/fix-issue-CONSOLIDATED.md`, `execute-CONSOLIDATED.md`, `agents-roles.md` — rule-level detail.
5. The current skill bodies — as a source of exact literals only, never as prose to copy.

## 3. Decisions (binding)

D1. **State carrier = the run-state manifest.** No rule may read TaskList state. Lanes, obligations
    (`defer-*`, `aborted-*`), round counts, and open gates live in manifest sections `## Lanes`,
    `## Obligations`, `## Rounds`, `## Open gate`. A gate = manifest `Write` then `AskUserQuestion` in the
    same turn (this replaces the two-step `TaskCreate` contract and serves the same purpose). No TaskList
    progress mirror. Delete the `-r<n>`/`-rev<n>` naming rules, name-class collision rules, and prefix sweeps;
    replace with "mark the lane closed in `## Lanes`". Reverse FX-RECOV-35 explicitly.
D2. **Reference files ship.** Location `skills/<name>/references/*.md`. Read by the orchestrator on demand via
    the same sibling-path discipline the helper scripts use. Every reference file must be rule-3 clean
    (no `docs/*`, `CONTRIBUTING.md`, or repo-only `CLAUDE.md ## <section>` references). Shared files live in
    one skill's `references/` and are read by the other via the sibling path.
D3. **Routing divergences stay** (blocker base pair, `Cancel` at gate (c), gate-(d) sets, part (g) rung,
    approved-design source, close-out target). Present as a two-column table, not parallel prose.
D4. **Context guard**: when no gauge producer is configured (helper reports `missing` and no opt-out marker),
    record `no reading` in the manifest and continue silently — no gate. The gate fires only on a real reading
    at or above threshold. Gate question text stays in SKILL.md; threshold stays in the helper.
D5. **Post-completion diff scope** (both skills): `git diff <pre-run-sha>` (working tree against the pre-run
    commit) plus untracked files from `git ls-files --others --exclude-standard`; changes no ticket body asks
    for are reported as likely pre-existing or unticketed in-run edits, as an inference.
D6. **Inter-Epic interaction checkpoint**: the orchestrator still runs the mechanical half itself (`git log` over
    the Epic's commits; compute the overlap-file list from the manifest's prior-Epic commit). The judgment half
    (contract drift, resource compounding, symmetric-change gaps) is dispatched to the EXISTING code-reviewer
    role with scope = the Epic's commit range plus the overlap-file list; its findings route through the normal
    routing table. Delete the checkpoint's bespoke "dispatch an Engineer to fix it" branch. Rationale: the
    orchestrator that just watched both Epics is the wrong reader for an interaction check, the step has no
    artifact and is the easiest to narrate, and under Mode 1 (fresh session per Epic) the "context is fresh"
    argument for Director-run is void. This is a simplification, not a delegate-mode purity rule.
D6a. **Delegate mode is a means, not a principle.** State once in each body: the orchestrator performs
    mechanical steps that produce a tool artifact directly (git queries, manifest reads/writes, bees status
    flips, helper invocations); it dispatches every step that is a judgment over file contents or a review.
    Do not write "stay in delegate mode" as a bare imperative anywhere.
D7. **Post-completion reviewer prompt skeleton** lives once, in `skills/quo-execute/references/post-completion-prompt.md`,
    with two parameters (diff scope, unit noun); both skills read it.
D8. **Destination label** is the single literal `addressed-now` in `agents/pm.md`, `agents/analyst.md`, and both skills.
D9. **Severity bounds the loop** (b.bix) ships as written in the current bodies, byte-identical in both, and the
    carve-out stays in the three review skills' routing trailer (do not touch those skills).
    *Amended 2026-09-10, after the first validation run:* the carve-out is unchanged, but the trailer and the
    Step-4 prose governing it in the three review skills were made caller-conditional — they name the calling
    skill's gate contract (manifest-fronted for these two skills; two-step `TaskCreate` for other callers)
    instead of prescribing the two-step contract outright. `docs/sdd.md` D9 records the same deviation. After the
    second validation run the selectivity paragraph that closes each skill's `### Step 3` (in `quo-doc-writer-review`,
    the trailing selectivity prose after the output-shape blocks) gained one severity-calibration sentence
    (a fix that changes neither what a true statement asserts nor what it causes a reader to do is a `nit`, not a
    `suggestion`). The same run added, to
    `quo-engineer-review`'s Step 2 implicit-contract check, a pending-not-false carve-out for a comment citing a test
    that a relayed `## Blast radius` tests kind-group or an `## Engineer's completeness evidence` entry dispositions to
    the Test Writer lane. A cold review must not report any of these three edits as a §1 / D9 violation.
    *Body-level deviations from the inventory, same run:* (i) at the Phase C site in `/quo-fix-issue` and the Bee-level
    site in `/quo-execute`, no implementer is dispatched for a finding until every concurrent reviewer (and, in execute,
    PM) lane at that scope has returned — a writer-direction ordering rule the Engineer-dispatch precondition
    (`FX-ENGPRE-1` / `EX-EDP-11`, which constrain only the Engineer direction) does not carry; (ii) the post-completion
    commit (`F7-129` / `E5-181`, which say only "commit") now carries the subject `Post-completion review fixes for <unit>`, unparenthesised so the `(<ticket-id>)`
    token still marks per-unit commits only; `/quo-fix-issue`'s form additionally names the id source (`**Unit scope:**`)
    because its `<issue-ids>` is plural where `/quo-execute`'s `<bee-id>` is not — a sanctioned Tier-2 divergence. (Its `Format` rung and staging are not deviations: §4 item 12 and the
    rationale reference already make every per-unit rule reusable at `postcomp-<n>` scope.) A cold review must not
    report either as an A2 violation.
    *Amended 2026-09-16 (Issue `b.upt`):* the "ships as written … do not touch those skills" clause is superseded.
    **Severity bounds the loop** is now a lead sentence plus seven one-rule bullets (still byte-identical in both
    bodies); severity is defined by consequence with one ordered test per level (in `references/routing.md`
    `## Severity levels` and the three review skills' selectivity paragraphs and worked examples); a residual clause
    lets the orchestrator close a `suggestion` whose fix meets the `nit` test on text a prior pass at that lane
    accepted; the per-round exit decision is written to `## Rounds` (new columns `classification`, `decision`,
    `residuals applied without re-review`) before it is acted on; and Section 11's `Fix in this session` states which
    reviewer lane reads a post-completion fix and prints a `**Reviews**` line at its close-out. The depth bound
    and the `trivial-tweak` batching are unchanged; part (g)'s elision sentence (and its `routing.md` rationale)
    now names the residuals the final pass may ship alongside `trivial-tweak` nits, and
    `references/post-completion-prompt.md`'s depth sentence says the tag is load-bearing rather than informative,
    because Section 11 now reads a `nit`'s depth to decide whether its fix gets a reviewer lane. A cold review must
    not report any of these as a §1 / D9 / A2 violation.
    *Amended 2026-09-16 (Issue `b.vtw`, Batch A):* **Severity bounds the loop** now holds a lane by the kind of the
    fix (`code` / `tests` earn a cold confirming pass; `contract-text` one read per lane; `comments` the sweep), read
    from a new implementer return line `Kinds changed:` checked against the same return's `## Files changed`; the
    residual clause and the depth-keyed hold are gone; Step 1 picks the smallest path that fully fixes the stated
    defect; a premise check (fix mode only) and an earned-chain escalation route to the Analyst (fix) or the
    operator's two-choice escalation gate (**Continue** / **Stop the unit**, execute only), per a new divergence-table
    row; no gate fires on round count; the PM invokes no in-flight review skill in fix mode, and at Bee scope
    skips only the one whose Bee-level reviewer lane ran. `## Rounds` is `scope | review | classification | decision | text fixes applied without re-review`. A
    cold review must not report any of these as a §1 / D9 / A2 violation.
D10. **Every recommendation in DECISIONS.md cards 2–12 is accepted.** Where a card says "simplify", the rule set
    is preserved and the prose is not; where it says "move to reference", the rule moves to a shipped reference
    file; where it says "cut", only the named item is cut (doc-verification section → one bullet; TEST rungs 1–4
    from the orchestrator since role files carry them; the Director-run interaction check → dispatched).
D11. **All 33 inconsistencies** in DECISIONS.md `## Inconsistencies to resolve` are resolved as proposed there.
D12. **Nothing reduces review coverage**: no round caps, no lane skipped, no narrowing of what a cold pass reads,
    blockers never accepted, human overrides only where they exist today.
    *Amended 2026-09-16 (Issue `b.vtw`):* review coverage is proportional to the kind of the fix. Code and test
    fixes keep a cold confirming pass over the whole diff and behavior blockers are never accepted by the
    orchestrator; contract text gets one confirming read per lane; comments are read by the post-completion sweep;
    no gate fires on round count, and an earned chain escalates to the design authority. The operator's principle: doing it right may cost
    more; polishing text with fresh full-diff reviewers is not doing it right.
    *Amended 2026-09-17 (Issue `b.vtw`, Batch B1):* implementers are named `<role>-<scope>` and resumed for their fix
    rounds (fresh only after a revision that changes the approach, a failed send, or a 600,000-token transcript); reviewers
    stay cold. Every review after a lane's first, and every `postcomp-*` reviewer, is a `## Confirming pass` answering two questions over the whole diff,
    opening with `Confirming pass: <n> fixes checked`. Two consecutive `late` rounds run an enumerated confirming pass,
    one implementer pass, and `close — enumerated`; `tests` and text gaps closed there are read by the sweep, a `code`
    fix still owes its confirming pass. Writers receive `## Blast radius` and `## Design decisions for writers`; the Doc
    Writer receives `## Engineer's diff (path)`. The manifest carries `**Ledger:**` (a companion file) and `**Cost:**`.
    The "no warmed Agent" premise of the original dispatch decision is withdrawn: the harness resumes a completed
    background Agent by name. A cold review must not report any of these as a §1 / D9 / D12 / A2 violation.
    *Amended 2026-09-18 (Issue `b.vtw`, b.sao must-do batch):* a one-sentence **Killed lane** paragraph in both bodies' Section 6 (a killed lane is
    re-dispatched with `unknown` usage cells; a killed Test Writer's re-dispatch first restores any file differing from a scratch copy its
    run wrote, asking the operator when unsure); the ledger's bound and increment read the latest row with a known `transcript`; the
    reviewers, the PM, the Analyst, and the post-completion reviewer read-only in their role files and prompt (check-mode tool runs
    permitted); the Test Writer's scratch copy named for the file's repository-relative path; row 1 keyed on the chosen path; the ambiguity-refused send resent with a ref; post-completion groups resumed at the unit's
    implementer per part (g); `## Design decisions for writers` to the Test Reviewer; resumes relay only amended blocks; `fix/<id>`. A
    cold review must not report any of these as a §1 / D9 / D12 / A2 violation.
    *Amended 2026-09-18 (Issue `b.vtw`, Batch B2a):* `/quo-execute` dispatches the Analyst on escalation — a design-question rung,
    the premise check, and the earned-chain rung, all with the Revise shape against the tickets from the escalation's scope up to the Bee and the spec — and carries the
    Analyst gate; the execute-only **Escalation** gate is gone; an approved revision is appended to the ticket at the escalation's scope under
    `## Design revision (Analyst)`; the blocker gate sets are aligned across the two skills and the divergence table has four rows;
    the `## Rounds` decision is `to the Analyst`; fix-issue's Phase C reviewers start as their own writer returns. A cold review must
    not report any of these as a §1 / D3 / D9 / D12 / A2 violation.
    *Amended 2026-09-19 (Issue `b.vtw`, Batch B2b):* `/quo-fix-issue` classifies a docs- or comments-only Issue as `text` from the body and
    runs one writer, that lane's reviewer, and no Analyst, Test Writer, PM, or post-completion sweep, re-escalating to the Analyst when the
    writer's `Kinds changed` names `code` or `tests`; `### Decisions for writers` also carries the client- or operator-facing statements the
    source must make, `## Design decisions for writers` reaches the Engineer and Code Reviewer, and `/quo-engineer-review` checks those
    statements; fix-issue writes each proposal that reaches the Analyst gate to `proposal-<issue-id>-<short-suffix>.md`, recorded on the
    manifest's `**Proposal:**` line, names it by path in the Revise shape, and reads it after a compaction instead of re-deriving (re-firing
    the gate from it when `## Open gate` names the Analyst gate); the Section 5 scope-character-replacement clause is deleted. A cold review
    must not report any of these as a §1 / D9 / D12 / A2 violation.
    *Amended 2026-09-25 (Issue `b.37n`):* the fix-mode PM receives `## Authoritative design directive (from the Analyst gate)`, `## Blast radius`,
    and `## Design decisions for writers`, and traces the diff against the directive, the Issue body staying the problem statement (FX-ROLES-19's
    body-as-spec is superseded for fix mode; FX-PROMPT-25's PM `## Blast radius` relay is restored). A cold review must not report this as an A2 violation.

## 4. Shape of each body (target ≤ 500 lines, hard cap 550)

Order is load-bearing: after a compaction only the first ~5,000 tokens (~150 lines) are re-injected.
1. Frontmatter (unchanged).
2. **Preconditions** (contract keys, hives, hard-fail line) — ≤ 15 lines.
3. **Run-state manifest**: path, the deterministic-filename rule, the CLAUDE.md-mandated lead statements
   byte-identical across the three orchestrators, the new sections from D1, write/read/verify rule — ≤ 40 lines.
4. **Post-compaction rule**: "re-read the manifest; `Read` the routing and post-completion references before
   routing or reviewing; never act on the summary" — ≤ 8 lines. (Must be inside the first 150 lines.)
5. **Loop skeleton**: Read state → Reconcile → Yield; no clock primitives; delegate mode; the phase ladder
   (fix: Analyst → Phase A/B/C; exec: per-Subtask fan-out → per-Task PM → Bee-level reviews) — ≤ 60 lines.
6. **Dispatch shape**: verbatim body; directive/relay table (heading → source → recipients → fixed empty line);
   role list pointing at `agents/*.md` — ≤ 40 lines.
7. **Gates** (each: trigger, question, choice labels verbatim, what each answer does): effort, isolation,
   mode (exec), Analyst approve/revise/cancel (fix), unexplained movement, routing (c)/(d), deferral hygiene,
   post-completion disposition, SR-6.7/SR-4.6, context guard — ≤ 90 lines total.
8. **Routing discipline in-body**: Severity bounds the loop; Step 1/Step 2 table; blocker rules; part (g)
   with elision; pointer to `references/routing.md` for shims, definitions, rationale — ≤ 50 lines.
9. **Per-unit close-out**: status flip, Format, staging via `hive_commit.py`, commit-subject contract, summary
   template, boundary checkpoint (five-line verify + rewrite), guard call — ≤ 60 lines.
10. **Deferral hygiene** (Steps 0–3, Fix/File/Encode, helper commit) — ≤ 35 lines.
11. **Compromise tracker**: file name, five-field entry, Decision enum verbatim, one trigger table — ≤ 30 lines.
12. **Post-completion**: scope (D5), dispatch of the reference-file prompt, disposition gate, postcomp lanes
    ("per-unit rules apply with `postcomp-<n>` as the unit"), recovery gates, commit — ≤ 45 lines.
13. **Aborted-unit close-out** — ≤ 20 lines.
14. **Final output / merge advice** (exec) or GH close pointer (fix) — ≤ 15 lines.

Reference files (shipped): `routing.md` (shared), `post-completion-prompt.md` (shared), `compromise-tracker.md`
(shared: trigger rationale, Decision-value history), `context-guard.md` (shared), `rationale.md` (shared: every
"why" and failure narrative the inventory classed as rationale, grouped by mechanism), `url-resolution.md`
and `github-close.md` (fix only). No reference file may be required to make a gate fire correctly; gates are
in-body.

## 5. Writing rules for the new bodies

- One rule per sentence; no paragraph over 120 words; no sentence over 40 words.
- Bold only headings and gate choice labels. No self-referential pointers ("per the paragraph below").
- Quote every literal from the inventory's `## Literals index` exactly; never paraphrase a heading, label,
  file name, command, or enum value.
- Every shell snippet as paired POSIX + PowerShell blocks (design rule 2); every command a single literal.
- Stack-neutral, project-neutral (design rules 1 and 3); scratch files only under `<tempdir>/.quorum/`, never deleted.
- No instruction may name an action the model cannot take (executable-verb test).
- Mirror map Tier 1 rules byte-identical across the two bodies; Tier 2 identical modulo the unit noun.

## 6. Acceptance criteria (each cold review checks all of these)

A1. Every `procedure`-class rule in INVENTORY.md is present in the body or in a shipped reference file the body
    points to, or is on the explicit cut list in D10. Reviewer samples ≥ 100 rules per pass, stratified by mechanism.
A2. No rule present that the inventory lacks (new mechanisms are forbidden; ask instead).
A3. Every literal in the `## Literals index` that the decisions keep appears verbatim; every renamed one is on D8.
A4. Mirror map holds (mechanical byte comparison); the divergence table matches D3.
A5. Every chain in EDGES.md still closes end to end; every SPOF string is present at every hop.
A6. Line budget: body ≤ 500 (hard cap 550); sections 2–5 within the first 150 lines.
A7. `tests/test_shipped_artifact_portability.py` passes with `references/` included in its scan.
A8. Executability read: a reviewer role-plays one full `/quo-fix-issue` run and one `/quo-execute` run from
    the text alone and reports any step where the next action is ambiguous.
A9. No coverage regression against D12, checked explicitly.

*Amended 2026-09-24 (CLAUDE.md `## How skill prose is written`):* A1 is met, in addition to the D10 cut list, when an
inventory rule is present, moved to a shipped reference file, or deleted under that standard with its evidence recorded in
the commit or ticket; INVENTORY.md's "procedure" class means any instruction, not the standard's sense of a how-to step.
§5's literal rule and A3 do not require an external-CLI invocation that standard retires (the indexed `stages:` query
strings, for example); a retired literal is recorded in the commit or ticket. A8 reports a step only when the agent
cannot tell what outcome satisfies it or what exact string a contract uses; a step whose procedure is left to the agent is
not ambiguous. A2 stands: a change that needs a rule the inventory lacks records it as an amendment here, as the batches
above did.

*Amended 2026-09-26 (Issue `b.87t`, the execute rebuild):* `/quo-execute`'s unit is the Task, and each Task runs `/quo-fix-issue`'s
Phase A / B / C ladder. §4 item 5's execute ladder, D6's inter-Epic checkpoint, and every inventory row for the per-Subtask
fan-out, the Bee-level reviews (#16 exec), the per-Task PM's in-flight reviews, and the execute half of #41 are superseded;
the tests' pair list, not the inventory's mirror map, is the live mirror. Rules this rebuild adds, each with its reason in
the commit:
- an Engineer return under `## Operator action needed` is not a completion and fires the execute-only Operator-action gate
  (**Resume the Engineer** / **Abort this unit**), because breakdown's contract has an operator-only step's implementer stop
  and ask, and execute had no receiver;
- a return with an explicitly empty `## Files changed` gets no reviewer;
- an `engineer` Subtask may direct research, a measurement, or a record outside the source tree (`agents/engineer.md`);
- the post-completion review runs per Epic, with the shared prompt's `<scope-notes>` parameter carrying the interaction checks,
  the tracker entries above the manifest's `**Compromises reviewed:**`, and the `Full test` result, which the Epic boundary runs once;
- deferral hygiene fires per Epic and before any other run exit; the context guard runs before each Task and Epic review;
- the per-Task PM invokes no review skill and verifies the Task's `## Sites` (b.eid item 4);
- a run resuming a Bee with an `in_progress` Epic keeps the earlier session's `**Compromise tracker:**` path and
  `**Compromises reviewed:**` count, because the rebuild's own mid-Epic stops (the Task-boundary guard, Mode 1, abort) would
  otherwise hide that Epic's compromises from its review (a state carrier; cold round 1);
- the Test Writer drops files it edits itself from its movement fingerprint set, because breakdowns put unit tests inside
  source files (b.v9c Tasks 2, 4, 5) and its own edits would read as movement (cold round 1);
- a run already on `bee/<bee-id>` in the main repo skips the isolation gate, because Mode 1 makes resuming onto that branch
  routine and the gate would offer to create it again.

The operator approved deletion-only edits to `/quo-fix-issue` §7 (the part-(g) divergence row, the execute design-source
cell, "a Task finding", the PM in-flight sentence) and §8 (the PM second-order clause). A cold review must not report any
of these as an A2, D6, D12, or §1 violation.

*Amended 2026-09-27 (Issue `b.rqc`, the mirrored batch from b.v9c):* rules this batch adds or changes, each with its reason in the commit:
- the premise-check label is defined as the finding's premise (`premise-holds`: the finding is right; `premise-false`: the finding is
  wrong), and the Analyst labels each finding of a premise-check dispatch in the prompt's order, because both b.v9c premise checks used the
  inverse reading and the bodies send every qualifying finding in one dispatch (a contract gap between two agents);
- after a compaction, §3 re-reads the skill's own `SKILL.md`, because only about the first 150 lines are re-injected (a recovery goal);
- the resume bound is 675,000 (operator decision); Phase A also closes on `/quo-engineer-review`'s `No code files to review`.

*Amended 2026-09-28 (Issue `b.d7t`, delegated gates):* a run launched with `--decider "<session name>"` sends every question it would put to the operator after the manifest write, gates and prose questions alike, to that session. §4's "No reference file may be required to make a gate fire correctly; gates are in-body" is amended: the delegation contract lives once, in the shipped `skills/quo-execute/references/delegated-gates.md`, which `/quo-execute`, `/quo-fix-issue`, `/quo-breakdown-epic`, and `/quo-plan` read when `**Decider:**` names a session. The rule's reason still holds, because every gate's trigger, question, and labels stay in-body, and a run that has not read the reference asks the operator, which is always a correct gate. Rules this batch adds, each with its reason in the commit:
- `**Decider:**` in each manifest, from the launch argument, checked against `ListAgents` before the first question (a state carrier; operator decisions D2 and D3, 2026-09-28);
- once the check passes, the run sends the decider one fixed `quorum decider:` introduction (which run, that the operator named it, how questions arrive and how to reply, to answer as the operator's delegate), because a decider receiving a bare `quorum gate:` message cannot know its role (operator, 2026-09-28; a gap between two agents);
- the launch questions before the manifest stay with the operator, and no gate after it is operator-only (operator decision D1: the decider alone decides when it needs a human);
- a delegated gate keeps the `## Open gate` write, writes a gate file carrying the question, the labels, and the context by path or copied verbatim, and sends a fixed `quorum gate:` message whose reply names the gate file, because the decider cannot see the worker's screen and two live_edit gates (b.v9c's Operator-action gate, b.y3m's Analyst gate) paraphrased their content despite "verbatim" and "in full" in the prose (a contract between two agents);
- the answer is the first of the decider's reply by `from-name` and the operator's typed text, recorded with its source in the gate file before the run acts; a reply naming another gate's file, or arriving when no gate is open, answers nothing (after an operator override the decider's reply may otherwise land on the next gate, a gap between two agents); any other wake-up gets bookkeeping and no dispatch (spike SS5 and op-override);
- a failed or held send falls back to the operator at once, and an idle, exit, or expiry notice with the question unanswered prompts a `ListAgents` check (spike SS3b and SS3d);
- after a compaction a delegated gate is never re-sent (a state carrier), except `/quo-execute`'s Analyst gate, which keeps its re-derive exception because the gate file does not carry the `### Deferred refinements` Approve consumes;
- where a skill names the operator as the one who answers, discusses, or re-issues a choice, the answerer is read instead (a recipient gap between two agents).

The bodies' Section 4 lead now reads "roles never message each other" in place of "no peer-to-peer messaging", and unexplained movement's **Wait** re-fires on a reply to the gate. A cold review must not report any of these as an A2 or §4 violation.

*Amended 2026-09-29 (Issue `b.dpp`, fix-issue resume and pre-review guard):* evidence is live_edit run cvei2 (2026-09-28/29). A machine restart mid-Issue was survived only by resuming the same conversation, and a re-run would have emptied two open deferrals. A context-full stop during the post-completion fix round needed a decider-written plan and a "skip Run start" prompt. Both announced themselves, and neither was recovered unaided. Rules this batch adds or changes, each with its reason in the commit:
- `/quo-fix-issue` run start resumes a manifest that records the invocation's batch and whose `**Next unit:**` is not `none`: it keeps every field and section, skips run-start steps 3–6, and recovers as after a compaction. It supersedes FX-MAN-21's rewrite and FX-MAN-24's fresh write for a stopped run, because they destroyed the only carrier of the run's obligations, lanes, rounds, and review base (a state carrier);
- `**Next unit:**` gains the value `post-completion review`, rewritten to `none` when Section 11 completes, because the fields could not tell a review still owed from a finished run, and cvei2 improvised "RUN CLOSED" and a plan file for it (a state carrier);
- a resumed run treats every `open` lane as killed, because the `## Lanes` rule's "will notify — wait for it" is false once the earlier session has ended (a state carrier's recovery goal);
- one resume command, `/quo-fix-issue <batch-ids>`, replaces `/quo-fix-issue all` and `/quo-fix-issue <remaining-ids>` (FX-GUARD-18, FX-ABORT-28). The old forms compute a batch the manifest no longer matches, and `<remaining-ids>` is empty at the new guard stop. The aborted-Issue STOP's resume continues after the aborted Issue (operator decision, 2026-09-29);
- `**Decider:**` on a resume comes from the invocation, as at every launch, and the printed command carries `--decider`, so a fresh-session resume re-introduces the run (operator decision, 2026-09-29);
- the guard also runs before the post-completion review in every mode, as execute's runs before each Epic review. This supersedes FX-GUARD-1, -2, and -4's continuing-path-only rule (the cvei2 context-full stop; single mode by operator decision, 2026-09-29);
- a session resuming a run fires again a delegated gate whose file has no `## Answer`, to its own `**Decider:**` or the operator, because the decider replies to the ended session (a gap between two agents on the resume path);
- the resume command is also printed when the manifest is written, because a session that ends uncleanly prints none, and cvei2's restart was such an end (cold round 1);
- a single-mode run checks its Issue's dependencies before the manifest write, so a blocked exit leaves no manifest that reads as a stopped run (cold round 1: a case the resume condition's own inputs cover);
- one goal sentence in §3: when a review's findings are needed and no longer readable, as after a compaction or a resume, that review is dispatched again.

A cold review must not report any of these as an A2 violation.

*Amended 2026-09-29 (Issue `b.h1t`, items 1, 5, and 6; operator decisions of the same day):* rules this batch adds, changes, or deletes, each with its evidence:
- `/quo-execute` deferral hygiene also fires before a Task starts when an open `defer-*` obligation's destination is that Task or one of its Subtasks. Evidence: b.v9c encoded such items mid-Epic three times (`fa6ebced`, `89871372`, `beede20d`), and b.y3m every time, unaided; b.y3m Task 3's PM caught hand-offs planned for the Epic boundary as too late. Three questions: every chained Epic; silent if missed; recovered unaided, once only through a PM catch;
- `/quo-execute`'s Analyst gate writes the return to a `**Proposal:**` file, reusing `/quo-fix-issue`'s mechanism unchanged: the §6 write sentence (Tier 2), the §3 read-back sentences (Tier 1), the Revise shape by path, and the line cleared at each Task's close-out. A delegated gate then names the return by path. Evidence: b.y3m Task 3's Analyst gate paraphrased the proposal, naming its rules inconsistently (a state carrier; a gap between two agents);
- **deleted:** `/quo-execute` §3's Analyst-gate exception (rewrite `## Open gate` to `none` and re-derive after a compaction; skip a delegated Analyst gate's gate file). It superseded the 2026-09-28 amendment's exception bullet, and its reason is gone, since the file carries the `### Deferred refinements` Approve consumes. §6's "Fires when the Analyst returns from a Section 4 rung" is deleted as redundant with every rung's "run the Analyst gate";
- a premise-check return that changes what the approved design states (a policy decision, a stated invariant or bound, or a directive statement) ends in a whole Design Proposal and its `Analyst verdict:` trailer, and §7 (Tier 1) sends such a return through the Analyst gate before any finding routes; §4's "no gate fires on it" is deleted in both bodies. Evidence: b.y3m Task 3 F2 and b.v9c Task 2 (both harmless), and a live_edit `/quo-fix-issue` run on 2026-09-29 whose premise check silently changed two statements the decider had approved. Three questions: 3 times; silent to the approver; not recovered unaided.

A cold review must not report any of these as an A2 violation.

Review loop: cold `/quo-engineer-review` passes with this brief embedded as the criteria, until a pass returns
nothing above a `trivial-tweak` nit (b.bix rule). No round cap.

## 7. Tests

Delete: `test_review_lane_ordering_contract.py`, `test_second_order_effects_contract.py`,
`test_writer_role_contracts.py`, `test_tasklist_name_class_closeout.py`, `test_routing_decision_contract.py`,
`test_blast_radius_contract.py`.
Keep: helper unit tests, `test_shipped_artifact_portability.py` (extended to `references/`).
Write: `test_orchestrator_structure.py` — (a) mirror-map identity from a checked-in pair list;
(b) per-skill line budget; (c) one presence assertion per kept inventory rule keyed on a heading or label
anchor, never a sentence; (d) every gate's choice labels present verbatim; (e) every contract-surface heading
from EDGES.md present in its emitter and consumer files. Target ≈ 40 tests. No test quotes a prose sentence.

## 8. Repo-local governance changes (this repo only; not shipped)

- `CLAUDE.md`: add `## Working on the orchestrator skills` — structural changes to `quo-fix-issue` /
  `quo-execute` go through inventory-anchored hand edits with cold reviews, not `/quo-fix-issue`; quorum runs
  remain appropriate for helper scripts, tests, and small bounded prose fixes; validate process changes on a
  code repo before this one; a finding whose fix adds a clause must say why restructuring cannot do it;
  line budget is a review criterion.
- `docs/test-writing-guide.md`: tests here cover Python helpers and structural invariants only; pinning prose
  sentences is out of scope.
- `docs/sdd.md`: one Feature entry recording the rewrite, D1–D12, and the reference-file architecture.

## 9. Validation before the second rebuild

One real Issue on one code repo with the rewritten skills, read end to end by the operator and the orchestrator
session; one `/quo-execute` over a small Bee. Any defect found is fixed on main with a cold review before rebuild.
