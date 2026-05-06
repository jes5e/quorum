---
id: b.ehy
type: bee
title: 'bees-breakdown-epic end-of-skill: per-option rationale, foundation-Epic detection,
  and missing commit step'
parent: null
created_at: '2026-05-03T13:17:08.032566'
status: done
schema_version: '0.1'
guid: ehy3itaec5c2vi1bce5kzr5aw549uuk8
reference_materials: null
---
## Description

Two related gaps in `bees-breakdown-epic`'s end-of-skill behavior:

**(A) Step 6 next-steps menu lacks per-option rationale and uses the wrong heuristic for the Recommended badge.** The menu describes *what* each option does but not *when to pick which*. The "Recommended" badge is unconditionally pinned to "execute the whole Bee", even when remaining drafted Epics consume contracts that the just-broken-down Epic's implementation will lock in (foundation-then-rewrites pattern), and breaking those siblings down now risks rework if the contract shifts during execution.

**(B) The skill ends without committing the new ticket files it just created.** When breakdown completes, `.bees/<plans-hive>/` carries new Task and Subtask files, plus the parent Epic's status update. The skill jumps straight to Step 6's next-steps menu without staging or committing them. If the user ends the session at that point — which is the explicitly-recommended fresh-session path for `/bees-execute` — they're left with a pile of uncommitted ticket files that the next session has to discover and reason about.

Both gaps live at the end of the same skill file (`SKILL.md` Steps 5–6) and the fix is one cohesive pass.

## Current behavior

**(A)** Step 6 lists five options with action-only descriptions and an unconditional "Recommended" tag on "Fresh session: execute whole Bee". The skill does not consult the just-broken-down Epic's drafted siblings, does not read those siblings' bodies to assess contract coupling, and does not vary its recommendation based on Epic-chain shape. Concrete observation: after `t1.5tm.27` (subagent definitions and infrastructure) was broken down, the menu pointed at "execute whole Bee" — but `.8s` / `.fk` / `.o1` rewrite skills to *consume* what `.27` produces, so breaking those Epics down before `.27`'s implementation lands risks stale Tasks. The menu hid the heuristic.

**(B)** After `bees create-ticket` runs for every new Task and Subtask and `bees update-ticket --status ready` runs for the Epic and its children, control returns to the skill, which then renders the next-steps menu. There is no `git add` / `git commit` step in `SKILL.md`. The user is implicitly expected to commit before ending the session, but nothing in the skill prose tells them to and the natural reading of "Recommended: open a fresh session" leads them to do exactly the wrong thing.

## Expected behavior

**(A)** The Recommended option should reflect the team-lead's read of design-reshape risk, not just `up_dependencies` presence. A drafted sibling having `up_dependencies: [<this-epic>]` is *only* an ordering constraint at execute-time — it doesn't automatically imply plan-time coupling. The right distinction is whether the upstream Epic's implementation will lock contract details that the drafted sibling's Tasks would otherwise have to guess at:

- **Default behavior** (most cases, including most "drafted siblings are blocked by this Epic" cases): keep going. Recommend either "break down the next Epic" or "execute the whole Bee" — same as if no dependencies existed. Don't surface a confirm-or-defer choice the user can't meaningfully answer.
- **Surface a defer-downstream-breakdown choice only when there's a real trade-off.** Trigger: after Step 5 finishes, the team-lead reads the bodies of any drafted siblings whose `up_dependencies` includes the just-broken-down Epic, and judges whether the upstream Epic's implementation will materially reshape the contract those siblings consume (e.g., upstream defines new infrastructure / API / schema / framework that the siblings explicitly rewrite-to-consume). When that judgment lands "yes, contract is in flux", surface a Recommended option of "execute this Epic first; defer downstream breakdown" with a one-line reason naming the dependent siblings and the contract-reshape concern.
- **Per-option rationale.** Each option in the menu should carry a one-line "best when …" clause in addition to the action description, so the user can compare trade-offs without external context.

**(B)** Before rendering Step 6, the skill should stage and commit the new ticket files it created (Tasks, Subtasks, and the Epic's status-update). Use the same hive-resolution pattern bees-file-issue uses (`bees list-hives` → check whether the Plans hive lives inside the repo → only `git add` if so). Commit message naming the Epic that was broken down. If the Plans hive lives outside the repo, skip the commit and remind the user where the tickets are stored. After the commit, then render Step 6's next-steps menu.

## Impact

**(A)** Users following the current skill get steered toward bulk breakdown even in foundation-then-rewrite Epic chains where it produces the most rework. The skill hides the heuristic the team-lead is uniquely positioned to apply (reading both Epic bodies and judging contract coupling), forcing the user to recognize the chain shape themselves and override the recommendation.

**(B)** The recommended next step is "open a fresh session" — but a fresh session inherits an unstaged, uncommitted pile of ticket files the user didn't know they were responsible for. They get discovered the next time someone runs `git status`, and can collide with unrelated work the user does in between sessions. This silently violates the skill's own "fresh session" recommendation.

## Suggested fix

Edit `skills/bees-breakdown-epic/SKILL.md`:

**For (A) — Step 6 logic**:
1. Before composing the menu, query the just-broken-down Epic's drafted siblings: `bees execute-freeform-query --query-yaml 'stages: [parent=<bee-id>, type=t1, status=drafted]
report: [title, up_dependencies, body]'` (or fetch bodies via `bees show-ticket` for the dependent subset).
2. Filter to siblings whose `up_dependencies` includes the just-broken-down Epic ID.
3. For each such sibling, the team-lead reads the upstream Epic body and the sibling Epic body and judges design-reshape risk. The judgment is the team-lead's call, not a hardcoded rule — treat it the same as other team-lead judgment calls in the skill.
4. Branch the Recommended option:
   - **Reshape-risk case** (any dependent sibling judged to consume an in-flux contract): Recommended is "execute this Epic first; defer downstream breakdown" with a rationale that names the at-risk siblings.
   - **No-reshape-risk case** (default, including dependent siblings whose coupling is just ordering): Recommended is the current "execute whole Bee" / "break down next Epic" — keep going, don't ask.
5. Append a one-line "best when …" rationale to every option's description.
6. Preserve the existing fresh-session-vs-same-session preamble — it's correct and orthogonal.

**For (B) — pre-Step-6 commit**:
1. Add a new step between Step 5 ("Review Epic") and Step 6 ("Offer Next Steps") that stages and commits the new ticket files.
2. Resolve the Plans hive path via `bees list-hives`, check whether it lives inside the current git repo, and only `git add` if so. Mirror the pattern in `bees-file-issue` Step 5 (POSIX bash + Windows PowerShell variants). Don't hardcode `.bees/plans/` — `/bees-setup` lets users put hives outside the repo.
3. Commit message: `Break down <epic-id>: <epic-title>` (or similar). Single literal command, no compound chains, per repo Bash etiquette.
4. If the Plans hive lives outside the repo, skip the commit and surface a one-line note in the next-steps menu so the user knows the tickets are persisted by the bees CLI but not git-tracked.
5. After the commit, then render Step 6's menu.

Key files:

- `skills/bees-breakdown-epic/SKILL.md` (Step 5 / new pre-Step-6 commit step / Step 6 prose)

Acceptance criteria:

- After breaking down an Epic with drafted dependent siblings whose contract is in flux (team-lead judgment), the menu's Recommended option is "execute this Epic first / defer downstream breakdown" and names the at-risk siblings.
- After breaking down an Epic where dependencies are pure ordering (no contract reshape), the menu's Recommended option is unchanged from current behavior — no extra confirm-or-defer prompt.
- Every option in the menu carries a one-line "best when …" rationale.
- Same-session-vs-fresh-session preamble preserved.
- Before the menu renders, new Task/Subtask files and the Epic's status update are staged and committed (when the Plans hive lives in-repo). When the hive lives out-of-repo, the skill surfaces a one-line note and skips the git commands.
- All shell snippets ship as paired POSIX bash + Windows PowerShell blocks, per repo design rule 2.
