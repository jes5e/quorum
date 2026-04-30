---
name: test-review
description: Review test files for quality, coverage, and correctness across a change set. Returns a simple list of improvement work items.
---

## Overview

This skill reviews test files in a change set — files changed during a Task, a git diff/range, a worktree, or a bees ticket.
It returns a list of improvement work items for the caller to review.
Be thorough but not pedantic — focus on substance over style.

**When invoked standalone** (e.g. `/test-review` from the prompt with no orchestrating skill above), the caller is a human or another standalone tool. Output the work-item list and stop. Skip the "infinite loop" concern below — that only applies inside `/bees-execute`'s review-fix-review cycle.

**When invoked by `/bees-execute` or `/bees-fix-issue`**, the caller is a team-lead agent that may loop back with a fix-and-re-review request. Apply the loop-bounding guidance under Step 3.

## Parameters

You will receive some instructions on which set of work to review — a list of files, a git diff/range, a worktree, or a bees ticket.

## Your Mission

Analyze changed test files and return a focused list of actionable improvement work items.
Understand the work context from the user input.
Review all commits and changed test files.
- Focus only on test files. Ignore source code files and natural language documentation.
If no test files were changed, output "No test files to review" and exit.

### Step 0: Understand project best practices

Find any testing best practices and architecture documentation and understand them.
Your job is to provide feedback where test work deviates from the guidance therein.
You may presume the previous agents left the tests in a working state, you do not need to run them.

### Step 1: Load the Test Suite Index, Then Read Selectively

Use Glob to find all test files in the project (e.g. `**/test_*.py`, `**/*.test.ts`, `**/*_test.go`, `**/tests/*.rs`, etc.). Read the **full file list and quickly scan file names** — that's the index of what tests exist.

Then read in full:
- **Every changed test file** (the focus of the review)
- **Every existing test file that overlaps with the code under test in the changed files** — i.e., tests that target the same module/function/component as the changes. Use the imports / file naming / `describe`-block / module declarations to decide overlap.

You need the cross-file picture to identify cross-file duplication, redundancy, and parameterization opportunities. But on a large suite (hundreds of files, tens of thousands of lines), reading everything blows the context budget — be selective. The index of file names plus the overlapping files is enough to spot near-duplicates without reading the entire suite.

If the project's test suite is small (under a few thousand lines total), reading everything is fine.

### Step 2: Review Changed Test Files - Critical Eye

With the full suite loaded, review the changed files and check for issues:

#### 1. Coverage Gaps
- New functions or behaviors in the codebase with no corresponding tests
- Missing edge cases (empty inputs, null/None, boundary values, max/min)
- Missing error/exception cases (only happy path tested)
- Missing negative tests (things that should fail but aren't verified)

**Scenario-matrix check for blocking-input / timing-sensitive paths** — apply only if the changed code includes a blocking I/O path or a timing-sensitive wait. Skip if the changes are pure logic / data transformations.

When applicable: any code path that waits on an external input (blocking I/O, BLOCK timeout, long poll, subscription receive, queue dequeue, gRPC streaming read, etc.) needs tests for the following scenarios. If any are missing, add them to the work-item list:

| Scenario | What to test |
|---|---|
| Input arrives immediately | Happy path before any timeout fires |
| Input arrives after a short delay | Wake-up from the waiting state works |
| Input never arrives (full idle) | Code handles the native timeout/no-input case cleanly; does NOT close, error, or leak |
| Input arrives in a burst (many at once) | All inputs are delivered in order, nothing dropped/coalesced by accident |
| Cancellation during the wait | Cleanup runs promptly; no leaked resources |
| Input arrives during cancellation | No delivery-after-cancel; state is consistent |

The "input never arrives" row is the one most commonly missing — tests usually set up an input before asserting, which never exercises the native-timeout path. If the production code uses a library-level block/poll/wait (examples: a Redis client's `XREAD BLOCK`, a Kafka consumer's `poll`, an in-process channel's `recv_timeout`, a long-poll HTTP handler), the test must exercise a wait that exceeds that library's timeout to catch issues in how the library's timeout reply is interpreted.

#### 2. Test Correctness
- Tests that assert the wrong thing (incorrect expectations)
- Tests that would pass even if the code is broken (vacuous tests)
- Tests checking implementation details instead of behavior
- Mocks/stubs that don't accurately reflect real dependencies
- Assertions that are too loose (e.g., `assert result is not None` when you should check the value)

#### 3. Test Structure & Quality
- Tests that do too much in one test (should be split)
- Poor test names (unclear what behavior is being verified)
- Missing or incorrect setup/teardown
- Shared mutable state between tests (causes flakiness)
- Tests that depend on execution order

#### 4. Bloat & Redundancy (HIGH PRIORITY)
This is one of the most common and damaging issues in test suites. Be aggressive here.
- **Parameterization opportunities**: Multiple test functions that run the same logic with different inputs — these should be collapsed into a single parameterized test (`@pytest.mark.parametrize`, `test.each`, etc.). Even 2-3 near-identical tests are a candidate.
- **Duplicate coverage**: Tests that assert the same behavior already covered elsewhere — find and flag them specifically
- **Copy-paste tests**: Blocks of nearly identical setup/assertion code repeated across tests — extract shared fixtures or helpers
- **Over-specified tests**: Tests that assert many things that are already covered by other tests; trim to what's unique
- When flagging these, always cite the specific test names and line numbers so the fix is unambiguous

#### 5. Stale/Obsolete Tests
- Old tests that are no longer valid given code changes
- Tests that test code which no longer exists

#### 6. Test Anti-patterns
- No assertions (test always passes)
- `except` that swallows failures silently
- Hardcoded sleep/delays (use mocks or event-based waits)
- External I/O in unit tests (network calls, file system) without mocking
- Tests that are too tightly coupled to internal implementation

### Step 3: Prioritize and Filter

Focus on important issues only:
- **Include:** Missing coverage for new code, incorrect assertions, flaky patterns, stale tests
- **Exclude:** Minor style issues, trivial naming nitpicks, personal preferences

Each work item should be:
1. Actionable as a standalone follow-up
2. Specific (includes file:line where applicable)
3. Important (not trivial)
4. Concise (one line description)
5. Applicable (understand requirements and don't aim for more than is needed)

NOTE: It is expected that many times you will return no important issues.
This is OK. Don't feel obliged to report things. Only report if there is something important.

**When invoked from `/bees-execute` or `/bees-fix-issue`**: the team-lead agent will loop back with fixes and re-invoke this skill. If you keep reporting trivial-but-not-important items each pass, you create an infinite loop. Be selective. If you have nothing important, say so.

### Step 4: Generate Work Item List

Output a simple numbered list directly in your response:

```markdown
## Test Review Work Items

1. Parameterize test_validates_empty/test_validates_null/test_validates_whitespace in test_input.py:10-40 - identical logic, different inputs
2. Remove test_create_returns_data() in test_orders.py:88 - duplicate of test_create_order():55 which already asserts the same fields
3. Fix incorrect assertion in test_cache.py:88 - expects 200 but endpoint returns 201 on create
4. Remove test_legacy_flow() in test_api.py:200 - tests deleted endpoint, always passes vacuously
5. Mock external HTTP call in test_fetcher.py:55 - test makes real network request, causes flakiness
```


