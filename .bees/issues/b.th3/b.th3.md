---
id: b.th3
type: bee
title: Execute pastes the approved directive the Engineer already has in its bodies file; a stale writers sentence; no reader for the Doc Writer's declined requests
status: open
created_at: '2026-11-17T11:34:31.989442'
schema_version: '0.1'
reference_materials: null
guid: th38kgkaxmrd5pezx2ne5iazg2mgf4ap
---

## Description

Since b.rgw, an approved Analyst revision is recorded in the ticket's body (`## Design revision (Analyst)`), and since b.mfz each implementer reads the Task body from its bodies file. `/quo-execute` §5 still describes the older world in two places, and one return line still has no reader:

1. **The directive arrives twice.** An Engineer after an Approve gets the revision inside its bodies file (the Task body) and again pasted under `## Authoritative design directive (from the Analyst gate)`, with `## Design context`. That paste is now the largest one an orchestrator still makes per dispatch: 10–35 KB on Epic 4's Engineers (b.mfz Checkpoint 3, second-order note 1).
2. **A stale sentence.** §5 says "Writers receive the revision's `## Blast radius` and `## Design decisions for writers` only, never the rest of it." That has been false since the revision moved into the Task body, which writers receive. live_edit improvised around it by stripping the section out of writers' prompts (b.mfz Checkpoint 3, second-order note 2).
3. **b.msx item 2.** `agents/doc-writer.md:39` tells the Doc Writer to name each request it declined, and why. `/quo-fix-issue` shows those in `**Doc Sync**`; `/quo-execute` has no reader. This is a return line with no reader, a gap between two agents. It was agreed to ride the next execute edit.

### Goal

- **One home for what each role receives of an approved revision.** In execute, the Task body (in the bodies file) carries the revision. Keep a pasted block only where a role keys on it and doesn't otherwise get the text. Say why for each role.
- **The contracts other agents key on:**
  - `agents/engineer.md` and `agents/pm.md` key on `## Authoritative design directive (from the Analyst gate)`, pinned in `CONTRACT_SURFACES` for both orchestrators.
  - `/quo-fix-issue` records no revision in the Issue body, so its directive block stays.

  If execute stops pasting the directive, every reader must still find the approved design and know it wins over the Subtask text. That means the Engineer, the PM, the sweep rule at `engineer.md`:65, and the routing table's approved-design cell. Fix the class in one pass.
- **Cut, don't append.** The stale writers sentence goes or becomes true. The Doc Writer's declined requests get one reader in execute's summary, mirroring fix-issue's sentence.
- **b.msx item 1** (Operator-action from any implementer) is out of scope unless the three questions earn it. Its only evidence is a case handled correctly with no rule.

### Constraints

- Orchestrator hand edit: inventory-anchored, with cold reviews under the exit rule. Changes to shared Tier 1 text stay byte-identical across both bodies.
- No change to the bodies file or the helper unless the design needs it.
- Watch the word count. The likely net is negative.

