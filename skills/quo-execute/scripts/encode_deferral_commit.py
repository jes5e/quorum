#!/usr/bin/env python3
"""Stage and commit the on-disk changes a deferral-hygiene Encode branch produced.

The deferral-hygiene gate shared by `/quo-execute` (Section 6.5),
`/quo-fix-issue` (Section 7.5), and `/quo-breakdown-epic` (Section 6.5) lets a
user route deferred items into an existing ticket body via
`bees update-ticket --body-file`. Those updates persist new on-disk changes in
the relevant hive's per-ticket directory (and, when the user routed an Encode to
the project PRD/SDD, in those doc files). This helper produces the single
follow-up commit that sweeps those changes — one commit per gate firing, not per
Encode item.

It exists so the three skill prose blocks can collapse their ~30-line paired
POSIX+PowerShell shell snippets (hive-path resolution, in-repo scoping,
conditional commit) into a single literal Bash tool call, matching the
bundled-helper precedent set by `detect_fast_path.py` and
`scoped_marker_resolver.py` (stdlib-only Python 3, cross-platform via
`pathlib`, single executable file, exit-2-on-hard-failure).

CLI contract
------------
    encode_deferral_commit.py --skill <slug> --count <N> [--doc-path <abs-path> ...]

- `--skill <slug>` (REQUIRED): one of `quo-execute`, `quo-fix-issue`,
  `quo-breakdown-epic`. Used only to build the commit subject. An unknown slug
  is a hard failure (exit 2).
- `--count <N>` (REQUIRED, integer): appears verbatim in the commit subject. The
  count of `defer-*` items the user routed to Encode in this gate firing. The
  helper does NOT derive it from git state.
- `--doc-path <abs-path>` (OPTIONAL, repeatable): a project PRD/SDD path the
  orchestrator already resolved from CLAUDE.md `## Documentation Locations` and
  routed an Encode to. Zero occurrences = no doc routed (the common case). Each
  given path must exist (exit 2 otherwise). The helper does NOT parse CLAUDE.md
  itself — the orchestrator passes resolved paths explicitly so the contract-key
  knowledge stays in the orchestrator and this helper stays purely
  git/hive-mechanical.

Behavior
--------
1. Resolve hive paths via `bees list-hives` (parsed in-process), keeping the
   `path` of every hive whose `normalized_name` is in {plans, specs, issues}.
2. Resolve the repo root via `git rev-parse --show-toplevel`.
3. `git add` each resolved hive path that is the repo root or a descendant of it
   (tested via `Path.resolve()` + `Path.is_relative_to`, NOT string-prefix
   matching). Out-of-repo hives are skipped — their `bees update-ticket` already
   persisted and they require no git action here.
4. `git add` each `--doc-path` (in-repo by definition).
5. Check staged state via `git diff --cached --quiet` exit status.
6. If nothing is staged: print `skipped: nothing staged` and exit 0. Do NOT
   create an empty commit.
7. If something is staged: commit with subject
   `Encode deferral: /<slug> — <N> ticket(s) updated`, print a one-line summary,
   exit 0.

Invariants (load-bearing)
-------------------------
- NEVER `git push`.
- NEVER `git add -A` — only the resolved hive paths and the explicit
  `--doc-path` arguments are staged, so in-flight changes elsewhere in the
  working tree are never swept in.
- NEVER create an empty commit.
- The commit subject string (em-dash `—`, exact spacing) is a contract shared
  with the three skill prose blocks; do not alter it.

Failure (exit 2): a single human-readable line on stderr.
"""

import argparse
import subprocess
import sys
import json
from pathlib import Path


VALID_SKILLS = frozenset({"quo-execute", "quo-fix-issue", "quo-breakdown-epic"})
HIVE_NAMES = frozenset({"plans", "specs", "issues"})


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def run_git(args, repo_root=None):
    """Run a git command, returning the CompletedProcess. Captures output."""
    cmd = ["git"]
    if repo_root is not None:
        cmd += ["-C", str(repo_root)]
    cmd += args
    return subprocess.run(cmd, capture_output=True, text=True)


def resolve_repo_root():
    """Return the repo root Path via `git rev-parse --show-toplevel`, or None."""
    result = run_git(["rev-parse", "--show-toplevel"])
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    return Path(out).resolve() if out else None


def resolve_hive_paths():
    """Return a list of hive Paths via `bees list-hives`, or None on failure."""
    try:
        result = subprocess.run(
            ["bees", "list-hives"],
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, OSError):
        return None
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None
    hives = data.get("hives") if isinstance(data, dict) else None
    if not isinstance(hives, list):
        return None
    paths = []
    for hive in hives:
        if not isinstance(hive, dict):
            continue
        if hive.get("normalized_name") in HIVE_NAMES:
            p = hive.get("path")
            if p:
                paths.append(Path(p))
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage and commit the on-disk changes a deferral-hygiene Encode branch produced.",
        add_help=True,
    )
    parser.add_argument(
        "--skill",
        required=True,
        help="one of quo-execute, quo-fix-issue, quo-breakdown-epic (commit subject only)",
    )
    parser.add_argument(
        "--count",
        required=True,
        type=int,
        help="count of defer-* items routed to Encode this gate firing (verbatim in subject)",
    )
    parser.add_argument(
        "--doc-path",
        action="append",
        default=[],
        dest="doc_paths",
        help="a resolved project PRD/SDD path routed an Encode (repeatable)",
    )
    try:
        args = parser.parse_args()
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.skill not in VALID_SKILLS:
        return fail(
            f"unknown --skill {args.skill!r}; expected one of: "
            + ", ".join(sorted(VALID_SKILLS))
        )

    repo_root = resolve_repo_root()
    if repo_root is None:
        return fail("could not resolve repo root via `git rev-parse --show-toplevel` (not a git repo?)")

    hive_paths = resolve_hive_paths()
    if hive_paths is None:
        return fail("could not resolve hive paths via `bees list-hives`")

    # Validate --doc-path existence up front.
    for raw in args.doc_paths:
        if not Path(raw).exists():
            return fail(f"--doc-path does not exist: {raw}")

    # Stage in-repo hive paths only (out-of-repo hives already persisted via bees).
    for hive_path in hive_paths:
        resolved = hive_path.resolve()
        if not resolved.is_relative_to(repo_root):
            continue
        add = run_git(["add", str(resolved)], repo_root=repo_root)
        if add.returncode != 0:
            return fail(f"`git add {resolved}` failed: {add.stderr.strip()}")

    # Stage each resolved PRD/SDD doc path (in-repo by definition).
    for raw in args.doc_paths:
        resolved = Path(raw).resolve()
        add = run_git(["add", str(resolved)], repo_root=repo_root)
        if add.returncode != 0:
            return fail(f"`git add {resolved}` failed: {add.stderr.strip()}")

    # Check staged state: `git diff --cached --quiet` exits 0 = nothing staged,
    # 1 = staged changes present.
    diff = run_git(["diff", "--cached", "--quiet"], repo_root=repo_root)
    if diff.returncode == 0:
        print("skipped: nothing staged")
        return 0

    subject = f"Encode deferral: /{args.skill} — {args.count} ticket(s) updated"
    commit = run_git(["commit", "-m", subject], repo_root=repo_root)
    if commit.returncode != 0:
        return fail(f"`git commit` failed: {commit.stderr.strip() or commit.stdout.strip()}")

    sha = run_git(["rev-parse", "--short", "HEAD"], repo_root=repo_root)
    short_sha = sha.stdout.strip() if sha.returncode == 0 else "unknown"
    print(f"Encode deferral committed: /{args.skill} — {args.count} ticket(s) updated ({short_sha})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
