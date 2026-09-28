import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { CLAW_SCRAPE_DURATIONS } from '../src/scene/presence-state.js';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMotion } from '../src/scene/era-motion.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';

const READY = Object.freeze({ arrived: true, settled: true, aligned: true, clawContact: true });

function tick(controller, count = 1, feedback = READY) {
  let snapshot;
  for (let i = 0; i < count; i += 1) snapshot = controller.update(0.1, feedback);
  return snapshot;
}

async function makeRig() {
  const path = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
  const template = await loadRigidValidation(await readFile(path));
  const model = clone(template.scene);
  const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  const rest = Object.fromEntries(names.map(name => [name, { position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone() }]));
  const motion = createEraMotion(model, nodes, rest);
  return { model, motion, nodes };
}

test('named floor scrape has readiness-gated phases and never stacks', () => {
  const controller = createEraController();
  assert.equal(controller.getSnapshot().canClawAction, true);
  assert.equal(controller.requestClawAction(), true);
  assert.equal(controller.requestClawAction(), false);
  let snapshot = controller.getSnapshot();
  assert.deepEqual(snapshot.clawAction, { phase: 0, stage: 'approach', side: 'left', target: 'floor-scrape' });

  snapshot = tick(controller, 8, { arrived: true, settled: false, aligned: true });
  assert.equal(snapshot.clawAction.stage, 'approach', 'approach remains gated until support is settled');
  snapshot = tick(controller, 1);
  assert.equal(snapshot.clawAction.stage, 'lift');
  const stages = ['contact', 'scrape', 'release', 'recovery'];
  for (const stage of stages) {
    snapshot = tick(controller, Math.ceil(CLAW_SCRAPE_DURATIONS[snapshot.clawAction.stage] / 0.1));
    assert.equal(snapshot.clawAction.stage, stage);
    assert.equal(snapshot.actionKind, 'claw-scrape');
    assert.equal(snapshot.clawAction.target, 'floor-scrape');
  }
  snapshot = tick(controller, Math.ceil(CLAW_SCRAPE_DURATIONS.recovery / 0.1) + 5);
  assert.equal(snapshot.clawAction, null);
  assert.equal(snapshot.actionKind, null);
  assert.ok(['settle', 'watch'].includes(snapshot.state));
  const restarted = controller.requestClawAction();
  assert.equal(restarted, snapshot.canClawAction, 'another action can begin only once the watch snapshot reports readiness');
});

test('pause freezes a scrape phase and inspection runs the declared recovery before settling', () => {
  const controller = createEraController();
  assert.equal(controller.requestClawAction(), true);
  tick(controller, 4);
  const before = controller.getSnapshot();
  controller.setPaused(true);
  const frozen = tick(controller, 8);
  assert.deepEqual(frozen.clawAction, before.clawAction);
  controller.setPaused(false);
  tick(controller, 1);
  controller.setInspection(true);
  assert.equal(controller.getSnapshot().clawAction.stage, 'recovery');
  tick(controller, 20);
  assert.equal(controller.getSnapshot().clawAction ?? null, null);
  assert.equal(controller.getSnapshot().actionKind, null);
  assert.equal(controller.requestClawAction(), false);
});

test('reduced motion recovers; era changes, reset, and power moves cannot resume or overlap a scrape', () => {
  const controller = createEraController();
  assert.equal(controller.requestClawAction(), true);
  assert.equal(controller.requestPowerMove('jump'), false);
  controller.setReducedMotion(true);
  assert.equal(controller.getSnapshot().clawAction.stage, 'recovery');
  tick(controller, 20);
  assert.equal(controller.getSnapshot().clawAction ?? null, null);
  assert.equal(controller.getSnapshot().actionKind, null);
  controller.setReducedMotion(false);
  assert.equal(controller.requestClawAction(), true);
  controller.setEra('mechanic');
  assert.equal(controller.getSnapshot().clawAction ?? null, null);
  assert.equal(controller.requestClawAction(), false);
  controller.setEra('builder');
  assert.equal(controller.getSnapshot().clawAction ?? null, null);
  controller.reset();
  assert.equal(controller.getSnapshot().clawAction, null);
  assert.equal(controller.getSnapshot().actionKind, null);
});

test('floor scrape contacts actual distal claw meshes while the opposite foot stays planted', async () => {
  const { model, motion } = await makeRig();
  const supportBefore = motion.metrics().feet[1].target;
  const pivotPositions = ['left-digit-1-proximal','left-digit-1-distal','left-digit-2-proximal','left-digit-2-distal','left-digit-3-proximal','left-digit-3-distal']
    .map(name => { const node=model.getObjectByName(name); return [node, node.position.clone()]; });
  motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'lift', phase: 0.7, side: 'left', target: 'floor-scrape' } });
  const lifted = motion.metrics();
  assert.ok(lifted.feet[0].groundMin > 0.02, 'claw clears the floor while lifting');
  motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'contact', phase: 1, side: 'left', target: 'floor-scrape' } });
  const contact = motion.metrics();
  assert.equal(contact.clawAction.contact, true, 'distal digit mesh bounds confirm floor contact');
  assert.ok(Math.abs(contact.clawAction.tipMinY - 0.002) < 0.006);
  assert.ok(contact.feet[0].digits.every(digit => Math.abs(digit.angle - digit.restAngle) > 0.04), 'all six separately owned digit hinges curl');
  assert.ok(contact.feet[1].target.every((value, index) => Math.abs(value - supportBefore[index]) < 1e-8));
  assert.ok(contact.clawAction.supportError < 1e-8);
  assert.ok(contact.clawAction.supportTargetError < 1e-8);
  assert.ok(Math.abs(contact.clawAction.supportGroundMin - 0.002) < 0.01, 'the opposite support foot remains on the floor');
  for (const [node, position] of pivotPositions) assert.ok(node.position.distanceTo(position) < 1e-9, `${node.name} pivot stays fixed`);
  motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'scrape', phase: 0.7, side: 'left', target: 'floor-scrape' } });
  const scrape = motion.metrics();
  assert.equal(scrape.clawAction.contact, true);
  assert.ok(Math.abs(scrape.clawAction.tipMinY - 0.002) < 0.006);
  assert.ok(scrape.feet[0].target[2] > contact.feet[0].target[2], 'the contacting claw advances along the floor');
  assert.ok(scrape.feet[1].target.every((value, index) => Math.abs(value - supportBefore[index]) < 1e-8));
});

test('all six action phase boundaries preserve the selected-foot target and body pose', async () => {
  const { motion, nodes } = await makeRig();
  const stages = ['approach','lift','contact','scrape','release','recovery'];
  let previous = null;
  for (const stage of stages) {
    motion.tick(1 / 60, { era: 'builder', clawAction: { stage, phase: 0, side: 'left', target: 'floor-scrape' } });
    const start = motion.metrics();
    if (previous) {
      assert.ok(start.feet[0].target.every((value,index)=>Math.abs(value-previous.feet[0].target[index])<.006), `${stage} starts without a foot-target pop`);
      assert.ok(nodes.body.position.distanceTo(previous.bodyPosition)<1e-6, `${stage} starts without a body-position pop`);
    }
    motion.tick(1 / 60, { era: 'builder', clawAction: { stage, phase: 1, side: 'left', target: 'floor-scrape' } });
    const end=motion.metrics();
    previous={...end,bodyPosition:nodes.body.position.clone()};
  }
});

test('kinematic recovery from lift and contact returns smoothly to the saved foot target', async () => {
  for (const interruptStage of ['lift', 'scrape']) {
    const { motion } = await makeRig();
    const anchor = motion.metrics().feet[0].target;
    const supportBefore = motion.metrics().feet[1].target;
    if (interruptStage === 'scrape') motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'contact', phase: 1, side: 'left', target: 'floor-scrape' } });
    const start = { era: 'builder', clawAction: { stage: interruptStage, phase: 0.72, side: 'left', target: 'floor-scrape' } };
    motion.tick(1 / 60, start);
    const before = motion.metrics();
    if (interruptStage === 'scrape') assert.equal(before.clawAction.contact, true);
    motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'recovery', phase: 0, side: 'left', target: 'floor-scrape' } });
    const recoveryStart = motion.metrics();
  assert.ok(recoveryStart.feet[0].target.every((value, index) => Math.abs(value - before.feet[0].target[index]) < 0.006), 'recovery starts at the interrupted pose, keeping talons above the floor');
    for (const phase of [.25, .5, .75, 1]) motion.tick(1 / 60, { era: 'builder', clawAction: { stage: 'recovery', phase, side: 'left', target: 'floor-scrape' } });
    const recovered = motion.metrics();
    motion.tick(1 / 60, { era: 'builder', state: 'settle', inspectionRequested: true });
    const planted = motion.metrics();
    assert.ok(planted.feet[0].target.every((value, index) => Math.abs(value - anchor[index]) < 1e-8));
    assert.ok(planted.feet[1].target.every((value, index) => Math.abs(value - supportBefore[index]) < 1e-8));
    assert.ok(planted.feet.every(foot => foot.groundMin >= 0.001));
    assert.ok(planted.feet[0].digits.every(digit => Math.abs(digit.angle - digit.restAngle) < 1e-8));
  }
});

test('inspection and reduced-motion requests during lift or real floor contact run recovery before neutral state', async () => {
  for (const [stopAt, interruption] of [['lift','inspection'],['scrape','reduced-motion']]) {
    const { motion } = await makeRig();
    const controller = createEraController();
    assert.equal(controller.requestClawAction(), true);
    let metrics;
    for (let i = 0; i < 100; i += 1) {
      const snapshot = controller.getSnapshot();
      motion.tick(0.1, snapshot);
      metrics = motion.metrics();
      controller.update(0.1, motion.feedback());
      const next = controller.getSnapshot();
      if (stopAt === 'lift' && next.clawAction?.stage === 'lift' && next.clawAction.phase >= .5) break;
      if (stopAt === 'scrape' && next.clawAction?.stage === 'scrape' && metrics.clawAction?.contact) break;
    }
    metrics = motion.metrics();
    if (stopAt === 'scrape') assert.equal(metrics.clawAction.contact, true);
    if (interruption === 'inspection') {
      controller.setPaused(true);
      controller.setInspection(true);
    } else controller.setReducedMotion(true);
    assert.equal(controller.getSnapshot().clawAction.stage, 'recovery');
    for (let i = 0; i < 20 && controller.getSnapshot().clawAction; i += 1) {
      motion.tick(0.1, controller.getSnapshot());
      controller.update(0.1, motion.feedback());
    }
    assert.equal(controller.getSnapshot().clawAction, null);
    for (let i = 0; i < 10 && (interruption === 'inspection' ? !controller.getSnapshot().inspection : controller.getSnapshot().state !== 'watch'); i += 1) {
      motion.tick(0.1, controller.getSnapshot());
      controller.update(0.1, motion.feedback());
    }
    const restored = motion.metrics();
    if (interruption === 'inspection') assert.equal(controller.getSnapshot().inspection, true);
    else assert.equal(controller.getSnapshot().state, 'watch');
    assert.equal(restored.clawAction, null);
    assert.ok(restored.feet.every(foot => foot.groundMin >= .001));
    assert.ok(restored.feet[0].digits.every(digit => Math.abs(digit.angle - digit.restAngle) < 1e-8));
  }
});
