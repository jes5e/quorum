---
id: b.cj2
type: bee
title: 'Re-probe upstream Claude Code context-window capabilities (#33026 self-compact, #34879 model-readable usage, #27969 hook-visible usage)'
status: open
created_at: '2026-08-15T18:09:38.166403'
schema_version: '0.1'
reference_materials: null
guid: cj2k4ndfjf6imnjqgwtvpmnxfgsgqcth
---

## Description

Track three open Claude Code upstream feature requests whose resolution would let quorum simplify — or make universal — its context-window handling (the state-externalization discipline in Issue b.ja9 and the statusline-fed context guard planned separately). This is a long-lived **periodic re-probe** Issue in the same spirit as b.x9w — do not close it on a single check; append a dated re-test line and leave it open until one of the tripwires below fires.

## Current behavior

quorum works around three gaps in today's Claude Code, all confirmed 2026-08-14/15 against official docs and live probes:

- **The model cannot clear or compact its own context.** `/clear` and `/compact` are user-only; auto-compaction fires automatically at ~83% of the window. → tracked upstream as **anthropics/claude-code#33026** ("Allow Claude to self-initiate context compaction").
- **The model has no native read of its own context usage.** No injected low-context warning, no env var, `/context` is user-only. quorum reads usage indirectly via a statusline script that writes a per-session gauge file. → tracked upstream as **anthropics/claude-code#34879** ("Expose context window usage metrics to Claude for self-analysis") and **#26340**.
- **Hooks cannot see context usage either.** A hook-based producer would be more robust than a statusline one, because hooks *merge* across settings sources while `statusLine` is a winner-takes-all slot (so a hook producer would work even in environments that pin the statusline, e.g. the claude-secure-container wrapper). → tracked upstream as **anthropics/claude-code#27969** ("Expose context window usage percentage to hooks").

## Expected behavior

Periodically (e.g. when a new Claude Code release ships), re-check the three requests. Trigger actions:

- **#33026 ships (model can self-compact):** the original "clear your working context at the Epic boundary" instruction becomes literally executable. Revisit b.ja9's rewrite — the state-externalization framing can regain a real active-clear step.
- **#34879 ships (model-readable usage):** the orchestrator can ask "how full am I?" natively. The entire statusline-bridge apparatus from the context-guard feature (bridge script, quo-setup install step, per-session gauge file, session-id lookup) becomes removable — replace with a direct read.
- **#27969 ships (hook-visible usage):** move the gauge producer from a statusline script to a hook, making the context guard work even in pinned-statusline environments with no per-environment producer — i.e. universal.

On each re-probe that finds no change, append a one-line dated note (`re-tested YYYY-MM-DD on Claude Code vN.N.N — still open`) and leave this Issue open. Close only when all three have either shipped-and-been-adopted or been permanently abandoned.

## Impact

Maintainer-guidance / audit-trail. Without this Issue, a future maintainer sees the statusline bridge and the state-externalization prose, has no idea they exist only because these upstream gaps hadn't closed, and either cargo-cults them forever or "cleans them up" without understanding what they compensate for. This ticket pins the rationale and the tripwires for revisiting, exactly as b.x9w did for the warm-Agent/SendMessage gap.

## Background and rationale

Filed alongside b.ja9 (the honesty rewrite of the Epic-boundary discipline) and the separately-planned context-guard feature, out of the same 2026-08-14/15 investigation. All three upstream references were read directly during that investigation; the statusline gauge mechanism (`/tmp/.quorum/context-usage-<session_id>.json`, fields `context_window.used_percentage` etc.) was verified working on both a corporate-managed host and inside claude-secure-container. `CLAUDE_CODE_SESSION_ID` is exported to Bash today, which is what makes the gauge-file lookup possible without any of the above shipping.

