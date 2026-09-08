# Pacing & gotchas

## Pacing (what reads well at 1x)

| Moment                          | Setting                              |
| ------------------------------- | ------------------------------------ |
| First frame of a new screen     | `h.pause(1200–1600)` before acting   |
| Long paragraph typing           | `delay: 8–12` ms/char (≈2–3 s / 200 chars) |
| Short field typing (titles)     | `delay: 25–30` ms/char               |
| After a click that changes state| `h.pause(800–1000)`                  |
| State the viewer must read      | `h.pause(2000–2600)`                 |
| Dialog / menu on screen         | `h.pause(1600–2200)` then dismiss    |
| Streaming / spinner tail        | `h.waitUntilIdle(..., { timeout: 15_000 })` then `h.pause(2000)` |

Target total length: **25–40 s**. Longer than ~45 s → GIF balloons and nobody watches.

Move the cursor to a neutral spot (`h.drift`) while the viewer reads; a parked
cursor over a button looks like a stalled click.

## Viewport

`1440x900` default. Use `--width 1280 --height 800` for denser layouts; keep
the GIF `--gif-width` at 1000–1200 so text stays legible.

## Trimming

- The video starts when the page is created → the first ~0.5–1.0 s is blank
  before `goto` paints. Check the sheet; `--from 0.8` is typical.
- End at the last `mark` + ~1–2 s. Don't include the idle tail after streaming
  stops.
- Marks in `marks.json` are video-relative seconds → use them directly for
  `--from/--to` and for the timestamped summary in the report.

## Gotchas

- **Stale dev server.** i18n JSON / config edits may not hot-reload. If the UI
  shows old copy, restart the dev server *before* recording.
- **Hidden overlays.** Framework dev badges are hidden by default
  (`nextjs-portal`, Vite/webpack overlays, Astro/Nuxt toolbars). Add others with
  `--hide "sel1,sel2"`.
- **Select-all** is `ControlOrMeta+a` (`h.selectAll()`), works on macOS + Linux.
- **Side effects.** Open confirm dialogs and *cancel*. Never submit real jobs,
  payments, emails, or deletes in a demo run. Prefer a dedicated local DB.
- **Slow server steps** (LLM calls, builds): give `waitFor` a 60 s timeout and
  `mark` right after so the report shows real latency.
- **Locator priority.** `getByRole` with the visible name is the most stable;
  fall back to `[aria-label=…]` / `[title=…]`; avoid CSS class chains.
- **Failure.** `record.mjs` still saves the partial video + `failure.png` and
  exits 1 — look at the screenshot, fix the selector/timing, re-run.
- **No `drawtext`** in the local ffmpeg: `contact-sheet.sh` prints a
  position→timestamp legend instead of burning labels into frames.
