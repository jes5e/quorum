# GitHub close recommendation reference (`/quo-fix-issue` only)

This file is read on demand by `/quo-fix-issue` at its final step. The skill emits a copy-paste block of `gh issue close` commands and never runs them.

## Scope

- One bullet per fixed Issue whose `reference_materials` carries a `github-issue` resolver.
- The recommendation is scoped to the `github-issue` resolver only; do not generalise it to `linear-issue` or `url`.
- The fixed-issue list is the set of Issues this run actually marked `done`, in the order worked. Skipped, cancelled, and never-reached Issues are not in it.

## Procedure

1. For each fixed Issue, read its `reference_materials`. Re-use the value already read for the dispatch prompts when it is still in view; otherwise re-read with `bees show-ticket --ids <issue-id>`.
2. `reference_materials` is a JSON array of `{value, resolver}` objects. An empty or null value means the Issue was filed in default capture mode and contributes nothing.
3. For each entry whose `resolver == "github-issue"`, parse `value` against `https://github.com/<owner>/<repo>/issues/<n>` to extract `<owner>`, `<repo>`, and `<n>`. HTTP and HTTPS both match; trailing slashes, fragments, and query strings are ignored. Skip an entry that does not match; `/quo-file-issue` writes only canonical Issue URLs, so a mismatch is a malformed entry.
4. Obtain the per-Issue commit SHA. Preferred: the SHA recorded under the manifest's `**Progress:**` entry `- <issue-id>: done — commit <sha>`. Abbreviate a full 40-character SHA with `git rev-parse --short <full-sha>`.
5. Fallback when the SHA is not recorded: run once per fixed Issue `git log --reverse --format=%h -F --grep='(<issue-id>)' <pre-session-sha>..HEAD`, substituting the literal Issue ID and the manifest's `**Pre-session SHA:**`. `-F` makes the pattern literal so `.` and the parentheses match as themselves; `%h` emits the abbreviated SHA directly. Each invocation returns at most one match.
6. Append one bullet per matching entry, in `reference_materials` array order: `gh issue close <n> --repo <owner>/<repo> -c "Fixed in <sha>."`
7. Suppress the entire block when zero bullets were collected.

## Output shape

```
Upstream GitHub Issues to consider closing:

- gh issue close <n1> --repo <owner1>/<repo1> -c "Fixed in <commit-sha-1>."
- gh issue close <n2> --repo <owner2>/<repo2> -c "Fixed in <commit-sha-2>."
```

- Bullet order matches the fixed-issue iteration order.
- The block is informational console output, not an `AskUserQuestion` gate. Emit it, then yield.
