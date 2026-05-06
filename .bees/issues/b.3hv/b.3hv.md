---
id: b.3hv
type: bee
title: Drop Teams-era vocabulary from README.md and CONTRIBUTING.md
parent: null
created_at: '2026-05-05T16:16:57.365702'
status: done
schema_version: '0.1'
guid: 3hvd2p4y1r7my2s875s2deeqvscumr74
reference_materials: null
---
## Description

Several lines in `README.md` and `CONTRIBUTING.md` still refer to the workflow's "team", "team members", "team-lead", and "implementation team" — vocabulary inherited from when bees-workflow used Claude Code's experimental Agent Teams feature. The repo has since switched to ephemeral background subagents (custom subagents under `agents/<role>.md`, dispatched via the Agent tool), and these doc lines are now stale.

The README sections that describe the new orchestration model (the workflow paragraph at line 24, the Install section at lines 49–88, and the "After install" subagent-registration note at lines 83–88) are already correct. Only a few specific lines still carry the Teams-era vocabulary.

## Current behavior

`README.md`:

- Line 106 — `/bees-execute` table row: *"Execute a Plan Bee end-to-end — spawn the implementation team, walk every Epic in dependency order, commit per Task, review at Bee close."*
- Line 108 — `/bees-fix-issue` table row: *"Fix one or more issue tickets. Single, list, or `all` modes. Spawns the same kind of team as `bees-execute` but at issue scope."*

`CONTRIBUTING.md`:

- Line 55 (under `## Intentional asymmetries`) — single bullet with three stale references: *"`/bees-breakdown-epic` is the only skill where team members run in `mode: \"plan\"`. Subagents during breakdown are read-only researchers; only the team-lead runs ticket-mutating commands. Other execution skills (`/bees-execute`, `/bees-fix-issue`) let team members create commits, not tickets — different scope of authority."*

## Expected behavior

Doc vocabulary should match the current orchestration model — ephemeral background subagents dispatched via the Agent tool, as described in `CLAUDE.md` `## Model assignment in execution skills` and the role contracts under `agents/<role>.md`.

Specifically:

`README.md`:

- Line 106 — drop "implementation team" in favor of subagent vocabulary.
- Line 108 — drop "the same kind of team" in favor of subagent vocabulary.
- Line 37 (Apiary description, *"async-team-spawning experience of Apiary"*) — **leave alone**. Apiary still uses the Agent Teams feature, so the contrast is accurate as written.

`CONTRIBUTING.md`:

- Line 55 — reword the bullet in subagent vocabulary while preserving the intentional-asymmetry point: in `/bees-breakdown-epic`, dispatched subagents run in `mode: "plan"` as read-only researchers and only the orchestrating skill mutates tickets; in `/bees-execute` and `/bees-fix-issue`, subagents are allowed to commit but still don't create tickets.

## Impact

Documentation correctness only. No runtime impact — the skills themselves no longer reference Teams. Risk is reader confusion: a contributor reading either file today will think the workflow still spawns a Claude Code "team" when it actually dispatches subagents.

## Suggested fix

Doc-only edits to `README.md` and `CONTRIBUTING.md`:

- `README.md:106` — rewrite the `/bees-execute` table cell to describe spawning subagents instead of "the implementation team".
- `README.md:108` — rewrite the `/bees-fix-issue` table cell to describe spawning subagents instead of "the same kind of team".
- `CONTRIBUTING.md:55` — rewrite the bullet to use subagent vocabulary throughout while preserving the intentional-asymmetry framing (read-only `mode: "plan"` for breakdown vs. commit-allowed for execute / fix-issue).

No skill prose, helper scripts, or agent definitions need to change. No update to `docs/prd.md` or `docs/sdd.md` is implied — this is pure doc-vocabulary cleanup, not a behavior or architecture change.
