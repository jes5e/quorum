# <img src="assets/header.png" alt="" width="48" valign="middle"> quorum

**Multi-agent software engineering for Claude Code, with independent review at every step.**

**quorum** is a set of [Claude Code](https://claude.com/claude-code) skills that runs a full development workflow on top of a ticket system: plan a feature, break it into tasks, implement, test, document, review, and fix. Each piece of work is done by a separate, short-lived agent with one role, such as an Engineer, a Test Writer, a Doc Writer, a Product Manager, or a Reviewer. The agents hand work to each other through tickets and git, not through a shared chat history. It is built for shipping large features and whole applications with LLMs.

```
/quo-setup                            ← once per repo (safe to re-run)
        │
        ▼
/quo-plan   or   /quo-plan-from-specs ← from an idea  /  from a PRD + SDD on disk
        │
        ▼
/quo-breakdown-epic                   ← Epics → Tasks and Subtasks
        │
        ▼
/quo-execute                          ← do the work, with reviews

/quo-file-issue + /quo-fix-issue      ← any time, for bugs and follow-ups
/quo-status                           ← any time: "where am I?"
```

You need Claude Code, git, Python, and the [bees](https://github.com/gabemahoney/bees) ticket CLI.

## Why this exists

Coding agents are excellent in tight scope and lossy in long ones. Hand one agent a multi-day feature and the same failures recur: it builds up context nobody can audit, it approves its own work during "review", it drifts from the spec, and hours in it has forgotten why a decision was made. Bigger context windows don't fix this. The problem is scope discipline, not memory.

quorum's bet is that agent-built features reach production quality when the work is **split into ticketed units** and **several independent agents must agree** on each unit before it ships. That's where the name comes from. In practice:

- **Specs and tickets are durable, not chat scrollback.** A feature's PRD and SDD live as tickets. The plan breaks into Epics, Tasks, and Subtasks, and each ticket carries its context, the change required, the key files, and acceptance criteria. That's enough for a fresh agent to do the work without the conversation that produced it.
- **Each role is a separate agent.** The reviewers never saw the implementer's reasoning and are review-only, with no Edit or Write tools, so a review is a second opinion, not the author re-reading its own work.
- **The PM checks the work against the spec.** After a Task's code, tests, and docs are done, a PM agent compares the diff with the spec and with the neighboring Tasks. It flags drift, assumptions that break a sibling Task, and scope nobody asked for, and the Task doesn't close until those are resolved.
- **State lives in tickets, git, and a small run file.** You can stop a run and resume it in a fresh session, and `/quo-status` shows where the work stands.
- **You decide at defined points.** A run asks you only at decision points, such as approving a plan or a design, choosing what to do with a review finding, or a step only you can take. Anything deferred is routed to a ticket before the run ends, so nothing is silently dropped.

A few design priorities follow from this:

- **Parallel where lanes touch different files, ordered where they share a diff.** Within a Task (in `/quo-execute`) or an Issue (in `/quo-fix-issue`), the Engineer and Code Reviewer loop until the code review is clean. Only then do the Test Writer and Doc Writer run, together, followed by their reviewers. Tests and docs are never written against code that is still changing. `/quo-execute` works a plan's Tasks one at a time.
- **Any language or stack.** Skills read your build, lint, and test commands from your repo's `CLAUDE.md` instead of hard-coding `cargo`, `npm`, or `pytest`. Rust, Node, Python, Go, Java, polyglot repos, and unfamiliar stacks all work.
- **Any platform.** macOS, Linux, and Windows (PowerShell, WSL, or Git Bash). Every shell step ships in both POSIX and PowerShell forms, and the bundled helpers are Python.
- **Safe to re-run.** `/quo-setup` detects what is already configured and only asks about what is missing, and an interrupted planning or execution run picks up where it stopped.
- **Docs that stay small and true.** The Doc Writer corrects or removes what a change makes false, and records in the design doc only the rules and decisions a future agent needs. How the code works stays in the code; history stays in commits and tickets.

## The roles

The session you run a skill in is the **orchestrator**. It dispatches the roles, routes review findings, owns ticket state, and makes the commits; it doesn't write the code itself. Each role is a subagent defined in `agents/<role>.md`.

| Role | What it does | What it can't do |
|---|---|---|
| **Engineer** | Implements the change and runs your compile, lint, and narrow-test commands. | Write tests or docs (other roles own those). |
| **Code Reviewer** | Reviews the Engineer's diff with `/quo-engineer-review`. | Edit files. |
| **Test Writer** | Writes or updates tests for the settled diff, and can confirm a test fails without the fix by temporarily reverting it. | Change source or docs. |
| **Test Reviewer** | Reviews the tests with `/quo-test-writer-review`. | Edit files. |
| **Doc Writer** | Keeps your customer-facing docs (such as the README), the design doc (SDD), and the PRD true to the change. | Change source or tests; it has no shell. |
| **Doc Reviewer** | Reviews the doc changes with `/quo-doc-writer-review`. | Edit files. |
| **Product Manager** | Checks the Task's work against the spec and the neighboring Tasks. | Edit source, tests, or docs. |
| **Analyst** | Works out the root cause and proposes a design before code is written (`/quo-fix-issue`), or on escalation when execution hits something the plan didn't settle (`/quo-execute`). | Edit files. |

Every role runs on Opus. Each pins its own reasoning effort, `high` for all of them and `xhigh` for the Analyst, so your session's effort setting doesn't change how the roles run.

## Requirements

- **Claude Code** ([install](https://claude.com/claude-code)).
- **bees CLI**: `pipx install bees-md` (Python 3.10+). See the [bees docs](https://github.com/gabemahoney/bees).
- **git**, and a git repository to work in.
- **Python 3** on your `PATH`, as `python3` on macOS and Linux or `python` on Windows, for the bundled helper scripts.
- **A POSIX shell** (bash or zsh on macOS, Linux, or WSL) **or PowerShell** (native Windows).

## Install

### Option A: for all your repos (recommended)

Copy the skills and the role definitions into your user-level Claude Code directories:

```bash
# POSIX (bash / zsh):
git clone https://github.com/jes5e/quorum ~/projects/quorum
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r ~/projects/quorum/skills/* ~/.claude/skills/
cp -r ~/projects/quorum/agents/* ~/.claude/agents/
```

```powershell
# Windows (PowerShell):
git clone https://github.com/jes5e/quorum $HOME\projects\quorum
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills", "$HOME\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\quorum\skills\* $HOME\.claude\skills\
Copy-Item -Recurse $HOME\projects\quorum\agents\* $HOME\.claude\agents\
```

### Option B: for one repo

To try quorum on one repo without affecting others, copy the same files into that repo's `.claude/` directory:

```bash
# POSIX (bash / zsh):
mkdir -p /path/to/your/repo/.claude/skills /path/to/your/repo/.claude/agents
cp -r ~/projects/quorum/skills/* /path/to/your/repo/.claude/skills/
cp -r ~/projects/quorum/agents/* /path/to/your/repo/.claude/agents/
```

```powershell
# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path "C:\path\to\your\repo\.claude\skills", "C:\path\to\your\repo\.claude\agents" | Out-Null
Copy-Item -Recurse $HOME\projects\quorum\skills\* C:\path\to\your\repo\.claude\skills\
Copy-Item -Recurse $HOME\projects\quorum\agents\* C:\path\to\your\repo\.claude\agents\
```

### After installing

Claude Code loads subagent definitions when a session starts. If a session was already open when you copied the files, run `/agents` in it (this reloads them) or restart Claude Code. Until you do, `/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` stop with `Run /quo-setup first. — required subagent types … are not registered in this session`.

**To update**, run `git pull` in your clone and copy the files again. If you'd rather have updates apply immediately, symlink each skill directory and role file from your clone instead of copying them.

## Quick start

In the repo you want to work on:

1. **`/quo-setup`** registers the ticket hives, adds two sections to your `CLAUDE.md` (where your docs live, and your build, lint, and test commands), and offers to draft a starter PRD and SDD from your code.
2. **`/quo-plan add rate limiting to the public API`**: agree the scope, review the specs and Epics it drafts, and approve. You get a Plan Bee (the plan's top ticket) with its Epics.
3. **`/quo-breakdown-epic`** turns each Epic into Tasks and Subtasks. Run it in a fresh session, as the plan suggests.
4. **`/quo-execute <plan-bee-id>`** works through the Tasks, one commit per Task, and asks you only at decision points.

For a bug or a small change, skip planning: **`/quo-file-issue <description or URL>`**, then **`/quo-fix-issue <issue-id>`**.

Long runs work best in a fresh session for each skill. Every skill re-reads what it needs from tickets and disk, so nothing is lost between sessions.

## Concepts

quorum stores its work in [bees](https://github.com/gabemahoney/bees), a ticket system kept as markdown files in your repo.

- **Hive**: a collection of tickets. `/quo-setup` creates three of them.
  - **Plans** holds a **Plan Bee** per feature, broken into **Epics**, then **Tasks**, then **Subtasks**.
  - **Issues** holds bugs, follow-ups, small features, and tech debt.
  - **Specs** holds a **Spec Bee** per feature, whose `PRD` and `SDD` child tickets are that feature's spec.
- **Bee**: a ticket. Plan Bees and Spec Bees are the top-level tickets of their hives; Issues are Bees too.

| Hive | Statuses |
|---|---|
| **Plans** (Plan Bees, Epics, Tasks, Subtasks) | `drafted` → `ready` → `in_progress` → `done` |
| **Issues** | `open` → `done` |
| **Specs** (Spec Bees and their PRD/SDD) | `drafted` → `ready` |

`drafted` means written but not yet approved or broken down into the next tier. `ready` means fully planned and ready for the next stage.

## The skills

### Skills you run

| Skill | What it does |
|---|---|
| `/quo-setup` | One-time setup per repo. Registers the Plans, Issues, and Specs hives; writes the `## Documentation Locations` and `## Build Commands` sections of `CLAUDE.md`; optionally drafts a starter PRD and SDD from your code; and optionally installs the [context-usage gauge](#long-runs-and-the-context-guard). Safe to re-run. On a new machine in an already-set-up repo, it re-registers the hives and offers the gauge step, skipping the full walk-through. `--configure-gauge-producer` runs only the gauge step, even in a repo not set up for quorum. |
| `/quo-plan` | Turns an idea into a plan. It agrees the scope with you, writes the feature's PRD and SDD as a Spec Bee, and drafts the Epics. A spec review and an independent plan review then run, and one approval step shows you the specs, the Epics, and the findings. Only after you approve does it create the Plan Bee and its Epics; your project docs are not changed at plan time. An interrupted run resumes where it stopped. |
| `/quo-plan-from-specs` | The express path when you already have a finished PRD and SDD on disk: it creates the Plan Bee and Epics from them. It expects docs that describe one feature; for a doc with several `### Feature:` sections, pass `--feature "<title>"` to plan one of them. |
| `/quo-breakdown-epic` | Breaks a plan's drafted Epics into Tasks and Subtasks, each Subtask tagged with the role that does it. Read-only research agents explore the code, the skill drafts the breakdown, and an independent PM checks it against the spec before any ticket is created. With several Epics, it asks once whether to stop after each Epic or work through them all. |
| `/quo-execute` | Runs a plan: Epics in dependency order, one Task at a time, one commit per Task. For each Task the Engineer and Code Reviewer loop until the code review is clean, then the Test Writer and Doc Writer run together, then their reviewers and the PM. At each Epic boundary it runs the full test suite and one fresh review of the Epic's work, and you decide what to fix, file, or skip. The Analyst joins only on escalation (a design question the plan didn't settle, a review finding that contradicts the plan, or a fix that keeps breaking), and its revision comes to you for approval. When a step needs you, the run stops and asks. |
| `/quo-file-issue` | Files an Issue. Give it a description, or run it with no arguments and let it ask, and it writes a full spec: description, current and expected behavior, impact, and suggested fix. Give it a URL (a GitHub issue, a Linear ticket, any bug tracker) and it files a short ticket that points at the original, and offers the existing open Issue if that URL was already filed. |
| `/quo-fix-issue` | Fixes one Issue, a list of Issues, or `all` of them, in order, with one commit per Issue. URLs are accepted and filed first. For each Issue the Analyst first proposes a design for you to approve: the root cause, every place the fix must touch, and any policy questions it raises. The fix then runs through the same lanes as `/quo-execute`. Issues that only change docs or comments skip the Analyst and go straight to a writer and its reviewer. After the batch, one review covers all of it. For Issues linked to GitHub, it prints `gh issue close` commands for you to run. A stopped run resumes when you run the resume command it prints (the batch's Issue IDs, in order). |
| `/quo-status` | Shows where the work stands across the hives, and suggests what to run next. |

### Skills the workflow runs for you

You don't need to call these during normal use, but they appear in `/help`.

| Skill | Run by | What it does |
|---|---|---|
| `/quo-write-prd` | `/quo-plan` | Writes or revises a feature's PRD in its Spec Bee. Also runs alone: `/quo-write-prd <spec-bee-id>`. |
| `/quo-write-sdd` | `/quo-plan` | Writes or revises a feature's SDD in its Spec Bee. Also runs alone: `/quo-write-sdd <spec-bee-id>`. |
| `/quo-spec-review` | `/quo-plan`, `/quo-write-prd`, `/quo-write-sdd` | Reviews a Spec Bee's PRD and SDD for clarity, completeness, and consistency. Also runs alone: `/quo-spec-review <spec-bee-id>` (optionally `--doc PRD` or `--doc SDD`). |
| `/quo-engineer-review` | `/quo-execute`, `/quo-fix-issue` | Reviews the Engineer's diff and returns findings. |
| `/quo-test-writer-review` | `/quo-execute`, `/quo-fix-issue` | Reviews the Test Writer's tests and returns findings. |
| `/quo-doc-writer-review` | `/quo-execute`, `/quo-fix-issue` | Checks that the docs a change touched are true and that each fact sits in the right doc, and returns findings. |

## Fixing issues straight from a URL

`/quo-file-issue` and `/quo-fix-issue` both accept a bug-tracker URL as an argument. quorum files a short ticket that points at the original, and the agents fetch the full report when they pick it up, so there's no copying the report into a ticket.

```
/quo-file-issue https://github.com/owner/repo/issues/123         # just file it
/quo-fix-issue  https://github.com/owner/repo/issues/123         # file and fix in one go
/quo-fix-issue  b.abc https://github.com/owner/repo/issues/456   # mix ticket IDs and URLs
```

## Send a run's questions to a decider session

If you keep a second Claude Code session that advises you on a run's questions, the run can ask it directly instead of you relaying answers by hand. Name that session with `/rename`, then launch `/quo-execute`, `/quo-fix-issue`, `/quo-breakdown-epic`, or `/quo-plan` with `--decider "<session name>"`:

```
/quo-execute b.abc --decider "my decider"
/quo-fix-issue all --decider "my decider"
```

`--decider` with no name lists your live sessions and stops. A name that no live session answers to also stops the run.

- **What still comes to you:** the questions a run asks at launch. These are the session-effort check, which plan or Issue to work on, the branch choice, `/quo-plan`'s offer to resume, and filing the URLs given to `/quo-fix-issue`. Every later question goes to the decider, including plain-text questions and the questions `/quo-file-issue` asks when the run files an Issue. The decider decides when it needs you.
- **What the decider receives:** an introduction at launch, sent again when a `/quo-fix-issue` run resumes in a fresh session, explaining the run and how to reply. Then, for each question, a short `quorum gate:` message naming a gate file in the scratch directory. That file holds the question, its choices, and everything you would have seen, with files given by path. The decider replies with a choice or free text, naming the gate file.
- **You stay in charge:** every message shows in both sessions, and you can answer in the run at any time; the first answer wins. If a message can't be sent, or the decider has gone, the run asks you instead. A decider that stays open but never replies leaves the run waiting for you.
- **The record:** each gate file ends with the answer and who gave it.

Both sessions must be able to message each other: on the same machine (or in the same container), and either both or neither bypassing permission prompts, since a session that bypasses them holds messages from one that does not.

## Recommended session settings

Each role's model and effort are pinned in its `agents/<role>.md` file and are not affected by your session. Your session setting governs the skill you run, its orchestration, and the un-pinned helper agents it dispatches (plan and end-of-run reviewers, research agents):

| Skill | Recommended |
|---|---|
| `/quo-execute`, `/quo-fix-issue` | Opus, `medium`: it delegates all implementation, and its context is the longest in the run |
| `/quo-plan`, `/quo-plan-from-specs`, `/quo-write-prd`, `/quo-write-sdd`, `/quo-spec-review`, `/quo-breakdown-epic` | Opus, `high`: mistakes here carry into every Epic downstream |
| `/quo-setup` | Opus, `high`: it writes the `CLAUDE.md` sections every other skill reads |
| `/quo-status`, `/quo-file-issue` | Opus, `medium`: short reporting and capture |

These are minimums, and quorum leaves the setting to you. `/quo-execute` and `/quo-fix-issue` ask once at the start if your session is below `medium`, and `/quo-breakdown-epic` if it is below `high`. The other skills don't check. To change it, run `/model` or launch with `--effort <level>`. The levels are `low` < `medium` < `high` < `xhigh` < `max`.

## Long runs and the context guard

`/quo-execute`, `/quo-fix-issue`, and `/quo-breakdown-epic` carry the longest context in a run. Before each Task, Issue, or Epic after the first, and before each end-of-Epic or end-of-batch review, they check how full the session's context is. If it is close to the point where Claude Code would compact it mid-unit, they stop cleanly and tell you how to continue in a fresh session.

That check needs a **context-usage gauge**. Claude Code reports context usage only to your status-line command, so quorum adds a small producer to your status line that saves the reading to a file. Without it, these skills can't see how full the session is and run unguarded.

- **Install it** with `/quo-setup --configure-gauge-producer`, from any session. It wraps your existing status line rather than replacing it. It takes effect from your next session.
- **If a repo commits its own status line** in `.claude/settings.json`, that setting outranks your user-level one in that repo, and setup will warn you. To guard runs there too, add a `statusLine` to the repo's `.claude/settings.local.json` (keep it git-ignored) whose command is `"<python>" "<skills-dir>/quo-setup/scripts/context_gauge.py" produce --wrap-command "<the repo's status-line command>"`. Local settings outrank the committed file, and nothing committed changes. Re-running setup doesn't refresh this entry, so redo it after a Python upgrade.
- **To decline for good,** choose "run unguarded" in setup. It records that choice in an opt-out marker file, and setup stops offering the step. Running `/quo-setup --configure-gauge-producer` offers it again.
- **If the producer breaks**, for example after a Python upgrade, re-running setup repairs the user-level entry.
- **Some environments can't be configured from settings.** A `--settings` launch flag, organization settings, or MDM policy can outrank every settings file. Such an environment can still publish the reading itself by following the [file contract](#the-context-usage-gauge-file) below.

## Where docs live

If you let `/quo-setup` draft them, your project gets:

- `docs/prd.md`: what the product must do and why, meaning its goals, non-goals, product-level targets, and promises to users. The Doc Writer keeps it true and updates it when a change alters one of those.
- `docs/sdd.md`: where things are, the guarantees and cross-module rules the code must keep, the contract clients rely on, and decisions with their reasons. The Doc Writer keeps it true to each change and adds a rule or decision when a change makes one, never a section per feature.

Each feature's own PRD and SDD are written at plan time as tickets in its Spec Bee, and are not copied into these docs. The skills find your docs through `CLAUDE.md`'s `## Documentation Locations` section, so any layout works.

## Scratch files

Skills write short-lived files to a scratch directory, `/tmp/.quorum/` on macOS and Linux, or `%TEMP%\.quorum\` on Windows. These include:

- ticket bodies on their way to bees;
- each run's state file, which a run reads back after a compaction or when it resumes;
- the compromise tracker (review findings you chose to accept or defer) and the cost ledger (one row per agent dispatch);
- diff snapshots for the Doc Writer, which has no shell;
- the Analyst's current design proposal;
- one gate file per question sent to a decider.

The context-usage gauge files and the opt-out marker are written by a Python helper into the `.quorum` directory of Python's temp directory. That's `/tmp/.quorum/` on most Linux systems, `$TMPDIR/.quorum/` on macOS (under `/var/folders/`), and `%TEMP%\.quorum\` on Windows.

Skills never delete these files: the footprint is small, and they help when you investigate a run that went wrong. You can delete these directories **between** runs. Don't delete them **during** a run, or while a stopped run waits to be resumed, because the run's state file and compromise tracker are not recreated. Deleting the gauge helper's `.quorum` directory (the `$TMPDIR` one on macOS) also removes the opt-out marker, so setup will offer the gauge step again.

## Reference

### The context-usage gauge file

This is the contract for the reading the context guard uses, for anyone writing their own producer. The bundled helper `skills/quo-setup/scripts/context_gauge.py` follows it.

- **Location:** one file per session, `<tempdir>/.quorum/context-usage-<session_id>.json`. Here `<tempdir>` is Python's `tempfile.gettempdir()` (see [Scratch files](#scratch-files)), and `<session_id>` is the Claude Code session id.
- **Content:** a top-level `session_id` string and a `context_window` object, written as received from the status-line payload:

  ```json
  {"session_id": "<id>", "context_window": {"used_percentage": 37}}
  ```

  Consumers read `context_window.used_percentage`. Always write `context_window` as an object, an empty one when there is no reading, never `null`.
- **Freshness:** every status-line refresh overwrites the file. Freshness is judged from the file's modification time, and a reading older than 20 minutes counts as stale, so a producer must refresh at least that often.
- **Wrapping:** `produce --wrap-command "<your status-line command>"` runs your command and prints its output unchanged, so the gauge is added to an existing status line. A payload it can't parse, or a gauge file it can't write, never blanks your status line; the gauge just stops updating (`stale`, or `missing` if it was never written).

To check a producer, read the file back with the helper. `<skills-dir>` is the directory that contains `quo-setup/` (for example `~/.claude/skills`), and the session id is in the `CLAUDE_CODE_SESSION_ID` environment variable (set inside a Claude Code session's shell):

```bash
# POSIX (bash / zsh):
python3 <skills-dir>/quo-setup/scripts/context_gauge.py read --session-id <id>
```

```powershell
# Windows (PowerShell):
python <skills-dir>\quo-setup\scripts\context_gauge.py read --session-id <id>
```

It prints a percentage, or `no-reading`, `stale`, or `missing`. A malformed file makes it exit non-zero with the problem on stderr. For the reasoning behind the contract, see [the contributor notes](docs/doc-writing-guide.md#the-context-gauge-file-contract).

### Bundled helper scripts

A few skills ship Python helpers in a `scripts/` directory beside their `SKILL.md`. Each skill finds its own helpers at run time, so there is nothing to configure. If an error mentions one, look in `<skill-name>/scripts/` in your skills directory.

## Scope

The 14 skills here are a portable core: they work on any project, language, and platform with only Claude Code, git, Python, and bees. Stack-specific helpers (changelog tooling, license attribution) and infrastructure-specific ones (pastebins, cloud storage) are out of scope, and belong in companion repos.

## Contributing

Issues and pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow's design, its conventions, and the anti-patterns to avoid, and [CLAUDE.md](CLAUDE.md) for the rules every skill change follows. Two of them matter most:

1. **Skills must work on any stack.** Never hard-code a language-specific command or file name in skill prose; read it from the target repo's `CLAUDE.md` `## Build Commands` and `## Documentation Locations` sections.
2. **Skills must work on POSIX and Windows.** Every shell snippet comes in POSIX and PowerShell forms; helpers are Python.

To run the tests: `python3 -m pip install -r requirements-dev.txt`, then `python3 -m pytest tests/` (`python` on Windows).

## License

MIT. See [LICENSE](LICENSE).

## Credits

Built on the [bees](https://github.com/gabemahoney/bees) ticket system by Gabe Mahoney.
