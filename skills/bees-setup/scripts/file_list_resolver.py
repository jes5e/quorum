#!/usr/bin/env python3
"""File list egg resolver for the bees workflow.

## RESOLVER CONVENTION

The egg field stores a JSON array of absolute file paths to source documents
(e.g., a PRD and an SDD) provided by the user at planning time.

Store the egg as a JSON-encoded array of absolute paths. Example:

    egg = ["/home/user/docs/my_prd.md", "/home/user/docs/my_sdd.md"]

This resolver validates that every path in the array exists and is a file,
then returns the resolved absolute paths as a JSON array. Downstream skills
read these files to understand the scope and requirements of the work.

Order in the array is preserved so consumers can rely on positional
conventions (e.g., index 0 = PRD, index 1 = SDD) if desired.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Resolve file list egg values")
    parser.add_argument("--repo-root", required=True, help="Repository root path")
    parser.add_argument("--egg-value", required=True, help="Egg field value (JSON array of paths, or 'null')")
    args = parser.parse_args()

    egg_value = args.egg_value

    if egg_value == "null" or egg_value == "":
        print("null")
        sys.exit(0)

    try:
        parsed = json.loads(egg_value)
    except json.JSONDecodeError as e:
        print(f"egg value is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if isinstance(parsed, str):
        parsed = [parsed]

    if not isinstance(parsed, list):
        print(f"egg value must be a JSON array of paths, got {type(parsed).__name__}", file=sys.stderr)
        sys.exit(1)

    if len(parsed) == 0:
        print(f"egg value is an empty list", file=sys.stderr)
        sys.exit(1)

    resolved = []
    for item in parsed:
        if not isinstance(item, str):
            print(f"every egg entry must be a string path, got {type(item).__name__}: {item!r}", file=sys.stderr)
            sys.exit(1)

        path = Path(item)
        if not path.is_absolute():
            path = Path(args.repo_root) / path

        if not path.exists():
            print(f"file does not exist: {path}", file=sys.stderr)
            sys.exit(1)

        if not path.is_file():
            print(f"path is not a file: {path}", file=sys.stderr)
            sys.exit(1)

        resolved.append(str(path.resolve()))

    print(json.dumps(resolved))
    sys.exit(0)


if __name__ == "__main__":
    main()
