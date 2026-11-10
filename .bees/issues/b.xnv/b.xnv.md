---
id: b.xnv
type: bee
title: 'Keep code organized: new code goes in the module whose responsibility it is, and a needed split is part of the fix'
status: open
created_at: '2026-11-10T18:47:20.455445'
schema_version: '0.1'
reference_materials: null
guid: xnvq8s9vw2n1k8vk4nx74us4g6yu7oxh
---

## Description

Quorum should keep code organized: new code goes in the module whose responsibility it is, and files don't grow into monoliths. Today nothing in quorum asks for that, and one rule actively defers it. The operator agreed on 2026-11-10 to make this a general engineering goal, not only an enforcement of a project's own size rules. A project with no size rules still gets the goal; a project that has them supplies the concrete bar.

### The evidence (a real-run failure, so a kind-5 goal is earned)

live_edit's root-cause report is `~/.quorum-scratch/rootcause-bloat-p4.md` (2026-11-09):
- Six `src` files grew from 23k to 165k lines in about 800 commits across about 30 quorum lanes. About 55% came from fix-issue and 30% from plan Tasks.
- Nothing was ever split. Six child modules were created, all for new code, never to move existing code out.
- In two months, no reviewer finding, PM report, Analyst proposal or decider ruling flagged size or structure. Ninety-four functions over 300 lines and 17 files over 10k lines drew zero findings.

Three questions: it happened continuously, it was silent, and it was never recovered unaided.

### What in quorum causes it (the report's §2, to verify against current text)

- **Routing Step 1** in both orchestrators (Tier-1 §7) and `routing.md`. "A deeper path that changes code the stated defect does not touch — recurrence prevention, centralizing, restructuring — is not a fuller fix … record the deeper one as `defer-to-new-Issue`." So even a reviewer that proposed a split would have it deferred out of the unit.
- **The engineer review.** Its severity scale makes behavior-preserving refactors "nits at any depth", and its Architecture & Design checks don't cover where new code lands.
- **`agents/engineer.md`** says nothing about placement.
- **`agents/pm.md`'s scope-creep rule.** "Work outside the directive" reads a split nobody asked for as scope creep.
- **`/quo-breakdown-epic`'s Subtask template.** Work is written as edits at `file:line` in existing files, and nothing asks whether a new module is warranted.
- **The Analyst** chooses file boundaries in its Recommended approach, but has no stated goal about them.

### The goal

New code goes in the file or module whose responsibility it is. When a change would push a new responsibility into a file that already carries many, it creates or splits a module instead, and that move is part of the fix, not later cleanup. A project's own size rules, where it has them (its engineering best-practices doc), are the concrete bar.

### Constraints

- **No numbers and no language specifics** (design rules 1 and 3). Line counts and thresholds belong to projects, which already set them in their own docs.
- **Only what the change adds.** A review flags a change that piles a new responsibility into an already large file, not every large file the change touches. Pre-existing size isn't the unit's work, so reviews must not fill with findings about existing code.
- **One home for the decision** "is a structural move part of the fix?". Today routing Step 1, the severity scale and the PM's scope-creep rule each decide it, so fix the class in one pass (routing, both bodies in step, `routing.md`, the review, `pm.md`, and `docs/sdd.md`'s current-state lines).
- **Restructure; don't append.** Reword the rules that defer or devalue restructuring rather than adding exceptions beside them. Watch the word count. The goal itself is a few sentences in the roles that act on it.
- **Out of scope:**
  - test placement (inline tests): include it only if the reader check shows a real gap, since about 50 saved test reviews do cite source files;
  - the doc lane (b.9ar covered it);
  - ticket bodies superseding by appending, which is the next batch;
  - a "make room first" Task in breakdown, or a close-out size view (live_edit's guards cover those for now).
- **Orchestrator process:** inventory-anchored hand edits, mirrors in step, the line budget, the cold review with REWRITE-BRIEF §5/§6 and CLAUDE.md's review criteria, and define-before-write.

## Process

One hand-edit batch:
1. **Checkpoint 1:** the design, with no edits. Report every carrier of the decision, the one home, each sentence's new wording or cut, and the expected word deltas. Any change to routing (a behavior change) is listed for the operator.
2. **The draft.**
3. **One cold review under the exit rule,** with role-plays drawn from live_edit's real growth: a fix that adds a responsibility to a 30k-line file; a reviewer proposing a split; a change to a large file that adds no new responsibility (no finding); and a project with no size rules.

Live_edit picks the change up at its next rebuild. The next real run is the validation: watch whether the Engineer creates modules, and whether the reviews flag misplaced code and stay quiet about pre-existing size.

