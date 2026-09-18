# Rationale reference — why the orchestrator rules are shaped the way they are

This file is read on demand by `/quo-execute` and `/quo-fix-issue`. It carries every "why" and failure narrative the skill bodies used to interleave with their rules, grouped by mechanism. Nothing here is a rule; when this file and a skill body disagree about what to do, the body governs. Routing, compromise-tracker, and context-guard rationale live in their own reference files beside this one.

## Preconditions and contract keys

- Commands and doc paths come from the target repo's CLAUDE.md `## Build Commands` and `## Documentation Locations` so the skill works on any stack; auto-detection is unsafe on polyglot repos, monorepos, and custom build systems, where running the wrong command masks real failures.
- The subagent check rides on the first dispatch because that is where Claude Code's session-load semantics actually fail; a gate at the natural failure point cannot be bypassed by token pressure or model creativity.
- `general-purpose` is never a substitute for a missing role; an improvised role runs an unreviewed workflow.

## Session-effort gate

- The gate fires first so its `Let me change it first` exit never forces the user to re-answer a pick already made.
- An unset or unrecognised `CLAUDE_EFFORT` skips the check silently because a spurious prompt on every run is worse than a missed advisory.
- The comparison is against the floor, never for equality: an operator running hotter costs wall-clock, not quality, and interrupting them is gate-fatigue noise.
- No gate is opened before the comparison; an open gate left behind on the common path would re-fire as a phantom prompt later.
- Subagent effort is pinned per role file and overrides the session setting; the check concerns only the orchestrator's seat and the role-file-less post-completion reviewer.

## Isolation strategy

- The run produces one commit per unit, so landing them on the wrong branch is hard to undo; the prompt exists to prevent many commits on `main` without confirmation.
- Option 1 creates a local branch only, so the user can review, squash-merge, or discard later.
- In `/quo-fix-issue`, isolating before URL resolution lets the user opt into a fresh branch that scopes the file-from-URL commits too.

## Run-state manifest

- A random suffix would make the manifest unfindable exactly when it is needed most, because its reader is the orchestrator after a compaction dropped the path from the conversation.
- The manifest holds only values with no other durable home; duplicating ticket bodies, directives, or findings would grow it into a shadow ticket store that drifts.
- `/quo-fix-issue` keys on the repository directory basename because batch membership and order are user-supplied and recorded only inside the manifest; an Issue ID is not recomputable by a reader that lost the conversation.
- `/quo-execute` keys on the Bee ID because it is the run's argument and the parent of every Epic, so any in-flight Plans ticket recovers it in one query.
- The skill-name segment keeps sibling skills from truncating each other's manifests; `/quo-breakdown-epic` keys on the same Bee ID.
- Accepted collisions: two concurrent runs in the same working directory or against the same Bee already collide over statuses and commits; two checkouts sharing a basename land on one file, and a `**Unit scope:**` mismatch is the tell.
- The run mode in `/quo-execute` is a user choice with no re-derivation path; if lost, the run cannot know whether to auto-continue, which is why it lives in the manifest.
- Lanes, obligations, rounds, and the open gate live in the manifest because the manifest is the one carrier that works in every environment; a carrier the harness treats as optional cannot hold load-bearing state.

## Reconciliation loop and dispatch

- Implementers are resumed for their fix rounds because the harness resumes a completed background Agent by name with its transcript intact, and the author's design context is what a fix needs; the first two cost ledgers put a fresh implementer round at roughly 65k–190k tokens of re-reading before any edit, and a fresh fixer fixes the code's surface rather than its design. Reviewers stay fresh because fresh eyes are what a review is for. The name is `<role>-<scope>`, scope characters outside letters, digits, hyphen, and underscore replaced by a hyphen (the Agent tool rejects the period every bees ID carries), so a resume is re-derivable from a `## Lanes` row after a compaction with no new manifest field; the send itself is the liveness test — `ListAgents` lists only running Agents, so it reports every completed implementer as absent (the first validation run found this) — and a session restart discards the Agents, so the send then fails and the dispatch goes fresh. A send refused because two Agents share the name, after a fresh dispatch superseded the first under it, is resent with the later spawn's ref and is not a failure; the same run needed the ref for every send after its one fresh re-dispatch. The 600,000-token resume bound exists because a resumed Agent's transcript grows every round and the harness compacts it near its window, which would lose the context the resume was keeping; the ledger's per-dispatch token figure measures transcript growth, so its sum is that transcript's size.
- Hub-and-spoke is a structural property of ephemeral background Agents, not a rule to enforce; no inter-Agent channel exists, so workers cannot couple even if a prompt invited it.
- Subagents cannot spawn subagents, so orchestration is flat and the orchestrator's context grows monotonically within a session; nothing in the skill reclaims it, the harness compacts, and the boundary checkpoint is what makes that compaction lossless.
- Paraphrasing a ticket body silently corrupts identifier names the worker uses literally, so the body travels verbatim.
- The relay headings are one string at every hop because the review verifies the diff against the list under exactly that label; a renamed heading silently drops the check.
- `## Engineer's completeness evidence` cannot be relayed on every path: a compaction after the Engineer returned destroys the list, and the resulting missing-list finding is a compaction artifact, not an Engineer defect.
- Stating that the assignment was sweep-shaped, separately from the list, is what keeps the missing-list check reachable; an unnamed sweep silently loses it.
- Writer prompts never claim the tree is frozen because the orchestrator cannot stop the user, a second session, or a background process from editing it; the writer-side fingerprint is the recovery, not the prompt wording.
- The Test Writer's fingerprint set comes from the Engineer's `## Files changed` rather than the working tree because the tree fallback sweeps in other actors' edits, each of which the writer will stop on.

## Roles and lane boundaries

- Framing prose never loosens a role file's lane; the only handoff is worker to orchestrator, so "coordinate with the other role's diff" cannot make a softening safe.
- A temptation to carve a role exception signals a need for orchestrator-level coordination, such as a follow-up dispatch or a re-scoped unit, not a softening clause.
- The orchestrator performs mechanical steps that produce a tool artifact directly and dispatches every judgment over file contents, because a reviewer that watched the work is the wrong reader for it.

## Movement reports and aborted lanes

- Without a receiver for a movement report the orchestrator would mark the writer complete and dispatch a reviewer over tests or docs the writer never finished.
- The writer's own lane closes because its Agent has exited; the owed redelivery becomes an obligation in the manifest because an obligation only in conversation does not survive compaction.
- Re-dispatching a writer into a still-moving diff reproduces the abort, so the mover's lane and its review round close first.
- The two writers detect different things, and the receiver should not overstate either: the Test Writer stops on any changed hash in its `## Source paths to fingerprint` set, a moved `HEAD`, or a path that no longer hashes.
- The Doc Writer's trigger is narrower: it stops when the material it is documenting appears to have moved, such as a file it read no longer matching its prose.
- Do not read a Doc Writer's silence as a clean-tree attestation over every source path.
- A Test Writer's discrimination experiment is the mover most easily misread as an external edit; its `## Perturbations` list is what attributes it.
- The unexplained-movement gate exists because a blind re-dispatch loop into a tree something else is editing is the failure it prevents.
- `Wait` re-fires only on the operator's reply because a sibling lane's completion notification is a normal tick and must not re-fire the gate.

## Analyst gate and design directive (`/quo-fix-issue` on every Issue; `/quo-execute` on escalation)

- Body-quality classification is a fragile heuristic: a body citing code paths may be a typo fix, and a one-sentence body may sit behind a rich upstream URL. Only the Analyst's codebase research is a reliable classification, so the Analyst is always dispatched.
- The verdict preamble exists so a user meets a divergent recommendation already knowing it diverges, rather than discovering it by careful reading.
- Naming the count of policy decisions tells the user that Approve ratifies the Analyst's recommended answers along with the design.
- The `### Deferred refinements` block is stripped from the surfaced prose because it is orchestrator plumbing for the deferral-hygiene gate, not design content.
- A Revise re-dispatch quotes the prior proposal in full, including its `### Deferred refinements`, so the revising Analyst carries each deferral forward or drops it explicitly.
- `defer-*` obligations from an earlier Approve survive a later re-fire because that approval still stands; clearing them would destroy every banked refinement.
- The Design Proposal has no durable carrier in `/quo-fix-issue` by design, and an execute revision has none until its Approve appends it to the Subtask body; re-deriving through the Analyst is the only honest recovery, because a proposal reconstructed from a summary is a guess.
- An Engineer's `## Design question` means the proposal's `### Blast radius` missed a mechanism; it is a revision of the proposal, not a new decision point.

## Close-out and commit

- `git add -A` is forbidden because other agents or processes may have in-flight changes in the working tree.
- The commit subject's parenthesised ticket-ID token is a contract, not style: in `/quo-fix-issue`, the boundary checkpoint and the GitHub close block both `--grep` for it.
- The close-out status flip is idempotent because a worker occasionally flips the status itself.
- The Issue type has only `open` and `done`, so there is no in-flight status to set; the manifest's `## Lanes` carries the in-flight signal.
- `Format` is the only rung the orchestrator runs before commit on its own initiative; the implementer lanes already validated, and re-running the suite wastes minutes per unit. The one exception is a target project whose CLAUDE.md requires a test run before a commit — then the orchestrator runs `Full test` too.

## Boundary checkpoint

- The unit boundary is where the run is most re-derivable: the unit is `done` and committed, or deliberately left `open` with no commit, and either pair is the durable record.
- In `/quo-fix-issue`, the ranged `--grep` over `<pre-session-sha>..HEAD` is load-bearing in both directions: a bare `git log -1` may inspect a later `Encode deferral:` commit, and an unscoped `--grep` may match a same-token commit from an earlier run.
- An absent tracker is not by itself a gap: a unit whose only ungated route hit Trigger C's lone-`trivial-tweak` carve-out is correctly entry-less.
- The checkpoint does not clear, compact, or reclaim context and must never be narrated as if it did.
- The per-unit consumption figure some earlier text quoted was an unverified working estimate; nothing measures it, and no rule depends on it.

## Deferral hygiene

- A deferral important enough to surface during the run is important enough to encode in a durable carrier before the run ends.
- Vague framings such as "defer to later" are forbidden because an item without a destination cannot be reconciled into a carrier.
- Step 0 is a safety net for orchestrators that missed the upstream record-creating sites; those sites remain the load-bearing source.
- The active set is scoped per unit because accumulating deferrals across a batch would surprise the user with a long list at the end and defeat per-unit close-out.
- Encode writes land after the per-unit commit, so a follow-up commit is needed or the tree is dirty at yield; the helper stages only in-repo hive paths and explicit `--doc-path` arguments, so an aborted unit's uncommitted fix is never swept in.
- The Encode heading's timestamp suffix lets several Encodes to one ticket body across runs sit side by side with distinguishable headings.
- `<N>` in the Encode commit subject counts deferral items, not tickets, because several items can land in one body and one item in several.
- Per-item routing at the deferral gate is the one place where the auto-appended free-text slot is the primary path, because the finite choices apply per item.

## Summaries

- `**Second-order effects**` is unconditional because a section that appears only when there is something to say degrades into one nobody can rely on being asked for.
- `**Accepted compromises**` is omitted when empty because it renders the tracker, and an empty tracker is the common clean case.
- All tracker entries are rendered in full, however many, because the tracker exists precisely to preserve that signal.

## Post-completion review

- The diff scope is the working tree against the pre-run commit plus untracked files because review-round edits may sit uncommitted; a commit-to-commit range alone misses them.
- The reviewer cannot see the run-start tree, so a change no ticket asked for is reported as likely pre-existing or an unticketed in-run edit, as an inference.
- Post-completion lanes reuse every per-unit rule with the finding index as the unit, because a follow-up answering one finding of a whole-run sweep belongs to no ticket.
- A post-completion abort closes out through the lane table alone, never through the aborted-unit close-out, because every unit is already `done` and committed.

## GitHub close block (`/quo-fix-issue`)

- The block is a recommendation the skill never runs, so no `gh` authentication assumption is baked into the workflow.
- Only the `github-issue` resolver is covered: Linear needs its own CLI or API, and the generic `url` resolver has no close concept.
- The per-Issue `--grep` on the `(<issue-id>)` token filters out post-completion commits that would otherwise mis-pair SHAs positionally.
