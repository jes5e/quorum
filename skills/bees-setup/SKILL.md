---
name: bees-setup
description: Configure hives for the bees workflow
---

## Overview

Configure a repo for the bees workflow. Sets up hives, writes a `## Documentation Locations` section and a `## Build Commands` section in CLAUDE.md, and (optionally) bootstraps baseline PRD/SDD docs by exploring the existing codebase.

**This skill is safe to re-run.** Each section detects existing configuration and only prompts where something is missing, stale, or you ask to change it. If you skipped doc bootstrap on the first run and want to add docs later, re-running setup re-offers the bootstrap option.

The bees workflow has two entry points for new work, both supported by this setup:
- **`/bees-plan`** — interactive scope discovery for an idea, refactor, or feature without finalized specs
- **`/bees-plan-from-specs`** — express path when you already have a finalized PRD and SDD on disk

## Valid configuration

The repo must have the following hives available and configured with these child tiers and valid status values:

### Issues Hive
Child tiers:
none

Status values:
- open — open issue
- done — completed

### Plans Hive
Child tiers:
- t1 — Epic / Epics
- t2 — Task / Tasks
- t3 — Subtask / Subtasks

Status values:
- drafted — not fully documented, not ready to work
- ready — fully documented, ready to work
- in_progress — actively being worked on
- done — completed

The Plans hive is a **top-level** hive. It is not nested inside an Ideas hive.

## Instructions

### Prerequisites

#### bees CLI

Verify bees is available on PATH. The exact lookup command depends on the host shell:

```bash
# POSIX (bash / zsh — macOS, Linux, WSL):
which bees

# Windows (PowerShell):
Get-Command bees -ErrorAction SilentlyContinue

# Windows (cmd.exe):
where bees
```

If bees is not present, install it:

```bash
pipx install bees-md
```

`pipx` itself can be installed several ways:

```bash
# macOS:
brew install pipx

# Linux (Debian/Ubuntu):
sudo apt install pipx

# Linux (Fedora):
sudo dnf install pipx

# Windows (scoop):
scoop install pipx

# Windows (or any platform via Python):
python -m pip install --user pipx
```

bees-md requires Python 3.10+. After install, the bees binary lives under the user's local-binary directory: `~/.local/bin/bees` on POSIX, `%USERPROFILE%\.local\bin\bees.exe` (or wherever pipx put it) on Windows. Documentation: https://github.com/gabemahoney/bees

### Fast-path detection (new-machine re-registration)

The `.bees/<hive>/` directories are committed to the repo, but the per-machine `~/.bees/config.json` is not. When a user clones a fully set-up repo onto a new machine (or a teammate clones it for the first time), the on-disk hive markers are present but the per-machine bees config has no scope entry for this repo. Result: every bees command behaves as if no tickets exist, and downstream skills hard-fail with `Run /bees-setup first.`

The full slow-path walk-through is wrong for this case — CLAUDE.md is already correct, the hives already exist on disk, the only thing missing is per-machine registration. The fast path detects this and re-registers in one or two prompts, leaving CLAUDE.md untouched.

#### Detect

Run the bundled detector script with the target repo's absolute path. The script lives at `<this skill's base directory>/scripts/detect_fast_path.py` (where "this skill" is `bees-setup` — see *Resolve bundled helper script paths* below for the same runtime-resolution convention used by the egg resolver). Replace `<bees-setup-base-dir>` with the literal path from the skill invocation header:

```bash
# POSIX (bash / zsh):
python3 "<bees-setup-base-dir>/scripts/detect_fast_path.py" --repo-root "$(pwd)"
```

```powershell
# Windows (PowerShell):
python "<bees-setup-base-dir>\scripts\detect_fast_path.py" --repo-root "$((Get-Location).Path)"
```

The script emits a JSON payload to stdout:

```json
{
  "repo_root": "/abs/path/to/repo",
  "on_disk_hives": [{"name": "issues", "path": "/abs/path/to/repo/.bees/issues"}, {"name": "plans", "path": "/abs/path/to/repo/.bees/plans"}],
  "any_registered_for_repo": false,
  "registered_hive_names": [],
  "claude_md_path": "/abs/path/to/repo/CLAUDE.md",
  "claude_md_doc_locations_set_up": true,
  "claude_md_build_commands_set_up": true,
  "fast_path_eligible": true
}
```

`fast_path_eligible` is true iff **all three** of the following hold:

1. At least one `.bees/<hive>/.hive/identity.json` marker exists in the repo (`on_disk_hives` non-empty).
2. None of the registered scopes in `~/.bees/config.json` cover the current repo path (`any_registered_for_repo` is false).
3. CLAUDE.md already contains both `## Documentation Locations` and `## Build Commands` sections with all required contract bullets present (`claude_md_doc_locations_set_up` and `claude_md_build_commands_set_up` are both true). Empty values for individual rows are acceptable — the user may have legitimately skipped a guide; what matters is that the section was previously walked through and the contract keys are in place.

If `fast_path_eligible` is **false**, fall through to the existing slow path starting at *Per-machine Claude Code settings*; if those are already configured, the slow path continues to *Resolve bundled helper script paths* — there is no behavior change for first-time setup or for already-fully-configured machines.

If `fast_path_eligible` is **true**, run the actions below.

#### Diagnose

Print this paragraph to the user verbatim:

> Looks like this repo was already set up for bees on another machine. The on-disk hive markers are here but they're not registered in your machine's bees config. I can re-register them for you and you'll be ready to go. CLAUDE.md will not be touched.

#### Re-register each on-disk hive

For each entry in `on_disk_hives`, branch on the hive name:

**Canonical hives (`issues` and `plans`)** — apply the canonical defaults verbatim. The scope glob is the repo root with a trailing `/**`. The `--egg-resolver` path is `<bees-setup-base-dir>/scripts/file_list_resolver.py` (see *Egg Resolver* below for the same convention). Inline the literal at the call site — do not store it in a shell variable across snippets.

**Before the first `bees colonize-hive` call**, verify the resolver script actually exists. A corrupted or partial install would otherwise register hives pointing at a non-existent resolver:

```bash
# POSIX (bash / zsh):
test -f "<bees-setup-base-dir>/scripts/file_list_resolver.py" || { echo "file_list_resolver.py not found at <bees-setup-base-dir>/scripts/file_list_resolver.py — bees-workflow install is incomplete. Fall through to the slow path (skip the fast path entirely) and tell the user to re-install per the README."; exit 1; }
```

```powershell
# Windows (PowerShell):
if (-not (Test-Path "<bees-setup-base-dir>\scripts\file_list_resolver.py")) { Write-Error "file_list_resolver.py not found at <bees-setup-base-dir>\scripts\file_list_resolver.py — bees-workflow install is incomplete. Fall through to the slow path (skip the fast path entirely) and tell the user to re-install per the README." ; exit 1 }
```

Then run the per-hive registration:

```bash
# POSIX (bash / zsh) — for each issues hive:
bees colonize-hive --name issues --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>/scripts/file_list_resolver.py"
bees set-status-values --scope hive --hive issues --status-values '["open","done"]'

# POSIX (bash / zsh) — for each plans hive:
bees colonize-hive --name plans --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>/scripts/file_list_resolver.py"
bees set-types --scope hive --hive plans --child-tiers '{"t1":["Epic","Epics"],"t2":["Task","Tasks"],"t3":["Subtask","Subtasks"]}'
bees set-status-values --scope hive --hive plans --status-values '["drafted","ready","in_progress","done"]'
```

```powershell
# Windows (PowerShell) — for each issues hive:
bees colonize-hive --name issues --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>\scripts\file_list_resolver.py"
bees set-status-values --scope hive --hive issues --status-values '["open","done"]'

# Windows (PowerShell) — for each plans hive:
bees colonize-hive --name plans --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>\scripts\file_list_resolver.py"
bees set-types --scope hive --hive plans --child-tiers '{"t1":["Epic","Epics"],"t2":["Task","Tasks"],"t3":["Subtask","Subtasks"]}'
bees set-status-values --scope hive --hive plans --status-values '["drafted","ready","in_progress","done"]'
```

**Unknown hive names** (anything other than `issues` or `plans`) — the canonical defaults do not apply. Do **not** silently re-register with assumed values. Walk the user through registration **inline** in the fast path (the slow path's *Hive Configuration* section is structured around colonizing *missing* hives — wrong shape here, since the on-disk path is already known and only the per-machine config bits are missing).

For each unknown hive, do this inline:

1. Use `AskUserQuestion` to confirm whether to re-register this hive now. Options: "Yes, re-register it" / "Skip this hive". If skipped, note to the user that downstream skills won't see this hive on this machine, and continue to the next on-disk hive.

2. If yes, ask the user for the **child tiers** in prose (free-text — `AskUserQuestion` is multi-choice only, do **not** invent fake "Other" options for free-text answers). Phrase it like:

   > "What child tiers should `<hive-name>` have? Reply with either:
   > - `none` (this hive holds leaf tickets only — like the `issues` hive), OR
   > - a JSON object mapping tier keys (`t1`, `t2`, `t3`) to display names, e.g. `{\"t1\": [\"Epic\", \"Epics\"], \"t2\": [\"Task\", \"Tasks\"]}`."

   Wait for the user's reply in the next turn.

3. Then ask for the **status values** in prose, also free-text:

   > "What status values should `<hive-name>` have? Reply with a JSON array of status names in workflow order, e.g. `[\"open\", \"done\"]` or `[\"drafted\", \"ready\", \"in_progress\", \"done\"]`."

   Wait for the user's reply in the next turn.

4. With the answers in hand, register the hive directly. Use the on-disk `<discovered-path>` from the detector output — do **not** re-prompt the user for it. Replace `<bees-setup-base-dir>` with the literal path from the skill invocation header:

   ```bash
   # POSIX (bash / zsh):
   bees colonize-hive --name <hive-name> --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>/scripts/file_list_resolver.py"
   # If user gave child tiers as a JSON object (not "none"):
   bees set-types --scope hive --hive <hive-name> --child-tiers '<user-supplied-json>'
   bees set-status-values --scope hive --hive <hive-name> --status-values '<user-supplied-json>'
   ```

   ```powershell
   # Windows (PowerShell):
   bees colonize-hive --name <hive-name> --path "<discovered-path>" --scope "<repo-root>/**" --egg-resolver "<bees-setup-base-dir>\scripts\file_list_resolver.py"
   # If user gave child tiers as a JSON object (not "none"):
   bees set-types --scope hive --hive <hive-name> --child-tiers '<user-supplied-json>'
   bees set-status-values --scope hive --hive <hive-name> --status-values '<user-supplied-json>'
   ```

   If the user replied `none` for child tiers, omit the `bees set-types` call entirely (matches the `issues` hive shape).

#### Configure per-machine Claude Code settings (condensed prompt)

Read `~/.claude/settings.json` (or `%USERPROFILE%\.claude\settings.json` on Windows). Check whether `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `"1"` and whether `teammateMode` is set to `"in-process"` or `"tmux"` (any explicit user choice).

- **If both are already set**: print `"Per-machine Claude Code settings already configured — leaving them alone."` and skip ahead to *Confirm and exit*.
- **If either or both are missing**: present a single combined `AskUserQuestion` confirming both at once with sensible defaults — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"` (required by `bees-execute` / `bees-fix-issue`) and `teammateMode = "in-process"` (the recommended default — works on every terminal, no setup-prompt surprises).

  > "Your per-machine Claude Code settings need two values to support `bees-execute` / `bees-fix-issue`. I can set both at once with the recommended defaults, or walk through each setting in detail."
  >
  > Options:
  > 1. **Set both with recommended defaults (Recommended)** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="1"`, `teammateMode="in-process"`.
  > 2. **Walk through each setting in detail** — fall through to the slow path's *Per-machine Claude Code settings* section instead of the condensed confirm.

  If option 1: write each missing setting using the **shared Python one-liner** in *Helper: write a single key to `~/.claude/settings.json`* below — one call per missing key.

  If option 2: after completing the slow path's *Per-machine Claude Code settings* section, jump back up to *Confirm and exit* in the fast-path branch above.

#### Confirm and exit

Print: `"Re-registered N hives. You're ready to go."` (where N is the count of hives processed above), then use `AskUserQuestion`:

> "Setup complete. The fast path skipped the full walk-through because your repo was already configured. Anything else?"
>
> Options:
> 1. **Exit now (Recommended)** — most users on a new machine want exactly this.
> 2. **Continue with the full setup walk anyway** — escape hatch for users who actually want to reconfigure CLAUDE.md sections, hive paths, build commands, etc. Falls through to *Resolve bundled helper script paths* below.

If option 1: stop. **Do not** modify CLAUDE.md, do not walk Documentation Locations, do not walk Build Commands. The repo state is already correct on disk and the per-machine bits are now in place.

If option 2: continue with the existing slow path starting at *Resolve bundled helper script paths* (*Per-machine Claude Code settings* was already configured by the condensed prompt above; we skip ahead to the next slow-path section).

### Per-machine Claude Code settings

The two settings below — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` and `teammateMode` — live in the user's per-machine Claude Code settings file (`~/.claude/settings.json` on POSIX, `%USERPROFILE%\.claude\settings.json` on Windows). They are not committed to a repo, so a fresh machine always needs them set even if the repo itself is fully configured. Both fast-path and slow-path setups configure them; the fast path uses a condensed single-prompt confirm, the slow path walks through each one in detail.

#### Claude Code Agent Teams (required)

`bees-execute` and `bees-fix-issue` use Claude Code's **Agent Teams** feature to run Engineer + Test Writer + Doc Writer + PM concurrently on each Task instead of in sequence. **Agent Teams is required for both skills** — they spawn a team unconditionally and will hard-fail with `Run /bees-setup first.` if Agent Teams is not enabled. `/bees-setup` configures both the env var that enables Agent Teams (this step) and the `teammateMode` display backend (the next step).

**Detect current state.** Read the user's Claude Code settings file:

- POSIX: `~/.claude/settings.json`
- Windows: `%USERPROFILE%\.claude\settings.json`

Check whether `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` is set to `"1"`.

**If already enabled**: confirm to the user ("Agent Teams is enabled — `bees-execute` and `bees-fix-issue` will run their teams in parallel.") and move on.

**If not enabled (or the settings file doesn't exist)**: don't silently skip. Explain the requirement and offer to enable it via `AskUserQuestion`:

> "Agent Teams is currently disabled. `/bees-execute` and `/bees-fix-issue` require it — they spawn a team unconditionally and hard-fail without it. The setting is `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = '1'` in your Claude Code user settings file. Want me to enable it now?"
>
> Options:
> 1. **Yes, enable it (Recommended)** — I'll add the setting to your settings file (creating it if it doesn't exist). Takes effect on your next Claude Code session.
> 2. **Skip for now** — `/bees-execute` and `/bees-fix-issue` will not function until you enable this; you can re-run `/bees-setup` later to enable.
> 3. **Show me what to add and I'll do it myself** — print the JSON snippet and file path, then continue.

If option 1: show the user a before/after diff, then write the setting using the **shared Python one-liner** documented below in *Helper: write a single key to `~/.claude/settings.json`* (key `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`, value `"1"`). Remind the user: "This takes effect on your next Claude Code session — restart Claude Code when you have a moment."

If option 2: continue setup; Agent Teams remains disabled. Note to the user that `/bees-execute` and `/bees-fix-issue` will hard-fail until they re-run `/bees-setup` (which will re-detect and re-offer) or edit the settings file by hand.

If option 3: print the exact addition (`"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"`) and the file path, then continue setup.

> **Optional later-installs not needed for the core portable workflow:**
> The skills `bees-fleet`, `bees-worktree-add`, and `bees-worktree-rm` require **tmux** for terminal session management. If you do not plan to use those skills, you do not need tmux. If you later install or invoke any of them, install tmux at that point (`brew install tmux` on macOS / `sudo apt install tmux` on Debian-Ubuntu Linux / install via WSL on Windows — tmux has no native Windows port). The core flow — `/bees-plan` or `/bees-plan-from-specs` → `/bees-breakdown-epic` → `/bees-execute` → `/bees-fix-issue` — does not need tmux and works on native Windows PowerShell.

#### teammateMode display backend

Agent Teams routes teammate output through a "display backend" controlled by `teammateMode` in `~/.claude/settings.json` (or `%USERPROFILE%\.claude\settings.json` on Windows). Pre-configuring it during setup avoids mid-run setup prompts that can abort a team spawn — most notably the iTerm2 Split Pane Setup prompt that ships with Claude Code's default `"auto"` mode on macOS + iTerm2, where picking Cancel aborts the team spawn entirely (a known re-prompt bug compounds the problem: https://github.com/anthropics/claude-code/issues/27413).

**Detect current state.** Read the same settings file as the previous step. Look up `teammateMode`.

- **If already set to `"in-process"` or `"tmux"`** (an explicit user choice): confirm to the user (`"teammateMode is already set to <value> — leaving it alone."`) and move on.
- **If unset, missing, or set to `"auto"`**: detect the user's terminal, then prompt for a choice (the steps below).

##### Detect the terminal

Terminal detection is best-effort and defensive. Read these environment variables and map them to the table that follows. When the terminal is unknown or ambiguous, do **not** offer the `"tmux"` option in the prompt below.

```bash
# POSIX (bash / zsh):
echo "TERM_PROGRAM=${TERM_PROGRAM:-}"
echo "TMUX=${TMUX:-}"
echo "TERM=${TERM:-}"
echo "WT_SESSION=${WT_SESSION:-}"
```

```powershell
# Windows (PowerShell):
"TERM_PROGRAM=$($env:TERM_PROGRAM)"
"TMUX=$($env:TMUX)"
"TERM=$($env:TERM)"
"WT_SESSION=$($env:WT_SESSION)"
```

| Environment cue | Terminal | Supports split panes? |
|---|---|---|
| `$TMUX` non-empty | already inside a tmux session | yes (tmux available by definition) |
| `TERM_PROGRAM=iTerm.app` | macOS iTerm2 | yes (via `it2` backend) |
| `TERM_PROGRAM=Apple_Terminal` | macOS Terminal.app | yes (via tmux) |
| `TERM_PROGRAM=WezTerm` | WezTerm | yes (via tmux) |
| `TERM_PROGRAM=WarpTerminal` | Warp | yes (via tmux) |
| `TERM=alacritty` | Alacritty | yes (via tmux) |
| `TERM_PROGRAM=ghostty` | Ghostty | **no** — split-pane unsupported per Claude Code docs |
| `TERM_PROGRAM=vscode` | VS Code integrated terminal | **no** — split-pane unsupported per Claude Code docs |
| `$WT_SESSION` non-empty | Windows Terminal | **no** — split-pane unsupported per Claude Code docs |
| (none of the above) | unknown terminal | unknown — skip the `"tmux"` option |

Reference: https://code.claude.com/docs/en/agent-teams.

##### Prompt the user

Present an `AskUserQuestion`. Always include options 1 and 3; include option 2 only when the detection table above flagged the terminal as supporting split panes.

> "How should Claude Code display teammate output during `/bees-execute` and `/bees-fix-issue` runs? `bees-workflow` recommends `"in-process"` for smooth onboarding."
>
> Options:
> 1. **`"in-process"` (Recommended)** — Inline status panel only; no terminal multiplexer required, no setup prompts, no abort-on-Cancel surprises. Works on every terminal.
> 2. **`"tmux"`** — Split-pane mode. Each teammate gets its own pane. Despite the value name, Claude Code chooses the actual backend per-terminal: `it2` on iTerm2, `tmux` everywhere else. (Only shown when the detected terminal supports split panes.)
> 3. **Leave as `"auto"`** — Claude Code's default. On macOS + iTerm2 this triggers an iTerm2 Split Pane Setup prompt on first team spawn; picking Cancel aborts the team spawn (and the re-prompt bug noted above can resurface even after the backend is installed). Recommend only if the user explicitly prefers Claude Code's default.

##### Apply the choice

Mirror the UX of the Agent Teams enable step: **read the existing JSON, show the user a before/after diff (the only changed line will be `"teammateMode": "<old>"` → `"teammateMode": "<new>"`, or a single new line on a fresh file), and confirm via `AskUserQuestion` before writing.** This keeps the user in the loop for any change to their settings file and matches the muscle memory the previous step established.

After confirmation, write the chosen value to the settings file using the **shared Python one-liner** documented below in *Helper: write a single key to `~/.claude/settings.json`*. Pass `teammateMode` as the key and the user's chosen value (`"in-process"`, `"tmux"`, or `"auto"`) as the value. Inline the literal at the call site — do not rely on a shell variable carried over from an earlier snippet. Remind the user: "This takes effect on your next Claude Code session — restart Claude Code when you have a moment."

##### If the user picked `"tmux"`, verify the backend is installed

Claude Code's `"tmux"` mode picks a per-terminal backend. Verify the appropriate one and offer to install if missing:

- **macOS + iTerm2** → `it2` backend. Requires iTerm2 3.3.0+ with the Python API enabled (Settings → General → Magic). Persistent install: `uv tool install it2` (per https://github.com/mkusaka/it2). If `uv` itself is missing, `brew install uv` first.
- **macOS + Terminal.app, Linux** → `tmux`. Install: `brew install tmux` on macOS, `sudo apt install tmux` on Debian/Ubuntu, `sudo dnf install tmux` on Fedora.
- **Already inside a tmux session** (`$TMUX` non-empty): tmux is available by definition — no install needed.

Verify presence:

```bash
# POSIX (bash / zsh) — iTerm2 backend (run on macOS + iTerm2):
which it2 || echo "it2 not installed — run 'uv tool install it2' (and 'brew install uv' first if uv is missing)"

# POSIX (bash / zsh) — tmux backend (macOS Terminal.app, Linux, WezTerm, etc.):
which tmux || echo "tmux not installed — run 'brew install tmux' (macOS) or 'sudo apt install tmux' (Debian/Ubuntu) or 'sudo dnf install tmux' (Fedora)"
```

```powershell
# Windows (PowerShell) — tmux backend:
if (-not (Get-Command tmux -ErrorAction SilentlyContinue)) {
    Write-Host "tmux not available on native Windows — install inside WSL if you need split-pane mode"
}
```

If the backend is missing, offer to install via `AskUserQuestion`. If the user declines, warn that team spawn will fail until the backend is available, and offer to fall back to `"in-process"` instead.

#### Helper: write a single key to `~/.claude/settings.json`

Both subsections above (and the fast-path branch below) write a single top-level key into the user's Claude Code settings file. Use this shared Python one-liner — direct text editing has no atomicity story and corrupts JSON on a wrong escape. Pass the key name and value as the second and third positional arguments so neither has to round-trip through a shell variable across snippet boundaries (each Bash tool invocation is a fresh shell).

The script:

1. Reads the existing JSON, or starts from `{}` if the file does not exist. Bails out with a clear error if the file exists but is not valid JSON — do not silently overwrite a corrupt-but-recoverable settings file.
2. Sets the named key to the chosen value, leaving every other key untouched.
3. Writes the result back atomically (tempfile in the same directory + `os.replace`).

```bash
# POSIX (bash / zsh):
python3 -c '
import json, os, sys, tempfile
p, key, new_value = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(p):
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {p} is not valid JSON ({e}). Fix or remove the file by hand, then re-run /bees-setup.", file=sys.stderr)
        sys.exit(1)
data[key] = new_value
parent = os.path.dirname(os.path.abspath(p)) or "."
os.makedirs(parent, exist_ok=True)
fd, tmp = tempfile.mkstemp(dir=parent, prefix=".settings.json.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise
print(f"Set {key}={new_value} in {p}")
' "$HOME/.claude/settings.json" "<key>" "<value>"
```

```powershell
# Windows (PowerShell):
# IMPORTANT: use a single-quoted here-string @'...'@ around the Python source so
# PowerShell does NOT expand $variables inside the script body before invoking Python.
$pyScript = @'
import json, os, sys, tempfile
p, key, new_value = sys.argv[1], sys.argv[2], sys.argv[3]
data = {}
if os.path.exists(p):
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {p} is not valid JSON ({e}). Fix or remove the file by hand, then re-run /bees-setup.", file=sys.stderr)
        sys.exit(1)
data[key] = new_value
parent = os.path.dirname(os.path.abspath(p)) or "."
os.makedirs(parent, exist_ok=True)
fd, tmp = tempfile.mkstemp(dir=parent, prefix=".settings.json.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, p)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise
print(f"Set {key}={new_value} in {p}")
'@
python -c $pyScript "$env:USERPROFILE\.claude\settings.json" "<key>" "<value>"
```

Replace `<key>` and `<value>` at the call site with the literals for the setting being written (e.g., `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS"` `"1"` for Agent Teams; `"teammateMode"` `"in-process"` for the display backend). Inline the literals — do not rely on a shell variable carried over from an earlier snippet.

---

### Resolve bundled helper script paths

This skill set works in two install modes:
- **Global install** — skills live under `~/.claude/skills/<skill-name>/` (per-user, recommended for single-user machines)
- **Per-project install** — skills live under `<repo>/.claude/skills/<skill-name>/`

Helper scripts (`file_list_resolver.py`, `detect_fast_path.py`, `force_clean_team.py`, `check_agent_teams.py`) ship bundled inside their owning skill's `scripts/` directory. Each skill that needs a bundled script computes the path at runtime from its own base directory — no probing, no persistence to CLAUDE.md.

The skill invocation header at session start tells Claude where this skill lives, e.g.:

```
Base directory for this skill: /Users/.../.claude/skills/bees-setup
```

`bees-setup`'s own bundled scripts (`file_list_resolver.py`, `detect_fast_path.py`) live at `<this skill's base directory>/scripts/<name>.py`. The `file_list_resolver.py` path is the absolute path passed to `bees colonize-hive --egg-resolver` below. No CLAUDE.md section is written for any helper — sibling skills resolve their own bundled scripts the same way (e.g., `bees-execute` computes `<bees-execute base>/scripts/force_clean_team.py` and `<bees-execute base>/scripts/check_agent_teams.py`; `bees-fix-issue` computes `<bees-fix-issue base>/../bees-execute/scripts/force_clean_team.py` and `<bees-fix-issue base>/../bees-execute/scripts/check_agent_teams.py`).

**Migration.** Earlier versions of `bees-setup` wrote a `## Skill Paths` section to CLAUDE.md containing absolute machine-local paths. That section was removed because committing per-machine paths to a tracked file broke multi-engineer collaboration. If the target repo's CLAUDE.md still has a `## Skill Paths` section from an earlier setup run, delete it as part of this run — the section is no longer used by any skill, and leaving it behind keeps the broken paths in git history.

Use the Python one-liner below from the repo root — direct text editing has no atomicity story and corrupts the file on a wrong escape, and an unanchored `sed`/regex deletion would mis-handle a `## ` heading that appears *inside* a fenced code block (e.g., a doc example) and either eat too little or too much. The script:

1. Reads CLAUDE.md (returns early as a no-op if the file doesn't exist yet — fresh repos hit this migration step before `Documentation Locations` creates the file).
2. Walks lines, tracking whether the cursor is inside a ```` ``` ```` fenced block.
3. Detects `^## ` section boundaries that occur **outside** fenced blocks — line-anchored boundary semantics with code-fence awareness layered on top, without `re.split`'s blind-spot for fenced content.
4. Drops the block whose heading line is exactly `## Skill Paths`.
5. Writes the result back atomically (tempfile in the same directory + `os.replace`, never an in-place edit).

```bash
# POSIX (bash / zsh):
python3 -c '
import sys, tempfile, os
p = sys.argv[1]
if not os.path.exists(p):
    print("CLAUDE.md does not exist yet — nothing to migrate."); sys.exit(0)
with open(p, encoding="utf-8") as f: lines = f.readlines()
out, in_fence, skipping, removed = [], False, False, False
for line in lines:
    stripped = line.rstrip("\r\n")
    if stripped.startswith("```"):
        in_fence = not in_fence
        if not skipping: out.append(line)
        continue
    if not in_fence and stripped.startswith("## "):
        if stripped.rstrip() == "## Skill Paths":
            skipping, removed = True, True
            continue
        if skipping: skipping = False
    if not skipping: out.append(line)
new = "".join(out)
if not removed:
    print("No ## Skill Paths section found — nothing to do."); sys.exit(0)
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(p)), prefix=".CLAUDE.md.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(new)
    os.replace(tmp, p)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise
print("Removed ## Skill Paths section from CLAUDE.md.")
' CLAUDE.md
```

```powershell
# Windows (PowerShell):
# IMPORTANT: use a single-quoted here-string @'...'@ around the Python source so
# PowerShell does NOT expand $variables inside the script body before invoking Python.
$pyScript = @'
import sys, tempfile, os
p = sys.argv[1]
if not os.path.exists(p):
    print("CLAUDE.md does not exist yet — nothing to migrate."); sys.exit(0)
with open(p, encoding="utf-8") as f: lines = f.readlines()
out, in_fence, skipping, removed = [], False, False, False
for line in lines:
    stripped = line.rstrip("\r\n")
    if stripped.startswith("```"):
        in_fence = not in_fence
        if not skipping: out.append(line)
        continue
    if not in_fence and stripped.startswith("## "):
        if stripped.rstrip() == "## Skill Paths":
            skipping, removed = True, True
            continue
        if skipping: skipping = False
    if not skipping: out.append(line)
new = "".join(out)
if not removed:
    print("No ## Skill Paths section found — nothing to do."); sys.exit(0)
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(p)), prefix=".CLAUDE.md.", suffix=".tmp")
try:
    with os.fdopen(fd, "w", encoding="utf-8") as f: f.write(new)
    os.replace(tmp, p)
except Exception:
    if os.path.exists(tmp): os.unlink(tmp)
    raise
print("Removed ## Skill Paths section from CLAUDE.md.")
'@
python -c $pyScript CLAUDE.md
```

If the script printed "CLAUDE.md does not exist yet — nothing to migrate." or "No ## Skill Paths section found — nothing to do.", skip ahead. Otherwise (the section was actually removed), mention to the user: "Removed obsolete `## Skill Paths` section from CLAUDE.md — paths are now resolved at runtime per-machine. Consider squashing this change with other in-flight work; don't push the delete on its own if the section was already pushed earlier."

### Egg Resolver

The egg resolver lets a Plan Bee's `egg` field point at one or more source documents on disk (PRD, SDD, etc.). Downstream skills (`/bees-execute`, `/bees-breakdown-epic`) read these files as the authoritative source for the work.

When colonizing hives, pass the resolved path to `file_list_resolver.py` as the `--egg-resolver` flag to `bees colonize-hive`. The path is `<this skill's base directory>/scripts/file_list_resolver.py` (where "this skill" is `bees-setup` — see the section above). The bees CLI persists this value in `~/.bees/config.json`, which is per-user and not committed; each new contributor on a different machine re-runs `/bees-setup` once to register hives on their machine.

If hives already exist and have a stale `egg_resolver` from an earlier installation (different home directory, install location moved, etc.), update their configuration to point to the current resolved path using the same Python one-liner pattern shown below. The bees CLI user config file lives at:

- POSIX: `~/.bees/config.json`
- Windows: `%USERPROFILE%\.bees\config.json`

The absolute path to `file_list_resolver.py` is `<bees-setup-base-dir>/scripts/file_list_resolver.py` on POSIX or `<bees-setup-base-dir>\scripts\file_list_resolver.py` on Windows. Replace `<bees-setup-base-dir>` with the literal path from the skill invocation header — do not try to derive it from environment variables or store it in a shell variable. Each Bash tool invocation in Claude Code is a fresh shell, so a `RESOLVER=...` set in one snippet is empty when referenced from a later snippet; inline the literal path at every site that needs it. (This is the same convention `bees-execute` and `bees-fix-issue` use for their `force_clean_team.py` references.)

First, verify the resolver script exists at that path. If it's missing, the bees-workflow install is incomplete; tell the user to re-install per the README and stop:

```bash
# POSIX (bash / zsh):
test -f "<bees-setup-base-dir>/scripts/file_list_resolver.py" || { echo "file_list_resolver.py not found at <bees-setup-base-dir>/scripts/file_list_resolver.py — bees-workflow install is incomplete; tell the user to re-install per the README and stop."; exit 1; }
```

```powershell
# Windows (PowerShell):
if (-not (Test-Path "<bees-setup-base-dir>\scripts\file_list_resolver.py")) { Write-Error "file_list_resolver.py not found at <bees-setup-base-dir>\scripts\file_list_resolver.py — bees-workflow install is incomplete; tell the user to re-install per the README and stop." ; exit 1 }
```

Then update the bees config file with a Python one-liner — direct text editing has no atomicity story and corrupts the JSON on a wrong escape. Pass the literal resolver path as the third positional argument (do not rely on a shell variable carried over from the earlier snippet):

```bash
# POSIX (bash / zsh):
python3 -c '
import json, sys
p = sys.argv[1]
hive_name = sys.argv[2]
new_resolver = sys.argv[3]
with open(p) as f: data = json.load(f)
data.setdefault("hives", {}).setdefault(hive_name, {})["egg_resolver"] = new_resolver
with open(p, "w") as f: json.dump(data, f, indent=2)
print(f"Updated {hive_name}.egg_resolver = {new_resolver}")
' "$HOME/.bees/config.json" "<hive-name>" "<bees-setup-base-dir>/scripts/file_list_resolver.py"
```

```powershell
# Windows (PowerShell):
# IMPORTANT: use a single-quoted here-string @'...'@ around the Python source so
# PowerShell does NOT expand $variables inside the script body before invoking Python.
$pyScript = @'
import json, sys
p = sys.argv[1]
hive_name = sys.argv[2]
new_resolver = sys.argv[3]
with open(p) as f: data = json.load(f)
data.setdefault("hives", {}).setdefault(hive_name, {})["egg_resolver"] = new_resolver
with open(p, "w") as f: json.dump(data, f, indent=2)
print(f"Updated {hive_name}.egg_resolver = {new_resolver}")
'@
python -c $pyScript "$env:USERPROFILE\.bees\config.json" "<hive-name>" "<bees-setup-base-dir>\scripts\file_list_resolver.py"
```

Verify with a `bees show-ticket` on a Plan Bee that has eggs.

### Hive Configuration

All bees CLI commands must be run from inside the target repo directory.

#### Scope requirement

When calling `bees colonize-hive`, **always pass an explicit scope** specific to the target project. The default scope overlaps with other projects' hives and bees will reject the creation if any other project has a hive with the same name.

Pick the narrowest scope glob that covers the entire project directory tree — typically the project root with a trailing `/**`.

#### Create or validate

Check for the existence of the above hives using `bees list-hives` and validate their configs with `bees get-types` and `bees get-status-values`.

If any hives are missing:
- **Use `AskUserQuestion` to ask which location strategy to use** for the missing hive(s). This is a genuine multi-choice prompt — the user is picking a strategy, not typing a path; the actual paths are derived from the strategy. Offer two options (the auto-appended `Type something.` slot already covers users who want a fully custom path — do not add a redundant "Other" option):
  - **In-repo** — `<repo>/.bees/issues` and `<repo>/.bees/plans`. Versions tickets alongside code; survives machine moves.
  - **Sibling-to-repo** — `<project-parent>/<repo>-issues` and `<project-parent>/<repo>-plans`. Right when hives should be gitignored or stay per-machine.

  If both hives are missing, ask once and apply the chosen strategy to both. If only one is missing, scope the question to just that hive.
- Once the user chooses, create the hive using the bees CLI. Pass the literal absolute path to `file_list_resolver.py` (the one verified in the *Egg Resolver* section above) as the `--egg-resolver` value so the hive can resolve eggs out of the box. Inline the literal path — do not reference a shell variable like `$RESOLVER`, since each Bash tool invocation is a fresh shell and the variable will be empty here. Replace `<bees-setup-base-dir>` with the literal path from the skill invocation header:
  ```bash
  # POSIX (bash / zsh):
  bees colonize-hive --name <name> --path <path> --scope "<scope>" --egg-resolver "<bees-setup-base-dir>/scripts/file_list_resolver.py"
  ```
  ```powershell
  # Windows (PowerShell):
  bees colonize-hive --name <name> --path <path> --scope "<scope>" --egg-resolver "<bees-setup-base-dir>\scripts\file_list_resolver.py"
  ```
- After colonization, set child tiers and status values:
  ```bash
  bees set-types --scope hive --hive <name> --child-tiers '<json>'
  bees set-status-values --scope hive --hive <name> --status-values '<json>'
  ```

If a hive exists:
- Validate its child tiers and status values.
- If they differ from above, ask user if you may change them.

**Important:** This workflow has no Ideas hive. If the target repo already has an Ideas hive from a prior setup, do not remove it — but note that bees-workflow skills will not use it.

### Documentation Locations

After hives are configured, set up the `## Documentation Locations` section in CLAUDE.md.

**First, detect existing configuration.** Read the project's CLAUDE.md (create it if it doesn't exist). If a `## Documentation Locations` section already exists, parse the current values for each of the six doc types below. For each row that's already set, **show the current value to the user and ask whether to keep or change it** — do not blindly re-prompt for paths that are already configured. Only prompt fully for rows that are missing or that the user opts to change.

If the section doesn't exist at all, ask whether to configure it now: "Would you like to configure documentation locations in CLAUDE.md now? The bees workflow uses these docs as the **machine-readable source of truth** that downstream agents (`bees-execute`, `bees-fix-issue`) read during work to detect spec drift and align with project standards. For each doc type, you can point to an existing file or have one generated for you. You may also skip this step entirely."
- Options: "Yes" / "Skip for now"

If yes (or for any individual rows the user opted to change), walk through each of the six doc types below **one at a time**. For each, use `AskUserQuestion` to ask the high-level decision (provide existing path / generate / skip / etc.) — these are genuine multi-choice prompts. **Do not** include `___`-suffixed labels or any "type your own answer" options — `AskUserQuestion` auto-appends a free-text slot, so a redundant fake option just confuses the UI. Then, **only if the user picks the "provide existing path" option, prompt for the actual path in prose** in the next turn (e.g., "Got it — what's the path to your PRD?") and let the user reply normally.

| Doc type | Question | Options |
|----------|----------|---------|
| Project requirements doc (PRD) | "Do you have a project-level PRD?" | "Yes, I'll provide the path" / "Skip (offer bootstrap below)" |
| Internal architecture docs (SDD) | "Do you have internal architecture docs (e.g., an SDD)?" | "Yes, I'll provide the path" / "Skip (offer bootstrap below)" |
| Customer-facing docs | "Do you have customer-facing docs (e.g., a README)?" | "Yes, I'll provide the path" / "Use README.md (will be created during execution)" / "Skip" |
| Engineering best practices | "Do you have an engineering best practices guide?" | "Yes, I'll provide the path" / "Generate one for me" / "Skip" |
| Test writing guide | "Do you have a test writing guide?" | "Yes, I'll provide the path" / "Generate one for me" / "Skip" |
| Test review guide | "Do you have a test review guide?" | "Yes, I'll provide the path" / "Generate one for me" / "Skip" |
| Doc writing guide | "Do you have a doc writing guide?" | "Yes, I'll provide the path" / "Generate one for me" / "Skip" |

Notes:
- **PRD and Internal architecture docs (SDD)** describe what the project is and how it's designed. If skipped here, the **Bootstrap PRD/SDD from existing codebase** subsection below offers to create them by exploring the repo. Don't auto-generate from a static template — they need real content drawn from the project.
- **Customer-facing docs** should not be generated during setup — offer to point to `README.md` which the Doc Writer agent will create during execution.
- The four boilerplate guides (engineering, test writing, test review, doc writing) can each independently be provided by the user or generated from a template tailored to the detected stack.
- You may batch multiple high-level decisions into a single `AskUserQuestion` if it reads clearly, but the user must be able to give a different answer per doc type. Path collection always happens as prose in the next turn — never as an option label.

#### Generating docs

Before generating any docs, determine the project's technology stack from CLAUDE.md, the SDD, `Cargo.toml`, `package.json`, `go.mod`, or similar manifest files. Then generate each requested doc tailored to that stack:

- **Engineering best practices** (`docs/engineering-best-practices.md`) — coding standards, error handling conventions, module/package boundary rules, async/concurrency patterns, type design, API conventions, observability, storage patterns, security, code style, and dependency management. Ground every recommendation in the project's actual stack (e.g., for a Rust/tonic/tokio project: thiserror for errors, tracing for observability, dashmap for concurrency, clippy/fmt for style).

- **Test writing guide** (`docs/test-writing-guide.md`) — test organization (unit vs integration), naming conventions, async test patterns, integration test isolation strategies, mocking approach (prefer hand-written trait mocks over frameworks where applicable), test data construction, assertion patterns, property-based testing, and what not to test.

- **Test review guide** (`docs/test-review-guide.md`) — checklist format covering: correctness (behavior not implementation), isolation (no cross-test dependencies), coverage (happy path + error paths + boundaries), robustness (no sleeps for sync, timeouts on hangs), readability (arrange-act-assert, named constants), performance, and anti-patterns to flag.

- **Doc writing guide** (`docs/doc-writing-guide.md`) — inline doc conventions (e.g., rustdoc, JSDoc, godoc), when to update architecture docs vs README, writing style (active voice, direct, code over prose), project-specific terminology to use consistently, formatting rules, and what not to document.

Each guide should be comprehensive but practical — opinionated defaults, not exhaustive references. Use the project's own technology choices as concrete examples throughout.

After generating, ask the user to review the generated docs and confirm before proceeding.

#### Writing the CLAUDE.md section

Do NOT volunteer the following context unless the user asks what a location is for:
- **Project requirements doc (PRD)**: Used by the Product Manager agent in `bees-execute` and `bees-fix-issue` to detect spec drift — does the work the Engineer landed match what the project says it does? Project-level cumulative spec; new features add sections, never overwrite.
- **Internal architecture docs (SDD)**: Used by the Engineer to understand existing system design, by the Product Manager for architectural drift detection, and by the Doc Writer to update architecture documentation after code changes.
- **Customer-facing docs**: Used by the Doc Writer to update user-facing documentation when user-visible behavior changes.
- **Engineering best practices**: Used by the Engineer agent in bees-fix-issue, bees-breakdown-epic, and bees-execute to follow project coding standards when writing or modifying source code.
- **Test writing guide**: Used by the Test Writer to follow project testing conventions when writing or modifying tests.
- **Test review guide**: Used by the Test Writer to self-review test quality before completing work.
- **Doc writing guide**: Used by the Doc Writer to follow project documentation style and format conventions.

Then write or update a `## Documentation Locations` section in the project's CLAUDE.md with the provided paths, using this format:

```markdown
## Documentation Locations

- **Project requirements doc (PRD)**: <path>
- **Internal architecture docs (SDD)**: <path>
- **Customer-facing docs**: <path>
- **Engineering best practices**: <path>
- **Test writing guide**: <path>
- **Test review guide**: <path>
- **Doc writing guide**: <path>
```

### Bootstrap PRD/SDD from existing codebase (optional)

This subsection runs **only if** the PRD or SDD (or both) were skipped during the Documentation Locations walkthrough above (or are still missing on a re-run). If both are already configured and present on disk, skip this subsection entirely.

**Why this matters.** Use the following framing when posing the question to the user — verbatim or close to it. The natural inclination of an engineer is to think "I don't care about reading PRD/SDD documents, I'll skip this." Reframe it:

> Your project doesn't have a PRD or SDD configured. Note: these docs aren't primarily for you to read. They're the **machine-readable source of truth that bees-workflow agents (`bees-execute`, `bees-fix-issue`) read during work** to detect spec drift, verify the Engineer hasn't built something different from what was planned, and keep multi-feature projects coherent over time. Without them, each agent has less context to anchor against and may make inconsistent assumptions across features.

Then offer three options via AskUserQuestion:

1. **Bootstrap baseline docs now** *(recommended for established projects with existing code)* — I'll explore your codebase, ask you a few short questions about the project's purpose, and produce starter `docs/prd.md` and `docs/sdd.md`.
2. **Defer** — `/bees-plan` will offer to create docs seeded from your first feature's scope when you plan something new. Best for greenfield projects with little or no code yet.
3. **Skip permanently — body-as-spec** — I won't create any docs. Each Plan Bee body becomes the spec for that feature. Each Issue Bee body is the spec for that issue. Works for one-off features or throwaway projects, but does not accumulate a project-level spec across features.

#### Detect repo state before showing the question

Run a quick heuristic to decide what the question should default to:

- **Established project** (more than ~3 source files in the repo, or a non-trivial README, or any of: existing test directory, existing CI config, existing manifest like `Cargo.toml` / `package.json` / `go.mod` / `pyproject.toml` with declared dependencies) → option 1 ("Bootstrap baseline docs now") is the default and recommended option.
- **Near-greenfield** (empty repo, hello-world only, no real source) → skip the bootstrap question entirely. Tell the user: "This looks like a new/empty project. `/bees-plan` will offer to create your initial PRD/SDD seeded from your first feature's scope. No bootstrap to do here." Skip ahead to Build Commands.

#### If the user picks option 1 (Bootstrap)

##### Step A: Explore the codebase

Read the project broadly. The goal isn't to write the PRD/SDD yet — it's to gather enough context that the docs aren't fabricated:

- The README (or whatever Customer-facing docs path was set, or `README.md` if present)
- The CLAUDE.md (already partially populated by setup at this point)
- Top-level project structure: directories, source files, test files
- Manifest files: `Cargo.toml`, `package.json`, `go.mod`, `pyproject.toml`, etc. — for dependencies and stack
- A handful of representative source files: the entry point if there is one, a couple of core modules
- Any `Dockerfile`, CI config (`.github/workflows/`, `.gitlab-ci.yml`, etc.)
- Any existing `docs/` content even if not formal PRD/SDD

Capture: the tech stack, the deployment model (CLI / library / web service / etc.), the major components and how they relate, key external dependencies, anything observable about code style and conventions.

##### Step B: Ask the user the questions code can't answer

The codebase tells you *what* and *how*; it doesn't tell you *why* or *for whom*. Ask the following batch — group the multiple-choice questions into one `AskUserQuestion` call (it supports multiple questions per call), then ask the open-ended ones as plain prose in a single message and let the user reply in their next turn. **Do not** wrap the open-ended questions in `AskUserQuestion` — it is multi-choice only; for free-text answers, prose is the right shape.

**Multiple-choice questions** (single-select; the runtime auto-appends a `Type something.` free-text slot, so you don't need to add an "Other" option yourself):

- **Primary audience:** End users (consumer-facing) / Developers (dev tool or library) / Internal team (internal tool) / Mixed audience
- **Deployment model:** CLI tool / Web service or API / Library or SDK / Desktop app / Mobile app / Browser extension
- **Maturity:** Production-shipping / Active maintenance / Early-stage prototype / Research or experiment
- **Project type:** Open-source / Proprietary product / Internal-only tool / Side project

**Open-ended questions** (ask these as a numbered prose list in a single message — no tool call; the user will reply in their next turn; ≤ 2-3 sentences each is ideal):

1. "In one or two sentences, what does this project do for its users? (the elevator pitch)"
2. "What's the main reason this project exists — what problem is it solving?"
3. "Are there explicit non-goals — things this project *deliberately* doesn't try to do? (Skip if none come to mind.)"
4. "What's one observable behavior you'd point at to say 'this project is working correctly'? (Becomes a baseline acceptance criterion.)"

##### Step C: Generate the seed docs

Create `docs/` if it doesn't exist:

```bash
# POSIX (bash / zsh):
mkdir -p docs

# Windows (PowerShell):
New-Item -ItemType Directory -Force -Path docs | Out-Null
```

Write `docs/prd.md` with this skeleton, filling in from the answers (Step B) and the codebase exploration (Step A):

```markdown
# <Project name> — Product Requirements

## Existing scope

<One-paragraph elevator pitch from Step B's "what does it do" + audience and
deployment model from MC. Synthesize so it reads like a single coherent
project description, not a bulleted list of answers.>

## Why

<From Step B's "why does this project exist". 1-2 paragraphs.>

## Out of scope

<From Step B's non-goals, or "(none specified at bootstrap; will be filled
in as features are planned)" if user skipped.>

## Acceptance criteria (project-level)

<From Step B's "observable behavior". Phrased as a measurable check the
user could perform.>

## Per-feature scope

<Empty section header for now. Each /bees-plan invocation that produces
docs adds a "### Feature: <title>" subsection here.>
```

Write `docs/sdd.md` with this skeleton, filling in from Step A (codebase exploration). On greenfield (we won't get here per the skip-rule above, but if for any reason we do): leave sections as stub placeholders. On established projects, populate as much as the codebase reveals:

```markdown
# <Project name> — Software Design

## Tech stack

<Languages, frameworks, key libraries — pulled from manifest files.>

## Architecture overview

<2-3 paragraphs describing the major components and how they interact.
Drawn from top-level directory structure + entry point + a couple of
core modules.>

## Key components

<Bulleted list, one per major module/package/directory. One sentence each
describing what it does.>

## External dependencies

<Storage, queues, external services, auth providers — anything observable
in the code.>

## Deployment

<From Dockerfile, CI config, README install instructions. If not detectable,
mark as "(not yet documented)".>

## Per-feature design

<Empty section header for now. Each /bees-plan invocation that produces
docs adds a "### Feature: <title>" subsection here.>
```

##### Step D: Show drafts and apply

Show both files to the user before writing. Use `AskUserQuestion`: "Here are the bootstrap docs I'd write. Apply them as-is, edit before applying, or cancel the bootstrap?"

If applied, write the files to disk and update the `## Documentation Locations` section in CLAUDE.md so the PRD and SDD rows point at the new files.

##### Step E: Tell the user how the docs grow from here

After the bootstrap completes, leave the user with this note:

> The docs you just bootstrapped are starter content. They'll grow incrementally as you use the workflow:
> - **`/bees-plan`** for new features adds a "Feature: <title>" subsection to both `docs/prd.md` and `docs/sdd.md`.
> - **`/bees-fix-issue`** for bug fixes that change documented behavior updates the relevant section.
> - **`/bees-execute`** Doc Writer keeps the architecture sections in sync with what the Engineer actually built.
>
> You don't need to maintain the docs by hand — the workflow handles it. You just need to keep using it.

#### If the user picks option 2 (Defer)

Don't bootstrap. Continue to Build Commands. Make sure CLAUDE.md `## Documentation Locations` has empty values for PRD and Internal architecture docs (so a future `/bees-plan` invocation will detect missing docs and offer Path 2 there).

#### If the user picks option 3 (Skip permanently — body-as-spec)

Don't bootstrap. Continue to Build Commands. Same CLAUDE.md state as Defer.

### Build Commands

After Documentation Locations is set, walk the user through the project's build/test/format/lint commands. The bees workflow's downstream skills (`bees-execute`, `bees-fix-issue`) read these commands from CLAUDE.md instead of hardcoding language-specific tooling, so the workflow works on Rust, Node, Python, Go, and other stacks without per-skill editing.

**First, detect existing configuration.** Read CLAUDE.md. If a `## Build Commands` section already exists with all five required keys (Compile/type-check, Format, Lint, Narrow test, Full test) populated, show the user the current values and ask whether to keep or change each one. **Do not blindly re-prompt the user for commands that are already set** — only prompt for slots that are missing or that the user explicitly wants to change. If every slot is already set and the user wants to keep all of them, this section is a no-op on this run.

**This section is required.** Unlike Documentation Locations, the user cannot skip the Build Commands walkthrough on first-time setup. Auto-detection alone is unsafe on polyglot projects, monorepos, and projects with custom build systems (Bazel, Buck, Nx, etc.) — silently running the wrong commands would mask real failures. The walkthrough must complete before setup is considered complete.

#### Detect the stack

Inspect the repo for one or more of these manifest files to identify the stack and propose sensible defaults:

| Manifest | Stack | Proposed defaults |
|---|---|---|
| `Cargo.toml` (with `[workspace]`) | Rust workspace | `cargo check --workspace` / `cargo fmt` / `cargo clippy --workspace --all-targets -- -D warnings` / `cargo test -p <crate>` / `cargo test --workspace` |
| `Cargo.toml` (single crate) | Rust crate | `cargo check` / `cargo fmt` / `cargo clippy --all-targets -- -D warnings` / `cargo test --lib` / `cargo test` |
| `package.json` + `tsconfig.json` | Node/TypeScript | `tsc --noEmit` / `prettier --write .` / `eslint .` / `vitest run <path>` / `vitest run` |
| `package.json` (no tsconfig) | Node/JavaScript | (skip Compile/type-check or use empty default) / `prettier --write .` / `eslint .` / `vitest run <path>` / `vitest run` |
| `package.json` + `jest.config.*` | Node + jest | substitute `jest <path>` / `jest` for the test slots above |
| `pyproject.toml` or `setup.py` | Python | `mypy .` / `black .` / `ruff check .` / `pytest <path>` / `pytest` |
| `pyproject.toml` + `poetry.lock` | Python (Poetry) | prefix the Python defaults with `poetry run` |
| `go.mod` | Go | `go build ./...` / `gofmt -w .` / `golangci-lint run` / `go test ./<pkg>/...` / `go test ./...` |
| `pom.xml` or `build.gradle` | Java | `mvn compile` (or `gradle build`) / no format default — ask user / no lint default — ask user / `mvn test -Dtest=<name>` / `mvn test` |
| (none of the above) | Other / unknown | No defaults — prompt the user to fill each command manually. |

If multiple manifests are present (polyglot repo or monorepo), surface this to the user and ask which stack the workflow should target. Polyglot projects may need to wrap commands in a per-package script — that's the user's choice, not the skill's.

#### Walk through each command slot

Use `AskUserQuestion` once per command slot, surfacing the detected default as the recommended option. Walk all five slots in order:

1. **Compile/type-check** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command" / (for interpreted languages with no static type-checker) "This project has no type-check step — leave empty".
2. **Format** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
3. **Lint** — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
4. **Narrow test** (single file or package) — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".
5. **Full test** (whole suite) — recommended: <detected>. Options: "Use the recommended default" / "I'll provide a custom command".

For the Compile/type-check slot, an empty value is acceptable for interpreted languages without a static type-checker. For all four other slots, an empty value is **not** acceptable — re-prompt with the recommended default and a note that downstream skills require a value.

You may batch related questions into a single `AskUserQuestion` call if the proposed defaults are clearly correct (e.g., for an obviously-Rust workspace project) — but the user must always be able to override any individual command.

#### Writing the CLAUDE.md section

Do NOT volunteer the following context unless the user asks what each command slot is for:
- **Compile/type-check**: Used by the Engineer agent in `bees-execute` and `bees-fix-issue` after each significant change to catch errors early before moving to the next subtask. May be empty for interpreted languages.
- **Format**: Used by `bees-execute` and `bees-fix-issue` to normalize formatting at commit time, so agent-induced reformatting in unrelated files is consistent.
- **Lint**: Used by the Engineer agent in `bees-execute` and `bees-fix-issue` at subtask boundary, and by the Code Reviewer during quality gates.
- **Narrow test**: Used by Engineer / Test Writer agents while iterating on a single file or package, to keep feedback loops fast.
- **Full test**: Used at the Task's authoritative final-validation subtask in `bees-execute`, and at the end of `bees-fix-issue` after the Engineer completes the fix.

Then write or update a `## Build Commands` section in the project's CLAUDE.md, using this exact format:

```markdown
## Build Commands

- **Compile/type-check**: <command>
- **Format**: <command>
- **Lint**: <command>
- **Narrow test**: <command>
- **Full test**: <command>
```

The bullet keys (`Compile/type-check`, `Format`, `Lint`, `Narrow test`, `Full test`) are a contract — downstream skills look up commands by these exact strings. Do not rename them.

### Next Steps

After setup is complete, tell the user that the bees workflow is ready to use. CLAUDE.md now contains both a `## Documentation Locations` section (consumed by Doc Writer / Engineer / Test Writer agents during execution) and a `## Build Commands` section (consumed by Engineer agents in `bees-execute` and `bees-fix-issue` for compile/format/lint/test invocations). Both are precondition checks for the downstream workflow skills — running `/bees-execute`, `/bees-fix-issue`, `/bees-plan-from-specs`, or `/bees-file-issue` against a repo missing either section will hard-fail with `Run /bees-setup first.`

The next-step recommendation depends on whether the user already has spec docs (a PRD and SDD, or equivalent) on disk. Use `AskUserQuestion` to find out, then surface the matching path:

- **Yes, the user has finalized PRD and SDD documents** → recommend:

  ```
  /bees-plan-from-specs <path-to-PRD> <path-to-SDD>
  ```

  `/bees-plan-from-specs` reads both documents, creates a Plan Bee in the Plans hive with the two paths as its `egg`, decomposes the work into Epics, and chains into `/bees-breakdown-epic`. This is the right choice when scope and design are already nailed down and just need to be turned into a plan.

  If your PRD/SDD already describe multiple features, use `/bees-plan` (or `/bees-plan-from-specs --feature "<title>"` to scope to one) — bare `/bees-plan-from-specs <PRD> <SDD>` assumes a single-feature spec and will hard-fail on cumulative docs.

  Run `/bees-plan-from-specs` in a fresh Claude Code session. `/bees-setup` may have just generated bootstrap PRD/SDD docs and consumed substantial context; `/bees-plan-from-specs` re-reads the specs and CLAUDE.md from disk, so a fresh session gives it full context budget for scope analysis and Epic creation.

- **No PRD/SDD yet, or the user wants to start from "I have an idea"** → recommend:

  ```
  /bees-plan [optional one-line description]
  ```

  `/bees-plan` is interactive — it asks clarifying questions to define scope, optionally drafts PRD/SDD updates if the project has those docs, then creates a Plan Bee with Epics. The Plan Bee body itself becomes the authoritative scope document when no PRD/SDD exist (the Bee's `egg` field stays empty), and downstream skills (`/bees-breakdown-epic`, `/bees-execute`) will use the Bee body as the spec source. This is the right choice for fresh ideas, refactors, infra work, or any feature that doesn't yet have a written spec.

  Run `/bees-plan` in a fresh Claude Code session. `/bees-setup` may have just generated bootstrap PRD/SDD docs and consumed substantial context; `/bees-plan` does deep codebase exploration and scope iteration, so a fresh session gives it full context budget for that work.

Both paths converge on the same Plan Bee shape (top-level Bee in the Plans hive with Epic children). The downstream chain — `/bees-breakdown-epic` → `/bees-execute` → `/bees-fix-issue` for any issues — works the same way for either entry point.
