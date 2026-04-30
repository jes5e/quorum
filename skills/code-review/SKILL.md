---
name: code-review
description: Perform code review of a change set. Returns a simple list of improvement work items.
---

## Overview

This skill performs code review on a change set — files changed during a Task, a git diff/range, a worktree, or a bees ticket.
It returns a list of improvement work items for the caller to review.
Be thorough but not pedantic — focus on substance over style.

**When invoked standalone** (e.g. `/code-review` from the prompt with no orchestrating skill above), the caller is a human or another standalone tool. Output the work-item list and stop. Skip the "infinite loop" concern below — that only applies inside `/bees-execute`'s review-fix-review cycle.

**When invoked by `/bees-execute` or `/bees-fix-issue`**, the caller is a team-lead agent that may loop back with a fix-and-re-review request. Apply the loop-bounding guidance under Step 3.

## Parameters

You will receive some instructions on which set of work to review — a list of files, a git diff/range, a worktree, or a bees ticket. Read the input carefully to determine what's in scope.

## Your Mission

Analyze changed code files and return a focused list of actionable improvement work items.
Understand the work context from the user input.
Review all commits and changed files.
- Focus only on source code files. Ignore natural language documentation and unit test code.
If no code files were changed, output "No code files to review" and exit.

### Step 0: Understand project best practices
Find any engineering best practices and architecture documentation and understand them.
Your job is to provide feedback in any case where the work done deviates from the guidance therein.
**Human Pro Tip**: Place references to your project-specific best-practices documents in the project's `CLAUDE.md` (at the repo root).

### Step 1: Run Linter

If the project has linters/formatters configured (ruff, black, eslint, etc.), run them:
Note any linting issues that should be fixed.

### Step 2: Review Changed Files - Critical Eye

For each changed file, use Read to load it and check for issues across these categories (in addition to any project specific best practice):

#### 1. Dead/Obsolete Code
- Commented-out code that should be removed
- Unused functions, variables, or imports
- Old implementations left behind
- Debugging code (print statements, console.log, TODO comments)

#### 2. Architecture & Design
- Inconsistent interfaces (does this match existing patterns?)
- Inappropriate mixing of concerns (business logic, API, data access should be separated)
- Unnecessary abstractions (YAGNI - You Aren't Gonna Need It)
- Inconsistent patterns with the rest of the codebase

#### 3. Security & Correctness (CRITICAL)

Check for security vulnerabilities (apply with the language and stack of the project in mind — examples below are illustrative, not prescriptive):
- Input validation: all user inputs should be validated using the language's standard validation/parsing (Pydantic in Python, zod / typescript-types in TS, serde/validator in Rust, encoding/json + manual checks in Go, etc.)
- SQL queries: must use parameterized queries (`?`, `:param`, prepared statements, query-builder bindings), never string interpolation/concatenation
- File paths: validate paths against an allowed workspace root using the language's standard path API (Python `pathlib.Path`, Node `path` + `fs.realpath`, Rust `std::path::Path` + `canonicalize`, Go `filepath.Clean` + base-prefix check)
- API keys / secrets: loaded from environment/config/secret store, never hardcoded
- Authentication: proper checks on protected endpoints; deny-by-default
- Error messages: no sensitive data in error responses (no internal paths, stack traces, raw DB errors)

#### 4. Code Quality
- Long/complex functions — projects vary, but as **default heuristics**: >50 lines or >3 levels of nesting deserve a second look. Override these defaults from the project's engineering best practices doc (see Step 0) if it specifies its own thresholds.
- Repeated code blocks (DRY violations) — but watch out for premature abstraction; three similar lines is better than the wrong abstraction
- Magic numbers/strings (should be named constants)
- Poor variable/function names (unclear purpose)
- Missing comments for complex logic — the *why*, not the *what*
- Catch-all error handlers that swallow exceptions silently (anti-pattern in any language)

#### 5. Error Handling
- Catch-all handlers that swallow specific exceptions silently (Python `except:`, JS `catch (e) {}`, Rust `let _ = ...?`, Go `_ = err`, etc.)
- Resources not properly cleaned up — use the language's idiomatic cleanup mechanism (Python context managers, JS `finally` / `using`, Rust RAII / `Drop`, Go `defer`, C# `using`)
- Missing error handling in critical paths
- Poor error messages (not actionable for users)

#### 6. Performance
- Database queries in loops (N+1 problem)
- Loading entire files into memory (should stream)
- No connection pooling for databases
- Synchronous I/O in async functions
- Missing cache invalidation

#### 7. Cross-File / Cross-Call-Site Interactions (CRITICAL — often missed)

These are the issues per-Task reviews structurally miss because reviewers typically only look at the diff. Extend the viewport deliberately:

- **Reverse-dependency check**: for every function, method, or public API the diff *modifies* (signature, ordering, return value, side effects), grep for callers in the rest of the codebase. For each caller, read enough context to verify the caller's assumptions still hold. Flag any caller whose implicit contract with the modified code is now violated. Example: if a diff reorders the steps inside an `auth_middleware` so user lookup runs before signature verification, callers in the request handler that assumed signature-first ordering ("by this point the request is verified") must be re-verified.
- **Implicit contract check**: if this diff's code comments or docstrings describe behavior that another file/function depends on (especially "this should never happen" / "defensive branch" / "unreachable" / "by the time we get here, X is true"), verify that the *actual* behavior of the collaborator still satisfies the invariant. Comments routinely lag the code they describe.
- **Pre-existing code exposed by new usage**: if the diff introduces a new call pattern for an unchanged function (new call site, new frequency, new argument combination), mentally run that unchanged function under the new pattern and flag any latent assumptions the new pattern breaks. Example: `get_user_profile(id)` is fine when called once per request from the request hot path, but a new batch endpoint that calls it for hundreds of IDs in a tight loop may miss the per-request memoization reset and leak stale data from the prior request into the next.
- **Cumulative resource accounting**: if the diff adds acquires from a bounded resource (connection pool, semaphore, mutex, queue slot), model the aggregate behavior across all call sites — including call sites in *other* files not touched by this diff. Flag starvation scenarios and lifetime-mismatch interactions (e.g., short-lived API request handlers competing for a connection pool against a new long-lived background worker that holds connections across many requests — at steady state the long-lived consumer can starve the request path).
- **Symmetric-change check**: if the diff adds a *new* resource (key, file, queue, pool entry, etc.), search for every code path that cleans up the sibling resource class and verify the new resource is handled symmetrically. Example: adding a new `cache:user:{id}:permissions` key class in the write path requires the cache-invalidation path, the user-deletion path, and any periodic-purge job to all DELETE this key class — otherwise stale-permissions data leaks past role changes.

### Step 3: Prioritize and Filter

Focus on important issues only:
- **Include:** Security vulnerabilities, logic errors, missing tests, architecture problems
- **Exclude:** Trivial style issues, minor naming nitpicks, personal preferences

Each work item should be:
1. Actionable as a standalone follow-up
2. Specific (includes file:line where applicable)
3. Important (not trivial)
4. Concise (one line description)
5. Applicable (understand requirements and don't aim for more than is needed)

NOTE: It is expected that many times you will return no important issues.
This is OK. Don't feel obliged to report things. Only report if there is something important.

**When invoked from `/bees-execute` or `/bees-fix-issue`** specifically: keep in mind that the team-lead agent will loop back with fixes and re-invoke this skill. If you keep reporting trivial-but-not-important items each pass, you create an infinite loop. Be selective. If you have nothing important, say so.

### Step 4: Generate Work Item List

Output a simple numbered list directly in your response:

```markdown
## Code Review Work items

1. Fix SQL injection in transactions.py:85 - use parameterized queries instead of f-strings
2. Add input validation to cache.py:45 endpoint - validate user input format
3. Refactor process_transactions() in llm_categorizer.py:120 - function is 60 lines, extract helper functions
4. Remove commented-out code in llm_categorizer.py:200-210
```

