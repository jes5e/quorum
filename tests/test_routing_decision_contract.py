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

  5. **A half-landed composed path.** Step 1 may compose a fix path no reviewer
     enumerated and assign it a depth. That one branch has five readers — the
     section lead's never-invent carve-out, the completeness definition (which
     exempts a composed path from row 4), both gates' presentation rules, and
     Trigger C's entry shape — and each is a separate paragraph in a separate
     part of two separate files. Any one of them left behind turns the branch
     into a path that is picked and then mis-routed, mis-presented, or
     unrecorded.

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
# prose. The two skills' copies of the sentence diverge after the shared count
# clause (execute mode's tail adds "and whether the gate fires at all"), so only
# the clause below is pinned.
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

# Step 1's two copies differ in exactly one token — the compromise-tracker
# section each skill numbers differently (7.5 in fix mode, 6.5 in execute mode).
# Normalizing every `Section <n>` / `Section <n>.<m>` reference to one token is
# what lets the rest of the paragraph be compared byte-for-byte; the paragraph
# carries no other numbered cross-reference, so the normalization cannot mask a
# real divergence.
SECTION_REF = re.compile(r"Section \d+(?:\.\d+)?")
SECTION_REF_TOKEN = "Section <n>"

# Step 1's compose branch: the orchestrator may write a path no reviewer
# enumerated, and must assign it a depth so Step 2 can route it.
STEP_1_COMPOSE_CLAUSES = (
    "**The enumeration is the menu, not a ceiling.**",
    "the orchestrator may **compose** the complete fix itself and pick that "
    "composed path",
    "**Assign the composed path a depth** from the reviewer's own three-value "
    "vocabulary",
    "Step 2's rows 5 and 6 read that assigned value wherever they say \"the "
    "chosen path's depth tag\"",
)

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

# The section lead's never-invent rule, and the one carve-out that keeps Step
# 1's depth assignment from contradicting it.
NEVER_INVENT_RULE = (
    "the depth of a path the reviewer enumerated is the reviewer's call, read "
    "as emitted, and is the one classification the orchestrator must never "
    "invent"
)
COMPOSED_ORIGINATION_CARVE_OUT = (
    "**One carve-out, and only one:** a path the orchestrator **composes** at "
    "Step 1 carries no reviewer depth tag because no reviewer ever saw it, so "
    "the orchestrator assigns that path a depth itself (Step 1 below). That is "
    "origination, not re-classification"
)

# The definition's closing clause, which is what stops the compose branch from
# looping: a composed path is complete by construction, so row 4 (narrower than
# the complete fix) can never send it to gate (c).
HIGHEST_QUALITY_COMPOSED_CLAUSE = (
    "**This definition is what a composed path is composed to**: a path the "
    "orchestrator writes because no enumerated one met it, so a composed path "
    "never satisfies row 4 by construction"
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

# --- The composed path across its four downstream readers ---------------------

GATE_C_COMPOSED_CONTEXT = (
    "**When the Step-1 pick was a composed path**, that context line also "
    "describes it — its letter, the depth Step 1 assigned it, and what it does"
)
GATE_C_COMPOSED_CROSS_REF = (
    "This is the same rule part (d)'s composed-path clause carries at its own "
    "gate."
)
GATE_D_COMPOSED_CHOICE = (
    "**When the Step-1 pick was a composed path** routed here by row 5, "
    "present that composed path as a choice of its own alongside the "
    "reviewer's — under the next unused letter, described in full — and mark "
    "**it** `(Recommended)` per the rule above"
)
TRIGGER_C_COMPOSED_CARVE_OUT = (
    "**The carve-out is evaluated on the reviewer's enumeration alone, and "
    "never applies when the Step-1 pick was composed:** composing is itself a "
    "pick between what the reviewer enumerated and a path no reviewer "
    "proposed, so a composed entry always appends however few — or however "
    "shallow — the enumerated paths were."
)

# Trigger C's composed-entry field substitution. The two skills carry it in
# different containers (an inline clause in fix mode, its own bullet in execute
# mode) and differ in sentence-initial casing, so the shared *clauses* are
# pinned rather than a whole sentence.
TRIGGER_C_COMPOSED_FIELDS = (
    "write the **next unused letter** after the reviewer's own in the `(x)` "
    "slot",
    "**carrying the depth Step 1 assigned it**",
    "in `Rationale` that **the reviewer did not enumerate this path**",
    "**what the enumerated paths lacked**",
)

# The inline marker the composed line carries in the paths field. The `Rationale`
# clauses above already say the path was composed, but PHASE 4 judges the
# reviewer's under-enumeration off the paths field alone; an unmarked composed
# line inflates that field with a path the reviewer never proposed, and does so
# in exactly the case where the composition is the evidence of under-enumeration.
TRIGGER_C_COMPOSED_INLINE_MARKER = (
    "(orchestrator-composed — not enumerated by the reviewer)"
)

# The two places the state-externalization checkpoint reasons about an absent
# tracker file. Both have to agree with Trigger C about which picks oblige an
# entry, or the checkpoint reports a gap for an entry Trigger C forbids.
CHECKPOINT_GAP_QUALIFIER = (
    "an ungated path pick **that Trigger C requires an entry for** was "
    "dispatched"
)
TRACKER_ABSENT_RENDER_CLAUSE = (
    "an ungated path pick appends an entry whenever the pick was among two or "
    "more paths, or was composed"
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
RETIRED_DECISION_VALUE = "Auto-routed (a) per single-path refactor-locally rule"

# The two halves of the enum value that survive the per-entry letter
# substitution. PHASE 3 must match on exactly these, since the letter varies.
DECISION_PICK_PREFIX = "Orchestrator picked path ("
DECISION_PICK_SUFFIX = ") — highest-quality"

# --- Severity rule -----------------------------------------------------------

# Both gates lead their severity rule with this. The remainder of the sentence
# differs per gate and per skill (execute mode's part (c) adds "and fires no
# gate here"), so only the shared lead is pinned.
BLOCKER_EXCLUSION_LEAD = "**Severity rules the choice set"

SCOPE_GATE_BLOCKER_RULE = (
    "**Severity rules the choice set — a `blocker` can be neither deferred nor "
    "accepted"
)
SCOPE_GATE_WITHHELD_CHOICES = (
    "the `Defer to follow-up Issue` and `Accept the limitation` choices below "
    "are **unreachable**"
)
ROUTING_GATE_BLOCKER_RULE = (
    "**Severity rules the choice set here too — a `blocker` has no Defer route.**"
)
ROUTING_GATE_WITHHELD_CHOICE = (
    "the `Defer to follow-up Issue` choice below is **unreachable**"
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
NON_BLOCKER_QUALIFIER = "**non-`blocker`**"

# The two clauses of that paragraph that are shared verbatim, pinned in the
# `MECHANISM_PRIMARY_SIGNAL` idiom rather than as a whole-paragraph mirror: the
# copies legitimately diverge in how each skill states the blocker exclusion,
# because the two gates withhold differently — fix mode drops the choice from a
# gate that still fires ("the choice does not exist at all"), execute mode does
# not fire the gate at all. Only the clauses below are mirrored prose.
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

TRIGGER_BLOCKER_CLAUSE = "**Unreachable for a `blocker`-severity finding**"

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
# fixed, which added `Cancel` as fix mode's third router and execute mode's
# second. The counts differ because fix mode has one router execute mode has
# no analogue for (Section 3's Analyst-proposal gate).
CLOSE_OUT_ROUTER_COUNT_WORD = {
    QUO_FIX_ISSUE: "Three",
    QUO_EXECUTE: "Two",
}
CANCEL_ROUTER_PHRASE = (
    "the routing-decision gate's **Cancel** choice (part (d) of "
    "`### Orchestrator discipline: routing review findings`)"
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
    "**Any deferred or accepted `blocker` the run's compromise tracker records.**"
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

    The tuple was the orchestrator's parse input, and three artifacts besides
    the orchestrators described it as such — `/quo-engineer-review`'s
    compatibility constraint and `/quo-spec-review`'s severity-rendering note
    among them. A surviving mention tells a reader the routing still keys on a
    path *count*, which is exactly the rule this Issue removed.

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

    Only the shared count clause is pinned. The sentence's tail diverges
    between the two skills — execute mode's adds "and whether the gate fires at
    all" — so it is not mirrored prose and is not compared as such.
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


def test_step_1_carries_the_compose_branch_in_both_orchestrators():
    """Step 1 lets the orchestrator write a path no reviewer enumerated.

    Without this branch the only move available when every enumerated path is
    a narrowing is to pick the least-bad one and route it to gate (c) via row
    4 — which is a user gate fired to ask about a menu the orchestrator has
    already judged incomplete. The depth-assignment sentence is part of the
    same branch, not decoration: a composed path with no depth would fall to
    row 1 and gate anyway, undoing the branch.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, STEP_1_LEAD)
        for clause in STEP_1_COMPOSE_CLAUSES:
            assert clause in paragraph, (
                f"{relpath}: Step 1 no longer carries the clause {clause!r} — "
                "the compose branch is incomplete, and a composed path either "
                "cannot be picked or reaches Step 2 with no depth to route on"
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

    It is duplicated prose with no shared carrier, and the two copies differ in
    exactly one token: the compromise-tracker section each skill numbers for
    itself. Normalizing that reference is what lets the rest be compared
    byte-for-byte — a difference anywhere else is drift, and drift in the
    orchestrator's only judgment step means the two skills pick differently on
    the same finding.
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


def test_the_never_invent_rule_carves_out_the_composed_path():
    """The section lead scopes "never invent a depth" to enumerated paths.

    Step 1 has the orchestrator assign a depth to a path it composed, which
    reads as a flat contradiction of the lead's never-invent rule unless the
    lead names the carve-out. Losing either half leaves the section telling the
    orchestrator both to assign the depth and never to — and the resolution a
    reader picks decides whether composed paths route at all.
    """
    for relpath in ORCHESTRATORS:
        section = routing_section(read(relpath))
        assert NEVER_INVENT_RULE in section, (
            f"{relpath}: the routing section no longer scopes the never-invent "
            "rule to the depth of a path the reviewer enumerated"
        )
        assert COMPOSED_ORIGINATION_CARVE_OUT in section, (
            f"{relpath}: the routing section states the never-invent rule with "
            "no carve-out for a composed path, so Step 1's depth assignment "
            "now contradicts it"
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


def test_a_composed_path_can_never_satisfy_row_four():
    """The definition closes the compose-then-gate-anyway loop.

    Row 4 sends a path narrower than the complete fix to gate (c). A composed
    path is written *to* the completeness definition, so it cannot be narrower
    than it — and saying so is what stops an orchestrator from composing a
    complete fix and then routing it to the very gate composing exists to
    avoid.
    """
    for relpath in ORCHESTRATORS:
        paragraph = paragraph_starting(relpath, HIGHEST_QUALITY_LEAD)
        assert HIGHEST_QUALITY_COMPOSED_CLAUSE in paragraph, (
            f"{relpath}: the highest-quality definition no longer says a "
            "composed path never satisfies row 4, so a composed pick can be "
            "read back onto the narrowing row and gated"
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
# The composed path's four downstream readers
# --------------------------------------------------------------------------


def test_scope_bounding_gate_describes_a_composed_pick_in_its_context_line():
    """Gate (c) shows the user the path it is asking about.

    The question text reproduces the reviewer's finding verbatim, and a
    composed path appears nowhere in it. Without the context line's
    composed-path clause the user is asked to bound the scope of a path they
    cannot see anywhere on the screen.
    """
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert GATE_C_COMPOSED_CONTEXT in part_c, (
            f"{relpath}: part (c)'s context line no longer describes a composed "
            "Step-1 pick, so the gate can fire about a path absent from the "
            "finding text it quotes"
        )
        assert GATE_C_COMPOSED_CROSS_REF in part_c, (
            f"{relpath}: part (c) no longer points at part (d)'s composed-path "
            "clause as the same rule, so the two gates' handling can drift "
            "apart unnoticed"
        )


def test_routing_decision_gate_offers_the_composed_path_as_its_recommendation():
    """Gate (d) presents the composed pick as a choice and recommends it.

    Part (d)'s own rule puts `(Recommended)` on the Step-1 pick. When that pick
    was composed, the reviewer-surfaced choices are exactly the paths the
    orchestrator rejected as incomplete — so a gate that lists only them has no
    choice to mark, and asks the user to ratify a pick it never showed.
    """
    for relpath in ORCHESTRATORS:
        part_d = routing_parts(relpath)["d"]
        assert GATE_D_COMPOSED_CHOICE in part_d, (
            f"{relpath}: part (d) no longer presents a composed Step-1 pick as "
            "its own `(Recommended)` choice"
        )


def test_trigger_c_carve_out_never_applies_to_a_composed_pick():
    """The lone-`trivial-tweak` carve-out is read off the reviewer's list only.

    The carve-out skips the tracker write when the reviewer enumerated a single
    trivial path. A composed pick is a decision *against* that enumeration, so
    reading the carve-out over the composed path's own shape would silently
    drop the only record that the orchestrator went outside the menu — the one
    entry PHASE 3 most needs to challenge.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        assert TRIGGER_C_COMPOSED_CARVE_OUT in text, (
            f"{relpath}: Trigger C's carve-out is no longer scoped to the "
            "reviewer's enumeration alone, so a composed pick can fall through "
            "it and go unrecorded"
        )


def test_trigger_c_records_a_composed_pick_with_its_letter_and_depth():
    """The composed entry carries what PHASE 3 needs to push against.

    A composed entry is the one tracker entry whose path no reviewer vouched
    for, so it needs the most on it: a letter that does not collide with the
    reviewer's, the depth Step 1 originated (PHASE 3's axis (i) has nothing to
    challenge without it), and a rationale saying what the enumerated paths
    lacked. The two skills carry these in different containers, so the shared
    clauses are pinned rather than a whole sentence.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        for clause in TRIGGER_C_COMPOSED_FIELDS:
            assert clause in text, (
                f"{relpath}: Trigger C's composed-entry field substitution no "
                f"longer carries {clause!r}"
            )


def test_trigger_c_marks_the_composed_line_inline_in_the_paths_field():
    """The composed path is labelled where PHASE 4 reads it, not only in Rationale.

    The paths field is one list holding two different kinds of line — what the
    reviewer enumerated, and what the orchestrator composed — and PHASE 4
    judges the reviewer's under-enumeration by counting that list. Without the
    inline marker the two kinds are indistinguishable there, so a composed
    entry makes the reviewer's menu look one path longer than it was, in
    precisely the case where the orchestrator having to compose is the evidence
    the menu was short. The marker is a fixed literal because it is matched by
    a reader, and exactly one per skill because a second copy would mean a
    reviewer-enumerated line had been marked too.
    """
    for relpath in ORCHESTRATORS:
        occurrences = read(relpath).count(TRIGGER_C_COMPOSED_INLINE_MARKER)
        assert occurrences == 1, (
            f"{relpath}: expected exactly one "
            f"{TRIGGER_C_COMPOSED_INLINE_MARKER!r} inline marker in Trigger C's "
            f"composed-path substitution, found {occurrences}"
        )


# --------------------------------------------------------------------------
# The tracker `Decision` value and its post-completion reader
# --------------------------------------------------------------------------


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
    """
    for relpath in ORCHESTRATORS:
        phase_3 = phase_block(relpath, 3)
        enum_line = paragraph_starting(relpath, DECISION_ENUM_LEAD)
        for anchor in (DECISION_PICK_PREFIX, DECISION_PICK_SUFFIX):
            assert anchor in phase_3, (
                f"{relpath}: PHASE 3 of the post-completion prompt no longer "
                f"carries the {anchor!r} anchor, so it cannot match the tracker "
                "entries it exists to challenge"
            )
            assert anchor in enum_line, (
                f"{relpath}: the tracker `Decision` enum no longer carries the "
                f"{anchor!r} anchor that PHASE 3 matches on"
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


def test_scope_bounding_gate_states_a_blocker_is_neither_deferred_nor_accepted():
    """Part (c) withholds both shelving choices from a `blocker`."""
    for relpath in ORCHESTRATORS:
        part_c = routing_parts(relpath)["c"]
        assert SCOPE_GATE_BLOCKER_RULE in part_c, (
            f"{relpath}: part (c) no longer states that a `blocker` can be "
            "neither deferred nor accepted"
        )
        assert SCOPE_GATE_WITHHELD_CHOICES in part_c, (
            f"{relpath}: part (c) no longer names `Defer to follow-up Issue` and "
            "`Accept the limitation` as unreachable for a `blocker`"
        )


def test_routing_decision_gate_states_a_blocker_has_no_defer_route():
    """Part (d) withholds the Defer choice from a `blocker`.

    Part (d) offers no Accept choice at all, so Defer is the whole of what has
    to be withheld here — but withholding it at part (c) alone would leave the
    other gate as an open route to the same outcome.
    """
    for relpath in ORCHESTRATORS:
        part_d = routing_parts(relpath)["d"]
        assert ROUTING_GATE_BLOCKER_RULE in part_d, (
            f"{relpath}: part (d) no longer states that a `blocker` has no Defer "
            "route"
        )
        assert ROUTING_GATE_WITHHELD_CHOICE in part_d, (
            f"{relpath}: part (d) no longer names `Defer to follow-up Issue` as "
            "unreachable for a `blocker`"
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


def test_defer_recommended_default_applies_only_to_non_blocker_findings():
    """The mechanism row's Defer default is qualified to non-`blocker` findings.

    Defer is the *recommended* answer when a chosen path builds machinery the
    ticket never asked for. Left unqualified, that recommendation points at a
    choice a blocker is not allowed to reach, which is a direct contradiction of
    the severity rule two paragraphs above it.

    The qualifier is only meaningful while there is a recommendation for it to
    qualify, so the two shared clauses of the same paragraph are pinned here
    too: the recommendation itself, and the verbatim-handoff sentence that is
    what makes deferring cost a round rather than the reviewer's sketched
    design. They are pinned as clauses rather than as a whole-paragraph mirror
    because the copies legitimately diverge on the blocker exclusion — fix mode
    withholds the choice from a gate that still fires, execute mode does not
    fire the gate at all.
    """
    for relpath in ORCHESTRATORS:
        default_paragraph = paragraph_starting(relpath, MECHANISM_DEFAULT_LEAD)
        assert NON_BLOCKER_QUALIFIER in default_paragraph, (
            f"{relpath}: the mechanism-row Defer default is no longer qualified "
            f"to {NON_BLOCKER_QUALIFIER} findings, so it recommends a choice a "
            "blocker cannot take"
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


def test_tracker_triggers_a_and_b_are_unreachable_for_a_blocker():
    """The two shelving triggers say no blocker entry can exist under them.

    Triggers A and B are the tracker writes for Defer and Accept. They are the
    downstream record of the choices the severity rule withholds, so each has to
    carry the same exclusion — otherwise the tracker still describes a shape the
    gates can no longer produce, and PHASE 2's contract-violation check reads as
    guarding against nothing.
    """
    for relpath in ORCHESTRATORS:
        for trigger in ("**Trigger A — ", "**Trigger B — "):
            paragraph = paragraph_starting(relpath, trigger)
            assert TRIGGER_BLOCKER_CLAUSE in paragraph, (
                f"{relpath}: {trigger.strip('* ')} no longer states it is "
                "unreachable for a `blocker`-severity finding"
            )


def test_post_completion_phase_2_challenges_a_deferred_or_accepted_blocker():
    """PHASE 2 emits a shelved blocker as a `blocker`-severity challenge.

    This is the backstop for the whole severity rule: the gates should never
    produce such an entry, so if one exists the run already violated the
    contract, and the post-completion reviewer is the last reader positioned to
    say so. Emitting it below `blocker` severity would let it be dispositioned
    as a nit.
    """
    for relpath in ORCHESTRATORS:
        phase_2 = phase_block(relpath, 2)
        assert (
            "is a contract violation — a blocker can be neither deferred nor "
            "accepted" in phase_2
        ), (
            f"{relpath}: PHASE 2 no longer names a deferred-or-accepted blocker "
            "tracker entry as a contract violation"
        )
        assert (
            "Emit it as a `[compromise-challenge]` finding at `blocker` "
            "severity, never lower." in phase_2
        ), (
            f"{relpath}: PHASE 2 no longer pins the severity of the "
            "deferred-blocker challenge at `blocker`"
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
# Part (d)'s `Cancel` — routed through the shared aborted-unit close-out
# --------------------------------------------------------------------------


def test_routing_gate_cancel_routes_through_the_aborted_close_out():
    """Part (d)'s `Cancel` exits through the shared close-out, not by hand.

    The pre-fix `Cancel` returned to the batch directly, skipping the
    `aborted-*` marker sweep, the deferral-hygiene gate, and the boundary
    state-externalization checkpoint. Naming the close-out is what makes all
    abort routes behave identically.
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


def test_tracker_absent_render_note_counts_a_composed_pick_as_appending():
    """The render step's rarity note counts composed picks among the appends.

    The note explains why an absent tracker file is now uncommon, which is what
    stops a reader from treating "no file" as the expected state. A composed
    pick always appends — Trigger C's carve-out never reaches it — so omitting
    it from the note understates how often an entry is due.
    """
    for relpath in ORCHESTRATORS:
        assert TRACKER_ABSENT_RENDER_CLAUSE in read(relpath), (
            f"{relpath}: the tracker-absent render note no longer counts a "
            "composed pick among the ungated picks that append an entry"
        )
