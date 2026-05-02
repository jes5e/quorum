#!/usr/bin/env python3
"""Verify the Agent Teams precondition for bees-execute and bees-fix-issue.

Reads ~/.claude/settings.json (or %USERPROFILE%\\.claude\\settings.json on
Windows) and looks up .env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS. Falls back
to the CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS environment variable when the
file is missing, unreadable, or does not contain the key. Exits 0 silently
when either source is "1"; otherwise exits 1 with a stable error message.

Usage:
    python3 check_agent_teams.py   # POSIX
    python check_agent_teams.py    # Windows
"""

import json
import os
import sys
from pathlib import Path


FAILURE_MESSAGE = (
    "Run /bees-setup first. — CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is not "
    "'1' in settings.json or the environment."
)


def main() -> int:
    settings_path = Path.home() / ".claude" / "settings.json"
    val = ""
    try:
        with open(settings_path, encoding="utf-8") as f:
            val = (json.load(f).get("env") or {}).get(
                "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", ""
            )
    except (FileNotFoundError, IsADirectoryError):
        val = ""
    except (PermissionError, json.JSONDecodeError, OSError) as e:
        print(
            f"Warning: could not read {settings_path}: {e!r} — falling back to environment check.",
            file=sys.stderr,
        )
        val = ""

    if val == "1":
        return 0

    if os.environ.get("CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS", "") == "1":
        return 0

    print(FAILURE_MESSAGE, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
