"""Unit + CLI-contract tests for ticket_bodies.py.

The ticket store is faked in-process by monkeypatching `subprocess.run`, and
in the CLI test by a fake `bees` executable on PATH that serves canned
`show-ticket` JSON. Output goes to a temp directory, never the real one.
"""

import json
import os
import stat
import subprocess
import sys

import pytest

from conftest import TICKET_BODIES, load_script, script_path

mod = load_script(TICKET_BODIES)
SCRIPT = script_path(TICKET_BODIES)

EPIC_BODY = (
    "## Description\n\nEpic prose.\n\n"
    "## Epic-wide contracts\n\n### S1 — re-grep\n\n- `snake_case_ident` stays.\n"
    "```text\n## not a heading inside a fence\n```\n\n"
    "## Scope\n\nnot relayed\n"
)

TICKETS = {
    "t2.a": {"ticket_id": "t2.a", "title": "Task A", "body": "Task body — `Ident_1`.\n",
             "parent": "t1.e", "children": ["t3.d", "t3.w", "t3.e"], "tags": []},
    "t3.d": {"ticket_id": "t3.d", "title": "second engineer", "body": "D body\n",
             "tags": ["engineer"], "up_dependencies": ["t3.e"]},
    "t3.w": {"ticket_id": "t3.w", "title": "docs", "body": "W body\n",
             "tags": ["doc-writer"], "up_dependencies": []},
    "t3.e": {"ticket_id": "t3.e", "title": "first engineer", "body": "E body\n",
             "tags": ["engineer"], "up_dependencies": []},
    "t1.e": {"ticket_id": "t1.e", "title": "Epic", "body": EPIC_BODY, "children": ["t2.a"]},
}


class _Done:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def _serve(tickets):
    def run(cmd, **kw):
        assert cmd[:3] == ["bees", "show-ticket", "--ids"]
        ids = cmd[3:]
        found = [tickets[i] for i in ids if i in tickets]
        missing = [i for i in ids if i not in tickets]
        return _Done(stdout=json.dumps({"status": "success", "tickets": found, "not_found": missing}))
    return run


@pytest.fixture
def store(monkeypatch, tmp_path):
    monkeypatch.setattr(mod.subprocess, "run", _serve(TICKETS))
    monkeypatch.setattr(mod.tempfile, "gettempdir", lambda: str(tmp_path))
    return tmp_path


def _run(capsys, *argv):
    code = mod.main(list(argv))
    out = capsys.readouterr()
    return code, out.out.strip(), out.err.strip()


def test_engineer_file_holds_task_own_subtasks_in_dependency_order_and_contracts(store, capsys):
    code, out, _ = _run(capsys, "--task", "t2.a", "--role", "engineer")
    assert code == 0
    path = store / ".quorum" / os.path.basename(out)
    assert out == str(path) and path.name.startswith("bodies-t2.a-engineer-")
    text = path.read_text(encoding="utf-8")
    assert text.index("Task body — `Ident_1`.") < text.index("E body") < text.index("D body")
    assert "W body" not in text
    assert "### S1 — re-grep" in text and "`snake_case_ident` stays." in text
    assert "## not a heading inside a fence" in text
    assert "not relayed" not in text and "Epic prose." not in text


def test_bodies_are_copied_byte_for_byte(store, capsys):
    _, out, _ = _run(capsys, "--task", "t2.a", "--role", "engineer")
    text = open(out, encoding="utf-8", newline="").read()
    for tid in ("t2.a", "t3.e", "t3.d"):
        assert TICKETS[tid]["body"] in text


def test_each_run_writes_a_new_file(store, capsys):
    _, first, _ = _run(capsys, "--task", "t2.a", "--role", "doc-writer")
    _, second, _ = _run(capsys, "--task", "t2.a", "--role", "doc-writer")
    assert first != second
    assert os.path.exists(first) and os.path.exists(second)


def test_epic_without_contracts_section_says_so(monkeypatch, store, capsys):
    tickets = dict(TICKETS, **{"t1.e": dict(TICKETS["t1.e"], body="## Description\n\nno contracts\n")})
    monkeypatch.setattr(mod.subprocess, "run", _serve(tickets))
    _, out, _ = _run(capsys, "--task", "t2.a", "--role", "engineer")
    assert "The Epic has no `## Epic-wide contracts` section." in open(out, encoding="utf-8").read()


def test_contracts_heading_must_match_exactly():
    assert mod.contracts_section("## Epic-wide contracts (old)\n\nx\n") is None
    assert mod.contracts_section("## Epic-wide contracts\nx\n# Top\ny\n") == "## Epic-wide contracts\nx\n"
    assert mod.contracts_section("## Epic-wide contracts\nx\n### keep\ny\n") == "## Epic-wide contracts\nx\n### keep\ny\n"


def test_dependency_cycle_keeps_input_order():
    a = {"ticket_id": "a", "up_dependencies": ["b"]}
    b = {"ticket_id": "b", "up_dependencies": ["a"]}
    assert [s["ticket_id"] for s in mod.dependency_order([a, b])] == ["a", "b"]


def test_missing_ticket_fails_with_one_line_and_no_file(store, capsys):
    code, out, err = _run(capsys, "--task", "t2.nope", "--role", "engineer")
    assert code == 2 and out == "" and "t2.nope" in err and "\n" not in err
    assert not (store / ".quorum").exists()


def test_store_failure_fails_with_one_line(monkeypatch, store, capsys):
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _Done(returncode=1, stderr="boom\nsecond line\n"))
    code, _, err = _run(capsys, "--task", "t2.a", "--role", "engineer")
    assert code == 2 and "boom second line" in err and "\n" not in err


def test_unwritable_scratch_dir_fails_with_one_line(monkeypatch, store, capsys):
    blocker = store / "not-a-dir"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setattr(mod.tempfile, "gettempdir", lambda: str(blocker))
    code, out, err = _run(capsys, "--task", "t2.a", "--role", "engineer")
    assert code == 2 and out == "" and err.startswith("could not write the bodies file") and "\n" not in err


def test_unknown_role_is_refused(store, capsys):
    code, _, _ = _run(capsys, "--task", "t2.a", "--role", "pm")
    assert code == 2


@pytest.mark.skipif(sys.platform == "win32", reason="fake executable is a POSIX script")
def test_cli_end_to_end_with_fake_store(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    fake = bindir / "bees"
    fake.write_text(
        "#!" + sys.executable + "\n"
        "import json, sys\n"
        f"T = json.loads({json.dumps(json.dumps(TICKETS))})\n"
        "ids = sys.argv[3:]\n"
        "print(json.dumps({'tickets': [T[i] for i in ids if i in T]}))\n",
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ["PATH"], TMPDIR=str(tmp_path))
    result = subprocess.run([sys.executable, str(SCRIPT), "--task", "t2.a", "--role", "doc-writer"],
                            capture_output=True, text=True, env=env)
    assert result.returncode == 0, result.stderr
    text = open(result.stdout.strip(), encoding="utf-8").read()
    assert "W body" in text and "E body" not in text
