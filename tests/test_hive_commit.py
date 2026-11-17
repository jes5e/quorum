"""Unit + CLI-contract tests for hive_commit.py.

Mutating paths run against a throwaway git repo in tmp_path with a fake `bees`
executable on PATH that prints canned `list-hives` JSON.
"""

import json
import os
import stat
import subprocess
import sys

from conftest import HIVE_COMMIT, load_script, script_path

mod = load_script(HIVE_COMMIT)
SCRIPT = script_path(HIVE_COMMIT)


# ---------------------------------------------------------------------------
# resolve_hive_paths JSON parsing: in-process via monkeypatched subprocess.run
# ---------------------------------------------------------------------------

class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_resolve_hive_paths_happy(monkeypatch):
    payload = {
        "hives": [
            {"normalized_name": "plans", "path": "/repo/.bees/plans"},
            {"normalized_name": "issues", "path": "/repo/.bees/issues"},
            {"normalized_name": "specs", "path": "/repo/.bees/specs"},
            {"normalized_name": "other", "path": "/repo/.bees/other"},
        ]
    }

    def fake_run(cmd, **kw):
        assert cmd == ["bees", "list-hives"]
        return _FakeCompleted(stdout=json.dumps(payload))

    monkeypatch.setattr(mod.subprocess, "run", fake_run)
    paths = mod.resolve_hive_paths()
    assert paths is not None
    names = {p.name for p in paths}
    # Only the three canonical hive names are kept; "other" is filtered out.
    assert names == {"plans", "issues", "specs"}


def test_resolve_hive_paths_filter_by_name(monkeypatch):
    payload = {
        "hives": [
            {"normalized_name": "plans", "path": "/repo/.bees/plans"},
            {"normalized_name": "issues", "path": "/repo/.bees/issues"},
        ]
    }
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _FakeCompleted(stdout=json.dumps(payload))
    )
    paths = mod.resolve_hive_paths(names=["plans"])
    assert [p.name for p in paths] == ["plans"]


def test_resolve_hive_paths_malformed_json_returns_none(monkeypatch):
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _FakeCompleted(stdout="{not json")
    )
    assert mod.resolve_hive_paths() is None


def test_resolve_hive_paths_nonzero_exit_returns_none(monkeypatch):
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _FakeCompleted(returncode=1, stdout="{}")
    )
    assert mod.resolve_hive_paths() is None


def test_resolve_hive_paths_missing_binary_returns_none(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError("bees not found")

    monkeypatch.setattr(mod.subprocess, "run", boom)
    assert mod.resolve_hive_paths() is None


def test_resolve_hive_paths_hives_not_a_list_returns_none(monkeypatch):
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _FakeCompleted(stdout=json.dumps({"hives": {}}))
    )
    assert mod.resolve_hive_paths() is None


# ---------------------------------------------------------------------------
# CLI-level: temp git repo + stub bees on PATH
# ---------------------------------------------------------------------------

def _init_git_repo(path):
    subprocess.run(["git", "init"], cwd=path, capture_output=True, text=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True,
                   capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True,
                   capture_output=True, text=True)


def _write_stub_bees(bin_dir, hives_json):
    """Write a fake `bees` executable that prints canned list-hives JSON to stdout."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    stub = bin_dir / "bees"
    # A tiny Python shim is cross-process portable; it ignores its args and emits JSON.
    stub.write_text(
        "#!" + sys.executable + "\n"
        "import sys\n"
        "sys.stdout.write(" + repr(hives_json) + ")\n",
        encoding="utf-8",
    )
    st = os.stat(stub)
    os.chmod(stub, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return stub


def _env_with_bin(bin_dir):
    env = dict(os.environ)
    env["PATH"] = str(bin_dir) + os.pathsep + env.get("PATH", "")
    return env


def _run_cli(args, cwd, env):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env,
    )


def _setup_repo_with_hive(tmp_path, hive_name="plans"):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    hive_dir = repo / ".bees" / hive_name
    hive_dir.mkdir(parents=True)
    hives_json = json.dumps(
        {"hives": [{"normalized_name": hive_name, "path": str(hive_dir.resolve())}]}
    )
    bin_dir = tmp_path / "bin"
    _write_stub_bees(bin_dir, hives_json)
    env = _env_with_bin(bin_dir)
    return repo, hive_dir, env


def test_encode_commit_creates_commit_with_exact_subject(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    # Stage-worthy change inside the hive dir.
    (hive_dir / "ticket.md").write_text("new ticket body\n", encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "3"], repo, env)
    assert res.returncode == 0, res.stderr
    # Exact commit subject including the Unicode em-dash; assert byte-for-byte.
    log = subprocess.run(
        ["git", "log", "-1", "--format=%s"], cwd=str(repo), capture_output=True, text=True
    )
    expected = "Encode deferral: /quo-execute — 3 deferral(s) encoded"
    assert log.stdout.strip() == expected
    # Sanity: the em-dash is present, not a hyphen.
    assert "—" in log.stdout


def test_encode_commit_bare_invocation_accepted(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    (hive_dir / "ticket.md").write_text("body\n", encoding="utf-8")
    # No "encode-commit" subcommand — bare --skill/--count.
    res = _run_cli(["--skill", "quo-fix-issue", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    log = subprocess.run(
        ["git", "log", "-1", "--format=%s"], cwd=str(repo), capture_output=True, text=True
    )
    assert log.stdout.strip() == "Encode deferral: /quo-fix-issue — 1 deferral(s) encoded"


def test_encode_commit_no_empty_commit_when_nothing_staged(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    # No changes inside the hive dir -> nothing staged.
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "0"], repo, env)
    assert res.returncode == 0, res.stderr
    assert "skipped: nothing staged" in res.stdout
    # No commit was created.
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=str(repo), capture_output=True, text=True
    )
    assert log.returncode != 0 or log.stdout.strip() == ""


def test_encode_commit_does_not_git_add_all(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    # Change inside the hive (should be committed)...
    (hive_dir / "ticket.md").write_text("body\n", encoding="utf-8")
    # ...and an unrelated file in the working tree (must NOT be swept in).
    stray = repo / "stray.txt"
    stray.write_text("do not commit me\n", encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    # The stray file remains untracked (would be tracked if `git add -A` ran).
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(repo), capture_output=True, text=True
    )
    assert "?? stray.txt" in status.stdout
    # And it is not in the committed tree.
    show = subprocess.run(
        ["git", "show", "--name-only", "--format=", "HEAD"],
        cwd=str(repo), capture_output=True, text=True,
    )
    assert "stray.txt" not in show.stdout
    assert "ticket.md" in show.stdout


def test_encode_commit_unknown_skill_exit2(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    res = _run_cli(["encode-commit", "--skill", "bogus", "--count", "1"], repo, env)
    assert res.returncode == 2
    assert "unknown --skill" in res.stderr


def test_encode_commit_missing_required_args_exit2(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    res = _run_cli(["encode-commit", "--skill", "quo-execute"], repo, env)
    assert res.returncode == 2
    assert "requires --skill and --count" in res.stderr


# ---------------------------------------------------------------------------
# A hive's `.hive/` configuration is never staged (encode-commit and stage)
# ---------------------------------------------------------------------------

def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True, text=True)


def _setup_tracked_hives(tmp_path, tickets, outside=()):
    """A repo whose hives each track `.hive/identity.json` and the given ticket files.

    `tickets` maps a hive name to ticket file paths relative to that hive. Hives
    named in `outside` live outside the repo and are not committed.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    hives = {}
    for name, files in tickets.items():
        root = (tmp_path / "outside" if name in outside else repo / ".bees") / name
        (root / ".hive").mkdir(parents=True)
        (root / ".hive" / "identity.json").write_text('{"hive": "%s"}\n' % name, encoding="utf-8")
        for rel in files:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text("body\n", encoding="utf-8")
        hives[name] = root.resolve()
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", "base")
    hives_json = json.dumps(
        {"hives": [{"normalized_name": n, "path": str(p)} for n, p in hives.items()]}
    )
    bin_dir = tmp_path / "bin"
    _write_stub_bees(bin_dir, hives_json)
    return repo, hives, _env_with_bin(bin_dir)


def _committed_files(repo):
    return _git(repo, "show", "--name-only", "--format=", "HEAD").stdout.split()


def test_encode_commit_never_stages_hive_configuration(tmp_path):
    # Role-play (a): a modified Specs identity file and one encoded Plans ticket.
    repo, hives, env = _setup_tracked_hives(
        tmp_path, {"plans": ["b.aaa/b.aaa.md"], "specs": ["b.sss/b.sss.md"]}
    )
    (hives["specs"] / ".hive" / "identity.json").write_text('{"local": true}\n', encoding="utf-8")
    (hives["plans"] / "b.aaa" / "b.aaa.md").write_text("encoded\n", encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    assert _git(repo, "log", "-1", "--format=%s").stdout.strip() == (
        "Encode deferral: /quo-execute — 1 deferral(s) encoded"
    )
    assert _committed_files(repo) == [".bees/plans/b.aaa/b.aaa.md"]
    assert " M .bees/specs/.hive/identity.json" in _git(repo, "status", "--porcelain").stdout


def test_encode_commit_skips_when_only_hive_configuration_changed(tmp_path):
    repo, hives, env = _setup_tracked_hives(tmp_path, {"plans": ["b.aaa/b.aaa.md"]})
    (hives["plans"] / ".hive" / "identity.json").write_text('{"local": true}\n', encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-fix-issue", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    assert "skipped: nothing staged" in res.stdout
    assert _git(repo, "log", "-1", "--format=%s").stdout.strip() == "base"


def test_encode_commit_tolerates_a_hive_holding_only_its_configuration(tmp_path):
    # A freshly colonized hive has no ticket yet; its pathspec matches only `.hive/`.
    repo, hives, env = _setup_tracked_hives(tmp_path, {"plans": ["b.aaa/b.aaa.md"], "issues": []})
    (hives["plans"] / "b.aaa" / "b.aaa.md").write_text("encoded\n", encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    assert _committed_files(repo) == [".bees/plans/b.aaa/b.aaa.md"]


def test_encode_commit_out_of_repo_hive_stages_nothing(tmp_path):
    # Role-play (b), encode side.
    repo, hives, env = _setup_tracked_hives(tmp_path, {"plans": ["b.aaa/b.aaa.md"]}, outside={"plans"})
    (hives["plans"] / "b.aaa" / "b.aaa.md").write_text("encoded\n", encoding="utf-8")
    res = _run_cli(["encode-commit", "--skill", "quo-execute", "--count", "1"], repo, env)
    assert res.returncode == 0, res.stderr
    assert "skipped: nothing staged" in res.stdout


# ---------------------------------------------------------------------------
# stage mode: stages whole in-repo hives except `.hive/`, never commits
# ---------------------------------------------------------------------------

def test_stage_mode_stages_every_bee_in_the_hive_but_not_its_configuration(tmp_path):
    # Role-play (e): a Task under one Bee writes into a Task under another Bee.
    repo, hives, env = _setup_tracked_hives(
        tmp_path,
        {"plans": ["b.aaa/t1.aaa.e1/t2.aaa.e1.t1/t2.aaa.e1.t1.md",
                   "b.bbb/t1.bbb.e1/t2.bbb.e1.t1/t2.bbb.e1.t1.md",
                   "b.ccc/b.ccc.md"]},
    )
    plans = hives["plans"]
    (plans / "b.aaa/t1.aaa.e1/t2.aaa.e1.t1/t2.aaa.e1.t1.md").write_text("done\n", encoding="utf-8")
    (plans / "b.bbb/t1.bbb.e1/t2.bbb.e1.t1/t2.bbb.e1.t1.md").write_text("decision\n", encoding="utf-8")
    (plans / "b.ccc/b.ccc.md").unlink()
    (plans / ".hive" / "identity.json").write_text('{"local": true}\n', encoding="utf-8")
    res = _run_cli(["stage", "--hive", "plans"], repo, env)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip().splitlines() == [str(plans)]
    staged = _git(repo, "diff", "--cached", "--name-only").stdout.split()
    assert sorted(staged) == [
        ".bees/plans/b.aaa/t1.aaa.e1/t2.aaa.e1.t1/t2.aaa.e1.t1.md",
        ".bees/plans/b.bbb/t1.bbb.e1/t2.bbb.e1.t1/t2.bbb.e1.t1.md",
        ".bees/plans/b.ccc/b.ccc.md",
    ]
    # Stage mode never commits.
    assert _git(repo, "log", "-1", "--format=%s").stdout.strip() == "base"


def test_stage_mode_stages_only_the_named_hives(tmp_path):
    repo, hives, env = _setup_tracked_hives(
        tmp_path, {"plans": ["b.aaa/b.aaa.md"], "issues": ["b.iii/b.iii.md"]}
    )
    (hives["plans"] / "b.aaa" / "b.aaa.md").write_text("x\n", encoding="utf-8")
    (hives["issues"] / "b.iii" / "b.iii.md").write_text("x\n", encoding="utf-8")
    res = _run_cli(["stage", "--hive", "plans"], repo, env)
    assert res.returncode == 0, res.stderr
    assert _git(repo, "diff", "--cached", "--name-only").stdout.split() == [".bees/plans/b.aaa/b.aaa.md"]


def test_stage_mode_out_of_repo_hive_prints_and_stages_nothing(tmp_path):
    # Role-play (b), stage side.
    repo, hives, env = _setup_tracked_hives(tmp_path, {"plans": ["b.aaa/b.aaa.md"]}, outside={"plans"})
    (hives["plans"] / "b.aaa" / "b.aaa.md").write_text("x\n", encoding="utf-8")
    res = _run_cli(["stage", "--hive", "plans"], repo, env)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == ""
    assert _git(repo, "diff", "--cached", "--name-only").stdout.strip() == ""


# ---------------------------------------------------------------------------
# resolve-hive-paths mode: NON-MUTATING query
# ---------------------------------------------------------------------------

def test_resolve_hive_paths_mode_prints_in_repo_path(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    res = _run_cli(["resolve-hive-paths"], repo, env)
    assert res.returncode == 0, res.stderr
    assert str(hive_dir.resolve()) in res.stdout.strip().splitlines()


def test_resolve_hive_paths_mode_is_non_mutating(tmp_path):
    repo, hive_dir, env = _setup_repo_with_hive(tmp_path)
    # Establish a baseline status (a stray untracked file to make status non-empty).
    (repo / "stray.txt").write_text("x\n", encoding="utf-8")
    before = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(repo), capture_output=True, text=True
    ).stdout
    res = _run_cli(["resolve-hive-paths"], repo, env)
    assert res.returncode == 0, res.stderr
    after = subprocess.run(
        ["git", "status", "--porcelain"], cwd=str(repo), capture_output=True, text=True
    ).stdout
    assert before == after
    # No commit exists (no git log).
    log = subprocess.run(
        ["git", "log", "--oneline"], cwd=str(repo), capture_output=True, text=True
    )
    assert log.returncode != 0 or log.stdout.strip() == ""


def test_resolve_hive_paths_mode_filters_by_hive(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    plans = repo / ".bees" / "plans"
    issues = repo / ".bees" / "issues"
    plans.mkdir(parents=True)
    issues.mkdir(parents=True)
    hives_json = json.dumps(
        {
            "hives": [
                {"normalized_name": "plans", "path": str(plans.resolve())},
                {"normalized_name": "issues", "path": str(issues.resolve())},
            ]
        }
    )
    bin_dir = tmp_path / "bin"
    _write_stub_bees(bin_dir, hives_json)
    env = _env_with_bin(bin_dir)
    res = _run_cli(["resolve-hive-paths", "--hive", "plans"], repo, env)
    assert res.returncode == 0, res.stderr
    lines = res.stdout.strip().splitlines()
    assert str(plans.resolve()) in lines
    assert str(issues.resolve()) not in lines


def test_resolve_hive_paths_mode_out_of_repo_prints_nothing(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    # Hive path lives OUTSIDE the repo.
    outside = tmp_path / "outside" / "plans"
    outside.mkdir(parents=True)
    hives_json = json.dumps(
        {"hives": [{"normalized_name": "plans", "path": str(outside.resolve())}]}
    )
    bin_dir = tmp_path / "bin"
    _write_stub_bees(bin_dir, hives_json)
    env = _env_with_bin(bin_dir)
    res = _run_cli(["resolve-hive-paths"], repo, env)
    assert res.returncode == 0, res.stderr
    assert res.stdout.strip() == ""


def test_resolve_hive_paths_mode_bees_failure_exit2(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_git_repo(repo)
    # Stub bees that exits non-zero.
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    stub = bin_dir / "bees"
    stub.write_text("#!" + sys.executable + "\nimport sys\nsys.exit(1)\n", encoding="utf-8")
    st = os.stat(stub)
    os.chmod(stub, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    env = _env_with_bin(bin_dir)
    res = _run_cli(["resolve-hive-paths"], repo, env)
    assert res.returncode == 2
    assert "could not resolve hive paths" in res.stderr
