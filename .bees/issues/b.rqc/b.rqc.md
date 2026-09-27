---
id: b.rqc
type: bee
title: 'Mirrored fix-issue/execute batch: premise-check label, re-read the skill after a compaction, resume bound 675,000, two text fixes'
down_dependencies:
- b.d7t
parent: null
reference_materials: null
created_at: '2026-09-27T14:04:44.627938'
status: open
schema_version: '0.1'
guid: rqcd6hjknfppeheiywqb8ckmzaanq48n
---

## Description

A small batch of fixes to the text `/quo-fix-issue` and `/quo-execute` share (Tier 1 mirrored, so each edit lands in both bodies), found during b.87t's rebuild and its b.v9c validation run. It runs next, before the delegated-gate work.

## Items

1. **The premise-check label says whose premise (priority).** `agents/analyst.md` `## Premise-check dispatch` asks for `Premise check: premise-holds` or `premise-false` without saying whose premise, and both bodies' §7 read `premise-false` as "the finding's premise is false: ignore the finding". In the b.v9c run the Analyst returned `premise-false` twice meaning "the design's premise is false: the finding is right". The orchestrator routed correctly only by reading the reason line; read literally, it would have discarded the correct finding behind the Epic's largest design fix. Three questions: 2 of 2 premise checks in that run; silent; recovered by luck of phrasing. A gap between two agents: define the label once, in the role file and the mirrored §7 text, so both sides read it the same way.
2. **Re-read the skill after a compaction.** Only about the first 150 lines of an orchestrator body are re-injected after a compaction; §3 re-reads the manifest, bees, git, and two references, but not the body, so §6's gates and §7's routing table are unseen afterwards. Add this skill's `SKILL.md` to §3's existing re-read list (a kind-2 recovery goal; about 16k tokens per compaction).
3. **Resume bound 600,000 → 675,000** (operator decision 2026-09-27). Evidence from seven ledgers (332 rows): the largest resume increment was 214,527 (typical under 190k; 166k in the b.v9c run); a Test Writer resumed past the bound to 857,913 without failing, and an Engineer's transcript shrank 755k → 692k (subagents compact themselves). The bound fired in b.v9c at 633,530. 675,000 leaves 325k of headroom. Edit both bodies' §5 and the rationale reference.
4. **Phase A's clean string on a record-only diff.** `/quo-engineer-review` answers "No code files to review" on a diff with no code (b.v9c Task 1), not `No code issues found.`; say that either closes Phase A.
5. **Phase C's redundant sentence.** "its dispatch prompt states that it invokes neither review skill" is now redundant: `agents/pm.md` has no `Skill` tool. Delete it.
6. **The three review skills' trailer** still says "carry the ignored items into the final/Bee-level summary"; there is no Bee-level summary any more.

## Process

Hand edits per CLAUDE.md `## Working on the orchestrator skills`, one cold review, the exit rule. Items 1, 2, 4, and 5 are mirrored edits (both bodies byte-identical where Tier 1). No dedicated validation run: the next `/quo-fix-issue` or `/quo-execute` run is the check, and a premise check in it confirms item 1.
