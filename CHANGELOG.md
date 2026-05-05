# Changelog

## Unreleased

- Migrated `/bees-execute`, `/bees-fix-issue`, and `/bees-breakdown-epic` from the experimental Agent Teams substrate to ephemeral background-Agent dispatch. Added top-level `agents/<role>.md` definitions for the seven roles (Engineer, Test Writer, Doc Writer, PM, Code Reviewer, Test Reviewer, Doc Reviewer). Deleted `force_clean_team.py` and `check_agent_teams.py` (no longer needed). `/bees-setup` no longer prompts for Agent Teams or `teammateMode`. Refreshed Plan Bee `b.gar`'s body for the bees-only post-orchestration world. (Plan Bee b.5tm)
  - The new substrate uses a reconciliation-loop pattern — see Section 3 of `skills/bees-execute/SKILL.md`.
