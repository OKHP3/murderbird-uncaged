/** Actual exported V25 geometry through the existing controller/motion layer.
 * No procedural era hardware is created. Tail command metrics are not a
 * physical tail test. Discrete sampled kinematics are not collision/physics.
 */
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { dirname, resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';

const args=process.argv.slice(2), option=(key,fallback)=>{const i=args.indexOf(key);return i<0?fallback:args[i+1];};
const modelPath=option('--model','assets/models/whole-character-v25/attempt-form01/murderbird-whole-character-v25.glb');
const outPath=option('--output','assets/audit/whole-character-v25/attempt-form01/motion');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const bytes=await readFile(modelPath),template=await loadRigidValidation(bytes),dt=1/60;
const names=['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield','cervical-mid-a','cervical-mid-b','cervical-upper'];
const report={generatedAt:new Date().toISOString(),model:{path:modelPath,sha256:sha(bytes),bytes:bytes.length},
  method:{loader:'Actual Three GLTFLoader through loadRigidValidation; in-memory texture bindings removed only',
    controllerStepSeconds:dt,geometryMetricSampleIntervalSeconds:.1,additionalSamples:'State changes, action completion and every jump flight frame',
    visibility:'Same exterior era eligibility and authored group gating as presence-exhibit.js; no procedural mechanisms created'},
  checks:[],limits:['Discrete sampled kinematics and attachment math only; no continuous collision, support-force or physics proof.',
    'No procedural Maker cradle/tail, Mechanic transmission or Advanced machinery is loaded.',
    'Bounding-box floor/support checks do not establish stable load support or artistic acceptance.']};
let rawVertices=0,meshCount=0,nodeCount=0;
template.scene.traverse(o=>{nodeCount++;if(o.isMesh){meshCount++;const a=o.geometry.attributes.position;rawVertices+=a.count;assert([...a.array].every(Number.isFinite),`Nonfinite source geometry ${o.name}`);}});
report.loaded={meshCount,nodeCount,positionVertices:rawVertices,physicalTailPresent:Boolean(template.scene.getObjectByName('compact-articulated-tail'))};

function run(era){
  const model=clone(template.scene),nodes=Object.fromEntries(names.filter(n=>model.getObjectByName(n)).map(n=>[n,model.getObjectByName(n)]));
  assert(names.slice(0,15).every(n=>nodes[n]),'Required model nodes absent');
  const rest=Object.fromEntries(Object.entries(nodes).map(([n,o])=>[n,{position:o.position.clone(),rotation:o.rotation.clone()}]));
  const motion=createEraMotion(model,nodes,rest),machine=createEraController({seed:927});
  const originals=[];model.traverse(o=>originals.push({object:o,parent:o.parent,position:o.position.clone(),local:o.matrix.clone(),mesh:o.isMesh}));
  const fixed=originals.filter(r=>!r.mesh&&(r.object.name.startsWith('cervical-')||r.object.name==='neck'||r.object.name==='head'||/^(left|right)-(shin|foot|toes|digit-)/.test(r.object.name)));
  const sums={frames:0,samples:0,stateFrames:{},stateTransitions:[],maxFootSolveErrorM:0,maxSupportTargetDriftM:0,maxSupportActualDriftM:0,
    minGroundY:Infinity,maxPlantedFloorOffsetM:0,maxRigidBasisError:0,maxFixedJointTranslationErrorM:0,maxMeshLocalMatrixDrift:0,
    visibleBounds:{min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]},contacts:[],violations:{},maxRootYaw:0,maxDistance:0,maxSteps:0,visibleMeshCounts:new Set()};
  let previous=new Map(),lastState='',lastMetrics,baseline;
  function violation(id,value,limit){const v=sums.violations[id];if(!v||Math.abs(value)>Math.abs(v.value))sums.violations[id]={value,limit,firstFrame:sums.frames,state:lastState};}
  function visibility(){
    model.traverse(o=>{const e=o.userData?.extras||o.userData||{},tag=e.exteriorEras;if(typeof tag==='string')o.visible=tag.split(',').includes(era);});
    nodes['winding-drive'].visible=false;nodes['power-core'].visible=era==='builder';nodes.processing.visible=era==='builder';nodes['builder-optics'].visible=era==='builder';nodes['industrial-repairs'].visible=era!=='maker';
  }
  function sample(s){
    const m=motion.metrics();lastMetrics=m;sums.samples++;
    const bounds=m.bodyBounds;
    for(let i=0;i<3;i++){sums.visibleBounds.min[i]=Math.min(sums.visibleBounds.min[i],bounds.min.getComponent(i));sums.visibleBounds.max[i]=Math.max(sums.visibleBounds.max[i],bounds.max.getComponent(i));}
    if(bounds.min.y<-.002)violation('visible-model-floor-penetration',bounds.min.y,-.002);
    if(bounds.max.y>2.55)violation('visible-model-ceiling',bounds.max.y,2.55);
    if(bounds.min.x< -2.9||bounds.max.x>2.9)violation('visible-model-cage-x',Math.max(Math.abs(bounds.min.x),Math.abs(bounds.max.x)),2.9);
    if(bounds.min.z< -2.1||bounds.max.z>2.1)violation('visible-model-cage-z',Math.max(Math.abs(bounds.min.z),Math.abs(bounds.max.z)),2.1);
    sums.maxDistance=Math.max(sums.maxDistance,m.distance);sums.maxSteps=Math.max(sums.maxSteps,m.steps);sums.maxRootYaw=Math.max(sums.maxRootYaw,Math.abs(m.root.yaw));
    sums.maxFootSolveErrorM=Math.max(sums.maxFootSolveErrorM,m.maxFootError);
    if(m.maxFootError>.002)violation('ankle-solve-error',m.maxFootError,.002);
    let visibleCount=0;
    model.traverseVisible(o=>{if(o.isMesh)visibleCount++;});sums.visibleMeshCounts.add(visibleCount);
    for(const r of originals){
      const o=r.object;if(o.parent!==r.parent)violation('parent-changed',1,0);
      const e=o.matrixWorld.elements;if(!e.every(Number.isFinite))violation('nonfinite-world-matrix',1,0);
      const c=[0,1,2].map(i=>new THREE.Vector3().setFromMatrixColumn(o.matrixWorld,i));
      const error=Math.max(...c.map(v=>Math.abs(v.length()-1)),Math.abs(c[0].dot(c[1])),Math.abs(c[0].dot(c[2])),Math.abs(c[1].dot(c[2])));
      sums.maxRigidBasisError=Math.max(sums.maxRigidBasisError,error);
      if(error>1e-6)violation('nonrigid-world-basis',error,1e-6);
      if(r.mesh){const drift=Math.max(...o.matrix.elements.map((v,i)=>Math.abs(v-r.local.elements[i])));sums.maxMeshLocalMatrixDrift=Math.max(sums.maxMeshLocalMatrixDrift,drift);if(drift>1e-9)violation('rigid-mesh-local-drift',drift,1e-9);}
    }
    for(const r of fixed){const d=r.object.position.distanceTo(r.position);sums.maxFixedJointTranslationErrorM=Math.max(sums.maxFixedJointTranslationErrorM,d);if(d>1e-9)violation('fixed-joint-translation',d,1e-9);}
    const jumping=m.powerMove?.kind==='jump',claw=m.clawAction?.side;
    for(const f of m.feet){
      sums.minGroundY=Math.min(sums.minGroundY,f.groundMin);
      if(!f.swinging&&!jumping&&f.side!==claw){
        const offset=Math.abs(f.groundMin-.002);sums.maxPlantedFloorOffsetM=Math.max(sums.maxPlantedFloorOffsetM,offset);if(offset>.0015)violation('planted-foot-floor-offset',offset,.0015);
        const old=previous.get(f.side);
        if(old&&!old.swinging&&!old.jumping){
          const targetDrift=Math.hypot(...f.target.map((v,i)=>v-old.target[i])),actualDrift=Math.hypot(...f.actual.map((v,i)=>v-old.actual[i]));
          sums.maxSupportTargetDriftM=Math.max(sums.maxSupportTargetDriftM,targetDrift);sums.maxSupportActualDriftM=Math.max(sums.maxSupportActualDriftM,actualDrift);
          if(targetDrift>1e-7)violation('planted-support-target-drift',targetDrift,1e-7);
          if(actualDrift>.002)violation('planted-support-geometry-drift',actualDrift,.002);
        }
      }
      previous.set(f.side,{...f,jumping});
    }
    if(m.contact){const railX=s.lookTarget?.x??s.goal?.x??m.root.x;const radial=Math.hypot(m.contactPoint[0]-railX,m.contactPoint[2]-2.1);sums.contacts.push({frame:sums.frames,state:s.state,point:m.contactPoint,railX,radial});if(Math.abs(radial-.021)>.008)violation('bill-contact-radius',radial,.021);}
    return m;
  }
  function step(force=false){
    const s=machine.update(dt,motion.feedback());
    for(const n of Object.keys(nodes)){nodes[n].position.copy(rest[n].position);nodes[n].rotation.copy(rest[n].rotation);}
    motion.tick(dt,s);model.updateMatrixWorld(true);sums.frames++;
    const changed=s.state!==lastState;if(changed){sums.stateTransitions.push({frame:sums.frames,state:s.state});lastState=s.state;}
    sums.stateFrames[s.state]=(sums.stateFrames[s.state]||0)+1;
    const m=force||changed||sums.frames%6===0||s.powerMove?.kind==='jump'?sample(s):null;
    return {state:s,metrics:m};
  }
  function advance(seconds){for(let i=0;i<Math.ceil(seconds/dt);i++)step();return sample(machine.getSnapshot());}
  function until(predicate,seconds=16){for(let i=0;i<Math.ceil(seconds/dt);i++){const f=step();if(predicate(f.state,f.metrics)){return sample(f.state);}}throw new Error(`Requested state not reached in ${seconds}s; last=${machine.getSnapshot().state}`);}
  function capture(){model.updateMatrixWorld(true);return originals.map(r=>r.object.matrix.elements.slice());}
  function resetCheck(){machine.reset();motion.resetEra(era);previous.clear();step(true);const now=capture();let max=0;for(let j=0;j<now.length;j++)for(let i=0;i<16;i++)max=Math.max(max,Math.abs(now[j][i]-baseline[j][i]));return {maxLocalMatrixDelta:max,exactWithin1e8:max<1e-8};}
  machine.setEra(era);motion.resetEra(era);visibility();step(true);baseline=capture();
  return {model,nodes,rest,motion,machine,sums,step,sample,advance,until,resetCheck,violation};
}

async function check(name,era,fn){
  const r=run(era);let result={},error;
  try{result=fn(r)||{};}catch(e){error=e.message;r.violation('scenario-incomplete',1,0);}
  const reset=r.resetCheck();if(!reset.exactWithin1e8)r.violation('era-reset-matrix-drift',reset.maxLocalMatrixDelta,1e-8);
  const s={...r.sums,visibleMeshCounts:[...r.sums.visibleMeshCounts]};
  report.checks.push({name,era,status:Object.keys(s.violations).length?'FAIL':'PASS',...(error?{error}:{}),metrics:s,result,reset});
  console.log(`${name}: ${report.checks.at(-1).status}`);
}

for(const id of ['leg','wing','tail','neck','jaw'])await check(`maker-${id}`,'maker',r=>{
  const before={jaw:r.nodes.jaw.rotation.x,wing:r.nodes['right-mantle'].rotation.x,neck:r.nodes.neck.rotation.y,foot:r.motion.metrics().feet.map(f=>f.actual)};
  assert(r.machine.setArticulation(id,1));const m=r.advance(1.8),command=m.actualArticulation[id];
  assert(command>.99,`${id} command did not reach the motion layer`);
  const result={commandMetric:command,root:m.root,footHeights:m.feet.map(f=>f.groundMin),jawAngle:r.nodes.jaw.rotation.x,wingAngle:r.nodes['right-mantle'].rotation.x,neckYaw:r.nodes.neck.rotation.y};
  if(id==='leg')assert(m.feet[0].actual[1]-m.feet[1].actual[1]>.14,'Physical foot lift absent');
  if(id==='wing')assert(Math.abs(r.nodes['right-mantle'].rotation.x-before.wing)>.1,'Physical mantle rotation absent');
  if(id==='neck')assert(Math.abs(r.nodes.neck.rotation.y-before.neck)>.4,'Physical neck yaw absent');
  if(id==='jaw')assert(r.nodes.jaw.rotation.x-before.jaw>.3,'Physical jaw opening absent');
  if(id==='tail')result.physicalMotion={status:'NOT TESTED',reason:'V25 GLB has no compact-articulated-tail; physical tail belongs to excluded createEraMechanisms assembly.'};
  r.machine.setArticulation(id,0);r.advance(1.8);return result;
});

await check('mechanic-stepped-traversal-and-turns','mechanic',r=>{
  assert(r.machine.requestRoutine());const stages=new Set();let maxYaw=0,maxSpeed=0,stationary=0;
  for(let i=0;i<48*60;i++){const f=r.step();if(f.metrics){stages.add(f.metrics.mechanicalStage);maxYaw=Math.max(maxYaw,Math.abs(f.metrics.root.yaw));maxSpeed=Math.max(maxSpeed,f.metrics.root.speed);if(f.metrics.root.speed<.001)stationary++;}}
  const m=r.sample(r.machine.getSnapshot());assert(m.distance>.8&&m.steps>=4&&maxYaw>1,'Route did not produce substantial stepping and turns');
  for(const s of ['load','release','settle','dwell'])assert(stages.has(s),`Missing cam phase ${s}`);
  r.machine.stopRoutine();r.until((s,m)=>s.state==='mechanical-ready'&&m?.settled,8);
  return {distanceM:m.distance,steps:m.steps,maxYawRad:maxYaw,maxSpeedMps:maxSpeed,camStages:[...stages],stationaryMetricSamples:stationary};
});

for(const x of [0,.6])await check(`advanced-attention-strike-contact-recovery-${x}`,'builder',r=>{
  assert(r.machine.requestReach({x,y:.25}));let greatestYaw=0,contactFrames=0;
  r.until((s,m)=>{if(m){greatestYaw=Math.max(greatestYaw,Math.abs(r.nodes.neck.rotation.y));if(s.state==='contact'&&m.contact)contactFrames++;}return s.state==='recover';},18);
  r.advance(1.1);assert(contactFrames>0,'Controller entered contact without actual bill/rail triangle contact');
  return {physicalContactSamples:contactFrames,maxAttentionNeckYawRad:greatestYaw,contactApproach:r.motion.metrics().contactApproach};
});

for(const kind of ['jump','thrust'])await check(`advanced-${kind}`,'builder',r=>{
  assert(r.machine.requestPowerMove(kind));let peakHeight=0,peakFeet=null,peakRight=0,peakLeft=0,started=false;
  r.until((s,m)=>{if(m?.powerMove?.kind===kind){started=true;if(m.powerMove.height>peakHeight){peakHeight=m.powerMove.height;peakFeet=m.feet.map(f=>f.groundMin);}peakRight=Math.max(peakRight,Math.abs(r.nodes['right-mantle'].rotation.x),Math.abs(r.nodes['right-wing-shield'].rotation.x));peakLeft=Math.max(peakLeft,Math.abs(r.nodes['left-mantle'].rotation.x),Math.abs(r.nodes['left-wing-shield'].rotation.x));return m.powerMove.phase>=1;}return false;},7);
  assert(started,'Power action never started');const m=r.sample(r.machine.getSnapshot());
  if(kind==='jump')assert(peakHeight>=.34&&peakFeet.every(y=>y>.15),'Actual feet were not airborne at jump peak');
  else assert(peakRight>.5&&peakLeft<peakRight,'Shield thrust did not exercise the intended asymmetric rig');
  assert(m.feet.every(f=>Math.abs(f.groundMin-.002)<.002),'Power move failed to return both foot surfaces to floor');
  return {peakHeightM:peakHeight,peakFeetGroundMin:peakFeet,peakRightWingRotationRad:peakRight,peakLeftWingRotationRad:peakLeft,finishedFeetGroundMin:m.feet.map(f=>f.groundMin)};
});

report.status=report.checks.some(c=>c.status==='FAIL')?'FAIL':'PASS WITH EXCLUDED PROCEDURAL TAIL';
report.summary={passed:report.checks.filter(c=>c.status==='PASS').length,failed:report.checks.filter(c=>c.status==='FAIL').length,
  physicalTail:'NOT TESTED',proceduralHardware:'NOT TESTED',continuousCollision:'NOT TESTED'};
assert.equal(sha(await readFile(modelPath)),report.model.sha256,'Validation modified the native GLB');
await mkdir(outPath,{recursive:true});
const sources=[fileURLToPath(import.meta.url),'scripts/load-rigid-validation.mjs','src/scene/era-motion.js','src/scene/era-controller.js','src/scene/cervical-articulation.js','src/scene/rigid-leg-kinematics.js','src/scene/presence-state.js'];
report.executedSources=[];
for(const p of sources){const source=await readFile(p),dest=resolve(outPath,`executed-${basename(p)}`);await copyFile(p,dest);report.executedSources.push({source:p,path:dest,sha256:sha(source)});}
await writeFile(resolve(outPath,'motion-validation.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.summary));if(report.summary.failed)process.exitCode=1;
