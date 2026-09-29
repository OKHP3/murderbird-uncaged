import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';
import { createCervicalArticulation } from '../src/scene/cervical-articulation.js';
import { createEraMotion } from '../src/scene/era-motion.js';

const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive',
  'power-core','processing','industrial-repairs','builder-optics','left-mantle',
  'right-mantle','left-wing-shield','right-wing-shield'];
const path = 'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.glb';

async function fixture() {
  const model = clone((await loadRigidValidation(await readFile(path))).scene);
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  const rest = Object.fromEntries(names.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  const followers = [
    ['cervical-root-cover', nodes.neck], ['cervical-skull-cover', nodes.head],
  ].map(([name, joint]) => {
    // Attachment-only fixture: this does not certify a V22 armor surface.
    const node = new THREE.Group(); node.name = name;
    node.position.copy(joint.position); joint.parent.add(node);
    return { node, joint, origin: node.position.clone() };
  });
  return { model, nodes, rest, followers };
}

function checkRigidReceivers(model, followers) {
  model.updateMatrixWorld(true);
  for (const { node, joint, origin } of followers) {
    assert.ok(node.position.distanceTo(origin) < 1e-12, 'Receiver translated away from its bearing');
    assert.ok(node.getWorldPosition(new THREE.Vector3()).distanceTo(
      joint.getWorldPosition(new THREE.Vector3())) < 1e-7, 'Receiver and joint centres separated');
    const half = node.quaternion.angleTo(new THREE.Quaternion());
    assert.ok(Math.abs(2 * half - joint.quaternion.angleTo(new THREE.Quaternion())) < 1e-6);
    assert.ok(node.quaternion.clone().multiply(node.quaternion).angleTo(joint.quaternion) < 1e-6,
      'Receiver is not on the shortest rotation arc of the completed joint pose');
    const basis = [0,1,2].map(axis => new THREE.Vector3().setFromMatrixColumn(node.matrixWorld, axis));
    assert.ok(basis.every(v => Math.abs(v.length() - 1) < 1e-6), 'Receiver scaled during movement');
    assert.ok(Math.abs(basis[0].dot(basis[1])) < 1e-6, 'Receiver sheared during movement');
  }
}

test('outer receivers follow completed mixed neck/head poses including early action returns', async () => {
  const f = await fixture(); const motion = createEraMotion(f.model, f.nodes, f.rest);
  const poses = [
    { era:'maker', state:'external-control', articulation:{neck:1} },
    { era:'builder', state:'watch', lookTarget:{x:2,z:2} },
    { era:'builder', state:'warning', phase:1, lookTarget:{x:-2,z:2} },
    { era:'builder', state:'contact', phase:1, goal:{x:0,z:motion.metrics().contactApproach.z}, speed:.42 },
    { era:'builder', state:'watch', powerMove:{kind:'thrust',phase:.5} },
    { era:'mechanic', state:'rest' },
  ];
  let largestSkullAngle = 0, largestYaw = 0;
  for (const pose of poses) for (let frame=0;frame<180;frame++) {
    for (const name of names) {
      f.nodes[name].position.copy(f.rest[name].position);
      f.nodes[name].rotation.copy(f.rest[name].rotation);
    }
    motion.tick(1/60, pose);
    checkRigidReceivers(f.model, f.followers);
    largestSkullAngle = Math.max(largestSkullAngle, Math.abs(f.nodes.head.rotation.x));
    largestYaw = Math.max(largestYaw, Math.abs(f.nodes.neck.rotation.y));
  }
  assert.ok(largestSkullAngle > .3, 'Fixture did not exercise large final skull counterrotation');
  assert.ok(largestYaw > .4, 'Fixture did not exercise Maker yaw');
});

test('a receiver with a displaced bearing centre is rejected before animation', async () => {
  const f = await fixture(); f.followers[0].node.position.x += .002;
  assert.throws(() => createCervicalArticulation(f.model, f.nodes, f.rest), /parent and centre/);
});
