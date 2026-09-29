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
let r=await fresh('maker');capture(r,'exported-rest');capture(r,'maker-rest',r.step());r.controller.setArticulation('leg',1);let f;for(let i=0;i<120;i++)f=r.step();capture(r,'maker-leg-peak',f);
r=await fresh('mechanic');r.controller.requestRoutine();const seen=new Set();for(let i=0;i<1800;i++){f=r.step();const s=f.metrics.mechanicalStage;if(['load','release','settle','dwell'].includes(s)&&f.metrics.mechanicalPhase>(s==='load'?.14:.45)&&!seen.has(s)){seen.add(s);capture(r,'mechanic-'+s,f);}if(seen.size===4)break;}assert.equal(seen.size,4);
r=await fresh('builder');r.controller.requestReach({x:0,y:.25});let found=false;for(let i=0;i<1800;i++){f=r.step();if(f.state.state==='contact'&&f.metrics.contact){capture(r,'advanced-contact',f);found=true;break;}}assert(found);
r=await fresh('builder');r.step();r.controller.requestPowerMove('jump');const jumps=new Set();for(let i=0;i<600;i++){f=r.step();const s=f.metrics.powerMove?.stage;if(['load','landing'].includes(s)&&!jumps.has(s)){jumps.add(s);capture(r,'advanced-jump-'+s,f);}if(jumps.size===2)break;}assert.equal(jumps.size,2);
const sourceHashes={};for(const p of ['scripts/load-rigid-validation.mjs','src/scene/era-motion.js','src/scene/era-controller.js','src/scene/rigid-leg-kinematics.js','src/scene/cervical-articulation.js','src/scene/presence-state.js','package-lock.json'])sourceHashes[p]=sha(await readFile(resolve(R,p)));
await writeFile(resolve(R,outputPath),JSON.stringify({sourceGLBPath:modelPath,sourceGLBSHA256:sha(bytes),sourceHashes,coordinateConvention:'browser=(nativeX,nativeZ,-nativeY); native world = C^-1 * runtimeWorld * C; column-major matrices',scope:'Ten deterministic actual controller/era-motion lower-limb samples. No procedural era hardware, physics or continuous-motion claim.',poses},null,2)+'\n',{flag:'wx'});assert.equal(sha(await readFile(resolve(R,modelPath))),expectedSHA);console.log('Captured actual poses:',poses.map(p=>p.id));
