---
id: b.9sv
type: bee
title: 'Agent Teams hard requirement: enforce in skills, configure teammateMode in bees-setup, drop fallback claims'
parent: null
egg: null
created_at: '2026-04-30T23:18:36.691498'
status: done
schema_version: '0.1'
guid: 9svamzf6dhkc9qpe65fsmec5tu2r33rr
---

## Description

Two related findings about the bees-workflow's relationship with Claude Code's experimental Agent Teams feature, both surfaced while debugging a `/bees-fix-issue all` run that stalled on the macOS + iTerm2 Split Pane Setup prompt:

1. **Agent Teams is effectively required** for `/bees-execute` and `/bees-fix-issue`, despite docs claiming a single-agent fallback exists. Reading the SKILL.md prose for both skills shows no fallback path is implemented — every step assumes a team can be spawned, `TeamCreate` / `TeamDelete` are called unconditionally, "stay in `delegate` mode" presupposes a team. The "fall back to single-agent execution" claim appears in four documented locations and is aspirational text with no corresponding skill prose.

2. **The default `teammateMode: "auto"` setting traps iTerm2 users.** On macOS + iTerm2 with default settings, the first team spawn triggers an "iTerm2 Split Pane Setup" prompt. Picking Cancel aborts the entire team spawn (returning `Teammate spawn cancelled - iTerm2 setup required`) — *not* declining a visual upgrade. The calling skill stalls with no recovery. A documented [Claude Code verification bug](https://github.com/anthropics/claude-code/issues/27413) compounds the problem: the prompt may re-appear even after `it2` is installed.

These compose into one workflow failure mode: a new bees-workflow user on macOS + iTerm2 follows the README, picks "Skip for now" in `bees-setup`'s Agent Teams prompt thinking it's optional (per the doc claim), then hits a team-required skill, gets the iTerm2 prompt, picks Cancel because the docs implied teams were optional anyway, and ends up with a stalled run and no clear path forward.

Bundled as one ticket because the fixes share files (`bees-execute/SKILL.md`, `bees-fix-issue/SKILL.md`, `bees-setup/SKILL.md`, `README.md`, `CLAUDE.md`) and the same mental model: "Agent Teams is required; `bees-setup` must configure both the env var AND the display backend; downstream skills must hard-fail without the prerequisite."

## Current behavior

**Doc claims that contradict skill prose** (the "fallback exists" claim — four locations to remove): `README.md:45`, `CLAUDE.md:66`, `skills/bees-setup/SKILL.md:90`, `skills/bees-setup/SKILL.md:107`. All four assert the skills "fall back to single-agent execution"; bees-setup:107 surfaces this as a "Skip for now" option.

**Skill prose that proves no fallback exists.** `skills/bees-execute/SKILL.md:131-167` (Step 3 "Form Team to Execute Tasks") and `skills/bees-fix-issue/SKILL.md:102-147` (Step 3 "Assess Complexity and Form Team") have unconditional `TeamCreate`, "spawn the Engineer", "always spawn the Product Manager", "Stay in delegate mode". `force_clean_team.py` recovery is referenced multiple times. `grep -niE "fall.?back|single.?agent|without.?team"` against both skill files returns zero hits.

**No `teammateMode` setup in `bees-setup`.** The skill currently checks for `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (`bees-setup/SKILL.md:67-114`) but does not detect or set `teammateMode`. New users land on Claude Code's default `"auto"`, which triggers the iTerm2 prompt for macOS + iTerm2 users.

**No platform-aware multiplexer guidance.** `bees-setup` doesn't tell macOS + iTerm2 users to install `it2` (`uv tool install it2` per https://github.com/mkusaka/it2) or `tmux` if they want split-pane mode. Users discover the requirement at first team spawn, mid-run.

**No Agent Teams precondition check in execution skills.** `bees-execute` and `bees-fix-issue` `## Preconditions` sections list hive colonization and the two CLAUDE.md sections, but not `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. A user who picked "Skip for now" and then ran one of these skills would hit cryptic team-spawn failures rather than a clean `Run /bees-setup first.` hard-fail.

## Expected behavior

**Docs honestly state Agent Teams is required.** The four "fall back to single-agent execution" claims are removed. Replaced with: *"Agent Teams is required for `/bees-execute` and `/bees-fix-issue`. `/bees-setup` configures both the env var enabling Agent Teams and the `teammateMode` display backend."*

**`bees-setup` gains a `teammateMode` configuration step**, run alongside the existing `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` step. Detects existing setting in `~/.claude/settings.json` and prompts only when unset or `"auto"`:

- If already `"in-process"` or `"tmux"` (user explicit choice), confirm and leave alone.
- If unset or `"auto"`, surface trade-offs via `AskUserQuestion`:
  - **`"in-process"` (Recommended)** — inline status panel only, no multiplexer required, no setup prompts, no abort-on-Cancel failure, works on any terminal.
  - **`"tmux"`** — split-pane mode (the value is misleadingly named per Claude Code docs; auto-detects whether to use tmux or iTerm2 backend depending on terminal).
  - **Leave as `"auto"`** — Claude Code's default; on macOS + iTerm2 triggers the iTerm2 Split Pane Setup prompt with Cancel-aborts-spawn behavior plus the [verification re-prompt bug](https://github.com/anthropics/claude-code/issues/27413). Recommend only if user explicitly prefers Claude Code's default.

**`bees-setup` gates the `"tmux"` option behind terminal detection.** Per Claude Code docs (https://code.claude.com/docs/en/agent-teams), split-pane mode is unsupported in VS Code's integrated terminal, Windows Terminal, and Ghostty. On those terminals, `AskUserQuestion` should not offer `"tmux"`. Defensive default: if terminal detection is ambiguous, skip the `"tmux"` option.

**`bees-setup` verifies multiplexer install when user picks `"tmux"`.** Per terminal: macOS + iTerm2 → `it2` (`uv tool install it2`; iTerm2 3.3.0+ with Python API enabled in Settings → General → Magic). macOS + Terminal.app, Linux → `tmux` (`brew install tmux` / `apt install tmux`). Inside an existing tmux session: tmux is by definition available.

**`bees-execute` and `bees-fix-issue` hard-fail without Agent Teams.** Add a precondition: read `~/.claude/settings.json` for `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. If not `"1"`, hard-fail with `Run /bees-setup first.` plus a one-line note. Match the existing precondition-check pattern.

(Suggested fix, files to modify, out-of-scope, and adjacent findings continue in next chunk via append-ticket-body.)
## Impact

**Onboarding correctness.** A new user following the README and picking "Skip for now" currently lands in a state where the next skill they invoke fails opaquely. Closing the gap turns that into either a clean hard-fail directing them back to `/bees-setup`, or a smooth flow where setup configured everything correctly upfront.

**iTerm2-specific dead end.** Even users who *did* enable Agent Teams hit the iTerm2 Split Pane Setup prompt mid-run on first team spawn. Picking Cancel aborts the run; picking Install or Use tmux disrupts flow with a setup task they didn't expect. Pre-configuring `teammateMode: "in-process"` during setup avoids the prompt entirely.

**Cross-platform claim integrity.** The CLAUDE.md / CONTRIBUTING.md "tmux not required for the portable core" claim is currently *technically* true at the bees-workflow layer but practically misleading because Claude Code's team-display layer has its own multiplexer behavior. Recommending `"in-process"` as the bees-workflow default makes the portability claim genuinely true everywhere.

**Doc honesty.** The "fall back to single-agent execution" claim is wrong. Users and contributors alike read it and reason from it. Fixing it removes a load-bearing falsehood from the project's docs.

## Suggested fix

**Phase 1 — strip aspirational fallback claims.** Edit the four locations:
- `README.md:45` — rewrite "Strongly recommended: enable Agent Teams" → "Required: enable Agent Teams". Body explains `/bees-setup` configures it.
- `CLAUDE.md:66` — drop the "fall back to single-agent execution" sentence and the "any edit must keep both code paths working" requirement. Single code path now.
- `skills/bees-setup/SKILL.md:90` — rewrite Agent Teams introduction; drop the "without it, the skills fall back" sentence.
- `skills/bees-setup/SKILL.md:107` — "Skip for now" option becomes either removed (forcing enable) or reworded to "Skip for now — `/bees-execute` and `/bees-fix-issue` will not function until you enable this; you can re-run `/bees-setup` later". Implementer's call which.

**Phase 2 — add precondition check to consumer skills.** `skills/bees-execute/SKILL.md` and `skills/bees-fix-issue/SKILL.md` `## Preconditions` each gain a new bullet:

> - `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `\"1\"` in either `~/.claude/settings.json` or the shell environment. The skill spawns a team unconditionally; without Agent Teams enabled, team-creation tools are unavailable and the skill cannot proceed.

Verification approach: agent reads `~/.claude/settings.json` and checks the value, falling back to env var. If neither is `\"1\"`, hard-fail with `Run /bees-setup first.`.

**Phase 3 — `bees-setup` adds a `teammateMode` configuration step.** After the existing Agent Teams enable step:

1. Read `~/.claude/settings.json`. Check `teammateMode`.
2. If set to `\"in-process\"` or `\"tmux\"`, confirm to user and skip.
3. If unset or `\"auto\"`:
   - Detect terminal via `\$TERM_PROGRAM` (`iTerm.app`, `Apple_Terminal`, `WarpTerminal`, `ghostty`, `WezTerm`, `vscode`), `\$WT_SESSION` (Windows Terminal), `\$TMUX` (already inside tmux), or `\$TERM` (`alacritty`). Defensive — if no recognizable terminal, skip the `\"tmux\"` option.
   - Build option list: always `\"in-process\"` (Recommended) and `\"auto\"` (with iTerm2 warning); add `\"tmux\"` if terminal supports split panes.
   - Surface via `AskUserQuestion`. Apply choice.
4. If user picks `\"tmux\"`, verify backend installed for their terminal and offer to install via the appropriate package manager.

Apply chosen value to `~/.claude/settings.json` using the structured-edit pattern in `CONTRIBUTING.md` `## Skill conventions` (Python one-liner with `json.load` / `json.dump` and atomic write — do not text-edit). Merge without disturbing other settings, same as the existing `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` set.

**Phase 4 — README gains a `## Display backend` section.** Document the three valid `teammateMode` values, what each does, and that bees-workflow recommends `\"in-process\"` for smooth onboarding. Quote the docs' enumeration. Note the macOS + iTerm2 + `\"auto\"` failure mode.

## Files to modify

- `README.md` — Phase 1 (title + body), Phase 4 (new section).
- `CLAUDE.md` — Phase 1.
- `skills/bees-setup/SKILL.md` — Phase 1, Phase 3.
- `skills/bees-execute/SKILL.md` — Phase 2.
- `skills/bees-fix-issue/SKILL.md` — Phase 2.

## Out of scope

- **Cross-platform manual testing during implementation.** Implementer doesn't need every platform/terminal combination. Terminal detection is defensive — unknown terminals default to skipping `\"tmux\"`. Implementation can be validated on whichever terminals the implementer has (typically macOS + iTerm2 + Terminal.app). Other platforms can be tested by users who hit issues, who file follow-ups.
- **Implementing an actual single-agent fallback** in `bees-execute` and `bees-fix-issue`. Rejected in the discussion that led to this ticket — too much code and ongoing maintenance for a workflow whose design intent is parallel team execution. If revisited, file separately.
- **Filing the upstream Claude Code verification bug** ([#27413](https://github.com/anthropics/claude-code/issues/27413)). Already exists upstream; we work around by recommending `\"in-process\"`.
- **Documenting cross-terminal behavior of `teammateMode: \"tmux\"` on unsupported terminals** (Windows Terminal, Ghostty, VS Code integrated). Claude Code docs are unclear; our defensive logic sidesteps the gap. If implementer wants to file an upstream docs issue against `anthropics/claude-code`, optional.

## Adjacent findings (note, do not bundle)

- **Existing tickets `b.ap8` and `b.ctf`** are separate correctness fixes in the same skill files. Independent — no overlap. Implementer should be aware that those may land first or alongside; rebase carefully if they touch overlapping lines.
- **The `it2` install command** is `uv tool install it2` per https://github.com/mkusaka/it2. The Claude Code iTerm2 prompt itself uses `uvx` (one-shot ephemeral); the persistent install for shell use is `uv tool install`. Either ends with `it2` reachable, but the persistent form is what bees-setup should recommend.
- **Recently-added rules in `CONTRIBUTING.md` `## Skill conventions` (structured file edits) and `docs/doc-writing-guide.md` `## OS-conditional shell blocks` (no shell variables across snippet boundaries)** are project rules that apply to this implementation. The `~/.claude/settings.json` edit must follow the JSON-edit pattern; multi-snippet shell flows must inline values rather than rely on variable persistence.
