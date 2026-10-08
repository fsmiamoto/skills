---
name: cmux
description: "Reach the user through cmux. Use to notify them (waiting on input, notable failure, important completion) or to show something in a browser pane: a URL, dev server, HTML artifact, or Markdown preview."
---

# cmux

The user usually drives this host from a remote machine through cmux. Invoke the CLI as bare `cmux` (app bundle locally, `~/.cmux/bin` on remote hosts).

## Notify

`cmux notify` takes flags, never a JSON payload. Title = tool/agent name; body = the actionable message, prefixed with project context:

```bash
cmux notify --title "Pi" --body "[$(basename "$PWD")] Need your input on this change"
```

Notify sparingly: waiting on user input, notable failures, important completions.

## Show in a browser pane

The pane is a user-visible surface; repeatable browser tests stay on Playwright/headless tooling.

- New thing → new split: `cmux browser open-split http://localhost:5173`.
- Same page, known surface → reuse it: `cmux browser surface:2 navigate http://localhost:5173`.
- `file://` URLs fail. Serve local files over HTTP instead (below).
- Ask first before opening admin consoles, credentials, production dashboards, or personal data.
- Open panes when visual review, QA, or a final deliverable benefits; otherwise report the URL/path.

## Local artifacts

- **Static HTML for alignment**: `servant serve <file-or-dir>` prints a URL; open it. Explanation-only HTML needs no Playwright QA.
- **Markdown with GitHub rendering**: `uvx grip README.md` (start it with `bg_start`), open the printed URL.
- **Anything else**: serve it with a named background process on a free port; stop it when the review ends.

Showing it in the pane plus reporting the remote path is enough; copy artifacts to the user's Mac only when asked.
