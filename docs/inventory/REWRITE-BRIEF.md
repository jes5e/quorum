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
  destination label per D8), all helper scripts and their unit tests, the review and planning skills, README,
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
D10. **Every recommendation in DECISIONS.md cards 2–12 is accepted.** Where a card says "simplify", the rule set
    is preserved and the prose is not; where it says "move to reference", the rule moves to a shipped reference
    file; where it says "cut", only the named item is cut (doc-verification section → one bullet; TEST rungs 1–4
    from the orchestrator since role files carry them; the Director-run interaction check → dispatched).
D11. **All 33 inconsistencies** in DECISIONS.md `## Inconsistencies to resolve` are resolved as proposed there.
D12. **Nothing reduces review coverage**: no round caps, no lane skipped, no narrowing of what a cold pass reads,
    blockers never accepted, human overrides only where they exist today.

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
