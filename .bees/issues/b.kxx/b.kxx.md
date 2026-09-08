---
id: b.kxx
type: bee
title: Decide whether the orchestrator may compose a fix path when no reviewer-enumerated path is complete (stripped from b.nn8)
status: open
created_at: '2026-09-08T15:00:03.633935'
schema_version: '0.1'
reference_materials: null
guid: kxxdqv2w8o6hauiofzn4duekq4isqyjs
---

## Description

During the b.nn8 fix run the orchestrator's pick-then-route procedure was widened so that, when no fix path the reviewer enumerated was the smallest internally-consistent complete change, the orchestrator could **compose** the complete fix itself, assign it a depth, and route it like any enumerated path. The run's own compromise tracker had already done this twice before the prose permitted it, which is what surfaced the gap. The post-completion review challenged the widening as an authority extension beyond b.nn8's stated table (the Issue authorizes picking *among* enumerated paths), and the operator directed that it be stripped and filed as its own design decision. This Issue carries the stripped design verbatim so nothing is lost.

## Current behavior

After b.nn8 (as landed), Step 1 reads: "**The pick is always one of the paths the reviewer enumerated.** When *no* enumerated path is the smallest internally-consistent complete change — every one of them leaves the stated defect partly unfixed — pick the most complete of them anyway: row 4 then routes it to gate (c) precisely because it is narrower than the complete fix, and `Fix properly now` there dispatches the complete fix. An incomplete menu is a **reviewer defect** for PHASE 4 to challenge, not a decision the orchestrator absorbs by writing a path of its own."

So the complete fix is reachable, but only through a user gate whose answer is the orchestrator's own composed fix — one click per under-enumerated finding.

## Expected behavior

Decide, as operator policy, whether the orchestrator may compose a fix path when the reviewer's menu has no complete option, and if so land the design below (or a smaller variant) with its full lifecycle: Step 1 origination and depth assignment; the section lead's never-invent carve-out; row 4's by-construction exclusion; Trigger C's record (letter, depth, inline marker, Rationale); gate (c)'s context-line description; gate (d)'s own `(Recommended)` choice; the render steps' "or was composed"; and the test pins (eight tests in `tests/test_routing_decision_contract.py` were removed with the strip).

## Impact

Trade-off between two things b.nn8 cares about. Composing removes a user gate whose answer the orchestrator already holds (the Issue's thesis). Not composing keeps orchestrator authority inside the reviewer's enumeration and surfaces under-enumeration as a reviewer defect. In the b.nn8 run the composed-path branch generated roughly a third of the tracker entries as follow-on repairs across seven threaded sites, which is the cost side of the argument.

## Suggested fix

If adopted: reinstate the prose below in `skills/quo-fix-issue/SKILL.md` and `skills/quo-execute/SKILL.md` (mirror sites: section lead, part (a) Step 1, "What highest-quality means", part (c) context line, part (d) fix-path bullet, the `**Accepted compromises**` render step, Trigger C), reinstate the eight tests, and document it in `docs/sdd.md` and `docs/prd.md`. If rejected: close this Issue with the reasoning and leave b.nn8's row-4 route as the design.

## Background and rationale

The b.nn8 PM surfaced the inconsistency (run applied it; prose forbade it). The orchestrator chose to widen Step 1 rather than route incomplete menus to gate (c), reasoning that a gate whose `Fix properly now` returns the orchestrator's own composed answer is the gate class b.nn8 removes. The post-completion reviewer challenged that as a design-direction decision made without the user and noted the widening's lifecycle cost; the operator agreed and directed the strip. Both positions are defensible; the decision is the operator's.

## Decisions and rejected alternatives

- Ratifying the widening in-run was reversed on operator review (2026-09-08).
- Routing an incomplete menu to gate (c) via row 4 (the landed behavior) was chosen as the smaller system for now.

## Stripped design (verbatim, from the b.nn8 branch before the strip)

### `### Orchestrator discipline: routing review findings` lead (both skills)

> **One carve-out, and only one:** a path the orchestrator **composes** at Step 1 carries no reviewer depth tag because no reviewer ever saw it, so the orchestrator assigns that path a depth itself (Step 1 below). That is origination, not re-classification — no tag the reviewer emitted is ever overwritten.

### Part (a) Step 1 (both skills; execute cites Section 6.5's Trigger C)

> **The enumeration is the menu, not a ceiling.** When *no* enumerated path is the smallest internally-consistent complete change — every one of them leaves the stated defect partly unfixed — the orchestrator may **compose** the complete fix itself and pick that composed path, rather than picking the least-bad enumerated one and routing it to gate (c) as a narrowing. A composed path is the Step-1 pick like any other and routes through Step 2 unchanged; Section 7.5's **Trigger C** records how it was composed. **Assign the composed path a depth** from the reviewer's own three-value vocabulary — `trivial-tweak` / `refactor-locally` / `re-architect` — judging it as a reviewer would; this is the one case where the orchestrator originates a depth rather than reading one, precisely because no reviewer emitted a tag for a path no reviewer proposed. Step 2's rows 5 and 6 read that assigned value wherever they say "the chosen path's depth tag", so a composed path the orchestrator judges `re-architect` gates at row 5 exactly as an enumerated one would.

### "What highest-quality means" closing clause

> **This definition is what a composed path is composed to**: a path the orchestrator writes because no enumerated one met it, so a composed path never satisfies row 4 by construction — row 4 fires on a chosen path that is *narrower* than the complete fix, and composing is the alternative to picking one that is.

### Part (c) question-text clause

> **When the Step-1 pick was a composed path**, that context line also describes it — its letter, the depth Step 1 assigned it, and what it does — because a composed path appears nowhere in the reviewer's emission the finding-verbatim text reproduces, so a user reading only that text would be answering about a path they cannot see. This is the same rule part (d)'s composed-path clause carries at its own gate.

### Part (d) fix-path bullet clause

> **When the Step-1 pick was a composed path** routed here by row 5, present that composed path as a choice of its own alongside the reviewer's — under the next unused letter, described in full — and mark **it** `(Recommended)` per the rule above; a gate that offers only the paths the orchestrator already rejected as incomplete is not offering the pick it is asking the user to ratify.

### `**Accepted compromises**` render step

Three words appended to the appends-an-entry condition: `, or was composed`.

### Trigger C (fix-issue inline form; execute carried the same as a labelled bullet under a "Field substitution" lead)

> **The carve-out is evaluated on the reviewer's enumeration alone, and never applies when the Step-1 pick was composed:** composing is itself a pick between what the reviewer enumerated and a path no reviewer proposed, so a composed entry always appends however few — or however shallow — the enumerated paths were.

> **Field substitution for a composed path.** When the Step-1 pick was **composed** rather than picked from the reviewer's enumeration (part (a) Step 1's "the enumeration is the menu, not a ceiling" branch), keep the `Decision` prefix byte-identical — `Orchestrator picked path ` … ` — highest-quality`, so Section 8's PHASE 3 match still hits — and write the **next unused letter** after the reviewer's own in the `(x)` slot (`(c)` when the reviewer enumerated `(a)` and `(b)`), listing the reviewer's enumerated paths unchanged in the paths field with the composed path appended under its new letter, **carrying the depth Step 1 assigned it** in the same `[depth:<...>]` shape the reviewer's own lines use, so Section 8's PHASE 3 axis (i) has a depth to challenge rather than a blank where every other entry has one. **Mark that line inline as orchestrator-composed** — append `(orchestrator-composed — not enumerated by the reviewer)` after its description — so the field stays a faithful record of what the reviewer actually surfaced: PHASE 4 reads it as the reviewer's menu when judging under-enumeration, and an unmarked composed line makes the reviewer look *less* under-enumerating in precisely the case where the composition is the evidence that it was. The marker lets PHASE 4 count the reviewer's own paths without reading the `Rationale`. Then state in `Rationale` that **the reviewer did not enumerate this path** and **what the enumerated paths lacked** — which part of the stated defect each of them left unfixed — since that is the whole record of a path no reviewer proposed.

## Related

- b.nn8 (landed): the routing rewrite this design extended; its 2026-09-08 amendment records the strip.
- b.q3f (open): the `[introduces-mechanism]` definition and the Analyst's blast-radius sweep; a composed path's lifecycle is the kind of sweep that Issue formalizes.
- b.262 (open): tracker vocabulary; the inline marker above is a tracker-field convention that Issue would inherit.

