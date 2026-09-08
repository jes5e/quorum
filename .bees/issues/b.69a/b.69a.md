---
id: b.69a
type: bee
title: Make the review-finding routing default (ask vs orchestrator picks) a per-project CLAUDE.md setting; b.nn8 hard-codes one operator's preference
status: open
created_at: '2026-09-08T14:55:34.419650'
schema_version: '0.1'
reference_materials: null
guid: 69apjn2x9jn5436avx8dci5iwm6rrg2z
---

## Description

Issue b.nn8 changes the review-finding routing default from "gate every multi-path finding" to "the orchestrator picks the highest-quality path; gate only re-architect, scope-widening, and mechanism-introducing fixes." The evidence for the new default is one operator's rejection of one gate on one project (the quoted "we don't care about how much work" exchange on the b.239 run). Quorum ships to many teams; some will want to be asked before an orchestrator picks a fix path with contract or API implications. The default is a preference, not a correctness property, and it is currently hard-coded.

## Current behavior

After b.nn8 lands, every installation routes multi-path findings to orchestrator judgment with no per-project way to restore the gate.

## Expected behavior

The routing default becomes a **per-project setting in the target repo's CLAUDE.md**, written by `/quo-setup` as an optional key (exact key name to be chosen by the Analyst; it joins the contract-key list and must not collide with existing keys):

- **Absent or `ask` (the shipped default):** multi-path findings route to the user gate as before b.nn8, *except* that b.nn8's correctness rules stay unconditional — mechanism-introducing findings still route to gate (c), the "highest quality" definition still governs the pick when a pick is made, and the blocker rules (b.qb1 Amendment 7) still apply.
- **`orchestrator`:** b.nn8's behavior — the orchestrator picks, records the pick and rationale in the compromise tracker, and gates only re-architect / scope-widening / mechanism cases.

`/quo-setup` offers the choice during setup with a one-line explanation of the trade (fewer interruptions vs. a human on every multi-path finding); the fast path leaves an existing value alone.

## Impact

Portability. Without it, one team's preference is baked into a tool used by many; with it, the correctness half of b.nn8 ships to everyone and the preference half is a documented choice.

## Suggested fix

1. `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md` routing sections: read the key; branch Step 2's first-match table on it (only the "otherwise dispatch ungated" row changes to a gate when the key is `ask`).
2. `skills/quo-setup/SKILL.md` (Build Commands / Documentation Locations neighbor section): write the key with the operator's choice; README documents it.
3. CLAUDE.md `## Contract keys` in this repo: add the key; `tests/test_shipped_artifact_portability.py`'s `ALLOWED_SECTIONS` unaffected (the key lives in an existing section) — the Analyst confirms.
4. Sequence after b.nn8 merges; small.

## Background and rationale

Raised 2026-09-08 when the operator asked whether b.nn8 reflected quorum's many users or one session's prompts. The orchestrator-decides default was the one part of the three process tickets (b.q3f, b.pdq, b.nn8) derived from a single user's stated preference rather than from a run pathology. Filed as a follow-up rather than widened into the in-flight b.nn8 run because a new contract key is a new mechanism (b.nn8's own rule).

