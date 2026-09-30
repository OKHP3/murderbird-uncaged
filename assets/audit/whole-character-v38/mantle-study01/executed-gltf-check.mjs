// node FILE GLB HELPER THREE_DIRECTORY OUTPUT; read-only exported loader/profile check.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';
const [input,helper,threeDirectory,output]=process.argv.slice(2);
assert(!fs.existsSync(output),'Write-once validation output already exists');
const {GLTFLoader}=await import(pathToFileURL(`${threeDirectory}/examples/jsm/loaders/GLTFLoader.js`));
const {applyEraFinishes}=await import(pathToFileURL(helper));
const raw=fs.readFileSync(input),buffer=raw.buffer.slice(raw.byteOffset,raw.byteOffset+raw.byteLength);
const gltf=await new GLTFLoader().parseAsync(buffer,'');
const materials=new Set(),plates=[];const visibility=[];
gltf.scene.traverse(object=>{visibility.push([object,object.visible]);if(object.isMesh){for(const material of Array.isArray(object.material)?object.material:[object.material])materials.add(material);if(typeof object.userData.v38MantleEnvelope==='string')plates.push(object);}});
assert.equal(plates.length,52);
const savedProfiles=new Map(plates.map(object=>[object.material,object.material.userData.eraFinishes]));
const reports={};const near=(a,b)=>assert(Math.abs(a-b)<1e-6,`${a} != ${b}`);
for(const era of ['maker','mechanic','builder']){
 const report=applyEraFinishes(gltf.scene,era);assert.equal(report.invalidMaterials,0);reports[era]=report;
 for(const object of plates){const material=object.material;const profile=material.userData.eraFinishes[era];assert(profile,'Reformed neck guard must be eligible in all inherited eras');near(material.color.r,profile.baseColorFactor[0]);near(material.color.g,profile.baseColorFactor[1]);near(material.color.b,profile.baseColorFactor[2]);near(material.metalness,profile.metallicFactor);near(material.roughness,profile.roughnessFactor);const emissive=profile.emissiveFactor??[0,0,0];near(material.emissive.r,emissive[0]);near(material.emissive.g,emissive[1]);near(material.emissive.b,emissive[2]);assert.equal(material.transparent,false);assert.equal(material.opacity,1);}
 for(const [object,visible] of visibility)assert.equal(object.visible,visible);
 assert(plates.every(object=>object.material.userData.eraFinishes===savedProfiles.get(object.material)),'Profile objects must remain the actual loaded material references');
}
fs.writeFileSync(output,JSON.stringify({status:'PASS exported GLTFLoader -> applyEraFinishes for 52 rigid mantle plates, all three inherited eras',input,helper,threeDirectory,uniqueLoadedMaterials:materials.size,reports,scope:'Actual exported material extras arrive as objects; standard linear PBR values apply, shared references and visibility persist. No rendered browser/likeness/motion acceptance.'},null,2)+'\n');
console.log(JSON.stringify(reports));
