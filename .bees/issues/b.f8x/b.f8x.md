---
id: b.f8x
type: bee
title: Unify /quo-execute Section 5 reviewer-feedback annotation contract with /quo-fix-issue Section 5
status: open
created_at: '2026-05-28T19:41:55.111313'
schema_version: '0.1'
reference_materials: null
guid: f8xmhscpuiuogb3mk11q62i9vs2x94vt
---

## Description

Commit cb30bc5 (post-completion fixes for the b.9q3 / b.dgq / b.wii session) tightened `/quo-fix-issue` Section 5's ignored-reviewer-feedback record-creating step into an explicit MUST contract: the Director MUST annotate the `defer-*` task's `metadata.activity` with one of the three destination labels from `agents/pm.md`'s destination vocabulary (`addressed-now-in-this-Task` / `defer-to-existing-ticket-body: <ticket-id>` / `defer-to-new-Issue`). The annotation is required, not optional; vague framings like "defer to later" are forbidden by the same anti-pattern rule that applies to PM annotations.

The matching site in `/quo-execute` Section 5 was NOT tightened. It still carries the softer original b.dgq prose: when the reviewer's framing suggests a destination, record it; otherwise, **mark it as pending-destination so Section 6.5's gate will surface the bullet for the user to map**. Two execution-skill peers diverged on the same load-bearing contract surface.

## Current behavior

- `skills/quo-execute/SKILL.md:447` — soft form: "Where the reviewer's framing suggests a destination ... record the destination annotation alongside the description in `metadata.activity`; otherwise, mark it as pending-destination so Section 6.5's gate will surface the bullet for the user to map."
- `skills/quo-fix-issue/SKILL.md:441` — strict MUST form: "the Director MUST annotate the `metadata.activity` with one of the three destination labels ... when creating the `defer-*` task. The destination is the Director's judgement call captured at ignore time, but the annotation itself is required, not optional ... Vague framings without a named destination (e.g., 'defer to later') are forbidden ..."

Two execution-skill peers with divergent reviewer-feedback contracts after the post-completion fix landed.

## Expected behavior

`/quo-execute` Section 5 carries the same strict MUST contract as `/quo-fix-issue` Section 5. Both skills require the Director to annotate the `defer-*` task's `metadata.activity` with one of the three destination labels at ignore-time. The `pending-destination` deferred-resolution shape is removed; resolution happens at decision-time, not at gate-surface-time.

The deferral-hygiene gate (`/quo-execute` Section 6.5 / `/quo-fix-issue` Section 7.5) then routes uniformly through the Fix / File / Encode branches for both skills.

## Impact

- **Self-consistency.** Two peer execution skills should not diverge on a load-bearing contract that the PM Agent and Doc Writer Agent already converge on.
- **Reduced runtime ambiguity.** `pending-destination` leaves the gate to ask the user to map items at surface time — which is the deferred-resolution shape b.dgq's whole hardening cycle was meant to close. Strict annotation at ignore-time keeps the carrier-encoding contract intact.
- **Simpler gate logic.** Removing the `pending-destination` branch from `/quo-execute`'s Section 6.5 enumeration means the gate's three Fix / File / Encode options always operate on a fully-annotated active set.

## Suggested fix

Update `skills/quo-execute/SKILL.md` Section 5's ignored-reviewer-feedback record-creating step (currently ~line 447) to match `skills/quo-fix-issue/SKILL.md` Section 5's strict MUST form (currently ~line 441), with the only differences being:

- "addressed-now-in-this-Task" reads literally (not as "addressed-now-in-this-Issue") in `/quo-execute` since the unit IS a Task there.
- Section 6.5 reference (not 7.5).
- Section 4 → Section 3 for the TaskList naming convention pointer.

Also remove the `pending-destination` enumeration from `/quo-execute` Section 6.5's Step 0 retroactive-sweep — every item the sweep encounters will already be fully annotated under the new contract.

## Background and rationale

The asymmetry was created in commit cb30bc5 when the orchestrator addressed Code Review finding #6 only against `/quo-fix-issue` Section 5 without unifying the matching `/quo-execute` Section 5 site. Caught by external reviewer in a fresh-eyes pass. Filed as a follow-up rather than fixed inline because (a) the asymmetry is small and not blocking, and (b) the unification has a small downstream consequence (removing the `pending-destination` enumeration from Section 6.5 Step 0) that benefits from a discrete commit with a clear scope.

## Decisions and rejected alternatives

- **Move both skills toward the softer `/quo-execute` Section 5 shape** (down-tighten `/quo-fix-issue`). Rejected — the b.dgq design directive's Layer 3 PM-contract change requires destinations to be named, and the strict shape matches that contract. The soft shape is the regression.
- **Leave the asymmetry in place and document it as intentional.** Rejected — no design rationale supports the asymmetry; it's an artifact of partial post-completion remediation.

