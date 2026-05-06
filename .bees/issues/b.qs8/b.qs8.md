---
id: b.qs8
type: bee
title: '/bees-file-issue: add --reference URL mode for external sources (GitHub, Linear, etc.)'
status: open
created_at: '2026-05-06T17:38:05.970102'
schema_version: '0.1'
reference_materials: null
guid: qs82oryj5iioydxupfqqivh8zv776dvu
---

## Description

Add a `--reference <url>` (or `--from-github <url>`) flag to
`/bees-file-issue` that creates a thin Issue ticket whose
`reference_materials` points at an external resource (GitHub Issue,
Linear ticket, internal bug tracker URL, etc.) instead of the body
carrying all the spec content. Symmetric with `/bees-plan-from-specs`
on the planning side.

## Background and rationale

Today's `/bees-file-issue` only supports the in-conversation capture
path: the user describes a bug interactively (or passes a free-text
description), the skill creates an Issue with body-as-spec content.
This is right for in-conversation discoveries, but it's a gap when
the user already has the bug described elsewhere — a GitHub Issue,
a Slack thread, an internal bug tracker — and just wants the bees
workflow to point at it.

This came up during the planning of `b.31f` ("Side-effect-free
/bees-plan and /bees-file-issue with preserved context"). The
discussion noted that `reference_materials` is a polymorphic
abstraction that already supports external pointers (the bees CLI
accepts arbitrary resolvers). Adding the external-reference mode
on the issue side would parallel `/bees-plan-from-specs` on the
plan side: same skill, two invocation modes, depending on whether
the spec content lives in-conversation (body-as-spec) or externally
(`reference_materials`).

Deferred from `b.31f` because:
- The core problem `b.31f` solves is docs pollution + info loss.
  External-reference mode is a *new feature*, not part of the bug
  fix. Folding it in expanded scope without addressing the original
  problem any better.
- A concrete external resolver (e.g., a GitHub-issue resolver) is
  separate work — the design accommodates them via the existing
  `reference_materials` abstraction; concrete resolvers are filed
  separately when their owners materialize.

## Suggested fix

Once `b.31f` lands (or in parallel — this Issue does not depend on it):

1. Add `--reference <url>` (and aliases like `--from-github <url>`,
   `--from-linear <id>` etc. as appropriate) to `/bees-file-issue`'s
   argument-hint and arg-parsing.
2. When the flag is present, skip the body-template authoring step and
   instead create the Issue with:
   - A short body summarizing what the bees workflow needs to know
     (2-3 sentences distilled from the URL or accompanying user
     description).
   - `--reference-materials '[{"value":"<url>","resolver":"<name>"}]'`
     where `<name>` is determined by the URL shape (e.g., a
     `github-issue` resolver if the URL matches a GitHub Issue
     pattern; fall back to a generic `url` resolver otherwise).
3. Verify `/bees-fix-issue`'s PM and engineer dispatch correctly
   reads `reference_materials` to fetch the external content (this
   may require adding the resolver-specific fetch logic if it
   doesn't already exist).
4. Update README's skill catalog to document the new mode.

## Out of scope

- Building specific external resolvers (GitHub Issues, Linear, etc.) —
  those are separate Issues filed against `bees` itself or
  `bees-workflow` as their owners materialize.
- Migrating existing in-conversation-filed Issues to external mode.
- Promoting an Issue to a Plan Bee (the manual workaround — close
  Issue, file Plan referencing it — remains for now).

## Dependencies

None. This Issue is independent of `b.31f` and can land in parallel.
The two changes don't conflict — `b.31f` makes the existing in-
conversation path richer; this Issue adds a new external-reference
path alongside it.

