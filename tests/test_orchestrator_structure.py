"""Structural invariants of the two orchestrator bodies and their reference files.

The orchestrator skills (`/quo-execute`, `/quo-fix-issue`) were rewritten clean-room
against an inventory of their rules. This module pins the *structure* that rewrite
committed to, never a prose sentence:

  (a) the mirror map — sections both bodies must carry byte-identical (Tier 1) or
      identical modulo the unit noun / skill name (Tier 2), from a checked-in pair list;
  (b) the per-body line budget and the first-150-lines ordering constraint;
  (c) one presence assertion per kept inventory rule, keyed on a heading or label
      anchor — the string a downstream consumer would key on, not a sentence;
  (d) every gate's choice labels, verbatim;
  (e) every contract-surface heading, present in its emitter and its consumer files.

Plus the design decisions the rewrite made structural: no rule reads TaskList state,
gates are manifest-fronted, the destination label is a single literal, and the two
bodies use one `Section N` vocabulary. When a body and this module disagree, read the
brief that governs the bodies before editing either; a test here exists to make a
structural regression fail loudly, not to freeze wording.
"""

import re

import pytest

from conftest import (
    AGENT_ANALYST,
    AGENT_CODE_REVIEWER,
    AGENT_DOC_REVIEWER,
    AGENT_DOC_WRITER,
    AGENT_ENGINEER,
    AGENT_PM,
    AGENT_TEST_REVIEWER,
    AGENT_TEST_WRITER,
    QUO_BREAKDOWN_EPIC,
    QUO_DOC_WRITER_REVIEW,
    QUO_ENGINEER_REVIEW,
    QUO_EXECUTE,
    QUO_FILE_ISSUE,
    QUO_FIX_ISSUE,
    QUO_TEST_WRITER_REVIEW,
    REF_COMPROMISE_TRACKER,
    REF_CONTEXT_GUARD,
    REF_GITHUB_CLOSE,
    REF_POST_COMPLETION_PROMPT,
    REF_RATIONALE,
    REF_ROUTING,
    REF_URL_RESOLUTION,
    REPO_ROOT,
    ROUTING_SECTION_HEADING,
    heading_section,
    read,
    shipped_artifacts,
)

FIX = read(QUO_FIX_ISSUE)
EXE = read(QUO_EXECUTE)
BODIES = {"quo-fix-issue": FIX, "quo-execute": EXE}

SHARED_REFS = [REF_ROUTING, REF_POST_COMPLETION_PROMPT, REF_COMPROMISE_TRACKER, REF_CONTEXT_GUARD, REF_RATIONALE]
FIX_ONLY_REFS = [REF_URL_RESOLUTION, REF_GITHUB_CLOSE]

LINE_HARD_CAP = 550
FIRST_LINES = 150


# --- helpers ----------------------------------------------------------------


def paragraphs(section_text):
    """Blank-line-separated blocks of a section, excluding its heading line."""
    body = section_text.split("\n", 1)[1] if "\n" in section_text else ""
    return [p for p in re.split(r"\n\s*\n", body) if p.strip()]


def first_paragraph(section_text):
    return paragraphs(section_text)[0]


def bullet_lines(section_text, prefix):
    return [line for line in section_text.splitlines() if line.startswith(prefix)]


def numbered_steps(section_text):
    """Top-level `N. ` lines of a section, in order."""
    return [line for line in section_text.splitlines() if re.match(r"^\d+\. ", line)]


def normalize_skill_name(text):
    """Tier 2 normalization: fold the fix-issue skill name and its sibling helper path onto execute's."""
    text = text.replace("<this skill's base directory>/../quo-execute/scripts/hive_commit.py",
                        "<this skill's base directory>/scripts/hive_commit.py")
    text = text.replace("<this skill's base directory>\\..\\quo-execute\\scripts\\hive_commit.py",
                        "<this skill's base directory>\\scripts\\hive_commit.py")
    return text.replace("quo-fix-issue", "quo-execute")


def normalize_unit_noun(text):
    """Tier 2 normalization: fold execute's unit placeholders onto fix-issue's."""
    return text.replace("<epic-id>", "<issue-id>").replace("`Bee`", "`fix`")


def assert_present(anchors, text, where):
    missing = [a for a in anchors if a not in text]
    assert not missing, f"{where} is missing anchor(s): {missing}"


# --- (a) mirror map ------------------------------------------------------------

TIER1_WHOLE_SECTIONS = [
    "## 7. Routing discipline",
    "## 10. Compromise tracker",
]


@pytest.mark.parametrize("heading", TIER1_WHOLE_SECTIONS)
def test_tier1_section_is_byte_identical(heading):
    assert heading_section(FIX, heading) == heading_section(EXE, heading), (
        f"{heading} diverges between the two orchestrators; it is Tier 1 in the mirror map"
    )


TIER1_FIRST_PARAGRAPHS = [
    "## 3. After a compaction",
    "## 4. The loop",
    "## 5. Dispatch shape",
    "## 6. Gates",
]


@pytest.mark.parametrize("heading", TIER1_FIRST_PARAGRAPHS)
def test_tier1_lead_paragraph_is_byte_identical(heading):
    assert first_paragraph(heading_section(FIX, heading)) == first_paragraph(heading_section(EXE, heading))


def test_tier1_session_effort_gate_is_byte_identical():
    fix = bullet_lines(heading_section(FIX, "## 6. Gates"), "- **Session effort.**")
    exe = bullet_lines(heading_section(EXE, "## 6. Gates"), "- **Session effort.**")
    assert fix and fix == exe


def test_tier1_tick_skeleton_is_byte_identical():
    fix_tick = heading_section(FIX, "### Tick")
    exe_tick = heading_section(EXE, "### Tick")
    assert first_paragraph(fix_tick) == first_paragraph(exe_tick)
    fix_yield = [line for line in fix_tick.splitlines() if line.startswith("3. **Yield.**")]
    exe_yield = [line for line in exe_tick.splitlines() if line.startswith("3. **Yield.**")]
    assert fix_yield and fix_yield == exe_yield


ROUNDS_HEADER_ROW = "| scope | review | classification | decision | text fixes applied without re-review |"


def test_tier1_rounds_template_and_bullet_are_byte_identical():
    for name, text in BODIES.items():
        assert ROUNDS_HEADER_ROW in text, f"{name} lacks the ## Rounds header row"
    fix = bullet_lines(heading_section(FIX, "## 2. Run-state manifest"), "- `## Rounds`")
    exe = bullet_lines(heading_section(EXE, "## 2. Run-state manifest"), "- `## Rounds`")
    assert fix and fix == exe


def test_tier1_movement_rung_closing_rules_are_byte_identical():
    tail = (
        'The re-dispatch is the next round at the same scope and carries the "how far I got" detail. '
        "A normal deliverable from the re-dispatched lane closes the obligation; "
        "a second abort refreshes the same obligation's detail, never opens another."
    )
    assert tail in FIX and tail in EXE


def test_tier1_checkpoint_disclaims_context_reclamation_identically():
    sentence = ("it does not clear, compact, or reclaim context, and must never be narrated as if it did.")
    assert sentence in heading_section(FIX, "#### Issue-boundary state-externalization checkpoint")
    assert sentence in heading_section(EXE, "#### Epic-boundary state-externalization checkpoint")


MANIFEST_LEAD_STATEMENTS = [
    "The manifest is a small markdown file holding the handful of run-scoped values that live **nowhere else on disk** — everything the orchestrator would otherwise have to remember.",
    "It is what makes harness compaction survivable: after a compaction the orchestrator re-reads this file instead of trusting a summary.",
    "**Path and filename.** The manifest is written under the project's standard scratch-file convention, in `<tempdir>/.quorum/` (`/tmp/.quorum/` on POSIX, `%TEMP%\\.quorum` on Windows).",
    "**The filename is deterministic — do NOT add a random suffix or timestamp.**",
    "**Semantics: truncate at run start, rewrite at each boundary.** The manifest is a **live snapshot, not an accumulating log**.",
    "Every skill in this set carries its own name in the filename's leading position and differs only in the discriminator it appends",
]


@pytest.mark.parametrize("skill", [QUO_FIX_ISSUE, QUO_EXECUTE, QUO_BREAKDOWN_EPIC])
def test_manifest_lead_statements_are_mirrored_across_all_three_orchestrators(skill):
    section = heading_section(read(skill), "#### Write the run-state manifest")
    assert_present(MANIFEST_LEAD_STATEMENTS, section, skill)


def test_tier2_deferral_hygiene_steps_match_modulo_skill_name():
    fix = heading_section(FIX, "## 9. Deferral hygiene")
    exe = heading_section(EXE, "## 9. Deferral hygiene")
    fix_bullets = [b for b in bullet_lines(fix, "- ") if not b.startswith("- **Step 0")]
    exe_bullets = [b for b in bullet_lines(exe, "- ") if not b.startswith("- **Step 0")]
    assert fix_bullets, "no hygiene bullets found"
    assert [normalize_skill_name(b) for b in fix_bullets] == exe_bullets


def test_tier2_post_completion_steps_match_modulo_unit_noun():
    fix = numbered_steps(heading_section(FIX, "## 11. Post-completion review"))
    exe = numbered_steps(heading_section(EXE, "## 11. Post-completion review"))
    assert len(fix) == len(exe) == 6
    assert fix[1:] == exe[1:]
    assert fix[0] == normalize_unit_noun(exe[0])


def test_tier2_context_guard_steps_match_modulo_unit_placeholder():
    fix = numbered_steps(heading_section(FIX, "#### Context-window boundary guard"))
    exe = numbered_steps(heading_section(EXE, "#### Epic-boundary context-window guard"))
    assert len(fix) == len(exe) == 4
    assert fix == [normalize_unit_noun(step) for step in exe]


def test_divergence_table_is_present_identically_in_both_bodies():
    rows = [
        "| Approved-design source for \"introduces a mechanism\" |",
        "| Gate (d) `Cancel` semantics |",
        "| Part (g) code-review rung |",
        "| Close-out target on `Cancel` / abort |",
    ]
    for body in BODIES.values():
        assert_present(rows, heading_section(body, ROUTING_SECTION_HEADING), "routing section")


# --- (b) line budget and ordering ---------------------------------------------


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_body_is_within_the_hard_line_cap(name, text):
    count = len(text.splitlines())
    assert count <= LINE_HARD_CAP, f"{name} is {count} lines; hard cap is {LINE_HARD_CAP}"


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_preconditions_manifest_compaction_and_loop_sit_in_the_first_lines(name, text):
    lines = text.splitlines()
    required = ["## 1. Preconditions", "## 2. Run-state manifest", "## 3. After a compaction", "## 4. The loop", "## 5. Dispatch shape"]
    positions = {}
    for h in required:
        idx = [i for i, line in enumerate(lines, start=1) if line.strip() == h]
        assert len(idx) == 1, f"{name}: expected exactly one {h!r}"
        positions[h] = idx[0]
    assert all(pos <= FIRST_LINES for pos in positions.values()), f"{name}: {positions}"
    assert list(positions.values()) == sorted(positions.values()), f"{name}: sections out of order"


def test_body_sections_are_numbered_one_through_thirteen():
    for name, text in BODIES.items():
        numbers = [int(m.group(1)) for m in re.finditer(r"^## (\d+)\. ", text, flags=re.M)]
        assert numbers == list(range(1, 14)), f"{name}: section numbers are {numbers}"


# --- (c) presence per kept rule, keyed on anchors ------------------------------

SHARED_ANCHORS = [
    "Run /quo-setup first.",
    "Run /quo-setup first. — required subagent types <missing-list> are not registered in this session; verify the install per README.md '## Install' and restart Claude Code or run /agents to hot-reload.",
    "Run /quo-setup first. — Specs hive is not colonized for this repo. Re-run /quo-setup to add the Specs hive without disturbing existing hives (Plans, Issues).",
    "`## Documentation Locations`",
    "`## Build Commands`",
    "#### Write the run-state manifest",
    "## Lanes",
    "## Obligations",
    "## Rounds",
    "## Open gate",
    "**Compromise tracker:**",
    "**Context guard:**",
    "**Progress:**",
    "**Next unit:**",
    "**Unit scope:**",
    "**Isolation strategy:**",
    "### Run start",
    "### Tick",
    "### Phase ladder",
    "**Read state.**",
    "**Reconcile.**",
    "**Yield.**",
    "`/loop`",
    "`ScheduleWakeup`",
    "`CronCreate`",
    "`Agent(subagent_type=<role>, run_in_background=true, prompt=…)`",
    "`name=<role>-<scope>`",
    "`SendMessage`",
    "`ListAgents`",
    "`**Ledger:**`",
    "`**Cost:**`",
    "**Late-chain enumeration.**",
    "`close — enumerated`",
    "`enumerated`",
    "`## Site enumeration requested`",
    "`## Confirming pass`",
    "`Confirming pass: <n> fixes checked`",
    "`## Source paths to fingerprint`",
    "`## Engineer's completeness evidence`",
    "`## Files changed`",
    "`git diff --name-only HEAD`",
    "`\"the source tree is frozen\"`",
    "`<scoped-marker-resolver-path>`",
    "`<compromise-tracker-path>`",
    "**Movement rung.**",
    "**Killed lane.**",
    "`## Perturbations`",
    "**Engineer-dispatch precondition.**",
    "**Scenario A — Already in a worktree**",
    "**Scenario B — On an existing branch in the main repo**",
    "**Severity bounds the loop.**",
    "**(a) Pick the path, then route on it.**",
    "**Step 1 — pick.**",
    "**Step 2 — route on the path chosen in Step 1.**",
    "**(c) Scope-bounding gate.**",
    "**(d) Routing-decision gate.**",
    "**(g) Re-dispatch ordering when a fix path changes source.**",
    "`[introduces-mechanism]`",
    "`[preferred]`",
    "`N text fixes applied without re-review`",
    "`count unavailable post-compaction`",
    "`N rounds (earned/late/text/unavailable = a/b/c/d)`",
    "(Engineer → Code Reviewer, Test Writer → Test Reviewer, Doc Writer → Doc Reviewer) at scope `postcomp-<n>`",
    "one slot per reviewer lane, in the slot format of Section 8",
    "`Kinds changed:`",
    "**Hold set by kind.**",
    "**Apply, never defer, text findings.**",
    "**Premise check.**",
    "**Earned-chain escalation.**",
    "**Exit decision per round.**",
    "`Premise check: premise-holds`",
    "`Premise check: premise-false`",
    "`another round`",
    "`to the Analyst`",
    "`close — clean`",
    "`close — text`",
    "`earned`",
    "`late`",
    "`clean`",
    "`unavailable post-compaction`",
    "**Your next tool use MUST address these findings now.**",
    "**Your next tool use MUST advance the workflow.**",
    "`addressed-now`",
    "`defer-to-existing-ticket-body: <ticket-id>`",
    "`defer-to-new-Issue`",
    "**Do NOT blindly `git add -A`**",
    "**NEVER push to remote — committing only.**",
    "resolve-hive-paths",
    "**Second-order effects**",
    "`None identified.`",
    "`No second-order effects identified.`",
    "**Accepted compromises**",
    "**Ignored Review Feedback**",
    "**Reviews**",
    "**Files Changed**",
    "`Deferral hygiene: no deferred items.`",
    "**Step 0 — Retroactive ledger reconciliation (safety net).**",
    "**Step 1 — Enumerate the active deferral ledger.**",
    "**Step 2 — Surface the active set and gate the user choice.**",
    "**Step 3 — Hard-stop on a non-empty active set.**",
    "`bees update-ticket --ids <ticket-id> --body-file <path>`",
    "bees-body-<defer-N>.md",
    "`skipped: nothing staged`",
    "#### Session-scoped compromise tracker",
    "#### Compromise-tracker append triggers",
    "## Compromise <n>",
    "**Finding (verbatim):**",
    "**Fix paths surfaced by reviewer:**",
    "**Decision:**",
    "**Rationale:**",
    "**Follow-up Issue:**",
    "**Trigger A — Defer to follow-up Issue at either gate.**",
    "**Trigger B — Accept the limitation at the scope-bounding gate.**",
    "**Trigger C — ungated route (the orchestrator's own path pick).**",
    "**Trigger D — post-completion override, covering BOTH override gates (SR-6.7 / SR-4.6).**",
    "`git ls-files --others --exclude-standard`",
    "`Agent(subagent_type=general-purpose, run_in_background=true, prompt=…)`",
    "`Post-completion review: no issues found`",
    "`Post-completion review found [N] issues. How would you like to handle them?`",
    "**SR-6.7 ungated-route recovery gate.**",
    "**SR-4.6 under-enumeration recovery gate.**",
    "stop-threshold",
    "read --session-id <trimmed-session-id>",
    "`no-reading`",
    "`stale`",
    "`missing`",
    "`<tempdir>/.quorum/context-guard-opt-out`",
    "`printenv CLAUDE_CODE_SESSION_ID`",
    "`Write-Output $env:CLAUDE_CODE_SESSION_ID`",
    "`printenv CLAUDE_EFFORT`",
    "`Write-Output $env:CLAUDE_EFFORT`",
    "`git status --porcelain`",
    "`Ctrl-C`",
    "`analyst`",
    "**Analyst.**",
    "`Agent(subagent_type=analyst, run_in_background=true, prompt=…)`",
    "**Design-question rung.**",
    "**Re-derivation shape.**",
    "`## Design question`",
    "`## Prior proposal and user feedback`",
    "`## Authoritative design directive (from the Analyst gate)`",
    "`## Design context (Analyst's Why / Alternatives considered / Options the body did not consider)`",
    "`## Blast radius`",
    "`No invariant added, removed, or weakened.`",
    "`None — the recommendation leaves no policy question open.`",
    "`### Deferred refinements`",
    "`Analyst verdict:`",
    "`recommend-different-approach`",
    "`escalate-to-user`",
    "`How should I proceed with this design proposal?`",
    "`Re-dispatch the Analyst with this finding`",
]


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_shared_rule_anchors_are_present(name, text):
    assert_present(SHARED_ANCHORS, text, name)


FIX_ANCHORS = [
    "`normalized_name` is `issues`",
    "`run-state-quo-fix-issue-<repo-dir-name>.md`",
    "`git rev-parse --show-toplevel`",
    "**Pre-session SHA:**",
    "`bees execute-freeform-query --query-yaml 'stages:\\n  - [type=bee, hive=issues, status=open]\\nreport: [title]'`",
    "**URL token**",
    "**ticket-ID token**",
    "`Cannot start Issue. It is blocked by: [list]`",
    "**Text class.**",
    "**Proposal:**",
    "proposal-<issue-id>-<short-suffix>.md",
    "**Phase A — source to clean.**",
    "**Phase B — writers once, in parallel.**",
    "**Phase C — remaining reviewers plus PM.**",
    "**PM is the exception to the conditional-spawn rules.**",
    "`No code issues found.`",
    "`\"no Engineer Agent will be dispatched for this Issue while you are running\"`",
    "`Fix issue: <title> (<issue-id>)`",
    "resolve-hive-paths --hive issues",
    "`git add <emitted-issues-path>/<issue-id>`",
    "## Issue [x] of [total] done: [issue-title]",
    "**Doc Sync**",
    "`no spec drift surface to review for this Issue`",
    "`## Doc divergence noted`",
    "#### Issue-boundary state-externalization checkpoint",
    "`git log --oneline -1 -F --grep='(<issue-id>)' <pre-session-sha>..HEAD`",
    "#### Context-window boundary guard",
    "`/quo-fix-issue all`",
    "`/quo-fix-issue <remaining-ids>`",
    "`Deferral hygiene (batch close): no deferred items.`",
    "`## Deferred from /quo-fix-issue run (<YYYY-MM-DD HH:MM>)`",
    "`Encode deferral: /quo-fix-issue — <N> deferral(s) encoded`",
    "--skill quo-fix-issue --count <N> [--doc-path <abs-path> ...]",
    "`git diff <pre-session-sha>`",
    "#### Aborted-Issue close-out",
    "`<issue-id>: aborted — no commit; Issue left open`",
    "**STOP the run here**",
    "`Upstream GitHub Issues to consider closing:`",
    "`gh issue close <n> --repo <owner>/<repo> -c \"Fixed in <sha>.\"`",
    "`github-issue`",
]


def test_fix_issue_rule_anchors_are_present():
    assert_present(FIX_ANCHORS, FIX, "quo-fix-issue")


EXE_ANCHORS = [
    "`normalized_name` is `plans`",
    "`run-state-quo-execute-<bee-id>.md`",
    "**Pre-Bee SHA:**",
    "**Multi-Epic run mode:**",
    "Mode 1 (Stop after each Epic)",
    "Mode 2 (Work through all Epics)",
    "`not captured (single Epic in scope)`",
    "`not captured (all Epics already done)`",
    "`pending Section 4 query`",
    "`bees execute-freeform-query --query-yaml 'stages:\\n  - [type=bee, hive=plans]\\nreport: [title, ticket_status]'`",
    "`bees execute-freeform-query --query-yaml 'stages:\\n  - [parent=<bee-id>, type=t1]\\nreport: [title, ticket_status, up_dependencies]'`",
    "`status!=drafted`",
    "**Per-Subtask fan-out.**",
    "**Per-Task PM.**",
    "**Epic boundary.**",
    "**Bee-level reviews.**",
    "`Agent(subagent_type=\"code-reviewer\", run_in_background=true)`",
    "`Agent(subagent_type=\"test-reviewer\", run_in_background=true)`",
    "`Agent(subagent_type=\"doc-reviewer\", run_in_background=true)`",
    "`\"no Engineer Agent will be dispatched for your Subtask's implementation dependency while you are running\"`",
    "`\"no Engineer Agent will be dispatched for this Bee while you are running\"`",
    "`bees update-ticket --ids <subtask-id> --status in_progress`",
    "Clause 1",
    "Clause 2",
    "`Plan <bee-id>, Epic N, Task M — <task title> (<task-id>)`",
    "resolve-hive-paths --hive plans",
    "## Task [N] of [total] Complete: [task-title]",
    "**Follow-up Tasks Created**",
    "Proceeding to next Task: [next-task-title]",
    "Final Task, moving on to Final Reviews",
    "**Inter-Epic interaction checkpoint.**",
    "`git log --oneline <previous-epic-last-commit>..HEAD`",
    "**Contract drift**",
    "**Resource compounding**",
    "**Symmetric-change gaps**",
    "**Drafted (or blocked-on-drafted) Epics remain**",
    "**Workable Epic remains**",
    "**All Epics under this Bee are `done`**",
    "`Mode 2 (Work through all Epics): auto-continuing to <next-epic-id> — <title>.`",
    "#### Epic-boundary state-externalization checkpoint",
    "#### Epic-boundary context-window guard",
    "`/quo-execute <bee-id>`",
    "`## Deferred from /quo-execute run (<YYYY-MM-DD HH:MM>)`",
    "`Encode deferral: /quo-execute — <N> deferral(s) encoded`",
    "--skill quo-execute --count <N> [--doc-path <abs-path> ...]",
    "`git diff <pre-bee-sha>`",
    "#### Aborted-run close-out",
    "`<epic-id>: aborted mid-Epic at <task-id> — last commit <sha>`",
    "`<bee-id>: Bee-level review aborted — <what stopped it>`",
    "`Cannot mark Bee complete — Epics <ids> are still <status>. Run /quo-breakdown-epic and /quo-execute on them first.`",
    "`bees update-ticket --ids <bee-id> --status done`",
    "## Bee Execution Complete: [bee-title]",
    "**Bee Status**: Finished",
    "All per-Task work has been committed.",
    "`/bees-worktree-rm`",
    "`git merge bee/b.Wx7`",
]


def test_execute_rule_anchors_are_present():
    assert_present(EXE_ANCHORS, EXE, "quo-execute")


REFERENCE_ANCHORS = {
    REF_ROUTING: [
        "## What \"highest-quality\" means",
        "## What \"introduces a mechanism\" means",
        "## (b) ANTI-PATTERN — do not write this:",
        "`\"out of scope for this issue\"`",
        "`\"out of scope for <id>\"`",
        "`\"prefer option (a)\"` / `\"prefer (a)\"`",
        "`\"Do NOT add X — out of scope\"`",
        "## (e) Backwards-compatibility shim.",
        "## (f) Edge-case handling.",
        "**Malformed tags.**",
        "**Routing ambiguity.**",
        "**`/quo-file-issue` failure at the Defer gate.**",
    ],
    REF_POST_COMPLETION_PROMPT: [
        "You are an independent reviewer for a quorum <unit-noun> that was just shipped.",
        "PHASE 1 — Consume the compromise tracker (passed as a FILE PATH).",
        "PHASE 2 — Challenge each tracked compromise on its merits.",
        "PHASE 3 — Ungated-pick plausibility check, on TWO axes.",
        "PHASE 4 — Fix-path-enumeration plausibility check.",
        "PHASE 5 — Holistic solution-quality judgment beyond the logged compromises",
        "PHASE 6 — Discrete-defect sweep (the final phase).",
        "`[compromise-challenge]`",
        "`[design]`",
        "`[defect]`",
        "\"no issues found\"",
        "`git ls-files --others --exclude-standard`",
        "`<pre-run-sha>`",
        "`<unit-noun>`",
    ],
    REF_COMPROMISE_TRACKER: [
        "`compromises-<YYYYMMDD-HHMM>-<short-suffix>.md`",
        "`User overrode auto-route after post-completion challenge (depth misjudgment)`",
        "`User accepted under-enumeration after post-completion challenge`",
        "`File follow-up Issue to revisit the depth decision`",
        "`Accept the misjudgment and proceed`",
        "`File follow-up Issue to surface the missing path`",
        "`Accept the under-enumeration and proceed`",
        "`Pause to discuss`",
    ],
    REF_CONTEXT_GUARD: [
        "`<tempdir>/.quorum/context-usage-<session_id>.json`",
        "`session_id`",
        "`used_percentage`",
        "`stop-threshold`",
        "`write-opt-out`",
        "`/quo-setup --configure-gauge-producer`",
    ],
    REF_URL_RESOLUTION: [
        "`Filing URL(s) as Issue(s) first, then fixing.`",
        "`url: <url>`",
        "`issue_ticket_id`",
        "`issue_status`",
        "`action`",
        "`created`",
        "`reused-existing`",
        "Post-resolution working list:",
    ],
    REF_GITHUB_CLOSE: [
        "`git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD`",
        "`git rev-parse --short <full-sha>`",
        "Upstream GitHub Issues to consider closing:",
        "`https://github.com/<owner>/<repo>/issues/<n>`",
    ],
}


@pytest.mark.parametrize("ref", sorted(REFERENCE_ANCHORS))
def test_reference_file_rule_anchors_are_present(ref):
    assert_present(REFERENCE_ANCHORS[ref], read(ref), ref)


def test_bodies_name_their_reference_files_and_the_files_exist():
    for name, text in BODIES.items():
        skill_dir = REPO_ROOT / "skills" / name
        table = heading_section(text, "## 3. After a compaction")
        paths = re.findall(r"`(<this skill's base directory>[^`]+\.md)`", table)
        assert paths, f"{name}: Section 3 names no reference paths"
        for p in paths:
            resolved = (skill_dir / p.replace("<this skill's base directory>/", "")).resolve()
            assert resolved.is_file(), f"{name}: reference path {p} does not resolve to a file"
    fix_paths = re.findall(r"`(<this skill's base directory>[^`]+\.md)`", heading_section(FIX, "## 3. After a compaction"))
    assert len(fix_paths) == len(SHARED_REFS) + len(FIX_ONLY_REFS)


# --- (d) gate choice labels -------------------------------------------------------

SHARED_GATE_LABELS = {
    "session effort": ["**Proceed anyway**", "**Let me change it first**"],
    "isolation": ["**Work on current branch**", "**Set up a worktree instead**"],
    "unexplained movement": ["**Re-dispatch the writer now**", "**Wait**"],
    "routing (c)": ["`Fix properly now`", "`Defer to follow-up Issue`", "`Accept the limitation`", "`(Recommended)`"],
    "routing (d)": ["`Defer to follow-up Issue`", "`Cancel`"],
    "deferral hygiene": ["`Fix in this session`", "`File as issue tickets`", "`Encode in an existing ticket body`"],
    "post-completion disposition": ["**Fix in this session**", "**File as issue tickets**", "**Skip**"],
    "analyst": ["**Approve & proceed to implementation (Recommended)**", "**Revise**", "**Cancel**"],
    "SR-6.7": ["`File follow-up Issue to revisit the depth decision`", "`Accept the misjudgment and proceed`", "`Pause to discuss`"],
    "SR-4.6": ["`File follow-up Issue to surface the missing path`", "`Accept the under-enumeration and proceed`", "`Pause to discuss`"],
}


@pytest.mark.parametrize("gate", sorted(SHARED_GATE_LABELS))
def test_shared_gate_choice_labels_are_verbatim_in_both_bodies(gate):
    for name, text in BODIES.items():
        assert_present(SHARED_GATE_LABELS[gate], text, f"{name} gate {gate}")


def test_fix_issue_only_gate_labels_are_verbatim():
    labels = [
        "**Create a feature branch (Recommended for `all` mode and list mode)**",
        "**Abort this Issue**",
    ]
    assert_present(labels, FIX, "quo-fix-issue")


def test_execute_only_gate_labels_are_verbatim():
    labels = [
        "**Create a feature branch (Recommended)**",
        "`How should this run handle multiple Epics? (You will not be asked again this run.)`",
        "**Stop after each Epic**",
        "**Work through all Epics**",
        "**Continue**",
        "**Abort this unit**",
        "`\"Are you ready to mark this Bee as done?\"`",
        "`\"Yes, mark as done\"`",
        "`\"No, we have more work to do\"`",
    ]
    assert_present(labels, EXE, "quo-execute")


def test_sr_gate_labels_match_trigger_d_labels_in_the_tracker_reference():
    tracker_ref = read(REF_COMPROMISE_TRACKER)
    for label in SHARED_GATE_LABELS["SR-6.7"] + SHARED_GATE_LABELS["SR-4.6"]:
        assert label in tracker_ref, f"Trigger D reference lacks recovery-gate label {label}"


def test_decision_enum_values_are_verbatim_in_both_bodies():
    values = [
        "User picked Defer to follow-up Issue",
        "User picked Accept the limitation",
        "Orchestrator picked path (x) — highest-quality",
        "User overrode auto-route after post-completion challenge (depth misjudgment)",
        "User accepted under-enumeration after post-completion challenge",
    ]
    for name, text in BODIES.items():
        assert_present(values, heading_section(text, "## 10. Compromise tracker"), name)


# --- (e) contract-surface headings: emitter and consumer ------------------------------

CONTRACT_SURFACES = [
    ("## Design question", [AGENT_ENGINEER], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Files changed", [AGENT_ENGINEER, AGENT_TEST_WRITER, AGENT_DOC_WRITER], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("Kinds changed:", [AGENT_ENGINEER, AGENT_TEST_WRITER, AGENT_DOC_WRITER], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Premise check", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_ANALYST]),
    ("Premise check: premise-false", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Source paths to fingerprint", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_TEST_WRITER]),
    ("## Perturbations", [AGENT_TEST_WRITER], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Engineer's completeness evidence", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_PM, AGENT_CODE_REVIEWER]),
    ("## Blast radius", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_ENGINEER, AGENT_PM, AGENT_CODE_REVIEWER, AGENT_TEST_WRITER, AGENT_DOC_WRITER, AGENT_TEST_REVIEWER, AGENT_DOC_REVIEWER]),
    ("### Blast radius", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("### Decisions for writers", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Design decisions for writers", [QUO_FIX_ISSUE, QUO_EXECUTE, AGENT_ANALYST], [AGENT_ENGINEER, AGENT_CODE_REVIEWER, AGENT_TEST_WRITER, AGENT_DOC_WRITER, AGENT_TEST_REVIEWER, AGENT_DOC_REVIEWER, QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW]),
    ("## Engineer's diff (path)", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_DOC_WRITER]),
    ("## Confirming pass", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_PM, AGENT_CODE_REVIEWER, AGENT_TEST_REVIEWER, AGENT_DOC_REVIEWER, QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW]),
    ("## Site enumeration requested", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_PM, AGENT_CODE_REVIEWER, AGENT_TEST_REVIEWER, AGENT_DOC_REVIEWER, QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW]),
    ("Confirming pass: <n> fixes checked", [QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("None — the approach leaves no test or doc decision to the writers.", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("### Deferred refinements", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("### Policy decisions this change implies", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("Analyst verdict:", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("## Authoritative design directive", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_ENGINEER]),
    ("### Second-order effects", [AGENT_PM, AGENT_CODE_REVIEWER, QUO_ENGINEER_REVIEW], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("no spec drift surface to review for this Issue", [AGENT_PM], [QUO_FIX_ISSUE]),
    ("**Your next tool use MUST address these findings now.**", [QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("**Your next tool use MUST advance the workflow.**", [QUO_ENGINEER_REVIEW, QUO_TEST_WRITER_REVIEW, QUO_DOC_WRITER_REVIEW], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("[introduces-mechanism]", [QUO_ENGINEER_REVIEW, AGENT_PM, AGENT_CODE_REVIEWER], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("addressed-now", [AGENT_PM, AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE, QUO_BREAKDOWN_EPIC]),
    ("defer-to-existing-ticket-body: <ticket-id>", [AGENT_PM, AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("defer-to-new-Issue", [AGENT_PM, AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("<scoped-marker-resolver-path>", [QUO_FIX_ISSUE, QUO_EXECUTE], [AGENT_PM]),
    ("## Doc divergence noted", [QUO_FILE_ISSUE], [QUO_FIX_ISSUE]),
    ("No code issues found.", [QUO_ENGINEER_REVIEW], [QUO_FIX_ISSUE]),
    ("No invariant added, removed, or weakened.", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
    ("None — the recommendation leaves no policy question open.", [AGENT_ANALYST], [QUO_FIX_ISSUE, QUO_EXECUTE]),
]


@pytest.mark.parametrize("surface,emitters,consumers", CONTRACT_SURFACES, ids=[s[0] for s in CONTRACT_SURFACES])
def test_contract_surface_is_present_in_every_emitter_and_consumer(surface, emitters, consumers):
    for path in emitters + consumers:
        assert surface in read(path), f"{path} lacks contract surface {surface!r}"


def test_context_gauge_vocabulary_matches_the_helper_seams():
    helper = read("skills/quo-setup/scripts/context_gauge.py")
    for token in ["stop-threshold", "write-opt-out", "no-reading", "stale", "missing", "context-guard-opt-out"]:
        assert token in helper
    for token in ["stop-threshold", "no-reading", "stale", "missing", "context-guard-opt-out"]:
        for name, text in BODIES.items():
            assert token in text, f"{name} lacks helper vocabulary {token!r}"


# --- design decisions made structural -------------------------------------------------


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_no_rule_reads_tasklist_state(name, text):
    for token in ["TaskList", "TaskCreate", "TaskUpdate", "gate-askuserquestion", "metadata.activity", "-r<n>", "-rev<n>", "-r<k>"]:
        assert token not in text, f"{name} still carries the retired TaskList carrier token {token!r}"


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_gates_are_manifest_fronted(name, text):
    gates = heading_section(text, "## 6. Gates")
    assert "`## Open gate`" in first_paragraph(gates)
    assert "`AskUserQuestion` in the same turn" in first_paragraph(gates)


def test_delegate_mode_is_stated_as_a_means_not_a_bare_imperative():
    for path in shipped_artifacts():
        if path.suffix != ".md":
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if not (rel.startswith("skills/quo-execute/") or rel.startswith("skills/quo-fix-issue/")):
            continue
        assert "stay in delegate mode" not in read(path).lower(), f"{rel} carries the bare imperative"
    statement = "The orchestrator performs mechanical steps that produce a tool artifact directly"
    assert statement in FIX and statement in EXE


def test_destination_label_is_a_single_literal_across_shipped_artifacts():
    for path in shipped_artifacts():
        assert "addressed-now-in-this-" not in read(path), f"{path} carries a retired destination spelling"


@pytest.mark.parametrize("name,text", list(BODIES.items()), ids=list(BODIES))
def test_section_vocabulary_is_uniform(name, text):
    assert not re.search(r"\bSection \d+\.\d", text), f"{name} uses dotted section numbers"
    assert not re.search(r"\bStep \d+\.\d", text), f"{name} uses dotted step numbers"
    referenced = {int(n) for n in re.findall(r"\bSection (\d+)\b", text)}
    assert referenced <= set(range(1, 14)), f"{name} references a section that does not exist: {referenced}"


def test_post_completion_scope_is_working_tree_plus_untracked_in_both_bodies():
    for name, text in BODIES.items():
        section = heading_section(text, "## 11. Post-completion review")
        assert "`git ls-files --others --exclude-standard`" in section, name
        assert "..HEAD" not in section, f"{name} still scopes the post-completion diff as a commit range"


def test_inter_epic_judgment_half_is_dispatched_not_director_run():
    section = heading_section(EXE, "## 8. Per-unit close-out")
    assert "dispatch a fresh `code-reviewer` Agent at Epic scope" in section
    assert "dispatch a fresh ephemeral Engineer" not in section


def test_context_guard_continues_silently_on_missing_reading():
    for name, text in BODIES.items():
        assert "`missing` → record `no reading`, continue silently" in text, name
        assert "**Configure now**" not in text, f"{name} still fires the retired missing-reading gate"


def test_references_directory_is_shipped():
    scanned = {p.relative_to(REPO_ROOT).as_posix() for p in shipped_artifacts()}
    for ref in SHARED_REFS + FIX_ONLY_REFS:
        assert ref in scanned, f"{ref} is not in the shipped tree"
