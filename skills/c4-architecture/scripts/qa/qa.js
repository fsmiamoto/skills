// Template run by qa.sh (playwright-cli run-code takes no args, so __URL__/__OUT__ are substituted).
async page => {
  const URL = '__URL__', OUT = '__OUT__';
  const report = { overflow: [], collisions: [], scrollWidth: {}, shots: [] };
  const load = async (w, h) => {
    await page.setViewportSize({ width: w, height: h });
    await page.goto(URL);
    await page.evaluate(() => document.fonts.ready);
  };
  await load(1440, 900);
  Object.assign(report, await page.evaluate(() => {
    const overflow = [], collisions = [];
    for (const s of document.querySelectorAll('svg.c4')) {
      const fig = s.getAttribute('aria-label') || s.querySelector('title')?.textContent || '?';
      // text wider than the rect it is drawn in (box(), state(), person())
      for (const g of s.querySelectorAll('g')) {
        const r = g.querySelector(':scope > rect'); if (!r) continue;
        const rb = r.getBBox();
        for (const t of g.querySelectorAll(':scope > text')) {
          if (!t.textContent.trim()) continue;
          const tb = t.getBBox();
          if (tb.x < rb.x - 1 || tb.x + tb.width > rb.x + rb.width + 1)
            overflow.push(`${fig}: "${t.textContent}" ${Math.round(tb.width)}>${Math.round(rb.width)}`);
        }
      }
      // text outside the viewBox (clipped)
      const vb = s.viewBox.baseVal, sr = s.getBoundingClientRect(), k = sr.width / vb.width;
      const texts = [...s.querySelectorAll('text')].filter((t) => t.textContent.trim());
      const boxes = texts.map((t) => t.getBoundingClientRect());
      boxes.forEach((b, i) => {
        if (b.left < sr.left - 1 || b.right > sr.right + 1 || b.top < sr.top - 1 || b.bottom > sr.bottom + 1)
          overflow.push(`${fig}: VIEWBOX "${texts[i].textContent}"`);
      });
      // text drawn over other text (label/label, label/box-title collisions); 2 svg-units of slack
      const slack = 2 * k;
      for (let i = 0; i < boxes.length; i++)
        for (let j = i + 1; j < boxes.length; j++) {
          const a = boxes[i], b = boxes[j];
          const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
          const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
          if (ox > slack && oy > slack)
            collisions.push(`${fig}: "${texts[i].textContent}" x "${texts[j].textContent}"`);
        }
    }
    return { overflow, collisions };
  }));
  for (const [w, h] of [[1440, 900], [1024, 768]]) {
    await load(w, h);
    report.scrollWidth[w] = await page.evaluate(() => document.documentElement.scrollWidth);
    await page.screenshot({ path: `${OUT}/hero-${w}.png` });
    report.shots.push(`hero-${w}.png`);
    // the sticky nav would otherwise paint over the top of element screenshots
    await page.addStyleTag({ content: 'nav.levels{position:static!important}' });
    for (const id of ['l1', 'l2', 'l3', 'l4', 'built']) {
      const sec = page.locator('#' + id);
      if (!(await sec.count())) continue;
      await sec.screenshot({ path: `${OUT}/${id}-${w}.png` });
      report.shots.push(`${id}-${w}.png`);
      const figs = sec.locator('figure');
      const n = await figs.count();
      for (let i = 0; i < n; i++) {
        // name shots by the build's figure key (data-fig), else by position
        const key = await figs.nth(i).locator('svg[data-fig]').first().getAttribute('data-fig', { timeout: 500 }).catch(() => null);
        const name = `${id}-${key || 'fig' + (i + 1)}-${w}.png`;
        await figs.nth(i).screenshot({ path: `${OUT}/${name}` });
        report.shots.push(name);
      }
    }
  }
  return JSON.stringify(report, null, 1);
}
