import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const ROOT=resolve(process.argv[2]||process.cwd());
const THREE=await import(pathToFileURL(resolve(ROOT,'node_modules/three/build/three.module.js')));
const {loadRigidValidation}=await import(pathToFileURL(resolve(ROOT,'scripts/load-rigid-validation.mjs')));
const {createCervicalArticulation}=await import(pathToFileURL(resolve(ROOT,'src/scene/cervical-articulation.js')));
const input=resolve(ROOT,'assets/audit/whole-character-v31/attempt-form02/export');
const out=resolve(input,'actual-runtime-roundtrip');
const receipt=JSON.parse(await readFile(resolve(input,'export-receipt.json'),'utf8'));
const native=JSON.parse(await readFile(resolve(input,'native-export-input.json'),'utf8'));
const bytes=await readFile(resolve(ROOT,receipt.glb.path));const hash=data=>createHash('sha256').update(data).digest('hex');assert.equal(hash(bytes),receipt.glb.sha256);
const gltf=await loadRigidValidation(bytes);assert.equal(gltf.animations.length,0);
const model=gltf.scene;model.updateMatrixWorld(true);
const json=JSON.parse(bytes.subarray(20,20+bytes.readUInt32LE(12)).toString('utf8'));
const C=new THREE.Matrix4().set(1,0,0,0, 0,0,1,0, 0,-1,0,0, 0,0,0,1);const inv=C.clone().invert();
const deltas=[];let loadedMeshes=0,loadedVertices=0;
model.traverse(o=> {
 if(o.isMesh){loadedMeshes++;for(const attribute of Object.values(o.geometry.attributes))for(const value of attribute.array)assert.ok(Number.isFinite(value));loadedVertices+=o.geometry.attributes.position.count;}
 const id=gltf.parser.associations.get(o)?.nodes;if(id===undefined)return;
 const name=json.nodes[id].name;const expected=new THREE.Matrix4().set(...native.nodes[name].worldNative.flat());expected.premultiply(C).multiply(inv);
 const delta=Math.max(...expected.elements.map((value,i)=>Math.abs(value-o.matrixWorld.elements[i])));assert.ok(delta<1e-6,`${name} native/GLB world delta ${delta}`);deltas.push({name,maximumWorldMatrixDelta:delta});
});
assert.equal(loadedMeshes,receipt.counts.meshObjects);assert.equal(deltas.length,receipt.counts.glbNodes);
const names=['body','neck','head'];const nodes=Object.fromEntries(names.map(name=>[name,model.getObjectByName(name)]));const rest=Object.fromEntries(names.map(name=>[name,{position:nodes[name].position.clone(),rotation:nodes[name].rotation.clone()}]));
const layout=JSON.parse(nodes.body.userData.cervicalLayoutV2);assert.deepEqual(layout.pitchJoints,['neck','cervical-mid-a','cervical-mid-b','cervical-upper']);
const cervical=createCervicalArticulation(model,nodes,rest);const saved=cervical.capturePose();const origins=cervical.joints.map(joint=>joint.position.clone());
const headRest=nodes.head.quaternion.clone();const samples=[];
for(const [label,pitch,yaw,headPitch,headYaw] of [['maker',-.14,-.45,0,0],['attention',.08,.288,-.05,.312],['contact',.65,0,-.731,0]]) {
 cervical.restoreAttachments();cervical.setPitch(pitch,yaw,0);nodes.head.quaternion.copy(headRest).multiply(new THREE.Quaternion().setFromEuler(new THREE.Euler(headPitch,headYaw,0)));model.updateMatrixWorld(true);
 let positionError=0,unitBasisError=0,orthogonalityError=0;
 cervical.joints.forEach((joint,i)=> {
  positionError=Math.max(positionError,joint.position.distanceTo(origins[i]));const cols=[0,1,2].map(axis=>new THREE.Vector3().setFromMatrixColumn(joint.matrixWorld,axis));unitBasisError=Math.max(unitBasisError,...cols.map(c=>Math.abs(c.length()-1)));orthogonalityError=Math.max(orthogonalityError,Math.abs(cols[0].dot(cols[1])),Math.abs(cols[1].dot(cols[2])),Math.abs(cols[0].dot(cols[2])));assert.ok(Math.abs(joint.quaternion.length()-1)<1e-7);
 });
 assert.ok(positionError<1e-12 && unitBasisError<1e-6 && orthogonalityError<1e-6);assert.ok(Math.abs(cervical.pitch-pitch)<1e-9);
 samples.push({label,totalPitch:pitch,rootYaw:yaw,headPitch,headYaw,pitchSum:cervical.pitch,maximumPositionError:positionError,maximumUnitBasisError:unitBasisError,maximumOrthogonalityError:orthogonalityError,joints:cervical.metrics().pitchJoints});
 cervical.restorePose(saved);saved.forEach(({node,position,quaternion})=>{assert.deepEqual(node.position.toArray(),position.toArray());assert.deepEqual(node.quaternion.toArray(),quaternion.toArray());});
}
assert.equal(hash(await readFile(resolve(ROOT,receipt.glb.path))),receipt.glb.sha256);assert.equal(hash(await readFile(resolve(ROOT,receipt.native.path))),receipt.native.sha256);
const result={status:'PASS bounded actual-GLB attachment roundtrip; no armor clearance or appearance acceptance',nativeSHA256:receipt.native.sha256,glbSHA256:receipt.glb.sha256,glbBytes:bytes.length,sourceSHA256:hash(await readFile(fileURLToPath(import.meta.url))),runtimeSourceSHA256:hash(await readFile(resolve(ROOT,'src/scene/cervical-articulation.js'))),counts:{loadedMeshes,loadedVertices,nativeWorldMatricesCompared:deltas.length},maximumWorldMatrixDelta:Math.max(...deltas.map(d=>d.maximumWorldMatrixDelta)),checks:{actualGLTFLoader:true,allLoadedVertexAttributesFinite:true,worldRestsMatchNativeWithin1eMinus6:true,allChainPositionsFixed:true,unitRigidJointBases:true,pitchSumCorrect:true,poseRestoreExact:true,originalFilesUnmodified:true},cervicalLayoutV2:layout,samples,contactAdjustments:receipt.contactAdjustments,limits:['Texture bindings stripped only from the in-memory loader input by existing loadRigidValidation helper; original GLB is unchanged.','Maker/attention/contact angle samples validate transforms, not armor clearance, era mechanism fit, WebGL appearance or owner acceptance.','Attention sample is a bounded simultaneous yaw/pitch contract sample, not a claim that every dynamic attention state was played.']};
await writeFile(resolve(out,'roundtrip-receipt.json'),JSON.stringify(result,null,2)+'\n');await writeFile(resolve(out,'world-matrix-deltas.json'),JSON.stringify(deltas,null,2)+'\n');console.log(JSON.stringify(result,null,2));
