---
id: b.veq
type: bee
title: 'Review skills (code/test/doc): re-read current state at review time + flag Black-25 except paren-strip'
status: open
created_at: '2026-05-02T13:36:25.555129'
schema_version: '0.1'
egg: null
guid: veq3drde7ke1yi49dkw26hg3649tvw1h
---

## Description

A user running `bees-execute` on another project reported that the PM / reviewer agent (`pm-hn`) reviewed an intermediate state of the change instead of the final committed / staged state. Specifically, the review fired against a post-Black-strip pre-restructure snapshot, so feedback was about code the engineer had already moved past.

A related landmine to bake into the same review skills: Black 25's known paren-stripping behaviour on `except (A, B):` lines (the user's project hit this on commit `2ddf934`). After a lint / format pass the paren-stripped form looks like a malformed except clause; review skills should flag it as suspect.

## Current behavior

- Review skills (`bees-code-review`, `bees-test-review`, `bees-doc-review`) appear to read from a buffered diff captured at review-spawn time, rather than re-reading the working tree / HEAD when the review actually runs.
- Reviews comment on already-superseded code, wasting the engineer's turn on stale feedback.
- No explicit guidance to suspect post-lint `except (A, B):` lines, even though Black 25's stripping is a known footgun.

## Expected behavior

- Each review skill re-reads the change set against current HEAD / working tree at the moment review runs — an explicit "re-read against current state" step in the skill prose.
- The review checklist includes an explicit suspect-pattern entry: after a format / lint pass, treat `except (A, B):` lines as suspect (Black 25 paren-stripping) and flag any malformed except clause.

## Impact

- Engineer receives stale feedback and either wastes a turn re-arguing it, or — worse — regresses the file back to match the stale critique.
- Silent Black-25 paren-strip bugs slip through reviews that should have caught them.

## Suggested fix

Edit `skills/bees-code-review/SKILL.md`, `skills/bees-test-review/SKILL.md`, and `skills/bees-doc-review/SKILL.md`:

1. Add an explicit "re-read against current state" step at the top of each skill's review procedure — invoke `git diff HEAD` (or read the working tree directly) at review time rather than trusting a buffered diff passed in by the caller.
2. Add a suspect-pattern checklist entry: "after a format / lint pass, treat `except (A, B):` lines as suspect (Black 25 paren-stripping)" — and flag any malformed except clause in the diff.

## Severity

Medium — stale reviews waste engineer turns and silently miss Black-25 lint regressions.

