---
name: c4-architecture
description: Build a zoomable C4 architecture page for a repo, one self-contained HTML file of hand-drawn inline-SVG diagrams from cloud infra down to the core mechanism, every claim cited to source. Use when asked to diagram, map, or explain a codebase's architecture, or for a C4 / architecture overview page.
---

# C4 architecture page

One HTML file, four zoom levels, each a box from the level above opened up:
L1 system context → L2 containers + infrastructure → L3 components → L4 the core mechanism.
The page shows what is **true today**: built things only, each note linking to the file that proves it, and
planned work confined to a built-vs-planned panel. Layouts are hand-placed SVG coordinates, written in a small
Python `build.py` on top of `scripts/c4kit.py`.

`<skill>` below is this file's directory. The worked example is `<skill>/examples/acme-shop/` (a fictional store)
(`build.py` + `page.html`): read it before writing any figure; copy its patterns.

Needs `python3`, `git`, and `playwright-cli` (step 6). The run is long: guard your context. Read big files by
section (`grep -n`, then a ranged read; files ≤120 lines may be read whole), and checkpoint so any later session can resume.
On a large repo the steps rarely fit one session: once your context is past about half, finish the current
step's file, write its `Progress:` line, and stop, telling the user to resume in a fresh session with the same paths.

## 0. Set up

- `REPO`: the target repo root. `OUT`: the page path; default `REPO/docs/architecture-c4.html`. When the user
  says the repo is read-only, or names another path, OUT lives outside the repo.
- `WORK`: a scratch dir outside the repo (your run/session dir, else `/tmp/c4-<repo>`): facts files, `build.py`,
  `page.html`, `audit.md`, `shots/`. The only write inside REPO, ever, is OUT (and none when OUT is outside).
- Record `git -C REPO status --short` and `git -C REPO rev-parse --short HEAD` in WORK/notes.md.
- **Resume**: if WORK/notes.md already exists, read it and continue from its last `Progress:` line; skip done steps.
  Append `Progress: step N done — <files written>` to notes.md at the end of every step.

Done when: REPO, OUT, WORK are fixed and the status snapshot is saved.

## 1. Scope the four levels

Read the repo's README, AGENTS.md/CLAUDE.md, top-level tree, deploy/IaC dirs, CI workflows, and roadmap or plan
docs. Then read `<skill>/references/levels.md` and write WORK/levels.md:

- one line per level: what it shows, and the 1–5 figures it needs (name them `L1`, `L2A`, `L2B`, `L3A`, ...);
- the L4 mechanism and its figure shapes (from the table in levels.md);
- three research areas with their source dirs: **infra** (L1–L2), **runtime** (L2–L3), **core** (L4).

Skimming the core entry point to pick L4 shapes is fine; deep reading is step 2. A repo with no IaC still has an L2: whatever runs it (compose, a CLI on a laptop, a hosted service).

Done when: every level has named figures and every figure maps to a research area.

## 2. Research into facts files

Each area writes `WORK/facts-<area>.md` in the format of `<skill>/references/facts-template.md`: **at most 120
lines, one fact per line, no prose**. These files are re-read in steps 3–5; bloated ones exhaust your context.

- With a subagent tool: run the three areas as parallel subagents. Give each a standalone prompt: REPO path
  (read-only: no writes, no git commands that change state), its area and source dirs, the levels.md lines it
  feeds, the template path, its output path (its only write), the 120-line cap, and "every fact carries a path;
  anything only in docs is PLANNED; unproven is UNSURE". Each area also scans roadmap/design docs/TODOs in its
  scope and lists the not-yet-built items as PLANNED: they feed the built-vs-planned panel.
- Without one: research the areas in turn yourself. Finish and write each facts file before starting the next,
  then drop its details from your working memory. Never launch external agent CLIs (`claude -p`, `codex`, ...).
  This path costs most of a session; expect to checkpoint after step 2.

Done when: three facts files exist, each ≤120 lines, every fact line has a path, and `grep -c PLANNED WORK/facts-*.md`
finds the planned items (zero only if the repo has no roadmap, design docs, or TODOs; note that in notes.md).

## 3. Design each figure

First settle each facts file's "Open questions" against REPO (fix the fact, or keep it UNSURE and off the page).
Read `<skill>/references/notation.md` and `<skill>/references/layout-gotchas.md`. For each figure, list in
WORK/levels.md its elements (name, kind, facts line), edges (from → to, label, solid/dashed), boundaries, and a
rough grid: rows, column x values, canvas height. Keep labels short; plan a gap for each one: ≥90 units
between boxes that carry an edge label, labels centred in the gap, never on a line or boundary border.

Hand-placing coordinates is the costliest step; on a large repo checkpoint after it, and again after page.html.

Done when: every element and edge in every figure traces to a facts line.

## 4. Build

1. `cp <skill>/assets/page.html WORK/page.html`. Fill every `{{TODO: ...}}`: copy from the facts, notes
   as "What is true today" bullets ending in `{{src:path|label}}`, legend rows retitled, built-vs-planned lists.
   Figure names are yours: the template's `{{FIG:L2}}`, `{{FIG:L3}}`, `{{FIG:L4}}` blocks are examples; rename them
   to your levels.md names (`{{FIG:L2A}}`) and duplicate the `<h3>` + `<figure>` block per extra figure.
   Every `{{FIG:X}}` needs a key `X` in the dict passed to `c.build`. Each figure block carries its own notes list.
   `{{src:...}}` may point at a file, `file#Lnn`, or a directory.
2. Write `WORK/build.py`: `sys.path.insert(0, '<skill>/scripts')`, `import c4kit as c`, one function per figure
   returning `c.svg(...)`, `LEVELS`, then `c.build({...}, template=WORK/page.html)` (add `extra_css=[path]` only
   for project-specific styles). Helper signatures and defaults are in `c4kit.py` docstrings.
3. Run `python3 WORK/build.py --repo REPO --out OUT` and `python3 <skill>/scripts/qa/check.py OUT`.

`build()` exits listing any `{{` left. WARN lines flag missing `{{src:}}` paths and unplaced figures (fix them),
and estimated text overflow (hints only). It prints HEAD: if it differs from notes.md, record the new sha there;
the audit verifies against it.

Done when: the build writes OUT, check.py prints PASS, and no src/figure WARN remains.

## 5. Accuracy audit

Write `WORK/audit.md`: a table `| Page claim | Source (file:line or command → result) | Result |` (OK / FIXED:
what changed / REMOVED), one row per named thing on the page: every box, resource, service, package, table, flag,
number, interval, role, edge label, and arrow direction. Box subtitles share their box's row. Example row:
`| L2A Cloud SQL "postgres 16" | infra/sql.tf:12 database_version = "POSTGRES_16" | OK |`.
Each built-vs-planned item needs a PLANNED facts line; count rows with `grep -c`, never estimate.
Verify each row with grep/read against REPO at HEAD, not against the facts files: research is often wrong.
Fix or delete every claim that fails, and every PLANNED item that leaked into a diagram; correct the facts line too.

- Keep a `## Not yet verified` list at the end of audit.md; on resume, continue from it. Large pages span sessions.
- HEAD moved since the facts were written: `git -C REPO diff --name-only OLD HEAD` and re-check only claims
  citing those files.
- Rebuild after fixes; changed text can trigger new overflow WARNs.

Done when: every row has a Result, the Not-yet-verified list is empty, and the page is rebuilt.

## 6. Visual QA (at most 3 rounds)

1. Serve OUT's directory on a free port as a named background process (`python3 -m http.server PORT --bind 127.0.0.1`),
   or reuse a server already serving it.
2. `<skill>/scripts/qa/qa.sh http://127.0.0.1:PORT/<file> WORK/shots`: reports text overflow, text-on-text
   collisions, horizontal scroll at 1440 and 1024, and screenshots the hero, each level, and each figure.
3. qa.sh PASS is necessary, not sufficient: it misses labels on borders, text under boxes, and crossings.
   Look at every figure screenshot (`<level>-<FIG>-<width>.png`) at 1440 and at 1024. Hunt the defects in layout-gotchas.md: labels on lines or
   borders, crossing edges, cramped gaps, clipped or wrapped text, arrows pointing the wrong way.
4. Fix in build.py/page.html, rebuild, re-run qa.sh. Log each round's findings and fixes in WORK/notes.md.

Done when: qa.sh prints PASS and the last round's screenshot review found no defects.

## 7. Deliver

- Keep the server running; open the page for the user (`cmux browser open-split <url>` when cmux exists).
- Confirm `git -C REPO status --short` equals the snapshot from step 0, plus OUT when OUT is inside REPO.
- Report: the URL, OUT, WORK (facts, audit, shots), and the rebuild command
  (`python3 WORK/build.py --repo REPO --out OUT`).

Done when: the user has the URL and the repo has no changes beyond OUT.
