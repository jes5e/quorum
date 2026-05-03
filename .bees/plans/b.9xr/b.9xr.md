---
id: b.9xr
type: bee
title: Optional beads backend
down_dependencies:
- b.gar
parent: null
children:
- t1.9xr.p6
- t1.9xr.4e
egg:
- /Users/jesseg/code/bees-workflow/docs/prd.md
- /Users/jesseg/code/bees-workflow/docs/sdd.md
created_at: '2026-05-02T14:09:41.628044'
status: in_progress
schema_version: '0.1'
guid: 9xr3vcmmpgympucy7314ji7dt5z2otz4
---

Add optional support for the beads ticket backend (https://github.com/gastownhall/beads) alongside the existing bees backend. A repo picks one at /bees-setup time; the choice persists in CLAUDE.md ## Ticket Backend. All 11 portable-core skills work transparently on either backend via a new skills/_shared/scripts/ticket_backend.py dispatcher. Both backends cannot coexist in a single repo.

See egg (PRD + SDD) for full scope, motivation, acceptance criteria, and architecture.
