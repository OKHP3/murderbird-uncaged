import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import * as THREE from 'three';
import { clone } from 'three/addons/utils/SkeletonUtils.js';
import { loadRigidValidation } from '../scripts/load-rigid-validation.mjs';
import { createCervicalArticulation } from '../src/scene/cervical-articulation.js';
import { createEraMotion } from '../src/scene/era-motion.js';

const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive',
  'power-core','processing','industrial-repairs','builder-optics','left-mantle',
  'right-mantle','left-wing-shield','right-wing-shield'];
const pitchNames = ['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];
const layout = { schema:1, pitchJoints:pitchNames, weights:[.25,.25,.25,.25], rootYaw:'neck', headOwner:'head' };
const path = 'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.glb';
const close = (a,b,tolerance=1e-10) => assert.ok(Math.abs(a-b)<tolerance, `${a} != ${b}`);

async function fixture({ declared = true, nonIdentity = false } = {}) {
  const model = clone((await loadRigidValidation(await readFile(path))).scene);
  const nodes = Object.fromEntries(names.map(name => [name,model.getObjectByName(name)]));
  if (declared) {
    // Adapt the actual V21 rigid rest scene into a four-pivot attachment
    // fixture, preserving the original upper/head world rests. No V23 armor
    // or runtime-model acceptance is implied by this synthetic topology.
    const cover=model.getObjectByName('cervical-joint-cover'); cover?.removeFromParent();
    model.updateMatrixWorld(true);
    const upper=model.getObjectByName('cervical-upper');
    const start=nodes.neck.getWorldPosition(new THREE.Vector3());
    const end=upper.getWorldPosition(new THREE.Vector3());
    const mids=[1/3,2/3].map((fraction,i)=> {
      const group=new THREE.Group(); group.name=pitchNames[i+1];
      group.position.copy(start.clone().lerp(end,fraction)); model.add(group); return group;
    });
    model.updateMatrixWorld(true); nodes.neck.attach(mids[0]); mids[0].attach(mids[1]); mids[1].attach(upper);
    if (nonIdentity) {
      mids[0].rotation.set(.07,-.03,.02); mids[1].rotation.set(-.045,.02,-.01);
      nodes.neck.rotation.set(.035,.025,-.015);
    }
    nodes.body.userData.cervicalLayoutV2=JSON.stringify(layout);
  }
  model.updateMatrixWorld(true);
  const rest=Object.fromEntries(names.map(name=>[name,{position:nodes[name].position.clone(),rotation:nodes[name].rotation.clone()}]));
  return {model,nodes,rest,joints:pitchNames.map(name=>model.getObjectByName(name))};
}

function assertRigid(f, positions) {
  f.model.updateMatrixWorld(true);
  f.joints.forEach((joint,i)=> {
    assert.deepEqual(joint.position.toArray(),positions[i].toArray(), `${joint.name} translated`);
    const columns=[0,1,2].map(axis=>new THREE.Vector3().setFromMatrixColumn(joint.matrixWorld,axis));
    columns.forEach(column=>close(column.length(),1,1e-6));
    close(columns[0].dot(columns[1]),0,1e-6); close(columns[1].dot(columns[2]),0,1e-6);
  });
}
function assertSnapshot(snapshot) {
  snapshot.forEach(({node,position,quaternion})=> {
    assert.deepEqual(node.position.toArray(),position.toArray(), `${node.name} probe position drift`);
    assert.deepEqual(node.quaternion.toArray(),quaternion.toArray(), `${node.name} probe rotation drift`);
  });
}

function addSkullReceiver(f) {
  const receiver = new THREE.Group(); receiver.name = 'cervical-skull-cover';
  receiver.position.copy(f.nodes.head.position);
  f.joints[3].add(receiver);
  f.nodes.body.userData.cervicalLayoutV2 = JSON.stringify({...layout, skullReceiver:receiver.name});
  return receiver;
}

test('declared rigid skull receiver bisects multi-axis motion at the shared pivot and restores snapshots', async()=> {
  const f=await fixture({nonIdentity:true}), receiver=addSkullReceiver(f);
  f.nodes.head.rotation.set(.13,-.09,.04); receiver.rotation.set(-.06,.08,.03);
  const headRest=f.nodes.head.quaternion.clone(), coverRest=receiver.quaternion.clone();
  const c=createCervicalArticulation(f.model,f.nodes,f.rest);
  for (const angles of [[-.509,0,0],[-.35,.3,-.06],[.1,-.45,.08]]) {
    const delta=new THREE.Quaternion().setFromEuler(new THREE.Euler(...angles));
    f.nodes.head.quaternion.copy(delta).multiply(headRest);
    c.updateCovers();
    const actual=receiver.quaternion.clone().multiply(coverRest.clone().invert());
    // Two receiver excursions reproduce the full head excursion. This checks
    // compound rotation, where halving Euler components gives a wrong result.
    assert.ok(actual.clone().multiply(actual).angleTo(delta)<1e-7);
    close(receiver.position.distanceTo(f.nodes.head.position),0);
    const saved=c.capturePose(); c.restoreAttachments();
    assert.deepEqual(receiver.quaternion.toArray(),coverRest.toArray());
    c.restorePose(saved); assertSnapshot(saved);
  }
});

test('four-stage skull receiver must be explicitly declared and share the actual head centre', async()=> {
  for (const defect of ['undeclared','missing','parent','centre','name']) {
    const f=await fixture(), receiver=addSkullReceiver(f);
    if(defect==='undeclared') f.nodes.body.userData.cervicalLayoutV2=JSON.stringify(layout);
    if(defect==='missing') receiver.removeFromParent();
    if(defect==='parent') f.nodes.neck.add(receiver);
    if(defect==='centre') receiver.position.x+=.002;
    if(defect==='name') f.nodes.body.userData.cervicalLayoutV2=JSON.stringify({...layout,skullReceiver:'arbitrary'});
    assert.throws(()=>createCervicalArticulation(f.model,f.nodes,f.rest),/receiver|Receiver|cover owners/);
  }
});

test('receiver follows final contact and clears through Maker, claw, power and reset paths', async()=> {
  const f=await fixture(), receiver=addSkullReceiver(f);
  const motion=createEraMotion(f.model,f.nodes,f.rest);
  const atRest=()=>close(receiver.quaternion.angleTo(new THREE.Quaternion()),0,1e-7);
  for(let i=0;i<180;i++) motion.tick(1/60,{era:'builder',state:'contact',phase:1,
    goal:{x:0,z:motion.metrics().contactApproach.z},speed:.42});
  assert.ok(receiver.rotation.x<-.15,'Receiver did not follow final contact counterrotation');
  assert.ok(receiver.quaternion.clone().multiply(receiver.quaternion).angleTo(f.nodes.head.quaternion)<1e-7);
  for(const snapshot of [
    {era:'maker',state:'external-control',articulation:{neck:1}},
    {era:'mechanic',state:'rest'},
    {era:'builder',state:'watch',clawAction:{side:'left',stage:'lift',phase:.2}},
    {era:'builder',state:'watch',powerMove:{kind:'jump',phase:.5}},
  ]) {
    motion.tick(1/60,snapshot); atRest();
    close(motion.metrics().cervical.outerReceivers[0].jointCentreError,0);
  }
  receiver.rotation.x=.2; motion.resetEra('maker'); atRest();
});

test('four rest-relative joints share pitch while root yaw remains independent and translations stay rigid', async()=> {
  const f=await fixture({nonIdentity:true}); const c=createCervicalArticulation(f.model,f.nodes,f.rest);
  const positions=f.joints.map(joint=>joint.position.clone()); const origins=f.joints.map(joint=>joint.quaternion.clone());
  for(const [pitch,yaw] of [[-.14,-.45],[.65,0],[-.07,0],[.08,.288]]) {
    c.setPitch(pitch,yaw,0); close(c.pitch,pitch);
    c.metrics().pitchJoints.forEach(joint=> {close(joint.pitch,pitch*.25);close(joint.translationError,0);});
    const expected=origins[0].clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(pitch*.25,yaw,0)));
    assert.ok(expected.angleTo(f.joints[0].quaternion)<1e-7);
    assertRigid(f,positions);
  }
  c.setPitch(.2,-.45,.01); c.setPitch(.4); close(c.pitch,.4);
  const expected=origins[0].clone().multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(.1,-.45,.01)));
  assert.ok(expected.angleTo(f.joints[0].quaternion)<1e-7,'Implicit pitch update lost independent yaw/roll');
  f.joints[1].position.x+=.02; c.restoreAttachments();
  origins.forEach((q,i)=>assert.deepEqual(f.joints[i].quaternion.toArray(),q.toArray())); close(c.pitch,0); assertRigid(f,positions);
});

test('repeated contact probes restore every joint and final head pose exactly', async()=> {
  const f=await fixture({nonIdentity:true}); const c=createCervicalArticulation(f.model,f.nodes,f.rest);
  c.setPitch(-.14,-.45); f.nodes.head.rotation.set(.02,-.12,.01);
  const saved=c.capturePose();
  for(let run=0;run<20;run++) {
    c.restoreAttachments(); c.setPitch(.65,0,0); f.nodes.head.rotation.set(-.731,0,0);
    c.restorePose(saved); assertSnapshot(saved); close(c.pitch,-.14);
  }
  assert.throws(()=>c.restorePose(saved.slice(1)),/different articulation/);
});

test('era contact precompute and Maker/Advanced/reset exercise the optional four-joint fixture', async()=> {
  const f=await fixture(); const c=createCervicalArticulation(f.model,f.nodes,f.rest);
  const saved=c.capturePose();
  const motion=createEraMotion(f.model,f.nodes,f.rest); assertSnapshot(saved);
  const positions=f.joints.map(joint=>joint.position.clone());
  for(let i=0;i<300;i++) motion.tick(1/60,{era:'maker',state:'external-control',articulation:{neck:1}});
  close(motion.metrics().cervical.totalPitch,-.14,1e-7); close(f.nodes.neck.rotation.y,-.45,1e-7);
  f.joints.forEach(joint=>close(joint.rotation.x,-.035,1e-7)); assertRigid(f,positions);
  motion.resetEra('builder');
  for(let i=0;i<180;i++) motion.tick(1/60,{era:'builder',state:'contact',phase:1,
    goal:{x:0,z:motion.metrics().contactApproach.z},speed:.42});
  const metrics=motion.metrics().cervical; assert.equal(metrics.jointCount,4);
  assert.ok(metrics.totalPitch>.3 && metrics.totalPitch<=.65+1e-7,'Contact did not exercise an actual extended chain');
  metrics.pitchJoints.forEach(joint=>close(joint.pitch,metrics.totalPitch*.25,1e-7));
  assert.ok(f.nodes.head.rotation.x<-.3,'Final head counterrotation was not exercised'); assertRigid(f,positions);
  motion.resetEra('mechanic'); motion.tick(1/60,{era:'mechanic',state:'rest'}); close(c.pitch,0);
});

test('invalid declared hierarchy, weights and names are rejected before animation',async()=> {
  for(const weights of [[.25,.25,.25,.3],[.5,.5,0,0],[.25,.25,.25,'0.25']]) {
    const f=await fixture(); f.nodes.body.userData.cervicalLayoutV2=JSON.stringify({...layout,weights});
    assert.throws(()=>createCervicalArticulation(f.model,f.nodes,f.rest),/Invalid cervicalLayoutV2/);
  }
  const f=await fixture(); f.nodes.neck.add(f.joints[2]);
  assert.throws(()=>createCervicalArticulation(f.model,f.nodes,f.rest),/hierarchy/);
  const bad=await fixture(); bad.nodes.body.userData.cervicalLayoutV2='{bad';
  assert.throws(()=>createCervicalArticulation(bad.model,bad.nodes,bad.rest),/JSON/);
  bad.nodes.body.userData.cervicalLayoutV2=JSON.stringify({...layout,pitchJoints:['neck','missing','cervical-mid-b','cervical-upper']});
  assert.throws(()=>createCervicalArticulation(bad.model,bad.nodes,bad.rest),/joint names/);
});

test('undeclared V21 retains the legacy 35/65 split and linked receiver',async()=> {
  const f=await fixture({declared:false}); const c=createCervicalArticulation(f.model,f.nodes,f.rest);
  c.setPitch(.65,-.45); close(f.nodes.neck.rotation.x,.2275);close(c.upper.rotation.x,.4225);
  close(f.model.getObjectByName('cervical-joint-cover').rotation.x,.21125);close(c.pitch,.65);
  const saved=c.capturePose();c.setPitch(-.14,0);c.restorePose(saved);assertSnapshot(saved);
  assert.equal(c.metrics().jointCount,2);
});

test('contact counterrotation clears on direct Maker, claw and reset boundaries without caller pose resets',async()=> {
  const f=await fixture();const headRest=f.nodes.head.quaternion.clone();
  const motion=createEraMotion(f.model,f.nodes,f.rest);
  async function contact() {
    for(let i=0;i<180;i++) motion.tick(1/60,{era:'builder',state:'contact',phase:1,
      goal:{x:0,z:motion.metrics().contactApproach.z},speed:.42});
    assert.ok(f.nodes.head.rotation.x<-.3,'Transition fixture did not counter-rotate the skull');
  }
  const assertHeadRest=()=>assert.deepEqual(f.nodes.head.quaternion.toArray(),headRest.toArray());
  await contact();
  motion.tick(1/60,{era:'maker',state:'external-control',articulation:{neck:1}});assertHeadRest();
  await contact();
  motion.tick(1/60,{era:'builder',state:'watch',clawAction:{side:'left',stage:'lift',phase:.2}});assertHeadRest();
  close(motion.metrics().cervical.totalPitch,0);
  await contact();motion.resetEra('maker');assertHeadRest();
});
