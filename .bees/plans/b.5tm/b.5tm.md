---
id: b.5tm
type: bee
title: Ephemeral-Agent Orchestration
parent: null
children:
- t1.5tm.27
- t1.5tm.8s
- t1.5tm.fk
- t1.5tm.o1
- t1.5tm.kn
- t1.5tm.fy
egg:
- /Users/jesseg/code/bees-workflow/docs/prd.md
- /Users/jesseg/code/bees-workflow/docs/sdd.md
created_at: '2026-05-03T01:16:37.269187'
status: ready
schema_version: '0.1'
guid: 5tm5an7kxvv2mo4mb1afh1s6dome5vpi
---

Replace Agent Teams orchestration in `bees-execute`, `bees-fix-issue`, and `bees-breakdown-epic` with ephemeral background `Agent` invocations + a reconciliation-loop orchestrator. Ships seven custom subagent definitions (`subagents/<role>.md`), preserves all current user-visible features at the high-level UX, and removes the experimental Agent Teams dependency along with its setup ceremony (the env var, the `teammateMode` display backend, the iTerm2 hard-prompt workaround, the `force_clean_team.py` and `check_agent_teams.py` helpers).

See `docs/prd.md` `## Per-feature scope` `### Feature: Ephemeral-Agent Orchestration` and `docs/sdd.md` `## Per-feature design` `### Feature: Ephemeral-Agent Orchestration` (linked via `egg`) for the canonical spec.
