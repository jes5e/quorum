"""Unit + CLI-contract tests for scoped_marker_resolver.py."""

import json
import subprocess
import sys

from conftest import SCOPED_MARKER_RESOLVER, load_script, script_path

mod = load_script(SCOPED_MARKER_RESOLVER)
SCRIPT = script_path(SCOPED_MARKER_RESOLVER)


# ---------------------------------------------------------------------------
# find_marker: marker match / malformed / absent discrimination
# ---------------------------------------------------------------------------

def test_find_marker_well_formed():
    body = "intro\nScoped to `### Feature: Widgets` from docs/prd.md and docs/sdd.md.\noutro"
    m, malformed = mod.find_marker(body)
    assert malformed is None
    assert m is not None
    assert m.group("title") == "Widgets"
    assert m.group("prd") == "docs/prd.md"
    assert m.group("sdd") == "docs/sdd.md"


def test_find_marker_leading_whitespace_tolerated():
    body = "   Scoped to `### Feature: X` from a.md and b.md.   "
    m, malformed = mod.find_marker(body)
    assert malformed is None
    assert m is not None
    assert m.group("title") == "X"


def test_find_marker_malformed_backtick_shaped_line():
    # Starts with `Scoped to ` followed by a backtick, but the grammar fails.
    body = "Scoped to `### Feature: only a heading, no from-clause`"
    m, malformed = mod.find_marker(body)
    assert m is None
    assert malformed is not None
    assert malformed.startswith("Scoped to `")


def test_find_marker_absent_prose_not_treated_as_malformed():
    # "Scoped to " without a backtick is prose, not a marker attempt.
    body = "This feature is Scoped to a single deliverable."
    m, malformed = mod.find_marker(body)
    assert m is None
    assert malformed is None


def test_find_marker_no_marker_at_all():
    m, malformed = mod.find_marker("just some\nplain body text\n")
    assert m is None
    assert malformed is None


# ---------------------------------------------------------------------------
# extract_subsection: boundaries
# ---------------------------------------------------------------------------

def test_extract_subsection_runs_to_next_feature_heading():
    doc = (
        "preamble\n"
        "### Feature: Alpha\n"
        "alpha line 1\n"
        "alpha line 2\n"
        "### Feature: Beta\n"
        "beta line\n"
    )
    out = mod.extract_subsection(doc, "Alpha")
    assert out == "alpha line 1\nalpha line 2"


def test_extract_subsection_runs_to_eof_when_last():
    doc = "### Feature: Alpha\nfirst\nsecond"
    out = mod.extract_subsection(doc, "Alpha")
    assert out == "first\nsecond"


def test_extract_subsection_excludes_heading_line():
    doc = "### Feature: Alpha\nbody"
    out = mod.extract_subsection(doc, "Alpha")
    assert "### Feature: Alpha" not in out
    assert out == "body"


def test_extract_subsection_missing_heading_returns_none():
    doc = "### Feature: Alpha\nbody\n"
    assert mod.extract_subsection(doc, "Gamma") is None


def test_extract_subsection_title_match_is_case_sensitive():
    doc = "### Feature: Alpha\nbody\n"
    assert mod.extract_subsection(doc, "alpha") is None


def test_extract_subsection_empty_body_between_adjacent_headings():
    doc = "### Feature: Alpha\n### Feature: Beta\nbeta"
    assert mod.extract_subsection(doc, "Alpha") == ""


# ---------------------------------------------------------------------------
# CLI: unscoped body -> {"scoped": false}, exit 0
# ---------------------------------------------------------------------------

def _run(args, **kw):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        **kw,
    )


def test_cli_unscoped_body(tmp_path):
    body = tmp_path / "bee.md"
    body.write_text("no marker here\n", encoding="utf-8")
    res = _run([str(body)])
    assert res.returncode == 0
    assert json.loads(res.stdout) == {"scoped": False}


def test_cli_scoped_success(tmp_path):
    prd = tmp_path / "prd.md"
    sdd = tmp_path / "sdd.md"
    prd.write_text("### Feature: Widgets\nprd body line\n", encoding="utf-8")
    sdd.write_text("### Feature: Widgets\nsdd body line\n", encoding="utf-8")
    body = tmp_path / "bee.md"
    body.write_text(
        "Scoped to `### Feature: Widgets` from prd.md and sdd.md.\n",
        encoding="utf-8",
    )
    res = _run([str(body), "--repo-root", str(tmp_path)])
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    assert out["scoped"] is True
    assert out["title"] == "Widgets"
    paths = [d["path"] for d in out["docs"]]
    assert str(prd.resolve()) == paths[0]
    assert str(sdd.resolve()) == paths[1]
    assert out["docs"][0]["content"] == "prd body line"
    assert out["docs"][1]["content"] == "sdd body line"


# ---------------------------------------------------------------------------
# CLI: failure exits (exit 2) with a single stderr one-liner
# ---------------------------------------------------------------------------

def test_cli_missing_file_exit2(tmp_path):
    res = _run([str(tmp_path / "does-not-exist.md")])
    assert res.returncode == 2
    assert res.stderr.strip()
    assert "could not read" in res.stderr


def test_cli_malformed_marker_exit2(tmp_path):
    body = tmp_path / "bee.md"
    body.write_text("Scoped to `### Feature: broken without from clause`\n", encoding="utf-8")
    res = _run([str(body)])
    assert res.returncode == 2
    assert "malformed" in res.stderr


def test_cli_empty_title_exit2(tmp_path):
    body = tmp_path / "bee.md"
    # Title is empty/whitespace-only after the prefix.
    body.write_text("Scoped to `### Feature:  ` from a.md and b.md.\n", encoding="utf-8")
    res = _run([str(body), "--repo-root", str(tmp_path)])
    assert res.returncode == 2
    assert "title is empty" in res.stderr


def test_cli_missing_doc_path_exit2(tmp_path):
    body = tmp_path / "bee.md"
    body.write_text(
        "Scoped to `### Feature: X` from nope-prd.md and nope-sdd.md.\n",
        encoding="utf-8",
    )
    res = _run([str(body), "--repo-root", str(tmp_path)])
    assert res.returncode == 2
    assert "do not exist on disk" in res.stderr


def test_cli_missing_heading_exit2(tmp_path):
    prd = tmp_path / "prd.md"
    sdd = tmp_path / "sdd.md"
    prd.write_text("### Feature: Other\nbody\n", encoding="utf-8")
    sdd.write_text("### Feature: Other\nbody\n", encoding="utf-8")
    body = tmp_path / "bee.md"
    body.write_text(
        "Scoped to `### Feature: Missing` from prd.md and sdd.md.\n",
        encoding="utf-8",
    )
    res = _run([str(body), "--repo-root", str(tmp_path)])
    assert res.returncode == 2
    assert "### Feature: Missing" in res.stderr
    assert "not found" in res.stderr


# ---------------------------------------------------------------------------
# The " and " PRD/SDD separator ambiguity
# ---------------------------------------------------------------------------

def test_separator_splits_on_first_and():
    # A path containing " and " before the real separator causes a split on the
    # FIRST occurrence: prd = "a", sdd = "b.md and c.md" (non-greedy prd, greedy-ish sdd).
    body = "Scoped to `### Feature: X` from a and b.md and c.md."
    m, malformed = mod.find_marker(body)
    assert malformed is None
    assert m is not None
    assert m.group("prd") == "a"
    # The remaining text after the first " and " is captured as the sdd group.
    assert m.group("sdd") == "b.md and c.md"


# ---------------------------------------------------------------------------
# UTF-8 BOM handling (read_text with utf-8-sig strips the BOM)
# ---------------------------------------------------------------------------

def test_cli_utf8_bom_on_bee_body(tmp_path):
    prd = tmp_path / "prd.md"
    sdd = tmp_path / "sdd.md"
    prd.write_text("### Feature: Widgets\nprd body\n", encoding="utf-8")
    sdd.write_text("### Feature: Widgets\nsdd body\n", encoding="utf-8")
    body = tmp_path / "bee.md"
    # Write the bee body with a UTF-8 BOM prefix.
    body.write_text(
        "Scoped to `### Feature: Widgets` from prd.md and sdd.md.\n",
        encoding="utf-8-sig",
    )
    res = _run([str(body), "--repo-root", str(tmp_path)])
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    assert out["scoped"] is True
    assert out["title"] == "Widgets"


def test_extract_subsection_bom_via_direct_call():
    # When the doc text still carries a BOM (raw read), the first heading would
    # carry the BOM; utf-8-sig at the read boundary is what strips it. Here we
    # confirm extract_subsection itself matches a clean heading.
    doc = "﻿### Feature: Alpha\nbody"
    # BOM glued onto the first line means the heading does not start with the prefix.
    assert mod.extract_subsection(doc, "Alpha") is None
    # Without the BOM it matches.
    assert mod.extract_subsection(doc.lstrip("﻿"), "Alpha") == "body"
