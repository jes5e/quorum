---
id: b.39j
type: bee
title: Prune the quo-execute and quo-fix-issue orchestrators by evidence, keeping every contract, state carrier and guard
status: open
created_at: '2026-11-10T13:31:16.138315'
schema_version: '0.1'
reference_materials: null
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

