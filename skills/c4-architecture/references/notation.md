# Notation, palette, and c4kit API

## Element kinds (`box(..., kind)`, legend swatches, `boundary(..., kind)`)
| kind | role | colour |
|---|---|---|
| `kf` | the system in focus (filled) | indigo `--k` |
| `k` | owned container/component | indigo tint |
| `g` | cloud / managed platform (GCP, AWS, k8s) | teal `--g` |
| `gh` | main external SaaS (GitHub, Slack, Stripe) | plum `--gh` |
| `p` | person (`person()`; its `h` includes the 34-unit head) | amber `--p` |
| `x` | other external, or pure/no-I/O parts | grey `--x` |

Retitle the legend rows for `g` / `gh` to the repo's actual platform and main SaaS. Keep the colour ↔ role mapping
consistent in every figure; a reader learns it once at L1.

## Edges and labels
- `edge(d, cls)`: `d` is an SVG path; draw orthogonal paths (`M x y H x2 V y2`), not diagonals.
  `cls`: `''` neutral, `k` `g` `h` `p` coloured by target kind, `bad` failure, `ok` success, `+ ' dash'` for
  imports/returns/async. Arrows point from the caller.
- `label(x, y, lines)`: halo text placed in a *gap*, never on a line, box, or boundary border.
- `text(x, y, s, cls)`: classes `t` title 15.5px, `y` type/tech mono 11.5px, `d` description 12.5px, `lb` label 12px,
  `bl` boundary label. Sizes match `c4kit.FS`.

## Boxes
`box(x, y, w, h, kind, title, typ='[Container: Go]', lines=[...], shape='rect'|'db', badge='ALWAYS')`.
Height: 25 + 17 (typ) + 6 + 16·lines + 8. Width ≥ 2·14 + longest line (c4kit WARNs on estimated overflow).

## Canvas
`svg(1200, H, body, title)`: keep the viewBox 1200 wide for full-width figures so text scales the same in every
figure; H fits the content. Lay out on a 4 or 8 unit grid, columns at round x values.

## Label conventions
- HTTP routes: the full path as served (mount prefix included), e.g. `POST /api/billing/webhook`.
- One source, several possible targets (re-promote → any terminal state): draw the common or most important
  arrow and name the others in the caption or a note; no fan-outs of near-identical arrows.

## L4 helpers
- `state(x, y, w, label, cls, busy=None)`: `st0` idle (dashed) · `st1` active · `st2` checking/gate · `st3` waiting ·
  `st4` approved · `st5` success · `st6` failure; `ex0..ex3` = one row's lifecycle new → done.
- `ring(steps, hub, arc_note=None, href='step-')` → body for `svg(620, 640, body, title, 'c4 ringsvg')`; pair with
  `<div class="ringwrap">FIG <ol class="ticks"><li id="step-1"><span class="n">1</span><div><b>…</b>…</div></li>…</ol></div>`.
- `sequence(lifelines, phases)` → `(body, H)`; lifelines `{key: (x, name, kind)}`, messages
  `(from, to, label, kind)` with kind `''` call · `ret` return (dashed) · `h` `g` coloured · `bad`.
- `.commit` diamonds (`<g class="commit"><path d="M{x} {y} l9 -9 l9 9 l-9 9 z"/></g>`) mark durable writes.

## Page assembly
`c4kit.build(figs, template, extra_css=[...], extra_defs='', argv=None)`; figs = `{'L1': svg, 'L2A': svg, ..., 'LEVELS': [...]}`.
Placeholders: `{{CSS}} {{DEFS}} {{LENS}} {{MINI:l1..l4}} {{FIG:<name>}} {{GIT:sha}} {{GIT:branch}}
{{src:path|label}}`. Repo-specific CSS goes in an `extra.css`; repo-specific `<pattern>`s in `extra_defs`.
Source links: relative when OUT is inside the repo, else GitHub blob URLs pinned to HEAD, else `file://`.
