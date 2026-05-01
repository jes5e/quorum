---
id: b.6e6
type: bee
title: Polish nits in /bees-setup fast-path prose and detect_fast_path.py
up_dependencies:
- b.kpt
status: open
created_at: '2026-05-01T17:28:23.704190'
schema_version: '0.1'
egg: null
guid: 6e6jcv5x9qrfftybqreitdusshooc5b2
---

## Description

Three polish-level findings from the post-completion review of `b.kpt` (commits `8d5f446` and `240f0bd`). All non-blocking; deferred from that session by the team-lead with the user's agreement, and bundled here so they don't rot. Pick up whenever the b.kpt fast-path prose is next being touched.

## Findings

### 1. `skills/bees-setup/SKILL.md:121` — slow-path entry-point prose imprecise

The fast-path-ineligible fall-through says "fall through to the existing slow path starting at *Per-machine Claude Code settings* below." That's correct, but the wording implies a single entry point — in practice the slow path's next stop after settings is *Resolve bundled helper script paths* (around line 410), and on the same-machine no-regression case from acceptance criterion 3 the user just confirms settings and continues. Not strictly wrong, just slightly awkward and depends on the agent reading the next section linearly.

**Suggested fix:** sharpen the prose to name both the entry section and what comes after — e.g. "…starting at *Per-machine Claude Code settings*; if those are already configured, the slow path continues to *Resolve bundled helper script paths*."

### 2. `skills/bees-setup/SKILL.md:198` — flow-control "return here" instruction lacks anchor

Option 2 of the condensed-prompt branch tells the agent to "fall through to the slow path's *Per-machine Claude Code settings* section for the per-setting walk-through, then return here for *Confirm and exit*." "Return here" is a flow-control instruction with no explicit anchor — Claude has to maintain the return-pointer mentally. The matching Confirm-and-Exit option-2 (line 212-ish, post-fix) cleanly says "skip ahead to the next slow-path section" with explicit naming.

**Suggested fix:** rewrite to "after completing the slow path's *Per-machine Claude Code settings* section, jump back up to *Confirm and exit* in the fast-path branch." Or restructure so the fast-path branch's exit doesn't depend on a remote return.

### 3. `skills/bees-setup/scripts/detect_fast_path.py:194` — `_BULLET_RE` could use a docstring noting expected bullet shape

The regex `^\s*-\s+\*\*(?P<key>[^*]+?)\*\*\s*:\s*(?P<value>.*?)\s*$` requires the bullet text be wrapped in `**bold**`. The contract emitter elsewhere in SKILL.md always emits this form, so it's fine in practice — but if a user hand-edits CLAUDE.md to drop the bold (or uses a different emphasis style), the detector silently reports the section as not-set-up and re-prompts the slow path. That's acceptable defensive behavior.

**Suggested fix:** add a brief comment above `_BULLET_RE` documenting the expected bullet shape (`- **Key**: value`) and the silent fallback semantics so future maintainers don't loosen the regex without realising they'd be widening the parse to match malformed CLAUDE.md.

## Why bundled

All three are 1- to 3-line edits in the same two files, all in the new fast-path branch. They share the same 'I just opened SKILL.md' attention budget for whoever picks them up. Splitting into three tickets would be more bookkeeping than the work.

## Out of scope

These are nit-level. They don't affect correctness on the happy path, the cross-platform contract, or the contract keys. The two substantive portability findings from the same review (PowerShell quoting, Windows path-separator normalization) and the one substantive spec finding (unknown-hive fall-through) were fixed in commit `240f0bd`.

## Acceptance criteria

- All three nits addressed in one commit (or three small commits, whichever).
- Lint stays clean (`python -m pyflakes skills/*/scripts/*.py`).
- No semantic change to the fast-path or slow-path control flow — purely prose polish on (1) and (2), purely documentation comment on (3).
