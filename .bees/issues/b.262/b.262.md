---
id: b.262
type: bee
title: 'Compromise tracker vocabulary and enum hygiene after b.nn8: rename to a decision-ledger vocabulary, retire unreachable Decision values, rename SR-6.7''s pinned strings'
parent: null
reference_materials: null
created_at: '2026-09-04T08:37:56.354582'
status: open
schema_version: '0.1'
guid: 262g14efu68dyxee7yt8iugzemdb2rct
---

## Description

Three related residues left in the compromise tracker's vocabulary and `Decision` enum after b.nn8 replaced the `(num-paths, max-depth)` routing table with the orchestrator's pick-then-route procedure. Each was deferred from that run because its fix is a name-class change or a new trigger — the kind of mechanism-introducing work the b.nn8 routing rule itself routes to a follow-up rather than builds in-flight.

1. **The tracker's name misdescribes most of its contents.** Trigger C now appends an entry on every ungated orchestrator pick (`Orchestrator picked path (x) — highest-quality`), so the file is written on most runs and most entries are not compromises at all — they are the orchestrator's highest-quality picks, recorded so the post-completion review can challenge them. The file is still `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`, the section is `#### Session-scoped compromise tracker`, and the end-of-run summary field is `**Accepted compromises**` — a user-visible heading that now renders on most runs over entries that were not accepted compromises.
2. **The `Decision` enum lists values no trigger writes.** `User picked path (a) | User picked path (b) | …` are enumerated in both skills' entry shape, but the routing-decision gate (part (d)) deliberately has no append trigger for a per-path pick (`docs/sdd.md` records this as a design choice), so those values are unreachable.
3. **SR-6.7's heading was renamed but four of its byte-pinned strings still say "auto-route" / "depth".** b.nn8 retitled the gate "ungated-route recovery gate" and widened it to two axes (depth plausibility; mechanism introduction), but kept these strings byte-identical because they are byte-matched against Trigger D at four sites across both skills: `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and `User overrode auto-route after post-completion challenge (depth misjudgment)` (both in Trigger D's branch and in the `Decision` enum line). b.nn8 added a generic-reading clause on the SR-6.7 lead as the interim.

## Current behavior

The tracker, its summary field, and its enum carry b.ut9-era vocabulary that describes a rarely-written record of user-accepted compromises. Under b.nn8 the same file is a routinely-written ledger of orchestrator decisions, two enum values are dead, and one recovery gate's labels name only half of what it now challenges.

## Expected behavior

The tracker's file name, section heading, summary field, `Decision` enum, and SR-6.7 labels describe what the ledger actually holds. Either every enum value has a writer or the value is retired. The SR-6.7 strings name the routing misjudgment generically (depth or mechanism) instead of "depth" alone, and the Trigger D byte-matches move with them.

## Impact

Correctness of the audit trail as read by humans: a user reading `**Accepted compromises**` on an ordinary run sees orchestrator picks labelled as compromises. Maintainability: unreachable enum values invite a future writer to "fix" the gap with a fifth trigger; stale labels on a two-axis gate misdescribe the mechanism-axis branch.

## Suggested fix

Bundle as one pass over the same file regions in both orchestrators:

- `skills/quo-fix-issue/SKILL.md` Section 7.5 (`#### Session-scoped compromise tracker`, entry shape, Triggers A–D) and Section 8 (PHASE 1–3, step 7 SR-6.7 / SR-4.6 gates, the `**Accepted compromises**` render step); the `/quo-execute` mirrors in Section 6.5 and Section 6, plus its Section 9 render step. Keep the PHASE blocks byte-identical across the two skills through PHASE 5 (a test pins that).
- `docs/sdd.md` and `docs/prd.md` (the b.ut9 and b.nn8 `### Feature:` entries and their superseded notes), `README.md` `### Scratch files` (names the tracker file).
- `tests/test_routing_decision_contract.py` pins `DECISION_PICK_VALUE` / `DECISION_PICK_SUFFIX`, the PHASE 3 anchor, and Trigger A/B clauses; update the pins with the rename rather than around it.

Decide (2) as either "add a gate (d) append trigger" (a fifth trigger — weigh against `four append triggers (A/B/C/D)` being stated in both skills, the SDD, and the PRD) or "retire the `User picked path (…)` values" (smaller). Rename the SR-6.7 strings and their Trigger D byte-matches together, in one change, in both skills.

## Additional scope from b.nn8's post-completion review (2026-09-08)

4. **Item 2 is an audit gap, not only enum hygiene.** An *ungated* orchestrator pick writes a Trigger C entry, but a *gated* user pick at the routing-decision gate — the `re-architect` design-direction call, the most consequential answer the flow asks for — writes nothing. Now that gate (d) is where design direction lands, the highest-stakes decision in the flow leaves no durable record while the low-stakes one does. When deciding item 2, weigh "add the writer" against "retire the values" with that reading in view rather than defaulting to deletion.
5. **The byte-matched strings have no test pin.** The four recovery-gate labels the skills newly declare "do not reword them" (`File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, `File follow-up Issue to surface the missing path`, `Accept the under-enumeration and proceed`) at their two sites per skill, and the two `Decision` values PHASE 2 and `agents/pm.md`'s tracker check key on (`User picked Accept the limitation`, `User picked Defer to follow-up Issue`), appear in no test — `grep -rn "SR-6.7\|SR-4.6\|Accept the misjudgment\|User picked Accept the limitation" tests/` returns nothing (only `Orchestrator picked path (x) — highest-quality` is pinned). Renaming any of them leaves the suite green while silently breaking the byte-match. Since this Issue proposes renaming exactly those strings, add the pins as part of the rename (a shared-constant test asserting each label at both sites in both skills, plus the two `Decision` values), so the move is guarded rather than around.

## Background and rationale

All three original items were surfaced during the b.nn8 run (the Analyst's `### Deferred refinements` for 1 and 2, the Code Reviewer's round-1 suggestion 3 for the labels) and routed to a follow-up because b.nn8's own routing rule — the one it was shipping — treats a fix path that adds a new name class, trigger, or byte-pinned contract string as a design change to defer, not build. The generic-reading clause on SR-6.7 and the correction of the four "empty tracker is the common case" claims were the minimal in-run changes. Items 4 and 5 were surfaced by the b.nn8 post-completion reviewer (second pass, over the post-completion fix commit) and appended here on the operator's direction as additional scope.

## Decisions and rejected alternatives

- Keeping both `Decision` values (`Auto-routed (a) per single-path refactor-locally rule` alongside the new pick value) was rejected in b.nn8: it re-introduces path count as a ledger axis exactly as the table dropped it. The retired value is gone; only the pre-existing user-pick values remain unreachable.
- Renaming inside b.nn8 was rejected as ~15 sites across four files plus a user-visible heading — a name-class change beyond the Issue's stated defect.

## Related

- b.nn8 (landed): the routing rewrite that changed the tracker's base rate.
- b.ut9 (landed): introduced the tracker and its vocabulary.

