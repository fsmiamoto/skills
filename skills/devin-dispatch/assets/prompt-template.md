Repository: <OWNER/REPO>. Create a small PR, base branch `<BASE>`.
First, before doing anything else, reply with this session's web URL (https://app.devin.ai/sessions/...).

## Problem
<What is broken, where it was observed, and the evidence: error text, log query + counts,
failing test name, stack trace, reproduction steps. Paste it; Devin cannot see your
terminal, Datadog, Slack, or local files.>
<Impact: user-facing or not, why it matters.>

## Fix
In `<path/to/file>`, `<function/symbol>`, <exact change>.
<Point at an existing pattern to copy, e.g. "do it the same way as the existing X skip".>
<Anything else to update: doc comment, types, config.>

## Tests
In `<path/to/test file>`, add cases for <inputs> asserting <behavior>.
Keep the existing tests passing.

## Repo conventions (from <AGENTS.md / CLAUDE.md / CONTRIBUTING.md>)
- Run `<lint cmd>` and `<typecheck cmd>` (and the relevant tests) before committing; fix any errors.
- PR title: `<title in the repo's format>`
- Add the label `<label>` and the assignee `<github login>`.
- Keep the PR description short: problem (with evidence above), fix, tests.
- Keep the change minimal: no refactors or unrelated edits.
- Do not merge the PR, do not push to `<BASE>`, do not force-push.

When done, reply with the PR URL.
