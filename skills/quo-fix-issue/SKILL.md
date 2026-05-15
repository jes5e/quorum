---
name: quo-fix-issue
description: Fix an issue described in a Bee ticket. Use '/quo-fix-issue all' to fix all open issues sequentially, or '/quo-fix-issue <id1> <id2> ...' (space- and/or comma-delimited) to fix an explicit subset.
argument-hint: "[<issue-id> | <url> | <id-or-url> ... | all]"
---

## Overview

The user can call this skill in six ways:
- `/quo-fix-issue` — list all open issues, ask user which one to fix
- `/quo-fix-issue <issue-id>` — fix a specific issue
- `/quo-fix-issue <id1> <id2> <id3>` — fix an explicit list of issues, sequentially, in the order given. IDs may be separated by spaces, commas, or any mix (e.g. `b.cnb,b.sgq b.xet` is valid)
- `/quo-fix-issue <url>` — file the URL as an Issue first via `/quo-file-issue`, then fix the resulting Issue (e.g. `/quo-fix-issue https://github.com/example/repo/issues/123`)
- `/quo-fix-issue <id-or-url> ...` — mixed list of ticket IDs and URLs interleaved, processed in the order given; each URL is filed as an Issue first and substituted in place (e.g. `/quo-fix-issue b.cnb https://github.com/example/repo/issues/123 b.xet`)
- `/quo-fix-issue all` — fix ALL open issues sequentially without user intervention

## Preconditions

Before doing anything else, verify the host repo is configured for quorum. **Hard-fail** with the message `Run /quo-setup first.` (plus a one-line note about what is missing) if any of the following are absent:

- The eight required custom subagent types are registered in the running Claude Code session: `engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`. Custom subagents are loaded at Claude Code session start, so a fresh install requires a Claude Code restart (or `/agents` to hot-reload) before the skill can dispatch them. If any of the eight is missing at run-time, the orchestrator STOPS at the precondition gate and emits the hard-fail message — there is no fallback to `general-purpose`, no skipping the dispatch, and no improvising substitute roles. The hard-fail message must direct the user to (a) verify the install per `README.md` `## Install` AND (b) restart Claude Code or run `/agents` to hot-reload, e.g.: `Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.`
- The Issues hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `issues`).
- The Specs hive is colonized for this repo (`bees list-hives` must include a hive whose `normalized_name` is `specs`). If absent, hard-fail with `Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).`
- CLAUDE.md contains a `## Documentation Locations` section. The PM and Doc Writer roles read architecture/customer-doc paths from this section by exact key.
- CLAUDE.md contains a `## Build Commands` section with all five required keys: `Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`. The Engineer reads compile/format/lint/test commands from this section by exact key.

Rationale: the workflow reads project-specific commands and doc paths from CLAUDE.md instead of hardcoding language-specific tooling, so the skill works on Rust, Node, Python, Go, etc. without per-skill editing. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems — silently running the wrong commands would mask real failures.

If any precondition is missing, stop with `Run /quo-setup first.` and direct the user there. Do not improvise commands or guess paths.

**Verifying the subagents precondition.** Verification is a hybrid of two complementary mechanisms:

- **Procedural gate (load-bearing primary).** If a dispatch later in the run hits an `Agent type '<name>' not found`-style error from the Agent tool for any of the eight required subagent types, the orchestrator STOPS, emits the hard-fail message above, and exits — no fallback to `general-purpose`, no skipping the dispatch, no substitute role. This gate is honest about Claude Code's session-load semantics (subagents are loaded at session start; mid-session installs require a restart or `/agents` hot-reload) and cannot be bypassed by token-budget pressure or model creativity, because it fires at the natural failure point.
- **Upfront fast-fail (opportunistic, belt-and-braces).** Before any dispatch is attempted, run `claude agents` to enumerate registered subagents and verify each of the eight literal names (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`) is present. The command prints one line per agent in the form `  <name> · <model>` under a `User agents:` heading, exits cleanly without spawning an interactive UI, and is safe to invoke from inside a running Claude Code session. If any of the eight names is absent from the output, hard-fail per the message above. This catches the missing-restart case upfront and saves the user one wasted dispatch turn.

```bash
# POSIX (bash / zsh):
claude agents
```

```powershell
# Windows (PowerShell):
claude agents
```

After running the command, scan its output for the eight required names; hard-fail if any are missing. If `claude agents` itself is unavailable (older Claude Code build, etc.), skip the upfront check — the procedural gate still catches the failure at first dispatch.

## Execution Flow

### 1. Determine which issues to fix

Parse the argument string. Split on any run of commas and/or whitespace; discard empty tokens. Each token is then classified by shape: a token starting with `http://` or `https://` is a **URL token**, anything else is treated as a **ticket-ID token** (validated downstream). URL tokens space-and-comma-delimit identically to ticket-ID tokens — the tokenization itself is unchanged. The resulting tokens determine the mode:

- **Zero tokens** (no arguments): Query all open issues, present them, ask user to pick one. Fix that one issue and exit.
- **Exactly one token equal to `all`**: `all` mode — query all open issues, sort by ticket_id, then execute the fix loop (step 2-7) for each sequentially.
- **Exactly one token that is an issue ID**: single-issue mode — fix that one issue and exit.
- **Exactly one token that is a URL** (matches `^https?://`): URL mode — file the URL as an Issue first via the URL-resolution sub-step below, then fix the resulting Issue. Example: `/quo-fix-issue https://github.com/example/repo/issues/123`.
- **Two or more tokens** (list mode): treat as an explicit, user-provided list of tokens, each of which is either an issue ID or a URL (mixed lists are allowed — for example, `/quo-fix-issue b.cnb https://github.com/example/repo/issues/123 b.xet`). Execute the fix loop (step 2-7) for each issue **in the order given** (do NOT sort — the user's order is intentional; earlier issues may be prerequisites for later ones). Any URL tokens in the list are resolved by the URL-resolution sub-step below and substituted *in place* with the resulting Issue ticket ID before the fix loop runs. Do not query or fix issues outside the list. No user confirmation between issues.

Notes for list mode:
- `/quo-fix-issue b.cnb b.sgq b.xet`, `/quo-fix-issue b.cnb,b.sgq,b.xet`, and `/quo-fix-issue b.cnb, b.sgq  b.xet` all parse to the same three-ID list.
- Up-front validation: after URL resolution (per the URL-resolution sub-step below) but before starting any fixes, `bees show-ticket --ids <id1> <id2> ...` on the full post-resolution list. If any ID does not exist, is not in the `issues` hive, or is not in `open` status, report the problem IDs to the user and continue with the subset that is valid and open (do not abort the whole run). The failure check is cumulative across both gates — URL-resolution failures (per the URL-resolution sub-step's soft-fail handling) AND `bees show-ticket` validation failures both contribute to the dropped-token count. If *no* tokens remain valid after both gates, exit with an error.
- Between issues, no inter-issue cleanup ceremony is needed — the per-issue cold dispatches established in Section 4 already complete-and-exit when each Agent returns, and Section 7 closes out the per-issue TaskList tasks at issue close-out.

To query open issues (used only in no-args and `all` modes — list mode uses the user's explicit list instead):
```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues, status=open]
report: [title]'
```

#### Choose agent model preference

Before iterating through the issue list, ask the user which model to use for the support roles (Doc Writer, Product Manager, Doc Reviewer). Use `AskUserQuestion`:

- Question: "Which model should support agents (Doc Writer, Product Manager, Doc Reviewer) use?"
- Options:
  - **Opus (Recommended)** — highest quality, slower, more expensive
  - **Sonnet** — fast and cost-effective, good for straightforward tasks

The core implementation roles (Engineer, Test Writer, Code Reviewer, Test Reviewer) always use **Opus** — this is not configurable. Store the user's choice and apply it when spawning agents for every issue in the run (single-issue, list, or `all` mode). Ask once at the start, not per issue.

#### Validate isolation strategy

After parsing the argument list and resolving which issues to fix, but **before** validating any individual issue or dispatching any per-issue Agent, check whether you are running in an isolated context — fixes will produce one git commit per issue, so landing them on the wrong branch is hard to undo. Mirror `/quo-execute`'s isolation block:

**Scenario A — Already in a worktree.** You are in a git worktree whose directory name suggests issue-fix work (e.g., `fix-issues`, `bug-sweep`, or contains a fix-issue-related slug). Proceed directly — no action needed.

**Scenario B — On an existing branch in the main repo.** You are in the main repo checkout (not a worktree). Behavior depends on mode and current branch:

- If on `main` (or `master`) — **always** prompt with `AskUserQuestion`, regardless of mode. Landing many commits on main without confirmation is the surprise this prompt prevents.
- If on a feature branch in single-issue mode — proceed silently. The user is intentionally on a feature branch and a single commit there is the obvious choice.
- If on a feature branch in `all` mode or list mode — prompt with `AskUserQuestion`. Many commits on a single feature branch may not be what the user wants; they might prefer a fresh branch per fix-issue session.

When prompting, present these options:

1. **Create a feature branch (Recommended for `all` mode and list mode)** — Create a new branch (e.g., `fix/issues-<short-slug>` or `fix/<id1>-<id2>` for a small list) from the current HEAD and commit all fixes there. Keeps main clean; lets the user review/squash/discard later. Local branch only — no remote push.
2. **Work on current branch** — Commit directly to whichever branch is checked out (tell the user the branch name). Appropriate when the user is already on a feature branch and intentionally wants the commits there.
3. **Set up a worktree instead** — If `/bees-worktree-add` is installed, suggest running it to spawn the fix-issue session in an isolated worktree (fire-and-forget in a separate tmux session). If the skill is not installed, omit this option. Exit after giving this advice — do not proceed with work.

In the question, always state:
- The current working directory
- The current branch name
- That option 1 creates a local branch only (no remote push)
- The number of issues queued (so the user understands the commit volume implication)

#### Resolve URL tokens to Issue tickets via /quo-file-issue

If the working list contains any URL tokens (tokens matching `^https?://`, classified by shape per the bullet list at the top of Section 1), resolve each one to an Issue ticket ID before the upfront `bees show-ticket --ids` validation pass runs. The model-preference and isolation-strategy choices made in the two preceding sub-steps apply to the entire run — including the file-then-fix transition this sub-step initiates — so isolating before resolution lets the user opt into a fresh branch that scopes the file-from-URL commits.

**File-then-fix transition announcement.** Before the per-URL Skill-tool dispatch loop runs, announce the file-then-fix transition to the user with a short informational line — recommended string: `Filing URL(s) as Issue(s) first, then fixing.` This is informational console output, NOT an `AskUserQuestion` gate; it does not block the run and the user is not asked to confirm. The announcement fires only when at least one URL token is present in the post-tokenization working list — on the all-IDs path (no URL tokens), suppress the announcement entirely so the trace stays uncluttered for users who never invoked URL handling.

For each URL token in the working list (iterating in input order — see in-place semantics below), dispatch `/quo-file-issue` inline through the Skill tool. This consumes the published `## Inline invocation via the Skill tool` contract section in `skills/quo-file-issue/SKILL.md`; the dispatch shape mirrors `skills/quo-plan/SKILL.md`'s sub-step 4b, which dispatches `/quo-write-prd` and `/quo-write-sdd` via the Skill tool with a free-text `args` payload and captures structured return fields. Pass `args` as a free-text payload of the shape:

```
url: <url>
```

This skill currently sends only `url: <url>`; the contract also accepts an OPTIONAL `summary:` field that callers MAY pass to skip the `WebFetch` step in `/quo-file-issue`'s External-reference branch. `/quo-fix-issue` does not pre-fetch the URL on this dispatch path, so the `summary:` field is left unset and `/quo-file-issue` performs its own `WebFetch`.

Capture three fields from `/quo-file-issue`'s structured return message (per the consumed contract's `### Output shape (this skill → caller)` block):

- **`issue_ticket_id`** — the Issue ticket ID to substitute into the working list.
- **`issue_status`** — always `open` on a successful return; the close-out flip to `done` is owned by Section 7 of this skill, not by `/quo-file-issue`.
- **`action`** — exactly `created` for a freshly-filed Issue or `reused-existing` for a dedupe match. The value is informational on this sub-step (it is consumed by the post-resolution display surface) and is NOT load-bearing for the substitution itself; both values produce a valid `issue_ticket_id` to substitute.

**In-place substitution semantics.** A URL token at position N in the user-supplied input becomes the resolved `issue_ticket_id` at position N in the post-resolution working list. The substitution is in place — NEVER append the resolved ID at the tail of the list, NEVER reorder the surrounding tokens, NEVER deduplicate within the list. This preserves the "do NOT sort — the user's order is intentional; earlier issues may be prerequisites for later ones" invariant declared in the bullet list at the top of Section 1: an earlier URL that resolves to an issue which is a prerequisite of a later token must remain in its earlier position so the fix loop processes it first.

**Soft-fail on dispatch failure.** Treat any of the following as a dispatch failure for a single URL token, and apply the soft-fail handling per the existing list-mode "Up-front validation" pattern in the "Notes for list mode" block above (drop the failed token, report the failure to the user, continue with the remaining tokens):

- The Skill tool itself raises an error.
- The user cancels at one of `/quo-file-issue`'s user-facing `AskUserQuestion` gates (per the consumed contract's behavioral-guarantees block, the gates that fire on the inline path are: the in-conversation distill `Approve` / `Revise` / `Cancel` gate, the External-reference body-confirmation step, and the dedupe disambiguation gate's `Cancel` choice).
- `/quo-file-issue` returns a non-success structured return.

The cumulative failure check across this sub-step's URL-resolution failures AND the subsequent `bees show-ticket --ids` validation failures (per the "Notes for list mode" block above) is what determines whether the run errors out: only when no valid tokens remain after both gates does the run exit with an error. A single dropped URL never aborts the whole run when other tokens remain. On the **single-URL-token path** (URL mode, per the bullet list at the top of Section 1), a soft-fail on the only URL leaves the working list empty after this sub-step — the cumulative-failure rule is what fires here, and the run exits with an error per the same rule that applies in list mode.

**Post-resolution working-list display.** After every URL token in the working list has either been resolved (with `issue_ticket_id` and `action` captured per the structured return above) or soft-failed (and dropped per the soft-fail handling above), and BEFORE the upfront `bees show-ticket --ids` validation pass at the top of step 2, display the post-resolution working list to the user as informational markdown output. Each input position is labeled with the resolved ticket ID; URL positions are called out as filed-from-URL with the captured `action` value (`created` for a freshly-filed Issue, `reused-existing` for a dedupe match) so the user can see at a glance when dedupe matched an already-filed Issue. Recommended display shape:

```
Post-resolution working list:
1. b.cnb (input: b.cnb)
2. b.<new-id> (input: https://github.com/example/repo/issues/123, action: created)
3. b.xet (input: b.xet)
```

The display is informational ONLY — NO `AskUserQuestion`, NO ability to re-order. Its purpose is to let the user confirm prerequisite ordering survived the in-place substitution; if the user is unhappy with the result they can `Ctrl-C` and re-run with corrected positional order. The display fires only when at least one URL token was present in the user-supplied input — on the all-IDs path (no URL tokens), suppress the display entirely (the working list at that point is identical to the user's input and adds no signal).

**End of URL-resolution sub-step — continue Section 1 and then Step 2.** After every URL token in the working list has been resolved (or soft-failed) and the post-resolution working-list display has fired, the URL-resolution sub-step is complete. Continue Section 1 at the upfront `bees show-ticket --ids` validation pass (per the "Notes for list mode" block above), then proceed to Step 2 (Validate Issue), Step 3 (design analysis), Step 4 (per-issue Agent dispatch), Step 5 (review loop), Step 6 (doc verify), Step 7 (mark Issue done + commit), Step 8 (post-completion review), and Step 9 (upstream GitHub close commands) — the URL-resolution sub-step replaces nothing else in `/quo-fix-issue`'s flow. The structured return from each `/quo-file-issue` Skill-tool dispatch is a hand-off marker (per `skills/quo-file-issue/SKILL.md`'s `### Behavioral guarantees` "hand-off marker, not a workflow exit" guarantee), NOT a signal that the `/quo-fix-issue` run has terminated.

### 2. Validate Issue

```bash
bees show-ticket --ids "<issue-id>"
```

Check:
- Issue has a status which means it is ready to begin work (`open`)
- Check `up_dependencies` array for any blockers. They must be in a completed state.

`up_dependencies` is returned as a list of ticket IDs only — not statuses. Collect the IDs and batch-look-up their statuses:

```bash
# After reading the issue, batch-look-up its up_dependencies' statuses:
bees show-ticket --ids <dep-id-1> <dep-id-2> <...>
```

For each up_dependency, check the returned `ticket_status`. The issue is unblocked only if all its `up_dependencies` are in `done` status. An issue with no `up_dependencies` is unblocked by default.

If blocked:
- Output blocking IDs and titles
- In batch mode (`all` or list mode): skip this issue and continue to the next one
- In single mode: exit with message: "Cannot start Issue. It is blocked by: [list]"

If not blocked:
- Mark issue status to signal work has begun (if needed)

### 3. Design analysis

Between Section 2's validation gate and Section 4's per-issue implementer dispatch, the orchestrator dispatches a single **Analyst** Agent per Issue to perform codebase-grounded design analysis. The Issue body's framing is treated as **problem-report context, not as authoritative design** — the Analyst returns a Design Proposal grounded in its own codebase research, and the orchestrator surfaces that proposal to the user for approval before any Engineer dispatch happens.

This section is **always run** for every Issue. The orchestrator does NOT pre-judge whether the body is "well-researched enough" to skip the Analyst — classification of body quality is a fragile heuristic, and the cleanest fix is often an option the body did not propose at all (see `agents/analyst.md` "Why this role exists" for the design rationale).

#### Cold-dispatch the Analyst

Spawn one fresh Analyst Agent per Issue, scoped per-issue, using the same cold-dispatch shape Section 4 uses for the implementer roles:

```
Agent(
  subagent_type=analyst,
  run_in_background=true,
  prompt=<dispatch prompt with the issue body embedded verbatim and reference_materials JSON if non-empty>,
)
```

The dispatch prompt must include:

- The Issue ID.
- The Issue body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names) the Analyst's research will then key against. The same "quote the issue body verbatim" rule documented in Section 4 applies here.
- The Issue's `reference_materials` JSON value when non-empty. The Analyst owns the `WebFetch` step (per `agents/analyst.md`); the orchestrator does NOT pre-fetch the URL.
- Framing prose that names the Analyst's lane (per `agents/analyst.md`): codebase-grounded design proposal, returned as structured output, never directly modifying files. The framing MUST NOT loosen the role boundaries defined in `agents/analyst.md` — the same anti-softening rule that applies to Section 4's dispatch prompts applies here.

Track the dispatch via a TaskList task named per Section 4's issue-scoped naming convention (`analyst-<issue-id>`), with the usual `pending` → `in_progress` → `completed` lifecycle.

The Analyst runs in the background like every other dispatched Agent in this skill, but the orchestrator MUST wait for the Analyst's completion notification before proceeding to the next step (the user-side approval gate). The orchestrator does not dispatch the Section 4 implementer Agents until the Analyst has returned and the user has approved the proposal — Section 4 is gated on this section's approval.

#### Surface the proposal to the user

When the Analyst's completion notification fires, read the Analyst's return — the structured Design Proposal per the contract in `agents/analyst.md` `## Structured-output contract`. The proposal is **free-form analysis** (Problem / Root cause / Recommended approach / Why / Alternatives considered / Options the body did not consider / Upstream-fetch status / verdict trailer); surface it to the user as prose, NOT as an `AskUserQuestion` body — `AskUserQuestion` is for finite-multi-choice gates, not free-text design recommendations (per CLAUDE.md `## AskUserQuestion usage`).

**Extract the verdict and frame the preamble.** Before surfacing the proposal body, read the `Analyst verdict: <…>` trailer line from the Analyst's return and use it to shape the one- or two-sentence prose preamble that precedes the proposal. The verdict is a load-bearing framing signal — when the Analyst found divergence, the user should encounter the proposal already knowing that, not discover it by reading carefully. Preamble shapes per verdict (adjust phrasing to fit context; the structural rule is "divergent verdicts surface divergence prominently"):

- **`recommend-as-stated`** — "The Analyst's codebase research agrees with the Issue body's framing. The Recommended approach reflects the body's approach. Proposal follows:"
- **`recommend-with-refinements`** — "The Analyst's codebase research broadly agrees with the Issue body, but the Recommended approach refines the body's framing. The refinements are called out in Why / Alternatives considered. Proposal follows:"
- **`recommend-different-approach`** — "⚠️ The Analyst's codebase research **diverged** from the Issue body's framing. The Recommended approach is an option the body did NOT propose; the Why section explains the divergence explicitly. Read carefully before approving. Proposal follows:"
- **`escalate-to-user`** — "⚠️ The Analyst could **not converge** on a single recommendation and is escalating the open question(s) to you. The Why section frames the design ambiguity; the alternatives below are the choices that need your input. Proposal follows:"

The preamble is the orchestrator's responsibility, not the Analyst's. The Analyst returns the verdict; the orchestrator turns the verdict into the user-facing framing. This split keeps the framing language consistent across runs while letting the Analyst stay focused on the design substance.

After the preamble is rendered and the proposal body is surfaced, present the user with a finite-multi-choice gate via `AskUserQuestion`:

- Question: "How should I proceed with this design proposal?"
- Options:
  - **Approve & proceed to implementation (Recommended)** — Accept the Analyst's Recommended approach as the authoritative design directive for this Issue. The orchestrator carries the directive forward into Section 4's implementer dispatch (the Engineer dispatch prompt when source code needs modification, the Test Writer and Doc Writer dispatches otherwise per Section 4's conditional-dispatch rules).
  - **Revise** — The user has feedback on the proposal. Iterate in prose (free-text reply), then optionally re-dispatch the Analyst with the user's feedback as additional context.
  - **Cancel** — Exit cleanly without dispatching any implementer Agent for this Issue. No commit is made; the Issue stays `open`.

#### Branch on the user's choice

- **Approve** — Capture the Analyst's Design Proposal as the run's authoritative design directive for this Issue (specifically: the `### Recommended approach` section, plus the `### Why` / `### Alternatives considered` / `### Options the body did not consider` context the Engineer may want to consult). Mark the corresponding TaskList task `analyst-<issue-id>` `completed` and clear it from the active set (the Analyst's work is done and its result has been consumed into the design directive). Pass the directive forward to Section 4's Engineer dispatch prompt per "Authoritative design directive" below. Proceed to Section 4.

- **Revise** — Continue the conversation with the user in prose. The user typically supplies feedback in the form "I disagree with X because…" or "have you considered Y?" — engage with that feedback in the conversation thread. When the user's feedback warrants a fresh codebase pass (a substantively different approach is on the table, the user wants the Analyst to investigate a specific code path, etc.), **re-dispatch the Analyst** as a fresh cold invocation:

  - Before dispatching, mark the prior Analyst's TaskList task `completed` and clear it from the active set — `analyst-<issue-id>` on the first revision, or `analyst-<issue-id>-rev<n-1>` on subsequent revisions (the prior Analyst's work is done and its proposal has been consumed into the user's revision feedback).
  - Issue a new Agent dispatch with `subagent_type=analyst` and a new TaskList task name `analyst-<issue-id>-rev<n>` where `<n>` is the 1-based revision count (e.g., `analyst-<issue-id>-rev1` for the first revision, `analyst-<issue-id>-rev2` for the second).
  - The new dispatch prompt embeds the same Issue body verbatim and `reference_materials` as the first dispatch, PLUS a clearly-labeled `## Prior proposal and user feedback` section that quotes the prior Design Proposal in full and the user's revision feedback verbatim.
  - When the new Analyst returns, repeat the surface-and-gate flow above.
  - There is no fixed cap on revision count; the user terminates the loop by picking Approve or Cancel.

  When the user's feedback is light enough to incorporate without a fresh codebase pass (a wording tweak, a clarification on terminology, a "yes please proceed with refinement X you mentioned in Alternatives"), the orchestrator may carry the user's clarification directly into the Approve branch without re-dispatching — capture both the original Recommended approach and the user's clarification in the design directive that flows to Section 4.

- **Cancel** — Mark the `analyst-<issue-id>` TaskList task `completed` (the Analyst's work is done, even if its proposal was not accepted), clear any in-flight TaskList entries scoped to this Issue, and exit this Issue cleanly. **NO commit is made; the Issue stays `open`.** In single-issue mode the run ends here; in list / `all` mode proceed to the next Issue in the batch (back to Section 2 for that next Issue).

#### Authoritative design directive (carried into Section 4)

Once the user picks Approve, the design directive that flows into Section 4's Engineer dispatch prompt is composed of:

- The Analyst's `### Recommended approach` section verbatim.
- The Analyst's `### Why`, `### Alternatives considered`, and `### Options the body did not consider` sections (context the Engineer may need to understand the trade-offs and the independent alternatives the Analyst surfaced and rejected — without re-deriving them).
- Any user-supplied refinement captured on the Approve branch from a "light enough to incorporate without a fresh Analyst pass" revision.

The Engineer dispatch prompt in Section 4 embeds this directive as the **authoritative design source** for the fix. The Issue body itself still flows into Section 4's prompt verbatim (per the long-standing "quote the issue body verbatim" rule — identifier spellings, contract surfaces, etc. must travel byte-for-byte), but the design source the Engineer follows is the directive; where the body's framing and the directive conflict, the directive wins. Section 4's dispatch-prompt prose documents the integration shape.

#### Anti-pattern: do not classify the body upfront

The orchestrator MUST NOT short-circuit Section 3 based on a heuristic judgement that the Issue body is "well-researched enough." Classification of body quality is fragile by construction (a body can cite code paths and still be a one-line typo fix; a one-sentence body can sit behind a `reference_materials` URL whose upstream content carries rich behavioral spec; the Analyst's own research is the only reliable signal). Always dispatch the Analyst; the Analyst's verdict (`recommend-as-stated` / `recommend-with-refinements` / `recommend-different-approach` / `escalate-to-user`) IS the classification, made on the basis of codebase research rather than a content-blind pre-read gate. When the body IS well-researched, the Analyst's pass converges cheaply (prompt-caching helps), and the user's Approve gate fires equally cheaply — the overhead is bounded.

### 4. Execute fix via per-issue Agent dispatch

The orchestrator (you, the Director) drives each Issue's fix through a **reconciliation loop** that dispatches **fresh, ephemeral background `Agent` invocations** against the custom subagent types defined in this skill set's sibling `agents/` directory. There is no long-lived team; there are no warmed Agents; there is no peer-to-peer messaging between workers. Unlike `/quo-execute`, an Issue has no Subtask breakdown — there is one implementation pass per Issue, so the dispatch scope here is **per-issue**, not per-Subtask. Section 3's Design analysis gate has already produced the authoritative design directive for the fix; this section's Engineer dispatch carries that directive into the implementation pass.

#### Reconciliation loop

The loop is **event-driven, not clock-driven**. Each tick has three phases:

1. **Read state.** Pull the current truth from three sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <issue-id>` to get the Issue body and current `ticket_status`. Use the canonical querying recipe (see `docs/doc-writing-guide.md` `## Querying tickets`) for any focused state query, e.g.:

     ```bash
     bees execute-freeform-query --query-yaml 'stages:
       - [id=<issue-id>]
     report: [title, ticket_status]'
     ```
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done).
   - **git state** — the actual diff on disk. Workers communicate by editing files; the diff is the only authoritative record of what they actually did.

   The Issue ticket type only supports two statuses — `open` and `done` — so there is no in-flight bees status to set while work is underway. The TaskList progress UI carries the in-flight signal (per-Agent `pending` / `in_progress` / `completed`), and the orchestrator flips the Issue from `open` to `done` only at issue close-out (per Section 7).

2. **Reconcile.** Compare current state to target state and act:
   - For every implementer role whose gating precondition is met for this Issue and which has no Agent already in flight for it, dispatch a fresh Agent (see "Per-issue cold dispatch" below).
   - For every Agent that has reported completion, persist the result: confirm any bees ticket transitions the Agent committed to, mark the corresponding TaskList task `completed`, and unlock any newly-eligible downstream role.
   - When all implementer Agents (Engineer if dispatched, Test Writer if dispatched, Doc Writer always) have returned for this Issue, advance to Section 5 (the review loop). The per-issue PM Agent is dispatched in Section 5 alongside the reviewer Agents on every Issue (see Section 5's reviewer dispatch block); the orchestrator does not pre-judge whether a PM pass is needed.

3. **Yield.** The orchestrator does not poll. After dispatching the work this tick uncovered, return control to the harness and wait for the **Agent completion notification** delivered by the `run_in_background=true` substrate. The notification is what triggers the next tick.

##### Anti-pattern: no clock primitives

The reconciliation loop is driven exclusively by Agent completion notifications. Do **not** use any of:

- **`/loop`** — repeats the orchestrator's last turn on a wall-clock cadence.
- **`ScheduleWakeup`** — fires the orchestrator after a delay.
- **`CronCreate`** — fires the orchestrator on a recurring schedule.
- **Polling** — re-reading bees / TaskList / git on a sleep-wait cycle without a triggering event.

If the work for this tick is dispatched and there is nothing else to reconcile, the correct action is to yield. Background Agents will wake the orchestrator when they finish; that is the only legitimate trigger for the next tick.

#### Per-issue cold dispatch

For each Issue, the orchestrator spawns one fresh Agent per role at issue scope:

```
Agent(
  subagent_type=<role>,            # one of: engineer, test-writer, doc-writer
  run_in_background=true,
  prompt=<dispatch prompt with the issue body embedded verbatim and Section 3's design directive embedded as the authoritative design source>,
)
```

Each role gets its own Agent invocation. The orchestrator does **not** name Agents (`Agent(name=...)` is not used) and does **not** reuse an Agent across roles. There is no `SendMessage` between roles — the worker reads its assignment from the dispatch prompt, edits files, and exits. The diff is the handoff to the next role.

Which roles to dispatch for a given Issue:

- **Engineer** — dispatched when source code needs modification.
- **Test Writer** — dispatched when tests need modification.
- **Doc Writer** — always dispatched. The Doc Writer decides whether docs actually need updating after reading the diff; the orchestrator does not pre-judge.

The Product Manager is no longer an implementer-phase role — it is dispatched in Section 5 alongside the reviewers on every Issue (see Section 5's reviewer dispatch block).

Reviewer Agents (Code Reviewer, Test Reviewer, Doc Reviewer) and the Product Manager Agent are introduced in Section 5 — they are dispatched after the implementer Agents return.

##### Per-issue cold dispatch (vs SDD's warm-Agent intent)

The original SDD intent was warm Agents that would receive `SendMessage` pings between roles, amortizing context-load cost across an Issue. That path requires the experimental teams substrate per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents) — and this Bee removes that substrate entirely, so `SendMessage`-based warm dispatch is no longer available. The trade-off is conscious: each cold-dispatched Agent re-loads its role file and any referenced docs, which is more tokens than a warm ping, but the architectural simplification (no long-lived team to manage, no shutdown choreography, no peer-to-peer coupling) is worth it; in practice prompt caching mitigates most of the cold-load cost. The divergence from the SDD's warm-Agent intent is intentional and is captured by Issue **`b.x9w`**; revisit if the constraint changes.

##### Dispatch prompt: quote the issue body verbatim and embed the design directive

The dispatch prompt sent to each Agent must embed the Issue body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names) that the worker will then use literally. Read the Issue via:

```bash
bees show-ticket --ids <issue-id>
```

Embed the returned body block in the dispatch prompt as a quoted block. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "your gating precondition is met — start now") is fine; the body itself stays untouched. The orchestrator's own progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

**Engineer dispatch — embed the Section 3 design directive as the authoritative design source.** When the dispatched role is `engineer`, the dispatch prompt MUST additionally embed the design directive captured at the end of Section 3's Approve branch (the Analyst's `### Recommended approach` section, plus `### Why`, `### Alternatives considered`, and `### Options the body did not consider` for context, plus any user-supplied refinement captured on the Approve branch). Label that block clearly in the prompt — recommended labels are `## Authoritative design directive (from Section 3 Analyst pass)` for the Recommended approach itself and `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)` for the surrounding context — so the Engineer can distinguish the directive from the verbatim Issue body. Where the Issue body's framing and the design directive conflict, **the directive wins**: the body still flows in verbatim because identifier spellings, contract surfaces, and other byte-accurate references travel with it, but the design source the Engineer implements is the directive. The Engineer's role file (`agents/engineer.md`) carries the same invariant in its **Authoritative design directive (fix mode only)** bullet, so the directive-wins rule is reloaded on every cold dispatch even if the dispatch-prompt framing is terse. The Test Writer and Doc Writer dispatch prompts do NOT carry the design directive separately — they read the resulting diff (the Engineer's implementation of the directive) as their work signal, per the hub-and-spoke flow.

The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the dispatched role's contract file (`agents/<role>.md`). The rule applies to **every** dispatched role type — both the implementer roles (Engineer / Test Writer / Doc Writer) and the review-only roles (PM, Code Reviewer, Test Reviewer, Doc Reviewer). Concrete examples of forbidden softening (illustrative, not exhaustive):

- MUST NOT tell the Engineer it may also write tests or docs.
- MUST NOT tell the Test Writer it may also modify source code.
- MUST NOT tell the Doc Writer it may also modify source or test files.
- MUST NOT tell the PM or any reviewer (Code Reviewer / Test Reviewer / Doc Reviewer) it may write source, tests, or docs — these are review-only roles, and the contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (each reviewer) explicitly.
- MUST NOT tell one reviewer it may also review another reviewer's lane (e.g., Code Reviewer reviewing tests, or Test Reviewer reviewing documentation).

The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also add this one test file" / "you may also touch this one source line"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer dispatch, a redirect of the Issue, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other; the only handoff is from worker to orchestrator (the diff in execution mode, the JSON return in research mode), never worker-to-worker. So a softening clause cannot be made safe by adding "coordinate with the other role's diff" or similar coordination prose — that channel does not exist.

When the Issue's `reference_materials` is non-empty (the external-reference mode produced by any of `/quo-file-issue`'s URL entry surfaces — bare URL `/quo-file-issue <url>`, the flag forms `/quo-file-issue --reference <url>` / `--from-github <url>`, or this skill's URL-resolution sub-step's inline-Skill-tool dispatch — all of which produce the same `reference_materials` shape), embed the `reference_materials` JSON value alongside the (thin) body in the dispatch prompt so the worker can read the resolver name and URL. Workers (the Analyst in Section 3; the Engineer in Section 4; the PM in Section 5) handle the upstream content fetch via `WebFetch` per their role contracts in `agents/analyst.md`, `agents/engineer.md`, and `agents/pm.md`; the orchestrator does not pre-fetch the URL.

#### Hub-and-spoke via substrate

Workers do not message each other. The orchestrator is the hub; each dispatched Agent is a spoke that reads its prompt, edits files, and exits. The diff is the handoff between roles — when the Engineer finishes, the next role (Test Writer, Doc Writer, or PM) reads the resulting diff to do its work. Hub-and-spoke is a **structural property** of ephemeral background Agents, not a rule the orchestrator must remember to enforce: there is no inter-Agent channel for workers to even attempt peer-to-peer coupling on.

#### Recursive delegation: not supported

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every Agent invocation originates from this skill's reconciliation loop, never from a worker.

#### Roles dispatched by the orchestrator

The orchestrator dispatches the following three implementer roles per Issue. The full role contracts (responsibilities, gating preconditions, instructions, shell-command etiquette) live in the role files; the orchestrator's job is to invoke the right role at the right time, not to carry the role's prose.

- **Engineer** (`agents/engineer.md`) — implements source-code changes for the fix. Model: Opus (always). Does not write tests or docs.
- **Test Writer** (`agents/test-writer.md`) — writes / updates / deletes tests to verify the fix and reviews the Engineer's diff for missing coverage. At minimum, ensures there is at least one test that fails before the Engineer's fix and passes after — this is the regression guard that prevents the same bug from recurring. Model: Opus (always).
- **Doc Writer** (`agents/doc-writer.md`) — reviews the Engineer's diff for documentation gaps and updates customer-facing and internal docs as needed, and additionally appends or updates the relevant `### Feature: <title>` subsection in the project's cumulative PRD and SDD (per the lookup-key paths in CLAUDE.md `## Documentation Locations`) when the fix lands user-visible behavior or architectural shifts that warrant a cumulative-doc entry — see `agents/doc-writer.md` for the categorization heuristic, idempotency rule, and `<title>` resolution recipe. In fix mode the Doc Writer is dispatched once per Issue (not per Subtask as in execute mode), and the Plan Bee — when one exists — is discovered via the Issue's `up_dependencies` rather than a parent-chain traversal; `agents/doc-writer.md` is the authoritative spec for that traversal. When the Issue body contains a `## Doc divergence noted` section (authored by `/quo-file-issue` when the filer flagged that an existing doc is wrong about the buggy behavior), the Doc Writer treats that section as an explicit doc-correction directive: the named file/section is wrong about today's behavior, and the documented correction is applied as part of this fix's doc updates. Model: user's choice (Opus or Sonnet, selected at the start of the run).

Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) and the Product Manager role (`agents/pm.md`) are introduced in Section 5 — the PM is always dispatched alongside the reviewers on every Issue, mirroring the always-dispatched pattern Doc Writer already uses in the implementer phase.

#### TaskList as progress UI

The orchestrator uses Claude Code's native **TaskList** as the visible progress UI for the run. There is no separate display backend to configure — TaskList renders in the harness automatically, replacing the team-display surface a prior message-bus substrate would have required.

For every Agent the orchestrator dispatches, it creates exactly **one** TaskList task:

- **`pending`** — created when the orchestrator decides this role is next for the current Issue but before the Agent invocation lands.
- **`in_progress`** — set the moment the Agent invocation is dispatched (`Agent(...)` returns).
- **`completed`** — set when the orchestrator processes the Agent's completion notification and confirms the worker's reported deliverables landed (file edits visible in `git status` / `git diff`, any bees ticket transitions the worker committed to are reflected on disk).

Use `metadata.activity` on the TaskList task to surface finer-grained progress when a worker emits intermediate signal (e.g., `"running narrow tests on package X"`, `"resolving Scoped-marker via up_dependencies iteration"`). The orchestrator updates this string opportunistically; it is informational, not a routing input.

##### TaskList naming convention

The naming convention is the **canonical cross-reference** for downstream Sections of this SKILL.md (Section 5's reviewer dispatches and Section 7's TaskList completion at issue close-out consume these names). It is deterministic so two concurrent invocations cannot collide and unambiguous so any reader can map a TaskList entry back to its Issue.

Naming is **issue-scoped** for every per-issue role — there is no Subtask breakdown under an Issue, so the parent ticket id used as the scope suffix is always the Issue id. The URL-resolution Skill-tool dispatches in Section 1's URL-resolution sub-step run *before* per-issue dispatch begins (the URL has not yet been resolved to an Issue ID at that point), so they use a positional-index discriminator instead:

- **Analyst Agents** (dispatched per Issue in Section 3 before the implementer phase) — Name: `analyst-<issue-id>` (e.g., `analyst-veq` for Issue `b.veq`). When the user picks `Revise` and the orchestrator re-dispatches the Analyst with the user's feedback as additional context, append a `-rev<n>` discriminator where `<n>` is the 1-based revision count (e.g., `analyst-veq-rev1` for the first revision, `analyst-veq-rev2` for the second) — per Section 3's Revise-branch instructions.
- **Implementer Agents** (Engineer, Test Writer, Doc Writer) — Name: `<role>-<issue-id>` (e.g., `engineer-veq`, `test-writer-veq`, `doc-writer-veq` for Issue `b.veq`).
- **Reviewer Agents** (Code Reviewer, Test Reviewer, Doc Reviewer — see Section 5) — Name: `<reviewer>-<issue-id>` (e.g., `code-reviewer-veq`, `test-reviewer-veq`, `doc-reviewer-veq`).
- **PM Agents** (dispatched per Issue in Section 5 alongside the reviewers) — Name: `pm-<issue-id>` (e.g., `pm-veq`).
- **URL-resolution Skill-tool dispatches** (per Section 1's URL-resolution sub-step) — Name: `file-from-url-<n>`, where `<n>` is the 1-based index of the URL token in the user-supplied positional-argument list (e.g., `file-from-url-1`, `file-from-url-2` for two URL tokens). The 1-based positional index is what makes the entry deterministic and unambiguous — not the URL itself, which may be long, may repeat after dedupe, or may contain reserved characters that would collide with the naming convention. Each entry is created `pending` when the orchestrator decides to dispatch `/quo-file-issue` for the corresponding URL token, set `in_progress` the moment the Skill-tool dispatch lands, and set `completed` when the resolved `issue_ticket_id` is captured from the structured return (whether the underlying `action` is `created` for a freshly-filed Issue or `reused-existing` on the dedupe `Use existing` path). The URL-resolution sub-step's soft-fail / user-cancel path also closes out the entry — mark the failed entry `completed` (with the failure reason recorded via `metadata.activity` per the per-Agent activity convention above if useful) and clear it from the active set so the cumulative failure check at the upfront `bees show-ticket --ids` validation pass operates on a clean active set.

#### Scoped-marker PM dispatch wiring

When the orchestrator dispatches the per-issue PM Agent in Section 5 (always dispatched, alongside the reviewers), the dispatch prompt must include the **resolved path** to the Scoped-marker helper as a `<scoped-marker-resolver-path>` substitution. The helper is a sibling-skill bundled script; resolve its path at runtime from this skill's own base directory:

```
<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py
```

The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-fix-issue`). Use the `..` traversal pattern to reach the sibling skill — this matches the same sibling-resolution discipline already used elsewhere in the skill set.

```bash
# POSIX (bash / zsh): the path the orchestrator embeds in the PM dispatch prompt
<this skill's base directory>/../quo-breakdown-epic/scripts/scoped_marker_resolver.py
```

```powershell
# Windows (PowerShell): the path the orchestrator embeds in the PM dispatch prompt
<this skill's base directory>\..\quo-breakdown-epic\scripts\scoped_marker_resolver.py
```

The dispatch prompt's context selects **Path B** of `agents/pm.md`'s Scoped-marker logic. The signal is structural: the prompt names an **Issue ID** and the Issue's **`up_dependencies`** array, and there is **no Grandparent Bee** in the context (Issues have no parent Bee — Path A's grandparent walk is unavailable here). `agents/pm.md` reads that shape and switches to its Path B branch, which iterates `up_dependencies` opportunistically looking for a Plan Bee whose body carries a Scoped marker, with a best-effort fallback to the unscoped spec when no marker is found. Path A (Grandparent Bee, hard-fail when absent) is the `quo-execute` path and does not apply here.

The orchestrator's responsibility ends at passing the resolved path placeholder, the Issue ID, the Issue body verbatim, and the Issue's `up_dependencies` to the PM. The orchestrator does **not** inline the Scoped-marker grammar, the temp-file recipe for staging the spec body, or the helper invocation itself — `agents/pm.md` owns those, and owns the Path A vs Path B selection logic. That separation lets `agents/pm.md` evolve the marker contract and the path-selection rules without dragging this SKILL.md along.

### 5. Review Loop

Once the implementer Agents return, dispatch four concurrent ephemeral Agents per Section 4's dispatch shape — three reviewer roles plus the Product Manager: `Agent(subagent_type="code-reviewer", run_in_background=true)`, `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`, `Agent(subagent_type="pm", run_in_background=true)`. Track each via a TaskList task per Section 4's issue-scoped naming convention: `code-reviewer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`.

Conditional spawn — only dispatch a reviewer whose corresponding implementer was used during this issue's implementation pass:
- If the Engineer Agent ran during this issue's implementation pass, dispatch the code-reviewer Agent now.
- If the Test Writer Agent ran during this issue's implementation pass, dispatch the test-reviewer Agent now.
- If the Doc Writer Agent ran during this issue's implementation pass, dispatch the doc-reviewer Agent now.

Corollary: a doc-only fix dispatches only the doc-reviewer; a code+test fix without a Doc Writer pass dispatches only code-reviewer + test-reviewer.

**PM is the exception to the conditional-spawn rules.** The Product Manager Agent is **always dispatched** per Issue regardless of which implementers ran — spec-alignment review is meaningful on any diff. The PM dispatches alongside the reviewers, not instead of any of them. This matches the always-dispatched pattern Doc Writer uses in Section 4 — the orchestrator does not pre-judge whether spec-drift risk is present; the PM Agent reads the spec sources, makes the substance-based judgement itself, and short-circuits in `agents/pm.md` when there is no spec drift surface to review.

The PM's dispatch prompt must include the Issue ID, the Issue body verbatim, the Issue's `up_dependencies` array, and `<scoped-marker-resolver-path>` — a placeholder the orchestrator fills in at runtime so `agents/pm.md` can perform its Scoped-marker check (see "Scoped-marker PM dispatch wiring" in Section 4).

The reconciliation-loop tick defined in Section 4 covers Agent completion notification — there is no idle teammate to escalate to. The orchestrator yields after dispatching the reviewer Agents and the PM Agent, and the harness fires the next tick on the `run_in_background=true` substrate's completion notification.

Role contracts (responsibilities, model assignment, gating, instructions) live in the role files; the orchestrator's job is to dispatch, not to carry the role's prose.

- **Code Reviewer** (`agents/code-reviewer.md`) — reviews the Engineer's output and surfaces gaps against engineering standards.
- **Test Reviewer** (`agents/test-reviewer.md`) — reviews the Test Writer's output and surfaces gaps against test-quality standards.
- **Doc Reviewer** (`agents/doc-reviewer.md`) — reviews the Doc Writer's output and surfaces gaps against documentation standards.
- **Product Manager** (`agents/pm.md`) — reviews the fix against the spec source (the Issue body, plus PRD/SDD-equivalent paths from CLAUDE.md `## Documentation Locations`, optionally Scoped-marker-narrowed via a Plan Bee in `up_dependencies`), flags scope creep or spec divergence. Issues filed by `/quo-file-issue` in the default in-conversation capture mode do not carry `reference_materials` — the body itself is the spec. Issues filed via any of `/quo-file-issue`'s URL entry surfaces — bare URL (`/quo-file-issue <url>`), the flag forms (`/quo-file-issue --reference <url>` / `--from-github <url>`), or this skill's URL-resolution sub-step's inline-Skill-tool dispatch — carry a `reference_materials` entry whose `value` is an external URL and whose `resolver` is one of `github-issue`, `linear-issue`, or `url`; on this path the PM fetches the upstream content via `WebFetch` and treats it as the spec source (the Issue body is intentionally thin in this mode). When the PM transitively consults a Plan Bee reached through the Issue's `up_dependencies`, that Plan Bee's `reference_materials` may resolve via the `file-path` resolver (path on disk — Scoped-marker narrowing applies) or the `bees` resolver (Spec Bee ID, in which case the PM walks the Spec Bee's `t1=Doc` children for PRD and SDD content). `agents/pm.md` is the authoritative spec for all three resolver-driven paths (`file-path`, `bees`, and the external-URL resolvers like `github-issue` / `linear-issue` / `url`); the body-as-spec path is the fallback when `reference_materials` is null/empty. The PM self-short-circuits in `agents/pm.md` when the collective spec sources carry no substantive content — see that role file for the content-based short-circuit rule. Model: user's choice (Opus or Sonnet, selected at the start of the run).

- Get the feedback, and make a judgement call about whether that work must be done. Each of the three review skills above (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a `**Next action for the orchestrator:**` trailer line at the bottom of its output that names the precise routing this step must take after consuming the findings. **Follow the trailer literally** — it is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory.
  - If feedback requires action, dispatch fresh ephemeral implementer Agents per Section 4's dispatch shape (Engineer / Test Writer / Doc Writer as needed) and/or re-dispatch the PM Agent per this section's dispatch shape if spec-alignment review needs another pass against the updated diff.
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** re-dispatch the Product Manager on this iteration
  - If not, move on but you MUST include the ignored feedback in the summary
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in the summary

### 6. Verify docs are still accurate

The per-issue PM Agent dispatched in Section 5 has already produced a spec-alignment verdict — either a deep review against the substantive spec source (when the PM found substantive content across the collective sources it consulted) or a one-line short-circuit verdict (`no spec drift surface to review for this Issue`, when no source carried substantive content). Either outcome lands in the per-issue summary. Section 6 is **informational confirmation** on every Issue — never load-bearing orchestrator-direct work: confirm the PM's verdict has been captured in the per-issue summary and proceed to Section 7.

If the Issue body carried a `## Doc divergence noted` section, the doc updates implied by that section have already been applied by the Section 4 Doc Writer pass — Section 6's job here is to **confirm** that consumption landed (the named file/section now matches today's behavior post-fix), not to re-discover the divergence from scratch.

Report what was confirmed (informational only — Section 6 never performs orchestrator-direct doc updates; any doc changes are the Doc Writer's lane per `agents/doc-writer.md` and were already applied in Section 4 when this Issue carried a `## Doc divergence noted` section):

- The PM's spec-alignment verdict from the Section 5 dispatch — either the deep-review outcome against the substantive spec source, or the `no spec drift surface to review for this Issue` short-circuit verdict from `agents/pm.md` — and confirmation that it has been captured in the per-issue summary.
- When the Issue body carried a `## Doc divergence noted` section, confirmation that the Section 4 Doc Writer pass consumed it — i.e. the named file/section now matches today's behavior post-fix. When the Issue body had no such section, this bullet is N/A.

### 7. After Issue is fixed

Once the issue is fixed:

1. Mark the issue's bees ticket `status=done` before committing, so any out-of-band ticket-state propagation is consistent. **Re-read the Issue's current status first** (`bees show-ticket --ids <issue-id>`) and skip the `bees update-ticket --status done` call if the status is already `done` — workers occasionally overstep their role contract and flip the status themselves, so the orchestrator's close-out flip should be idempotent against that case rather than failing or double-flipping. The bees CLI writes the new status to the issue's on-disk record (under the resolved Issues hive path) — when that path is inside this repo, the resulting working-tree change is staged as part of the per-issue commit at step 2.3 below alongside the fix's code/test/doc changes, so the ticket's git state stays in sync with its bees state.
2. Create one git commit for the Issue (including any doc updates). **NEVER push to remote — committing only.** Use this staging procedure:
   1. Run the **Format** command from CLAUDE.md `## Build Commands` (e.g. `cargo fmt`, `prettier --write`, `gofmt -w`) to normalize formatting (agents may have triggered reformatting in files they didn't report).
   2. Run `git status` to see the full set of modified and untracked files.
   3. Stage files related to this issue's actual code, test, and doc changes — agent-reported files plus formatting changes to files that were touched by this issue's agents — plus (only if the Issues hive lives inside this repo) the per-issue directory under the resolved Issues hive path, so the issue's `open → done` status flip and any body updates the orchestrator made via `bees update-ticket` land in the same per-issue commit as the fix itself. The Issues-hive scoping mirrors `quo-execute`'s Plans-hive scoping (see `quo-execute`'s After-Task commit step); use the same hive-path resolution as `/quo-plan` and `/quo-file-issue`:

      ```bash
      # POSIX (bash / zsh):
      issues_path=$(bees list-hives | python3 -c 'import json,sys; data=json.load(sys.stdin); p=next((h["path"] for h in data["hives"] if h["normalized_name"]=="issues"), None); print(p or "")')
      repo_root=$(git rev-parse --show-toplevel)
      case "$issues_path" in
        "$repo_root"|"$repo_root"/*) git add "$issues_path/<issue-id>" ;;
      esac
      ```

      ```powershell
      # Windows (PowerShell):
      $issuesPath = (bees list-hives | ConvertFrom-Json).hives | Where-Object { $_.normalized_name -eq 'issues' } | Select-Object -ExpandProperty path
      $repoRoot = git rev-parse --show-toplevel
      $issuesNorm = if ($issuesPath) { $issuesPath.Replace('\','/') } else { '' }
      $repoNorm = $repoRoot.Replace('\','/')
      if ($issuesNorm -and ($issuesNorm -eq $repoNorm -or $issuesNorm.StartsWith("$repoNorm/"))) {
        git add "$issuesPath/<issue-id>"
      }
      ```

      **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this issue. The per-issue scoping `<issue-id>` on the `git add` path also keeps drift in *other* issues' on-disk records out of this commit; if other issues have stale working-tree state, that gets caught by the next `/quo-fix-issue` run on those issues, not swept in here.
   4. Commit with a descriptive message per system/project git guidance. The commit's subject line MUST follow the literal format `Fix issue: <title> (<issue-id>)` (e.g., `Fix issue: Tighten dispatch contract gap (b.abc)`) — Section 9's post-hoc SHA-derivation fallback `--grep`-filters the session log against the literal `(<issue-id>)` token in this subject, so the parenthesized-ID suffix is a load-bearing contract, not a stylistic preference.
3. Mark the per-issue TaskList tasks (named per Section 4's issue-scoped naming convention — `engineer-<issue-id>`, `test-writer-<issue-id>`, `doc-writer-<issue-id>`, plus the Section 3 Analyst task `analyst-<issue-id>` if not already marked `completed` at the end of Section 3, plus the Section 5 tasks: `code-reviewer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`) as `completed` and clear them from the active set. There is no Agent shutdown to perform — the per-issue cold dispatches established in Sections 3, 4, and 5 already complete-and-exit when each Agent returns.
4. Output the summary:

```markdown
## Issue [x] of [total] done: [issue-title]

**Issue**: <issue-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed (use the actual path from CLAUDE.md "Documentation Locations", not literal "SDD"/"PRD")]
**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]
```

5. In batch mode (`all` or list mode): proceed to the next issue in the batch (go back to step 2). In single mode: continue to step 8.

### 8. Post-Completion Review

After all issues are fixed (in batch mode: after the final issue in the batch; in single mode: after the one issue), run a final fresh-context generalist sweep across all changes made during this quo-fix-issue session.

**Anti-pattern callout — read before acting.** Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/quo-engineer-review` is scoped to source code, `/quo-doc-writer-review` to user-facing docs, `/quo-test-writer-review` to test files — none of them runs the cross-lane sweep this step needs). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, and reviewer verdicts from the whole run; that context biases it toward "did the four phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the issue body and nothing else — that's the point.

1. Compute the pre-session diff scope. Capture `<pre-session-sha>` as the HEAD that existed when quo-fix-issue began (use the SHA recorded at the start of the run, or `HEAD~N` where `N` is the number of issues actually fixed in this session — one commit per issue per Section 7 step 2.4). Collect the issue ID list as `<issue-id-1> <issue-id-2> ...` (one ID in single-issue mode; the full session list in batch mode).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. The agent will not see anything else from this session, so the prompt must be self-contained. Starting skeleton (substitute `<pre-session-sha>` and the issue ID list before sending):

   ```
   You are an independent reviewer for a quorum fix that was just shipped.

   Scope: review the diff `git diff <pre-session-sha>..HEAD` (compute it
   yourself via git) against the issue body, or bodies in batch mode — read
   each via `bees show-ticket --ids <id>`. Issue IDs in this session:
   <issue-id-1> <issue-id-2> ...
   The orchestrating team-lead has finished the work — your job is to give it a
   fresh-eyes review with no context of how the work was done.

   Flag anything that looks wrong: code defects, prose problems, spec drift
   between the change and the issue, contract-key violations (do NOT allow
   renames of keys in CLAUDE.md `## Documentation Locations` or `## Build
   Commands`), cross-file inconsistencies, missing edits the issue called for.
   One generalist pass covers code AND docs AND tests — do not lane-scope.

   Note: in skill repos (where the diff includes `skills/<name>/SKILL.md` or
   `agents/<name>.md` files), those markdown files are skill / subagent program
   source code, not natural-language documentation. Review them with the same
   rigor as language-specific source — broken cross-references, drifted
   contracts, ambiguous prose, and CLAUDE.md design-rule violations are all
   in scope.

   Do NOT do a general repo audit. Stay focused on the diff.

   Do NOT invoke /quo-engineer-review, /quo-doc-writer-review, or /quo-test-writer-review at
   this stage. Those skills are designed as parallel lanes of an in-flight
   review; they each have lane-specific scope rules that make them wrong for a
   final generalist sweep.

   Return findings as a numbered list. For each item: `file:line`, what's
   wrong, severity (`blocker` / `suggestion` / `nit`). If clean, return
   exactly "no issues found".
   ```

   Wait for the agent's report.

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-issue code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

   **Orchestrator self-tracking close-out (mandatory before yielding).** Independent of the per-issue TaskList tasks already closed in Section 7 step 3 and the per-finding follow-up tasks closed in step 6 below, the orchestrator typically creates additional ad-hoc TaskList tasks during this Section 8 pass to break the post-completion review into discrete steps (e.g., "Get diff scope", per-issue "Verify <id>" entries, "Synthesize findings"). Before presenting the synthesized findings to the user — i.e., before yielding the turn at step 4 / step 5 below, whether to deliver "no issues found" or to ask the user how to handle flagged issues via `AskUserQuestion` — mark every such orchestrator self-tracking TaskList task `completed` and clear them from the active set. The yield is the close-out trigger: when the orchestrator stops responding (either at end-of-flow or to wait on the user's reply), the TaskList must show no `in_progress` entries left over from these synthesis steps. This discipline is the orchestrator-self-tracking analog of step 6's per-finding follow-up close-out (which scopes to dispatched `<role>-postcomp-<n>` Agents and `file-issue-postcomp-<n>` per-finding tracking entries — the latter created by the "File as issue tickets" branch, which invokes `/quo-file-issue` per finding rather than dispatching an Agent); the two scopes are complementary, not overlapping.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and exit.

5. If the agent flagged any issues, use `AskUserQuestion`:
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now
     - **File as issue tickets** — create issue tickets via `/quo-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
   - **Fix in this session**: Dispatch fresh ephemeral Agents per Section 4's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. Stay in delegate mode. Section 4's TaskList naming convention is issue-scoped (`<role>-<issue-id>`) and does not cover post-completion follow-up Agents that span the whole session, so for these dispatches use the **post-completion-scoped** name `<role>-postcomp-<n>`, where `<n>` is the 1-based index of the finding being addressed in the fresh reviewer's numbered list (e.g., `engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`). The per-finding discriminator is load-bearing: Section 4's "exactly one TaskList task per Agent" rule still applies here, so two findings that each need an Engineer follow-up must dispatch to distinct task names (`engineer-postcomp-1` and `engineer-postcomp-3`, say) rather than colliding on a shared `engineer-postcomp`. When each follow-up Agent returns, persist the result the same way Section 4's reconcile-on-completion step does: confirm any bees ticket transitions the worker committed to, then mark the corresponding `<role>-postcomp-<n>` TaskList task `completed` and clear it from the active set (mirroring Section 7 step 3's per-issue close-out). After fixes are done, commit.
   - **File as issue tickets**: For each issue, invoke `/quo-file-issue` with the issue description. Report the created ticket IDs to the user. If the orchestrator created any TaskList progress entries during this Section 8 pass (for example, to track per-finding filing progress), use the same per-finding discriminator pattern as the "Fix in this session" branch — name each entry `file-issue-postcomp-<n>` where `<n>` is the 1-based index of the finding being filed — and mark them `completed` and clear them from the active set before exiting, the same close-out discipline as the "Fix in this session" branch.
   - **Skip**: Done.

### 9. Recommend upstream GitHub close commands

After Section 8's post-completion review either reports clean (step 4) or the per-finding follow-ups in step 6 close out, and **before yielding the turn**, emit a copy-paste-ready recommendation block of `gh issue close ...` commands for each fixed Issue whose `reference_materials` carries a `github-issue` resolver. **Pure recommendation — the skill NEVER runs `gh issue close` itself.** No `gh` auth assumption is baked into the workflow; the user copies the command(s) and runs them from a machine where they're authenticated.

The recommendation is scoped to the `github-issue` resolver only. `linear-issue` close requires Linear's own CLI/API which isn't bundled with the workflow; the generic `url` resolver has no close concept. Adding either to this block is a separate Issue once the corresponding integration is decided — do **not** generalize the recommendation to those resolvers here.

**Procedure:**

1. **Iterate the run's fixed-issue list** — the IDs of Issues that this run actually marked `done` via Section 7 (single-issue mode: one ID; list / `all` mode: the full session list, in fixed order). Issues that were skipped (per Section 2's blocked-issue handling in batch mode), cancelled at Section 3's user-approval gate, or never reached (e.g., `bees show-ticket` validation soft-failed in Section 1) are NOT part of this list.

2. **For each fixed Issue, read its `reference_materials`.** The orchestrator captured this earlier in Section 2 / Section 3 / Section 4's dispatch reads — re-use that captured value if still in context. If not, re-read via:

   ```bash
   # POSIX (bash / zsh):
   bees show-ticket --ids <issue-id>
   ```

   ```powershell
   # Windows (PowerShell):
   bees show-ticket --ids <issue-id>
   ```

   `reference_materials` is a JSON array of `{value, resolver}` objects; an empty / null value means the Issue was filed via the in-conversation default capture mode (no upstream URL) and contributes nothing to this block.

3. **For each `reference_materials` entry whose `resolver == "github-issue"`**, parse `value` against the canonical GitHub Issue URL pattern `https://github.com/<owner>/<repo>/issues/<n>` (HTTP and HTTPS both acceptable; trailing slashes / fragments / query strings ignored) to extract `<owner>`, `<repo>`, and `<n>`. If the URL does not match this shape, skip the entry — by construction `/quo-file-issue`'s `github-issue` resolver writes only canonical Issue URLs, so a mismatch indicates a malformed entry rather than a legitimate variant to handle.

4. **Capture the per-issue commit SHA** from Section 7 step 2.4's commit step. Two equivalent paths to obtain it:
   - **Track at commit time (preferred).** Record the commit SHA the moment Section 7 step 2.4's `git commit` returns, keyed by issue ID, and re-use the captured SHA here. If the captured SHA is the full 40-char form, abbreviate it (e.g., `git rev-parse --short <full-sha>`) before emitting in step 5 — short enough to read at a glance, long enough to be unambiguous in any reasonable repo.
   - **Re-derive post-hoc.** If not tracked at commit time, resolve the commit per Issue by `--grep`-filtering the session's commits against the per-issue commit-message contract anchored at Section 7 step 2.4 (every per-issue commit's subject ends with the literal `(<issue-id>)` suffix). Run, once per fixed Issue:

     ```bash
     # POSIX (bash / zsh):
     git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD
     ```

     ```powershell
     # Windows (PowerShell):
     git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD
     ```

     Substitute the literal Issue ID (e.g., `b.abc`) for `<issue-id>` and the session-start SHA captured at Section 8 step 1 for `<pre-session-sha>`. The `-F` flag (`--fixed-strings`) makes the entire grep pattern literal — the `.` in the ID and the surrounding `(` `)` parens match as themselves rather than as regex metacharacters, removing any regex-vs-literal ambiguity for future maintainers. Each invocation returns at most one match — the per-issue commit for that Issue — and `%h` emits the abbreviated SHA directly so no follow-up `git rev-parse --short` step is needed. Scoping each lookup by the parenthesized `(<issue-id>)` token is load-bearing: the literal parens (anchored as a contract by Section 7 step 2.4) make the token unique per issue, filtering out any extra commits Section 8 step 6's "Fix in this session" branch may have landed in the same `<pre-session-sha>..HEAD` window, which would otherwise mis-pair against the fixed-issue list under a positional bulk-log pairing.

5. **Append a bullet** of the form `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."` to the recommendation block, one bullet per matching `reference_materials` entry.

6. **Suppress the entire recommendation block** if zero bullets were collected — keeps the trace clean for users who never used the URL path. Equivalently: emit nothing on runs where every fixed Issue's `reference_materials` is null/empty or carries only non-`github-issue` resolvers.

**Output shape (when at least one bullet was collected):**

```
Upstream GitHub Issues to consider closing:

- gh issue close <n1> --repo <owner1>/<repo1> -c "Fixed in <commit-sha-1>."
- gh issue close <n2> --repo <owner2>/<repo2> -c "Fixed in <commit-sha-2>."
```

Bullet ordering matches the run's fixed-issue iteration order (single-issue mode: one bullet; list / `all` mode: bullets in fixed-list order). When a single fixed Issue carries multiple `github-issue` entries in `reference_materials` (uncommon but legal — the resolver list is an array), emit one bullet per matching entry, in array order.

The recommendation block is informational console output — NOT an `AskUserQuestion` gate. The user is not asked to confirm; the orchestrator emits the block and yields.
