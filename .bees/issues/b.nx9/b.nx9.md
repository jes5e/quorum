---
id: b.nx9
type: bee
title: 'Deferral hygiene: Encode to a ticket in another repo''s hive has no defined write or commit path'
tags:
- process
- quo-fix-issue
- quo-execute
- deferral-hygiene
status: open
created_at: '2026-09-10T19:09:42.387064'
schema_version: '0.1'
reference_materials: null
guid: nx99qhi3jtqiz5r7bgd8bjvaxodvyz41
---

## Description

The deferral-hygiene gate's `Encode in an existing ticket body` branch assumes the destination ticket lives in the current repo's hive. On a real run a deferral targeted a ticket in a sibling repo's hive; the bees CLI is cwd-scoped, so `bees update-ticket` had to run from that other checkout, which wrote the body into another repo's working tree, and `hive_commit.py --skill quo-fix-issue` commits only in the current repo, so the change was left uncommitted in another lane's worktree.

## Expected behavior

Both orchestrators' Encode branch handles a cross-hive destination explicitly: name the destination checkout, say whether and how to commit there (or refuse the destination and route the item to `File as issue tickets` in the current hive instead), and never leave an uncommitted write in a checkout the run does not own. Whichever design is chosen must stay stack-neutral and must not add a scratch write outside `<tempdir>/.quorum/`.

## Source

First validation run of the rewritten orchestrators (2026-09-10), defect 10. This is a design question (a cross-repo write path is new machinery), so it is filed rather than fixed in the validation pass.

