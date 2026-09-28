import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';

// A sampled triangle-crossing diagnostic, not an exhaustive collision solver.
// Coplanar contact and a whole mesh enclosed inside another are not certified.
const modelPath=process.env.UNCAGED_MODEL||'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const auditPath=process.env.UNCAGED_AUDIT||'assets/audit/alignment-v3';
assert.ok(!auditPath.includes('/neutral-v2'));
const bytes=await readFile(modelPath),{scene:model}=await loadRigidValidation(bytes);
const head=model.getObjectByName('head'),jaw=model.getObjectByName('jaw');
model.updateMatrixWorld(true);
const inverse=head.matrixWorld.clone().invert(),pivot=jaw.position.clone();
const stationaryNames=['head-head-plate','upper-bill-head-plate','cranial-cover-head-plate'];
const cell=.025,grid=new Map(),point=new THREE.Vector3(),ray=new THREE.Ray();
function triangles(mesh) {
  const result=[],positions=mesh.geometry.attributes.position,index=mesh.geometry.index;
  const matrix=inverse.clone().multiply(mesh.matrixWorld),count=index?index.count:positions.count;
  for(let i=0;i<count;i+=3){
    const vertices=[0,1,2].map(j=>new THREE.Vector3().fromBufferAttribute(positions,index?index.getX(i+j):i+j).applyMatrix4(matrix));
    if(new THREE.Triangle(...vertices).getArea()<1e-12)continue;
    result.push({vertices,box:new THREE.Box3().setFromPoints(vertices),name:mesh.name,index:i/3});
  }
  return result;
}
function keys(box) {
  const result=[];
  for(let x=Math.floor(box.min.x/cell);x<=Math.floor(box.max.x/cell);x++)for(let y=Math.floor(box.min.y/cell);y<=Math.floor(box.max.y/cell);y++)for(let z=Math.floor(box.min.z/cell);z<=Math.floor(box.max.z/cell);z++)result.push(`${x},${y},${z}`);
  return result;
}
const fixed=stationaryNames.flatMap(name=>{const mesh=model.getObjectByName(name);assert.ok(mesh,`Missing stationary surface ${name}`);return triangles(mesh);});
assert.ok(fixed.length>0,'Stationary surface triangle inventory is empty.');
fixed.forEach((tri,i)=>{for(const key of keys(tri.box)){if(!grid.has(key))grid.set(key,[]);grid.get(key).push(i);}});
const moving=[];jaw.traverse(object=>{if(object.isMesh)moving.push(object);});
assert.ok(moving.length>0,'Moving jaw mesh inventory is empty.');
function crossing(first,second) {
  const contacts=[];
  for(const [from,to] of [[first,second],[second,first]])for(let i=0;i<3;i++){
    const a=from.vertices[i],b=from.vertices[(i+1)%3],direction=b.clone().sub(a),length=direction.length();
    if(length<1e-8)continue;
    ray.set(a,direction.divideScalar(length));
    if(ray.intersectTriangle(...to.vertices,false,point)){
      const t=point.distanceTo(a);
      if(t>.00001&&t<length-.00001)contacts.push(point.clone());
    }
  }
  return contacts;
}
const fixture={vertices:[new THREE.Vector3(-1,-1,0),new THREE.Vector3(1,-1,0),new THREE.Vector3(0,1,0)]};
const through={vertices:[new THREE.Vector3(0,-.5,-1),new THREE.Vector3(0,-.5,1),new THREE.Vector3(0,.5,0)]};
assert.ok(crossing(fixture,through).length>0,'Crossing kernel failed its intersecting fixture.');
assert.equal(crossing(fixture,{vertices:through.vertices.map(vertex=>vertex.clone().add(new THREE.Vector3(0,0,3)))}).length,0,'Crossing kernel rejected its separated fixture.');
const samples=[];
for(let frame=0;frame<=32;frame++){
  const angle=frame/100;jaw.rotation.x=angle;model.updateMatrixWorld(true);
  let intersections=0,excludedBearingContacts=0;const examples=[],pairs={},swept=moving.flatMap(triangles);
  assert.ok(swept.length>0,'Sampled jaw triangle inventory is empty.');
  for(const tri of swept){
    const candidates=new Set(keys(tri.box).flatMap(key=>grid.get(key)||[]));
    for(const id of candidates){
      const other=fixed[id];if(!tri.box.intersectsBox(other.box))continue;
      const contacts=crossing(tri,other);if(!contacts.length)continue;
      // The real coaxial journal is 32 mm in radius. Exclude only its 34 mm
      // radial envelope near the two lateral journals, not the whole cheek.
      const contact=contacts.find(hit=>!(Math.hypot(hit.y-pivot.y,hit.z-pivot.z)<=.034&&Math.abs(hit.x)>=.071&&Math.abs(hit.x)<=.128));
      if(!contact){excludedBearingContacts++;continue;}
      intersections++;const pair=`${tri.name} / ${other.name}`;pairs[pair]=(pairs[pair]||0)+1;
      if(examples.length<12)examples.push({moving:tri.name,movingTriangle:tri.index,fixed:other.name,fixedTriangle:other.index,point:contact.toArray()});
    }
  }
  samples.push({angle,movingTriangles:swept.length,intersections,excludedBearingContacts,pairs,examples});
}
const failed=samples.filter(sample=>sample.intersections>0);
const output={generatedAt:new Date().toISOString(),model:modelPath,sha256:createHash('sha256').update(bytes).digest('hex'),status:failed.length?'crossings-detected':'no-crossings-detected',scope:'33 actual-mesh samples from closed through +0.32 rad. Jaw against fixed cheek, upper bill and crown plates. Proper segment/triangle crossings only; coplanar contact, containment, continuous between-sample clearance, forces and all other pairs remain unverified.',stationaryMeshes:stationaryNames,stationaryTriangles:fixed.length,excludedJournalEnvelope:{radialMetres:.034,absoluteX:[.071,.128],centerHeadLocal:pivot.toArray()},samples};
await mkdir(auditPath,{recursive:true});await writeFile(`${auditPath}/jaw-sweep.json`,`${JSON.stringify(output,null,2)}\n`);
console.log(`${output.status}: ${failed.length}/${samples.length} sampled poses contain crossings outside journal envelope`);
for(const sample of failed)console.log(JSON.stringify({angle:sample.angle,intersections:sample.intersections,pairs:sample.pairs,example:sample.examples[0]}));
if(failed.length)process.exitCode=1;
