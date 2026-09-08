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

**Verifying the subagents precondition.** Verification rides on the procedural gate at the first dispatch: if any dispatch in the run hits an `Agent type '<name>' not found`-style error from the Agent tool for any of the eight required subagent types (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`), the orchestrator STOPS, emits the hard-fail message above, and exits — no fallback to `general-purpose`, no skipping the dispatch, no substitute role. This gate is honest about Claude Code's session-load semantics (subagents are loaded at session start; mid-session installs require a restart or `/agents` hot-reload) and cannot be bypassed by token-budget pressure or model creativity, because it fires at the natural failure point.

## Execution Flow

### 1. Determine which issues to fix

#### Check session reasoning effort

Run this check **first in this section**, ahead of the issue-pick gate below (no-args mode) and the isolation-strategy gate that follows it. Its **Let me change it first** option exits the run, so firing it before any other gate means the user never re-answers a pick they already made. Run the check once at the start of the run — not per issue.

This skill is tuned for an orchestrator session running at **`medium`** reasoning effort or higher. Every subagent dispatched from a role file (`agents/*.md`) has its effort pinned in that file's frontmatter and is **not** affected by the orchestrator's session setting, so this check concerns the seat you are running in plus any dispatch that has no role file — notably Section 8's `general-purpose` post-completion review sweep, which inherits the session setting. The skill cannot change the session setting itself — the most it can do is name the recommendation and let the user apply it.

**Ordering is load-bearing.** Read the environment variable **first**, evaluate it against the floor, and only *then* decide whether a gate fires. Do NOT create the gate task before the comparison: on the common path no gate fires at all, and a stranded `pending` `gate-*` task violates the yield-control discipline of the two-step contract — whose recovery mechanism re-fires the prescribed tool from any leftover `gate-*` task, producing a phantom prompt on a later run.

**Step 1 — read the session's current effort.** One literal command, no shell conditional (the comparison below is your own reasoning, not shell logic):

```bash
# POSIX (bash / zsh):
printenv CLAUDE_EFFORT
```

```powershell
# Windows (PowerShell):
Write-Output $env:CLAUDE_EFFORT
```

`CLAUDE_EFFORT` reports the session's **current** effort level and tracks mid-session changes (e.g. via `/model`) rather than echoing a launch-time flag, so the floor comparison reflects the level the session is actually running at when you read it.

If the output is empty, the command exits non-zero, or the value is not one of `low` / `medium` / `high` / `xhigh` / `max`, treat it as unset (an older CLI, a launch path that does not export it, or a token this skill does not know how to order): **skip this check entirely and continue to the next sub-step, silently.** A spurious prompt on every run is worse than a missed advisory.

**Step 2 — compare against this skill's floor, which is `medium`.** The ordering is `low` < `medium` < `high` < `xhigh` < `max`. Compare against the floor, never for equality — an operator running hotter than the recommendation costs wall-clock but not quality, and interrupting them is pure gate-fatigue noise.

- **At or above `medium`** — say nothing at all. No gate, no prompt, no output, and **no `TaskCreate`**. Continue to the next sub-step.
- **Strictly below `medium`** — fire the gate in step 3.

**Step 3 — fire the gate (this branch only).** This gate honors the two-step `TaskCreate` → `AskUserQuestion` contract: first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this gate (per Section 4's TaskList naming convention's gate-task entry), then call `AskUserQuestion` in the same turn. Substitute the value read in step 1 for `<current>`. Question text:

```
This session is running at `effort=<current>`, below the `medium` floor this
skill is tuned for. This skill delegates implementation rather than producing
work itself, but it still owns ticket state, dispatch ordering, gate handling
and the review loop.

Subagent effort is pinned per role and is NOT affected by this setting.
```

Present these options:

1. **Proceed anyway** — Run at the current effort level. Mark the `gate-*` task `completed` and continue to the next sub-step.
2. **Let me change it first** — Exits without dispatching anything and without fixing any issue in the list; the user runs `/model`, then re-invokes. Mark the `gate-*` task `completed`, then exit cleanly.

#### Parse the argument list and pick issues

Parse the argument string. Split on any run of commas and/or whitespace; discard empty tokens. Each token is then classified by shape: a token starting with `http://` or `https://` is a **URL token**, anything else is treated as a **ticket-ID token** (validated downstream). URL tokens space-and-comma-delimit identically to ticket-ID tokens — the tokenization itself is unchanged. The resulting tokens determine the mode:

- **Zero tokens** (no arguments): Query all open issues, present them, ask user to pick one. Fix that one issue and exit.
- **Exactly one token equal to `all`**: `all` mode — query all open issues, sort by ticket_id, then execute the fix loop (step 2-7) for each sequentially.
- **Exactly one token that is an issue ID**: single-issue mode — fix that one issue and exit.
- **Exactly one token that is a URL** (matches `^https?://`): URL mode — file the URL as an Issue first via the URL-resolution sub-step below, then fix the resulting Issue. Example: `/quo-fix-issue https://github.com/example/repo/issues/123`.
- **Two or more tokens** (list mode): treat as an explicit, user-provided list of tokens, each of which is either an issue ID or a URL (mixed lists are allowed — for example, `/quo-fix-issue b.cnb https://github.com/example/repo/issues/123 b.xet`). Execute the fix loop (step 2-7) for each issue **in the order given** (do NOT sort — the user's order is intentional; earlier issues may be prerequisites for later ones). Any URL tokens in the list are resolved by the URL-resolution sub-step below and substituted *in place* with the resulting Issue ticket ID before the fix loop runs. Do not query or fix issues outside the list. No user confirmation between issues.

Notes for list mode:
- `/quo-fix-issue b.cnb b.sgq b.xet`, `/quo-fix-issue b.cnb,b.sgq,b.xet`, and `/quo-fix-issue b.cnb, b.sgq  b.xet` all parse to the same three-ID list.
- Up-front validation: after URL resolution (per the URL-resolution sub-step below) but before starting any fixes, `bees show-ticket --ids <id1> <id2> ...` on the full post-resolution list. If any ID does not exist, is not in the `issues` hive, or is not in `open` status, report the problem IDs to the user and continue with the subset that is valid and open (do not abort the whole run). The failure check is cumulative across both gates — URL-resolution failures (per the URL-resolution sub-step's soft-fail handling) AND `bees show-ticket` validation failures both contribute to the dropped-token count. If *no* tokens remain valid after both gates, exit with an error.
- Between issues, there is no Agent-teardown ceremony to perform — the per-issue cold dispatches established in Section 4 already complete-and-exit when each Agent returns, and Section 7 closes out the per-issue TaskList tasks at issue close-out. The Issue boundary is not unmanaged, though: Section 7 step 5 runs the **Issue-boundary state-externalization checkpoint** after Section 7.5's deferral-hygiene gate and before the next issue starts. See Section 7 step 5 for the checkpoint; this bullet is an argument-parsing note and does not define it.

To query open issues (used only in no-args and `all` modes — list mode uses the user's explicit list instead):
```bash
bees execute-freeform-query --query-yaml 'stages:
  - [type=bee, hive=issues, status=open]
report: [title]'
```

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

If the working list contains any URL tokens (tokens matching `^https?://`, classified by shape per the bullet list at the top of Section 1), resolve each one to an Issue ticket ID before the upfront `bees show-ticket --ids` validation pass runs. The isolation-strategy choice made in the preceding sub-step applies to the entire run — including the file-then-fix transition this sub-step initiates — so isolating before resolution lets the user opt into a fresh branch that scopes the file-from-URL commits.

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

**End of URL-resolution sub-step — continue Section 1 and then Step 2.** After every URL token in the working list has been resolved (or soft-failed) and the post-resolution working-list display has fired, the URL-resolution sub-step is complete. Continue Section 1 at the upfront `bees show-ticket --ids` validation pass (per the "Notes for list mode" block above) and then at the `#### Write the run-state manifest` sub-step below, then proceed to Step 2 (Validate Issue), Step 3 (design analysis), Step 4 (per-issue Agent dispatch), Step 5 (review loop), Step 6 (doc verify), Step 7 (mark Issue done + commit), Step 8 (post-completion review), and Step 9 (upstream GitHub close commands) — the URL-resolution sub-step replaces nothing else in `/quo-fix-issue`'s flow. The structured return from each `/quo-file-issue` Skill-tool dispatch is a hand-off marker (per `skills/quo-file-issue/SKILL.md`'s `### Behavioral guarantees` "hand-off marker, not a workflow exit" guarantee), NOT a signal that the `/quo-fix-issue` run has terminated.

#### Write the run-state manifest

This is the **canonical definition site** for the run-state manifest; later sections refer to it by name. Write it as the last step of Section 1 — after the working list is parsed, URL tokens are resolved, the upfront `bees show-ticket --ids` validation has run, and the isolation strategy is settled — and before validating or fixing any individual Issue.

The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember. bees holds ticket state, git holds the diff, the compromise tracker holds accepted compromises, and the `defer-*` TaskList holds open deferrals; the manifest holds only what those four do not. It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.

**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `run-state-quo-fix-issue-<repo-dir-name>.md`, where `<repo-dir-name>` is the **basename of this run's repository working directory** — the last path segment of the working tree root (e.g., a run inside `/home/dev/projects/widget-api` writes `run-state-quo-fix-issue-widget-api.md`). Resolve the working tree root with one literal command, then take its last path segment:

```bash
# POSIX (bash / zsh):
git rev-parse --show-toplevel
```

```powershell
# Windows (PowerShell):
git rev-parse --show-toplevel
```

Create the `.quorum` directory if it does not already exist, then author the manifest via the `Write` tool (no shell redirect):

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write the manifest to /tmp/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write the manifest to $env:TEMP\.quorum\run-state-quo-fix-issue-<repo-dir-name>.md via the Write tool
```

**The filename is deterministic — do NOT add a random suffix or timestamp.** This deliberately differs from the compromise tracker's `<short-suffix>` naming, and the difference is load-bearing: the tracker's reader is a dispatched Agent that is handed the path in its prompt, while the manifest's reader is the orchestrator itself, possibly after a compaction that dropped the path from the conversation. A random suffix would be unfindable exactly when the manifest is needed most.

**Why the key is skill name plus repo directory — and not an Issue ID.** The key has to be recomputable by a reader that has lost the conversation, using only what the session still has: its working directory. `<repo-dir-name>` satisfies that — one `git rev-parse --show-toplevel` call recovers it at any point in the run, in any session, with no ticket lookup and no memory of how the run started. **An Issue ID does not.** In `all` / list mode the run works a batch, and the batch's membership and ordering are user-supplied and are recorded *inside this manifest* — bees stores no batch grouping — so keying the filename to (say) the first Issue of the batch would make the path depend on a value that is only recoverable by reading the very file the path points at. Nor is that ID recoverable from the run's commit subjects: those name whichever Issues have already been fixed, not which one started the batch, and by mid-run the first Issue is `done` and indistinguishable from any other closed Issue. The skill-name segment keeps this manifest from colliding with a sibling skill's manifest in the same repo; the repo-directory segment keeps two runs in two different projects from *normally* colliding in the machine-wide `<tempdir>/.quorum/`. Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends: `/quo-execute` and `/quo-breakdown-epic` append the most re-derivable ticket ID their run has, while `/quo-fix-issue` — whose batch membership is only recoverable from inside the manifest itself — appends the repository directory basename instead. See each skill's own manifest section for its rationale.

What this key does **not** discriminate is two cases, both accepted knowingly rather than hidden:

- **Two concurrent `/quo-fix-issue` runs in the same working directory.** They share one manifest filename and the later run's truncating write wins. That matches the layer below — two such runs already collide destructively over Issue statuses and commits, so it is not a case the workflow supports.
- **Two different checkouts whose directories share a basename** (e.g., `~/work/widget-api` and `~/scratch/widget-api`). The basename is only *normally* discriminating across projects, not reliably so: same-named checkouts land on one file. When runs in both are live at once, the second run's truncating write replaces the first run's manifest, and the concrete consequence is the other checkout's **Pre-session SHA** — a SHA that need not even exist in this repository — reaching Section 8's post-completion review and scoping its diff wrongly. (Sequential runs are unaffected: each truncates at run start.) The trade is accepted rather than hidden, because the alternative keys are worse — an absolute path makes the filename unwieldy and leaks directory structure into `<tempdir>`, and an Issue ID is not recomputable at all (above) — and because the failure is detectable: a manifest whose Issue batch does not match the run in hand is the tell, and a reader that spots it recovers by ignoring the manifest and taking the same `HEAD~N` fallback Section 8 already defines for a missing one.

**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**. Write it fresh here (overwriting any manifest left by a previous `/quo-fix-issue` run in this same repository directory) and rewrite it in full at each Issue boundary per Section 7 step 5's Issue-boundary state-externalization checkpoint. Never delete it — the scratch-file convention forbids cleanup, so do NOT instruct any `rm` / `Remove-Item`.

**Contents — and an invariant that bounds them.** The manifest carries **only values that have no other durable home.** Do not add Issue bodies, design directives, or review findings; those are readable from bees, the tracker, or the diff, and duplicating them here would grow the manifest into a shadow ticket store that drifts. The fields are:

```markdown
# Run state — quo-fix-issue @ <repo-dir-name>

- **Skill:** quo-fix-issue
- **Run started (UTC):** <YYYY-MM-DDTHH:MM:SSZ>
- **Unit scope:** ordered Issue batch: <issue-id-1>, <issue-id-2>, ...
- **Isolation strategy:** <branch created: <name> | current branch: <name> | worktree: <path>>
- **Pre-session SHA:** <pre-session-sha>
- **Compromise tracker:** <tempdir>/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md
- **Progress:**
  - <issue-id>: done — commit <sha>
- **Next unit:** <next-issue-id | none>
```

The **compromise tracker** field records the tracker's full path *including* its random `<short-suffix>`. Generate that filename here, at run start, per Section 7.5 `#### Session-scoped compromise tracker` (the timestamp and suffix are generated once per run), and record it in this field — the manifest is the only place a randomly-suffixed tracker path stays recoverable after a compaction. The tracker file itself is not created until its first append trigger fires; recording the path here does not create it.

The **Progress** field carries one line per Issue this run has finished with, in the order they were worked: `<issue-id>: done — commit <sha>` on the fixed path, and `<issue-id>: aborted — no commit; Issue left open` on the aborted path (Section 7 `#### Aborted-Issue close-out`). Recording the aborted shape rather than omitting the Issue is what keeps the batch's progress readable after a compaction — an Issue absent from Progress is indistinguishable from one not yet reached.

The **ordered Issue batch** is recorded verbatim in post-resolution order — that order is user-supplied and intentional (earlier issues may be prerequisites for later ones), and once the conversation is compacted there is no way to re-derive it from bees, which is exactly why it belongs here.

Capture `<pre-session-sha>` here, at run start, with one literal command — this is the **only** place the run records it. Section 8 step 1 reads it back from this file, and Section 9 reuses the value Section 8 captured:

```bash
# POSIX (bash / zsh):
git rev-parse HEAD
```

```powershell
# Windows (PowerShell):
git rev-parse HEAD
```

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

When the Analyst's completion notification fires, read the Analyst's return — the structured Design Proposal per the contract in `agents/analyst.md` `## Structured-output contract`. The proposal is **free-form analysis** (Problem / Root cause / Recommended approach / Why / Alternatives considered / Options the body did not consider / Upstream-fetch status / verdict trailer); surface it to the user as prose, NOT as an `AskUserQuestion` body — `AskUserQuestion` is for finite-multi-choice gates, not free-text design recommendations. The Analyst's `### Deferred refinements` block (per `agents/analyst.md`'s structured-return shape) is **consumed by the orchestrator and NOT surfaced to the user** — it is orchestrator plumbing for Section 7.5's deferral-hygiene gate, not user-facing design content. The consumption paragraph below ("Consume the Analyst's `### Deferred refinements` block") is the load-bearing site for that consumption; strip the `### Deferred refinements` block from the surfaced proposal before rendering the user-visible prose.

**Extract the verdict and frame the preamble.** Before surfacing the proposal body, read the `Analyst verdict: <…>` trailer line from the Analyst's return and use it to shape the one- or two-sentence prose preamble that precedes the proposal. The verdict is a load-bearing framing signal — when the Analyst found divergence, the user should encounter the proposal already knowing that, not discover it by reading carefully. Preamble shapes per verdict (adjust phrasing to fit context; the structural rule is "divergent verdicts surface divergence prominently"):

- **`recommend-as-stated`** — "The Analyst's codebase research agrees with the Issue body's framing. The Recommended approach reflects the body's approach. Proposal follows:"
- **`recommend-with-refinements`** — "The Analyst's codebase research broadly agrees with the Issue body, but the Recommended approach refines the body's framing. The refinements are called out in Why / Alternatives considered. Proposal follows:"
- **`recommend-different-approach`** — "⚠️ The Analyst's codebase research **diverged** from the Issue body's framing. The Recommended approach is an option the body did NOT propose; the Why section explains the divergence explicitly. Read carefully before approving. Proposal follows:"
- **`escalate-to-user`** — "⚠️ The Analyst could **not converge** on a single recommendation and is escalating the open question(s) to you. The Why section frames the design ambiguity; the alternatives below are the choices that need your input. Proposal follows:"

The preamble is the orchestrator's responsibility, not the Analyst's. The Analyst returns the verdict; the orchestrator turns the verdict into the user-facing framing. This split keeps the framing language consistent across runs while letting the Analyst stay focused on the design substance.

After the preamble is rendered and the proposal body is surfaced, present the user with a finite-multi-choice gate via `AskUserQuestion`. **This gate is trailer-less** — the Analyst's structured return does not embed a routing trailer, so the orchestrator prose itself is the source of the prescription. Per the two-step contract, the orchestrator's obligation at this gate is two-step in the same turn: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this Analyst-proposal gate (the `<short-suffix>` can be the Issue's short-id slug, e.g. `gate-askuserquestion-veq` for Issue `b.veq`, or any collision-resistant suffix that does not collide with `analyst-<issue-id>`), **then** call `AskUserQuestion` with the finite choices below. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once `AskUserQuestion` returns and the routing branch is entered.

- Question: "How should I proceed with this design proposal?"
- Options:
  - **Approve & proceed to implementation (Recommended)** — Accept the Analyst's Recommended approach as the authoritative design directive for this Issue. The orchestrator carries the directive forward into Section 4's implementer dispatch (the Engineer dispatch prompt when source code needs modification, the Test Writer and Doc Writer dispatches otherwise per Section 4's conditional-dispatch rules).
  - **Revise** — The user has feedback on the proposal. Iterate in prose (free-text reply), then optionally re-dispatch the Analyst with the user's feedback as additional context.
  - **Cancel** — Exit cleanly without dispatching any implementer Agent for this Issue. No commit is made; the Issue stays `open`.

#### Branch on the user's choice

- **Approve** — Capture the Analyst's Design Proposal as the run's authoritative design directive for this Issue (specifically: the `### Recommended approach` section, plus the `### Why` / `### Alternatives considered` / `### Options the body did not consider` context the Engineer may want to consult). Mark the corresponding TaskList task `analyst-<issue-id>` (or `analyst-<issue-id>-rev<n>` when this gate was re-fired) `completed` and clear it from the active set (the Analyst's work is done and its result has been consumed into the design directive). Pass the directive forward to Section 4's Engineer dispatch prompt per "Authoritative design directive" below. **When this gate was re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice**, run that choice's in-flight-lane TaskList sweep — mark every active `test-writer-<issue-id>` / `doc-writer-<issue-id>` / `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` task `completed` and discard their findings — **before** re-entering Section 4; that bullet in `### Orchestrator discipline: routing review findings` is the specification, this is only the ordering. This holds on **every** Approve reached from that re-fire — including a later Approve after one or more Revise iterations on it — not only on an Approve of the re-dispatched Analyst's first return. Proceed to Section 4.

- **Revise** — Continue the conversation with the user in prose. The user typically supplies feedback in the form "I disagree with X because…" or "have you considered Y?" — engage with that feedback in the conversation thread. When the user's feedback warrants a fresh codebase pass (a substantively different approach is on the table, the user wants the Analyst to investigate a specific code path, etc.), **re-dispatch the Analyst** as a fresh cold invocation:

  - Before dispatching, mark the prior Analyst's TaskList task `completed` and clear it from the active set — `analyst-<issue-id>` on the first revision, or `analyst-<issue-id>-rev<n-1>` on subsequent revisions (the prior Analyst's work is done and its proposal has been consumed into the user's revision feedback).
  - Issue a new Agent dispatch with `subagent_type=analyst` and a new TaskList task name `analyst-<issue-id>-rev<n>` where `<n>` is the 1-based revision count (e.g., `analyst-<issue-id>-rev1` for the first revision, `analyst-<issue-id>-rev2` for the second).
  - The new dispatch prompt embeds the same Issue body verbatim and `reference_materials` as the first dispatch, PLUS a clearly-labeled `## Prior proposal and user feedback` section that quotes the prior Design Proposal in full and the user's revision feedback verbatim.
  - When the new Analyst returns, repeat the surface-and-gate flow above.
  - There is no fixed cap on revision count; the user terminates the loop by picking Approve or Cancel.

  When the user's feedback is light enough to incorporate without a fresh codebase pass (a wording tweak, a clarification on terminology, a "yes please proceed with refinement X you mentioned in Alternatives"), the orchestrator may carry the user's clarification directly into the Approve branch without re-dispatching — capture both the original Recommended approach and the user's clarification in the design directive that flows to Section 4.

- **Cancel** — **NO commit is made; the Issue stays `open`.** Exit this Issue through Section 7's **`#### Aborted-Issue close-out`** rather than closing out by hand here: that shared sub-step marks the `analyst-<issue-id>` TaskList task `completed` (the Analyst's work is done, even if its proposal was not accepted) along with every other TaskList entry scoped to this Issue, runs Section 7.5's deferral-hygiene gate over any deferral this Issue already recorded, runs the **Issue-boundary state-externalization checkpoint** on its aborted path, and carries the mode branch — in single-issue mode the run ends there; in list / `all` mode with Issues still remaining it **stops the run** rather than continuing to the next Issue, naming the uncommitted working-tree state and the fresh-session resume command for the still-unfixed subset (see that sub-step's step 4).

#### Consume the Analyst's `### Deferred refinements` block

Independently of the Approve / Revise / Cancel routing above, the Analyst's structured return carries a `### Deferred refinements` block (per `agents/analyst.md`'s return-shape contract — on verdicts `recommend-as-stated` and `escalate-to-user` the block is structurally `None`; on `recommend-with-refinements` and `recommend-different-approach` it carries a bulleted list of refinements the Analyst proposes the orchestrator handle outside the immediate fix pass). This block is the load-bearing inter-session carrier for refinements the Analyst surfaces but the Engineer will not implement during this Issue's fix.

**At the moment of user approval — i.e., when the user picks Approve on the original proposal, when the user picks Approve after a Revise iteration (re-dispatched Analyst's return), OR when the user picks Approve after this gate was re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice — walk the latest Analyst return's `### Deferred refinements` block and create one `defer-<short-suffix>` TaskList task per non-`None` bullet whose destination annotation is `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`.** The `metadata.activity` string carries the bullet's one-line description. Bullets annotated `addressed-now-in-this-Issue` are NOT added to the `defer-*` ledger — those refinements are rolled into the `### Recommended approach` flowing into Section 4's Engineer dispatch and need no inter-session carrier. Bullets emitted without a destination annotation are a contract violation per `agents/analyst.md`'s return-shape contract; surface that back to the user as a malformed return rather than guessing a destination.

On any re-dispatch — a Revise iteration, or a re-fire from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice — the orchestrator only consumes the **latest** re-dispatched Analyst's `### Deferred refinements` block at the moment of Approve; prior blocks are superseded by the `-rev<n>` iteration the user actually approved, whichever route produced it. **Supersession clears only the `defer-*` tasks of an iteration the user never approved** — a Revise chain's, where each iteration was rejected in favour of the next: mark those `completed` with `metadata.activity` annotated as superseded before consuming the approved iteration's block. **`defer-*` tasks created at an earlier *Approve* survive a later re-fire** and stay in the active set. That approval still stands over the refinements it banked; the re-fired Analyst is briefed on the reviewer's finding rather than on those deferrals, so its block may legitimately be `None`, and nothing downstream would recover them — Section 7.5's Step 1 enumerates only tasks that are still active, and its Step 0 walks only the latest Analyst block. Clearing them would destroy every banked refinement at the first re-fire. On Cancel, no `defer-*` tasks are created from the Analyst's `### Deferred refinements` block — the Issue stays `open` and the deferrals travel with the next Analyst pass when the user re-runs `/quo-fix-issue` on the Issue.

This consumption paragraph is the load-bearing source for the Analyst-lane portion of Section 7.5's deferral-hygiene gate; without it, the gate would fire empty for Analyst-surfaced refinements, defeating the gate's purpose for that lane.

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

1. **Read state.** Pull the current truth from four sources before deciding what to do:
   - **bees** — the canonical ticket store. Use `bees show-ticket --ids <issue-id>` to get the Issue body and current `ticket_status`. Use the canonical freeform-query recipe (`bees execute-freeform-query --query-yaml '<yaml>'`) for any focused state query, e.g.:

     ```bash
     bees execute-freeform-query --query-yaml 'stages:
       - [id=<issue-id>]
     report: [title, ticket_status]'
     ```
   - **TaskList** — the orchestrator's progress UI (see "TaskList as progress UI" below). Each in-flight Agent has a corresponding TaskList task whose `status` reflects whether the Agent is `pending` (queued), `in_progress` (running), or `completed` (Agent reported done).
   - **git state** — the actual diff on disk. Workers communicate by editing files; the diff is the only authoritative record of what they actually did.
   - **the run-state manifest** — the on-disk file defined in Section 1 `#### Write the run-state manifest`, holding the run-scoped values that have no other durable home (the ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress, next unit). `Read` it at `<tempdir>/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md`; the path is derived from this skill's name plus the basename of the working tree root (`git rev-parse --show-toplevel`), so it is recomputable from the session's own working directory even when nothing about the run survives in the conversation. **Validate it before trusting any field:** compare its **Unit scope** ordered Issue batch against the batch this run is fixing, and if it names Issues this run is not working — the stale/foreign-manifest tell Section 1 `#### Write the run-state manifest` describes, where a concurrent run in a same-basename checkout truncated the file — treat the manifest as absent and recover per that section rather than reading a foreign run's `<pre-session-sha>`, isolation strategy, or tracker path into this tick.

   **Conversation memory is never a substitute for these four sources.** Whatever the orchestrator believes it remembers about Issue status, landed commits, the batch order, or the pre-session SHA, the four sources above are the truth and are re-read rather than recalled. This is unconditional — it holds on every tick, not only after something goes wrong. On top of it, one conditional rule for the observable case: **if a summarization marker is visible in the conversation** (the harness compacted mid-run), treat everything before it as non-authoritative and re-read all four sources in full before dispatching anything else — starting with re-reading the Issue body from bees rather than working from a summary of it. One value has no durable carrier by design: Section 3's authoritative design directive lives only in the Analyst's returned message until it is embedded in the Engineer dispatch prompt. If a compaction lands in that window, do **not** reconstruct the directive from a summary — re-dispatch the Analyst per Section 3 and re-run its approval gate.

   The Issue ticket type only supports two statuses — `open` and `done` — so there is no in-flight bees status to set while work is underway. The TaskList progress UI carries the in-flight signal (per-Agent `pending` / `in_progress` / `completed`), and the orchestrator flips the Issue from `open` to `done` only at issue close-out (per Section 7).

2. **Reconcile.** Compare current state to target state and act. Dispatch for an Issue is **ordered into three phases** — the implementer lanes are NOT fanned out together, and the reviewers are not all held to the end. Walk the phases in order; dispatch concurrently only *within* a phase.

   - **Phase A — source to clean.** When the fix needs source changes, dispatch the **Engineer alone** (see "Per-issue cold dispatch" below). On its return, dispatch the **Code Reviewer alone** (Section 5 carries the reviewer dispatch shape and `code-reviewer-<issue-id>` naming). Loop Engineer → Code Reviewer → Engineer until either the Code Reviewer emits its clean shape (`No code issues found.`) or every remaining finding has been routed through `### Orchestrator discipline: routing review findings` — accepted into the session-scoped compromise tracker (Section 7.5), recorded as a `defer-*` task (Section 5's ignored-feedback rule), or gated to the user. Every round after the first uses a round-discriminated TaskList name (`engineer-<issue-id>-r<n>` / `code-reviewer-<issue-id>-r<n>`, per the TaskList naming convention below). When the Issue needs no source change at all, Phase A is empty and the loop proceeds directly to Phase B.

     **The Phase A exit test reads the numbered work-item list only.** `/quo-engineer-review` emits a `### Second-order effects` subsection on **every** review, clean ones included, so a clean review can legitimately carry narrative bullets there. **A non-empty `### Second-order effects` narrative alongside a clean numbered list does NOT block Phase A closure.** By that skill's double-emission rule, anything actionable a second-order effect surfaced is *already* present in the numbered list as a severity- and depth-tagged work item; what remains under the heading is context recorded for the audit trail. Carry that narrative forward into the per-issue summary's `**Second-order effects**` field (Section 7 step 4) — that field is its destination — and do not re-dispatch the Engineer against it or hold Phase A open for it.
   - **Phase B — writers once, in parallel.** Once Phase A has closed, dispatch the **Test Writer** (when tests need changing) and the **Doc Writer** (always) concurrently. This is the **only** place these two roles are dispatched on the forward path — they read a diff whose source half is already review-clean, so they do not pin behavior that a later code-review round rewrites.
   - **Phase C — remaining reviewers plus PM.** When the Phase B writers have returned for this Issue **and no `aborted-*` TaskList task for this Issue is `pending`** (the aborted-lane guard from the movement-report rung below — match on the `aborted-` name prefix plus the status), advance to Section 5 and dispatch the **Test Reviewer** (if the Test Writer ran), the **Doc Reviewer** (if the Doc Writer ran), and the **PM** (always). The Code Reviewer is NOT dispatched again here — it already ran to closure in Phase A. The orchestrator does not pre-judge whether a PM pass is needed.
   - **Engineer-dispatch precondition (checkable, not a promise).** The orchestrator **MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, or `pm-<issue-id>` is `pending` or `in_progress`.** Match on the name **prefix** plus the status, never on an exact name — Phase A's round discriminator (`-r<n>`) and any other suffix a re-dispatch appends must still be caught by this check. This is a **precondition to check, not a state to remember**: before *every* Engineer dispatch — forward Phase A rounds and re-entry rounds alike — walk the TaskList (one of the four authoritative read-state sources this tick already reads) and confirm no task matching those prefixes is active. Deriving the rule from the TaskList rather than from orchestrator memory is what makes it survive a compaction — see the "Conversation memory is never a substitute for these four sources" discipline above.

     **Why the two Phase C reviewers and the PM are covered, not just the writers.** A writer handed a diff an Engineer is about to rewrite has to redo its work. A **reviewer or PM** that is mid-read when Engineer edits land is worse: the verdict it returns describes a diff that no longer exists, so the whole round is spent and has to be repeated — precisely the cost this phase ladder exists to save. So a Phase C finding that re-enters Phase A waits for **all** Phase C returns before the Engineer is dispatched.

     **The Code Reviewer is the one deliberate exception, and is NOT in the prefix list.** Phase A alternates Engineer and Code Reviewer by construction — the Code Reviewer is dispatched only on an Engineer's return, and the next Engineer is dispatched only on the Code Reviewer's return — so a `code-reviewer-<issue-id>` task is never in flight at the moment an Engineer dispatch is being considered. Listing it would add a test that can never fire, and would read as licence to dispatch the two concurrently if it ever did. The exclusion rests on that alternation, so it is specific to this ladder: it does **not** generalize to a review site where the Code Reviewer runs concurrently with other reviewers.

     **When the blocking task is `pending` with no Agent behind it.** `pending` is in the status test deliberately: it closes the race where the orchestrator has created the task but the `Agent(...)` call has not landed yet. But a `pending` task with no dispatch behind it will never produce a completion notification, and there are no clock primitives to time it out (see "Anti-pattern: no clock primitives" below), so waiting on it deadlocks the loop. Therefore: when the blocking task is `in_progress`, or is `pending` **with a dispatch already landed**, wait for its completion notification and re-check on the next tick. When it is `pending` and **no dispatch has landed for it**, do not wait — either dispatch that role now (when its work is still wanted) or mark the stale task `completed` and clear it from the active set (when it is not), then re-check the precondition. Do **not** narrow the rule to `in_progress` only; `pending` stays in the test, and this clause is what keeps it from stranding the loop.

     **A writer that aborted on source movement does not block an Engineer round, and needs no exemption.** When a writer returns a movement report, the **movement-report rung** below marks that writer's own `test-writer-<issue-id>` / `doc-writer-<issue-id>` task `completed` — its Agent has exited — and records the owed redelivery as a separate `aborted-<role>-<issue-id>` task. `aborted-` is a **distinct name class**, so the prefix test above structurally does not match it and no exemption clause is needed: an Engineer can be dispatched to settle the source while the redelivery stays owed. This is deliberate — an exemption keyed on an abort annotation would make the Engineer's dispatch depend on `metadata.activity`, which is informational and not a routing input. What the `aborted-*` task gates is **Phase C**, not the Engineer; see the movement-report rung.
   - **Re-entry from Phase C.** A Phase C finding whose chosen fix path changes **source** re-enters Phase A: dispatch the Engineer, then the Code Reviewer, and loop until Phase A re-closes. When it does, re-dispatch **only** the writer lanes whose input the source change invalidated (the Test Writer when the behavior its tests pin moved, the Doc Writer when the diff it documented moved), then re-run the corresponding Phase C reviewers. A Phase C finding confined to a writer's own lane (a test-quality nit, a doc-wording gap, anything that changes no source file) re-dispatches that writer alone and does **not** re-enter Phase A. The ordering rule for any re-dispatch that touches source is part (g) of `### Orchestrator discipline: routing review findings`.
   - **Post-compaction recovery inside Phase A.** "Did the last code review come back clean?" has **no durable carrier**, and it should not be given one. The run-state manifest records only values that live nowhere else on disk; a lane's phase is not such a value, because it is **re-derivable at any moment by asking the Code Reviewer again**. So do NOT add a lane-phase field to the manifest. If a compaction lands mid-Phase-A and the orchestrator cannot read the Code Reviewer's last verdict from the conversation, **re-dispatch the Code Reviewer**: a cold fresh-eyes pass over the current diff is idempotent and cheap, and is the correct recovery rather than guessing the prior verdict.
   - **Movement report from a Phase B writer.** `agents/test-writer.md` and `agents/doc-writer.md` both instruct the writer to **stop mid-run and report** when the source it was working against moved underneath it (the Test Writer detects this with a `git rev-parse HEAD` + `git hash-object` fingerprint taken at start and again before finishing; the Doc Writer, which has no `Bash`, re-reads with `Read` / `Grep`). That report is a distinct return shape and this rung is its receiver — without one, the orchestrator marks the task `completed`, advances to Phase C, and dispatches a reviewer against tests or docs the writer never finished writing.

     **Recognising it.** Read the writer's return before persisting anything. A movement report says the source moved and names what moved (files, and the opening/closing HEAD when HEAD moved) plus how far the writer's work got, in place of — or alongside a partial version of — the normal completed deliverable. Both role files scope the obligation per mode, and **fix mode is the strict branch**: one implementation pass per Issue means every Engineer in play is this Issue's, so movement outside the writer's own lane is anomalous rather than expected concurrency, and neither writer is told to shrug it off. (The role files' softer execute-mode branch — record sibling-Subtask movement as an observation and finish — has no analogue here; do not import it.) **The two writers detect different things, and the receiver should not overstate either.** The Test Writer's trigger is mechanical and broad: any changed hash in its `## Source paths to fingerprint` set, a moved `HEAD`, or a path that no longer hashes. The Doc Writer's is narrower and judgement-based, because it has no `Bash` and no fingerprint: it stops when **the material it is documenting appears to have moved — a file it read earlier no longer matches the prose it wrote against it** (`agents/doc-writer.md`). So a Doc Writer that never re-read a given file will not report movement in it; do not read its silence as a clean-tree attestation over every source path. What marks either return as a movement report is that the writer **stopped**.

     **What to do.** Do **NOT** unlock Phase C on that lane — it has not delivered. Record the owed redelivery as a durable TaskList entry instead, the same obligation-as-pending-task pattern `defer-*` and `gate-*` already use:

     1. **Mark the writer's own TaskList task `completed`** — `test-writer-<issue-id>` / `doc-writer-<issue-id>`, including any `-r<n>` suffix it carries. Its Agent **has** exited, so leaving it active would strand a task no completion notification will ever clear.
     2. **Create a new `aborted-<role>-<issue-id>` TaskList task** — `aborted-test-writer-<issue-id>` / `aborted-doc-writer-<issue-id>`, per the naming convention below — with status `pending` and the writer's "how far I got" report as its `metadata.activity` string. That pending task **is** the redelivery-owed marker: the orchestrator reads it off the TaskList on the next tick rather than holding it in conversation, so it survives a compaction. What routing tests is the task's **name prefix and status**; the `metadata.activity` string is informational context for the re-dispatch prompt, consistent with `metadata.activity` never being a routing input.
     3. **Phase C MUST NOT begin while any `aborted-*` task for this Issue is `pending`.** That is the gate this marker exists to hold — a Test Reviewer, Doc Reviewer, or PM dispatched over a half-written test or doc set spends its round for nothing.

     Then re-dispatch the lane, per who moved the source:

     - **When the mover was an Engineer** (a Phase A round that was still landing, or a re-entry round) — **in fix mode this should not occur**: Phase B begins only after Phase A has closed, and the Engineer-dispatch precondition keeps an Engineer out while any writer task is active, so an Engineer landing edits during Phase B indicates a **precondition breach**. Treat it as one — recover through the ordering below rather than reading it as a normal path, and note the breach when it happens rather than absorbing it silently. Phase A must **re-close first** — finish the Engineer → Code Reviewer loop per Phase A above, and only once it closes re-dispatch the writer. Re-dispatching the writer against a still-moving diff reproduces the abort. The `aborted-*` task holds Phase C shut throughout, and does not block that Engineer round: it is a different name class from the Engineer-dispatch precondition's prefixes.
     - **When the mover was the sibling Phase B Test Writer's discrimination experiment** — the second **attributable** in-workflow mover, and the one most easily misread as an external edit. `agents/test-writer.md` sanctions perturbing a source file **in place** with `Edit` / `Write` (restoring afterwards from a scratch copy) to confirm a test really fails without the fix, and requires the Test Writer's return to list every perturbed path under a `## Perturbations` heading, `None` when there were none. Phase B dispatches the Doc Writer always and the Test Writer **only when tests need modification**; when both are in flight they run concurrently, so a Doc Writer can legitimately observe a Test Writer's perturbation as source moving under it. Read the Test Writer's `## Perturbations` heading: when it lists **every** path the aborted writer reported as moved, the movement is attributed — self-inflicted by the workflow and already restored — so **re-dispatch the aborted lane once that sibling has returned, with no gate**; when it covers only **some** of them, fall through to the external-actor case below for the remainder. **When a Test Writer was dispatched in Phase B and has not returned yet, do not classify and do not fire the gate**: it is a live dispatch that *will* notify, so wait for its completion notification, read its `## Perturbations` heading on that tick, and classify then. This case fails to apply once every dispatched Test Writer has returned and none lists the moved path — and it **never applies at all when Phase B dispatched no Test Writer** (a doc-only Issue, where the Doc Writer is the only Phase B lane): there is no notification coming, so do not wait for one. Either way, fall through to the external-actor case below.
     - **When the mover was an external actor** (the user, a second session, a background process — nothing this orchestrator dispatched): re-dispatch the writer once the movement is understood, i.e. once the orchestrator has read the current diff and can see the tree has settled. When the movement is **unexplained**, fire the **unexplained-movement gate** below instead of re-dispatching into it.

     Either way the re-dispatch is a repeat dispatch of an already-named role, so it takes the next `-r<n>` round-discriminated TaskList name per the naming convention below (`test-writer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`, …). Carry the writer's "how far I got" report — the `metadata.activity` string on the `aborted-*` task — into the re-dispatch prompt so the fresh Agent does not start from zero. **When the re-dispatched lane returns a normal deliverable, mark the `aborted-*` task `completed`** — that is what releases Phase C. If the re-dispatched lane aborts on movement again, repeat this rung from the top: mark its own `-r<n>` task `completed` and refresh the **existing** `aborted-*` task's `metadata.activity` with the newer report rather than creating a second one — it is the same obligation, still owed.

     **Unexplained-movement gate.** The movement is unexplained when the orchestrator dispatched **no** Engineer for this Issue over the window the writer reports, **no returned Phase B Test Writer's `## Perturbations` list covers the moved paths** — with the remainder still uncovered when a list covers only some of them, and **including the case where Phase B dispatched no Test Writer at all**, so no such list exists to check — and **no dispatched Test Writer is still in flight** (per the case above), and it cannot otherwise account for who changed the source or whether more is coming. Do not re-dispatch blindly — a blind re-dispatch loop is the failure mode this branch exists to prevent. Fire this gate through the two-step `TaskCreate` → `AskUserQuestion` contract: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this unexplained-movement gate (per the TaskList naming convention below), **then** call `AskUserQuestion` in the same turn. Do not produce a text response describing the gate — fire the two calls. The yield-control discipline applies: do not yield to the harness while the `gate-*` task is `pending` or `in_progress`.

     The question text carries the writer's movement report **verbatim** — which files moved, the opening and closing HEAD when HEAD moved, and how far the writer's work got — plus this one-line statement: *the orchestrator dispatched no Engineer for this Issue while the writer was running, and no Phase B Test Writer's `## Perturbations` list names the moved paths — either because the lists it received do not name them, or because Phase B dispatched no Test Writer for this Issue at all — so it cannot attribute the movement.* Offer exactly these three options. The gate is multi-choice only; do not add fake free-text options duplicating `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot:

     - **Re-dispatch the writer now** — the movement is understood or accepted. Re-dispatch the lane under its next `-r<n>` name against the current tree, per the paragraph above.
     - **Wait** — the operator resolves the external change first. The orchestrator yields control and re-fires this gate **only on the operator's reply** — that reply is the trigger, and it is the only one. Do **not** read this as "no Agent is in flight": Phase B dispatches the Test Writer and the Doc Writer **concurrently** and the Doc Writer is always dispatched, so the sibling lane can return its completion notification seconds after the operator picked Wait. **A sibling lane's completion notification is a tick that processes that lane normally** through the Reconcile step above — persist its result, mark its task `completed` — and it **MUST NOT** re-fire this gate. The rule is derivable from the tick's trigger and needs no bookkeeping: re-fire on the operator's reply, never on an Agent notification. (Do not record the Wait state in `metadata.activity` and route on it — that string is informational and is never a routing input.) The `aborted-*` task stays `pending`, so Phase C stays shut across the wait.
     - **Abort this Issue** — the Issue stays `open` and nothing is committed for it. Do **not** simply move on to the next Issue: route the exit through Section 7's **`#### Aborted-Issue close-out`**, which sweeps this Issue's TaskList tasks by prefix (including the `aborted-*` marker this rung just created), runs Section 7.5's deferral-hygiene gate, runs the **Issue-boundary state-externalization checkpoint** on its aborted path, and — in batch mode with a next Issue still remaining — **stops the run** instead of continuing, naming the uncommitted working-tree state this abort leaves behind and the fresh-session resume command for the still-unfixed subset (that sub-step's step 4). Unlike a fixed Issue, an aborted one does not hand its dirty tree to the next Issue in the batch.

     Mark the `gate-*` task `completed` the moment the answer is consumed and the chosen branch is entered — including on **Wait**, where consuming the answer means yielding; the re-fire on the next tick creates a **fresh** `gate-askuserquestion-<short-suffix>` task rather than reusing the closed one.

   - For every Agent that has reported completion, persist the result: confirm any bees ticket transitions the Agent committed to, mark the corresponding TaskList task `completed`, and unlock the next phase (or the next lane within the current phase) per the ladder above. **A Phase B writer return that reports detected source movement is not a completion** — route it through the movement-report rung above instead: it does not unlock the next phase. That rung does close out the writer's own TaskList task (the Agent has exited), but it opens an `aborted-*` task in its place, and Phase C stays shut while that task is `pending`.

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

Which roles to dispatch for a given Issue — and **when**, per the Reconcile step's phase ladder. These three are not dispatched together:

- **Engineer** — dispatched in **Phase A** when source code needs modification, alone, looping with the Code Reviewer until Phase A closes. Never dispatched while any TaskList task for this Issue whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, or `pm-<issue-id>` is `pending` or `in_progress` — see the Reconcile step's **Engineer-dispatch precondition** for the prefix-match rule, the Code Reviewer exception, and the stranded-`pending` clause.
- **Test Writer** — dispatched in **Phase B**, once, when tests need modification.
- **Doc Writer** — dispatched in **Phase B**, once, always. The Doc Writer decides whether docs actually need updating after reading the diff; the orchestrator does not pre-judge.

The Product Manager is no longer an implementer-phase role — it is dispatched in **Phase C** alongside the remaining reviewers on every Issue (see Section 5's reviewer dispatch block).

Reviewer Agents and the Product Manager Agent take their dispatch shape and TaskList naming from Section 5. The **Code Reviewer** is dispatched in **Phase A**, interleaved with the Engineer rather than after all implementers return; the **Test Reviewer**, **Doc Reviewer**, and **PM** are dispatched in **Phase C**, after the Phase B writers return.

##### Per-issue cold dispatch (vs SDD's warm-Agent intent)

The original SDD intent was warm Agents that would receive `SendMessage` pings between roles, amortizing context-load cost across an Issue. That path requires the experimental teams substrate per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents) — and this skill set does not use that substrate at all, so `SendMessage`-based warm dispatch is not available. The trade-off is conscious: each cold-dispatched Agent re-loads its role file and any referenced docs, which is more tokens than a warm ping, but the architectural simplification (no long-lived team to manage, no shutdown choreography, no peer-to-peer coupling) is worth it; in practice prompt caching mitigates most of the cold-load cost. The divergence from the SDD's warm-Agent intent is intentional and is tracked by a re-probe issue in this skill set's own backlog; revisit if the upstream constraint changes.

##### Dispatch prompt: quote the issue body verbatim and embed the design directive

The dispatch prompt sent to each Agent must embed the Issue body **verbatim** — paraphrasing silently corrupts identifier names (function names, flag names, type names) that the worker will then use literally. Read the Issue via:

```bash
bees show-ticket --ids <issue-id>
```

Embed the returned body block in the dispatch prompt as a quoted block. Do not summarise, paraphrase, or "clean up" identifier spellings. Framing prose around the quoted block (e.g., "your gating precondition is met — start now") is fine; the body itself stays untouched. The orchestrator's own progress signal is the TaskList progress UI (see below) — the dispatch prompt does not need to ask the worker to ping back, because Agent completion notifications are delivered automatically by the substrate.

**Engineer dispatch — embed the Section 3 design directive as the authoritative design source.** When the dispatched role is `engineer`, the dispatch prompt MUST additionally embed the design directive captured at the end of Section 3's Approve branch (the Analyst's `### Recommended approach` section, plus `### Why`, `### Alternatives considered`, and `### Options the body did not consider` for context, plus any user-supplied refinement captured on the Approve branch). Label that block clearly in the prompt — recommended labels are `## Authoritative design directive (from Section 3 Analyst pass)` for the Recommended approach itself and `## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)` for the surrounding context — so the Engineer can distinguish the directive from the verbatim Issue body. Where the Issue body's framing and the design directive conflict, **the directive wins**: the body still flows in verbatim because identifier spellings, contract surfaces, and other byte-accurate references travel with it, but the design source the Engineer implements is the directive. The Engineer's role file (`agents/engineer.md`) carries the same invariant in its **Authoritative design directive (fix mode only)** bullet, so the directive-wins rule is reloaded on every cold dispatch even if the dispatch-prompt framing is terse. The Test Writer and Doc Writer dispatch prompts do NOT carry the design directive separately — they read the resulting diff (the Engineer's implementation of the directive) as their work signal, per the hub-and-spoke flow.

**Code Reviewer dispatch — relay the Engineer's completeness evidence verbatim.** `agents/engineer.md` requires the Engineer's return to carry a **completeness check with evidence** whenever its assignment directed a change at *every site* where some property holds (the search patterns run, every hit, and per hit either the change made or the reason it is deliberately untouched). That evidence has no other carrier — the Engineer Agent has exited and its return lives only in this conversation — so **when an Engineer's return for this Issue carried a completeness list, the Phase A Code Reviewer dispatch prompt MUST embed that list verbatim** under a clearly labelled heading; the recommended label is `## Engineer's completeness evidence`. Embed it as text in the prompt (the same way the Issue body and the design directive are embedded) — do **not** write it to a scratch file and pass a path. `agents/code-reviewer.md` carries the Code-Reviewer-side half (pass the list through into its `/quo-engineer-review` invocation). **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was** — that is a fact about the assignment that was dispatched (a directive or Subtask body that directed a change at *every site* where some property holds), known independently of whether a list came back. `/quo-engineer-review`'s sweep-verification check only reports a *missing* list as a finding when the invocation itself named the assignment that way, so an unnamed sweep silently loses the check — and the case that most needs the check is precisely a sweep-shaped assignment whose Engineer returned no list. When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one — but still state that the assignment was sweep-shaped when it was, so `/quo-engineer-review`'s missing-list check stays reachable.

**Test Writer / Doc Writer dispatch — state the orchestrator-side rule, never a freeze guarantee.** The Phase B writer dispatch prompts MAY state the rule the orchestrator actually controls: **"no Engineer Agent will be dispatched for this Issue while you are running"** — that is a decision about the orchestrator's own dispatches, enforced by the Engineer-dispatch precondition in the Reconcile step above, so it is a claim the orchestrator can keep. Keep the `for this Issue` qualifier: `agents/test-writer.md` and `agents/doc-writer.md` scope the guarantee per mode, and this is the fix-mode wording their fix-mode branch expects. The prompts **MUST NOT** claim that **"the source tree is frozen"**, or any close paraphrase promising the files will not move. The orchestrator cannot prevent the user, a second session, or a background process from editing the tree, so that phrasing promises a lever the orchestrator does not hold — an unkeepable guarantee, not a dispatch instruction. `agents/test-writer.md` carries the writer-side half (capture the tree's state at start, re-check before finishing, stop and report if source outside the writer's lane moved), so the writer's recovery path does not depend on the dispatch prompt getting the wording right.

**Test Writer dispatch — supply the fingerprint path list.** `agents/test-writer.md`'s movement fingerprint hashes a set of non-test source paths, and the orchestrator already knows that set — **not by re-deriving it from the tree, but by carrying forward the changed-file list the Engineer's own return supplied.** `agents/engineer.md` requires every Engineer return to carry a `## Files changed` list, so the orchestrator has the set in hand the moment Phase A closes: take the Phase A Engineer return(s) for this Issue, **union the lists across every Phase A round** (a later round's Engineer may have touched files the first did not), drop any test paths, and emit what remains under a labelled `## Source paths to fingerprint` heading — one path per line, repository-relative — so the writer does not have to derive it. Include only non-test paths; the writer's own test files are excluded by construction. **An explicitly-empty `## Files changed` list is a list, not a missing one:** an Engineer round that changed nothing contributes nothing to the union and does **not** trigger the fallback below. So when every round in scope carried a list and the union across them is empty, **omit the `## Source paths to fingerprint` heading** rather than emitting an empty one — `agents/test-writer.md`'s empty-path-set clause keys on the heading being *absent*, and an empty heading would read to the writer as a supplied set rather than as none.

**Fallback when an Engineer return did not list files.** Derive the set with one literal command and drop the test paths from the result:

```bash
# POSIX (bash / zsh):
git diff --name-only HEAD
```

```powershell
# Windows (PowerShell):
git diff --name-only HEAD
```

Prefer the return-carried list whenever one exists: this fallback reads the **whole working tree**, so it picks up anything else uncommitted there — another actor's in-flight edit, a stray local change — not only this Issue's fix, and every extra path is one the writer will stop on. When Phase A was empty (no Engineer ran, so there is no diff at all), omit the heading rather than emitting an empty one — `agents/test-writer.md` carries the fallback derivation and the empty-path-set handling for that case.

The framing prose around the quoted block MUST NOT loosen the role boundaries defined in the dispatched role's contract file (`agents/<role>.md`). The rule applies to **every** dispatched role type — both the implementer roles (Engineer / Test Writer / Doc Writer) and the review-only roles (PM, Code Reviewer, Test Reviewer, Doc Reviewer). Concrete examples of forbidden softening (illustrative, not exhaustive):

- MUST NOT tell the Engineer it may also write tests or docs.
- MUST NOT tell the Test Writer it may also modify source code.
- MUST NOT tell the Doc Writer it may also modify source or test files.
- MUST NOT tell the PM or any reviewer (Code Reviewer / Test Reviewer / Doc Reviewer) it may write source, tests, or docs — these are review-only roles, and the contract files state "Does NOT modify source code, tests, or docs" (PM) and "Does NOT review <other-lanes>" (each reviewer) explicitly.
- MUST NOT tell one reviewer it may also review another reviewer's lane (e.g., Code Reviewer reviewing tests, or Test Reviewer reviewing documentation).

The role boundaries are a structural property of the workflow — if the orchestrator finds itself tempted to carve an exception ("you may also add this one test file" / "you may also touch this one source line"), that is a signal the per-role division of labor needs orchestrator-level coordination (a follow-up Test Writer dispatch, a redirect of the Issue, etc.), NOT a softening clause in the dispatch prompt. Workers do not message each other; the only handoff is from worker to orchestrator (the diff in execution mode, the JSON return in research mode), never worker-to-worker. So a softening clause cannot be made safe by adding "coordinate with the other role's diff" or similar coordination prose — that channel does not exist.

When the Issue's `reference_materials` is non-empty (the external-reference mode produced by any of `/quo-file-issue`'s URL entry surfaces — bare URL `/quo-file-issue <url>`, the flag forms `/quo-file-issue --reference <url>` / `--from-github <url>`, or this skill's URL-resolution sub-step's inline-Skill-tool dispatch — all of which produce the same `reference_materials` shape), embed the `reference_materials` JSON value alongside the (thin) body in the dispatch prompt so the worker can read the resolver name and URL. Workers (the Analyst in Section 3; the Engineer in Section 4; the PM in Section 5) handle the upstream content fetch via `WebFetch` per their role contracts in `agents/analyst.md`, `agents/engineer.md`, and `agents/pm.md`; the orchestrator does not pre-fetch the URL.

#### Hub-and-spoke via substrate

Workers do not message each other. The orchestrator is the hub; each dispatched Agent is a spoke that reads its prompt, edits files, and exits. The diff is the handoff between roles — when the Engineer finishes, the next role (the Code Reviewer in Phase A; once Phase A has closed, the Test Writer, Doc Writer, or PM) reads the resulting diff to do its work. Hub-and-spoke is a **structural property** of ephemeral background Agents, not a rule the orchestrator must remember to enforce: there is no inter-Agent channel for workers to even attempt peer-to-peer coupling on.

#### Recursive delegation: not supported

Per the [Claude Code sub-agents docs](https://docs.claude.com/en/docs/claude-code/sub-agents), "Subagents cannot spawn other subagents" — only the top-level orchestrator may dispatch Agents. The skill ships **flat orchestration**: every Agent invocation originates from this skill's reconciliation loop, never from a worker.

Flat orchestration means the orchestrator's working context grows **monotonically within a session** — every Analyst pass, every implementer dispatch, every reviewer and PM return, and every reconciliation tick adds to the loop's running set, and in `all` / list mode that set accumulates across every Issue in the batch — and **nothing in this skill reclaims those tokens.** Token reclamation is owned by the harness, which compacts the conversation on its own once the window fills; the skill has no model-invocable way to clear or compact its own context. What the skill does guarantee is that the growth is **survivable**: Section 7 step 5's **Issue-boundary state-externalization checkpoint** keeps every load-bearing fact in a durable carrier the orchestrator can re-read, so whenever the harness compacts — at an Issue boundary or in the middle of one — the run can be re-derived rather than reconstructed from memory. The actual reclamation lever is starting a **fresh session**, which the fresh-session-per-phase recommendation at run close-out prescribes; the checkpoint is what makes that lever safe to pull at any point.

#### Roles dispatched by the orchestrator

The orchestrator dispatches the following three implementer roles per Issue. The full role contracts (responsibilities, gating preconditions, instructions, shell-command etiquette) live in the role files; the orchestrator's job is to invoke the right role at the right time, not to carry the role's prose.

- **Engineer** (`agents/engineer.md`) — implements source-code changes for the fix. Model: Opus (always). Does not write tests or docs.
- **Test Writer** (`agents/test-writer.md`) — writes / updates / deletes tests to verify the fix and reviews the Engineer's diff for missing coverage. At minimum, ensures there is at least one test that fails before the Engineer's fix and passes after — this is the regression guard that prevents the same bug from recurring. Model: Opus (always).
- **Doc Writer** (`agents/doc-writer.md`) — reviews the Engineer's diff for documentation gaps and updates customer-facing and internal docs as needed, and additionally appends or updates the relevant `### Feature: <title>` subsection in the project's cumulative PRD and SDD (per the lookup-key paths in CLAUDE.md `## Documentation Locations`) when the fix lands user-visible behavior or architectural shifts that warrant a cumulative-doc entry — see `agents/doc-writer.md` for the categorization heuristic, idempotency rule, and `<title>` resolution recipe. In fix mode the Doc Writer is dispatched once per Issue (not per Subtask as in execute mode), and the Plan Bee — when one exists — is discovered via the Issue's `up_dependencies` rather than a parent-chain traversal; `agents/doc-writer.md` is the authoritative spec for that traversal. When the Issue body contains a `## Doc divergence noted` section (authored by `/quo-file-issue` when the filer flagged that an existing doc is wrong about the buggy behavior), the Doc Writer treats that section as an explicit doc-correction directive: the named file/section is wrong about today's behavior, and the documented correction is applied as part of this fix's doc updates. Model: Opus (always).

Reviewer roles (`agents/code-reviewer.md`, `agents/test-reviewer.md`, `agents/doc-reviewer.md`) and the Product Manager role (`agents/pm.md`) are introduced in Section 5 — the PM is always dispatched alongside the reviewers on every Issue, mirroring the always-dispatched pattern Doc Writer already uses in the implementer phase.

#### TaskList as progress UI

The orchestrator uses Claude Code's native **TaskList** as the visible progress UI for the run. There is no separate display backend to configure — TaskList renders in the harness automatically, replacing the team-display surface a prior message-bus substrate would have required.

For every Agent the orchestrator dispatches, it creates exactly **one** TaskList task:

- **`pending`** — created when the orchestrator decides this role is next for the current Issue but before the Agent invocation lands.
- **`in_progress`** — set the moment the Agent invocation is dispatched (`Agent(...)` returns).
- **`completed`** — set when the orchestrator processes the Agent's completion notification and confirms the worker's reported deliverables landed (file edits visible in `git status` / `git diff`, any bees ticket transitions the worker committed to are reflected on disk). **One exception:** a writer lane that returned a movement report has its task set `completed` **without** landed deliverables — the Agent exited, which is what this status tracks, while the delivery obligation moves to an `aborted-*` task (see Section 4's Reconcile-step movement-report rung). `completed` on an Agent task means "this Agent is gone", not "this work shipped".

Use `metadata.activity` on the TaskList task to surface finer-grained progress when a worker emits intermediate signal (e.g., `"running narrow tests on package X"`, `"resolving Scoped-marker via up_dependencies iteration"`). The orchestrator updates this string opportunistically; it is informational, not a routing input.

##### TaskList naming convention

The naming convention is the **canonical cross-reference** for downstream Sections of this SKILL.md (Section 5's reviewer dispatches and Section 7's TaskList completion at issue close-out consume these names). It is deterministic so two concurrent invocations cannot collide and unambiguous so any reader can map a TaskList entry back to its Issue.

Naming is **issue-scoped** for every per-issue role — there is no Subtask breakdown under an Issue, so the parent ticket id used as the scope suffix is always the Issue id. The URL-resolution Skill-tool dispatches in Section 1's URL-resolution sub-step run *before* per-issue dispatch begins (the URL has not yet been resolved to an Issue ID at that point), so they use a positional-index discriminator instead:

- **Analyst Agents** (dispatched per Issue in Section 3 before the implementer phase) — Name: `analyst-<issue-id>` (e.g., `analyst-veq` for Issue `b.veq`). When the user picks `Revise` and the orchestrator re-dispatches the Analyst with the user's feedback as additional context, append a `-rev<n>` discriminator where `<n>` is the 1-based revision count (e.g., `analyst-veq-rev1` for the first revision, `analyst-veq-rev2` for the second) — per Section 3's Revise-branch instructions.
- **Implementer Agents** (Engineer, Test Writer, Doc Writer) — Name: `<role>-<issue-id>` (e.g., `engineer-veq`, `test-writer-veq`, `doc-writer-veq` for Issue `b.veq`). **Round discriminator for repeat dispatches.** The Phase A loop dispatches the Engineer once per round, and a Phase C finding can re-dispatch a writer, so the same role is dispatched against the same Issue more than once in a run. The "exactly one TaskList task per Agent" rule above still holds, so every dispatch after the first appends `-r<n>`, where `<n>` is the 1-based **re**-dispatch count for that role on that Issue — `engineer-veq` for the first round, `engineer-veq-r1` for the second, `engineer-veq-r2` for the third, and likewise `doc-writer-veq-r1` for a re-dispatched Doc Writer. This follows the `analyst-<issue-id>-rev<n>` precedent above; the discriminator differs (`-r<n>` vs `-rev<n>`) because the two count different things — review rounds rather than Analyst revisions. Because the discriminator is a **suffix**, every rule that tests these names — most importantly the Reconcile step's Engineer-dispatch precondition — matches on the name **prefix** plus status, so discriminated names are caught alongside undiscriminated ones.
- **Reviewer Agents** (Code Reviewer, Test Reviewer, Doc Reviewer) — Name: `<reviewer>-<issue-id>` (e.g., `code-reviewer-veq`, `test-reviewer-veq`, `doc-reviewer-veq`). The **Code Reviewer** is dispatched in **Phase A** of Section 4's Reconcile step, interleaved with the Engineer; the **Test Reviewer** and **Doc Reviewer** are dispatched in **Phase C** (Section 5). All three take their dispatch shape from Section 5. The same `-r<n>` round discriminator applies to repeat dispatches (`code-reviewer-veq-r1` for the second Phase A review round, and so on), with `<n>` the 1-based re-dispatch count for that reviewer on that Issue.
- **PM Agents** (dispatched per Issue in Section 5 alongside the reviewers) — Name: `pm-<issue-id>` (e.g., `pm-veq`).
- **Aborted-writer redelivery markers** — **Issue scope** (or **post-completion scope** in Section 8). Name: `aborted-<role>-<issue-id>` (e.g., `aborted-test-writer-veq`, `aborted-doc-writer-veq`), and `aborted-<role>-postcomp-<n>` for a Section 8 post-completion lane — where `<n>` is **the same finding index as the lane it marks**, so the marker reads back to its finding. Created by Section 4's Reconcile-step **movement-report rung** when a Test Writer or Doc Writer stops mid-run on detected source movement: the writer's own task is marked `completed` (its Agent has exited) and this task is created `pending` in its place, with the writer's "how far I got" report as its `metadata.activity` string. **This is not an Agent task** — no Agent is behind it, so the "exactly one TaskList task per Agent" rule and the `-r<n>` round discriminator do not apply to it; a lane that aborts a second time refreshes this task's `metadata.activity` rather than opening another. It is an **obligation marker**, the same pattern `defer-*` and `gate-*` use: while it is `pending`, **Phase C must not begin** for this Issue. Marked `completed` when the re-dispatched lane returns a normal deliverable — that lane is `<role>-<issue-id>-r<n>` for an Issue-scoped marker, and `<role>-postcomp-<n>-r<k>` for a post-completion one, per the round-discriminator carve-out Section 8 step 6 states for post-completion names. The `aborted-` prefix is a distinct name class from `<role>-<issue-id>`, which is what keeps these markers out of the Reconcile step's Engineer-dispatch precondition without needing an exemption clause there.
- **URL-resolution Skill-tool dispatches** (per Section 1's URL-resolution sub-step) — Name: `file-from-url-<n>`, where `<n>` is the 1-based index of the URL token in the user-supplied positional-argument list (e.g., `file-from-url-1`, `file-from-url-2` for two URL tokens). The 1-based positional index is what makes the entry deterministic and unambiguous — not the URL itself, which may be long, may repeat after dedupe, or may contain reserved characters that would collide with the naming convention. Each entry is created `pending` when the orchestrator decides to dispatch `/quo-file-issue` for the corresponding URL token, set `in_progress` the moment the Skill-tool dispatch lands, and set `completed` when the resolved `issue_ticket_id` is captured from the structured return (whether the underlying `action` is `created` for a freshly-filed Issue or `reused-existing` on the dedupe `Use existing` path). The URL-resolution sub-step's soft-fail / user-cancel path also closes out the entry — mark the failed entry `completed` (with the failure reason recorded via `metadata.activity` per the per-Agent activity convention above if useful) and clear it from the active set so the cumulative failure check at the upfront `bees show-ticket --ids` validation pass operates on a clean active set.
- **Deferral-ledger tasks** — **Run scope**. Name: `defer-<short-suffix>` (e.g., `defer-1`, `defer-2`, or any collision-resistant suffix). Created when an agent's structured return (per `agents/pm.md`'s Final report contract or `agents/analyst.md`'s `### Deferred refinements` block) names a destination the orchestrator chose not to address inline this Issue — `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue`. `metadata.activity` carries the deferral's one-line description so the gate prose (Section 7.5 below) can surface the active set. Marked `completed` the moment the deferral is encoded in a durable carrier — an updated ticket body, a new Issue, or an explicit in-session resolution (in which case `metadata.activity` logs the resolution path). The pre-handoff Section 7.5 gate reads this ledger for active `defer-*` entries and refuses to yield control while any remain pending or in-progress. The existing post-completion-scoped names (`<role>-postcomp-<n>` / `file-issue-postcomp-<n>` per Section 8 step 6) and the deferral-ledger names coexist without overlap — they track different lifecycles (Agent dispatch vs. carrier-encoding reconciliation).
- **Gate-task tasks** — **Turn scope**. Name: `gate-<kind>-<short-suffix>` (today the dominant `<kind>` is `askuserquestion`, e.g. `gate-askuserquestion-veq` for the Section 3 Analyst-proposal user-approval gate on Issue `b.veq`, or `gate-askuserquestion-1` for any other `AskUserQuestion` gate this run fires). Created by the orchestrator via `TaskCreate` immediately before firing the prescribed tool call (typically `AskUserQuestion`), per the two-step contract. The `<short-suffix>` MUST be unique per fire within the same run across every `gate-*` task regardless of `<kind>` — use one of the two acceptable patterns (monotonic integers or gate-specific slugs encoding context; the Issue-ID-suffixed slugs used by this skill in batch mode like `gate-askuserquestion-veq` are the gate-specific-slug pattern). The two-step contract applies at every gate this skill fires — both the trailer-driven gates surfaced by the review skills (Section 5's review-loop's escalation gates when the orchestrator escalates a contested finding to the user) and the trailer-less orchestrator-driven gates (Section 1's conditional session-effort gate — fires only when the session is below the floor, see Section 1's `Check session reasoning effort` sub-step — Section 3's Analyst-proposal user-approval gate, Section 4's Reconcile-step **unexplained-movement gate** in the movement-report rung, Section 7.5's deferral-hygiene gate, Section 8's post-completion findings gate). `metadata.activity` carries the gate's finite choices verbatim where applicable. Marked `completed` the moment the prescribed tool call returns and its result has been consumed (the user's answer routed, the next branch entered, etc.). Normally enters and exits within a single turn — the lifecycle is shorter than `defer-*` (which spans the whole run). The **yield-control discipline** mirrors `defer-*`: this skill MUST NOT yield control to the harness while any `gate-*` task is in `pending` or `in_progress` status. If a `gate-*` task is somehow left active when the orchestrator would yield (e.g., a bug fired the prescribed tool call without the paired `TaskCreate`, or the orchestrator hit an error between the two), the next reconciliation tick walks the TaskList, surfaces the active `gate-*` task, and re-fires the prescribed tool call from the recorded `metadata.activity` choices. The `gate-*` namespace coexists without overlap with `defer-*`, `<role>-<issue-id>`, `analyst-<issue-id>`, `pm-<issue-id>`, `code-reviewer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `file-from-url-<n>`, the aborted-writer markers (`aborted-<role>-<issue-id>` / `aborted-<role>-postcomp-<n>`), and the Section 8 post-completion names (`<role>-postcomp-<n>` / `file-issue-postcomp-<n>`) — with or without an `-r<n>` round discriminator.

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

### Orchestrator discipline: routing review findings

This section governs how the orchestrator routes the depth-tagged findings the in-flow review skills emit. Each reviewer finding the review skills surface carries a severity tag (`blocker` / `suggestion` / `nit`) and a depth tag (`trivial-tweak` / `refactor-locally` / `re-architect`) on each fix path it proposes, plus the count of fix paths it surfaced. The orchestrator's job here is to turn the reviewer's **enumerated fix paths and their depth tags** into exactly one routing decision — **deterministically for whether a gate fires**, and **by its own judgment for which path it picks when no gate fires**. It does NOT re-classify the reviewer's depth tags: the depth of a path is the reviewer's call, read as emitted, and is the one classification the orchestrator must never invent.

**(a) Pick the path, then route on it.** Routing is a two-step procedure — Step 1 is the orchestrator's own judgment; Step 2 is deterministic given the path Step 1 chose.

**Step 1 — pick.** Choose the highest-quality fix path among those the reviewer enumerated (definition below). The reviewer's `[preferred]` token is an **input** to this choice, not a verdict: prefer it when it is also the most complete; when `[preferred]` marks a narrowing and a fuller path exists that is still the smallest internally-consistent complete change, take the fuller path. **The pick is always one of the paths the reviewer enumerated.** When *no* enumerated path is the smallest internally-consistent complete change — every one of them leaves the stated defect partly unfixed — pick the most complete of them anyway. Step 2 then routes it: rows 2, 3 and 4 all send it to gate (c), where `Fix properly now` dispatches the complete fix; the exception is a finding whose depth tag is absent or malformed, which row 1 sends to gate (d) instead, and that gate has no `Fix properly now` — the user picks among the paths as emitted. Either way the incomplete menu becomes visible **in session**: a gate fires where it otherwise would not have, and the user sees the menu it fired on. A **durable** record reaches the post-completion review only when the user defers or accepts — Trigger A on `Defer to follow-up Issue`, Trigger B on `Accept the limitation` — while `Fix properly now` writes none, so an incomplete menu resolved that way leaves no trace past the run. That is the limit of what this routing does with an under-enumerated finding; the orchestrator does not absorb the gap by writing a path of its own.

**Step 2 — route on the path chosen in Step 1.** Evaluate these conditions **in order**, taking the first that matches, so each finding yields exactly one routing decision:

```
| # | Condition (evaluated in order, first match wins)                      | Routing                            |
|---|----------------------------------------------------------------------|------------------------------------|
| 1 | The finding carries no depth tag, or a malformed severity/depth tag  | Treat as `re-architect` → gate (d) |
| 2 | The chosen path carries the reviewer's `[introduces-mechanism]` tag, | Scope-bounding gate (c)            |
|   | or introduces a mechanism by the orchestrator's own reading (below)  |                                    |
| 3 | The chosen path moves a published contract surface beyond what this  | Scope-bounding gate (c)            |
|   | unit's ticket states, or is breaking for existing consumers          |                                    |
| 4 | The chosen path is narrower than the smallest internally-consistent  | Scope-bounding gate (c)            |
|   | complete fix — it leaves the stated defect partly unfixed            |                                    |
| 5 | The chosen path's depth tag is `re-architect`                        | Routing-decision gate (d)          |
| 6 | Otherwise                                                            | Dispatch the chosen path, no gate  |
```

Row 6 dispatches a fresh ephemeral implementer Agent (Engineer / Test Writer / Doc Writer as the finding's lane dictates) per Section 4's dispatch shape with the chosen fix path, no user gate, and appends a tracker entry per Section 7.5's **Trigger C**. The evaluation order is load-bearing: rows 2–4 precede row 5 so a mechanism-introducing or scope-moving path reaches gate (c) **regardless of its depth tag**, and row 1 comes first so parts (e) and (f) stay reachable unchanged. Whatever row fires, **when the chosen path changes source the re-dispatch follows part (g)'s ordering** — Engineer, then the code review for that site, then the affected writer.

**What "highest-quality" means.** The **smallest change under which the code compiles, the tests pass, and every surface agrees with the invariant this unit's ticket names** — internal consistency across surfaces, not merely local correctness. Total-system complexity counts *against* a path. Effort is never the tiebreaker between paths of equal completeness. "Adds a mechanism" is a reason to route to gate (c), not a reason to build. For a docs- or prose-only change set, "compiles and the tests pass" degenerates to "every surface that states the invariant states it consistently".

**What "introduces a mechanism" means.** The path adds machinery per the mechanism definition in `agents/analyst.md` that **the approved design for this unit did not enumerate** — here, the `## Authoritative design directive` block carried from Section 3's Analyst gate. **The reviewer's `[introduces-mechanism]` tag on a fix path is the primary signal for row 2** — a tagged path routes to gate (c) with no further judgment. Orchestrator-side detection is the **fallback**, used only when no tag is present: read the fix path's own description against that definition and route it the same way.

**(b) ANTI-PATTERN — do not write this:** The orchestrator MUST NOT inline scope-bounding directives into the dispatch prompt of a re-dispatched implementer Agent (R2/R3 rounds). The following phrasings, and any close paraphrase, are forbidden inside a dispatch prompt: `"out of scope for this issue"`, `"out of scope for <id>"`, `"prefer option (a)"` / `"prefer (a)"`, `"Do NOT add X — out of scope"`. Inlining a scope-bound silently narrows the fix without the user ever seeing the decision. When the orchestrator would otherwise scope-bound a finding, it MUST surface that decision through the scope-bounding gate in part (c) instead of writing it into the dispatch prompt.

**The prohibition targets *narrowing* language, not path selection.** Under part (a) the orchestrator's job **is** to pick a fix path and dispatch it, so a dispatch prompt that names the path chosen per part (a) and carries that path's fix **in full** is not a violation of this part. Instructing the implementer to do *less* than the chosen path is — and a path that is itself narrower than the smallest internally-consistent complete fix does not get written into a prompt at all: it routes to gate (c) via row 4.

**(c) Scope-bounding gate.** This gate has **four** entry conditions: when the orchestrator would otherwise scope-bound a finding (the behavior that REPLACES the forbidden directives in part (b)), and rows 2, 3, and 4 of part (a) — the chosen path introduces a mechanism, moves a published contract surface beyond what this unit's ticket states or breaks existing consumers, or is narrower than the smallest internally-consistent complete fix. **Downstream, the part-(b) scope-bound condition is read as row 4** — it is the same condition stated twice (the orchestrator was about to dispatch something narrower than the smallest internally-consistent complete fix), so every rule below that enumerates "row 2, 3, or 4" covers it without naming it separately. On any of the four, it fires an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract with the finite choices below — the severity paragraph that follows establishes which of them the finding's severity makes available:

**Severity rules the choice set — a `blocker` can never be accepted, and can be deferred only with a narrowing.** When the finding reaching this gate carries the `blocker` severity tag:

- **`Accept the limitation` is unreachable, unconditionally** — do not offer it, do not mark it Recommended, and do not route to it by any other path. Accepting a blocker ships the blocker.
- **The base pair is always offered.** Whatever else is available, a `blocker` gets `Fix properly now` and `Re-dispatch the Analyst with this finding` — these two are its floor, and when the two Defer conditions below do not **both** hold they are the whole set.

  - **Fix properly now** — as below.
  - **Re-dispatch the Analyst with this finding** — for a `blocker` that shows the **approved design directive itself is wrong** rather than the implementation of it. Reuse Section 3's Revise-branch re-dispatch shape: mark the prior Analyst task `completed`, issue a fresh cold `subagent_type=analyst` dispatch tracked as `analyst-<issue-id>-rev<n>`, and carry the finding **verbatim** as the revision context in place of the user's revision feedback. When that Analyst returns, Section 3's Approve / Revise / Cancel approval gate re-fires over the new proposal, exactly as on the Revise branch. **On `Approve`, re-enter Section 4 Phase A with the revised directive — but close out this Issue's open TaskList tasks first**: sweep by prefix and mark `completed` every active `test-writer-<issue-id>` / `doc-writer-<issue-id>` / `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` task (and their `-r<n>` rounds), because Section 4's Engineer-dispatch precondition forbids a fresh Engineer while any of them is `pending` or `in_progress`, and this gate can fire from a review phase where several of them are — sweep whichever are actually active, which on a Phase A code-review finding may be none. A lane still **in flight** when that sweep fires is marked `completed` anyway — the orchestrator cannot terminate a dispatched background Agent — with `metadata.activity` recording that it was in flight at the Analyst re-dispatch; when its completion notification arrives, **discard its findings rather than routing them**, because they were raised against the directive this re-dispatch just superseded. **That discard covers every finding raised under the superseded directive, not only the lanes this sweep caught in flight** — the sibling findings the reviewer return that fired this gate co-emitted (they sit in the orchestrator's context on no TaskList task of their own, so no sweep reaches them), and any lane that returned between the gate answer and this sweep (its task is already `completed`, so the every-active-task sweep passes over it). Route none of them; the revised directive is what the next round reviews against. The new Engineer works **against the current working tree**: the edits already landed stay in it, uncommitted, and the revised directive is applied on top of them rather than to a clean base.

- **`Defer to follow-up Issue` is added as a third choice *only when both* of these hold:** (i) the fix path the finding needs **introduces a mechanism** — the reviewer's `[introduces-mechanism]` tag, or the orchestrator's own reading against the mechanism definition in `agents/analyst.md`; **and** (ii) that mechanism serves a case **outside this unit's stated defect**, so the change **narrowed to the stated defect** is still complete and the blocker no longer describes anything that ships. **A narrowing may never reduce coverage of the stated defect.** When the blocker cannot be made inapplicable to what ships without leaving the stated defect partly unfixed, it is **in scope**: it takes one of the base pair, never `Defer`. When both hold, offer it — and **the deferral is paired with the narrowing, never shipped alone**: **file the follow-up Issue first**, carrying the reviewer's sketched design **verbatim**, and dispatch the narrowing (remove or scope down the part of the change that needed the mechanism) only once `/quo-file-issue` has returned an Issue ID — part (f) forbids shipping the narrowing when the filing failed, and Trigger A writes its entry in that same window. **Dispatch that narrowing directly, not by re-entering Step 2 with it** — it is narrower than the complete fix by construction, so Step 2 would match row 4 and route it straight back to this gate. This is the same terminality the `Defer to follow-up Issue` bullet's soft-fix rule states below, for the same reason; the two are one rule, applied to a blocker's narrowing and to a non-blocker's soft fix. That pairing is then the **recommended default** — mark the choice `(Recommended)` even on a blocker, on the same reasoning as the **Recommended default on the mechanism row.** paragraph below. **It applies whichever row fired this gate on a blocker — 2, 3 or 4.** Condition (i) tests the fix path the finding *needs*, not the chosen path, so a blocker's Defer branch can open on a row-3 or row-4 fire as readily as on row 2. (A `suggestion` or `nit` keeps the narrower rule that paragraph states: its Defer default is row-2 only.)

The gate fires for a `blocker` like any other finding — the base pair is a real decision, three choices when the Defer-with-narrowing branch is open. **Neither of the `Defer to follow-up Issue` bullet's closing clauses applies to one:** its no-fix-this-round branch cannot arise, because condition (ii) guarantees a narrowing exists and that narrowing always ships; its never-invent-a-narrowing prohibition is about filling an empty soft-fix slot on a non-blocker, not about the narrowing this branch requires; and neither does its soft-fix identification: what ships on a blocker is the narrowing this branch requires, not the most complete of the enumerated paths that remain. The three choices below are the choice set for `suggestion`- and `nit`-severity findings. Because a `blocker` never reaches the `Accept the limitation` branch, Section 7.5's **Trigger B** is unreachable for `blocker` findings — no tracker entry can record an accepted blocker. **Trigger A is reachable for one**, on the Defer-with-narrowing branch above — and on part (d)'s Defer branch, which fires the same trigger — and its entry must carry the narrowing record that branch's prose requires.

- **Fix properly now** — Re-dispatch the appropriate implementer Agent per Section 4's dispatch shape to address the finding fully, no scope-bound.
- **Defer to follow-up Issue** — File a follow-up Issue via `/quo-file-issue` (inline via the Skill tool, per the precedent in Section 1's URL-resolution sub-step) carrying the finding's description, and proceed with the soft fix this round. **The soft fix is the most complete of the enumerated paths that remain once the deferred one is set aside** — dispatch it **directly**, not by re-entering Step 2 with it: a remaining path is by definition narrower than the one just deferred, so Step 2 would match row 4 and route it straight back to this gate. Or, when the deferred path was the only one enumerated, with no fix for this finding this round (the same end state as `Accept the limitation`, with the follow-up Issue filed). Never invent a narrowing to fill the slot; part (b) forbids it.
- **Accept the limitation** — Record the limitation as an accepted compromise and proceed. (Recorded by the session-scoped compromise tracker — see the `#### Session-scoped compromise tracker` block in Section 7.5.)

The question text includes the finding verbatim plus a one-line context line stating why the gate is firing (which of the four entry conditions above brought it here). **There is no `Cancel` option at this gate** — scope-bounding is a per-finding decision and a `Cancel` here would be ambiguous; the user retains `Ctrl-C` for run-level abort.

**Recommended default on the mechanism row.** When this gate fires because the chosen path **introduces a mechanism** (row 2) serving a case this unit's ticket never mentions, `Defer to follow-up Issue` is the **recommended default** — mark that choice `(Recommended)`. This holds **at every severity**, with one qualification on a `blocker`: on a `suggestion` or `nit` the deferral ships the soft fix, and on a `blocker` it ships the narrowing the severity rule above requires — but only where that rule's Defer-with-narrowing branch is open at all. When its coverage guard withholds `Defer` (narrowing the change would leave the stated defect partly unfixed), there is no choice to mark, even on a row-2 fire. A mechanism the ticket never asked for has its own lifecycle to design, and building it inside this unit is what turns one finding into several rounds. The follow-up Issue MUST carry the reviewer's sketched design **verbatim**, so nothing about the proposed mechanism is lost by deferring it.

**(d) Routing-decision gate.** When part (a)'s Step 2 routes a finding here (row 1 or row 5 — a finding whose depth is unknown or malformed, or whose chosen path is `re-architect`), fire an `AskUserQuestion` via the two-step `TaskCreate` → `AskUserQuestion` contract whose choices are:

**Severity rules the choice set here too — a `blocker`'s Defer route is conditional.** When the finding reaching this gate carries the `blocker` severity tag, the `Defer to follow-up Issue` choice below is **unreachable unless part (c)'s two conditions both hold** — the fix path the finding needs introduces a mechanism, and that mechanism serves a case outside this unit's stated defect, so the change narrowed to the stated defect is still complete. **A narrowing may never reduce coverage of the stated defect**, so a blocker that cannot be made inapplicable to what ships without leaving that defect partly unfixed is in scope here too, and takes one of the choices below rather than `Defer`. When they hold, offer it under part (c)'s rule and on part (c)'s terms: **paired with the narrowing in the same round**, `(Recommended)`, with the follow-up Issue carrying the reviewer's sketched design verbatim. **That `(Recommended)` takes precedence over the per-path marker**: mark `Defer to follow-up Issue` Recommended and withhold the marker from **every other choice** — each fix-path choice's Step-1 marker, and `Re-dispatch the Analyst with this finding`, which the empty-list case would otherwise mark — so exactly one choice carries it, as at part (c). A zero-path row-1 blocker whose Defer branch is open therefore shows `(Recommended)` on `Defer` alone. When they do not, do not offer it, do not mark it Recommended, and do not route to it by any other path. **When it is offered to a blocker here, the deferral is paired with a narrowing dispatched this round, never shipped alone** — the `Defer to follow-up Issue` bullet's "rather than picking a path now" describes the non-blocker case, where nothing ships against the finding this round. The choice set for a `blocker` that cannot be deferred is then the one-choice-per-fix-path list below — **which may be empty**, since a row-1 finding can arrive with no fix path enumerated at all, and in that case the Analyst re-dispatch is the natural home for it: a blocker with no shape to route is exactly what a fresh design pass is for, so mark that choice `(Recommended)` there — plus **Re-dispatch the Analyst with this finding** (the same choice part (c) defines for a blocker — Section 3's Revise-branch re-dispatch shape, a fresh cold `subagent_type=analyst` dispatch tracked as `analyst-<issue-id>-rev<n>` carrying the finding **verbatim** as the revision context, after which Section 3's approval gate re-fires), plus **Cancel**. Together with part (c)'s severity rule this means **no `blocker` reaches an Accept branch at either gate, and reaches a Defer branch only paired with a narrowing** — so the tracker's `User picked Accept the limitation` `Decision` value can never describe a `blocker` finding, and its `User picked Defer to follow-up Issue` value describes one only when that entry's `Rationale` carries the narrowing record Trigger A requires.

- **One choice per reviewer-surfaced fix path** — each choice's description includes that path's depth tag (e.g., `re-architect`, `refactor-locally`). **The `(Recommended)` marker goes on the path the orchestrator chose at part (a) Step 1** — this gate asks the user to ratify or override a pick that has already been made, so the marker must name that pick. The reviewer's `[preferred]` token is an **input** to Step 1 and usually coincides with the pick; when it does not — the shape Step 1 exists for, where `[preferred]` marks a narrowing and a fuller path is the smallest internally-consistent complete change — mark the **fuller** path Recommended, not the `[preferred]` one, and say in that choice's description that the reviewer preferred the other path so the user can see the divergence. **Fallback:** on a row-1 entry (no depth tag, or a malformed one) no Step-1 pick was possible, so no path is marked Recommended.
- **Defer to follow-up Issue** — File a follow-up Issue via `/quo-file-issue` (inline via the Skill tool) carrying the finding's description, rather than picking a path now.
- **Cancel** — Ends work on the current Issue without a fix landing. Route through `#### Aborted-Issue close-out` (Section 7), which sweeps this Issue's TaskList tasks by prefix, runs Section 7.5's deferral-hygiene gate, runs the Issue-boundary state-externalization checkpoint on its aborted path, then reads the working tree and branches on mode. `Cancel` does **not** decide the run's fate from here — the close-out's mode branch does, and in batch mode with Issues still remaining that branch **stops the run** rather than advancing, because this Issue's edits are left uncommitted. `Ctrl-C` remains the unconditional run-level abort.

The question text includes the finding verbatim.

**(e) Backwards-compatibility shim.** A finding emitted **without a depth tag** — a legacy reviewer emission during rollout, or a hand-authored finding from a future call site — MUST be treated by the routing table as if it carried `re-architect` depth, i.e., it routes to the user gate in part (d). The shim errs toward user input when uncertain: when the orchestrator cannot determine a finding's depth, it surfaces the decision to the user rather than dispatching its own pick ungated under row 6.

**(f) Edge-case handling.**

- **Malformed tags.** When a severity tag is not exactly `blocker` / `suggestion` / `nit`, or a depth tag is not exactly `trivial-tweak` / `refactor-locally` / `re-architect`, the orchestrator treats the finding as `re-architect` depth (per the shim in part (e)) AND surfaces the parse failure to the user so the reviewer emission can be corrected.
- **Routing ambiguity.** If the routing table somehow returns more than one decision (impossible by construction), default to the user gate in part (d) and surface the ambiguity to the user.
- **`/quo-file-issue` failure at the Defer gate.** When the user picks `Defer to follow-up Issue` (at either the scope-bounding gate in part (c) or the routing-decision gate in part (d)) but the inline `/quo-file-issue` dispatch fails or the user cancels at one of its gates, the orchestrator MUST NOT silently ship the soft fix (or no fix). Instead it surfaces the failure to the user and re-prompts with the same gate's choices, so the user can re-attempt the defer, pick `Accept the limitation` where that choice exists (non-`blocker` findings only — per the severity rules in parts (c) and (d), `Accept the limitation` is never offered on a `blocker`) / a specific fix path explicitly, or (at the routing gate) Cancel. **A `blocker` can reach this bullet**, via the Defer-with-narrowing branch, and on one the failed filing is load-bearing: **do not ship the narrowing when the filing failed** — the narrowing is only legitimate paired with the follow-up Issue that carries the deferred design, so re-prompt with the same gate's choices and let the user re-attempt the filing or pick a non-deferring choice.

**(g) Re-dispatch ordering when a fix path changes source.** Once a finding's routing is settled (**the orchestrator's own path pick per part (a), or the user's pick at the gate in part (c) or (d)**), the orchestrator still has to decide *how many lanes to dispatch at once*. When the chosen fix path requires a **source change**, the Engineer re-dispatch and the affected writer re-dispatch are **ordered, not concurrent**: dispatch the **Engineer** first, then the **Code Reviewer** against the resulting diff, and only once that code review has closed dispatch the **Test Writer** and/or **Doc Writer** whose input the source change invalidated. Dispatching the Engineer and a writer in the same round hands the writer a diff that the pending code review is about to rewrite, which is what forces the writer's work to be redone.

The precondition that makes this checkable rather than remembered is the **Engineer-dispatch precondition** in Section 4's Reconcile step: **the orchestrator MUST NOT dispatch an Engineer Agent for this Issue while any TaskList task whose name begins with `test-writer-<issue-id>`, `doc-writer-<issue-id>`, `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, or `pm-<issue-id>` is `pending` or `in_progress`.** Walk the TaskList before every Engineer dispatch — including every re-dispatch routed from this section — and confirm no task matching those prefixes is active. That section is authoritative for the three qualifications this one does not restate: the **prefix**-match rule (so round-discriminated names like `engineer-<issue-id>-r<n>` are still caught), the Code Reviewer's deliberate exclusion from the list, and what to do when the blocking task is `pending` with no Agent behind it.

A finding whose chosen fix path changes **no source file** — a test-quality nit, a doc-wording gap — carries no ordering constraint: re-dispatch that single writer lane on its own, no Engineer round, no code review.

**Two-step gate mechanics (parts (c) and (d)).** Both gates above fire through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (per each file's Section 4 / Section 3 TaskList naming convention's gate-task entry, with a distinct per-fire `<short-suffix>` so concurrent or repeated fires do not collide), **then** call `AskUserQuestion` with the finite choices above in the same turn. Do not produce a text response describing the gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. These gates are multi-choice only — do not add fake free-text options that duplicate `AskUserQuestion`'s auto-appended `Type something.` / `Chat about this` slot.

These new gates inherit a prose-adherence fragility — that is an execution-time risk acknowledged at run time, not something this section fixes.

### 5. Review Loop

This section is **Phase C** of the Reconcile step's phase ladder (Section 4). It runs when the Phase B writers have returned **and no `aborted-*` TaskList task for this Issue is `pending`** — the same two-conjunct trigger Section 4's Phase C bullet states, restated here so this section's own entry condition is complete; match on the `aborted-` name prefix plus the status. The **Code Reviewer is not dispatched here** — it is dispatched in **Phase A**, alone, interleaved with the Engineer until the source is clean; this section carries the Code Reviewer's dispatch shape and TaskList name for Phase A to use, but not its trigger. **Phase A also borrows this section's feedback-consumption discipline in full**, not only the dispatch shape: the "**Follow the trailer literally**" bullet below is the only prose in this skill on how to consume a review skill's output, and the ignored-feedback rule beneath it (record each ignored item as a `defer-<short-suffix>` TaskList task, with a destination annotation, at the moment of the ignore decision) is one of the three ways Phase A is allowed to close with findings outstanding. Read both as applying to the Code Reviewer's Phase A returns exactly as they apply to the Phase C returns dispatched here.

Dispatch three concurrent ephemeral Agents per Section 4's dispatch shape — two reviewer roles plus the Product Manager: `Agent(subagent_type="test-reviewer", run_in_background=true)`, `Agent(subagent_type="doc-reviewer", run_in_background=true)`, `Agent(subagent_type="pm", run_in_background=true)`. Track each via a TaskList task per Section 4's issue-scoped naming convention: `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`. The Phase A Code Reviewer dispatch uses the same shape — `Agent(subagent_type="code-reviewer", run_in_background=true)`, tracked as `code-reviewer-<issue-id>`.

Conditional spawn — only dispatch a reviewer whose corresponding implementer was used during this issue's implementation pass:
- If the Test Writer Agent ran in Phase B, dispatch the test-reviewer Agent now.
- If the Doc Writer Agent ran in Phase B, dispatch the doc-reviewer Agent now.
- The Code Reviewer's own conditional spawn lives in Phase A: if the Engineer Agent ran, the Code Reviewer runs against its diff there, before Phase B begins.

Corollary: a doc-only fix dispatches only the doc-reviewer here (and no Code Reviewer at all, since Phase A was empty); a code+test fix without a Doc Writer pass dispatches the Code Reviewer in Phase A and only the test-reviewer here.

**PM is the exception to the conditional-spawn rules.** The Product Manager Agent is **always dispatched** per Issue regardless of which implementers ran — spec-alignment review is meaningful on any diff. The PM dispatches alongside the reviewers, not instead of any of them. This matches the always-dispatched pattern Doc Writer uses in Section 4 — the orchestrator does not pre-judge whether spec-drift risk is present; the PM Agent reads the spec sources, makes the substance-based judgement itself, and short-circuits in `agents/pm.md` when there is no spec drift surface to review.

The PM's dispatch prompt must include the Issue ID, the Issue body verbatim, the Issue's `up_dependencies` array, `<scoped-marker-resolver-path>` — a placeholder the orchestrator fills in at runtime so `agents/pm.md` can perform its Scoped-marker check (see "Scoped-marker PM dispatch wiring" in Section 4) — and `<compromise-tracker-path>`, this run's compromise-tracker path (the same value Section 8 passes to the post-completion reviewer). **Pass the tracker path, not its contents**, exactly as Section 8 does; `agents/pm.md` reads the file itself and carries the deferred-blocker check that path enables.

**The Phase C PM dispatch prompt must also relay the Engineer's completeness evidence verbatim.** Same rule as the Phase A Code Reviewer dispatch (see "Code Reviewer dispatch — relay the Engineer's completeness evidence verbatim" in Section 4), applied again here because the PM is a **second** `/quo-engineer-review` caller on this Issue: `agents/pm.md` drives that skill in flight via the `Skill` tool, and its PM-side bullet requires it to pass a completeness list through into the invocation — a list it can only pass on if this dispatch prompt gave it one. Relaying to the Phase A Code Reviewer does not cover this: those are different Agents with no channel between them, and the Phase C PM reviews a **wider** diff than the Phase A Code Reviewer ever saw (it includes the Phase B test and doc changes). So **when any Engineer return for this Issue carried a completeness list** (the search patterns run, every hit, and per hit either the change made or the reason it is deliberately untouched), embed it **verbatim** in the PM dispatch prompt under a clearly labelled heading — the recommended label is `## Engineer's completeness evidence`. Embed it as text in the prompt, the same way the Issue body is embedded; do **not** write it to a scratch file and pass a path. Attribute each list to its Phase A round when more than one Engineer round produced one. **Separately from the list, state in the prompt that the assignment was sweep-shaped whenever it was** — that is a fact about the assignment that was dispatched (a directive or Subtask body that directed a change at *every site* where some property holds), known independently of whether a list came back. `/quo-engineer-review`'s sweep-verification check only reports a *missing* list as a finding when the invocation itself named the assignment that way, so an unnamed sweep silently loses the check — and the case that most needs the check is precisely a sweep-shaped assignment whose Engineer returned no list. When no completeness list arrived, omit the `## Engineer's completeness evidence` heading rather than emitting an empty one — but still state that the assignment was sweep-shaped when it was, so `/quo-engineer-review`'s missing-list check stays reachable.

The reconciliation-loop tick defined in Section 4 covers Agent completion notification — there is no idle teammate to escalate to. The orchestrator yields after dispatching the reviewer Agents and the PM Agent, and the harness fires the next tick on the `run_in_background=true` substrate's completion notification.

Role contracts (responsibilities, model assignment, gating, instructions) live in the role files; the orchestrator's job is to dispatch, not to carry the role's prose.

- **Code Reviewer** (`agents/code-reviewer.md`) — reviews the Engineer's output and surfaces gaps against engineering standards. Dispatched in **Phase A** (not here), alone, looping with the Engineer until the source is clean.
- **Test Reviewer** (`agents/test-reviewer.md`) — reviews the Test Writer's output and surfaces gaps against test-quality standards.
- **Doc Reviewer** (`agents/doc-reviewer.md`) — reviews the Doc Writer's output and surfaces gaps against documentation standards.
- **Product Manager** (`agents/pm.md`) — reviews the fix against the spec source (the Issue body, plus PRD/SDD-equivalent paths from CLAUDE.md `## Documentation Locations`, optionally Scoped-marker-narrowed via a Plan Bee in `up_dependencies`), flags scope creep or spec divergence. Issues filed by `/quo-file-issue` in the default in-conversation capture mode do not carry `reference_materials` — the body itself is the spec. Issues filed via any of `/quo-file-issue`'s URL entry surfaces — bare URL (`/quo-file-issue <url>`), the flag forms (`/quo-file-issue --reference <url>` / `--from-github <url>`), or this skill's URL-resolution sub-step's inline-Skill-tool dispatch — carry a `reference_materials` entry whose `value` is an external URL and whose `resolver` is one of `github-issue`, `linear-issue`, or `url`; on this path the PM fetches the upstream content via `WebFetch` and treats it as the spec source (the Issue body is intentionally thin in this mode). When the PM transitively consults a Plan Bee reached through the Issue's `up_dependencies`, that Plan Bee's `reference_materials` may resolve via the `file-path` resolver (path on disk — Scoped-marker narrowing applies) or the `bees` resolver (Spec Bee ID, in which case the PM walks the Spec Bee's `t1=Doc` children for PRD and SDD content). `agents/pm.md` is the authoritative spec for all three resolver-driven paths (`file-path`, `bees`, and the external-URL resolvers like `github-issue` / `linear-issue` / `url`); the body-as-spec path is the fallback when `reference_materials` is null/empty. The PM self-short-circuits in `agents/pm.md` when the collective spec sources carry no substantive content — see that role file for the content-based short-circuit rule. Model: Opus (always).

- Get the feedback, and make a judgement call about whether that work must be done. Each of the three review skills above (`/quo-engineer-review`, `/quo-test-writer-review`, `/quo-doc-writer-review`) emits a second-person imperative routing trailer (`**Your next tool use MUST address these findings now.**` / `**Your next tool use MUST advance the workflow.**`) plus a counter-anchor clause at the bottom of its output, naming the precise routing this step must take after consuming the findings. **Follow the trailer literally** — it is the authoritative routing prescription; the prose below is reference context, not a load-bearing rule the orchestrator must recall from memory.
  - If feedback requires action, dispatch fresh ephemeral implementer Agents per Section 4's dispatch shape (Engineer / Test Writer / Doc Writer as needed) and/or re-dispatch the PM Agent per this section's dispatch shape if spec-alignment review needs another pass against the updated diff. **These re-dispatches are ordered, not concurrent, whenever a fix path changes source** — see part (g) of `### Orchestrator discipline: routing review findings` for the ordering rule, and the Reconcile step's re-entry bullet in Section 4 for how a source-changing finding re-enters Phase A.
    - **IMPORTANT** Stay in delegate mode and do not do the work yourself.
    - If the feedback was minor enough, you may choose to **NOT** re-dispatch the Product Manager on this iteration
  - If not, move on but you MUST include the ignored feedback in the summary
  - Note: This could create an infinite loop so you may ignore feedback so long as you present it in the summary
  - **Record each ignored item as a `defer-N` TaskList task at the moment of the ignore decision.** Whenever the Director chooses to ignore reviewer or PM feedback rather than re-dispatch implementers to address it, create a `defer-<short-suffix>` TaskList task (named per Section 4's "TaskList naming convention") with the feedback's one-line description as the `metadata.activity` string, status `pending`. The PM Agent's Final report contract (`agents/pm.md`) requires the PM to annotate each deferred item with a destination — `addressed-now-in-this-Task` (read here as "addressed-now-in-this-Issue" per the generic-naming note in `agents/pm.md`), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — that the orchestrator records in the same `metadata.activity` string. **For reviewer-feedback items (code/test/doc-reviewer findings the Director chose to ignore), the Director MUST annotate the `metadata.activity` with one of the three destination labels from the PM Agent's destination vocabulary — `addressed-now-in-this-Task` (read as "addressed-now-in-this-Issue"), `defer-to-existing-ticket-body: <ticket-id>`, or `defer-to-new-Issue` — when creating the `defer-*` task.** The destination is the Director's judgement call captured at ignore time, but the annotation itself is required, not optional; matching the PM Agent's contract here keeps Section 7.5's deferral-hygiene gate able to route reviewer-feedback and PM-feedback items through the same Fix / File / Encode branches uniformly. Vague framings without a named destination (e.g., "defer to later") are forbidden by the same anti-pattern rule that applies to the PM Agent's annotations. This upstream record-creating step is the load-bearing source for Section 7.5's deferral-hygiene gate; without it, the gate would fire empty even when items were ignored at this site, defeating the gate's purpose.

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
   3. Stage files related to this issue's actual code, test, and doc changes — agent-reported files plus formatting changes to files that were touched by this issue's agents — plus (only if the Issues hive lives inside this repo) the per-issue directory under the resolved Issues hive path, so the issue's `open → done` status flip and any body updates the orchestrator made via `bees update-ticket` land in the same per-issue commit as the fix itself. The Issues-hive scoping mirrors `quo-execute`'s Plans-hive scoping (see `quo-execute`'s After-Task commit step). To learn the in-repo Issues hive path, run the bundled helper's NON-MUTATING `resolve-hive-paths` mode (the same `hive_commit.py` helper this skill calls at its Section 7.5 Encode step — resolve its sibling path the same way). The helper emits the Issues hive's absolute path when it lives inside this repo, or nothing when it lives outside (in which case you stage no hive path here). Run it as a single literal Bash call:

      ```bash
      # POSIX (bash / zsh):
      python3 "<this skill's base directory>/../quo-execute/scripts/hive_commit.py" resolve-hive-paths --hive issues
      ```

      ```powershell
      # Windows (PowerShell):
      python "<this skill's base directory>\..\quo-execute\scripts\hive_commit.py" resolve-hive-paths --hive issues
      ```

      When the helper emits an Issues hive path, append `/<issue-id>` to it and `git add` that per-issue directory (e.g., `git add <emitted-issues-path>/<issue-id>`) alongside your judgement-selected source files. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree. Review each modified file and only stage it if it's plausibly related to this issue. The per-issue scoping `<issue-id>` on the `git add` path also keeps drift in *other* issues' on-disk records out of this commit; if other issues have stale working-tree state, that gets caught by the next `/quo-fix-issue` run on those issues, not swept in here.
   4. Commit with a descriptive message per system/project git guidance. The commit's subject line MUST follow the literal format `Fix issue: <title> (<issue-id>)` (e.g., `Fix issue: Tighten dispatch contract gap (b.abc)`) — Section 9's post-hoc SHA-derivation fallback `--grep`-filters the session log against the literal `(<issue-id>)` token in this subject, so the parenthesized-ID suffix is a load-bearing contract, not a stylistic preference.
3. Mark the per-issue TaskList tasks as `completed` and clear them from the active set. All of them are named per Section 4's issue-scoped naming convention; group them by the phase that dispatched them:

   - the Section 3 Analyst task `analyst-<issue-id>` (plus any `analyst-<issue-id>-rev<n>` revisions), if not already marked `completed` at the end of Section 3;
   - the **Phase A** tasks `engineer-<issue-id>` and `code-reviewer-<issue-id>` — both dispatched from Section 4's Reconcile step, the Code Reviewer using Section 5's dispatch shape;
   - the **Phase B** tasks `test-writer-<issue-id>` and `doc-writer-<issue-id>`;
   - the **Phase C** tasks dispatched in Section 5: `test-reviewer-<issue-id>`, `doc-reviewer-<issue-id>`, `pm-<issue-id>`;
   - any **aborted-writer redelivery markers** the movement-report rung opened for this Issue: `aborted-test-writer-<issue-id>`, `aborted-doc-writer-<issue-id>`. Reaching close-out means the redelivery landed, so mark them `completed` along with everything else — a marker left `pending` past close-out would hold Phase C shut on a subsequent re-entry into this Issue.

   **Close out round-discriminated names too.** Phase A runs N rounds and a Phase C finding can re-dispatch a writer, so the active set will also hold `-r<n>`-suffixed tasks (`engineer-<issue-id>-r1`, `code-reviewer-<issue-id>-r1`, `doc-writer-<issue-id>-r1`, …). Sweep by name **prefix**, not by the exact names listed above, so no round is left behind. There is no Agent shutdown to perform — the per-issue cold dispatches established in Sections 3, 4, and 5 already complete-and-exit when each Agent returns.

   **The aborted path runs this same sweep at its own site.** An Issue that ends without a fix landing never reaches this step — `#### Aborted-Issue close-out` below performs the identical prefix sweep at that boundary. Keep the two in step: a name added to the list above belongs in that step's list too.
4. Output the summary:

```markdown
## Issue [x] of [total] done: [issue-title]

**Issue**: <issue-id>
**Files Changed**: [count] files ([list key filenames if < 5, otherwise just count])
**Reviews**: [Code review: X issues found/None needed | Docs review: Y issues found/None needed]
**Doc Sync**: [Docs verified accurate / Updated <doc path> §X — describe what changed (use the actual path from CLAUDE.md "Documentation Locations", not literal "SDD"/"PRD")]
**Ignored Review Feedback**: [list items that were flagged but not addressed, or "None"]
**Second-order effects**: [the relayed `### Second-order effects` narrative — rendered per the "Second-order effects" logic below]
[**Accepted compromises** — rendered per the "Accepted compromises" logic below, or OMITTED ENTIRELY when the tracker is empty or absent]
```

**Second-order effects (rendered into the summary block above).** This field is the **destination** for the narrative `/quo-engineer-review` emits under its `### Second-order effects` heading on every review — the relay chain that carries it here is `/quo-engineer-review` → the Code Reviewer Agent (`agents/code-reviewer.md` relays the subsection verbatim) and/or the PM Agent (`agents/pm.md` relays it into its Final report) → this field. Without a named destination the narrative reaches the orchestrator and stops there, which is the whole point of asking for it. Render it as follows:

1. **Collect every relayed narrative for this Issue** — from each Phase A Code Reviewer return (one per round) and from the Phase C PM's Final report `### Second-order effects` section. Render the bullets **verbatim**; do not re-summarize, re-rank, or merge them into the `**Reviews**` line.
2. **Attribute each block** when more than one source contributed, using the same labelling shape `agents/pm.md`'s Final report uses — a short scope label (the round, or the relaying role) ahead of that source's bullets — so a reader can tell a Phase A round-2 observation from a PM-relayed one.
3. **De-duplicate exact repeats.** A Phase A observation the PM's own `/quo-engineer-review` invocation surfaced again verbatim is one effect, not two; keep the earliest attribution. Near-duplicates that differ in substance are kept separately.
4. **When every source reported the fixed empty line** (`No second-order effects identified.`), or no review that emits the subsection ran at all (Phase A was empty and the PM made no `/quo-engineer-review` invocation), render the single line `None identified.` — do **not** omit the field. Unlike `**Accepted compromises**`, this field is unconditional: a section that appears only when there was something to say degrades into one nobody can rely on being asked for.

**Accepted compromises (rendered into the summary block above).** The session-scoped compromise tracker (defined in Section 7.5 `#### Session-scoped compromise tracker`) accumulates one entry per accepted compromise across the whole run/batch, so this surface reflects the tracker file's current contents at the moment the summary renders. Render it as follows:

1. **Read the run's tracker file via the `Read` tool** at the path generated once at the start of this run per Section 7.5's path convention — `<tempdir>/.quorum/compromises-YYYYMMDD-HHMM-<short-suffix>.md` (`/tmp/.quorum/...` on POSIX, `%TEMP%\.quorum\...` on Windows). The path is already known from run start, and if it is no longer in view it is recoverable from the run-state manifest's **Compromise tracker** field (Section 1 `#### Write the run-state manifest`); no shell is needed to locate or test it — just `Read` it.
2. **Omit the section entirely when there is nothing to show.** If the `Read` reports the file does not exist (an uncommon state now that an ungated path pick appends an entry whenever the pick was among two or more paths — Trigger C's lone-`trivial-tweak` carve-out is the only ungated route that appends nothing, so expect most runs with a tracked pick to have at least one entry), OR the file exists but contains no `## Compromise <n>` entries, do NOT render the `**Accepted compromises**` line at all — no empty heading, no `N/A`, no "no compromises" placeholder. Treat "file absent" and "file present but empty" identically: omit.
3. **When entries exist, render one bullet per `## Compromise <n>` entry**, surfacing exactly these four user-facing fields from the entry:
   - the **finding** — the entry's `Finding (verbatim)`,
   - the **chosen path** — the entry's `Decision`,
   - the **rationale** — the entry's `Rationale`,
   - the **follow-up Issue ID** — the entry's `Follow-up Issue` (a ticket ID, or `none`).

   Do NOT surface the fifth entry field (`Fix paths surfaced by reviewer`) — this surface shows the path that was chosen, not the full menu of paths the reviewer offered.
4. **Volume (>10 entries).** When the tracker has accumulated more than ~10 entries, surface them ALL in full — do NOT truncate, summarize away, or elide any entry; the tracker exists precisely to preserve this signal. Precede the bullets with a short prologue noting the volume (e.g., "N compromises were accepted during this run:").

This surface only **reads** the tracker — it never writes, appends to, or deletes it (the write side is owned by Section 7.5's append triggers).

5. Continue to Section 7.5 (per-Issue deferral hygiene) first. Once that gate closes, run the **Issue-boundary state-externalization checkpoint** defined immediately below. Then branch on mode:
   - **Single mode** — proceed to Section 8.
   - **Batch mode (`all` or list mode) with the batch exhausted** (no next Issue remains) — proceed to Section 8.
   - **Batch mode with a next Issue still remaining in the batch** — run the **Context-window boundary guard** defined below (it fires ONLY on this one continuing, in-session path), and then, if the guard did not stop the run, proceed to the next issue in the batch (go back to step 2).

#### Issue-boundary state-externalization checkpoint

This is the canonical anchor name; other sections refer to it by name. **It is a definition, not a step in Section 7's linear flow** — do not run it merely because reading reached this heading. Run it only where step 5 above calls for it, or where `#### Aborted-Issue close-out` below calls for it on the aborted path — in both cases always *after* Section 7.5's deferral-hygiene gate has closed: step 1 below confirms the `defer-*` active set is empty, and that set is not drained until that gate runs.

The Issue boundary is where the run is at its most re-derivable: on the fixed path the Issue is marked `done` and its commit is landed; **on the aborted path** (`#### Aborted-Issue close-out` below) the Issue is deliberately left `open` with no commit, and that pair — an `open` ticket and an absent commit — *is* the durable record that this Issue was not fixed. Either way every fact the next Issue needs is already carried by something on disk rather than by the conversation. The checkpoint's job is to **verify that invariant and refresh the durable carriers**, so that whenever the harness compacts the conversation — at this boundary or partway through the next Issue — the run can be re-derived instead of reconstructed from memory.

Most of the invariant is already structurally enforced here: Section 7.5 hard-stops the run at every Issue boundary until the `defer-*` ledger is empty, so by the time this checkpoint runs, the deferral carrier is closed by construction. What is left is a short verification pass plus the manifest write.

The durable carriers are:

- **the Issue's bees ticket** — flipped `open` → `done` at step 1 above. Re-readable via `bees show-ticket`.
- **the per-issue git commit** — one commit per Issue per step 2 above, with the `(<issue-id>)` token in its subject. Re-readable via `git log` / `git diff`.
- **the session-scoped compromise tracker** — the on-disk file defined in Section 7.5 `#### Session-scoped compromise tracker`. Re-readable via the `Read` tool.
- **the `defer-*` TaskList ledger** — emptied by Section 7.5's hard-stop gate before this checkpoint runs. Re-readable by walking the TaskList.
- **the run-state manifest** — the on-disk file defined in Section 1 `#### Write the run-state manifest`, which carries the run-scoped values (the ordered Issue batch, isolation strategy, `<pre-session-sha>`, compromise-tracker path, per-Issue progress) that have no other durable home. Re-readable via the `Read` tool.

At the point step 5 — or `#### Aborted-Issue close-out`'s step 3 — calls for it, and not before, run these three steps, ahead of whatever the invoking site does next (step 5: pick up the next Issue in the batch, or move to Section 8; the aborted close-out: move to Section 8, or stop the run at its step 4). Every step below is a tool call the orchestrator can actually make — run a bees query, run a git command, read a file, walk the TaskList, write a file:

1. **Verify the carriers.** Do all four. (**Aborted-path qualification.** When this checkpoint is invoked from `#### Aborted-Issue close-out` below, the first two verifications invert rather than fail: confirm the Issue reads **`open`**, not `done`, and expect **no** per-issue commit — skip the `(<issue-id>)` subject-token search entirely rather than running it and reporting its empty result as a gap. The tracker and TaskList verifications run unchanged.)
   - Re-read the just-fixed Issue in bees and confirm it reads `done`.
   - Confirm the per-issue commit landed with the `(<issue-id>)` subject token, using the subject-token search rather than a positional lookup: `git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD` (the same `-F --grep` form scoped to the same `<pre-session-sha>..HEAD` window that Section 9 step 4's re-derive path uses; identical literal on POSIX and PowerShell). Resolve `<pre-session-sha>` by `Read`ing the run-state manifest and taking its **Pre-session SHA** field — the same manifest the tracker-path bullet below reads — not from a value quoted earlier in the conversation. **Validate the manifest before trusting that field:** compare its **Unit scope** ordered Issue batch against the batch this run is fixing, and if the batch names Issues this run is not working (the stale/foreign-manifest tell Section 1 `#### Write the run-state manifest` describes — a concurrent run in a same-basename checkout truncated it), treat the manifest as absent and recover per that section: ignore its **Pre-session SHA** and bound this check with `HEAD~N` instead, where `N` is the number of Issues fixed so far in this run (one commit per Issue per step 2 above), then let step 2 below rewrite the manifest from this run's own batch. The range is load-bearing in both directions: **do not use a bare `git log --oneline -1`** — this checkpoint runs *after* Section 7.5, whose Encode branch can land a follow-up `Encode deferral: ...` commit on top of the per-issue commit, so `-1` alone would inspect that follow-up commit, find no `(<issue-id>)` token, and report a gap against a commit that already landed — and **do not drop the `<pre-session-sha>..HEAD` bound** either, because an unscoped `--grep` searches all of history and can match a same-`(<issue-id>)` commit from an earlier run (a re-opened Issue, a reverted fix), reporting "no gap" when this run's commit never landed. An empty result from the ranged `--grep` form is a real gap; a non-empty result is this run's per-issue commit wherever it now sits.
   - `Read` the compromise-tracker file at the path in the manifest's **Compromise tracker** field and confirm every compromise accepted on this Issue has an entry. **A `Read` reporting that the file does not exist is not by itself a gap** — the tracker is not created until its first append trigger fires, and an Issue records nothing when every finding it routed was answered by the user at a gate, or when its only ungated routes hit Trigger C's lone-`trivial-tweak` carve-out. That combination is less common than it once was, so do not read an absent file as the expected state; read it as "nothing was appended", and check that against what this Issue actually did. Only treat it as a gap if a compromise **was accepted**, or an ungated path pick **that Trigger C requires an entry for** was dispatched, on this Issue and no entry (or no file) exists for it. That qualifier is what keeps this check from contradicting the trigger it verifies: a unit whose sole ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less, and reporting it as a gap would tell the orchestrator to append the very entry Trigger C says not to write.
   - Walk the TaskList and confirm every per-issue role task and `gate-*` task is `completed` and the `defer-*` active set is empty.

   Fix any gap **now** rather than carrying it forward in conversation.
2. **Rewrite the run-state manifest** per Section 1 `#### Write the run-state manifest`, recording the just-fixed Issue's ID and commit SHA under progress and the next Issue's ID as the next unit (or `none` in single mode, or when the batch is exhausted). **On the aborted path**, record the Issue as aborted instead — `<issue-id>: aborted — no commit; Issue left open` — and set the next unit by the same batch rule.
3. **Re-read, do not recall, at every dispatch on the next Issue.** Concretely: before each Agent dispatch on the next Issue, `bees show-ticket` that Issue's body and status and `Read` the run-state manifest for the run-scoped values (ordered batch, isolation strategy, tracker path, `<pre-session-sha>`) — rather than reusing a value quoted earlier in the conversation. The next Issue's design directive comes from its own Section 3 Analyst pass, never from the previous Issue's. Carry **no** value forward from the prior Issue: if a fact the next Issue needs is not readable from one of the carriers above, stop and write it into one before dispatching anything.

**What this checkpoint does not do.** It does not clear, compact, or otherwise reclaim the orchestrator's context, and it must never be narrated as if it did. No model-invocable mechanism for self-clearing or self-compacting exists; token reclamation is owned by the harness, which compacts the conversation on its own once the window fills. This checkpoint is what makes any such compaction — whenever it fires, including mid-Issue — lossless.

#### Context-window boundary guard

This guard is a **definition co-located with the Issue-boundary checkpoint above**, not a step in Section 7's linear flow — run it only where step 5 calls for it: on the **one continuing, in-session path** — batch mode (`all` or list) with a next Issue still remaining in the batch — *after* the Issue-boundary state-externalization checkpoint has refreshed the durable carriers (so a fresh session can resume from disk) and *before* control loops back to step 2. It does **NOT** run on any run-ending path: single mode (proceeds to Section 8) and batch mode when the batch is exhausted (also proceeds to Section 8) cross no in-session Issue boundary, so a fresh-session stop recommendation there is noise and a missing-reading gate would fire an `AskUserQuestion` immediately before final review. **`#### Aborted-Issue close-out` below does not invoke it either** — an aborted Issue stops the batch outright at its step 4 rather than continuing, which makes that a run-ending path too. The Issue-boundary checkpoint above is unconditional on every path; this guard deliberately is not — do not inherit its unconditionality. A single-Issue run crosses no boundary and never invokes the guard.

**What the guard reads, and what it does not.** The guard reads an **external gauge file** published by a separate status-line producer process — it does not and cannot measure the orchestrator's own token usage, and it is not self-introspection. When the reading says the window is filling, the only reclamation lever is starting a **fresh session** (per the fresh-session-per-phase recommendation at run close-out); the orchestrator has no model-invocable way to clear or compact its own context, so this guard never instructs that. Its job is narrow: stop the batch at this clean Issue boundary — where the run is fully re-derivable from disk — before the harness's auto-compaction would otherwise fire partway through the next Issue.

**Ordering is load-bearing (mirror Section 1's `#### Check session reasoning effort`).** Read the session id **first**, evaluate it, and only *then* decide whether any gate task is created. Do NOT create a `gate-*` task before the reading is in hand: on the common path no gate fires at all, and a stranded `pending` `gate-*` task violates the yield-control discipline of the two-step contract.

**Step 1 — read the session id.** One literal command:

```bash
# POSIX (bash / zsh):
printenv CLAUDE_CODE_SESSION_ID
```

```powershell
# Windows (PowerShell):
Write-Output $env:CLAUDE_CODE_SESSION_ID
```

**Trim any trailing whitespace or newline** from the value before use — a trailing newline fails the helper's `--session-id` charset validation.

**Step 2 — session id unset or empty → skip the guard silently and continue** to the next Issue (back to Section 2). This is the ONLY silent-skip path (the unsupported-CLI carve-out), matching how Section 1 treats an unset `CLAUDE_EFFORT`. Create no `gate-*` task and emit no output.

**Step 3 — session id present.** Resolve the gauge helper as a sibling of this skill's base directory — `<this skill's base directory>/../quo-setup/scripts/context_gauge.py` (POSIX `/`, PowerShell `\`; the base directory is in the skill invocation header). This is the same sibling-resolution discipline this skill already uses for `scoped_marker_resolver.py` and `hive_commit.py`.

First obtain the stop threshold from the helper's threshold-emitting seam — one literal call that prints the integer on stdout:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" stop-threshold
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" stop-threshold
```

Obtain the threshold from this seam and compare the reading against whatever integer it prints — the helper is the single definition site of the number, so this prose never restates it.

Then read the current reading for this session — one literal call:

```bash
# POSIX (bash / zsh):
python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" read --session-id <trimmed-session-id>
```

```powershell
# Windows (PowerShell):
python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" read --session-id <trimmed-session-id>
```

**Step 4 — branch on the `read` output and its exit status.** `read` prints exactly one of four values (an integer percentage, `no-reading`, `stale`, or `missing`) and exits `0` for all four; it exits non-zero (`2`) on a malformed gauge OR an invalid `--session-id`. The resume command named in every stop branch below is the fresh-session resume: `/quo-fix-issue all` for an `all` run, or `/quo-fix-issue <remaining-ids>` listing the still-unfixed subset (the Issues in this run's batch not yet marked `done`) for a list run.

- **Integer ≥ threshold → STOP** at this boundary. Report the current percentage and recommend resuming in a **fresh session**, naming the exact resume command. Then exit the skill — do not loop back to step 2.
- **Integer < threshold → continue** to the next Issue (back to step 2). No output.
- **`no-reading` → continue** to the next Issue (back to step 2). This is the transient fresh-but-null state — the producer is alive, the number is just not populated yet. No output.
- **`stale` → STOP** at this boundary. The gauge file exists but the producer appears to have stalled; because usage only grows within a session, a stale number biases low and must not be trusted as headroom. Note that the producer appears stalled, and that recurring staleness across fresh sessions means the operator should check their status-line producer. Recommend the fresh-session resume with the resume command. Do NOT let `stale` fall through to continue.
- **Non-zero exit, or empty stdout → the same fail-safe stop-and-ask as `stale`** (an untrustworthy reading). Because `read` exits `2` on a malformed gauge OR an invalid `--session-id`, do NOT assume exit `2` implies a corrupt file. Never fall through to continue.
- **`missing`** — no gauge file exists for this session (usually no producer is configured in this environment). Before stopping, check the persistent opt-out marker at `<tempdir>/.quorum/context-guard-opt-out` (`/tmp/.quorum/context-guard-opt-out` on POSIX, `%TEMP%\.quorum\context-guard-opt-out` on Windows) with one literal existence check:

  ```bash
  # POSIX (bash / zsh):
  test -f /tmp/.quorum/context-guard-opt-out
  ```

  ```powershell
  # Windows (PowerShell):
  Test-Path "$env:TEMP\.quorum\context-guard-opt-out"
  ```

  **If the marker is present → skip the guard silently and continue** to the next Issue (back to step 2). **If absent → hard-stop via the two-step gate in step 5 below.**

**Step 5 — the missing-reading gate (reached only from the `missing`-and-no-marker branch above).** Honor the two-step `TaskCreate` → `AskUserQuestion` contract: **first** `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming this boundary context-guard gate (a distinct `<short-suffix>` per fire, per Section 4's TaskList naming convention's gate-task entry; honor the yield-control discipline — do not yield while it is `pending`/`in_progress`), **then** call `AskUserQuestion` in the same turn. Mark the `gate-*` task `completed` once the answer is consumed. The question text must (a) state that the environment may override the operator's user-level status-line config, so no reading is being published; (b) publish the gauge file contract — its path (`<tempdir>/.quorum/context-usage-<session_id>.json`), the required `session_id` and `context_window.used_percentage` fields, and its overwrite-per-refresh semantics; and (c) state that **Configure now** runs `/quo-setup --configure-gauge-producer` inline. Present these options (multi-choice only — no fake free-text options):

- **Configure now** — invoke `/quo-setup --configure-gauge-producer` inline via the Skill tool (the same inline-Skill precedent Section 1's URL-resolution sub-step uses for `/quo-file-issue`). Because a freshly-configured producer only begins publishing **next** session, after a successful Configure now **recommend resuming in a fresh session** with the resume command rather than implying the current run is now guarded, then exit.
- **Proceed without the guard (this run)** — continue to the next Issue (back to step 2); write no marker.
- **Never guard me (persistent opt-out)** — write the marker via the sibling helper's `write-opt-out` mode (one literal call), then continue to the next Issue (back to step 2):

  ```bash
  # POSIX (bash / zsh):
  python3 "<this skill's base directory>/../quo-setup/scripts/context_gauge.py" write-opt-out
  ```

  ```powershell
  # Windows (PowerShell):
  python "<this skill's base directory>\..\quo-setup\scripts\context_gauge.py" write-opt-out
  ```

- **Stop here** — exit the skill with the fresh-session resume command.

#### Aborted-Issue close-out

This is the canonical anchor name for the path where an Issue ends **without a fix landing**. Three branches route here: Section 4's Reconcile-step unexplained-movement gate's **Abort this Issue** choice, Section 3's Analyst-proposal gate's **Cancel** choice, and the routing-decision gate's **Cancel** choice (part (d) of `### Orchestrator discipline: routing review findings`). Like the two definitions above it, **this is a definition, not a step in Section 7's linear flow** — do not run it merely because reading reached this heading; run it only where one of those branches calls for it by name.

An aborted Issue is still an Issue boundary. Leaving one by simply "moving on" skips every close-out the fixed path runs — the prefix-swept TaskList close-out, the deferral-hygiene gate, and the state-externalization checkpoint — and in batch mode this boundary ends the run rather than advancing to the next Issue (step 4). That is how an `aborted-*` marker (when the entering branch opened one) survives into a later re-entry and holds Phase C shut on an Issue that has nothing wrong with it, how a `defer-*` entry is stranded with no durable carrier, and how the manifest is left naming an Issue this run has already left. Run these four steps in order:

1. **Close out this Issue's TaskList tasks**, exactly the sweep Section 7 step 3 runs on the fixed path: sweep by name **prefix**, not by exact name, and mark `completed` every task scoped to this Issue — the Section 3 `analyst-<issue-id>` task (plus any `-rev<n>` revisions), the Phase A `engineer-<issue-id>` / `code-reviewer-<issue-id>` tasks, the Phase B `test-writer-<issue-id>` / `doc-writer-<issue-id>` tasks, the Phase C `test-reviewer-<issue-id>` / `doc-reviewer-<issue-id>` / `pm-<issue-id>` tasks, every `-r<n>`-discriminated round of any of them, and the `gate-*` task that fired the branch routing here. **Include every `aborted-<role>-<issue-id>` redelivery marker still `pending`, when one is open** — on the Abort-this-Issue branch that marker is precisely why this close-out is being run, while the two `Cancel` branches (Section 3's Analyst gate, part (d)'s routing gate) open none themselves. That does not make the clause vacuous on those branches: a Section 3 `Cancel` re-fired from a Phase A round can land here with a marker another lane already opened, since a Phase A round may run while an `aborted-*` marker is still `pending`. Run the clause on every branch rather than assuming it has nothing to sweep. One left `pending` past the boundary holds Phase C shut on any later re-entry into this Issue. Mark each `completed` with the abort reason recorded in `metadata.activity`: informational context for whoever re-opens the Issue, never a routing input. Throughout, **"clear from the active set" means mark the task `completed`** — never delete it, or the `-r<n>` round count the naming convention derives by counting recorded rounds goes with it.

   **A sibling lane still in flight when this close-out fires.** Whichever branch routed here, a concurrently-dispatched lane may still have a live Agent behind it — on the Abort-this-Issue branch that is the Phase B writer that did not abort (Phase B dispatches the Test Writer and Doc Writer concurrently); on a routing-gate `Cancel` fired at Phase C it is whichever of the two reviewers and the PM have not yet returned; and on a Section 3 `Cancel` **re-fired from part (c)/(d)'s `Re-dispatch the Analyst with this finding` choice** it is whichever Phase A or Phase C lanes were active when that gate fired — typically none on a Phase A finding, since Phase A alternates Engineer and Code Reviewer and the Code Reviewer has returned by the time its finding fires the gate; the reviewers and PM on a Phase C one. The orchestrator cannot terminate a dispatched background Agent. Mark its task `completed` anyway and record in `metadata.activity` that it was in flight at the abort. Its completion notification, when it arrives, is a tick for an Issue this run has already closed out: process nothing for that Issue on it, note that an implementer lane's work may be partially landed in the tree (a review-only lane lands nothing — it returns findings this close-out discards), and continue with whatever unit the run is on.
2. **Run Section 7.5's deferral-hygiene gate** for this Issue. Deferrals recorded before this close-out fires — the bullets consumed from the Analyst's `### Deferred refinements` block, and any reviewer or PM feedback the Director chose to ignore in whichever phases this Issue reached — are exactly as stranded on an aborted Issue as on a fixed one, and this gate is what moves each into a durable carrier. The gate's hard-stop applies unchanged: do not advance past it while any `defer-*` task is `pending` or `in_progress`.
3. **Run the Issue-boundary state-externalization checkpoint** defined above, on its **aborted path** — its step 1 carries the aborted-path qualification for the two verifications that invert (the Issue reads `open`, and no per-issue commit is expected), and its step 2 the aborted **Progress** entry. Everything else runs unchanged: verify the compromise tracker, verify the TaskList is clear, rewrite the manifest, and re-read rather than recall at every dispatch on the next Issue.
4. **Read the working tree, then branch on mode.** This step is where the aborted path **diverges** from Section 7 step 5: an aborted Issue lands no commit, so whatever the phases it reached produced — the Engineer's edits, any Phase B writer's partial work — stays uncommitted in the tree, and the run does **not** carry that tree into another Issue. How much is there depends on the entering branch (a `Cancel` at the **initial** Section 3 gate fires before any implementer ran, so typically nothing — but Section 3 can re-fire from a later phase — Phase A's code review, or Phase C — via part (c)'s and part (d)'s `Re-dispatch the Analyst with this finding` choice, and a `Cancel` there lands on a tree carrying whatever that phase had already landed: a Phase A round's Engineer edits alone, or a full Phase A/B pass), which is why the next paragraph reads the tree rather than asserting what is in it.

   First read what is sitting there, with one literal command, so the messages below can name it:

   ```bash
   # POSIX (bash / zsh):
   git status --porcelain
   ```

   ```powershell
   # Windows (PowerShell):
   git status --porcelain
   ```

   Then branch:

   - **Single-issue mode** — the run ends with this Issue. **Name the aborted Issue and the uncommitted paths** that command reported, so the operator knows what the run left behind. Then proceed to Section 8 over whatever this session *did* land; when the session landed no commit at all, say so plainly and exit rather than dispatching a post-completion sweep over an empty diff.
   - **Batch mode (`all` or list) with the batch exhausted** — name the aborted Issue and the uncommitted paths the same way, then proceed to Section 8.
   - **Batch mode with a next Issue still remaining in the batch — STOP the run here.** Do **NOT** proceed to the next Issue. Nothing committed this Issue's edits, so the next Issue would begin on a dirty tree and inherit them: its Doc Writer would read them as "the Engineer's diff", the fingerprint fallback would sweep them into its Test Writer's `## Source paths to fingerprint` set, and its per-issue commit's "plausibly related" staging could absorb them into an unrelated Issue's commit. Stopping is the same shape the **Context-window boundary guard** uses at this boundary — and because this is a run-ending path, do **not** run that guard here (per its own no-run-ending-path rule). Tell the operator: **which Issue aborted**, the **uncommitted paths** `git status --porcelain` reported, and the **fresh-session resume command** for the still-unfixed subset — `/quo-fix-issue <remaining-ids>` listing the Issues in this run's batch not yet marked `done`, or `/quo-fix-issue all` on an `all` run. Then exit the skill, so the operator resolves the tree before the batch resumes.

### 7.5 Before handoff — deferral hygiene

Every `AskUserQuestion` firing in this gate (Step 2's initial Fix / File / Encode choice, plus any Step 3 re-fires when an earlier routing branch failed to close out a subset of the active `defer-*` set) goes through the two-step `TaskCreate` → `AskUserQuestion` contract — first `TaskCreate` a `gate-askuserquestion-<short-suffix>` TaskList task naming the deferral-hygiene gate (a distinct `<short-suffix>` per fire, so the Step 3 re-fires are not mistaken for the Step 2 first fire), then `AskUserQuestion` in the same turn. Mark each `gate-*` task `completed` the moment the corresponding `AskUserQuestion` returns and its result has been consumed.

#### Session-scoped compromise tracker

The orchestrator maintains a **session-scoped compromise tracker** — a single markdown file that accumulates one entry per accepted compromise across this run, so a legitimately-accepted compromise (a `Defer to follow-up Issue` choice, an `Accept the limitation` choice, an ungated orchestrator path pick, or a post-completion override) stays visible and challengeable rather than being baked silently into the new baseline. The four append triggers (A/B/C/D) are defined under "Compromise-tracker append triggers" below; the post-completion review in Section 8 consumes the tracker as input. This subsection is the **canonical definition site** that those trigger write-instructions reference by name.

**Tracker file path and naming.** The tracker is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\.quorum` on Windows). Canonical filename: `compromises-YYYYMMDD-HHMM-<short-suffix>.md`, where `YYYYMMDD-HHMM` is a UTC timestamp (e.g., `20260520-1714`) generated **once at the start of the run** and `<short-suffix>` is a short collision-resistant random string. The timestamp prefix makes tracker files debuggably identifiable across multiple runs accumulated in `<tempdir>/.quorum/` over time — without it, the user has no easy way to map an old tracker file back to a specific session. Create the `.quorum` directory if it does not already exist, then author and append the tracker file itself via the `Write` tool (no shell redirect), consistent with the bash-etiquette and scratch-file conventions:

```bash
# POSIX (bash / zsh):
mkdir -p /tmp/.quorum
# then write / append the tracker to /tmp/.quorum/compromises-<YYYYMMDD-HHMM>-<short-suffix>.md via the Write tool
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
# then write / append the tracker to $env:TEMP\.quorum\compromises-<YYYYMMDD-HHMM>-<short-suffix>.md via the Write tool
```

**Entry shape.** Each accepted compromise appends one `## Compromise <n>` section, where `<n>` is a **1-based counter scoped to the current run's tracker file** (NOT a globally unique identifier). The canonical shape (reproduced from the SDD Data models `#### Compromise tracker entry shape`) is:

```markdown
## Compromise <n>

- **Finding (verbatim):** <severity tag> <fix-path enumeration with depth tags> <description>
- **Fix paths surfaced by reviewer:**
  - (a) [depth:<depth>] <description>
  - (b) [depth:<depth>] <description>
  - ...
- **Decision:** <one of: User picked path (a) | User picked path (b) | ... | User picked Defer to follow-up Issue | User picked Accept the limitation | Orchestrator picked path (x) — highest-quality | User overrode auto-route after post-completion challenge (depth misjudgment) | User accepted under-enumeration after post-completion challenge>
- **Rationale:** <user's stated reason if surfaced via AskUserQuestion, or — on an ungated orchestrator pick — the one-line reason that path was preferred over the others; on a `Defer to follow-up Issue` entry it also names which remaining enumerated path shipped as the soft fix, or that none did, and on a blocker deferral the narrowing record in its place>
- **Follow-up Issue:** <ticket ID if filed via /quo-file-issue, else `none`>
```

The five fields are **Finding (verbatim)** (the severity tag + fix-path enumeration with depth tags + description), **Fix paths surfaced by reviewer** (the `(a)/(b)/...` lines, each carrying its `[depth:<...>]` tag), **Decision** (one of the enum values above), **Rationale** (the user's stated reason if surfaced via `AskUserQuestion`, or — on an ungated orchestrator path pick — the one-line reason that path was preferred over the others; on a `Defer to follow-up Issue` entry it also names which remaining enumerated path shipped as the soft fix, or that none did, and on a blocker deferral the narrowing record in its place), and **Follow-up Issue** (a ticket ID, else `none`). The `Decision` enum carries **two** post-completion-override values — `User overrode auto-route after post-completion challenge (depth misjudgment)` (the SR-6.7 depth-misjudgment override) and `User accepted under-enumeration after post-completion challenge` (the SR-4.6 under-enumeration analog override) — because Trigger D (below) is the single owner of all post-completion-override writes regardless of which kind fired.

**Persistence.** The tracker is a file-system artifact, so it persists across orchestrator-yield events within a single run inherently (a yield does not lose file state). A fresh `YYYYMMDD-HHMM` timestamp + `<short-suffix>` is generated at the **start of each run**, so previous-run tracker files remain visible in `<tempdir>/.quorum/` but are **NEVER appended to** — a new run always writes its own new file. Never delete the tracker file (scratch-file convention) — do NOT instruct any `rm` / `Remove-Item`.

#### Compromise-tracker append triggers

Four moments append an entry to the session-scoped compromise tracker defined above. The first three fire from the "Orchestrator discipline: routing review findings" section's gates / ungated dispatch; the fourth fires from Section 8's post-completion review. Each trigger anchors to its gate by name; the write fires from the branch named here.

**Trigger A — Defer to follow-up Issue at either gate.** At the scope-bounding gate (part (c) of the "### Orchestrator discipline: routing review findings" section above), when the user picks `Defer to follow-up Issue`: append a tracker entry **IMMEDIATELY AFTER** `/quo-file-issue` returns successfully with the new Issue ticket ID, and **BEFORE** the orchestrator continues with the soft-fix dispatch this round. Capture the follow-up Issue ID in the entry's `Follow-up Issue` field; set `Decision: User picked Defer to follow-up Issue`. Write `Fix paths surfaced by reviewer: none` when the reviewer enumerated no path at all — reachable at the routing-decision gate, whose `Defer` choice is offered whatever the path count. **Name in `Rationale` which remaining enumerated path shipped as the soft fix** — by its letter — or that **none did**, whenever deferring leaves no fix this round — the single-path case at the scope-bounding gate, and any deferral at the routing-decision gate, whose `Defer` bullet ships nothing against the finding regardless of how many paths the reviewer enumerated. **On a `blocker` deferral the narrowing takes that slot**: record the narrowing that shipped — what was scoped down, and why the blocker no longer describes what remains — in place of an enumerated letter or a `none did`, since a blocker's Defer branch ships a narrowing rather than one of the reviewer's other paths. Either way, the deferral and what shipped in its place are one decision, and an entry recording only the deferral leaves the reader unable to tell a soft-fixed finding from an unfixed one. (This write fires from that gate's `Defer to follow-up Issue` branch.) **The routing-decision gate's `Defer to follow-up Issue` branch fires this same trigger**, on the same terms and with the same entry shape — that gate offers the choice to any finding, and to a `blocker` when part (c)'s two Defer conditions hold, so a deferral taken there is recorded exactly as one taken here. **On a `blocker`-severity finding this branch is reachable only as Defer-with-narrowing, at either gate** (part (c)'s severity rule, which part (d) applies on its own terms), and the entry MUST then carry a **narrowing record** in `Rationale`: what was narrowed out of the change, and why the blocker no longer describes anything that ships. A blocker deferral without that record is the shape every downstream consumer reads as a contract violation.

**Trigger B — Accept the limitation at the scope-bounding gate.** At the same scope-bounding gate's `Accept the limitation` branch, when the user picks `Accept the limitation`: append a tracker entry **IMMEDIATELY AFTER** the `AskUserQuestion` returns the user's choice, and **BEFORE** the orchestrator continues without a fix. Set `Decision: User picked Accept the limitation`; set `Follow-up Issue: none`. **Unreachable for a `blocker`-severity finding**, unconditionally — that gate's severity rule withholds this branch from blockers entirely, since accepting a blocker ships it.

**Trigger C — ungated route (the orchestrator's own path pick).** This trigger has **no gate** — the write is wired into the dispatch step itself. At the **MOMENT of implementer dispatch** for any finding part (a) routed by **row 6** (the ungated dispatch of the path the orchestrator picked at Step 1), append a tracker entry in the **SAME LOGICAL BLOCK as that dispatch** — not a separate post-gate block. **One carve-out:** a finding whose *only* fix path is `trivial-tweak` appends nothing — a single trivially-deletable path is not a decision worth tracking. A pick among two or more paths always is, even when every path is shallow. Set `Decision: Orchestrator picked path (x) — highest-quality`, where `(x)` is the chosen path's letter; set `Rationale:` to **the orchestrator's own one-line reason for preferring that path over the others** — why it is the smallest internally-consistent complete change — not merely the name of the rule that fired, since the rule name gives Section 8's challenge nothing to push against; set `Follow-up Issue: none`.

**Row 6 is this trigger's only firing site.** A `blocker` routed to the scope-bounding gate still *fires* that gate — its severity rule leaves the user a choice — so the user picks, and a user-picked path is not an ungated route: no Trigger C entry is written for it.

**Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).** Trigger D is the single owner of all post-completion-override tracker writes, fired from Section 8's post-completion review. It covers **both** post-completion-override gates present in Section 8 — the SR-6.7 depth-misjudgment recovery gate AND the SR-4.6 under-enumeration analog recovery gate. The write logic here anchors to those gates by name, with choice labels byte-identical to the recovery-gate choices so they line up.

- **SR-6.7 depth-misjudgment recovery gate:**
  - `Accept the misjudgment and proceed` → append a **NEW** tracker entry **IMMEDIATELY AFTER** the user picks this choice, **BEFORE** the post-completion flow continues. Set `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)`; set `Rationale:` to the post-completion reviewer's challenge text.
  - `File follow-up Issue to revisit the depth decision` → **NO new entry is appended.** Instead, the **ORIGINAL Trigger C entry** (already written at dispatch time for this ungated-route finding) has its `Follow-up Issue` field **UPDATED in place** to the new Issue ID. (The depth misjudgment concerns a path the in-flow reviewer already surfaced and the orchestrator routed without a gate, so an originating Trigger C entry always exists to amend.)
  - `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again — no write fires on this branch until a subsequent `Accept` / `File` pick.
- **SR-4.6 under-enumeration analog recovery gate (same Trigger D mechanism, under-enumeration variant):**
  - `Accept the under-enumeration and proceed` → append a **NEW** tracker entry **IMMEDIATELY AFTER** the user picks this choice, **BEFORE** the post-completion flow continues. Set `Decision: User accepted under-enumeration after post-completion challenge`; set `Rationale:` to the post-completion reviewer's under-enumeration challenge text.
  - `File follow-up Issue to surface the missing path` → file the follow-up Issue and capture its ID. This branch concerns a missing path the in-flow reviewer never surfaced, so there is generally **no original Trigger C entry to amend** — append a **new** entry with the under-enumeration `Decision` value and the new Issue ID in `Follow-up Issue`. If the under-enumeration relates to an existing ungated-route finding (an originating Trigger C entry does exist), mirror the SR-6.7 File-branch's behavior instead and **UPDATE that entry's `Follow-up Issue` in place**; append otherwise.
  - `Pause to discuss` → **DEFER** any tracker write until the discussion resolves and the user picks again.

Throughout the per-Issue lifecycle (Section 3's Analyst pass, Section 4's implementer dispatch, Section 5's reviewer + PM review loop, Section 6's doc-verify confirmation), agents may have flagged items as "address later", "defer to next phase", "pick up during a follow-up Issue", or similar inter-session deferrals. Per `agents/pm.md`'s Final report contract and `agents/analyst.md`'s `### Deferred refinements` block, each such item arrives with a destination annotation; the orchestrator records the items it chose not to address inline as `defer-<short-suffix>` TaskList tasks per Section 4's TaskList naming convention (at the Section 3 Analyst-Approve / Analyst-Revise consumption sites — see Section 3's `### Deferred refinements` consumption paragraph — and at the Section 5 may-ignore-feedback site). This gate is the pre-handoff reconciliation step that closes them out into durable inter-session carriers before the run yields control (single-issue mode), advances to the next Issue (batch mode), or reaches Section 8's post-completion review.

**Step 0 — Retroactive ledger reconciliation (safety net).** The Section 3 Analyst-Approve / Analyst-Revise consumption paragraph and the Section 5 may-ignore-feedback site each instruct the Director to create a `defer-<short-suffix>` TaskList task at the moment the deferral is recorded. Before running Step 1's enumeration, walk three additional surfaces and **create a corresponding `defer-*` TaskList task for any item that does not already have one**:

1. **Section 5's per-Issue `**Ignored Review Feedback**` summary field** (the line in Section 7's per-Issue summary listing items flagged but not addressed). Each non-`None` bullet maps to a `defer-*` task. **This surface does not exist on the aborted path:** `#### Aborted-Issue close-out` invokes this gate at a boundary the Issue reached *without* passing through Section 7 step 4, so no per-Issue summary was ever rendered. Skip this surface there rather than hunting for a field that was never emitted — and do not treat its absence as an empty active set. The two surfaces below still apply on that path: the Analyst's block exists whenever Section 3 ran, and a PM Final report exists whenever a Phase C PM returned before the abort.
2. **PM Agent's Final report deferred items** (per `agents/pm.md`'s Final report contract — every item with a `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` destination annotation maps to a `defer-*` task; items annotated `addressed-now-in-this-Task` are skipped because they were addressed inline).
3. **Analyst's `### Deferred refinements` block** (per `agents/analyst.md`'s structured-return shape — every non-`None` bullet with a `defer-to-existing-ticket-body: <ticket-id>` or `defer-to-new-Issue` destination annotation maps to a `defer-*` task; bullets annotated `addressed-now-in-this-Issue` are skipped). The Section 3 Approve / Revise consumption paragraph is the load-bearing source for these items; this retroactive sweep is the defense-in-depth safety net.

The upstream record-creating instructions at the Section 3 consumption paragraph and at the Section 5 may-ignore site are the load-bearing source; this retroactive sweep is the defense-in-depth safety net for orchestrators that miss the instruction. After the retroactive reconcile, every deferred item from these three surfaces is represented in the active `defer-*` set and Step 1's enumeration sees the canonical view.

**Per-Issue firing.** This gate fires at the end of every Issue, on **both** of that boundary's paths — it has two invocation sites, not one:

- **Fixed path** — between Section 7's mark-done-and-commit step and the per-Issue advance to the next Issue (batch mode) or to Section 8 (single mode).
- **Aborted path** — invoked by `#### Aborted-Issue close-out` step 2, after that close-out's prefix sweep of this Issue's TaskList tasks and before the Issue-boundary state-externalization checkpoint. There is no mark-done-and-commit step to sit after there (the Issue stays `open` with no commit), but the deferrals recorded before the abort are exactly as stranded as on a fixed Issue, and this gate is what moves each into a durable carrier. The hard-stop in Step 3 applies unchanged.

The per-Issue firing scopes the active deferral set to **deferrals surfaced during this Issue only**; deferrals from prior Issues in a batch run were already closed out at the end of their own per-Issue gate. Scoping per-Issue rather than per-batch is load-bearing — accumulating deferrals across a multi-Issue batch would surprise the user with a long list at session end and defeat the per-Issue close-out discipline this skill already enforces.

**Batch end-of-run firing.** In batch / `all` mode, this gate fires again at the end of the whole batch, between the last Issue's Section 7.5 per-Issue close-out and Section 8 (post-completion review). The end-of-batch firing catches any deferrals the orchestrator surfaced *between* Issues — at the inter-Issue advance boundary, during batch-level reconciliation, etc. — that did not belong to any single Issue's per-Issue gate. The active set at the end-of-batch firing should typically be empty (per-Issue gates already closed out per-Issue deferrals); the end-of-batch firing exists as a defensive sweep, not as a routine surface, so a one-line `Deferral hygiene (batch close): no deferred items.` is the expected output.

**Step 1 — Enumerate the active deferral ledger.** Scan the TaskList for tasks whose name starts with `defer-` and whose status is `pending` or `in_progress`. If the active set is empty, emit a one-line console message — recommended string: `Deferral hygiene: no deferred items.` (per-Issue firing) or `Deferral hygiene (batch close): no deferred items.` (end-of-batch firing) — and advance per the firing-mode rules above.

**Step 2 — Surface the active set and gate the user choice.** When the active set is non-empty, surface the list to the user as numbered markdown (one bullet per `defer-*` task, the `metadata.activity` text as the bullet's body), then fire the user gate through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this deferral-hygiene gate (per Section 4's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` with the finite choices below in the same turn. Mark the `gate-*` task `completed` the moment the user's answer is consumed and the routing into Fix / File / Encode begins.

- **Fix in this session** — Re-dispatch the appropriate implementer / reviewer Agents per Section 4's dispatch shape, or do the orchestrator-owned ticket-body update inline per the Encode branch below, to resolve each deferred item now. After each item is resolved, mark its `defer-*` TaskList task `completed` (with `metadata.activity` updated to log the resolution path).
- **File as issue tickets** — For each item, invoke `/quo-file-issue` inline via the Skill tool with the deferral's description as the issue body (the precedent for inline-Skill-tool dispatch lives in Section 1's URL-resolution sub-step). Mark each `defer-*` TaskList task `completed` once the `/quo-file-issue` dispatch returns successfully and the created Issue ID is captured.
- **Encode in an existing ticket body** — For each item the user maps to an existing ticket (a Plan Bee, Epic, Task, Subtask, Spec Bee `t1=Doc` child, or the project PRD/SDD via a doc-writer pass), append a `## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)` section to the named ticket's body and run `bees update-ticket --ids <ticket-id> --body-file <path>` to land the update, where `<YYYY-MM-DD HH:MM>` is the current local date and time written into the heading from your own clock via the `Write` tool (it is a value you author into the body-file as a string, not a shell-computed substitution — do not add a `date` / `Get-Date` snippet for it). Keep the `## Deferred from /quo-fix-issue run` stem verbatim and only append the parenthesized timestamp suffix: the suffix exists so that multiple Encodes to the same ticket body across separate runs sit side-by-side with distinguishable headings rather than stacking identical ones — do not simplify it back to a bare heading. Author the revised body to a temp file via the `Write` tool under the namespaced workflow scratch dir. **Filename**: re-use the suffix of the `defer-N` TaskList task that triggered the encode — e.g., for the encode triggered by `defer-3`, the scratch file is `bees-body-defer-3.md`. Reusing the triggering task's suffix is deterministic, debuggable, collision-resistant under this run's active `defer-*` set, and ties the scratch file directly back to its TaskList progenitor:

  ```bash
  # POSIX (bash / zsh):
  mkdir -p /tmp/.quorum
  # then write the revised body to /tmp/.quorum/bees-body-<defer-N>.md via the Write tool
  # (e.g., /tmp/.quorum/bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  ```powershell
  # Windows (PowerShell):
  New-Item -ItemType Directory -Force -Path "$env:TEMP\.quorum" | Out-Null
  # then write the revised body to $env:TEMP\.quorum\bees-body-<defer-N>.md via the Write tool
  # (e.g., $env:TEMP\.quorum\bees-body-defer-3.md for the encode triggered by defer-3)
  bees update-ticket --ids <ticket-id> --body-file <path>
  ```

  Do NOT remove the temp file after the bees command exits — files under `<tempdir>/.quorum/` accumulate intentionally so a crashed run leaves debuggable artifacts in a known place. Mark each `defer-*` TaskList task `completed` once the update succeeds.

  **Follow-up commit (after all Encode writes in this gate firing have landed).** On the **fixed** path this gate fires after Section 7 step 2's per-Issue commit step, so a commit already exists for that Issue; on the **aborted** path it fires from `#### Aborted-Issue close-out`, where that step never ran and the Issue contributes **no** per-issue commit at all. Do not rest this follow-up commit on a per-Issue commit having landed — the premise it actually needs is narrower and holds on both paths: the `bees update-ticket --body-file` writes above persist new on-disk changes to the relevant hive's per-ticket directory (or to the project PRD/SDD file path), those changes are NOT swept into any prior commit, and they would otherwise leave the working tree dirty when the skill yields (per-Issue firing) or advances (end-of-batch firing). The commit stays well-defined on a commitless Issue precisely because of what it stages: only the resolved in-repo hive paths and the explicit `--doc-path` arguments, committed **conditionally** on there being staged changes. An aborted Issue with no Encode writes therefore stages nothing and produces no commit — the correct outcome, not a gap — and the aborted Issue's uncommitted fix-in-progress is never swept in, since it is neither a hive path nor a `--doc-path`. Produce one follow-up commit per gate firing covering all Encode writes from this firing — not per Encode item — to keep commit churn proportional to the user's choice. Resolve the Plans, Specs, and Issues hive paths via `bees list-hives` (the same pattern Section 7 step 2's commit step uses for Issues), `git add` each hive path that lives inside this repo, additionally `git add` the project PRD/SDD file paths from CLAUDE.md `## Documentation Locations` when the user routed any Encode to those destinations, then commit only if `git diff --cached` shows staged changes (an out-of-repo hive plus no PRD/SDD encode routes would stage nothing — skip the commit in that case rather than producing an empty one). Commit subject contract: `Encode deferral: /quo-fix-issue — <N> deferral(s) encoded` where `<N>` is the count of `defer-*` items the user routed to Encode in this gate firing. **`<N>` counts deferral items, not tickets** — several items can be encoded into one ticket body, and one item can be encoded into several, so the item count is the honest number and is the same value passed as the helper's `--count` below.

  This workflow (hive-path resolution via `bees list-hives`, in-repo scoping, conditional commit on staged state) is encapsulated in a bundled Python helper, `hive_commit.py`, so the orchestrator runs it as a single literal Bash tool call rather than decomposing a multi-step shell snippet at runtime. The helper resolves the Plans/Specs/Issues hive paths, `git add`s each hive path that lives inside this repo (out-of-repo hives have already had their bees update persisted by `bees update-ticket` and require no git action), `git add`s any project PRD/SDD paths passed via `--doc-path`, then commits only if there are staged changes — printing `skipped: nothing staged` and making no commit when nothing is staged. **Do NOT blindly `git add -A`** — other agents or processes may have in-flight changes in the working tree (same anti-pattern as Section 7 step 2's per-Issue commit step); the helper stages only the resolved hive paths and the explicit `--doc-path` arguments, never `-A`.

  **Resolving the helper path (sibling-skill resolution).** `hive_commit.py` is shipped by `/quo-execute`; this skill consumes it as a *sibling* bundled script. Resolve its path at runtime from this skill's own base directory: `<this skill's base directory>/../quo-execute/scripts/hive_commit.py`. The base directory is shown in the skill invocation header at session start (e.g., `Base directory for this skill: /Users/.../quo-fix-issue`). Use the `..` traversal pattern to reach the sibling skill — this matches the same sibling-resolution discipline used elsewhere in the skill set (e.g., `scoped_marker_resolver.py`). On Windows, use backslash separators: `<this skill's base directory>\..\quo-execute\scripts\hive_commit.py`.

  Invoke it with `--skill quo-fix-issue`, `--count <N>` (the count of `defer-*` items the user routed to Encode in this gate firing — matching the commit-subject contract above), and one `--doc-path <abs-path>` per project PRD/SDD file the user routed an Encode to (resolved from CLAUDE.md `## Documentation Locations`; omit entirely in the common case where no doc was routed):

  ```bash
  # POSIX (bash / zsh):
  python3 "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]
  ```

  ```powershell
  # Windows (PowerShell):
  python "<resolved-helper-path>" --skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]
  ```

  After the helper lands the commit (or prints `skipped: nothing staged`), proceed to Step 3 below.

The three options are mutually-non-exclusive at the active-set level — the user may pick one option overall, or the orchestrator may resolve different items via different options when the user's reply directs it that way (e.g., "fix items 1 and 2 now, file 3 as an Issue"). Whatever the routing, every `defer-*` task in the active set MUST be `completed` by the end of this gate. When the user wants to route different items to different options, they select `AskUserQuestion`'s auto-appended free-text slot (`Type something.` / `Chat about this`) and type the per-item routing in free-form; the orchestrator parses the reply and closes out each `defer-*` task accordingly.

**Step 3 — Hard-stop on a non-empty active set.** Until every `defer-*` task is `completed`, the skill cannot advance past this gate. On per-Issue firing, the next Issue (batch mode) or Section 8 (single mode) is blocked until the active set is empty; on end-of-batch firing, Section 8 is blocked. This is the structural enforcement: a deferral that was important enough to surface during the run is important enough to encode in a durable carrier before the run ends. If the user picks options that fail to close out a subset (e.g., `/quo-file-issue` cancelled at one of its gates, or a `bees update-ticket` invocation errors), surface the still-active `defer-*` tasks back to the user with `AskUserQuestion` and re-run the gate until the active set is empty.

The fresh-session-per-phase recommendation at run close-out is preserved verbatim — this gate sits before that handoff prose; it does not replace it.

### 8. Post-Completion Review

After all issues are fixed (in batch mode: after the final issue in the batch; in single mode: after the one issue), run a final fresh-context generalist sweep across all changes made during this quo-fix-issue session.

**End-of-batch deferral-hygiene firing.** In batch / `all` mode, before this section's fresh-context sweep, re-fire Section 7.5's deferral-hygiene gate as the **end-of-batch firing** documented there. **When re-firing here, treat the invocation as the end-of-batch firing per Section 7.5's batch-firing semantics** — emit the `Deferral hygiene (batch close): no deferred items.` console message on an empty active set (not the per-Issue variant), and apply the end-of-batch active-set scope (deferrals surfaced *between* Issues at the inter-Issue advance boundary or during batch-level reconciliation, which did not belong to any single Issue's per-Issue gate). In single mode, the per-Issue firing at the end of the one Issue already covered the active set and the end-of-batch firing is skipped — Section 7.5's batch-firing prose is a no-op on the single-issue path. The active set at the end-of-batch firing should typically be empty (per-Issue gates already closed out per-Issue deferrals); the end-of-batch firing exists as a defensive sweep against deferrals surfaced at the inter-Issue advance boundary or during batch-level reconciliation. Until the active set is empty, this section cannot proceed to the fresh-context sweep below.

**Anti-pattern callout — read before acting.** Do NOT invoke `/quo-engineer-review`, `/quo-doc-writer-review`, or `/quo-test-writer-review` at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep (e.g. `/quo-engineer-review` is scoped to source code, `/quo-doc-writer-review` to user-facing docs, `/quo-test-writer-review` to test files — none of them runs the cross-lane sweep this step needs). Spawn a fresh general-purpose agent with a self-contained prompt instead.

**Anti-pattern callout, second.** The team-lead must NOT do this review directly. By construction the team-lead has accumulated framing prompts, agent reports, and reviewer verdicts from the whole run; that context biases it toward "did the four phases get done correctly?" rather than "is this good?". The fresh agent gets the diff and the issue body and nothing else — that's the point.

1. Compute the pre-session diff scope. Capture `<pre-session-sha>` as the HEAD that existed when quo-fix-issue began (`Read` the run-state manifest at `<tempdir>/.quorum/run-state-quo-fix-issue-<repo-dir-name>.md` — the path is recomputed from the working tree root's basename per Section 1, not remembered — and take its **Pre-session SHA** field — that is where Section 1's run-start step recorded it; as a fallback if the manifest is missing, use `HEAD~N` where `N` is the number of issues actually fixed in this session — one commit per issue per Section 7 step 2.4). **Before trusting the Pre-session SHA, validate the manifest is this run's:** compare its **Unit scope** ordered Issue batch against the Issue list this session actually fixed. On mismatch — the stale/foreign-manifest tell Section 1 `#### Write the run-state manifest` describes, where a concurrent run in a same-basename checkout truncated the file and left a SHA that need not even exist in this repository — ignore the manifest entirely and take the same `HEAD~N` fallback above, rather than scoping the review diff from a foreign SHA. Collect the issue ID list as `<issue-id-1> <issue-id-2> ...` (one ID in single-issue mode; the full session list in batch mode).

2. Spawn a fresh reviewer using the **Agent tool with `subagent_type=general-purpose` and `run_in_background=true`**. The agent will not see anything else from this session, so the prompt must be self-contained. Pass the compromise-tracker file path (Section 7.5's `compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`) as `<compromise-tracker-path>` — the path, NOT the inlined contents; the dispatched Agent reads the file itself via its own `Read` tool. Starting skeleton (substitute `<pre-session-sha>`, `<compromise-tracker-path>`, and the issue ID list before sending):

   ```
   You are an independent reviewer for a quorum fix that was just shipped.

   Scope: review the diff `git diff <pre-session-sha>..HEAD` (compute it
   yourself via git) against the issue body, or bodies in batch mode — read
   each via `bees show-ticket --ids <id>`. Issue IDs in this session:
   <issue-id-1> <issue-id-2> ...
   The orchestrating team-lead has finished the work — your job is to give it a
   fresh-eyes review with no context of how the work was done.

   Perform these phases IN ORDER. Phases 1–5 lead with challenging the
   compromises that were accepted during the run; the discrete-defect sweep is
   the FINAL phase, not the first.

   PHASE 1 — Consume the compromise tracker (passed as a FILE PATH).
   The session-scoped compromise tracker records every compromise the run
   accepted (deferred-to-Issue findings, accepted limitations, ungated
   orchestrator path picks, post-completion overrides). Its path is:
   <compromise-tracker-path>
   Read that file yourself via your Read tool — it is passed as a path, not
   inlined. Each `## Compromise <n>` entry carries: Finding (verbatim), Fix
   paths surfaced by reviewer (each with a `[depth:<...>]` tag), Decision,
   Rationale, Follow-up Issue. If the tracker file is MISSING or unreadable,
   do NOT abort — PROCEED with the remaining phases and flag the missing
   tracker explicitly in your output (so the dropped hand-off is visible
   rather than silent).

   PHASE 2 — Challenge each tracked compromise on its merits. For every entry,
   push back when the chosen path is not defensible; do not rubber-stamp a
   compromise just because it was accepted. Include the deep-asked-but-cheap-
   shipped check: the tracker records what the user asked for (or, on an
   ungated pick, what the orchestrator chose), the diff is what actually
   shipped — flag any mismatch (e.g., the user picked a deep fix path but the
   implementer's diff implemented the cheap path). ALSO: any entry whose
   `Finding (verbatim)` carries the `blocker` severity tag and whose
   `Decision` is `User picked Accept the limitation` is a contract violation
   — a blocker can never be accepted. So is one whose `Decision` is `User
   picked Defer to follow-up Issue` and whose `Rationale` carries **no
   narrowing record** (what was narrowed out of the change, and why the
   blocker no longer describes anything that ships): a blocker may be
   deferred only paired with that narrowing. So is one whose narrowing
   record shows the narrowing **left the unit's stated defect partly
   unfixed** — a narrowing may never reduce coverage of the stated defect,
   and a blocker that cannot be made inapplicable to what ships without
   that loss was in scope and should have been fixed. Emit any of these as
   a `[compromise-challenge]` finding at `blocker` severity, never lower.

   PHASE 3 — Ungated-pick plausibility check, on TWO axes. For every tracker
   entry whose Decision is `Orchestrator picked path (<letter>) —
   highest-quality` — the `<letter>` varies per entry, since the writing step
   substitutes the chosen path's own letter, so match on the surrounding
   wording rather than on a literal letter — evaluate BOTH: (i) was the depth
   judgment plausible, or is the chosen path's true depth `re-architect`; and
   (ii) did the chosen path in fact introduce a mechanism — a new state,
   configuration surface (flag, environment variable, setting), persisted or
   wire field, background task, exception or error type, metric / log / trace
   attribute, name or identifier class, gate, or retry / fallback path that
   the unit's approved design did not enumerate — and, if so, should that
   machinery have been deferred to a follow-up ticket or put to the user
   rather than built here? Ask that of every such entry. Emit a
   `[compromise-challenge]` finding on either axis. Axis (ii) is required, not
   optional: an ungated pick is an orchestrator judgment no gate reviewed, and
   this phase is the only place it gets challenged.

   PHASE 4 — Fix-path-enumeration plausibility check. For EVERY finding the
   in-flow reviewer surfaced (regardless of severity / depth / path-count),
   evaluate whether the in-flow reviewer should have enumerated an additional
   plausible fix path. When you judge under-enumeration — the reviewer
   surfaced fewer paths than existed, so the pick (the orchestrator's, or the
   user's at a gate) was made from an incomplete menu — emit a
   `[compromise-challenge]` finding naming the under-enumeration. These two
   checks are complementary: PHASE 3 catches misjudged depth or an unnoticed
   mechanism on a path that WAS surfaced; PHASE 4 catches a plausible path
   that was NOT surfaced at all.

   PHASE 5 — Holistic solution-quality judgment beyond the logged compromises:
   is the shipped solution actually good, independent of any single tracked
   decision?

   PHASE 6 — Discrete-defect sweep (the final phase). Flag anything that looks
   wrong: code defects, prose problems, spec drift between the change and the
   issue, contract-key violations (do NOT allow renames of keys in CLAUDE.md
   `## Documentation Locations` or `## Build Commands`), cross-file
   inconsistencies, missing edits the issue called for.
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

   Return findings as a numbered list. Tag EVERY finding with exactly one of
   `[compromise-challenge]` (a challenge to an accepted compromise, from
   PHASE 2/3/4) / `[design]` (a solution-quality concern) / `[defect]` (a
   discrete defect), PLUS the severity tag (`blocker` / `suggestion` / `nit`),
   PLUS the per-fix-path depth tag and the enumerated fix paths from the
   in-flight emission contract. The depth tag is informative here: this
   post-completion sweep is the final pre-merge gate, so any finding it emits
   is a gate candidate regardless of depth. Preserve the `file:line` +
   severity shape — the new tags are additive to it. If clean, return exactly
   "no issues found".
   ```

   Wait for the agent's report.

3. Synthesize the findings before presenting. Compare the fresh reviewer's findings against the in-flight per-issue code/test/doc reviewer verdicts (which the team-lead still has in context) and flag any disagreements explicitly — e.g. "fresh reviewer flagged X but in-flight code reviewer judged X clean." Then present the synthesized findings (fresh reviewer's list plus your synthesis notes) to the user.

   **Compromise-challenge preamble (rendered before presenting the findings).** When the post-completion reviewer returns one or more `[compromise-challenge]` findings, render a one-or-two-sentence prose preamble BEFORE the findings list that names this explicitly, so the user reads the section with the right framing. Mirror the verdict-keyed preamble pattern in `/quo-plan` Step 5e and this skill's Section 3 Analyst-verdict preamble — a short prose lead with the `⚠️`-led divergent-framing convention used when a challenge is present, e.g. "⚠️ The post-completion reviewer **challenged** [N] compromise(s) accepted during this run — these are not new defects but pushback on decisions you already made; read them before the discrete findings below." When there are no `[compromise-challenge]` findings, no preamble is needed (present the findings directly).

   **Orchestrator self-tracking close-out (mandatory before yielding).** Independent of the per-issue TaskList tasks already closed in Section 7 step 3 and the per-finding follow-up tasks closed in step 6 below, the orchestrator typically creates additional ad-hoc TaskList tasks during this Section 8 pass to break the post-completion review into discrete steps (e.g., "Get diff scope", per-issue "Verify <id>" entries, "Synthesize findings"). Before presenting the synthesized findings to the user — i.e., before yielding the turn at step 4 / step 5 below, whether to deliver "no issues found" or to ask the user how to handle flagged issues via `AskUserQuestion` — mark every such orchestrator self-tracking TaskList task `completed` and clear them from the active set. The yield is the close-out trigger: when the orchestrator stops responding (either at end-of-flow or to wait on the user's reply), the TaskList must show no `in_progress` entries left over from these synthesis steps. This discipline is the orchestrator-self-tracking analog of step 6's per-finding follow-up close-out (which scopes to dispatched `<role>-postcomp-<n>` Agents and `file-issue-postcomp-<n>` per-finding tracking entries — the latter created by the "File as issue tickets" branch, which invokes `/quo-file-issue` per finding rather than dispatching an Agent); the two scopes are complementary, not overlapping.

4. If the agent returned "no issues found", report "Post-completion review: no issues found" and exit.

5. If the agent flagged any issues, fire the user-facing gate through the two-step `TaskCreate` → `AskUserQuestion` contract. **First** create a `gate-askuserquestion-<short-suffix>` TaskList task naming this post-completion findings gate (per Section 4's TaskList naming convention's gate-task entry), **then** call `AskUserQuestion` in the same turn. Do not produce a text response describing this gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch in step 6 is entered.
   - Question: "Post-completion review found [N] issues. How would you like to handle them?"
   - Options:
     - **Fix in this session** — address the issues now
     - **File as issue tickets** — create issue tickets via `/quo-file-issue` for each issue
     - **Skip** — acknowledge and move on without action

6. Execute the user's choice:
   - **Fix in this session**: Dispatch fresh ephemeral Agents per Section 4's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. Stay in delegate mode. Section 4's TaskList naming convention is issue-scoped (`<role>-<issue-id>`) and does not cover post-completion follow-up Agents that span the whole session, so for these dispatches use the **post-completion-scoped** name `<role>-postcomp-<n>`, where `<n>` is the 1-based index of the finding being addressed in the fresh reviewer's numbered list (e.g., `engineer-postcomp-1`, `doc-writer-postcomp-2`, `engineer-postcomp-3`). The per-finding discriminator is load-bearing: Section 4's "exactly one TaskList task per Agent" rule still applies here, so two findings that each need an Engineer follow-up must dispatch to distinct task names (`engineer-postcomp-1` and `engineer-postcomp-3`, say) rather than colliding on a shared `engineer-postcomp`. These names take **no** issue-id suffix, and normally no round discriminator either — the per-finding index is the discriminator. **One carve-out: a round discriminator IS permitted, and required, when a post-completion writer lane is re-dispatched after a movement abort** (the rung carried over below). That re-dispatch is a *second* Agent answering the *same* finding, so the one-task-per-Agent rule needs a fresh name that the finding index alone cannot supply: append `-r<k>`, where `<k>` is the 1-based re-dispatch count for that role at that finding index — `test-writer-postcomp-2-r1` for the first re-dispatch of the Test Writer lane on finding 2. `/quo-execute`'s post-completion naming entry carries the identical carve-out, so the two skills still read as one convention. Outside that case, do not append a round discriminator to a post-completion name. When each follow-up Agent returns, persist the result the same way Section 4's reconcile-on-completion step does: confirm any bees ticket transitions the worker committed to, then mark the corresponding `<role>-postcomp-<n>` TaskList task `completed` and clear it from the active set (mirroring Section 7 step 3's per-issue close-out). **Section 4's movement-report rung carries over with it**: a `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` return that reports it *stopped* on detected source movement is not a completion. Apply that rung here on the post-completion names — mark the writer's own `<role>-postcomp-<n>` task `completed` (its Agent has exited) and open an `aborted-<role>-postcomp-<n>` task `pending` in its place, **carrying the same `<n>` as the lane it marks**, with the writer's "how far I got" report as its `metadata.activity` string. Re-dispatch the lane once the source has settled, per that rung's three mover branches, under the round-discriminated post-completion name the carve-out above permits — `<role>-postcomp-<n>-r<k>` — and mark the `aborted-*` task `completed` when that re-dispatch delivers. While an `aborted-<role>-postcomp-<n>` task is `pending`, do **not** treat this Section 8 pass as finished and do **not** commit — that pending marker is the owed redelivery, exactly as in Section 4.

     **The rung's unexplained-movement gate applies here, but read its abort option's *whole body*, not just its title.** The gate itself carries over unchanged, and its third option is read as *abort this follow-up lane* rather than *abort this Issue* — the Issue is already `done` and its per-issue commit already landed by the time Section 8 runs. **That re-titling is not the only thing that changes: the option's body routes an aborted Issue through `#### Aborted-Issue close-out`, and none of that routing applies on this branch.** Here the abort closes out via **this branch's OWN prefix sweep** — the "Close out the `aborted-*-postcomp-<n>` markers with the rest" paragraph below — and **not** via `#### Aborted-Issue close-out`, which is scoped to an Issue abandoned *before* its fix landed. Running that close-out from here would re-fire Section 7.5 for an Issue whose deferral gate already closed, run the Issue-boundary checkpoint's aborted path (which asserts the Issue reads `open` and expects no commit) against an Issue that is legitimately `done` and committed, and — in batch mode with Issues still remaining — stop the run outright with a fresh-session resume command for the still-unfixed subset, even though post-completion review over the whole session's diff was already under way. After this branch's sweep, **continue Section 8's own flow**: the remaining findings' dispositions, then step 7's compromise-challenge recovery gates, then Section 9. Once all follow-up lanes have delivered, commit.

     **Close out the `aborted-*-postcomp-<n>` markers with the rest.** The close-out sentence above ("mark the corresponding `<role>-postcomp-<n>` TaskList task `completed` and clear it from the active set") covers these too — sweep by name **prefix**, so both an `aborted-<role>-postcomp-<n>` marker and any `-r<k>`-discriminated movement-abort re-dispatch are closed alongside their first round rather than left behind in the active set when this Section 8 pass exits. This sweep is also the close-out the unexplained-movement gate's abort option routes to on this branch, per the paragraph above.

     **The Engineer-dispatch precondition applies here too, on the post-completion names.** Section 4's precondition keys on the issue-scoped names (`test-writer-<issue-id>` and friends), which do not match these post-completion-scoped ones, so state it explicitly for this branch: **the orchestrator MUST NOT dispatch an `engineer-postcomp-<n>` Agent while any `test-writer-postcomp-*` or `doc-writer-postcomp-*` TaskList task is `pending` or `in_progress`** — matching on the name prefix plus status, at **every** finding index and every `-r<k>` re-dispatch round, not only the `<n>` of the finding being addressed. The reason is the one Section 4 gives: a writer handed a diff an Engineer is about to rewrite has to redo its work. Section 4's `pending`-with-no-Agent-behind-it clause carries over unchanged — dispatch the stalled role, or clear the stale task, rather than waiting on a notification that will never arrive.

     **Order the lanes when one finding needs both a source change and a test/doc change.** Dispatch the **Engineer** (`engineer-postcomp-<n>`) first and let it return; only then dispatch the `test-writer-postcomp-<n>` / `doc-writer-postcomp-<n>` lane whose input that source change determines. Two findings independent of each other may still be worked concurrently — the within-finding ordering above and the cross-finding precondition before it are the only constraints.
   - **File as issue tickets**: For each issue, invoke `/quo-file-issue` with the issue description. Report the created ticket IDs to the user. If the orchestrator created any TaskList progress entries during this Section 8 pass (for example, to track per-finding filing progress), use the same per-finding discriminator pattern as the "Fix in this session" branch — name each entry `file-issue-postcomp-<n>` where `<n>` is the 1-based index of the finding being filed — and mark them `completed` and clear them from the active set before exiting, the same close-out discipline as the "Fix in this session" branch.
   - **Skip**: Done.

7. **Compromise-challenge recovery gates.** A `[compromise-challenge]` finding from PHASE 3 or PHASE 4 is not handled by step 6's generic Fix / File / Skip disposition alone — each such finding triggers its own recovery gate, fired **before or alongside** the step-6 disposition for that finding. **One challenge class has no recovery gate, by design: the accepted-`blocker`-or-unnarrowed-deferral contract violation PHASE 2 emits.** There is nothing to recover — the entry records an acceptance the gates should never have offered, or a deferral shipped without the narrowing that was its precondition, or one whose narrowing left the stated defect partly unfixed — so that finding is dispositioned by **step 6's Fix / File / Skip gate alone**, and because it is a `blocker`, the orchestrator recommends **`Fix in this session`** in that gate's question text. Do not invent a fourth gate for it. Both gates below use the two-step `TaskCreate` → `AskUserQuestion` contract: **first** create a `gate-askuserquestion-<short-suffix>` TaskList task naming the gate (a distinct collision-resistant `<short-suffix>` per fire, per the per-fire-uniqueness rule), **then** call `AskUserQuestion` with the finite choices in the same turn. Do not produce a text response describing the gate — fire `TaskCreate` and `AskUserQuestion` directly. Mark the `gate-*` task `completed` once the user's answer is consumed and the routing branch is entered. These are multi-choice only — do not add fake free-text options. Each gate **fires per challenged finding** (once per such `[compromise-challenge]` finding — three such findings ⇒ three gate firings), NOT aggregated into one gate; the **firing order equals the reviewer's emission order** in its numbered list. These gates inherit a prose-adherence fragility — an execution-time risk narrowed (not closed) by the two-step contract; do not claim it is fixed.

   - **SR-6.7 ungated-route recovery gate.** When a `[compromise-challenge]` finding flags an ungated orchestrator path pick (Decision `Orchestrator picked path (x) — highest-quality`) on either of PHASE 3's two axes — a misjudged depth, or a chosen path that introduced a mechanism and should have routed to the scope-bounding gate — fire a three-choice `AskUserQuestion` (the choice labels below are byte-matched against Section 7.5's Trigger D branches; do not reword them). **The pinned strings read generically across both axes:** `File follow-up Issue to revisit the depth decision`, `Accept the misjudgment and proceed`, and Trigger D's `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` all name **the routing misjudgment** the challenge landed on — the mechanism axis included, not the depth axis only. Read "depth decision" / "misjudgment" that way rather than concluding the mechanism axis has no gate; the choices are:
     - `File follow-up Issue to revisit the depth decision` — dispatch `/quo-file-issue` via the Skill tool capturing the depth-mismatch finding plus the original compromise-tracker entry as context; the **original Trigger C tracker entry's `Follow-up Issue` field is updated in place** with the new Issue ID (NO new tracker entry — per Section 7.5's Trigger D `File`-branch note).
     - `Accept the misjudgment and proceed` — fires Section 7.5's **Trigger D** append (a NEW tracker entry with `Decision: User overrode auto-route after post-completion challenge (depth misjudgment)` and the reviewer's challenge text as Rationale). This step FIRES Trigger D's write — it does not author it; the write mechanism is owned by Section 7.5's Trigger D.
     - `Pause to discuss` — stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. No tracker write fires on this branch until a subsequent `Accept` / `File` pick (per Trigger D's `Pause` note).
   - **SR-4.6 under-enumeration recovery gate.** When a `[compromise-challenge]` finding flags under-enumeration (the reviewer's fix-path-enumeration plausibility check), fire the **same three-choice gate shape** with relabeled choices:
     - `File follow-up Issue to surface the missing path` — dispatch `/quo-file-issue` via the Skill tool capturing the under-enumeration finding as context; the tracker write follows Section 7.5's Trigger D `File`-branch under-enumeration note (append a new entry, or update an existing originating Trigger C entry's `Follow-up Issue` in place when one exists).
     - `Accept the under-enumeration and proceed` — fires Section 7.5's **Trigger D** append (a NEW tracker entry with `Decision: User accepted under-enumeration after post-completion challenge` and the reviewer's under-enumeration challenge text as Rationale). This step FIRES Trigger D's write — it does not author it.
     - `Pause to discuss` — stop the post-completion flow at this gate and surface a prose discussion; the user can re-issue any of the three choices afterward. No tracker write fires on this branch until a subsequent `Accept` / `File` pick.

   The SR-4.6 gate's per-branch behavior shape mirrors the SR-6.7 gate exactly (file follow-up Issue / append explicit-override tracker entry via Section 7.5's Trigger D mechanism / pause-and-resume). Like the SR-6.7 gate, it fires per challenged finding (non-aggregated) in reviewer emission order.

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
