#!/usr/bin/env python3
"""Force-clean a stuck Claude Code team by removing its directories.

Cross-platform replacement for force-clean-team.sh. Functionally identical:
removes ~/.claude/teams/<team-name> and ~/.claude/tasks/<team-name> if they
exist, and reports what was removed.

Usage:
    python force_clean_team.py <team-name>
    python3 force_clean_team.py <team-name>   # POSIX equivalent

Works on macOS, Linux, and Windows (uses pathlib for path handling).
"""

import shutil
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2 or not sys.argv[1]:
        print("Usage: force_clean_team.py <team-name>", file=sys.stderr)
        return 2

    team_name = sys.argv[1]
    home = Path.home()
    targets = [
        home / ".claude" / "teams" / team_name,
        home / ".claude" / "tasks" / team_name,
    ]

    removed = 0
    for path in targets:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=False)
            print(f"Removed {path}")
            removed += 1

    if removed == 0:
        print(f"No directories found for team '{team_name}'")
    else:
        print(f"Team '{team_name}' force-cleaned.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
