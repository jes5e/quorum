"""Size ratchet over every shipped prose file.

Skill and role prose grew 4-8x over its history one reasonable-looking fix at a
time, and nothing made the growth visible commit by commit. Each shipped `.md`
file carries a word cap at its accepted size. Growing a file past its cap fails
until the same commit raises the cap, so growth is a stated decision with its
reason in the commit message; shrinking well below the cap fails until the cap
is lowered, so the slack cannot be regrown silently later.

Words, not lines: a paragraph is one line in these files, so line counts barely
move as prose grows. The orchestrators' line budget in
`test_orchestrator_structure.py` still applies on top of this.

This repo's CLAUDE.md is capped too: it does not ship, but every session and
every dispatched agent here loads it, and it grows the same way.
"""

import pytest

from conftest import REPO_ROOT, read, shipped_artifacts

# Accepted size of each capped prose file, in whitespace-separated words.
# Raise an entry in the same commit that grows its file, with the growth's
# reason recorded; lower it when the file shrinks.
CAPS = {
    "CLAUDE.md": 4659,
    "skills/quo-breakdown-epic/SKILL.md": 2908,
    "skills/quo-doc-writer-review/SKILL.md": 3139,
    "skills/quo-engineer-review/SKILL.md": 6472,
    "skills/quo-execute/SKILL.md": 13309,
    "skills/quo-execute/references/compromise-tracker.md": 1093,
    "skills/quo-execute/references/context-guard.md": 721,
    "skills/quo-execute/references/post-completion-prompt.md": 1521,
    "skills/quo-execute/references/rationale.md": 2573,
    "skills/quo-execute/references/routing.md": 2994,
    "skills/quo-file-issue/SKILL.md": 7180,
    "skills/quo-fix-issue/SKILL.md": 12588,
    "skills/quo-fix-issue/references/github-close.md": 382,
    "skills/quo-fix-issue/references/url-resolution.md": 525,
    "skills/quo-plan/SKILL.md": 3130,
    "skills/quo-plan-from-specs/SKILL.md": 3236,
    "skills/quo-setup/SKILL.md": 9699,
    "skills/quo-spec-review/SKILL.md": 845,
    "skills/quo-status/SKILL.md": 730,
    "skills/quo-test-writer-review/SKILL.md": 3780,
    "skills/quo-write-prd/SKILL.md": 962,
    "skills/quo-write-sdd/SKILL.md": 1133,
    "agents/analyst.md": 5000,
    "agents/code-reviewer.md": 1309,
    "agents/doc-reviewer.md": 676,
    "agents/doc-writer.md": 3304,
    "agents/engineer.md": 2647,
    "agents/pm.md": 6891,
    "agents/test-reviewer.md": 692,
    "agents/test-writer.md": 3200,
}

# Capped files that do not ship.
NON_SHIPPED = {"CLAUDE.md"}

# How far below its cap a file may sit before the cap must come down. Flat, not
# proportional: a clause-sized fix is 50-200 words, so proportional slack on the
# largest files would leave room for silent regrowth exactly where prose grew most.
SLACK_WORDS = 50


def capped_prose():
    files = {
        p.relative_to(REPO_ROOT).as_posix()
        for p in shipped_artifacts()
        if p.suffix == ".md"
    }
    return files | NON_SHIPPED


def existing_caps():
    return sorted(set(CAPS) & capped_prose())


def word_count(relpath):
    return len(read(relpath).split())


def test_every_capped_prose_file_has_a_cap_and_every_cap_has_a_file():
    files = capped_prose()
    missing = sorted(files - set(CAPS))
    stale = sorted(set(CAPS) - files)
    assert not missing, (
        f"prose file(s) with no size cap: {missing}. Add each to CAPS in "
        "tests/test_prose_size.py at its current word count."
    )
    assert not stale, (
        f"CAPS names file(s) that are no longer shipped or capped: {stale}. "
        "Remove them from CAPS."
    )


@pytest.mark.parametrize("relpath", existing_caps())
def test_prose_file_has_not_grown_past_its_cap(relpath):
    words = word_count(relpath)
    cap = CAPS[relpath]
    assert words <= cap, (
        f"{relpath} grew to {words} words (cap {cap}). First try stating the change "
        "as a goal or cutting something (CLAUDE.md `## How skill prose is written`). "
        "If the growth is deliberate, record why (ticket, reviewer dispatch, or commit "
        f"message) and raise its cap to {words} in this commit."
    )


@pytest.mark.parametrize("relpath", existing_caps())
def test_prose_file_cap_ratchets_down_when_it_shrinks(relpath):
    words = word_count(relpath)
    cap = CAPS[relpath]
    assert cap - words <= SLACK_WORDS, (
        f"{relpath} shrank to {words} words, well below its cap of {cap}. "
        f"Lower its cap to {words} so the reduction is locked in."
    )
