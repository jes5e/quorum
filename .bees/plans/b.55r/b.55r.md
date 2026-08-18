---
id: b.55r
type: bee
title: Context-window guard for long orchestrator runs
parent: null
children:
- t1.55r.ec
- t1.55r.9d
- t1.55r.h9
reference_materials:
- value: b.8sh
  resolver: bees
created_at: '2026-08-16T17:33:11.989013'
status: ready
schema_version: '0.1'
guid: 55rjpn2y82za9a8qrkpqkfe8st5ds24r
---

Ship the **context-window guard**: a producer/consumer mechanism that lets the orchestrator skills (`/quo-execute`, `/quo-breakdown-epic`, `/quo-fix-issue`) stop gracefully at an Epic/Issue boundary before Claude Code's auto-compaction fires on long boundary-crossing runs. A status-line-fed per-session gauge file supplies the context-usage reading the model cannot obtain natively; the execution skills read it at boundaries and stop (recommending a fresh session) when usage nears the compaction threshold, hard-stopping with an inline `/quo-setup` offer when the gauge is absent in a supported environment.

Authoritative spec: the PRD and SDD `t1=Doc` children of Spec Bee **b.8sh** (referenced below). **Sequenced to land after the foundation defect-fix Issue b.ja9** (honesty rewrite of the Epic-boundary discipline) — the boundary consumer gate co-locates with the prose b.ja9 rewrites and must compose with it. Upstream simplifications tracked in b.cj2.

## Anticipated doc impact

- **Customer-facing docs** (`Customer-facing docs` key): publish the gauge-file contract (path, fields, overwrite-per-session semantics), a restricted/pinned-statusline-environment note, and the new optional `/quo-setup` step with its next-session activation caveat. Folded into the Epics that define those surfaces (not a standalone doc Epic).
- **Internal architecture docs (SDD)** and **Project requirements doc (PRD)** (`Internal architecture docs (SDD)` / `Project requirements doc (PRD)` keys): a cumulative `### Feature: Context-window guard for long orchestrator runs` subsection, authored exactly once by the post-implementation doc-writer pass triggered under **Epic 3** (the final Epic, when the feature is complete). Epics 1–2 fold in only their own surface docs (Epic 1 the README file-contract; Epic 2 the setup how-to) and must NOT also author the cumulative subsection. This resolves the SDD `RESEARCH NEEDED` on doc ownership.
- **Engineering best practices** (`Engineering best practices` key): only if the guard's residual limitation (pinned environments / unsupported-CLI carve-out) warrants a note; otherwise none.

## Review criterion — no shipped-artifact references to unshipped docs (user-requested 2026-08-18)

Every review cycle of this Bee's work (code review, test review, doc review, and PM review, in every Epic) MUST additionally flag any reference in a **shipped artifact** — `skills/<name>/SKILL.md` prose, `agents/<role>.md` contract files, or bundled helper scripts under `skills/*/scripts/` — to a **repo-only document the installed user never receives**: `docs/doc-writing-guide.md`, `docs/sdd.md`, `docs/prd.md`, `CONTRIBUTING.md`, `tests/`, or this repo's ticket IDs. Installed users get the `skills/` and `agents/` trees copied into their Claude Code config; they do not get this repo's `docs/` directory, so a shipped artifact that says "see `docs/doc-writing-guide.md` `## The context-gauge file contract`" points its reader at a file that does not exist for them.

Concrete watch-points for this feature: Epic 1's helper docstring must carry its own contract summary rather than deferring to the doc-writing guide; Epic 2's new quo-setup SKILL.md step and Epic 3's boundary-gate prose in the three execution SKILL.md files must cross-reference only shipped surfaces (the skill's own prose, the helper's docstring/`--help`, or the published README content) — never `docs/*` or `CONTRIBUTING.md`. Repo-internal docs referencing each other (SDD → doc-writing guide, etc.) is fine; the criterion bites only on shipped artifacts. The systemic fix (a reference architecture for installed-skill doc references) is tracked as Issue **b.bq4** — reviewers should flag new instances rather than wait on it.

