"""Writer-lane role-file guards and the completeness-evidence relay chain.

Regression test for Issue b.pdq. The Issue gave the two writer roles a stability
rule the orchestrator can actually keep, forbade them from reaching for
destructive git commands outside their own lane, and threaded the Engineer's
sweep-completeness evidence from the Engineer's return all the way into
`/quo-engineer-review`.

Both halves are cross-file contracts carried by *prose in separate files*, which
is what makes them worth pinning mechanically:

  * **The relay chain** only works if every hop agrees on one heading string.
    `agents/engineer.md` produces the evidence, the two orchestrators embed it
    in a dispatch prompt, `agents/code-reviewer.md` and `agents/pm.md` forward
    it into their `/quo-engineer-review` invocation, and that skill verifies the
    diff against it. A hop that renames the heading, or a role file that learns
    to invoke the review skill without learning to forward the evidence, breaks
    the chain silently — the review simply stops performing the check.

  * **The writer guards** are the mitigation for a writer destroying uncommitted
    work it does not own. A `git checkout` / `git restore` / `git stash` /
    `git reset` on a source path discards whatever another role (or the user)
    was holding in the working tree, and the loss is invisible to its owner. The
    sanctioned substitute is a scratch-dir copy plus an `Edit`, reported under a
    `## Perturbations` heading so a concurrent writer's movement abort can be
    attributed to it instead of escalating to an operator gate.
"""

import re

import pytest

from conftest import (
    AGENTS_DIR,
    AGENT_CODE_REVIEWER,
    AGENT_DOC_WRITER,
    AGENT_ENGINEER,
    AGENT_PM,
    AGENT_TEST_WRITER,
    QUO_EXECUTE,
    QUO_FIX_ISSUE,
    read,
)

TEST_WRITER = AGENT_TEST_WRITER
DOC_WRITER = AGENT_DOC_WRITER
ENGINEER = AGENT_ENGINEER

# The sites that relay the evidence **out of an Engineer's return**: the two
# orchestrators (which compose the dispatch prompt) and the PM (which reads a
# return directly). `agents/code-reviewer.md` is a relay site too — see
# `test_review_invokers_are_exactly_the_evidence_relayers` — but it is
# deliberately NOT in this set, because its trigger differs: the Code Reviewer
# wrapper never sees an Engineer return, only the dispatch prompt it was handed,
# so its negative branch is keyed on "the dispatch prompt carried no such block"
# rather than "no completeness list arrived". Byte-identity across those two
# triggers would be wrong prose, so that lane gets its own assertion in
# `test_code_reviewer_carries_its_own_negative_branch` instead.
RELAY_FILES = (
    QUO_FIX_ISSUE,
    QUO_EXECUTE,
    AGENT_PM,
)

EVIDENCE_HEADING = "## Engineer's completeness evidence"
FINGERPRINT_HEADING = "## Source paths to fingerprint"
FILES_CHANGED_HEADING = "## Files changed"
PERTURBATIONS_HEADING = "## Perturbations"

# The negative branch of the relay. Pinned byte-for-byte: every site that can
# relay the evidence must handle "no list arrived" the same way, because
# `/quo-engineer-review` reports a *missing* list as a finding only when the
# invocation named the assignment sweep-shaped. A site that omits the trailing
# clause silently loses the missing-list check.
NEGATIVE_BRANCH_SENTENCE = (
    "When no completeness list arrived, omit the `## Engineer's completeness "
    "evidence` heading rather than emitting an empty one — but still state that "
    "the assignment was sweep-shaped when it was, so `/quo-engineer-review`'s "
    "missing-list check stays reachable."
)
EXPECTED_RELAY_SITES = 5

# The Code Reviewer lane's own negative branch. Same two obligations — suppress
# the empty heading, keep the sweep-shaped statement — stated against the
# prompt-side trigger.
CODE_REVIEWER_NEGATIVE_BRANCH = (
    "When the dispatch prompt carried no such block, forward no heading rather "
    "than an empty one"
)
CODE_REVIEWER_SWEEP_CLAUSE = (
    "still forward the sweep-shaped statement when the prompt made it"
)

FORBIDDEN_GIT_COMMANDS = ("git checkout", "git restore", "git stash", "git reset")

# A shell git invocation: the word `git` followed by a subcommand.
GIT_COMMAND = re.compile(r"\bgit\s+[a-z][a-z-]*")

# Sentence-ish split, good enough for prose scanning. The `|\n` alternative is
# load-bearing: these are markdown files, where a claim frequently occupies a
# whole line with no terminal punctuation. Splitting on sentence enders alone
# glued such a line to the paragraph below it, so an affirmative freeze claim
# inserted directly above the existing denial paragraph landed in the *same*
# segment as that denial and inherited its `FREEZE_DENIAL` match — the guard
# read as green while the forbidden claim sat in the file. A line break ends a
# scanned segment regardless of how the line was punctuated.
SENTENCE_SPLIT = re.compile(r"(?<=[.:!?])\s+|\n")

# Cues that a sentence mentioning a frozen tree is *denying* the guarantee.
# Deliberately narrow: an earlier revision also accepted a bare `not` / `no`,
# which any ordinary sentence carries incidentally — "The source tree is frozen,
# so you need not re-check it" passed on the strength of the word "not" while
# asserting exactly the guarantee the rule forbids. Only phrases that negate the
# *guarantee itself* count.
FREEZE_DENIAL = re.compile(
    r"(neither mode guarantees|does not guarantee|never guaranteed|"
    r"cannot prevent|overclaiming)",
    re.I,
)


def agent_files():
    return sorted(p for p in AGENTS_DIR.glob("*.md"))


def frontmatter_tools(text):
    """The `tools:` list from a role file's YAML frontmatter."""
    match = re.search(r"^tools:\s*\[(?P<tools>[^\]]*)\]", text, re.M)
    assert match, "role file has no `tools:` frontmatter list"
    return [tool.strip() for tool in match.group("tools").split(",") if tool.strip()]


# --------------------------------------------------------------------------
# Relay chain
# --------------------------------------------------------------------------


def test_review_invokers_are_exactly_the_evidence_relayers():
    """Every role file that invokes `/quo-engineer-review` also relays evidence.

    Set equality in both directions. A role that gains the review invocation
    without gaining the relay drops the sweep-verification check on that lane;
    a role that relays evidence it never passes to a review has a dead relay.
    """
    invokers, relayers = set(), set()
    for path in agent_files():
        text = read(path)
        if "quo-engineer-review" in text:
            invokers.add(path.name)
        if "Engineer's completeness evidence" in text:
            relayers.add(path.name)
    assert invokers == relayers, (
        "role files that invoke `/quo-engineer-review` and role files that relay "
        "the Engineer's completeness evidence must be the same set.\n"
        f"  invoke but do not relay: {sorted(invokers - relayers)}\n"
        f"  relay but do not invoke: {sorted(relayers - invokers)}"
    )
    assert invokers == {"code-reviewer.md", "pm.md"}, (
        f"unexpected `/quo-engineer-review` invoker set: {sorted(invokers)} — if "
        "a role legitimately gained the invocation, confirm it also gained the "
        "relay and update this assertion"
    )


def test_negative_branch_sentence_is_byte_identical_at_every_return_side_relay_site():
    """Every return-side relay site handles "no list arrived" with one sentence.

    Divergence here is how the missing-list check gets lost at one site while
    reading as present everywhere else. Scope is RELAY_FILES — the sites keyed
    on an Engineer's *return*; the Code Reviewer lane is keyed on the dispatch
    prompt instead and is covered by the test below.
    """
    total = 0
    for relpath in RELAY_FILES:
        count = read(relpath).count(NEGATIVE_BRANCH_SENTENCE)
        assert count, (
            f"{relpath}: the relay's negative-branch sentence is missing or "
            "reworded"
        )
        total += count
    assert total >= EXPECTED_RELAY_SITES, (
        f"expected at least {EXPECTED_RELAY_SITES} relay sites carrying the "
        f"negative-branch sentence, found {total}"
    )


def test_code_reviewer_carries_its_own_negative_branch():
    """The fourth relay site states both halves of the negative branch.

    `agents/code-reviewer.md` is a relay site by the set-equality test above,
    but it paraphrases rather than repeats: it never sees an Engineer return, so
    its trigger is "the dispatch prompt carried no such block". Both obligations
    still apply, and the second is the load-bearing one — dropping the trailing
    sweep-shaped clause leaves the wrapper forwarding nothing at all when no
    list came back, which is precisely the case `/quo-engineer-review`'s
    missing-list check exists to catch.
    """
    text = read(AGENT_CODE_REVIEWER)
    assert CODE_REVIEWER_NEGATIVE_BRANCH in text, (
        "agents/code-reviewer.md: the suppress-the-empty-heading half of the "
        "negative branch is missing or reworded"
    )
    assert CODE_REVIEWER_SWEEP_CLAUSE in text, (
        "agents/code-reviewer.md: the negative branch no longer forwards the "
        "sweep-shaped statement when no evidence block arrived, so "
        "`/quo-engineer-review`'s missing-list check is unreachable on this lane"
    )
    assert text.index(CODE_REVIEWER_NEGATIVE_BRANCH) < text.index(
        CODE_REVIEWER_SWEEP_CLAUSE
    ), (
        "agents/code-reviewer.md: the sweep-shaped clause must qualify the "
        "no-heading rule, not precede it"
    )


def test_engineer_produces_the_evidence_the_relay_carries():
    """`agents/engineer.md` requires the sweep-completeness evidence and the file list.

    Both are inputs nothing else can regenerate once the Engineer Agent exits:
    the evidence feeds `/quo-engineer-review`'s sweep verification, and the
    changed-file list becomes the Test Writer's `## Source paths to fingerprint`
    set.
    """
    text = read(ENGINEER)
    assert "**Sweep-completeness evidence.**" in text
    assert "a **completeness check with evidence**" in text, (
        "the evidence-not-assertion requirement is missing"
    )
    assert FILES_CHANGED_HEADING in text
    assert "**Changed-file list (required in every return).**" in text


def test_fingerprint_path_relay_is_wired_end_to_end():
    """The fingerprint path set has a producer, two carriers, and a consumer."""
    for relpath in (QUO_FIX_ISSUE, QUO_EXECUTE):
        text = read(relpath)
        assert FINGERPRINT_HEADING in text, (
            f"{relpath}: no `{FINGERPRINT_HEADING}` heading supplied to the "
            "Test Writer dispatch"
        )
        assert FILES_CHANGED_HEADING in text, (
            f"{relpath}: the Engineer's changed-file list is not read as the "
            "source of that set"
        )
    assert FINGERPRINT_HEADING in read(TEST_WRITER), (
        "agents/test-writer.md no longer names the heading its fingerprint set "
        "arrives under"
    )


# --------------------------------------------------------------------------
# Writer-lane guards
# --------------------------------------------------------------------------


def test_test_writer_forbids_destructive_git_on_non_test_paths():
    """All four destructive git commands are named and forbidden.

    Naming them individually matters: a writer reaching for the one that was
    left off the list does the same damage as any of the others.
    """
    text = read(TEST_WRITER)
    prohibition = next(
        line for line in text.splitlines()
        if "**Never mutate files outside the test lane.**" in line
    )
    for command in FORBIDDEN_GIT_COMMANDS:
        assert f"`{command}`" in prohibition, (
            f"agents/test-writer.md no longer forbids `{command}` in its "
            "never-mutate-outside-the-lane rule"
        )
    assert "non-test path" in prohibition, (
        "the prohibition no longer scopes itself to non-test paths"
    )
    assert "even for a momentary revert" in prohibition, (
        "the momentary-revert carve-out closure is gone — that is the loophole "
        "a discrimination experiment reaches for"
    )


def test_test_writer_requires_a_perturbations_section():
    """Perturbations are reported under a required heading, `None` when empty.

    Both orchestrators read that list to attribute a concurrent writer's
    movement abort to a self-inflicted, already-reverted edit; an omitted
    heading is indistinguishable from a forgotten one.
    """
    text = read(TEST_WRITER)
    assert f"`{PERTURBATIONS_HEADING}` heading" in text
    assert "emit the heading with the single word `None` under it" in text, (
        "the empty-case rule for `## Perturbations` is missing"
    )
    for orchestrator in (QUO_FIX_ISSUE, QUO_EXECUTE):
        assert PERTURBATIONS_HEADING in read(orchestrator), (
            f"{orchestrator}: no reader for the writer's `## Perturbations` list"
        )


def test_test_writer_sanctions_a_scratch_copy_instead_of_git():
    """The substitute for a destructive git revert is a namespaced scratch copy.

    Forbidding the git commands without naming a substitute leaves the
    discrimination experiment with no sanctioned route.
    """
    text = read(TEST_WRITER)
    assert "/tmp/.quorum" in text and "%TEMP%\\.quorum" in text, (
        "the scratch-copy recipe lost one of its two OS-paired paths"
    )
    assert "**Do not delete the scratch copy**" in text
    assert "`git hash-object`" in text, (
        "the byte-exact restore check is no longer offered"
    )


def test_neither_writer_role_claims_a_frozen_tree():
    """No sentence in either writer role file asserts a frozen source tree.

    Both files may — and do — *deny* the guarantee. What must not appear is an
    affirmative claim, because the orchestrator cannot keep it.
    """
    for relpath in (TEST_WRITER, DOC_WRITER):
        text = read(relpath)
        for sentence in SENTENCE_SPLIT.split(text):
            if "frozen" not in sentence:
                continue
            assert FREEZE_DENIAL.search(sentence), (
                f"{relpath}: a sentence asserts a frozen tree rather "
                f"than denying the guarantee: {sentence.strip()!r}"
            )
        assert "Neither mode guarantees the source tree is" in text, (
            f"{relpath}: the explicit no-freeze-guarantee statement is gone"
        )


@pytest.mark.parametrize(
    "prose",
    [
        # The mutation that slipped past the earlier `not\b` / `no\b` cues: an
        # affirmative freeze claim whose only negation is an incidental "not".
        "The source tree is frozen for the duration of your run, so you need "
        "not re-check it.",
        "The source tree is frozen; no re-check is required.",
        "Your dispatch prompt guarantees a frozen tree.",
        # The mutation that slipped past the sentence-ender-only split: an
        # unpunctuated markdown line carrying the claim, sitting directly above
        # the denial paragraph the role files legitimately contain. Splitting on
        # `[.:!?]` alone merged the two, handing the claim the denial's
        # `FREEZE_DENIAL` match; the `\n` alternative keeps them separate.
        "The source tree is frozen while you run\n"
        "Neither mode guarantees the source tree is **frozen**: the "
        "orchestrator cannot prevent a second session from editing files.",
    ],
)
def test_freeze_detector_flags_affirmative_claims_containing_a_negation(prose):
    """Proof the guard is not hollow — a nearby negation is not a denial.

    Two ways an affirmative claim could borrow a denial it does not make: an
    incidental "not"/"no" inside the same sentence, and a genuine denial on an
    adjacent line that a too-coarse split folds into the same segment. The
    scanner must flag the claim in both shapes, so this drives the real
    `SENTENCE_SPLIT` rather than calling `FREEZE_DENIAL` on the whole input.
    """
    flagged = [
        segment
        for segment in SENTENCE_SPLIT.split(prose)
        if "frozen" in segment and not FREEZE_DENIAL.search(segment)
    ]
    assert flagged, (
        "an affirmative frozen-tree claim reads as a denial once split: "
        f"{prose!r}"
    )


@pytest.mark.parametrize(
    "sentence",
    [
        "Neither mode guarantees the source tree is **frozen**:",
        "The orchestrator cannot prevent a second session from editing files, "
        "so treat a claim of a frozen tree as overclaiming.",
        "This prompt does not guarantee that the tree stays frozen.",
        "A frozen tree is never guaranteed in either mode.",
    ],
)
def test_freeze_detector_accepts_genuine_denials(sentence):
    """The tightened cues still recognize the denials both role files use."""
    assert FREEZE_DENIAL.search(sentence), (
        f"a genuine no-freeze-guarantee denial is no longer recognized: {sentence!r}"
    )


def test_doc_writer_has_no_bash_and_is_given_no_git_command():
    """`agents/doc-writer.md` carries no shell git instruction.

    Its tool allowlist has no `Bash`, so a git command in its prose is an
    instruction it cannot execute — the narrate-instead-of-do shape.
    """
    text = read(DOC_WRITER)
    assert "Bash" not in frontmatter_tools(text), (
        "doc-writer gained `Bash`; the no-git-instruction rule below assumes it "
        "has none"
    )
    hits = [
        f"line {line_no}: {match.group(0)!r}"
        for line_no, line in enumerate(text.splitlines(), start=1)
        for match in [GIT_COMMAND.search(line)]
        if match
    ]
    assert not hits, (
        "agents/doc-writer.md contains a git command instruction despite having "
        "no `Bash` tool: " + "; ".join(hits)
    )
    assert "`Bash` is not in this subagent's tool allowlist" in text, (
        "the re-check-with-Read/Grep routing for the movement check is gone"
    )


def test_test_writer_orders_the_closing_fingerprint_before_the_done_flip():
    """In execute mode the closing reading precedes `status=done`, and an abort skips it.

    A `done` Subtask on a lane that stopped on movement is a premature flip the
    orchestrator has to undo, so the ordering is part of the contract rather
    than a suggestion.
    """
    text = read(TEST_WRITER)
    assert (
        "**Order the `done` flip after the closing movement-fingerprint reading "
        "(execute mode).**" in text
    )
    assert "do NOT perform the flip at all" in text, (
        "the abort branch no longer forbids the `done` flip"
    )
    assert "Fix mode has no flip to order" in text, (
        "the fix-mode branch of the ordering rule is missing"
    )
