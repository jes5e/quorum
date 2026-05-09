---
id: b.v4g
type: bee
title: Harden /quo-file-issue inline-dispatch handoff prose for /quo-fix-issue
status: open
created_at: '2026-05-08T22:06:16.053831'
schema_version: '0.1'
reference_materials: null
guid: v4g2tmwxfytuh7e6njkpswzwtjrxxe79
---

## Description
The post-inline-dispatch handoff prose between `/quo-fix-issue`'s URL-resolution sub-step and `/quo-file-issue`'s "Inline invocation via the Skill tool" contract is under-specified, making it easy for an orchestrator to misread the structured return as a workflow exit instead of a sub-step hand-off — and silently file the Issue without continuing to the fix.

## Current behavior
When `/quo-fix-issue <url>` runs, Section 1's URL-resolution sub-step dispatches `/quo-file-issue` inline via the Skill tool. After the inline dispatch returns:

- `/quo-file-issue`'s "Inline invocation via the Skill tool" → "Output shape" / "Behavioral guarantees" sections describe a structured `issue_ticket_id` / `action` return "so the caller can wire its own follow-up state." The "return ... to the caller" framing reads like a process boundary even though Skill-tool inline dispatch runs in the same conversation; nothing in the contract section explicitly says "on the inline path the structured return is a hand-off marker, not a stop — control resumes in the caller skill's flow."
- `/quo-fix-issue` Section 1's URL-resolution sub-step ends with the post-resolution working-list display. The only forward-pointer to Step 2 is a parenthetical *"BEFORE the upstream `bees show-ticket --ids` validation pass at the top of step 2"* buried mid-sentence in the display sub-step. There is no explicit terminator like *"After this sub-step completes, proceed to the upfront validation pass and then Step 2 — the URL-resolution sub-step is part of Section 1, not a replacement for the rest of `/quo-fix-issue`."*
- `/quo-file-issue` Step 5's "Report back" output (the bullet list naming ticket ID, title, etc.) visually mimics a completed-workflow summary on the inline path. Under context pressure an orchestrator naturally treats it as the run's terminal output.

In a real session in this repo, the orchestrator filed Issue b.6z8 from URL https://github.com/jes5e/quorum/issues/1 and then stopped, never proceeding to validate / dispatch / fix / commit-as-done. The user had to point this out and resume the run manually.

## Expected behavior
After the inline `/quo-file-issue` dispatch returns its structured payload, the orchestrator continues `/quo-fix-issue`'s flow at the post-resolution working-list display, then the upfront `bees show-ticket --ids` validation pass, then Step 2 (validate Issue), Step 3 (per-issue Agent dispatch), Step 4 (review loop), Step 5 (doc verify), Step 6 (mark Issue done + commit), and Step 7 (post-completion review) — exactly as it would for a user-typed `/quo-fix-issue <issue-id>` invocation.

The skill prose should make this hand-off obvious enough that another engineer (or another LLM orchestrator) reading the prose cold cannot mistake the inline-dispatch return for a workflow exit.

## Impact
- **Correctness — silent half-runs.** A `/quo-fix-issue <url>` invocation that stops after filing leaves the user with a freshly-filed but unfixed Issue and a misleading "I'm done" signal. The user has to notice and manually resume.
- **Repeatability — recurs across machines / engineers / LLMs.** The slip is a function of the prose, not of the specific orchestrator that ran. Anyone running `/quo-fix-issue <url>` in any project on any machine is exposed to the same ambiguity.
- **Trust in the URL-mode shorthand.** The shorthand's value (typing a URL instead of filing-then-fixing in two commands) depends on the orchestrator reliably running both halves. A flaky hand-off undermines the reason the shorthand exists.

## Suggested fix
Three small prose hardenings, scoped to the URL → file-then-fix composition direction only — pure-ID `/quo-fix-issue` invocations and user-typed `/quo-file-issue` invocations are unaffected:

1. **`skills/quo-file-issue/SKILL.md` → `## Inline invocation via the Skill tool`** — add an explicit "this is a hand-off, not an exit" callout. The structured return is a marker for the caller to consume, *not* a workflow termination; on the Skill-tool inline path the "caller" is the same conversation, so the parent skill's flow continues after the return. Place the callout in the "Output shape" or "Behavioral guarantees" sub-section so any future inline caller reads it inline with the rest of the contract.

2. **`skills/quo-fix-issue/SKILL.md` → Section 1's URL-resolution sub-step** — add an explicit terminator at the end of the sub-step: *"After every URL token in the working list has been resolved (or soft-failed) and the post-resolution working-list display has fired, the URL-resolution sub-step is complete. Continue Section 1 at the upfront `bees show-ticket --ids` validation pass, then proceed to Step 2 (Validate Issue) — the URL-resolution sub-step replaces nothing else in `/quo-fix-issue`'s flow."*

3. **`skills/quo-file-issue/SKILL.md` → Step 5 ("Report back")** — note that on the inline-dispatch path, the human-readable bullet list is supplemental to the structured payload and does not signify run completion of the calling skill. The user-typed slash-command path keeps Step 5's report-and-exit semantics unchanged.

Also worth verifying: the user-typed `/quo-file-issue <url>` path (no caller) and pure-ID `/quo-fix-issue` paths (no inline dispatch) still report-and-exit / continue normally after these prose tweaks. The fix is observation-only on those paths.

## Background and rationale
This issue surfaced during a real session in the quorum repo on 2026-05-08. The user invoked `/quo-fix-issue https://github.com/jes5e/quorum/issues/1`. The orchestrator verified preconditions, asked for isolation strategy, dispatched `/quo-file-issue` inline via the Skill tool, ran the External-reference branch end-to-end (dedupe → URL fetch via `gh issue view` → thin-body authoring → `bees create-ticket --reference-materials` → scratch-file commit `9029686`), returned a structured payload (`issue_ticket_id: b.6z8`, `action: created`), and **stopped** — emitting a "Returning control to caller" summary line and yielding the turn without proceeding to Step 2.

Root-cause analysis:
- The **load-bearing failure** was the orchestrator misreading `/quo-file-issue`'s structured return as a workflow termination. That misread is itself rooted in two prose ambiguities: (a) the "caller wires its own follow-up state" framing in `/quo-file-issue`'s contract section reads like a process boundary even though Skill-tool inline dispatch is in-conversation, with no sentence binding "caller" to "same orchestrator continuing the parent skill's flow"; and (b) `/quo-fix-issue` Section 1's URL-resolution sub-step has no explicit "now continue at Step 2" terminator — only a parenthetical buried in the working-list display sentence.
- A secondary contributor: `/quo-file-issue`'s Step 5 "Report back" emits a bullet-list summary that visually mimics a completed-workflow summary; on the inline path, that visual cue compounds with the contract-section framing.

Root causes ruled out:
- **Skill-tool inline-dispatch contract correctness.** `/quo-file-issue` ran end-to-end correctly: dedupe fired, External-reference branch executed, ticket filed at `status=open`, structured payload emitted, commit landed. No bug in the dispatched skill itself.
- **Specific-orchestrator artifact.** The slip is a function of the prose, not the orchestrator instance — the same prose would mislead another engineer (or another LLM) reading it cold.
- **`/quo-fix-issue`'s URL-token classifier.** The classifier (per b.ahr — commit `23d083b`) is correct; the URL was tokenized as a URL token and the sub-step ran. The gap is downstream, in the post-sub-step continuation.
- **Memory-rule interference.** A user-memory entry exists for the support-model prompt, but it only suppresses that one AskUserQuestion. No bearing on the post-inline-dispatch continuation.

Trade-offs surfaced:
- **Scope discipline — do NOT introduce auto-chain in the reverse direction.** A naïve reading might tempt an editor to also add a "user-typed `/quo-file-issue <url>` chains into `/quo-fix-issue`" auto-flow. Out of scope: the composition is one-way. The fix targets only the post-dispatch handoff inside `/quo-fix-issue`'s URL-mode path and `/quo-file-issue`'s inline-invocation contract section.
- **Don't strengthen by deleting Step 5's report-and-exit semantics.** On the user-typed slash-command path, Step 5 is correctly a final summary. The prose tweak should differentiate inline-vs-user-typed without removing existing behavior.

## Decisions and rejected alternatives
**Chosen path:** prose-only hardening at three sites (the two skills' relevant sections), scoped narrowly to the inline-dispatch handoff. No code/control-flow change. No new mechanism.

**Rejected alternative — auto-chain `/quo-file-issue` → `/quo-fix-issue` on user-typed `/quo-file-issue <url>` invocations.** Tempting because it would "complete the same end-to-end behavior" the user expected. Rejected: the composition direction is intentionally one-way; chaining backward would surprise users who genuinely want to file-and-stop (e.g., capturing a bug to triage later). The fix should not change which entry points trigger fixes.

**Rejected alternative — change `/quo-file-issue`'s Step 5 "Report back" to suppress its bullet list on the inline path.** Tempting because the bullet list is part of what visually misleads the orchestrator. Rejected: the bullet list is informationally useful even on the inline path; the right tweak is a callout that distinguishes "report" from "exit," not removing the report.

**Rejected alternative — push the fix into `/quo-fix-issue`'s reconciliation loop instead of the prose.** Tempting because Section 3 already does state-driven reconciliation. Rejected: Section 3's loop is per-issue and starts *after* the URL-resolution sub-step completes; tweaking the loop would not address the gap, which is in Section 1's sub-step boundary.

