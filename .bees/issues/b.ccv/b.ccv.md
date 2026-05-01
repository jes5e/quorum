---
id: b.ccv
type: bee
title: Rename code-review/doc-review/test-review skills to bees-* prefix
parent: null
egg: null
created_at: '2026-04-30T22:03:08.576769'
status: done
schema_version: '0.1'
guid: ccvj52677qk6s44e4q3vdx7rgyxkd4zd
---

## Description

The three review skills `code-review`, `doc-review`, `test-review` ship as part of the bees-workflow package but are not prefixed with `bees-`. The original rationale in `CONTRIBUTING.md` `## Considered and rejected` claims they were left unprefixed because they are *"general-purpose review skills useful standalone."* Reading the actual SKILL.md files invalidates that claim:

- Each skill is **dual-mode by design**, with explicit prose branches for standalone vs bees-coupled invocation (`code-review/SKILL.md:12-14`, `:111`; `doc-review/SKILL.md:13-15`, `:111`; `test-review/SKILL.md:13-15`, `:120`).
- ~85% of each SKILL.md is generic review guidance (look for bugs, security issues, dead code, test coverage gaps, doc completeness, etc.).
- ~15% is bees-specific: the loop-bounding logic that prevents infinite review-fix-review cycles inside `/bees-execute` and `/bees-fix-issue`. Worded as "When invoked from `/bees-execute` or `/bees-fix-issue` specifically: …"
- The standalone branch is real but provides marginal value beyond a free-form Claude prompt (e.g., "review the diff against main"). The skills' load-bearing use case is bees-coupled invocation by the team-lead during `/bees-execute` / `/bees-fix-issue` review cycles.

The "general-purpose" framing in CONTRIBUTING.md and README.md misrepresents what the skills are. The `bees-` prefix more honestly conveys package origin without precluding standalone use.

## Current behavior

- Skill directories: `skills/code-review/`, `skills/doc-review/`, `skills/test-review/`.
- Frontmatter `name:` fields in each `SKILL.md`: `code-review`, `doc-review`, `test-review`.
- `bees-execute/SKILL.md` and `bees-fix-issue/SKILL.md` reference the unprefixed names when telling the team-lead to invoke `/code-review`, `/test-review`, `/doc-review`.
- `README.md` skill table lists the unprefixed names and includes the (overstated) sentence: *"The three reviewers (`code-review`, `doc-review`, `test-review`) are general-purpose and don't depend on the bees workflow — useful standalone too."*
- `CONTRIBUTING.md` `## Considered and rejected` documents the prefix decision as deliberate based on the now-invalid premise.
- `docs/sdd.md` `## Key components` lists the three skills under their unprefixed names.

## Expected behavior

- Skill directories renamed: `skills/bees-code-review/`, `skills/bees-doc-review/`, `skills/bees-test-review/`.
- Frontmatter `name:` fields updated to match.
- The dual-mode prose inside each SKILL.md is **preserved** — keeping standalone invocation as a documented affordance even though primary use is bees-coupled. The rename acknowledges package origin without removing optionality.
- Consumer skills (`bees-execute`, `bees-fix-issue`) invoke the new names.
- README's skill table reflects the rename.
- CONTRIBUTING.md's `## Considered and rejected` entry is reversed to a `## Status / type renames history` entry (the existing section already documents past renames like `bugs`→`issues` and the larva/pupa/worker/finished status renames; this is the same pattern).
- README sentence about standalone use updated to acknowledge that the prefix is package-origin signal, not coupling-strength signal: e.g., *"The three reviewers (`bees-code-review`, `bees-doc-review`, `bees-test-review`) are dual-mode — primarily invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles, but they also support standalone invocation if you want an ad-hoc review without the bees workflow."*
- `docs/sdd.md` updated similarly.

## Impact

**Discoverability and disambiguation.** Generic names (`code-review`, etc.) are likely to collide with other skill packages a user installs. Prefixing eliminates the namespace collision and makes "this came from bees-workflow" obvious at the skill-list level.

**Documentation honesty.** The current "general-purpose" framing is misleading and CONTRIBUTING.md explicitly reasoned from a false premise. The rename + doc updates put the documented rationale in agreement with the actual skill content.

**Removability.** A user uninstalling bees-workflow can grep for `bees-` to identify which skills came from this package. With unprefixed names, this is harder.

**Standalone-use friction (small, accepted).** A user browsing their skill list for "give me a code review" might skip past `/bees-code-review` thinking it requires the bees workflow. Mitigated by:

1. The README sentence about dual-mode use (gets updated as part of the fix).
2. The skill `description` field, which Claude Code shows to the user — if updated to mention dual-mode use, the standalone affordance stays discoverable.

**Existing user impact.** Users who have `/code-review` etc. wired into shortcuts, automations, or muscle memory will need to update. No deprecation-shim mechanism exists in this repo and adding one for three rarely-renamed skills is overkill. Just announce in the commit message; CONTRIBUTING.md's rename-history section captures it permanently.

## Suggested fix

**Phase 1 — rename skill directories and frontmatter.**

For each of the three skills:

1. `mv skills/<name> skills/bees-<name>` (preserve git history with `git mv`).
2. Edit the frontmatter at the top of `SKILL.md`: `name: <name>` → `name: bees-<name>`.
3. Optionally update the `description:` field to mention dual-mode use, e.g., for code-review:
   *"Perform code review of a change set. Primary use: invoked by `/bees-execute` and `/bees-fix-issue` during review cycles. Standalone use: ad-hoc review of a diff/worktree/files."*

The skill prose (Sections 1 and 2 of the dual-mode branches I described — top-of-file and the loop-bounding rule) stays as-is. The standalone branch is preserved.

**Phase 2 — update consumer references in execution skills.**

`bees-execute/SKILL.md` and `bees-fix-issue/SKILL.md` invoke `/code-review`, `/test-review`, `/doc-review` from inside their team-lifecycle prose. Find each callsite and update to the prefixed name. `grep -n "/code-review\|/doc-review\|/test-review" skills/bees-execute/SKILL.md skills/bees-fix-issue/SKILL.md` to enumerate.

**Phase 3 — update repo docs.**

- `README.md` skill table: rename the three rows.
- `README.md` standalone-use sentence: reframe as "dual-mode" per the Expected behavior section above.
- `CONTRIBUTING.md`: delete the existing `## Considered and rejected` entry titled *"Renaming `code-review` / `doc-review` / `test-review` to `bees-code-review` etc. for prefix consistency"*. Add an entry under `## Status / type renames history` (the existing section that covers `bugs` → `issues` and the bee-themed-status rename). Suggested text:

  > **Skill renames `code-review` / `doc-review` / `test-review` → `bees-code-review` / `bees-doc-review` / `bees-test-review`.** The original rejection of this prefix in *Considered and rejected* was based on the premise that the skills were "general-purpose useful standalone." Reading the SKILL.md files invalidated that premise — the skills are dual-mode by design with explicit bees-coupled prose (loop-bounding logic for the `/bees-execute` and `/bees-fix-issue` review cycle) interleaved with the generic review prose. The `bees-` prefix more honestly conveys package origin. Standalone invocation remains supported via the existing dual-mode prose; the prefix says nothing about coupling strength.

- `docs/sdd.md` `## Key components`: rename the three review-skill bullets.

## Files to modify

- `skills/code-review/` → `skills/bees-code-review/` (directory rename via `git mv`)
- `skills/doc-review/` → `skills/bees-doc-review/`
- `skills/test-review/` → `skills/bees-test-review/`
- `skills/bees-code-review/SKILL.md` (frontmatter `name:` field, optional description update)
- `skills/bees-doc-review/SKILL.md` (same)
- `skills/bees-test-review/SKILL.md` (same)
- `skills/bees-execute/SKILL.md` (consumer references)
- `skills/bees-fix-issue/SKILL.md` (consumer references)
- `README.md` (skill table + standalone-use sentence)
- `CONTRIBUTING.md` (move entry from Considered and rejected to Status / type renames history)
- `docs/sdd.md` (Key components list)

## Out of scope

- **Stripping the dual-mode prose / standalone branch.** The earlier framing of this fix (option 1 in the conversation that led to filing this) was "rename + drop standalone branch." That was rejected in favor of "rename + keep standalone branch" because the rename is about acknowledging package origin, not enforcing coupling. Don't strip the standalone branch as part of this fix.
- **Adding deprecation shims for the old names.** Overkill for a three-skill rename. Just announce in the commit message; users update their automations.
- **Adding genuine standalone value (review checklists, methodology, etc.).** Was a separate option in the same conversation; would be its own ticket if pursued. Don't bundle.
- **Inlining the three skills into the consumers.** Was a third option; rejected for being too invasive. Out of scope.

## Adjacent findings (note, do not bundle)

- The skill `description` field is what Claude Code surfaces to the user when picking which skill to invoke. Currently the descriptions are short and don't mention dual-mode use. As part of this rename, consider lengthening each description to make the standalone affordance discoverable from the description alone, not just the README. Mentioned under Phase 1 step 3 above as optional; can also be a follow-up.
- After the rename, the README and CONTRIBUTING.md will note that bees-workflow ships eight `bees-*` skills (was: five `bees-*` skills + three unprefixed). The CLAUDE.md count and language about "11 portable-core skills" should be re-checked for any places where the count or split is referenced numerically.
