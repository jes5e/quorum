# URL-resolution reference (`/quo-fix-issue` only) — filing URL tokens as Issues via `/quo-file-issue`

This file is read on demand by `/quo-fix-issue` when the argument list contains a URL token. It carries the full procedure the body summarises in one paragraph. Nothing here fires a gate of this skill's own; `/quo-file-issue` fires its own gates inline.

## When this procedure runs

- It runs after the isolation strategy is settled and before the up-front `bees show-ticket --ids <id1> <id2> ...` validation pass.
- The isolation choice applies to the entire run, including the file-then-fix transition this procedure starts.
- It runs only when at least one token matched `^https?://`; on the all-IDs path every step below is skipped and nothing is printed.

## Procedure

1. Print the informational line `Filing URL(s) as Issue(s) first, then fixing.` This is console output, not a gate; the user is not asked to confirm.
2. For each URL token, in input order, dispatch `/quo-file-issue` inline through the Skill tool. Pass `args` as the free-text payload `url: <url>`.
3. Send only `url: <url>`; leave the optional `summary:` field unset so `/quo-file-issue` performs its own `WebFetch`. This skill does not pre-fetch.
4. Capture three fields from the structured return: `issue_ticket_id`, `issue_status` (always `open` on success), and `action` (exactly `created` or `reused-existing`).
5. Substitute `issue_ticket_id` for the URL token in place, at the same position. NEVER append at the tail, NEVER reorder surrounding tokens, NEVER deduplicate within the list. `action` is informational and not load-bearing for the substitution.
6. Treat any of these as a dispatch failure for that one token: the Skill tool raises an error; the user cancels at one of `/quo-file-issue`'s gates (the distill `Approve` / `Revise` / `Cancel` gate, the External-reference body-confirmation step, or the dedupe disambiguation gate's `Cancel`); `/quo-file-issue` returns a non-success structured return.
7. On a dispatch failure, drop that token, report the failure, and continue with the remaining tokens. A single dropped URL never aborts the run when other tokens remain.
8. After every URL token is resolved or dropped, print the post-resolution working list as informational markdown, one line per input position, calling out URL positions with their `action`:

```
Post-resolution working list:
1. b.cnb (input: b.cnb)
2. b.<new-id> (input: https://github.com/example/repo/issues/123, action: created)
3. b.xet (input: b.xet)
```

9. The display is informational only: no `AskUserQuestion`, no ability to re-order. A user unhappy with the order presses `Ctrl-C` and re-runs with corrected positional order.
10. Record each filing in the manifest's `## Lanes` as a lane named `file-from-url-<n>`, `<n>` the 1-based index of the URL token in the argument list; mark it closed when `issue_ticket_id` is captured or the token is dropped.
11. Continue at the up-front validation pass. The dropped-token count is cumulative across this procedure and that pass; only when no valid token remains after both does the run exit with an error. On the single-URL path a dropped URL leaves the list empty and that rule fires.

## Notes

- Each `/quo-file-issue` structured return is a hand-off marker, not a signal that this run has terminated.
- In-place substitution preserves the user's order because an Issue filed from an earlier URL may be a prerequisite of a later token.
- The index, not the URL, discriminates the `file-from-url-<n>` lane because a URL may be long, may repeat after dedupe, or may contain reserved characters.
