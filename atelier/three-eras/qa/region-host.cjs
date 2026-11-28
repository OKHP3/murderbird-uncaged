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
const out = path.join(output, "regions");
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
      regions: [],
      interruptions: [],
      errors: [],
    };
    p.on("pageerror", (e) => result.errors.push(String(e)));
    await p.goto("http://127.0.0.1:" + server.address().port + "/");
    await p.locator("#load").click();
    await p.waitForFunction(() => murderBirdStudy.snapshot().detail === "full");
    const cycleFile = path.join(out, "region-matrix.json");
    const save = () =>
      fs.writeFileSync(cycleFile, JSON.stringify(result, null, 2) + "\n");
    const actions = {
      maker: ["neck", "leg", "wing", "tail", "jaw", "combined"],
      mechanic: ["wind"],
      advanced: [
        "first-choice",
        "patrol",
        "approach",
        "enclosure",
        "reach-left",
        "reach-center",
        "reach-right",
        "withdraw",
      ],
    };
    const state = () => p.evaluate(() => murderBirdStudy.snapshot());
    const visible = (s) => p.locator(s).isVisible();
    const drag100 = async (selector, v) =>
      p.locator(selector).evaluate((e, v) => {
        e.value = String(v);
        e.dispatchEvent(new Event("input", { bubbles: true }));
      }, v);
    for (const era of process.argv.includes("--interrupt-only")
      ? []
      : Object.keys(actions)) {
      await p.locator("[data-era=" + era + "]").click();
      const opts = await p
        .locator("#inspection-region option")
        .evaluateAll((nodes) =>
          nodes.map((x) => ({ id: x.value, label: x.textContent })),
        );
      assert.equal(opts.length, 16);
      for (const { id, label } of opts) {
        await p.locator("#inspection-region").selectOption(id);
        await p.locator("#region-focus").focus();
        await p.keyboard.press("Enter");
        const first = await state();
        const prefix = [era, id, label];
        const cam = first.view;
        const note = await p.locator("#region-note").innerText();
        assert.ok(note.length > 15, JSON.stringify(prefix));
        assert.ok(
          (id === "all" && cam === "interior") || cam === "region-" + id,
          cam + " " + id,
        );
        const receipt = await p.evaluate(
          async ({ id }) => {
            const slider = document.getElementById("cut-fraction"),
              snap = () => murderBirdStudy.snapshot();
            const baseline = JSON.stringify(snap().joints);
            let sample = 0,
              reset = 0,
              selected;
            const frames = () =>
              new Promise((a) =>
                requestAnimationFrame(() => requestAnimationFrame(a)),
              );
            for (let i = 0; i < 5; i++) {
              for (const n of [0, 50, 100]) {
                slider.value = String(n);
                slider.dispatchEvent(new Event("input", { bubbles: true }));
                if (i === 0) await frames();
                const s = snap();
                if (
                  Math.abs(s.open - n / 100) > 1e-6 ||
                  document.getElementById("inspection-region").value !== id
                )
                  throw Error("range lost selection " + id);
                if (!slider.getAttribute("aria-valuetext")?.includes(String(n)))
                  throw Error("unannounced range");
                if (s.inspection?.selection)
                  for (const g of s.inspection.selection)
                    if (g.visibleTriangles !== g.restTriangles)
                      throw Error("shared face duplication");
                if (n === 100) selected = s.inspection || null;
                sample++;
              }
              slider.value = "0";
              slider.dispatchEvent(new Event("input", { bubbles: true }));
              if (
                snap().open !== 0 ||
                JSON.stringify(snap().joints) !== baseline
              )
                throw Error("joint reset drift");
              reset++;
            }
            return {
              samples: sample,
              resets: reset,
              selection: selected?.region,
              enabledCompartment: selected?.compartments,
            };
          },
          { id },
        );
        await drag100("#cut-fraction", 100);
        await p.waitForTimeout(40);
        await p
          .locator("#canvas")
          .screenshot({
            path: path.join(out, era + "-" + id + ".jpg"),
            type: "jpeg",
            quality: 72,
          });
        await drag100("#cut-fraction", 0);
        result.regions.push({ era, id, label, note, cam, ...receipt });
      }
      save();
    }
    await p.emulateMedia({ reducedMotion: "no-preference" });
    for (const [era, rows] of Object.entries(actions)) {
      for (const action of rows)
        for (const interrupt of [
          "pause",
          "reduced-motion",
          "inspection",
          "reset",
          "rapid-switch",
        ]) {
          const rec = { era, action, interrupt };
          try {
            await p.locator("[data-era=" + era + "]").click();
            await p.locator("#reset").click();
            if (era === "maker") {
              for (const command of action === "combined"
                ? ["leg", "wing", "tail", "neck", "jaw"]
                : [action]) {
                await p.locator("#linkage").selectOption(command);
                await drag100("#handle", 72);
              }
            } else {
              const target =
                action === "wind" || action === "first-choice"
                  ? "#play"
                  : action === "patrol"
                    ? "#patrol"
                    : action === "approach"
                      ? "#approach"
                      : "#enclosure";
              await p.locator(target).click();
              if (action.startsWith("reach-") || action === "withdraw") {
                await p
                  .locator(
                    "[data-lane=" +
                      (action === "withdraw" ? "center" : action.slice(6)) +
                      "]",
                  )
                  .click();
                if (action === "withdraw") await p.locator("#withdraw").click();
              }
              await p.waitForFunction(
                () =>
                  murderBirdStudy.snapshot().playing &&
                  murderBirdStudy.snapshot().time > 0.02,
                null,
                { timeout: 3500 },
              );
            }
            if (interrupt === "pause") {
              if (era === "maker") {
                assert.equal(await visible("#play"), false);
                rec.manualHasNoTransport = true;
              } else await p.locator("#play").click();
            } else if (interrupt === "reduced-motion") {
              await p.emulateMedia({ reducedMotion: "reduce" });
              await p.waitForFunction(
                () =>
                  murderBirdStudy.snapshot().reduced &&
                  !murderBirdStudy.snapshot().playing,
                null,
                { timeout: 3500 },
              );
            } else if (interrupt === "inspection") {
              await p.locator("#inspection-region").selectOption("head");
              await drag100("#cut-fraction", 50);
            } else if (interrupt === "reset") await p.locator("#reset").click();
            else
              await p.evaluate(() => {
                for (const e of [
                  "advanced",
                  "maker",
                  "mechanic",
                  "advanced",
                  "maker",
                  "advanced",
                ])
                  document.querySelector("[data-era=" + e + "]").click();
              });
            let before = await state();
            await p.waitForTimeout(75);
            let after = await state();
            rec.finalEra = after.era;
            rec.mode = after.mode;
            rec.open = after.open;
            rec.stable =
              !after.playing && Math.abs(after.time - before.time) < 1e-8;
            assert.ok(rec.stable, "still playing or drifting");
            if (interrupt === "inspection") assert.equal(after.open, 0.5);
            if (["reset", "rapid-switch"].includes(interrupt)) {
              assert.equal(after.open, 0);
              assert.equal(after.time, 0);
              assert.equal(after.encounter?.activeContact || false, false);
            }
            if (interrupt === "reduced-motion") {
              assert.equal(after.muted, true);
              await p.emulateMedia({ reducedMotion: "no-preference" });
              assert.equal((await state()).playing, false);
            }
            rec.pass = true;
          } catch (e) {
            rec.pass = false;
            rec.failure = String(e).slice(0, 200);
            await p.emulateMedia({ reducedMotion: "no-preference" });
          }
          result.interruptions.push(rec);
          save();
          if (!rec.pass) console.log("FAILED", rec);
        }
      save();
    }
    result.finalScriptSHA = sha(path.join(dir, "assets/study.js"));
    save();
    console.log(
      JSON.stringify({
        regions: result.regions.length,
        interruptions: result.interruptions.length,
        failures: result.interruptions.filter((x) => !x.pass),
        pageErrors: result.errors,
      }),
    );
  } finally {
    await browser?.close();
    server.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
