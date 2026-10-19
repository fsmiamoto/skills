# Layout gotchas (each one shipped as a bug once)

Visual QA catches these; checking for them while laying out saves a round.

- **Label on a border.** Edge labels placed on a boundary's dashed line or a box edge read as clutter. qa.sh only
  checks text against text, so only the screenshots catch this. Center labels in the gap between boundary and box (e.g. the 88-unit gap 902–990, x = 946).
- **Crossing edges.** Two diagonals forming an X; a vertical edge running through another edge's label. Route
  orthogonally, move the label, or drop the edge if a dashed "imports" arrow adds nothing.
- **Labels between close boxes.** A 40-unit gap cannot hold a label; widen the gap to ≥ 90 and center it there.
- **Sequence leftward messages.** The number badge at the sender sits where a centered label starts. c4kit's
  `sequence()` end-anchors leftward labels before the badge; keep that when hand-drawing sequences.
- **Small boxes overflow.** Type lines like `[Container: Single-page app]` outrun 150-wide boxes. Shorten the
  type (`[Container: SPA]`) or widen the box; re-lay the row rather than overlapping neighbours.
- **Inline code wraps mid-token.** `code{white-space:nowrap}` is in page.css; split very long code into two spans.
- **Sticky nav over shots.** Element screenshots taken while the nav is sticky lose their top; qa.js makes it
  static after the hero shot. Do the same in any ad-hoc screenshot script.
- **Fonts not loaded.** Measuring before `document.fonts.ready` measures the fallback font; qa.js waits.
- **Estimator vs real overflow.** c4kit's WARNs are conservative estimates (often 10–20 on a clean page). The
  playwright check in qa.sh is the truth; fix what it reports, and read WARNs only as hints while laying out.
- **Scaling at 1024.** A 1200-wide viewBox renders at ~0.8 scale at 1024; 12px labels stay legible, 10px do not.
  Text measured at a minimum font size does not shrink with the figure, so a subtitle that just fits at 1440 can
  run under a neighbouring box at 1024. Leave ~20% spare room for text near boxes; check the 1024 shots.
- **State machines with a return edge.** Several states feeding one target plus an edge back to a middle state
  cross unless routed apart: send the outer state's edge around the far side and start the return edge outside
  the bundle.
- **Badges on filled boxes.** page.css keeps badge pills white on `kf` boxes; custom fills need the same rule.
