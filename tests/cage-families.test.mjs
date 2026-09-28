import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { createEraMotion } from '../src/scene/era-motion.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';

const NODE_NAMES = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];

async function actualRig() {
  const path = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
  const template = await loadRigidValidation(await readFile(path));
  const model = clone(template.scene);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), `missing runtime nodes in ${path}`);
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, { position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone() }]));
  return createEraMotion(model, nodes, rest);
}

function contactIntervals(samples) {
  const intervals = [];
  let start = null;
  for (const sample of samples) {
    if (sample.contact && start === null) start = sample.phase;
    if (!sample.contact && start !== null) {
      intervals.push({ start, end: sample.phase });
      start = null;
    }
  }
  if (start !== null) intervals.push({ start, end: samples.at(-1).phase });
  return intervals;
}

async function sampleFamily(family) {
  const motion = await actualRig();
  const approachZ = motion.metrics().contactApproach.z;
  let arrived = false;
  for (let frame = 0; frame < 600; frame += 1) {
    motion.tick(1 / 60, { era:'builder', state:'pace', goal:{ x:0, z:approachZ }, speed:.6,
      heading:0, lookTarget:{ x:0, y:1.2, z:2.1 }, phase:0, agitation:.5 });
    const metrics = motion.metrics();
    if (metrics.arrived && metrics.settled && metrics.aligned) { arrived = true; break; }
  }
  assert.ok(arrived, 'the actual rig reaches a settled rail approach before the sampled action');
  // Let any foot that is still within the runtime's settle tolerance finish
  // planting before measuring the family's support targets.
  for (let frame = 0; frame < 120; frame += 1) {
    motion.tick(1 / 60, { era:'builder', state:'watch', goal:null, speed:0,
      heading:0, lookTarget:{ x:0, y:1.2, z:2.1 }, phase:0, agitation:.5 });
  }
  const initial = motion.metrics();
  const anchors = initial.feet.map(foot => [...foot.target]);
  const goal = { x:initial.root.x, z:initial.root.z };
  const samples = [];
  for (let frame = 0; frame < 120; frame += 1) {
    const phase = (frame + 1) / 120;
    motion.tick(1 / 60, { era:'builder', state:'cage-test', goal, speed:0,
      heading:0, lookTarget:{ x:0, y:1.2, z:2.1 }, phase, actionFamily:family,
      actionKind:'cage', agitation:.5 });
    const metrics = motion.metrics();
    assert.equal(metrics.cageAction?.family, family);
    assert.ok(Math.abs(metrics.cageAction.phase - phase) < 1e-9);
    samples.push({ phase, contact:metrics.cageAction.contact, extension:metrics.pose.extension,
      load:metrics.pose.load, envelope:metrics.cageAction.envelope, feet:metrics.feet });
  }
  for (const sample of samples) {
    for (let index = 0; index < anchors.length; index += 1) {
      const drift = Math.hypot(...sample.feet[index].target.map((value, axis) => value - anchors[index][axis]));
      assert.ok(drift < 1e-8, `${family} moved planted ${sample.feet[index].side} target by ${drift}`);
      assert.equal(sample.feet[index].swinging, false, `${family} lifted a support foot`);
      assert.ok(sample.feet[index].groundMin >= -.003 && sample.feet[index].groundMin <= .01,
        `${family} support foot left the floor: ${sample.feet[index].groundMin}`);
    }
  }
  return { samples, intervals:contactIntervals(samples) };
}

test('actual exported rig gives edge tap, sustained rail press, and separated seam probes distinct contact timing', async () => {
  const edge = await sampleFamily('edge-probe');
  const press = await sampleFamily('rail-press');
  const seam = await sampleFamily('seam-rattle');

  assert.equal(edge.intervals.length, 1, 'edge-probe makes one brief contact');
  assert.equal(press.intervals.length, 1, 'rail-press makes one sustained contact');
  assert.ok((press.intervals[0].end - press.intervals[0].start) >
    (edge.intervals[0].end - edge.intervals[0].start) * 1.5,
  'rail-press holds the actual bill contact substantially longer than an edge tap');
  assert.ok(seam.intervals.length >= 2, 'seam-rattle produces multiple separated actual probe contacts');
  for (let index = 1; index < seam.intervals.length; index += 1) {
    assert.ok(seam.intervals[index].start - seam.intervals[index - 1].end > .08,
      'seam probes visibly release between contacts');
  }
  assert.ok(Math.max(...edge.samples.map(item => item.extension)) > .9);
  assert.ok(Math.max(...press.samples.map(item => item.load)) > Math.max(...edge.samples.map(item => item.load)) * 1.5,
    'rail-press carries a distinct sustained body-load envelope');
});

test('actual rail contact treats accumulated full-turn headings as equivalent to zero', async () => {
  const targets = [0, 2 * Math.PI, -2 * Math.PI];
  const results = [];
  for (const target of targets) {
    const motion = await actualRig();
    const frames = Math.ceil(Math.abs(target) / .1);
    for (let index = 1; index <= frames; index += 1) {
      const heading = target * index / frames;
      for (let frame = 0; frame < 6; frame += 1) {
        motion.tick(1 / 60, { era:'builder', state:'pace', goal:null, speed:0,
          heading, lookTarget:{ x:0, y:1.2, z:2.1 }, phase:0, agitation:.5 });
      }
    }
    const yawBeforeApproach = motion.metrics().root.yaw;
    assert.ok(Math.abs(yawBeforeApproach - target) < .08,
      `rig accumulated heading ${yawBeforeApproach} instead of ${target}`);
    const approachZ = motion.metrics().contactApproach.z;
    let arrived = false;
    for (let frame = 0; frame < 900; frame += 1) {
      motion.tick(1 / 60, { era:'builder', state:'pace', goal:{ x:0, z:approachZ }, speed:.6,
        heading:target, lookTarget:{ x:0, y:1.2, z:2.1 }, phase:0, agitation:.5 });
      const metrics = motion.metrics();
      if (metrics.arrived && metrics.settled && metrics.aligned) { arrived = true; break; }
    }
    assert.ok(arrived, `rig reaches the same settled rail approach at heading ${target}`);
    const root = motion.metrics().root;
    let contactSamples = 0;
    let minimumContactRadius = Infinity;
    for (let frame = 0; frame < 120; frame += 1) {
      const phase = (frame + 1) / 120;
      motion.tick(1 / 60, { era:'builder', state:'cage-test', goal:{ x:root.x, z:root.z }, speed:0,
        heading:target, lookTarget:{ x:0, y:1.2, z:2.1 }, phase, actionFamily:'rail-press',
        actionKind:'cage', agitation:.5 });
      const metrics = motion.metrics();
      if (metrics.cageAction?.contact) {
        contactSamples += 1;
        const radius = Math.hypot(metrics.contactPoint[0], metrics.contactPoint[2] - 2.1);
        minimumContactRadius = Math.min(minimumContactRadius, radius);
      }
    }
    assert.ok(contactSamples > 0, `actual bill/rail contact occurs at heading ${target}`);
    assert.ok(minimumContactRadius >= .013 && minimumContactRadius <= .029,
      `contact remains within the existing physical radius at heading ${target}: ${minimumContactRadius}`);
    results.push({ target, yawBeforeApproach, contactSamples, minimumContactRadius });
  }
  assert.ok(results.every(result => result.contactSamples > 0));
});
