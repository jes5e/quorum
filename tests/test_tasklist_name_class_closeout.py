"""TaskList name-class create/close-out guard for the two orchestrator skills.

Regression test for Issue b.pdq. Across nine review rounds on that Issue the most
frequently recurring defect was a **TaskList name class that is created in one
section but never closed out in another** — or the mirror image, a close-out
sweep silently narrowed so that a class it used to cover drops off the list. A
name class left open is not cosmetic: `/quo-execute` and `/quo-fix-issue` both
gate Engineer dispatch and unit advance on TaskList *name prefix plus status*,
so an unswept `pending`/`in_progress` task wedges a later dispatch on a task
nothing will ever clear.

This module is a mechanical tripwire for that shape. It is deliberately NOT an
English parser: it fails when a class gains no close-out anywhere, and when one
of the two skills' pinned prefix-sweep sites stops enumerating a class it owns.
Judgement calls about whether a particular close-out is *correct* stay with the
human review criteria in CLAUDE.md `## Review criteria for skill changes`.

EXTRACTION RULE — how a "name-class stem" is derived
----------------------------------------------------
The authority for the name classes a skill defines is its
``##### TaskList naming convention`` section (both skills carry one). Inside
that section only, every inline code span is examined:

  1. The span must be a **name template**: hyphen-joined segments, each segment
     either a literal lowercase word, a digit run, or a ``<placeholder>``; and
     at least one segment must be a ``<placeholder>``. Concrete example names
     (``engineer-veq``, ``test-writer-postcomp-2-r1``) are skipped here — they
     illustrate a template that is already being counted. Mixed segments such
     as ``r<n>`` are not segments the grammar accepts, so a token like
     ``<role>-<subtask-id>-r<n>`` is skipped; its class is already contributed
     by ``<role>-<subtask-id>``.
  2. A leading ``<role>`` / ``<reviewer>`` placeholder is **expanded** against
     ROLE_PLACEHOLDERS, because the prose uses those two generically to mean
     "each of the three implementer/reviewer roles". Expansion applies only in
     leading position; a ``<role>`` anywhere else terminates the stem instead
     (so ``aborted-<role>-<issue-id>`` yields the single stem ``aborted-``,
     matching how the prose treats `aborted-` as one name class). A template
     whose leading segment is a placeholder ROLE_PLACEHOLDERS does **not** know
     is a hard error, not a silent skip: the extractor cannot guess what the new
     placeholder expands to, and returning no stem for it would let a whole new
     name class enter a skill without this module noticing. Teach
     ROLE_PLACEHOLDERS about it instead. (Tokens the grammar in rule 1 rejects —
     the discriminated forms ``-r<n>``, ``-rev<n>``, ``<role>-postcomp-<n>-r<k>``
     — are still skipped silently, before the placeholder check runs; their
     classes are contributed by the undiscriminated template.)
  3. The stem is the leading run of literal segments (after any expansion),
     hyphen-terminated: ``analyst-<issue-id>`` -> ``analyst-``,
     ``gate-<kind>-<short-suffix>`` -> ``gate-``, ``<role>-postcomp-<n>`` ->
     ``engineer-postcomp-`` / ``test-writer-postcomp-`` / ``doc-writer-postcomp-``.

The extracted set is pinned in EXPECTED_STEMS so that *adding* a name class is a
conscious edit to this file — which is the moment to confirm the new class is
also closed out somewhere.

MATCHING RULE — when does a piece of prose "mention" a stem
-----------------------------------------------------------
Only inline code spans count, and the stem must match at the **start** of the
span. That is what keeps ``/quo-engineer-review`` (a skill name, not a TaskList
name) from reading as a mention of the ``engineer-`` class. Each stem also
matches through its generic form — ``engineer-postcomp-`` is mentioned by both
``engineer-postcomp-1`` and ``<role>-postcomp-<n>`` — and longest-prefix-wins,
so ``<role>-postcomp-<n>`` evidences the three postcomp stems and NOT the bare
``engineer-`` / ``test-writer-`` / ``doc-writer-`` classes.

CONTEXT RULE — creation vs close-out
------------------------------------
Evidence is looked for at **block** granularity (blank-line-separated groups of
lines), widened to include the two preceding blocks. The widening is load-
bearing for markdown: a close-out's verb usually sits in the list's lead-in
paragraph ("mark the following `completed` ... sweeping by name prefix:") while
the names themselves sit in the bullets underneath it. A block window counts as
a creation context when it carries a creation verb (create / dispatch / open /
pending) and as a close-out context when it carries a close-out verb (complete /
close out / sweep / mark / clear). A prefix sweep therefore closes out every
stem its sweep block names, which is exactly how both skills are written.

WHAT THIS DELIBERATELY DOES NOT DO
----------------------------------
It does not check that a close-out fires on the right *path*, nor that the two
skills agree with each other on class inventory (they legitimately differ:
`analyst-` and `file-from-url-` exist only in `/quo-fix-issue`, whose Issue
lifecycle has an Analyst pass and a URL-resolution sub-step). It also cannot
tell a real close-out sentence from an incidental co-occurrence inside the same
block; the pinned-site test below is the sharp check, and the global test is the
broad one.
"""

import re

import pytest

from conftest import QUO_EXECUTE, QUO_FIX_ISSUE, read

FIX_ISSUE = QUO_FIX_ISSUE
EXECUTE = QUO_EXECUTE

NAMING_HEADING = "##### TaskList naming convention"

CODE_SPAN = re.compile(r"`([^`\n]+)`")

# A hyphen-joined name template: literal words, digit runs, or <placeholders>.
NAME_TEMPLATE = re.compile(
    r"^(?:[a-z][a-z0-9]*|<[a-z][a-z-]*>)"
    r"(?:-(?:[a-z][a-z0-9]*|<[a-z][a-z-]*>|\d+))+$"
)

# Placeholders the prose uses generically for "each of these roles".
ROLE_PLACEHOLDERS = {
    "<role>": ("engineer", "test-writer", "doc-writer"),
    "<reviewer>": ("code-reviewer", "test-reviewer", "doc-reviewer"),
}

CREATION_VERB = re.compile(r"\b(creat\w*|dispatch\w*|opens?|opened|pending)\b", re.I)
CLOSEOUT_VERB = re.compile(
    r"\b(complet\w*|closes? out|close-out|sweep\w*|swept|mark|marks|marked|"
    r"marking|clear|clears|cleared)\b",
    re.I,
)

# The prefix-sweep phrasing every close-out site must keep. Narrowing a site
# from a prefix sweep to an exact-name sweep silently strands every `-r<n>`
# round discriminator, which is its own recurring defect.
PREFIX_SWEEP_PHRASE = re.compile(r"by name\s+\*{0,2}prefix", re.I)

# Name classes each skill's naming-convention section defines. Pinned so that a
# newly-added class is a conscious edit here — and the prompt to confirm the new
# class is created AND closed out somewhere.
EXPECTED_STEMS = {
    FIX_ISSUE: {
        "aborted-",
        "analyst-",
        "code-reviewer-",
        "defer-",
        "doc-reviewer-",
        "doc-writer-",
        "doc-writer-postcomp-",
        "engineer-",
        "engineer-postcomp-",
        "file-from-url-",
        "file-issue-postcomp-",
        "gate-",
        "pm-",
        "test-reviewer-",
        "test-writer-",
        "test-writer-postcomp-",
    },
    EXECUTE: {
        "aborted-",
        "code-reviewer-",
        "defer-",
        "doc-reviewer-",
        "doc-writer-",
        "doc-writer-postcomp-",
        "engineer-",
        "engineer-postcomp-",
        "gate-",
        "pm-",
        "test-reviewer-",
        "test-writer-",
        "test-writer-postcomp-",
    },
}

# The prefix-sweep close-out sites, each delimited by a start and an end anchor
# (both must occur exactly once in the file), plus the name classes that site is
# required to enumerate. These are the lists that get silently narrowed.
SWEEP_SITES = {
    FIX_ISSUE: {
        # Section 7 step 3 — the fixed-path per-issue close-out.
        "section-7-step-3": (
            "3. Mark the per-issue TaskList tasks as `completed`",
            "4. Output the summary:",
            {
                "aborted-",
                "analyst-",
                "code-reviewer-",
                "doc-reviewer-",
                "doc-writer-",
                "engineer-",
                "pm-",
                "test-reviewer-",
                "test-writer-",
            },
        ),
        # `#### Aborted-Issue close-out` step 1 — the same sweep on the aborted
        # path, plus the `gate-*` task that routed the abort.
        "aborted-issue-close-out": (
            "1. **Close out this Issue's TaskList tasks**",
            "2. **Run Section 7.5's deferral-hygiene gate**",
            {
                "aborted-",
                "analyst-",
                "code-reviewer-",
                "doc-reviewer-",
                "doc-writer-",
                "engineer-",
                "gate-",
                "pm-",
                "test-reviewer-",
                "test-writer-",
            },
        ),
    },
    EXECUTE: {
        # Section 4.1 step 3 — per-Task close-out. It sweeps "named per the
        # convention established in Section 3" generically and names only the
        # classes it calls out by example, so its pinned set is deliberately
        # small; Section 4.2's aborted-run site is the explicit enumeration.
        "section-4.1-step-3": (
            "3. Mark the per-Task TaskList tasks",
            "4. Output the summary below",
            {"aborted-", "doc-writer-", "pm-"},
        ),
        # Section 4.2 `##### Aborted-run close-out` step 1. Per-Task scope names
        # `<role>-<subtask-id>` (the three implementer classes) and
        # `pm-<task-id>`; Bee scope is closed by reference to Section 5's
        # Bee-level close-out, so the three reviewer classes are not named here.
        "aborted-run-close-out": (
            "1. **Close out the TaskList, sweeping by name prefix.**",
            "2. **Run the Epic-boundary state-externalization checkpoint**",
            {"aborted-", "doc-writer-", "engineer-", "gate-", "pm-", "test-writer-"},
        ),
        # Section 5's Bee-level close-out — the only site that closes the
        # Bee-scoped names, which have no per-Task site to fall into.
        "bee-level-close-out": (
            "**Bee-level TaskList close-out (runs once",
            '**"Clear from the active set" means mark the task `completed`',
            {
                "aborted-",
                "code-reviewer-",
                "doc-reviewer-",
                "doc-writer-",
                "engineer-",
                "pm-",
                "test-reviewer-",
                "test-writer-",
            },
        ),
    },
}


def read_skill(relpath):
    return read(relpath)


def naming_convention_section(text):
    """Return the `##### TaskList naming convention` section's text."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if line.strip() == NAMING_HEADING]
    assert len(starts) == 1, (
        f"expected exactly one {NAMING_HEADING!r} heading, found {len(starts)}"
    )
    start = starts[0]
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("#"):
            end = j
            break
    return "\n".join(lines[start:end])


def _segments(token):
    """Split a name template into literal words and `<placeholder>` segments."""
    segs = []
    i = 0
    while i < len(token):
        if token[i] == "<":
            j = token.index(">", i)
            segs.append(token[i:j + 1])
            i = j + 1
            if i < len(token) and token[i] == "-":
                i += 1
        else:
            j = token.find("<", i)
            chunk = token[i:] if j == -1 else token[i:j]
            i = len(token) if j == -1 else j
            segs.extend(part for part in chunk.split("-") if part)
    return segs


def stems_from_template(token):
    """Derive the name-class stem(s) a naming-convention template defines.

    Raises `AssertionError` when the template leads with a `<placeholder>` this
    module has no expansion for — see extraction rule 2 in the module docstring.
    Returning `[]` there would let a newly-introduced name class slip in with the
    suite still green, which is the one outcome this module exists to prevent.
    """
    if "<" not in token or not NAME_TEMPLATE.match(token):
        return []
    segs = _segments(token)
    if len(segs) < 2:
        return []
    heads = [()]
    rest = segs
    if segs[0].startswith("<"):
        assert segs[0] in ROLE_PLACEHOLDERS, (
            f"name template {token!r} leads with an unrecognised placeholder "
            f"{segs[0]!r} — teach ROLE_PLACEHOLDERS about it (with the roles it "
            "expands to) so its name class is extracted, rather than letting the "
            "template yield no stem and enter the skill unnoticed"
        )
        heads = [(role,) for role in ROLE_PLACEHOLDERS[segs[0]]]
        rest = segs[1:]
    literals = []
    for seg in rest:
        if seg.startswith("<"):
            break
        literals.append(seg)
    stems = []
    for head in heads:
        parts = list(head) + literals
        if parts:
            stems.append("-".join(parts) + "-")
    return stems


def declared_stems(text):
    """Every name-class stem the skill's naming-convention section defines."""
    stems = set()
    for token in CODE_SPAN.findall(naming_convention_section(text)):
        stems.update(stems_from_template(token))
    return stems


def surface_prefixes(stem):
    """Every prefix that counts as a mention of `stem` at a code span's start."""
    prefixes = {stem}
    for placeholder, roles in ROLE_PLACEHOLDERS.items():
        for role in roles:
            if stem.startswith(role + "-"):
                prefixes.add(placeholder + "-" + stem[len(role) + 1:])
    return prefixes


def stems_mentioned(text, stems):
    """Stems mentioned by any code span in `text`, longest-prefix-wins."""
    index = {stem: surface_prefixes(stem) for stem in stems}
    mentioned = set()
    for token in CODE_SPAN.findall(text):
        best_len, best = 0, set()
        for stem, prefixes in index.items():
            for prefix in prefixes:
                if token.startswith(prefix):
                    if len(prefix) > best_len:
                        best_len, best = len(prefix), {stem}
                    elif len(prefix) == best_len:
                        best.add(stem)
        mentioned |= best
    return mentioned


def blocks(text):
    """Blank-line-separated blocks, in document order."""
    out, current = [], []
    for line in text.splitlines():
        if line.strip():
            current.append(line)
        elif current:
            out.append("\n".join(current))
            current = []
    if current:
        out.append("\n".join(current))
    return out


def creation_and_closeout(text, stems):
    """Return (created, closed) stem sets evidenced anywhere in the skill."""
    created, closed = set(), set()
    doc_blocks = blocks(text)
    for i, block in enumerate(doc_blocks):
        here = stems_mentioned(block, stems)
        if not here:
            continue
        window = "\n".join(doc_blocks[max(0, i - 2):i + 1])
        if CREATION_VERB.search(window):
            created |= here
        if CLOSEOUT_VERB.search(window):
            closed |= here
    return created, closed


def site_region(text, start_anchor, end_anchor):
    """The lines from `start_anchor`'s line up to (not including) `end_anchor`'s."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if start_anchor in line]
    assert len(starts) == 1, (
        f"start anchor {start_anchor!r} must occur exactly once; found {len(starts)}"
    )
    ends = [i for i, line in enumerate(lines) if end_anchor in line]
    assert len(ends) == 1, (
        f"end anchor {end_anchor!r} must occur exactly once; found {len(ends)}"
    )
    assert ends[0] > starts[0], (
        f"end anchor {end_anchor!r} precedes start anchor {start_anchor!r}"
    )
    return "\n".join(lines[starts[0]:ends[0]])


def test_declared_name_classes_match_the_pinned_inventory():
    """The stems extracted from each naming convention are the pinned set.

    Fails when a name class is added, renamed, or removed. That failure is the
    prompt to update EXPECTED_STEMS *and* to confirm the new class has both a
    creation site and a close-out site — the pairing this module exists for.
    """
    for relpath, expected in EXPECTED_STEMS.items():
        found = declared_stems(read_skill(relpath))
        assert found == expected, (
            f"{relpath}: TaskList name classes drifted from the pinned inventory.\n"
            f"  added:   {sorted(found - expected)}\n"
            f"  removed: {sorted(expected - found)}\n"
            "Update EXPECTED_STEMS, and confirm any added class is both created "
            "and closed out."
        )


def test_every_name_class_is_created_and_closed_out():
    """Each declared name class has both a creation and a close-out context.

    The broad tripwire: a class that is dispatched/created but that no sweep,
    mark-completed, or close-out prose ever names is a task nothing will clear.
    """
    for relpath, expected in EXPECTED_STEMS.items():
        text = read_skill(relpath)
        created, closed = creation_and_closeout(text, expected)
        missing_creation = sorted(expected - created)
        missing_closeout = sorted(expected - closed)
        assert not missing_creation, (
            f"{relpath}: name class(es) with no creation context: {missing_creation}"
        )
        assert not missing_closeout, (
            f"{relpath}: name class(es) created but never closed out: "
            f"{missing_closeout}"
        )


def test_prefix_sweep_sites_enumerate_their_name_classes():
    """Each pinned close-out site still enumerates the classes it owns.

    This is the sharp check. Dropping an entry from one of these lists — e.g.
    removing the `aborted-` marker from `/quo-fix-issue` Section 7 step 3's
    close-out — fails here even though the class is still closed out elsewhere.
    """
    for relpath, sites in SWEEP_SITES.items():
        text = read_skill(relpath)
        stems = EXPECTED_STEMS[relpath]
        for site_name, (start, end, expected) in sites.items():
            region = site_region(text, start, end)
            found = stems_mentioned(region, stems)
            assert found == expected, (
                f"{relpath} [{site_name}]: close-out sweep no longer covers the "
                "same name classes.\n"
                f"  newly named: {sorted(found - expected)}\n"
                f"  dropped:     {sorted(expected - found)}\n"
                "A dropped class is a task the sweep will leave active."
            )


def test_prefix_sweep_sites_still_sweep_by_prefix():
    """Every close-out site keeps its by-name-prefix sweep instruction.

    Narrowing a sweep from prefix-matching to exact names strands every
    `-r<n>` round-discriminated re-dispatch the naming convention permits.
    """
    for relpath, sites in SWEEP_SITES.items():
        text = read_skill(relpath)
        for site_name, (start, end, _) in sites.items():
            region = site_region(text, start, end)
            assert PREFIX_SWEEP_PHRASE.search(region), (
                f"{relpath} [{site_name}]: close-out no longer says it sweeps "
                "by name prefix"
            )


def test_paired_fix_issue_sweeps_stay_in_step():
    """`/quo-fix-issue`'s two per-Issue sweeps cover the same classes.

    The skill states the invariant itself — "The aborted path runs this same
    sweep at its own site ... a name added to the list above belongs in that
    step's list too". The aborted site additionally closes the `gate-*` task
    that routed the abort, which the fixed path never created; that one class is
    the documented difference.
    """
    text = read_skill(FIX_ISSUE)
    stems = EXPECTED_STEMS[FIX_ISSUE]
    sites = SWEEP_SITES[FIX_ISSUE]
    fixed = stems_mentioned(site_region(text, *sites["section-7-step-3"][:2]), stems)
    aborted = stems_mentioned(
        site_region(text, *sites["aborted-issue-close-out"][:2]), stems
    )
    assert fixed - {"gate-"} == aborted - {"gate-"}, (
        "/quo-fix-issue's fixed-path and aborted-path per-Issue sweeps diverged "
        "(the skill requires them to stay in step).\n"
        f"  only on the fixed path:   {sorted(fixed - aborted - {'gate-'})}\n"
        f"  only on the aborted path: {sorted(aborted - fixed - {'gate-'})}"
    )


def test_detector_flags_a_class_that_is_created_but_never_closed():
    """Proof the guard is not hollow, on synthetic prose.

    A class that is dispatched but appears in no close-out context must be
    reported as missing a close-out, and a sweep block that names a class must
    count as that class's close-out.
    """
    stems = {"engineer-", "widget-"}
    synthetic = (
        "Dispatch the Engineer and create its `engineer-<issue-id>` task.\n"
        "\n"
        "Create a `widget-<n>` task when the widget lane opens.\n"
        "\n"
        "At close-out, sweep by name prefix and mark `completed`:\n"
        "\n"
        "- the `engineer-<issue-id>` task and every `-r<n>` round of it;\n"
    )
    created, closed = creation_and_closeout(synthetic, stems)
    assert created == {"engineer-", "widget-"}, created
    assert closed == {"engineer-"}, closed


def test_extractor_rejects_an_unrecognised_leading_placeholder():
    """A new leading placeholder is a hard error, not a silent empty result.

    Adding a class like `<writer>-recheck-<issue-id>` to a naming-convention
    section used to yield no stem at all, so the class entered the skill without
    EXPECTED_STEMS changing and without any close-out being demanded of it.
    """
    with pytest.raises(AssertionError, match="unrecognised placeholder"):
        stems_from_template("<writer>-recheck-<issue-id>")


def test_extractor_still_skips_the_discriminated_forms_silently():
    """`-r<n>` / `-rev<n>` / `-r<k>` forms are rejected by the grammar first.

    They must not trip the new placeholder error: each is a round-discriminated
    spelling of a template already counted, and the mixed `r<n>` segment is what
    the grammar in extraction rule 1 refuses.
    """
    for token in (
        "-r<n>",
        "-rev<n>",
        "<role>-<issue-id>-r<n>",
        "<role>-postcomp-<n>-r<k>",
        "analyst-<issue-id>-rev<n>",
    ):
        assert stems_from_template(token) == [], token


def test_extractor_expands_the_two_known_leading_placeholders():
    """The recognised leading placeholders still expand to one stem per role."""
    assert stems_from_template("<role>-<issue-id>") == [
        "engineer-",
        "test-writer-",
        "doc-writer-",
    ]
    assert stems_from_template("<reviewer>-<bee-id>") == [
        "code-reviewer-",
        "test-reviewer-",
        "doc-reviewer-",
    ]


def test_detector_ignores_skill_names_that_share_a_role_prefix():
    """`/quo-engineer-review` is a skill name, not an `engineer-` TaskList task.

    Guards the start-of-code-span matching rule: without it, every mention of
    the review skill would forge creation and close-out evidence for the
    `engineer-` class.
    """
    stems = {"engineer-", "test-writer-"}
    synthetic = "The PM drives `/quo-engineer-review` and `quo-test-writer-review`."
    assert stems_mentioned(synthetic, stems) == set()
