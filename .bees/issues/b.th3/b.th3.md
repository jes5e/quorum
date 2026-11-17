---
id: b.th3
type: bee
title: Execute pastes the approved directive the Engineer already has in its bodies file; a stale writers sentence; no reader for the Doc Writer's declined requests
parent: null
reference_materials: null
created_at: '2026-11-17T11:34:31.989442'
status: done
schema_version: '0.1'
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

## Closed (2026-11-17)

Merged by fast-forward from `36b640f` to `b801bf4`, with the operator's go: "go" at Checkpoint 1, "A" on the post-completion carrier, then "merge".

**Commits:**
- `5ebbafc`: the draft;
- `6ada892`, `679245e` and `b801bf4`: cold rounds 1–3.

The work was Worker 1's. Its checkpoints are `~/.quorum-overseer/bth3-checkpoint-1.md` through `-3.md`. Full test passes on `main` (620), run by the overseer, who also read the full diff.

**Net shipped: −59 words** (execute −30, engineer −18, pm +10, analyst −21).

### What landed

- **Execute stops pasting the directive.** `## Authoritative design directive` and `## Design context` no longer go to the Engineer, nor the directive block to the PM. After an Approve, the Task body carries the revision (Section 6): implementers read it in their bodies file, and the PM in the Task.
- **The bodies file is rewritten** before an implementer's first resume after an Approve.
- **At a `postcomp-<n>` scope, which has no ticket,** the dispatch carries the revision under `## Design revision (Analyst)`. That's the operator's option (A), which keeps today's behavior.
- **`agents/engineer.md` and `agents/pm.md`** treat that heading as the directive in execute, and it wins over conflicting ticket text. `## Design revision (Analyst)` is pinned as a contract surface.
- **Stale sentences cut:** execute's "Writers receive … only", and two of the same class in `agents/analyst.md`.
- **Execute's Task summary** gains `**Declined doc requests**`. This closes b.msx item 2.
- **b.msx item 1** (operator steps from any role) was not earned: once, loud, and handled correctly without a rule.

### Rollout

The role files change, and subagent definitions load at session start. So the order is: sync, then reload the agents in every session (`/agents` or a restart), then each session re-reads execute and the two role files. The prompt is at `~/.quorum-overseer/paste-live-edit-b-th3-sync.md`.

### Watch

- The next fresh Engineer dispatch after an Approve costs a few points; it was 9 before this change.
- The Engineer and PM act on the Task body's revision.
- No orchestrator strips the revision from writers.
- A declined doc request shows up in a Task summary.
