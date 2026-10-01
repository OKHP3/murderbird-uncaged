import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';
import { createEraMotion } from '../src/scene/era-motion.js';

// Bounded actual-controller pose capture for the cranial support reconstruction.
// No collision, likeness, or continuous-envelope claim.
const MODEL_PATH = 'assets/models/whole-character-v38/neck-fit01/attempt02/murderbird-v38-neck-fit01-attempt02-rigid.glb';
const REPORT_PATH = 'assets/audit/whole-character-v38/cranial-route-integration01/source-runtime-poses.json';
const NODE_NAMES = [
  'body', 'neck', 'head', 'jaw', 'breastplate', 'cranial-cover', 'winding-drive',
  'power-core', 'processing', 'industrial-repairs', 'builder-optics', 'left-mantle',
  'right-mantle', 'left-wing-shield', 'right-wing-shield',
];
let template;

function createRun({ seed = 927, dt = 1 / 60 } = {}) {
  const model = clone(template.scene);
  const scene = new THREE.Scene();
  scene.add(model);
  const nodes = Object.fromEntries(NODE_NAMES.map(name => [name, model.getObjectByName(name)]));
  assert.ok(Object.values(nodes).every(Boolean), 'Source GLB is missing a required motion node');
  const rest = Object.fromEntries(NODE_NAMES.map(name => [name, {
    position: nodes[name].position.clone(), rotation: nodes[name].rotation.clone(),
    quaternion: nodes[name].quaternion.clone(),
  }]));
  const motion = createEraMotion(model, nodes, rest);
  const mechanisms = createEraMechanisms({ scene, model, nodes, rest });
  const machine = createEraController({ seed });
  let era = 'builder';
  let time = 0;

  function step(seconds = dt) {
    const state = machine.update(seconds, motion.feedback());
    if (state.era !== era) {
      era = state.era;
      mechanisms.setEra(era);
    }
    for (const name of NODE_NAMES) {
      nodes[name].position.copy(rest[name].position);
      nodes[name].rotation.copy(rest[name].rotation);
    }
    motion.tick(seconds, state);
    mechanisms.tick(seconds, state, motion.driveMetrics(), { open: 0, separation: 0 });
    time += seconds;
    return { state, metrics: motion.metrics(), time };
  }

  function advanceUntil(predicate, limitSeconds = 16) {
    const limit = Math.ceil(limitSeconds / dt);
    for (let i = 0; i < limit; i += 1) {
      const frame = step();
      if (predicate(frame.state, frame.metrics)) return frame;
    }
    assert.fail(`condition not reached within ${limitSeconds}s; state=${machine.getSnapshot().state}`);
  }

  function advanceFor(seconds) {
    const end = time + seconds;
    while (time + 1e-9 < end) step(Math.min(dt, end - time));
  }

  return { scene, model, nodes, rest, motion, mechanisms, machine, step, advanceUntil, advanceFor };
}


// Capture actual controller-produced transforms, not hand-authored angle combinations.
const bytes = await readFile(MODEL_PATH);
template = await loadRigidValidation(bytes);
for (const name of ['cervical-mid-a','cervical-mid-b','cervical-upper']) NODE_NAMES.push(name);
const names=['body','neck','cervical-mid-a','cervical-mid-b','cervical-upper','head'];
const samples=[];
function snapshot(run,label,frame){return {label,time:frame?.time??0,state:frame?.state?.state??'rest',headEuler:run.nodes.head.rotation.toArray(),gaze:frame?.metrics.pose.gaze??0,nodes:Object.fromEntries(names.map(n=>[n,{position:run.nodes[n].position.toArray(),quaternion:run.nodes[n].quaternion.toArray(),scale:run.nodes[n].scale.toArray(),restQuaternion:run.rest[n].quaternion.toArray()}]))};}
for(const rail of [-1,0,1]){
 const run=createRun(); let extreme=null;
 run.machine.requestReach({x:rail});
 for(let i=0;i<720;i++){
  const frame=run.step();
  if(!extreme||Math.abs(run.nodes.head.rotation.y)>Math.abs(extreme.headEuler[1]))extreme=snapshot(run,`rail${rail}-sampled-max-yaw`,frame);
  if(frame.state.state==='contact'&&frame.metrics.contact){samples.push(snapshot(run,`rail${rail}-contact`,frame));break;}
 }
 samples.push(extreme);run.mechanisms.dispose();
}
const maker=createRun();maker.machine.setEra('maker');maker.advanceFor(.2);maker.machine.setArticulation('neck',1);maker.advanceFor(.8);samples.push(snapshot(maker,'maker-neck-control',{time:1,state:{state:'maker'},metrics:maker.motion.metrics()}));maker.mechanisms.dispose();
const result={model:MODEL_PATH,modelSHA256:createHash('sha256').update(bytes).digest('hex'),scope:'Seven actual controller-generated local-transform samples from three reach trajectories plus Maker neck. Sampled maxima, not analytic full limits or continuous sweep. glTF local TRS, quaternion xyzw; convert basis from actual imported glTF or world matrices before using in Blender.',samples};
await mkdir(dirname(REPORT_PATH),{recursive:true});await writeFile(REPORT_PATH,JSON.stringify(result,null,2)+'\n',{flag:'wx'});console.log(samples.map(x=>({label:x.label,state:x.state,headEuler:x.headEuler})));
