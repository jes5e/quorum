---
id: b.cpy
type: bee
title: Per-project reasoning-effort overrides via a CLAUDE.md contract key
status: open
created_at: '2026-07-28T20:43:51.278099'
schema_version: '0.1'
reference_materials: null
guid: cpy6bi3saepkr1qc5igssfgnycnd1tsw
---

## Description

Add a per-project mechanism for overriding the per-role reasoning-effort tiers that **b.ajk** pinned globally in `agents/*.md` frontmatter.

Deferred out of **b.ajk** (Pin reasoning effort per role; drop the Sonnet downgrade prompt), which recorded this as a known limitation:

> **Known limitation — no per-project effort override.** The pinned table is global: a docs-heavy project and a docs-light one receive the same tiers, and the only escape hatch is hand-editing the installed agent files. Raising doc-writer to `high` mitigates the worst case but does not remove the limitation. If this bites in practice, the follow-up is a CLAUDE.md contract key for per-project effort overrides — deliberately out of scope here, since adding a contract key is a larger change than this ticket warrants.

## Why this is now more tractable than b.ajk assumed

b.ajk assumed the only viable path was a new CLAUDE.md contract key plus whatever machinery would apply it, and priced that as too large. A cheaper mechanism is now confirmed available.

The Agent tool's input schema in the installed Claude Code CLI carries a per-dispatch `effort` parameter:

> overrides the reasoning effort for this agent call ('low' | 'medium' | 'high' | 'xhigh' | 'max') — omit to inherit the session effort; use 'low' for cheap mechanical stages and higher tiers only for the hardest verify/judge stages.

This matters because it means an orchestrator can read a per-project key and pass the override **at dispatch time**, with no mutation of the installed agent files. That removes the worst part of the original design problem: the shipped skill set stays a single reviewed artifact, and per-project variation lives entirely in the consuming project's own tracked config — which is also where every other quorum contract key already lives.

Verified during the b.ajk fix pass by reading the tool-input validator out of the installed CLI binary.

## Design questions

1. **Key shape.** A `## Role Overrides` section in the target repo's CLAUDE.md, with one row per role and an effort value? Or a flatter single-key form? It must degrade cleanly when absent — the common case is no section at all, meaning "use the shipped defaults".
2. **Which skills read it.** All three dispatching skills (`quo-execute`, `quo-fix-issue`, `quo-breakdown-epic`), which means the read and the apply logic get triplicated into orchestrator prose — the drift surface b.ajk was explicitly trying to avoid. Weigh that cost honestly; it is the main argument against.
3. **Interaction with the reviewer invariant.** `CLAUDE.md` `## Model assignment in execution skills` records: never pin a reviewer below the role it reviews. A per-project override can silently violate that (raise the Engineer, leave the Code Reviewer). Either the skills validate the invariant when applying overrides, or the docs must state plainly that overriding is the operator's responsibility.
4. **Model as well as effort?** The same mechanism could carry a per-role model override. Note that b.ajk found frontmatter `model: opus` already floats with the operator's session Opus version, so the demand for a model override is weaker than it looks — and any model override must contend with availability (some models return HTTP 429 at zero rate limit in some organizations). Consider shipping effort-only first.
5. **Is a contract key the right home at all?** `quo-setup` writes the existing contract keys, so a new one implies a `quo-setup` change and a migration story for projects already set up.

## Scope

The target repo's `CLAUDE.md` contract-key surface (documented in this repo's `CLAUDE.md` `## Contract keys that downstream skills depend on`), `skills/quo-setup/SKILL.md`, and the three dispatching skills. Docs: `README.md`, `CLAUDE.md`, `docs/sdd.md`.

## Prior art to respect

`b.963` removed a `## Skill Paths` section that wrote per-machine absolute paths into a tracked file, because per-machine config in a shared file broke multi-engineer collaboration. A per-project effort table is **not** that error — it is per-project, not per-machine, and belongs to the project rather than the operator — but the distinction should be stated explicitly in whatever ships, so the precedent is not misread as forbidding this.

