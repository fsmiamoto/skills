# Devin cloud CLI: behavior notes

Verified against `devin 3000.11.3` (Oct 2026) unless marked *unverified*.
Docs: <https://docs.devin.ai/cli/cloud>, <https://docs.devin.ai/cli/reference/commands>.

## Session lifecycle

- `devin --cloud -p` creates a cloud session, sends one prompt, streams Devin's
  messages to stdout, and exits when the turn ends (Devin goes idle: done, or
  waiting on you). A small fix + PR took ~10 min.
- Killing the CLI does **not** stop the session. Docs: "closing the terminal
  does not stop it"; "The session persists; resume it with `devin --cloud -r`".
  Tested: killed the CLI mid-`sleep 90`; the session finished the sleep and
  reported both timestamps on resume.
- No built-in detach flag. Fire-and-forget = run in the background and ignore,
  or use the REST API (below), which returns immediately with `session_id` + `url`.

## Session ID / URL

- `-p` never prints the session ID, `--export` wrote nothing for a cloud run,
  and `devin list --format json` only lists local sessions (returned `[]`).
- Reliable trick: the prompt asks Devin to reply with its session URL first.
  Devin knows it; the first stdout line becomes
  `https://app.devin.ai/sessions/<32-hex>`. Session ID = `devin-<32-hex>`.
- Messages are concatenated with no newline, e.g. `...8305DONE`. Extract with
  `grep -oE 'app\.devin\.ai/sessions/[0-9a-f]{32}'`.
- Interactive fallback: `devin --cloud -r` (no ID) opens a picker of all your
  cloud sessions, newest first, showing title + `devin-<id>`. Needs a TTY (tmux).
- Also visible in the app.devin.ai sidebar.

## Resume / follow up

```bash
devin --cloud --respect-workspace-trust false -r devin-<id> -p "follow-up message"
devin --cloud -r https://app.devin.ai/sessions/<id>     # interactive; /open, /ssh, /pickup, /archive
devin ssh devin-<id>                                     # shell on the VM
```

`/pickup` (interactive) checks out the session's PR branch locally.

## Which repo

- Every session boots the org's snapshot. All repos configured in the org's
  Devin environment are already cloned under `/home/ubuntu/repos/` (observed:
  6 repos, even when started from an empty, remote-less dir).
- A local clone or cwd is **not** required (tested from a `mktemp -d`).
  The cwd's git remote may be used as a hint (*unverified*); always name
  `owner/repo` + base branch in the prompt.
- Repos not in the environment: Devin may still clone them if its GitHub
  integration has access (*unverified*). Check with `devin cloud drs blueprint-list`.

## "Environment build incomplete … N blueprint failed setup"

DRS = Declarative Repo Setup. Blueprint (YAML) → build → snapshot that every
session boots from. Build status **partial** = some repo-level setup steps
failed; the snapshot is usable, all code is cloned, but that repo's deps/tools
may be missing (<https://docs.devin.ai/onboard-devin/environment/blueprints>).
Effect: Devin may be unable to run lint/tests locally, so CI is the real gate.
Tell the user once; it's an org admin fix (Settings → Environment, or
`devin cloud drs build-start` / `build-logs --build-job-id <id>`), not a
reason to abort.

## REST API alternative (true fire-and-forget)

```bash
curl -s https://api.devin.ai/v1/sessions -H "Authorization: Bearer $DEVIN_API_KEY" \
  -H 'Content-Type: application/json' \
  -d "$(jq -n --rawfile p prompt.md '{prompt:$p, title:"…", tags:["dispatch"]}')"
# → {"session_id": "...", "url": "https://app.devin.ai/sessions/...", ...}
```

Needs a personal API key (`apk_*`, app.devin.ai/settings/api-keys); the CLI
login is not exposed as `DEVIN_API_KEY`. Cognition's `club-cog/devin-handoff`
skill wraps this (create / poll / archive). Body fields: `prompt`, `title`,
`tags`, `max_acu_limit`, `idempotent`, `unlisted`, `secret_ids`, …
(<https://docs.devin.ai/api-reference/v1/sessions/create-a-new-devin-session>).
