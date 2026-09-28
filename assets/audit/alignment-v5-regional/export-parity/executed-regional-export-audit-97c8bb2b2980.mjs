#!/usr/bin/env node
/**
 * Direct GLB-to-GLB preservation audit for the regional composition.
 * It never opens Blender or changes an input. Geometry is loaded through the
 * same Three.js GLTFLoader path used by runtime validation.
 *
 * Required: --candidate GLB --out NEW_AUDIT_DIR
 * Optional: --base GLB --base-inventory JSON --guard GLB --guard-manifest JSON --talon GLB
 *           --talon-manifest JSON
 * Environment aliases: UNCAGED_CANDIDATE, UNCAGED_AUDIT, UNCAGED_BASE,
 * UNCAGED_BASE_INVENTORY, UNCAGED_GUARD, UNCAGED_GUARD_MANIFEST, UNCAGED_TALON,
 * UNCAGED_TALON_MANIFEST.
 */
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '..');
const DEFAULT_BASE = path.join(ROOT, '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9/murderbird-alignment-v5.glb');
const DEFAULT_GUARD = path.join(ROOT, '.local/alignment-limb-study/v5-fourth-limb-profile-study-05/murderbird-limb-profile-study.glb');
const DEFAULT_GUARD_MANIFEST = path.join(ROOT, '.local/alignment-limb-study/v5-fourth-limb-profile-study-05/manifest.json');
const BASE_SHA = '1e7febcc03d9f8d1a644580c8422b124403cf4e5768aa01df747e3d9b6af9f1e';
const GUARD_SHA = 'd7074699b566dac07d40b226865db766c48cb36be104b0845cec5c2ddf059268';
const BASE_INVENTORY_SHA = 'b9cfaf8cd7681396311d61537d2381ff6ef54f9cdc515c1aa1b77b34bd58beee';
const DEFAULT_BASE_INVENTORY = path.join(ROOT, '.local/alignment-composed-study/inputs/v5-sixth-1e7febcc03d9/alignment-inventory.json');
const TALON_NAMES = [1,2,3].flatMap(digit => ['left','right'].map(side => `${side} digit ${digit} tapered claw sheath`));
const REGIONAL_ERAS = 'maker,mechanic,builder';
const PIVOT_TOLERANCE = 1e-8;
const GEOMETRY_TOLERANCE = 1e-5;
const CELL = GEOMETRY_TOLERANCE;
const hash = bytes => createHash('sha256').update(bytes).digest('hex');

function argsFrom(argv) {
  const values = {};
  for (let i=2;i<argv.length;i++) {
    const item=argv[i];
    if (!item.startsWith('--')) throw new Error(`Unexpected argument: ${item}`);
    const key=item.slice(2);
    if (key==='help') { values.help=true; continue; }
    if (!argv[i+1] || argv[i+1].startsWith('--')) throw new Error(`Missing value for --${key}`);
    values[key]=argv[++i];
  }
  return values;
}
const cli=argsFrom(process.argv);
if (cli.help) {
  console.log('Usage: node scripts/verify-alignment-regional-export.mjs --candidate FILE --out NEW_DIR [--base FILE] [--guard FILE] [--guard-manifest FILE] [--talon FILE --talon-manifest FILE]');
  process.exit(0);
}
const candidatePath=path.resolve(cli.candidate||process.env.UNCAGED_CANDIDATE||'');
const outDir=path.resolve(cli.out||process.env.UNCAGED_AUDIT||'');
const basePath=path.resolve(cli.base||process.env.UNCAGED_BASE||DEFAULT_BASE);
const baseInventoryPath=path.resolve(cli['base-inventory']||process.env.UNCAGED_BASE_INVENTORY||DEFAULT_BASE_INVENTORY);
const guardPath=path.resolve(cli.guard||process.env.UNCAGED_GUARD||DEFAULT_GUARD);
const guardManifestPath=path.resolve(cli['guard-manifest']||process.env.UNCAGED_GUARD_MANIFEST||DEFAULT_GUARD_MANIFEST);
const talonPath=(cli.talon||process.env.UNCAGED_TALON)?path.resolve(cli.talon||process.env.UNCAGED_TALON):null;
const talonManifestPath=(cli['talon-manifest']||process.env.UNCAGED_TALON_MANIFEST)?path.resolve(cli['talon-manifest']||process.env.UNCAGED_TALON_MANIFEST):null;
assert.ok(cli.candidate||process.env.UNCAGED_CANDIDATE,'Provide --candidate or UNCAGED_CANDIDATE.');
assert.ok(cli.out||process.env.UNCAGED_AUDIT,'Provide --out as a new audit directory or UNCAGED_AUDIT.');
assert.equal(Boolean(talonPath),Boolean(talonManifestPath),'--talon and --talon-manifest must be supplied together.');
assert.notEqual(outDir,ROOT,'Output directory cannot be repository root.');

await mkdir(path.dirname(outDir),{recursive:true});
await mkdir(outDir,{recursive:false});
const sourceBytes=await readFile(fileURLToPath(import.meta.url));
const sourceSha=hash(sourceBytes);
const sourceSnapshot=path.join(outDir,`executed-regional-export-audit-${sourceSha.slice(0,12)}.mjs`);
await writeFile(sourceSnapshot,sourceBytes,{flag:'wx'});
assert.equal(hash(await readFile(sourceSnapshot)),sourceSha,'Write-once diagnostic source snapshot did not verify.');
const loaderPath=path.join(HERE,'load-rigid-validation.mjs');
const loaderBytes=await readFile(loaderPath);
const loaderIdentity={path:loaderPath,bytes:loaderBytes.byteLength,sha256:hash(loaderBytes)};

async function inputRecord(file,label) {
  assert.ok(file && path.isAbsolute(file),`${label}: absolute file path required`);
  const bytes=await readFile(file);
  return {path:file,bytes:bytes.byteLength,sha256:hash(bytes),bytesBuffer:bytes};
}
const [base,guard,candidate,...rest]=await Promise.all([
  inputRecord(basePath,'base GLB'),inputRecord(guardPath,'guard GLB'),
  inputRecord(candidatePath,'candidate GLB'),
  talonPath?inputRecord(talonPath,'talon GLB'):Promise.resolve(null),
  readFile(guardManifestPath),talonManifestPath?readFile(talonManifestPath):Promise.resolve(null),
]);
const talon=rest[0],guardManifestBytes=rest[1],talonManifestBytes=rest[2];
const baseInventoryBytes=await readFile(baseInventoryPath),baseInventorySha=hash(baseInventoryBytes);
assert.equal(base.sha256,BASE_SHA,'Preserved base GLB SHA does not match the frozen V5 sixth model.');
assert.equal(baseInventorySha,BASE_INVENTORY_SHA,'Frozen base inventory manifest SHA changed.');
const baseInventory=JSON.parse(baseInventoryBytes.toString('utf8'));
const inventoriedBaseGlb=(baseInventory.generatedFiles||[]).find(row=>row.sha256===base.sha256);
assert.ok(inventoriedBaseGlb,'Base inventory does not bind the exact supplied base GLB.');
assert.equal(guard.sha256,GUARD_SHA,'Guard GLB SHA does not match the frozen guard-study05 source.');
const guardManifest=JSON.parse(guardManifestBytes.toString('utf8'));
const guardOutput=guardManifest.outputs?.glb;
assert.ok(guardOutput,'Guard manifest lacks GLB output identity.');
assert.equal(guardOutput.sha256,guard.sha256,'Guard manifest and input GLB hashes differ.');
const removedNames=new Set(guardManifest.replacedObjects||[]);
const guardNames=(guardManifest.newObjects||[]).map(row=>row.name);
assert.equal(removedNames.size,26,'Expected exact 26-object guard replacement contract.');
assert.equal(guardNames.length,10,'Expected exact 10 guard-study05 source meshes.');
const INVENTORY_PARTS=new Map((baseInventory.parts||[]).map(row=>[row.name,row]));
const REPLACED_BASE_BATCHES=['left-thigh-leg-plate','left-shin-leg-plate','right-thigh-leg-plate','right-shin-leg-plate','left-foot-foot-plate','right-foot-foot-plate'];
const TALON_BASE_BATCHES=['left-digit-1-distal-foot-edge','left-digit-2-distal-foot-edge','left-digit-3-distal-foot-edge','right-digit-1-distal-foot-edge','right-digit-2-distal-foot-edge','right-digit-3-distal-foot-edge'];
for(const name of removedNames)assert.ok(INVENTORY_PARTS.has(name),`Guard native replacement is absent from frozen base inventory: ${name}`);
function inventorySourcesForBatch(owner,region,role){
  return (baseInventory.parts||[]).filter(row=>row.parent===owner&&row.region===region&&row.role===role&&['maker','mechanic','builder'].every(era=>row.eras?.includes(era))).map(row=>row.name);
}

let talonManifest=null;
if(talon){
  talonManifest=JSON.parse(talonManifestBytes.toString('utf8'));
  assert.equal(talonManifest.status,'local talon profile study 02; visual/contact review pending');
  const output=talonManifest.outputs?.glb||talonManifest.output?.glb;
  const declared=output?.sha256||talonManifest.outputGlbSha256;
  assert.equal(talon.sha256,declared,'Talon source manifest and input GLB hashes differ.');
  const names=(talonManifest.changedTalons||[]).map(row=>row.name);
  assert.deepEqual([...names].sort(),[...TALON_NAMES].sort(),'Talon manifest does not identify the exact six distal talon source meshes.');
}

function readGltfDoc(bytes){
  assert.equal(bytes.toString('ascii',0,4),'glTF','Input is not a GLB.');
  const jsonLength=bytes.readUInt32LE(12);
  return JSON.parse(bytes.subarray(20,20+jsonLength).toString('utf8'));
}
async function loadModel(record,label){
  const doc=readGltfDoc(record.bytesBuffer);
  const loaded=await loadRigidValidation(record.bytesBuffer);
  assert.ok(loaded.scene,`${label} has no runtime scene.`);
  loaded.scene.updateMatrixWorld(true);
  const pivotNames=new Set((doc.nodes||[]).filter(node=>node.mesh===undefined&&node.name).map(node=>node.name));
  const pivots=new Map();
  const meshes=[];
  loaded.scene.traverse(object=>{
    if(object.isMesh)meshes.push(object);
    if(pivotNames.has(object.name))pivots.set(object.name,object.matrixWorld.clone());
  });
  assert.ok(meshes.length,`${label} contains no loaded runtime meshes.`);
  return {doc,scene:loaded.scene,pivotNames,pivots,meshes};
}
const models={base:await loadModel(base,'base'),guard:await loadModel(guard,'guard'),candidate:await loadModel(candidate,'candidate')};
if(talon)models.talon=await loadModel(talon,'talon');
function matrixDelta(a,b){let max=0,component=-1;for(let i=0;i<16;i++){const d=Math.abs(a.elements[i]-b.elements[i]);if(d>max){max=d;component=i;}}return{max,component};}
const basePivotNames=[...models.base.pivotNames].sort();
assert.equal(basePivotNames.length,51,'Base GLB does not expose the expected 51 no-mesh pivot nodes.');
const candidatePivotRows=basePivotNames.map(name=>{
  const a=models.base.pivots.get(name),b=models.candidate.pivots.get(name);
  assert.ok(a&&b,`Missing pivot in direct GLB comparison: ${name}`);
  const delta=matrixDelta(a,b);
  return{name,maxComponentDelta:delta.max,maxComponentIndex:delta.component,baseWorldMatrix:a.toArray(),candidateWorldMatrix:b.toArray()};
});
const missingCandidatePivots=[...models.base.pivotNames].filter(name=>!models.candidate.pivotNames.has(name));
const extraCandidatePivots=[...models.candidate.pivotNames].filter(name=>!models.base.pivotNames.has(name));
const maxPivotDelta=Math.max(...candidatePivotRows.map(row=>row.maxComponentDelta));

function nearestRigidOwner(mesh,model){
  for(let object=mesh;object;object=object.parent)if(model.pivotNames.has(object.name))return object.name;
  return '(scene-root)';
}
function inheritedTags(mesh){
  const chain=[];for(let object=mesh;object;object=object.parent)chain.push(object);
  const tags={};for(const object of chain.reverse())Object.assign(tags,object.userData||{});
  return tags;
}
function materialName(mesh,index){
  const materials=Array.isArray(mesh.material)?mesh.material:[mesh.material];
  return materials[index]?.name||'(unnamed-material)';
}
function keyFor(owner,tags,material){return JSON.stringify([owner,tags.exteriorEras??tags.eras??'',tags.region??'',tags.surfaceRole??tags.role??'',material]);}
const canonicalName = name => String(name).toLowerCase().replace(/[^a-z0-9]/g,'');
function metadataMap(rows,extra={}){return new Map(rows.map(row=>[canonicalName(row.name),{...row,...extra}]));}
function addTriangle(group,points){
  group.triangles++;
  for(const p of points){
    group.vertexOccurrences++;
    const q=p.map(value=>Math.round(value*1e9)/1e9);
    const token=q.join(',');
    if(!group.unique.has(token))group.unique.set(token,q);
    for(let i=0;i<3;i++){group.min[i]=Math.min(group.min[i],q[i]);group.max[i]=Math.max(group.max[i],q[i]);}
  }
}
function extractGroups(model,excludeMeshNames=new Set(),includeMeshNames=null,metadata=new Map()){
  const groups=new Map();groups.untagged=[];groups.meshNames=[];
  for(const mesh of model.meshes){
    const sourceName=mesh.userData?.name||mesh.name;
    const tags={...inheritedTags(mesh),...(metadata.get(canonicalName(sourceName))||{})},owner=nearestRigidOwner(mesh,model);
    const missing=[];
    if(owner==='(scene-root)')missing.push('rigidOwner');
    if(!(tags.exteriorEras??tags.eras))missing.push('exteriorEras');
    if(!tags.region)missing.push('region');
    if(!(tags.surfaceRole??tags.role))missing.push('surfaceRole');
    if(missing.length){groups.untagged.push({mesh:mesh.name,missing});continue;}
    if([...excludeMeshNames].some(name=>canonicalName(name)===canonicalName(sourceName)))continue;
    if(includeMeshNames&&![...includeMeshNames].some(name=>canonicalName(name)===canonicalName(sourceName)))continue;
    const geometry=mesh.geometry,position=geometry.attributes.position,index=geometry.index;
    if(!position){groups.untagged.push({mesh:mesh.name,missing:['positionAttribute']});continue;}
    groups.meshNames.push(mesh.name);
    const elementCount=index?index.count:position.count;
    const ranges=geometry.groups?.length?geometry.groups:[{start:0,count:elementCount,materialIndex:0}];
    for(const range of ranges){
      const start=range.start??0,end=Math.min(elementCount,start+(Number.isFinite(range.count)?range.count:elementCount-start));
      const material=materialName(mesh,range.materialIndex??0),key=keyFor(owner,tags,material);
      if(!groups.has(key))groups.set(key,{key,owner,exteriorEras:tags.exteriorEras??tags.eras??'',region:tags.region??'',surfaceRole:tags.surfaceRole??tags.role??'',material,triangles:0,vertexOccurrences:0,unique:new Map(),min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity],sourceMeshes:[]});
      const group=groups.get(key);if(!group.sourceMeshes.includes(sourceName))group.sourceMeshes.push(sourceName);
      for(let i=start;i+2<end;i+=3){
        const points=[0,1,2].map(j=>{
          const vertex=index?index.getX(i+j):i+j;
          return new THREE.Vector3().fromBufferAttribute(position,vertex).applyMatrix4(mesh.matrixWorld).toArray();
        });
        addTriangle(group,points);
      }
    }
  }
  for(const group of groups.values())group.points=[...group.unique.values()];
  return groups;
}
function nearestDistances(source,target){
  if(!source.length||!target.length)return{maxDistance:null,unmatched:source.length};
  const cells=new Map();
  const cellOf=p=>p.map(v=>Math.floor(v/CELL));
  for(let i=0;i<target.length;i++){
    const c=cellOf(target[i]),key=c.join(',');if(!cells.has(key))cells.set(key,[]);cells.get(key).push(i);
  }
  let max=0,unmatched=0;
  for(const p of source){
    const c=cellOf(p);let best=Infinity;
    for(let x=-1;x<=1;x++)for(let y=-1;y<=1;y++)for(let z=-1;z<=1;z++){
      const rows=cells.get(`${c[0]+x},${c[1]+y},${c[2]+z}`)||[];
      for(const i of rows){const q=target[i],dx=p[0]-q[0],dy=p[1]-q[1],dz=p[2]-q[2],d=Math.hypot(dx,dy,dz);if(d<best)best=d;}
    }
    if(best===Infinity){unmatched++;continue;}max=Math.max(max,best);if(best>GEOMETRY_TOLERANCE)unmatched++;
  }
  return{maxDistance:max,unmatched};
}
function compareGroupMaps(expected,actual,label){
  const all=[...new Set([...expected.keys(),...actual.keys()])].sort();
  return all.map(key=>{
    const a=expected.get(key),b=actual.get(key),left=a?.points||[],right=b?.points||[];
    const forward=nearestDistances(left,right),reverse=nearestDistances(right,left);
    const triangleDelta=(b?.triangles||0)-(a?.triangles||0);
    const material=JSON.parse(key);
    const hasUnmatched=forward.unmatched>0||reverse.unmatched>0;
    return{key,owner:material[0],exteriorEras:material[1],region:material[2],surfaceRole:material[3],material:material[4],expectedTriangles:a?.triangles||0,actualTriangles:b?.triangles||0,triangleDelta,expectedUniqueVertices:left.length,actualUniqueVertices:right.length,expectedVertexOccurrences:a?.vertexOccurrences||0,actualVertexOccurrences:b?.vertexOccurrences||0,maxMatchedBidirectionalNearestDistanceMetres:Math.max(forward.maxDistance??0,reverse.maxDistance??0),maxBidirectionalNearestDistanceMetres:hasUnmatched?null:Math.max(forward.maxDistance??0,reverse.maxDistance??0),expectedPointsUnmatched:forward.unmatched,actualPointsUnmatched:reverse.unmatched,expectedBounds:a?{min:a.min,max:a.max}:null,actualBounds:b?{min:b.min,max:b.max}:null,expectedSourceMeshes:a?.sourceMeshes||[],actualSourceMeshes:b?.sourceMeshes||[],pass:!!a&&!!b&&triangleDelta===0&&forward.unmatched===0&&reverse.unmatched===0};
  });
}

const guardNamesSet=new Set(guardNames);
const batchContract=[];
for(const name of REPLACED_BASE_BATCHES){
  const mesh=models.base.meshes.find(item=>(item.userData?.name||item.name)===name);
  const owner=name.replace(/-leg-plate$/,'').replace(/-foot-plate$/,'');
  const region=/-foot-plate$/.test(name)?'foot':'leg';
  assert.ok(mesh,`Base GLB is missing exact replacement batch ${name}`);
  const tags=inheritedTags(mesh),actualOwner=nearestRigidOwner(mesh,models.base);
  assert.equal(actualOwner,owner,`Base replacement batch owner changed: ${name}`);
  assert.equal(tags.region,region,`Base replacement batch region changed: ${name}`);
  assert.equal(tags.surfaceRole,'plate',`Base replacement batch role changed: ${name}`);
  assert.equal(tags.exteriorEras,REGIONAL_ERAS,`Base replacement batch era tags changed: ${name}`);
  const nativeSources=inventorySourcesForBatch(owner,region,'plate');
  assert.ok(nativeSources.length,`Base native inventory has no source meshes for ${name}`);
  batchContract.push({batch:name,owner,region,role:'plate',nativeSourceMeshNames:nativeSources});
}
for(const name of TALON_BASE_BATCHES){
  const owner=name.replace(/-foot-edge$/,'');
  const nativeSources=inventorySourcesForBatch(owner,'foot','edge');
  assert.ok(nativeSources.length,`Base native inventory has no distal edge source for ${name}`);
  batchContract.push({batch:name,owner,region:'foot',role:'edge',nativeSourceMeshNames:nativeSources});
  if(talon){
    const mesh=models.base.meshes.find(item=>(item.userData?.name||item.name)===name);
    assert.ok(mesh,`Base GLB is missing exact talon batch ${name}`);
    const tags=inheritedTags(mesh);
    assert.equal(nearestRigidOwner(mesh,models.base),owner,`Base talon batch owner changed: ${name}`);
    assert.equal(tags.region,'foot',`Base talon batch region changed: ${name}`);
    assert.equal(tags.surfaceRole,'edge',`Base talon batch role changed: ${name}`);
    assert.equal(tags.exteriorEras,REGIONAL_ERAS,`Base talon batch era tags changed: ${name}`);
  }
}
const baseBatchExclusions=new Set([...REPLACED_BASE_BATCHES,...(talon?TALON_BASE_BATCHES:[])]);
const expectedBase=extractGroups(models.base,baseBatchExclusions);
const candidateAll=extractGroups(models.candidate);
const guardTags=metadataMap(guardManifest.newObjects,{exteriorEras:REGIONAL_ERAS});
const guardNew=extractGroups(models.guard,new Set(),guardNamesSet,guardTags);
function mergeGroupMaps(...maps){
  const result=new Map();
  for(const map of maps)for(const [key,src]of map){
    if(!result.has(key))result.set(key,{...src,triangles:0,vertexOccurrences:0,unique:new Map(),points:[],min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity],sourceMeshes:[]});
    const dst=result.get(key);dst.triangles+=src.triangles;dst.vertexOccurrences+=src.vertexOccurrences;
    for(const [token,p]of src.unique)dst.unique.set(token,p);
    for(const name of src.sourceMeshes)if(!dst.sourceMeshes.includes(name))dst.sourceMeshes.push(name);
    for(let i=0;i<3;i++){dst.min[i]=Math.min(dst.min[i],src.min[i]);dst.max[i]=Math.max(dst.max[i],src.max[i]);}
  }
  for(const group of result.values())group.points=[...group.unique.values()];
  return result;
}
const selectedGuardNames=new Set([...guardNew.values()].flatMap(group=>group.sourceMeshes));
const selectedGuardCanon=new Set([...selectedGuardNames].map(canonicalName));
const missingGuardNames=guardNames.filter(name=>!selectedGuardCanon.has(canonicalName(name)));
let expected=mergeGroupMaps(expectedBase,guardNew);
const baseGroupReport=compareGroupMaps(expected,candidateAll,'base+guard');
const guardKeys=[...guardNew.keys()];
const guardReplacementReport=baseGroupReport.filter(row=>guardKeys.includes(row.key));
const baseRetainedReport=baseGroupReport.filter(row=>!guardKeys.includes(row.key));

let talonReport=null,expectedWithTalon=null,missingTalonNames=[];
if(talon){
  const talonNameSet=new Set(TALON_NAMES);
  const expectedWithoutBaseTalons=extractGroups(models.base,new Set([...REPLACED_BASE_BATCHES,...TALON_BASE_BATCHES]));
  const sourceGuard=extractGroups(models.guard,new Set(),guardNamesSet,guardTags);
  const talonTags=metadataMap(talonManifest.changedTalons,{exteriorEras:REGIONAL_ERAS});
  const talonSource=extractGroups(models.talon,new Set(),talonNameSet,talonTags);
  const selectedTalonNames=new Set([...talonSource.values()].flatMap(group=>group.sourceMeshes).map(canonicalName));
  missingTalonNames=TALON_NAMES.filter(name=>!selectedTalonNames.has(canonicalName(name)));
  expectedWithTalon=mergeGroupMaps(expectedWithoutBaseTalons,sourceGuard,talonSource);
  talonReport=compareGroupMaps(expectedWithTalon,candidateAll,'base+guard+talon');
}

const controllingReport=talonReport||baseGroupReport;
const failures=controllingReport.filter(row=>!row.pass);
const coverage={base:expectedBase.untagged,candidate:candidateAll.untagged,guard:guardNew.untagged,talon:[]};
if(talonPath){
  const talonCheck=extractGroups(models.talon,new Set(),new Set(TALON_NAMES));
  coverage.talon=talonCheck.untagged;
}
const allMeshCoveragePass=Object.values(coverage).every(rows=>rows.length===0);
const expectedSourceCoveragePass=guardNew.size>0&&!missingGuardNames.length&&(!talonPath||!missingTalonNames.length);
function totals(groups){return{groupCount:groups.size,triangleCount:[...groups.values()].reduce((n,g)=>n+g.triangles,0),uniquePositionCount:[...groups.values()].reduce((n,g)=>n+g.unique.size,0),vertexOccurrenceCount:[...groups.values()].reduce((n,g)=>n+g.vertexOccurrences,0)};}
const inputs={base:{path:base.path,bytes:base.bytes,sha256:base.sha256,inventoryPath:baseInventoryPath,inventoryBytes:baseInventoryBytes.byteLength,inventorySha256:baseInventorySha},guard:{path:guard.path,bytes:guard.bytes,sha256:guard.sha256,manifestPath:guardManifestPath,manifestSha256:hash(guardManifestBytes)},candidate:{path:candidate.path,bytes:candidate.bytes,sha256:candidate.sha256},talon:talon&&{path:talon.path,bytes:talon.bytes,sha256:talon.sha256,manifestPath:talonManifestPath,manifestSha256:hash(talonManifestBytes)}};
const pivotPass=basePivotNames.length===models.candidate.pivotNames.size&&!missingCandidatePivots.length&&!extraCandidatePivots.length&&maxPivotDelta<=PIVOT_TOLERANCE;
const report={generatedAt:new Date().toISOString(),diagnosticSource:{path:sourceSnapshot,sha256:sourceSha,bytes:sourceBytes.byteLength},runtimeLoaderSource:loaderIdentity,inputs,method:{runtime:'Three.js GLTFLoader with the project runtime validator’s in-memory texture stripping; no Blender re-import.',coordinateSpace:'actual loaded GLTF scene world coordinates (metres, glTF Y-up); each mesh vertex transformed by its runtime matrixWorld.',pivotComparison:'named GLTF nodes without meshes; full 4x4 world matrices compared base vs candidate.',geometryComparison:'triangle counts are summed per owner/exteriorEras/region/surfaceRole/material group. Unique world-position point clouds are compared bidirectionally by nearest neighbor through a 27-cell spatial-hash neighborhood.',geometryToleranceMetres:GEOMETRY_TOLERANCE,pivotTolerance:PIVOT_TOLERANCE,duplicateHandling:'spatial clouds deduplicate positions after 1 nm rounding; triangle/material counts independently detect topology-count changes.',excludedBaseBatchedNodeNames:talon?[...REPLACED_BASE_BATCHES,...TALON_BASE_BATCHES]:REPLACED_BASE_BATCHES,excludedBaseNativeMeshNames:[...removedNames].sort(),baseBatchCompatibilityContract:batchContract,nativeReplacementRows:[...removedNames].sort().map(name=>INVENTORY_PARTS.get(name)),guardSourceMeshNames:guardNames,guardSourceTotals:totals(guardNew),optionalTalonMeshNames:talon?TALON_NAMES:[],limits:['Vertex-cloud equivalence is not triangle-topology identity; material-weighted triangle counts and bounds are reported separately.','The neighborhood test can establish sampled vertex-position proximity only; it does not prove surface normals, UVs, connectivity, collision clearance, forces, or silhouette acceptance.','All runtime meshes must inherit owner, era, region, and role tags; incomplete mesh coverage is reported and fails the result.','A direct GLB-to-GLB result supersedes Blender import-roundtrip coordinate parity only for the loaded GLTF scene; it is not an application/WebGL acceptance test.']},pivots:{baseCount:basePivotNames.length,candidateCount:models.candidate.pivotNames.size,missingCandidateNames:missingCandidatePivots,extraCandidateNames:extraCandidatePivots,maxWorldMatrixComponentDelta:maxPivotDelta,tolerance:PIVOT_TOLERANCE,pass:pivotPass,nodes:candidatePivotRows},basePlusGuard:{comparedAgainstCandidate:!talon,pass:baseGroupReport.every(row=>row.pass),expectedTotals:totals(expected),actualTotals:totals(candidateAll),groupCount:baseGroupReport.length,failedGroupCount:baseGroupReport.filter(row=>!row.pass).length,groups:baseGroupReport,guardReplacementGroups:guardReplacementReport,retainedBaseGroups:baseRetainedReport},basePlusGuardPlusTalon:talonReport?{controllingExpected:true,pass:talonReport.every(row=>row.pass),expectedTotals:totals(expectedWithTalon),actualTotals:totals(candidateAll),groupCount:talonReport.length,failedGroupCount:talonReport.filter(row=>!row.pass).length,groups:talonReport}:null,sourceCoverage:{pass:expectedSourceCoveragePass&&allMeshCoveragePass,missingGuardMeshNames:missingGuardNames,missingTalonMeshNames:talonPath?missingTalonNames:[],allRuntimeMeshesClassified:allMeshCoveragePass,unclassifiedMeshes:coverage},controllingComparison:talon?'base+guard+talon':'base+guard',status:failures.length===0&&pivotPass&&allMeshCoveragePass&&expectedSourceCoveragePass?'passed':'failed'};
const reportPath=path.join(outDir,`regional-export-parity-${candidate.sha256.slice(0,12)}.json`);
await writeFile(reportPath,`${JSON.stringify(report,null,2)}\n`,{flag:'wx'});
console.log(JSON.stringify({reportPath,status:report.status,inputs,pivots:{count:candidatePivotRows.length,maxWorldMatrixComponentDelta:maxPivotDelta,pass:report.pivots.pass},sourceGuardTriangleCount:totals(guardNew).triangleCount,controllingComparison:report.controllingComparison,comparison:{expected:totals(talon?expectedWithTalon:expected),actual:totals(candidateAll),failedGroupCount:failures.length,failedGroups:failures.slice(0,12).map(row=>({owner:row.owner,eras:row.exteriorEras,region:row.region,role:row.surfaceRole,material:row.material,expectedTriangles:row.expectedTriangles,actualTriangles:row.actualTriangles,maxDistance:row.maxBidirectionalNearestDistanceMetres,unmatched:[row.expectedPointsUnmatched,row.actualPointsUnmatched]}))},basePlusGuard:{comparedAgainstCandidate:report.basePlusGuard.comparedAgainstCandidate,failedGroupCount:report.basePlusGuard.failedGroupCount},talon:talonReport&&{pass:talonReport.every(row=>row.pass),failed:talonReport.filter(row=>!row.pass).length}},null,2));
if(report.status!=='passed')process.exitCode=1;
