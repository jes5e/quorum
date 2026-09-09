# Routing reference — definitions, shims, and rationale for `### Orchestrator discipline: routing review findings`

This file is read on demand by `/quo-execute` and `/quo-fix-issue`. It carries the definitions, edge-case shims, and rationale behind the routing table those skills keep in their bodies. Nothing here fires a gate; every gate, its question text, and its choice labels live in the invoking skill's body. Read this file before routing a finding when the routing section is no longer in view, and never route from a summary of it.

## What "highest-quality" means

- The highest-quality fix path is the smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names.
- Internal consistency across surfaces counts, not merely local correctness.
- Total-system complexity counts against a path.
- Effort is never the tiebreaker between paths of equal completeness.
- "Adds a mechanism" is a reason to route to gate (c), not a reason to build.
- For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently".

## What "introduces a mechanism" means

- A path introduces a mechanism when it adds machinery, per the mechanism definition in `agents/analyst.md`, that the approved design for this unit did not enumerate.
- The approved design is whatever the invoking skill's body names as its approved-design source; the two skills differ here and the body's divergence table states each.
- The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2: a tagged path routes to gate (c) with no further judgment.
- Orchestrator-side detection is the fallback, used only when no tag is present: read the fix path's own description against that definition and route it the same way.

## (a) Pick, then route — the split

- Whether a gate fires is decided deterministically by the table; which path is picked when no gate fires is the orchestrator's own judgment.
- The pick precedes the route because rows 2–5 test properties of the chosen path, not of the finding.

## Under-enumerated findings

- The pick at Step 1 is always one of the paths the reviewer enumerated.
- When no enumerated path is the smallest internally-consistent complete change, pick the most complete of them anyway.
- Step 2 then routes that pick: rows 2, 3, and 4 send it to gate (c), where `Fix properly now` dispatches the complete fix.
- The exception is a finding whose depth tag is absent or malformed; row 1 sends it to gate (d), which has no `Fix properly now`, so the user picks among the paths as emitted.
- Either way the incomplete menu becomes visible in session: a gate fires where it otherwise would not have, and the user sees the menu it fired on.
- A durable record of an incomplete menu reaches the post-completion review only via Trigger A (`Defer to follow-up Issue`) or Trigger B (`Accept the limitation`); `Fix properly now` writes none.
- The orchestrator does not absorb an enumeration gap by writing a fix path of its own.

## (b) ANTI-PATTERN — do not write this:

- The orchestrator MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent.
- Forbidden phrasings, and any close paraphrase: `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`.
- Inlining a scope-bound silently narrows the fix without the user ever seeing the decision.
- When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through gate (c) instead.
- The prohibition targets narrowing language, not path selection: a dispatch prompt that names the chosen path and carries its fix in full is not a violation.
- Instructing the implementer to do less than the chosen path is a violation.
- A path narrower than the smallest internally-consistent complete fix is never written into a prompt at all; it routes to gate (c) via row 4.
- Downstream, the part-(b) scope-bound condition is read as row 4, so every rule that enumerates "row 2, 3, or 4" covers it without naming it.

## Gate (c) — the blocker Defer-with-narrowing branch in full

- `Defer to follow-up Issue` is added to a `blocker`'s choice set only when both hold: (i) the fix path the finding needs introduces a mechanism, and (ii) that mechanism serves a case outside this unit's stated defect.
- Condition (ii) means the change narrowed to the stated defect is still complete and the blocker no longer describes anything that ships.
- A narrowing may never reduce coverage of the stated defect, at gate (c) and at gate (d) alike.
- A `blocker` that cannot be made inapplicable to what ships without leaving the stated defect partly unfixed is in scope; it takes one of the base pair, never `Defer`.
- The blocker deferral is paired with the narrowing, never shipped alone.
- File the follow-up Issue first, carrying the reviewer's sketched design verbatim; dispatch the narrowing only once `/quo-file-issue` has returned an Issue ID.
- Dispatch the narrowing directly, not by re-entering Step 2 with it, because Step 2 would match row 4 and route it straight back to this gate.
- The direct-dispatch terminality is one rule with the soft-fix rule: it applies to a blocker's narrowing and to a non-blocker's soft fix alike.
- When the Defer-with-narrowing branch is open, mark the choice `(Recommended)` even on a `blocker`.
- When the coverage guard withholds `Defer` because the narrowing would leave the stated defect partly unfixed, there is no choice to mark `(Recommended)`, even on a row-2 fire.
- The blocker Defer branch applies whichever row fired the gate — 2, 3, or 4 — because condition (i) tests the fix path the finding needs, not the chosen path.
- A `suggestion` or `nit` keeps the narrower rule: its Defer default is row-2 only.
- The gate fires for a `blocker` like any other finding; the base pair is a real decision, three choices when the Defer-with-narrowing branch is open.
- The `Defer to follow-up Issue` bullet's closing clauses do not apply to a blocker: its no-fix-this-round branch cannot arise, its never-invent-a-narrowing prohibition concerns a non-blocker's empty soft-fix slot, and its soft-fix identification does not apply because what ships is the narrowing.

## Gate (c) — the soft fix

- `Defer to follow-up Issue` on a `suggestion` or `nit` files the follow-up Issue and proceeds with the soft fix this round.
- The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside.
- Dispatch the soft fix directly, not by re-entering Step 2, because a remaining path is narrower than the deferred one and row 4 would loop it back.
- When the deferred path was the only one enumerated, ship no fix for this finding this round; the end state matches `Accept the limitation` with the follow-up Issue filed.
- Never invent a narrowing to fill the soft-fix slot; part (b) forbids it.
- The follow-up Issue MUST carry the reviewer's sketched design verbatim so nothing about the proposed mechanism is lost by deferring.

## Gate (d) — the `(Recommended)` marker

- The `(Recommended)` marker goes on the path the orchestrator chose at Step 1; gate (d) asks the user to ratify or override a pick already made.
- When `[preferred]` marks a narrowing and a fuller path is the smallest internally-consistent complete change, mark the fuller path Recommended and state in its description that the reviewer preferred the other path.
- On a row-1 entry no Step-1 pick was possible, so no path is marked Recommended.
- When a `blocker`'s Defer-with-narrowing branch is open at gate (d), `Defer to follow-up Issue` takes the marker and every other choice is left unmarked, so exactly one choice carries it.
- Each per-path choice's description includes that path's depth tag, for example `re-architect` or `refactor-locally`.

## (e) Backwards-compatibility shim.

- A finding emitted without a depth tag — a legacy reviewer emission, or a hand-authored finding from a future call site — MUST be treated as `re-architect` depth and routed to gate (d).
- When the orchestrator cannot determine a finding's depth, it surfaces the decision to the user rather than dispatching its own pick ungated under row 6.
- A PM emission that `agents/pm.md`'s tracker-check bullet designates a report note, not a finding, is exempt from this shim and from the malformed-tag bullet below; that bullet defines the shape.

## (f) Edge-case handling.

- **Malformed tags.** When a severity tag is not exactly `blocker` / `suggestion` / `nit`, or a depth tag is not exactly `trivial-tweak` / `refactor-locally` / `re-architect`, treat the finding as `re-architect` depth per part (e) AND surface the parse failure to the user so the reviewer emission can be corrected.
- **Routing ambiguity.** If the routing table returns more than one decision, default to gate (d) and surface the ambiguity to the user.
- **`/quo-file-issue` failure at the Defer gate.** When the user picks `Defer to follow-up Issue` at either gate but the inline filing fails or the user cancels inside it, MUST NOT silently ship the soft fix or no fix.
- On a filing failure, surface it and re-prompt with the same gate's choices, so the user can re-attempt the defer, pick `Accept the limitation` where it exists (never on a `blocker`), pick a specific fix path explicitly, or cancel where that gate offers `Cancel`.
- A `blocker` can reach the filing-failure bullet via the Defer-with-narrowing branch; do not ship the narrowing when the filing failed, because the narrowing is legitimate only paired with the follow-up Issue that carries the deferred design.

## (g) Re-dispatch ordering — the rationale

- Dispatching the Engineer and a writer in the same round hands the writer a diff the pending code review is about to rewrite, forcing the writer's work to be redone.
- The one elision is the final `trivial-tweak` nit pass: the code-review rung is the round **Severity bounds the loop** suppresses, so the affected writer follows that Engineer directly.
- A finding whose chosen fix path changes no source file carries no ordering constraint; re-dispatch that single writer lane alone.
- Part (g) governs the review-finding re-dispatch path only; in `/quo-execute` the forward per-Subtask fan-out stays concurrent by design.

## Rationale index

- **Row order.** Rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of depth tag; row 1 comes first so parts (e) and (f) stay reachable.
- **Why `Defer` is the default on the mechanism row.** A mechanism the ticket never asked for has its own lifecycle to design; building it inside this unit turns one finding into several rounds.
- **Why gate (c) offers no `Cancel` to a `suggestion` or `nit`.** Scope-bounding is a per-finding decision and a `Cancel` there would be ambiguous; the user retains `Ctrl-C` for run-level abort.
- **Why accepting a blocker is unreachable.** Accepting a blocker ships the blocker.
- **Why the deferral and its narrowing are one decision.** An entry recording only the deferral cannot distinguish a soft-fixed finding from an unfixed one.
- **Why `Severity bounds the loop` gives up nothing.** The cold pass that raised a `trivial-tweak` nit already read the text it corrects, the fix is a `trivial-tweak` by the reviewer's own tag, and the post-completion review reads the whole diff, nit fixes included.
- **Why "Follow the trailer literally".** The review skills' routing trailer is the authoritative prescription; the surrounding prose is reference context, not a rule to recall from memory.
- **Why the Engineer's return with `## Design question` is not a completion.** The Engineer stops rather than invent an unenumerated mechanism, so the diff on disk is partial by construction.
- **Prose-adherence fragility.** These gates inherit a prose-adherence fragility that the manifest-write-then-ask contract narrows but does not close; it is an execution-time risk, not something this text fixes.
