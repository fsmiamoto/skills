#!/usr/bin/env node
// Record a browser demo from a scenario file.
//
//   node record.mjs <scenario.mjs> [--out DIR] [--base URL] [--width N]
//                   [--height N] [--locale en-US] [--headed] [--hide "css,selectors"]
//
// The scenario module default-exports `async ({ page, context, h, base }) => {}`.
// See ../references/scenario-example.mjs and the `h` helpers below.
//
// Output (in --out, default ./demo-out): demo.webm, marks.json, failure.png (on error).

import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

// ---------------------------------------------------------------- args ----
const argv = process.argv.slice(2);
const opts = {
  out: "demo-out",
  base: process.env.BASE ?? "",
  width: 1440,
  height: 900,
  headed: false,
  hide: "",
  locale: "en-US",
};
let scenarioPath = null;
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === "--out") opts.out = argv[++i];
  else if (a === "--base") opts.base = argv[++i];
  else if (a === "--width") opts.width = Number(argv[++i]);
  else if (a === "--height") opts.height = Number(argv[++i]);
  else if (a === "--hide") opts.hide = argv[++i];
  else if (a === "--locale") opts.locale = argv[++i];
  else if (a === "--headed") opts.headed = true;
  else if (a.startsWith("--")) die(`unknown option ${a}`);
  else scenarioPath = a;
}
if (!scenarioPath) die("usage: record.mjs <scenario.mjs> [--out DIR] [--base URL] [--width N] [--height N] [--locale TAG] [--headed] [--hide sel,sel]");

function die(msg) {
  console.error(msg);
  process.exit(2);
}

// --------------------------------------------------- resolve playwright ----
// Prefer whatever is already on the machine; never install.
function resolvePlaywright() {
  const req = createRequire(path.join(process.cwd(), "noop.js"));
  const candidates = [];
  if (process.env.PLAYWRIGHT_MODULE) candidates.push(process.env.PLAYWRIGHT_MODULE);
  candidates.push("playwright"); // project-local
  let g = "";
  try {
    g = execSync("npm root -g", { stdio: ["ignore", "pipe", "ignore"] }).toString().trim();
  } catch {}
  if (g) {
    candidates.push(path.join(g, "playwright"));
    candidates.push(path.join(g, "@playwright", "cli", "node_modules", "playwright"));
    candidates.push(path.join(g, "@playwright", "test", "node_modules", "playwright"));
  }
  try {
    const bin = execSync("command -v playwright-cli", { stdio: ["ignore", "pipe", "ignore"] })
      .toString()
      .trim();
    if (bin) {
      const real = fs.realpathSync(bin);
      candidates.push(path.join(path.dirname(real), "node_modules", "playwright"));
    }
  } catch {}
  for (const c of candidates) {
    try {
      return { pw: req(c), from: c };
    } catch {}
  }
  die(
    "playwright not found. Set PLAYWRIGHT_MODULE=/path/to/node_modules/playwright, " +
      "or install @playwright/cli globally (npm i -g @playwright/cli).",
  );
}
const { pw, from } = resolvePlaywright();

// ----------------------------------------------------------- overlays ----
// Playwright videos have no OS cursor; draw one that follows mouse events,
// plus a click ripple. Also hide common dev-tool badges/overlays.
const DEFAULT_HIDE = [
  "nextjs-portal", // Next.js dev tools button
  "vite-error-overlay",
  "#webpack-dev-server-client-overlay",
  "#__vite-plugin-checker-error-overlay",
  "astro-dev-toolbar",
  "nuxt-devtools-frame",
];
const hideSelectors = [...DEFAULT_HIDE, ...opts.hide.split(",").map((s) => s.trim()).filter(Boolean)];

const OVERLAY_SCRIPT = `
(() => {
  const HIDE = ${JSON.stringify(hideSelectors.join(","))};
  const SVG = '<svg width="22" height="22" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M5 3l14 8.5-6.2 1.4L9.5 19z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
  const ensure = () => {
    let c = document.getElementById('__demo_cursor');
    if (!c && document.body) {
      c = document.createElement('div');
      c.id = '__demo_cursor';
      c.style.cssText = 'position:fixed;left:-50px;top:-50px;z-index:2147483647;pointer-events:none;width:22px;height:22px;transform:translate(-3px,-2px);filter:drop-shadow(0 1px 2px rgba(0,0,0,.35));';
      c.innerHTML = SVG;
      document.body.appendChild(c);
      const st = document.createElement('style');
      st.textContent = HIDE + '{display:none!important}' +
        '.__demo_ripple{position:fixed;z-index:2147483646;pointer-events:none;width:36px;height:36px;margin:-18px 0 0 -18px;border-radius:50%;border:2px solid rgba(37,99,235,.9);animation:__demo_rip .45s ease-out forwards}' +
        '@keyframes __demo_rip{from{transform:scale(.3);opacity:.9}to{transform:scale(1.2);opacity:0}}';
      document.head.appendChild(st);
    }
    return c;
  };
  window.addEventListener('mousemove', (e) => {
    const c = ensure(); if (!c) return;
    c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px';
  }, true);
  window.addEventListener('mousedown', (e) => {
    if (!ensure()) return;
    const r = document.createElement('div');
    r.className = '__demo_ripple';
    r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
    document.body.appendChild(r);
    setTimeout(() => r.remove(), 500);
  }, true);
  document.addEventListener('DOMContentLoaded', ensure);
})();
`;

// --------------------------------------------------------------- setup ----
const OUT = path.resolve(opts.out);
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const { width: W, height: H } = opts;

const browser = await pw.chromium.launch({ headless: !opts.headed });
const context = await browser.newContext({
  viewport: { width: W, height: H },
  deviceScaleFactor: 1,
  recordVideo: { dir: OUT, size: { width: W, height: H } },
  locale: opts.locale,
});
await context.addInitScript(OVERLAY_SCRIPT);
const page = await context.newPage();
const videoStart = Date.now(); // recording begins when the page is created
page.setDefaultTimeout(30_000);

// ------------------------------------------------------------- helpers ----
const marks = [];
const now = () => (Date.now() - videoStart) / 1000;
const h = {
  /** Wait `ms` — use generously so viewers can read. */
  pause: sleep,
  /** Timestamp a moment (video-relative seconds) for the report / trimming. */
  mark(label) {
    marks.push({ label, s: Number(now().toFixed(1)) });
  },
  /** Glide the cursor onto a locator's center. */
  async moveTo(locator, { steps = 22, settle = 180 } = {}) {
    await locator.waitFor({ state: "visible" });
    const box = await locator.boundingBox();
    if (!box) throw new Error("moveTo: element has no bounding box");
    await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2, { steps });
    await sleep(settle);
  },
  /** Glide + press/release with a visible ripple. */
  async click(locator, o) {
    await h.moveTo(locator, o);
    await page.mouse.down();
    await sleep(70);
    await page.mouse.up();
  },
  /** Human-paced typing into the focused element. */
  async type(text, { delay = 12 } = {}) {
    await page.keyboard.type(text, { delay });
  },
  /** Click a field, then type into it. */
  async typeInto(locator, text, o) {
    await h.click(locator);
    await sleep(250);
    await h.type(text, o);
  },
  /** Cross-platform select-all in the focused input. */
  async selectAll() {
    await page.keyboard.press("ControlOrMeta+a");
    await sleep(200);
  },
  /** Park the cursor somewhere neutral while the viewer "reads". */
  async drift(x, y, { steps = 30 } = {}) {
    await page.mouse.move(x, y, { steps });
  },
  /**
   * Wait until `busyLocator` (spinner / Stop button / "Thinking…") is gone,
   * but never longer than `timeout` — caps open-ended streaming (LLM turns).
   */
  async waitUntilIdle(busyLocator, { timeout = 15_000, poll = 400 } = {}) {
    const deadline = Date.now() + timeout;
    while (Date.now() < deadline) {
      if (!(await busyLocator.isVisible().catch(() => false))) return true;
      await sleep(poll);
    }
    return false;
  },
  W,
  H,
};

// ---------------------------------------------------------------- run ----
let failed = false;
try {
  const mod = await import(pathToFileURL(path.resolve(scenarioPath)).href);
  const scenario = mod.default ?? mod.scenario;
  if (typeof scenario !== "function") die("scenario must default-export an async function");
  await page.mouse.move(W / 2, H / 2);
  await scenario({ page, context, h, base: opts.base });
  h.mark("end");
} catch (err) {
  failed = true;
  console.error("RECORDING FAILED:", err);
  await page.screenshot({ path: path.join(OUT, "failure.png") }).catch(() => {});
} finally {
  const video = page.video();
  await context.close();
  await browser.close();
  const final = path.join(OUT, "demo.webm");
  fs.renameSync(await video.path(), final);
  fs.writeFileSync(path.join(OUT, "marks.json"), JSON.stringify(marks, null, 2));
  console.log(`playwright: ${from}`);
  console.log(`video:      ${final}`);
  console.log("marks:");
  for (const m of marks) console.log(`  ${String(m.s).padStart(6)}s  ${m.label}`);
  if (failed) console.log(`screenshot: ${path.join(OUT, "failure.png")}`);
  process.exit(failed ? 1 : 0);
}
