---
id: b.51d
type: bee
title: Downstream skills don't respect Plan Bee 'Scoped to ...' marker (b.mu9 follow-up)
status: open
created_at: '2026-05-03T01:59:18.305296'
schema_version: '0.1'
egg: null
guid: 51d97prmesca53c4ud7g3av353fm5qbu
---

## Description

Downstream skills (`bees-breakdown-epic`, `bees-execute`, `bees-fix-issue`) do not respect the `Scoped to `### Feature: <title>` from <prd> and <sdd>.` marker that `/bees-plan-from-specs --feature "<title>"` now writes into the Plan Bee body (shipped as part of b.mu9).

This is a known follow-up surfaced during the b.mu9 review loop by both the in-flight Phase 2 PM (`pm-mu9-b`) and the final Code Reviewer (`code-reviewer-mu9-final`). Both agreed deferral was safe because the recommended workflow (`/bees-plan` inline-only) does not trigger the scoped-egg case — only standalone `/bees-plan-from-specs --feature` invocations against a cumulative PRD/SDD hit it. The Step 8 fresh-context post-completion reviewer for b.mu9 also explicitly endorsed deferring it.

## Current behavior

When a Plan Bee is created via `/bees-plan-from-specs --feature "<title>"`:

1. The Plan Bee's `egg` is set to the full cumulative PRD + SDD absolute paths (intentional — egg points at canonical doc files, not at scoped subsections).
2. The Plan Bee's body contains a marker line of the literal form:
   `Scoped to ``### Feature: <title>`` from <prd-path> and <sdd-path>.`
3. Downstream skills (`bees-breakdown-epic` Step 1 when reading the parent Bee; `bees-execute` Step 4 PM section when comparing implementation to spec; `bees-fix-issue` PM role similarly) resolve the egg and treat the resulting full doc content as the canonical spec for the Bee.
4. The marker is invisible to those skills — they branch only on "egg present" vs "egg null", with no awareness that the egg's resolved content might be scoped.

Result: a Plan Bee scoped to one feature inside a cumulative spec will silently surface every other feature's content to PM/Code-Reviewer logic during breakdown, execute, and fix-issue flows — exactly the scope-drift class b.mu9 tried to eliminate, just at a later workflow phase.

## Expected behavior

When a downstream skill (`bees-breakdown-epic`, `bees-execute`, `bees-fix-issue`) reads a Plan Bee whose body contains the marker:

`Scoped to ``### Feature: <title>`` from <prd-path> and <sdd-path>.`

…it should restrict the egg-resolved doc content to the matching `### Feature: <title>` subsection in each named doc:

- The subsection body runs from the matched heading line (exclusive) to the next `### Feature:` heading (exclusive) or end-of-file, whichever comes first — the same extraction rule `/bees-plan-from-specs` Step 1b applies.
- All PM / spec-compare / Epic-decomposition logic in the downstream skill should operate on the scoped content only.
- If the marker references a heading that no longer exists in either doc (e.g., the doc was edited after the Plan Bee was created), hard-fail with a clear error rather than silently falling back to the full doc.

The marker line is the durable signal of scope. The egg-paths-stay-full design from b.mu9 is intentional — it keeps the canonical-spec contract stable so the docs themselves remain the source of truth — and this issue's job is to teach the downstream readers about the scoping convention.

## Impact

**Severity: medium.**

- Footgun-class. Feature works as documented today; the standalone `--feature` path is one step removed from a real scope-drift incident at breakdown / execute / fix-issue time.
- Limited blast radius. Recommended workflow (`/bees-plan` inline-only) does not produce scoped Plan Bees, so this only affects users who deliberately reach for `/bees-plan-from-specs --feature "<title>"` against a cumulative spec.
- Docs and SKILL.md prose for `/bees-plan-from-specs` correctly describe what the marker is; the gap is that downstream skills don't yet read it.

## Suggested fix

Three skill files to update, each in roughly the same shape:

- `skills/bees-breakdown-epic/SKILL.md` — Step 1 (read parent Bee). After resolving the egg, check the parent Bee's body for the `Scoped to ...` marker; if present, parse out `<title>`, `<prd-path>`, `<sdd-path>`, and scope each resolved doc's content to the matching `### Feature: <title>` subsection.
- `skills/bees-execute/SKILL.md` — Step 4 PM section (compare impl against spec). Same marker check; PM should compare the diff against scoped content only when the marker is present.
- `skills/bees-fix-issue/SKILL.md` — PM role (complex fixes only) reads spec docs for context. Same marker check; scope to the relevant subsection when the issue's parent Bee carries the marker. (This skill operates on Issues, which don't have parent Plan Bees by default — the marker check applies only when an Issue derives from a scoped Plan Bee, which is currently rare but should be handled correctly.)

Recommended approach: extract a shared marker-parsing helper (Python script under one skill's `scripts/` or a small inline parser block referenced from each SKILL.md) so the three skills stay in sync. The marker grammar is small enough to keep as inline prose if a script feels heavy.

Constraints carried over from this repo's CLAUDE.md (mandatory):
- Language-neutral, project-neutral, POSIX+PowerShell paired shell snippets.
- No CLAUDE.md `## Documentation Locations` / `## Build Commands` contract-key renames.
- Bash etiquette: one literal command per Bash call.

## Related work

- b.mu9 (`/bees-plan` Path A delegation breaks with cumulative PRDs) — closed; introduced the marker.
- This issue closes the cumulative-PRD pattern end-to-end across the planning + breakdown + execute + fix-issue flow.

