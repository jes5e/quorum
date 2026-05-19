---
id: b.vh4
type: bee
title: /quo-fix-issue upfront 'claude agents' fast-fail check is dead code; misleads about the CLI
parent: null
reference_materials: null
created_at: '2026-05-19T18:07:04.515553'
status: done
schema_version: '0.1'
guid: vh4cb93h6ofjdg1425jxx83gy9h5y1o1
---

## Description

The `/quo-fix-issue` precondition block's "Upfront fast-fail (opportunistic, belt-and-braces)" check is dead code on every modern Claude Code build. The skill at `skills/quo-fix-issue/SKILL.md:34` instructs the orchestrator to run `claude agents` to enumerate registered user subagent types and verify the eight required names (`engineer`, `test-writer`, `doc-writer`, `pm`, `code-reviewer`, `test-reviewer`, `doc-reviewer`, `analyst`) are present, claiming the command "prints one line per agent in the form `  <name> · <model>` under a `User agents:` heading, exits cleanly without spawning an interactive UI, and is safe to invoke from inside a running Claude Code session."

That description does not match what `claude agents` actually does on Claude Code 2.1.145. `claude agents` is the **background-sessions management UI** — `claude agents --help` says "Manage background agents" — and it is interactive-only when stdout is a TTY. When run as a non-TTY child process (the only way `quo-fix-issue` ever invokes it, because the orchestrator's `Bash` calls don't have a TTY on stdout), it exits with: `'claude agents' requires an interactive terminal (stdout is not a TTY) — use 'claude agents --json' for a machine-readable listing.` The `--json` form does exit cleanly, but it returns running Claude Code sessions (objects with `pid`, `cwd`, `sessionId`, `status`), not registered subagent type definitions. There is no `User agents:` heading anywhere in either output mode, and there is no CLI surface at all that enumerates user subagent type markdown files (`~/.claude/agents/*.md` etc.).

## Current behavior

Every `/quo-fix-issue` run shells out to `claude agents`, gets the "requires an interactive terminal" error on stdout, and falls back to the procedural gate per `skills/quo-fix-issue/SKILL.md:46`:

> If `claude agents` itself is unavailable (older Claude Code build, etc.), skip the upfront check — the procedural gate still catches the failure at first dispatch.

The procedural gate works correctly (the orchestrator hard-fails on `Agent type '<name>' not found` at first dispatch), so there is no functional bug at runtime. But the upfront check has never delivered its advertised "catches the missing-restart case upfront and saves the user one wasted dispatch turn" benefit, and the skill text actively misleads any reader about what `claude agents` does.

Reproduction (host, fresh shell — not inside Claude Code):
```
$ claude --version
2.1.145 (Claude Code)
$ claude agents 2>&1
'claude agents' requires an interactive terminal (stdout is not a TTY) — use 'claude agents --json' for a machine-readable listing.
$ claude agents --json | head -10
[
  {
    "pid": 39564,
    "cwd": "/Users/jesseg/code/claude-secure-container",
    "kind": "interactive",
    ...
  },
  ...
]
$ claude agents --help | head -3
Usage: claude agents [options]

Manage background agents
```

The interactive `claude agents` UI (run from a real TTY) is a "start a task in the background" prompt — a UI for dispatching and managing live background `claude` sessions, not a registry view for subagent type markdown files.

## Expected behavior

Either:

1. The upfront check is removed and the procedural gate stands alone (it already works and is described accurately at `skills/quo-fix-issue/SKILL.md:33`), or
2. The upfront check is replaced by a mechanism that actually enumerates registered subagent type definitions (e.g., a direct read of `~/.claude/agents/*.md` and `.claude/agents/*.md` in the current project, grepping for the eight required names).

In either outcome, the skill text should no longer claim `claude agents` does something it does not do.

## Impact

- **Low runtime impact** — the procedural gate already catches the missing-subagent case correctly. No runs are broken by this.
- **Documentation correctness** — the SKILL.md `skills/quo-fix-issue/SKILL.md` text and the SDD reference at `docs/sdd.md:409` both describe `claude agents` as a subagent enumerator. Anyone reading the skill (a contributor, an LLM working on quorum, a user debugging a `/quo-fix-issue` run) will form an incorrect mental model of what the upfront check does and what `claude agents` is for.
- **Wasted bash call** — every `/quo-fix-issue` run spawns a useless `claude agents` shell-out that always fails. Negligible in wall-clock terms but reflects badly in the trace.

## Suggested fix

Pick one of the two directions above. The Analyst pass should weigh the trade-offs:

- Direction 1 (drop the upfront check entirely) is the smallest diff and removes the misleading text. The skill loses the "save one wasted dispatch turn" benefit, but the upfront check was never actually delivering that benefit, so the net change in user experience is zero. Touches `skills/quo-fix-issue/SKILL.md` (the four references at lines 34–46) and `docs/sdd.md:409` (the SDD's "subagent-registry precondition bump" paragraph that names the upfront-fast-fail `claude agents` scan).
- Direction 2 (read agent files directly) keeps the upfront-check intent and actually delivers on it. The check would read `~/.claude/agents/*.md` (user-level) and `.claude/agents/*.md` (project-level) and grep the frontmatter or filename for the eight required names. More moving parts, but it's the only way to verify subagent registration from outside the running Claude Code session.

Files involved:
- `skills/quo-fix-issue/SKILL.md` (lines 34, 38, 43, 46 — the four `claude agents` references in the "Verifying the subagents precondition" block)
- `docs/sdd.md:409` (the "Subagent-registry precondition bump" paragraph that names the broken scan)

## Background and rationale

This was surfaced during a conversation about an observed trace from a `/quo-fix-issue` run inside a docker sandbox (`claude-secure-container`), where the orchestrator's status-line thought read:

> The claude agents CLI requires a TTY here, so I'll fall back to the procedural gate (first-dispatch failure check). All required hives are present. Now querying open issues.

The user asked whether this was correct behavior. Investigation showed:

- The orchestrator's fallback was correct per the skill's own "skip the upfront check — the procedural gate still catches the failure at first dispatch" sentence. No work was lost or done wrong at runtime.
- BUT the underlying premise of the upfront check is wrong: `claude agents` does not do what the skill says it does, and never has on any Claude Code build the user has access to. The skill's claim was reproduced as false on Claude Code 2.1.145 on the host (outside the container), so the TTY constraint is not container-specific — it's how `claude agents` is designed.

Root causes ruled out:

- **Not a container TTY issue.** The same error reproduces on the host, outside any sandbox. `claude agents` requires a TTY by design regardless of execution environment.
- **Not a Claude Code version regression.** `claude agents --help` clearly documents the command as a "Manage background agents" UI, and the `--json` flag's help text says "Print live sessions as a JSON array and exit (for scripting; does not require a TTY)" — "live sessions", not "registered subagents". The command is doing what it was designed to do; the skill is describing a different (nonexistent) command.
- **Not a missing CLI subcommand.** No `claude` subcommand enumerates user subagent type registrations. The skill's described behavior — a "User agents:" heading with `<name> · <model>` lines — does not exist as a CLI surface.

## Decisions and rejected alternatives

The user surfaced two fix directions in the issue write-up (drop the check vs read the agent files). Both are viable; the Analyst pass should decide. A third option — "ask the user to invoke `claude agents` interactively before running `/quo-fix-issue`" — was implicitly rejected by not surfacing it: forcing a TTY context switch is a worse UX than either dropping the check or reading the files programmatically.

## Doc divergence noted

The SDD at `docs/sdd.md:409` (the "Subagent-registry precondition bump" paragraph) describes the same broken upfront-fast-fail `claude agents` scan and inherits the same misleading characterization. The fix for this Issue should update the SDD paragraph in lockstep with the SKILL.md changes — either drop the mention of the upfront-fast-fail scan, or rewrite it to reflect whichever replacement mechanism is chosen.
