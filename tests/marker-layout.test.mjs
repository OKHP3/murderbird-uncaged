import test from 'node:test';
import assert from 'node:assert/strict';
import { layoutMarkers } from '../src/scene/marker-layout.js';

test('projected labels stay anchored while naturally separated', () => {
  const result = layoutMarkers([
    { id: 'bill', x: 30, y: 40 },
    { id: 'foot', x: 150, y: 120 },
  ], 320, 450);
  assert.deepEqual(result.map(({ id, x, y }) => ({ id, x, y })), [
    { id: 'bill', x: 30, y: 40 },
    { id: 'foot', x: 150, y: 120 },
  ]);
  assert.ok(result.every(marker => marker.leaderLength === 0));
});

test('overlapping projected labels receive bounded, separated positions and leaders', () => {
  const result = layoutMarkers([
    { id: 'bill', x: 160, y: 220 },
    { id: 'shoulder', x: 161, y: 220 },
    { id: 'heart', x: 159, y: 221 },
    { id: 'mind', x: 160, y: 219 },
    { id: 'ankle', x: 162, y: 220 },
  ], 320, 450);
  assert.equal(result.length, 5);
  for (const marker of result) {
    assert.ok(marker.x >= 24 && marker.x <= 296);
    assert.ok(marker.y >= 24 && marker.y <= 426);
    assert.ok(marker.leaderLength > 0);
    assert.ok(Number.isFinite(marker.leaderAngle));
  }
  for (let index = 0; index < result.length; index += 1) {
    for (const other of result.slice(index + 1)) {
      assert.ok(Math.abs(result[index].x - other.x) >= 48 || Math.abs(result[index].y - other.y) >= 48);
    }
  }
});

test('hidden or invalid projections are omitted without changing keyboard button ownership', () => {
  const result = layoutMarkers([
    { id: 'visible', x: 20, y: 20 },
    { id: 'hidden', x: 30, y: 30, visible: false },
    { id: 'invalid', x: Number.NaN, y: 40 },
  ], 320, 450);
  assert.deepEqual(result.map(marker => marker.id), ['visible']);
});
