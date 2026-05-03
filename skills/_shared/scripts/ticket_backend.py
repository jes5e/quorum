#!/usr/bin/env python3
"""Single dispatcher between bees-workflow skills and a ticket-backend CLI.

Skills shell out to this module instead of calling bees (or, in Epic B, beads)
directly. The module reads `## Ticket Backend` from the target repo's CLAUDE.md
and routes each verb to the correct backend, normalizing argv shape and JSON
output across backends so skill prose does not branch per backend.

In Epic A (this Task), only the bees backend is wired. Calling any verb when
the resolved backend is `beads` exits with code 2 and a stable error message
pointing at Epic B (Plan Bee b.9xr / t1.9xr.4e).

CROSS-TASK CONTRACT
-------------------
Tasks 2 and 4 of Plan Bee b.9xr Epic A consume this contract — do not change
verb names, flag names, or JSON keys without updating those Tasks.
- Task 2 (skill-prose migration) replaces every direct `bees ...` invocation
  with `python3 ticket_backend.py <verb> ...`. Argv shape and JSON output of
  each verb is the contract.
- Task 4 (CLAUDE.md design-rules subsection) names the seven verbs and points
  readers at this docstring as the authoritative source rather than restating
  argv or JSON shapes inline.
- Sibling Epic B (`t1.9xr.4e`)'s beads adapter must produce equivalent
  normalized JSON for every verb defined here.

VERBS
-----
All verbs accept a top-level `--repo-root PATH` flag (default: current working
directory). The dispatcher resolves the backend from `<repo-root>/CLAUDE.md`
`## Ticket Backend` (defaults to `bees` when section absent — Epic A is purely
additive).

`query` — find tickets via a YAML query pipeline.
    Argv:    --query-yaml <yaml-string>
    bees:    bees execute-freeform-query --query-yaml <yaml-string>
    Stdout:  bees JSON unchanged (pass-through).
    Exit:    bees exit code propagated.

`show` — fetch one or more tickets by ID.
    Argv:    --ids <id> [<id> ...]
    bees:    bees show-ticket --ids <id> [<id> ...]
    Stdout:  bees JSON unchanged.
    Exit:    bees exit code propagated.

`list-spaces` — list registered ticket spaces (hives on bees).
    Argv:    (no flags)
    bees:    bees list-hives
    Stdout:  bees JSON unchanged. The bees response carries a `hives` key in
             Epic A; Epic B will normalize this to a backend-neutral `spaces`
             key if and when the beads adapter lands.
    Exit:    bees exit code propagated.

`create` — create a ticket.
    Argv:    --ticket-type <type> --title <title> --hive <hive>
             [--body <text> | --body-file <path>]
             [--parent <id>] [--children <json>]
             [--up-deps <json>] [--down-deps <json>]
             [--tags <json>] [--status <status>] [--egg <json>]
    bees:    bees create-ticket with the same flags (1:1 mirror).
    Stdout:  bees JSON unchanged.
    Exit:    bees exit code propagated.

`update` — update fields on one or more tickets.
    Argv:    --ids <id> [<id> ...]
             [--title <title>]
             [--body <text> | --body-file <path>]
             [--status <status>] [--tags <json>]
             [--up-deps <json>] [--down-deps <json>] [--egg <json>]
             [--add-tags <json>] [--remove-tags <json>]
             [--hive <hive>]
    bees:    bees update-ticket with the same flags (1:1 mirror).
    Stdout:  bees JSON unchanged.
    Exit:    bees exit code propagated.

`setup-spaces` — composite: create one ticket space and configure tier and
                 status vocabularies in a single dispatcher call.
    Argv:    --hive <name> --path <abs-path> [--scope <pattern>]
             [--egg-resolver <path>]
             [--child-tiers <json>]
             --status-values <json>
    bees:    Fans out to `bees colonize-hive` (always), then optionally
             `bees set-types --scope hive --hive <name> --child-tiers <json>`
             (skipped when --child-tiers is omitted), then
             `bees set-status-values --scope hive --hive <name>
             --status-values <json>`. Any non-zero exit aborts and propagates.
    Stdout (success): {"status":"success","hive":"<name>","steps_run":[...]}
             where steps_run is a subset of
             ["colonize-hive","set-types","set-status-values"] in the order
             they ran.
    Stdout (failure): bees JSON from the failing step is forwarded to stdout
             unchanged; the dispatcher exits with bees' exit code.
    NOTE: This envelope shape is dispatcher-NEW (not a bees-CLI shape), since
    no single bees subcommand performs this composite. Skills should consume
    `status` and `steps_run` directly.

`resolve-spec` — emit the egg pointer for one ticket.
    Argv:    --id <bee-id>
    bees:    Internally runs `bees show-ticket --ids <bee-id>`.
    Stdout (success): {"status":"success","ticket_id":"<id>",
                       "egg":<egg-value-as-bees-returned-it>}
    Stdout (failure): bees JSON from `show-ticket` forwarded unchanged.
    Exit:    bees exit code propagated.
    NOTE: Skill-side resolver invocation (calling `file_list_resolver.py`
    against the egg value) is OUT OF SCOPE for Epic A. Epic B's beads branch
    will run the resolver here because beads has no equivalent of bees' built-
    in `egg_resolver` hook.

EXIT CODES
----------
0  — success.
1  — generic dispatcher error (e.g., malformed `## Ticket Backend` value, IO
     failure reading CLAUDE.md). Stderr carries a human-readable message.
2  — backend `beads` requested but not yet supported in this build. Stderr
     carries a stable message naming the verb and pointing at Epic B.
N  — bees exit code N propagated unchanged for verbs that delegate to bees.

JSON ENVELOPE CONVENTIONS
-------------------------
Read verbs (`query`, `show`, `list-spaces`) and primitive write verbs
(`create`, `update`) pass the bees CLI JSON through unchanged so skills can
consume bees' field names directly. The two composite verbs (`setup-spaces`,
`resolve-spec`) emit a dispatcher-shaped envelope on success because no single
bees subcommand maps onto them; on failure, they forward the failing step's
bees JSON unchanged.
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


VERBS = (
    "query",
    "show",
    "create",
    "update",
    "list-spaces",
    "setup-spaces",
    "resolve-spec",
)


SUPPORTED_BACKENDS = ("bees", "beads")


@dataclass
class BackendInfo:
    """Resolved backend choice plus room for Epic B to attach context.

    Epic A populates only `name`. Epic B's beads branch is expected to extend
    this with per-database paths or similar; keeping the carrier shape stable
    means Epic A's verb handlers do not need to be re-plumbed when Epic B
    lands.
    """

    name: str
    extra: Dict[str, object] = field(default_factory=dict)


def _run_bees(argv: List[str]) -> int:
    """Run a single `bees ...` invocation and pass through stdout/stderr/exit.

    Output is forwarded verbatim — JSON contracts are bees' JSON, and skill
    prose parses bees' shapes directly.
    """
    proc = subprocess.run(["bees", *argv], check=False, capture_output=True)
    sys.stdout.buffer.write(proc.stdout)
    sys.stdout.flush()
    sys.stderr.buffer.write(proc.stderr)
    sys.stderr.flush()
    return proc.returncode


def _run_bees_capture(argv: List[str]) -> Tuple[int, bytes, bytes]:
    """Run `bees ...` and return (exit, stdout-bytes, stderr-bytes).

    Used by composite verbs (`setup-spaces`, `resolve-spec`) that inspect or
    repackage bees output before forwarding. On bees-failure, callers
    typically write the captured bytes through unchanged so skill prose sees
    bees' diagnostics verbatim.
    """
    proc = subprocess.run(["bees", *argv], check=False, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def _beads_not_supported(verb: str) -> int:
    """Stable error path for the beads backend in Epic A.

    Subtask t3.9xr.p6.qf.3v finalizes the message; this stub gives the
    earlier read-verb subtask a working dispatch seam without changing the
    message text later.
    """
    print(
        f"ticket_backend.py: backend 'beads' is not supported in this build "
        f"(verb: {verb}). Set '## Ticket Backend' to 'bees' in CLAUDE.md, or "
        f"wait for Epic B (b.9xr / t1.9xr.4e).",
        file=sys.stderr,
    )
    return 2


def _verb_query(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("query")
    return _run_bees(["execute-freeform-query", "--query-yaml", args.query_yaml])


def _verb_show(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("show")
    return _run_bees(["show-ticket", "--ids", *args.ids])


def _verb_list_spaces(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("list-spaces")
    return _run_bees(["list-hives"])


def _build_bees_create_argv(args) -> List[str]:
    argv = [
        "create-ticket",
        "--ticket-type", args.ticket_type,
        "--title", args.title,
        "--hive", args.hive,
    ]
    if args.body is not None:
        argv.extend(["--body", args.body])
    if args.body_file is not None:
        argv.extend(["--body-file", args.body_file])
    if args.parent is not None:
        argv.extend(["--parent", args.parent])
    if args.children is not None:
        argv.extend(["--children", args.children])
    if args.up_deps is not None:
        argv.extend(["--up-deps", args.up_deps])
    if args.down_deps is not None:
        argv.extend(["--down-deps", args.down_deps])
    if args.tags is not None:
        argv.extend(["--tags", args.tags])
    if args.status is not None:
        argv.extend(["--status", args.status])
    if args.egg is not None:
        argv.extend(["--egg", args.egg])
    return argv


def _build_bees_update_argv(args) -> List[str]:
    argv = ["update-ticket", "--ids", *args.ids]
    if args.title is not None:
        argv.extend(["--title", args.title])
    if args.body is not None:
        argv.extend(["--body", args.body])
    if args.body_file is not None:
        argv.extend(["--body-file", args.body_file])
    if args.status is not None:
        argv.extend(["--status", args.status])
    if args.tags is not None:
        argv.extend(["--tags", args.tags])
    if args.up_deps is not None:
        argv.extend(["--up-deps", args.up_deps])
    if args.down_deps is not None:
        argv.extend(["--down-deps", args.down_deps])
    if args.egg is not None:
        argv.extend(["--egg", args.egg])
    if args.add_tags is not None:
        argv.extend(["--add-tags", args.add_tags])
    if args.remove_tags is not None:
        argv.extend(["--remove-tags", args.remove_tags])
    if args.hive is not None:
        argv.extend(["--hive", args.hive])
    return argv


def _verb_create(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("create")
    return _run_bees(_build_bees_create_argv(args))


def _verb_update(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("update")
    return _run_bees(_build_bees_update_argv(args))


def _setup_spaces_bees(args) -> int:
    """Run colonize-hive, optionally set-types, then set-status-values.

    Each step's stdout/stderr is captured. On any non-zero exit, the failing
    step's output is forwarded unchanged (matching the contract for bees
    pass-through verbs) and the dispatcher exits with bees' exit code. On
    overall success, the dispatcher emits its own envelope listing the steps
    that ran.
    """
    steps_run: List[str] = []

    colonize_argv = ["colonize-hive", "--name", args.hive, "--path", args.path]
    if args.scope:
        colonize_argv.extend(["--scope", args.scope])
    if args.egg_resolver:
        colonize_argv.extend(["--egg-resolver", args.egg_resolver])
    if args.child_tiers is not None:
        colonize_argv.extend(["--child-tiers", args.child_tiers])
    rc, out, err = _run_bees_capture(colonize_argv)
    if rc != 0:
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        sys.stderr.buffer.write(err)
        sys.stderr.flush()
        return rc
    steps_run.append("colonize-hive")

    if args.child_tiers is not None:
        set_types_argv = [
            "set-types",
            "--scope", "hive",
            "--hive", args.hive,
            "--child-tiers", args.child_tiers,
        ]
        rc, out, err = _run_bees_capture(set_types_argv)
        if rc != 0:
            sys.stdout.buffer.write(out)
            sys.stdout.flush()
            sys.stderr.buffer.write(err)
            sys.stderr.flush()
            return rc
        steps_run.append("set-types")

    set_status_argv = [
        "set-status-values",
        "--scope", "hive",
        "--hive", args.hive,
        "--status-values", args.status_values,
    ]
    rc, out, err = _run_bees_capture(set_status_argv)
    if rc != 0:
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        sys.stderr.buffer.write(err)
        sys.stderr.flush()
        return rc
    steps_run.append("set-status-values")

    envelope = {
        "status": "success",
        "hive": args.hive,
        "steps_run": steps_run,
    }
    print(json.dumps(envelope))
    return 0


def _verb_setup_spaces(args, backend):
    # The forward-compat seam: backend is read from CLAUDE.md once in main()
    # and dispatched here. Epic B (b.9xr / t1.9xr.4e) drops the beads branch
    # in next to the bees branch; the early `_beads_not_supported` return is
    # what gets replaced.
    if backend.name == "beads":
        return _beads_not_supported("setup-spaces")
    if backend.name == "bees":
        return _setup_spaces_bees(args)
    return _beads_not_supported(f"setup-spaces (backend={backend.name})")


def _verb_resolve_spec(args, backend):
    if backend.name == "beads":
        return _beads_not_supported("resolve-spec")
    rc, out, err = _run_bees_capture(["show-ticket", "--ids", args.id])
    if rc != 0:
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        sys.stderr.buffer.write(err)
        sys.stderr.flush()
        return rc
    try:
        payload = json.loads(out.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(
            f"ticket_backend.py: could not parse bees show-ticket output as "
            f"JSON: {exc}",
            file=sys.stderr,
        )
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        return 1
    tickets = payload.get("tickets") or []
    if not tickets:
        # Forward bees' diagnostic JSON unchanged so callers see what bees saw.
        sys.stdout.buffer.write(out)
        sys.stdout.flush()
        sys.stderr.buffer.write(err)
        sys.stderr.flush()
        return 1
    egg = tickets[0].get("egg")
    envelope = {
        "status": "success",
        "ticket_id": args.id,
        "egg": egg,
    }
    print(json.dumps(envelope))
    return 0


VERB_HANDLERS = {
    "query": _verb_query,
    "show": _verb_show,
    "list-spaces": _verb_list_spaces,
    "create": _verb_create,
    "update": _verb_update,
    "setup-spaces": _verb_setup_spaces,
    "resolve-spec": _verb_resolve_spec,
}


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="ticket_backend.py",
        description=(
            "Dispatch ticket-backend verbs (bees today, beads in Epic B). "
            "See module docstring for per-verb argv shape, JSON output shape, "
            "and exit-code semantics."
        ),
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help=(
            "Path to the target repo root (used to read `## Ticket Backend` "
            "from <repo-root>/CLAUDE.md). Defaults to the current working "
            "directory."
        ),
    )
    subparsers = parser.add_subparsers(dest="verb", metavar="VERB")
    subparsers.required = True

    p_query = subparsers.add_parser(
        "query",
        help="Find tickets via a YAML query pipeline (mirrors bees execute-freeform-query).",
    )
    p_query.add_argument(
        "--query-yaml",
        required=True,
        help='YAML dict with a "stages" key. See bees execute-freeform-query --help.',
    )

    p_show = subparsers.add_parser(
        "show",
        help="Fetch one or more tickets by ID (mirrors bees show-ticket).",
    )
    p_show.add_argument(
        "--ids",
        required=True,
        nargs="+",
        metavar="ID",
        help="One or more ticket IDs.",
    )

    subparsers.add_parser(
        "list-spaces",
        help="List registered ticket spaces (mirrors bees list-hives; takes no flags).",
    )

    p_create = subparsers.add_parser(
        "create",
        help="Create a ticket (mirrors bees create-ticket).",
    )
    p_create.add_argument("--ticket-type", required=True)
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--hive", required=True)
    body_group = p_create.add_mutually_exclusive_group()
    body_group.add_argument("--body")
    body_group.add_argument("--body-file", metavar="PATH")
    p_create.add_argument("--parent")
    p_create.add_argument("--children", metavar="JSON")
    p_create.add_argument("--up-deps", metavar="JSON")
    p_create.add_argument("--down-deps", metavar="JSON")
    p_create.add_argument("--tags", metavar="JSON")
    p_create.add_argument("--status")
    p_create.add_argument("--egg", metavar="JSON")

    p_update = subparsers.add_parser(
        "update",
        help="Update fields on one or more tickets (mirrors bees update-ticket).",
    )
    p_update.add_argument(
        "--ids",
        required=True,
        nargs="+",
        metavar="ID",
        help="One or more ticket IDs.",
    )
    p_update.add_argument("--title")
    update_body_group = p_update.add_mutually_exclusive_group()
    update_body_group.add_argument("--body")
    update_body_group.add_argument("--body-file", metavar="PATH")
    p_update.add_argument("--status")
    p_update.add_argument("--tags", metavar="JSON")
    p_update.add_argument("--up-deps", metavar="JSON")
    p_update.add_argument("--down-deps", metavar="JSON")
    p_update.add_argument("--egg", metavar="JSON")
    p_update.add_argument("--add-tags", metavar="JSON")
    p_update.add_argument("--remove-tags", metavar="JSON")
    p_update.add_argument("--hive")

    p_setup = subparsers.add_parser(
        "setup-spaces",
        help=(
            "Composite: colonize a ticket space and configure tier and status "
            "vocabularies in a single call. Emits a dispatcher-shaped envelope "
            "on success."
        ),
    )
    p_setup.add_argument("--hive", required=True)
    p_setup.add_argument("--path", required=True, help="Absolute path for the new space.")
    p_setup.add_argument("--scope", help="Optional scope pattern.")
    p_setup.add_argument("--egg-resolver", metavar="PATH")
    p_setup.add_argument(
        "--child-tiers",
        metavar="JSON",
        help=(
            'JSON dict mapping tier keys to [singular, plural] (e.g. \'{"t1":'
            '["Epic","Epics"]}\'). When omitted, the set-types step is skipped.'
        ),
    )
    p_setup.add_argument(
        "--status-values",
        required=True,
        metavar="JSON",
        help='JSON array of allowed status strings (e.g. \'["open","done"]\').',
    )

    p_resolve = subparsers.add_parser(
        "resolve-spec",
        help=(
            "Emit the egg pointer for one ticket. Internally runs bees show-"
            "ticket and emits a dispatcher-shaped envelope on success."
        ),
    )
    p_resolve.add_argument("--id", required=True, help="Bee ticket ID.")

    return parser


def _resolve_repo_root(args) -> Path:
    if args.repo_root:
        return Path(args.repo_root).resolve()
    return Path.cwd().resolve()


# Style precedent: skills/bees-setup/scripts/detect_fast_path.py
# `_split_top_level_sections`. Tracks fenced-code-block state so a literal
# `## Ticket Backend` heading that appears inside a code block is not
# mistaken for a real section.
def _split_top_level_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, str] = {}
    current_heading: Optional[str] = None
    current_body: list = []
    in_fence = False
    for line in text.splitlines(keepends=True):
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


# Strip common Markdown decorations (list bullet, surrounding backticks, bold,
# trailing punctuation) from a section-body line so prose like `- **bees**`
# or `` `beads` `` resolves to the backend name. The caller validates the
# stripped result against SUPPORTED_BACKENDS, so over-stripping just produces
# a clear "unrecognized value" error rather than silently wrong dispatch.
_BACKEND_LINE_TRIM_RE = re.compile(r"^[\s\-\*\>`'\"]+|[\s\.,;:`'\"]+$")
_BACKEND_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def _extract_backend_value(body: str) -> Optional[str]:
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("```"):
            continue
        bold_match = _BACKEND_BOLD_RE.search(stripped)
        candidate = bold_match.group(1) if bold_match else stripped
        candidate = _BACKEND_LINE_TRIM_RE.sub("", candidate)
        if candidate:
            return candidate.lower()
    return None


def _resolve_backend(repo_root: Path) -> BackendInfo:
    """Read `## Ticket Backend` from `<repo-root>/CLAUDE.md`.

    Returns BackendInfo(name="bees") when the file or section is missing or
    empty (Epic A default — purely additive). Returns BackendInfo with the
    parsed value when present and well-formed. Calls `sys.exit(1)` with a
    stderr message when the section is present but holds an unrecognized
    value.
    """
    claude_md = repo_root / "CLAUDE.md"
    if not claude_md.is_file():
        return BackendInfo(name="bees")
    try:
        text = claude_md.read_text(encoding="utf-8")
    except OSError as exc:
        print(
            f"ticket_backend.py: could not read {claude_md}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)
    sections = _split_top_level_sections(text)
    body = sections.get("Ticket Backend")
    if body is None:
        return BackendInfo(name="bees")
    value = _extract_backend_value(body)
    if value is None:
        return BackendInfo(name="bees")
    if value not in SUPPORTED_BACKENDS:
        print(
            f"ticket_backend.py: unrecognized backend '{value}' in "
            f"{claude_md} '## Ticket Backend' (expected one of: "
            f"{', '.join(SUPPORTED_BACKENDS)}).",
            file=sys.stderr,
        )
        sys.exit(1)
    return BackendInfo(name=value)


def main():
    parser = _build_parser()
    args = parser.parse_args()
    repo_root = _resolve_repo_root(args)
    backend = _resolve_backend(repo_root)
    handler = VERB_HANDLERS[args.verb]
    return handler(args, backend) or 0


if __name__ == "__main__":
    sys.exit(main())
