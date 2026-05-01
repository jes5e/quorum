---
id: b.yf9
type: bee
title: 'Post-completion review: spawn fresh generalist agent instead of /bees-code-review'
parent: null
egg: null
created_at: '2026-05-01T10:32:49.439820'
status: done
schema_version: '0.1'
guid: yf981x6hbphk387mw36uww1q4ufeaqq2
---

## Description

The post-completion review step in /bees-fix-issue (Step 8) and /bees-execute (Step 6) currently invokes /bees-code-review. Two compounding problems with that:

1. **/bees-code-review explicitly ignores natural-language documentation.** The skill prose says "Focus only on source code files. Ignore natural language documentation and unit test code." That's correct *as one lane of a three-lane in-flight review* (code/doc/test in parallel) — but at the post-completion stage it leaves prose changes unreviewed, which is unsafe for doc-heavy fixes (e.g. b.9sv had 5 of 8 changed files as pure prose).

2. **The team-lead is the wrong agent to do post-completion review.** By construction, the team-lead has been delegating the whole run, accumulating: every prompt it wrote for each subagent (with framing of what to look at), every final report from those agents (with their rationale and decisions), the PM verdict, both reviewers' verdicts, the issue body, and the team-lead's mental model of the phases. That context is loaded with confirmation bias. When the team-lead reads the diff, it asks "did the four phases get done correctly?" not "is this good?". The in-flight Code/Doc/Test Reviewers work *because* they get fresh contexts via subagent spawn; the team-lead doesn't, by accident of accumulating orchestration.

The combined effect on b.9sv (the run that surfaced this finding): the post-completion check ran as /bees-code-review with team-lead context, dutifully ignored prose because the skill said to, and would have missed any wording drift across the README/CLAUDE.md/sdd.md/skill prose triangle if it had occurred. The fact that the in-flight Doc Reviewer caught an omission (the README skill catalog row) earlier in the run means doc review is genuinely valuable; skipping it at the final sweep is a real gap.

## Current behavior

`skills/bees-fix-issue/SKILL.md:335` ("### 8. Post-Completion Code Review"):
> Invoke the /bees-code-review skill against all changes made during this session

`skills/bees-execute/SKILL.md:444` ("### 6. Post-Completion Code Review"): same shape, same skill invocation.

Both run as the team-lead (the orchestrating agent), both use /bees-code-review, both inherit its "ignore docs" scope.

## Expected behavior

Both Step 8 (fix-issue) and Step 6 (execute) become a single fresh-context generalist review:

- **Spawn a fresh general-purpose agent** (subagent_type=general-purpose, NOT a custom reviewer agent type). The team-lead does not do this work directly.
- **No skill invocation in the spawned agent's prompt.** Specifically: do NOT instruct it to call /bees-code-review or /bees-doc-review or any review skill. The whole point is to escape those skills' lane limitations.
- **Hand it scope explicitly**: the diff range or commit list for the work just completed, plus the issue body (or Bee body for execute) it claims to fix. The agent computes the diff itself via git, reads the issue via `bees show-ticket --ids <id>`.
- **No lane scope in the prompt.** Tell the agent to flag anything that looks wrong: code issues, prose issues, spec drift, missing edits, contract-key violations, cross-file inconsistencies. One generalist pass covers code AND docs AND tests.
- **Return findings as a numbered list with severity (blocker / suggestion / nit) and file:line.**
- **Team-lead synthesizes**: takes the fresh reviewer's findings, compares against in-flight review history (which the team-lead does still have in context), uses the same AskUserQuestion (Fix in this session / File as issue tickets / Skip) flow that already exists.

## Anti-pattern to call out explicitly in the new prose

The implementing agent will be tempted to "be helpful" and reuse /bees-code-review with a flag like "review docs too". Do not. The new step's prose must explicitly say:

> Do NOT invoke /bees-code-review, /bees-doc-review, or /bees-test-review at this stage. Those skills are designed as parallel lanes of an in-flight review; they each have lane-specific scope rules that make them wrong for a final generalist sweep. Spawn a fresh general-purpose agent with a self-contained prompt instead.

## Files to modify

- `skills/bees-fix-issue/SKILL.md` — rewrite Step 8 ("Post-Completion Code Review", currently at line 335) per the spec above. Rename the step heading from "Post-Completion Code Review" to "Post-Completion Review" (drop "Code" — it's no longer code-only).
- `skills/bees-execute/SKILL.md` — rewrite Step 6 ("Post-Completion Code Review", currently at line 444) symmetrically. Same heading rename.
- `README.md` and `docs/sdd.md` were checked at filing time — neither references "post-completion" by name, so no updates needed there. If the implementer's edit changes that (e.g., introduces user-facing terminology for the step), update the customer-facing doc accordingly.

## Suggested fix

Concrete prompt skeleton the new step should produce when spawning the fresh reviewer:

```
You are an independent reviewer for a bees-workflow fix that was just shipped.

Scope: review the diff for HEAD~N..HEAD (compute via git) against the issue/Bee body
(read via `bees show-ticket --ids <id>`). The orchestrating team-lead has finished
the work — your job is to give it a fresh-eyes review with no context of how
the work was done.

Flag anything that looks wrong: code defects, prose problems, spec drift between
the change and the issue, contract-key violations (do not allow renames of keys
in CLAUDE.md ## Documentation Locations or ## Build Commands), cross-file
inconsistencies, missing edits the issue called for.

Do NOT do a general repo audit. Stay focused on the diff.

Return findings as a numbered list. For each item: file:line, what's wrong,
severity (blocker / suggestion / nit). Or "no issues found".
```

Plus the explicit anti-pattern call-out in the SKILL.md prose:

> Do NOT invoke /bees-code-review, /bees-doc-review, or /bees-test-review at this stage.

The team-lead-side flow stays mostly the same: receive the reviewer's findings, present to the user with the existing AskUserQuestion (Fix in this session / File as issue tickets / Skip).

## Out of scope

- **The in-flight review loop** in /bees-execute Step 5 ("Final Bee-level Code, Doc and Eng reviews", line 404) and /bees-fix-issue Step 4 ("Review Loop"). Those still use the three lane-specific review skills and that's correct — they are parallel lanes of the work, not a final synthesis pass.
- **Test coverage of the change.** This issue is purely about the post-completion step's design. Test-writing concerns are handled inside the in-flight review loop.
- **/bees-code-review's own prose.** The "ignore documentation" instruction is correct *for that skill's role* (one lane of a three-lane review). Don't change /bees-code-review.

## Impact

- Post-completion sweep actually catches doc/spec drift on doc-heavy fixes — closes the gap that b.9sv would have hit had any wording inconsistency slipped through.
- Eliminates orchestration bias from final review — the team-lead is structurally the worst agent in the system to do this review and the new design moves it to a fresh agent.
- Single-pass generalist review at the end is also more aligned with how a real engineer reviews their own diff before pushing — read the whole thing, look for any kind of problem, not three separate passes.

## Adjacent finding (note, do not bundle)

The b.9sv "ignore documentation" gap was *masked* by the in-flight Doc Reviewer doing its job. A future fix that bypasses or fails to spawn the Doc Reviewer in the in-flight loop would have no doc review at all. Worth a separate audit later: does any /bees-fix-issue or /bees-execute path skip the Doc Reviewer? Out of scope for this ticket.
