/** Independent exported-geometry comparison: v6 body plus the reviewed regional batches.
 * Run with UNCAGED_MODEL, UNCAGED_MODEL_SHA256 and a new UNCAGED_AUDIT directory.
 * Compares material-tagged triangle counts, bidirectional position clouds and pivots.
 * Does not establish topology equivalence, moving clearance or artistic acceptance.
 */
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import * as THREE from 'three';
import {loadRigidValidation} from './load-rigid-validation.mjs';

const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const TOLERANCE=1e-5;
const hash=b=>createHash('sha256').update(b).digest('hex');
const stable=v=>Array.isArray(v)?`[${v.map(stable).join(',')}]`:v&&typeof v==='object'?`{${Object.keys(v).sort().map(k=>`${JSON.stringify(k)}:${stable(v[k])}`).join(',')}}`:JSON.stringify(v);
const REGIONAL_BATCHES=new Set(['left','right'].flatMap(side=>[
  JSON.stringify([`${side}-thigh`,'leg','plate']),
  JSON.stringify([`${side}-shin`,'leg','plate']),
  JSON.stringify([`${side}-foot`,'foot','plate']),
  JSON.stringify([`${side}-foot`,'foot','edge']),
  ...[1,2,3].map(n=>JSON.stringify([`${side}-digit-${n}-distal`,'foot','edge'])),
]));

async function load(relative,expected){
  const filename=path.resolve(ROOT,relative),bytes=await readFile(filename);
  assert.equal(hash(bytes),expected,`Changed input: ${filename}`);
  const doc=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString());
  const gltf=await loadRigidValidation(bytes);gltf.scene.updateMatrixWorld(true);
  const pivotNames=new Set(doc.nodes.filter(n=>n.mesh===undefined&&n.name).map(n=>n.name));
  const pivots=new Map([...pivotNames].map(name=>{
    const object=gltf.scene.getObjectByName(name);assert.ok(object,`Missing pivot ${name}`);
    return [name,{parent:object.parent?.name||null,matrix:object.matrixWorld.toArray()}];
  }));
  const groups=new Map(),meshes=[];
  gltf.scene.traverse(mesh=>{
    if(!mesh.isMesh)return;
    const chain=[];for(let o=mesh;o;o=o.parent)chain.push(o);
    const tags=Object.assign({},...chain.toReversed().map(o=>o.userData||{}));
    const owner=chain.find(o=>pivotNames.has(o.name))?.name;
    const eras=tags.exteriorEras,region=tags.region,role=tags.surfaceRole;
    assert.ok(owner&&eras&&region&&role,`Unclassified mesh ${mesh.name}`);
    const position=mesh.geometry.attributes.position,index=mesh.geometry.index;
    assert.ok(position,`No positions in ${mesh.name}`);
    const count=index?.count??position.count;
    const ranges=mesh.geometry.groups.length?mesh.geometry.groups:[{start:0,count,materialIndex:0}];
    for(const range of ranges){
      const materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];
      const material=materials[range.materialIndex||0];
      const raw=doc.materials.find(m=>m.name===material.name);assert.ok(raw,`Unknown material ${material.name}`);
      const properties={...raw};delete properties.name;
      const signature=hash(Buffer.from(stable(properties)));
      const key=JSON.stringify([owner,eras,region,role,signature]);
      if(!groups.has(key))groups.set(key,{key,owner,eras,region,role,material:properties,triangles:0,occurrences:0,unique:new Map()});
      const group=groups.get(key),end=Math.min(count,range.start+range.count);
      assert.equal((end-range.start)%3,0,`Non-triangle range ${mesh.name}`);
      group.triangles+=(end-range.start)/3;
      for(let i=range.start;i<end;i++){
        const p=new THREE.Vector3().fromBufferAttribute(position,index?index.getX(i):i).applyMatrix4(mesh.matrixWorld).toArray();
        assert.ok(p.every(Number.isFinite),'Nonfinite exported position');
        const rounded=p.map(n=>Math.round(n*1e9)/1e9);group.unique.set(rounded.join(','),rounded);group.occurrences++;
      }
    }
    meshes.push(mesh.name);
  });
  for(const g of groups.values())g.points=[...g.unique.values()];
  return{identity:{path:path.relative(ROOT,filename),bytes:bytes.length,sha256:hash(bytes)},groups,pivots,meshes};
}

function nearest(source,target){
  const cells=new Map(),cell=p=>p.map(n=>Math.floor(n/TOLERANCE));
  for(const p of target){const k=cell(p).join(',');if(!cells.has(k))cells.set(k,[]);cells.get(k).push(p);}
  let unmatched=0,maxMatchedDistance=0;
  for(const p of source){
    const c=cell(p);let best=Infinity;
    for(let x=-1;x<=1;x++)for(let y=-1;y<=1;y++)for(let z=-1;z<=1;z++)
      for(const q of cells.get(`${c[0]+x},${c[1]+y},${c[2]+z}`)||[])best=Math.min(best,Math.hypot(...p.map((n,i)=>n-q[i])));
    if(best>TOLERANCE)unmatched++;else maxMatchedDistance=Math.max(maxMatchedDistance,best);
  }
  return{unmatched,maxMatchedDistance};
}

function compare(expected,actual){
  return [...new Set([...expected.keys(),...actual.keys()])].sort().map(key=>{
    const e=expected.get(key),a=actual.get(key),forward=nearest(e?.points||[],a?.points||[]),reverse=nearest(a?.points||[],e?.points||[]);
    return{key,expectedSource:e?.expectedSource,expectedTriangles:e?.triangles,actualTriangles:a?.triangles,
      expectedUniquePositions:e?.points.length,actualUniquePositions:a?.points.length,
      expectedVertexOccurrences:e?.occurrences,actualVertexOccurrences:a?.occurrences,forward,reverse,
      pass:!!e&&!!a&&e.triangles===a.triangles&&e.occurrences===a.occurrences&&forward.unmatched===0&&reverse.unmatched===0};
  });
}

function comparePivots(base,candidate){
  return [...new Set([...base.keys(),...candidate.keys()])].sort().map(name=>{
    const b=base.get(name),c=candidate.get(name);
    const maxDelta=b&&c?Math.max(...b.matrix.map((v,i)=>Math.abs(v-c.matrix[i]))):null;
    return{name,baseParent:b?.parent,candidateParent:c?.parent,maxWorldMatrixDelta:maxDelta,
      pass:!!b&&!!c&&b.parent===c.parent&&maxDelta<=1e-8};
  });
}
const fixtureGroup={triangles:1,occurrences:3,points:[[0,0,0],[1,0,0],[0,1,0]]};
const groupFixture=(key,value)=>new Map([[key,value]]);
const pivotFixture={parent:'body',matrix:new THREE.Matrix4().toArray()};
const fixtures={identity:nearest([[0,0,0]],[[0,0,0]]).unmatched===0,
  movedVertex:nearest([[0,0,0]],[[.001,0,0]]).unmatched===1,
  missingPoint:nearest([[0,0,0]],[]).unmatched===1,
  missingGroup:compare(groupFixture('x',fixtureGroup),new Map())[0].pass===false,
  triangleCount:compare(groupFixture('x',fixtureGroup),groupFixture('x',{...fixtureGroup,triangles:2}))[0].pass===false,
  occurrenceCount:compare(groupFixture('x',fixtureGroup),groupFixture('x',{...fixtureGroup,occurrences:6}))[0].pass===false,
  materialOrEraKey:compare(groupFixture('original-key',fixtureGroup),groupFixture('changed-key',fixtureGroup)).every(r=>!r.pass),
  pivotMoved:comparePivots(groupFixture('foot',pivotFixture),groupFixture('foot',{...pivotFixture,matrix:new THREE.Matrix4().makeTranslation(.01,0,0).toArray()}))[0].pass===false,
  pivotReparented:comparePivots(groupFixture('foot',pivotFixture),groupFixture('foot',{...pivotFixture,parent:'other'}))[0].pass===false,
  pivotMissing:comparePivots(groupFixture('foot',pivotFixture),new Map())[0].pass===false,
};
assert.ok(Object.values(fixtures).every(Boolean),'Comparator fixture failed');
assert.ok(process.env.UNCAGED_MODEL&&process.env.UNCAGED_MODEL_SHA256&&process.env.UNCAGED_AUDIT,'Supply exact candidate and a new audit directory');
const out=path.resolve(ROOT,process.env.UNCAGED_AUDIT);assert.notEqual(out,ROOT);
await mkdir(path.dirname(out),{recursive:true});await mkdir(out,{recursive:false});
const source=await readFile(fileURLToPath(import.meta.url));await writeFile(path.join(out,'executed-v7-export-comparison.mjs'),source,{flag:'wx'});
const [base,regional,candidate]=await Promise.all([
  load('assets/models/uncaged-alignment-v6/murderbird-alignment-v6.glb','ce35024adda89681a0f37e7018e2563a74af67cd06558a887222df87b78a87fe'),
  load('assets/models/uncaged-alignment-v5-regional/candidate-04/murderbird-v5-sixth-guard-talon-study.glb','829d416a9eb65226543ce619ffc37ce8f135f3f8869ffb291b65da2a5c664c67'),
  load(process.env.UNCAGED_MODEL,process.env.UNCAGED_MODEL_SHA256),
]);
const isRegional=g=>REGIONAL_BATCHES.has(JSON.stringify([g.owner,g.region,g.role]));
const expected=new Map([...base.groups].filter(([,g])=>!isRegional(g)).map(([k,g])=>[k,{...g,expectedSource:'v6'}]));
const regionalSelected=[...regional.groups].filter(([,g])=>isRegional(g));
const matchedContracts=new Set(regionalSelected.map(([,g])=>JSON.stringify([g.owner,g.region,g.role])));
assert.deepEqual([...matchedContracts].sort(),[...REGIONAL_BATCHES].sort(),'Regional source does not contain all exact replacement batches');
for(const [k,g]of regionalSelected){assert.equal(g.eras,'maker,mechanic,builder');assert.ok(!expected.has(k));expected.set(k,{...g,expectedSource:'regional-candidate04'});}
const rows=compare(expected,candidate.groups);
const pivotRows=comparePivots(base.pivots,candidate.pivots);
const pass=rows.every(r=>r.pass)&&pivotRows.every(r=>r.pass);
const report={status:pass?'pass':'fail',candidate:candidate.identity,base:base.identity,regional:regional.identity,
  sourceSha256:hash(source),loaderSha256:hash(await readFile(path.join(ROOT,'scripts/load-rigid-validation.mjs'))),
  toleranceMetres:TOLERANCE,fixtures,regionalBatchContract:[...REGIONAL_BATCHES].map(v=>JSON.parse(v)),
  groups:rows,pivots:pivotRows,summary:{passedGroups:rows.filter(r=>r.pass).length,totalGroups:rows.length,
    passedPivots:pivotRows.filter(r=>r.pass).length,totalPivots:pivotRows.length,
    expectedTriangles:[...expected.values()].reduce((n,g)=>n+g.triangles,0),actualTriangles:[...candidate.groups.values()].reduce((n,g)=>n+g.triangles,0)},
  limits:['Direct exported position clouds, material groups and pivots only; not topology/normal/UV equivalence.','Native object names and modifier stacks are checked by the separate composer receipt, not by this aggregated exported-geometry comparison.','The regional source already has its own native/source parity receipt; this comparison does not replace native transfer checks.','No moving collision, physical simulation, browser appearance or artistic acceptance.']};
await writeFile(path.join(out,'export-comparison.json'),JSON.stringify(report,null,2)+'\n',{flag:'wx'});
console.log(JSON.stringify({status:report.status,...report.summary}));assert.ok(pass,'V7 export differs from the exact selective composition');
