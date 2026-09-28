/** Compare independent evaluated Blender position clouds with the loaded GLB.
 * Requires exact UNCAGED_NATIVE_SNAPSHOT / SHA256, UNCAGED_MODEL / SHA256,
 * and a new UNCAGED_AUDIT directory. Does not certify shading or movement.
 */
import assert from 'node:assert/strict';
import {readFile, writeFile, mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {gunzipSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as THREE from 'three';
import {loadRigidValidation} from './load-rigid-validation.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const TOLERANCE=1e-5;
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');

function nearest(source,target){
  const cells=new Map(),cell=p=>p.map(n=>Math.floor(n/TOLERANCE));
  for(const p of target){const k=cell(p).join(',');if(!cells.has(k))cells.set(k,[]);cells.get(k).push(p);}
  let unmatched=0,maxMatchedDistance=0;
  for(const p of source){
    const c=cell(p);let best=Infinity;
    for(let x=-1;x<=1;x++)for(let y=-1;y<=1;y++)for(let z=-1;z<=1;z++)
      for(const q of cells.get(`${c[0]+x},${c[1]+y},${c[2]+z}`)||[])
        best=Math.min(best,Math.hypot(...p.map((n,i)=>n-q[i])));
    if(best>TOLERANCE)unmatched++;else maxMatchedDistance=Math.max(maxMatchedDistance,best);
  }
  return {unmatched,maxMatchedDistance};
}

function compareGroups(expected,actual){
  return [...new Set([...Object.keys(expected),...Object.keys(actual)])].sort().map(key=>{
    const e=expected[key],a=actual[key];
    const forward=nearest(e?.points||[],a?.points||[]),reverse=nearest(a?.points||[],e?.points||[]);
    return {key,nativeTriangles:e?.triangles,runtimeTriangles:a?.triangles,
      nativeUniquePositions:e?.points.length,runtimeUniquePositions:a?.points.length,
      forward,reverse,pass:!!e&&!!a&&e.triangles===a.triangles&&!forward.unmatched&&!reverse.unmatched};
  });
}

const triangle={triangles:1,points:[[0,0,0],[1,0,0],[0,1,0]]};
const fixtures={identity:compareGroups({x:triangle},{x:triangle})[0].pass,
  displaced:!compareGroups({x:triangle},{x:{...triangle,points:[[0,0,0],[1.01,0,0],[0,1,0]]}})[0].pass,
  missing:!compareGroups({x:triangle},{})[0].pass,
  extra:!compareGroups({},{x:triangle})[0].pass,
  triangleCount:!compareGroups({x:triangle},{x:{...triangle,triangles:2}})[0].pass,
  changedTag:compareGroups({x:triangle},{y:triangle}).every(row=>!row.pass)};
assert.ok(Object.values(fixtures).every(Boolean));
for(const key of ['UNCAGED_NATIVE_SNAPSHOT','UNCAGED_NATIVE_SNAPSHOT_SHA256','UNCAGED_MODEL','UNCAGED_MODEL_SHA256','UNCAGED_AUDIT'])
  assert.ok(process.env[key],`Missing ${key}`);
const nativePath=path.resolve(ROOT,process.env.UNCAGED_NATIVE_SNAPSHOT),modelPath=path.resolve(ROOT,process.env.UNCAGED_MODEL);
const [nativeBytes,modelBytes]=await Promise.all([readFile(nativePath),readFile(modelPath)]);
assert.equal(hash(nativeBytes),process.env.UNCAGED_NATIVE_SNAPSHOT_SHA256);
assert.equal(hash(modelBytes),process.env.UNCAGED_MODEL_SHA256);
const native=JSON.parse(gunzipSync(nativeBytes));
assert.equal(hash(await readFile(path.resolve(ROOT,native.native.path))),native.native.sha256,'Native changed after snapshot');
const out=path.resolve(ROOT,process.env.UNCAGED_AUDIT);
assert.notEqual(out,ROOT);
await mkdir(path.dirname(out),{recursive:true});await mkdir(out,{recursive:false});
const source=await readFile(fileURLToPath(import.meta.url));
await writeFile(path.join(out,'executed-comparator.mjs'),source,{flag:'wx'});
const gltf=await loadRigidValidation(modelBytes);gltf.scene.updateMatrixWorld(true);
const pivotNames=new Set(Object.keys(native.pivots));
const pivots=Object.entries(native.pivots).map(([name,expected])=>{
  const object=gltf.scene.getObjectByName(name);
  const actualParent=object&&pivotNames.has(object.parent?.name)?object.parent.name:null;
  const maxDelta=object?Math.max(...object.matrixWorld.toArray().map((n,i)=>Math.abs(n-expected.matrix[i]))):null;
  return {name,nativeParent:expected.parent,runtimeParent:actualParent,maxWorldMatrixDelta:maxDelta,
    pass:!!object&&actualParent===expected.parent&&maxDelta<=1e-6};
});
const actual={};
gltf.scene.traverse(mesh=>{
  if(!mesh.isMesh)return;
  const chain=[];for(let obj=mesh;obj;obj=obj.parent)chain.push(obj);
  const tags=Object.assign({},...chain.toReversed().map(obj=>obj.userData||{}));
  const owner=chain.find(obj=>pivotNames.has(obj.name))?.name;
  const position=mesh.geometry.attributes.position,index=mesh.geometry.index;
  assert.ok(position,'No exported positions');
  const count=index?.count??position.count;
  const ranges=mesh.geometry.groups.length?mesh.geometry.groups:[{start:0,count,materialIndex:0}];
  for(const range of ranges){
    const materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];
    const material=materials[range.materialIndex||0];
    const identity=[owner,tags.exteriorEras,tags.region,tags.surfaceRole,material.name];
    assert.ok(identity.every(Boolean),`Unclassified ${mesh.name}`);
    const key=JSON.stringify(identity),end=Math.min(count,range.start+range.count);
    assert.equal((end-range.start)%3,0);
    const group=actual[key]??={triangles:0,unique:new Map()};
    group.triangles+=(end-range.start)/3;
    for(let i=range.start;i<end;i++){
      const p=new THREE.Vector3().fromBufferAttribute(position,index?index.getX(i):i).applyMatrix4(mesh.matrixWorld).toArray();
      assert.ok(p.every(Number.isFinite));group.unique.set(p.join(','),p);
    }
  }
});
for(const group of Object.values(actual)){group.points=[...group.unique.values()];delete group.unique;}
const groups=compareGroups(native.groups,actual);
const pass=groups.every(row=>row.pass)&&pivots.every(row=>row.pass);
const report={status:pass?'pass':'fail',native:native.native,
  nativeSnapshot:{path:path.relative(ROOT,nativePath),sha256:hash(nativeBytes)},
  runtime:{path:path.relative(ROOT,modelPath),sha256:hash(modelBytes),bytes:modelBytes.length},
  comparatorSha256:hash(source),loaderSha256:hash(await readFile(path.join(ROOT,'scripts/load-rigid-validation.mjs'))),
  toleranceMetres:TOLERANCE,fixtures,groups,pivots,
  summary:{passedGroups:groups.filter(row=>row.pass).length,totalGroups:groups.length,
    passedPivots:pivots.filter(row=>row.pass).length,totalPivots:pivots.length,
    nativeTriangles:Object.values(native.groups).reduce((sum,group)=>sum+group.triangles,0),
    runtimeTriangles:Object.values(actual).reduce((sum,group)=>sum+group.triangles,0)},
  limits:['Position clouds, triangle totals, material names, era/region/role/owner tags and known rigid pivots only.',
    'Does not certify topology, triangle winding, normals, shader interpretation, UVs, moving clearance or artistic likeness.',
    'Native and export share authoring inputs but use independent geometry-reading paths.']};
await writeFile(path.join(out,'geometry-parity.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:report.status,...report.summary}));assert.ok(pass,'Native/export geometry mismatch');
