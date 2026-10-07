---
name: devin-dispatch
description: |
  Dispatch a small, self-contained fix to a Devin cloud session (`devin --cloud -p`)
  that works on its own VM and opens a PR, while the local agent keeps going.
  Covers when a fix qualifies, writing a self-contained prompt with evidence and
  the repo's PR conventions, running the blocking CLI in the background, getting
  the session URL, and following up. Use when the user asks to send, dispatch,
  hand off, or offload a fix to Devin, or to "have Devin open a PR". Keywords:
  devin, devin cloud, cloud session, dispatch, handoff, offload, small fix, ad-hoc
  fix, PR, pull request, app.devin.ai.
---

# Devin Dispatch

Send one small, well-understood fix to a Devin cloud session that opens a PR.
You write the prompt; Devin does the edit, tests, and PR on its VM.

## Fit check

Dispatch when **all** hold:
- Root cause and fix location are known; the change is a few files.
- The repo is in the org's Devin environment (`devin cloud drs blueprint-list`).
- Everything Devin needs fits in the prompt (it can't see your terminal,
  local files, Datadog, Slack, or uncommitted changes).

Don't dispatch: needs local-only context or secrets, large/ambiguous work,
open product/design decisions, or anything destructive (migrations, data
deletes, force-push, infra changes) without explicit user confirmation.

## 1. Write the prompt

Copy `assets/prompt-template.md` (relative to this skill) to
`/tmp/devin-<slug>/prompt.md` and fill it:
- `owner/repo` + base branch, explicit (no local clone needed).
- Problem **with evidence**: error text, counts, query, failing test.
- Exact fix: file, symbol, the existing pattern to copy.
- Tests to add; "keep existing tests passing".
- The repo's own conventions, read from its `AGENTS.md` / `CLAUDE.md` /
  `CONTRIBUTING.md` / PR template: lint + check commands, PR title format,
  labels, description style.
- Assignee = `gh api user --jq .login`.
- Keep the template's first line (reply with session URL) and last line
  (reply with the PR URL). Never ask Devin to merge.

Show the prompt to the user before sending unless they already said "just send it".

## 2. Dispatch

```bash
devin --cloud --respect-workspace-trust false --prompt-file /tmp/devin-<slug>/prompt.md -p
```

It **blocks** until Devin's turn ends (~10 min for a small PR; can stay attached for
minutes after the PR is created). Never run it as
a blocking shell call; use the host's background facility:
- pi: `bg_start` name `devin-<slug>`; logs in `~/.pi/bg/logs/devin-<slug>/stdout.log`
- Claude Code: Bash with `run_in_background: true`
- Codex/other: `nohup devin … > /tmp/devin-<slug>/out.log 2>&1 &`

## 3. Report, don't poll

Wait ~30 s, read stdout once, extract the URL:
`grep -oE 'app\.devin\.ai/sessions/[0-9a-f]{32}' <log>`.
Tell the user: session URL, log path, background process name. Then move on.
Check the log again only when asked or when the process exits. The PR appears
as `Created PR: [title](https://github.com/…/pull/N)`.

Follow-ups (Devin asked a question, review feedback):
`devin --cloud --respect-workspace-trust false -r devin-<id> -p "<msg>"` (also blocks).

## Gotchas

- `-p` in an untrusted dir fails without `--respect-workspace-trust false`.
- Killing the CLI does **not** stop the session; it keeps running server-side.
  Stop/archive it in app.devin.ai (or interactive `devin --cloud -r <id>` → `/archive`).
- The CLI never prints the session ID; `devin list` shows local sessions only.
  The "reply with your URL first" line in the prompt is how you get it.
- stdout joins messages with no newlines (`…8305DONE`); regex, don't split lines.
- "Environment build incomplete … blueprint failed setup" = partial DRS build:
  code is there, deps may not be, so Devin may skip lint/tests. Tell the user
  CI is the gate; not a reason to abort.
- Every session (even a test "reply OK") costs ACUs. Don't spawn throwaways.

Details, evidence, resume/ssh, REST API fire-and-forget:
[references/cloud-cli.md](references/cloud-cli.md).
