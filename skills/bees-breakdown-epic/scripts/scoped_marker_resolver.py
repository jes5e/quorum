#!/usr/bin/env python3
"""Detect and apply the Plan Bee Scoped-marker.

A Plan Bee authored via `/bees-plan-from-specs --feature "<title>"` contains
a single line of the literal form:

    Scoped to `### Feature: <title>` from <prd-path> and <sdd-path>.

When present, downstream skills (bees-breakdown-epic, bees-execute,
bees-fix-issue) must scope each named doc's content to the matching
`### Feature: <title>` subsection rather than treat the full doc as the
canonical spec. This script is the shared parser/scoper for all three
skills.

Input
-----
Positional arg 1: path to a file containing the parent Bee body.

Output (stdout, JSON)
---------------------
On success (always exit 0 when no error condition is hit):

    {
      "scoped": false
    }

  or

    {
      "scoped": true,
      "title": "<trimmed title>",
      "docs": [
        {"path": "<absolute path>", "content": "<scoped subsection body>"},
        ...
      ]
    }

The `docs` array preserves the order the marker line names the paths in
(PRD first, SDD second per the emitter).

Failure (exit 2): a single human-readable error line on stderr and exit 2.

Failure modes
-------------
- Bee-body file unreadable -> exit 2 ("could not read <path>: ...").
- Marker present but malformed (cannot extract title/paths) -> exit 2.
- Marker references a doc that does not exist on disk -> exit 2.
- Marker references a doc but the heading `### Feature: <title>` is not
  present in that doc -> exit 2 with a clear message naming the missing
  heading, the doc paths checked, and a hint that the docs may have been
  edited after the Plan Bee was created.

Subsection extraction rule (mirrors `/bees-plan-from-specs` Step 1b):
- The matched heading line itself is excluded.
- The body runs until the next line starting with `### Feature: `
  (literal `### Feature:` followed by a single space — the trailing
  space is required and matches `HEADING_PREFIX` below; also excluded),
  or end-of-file, whichever comes first.
- Heading-side title comparison is case-sensitive against the trimmed
  text after the `### Feature: ` prefix.

Usage:
    python3 scoped_marker_resolver.py <bee-body-file>   # POSIX
    python  scoped_marker_resolver.py <bee-body-file>   # Windows
"""

import json
import re
import sys
from pathlib import Path


MARKER_RE = re.compile(
    r"^\s*Scoped to `### Feature: (?P<title>.*?)` from (?P<prd>.+?) and (?P<sdd>.+?)\.\s*$"
)
MARKER_PREFIX_RE = re.compile(r"^\s*Scoped to `")
HEADING_PREFIX = "### Feature: "


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 2


def find_marker(body: str):
    """Return (match, malformed_line).

    - (m, None): a well-formed marker line was found.
    - (None, line): a marker-shaped line (starts with `` Scoped to ` ``,
      i.e. the literal `Scoped to ` followed by a backtick) was found but
      the full grammar did not match — caller must hard-fail. The backtick
      requirement narrows this from any prose starting with "Scoped to "
      (e.g. "Scoped to a single feature.") to lines that are clearly
      attempting the marker shape.
    - (None, None): no marker-shaped line at all — caller treats as unscoped.
    """
    for line in body.splitlines():
        m = MARKER_RE.match(line)
        if m:
            return m, None
        if MARKER_PREFIX_RE.match(line):
            return None, line
    return None, None


def extract_subsection(doc_text: str, title: str):
    lines = doc_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if not line.startswith(HEADING_PREFIX):
            continue
        heading_title = line[len(HEADING_PREFIX):].rstrip()
        if heading_title == title:
            start = i + 1
            break
    if start is None:
        return None

    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith(HEADING_PREFIX):
            end = j
            break

    return "\n".join(lines[start:end])


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        return fail("Usage: scoped_marker_resolver.py <bee-body-file>")

    bee_body_path = Path(sys.argv[1])
    try:
        body = bee_body_path.read_text(encoding="utf-8-sig")
    except OSError as e:
        return fail(f"could not read {bee_body_path}: {e!r}")

    m, malformed_line = find_marker(body)
    if m is None and malformed_line is not None:
        return fail(f"Scoped-marker line is malformed: {malformed_line}")
    if m is None:
        print(json.dumps({"scoped": False}))
        return 0

    title = m.group("title").strip()
    if not title:
        return fail(
            "Scoped-marker present but title is empty after trimming. "
            "Marker grammar requires a non-empty `### Feature: <title>`."
        )

    doc_paths = [m.group("prd").strip(), m.group("sdd").strip()]
    docs_out = []
    missing_paths = []
    missing_heading_paths = []

    for raw_path in doc_paths:
        p = Path(raw_path)
        if not p.is_file():
            missing_paths.append(raw_path)
            continue
        try:
            text = p.read_text(encoding="utf-8-sig")
        except OSError as e:
            return fail(f"could not read {raw_path}: {e!r}")
        scoped = extract_subsection(text, title)
        if scoped is None:
            missing_heading_paths.append(raw_path)
            continue
        docs_out.append({"path": str(p), "content": scoped})

    if missing_paths:
        return fail(
            "Scoped-marker references doc(s) that do not exist on disk: "
            + ", ".join(missing_paths)
            + ". The Plan Bee may have been created against a different "
            "checkout, or the doc was moved/deleted after the Plan Bee was "
            "authored. Note: this can also happen if a PRD or SDD absolute "
            'path contains the substring " and " — the marker grammar uses '
            '" and " as a separator and the parser splits on the first '
            "occurrence."
        )

    if missing_heading_paths:
        return fail(
            f"Scoped-marker heading `### Feature: {title}` not found in: "
            + ", ".join(missing_heading_paths)
            + ". The doc(s) may have been edited (heading renamed or "
            "removed) after the Plan Bee was created. Re-author the Plan "
            "Bee or restore the heading before continuing."
        )

    print(
        json.dumps(
            {
                "scoped": True,
                "title": title,
                "docs": docs_out,
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
