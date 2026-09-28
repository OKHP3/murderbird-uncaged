import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMotion } from '../src/scene/era-motion.js';

const modelPath = process.env.UNCAGED_MODEL || 'assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb';
const auditDir = process.env.UNCAGED_AUDIT || 'assets/audit/alignment-v4';
const reportPath = resolve(auditDir, 'claw-contact-v4.json');
const NODE_NAMES = [
  'body','neck','head','jaw','breastplate','cranial-cover','winding-drive',
  'power-core','processing','industrial-repairs','builder-optics','left-mantle',
  'right-mantle','left-wing-shield','right-wing-shield',
];
const PHASES = ['approach','lift','contact','scrape','release','recovery'];
const INTERRUPTS = ['inspection','reduced-motion','pause','era-change','reset'];
// Screening tolerances allow small mesh/solver margins while catching visible
// floor penetration, a lost planted support, and a one-frame pose discontinuity.
// They are not contact-force, balance, or anatomical acceptance thresholds.
const LIMITS = {
  maxSingleFrameAnkleTravelAt60Hz: .025,
  maxSupportAnkleDrift: .002,
  minimumDistalFloor: -.008,
  minimumSupportFootFloor: -.003,
  maximumSupportFootFloor: .010,
  contactPlaneY: .002,
  contactTipTolerance: .003,
  pivotLocalDrift: 1e-8,
  rigidBasisError: 1e-6,
  neutralAnkleReturn: .015,
};

const bytes = await readFile(modelPath);
const template = await loadRigidValidation(bytes);
const output = {
  generatedAt: new Date().toISOString(),
  model: modelPath,
  sha256: createHash('sha256').update(bytes).digest('hex'),
  scope: 'Deterministic exported-rig claw-cycle samples at 60/120 Hz and bounded state interruptions. This is kinematic floor/support evidence only; it does not establish force, grip, balance, anatomy, full swept collision clearance, or human motion acceptance.',
  thresholds: LIMITS,
  checks: [],
};

function check(name, run) {
  try {
    const result=run();
    const violations=result?.violations||[];
    output.checks.push({name,status:violations.length?'failed':'passed',result,
      ...(violations.length?{error:`${violations.length} measured threshold violation(s)`}:{})});
  }
  catch (error) { output.checks.push({ name, status: 'failed', error: error.stack || error.message }); }
}

function createRun(dt) {
  const model = clone(template.scene);
  const scene = new THREE.Scene(); scene.add(model);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'V4 GLB is missing a required motion node');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
  }]));
  const motion = createEraMotion(model, nodes, rest);
  const controller = createEraController({ seed: 927 });
  const hinges = [];
  for (const side of ['left','right']) {
    for (const name of [
      `${side}-shin`,`${side}-foot`,`${side}-toes`,
      ...[1,2,3].flatMap(digit => [`${side}-digit-${digit}-proximal`, `${side}-digit-${digit}-distal`]),
    ]) {
      const node = model.getObjectByName(name);
      assert.ok(node, `Missing rigid joint ${name}`);
      hinges.push({ node, position: node.position.clone(), rotation: node.rotation.clone() });
    }
  }
  const feet = Object.fromEntries(['left','right'].map(side => {
    const foot = model.getObjectByName(`${side}-foot`);
    const digits = [1,2,3].flatMap(digit => ['proximal','distal'].map(segment =>
      model.getObjectByName(`${side}-digit-${digit}-${segment}`)));
    return [side,{foot,digits}];
  }));
  model.updateMatrixWorld(true);
  const anklePosition = side => feet[side].foot.getWorldPosition(new THREE.Vector3());
  const baseline = { left: anklePosition('left'), right: anklePosition('right') };
  const distalNodes = side => [1,2,3].map(d => model.getObjectByName(`${side}-digit-${d}-distal`));
  const distalMinY = side => Math.min(...distalNodes(side).map(node =>
    new THREE.Box3().setFromObject(node, true).min.y));
  const footMinY = side => new THREE.Box3().setFromObject(feet[side].foot, true).min.y;

  let elapsed=0, state=controller.getSnapshot(), previous={left:anklePosition('left'),right:anklePosition('right')};
  let maxFrameTravel=0, maxSupportDrift=0, maxPivotDrift=0, maxBasisError=0;
  let exemptNextFrameJump=false;
  let minimumDistalFloor=Infinity, maximumSupportFloor=-Infinity, maximumContactTipFloor=-Infinity;
  let peakContactToeAngles=[];
  const violations=new Map();
  const stagesSeen=new Set(), stageTransitions=[], trajectory=[];
  let priorStage=null, sampleTime=-Infinity;
  function recordViolation(key,severity,details){
    const prior=violations.get(key);
    if(!prior||severity>prior.severity)violations.set(key,{key,severity,...details});
  }

  function step() {
    state=controller.update(dt,motion.feedback());
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(dt,state);
    model.updateMatrixWorld(true);
    elapsed+=dt;
    const metrics=motion.metrics();
    for(const item of hinges){
      maxPivotDrift=Math.max(maxPivotDrift,item.node.position.distanceTo(item.position));
      const basis=[0,1,2].map(axis=>new THREE.Vector3().setFromMatrixColumn(item.node.matrixWorld,axis));
      const error=Math.max(...basis.map(axis=>Math.abs(axis.length()-1)),
        Math.abs(basis[0].dot(basis[1])),Math.abs(basis[0].dot(basis[2])),Math.abs(basis[1].dot(basis[2])));
      maxBasisError=Math.max(maxBasisError,error);
    }
    assert.ok(nodes.neck.position.distanceTo(rest.neck.position)<LIMITS.pivotLocalDrift,'Neck joint translated');
    assert.ok(nodes.head.position.distanceTo(rest.head.position)<LIMITS.pivotLocalDrift,'Skull joint translated');
    const points={left:anklePosition('left'),right:anklePosition('right')};
    const frameTravelLimit=LIMITS.maxSingleFrameAnkleTravelAt60Hz*dt*60;
    for(const side of ['left','right']){
      const frameTravel=points[side].distanceTo(previous[side]);
      if(!exemptNextFrameJump)maxFrameTravel=Math.max(maxFrameTravel,frameTravel);
      previous[side]=points[side].clone();
      const min=distalMinY(side); minimumDistalFloor=Math.min(minimumDistalFloor,min);
      if(min<LIMITS.minimumDistalFloor)recordViolation(`distal-floor-${side}`,
        LIMITS.minimumDistalFloor-min,{measuredY:min,limitY:LIMITS.minimumDistalFloor,
          stage:metrics.clawAction?.stage||'neutral',phase:metrics.clawAction?.phase??null,
          timeSeconds:Number(elapsed.toFixed(4)),motionTipMinY:metrics.clawAction?.tipMinY??null});
      if(!exemptNextFrameJump&&frameTravel>frameTravelLimit)recordViolation('ankle-frame-travel',
        frameTravel/frameTravelLimit,{measuredMeters:frameTravel,limitMeters:frameTravelLimit,
          side,timeSeconds:Number(elapsed.toFixed(4)),stage:metrics.clawAction?.stage||'neutral',
          phase:metrics.clawAction?.phase??null});
    }
    exemptNextFrameJump=false;
    assert.ok(maxPivotDrift<LIMITS.pivotLocalDrift,`A lower-leg joint translated ${maxPivotDrift}`);
    assert.ok(maxBasisError<LIMITS.rigidBasisError,`Rigid joint basis error ${maxBasisError}`);
    const claw=metrics.clawAction;
    const stage=claw?.stage??null;
    if(stage){
      stagesSeen.add(stage);
      const active=claw.side;
      const support=active==='left'?'right':'left';
      maxSupportDrift=Math.max(maxSupportDrift,points[support].distanceTo(baseline[support]));
      const supportFloor=footMinY(support);
      maximumSupportFloor=Math.max(maximumSupportFloor,supportFloor);
      if(supportFloor<LIMITS.minimumSupportFootFloor)recordViolation('support-floor-low',
        LIMITS.minimumSupportFootFloor-supportFloor,{side:support,measuredY:supportFloor,
          limitY:LIMITS.minimumSupportFootFloor,stage,phase:claw.phase,timeSeconds:Number(elapsed.toFixed(4))});
      if(supportFloor>LIMITS.maximumSupportFootFloor)recordViolation('support-floor-high',
        supportFloor-LIMITS.maximumSupportFootFloor,{side:support,measuredY:supportFloor,
          limitY:LIMITS.maximumSupportFootFloor,stage,phase:claw.phase,timeSeconds:Number(elapsed.toFixed(4))});
      if(stage==='contact'||stage==='scrape'){
        const tip=distalMinY(active);
        const angles=feet[active].digits.map(node=>node.rotation.x);
        if(angles.reduce((sum,value)=>sum+Math.abs(value),0)>
           peakContactToeAngles.reduce((sum,value)=>sum+Math.abs(value),0))peakContactToeAngles=angles;
        // Contact phase starts raised and descends over its duration; apply the
        // plane test only at its final 10%, then throughout the scrape hold.
        if((stage==='contact'&&claw.phase>=.90)||stage==='scrape'){
          maximumContactTipFloor=Math.max(maximumContactTipFloor,tip);
          const deviation=Math.abs(tip-LIMITS.contactPlaneY);
          if(deviation>LIMITS.contactTipTolerance)recordViolation('contact-plane-distance',
            deviation/LIMITS.contactTipTolerance,{side:active,measuredY:tip,
              planeY:LIMITS.contactPlaneY,tolerance:LIMITS.contactTipTolerance,
              stage,phase:claw.phase,timeSeconds:Number(elapsed.toFixed(4))});
        }
      }
      if(stage!==priorStage){
        stageTransitions.push({stage,phase:claw.phase,timeSeconds:Number(elapsed.toFixed(4)),
          activeAnkle:points[active].toArray(),supportAnkle:points[support].toArray(),
          supportFootMinY:supportFloor,activeDistalMinY:distalMinY(active)});
        priorStage=stage;
      }
      if(elapsed-sampleTime>=.12 || trajectory.length===0){
        trajectory.push({stage,phase:Number(claw.phase.toFixed(3)),timeSeconds:Number(elapsed.toFixed(3)),
          leftAnkle:points.left.toArray(),rightAnkle:points.right.toArray(),
          supportFootMinY:supportFloor,activeDistalMinY:distalMinY(active),
          activeToeAngles:feet[active].digits.map(node=>Number(node.rotation.x.toFixed(5)))});
        sampleTime=elapsed;
      }
      if(maxSupportDrift>LIMITS.maxSupportAnkleDrift)recordViolation('support-ankle-drift',
        maxSupportDrift/LIMITS.maxSupportAnkleDrift,{measuredMeters:maxSupportDrift,
          limitMeters:LIMITS.maxSupportAnkleDrift,side:support,stage,phase:claw.phase,
          timeSeconds:Number(elapsed.toFixed(4))});
    }
    return {state,metrics,points};
  }
  // Establish the renderer's configured root offset and solved rest ankles
  // before measuring action travel; the setup translation is not acting.
  motion.resetEra('builder');
  model.updateMatrixWorld(true);
  motion.tick(0,controller.getSnapshot());
  model.updateMatrixWorld(true);
  for(const side of ['left','right']){
    baseline[side].copy(anklePosition(side));
    previous[side].copy(baseline[side]);
  }
  return {model,nodes,rest,motion,controller,feet,baseline,dt,step,elapsed:()=>elapsed,
    distalMinY,footMinY,anklePosition,hinges,
    allowJumpOnce:()=>{exemptNextFrameJump=true;},
    recordViolation,
    result:()=>({elapsedSeconds:Number(elapsed.toFixed(4)),stages:[...stagesSeen],stageTransitions,
      trajectory,maxFrameAnkleTravel:maxFrameTravel,maxSupportAnkleDrift:maxSupportDrift,
      maxPivotLocalDrift:maxPivotDrift,maxRigidBasisError:maxBasisError,
      minimumDistalFloorY:minimumDistalFloor,maximumSupportFootMinY:maximumSupportFloor,
      maximumContactTipFloorY:maximumContactTipFloor,
      violations:[...violations.values()],
      distalJointAngles:{left:feet.left.digits.map(node=>Number(node.rotation.x.toFixed(6))),
                         right:feet.right.digits.map(node=>Number(node.rotation.x.toFixed(6)))},
      contactToeAngles:peakContactToeAngles.map(value=>Number(value.toFixed(6)))}),
    captureBaseline:()=>{baseline.left.copy(anklePosition('left'));baseline.right.copy(anklePosition('right'));}};
}

function startAction(run) {
  run.captureBaseline();
  assert.equal(run.controller.requestClawAction(),true,'Builder claw action was not available from settled watch');
}

function rotationDistance(a,b) {
  return new THREE.Quaternion().setFromEuler(a).angleTo(new THREE.Quaternion().setFromEuler(b));
}

function advanceUntil(run,predicate,maxSeconds=6) {
  const frames=Math.ceil(maxSeconds/run.dt);
  for(let i=0;i<frames;i++){
    const frame=run.step();
    if(predicate(frame.state,frame.metrics))return frame;
  }
  assert.fail(`Condition was not reached within ${maxSeconds}s; state=${run.controller.getSnapshot().state}`);
}

function completeCycle(run) {
  startAction(run);
  advanceUntil(run,(state,metrics)=>!state.clawAction&&!metrics.clawAction,6);
  for(const phase of PHASES)if(!run.result().stages.includes(phase))
    run.recordViolation(`phase-missing-${phase}`,1,{phase,stagesSeen:run.result().stages});
  const recovery=advanceUntil(run,(state,metrics)=>!state.clawAction&&!metrics.clawAction,0.2);
  const final=run.result();
  if(!Number.isFinite(final.maximumContactTipFloorY))run.recordViolation('contact-plane-unreached',1,
    {planeY:LIMITS.contactPlaneY,stagesSeen:final.stages});
  const angles=final.contactToeAngles;
  if(!angles.length||!angles.every(value=>Math.abs(value)>0.05))run.recordViolation('toe-articulation',1,
    {angles,requiredMagnitude:.05});
  if(new Set(angles.map(value=>value.toFixed(4))).size<5)run.recordViolation('independent-toe-angles',1,
    {angles,requiredUniqueAngles:5});
  for(const side of ['left','right']){
    const end=run.anklePosition(side);
    if(end.distanceTo(run.baseline[side])>=LIMITS.neutralAnkleReturn)run.recordViolation(`neutral-ankle-${side}`,
      end.distanceTo(run.baseline[side])/LIMITS.neutralAnkleReturn,{side,
        measuredMeters:end.distanceTo(run.baseline[side]),limitMeters:LIMITS.neutralAnkleReturn});
    for(const node of run.feet[side].digits){
      const original=run.hinges.find(item=>item.node===node).rotation;
      if(rotationDistance(node.rotation,original)>=1e-6)run.recordViolation(`neutral-digit-${node.name}`,
        rotationDistance(node.rotation,original)/1e-6,{node:node.name,
          angularError:rotationDistance(node.rotation,original)});
    }
  }
  return {...run.result(),recoveredNearBaseline:true,fullRestRotationRestored:true,
    actionCleared:!recovery.state.clawAction&&!recovery.metrics.clawAction};
}

check('complete-claw-contact-cycle-at-60hz',()=>{
  const run=createRun(1/60);return completeCycle(run);
});
check('complete-claw-contact-cycle-at-120hz',()=>{
  const run=createRun(1/120);return completeCycle(run);
});

for(const phase of PHASES){
  for(const interruption of INTERRUPTS){
    check(`${phase}-interrupted-by-${interruption}`,()=>{
      const run=createRun(1/60);startAction(run);
      const reached=advanceUntil(run,(state)=>state.clawAction?.stage===phase&&state.clawAction.phase>=.35,4);
      const before={left:run.anklePosition('left'),right:run.anklePosition('right')};
      const toeBefore=run.feet.left.digits.map(node=>node.rotation.x);
      if(interruption==='inspection')run.controller.setInspection(true);
      else if(interruption==='reduced-motion')run.controller.setReducedMotion(true);
      else if(interruption==='pause')run.controller.setPaused(true);
      else if(interruption==='era-change'){run.controller.setEra('maker');run.allowJumpOnce();}
      else {run.controller.reset();run.allowJumpOnce();}

      let recoverySeen=false,inspectionReached=false,pausedPoseStable=null;
      if(interruption==='pause'){
        for(let i=0;i<18;i++)run.step();
        const paused={left:run.anklePosition('left'),right:run.anklePosition('right'),
          toe:run.feet.left.digits.map(node=>node.rotation.x)};
        const drift=Math.max(paused.left.distanceTo(before.left),paused.right.distanceTo(before.right),
          ...paused.toe.map((value,index)=>Math.abs(value-toeBefore[index])));
        assert.ok(drift<1e-6,`Pause changed the committed pose by ${drift}`);
        pausedPoseStable={driftMetersOrRadians:drift,frames:18};
        run.controller.setPaused(false);
        advanceUntil(run,(state,metrics)=>!state.clawAction&&!metrics.clawAction,4);
      }else if(interruption==='inspection'){
        for(let i=0;i<Math.ceil(4/run.dt);i++){
          const frame=run.step();
          recoverySeen ||= frame.state.clawAction?.stage==='recovery';
          if(frame.state.inspection&&!frame.state.clawAction&&!frame.metrics.clawAction){inspectionReached=true;break;}
        }
        assert.ok(recoverySeen,'Inspection did not route the committed action through recovery');
        assert.ok(inspectionReached,'Inspection did not open after grounded recovery');
        run.controller.setInspection(false);
      }else if(interruption==='reduced-motion'){
        for(let i=0;i<Math.ceil(4/run.dt);i++){
          const frame=run.step();
          recoverySeen ||= frame.state.clawAction?.stage==='recovery';
          if(!frame.state.clawAction&&!frame.metrics.clawAction&&frame.state.state==='watch')break;
        }
        assert.ok(recoverySeen,'Reduced motion did not route the committed action through recovery');
      }else{
        // Era change/reset aborts the action state. A motion tick must clear
        // its private claw cycle and restore toe joints without stale restart.
        for(let i=0;i<45;i++)run.step();
        if(interruption==='era-change'){
          assert.equal(run.controller.getSnapshot().era,'maker');
          run.controller.setEra('builder');
          for(let i=0;i<45;i++)run.step();
        }
      }
      for(let i=0;i<36;i++)run.step();
      const snapshot=run.controller.getSnapshot(),metrics=run.motion.metrics();
      assert.ok(!snapshot.clawAction&&!metrics.clawAction,'Interrupted claw action restarted or remained stale');
      assert.ok(run.feet.left.digits.every(node=>{
        const original=run.hinges.find(item=>item.node===node).rotation;
        return rotationDistance(node.rotation,original)<1e-6;
      }),'Interrupted action left a stale left toe pose');
      return {phase,interruption,phaseAtInterrupt:Number(reached.state.clawAction.phase.toFixed(3)),
        recoverySeen,inspectionReached,pausedPoseStable,actionCleared:true,
        staleRestart:false,activeFootMinY:run.distalMinY('left'),
        supportFootMinY:run.footMinY('right'),trajectory:run.result().stageTransitions,
        violations:run.result().violations};
    });
  }
}

output.status=output.checks.every(item=>item.status==='passed')?'passed':'failed';
await mkdir(dirname(reportPath),{recursive:true});
await writeFile(reportPath,`${JSON.stringify(output,null,2)}\n`);
console.log(`${output.status}: ${output.checks.filter(item=>item.status==='passed').length}/${output.checks.length} claw-contact checks`);
for(const item of output.checks.filter(item=>item.status==='failed'))console.error(`${item.name}: ${item.error}`);
if(output.status!=='passed')process.exitCode=1;
