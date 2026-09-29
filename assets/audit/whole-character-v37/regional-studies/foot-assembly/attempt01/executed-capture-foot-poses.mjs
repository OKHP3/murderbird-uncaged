/** Fresh actual final-composition runtime matrices. Exact model hash required. */
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const R='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged';
const {loadRigidValidation}=await import(pathToFileURL(resolve(R,'scripts/load-rigid-validation.mjs')));
const {createEraMotion}=await import(pathToFileURL(resolve(R,'src/scene/era-motion.js')));
const {createEraController}=await import(pathToFileURL(resolve(R,'src/scene/era-controller.js')));
const args=process.argv.slice(2),opt=k=>{const i=args.indexOf(k);assert(i>=0,'Required '+k);return args[i+1];};
const modelPath=opt('--model'),outputPath=opt('--output'),expectedSHA=opt('--expected-sha');
const bytes=await readFile(resolve(R,modelPath));
const sha=b=>createHash('sha256').update(b).digest('hex');assert.equal(sha(bytes),expectedSHA);
const names=['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield','cervical-mid-a','cervical-mid-b','cervical-upper'];
const poses=[];
async function fresh(era){const model=(await loadRigidValidation(bytes)).scene;model.updateMatrixWorld(true);const exportedTransforms=[];model.traverse(o=>{if(o.name&&!o.isMesh)exportedTransforms.push({name:o.name,worldMatrix:o.matrixWorld.elements.slice()});});const nodes=Object.fromEntries(names.map(n=>[n,model.getObjectByName(n)]));assert(Object.values(nodes).every(Boolean));const rest=Object.fromEntries(names.map(n=>[n,{position:nodes[n].position.clone(),rotation:nodes[n].rotation.clone()}]));const motion=createEraMotion(model,nodes,rest),controller=createEraController({seed:927});controller.setEra(era);controller.reset();motion.resetEra(era);let frame=0;const step=()=>{const state=controller.update(1/60,motion.feedback());for(const n of names){nodes[n].position.copy(rest[n].position);nodes[n].rotation.copy(rest[n].rotation);}motion.tick(1/60,state);model.updateMatrixWorld(true);frame++;return {state,metrics:motion.metrics(),frame};};return {model,nodes,motion,controller,step,exportedTransforms};}
function capture(r,id,f){const transforms=[];r.model.traverse(o=>{if(o.name&&!o.isMesh){assert(o.matrixWorld.elements.every(Number.isFinite));transforms.push({name:o.name,worldMatrix:o.matrixWorld.elements.slice()});}});poses.push({id,frame:f?.frame??0,controller:f?.state??null,metrics:f?.metrics??null,transforms:id==='exported-rest'?r.exportedTransforms:transforms});}
let r=await fresh('maker');capture(r,'exported-rest');
r=await fresh('builder');r.step();assert.equal(r.controller.requestClawAction(),true);let f,found=false;
for(let i=0;i<900;i++){f=r.step();const c=f.state.clawAction;if(c?.stage==='scrape'&&c.phase>=.5){capture(r,'advanced-claw-scrape',f);found=true;break;}}assert(found,'actual claw scrape unavailable');
r=await fresh('builder');r.step();assert.equal(r.controller.requestPowerMove('jump'),true);found=false;
for(let i=0;i<600;i++){f=r.step();const p=f.metrics.powerMove;if(p?.stage==='landing'&&p.phase>=.74){capture(r,'advanced-jump-landing',f);found=true;break;}}assert(found,'actual jump landing unavailable');
const sourceHashes={};for(const p of ['scripts/load-rigid-validation.mjs','src/scene/era-motion.js','src/scene/era-controller.js','src/scene/rigid-leg-kinematics.js','src/scene/cervical-articulation.js','src/scene/presence-state.js','package-lock.json'])sourceHashes[p]=sha(await readFile(resolve(R,p)));
await writeFile(resolve(R,outputPath),JSON.stringify({sourceGLBPath:modelPath,sourceGLBSHA256:sha(bytes),sourceHashes,coordinateConvention:'browser=(nativeX,nativeZ,-nativeY); native world=C^-1*runtimeWorld*C; column-major matrices',scope:'Three fresh actual GLB states: exported rest, Advanced claw scrape at phase>=.5, Advanced jump landing at phase>=.74. No procedural hardware or continuous motion claim.',poses},null,2)+'\n',{flag:'wx'});assert.equal(sha(await readFile(resolve(R,modelPath))),expectedSHA);console.log('Captured',poses.map(p=>({id:p.id,claw:p.metrics?.clawAction,power:p.metrics?.powerMove})));
