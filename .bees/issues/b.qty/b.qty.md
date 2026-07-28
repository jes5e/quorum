---
id: b.qty
type: bee
title: Escalate reasoning effort on repeated review failure
status: open
created_at: '2026-07-28T20:43:48.249421'
schema_version: '0.1'
reference_materials: null
guid: qtysfivccr99c3m9da7idzs1bhd3pzut
---

## Description

When a Code Reviewer returns findings on the same Subtask twice, re-dispatch the Engineer at a raised reasoning effort (`xhigh`) rather than at its pinned `high`. The premise is that repeated review failure is evidence the task is harder than its role tier assumed, and that the cheapest correction is more reasoning depth on the retry rather than another identical attempt.

Deferred out of **b.ajk** (Pin reasoning effort per role; drop the Sonnet downgrade prompt), which pinned a static per-role effort table but explicitly left dynamic escalation out of scope.

## The blocker that has now been lifted

b.ajk deferred this item on a capability question it could not answer:

> depends on a capability this ticket did NOT verify: whether an effort override can be passed per Agent dispatch, as opposed to pinned in frontmatter. Verify that separately before picking this up.

**That capability is confirmed to exist.** The Agent tool's input schema in the installed Claude Code CLI carries its own `effort` parameter, described verbatim as:

> overrides the reasoning effort for this agent call ('low' | 'medium' | 'high' | 'xhigh' | 'max') — omit to inherit the session effort; use 'low' for cheap mechanical stages and higher tiers only for the hardest verify/judge stages.

So the mechanism for a per-dispatch escalation is available and does not require touching installed agent files. Verified during the b.ajk fix pass by reading the agent-definition and tool-input validators out of the installed CLI binary.

Note that b.ajk deliberately **rejected** per-dispatch overrides as the mechanism for its *static* table — frontmatter is declarative, diffable, single-source across three dispatching skills, and does not put the tier table into orchestrator prose (the most drift-prone surface in the repo). That reasoning does not apply here: escalation is inherently dynamic and per-dispatch, so the override parameter is the right tool for it specifically.

## Open questions this ticket must answer

These are the objections b.ajk raised that are **not** resolved by the capability finding, and they are the real work:

1. **Does it actually help?** The premise is untested. Re-running a failed Subtask at higher effort may fix it, or may produce the same wrong answer more elaborately. There is no eval harness in this repo to measure the difference (itself a known gap).
2. **Retry bookkeeping.** The orchestrator would need per-Subtask state: how many review rounds have run, which role is being escalated, and when to stop. `quo-execute` and `quo-fix-issue` currently hold no such counter, and the reconciliation loop is deliberately event-driven and stateless between ticks.
3. **Where does escalation stop?** `xhigh` after two rounds, then `max` after three? Or a single step? An unbounded ladder interacts badly with the wall-clock argument that set the static tiers at `high` in the first place.
4. **Which role escalates?** The obvious reading is the implementer, but a reviewer that keeps finding the same class of defect may itself be the weaker seat.
5. **Interaction with the reviewer invariant.** b.ajk records: never pin a reviewer below the role it reviews. Escalating an Engineer to `xhigh` transiently puts it at parity with the Code Reviewer that reviews it, which the invariant's spirit arguably prohibits — so either the reviewer escalates in lockstep, or the invariant needs a documented carve-out for transient escalation.

## Scope

`skills/quo-execute/SKILL.md` and `skills/quo-fix-issue/SKILL.md` (the two skills that run review loops). `skills/quo-breakdown-epic/SKILL.md` has no review loop and is out of scope. Any change to the reviewer invariant would also touch `CLAUDE.md` and `docs/sdd.md` `## Model assignment in execution skills`.

## Suggested first step

Do not implement blind. Answer question 1 first — even informally, by escalating manually on a few real review-failure cases and comparing outcomes. If the effect is not visible at that scale, the bookkeeping cost in questions 2-4 is not worth paying.

