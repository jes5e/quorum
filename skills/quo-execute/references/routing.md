# Routing reference — definitions, shims, and rationale for `### Orchestrator discipline: routing review findings`

This file is read on demand by `/quo-execute` and `/quo-fix-issue`. It carries the definitions, edge-case shims, and rationale behind the routing table those skills keep in their bodies. Nothing here fires a gate; every gate, its question text, and its choice labels live in the invoking skill's body. Read this file before routing a finding when the routing section is no longer in view, and never route from a summary of it.

## Severity levels

- Severity is consequence, orthogonal to depth. Apply the three tests in order; the first match wins.
- `blocker` — what is there is wrong: a false statement, a failing or broken behavior, a violated contract. Test: someone acting on the current state is misled or fails.
- `suggestion` — true and working as far as it goes, but a reader or the code will go wrong in a case it does not cover. Test: the fix changes what the text asserts or what the code does.
- `nit` — true and complete; the fix makes it better. Test: the fix changes neither what is asserted nor what happens. Behavior-preserving refactors and wording are nits, at any depth.
- The review skills carry the same three tests with worked examples. The orchestrator reads the tags as given and never re-grades a finding; what it judges is the kind of the fix, below.

## Kinds of change

- Every implementer return names the kinds its change touched: `code` — any source change other than comments, including a behavior-preserving refactor; `tests` — a change to what a test asserts, sets up, or covers; `contract-text` — text a client or operator relies on: API and on-the-wire protocol comments, README and getting-started docs, runbooks, changelog entries, architecture statements; `comments` — internal comments and docstrings, and any text in a test file that changes no assertion, setup, or coverage (an assertion message, a test docstring, a module header). The kind keys on what the change alters, never on the file it lives in.
- The kind decides whether a further reviewer round follows (**Severity bounds the loop**): `code` and `tests` earn a cold confirming pass; `contract-text` earns one read, at most one per lane; `comments` earn none and are read by the post-completion sweep.
- The orchestrator confirms the line is plausible against the files the return lists — adding a kind a listed file plainly requires, never removing one, and treating a missing or unreadable report as `code` — so an unreported change gets more review, not less. A comment edit inside a source file cannot be told from a code edit by its path; the implementer's report is the guard there, and the sweep the backstop.

## What "highest-quality" means

- The pick is the smallest enumerated path that fully fixes the stated defect as the finding describes it.
- A deeper path is taken only when every shallower one leaves that defect partly unfixed; that is row 4's test, applied to the pick.
- A deeper path that changes code the stated defect does not touch — recurrence prevention, centralizing, restructuring — is not a fuller fix of the defect; it is recorded as a `defer-to-new-Issue` refinement carrying the reviewer's sketch, never picked in-run. A `[preferred]` deeper path that covers, in the same artifact, a class of sites the finding names is the complete fix of that defect, not recurrence prevention.
- Internal consistency across every surface that states the invariant still counts: a path that fixes the defect in one place and leaves a sibling surface asserting the old behavior is partial.
- Effort is a legitimate tiebreaker between paths that both fully fix the defect.
- "Adds a mechanism" is a reason to route to gate (c), not a reason to build.
- For a docs- or prose-only change set, "fully fixes" means every surface that states the invariant states it consistently.

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
- When the reviewer's `[preferred]` path is shallower than the pick, and the pick is deeper only because the shallower path leaves the defect partly unfixed, say so in the Recommended choice's description.
- On a row-1 entry no Step-1 pick was possible, so no path is marked Recommended.
- When a `blocker`'s Defer-with-narrowing branch is open at gate (d), `Defer to follow-up Issue` takes the marker and every other choice is left unmarked, so exactly one choice carries it.
- Each per-path choice's description includes that path's depth tag, for example `re-architect` or `refactor-locally`.
- Zero-path fire (`/quo-execute` only): when the reviewer enumerated no fix path, the user's prose direction is dispatched per the dispatch shape as the fix; it is not an ungated route, so Trigger C writes nothing; when the user gives neither prose nor `Cancel`, re-fire the gate rather than inventing a dispatch.

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
- The one elision is a final pass that ships only text: the code-review rung is the round **Severity bounds the loop** suppresses, so the affected writer follows that Engineer directly.
- A finding whose chosen fix path changes no source file carries no ordering constraint; re-dispatch that single writer lane alone.
- Part (g) governs the review-finding re-dispatch path only; in `/quo-execute` the forward per-Subtask fan-out stays concurrent by design.

## Rationale index

- **Row order.** Rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) regardless of depth tag; row 1 comes first so parts (e) and (f) stay reachable.
- **Why `Defer` is the default on the mechanism row.** A mechanism the ticket never asked for has its own lifecycle to design; building it inside this unit turns one finding into several rounds.
- **Why gate (c) offers no `Cancel` to a `suggestion` or `nit`.** Scope-bounding is a per-finding decision and a `Cancel` there would be ambiguous; the user retains `Ctrl-C` for run-level abort.
- **Why accepting a blocker is unreachable.** Accepting a blocker ships the blocker.
- **Why the deferral and its narrowing are one decision.** An entry recording only the deferral cannot distinguish a soft-fixed finding from an unfixed one.
- **Why `Severity bounds the loop` re-reviews by kind and not by tag.** A cold pass over a code or test change can catch a fix that broke something adjacent; a cold pass over a comment fix can only re-read a sentence, and the post-completion review reads every sentence once at the end. The first full-run cost ledger showed five consecutive full-diff reviewer rounds confirming one-line comment fixes, and a sweep that found nothing wrong with the one such fix applied unreviewed. Client-facing text gets one read because a wrong sentence there misleads a user; internal comments get the sweep because the next engineer fixes them on their own pass.
- **Why, in a skill with a design authority, a contradicting finding goes there first.** A reviewer finding that contradicts the approved design or a prior clean pass is either a real gap in the design or a false premise; dispatching an implementer settles neither, and on a false premise it starts a cascade of fixes to a bug that does not exist. One design-side read answers it. A skill with no design authority to consult routes the finding normally.
- **Why two consecutive earned rounds escalate, and only on the code lane.** Each earned round means the previous fix left an outstanding code or test finding against it; two in a row on the code lane means the implementer is patching without the rule that would make the fix right, and the design authority supplies that rule. On a test or docs lane the same pattern is a coverage or accuracy gap, which a design read cannot close and an enumerated pass can; sending a test lane's chain to an `xhigh` Analyst spends a design dispatch on a writer's problem, which the first validation run of this rule nearly did for a two-word assertion-message fix.
- **Why the exit decision is written before it is acted on.** The `## Rounds` row is the only durable record of which lanes closed on what, for the summary and the audit trail. Writing it before the re-dispatch or the final pass borrows the manifest-write-then-act shape the gates use, but the row carries decisions and counts, never the findings. A compaction between the decision and the action therefore costs the pass itself: the resumed orchestrator finds no clean return to stop on, dispatches a fresh cold pass, and that round's decision rewrites the row.
- **Why "Follow the trailer literally".** The review skills' routing trailer is the authoritative prescription; the surrounding prose is reference context, not a rule to recall from memory.
- **Why the Engineer's return with `## Design question` is not a completion.** The Engineer stops rather than invent an unenumerated mechanism, so the diff on disk is partial by construction.
- **Prose-adherence fragility.** These gates inherit a prose-adherence fragility that the manifest-write-then-ask contract narrows but does not close; it is an execution-time risk, not something this text fixes.
