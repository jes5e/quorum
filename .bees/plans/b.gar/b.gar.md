---
id: b.gar
type: bee
title: Test strategy for the skills repo
up_dependencies:
- b.9xr
parent: null
children:
- t1.gar.9u
- t1.gar.hc
- t1.gar.y1
egg:
- /Users/jesseg/code/bees-workflow/docs/prd.md
- /Users/jesseg/code/bees-workflow/docs/sdd.md
created_at: '2026-05-02T14:35:15.596968'
status: ready
schema_version: '0.1'
guid: gar4i66e8qut657irna2i8ate97b4hjq
---

Add a layered test strategy for the bees-workflow repo itself: pytest unit tests on bundled helpers (Layer 1), a structural SKILL.md linter (Layer 2), and a backend-equivalence harness validating the bees and beads adapter paths in ticket_backend.py (Layer 2.5). All three layers wire to a single `make test` entrypoint. Layer 3 (live Claude Code end-to-end smoke) is explicitly out of scope.

See egg (PRD + SDD) for full scope, motivation, acceptance criteria, and architecture. Blocks on b.9xr ("Optional beads backend").
