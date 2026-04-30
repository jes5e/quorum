---
name: bees-file-issue
description: File a new issue ticket in the issues hive
---

## Overview

Create a new issue ticket in the issues hive. The user describes the issue and this skill creates a well-structured ticket.

## Usage

The user can call this skill in several ways:

- `/bees-file-issue` — interactive: ask the user to describe the issue
- `/bees-file-issue Some description of the problem` — create directly from the description

## Preconditions

Before doing anything else, verify the host repo is configured for the bees workflow. **Hard-fail** with the message `Run /bees-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
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
- Check if there's already an issue ticket for this issue (search existing issues hive)

### 3. Create the ticket

Use the bees CLI to create the ticket:

```bash
bees create-ticket \
  --ticket-type bee \
  --hive issues \
  --status open \
  --title "<concise title>" \
  --body "<structured body>"
```

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

Stage and commit the ticket file and any doc changes:
```bash
git add .bees/issues/ docs/
git commit -m "File issue: <title>"
```

### 6. Report back

Show the user:
- The ticket ID
- The title
- A one-line summary of what was filed
- Whether any docs were updated (and what changed)
