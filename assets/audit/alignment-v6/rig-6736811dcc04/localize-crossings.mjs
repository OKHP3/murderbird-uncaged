import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, writeFile } from 'node:fs/promises';
import * as THREE from 'three';
import { loadRigidValidation } from '../../../../scripts/load-rigid-validation.mjs';

// Diagnostic only: same sampled transforms and crossing kernel as the existing
// jaw-neck validator; emits full points and triangle bounds without changing its gate.
const dir = 'assets/audit/alignment-v6/rig-6736811dcc04';
const modelPath = `${dir}/model-inputs/v6-fourth.glb`;
const bytes = await readFile(modelPath);
const sha = b => createHash('sha256').update(b).digest('hex');
const modelSha256 = sha(bytes);
assert.equal(modelSha256, '6736811dcc04605eb59bf8b105a62c348dd5457c5d2b45aa39d42a55a0785784');
const { scene: model } = await loadRigidValidation(bytes);
const head = model.getObjectByName('head'), jaw = model.getObjectByName('jaw'), neck = model.getObjectByName('neck');
assert.ok(head && jaw && neck);
function descendantOf(object, ancestor) { for (let node=object;node;node=node.parent) if(node===ancestor)return true; return false; }
const movingMeshes=[]; jaw.traverse(o=>{if(o.isMesh)movingMeshes.push(o);});
const fixedMeshes=[]; neck.traverse(o=>{if(o.isMesh&&o.userData?.region==='neck'&&['plate','frame'].includes(o.userData?.surfaceRole)&&!descendantOf(o,head))fixedMeshes.push(o);});
function trianglesFor(mesh, rootInverse) {
  const out=[],p=mesh.geometry.attributes.position,index=mesh.geometry.index;
  const matrix=rootInverse.clone().multiply(mesh.matrixWorld),count=index?index.count:p.count;
  for(let i=0;i<count;i+=3){
    const vertices=[0,1,2].map(j=>new THREE.Vector3().fromBufferAttribute(p,index?index.getX(i+j):i+j).applyMatrix4(matrix));
    if(new THREE.Triangle(...vertices).getArea()<1e-12)continue;
    out.push({vertices,box:new THREE.Box3().setFromPoints(vertices),name:mesh.name,index:i/3});
  }
  return out;
}
function crossing(first,second){
  const contacts=[],point=new THREE.Vector3(),ray=new THREE.Ray();
  for(const [from,to] of [[first,second],[second,first]])for(let i=0;i<3;i++){
    const a=from.vertices[i],b=from.vertices[(i+1)%3],direction=b.clone().sub(a),length=direction.length();
    if(length<1e-8)continue;ray.set(a,direction.divideScalar(length));
    if(!ray.intersectTriangle(...to.vertices,false,point))continue;
    const distance=point.distanceTo(a);if(distance>.00001&&distance<length-.00001)contacts.push(point.clone());
  }
  return contacts;
}
function bounds(tri){return {min:tri.box.min.toArray(),max:tri.box.max.toArray()};}
model.updateMatrixWorld(true);
const modelInverse=model.matrixWorld.clone().invert();
const fixed=fixedMeshes.flatMap(mesh=>trianglesFor(mesh,modelInverse));
const cell=.025;
function keys(box){const out=[];for(let x=Math.floor(box.min.x/cell);x<=Math.floor(box.max.x/cell);x++)for(let y=Math.floor(box.min.y/cell);y<=Math.floor(box.max.y/cell);y++)for(let z=Math.floor(box.min.z/cell);z<=Math.floor(box.max.z/cell);z++)out.push(`${x},${y},${z}`);return out;}
const grid=new Map();fixed.forEach((tri,i)=>{for(const key of keys(tri.box)){if(!grid.has(key))grid.set(key,[]);grid.get(key).push(i);}});
const headRest=head.rotation.clone(),jawRest=jaw.rotation.clone();
const failures=[];
for(const yaw of [-.35,0,.35]){
  head.rotation.copy(headRest);head.rotation.x+=0;head.rotation.y+=yaw;
  jaw.rotation.copy(jawRest);jaw.rotation.x+=.32;model.updateMatrixWorld(true);
  const moving=movingMeshes.flatMap(mesh=>trianglesFor(mesh,modelInverse));
  const points=[],angles=[],highPoints=[],highAngles=[],movingBounds=[],fixedBounds=[],fixedTriangleCounts={},movingTriangleCounts={};
  for(const a of moving){
    const candidates=new Set(keys(a.box).flatMap(key=>grid.get(key)||[]));
    for(const id of candidates){const b=fixed[id];if(!a.box.intersectsBox(b.box))continue;
      const hits=crossing(a,b);if(!hits.length)continue;
      fixedTriangleCounts[b.index]=(fixedTriangleCounts[b.index]||0)+1;
      movingTriangleCounts[`${a.name}#${a.index}`]=(movingTriangleCounts[`${a.name}#${a.index}`]||0)+1;
      movingBounds.push(bounds(a));fixedBounds.push(bounds(b));
      for(const p of hits){points.push(p.toArray());angles.push(neckAngle(p));if(p.y>=1.55){highPoints.push(p.toArray());highAngles.push(neckAngle(p));}}
    }
  }
  failures.push({pitch:0,yaw,jawOpen:.32,crossingTrianglePairs:Object.values(fixedTriangleCounts).reduce((s,n)=>s+n,0),contactPointCount:points.length,
    contactPointBounds:range(points),sourceAngleRangeRad:{min:Math.min(...angles),max:Math.max(...angles)},highContactPointsAtOrAboveHeight1_55:{count:highPoints.length,bounds:highPoints.length?range(highPoints):null,sourceAngleRangeRad:highAngles.length?{min:Math.min(...highAngles),max:Math.max(...highAngles)}:null},nativePlatePairCounts:groupByNativePlate(fixedTriangleCounts),movingTriangleBounds:mergeBounds(movingBounds),fixedTriangleBounds:mergeBounds(fixedBounds),
    topFixedTriangles:Object.entries(fixedTriangleCounts).sort((a,b)=>b[1]-a[1]).slice(0,24).map(([triangle,pairCount])=>({triangle:Number(triangle),pairCount})),
    topMovingTriangles:Object.entries(movingTriangleCounts).sort((a,b)=>b[1]-a[1]).slice(0,16).map(([key,pairCount])=>({key,pairCount}))});
}
head.rotation.copy(headRest);jaw.rotation.copy(jawRest);model.updateMatrixWorld(true);
function neckAngle(p){
  // GLB axis conversion: model x=source x, model y=source z, model z=-source y.
  const z=p.y, y=-p.z, knots=[[1.25,-.095,.205,.208],[1.325,-.15,.177,.19],[1.41,-.23,.147,.17],[1.48,-.283,.127,.148],[1.55,-.253,.109,.107],[1.60,-.218,.088,.086],[1.65,-.200,.082,.082]];
  let i=0;while(i<knots.length-2&&z>knots[i+1][0])i++;const a=knots[i],b=knots[i+1],t=Math.max(0,Math.min(1,(z-a[0])/(b[0]-a[0])));
  const cy=a[1]+(b[1]-a[1])*t,rx=a[2]+(b[2]-a[2])*t,ry=a[3]+(b[3]-a[3])*t;
  return Math.atan2(p.x/rx,-(y-cy)/ry);
}
function range(points){const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];for(const p of points)for(let i=0;i<3;i++){min[i]=Math.min(min[i],p[i]);max[i]=Math.max(max[i],p[i]);}return {min,max};}
function mergeBounds(items){return {min:[0,1,2].map(i=>Math.min(...items.map(b=>b.min[i]))),max:[0,1,2].map(i=>Math.max(...items.map(b=>b.max[i])))};}
function groupByNativePlate(counts){const names=['Throat formed lamina 1','Throat formed lamina 2','Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Cervical flank lamina -1 1','Cervical flank lamina 1 1','Cervical flank lamina -1 2','Cervical flank lamina 1 2','Cervical flank lamina -1 3','Cervical flank lamina 1 3','Cervical flank lamina -1 4','Cervical flank lamina 1 4','Cervical flank lamina -1 5','Cervical flank lamina 1 5','Cervical flank lamina -1 6','Cervical flank lamina 1 6'];const out={};for(const [id,n] of Object.entries(counts)){const i=Math.floor(Number(id)/464);const label=names[i]||`triangle ${id} outside inferred ranges`;out[label]=(out[label]||0)+n;}return out;}
const out={generatedAt:new Date().toISOString(),model:{path:modelPath,sha256:modelSha256,bytes:bytes.length},inputs:{validator:'scripts/verify-jaw-neck-clearance.mjs',validatorSha256:sha(await readFile('scripts/verify-jaw-neck-clearance.mjs')),neckRecipe:'scripts/alignment-v6-neck.py',neckRecipeSha256:sha(await readFile('scripts/alignment-v6-neck.py')),inventory:'assets/models/uncaged-alignment-v6/alignment-inventory.json',inventorySha256:sha(await readFile('assets/models/uncaged-alignment-v6/alignment-inventory.json'))},method:'Diagnostic replay of validator triangle generation, fixed neck mesh grid, pose values, and proper segment/triangle crossing kernel. Uses all intersection points instead of validator capped examples. Bounds in GLB loader model coordinates; exported neck plate geometry is one joined mesh.',fixedMeshNames:fixedMeshes.map(m=>m.name),failurePoses:failures,nativeMapping:{status:'strongly inferred from construction/export ordering, not independently inspected in Blender',trianglesPerPlate:464,mergedTriangleCount:fixed.filter(t=>t.name==='neck-neck-plate').length,orderedSourcePlates:['Throat formed lamina 1','Throat formed lamina 2','Throat formed lamina 3','Throat formed lamina 4','Throat formed lamina 5','Throat formed lamina 6','Cervical flank lamina -1 1','Cervical flank lamina 1 1','Cervical flank lamina -1 2','Cervical flank lamina 1 2','Cervical flank lamina -1 3','Cervical flank lamina 1 3','Cervical flank lamina -1 4','Cervical flank lamina 1 4','Cervical flank lamina -1 5','Cervical flank lamina 1 5','Cervical flank lamina -1 6','Cervical flank lamina 1 6'],reason:'Each authored grid plate has 96 front + 96 back + 40 solidify-wall quads, or 464 triangles after triangulation. The exported neck-neck-plate has 8352 triangles (=18*464), and the recipe creates these objects in the listed order before build script groups and joins by scene order. Triangle-index ranges therefore map to native pieces if Blender join preserves that order; not independently confirmed from the .blend in this read-only diagnostic.'}};
await writeFile(`${dir}/crossing-localization-detail-v3.json`,JSON.stringify(out,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify(failures.map(({pitch,yaw,jawOpen,crossingTrianglePairs,contactPointCount,contactPointBounds,movingTriangleBounds,fixedTriangleBounds,topFixedTriangles})=>({pitch,yaw,jawOpen,crossingTrianglePairs,contactPointCount,contactPointBounds,movingTriangleBounds,fixedTriangleBounds,topFixedTriangles:topFixedTriangles.slice(0,8)})),null,2));
