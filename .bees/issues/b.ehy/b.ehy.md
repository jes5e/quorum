---
id: b.ehy
type: bee
title: 'bees-breakdown-epic next-steps menu: add per-option rationale and detect foundation-Epic chains'
status: open
created_at: '2026-05-03T13:17:08.032566'
schema_version: '0.1'
egg: null
guid: ehy3itaec5c2vi1bce5kzr5aw549uuk8
---

## Description

The post-completion next-steps menu in `bees-breakdown-epic` (Step 6, "Offer Next Steps") describes *what* each option does but not *when to pick which* or *what trade-off it implies*. The "Recommended" badge is unconditionally pinned to "execute the whole Bee in a fresh session", even when the just-broken-down Epic is foundational and the remaining drafted sibling Epics depend on it — i.e. the case where breaking those siblings down before the foundation Epic's implementation lands is the rework-prone path.

## Current behavior

Step 6 lists five options:

1. Fresh session: execute whole Bee (Recommended)
2. Fresh session: start at a specific Epic
3. Fresh session: break down next Epic
4. Review first
5. Done for now

Each option's description states only the action ("Walks every Epic in dependency order, starting with t1.5tm.27" / "5 more Epics in b.5tm remain drafted ... Run /bees-breakdown-epic in a new session for the next foundational one"). There is no per-option reason, no comparison of trade-offs, and no awareness of whether the just-broken-down Epic is foundational to drafted siblings.

Concrete observation that prompted this issue: in b.5tm, after `t1.5tm.27` (subagent definitions and infrastructure) was broken down, the menu surfaced "execute whole Bee" as Recommended. But `.8s` / `.fk` / `.o1` rewrite skills to *consume* what `.27` produces — breaking those Epics down before `.27`'s implementation lands risks stale Tasks if the subagent contract shifts during implementation. The skill steered the user toward the higher-rework default with no rationale visible to the user.

## Expected behavior

The menu should reason about Epic-chain shape and embed per-option rationale:

1. **Detect foundation Epics before composing the menu.** Before calling `AskUserQuestion`, query the just-broken-down Epic's drafted siblings and check whether any list this Epic in their `up_dependencies`:

   ```
   bees execute-freeform-query --query-yaml 'stages:
     - [parent=<bee-id>, type=t1, status=drafted]
   report: [title, up_dependencies]'
   ```

   Filter the result to siblings whose `up_dependencies` includes the just-broken-down Epic ID.

2. **Branch the recommendation:**
   - If one or more drafted siblings depend on this Epic, recommend "execute this Epic first, defer downstream breakdown" with a one-line reason (e.g. "drafted siblings <ids> depend on this Epic's output; breaking them down before this Epic's implementation lands risks rework if the contract shifts during execution").
   - If no drafted siblings depend on this Epic (or no drafted siblings exist), keep the current "execute whole Bee" / "break down next Epic" recommendation.

3. **Embed per-option rationale.** Each option's description should carry a short "why / when to pick this" clause in addition to the what. Example shape:
   - "Execute whole Bee — best when remaining drafted Epics are independent or you're confident the spec is stable. Walks every Epic in dependency order."
   - "Break down next Epic now — best when remaining Epics are independent or unblocked. Avoids context-switching back to breakdown later."
   - "Defer downstream breakdown until this Epic is done — best when drafted siblings consume what this Epic produces, so per-Task contracts aren't locked in yet."

## Impact

Users following the current skill get steered toward bulk breakdown even in foundation-then-rewrite Epic chains where it produces the most rework. The menu hides the heuristics the skill should know, forcing the user to recognize the chain shape themselves and override the recommendation. Users who don't notice will spend agent cycles writing Subtasks that go stale when the foundation Epic's implementation reshapes the contract.

## Suggested fix

Edit `skills/bees-breakdown-epic/SKILL.md` Step 6 ("Offer Next Steps", currently lines ~339–349):

1. Insert a pre-menu step that queries drafted siblings of the just-broken-down Epic and identifies which (if any) list it in `up_dependencies`. Reuse the freeform-query recipe pattern already used in Step 1.
2. Add conditional logic that shifts the Recommended badge:
   - **Foundation case** (drafted siblings depend on this Epic): recommend "execute this Epic first; defer downstream breakdown" and include the dependent sibling IDs in the rationale.
   - **Independent case** (no dependent drafted siblings): keep current behavior.
3. Append a short "why" clause to each option's description so the user can compare trade-offs without external context.
4. Keep the existing fresh-session-vs-same-session preamble — it's still correct and orthogonal to the rationale gap.

Key files:

- `skills/bees-breakdown-epic/SKILL.md` (Step 6 prose)

Acceptance criteria:

- After breaking down a foundation Epic with drafted dependent siblings, the menu's Recommended option is "execute this Epic first / defer downstream breakdown" and names the dependent siblings.
- After breaking down an Epic with no drafted dependent siblings, the menu's Recommended option is unchanged from current behavior.
- Every option in the menu carries a one-line rationale ("best when …") in addition to the action description.
- Same-session vs fresh-session guidance is preserved.

