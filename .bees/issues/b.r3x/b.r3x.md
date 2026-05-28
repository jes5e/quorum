---
id: b.r3x
type: bee
title: Multi-run Encode-branch writes stack identical '## Deferred from /<skill> run' headings in target ticket body
parent: null
reference_materials: null
created_at: '2026-05-28T19:41:58.331113'
status: done
schema_version: '0.1'
guid: r3x6wbyxouctkdfyk46vhty91e2cgk2m
---

## Description

The Encode-in-an-existing-ticket-body branch shipped in b.dgq (commit 63f75cc) writes a `## Deferred from /<skill> run` section to the named ticket's body via `bees update-ticket --ids <id> --body-file <path>`. When two runs of the same phase skill both Encode deferrals to the same ticket body — e.g., two `/quo-execute` runs both routing deferrals to the same Plan Bee — both writes produce a `## Deferred from /quo-execute run` heading, with no dedup contract.

Result: the target ticket's body accumulates duplicate section headings over multiple runs. Each section is content-distinct (different deferrals from different runs), but the heading is identical, so a reader scanning by heading sees ambiguity ("which run is this from?").

## Current behavior

The Encode-branch prose in the three phase skills (`/quo-execute` Section 6.5, `/quo-fix-issue` Section 7.5, `/quo-breakdown-epic` Section 6.5) instructs the orchestrator to append a `## Deferred from /<skill> run` section to the target ticket's body. There is no:

- Run identifier in the heading (timestamp, commit-SHA, session-id) to distinguish multiple runs.
- Dedup check ("if a section with this heading already exists in the body, append items to it instead of creating a new section").
- Mention in the skill prose that multi-run accumulation is expected or how to handle it.

## Expected behavior

Pick one shape and commit to it in prose:

- **(a) Disambiguate the heading.** Add a run-identifier suffix — date (`## Deferred from /quo-execute run (2026-05-28)`) or short commit-SHA (`## Deferred from /quo-execute run (cb30bc5)`). Multi-run sections sit side-by-side in the body with distinguishable headings.
- **(b) Single heading, append items.** Check whether `## Deferred from /<skill> run` already exists in the body. If it does, append the new bullet items inside the existing section. If not, create the section. One heading per skill regardless of run count.
- **(c) Allow stacking but document it.** Accept duplicate headings as a known pattern; document in skill prose that "multiple runs may stack identical headings; readers should treat each one as a per-run section in chronological order."

Recommended: **(a)** — date or short-SHA suffix. Simplest to implement (one prose change per skill, no body-parsing logic). Date is more human-readable; short-SHA is unambiguous even if multiple runs happen the same day. Either works.

## Impact

- **Reader clarity.** Future ticket-body readers (orchestrator on next-session start, human user reviewing the Plan Bee) can distinguish per-run deferral sections.
- **Idempotency tractability.** Option (b) would make multi-run Encode idempotent per-run (appending to existing section); option (a) keeps each run isolated.
- **Small surface today.** Multi-run accumulation hasn't been observed in practice yet (b.dgq just shipped), so this is forward-looking.

## Suggested fix

For option (a) — preferred:

Update the Encode-branch prose in:
- `skills/quo-execute/SKILL.md` Section 6.5
- `skills/quo-fix-issue/SKILL.md` Section 7.5
- `skills/quo-breakdown-epic/SKILL.md` Section 6.5

to specify the heading as `## Deferred from /<skill> run (<YYYY-MM-DD>)` or `## Deferred from /<skill> run (<short-sha>)`. Date is simpler — `date +%Y-%m-%d` on POSIX, `Get-Date -Format yyyy-MM-dd` on PowerShell. Short-SHA is `git rev-parse --short HEAD` either way.

The follow-up commit step (which already fires after Encode writes) carries the SHA naturally — if you prefer SHA, capture it before the Encode writes and use it in the heading.

## Background and rationale

Caught by external reviewer in a fresh-eyes pass against b.dgq's Encode-branch. Filed as a follow-up rather than fixed inline because the multi-run pattern hasn't manifested in practice yet (b.dgq shipped in the same session this Issue is filed in), so the fix is forward-looking. Filed before the pattern accumulates real ambiguity in tickets.

## Decisions and rejected alternatives

- **Option (b) append-to-existing-section.** More elegant but requires the orchestrator to parse the existing body to find the existing heading — adds complexity. Option (a) sidesteps that.
- **Option (c) accept stacking with documentation.** Acceptable but leaves the reader-clarity issue unresolved. Option (a) costs little more and fixes the underlying confusion.
