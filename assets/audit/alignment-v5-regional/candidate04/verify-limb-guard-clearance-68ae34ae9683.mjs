import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

// Discrete armor-to-armor surface-crossing diagnostic. This deliberately tests
// only plate-role meshes (including primitive wrappers) owned by adjacent thigh/shin and shin/foot
// pivot nodes. It does not infer forces, volume penetration, or continuous
// clearance from the sampled poses.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const MODEL_PATH = process.env.UNCAGED_MODEL;
assert.ok(MODEL_PATH && process.env.UNCAGED_AUDIT, 'Provide UNCAGED_MODEL and UNCAGED_AUDIT.');
const AUDIT_DIR = path.resolve(process.env.UNCAGED_AUDIT);
const NODE_NAMES = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
const PLANE_TOLERANCE_METRES = 1e-6;
const BARYCENTRIC_INTERIOR_TOLERANCE = 1e-4;
const GRID_CELL_METRES = .025;
const hash = value => createHash('sha256').update(value).digest('hex');
await mkdir(AUDIT_DIR,{recursive:true});
const diagnosticSourceBytes=await readFile(fileURLToPath(import.meta.url));
const diagnosticSourceSha256=hash(diagnosticSourceBytes);
const diagnosticSourcePath=path.join(AUDIT_DIR,`verify-limb-guard-clearance-${diagnosticSourceSha256.slice(0,12)}.mjs`);
await writeFile(diagnosticSourcePath,diagnosticSourceBytes,{flag:'wx'});
assert.equal(hash(await readFile(diagnosticSourcePath)),diagnosticSourceSha256,'Archived diagnostic source snapshot failed hash verification.');
const modelBytes = await readFile(MODEL_PATH);
const modelSha256 = hash(modelBytes);
assert.equal(modelSha256, process.env.UNCAGED_MODEL_SHA256, 'Provide exact UNCAGED_MODEL_SHA256; frozen model changed.');
const gltf=JSON.parse(modelBytes.subarray(20,20+modelBytes.readUInt32LE(12)).toString('utf8'));
const rigidPivotNames=new Set(gltf.nodes.filter(node=>node.mesh===undefined&&node.name).map(node=>node.name));
const template = await loadRigidValidation(modelBytes);
assert.ok(template.scene, 'Model has no scene.');

function createRig(seed=927) {
  const model=clone(template.scene);
  const names=[...NODE_NAMES,'left-thigh','left-shin','left-foot','right-thigh','right-shin','right-foot'];
  const nodes=Object.fromEntries(names.map(name=>[name,model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean),'Model is missing required scene or limb pivot nodes.');
  const rest=Object.fromEntries(names.map(name=>[name,{position:nodes[name].position.clone(),rotation:nodes[name].rotation.clone()}]));
  const motion=createEraMotion(model,nodes,rest),machine=createEraController({seed});
  let era='builder';
  function step(dt=1/60) {
    const state=machine.update(dt,motion.feedback());
    if(state.era!==era){era=state.era;motion.resetEra(era);}
    for(const name of names){nodes[name].position.copy(rest[name].position);nodes[name].rotation.copy(rest[name].rotation);}
    motion.tick(dt,state);model.updateMatrixWorld(true);
    return{state,metrics:motion.metrics()};
  }
  return{model,nodes,rest,motion,machine,step};
}

function barycentric(point,triangle) {
  const [a,b,c]=triangle.vertices,v0=b.clone().sub(a),v1=c.clone().sub(a),v2=point.clone().sub(a);
  const d00=v0.dot(v0),d01=v0.dot(v1),d11=v1.dot(v1),d20=v2.dot(v0),d21=v2.dot(v1),den=d00*d11-d01*d01;
  if(Math.abs(den)<1e-20)return null;
  const v=(d11*d20-d01*d21)/den,w=(d00*d21-d01*d20)/den;return[1-v-w,v,w];
}
function inside(point,triangle,tolerance=0){const q=barycentric(point,triangle);return q&&q.every(v=>v>=-tolerance&&v<=1+tolerance);}
function interior(point,triangle){const q=barycentric(point,triangle);return q&&q.every(v=>v>BARYCENTRIC_INTERIOR_TOLERANCE&&v<1-BARYCENTRIC_INTERIOR_TOLERANCE);}
function plane(triangle){const n=triangle.vertices[1].clone().sub(triangle.vertices[0]).cross(triangle.vertices[2].clone().sub(triangle.vertices[0]));const l=n.length();return l<1e-12?null:{n:n.divideScalar(l),origin:triangle.vertices[0]};}
function dedupe(points){const out=[];for(const p of points)if(!out.some(q=>q.distanceTo(p)<1e-7))out.push(p.clone());return out;}
function classify(first,second){
  const hits=[],proper=[];
  for(const [from,to] of [[first,second],[second,first]]){
    const p=plane(to);if(!p)continue;
    const d=from.vertices.map(v=>v.clone().sub(p.origin).dot(p.n));
    if(d.every(x=>Math.abs(x)<=PLANE_TOLERANCE_METRES)){hits.push({kind:'coplanar',point:from.vertices[0]});continue;}
    for(let i=0;i<3;i++){
      const da=d[i],db=d[(i+1)%3],a=from.vertices[i],b=from.vertices[(i+1)%3];
      if(Math.abs(da)<=PLANE_TOLERANCE_METRES&&inside(a,to,1e-8))hits.push({kind:'grazing',point:a});
      if(!((da>PLANE_TOLERANCE_METRES&&db< -PLANE_TOLERANCE_METRES)||(db>PLANE_TOLERANCE_METRES&&da< -PLANE_TOLERANCE_METRES)))continue;
      const hit=a.clone().lerp(b,da/(da-db));
      if(interior(hit,to))proper.push(hit);else if(inside(hit,to,1e-8))hits.push({kind:'grazing',point:hit});
    }
  }
  if(proper.length)return{kind:'proper-crossing',points:dedupe(proper)};
  if(hits.some(h=>h.kind==='coplanar'))return{kind:'coplanar-overlap-candidate',points:dedupe(hits.filter(h=>h.kind==='coplanar').map(h=>h.point))};
  if(hits.length)return{kind:'grazing-or-boundary',points:dedupe(hits.map(h=>h.point))};
  return{kind:'separated-or-nonintersecting',points:[]};
}
function verifyFixtures(){
  const tri=(a,b,c)=>({vertices:[new THREE.Vector3(...a),new THREE.Vector3(...b),new THREE.Vector3(...c)]});
  const target=tri([0,0,0],[1,0,0],[0,1,0]);
  const fixtures=[
    ['crossing',target,tri([.2,.2,-.2],[.2,.2,.2],[.65,.2,.2]),'proper-crossing'],
    ['separated',target,tri([.2,.2,.1],[.65,.2,.1],[.2,.65,.1]),'separated-or-nonintersecting'],
    ['grazing',target,tri([.25,.25,0],[.6,.2,.2],[.2,.6,.2]),'grazing-or-boundary'],
    ['coplanar',target,tri([.2,.2,0],[.6,.2,0],[.2,.6,0]),'coplanar-overlap-candidate'],
  ].map(([name,a,b,expected])=>{const got=classify(a,b).kind;assert.equal(got,expected,`Kernel fixture ${name} failed`);return{name,expected,actual:got};});
  return{planeToleranceMetres:PLANE_TOLERANCE_METRES,barycentricInteriorTolerance:BARYCENTRIC_INTERIOR_TOLERANCE,fixtures};
}
const KERNEL_FIXTURES=verifyFixtures();

const effectiveTags=new WeakMap();
function plateMeshes(owner) {
  const selected=[];
  function visit(object,inherited={}) {
    if(rigidPivotNames.has(object.name)) return;
    const tags={...inherited,...object.userData};
    if(object.isMesh&&tags.surfaceRole==='plate'&&['leg','foot'].includes(tags.region)) {selected.push(object);effectiveTags.set(object,tags);}
    for(const child of object.children) visit(child,tags);
  }
  for(const child of owner.children) visit(child);
  return selected;
}
// A multi-primitive wrapper must contribute every plate primitive while a
// nested rigid joint must retain ownership of its own geometry.
{
  const owner=new THREE.Object3D(),direct=new THREE.Mesh(),wrapper=new THREE.Group();
  direct.userData={surfaceRole:'plate',region:'leg'};wrapper.userData={surfaceRole:'plate',region:'leg'};
  const primitive=new THREE.Mesh(),nestedPivot=new THREE.Object3D(),nestedPlate=new THREE.Mesh();
  nestedPivot.name='left-shin';nestedPlate.userData={surfaceRole:'plate',region:'leg'};
  assert.ok(rigidPivotNames.has(nestedPivot.name),'Missing expected rigid boundary for selector fixture');
  wrapper.add(primitive);nestedPivot.add(nestedPlate);owner.add(direct,wrapper,nestedPivot);
  assert.deepEqual(plateMeshes(owner),[direct,primitive],'Plate selector omitted wrapped geometry or crossed rigid ownership');
} 
const REGION_PAIRS=[
  {joint:'left-knee',owners:['left-thigh','left-shin']},
  {joint:'left-ankle',owners:['left-shin','left-foot']},
  {joint:'right-knee',owners:['right-thigh','right-shin']},
  {joint:'right-ankle',owners:['right-shin','right-foot']},
];
function triangleList(mesh,inverseOwner){
  const pos=mesh.geometry.attributes.position,index=mesh.geometry.index,out=[],toOwner=new THREE.Matrix4().multiplyMatrices(inverseOwner,mesh.matrixWorld);
  for(let i=0;i<(index?index.count:pos.count);i+=3){
    const vertices=[0,1,2].map(j=>new THREE.Vector3().fromBufferAttribute(pos,index?index.getX(i+j):i+j).applyMatrix4(toOwner));
    if(new THREE.Triangle(...vertices).getArea()<1e-12)continue;
    out.push({vertices,box:new THREE.Box3().setFromPoints(vertices),mesh:mesh.name,meshId:mesh.uuid,triangle:i/3});
  }
  return out;
}
function cellKeys(box){const out=[];for(let x=Math.floor(box.min.x/GRID_CELL_METRES);x<=Math.floor(box.max.x/GRID_CELL_METRES);x++)for(let y=Math.floor(box.min.y/GRID_CELL_METRES);y<=Math.floor(box.max.y/GRID_CELL_METRES);y++)for(let z=Math.floor(box.min.z/GRID_CELL_METRES);z<=Math.floor(box.max.z/GRID_CELL_METRES);z++)out.push(`${x},${y},${z}`);return out;}
function evaluate(rig,label,frame,tick,setup){
  rig.model.updateMatrixWorld(true);
  const groups=[];
  for(const pair of REGION_PAIRS){
    const [aName,bName]=pair.owners,[a,b]=[rig.nodes[aName],rig.nodes[bName]];
    const aMeshes=plateMeshes(a),bMeshes=plateMeshes(b);
    assert.ok(aMeshes.length&&bMeshes.length,`${pair.joint} has no direct-owner armor plate pair.`);
    const commonInverse=a.matrixWorld.clone().invert();
    const aTriangles=aMeshes.flatMap(mesh=>triangleList(mesh,commonInverse));
    const bTriangles=bMeshes.flatMap(mesh=>triangleList(mesh,commonInverse));
    assert.ok(aTriangles.length&&bTriangles.length,`${pair.joint} plate geometry is empty.`);
    const grid=new Map();bTriangles.forEach((triangle,id)=>cellKeys(triangle.box).forEach(key=>{if(!grid.has(key))grid.set(key,[]);grid.get(key).push(id);}));
    const meshes=[];
    for(const am of aMeshes)for(const bm of bMeshes){
      const ta=aTriangles.filter(t=>t.meshId===am.uuid),tb=bTriangles.filter(t=>t.meshId===bm.uuid);
      const counts={meshA:am.name,ownerA:aName,roleA:effectiveTags.get(am).surfaceRole,meshB:bm.name,ownerB:bName,roleB:effectiveTags.get(bm).surfaceRole,trianglesA:ta.length,trianglesB:tb.length,possiblePairs:ta.length*tb.length,gridCandidates:0,aabbOverlaps:0,properCrossingPairs:0,grazingPairs:0,coplanarOverlapCandidates:0,examples:[]};
      const targetIds=new Set(tb.map(t=>`${t.meshId}:${t.triangle}`));
      for(const x of ta){const candidates=new Set(cellKeys(x.box).flatMap(key=>grid.get(key)||[]));for(const id of candidates){const y=bTriangles[id];if(!targetIds.has(`${y.meshId}:${y.triangle}`))continue;counts.gridCandidates++;if(!x.box.intersectsBox(y.box))continue;counts.aabbOverlaps++;const result=classify(x,y);if(result.kind==='proper-crossing')counts.properCrossingPairs++;else if(result.kind==='grazing-or-boundary')counts.grazingPairs++;else if(result.kind==='coplanar-overlap-candidate')counts.coplanarOverlapCandidates++;if(result.points.length&&counts.examples.length<8)counts.examples.push({kind:result.kind,triangleA:x.triangle,triangleB:y.triangle,pointsOwnerA:result.points.slice(0,4).map(p=>p.toArray())});}}
      meshes.push(counts);
    }
    groups.push({joint:pair.joint,ownerA:{name:aName,parent:a.parent.name,localPosition:a.position.toArray(),localRotation:a.rotation.toArray()},ownerB:{name:bName,parent:b.parent.name,localPosition:b.position.toArray(),localRotation:b.rotation.toArray()},coordinateSpace:'each mesh transformed into ownerA local space after matrixWorld update',includedRoles:['plate'],excludedRoles:['bearing','frame'],sameOwnerPairsTested:false,meshPairs:meshes,totals:meshes.reduce((sum,m)=>{for(const k of ['possiblePairs','gridCandidates','aabbOverlaps','properCrossingPairs','grazingPairs','coplanarOverlapCandidates'])sum[k]+=m[k];return sum;},{possiblePairs:0,gridCandidates:0,aabbOverlaps:0,properCrossingPairs:0,grazingPairs:0,coplanarOverlapCandidates:0})});
  }
  return{label,setup,tick,controller:{era:frame.state.era,state:frame.state.state,phase:frame.state.phase,actionKind:frame.state.actionKind??null,goal:frame.state.goal??null,powerMove:frame.state.powerMove??null,clawAction:frame.state.clawAction??null,mechanicalStage:frame.metrics.mechanicalStage??null,mechanicalPhase:frame.metrics.mechanicalPhase??null,root:frame.metrics.root,steps:frame.metrics.steps},motionMetrics:{powerMove:frame.metrics.powerMove??null,clawAction:frame.metrics.clawAction??null,contact:frame.metrics.contact,settled:frame.metrics.settled},nodes:Object.fromEntries(['left-thigh','left-shin','left-foot','right-thigh','right-shin','right-foot'].map(name=>[name,{localPosition:rig.nodes[name].position.toArray(),localRotation:rig.nodes[name].rotation.toArray(),worldPosition:rig.nodes[name].getWorldPosition(new THREE.Vector3()).toArray()}])),feet:(frame.metrics.feet||[]).map(f=>({side:f.side,target:f.target,actual:f.actual,swinging:f.swinging,phase:f.phase,groundMin:f.groundMin})),clawMetrics:frame.metrics.clawAction,groups};
}
function advance(rig,ticks){let frame;for(let i=0;i<ticks;i++)frame=rig.step(1/60);return frame;}
function replay(setup,index){
  const rig=createRig(927);let initialTicks=0;
  if(setup==='maker-leg-maximum'){rig.machine.setEra('maker');assert.equal(rig.machine.setArticulation('leg',1),true);}
  if(setup==='mechanic-routine-raised-step'){rig.machine.setEra('mechanic');advance(rig,12);assert.equal(rig.machine.requestRoutine(),true);initialTicks=0;}
  if(setup.startsWith('advanced-jump-')){advance(rig,1);assert.equal(rig.machine.requestPowerMove('jump'),true);initialTicks=0;}
  if(setup.startsWith('advanced-claw-')){const first=rig.step();assert.equal(first.state.canClawAction,true,'Builder was not settled and ready for claw action');assert.equal(rig.machine.requestClawAction(),true);initialTicks=0;}
  const frame=advance(rig,index+1);
  return{rig,frame};
}
function closeNumber(a,b){return Math.abs(a-b)<1e-10;}
function pickAndReplay(setup,label,prepare,eligible,score){
  const scan=createRig(927),prepared=prepare(scan);let chosenIndex=-1,best=-Infinity,summary=null;
  for(let i=0;i<prepared.maxTicks;i++){
    const frame=scan.step(1/60);if(!eligible(frame))continue;const value=score(frame);if(value>=best){best=value;chosenIndex=i;summary={state:frame.state.state,phase:frame.state.phase,root:{...frame.metrics.root},feet:(frame.metrics.feet||[]).map(f=>({target:f.target,actual:f.actual,phase:f.phase,groundMin:f.groundMin})),pose:['left-thigh','left-shin','left-foot','right-thigh','right-shin','right-foot'].map(n=>[scan.nodes[n].position.toArray(),scan.nodes[n].rotation.toArray()])};}}
  assert.ok(chosenIndex>=0,`${label} was not reached by controller`);
  const {rig,frame}=replay(setup,chosenIndex);
  const replaySummary={state:frame.state.state,phase:frame.state.phase,root:{...frame.metrics.root},feet:(frame.metrics.feet||[]).map(f=>({target:f.target,actual:f.actual,phase:f.phase,groundMin:f.groundMin})),pose:['left-thigh','left-shin','left-foot','right-thigh','right-shin','right-foot'].map(n=>[rig.nodes[n].position.toArray(),rig.nodes[n].rotation.toArray()])};
  assert.deepEqual(replaySummary,summary,`${label} deterministic replay mismatch`);
  return evaluate(rig,label,frame,chosenIndex,setup);
}

const samples=[];
{
  const rig=createRig(927),frame=rig.step();samples.push(evaluate(rig,'loaded-neutral-rest',frame,0,'initial builder state'));
}
{
  const run=pickAndReplay('maker-leg-maximum','maker-leg-maximum',rig=>{rig.machine.setEra('maker');assert.equal(rig.machine.setArticulation('leg',1),true);return{maxTicks:90};},f=>f.state.era==='maker'&&f.state.state==='puppet-articulation',f=>f.metrics.actualArticulation?.leg||0);samples.push(run);
}
{
  const run=pickAndReplay('mechanic-routine-raised-step','mechanic-raised-step',rig=>{rig.machine.setEra('mechanic');advance(rig,12);assert.equal(rig.machine.requestRoutine(),true);return{maxTicks:60*14};},f=>f.state.era==='mechanic'&&f.state.state==='mechanical-run'&&f.metrics.steps>0&&(f.metrics.feet||[]).some(x=>x.swinging),f=>Math.max(0,...(f.metrics.feet||[]).filter(x=>x.swinging).map(x=>x.target[1])));samples.push(run);
}
for(const [label,wanted] of [['advanced-jump-airborne','airborne'],['advanced-jump-landed','landed']]){
  const run=pickAndReplay('advanced-jump-'+wanted,label,rig=>{advance(rig,1);assert.equal(rig.machine.requestPowerMove('jump'),true);return{maxTicks:60*9};},f=>wanted==='airborne'?f.metrics.powerMove?.kind==='jump'&&f.metrics.powerMove.height>0.02:f.state.era==='builder'&&!f.metrics.powerMove&&f.metrics.settled===true&&(f.metrics.feet||[]).every(x=>Math.abs(x.groundMin-.002)<.002),f=>wanted==='airborne'?f.metrics.powerMove.height:-f.state.phase);samples.push(run);
}
for(const [label,wanted] of [['advanced-claw-contact','contact'],['advanced-claw-recovery','recovery']]){
  const run=pickAndReplay('advanced-claw-'+wanted,label,rig=>{const first=rig.step();assert.equal(first.state.canClawAction,true,'Builder not ready to claw');assert.equal(rig.machine.requestClawAction(),true);return{maxTicks:60*6};},f=>f.state.clawAction?.stage===wanted&&(wanted!=='contact'||f.metrics.clawAction?.contact===true),f=>f.state.clawAction.phase);samples.push(run);
}

const output={generatedAt:new Date().toISOString(),model:{path:MODEL_PATH,sha256:modelSha256,bytes:modelBytes.byteLength},diagnosticSource:{path:diagnosticSourcePath,sha256:diagnosticSourceSha256,bytes:diagnosticSourceBytes.byteLength,archivedBeforeExecution:true},controllerSourceHashes:Object.fromEntries(await Promise.all(['src/scene/era-motion.js','src/scene/era-controller.js','src/scene/presence-state.js','scripts/load-rigid-validation.mjs'].map(async p=>[p,hash(await readFile(path.resolve(HERE,'../',p)))]))),kernel:{planeToleranceMetres:PLANE_TOLERANCE_METRES,barycentricInteriorTolerance:BARYCENTRIC_INTERIOR_TOLERANCE,gridCellMetres:GRID_CELL_METRES,fixtures:KERNEL_FIXTURES},ownerSelection:{method:'Mesh descendants, including primitive wrappers, whose inherited extras surfaceRole=plate and region is leg/foot; traversal stops at every native rigid node',owners:REGION_PAIRS.map(p=>p.owners),pairs:REGION_PAIRS.map(p=>p.joint),excludedRoles:['bearing','frame'],sameOwnerOverlapTested:false},diagnostic:'Strict discrete armor-plate surface-crossing candidates across neighboring rigid knee (thigh/shin) and ankle (shin/foot) owners. Includes loaded rest, actual Maker leg max, a real Mechanic raised step, Advanced jump airborne/settled landing, and actual claw contact/recovery. Selected poses are replayed from seeded controller setup and asserted against state/phase/root/foot/pivot snapshots before geometry evaluation.',limits:['Only plate-role meshes owned by the two adjacent pivot nodes are tested, including grouped primitives and stopping at child rigid nodes. Bearing and frame roles are deliberately excluded; this is not a full limb collision audit.','Samples are actual controller-reachable states; no exhaustive or continuous sweep is implied.','Proper crossings require strict edge-plane endpoint separation above 1e-6 m and an interior barycentric hit margin of 1e-4. Boundary, coplanar, contained, volume, forces, and response behavior are not certified.','Pair counts are mesh-triangle pairs and may count adjacent tessellation triangles separately.'],samples};
const outputPath=path.join(AUDIT_DIR,`limb-guard-clearance-${modelSha256.slice(0,12)}.json`);await writeFile(outputPath,`${JSON.stringify(output,null,2)}\n`,{flag:'wx'});console.log(JSON.stringify({outputPath,diagnosticSource:output.diagnosticSource,model:output.model,samples:samples.map(s=>({label:s.label,state:s.controller.state,tick:s.tick,groups:s.groups.map(g=>({joint:g.joint,owners:[g.ownerA.name,g.ownerB.name],total:g.totals}))}))},null,2));

if(samples.some(sample=>sample.groups.some(group=>group.totals.properCrossingPairs>0))) process.exitCode=1;
