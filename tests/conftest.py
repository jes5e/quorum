"""Shared pytest fixtures and the import-by-path helper for the helper-script suite.

The scripts under test are single-file CLIs living under `skills/<name>/scripts/`,
not an importable package. `load_script` centralizes the importlib dance so each test
module can get the module object with one call and unit-test its pure functions directly.

The prose-contract modules (the ones that pin cross-file invariants carried by
skill and role *prose* rather than by a helper's CLI) need no importlib dance —
just the artifact's path and its text. Their shared paths and the one-line
`read` helper live here for the same reason the script relpaths do: a path
hardcoded in three modules drifts in one of them when an artifact is renamed.
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Relative paths (from repo root) of the live helper scripts.
SCOPED_MARKER_RESOLVER = "skills/quo-breakdown-epic/scripts/scoped_marker_resolver.py"
DETECT_FAST_PATH = "skills/quo-setup/scripts/detect_fast_path.py"
HIVE_COMMIT = "skills/quo-execute/scripts/hive_commit.py"
CONTEXT_GAUGE = "skills/quo-setup/scripts/context_gauge.py"

# Relative paths (from repo root) of the shipped artifacts whose prose carries a
# cross-file contract the suite pins.
QUO_EXECUTE = "skills/quo-execute/SKILL.md"
QUO_FIX_ISSUE = "skills/quo-fix-issue/SKILL.md"
QUO_ENGINEER_REVIEW = "skills/quo-engineer-review/SKILL.md"

AGENTS_DIR = REPO_ROOT / "agents"

AGENT_ANALYST = "agents/analyst.md"
AGENT_CODE_REVIEWER = "agents/code-reviewer.md"
AGENT_DOC_WRITER = "agents/doc-writer.md"
AGENT_ENGINEER = "agents/engineer.md"
AGENT_PM = "agents/pm.md"
AGENT_TEST_WRITER = "agents/test-writer.md"


def read(path):
    """Read a repo file as text.

    Accepts either a repo-root-relative string (the constants above) or an
    absolute `Path` — `REPO_ROOT / <absolute>` is that absolute path, so both
    call shapes the prose-contract modules use resolve identically.
    """
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def load_script(relpath):
    """Import a single-file script by its repo-root-relative path and return the module.

    Uses a unique module name derived from the file stem so repeated loads (and the
    test modules each loading their own script) do not collide in sys.modules.
    """
    abspath = (REPO_ROOT / relpath).resolve()
    mod_name = f"_quorum_script_{abspath.stem}"
    spec = importlib.util.spec_from_file_location(mod_name, str(abspath))
    if spec is None or spec.loader is None:
        raise ImportError(f"could not create import spec for {abspath}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


def script_path(relpath):
    """Return the absolute Path to a repo-root-relative script (for subprocess calls)."""
    return (REPO_ROOT / relpath).resolve()
