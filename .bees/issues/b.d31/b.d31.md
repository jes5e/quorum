---
id: b.d31
type: bee
title: 'agents/pm.md: restore the Instructions list''s structure and move Scoped-marker Paths A/B and maintainer rationale out of the cold-loaded role file'
status: open
created_at: '2026-09-11T01:35:04.266409'
schema_version: '0.1'
reference_materials: null
guid: d31kkq9x2uz3xsa6mryhc4dfuu2o7u3w
---

## Description

`agents/pm.md` is loaded cold on every PM dispatch, so its size is a per-dispatch cost, and it has grown 25% (4,887 → 6,125 words) since the rewrite brief asked for it to be trimmed. A cold research pass on 2026-09-11 classified it as roughly 59% executable instruction, 20% counter-anchor prose (24 "do not"; a ~150-word "shape-based short-circuit is explicitly rejected" paragraph restating the preceding four-step procedure negatively; "future maintainers MUST NOT silently break this dual-use"), 10% maintainer rationale (`### Asymmetric error-handling (intentional; load-bearing; do NOT harmonize)` is addressed to future maintainers, not to the PM being dispatched), and 9% duplication (Scoped-marker Paths A and B each carry the same mkdir pair, helper-invocation pair, exit-code parse, and no-delete note).

## Current behavior

The `## Instructions` bullet list is interrupted at line 27 by four inserted sections (`### Resolving reference_materials entries`, `## No-spec-surface short-circuit`, `## Spec-source scoping`, Paths A / B, `### Asymmetric error-handling`) and resumes as bare bullets at line 213 under the asymmetric-error-handling heading. The 2,400 words of core PM instruction (review scope, in-flight review orchestration, cross-Task checks, the Final report contract, the deferred-item destination contract) therefore sit under a heading about exit-code handling. That is accretion, not design.

## Expected behavior

The core PM instructions sit under `## Instructions` in one list. The Scoped-marker Paths A and B live in one shipped reference file (for example `skills/quo-execute/references/scoped-marker-pm.md`, read by the PM, which has `Read`) with one mkdir / invoke pair rather than two. Maintainer rationale about why Path A hard-fails and Path B is best-effort moves to `docs/sdd.md`, where maintainer rationale belongs, leaving one sentence in the role file stating the asymmetry as a rule. Estimated saving ~1,500 words per PM dispatch.

## Suggested fix

Inventory-anchored hand edits with a cold review, per CLAUDE.md `## Working on the orchestrator skills`; not a `/quo-fix-issue` run. Risk is medium: the Path A hard-fail versus Path B best-effort behavior is load-bearing and cross-referenced by three skills through `<scoped-marker-resolver-path>`, and the role frontmatter must keep the `Write` tool and its rationale. Note that b.sb7 follow-up 12a proposes retiring the Scoped-marker machinery entirely once the downstream repos migrate; if 12a lands first, Paths A / B are deleted rather than moved, so sequence this after b.sb7's follow-ups are decided.

## Background and rationale

Surfaced by the prose-size research the operator requested after asking whether the skill files are unnecessarily large. The research's overall finding: shipped prose is ~128k words, of which roughly 30–35% is accumulated (cuttable or movable) rather than intrinsic; this file and `quo-setup`'s dead migration are the two items outside the b.pcc / b.7ib rewrite scope.

