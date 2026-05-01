---
id: b.iaz
type: bee
title: AskUserQuestion misused for open-ended questions across skills (renders confusing 'Pick Other' UX)
status: open
created_at: '2026-05-01T12:09:33.348285'
schema_version: '0.1'
egg: null
guid: iazhxdfa3r9xqvsuwn4sv8st6byax76p
---

## Description

Several skills wrap genuinely open-ended questions in `AskUserQuestion`, which is a multiple-choice tool. Claude Code auto-appends `Type something.` (free-text input) and `Chat about this` (escape) to every `AskUserQuestion` call. When a skill adds its own redundant "type your own answer" options on top of that, the result is a self-referential UI where option descriptions point at a labeled-but-nonexistent "Other" choice (the free-text slot is rendered as `Type something.`, not `Other`).

## Current behavior

Concrete example seen running `/bees-setup` on 2026-05-01: the "non-goals" bootstrap question rendered as:

1. **Use my own answer** — description: "Pick 'Other' and list non-goals."
2. **None come to mind right now** — description: "Leave the non-goals section as a placeholder; fill in later as features are planned."
3. **Type something.** (auto-appended free-text)
4. **Chat about this** (auto-appended escape)

Problems:
- Option 1's description tells the user to pick `'Other'`, but the UI has no option labeled `Other` — the free-text slot is rendered as `Type something.`
- Option 1 is functionally redundant with option 3 (the auto-appended free-text slot already exists)
- The user reported the prompt as confusing

This is a recurring anti-pattern, not a one-off. Audit found six locations:

| Location | Anti-pattern |
|---|---|
| `skills/bees-setup/SKILL.md:583, 594-597` | 4 open-ended bootstrap questions (elevator pitch, why, non-goals, observable behavior) wrapped in a single `AskUserQuestion` call. The skill prose explicitly says "ask the open-ended ones in a follow-up `AskUserQuestion` call." |
| `skills/bees-setup/SKILL.md:485-495` | Doc-location prompts use `"Yes, here's the path: ___"` as option labels. The `___` suggests fill-in-the-blank, which `AskUserQuestion` does not support. |
| `skills/bees-setup/SKILL.md:454` | "Use `AskUserQuestion` to ask the user where each missing hive should live" — asking for a filesystem path is a free-text question. |
| `skills/bees-plan/SKILL.md:22-24` | "Before I start researching, is there anything I should know? For example: reference implementations, existing services to look at..." — open-ended context gathering. |
| `skills/bees-plan/SKILL.md:69-73` | "What problem does this solve? / What's the scope? / Are there constraints or preferences? / Any dependencies on other work?" — all open-ended. |
| `skills/bees-plan-from-specs/SKILL.md:18` | "If the caller does not provide both paths, ask them for the missing one(s) using `AskUserQuestion`." — asking for file paths. |

## Expected behavior

`AskUserQuestion` is for prompts with a small finite set of meaningful choices (e.g., proceed/skip/abort, model picker Opus/Sonnet, branch-handling options). For genuinely open-ended questions ("what is the elevator pitch?", "what file path?", "what's the scope?"), the skill should print the question as plain prose and let the user reply in the next conversational turn — no `AskUserQuestion` call at all.

For prompts that *are* multi-choice but include a "let me type my own" path, the skill should rely on the auto-appended `Type something.` slot rather than adding a redundant option, and option labels must not contain `___` placeholders or reference a fictional `Other` label.

## Impact

- **UX**: users hit confusing prompts that reference labels they cannot see, and have to guess which option to pick.
- **Workflow correctness**: when a user asks for a free-text path via `AskUserQuestion`, picking option 1 may not produce a usable answer in the next turn — the model has to re-prompt or improvise, slowing the skill down.
- **Skill quality signal**: this pattern shows up in four of the eleven core skills, suggesting the issue is in the skills' shared mental model of `AskUserQuestion`, not isolated authoring mistakes.

## Suggested fix

For each affected location:

1. **`bees-setup` Step B (lines 583, 594-597)** — change "ask the open-ended ones in a follow-up `AskUserQuestion` call" to "ask the open-ended ones as plain prose in a single message; let the user reply in their next turn." The four questions remain a batch but are presented as a numbered prose list, not a tool call.

2. **`bees-setup` lines 485-495 (doc location table)** — for each row, drop the `___` suffix from option labels. The "Yes, here's the path" option should be re-shaped: either ask via prose ("What's the path to your PRD?") or use `AskUserQuestion` only for the high-level decision (provide path / generate / skip) and then prompt for the path as prose if the user picked "provide path."

3. **`bees-setup` line 454** — change to plain prose for hive paths, optionally with `AskUserQuestion` only when offering a recommended default vs. an explicit "let me type a different path" path.

4. **`bees-plan` line 22-24 (pre-research context)** — print the question as prose, no `AskUserQuestion`.

5. **`bees-plan` lines 69-73 (clarifying questions)** — print as a prose-numbered list, no `AskUserQuestion`. The user will answer them in their reply.

6. **`bees-plan-from-specs` line 18** — print "I need the path to the PRD/SDD; please provide it." as prose.

Add a short principle to the project's CLAUDE.md (or a "skill-authoring-notes" doc if one is created) capturing the rule:

> **`AskUserQuestion` is multi-choice only.** It auto-appends `Type something.` and `Chat about this`. Use it when there is a small finite set of meaningful choices. For free-text answers (paths, descriptions, names), ask in prose and let the user reply normally — do NOT add fake "Use my own answer" / "Pick Other" options that point at the auto-appended slot.

This is a workflow-level guidance issue, so the fix is documentation + the six skill edits above. No tests to add (no test suite exists for this repo).
