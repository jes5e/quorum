"""Shared pytest fixtures and the import-by-path helper for the helper-script suite.

The scripts under test are single-file CLIs living under `skills/<name>/scripts/`,
not an importable package. `load_script` centralizes the importlib dance so each test
module can get the module object with one call and unit-test its pure functions directly.

The prose-contract modules (the ones that pin cross-file invariants carried by
skill and role *prose* rather than by a helper's CLI) need no importlib dance —
just the artifact's path and its text. What they share lives here in three
layers, each with its own drift rationale:

  * the **artifact paths** and the one-line `read` helper, for the same reason
    the script relpaths do — a path hardcoded in three modules drifts in one of
    them when an artifact is renamed;
  * `shipped_artifacts()`, the single definition of *what ships*, because two
    enumerators would drift into disagreeing about the shipped boundary that
    both of their callers are asserting about;
  * `heading_section()` / `routing_section()`, the section slicers, because a
    slicer that silently yields an empty slice turns every assertion made
    against it vacuous rather than failing — so the exactly-one-heading check
    belongs in one place, not re-derived per module.
"""

import importlib.util
import re
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
QUO_BREAKDOWN_EPIC = "skills/quo-breakdown-epic/SKILL.md"
QUO_ENGINEER_REVIEW = "skills/quo-engineer-review/SKILL.md"
QUO_TEST_WRITER_REVIEW = "skills/quo-test-writer-review/SKILL.md"
QUO_DOC_WRITER_REVIEW = "skills/quo-doc-writer-review/SKILL.md"
QUO_SPEC_REVIEW = "skills/quo-spec-review/SKILL.md"
QUO_PLAN = "skills/quo-plan/SKILL.md"
QUO_FILE_ISSUE = "skills/quo-file-issue/SKILL.md"

# Shipped reference files the two orchestrators read on demand. The shared
# ones live under quo-execute and are sibling-resolved by quo-fix-issue.
REF_ROUTING = "skills/quo-execute/references/routing.md"
REF_POST_COMPLETION_PROMPT = "skills/quo-execute/references/post-completion-prompt.md"
REF_COMPROMISE_TRACKER = "skills/quo-execute/references/compromise-tracker.md"
REF_CONTEXT_GUARD = "skills/quo-execute/references/context-guard.md"
REF_RATIONALE = "skills/quo-execute/references/rationale.md"
REF_URL_RESOLUTION = "skills/quo-fix-issue/references/url-resolution.md"
REF_GITHUB_CLOSE = "skills/quo-fix-issue/references/github-close.md"

AGENTS_DIR = REPO_ROOT / "agents"

AGENT_ANALYST = "agents/analyst.md"
AGENT_CODE_REVIEWER = "agents/code-reviewer.md"
AGENT_DOC_WRITER = "agents/doc-writer.md"
AGENT_ENGINEER = "agents/engineer.md"
AGENT_PM = "agents/pm.md"
AGENT_TEST_WRITER = "agents/test-writer.md"

# The one section both orchestrators carry that defines how review findings are
# routed. More than one prose-contract module slices it, so the heading and the
# slicer live here rather than in whichever module needed them first.
ROUTING_SECTION_HEADING = "### Orchestrator discipline: routing review findings"


def read(path):
    """Read a repo file as text.

    Accepts either a repo-root-relative string (the constants above) or an
    absolute `Path` — `REPO_ROOT / <absolute>` is that absolute path, so both
    call shapes the prose-contract modules use resolve identically.
    """
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def shipped_artifacts():
    """Every file the install procedure copies into a target project.

    `skills/*` and `agents/*` ship wholesale, so this covers every SKILL.md,
    every bundled helper script, and every role contract. Returned as absolute
    `Path`s, sorted within each group; pass one to `read` for its text.

    This is the single definition of "what ships". More than one prose-contract
    module needs the set — one to prove no shipped artifact carries a dangling
    repo-only-doc citation, another to prove none names a retired vocabulary
    token — and two enumerators would drift into disagreeing about the shipped
    boundary, which is the one thing both of them are asserting about.
    """
    paths = []
    paths += sorted((REPO_ROOT / "skills").rglob("*.md"))
    paths += sorted((REPO_ROOT / "skills").rglob("*.py"))
    paths += sorted((REPO_ROOT / "agents").rglob("*.md"))
    return [p for p in paths if "__pycache__" not in p.parts]


def heading_section(text, heading):
    """The slice of `text` under `heading`, up to the next same-or-higher heading.

    `heading` is the full markdown heading line (`### Foo`); its `#` run fixes
    the level, so a `####` sub-heading is kept inside the returned slice and a
    sibling `###` ends it. The exactly-one assertion is deliberate: a heading
    that was renamed or duplicated would otherwise silently yield an empty or
    over-long slice, and every assertion made against that slice would go
    vacuous rather than fail.

    Lines inside fenced code blocks are never headings: the orchestrator
    bodies embed manifest and tracker templates whose fenced contents start
    with `##`, and a slicer that honored those would cut a section short.
    """
    level = len(heading) - len(heading.lstrip("#"))
    lines = text.splitlines()
    headings = _heading_lines(lines)
    starts = [i for i in headings if lines[i].strip() == heading]
    assert len(starts) == 1, (
        f"expected exactly one {heading!r} heading, got {len(starts)}"
    )
    start = starts[0]
    end = len(lines)
    for j in headings:
        if j <= start:
            continue
        match = re.match(r"^(#{1,6}) ", lines[j])
        if match and len(match.group(1)) <= level:
            end = j
            break
    return "\n".join(lines[start:end])


def _heading_lines(lines):
    """Indices of markdown heading lines that sit outside fenced code blocks."""
    indices = []
    in_fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and re.match(r"^#{1,6} ", line):
            indices.append(i)
    return indices


def routing_section(text):
    """The `### Orchestrator discipline: routing review findings` section."""
    return heading_section(text, ROUTING_SECTION_HEADING)


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
