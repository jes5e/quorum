#!/usr/bin/env python3
"""Write the ticket text an implementer works from into one scratch file.

`/quo-execute` hands each implementer the Task body, its own role's Subtask
bodies and the Epic's `## Epic-wide contracts` section. Pasting that text into
every dispatch prompt costs the orchestrator its own context twice per dispatch
(once to read it, once to emit it), and on large Tasks that repeat is what
drives the orchestrator to hand off. This helper copies the text from the
ticket store straight into a file, so the orchestrator passes only the path and
the implementer reads the file in full. The text is copied byte for byte, so
nothing is paraphrased.

It is the one place that knows how the ticket store is queried; another ticket
system needs only a new `fetch` here.

Usage
-----
    ticket_bodies.py --task <task-id> --role <engineer|test-writer|doc-writer>

Writes `<tempdir>/.quorum/bodies-<task-id>-<role>-<suffix>.md` (`<tempdir>` is
Python's `tempfile.gettempdir()`: `/tmp` on most POSIX systems, `%TEMP%` on
Windows), creating `.quorum` when absent, and prints the file's path. The file
holds, in order:

- the Task's title and body;
- the body of each of the Task's Subtasks tagged with the role, in dependency
  order (a Subtask after those it depends on), ties kept in the Task's order;
- the parent Epic's `## Epic-wide contracts` section, from its heading to the
  next heading of level 1 or 2, or a line saying the Epic has none.

Run it just before every fresh dispatch: a new file each time carries any
revision approved since the last one. The file is never deleted.

Failure (exit 2): one line on stderr, and no file is written.
"""

import argparse
import json
import re
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

ROLES = ("engineer", "test-writer", "doc-writer")
CONTRACTS_HEADING = "## Epic-wide contracts"


class FetchError(Exception):
    pass


def fetch(ids):
    """Return {id: ticket} for the given ticket ids from `bees show-ticket`."""
    try:
        result = subprocess.run(
            ["bees", "show-ticket", "--ids", *ids],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (FileNotFoundError, OSError) as exc:
        raise FetchError(f"could not run `bees show-ticket`: {exc}")
    if result.returncode != 0:
        raise FetchError(f"`bees show-ticket` failed: {(result.stderr or result.stdout).strip()}")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise FetchError("`bees show-ticket` returned output that is not JSON")
    tickets = data.get("tickets") if isinstance(data, dict) else None
    if not isinstance(tickets, list):
        raise FetchError("`bees show-ticket` returned no ticket list")
    found = {t.get("ticket_id"): t for t in tickets if isinstance(t, dict)}
    missing = [i for i in ids if i not in found]
    if missing:
        raise FetchError("ticket(s) not found: " + ", ".join(missing))
    return found


def dependency_order(subtasks):
    """Order Subtasks so each follows those it depends on; ties keep input order."""
    ids = [s["ticket_id"] for s in subtasks]
    by_id = dict(zip(ids, subtasks))
    placed, ordered = set(), []
    while len(ordered) < len(ids):
        progressed = False
        for i in ids:
            if i in placed:
                continue
            deps = [d for d in by_id[i].get("up_dependencies") or [] if d in by_id]
            if all(d in placed for d in deps):
                placed.add(i)
                ordered.append(by_id[i])
                progressed = True
        if not progressed:  # a cycle: keep the rest in input order
            ordered += [by_id[i] for i in ids if i not in placed]
            break
    return ordered


def contracts_section(body):
    """The `## Epic-wide contracts` section of an Epic body, or None."""
    lines = body.splitlines(keepends=True)
    in_fence, start = False, None
    for n, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if start is None:
            if line.rstrip() == CONTRACTS_HEADING:
                start = n
        elif re.match(r"^#{1,2} ", line):
            return "".join(lines[start:n])
    return "".join(lines[start:]) if start is not None else None


def compose(task, subtasks, epic):
    parts = [f"# Task {task['ticket_id']}: {task.get('title', '')}\n\n", task.get("body") or "", "\n"]
    for sub in subtasks:
        parts += [f"\n# Subtask {sub['ticket_id']}: {sub.get('title', '')}\n\n", sub.get("body") or "", "\n"]
    if epic is None:
        parts.append("\n# Epic: none (the Task has no parent)\n")
    else:
        section = contracts_section(epic.get("body") or "")
        parts.append(f"\n# Epic {epic['ticket_id']}: {epic.get('title', '')}\n\n")
        parts.append(section if section is not None else f"The Epic has no `{CONTRACTS_HEADING}` section.\n")
    return "".join(parts)


def write(task_id, role, text):
    directory = Path(tempfile.gettempdir()) / ".quorum"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"bodies-{task_id}-{role}-{secrets.token_hex(3)}.md"
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Write a Task's body, one role's Subtask bodies and the Epic's "
        "`## Epic-wide contracts` into a scratch file; print its path."
    )
    parser.add_argument("--task", required=True, help="the Task's ticket id")
    parser.add_argument("--role", required=True, choices=ROLES, help="the implementer role")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        task = fetch([args.task])[args.task]
        children = task.get("children") or []
        tagged = []
        if children:
            found = fetch(children)
            tagged = [found[c] for c in children if args.role in (found[c].get("tags") or [])]
        parent = task.get("parent")
        epic = fetch([parent])[parent] if parent else None
    except FetchError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    path = write(args.task, args.role, compose(task, dependency_order(tagged), epic))
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
