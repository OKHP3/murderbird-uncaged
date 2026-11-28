const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { web, output, digest, portable, manifest } = require("./common.cjs");

const portableSha =
  "ff21d980020c4654ced6e1617df1076e63eb599e99b9af1e6461643db6ad23e9";
const scriptSha =
  "69e9632fa2fbf7a86d91b270ac393a25163839e20eecd23da7511c1fa92070e4";
const modelSha =
  "20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c";
const files = {
  runtime: "runtime-checks.json",
  failure: "failure-checks.json",
  soak: "soak.json",
  "region-host": "regions/region-matrix.json",
  "capture-open": "plates/capture.json",
  gpu: "gpu.json",
  "motion-pref": "motion/motion-preference.json",
};
function checkCandidate() {
  assert.equal(fs.statSync(portable).size, 47367367);
  assert.deepEqual(manifest.portable, { bytes: 47367367, sha256: portableSha });
  assert.equal(digest(portable), portableSha);
  assert.equal(digest(path.join(web, "assets/study.js")), scriptSha);
}
checkCandidate();
const args = process.argv.slice(2);
assert.ok(
  args.length === 0 || (args.length === 1 && args[0] === "--receipts-only"),
  "Unexpected argument",
);
if (!args.length) {
  for (const [suite, receipt] of Object.entries(files)) {
    const start = Date.now();
    const run = spawnSync(
      process.execPath,
      [path.join(__dirname, suite + ".cjs")],
      { stdio: "inherit" },
    );
    if (run.error) throw run.error;
    assert.equal(run.status, 0, suite + " failed");
    assert.ok(
      fs.statSync(path.join(output, receipt)).mtimeMs >= start - 1000,
      suite + " did not write a new receipt",
    );
  }
}
function read(suite) {
  return JSON.parse(fs.readFileSync(path.join(output, files[suite])));
}
const engines = ["chromium", "webkit", "firefox", "edge"];
const runtime = read("runtime");
assert.equal(runtime.hostedScriptSHA256, scriptSha);
assert.equal(runtime.portable.sha256, portableSha);
assert.equal(runtime.transferSHA256, manifest["bird.pack"].sha256);
assert.equal(runtime.runs.length, 16);
for (const row of runtime.runs) {
  assert.ifError(row.failure);
  assert.deepEqual(row.errors, []);
  if (["fast", "slow", "portable", "retrydetail"].includes(row.mode)) {
    assert.ok(row.ready && row.initialStationary);
    assert.equal(row.verifiedFullDigest, modelSha);
  }
  if (["fast", "slow", "portable"].includes(row.mode))
    assert.deepEqual(row.missing, []);
  if (row.mode === "portable") assert.equal(row.httpCount, 0);
}
for (const engine of engines) {
  for (const mode of ["fast", "portable"]) {
    const row = runtime.runs.find(
      (row) => row.name === engine && row.mode === mode,
    );
    assert(row?.closedExact && row.exactCameraHome);
    assert(Math.abs(row.keyboardOrbitDegrees - 5) < 0.001);
    assert.equal(row.makerAtEnd, "100");
    assert.equal(row.mechanicEndTime, 5.2);
    assert.equal(row.advancedEndTime, 10.5);
    assert.equal(row.patrolDuration, 8);
    assert.equal(row.narrowLayout.overflow, false);
    for (const era of ["maker", "mechanic", "advanced"]) {
      assert.equal(row[era + "HalfCutaway"].open, 0.5);
      assert.match(row[era + "HalfCutaway"].announced, /50/);
      assert.equal(row[era + "FullCutaway"], 1);
      assert.equal(row[era + "ClosedCutaway"], 0);
    }
  }
}
const chromium = runtime.runs.filter((row) => row.name === "chromium");
for (const mode of ["fast", "slow"])
  assert.equal(chromium.filter((row) => row.mode === mode).length, 3);
const fail = chromium.find((row) => row.mode === "fail");
assert.equal(fail.ready, false);
assert.deepEqual(fail.fallback, {
  walkthroughOpen: true,
  poster: true,
  guide: true,
});
assert.equal(
  chromium.find((row) => row.mode === "retry").retrySingleActionRecovered,
  true,
);
assert.deepEqual(
  chromium.find((row) => row.mode === "retrydetail").beforeDetailRetry,
  { ready: true, detail: "first draw", resetEnabled: true },
);
const failures = read("failure");
assert.equal(failures.source.hostedScriptSHA256, scriptSha);
assert.equal(failures.source.endHostedScriptSHA256, scriptSha);
assert.equal(failures.source.portableSha256, portableSha);
for (const key of ["disabled", "midflight", "contextLoss"]) {
  const r = failures[key];
  assert(
    r.fallback && r.guideOpen && r.guideImageDecoded && r.posterBytesDecoded,
  );
  assert.deepEqual(r.errors, []);
}
const soak = read("soak");
for (const source of [soak.source, soak.finalSource]) {
  assert.equal(source.bundle, scriptSha);
  assert.equal(source.manifest.sha256, portableSha);
}
assert.deepEqual(
  soak.cache.map((r) => r.phase),
  ["cold", "warm", "cold", "warm", "cold", "warm"],
);
assert.equal(soak.dwell.length, 4);
for (const r of soak.dwell) {
  assert.ifError(r.failure);
  assert.deepEqual(r.errors, []);
  if (r.era === "idle") {
    assert(
      r.elapsedMs >= 60000 && r.idlePoseUnchanged && r.poseUnchangedAfterCamera,
    );
    assert(!r.autonomousCommandVisible && !r.playing && r.autonomousTime === 0);
  } else {
    assert(r.elapsedMs >= 120000 && r.exactReset);
    assert.equal(r.fullDigest, modelSha);
    assert(
      r.samples.length >= 12 &&
        r.samples.every((s) => s.ready && s.intact && s.open === 1),
    );
  }
}
const regions = read("region-host");
assert.equal(regions.scriptSHA, scriptSha);
assert.equal(regions.finalScriptSHA, scriptSha);
assert.equal(regions.portable.sha256, portableSha);
assert.deepEqual(regions.errors, []);
assert.equal(regions.regions.length, 48);
assert(regions.regions.every((r) => r.samples === 15 && r.resets === 5));
assert.equal(regions.interruptions.length, 75);
assert(regions.interruptions.every((r) => r.pass));
const capture = read("capture-open");
assert.equal(capture.portable, portableSha);
assert.equal(capture.script, scriptSha);
assert.equal(capture.rigidGeometryDigest, modelSha);
assert.deepEqual(capture.errors, []);
for (const era of ["maker", "mechanic", "advanced"]) {
  assert.equal(capture.eras[era].region, "all");
  assert.equal(capture.eras[era].open, 1);
  assert.equal(capture.eras[era].time, 0);
  for (const [field, name] of [
    ["newOpen", "-open.jpg"],
    ["observedRest", "-rest-observation.jpg"],
  ]) {
    assert.equal(
      capture.eras[era][field],
      digest(path.join(output, "plates", era + name)),
    );
  }
}
const gpu = read("gpu");
assert.equal(gpu.portable, portableSha);
assert.deepEqual(
  gpu.trials.map((t) => t.failure),
  [false, true],
);
for (const trial of gpu.trials) {
  const a = trial.audit;
  assert.equal(a.stage, "full");
  assert.equal(a.firstDrawRejected, trial.failure);
  assert(a.rows.length >= 26 && a.uploads.length >= a.rows.length);
  assert(a.uploads.every(([w, h]) => w === 768 && h === 768));
  assert(
    a.rows.every(
      (r) =>
        r.complete &&
        r.error === 0 &&
        r.alloc[0] === 768 &&
        r.alloc[1] === 768 &&
        r.pixels.some((v, i) => i % 4 !== 3 && v > 0),
    ),
  );
  assert.deepEqual(a.preexistingErrors, []);
  assert.deepEqual(trial.log, []);
}
const motion = read("motion-pref");
assert.equal(motion.scriptSHA, scriptSha);
assert.equal(motion.portable.sha256, portableSha);
assert.equal(motion.rows.length, 32);
assert.deepEqual(motion.errors, []);
for (let i = 0; i < 32; i += 4) {
  const [before, active, early, settled] = motion.rows.slice(i, i + 4);
  assert(!before.query && active.snap);
  assert(
    early.query &&
      early.app &&
      !early.snap &&
      settled.query &&
      settled.app &&
      !settled.snap,
  );
  assert.equal(early.time, settled.time);
}
checkCandidate();
const summary = {
  finishedUTC: new Date().toISOString(),
  portable: manifest.portable,
  hostedScript: scriptSha,
  fullModel: modelSha,
  engineVersions: Object.fromEntries(
    engines.map((name) => [
      name,
      runtime.runs.find((r) => r.name === name).engineVersion,
    ]),
  ),
  renderer: gpu.trials[0].audit.renderer,
  hostedAndOfflineCases: runtime.runs.length,
  offlineHttpRequests: runtime.runs
    .filter((r) => r.mode === "portable")
    .map((r) => r.httpCount),
  fallbackModes: ["disabled", "midflight", "contextLoss"],
  freshWarmPairs: soak.cache.length / 2,
  dwellSeconds: soak.dwell.map((r) => ({
    era: r.era,
    seconds: r.elapsedMs / 1000,
  })),
  inspectionStates: regions.regions.reduce((sum, r) => sum + r.samples, 0),
  restorations: regions.regions.reduce((sum, r) => sum + r.resets, 0),
  interruptions: regions.interruptions.length,
  gpu: gpu.trials.map((t) => ({
    injected: t.failure,
    uploads: t.audit.uploads.length,
    readableTextures: t.audit.rows.length,
  })),
  preferenceSwitches: motion.rows.length / 4,
  walkthroughCaptures: 6,
  evidence: Object.fromEntries(
    Object.values(files).map((file) => [file, digest(path.join(output, file))]),
  ),
};
fs.writeFileSync(
  path.join(output, "verified.json"),
  JSON.stringify(summary, null, 2) + "\n",
);
console.log(JSON.stringify(summary, null, 2));
