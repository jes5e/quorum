"""The `### Second-order effects` producer -> relayers -> destinations chain.

Regression test for Issue b.pdq. The Issue added a **required** second-order
effects subsection to `/quo-engineer-review`: a new Step 2 check category (#8)
that asks what a change newly exposes rather than only whether it is correct,
plus an unconditional subsection in the skill's emission contract that carries
the answer downstream.

"Unconditional" is the whole point and also the fragile part. A section emitted
only when the reviewer had something to say degrades into one nobody can rely on
being asked for — so the heading has to be present in **both** worked emission
shapes, including the clean one (`No code issues found.`), where the temptation
to drop it is greatest.

But an unconditionally-emitted subsection with nowhere to land is just as dead
as one that is never emitted, so this module pins the **whole chain**, in the
producer -> carriers -> consumer shape `test_writer_role_contracts.py` uses for
the completeness-evidence relay:

  * **Producer** — `/quo-engineer-review` (the emission contract, category #8,
    and both worked emission shapes).
  * **Relayers** — `agents/code-reviewer.md` and `agents/pm.md`, which forward
    the subsection's *body* (never its heading line, which would land inside the
    destination field) into their returns. `agents/pm.md` additionally owes the
    Final report shape the orchestrators parse: exactly one `### Second-order
    effects` section with one `#### <invocation scope>` sub-block per in-flight
    invocation.
  * **Destinations** — the three `**Second-order effects**` summary fields:
    `/quo-fix-issue` Section 7's per-issue summary, `/quo-execute` Section 4.1's
    per-Task summary, and `/quo-execute` Section 9's `## Bee Execution Complete`
    block. Deleting any one of them strands every relay aimed at it.

Pinning only the producer half was the earlier defect: the relay bullets and the
destination fields could each be deleted with the suite still green.
"""

import re
from collections import Counter

from conftest import (
    AGENT_CODE_REVIEWER,
    AGENT_PM,
    QUO_ENGINEER_REVIEW,
    QUO_EXECUTE,
    QUO_FIX_ISSUE,
    read,
)

SUBSECTION_HEADING = "### Second-order effects"
CLEAN_FINDINGS_LINE = "No code issues found."
CLEAN_EFFECTS_LINE = "No second-order effects identified."
TRAILER_PREFIX = "**Your next tool use MUST"

# The rendered summary field the relayed body lands in.
SUMMARY_FIELD = "**Second-order effects**:"

# The relay's no-heading rule. Byte-identical in both role files on purpose: the
# orchestrator renders the relayed body straight into a one-line summary field,
# so a heading line that rides along lands *inside* the field. A site that keeps
# the relay but drops this clause produces a malformed summary.
NO_HEADING_RULE = (
    "Relay the subsection's **body** verbatim; do **not** re-emit the "
    "`### Second-order effects` heading line that came with it"
)

# The three `**Second-order effects**` destination fields, each identified by the
# title line of the summary template it lives in.
DESTINATIONS = {
    "/quo-fix-issue Section 7 per-issue summary": (
        QUO_FIX_ISSUE,
        "## Issue [x] of [total] done: [issue-title]",
    ),
    "/quo-execute Section 4.1 per-Task summary": (
        QUO_EXECUTE,
        "## Task [N] of [total] Complete: [task-title]",
    ),
    "/quo-execute Section 9 Bee Execution Complete": (
        QUO_EXECUTE,
        "## Bee Execution Complete: [bee-title]",
    ),
}

# The sentence that defines category #8. Pinned verbatim because it is the
# forward question the category exists to force — "is it correct?" is category
# #7's job, and a reviewer that answers only that pushes the consequence into
# the next round.
CATEGORY_8_SENTENCE = (
    "state what it newly exposes, weakens, or can now fail"
)

FENCE = re.compile(r"```markdown\n(.*?)\n```", re.S)


def review_text():
    return read(QUO_ENGINEER_REVIEW)


def emission_shape(text, shape_marker):
    """The first ```markdown fenced block after `shape_marker`."""
    idx = text.index(shape_marker)
    match = FENCE.search(text, idx)
    assert match, f"no fenced markdown block follows {shape_marker!r}"
    return match.group(1)


def summary_template(text, title_line):
    """The summary template beginning at `title_line`, up to its closing fence.

    Scanned line-wise rather than by pairing ``` fences: these skills nest
    fenced blocks inside fenced blocks, so a regex that pairs delimiters
    mis-associates them.
    """
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == title_line]
    assert len(starts) == 1, (
        f"expected exactly one summary-template title line {title_line!r}, "
        f"found {len(starts)}"
    )
    start = starts[0]
    for j in range(start + 1, len(lines)):
        if lines[j].rstrip() == "```":
            return "\n".join(lines[start:j])
    raise AssertionError(
        f"summary template {title_line!r} has no closing fence"
    )


# --------------------------------------------------------------------------
# Producer — `/quo-engineer-review`
# --------------------------------------------------------------------------


def test_check_category_8_exists_with_its_defining_sentence():
    """Step 2 carries a `#### 8. Second-Order Effects` category.

    Without the category, the emission contract below asks for a section the
    review process never actually performed.
    """
    text = review_text()
    assert "#### 8. Second-Order Effects" in text, (
        "check category #8 (Second-Order Effects) is missing from Step 2"
    )
    assert CATEGORY_8_SENTENCE in text, (
        "category #8 no longer carries its defining sentence: "
        f"{CATEGORY_8_SENTENCE!r}"
    )


def test_category_8_applies_to_markdown_skill_source():
    """#8 is in the *apply* list for markdown skill / subagent program source.

    That selective list is what makes the category reach this repo's own
    reviews, where the "source" is skill prose rather than a compiled language.
    """
    text = review_text()
    selectivity_line = next(
        line for line in text.splitlines()
        if "**Apply** these categories" in line
    )
    apply_half, _, skip_half = selectivity_line.partition("**Skip**")
    assert "#8 Second-Order Effects" in apply_half, (
        "category #8 is not in the apply-list for markdown skill program source"
    )
    assert skip_half, "the selectivity sentence lost its **Skip** half"
    assert "#8" not in skip_half, (
        "category #8 must not be listed among the skipped categories"
    )


def test_emission_contract_declares_the_subsection_unconditional():
    """The contract states the heading is emitted on every review."""
    text = review_text()
    assert "**Required `### Second-order effects` subsection.**" in text
    assert "emit the heading on every review, including clean ones" in text, (
        "the unconditional-emission rule is missing or reworded"
    )
    assert f"`{CLEAN_EFFECTS_LINE}`" in text, (
        "the fixed empty-case line is no longer named in the contract"
    )


def test_subsection_present_in_shape_1_findings_present():
    """Shape 1 carries the subsection between the findings list and the trailer."""
    block = emission_shape(review_text(), "**Shape 1 — Findings present**")
    assert SUBSECTION_HEADING in block, (
        "Shape 1's worked emission dropped the `### Second-order effects` heading"
    )
    heading_at = block.index(SUBSECTION_HEADING)
    last_finding = max(
        block.index(line) for line in block.splitlines()
        if re.match(r"^\d+\. `", line)
    )
    trailer_at = block.index(TRAILER_PREFIX)
    assert last_finding < heading_at < trailer_at, (
        "Shape 1's subsection must sit after the numbered work-item list and "
        "immediately above the routing trailer"
    )


def test_subsection_present_in_shape_2_clean_review():
    """Shape 2 — the clean review — carries the subsection too.

    This is the case the contract exists to protect: a reviewer with no findings
    must still emit the heading, with the fixed empty line under it.
    """
    block = emission_shape(review_text(), "**Shape 2 — No findings**")
    assert CLEAN_FINDINGS_LINE in block, "Shape 2 lost its clean work-item line"
    assert SUBSECTION_HEADING in block, (
        "Shape 2's clean emission dropped the `### Second-order effects` heading "
        "— the exact regression the unconditional rule forbids"
    )
    assert CLEAN_EFFECTS_LINE in block, (
        "Shape 2 no longer shows the fixed empty-case line under the heading"
    )
    assert (
        block.index(CLEAN_FINDINGS_LINE)
        < block.index(SUBSECTION_HEADING)
        < block.index(CLEAN_EFFECTS_LINE)
        < block.index(TRAILER_PREFIX)
    ), "Shape 2's subsection is out of contract order"


def test_clean_review_may_still_carry_effects_bullets():
    """`No code issues found.` and the effects bullets are independent.

    Collapsing the two would make the subsection conditional on findings by the
    back door — a clean review that exposes something worth recording must still
    be able to say so.
    """
    text = review_text()
    assert (
        "Shape 2's `No second-order effects identified.` line is the empty case, "
        "not the only case." in text
    ), "the independence of the two clean-shape lines is no longer stated"


def test_subsection_is_narrative_not_a_routing_surface():
    """Actionable effects must also appear as numbered, tagged findings.

    The orchestrators' routing table parses `(num-paths, max-depth)` from the
    numbered list and from nothing else, so an actionable effect that lives only
    in the narrative is invisible to routing.
    """
    text = review_text()
    assert "The numbered list remains the **sole** routing surface" in text
    assert "**Compatibility constraint — the subsection is narrative, not a routing surface.**" in text


# --------------------------------------------------------------------------
# Relayers — `agents/code-reviewer.md` and `agents/pm.md`
# --------------------------------------------------------------------------


def test_both_relayers_carry_the_relay_instruction():
    """Each role file that wraps `/quo-engineer-review` relays the subsection.

    These two are the only carriers between the producer and the summary
    fields. A role file that keeps the review invocation but loses the relay
    bullet terminates the narrative in its own return, which is exactly the
    "reaches the orchestrator and stops there" failure the destinations exist
    to prevent.
    """
    for relpath in (AGENT_CODE_REVIEWER, AGENT_PM):
        text = read(relpath)
        assert SUBSECTION_HEADING in text, (
            f"{relpath}: no longer names the `{SUBSECTION_HEADING}` subsection "
            "it is supposed to relay"
        )
        assert "verbatim" in text and SUMMARY_FIELD.rstrip(":") in text, (
            f"{relpath}: the verbatim-relay instruction or its named "
            f"`{SUMMARY_FIELD.rstrip(':')}` destination is gone"
        )
        assert "narrative rather than routing input" in text, (
            f"{relpath}: lost the narrative-not-routing-input qualifier, which "
            "is what forbids folding the subsection into the findings list"
        )
        assert "drop it when it reads as clean" in text, (
            f"{relpath}: no longer forbids dropping the subsection on a clean "
            "review — the case the unconditional-emission rule exists for"
        )


def test_no_heading_rule_is_byte_identical_in_both_relayers():
    """Both relayers forward the body and suppress the heading line, identically.

    The rule is stated in the same words at both sites because both bodies land
    in the same one-line `**Second-order effects**` field; a relayed heading
    line lands *inside* that field. Divergence here is how one lane starts
    emitting a malformed summary while the other reads as correct.
    """
    for relpath in (AGENT_CODE_REVIEWER, AGENT_PM):
        assert NO_HEADING_RULE in read(relpath), (
            f"{relpath}: the relay-the-body/not-the-heading rule is missing or "
            "reworded — it must stay byte-identical at both relay sites"
        )


def test_pm_final_report_declares_exactly_one_section_with_labelled_sub_blocks():
    """`agents/pm.md` owes one section, one labelled sub-block per invocation.

    A PM pass can make several in-flight `/quo-engineer-review` invocations. The
    orchestrators collect "each `#### <invocation scope>` sub-block" under a
    single heading; N repeats of the `### Second-order effects` heading, or
    unlabelled bodies, make the section unparseable at the destination.
    """
    text = read(AGENT_PM)
    assert f"**Exactly one** `{SUBSECTION_HEADING}` section" in text, (
        "agents/pm.md: the exactly-one-section rule for the Final report is gone"
    )
    assert "one labelled sub-block per invocation" in text, (
        "agents/pm.md: the one-sub-block-per-invocation rule is gone"
    )
    assert "`#### <invocation scope>`" in text, (
        "agents/pm.md: the sub-block heading shape the orchestrators collect on "
        "is no longer named"
    )
    assert "Do not nest a second `### Second-order effects` heading inside a sub-block" in text, (
        "agents/pm.md: the no-nested-heading rule is gone"
    )
    assert "say so under the heading rather than omitting it" in text, (
        "agents/pm.md: the no-invocations-this-pass case may now omit the "
        "section, making it conditional by the back door"
    )


# --------------------------------------------------------------------------
# Destinations — the three `**Second-order effects**` summary fields
# --------------------------------------------------------------------------


def test_every_summary_template_carries_the_destination_field():
    """All three rendered summary templates carry the field the relays aim at.

    Deleting the field from a template does not break any relay loudly — the
    narrative simply stops at the orchestrator. That silence is why the field
    is pinned inside its fenced template rather than merely somewhere in the
    file.
    """
    for label, (relpath, title_line) in DESTINATIONS.items():
        block = summary_template(read(relpath), title_line)
        assert SUMMARY_FIELD in block, (
            f"{label} ({relpath}): the summary template no longer carries a "
            f"`{SUMMARY_FIELD}` field, so the relayed narrative has nowhere to land"
        )
        assert SUBSECTION_HEADING in block, (
            f"{label} ({relpath}): the field no longer names the "
            f"`{SUBSECTION_HEADING}` narrative it renders"
        )


def test_every_destination_field_has_rendering_logic_declaring_it_unconditional():
    """Each field is backed by rendering logic, and none of them may be omitted.

    `**Accepted compromises**` is the conditional field in these same templates;
    this one is not, and each site says so in its own words. A field rendered
    only when there was something to say degrades into one nobody can rely on.

    Asserted as **occurrence counts, not containment**. `/quo-execute` owns two
    of the three destinations, so a whole-file `in` test let both of its
    DESTINATIONS entries be satisfied by the *same* rendering block: deleting or
    renaming one of the two left the other answering for both, and the suite
    stayed green. Requiring one occurrence per entry ties each destination to
    rendering logic of its own.
    """
    expected = Counter(relpath for relpath, _ in DESTINATIONS.values())
    pinned = {
        "the field's rendering logic block": (
            "**Second-order effects (rendered into the summary block above).**"
        ),
        f"the producer's fixed empty line `{CLEAN_EFFECTS_LINE}`": (
            f"(`{CLEAN_EFFECTS_LINE}`)"
        ),
        "the `None identified.` empty case": (
            "render the single line `None identified.` — do **not** omit the field"
        ),
    }
    labels = {
        relpath: sorted(
            label for label, (dest, _) in DESTINATIONS.items() if dest == relpath
        )
        for relpath in expected
    }
    for relpath, count in expected.items():
        text = read(relpath)
        for description, needle in pinned.items():
            assert text.count(needle) == count, (
                f"{relpath}: expected {count} occurrence(s) of {description} — "
                f"one per destination in this file ({', '.join(labels[relpath])}) "
                f"— found {text.count(needle)}. Each destination field needs its "
                "own rendering logic; a shared one leaves the other destination "
                "unpinned."
            )


def test_execute_keeps_its_two_destinations_distinct():
    """`/quo-execute`'s per-Task and Bee-level fields are not interchangeable.

    Per-Task summaries are printed as each Task closes, so a Bee-level narrative
    routed there would be aimed at output the run has already emitted. The skill
    states the split at both ends; collapsing it silently loses the Bee-level
    narrative.
    """
    text = read(QUO_EXECUTE)
    assert (
        "The **Bee-level** review in Section 5 has its own destination" in text
    ), "/quo-execute Section 4.1 no longer disclaims the Bee-level narrative"
    assert "Do **not** route it into Section 4.1's per-Task field" in text, (
        "/quo-execute's Bee-level review site no longer forbids routing its "
        "narrative into the already-printed per-Task field"
    )
    bee_block = summary_template(text, "## Bee Execution Complete: [bee-title]")
    assert "from the Bee-level review" in bee_block, (
        "/quo-execute Section 9's field no longer scopes itself to the "
        "Bee-level review's narrative"
    )
