---
id: b.q3f
type: bee
title: Analyst must produce a blast-radius sweep and name implied policy decisions at the design gate
tags:
- process
- quo-fix-issue
- analyst
parent: null
reference_materials: null
created_at: '2026-09-02T20:22:55.277552'
status: open
schema_version: '0.1'
guid: q3fgxrryv8h9ibsij6hh39ye2cihkrbm
---

## Description

`/quo-fix-issue` Section 3 dispatches the Analyst once and gates on its Design Proposal (Problem / Root cause / Recommended approach / Why / Alternatives / Options the body did not consider). Two things the proposal does **not** require are what caused serial review-round churn on a real run:

1. **No blast-radius sweep.** The proposal names the approach but not *every site* an added/removed invariant touches (log lines, span attributes, metric labels, background-task names, exception messages, docstrings, deployment-manifest comments, customer docs, tests). Every one of those sites is grep-findable before implementation; instead they were discovered one per review round.
2. **No enumeration of implied policy decisions.** A change frequently forces a yes/no policy question the body never states ("is this value now a secret?", "does this validation apply on every surface or only the one the body names?"). On the reference run those were decided implicitly by a Doc Writer and a Code Reviewer mid-stream, each decision then obligating an unplanned sweep.

## Reference run (worked example)

event_consumer_service Issue b.239 (drop the hashed principal from durable-queue names), 2026-09-02. The Analyst correctly found the load-bearing refinement (the removed call was the service's only token-validation trigger). But the follow-on consequences arrived serially:

- Doc Writer r1 documented "reconnect tokens are secrets" → Code Review r1: secrecy missing from proto/REST contract text → Code Review r2 (blocker): token logged verbatim at INFO and in span attributes → Engineer r4 sweep found it also in metric labels, task names, `extra=` dicts, `__del__` warnings → Code Review r3 (blocker): one more task name + warning missed → Doc Writer r3: uvicorn access log still records the query string.
- Code Review r1: `QUEUE_ID_PATTERN` enforced only on create → Engineer r2 enforced on every API surface → Code Review r2: enforce structurally inside `DurableQueueConsumer` too.

Net: 5 Engineer rounds, 3 Test Writer rounds, 3 Doc Writer rounds, 3 code reviews, ~30 files, for a change whose design was approved at round 1. A single grep-backed sweep at the Analyst gate (`queue.name`, `queue_id`, `reconnect_token`, `extra=`, `add_current_span_attributes`, task `name=`) would have produced the full site list up front.

## Expected behavior

`agents/analyst.md` structured-output contract gains two required sections, and SKILL.md Section 3 surfaces both at the approval gate:

- **`### Blast radius`** — for each invariant the Recommended approach adds, removes, or weakens: the invariant in one line, then the enumerated sites (file:line) where it is observable or assumed, grouped by kind (source logic / logs / traces / metrics / error text / docstrings-comments / deployment manifests or charts / customer docs / internal docs / tests), each with the grep pattern used as evidence. "None found" is an acceptable entry only with the pattern that was tried.
- **`### Policy decisions this change implies`** — yes/no questions the body leaves open whose answer changes the sweep (e.g. "Is `<value>` a secret once `<change>` lands? If yes: redact from logs/spans/metrics/task names/error text; if no: document that it is not."). The Analyst recommends an answer for each; the orchestrator surfaces them in the Section 3 preamble so the user approves the design AND the policies in one gate.

The Engineer dispatch prompt embeds both sections alongside the Recommended approach, so implementation is one round. Reviewers check the diff against the Blast radius list (a site on the list not addressed is a finding; a site not on the list is a finding against the Analyst pass, not a new fix round).

## Suggested fix

1. `agents/analyst.md`: add the two sections to the return-shape contract with the grouping/evidence rules above; extend "Why this role exists" with the churn rationale.
2. `skills/quo-fix-issue/SKILL.md` Section 3: include both sections in the surfaced proposal (not stripped like `### Deferred refinements`); add the policy decisions to the verdict preamble; carry both into the Section 4 Engineer directive block and into the Section 5 reviewer dispatch prompts as the checklist.
3. Consider the same for `/quo-execute`'s design inputs where a Subtask removes or weakens an invariant.

## Related

- Sibling Issue: strict lane sequencing (Engineer → code review until clean → Test Writer + Doc Writer once) — same reference run.
- Sibling Issue: routing table sends every multi-path finding to a user gate.
- Sibling Issue IDs: b.pdq (lane sequencing), b.nn8 (routing table default). Reference run: event_consumer_service b.239, 2026-09-02.
## Amendment (2026-09-02, after the reference run completed)

**Scope-split recommendation is part of the Analyst's job.** When the Blast radius sweep surfaces a concern that is distinct from the Issue's stated defect (on the reference run: "the reconnect token becomes a bare bearer capability once the principal hash is gone" was distinct from "durable-queue names must not embed identity"), the Analyst MUST recommend, in the proposal, whether to (a) fold it into this Issue or (b) file it as its own Issue and only *document* the property here. The orchestrator surfaces that recommendation at the Section 3 gate. On the reference run the reconnect-token concern drove ~4 of the 6 Engineer rounds and every second-round review finding; splitting it at the gate would roughly have halved the run and kept the naming Issue's diff reviewable.

**The sweep must cross into shared libraries the service depends on** (first-party dependencies the team owns and can change; the host repo's CLAUDE.md typically names them). The last blocker on the reference run — the raw token recorded on the `http.url` span attribute — lived in `../notification_common/rest/middleware/tracing_middleware.py`, not in the service.
## Amendment 2 (2026-09-03) — policy decisions must be grounded in the full request pipeline

On the reference run the team documented a value as "a secret / a bearer capability: anyone who presents it attaches" across 13 surfaces. The user corrected it: every request still passed an authentication step and a per-principal permissions filter, so the value was an *identifier* usable only by an already-authenticated principal, subject to its own permissions. The claim had been derived from the one mechanism the change removed, and every reviewer verified the claim's *consistency* across surfaces rather than its *truth*. Add to the `### Policy decisions this change implies` contract: for any decision of the form "is X a secret / what does holding X grant?", the Analyst MUST enumerate the gates a request passes (authn, coarse authz, per-principal filters, per-principal caches) with file:line evidence and state what remains true after them; the Recommended approach must use that precise phrasing (e.g. "any authenticated principal that obtains X can …, subject to its own permissions") rather than "secret"/"capability". Reviewers check the claim against the enumerated gates, not against the other surfaces.

