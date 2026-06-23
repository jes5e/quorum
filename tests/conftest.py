"""Shared pytest fixtures and the import-by-path helper for the helper-script suite.

The three scripts under test are single-file CLIs living under `skills/<name>/scripts/`,
not an importable package. `load_script` centralizes the importlib dance so each test
module can get the module object with one call and unit-test its pure functions directly.
"""

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Relative paths (from repo root) of the three live helper scripts.
SCOPED_MARKER_RESOLVER = "skills/quo-breakdown-epic/scripts/scoped_marker_resolver.py"
DETECT_FAST_PATH = "skills/quo-setup/scripts/detect_fast_path.py"
HIVE_COMMIT = "skills/quo-execute/scripts/hive_commit.py"


def load_script(relpath):
    """Import a single-file script by its repo-root-relative path and return the module.

    Uses a unique module name derived from the file stem so repeated loads (and the
    three modules each loading their own script) do not collide in sys.modules.
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
