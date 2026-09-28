/** Actual exported rig, accelerated clock. This is NOT a browser/video acting test. */
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';
import { analyzeActingTrace } from './analyze-acting-trace.mjs';

const modelPath = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const output = resolve(process.env.UNCAGED_ACTING_REPORT || 'assets/audit/regression-v4/baseline-acting-envelope.json');
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const sourcePaths = [modelPath, 'src/scene/era-motion.js', 'src/scene/era-controller.js', 'src/scene/presence-state.js', 'src/scene/rigid-leg-kinematics.js', 'scripts/load-rigid-validation.mjs', 'scripts/analyze-acting-trace.mjs', 'scripts/verify-acting-envelope-v4.mjs', 'package.json', 'package-lock.json'];
const identities = [];
for (const path of sourcePaths) {
  const bytes = await readFile(path);
  identities.push({ path, bytes: bytes.length, sha256: sha(bytes) });
}
const template = await loadRigidValidation(await readFile(modelPath));
const names = ['body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive', 'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'];
const report = { schemaVersion: 2, generatedAt: new Date().toISOString(), baseCommit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(), runtime: { node: process.version, platform: process.platform, architecture: process.arch }, kind: 'accelerated-actual-rig-kinematic-diagnostic', sources: identities, runs: [], status: 'running', limits: 'No browser rendering, video, continuous human acting judgment, force simulation, audio, real-time performance, or exhaustive collision review. Renderer claw contact is based on distal-mesh proximity thresholds, not force or physical-contact proof. Distinct labels alone cannot close F08 or T06.' };
try {
  for (const seed of [927, 20260928]) {
    const model = clone(template.scene);
    const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
    assert(Object.values(nodes).every(Boolean));
    const rest = Object.fromEntries(names.map(n => [n, { position: nodes[n].position.clone(), rotation: nodes[n].rotation.clone() }]));
    const motion = createEraMotion(model, nodes, rest), machine = createEraController({ seed });
    const samples = [], dt = 1 / 60;
    for (let frame = 0; frame <= 7200; frame++) {
      const state = machine.update(frame === 0 ? 0 : dt, motion.feedback());
      for (const name of names) { nodes[name].position.copy(rest[name].position); nodes[name].rotation.copy(rest[name].rotation); }
      motion.tick(frame === 0 ? 0 : dt, state);
      if (frame % 6 === 0) {
        const m = motion.metrics();
        samples.push({ seconds: frame * dt, era: state.era, state: state.state, phase: state.phase, paused: state.paused, reducedMotion: state.reducedMotion, inspection: state.inspection, visitorPresent: state.visitorPresent, beatId: state.beatId, routeKind: state.routeKind, actionFamily: state.actionFamily, intensity: state.intensity, clawAction: state.clawAction ?? null, motion: { root: m.root, distance: m.distance, steps: m.steps, contact: m.contact, clawAction: m.clawAction ?? null, pose: m.pose, settled: m.settled, feet: m.feet.map(f => ({ side: f.side, groundMin: f.groundMin, swinging: f.swinging, solveError: f.solveError })), jointAngles: Object.fromEntries(['neck', 'head', 'jaw', 'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'].map(n => [n, nodes[n].rotation.toArray().slice(0, 3)])) } });
      }
    }
    const summary = analyzeActingTrace(samples);
    report.runs.push({ seed, clock: 'deterministic 60 Hz simulated time; sampled at 10 Hz', input: 'No controller interaction after construction', summary, samples });
    console.log(JSON.stringify({ seed, executedFamilies: summary.executedFamilyCounts, contacts: summary.contactIntervals.length, clawActions: summary.executedClawActions.length, clawContacts: summary.clawContactIntervals.length, warnings: summary.warnings }));
  }
  report.status = 'diagnostic-complete';
} catch (error) { report.status = 'failed'; report.failure = error.stack; process.exitCode = 1; }
await mkdir(dirname(output), { recursive: true });
await writeFile(output, JSON.stringify(report, null, 2) + '\n', { flag: 'wx' });
console.log(JSON.stringify({ status: report.status, output, failure: report.failure }));
