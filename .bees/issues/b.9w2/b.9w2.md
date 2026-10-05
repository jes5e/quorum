---
id: b.9w2
type: bee
title: 'quo-plan-from-specs: stale /quo-plan claims, and a next-steps gate over AskUserQuestion''s four-choice limit'
parent: null
reference_materials: null
created_at: '2026-09-25T10:10:00.061506'
status: done
schema_version: '0.1'
guid: 9w2y36cyshns46youn5ktdr1xfh9f6bi
---

## Description

`/quo-plan-from-specs` was out of scope for the b.7ib rewrite of `/quo-plan`, and three problems surfaced there during that work.

## Current behavior

- **Stale claims.** `skills/quo-plan-from-specs/SKILL.md:25` and `:54`, and `docs/sdd.md:30`, say `/quo-plan` adds feature sections to cumulative docs. That has been false since b.31f: `/quo-plan` authors specs as Spec Bee children and never touches project docs.
- **Its next-steps gate lists five choices,** one over `AskUserQuestion`'s limit of four, so it can't be asked as written.
- **Some of its gate labels run past five words,** the tool's label guidance.

## Expected behavior

The claims describe `/quo-plan` as it is. The next-steps gate offers at most four choices, following `/quo-plan`'s set after b.7ib (the execute-now choices dropped, because every Epic is still drafted right after planning), and every label is five words or fewer.

## Suggested fix

A small prose fix in `/quo-plan-from-specs`, with its reader in `docs/sdd.md`. It's suitable for a `/quo-fix-issue` run, as a bounded prose fix to one skill. Leave "Encode in an existing ticket body" alone if it appears: b.pcc renames that label across all four deferral-hygiene gates in one pass.
## Closed (2026-10-04)

Fixed in small batch 1, merged to main by fast-forward, head `cc319f3`, not pushed.
- **The stale claims are gone.** `/quo-plan-from-specs` no longer says `/quo-plan` adds feature sections to project docs. That covers the description, the `--feature` note, the multi-feature guard, its hard-fail text, and its exit sentence. The matching `docs/sdd.md` line is corrected too. The guard now points only at `--feature`.
- **The next-steps gate now follows `/quo-plan`'s set and labels exactly:** four choices, each label five words or fewer. The "break down a specific Epic" choice is dropped, as in `/quo-plan`.
- **The guide matches.** `docs/doc-writing-guide.md`'s next-steps label rule now fits the five-word limit.
- **Not touched:** no deferral label appears in this skill.

Net −155 words in the skill. Recorded, not acted on: the skill's Overview still narrates history (true; a deletion candidate when a later change touches it), and nothing pins its next-steps gate to `/quo-plan`'s.
