---
id: b.dkw
type: bee
title: Standardize transient scratch files under <tempdir>/.bees-workflow/, never delete
status: open
created_at: '2026-05-03T14:27:18.837295'
schema_version: '0.1'
egg: null
guid: dkw8krya1ucbnvkc7j8w6cy5qdopc7dc
---

## Description

Skills currently write `--body-file` scratch (and other transient files) into the OS temp dir at unpredictable, unnamespaced paths (e.g., `/tmp/bees-body-<suffix>.md`). This makes the artifacts hard to identify after a run, hard to clean up safely, and impossible to allowlist with a tight pattern. The skill prose has no shared rule for *where* these files go or *who* cleans them up, so each skill ad-libs.

## Current behavior

- Each skill picks its own scratch path under the OS temp dir. The naming convention is loose and per-skill.
- `bees-file-issue` instructs the caller to remove the temp file after the bees command exits — i.e., mid-workflow cleanup. Other skills may or may not do the same.
- There is no convention that lets a user (or a later skill run) identify "files this workflow created" vs. unrelated temp-dir contents.
- If a workflow crashes, the artifacts may or may not survive depending on which skill was running, leaving inconsistent debugging surface.

## Expected behavior

A single shared rule that all skills follow:

1. **Always write transient `--body-file` (and similar) scratch under `<tempdir>/.bees-workflow/`**, where `<tempdir>` is `/tmp` on POSIX and `%TEMP%` on Windows. Resolve via Python's `tempfile.gettempdir()` when a helper is involved, or paired POSIX-bash + PowerShell snippets when inline. Create the `.bees-workflow` subdir if it doesn't exist.
2. **Never delete on any OS.** The footprint is small (KBs per run, low-MB after heavy use). Linux/macOS clean `/tmp` on a days-to-reboot cadence; Windows users can clean `%TEMP%\.bees-workflow` manually whenever they want. Eliminating mid-run cleanup avoids permission-prompt churn and leaves artifacts around for debugging when a run crashes.
3. **Document the location in the README** so users know where to look and that the dir is safe to delete anytime.

This approach was chosen over a per-skill cleanup-with-allowlist design because Claude Code permission patterns are prefix-matched on the literal command string, so an allowlist entry like `Bash(rm /tmp/.bees-workflow/**)` would also match `rm /tmp/.bees-workflow/../../etc/something` — a path-traversal-shaped failure under prompt injection. Skipping cleanup entirely sidesteps the security question.

## Impact

- **Discoverability:** users can find every scratch file the workflow created in one well-known dir.
- **Safety:** no `rm`-pattern allowlist entries needed, so no path-traversal escape surface.
- **Friction:** no mid-run permission prompts for cleanup commands.
- **Debuggability:** crashed runs leave artifacts in a known place.
- **Consistency:** one rule across all skills and both OS families, easy for skill authors and reviewers to enforce.

## Suggested fix

1. Add a new section to `CLAUDE.md` (this repo's, not the target repo's) — likely under "Bash etiquette" or a new "Scratch-file convention" heading — stating the `<tempdir>/.bees-workflow/` rule and the no-delete policy. Make it a review criterion alongside the three design rules.
2. Audit every skill that writes a `--body-file` or similar scratch path and update the prose to use `<tempdir>/.bees-workflow/<name>`. Known sites at minimum:
   - `skills/bees-file-issue/SKILL.md` (step 3 — currently writes to `/tmp/bees-body-<suffix>.md` and removes after; both lines need to change).
   - Any other skill that authors body files (sweep with a grep for `body-file`, `tempfile`, `/tmp/`, `$env:TEMP`).
3. Update paired POSIX-bash + Windows-PowerShell snippets accordingly. Where Python helpers do the writing, route through `tempfile.gettempdir()` + `.bees-workflow` subdir.
4. Add a short "Scratch files" note to `README.md` telling users where the dir lives per-OS and that it's safe to delete.
5. Remove any "remove the temp file after the bees command exits" instructions from skill prose.

Key files: this repo's `CLAUDE.md`, `README.md`, `skills/bees-file-issue/SKILL.md`, plus whatever the audit in step 2 surfaces.

