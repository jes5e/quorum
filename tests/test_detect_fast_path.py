"""Unit + CLI-contract tests for detect_fast_path.py."""

import json
import subprocess
import sys

from conftest import DETECT_FAST_PATH, load_script, script_path

mod = load_script(DETECT_FAST_PATH)
SCRIPT = script_path(DETECT_FAST_PATH)


# ---------------------------------------------------------------------------
# _glob_to_regex
# ---------------------------------------------------------------------------

def test_glob_double_star_matches_zero_or_more_segments():
    pat = mod._glob_to_regex("/repo/**")
    assert pat.match("/repo/")
    assert pat.match("/repo/a/b/c")


def test_glob_single_star_stays_within_segment():
    pat = mod._glob_to_regex("/repo/*.ext")
    assert pat.match("/repo/file.ext")
    assert not pat.match("/repo/sub/file.ext")


def test_glob_question_mark_matches_one_non_slash():
    pat = mod._glob_to_regex("/repo/?")
    assert pat.match("/repo/a")
    assert not pat.match("/repo/")
    assert not pat.match("/repo//")


def test_glob_escapes_regex_metacharacters_literally():
    pat = mod._glob_to_regex("/repo/a.b+c")
    assert pat.match("/repo/a.b+c")
    assert not pat.match("/repo/aXbXc")


# ---------------------------------------------------------------------------
# scope_covers (incl. Windows backslash-separator handling, POSIX-testable)
# ---------------------------------------------------------------------------

def test_scope_covers_forward_slash_double_star(tmp_path):
    scope = str(tmp_path.resolve()) + "/**"
    assert mod.scope_covers(scope, tmp_path)


def test_scope_covers_bare_prefix_no_trailing(tmp_path):
    scope = str(tmp_path.resolve())
    assert mod.scope_covers(scope, tmp_path)


def test_scope_covers_non_matching_scope(tmp_path):
    other = tmp_path / "elsewhere"
    other.mkdir()
    scope = str(other.resolve()) + "/**"
    # repo_root is tmp_path, scope targets a subdir; the bare repo path is not covered.
    assert not mod.scope_covers(scope, tmp_path)


def test_scope_covers_forward_slash_glob_matches_forward_candidate(tmp_path):
    # A forward-slash scope glob matches the forward-separator candidate that
    # scope_covers builds from the resolved repo path. (Renamed from the former
    # test_scope_covers_backslash_separator_form, which despite its name only
    # ever exercised the forward path; the genuine backslash branch is covered
    # by test_scope_covers_backslash_separator_form below.)
    repo_fwd = str(tmp_path.resolve()).replace("\\", "/")
    scope = repo_fwd + "/**"
    assert mod.scope_covers(scope, tmp_path)


def test_scope_covers_backslash_separator_form(tmp_path):
    # Exercise the genuinely Windows-specific branch POSIX-side. The only candidate
    # scope_covers builds that carries a backslash is `repo_str + "\\"` (a trailing
    # backslash on the resolved path); the path body of every candidate keeps its
    # native separators. So the branch is reached by a scope glob whose trailing
    # separator is a backslash: `<repo_str>\**`. _glob_to_regex escapes that `\`
    # to a literal backslash in the regex (the `c in ".^$+(){}[]|\\"` branch), and
    # the `**` becomes `.*`, so the glob matches the `repo_str + "\\"` candidate.
    # NOTE: a fully backslash-separated body (str.replace("/", "\\")) would NOT
    # match POSIX-side, because no candidate has a backslash-separated body.
    scope = str(tmp_path.resolve()) + "\\**"
    assert mod.scope_covers(scope, tmp_path)


def test_scope_covers_invalid_glob_returns_false(monkeypatch, tmp_path):
    # Force _glob_to_regex to raise re.error so the except branch returns False.
    import re

    def boom(_glob):
        raise re.error("boom")

    monkeypatch.setattr(mod, "_glob_to_regex", boom)
    assert mod.scope_covers("anything", tmp_path) is False


# ---------------------------------------------------------------------------
# _split_top_level_sections (fence-aware)
# ---------------------------------------------------------------------------

def test_split_sections_basic():
    text = "## A\nbody a\n## B\nbody b\n"
    sections = mod._split_top_level_sections(text)
    assert set(sections) == {"A", "B"}
    assert "body a" in sections["A"]
    assert "body b" in sections["B"]


def test_split_sections_ignores_headings_inside_fences():
    text = (
        "## Real\n"
        "intro\n"
        "```\n"
        "## NotAHeading inside fence\n"
        "```\n"
        "after fence\n"
        "## Second\n"
        "tail\n"
    )
    sections = mod._split_top_level_sections(text)
    assert set(sections) == {"Real", "Second"}
    assert "## NotAHeading inside fence" in sections["Real"]


def test_split_sections_text_before_first_heading_dropped():
    text = "preamble line\n## Only\nbody\n"
    sections = mod._split_top_level_sections(text)
    assert set(sections) == {"Only"}


# ---------------------------------------------------------------------------
# _parse_keyed_bullets
# ---------------------------------------------------------------------------

def test_parse_keyed_bullets_basic():
    body = "- **Key One**: value one\n- **Key Two**: value two\n"
    result = mod._parse_keyed_bullets(body)
    assert result == {"Key One": "value one", "Key Two": "value two"}


def test_parse_keyed_bullets_empty_value_preserved():
    body = "- **Empty**:\n"
    result = mod._parse_keyed_bullets(body)
    assert result == {"Empty": ""}


def test_parse_keyed_bullets_ignores_non_matching_lines():
    body = "- plain bullet\nsome prose\n- **Key**: v\n"
    result = mod._parse_keyed_bullets(body)
    assert result == {"Key": "v"}


# ---------------------------------------------------------------------------
# fast_path_eligible via inspect_claude_md / main JSON, exercised through the CLI
# ---------------------------------------------------------------------------

def _full_doc_section():
    lines = ["## Documentation Locations"]
    for k in mod.REQUIRED_DOC_KEYS:
        lines.append(f"- **{k}**: somewhere/{k}.md")
    return "\n".join(lines)


def _full_build_section(compile_value="cargo check"):
    lines = ["## Build Commands"]
    for k in mod.REQUIRED_BUILD_KEYS:
        if k == "Compile/type-check":
            lines.append(f"- **{k}**: {compile_value}")
        else:
            lines.append(f"- **{k}**: some command")
    return "\n".join(lines)


def _make_repo_with_hives(tmp_path, hive_names):
    repo = tmp_path / "repo"
    repo.mkdir()
    bees = repo / ".bees"
    bees.mkdir()
    for name in hive_names:
        hive_dir = bees / name
        (hive_dir / ".hive").mkdir(parents=True)
        marker = hive_dir / ".hive" / "identity.json"
        marker.write_text(json.dumps({"normalized_name": name}), encoding="utf-8")
    return repo


def _write_claude(repo, doc_section, build_section):
    (repo / "CLAUDE.md").write_text(
        doc_section + "\n\n" + build_section + "\n", encoding="utf-8"
    )


def _run_cli(repo, fake_home):
    # Point HOME at an empty dir so load_bees_config returns {} (no registration).
    import os

    env = dict(os.environ)
    env["HOME"] = str(fake_home)
    env["USERPROFILE"] = str(fake_home)
    res = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(repo)],
        capture_output=True,
        text=True,
        env=env,
    )
    return res


def test_fast_path_eligible_true_when_all_conditions_met(tmp_path):
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs"])
    _write_claude(repo, _full_doc_section(), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    assert out["fast_path_eligible"] is True
    assert out["on_disk_hive_names_superset_of_canonical"] is True
    assert out["claude_md_doc_locations_set_up"] is True
    assert out["claude_md_build_commands_set_up"] is True


def test_registration_gate_blocks_eligibility(tmp_path):
    # All other conditions are met (canonical hives on disk, CLAUDE.md populated),
    # but ~/.bees/config.json registers a scope that covers the repo. The
    # registration gate (any_registered_for_repo True) must force eligibility False.
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs"])
    _write_claude(repo, _full_doc_section(), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    # Config shape per load_bees_config / find_repo_registration: a top-level
    # "scopes" dict keyed by scope glob, each value a dict with a "hives" dict.
    bees_dir = fake_home / ".bees"
    bees_dir.mkdir()
    scope_glob = str(repo.resolve()) + "/**"
    config = {"scopes": {scope_glob: {"hives": {"issues": {}, "plans": {}}}}}
    (bees_dir / "config.json").write_text(json.dumps(config), encoding="utf-8")
    res = _run_cli(repo, fake_home)
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
    assert out["any_registered_for_repo"] is True
    assert sorted(out["registered_hive_names"]) == ["issues", "plans"]
    # Every non-registration precondition is satisfied, so this proves the gate.
    assert out["on_disk_hive_names_superset_of_canonical"] is True
    assert out["claude_md_doc_locations_set_up"] is True
    assert out["claude_md_build_commands_set_up"] is True
    assert out["fast_path_eligible"] is False


def test_superset_not_subset_rule_strict_subset_falls_through(tmp_path):
    # Only issues + plans on disk: a strict subset of the canonical set.
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans"])
    _write_claude(repo, _full_doc_section(), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["on_disk_hive_names_superset_of_canonical"] is False
    assert out["fast_path_eligible"] is False


def test_proper_superset_still_eligible(tmp_path):
    # The canonical three plus an extra hive is a (non-strict) superset -> eligible.
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs", "extra"])
    _write_claude(repo, _full_doc_section(), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["on_disk_hive_names_superset_of_canonical"] is True
    assert out["fast_path_eligible"] is True


def test_empty_compile_type_check_is_allowed(tmp_path):
    # Compile/type-check is the only build key allowed to be empty.
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs"])
    _write_claude(repo, _full_doc_section(), _full_build_section(compile_value=""))
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["claude_md_build_commands_set_up"] is True
    assert out["fast_path_eligible"] is True


def test_empty_non_exempt_build_key_blocks_eligibility(tmp_path):
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs"])
    # Empty the Lint key (not exempt) -> build commands not set up.
    build = "\n".join(
        [
            "## Build Commands",
            "- **Compile/type-check**: cargo check",
            "- **Format**: fmt",
            "- **Lint**:",
            "- **Narrow test**: t",
            "- **Full test**: t",
        ]
    )
    _write_claude(repo, _full_doc_section(), build)
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["claude_md_build_commands_set_up"] is False
    assert out["fast_path_eligible"] is False


def test_missing_doc_key_blocks_eligibility(tmp_path):
    repo = _make_repo_with_hives(tmp_path, ["issues", "plans", "specs"])
    # Drop one required doc key.
    doc_lines = ["## Documentation Locations"]
    for k in mod.REQUIRED_DOC_KEYS[:-1]:
        doc_lines.append(f"- **{k}**: x")
    _write_claude(repo, "\n".join(doc_lines), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["claude_md_doc_locations_set_up"] is False
    assert out["fast_path_eligible"] is False


def test_no_on_disk_hives_not_eligible(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_claude(repo, _full_doc_section(), _full_build_section())
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    res = _run_cli(repo, fake_home)
    out = json.loads(res.stdout)
    assert out["on_disk_hives"] == []
    assert out["fast_path_eligible"] is False


def test_cli_nonexistent_repo_root_exit1(tmp_path):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    missing = tmp_path / "nope"
    import os

    env = dict(os.environ)
    env["HOME"] = str(fake_home)
    res = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(missing)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert res.returncode == 1
    assert "not a directory" in res.stderr
