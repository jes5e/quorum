---
id: b.kpt
type: bee
title: /bees-setup should detect new-machine case and offer fast-path re-registration
down_dependencies:
- b.6e6
parent: null
egg: null
created_at: '2026-05-01T16:19:06.836236'
status: done
schema_version: '0.1'
guid: kptbfot4gdgdnuydd79q861esjqre622
---

## Description

When a user pulls a bees-workflow repo onto a new machine (or another engineer pulls it for the first time), the on-disk `.bees/<hive>/` directories are present and the hive markers (`.bees/<hive>/.hive/identity.json`) exist, but the per-machine `~/.bees/config.json` has no scope entry for this repo. Result: every bees command silently behaves as if no tickets exist (`bees list-hives` returns `{"hives": [], "message": "No hives configured"}`), and downstream skills (`/bees-execute`, `/bees-fix-issue`, `/bees-file-issue`, `/bees-breakdown-epic`) hard-fail with `Run /bees-setup first.`

The user's only recovery path today is to re-run `/bees-setup` from scratch, which walks through Agent Teams confirmation, teammateMode confirmation, doc-locations table, build-commands prompts, and bootstrap-doc generation — all of which are already correct in the repo's committed CLAUDE.md. The walk-through is heavy, error-prone (a wrong answer can overwrite committed CLAUDE.md sections), and unnecessary: the only thing actually missing is the per-machine config registration.

This is the multi-machine and multi-engineer use case for bees-workflow. With `.bees/` committed to git, the workflow assumes shared tickets travel with the repo — but bees itself has no built-in path to bootstrap registration from on-disk markers (verified against `gabemahoney/bees` source: the identity marker deliberately doesn't carry per-hive config like `child_tiers`, `status_values`, `egg_resolver` — those live only in `~/.bees/config.json` per `docs/architecture/storage.md:72`). So the fix has to happen in our `/bees-setup` skill, which already knows the canonical defaults.

A separate upstream issue should be filed on `gabemahoney/bees` proposing a first-class `bees adopt-hive --from-marker` command, but the skills fix is independent of and unblocks the workflow today.

## Current behavior

User runs `/bees-setup` on a new machine in an already-set-up repo. The skill walks the full setup flow:

1. Agent Teams env-var check (the env var is per-machine — fine to keep).
2. teammateMode prompt (per-machine — fine to keep).
3. Hive setup: asks where each missing hive should live, even though the on-disk hive directories already exist. The user has to manually point the skill at the existing `.bees/issues` and `.bees/plans` paths.
4. Documentation Locations: re-prompts for every doc type, even though CLAUDE.md already has them populated. The skill does have a 'detect existing values' check at `skills/bees-setup/SKILL.md:480`, but it still walks the user through confirming each row.
5. Build Commands: same — re-prompts for every slot.
6. Bootstrap PRD/SDD offer: triggered if the existing CLAUDE.md doesn't list both, which can mis-fire if the original author skipped the bootstrap.

For a user who just wants their machine's bees config restored to match the repo, this is far more friction than the situation warrants.

## Expected behavior

`/bees-setup` should detect the **new-machine, repo-already-set-up** case early and offer a fast path.

**Detection rule** (all three must be true):

- `.bees/<hive>/.hive/identity.json` exists for one or more hives in the current repo (walk on disk; do not hardcode hive names).
- Those hives are not registered in `~/.bees/config.json` for any scope that covers this repo path.
- The repo's `CLAUDE.md` already contains a populated `## Documentation Locations` section AND a populated `## Build Commands` section (i.e. the repo was previously fully set up).

If all three are true → fast path. If any are false → existing full flow.

**Fast-path actions**:

1. Print a one-paragraph diagnosis: 'Looks like this repo was already set up for bees on another machine. The on-disk hive markers are here but they're not registered in your machine's bees config. I can re-register them for you and you'll be ready to go. CLAUDE.md will not be touched.'
2. For each on-disk hive marker found, re-register using canonical defaults plus the egg-resolver path resolved from this skill's own base dir:
   - `bees colonize-hive --name <name> --path <discovered-path> --scope <repo-glob> --egg-resolver <bees-setup-base>/scripts/file_list_resolver.py`
   - For 'issues' hives: `bees set-status-values --scope hive --hive issues --status-values '[\"open\",\"done\"]'`
   - For 'plans' hives: `bees set-types --scope hive --hive plans --child-tiers '{\"t1\":[\"Epic\",\"Epics\"],\"t2\":[\"Task\",\"Tasks\"],\"t3\":[\"Subtask\",\"Subtasks\"]}'` and `bees set-status-values --scope hive --hive plans --status-values '[\"drafted\",\"ready\",\"in_progress\",\"done\"]'`
   - For unknown hive names (anything other than 'issues' or 'plans'): prompt the user via `AskUserQuestion` for each — these are out-of-scope for the canonical defaults.
3. Check `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` and `teammateMode` in `~/.claude/settings.json`. If either is missing, offer to add — keep this to a single quick confirm, not the full per-setting walk-through that the existing flow uses.
4. Print: 'Re-registered N hives. You're ready to go.' Then use `AskUserQuestion`:
   - 'Exit now (recommended)' — most users on a new machine want exactly this.
   - 'Continue with the full setup walk anyway' — escape hatch for users who actually want to reconfigure CLAUDE.md, paths, build commands, etc.

**Do not touch CLAUDE.md in the fast path.** It's repo state and is already correct on disk; the original author committed it. Modifying it on a new machine would risk overwriting something the user updated since pulling.

**Keep the existing slow path** for genuine first-time setup (where any of the detection rule's three conditions is false). Both paths converge on the same final state — a working hive registration plus per-machine settings — but the fast path skips ~10 prompts when nothing in the repo state requires them.

## Impact

- **UX**: a new-machine user (or a second engineer pulling the repo for the first time) goes from a ~10-prompt walk-through to a 1- or 2-prompt confirm. The skill stops feeling like initial setup and starts feeling like re-attaching to an existing setup, which is what's actually happening.
- **Workflow correctness**: today's full-walk path can corrupt repo state if the user picks a wrong answer to a doc-location or build-command prompt — the skill rewrites those CLAUDE.md sections. The fast path eliminates the chance of that on the new-machine case.
- **Multi-engineer adoption**: bees-workflow doesn't have a documented onboarding-second-engineer story today. A teammate who clones the repo runs into the silent 'no hives configured' failure mode and has to be hand-walked through the recovery. The fast path makes the second-engineer case a one-prompt operation and is the natural place to put any onboarding documentation we eventually write.

## Suggested fix

1. Add a 'Fast-path detection' section to `skills/bees-setup/SKILL.md` near the top of the steps, after the precondition check and before the Agent Teams subsection. Spell out the three-part detection rule and the four fast-path actions exactly as in 'Expected behavior' above. Make the OS-conditional bash/PowerShell snippets explicit — a Python helper for walking the on-disk markers may be cleaner than inlining shell, since the same script can produce a list of `(name, path)` pairs cross-platform.
2. The unknown-hive-name branch (any hive directory whose name isn't 'issues' or 'plans') should fall through to the existing full-flow per-hive prompts. The fast path is only for the canonical two; treat anything else as 'I don't know the defaults for this; ask the user.'
3. The Agent Teams + teammateMode check should be lifted from the existing slow path and made callable from both paths — same check, different surrounding prose. Don't duplicate the JSON-mutation logic in two places.
4. Update the README's `/bees-setup` description to mention the fast path: 'On a new machine in an already-set-up repo, `/bees-setup` detects the existing hive markers and offers to just re-register them, skipping the full walk-through.' One sentence in the existing skill table is enough.
5. File a separate upstream issue on `gabemahoney/bees` proposing `bees adopt-hive --from-marker <path>` (or `colonize-hive --from-marker`) so future bees-on-multiple-machines users don't all have to reinvent this fix in their own skill sets. Reference `docs/architecture/storage.md:72`'s deliberate decision that the marker doesn't carry config — any upstream fix needs to either widen the marker schema or accept a `--defaults-from <other-hive-or-scope>` template argument.

## Acceptance criteria

- On a fresh machine in an already-set-up repo (CLAUDE.md present and populated, `.bees/<hive>/.hive/identity.json` present, `~/.bees/config.json` missing the scope), `/bees-setup` enters the fast path and completes in at most two prompts (the 'Exit / Continue' question, plus optionally one quick confirm if Agent Teams or teammateMode is missing).
- On a fresh machine in a fresh repo (no `.bees/`, no CLAUDE.md or empty CLAUDE.md), `/bees-setup` enters the existing slow path with no behavior change.
- On the same machine that ran the original setup (everything already configured), `/bees-setup` is a no-op for the hive-registration step (it sees the hives are already registered) and the existing 'detect existing CLAUDE.md values' branch handles the rest. Confirm no regression here.
- The fast path does not write to or modify `CLAUDE.md` under any circumstances.
- Unknown hive names (anything other than 'issues' or 'plans') trigger a prompt asking the user for child tiers and status values; they don't silently get canonical defaults.

This is a workflow-level fix; no test suite exists for this repo, so verification is by manual walk-through on each of the three scenarios above.
