/** Check the altered visible exterior's contacts and rigid attachment contract. */
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';
const modelPath='assets/models/uncaged-exterior-v1/murderbird-exterior-v1.glb';
const gltf=await loadRigidValidation(await readFile(modelPath));
const scene=gltf.scene;scene.updateMatrixWorld(true);
const inventory=JSON.parse(await readFile('assets/models/uncaged-exterior-v1/exterior-inventory.json','utf8'));
const checks=[];
function check(name,fn){try{checks.push({name,status:'passed',detail:fn()});}catch(e){checks.push({name,status:'failed',error:e.message});}}
check('Bill contact landmark lies on the new hard bill surface',()=>{
 const tip=scene.getObjectByName('bill-contact').getWorldPosition(new THREE.Vector3());
 const upper=scene.getObjectByName('upper-bill');const triangle=new THREE.Triangle(),closest=new THREE.Vector3();let distance=Infinity,triangles=0;
 upper.traverse(o=>{let owner=o;while(owner&&!owner.userData.exteriorEras)owner=owner.parent;if(!o.isMesh||owner?.userData.exteriorEras!=='builder')return;const p=o.geometry.attributes.position,index=o.geometry.index;
  for(let i=0;i<index.count;i+=3){for(const [point,offset] of [[triangle.a,0],[triangle.b,1],[triangle.c,2]])point.fromBufferAttribute(p,index.getX(i+offset)).applyMatrix4(o.matrixWorld);triangle.closestPointToPoint(tip,closest);distance=Math.min(distance,tip.distanceTo(closest));triangles++;}
 });assert(triangles>0);assert(distance<.015,`contact landmark is ${distance} m from upper bill`);return {distanceMeters:distance,triangles,scope:'Static exported surface proximity; dynamic contact is checked separately'};
});
check('Opening covers and joint armor retain independent rigid owners',()=>{
 const pairs={'cranial-cover':'head','breastplate':'body','left-wing-shield':'left-mantle','right-wing-shield':'right-mantle'};
 for(const [child,parent] of Object.entries(pairs))assert.equal(scene.getObjectByName(child).parent.name,parent);
 for(const p of inventory.parts){
  if(p.region==='wing')assert(/-(?:mantle|wing-shield)$/.test(p.attachment),p.part);
  if(p.part.startsWith('Cranial '))assert.equal(p.attachment,'cranial-cover',p.part);
  if(p.part.includes('fitted shin guard'))assert(/-shin/.test(p.attachment),p.part);
  if(p.part.includes('toe sheath'))assert(/-toes/.test(p.attachment),p.part);
 }
 return {pairs,editableParts:inventory.parts.length,scope:'Rigid ownership, not a full swept collision solver'};
});
check('Earlier exteriors exclude awakened lenses, power and processing',()=>{
 const late=inventory.parts.filter(p=>p.role==='optic'||['power-core','processing','builder-optics'].includes(p.attachment));
 assert(late.length>0);assert(late.every(p=>p.era==='builder'));
 const repairs=inventory.parts.filter(p=>p.attachment==='industrial-repairs');assert(repairs.length>0);assert(repairs.every(p=>p.era!=='maker'));
 return {advancedOnlyParts:late.length,laterRepairParts:repairs.length};
});
const report={generatedAt:new Date().toISOString(),model:modelPath,status:checks.every(c=>c.status==='passed')?'passed':'failed',checks};
await writeFile('assets/audit/exterior-v1/construction-validation.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));if(report.status!=='passed')process.exitCode=1;
