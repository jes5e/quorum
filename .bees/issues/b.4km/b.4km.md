---
id: b.4km
type: bee
title: bees-fix-issue Section 7 fix-in-session branch missing TaskList close-out
status: open
created_at: '2026-05-05T16:50:00.559645'
schema_version: '0.1'
guid: 4kmr6ka5e17bembfdfu11zyapcxy3q4g
reference_materials: null
---
## Description

`skills/bees-fix-issue/SKILL.md` Section 7 step 6's **"Fix in this session"** branch lacks explicit TaskList lifecycle guidance for the follow-up Agents it dispatches. The orchestrator can dispatch a follow-up Agent, mark its TaskList task `in_progress`, and never flip it to `completed` after the Agent returns — leaving stale `in_progress` entries in the TaskList UI after the session ends.

Observed in a `/bees-fix-issue` run on 2026-05-05: a follow-up Doc Writer dispatch named `doc-writer-postcomp` (post-completion fresh-review remediation) was left at `in_progress` after the Agent returned. The user noticed the stale UI state and asked whether a subagent was still running. It was not — the orchestrator simply didn't run the close-out.

## Current behavior

Section 7 step 6 currently says:

> **Fix in this session**: Dispatch fresh ephemeral Agents per Section 3's dispatch shape (Engineer / Test Writer / Doc Writer as needed) to address the findings. Stay in delegate mode. After fixes are done, commit.

Two pieces are missing:

1. **No naming convention extension.** Section 3's TaskList naming convention is *issue-scoped* (`<role>-<issue-id>`). Post-completion follow-up Agents are not tied to a single issue ID — they address findings spanning the whole session — so there is no canonical name to use. The orchestrator has to invent one (the 2026-05-05 run picked `doc-writer-postcomp` ad hoc).
2. **No close-out instruction.** Section 6 step 3 explicitly closes out TaskList tasks at issue close-out, but it is *per-issue scoped*: *"Mark the per-issue TaskList tasks … as `completed`"*. Section 7 step 6's "Fix in this session" branch has no parallel close-out step. The orchestrator implicitly inherits TaskList tracking from "per Section 3's dispatch shape" but the inheritance is fragile — a careful reader can infer "track via TaskList", but the close-out step is not visibly anchored anywhere applicable to follow-up Agents.

## Expected behavior

Section 7 step 6's "Fix in this session" branch should:

1. Specify a TaskList naming convention that covers post-completion follow-up Agents (e.g., `<role>-postcomp` or `<role>-followup-<short-suffix>`). Either is fine — pick one and bake it in.
2. Add a parallel close-out step: "When each follow-up Agent returns, mark its TaskList task `completed` (and confirm any bees ticket transitions the worker committed to)." Mirror the wording of Section 3's reconcile-on-completion paragraph and Section 6 step 3.

Optional but worth considering: extend the same fix to Section 7 step 6's **"File as issue tickets"** branch — that branch invokes `/bees-file-issue` per finding, which doesn't dispatch Agents, but the same close-out discipline (mark whatever TaskList progress entries the orchestrator created during Section 7 as `completed`) applies.

## Impact

User-visible UX bug: stale `in_progress` TaskList entries after a `/bees-fix-issue` session that took the Section 7 "Fix in this session" path. The user has to mentally distinguish "agent still running" (real in-flight work) from "orchestrator forgot to close out" (stale UI state). For interactive sessions this is small but annoying; for sessions where the user steps away and comes back, the stale state is confusing.

No correctness impact — the work itself completed; only the progress-UI bookkeeping is wrong.

## Suggested fix

Edit `skills/bees-fix-issue/SKILL.md` Section 7 step 6's "Fix in this session" branch:

1. Add a sentence specifying the TaskList naming convention for follow-up Agents (e.g., `<role>-postcomp`).
2. Add an explicit close-out instruction: "When each follow-up Agent returns, mark its TaskList task `completed`."
3. Optionally also touch up the "File as issue tickets" branch with the same close-out discipline if the orchestrator created any TaskList entries during Section 7.

Out of scope:

- Section 6 step 3's per-issue close-out is fine as written — this fix is purely additive at Section 7 step 6.
- No change to Section 3's naming convention itself; the fix at Section 7 step 6 *extends* the convention to post-completion scope without modifying the issue-scoped form used in Section 3.
- No change to `bees-execute/SKILL.md` — Section 7 of `bees-fix-issue` has no parallel in `bees-execute` (which has a different post-completion review structure).

