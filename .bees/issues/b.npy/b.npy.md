---
id: b.npy
type: bee
title: 'Analyst gate rendering: site lists as counts, scope split and policy decisions in full'
tags:
- process
- quo-fix-issue
- analyst
status: open
created_at: '2026-09-10T19:09:45.708269'
schema_version: '0.1'
reference_materials: null
guid: npyxnmckvueseb2snv7exsongyopxhs7
---

## Description

The Analyst gate surfaces `### Blast radius` and `### Policy decisions this change implies` in full before firing the Approve / Revise / Cancel question. On a real run that produced a multi-page gate message; in an unattended run it is log volume, and in an attended run it buries the question the operator must answer.

## Expected behavior

Decide the rendering: keep the scope-split recommendation and the policy decisions in full, and render the per-invariant site lists as counts with a pointer to the full proposal already surfaced as prose. The full sections must still reach the Engineer directive verbatim; only the gate's rendering changes. This alters a ratified decision from the Analyst blast-radius Issue (surface both sections in full), so it is a design decision for the operator, not a fix.

## Source

First validation run of the rewritten orchestrators (2026-09-10), defect 14.

