---
id: b.31f
type: bee
title: Side-effect-free /bees-plan and /bees-file-issue with preserved context
down_dependencies:
- b.uxa
- b.2w1
- b.tbr
parent: null
children:
- t1.31f.ho
- t1.31f.by
- t1.31f.5u
- t1.31f.y2
- t1.31f.4u
- t1.31f.6w
- t1.31f.67
- t1.31f.g8
reference_materials: null
created_at: '2026-05-06T17:32:38.048868'
status: done
schema_version: '0.1'
guid: 31fywhgtz3ipqo8afnwcgbf1ft9dcx2s
---

## What

Redesign `/bees-plan` and `/bees-file-issue` to (a) remove their current
doc-mutation side-effects on the project's PRD/SDD/README, and (b) preserve
the rich context of pre-skill-invocation conversations through to downstream
execution agents. Adopt apiary's two-Bee + `reference_materials` pattern: a
new `Specs` hive holds Spec Bees with `t1=Doc/Docs` children (PRD, SDD); the
Plan Bee's `reference_materials` points at the Spec Bee via the `bees`
resolver. Project-wide cumulative PRD/SDD docs continue to exist but are
maintained *after-the-fact* by the doc-writer agent during execution,
reflecting current/historical state of the system rather than forward intent.

## Why — three classes of problem this Bee solves

### Problem 1: `/bees-plan` Step 4 mutates project docs at plan time

Today's `/bees-plan` Step 4 categorizes the feature and writes updates to
`docs/prd.md`, `docs/sdd.md`, and the README before any code exists, then
sets `reference_materials` to point at the (now-mutated) docs. This is the
primary problem the user surfaced, and it has three downstream symptoms:

1. **Plan-without-execute pollutes docs.** Drafting a plan you may never
   execute (or won't execute for weeks) writes future-state design into
   docs that are nominally describing current behavior. Reverting is
   manual and error-prone.
2. **Pass-through coordination is complex.** The Scoped-marker machinery
   (`Scoped to '### Feature: <title>' from <prd> and <sdd>.`) exists
   precisely so downstream skills can find the right `### Feature:`
   subsection in cumulative project docs. The marker, the
   `scoped_marker_resolver.py` helper, the asymmetric Path A vs Path B
   handling in `agents/pm.md` — all of it is overhead created by
   co-mingling per-feature spec content into shared project docs.
3. **Parallel planning becomes incoherent.** Drafting Plan A then Plan B
   before executing A leaves the docs layered with future state for two
   features that don't exist yet. Reviewers and execution agents see
   the docs as authoritative but they're partially fictional.

### Problem 2: Information loss across the planning boundary

Quorum is built on a "every session is cold" principle —
`/bees-plan`, `/bees-breakdown-epic`, `/bees-execute`, the dispatched
subagents, all read from tickets + disk and nothing else. This is good and
intentional; it lets work happen in parallel sessions and across machines.
But the corollary is unforgiving: whatever doesn't make it into a ticket,
doc, or `reference_materials` simply doesn't exist for any subsequent
session.

Today's `/bees-plan` writes a "2-3 sentence summary" Plan Bee body, which
was barely defensible when `reference_materials` carried the spec content
and is *not* defensible if we move to body-as-spec. A thorough planning
conversation — with rationale, rejected alternatives, constraints, the
*why* behind decisions — gets funneled into 2-3 sentences. Downstream
PM agents and engineers may re-litigate decisions or re-introduce
rejected approaches because they have no record of what was already
considered.

The skill itself makes the problem worse mid-conversation: Step 1 ("Before
I start researching, is there anything I should know?") and Step 2
clarifying questions treat every invocation as if you'd just walked in
cold, even when invoked from a substantive preceding discussion.

### Problem 3: `/bees-file-issue` has the smaller analog of both

Step 4 of `/bees-file-issue` mutates project docs at filing time when the
issue surfaces doc divergence. Smaller in scope than `/bees-plan` Step 4
(only fires for divergence-revealing issues, only edits existing claims
rather than adding wholesale sections), but the same conflation of
"observation" with "remediation," and the same coupling of doc updates to
the wrong skill phase.

The Issue body itself is the spec source for `/bees-fix-issue` (no
`reference_materials`, no children, no PRD/SDD pointer). When a thick
discussion produces an Issue, the body's shallow template (`Description /
Current behavior / Expected behavior / Impact / Suggested fix`) loses the
analytical depth that came out of the discussion.

## Decisions and rejected alternatives

The design landed here through several iterations during the planning
conversation. Capturing them so downstream agents don't re-litigate:

### Decision: Adopt apiary's Spec Bee + `reference_materials` pattern

`reference_materials` on the bees CLI accepts arbitrary resolvers, not
just `file-path`. Apiary uses `[{"value":"<idea-bee-id>","resolver":"bees"}]`
to point a Plan Bee at an Idea Bee whose children are the PRD and SDD
tickets. We adopt the same pattern (renaming "Idea" to "Spec" for our
usage — we don't have apiary's loose-capture phase). This preserves
polymorphism: future GitHub-issue / Linear / external-doc resolvers drop
into the same field with no skill changes.

### Rejected: Body-as-spec (move all rich content into the Plan Bee body)

Initially proposed during the planning conversation. Rejected because it
collapses the `reference_materials` abstraction the bees CLI already
supports. It would tightly couple spec content to the bees body field,
preclude pointing at external systems (GitHub issues, Linear, wikis),
and break parity with apiary. Body-as-spec remains valid as a *fallback*
(Plan Bee body when no Spec Bee exists — e.g., this Plan Bee itself in
its bootstrap-mode authoring), but should not be the default.

### Rejected: File-based per-plan spec (`.quorum/plans/<bee-id>/spec.md`)

Considered as a middle ground between docs-mutation and Spec-Bee-children.
Rejected because the apiary-faithful pattern is simpler conceptually,
already proven, and — critically — files committed to the repo are
*another* form of repo side-effect. Spec Bee children live in bees
ticket storage, are queryable via the bees CLI, and don't add files
under any project directory.

### Rejected: Child tickets of the Plan Bee directly

Considered: instead of a separate Spec Bee, attach PRD/SDD as `t1`
children of the Plan Bee alongside Epics. Rejected because the Plans
hive's `t1` slot is already `Epic/Epics`, and overloading it to also
carry doc-typed children creates title-disambiguation complexity. A
separate Specs hive with its own `t1=Doc/Docs` configuration is cleaner
and matches apiary's hive-shape parity.

### Rejected: Hybrid file-or-ticket mode in /bees-plan

Considered: default to file-based, allow user-supplied
`--reference-materials` to override. Rejected as overkill for now —
easy to add later once we know what user-supplied pointer flows actually
look like (e.g., once a GitHub-issue resolver exists). Adding it now
expands surface area for hypothetical future requirements.

### Decision: Separate `/bees-write-prd` and `/bees-write-sdd` skills, with `/bees-plan` delegating

Rather than inlining all spec-authoring logic into `/bees-plan`, factor
it out. Reasons: (1) re-authoring without re-planning is a real use
case (revise a PRD after learning something during execution); (2)
quality-bar prose lives in one place per skill; (3) `/bees-plan` shrinks
substantially and becomes maintainable; (4) mental-model parity with
apiary's `/write-prd` + `/write-srd`. Default user experience is
unchanged (still type `/bees-plan`) — the delegation is via the Skill
tool, invisible to the user.

### Decision: Keep `/bees-plan-from-specs` and the Scoped-marker machinery

The redesign does NOT remove `/bees-plan-from-specs` or the
Scoped-marker / `scoped_marker_resolver.py` infrastructure. That flow
serves users who author cumulative PRD/SDD on disk by hand (or via
external tooling); it remains valid. The change is only that
`/bees-plan` no longer emits markers (because it no longer co-mingles
feature content into shared cumulative docs). The PM and breakdown
skills' marker handling stays for the file-resolver path.

### Decision: `doc-writer` agent owns post-implementation cumulative-doc updates

The redundancy was: today's `/bees-plan` writes feature design into
SDD speculatively, AND the `doc-writer` agent already updates SDD
during execution based on the actual diff. Two writes for the same
content, with the speculative one biasing the post-impl version. We
keep the post-impl write (anchored to what was actually built) and
drop the speculative one. `doc-writer`'s responsibility expands to
include appending `### Feature: <title>` subsections to the cumulative
PRD/SDD docs after implementation lands.

### Decision: Two statuses for Specs hive (`drafted`, `ready`), not four

Apiary uses the same 4-status ladder (`larva → pupa → worker → finished`)
for both Ideas and Plans. For us, a spec doc has only two meaningful
states — being-written vs ready-to-be-referenced — and apiary's
`worker`/`finished` for spec docs are conformance-driven rather than
semantically meaningful. We already break uniformity for Issues
(`open → done`), so per-hive status sets are precedented.

### Decision: Preserve transcript via structured body sections, not literal transcript persistence

Tempting to dump the planning transcript somewhere, rejected — transcripts
are noisy, hard for cold-start agents to consume, no clean storage
location. The structured distillation (Decisions / Rejected alternatives
/ Background / Constraints sections in PRD/SDD bodies) is what matters;
the transcript is just the medium for arriving at the distillation.

### Deferred: `/bees-spec-review` skill (apiary `/req-review` analog)

Quality-review pass over PRD/SDD ticket bodies, parallel to our existing
`/bees-code-review`, `/bees-test-review`, `/bees-doc-review`. Useful
eventually, but separable from the bug fix this Bee delivers. The
quality bar is already enforced by `/bees-write-prd` / `/bees-write-sdd`'s
own checklists plus the user-as-reviewer gates in `/bees-plan`.
Deferred to a follow-up Issue filed as part of this Bee's commit.

### Deferred: `/bees-file-issue --reference <url>` external-reference mode

A `/bees-file-issue --from-github <url>` (or generic `--reference <url>`)
mode that creates a thin wrapper Issue with the URL in
`reference_materials`. Symmetric with `/bees-plan-from-specs`.
Real gap, but separable from this Bee's bug fix. Deferred to a
follow-up Issue.

## Acceptance criteria

- `/bees-plan` no longer writes to `docs/prd.md`, `docs/sdd.md`, or the
  README. Running it on a Plan that's never executed leaves project docs
  untouched.
- `/bees-plan` creates a Spec Bee with PRD and SDD `t1=Doc` child tickets,
  plus a Plan Bee with Epic children whose `reference_materials` is
  `[{"value":"<spec-bee-id>","resolver":"bees"}]`.
- New skills `/bees-write-prd` and `/bees-write-sdd` exist as composable
  sub-skills (invokable solo for spec revisions, also invoked inline by
  `/bees-plan`).
- `/bees-plan` distills pre-invocation conversation context into the
  PRD/SDD child tickets when invoked mid-conversation, instead of
  restarting discovery.
- PRD and SDD child-ticket bodies include explicit sections for
  decisions, rejected alternatives, and rationale (not just requirements).
- `agents/pm.md` and `skills/bees-breakdown-epic/SKILL.md` perform two-hop
  lookup: read `reference_materials`, follow the `bees` resolver to the
  Spec Bee, walk the Spec Bee's children for PRD/SDD content. Existing
  `file-path` resolver path and body-as-spec fallback remain functional.
- `agents/doc-writer.md` is responsible for appending/updating
  `### Feature: <title>` subsections in the cumulative project PRD/SDD
  post-implementation, reflecting what was actually built.
- `/bees-file-issue` Step 4 no longer mutates docs; instead, doc
  divergence observations are captured in a `## Doc divergence noted`
  section in the Issue body for `/bees-fix-issue`'s doc-writer to act on.
- `/bees-file-issue` is mid-conversation aware (no re-asking discovery
  questions when context exists) and supports optional `## Background and
  rationale` / `## Decisions and rejected alternatives` sections in the
  body template.
- `/bees-setup` colonizes the Specs hive on new repos and detect-and-adds
  it on existing repos; `/bees-execute`, `/bees-fix-issue`, and
  `/bees-breakdown-epic` hard-fail with `Run /bees-setup first.` when the
  Specs hive is missing.
- `/bees-plan-from-specs` continues to work unchanged for the file-based
  PRD/SDD path (regression-tested by inspection).

## Anticipated doc impact (post-implementation)

When this Bee executes, the `doc-writer` agent (per the new responsibility
in Epic 6) will need to update quorum's own cumulative docs to
reflect what was built:

- `docs/prd.md` — add a new `### Feature:` subsection describing the
  Spec Bee + reference_materials pattern, the new write-prd/write-sdd
  skills, the redesigned planning flow, and the file-issue redesign.
- `docs/sdd.md` — add a new `### Feature:` subsection describing the
  data-model changes (Specs hive), the two-hop reference_materials
  resolution, the doc-writer's expanded responsibility.
- `README.md` — update the skill catalog table to add `/bees-write-prd`
  and `/bees-write-sdd`; update the workflow diagram to reflect the
  Spec Bee creation step and reference_materials pointer; update the
  upgrading-from-older-versions section to cover the Specs-hive addition.
- `docs/doc-writing-guide.md` — update the "Reference materials" entry
  to document the `bees` resolver usage; update the Scoped-marker
  contract section to clarify it now applies only to
  `/bees-plan-from-specs` flows.

These are anticipated only — actual doc edits happen post-implementation
via doc-writer, not at plan time. Listed here so the doc-writer subagent
has a starting checklist when Epic 6 executes.

## Out of scope

- A `/bees-spec-review` analog of apiary's `/req-review` (deferred to
  follow-up Issue).
- A `/bees-file-issue --from-github <url>` (or generic `--reference <url>`)
  external-reference mode (deferred to follow-up Issue).
- Migrating the existing Plan Bees `b.5tm`, `b.9xr`, `b.gar`, `b.kw3` to
  the new Spec Bee structure (they remain on the old shape; new flow
  applies forward).
- Building a GitHub-issue resolver or any other new resolver (the design
  accommodates them via the existing `reference_materials` abstraction;
  concrete resolvers are separate work).
- A formal Issue→Plan promotion path (the manual workaround — close
  Issue, file Plan referencing it — remains).

## Bootstrap-mode note

This Plan Bee was authored in `/bees-plan` "bootstrap mode" — Step 4 was
explicitly skipped because performing doc mutations at plan time is
exactly the bug being fixed. `reference_materials` is empty (no Spec Bee
yet — Spec Bee creation is what Epic 1 enables). The Plan Bee body itself
serves as the authoritative spec source until Epic 4 lands and the new
skills are available; the PM agent's existing body-as-spec branch (in
`agents/pm.md`) handles this correctly.
