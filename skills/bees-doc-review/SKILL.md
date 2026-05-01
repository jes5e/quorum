---
name: bees-doc-review
description: Review documentation completeness for a change set. Primary use - invoked by `/bees-execute` and `/bees-fix-issue` during their review cycles. Standalone use - ad-hoc doc review of a diff, worktree, files, or bees ticket. Checks README and architecture docs are updated with new functionality. Returns structured list of documentation work items.
argument-hint: "[<ticket-id> | <git-ref> | <files>]"
---

## Overview

Review documentation completeness for a change set — files changed during a Task, a git diff/range, a worktree, or a bees ticket. Verify README and any architecture documents.
Concise is better than verbose. Value brevity.
The README is for human users that want to use the program.
Architecture docs should contain the high-level architecture and core technology.

**When invoked standalone** (e.g. `/bees-doc-review` from the prompt with no orchestrating skill above), the caller is a human or another standalone tool. Output the work-item list and stop. Skip the "infinite loop" concern below — that only applies inside `/bees-execute`'s review-fix-review cycle.

**When invoked by `/bees-execute` or `/bees-fix-issue`**, the caller is a team-lead agent that may loop back with a fix-and-re-review request. Apply the loop-bounding guidance below.

This skill **returns work items** — it does not apply fixes itself. The team lead (or human) decides whether and how to address each item.

## Mission

Analyze what changed, compare against current docs, return list of specific documentation gaps.

### Readme
Readme is for human users to understand how to install and run the project
- No implementation details
- No testing or unit testing details
  - This is IMPORTANT. Seriously. Don't talk about how to test the product in the Readme. 
- No discussion of security implications or requirements
- Keep it short and simple - focused on how to install and how to use
- Don't describe how to use common tools (like screen, poetry, bash etc)
Architecture docs — house style for this skill: written as an "LLM cheat sheet" so codegen agents can navigate the code base without reading all of it. (Some teams write architecture docs primarily for humans; if the project's own conventions say otherwise, follow them. The list below is the default.)
- Don't brag about or rationalize the code
  - No performance details
  - Don't describe how comprehensive the tests are or the testing strategy
  - Don't describe design decisions, trade-offs, or other designs considered
  - Don't describe what happened before — just the current state of things
  - No design patterns
- No code — that defeats the purpose, the LLM can read the code if it wants to
  - no functions, no methods
- Do add:
  - list of logical components
  - what the components do
  - how the components interact
  - how data flows through the components
  - use of resources like databases or file storage
  - schemas or API endpoints

## Workflow

### 0. Understand Project Documentation Standards

Find any documentation standards, style guides, or writing conventions in the project (e.g. `CONTRIBUTING.md`, `docs/standards.md`, architecture docs, or references in `CLAUDE.md`).
Your job is to flag gaps where the work done deviates from whatever standards are defined.

### 1. Understand What Changed

Review all commits and changed files to understand the scope of work: new features, changed behavior, new commands/APIs, config/schema changes.

### 2. Review Current Documentation

Read README.md and Architecture docs to understand current state.

### 3. Find Documentation Gaps

**README.md** (user-focused, concise):
- Install instructions correct?
- Updated setup/dependencies?
- Are CLI commands and API references correct?
- If outdated, return a work item ("Update README §X — Y is now Z"). If correct, LEAVE IT ALONE!


**Architecture Docs** (cheat sheet for llms):
- Has the high-level architecture changed?
- Have new components been introduced or old ones removed?
- Schema/API changes?
- Data flow still accurate?
- If yes, return a work item describing what's stale. If no, LEAVE IT ALONE!


### 4. Check for Inconsistencies
Look for docs that are now incorrect: outdated commands, deprecated features still shown, changed file paths, old config formats.

### 5. Find and reduce duplication and waste
- Look for sections of the docs that repeat information and suggest removing them.
- Look for sections of the doc that are too verbose and recommend ways to compact them without losing meaning
- Ensure docs serve the right purpose:
  - Readme is a user manual
  - Architecture docs are a cheat sheet for LLMs to understand the architecture and core technology

### 6. Output Work Items

Return specific, actionable items as numbered list:

```markdown
## Documentation Review Work Items

1. Update README.md Quick Start - add `new-command` usage
2. Mark Component X as Implemented in architecture docs:289
3. Remove deprecated `old-cmd` from README Commands section
```

Or if no issues:
```markdown
## Documentation Review Work Items

No documentation issues found. README and architecture docs are up to date!
```

NOTE: It is OK to return "no issues found". Only return issues if they are very important.

**When invoked from `/bees-execute` or `/bees-fix-issue`**: the team-lead agent will loop back with fixes and re-invoke this skill. If you never return "no issues found", the workflow goes into an infinite loop. Be selective — return real gaps, not nice-to-haves.
**Important**
- Docs are wrong
- Readme is missing information the user needs to use the app
**Not Important**
- Formatting issues
- Grammar

**Work item quality:**
- Be specific: include file, section, line number when possible
- Be actionable: "Update X section - add Y detail" not "docs need work"
- Focus on user-visible changes and breaking changes
- Skip trivial wording/style issues

**Priority guide:**
1. Critical: New commands, changed APIs, altered workflows
2. Important: Component status, schema changes, new features
3. Nice-to-have: Enhanced examples, clarifications

