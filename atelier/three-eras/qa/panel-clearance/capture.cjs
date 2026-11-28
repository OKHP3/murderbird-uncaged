/* Record the selected triangle groups after the normal inspection controls position them. */
const fs = require("node:fs");
const path = require("node:path");
const assert = require("node:assert/strict");
const {
  app,
  web,
  portable: portableFile,
  serve,
  launch,
  digest,
} = require("../common.cjs");
const out = process.argv[2];
if (!out) throw Error("Pass a temporary directory for the geometry capture");
const manifest = JSON.parse(
  fs.readFileSync(path.join(app, "hosted-manifest.json")),
);
const portable = digest(portableFile),
  script = digest(path.join(web, "assets/study.js"));
assert.equal(portable, manifest.portable.sha256);
assert.equal(script, manifest.files["assets/study.js"].sha256);
const server = serve();
(async () => {
  let browser;
  try {
    await new Promise((r) => server.listen(0, "127.0.0.1", r));
    browser = await launch();
    const page = await browser.newPage({
        viewport: { width: 1000, height: 760 },
      }),
      errors = [];
    page.on("pageerror", (e) => errors.push(String(e)));
    await page.addInitScript(() => {
      window.__THREE_DEVTOOLS__ = new EventTarget();
      window.obs = [];
      __THREE_DEVTOOLS__.addEventListener("observe", (e) => {
        if (e.detail?.isScene) obs.push(e.detail);
      });
    });
    await page.goto("http://127.0.0.1:" + server.address().port);
    await page.locator("#load").click();
    await page.waitForFunction(
      () => window.murderBirdStudy?.snapshot()?.detail === "full",
      null,
      { timeout: 90000 },
    );
    const meta = await page.evaluate(() => {
      const scene = obs.find(
        (s) =>
          s.getObjectByName("advanced cranial compartment") &&
          s.getObjectByName("Exhibit boundary"),
      );
      if (!scene) throw Error("Unable to identify exhibit scene");
      const all = [];
      scene.traverse((o) => all.push(o));
      const regs = Object.fromEntries(
        all.filter((o) => o.userData.region).map((o) => [o.userData.region, o]),
      );
      const ances = (o, ancestor) => {
        for (let p = o; p; p = p.parent) if (p === ancestor) return true;
        return false;
      };
      const paint = () => scene.updateWorldMatrix(true, true);
      const selected = (era, region) => {
        const c = {};
        const mesh = all.filter((o) => o.isMesh);
        if (region === "head" || region === "breast") {
          c.cover = mesh.filter(
            (o) =>
              /^Original .+ access panel$/.test(o.name) &&
              (region === "head"
                ? o.name === "Original head access panel"
                : o.name !== "Original head access panel") &&
              o.visible &&
              o.material.visible,
          );
          const r = scene.getObjectByName(
            era +
              (region === "head" ? " cranial" : " thoracic") +
              " compartment",
          );
          c.inside = mesh.filter((o) => ances(o, r) && o.material.visible);
        } else {
          const side = region === "left-wing" ? "wing.l" : "wing.r",
            opposite = region === "left-wing" ? "wing.r" : "wing.l";
          c.wing = mesh.filter(
            (o) =>
              ances(o, regs[side]) &&
              !o.userData.eraArt &&
              !o.userData.fc_inspection &&
              !o.userData.fc_locomotion &&
              o.material.visible,
          );
          c.other = mesh.filter(
            (o) =>
              ances(o, regs[opposite]) &&
              !o.userData.eraArt &&
              !o.userData.fc_inspection &&
              !o.userData.fc_locomotion &&
              o.material.visible,
          );
        }
        return c;
      };
      const geos = new Map();
      window.__geo = geos;
      const ids = (arr) =>
        arr.map((o) => {
          const id = o.geometry.uuid;
          if (!geos.has(id)) geos.set(id, o.geometry);
          return { node: o.id, geom: id, name: o.name, mat: o.material.name };
        });
      const v = (o, p) => {
        const e = o.matrixWorld.elements,
          [x, y, z] = p;
        return [
          e[0] * x + e[4] * y + e[8] * z + e[12],
          e[1] * x + e[5] * y + e[9] * z + e[13],
          e[2] * x + e[6] * y + e[10] * z + e[14],
        ];
      };
      window.runPanel = (era, region) => {
        const select = document.querySelector("#inspection-region"),
          slider = document.querySelector("#cut-fraction");
        function open(f) {
          slider.value = f;
          slider.dispatchEvent(new Event("input", { bubbles: true }));
          paint();
        }
        select.value = region;
        select.dispatchEvent(new Event("change", { bubbles: true }));
        open(1);
        const groups = selected(era, region);
        if (Object.values(groups).some((x) => !x.length))
          throw Error(
            "Empty geometry group: " +
              era +
              "/" +
              region +
              " " +
              JSON.stringify(
                Object.fromEntries(
                  Object.entries(groups).map(([k, v]) => [k, v.length]),
                ),
              ),
          );
        const members = Object.values(groups).flat();
        const groupsById = Object.fromEntries(
          Object.entries(groups).map(([k, objs]) => [k, ids(objs)]),
        );
        const w = region === "left-wing" ? regs["wing.l"] : regs["wing.r"];
        const hinge =
          region === "head"
            ? [-0.072, 0.167, -0.21]
            : region === "breast"
              ? [-0.135, 1.044, -0.268]
              : [region === "left-wing" ? -0.238 : 0.238, 1.317, 0.039];
        const nodes = groups.cover || [w],
          anchors = nodes.map((o) => v(o, hinge));
        open(0);
        const start = nodes.map((o) => o.matrixWorld.clone());
        const samples = [];
        let drift = 0,
          reassembly = 0;
        for (const f of Array.from({ length: 51 }, (_, i) => i * 2).concat([
          0,
        ])) {
          open(f);
          for (let i = 0; i < nodes.length; i++) {
            let q = v(nodes[i], hinge);
            drift = Math.max(
              drift,
              Math.hypot(...q.map((x, j) => x - anchors[i][j])),
            );
            if (f === 0)
              reassembly = Math.max(
                reassembly,
                ...nodes[i].matrixWorld.elements.map((x, j) =>
                  Math.abs(x - start[i].elements[j]),
                ),
              );
          }
          samples.push({
            f,
            mats: members.map((o) => o.matrixWorld.elements.slice()),
          });
        }
        return {
          era,
          region,
          groups: groupsById,
          samples,
          pivotDrift: drift,
          returnMatrixError: reassembly,
        };
      };
      window.encodeGeometry = (key) => {
        const g = geos.get(key),
          a = g.attributes.position,
          ix = g.index,
          uniq = new Map(),
          p = [],
          i = [];
        for (let k = 0; k < (ix ? ix.count : a.count); k++) {
          const original = ix ? ix.getX(k) : k;
          if (!uniq.has(original)) {
            uniq.set(original, p.length / 3);
            p.push(a.getX(original), a.getY(original), a.getZ(original));
          }
          i.push(uniq.get(original));
        }
        function b64(typed) {
          const u = new Uint8Array(typed.buffer);
          let s = "";
          for (let j = 0; j < u.length; j += 16384)
            s += String.fromCharCode(...u.subarray(j, j + 16384));
          return btoa(s);
        }
        return {
          positions: b64(new Float32Array(p)),
          indices: b64(new Uint32Array(i)),
        };
      };
      const gl = document.querySelector("canvas").getContext("webgl2"),
        dbg = gl.getExtension("WEBGL_debug_renderer_info");
      return {
        model: murderBirdStudy.snapshot().modelDigest,
        gpu: gl.getParameter(dbg ? dbg.UNMASKED_RENDERER_WEBGL : gl.RENDERER),
      };
    });
    const cases = [];
    for (const era of ["maker", "mechanic", "advanced"]) {
      await page.locator('[data-era="' + era + '"]').click();
      for (const region of ["head", "breast", "left-wing", "right-wing"])
        cases.push(
          await page.evaluate(([a, b]) => runPanel(a, b), [era, region]),
        );
    }
    fs.mkdirSync(out, { recursive: true });
    const keys = await page.evaluate(() => Array.from(__geo.keys()));
    for (const key of keys) {
      const a = await page.evaluate((k) => encodeGeometry(k), key);
      for (const [suffix, bytes] of Object.entries(a))
        fs.writeFileSync(
          path.join(out, key + "." + suffix),
          Buffer.from(bytes, "base64"),
        );
    }
    fs.writeFileSync(
      path.join(out, "capture.json"),
      JSON.stringify({ portable, script, ...meta, errors, cases }),
    );
    console.log(
      cases
        .map(
          (r) =>
            r.era +
            "/" +
            r.region +
            ": " +
            Object.keys(r.groups)
              .map((k) => r.groups[k].length)
              .join("/") +
            " leaves, hinge " +
            r.pivotDrift,
        )
        .join("\n"),
    );
    assert(!errors.length);
  } finally {
    await browser?.close();
    server.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
