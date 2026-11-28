const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {
  app,
  web: base,
  output: resultDir,
  serve,
  launch,
  digest: show,
} = require("./common.cjs");
const output = path.join(resultDir, "plates");
async function run() {
  fs.mkdirSync(output, { recursive: true });
  const server = serve();
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  let browser;
  try {
    browser = await launch("chrome");
    const page = await browser.newPage({
      viewport: { width: 1152, height: 900 },
      reducedMotion: "reduce",
    });
    const errors = [];
    page.on("pageerror", (error) => errors.push(String(error)));
    await page.goto("http://127.0.0.1:" + server.address().port);
    await page.click("#load");
    await page.waitForFunction(
      () => window.murderBirdStudy?.snapshot().detail === "full",
      null,
      { timeout: 45000 },
    );
    const canvas = page.locator("#canvas");
    const receipt = {
      portable: show(path.join(app, "MurderBird-Three-Eras.html")),
      script: show(path.join(base, "assets/study.js")),
      chromium: browser.version(),
      viewport: [1152, 900],
      JPEGquality: 86,
      rigidGeometryDigest: null,
      eras: {},
      errors,
    };
    for (const era of ["maker", "mechanic", "advanced"]) {
      await page.locator("[data-era=" + era + "]").click();
      await page.waitForTimeout(140);
      const rest = await page.evaluate(() => murderBirdStudy.snapshot());
      assert.equal(rest.era, era);
      assert.equal(rest.open, 0);
      await canvas.screenshot({
        path: path.join(output, era + "-rest-observation.jpg"),
        type: "jpeg",
        quality: 86,
      });
      await page.click("#open");
      await page.waitForTimeout(140);
      const open = await page.evaluate(() => murderBirdStudy.snapshot());
      assert.equal(open.era, era);
      assert.equal(open.open, 1);
      assert.equal(open.region, "all");
      const jpg = path.join(output, era + "-open.jpg");
      await canvas.screenshot({ path: jpg, type: "jpeg", quality: 86 });
      receipt.rigidGeometryDigest = open.modelDigest;
      receipt.eras[era] = {
        open: open.open,
        view: open.view,
        region: open.region,
        time: open.time,
        camera: { view: open.view, azimuth: open.azimuth },
        triangles: open.triangles,
        canvas: await canvas.boundingBox(),
        approvedRest: show(path.join(app, "assets", era + ".jpg")),
        observedRest: show(path.join(output, era + "-rest-observation.jpg")),
        newOpen: show(jpg),
      };
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(output, "capture.json"),
      JSON.stringify(receipt, null, 2) + "\n",
    );
  } finally {
    await browser?.close();
    server.close();
  }
}
run().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
