"""Routing-decision invariants shared by the two orchestrators.

Regression test for Issue b.nn8. The Issue replaced the `(num-paths,
max-depth)` routing table in `### Orchestrator discipline: routing review
findings` — which gated **every** multi-path finding — with a two-step
pick-then-route procedure: Step 1 the orchestrator picks the highest-quality
fix path, Step 2 a six-row first-match-wins table that fires a gate only where
the decision is genuinely the user's (a mechanism, a scope/contract move, a
silent narrowing, an unknown depth, or `re-architect`). The rewrite landed in
BOTH `/quo-fix-issue` and `/quo-execute` — including the post-completion
reviewer prompt each of them embeds, which challenges the picks the
orchestrator now makes ungated — and reaches eight more shipped artifacts:

  - `skills/quo-engineer-review/SKILL.md`, which emits the
    `[introduces-mechanism]` tag row 2 keys on and constrains what the routing
    parses;
  - the four other emitters of a `[preferred]` fix-path line, whose closing
    clause tells each of them that an absent `[preferred]` is valid —
    `skills/quo-test-writer-review/SKILL.md`,
    `skills/quo-doc-writer-review/SKILL.md`,
    `skills/quo-spec-review/SKILL.md`, and `skills/quo-plan/SKILL.md`;
  - `agents/code-reviewer.md` and `agents/pm.md`, which relay the
    `[introduces-mechanism]` tag to the orchestrator (and, for the PM, read the
    compromise tracker the ungated picks are recorded in);
  - `agents/analyst.md`, the sole site the other four citers point at for what
    "introduces a mechanism" means.

The failure modes pinned here:

  1. **Mirror drift between the two orchestrators.** The table, its row order,
     the tracker `Decision` enum value, and the post-completion PHASE blocks are
     mirrored prose with no shared carrier. The two files are edited
     independently, so a one-sided edit is silent.

  2. **Anchor drift between the writer and the reader of the `Decision`
     value.** PHASE 3 of the post-completion prompt matches tracker entries by
     the wording around the substituted path letter. If the tracker's enum value
     and PHASE 3's matcher drift apart, PHASE 3 matches nothing and the only
     surface that challenges an ungated orchestrator pick goes quietly dead.

  3. **A routing path from a `blocker` to Defer or Accept.** The severity rule
     is the load-bearing half of "gate less": the orchestrator may now dispatch
     its own pick without asking, so the one thing the gates must never offer is
     a way to shelve a blocker. Every choice list, both tracker triggers, the
     PM's deferral-destination contract, and PHASE 2 of the post-completion
     prompt each carry one end of that rule; any of them can be reworded back.

  4. **A broken `[introduces-mechanism]` chain.** The tag is row 2's *primary*
     signal (orchestrator-side detection is only the fallback), and it crosses
     three files between emitter and consumer. A relay bullet dropped in either
     role file silently demotes every tagged path to the fallback reading. The
     chain has a fifth link that is not an emitter or a relay but a *citation*:
     four artifacts define "introduces a mechanism" by pointing at
     `agents/analyst.md` rather than restating it, so the definition site is
     load-bearing for both row 2's primary signal and its fallback reading.

  5. **A half-landed `blocker` Defer-with-narrowing branch.** A `blocker` is
     never accepted, and reaches Defer only when the fix path it needs
     introduces a mechanism serving a case outside the unit's stated defect —
     and then only paired with a narrowing that still covers that defect. That
     one conditional branch has six readers — part (c)'s two-condition rule and
     its coverage guard, the file-first / dispatch-directly pairing order, part
     (d)'s mirror of the same guard, the mechanism-row default's severity
     qualification, Trigger A's narrowing record, and PHASE 2's third violation
     shape — each a separate paragraph in a separate part of two separate
     files. Any one left behind turns the branch into a route that shelves a
     blocker, drops the narrowing, or records neither.

  6. **A resurrected composed path.** An earlier revision let Step 1 compose a
     fix path no reviewer enumerated. That allowance was stripped: the pick is
     always one of the enumerated paths, and an incomplete menu is made visible
     by gating rather than absorbed by the orchestrator writing its own path.
     The allowance reached **seven** sites in each skill — the section lead's
     never-invent carve-out, Step 1's branch, the completeness definition's
     row-4 exemption, both gates' presentation rules, the render step's
     tracker-absent clause, and Trigger C's entry substitution — so a
     half-reverted edit is what a residue guard has to catch.

`docs/sdd.md` is deliberately **not** pinned here. It carries the same
`Decision` enum and is updated in the Doc Writer's lane, which runs concurrently
with this one; pinning it would make this module's result depend on lane timing.
The skills are the shipped artifacts and are the contract that matters at run
time.
"""

import re

import pytest

from conftest import (
    AGENT_ANALYST,
    AGENT_CODE_REVIEWER,
    AGENT_PM,
    QUO_DOC_WRITER_REVIEW,
    QUO_ENGINEER_REVIEW,
    QUO_EXECUTE,
    QUO_FIX_ISSUE,
    QUO_PLAN,
    QUO_SPEC_REVIEW,
    QUO_TEST_WRITER_REVIEW,
    REPO_ROOT,
    heading_section,
    read,
    routing_section,
    shipped_artifacts,
)

ORCHESTRATORS = (
    QUO_FIX_ISSUE,
    QUO_EXECUTE,
)

# --- Part slicing ------------------------------------------------------------

# The routing section is a lettered run of parts (a)..(g), each led by a bolded
# marker. Reference prose spells the letters unbolded ("the gate in part (c) or
# (d)"), so only the bolded form starts a part.
PART_MARKER = re.compile(r"\*\*\((?P<letter>[a-z])\)")
PART_LETTERS = list("abcdefg")

# --- Part (a): the routing table --------------------------------------------

# One row per condition, in evaluation order. First match wins, so the ORDER is
# as load-bearing as the contents: rows 2-4 must precede row 5 or a
# mechanism-introducing path with a shallow depth tag reaches row 6 and is
# dispatched ungated, and row 1 must come first or parts (e)/(f) stop being
# reachable.
EXPECTED_ROUTING_ROWS = (
    (
        "1",
        "The finding carries no depth tag, or a malformed severity/depth tag",
        "Treat as `re-architect` → gate (d)",
    ),
    (
        "2",
        "The chosen path carries the reviewer's `[introduces-mechanism]` tag, "
        "or introduces a mechanism by the orchestrator's own reading (below)",
        "Scope-bounding gate (c)",
    ),
    (
        "3",
        "The chosen path moves a published contract surface beyond what this "
        "unit's ticket states, or is breaking for existing consumers",
        "Scope-bounding gate (c)",
    ),
    (
        "4",
        "The chosen path is narrower than the smallest internally-consistent "
        "complete fix — it leaves the stated defect partly unfixed",
        "Scope-bounding gate (c)",
    ),
    (
        "5",
        "The chosen path's depth tag is `re-architect`",
        "Routing-decision gate (d)",
    ),
    (
        "6",
        "Otherwise",
        "Dispatch the chosen path, no gate",
    ),
)

# Cells of the retired `(num-paths, max-depth)` table. Each is distinctive
# enough that its reappearance means the old table came back rather than that
# some unrelated prose happens to match.
#
# This constant and the two below are **first-generation** retirements, removed
# by `6fc1c28` and therefore present only at `6fc1c28~1` (= `91eb07d`) — NOT at
# `6fc1c28`, which is the reference for the module's second-generation
# retirements. See the reference-points note above `RETIRED_COMPOSE_SHAPES`
# before checking any of these against a revision.
RETIRED_TABLE_SHAPES = (
    "Number of fix paths",
    "Maximum depth across paths",
    "Auto-dispatch the implementer",
    "User gate before dispatching",
)

# The retired table's catch-all row — every multi-path finding to a gate — which
# is the behavior the Issue was filed against. Matched against a
# whitespace-normalized section so column padding cannot hide it.
RETIRED_MULTIPATH_ROW = "| > 1 | (any) | User gate before dispatching |"

# The retired routing *input*. The orchestrator no longer derives a tuple from
# the finding; it picks a path and routes on that path's properties.
RETIRED_ROUTING_TUPLE_TOKEN = "num-paths"

# --- Part (c)'s count of the rows that reach it ------------------------------

# Part (c) opens by counting its own entry conditions: part (b)'s scope-bound
# behavior, plus every row of part (a) that routes to gate (c). The count is the
# half of that sentence that goes stale silently — the same defect
# `CLOSE_OUT_ROUTER_COUNT_WORD` pins for the close-out's router list — so it is
# derived from the table on disk rather than hardcoded: a future row routed to
# gate (c) moves the derived word off "four" and fails against the unrecounted
# prose.
#
# Only the count clause is pinned, and not because the sentence diverges — the
# two skills' copies are byte-identical today, the execute-only tail this
# comment used to cite having gone with the gate-fires-for-a-blocker change.
# The clause is pinned because it is the **derived half** of the fact: it is
# what this module computes from the table and compares, while the rest of the
# sentence is prose no computation produces. Widening the pin to the whole
# sentence would convert a staleness guard into a second mirror test, which
# `routing_parts` already covers, and would make an unrelated reword of the
# surrounding prose fail a check about the count.
SCOPE_GATE_ROUTING_CELL = "gate (c)"
SCOPE_GATE_NON_ROW_ENTRY_CONDITIONS = 1  # part (b)'s scope-bound behavior
COUNT_WORDS = {
    1: "one",
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
    7: "seven",
}

# --- The three definitional paragraphs ---------------------------------------

# Step 1 and the two definitions it leans on are the whole of the orchestrator's
# judgment half. They are duplicated prose with no shared carrier, so each is
# pinned twice over: the load-bearing clauses by name (so a failure says which
# clause went missing) and the paragraphs against each other (so a reword has to
# land in both skills or fail here).
STEP_1_LEAD = "**Step 1 — pick.**"
HIGHEST_QUALITY_LEAD = '**What "highest-quality" means.**'
MECHANISM_MEANING_LEAD = '**What "introduces a mechanism" means.**'

# The paragraph that closes part (a): what row 6 does when it fires, why the row
# order is what it is, and the part-(g) ordering rule the test below reads out of
# it. Its two copies diverge only in the two `Section <n>` references each skill
# numbers for itself, so it is mirrored whole rather than clause by clause.
ROW_SIX_LEAD = "Row 6 dispatches a fresh ephemeral implementer Agent"

# Normalizes every `Section <n>` / `Section <n>.<m>` reference to one token, so
# prose mirrored across the two skills can be compared byte-for-byte despite
# each skill numbering its own sections.
#
# Its live consumer is the **row-6 paragraph**, which cites two sections that
# differ per skill (Section 4 / Section 7.5 in fix mode, Section 3 / Section 6.5
# in execute mode). Step 1 also runs through it but no longer needs to: Step 1
# carries no numbered cross-reference in either skill today — it once pointed at
# the compromise-tracker section, in the sentence the composed-path branch took
# with it — so the normalization is currently a no-op there. It is kept on that
# comparison deliberately, as the cheap direction of the trade: a Step 1 that
# later gains a section reference keeps mirroring, whereas removing the call now
# means a future one-sided reference reads as drift.
#
# What the normalization cannot mask, on either paragraph, is a divergence
# outside a `Section <n>` token — which is what both mirror tests are for.
SECTION_REF = re.compile(r"Section \d+(?:\.\d+)?")
SECTION_REF_TOKEN = "Section <n>"

# Step 1's closure rule and what it does when the menu is short. The pick is
# drawn from the reviewer's enumeration and nothing else; an incomplete menu is
# surfaced by routing the most complete enumerated path to a gate, never
# absorbed by the orchestrator writing a path of its own.
STEP_1_ENUMERATION_IS_CLOSED = (
    "**The pick is always one of the paths the reviewer enumerated.**"
)
STEP_1_INCOMPLETE_MENU_CLAUSES = (
    "When *no* enumerated path is the smallest internally-consistent complete "
    "change — every one of them leaves the stated defect partly unfixed — pick "
    "the most complete of them anyway.",
    "rows 2, 3 and 4 all send it to gate (c), where `Fix properly now` "
    "dispatches the complete fix; the exception is a finding whose depth tag "
    "is absent or malformed, which row 1 sends to gate (d) instead",
    # The accounting of what the gating actually buys, in two halves. Stated as
    # bare "the menu becomes visible" the clause overclaims: the visibility is
    # in-session only, and on `Fix properly now` — the branch the gate
    # recommends — nothing is written down at all. Both halves are pinned
    # because either alone misreports the guarantee. Without the first, the
    # in-session visibility this routing does deliver goes unstated; without
    # the second, a reader takes the post-completion review to see every
    # under-enumerated finding, when it sees only the shelved ones.
    #
    # The durable half names BOTH shelving triggers, not just Trigger A. Naming
    # only the Defer branch understates the record by exactly one branch — an
    # accepted limitation is a Trigger B entry and reaches the same review — so
    # a constant stopping at Trigger A would pin a narrower claim than the
    # prose makes and would go stale against the honest one.
    "Either way the incomplete menu becomes visible **in session**: a gate "
    "fires where it otherwise would not have, and the user sees the menu it "
    "fired on.",
    "A **durable** record reaches the post-completion review only when the "
    "user defers or accepts — Trigger A on `Defer to follow-up Issue`, Trigger "
    "B on `Accept the limitation` — while `Fix properly now` writes none, so "
    "an incomplete menu resolved that way leaves no trace past the run.",
    "the orchestrator does not absorb the gap by writing a path of its own",
)

# The retired compose branch, by its most distinctive surviving shapes.
#
# It reached **seven** sites in each skill: the section lead's never-invent
# carve-out, Step 1's branch, the completeness definition's row-4 exemption,
# gate (c)'s context line, gate (d)'s presentation rule, the render step's
# tracker-absent clause, and Trigger C's entry substitution. (Seven *sites*, not
# seven paragraphs everywhere — in execute mode the Trigger C site spans two.)
#
# The shapes below do NOT map one-to-one onto those sites, and reading them that
# way is what previously left a site uncovered: three of the six live in the
# single Step 1 paragraph, while `composed path` alone spans five sites. What
# covers the set is the six shapes **plus** the section-scoped stem scan below —
# the first five sites sit inside the routing section, so the stem reaches them,
# while the render clause and Trigger C sit outside it and are reachable only by
# a fixed shape. That is why `, or was composed` had to be added (round 2's
# blocker) rather than left to the stem.
#
# One acknowledged gap, covered elsewhere: execute mode's Trigger C carve-out
# clause ("never applies when the Step-1 pick was composed") carries none of
# these shapes and sits outside the routing section, so this guard alone would
# miss a revert of it. `RETIRED_TRIGGER_C_SHAPES` catches that paragraph instead
# — verified against the pre-strip prose at `6fc1c28`, where three of its
# entries match that line.
#
# ---------------------------------------------------------------------------
# Reference points for every "what was retired" statement in this module.
#
# Both generations are committed, so **HEAD names neither of them** — a comment
# here that says "at HEAD" is describing prose that no longer exists. There are
# two reference points, because this module pins two distinct retirements:
#
#   * **Retired by `6fc1c28`** (the Issue's original landing) — present only at
#     `6fc1c28~1` (= `91eb07d`), already gone by `6fc1c28`:
#     `RETIRED_TABLE_SHAPES`, `RETIRED_MULTIPATH_ROW`,
#     `RETIRED_ROUTING_TUPLE_TOKEN`, `RETIRED_DECISION_VALUE`. These are the
#     `(num-paths, max-depth)` routing table and its vocabulary.
#   * **Retired by `c9b1651`** (this run's post-completion fix) — present at
#     `6fc1c28`, gone today: `RETIRED_COMPOSE_SHAPES`,
#     `RETIRED_TRIGGER_C_SHAPES`. These are the composed-path allowance and the
#     second Trigger C firing site, both of which `6fc1c28` *introduced*.
#
# So `6fc1c28` is the "before" for the second generation and the "after" for the
# first: checking a first-generation shape against it finds nothing and proves
# nothing. Reach for `6fc1c28~1` there instead.
#
# One idiom note: `RETIRED_MULTIPATH_ROW` is a table row whose columns are
# padded, so it is matched against `squeeze()`d text. A raw substring check
# against either revision finds nothing and is not evidence of absence.
# ---------------------------------------------------------------------------
RETIRED_COMPOSE_SHAPES = (
    "The enumeration is the menu, not a ceiling",
    "**compose** the complete fix",
    "composed path",
    "**One carve-out, and only one:**",
    "orchestrator-composed",
    # The render step's own residue. Its site is a mid-sentence clause with no
    # distinctive vocabulary of its own, so the file-wide scan is what reaches
    # it — `TRACKER_ABSENT_RENDER_CLAUSE` proves the surviving text is right,
    # and this proves the retired text is gone. Neither implies the other: a
    # sentence can carry both halves at once.
    ", or was composed",
)

# The stem is scanned across the whole routing section as a backstop for a
# residue the fixed shapes above would miss. Scoped to that section because the
# stem has legitimate unrelated uses elsewhere in both skills — the hive-commit
# helper note's "decomposing a multi-step shell snippet" is the one that appears
# in both, outside the routing section, and would otherwise fail a file-wide
# scan on every run.
COMPOSE_STEM = re.compile(r"compos", re.IGNORECASE)

# Step 1's tie-break rule: what the reviewer's `[preferred]` token is worth when
# it disagrees with completeness. The Step 1 mirror test above catches only
# one-sided drift — a deletion from both skills leaves the two copies equal and
# passes — so the rule is pinned by name here as well.
#
# Pinned as the whole sentence, not its opening: part (d)'s gate carries a
# near-miss restatement ("... is an **input** to Step 1 and usually coincides
# with the pick"), so a shorter prefix would match in two places and stop
# distinguishing Step 1's copy from the gate's.
STEP_1_PREFERRED_IS_AN_INPUT = (
    "The reviewer's `[preferred]` token is an **input** to this choice, not a "
    "verdict: prefer it when it is also the most complete; when `[preferred]` "
    "marks a narrowing and a fuller path exists that is still the smallest "
    "internally-consistent complete change, take the fuller path."
)

# The section lead's never-invent rule, stated unqualified. With the compose
# branch gone the orchestrator originates no depth at all, so the rule carries
# no carve-out — and the absence of one is the contract, not an omission.
NEVER_INVENT_RULE = (
    "the depth of a path is the reviewer's call, read as emitted, and is the "
    "one classification the orchestrator must never invent"
)

# The two sentences of the mechanism definition that are shared verbatim. The
# rest of that paragraph names each skill's own design source (the Analyst
# directive vs. the Subtask/Task bodies and the PRD/SDD) and legitimately
# differs, so only these are pinned.
MECHANISM_PRIMARY_SIGNAL = (
    "**The reviewer's `[introduces-mechanism]` tag on a fix path is the "
    "primary signal for row 2** — a tagged path routes to gate (c) with no "
    "further judgment. Orchestrator-side detection is the **fallback**, used "
    "only when no tag is present"
)

# --- Trigger C's single firing site ------------------------------------------

# Row 6 is the whole of the ungated route in both skills, and the sentence
# saying so is byte-identical across them and stands as its own paragraph in
# each. It is therefore addressed with `paragraph_starting`, whose exactly-one
# assertion makes that own-paragraph claim true by construction rather than by
# this comment: should the sentence ever be folded back into the trigger's
# paragraph — the shape it briefly had in execute mode — the guard fails and
# says so, instead of a bare containment check passing over the change.
TRIGGER_C_LEAD = "**Trigger C — ungated route (the orchestrator's own path pick).**"
TRIGGER_C_FIRING_SITE = "**Row 6 is this trigger's only firing site.**"
TRIGGER_C_FIRING_SITE_TAIL = "no Trigger C entry is written for it."

# The region ends at the NEXT trigger's lead, not at the firing-site sentence's
# own tail, because Trigger C's prose extends past that sentence and the retired
# prose lived in the part a tail-bounded slice cannot see. In the **pre-strip**
# state (`6fc1c28`) the two skills failed that bound differently, and neither
# failure is a near miss:
#
#   * fix mode HAD the tail, and the cross-skill parenthetical began on the same
#     line just **two bytes** past it (the gap is a space and an open paren), so
#     a tail-bounded slice stopped immediately short of the very text the
#     sibling-name scan exists to find;
#   * execute mode had **no firing-site sentence at all** — its trigger ran
#     straight on through further paragraphs and bullet blocks of site-(2)
#     machinery — so a tail-bounded slice had nothing to anchor on there and
#     would raise rather than under-read.
#
# Bounding on the next lead is also what makes the region survive a paragraph
# being added: whatever Trigger C grows, it grows before Trigger D.
TRIGGER_C_REGION_END = "**Trigger D — "

# The retired second firing site and the cross-skill comparison that justified
# it. Execute mode once collapsed its blocker choice sets to a single choice and
# dispatched those findings ungated, which obliged a second Trigger C site and a
# paragraph in each skill explaining how the other differed. Both gates now fire
# for a blocker in both skills, so the second site is gone — and with it the
# comparison, which is the half that rots silently once only one skill is
# edited.
RETIRED_TRIGGER_C_SHAPES = (
    # The two firing-site counts, one per skill's own retired wording.
    "only firing site in this skill",
    "second firing site",
    # The retired execute-mode trigger's own vocabulary. The two counts above
    # are single clauses, but the machinery they belonged to was not: it ran on
    # past them through further paragraphs and bullet blocks — a second site
    # class, its `Rationale` additions, field substitutions for its sub-cases,
    # and a carve-out scoped to site (1). A half-revert that restores that
    # machinery without restoring either count would pass a count-only list
    # while the second ungated route is back in the prose, so the vocabulary is
    # pinned alongside. Every one of these is verified present in the
    # **pre-strip** prose at `6fc1c28` and absent from both skills today.
    "It fires at **two** sites",
    "site (2)",
    "gateless `blocker` dispatch",
    "Field substitution on site (2)",
    "The lone-`trivial-tweak` carve-out applies on site (1) only.",
)
OTHER_ORCHESTRATOR_NAME = {
    QUO_FIX_ISSUE: "/quo-execute",
    QUO_EXECUTE: "/quo-fix-issue",
}

# The two places the state-externalization checkpoint reasons about an absent
# tracker file. Both have to agree with Trigger C about which picks oblige an
# entry, or the checkpoint reports a gap for an entry Trigger C forbids.
CHECKPOINT_GAP_QUALIFIER = (
    "an ungated path pick **that Trigger C requires an entry for** was "
    "dispatched"
)
# Extended through the em-dash continuation deliberately. The pre-change
# sentence read "... among two or more paths, or was composed — Trigger C's
# ...", so a constant stopping at "two or more paths" is a strict PREFIX of the
# old text and matches it too — the guard would have passed against the very
# prose the removal was supposed to retire, leaving this site uncovered. Reading
# through the em-dash is what makes the constant discriminate: the old sentence
# has ", or was composed" between the two halves, so the extended string is
# absent from it.
TRACKER_ABSENT_RENDER_CLAUSE = (
    "an ungated path pick appends an entry whenever the pick was among two or "
    "more paths — Trigger C's lone-`trivial-tweak` carve-out is the only "
    "ungated route that appends nothing"
)

# --- The `[preferred]` closing clause, in five emitters ----------------------

# Every skill that emits a fix-path line documents `[preferred]` the same way,
# and the clause below is the one that tells the emitter an absent `[preferred]`
# is not an omission. It has no shared carrier: four review skills plus
# `/quo-plan` carry their own copy, and `/quo-plan`'s is hard-wrapped, so the
# comparison runs over whitespace-squeezed text.
PREFERRED_CLOSING_CLAUSE = (
    "When no path carries `[preferred]`, that is fully valid — the consumer "
    "makes its own pick either way, and `[preferred]` is only an input to it."
)
PREFERRED_EMITTERS = (
    QUO_ENGINEER_REVIEW,
    QUO_TEST_WRITER_REVIEW,
    QUO_DOC_WRITER_REVIEW,
    QUO_SPEC_REVIEW,
    QUO_PLAN,
)

# --- `/quo-engineer-review`'s compatibility constraint ------------------------

COMPAT_CONSTRAINT_LEAD = (
    "**Compatibility constraint — the subsection is narrative, not a routing "
    "surface.**"
)
# Every input the orchestrator's routing actually reads. The constraint's job is
# to enumerate them exhaustively, so the tokens are pinned individually and the
# closing "nothing else" alongside them; the sentence around them is free to be
# reworded.
COMPAT_ROUTING_INPUTS = (
    "severity tags",
    "enumerated fix paths",
    "`[depth:<...>]`",
    "`[preferred]`",
    "`[introduces-mechanism]`",
    "and nothing else",
)

# --- Tracker `Decision` enum and its post-completion reader -------------------

DECISION_ENUM_LEAD = "- **Decision:** <one of:"
DECISION_PICK_VALUE = "Orchestrator picked path (x) — highest-quality"

# A **first-generation** retirement, like the table shapes near the top of this
# module: removed by `6fc1c28`, so it is present only at `6fc1c28~1`
# (= `91eb07d`) and not at `6fc1c28`. See the reference-points note above
# `RETIRED_COMPOSE_SHAPES`.
RETIRED_DECISION_VALUE = "Auto-routed (a) per single-path refactor-locally rule"

# The two halves of the enum value that survive the per-entry letter
# substitution. PHASE 3 must match on exactly these, since the letter varies.
#
# **Derived from the value, not restated.** The enum's `(x)` slot is where the
# writing step substitutes the chosen path's own letter, so the two halves are
# by definition what remains once `x` is removed — and splitting on it makes
# that relationship structural. Two literals would be a second copy of the
# value, free to drift out of agreement with it while both still looked right;
# this way a reword of `DECISION_PICK_VALUE` carries the anchors with it, and
# the subsumption the PHASE 3 test relies on holds by construction rather than
# by coincidence.
#
# The single-`x` check runs **before** the split, not after: a value with two
# `x`s (or none) makes the unpack itself raise `ValueError`, so an assert placed
# below could never run and its diagnostic would never print. Ordering it first
# is what turns "too many values to unpack" — which names neither the constant
# nor the reason — into a message that says which value broke and why the `x`
# matters.
assert DECISION_PICK_VALUE.count("x") == 1, (
    "DECISION_PICK_VALUE must contain exactly one 'x' — the letter placeholder "
    f"the PHASE 3 anchors are split on; got {DECISION_PICK_VALUE!r}"
)
DECISION_PICK_PREFIX, DECISION_PICK_SUFFIX = DECISION_PICK_VALUE.split("x")

# --- The SR-6.7 recovery gate's name ------------------------------------------

# Trigger D's prose says it "anchors to those gates by name", which makes the
# name a cross-reference rather than a label: step 7 defines the gate, Trigger D
# names it twice (once in the lead that claims the anchoring, once as the
# sub-heading carrying that gate's write logic), and nothing but the string
# itself links the three. Rename one and Trigger D's claim quietly becomes false
# — the write logic would sit under a heading no gate answers to.
SR_6_7_GATE_NAME = "SR-6.7 ungated-route recovery gate"
SR_6_7_GATE_SITES = {
    "step 7's bullet heading": f"- **{SR_6_7_GATE_NAME}.**",
    "Trigger D's sub-heading": f"- **{SR_6_7_GATE_NAME}:**",
}

# The name this gate carried before it was renamed for what it recovers rather
# than for the misjudgment that reaches it. Pinned as an absence because the old
# name is the plausible thing to write from memory.
#
# Scoped deliberately: `(depth misjudgment)` survives inside the tracker's
# `Decision` value and `depth-misjudgment override` survives as a gloss on that
# value — both deliberate, both retained, and neither is this gate's name. The
# absence check keys on the full retired **gate name** so it cannot catch them.
RETIRED_SR_6_7_GATE_NAME = "depth-misjudgment recovery gate"

# Trigger D's lead, for addressing the third site (the one with no bullet form
# of its own). Aliased rather than restated: Trigger C's region ends exactly
# where Trigger D's paragraph begins, so the two are one string by construction
# and a reword of the lead moves both readers together.
TRIGGER_D_LEAD = TRIGGER_C_REGION_END

# --- Severity rule -----------------------------------------------------------

# Both gates lead their severity rule with this prefix, and it is the longest
# string common to all four copies — so it is what the mechanical
# every-shelving-choice-is-qualified scan below keys on.
#
# What varies, and where: the remainder differs **per gate** (part (c) states
# the never-accept / defer-only-with-a-narrowing rule, part (d) states that a
# blocker's Defer route is conditional), and part (d)'s paragraph additionally
# differs **per skill** past its lead — fix mode names the Analyst re-dispatch
# among the choices the `(Recommended)` marker must be withheld from, execute
# mode carries the zero-path **free-text** branch in its place. Both skills'
# part (d) name the zero-path case; what differs is how each resolves it (fix
# mode sends it to the Analyst re-dispatch, execute mode fires the gate on an
# empty per-path list and takes a prose direction), which is the same
# distinction `EXECUTE_ZERO_PATH_GATE_FIRES` records. Part (c)'s paragraph is byte-
# identical across the two skills today; the execute-only "and fires no gate
# here" tail this comment used to cite is gone, because that gate now fires for
# a blocker in both skills. The per-gate leads are pinned in full by
# SCOPE_GATE_BLOCKER_RULE and ROUTING_GATE_BLOCKER_RULE.
BLOCKER_EXCLUSION_LEAD = "**Severity rules the choice set"

SCOPE_GATE_BLOCKER_RULE = (
    "**Severity rules the choice set — a `blocker` can never be accepted, and "
    "can be deferred only with a narrowing.**"
)
SCOPE_GATE_ACCEPT_UNREACHABLE = (
    "**`Accept the limitation` is unreachable, unconditionally**"
)
ROUTING_GATE_BLOCKER_RULE = (
    "**Severity rules the choice set here too — a `blocker`'s Defer route is "
    "conditional.**"
)

# The paragraph lead, for addressing part (d)'s severity paragraph specifically
# rather than part (d) at large. Shorter than the full rule above because it is
# used as a `paragraph_starting` anchor, which matches on a line's opening.
ROUTING_GATE_SEVERITY_LEAD = "**Severity rules the choice set here too"
ROUTING_GATE_CONDITIONAL_DEFER = (
    "the `Defer to follow-up Issue` choice below is **unreachable unless part "
    "(c)'s two conditions both hold**"
)

# Execute mode's zero-path **free-text** branch, and the reason
# `TRIGGER_C_FIRING_SITE` is true here. Both skills' part (d) name the zero-path
# case; this is how execute mode resolves it.
# A row-1 blocker can arrive with no fix path enumerated at all —
# nothing for the per-path list to hold — and the shape that resolves it is a
# gate that fires anyway on an empty list, taking the user's prose direction
# through the free-text slot. Both halves are load-bearing and neither implies
# the other: without the first the gate would have nothing to present and the
# natural reading is that it does not fire, which is exactly the "gate declines
# to fire, so dispatch ungated" shape the retired second Trigger C firing site
# existed to record; without the second, a user-directed dispatch looks like an
# ungated route and Trigger C's row-6-only claim becomes false in execute mode.
# QUO_EXECUTE-only: fix mode routes a zero-path blocker to its Analyst
# re-dispatch, so it has no free-text branch to exempt.
EXECUTE_ZERO_PATH_GATE_FIRES = (
    "the gate still fires on it: the per-path list is simply empty"
)
EXECUTE_USER_DIRECTED_IS_NOT_UNGATED = (
    "a user-directed fix is not an ungated route, so Section 6.5's **Trigger "
    "C** writes nothing for it"
)

# Part (d)'s own Defer bullet reads "rather than picking a path now" — nothing
# ships against the finding this round. That is right for a `suggestion` or
# `nit` and flatly wrong for a `blocker`, whose deferral is only legitimate
# paired with a narrowing dispatched the same round. The gate carries the
# correction explicitly rather than leaving a reader to reconcile the bullet
# with part (c)'s rule, because the bullet is what the orchestrator reads when
# it assembles the choice. Part (c) carries the same reconciliation for its own
# copy of that bullet — see `SCOPE_GATE_DEFER_BULLET_RECONCILIATION`.
ROUTING_GATE_BLOCKER_PAIRING = (
    "**When it is offered to a blocker here, the deferral is paired with a "
    "narrowing dispatched this round, never shipped alone** — the `Defer to "
    "follow-up Issue` bullet's \"rather than picking a path now\" describes the "
    "non-blocker case, where nothing ships against the finding this round."
)

# Part (c)'s floor for a `blocker`. The two members differ per skill — fix mode
# routes a wrong-directive blocker back to the Analyst, execute mode has no
# Analyst and offers `Cancel` (stop the run and re-plan) instead — so the lead
# is mirrored prose and the pair itself is per-skill. Without the floor, a
# blocker whose Defer conditions do not both hold reaches a gate with one
# choice, which is a dispatch wearing a gate's clothes.
BASE_PAIR_LEAD = "**The base pair is always offered.**"
BASE_PAIR_MEMBERS = {
    QUO_FIX_ISSUE: (
        "a `blocker` gets `Fix properly now` and `Re-dispatch the Analyst with "
        "this finding`"
    ),
    QUO_EXECUTE: "a `blocker` gets `Fix properly now` and `Cancel`",
}

# The other half of that per-skill split: where `Cancel` is NOT offered. The two
# statements are not stylistic variants — they scope differently because the
# base pairs differ. Execute mode puts `Cancel` in a blocker's base pair, so its
# rule has to withhold it from the `suggestion` / `nit` set specifically; fix
# mode has no `Cancel` at this gate at all, since the Analyst re-dispatch
# carries the stop-and-re-plan answer instead. Swap either sentence for the
# other and the gate contradicts its own base pair — execute mode would deny a
# blocker the `Cancel` its floor guarantees, or fix mode would advertise a
# choice it never defines.
SCOPE_GATE_NO_CANCEL_RULE = {
    QUO_FIX_ISSUE: "**There is no `Cancel` option at this gate**",
    QUO_EXECUTE: (
        "**There is no `Cancel` option on the `suggestion` / `nit` choice set**"
    ),
}

# The two conditions that open a `blocker`'s Defer route, and the guard that
# closes it again. Both conditions must hold — an `and`, not an `or` — because
# either alone still shelves a blocker: a mechanism serving the stated defect
# cannot be narrowed away, and a non-mechanism path has nothing to defer.
DEFER_THIRD_CHOICE_LEAD = (
    "- **`Defer to follow-up Issue` is added as a third choice *only when "
    "both* of these hold:**"
)
DEFER_CONDITIONS = (
    "(i) the fix path the finding needs **introduces a mechanism**",
    "(ii) that mechanism serves a case **outside this unit's stated defect**",
)

# The branch is row-independent on a `blocker`. Condition (i) tests the fix path
# the finding *needs*, not the path Step 2 routed — so the two conditions can
# both hold on a row-3 or row-4 fire, where nothing about the chosen path
# mentions a mechanism at all. Without this sentence the branch reads as row-2
# only (the mechanism row), which is the reading the mechanism-row default
# paragraph invites, and a blocker that could legitimately defer would be
# handed the base pair instead.
DEFER_ROW_INDEPENDENCE = (
    "**It applies whichever row fired this gate on a blocker — 2, 3 or 4.**"
)

# "It" in that sentence is this: the Defer-plus-narrowing pairing being the
# recommended default. Pinned because a pronoun with no pinned antecedent is a
# sentence whose meaning can change without the sentence changing — reword the
# clause above it and the row-independence rule silently starts qualifying
# something else, while the guard on it still passes.
DEFER_ROW_INDEPENDENCE_ANTECEDENT = (
    "That pairing is then the **recommended default** — mark the choice "
    "`(Recommended)` even on a blocker"
)

# The guard, stated at both gates. Pinned without its trailing punctuation: part
# (c) closes the bolded run with a period inside the emphasis and part (d)
# continues the sentence with a comma outside it, so the shared contract is the
# clause rather than either file's sentence boundary.
NARROWING_COVERAGE_GUARD = (
    "A narrowing may never reduce coverage of the stated defect"
)

# The pairing order. Filing first is what makes the narrowing legitimate: part
# (f) forbids shipping it when the filing failed, so a narrowing dispatched
# before `/quo-file-issue` returned has already shipped by the time that rule
# could withhold it.
DEFER_FILE_FIRST = (
    "**the deferral is paired with the narrowing, never shipped alone**: "
    "**file the follow-up Issue first**, carrying the reviewer's sketched "
    "design **verbatim**, and dispatch the narrowing"
)
DEFER_FILE_FIRST_ORDER = "only once `/quo-file-issue` has returned an Issue ID"

# The narrowing's terminality. Re-entering Step 2 with it would match row 4 —
# narrower than the smallest internally-consistent complete fix — and route it
# back to the gate that just produced it, which is an unbounded loop rather than
# a fix.
NARROWING_DISPATCHED_DIRECTLY = (
    "**Dispatch that narrowing directly, not by re-entering Step 2 with it** — "
    "it is narrower than the complete fix by construction, so Step 2 would "
    "match row 4 and route it straight back to this gate."
)

# Part (d) now carries two independent `(Recommended)` rules — the Step-1 pick's
# per-path marker, and the blocker Defer branch's — so it has to say which wins.
# The two copies diverge mid-sentence (fix mode names the third marker its
# empty-list case would otherwise set), so the shared head and tail are pinned
# rather than the sentence.
ROUTING_GATE_MARKER_PRECEDENCE = (
    "**That `(Recommended)` takes precedence over the per-path marker**: mark "
    "`Defer to follow-up Issue` Recommended and withhold the marker from "
    "**every other choice**"
)
ROUTING_GATE_EXACTLY_ONE_MARKER = "so exactly one choice carries it, as at part (c)."

# The Analyst re-dispatch choice, fix mode only. Its two ends: part (c) defines
# the in-flight-lane sweep, Section 3's Approve branch orders it before Phase A
# re-entry. Execute mode has no Analyst and no counterpart.
#
# The heading below is the container the ordering end must live in. Naming it
# lets each end be asserted against its own section rather than file-wide,
# which is what makes "these two ends are in different places" checkable at
# all — the whole point of the pin.
ANALYST_APPROVE_BRANCH_HEADING = "#### Branch on the user's choice"

# --- Deferred-refinements supersession, fix mode only -------------------------

# The `defer-*` ledger is the Analyst lane's only inter-session carrier: nothing
# downstream reconstructs it (Section 7.5's Step 1 enumerates only tasks still
# active, and its Step 0 walks only the latest Analyst block). So the rule for
# what supersession clears is destructive if stated one clause too wide — and it
# briefly was, until a code review caught it. The narrow rule turns on WHY an
# iteration's tasks are stale: a Revise chain's tasks belong to proposals the
# user rejected in favour of the next, while an earlier *Approve*'s tasks belong
# to an approval that still stands. Both sentences are pinned, because the
# clearing half alone is exactly the over-wide rule that would destroy every
# banked refinement at the first re-fire.
DEFERRED_REFINEMENTS_HEADING = (
    "#### Consume the Analyst's `### Deferred refinements` block"
)
DEFERRED_REFINEMENTS_THIRD_ROUTE = (
    "OR when the user picks Approve after this gate was re-fired from part "
    "(c)/(d)'s `Re-dispatch the Analyst with this finding` choice"
)
DEFERRED_REFINEMENTS_SUPERSESSION_RULES = (
    "**Supersession clears only the `defer-*` tasks of an iteration the user "
    "never approved**",
    "**`defer-*` tasks created at an earlier *Approve* survive a later "
    "re-fire**",
)

# The sweep obligation survives Revise iterations. The re-fire lands on a gate
# whose Revise branch loops back through a fresh Analyst, so an operator can
# Revise once or twice before Approving — and read narrowly ("on Approve of the
# re-dispatched Analyst's return"), the sweep then never runs on the Approve
# that actually re-enters Phase A. That failure is silent in the worst way: the
# writer lanes stay `pending`, and part (g)'s Engineer-dispatch precondition
# wedges the next Engineer on tasks nothing will ever clear.
ANALYST_REDISPATCH_SWEEP_SURVIVES_REVISE = (
    "This holds on **every** Approve reached from that re-fire — including a "
    "later Approve after one or more Revise iterations on it — not only on an "
    "Approve of the re-dispatched Analyst's first return."
)
ANALYST_REDISPATCH_SWEEP_SPEC = (
    "**On `Approve`, re-enter Section 4 Phase A with the revised directive — "
    "but close out this Issue's open TaskList tasks first**"
)
ANALYST_REDISPATCH_SWEEP_ORDERING = (
    "**When this gate was re-fired from part (c)/(d)'s `Re-dispatch the "
    "Analyst with this finding` choice**, run that choice's in-flight-lane "
    "TaskList sweep"
)
ANALYST_REDISPATCH_SPEC_POINTER = (
    "that bullet in `### Orchestrator discipline: routing review findings` is "
    "the specification, this is only the ordering"
)

# The discard is wider than the sweep. The sweep can only reach lanes that have
# an active TaskList task, and two classes of finding have none: the siblings
# co-emitted by the reviewer return that fired this gate (they live in the
# orchestrator's context on no task at all) and any lane that returned between
# the gate answer and the sweep (already `completed`). Read as "discard what the
# sweep caught", both classes get routed — against the directive the
# re-dispatch just superseded, which is the one thing this branch exists to
# prevent. Head and tail are pinned; the two parenthetical classes between them
# are the reasoning.
ANALYST_REDISPATCH_DISCARD_SCOPE = (
    "**That discard covers every finding raised under the superseded "
    "directive, not only the lanes this sweep caught in flight**",
    "Route none of them; the revised directive is what the next round reviews "
    "against.",
)

DEFER_BULLET = "- **Defer to follow-up Issue**"
ACCEPT_BULLET = "- **Accept the limitation**"
SHELVING_BULLETS = (DEFER_BULLET, ACCEPT_BULLET)

# Each orchestrator's routing section offers exactly three shelving choices
# today: part (c) offers Defer and Accept, part (d) offers Defer alone. The floor
# is a count, not merely "at least one part had bullets": a bare truthiness check
# let two of the three bullets be reworded out of `part_choice_bullets`' reach
# with the guard still scanning — and passing — over the single survivor, which
# is the same vacuity the `EXPECTED_PRECONDITIONS` floor in
# `tests/test_review_lane_ordering_contract.py` closes. Raise this if a part
# legitimately gains a fourth shelving choice.
EXPECTED_SHELVING_BULLETS = 3

MECHANISM_DEFAULT_LEAD = "**Recommended default on the mechanism row.**"

# The mechanism row's Defer default now applies at every severity, with one
# qualification: on a `blocker` the deferral ships the narrowing rather than a
# soft fix, and only while the Defer-with-narrowing branch is open at all. The
# withholding half is the load-bearing one — without it the default recommends a
# choice the coverage guard has already taken off the table.
MECHANISM_DEFAULT_SEVERITY_SCOPE = (
    "This holds **at every severity**, with one qualification on a `blocker`:"
)
MECHANISM_DEFAULT_COVERAGE_WITHHOLDING = (
    "When its coverage guard withholds `Defer` (narrowing the change would "
    "leave the stated defect partly unfixed), there is no choice to mark, even "
    "on a row-2 fire."
)

# Two clauses of that paragraph, pinned individually in the
# `MECHANISM_PRIMARY_SIGNAL` idiom. The paragraph is byte-identical across the
# two skills today — the per-skill blocker-exclusion parentheticals it used to
# carry are gone, since that gate now fires for a blocker in both — so a
# whole-paragraph mirror would also hold. Clause-level pins are kept anyway,
# because a mirror only proves the two copies agree: delete a clause from both
# and they still agree, and these two are the ones whose loss is silent.
#
# The first is the recommendation itself; without it the gate presents Defer as
# one neutral option among the set, and the "gate less, but shelve the machinery
# the ticket never asked for" default is gone. The second is what makes deferring
# non-lossy: the sketched design travels to the follow-up Issue, so the choice
# costs a round rather than the reviewer's proposal.
MECHANISM_DEFAULT_RECOMMENDATION = (
    "`Defer to follow-up Issue` is the **recommended default** — mark that "
    "choice `(Recommended)`."
)
MECHANISM_DEFAULT_VERBATIM_HANDOFF = (
    "The follow-up Issue MUST carry the reviewer's sketched design "
    "**verbatim**, so nothing about the proposed mechanism is lost by "
    "deferring it."
)

# Trigger B records an accepted limitation, which no `blocker` can ever reach —
# so its exclusion is unconditional, and the word carrying that is the whole
# difference between it and Trigger A's conditional one.
TRIGGER_B_UNREACHABLE = (
    "**Unreachable for a `blocker`-severity finding**, unconditionally"
)

# Trigger A is the one tracker write a `blocker` CAN reach, and only on the
# Defer-with-narrowing branch. Its heading was widened to "either gate" when
# part (d)'s Defer branch was made to fire the same trigger, and the entry's
# narrowing record is what separates a legitimate blocker deferral from the
# contract violation PHASE 2 and the PM both hunt for.
TRIGGER_A_HEADING = "**Trigger A — Defer to follow-up Issue at either gate.**"
TRIGGER_A_BLOCKER_REACHABILITY = (
    "**On a `blocker`-severity finding this branch is reachable only as "
    "Defer-with-narrowing, at either gate**"
)
TRIGGER_A_NARROWING_RECORD = (
    "the entry MUST then carry a **narrowing record** in `Rationale`"
)

# What the entry's **paths field** holds when the reviewer enumerated nothing
# at all. Reachable only at the routing-decision gate, whose `Defer` is offered
# whatever the path count. Without it a zero-path deferral is written with that
# field unspecified, while `Rationale` already has a rule for the same
# situation — one case, two fields, and an entry shape that is incomplete until
# both are stated.
TRIGGER_A_ZERO_PATH_FIELD = (
    "Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated "
    "no path at all — reachable at the routing-decision gate, whose `Defer` "
    "choice is offered whatever the path count."
)

# When the entry's `Rationale` soft-fix slot reads `none did`. Broader than the
# zero-path case above: it covers every deferral that ships nothing, which
# includes the single-path case at the scope-bounding gate. This is the
# tracker-side twin of part (d)'s "ships nothing against the finding this
# round" — scoped to "the single-path case" alone it is wrong at gate (d),
# where Defer ships nothing no matter how many paths the reviewer enumerated,
# so a multi-path deferral taken there would be recorded as though one of the
# remaining paths shipped as a soft fix. That is not a vague entry but a false
# one, and PHASE 2 and the PM both read the tracker as fact.
TRIGGER_A_NONE_DID_SCOPE = (
    "or that **none did**, whenever deferring leaves no fix this round — the "
    "single-path case at the scope-bounding gate, and any deferral at the "
    "routing-decision gate, whose `Defer` bullet ships nothing against the "
    "finding regardless of how many paths the reviewer enumerated."
)

# Part (c)'s statement of the same split, from the gate end. Trigger B is
# unreachable for a blocker; Trigger A is reachable for exactly one shape.
SCOPE_GATE_TRIGGER_SPLIT = (
    "**Trigger A is reachable for one**, on the Defer-with-narrowing branch "
    "above"
)

# Part (c)'s twin of `ROUTING_GATE_BLOCKER_PAIRING`. Both gates share one
# `Defer to follow-up Issue` bullet written for the non-blocker case, and both
# have to reconcile it against the blocker branch before a reader reaches it.
# Part (c)'s bullet carries THREE closing clauses a blocker would otherwise be
# read against, and the sentence answers each in turn:
#
#   1. the no-fix-this-round branch — impossible here, since condition (ii)
#      guarantees a narrowing exists and it always ships;
#   2. the never-invent-a-narrowing prohibition — aimed at filling an empty
#      soft-fix slot on a non-blocker, not at the narrowing this branch
#      requires. Unreconciled, this one reads as forbidding the very narrowing
#      the severity rule demands;
#   3. the soft-fix identification ("the most complete of the enumerated paths
#      that remain") — on a blocker what ships is the narrowing, not a
#      leftover enumerated path. Unreconciled, this one is worse than a
#      contradiction: it is followable, and following it ships a path the
#      severity rule never authorised while the narrowing goes undispatched.
#
# Pinned whole rather than clause-by-clause because the count is the contract —
# the sentence opens by claiming to dispose of the bullet's closing clauses, so
# a fourth clause added to the bullet without a fourth answer here leaves that
# claim false while every individual clause pin still passes.
SCOPE_GATE_DEFER_BULLET_RECONCILIATION = (
    "**Neither of the `Defer to follow-up Issue` bullet's closing clauses "
    "applies to one:** its no-fix-this-round branch cannot arise, because "
    "condition (ii) guarantees a narrowing exists and that narrowing always "
    "ships; its never-invent-a-narrowing prohibition is about filling an "
    "empty soft-fix slot on a non-blocker, not about the narrowing this branch "
    "requires; and neither does its soft-fix identification: what ships on a "
    "blocker is the narrowing this branch requires, not the most complete of "
    "the enumerated paths that remain."
)

# The paragraph that carries part (c)'s reconciliation, for anchoring it there
# rather than to part (c) at large — the same anchoring `ROUTING_GATE_SEVERITY_LEAD`
# gives part (d)'s.
#
# NOT the severity lead, which is what part (d)'s anchor is: the two parts are
# shaped differently. Part (d) states its whole severity rule as one paragraph,
# so its lead addresses all of it. Part (c) opens with a one-line lead, hangs
# the blocker choice set off it as sub-bullets, and then closes with this
# summary paragraph — so the severity lead addresses only that first line, and
# the reconciliation lives here. This paragraph still sits above part (c)'s
# choice bullets, which is what the ordering requirement needs; the test
# asserts that position rather than assuming it.
SCOPE_GATE_BLOCKER_SUMMARY_LEAD = (
    "The gate fires for a `blocker` like any other finding"
)

# PHASE 2's three violation shapes. The gates should never produce any of them,
# so each is a backstop rather than a routine check — and the third is the one
# that only exists because a blocker CAN now be deferred: an entry that carries a
# narrowing record still violates the contract when the narrowing it records
# left the stated defect partly unfixed. Matched against squeezed text because
# the prompt is hard-wrapped mid-sentence.
PHASE_2_VIOLATION_SHAPES = (
    "is a contract violation — a blocker can never be accepted",
    "carries **no narrowing record**",
    "left the unit's stated defect partly unfixed",
)
PHASE_2_CHALLENGE_SEVERITY = (
    "Emit any of these as a `[compromise-challenge]` finding at `blocker` "
    "severity, never lower."
)

# The post-completion step that routes PHASE 2's output. It names the excluded
# class and enumerates the same three shapes PHASE 2 emits, so the two ends have
# to describe one class; a shape added to PHASE 2 and not here arrives at a
# recovery gate that was written for a class it is not in.
RECOVERY_GATE_EXCLUDED_CLASS = (
    "**One challenge class has no recovery gate, by design: the "
    "accepted-`blocker`-or-unnarrowed-deferral contract violation PHASE 2 "
    "emits.**"
)
RECOVERY_GATE_EXCLUDED_SHAPES = (
    "the entry records an acceptance the gates should never have offered, or a "
    "deferral shipped without the narrowing that was its precondition, or one "
    "whose narrowing left the stated defect partly unfixed"
)

# Part (f)'s enforcement half of the file-first ordering. Part (c) says file
# first; this says what happens when the filing fails, and without it the
# ordering rule has no consequence attached to it.
FILE_ISSUE_FAILURE_REACHES_A_BLOCKER = (
    "**A `blocker` can reach this bullet**, via the Defer-with-narrowing "
    "branch, and on one the failed filing is load-bearing: **do not ship the "
    "narrowing when the filing failed**"
)

# The tracker's `Rationale` field spec, which has to describe what Trigger A
# writes into it. The field spec is stated twice per skill — once in the entry
# template's placeholder, once in the five-fields prose beneath it — and both
# copies are the reader's account of what a blocker deferral's entry contains.
TRACKER_RATIONALE_NARROWING_CLAUSE = (
    "on a blocker deferral the narrowing record in its place"
)
TRACKER_RATIONALE_CARRIERS = 2

# --- Cancel routing ----------------------------------------------------------

# Each orchestrator's shared aborted-unit close-out, and the sentence in it that
# enumerates its routers. `Cancel` is the third router in fix mode and the
# second in execute mode, added by this Issue.
CLOSE_OUT_HEADING = {
    QUO_FIX_ISSUE: "#### Aborted-Issue close-out",
    QUO_EXECUTE: "##### Aborted-run close-out",
}
CLOSE_OUT_ROUTER_SENTENCE = "branches route here"

# The spelled-out count that opens each close-out's router sentence. It is the
# half of the pointer a reader checks the list against, and it is what goes
# stale when a router is added without recounting — the exact defect this Issue
# fixed, which added `Cancel` as a router to both close-outs. Both counts are
# three, for different reasons: fix mode has a router execute mode has no
# analogue for (Section 3's Analyst-proposal gate), and execute mode has one fix
# mode has no analogue for (part (c)'s `Cancel`, which sits in a `blocker`'s
# base pair where fix mode offers the Analyst re-dispatch instead).
CLOSE_OUT_ROUTER_COUNT_WORD = {
    QUO_FIX_ISSUE: "Three",
    QUO_EXECUTE: "Three",
}
CANCEL_ROUTER_PHRASE = (
    "the routing-decision gate's **Cancel** choice (part (d) of "
    "`### Orchestrator discipline: routing review findings`)"
)

# A second router from each close-out's sentence, pinned per skill: the gate
# `CANCEL_ROUTER_PHRASE` does not name. It is not "the remaining" one — each
# sentence names three routers and this module pins two, so one is left over
# either way. Nor is the name positional: fix mode lists this one second and
# execute mode third.
#
# What it buys: with the count word alone, "Three" is checkable only against
# itself. Adding a second name makes the guard a change-detector over the count
# word plus two of the three routers, so a rewrite that drops or renames either
# of those two is caught rather than passing under an unchanged "Three".
#
# One acknowledged gap, not covered anywhere in this module: the third router —
# the Reconcile-step unexplained-movement gate's **Abort this Issue** / **Abort
# this unit** choice — is unpinned. Verified by deletion: removing it from
# either close-out's router sentence leaves every guard in this module passing,
# with the count word still reading "Three" over a list of two. Pinning it was
# considered and declined; it is the one router this Issue did not touch, and
# the constant would exist only to make the count self-consistent rather than to
# protect a contract this Issue changed.
THIRD_ROUTER_PHRASE = {
    QUO_FIX_ISSUE: "Section 3's Analyst-proposal gate's **Cancel** choice",
    QUO_EXECUTE: (
        "the scope-bounding gate's **Cancel** choice (part (c) of that same "
        "section, offered only in a `blocker`'s choice set)"
    ),
}

# Execute mode's close-out has two `Cancel` producers but its downstream prose
# names only one. **Every** statement in this skill that branches on "a
# routing-gate `Cancel`" — the sweep's scope selection, the marker rule, the
# checkpoint's scope resolution, the Progress write, the stop message — was
# written when part (d)'s was the only such branch. This sentence is the sole
# carrier making them cover part (c)'s too; without it, part (c)'s `Cancel`
# routes to a close-out whose every step reads as specified for the other
# branch. (No count is given deliberately: the occurrences are spread across
# more lines than any figure written here would stay true to, and the claim
# does not need one — it is about all of them.)
EXECUTE_CANCEL_EQUIVALENCE = (
    "The two `Cancel` branches behave identically here — both are a user "
    "answering *stop and re-plan* at a review site — so wherever any statement "
    "in this skill branches on the routing-gate `Cancel`, read it as covering "
    "either gate's `Cancel`."
)

# Execute mode's Bee-scope abort sweep. The Bee-level TaskList close-out it
# borrows enumerates only `*-<bee-id>` names, so the `gate-*` task that fired the
# `Cancel` is not in that enumeration and has to be named here or it is stranded
# `pending` by the very branch that created it.
EXECUTE_BEE_SCOPE_GATE_SWEEP = (
    "**and the `gate-*` task that fired the branch routing here** — that "
    "enumeration carries no `gate-*` name, so a `Cancel` fired at this review "
    "would otherwise strand its own gate task `pending`"
)

# --- `[introduces-mechanism]` chain ------------------------------------------

MECHANISM_TOKEN = "[introduces-mechanism]"
MECHANISM_TOKEN_DEFINITION = (
    "**`[introduces-mechanism]` — an optional additional token on a fix-path "
    "line.**"
)
MECHANISM_CANONICAL_ORDER = (
    "`(<letter>) [depth:<...>] [preferred] [introduces-mechanism] <description>`"
)
MECHANISM_RELAY_BULLET_LEAD = "- **Relay the `[introduces-mechanism]` tag"
RELAYERS = (AGENT_CODE_REVIEWER, AGENT_PM)

# The chain's fifth link. Four artifacts define "introduces a mechanism" by
# citation rather than by restatement, so `agents/analyst.md` is the sole
# definition site for both the emitter's tagging criterion and the
# orchestrator's fallback reading. The surrounding sentences differ per file
# (the citation is parenthetical in the role file, mid-clause in the other
# three), so only the citation itself is pinned.
MECHANISM_DEFINITION_CITATION = "the mechanism definition in `agents/analyst.md`"
MECHANISM_DEFINITION_CITERS = (
    QUO_FIX_ISSUE,
    QUO_EXECUTE,
    QUO_ENGINEER_REVIEW,
    AGENT_CODE_REVIEWER,
)

# What the definition site has to carry to satisfy those citations. Pinned as
# alternative-groups of enumeration terms rather than as a heading or a
# sentence: the definition's own wording and placement are the sibling change's
# to choose, and pinning either would make this a test of that change's prose
# instead of a test that the citation resolves. Each group is satisfied by any
# one member, matched case-insensitively.
MECHANISM_DEFINITION_TERM_GROUPS = (
    ("configuration surface",),
    ("identifier class",),
    ("retry", "fallback"),
)

# --- PM wiring ---------------------------------------------------------------

TRACKER_PATH_PLACEHOLDER = "<compromise-tracker-path>"
PM_TRACKER_CHECK_LEAD = (
    "**Any accepted `blocker`, or improperly deferred `blocker`, the run's "
    "compromise tracker records.**"
)

# The half of the PM's check that a coverage-blind reading loses. A deferral
# carrying a narrowing record is not automatically legitimate — the narrowing
# has to still cover the unit's stated defect, which is the same guard parts (c)
# and (d) state at the gates and PHASE 2 states after the run. The PM is the
# only one of the three positioned to read the record against the diff while a
# lane is still open to fix it.
PM_NARROWING_MUST_COVER_THE_DEFECT = (
    "A blocker deferral **with** a narrowing record is legitimate **only when "
    "that narrowing still covers the unit's stated defect**"
)

# Why the PM's destination channel cannot carry a blocker deferral, now that the
# gates can. The prohibition alone reads as a flat asymmetry a later editor could
# "correct" by mirroring the gates' new conditional Defer into the PM's
# destination list. The rationale is what makes the asymmetry legible: the gates
# pair a deferral with a dispatched narrowing and a tracker entry recording it,
# and a `defer-*` ledger entry pairs it with nothing.
PM_BLOCKER_DESTINATION_RATIONALE = (
    "Deferring a blocker is a decision that belongs to the orchestrator's "
    "routing gates, which pair the deferral with a **dispatched narrowing** "
    "and a tracker entry recording it"
)

# The bullet's closing instruction, which used to read "say plainly that it
# must be fixed in this scope" — a claim the gates made false the moment a
# blocker's Defer-with-narrowing branch opened. The corrected form says what is
# actually true: the outcome is not the PM's to decide, and the gates have two
# outcomes open to them. Pinned because the retired wording is the tempting one
# to restore: it is shorter, it reads as a stronger rule, and it contradicts
# the two gates it shares a contract with.
PM_BLOCKER_NOT_THE_PMS_TO_SHELVE = (
    "say plainly that it is not the PM's to shelve: the gates decide, and the "
    "only outcomes open to them are a fix in this scope or a deferral paired "
    "with a dispatched narrowing."
)

# A violation the diff under review has already resolved is not a violation.
# Without this the PM re-raises, at `blocker` severity, an entry whose fix is
# sitting in the very tree it is reading — routing a finding with no work left
# in it, once per pass, because the tracker is append-only and this check reads
# it without amending it.
PM_RESOLVED_ENTRY_ONE_LINE = (
    "when the deferred blocker has been re-opened and addressed in the tree "
    "this PM is reviewing, name the entry in **one line** as already resolved "
    "rather than re-emitting it as a `blocker` finding"
)

# The tracker stays append-only: the PM reports what it reads and never edits
# it. This is what keeps the already-resolved rule above from turning into a
# licence to tidy — "the entry is stale, so fix the entry" is the obvious next
# thought, and acting on it would silently rewrite the run's only record of a
# routing decision, out from under PHASE 2, which reads the same file after the
# run and has no way to know an entry was amended.
PM_TRACKER_IS_READ_ONLY = (
    "Leave the tracker entry itself alone; this check reads it, it does not "
    "amend it."
)

# The tracker is run-scoped; the PM is unit-scoped. Without the split below, a
# violation from an earlier unit is re-raised as this unit's blocker once per
# remaining unit, against a scope that cannot fix it.
PM_TRACKER_SCOPE_SPLIT = (
    "**The tracker is run-scoped and this review is unit-scoped, so split the "
    "violating entries by whose diff they concern.**"
)
PM_OUT_OF_SCOPE_ONE_LINE = (
    "name it in **one line** as a pre-existing violation from an earlier unit, "
    "with no fix-path line"
)
# The skill-side counterpart of `PM_REPORT_NOTE_CLAUSE`. The PM declares its
# one-line note is not a finding; part (e) is where that declaration has to be
# honoured, because the shim there is what would otherwise pick the note up —
# untagged, read as `re-architect`, and gated. Two ends, two files, no shared
# carrier: the PM can go on declaring the exemption long after the shim stopped
# granting it, and the symptom is a user gate firing on a report note.
#
# The part (f) clause is pinned with the lead because part (f)'s malformed-tag
# bullet is the shim's sibling reader and would otherwise inherit the same
# problem — an exemption that covers only part (e) leaves the note reachable by
# the other route that surfaces untagged emissions to the user.
SHIM_REPORT_NOTE_EXEMPTION_LEAD = "**One emission is out of the shim's reach:**"
SHIM_REPORT_NOTE_PART_F_CLAUSE = (
    "part (f)'s malformed-tag bullet does not reach it either"
)

PM_REPORT_NOTE_CLAUSE = (
    "**That one line is a report note, not a finding** — it carries no "
    "severity tag and no fix-path line **by design**, so the orchestrator must "
    "not route it through its routing-review-findings discipline"
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def squeeze(text):
    """Collapse every whitespace run to a single space.

    Table columns are padded for alignment and the post-completion prompt is
    hard-wrapped mid-sentence, so the on-disk bytes of a phrase depend on
    formatting the contract does not care about.

    The normalization is whitespace **only**, so it does not deliver
    format-independence in general: a hard wrap that breaks a hyphenated word
    (`highest-` / `quality`) leaves a space the source did not have, and a
    pinned phrase spanning that break will not match. That residue fails
    *closed* — the assertion using the phrase fails with a diagnostic naming
    it, rather than passing vacuously — so it costs a re-wrap, not a missed
    regression. Do not read `squeeze` as licence to pin a phrase across an
    arbitrary wrap point.
    """
    return re.sub(r"\s+", " ", text).strip()


def routing_parts(relpath):
    """`{letter: part text}` for the routing section's lettered parts.

    The letters are asserted to be exactly (a)..(g) in order, which is the
    non-vacuity guard for every per-part assertion below: a part renamed or
    re-lettered would otherwise yield a missing key or a slice running to the
    end of the section, and the checks made against it would stop meaning what
    they say.
    """
    section = routing_section(read(relpath))
    marks = list(PART_MARKER.finditer(section))
    assert [m.group("letter") for m in marks] == PART_LETTERS, (
        f"{relpath}: routing-section parts are "
        f"{[m.group('letter') for m in marks]}, expected {PART_LETTERS} — the "
        "section was restructured and the per-part checks below cannot be "
        "trusted"
    )
    parts = {}
    for i, mark in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(section)
        parts[mark.group("letter")] = section[mark.start() : end]
    return parts


def routing_table_rows(relpath):
    """`(number, condition, routing)` per row of part (a)'s fenced table.

    A row whose first cell is empty is a wrapped continuation of the row above
    it; its cells are folded into that row so the comparison is against the
    condition text rather than against where the author chose to wrap it.
    """
    lines = routing_parts(relpath)["a"].splitlines()
    fences = [i for i, line in enumerate(lines) if line.strip() == "```"]
    assert len(fences) == 2, (
        f"{relpath}: expected exactly one fenced routing table in part (a), "
        f"found {len(fences)} fence line(s)"
    )
    rows = []
    for line in lines[fences[0] + 1 : fences[1]]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3:
            continue
        number, condition, routing = cells
        if number == "#" or set(number) == {"-"}:
            continue
        if number:
            rows.append([number, condition, routing])
        else:
            assert rows, (
                f"{relpath}: the routing table opens with a continuation row"
            )
            rows[-1][1] = f"{rows[-1][1]} {condition}".strip()
            rows[-1][2] = f"{rows[-1][2]} {routing}".strip()
    return [tuple(row) for row in rows]


def scope_gate_entry_condition_sentence(relpath):
    """Part (c)'s count clause, with the count derived from part (a)'s table.

    Reading the count off the table on disk — rather than writing "four" here
    too — is what makes this a staleness guard instead of a second copy of the
    number: the sentence and the table are the two ends of one fact, and adding
    a gate-(c) row without recounting the sentence is exactly the drift being
    pinned.
    """
    rows = [
        row for row in routing_table_rows(relpath) if SCOPE_GATE_ROUTING_CELL in row[2]
    ]
    count = len(rows) + SCOPE_GATE_NON_ROW_ENTRY_CONDITIONS
    assert count in COUNT_WORDS, (
        f"{relpath}: part (a) routes {len(rows)} row(s) to the scope-bounding "
        f"gate, for {count} entry conditions — beyond the spelled-out counts "
        f"this guard knows ({sorted(COUNT_WORDS)}); extend `COUNT_WORDS`"
    )
    return f"This gate has **{COUNT_WORDS[count]}** entry conditions"


def part_choice_bullets(part_text):
    """Line numbers (part-relative) and text of the shelving choice bullets."""
    return [
        (offset, line)
        for offset, line in enumerate(part_text.splitlines())
        if line.startswith(SHELVING_BULLETS)
    ]


def phase_block(relpath, number):
    """The whitespace-squeezed text of one PHASE of the post-completion prompt."""
    lines = read(relpath).splitlines()
    starts = [
        i for i, line in enumerate(lines) if line.strip().startswith(f"PHASE {number} —")
    ]
    assert len(starts) == 1, (
        f"{relpath}: expected exactly one `PHASE {number} —` block in the "
        f"post-completion reviewer prompt, found {len(starts)}"
    )
    start = starts[0]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].strip().startswith("PHASE "):
            end = j
            break
    return squeeze(" ".join(lines[start:end]))


def normalize_section_refs(text):
    """Replace every `Section <n>` / `Section <n>.<m>` reference with one token.

    Used only when comparing mirrored prose across the two orchestrators, which
    number their own sections differently. Applying it anywhere else would hide
    a cross-reference that genuinely broke.
    """
    return SECTION_REF.sub(SECTION_REF_TOKEN, text)


def trigger_c_region(relpath):
    """All of Trigger C's prose: its lead through to Trigger D's.

    Sliced rather than read as a paragraph because Trigger C spans more than
    one: the firing-site sentence is its own paragraph in both skills today,
    and the retired revision ran on past it through further paragraphs and
    bullet blocks of machinery. Bounding on the next trigger's lead is what
    makes the slice cover whatever lies between, which is the whole point of a
    residue scan — prose sitting *past* the sentence the scan would otherwise
    anchor on is exactly the prose a tail-bounded slice cannot see. (The
    `TRIGGER_C_REGION_END` comment records how each skill failed that narrower
    bound in the pre-strip state at `6fc1c28`; the two failed it in different
    ways.)

    Both ends are asserted, plus the firing-site tail in between: a missing
    anchor would otherwise yield a region that silently proves nothing.
    """
    text = read(relpath)
    assert TRIGGER_C_LEAD in text, f"{relpath}: no {TRIGGER_C_LEAD!r} paragraph"
    start = text.index(TRIGGER_C_LEAD)
    assert TRIGGER_C_REGION_END in text[start:], (
        f"{relpath}: no {TRIGGER_C_REGION_END!r} lead after Trigger C, so the "
        "region this scans has no defined end"
    )
    end = text.index(TRIGGER_C_REGION_END, start)
    region = text[start:end]
    assert TRIGGER_C_FIRING_SITE_TAIL in region, (
        f"{relpath}: Trigger C's region does not contain "
        f"{TRIGGER_C_FIRING_SITE_TAIL!r} — the firing-site prose moved out from "
        "between the two triggers and this slice no longer covers it"
    )
    return region


def paragraph_starting(relpath, lead):
    """The single line of `relpath` that begins with `lead`."""
    matched = [line for line in read(relpath).splitlines() if line.startswith(lead)]
    assert len(matched) == 1, (
        f"{relpath}: expected exactly one paragraph led by {lead!r}, found "
        f"{len(matched)} — it was reworded or duplicated, and the assertions "
        "against it would go vacuous"
    )
    return matched[0]


# --------------------------------------------------------------------------
# Part (a) — the pick-then-route table
# --------------------------------------------------------------------------


def test_both_orchestrators_carry_the_same_six_routing_rows_in_order():
    """The routing table is mirrored row-for-row, in evaluation order.

    First match wins, so the row order is part of the contract: rows 2-4 ahead
    of row 5 is what sends a mechanism-introducing path to the scope-bounding
    gate *regardless of its depth tag*, and row 1 ahead of everything is what
    keeps the untagged-finding shim in parts (e)/(f) reachable.
    """
    for relpath in ORCHESTRATORS:
        assert routing_table_rows(relpath) == list(EXPECTED_ROUTING_ROWS), (
            f"{relpath}: part (a)'s routing rows are "
            f"{routing_table_rows(relpath)}, expected "
            f"{list(EXPECTED_ROUTING_ROWS)}"
        )


def test_the_retired_gate_every_multipath_finding_table_is_gone():
    """No cell of the `(num-paths, max-depth)` table survives in either skill.

    The retired table's `> 1 | (any) | User gate` row is the behavior Issue
    b.nn8 was filed against: it turned every finding the reviewer enumerated two
    paths for into a user prompt.
    """
    for relpath in ORCHESTRATORS:
        section = routing_section(read(relpath))
        # The whole-row check runs first, before the per-cell loop. Its cells are
        # substrings of the row (`User gate before dispatching` among them), so a
        # cell assertion would otherwise always fire first on a resurrected row
        # and the row's more specific diagnostic could never be reached.
        assert RETIRED_MULTIPATH_ROW not in squeeze(section), (
            f"{relpath}: the retired `{RETIRED_MULTIPATH_ROW}` row is back — "
            "every multi-path finding would gate again"
        )
        for shape in RETIRED_TABLE_SHAPES:
            assert shape not in section, (
                f"{relpath}: the retired routing table's {shape!r} cell is back "
                "in the routing section"
            )


def test_no_shipped_artifact_names_the_retired_routing_tuple():
    """`(num-paths, max-depth)` is retired vocabulary across shipped prose.

    The tuple was the orchestrator's parse input, and two artifacts besides the
    orchestrators described it as such — `/quo-engineer-review`'s compatibility
    constraint and `/quo-spec-review`'s severity-rendering note. A surviving
    mention tells a reader the routing still keys on a path *count*, which is
    exactly the rule this Issue removed.

    Scoped to shipped artifacts on purpose: repo-only ticket bodies under
    `.bees/` record the historical design and are not rewritten. The set comes
    from `conftest.shipped_artifacts()`, the suite's single definition of what
    an install copies, so this guard and the portability guard can never
    disagree about which files are in scope. That set includes the bundled
    helper scripts, where the token has never appeared and is harmless to scan
    for.
    """
    artifacts = shipped_artifacts()
    # Sanity: the scan must actually be looking at the shipped tree.
    assert artifacts, "no shipped artifacts discovered — glob is wrong"

    offenders = [
        str(path.relative_to(REPO_ROOT))
        for path in artifacts
        if RETIRED_ROUTING_TUPLE_TOKEN in read(path)
    ]
    assert not offenders, (
        f"shipped artifact(s) still name the retired {RETIRED_ROUTING_TUPLE_TOKEN!r} "
        "routing tuple: " + ", ".join(offenders)
    )


def test_row_six_dispatch_follows_part_g_ordering():
    """An ungated pick that changes source still goes through part (g).

    Row 6 is the new ungated path, and it is the one route to an implementer
    that no gate passes through. Without this sentence the ordering rule reads
    as applying only to gate outcomes, and an ungated pick could dispatch an
    Engineer and a writer in the same round.
    """
    for relpath in ORCHESTRATORS:
        assert (
            "when the chosen path changes source the re-dispatch follows part "
            "(g)'s ordering" in routing_parts(relpath)["a"]
        ), (
            f"{relpath}: part (a) no longer routes its chosen path through part "
            "(g)'s ordering rule"
        )


def test_row_six_paragraph_is_mirrored_across_the_two_orchestrators():
    """Part (a)'s closing paragraph is one paragraph kept in two files.

    The guard above reads one clause out of this paragraph; the paragraph
    carries two further obligations that nothing else in this module pins at
    their source. The first is row 6's tracker obligation — an ungated dispatch
    "appends a tracker entry per Section <n>'s **Trigger C**", which is the only
    record an ungated pick leaves and the input PHASE 3 of the post-completion
    prompt challenges. The second is the evaluation-order sentence, which states
    *why* the row order this module asserts elsewhere is what it is; the order
    can be preserved in the table while the paragraph explaining it drifts, and a
    reader who reorders the table then has no surviving statement of what the
    order was protecting.

    Mirrored whole rather than clause by clause because the two copies diverge in
    exactly the two `Section <n>` references each skill numbers for itself — the
    same normalization Step 1 needs, for the same reason, and the paragraph
    carries no other numbered cross-reference for it to mask.
    """
    normalized = {
        relpath: normalize_section_refs(paragraph_starting(relpath, ROW_SIX_LEAD))
        for relpath in ORCHESTRATORS
    }
    assert normalized[QUO_FIX_ISSUE] == normalized[QUO_EXECUTE], (
        "part (a)'s row-6 paragraph has diverged between `/quo-fix-issue` and "
        "`/quo-execute` beyond each skill's own section cross-references:\n"
        f"  fix-issue: {normalized[QUO_FIX_ISSUE]}\n"
        f"  execute:   {normalized[QUO_EXECUTE]}"
    )


def test_scope_bounding_gate_counts_the_rows_that_route_to_it():
    """Part (c)'s spelled-out entry-condition count matches part (a)'s table.

    Gate (c) opens by telling the reader how many ways there are into it, and
    the rest of the part is written against that number ("on any of the four").
    A reader who trusts the count stops looking once they have found that many
    conditions, so a stale count is a silently under-read gate — the same
    failure `CLOSE_OUT_ROUTER_COUNT_WORD` pins for the close-out's router list,
    and the same one this Issue had to fix there.

    The count is derived from the routing table on disk, so the guard fails on
    the *cause* rather than only on a mismatch between two literals: route a
    future row to gate (c) and the derived word moves off "four" while the
    unrecounted sentence still says four.

    Only the count clause is pinned, and not because the sentence diverges —
    the two skills' copies are byte-identical today, the execute-only tail this
    docstring used to cite having gone with the change that made the gate fire
    for a blocker in both. The clause is pinned because it is the **derived
    half** of the fact: the count is computed here from the table and compared,
    while the surrounding prose is not something this guard can derive. Pinning
    the whole sentence would restate the mirror check `routing_parts` already
    provides, and would fail this count guard on an unrelated reword.
    """
    for relpath in ORCHESTRATORS:
        sentence = scope_gate_entry_condition_sentence(relpath)
        assert sentence in routing_parts(relpath)["c"], (
            f"{relpath}: part (c) does not open with {sentence!r} — part (a) "
            "routes a number of rows to the scope-bounding gate that the gate's "
            "own spelled-out count no longer agrees with"
        )


# --------------------------------------------------------------------------
# The three definitional paragraphs behind Step 1
# --------------------------------------------------------------------------


def test_step_1_picks_only_from_the_paths_the_reviewer_enumerated():
    """Step 1's pick is closed over the reviewer's enumeration.

    This is the rule that decides who absorbs an incomplete menu. Without it
    the orchestrator's judgment step reads as open-ended — nothing says the
    pick has to come from the list — and the natural move when every
    enumerated path is a narrowing is to write a better one and dispatch it
    ungated, which is precisely the decision the gates exist to surface.

    The incomplete-menu clauses are pinned alongside the closure rule because
    the rule alone leaves a dead end: told only that it may not go outside the
    list, an orchestrator facing an all-narrowings menu has no stated move.
    The clauses are that move — pick the most complete anyway, let rows 2-4
    (or row 1) carry it to a gate, and do not absorb the gap.

    Two of them carry the **accounting** of what that gating buys, and they are
    the honest half of the branch: the menu becomes visible **in session**, and
    a **durable** record reaches the post-completion review *only* where the
    user shelves the finding — Trigger A on Defer, Trigger B on Accept —
    because `Fix properly now`, the branch the gate recommends, writes no
    tracker entry at all. Losing either clause turns a bounded guarantee into
    an unbounded-sounding one, and that is the failure mode this whole section
    replaced a composed-path allowance to avoid; overstating what replaced it
    is the regression that matters most here.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, STEP_1_LEAD)
        assert STEP_1_ENUMERATION_IS_CLOSED in paragraph, (
            f"{relpath}: Step 1 no longer closes the pick over the reviewer's "
            "enumeration, so nothing stops the orchestrator dispatching a path "
            "no reviewer proposed and no gate ever saw"
        )
        for clause in STEP_1_INCOMPLETE_MENU_CLAUSES:
            assert clause in paragraph, (
                f"{relpath}: Step 1 no longer carries the clause {clause!r} — "
                "an all-narrowings menu now has no stated move, and the "
                "closure rule above reads as a dead end"
            )


def test_the_composed_path_branch_is_retired_from_both_orchestrators():
    """No trace of the orchestrator-composes-its-own-path allowance survives.

    The allowance was stripped because a composed path is a fix the user never
    saw, dispatched ungated, on the one finding whose menu the orchestrator had
    just judged incomplete — the exact decision the gates exist for. Removing
    it touched **seven** sites in each file: the section lead's never-invent
    carve-out, Step 1's branch, the completeness definition's row-4 exemption,
    gate (c)'s context line, gate (d)'s presentation rule, the render step's
    tracker-absent clause, and Trigger C's entry substitution. A half-reverted
    edit is one of those sites coming back on its own.

    The pinned shapes are not one per site, and reading them that way is how
    the render clause went uncovered until round 2 — three shapes live in the
    Step 1 paragraph alone, while `composed path` spans five sites. Coverage
    comes from the two halves together. The fixed shapes are checked file-wide,
    which is what reaches the render clause and Trigger C, both outside the
    routing section; the bare stem is checked only inside that section, where
    any occurrence at all is residue, and catches a reworded reintroduction no
    fixed shape would match.

    One site is knowingly not covered here: execute mode's Trigger C carve-out
    clause carries no compose shape and sits outside the routing section.
    `test_trigger_c_names_row_six_as_its_only_firing_site_in_both_skills`
    catches that paragraph via its own retired-shape list.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        for shape in RETIRED_COMPOSE_SHAPES:
            assert shape not in text, (
                f"{relpath}: the retired composed-path branch's {shape!r} is "
                "back — the orchestrator can again dispatch a path no reviewer "
                "enumerated and no gate saw"
            )
        residue = COMPOSE_STEM.findall(routing_section(text))
        assert not residue, (
            f"{relpath}: the routing section still uses the compose vocabulary "
            f"({len(residue)} occurrence(s)) — Step 1's pick is closed over the "
            "reviewer's enumeration and nothing there should mention composing"
        )


def test_step_1_treats_the_preferred_token_as_an_input_not_a_verdict():
    """Step 1 says what to do when `[preferred]` and completeness disagree.

    This is the tie-break the whole judgment step turns on: without it,
    `[preferred]` reads as the reviewer's verdict, the orchestrator picks it
    unconditionally, and Step 1 degenerates into relaying a token — which is
    exactly the deference this step exists to withhold. The mirror test cannot
    stand in for this one: it compares the two copies against each other, so a
    clause deleted from both skills leaves them equal and passes.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, STEP_1_LEAD)
        assert STEP_1_PREFERRED_IS_AN_INPUT in paragraph, (
            f"{relpath}: Step 1 no longer states that the reviewer's "
            "`[preferred]` token is an input rather than a verdict, so a "
            "`[preferred]` narrowing outranks a fuller path that is still the "
            "smallest internally-consistent complete change"
        )


def test_step_1_is_mirrored_across_the_two_orchestrators():
    """Step 1 is one paragraph kept in two files.

    It is duplicated prose with no shared carrier, and the two copies are
    byte-identical today: any difference at all is drift, and drift in the
    orchestrator's only judgment step means the two skills pick differently on
    the same finding.

    The `normalize_section_refs` call is a no-op on this paragraph as it now
    stands — Step 1 carries no numbered cross-reference in either skill, having
    lost the compromise-tracker pointer along with the composed-path branch that
    cited it. It is kept because it costs nothing and fails in the safe
    direction: a Step 1 that later regains a per-skill section reference keeps
    mirroring instead of reporting a false divergence. (The same helper is not
    optional on the row-6 paragraph, which cites two such sections today.)
    """
    normalized = {
        relpath: normalize_section_refs(paragraph_starting(relpath, STEP_1_LEAD))
        for relpath in ORCHESTRATORS
    }
    assert normalized[QUO_FIX_ISSUE] == normalized[QUO_EXECUTE], (
        "Step 1 has diverged between `/quo-fix-issue` and `/quo-execute` "
        "beyond each skill's own section cross-reference:\n"
        f"  fix-issue: {normalized[QUO_FIX_ISSUE]}\n"
        f"  execute:   {normalized[QUO_EXECUTE]}"
    )


def test_the_never_invent_rule_is_stated_without_a_carve_out():
    """The section lead forbids the orchestrator originating any depth at all.

    Depth decides routing — row 5 gates on `re-architect`, row 6 dispatches
    everything shallower ungated — so an orchestrator that may originate a
    depth may route its own pick past the gate by judging it shallow. With the
    compose branch gone there is no path the orchestrator originates, so the
    rule stands unqualified; the absence of a carve-out is the contract, and
    `test_the_composed_path_branch_is_retired_from_both_orchestrators` is what
    keeps one from being reintroduced.
    """
    for relpath in ORCHESTRATORS:
        assert NEVER_INVENT_RULE in routing_section(read(relpath)), (
            f"{relpath}: the routing section no longer states, unqualified, "
            "that a path's depth is the reviewer's call and the one "
            "classification the orchestrator must never invent"
        )


def test_highest_quality_definition_is_mirrored_across_the_two_orchestrators():
    """The definition of "highest-quality" is byte-identical in both skills.

    It carries no section cross-reference, so unlike Step 1 it is compared
    raw. This is the definition every ungated pick is made against; two
    versions of it is two different routing behaviors under one name.
    """
    assert paragraph_starting(QUO_FIX_ISSUE, HIGHEST_QUALITY_LEAD) == (
        paragraph_starting(QUO_EXECUTE, HIGHEST_QUALITY_LEAD)
    ), (
        'the `What "highest-quality" means` definition has diverged between '
        "`/quo-fix-issue` and `/quo-execute`"
    )


def test_the_mechanism_tag_is_primary_and_detection_is_the_fallback():
    """Row 2's signal precedence is stated in both skills.

    The reviewer's tag and the orchestrator's own reading are not peers: a
    tagged path routes with no further judgment, and reading the description is
    what happens only when no tag arrived. Flattening the two into alternatives
    lets an orchestrator re-adjudicate a tag the reviewer already emitted, which
    is the one thing the relay chain exists to prevent.

    Only these two sentences are pinned. The rest of the paragraph names each
    skill's own approved-design source and legitimately differs.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, MECHANISM_MEANING_LEAD)
        assert MECHANISM_PRIMARY_SIGNAL in paragraph, (
            f"{relpath}: the mechanism definition no longer names the "
            "reviewer's tag as row 2's primary signal with orchestrator-side "
            "detection as the fallback"
        )


# --------------------------------------------------------------------------
# Trigger C's single firing site
# --------------------------------------------------------------------------


def test_trigger_c_names_row_six_as_its_only_firing_site_in_both_skills():
    """Row 6 is the whole of the ungated route, and neither skill says otherwise.

    Trigger C is the only record an ungated pick leaves, so the set of routes
    that fire it is the set PHASE 3 can challenge. Execute mode once collapsed
    a `blocker`'s choice set to a single choice and dispatched those findings
    without firing the gate, which obliged a second firing site and a
    cross-skill paragraph in each file explaining how the other differed. Both
    gates now fire for a blocker in both skills, so there is one site and
    nothing to compare.

    The cross-skill comparison is pinned as an absence, not just the retired
    wording: a paragraph in one file describing the *other* file's behavior has
    no carrier keeping it true, so it rots the moment the other file is edited
    alone — the same one-sided-edit failure this module exists for, in the one
    shape a mirror test cannot catch.

    The firing-site sentence is addressed as a **paragraph** rather than looked
    up in the file text. `paragraph_starting`'s exactly-one assertion is what
    keeps the claim honest: the sentence stands alone in both skills today, and
    folding it back into the trigger's own paragraph — the shape execute mode
    briefly had, and the shape that let the retired second firing site sit
    beside it unnoticed — now fails here rather than passing a containment
    check. The wider `trigger_c_region` slice is unaffected and still bounded
    at Trigger D, because the residue scans have to reach prose *past* this
    sentence, which is exactly what a paragraph-sized view would miss.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        firing_site = paragraph_starting(relpath, TRIGGER_C_FIRING_SITE)
        assert firing_site.rstrip().endswith(TRIGGER_C_FIRING_SITE_TAIL), (
            f"{relpath}: Trigger C's firing-site paragraph no longer closes on "
            f"{TRIGGER_C_FIRING_SITE_TAIL!r} — it has grown a tail past the "
            "point where the sentence stops ruling out a second ungated route, "
            "which is where the retired cross-skill parenthetical lived"
        )
        for shape in RETIRED_TRIGGER_C_SHAPES:
            assert shape not in text, (
                f"{relpath}: the retired {shape!r} wording is back — Trigger C "
                "describes more firing sites than row 6"
            )
        region = trigger_c_region(relpath)
        other = OTHER_ORCHESTRATOR_NAME[relpath]
        assert other not in region, (
            f"{relpath}: Trigger C's prose describes `{other}`'s behavior. "
            "Nothing carries that claim across the two files, so it goes stale "
            f"the next time `{other}` is edited on its own"
        )


# --------------------------------------------------------------------------
# The tracker `Decision` value and its post-completion reader
# --------------------------------------------------------------------------


def test_the_sr_6_7_gate_name_matches_at_all_three_sites_in_both_skills():
    """Trigger D's write logic and step 7's gate agree on the gate's name.

    Trigger D says it "anchors to those gates by name", so the name is doing
    cross-reference work, not labelling. **This test covers the SR-6.7 gate
    only** — see the acknowledged gap below for SR-4.6, whose name is already
    inconsistent and is not pinned here.

    SR-6.7's name appears three times per skill — step 7's bullet defining the
    gate, Trigger D's lead claiming the anchoring, and Trigger D's sub-heading
    holding that gate's write logic — and the string is the only thing tying
    them together. Rename one site and Trigger D's claim becomes false without
    anything failing: the write logic ends up under a heading no gate answers
    to, and the tracker write for a recovered ungated pick has no reachable
    specification.

    The count is asserted alongside the sites, because "three" is what makes
    the enumeration exhaustive: a fourth mention added elsewhere and left out of
    a later rename is the same drift in a place this test does not look.

    The old name is pinned as an absence in the same pass. Note what that check
    deliberately does *not* catch: `(depth misjudgment)` inside the tracker's
    `Decision` value, and the `depth-misjudgment override` gloss on it, are
    retained on purpose — they describe the misjudgment, not the gate. The
    absence check keys on the full retired gate name so those survive it.

    One acknowledged gap, knowingly unpinned: **SR-4.6's name is already
    inconsistent across the same three sites, identically in both skills.**
    Step 7's bullet defines `SR-4.6 under-enumeration recovery gate`, while
    Trigger D's lead and sub-heading both say `SR-4.6 under-enumeration analog
    recovery gate` — so Trigger D's anchor-by-name resolves for SR-6.7 and not
    for SR-4.6. That asymmetry was ratified as a sanctioned seam rather than
    repaired, and skill edits are out of scope for this pass, so pinning it now
    would encode a state the prose is not committed to. Both wordings are
    recorded here, with the sites each occupies, so whoever reconciles them
    knows which two strings to converge and where each one lives.
    (`SR-4.6 under-enumeration analog override`, in the tracker's `Decision`
    enum, is the override gloss and is not the gate's name; it survives any
    such rename, exactly as SR-6.7's does.)
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        assert text.count(SR_6_7_GATE_NAME) == 3, (
            f"{relpath}: expected {SR_6_7_GATE_NAME!r} at exactly three sites "
            f"(step 7's bullet, Trigger D's lead, Trigger D's sub-heading), "
            f"found {text.count(SR_6_7_GATE_NAME)}"
        )
        for label, form in SR_6_7_GATE_SITES.items():
            assert text.count(form) == 1, (
                f"{relpath}: {label} is no longer exactly one {form!r} — the "
                "gate was renamed at one site and not the others, so Trigger "
                "D's anchor-by-name no longer resolves"
            )
        trigger_d = paragraph_starting(relpath, TRIGGER_D_LEAD)
        assert SR_6_7_GATE_NAME in trigger_d, (
            f"{relpath}: Trigger D's lead no longer names "
            f"{SR_6_7_GATE_NAME!r}, so its claim to anchor on the gates by "
            "name has nothing behind it"
        )
        assert RETIRED_SR_6_7_GATE_NAME not in text, (
            f"{relpath}: the retired gate name {RETIRED_SR_6_7_GATE_NAME!r} is "
            "back — the gate is named for what it recovers, not for the "
            "misjudgment that reaches it"
        )


def test_decision_enum_carries_the_orchestrator_pick_value():
    """Both trackers can record an ungated orchestrator pick."""
    for relpath in ORCHESTRATORS:
        enum_line = paragraph_starting(relpath, DECISION_ENUM_LEAD)
        assert DECISION_PICK_VALUE in enum_line, (
            f"{relpath}: the compromise-tracker `Decision` enum does not offer "
            f"{DECISION_PICK_VALUE!r}, so an ungated pick has no value to record "
            "under"
        )


def test_retired_auto_route_decision_value_is_gone():
    """The single-path auto-route `Decision` value is retired in both skills.

    Its rule no longer exists: the orchestrator picks among *any* number of
    paths rather than auto-routing the lone `refactor-locally` one. A tracker
    entry written under the old value would be invisible to PHASE 3, which now
    matches only the pick value.
    """
    for relpath in ORCHESTRATORS:
        assert RETIRED_DECISION_VALUE not in read(relpath), (
            f"{relpath}: the retired {RETIRED_DECISION_VALUE!r} `Decision` value "
            "is still present"
        )


def test_phase_3_anchors_match_the_decision_value_written_in_the_same_skill():
    """PHASE 3's matcher and the tracker's enum value share their anchors.

    PHASE 3 cannot match a literal `Decision` string — the writing step
    substitutes the chosen path's own letter — so it matches on the wording
    around the letter. Those anchors live in two places per file with nothing
    linking them; drift in either one leaves PHASE 3 matching no entry at all,
    and PHASE 3 is the only surface that challenges an ungated pick.

    Only the PHASE 3 end is asserted here. The enum end is covered by
    `test_decision_enum_carries_the_orchestrator_pick_value`, which pins
    `DECISION_PICK_VALUE` — and the anchors are **split from that value**, so
    each is a substring of it by construction, not by two literals happening to
    agree. Asserting them against the enum line again therefore could not fail
    unless that test already had. Keeping the redundant pair would spread one
    fact across two guards and make the enum's owner ambiguous.
    """
    for relpath in ORCHESTRATORS:
        phase_3 = phase_block(relpath, 3)
        for anchor in (DECISION_PICK_PREFIX, DECISION_PICK_SUFFIX):
            assert anchor in phase_3, (
                f"{relpath}: PHASE 3 of the post-completion prompt no longer "
                f"carries the {anchor!r} anchor, so it cannot match the tracker "
                "entries it exists to challenge"
            )


def test_phase_2_and_phase_3_are_mirrored_across_the_two_skills():
    """The post-completion PHASE blocks are one prompt kept in two files.

    Both skills dispatch the same fresh-eyes reviewer with the same phases; the
    text is duplicated only because each skill embeds its own prompt skeleton.
    A challenge clause added to one and not the other means half the runs stop
    challenging it.
    """
    for number in (2, 3):
        assert phase_block(QUO_FIX_ISSUE, number) == phase_block(
            QUO_EXECUTE, number
        ), (
            f"PHASE {number} of the post-completion reviewer prompt has diverged "
            "between `/quo-fix-issue` and `/quo-execute`"
        )


# --------------------------------------------------------------------------
# The severity rule — a `blocker` is never deferred or accepted
# --------------------------------------------------------------------------


def test_scope_bounding_gate_never_lets_a_blocker_be_accepted():
    """Part (c) withholds `Accept the limitation` from a `blocker`, always.

    Accept is the one choice with no conditional branch on either side of it:
    accepting a blocker ships the blocker, and no narrowing, follow-up Issue,
    or tracker entry changes that. The word carrying the unconditionality is
    the load-bearing one — "unreachable" alone reads as the head of a sentence
    that could grow an exception clause, which is how the Defer half came to
    have one.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert SCOPE_GATE_BLOCKER_RULE in part_c, (
            f"{relpath}: part (c) no longer leads its severity rule with the "
            "never-accepted / defer-only-with-a-narrowing statement"
        )
        assert SCOPE_GATE_ACCEPT_UNREACHABLE in part_c, (
            f"{relpath}: part (c) no longer names `Accept the limitation` "
            "unreachable *unconditionally* for a `blocker`"
        )


def test_routing_decision_gate_makes_a_blockers_defer_route_conditional():
    """Part (d) opens Defer to a `blocker` only on part (c)'s two conditions.

    Part (d) offers no Accept choice at all, so Defer is the whole of what has
    to be governed here — and governing it at part (c) alone would leave the
    other gate as an open route to the same outcome, on terms part (c) never
    set. Deferring to part (c)'s conditions rather than restating them is what
    keeps one rule: a second copy of the two conditions is a second copy that
    can be relaxed on its own.

    The pairing correction is asserted against the **severity paragraph**, not
    against part (d) at large. Its whole job is to qualify the `Defer to
    follow-up Issue` bullet *before* a reader reaches it — the same
    rule-above-the-choices ordering the mechanical shelving-bullet guard
    enforces elsewhere in this module. Sitting anywhere in part (d) satisfies a
    part-wide check, including below the bullet it corrects, where a reader
    assembling the choice has already passed it.
    """
    for relpath in ORCHESTRATORS:
        part_d = routing_parts(relpath)["d"]
        severity_paragraph = paragraph_starting(relpath, ROUTING_GATE_SEVERITY_LEAD)
        assert ROUTING_GATE_BLOCKER_RULE in part_d, (
            f"{relpath}: part (d) no longer states that a `blocker`'s Defer "
            "route is conditional"
        )
        assert ROUTING_GATE_CONDITIONAL_DEFER in part_d, (
            f"{relpath}: part (d) no longer conditions `Defer to follow-up "
            "Issue` on part (c)'s two conditions both holding — it either "
            "offers a blocker an unconditional Defer or withholds one part (c) "
            "allows"
        )
        assert ROUTING_GATE_BLOCKER_PAIRING in severity_paragraph, (
            f"{relpath}: part (d)'s severity paragraph no longer corrects its "
            "own `Defer to follow-up Issue` bullet for the blocker case, so "
            "the bullet's \"rather than picking a path now\" reads as licence "
            "to defer a blocker with nothing narrowed and nothing shipped"
        )


def test_execute_zero_path_gate_fires_and_its_dispatch_is_not_an_ungated_route():
    """Execute's gate (d) fires on an empty path list, and that dispatch is gated.

    This paragraph is what makes Trigger C's "row 6 is the only firing site"
    true in execute mode. A row-1 `blocker` can arrive with no fix path
    enumerated at all, and the retired revision read that as a gate declining
    to fire — which made the follow-on dispatch ungated, which is why its
    Trigger C carried a second firing site to record it. The replacement closes
    the branch at the gate instead: the gate fires on an empty list, the user
    directs the fix in prose, and a user-directed fix is not an ungated route,
    so no tracker entry is due.

    Both halves are pinned because neither implies the other. Drop the first
    and the gate has nothing to present, so "it does not fire" is the natural
    reading and the ungated dispatch is back. Drop the second and the dispatch
    that follows looks ungated, so Trigger C's single-site claim is false in
    this skill while its own sentence still says otherwise.

    `QUO_EXECUTE`-only: fix mode sends a zero-path blocker to its Analyst
    re-dispatch, so it has no free-text branch to exempt.
    """
    part_d = routing_parts(QUO_EXECUTE)["d"]
    assert EXECUTE_ZERO_PATH_GATE_FIRES in part_d, (
        f"{QUO_EXECUTE}: part (d) no longer says the gate fires on a zero-path "
        "blocker with an empty per-path list — a gate with nothing to present "
        "reads as a gate that does not fire, and the dispatch after it is "
        "ungated with no Trigger C site to record it"
    )
    assert EXECUTE_USER_DIRECTED_IS_NOT_UNGATED in part_d, (
        f"{QUO_EXECUTE}: part (d) no longer exempts a user-directed fix from "
        f"Trigger C, so {TRIGGER_C_FIRING_SITE!r} is false in this skill while "
        "Trigger C still claims it"
    )


def test_scope_bounding_gate_always_offers_a_blocker_the_base_pair():
    """Part (c) never presents a `blocker` with fewer than two real choices.

    The Defer-with-narrowing branch is conditional, so without a floor a
    blocker whose conditions do not both hold reaches a gate holding one
    choice — a dispatch wearing a gate's clothes, which asks the user to
    ratify what was going to happen anyway. The pair itself is per-skill (fix
    mode routes a wrong-directive blocker back to the Analyst; execute mode has
    no Analyst and offers `Cancel` — stop the run and re-plan) but the floor is
    the shared rule, so the lead is checked in both and the members per file.

    Each skill's no-`Cancel` presentation rule is checked here too, because it
    is the negative half of that same per-skill split and the two halves have
    to agree: execute mode withholds `Cancel` from the `suggestion` / `nit` set
    *because* a blocker's base pair contains it, while fix mode withholds it
    from the gate outright *because* no choice set there has one. Pin the base
    pair without its matching withholding rule and a skill can end up denying a
    blocker the `Cancel` its own floor guarantees.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert BASE_PAIR_LEAD in part_c, (
            f"{relpath}: part (c) no longer guarantees a `blocker` the base "
            "pair, so its choice set can collapse to one"
        )
        assert BASE_PAIR_MEMBERS[relpath] in part_c, (
            f"{relpath}: part (c)'s base pair is no longer "
            f"{BASE_PAIR_MEMBERS[relpath]!r}"
        )
        assert SCOPE_GATE_NO_CANCEL_RULE[relpath] in part_c, (
            f"{relpath}: part (c)'s no-`Cancel` rule is no longer "
            f"{SCOPE_GATE_NO_CANCEL_RULE[relpath]!r} — it now scopes the "
            "withholding to a set that contradicts this skill's own base pair"
        )


def test_scope_bounding_gate_adds_defer_only_when_both_conditions_hold():
    """A `blocker`'s third choice requires a mechanism AND an out-of-scope case.

    Either condition alone still shelves a blocker. A mechanism that serves the
    unit's own stated defect cannot be narrowed away without leaving that
    defect partly unfixed, and a path that introduces no mechanism has nothing
    to hand to a follow-up Issue — so an `or` here, or a single condition,
    reopens the route the severity rule exists to close.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert DEFER_THIRD_CHOICE_LEAD in part_c, (
            f"{relpath}: part (c) no longer gates a `blocker`'s "
            "`Defer to follow-up Issue` on *both* conditions holding"
        )
        for condition in DEFER_CONDITIONS:
            assert condition in part_c, (
                f"{relpath}: part (c)'s Defer branch no longer states the "
                f"condition {condition!r}"
            )
        assert DEFER_ROW_INDEPENDENCE_ANTECEDENT in part_c, (
            f"{relpath}: part (c)'s Defer branch no longer names the "
            "pairing-as-recommended-default that the row-independence sentence "
            "below it says 'It' refers to — that sentence now qualifies "
            "whatever happens to precede it"
        )
        assert DEFER_ROW_INDEPENDENCE in part_c, (
            f"{relpath}: part (c)'s Defer branch no longer says it applies "
            "whichever row fired the gate on a `blocker`, so it reads as row-2 "
            "only — and a blocker whose needed fix path introduces a mechanism "
            "is denied the branch on a row-3 or row-4 fire"
        )


def test_the_narrowing_coverage_guard_is_stated_at_both_gates():
    """Neither gate lets a narrowing buy the deferral with the stated defect.

    The narrowing is what makes a blocker deferral legitimate, so the guard on
    what a narrowing may cost is the whole of the branch's safety: narrow far
    enough and every blocker becomes deferrable, which is the severity rule
    read backwards. Both gates need their own copy because part (d) opens the
    Defer route on part (c)'s conditions but presents its own choice set — a
    reader working part (d) need never read part (c)'s paragraph.
    """
    for relpath in ORCHESTRATORS:
        parts = routing_parts(relpath)
        for letter in ("c", "d"):
            assert NARROWING_COVERAGE_GUARD in parts[letter], (
                f"{relpath}: part ({letter}) no longer states that a narrowing "
                "may never reduce coverage of the stated defect, so a blocker "
                "can be deferred by narrowing the defect itself out of scope"
            )


def test_the_blocker_deferral_files_the_follow_up_issue_before_the_narrowing():
    """The follow-up Issue is filed first, and the narrowing dispatched after.

    Part (f) forbids shipping the narrowing when the filing failed, and that
    rule is only enforceable while the narrowing has not shipped yet. Reverse
    the order and the failure branch arrives after the fact: the change has
    already been narrowed, the deferred design has no ticket carrying it, and
    what remains is a quietly reduced fix with no record of the reduction.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert DEFER_FILE_FIRST in part_c, (
            f"{relpath}: part (c) no longer pairs the deferral with the "
            "narrowing and files the follow-up Issue first"
        )
        assert DEFER_FILE_FIRST_ORDER in part_c, (
            f"{relpath}: part (c) no longer holds the narrowing's dispatch "
            "until `/quo-file-issue` has returned an Issue ID, so part (f)'s "
            "failure branch arrives after the narrowing already shipped"
        )


def test_routing_decision_gate_marks_exactly_one_choice_recommended():
    """Part (d) resolves the collision between its two `(Recommended)` rules.

    Part (d) marks the Step-1 pick Recommended, and a `blocker` whose Defer
    branch is open gets that choice marked too — two rules, both firing on the
    same question. A gate that renders two `(Recommended)` choices recommends
    nothing, and does it at the one gate whose whole job is to surface a
    decision the orchestrator would not make alone. Both ends of the sentence
    are pinned: the precedence half without the exactly-one half states which
    marker wins but not that the loser is withheld.
    """
    for relpath in ORCHESTRATORS:
        part_d = routing_parts(relpath)["d"]
        assert ROUTING_GATE_MARKER_PRECEDENCE in part_d, (
            f"{relpath}: part (d) no longer gives the blocker Defer branch's "
            "`(Recommended)` precedence over the per-path marker, so a gate can "
            "render two recommended choices"
        )
        assert ROUTING_GATE_EXACTLY_ONE_MARKER in part_d, (
            f"{relpath}: part (d) no longer states that exactly one choice "
            "carries `(Recommended)`, so withholding it from the other choices "
            "reads as optional"
        )


def test_fix_issue_analyst_redispatch_sweeps_in_flight_lanes_before_phase_a():
    """The Analyst re-dispatch clears the writer lanes that would wedge the Engineer.

    Part (g)'s Engineer-dispatch precondition forbids a fresh Engineer while
    any writer, reviewer, or PM task for the Issue is `pending` or
    `in_progress` — and this choice can fire from a review phase where several
    are. Re-entering Phase A without the sweep therefore does not fail loudly;
    it waits on tasks whose findings were raised against the directive the
    re-dispatch just superseded. The two ends have no shared carrier: part (c)
    specifies the sweep, and Section 3's Approve branch is where it has to
    actually run, which is a different section of the file.

    Each end is asserted **against its own section**, not against the whole
    file, because "these two things are in different places" is the entire
    contract here. A file-wide `in` check passes just as happily when both ends
    have been collapsed into part (c) — leaving the Approve branch with no
    instruction to run the sweep, which is precisely the half-landed shape this
    pins against.

    Fix mode only — `/quo-execute` has no Analyst, and offers `Cancel` in its
    place.
    """
    part_c = routing_parts(QUO_FIX_ISSUE)["c"]
    approve_branch = heading_section(
        read(QUO_FIX_ISSUE), ANALYST_APPROVE_BRANCH_HEADING
    )
    assert ANALYST_REDISPATCH_SWEEP_SPEC in part_c, (
        f"{QUO_FIX_ISSUE}: part (c)'s Analyst re-dispatch no longer requires "
        "the Issue's open TaskList tasks to be closed out before Phase A "
        "re-entry"
    )
    assert ANALYST_REDISPATCH_SWEEP_ORDERING in approve_branch, (
        f"{QUO_FIX_ISSUE}: `{ANALYST_APPROVE_BRANCH_HEADING}` no longer runs the "
        "Analyst re-dispatch's in-flight-lane sweep, so the sweep is specified "
        "in part (c) and executed nowhere"
    )
    assert ANALYST_REDISPATCH_SPEC_POINTER in approve_branch, (
        f"{QUO_FIX_ISSUE}: `{ANALYST_APPROVE_BRANCH_HEADING}` no longer points "
        "at part (c) as the sweep's specification, so the two copies can drift "
        "into listing different task prefixes"
    )
    assert ANALYST_REDISPATCH_SWEEP_SURVIVES_REVISE in approve_branch, (
        f"{QUO_FIX_ISSUE}: `{ANALYST_APPROVE_BRANCH_HEADING}` no longer carries "
        "the sweep obligation across Revise iterations — read as applying only "
        "to an Approve of the re-dispatched Analyst's first return, a Revise "
        "before Approving skips the sweep entirely, and part (g)'s precondition "
        "then wedges the next Engineer on lanes nothing will clear"
    )
    for clause in ANALYST_REDISPATCH_DISCARD_SCOPE:
        assert clause in part_c, (
            f"{QUO_FIX_ISSUE}: part (c)'s Analyst re-dispatch no longer carries "
            f"{clause[:60]!r}… — the discard collapses back onto the sweep, and "
            "findings with no TaskList task of their own (the gate-firing "
            "return's siblings, and lanes that landed before the sweep) get "
            "routed against the superseded directive"
        )


def test_fix_issue_supersession_spares_defer_tasks_banked_at_an_earlier_approve():
    """Supersession clears a rejected iteration's `defer-*` tasks, and only those.

    The `defer-*` ledger is the Analyst lane's only inter-session carrier for
    refinements the Engineer will not implement this Issue. Nothing downstream
    rebuilds it — Section 7.5's Step 1 enumerates only tasks still active, and
    its Step 0 walks only the latest Analyst block — so a task cleared here is
    a refinement lost outright, silently, with no surface that reports it.

    That makes the width of the rule load-bearing rather than a nicety. Stated
    as "a re-dispatch supersedes the prior block", it clears the tasks banked
    at an **earlier Approve** too: an approval that still stands, whose
    refinements the re-fired Analyst was never briefed on (it is briefed on the
    reviewer's finding), so its block may legitimately be `None` and there is
    nothing to re-create them from. Every banked refinement would be destroyed
    at the first re-fire. The narrow rule turns on why an iteration is stale —
    a Revise chain's iterations were rejected in favour of the next, an
    Approve's was not — so both halves are pinned: the clearing sentence alone
    is the over-wide rule this replaced.

    The third route into the approval moment is pinned with them because the
    rules are written against it. A re-fire from part (c)/(d) is the only route
    on which an earlier Approve's tasks can already exist; drop it from the
    approval-moment sentence and the surviving rules govern a case the
    paragraph no longer says it handles.

    Fix mode only — `/quo-execute` has no Analyst and no deferred-refinements
    block.
    """
    section = heading_section(read(QUO_FIX_ISSUE), DEFERRED_REFINEMENTS_HEADING)
    assert DEFERRED_REFINEMENTS_THIRD_ROUTE in section, (
        f"{QUO_FIX_ISSUE}: the deferred-refinements consumption no longer names "
        "the part (c)/(d) re-fire among the Approve routes that consume the "
        "block — the one route on which an earlier Approve's `defer-*` tasks "
        "can already exist, which is what the supersession rules are about"
    )
    for rule in DEFERRED_REFINEMENTS_SUPERSESSION_RULES:
        assert rule in section, (
            f"{QUO_FIX_ISSUE}: the deferred-refinements consumption no longer "
            f"carries {rule!r} — without both halves the rule reads wide enough "
            "to clear the `defer-*` tasks banked at an earlier Approve, "
            "destroying every banked refinement at the first re-fire with "
            "nothing downstream able to recover them"
        )


def test_the_blocker_narrowing_is_dispatched_directly_not_through_step_2():
    """The narrowing bypasses Step 2 rather than looping back through it.

    A narrowing is narrower than the smallest internally-consistent complete
    fix by construction — that is what makes it a narrowing — so re-entering
    Step 2 with it matches row 4 and routes it straight back to the gate that
    just produced it. Stated once, this is the same terminality the non-blocker
    soft fix already carries; left unstated, the gate's own answer re-enters
    the gate.
    """
    for relpath in ORCHESTRATORS:
        assert NARROWING_DISPATCHED_DIRECTLY in routing_parts(relpath)["c"], (
            f"{relpath}: part (c) no longer dispatches a `blocker`'s narrowing "
            "directly, so the narrowing re-enters Step 2, matches row 4, and "
            "routes back to this same gate"
        )


def test_every_shelving_choice_is_preceded_by_its_part_s_blocker_exclusion():
    """No part offers Defer or Accept without first withholding it from blockers.

    This is the mechanical form of the rule, rather than a check on parts (c)
    and (d) by name: it scans *every* lettered part for a choice that shelves a
    finding, and requires the severity rule to appear above it in the same part.
    A future gate that grows a Defer choice is caught the same way, and so is a
    reorder that moves the rule below the choice list, where a reader picking
    choices off the bullets would never reach it.
    """
    for relpath in ORCHESTRATORS:
        scanned = 0
        for letter, part_text in routing_parts(relpath).items():
            lines = part_text.splitlines()
            bullets = part_choice_bullets(part_text)
            if not bullets:
                continue
            scanned += len(bullets)
            rules = [i for i, line in enumerate(lines) if BLOCKER_EXCLUSION_LEAD in line]
            assert rules, (
                f"{relpath}: part ({letter}) offers a shelving choice with no "
                f"{BLOCKER_EXCLUSION_LEAD!r} rule — a `blocker` could be shelved "
                "there"
            )
            rule_line = rules[0]
            first_bullet = bullets[0][0]
            assert rule_line < first_bullet, (
                f"{relpath}: part ({letter})'s blocker-exclusion rule sits at "
                f"line {rule_line} of the part, below its first shelving choice "
                f"at line {first_bullet} — the rule must qualify the choices "
                "before they are read"
            )
        assert scanned == EXPECTED_SHELVING_BULLETS, (
            f"{relpath}: this guard scanned {scanned} shelving choice(s), "
            f"expected {EXPECTED_SHELVING_BULLETS} (part (c): "
            f"{DEFER_BULLET!r} and {ACCEPT_BULLET!r}; part (d): "
            f"{DEFER_BULLET!r}) — a bullet was reworded out of this guard's "
            "reach, or a new one was added and needs the floor raised"
        )


def test_shelving_choice_descriptions_never_mention_a_blocker():
    """The Defer / Accept bullets stay blocker-free.

    The exclusion is stated once, as a rule above the choice list. Re-stating it
    inside a choice description — "defer unless the finding is a blocker" — is
    how an exception creeps back in: the bullet is what an orchestrator reads
    when it is assembling the `AskUserQuestion`, and a qualified bullet reads as
    a blocker-bearing choice that is merely discouraged.

    Carries the same count floor as the ordering guard above, and for the same
    reason: this test's whole content is a loop over the bullets
    `part_choice_bullets` finds, so a rewording that moves them out of its
    reach turns it into a loop over nothing that reports a pass.
    """
    for relpath in ORCHESTRATORS:
        scanned = 0
        for letter, part_text in routing_parts(relpath).items():
            for _, line in part_choice_bullets(part_text):
                scanned += 1
                assert "blocker" not in line.lower(), (
                    f"{relpath}: part ({letter})'s shelving choice description "
                    f"mentions a blocker: {line!r}"
                )
        assert scanned == EXPECTED_SHELVING_BULLETS, (
            f"{relpath}: this guard scanned {scanned} shelving choice(s), "
            f"expected {EXPECTED_SHELVING_BULLETS} — a bullet was reworded out "
            "of this guard's reach, or a new one was added and needs the floor "
            "raised"
        )


def test_defer_recommended_default_holds_at_every_severity_with_one_qualification():
    """The mechanism row's Defer default now reaches a `blocker` too, conditionally.

    Defer is the recommended answer when a chosen path builds machinery the
    ticket never asked for, and that reasoning does not weaken at `blocker`
    severity — what changes is *what ships alongside* the deferral (a narrowing
    rather than a soft fix) and *whether the choice exists at all*. Both halves
    have to be stated: qualified to non-blockers it recommends nothing on the
    severity that most needs the recommendation, and stated flatly at every
    severity it recommends a choice the coverage guard may have withheld.

    The recommendation itself and the verbatim-handoff sentence are pinned in
    the same test because the qualification is only meaningful while there is a
    recommendation for it to qualify. They are pinned as clauses rather than as
    a whole-paragraph mirror because the copies still name each skill's own
    surrounding structure.
    """
    for relpath in ORCHESTRATORS:
        default_paragraph = paragraph_starting(relpath, MECHANISM_DEFAULT_LEAD)
        assert MECHANISM_DEFAULT_SEVERITY_SCOPE in default_paragraph, (
            f"{relpath}: the mechanism-row Defer default no longer holds at "
            "every severity with one qualification on a `blocker` — it either "
            "excludes the severity the recommendation matters most on, or "
            "recommends a blocker a choice unconditionally"
        )
        assert MECHANISM_DEFAULT_COVERAGE_WITHHOLDING in default_paragraph, (
            f"{relpath}: the mechanism-row default no longer says there is no "
            "choice to mark when the coverage guard withholds `Defer`, so it "
            "recommends a choice the severity rule already took off the table"
        )
        assert MECHANISM_DEFAULT_RECOMMENDATION in default_paragraph, (
            f"{relpath}: the mechanism-row paragraph no longer names "
            "`Defer to follow-up Issue` the recommended default, or no longer "
            "tells the orchestrator to mark it `(Recommended)` — the gate now "
            "presents Defer as one neutral choice among the set"
        )
        assert MECHANISM_DEFAULT_VERBATIM_HANDOFF in default_paragraph, (
            f"{relpath}: the mechanism-row paragraph no longer requires the "
            "follow-up Issue to carry the reviewer's sketched design verbatim, "
            "so the recommended default now loses that design on the way out"
        )


def test_tracker_trigger_b_is_unreachable_for_a_blocker_unconditionally():
    """Trigger B records an accepted limitation, which no blocker can reach.

    Trigger B is the downstream record of the choice part (c) withholds
    outright, so it carries the same exclusion — otherwise the tracker still
    describes a shape the gates can no longer produce, and PHASE 2's
    contract-violation check reads as guarding against nothing. The
    "unconditionally" is pinned with the clause: it is the only thing
    distinguishing this exclusion from Trigger A's conditional one, and the two
    triggers sit two paragraphs apart.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, "**Trigger B — ")
        assert TRIGGER_B_UNREACHABLE in paragraph, (
            f"{relpath}: Trigger B no longer states it is unreachable for a "
            "`blocker`-severity finding *unconditionally*, so the tracker can "
            "record an accepted blocker"
        )


def test_tracker_trigger_a_reaches_a_blocker_only_with_a_narrowing_record():
    """Trigger A is the one tracker write a blocker can reach, and it is qualified.

    A blocker's Defer branch ships a narrowing rather than one of the
    reviewer's other paths, so its entry has nothing in the "which enumerated
    path shipped as the soft fix" slot unless the narrowing goes there. That
    record is not bookkeeping: it is the only artifact distinguishing a
    legitimate Defer-with-narrowing from the contract violation both PHASE 2
    and the PM's tracker check hunt for, and an entry without it is
    indistinguishable from a shelved blocker.

    The heading is pinned alongside because it was widened to "either gate"
    when part (d)'s Defer branch was made to fire this same trigger. A heading
    still naming one gate leaves part (d)'s deferrals with no stated tracker
    write at all.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, "**Trigger A — ")
        assert paragraph.startswith(TRIGGER_A_HEADING), (
            f"{relpath}: Trigger A's heading is not {TRIGGER_A_HEADING!r} — a "
            "heading naming one gate leaves the other gate's Defer branch with "
            "no stated tracker write"
        )
        assert TRIGGER_A_BLOCKER_REACHABILITY in paragraph, (
            f"{relpath}: Trigger A no longer scopes a `blocker` entry to the "
            "Defer-with-narrowing branch, so it reads as recording any blocker "
            "deferral the gates might produce"
        )
        assert TRIGGER_A_NARROWING_RECORD in paragraph, (
            f"{relpath}: Trigger A no longer requires the narrowing record on a "
            "`blocker` entry, so a legitimate deferral and a contract violation "
            "write the same entry"
        )
        assert TRIGGER_A_NONE_DID_SCOPE in paragraph, (
            f"{relpath}: Trigger A no longer scopes its `none did` slot to every "
            "deferral that ships nothing — scoped to the single-path case "
            "alone, a multi-path deferral at the routing-decision gate records "
            "a soft fix that never shipped"
        )
        assert TRIGGER_A_ZERO_PATH_FIELD in paragraph, (
            f"{relpath}: Trigger A no longer says what the paths field holds "
            "when the reviewer enumerated nothing, so a zero-path deferral's "
            "entry is written with that field unspecified while `Rationale` "
            "already has a rule for the same case"
        )


def test_scope_bounding_gate_states_which_trigger_a_blocker_can_reach():
    """Part (c) names the trigger split from the gate end, not just the tracker end.

    The tracker's triggers say what they record; the gate says what it can
    produce. Both ends are needed — a reader routing a blocker at part (c) has
    no reason to open the tracker section, and would otherwise learn only from
    the trigger paragraphs that one of the two shelving records is reachable
    and the other is not.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert SCOPE_GATE_TRIGGER_SPLIT in part_c, (
            f"{relpath}: part (c) no longer states that Trigger A is reachable "
            "for a `blocker` on the Defer-with-narrowing branch, so the gate "
            "and the tracker describe different sets of producible entries"
        )


def test_scope_bounding_gate_reconciles_its_defer_bullet_for_a_blocker():
    """Part (c) disposes of its Defer bullet's non-blocker clauses before the bullet.

    Both gates present one `Defer to follow-up Issue` bullet, written for the
    `suggestion` / `nit` case, and both must reconcile it against the blocker
    branch. This is part (c)'s half; `ROUTING_GATE_BLOCKER_PAIRING` is part
    (d)'s, and it is anchored the same way and for the same reason.

    The anchor is the **blocker-summary paragraph**, not part (c) at large,
    because ordering is the contract: the reconciliation exists to qualify the
    bullet *before* a reader reaches it, exactly as the mechanical
    shelving-bullet guard requires of the severity rule itself. A sentence
    sitting anywhere in part (c) satisfies a part-wide check — including below
    the bullet it corrects, where an orchestrator assembling the choice has
    already passed it and acted on the unqualified text. That position is
    asserted outright rather than left to the anchor, so the guard states the
    ordering it depends on instead of inheriting it from today's layout.

    Note the anchor is *not* part (c)'s severity lead, the way part (d)'s is.
    The two parts are shaped differently: part (d) states its severity rule as
    one paragraph, while part (c) opens with a one-line lead, hangs the blocker
    choice set off it as sub-bullets, and closes with this summary paragraph.

    The third clause is why this is not merely tidy. The first two produce
    contradictions, which a careful reader notices and resolves. The soft-fix
    identification produces something worse — a *followable* instruction: ship
    "the most complete of the enumerated paths that remain". Followed on a
    blocker, that dispatches a path the severity rule never authorised while
    the narrowing the branch requires goes out undispatched, and the run looks
    normal throughout.
    """
    for relpath in ORCHESTRATORS:
        summary = paragraph_starting(relpath, SCOPE_GATE_BLOCKER_SUMMARY_LEAD)
        assert SCOPE_GATE_DEFER_BULLET_RECONCILIATION in summary, (
            f"{relpath}: part (c)'s blocker-summary paragraph no longer "
            "reconciles the `Defer to follow-up Issue` bullet's closing clauses "
            "with the blocker branch — its never-invent-a-narrowing prohibition "
            "then reads as forbidding the very narrowing the branch requires, "
            "and its soft-fix identification reads as directing a leftover "
            "enumerated path to ship in the narrowing's place"
        )

        part_c = routing_parts(relpath)["c"]
        reconciliation_at = part_c.index(SCOPE_GATE_DEFER_BULLET_RECONCILIATION)
        defer_bullets = [
            offset
            for offset, line in enumerate(part_c.splitlines())
            if line.startswith(DEFER_BULLET)
        ]
        assert len(defer_bullets) == 1, (
            f"{relpath}: expected exactly one {DEFER_BULLET!r} line in part (c), "
            f"found {len(defer_bullets)}"
        )
        defer_at = part_c.index(DEFER_BULLET)
        assert reconciliation_at < defer_at, (
            f"{relpath}: part (c)'s reconciliation sits at offset "
            f"{reconciliation_at}, below the `Defer to follow-up Issue` bullet "
            f"at {defer_at} — an orchestrator assembling that choice reads the "
            "bullet's non-blocker clauses and acts on them before reaching the "
            "sentence that withdraws them"
        )


def test_post_completion_phase_2_challenges_all_three_blocker_violation_shapes():
    """PHASE 2 catches every shape a shelved blocker can take, at `blocker` severity.

    This is the backstop for the whole severity rule: the gates should never
    produce any of these entries, so if one exists the run already violated the
    contract, and the post-completion reviewer is the last reader positioned to
    say so. Emitting it below `blocker` severity would let it be dispositioned
    as a nit.

    Three shapes, not one, because the Defer route is now conditional rather
    than closed. An accepted blocker is the flat violation; a deferral with no
    narrowing record is the deferral that shelved rather than narrowed; and a
    deferral whose narrowing left the stated defect partly unfixed is the one
    that *looks* legitimate — it carries a record, and the record is the
    evidence against it. Dropping the third leaves the branch's only real
    failure mode uncovered.
    """
    for relpath in ORCHESTRATORS:
        phase_2 = phase_block(relpath, 2)
        for shape in PHASE_2_VIOLATION_SHAPES:
            assert shape in phase_2, (
                f"{relpath}: PHASE 2 no longer names {shape!r} among the "
                "tracker-entry shapes that are a contract violation"
            )
        assert PHASE_2_CHALLENGE_SEVERITY in phase_2, (
            f"{relpath}: PHASE 2 no longer pins the severity of the "
            "shelved-blocker challenge at `blocker`"
        )


def test_the_phase_2_violation_class_is_routed_past_the_recovery_gates():
    """The post-completion step-7 exclusion describes the same class PHASE 2 emits.

    PHASE 2's output is the one `[compromise-challenge]` class with nothing to
    recover — the entry records a choice the gates should never have produced —
    so it is dispositioned by the generic Fix / File / Skip gate alone. That
    exclusion is stated by naming the class and enumerating its shapes, which
    makes it a second reader of PHASE 2's violation set: a shape added to
    PHASE 2 and not here arrives at a recovery gate written for a class it is
    not in, and one dropped here silently sends the whole class through a
    fourth gate the step forbids inventing.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        assert RECOVERY_GATE_EXCLUDED_CLASS in text, (
            f"{relpath}: the post-completion recovery-gate step no longer names "
            "PHASE 2's contract-violation class as the one with no recovery gate"
        )
        assert RECOVERY_GATE_EXCLUDED_SHAPES in text, (
            f"{relpath}: the recovery-gate exclusion no longer enumerates the "
            "same three violation shapes PHASE 2 emits, so the two ends "
            "describe different classes"
        )


def test_the_file_issue_failure_bullet_withholds_the_narrowing_on_a_blocker():
    """Part (f) attaches a consequence to part (c)'s file-first ordering.

    Filing first is only enforceable if something happens when the filing
    fails. This bullet is that something: the narrowing has not shipped yet, so
    withholding it is still possible, and a blocker whose follow-up Issue never
    got filed is a blocker with neither a fix nor a ticket carrying the
    deferred design. Without the bullet the ordering rule reads as a
    preference — and the bullet's own earlier text said a blocker could never
    reach it at all, which is the reading this branch made false.
    """
    for relpath in ORCHESTRATORS:
        assert FILE_ISSUE_FAILURE_REACHES_A_BLOCKER in routing_parts(relpath)["f"], (
            f"{relpath}: part (f)'s `/quo-file-issue` failure bullet no longer "
            "says a `blocker` can reach it, or no longer withholds the "
            "narrowing when the filing failed"
        )


def test_the_tracker_rationale_field_spec_describes_the_narrowing_record():
    """Both statements of the `Rationale` field say what a blocker deferral puts there.

    Trigger A writes the narrowing record into `Rationale`; the field spec is
    what every reader of the tracker — PHASE 2, the PM's check, the close-out's
    render step — consults for what that field holds. A spec that describes
    only the ungated-pick and user-reason cases leaves the record looking like
    free-form commentary rather than the artifact those three readers test
    against. The spec is stated twice per skill (the entry template's
    placeholder and the five-fields prose), so both carriers are counted.
    """
    for relpath in ORCHESTRATORS:
        occurrences = read(relpath).count(TRACKER_RATIONALE_NARROWING_CLAUSE)
        assert occurrences == TRACKER_RATIONALE_CARRIERS, (
            f"{relpath}: expected {TRACKER_RATIONALE_CARRIERS} statements of the "
            "`Rationale` field spec naming a blocker deferral's narrowing "
            f"record (the entry template and the five-fields prose), found "
            f"{occurrences}"
        )


def test_pm_never_annotates_a_blocker_with_a_deferral_destination():
    """`agents/pm.md` allows a blocker only the address-now destination.

    The PM's deferral-destination contract is a second route to shelving a
    blocker that bypasses both gates entirely: an item annotated
    `defer-to-new-Issue` is filed at the deferral-hygiene gate without any
    severity check.
    """
    text = read(AGENT_PM)
    assert (
        "**This is the only permitted destination for a `blocker`-severity "
        "item:**" in text
    ), (
        f"{AGENT_PM}: `addressed-now-in-this-Task` is no longer declared the only "
        "permitted destination for a blocker"
    )
    assert (
        "a blocker is never annotated `defer-to-existing-ticket-body` or "
        "`defer-to-new-Issue`" in text
    ), (
        f"{AGENT_PM}: the prohibition on annotating a blocker with a deferral "
        "destination is gone"
    )
    assert PM_BLOCKER_DESTINATION_RATIONALE in text, (
        f"{AGENT_PM}: the blocker-destination rule no longer says *why* the "
        "PM's channel cannot carry a deferral the gates now can — that the "
        "gates pair one with a dispatched narrowing and a tracker entry, and a "
        "`defer-*` ledger entry pairs it with nothing. Unexplained, the rule "
        "reads as an asymmetry to be corrected rather than a design"
    )
    assert PM_BLOCKER_NOT_THE_PMS_TO_SHELVE in text, (
        f"{AGENT_PM}: the blocker-destination rule's closing instruction no "
        "longer routes the outcome to the gates — if it has gone back to "
        "asserting the blocker must be fixed in this scope, it contradicts the "
        "Defer-with-narrowing branch both gates now carry"
    )


def test_pm_reports_a_shelved_blocker_tracker_entry_as_a_blocker_finding():
    """The PM reads the tracker and re-surfaces a shelved blocker in flight.

    PHASE 2 catches this only after the run is over. The PM is dispatched per
    unit while there is still a lane to fix it in, so its check is the earlier
    of the two — and it only works if the finding comes back in the ordinary
    shape the orchestrator can route.
    """
    text = read(AGENT_PM)
    assert PM_TRACKER_CHECK_LEAD in text, (
        f"{AGENT_PM}: the compromise-tracker deferred-blocker check is missing "
        "from the report contract"
    )
    assert (
        "Report each such entry as a `blocker`-severity finding in this report"
        in text
    ), (
        f"{AGENT_PM}: the deferred-blocker check no longer reports its entries at "
        "`blocker` severity"
    )
    assert "**at least one** lettered fix-path line carrying a depth tag" in text, (
        f"{AGENT_PM}: the deferred-blocker finding no longer has to carry a "
        "lettered fix path, so the orchestrator would get a shapeless emission "
        "it cannot route"
    )


def test_pm_requires_a_blocker_narrowing_to_still_cover_the_stated_defect():
    """The PM reads the narrowing record against the defect, not just for its presence.

    A blocker deferral is legitimate only when the narrowing that shipped with
    it still covers the unit's stated defect — narrow past that and the
    deferral has bought itself the very defect the blocker named. Checking only
    that a record exists passes every such entry, which makes the record a
    formality rather than the thing that distinguishes a legitimate deferral
    from a shelved blocker. The PM is the earliest of the three readers of this
    guard (the gates set it, PHASE 2 catches it after the run) and the only one
    dispatched while a lane is still open to fix it.
    """
    assert PM_NARROWING_MUST_COVER_THE_DEFECT in read(AGENT_PM), (
        f"{AGENT_PM}: the tracker check no longer requires a blocker's "
        "narrowing to still cover the unit's stated defect, so any deferral "
        "carrying a record at all reads as legitimate"
    )


def test_pm_names_an_already_resolved_tracker_entry_in_one_line():
    """A violation the diff under review has already fixed is reported, not re-raised.

    The tracker is append-only and this check reads it without amending it, so
    an entry stays on the file after the deferred blocker has been re-opened
    and addressed. Re-emitted as a `blocker` finding, that entry sends the
    orchestrator routing a fix path for work already sitting in the tree the PM
    is reading — a round spent on nothing, repeated every pass. The one-line
    treatment is the same one the bullet gives an earlier unit's entries.
    """
    text = read(AGENT_PM)
    assert PM_RESOLVED_ENTRY_ONE_LINE in text, (
        f"{AGENT_PM}: the tracker check no longer distinguishes an entry the "
        "diff under review has already resolved, so it re-raises a fixed "
        "violation as a `blocker` finding once per pass"
    )
    assert PM_TRACKER_IS_READ_ONLY in text, (
        f"{AGENT_PM}: the tracker check no longer states that it reads the "
        "entry without amending it — the natural next move on a stale entry is "
        "to correct it, which rewrites the run's only record of a routing "
        "decision underneath PHASE 2, which reads the same file afterwards"
    )


def test_both_orchestrators_pass_the_tracker_path_to_their_pm():
    """The PM's tracker check is reachable only if the dispatch supplies a path.

    `agents/pm.md` reads the tracker file itself and skips the check when no
    path is supplied. That makes the placeholder in each skill's PM dispatch
    prompt load-bearing: drop it and the check degrades to a one-line "skipped"
    note in every run, silently.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        assert (
            f"and `{TRACKER_PATH_PLACEHOLDER}`, this run's compromise-tracker "
            "path" in text
        ), (
            f"{relpath}: the PM dispatch prompt no longer passes "
            f"`{TRACKER_PATH_PLACEHOLDER}`, so `{AGENT_PM}`'s deferred-blocker "
            "check can never run"
        )
        assert "carries the deferred-blocker check that path enables" in text, (
            f"{relpath}: the PM dispatch prompt no longer says what the tracker "
            "path is for"
        )


# --------------------------------------------------------------------------
# Every routing-gate `Cancel` — routed through the shared aborted-unit close-out
# --------------------------------------------------------------------------


def test_routing_gate_cancel_routes_through_the_aborted_close_out():
    """Every `Cancel` at a routing gate exits through the shared close-out.

    The pre-fix `Cancel` returned to the batch directly, skipping the
    `aborted-*` marker sweep, the deferral-hygiene gate, and the boundary
    state-externalization checkpoint. Naming the close-out is what makes all
    abort routes behave identically.

    Execute mode has a **second** producer — part (c)'s `Cancel`, in a
    `blocker`'s base pair — and it needs the same pin from the gate end. The
    close-out's router sentence claims that branch, but a claim from one end is
    not a route: the bullet the orchestrator actually reads when assembling the
    choice is part (c)'s, and a bullet that stops the run without naming the
    close-out skips the same three steps the pre-fix `Cancel` did. Part (c)'s
    bullet is nested under the base-pair sub-list, so it is matched on the
    stripped line rather than at column zero.
    """
    for relpath in ORCHESTRATORS:
        cancel_bullets = [
            line
            for line in routing_parts(relpath)["d"].splitlines()
            if line.startswith("- **Cancel**")
        ]
        assert len(cancel_bullets) == 1, (
            f"{relpath}: expected exactly one `Cancel` choice bullet in part "
            f"(d), found {len(cancel_bullets)}"
        )
        assert f"Route through `{CLOSE_OUT_HEADING[relpath]}`" in cancel_bullets[0], (
            f"{relpath}: part (d)'s `Cancel` no longer routes through "
            f"`{CLOSE_OUT_HEADING[relpath]}` — it would skip the marker sweep, "
            "the deferral-hygiene gate, and the boundary checkpoint"
        )

    # Execute mode's second producer, in part (c)'s base pair.
    part_c_cancels = [
        line.lstrip()
        for line in routing_parts(QUO_EXECUTE)["c"].splitlines()
        if line.lstrip().startswith("- **Cancel**")
    ]
    assert len(part_c_cancels) == 1, (
        f"{QUO_EXECUTE}: expected exactly one `Cancel` choice bullet in part "
        f"(c)'s blocker base pair, found {len(part_c_cancels)}"
    )
    # Matched on the heading alone, not on a `Route through` prefix: part (c)'s
    # bullet names the close-out mid-sentence ("route through ..."), where part
    # (d)'s opens with it. The contract is that the bullet names the close-out,
    # not that the two bullets are phrased alike.
    assert f"`{CLOSE_OUT_HEADING[QUO_EXECUTE]}`" in part_c_cancels[0], (
        f"{QUO_EXECUTE}: part (c)'s `Cancel` no longer names "
        f"`{CLOSE_OUT_HEADING[QUO_EXECUTE]}` — the close-out claims this branch "
        "from its own end, but the bullet the orchestrator reads would end the "
        "run without the marker sweep, the checkpoint, or the resume command"
    )


def test_the_aborted_close_out_counts_the_routing_gate_cancel_among_its_routers():
    """Each close-out's lead sentence enumerates the routing gate's `Cancel`.

    The pointer has to hold from both ends. The close-out's router list is what
    a reader consults to know which branches reach it, and a `Cancel` that
    points at a close-out the close-out does not claim is the half-landed shape
    this pins against.

    The spelled-out count is pinned alongside the phrase because the count is
    the part that goes stale silently: adding a router and forgetting to
    recount leaves a sentence that says "Two branches" above a list of three,
    and a reader who trusts the number stops reading at the second.

    What this buys, stated exactly: a change-detector over the count word plus
    **two of the three** routers each sentence names. It does not verify that
    the sentence lists as many routers as it counts. Each close-out names three;
    `CANCEL_ROUTER_PHRASE` and `THIRD_ROUTER_PHRASE` cover two of them.

    One acknowledged gap, not covered anywhere in this module: the
    Reconcile-step unexplained-movement gate's **Abort this Issue** / **Abort
    this unit** choice is unpinned. Verified by deletion — removing it from
    either close-out's router sentence leaves every guard here passing, count
    word intact, over a list of two. It is the one router this Issue did not
    touch, so pinning it was declined rather than overlooked; the note exists so
    the next reader does not mistake this guard for a completeness check.
    """
    for relpath in ORCHESTRATORS:
        close_out = heading_section(read(relpath), CLOSE_OUT_HEADING[relpath])
        router_lines = [
            line for line in close_out.splitlines() if CLOSE_OUT_ROUTER_SENTENCE in line
        ]
        assert len(router_lines) == 1, (
            f"{relpath}: expected exactly one {CLOSE_OUT_ROUTER_SENTENCE!r} "
            f"sentence in `{CLOSE_OUT_HEADING[relpath]}`, found "
            f"{len(router_lines)}"
        )
        word = CLOSE_OUT_ROUTER_COUNT_WORD[relpath]
        assert f"{word} branches route here" in router_lines[0], (
            f"{relpath}: `{CLOSE_OUT_HEADING[relpath]}`'s router sentence no "
            f"longer counts {word.lower()} branches — recount it against the "
            "list that follows, which this Issue extended with the "
            "routing-decision gate's `Cancel`"
        )
        assert CANCEL_ROUTER_PHRASE in router_lines[0], (
            f"{relpath}: `{CLOSE_OUT_HEADING[relpath]}` does not list the "
            "routing-decision gate's `Cancel` among the branches that route to "
            "it"
        )
        assert THIRD_ROUTER_PHRASE[relpath] in router_lines[0], (
            f"{relpath}: `{CLOSE_OUT_HEADING[relpath]}`'s router sentence no "
            f"longer names {THIRD_ROUTER_PHRASE[relpath]!r}. This guard covers "
            f"two of the three routers the sentence lists, not the count "
            "itself — so recount the sentence by reading it, rather than "
            "trusting that a passing suite means the list is complete"
        )


def test_execute_checkpoint_invoker_note_counts_the_same_routers():
    """The checkpoint's invoker note and the close-out agree on how many enter it.

    Execute mode states the close-out's entering-branch count in two places:
    the close-out's own router sentence, and the boundary checkpoint's note
    listing the invokers that sit outside Section 4.2's branches. Both were
    "two" before part (c) grew its `Cancel`. The count is derived from the same
    constant the close-out's guard uses, so the two ends cannot be updated
    apart: recount one and this fails until the other follows.
    """
    word = CLOSE_OUT_ROUTER_COUNT_WORD[QUO_EXECUTE].lower()
    assert f"All {word} of that close-out's entering branches" in read(QUO_EXECUTE), (
        f"{QUO_EXECUTE}: the Epic-boundary checkpoint's invoker note no longer "
        f"counts {word} entering branches for "
        f"`{CLOSE_OUT_HEADING[QUO_EXECUTE]}` — it and the close-out's own "
        "router sentence now disagree on how many branches reach the checkpoint"
    )


def test_execute_close_out_bridges_its_two_cancel_branches():
    """One sentence makes execute's `Cancel`-branching prose cover both gates.

    Execute mode grew a second `Cancel` producer at part (c), but the
    close-out's own steps — which scope to sweep, whether an `aborted-*` marker
    is open, how the checkpoint resolves scope, what the Progress entry says,
    what the stop message names — were all written naming "a routing-gate
    `Cancel`", meaning part (d)'s. Rather than editing each of those sites to
    enumerate two branches, the close-out states the equivalence once. That
    makes this sentence load-bearing in a way its brevity hides: delete it and
    every one of those steps reads as specified for the other branch, so part
    (c)'s `Cancel` reaches a close-out with no defined behavior at any step.

    Execute-only. `/quo-fix-issue` has a single routing-gate `Cancel` (its part
    (c) offers the Analyst re-dispatch in that slot), so there is no
    equivalence for it to state.
    """
    close_out = heading_section(read(QUO_EXECUTE), CLOSE_OUT_HEADING[QUO_EXECUTE])
    assert EXECUTE_CANCEL_EQUIVALENCE in close_out, (
        f"{QUO_EXECUTE}: `{CLOSE_OUT_HEADING[QUO_EXECUTE]}` no longer states "
        "that its two `Cancel` branches behave identically, so every step "
        "phrased as 'a routing-gate `Cancel`' stops covering part (c)'s"
    )


def test_execute_bee_scope_abort_sweep_clears_the_gate_task():
    """Execute's Bee-scope abort sweep names the `gate-*` task explicitly.

    That scope's sweep is expressed by borrowing Section 5's Bee-level TaskList
    close-out, whose enumeration is `*-<bee-id>` names only — and a gate task is
    named `gate-askuserquestion-<short-suffix>`, which matches none of them. So
    a `Cancel` fired at the Bee-level review would strand the very gate task
    that produced it `pending`, where part (g)'s Clause 2 does not look for it
    but the next session's boundary checkpoint does. The per-Task scope needs no
    such addition: its sweep already enumerates the gate task.
    """
    close_out = heading_section(read(QUO_EXECUTE), CLOSE_OUT_HEADING[QUO_EXECUTE])
    assert EXECUTE_BEE_SCOPE_GATE_SWEEP in close_out, (
        f"{QUO_EXECUTE}: `{CLOSE_OUT_HEADING[QUO_EXECUTE]}`'s Bee-scope sweep no "
        "longer names the `gate-*` task, so a `Cancel` at the Bee-level review "
        "leaves its own gate task `pending`"
    )


# --------------------------------------------------------------------------
# The `[introduces-mechanism]` emitter -> relay -> consumer chain
# --------------------------------------------------------------------------


def test_engineer_review_defines_the_mechanism_token_in_canonical_order():
    """`/quo-engineer-review` is the token's sole emitter and fixes its position.

    The token shares a fix-path line with `[depth:<...>]` and `[preferred]`, and
    `[preferred]`'s own rule pins it *immediately* after the depth tag. Only one
    ordering satisfies both, so the canonical order is what keeps the two rules
    from contradicting each other.
    """
    text = read(QUO_ENGINEER_REVIEW)
    assert MECHANISM_TOKEN_DEFINITION in text, (
        f"{QUO_ENGINEER_REVIEW}: the `{MECHANISM_TOKEN}` token is no longer "
        "defined, so nothing emits the signal row 2 keys on"
    )
    assert MECHANISM_CANONICAL_ORDER in text, (
        f"{QUO_ENGINEER_REVIEW}: the canonical fix-path token order "
        f"{MECHANISM_CANONICAL_ORDER} is gone"
    )


def test_engineer_review_worked_example_emits_the_mechanism_token():
    """A worked example shows both optional tokens on one line.

    The line shapes are prose; the worked examples are what a reviewer actually
    pattern-matches against. An optional token with no example is the one that
    gets emitted in the wrong position or not at all.
    """
    text = read(QUO_ENGINEER_REVIEW)
    assert "[depth:refactor-locally] [preferred] [introduces-mechanism]" in text, (
        f"{QUO_ENGINEER_REVIEW}: no worked example emits `{MECHANISM_TOKEN}` "
        "alongside `[preferred]` in the canonical order"
    )


def test_both_relayers_pass_the_mechanism_token_through():
    """Both `/quo-engineer-review` wrappers relay the token to the orchestrator.

    These two role files are the entire path between the emitter and the
    orchestrator's row 2. A dropped relay does not fail loudly — it demotes
    every tagged path to orchestrator-side detection, which the routing prose
    calls the fallback, so mechanism findings quietly stop reaching the
    scope-bounding gate. (Row 2's own wording is pinned by
    `test_both_orchestrators_carry_the_same_six_routing_rows_in_order`.)
    """
    for relpath in RELAYERS:
        bullets = [
            line
            for line in read(relpath).splitlines()
            if line.strip().startswith(MECHANISM_RELAY_BULLET_LEAD)
        ]
        assert len(bullets) == 1, (
            f"{relpath}: expected exactly one `{MECHANISM_TOKEN}` relay bullet, "
            f"found {len(bullets)}"
        )
        assert "primary** signal" in bullets[0], (
            f"{relpath}: the relay bullet no longer says the tag is the "
            "orchestrator's primary routing signal, which is why dropping it "
            "matters"
        )


def test_four_artifacts_define_the_mechanism_by_citing_the_analyst_role():
    """The definition is consumed by pointer, from four files, and stated in none.

    This is the near half of the chain's fifth link. All four citers — both
    orchestrators' row-2 fallback reading, the emitter's tagging criterion, and
    the relaying role file — say "per the mechanism definition in
    `agents/analyst.md`" instead of restating the enumeration, which is what
    keeps one definition from becoming four that drift. The cost of that choice
    is that the citation is the *only* thing tying row 2 to a definition: drop
    it and both the tag's emission criterion and the orchestrator's fallback
    lose their referent while every surface still reads as though defined.
    """
    for relpath in MECHANISM_DEFINITION_CITERS:
        assert MECHANISM_DEFINITION_CITATION in read(relpath), (
            f"{relpath}: no longer cites {MECHANISM_DEFINITION_CITATION!r}, so "
            f"its use of `{MECHANISM_TOKEN}` / \"introduces a mechanism\" has no "
            "definition behind it"
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "The definition lands in `agents/analyst.md` with the concurrent "
        "sibling change b.q3f, whose Amendment 3 specifies it; this Issue's own "
        "change set deliberately does not write it (docs/sdd.md records the "
        "forward-looking pointer). REMOVE THIS MARKER when b.q3f lands — under "
        "strict mode this test reports XPASS, which fails the run, the moment "
        "the definition appears."
    ),
)
def test_analyst_role_carries_the_mechanism_definition_its_citers_point_at():
    """The far half of the fifth link: the citation target actually exists.

    Four shipped artifacts point at `agents/analyst.md` for what "introduces a
    mechanism" means, and in this worktree that file carries no such
    definition — a dangling pointer that a reader following it today resolves
    to nothing, quietly degrading row 2's fallback to whatever the reader
    already believed. The definition is not this Issue's to write: it is
    specified by the concurrent sibling change b.q3f and is the one place a
    ticket ID belongs in this suite, because the marker's removal condition is
    that ticket landing.

    `xfail(strict=True)` is the shape that fits: the pin exists now, so the
    dangling link is visible as an XFAIL in every run's report rather than
    living only in review prose, and strict mode converts the fix into a loud
    XPASS failure — so the marker cannot outlive the condition it documents.
    The assertion deliberately anchors on the enumeration's vocabulary and not
    on a heading or a sentence, since neither is knowable from here.
    """
    text = read(AGENT_ANALYST).lower()
    assert "mechanism" in text, (
        f"{AGENT_ANALYST}: does not mention a mechanism at all, so the "
        f"{MECHANISM_DEFINITION_CITATION!r} citation carried by "
        f"{len(MECHANISM_DEFINITION_CITERS)} shipped artifacts dangles"
    )
    missing = [
        group
        for group in MECHANISM_DEFINITION_TERM_GROUPS
        if not any(term in text for term in group)
    ]
    assert not missing, (
        f"{AGENT_ANALYST}: mentions a mechanism but enumerates none of "
        f"{missing} — the citers need an enumeration to read a fix path "
        "against, not the bare word"
    )


def test_engineer_review_compat_constraint_names_every_routing_input():
    """The constraint enumerates exactly what routing parses, and nothing else.

    Its job is to tell a reviewer which surface is read, so an under-count is
    the harmful direction: a token left out reads as "routing ignores this",
    and a reviewer who believes that stops emitting it. The tokens are pinned
    individually rather than as one sentence because the sentence around them
    is free prose, while the set is the contract.
    """
    constraint = paragraph_starting(QUO_ENGINEER_REVIEW, COMPAT_CONSTRAINT_LEAD)
    for token in COMPAT_ROUTING_INPUTS:
        assert token in constraint, (
            f"{QUO_ENGINEER_REVIEW}: the compatibility constraint no longer "
            f"names {token!r} among the inputs the orchestrator's routing "
            "reads — a reviewer reading it would take that input to be ignored"
        )


# --------------------------------------------------------------------------
# The `[preferred]` closing clause across all five emitters
# --------------------------------------------------------------------------


def test_every_fix_path_emitter_states_that_no_preferred_is_valid():
    """All five emitters carry the same closing clause, once each.

    `[preferred]` is optional, and the consumer picks its own path regardless.
    An emitter missing this clause reads the surrounding "emit it when your
    preference is real" prose as an obligation and marks a path it does not
    actually prefer — which feeds Step 1 a false input. There is no shared
    carrier for the clause: five files each hold a copy, and `/quo-plan`'s is
    hard-wrapped, so the comparison runs over squeezed text.
    """
    for relpath in PREFERRED_EMITTERS:
        occurrences = squeeze(read(relpath)).count(PREFERRED_CLOSING_CLAUSE)
        assert occurrences == 1, (
            f"{relpath}: expected exactly one copy of the `[preferred]` closing "
            f"clause, found {occurrences} — the five emitters' copies must stay "
            "identical, and a missing one lets that emitter read `[preferred]` "
            "as mandatory"
        )


# --------------------------------------------------------------------------
# The PM's unit-scoped reading of a run-scoped tracker
# --------------------------------------------------------------------------


def test_pm_reports_an_out_of_scope_tracker_violation_as_a_note_not_a_finding():
    """A violation from an earlier unit is named once, without a fix path.

    The tracker is run-scoped and the PM is unit-scoped, so every PM after the
    offending unit sees the same violating entry. Emitted as a finding it would
    be re-raised once per remaining unit against a scope that cannot fix it —
    and, carrying no depth tag, each re-raise would hit the routing section's
    untagged-emission shim and fire a user gate. Saying the line is a report
    note is what keeps it out of routing entirely.

    Both ends of that exemption are guarded here, because either alone is
    inert. `agents/pm.md` *declares* the note is not a finding; part (e) is
    where the declaration has to be honoured, since its shim is what would
    otherwise pick the note up. They sit in three different files with nothing
    linking them, so the PM can go on declaring an exemption the shim stopped
    granting, and the only symptom is a user gate firing on a report note —
    which reads as the shim working correctly.

    Part (f)'s malformed-tag bullet is pinned with it: it is the shim's sibling
    reader, and an exemption scoped to part (e) alone leaves the note reachable
    by the other route that surfaces untagged emissions to the user.
    """
    text = read(AGENT_PM)
    assert PM_TRACKER_SCOPE_SPLIT in text, (
        f"{AGENT_PM}: the deferred-blocker check no longer splits the "
        "run-scoped tracker's entries by whose diff they concern"
    )
    assert PM_OUT_OF_SCOPE_ONE_LINE in text, (
        f"{AGENT_PM}: an out-of-scope violation is no longer confined to a "
        "one-line, fix-path-free mention"
    )
    assert PM_REPORT_NOTE_CLAUSE in text, (
        f"{AGENT_PM}: the out-of-scope line is no longer declared a report note "
        "rather than a finding, so the orchestrator would route it — and the "
        "untagged-emission shim would gate it"
    )

    for relpath in ORCHESTRATORS:
        part_e = routing_parts(relpath)["e"]
        assert SHIM_REPORT_NOTE_EXEMPTION_LEAD in part_e, (
            f"{relpath}: part (e)'s shim no longer exempts the PM's report "
            f"note, so `{AGENT_PM}` declares an exemption the shim does not "
            "grant — the note is read as `re-architect` and gated"
        )
        assert SHIM_REPORT_NOTE_PART_F_CLAUSE in part_e, (
            f"{relpath}: part (e)'s exemption no longer extends to part (f)'s "
            "malformed-tag bullet, leaving the report note reachable by the "
            "shim's sibling reader"
        )


# --------------------------------------------------------------------------
# The tracker-absent readers agree with Trigger C
# --------------------------------------------------------------------------


def test_checkpoint_gap_test_defers_to_trigger_c_on_which_picks_need_an_entry():
    """The checkpoint asks Trigger C whether a missing entry is a gap.

    Stated as "an ungated path pick was dispatched", the gap test contradicts
    the trigger it verifies: a run whose only ungated route hit Trigger C's
    lone-`trivial-tweak` carve-out is correctly entry-less, and the checkpoint
    would tell the orchestrator to append the entry Trigger C says not to
    write. Deferring the condition to Trigger C is what keeps one rule.
    """
    for relpath in ORCHESTRATORS:
        assert CHECKPOINT_GAP_QUALIFIER in read(relpath), (
            f"{relpath}: the state-externalization checkpoint's tracker gap "
            "test no longer defers to Trigger C on which ungated picks oblige "
            "an entry"
        )


def test_tracker_absent_render_note_states_when_an_ungated_pick_appends():
    """The render step's rarity note agrees with Trigger C on when an entry is due.

    The note explains why an absent tracker file is now uncommon, which is what
    stops a reader from treating "no file" as the expected state. Its condition
    has to be Trigger C's — a pick among two or more paths, with the
    lone-`trivial-tweak` carve-out as the only ungated route that appends
    nothing — or the note either understates how often an entry is due or
    describes a write Trigger C does not make.
    """
    for relpath in ORCHESTRATORS:
        assert TRACKER_ABSENT_RENDER_CLAUSE in read(relpath), (
            f"{relpath}: the tracker-absent render note no longer states "
            "Trigger C's own condition for when an ungated pick appends an "
            "entry"
        )
