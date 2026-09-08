// Example scenario: fill a form, land on a detail page, open a dialog and
// cancel it, rename inline, then trigger an async action and let it stream.
//
//   node scripts/record.mjs scenario.mjs --base http://localhost:3000 --out /tmp/demo
//
// Rules of thumb: h.mark() every state you want in the report; h.pause()
// after every state change so viewers can read; never trigger irreversible
// side effects (real submits, payments, emails) — open the dialog and cancel.

export default async ({ page, h, base }) => {
  // 1. Landing form -------------------------------------------------------
  await page.goto(`${base}/new`, { waitUntil: "networkidle" });
  const field = page.getByRole("textbox", { name: /describe/i });
  await field.waitFor();
  h.mark("form");
  await h.pause(1400);

  await h.typeInto(
    field,
    "First line of the request.\nBackground: why we need it.\nKey points: what to emphasize.",
    { delay: 9 },
  );
  await h.pause(900);
  await h.click(page.getByRole("button", { name: "Continue" }));

  // 2. Detail page --------------------------------------------------------
  await page.waitForURL(/\/items\//, { timeout: 60_000 });
  const primaryChip = page.getByRole("button", { name: "Start as is" });
  await primaryChip.waitFor({ timeout: 60_000 }); // server work may be slow
  h.mark("detail");
  await h.drift(h.W - 260, h.H / 2); // park cursor, let the viewer read
  await h.pause(2600);

  // 3. Open confirm dialog, then cancel (no side effects) -----------------
  await h.click(primaryChip);
  await page.getByRole("heading", { name: /confirm/i }).waitFor();
  h.mark("dialog");
  await h.pause(2200);
  await h.click(page.getByRole("button", { name: "Cancel" }));
  await h.pause(900);

  // 4. Inline rename ------------------------------------------------------
  await h.click(page.getByRole("button", { name: "Edit title" }));
  const input = page.getByRole("textbox", { name: "Edit title" });
  await input.waitFor();
  h.mark("rename");
  await h.pause(700);
  await h.selectAll();
  await h.type("A shorter, clearer title", { delay: 28 });
  await h.pause(700);
  await page.keyboard.press("Enter");
  await page.getByRole("button", { name: "A shorter, clearer title" }).waitFor();
  await h.pause(1400);

  // 5. Async action that streams (cap how long we wait) --------------------
  //    Skip this section entirely if the flow has no async/streaming step;
  //    end after the last state the viewer needs to see + a short pause.
  await h.click(page.getByRole("button", { name: "Refine" }));
  h.mark("refine");
  await h.drift(h.W - 300, h.H - 200);
  await h.waitUntilIdle(page.getByRole("button", { name: "Stop" }), { timeout: 15_000 });
  await h.pause(2000);
};
