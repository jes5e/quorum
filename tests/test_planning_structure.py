"""Structural invariants of `/quo-plan` and its three sub-skills.

The four bodies were rewritten minimally (ticket b.7ib) from a failure inventory
(`docs/inventory/plan-failures.md`). This module pins what that rewrite committed
to, never a prose sentence:

  (a) a line cap per body, since these bodies once grew 7x one fix at a time;
  (b) no TaskList dependence, because the TaskList tools are off by default;
  (c) gates fronted by a tool call in the gate's turn, and every gate label;
  (d) the output contract `/quo-breakdown-epic` and the PM read;
  (e) the writer inline contract shared by `/quo-plan` and the two writers;
  (f) the two reviewers' finding and verdict lines, and the SDD subsections
      the plan path's reviewers and breakdown key on.
"""

import pytest

from conftest import QUO_PLAN, QUO_SPEC_REVIEW, QUO_WRITE_PRD, QUO_WRITE_SDD, heading_section, read

PLAN = read(QUO_PLAN)
PRD = read(QUO_WRITE_PRD)
SDD = read(QUO_WRITE_SDD)
REVIEW = read(QUO_SPEC_REVIEW)
BODIES = {"quo-plan": PLAN, "quo-write-prd": PRD, "quo-write-sdd": SDD, "quo-spec-review": REVIEW}

# Hard caps. /quo-plan's target is 250 lines; the sub-skills' cap sits well
# above their size so a clause-sized fix fits, and a rewrite-sized one does not.
LINE_CAPS = {"quo-plan": 350, "quo-write-prd": 120, "quo-write-sdd": 120, "quo-spec-review": 120}


def assert_present(anchors, text, where):
    missing = [a for a in anchors if a not in text]
    assert not missing, f"{where} is missing anchor(s): {missing}"


# --- (a) line caps ----------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(BODIES))
def test_body_is_within_its_line_cap(name):
    count = len(BODIES[name].splitlines())
    assert count <= LINE_CAPS[name], f"{name} is {count} lines; cap is {LINE_CAPS[name]}"


# --- (b) no TaskList dependence -----------------------------------------------------


@pytest.mark.parametrize("name", sorted(BODIES))
def test_no_tasklist_dependence(name):
    for token in ["TaskList", "TaskCreate", "TaskUpdate", "gate-askuserquestion", "metadata.activity", "-rev<n>", "defer-<"]:
        assert token not in BODIES[name], f"{name} still carries the TaskList token {token!r}"


def test_spec_review_emits_no_routing_trailer():
    for token in ["Your next tool call MUST", "Your next tool use MUST"]:
        assert token not in REVIEW


# --- (c) gates ----------------------------------------------------------------------


def test_plan_gates_are_manifest_fronted():
    lead = heading_section(PLAN, "## 3. Gates").split("\n\n")[1]
    assert "`## Open gate`" in lead
    assert "`AskUserQuestion` in the same turn" in lead


@pytest.mark.parametrize("body", [PRD, SDD], ids=["quo-write-prd", "quo-write-sdd"])
def test_solo_writer_gate_is_fronted_by_the_body_file_write(body):
    assert "write the current body to a fresh body file and, in the same turn, call `AskUserQuestion`" in body


PLAN_GATE_LABELS = [
    "**Resume**", "**Start fresh**",
    "**Approve**", "**Revise**", "**Cancel**",
    "`Reuse existing Spec Bee`", "`Create a new Spec Bee anyway`",
    "**Approve over blockers**",
    "`Fix in this session`", "`File as issue tickets`", "`Encode in an existing ticket body`",
    "**In a fresh session, break down now** (Recommended)",
    "**In a fresh session, execute now**",
    "**Continue in this session: break down now**",
    "**Continue in this session: execute now**",
    "**Review first**", "**Done for now**",
]


def test_plan_gate_labels_are_verbatim():
    assert_present(PLAN_GATE_LABELS, PLAN, "quo-plan")


@pytest.mark.parametrize("body", [PRD, SDD], ids=["quo-write-prd", "quo-write-sdd"])
def test_solo_writer_gate_labels_are_verbatim(body):
    assert_present(["**Approve**", "**Revise**", "**Cancel**"], body, "writer")


# --- (d) output contract --------------------------------------------------------------

PLAN_ANCHORS = [
    "Run /quo-setup first.",
    "run-state-quo-plan-<repo-dir-name>.md",
    "## Obligations",
    "## Open gate",
    "**Phase:**",
    "`Epic N — <short title>`",
    "`## Anticipated doc impact`",
    '`[{"value":"<spec-bee-id>","resolver":"bees"}]`',
    "`up_dependencies`",
    "`drafted`",
    "`ready`",
    "`PRD`",
    "`SDD`",
    "`Deferral hygiene: no deferred items.`",
    "`## Deferred from /quo-plan run (<YYYY-MM-DD HH:MM>)`",
    "resolve-hive-paths --hive plans --hive specs",
    "`Plan feature: <title> (<plan-bee-id>)`",
    "`Plan stored in bees; no in-repo changes to commit.`",
]


def test_plan_output_contract_anchors_are_present():
    assert_present(PLAN_ANCHORS, PLAN, "quo-plan")


# --- (e) writer inline contract ---------------------------------------------------------


@pytest.mark.parametrize("body", [PLAN, PRD, SDD], ids=["quo-plan", "quo-write-prd", "quo-write-sdd"])
def test_inline_args_shape_is_shared(body):
    assert_present(["spec-bee-id: <spec-bee-id>", "distilled-scope:"], body, "inline args")


def test_writer_return_fields_match_their_reader():
    assert_present(["prd_ticket_id", "prd_status", "action"], PRD, "quo-write-prd")
    assert_present(["sdd_ticket_id", "sdd_status", "action", "research_needed"], SDD, "quo-write-sdd")
    assert_present(["prd_ticket_id", "sdd_ticket_id", "`action`", "`research_needed`"], PLAN, "quo-plan")


@pytest.mark.parametrize("body", [PRD, SDD], ids=["quo-write-prd", "quo-write-sdd"])
def test_writers_accept_findings_on_revise(body):
    assert "findings:" in body


PRD_SECTIONS = [
    "## Problem Statement", "## Goals", "## Non-Goals / Out of Scope", "## Functional Requirements",
    "## Edge Cases and Error Handling", "## Non-Functional Requirements", "## UI/UX Requirements",
    "## Acceptance Criteria", "## Assumptions", "## Open Questions", "## Background and rationale",
    "## Decisions and rejected alternatives",
]
SDD_SECTIONS = [
    "## Codebase exploration findings", "## Requirements", "## Test Fixtures", "## Existing Behavior",
    "## Documentation", "## Background and rationale", "## Decisions and rejected alternatives",
]
SDD_SUBSECTIONS = ["### Mechanism lifecycle", "### Policy decisions this design implies"]


def _in_order(text, items):
    positions = [text.find(f"`{i}`") for i in items]
    return all(p >= 0 for p in positions) and positions == sorted(positions)


def test_prd_sections_are_listed_in_order():
    assert _in_order(PRD, PRD_SECTIONS)


def test_sdd_sections_are_listed_in_order():
    assert _in_order(SDD, SDD_SECTIONS)


# --- (f) reviewer contracts ------------------------------------------------------------


def test_sdd_subsections_are_named_by_their_writer_and_reviewer():
    assert_present([f"`{s}`" for s in SDD_SUBSECTIONS], SDD, "quo-write-sdd")
    assert_present([f"`{s}`" for s in SDD_SUBSECTIONS], REVIEW, "quo-spec-review")


def test_spec_review_output_lines():
    assert_present([
        "## Spec Review Work Items",
        "`No spec issues found.`",
        "`No spec content to review`",
        "`<blocker|suggestion|nit>` target:",
        "[depth:<trivial-tweak|refactor-locally|re-architect>]",
        "[preferred]",
    ], REVIEW, "quo-spec-review")


def test_plan_reviewer_output_lines():
    assert_present([
        "`<blocker|suggestion|nit>` target: <PRD|SDD|Plan-Bee-body|Epic:<N>>",
        "[depth:<trivial-tweak|refactor-locally|re-architect>]",
        "[preferred]",
        "Plan-review verdict: <approve | revise-recommended | escalate-to-user>",
        "`No plan-review issues found.`",
    ], PLAN, "quo-plan")
