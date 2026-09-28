import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { solveTransverseLeg } from '../src/scene/rigid-leg-kinematics.js';

const upper = new THREE.Vector3(.04401037, -.28021789, .16397882);
const lower = new THREE.Vector3(-.00043702, -.25095776, -.11507958);

function endpoint(u, l, solved) {
  return u.clone().add(l.clone().applyQuaternion(solved.kneeQuaternion)).applyQuaternion(solved.hipQuaternion);
}

test('transverse knee reaches bilateral varied targets with fixed links and a single axis', () => {
  for (const side of [-1, 1]) {
    const u = upper.clone(), l = lower.clone(); u.x *= side; l.x *= side;
    for (const target of [new THREE.Vector3(.04 * side, -.46, .03), new THREE.Vector3(-.03 * side, -.3, .13), new THREE.Vector3(.10 * side, -.49, -.12)]) {
      const solved = solveTransverseLeg(u, l, target);
      assert.equal(solved.clamped, false);
      assert.ok(endpoint(u, l, solved).distanceTo(target) < 1e-9);
      assert.equal(solved.kneeQuaternion.y, 0);
      assert.equal(solved.kneeQuaternion.z, 0);
      assert.ok(Math.abs(u.clone().applyQuaternion(solved.hipQuaternion).length() - u.length()) < 1e-12);
      assert.ok(Math.abs(l.clone().applyQuaternion(solved.kneeQuaternion).length() - l.length()) < 1e-12);
    }
  }
});

test('unreachable and singular target requests remain finite and report the reach clamp', () => {
  for (const target of [new THREE.Vector3(), new THREE.Vector3(0, 0, 2), new THREE.Vector3(0, 0, -.3)]) {
    const solved = solveTransverseLeg(upper, lower, target);
    assert.ok([...solved.hipQuaternion.toArray(), ...solved.kneeQuaternion.toArray()].every(Number.isFinite));
    const actual = endpoint(upper, lower, solved);
    assert.ok(actual.length() <= solved.maximumReach + 1e-9);
    assert.ok(actual.length() >= solved.minimumReach - 1e-9);
    if (target.length() === 0 || target.length() === 2) assert.equal(solved.clamped, true);
    else assert.ok(actual.distanceTo(target) < 1e-9);
  }
});
