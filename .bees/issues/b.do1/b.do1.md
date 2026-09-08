---
id: b.do1
type: bee
title: Make Bash-mediated file edits fail loudly in engineer and test-writer role prose so auto mode is safe
status: open
created_at: '2026-09-08T17:00:11.344687'
schema_version: '0.1'
reference_materials: null
guid: do1si5eaes6mownnkbp79f9ue4x77acw
---

## Description
Claude Code auto mode injects a session-level instruction to make file changes with sed, heredocs, or short scripts rather than the Read/Edit/Write tools, falling back to a dedicated tool only when Bash genuinely cannot do the job. Dispatched subagents inherit it. Stacked with the shipped shell-etiquette bullet in agents/engineer.md (and its twin in agents/test-writer.md), which routes multi-step logic to a script file rather than a heredoc, the only compliant edit path in auto mode is "write a Python script, run it" — even for a two-hunk doc-comment change.

## Current behavior
In auto mode the Engineer writes and runs an ad hoc Python script for small edits. Nothing in the role prose constrains how that script performs the replacement, so a stale or ambiguous anchor can silently no-op or double-apply. Outside auto mode the Engineer uses Edit, which errors loudly on a stale or non-unique anchor. Observed in a downstream repo using quorum; the Engineer confirmed it would have used Edit if left to its own judgment.

## Expected behavior
When file edits must go through Bash, the role prose directs the Engineer and Test Writer to do them from a Python helper file that reads the file, asserts the anchor text occurs exactly once, replaces it, and writes back — never via `sed -i` or a regex substitution. This restores Edit's loud-failure guarantee in every permission mode and stays cross-platform (design rule 2).

## Impact
Correctness: silent bad edits in auto mode can reach review undetected. Cost: extra tokens per small edit (accepted; not addressed by this ticket).

## Suggested fix
1. agents/engineer.md `**Shell-command etiquette.**` bullet (~line 66) and the twin in agents/test-writer.md (~line 132): add the exact-once anchor-assertion rule for Bash-mediated edits described above.
2. Optional polish in the same bullets: note that the one-literal-command etiquette exists to avoid permission-prompt churn and may be relaxed when the session is in auto mode (the injected block is visible in context), since that rationale largely evaporates there.
3. Optional follow-on: a README caveat near the recommended-session-settings table that auto mode adds per-edit token overhead. Not a safety concern once (1) lands.

## Background and rationale
Verified in-session by toggling auto mode on and observing the injected block appear. The script-to-file rule did not choose Bash over Edit; the harness block did. The etiquette rule only shaped "script file" versus "heredoc" once Bash was already chosen, so conditioning that rule on auto mode would not bring Edit back — it would only save one Write call. The actual loss is the loud-failure property, which is what the fix targets. agents/doc-writer.md is unaffected (no Bash tool, so auto mode has nothing to steer it to); agents/pm.md never edits files.

## Decisions and rejected alternatives
- Rewording the role files to prefer Edit over the harness instruction: rejected. Repo prose cannot outrank a system-level instruction; the outcome would be narration, not compliance.
- Telling users never to run the execution skills in auto mode: rejected as the primary fix. Auto mode is sometimes the right choice; the workflow should be safe in it rather than forbid it.
- Making the script-to-file rule conditional on auto mode: demoted to optional polish (item 2) because it does not address the safety property.

## Doc divergence noted
Doc gap, not a wrong claim: README.md (Customer-facing docs) says nothing about how Claude Code's auto mode interacts with the execution skills. Item 3 above covers it.

