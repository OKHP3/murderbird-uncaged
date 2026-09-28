import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';

const root = process.cwd();
// Alignment derivative: retain the neutral-v2 script and receipts unchanged.
const modelPath = resolve(root, process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb');
const reportPath = resolve(root, process.env.UNCAGED_AUDIT || 'assets/audit/alignment-v4', 'mechanism-validation.json');
assert.ok(!reportPath.includes('/neutral-v2/'), 'Alignment checks cannot replace neutral-v2 receipts.');
const bytes = await readFile(modelPath);
const arrayBuffer = bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
const gltf = await loadRigidValidation(bytes);
const scene = new THREE.Scene();
const model = gltf.scene;
scene.add(model);
const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
assert.ok(names.every(name => nodes[name]), 'all runtime contract nodes load from the structural GLB');
const rest = Object.fromEntries(names.map(name => [name, { position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone() }]));
model.updateMatrixWorld(true);
const mechanisms = createEraMechanisms({ scene, model, nodes, rest });
const result = { generatedAt: new Date().toISOString(), model: modelPath, sha256: createHash('sha256').update(bytes).digest('hex'), textureDecoding: 'excluded in Node motion test; checked separately in browser', renderer: 'none (headless Three.js scene)', checks: {} };
const finitePositive = value => Number.isFinite(value) && value > 0;
const find = name => scene.getObjectByName(name);

try {
  mechanisms.setEra('maker');
  mechanisms.tick(.016, { articulation: { leg:.2, wing:.1, tail:.1, neck:.1, jaw:.1 } }, {}, { open:0, separation:0 });
  let metric = mechanisms.metrics();
  assert.equal(metric.visible.maker, true);
  assert.equal(metric.visible.builder, false);
  assert.equal(metric.inspectionConnections.powerCore.mode, 'not-eligible');
  assert.equal(metric.externalControlTargets.length, 5);
  for (const target of ['left-foot','right-mantle','compact-articulated-tail','neck','jaw']) {
    const horn = find(`maker-control-horn-${target === 'left-foot' ? 'leg' : target === 'right-mantle' ? 'wing' : target === 'compact-articulated-tail' ? 'tail' : target}`);
    assert.ok(horn?.visible && Number.isFinite(horn.scale.y) && horn.scale.y > 0, `${target} Maker control horn joins a live joint to its offset control point`);
  }
  result.checks.maker = { visible: metric.visible, targetCount: metric.externalControlTargets.length, horns: 'five finite joint-to-offset connectors' };

  mechanisms.setEra('mechanic');
  mechanisms.tick(.016, {}, { mechanicalPhase:.5, camAngle:Math.PI, mechanicalStage:'release' }, { open:0, separation:0 });
  metric = mechanisms.metrics();
  assert.equal(metric.visible.mechanic, true);
  assert.equal(metric.visible.builder, false);
  assert.equal(metric.inspectionConnections.powerCore.mode, 'not-eligible');
  for (const side of ['left','right']) {
    assert.ok(find(`mechanic-${side}-slotted-knee-link-sleeve`)?.visible, `${side} slotted sleeve visible`);
    assert.ok(find(`mechanic-${side}-slotted-knee-link-slider`)?.visible, `${side} slotted slider visible`);
    assert.ok(finitePositive(metric.inspectionConnections.mechanicSlidingLinks[side]), `${side} linkage length is finite`);
  }
  result.checks.mechanic = { visible: metric.visible, slidingLinks: metric.inspectionConnections.mechanicSlidingLinks };

  mechanisms.setEra('builder');
  mechanisms.tick(.016, {}, { actualArticulation:{} }, { open:0, separation:0 });
  metric = mechanisms.metrics();
  assert.equal(metric.visible.builder, true);
  assert.equal(metric.inspectionConnections.separationMode, 'connected');
  assert.equal(metric.inspectionConnections.powerCore.mode, 'connected');
  assert.equal(find('builder-core-to-distribution-conduit')?.visible, true);
  assert.ok(metric.inspectionConnections.wing.endpointDistance < .5, 'assembled shoulder/elbow endpoints remain local');
  assert.ok(metric.inspectionConnections.cervical.length === 2);
  assert.ok(metric.inspectionConnections.cervical.every(link => link.mode === 'connected' && finitePositive(link.endpointDistance)));
  result.checks.builderAssembled = metric.inspectionConnections;
  const assembledWingDistance = metric.inspectionConnections.wing.endpointDistance;
  scene.updateMatrixWorld(true);
  const busBounds = new THREE.Box3().setFromObject(find('builder-sealed-bus-case'));
  const coreBounds = new THREE.Box3().setFromObject(nodes['power-core']);
  const busCenter = busBounds.getCenter(new THREE.Vector3());
  assert.equal(busBounds.intersectsBox(coreBounds), false, 'protected distribution case clears the retained power package');
  assert.ok(busBounds.min.y > 1 && busBounds.max.y < 1.4, 'distribution case remains inside the torso height, above the leg roots');
  const manifoldSocket = find('builder-core-conduit-socket');
  assert.ok(manifoldSocket.position.distanceTo(nodes['power-core'].getWorldPosition(new THREE.Vector3())) < 1e-6);
  result.checks.protectedDistribution = { busCenter: busCenter.toArray(), busMin:busBounds.min.toArray(), busMax:busBounds.max.toArray(), powerBoundsClear:true, scope:'Rest-pose packaging bounds, not a full assembly collision proof' };

  nodes['right-mantle'].position.copy(rest['right-mantle'].position).add(new THREE.Vector3(-.39,.09,0));
  nodes['right-wing-shield'].position.copy(rest['right-wing-shield'].position).add(new THREE.Vector3(-.11,-.04,.12));
  nodes['power-core'].position.copy(rest['power-core'].position).add(new THREE.Vector3(.32,-.05,.28));
  model.updateMatrixWorld(true);
  mechanisms.tick(.016, {}, { actualArticulation:{} }, { open:1, separation:1 });
  metric = mechanisms.metrics();
  assert.equal(metric.inspectionConnections.separationMode, 'disengaged-at-sockets');
  assert.equal(metric.inspectionConnections.powerCore.mode, 'disengaged-at-sockets');
  assert.ok(metric.inspectionConnections.wing.endpointDistance > assembledWingDistance + .10, `inspection reports detached shoulder/elbow endpoints (${assembledWingDistance} -> ${metric.inspectionConnections.wing.endpointDistance})`);
  assert.ok(metric.inspectionConnections.powerCore.endpointDistance > 0, 'inspection reports the separated core/manifold socket distance');
  for (const name of ['builder-right-shoulder-actuator','builder-right-shoulder-actuator-rod','builder-shoulder-power-conduit','builder-core-to-distribution-conduit','builder-distribution-copper-run']) {
    assert.equal(find(name)?.visible, false, `${name} hides instead of stretching across the split`);
  }
  for (const name of ['builder-right-shoulder-disconnected-sleeve-stub','builder-right-elbow-disconnected-rod-stub','builder-shoulder-disconnected-body-conduit-stub','builder-shoulder-disconnected-wing-conduit-stub','builder-core-disconnected-conduit-stub','builder-distribution-disconnected-conduit-stub']) {
    const o = find(name);
    assert.equal(o?.visible, true, `${name} remains visible at its local socket`);
    assert.ok(Number.isFinite(o.scale.y) && o.scale.y < .1, `${name} has a short finite stub length`);
  }
  assert.deepEqual(metric.inspectionConnections.cervical.map(link => link.side), ['left','right']);
  assert.ok(metric.inspectionConnections.cervical.every(link => link.mode === 'disengaged-at-sockets'));
  result.checks.builderSeparated = metric.inspectionConnections;

  nodes['right-mantle'].position.copy(rest['right-mantle'].position);
  nodes['right-wing-shield'].position.copy(rest['right-wing-shield'].position);
  nodes['power-core'].position.copy(rest['power-core'].position);
  model.updateMatrixWorld(true);
  mechanisms.tick(.016, {}, { actualArticulation:{} }, { open:0, separation:0 });
  metric = mechanisms.metrics();
  assert.equal(metric.inspectionConnections.wing.mode, 'connected');
  assert.equal(metric.inspectionConnections.powerCore.mode, 'connected');
  for (const name of ['builder-right-shoulder-disconnected-sleeve-stub','builder-right-elbow-disconnected-rod-stub','builder-core-disconnected-conduit-stub','builder-distribution-disconnected-conduit-stub']) assert.equal(find(name)?.visible,false,`${name} hides after reassembly`);
  result.checks.builderReassembled = metric.inspectionConnections;

  mechanisms.setEra('mechanic');
  mechanisms.tick(.016, {}, { mechanicalPhase:.25, camAngle:Math.PI/2, mechanicalStage:'release' }, { open:0, separation:0 });
  metric = mechanisms.metrics();
  assert.equal(metric.visible.builder,false);
  assert.equal(metric.inspectionConnections.powerCore.mode,'not-eligible');
  result.checks.mechanicHidesBuilder = metric.visible;

  result.status = 'passed';
} catch (error) {
  result.status = 'failed';
  result.error = String(error?.stack || error);
  throw error;
} finally {
  mechanisms.dispose();
  await mkdir(dirname(reportPath), { recursive:true });
  await writeFile(reportPath, JSON.stringify(result, null, 2) + '\n');
}

console.log(JSON.stringify({ status:result.status, report:reportPath, checks:Object.keys(result.checks) }, null, 2));
