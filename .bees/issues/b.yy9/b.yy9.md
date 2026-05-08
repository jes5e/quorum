---
id: b.yy9
type: bee
title: quo-breakdown-epic Step 7 recommends execute when it should recommend break-down-next;
  rationale truncates in header
parent: null
created_at: '2026-05-05T16:16:29.414353'
status: done
schema_version: '0.1'
guid: yy98rexzdik99r4ainf1x7k91f4hgdh8
reference_materials: null
---
## Description

`quo-breakdown-epic` Step 7's `Pick the Recommended option` block uses 2-way branching (reshape-risk vs. no-reshape-risk), with the "Recommended" badge landing on an execute option in **both** branches. When drafted sibling Epics remain and their dependencies are pure ordering (no contract-reshape risk), the user's intent is to default to **continuing breakdown** of the next Epic — not to start execution. Today the skill recommends bulk-execute in that case, which is the wrong default.

A secondary problem: the rationale ("why this is the recommended pick") is rendered as a free-floating paragraph above the `AskUserQuestion` menu. Observed in a recent run, the paragraph truncated mid-sentence in the Claude Code UI, leaving the user unable to read the reasoning. The Recommended option's `Best when …` subtitle is a more reliable surface.

## Current behavior

`skills/quo-breakdown-epic/SKILL.md` `### 7. Offer Next Steps` → `#### Pick the Recommended option` (lines 498–521 at the time of filing) branches as follows:

- **Reshape-risk case** (any dependent sibling judged to consume an in-flux contract) → Recommended = "In a fresh session, execute this Epic first; defer downstream breakdown".
- **No-reshape-risk case** (default — no dependent siblings, or dependencies are pure ordering) → Recommended = "In a fresh session, execute the whole Bee" (line 521: *"Recommended badge stays on the bulk-execute option as today"*; line 529: *"Recommended in the no-reshape-risk case"* on the bulk-execute menu entry).

Neither branch ever recommends `In a fresh session, break down the next Epic` (line 535) — it exists in the menu but is never the Recommended option.

Observed in two recent runs against `b.5tm`:

1. First run — `t1.5tm.o1` just broken down; drafted siblings `t1.5tm.kn` and `t1.5tm.fy` remained with pure-ordering dependencies. Skill correctly diagnosed no reshape risk → recommended `/quo-execute b.5tm` (bulk execute). Header rationale paragraph truncated in the UI.
2. Second run (after `t1.5tm.kn` was broken down; only `t1.5tm.fy` remained drafted, pure ordering on `kn`) — orchestrator's prose explicitly stated *"This is pure ordering coupling, not contract-reshape risk — t1.5tm.fy could be broken down now and still produce valid Tasks"*, then issued *"Recommendation: open a fresh session and run /quo-execute b.5tm"*. Faithful to the skill's prose; wrong direction by intent.

## Expected behavior

The Recommended-pick logic should be a **3-way branch** keyed on two facts already gathered in Step 7:

1. Are any drafted sibling Epics still in `drafted` state under the parent Bee? (existing query at lines 502–508 already produces this)
2. Among siblings whose `up_dependencies` includes the just-broken-down Epic, is there reshape risk? (existing judgment at lines 512–517 stays unchanged)

Mapping:

- **No drafted siblings remain** → Recommended = *"In a fresh session, execute the whole Bee"*. Rationale: planning is done; ready to ship.
- **Drafted siblings remain, reshape risk present** → Recommended = *"In a fresh session, execute this Epic first; defer downstream breakdown"*. Rationale: name the at-risk siblings (ID + short title) and the contract concern.
- **Drafted siblings remain, no reshape risk** → Recommended = *"In a fresh session, break down the next Epic"*. Rationale: name which siblings are still drafted and why their Tasks won't go stale.

Rationale must live on the Recommended option's `Best when …` subtitle (one short sentence, ≤ ~150 chars). Forbid the freestanding header paragraph — the Claude Code UI does not render it reliably.

The reshape-risk judgment criteria at lines 512–517 (rewrites-to-consume vs. pure ordering) are sound and should be retained unchanged. Only the **direction** of the recommendation in the no-reshape-risk case flips.

The menu options at lines 527–540 should retain their `Best when …` subtitles (these double as the rationale slot when the option is the Recommended pick); the menu count tightening called out in earlier discussion is **separate, optional cleanup** and is not part of this fix.

## Impact

User confusion at the end of every `quo-breakdown-epic` run that has remaining drafted Epics with pure-ordering dependencies — i.e., the common case for cleanup-style or sequential-rollout Bees. Users who follow the Recommended badge end up executing partially-planned Bees instead of finishing the plan first, which contradicts the documented "finish planning before any execution starts" intent for the no-reshape-risk path. The truncated rationale paragraph compounds the confusion: the user cannot see *why* the skill chose the recommendation it did.

## Suggested fix

Edit `skills/quo-breakdown-epic/SKILL.md` Step 7:

- **`#### Pick the Recommended option`** (lines 498–521): replace the 2-way branching with the 3-way mapping described in *Expected behavior*. Keep the existing query (step 1) and reshape-risk judgment criteria (step 3 + lines 512–517) unchanged. Update step 4's branch list to the three cases. Move rationale guidance from "include a one-line rationale ... in the prose" to "set the Recommended option's `Best when …` subtitle to the one-line rationale".
- **`#### Menu options`** (lines 523–540): update the `*Recommended in the …*` annotations on the three Recommended-eligible options:
  - "execute the whole Bee" → *Recommended when no drafted Epics remain.*
  - "execute this Epic first; defer downstream breakdown" → *Recommended when drafted siblings present reshape risk.*
  - "break down the next Epic" → *Recommended when drafted siblings remain with no reshape risk.*
- Add an explicit prohibition (in `#### Pick the Recommended option`) on emitting a freestanding header paragraph above the `AskUserQuestion` menu; the rationale belongs on the option subtitle.

Out of scope for this issue:
- Tightening the option count (currently six core options + auto-appended "Type something" / "Chat about this"). Worth doing later but not load-bearing for the recommendation-direction fix.
- Changes to the reshape-risk judgment criteria themselves — they are working as intended.
