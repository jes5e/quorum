#!/usr/bin/env python3
"""Stage and commit the on-disk changes a deferral-hygiene Encode branch produced.

The deferral-hygiene gate shared by `/quo-execute` and `/quo-fix-issue` (their
`## 9. Deferral hygiene`) and `/quo-breakdown-epic` (its end of run) lets a
user route deferred items into an existing ticket body via
`bees update-ticket --body-file`. Those updates persist new on-disk changes in
the relevant hive's per-ticket directory. This helper produces the single
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
This helper has three modes, selected by an argparse subcommand. All reuse the
same `bees list-hives` parsing, repo-root resolution, and in-repo membership
test — that single implementation of the hive-scoping mechanics is the whole
reason the helper exists.

**Encode-commit mode (default-shaped subcommand `encode-commit`, also accepted
bare for backward compatibility):**

    hive_commit.py [encode-commit] --skill <slug> --count <N>

Stages and commits the on-disk changes a deferral-hygiene Encode branch
produced — one follow-up commit per gate firing.

**Stage mode:**

    hive_commit.py stage [--hive <name> ...]

`git add`s each named in-repo hive except its `.hive/` configuration directory,
and prints each staged hive's absolute path, one per line. Every skill commit
step that stages a whole hive calls this mode, beside its judgement-selected
source files, so the `.hive/` exclusion has one home and no caller passes an
exclude pathspec. It never commits.

**Resolve-hive-paths mode (NON-MUTATING query):**

    hive_commit.py resolve-hive-paths [--hive <name> ...]

Pure query — performs NO `git add`, NO `git commit`, NO mutation whatsoever.
Prints each named IN-REPO hive's absolute path, one per line, for a caller that
stages one ticket's directory under it (`/quo-fix-issue`'s per-Issue commit).

Both `stage` and `resolve-hive-paths` take:

- `--hive <name>` (OPTIONAL, repeatable): one of `plans`, `specs`, `issues`.
  Default = all three when none given (matching the encode-commit mode's
  resolve-all behavior). Filters the resolved hives to the named set.
- Print nothing and exit 0 when no named hive is in-repo (out-of-repo case —
  the caller stages nothing). Exit 2 with a one-line stderr message on
  `bees list-hives`, `git rev-parse`, or `git add` failure (matching the
  encode-commit failure contract).

encode-commit mode arguments:

- `--skill <slug>` (REQUIRED): one of `quo-execute`, `quo-fix-issue`,
  `quo-breakdown-epic`. Used only to build the commit subject. An unknown slug
  is a hard failure (exit 2).
- `--count <N>` (REQUIRED, integer): appears verbatim in the commit subject. The
  count of `defer-*` items the user routed to Encode in this gate firing. The
  helper does NOT derive it from git state.

Behavior
--------
1. Resolve hive paths via `bees list-hives` (parsed in-process), keeping the
   `path` of every hive whose `normalized_name` is in {plans, specs, issues}.
2. Resolve the repo root via `git rev-parse --show-toplevel`.
3. Stage each resolved hive that is the repo root or a descendant of it
   (tested via `Path.resolve()` + `Path.is_relative_to`, NOT string-prefix
   matching), as stage mode does: everything but its `.hive/` configuration.
   Out-of-repo hives are skipped — their `bees update-ticket` already
   persisted and they require no git action here.
4. Check staged state via `git diff --cached --quiet` exit status.
5. If nothing is staged: print `skipped: nothing staged` and exit 0. Do NOT
   create an empty commit.
6. If something is staged: commit with subject
   `Encode deferral: /<slug> — <N> deferral(s) encoded`, print a one-line summary,
   exit 0.

Invariants (load-bearing)
-------------------------
- NEVER `git push`.
- NEVER `git add -A` — only the resolved hive paths are staged, so in-flight
  changes elsewhere in the working tree are never swept in.
- NEVER stage a hive's `.hive/` configuration (see `HIVE_CONFIG_DIR`).
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
# A hive's own configuration directory. Never staged: a repo may track it, and
# registering a hive from a worktree rewrites it locally, so committing it would
# write one checkout's local configuration over the shared file.
HIVE_CONFIG_DIR = ".hive"


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


def resolve_hive_paths(names=None):
    """Return a list of hive Paths via `bees list-hives`, or None on failure.

    `names` is an optional collection of normalized hive names to filter to;
    when None (the default), all hives in `HIVE_NAMES` are returned — preserving
    the encode-commit mode's resolve-all behavior verbatim.
    """
    wanted = HIVE_NAMES if names is None else frozenset(names)
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
        if hive.get("normalized_name") in wanted:
            p = hive.get("path")
            if p:
                paths.append(Path(p))
    return paths


def in_repo_hives(repo_root, hive_paths):
    """Return the resolved hive Paths that are the repo root or inside it."""
    resolved = (p.resolve() for p in hive_paths)
    return [p for p in resolved if p.is_relative_to(repo_root)]


def stage_hives(repo_root, hives):
    """`git add` each in-repo hive except its `.hive/` configuration.

    Returns None on success, or the failure message. The exclusion is a
    pathspec, not a directory walk, so a deleted ticket directory is staged too.
    """
    for hive in hives:
        rel = hive.relative_to(repo_root)
        spec = rel.as_posix()
        exclude = ":(exclude)" + (rel / HIVE_CONFIG_DIR).as_posix()
        add = run_git(["add", "--", spec, exclude], repo_root=repo_root)
        if add.returncode != 0:
            return f"`git add {spec}` failed: {add.stderr.strip()}"
    return None


def cmd_resolve_hive_paths(args) -> int:
    """NON-MUTATING query: print each named in-repo hive's absolute path."""
    repo_root = resolve_repo_root()
    if repo_root is None:
        return fail("could not resolve repo root via `git rev-parse --show-toplevel` (not a git repo?)")

    names = args.hives if args.hives else None
    hive_paths = resolve_hive_paths(names)
    if hive_paths is None:
        return fail("could not resolve hive paths via `bees list-hives`")

    for hive in in_repo_hives(repo_root, hive_paths):
        print(str(hive))
    return 0


def cmd_stage(args) -> int:
    """Stage each named in-repo hive except `.hive/`; print each staged hive's path."""
    repo_root = resolve_repo_root()
    if repo_root is None:
        return fail("could not resolve repo root via `git rev-parse --show-toplevel` (not a git repo?)")

    names = args.hives if args.hives else None
    hive_paths = resolve_hive_paths(names)
    if hive_paths is None:
        return fail("could not resolve hive paths via `bees list-hives`")

    hives = in_repo_hives(repo_root, hive_paths)
    error = stage_hives(repo_root, hives)
    if error:
        return fail(error)
    for hive in hives:
        print(str(hive))
    return 0


def cmd_encode_commit(args) -> int:
    """Stage and commit the on-disk changes a deferral-hygiene Encode branch produced."""
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

    # Out-of-repo hives already persisted via bees and need no git action.
    error = stage_hives(repo_root, in_repo_hives(repo_root, hive_paths))
    if error:
        return fail(error)

    # Check staged state: `git diff --cached --quiet` exits 0 = nothing staged,
    # 1 = staged changes present.
    diff = run_git(["diff", "--cached", "--quiet"], repo_root=repo_root)
    if diff.returncode == 0:
        print("skipped: nothing staged")
        return 0

    subject = f"Encode deferral: /{args.skill} — {args.count} deferral(s) encoded"
    commit = run_git(["commit", "-m", subject], repo_root=repo_root)
    if commit.returncode != 0:
        return fail(f"`git commit` failed: {commit.stderr.strip() or commit.stdout.strip()}")

    sha = run_git(["rev-parse", "--short", "HEAD"], repo_root=repo_root)
    short_sha = sha.stdout.strip() if sha.returncode == 0 else "unknown"
    print(f"Encode deferral committed: /{args.skill} — {args.count} deferral(s) encoded ({short_sha})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage/commit a deferral-hygiene Encode branch, or resolve in-repo hive paths.",
        add_help=True,
    )
    subparsers = parser.add_subparsers(dest="mode")

    # Encode-commit mode (also accepted bare, with no subcommand, for backward
    # compatibility with the existing --skill/--count invocation).
    encode = subparsers.add_parser(
        "encode-commit",
        help="stage and commit the on-disk changes a deferral-hygiene Encode branch produced",
    )
    for p in (parser, encode):
        p.add_argument(
            "--skill",
            help="one of quo-execute, quo-fix-issue, quo-breakdown-epic (commit subject only)",
        )
        p.add_argument(
            "--count",
            type=int,
            help="count of defer-* items routed to Encode this gate firing (verbatim in subject)",
        )

    # Stage mode: the one place a hive is staged.
    stage = subparsers.add_parser(
        "stage",
        help="git add each named in-repo hive except its .hive/ configuration; print each staged hive's path",
    )

    # Resolve-hive-paths mode (NON-MUTATING query).
    resolve = subparsers.add_parser(
        "resolve-hive-paths",
        help="print each named, in-repo hive's absolute path (one per line); no mutation",
    )
    for p in (stage, resolve):
        p.add_argument(
            "--hive",
            action="append",
            default=[],
            dest="hives",
            choices=sorted(HIVE_NAMES),
            help="hive name (repeatable; default = all three when omitted)",
        )

    try:
        args = parser.parse_args()
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 2

    if args.mode == "resolve-hive-paths":
        return cmd_resolve_hive_paths(args)
    if args.mode == "stage":
        return cmd_stage(args)

    # Default / bare invocation and the explicit `encode-commit` subcommand both
    # route to encode-commit mode. --skill/--count are required there.
    if args.skill is None or args.count is None:
        return fail("encode-commit mode requires --skill and --count")
    return cmd_encode_commit(args)


if __name__ == "__main__":
    sys.exit(main())
