/** Targeted exported-bill contact diagnostic. No browser, collision or physics claim. */
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname } from 'node:path';
import { createHash } from 'node:crypto';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

const [modelPath, reportPath] = process.argv.slice(2);
assert(modelPath && reportPath, 'Provide actual GLB and new report paths.');
const names = ['body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover',
  'winding-drive', 'power-core', 'processing', 'industrial-repairs', 'builder-optics',
  'left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'];
const sourcePaths = [modelPath, 'src/scene/era-motion.js', 'src/scene/era-controller.js',
  'src/scene/cervical-articulation.js', 'scripts/load-rigid-validation.mjs',
  'scripts/verify-v38-head-contact.mjs'];
const sources = [];
for (const path of sourcePaths) {
  const bytes = await readFile(path);
  sources.push({path, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
}
const template = await loadRigidValidation(await readFile(modelPath));
const report = {generatedAt: new Date().toISOString(), kind: 'actual-export-kinematic-diagnostic',
  sources, runs: [], status: 'running',
  scope: 'Three visitor rails through actual controller approach, warning, strike, contact and recovery. Actual exported bill triangles drive the solver. Attachment translations, contact radius and foot reach are sampled at 60 Hz. No continuous collisions, solid containment, physics, visual acceptance or performance benchmark.'};
for (const inputX of [-1, 0, 1]) {
  const run = {inputX, status: 'running', states: [], frames: 0, contacts: [],
    maxAttachmentTranslationError: 0, maxFootSolveError: 0, maxContactRadiusError: 0};
  report.runs.push(run);
  try {
    const model = clone(template.scene);
    const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
    assert(Object.values(nodes).every(Boolean), 'Missing retained rig owner.');
    const rest = Object.fromEntries(names.map(name => [name, {
      position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone()}]));
    const motion = createEraMotion(model, nodes, rest), machine = createEraController({seed: 927});
    assert(machine.requestReach({x: inputX, y: .25}), 'Reach request rejected.');
    let lastState = '', recovered = false;
    for (let frame = 0; frame < 960; frame++) {
      const state = machine.update(1 / 60, motion.feedback());
      for (const name of names) {
        nodes[name].position.copy(rest[name].position);
        nodes[name].rotation.copy(rest[name].rotation);
      }
      motion.tick(1 / 60, state);
      const metrics = motion.metrics(), cervical = metrics.cervical;
      run.frames++;
      if (state.state !== lastState) {run.states.push(state.state); lastState = state.state;}
      run.maxAttachmentTranslationError = Math.max(run.maxAttachmentTranslationError,
        cervical.baseTranslationError, cervical.skullTranslationError, cervical.upperTranslationError,
        ...cervical.pitchJoints.map(joint => joint.translationError));
      run.maxFootSolveError = Math.max(run.maxFootSolveError, metrics.maxFootError);
      assert(Number.isFinite(run.maxAttachmentTranslationError), 'Non-finite cervical attachment.');
      assert(run.maxAttachmentTranslationError < 1e-7, 'Contact solver translated a fixed cervical attachment.');
      assert(run.maxFootSolveError < .002, 'Foot reach solve exceeded existing 2 mm tolerance.');
      if (state.state === 'contact' && metrics.contact) {
        const railX = state.lookTarget?.x ?? state.goal?.x;
        const radius = Math.hypot(metrics.contactPoint[0] - railX, metrics.contactPoint[2] - 2.1);
        run.maxContactRadiusError = Math.max(run.maxContactRadiusError, Math.abs(radius - .021));
        assert(Math.abs(radius - .021) <= .008, 'Actual bill/rail contact missed existing tolerance.');
        run.contacts.push({frame, point: metrics.contactPoint, railX, radius,
          neckPitch: cervical.totalPitch, approach: metrics.contactApproach});
      }
      if (state.state === 'recover' && run.contacts.length) {recovered = true; break;}
    }
    assert(recovered && run.contacts.length, 'Contact and recovery were not both observed within16 simulated seconds.');
    assert(run.states.includes('warning') && run.states.includes('strike'), 'Encounter skipped warning/strike.');
    run.status = 'passed';
  } catch (error) {run.status = 'failed'; run.failure = error.stack;}
}
report.status = report.runs.every(run => run.status === 'passed') ? 'passed' : 'failed';
await mkdir(dirname(reportPath), {recursive: true});
await writeFile(reportPath, JSON.stringify(report, null, 2) + '\n', {flag: 'wx'});
console.log(JSON.stringify({status: report.status, reportPath, runs: report.runs.map(({inputX, status, frames,
  contacts, maxAttachmentTranslationError, maxFootSolveError, failure}) => ({inputX, status, frames,
  contacts: contacts.length, maxAttachmentTranslationError, maxFootSolveError, failure}))}));
if (report.status !== 'passed') process.exitCode = 1;
