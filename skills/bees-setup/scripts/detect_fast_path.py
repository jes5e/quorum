#!/usr/bin/env python3
"""Fast-path detection for /bees-setup.

Walks the target repo's `.bees/<hive>/.hive/identity.json` markers, checks the
per-machine `~/.bees/config.json` for any scope that covers the repo, and
inspects `CLAUDE.md` for populated `## Documentation Locations` and
`## Build Commands` sections.

Emits a JSON payload to stdout describing the situation so the skill prose
can decide between the fast path (re-register existing hives only) and the
existing slow path (full setup walk).

Output schema:

    {
      "repo_root": "/abs/path",
      "on_disk_hives": [{"name": "issues", "path": "/abs/path/.bees/issues"}, ...],
      "any_registered_for_repo": true|false,
      "registered_hive_names": ["issues", "plans"],
      "claude_md_path": "/abs/path/CLAUDE.md",
      "claude_md_doc_locations_set_up": true|false,
      "claude_md_build_commands_set_up": true|false,
      "fast_path_eligible": true|false
    }

`fast_path_eligible` is true iff:
  - on_disk_hives is non-empty
  - any_registered_for_repo is false
  - both CLAUDE.md sections are populated
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


REQUIRED_DOC_KEYS = [
    "Project requirements doc (PRD)",
    "Internal architecture docs (SDD)",
    "Customer-facing docs",
    "Engineering best practices",
    "Test writing guide",
    "Test review guide",
    "Doc writing guide",
]

REQUIRED_BUILD_KEYS = [
    "Compile/type-check",
    "Format",
    "Lint",
    "Narrow test",
    "Full test",
]

# Build keys for which an empty value is acceptable (matches the contract in CLAUDE.md).
BUILD_KEYS_ALLOWED_EMPTY = {"Compile/type-check"}


def find_on_disk_hives(repo_root: Path):
    bees_dir = repo_root / ".bees"
    if not bees_dir.is_dir():
        return []
    hives = []
    for child in sorted(bees_dir.iterdir()):
        if not child.is_dir():
            continue
        marker = child / ".hive" / "identity.json"
        if not marker.is_file():
            continue
        name = child.name
        try:
            with marker.open(encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("normalized_name") or data.get("display_name") or name
        except (OSError, json.JSONDecodeError):
            pass
        hives.append({"name": name, "path": str(child.resolve())})
    return hives


def _glob_to_regex(glob: str) -> re.Pattern:
    """Translate a bees scope glob into a regex.

    Bees scope strings are typically `<abs-prefix>/**` or `<abs-prefix>/**/*.ext`.
    We need `**` to match zero-or-more path segments, and `*` to match within a
    single segment. Python's stdlib `fnmatch` flattens both, so do it by hand.

    ASSUMES the scope grammar bees uses today: literal segments plus `*`, `**`,
    and `?` wildcards. If bees ever extends scope semantics (brace expansion,
    negation, case-insensitive matching, etc.), this translator will silently
    diverge from bees' own scope-matching logic — re-verify against the bees
    source before assuming this still gives the same coverage answer.
    """
    i = 0
    out = []
    while i < len(glob):
        c = glob[i]
        if c == "*":
            if i + 1 < len(glob) and glob[i + 1] == "*":
                out.append(".*")
                i += 2
                if i < len(glob) and glob[i] == "/":
                    i += 1
            else:
                out.append("[^/]*")
                i += 1
        elif c == "?":
            out.append("[^/]")
            i += 1
        elif c in ".^$+(){}[]|\\":
            out.append("\\" + c)
            i += 1
        else:
            out.append(c)
            i += 1
    return re.compile("^" + "".join(out) + "$")


def scope_covers(scope_glob: str, repo_root: Path) -> bool:
    repo_str = str(repo_root.resolve())
    try:
        pat = _glob_to_regex(scope_glob)
    except re.error:
        return False
    # Cross-platform separator gotcha: on Windows, Path.resolve() returns
    # backslash-separated form (`C:\Users\foo\repo`), but scopes are typically
    # registered with forward slashes (the prose in SKILL.md uses `<repo-root>/**`).
    # Test both separator forms (and both trailing-separator variants) against
    # the pattern so detection is robust regardless of which form was used at
    # registration time. On POSIX the replace() is a no-op since path strings
    # have no backslashes, so behavior is unchanged.
    repo_fwd = repo_str.replace("\\", "/")
    candidates = {
        repo_str, repo_str + "/", repo_str + "\\",
        repo_fwd, repo_fwd + "/",
    }
    return any(pat.match(c) for c in candidates)


def load_bees_config():
    home = Path(os.path.expanduser("~"))
    candidate = home / ".bees" / "config.json"
    if not candidate.is_file():
        return {}
    try:
        with candidate.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def find_repo_registration(config: dict, repo_root: Path):
    """Return list of hive names registered under any scope that covers repo_root."""
    scopes = config.get("scopes") or {}
    registered = set()
    for scope_key, scope_data in scopes.items():
        if not isinstance(scope_data, dict):
            continue
        if not scope_covers(scope_key, repo_root):
            continue
        hives = scope_data.get("hives") or {}
        if isinstance(hives, dict):
            for hive_name in hives:
                registered.add(hive_name)
    return sorted(registered)


def _split_top_level_sections(text: str):
    """Yield (heading, body) for each `## ` section, ignoring fenced blocks.

    Returns a dict mapping the exact heading text (e.g. "Documentation Locations")
    to the body string between that heading and the next top-level heading or EOF.
    """
    lines = text.splitlines(keepends=True)
    sections = {}
    current_heading = None
    current_body = []
    in_fence = False
    for line in lines:
        stripped = line.rstrip("\r\n")
        if stripped.startswith("```"):
            in_fence = not in_fence
            if current_heading is not None:
                current_body.append(line)
            continue
        if not in_fence and stripped.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "".join(current_body)
            current_heading = stripped[3:].strip()
            current_body = []
            continue
        if current_heading is not None:
            current_body.append(line)
    if current_heading is not None:
        sections[current_heading] = "".join(current_body)
    return sections


# Matches the canonical contract bullet shape `- **Key**: value` that the
# bees-setup slow path emits. If a user hand-edits CLAUDE.md to drop the bold
# emphasis or use a different style, the bullet silently fails to match and
# the section is reported as not-set-up, which causes the slow path to re-prompt
# — that is intentional defensive behavior. Don't loosen this regex without
# considering that you'd be widening the parse to match malformed CLAUDE.md.
_BULLET_RE = re.compile(r"^\s*-\s+\*\*(?P<key>[^*]+?)\*\*\s*:\s*(?P<value>.*?)\s*$")


def _parse_keyed_bullets(body: str):
    """Parse `- **Key**: value` bullet lines into a dict."""
    result = {}
    for line in body.splitlines():
        m = _BULLET_RE.match(line)
        if not m:
            continue
        key = m.group("key").strip()
        value = m.group("value").strip()
        result[key] = value
    return result


def inspect_claude_md(repo_root: Path):
    path = repo_root / "CLAUDE.md"
    info = {
        "claude_md_path": str(path),
        "claude_md_doc_locations_set_up": False,
        "claude_md_build_commands_set_up": False,
    }
    if not path.is_file():
        return info
    try:
        with path.open(encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return info
    sections = _split_top_level_sections(text)

    doc_body = sections.get("Documentation Locations")
    if doc_body is not None:
        bullets = _parse_keyed_bullets(doc_body)
        # "Populated" = every contract key is present as a bullet. Individual
        # values may be empty (the user can legitimately skip a guide), but the
        # row must exist. A stub-empty section with no bullets does not count.
        info["claude_md_doc_locations_set_up"] = all(
            k in bullets for k in REQUIRED_DOC_KEYS
        )

    build_body = sections.get("Build Commands")
    if build_body is not None:
        bullets = _parse_keyed_bullets(build_body)
        ok = True
        for k in REQUIRED_BUILD_KEYS:
            if k not in bullets:
                ok = False
                break
            if not bullets[k] and k not in BUILD_KEYS_ALLOWED_EMPTY:
                ok = False
                break
        info["claude_md_build_commands_set_up"] = ok

    return info


def main():
    parser = argparse.ArgumentParser(description="Detect /bees-setup fast-path eligibility")
    parser.add_argument("--repo-root", required=True, help="Absolute path to the target repo root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"repo root is not a directory: {repo_root}", file=sys.stderr)
        sys.exit(1)

    on_disk = find_on_disk_hives(repo_root)
    config = load_bees_config()
    registered_names = find_repo_registration(config, repo_root)
    claude = inspect_claude_md(repo_root)

    fast_path_eligible = bool(
        on_disk
        and not registered_names
        and claude["claude_md_doc_locations_set_up"]
        and claude["claude_md_build_commands_set_up"]
    )

    out = {
        "repo_root": str(repo_root),
        "on_disk_hives": on_disk,
        "any_registered_for_repo": bool(registered_names),
        "registered_hive_names": registered_names,
        "fast_path_eligible": fast_path_eligible,
    }
    out.update(claude)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
