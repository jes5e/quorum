"""Lane-ordering and routing-input invariants shared by the two orchestrators.

Regression test for Issue b.pdq. The Issue sequenced the lanes so that source
reaches a review-clean state *before* the writers read it — Engineer and Code
Reviewer loop to clean, then Test Writer and Doc Writer run once in parallel,
then the remaining reviewers and the PM — and mirrored the same ordering into
the re-dispatch path as part **(g)** of `### Orchestrator discipline: routing
review findings` in BOTH `/quo-fix-issue` and `/quo-execute`.

Two failure modes this pins:

  1. **Part (g) going missing from one skill.** The ordering was mirrored into
     `/quo-execute` precisely because a one-sided fix leaves the peer skill
     handing writers a diff a pending code review is about to rewrite. The two
     skills are edited independently and drift silently.

  2. **`metadata.activity` becoming a routing input.** Both skills state that
     the string is informational only. An earlier revision of this Issue's fix
     carried an "aborted-writer exemption" that keyed an Engineer-dispatch
     decision on that annotation; it was replaced by the structural argument
     that `aborted-` is a *distinct name class* and so needs no exemption at
     all. Re-keying dispatch on an informational string is the regression.
"""

import re

from conftest import (
    AGENT_DOC_WRITER,
    AGENT_TEST_WRITER,
    QUO_EXECUTE,
    QUO_FIX_ISSUE,
    read,
    routing_section,
)

ORCHESTRATORS = (
    QUO_FIX_ISSUE,
    QUO_EXECUTE,
)

PART_G_MARKER = "**(g) Re-dispatch ordering when a fix path changes source.**"

# Stable phrases from part (g)'s lead and its ordering rule. Both skills carry
# these byte-identically even though the middle of the sentence differs
# (`/quo-execute` names two code-review sites, `/quo-fix-issue` one).
#
# The first entry is part (g)'s back-reference to where a finding's routing gets
# settled. It names **both** origins — the orchestrator's own path pick under
# part (a) *and* the user's pick at gate (c)/(d). The retired wording said
# "auto-dispatch per part (a)", which mislabels part (a) as an automatic
# dispatch rather than a decision the orchestrator makes; pinning the trailing
# "or the user's pick..." half alone would not catch a revert, because that half
# is common to both wordings. The bold markers are included: they are part of
# the byte-identical text, and the surrounding entries quote their emphasis
# markers the same way.
ORDERING_PHRASES = (
    "**the orchestrator's own path pick per part (a), or the user's pick at "
    "the gate in part (c) or (d)**",
    "are **ordered, not concurrent**",
    "dispatch the **Engineer** first",
    "only once that code review has closed dispatch the **Test Writer** and/or "
    "**Doc Writer**",
    "Dispatching the Engineer and a writer in the same round hands the writer a "
    "diff that the pending code review is about to rewrite",
)

METADATA_INFORMATIONAL = (
    "it is informational, not a routing input"
)

# An Engineer-dispatch precondition sentence. These are the sentences that
# decide whether an Engineer may be dispatched; none of them may consult
# `metadata.activity`.
DISPATCH_PRECONDITION = re.compile(r"MUST NOT (?:re-)?dispatch an .{0,60}?Engineer", re.I)

# Each orchestrator carries three such sentences today. The floor is a count,
# not merely "at least one": a bare truthiness check let two of the three be
# reworded out of the regex's reach with the guard still scanning — and passing
# — over the single survivor. Raise this if a skill legitimately gains a fourth.
EXPECTED_PRECONDITIONS = 3

# A line that mentions both the annotation and an exemption must be *denying*
# that an exemption exists. These are the negating cues the current prose uses.
EXEMPTION_DENIAL = re.compile(r"(no exemption|without needing an exemption)", re.I)

# --- Writer-dispatch wording -------------------------------------------------

WRITER_DISPATCH_LEAD = (
    "**Test Writer / Doc Writer dispatch — state the orchestrator-side rule, "
    "never a freeze guarantee.**"
)
FREEZE_PHRASE = "the source tree is frozen"

WRITER_ROLE_FILES = (AGENT_TEST_WRITER, AGENT_DOC_WRITER)

# Per orchestrator: the keepable claim(s) its writer dispatch prompts MAY state,
# each paired with the wording in BOTH writer role files that the claim has to
# line up with.
#
# The two modes corroborate differently on purpose. Fix mode's role-side branch
# restates the claim verbatim, so the claim is its own corroborator and the pair
# is a literal cross-file equality. Execute mode's role-side branch deliberately
# does *not* restate the skill's wording — it scopes the guarantee in its own
# words — so each execute-mode claim is instead paired with the role-side clause
# that makes that particular scope the correct one: the Subtask-scoped claim
# cannot widen past the Subtask because siblings may run concurrently, and the
# Bee-scoped claim only becomes available on the whole-Bee dispatch. Delete
# either clause from the role files and the skill is quoting a scope its writers
# no longer expect.
KEEPABLE_CLAIMS = {
    QUO_FIX_ISSUE: (
        (
            "no Engineer Agent will be dispatched for this Issue while you are "
            "running",
            "no Engineer Agent will be dispatched for this Issue while you are "
            "running",
        ),
    ),
    QUO_EXECUTE: (
        (
            "no Engineer Agent will be dispatched for your Subtask's "
            "implementation dependency while you are running",
            "an Engineer working a **sibling Subtask** may legitimately be "
            "running concurrently",
        ),
        (
            "no Engineer Agent will be dispatched for this Bee while you are "
            "running",
            "When the dispatch prompt scopes you to the whole Bee rather than "
            "to a Subtask",
        ),
    ),
}


def writer_dispatch_paragraph(relpath):
    """The single line carrying an orchestrator's writer-dispatch wording rule."""
    matched = [
        line for line in read(relpath).splitlines() if WRITER_DISPATCH_LEAD in line
    ]
    assert len(matched) == 1, (
        f"{relpath}: expected exactly one paragraph led by "
        f"{WRITER_DISPATCH_LEAD!r}, found {len(matched)} — the rule was reworded "
        "or dropped, and the assertions below would pass vacuously"
    )
    return matched[0]


def precondition_lines(relpath):
    """`(line_no, line)` for every Engineer-dispatch precondition in a skill."""
    return [
        (line_no, line)
        for line_no, line in enumerate(read(relpath).splitlines(), start=1)
        if DISPATCH_PRECONDITION.search(line)
    ]


def test_both_orchestrators_carry_part_g():
    """Part (g) exists in both skills' routing-findings section."""
    for relpath in ORCHESTRATORS:
        section = routing_section(read(relpath))
        assert PART_G_MARKER in section, (
            f"{relpath}: `### Orchestrator discipline: routing review findings` "
            "has no part **(g)** — the re-dispatch ordering rule"
        )


def test_part_g_names_the_engineer_then_review_then_writer_ordering():
    """Part (g) states the Engineer -> code review -> writer ordering.

    Also pins part (g)'s lead back-reference to the two places a finding's
    routing gets settled, which is the precondition the ordering rule attaches
    to: the orchestrator's own path pick under part (a), or the user's pick at
    gate (c)/(d).
    """
    for relpath in ORCHESTRATORS:
        section = routing_section(read(relpath))
        part_g = section[section.index(PART_G_MARKER):]
        for phrase in ORDERING_PHRASES:
            assert phrase in part_g, (
                f"{relpath}: part (g) no longer states {phrase!r}"
            )


def test_part_g_is_lettered_in_sequence():
    """(g) follows (f) — the section's parts stay a single lettered run.

    A part (g) appended without (f) present would mean the section was
    restructured underneath it, and the cross-references to "part (g)" that both
    skills carry elsewhere would point at nothing.
    """
    for relpath in ORCHESTRATORS:
        section = routing_section(read(relpath))
        letters = re.findall(r"\*\*\((?P<letter>[a-z])\)", section)
        assert letters[:7] == list("abcdefg"), (
            f"{relpath}: routing-findings parts are {letters[:7]}, expected a..g"
        )


def test_fix_issue_defines_the_three_phase_ladder():
    """`/quo-fix-issue`'s Reconcile step sequences the lanes into A / B / C.

    Phase B is the load-bearing one: the writers are dispatched **once**, in
    parallel, and only after the source half of the diff is review-clean. If
    Phase B stops being the sole forward dispatch site for those two roles, a
    writer can again be handed a diff a pending code review is about to rewrite.
    """
    text = read(QUO_FIX_ISSUE)
    for phase in (
        "**Phase A — source to clean.**",
        "**Phase B — writers once, in parallel.**",
        "**Phase C — remaining reviewers plus PM.**",
    ):
        assert phase in text, f"/quo-fix-issue: {phase} is missing from Section 4"
    assert text.index("**Phase A — source to clean.**") < text.index(
        "**Phase B — writers once, in parallel.**"
    ) < text.index("**Phase C — remaining reviewers plus PM.**"), (
        "the phases are no longer in ladder order"
    )
    assert (
        "This is the **only** place these two roles are dispatched on the "
        "forward path" in text
    ), "Phase B is no longer declared the sole forward writer-dispatch site"
    assert "The Code Reviewer is NOT dispatched again here" in text, (
        "Phase C no longer excludes the Code Reviewer, which ran to closure in "
        "Phase A"
    )


def test_phase_c_and_task_advance_are_gated_on_no_pending_abort_marker():
    """A `pending` `aborted-*` marker holds the next stage shut in both skills.

    The marker is the owed-redelivery signal a writer's movement abort leaves
    behind; advancing past it dispatches a reviewer over a half-written test or
    doc set.
    """
    fix_gate = "and no `aborted-*` TaskList task for this Issue is `pending`"
    execute_gate = "and no `aborted-*` TaskList task for this Task is `pending`"
    fix_text = read(QUO_FIX_ISSUE)
    execute_text = read(QUO_EXECUTE)
    assert fix_text.count(fix_gate) >= 2, (
        "/quo-fix-issue: the Phase C entry condition must be stated at both its "
        "Section 4 and Section 5 sites"
    )
    assert execute_text.count(execute_gate) >= 2, (
        "/quo-execute: the per-Task advance gate must be stated at both its "
        "Reconcile-step and per-Task-PM-dispatch sites"
    )


def test_metadata_activity_is_declared_informational_in_both_skills():
    """Both skills state the annotation is not a routing input."""
    for relpath in ORCHESTRATORS:
        assert METADATA_INFORMATIONAL in read(relpath), (
            f"{relpath}: the `metadata.activity` informational-only statement is "
            "missing or reworded"
        )


def test_no_engineer_dispatch_precondition_consults_metadata_activity():
    """No Engineer-dispatch precondition sentence mentions `metadata.activity`.

    The precondition is a TaskList *name prefix plus status* test by design —
    derivable from state, so it survives a compaction. Folding an annotation
    into it makes the decision depend on a string the orchestrator writes
    opportunistically.

    The scan is **line-scoped**: it sees an annotation folded into a
    precondition sentence, not a routing dependency stated in a separate
    sentence nearby. `test_aborted_marker_needs_no_dispatch_exemption` covers
    part of that gap by requiring every exemption-shaped line to be a denial.

    The non-vacuity assertion below is load-bearing, and it is a *count* floor
    rather than a truthiness check. Rewording the preconditions so
    `DISPATCH_PRECONDITION` matches nothing would leave this guard passing over
    an empty set; rewording all but one of them would leave it passing over a
    set too small to be the contract, which reads identically from the outside.
    """
    offenders = []
    for relpath in ORCHESTRATORS:
        matched = precondition_lines(relpath)
        assert len(matched) >= EXPECTED_PRECONDITIONS, (
            f"{relpath}: only {len(matched)} Engineer-dispatch precondition "
            f"sentence(s) matched {DISPATCH_PRECONDITION.pattern!r}, expected at "
            f"least {EXPECTED_PRECONDITIONS} — the prose was reworded and this "
            "guard would otherwise pass over a shrunken set. Today each "
            "orchestrator carries three."
        )
        offenders.extend(
            f"{relpath}:{line_no}"
            for line_no, line in matched
            if "metadata.activity" in line
        )
    assert not offenders, (
        "Engineer-dispatch precondition(s) now consult `metadata.activity`, "
        "which is informational and never a routing input: " + ", ".join(offenders)
    )


def test_aborted_marker_needs_no_dispatch_exemption():
    """`aborted-` is kept out of the precondition structurally, not by exemption.

    Every line that mentions both `metadata.activity` and an exemption must be
    *denying* that one exists — the pre-fix shape was an aborted-writer
    exemption keyed on that annotation.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        assert "**distinct name class**" in text, (
            f"{relpath}: the structural argument that `aborted-` is a distinct "
            "name class is gone; an exemption clause is the likely replacement"
        )
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "metadata.activity" in line and "exempt" in line:
                assert EXEMPTION_DENIAL.search(line), (
                    f"{relpath}:{line_no}: an exemption appears to be keyed on "
                    "`metadata.activity` rather than denied"
                )


def test_writer_dispatch_states_a_keepable_rule_not_a_freeze():
    """Both orchestrators allow the orchestrator-side rule and forbid the freeze.

    An orchestrator controls only its own dispatches, so a claim scoped to those
    dispatches is keepable and "the source tree is frozen" is not — the latter
    promises a lever over the user, a second session, and any background process
    that no orchestrator holds.

    What is keepable differs by mode, which is why the claims are tabled rather
    than shared. `/quo-fix-issue` runs one implementation pass per Issue, so it
    may promise the whole Issue. `/quo-execute` fans Subtasks out concurrently,
    so it may promise only the writer's own Subtask — except on the Bee-scoped
    re-dispatch, where every Subtask is finished and the promise widens to the
    Bee. Each claim is checked against the wording the writer role files carry
    for that mode (see `KEEPABLE_CLAIMS`); a skill quoting a scope its writers
    do not expect is the drift this catches.
    """
    for relpath in ORCHESTRATORS:
        text = read(relpath)
        paragraph = writer_dispatch_paragraph(relpath)

        for claim, corroborator in KEEPABLE_CLAIMS[relpath]:
            assert f'**"{claim}"**' in paragraph, (
                f"{relpath}: the keepable orchestrator-side rule {claim!r} is no "
                "longer quoted in the writer-dispatch paragraph"
            )
            for role_file in WRITER_ROLE_FILES:
                assert corroborator in read(role_file), (
                    f"{role_file}: no longer carries {corroborator!r}, so the "
                    f"claim {claim!r} that {relpath} tells its dispatch prompts "
                    "to state is scoped to a guarantee the writer role no longer "
                    "describes"
                )

        assert FREEZE_PHRASE in paragraph, (
            f"{relpath}: the forbidden freeze-guarantee phrasing is no longer "
            "quoted in the writer-dispatch paragraph, so the prohibition cannot "
            "be stated"
        )
        assert "MUST NOT" in paragraph, (
            f"{relpath}: the writer-dispatch paragraph no longer forbids the "
            "freeze guarantee — it names the phrasing without prohibiting it"
        )
        for role_file in WRITER_ROLE_FILES:
            assert f"`{role_file}`" in paragraph, (
                f"{relpath}: the writer-dispatch paragraph no longer points at "
                f"`{role_file}`, which carries the writer-side half the rule "
                "relies on"
            )

        for line_no, line in enumerate(text.splitlines(), start=1):
            if FREEZE_PHRASE in line:
                assert "MUST NOT" in line, (
                    f"{relpath}:{line_no}: {FREEZE_PHRASE!r} appears outside a "
                    "prohibition"
                )
