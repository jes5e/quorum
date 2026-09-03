---
id: b.cvf
type: bee
title: quo-setup fast path re-colonize rewrites .hive/identity.json and drops allowed_resolvers
status: open
created_at: '2026-09-03T23:39:36.409791'
schema_version: '0.1'
reference_materials: null
guid: cvfmnfyztkk5y6df17xa2w8otareiymg
---

## Description

`/quo-setup`'s new-machine fast path re-registers an already-colonized hive by running `bees colonize-hive --name <hive>` against the existing on-disk hive. That call rewrites the hive's `.hive/identity.json` marker and drops fields the original colonization wrote — observed: the Specs hive lost its `"allowed_resolvers": ["bees"]` entry.

## Current behavior

Running the fast path in a fresh git worktree of this repo (2026-09-03, during the Issue b.y2q fix run) left `.bees/specs/.hive/identity.json` modified in the working tree with the `allowed_resolvers` array removed; `tiers`, `status_values`, and the rest were preserved. The run excluded the change from its commits; had it been swept in by a hive-directory stage (`hive_commit.py` stages whole hive paths), the Specs hive would have silently lost its resolver allowlist on the branch.

## Expected behavior

Re-registering an existing hive on a new machine must not modify the hive's identity marker. Either the fast path calls a registration-only bees operation (if one exists), or it passes the existing marker's settings (`allowed_resolvers`, tiers, status values) through unchanged, or it verifies the marker is byte-identical after the call and fails loudly if not.

## Impact

Correctness. `allowed_resolvers` governs which `reference_materials` resolvers a hive accepts; losing it can make Plan Bees that reference Spec Bees via the `bees` resolver fail validation on the affected checkout, and the loss is invisible unless someone reads the marker diff. Every worktree-based parallel run hits this path.

## Suggested fix

1. In `skills/quo-setup/SKILL.md` fast path (`#### Offer to re-register`/colonize step): replace the bare `colonize-hive --name` re-registration with whatever bees exposes for register-existing (check `bees colonize-hive --help` and `bees update-config --help`), or read `.hive/identity.json` first and re-supply its `allowed_resolvers` / tiers / status values on the call.
2. Add a post-step check: `git diff --quiet -- <hive>/.hive/identity.json` (or an equivalent read-back) and surface a warning if the marker changed.
3. Consider the same for `skills/quo-setup/scripts/detect_fast_path.py` if it participates in the rewrite.

## Background and rationale

Surfaced by the `/quo-fix-issue b.y2q` run in worktree `quorum-gauge-crash` on 2026-09-03; the run reported it as an unstaged side effect and deliberately excluded it. The same fast path runs at the start of every worktree-isolated quorum run, so the exposure recurs on every parallel run.

