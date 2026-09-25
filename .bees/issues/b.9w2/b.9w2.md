---
id: b.9w2
type: bee
title: 'quo-plan-from-specs: stale /quo-plan claims, and a next-steps gate over AskUserQuestion''s four-choice limit'
status: open
created_at: '2026-09-25T10:10:00.061506'
schema_version: '0.1'
reference_materials: null
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

