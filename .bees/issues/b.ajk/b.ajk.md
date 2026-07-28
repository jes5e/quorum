---
id: b.ajk
type: bee
title: Pin reasoning effort per role; drop the Sonnet downgrade prompt
parent: null
reference_materials: null
created_at: '2026-07-28T01:26:10.606693'
status: open
schema_version: '0.1'
guid: ajkwd46tdphaq4wh62u4vih1kuzz3rh1
---

## Description

Reasoning effort has no per-role expression in quorum. Every dispatched subagent inherits whatever effort the orchestrator's Claude Code session happens to be set to, so one `/model` setting governs root-cause analysis, implementation, adversarial code review and doc prose identically. Meanwhile the one model lever that does exist — the run-start prompt that downgrades three roles to Sonnet — is a cost control on a workflow whose stated objective is output quality, and it doubles as a footgun: it lets the user downgrade the PM, which is a review gate.

This ticket pins reasoning effort per role in `agents/*.md` frontmatter and removes the Sonnet downgrade path. **Model assignment itself does not change** — all eight role files are already `model: opus` and stay that way. The diff is an added effort key per role, a deleted prompt, and a replacement gate.

## Current behavior

- All eight `agents/*.md` files carry `model: opus`. Engineer, Test Writer, Code Reviewer, Test Reviewer and Analyst are hard-pinned (`skills/quo-execute/SKILL.md:99`, `skills/quo-fix-issue/SKILL.md:66`); Doc Writer, PM and Doc Reviewer ship `opus` as a default that a run-start prompt can override to Sonnet.
- `skills/quo-execute/SKILL.md:96-99`, `skills/quo-fix-issue/SKILL.md:63-66` and `skills/quo-breakdown-epic/SKILL.md:37-40` ask the user once at run start to pick Opus or Sonnet for the "support roles" (Doc Writer, PM, Doc Reviewer).
- No `agents/*.md` file sets a reasoning-effort key, so all eight roles inherit the orchestrator session's effort. A single dial governs eight roles with materially different needs.
- Nothing tells the user what session setting a given skill is tuned for, and the skills cannot read the current setting to check it.

## Expected behavior

### Pinned in `agents/*.md` frontmatter

| Role | Model | Effort |
|---|---|---|
| `agents/analyst.md` | Opus (unchanged) | xhigh |
| `agents/code-reviewer.md` | Opus (unchanged) | xhigh |
| `agents/engineer.md` | Opus (unchanged) | high |
| `agents/pm.md` | Opus (unchanged) | high |
| `agents/test-writer.md` | Opus (unchanged) | high |
| `agents/test-reviewer.md` | Opus (unchanged) | high |
| `agents/doc-writer.md` | Opus (unchanged) | high |
| `agents/doc-reviewer.md` | Opus (unchanged) | high |

Rule: every role that produces or reviews work runs at `high` minimum; the two adversarial roles — the one that diagnoses before implementation and the one that hunts for what no test covers — run at `xhigh`.

**Invariant: never pin a reviewer below the role it reviews.** A gate weaker than the work it inspects is not a gate. This holds across the table today (engineer `high` / code-reviewer `xhigh`; test-writer `high` / test-reviewer `high`; doc-writer `high` / doc-reviewer `high`) and must be preserved by any future retune.

### Advisory — runs as the main session, not pinnable from the repo

| Surface | Recommended |
|---|---|
| Orchestrator (`/quo-execute`, `/quo-fix-issue`) | Opus / medium — it delegates all implementation rather than producing work, and its context is the longest in the run |
| `/quo-plan`, `/quo-write-prd`, `/quo-write-sdd`, `/quo-spec-review`, `/quo-breakdown-epic` | Opus / high — tiny fan-out, maximal blast radius; errors here propagate into every Epic downstream |

### Run-start prompt replaced by a session-setting gate

The "pick Opus or Sonnet for support roles" prompt is deleted and its slot reused for a gate that surfaces the recommended session setting. Net gate count is unchanged.

## Impact

- **Quality, directly.** The two roles where reasoning depth pays off most — the Analyst diagnosing root cause before any code is written, and the Code Reviewer searching adversarially for untested failure modes — currently run at whatever the user's session happens to be. A user on `medium` gets medium-effort root-cause analysis feeding every downstream Engineer dispatch.
- **Removes a live footgun.** The run-start prompt's only function is downgrading three roles to Sonnet. One of those three is the PM — the spec-traceability and scope-creep gate. A cost-conscious user downgrading "support roles" is downgrading a gate without realising it.
- **Reproducibility.** Run quality currently depends on whatever each engineer has set in `/model`, recorded nowhere and invisible in review. Frontmatter makes it a diff.
- **Residual gap.** Only the pinned block is enforceable. The advisory block is a recommendation the repo cannot enforce, which the session gate narrows but does not close.

## Suggested fix

### Verified before filing (Claude Code v2.1.220)

Both capability questions this ticket depends on were resolved at filing time. No verification spike is needed.

1. **Effort is settable in subagent frontmatter.** The key is `effort`. Values are `low`, `medium`, `high`, `xhigh`, `max` — available levels depend on the model, so confirm `xhigh` resolves on Opus at implementation time. Per the subagent documentation it **overrides the session effort level** rather than capping it; the default is inherit-from-session. Change 1 is viable exactly as specified.
2. **The session's current effort is readable, and the value is live.** `printenv CLAUDE_EFFORT` returns the session's effort level. It reflects mid-session changes, not just the launch flag — verified by launching with `--effort xhigh`, changing the setting to `high` via `/model`, and re-reading, which returned `high`. Change 3's gate can therefore compare against the operator's actual current setting. Re-run that same launch/change/re-read check if the gate ever appears to misfire.

**Consequence of override semantics — accepted deliberately.** Because frontmatter overrides rather than caps, an operator running the session above `high` (e.g. `claude --effort xhigh`) will see six of the eight roles *lowered* to `high` once this lands. Rebasing the table upward to avoid that was considered and rejected — see Decisions below. The two roles where reasoning depth pays off most are pinned above the default and are unaffected either way.

### Change 1 — pin effort per role

Add the effort key to all eight `agents/*.md` files per the table above. Leave `model: opus` untouched in every file.

### Change 2 — delete the run-start Opus/Sonnet prompt

Remove it from `skills/quo-execute/SKILL.md:96-99`, `skills/quo-fix-issue/SKILL.md:63-66` and `skills/quo-breakdown-epic/SKILL.md:37-40`, along with the downstream prose that references the user's choice (`quo-execute` lines ~256-257, `quo-fix-issue` lines ~357, ~480, and the `## Model selection` paragraph at the top of `agents/doc-writer.md`, `agents/pm.md`, `agents/doc-reviewer.md`).

### Change 3 — repurpose the prompt slot as a conditional session-setting gate

Same three skills. Read the session's current effort from `CLAUDE_EFFORT` and compare it against the skill's recommended **floor** for the orchestrator. **Say nothing when the session is at or above the floor** — no gate, no prompt, no output. Fire the gate only when the session is below it:

```
This session is running at effort=<current>, below the <floor> this skill
is tuned for. The orchestrator delegates implementation rather than
producing work itself, but it still owns ticket state, dispatch ordering,
gate handling and the review loop.

Subagent effort is pinned per role and is NOT affected by this setting.

  -> Proceed anyway
  -> Let me change it first   (exits; run /model, then re-invoke)
```

**Compare against a floor, not for equality.** An operator running hotter than the recommendation costs wall-clock but not quality, and prompting someone who deliberately chose a higher tier is pure noise — the exact gate fatigue this design is trying to avoid. Only a session *below* the floor is worth interrupting for. Ordering for the comparison is `low` < `medium` < `high` < `xhigh` < `max`.

The `Let me change it first` branch exits cleanly without dispatching anything; the skill cannot change the session setting itself.

Read the variable with a single literal Bash call per this repo's `## Bash etiquette` rules — do not compose a shell conditional. When `CLAUDE_EFFORT` is unset (an older CLI, or a launch path that does not export it), **skip the gate rather than firing it unconditionally**: a spurious prompt on every run is worse than a missed advisory.

**Rule: repurpose existing run-start prompts, never add new ones.** The three skills above already have a prompt in that slot. `/quo-plan`, `/quo-status` and `/quo-file-issue` do not, and must not gain one — gating a short skill on a model advisory costs more than the problem it solves. Those stay documented in README only.

This gate is orchestrator-fired and therefore inherits the two-step `TaskCreate` -> `AskUserQuestion` contract per CLAUDE.md `## AskUserQuestion usage`.

### Files

`agents/*.md` (8 files), `skills/quo-execute/SKILL.md`, `skills/quo-fix-issue/SKILL.md`, `skills/quo-breakdown-epic/SKILL.md`, `CLAUDE.md` `## Model assignment in execution skills`, `docs/sdd.md` (the role table at ~44-51, the model-assignment block at ~84-85, and the analyst rationale at ~333), `README.md` if it surfaces the run-start prompt to users.

## Background and rationale

**Why tier at all, when the objective is quality rather than token spend?** Two non-cost reasons, and every sub-`xhigh` row rests on them:

1. **More reasoning does not uniformly improve output.** Effort helps most on open-ended search and diagnosis; it helps least on well-specified mechanical work, where it can push toward over-elaboration.
2. **Wall-clock.** `xhigh` across eight roles times N Subtasks makes an Epic run substantially slower. That is a real cost that is not token spend, and it is the reason the default tier is `high` rather than `xhigh` everywhere.

**Why doc-writer is `high` and not `medium`.** An earlier draft put both doc roles at `medium` on the reasoning that doc work is prose written against a guide. That calibration reflects quorum's *typical* doc workload — appending a `### Feature:` block to a cumulative PRD, updating a README section — and does not generalise. A project whose customer-facing docs are an API reference guide needs systematic extraction of the real contract from source, completeness across many endpoints, and accuracy where an error breaks a downstream integration. That is verification work, not prose, and `medium` is not defensible for it. Since these skills install into projects whose doc surfaces look nothing alike, the pinned tier must serve the demanding case.

Note the division of labour that question surfaced: `agents/doc-writer.md` has `tools: [Read, Edit, Write, Grep, Glob]` — no `Bash`, by design — and its contract limits it to editing markdown. It cannot run a static-site generator, install a dependency or execute a build. Building a documentation *site* is Engineer work (scaffolding, build config, templates, CI); the Doc Writer authors the content that goes into it.

**Known limitation — no per-project effort override.** The pinned table is global: a docs-heavy project and a docs-light one receive the same tiers, and the only escape hatch is hand-editing the installed agent files. Raising doc-writer to `high` mitigates the worst case but does not remove the limitation. If this bites in practice, the follow-up is a CLAUDE.md contract key for per-project effort overrides — deliberately out of scope here, since adding a contract key is a larger change than this ticket warrants.

## Decisions and rejected alternatives

- **Rejected: downgrade the fan-out roles to Sonnet.** An earlier draft moved test-writer, test-reviewer, doc-writer and doc-reviewer to Sonnet on the reasoning that they dominate token spend on a large Epic and buy the least per token. That is a cost optimisation, and cost is not this workflow's objective. Against a quality goal all four are regression risks with no offsetting benefit. Cut entirely — every role stays Opus.
- **Rejected: run everything at `xhigh`.** Wall-clock, per the rationale above. Also worth noting that quorum's documented failure mode is narrate-instead-of-do (`CONTRIBUTING.md` known-limitations, the two-step `TaskCreate` -> `AskUserQuestion` contract), which is instruction adherence rather than reasoning depth — effort nudges it, the existing structural mitigation does more.
- **Rejected: Sonnet orchestrator, Opus workers.** Inverted twice over. Worker frontmatter pins `model: opus` explicitly, so a Sonnet session does not make workers cheaper — it only degrades the seat holding ticket state, dispatch ordering, gate handling and the review loop.
- **Rejected: keep the run-start prompt and add effort to it.** It asks a question the user cannot answer at time zero, before they know whether the Epic is trivial or gnarly, over a grouping ("support roles" = PM + Doc Writer + Doc Reviewer) that is not cognitively coherent. The PM is a gate; the Doc Writer is fan-out.
- **Rejected: add a session-setting gate to every skill.** Gate fatigue is real and quorum already has many gates. Reusing the three existing run-start prompt slots keeps net gate count flat; the short skills stay README-documented.
- **Rejected: have quorum pin session effort via `settings.json`.** An earlier draft proposed checking whether effort is settable in a user's `.claude/settings.json` so the advisory block could be made enforceable. It cannot be done and should not be attempted. Quorum's install surface is the skills and agent files it ships and owns; `settings.json` holds the user's permissions, env vars and hooks, and merging into it is a categorically more invasive act with no mechanism behind it. There is also direct precedent: an earlier revision wrote a `## Skill Paths` section of absolute paths into a tracked file and it was removed (b.963) because per-machine config in a shared file broke multi-engineer collaboration. Quorum writing harness config on the user's behalf is the same class of error. The most it can legitimately do is name the recommended setting and let the user apply it — which is what the advisory block and change 3's gate already do.
- **Considered and rejected: rebase the table upward to use the `max` tier.** The `effort` vocabulary includes a `max` level above `xhigh`. Pinning the two adversarial roles to `max` and the remaining six to `xhigh` would preserve the current level for operators already running xhigh sessions and add headroom on top, so no role would be lowered by this ticket. Rejected on wall-clock: the tiering rationale in Background holds independently of what any individual operator's session happens to be set to, and a per-role table calibrated to one operator's launch flags is not a per-role table. Revisit if the two `xhigh` roles turn out to be the binding constraint on review quality.
- **Deferred: escalate effort on review failure.** Re-dispatching the Engineer at `xhigh` after a Code Reviewer returns findings twice is sound in principle, but it is unproven, adds per-Subtask retry bookkeeping to the orchestrator, and depends on Step 0's question (3) about per-dispatch effort. Not in this ticket.
- **Deferred: build a way to measure whether a quality change helped.** There is no eval harness in this repo, so every tier in the table above is reasoning about what roles do rather than evidence about what they produce. This is a real gap and arguably a more valuable ticket, but it is separate work.

## Doc divergence noted

`CLAUDE.md` `## Repo layout` describes "Seven role contracts" and enumerates seven `agents/*.md` files, omitting `agents/analyst.md`. There are eight. `CLAUDE.md` `## Model assignment in execution skills` likewise omits the Analyst from its always-Opus list. `docs/sdd.md:333` has it right ("The eighth custom-subagent definition file").

This is load-bearing for the present fix: the effort table must cover eight roles, and an engineer working from CLAUDE.md alone would miss the Analyst — which is one of the two `xhigh` rows. Correct both CLAUDE.md sections as part of this work.

