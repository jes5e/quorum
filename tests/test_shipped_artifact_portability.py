"""Shipped-artifact portability guard — regression test for Issue b.bq4.

The install procedure copies only `skills/*` and `agents/*` into a user's
project (see CLAUDE.md `## Review criteria for skill changes`). A *shipped
artifact* — any `skills/*/SKILL.md`, any `agents/*.md`, or a bundled helper
script under `skills/*/scripts/` — therefore must not cite a repo-only document
that never ships: `docs/*`, `CONTRIBUTING.md`, or a section of *this* repo's
`CLAUDE.md`. Such a citation DANGLES on a fresh install (the target has no
`docs/doc-writing-guide.md`, no `CLAUDE.md ## Scratch-file convention`, etc.).
That invariant regrew silently before, which is what spawned Issue b.bq4; this
module pins the mechanically-checkable part of it so a reintroduction fails the
suite rather than shipping unnoticed.

WHAT THIS ENFORCES — the dangling *citation-tail* shape the fix severed: a
repo-only doc reference (`docs/<name>.md`, `CONTRIBUTING.md`, or `CLAUDE.md`)
carrying a backtick-wrapped ``## <Section>`` anchor immediately after it. The
only legitimate `<doc> `## <Section>`` tails in shipped prose point at the two
target-repo CLAUDE.md **contract keys** (`## Documentation Locations`,
`## Build Commands`) — the string contract every skill is DESIGNED to read from
the *installing* project's CLAUDE.md (CLAUDE.md `## Contract keys that
downstream skills depend on`). Those two, and only those two, are allowlisted.
Any other doc-plus-section tail is a dangling cross-repo citation and fails.

The allowlist is deliberately just those two keys and nothing more: if a future
skill legitimately needs to cite another *target*-repo CLAUDE.md section, the
failure here is the correct prompt to add it consciously (after confirming it is
a target-repo section, not a this-repo dangling reference) — not something to
pre-widen the fence for.

WHAT THIS DELIBERATELY DOES NOT ENFORCE (left to the `## Review criteria for
skill changes` review criterion, because it is not lexically separable from
legitimate prose):

  (a) Bare repo-only-doc mentions with NO section anchor. `quo-setup` writes
      `docs/test-writing-guide.md` / `docs/doc-writing-guide.md` as the *default
      values* of a target repo's `## Documentation Locations` contract keys, and
      several skills carry "don't hardcode `docs/prd.md`" *negative* examples.
      A bare `docs/*.md` token is indistinguishable by regex from those, so
      flagging it would false-positive worse than no guard. The dangling tails
      the Issue is about all carried a `## <Section>` anchor, which those
      legitimate mentions never do — that anchor is the sharp discriminator.

  (b) This-repo ticket-ID citations (`b.wii`, `b.fpm`, ...). They are lexically
      IDENTICAL to the illustrative placeholder IDs that legitimately pepper the
      prose (`b.abc`, `b.veq`, `t1.rwx.o4`, ...), so no regex can tell a real
      citation from a placeholder. That half stays a human-review criterion.

The README->`docs/*` carve-out (a `README.md` link to `docs/*` is legitimate —
README is not installed via `cp -r skills/*`) needs no handling here because
README.md is not a shipped artifact and is not scanned.

`README.md` is ALSO intentionally omitted from the detector's repo-only-doc
token set (the `docs/*`|`CONTRIBUTING.md`|`CLAUDE.md` alternation in
`CITATION_TAIL`) — not merely unscanned as a scan *source*. Unlike internal
`docs/*`, the README is the customer-facing install guide that installed users
demonstrably receive and consult, so a shipped artifact citing
`` `README.md` `## <Section>` `` (e.g. the existing `` `README.md` `## Install` ``
references in `skills/quo-fix-issue/SKILL.md`, `skills/quo-execute/SKILL.md`, and
`skills/quo-breakdown-epic/SKILL.md`) points at a document that is reachable on a
fresh install in a way `docs/*` citations are not. Such tails do NOT dangle, so
folding `README.md` into the detector would be a false-positive regression — do
not add it.
"""

import re

from conftest import REPO_ROOT

# Target-repo CLAUDE.md contract keys every skill legitimately reads from the
# *installing* project's CLAUDE.md. These are the only doc-plus-section citation
# tails permitted in shipped prose (CLAUDE.md `## Contract keys that downstream
# skills depend on`).
ALLOWED_SECTIONS = frozenset({
    "Documentation Locations",
    "Build Commands",
})

# A repo-only doc token (`docs/<name>.md`, `CONTRIBUTING.md`, or `CLAUDE.md`)
# immediately followed by a backtick-wrapped `## <Section>` anchor. The optional
# ``` `? ``` after the doc absorbs a closing backtick when the doc path is itself
# backtick-wrapped (e.g. `` `docs/doc-writing-guide.md` `## Querying tickets` ``);
# the bare-doc form (e.g. ``CLAUDE.md `## Build Commands` ``) has no closing
# backtick to absorb. This is the exact "citation tail" shape Issue b.bq4 severed.
CITATION_TAIL = re.compile(
    r"(?:docs/[\w.-]+\.md|CONTRIBUTING\.md|CLAUDE\.md)"
    r"`?\s*`##\s*(?P<section>[^`]+?)\s*`"
)


def shipped_artifacts():
    """Every file the install procedure copies into a target project.

    `skills/*` and `agents/*` ship wholesale, so this covers every SKILL.md,
    every bundled helper script, and every role contract. Returned repo-root
    relative for readable failure messages.
    """
    paths = []
    paths += sorted((REPO_ROOT / "skills").rglob("*.md"))
    paths += sorted((REPO_ROOT / "skills").rglob("*.py"))
    paths += sorted((REPO_ROOT / "agents").rglob("*.md"))
    return [p for p in paths if "__pycache__" not in p.parts]


def dangling_citations(text):
    """Return (section, line_no) for every non-allowlisted doc citation tail."""
    hits = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for m in CITATION_TAIL.finditer(line):
            section = m.group("section").strip()
            if section not in ALLOWED_SECTIONS:
                hits.append((section, line_no))
    return hits


def test_no_shipped_artifact_cites_a_repo_only_doc_section():
    """No shipped artifact carries a dangling repo-only-doc citation tail.

    Fails on any `<repo-only-doc> `## <Section>`` reference whose section is not
    one of the two target-repo CLAUDE.md contract keys — the regression Issue
    b.bq4 fixed and this guard prevents from regrowing.
    """
    artifacts = shipped_artifacts()
    # Sanity: the scan must actually be looking at the shipped tree.
    assert artifacts, "no shipped artifacts discovered — glob is wrong"

    offenders = []
    for path in artifacts:
        rel = path.relative_to(REPO_ROOT)
        for section, line_no in dangling_citations(path.read_text(encoding="utf-8")):
            offenders.append(f"{rel}:{line_no}: dangling citation to `## {section}`")

    assert not offenders, (
        "Shipped artifact(s) cite a repo-only doc section that never ships "
        "(dangling on a fresh install — Issue b.bq4). Inline the operative "
        "instruction at the site and sever the cross-repo citation tail, or, if "
        "this is a genuine target-repo CLAUDE.md contract key, add it to "
        "ALLOWED_SECTIONS:\n  " + "\n  ".join(offenders)
    )


def test_contract_key_tails_are_allowlisted_not_flagged():
    """The two legitimate contract-key tails must NOT be flagged.

    Guards against the allowlist being lost or the regex over-matching, which
    would false-positive on the many legitimate ``CLAUDE.md `## Build Commands` ``
    / ``CLAUDE.md `## Documentation Locations` `` references skills depend on.
    """
    for section in ALLOWED_SECTIONS:
        sample = f"read the target repo's CLAUDE.md `## {section}` before proceeding"
        assert dangling_citations(sample) == [], (
            f"contract key `## {section}` was wrongly flagged as dangling"
        )


def test_detector_fires_on_a_reintroduced_dangling_reference():
    """Proof the guard is not hollow: it flags a synthetic dangling tail.

    Uses the exact citation shapes the b.bq4 fix removed — a backtick-wrapped
    `docs/*` path plus a `## Section` anchor, and a bare `CLAUDE.md` plus a
    this-repo section — so a future refactor that neuters the regex is caught.
    """
    reintroduced = (
        "see `docs/doc-writing-guide.md` `## The Scoped-marker contract` for the grammar\n"
        "the manifest follows CLAUDE.md `## Scratch-file convention`\n"
        "per `CONTRIBUTING.md` `## Verifying external-system contracts`\n"
    )
    hits = dangling_citations(reintroduced)
    flagged = {section for section, _ in hits}
    assert flagged == {
        "The Scoped-marker contract",
        "Scratch-file convention",
        "Verifying external-system contracts",
    }, f"detector missed a reintroduced dangling reference; caught {flagged}"
