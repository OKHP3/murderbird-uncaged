import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';

const names = ['body', 'neck', 'head', 'jaw', 'power-core', 'processing',
  'right-mantle', 'right-wing-shield'];
const source = await loadRigidValidation(await readFile(
  'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.glb'));

function fixture(socket) {
  const scene = new THREE.Scene();
  const model = clone(source.scene);
  scene.add(model);
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  // Synthetic socket tests the coordinate contract on a real rigid hierarchy;
  // it does not certify a V31 authored surface or mechanism clearance.
  delete nodes.body.userData.mechanismLayoutV1;
  if (socket !== undefined) nodes.jaw.userData.makerControlSocketV1 = socket;
  const rest = Object.fromEntries(names.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  return { scene, model, nodes, rest };
}

test('authored jaw socket follows relocated jaw and transformed ancestors through era switches', () => {
  const point = [-.12, -.02, .07];
  const socket = { schema: 1, coordinateSpace: 'gltf-node-local', point,
    surfaceObject: 'Synthetic control receiver' };
  for (const raw of [socket, JSON.stringify(socket)]) {
    const f = fixture(raw);
    const system = createEraMechanisms(f);
    try {
      f.model.position.set(.43, .21, -.38);
      f.model.rotation.y = .65;
      f.nodes.head.rotation.set(-.12, .23, .05);
      f.nodes.jaw.position.add(new THREE.Vector3(.013, .07, -.018));
      for (const angle of [0, .08, .16, .24, .32, 0]) {
        f.nodes.jaw.rotation.x = angle;
        system.setEra('maker');
        system.tick(0, {}, { actualArticulation: { jaw: angle / .32 } });
        f.scene.updateMatrixWorld(true);
        const expected = f.nodes.jaw.localToWorld(new THREE.Vector3(...point));
        const actual = f.scene.getObjectByName('maker-joint-attachment-jaw')
          .getWorldPosition(new THREE.Vector3());
        assert.ok(actual.distanceTo(expected) < 1e-9, 'Socket stayed at stale world or pivot offset');
        assert.equal(system.metrics().visible.maker, true);
        assert.deepEqual(system.metrics().attachmentLayout.makerOwnerSockets,
          [{ control: 'jaw', owner: 'jaw', point, surfaceObject: socket.surfaceObject }]);
        for (const era of ['mechanic', 'builder']) {
          system.setEra(era);
          assert.equal(system.metrics().visible.maker, false, `${era} exposed Maker controls`);
        }
      }
      assert.deepEqual(socket.point, point, 'Runtime mutated authored coordinates');
    } finally { system.dispose(); }
  }
});

test('historical models without owner sockets retain all five legacy offsets', () => {
  const f = fixture();
  const system = createEraMechanisms(f);
  try {
    assert.deepEqual(system.metrics().attachmentLayout.makerOwnerSockets, []);
    assert.deepEqual(system.metrics().attachmentLayout.makerControlOffsets,
      [[.065, .015, .045], [-.095, -.10, .10], [-.07, 0, -.16], [-.16, .06, .02], [-.18, -.06, .20]]);
  } finally { system.dispose(); }
});

test('declared malformed owner sockets fail before mechanism objects are created', () => {
  for (const socket of ['{', { schema: 1, coordinateSpace: 'world', point: [0, 0, 0], surfaceObject: 'receiver' },
    { schema: 1, coordinateSpace: 'gltf-node-local', point: [0, Infinity, 0], surfaceObject: 'receiver' }]) {
    const f = fixture(socket);
    const before = [];
    f.scene.traverse(o => before.push(o));
    assert.throws(() => createEraMechanisms(f), /Invalid Maker control socket/);
    const after = [];
    f.scene.traverse(o => after.push(o));
    assert.deepEqual(after, before);
  }
});
