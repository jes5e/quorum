# Contributing to quorum

This file captures workflow design rationale, intentional asymmetries, and anti-patterns. External reviewers and future agents working on these skills don't have access to the conversation history, commit messages, or ticket bodies that informed many non-obvious choices. This is the durable record so design decisions don't have to be re-litigated each time someone touches a skill.

## This is the canonical source

All skill edits happen in this repository. Per-project copies (e.g., `~/.claude/skills/<skill>/` or `<repo>/.claude/skills/<skill>/`) are install artifacts. Editing them directly creates drift; future re-installs will overwrite the edits.

If you have a clone at `~/code/quorum/` and want live editing, symlink your global install at it:

```bash
# POSIX (bash / zsh):
for s in quo-breakdown-epic quo-doc-writer-review quo-engineer-review \
         quo-execute quo-file-issue quo-fix-issue quo-plan \
         quo-plan-from-specs quo-setup quo-status quo-test-writer-review; do
  ln -sfn "$HOME/code/quorum/skills/$s" "$HOME/.claude/skills/$s"
done

# Windows (PowerShell, run as Administrator for symlinks):
$skills = 'quo-breakdown-epic','quo-doc-writer-review','quo-engineer-review',
          'quo-execute','quo-file-issue','quo-fix-issue','quo-plan',
          'quo-plan-from-specs','quo-setup','quo-status','quo-test-writer-review'
foreach ($s in $skills) {
  New-Item -ItemType SymbolicLink -Force -Path "$HOME\.claude\skills\$s" `
    -Target "$HOME\code\quorum\skills\$s"
}
```

After this, edits in `~/code/quorum/skills/<skill>/SKILL.md` are immediately picked up by Claude Code without re-installing.

## Workflow principles

1. **Language-agnostic.** Skills must work on Rust, Node, Python, Go, Java, C/C++, and unknown stacks. The pattern is: a project's `CLAUDE.md` declares `## Build Commands` and `## Documentation Locations` sections; skills look up commands and paths from there by exact key. Never hardcode `cargo`, `npm`, `cargo test`, `pytest`, etc. in skill prose.
2. **Cross-platform.** POSIX (bash/zsh on macOS and Linux) and native Windows PowerShell both work. Every multi-line shell snippet ships as labeled OS-conditional blocks. Helper scripts are Python (cross-platform) or come in OS-paired implementations.
3. **Idempotent.** Re-running `/quo-setup`, `/quo-plan`, etc. on an already-configured project should be a no-op or surface "already configured, change anything?" prompts — never blow away existing config.
4. **Body-as-spec is a supported mode.** When a Plan Bee is created via `/quo-plan` for a feature without a separate PRD/SDD, its `reference_materials` is null and the Plan Bee body itself is the authoritative spec. Downstream skills (`/quo-breakdown-epic`, `/quo-execute`, `/quo-fix-issue`) all have explicit prose for this — don't simplify it away on a future refactor.
5. **Cumulative docs preferred but not required.** When `/quo-plan` updates docs, it adds a new `### Feature: <title>` subsection under cumulative `## Per-feature scope` / `## Per-feature design` headers; old features stay documented. But the workflow does not enforce this — projects with monolithic specs work fine too.

## Skill conventions

- **Frontmatter:** Both of Claude Code's loaders honor more than `name` and `description`, and they honor *different* key sets. What this repo actually relies on: `skills/<name>/SKILL.md` uses `name`, `description`, and `argument-hint` (the placeholder shown after the slash-command name — see `/quo-fix-issue` and `/quo-breakdown-epic`); `agents/<role>.md` uses `name`, `description`, `model`, `tools`, and `effort`, which is how the per-role model and reasoning-effort assignments are pinned. Each loader accepts further keys beyond those (the command/skill loader also takes `disallowed-tools`, `disable-model-invocation`, `user-invocable`, `effort`, and `shell`; the agent loader also takes `memory`, `maxTurns`, `background`, `permissionMode`, `observer`, and `disallowedTools`). **The Claude Code CLI's own frontmatter schema is the authority — check a key against it before adding or removing one.** Don't treat any list in this file as exhaustive, don't assume an unfamiliar key is inert, and don't use keys the schema marks internal: those are not public API and can change without notice.
- **Shell snippets:** OS-conditional labeled blocks (POSIX bash + Windows PowerShell at minimum). Single-line trivial snippets can omit the PowerShell variant if and only if the syntax is identical (e.g., `bees show-ticket --ids b.xyz`).
- **Helper scripts:** Ship inside the owning skill's `scripts/` directory (e.g., `quo-breakdown-epic/scripts/scoped_marker_resolver.py`). Resolve the absolute path at runtime from the skill's own base directory, which Claude Code prints in the skill invocation header. A skill using its own bundled script: `<base>/scripts/<name>.py`. A skill using a sibling skill's bundled script: `<base>/../<sibling>/scripts/<name>.py`. Do not persist these paths to CLAUDE.md or any other tracked file — they're per-machine and the install location varies between contributors.
- **Structured file edits:** Use a Python one-liner with proper parsing and an atomic write — `json.load`/`json.dump` for JSON; a line-walking section split with code-fence state tracking plus `tempfile.mkstemp` + `os.replace` for markdown section deletes. Don't use prose-text-edit instructions, and don't reach for a pure regex on markdown — regex can't distinguish a `## ` heading inside a fenced code block from a real section boundary, and the failure mode is silently eating too little or too much of the file. Direct text editing has no atomicity story and corrupts the file on a wrong escape. Invoke as `python3` on POSIX and `python` (or `py -3`) on Windows — `python3` is generally not on Windows PATH for python.org installs.
- **TaskList name classes:** The execution skills route on TaskList task names — a dispatch precondition or a phase gate tests whether any task whose name starts with a given prefix is `pending` or `in_progress`. So a new name class is a routing surface, not just a label. Give it a prefix no existing test matches by accident (the `aborted-*` redelivery markers are deliberately a distinct class from `<role>-<scope>` for exactly this reason), match on the **prefix** plus status rather than an exact name so round discriminators like `-r<n>` are still caught, and author the close-out site in the same change as the creation site — including the skill's abort path, since a marker left `pending` past a unit boundary silently blocks a later phase on a subsequent run. A mechanical guard in the pytest suite backs this pairing; a name class introduced with no close-out is a defect, not a loose end.
- **CLI invocation form:** Use the shell-form `bees show-ticket --ids <id>`, not the function-call form `show_ticket(ticket_id="<id>")`. None of the skills bootstrap the MCP server, so the CLI form is the right one. (The function-call form is what the bees MCP server exposes, but skills don't run that path.)

## Intentional asymmetries

These look like inconsistencies if you compare two skills side-by-side without context. They're deliberate.

- **`/quo-execute`'s Doc Writer executes pre-planned doc Subtasks; `/quo-fix-issue`'s Doc Writer reviews the Engineer's diff for ad-hoc gaps.** `/quo-execute` Tasks have a planned subtask breakdown (from `/quo-breakdown-epic`); the Doc Writer's primary job is to execute the doc subtasks and then review for gaps. `/quo-fix-issue` has no pre-planned subtasks — the Doc Writer reviews the diff and updates ad-hoc. Different work shapes need different postures. Both blocks have an inline note pointing at the other.
- **`/quo-fix-issue` orders the lanes within one unit; `/quo-execute` only orders its review re-dispatch path.** `/quo-fix-issue` walks each Issue through an ordered Phase A / B / C ladder, so its Engineer and its writers never run at the same time. `/quo-execute` keeps the forward per-Subtask fan-out concurrent — an Engineer on Subtask N+1 still overlaps a Test Writer on Subtask N — and orders only the re-dispatch that follows a review finding. The asymmetry is deliberate: an Epic's ticket graph already sequences the forward work into units whose diffs do not overlap, while an Issue is one undivided implementation pass where every lane reads the same diff. Don't "fix" one to match the other.
- **`/quo-plan` (interactive scope-shaping) vs `/quo-plan-from-specs` (express path with finalized PRD+SDD on disk).** Two entry points to the same Plan Bee + Epics output. `/quo-plan` is the discovery path; `/quo-plan-from-specs` is the "I already nailed the scope" path. Keep both — collapsing them into one pushes too much complexity into a single skill.
- **Language-conditional examples in `/quo-setup`.** The stack-detection table IS supposed to be Rust/Node/Python/Go specific — it's defining what the user's `## Build Commands` section should resolve to in each stack. Generalizing it to "the appropriate command for your language" defeats the point.
- **Reference materials live on the Plan Bee, not on Epics.** The bees CLI accepts `--reference-materials` only on top-level Bees, not on child-tier tickets. Every Epic in a Plan Bee can trace back to the same PRD/SDD by reading the parent's `reference_materials`. Don't try to set `reference_materials` on Epics.
- **`/quo-breakdown-epic` is the only skill where dispatched subagents run in `mode: "plan"`.** Subagents during breakdown are read-only researchers; only the orchestrating skill runs ticket-mutating commands. Other execution skills (`/quo-execute`, `/quo-fix-issue`) let dispatched subagents create commits, not tickets — different scope of authority.

## Anti-patterns

- **Don't proliferate bundled scripts.** Each new helper in `scripts/` is install-mode coupling and maintenance burden. Use a Python one-liner in skill prose for one-off operations (JSON edits, simple file ops). Add a script only when the operation is non-trivial AND used in 2+ places.
- **Don't add frontmatter keys Claude Code ignores.** Keeps the source honest about what's actually consumed. This forbids *inert* keys — ones no loader reads — not the honored ones. Since the two loaders honor different (and larger than commonly assumed) key sets, verify against the CLI's own frontmatter schema before concluding a key is inert or adding a new one; see the frontmatter bullet under *Skill conventions* for the keys this repo relies on.
- **Don't hardcode hive paths or doc paths.** `/quo-setup` lets the user pick where each hive lives (in-repo, sibling-to-repo, or anywhere). Skills must resolve paths at runtime via `bees list-hives` or CLAUDE.md `## Documentation Locations`.
- **Don't replace concrete shell snippets with vague prose** ("run the appropriate test command"). Concrete commands per OS keep agent reliability up — vague prose forces the agent to guess and often guesses wrong.
- **Don't categorize-and-split issue tickets.** Default to bundling related issues into a single ticket with sub-task labels. Quorum optimizes for agent work efficiency (per-ticket overhead is the cost), not human triage. See `/quo-file-issue`'s "House style" section for the rule.
- **Don't skip verification before recommending paths or flags.** When prose says `bees set-types --child-tiers ...`, that flag must exist. Verify with `--help` before writing it. CLI-flag drift is a recurring source of P0 bugs (see *Where things live* below for where past findings are tracked).

## Verifying external-system contracts

Before designing a validation probe for an external system's contract — Claude Code's subagent loader, a third-party CLI's flag set, a platform feature's behavior — search the system's authoritative docs first. WebSearch and WebFetch are available; use them. If the docs are sufficient to establish the contract, skip the probe entirely.

If a probe is still needed, use what the docs told you to design specific, tight assertions rather than broad discovery probes. *"Does the harness register this exact frontmatter shape at this exact path with this exact session-lifecycle behavior?"* beats *"does anything happen when I dispatch this?"* — the first probe distinguishes failure causes; the second forces a guess-and-check loop.

This applies at all stages: when authoring a spec (PRD/SDD), when breaking down an Epic that touches an external contract, and when running validation probes themselves. Spending five minutes on docs upfront often saves hours of probe-and-fix cycles later, *and* makes the probes that do run far more diagnostic when they fail. (`b.5tm` Epic A's AC#2 ran probes against the wrong install directory because the spec was authored without checking the canonical Claude Code subagents directory; one WebSearch would have prevented the entire failed-probe-and-fix cycle.)

## Considered and rejected

Specific past suggestions that were evaluated and deliberately not adopted. Writing them down prevents future reviewers from re-flagging the same patterns and going through the same pushback cycle. Scan this list before flagging "this skill should do X" — X may already have been weighed and rejected.

- **Dedicated bundled helper script for JSON edits to `~/.bees/config.json` and Claude Code `settings.json`** — rejected: skill prose specifying a Python one-liner (`python -c 'import json,sys; ...'`) gives the same atomicity without adding a maintained file.
- **Unconditional "read ALL test files" in quo-test-writer-review** — rejected as written: blows context budget on large suites. Replaced with conditional "read the index plus contents of files that overlap with the changed code." Preserves duplication-detection without context bloat.
- **Adding `triggers:` and `disable-model-invocation:` frontmatter to skills** — rejected, for a different reason per key. `triggers:` is not a key either loader reads, so it wires up no trigger phrases and is pure noise. `disable-model-invocation:` *is* honored, but it stops the model from invoking a skill via the Skill tool and leaves only the user-typed slash command — which would break the orchestrator-invoked paths quorum depends on (`/quo-fix-issue` dispatching `/quo-file-issue`, the execution skills dispatching the review skills). Neither rejection generalizes into "frontmatter beyond `name` and `description` is ignored": see the frontmatter bullet under *Skill conventions*. Pinning a role's model or reasoning effort in `agents/<role>.md` frontmatter is in-bounds and is how the per-role assignments in CLAUDE.md `## Model assignment in execution skills` are expressed; don't read this rejection as forbidding it.
- **Centralizing skills into a global "shared" directory rather than skill-bundled `scripts/`** — rejected: each skill owns its helpers. Makes the bundle self-contained and avoids cross-skill coupling.

When future tickets close with a "Skipped from external review" or "Considered and rejected" note, append a one-liner here so the record stays current.

## Known limitations

These are failure modes the workflow has identified but cannot fully close at the layer this repo controls. Document them so future maintainers don't re-litigate the design and don't ship further variants of a remediation path the evidence chain has already exhausted.

- **The unexplained-movement gate has no retry-first step.** When a writer reports that the source moved underneath it and the orchestrator cannot attribute the movement — to the Engineer, to a concurrently-dispatched Test Writer's recorded perturbation, or to an external actor — `/quo-fix-issue` Section 4's movement-report rung and `/quo-execute` Section 3's Reconcile receiver fire a three-option gate (**Re-dispatch the writer now** / **Wait** / **Abort this Issue** in `/quo-fix-issue`, **Abort this unit** in `/quo-execute` — execute mode has no Issue concept, and its abort always ends the run). That gate is the deliberate design for the unattributable case and fires **only** there; attributable movement re-dispatches or waits with no gate. A retry-once refinement ahead of it — re-dispatch the writer a single time and gate only on a second abort — was not evaluated when the gate was designed; it is a plausible future simplification, not a defect in what shipped.

### Narrate-instead-of-do failure mode (residual surface after b.wii)

**The failure mode.** When an orchestrator skill is about to fire a tool call (most commonly `AskUserQuestion`), the model sometimes emits a text response describing the gate it should fire and yields control without actually firing the tool call. The user sees prose explaining what's about to happen instead of the prompt itself; the workflow stalls until the user notices and intervenes.

**Where the mitigation lives today.** This repo has shipped three layers of remediation against this failure mode:

1. **`b.sfy` (prose mitigation, first attempt)** — Added a `**Your next tool call MUST be …**` second-person imperative trailer to each review skill's output. Observed leakage of the failure mode after deployment.
2. **`b.fpm` (prose mitigation, strengthened)** — Strengthened the trailer wording, added counter-anchor clauses (`Do not produce a text response describing this gate — call the tool directly.`), and added pre-commitment lines at each Skill-call site. Observed continued leakage of the failure mode after deployment — the prose-only counter-anchor demonstrably does not hold under load.
3. **`b.wii` (structural mitigation, current state)** — Added a two-step `TaskCreate` → prescribed-tool contract at every gate-firing site (see `docs/doc-writing-guide.md` `## The two-step TaskCreate → prescribed-tool contract`). The orchestrator must first create a `gate-<kind>-<short-suffix>` TaskList task via `TaskCreate`, then fire the prescribed tool call (typically `AskUserQuestion`) in the same turn. The structural improvement is that `TaskCreate` is itself a tool call — the orchestrator cannot silently yield a `TaskCreate` invocation the way it can silently yield an `AskUserQuestion` invocation. A missed `gate-*` task is recoverable by next-turn TaskList processing; a silent prose yield of the trailer is only recoverable by the user noticing.

**The residual failure surface b.wii does not close.** The two-step contract narrows but does not eliminate the failure surface — the model can still fail to fire the *first* tool call (`TaskCreate`) before yielding. The narrowing is real (the second step's prescribed tool call is now structurally hard to drop because the orchestrator has already begun the two-step sequence, and a half-fired sequence is more visible than a fully-narrated yield), but residual leakage is expected. Definitive closure requires harness-level enforcement that this repo cannot author:

- **Anthropic API `tool_choice` mechanism** — forcing a specific tool to be called on a specific turn at the API layer would eliminate the model-adherence variance entirely. The mechanism exists today but is not exposed to skill prose in Claude Code's harness, so this repo cannot reach it.
- **Claude Code harness change** — a harness-level rule that detects "skill prose says fire X, model yielded without firing X" and re-prompts the model to fire X would close the failure mode at the integration layer. Tracked outside this repo.

The b.wii note exists so future readers don't see the residual failure surface and conclude "the structural fix didn't work, ship a fourth prose variant." The evidence chain `b.sfy` → `b.fpm` → `b.wii` is the documentation that prose-only remediations have been demonstrably exhausted.

**Do not ship further prose-only variants.** Specifically, do NOT:

- Add a more imperative form of the trailer prefix (e.g., `**YOU MUST ABSOLUTELY CALL THE TOOL NOW.**`).
- Add additional counter-anchor clauses (e.g., layered `Do not narrate. Do not yield. Do not summarize.` chains).
- Add additional pre-commitment lines on top of the existing ones at each Skill-call site.
- Rewrite the trailer in third-person framing thinking the narrative drop is caused by second-person framing — the evidence is the opposite.

Each of these has been considered and rejected (under the b.fpm → b.wii transition) on the grounds that the failure mode is a model-adherence phenomenon, not a prose-clarity phenomenon. The structural mitigation is the right shape; the residual surface is a harness-or-API problem.

**Scope of the b.wii contract — user-facing gates only.** The two-step `TaskCreate` → prescribed-tool contract is scoped narrowly. The bullets below capture the scoping decision, an illustrative non-covered case, the rationale, and how future expansion proposals should be weighed:

- **Applies to:** user-facing gate prescriptions — today `AskUserQuestion` invocations whose silent yield would stall the workflow on an invisible prompt, and any future tool whose absence stalls the workflow on a user-visible prompt.
- **Does NOT apply to:** non-user-facing state-mutation tool calls. Concretely, `/quo-spec-review`'s no-findings Shape-3 trailer prescribes `bees update-ticket --status ready` and runs *without* a paired `gate-*` task because no user prompt fires; the same is true for other workflow-internal state mutations the orchestrator may emit.
- **Rationale:** the b.wii Issue body and the Analyst proposal both framed the failure mode specifically around silent `AskUserQuestion` yields, where the user has no way to surface the missing prompt manually. A `bees update-ticket` or similar state-mutation call that the orchestrator silently drops has a different recovery path — the normal next-turn TaskList / ticket-status reconciliation already present in every consuming skill picks it up. Extending the contract to cover those non-user-facing calls would add a `TaskCreate` round-trip at every workflow-internal tool call without addressing the model-adherence failure mode the contract exists to mitigate.
- **Future expansion:** an Issue that proposes extending the contract to non-user-facing tool calls should explicitly weigh the cost (a `TaskCreate` per workflow-internal tool call) against the coverage (which model-adherence failure mode does this address that the normal ticket / TaskList reconciliation does not?) before expanding, rather than silently broadening the scope.

### Model-initiated context clearing / compaction is unavailable (mechanism-unavailable class)

**The limitation.** An orchestrator skill has no way to clear or compact its own context. This is a *mechanism-unavailable* limitation, not a model-adherence one: the lever does not exist at the harness layer, so no amount of prose can make an orchestrator pull it.

**What was verified, and how (2026-08-14/15).** Checked against the official Claude Code documentation plus a live probe in a running session:

- `/clear` and `/compact` are **user-only** slash commands. They are not reachable from skill prose, from a tool call, or from any model-invocable surface.
- **Auto-compaction fires on its own** at roughly **83%** of the context window. The threshold is only *lowerable*, and only by the user — via the `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` environment variable or the `autoCompactWindow` setting. There is no model-side control over when it fires.
- **Model-initiated compaction is an open upstream feature request** — `anthropics/claude-code#33026` — not a shipped capability.

**Two harness mechanisms reclaim tokens, and only one is observable.** Alongside auto-compaction, the harness also performs **automatic microcompaction of old tool results** — older tool-call output is dropped from the live context to make room. Both are harness-owned, neither is model-invocable, and neither is schedulable from skill prose. They differ in one way that matters to skill design: auto-compaction leaves a **visible summarization marker** in the conversation, while microcompaction leaves **no marker at all** — the orchestrator gets no signal that a tool result it "remembers" is gone.

**Why the skills carry two post-compaction rules, not one.** That asymmetry is why each orchestrator skill's reconciliation loop pairs an **unconditional** rule — conversation memory is never a substitute for the durable sources (bees, git or the returned research findings, the TaskList, and the run-state manifest); re-read them on every tick — with a **conditional** one that fires only when a summarization marker is visible (treat everything before it as non-authoritative and re-read all sources in full before dispatching). The unconditional rule is **not** redundant with the conditional one and must not be pruned as such: the conditional rule covers only the case the harness announces, and microcompaction announces nothing.

**How this surfaced.** `skills/quo-execute/SKILL.md` Section 4.2 previously defined an "Epic-boundary context-clear discipline" instructing the orchestrator to clear its own working context at each Epic boundary, and Section 3 asserted as fact that this happened. An orchestrator reaching that instruction could only *narrate* compliance — the narrate-instead-of-do failure mode documented in the entry above, arrived at from the opposite direction: there, the tool call exists and the model sometimes skips it; here, there is no tool call to make. The phrase was minted as the replacement for an older team-disband ceremony and was never load-tested against whether the model can execute it.

**Design consequence.** The three orchestrator skills use **state-externalization checkpoints plus harness-owned compaction** instead of any self-clear. `/quo-execute` and `/quo-breakdown-epic` carry the **Epic-boundary state-externalization checkpoint**; `/quo-fix-issue` carries the **Issue-boundary state-externalization checkpoint**. At each boundary the orchestrator verifies that all load-bearing state is already in a durable carrier (bees ticket statuses, per-unit commits, the compromise tracker in the two execution skills — `/quo-breakdown-epic` has none — and the `defer-*` TaskList), rewrites the run-state manifest under `<tempdir>/.quorum/`, and treats the prior unit's conversation as non-authoritative from that point on. Context is not reclaimed by any of this — it grows monotonically until the harness compacts — but the compaction is **lossless whenever it fires, including mid-unit**, and a post-compaction reconciliation tick can re-derive the whole run from the carriers. The reclamation lever that does exist is the user starting a **fresh session** at a boundary. The general rule this case produced is the **executable-verb test** in CLAUDE.md `## Review criteria for skill changes`.

**Re-probe carrier.** Upstream capabilities here are expected to change. Issue **`b.cj2`** — *"Re-probe upstream Claude Code context-window capabilities (#33026 self-compact, #34879 model-readable usage, #27969 hook-visible usage)"*, filed 2026-08-15, status `open` — is the durable carrier for periodically re-checking whether any of these mechanisms have shipped. Re-verify through that Issue rather than re-deriving the limitation ad hoc; if `#33026` ships, this entry (and the skill prose it governs) is what needs revisiting.

**Do not re-ship the instruction.** Specifically, do NOT:

- Reintroduce an instruction telling the orchestrator to clear, compact, reset, or otherwise reclaim its own context at a boundary (or anywhere else).
- Reintroduce declarative prose *describing* such a mechanism as something a skill does — "the skill clears the orchestrator's context between Epics" is the same defect in descriptive form, and it is how the original claim survived review as long as it did.
- Add prose instructing the orchestrator to measure its own token usage, report a remaining-context percentage, or gate a branch on that self-estimate. The orchestrator cannot read its own usage; `#34879` and `#27969` track the upstream capability and are covered by `b.cj2`. **Carve-out — this bans self-introspection, not consuming an external gauge.** The prohibition targets the model *pretending to know its own usage without an external source*: inventing or estimating a token count for its own remaining context from memory, reporting a self-measured percentage, or gating on such a self-estimate — none of which name a model-invocable action, since the lever that would produce a true self-reading is owned by the harness/API, not the model. It does **not** forbid reading an out-of-band, machine-written context-usage gauge that a separate status-line *producer* process computed and wrote to a file, via the helper's `read` subcommand, and stopping at a unit boundary when that reading crosses the stop threshold. That read is an ordinary file read / command run against a file another process wrote — the gauge value originates out-of-band from the status-line payload, not from the model measuring itself — so both the read and the boundary-stop are actions the model can actually take with its tools, and both pass the **executable-verb test** in CLAUDE.md `## Review criteria for skill changes`. The gauge's file path, the `read` / `produce` subcommands, the fail-safe rules, and the `STOP_THRESHOLD_PERCENT` seam the boundary consumer gates on all live in `docs/doc-writing-guide.md` `## The context-gauge file contract`; consult it rather than re-deriving the mechanism. Consuming that gauge does not resolve or soften the self-introspection ban above — the genuinely-unavailable self-measurement capability is still what `#34879` / `#27969` / `b.cj2` track.
- Substitute a softer verb ("trim", "release", "free", "drop the prior Epic's context") for the same unavailable mechanism. Name the owner of the lever — user or harness — instead.

## Status / type renames history

These renames happened in this order with specific reasons. A future "simplification" that reverses any of them would re-introduce the issue it solved.

- **Hive name `bugs` → `issues`.** "Bugs" is a subset of what gets filed. "Issues" covers bugs, wishlist items, doc fixes, and meta-tasks. The skill prose was updated; some legacy projects still have a `bugs` hive — those should be `bees colonize-hive` migrated.
- **Status names `larva` / `pupa` / `worker` / `finished` → `drafted` / `ready` / `in_progress` / `done`.** The bee-themed names obscured what state a ticket was in. The current names line up with how every other ticket system describes status, which makes the workflow accessible to people new to bees.
- **Skill prefix: `bees-*`.** All workflow skills are prefixed `bees-` so a project with multiple skill providers can tell at a glance what comes from this repo.
- **Skill renames `bees-code-review` / `bees-doc-review` / `bees-test-review` → `quo-engineer-review` / `quo-doc-writer-review` / `quo-test-writer-review`.** The earlier `bees-` prefix rename did not eliminate the misinvocation problem: Claude Code's skill matcher hits on `/<x>-review` substrings, so `/code-review`, `/doc-review`, and `/test-review` continued firing the wrong skills against unrelated user requests even after the prefix landed. The previous entry's precedent — that standalone invocation was worth optimizing the skill name for — did not hold up in practice; the dominant invocation path is the orchestrated review cycle inside `/quo-execute` and `/quo-fix-issue`, and standalone use exists but is not load-bearing on the naming choice. The new role-based names mirror `agents/<role>.md` (`engineer.md`, `doc-writer.md`, `test-writer.md`), making the orchestration-side mental model consistent across the skill catalog and the dispatched-subagent contracts.

## Where things live

- **Issues / bugs in this repo** — file in the issues hive of whichever project surfaced them, then reference them in PRs/commits here. The issues hive in `live_edit` was the first home for the validation reports that drove this workflow's design (b.622 and the b.sjz / b.dp2 / b.nyv / b.4xw / b.qw2 / b.ewe / b.bp5 / b.obn set that followed).
- **Discussion** — GitHub issues on this repo are fine for "what should the skill do?" questions. Use issue tickets in quorum for "fix X in skill Y" findings — those become the agent-fixable input set.

## Running the tests

The repo's test suite (`tests/`) and lint check both depend on dev tools that are not installed in a fresh checkout. Bootstrap them from the pinned manifest with `python -m pip install -r requirements-dev.txt` — it carries `pytest` (for the `## Build Commands` `Narrow test` / `Full test` commands) and `pyflakes` (for the `Lint` key, `python -m pyflakes skills/*/scripts/*.py`). On an externally-managed environment (PEP 668; recent Debian/Ubuntu, Homebrew) where a bare `pip install` fails with `externally-managed-environment`, either install into a virtualenv or pass `--break-system-packages`.

## Reviewing changes

A change to skill prose touches behavior that may not surface until a downstream skill executes. Before merging a non-trivial change:

1. Re-read both skills if you change cross-skill prose (e.g., a precondition the other skill relies on).
2. If you change a skill's required CLAUDE.md section keys, update `/quo-setup` so it writes the new keys, AND update every consumer skill's precondition list.
3. If you change a CLI invocation, run `bees <command> --help` and verify the flag still exists with the same name.
4. If you change a multi-line shell snippet, verify both POSIX and PowerShell variants still produce the same effect.
