const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {
  web: dir,
  output,
  serve,
  launch,
  digest: sha,
} = require("./common.cjs");
const out = path.join(output, "motion");
fs.mkdirSync(out, { recursive: true });
const server = serve();
(async () => {
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  let browser;
  try {
    browser = await launch();
    const p = await browser.newPage({
      viewport: { width: 1030, height: 780 },
      reducedMotion: "reduce",
    });
    p.setDefaultTimeout(10000);
    const result = {
      utc: new Date().toISOString(),
      scriptSHA: sha(path.join(dir, "assets/study.js")),
      portable: JSON.parse(fs.readFileSync(path.join(dir, "../manifest.json")))
        .portable,
      errors: [],
    };
    p.on("pageerror", (e) => result.errors.push(String(e)));
    await p.goto("http://127.0.0.1:" + server.address().port + "/");
    await p.locator("#load").click();
    await p.waitForFunction(() => murderBirdStudy.snapshot().detail === "full");
    await p.evaluate(() => {
      window.prefProbe = [];
      const pref = matchMedia("(prefers-reduced-motion: reduce)");
      pref.addEventListener("change", (e) =>
        window.prefProbe.push({
          event: e.matches,
          time: performance.now(),
          playing: murderBirdStudy.snapshot().playing,
        }),
      );
      return pref.matches;
    });
    const rows = [];
    const observe = async (label) => {
      const v = await p.evaluate(() => ({
        snap: murderBirdStudy.snapshot().playing,
        query: matchMedia("(prefers-reduced-motion: reduce)").matches,
        app: murderBirdStudy.snapshot().reduced,
        time: murderBirdStudy.snapshot().time,
        events: window.prefProbe.slice(-3),
      }));
      rows.push({ label, ...v });
    };
    for (let i = 0; i < 8; i++) {
      await p.emulateMedia({ reducedMotion: "no-preference" });
      await p.waitForTimeout(i % 2 ? 300 : 60);
      await observe("before");
      await p.locator("[data-era=advanced]").click();
      await p.locator(i % 2 ? "#enclosure" : "#play").click();
      await p.waitForFunction(() => murderBirdStudy.snapshot().time > 0.12);
      await observe("playing");
      await p.emulateMedia({ reducedMotion: "reduce" });
      await p.waitForTimeout(350);
      await observe("after350");
      await p.waitForTimeout(850);
      await observe("after1200");
    }
    const observations = rows.filter((row) => row.label === "after1200");
    fs.writeFileSync(
      path.join(out, "motion-preference.json"),
      JSON.stringify(
        {
          scriptSHA: result.scriptSHA,
          portable: result.portable,
          rows,
          errors: result.errors,
        },
        null,
        2,
      ) + "\n",
    );
    assert.equal(observations.length, 8);
    assert.deepEqual(result.errors, []);
    for (let index = 0; index < rows.length; index += 4) {
      const [before, playing, early, settled] = rows.slice(index, index + 4);
      assert.equal(before.query, false);
      assert.equal(playing.snap, true);
      for (const reading of [early, settled]) {
        assert.equal(reading.query, true);
        assert.equal(reading.app, true);
        assert.equal(reading.snap, false);
      }
      assert.equal(early.time, settled.time);
    }
  } finally {
    await browser?.close();
    server.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
