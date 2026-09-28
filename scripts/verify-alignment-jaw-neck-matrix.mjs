import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

const MODEL_PATH = process.env.UNCAGED_MODEL;
const OUT = process.env.UNCAGED_AUDIT;
const EXPECTED_SHA256 = process.env.UNCAGED_MODEL_SHA256;
assert.ok(MODEL_PATH && OUT && /^[a-f0-9]{64}$/.test(EXPECTED_SHA256 || ''), 'Provide UNCAGED_MODEL, UNCAGED_AUDIT and UNCAGED_MODEL_SHA256.');
await mkdir(OUT, {recursive:true});
const NODE_NAMES = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const sourcePaths = [
  'scripts/load-rigid-validation.mjs',
  'src/scene/era-motion.js',
  'src/scene/era-controller.js',
  'src/scene/presence-state.js',
];
const sourceHashes = Object.fromEntries(await Promise.all(sourcePaths.map(async file => [file, hash(await readFile(file))])));
const modelBytes = await readFile(MODEL_PATH);
assert.equal(hash(modelBytes), EXPECTED_SHA256, 'Frozen model identity changed.');
const template = await loadRigidValidation(modelBytes);
assert.ok(template.scene, 'GLB has no scene.');
const diagnosticScriptBytes = await readFile(new URL(import.meta.url));
const diagnosticScriptSha256 = hash(diagnosticScriptBytes);
await writeFile(path.join(OUT, 'executed-jaw-neck-matrix.mjs.txt'), diagnosticScriptBytes, {flag:'wx'});
const PLANE_TOLERANCE_METRES = 1e-6;
const BARYCENTRIC_INTERIOR_TOLERANCE = 1e-4;

function createRig(seed = 927) {
  const model = clone(template.scene);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'Model is missing a required motion node.');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, { position:nodes[name].position.clone(), rotation:nodes[name].rotation.clone() }]));
  const motion = createEraMotion(model, nodes, rest);
  const machine = createEraController({ seed });
  let era = 'builder';
  function step(dt = 1/60) {
    const state = machine.update(dt, motion.feedback());
    if (state.era !== era) { era = state.era; motion.resetEra(era); }
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(dt, state);
    return { state, metrics:motion.metrics() };
  }
  return { model, nodes, motion, machine, step };
}

// Return only the mesh triangles owned under jaw and directly/indirectly under
// neck while excluding the complete head subtree. Both sets are expressed in
// neck-local coordinates so every recorded check uses the actual solved pose.
const matrix = new THREE.Matrix4();
const point = new THREE.Vector3();
function triangles(mesh, neckInverse) {
  const result = [], positions = mesh.geometry.attributes.position, index = mesh.geometry.index;
  matrix.multiplyMatrices(neckInverse, mesh.matrixWorld);
  const count = index ? index.count : positions.count;
  for (let i=0; i<count; i+=3) {
    const vertices = [0,1,2].map(j => new THREE.Vector3().fromBufferAttribute(positions, index ? index.getX(i+j) : i+j).applyMatrix4(matrix));
    if (new THREE.Triangle(...vertices).getArea() < 1e-12) continue;
    result.push({ vertices, box:new THREE.Box3().setFromPoints(vertices), name:mesh.name, meshId:mesh.uuid, index:i/3 });
  }
  return result;
}
const CELL = .025;
function keys(box) {
  const result=[];
  for(let x=Math.floor(box.min.x/CELL);x<=Math.floor(box.max.x/CELL);x++)
    for(let y=Math.floor(box.min.y/CELL);y<=Math.floor(box.max.y/CELL);y++)
      for(let z=Math.floor(box.min.z/CELL);z<=Math.floor(box.max.z/CELL);z++) result.push(`${x},${y},${z}`);
  return result;
}
function barycentric(p, tri) {
  const [a,b,c]=tri.vertices, v0=b.clone().sub(a), v1=c.clone().sub(a), v2=p.clone().sub(a);
  const d00=v0.dot(v0),d01=v0.dot(v1),d11=v1.dot(v1),d20=v2.dot(v0),d21=v2.dot(v1);
  const denominator=d00*d11-d01*d01;
  if(Math.abs(denominator)<1e-20)return null;
  const v=(d11*d20-d01*d21)/denominator,w=(d00*d21-d01*d20)/denominator;
  return [1-v-w,v,w];
}
function insideBarycentric(p, tri, tolerance=0) {
  const values=barycentric(p,tri);
  return values&&values.every(value=>value>=-tolerance&&value<=1+tolerance);
}
function interiorBarycentric(p, tri) {
  const values=barycentric(p,tri);
  return values&&values.every(value=>value>BARYCENTRIC_INTERIOR_TOLERANCE&&value<1-BARYCENTRIC_INTERIOR_TOLERANCE);
}
function plane(tri) {
  const normal=tri.vertices[1].clone().sub(tri.vertices[0]).cross(tri.vertices[2].clone().sub(tri.vertices[0]));
  const length=normal.length();
  return length<1e-12?null:{normal:normal.divideScalar(length),origin:tri.vertices[0]};
}
function classifyTrianglePair(first, second) {
  const near=[], proper=[];
  for(const [from,to] of [[first,second],[second,first]]) {
    const targetPlane=plane(to);if(!targetPlane)continue;
    const distances=from.vertices.map(vertex=>vertex.clone().sub(targetPlane.origin).dot(targetPlane.normal));
    if(distances.every(distance=>Math.abs(distance)<=PLANE_TOLERANCE_METRES)) {
      near.push({kind:'coplanar',point:from.vertices[0]});
      continue;
    }
    for(let i=0;i<3;i++) {
      const da=distances[i],db=distances[(i+1)%3];
      const a=from.vertices[i],b=from.vertices[(i+1)%3];
      if(Math.abs(da)<=PLANE_TOLERANCE_METRES&&insideBarycentric(a,to,1e-8)) near.push({kind:'grazing',point:a.clone()});
      if(Math.abs(db)<=PLANE_TOLERANCE_METRES&&insideBarycentric(b,to,1e-8)) near.push({kind:'grazing',point:b.clone()});
      // Strict crossing requires edge endpoints on opposite sides by more
      // than the plane tolerance and the interpolated hit in the target's
      // barycentric interior, excluding edge/vertex grazing.
      if(!((da>PLANE_TOLERANCE_METRES&&db< -PLANE_TOLERANCE_METRES)||(db>PLANE_TOLERANCE_METRES&&da< -PLANE_TOLERANCE_METRES)))continue;
      const t=da/(da-db),hit=a.clone().lerp(b,t);
      if(interiorBarycentric(hit,to))proper.push(hit);
      else if(insideBarycentric(hit,to,1e-8))near.push({kind:'grazing',point:hit});
    }
  }
  if(proper.length)return{classification:'proper-crossing',points:deduplicate(proper)};
  if(near.some(hit=>hit.kind==='coplanar'))return{classification:'coplanar-overlap-candidate',points:deduplicate(near.filter(hit=>hit.kind==='coplanar').map(hit=>hit.point))};
  if(near.length)return{classification:'grazing-or-boundary',points:deduplicate(near.map(hit=>hit.point))};
  return{classification:'separated-or-nonintersecting',points:[]};
}
function deduplicate(points) {
  const output=[];for(const candidate of points)if(!output.some(existing=>existing.distanceTo(candidate)<1e-7))output.push(candidate.clone());return output;
}
function runKernelFixtures() {
  const tri=(a,b,c)=>({vertices:[new THREE.Vector3(...a),new THREE.Vector3(...b),new THREE.Vector3(...c)]});
  const target=tri([0,0,0],[1,0,0],[0,1,0]);
  const fixtures=[
    ['crossing',target,tri([.2,.2,-.2],[.2,.2,.2],[.65,.2,.2]),'proper-crossing'],
    ['separated',target,tri([.2,.2,.1],[.65,.2,.1],[.2,.65,.1]),'separated-or-nonintersecting'],
    ['grazing',target,tri([.25,.25,0],[.6,.2,.2],[.2,.6,.2]),'grazing-or-boundary'],
    ['coplanar',target,tri([.2,.2,0],[.6,.2,0],[.2,.6,0]),'coplanar-overlap-candidate'],
  ].map(([name,a,b,expected])=>{const actual=classifyTrianglePair(a,b);assert.equal(actual.classification,expected,`Kernel fixture ${name} failed`);return{name,expected,actual:actual.classification,points:actual.points.map(point=>point.toArray())};});
  return{toleranceMetres:PLANE_TOLERANCE_METRES,barycentricInteriorTolerance:BARYCENTRIC_INTERIOR_TOLERANCE,fixtures};
}
function owners(model, jaw, neck, neckInverse) {
  const fixedMeshes=[];
  neck.traverse(object=>{
    if(!object.isMesh)return;
    for(let owner=object;owner;owner=owner.parent) if(owner===jaw) return;
    let underHead=false;
    for(let owner=object;owner;owner=owner.parent) if(owner===model.getObjectByName('head')) { underHead=true; break; }
    if(!underHead)fixedMeshes.push(object);
  });
  const movingMeshes=[];
  jaw.traverse(object=>{if(object.isMesh)movingMeshes.push(object);});
  assert.ok(fixedMeshes.length>0,'No neck-owned meshes remained after excluding head descendants.');
  assert.ok(movingMeshes.length>0,'Jaw has no moving meshes.');
  return { fixedMeshes, movingMeshes };
}
const KERNEL_FIXTURES=runKernelFixtures();
function evaluate(rig, label, state, metrics) {
  rig.model.updateMatrixWorld(true);
  const { jaw, neck, head }=rig.nodes;
  const neckInverse=neck.matrixWorld.clone().invert();
  const {fixedMeshes,movingMeshes}=owners(rig.model,jaw,neck,neckInverse);
  const fixed=fixedMeshes.flatMap(mesh=>triangles(mesh,neckInverse));
  const moving=movingMeshes.flatMap(mesh=>triangles(mesh,neckInverse));
  assert.ok(fixed.length > 0 && moving.length > 0, 'Nonempty jaw and neck triangle inventories are required.');
  const grid=new Map();
  fixed.forEach((tri,i)=>{for(const key of keys(tri.box)){if(!grid.has(key))grid.set(key,[]);grid.get(key).push(i);}});
  const meshPairs=[];
  for(const jawMesh of movingMeshes)for(const neckMesh of fixedMeshes) {
    const jawTriangles=moving.filter(tri=>tri.meshId===jawMesh.uuid),neckTriangles=fixed.filter(tri=>tri.meshId===neckMesh.uuid);
    const counts={jawMesh:jawMesh.name,neckMesh:neckMesh.name,jawTriangles:jawTriangles.length,neckTriangles:neckTriangles.length,possiblePairs:jawTriangles.length*neckTriangles.length,aabbGridCandidates:0,aabbOverlapPairs:0,properCrossingPairs:0,grazingPairs:0,coplanarOverlapCandidates:0,separatedOrNonintersectingPairs:0,examples:[]};
    for(const tri of jawTriangles) {
      const candidates=new Set(keys(tri.box).flatMap(key=>grid.get(key)||[]));
      for(const id of candidates) {
        const other=fixed[id];if(other.meshId!==neckMesh.uuid)continue;
        counts.aabbGridCandidates++;
        if(!tri.box.intersectsBox(other.box))continue;
        counts.aabbOverlapPairs++;
        const result=classifyTrianglePair(tri,other);
        const key={ 'proper-crossing':'properCrossingPairs','grazing-or-boundary':'grazingPairs','coplanar-overlap-candidate':'coplanarOverlapCandidates','separated-or-nonintersecting':'separatedOrNonintersectingPairs' }[result.classification];
        counts[key]++;
        if(result.points.length&&counts.examples.length<8)counts.examples.push({classification:result.classification,jawTriangle:tri.index,neckTriangle:other.index,pointsNeckLocal:result.points.slice(0,4).map(p=>p.toArray())});
      }
    }
    meshPairs.push(counts);
  }
  const totals=meshPairs.reduce((sum,pair)=>{for(const key of ['possiblePairs','aabbGridCandidates','aabbOverlapPairs','properCrossingPairs','grazingPairs','coplanarOverlapCandidates','separatedOrNonintersectingPairs'])sum[key]+=pair[key];return sum;},{possiblePairs:0,aabbGridCandidates:0,aabbOverlapPairs:0,properCrossingPairs:0,grazingPairs:0,coplanarOverlapCandidates:0,separatedOrNonintersectingPairs:0});
  const pose={
    era:state.era,state:state.state,phase:state.phase,actionKind:state.actionKind??null,
    goal:state.goal??null,heading:state.heading??null,lookTarget:state.lookTarget??null,
    contact:metrics.contact,root:metrics.root,
    bodyPosition:rig.nodes.body.position.toArray(),bodyRotation:rig.nodes.body.rotation.toArray(),
    neckPosition:neck.position.toArray(),neckRotation:neck.rotation.toArray(),neckWorld:neck.getWorldPosition(new THREE.Vector3()).toArray(),
    headPosition:head.position.toArray(),headRotation:head.rotation.toArray(),
    jawPosition:jaw.position.toArray(),jawRotation:jaw.rotation.toArray(),
    cervical:metrics.cervical,contactPoint:metrics.contactPoint,actualArticulation:metrics.actualArticulation??null,feet:(metrics.feet||[]).map(foot=>({side:foot.side,target:foot.target,actual:foot.actual,groundMin:foot.groundMin,phase:foot.phase,steps:foot.steps})),mechanicalStage:metrics.mechanicalStage??null,mechanicalPhase:metrics.mechanicalPhase??null,
  };
  return { label, pose, geometry:{jawMeshes:movingMeshes.map(m=>m.name),neckOwnedMeshes:fixedMeshes.map(m=>m.name),jawTriangles:moving.length,neckTriangles:fixed.length}, result:{kernel:KERNEL_FIXTURES,totals,meshPairs}, scope:'Strict sampled surface-crossing candidates in this exact reachable pose only. Proper crossing requires edge endpoints to straddle the target plane by more than 1e-6 m and the interpolated hit to lie inside the target triangle by 1e-4 barycentric margin. This detects no penetration volume or force; it may omit real crossings whose segment endpoints only hit target-triangle boundaries, as well as coplanar, contained, or unsampled cases.' };
}

const runs=[];
function advance(rig, seconds, dt=1/60) { let last; for(let t=0;t<seconds-1e-9;t+=dt) last=rig.step(Math.min(dt,seconds-t)); return last; }
function add(rig,label,frame) { runs.push(evaluate(rig,label,frame.state,frame.metrics)); }

// Maker: individually actuate each relevant neck/jaw lever to its minimum
// and maximum through setArticulation; no hand-authored joint transforms.
for (const channel of ['neck','jaw']) for (const value of [0,1]) {
  const rig=createRig(927); rig.machine.setEra('maker');
  assert.equal(rig.machine.setArticulation(channel,value),true,`Maker rejected ${channel}=${value}`);
  let frame; for(let i=0;i<60;i++) frame=rig.step(1/60);
  add(rig,`maker-${channel}-${value?'maximum':'minimum'}`,frame);
}

// Mechanic: select the moving frame with the greatest measured vertical
// support-target displacement during an actual requestRoutine, then replay
// the deterministic controller to that exact tick before evaluating meshes.
{
  const rig=createRig(927); rig.machine.setEra('mechanic'); advance(rig,.2);
  assert.equal(rig.machine.requestRoutine(),true,'Mechanic routine rejected');
  let chosenIndex=-1,best=-Infinity,chosenSummary=null;
  for(let i=0;i<60*8;i++) {
    const frame=rig.step(1/60);
    const supportTarget=Math.max(0,...(frame.metrics.feet||[]).map(foot=>Math.abs(foot.target?.[1]||0)));
    if(frame.state.state==='mechanical-run'&&frame.metrics.steps>0&&frame.metrics.root?.speed>0&&supportTarget>=best){
      best=supportTarget;chosenIndex=i;
      chosenSummary={state:frame.state.state,phase:frame.state.phase,mechanicalStage:frame.metrics.mechanicalStage,
        mechanicalPhase:frame.metrics.mechanicalPhase,root:{...frame.metrics.root},
        neckPosition:rig.nodes.neck.position.toArray(),neckRotation:rig.nodes.neck.rotation.toArray(),
        headPosition:rig.nodes.head.position.toArray(),headRotation:rig.nodes.head.rotation.toArray(),
        jawPosition:rig.nodes.jaw.position.toArray(),jawRotation:rig.nodes.jaw.rotation.toArray()};
    }
  }
  assert.ok(chosenIndex>=0,'Mechanic moving/support-target sample was not reached');
  const replay=createRig(927);replay.machine.setEra('mechanic');advance(replay,.2);
  assert.equal(replay.machine.requestRoutine(),true,'Mechanic replay routine rejected');
  let replayFrame;
  for(let i=0;i<=chosenIndex;i++)replayFrame=replay.step(1/60);
  const replaySummary={state:replayFrame.state.state,phase:replayFrame.state.phase,mechanicalStage:replayFrame.metrics.mechanicalStage,
    mechanicalPhase:replayFrame.metrics.mechanicalPhase,root:{...replayFrame.metrics.root},
    neckPosition:replay.nodes.neck.position.toArray(),neckRotation:replay.nodes.neck.rotation.toArray(),
    headPosition:replay.nodes.head.position.toArray(),headRotation:replay.nodes.head.rotation.toArray(),
    jawPosition:replay.nodes.jaw.position.toArray(),jawRotation:replay.nodes.jaw.rotation.toArray()};
  assert.deepEqual(replaySummary,chosenSummary,'Mechanic replay diverged from the selected actual controller pose');
  add(replay,'mechanic-routine-moving-support-target-sample',replayFrame);
  runs[runs.length-1].pose.sampleTick=chosenIndex;
  runs[runs.length-1].pose.supportTargetDisplacementMetres=best;
  runs[runs.length-1].pose.deterministicReplayVerified=true;
}

// Advanced: capture visitor contact and the resulting recovery from a real
// rail request; then capture seeded autonomous gaze extrema in a separate run.
{
  const rig=createRig(927);
  assert.equal(rig.machine.requestReach({x:0}),true,'Advanced rail request rejected');
  let contact=null;
  for(let i=0;i<60*20;i++){const frame=rig.step(1/60);if(frame.state.state==='contact'&&frame.metrics.contact){contact=frame;break;}}
  assert.ok(contact,'Advanced contact state not reached'); add(rig,'advanced-visitor-contact-center-rail',contact);
  let recover=null;
  for(let i=0;i<60*6;i++){const frame=rig.step(1/60);if(frame.state.state==='recover'){recover=frame;break;}}
  assert.ok(recover,'Advanced recovery state not reached'); add(rig,'advanced-contact-recovery',recover);
}
{
  const rig=createRig(927); let pitchIndex=-1,yawIndex=-1,maxPitchValue=-1,maxYawValue=-1;
  for(let i=0;i<60*120;i++){
    const frame=rig.step(1/60), s=frame.state;
    if(s.actionKind==='visitor'||s.state==='contact'||s.state==='strike')continue;
    const pitch=Math.abs(rig.nodes.neck.rotation.x), yaw=Math.abs(rig.nodes.neck.rotation.y);
    if(pitch>maxPitchValue){maxPitchValue=pitch;pitchIndex=i;}
    if(yaw>maxYawValue){maxYawValue=yaw;yawIndex=i;}
  }
  assert.ok(pitchIndex>=0&&yawIndex>=0,'Seeded Advanced gaze extrema not observed');
  // Replay the deterministic seeded controller so evaluate() receives the
  // actual rig transforms at each captured index, not the final loop pose.
  for(const [index,label] of [[pitchIndex,'advanced-seeded-gaze-pitch-extreme'],[yawIndex,'advanced-seeded-gaze-yaw-extreme']]){
    const sampleRig=createRig(927); let frame;
    for(let i=0;i<=index;i++)frame=sampleRig.step(1/60);
    add(sampleRig,label,frame);
  }
}

const output={
  generatedAt:new Date().toISOString(),
  model:{path:MODEL_PATH,sha256:hash(modelBytes),bytes:modelBytes.byteLength,expectedSha256:EXPECTED_SHA256},
  worktree:{head:execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),path:process.cwd()},
  sources:sourceHashes,diagnosticScriptSha256,
  diagnostic:'Corrected reachable-state matrix for strict jaw/neck surface crossings across Maker, Mechanic, and Advanced. Maker endpoints use setArticulation; Mechanic moving/support-target sample is selected from a live requestRoutine and replayed at its exact tick; Advanced samples are actual visitor contact/recovery plus seeded autonomous gaze extrema. No force inference or exhaustive sweep claim.',
  kernel:{planeToleranceMetres:PLANE_TOLERANCE_METRES,barycentricInteriorTolerance:BARYCENTRIC_INTERIOR_TOLERANCE,fixtures:KERNEL_FIXTURES},
  meshInventoryAudit:{perPose:runs.map(run=>({label:run.label,...run.geometry})),excludedHeadDescendants:true,coordinates:'mesh triangle vertices transformed by inverse actual neck.matrixWorld times each mesh.matrixWorld'},
  limits:['Sampled reachable states only; not an exhaustive control or animation sweep.','Counts are strict triangle edge-plane crossing pairs, not penetration depths, volumes, forces, or collision response.','Strict interior barycentric margin can omit boundary intersections; coplanar, contained, and unsampled cases are not ruled out.','A zero broadphase count is evidence only for these mesh pairs at these sampled poses.'],runs,
};
const reportPath=path.join(OUT,'jaw-neck-era-matrix.json');
await writeFile(reportPath,`${JSON.stringify(output,null,2)}\n`,{flag:'wx'});
if(runs.some(run=>run.result.totals.properCrossingPairs>0)) process.exitCode=1;
console.log(JSON.stringify({reportPath,model:output.model,sources:output.sources,runs:runs.map(run=>({label:run.label,era:run.pose.era,state:run.pose.state,phase:run.pose.phase,neckPosition:run.pose.neckPosition,neckRotation:run.pose.neckRotation,jawRotation:run.pose.jawRotation,triangles:run.geometry,totals:run.result.totals}))},null,2));
