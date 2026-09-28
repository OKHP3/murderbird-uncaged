import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { dirname } from 'node:path';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';

const modelPath = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const reportPath = `${process.env.UNCAGED_AUDIT || 'assets/audit/alignment-v3'}/kinematic-alignment.json`;
assert.ok(!reportPath.includes('/neutral-v2/'), 'Alignment diagnostics must not replace neutral-v2 receipts.');
const bytes = await readFile(modelPath), template = await loadRigidValidation(bytes);
const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const output = { generatedAt: new Date().toISOString(), model: modelPath, sha256: createHash('sha256').update(bytes).digest('hex'), scope: 'Deterministic kinematic samples of the actual exported rigid model; no forces, exhaustive collision test, supported grip, human acting approval or publication claim.', sampleStepSeconds: 1 / 60, checks: [] };

function rig() {
  const model = clone(template.scene);
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean));
  const rest = Object.fromEntries(names.map(name => [name, { position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone() }]));
  const motion = createEraMotion(model, nodes, rest);
  const localPositions = new Map();
  for (const side of ['left','right']) {
    for (const suffix of ['shin','foot','toes','digit-1-proximal','digit-1-distal','digit-2-proximal','digit-2-distal','digit-3-proximal','digit-3-distal']) {
      const node = model.getObjectByName(`${side}-${suffix}`);
      assert.ok(node, `Missing rigid joint ${side}-${suffix}`);
      localPositions.set(node, node.position.clone());
    }
  }
  function step(snapshot) {
    for (const name of names) { nodes[name].position.copy(rest[name].position); nodes[name].rotation.copy(rest[name].rotation); }
    motion.tick(1 / 60, snapshot);
    model.updateMatrixWorld(true);
    for (const [node, position] of localPositions) assert.ok(node.position.distanceTo(position) < 1e-9, `Translated fixed pivot ${node.name}`);
    for(const node of [nodes.jaw,nodes.neck,nodes.head,nodes['left-mantle'],nodes['right-mantle'],nodes['left-wing-shield'],nodes['right-wing-shield'],...localPositions.keys()]) {
      const basis=[0,1,2].map(axis=>new THREE.Vector3().setFromMatrixColumn(node.matrixWorld,axis));
      assert.ok(basis.every(vector=>Math.abs(vector.length()-1)<1e-6),`Nonunit rigid world basis at ${node.name}`);
      assert.ok(Math.abs(basis[0].dot(basis[1]))<1e-6&&Math.abs(basis[0].dot(basis[2]))<1e-6&&Math.abs(basis[1].dot(basis[2]))<1e-6,`Sheared rigid world basis at ${node.name}`);
    }
    for (const side of ['left','right']) {
      const shin = model.getObjectByName(`${side}-shin`);
      assert.ok(Math.abs(shin.quaternion.y) < 1e-10 && Math.abs(shin.quaternion.z) < 1e-10, `${side} knee left its transverse hinge axis`);
    }
    return motion.metrics();
  }
  return { model, nodes, rest, motion, step };
}

function check(name, run) {
  try { output.checks.push({ name, status: 'passed', result: run() }); }
  catch (error) { output.checks.push({ name, status: 'failed', error: error.stack }); }
}

check('jaw-sweep-preserves-rigid-world-distances-without-parent-scale-shear', () => {
  const run=rig(),jaw=run.nodes.jaw;let maximumBasisError=0;const samples=[];
  for(let i=0;i<=32;i++) {
    jaw.rotation.x=i/100;run.model.updateMatrixWorld(true);
    const basis=[0,1,2].map(axis=>new THREE.Vector3().setFromMatrixColumn(jaw.matrixWorld,axis));
    const lengths=basis.map(vector=>vector.length()),products=[basis[0].dot(basis[1]),basis[0].dot(basis[2]),basis[1].dot(basis[2])];
    maximumBasisError=Math.max(maximumBasisError,...lengths.map(length=>Math.abs(length-1)),...products.map(Math.abs));
    samples.push({angle:i/100,basisLengths:lengths,basisDotProducts:products});
  }
  assert.ok(maximumBasisError<1e-6,`Articulated jaw has nonrigid world basis error ${maximumBasisError}; bake inherited nonuniform scale into rest geometry.`);
  return {samples,maximumBasisError};
});

check('actual-jaw-tip-opens-downward-about-fixed-transverse-pivot', () => {
  const run = rig(), jaw = run.nodes.jaw, head = run.nodes.head;
  let mesh, vertexIndex, front = -Infinity;
  run.model.updateMatrixWorld(true);
  const vertex = new THREE.Vector3(), headInverse = head.matrixWorld.clone().invert();
  jaw.traverse(object => {
    if (!object.isMesh) return;
    const positions = object.geometry.attributes.position;
    for (let i=0;i<positions.count;i++) {
      vertex.fromBufferAttribute(positions,i).applyMatrix4(object.matrixWorld).applyMatrix4(headInverse);
      if (vertex.z > front) { front=vertex.z; mesh=object; vertexIndex=i; }
    }
  });
  assert.ok(mesh && front > .1, 'Jaw requires an actual anterior mesh vertex.');
  const localVertex = new THREE.Vector3().fromBufferAttribute(mesh.geometry.attributes.position, vertexIndex);
  const point = () => mesh.localToWorld(localVertex.clone()).applyMatrix4(head.matrixWorld.clone().invert());
  const samples = [], closed = point(), pivot = jaw.position.clone();
  let previousY = closed.y;
  for (let i=0;i<=32;i++) {
    jaw.rotation.set(i / 100, 0, 0); run.model.updateMatrixWorld(true);
    const value = point();
    assert.ok(value.y <= previousY + 1e-10, `Opening jaw rises at angle ${i/100}`);
    assert.ok(jaw.position.distanceTo(pivot) < 1e-12);
    previousY=value.y; samples.push({ angle: i/100, vertex: value.toArray() });
  }
  assert.ok(closed.y-previousY > .035, 'Full jaw opening must lower the tracked anterior vertex by at least 35 mm.');
  return { trackedMesh: mesh.name, vertexIndex, closed: closed.toArray(), opened: samples.at(-1), downwardDisplacement: closed.y-previousY, samples, limitation: 'Direction and fixed pivot only; the jaw/cheek bearing overlap and full surface sweep still require visual review.' };
});

check('maker-raised-foot-tucks-digits-and-recovers-with-support-fixed', () => {
  const run = rig(); let peak = null, maxError = 0, minSupport = Infinity;
  const support = new THREE.Vector3(); let supportStart;
  for (let i=0;i<360;i++) {
    const metrics=run.step({ era:'maker', state:'external-control', articulation:{ leg:i<180?1:0 } });
    const right=run.model.getObjectByName('right-foot');right.getWorldPosition(support);
    if (!supportStart) supportStart=support.clone();
    assert.ok(support.distanceTo(supportStart)<1e-8, 'Maker support foot moved while the other foot lifted.');
    minSupport=Math.min(minSupport,metrics.feet[1].groundMin);maxError=Math.max(maxError,metrics.maxFootError);
    if(i===179)peak={ digitAngles:[1,2,3].map(digit=>['proximal','distal'].map(segment=>run.model.getObjectByName(`left-digit-${digit}-${segment}`).rotation.x)), floor:metrics.feet[0].groundMin };
  }
  assert.ok(peak.digitAngles.flat().every(angle=>angle>.05), 'All six lifted digit hinges must articulate.');
  assert.ok(peak.floor>.07, 'Tucked Maker foot lost ground clearance.');
  for(const side of ['left','right'])for(const digit of [1,2,3])for(const segment of ['proximal','distal'])assert.equal(run.model.getObjectByName(`${side}-digit-${digit}-${segment}`).rotation.x,0, 'Planted digit must recover its exact rest rotation.');
  assert.ok(maxError<.002);assert.ok(Math.abs(minSupport-.002)<.002);
  return { peak, maxAnkleError:maxError, minSupportGroundY:minSupport, exactDigitRestored:true };
});

check('bilateral-travel-uses-transverse-knees-and-keeps-support-targets-and-digits-fixed', () => {
  const run=rig(), prior=new Map(), flexed=new Set();let maxError=0,minFloor=Infinity,maxSupportDrift=0,frames=0;
  const legs=[{x:.6,z:.72},{x:-.6,z:-.2},{x:0,z:-.25}];
  for(const goal of legs)for(let frame=0;frame<360;frame++) {
    const metrics=run.step({ era:'builder',state:'pace',goal,speed:.42,phase:0 });frames++;
    maxError=Math.max(maxError,metrics.maxFootError);
    for(const foot of metrics.feet) {
      minFloor=Math.min(minFloor,foot.groundMin);
      const old=prior.get(foot.side);
      if(!foot.swinging&&old&&!old.swinging)maxSupportDrift=Math.max(maxSupportDrift,new THREE.Vector3(...foot.actual).distanceTo(new THREE.Vector3(...old.actual)));
      for(const digit of [1,2,3])for(const segment of ['proximal','distal']) {
        const node=run.model.getObjectByName(`${foot.side}-digit-${digit}-${segment}`);
        if(!foot.swinging)assert.equal(node.rotation.x,0,'Supported digit changed its planted contact geometry.');
        if(node.rotation.x>.05)flexed.add(node.name);
      }
      prior.set(foot.side,foot);
    }
  }
  assert.equal(flexed.size,12,'All twelve digit hinges must flex over bilateral travel.');
  assert.ok(maxError<.002,`Ankle solve error ${maxError} exceeds 2 mm.`);
  assert.ok(maxSupportDrift<.002,`Support drift ${maxSupportDrift} exceeds 2 mm.`);
  assert.ok(minFloor>=-.001,`Digit or foot penetrated floor by ${-minFloor} m.`);
  return { frames, simulatedSeconds:frames/60, maxAnkleError:maxError, maxSupportDrift, minFloor, articulatedDigitHinges:[...flexed] };
});

output.status=output.checks.every(item=>item.status==='passed')?'passed':'failed';
await mkdir(dirname(reportPath),{recursive:true});await writeFile(reportPath,`${JSON.stringify(output,null,2)}\n`);
console.log(`${output.status}: ${output.checks.filter(item=>item.status==='passed').length}/${output.checks.length} kinematic alignment checks`);
for(const item of output.checks.filter(item=>item.status==='failed'))console.error(`${item.name}: ${item.error}`);
if(output.status!=='passed')process.exitCode=1;
