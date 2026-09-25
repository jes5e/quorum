"""Structural invariants of `/quo-breakdown-epic`.

The body was rewritten minimally (ticket b.pcc) from a failure inventory
(`docs/inventory/breakdown-failures.md`). This module pins what that rewrite
committed to, never a prose sentence:

  (a) a line cap, since the body once grew 6x one fix at a time;
  (b) no TaskList dependence, because the TaskList tools are off by default;
  (c) gates fronted by a tool call in the gate's turn, and every gate label;
  (d) the output contract `/quo-execute` and the PM read;
  (e) the deferral-hygiene labels shared by the four skills that carry the gate.
"""

import pytest

from conftest import (
    QUO_BREAKDOWN_EPIC,
    QUO_EXECUTE,
    QUO_FIX_ISSUE,
    QUO_PLAN,
    REPO_ROOT,
    heading_section,
    read,
)

BODY = read(QUO_BREAKDOWN_EPIC)

# Target 250 lines; the cap leaves room for a clause-sized fix, not a rewrite-sized one.
LINE_CAP = 350


def assert_present(anchors, text, where):
    missing = [a for a in anchors if a not in text]
    assert not missing, f"{where} is missing anchor(s): {missing}"


# --- (a) line cap ---------------------------------------------------------------------


def test_body_is_within_its_line_cap():
    count = len(BODY.splitlines())
    assert count <= LINE_CAP, f"quo-breakdown-epic is {count} lines; cap is {LINE_CAP}"


# --- (b) no TaskList dependence ---------------------------------------------------------


def test_no_tasklist_dependence():
    for token in ["TaskList", "TaskCreate", "TaskUpdate", "gate-askuserquestion", "metadata.activity", "defer-<"]:
        assert token not in BODY, f"quo-breakdown-epic still carries the TaskList token {token!r}"


# --- (c) gates ------------------------------------------------------------------------------


def test_gates_are_manifest_fronted():
    lead = heading_section(BODY, "## 3. Gates").split("\n\n")[1]
    assert "`## Open gate`" in lead
    assert "`AskUserQuestion` in the same turn" in lead


GATE_LABELS = [
    "**Proceed anyway**", "**Let me change it first**",
    "`How should this run handle multiple Epics? (You will not be asked again this run.)`",
    "**Stop after each Epic**", "**Work through all Epics**",
    "`Fix in this session`", "`File as issue tickets`", "`Encode in existing ticket`",
    "**Execute in fresh session**", "**Next Epic, fresh session**",
    "**Next Epic, this session**", "**Done for now**",
]


def test_gate_labels_are_verbatim():
    assert_present(GATE_LABELS, BODY, "quo-breakdown-epic")


def _next_steps_choices():
    after = heading_section(BODY, "## 9. End of run").split("Fire the next-steps gate", 1)[1]
    return [line for line in after.splitlines() if line.startswith("- **")]


def test_next_steps_gate_fits_one_askuserquestion():
    # AskUserQuestion takes 2-4 options per question; a longer list cannot be asked as written.
    assert 2 <= len(_next_steps_choices()) <= 4


def test_next_steps_labels_are_five_words_or_fewer():
    for line in _next_steps_choices():
        label = line.split("**")[1]
        assert len(label.split()) <= 5, label


# --- (d) output contract ------------------------------------------------------------------

OUTPUT_ANCHORS = [
    "Run /quo-setup first.",
    "Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.",
    "`## Documentation Locations`",
    "`## Build Commands`",
    "run-state-quo-breakdown-epic-<bee-id>.md",
    "## Obligations",
    "## Open gate",
    "Task N — <short title>",
    "`up_dependencies`",
    "`drafted`",
    "`ready`",
    "`PRD`",
    "`SDD`",
    "`## Sites`",
    "`### Mechanism lifecycle`",
    "`### Policy decisions this design implies`",
    "## Context",
    "## What Needs to Change",
    "## Key Files",
    "## Acceptance Criteria",
    "`## Anticipated doc impact`",
    "scripts/scoped_marker_resolver.py",
    "<scoped-marker-resolver-path>",
    "| Spec Requirement | Source | Covered By Subtask | Status |",
    "`OK`",
    "`GAP`",
    "addressed-now",
    "defer-to-existing-ticket-body: <ticket-id>",
    "defer-to-new-Issue",
    "resolve-hive-paths --hive plans",
    "`Plan <bee-id>, Break down <epic-title> (<epic-id>)`",
    "`Deferral hygiene: no deferred items.`",
    "`## Deferred from /quo-breakdown-epic run (<YYYY-MM-DD HH:MM>)`",
    "--skill quo-breakdown-epic --count <N>",
    "CLAUDE_EFFORT",
    "CLAUDE_CODE_SESSION_ID",
    "stop-threshold",
    "read --session-id <trimmed-id>",
    "`no-reading`",
    "`stale`",
    "`missing`",
]


def test_output_contract_anchors_are_present():
    assert_present(OUTPUT_ANCHORS, BODY, "quo-breakdown-epic")


ROLE_TAGS = ["engineer", "test-writer", "doc-writer"]


def test_role_tags_name_dispatchable_roles():
    # `/quo-execute` dispatches by the tag, so each must be an installed role name.
    tags = heading_section(BODY, "## 6. Draft the Tasks and Subtasks")
    for tag in ROLE_TAGS:
        assert f"`{tag}`" in tags, tag
        assert (REPO_ROOT / "agents" / f"{tag}.md").is_file(), tag


def test_missing_reading_gate_is_gone():
    for token in ["**Configure now**", "context-guard-opt-out", "write-opt-out"]:
        assert token not in BODY, f"quo-breakdown-epic still carries {token!r}"


# --- (e) deferral-hygiene labels shared across four skills --------------------------------

HYGIENE_LABELS = ["`Fix in this session`", "`File as issue tickets`", "`Encode in existing ticket`"]


@pytest.mark.parametrize("skill", [QUO_PLAN, QUO_EXECUTE, QUO_FIX_ISSUE, QUO_BREAKDOWN_EPIC])
def test_deferral_hygiene_labels_match_across_skills(skill):
    text = read(skill)
    assert_present(HYGIENE_LABELS, text, skill)
    assert "Encode in an existing ticket body" not in text, f"{skill} keeps the retired six-word label"
