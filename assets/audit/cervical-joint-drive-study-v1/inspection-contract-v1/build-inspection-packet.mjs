import {readFile,writeFile,access} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {applyInspectionPose} from '../../../../src/scene/inspection-pose.js';

const root=new URL('../../../../',import.meta.url);
const out=new URL('./',import.meta.url);
const packetPath='assets/audit/cervical-runtime-study-v1/expanded-runtime-poses/pose-snapshot.json';
const inventoryPath='assets/models/uncaged-alignment-v9/alignment-inventory.json';
const hash=b=>createHash('sha256').update(b).digest('hex');
const bytes=await readFile(new URL(packetPath,root));
assert.equal(hash(bytes),'1cb4a2f75ecae625a44c768ba543e9b99e1caa9791a3056e20f5d88bd73d2f26');
const original=JSON.parse(bytes), inventoryBytes=await readFile(new URL(inventoryPath,root));
const names=new Set([...JSON.parse(inventoryBytes).pivots.map(p=>p.name),'cervical-upper']);
assert.equal(names.size,52);
const initial=original.poses.find(p=>p.id==='inspection-open-0-separation-0');
const base=initial.pivotMatrices.filter(r=>names.has(r.name));
assert.equal(base.length,52);
const sourcePath='src/scene/inspection-pose.js';
const sourceBytes=await readFile(new URL(sourcePath,root));
const sourceArtifact={path:sourcePath,sha256:hash(sourceBytes)};
const poses=[],anchors=[];
for(let i=0;i<=40;i++){
  const open=i/40,nodes={},rest={};
  for(const row of base){
    const o=new THREE.Object3D();o.name=row.name;
    new THREE.Matrix4().fromArray(row.localMatrix).decompose(o.position,o.quaternion,o.scale);
    nodes[row.name]=o;rest[row.name]={position:o.position.clone()};
  }
  const roots=[];
  for(const row of base){
    if(nodes[row.parent])nodes[row.parent].add(nodes[row.name]);
    else{assert.deepEqual(row.localMatrix,row.worldMatrix);roots.push(nodes[row.name]);}
  }
  applyInspectionPose(nodes,rest,open,0);
  roots.forEach(o=>o.updateMatrixWorld(true));
  const rows=base.map(row=>{
    const o=nodes[row.name];return {name:row.name,path:row.path,parent:row.parent,kind:'transform',
      localMatrix:o.matrix.toArray(),worldMatrix:o.matrixWorld.toArray(),
      position:o.position.toArray(),quaternion:o.quaternion.toArray(),scale:o.scale.toArray()};
  });
  const id=`inspection-open-${open}-separation-0`;
  poses.push({id,open,separation:0,source:'derived using unchanged application inspection function',pivotMatrices:rows});
  if(i%10===0){
    const actual=original.poses.find(p=>p.id===id);assert(actual,id);
    const expected=new Map(actual.pivotMatrices.filter(r=>names.has(r.name)).map(r=>[r.name,r]));
    let maxLocal=0,maxWorld=0;
    for(const row of rows){
      const e=expected.get(row.name);assert(e);
      maxLocal=Math.max(maxLocal,...row.localMatrix.map((v,k)=>Math.abs(v-e.localMatrix[k])));
      maxWorld=Math.max(maxWorld,...row.worldMatrix.map((v,k)=>Math.abs(v-e.worldMatrix[k])));
    }
    assert(maxLocal<2e-7&&maxWorld<2e-7,JSON.stringify({id,maxLocal,maxWorld}));
    anchors.push({id,comparedPivots:52,maxLocalMatrixError:maxLocal,maxWorldMatrixError:maxWorld});
  }
}
const result={status:'41 derived inspection poses; five anchors match captured runtime across all52 native pivots',
  model:original.model,sourcePacket:{path:packetPath,sha256:hash(bytes)},applicationSource:sourceArtifact,
  inventory:{path:inventoryPath,sha256:hash(inventoryBytes)},coordinateConvention:'Browser column-major matrices; native mapping is C^-1 * browser * C, with C mapping native(X,Y,Z) to browser(X,Z,-Y).',
  limits:['Only five anchors are compared with recorded runtime. The36 intermediate poses are derived, not new browser captures.',
    'The52-pivot rest hierarchy must match before application to native geometry. No collision, containment or physical simulation result is implied.'],poses};
const packetOut=new URL('pose-snapshot.json',out),proofOut=new URL('anchor-proof.json',out);
for(const p of [packetOut,proofOut])await assert.rejects(access(p));
const output=Buffer.from(JSON.stringify(result,null,2)+'\n');
await writeFile(packetOut,output);
await writeFile(proofOut,JSON.stringify({status:'pass',applicationSource:sourceArtifact,
  generator:{path:'assets/audit/cervical-joint-drive-study-v1/inspection-contract-v1/build-inspection-packet.mjs',sha256:hash(await readFile(new URL(import.meta.url)))},
  packet:{path:'assets/audit/cervical-joint-drive-study-v1/inspection-contract-v1/pose-snapshot.json',sha256:hash(output),bytes:output.length},
  nodeVersion:process.version,threeRevision:THREE.REVISION,anchors,
  nativeMotion:'Breast rotates localZ by negative1.35*open. Cranial cover translates localZ by positive0.08*open.'},null,2)+'\n');
console.log(JSON.stringify({status:'pass',poseCount:poses.length,anchors,sha256:hash(output)}));
