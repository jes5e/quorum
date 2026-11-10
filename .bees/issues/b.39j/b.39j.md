---
id: b.39j
type: bee
title: Prune the quo-execute and quo-fix-issue orchestrators by evidence, keeping every contract, state carrier and guard
parent: null
reference_materials: null
created_at: '2026-11-10T13:31:16.138315'
status: done
schema_version: '0.1'
guid: 39j6gi781gfd6mo2f3dbbde6dhfb5cc5
---

## Description

Prune `/quo-execute` and `/quo-fix-issue` (about 12,200 and 12,800 words) and their shipped `references/` files by evidence, as b.tdq and b.4wd did for the three review skills. The operator agreed on 2026-11-10 ("go for it if you think it's safe and the right thing to do"). The method is in the memory `feedback_prune_by_evidence`, and in the closing notes of b.tdq and b.4wd.

The orchestrators are higher-stakes than the reviews: they carry the run's contracts, state and gates. So this batch keeps everything those protect, and cuts only text with evidence that it does no work.

### What counts as evidence here

Orchestrator rules rarely produce "findings". Their evidence is in what real runs did. These are in `~/.quorum-scratch`:
- the run-state manifests (`run-state-quo-*`) and ledgers (`ledger-*`);
- the gate files (`gate-*`);
- the compromise trackers (`compromises-*`);
- the Analyst proposals;
- live_edit's diagnosis reports (`diag-*`, `rootcause-*`, `audit-*`).

This repo's tickets and commits also record which rules validation runs exercised or improvised around. Use `docs/inventory/INVENTORY.md` to map each rule to where it lives.

### Classify each piece of text

- **(a) Protected; keep word for word.** These are CLAUDE.md's kinds 1–4:
  - contracts: manifest fields and headings, gate labels, return lines, ticket shapes;
  - state that must survive a compaction, including the post-compaction rule;
  - structural guards: the manifest-fronted gates and the context guard;
  - operator policy;
  - and anything pinned by `tests/test_orchestrator_structure.py` (the Tier-1/Tier-2 mirrors, `SHARED_ANCHORS`, `CONTRACT_SURFACES`, the manifest lead statements).
- **(b) A kind-5 rule.** Keep it if runs show it firing or its case arising. Cut it when the case arose and was handled without it, or its reader or failure mode is gone. A rule that never had a chance to fire is a candidate for the operator, with its reason.
- **(c) Rationale in a body.** A reason the agent doesn't need in order to act moves to `references/rationale.md` or goes, if it's already there.
- **(d) Procedure or recipe.** Text the agent works out for itself, or a spelled-out external-CLI invocation whose exact form isn't the point, is cut to its goal.
- **(e) Duplicates.** The same rule stated in the body and in a reference gets one home.

### Known candidates

- The engineer review's never-fired sweep rules: the missing-list rule and the explicitly-empty-list rule (b.4wd's E27 and E30), wired through both bodies' dispatch tables, `agents/code-reviewer.md` and `agents/engineer.md`.
- Anything b.4wd noted as stale in the bodies.

### Constraints

- **Mirrors:** both bodies change in step wherever the mirror tests pin them.
- **Line budget:** the cap holds, and §§1–5 stay inside the first 150 lines.
- **Review:** the cold review embeds REWRITE-BRIEF §5/§6 and CLAUDE.md's review criteria.
- **Scope:** deleting a routing, gate or dispatch rule is a behavior change. It needs evidence that its reader is gone, or the operator's approval as a separate item.

## Process

One hand-edit batch:
1. **Checkpoint 1:** the evidence table and the cut list, with no edits. The operator approves the cuts.
2. **The draft.**
3. **One cold review under the exit rule.** It replays a real saved run's manifest through the pruned text: does each recorded step still have the text that drove it?

Live_edit picks the change up at its next rebuild. The next real run is the validation.

## Closed (2026-11-10)

Merged by fast-forward to `53f0e64`:
- `51da68c`: the prune (C1–C14, D1–D3, O3, W1);
- `2b177cf`: "Write the manifest" where C4 left a bare "it";
- `df833ee`: cold round 1, with no behavior findings (F1 restored fix's bees orientation, +18; F2 and F4 applied; F3 declined: the reviewer's own trace resolves it, and the branch has 0 fires);
- `966cd6a`: dropped the ticket reference from `docs/sdd.md:611`;
- `53f0e64`: F5, three more restatements the review found, with the operator's go.

The lane closed under the exit rule. The work was Worker 1's, in a fresh session. Its checkpoints are `~/.quorum-overseer/b39j-checkpoint-1.md` through `-3.md`, and its tallies are in `~/.quorum-overseer/b39j-evidence/`. Full test passes (601), run by the overseer, who also read the full diff.

**Net shipped: −1,199 words.**

| File | Change |
|---|---|
| execute body | −122 |
| fix-issue body | −380 |
| `routing.md` | −436 |
| `compromise-tracker.md` | −171 |
| `rationale.md` | −42 |
| `context-guard.md` | −29 |
| `post-completion-prompt.md` | −15 |
| `url-resolution.md` | −4 |

### Evidence

A fixed catalog of 38 rules was tallied against:
- 168 fix-issue manifests and 165 ledgers;
- 14 execute runs;
- 953 gate files;
- 166 compromise trackers (1,570 entries);
- 343 Analyst files;
- the diagnosis reports;
- 18 tickets' validation notes.

The bodies are mostly contracts, state and gates, and the runs exercise nearly all of them. The cuts are duplicates, rationale whose reader is gone, ticket-CLI recipes, one never-used re-derivation table, and one instruction that misfired.

### Operator decisions

- **O1** (route a missing-list finding as a compaction artifact): **kept.** The operator keeps compactions rare, so zero fires is not evidence the rule is idle.
- **O3** (the post-completion reviewer no longer flags a missing tracker): approved. Its 7 flags on record were all false.
- **D3** (re-derivation shape compressed): approved.
- **In-step cuts inside Tier-1 §7** (C6, C7): approved by the overseer under the operator's delegation. The byte-identity test still binds.

### Kept

- **The engineer review's missing-list and empty-list rules (E27, E30):** two real catches of an orchestrator relay gap.
- **No-chance rules:** the text class, the unexplained-movement gate, GitHub close and URL tokens, the effort gate, and deferral-hygiene Step 0. Their reasons are in Checkpoint 1.

### Validation

The cold round replayed live_edit b.ug2 (fix-issue, 15 steps) and b.f9p Epic 2 (execute, 12 steps). It also traced a blocker through gate (c) and a lost-proposal resume.

### Noted for later triage

- **Ten gaps the runs worked around**, from Checkpoint 1:
  - mid-run `origin/main` merges;
  - hand-off state in RESUME blocks;
  - `hive_commit.py` staging `identity.json`;
  - the movement rung's missing movers;
  - no operator-action rung in fix;
  - the orchestrator writing content itself;
  - undefined row kinds and scopes;
  - unnoticed 675k-bound crossings;
  - deferral hygiene's de facto fourth answer;
  - rubber-stamp dispositions.
- **`agents/pm.md:237`** may share O3's false missing-tracker flag.
- **C8:** fix's "write a needed fact into a carrier" half has no home.
- **Execute's re-derivation shape** doesn't carry a lost `## Design question`.
