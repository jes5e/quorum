# DECISIONS — operator decision list for the orchestrator rewrite

Twelve cards over the 43 unified mechanisms in `INVENTORY.md`. "Rules" = unified count after cross-skill dedupe; "lines" = current SKILL.md lines (fix / exec). "Evidence" cites failure-narrative rows only; the inventory records narrated failure modes, not incident logs, so "none recorded" means the text names no occurrence. Environment fact: TaskList tools (`TaskCreate`/`TaskList`/`TaskUpdate`) are OFF by default for the Fable model family and ON for other models; `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` enables them. The operator's stated view: making load-bearing state depend on an optional tool was a design miss. Bias throughout: smallest internally-consistent design; nothing below reduces review coverage (no round caps, no skipped lanes, no narrowed cold pass).

## Card 1 — TaskList-carried state
**What it is:** #12 naming, #13 `gate-*` two-step contract, #17 `defer-*` ledger, the `aborted-*` markers (#8), the Engineer-dispatch precondition prefix tests (#7), close-out prefix sweeps (#18/#22/#16), `-r<n>`/`-rev<n>` round counting, and the fix-only TaskList-derived resume arms (#6) — every obligation the orchestrator must remember across ticks is carried as a TaskList task keyed by name prefix + status.
**Failure it prevents:** Narrating a gate instead of firing it; yielding with a decision open; a stale conversation deciding whether a lane is in flight; phantom re-prompts (FX-GATE-11, EX-EFF-9); redelivery owed but forgotten (FX-MOVE-3).
**Evidence:** Narrated only — FX-MOVE-3, FX-ABORT-6, EX-ABORT-5, FX-RECOV-33, FX-DQ-13. No incident recorded.
**Cost:** ≈ 240 unified rules (16% of all), ≈ 55 literals (S18), touches 20 of 43 mechanisms via E43/E44; ≈ 130 / 110 lines.
**Environment reality:** On Fable the tools are absent unless `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`; every rule here is then unexecutable and is improvised around. On other models it works as written.
**Options:**
- (a) Hard precondition: `/quo-setup` writes/checks `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`; orchestrators verify at run start (`printenv`, hard-fail `Run /quo-setup first.`). Keeps all ≈ 240 rules; adds ~6.
- (b) Re-carry on the run-state manifest (#4, already deterministic and compaction-safe): sections `## Lanes` (name, status, dispatch-landed), `## Obligations` (`defer-*`, `aborted-*` with the one-line body), `## Round counts`; gate = manifest `Write` then `AskUserQuestion` in the same turn; TaskList becomes an optional progress mirror, never read for routing.
- (c) Dual path — rejected: doubles prose and edges.
- Cut (drop obligation carriers entirely) — loses the deferral gate and Phase C gate; not acceptable.
**Recommendation:** (b). Reason: (a) pins a workflow to a tool the harness treats as optional and model-specific — the exact miss the operator named — and still leaves every rule TaskList-shaped; (b) removes one carrier (TaskList) instead of adding one (env var + check), and the two-step contract's purpose ("a tool call precedes the gate so the model acts, not narrates") is satisfied by a manifest `Write` equally. Rule count falls: the naming convention shrinks to a lane table (~10 rules), prefix-sweep rules become "mark lane closed in the manifest" (~5), the TaskList-derived resume arms read the same table. Estimated ≈ 240 → ≈ 90.
**Residual risk:** Manifest writes are per dispatch (one extra tool call each); a concurrent second orchestrator in the same repo shares the file (already an accepted collision, FX-MAN-17); FX-RECOV-35 ("do not add a lane-phase field to the manifest") must be explicitly reversed, not left contradicting the new design.

## Card 2 — Compromise tracker, triggers, PM tracker check, post-completion challenges
**What it is:** #24 tracker file + five-field entry + Decision enum + Triggers A–D, #26 SR-6.7/SR-4.6 recovery gates, PHASE 1–4 of #25, and the PM's per-unit tracker-blocker check (R-425..439).
**Failure it prevents:** Compromises baked silently into the baseline (FX-TRACK-3); a blocker accepted or deferred without narrowing (FX-TRACK-50/54); an ungated orchestrator pick never challenged (FX-POSTC-37).
**Evidence:** none recorded (rationale rows only).
**Cost:** 81 + 21 + ≈ 45 (POSTC PHASE 1–4) + 15 (R-425..439) ≈ 160 rules; ≈ 45 literals (S12–S14); edges E9, E12, E48–E50, E71–E75; TaskList rows 3 (SR gate tasks only); ≈ 110 / 95 lines.
**Environment reality:** Executable — file carrier, `Write`/`Read`, `AskUserQuestion`.
**Options:** keep as-is | simplify: one trigger table (moment → Decision value → Rationale content → Follow-up field) replacing four prose triggers; one SR gate shape parameterised by axis with labels unchanged | move Decision-enum rationale, "why two override values", and PHASE rationale to a reference file | cut — loses the only run-level challenge of orchestrator judgement.
**Recommendation:** simplify + move rationale; keep every check and label byte-identical (S12/S13). Reason: the mechanism works today and is the single defense on ungated picks; its prose is 4× its rule content.
**Residual risk:** Tracker notation drift (`YYYYMMDD-HHMM` vs `<…>`) must be fixed at the one definition site; an accidentally reworded SR label silently breaks Trigger D.

## Card 3 — Run-state manifest, boundary checkpoint, context guard, post-compaction recovery
**What it is:** #4, #20, #21, #6 — the file that survives compaction, the per-boundary verify-and-rewrite, the external-gauge stop, and the re-read/re-derive rules (fix: Analyst re-derivation shape).
**Failure it prevents:** Acting on a compacted summary (FX-LOOP-11); foreign-checkout SHA scoping Section 8 wrongly (FX-MAN-19); compaction mid-Issue (FX-GUARD-7); reconstructing a lost proposal from memory (FX-RECOV-5).
**Evidence:** FX-MAN-19 (narrated), FX-RECOV-33 (accepted wasted round); none recorded as incidents.
**Cost:** 77 + 46 + 41 + 44 = 208 rules; ≈ 120 literals (S16, S17, S19); edges E9–E15, E25–E26, E64–E69; TaskList rows FX 26 / EX 11; ≈ 285 / 275 lines.
**Environment reality:** Manifest, checkpoint and recovery execute today. Guard depends on a status-line producer: where none publishes, `read` returns `missing` at every boundary and the four-option gate fires unless the opt-out marker exists.
**Options:** keep | simplify: checkpoint to a five-line verify list + one rewrite; guard to a ten-line helper-driven branch with the question text moved to `context_gauge.py --gate-text`; recovery keeps re-derivation and drops the TaskList arms (Card 1 re-carries them) | re-carry: manifest gains the lane/obligation sections from Card 1 (reverses FX-RECOV-35) | move the 21 rationale rows and the collision-case discussion to a reference file.
**Recommendation:** keep all four, simplify as above, extend the manifest per Card 1. Reason: this is the only carrier that works everywhere; the CLAUDE.md lead-statement mirror is already mandated. Guard: keep but make the `missing` path honour the opt-out first and shorten the gate text (the helper already owns the threshold).
**Residual risk:** `HEAD~N`/`HEAD~M` fallbacks under-count when Encode or postcomp commits land (FX inc. 9, EX inc. 7) — replace with `git log --grep` on the subject token or drop the fallback and hard-stop on a missing manifest.

## Card 4 — Movement / abort machinery
**What it is:** #8 movement rung and `aborted-*` markers, #9 unexplained-movement gate, #22 aborted close-out (fix: 4 steps with mode branch; exec: 3 steps, always ends run), plus the postcomp restatements (FX-POSTC-82..94 / EX-POST-50..55).
**Failure it prevents:** Reviewing unfinished tests/docs after a writer stopped (FX-MOVE-3); blind re-dispatch into a moving tree (FX-UNEXP-2); a marker or dirty tree leaking into the next unit/session (FX-ABORT-6, -26; EX-ABORT-5).
**Evidence:** narrated in the four rows above; none recorded.
**Cost:** 40 + 17 + 40 ≈ 97 rules; ≈ 47 literals; edges E36–E42, E70; TaskList rows FX 27 / EX 30; ≈ 75 / 60 lines.
**Environment reality:** Writer-side detection lives in the role files and runs; orchestrator-side marker is TaskList-carried → currently improvised.
**Options:** keep | simplify: state the rung once scope-generically (Issue / Subtask / Bee / postcomp) instead of three restatements; collapse attribution to a three-line table | re-carry `aborted-*` as an `## Obligations` row in the manifest (Card 1) | cut the unexplained gate — loses the only stop before a re-dispatch loop; not recommended.
**Recommendation:** keep, simplify, re-carry. Reason: the marker is the whole mechanism; once it lives in the manifest the rung is ~15 rules. Keep fix's strict branch and exec's sibling-concurrency branch as a one-line mode switch.
**Residual risk:** Exec's bees `in_progress` corrective (EX-MOV-16..21) stays exec-only prose; the postcomp "abort this lane" reading still needs its own two lines.

## Card 5 — Deferral-hygiene gate and defer-* ledger
**What it is:** #23 Steps 0–3 (Fix / File / Encode, `hive_commit.py` follow-up commit) + #17 ledger + #31 Analyst-block consumption (fix).
**Failure it prevents:** Deferrals surfaced mid-run evaporating before reaching a durable carrier (FX-HYG-84); a dirty tree at yield from Encode writes (FX-HYG-56); gate firing empty because records were never created (FX-LEDGER-9).
**Evidence:** none recorded.
**Cost:** 90 + 14 + 19 = 123 rules; ≈ 40 literals (S5, S27); edges E18, E53–E61, E77; TaskList rows FX 34 / EX 21; ≈ 85 / 63 lines.
**Environment reality:** Ledger is TaskList → improvised; Encode/File/commit steps execute.
**Options:** keep | simplify: one firing definition parameterised by site (fixed / aborted / batch-end) instead of three paragraphs; Step 0 kept as one sentence | re-carry ledger as manifest `## Obligations` rows with destination annotation (Card 1) | cut Encode (keep Fix/File only) — loses ticket-body encoding, the only path that lands a deferral on an existing Bee.
**Recommendation:** keep all three routes, simplify, re-carry. Reason: it is the only inter-session carrier for deferred review items; the helper already encapsulates the commit. Unify the label to one spelling (`addressed-now`) across pm.md, analyst.md and both skills.
**Residual risk:** Per-item routing relies on the auto-appended free-text slot (FX inc. 14) — state it explicitly as the one gate where free text is the primary path.

## Card 6 — Routing discipline and trailer consumption
**What it is:** #15 SBL + parts (a)–(g) with rows 1–6, gates (c)/(d), blocker rules, shims; #16 "follow the trailer literally".
**Failure it prevents:** Silent scope-narrowing in a re-dispatch prompt (FX-ROUTE-52); building an unasked mechanism inside the unit (FX-ROUTE-93); accepting/un-narrowed-deferring a blocker; a writer redoing work on a diff the pending review rewrites (FX-ROUTE-123); non-terminating nit loops.
**Evidence:** none recorded in the inventory.
**Cost:** 139 + 18 = 157 rules; ≈ 50 literals (S8, S9); edges E46–E53; TaskList rows FX 8 / EX 16; ≈ 118 / 110 lines (ODR lines are the longest in both files).
**Environment reality:** Executable — `AskUserQuestion`, `Agent`, `/quo-file-issue`; only the gate-task step depends on TaskList.
**Options:** keep as-is | simplify: body keeps SBL, Step 1/2 table, gate (c)/(d) choice sets and the blocker rules (~40 rules); (b) forbidden phrasings, (e)/(f) shims, "what highest-quality means", and all rationale move to a shared reference file read on demand | cut shims (e)/(f) — loses legacy-tag handling; low value once review skills always emit tags | never: reduce lanes or rounds.
**Recommendation:** simplify + move to reference; keep both skills' nine divergences as an explicit two-column table rather than parallel prose. Reason: the table is intrinsically ~40 lines; the surrounding 80 are explanation.
**Residual risk:** A reference file read after compaction costs a `Read` per finding batch; the rewrite must place "Read the routing reference before routing" in the first 5,000 tokens.

## Card 7 — Analyst gate, design directive, design-question receiver (fix-issue only)
**What it is:** #30 always-dispatched Analyst + verdict preamble + Approve/Revise/Cancel; #32 directive composition; #33 `## Design question` → Section 3 Revise by reference; #31 deferred-refinements consumption.
**Failure it prevents:** Treating the body's framing as design (FX-ANA-2); paraphrase corrupting identifiers (FX-PROMPT-5); an Engineer inventing an unenumerated mechanism (R-155); banked refinements lost on re-fire (FX-DEFC-17).
**Evidence:** R-014/R-155 narrate half-fixes and undecided mechanisms; none recorded as incidents.
**Cost:** 61 + 8 + 25 + 19 = 113 rules; ≈ 60 literals (S1, S6, S7, S24); edges E16–E28; TaskList rows 22; ≈ 100 lines.
**Environment reality:** Executable except `analyst-*`/`-rev<n>` tracking and the DQ sweep (Card 1).
**Options:** keep | simplify: four preamble templates → one rule ("name the verdict; lead with ⚠️ on the two divergent verdicts; name the count of policy decisions"); DQ stated as "Revise, by reference" in five lines | cut the gate (auto-approve `recommend-as-stated`) — loses the user's ratification of policy decisions; not recommended | move "anti-pattern: do not classify upfront" rationale to reference.
**Recommendation:** keep, simplify. Reason: the Analyst is the workflow's design-quality lever and its contract headings are already pinned in `agents/analyst.md`; the skill only needs the surface-and-gate flow and the directive shape.
**Residual risk:** FX inconsistency 2 (directive to writers) must be settled: recommend writers never receive the directive (FX-PROMPT-12) and FX-ANA-60 is corrected.

## Card 8 — Dispatch shape, roles, loop skeleton, PM wiring
**What it is:** #5 loop (Read/Reconcile/Yield, no clock primitives; fix Phase A/B/C; exec per-Subtask fan-out), #10 prompt contents and relays, #11 roles, #7 Engineer-dispatch precondition ordering, #14 scoped-marker wiring, #39 PM dispatch, #16 reviewer dispatch.
**Failure it prevents:** Polling/warm-agent assumptions the substrate lacks; identifier corruption; a renamed relay heading dropping a review check (FX-PROMPT-26); loosened role lanes (FX-ROLES-7); writers reading a diff the pending review rewrites (Phase ordering).
**Evidence:** R-159, R-162 narrate sibling-edit sweeps and round-per-site; none recorded.
**Cost:** 47 + 56 + 29 + 31 + 6 + 4 + 18 ≈ 190 rules; ≈ 140 literals; edges E29–E35, E43, E52; TaskList rows FX 17 / EX 19; ≈ 230 / 230 lines.
**Environment reality:** Executable; the precondition's carrier moves per Card 1.
**Options:** keep | simplify: one dispatch-shape paragraph + a relay table (heading → source → recipients → "even when fixed line"); roles reduced to a seven/eight-line list pointing at `agents/*.md` (drop restated responsibilities, FX-ROLES-10..24); Phase A/B/C as a six-line ladder | cut the exec Subtask fingerprint-union rules (EX-DPS-6..11) — loses writer safety on concurrent siblings; keep | move hub-and-spoke/warm-dispatch rationale to reference.
**Recommendation:** simplify + move. Reason: half of these rules restate role-file content that is reloaded on every cold dispatch anyway (R-* is authoritative).
**Residual risk:** S2–S4 relay headings must appear verbatim in the relay table; the exec fingerprint-union stays ~8 lines of dense prose.

## Card 9 — Summaries, templates, final output, GH block, doc verification
**What it is:** #19 per-unit and run-end summary blocks + second-order relay + accepted-compromises render; #35 GH close block (fix); #34 doc verification (fix); #42 Final, #43 Merge (exec).
**Failure it prevents:** A conditional field nobody can rely on (FX-SUM-15); compromises truncated out of view (FX-SUM-24); a `gh` auth assumption baked in (FX-GH-5); SHA mis-pairing (FX-GH-25).
**Evidence:** none recorded.
**Cost:** 34 + 33 + 7 + 11 + 5 = 90 rules; ≈ 70 literals (S10, S15, S26); edges E55–E56, E62, E81; TaskList rows 0; ≈ 100 / 80 lines.
**Environment reality:** Executable.
**Options:** keep | simplify: one template per skill with field rules inline; GH block to eight lines keyed on the subject token | cut #34 (fold "PM verdict captured" into the `**Doc Sync**` field) | move render-rule rationale to reference.
**Recommendation:** simplify; cut #34 as a section (keep the one confirmation bullet). Reason: templates are the user-visible contract and cheap; #34 is informational only (FX-DOCV-1).
**Residual risk:** `**Reviews**` nit-count slot per lane is unspecified (FX inc. 13) — define once.

## Card 10 — Preconditions, effort gate, isolation, argument parsing, unit selection, shell conventions
**What it is:** #1, #2, #3, #28 ARG (fix), #29 VAL (fix), #36 META, #37 BEE, #38 EPIC (exec), #27 shell/scratch.
**Failure it prevents:** Guessed build commands/doc paths (FX-PRE-14); many commits on `main` (FX-ISO-2); losing user-intended batch order (FX-ARG-16); stranded gate prompts (FX-GATE-11).
**Evidence:** none recorded.
**Cost:** 21 + 24 + 17 + 56 + 11 + 9 + 10 + 17 + 7 = 172 rules; ≈ 110 literals; edges E1–E8, E82; TaskList rows FX 9 / EX 10; ≈ 250 / 190 lines.
**Environment reality:** Executable except gate tasks (Card 1) and `file-from-url-<n>` tracking.
**Options:** keep | simplify: effort gate to eight lines (helper-free, two commands); ARG URL resolution to a ten-line procedure + one display line; isolation to one paired snippet + three options; drop ARG's flow restatement (FX-ARG-49..52) | cut the effort gate — loses the only floor check; keep | move rationale to reference; inline the scratch-file snippet once (rule 3 forbids referencing CLAUDE.md `## Scratch-file convention`).
**Recommendation:** simplify; also fix EX-META typo and "Team" vocabulary. Reason: mechanical steps with little judgement; most lines are POSIX/PowerShell pairs that can share one block per file.
**Residual risk:** FX inc. 8 (isolation prompt outside the gate contract) resolves itself once gates are manifest-fronted (Card 1).

## Card 11 — Post-completion sweep and follow-up lanes
**What it is:** #25 minus the PHASE 1–4 checks (Card 2): fresh `general-purpose` reviewer with self-contained prompt over the pre-run diff, PHASE 5/6, synthesis, Fix/File/Skip gate, `*-postcomp-<n>` lanes with their own precondition/movement/close-out, commit.
**Failure it prevents:** The team-lead rubber-stamping its own run (FX-POSTC-8); lane-scoped skills missing cross-lane defects (FX-POSTC-5); mis-routing a lane abort through the Issue-level close-out (FX-POSTC-90).
**Evidence:** none recorded.
**Cost:** ≈ 66 rules; ≈ 30 literals; edges E74–E77; TaskList rows FX 13 / EX 15; ≈ 110 / 120 lines (the prompt skeleton is ~80 of them).
**Environment reality:** Executable; lane tracking per Card 1.
**Options:** keep | simplify: postcomp lane rules become "the per-unit rules apply with `postcomp-<n>` as the unit" (one paragraph) | move the six-PHASE prompt skeleton to a shipped reference file (`skills/quo-execute/references/post-completion-prompt.md`, read by both skills via the existing sibling-path discipline) with two substitution notes (diff scope, spec noun) | cut — no.
**Recommendation:** move skeleton + simplify. Reason: the skeleton is verbatim-shared text with two parameters; keeping two copies in-body is the largest single duplication in the set.
**Residual risk:** Diff-scope divergence (`..HEAD` vs working tree + untracked) must be a deliberate parameter, not an accident — see open question 6.

## Card 12 — Per-unit close-out, commit, testing ladder, next-Epic routing
**What it is:** #18 flip + Format + judgement staging + `hive_commit.py resolve-hive-paths` + subject contract + sweep; #40 five-rung testing ladder (exec); #41 inter-Epic interaction checkpoint and branch classification (exec).
**Failure it prevents:** `git add -A` sweeping other agents' edits (FX-CLOSE-15); `drafted` Epics falling through to final review (EX-NEXT-8); redundant full-suite runs (EX-TEST-8).
**Evidence:** none recorded.
**Cost:** 46 + 12 + 21 = 79 rules; ≈ 60 literals (S15); edges E62–E66, E78–E79; TaskList rows FX 3 / EX 5; ≈ 40 / 90 lines.
**Environment reality:** Executable.
**Options:** keep | simplify: TEST rungs 1–4 already live in role files (R-173..179, R-238, R-409) — keep only rung 5 in the orchestrator; commit step as a six-line recipe shared modulo hive/subject | cut the Director-run interaction checkpoint — loses cross-Epic drift detection; instead dispatch it (Engineer/PM) to honour delegate mode | move rationale to reference.
**Recommendation:** simplify; convert the interaction checkpoint into a dispatched PM/Engineer pass (open question 7). Reason: the ladder is duplicated role prose; the subject token is a pinned contract (S15) that needs one line each.
**Residual risk:** EX inc. 5/6 (manual staging recipe vs helper) must be resolved in favour of the helper only.

## Inconsistencies to resolve
Fix-issue (FX) 1–18 and execute (EX) 1–15 from the consolidated files; proposed resolution in one line each.
1. FX-1 in-flight Issue status: delete FX-VAL-11; Issues have only `open`/`done`.
2. FX-2 directive to writers: writers never receive the directive; correct FX-ANA-60; delete the "conditional-dispatch rules" referent.
3. FX-3 single-mode Cancel: Section 3 text adopts FX-ABORT-23 (proceed to post-completion over what landed).
4. FX-4 destination labels: one literal `addressed-now` in pm.md, analyst.md, both skills.
5. FX-5 compaction-artifact `defer-*`: record it in the summary field only; create no ledger entry (an `addressed-now` item never enters the ledger).
6. FX-6 gate-suffix uniqueness: suffix = monotonic per-run integer; drop the Issue-slug option.
7. FX-7 / EX-3 gate enumerations incomplete: delete both lists; state "every `AskUserQuestion` this skill fires" once.
8. FX-8 isolation prompt ungated: covered by rule 7 once gates are manifest-fronted.
9. FX-9 / EX-7 `HEAD~N`/`HEAD~M`: replace with subject-token `--grep` bound or hard-stop on missing manifest (Card 3).
10. FX-10 step list omits 7.5: regenerate the overview from the final section list.
11. FX-11 self-tracking task class: delete (no ad-hoc tasks; manifest lanes only).
12. FX-12 eight vs seven roles: keep the divergence; make `<missing-list>` the only variable in the shared message.
13. FX-13 nit-count slot: one `N nits applied without re-review` per lane slot, or omit.
14. FX-14 free-text routing at the deferral gate: state explicitly as the one free-text-primary gate.
15. FX-15 movement-report `completed` carve-out: define "lane closed = Agent gone" once in the lane table.
16. FX-16 class quirks: no action (extract artefact).
17. FX-17 "stated once" claim: state the stranded-`pending` clause once in the lane table; delete restatements.
18. FX-18 / EX-11 "Section" vs "Step": one vocabulary (`Section N`), enforced by a doc test.
19. EX-1 "three scenarios": say two.
20. EX-2 branch 3 described two ways: Section 2 adopts 4.2's wording (checkpoint then final review).
21. EX-4 completeness heading recommended vs required: required label, unconditional attribution.
22. EX-5/6 hive-path source and manual recipe: helper only; delete the decomposed recipe.
23. EX-8 shared gate labels: distinct third options already differ; with manifest-fronted gates the `metadata.activity` ambiguity disappears — no action.
24. EX-9 "Team" vocabulary: rewrite overview.
25. EX-10 tracker notation: one spelling `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md` everywhere.
26. EX-12 `general-purpose` forbidden vs required: qualify the precondition "as a substitute for a missing role".
27. EX-13 Mode 1 gate on single-Epic run: fire the continuation gate whenever branch 2 is reached and no mode was captured; record `captured late` in the manifest.
28. EX-14 typo "therin": fix.
29. EX-15 row-6 tracker append stated unconditionally: add "(except a lone `trivial-tweak`)" at the routing site.
30. INVENTORY divergence "part (g) rung": keep both readings; name them Clause 1/2 in both skills (fix has one clause).
31. INVENTORY S28: confirm `/quo-engineer-review` emits `No code issues found.`; otherwise Phase A exits on an empty numbered list.
32. INVENTORY S29: no action after rule 23.
33. FX-RECOV-35 vs Card 1: reverse the "no lane-phase field" invariant explicitly.

## Size projection
Current: fix ≈ 1,342 lines / 1,177 rules; exec ≈ 1,322 lines / 790 rules (both ≈ 43K tokens; post-compaction truncation keeps ≈ 5,000 tokens ≈ first 150 lines).
If every recommendation is taken: TaskList re-carry (−≈150 unified rules, +≈40 manifest rules); rationale/examples to reference (−≈165); role/ladder restatements cut (−≈45); routing (b)/(e)/(f)/definitions to reference (−≈60); post-completion skeleton to reference (−≈45); tracker/SR/guard prose collapsed to tables (−≈70); doc-verification section cut (−7); duplicated shell snippets shared (−≈20).
Projected unified ≈ 1,457 → ≈ 940 rules total; per body: **fix ≈ 560 rules / ≈ 540 lines; exec ≈ 420 rules / ≈ 450 lines** at the current ≈ 1 rule per line.
To reach ≤ 500 lines in fix-issue, additionally move to shipped reference files: ARG URL-resolution procedure (≈ 30 lines), GH block procedure (≈ 25), and the tracker trigger table (≈ 30) → **fix ≈ 455 lines**. Reference files (shipped under `skills/*/references/`, resolved by the existing sibling-path discipline): `routing.md` (≈ 130 lines, shared), `post-completion-prompt.md` (≈ 90, shared), `compromise-tracker.md` (≈ 60, shared), `context-guard.md` (≈ 50, shared), `rationale.md` (≈ 150, shared), `url-resolution.md` + `github-close.md` (fix). The first 150 lines of each body must contain: preconditions, manifest write/read, the post-compaction rule ("re-read the manifest; Read the reference files before routing or reviewing"), and the loop skeleton.

## Open questions for the operator
1. Card 1: confirm option (b) over (a); if any other model will run these skills with TaskList on, is a read-only progress mirror worth its ~10 lines?
2. Reverse FX-RECOV-35 (manifest carries lane phase)? The text forbade it only because TaskList carried it.
3. Are shipped reference files under `skills/<name>/references/` acceptable as post-compaction reading, given each costs a `Read` per use and must stay rule-3 clean?
4. Keep the nine routing divergences (blocker base pair, `Cancel` at (c), gate-(d) sets, part-(g) rung) or converge exec on fix's shape by giving exec a stop-and-re-plan choice with the same label?
5. Statusline guard: does the operator's environment publish `context-usage-<session_id>.json`? If never, choose: persistent opt-out by default, or fix the producer in `quo-setup`.
6. Post-completion diff scope: unify on working-tree-plus-untracked (exec) or committed range (fix)?
7. Inter-Epic interaction checkpoint: dispatch it (delegate mode) or keep it Director-direct?
8. Destination label: `addressed-now` (new) or keep `addressed-now-in-this-Task` and edit analyst.md?
9. May the effort-gate and guard question texts move into the helpers (`context_gauge.py --gate-text`) to shorten the bodies, or must all user-facing text stay in SKILL.md?
