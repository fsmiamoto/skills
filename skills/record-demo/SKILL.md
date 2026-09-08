---
name: record-demo
description: |
  Record a polished GIF/MP4 walkthrough of a web UI flow (feature demos for PRs,
  tickets, Slack, release notes). Drives the browser with Playwright at human pace,
  overlays a visible cursor + click ripples, hides dev-tool badges, then trims and
  exports with ffmpeg. Use when the user asks to record, capture, screencast, or
  make a gif/video of UI behavior or changes. Keywords: gif, video, screen recording,
  screencast, demo, walkthrough, capture flow, show the behavior.
---

# Record Demo

Produce a short (25–40 s) GIF + MP4 of a UI flow that looks hand-recorded:
smooth cursor, human typing, pauses long enough to read, no dev-tool clutter.

Scripts live in `scripts/` relative to this skill's directory; resolve them
against the skill path (`$SKILL/scripts/record.mjs`). Requires `ffmpeg` and an
existing Playwright install (`@playwright/cli` global is enough — nothing is
installed).

## Workflow

1. **Confirm the stack is live and fresh.** Identify the dev server/port for
   the *current* checkout (other worktrees may own the usual ports). Restart it
   if it predates the last edit to copy/i18n/config files — stale labels ruin
   demos.
2. **Dry-run with `playwright-cli`.** Walk the flow once by hand: `open` →
   `snapshot` → click/fill. Note stable locators (`getByRole` + visible name),
   real latencies (server-side work), and anything with side effects. Open
   confirm dialogs and **cancel** — never submit real jobs/payments/deletes.
   Check for quotas/caps the flow can hit (draft limits, rate limits): every
   dry-run *and* every recording creates its own entities, so re-runs alone can
   exhaust a cap. Delete only what **your** runs created; ask before touching
   pre-existing data.
3. **Write the scenario** (`/tmp/<name>/scenario.mjs`) from
   `references/scenario-example.mjs`. One `h.mark()` per state you'll report,
   `h.pause()` after every state change (see `references/pacing.md`).
4. **Record.**
   ```bash
   node $SKILL/scripts/record.mjs scenario.mjs --base http://localhost:3000 --out /tmp/<name>/out
   ```
   Prints the `playwright` module used, `demo.webm`, and a marks table. On
   failure it still saves the partial video + `failure.png`; fix and re-run.
5. **QA visually.**
   ```bash
   $SKILL/scripts/contact-sheet.sh /tmp/<name>/out/demo.webm --n 12 --cols 4
   ```
   *Read the sheet image.* Check: no blank leading frames, copy matches the
   working tree, every marked state is actually visible, cursor isn't parked
   on a button, streaming tail isn't a long static hold. Zoom with
   `--at 13.5,22.6 --width 1000` if a state needs a closer look.
6. **Trim + export.** Use marks for bounds (first paint ≈ `0.8`, end ≈ last
   mark + 1–2 s):
   ```bash
   $SKILL/scripts/finalize.sh /tmp/<name>/out/demo.webm --name <name> --from 0.8 --to 34
   ```
   Writes `~/Downloads/<name>.mp4` + `.gif` (override `--dest`). Prefer MP4 for
   sharing (≈10× smaller); GIF for inline previews.
7. **Clean up** entities the dry-run/recording created (test drafts, threads,
   uploads) so the user's data ends where it started.
8. **Report** file paths + sizes and a timestamped list of what the clip shows
   (from marks). Mention what was *not* exercised (e.g. "dialog cancelled, no
   real submit"), what was created/deleted, and any env noise seen (unrelated
   4xx, stale server restart).

## Scenario helpers (`h`)

| Helper | Purpose |
| --- | --- |
| `h.click(locator)` | glide cursor onto element, press with ripple |
| `h.typeInto(locator, text, { delay })` | click then type at human pace |
| `h.type(text, { delay })` | type into focused element |
| `h.selectAll()` | `ControlOrMeta+a` |
| `h.moveTo(locator)` / `h.drift(x, y)` | move cursor without clicking / park it |
| `h.pause(ms)` | reading time |
| `h.mark(label)` | timestamp for report + trimming |
| `h.waitUntilIdle(busyLocator, { timeout })` | wait for spinner/Stop to vanish, capped |
| `h.W`, `h.H` | viewport size |

`page` and `context` are raw Playwright objects; anything not covered above
(`waitForURL`, `keyboard.press`, `getByRole`, …) is used directly.

## Options

`record.mjs`: `--base URL` `--out DIR` `--width N --height N` (default 1440×900)
`--locale TAG` (default `en-US`; browser `Accept-Language`, so i18n apps render
predictably) `--headed` `--hide "sel,sel"` (extra selectors to hide; framework dev badges are
hidden by default). `PLAYWRIGHT_MODULE=/path/node_modules/playwright` overrides
resolution.

`finalize.sh`: `--from/--to` seconds, `--dest DIR`, `--gif-width PX` (1200),
`--fps N` (12), `--no-gif`, `--no-mp4`.

## Don'ts

- Don't change app code to make the recording look better; use `--hide`.
- Don't record against shared/staging data with real side effects.
- Don't ship without looking at the contact sheet.
- Don't exceed ~45 s; cut the streaming tail instead.
