---
name: bees-status
description: Show the bees-driven SDLC workflow stages and current progress across all hives in this repo
triggers:
  - where are we
  - what's next
  - workflow status
  - bees status
  - what do I do next
---

# Bees Workflow Status

Show the user where they are in the bees-driven SDLC workflow and what to do next.

## Workflow Stages

The bees SDLC has these stages, in order:

| # | Stage | Skill | Input | Output |
|---|-------|-------|-------|--------|
| 1 | **Setup** | `/bees-setup` | A repo | `plans` and `issues` hives configured with ticket types and statuses |
| 2 | **Write specs** | (manual) | PRD and SDD documents on disk | `docs/prd.md` and `docs/sdd.md` (or similar) |
| 3 | **Plan** | `/bees-plan-from-specs` | PRD + SDD | A Plan Bee (`status=ready`) with Epic children (`status=drafted`) |
| 4 | **Break Down** | `/bees-breakdown-epic` | A Plan Bee or Epic | Epics broken into Tasks and Subtasks (Epic `status=ready`) |
| 5 | **Execute** | `/bees-execute` | A Bee | Code written, committed, tests passing. Tickets `status=done` |
| 6 | **Merge** | `/bees-worktree-rm` | A completed worktree | Branch merged, worktree cleaned up |

For multi-Bee or multi-repo orchestration, `/bees-fleet` can launch and monitor multiple `/bees-execute` instances in parallel via worktrees.

## How to Determine Current State

Run these queries in parallel to assess progress:

```bash
# 1. Check if hives exist
bees list-hives

# 2. All Plan Bees
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans]
report: [title, ticket_status, children]'

# 3. All Epics under Plan Bees
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=plans]
  - [children]
report: [title, ticket_status, up_dependencies]'

# 4. All Issue Bees
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues]
report: [title, ticket_status]'
```

## How to Report Status

### 1. Hive Setup
If no hives exist: **"No hives configured. Run `/bees-setup` to get started."**

### 2. Spec Documents
Check if the repo has PRD/SDD documents (look at CLAUDE.md for paths, or check `docs/`).
If no specs: **"Write your PRD and SDD first, then run `/bees-plan-from-specs`."**

### 3. Plan Bees
For each Plan Bee, report:
- Title and status
- Total Epics and their status breakdown

Use these status meanings:
- `drafted` = written but children not yet created (needs `/bees-breakdown-epic` to create them)
- `ready` = fully planned with Tasks/Subtasks (ready for `/bees-execute`)
- `in_progress` = actively being worked on
- `done` = completed

### 4. Output Format

```markdown
## Bees Workflow Status

### Hives: [OK | Not configured]
### Specs: [Found at path | Not found]

### Plan Bees
| Bee | Title | Status | Epics |
|-----|-------|--------|-------|
| b.xxx | Title | ready | 3 done, 5 ready, 2 drafted |

### Epic Breakdown: [bee title]
| Epic | Title | Status | Blocked By | Next Action |
|------|-------|--------|------------|-------------|
| t1.xxx | ... | done | — | Done |
| t1.yyy | ... | ready | — | Ready for `/bees-execute` |
| t1.zzz | ... | drafted | — | Needs `/bees-breakdown-epic` |
| t1.aaa | ... | ready | t1.yyy (ready) | Blocked until t1.yyy is done |

### Issue Bees
| Bee | Title | Status |
|-----|-------|--------|
(or "No issues tracked")

### What's Next
[One clear sentence telling the user the recommended next action, e.g.:]
- "All Epics are broken down. Run `/bees-execute b.xxx` to start executing."
- "2 Epics still need to be broken down. Run `/bees-breakdown-epic` to continue."
- "All Epics are done. Run `/bees-worktree-rm` to merge."
```

### 5. Decision Logic for "What's Next"

Walk this tree top-to-bottom; first match wins:

1. No hives → `/bees-setup`
2. No specs found → "Write PRD and SDD"
3. No Plan Bees → `/bees-plan-from-specs`
4. Any Plan Bee has drafted Epics → `/bees-breakdown-epic` (report how many are drafted vs. ready)
5. Any Plan Bee has ready Epics with all deps done or no deps → `/bees-execute [bee-id]`
6. All Epics are `in_progress` → "Work in progress — check active sessions"
7. All Epics are `done` → `/bees-worktree-rm` or "All done — merge and ship"
8. Issue Bees open → `/bees-fix-issue` or `/bees-execute [issue-id]`
