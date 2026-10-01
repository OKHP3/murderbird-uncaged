// Read-only comparison of the exact GLBs; scope supplied from reviewed construction receipt.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const [sourcePath,candidatePath,scopePath,out]=process.argv.slice(2);
const hash=b=>createHash('sha256').update(b).digest('hex');
async function read(path){
 const bytes=await readFile(path); assert.equal(bytes.toString('ascii',0,4),'glTF');
 const length=bytes.readUInt32LE(12),doc=JSON.parse(bytes.toString('utf8',20,20+length));
 const bin=bytes.subarray(28+length),parents={};
 doc.nodes.forEach(n=>(n.children||[]).forEach(i=>parents[doc.nodes[i].name]=n.name));
 const size={5120:1,5121:1,5122:2,5123:2,5125:4,5126:4},width={SCALAR:1,VEC2:2,VEC3:3,VEC4:4,MAT4:16};
 function accessor(i){const a=doc.accessors[i],v=doc.bufferViews[a.bufferView];assert.ok(!a.sparse);const n=size[a.componentType]*width[a.type],stride=v.byteStride||n;let chunks=[];for(let j=0;j<a.count;j++){const start=(v.byteOffset||0)+(a.byteOffset||0)+j*stride;chunks.push(bin.subarray(start,start+n));}return {count:a.count,type:a.type,componentType:a.componentType,normalized:a.normalized||false,sha:hash(Buffer.concat(chunks))};}
 function mesh(i){return doc.meshes[i].primitives.map(p=>({mode:p.mode??4,material:doc.materials[p.material],indices:p.indices===undefined?null:accessor(p.indices),attributes:Object.fromEntries(Object.entries(p.attributes).sort().map(([k,v])=>[k,accessor(v)]))}));}
 return {sha:hash(bytes),materials:doc.materials.slice().sort((a,b)=>a.name.localeCompare(b.name)),nodes:new Map(doc.nodes.map(n=>[n.name,{parent:parents[n.name]||null,translation:n.translation||[0,0,0],rotation:n.rotation||[0,0,0,1],scale:n.scale||[1,1,1],matrix:n.matrix||null,extras:n.extras||{},mesh:n.mesh===undefined?null:mesh(n.mesh)}]))};
}
const scope=JSON.parse(await readFile(scopePath)),s=await read(sourcePath),c=await read(candidatePath);
const failures=[],changes=[],removed=[],added=[];
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
if(!same(s.materials,c.materials))failures.push('Material records differ');
for(const [name,a] of s.nodes){const b=c.nodes.get(name);if(!b){removed.push(name);continue;}
 const fields=Object.keys(a).filter(k=>!same(a[k],b[k]));if(fields.length)changes.push({name,fields});
 const permitted=scope.allowed?.[name]||[];
 for(const field of fields)if(!permitted.includes(field))failures.push(`${name}: undeclared ${field}`);
}
for(const [name,node]of c.nodes)if(!s.nodes.has(name)){added.push({name,parent:node.parent});if(scope.added?.[name]!==node.parent)failures.push(`${name}: undeclared new owner`);}
for(const name of removed)if(!scope.removed?.includes(name))failures.push(`${name}: undeclared removal`);
assert.deepEqual(removed.slice().sort(),(scope.removed||[]).slice().sort(),'Declared removals differ');
assert.deepEqual(added.map(n=>n.name).sort(),Object.keys(scope.added||{}).sort(),'Declared additions differ');
const result={scope:'Exact GLB attributes, indices, materials, extras, parents and rest transforms; not collision or artistic acceptance',source:sourcePath,candidate:candidatePath,sourceSHA256:s.sha,candidateSHA256:c.sha,sourceNodes:s.nodes.size,candidateNodes:c.nodes.size,unchangedNodes:s.nodes.size-removed.length-changes.length,changes,added,removed,failures,status:failures.length?'FAIL':'PASS'};
await writeFile(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({status:result.status,unchanged:result.unchangedNodes,changed:changes.length,added:added.length,removed:removed.length,failures}));if(failures.length)process.exitCode=1;
