# Rewrite handoff — 2026-09-09

Repo-only document; nothing here ships. Read `REWRITE-BRIEF.md` first; this file records where the implementing session stopped.

## Where the work is

- Worktree: `/workspaces/worktrees/quorum-rewrite`, branch `rewrite/orchestrators`, based on `main` at `17ea50d`. Never merged; `main` untouched.
- Commits: `3048c28` (bodies, reference files, role-file edits, breakdown-epic label rename, test suite) and `a26f922` (CLAUDE.md `## Working on the orchestrator skills`, test-writing guide scope, SDD Feature entry). The commit adding this note is the handoff commit (`git log -1 --oneline -- docs/inventory/REWRITE-HANDOFF.md`).
- Suite: `python -m pytest tests/` → 475 passed (was 559; six prose-pin modules deleted, structural module added). Lint clean.
- Line counts: `skills/quo-execute/SKILL.md` 323, `skills/quo-fix-issue/SKILL.md` 303. Reference files: 850 lines total across seven files.

## Review loop status

Round 1 (cold `code-reviewer`, brief §6 A1–A9 embedded, scope `main..HEAD`) returned 15 findings: 5 blockers (exec never selected the Epic to work; exec's checkpoint imported fix's hygiene-gate ordering; the review skills' trailer still prescribes the two-step gate contract; README described the retired missing-reading gate; seven numeric `Section N` pointers from role files and review skills broke under the renumbering), 6 suggestions (D9 paragraph condensed instead of verbatim; exec hygiene gate moved before post-completion; CLAUDE.md exemption (ii) stale; no open-lane dispatch guard in fix; FX-PROMPT-36 missing from fix; late-capture rule not at branch 2), 4 nits. All 15 were fixed in the commit that follows the handoff commit; suite 475 green.

Round 2 returned 2 blockers (the pointer sweep had missed `quo-breakdown-epic`, `quo-plan`, `quo-file-issue`, and `hive_commit.py`'s docstring; README's D4 text over-claimed for `/quo-breakdown-epic`), 6 suggestions (checkpoint step 2 wrote the guard field before the guard ran; the D6 inter-Epic reviewer had no part-(g) clause; SDD/PRD/CONTRIBUTING/doc-writing-guide still carried retired labels and TaskList descriptions; the post-compaction `dispatched: no` default would re-dispatch live lanes; inconsistency 27 landed as a run-mode gate instead of the continuation gate), 11 nits. All fixed in the following commit.

Round 3 returned 1 blocker (the three run-start gates fire before the manifest exists, so Section 6's contract was unsatisfiable there — now scoped: those gates fire `AskUserQuestion` directly and the `## Open gate` discipline begins at the manifest write), 6 suggestions (url-resolution's pre-manifest lane row deleted per inconsistency 11; fix Phase C re-entry names the PM; post-completion commit waits on `aborted-*` obligations; exec states second-order effects are narrative; gate (d)'s `Defer` ships nothing; analyst/pm role files no longer name a TaskList carrier), 4 nits (checkpoint verifies `## Open gate` is `none`; abort detail lands on obligations; remaining doc pointers in CLAUDE.md/CONTRIBUTING/PRD/SDD; the Epic-boundary classifier split into three bullets). All fixed in the following commit.

Prompt shape for each further round: scope `main..HEAD`, read the brief and inventory first, D1–D12 final, criteria A1–A9, role-play both runs, return findings in the review-skill shape plus an A1–A9 PASS/FAIL checklist. Loop until a pass returns nothing above a `trivial-tweak` nit. No round cap.

## Judgment calls the reviewer and operator should know about

1. **D4 interpretation.** `missing` → record `no reading` in a new `**Context guard:**` manifest field and continue silently (opt-out marker or not); the four-option missing-reading gate is gone. The guard's only `AskUserQuestion` fires on an integer reading ≥ threshold with `Stop here` (Recommended) / `Proceed without the guard (this run)`. `stale` / non-zero exit / empty stdout remain fail-safe STOPs. If D4 meant the ≥-threshold stop to stay unconditional, delete that gate and restore the STOP.
2. **D8 reach.** `addressed-now` also replaced the label in `skills/quo-breakdown-epic/SKILL.md` (3 occurrences) because it consumes the PM contract; the brief's keep-list did not name that file.
3. **Frontmatter typo** `therin` → `therein` fixed per inconsistency 28 although §1 freezes frontmatter.
4. **Literal changed:** `## Authoritative design directive (from Section 3 Analyst pass)` → `## Authoritative design directive (from the Analyst gate)` (old parenthetical named a section that no longer exists; the `## Authoritative design directive` prefix the Engineer keys on is unchanged).
5. **Anchor heading levels** are all `####` (old exec used `#####`); heading text unchanged.
6. **`HEAD~N` fallback** replaced by a hard-stop on a missing or foreign manifest at post-completion (inconsistency 9 offered either).
7. **Edits outside the brief's keep-list, forced by the rewrite itself (round 1):** README's three context-guard sentences now describe D4's behaviour; the seven numeric `Section N` pointers in `agents/engineer.md`, `agents/test-writer.md`, `agents/code-reviewer.md`, and the three review skills' routing trailers were replaced by the anchors they meant (no other text in those files changed). The review skills' two-step `TaskCreate` prescription itself was left alone (D9); each body's Section 6 lead now says the manifest-fronted contract substitutes for it.
8. **D9 as landed:** the pre-rewrite **Severity bounds the loop** paragraph is restored verbatim with three D1-forced substitutions (`defer-*` task → obligation, twice; conversation-carried nit count → manifest `## Rounds`, per lane). `## Rounds` gained a `role` column (inconsistency 13).
9. **Exec ordering restored to the inventory:** the deferral-hygiene gate fires after Section 11 and before Section 13 (was before Section 11); the Epic-boundary checkpoint no longer waits on the hygiene gate or checks the `defer-*` ledger; the aborted close-out no longer runs the hygiene gate.
10. **Known follow-ups not done:** `/quo-breakdown-epic` still uses the TaskList-fronted two-step gate contract and TaskList `defer-*` ledger (out of the brief's scope); CLAUDE.md `## AskUserQuestion usage` was qualified rather than rewritten; `skills/quo-file-issue/SKILL.md` lines ~443/458 cite a `/quo-fix-issue` "Section 6 close-out" that was already wrong before the rewrite (pre-existing; file, do not fix here).

## Structural shape (both bodies)

Sections `## 1. Preconditions` … `## 13. Final output`, identical numbering; Sections 1–5 within the first 150 lines. Tier 1 byte-identical sections: `## 7. Routing discipline`, `## 10. Compromise tracker`, lead paragraphs of Sections 3–6, the effort gate, the Tick skeleton, the movement-rung closing rules. Tier 2 (normalized): Section 9 bullets, Section 11 steps, guard steps. `tests/test_orchestrator_structure.py` encodes the pair list.
