---
name: bees-file-issue
description: File a new issue ticket in the issues hive
argument-hint: "[<description>]"
---

## Overview

Create a new issue ticket in the issues hive. The user describes the issue and this skill creates a well-structured ticket.

## House style: bundle related issues

When filing issues, **default to bundling related items into fewer tickets** rather than splitting them along human-triage lines. The bees workflow is optimized for agent work efficiency: per-ticket overhead — read scope, load context, write tests, commit — is the cost to minimize, not human-triage legibility.

Split into separate tickets only when:

- Issues are truly independent (no shared code paths, no shared tests, no shared mental model required to fix them)
- Different status / priority lifecycles are needed
- One genuinely blocks another and they need separate tracking

Don't split along categorical lines (e.g. "memory leak vs correctness vs doc fix") if the fixes touch the same module or can share a single pass through the code. A bundled ticket with clearly-labeled sub-findings inside the body is the right shape.

This is workflow-level house style. Projects that disagree (e.g., projects with human triage workflows) can override in their CLAUDE.md or via project-specific instructions to the agent calling this skill.

## Usage

The user can call this skill in several ways:

- `/bees-file-issue` — interactive: ask the user to describe the issue
- `/bees-file-issue Some description of the problem` — create directly from the description

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Issues hive is colonized for this repo (the dispatcher's `list-spaces` verb — `python3 "<this skill's base directory>/../_shared/scripts/ticket_backend.py" list-spaces`, base directory is shown in the skill invocation header at session start — must return an entry whose `normalized_name` is `issues`).
- CLAUDE.md contains a `## Documentation Locations` section. Step 4 (doc-update check) reads architecture/customer-doc paths from this section by exact key.

Note: bees-file-issue does **not** require CLAUDE.md `## Build Commands`. bees-file-issue only files a ticket — it doesn't run any build/test/lint/format command. The Build Commands section is needed by `/bees-fix-issue` and `/bees-execute` when they actually execute the work, not at filing time.

If the precondition is missing, stop with `Run /bees-setup first.` and direct the user there.

## Steps

### 1. Gather issue information

If called without arguments, use AskUserQuestion to ask:
- "What's the issue?" (free text description)

If called with arguments, use those as the description.

### 2. Research the issue (optional)

If the description references specific code, files, or behavior:
- Read the relevant source files to understand the current state
- Check if there's already an issue ticket for the same problem. Query the open issues in the issues hive via the bundled dispatcher (resolved at `<this skill's base directory>/../_shared/scripts/ticket_backend.py` — base directory is shown in the skill invocation header at session start) and scan returned titles for overlap with the user's description:

  ```bash
  python3 "<this skill's base directory>/../_shared/scripts/ticket_backend.py" query --query-yaml 'stages:
    - [type=bee, hive=issues, status=open]
  report: [title]'
  ```

  If a clear duplicate exists, surface it to the user and ask whether to file anyway (sometimes a near-duplicate captures a different angle), append to the existing ticket, or stop.

### 3. Create the ticket

Author the structured body to a temp file via the `Write` tool, then pass `--body-file <path>` to the dispatcher's `create` verb. Do not inline a multi-paragraph body as a `--body "..."` argument: bodies containing a newline followed by a `#` heading trip Claude Code's command-injection guard and force a permission prompt regardless of the user's allowlist, and inlined markdown is also fragile to shell quoting (backticks, dollar signs, quotes). A short path argument clears both problems. Status-only updates with no body (e.g. an `update --ids <id> --status done` invocation) and genuinely single-line bodies can stay on inline `--body`. Steps:

1. Pick a temp path under the OS temp dir: `/tmp/bees-body-<short-suffix>.md` on POSIX, `$env:TEMP\bees-body-<short-suffix>.md` on Windows.
2. Use the `Write` tool to write the structured body to that path.
3. Run the dispatcher command (the file-flag carries no shell-quoting surface — only the line-continuation character differs between OSes):

   ```bash
   # POSIX (bash / zsh):
   python3 "<this skill's base directory>/../_shared/scripts/ticket_backend.py" create \
     --ticket-type bee \
     --hive issues \
     --status open \
     --title "<concise title>" \
     --body-file <path>

   # Windows (PowerShell):
   python "<this skill's base directory>\..\_shared\scripts\ticket_backend.py" create `
     --ticket-type bee `
     --hive issues `
     --status open `
     --title "<concise title>" `
     --body-file <path>
   ```

4. Remove the temp file after the dispatcher command exits.

**Title guidelines:**
- Under 80 characters
- Starts with a verb or describes the symptom
- Include a spec-doc section reference if the issue ties to a documented requirement (use the actual doc name from CLAUDE.md "Documentation Locations")

**Body structure:**
```markdown
## Description
<What's wrong — the symptom or deviation from expected behavior>

## Current behavior
<What happens now>

## Expected behavior
<What should happen, with a spec-doc reference if applicable (use the doc paths from CLAUDE.md "Documentation Locations")>

## Impact
<Correctness, performance, or UX impact>

## Suggested fix
<Brief description of what needs to change, key files involved>
```

### 4. Check if any project documentation needs updating

Review whether the issue description implies the project's spec docs contain incorrect information. Use the paths configured in CLAUDE.md `## Documentation Locations` — specifically `Internal architecture docs` (the SDD-equivalent) and `Customer-facing docs` (the README-equivalent). The Documentation Locations section has no canonical "PRD" key; if the project has a PRD-equivalent at a known path, include it in the review, otherwise skip the PRD-update step.

Examples of doc divergence to watch for:
- Documenting behavior that is now known to be wrong
- Missing config variables or wrong defaults
- Wrong API contracts or field names
- Incorrect architecture descriptions

If the docs describe the buggy behavior as correct (or are missing information the issue reveals), update them now so they reflect the intended/correct behavior. This keeps docs accurate before the bees-fix-issue skill runs.

### 5. Commit the ticket (and any doc updates)

Stage and commit the ticket file and any doc changes. **Do not hardcode the `.bees/issues/` path.** `/bees-setup` lets the user choose where each hive lives — in-repo, sibling-to-repo, or anywhere else. A hardcoded `git add .bees/issues/` silently stages nothing when the user picked a sibling path.

Resolve the Issues hive path via the dispatcher's `list-spaces` verb. Run the verb as a single literal command and parse its JSON stdout in your reasoning — locate the entry whose `normalized_name` is `issues` and read its `path` field — rather than piping or redirecting in shell. Then run `git rev-parse --show-toplevel` separately to learn the repo root, and only stage the Issues hive path if it sits inside the repo. Stage `docs/` only if it was modified during this run.

```bash
# POSIX (bash / zsh) and Windows (PowerShell) — single command:
python3 "<this skill's base directory>/../_shared/scripts/ticket_backend.py" list-spaces
```

```bash
# POSIX (bash / zsh):
git add docs/ <issues_path_if_in_repo>
git commit -m "File issue: <title>"
```

```powershell
# Windows (PowerShell):
git add docs/ <issues_path_if_in_repo>
git commit -m "File issue: <title>"
```

When comparing the Issues hive path to the repo root, normalize separators — `git rev-parse --show-toplevel` returns forward slashes on Windows while the dispatcher passes through whatever bees recorded (which may be backslashes); compare both sides on the same form before deciding whether to stage. If the Issues hive lives outside the repo, commit the doc/ changes here and remind the user that the issue ticket is stored separately (the dispatcher persists it through bees; no git tracking needed for the ticket file itself). If `docs/` was not modified, drop it from the `add` list as well.

### 6. Report back

Show the user:
- The ticket ID
- The title
- A one-line summary of what was filed
- Whether any docs were updated (and what changed)
