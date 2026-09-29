import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';
import { solveTransverseLeg } from '../src/scene/rigid-leg-kinematics.js';

const path=process.env.UNCAGED_MODEL||'assets/models/whole-character-v25/attempt-form01/murderbird-whole-character-v25.glb';
const template=await loadRigidValidation(await readFile(path));
const names=['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield','cervical-mid-a','cervical-mid-b','cervical-upper'];

for(const x of [-.6,.6])test(`actual V25 off-center visitor ${x} preserves reachable support through contact and recovery`,()=>{
  const model=clone(template.scene),nodes=Object.fromEntries(names.filter(n=>model.getObjectByName(n)).map(n=>[n,model.getObjectByName(n)]));
  const rest=Object.fromEntries(Object.entries(nodes).map(([n,o])=>[n,{position:o.position.clone(),rotation:o.rotation.clone()}]));
  const motion=createEraMotion(model,nodes,rest),machine=createEraController({seed:927});
  machine.reset();motion.resetEra('builder');
  const prior=new Map();let contacts=0,recovered=false;
  function step(frame){
    const s=machine.update(1/60,motion.feedback());
    for(const n of Object.keys(nodes)){nodes[n].position.copy(rest[n].position);nodes[n].rotation.copy(rest[n].rotation);}
    motion.tick(1/60,s);const m=motion.metrics();
    for(const f of m.feet){
      const hip=model.getObjectByName(f.side+'-thigh'),shin=model.getObjectByName(f.side+'-shin'),foot=model.getObjectByName(f.side+'-foot');
      const target=model.worldToLocal(new THREE.Vector3(...f.target)).sub(hip.position),solution=solveTransverseLeg(shin.position,foot.position,target);
      const context=JSON.stringify({frame,state:s.state,side:f.side,swinging:f.swinging,phase:f.phase,error:f.solveError,targetLength:target.length(),minimumReach:solution.minimumReach,maximumReach:solution.maximumReach,reachDrop:m.reachDrop,root:m.root});
      assert(f.solveError<.002,`Actual ankle left its commanded target: ${context}`);
      assert(Math.abs(shin.quaternion.y)<1e-10&&Math.abs(shin.quaternion.z)<1e-10,'Knee left its transverse hinge');
      if(!f.swinging){
        assert(Math.abs(f.groundMin-.002)<.0015,`Support foot left floor: ${context}`);
        const old=prior.get(f.side);if(old&&!old.swinging){
          assert(Math.hypot(...f.target.map((v,i)=>v-old.target[i]))<1e-7,'Planted support target shifted');
          assert(Math.hypot(...f.actual.map((v,i)=>v-old.actual[i]))<.002,`Planted support geometry drifted: ${context}`);
        }
      }
      prior.set(f.side,f);
    }
    if(s.state==='contact'&&m.contact)contacts++;if(s.state==='recover')recovered=true;
    return s;
  }
  step(0);assert(machine.requestReach({x,y:.25}));
  for(let frame=1;frame<=18*60;frame++){const s=step(frame);if(recovered&&s.state!=='recover')break;}
  assert(recovered&&contacts>0,'Reach correction prevented actual bill contact/recovery');
});
