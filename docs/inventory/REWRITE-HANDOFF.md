# Rewrite handoff — 2026-09-09

Repo-only document; nothing here ships. Read `REWRITE-BRIEF.md` first; this file records where the implementing session stopped.

## Where the work is

- Worktree: `/workspaces/worktrees/quorum-rewrite`, branch `rewrite/orchestrators`, based on `main` at `17ea50d`. Never merged; `main` untouched.
- Commits: `3048c28` (bodies, reference files, role-file edits, breakdown-epic label rename, test suite) and `a26f922` (CLAUDE.md `## Working on the orchestrator skills`, test-writing guide scope, SDD Feature entry). The commit adding this note is the handoff commit (`git log -1 --oneline -- docs/inventory/REWRITE-HANDOFF.md`).
- Suite: `python -m pytest tests/` → 475 passed (was 559; six prose-pin modules deleted, structural module added). Lint clean.
- Line counts: `skills/quo-execute/SKILL.md` 323, `skills/quo-fix-issue/SKILL.md` 303. Reference files: 850 lines total across seven files.

## What is in flight

A cold `code-reviewer` Agent was dispatched against `main..HEAD` with brief §6 (A1–A9) embedded as criteria. Its report had NOT been received when the session ran out of context. **Next session: re-dispatch that review** (prompt shape: scope `main..HEAD`, read the brief and inventory first, D1–D12 final, criteria A1–A9, role-play both runs, return findings in the review-skill shape plus an A1–A9 PASS/FAIL checklist), then fix findings and re-review until a pass returns nothing above a `trivial-tweak` nit. No round cap.

## Judgment calls the reviewer and operator should know about

1. **D4 interpretation.** `missing` → record `no reading` in a new `**Context guard:**` manifest field and continue silently (opt-out marker or not); the four-option missing-reading gate is gone. The guard's only `AskUserQuestion` fires on an integer reading ≥ threshold with `Stop here` (Recommended) / `Proceed without the guard (this run)`. `stale` / non-zero exit / empty stdout remain fail-safe STOPs. If D4 meant the ≥-threshold stop to stay unconditional, delete that gate and restore the STOP.
2. **D8 reach.** `addressed-now` also replaced the label in `skills/quo-breakdown-epic/SKILL.md` (3 occurrences) because it consumes the PM contract; the brief's keep-list did not name that file.
3. **Frontmatter typo** `therin` → `therein` fixed per inconsistency 28 although §1 freezes frontmatter.
4. **Literal changed:** `## Authoritative design directive (from Section 3 Analyst pass)` → `## Authoritative design directive (from the Analyst gate)` (old parenthetical named a section that no longer exists; the `## Authoritative design directive` prefix the Engineer keys on is unchanged).
5. **Anchor heading levels** are all `####` (old exec used `#####`); heading text unchanged.
6. **`HEAD~N` fallback** replaced by a hard-stop on a missing or foreign manifest at post-completion (inconsistency 9 offered either).
7. **Known follow-ups not done:** README's context-guard paragraph (line ~176) still describes the retired missing-reading gate; `/quo-breakdown-epic` still uses the TaskList-fronted two-step gate contract and TaskList `defer-*` ledger (out of the brief's scope); CLAUDE.md `## AskUserQuestion usage` was qualified rather than rewritten.
8. **Possible A3 gaps to check first:** the Bee-ID-path Epic-children query literal (`[parent=<bee-id>, type=t1, status=ready] report: [title, up_dependencies]`) was folded into the run-start Epic query; fix-issue Section 8 does not name `#### <invocation scope>` sub-block labels explicitly.

## Structural shape (both bodies)

Sections `## 1. Preconditions` … `## 13. Final output`, identical numbering; Sections 1–5 within the first 150 lines. Tier 1 byte-identical sections: `## 7. Routing discipline`, `## 10. Compromise tracker`, lead paragraphs of Sections 3–6, the effort gate, the Tick skeleton, the movement-rung closing rules. Tier 2 (normalized): Section 9 bullets, Section 11 steps, guard steps. `tests/test_orchestrator_structure.py` encodes the pair list.
