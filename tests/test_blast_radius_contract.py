"""The `### Blast radius` producer -> relayers -> consumer chain, and the
design-question rung that fires when the chain's list turns out incomplete.

Regression test for Issue b.q3f. The Issue attacked **serial discovery**: a
design approved at round one still cost many implementation-and-review rounds
because the sites an invariant touches were found one per round, and because a
yes/no policy question the change forced was never asked at the gate. The fix
gives the Analyst two new unconditional sections — `### Blast radius` and
`### Policy decisions this change implies` — relays the first of them down the
whole dispatch ladder so `/quo-engineer-review` can verify a diff against a list
the implementer did not write, and gives the Engineer a way to stop and ask
rather than invent a mechanism the approved design never enumerated.

Every piece of that is prose spread across six files, which is what makes it
worth pinning mechanically. Five failure shapes this module guards:

  * **A relay hop renaming the heading.** The chain only works if `## Blast
    radius` is the same string at every hop — the Analyst emits `### Blast
    radius`, `/quo-fix-issue` relays it under `## Blast radius` to the Engineer,
    the Phase A Code Reviewer, and the Phase C PM, the two role wrappers forward
    it into `/quo-engineer-review`, and that skill keys its sweep verification on
    exactly that label. A hop that renames it does not fail loudly; the review
    just silently stops performing the check.

  * **A section becoming conditional by the back door.** Both new sections are
    unconditional, each with a fixed line for the empty case, so a reader can
    tell "swept and found nothing" from "never swept". Dropping the fixed line
    at any relay site collapses that distinction.

  * **The section list drifting between its enumeration sites.** The proposal's
    section list is written out in three places — the Analyst's frontmatter
    `description`, its contract fence, and `/quo-fix-issue`'s surfacing
    paragraph. The fence is the source of truth; the other two are pinned as
    ordered subsequences of it.

  * **The "mechanism" definition growing a second normative home.** The Engineer
    must not invent a mechanism the design did not enumerate, so both roles need
    the term — but only `agents/analyst.md`'s lifecycle-axis paragraph defines
    it. `agents/engineer.md` carries an explicitly non-normative gloss. Two
    normative lists would drift, and the drift would be invisible.

  * **A scope-split recommendation surfaced with no durable carrier.** The sweep
    can surface a concern distinct from the Issue's stated defect. The
    recommendation about it is stated where the user sees it (`### Blast
    radius`) and mirrored where the orchestrator can act on it (`### Deferred
    refinements`, which becomes a `defer-*` task). Losing the mirror, the
    verdict floor that keeps the mirror block non-empty, or the gate text that
    tells the user their Approve covers the split, loses the recommendation at
    the end of the session — silently, because the user did see it.

Scope note: this module pins shipped artifacts only (`skills/*/SKILL.md`,
`agents/*.md`). `docs/*` carries its own prose about the same feature and is not
pinned here.
"""

import re

import pytest

from conftest import (
    AGENTS_DIR,
    AGENT_ANALYST,
    AGENT_CODE_REVIEWER,
    AGENT_ENGINEER,
    AGENT_PM,
    QUO_ENGINEER_REVIEW,
    QUO_FIX_ISSUE,
    read,
)

# The one heading string the whole relay chain keys on. The producer emits it at
# `###` inside its proposal; every downstream hop relays it at `##`.
PRODUCER_HEADING = "### Blast radius"
RELAY_HEADING = "## Blast radius"

POLICY_HEADING = "### Policy decisions this change implies"

# The same section named in running prose rather than as a heading.
# `agents/engineer.md`'s authoritative-directive bullet enumerates what the
# directive block carries in a sentence, so it spells the section's name without
# the `###` marker. Deriving the bare name from the heading keeps that site
# pinned to the same string every heading site uses, so renaming the section
# fails both rather than only the ones that spell it as a heading.
POLICY_SECTION_NAME = POLICY_HEADING.removeprefix("### ")

# The fixed lines that make each section's empty case distinguishable from an
# omitted section.
BLAST_RADIUS_EMPTY_LINE = "No invariant added, removed, or weakened."
POLICY_EMPTY_LINE = "None — the recommendation leaves no policy question open."

# The condition under which `### Blast radius` may emit its fixed empty line.
# The line's own wording mentions only invariants, so the mechanism half of the
# condition lives here and nowhere else: drop it and an Analyst who introduces a
# mechanism but touches no invariant may legitimately emit "nothing to enumerate"
# — the lifecycle legs check #8 is told to verify the diff against would then be
# absent from a list that claims to be complete, and nothing downstream could
# tell that from a change that genuinely swept clean.
BLAST_RADIUS_EMPTY_CONDITION = (
    "adds, removes, and weakens no invariant **and introduces no mechanism**"
)

DESIGN_QUESTION_HEADING = "## Design question"

# The `## Design question` payload contract, pinned on both halves.
#
# The heading alone is not the contract. `/quo-fix-issue` relays the return's
# *contents* into the revising Analyst's prompt **in place of the user's
# revision feedback**, so a return carrying the heading and nothing else
# re-dispatches the Analyst on a bare question: it would not know which
# mechanism was missing, why the assignment stalled on it, what the Engineer had
# already weighed, or how much of the directive is already on disk.
#
# Both halves enumerate the same four items — the mechanism, why it blocks the
# assignment, the alternatives, and the landed/undone split — but in opposite
# voices, the producer instructing the Engineer ("you would have had to add")
# and the receiver describing what arrives ("it would have had to add"). Only
# the middle clause is byte-shared, so that one is a single constant both halves
# are checked against and a reword of it on either side fails; the voiced halves
# are pinned in their own words, which is what makes them fail independently.
PAYLOAD_WHY_BLOCKED = "why the assignment cannot be completed without it"

DESIGN_QUESTION_PAYLOAD_PRODUCER = (
    "naming the mechanism you would have had to add, "
    f"{PAYLOAD_WHY_BLOCKED}, and the alternatives you see"
)

# The producer's fourth item is its own sentence rather than part of the run
# above, so it is pinned separately — dropping it leaves the first three intact
# and the dispatcher unable to tell the diff is partial.
DESIGN_QUESTION_PARTIAL_SPLIT_PRODUCER = (
    "Say plainly which parts of the assignment you did land and which you left "
    "undone, so the dispatcher knows the diff is partial."
)

DESIGN_QUESTION_PAYLOAD_RECEIVER = (
    "the mechanism it would have had to add, "
    f"{PAYLOAD_WHY_BLOCKED}, the alternatives it named, and which parts of the "
    "assignment landed and which did not"
)

# The design-question rung's producer -> consumer clause pair. `/quo-fix-issue`
# obliges the re-dispatch prompt to say that half the fix is already on disk;
# `agents/analyst.md` is what acts on the statement. The shared clause is the
# part both halves have to spell the same way.
PARTIAL_ON_DISK_CLAUSE = (
    "**partial implementation of the prior directive is already on disk**"
)
MID_CHANGE_CLAUSE = (
    "the working tree as **mid-change** rather than as the pre-fix baseline"
)
ANALYST_MID_IMPLEMENTATION_ANCHOR = "re-dispatched **mid-implementation**"

# The two sites that advertise the mid-change dispatch outside the operative
# paragraph: the frontmatter `description` Claude Code renders, and the
# cold-start invariant that would otherwise read as "always the pre-fix tree".
ANALYST_MID_CHANGE_ADVERTISEMENTS = {
    "frontmatter description": (
        "revise that analysis mid-implementation against a working tree that "
        "already carries a partial fix"
    ),
    "cold-start invariant": (
        "including a working tree that on the mid-implementation path already "
        "carries a partial fix"
    ),
}

# The mid-change dispatch's *other* obligation, stated once by the producer of
# the prompt and once by its receiver. The two halves are worded differently on
# purpose — one instructs the orchestrator what the prompt must say, the other
# instructs the Analyst what to do — so each is pinned in its own words. The
# rung fires precisely because a mechanism went unenumerated, so a revision that
# names the mechanism without walking its legs re-runs the same design question
# a round later, which is the churn the whole rung exists to end.
RUNG_LIFECYCLE_CLAUSE = (
    "MUST state that its revised `### Blast radius` has to cover the lifecycle "
    "of whatever mechanism it now enumerates"
)
ANALYST_LIFECYCLE_CLAUSE = (
    "make sure the revised proposal's `### Blast radius` covers the lifecycle "
    "of the mechanism it now enumerates"
)

# The carry-forward obligation: quoting the prior proposal "in full" includes
# its `### Deferred refinements` block. The clause has two homes — Section 3's
# Revise branch, where the user's own revision feedback drives the re-dispatch,
# and Section 4's design-question rung, which enters that same branch from an
# Engineer return — so this constant is shared and each site is pinned
# separately, against its own paragraph and alongside its own lead-in.
#
# This is the leg of the scope-split's silent-loss shape those two sites own.
# Section 3 strips the
# block before rendering the user-facing prose, so a re-dispatch that quotes
# what the user *saw* quotes a proposal with no deferrals in it; Section 3's
# supersede-and-clear rule then fires on the revision's Approve and clears the
# superseded iteration's `defer-*` tasks. The deferral is gone with no carrier
# anywhere and nothing reports its loss — the revision reads complete, and the
# only trace was a task the workflow itself deleted. What the clause buys is
# that the revising Analyst has the block in hand and must therefore make a
# choice about each prior deferral, carry it or drop it, rather than never
# seeing it.
RUNG_DEFERRAL_CARRY_FORWARD_CLAUSE = (
    "the revising Analyst needs in hand so it either carries each prior "
    "deferral forward or explicitly drops it"
)

# Section 3's Revise branch — the clause's other home. The paragraph is the one
# that builds the re-dispatch prompt, and its lead-in is worded for that site
# ("the prior proposal's" block, where the rung says "its"), so pinning the
# lead-in alongside the shared clause is what makes the two homes fail
# independently: deleting either copy fails exactly one test.
REVISE_DISPATCH_ANCHOR = (
    "The new dispatch prompt embeds the same Issue body verbatim"
)
REVISE_DEFERRAL_CARRY_FORWARD_LEAD_IN = (
    '**"In full" includes the prior proposal\'s `### Deferred refinements` '
    "block**"
)

# --- Sweep shape and auditability --------------------------------------------
#
# The Responsibilities bullet that makes the sweep run *before* the proposal is
# written. Without the ordering, the sweep degrades into a post-hoc justification
# of a recommendation already chosen — which finds the sites the recommendation
# already accounts for and no others.
SWEEP_BEFORE_PROPOSAL = (
    "**Run the blast-radius sweep before writing the proposal.**"
)
SWEEP_RECORD_PATTERNS = "**Record every pattern you ran verbatim**"

# The auditability rule the `**Choosing patterns.**` paragraph argues from: a
# site list is only re-runnable if every entry carries the pattern that found it,
# and a `None found` entry is only meaningful if it names the pattern that came
# back empty.
ENTRY_CARRIES_ITS_PATTERN = (
    "**plus the verbatim search pattern that found it**"
)
NONE_FOUND_NAMES_ITS_PATTERN = (
    "`None found` is an acceptable entry inside a group **only when it names "
    "the pattern that was tried**"
)

# The sweep's first-party / third-party boundary. It is stated twice — in the
# Responsibilities bullet and in the contract fence's `**Scope.**` paragraph —
# because the two are read by different readers at different times.
SWEEP_SCOPE_BOUNDARY = (
    "third-party dependencies the team does not own are out of scope"
)
SCOPE_MARKER = "**Scope.**"
SCOPE_FIRST_PARTY = (
    "When the change reaches **first-party dependencies the same team owns**"
)

# --- Policy grounding --------------------------------------------------------
GROUNDING_RULE_MARKER = "**Grounding rule.**"
GROUNDING_ENUMERATE_CHECKS = (
    "Enumerate, with `file:line`, **every check the system still applies on "
    "the path where that value is used**"
)
GROUNDING_NOT_A_BARE_LABEL = (
    'rather than as an unqualified label such as "secret" or "capability"'
)

# --- Policy-entry shape ------------------------------------------------------
#
# The producer obligation behind Section 3's Approve promise. The consumer half
# ("approval covers the Analyst's recommended answer to every question") is
# pinned at the gate; this is what makes that promise meetable.
POLICY_QUESTION_SHAPE = (
    "One entry per **yes/no policy question the Recommended approach forces "
    "but the Issue body does not settle**"
)
POLICY_ENTRY_SHAPE = (
    "For each entry give the question, the consequence of answering yes, the "
    "consequence of answering no, and **the Analyst's recommended answer**."
)

# The three sections Section 3's Approve branch captures as *directive* rather
# than as context. Every site that enumerates the directive must name all three.
DIRECTIVE_SECTIONS = (
    "### Recommended approach",
    PRODUCER_HEADING,
    POLICY_HEADING,
)

# --- Relay hops --------------------------------------------------------------
#
# One entry per hop in the chain, each keyed by a **unique** anchor string in its
# file. The assertion is that the hop's own paragraph names `## Blast radius`:
# a hop that keeps the prose but renames the heading breaks the chain silently.
#
# Only hops whose anchor does *not* itself contain the heading string belong
# here. The two wrapper role files' relay bullets are anchored on a sentence that
# spells `## Blast radius` inside the anchor, which would make the assertion
# below tautological — those two are covered instead by
# `test_wrapper_relay_sentences_are_byte_identical_in_both_role_files` (which
# pins four sentences of each bullet, by substring, one of which spells the
# heading) and by
# `test_every_review_invoker_role_file_forwards_the_blast_radius_block` (which
# pins the forward on every role file that drives the review, discovered rather
# than enumerated).
RELAY_HOPS = {
    "/quo-fix-issue Engineer dispatch": (
        QUO_FIX_ISSUE,
        "**Engineer dispatch — embed the Section 3 design directive as the "
        "authoritative design source.**",
    ),
    "/quo-fix-issue Phase A Code Reviewer dispatch": (
        QUO_FIX_ISSUE,
        "**Code Reviewer dispatch — relay the Analyst's `### Blast radius` "
        "verbatim.**",
    ),
    "/quo-fix-issue Phase C PM dispatch": (
        QUO_FIX_ISSUE,
        "**The Phase C PM dispatch prompt must also relay the Analyst's "
        "`### Blast radius` verbatim.**",
    ),
    "agents/engineer.md enumerated-site-list bullet": (
        AGENT_ENGINEER,
        "**When the dispatch prompt carries an enumerated site list**",
    ),
    "agents/engineer.md authoritative-directive bullet": (
        AGENT_ENGINEER,
        "**Authoritative design directive (fix mode only).**",
    ),
    "/quo-engineer-review check #8 sweep verification": (
        QUO_ENGINEER_REVIEW,
        "**Sweep verification against an upstream site list.**",
    ),
}

# The two orchestrator-side hops that must relay the section even when it is
# empty — otherwise "nothing to verify" and "never supplied" become
# indistinguishable downstream.
EMPTY_LINE_RELAY_HOPS = (
    "/quo-fix-issue Phase A Code Reviewer dispatch",
    "/quo-fix-issue Phase C PM dispatch",
)

# The two `/quo-engineer-review` wrapper role files. Their relay bullets carry
# these four sentences byte-identically on purpose: both feed the same check in
# the same skill, so a divergence means one caller's list silently stops
# arriving. It is the four sentences that are pinned, not the whole bullet — the
# rest of each bullet legitimately differs, because each names its own dispatch
# path (`agents/code-reviewer.md`'s "the orchestrator's dispatch prompt" /
# "this wrapper adds none" against `agents/pm.md`'s "the dispatch prompt that
# spawned this PM" / "the PM adds none"). Forcing those apart-by-design clauses
# together would be a worse pin, not a stricter one.
WRAPPER_RELAY_SENTENCES = (
    "**Pass the upstream `## Blast radius` list into the review.**",
    "forward it **verbatim** into the `/quo-engineer-review` invocation under "
    "that same heading — one heading string at every hop, so the review's sweep "
    "verification can key on it.",
    'Forward it even when the block carries only an explicit "nothing to verify" '
    "line, so the review can tell that from a list that was never supplied.",
    "When the dispatch prompt carried no `## Blast radius` block, forward no "
    "such heading rather than an empty one.",
)

# --- Section-list enumeration sites ------------------------------------------
#
# Each site writes the proposal's sections out as a `A / B / C` run. The
# contract fence in `agents/analyst.md` is the source of truth; each run is
# checked as an ordered prefix of it.
ENUMERATION_SITES = {
    "agents/analyst.md frontmatter description": (
        AGENT_ANALYST,
        "Produces a Design Proposal grounded in the codebase research — ",
        ".",
    ),
    "/quo-fix-issue Section 3 surfacing paragraph": (
        QUO_FIX_ISSUE,
        "The proposal is **free-form analysis** (",
        ")",
    ),
}

# --- Directive-section enumeration sites -------------------------------------
DIRECTIVE_SITES = {
    "/quo-fix-issue Section 3 Approve branch": (
        QUO_FIX_ISSUE,
        "- **Approve** — Capture the Analyst's Design Proposal as the run's "
        "authoritative design directive",
    ),
    "/quo-fix-issue Read-state proposal-recovery rule": (
        QUO_FIX_ISSUE,
        "One value has no durable carrier by design: Section 3's **Design "
        "Proposal**",
    ),
    "/quo-fix-issue Engineer dispatch paragraph": (
        QUO_FIX_ISSUE,
        "**Engineer dispatch — embed the Section 3 design directive as the "
        "authoritative design source.**",
    ),
}

# `#### Authoritative design directive (carried into Section 4)` spreads its
# enumeration across two bullets, so it is checked as a section block rather than
# as a single paragraph.
DIRECTIVE_SECTION_HEADING = (
    "#### Authoritative design directive (carried into Section 4)"
)

# --- Proposal recovery after a compaction ------------------------------------
#
# `DIRECTIVE_SITES` pins the Read-state proposal-recovery rule for its three
# *section names* only, which leaves the rule's operative content free to be
# rewritten around them. These three clauses are that content, and each fails
# silently if it goes. The first is the trigger list — the dispatches at which
# the rule actually fires. It is what makes the rule reach every point that
# relays the proposal rather than only the one the orchestrator happens to be
# standing at; lose it and the decision and the guarantee below both survive
# with nothing left to say *when* they apply, so an orchestrator re-derives for
# the next Engineer round and hands the Code Reviewer a summary. The second
# forbids the two cheap recoveries a compacted orchestrator will otherwise reach
# for — reconstructing the proposal from a summary, or giving it a manifest
# field — and names the only sanctioned one; lose it and the run continues
# against an invented design directive that reads exactly like an approved one.
# The third is the guarantee the relay chain's consumer rests on: because the
# proposal is always re-derived *before* the dispatch that needs it, a
# downstream `## Blast radius` heading is never legitimately absent, so
# `/quo-engineer-review` may treat a missing one as a fault rather than as a
# compaction it must tolerate — which holds only for as long as the trigger list
# keeps naming those dispatches.
PROPOSAL_RECOVERY_ANCHOR = DIRECTIVE_SITES[
    "/quo-fix-issue Read-state proposal-recovery rule"
][1]

PROPOSAL_RECOVERY_CLAUSES = {
    "the list of dispatches that trigger the recovery": (
        "an Engineer dispatch (any round, including a Phase C re-entry round), "
        "a Phase A Code Reviewer relay, a Phase C PM relay, or a re-run of any "
        "of these"
    ),
    "the re-derive-through-the-Analyst rule": (
        "do **not** reconstruct it from a summary, and do **not** give it a "
        "manifest field. **Re-derive it through the Analyst."
    ),
    "the no-omitted-relay-heading guarantee": (
        f"there is no path in fix mode that omits a downstream "
        f"`{RELAY_HEADING}` relay heading"
    ),
}

# --- The re-derivation shape, and its one reuse site -------------------------
#
# `PROPOSAL_RECOVERY_CLAUSES` pins the rule that says *re-derive through the
# Analyst*; the constants below pin what "re-derive" is actually made of. The
# shape is stated once, as three bullets hanging off the recovery paragraph, and
# consumed by reference at exactly one other site — the design-question rung's
# compaction branch. Both ends fail silently. Lose a bullet and the re-dispatch
# still happens, just underspecified: without the first the fresh Analyst has no
# Issue body to work from, without the second it cannot see what already landed,
# without the third it reads the half-landed diff as the pre-fix baseline. Lose
# the rung's reuse sentence and that rung has no instruction at all for the
# compaction case — the branch that most needs one — or grows a second copy of
# the shape that drifts from this one.
#
# The anchor is the "defined once here" clause rather than the phrase
# `**re-derivation shape**`, which appears three times in the recovery paragraph
# alone and so is not a unique site marker.
RE_DERIVATION_SHAPE_ANCHOR = (
    "defined once here and referenced from the design-question rung below:"
)

# Two of these bullets are the compaction-path twins of clauses the
# design-question rung states for the readable-proposal path — the changed-file
# statement against `PARTIAL_ON_DISK_CLAUSE`, and the blast-radius obligation
# against `RUNG_LIFECYCLE_CLAUSE`. Neither is derived from its twin, because the
# shipped wording is genuinely different rather than incidentally so: the rung
# names a *partial implementation of the prior directive* where this bullet
# names *the changed-file list above*, and the rung scopes the revised sweep to
# the **lifecycle of the mechanism it now enumerates** where this bullet scopes
# it to **the tree as it stands** — a compaction strands the whole proposal, not
# one unenumerated mechanism. Deriving either would assert a byte-sharing the
# files do not have.
RE_DERIVATION_BULLET_CLAUSES = {
    "the Issue body and the same reference_materials": (
        "the **Issue body re-read from bees**, and the same "
        "`reference_materials` the first dispatch carried"
    ),
    "the changed-file list of what is on disk": (
        "the **changed-file list of what is on disk for this Issue**"
    ),
    "the empty changed-file list is itself informative": (
        "an **empty** list is itself informative, saying no implementation has "
        "landed for this Issue yet"
    ),
    "the proposal-was-lost-to-a-compaction statement": (
        "a plain statement that **the prior proposal was lost to a compaction** "
        "and that the changed-file list above is what has already been "
        "implemented against it"
    ),
    "re-derive from the codebase rather than from a summary": (
        "the Analyst **re-derives** the design from the codebase rather than "
        "revising a summary of one"
    ),
    "the revised sweep covers the tree as it stands": (
        f"its `{PRODUCER_HEADING}` must cover the tree as it stands"
    ),
}

RUNG_REUSE_ANCHOR = "**When the approved Design Proposal is no longer readable**"

RUNG_REUSE_CLAUSES = {
    "the reuse-by-reference of the single definition": (
        "use the **re-derivation shape** the Read-state step above defines"
    ),
    "the single-definition claim": (
        "it is the single definition of what to send in place of a proposal a "
        "compaction stranded"
    ),
    "the one delta this rung adds to the shape": (
        f"This rung adds one thing to it: the Engineer's "
        f"`{DESIGN_QUESTION_HEADING}` travels in the "
        "`## Prior proposal and user feedback` section as the feedback."
    ),
}

# --- Section 8's post-completion design-question rung -------------------------
#
# The same stop-rather-than-invent return, arriving where there is no Analyst to
# revise the design against. Section 4 routes it back through the proposal;
# Section 8 terminates it in a filed Issue, which makes the filing itself the
# whole payload. The routing is pinned three ways already; these two clauses are
# what that routing has to carry to be worth anything, and each fails silently.
# Lose the first and the follow-up Issue records that a question was asked
# without recording the question or how much of that finding's fix landed, so
# whoever picks the Issue up restarts from the finding alone. Lose the second and
# the session's last word says nothing about the partial diff on disk, so the
# next reader takes an open Issue for untouched work and re-implements over it.
#
# Neither clause is derived from `DESIGN_QUESTION_PAYLOAD_RECEIVER` above. That
# one is Section 4's receiver describing what arrives from the Engineer; this is
# Section 8's receiver describing what it writes into a ticket, and the shipped
# wordings genuinely differ rather than incidentally so. Deriving either would
# assert a byte-sharing the files do not have.
POSTCOMP_DESIGN_QUESTION_ANCHOR = (
    f"**An `engineer-postcomp-<n>` return carrying a "
    f"`{DESIGN_QUESTION_HEADING}` is not a completion of that finding**"
)

POSTCOMP_FOLLOW_UP_ISSUE_PAYLOAD = (
    "the follow-up Issue carries the finding, the Engineer's question verbatim, "
    "and its what-landed / what-did-not list"
)

POSTCOMP_REPORT_EDITS_ON_DISK = (
    "note in the final report which of that finding's edits are already on disk"
)

# --- Analyst task lifecycle --------------------------------------------------
#
# Section 3 marks the Analyst's task `completed` the moment its return is read,
# so every later close-out site must describe it as already closed rather than
# re-closing it. A site that reverts to "mark it completed here" reopens the
# window in which the Engineer-dispatch precondition below sees a stale active
# task and refuses the forward dispatch.
MARK_ON_READ_SENTENCE = (
    "**Mark that Analyst's `analyst-<issue-id>` (or `-rev<n>`) TaskList task "
    "`completed` the moment its return is read, before surfacing the proposal "
    "and before creating the gate task below**"
)

ALREADY_COMPLETED_SITES = {
    "Section 3 Approve branch": "- **Approve** — Capture the Analyst's Design Proposal",
    "Section 3 Revise branch": "- The prior Analyst's TaskList task — `analyst-<issue-id>` on the first revision",
    "Section 3 Cancel branch": "- **Cancel** — **NO commit is made; the Issue stays `open`.**",
    "Section 7 step 3 close-out": "- the Section 3 Analyst task `analyst-<issue-id>` (plus any `analyst-<issue-id>-rev<n>` revisions)",
    "Aborted-Issue close-out step 1": "1. **Close out this Issue's TaskList tasks**",
}

ALREADY_COMPLETED = re.compile(r"already (?:marked )?`completed`", re.I)

# The Engineer-dispatch precondition's prefix list, copied at three sites in
# `/quo-fix-issue`. Every copy must carry the Analyst prefix: an Analyst
# mid-revision is authoring the very directive the next Engineer round would
# implement, so a copy that omits it licenses a dispatch against a stale one.
PREFIX_LIST_MARKER = "name begins with"
PREFIX_LIST_SENTINEL = "`test-writer-<issue-id>`"
ANALYST_PREFIX = "`analyst-<issue-id>`"
EXPECTED_PREFIX_LIST_COPIES = 3

# --- check #8 kind groups ----------------------------------------------------
#
# Both files name the same three out-of-lane kind groups, and both resolve the
# lane by their own scope rather than by the upstream list's group name.
KIND_GROUPS = "**tests**, **customer docs**, and **internal docs** kind-groups"
LANE_BY_OWN_SCOPE = ", not by the upstream group name**"
REVIEW_SCOPE_HEADING = '### Scope: what counts as "code" for this review'

# --- check #8 shortfall routing ----------------------------------------------
#
# The two upstream-list shortfalls route to different surfaces, and each bullet
# says so at the check site itself. `### Second-order effects` names both kinds
# too (pinned separately), but a reader working through check #8 top-to-bottom
# decides the routing there and may never reach the emission contract — so the
# routing sentence has to survive at the check, not only downstream of it.
#
# Each bullet is pinned on both halves of its routing. The negative half ("not a
# numbered work item") only tells a reviewer where the entry does *not* go; a
# bullet that keeps it and loses the positive destination reads as licence to
# drop the entry entirely, which is exactly the silent loss `### Second-order
# effects` exists to prevent. So the destination clause is pinned alongside.
UPSTREAM_SHORTFALL_ROUTING = {
    "in-lane upstream entry left without a disposition": (
        "**A site on the upstream list that the diff neither changes nor "
        "dispositions**",
        (
            "is a normal finding **against the Engineer**: emit it as a "
            "numbered, severity- and depth-tagged work item",
            "so record it under `### Second-order effects` as owed to the "
            "other lane",
            "Only an upstream entry **in this review's own lane**, left with "
            "no change and no disposition at all, is the finding.",
        ),
    ),
    "diff-touched site on neither list": (
        "**A site the diff touches that appears on neither list**",
        (
            "not an Engineer defect",
            "Record it as a list gap in the `### Second-order effects` "
            "narrative subsection",
            "do **not** emit it as a numbered work item",
        ),
    ),
}

# --- Mechanism definition ----------------------------------------------------
CANONICAL_HOME_SENTENCE = (
    "**This paragraph is the single canonical home for that definition**"
)
ENGINEER_DEFERS_TO_CANONICAL = (
    "that paragraph is the definition's single canonical home"
)

# The obligation the canonical paragraph attaches to the term it defines. The
# definition alone only says what counts as a mechanism; these three clauses are
# what turn "you enumerated a mechanism" into work a reviewer can check. Losing
# the legs leaves a mechanism named with no sites, losing the every-scope clause
# lets one scope's legs stand in for all of them, and losing the design-gap
# sentence leaves a missing leg as something to notice rather than report — the
# one-leg-per-round discovery this whole limb exists to end.
LIFECYCLE_LEGS = (
    "name each leg of its **lifecycle**: where it is created or initialized, "
    "where it is read or consumed, where it is mutated / invalidated / "
    "migrated, where it is torn down or removed, where it is observable (logs, "
    "spans, metrics, error text), and where it is documented"
)
LIFECYCLE_EVERY_SCOPE = (
    "**in every scope the change touches and on every exit path** (normal "
    "completion, cancel, abort, interruption)"
)
LIFECYCLE_DESIGN_GAP = (
    "A leg missing in any scope is a **design gap**: report it here, at the "
    "gate, rather than leaving reviewers to discover one leg per round."
)

# The consumer end of the same obligation: what check #8 says the upstream list
# contains. A relay that describes the list as invariant sites only tells the
# reviewer to verify half of what the producer was told to emit.
UPSTREAM_LIST_LIFECYCLE_LEGS = (
    "the lifecycle legs of each mechanism the change introduces"
)

# --- Out-of-lane disposition handshake ---------------------------------------
#
# The two halves of one handshake. The Engineer lists an out-of-lane entry in
# its completeness evidence *with* the disposition; check #8 accepts exactly
# that as the accounting it asks for. Each half is useless alone: the Engineer
# emitting a disposition no reviewer credits produces a finding against work
# that was in fact accounted for, and the reviewer crediting a disposition the
# Engineer was never told to emit credits something that never arrives.
DISPOSITION_IS_NOT_DROPPING = (
    "Dispositioning is not dropping — list those entries in your completeness "
    "evidence with that disposition"
)
DISPOSITION_IS_THE_ACCOUNTING = (
    "that disposition *is* the accounting this bullet asks for"
)

# The explicitly-empty upstream list's closing clause: having said what the
# empty list does *not* license, the rule says what it does. Without it the
# paragraph is three prohibitions and no instruction, and the reviewer that
# reads an empty list has nothing left to check — including the one case the
# empty list is a claim about, a diff that in fact does touch an invariant or
# introduce a mechanism, which is exactly when the upstream analysis was wrong.
EMPTY_LIST_LICENSED_CHECK = (
    "the only check it licenses is whether the diff in fact does add, remove, "
    "or weaken an invariant or introduce a mechanism"
)

# The third shortfall shape: a list arrived, evidence did not. It has its own
# sentence because the empty-list rule above does not reach it — there the list
# is empty, here the list is full and the reconciliation is missing.
UPSTREAM_LIST_ALONE = (
    "When the upstream list is supplied but no Engineer completeness evidence "
    "arrived, verify the diff against the upstream list alone, and handle the "
    "absent evidence under the missing-list rule above."
)

# --- Scope-split and gate ratification ---------------------------------------
#
# A sweep can surface a concern distinct from the Issue's stated defect, and the
# Analyst recommends what to do with it. That recommendation has two homes on
# purpose: `### Blast radius` is what the user sees at the gate, and the mirrored
# `### Deferred refinements` bullet is what the orchestrator turns into a
# `defer-*` task. The limb below keeps the two in step — the mirror itself, the
# destination annotation that makes the mirror actionable, the verdict floor that
# keeps the mirror block structurally non-empty, the `escalate-to-user` carve-out
# where there is no carrier to mirror into, and the gate text that tells the user
# their Approve covers the split.
SCOPE_SPLIT_MARKER = "**Scope-split recommendation.**"
DEFERRED_REFINEMENTS_HEADING = "### Deferred refinements"

# The two destinations a scope-split mirror may carry, one per branch of the
# recommendation. Both must also be destinations the `### Deferred refinements`
# contract actually permits, or the mirror names a value its consumer rejects.
SCOPE_SPLIT_DESTINATIONS = ("addressed-now-in-this-Issue", "defer-to-new-Issue")

REFINEMENTS_VERDICT = "recommend-with-refinements"
REFINEMENTS_VERDICT_ANCHOR = f"- **`{REFINEMENTS_VERDICT}`**"

# The premise three scope-split rules argue from — the `escalate-to-user`
# carve-out, the converged-verdict floor, and the trivial-fix deferral. Each
# states it in its own words inside the scope-split paragraph; the deferrals
# contract below is what actually holds it. A contract that began permitting
# bullets on those two verdicts would leave all three rules reading correctly
# while defending a premise their own file no longer holds — and the floor in
# particular would then be flooring nothing.
DEFERRALS_STRUCTURALLY_EMPTY = (
    "- On verdicts `recommend-as-stated` and `escalate-to-user` — this section "
    "is structurally empty"
)
DEFERRALS_EMIT_NONE = (
    "Emit the heading followed by `None` so the orchestrator can parse the "
    "section deterministically."
)

# The design-question rung reuses Section 3's gate rather than minting one, so
# any `gate-*` token — or any mention of the gate tool itself — inside the rung
# must sit in a sentence that attributes it to Section 3. A bare "no `gate-`
# anywhere" (or "no `AskUserQuestion` anywhere") guard would also reject that
# legitimate cross-reference, which is the point: the rung is *supposed* to be
# able to say it reuses Section 3's gate, and a guard that forbids naming the
# thing being reused fails on prose that is exactly right.
GATE_TASK_PREFIX = "gate-"
GATE_TOOL = "AskUserQuestion"
SECTION_3_ATTRIBUTION = "Section 3"

# The premise both gate-ratification sites argue from: the two sections actually
# reach the user. Section 3's surfacing paragraph is where that is decided — it
# is also the paragraph that withholds `### Deferred refinements`, so the rule is
# a contrast, not a blanket "surface everything". The anchor is derived from the
# enumeration site rather than re-spelled, so a reworded anchor fails in one
# place instead of drifting between two.
SURFACING_PARAGRAPH_ANCHOR = ENUMERATION_SITES[
    "/quo-fix-issue Section 3 surfacing paragraph"
][1]

# The two `/quo-fix-issue` gate sites that tell the user what Approve ratifies.
GATE_PREAMBLE_ANCHOR = (
    "**The preamble also carries the policy decisions and any scope-split "
    "recommendation.**"
)
APPROVE_OPTION_ANCHOR = "- **Approve & proceed to implementation (Recommended)**"

FENCE_LINE = "```"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def paragraph_with(relpath, anchor):
    """The single line in `relpath` containing `anchor`.

    These skills write one markdown paragraph per line, so the containing line
    is the paragraph. Uniqueness is asserted rather than assumed: an anchor that
    starts matching twice would silently begin testing the wrong site.
    """
    lines = read(relpath).splitlines()
    hits = [line for line in lines if anchor in line]
    assert len(hits) == 1, (
        f"{relpath}: expected exactly one paragraph containing {anchor!r}, "
        f"found {len(hits)} — the anchor is no longer a unique site marker"
    )
    return hits[0]


def bullets_after(relpath, anchor):
    """The contiguous markdown bullet block that follows `anchor`'s line.

    Some rules state their operative content as a bullet list hanging off a
    paragraph rather than inside it, so `paragraph_with` — which returns the one
    containing line — cannot reach them. Leading blank lines are skipped; the
    block ends at the first line after it that is not a bullet. Scoping to the
    block rather than searching the whole file is what keeps the assertions
    pinned to *this* rule's bullets: an identical clause added under some other
    paragraph would otherwise satisfy them.
    """
    lines = read(relpath).splitlines()
    hits = [i for i, line in enumerate(lines) if anchor in line]
    assert len(hits) == 1, (
        f"{relpath}: expected exactly one paragraph containing {anchor!r}, "
        f"found {len(hits)} — the anchor is no longer a unique site marker"
    )
    bullets = []
    for line in lines[hits[0] + 1:]:
        if line.lstrip().startswith("- "):
            bullets.append(line)
        elif bullets or line.strip():
            break
    assert bullets, (
        f"{relpath}: the paragraph containing {anchor!r} is no longer followed "
        "by a bullet list"
    )
    return "\n".join(bullets)


def section_block(relpath, heading):
    """The lines from `heading` up to (not including) the next markdown heading."""
    lines = read(relpath).splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == heading]
    assert len(starts) == 1, (
        f"{relpath}: expected exactly one {heading!r} heading, found {len(starts)}"
    )
    start = starts[0]
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#"):
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


def contract_fence():
    """The body of the fenced Design Proposal template in `agents/analyst.md`."""
    lines = read(AGENT_ANALYST).splitlines()
    fences = [i for i, line in enumerate(lines) if line.rstrip() == FENCE_LINE]
    assert len(fences) == 2, (
        "agents/analyst.md: expected exactly one fenced Design Proposal "
        f"template, found {len(fences)} fence delimiters"
    )
    return "\n".join(lines[fences[0] + 1:fences[1]])


def contract_sections():
    """The `###` section headings of the Design Proposal template, in order."""
    sections = re.findall(r"^### (.+)$", contract_fence(), re.M)
    assert sections, "agents/analyst.md: the contract fence has no `###` sections"
    return sections


def enumeration_tokens(relpath, anchor, terminator):
    """The `A / B / C` run following `anchor`, split into stripped tokens."""
    text = read(relpath)
    assert text.count(anchor) == 1, (
        f"{relpath}: expected exactly one enumeration anchored at {anchor!r}, "
        f"found {text.count(anchor)}"
    )
    start = text.index(anchor) + len(anchor)
    end = text.index(terminator, start)
    return [token.strip() for token in text[start:end].split("/")]


def scope_split_paragraph():
    """The producer's `**Scope-split recommendation.**` paragraph.

    Asserted to sit inside `### Blast radius` before it is returned: the
    paragraph's own premise is that the recommendation belongs in the section the
    orchestrator surfaces at the gate, so a copy that drifted into a sibling
    section would still read correctly and be surfaced nowhere.
    """
    assert SCOPE_SPLIT_MARKER in section_block(AGENT_ANALYST, PRODUCER_HEADING), (
        f"agents/analyst.md: the {SCOPE_SPLIT_MARKER} rule is no longer inside "
        f"`{PRODUCER_HEADING}`, so the recommendation it governs no longer sits "
        "in the section the orchestrator surfaces at the approval gate"
    )
    return paragraph_with(AGENT_ANALYST, SCOPE_SPLIT_MARKER)


# Segment split for `sentences()` below, deliberately the same shape
# `tests/test_writer_role_contracts.py`'s `SENTENCE_SPLIT` settled on after that
# suite shipped this exact false negative. Both extra alternatives are
# load-bearing in markdown prose: `:` ends a segment because a lead-in line that
# introduces a bullet list ends in a colon rather than a period, and `\n` ends
# one because a bullet is its own line and frequently carries no terminal
# punctuation at all. Splitting on `.!?` alone glued the rung's
# colon-terminated lead-in ("Then route the question as a **Section 3 Revise, by
# reference**:") to the whole bullet beneath it, so a bullet that minted a
# `gate-*` task name of its own inherited that lead-in's `Section 3` attribution
# and the guard below read green while the rung grew exactly the machinery its
# closing sentence promises it does not add.
#
# The attribution window is the segment, and the line is the widest segment, so
# a minting token added *inside* a long line that already says `Section 3`
# somewhere else is still swallowed. That residue is deliberate: splitting
# further (on `—`, on `;`) would strand the rung's legitimate "reuses Section
# 3's gate" phrasings in segments of their own and fail on prose that is exactly
# right — the false positive this guard must not have, per the
# `GATE_TASK_PREFIX` comment above.
SENTENCE_SPLIT = re.compile(r"(?<=[.:!?])\s+|\n")


def sentences(text):
    """`text` split into segments at sentence, colon, and line boundaries.

    Used where a token is legitimate in one segment and a defect in another, so
    a whole-block substring check cannot tell the two apart. The boundaries are
    drawn narrowly on purpose (see `SENTENCE_SPLIT`): the wider a segment, the
    more attribution a defect inside it can borrow from a neighbouring clause
    that has nothing to do with it.
    """
    return [part for part in SENTENCE_SPLIT.split(text) if part.strip()]


def minting_segments(text, token):
    """Segments of `text` naming `token` without attributing it to Section 3.

    The design-question rung's whole guard, factored out so the detector
    self-tests below exercise the real splitter and the real attribution window
    rather than a paraphrase of them. A self-test that re-implemented this
    comprehension could stay green across a change to `SENTENCE_SPLIT` — which
    is exactly the failure it exists to catch.
    """
    return [
        segment
        for segment in sentences(text)
        if token in segment and SECTION_3_ATTRIBUTION not in segment
    ]


def assert_deferrals_block_is_structurally_none_on_both_verdicts():
    """The deferrals contract itself says the block is empty on two verdicts.

    Three scope-split rules rest on this and none of them can establish it:
    each restates the premise in its own words, inside a paragraph the contract
    does not read. Asserting it here is what keeps those three from being
    self-referential — they cite a rule, and this checks the rule is there.
    """
    fence = contract_fence()
    assert DEFERRALS_STRUCTURALLY_EMPTY in fence, (
        f"agents/analyst.md: the `{DEFERRED_REFINEMENTS_HEADING}` contract no "
        "longer declares itself structurally empty on `recommend-as-stated` "
        "and `escalate-to-user` — the scope-split carve-out, the "
        f"`{REFINEMENTS_VERDICT}` floor, and the trivial-fix deferral all argue "
        "from that premise and now have nothing holding it"
    )
    assert DEFERRALS_EMIT_NONE in fence, (
        f"agents/analyst.md: the `{DEFERRED_REFINEMENTS_HEADING}` contract no "
        "longer requires emitting the heading followed by `None` on those "
        "verdicts, so 'structurally empty' becomes an omitted section the "
        "orchestrator cannot parse deterministically"
    )


def agent_files():
    return sorted(AGENTS_DIR.glob("*.md"))


def shipped_files():
    """Every shipped artifact: the role files plus every skill's SKILL.md."""
    root = AGENTS_DIR.parent
    return sorted(root.glob("agents/*.md")) + sorted(
        root.glob("skills/*/SKILL.md")
    )


# --------------------------------------------------------------------------
# Producer — `agents/analyst.md`
# --------------------------------------------------------------------------


def test_the_two_new_sections_sit_between_recommended_approach_and_why():
    """Placement is contractual, not cosmetic.

    `### Blast radius` enumerates the sites the Recommended approach touches and
    `### Policy decisions this change implies` carries the answers the user
    ratifies with it, so both belong immediately after the recommendation and
    before the `### Why` rationale. Downstream prose describes them in exactly
    that position; moving either one leaves those descriptions wrong.
    """
    sections = contract_sections()
    for heading in ("Blast radius", "Policy decisions this change implies"):
        assert heading in sections, (
            f"agents/analyst.md: the contract fence no longer carries a "
            f"`### {heading}` section — found {sections}"
        )
    assert (
        sections.index("Recommended approach") + 1
        == sections.index("Blast radius")
    ), (
        "agents/analyst.md: `### Blast radius` must directly follow "
        f"`### Recommended approach` — section order is {sections}"
    )
    assert (
        sections.index("Blast radius") + 1
        == sections.index("Policy decisions this change implies")
    ), (
        "agents/analyst.md: `### Policy decisions this change implies` must "
        f"directly follow `### Blast radius` — section order is {sections}"
    )
    assert (
        sections.index("Policy decisions this change implies") + 1
        == sections.index("Why")
    ), (
        "agents/analyst.md: `### Why` must directly follow "
        f"`### Policy decisions this change implies` — section order is {sections}"
    )


def test_both_new_sections_are_unconditional_with_a_fixed_empty_line():
    """Each section is always emitted, with a fixed line for the empty case.

    A section emitted only when the Analyst had something to say degrades into
    one nobody can rely on being asked for — and, at the gate, "swept and found
    nothing" becomes indistinguishable from "never swept". The fixed line is
    what keeps those two apart, so it is pinned byte-for-byte.

    The blast-radius line's emit *condition* is pinned with it. The line names
    only invariants, so the mechanism half of the condition is carried by the
    condition sentence alone; lose it and the empty line becomes emittable by a
    recommendation that introduces a mechanism, which is precisely the case the
    section's lifecycle-legs obligation exists to enumerate.
    """
    fence = contract_fence()
    assert fence.count("**Unconditional — always emit this heading.**") == 2, (
        "agents/analyst.md: both `### Blast radius` and `### Policy decisions "
        "this change implies` must declare themselves unconditional"
    )
    assert f"`{BLAST_RADIUS_EMPTY_LINE}`" in fence, (
        "agents/analyst.md: `### Blast radius` no longer names its fixed "
        f"empty-case line {BLAST_RADIUS_EMPTY_LINE!r}"
    )
    assert BLAST_RADIUS_EMPTY_CONDITION in fence, (
        "agents/analyst.md: `### Blast radius` no longer states the condition "
        f"under which its fixed empty line may be emitted "
        f"({BLAST_RADIUS_EMPTY_CONDITION!r}) — an Analyst that introduces a "
        "mechanism but touches no invariant can now emit it"
    )
    assert f"`{POLICY_EMPTY_LINE}`" in fence, (
        "agents/analyst.md: `### Policy decisions this change implies` no longer "
        f"names its fixed empty-case line {POLICY_EMPTY_LINE!r}"
    )


def test_the_sweep_is_ordered_before_the_proposal_and_records_its_patterns():
    """The instruction that makes the sweep an input, not a justification.

    Ordering is the whole mechanism here. A sweep run *after* the Recommended
    approach is written can only confirm the sites that approach already
    accounts for — the recommendation is fixed by then, so a site that would
    have changed it arrives too late to. Run first, it is what the
    recommendation is built on. The two halves are pinned together because the
    ordering is stated in the same bullet as the record-your-patterns rule that
    makes the result auditable, and a bullet rewritten to drop one usually drops
    both.

    Every clause is asserted against that one bullet rather than against the
    whole file, because the file has a second home for this material — the
    contract fence's `**Scope.**` paragraph — and a whole-file check cannot tell
    a clause that stayed in the Responsibilities bullet from one that migrated
    into the fence. The migration matters: the Responsibilities bullet is what
    the Analyst reads *before* sweeping, the fence is what it fills in *after*,
    so an ordering instruction that drifts into the fence is read too late to
    order anything. The scope boundary is deliberately stated in both homes
    (see the `SWEEP_SCOPE_BOUNDARY` comment above), and this is the assertion
    that keeps the Responsibilities copy from being dropped as redundant with
    the fence copy the first-party/third-party test below pins.
    """
    assert SWEEP_BEFORE_PROPOSAL in read(AGENT_ANALYST), (
        "agents/analyst.md: the Responsibilities bullet no longer orders the "
        "blast-radius sweep **before** the proposal is written, so the sweep "
        "degrades into a post-hoc justification of a recommendation already "
        "chosen"
    )
    bullet = paragraph_with(AGENT_ANALYST, SWEEP_BEFORE_PROPOSAL)
    assert SWEEP_RECORD_PATTERNS in bullet, (
        "agents/analyst.md: the sweep bullet no longer requires recording every "
        "pattern verbatim, so the reader cannot re-run the sweep"
    )
    assert (
        "a site list without its patterns cannot be audited for whether the "
        "patterns were wide enough" in bullet
    ), (
        "agents/analyst.md: the sweep bullet lost the reason the patterns are "
        "recorded, leaving the requirement readable as bookkeeping"
    )
    assert SWEEP_SCOPE_BOUNDARY in bullet, (
        "agents/analyst.md: the Responsibilities bullet no longer carries the "
        "sweep's first-party / third-party boundary, leaving the reach of the "
        "sweep stated only in the contract fence the Analyst fills in after "
        "sweeping — too late to bound the sweep it was meant to bound"
    )


def test_the_sweep_reaches_first_party_dependencies_and_stops_at_third_party():
    """The sweep's scope boundary, drawn at ownership rather than at the package.

    A change's invariant does not stop at the primary package: the sites that
    assume it most often sit in a sibling package or a vendored internal
    library, which is exactly where a package-scoped sweep reports a clean
    result. The far edge matters as much — without it the sweep has no stated
    end and reads as an obligation to search dependencies the team cannot
    change.
    """
    fence = contract_fence()
    assert SCOPE_MARKER in fence, (
        f"agents/analyst.md: `{PRODUCER_HEADING}`'s {SCOPE_MARKER} paragraph is "
        "gone — the sweep no longer states how far it reaches"
    )
    assert (
        "The sweep covers the whole change set, not only the primary package."
        in fence
    ), (
        "agents/analyst.md: the sweep is no longer scoped to the whole change "
        "set, so a package-scoped sweep can report clean while a sibling "
        "package still assumes the old invariant"
    )
    assert SCOPE_FIRST_PARTY in fence, (
        "agents/analyst.md: the sweep no longer names first-party dependencies "
        "the same team owns as in scope"
    )
    assert SWEEP_SCOPE_BOUNDARY in fence, (
        "agents/analyst.md: the sweep no longer stops at third-party "
        "dependencies, leaving its scope unbounded at the far edge"
    )


def test_blast_radius_entries_carry_the_pattern_that_found_them():
    """A site list is auditable only if each entry names its own pattern.

    The list itself cannot show whether the sweep was wide enough — a narrow
    pattern produces a short list that looks complete. The patterns are what
    make the sweep re-runnable, and the `None found` rule is the sharp case: an
    empty group with no pattern is indistinguishable from a group never swept,
    which is the same "swept and found nothing" vs "never swept" collapse the
    fixed empty line prevents one level up. `**Choosing patterns.**` cites this
    rule by name to justify recording a pattern that returned nothing, so
    without it that paragraph argues from a rule its own file no longer states.
    """
    fence = contract_fence()
    assert ENTRY_CARRIES_ITS_PATTERN in fence, (
        f"agents/analyst.md: `{PRODUCER_HEADING}` entries no longer carry the "
        "verbatim search pattern that found them, so the enumerated list can no "
        "longer be audited for whether the patterns were wide enough"
    )
    assert (
        "so the reader can re-run the sweep and judge whether the pattern was "
        "wide enough" in fence
    ), (
        "agents/analyst.md: the per-entry pattern requirement lost the reason "
        "it exists, leaving it readable as redundant with the `file:line`"
    )
    assert NONE_FOUND_NAMES_ITS_PATTERN in fence, (
        f"agents/analyst.md: `{PRODUCER_HEADING}` no longer requires a `None "
        "found` entry to name the pattern that was tried, so an empty group is "
        "again indistinguishable from a group that was never swept — and the "
        "`**Choosing patterns.**` paragraph's cross-reference to this rule now "
        "cites a rule this file does not state"
    )


def test_policy_grounding_rule_phrases_the_answer_in_terms_of_remaining_checks():
    """A policy answer is grounded in what still guards the path, not in a label.

    The failure this rule prevents is a decision derived from the single
    mechanism the change removes — reasoning that treats removing one check as
    removing all of them, and lands on an unqualified "secret" or "capability"
    that overstates what possessing the value grants. Enumerating the checks
    that remain is what makes the answer checkable: a reviewer can verify a
    claim about named `file:line` checks and cannot verify a label.
    """
    fence = contract_fence()
    assert GROUNDING_RULE_MARKER in fence, (
        f"agents/analyst.md: `{POLICY_HEADING}`'s {GROUNDING_RULE_MARKER} "
        "paragraph is gone — policy answers are no longer grounded in the "
        "codebase at all"
    )
    assert (
        "do not derive the answer from the one mechanism the change removes"
        in fence
    ), (
        "agents/analyst.md: the grounding rule no longer forbids deriving the "
        "answer from the single mechanism the change removes, which is the "
        "reasoning that produces an overstated policy answer"
    )
    assert GROUNDING_ENUMERATE_CHECKS in fence, (
        "agents/analyst.md: the grounding rule no longer requires enumerating "
        "every check still applied on the value's path, so the answer rests on "
        "nothing a reviewer can check"
    )
    assert GROUNDING_NOT_A_BARE_LABEL in fence, (
        "agents/analyst.md: the grounding rule no longer requires phrasing the "
        "conclusion in terms of the enumerated checks rather than as an "
        "unqualified label, so the section can again ratify a policy answer "
        "that overstates what the value grants"
    )


def test_policy_entries_carry_a_yes_no_question_both_consequences_and_an_answer():
    """The producer obligation behind the gate's one-decision promise.

    Section 3's Approve tells the user their approval covers "the Analyst's
    recommended answer to every question" in the section — a promise only
    meetable if every entry in fact carries one. That consumer half is pinned at
    the gate; this is the producer half, and it is the one that can quietly stop
    being true. An entry stating a question with no recommended answer turns the
    single ratification back into an open decision the user must research
    themselves, and one missing a consequence leaves them ratifying an answer
    whose cost was never stated.
    """
    fence = contract_fence()
    assert POLICY_QUESTION_SHAPE in fence, (
        f"agents/analyst.md: `{POLICY_HEADING}` no longer scopes its entries to "
        "yes/no questions the Recommended approach forces and the Issue body "
        "leaves unsettled — without that scope the section collects open musings "
        "the gate cannot ratify in one decision"
    )
    assert POLICY_ENTRY_SHAPE in fence, (
        f"agents/analyst.md: `{POLICY_HEADING}` no longer requires each entry to "
        "carry the question, both consequences, and **the Analyst's recommended "
        "answer** — Section 3's Approve option promises approval covers that "
        "recommended answer for every question, and this is the obligation that "
        "makes the promise meetable"
    )


def test_trivial_fix_short_circuit_still_emits_both_sections():
    """The cheapest case is the one most tempting to skip.

    `## Short-circuit conditions` lets a trivial mechanical fix converge cheaply.
    Cheap convergence is not the same as skipping the sweep, and the distinction
    the fixed empty lines protect is exactly what a skipped section destroys.
    """
    block = section_block(AGENT_ANALYST, "## Short-circuit conditions")
    assert "**still emit** — they are unconditional" in block, (
        "agents/analyst.md: the trivial-fix short-circuit no longer states that "
        "both new sections still emit, so the cheap path can now drop them"
    )
    assert (
        '"swept and found nothing" and "never swept" must stay distinguishable'
        in block
    ), (
        "agents/analyst.md: the short-circuit lost the reason the sections may "
        "not be skipped on a trivial fix"
    )


def test_choosing_patterns_requires_both_spellings_on_a_rename_or_removal():
    """A rename swept only under its new spelling finds no stale consumer.

    This is the sweep's sharpest edge: the old spelling finds the sites that
    still assume the old behavior, the new one finds the sites already touched
    plus any pre-existing collision. Dropping either half turns the enumerated
    list into one that looks complete and is not.
    """
    fence = contract_fence()
    assert "**Choosing patterns.**" in fence, (
        "agents/analyst.md: the `**Choosing patterns.**` paragraph is gone — "
        "the sweep no longer says how to pick a pattern"
    )
    assert (
        "run the **old** spelling and the **new** spelling both and record the "
        "hits from each" in fence
    ), (
        "agents/analyst.md: the both-spellings rule for a rename or removal is "
        "missing or reworded"
    )
    assert (
        "rather than the identifier names of the machinery the Recommended "
        "approach adds or removes" in fence
    ), (
        "agents/analyst.md: the property-targeted (not identifier-targeted) "
        "pattern rule is gone, which is what makes the sweep find consumers"
    )


def test_mechanism_definition_has_exactly_one_normative_home():
    """One normative list, in `agents/analyst.md`; everything else defers to it.

    Two roles need the term — the Analyst enumerates mechanisms, the Engineer
    must not invent one — so the temptation is to restate the list in both. A
    second normative copy drifts, and the drift is invisible: each file reads
    self-consistently while the two roles disagree about what counts.

    The obligation the paragraph attaches to the term is pinned here too,
    because it lives or dies with the definition: the same paragraph that says
    what a mechanism *is* says what enumerating one costs. Naming a mechanism
    and stopping there produces exactly the `### Blast radius` the
    design-question rung fires against — one that names the mechanism whose
    unwalked leg the Engineer then trips over.
    """
    homes = [
        path.relative_to(AGENTS_DIR.parent).as_posix()
        for path in shipped_files()
        if CANONICAL_HOME_SENTENCE in path.read_text(encoding="utf-8")
    ]
    assert homes == [AGENT_ANALYST], (
        "the `mechanism` definition must have exactly one canonical home "
        f"(`{AGENT_ANALYST}`) — found it declared in {homes}"
    )
    block = section_block(AGENT_ANALYST, PRODUCER_HEADING)
    assert CANONICAL_HOME_SENTENCE in block, (
        "agents/analyst.md: the canonical-home declaration moved out of the "
        "`### Blast radius` lifecycle-axis paragraph that downstream files cite"
    )
    assert LIFECYCLE_LEGS in block, (
        "agents/analyst.md: the lifecycle-axis paragraph no longer enumerates "
        "the legs to name for each mechanism (created / read / mutated / torn "
        "down / observable / documented), so a mechanism can now be enumerated "
        "with no sites at all and still satisfy the section"
    )
    assert LIFECYCLE_EVERY_SCOPE in block, (
        "agents/analyst.md: the lifecycle legs are no longer required in every "
        "scope the change touches and on every exit path — the legs on the "
        "normal-completion path now stand in for the cancel, abort, and "
        "interruption paths, which is where a missing leg actually hides"
    )
    assert LIFECYCLE_DESIGN_GAP in block, (
        "agents/analyst.md: a missing lifecycle leg is no longer declared a "
        "**design gap** to report at the gate, so the Analyst may notice one "
        "and say nothing — leaving reviewers to discover one leg per round, "
        "the serial discovery this section exists to end"
    )

    engineer = read(AGENT_ENGINEER)
    assert ENGINEER_DEFERS_TO_CANONICAL in engineer, (
        "agents/engineer.md: no longer points at the Analyst's lifecycle-axis "
        "paragraph as the definition's canonical home"
    )
    assert "**non-normatively**" in engineer, (
        "agents/engineer.md: its mechanism list is no longer marked "
        "non-normative, so it now reads as a second definition"
    )
    assert "The canonical list governs wherever the two differ." in engineer, (
        "agents/engineer.md: the tie-breaker sentence that subordinates its own "
        "gloss to the canonical list is gone"
    )


# --------------------------------------------------------------------------
# Section-list enumerations
# --------------------------------------------------------------------------


def test_every_section_enumeration_agrees_with_the_contract_fence():
    """The prose section lists are ordered prefixes of the contract fence.

    Three sites write the proposal's shape out in prose. The fence is what the
    Analyst actually emits; the frontmatter `description` is what Claude Code
    shows, and `/quo-fix-issue`'s surfacing paragraph is what the orchestrator
    expects to render. A site that misses a section describes a proposal the
    Analyst does not produce.

    Unrecognized tokens are filtered rather than rejected, because the surfacing
    paragraph legitimately closes with non-section tokens (`Upstream-fetch
    status` is a section, but `verdict trailer` is not). The filter is bounded to
    the run's tail, because inside the run it hides drift the order check cannot
    see: a token inserted mid-run — a section the fence does not have, or one
    whose name drifted apart from the fence's — is silently dropped, after which
    the surviving tokens still line up as a clean prefix and the site passes
    while describing a proposal shape the Analyst does not emit.
    """
    sections = contract_sections()
    for label, (relpath, anchor, terminator) in ENUMERATION_SITES.items():
        tokens = enumeration_tokens(relpath, anchor, terminator)
        indices = [i for i, token in enumerate(tokens) if token in sections]
        known = [tokens[i] for i in indices]
        last_known = indices[-1] if indices else 0
        interleaved = [
            token for token in tokens[:last_known] if token not in sections
        ]
        assert not interleaved, (
            f"{label}: {interleaved} sits among the recognized section names "
            "rather than after them — a token inside the run names no section of "
            "the contract fence, so it is either a section this site invented or "
            "one whose name has drifted from the fence's.\n  "
            f"enumerated: {tokens}\n  contract:   {sections}"
        )
        assert known == sections[: len(known)], (
            f"{label}: the enumerated section list does not match the contract "
            f"fence's order.\n  enumerated: {known}\n  contract:   "
            f"{sections[: len(known)]}"
        )
        for heading in ("Blast radius", "Policy decisions this change implies"):
            assert heading in tokens, (
                f"{label}: the enumeration no longer names {heading!r} — "
                f"found {tokens}"
            )


# --------------------------------------------------------------------------
# Directive sections
# --------------------------------------------------------------------------


def test_every_directive_enumeration_site_names_all_three_sections():
    """All three sections travel as *directive*, not as context.

    Section 3's Approve branch is what makes the user's approval cover the
    enumerated sites and the ratified policy answers, and the Engineer dispatch
    is what carries them. A site that lists only `### Recommended approach`
    quietly demotes the other two to background reading the Engineer may skip.
    """
    for label, (relpath, anchor) in DIRECTIVE_SITES.items():
        paragraph = paragraph_with(relpath, anchor)
        for section in DIRECTIVE_SECTIONS:
            assert f"`{section}`" in paragraph, (
                f"{label}: no longer names `{section}` among the directive "
                "sections it carries forward"
            )


def test_authoritative_directive_section_carries_all_three_on_the_directive_side():
    """`#### Authoritative design directive` splits directive from context.

    Its enumeration spans two bullets, and the split is the point: the first two
    bullets are directive, the third is context. Moving `### Blast radius` or
    `### Policy decisions this change implies` into the context bullet is a
    silent demotion.
    """
    block = section_block(QUO_FIX_ISSUE, DIRECTIVE_SECTION_HEADING)
    for section in DIRECTIVE_SECTIONS:
        assert f"`{section}`" in block, (
            f"{DIRECTIVE_SECTION_HEADING}: no longer names `{section}`"
        )
    assert (
        "These sit on the **directive** side alongside the Recommended "
        "approach, not the context side" in block
    ), (
        f"{DIRECTIVE_SECTION_HEADING}: the directive-not-context classification "
        "for the two new sections is gone"
    )


# --------------------------------------------------------------------------
# Relay chain — one heading string at every hop
# --------------------------------------------------------------------------


def test_every_relay_hop_names_the_one_heading_string():
    """`## Blast radius` is spelled identically at every hop.

    The chain has no schema and no runtime check: each hop finds the block by
    matching that literal heading. A hop that renames it — to `## Blast-radius`,
    `## Impact`, anything — produces no error anywhere. The list simply stops
    arriving, and `/quo-engineer-review` silently stops verifying against it.

    `RELAY_HOPS` deliberately excludes the two wrapper role files: their anchor
    sentence contains the heading string, so asserting the heading against the
    paragraph the anchor selected would assert only that the anchor matched
    itself. Those two hops are pinned by the byte-identical-bullet and
    forwards-the-block tests instead.
    """
    for label, (relpath, anchor) in RELAY_HOPS.items():
        paragraph = paragraph_with(relpath, anchor)
        assert f"`{RELAY_HEADING}`" in paragraph, (
            f"{label} ({relpath}): this relay hop no longer names the "
            f"`{RELAY_HEADING}` heading string, so the chain breaks here "
            "without failing anywhere"
        )


def test_the_directive_relay_hop_also_names_the_policy_section():
    """The Engineer's directive bullet relays both new sections, not just one.

    `RELAY_HOPS` above pins the one heading the whole chain keys on, so it
    checks this bullet for `## Blast radius` alone. But the bullet is also the
    **only** place `agents/engineer.md` mentions the policy section at all: it
    enumerates what the `## Authoritative design directive` block carries, and
    dropping the policy section from that enumeration would leave the Engineer
    told the directive carries a Recommended approach and a Blast radius and
    nothing else — while every relay-hop assertion above stayed green.

    The bullet names the section in running prose rather than as a backticked
    heading, which is why it is deliberately **not** a `DIRECTIVE_SITES` entry:
    that loop matches each section as `` `### ...` `` and would fail here on the
    Recommended approach too, which this bullet also names in prose.
    """
    relpath, anchor = RELAY_HOPS[
        "agents/engineer.md authoritative-directive bullet"
    ]
    bullet = paragraph_with(relpath, anchor)
    assert POLICY_SECTION_NAME in bullet, (
        f"{relpath}: the authoritative-directive bullet no longer names "
        f"{POLICY_SECTION_NAME!r} among what the directive block carries. This "
        "is the file's sole mention of that section, so the Engineer now has "
        "no statement anywhere that the directive carries it"
    )


def test_relay_hops_that_must_forward_an_empty_section_say_so():
    """"Nothing to verify" and "not supplied" must stay distinguishable.

    Both orchestrator-side relays forward the section even when it carries only
    its fixed empty line. Omitting the heading instead collapses the two states
    at the consumer, which is precisely the distinction check #8 keys on.
    """
    for label in EMPTY_LINE_RELAY_HOPS:
        relpath, anchor = RELAY_HOPS[label]
        paragraph = paragraph_with(relpath, anchor)
        assert (
            "**Relay it even when the Analyst's section carried only its fixed "
            "empty line**" in paragraph
        ), (
            f"{label}: no longer requires relaying the section when it is empty"
        )
        assert f"`{BLAST_RADIUS_EMPTY_LINE}`" in paragraph, (
            f"{label}: no longer names the fixed empty line "
            f"{BLAST_RADIUS_EMPTY_LINE!r} it must relay"
        )
        assert '"nothing to verify" rather than "not supplied"' in paragraph, (
            f"{label}: lost the reason the empty section is still relayed"
        )


def test_fixed_empty_lines_are_byte_identical_at_every_site():
    """Each empty-case line is one string, repeated exactly.

    The blast-radius line is produced in `agents/analyst.md` and quoted at three
    sites in `/quo-fix-issue` (the surfacing paragraph, the Code Reviewer relay,
    the PM relay). A site that paraphrases it — "no invariants affected", say —
    makes the orchestrator's own prose disagree with what the Analyst emits.

    The policy line is pinned for a sharper reason than prose agreement: it is
    *matched*, not just quoted. `/quo-fix-issue`'s gate preamble keys its
    conditional on the section being "anything other than its fixed
    `None — …` line", so a paraphrase at either end silently flips that test —
    an empty section reads as non-empty and the preamble announces policy
    decisions the proposal does not carry.

    The counts are exact rather than "at least one" on purpose. A too-low count
    catches a paraphrase; the upper bound catches the opposite failure, a copy
    of the line pasted into a site that then owes it a relay obligation nobody
    wrote. When a site is legitimately added or removed, update the count here
    and confirm the new site quotes the line byte-for-byte.
    """
    counts = {
        BLAST_RADIUS_EMPTY_LINE: {AGENT_ANALYST: 1, QUO_FIX_ISSUE: 3},
        POLICY_EMPTY_LINE: {AGENT_ANALYST: 2, QUO_FIX_ISSUE: 2},
    }
    for line, per_file in counts.items():
        for relpath, expected in per_file.items():
            found = read(relpath).count(line)
            assert found == expected, (
                f"{relpath}: expected {expected} byte-identical occurrence(s) "
                f"of {line!r}, found {found} — a site has paraphrased, dropped, "
                "or duplicated the fixed empty-case line"
            )


def test_every_review_invoker_role_file_forwards_the_blast_radius_block():
    """A role that drives `/quo-engineer-review` must forward the upstream list.

    The check lives in the skill, but the block only reaches it if the wrapper
    passes it through. A role file that gains the review invocation without
    gaining the forward drops the sweep verification on that lane entirely —
    the same failure the completeness-evidence relay guards against.
    """
    for path in agent_files():
        text = path.read_text(encoding="utf-8")
        if "quo-engineer-review" not in text:
            continue
        assert f"`{RELAY_HEADING}`" in text, (
            f"agents/{path.name}: invokes `/quo-engineer-review` but does not "
            f"forward the upstream `{RELAY_HEADING}` block, so the review's "
            "sweep verification has nothing to check against on this lane"
        )


def test_wrapper_relay_sentences_are_byte_identical_in_both_role_files():
    """Both `/quo-engineer-review` wrappers state the relay in the same words.

    They feed the same check in the same skill, so divergence means one caller
    develops a different rule than the other — and the lane whose rule quietly
    weakened is the one nobody notices, because the other lane keeps producing
    the check.

    What is pinned is the four `WRAPPER_RELAY_SENTENCES`, each by substring —
    the rule, the forward-under-the-same-heading obligation, the forward-when-
    empty obligation, and the forward-nothing-when-absent negative branch. The
    bullets are *not* pinned as wholes: each also names its own dispatch path,
    and those clauses differ by design (see the constant's comment above).
    """
    for relpath in (AGENT_CODE_REVIEWER, AGENT_PM):
        text = read(relpath)
        for sentence in WRAPPER_RELAY_SENTENCES:
            assert sentence in text, (
                f"{relpath}: the relay bullet's sentence is missing or "
                f"reworded — it must stay byte-identical at both wrapper "
                f"sites: {sentence!r}"
            )


# --------------------------------------------------------------------------
# Consumer — `/quo-engineer-review` check #8
# --------------------------------------------------------------------------


def test_check_8_consumes_the_upstream_list_as_an_independent_second_list():
    """The upstream list's value is that the implementer did not write it.

    Verifying only against the Engineer's own completeness evidence cannot
    surface an entry that list never had — which is the whole serial-discovery
    failure the upstream list exists to close. A revision that folds the two
    lists into one erases the independence without erasing the prose.
    """
    paragraph = paragraph_with(
        QUO_ENGINEER_REVIEW, RELAY_HOPS[
            "/quo-engineer-review check #8 sweep verification"
        ][1]
    )
    assert "**second, independently-authored enumerated site list**" in paragraph, (
        "/quo-engineer-review: check #8 no longer treats the upstream list as a "
        "second, independently-authored list"
    )
    assert (
        "a sweep verified only against the implementer's own list cannot "
        "surface an entry that list never had" in paragraph
    ), "/quo-engineer-review: check #8 lost the reason the second list matters"
    assert "verify the diff against **both**" in paragraph, (
        "/quo-engineer-review: check #8 no longer verifies against both lists "
        "when both are present"
    )
    assert UPSTREAM_LIST_LIFECYCLE_LEGS in paragraph, (
        "/quo-engineer-review: check #8 no longer describes the upstream list "
        "as carrying the lifecycle legs of each mechanism the change "
        "introduces, only its invariant sites — so the reviewer verifies half "
        "of what `agents/analyst.md`'s lifecycle-axis paragraph obliges the "
        "producer to emit, and an unwalked leg passes review"
    )


def test_explicitly_empty_upstream_list_counts_as_supplied_without_firing_a_finding():
    """An empty upstream list is "nothing to verify", not "nothing supplied".

    Both halves matter and pull in opposite directions: it counts as supplied
    (so the review can tell it from a list nobody relayed), yet it must not
    activate the missing-completeness-list finding (an empty list gives the
    Engineer nothing to reconcile against). Losing either half turns the empty
    case into a spurious finding or into an invisible one.
    """
    paragraph = paragraph_with(
        QUO_ENGINEER_REVIEW,
        "**When the supplied list explicitly states that it enumerates no "
        "sites**",
    )
    assert (
        "it counts as a list having been **supplied**, so the review can tell "
        "it from a list the caller never relayed" in paragraph
    ), (
        "/quo-engineer-review: an explicitly-empty upstream list no longer "
        "counts as supplied"
    )
    assert (
        "it does **not** activate that clause's missing-completeness-list "
        "finding" in paragraph
    ), (
        "/quo-engineer-review: an explicitly-empty upstream list now fires the "
        "missing-completeness-list finding, which it has nothing to reconcile "
        "against"
    )
    assert EMPTY_LIST_LICENSED_CHECK in paragraph, (
        "/quo-engineer-review: the explicitly-empty-list rule no longer says "
        "which check the empty list does license, leaving three prohibitions "
        "and no instruction — so nobody tests the claim the empty list makes, "
        "and a diff that does add, remove, or weaken an invariant or introduce "
        f"a mechanism passes unremarked: {EMPTY_LIST_LICENSED_CHECK!r}"
    )


def test_second_order_effects_absorbs_the_list_gap_and_the_other_lane_record():
    """The two non-actionable entry kinds route to the narrative subsection.

    Neither is an Engineer defect, so neither belongs in the numbered list — the
    sole routing surface, reserved for actionable items. Both forms of the list
    gap (per-site, and the single bullet the explicitly-empty case licenses) plus
    the out-of-lane record must be named in the emission contract, or check #8
    routes findings the orchestrator will act on to a fix round that has nothing
    to fix.
    """
    text = read(QUO_ENGINEER_REVIEW)
    assert (
        "a **list gap** — a site the diff touches and handles correctly that "
        "appeared on neither supplied list, or, when the upstream list was "
        "explicitly empty, a single bullet against the upstream analysis rather "
        "than one bullet per site" in text
    ), (
        "/quo-engineer-review: the `### Second-order effects` contract no longer "
        "names both forms of the list gap"
    )
    assert (
        "an **out-of-lane upstream site left without a disposition**, recorded "
        "as owed to the lane that owns it" in text
    ), (
        "/quo-engineer-review: the `### Second-order effects` contract no longer "
        "names the other-lane record"
    )
    assert (
        "and records of work owed to another lane, which this review's numbered "
        "list cannot route" in text
    ), (
        "/quo-engineer-review: the double-emission constraint no longer exempts "
        "records owed to another lane, so it now demands they also be emitted as "
        "numbered work items this review cannot route"
    )


def test_check_8_routes_the_two_upstream_shortfalls_at_the_check_site():
    """One shortfall is a work item, the other an audit-trail note; never both.

    The asymmetry is the reason check #8 splits them. An in-lane upstream entry
    the diff neither changed nor dispositioned is work the Engineer owes, so it
    belongs in the numbered list the orchestrator turns into a fix round; a site
    the diff already handles correctly owes nobody anything, so a numbered entry
    for it buys a round with nothing to fix. Both kinds are named in the
    `### Second-order effects` emission contract as well, but a reviewer working
    check #8 top-to-bottom decides the routing right here and may never read
    that contract — so the routing has to survive at the check, not only
    downstream of it.
    """
    for label, (anchor, expected_sentences) in UPSTREAM_SHORTFALL_ROUTING.items():
        bullet = paragraph_with(QUO_ENGINEER_REVIEW, anchor)
        for expected in expected_sentences:
            assert expected in bullet, (
                f"/quo-engineer-review check #8, {label}: the routing sentence "
                "is missing or reworded at the check site, leaving the routing "
                "stated only in the emission contract a reviewer working this "
                f"check may never reach: {expected!r}"
            )


def test_kind_groups_agree_between_the_engineer_and_check_8():
    """Both sides name the same three out-of-lane kind groups.

    The Engineer dispositions entries in those groups to the writer lanes; check
    #8 exempts exactly those groups from being findings against the Engineer. If
    the two lists diverge, a site is either double-owned or owned by nobody —
    and the second is silent.
    """
    for relpath in (AGENT_ENGINEER, QUO_ENGINEER_REVIEW):
        assert KIND_GROUPS in read(relpath), (
            f"{relpath}: no longer names the three out-of-lane kind groups as "
            f"{KIND_GROUPS!r} — the Engineer's handoff and check #8's exemption "
            "must cover the same set"
        )


def test_both_sides_resolve_the_lane_by_their_own_scope_not_the_group_name():
    """An upstream mislabel must not exempt a site from every lane.

    Skill repos are the sharp case: markdown under `skills/` or `agents/` is
    program source, so an upstream list that files it under a docs kind would
    otherwise hand it out of the code lane and into a writer lane that does not
    claim it. Both sides therefore resolve the lane themselves.
    """
    for relpath in (AGENT_ENGINEER, QUO_ENGINEER_REVIEW):
        assert LANE_BY_OWN_SCOPE in read(relpath), (
            f"{relpath}: no longer resolves an upstream entry's lane by its own "
            "scope, so an upstream group name can now exempt a site no lane owns"
        )
    # The target must be asserted as a standalone **heading line**, not as a
    # substring of the file. Check #8's own cross-reference spells the heading
    # inside its bullet, so a containment check is satisfied by the pointer
    # alone: delete the real `### Scope: …` section and the dangling-reference
    # message below can never fire, which is the shape this assertion had.
    scope_headings = [
        line
        for line in read(QUO_ENGINEER_REVIEW).splitlines()
        if line.strip() == REVIEW_SCOPE_HEADING
    ]
    assert len(scope_headings) == 1, (
        "/quo-engineer-review: check #8 points at "
        f"{REVIEW_SCOPE_HEADING!r} to resolve the lane, but that section exists "
        f"as a heading line {len(scope_headings)} time(s) in this file — the "
        "cross-reference dangles, so a reviewer told to resolve the lane by "
        "that section has nothing to resolve it against"
    )


def test_out_of_lane_disposition_is_emitted_and_credited_as_the_accounting():
    """The handshake that keeps a lane boundary from reading as a missed site.

    The two files above agree on *which* groups are out of lane; this is what
    happens to an entry in one. The Engineer does not implement it, but does
    list it with its disposition; check #8 does not treat it as a finding, but
    does credit that disposition as the accounting it asked for. Each half is
    inert without the other, and each fails in its own direction: an Engineer
    that stops listing dispositioned entries hands the reviewer a diff with an
    upstream entry it can only read as untouched, and a reviewer that stops
    crediting the disposition emits a finding against work that was accounted
    for — a fix round for a site the Engineer correctly refused to touch.
    """
    assert DISPOSITION_IS_NOT_DROPPING in read(AGENT_ENGINEER), (
        "agents/engineer.md: an out-of-lane upstream entry may now be "
        "dispositioned without being listed in the completeness evidence, so "
        "the reviewer sees a lane boundary as a missed site"
    )
    assert DISPOSITION_IS_THE_ACCOUNTING in read(QUO_ENGINEER_REVIEW), (
        "/quo-engineer-review: check #8 no longer credits the Engineer's "
        "to-another-lane disposition as the accounting this bullet asks for, so "
        "an entry the Engineer correctly dispositioned now reads as one left "
        "without a disposition"
    )


def test_an_upstream_list_with_no_completeness_evidence_is_verified_alone():
    """A list that arrived with no reconciliation is still verifiable.

    This is the third shortfall shape, and the empty-list rule does not reach
    it: there the list is empty and there is nothing to check, here the list is
    full and only the Engineer's reconciliation is missing. Without this
    sentence the reviewer has no stated route for the case and the most
    available reading is to skip the sweep verification entirely — discarding
    the independently-authored list precisely when it is the only list there
    is. The absent evidence is handled separately, as a list defect, so the two
    failures stay distinct rather than collapsing into one.
    """
    assert UPSTREAM_LIST_ALONE in read(QUO_ENGINEER_REVIEW), (
        "/quo-engineer-review: check #8 no longer says to verify the diff "
        "against the upstream list alone when no Engineer completeness "
        "evidence arrived, so the one independently-authored list in hand goes "
        "unused in exactly the case where nothing else is available"
    )


def test_engineer_owes_no_reconciliation_for_an_explicitly_empty_upstream_list():
    """An empty upstream list carries nothing to reconcile.

    The mirror of check #8's empty-list rule. Without it the Engineer owes
    completeness evidence for a list with no entries, which is the sweep
    obligation firing on every dispatch that relays an empty section — i.e. on
    the majority of them.
    """
    text = read(AGENT_ENGINEER)
    assert (
        "**An upstream list that explicitly states it enumerates no sites**"
        in text
    ), (
        "agents/engineer.md: the explicitly-empty upstream-list carve-out is gone"
    )
    assert (
        "carries nothing to reconcile, so it does not trigger the obligation on "
        "its own" in text
    ), (
        "agents/engineer.md: an explicitly-empty upstream list now triggers the "
        "reconcile-and-disposition obligation it has no entries for"
    )
    assert (
        "A supplied enumerated site list triggers this reconcile-and-disposition "
        "obligation **on its own**" in text
    ), (
        "agents/engineer.md: a non-empty upstream list no longer triggers the "
        "reconcile obligation by itself, so a non-sweep-shaped assignment can "
        "now leave upstream entries unaccounted for"
    )


# --------------------------------------------------------------------------
# Design questions — the Engineer's way out, and its receiver
# --------------------------------------------------------------------------


def test_engineer_returns_design_questions_instead_of_inventing_mechanisms():
    """Stop and ask; do not pick a mechanism the design never enumerated.

    The rule is mode-independent on purpose — an unenumerated mechanism landing
    in the diff with no design decision behind it costs a round in either mode.
    In execute mode the status ladder is the tell, so the partial Subtask must
    stay `in_progress`: flipped to `done` it reads to the dispatcher as finished.

    The heading is only half of what the receiver needs. `/quo-fix-issue` puts
    this return's *contents* into the revising Analyst's prompt where the user's
    revision feedback would go, so the required payload is pinned here too — a
    bullet that keeps the heading but stops requiring the four items produces a
    return that routes correctly and says nothing the Analyst can act on.
    """
    text = read(AGENT_ENGINEER)
    assert (
        "**Return design questions; do not invent mechanisms (both modes).**"
        in text
    ), "agents/engineer.md: the design-question bullet is gone"
    assert (
        "This rule is mode-independent — it binds identically in fix mode and "
        "execute mode." in text
    ), "agents/engineer.md: the design-question rule is no longer mode-independent"
    assert f"`{DESIGN_QUESTION_HEADING}`" in text, (
        "agents/engineer.md: no longer names the "
        f"`{DESIGN_QUESTION_HEADING}` return heading its receiver keys on"
    )
    assert DESIGN_QUESTION_PAYLOAD_PRODUCER in text, (
        "agents/engineer.md: the design-question return no longer has to name "
        "the mechanism, why it blocks the assignment, and the alternatives, so "
        "the heading can now arrive at `/quo-fix-issue` with no payload behind "
        "it and the revising Analyst is re-dispatched on a bare question: "
        f"{DESIGN_QUESTION_PAYLOAD_PRODUCER!r}"
    )
    assert DESIGN_QUESTION_PARTIAL_SPLIT_PRODUCER in text, (
        "agents/engineer.md: the design-question return no longer has to say "
        "which parts of the assignment landed and which were left undone, so "
        "neither the dispatcher nor the revising Analyst can tell from the "
        "return that the diff on disk is partial"
    )
    assert (
        "**In execute mode, do not run the `status=done` transition on such a "
        "return**" in text
    ), (
        "agents/engineer.md: a partial Subtask may now be flipped to `done`, "
        "which reads to the dispatcher as a finished unit"
    )
    assert "leave the Subtask at `in_progress`" in text, (
        "agents/engineer.md: the partial Subtask no longer stays `in_progress`, "
        "so the partial return is undetectable from the ticket state"
    )


def test_execute_mode_status_ladder_points_at_the_design_question_exception():
    """The status bullet names its one exception where a reader will hit it.

    An Engineer reading "mark `status=done` when finishing it" in isolation has
    no reason to look further; the cross-reference is what keeps the ladder and
    the design-question rule from being read as contradictory.
    """
    text = read(AGENT_ENGINEER)
    assert (
        "One exception: a Subtask you stop partway through on a design question "
        "stays at `in_progress`" in text
    ), (
        "agents/engineer.md: the execute-mode status ladder no longer "
        "cross-references the design-question exception"
    )


def test_fix_issue_receives_the_design_question_and_routes_it_as_a_revise():
    """A `## Design question` return is a proposal revision, not a review round.

    It is evidence the approved `### Blast radius` missed a mechanism, so the
    right receiver is Section 3's Revise branch — not the Code Reviewer, which
    would be handed a partial diff and asked to review it as finished work.
    """
    paragraph = paragraph_with(
        QUO_FIX_ISSUE,
        f"**An Engineer return carrying a `{DESIGN_QUESTION_HEADING}` is not a "
        "Phase A completion either.**",
    )
    assert f"`{PRODUCER_HEADING}` **missed a mechanism**" in paragraph, (
        "/quo-fix-issue: the design-question rung no longer frames the return as "
        "evidence the approved Blast radius missed a mechanism"
    )
    assert (
        "do **not** dispatch the Code Reviewer against that partial diff"
        in paragraph
    ), (
        "/quo-fix-issue: the design-question rung no longer suppresses the Code "
        "Reviewer dispatch over the partial diff"
    )
    assert "**Section 3 Revise, by reference**" in paragraph, (
        "/quo-fix-issue: the design-question rung no longer routes the question "
        "into Section 3's Revise branch"
    )

    text = read(QUO_FIX_ISSUE)
    assert (
        "under the next `analyst-<issue-id>-rev<n>` name, with the same Issue "
        "body verbatim" in text
    ), (
        "/quo-fix-issue: the design-question re-dispatch no longer reuses "
        "Section 3's Revise naming and dispatch shape"
    )
    assert (
        "**unless that return carries a `## Design question`**" in text
    ), (
        "/quo-fix-issue: Phase A's loop no longer branches on a design-question "
        "return before dispatching the Code Reviewer"
    )


def test_design_question_re_dispatch_tells_the_analyst_the_tree_is_mid_change():
    """The producer states it, the receiver acts on it; both halves are pinned.

    On this one path the Analyst is dispatched against a tree that already
    carries half the fix, and nothing in the tree says so — a partial diff and a
    finished one look identical on disk. The fact travels only in the prompt, so
    the two halves fail in opposite directions and neither is inferable from the
    other. Drop `/quo-fix-issue`'s clause and the Analyst re-baselines against
    mid-change source, reading the Engineer's own half-landed edits as
    pre-existing code and sweeping a `### Blast radius` against them. Drop
    `agents/analyst.md`'s and the prompt keeps saying it to a role file that no
    longer tells the Analyst what to do with what it was told.

    The same rung is where the Engineer's `## Design question` payload lands, so
    the receiving half of that contract is pinned here as well: this paragraph
    names the four items it forwards in place of the user's revision feedback,
    and `agents/engineer.md` requires the return to carry them. It is also where
    the prior proposal's `### Deferred refinements` block is carried forward,
    which is pinned here for the same reason — the block travels only in this
    prompt, and losing the clause loses each prior deferral silently at the
    revision's Approve.
    """
    rung = paragraph_with(QUO_FIX_ISSUE, PARTIAL_ON_DISK_CLAUSE)
    assert DESIGN_QUESTION_PAYLOAD_RECEIVER in rung, (
        "/quo-fix-issue: the design-question re-dispatch no longer enumerates "
        "what the Engineer's return carries into the Analyst's prompt in place "
        "of the user's revision feedback, so the relay may now forward a bare "
        f"`{DESIGN_QUESTION_HEADING}` heading and the receiving half of "
        "`agents/engineer.md`'s payload requirement is gone: "
        f"{DESIGN_QUESTION_PAYLOAD_RECEIVER!r}"
    )
    assert MID_CHANGE_CLAUSE in rung, (
        "/quo-fix-issue: the design-question re-dispatch still names the partial "
        "implementation on disk but no longer says the Analyst must read "
        f"{MID_CHANGE_CLAUSE!r} — the prompt now reports the fact without "
        "stating what the Analyst is to conclude from it"
    )
    assert RUNG_LIFECYCLE_CLAUSE in rung, (
        "/quo-fix-issue: the design-question re-dispatch no longer requires the "
        "prompt to say the revised `### Blast radius` must cover the "
        "**lifecycle** of whatever mechanism it now enumerates — the rung fired "
        "because a mechanism went unenumerated, so a revision that names it "
        "without walking its legs buys one round and re-raises the same "
        "question at the next unwalked leg"
    )
    assert RUNG_DEFERRAL_CARRY_FORWARD_CLAUSE in rung, (
        "/quo-fix-issue: the design-question re-dispatch no longer says the "
        "prior proposal quoted **in full** includes its "
        f"`{DEFERRED_REFINEMENTS_HEADING}` block, so the revision is written "
        "against the stripped user-facing prose and every prior deferral is "
        "cleared by the supersede-and-clear rule at the next Approve with no "
        f"carrier left anywhere: {RUNG_DEFERRAL_CARRY_FORWARD_CLAUSE!r}"
    )

    opening = paragraph_with(AGENT_ANALYST, ANALYST_MID_IMPLEMENTATION_ANCHOR)
    assert MID_CHANGE_CLAUSE in opening, (
        "agents/analyst.md: the opening paragraph no longer tells the Analyst to "
        f"read {MID_CHANGE_CLAUSE!r}, so `/quo-fix-issue`'s producer clause "
        "arrives at a receiver that does nothing with it"
    )
    assert ANALYST_LIFECYCLE_CLAUSE in opening, (
        "agents/analyst.md: the opening paragraph no longer tells the Analyst "
        "that the revised `### Blast radius` must cover the mechanism's "
        "**lifecycle**, so `/quo-fix-issue`'s matching clause again arrives at "
        "a receiver that does nothing with it"
    )
    assert "names the partial implementation already on disk" in opening, (
        "agents/analyst.md: the opening paragraph no longer says the dispatch "
        "prompt names the partial implementation on disk, dropping the receiving "
        "half of `/quo-fix-issue`'s obligation to name it"
    )

    text = read(AGENT_ANALYST)
    for label, clause in ANALYST_MID_CHANGE_ADVERTISEMENTS.items():
        assert clause in text, (
            f"agents/analyst.md {label}: no longer advertises the "
            "mid-implementation dispatch against a tree carrying a partial fix, "
            "so this site now describes a role that only ever runs against the "
            f"pre-fix baseline: {clause!r}"
        )


def test_design_question_rung_introduces_no_machinery_of_its_own():
    """The rung is Section 3's Revise branch entered from Section 4.

    Reusing the existing gate, task-name class, and carrier is what keeps this a
    routing rung rather than a design change. A new gate here would ask the
    operator to answer the same design question twice, and a new name class
    would need its own close-out sweep in two sections.
    """
    text = read(QUO_FIX_ISSUE)
    closing = (
        "This receiver introduces no gate, option, task-name class, marker, or "
        "manifest field of its own — it is Section 3's Revise branch, entered "
        "from Section 4."
    )
    assert closing in text, (
        "/quo-fix-issue: the design-question rung no longer declares that it "
        "adds no gate, option, task-name class, marker, or manifest field"
    )
    start = text.index(
        f"**An Engineer return carrying a `{DESIGN_QUESTION_HEADING}` is not a "
        "Phase A completion either.**"
    )
    rung = text[start:text.index(closing, start)]
    for token, machinery in (
        (GATE_TASK_PREFIX, "task-name class"),
        (GATE_TOOL, "gate"),
    ):
        minted = minting_segments(rung, token)
        assert not minted, (
            f"/quo-fix-issue: the design-question rung names {token!r} in a "
            f"sentence that does not attribute it to {SECTION_3_ATTRIBUTION}, "
            f"so the rung now reads as minting a {machinery} of its own rather "
            f"than reusing {SECTION_3_ATTRIBUTION}'s gate: {minted}"
        )
    assert "**The durable carrier is the Analyst task.**" in rung, (
        "/quo-fix-issue: the rung no longer names the active Analyst task as "
        "what holds Phase A suspended, leaving the suspension in conversation"
    )


@pytest.mark.parametrize(
    "token, prose",
    [
        # The colon case. Markdown lead-ins that introduce a bullet or a clause
        # end in `:`, not in `.`, so a splitter keyed on sentence-enders alone
        # never cuts here — and the mint that follows inherits the lead-in's
        # `Section 3` attribution. This is the shape the rung actually grew.
        (
            GATE_TASK_PREFIX,
            "Then route the question as a **Section 3 Revise, by reference**: "
            "create a `gate-designquestion-<short-suffix>` task of its own to "
            "carry it.",
        ),
        # The newline case. A markdown line frequently carries no terminal
        # punctuation at all, so the following line is not cut off from it
        # either — note the shield line here ends in a bare word, which is why
        # the `\s+` in a sentence-ender-only split does not reach it.
        (
            GATE_TOOL,
            "- The rung is entered from Section 4 and reuses Section 3's "
            "routing\n"
            "  Fire a fresh `AskUserQuestion` gate for the design question "
            "before re-dispatching the Analyst.",
        ),
    ],
)
def test_minting_detector_flags_a_mint_a_shield_lead_in_would_hide(token, prose):
    """Proof the guard above is not hollow — attribution cannot be borrowed.

    The guard reads green in two ways: because the rung mints nothing, or
    because the segment carrying a mint is wide enough to have swallowed an
    unrelated `Section 3` mention. Only the first is the check doing its job.
    These drive the real `SENTENCE_SPLIT` over prose where a preceding clause
    supplies the attribution and the mint is genuinely new; a splitter that
    cuts only at `.!?` merges the two and reports nothing.
    """
    assert minting_segments(prose, token), (
        f"a segment minting {token!r} of its own reads as attributed to "
        f"{SECTION_3_ATTRIBUTION} once split — the boundary between the "
        f"attributing clause and the mint was not cut: {prose!r}"
    )


@pytest.mark.parametrize(
    "prose",
    [
        # The rung is *supposed* to be able to name what it reuses. A guard
        # that flagged these would fail on prose that is exactly right, which
        # is why the split is not drawn any finer than `.:!?` and `\n`.
        "The rung reuses Section 3's `gate-askuserquestion-<short-suffix>` "
        "task rather than minting a task-name class of its own.",
        "Section 3's `AskUserQuestion` gate is the one the operator answers; "
        "the rung re-enters it rather than firing a second one.",
        "- The durable carrier is the Analyst task, not a new marker\n"
        "  Section 3's `gate-askuserquestion-<short-suffix>` task is reused "
        "as-is.",
    ],
)
def test_minting_detector_accepts_the_rungs_reuse_phrasings(prose):
    """The finer split introduces no false positive on legitimate reuse.

    Each segment that names a token here also carries its `Section 3`
    attribution, including across the colon and newline boundaries the split
    now cuts at.
    """
    for token in (GATE_TASK_PREFIX, GATE_TOOL):
        assert not minting_segments(prose, token), (
            f"a legitimate statement that the rung reuses "
            f"{SECTION_3_ATTRIBUTION}'s gate is flagged as minting {token!r} "
            f"of its own: {prose!r}"
        )


def test_post_completion_design_question_routes_to_the_file_branch():
    """Section 8 has no Analyst, so its design question becomes a filed Issue.

    Reusing Section 4's Revise route here would re-dispatch an Analyst that this
    section never dispatches. Filing is the honest terminal: the follow-up Issue
    carries the question and the what-landed list, and the report says which
    edits are already on disk.
    """
    text = read(QUO_FIX_ISSUE)
    assert POSTCOMP_DESIGN_QUESTION_ANCHOR in text, (
        "/quo-fix-issue: Section 8 no longer recognises a post-completion design "
        "question"
    )
    assert (
        "route the finding to this step's **File as issue tickets** branch "
        "instead" in text
    ), (
        "/quo-fix-issue: a post-completion design question no longer routes to "
        "the File branch"
    )
    assert (
        "There is no Analyst in this section, so Section 4's Revise route does "
        "not apply here" in text
    ), (
        "/quo-fix-issue: Section 8 no longer explains why it cannot reuse "
        "Section 4's Revise route, inviting a re-dispatch of an Analyst it never "
        "dispatched"
    )

    paragraph = paragraph_with(QUO_FIX_ISSUE, POSTCOMP_DESIGN_QUESTION_ANCHOR)
    assert POSTCOMP_FOLLOW_UP_ISSUE_PAYLOAD in paragraph, (
        "/quo-fix-issue: Section 8 still routes a post-completion design "
        "question to the File branch but no longer says what the follow-up "
        "Issue carries, so the filing can record that a question was asked "
        "without recording the question or the what-landed / what-did-not "
        f"split: {POSTCOMP_FOLLOW_UP_ISSUE_PAYLOAD!r}"
    )
    assert POSTCOMP_REPORT_EDITS_ON_DISK in paragraph, (
        "/quo-fix-issue: Section 8 no longer obliges the final report to say "
        "which of that finding's edits are already on disk, so the run ends "
        "with a filed Issue that reads as untouched work over a tree that "
        f"already carries part of its fix: {POSTCOMP_REPORT_EDITS_ON_DISK!r}"
    )


# --------------------------------------------------------------------------
# Analyst task lifecycle
# --------------------------------------------------------------------------


def test_proposal_recovery_rule_keeps_its_three_operative_clauses():
    """The recovery rule's content, not just the section names it enumerates.

    `test_every_directive_enumeration_site_names_all_three_sections` pins this
    site for the three section names only, so the sentences that say what to do
    when the proposal is gone could be rewritten out from under them and every
    existing assertion would still pass. All three clauses fail silently. Lose
    the first and the rule keeps its decision but stops naming the dispatches
    that trigger it, so recovery happens at whichever one the orchestrator
    notices and the rest relay a summary. Lose the second and a compacted
    orchestrator reconstructs the directive from a summary — indistinguishable,
    downstream, from one the user approved. Lose the third and the guarantee
    `/quo-engineer-review` rests on goes with it: an absent `## Blast radius`
    stops being a fault and becomes something a consumer has to tolerate as
    possibly-just-a-compaction.
    """
    paragraph = paragraph_with(QUO_FIX_ISSUE, PROPOSAL_RECOVERY_ANCHOR)
    for label, clause in PROPOSAL_RECOVERY_CLAUSES.items():
        assert clause in paragraph, (
            f"/quo-fix-issue Read-state proposal-recovery rule: {label} is "
            f"gone from the paragraph that still enumerates the three "
            f"directive sections: {clause!r}"
        )


def test_the_re_derivation_shape_is_defined_once_and_reused_by_reference():
    """What "re-derive through the Analyst" actually sends, and its one reuse.

    `test_proposal_recovery_rule_keeps_its_three_operative_clauses` pins the
    decision — re-derive rather than reconstruct — and stops there, so the shape
    that decision names could be emptied out bullet by bullet with every
    existing assertion still passing. Each bullet is what keeps the re-dispatch
    from being underspecified in a different direction, and the last of them is
    the compaction-path counterpart of the mid-change framing the readable-
    proposal branch gets: without it the Analyst sweeps a `### Blast radius`
    against a tree it believes is the pre-fix baseline.

    The rung half is pinned in the same test because the two are one contract:
    the shape is defined once *because* the rung consumes it by reference. Drop
    the rung's reuse sentence and the branch that most needs the shape — the
    proposal is unreadable, so there is nothing to quote in its place — is left
    with no instruction, or with a second copy of the shape free to drift from
    this one.
    """
    bullets = bullets_after(QUO_FIX_ISSUE, RE_DERIVATION_SHAPE_ANCHOR)
    for label, clause in RE_DERIVATION_BULLET_CLAUSES.items():
        assert clause in bullets, (
            f"/quo-fix-issue Read-state re-derivation shape: {label} is gone "
            f"from the bullets the recovery rule points at, so the Analyst "
            f"re-dispatch it defines is underspecified: {clause!r}"
        )

    rung = paragraph_with(QUO_FIX_ISSUE, RUNG_REUSE_ANCHOR)
    for label, clause in RUNG_REUSE_CLAUSES.items():
        assert clause in rung, (
            f"/quo-fix-issue design-question rung: {label} is gone from the "
            f"unreadable-proposal branch, which no longer reuses the Read-state "
            f"step's single definition of what to send instead: {clause!r}"
        )


def test_analyst_task_is_completed_the_moment_its_return_is_read():
    """Close the task on read, before the gate — not after the branch.

    Its Agent has exited, so an active task is one no completion notification
    will ever clear. Closing it on read is also what keeps the Engineer-dispatch
    precondition below from blocking the forward Approve -> Engineer dispatch on
    the Analyst that just finished.
    """
    text = read(QUO_FIX_ISSUE)
    assert MARK_ON_READ_SENTENCE in text, (
        "/quo-fix-issue: Section 3's surfacing step no longer marks the Analyst "
        "task `completed` the moment its return is read"
    )
    assert (
        "Section 3 marks the task `completed` the moment the Analyst's return "
        "is read, so an active one still has an Agent behind it" in text
    ), (
        "/quo-fix-issue: the Read-state step no longer relies on an active "
        "`analyst-*` task meaning an Analyst is genuinely in flight"
    )


def test_every_later_close_out_site_says_the_analyst_task_is_already_completed():
    """Five sites describe the task as already closed rather than closing it.

    A site that reverts to "mark it completed here" is not merely redundant: it
    implies the task is still active at that point, which contradicts the
    in-flight test the Engineer-dispatch precondition and the Phase A recovery
    branch both make.
    """
    for label, anchor in ALREADY_COMPLETED_SITES.items():
        paragraph = paragraph_with(QUO_FIX_ISSUE, anchor)
        assert "analyst-<issue-id>" in paragraph, (
            f"/quo-fix-issue {label}: no longer mentions the "
            "`analyst-<issue-id>` task at all"
        )
        assert ALREADY_COMPLETED.search(paragraph), (
            f"/quo-fix-issue {label}: no longer describes the Analyst task as "
            "already `completed` on return — this site now implies it is still "
            "active, contradicting Section 3's surfacing step"
        )


def test_every_engineer_dispatch_precondition_copy_lists_the_analyst_prefix():
    """All three copies of the prefix list block on an in-flight Analyst.

    An Analyst mid-revision is authoring the very directive the next Engineer
    round would implement, so an Engineer dispatched alongside it runs against
    the stale directive that just failed. The rule is copied three times in this
    skill, and a copy that misses the prefix is the one a reader will follow.
    """
    lines = [
        line
        for line in read(QUO_FIX_ISSUE).splitlines()
        if PREFIX_LIST_MARKER in line and PREFIX_LIST_SENTINEL in line
    ]
    assert len(lines) == EXPECTED_PREFIX_LIST_COPIES, (
        f"/quo-fix-issue: expected {EXPECTED_PREFIX_LIST_COPIES} copies of the "
        f"Engineer-dispatch precondition prefix list, found {len(lines)} — if a "
        "copy was legitimately added or removed, update this count and confirm "
        "every copy still carries the Analyst prefix"
    )
    for line in lines:
        assert ANALYST_PREFIX in line, (
            "/quo-fix-issue: an Engineer-dispatch precondition prefix list omits "
            f"{ANALYST_PREFIX}, licensing an Engineer dispatch while an Analyst "
            f"is mid-revision:\n  {line[:160]}..."
        )


def test_analyst_naming_convention_covers_the_design_question_rung():
    """`-rev<n>` is the discriminator for the design-question re-dispatch too.

    The rung is Section 3's Revise branch entered from Section 4, so it reuses
    that branch's name class. Saying so in the naming convention is what stops a
    reader from minting a new one for it — the machinery the rung's closing
    sentence promises it does not add.
    """
    paragraph = paragraph_with(
        QUO_FIX_ISSUE, "- **Analyst Agents** (dispatched per Issue in Section 3"
    )
    assert (
        "The same `-rev<n>` discriminator is used when Section 4's "
        "Reconcile-step **design-question rung** re-dispatches the Analyst"
        in paragraph
    ), (
        "/quo-fix-issue: the naming convention no longer covers the "
        "design-question rung's Analyst re-dispatch, leaving its task name "
        "unconventioned"
    )


def test_phase_a_recovery_waits_for_an_in_flight_analyst():
    """Post-compaction recovery must not review a suspended Phase A's diff.

    The generic recovery re-dispatches the Code Reviewer, which is right when
    Phase A is merely mid-loop and wrong when a design-question revision is in
    flight: the diff on disk is partial by construction, so the review would
    report the missing half as findings.
    """
    paragraph = paragraph_with(
        QUO_FIX_ISSUE, "- **Post-compaction recovery inside Phase A.**"
    )
    assert (
        "unless an `analyst-<issue-id>` task is active for this Issue"
        in paragraph
    ), (
        "/quo-fix-issue: Phase A's post-compaction recovery no longer excepts an "
        "in-flight Analyst, so it can re-dispatch the Code Reviewer against a "
        "partial diff"
    )
    assert "Match on the `analyst-<issue-id>` name **prefix** plus status" in paragraph, (
        "/quo-fix-issue: Phase A's recovery exception no longer prefix-matches, "
        "so a `-rev<n>`-discriminated Analyst task escapes the check"
    )


def test_revise_branch_carries_the_prior_proposals_deferrals_forward():
    """Section 3's Revise branch is the carry-forward clause's other home.

    A user-driven Revise reaches the same re-dispatch the design-question rung
    reaches, and loses the same thing when the clause goes: the prompt quotes
    the proposal the user *saw*, which Section 3's surfacing step stripped of
    `### Deferred refinements`, and the revision's Approve then clears the
    superseded iteration's `defer-*` tasks with nothing carrying the deferrals.
    This is the more-travelled of the two paths — the rung fires only on an
    Engineer design question, while this branch fires whenever the user asks for
    a revision — so leaving it unpinned would let the clause be deleted here
    with the suite green.
    """
    # The clause has two homes; both are pinned. The rung's copy is checked in
    # `test_design_question_re_dispatch_tells_the_analyst_the_tree_is_mid_change`
    # against its own paragraph, so deleting either copy fails exactly one test.
    paragraph = paragraph_with(QUO_FIX_ISSUE, REVISE_DISPATCH_ANCHOR)
    assert REVISE_DEFERRAL_CARRY_FORWARD_LEAD_IN in paragraph, (
        "/quo-fix-issue: Section 3's Revise branch no longer says that quoting "
        "the prior proposal **in full** includes its "
        f"`{DEFERRED_REFINEMENTS_HEADING}` block, so the re-dispatch prompt is "
        "built from the stripped user-facing prose: "
        f"{REVISE_DEFERRAL_CARRY_FORWARD_LEAD_IN!r}"
    )
    assert RUNG_DEFERRAL_CARRY_FORWARD_CLAUSE in paragraph, (
        "/quo-fix-issue: Section 3's Revise branch still names the "
        f"`{DEFERRED_REFINEMENTS_HEADING}` block but no longer says why the "
        "revising Analyst needs it, so the prompt may now forward the block "
        "without obliging a carry-or-drop decision on each prior deferral — "
        "and a deferral the revision simply omits is cleared by the "
        "supersede-and-clear rule at the next Approve with no carrier left "
        f"anywhere: {RUNG_DEFERRAL_CARRY_FORWARD_CLAUSE!r}"
    )


# --------------------------------------------------------------------------
# Scope-split and gate ratification
# --------------------------------------------------------------------------


def test_scope_split_recommendation_is_mirrored_into_deferred_refinements():
    """The gate-visible recommendation is also written where it survives.

    `### Blast radius` is surfaced to the user and then discarded with the
    conversation; `### Deferred refinements` is the block the orchestrator walks
    at Approve to create the `defer-*` tasks. Stating the split only in the
    section the user reads produces a recommendation everyone agreed to and
    nothing carries — the same producer -> carrier -> silent-loss shape this
    module pins elsewhere.
    """
    paragraph = scope_split_paragraph()
    assert (
        f"**mirror the same recommendation as a `{DEFERRED_REFINEMENTS_HEADING}` "
        "bullet**" in paragraph
    ), (
        "agents/analyst.md: the scope-split rule no longer mirrors the "
        f"recommendation into `{DEFERRED_REFINEMENTS_HEADING}`, so a split the "
        "user approves at the gate reaches no durable carrier"
    )
    assert (
        "because that block is what the orchestrator turns into a durable "
        "carrier" in paragraph
    ), (
        "agents/analyst.md: the scope-split rule lost the reason the mirror "
        "exists, leaving it readable as redundant restatement a later edit drops"
    )
    assert (
        "This section is what the user sees at the approval gate, so the "
        "recommendation belongs here" in paragraph
    ), (
        "agents/analyst.md: the scope-split rule no longer says why the "
        f"recommendation itself belongs in `{PRODUCER_HEADING}` — without it the "
        "two homes look interchangeable and one gets dropped"
    )


def test_scope_split_mirror_carries_a_destination_for_each_branch():
    """Each branch of the recommendation maps to a permitted destination.

    A mirrored bullet without a destination annotation is a contract violation
    the orchestrator surfaces as a malformed return, so the mapping has to be
    stated where the split is recommended. Both destinations are cross-checked
    against the `### Deferred refinements` contract itself: a mirror that names a
    destination that contract does not permit is rejected at consumption time.
    """
    paragraph = scope_split_paragraph()
    assert (
        "carrying the matching destination annotation — "
        f"`{SCOPE_SPLIT_DESTINATIONS[0]}` for fold-in, "
        f"`{SCOPE_SPLIT_DESTINATIONS[1]}` for the split" in paragraph
    ), (
        "agents/analyst.md: the scope-split rule no longer maps its two branches "
        f"onto {SCOPE_SPLIT_DESTINATIONS} — a mirrored bullet with no "
        "destination annotation cannot be reconciled into a `defer-*` task"
    )
    fence = contract_fence()
    for destination in SCOPE_SPLIT_DESTINATIONS:
        assert f"- **`{destination}`**" in fence, (
            f"agents/analyst.md: `{destination}` is no longer a permitted "
            f"`{DEFERRED_REFINEMENTS_HEADING}` destination, but the scope-split "
            "rule still tells the Analyst to mirror with it — the mirror now "
            "names a value its consumer rejects"
        )


def test_no_scope_split_is_issued_on_an_escalate_to_user_verdict():
    """No carrier, no recommendation — the concern rides `### Why` instead.

    On `escalate-to-user` the `### Deferred refinements` block is structurally
    `None`, so a scope-split stated in `### Blast radius` would have nowhere to
    mirror to. The carve-out folds the concern into the escalated open questions,
    which the escalation shape already carries to the user.
    """
    assert_deferrals_block_is_structurally_none_on_both_verdicts()
    paragraph = scope_split_paragraph()
    assert (
        "On `escalate-to-user`, do **not** issue a scope-split recommendation as "
        "such" in paragraph
    ), (
        "agents/analyst.md: the scope-split rule no longer excepts "
        "`escalate-to-user`, so it now licenses a recommendation on the one "
        f"verdict whose `{DEFERRED_REFINEMENTS_HEADING}` block is structurally "
        "`None`"
    )
    assert (
        f"`{DEFERRED_REFINEMENTS_HEADING}` stays structurally `None` per its own "
        "contract below, so a recommendation stated here would have no durable "
        "carrier at all" in paragraph
    ), (
        "agents/analyst.md: the `escalate-to-user` carve-out lost the reason it "
        "exists, which is also what ties it to the deferrals contract below"
    )
    assert (
        "Fold the distinct concern into the escalated open questions in "
        "`### Why` instead" in paragraph
    ), (
        "agents/analyst.md: the `escalate-to-user` carve-out no longer names "
        "`### Why` as where the distinct concern goes, so on that verdict the "
        "concern is now dropped rather than rerouted"
    )


def test_a_surfaced_scope_split_floors_the_converged_verdict():
    """A split makes the verdict at least `recommend-with-refinements`.

    The floor is what keeps the mirror reachable: on `recommend-as-stated` the
    `### Deferred refinements` block is structurally `None`, so a proposal that
    recommends a split under that verdict has, by its own contract, no bullet to
    mirror into.
    """
    assert_deferrals_block_is_structurally_none_on_both_verdicts()
    paragraph = scope_split_paragraph()
    assert (
        "A scope-split recommendation is itself a refinement, so on a "
        "**converged** verdict the verdict is at least "
        f"`{REFINEMENTS_VERDICT}`." in paragraph
    ), (
        "agents/analyst.md: the scope-split rule no longer floors a converged "
        f"verdict at `{REFINEMENTS_VERDICT}`, so a split can now be recommended "
        "under a verdict whose deferrals block is structurally `None`"
    )


def test_the_refinements_verdict_definition_names_the_scope_split_case():
    """The verdict ladder's own definition names the case and both carriers.

    An Analyst picking a verdict reads the ladder, not the sweep rule. A
    definition that lists only "refines the body's framing" gives a sweep-driven
    split no verdict to land on, and the floor asserted above becomes a rule
    stated only where the reader who needs it does not look.
    """
    paragraph = paragraph_with(AGENT_ANALYST, REFINEMENTS_VERDICT_ANCHOR)
    assert (
        "**or the sweep surfaced a distinct concern the Analyst recommends "
        "splitting out**" in paragraph
    ), (
        f"agents/analyst.md: the `{REFINEMENTS_VERDICT}` definition no longer "
        "names the scope-split case, so the verdict floor the sweep rule states "
        "has no matching rung in the ladder"
    )
    assert (
        f"and a scope-split additionally in `{PRODUCER_HEADING}` and "
        f"`{DEFERRED_REFINEMENTS_HEADING}`." in paragraph
    ), (
        f"agents/analyst.md: the `{REFINEMENTS_VERDICT}` definition no longer "
        "names both of the scope-split's carriers, so a reader following the "
        "ladder alone writes it in one place"
    )


def test_trivial_fix_short_circuit_defers_to_the_scope_split_rule():
    """A sweep that surfaces a distinct concern means the fix was not trivial.

    The trivial bullet pins the verdict at `recommend-as-stated`, whose deferrals
    block is structurally `None`. Without this clause the cheapest path is also
    the one that silently swallows a split — the Analyst has already committed to
    a verdict that cannot carry it.
    """
    assert_deferrals_block_is_structurally_none_on_both_verdicts()
    block = section_block(AGENT_ANALYST, "## Short-circuit conditions")
    assert (
        "if the sweep does surface a distinct concern to split out, the fix was "
        "not trivial after all — the scope-split rule applies and the verdict is "
        f"at least `{REFINEMENTS_VERDICT}`" in block
    ), (
        "agents/analyst.md: the trivial-fix short-circuit no longer defers to "
        "the scope-split rule, so a trivial fix that surfaces a distinct concern "
        "keeps a verdict whose deferrals block cannot carry it"
    )


def test_surfacing_paragraph_keeps_both_sections_user_facing():
    """The premise the two gate-ratification tests argue from.

    A preamble that names a policy count, and an Approve whose text says approval
    covers the policy answers and the scope split, are both worthless if the
    sections carrying them never reach the user. Section 3's surfacing paragraph
    is the only site that decides this, and it decides it as a *contrast* —
    `### Deferred refinements` is withheld from the same proposal — so the rule
    cannot be inferred from anything else in the file.

    `test_fixed_empty_lines_are_byte_identical_at_every_site` only counts the two
    fixed lines, so it catches an outright deletion of this sentence but passes a
    reword that keeps both lines quoted while dropping the obligation they hang
    off. Hence the two clauses below: the sections ARE surfaced, and they are
    surfaced *in full* — an abridged surfacing that drops the empty line puts the
    user back to guessing "swept and found nothing" from "never swept".
    """
    paragraph = paragraph_with(QUO_FIX_ISSUE, SURFACING_PARAGRAPH_ANCHOR)
    assert (
        f"**Unlike `{DEFERRED_REFINEMENTS_HEADING}`, the `{PRODUCER_HEADING}` "
        f"and `{POLICY_HEADING}` sections ARE surfaced**" in paragraph
    ), (
        "/quo-fix-issue: Section 3's surfacing paragraph no longer states that "
        f"`{PRODUCER_HEADING}` and `{POLICY_HEADING}` are surfaced to the user "
        f"unlike `{DEFERRED_REFINEMENTS_HEADING}` — the gate preamble and the "
        "Approve option now ratify sections nothing requires the user to be shown"
    )
    assert (
        "surface both in full, including their fixed empty lines "
        f"(`{BLAST_RADIUS_EMPTY_LINE}` / `{POLICY_EMPTY_LINE}`) when the "
        "Analyst emitted those" in paragraph
    ), (
        "/quo-fix-issue: Section 3's surfacing paragraph no longer requires "
        "surfacing both sections in full including their fixed empty lines, so "
        "an empty section may be abridged away and the user can no longer tell "
        '"swept and found nothing" from "never swept"'
    )


def test_gate_preamble_names_the_policy_count_and_the_scope_split():
    """The preamble tells the user what the Approve below actually ratifies.

    Both sections are surfaced in full, so the preamble's job is not to restate
    them but to say they are there and that Approve covers them. Naming **how
    many** policy decisions is the part that cannot be satisfied by a vague
    gesture: a count is either right or wrong, and getting it means reading the
    section.
    """
    paragraph = paragraph_with(QUO_FIX_ISSUE, GATE_PREAMBLE_ANCHOR)
    assert (
        "the preamble MUST name **how many** decisions it carries and point at "
        "the section" in paragraph
    ), (
        "/quo-fix-issue: the Section 3 preamble no longer names how many policy "
        "decisions it carries, so the user can approve a ratification whose size "
        "was never stated"
    )
    assert (
        "so the user knows Approve ratifies the Analyst's recommended answers "
        "along with the design" in paragraph
    ), (
        "/quo-fix-issue: the Section 3 preamble no longer says Approve ratifies "
        "the recommended policy answers along with the design"
    )
    assert (
        f"when the Analyst's `{PRODUCER_HEADING}` carries a **scope-split "
        "recommendation**" in paragraph
    ), (
        "/quo-fix-issue: the Section 3 preamble no longer covers the scope-split "
        f"case, so a split carried in `{PRODUCER_HEADING}` is surfaced with no "
        "signal that Approve decides it"
    )
    assert (
        "the preamble says one is carried and points at that section" in paragraph
    ), (
        "/quo-fix-issue: the Section 3 preamble no longer points at the section "
        "carrying the scope-split recommendation"
    )


def test_gate_preamble_adds_no_second_gate_option_or_task():
    """Both ratifications ride the existing gate — no new machinery.

    A second gate would ask the user to decide the same proposal twice, and an
    extra option or a separate task would need its own close-out sweep. This is
    the same no-new-machinery constraint the design-question rung carries, and it
    is asserted here for the same reason: it is cheap to violate by addition.
    """
    paragraph = paragraph_with(QUO_FIX_ISSUE, GATE_PREAMBLE_ANCHOR)
    assert (
        "Both ride this existing preamble paragraph and the existing Approve / "
        "Revise / Cancel gate below" in paragraph
    ), (
        "/quo-fix-issue: the policy decisions and the scope-split no longer ride "
        "the existing preamble and gate, so they may now be given surfaces of "
        "their own"
    )
    assert (
        "do **not** add a second gate, an extra option, or a separate task for "
        "them" in paragraph
    ), (
        "/quo-fix-issue: the Section 3 preamble no longer forbids a second gate, "
        "an extra option, or a separate task for the ratifications it carries"
    )


def test_approve_option_says_approval_covers_the_scope_split():
    """The option text is the user's record of what they agreed to.

    The preamble frames the proposal, but the option is what the user clicks, and
    an Approve whose text mentions only "the Recommended approach" gives the
    orchestrator no license to create a `defer-*` task from a split the user
    never saw themselves agreeing to.
    """
    paragraph = paragraph_with(QUO_FIX_ISSUE, APPROVE_OPTION_ANCHOR)
    assert (
        "Approval covers the design, the Analyst's recommended answer to every "
        f"question in `{POLICY_HEADING}`, and any scope-split recommendation "
        f"carried in `{PRODUCER_HEADING}`." in paragraph
    ), (
        "/quo-fix-issue: Section 3's Approve option no longer states that "
        "approval covers the design, the recommended policy answers, and any "
        "scope-split recommendation — the three things this gate ratifies in one "
        "decision"
    )
