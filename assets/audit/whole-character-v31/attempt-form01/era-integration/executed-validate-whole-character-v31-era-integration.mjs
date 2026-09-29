/** Actual exported rigid bird plus the complete runtime era assemblies.
 * Sampled geometry/alignment diagnostics, not collision/physics or art proof.
 * --smoke is mandatory for historical inputs; final runs require --expected-sha.
 */
import assert from 'node:assert/strict';
import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { resolve, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
import * as THREE from 'three';
import { loadRigidValidation } from './load-rigid-validation.mjs';
import { createEraMotion } from '../src/scene/era-motion.js';
import { createEraController } from '../src/scene/era-controller.js';
import { createEraMechanisms } from '../src/scene/era-mechanisms.js';
import { applyInspectionPose } from '../src/scene/inspection-pose.js';

const args=process.argv.slice(2),opt=(k,d)=>{const i=args.indexOf(k);return i<0?d:args[i+1];};
const smoke=args.includes('--smoke'),modelPath=opt('--model','assets/models/whole-character-v31/attempt-form01/murderbird-whole-character-v31.glb');
const output=opt('--output',smoke?'/tmp/v31-era-integration-smoke':'assets/audit/whole-character-v31/attempt-form01/era-integration');
const hash=b=>createHash('sha256').update(b).digest('hex'),expected=opt('--expected-sha',null),bytes=await readFile(modelPath);
assert(smoke||expected,'Final run requires --expected-sha binding; historical models require --smoke');
if(expected)assert.equal(hash(bytes),expected,'Unexpected exported input');
const sources=[fileURLToPath(import.meta.url),'scripts/load-rigid-validation.mjs','src/scene/era-motion.js','src/scene/era-controller.js','src/scene/era-mechanisms.js','src/scene/inspection-pose.js','src/scene/cervical-articulation.js','src/scene/rigid-leg-kinematics.js','src/scene/presence-state.js'];
const sourceHashes=await Promise.all(sources.map(async p=>({path:p,sha256:hash(await readFile(p))})));
const gltf=await loadRigidValidation(bytes),scene=new THREE.Scene(),model=gltf.scene;scene.add(model);
const names=['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield','cervical-mid-a','cervical-mid-b','cervical-upper'];
const nodes=Object.fromEntries(names.filter(n=>model.getObjectByName(n)).map(n=>[n,model.getObjectByName(n)]));
assert(names.slice(0,15).every(n=>nodes[n]),'Incomplete real exported model');
const rest=Object.fromEntries(Object.entries(nodes).map(([n,o])=>[n,{position:o.position.clone(),rotation:o.rotation.clone()}]));
const sourceMeshes=new Set();model.traverse(o=>{if(o.isMesh)sourceMeshes.add(o);});
const motion=createEraMotion(model,nodes,rest),controller=createEraController({seed:927});
const mechanisms=createEraMechanisms({scene,model,nodes,rest});
const findSurface=name=>model.getObjectByName(name)||model.getObjectByName(THREE.PropertyBinding.sanitizeNodeName(name));
const controls=['leg','wing','tail','neck','jaw'],targets=['left-foot','right-mantle','compact-articulated-tail','neck','jaw'];
const report={generatedAt:new Date().toISOString(),status:smoke?'SMOKE ONLY — NOT A V31 RESULT':'INCOMPLETE',input:{path:modelPath,sha256:hash(bytes),bytes:bytes.length,smoke},method:{loader:'Actual GLTFLoader; only in-memory texture bindings omitted',constructors:['createEraController','createEraMotion','createEraMechanisms','applyInspectionPose'],dt:1/60,surfaceMethod:'Closest point on actual exported triangles; GLTFLoader PropertyBinding name normalization resolves declared source mesh names; no bounding-box seating claims',eraVisibility:'Actual exteriorEras plus presence-exhibit assembly gates',socketToleranceM:.001,endpointToleranceM:1e-7},failures:[],fitRisks:[],scenarios:[],limits:['Discrete runtime samples, not continuous collision, containment, force/support stability or physical simulation.','Nearest-surface distance reports possible placement gaps; internal placement can require visual inspection.','No WebGL/material/art acceptance or full mechanism collision screen.','Historical priorV21_mechanismLayoutV1 is recorded only and is not treated as active metadata.']};
const failure=(id,details)=>report.failures.push({id,...details});
const risk=(id,details)=>report.fitRisks.push({id,...details});
const point=o=>o.getWorldPosition(new THREE.Vector3());
const effectiveVisible=o=>{for(let n=o;n;n=n.parent)if(!n.visible)return false;return true;};
const makerSocketRaw=nodes.jaw.userData.makerControlSocketV1;
let socket=null;if(makerSocketRaw!=null)socket=typeof makerSocketRaw==='string'?JSON.parse(makerSocketRaw):makerSocketRaw;
const ownerSockets=Object.fromEntries(targets.flatMap((name,i)=>{const raw=model.getObjectByName(name)?.userData.makerControlSocketV1;return raw==null?[]:[[controls[i],typeof raw==='string'?JSON.parse(raw):raw]];}));
report.metadata={jawSocket:socket,ownerSockets,activeLayout:nodes.body.userData.mechanismLayoutV1??null,historicalLayoutPresent:nodes.body.userData.priorV21_mechanismLayoutV1!=null,initialMechanismLayout:mechanisms.metrics().attachmentLayout};
if(!socket&&!smoke)failure('authored-jaw-socket-absent',{});
if(socket&&!findSurface(socket.surfaceObject))failure('declared-jaw-surface-absent',{name:socket.surfaceObject});
const tri=new THREE.Triangle(),closest=new THREE.Vector3();
function nearest(p,meshes){let best=Infinity,object=null,at=null;
 for(const o of meshes){const a=o.geometry.attributes.position,index=o.geometry.index,count=index?index.count:a.count;
  for(let i=0;i<count;i+=3){for(let j=0;j<3;j++)tri[['a','b','c'][j]].fromBufferAttribute(a,index?index.getX(i+j):i+j).applyMatrix4(o.matrixWorld);tri.closestPointToPoint(p,closest);const d=p.distanceToSquared(closest);if(d<best){best=d;object=o.name;at=closest.toArray();}}
 }return {distanceM:Math.sqrt(best),object,point:at};}
function ownedMeshes(owner){const result=[];owner.traverse(o=>{if(o.isMesh&&(sourceMeshes.has(o)||owner.name==='compact-articulated-tail'))result.push(o);});return result;}
function directBodyMeshes(){return [...sourceMeshes].filter(o=>{for(let p=o.parent;p&&p!==nodes.body;p=p.parent)if(names.includes(p.name))return false;return nodes.body===o.parent||o.parent?.parent===nodes.body;});}
function ends(name){const o=scene.getObjectByName(name);if(!o)throw Error('Missing link '+name);return [new THREE.Vector3(0,-.5,0).applyMatrix4(o.matrixWorld),new THREE.Vector3(0,.5,0).applyMatrix4(o.matrixWorld)];}
function endpoint(name,p){return Math.min(...ends(name).map(e=>e.distanceTo(p)));}
let era='builder',frame=0;
function visibility(){for(const o of sourceMeshes){const tags=(o.userData.extras||o.userData).exteriorEras;if(typeof tags==='string')o.visible=tags.split(',').includes(era);}nodes['winding-drive'].visible=false;nodes['power-core'].visible=era==='builder';nodes.processing.visible=era==='builder';nodes['builder-optics'].visible=era==='builder';nodes['industrial-repairs'].visible=era!=='maker';}
function step(open=0,separation=0){const s=controller.update(1/60,motion.feedback());for(const [n,o] of Object.entries(nodes)){o.position.copy(rest[n].position);o.rotation.copy(rest[n].rotation);}motion.tick(1/60,s);applyInspectionPose(nodes,rest,open,separation);scene.updateMatrixWorld(true);mechanisms.tick(1/60,s,motion.driveMetrics(),{open,separation});scene.updateMatrixWorld(true);frame++;return s;}
function advance(seconds,open=0,separation=0){let s;for(let i=0;i<Math.ceil(seconds*60);i++)s=step(open,separation);return s;}
function probe(target){let choice=null,radius=-1;target.traverse(o=>{if(!o.isMesh)return;const a=o.geometry.attributes.position;for(let i=0;i<a.count;i++){const p=new THREE.Vector3().fromBufferAttribute(a,i);const w=p.clone().applyMatrix4(o.matrixWorld),r=w.distanceToSquared(point(target));if(r>radius){radius=r;choice={object:o,local:p,world:w};}}});return choice;}
function switchEra(next){era=next;controller.setEra(next);controller.reset();motion.resetEra(next);mechanisms.setEra(next);visibility();step();}
function snapshot(label,{surfaces=true}={}){scene.updateMatrixWorld(true);const metric=mechanisms.metrics(),mm=motion.metrics();const result={label,frame,era,state:controller.getSnapshot().state,mechanisms:metric,root:mm.root,actualArticulation:mm.actualArticulation,jawAngleRad:nodes.jaw.rotation.x,tailAngleRad:model.getObjectByName('compact-articulated-tail').rotation.x,finite:true,visibleMeshes:{},maker:[],endpointErrors:{},groupSeats:[]};
 scene.traverse(o=>{if(!o.matrixWorld.elements.every(Number.isFinite)){result.finite=false;failure('nonfinite-transform',{label,name:o.name});}});
 for(const e of ['maker','mechanic','builder']){const group=scene.getObjectByName('era-'+e+'-mechanisms');let count=0;group?.traverseVisible(o=>{if(o.isMesh)count++;});result.visibleMeshes[e]=effectiveVisible(group)?count:0;if(effectiveVisible(group)!==(e===era))failure('era-group-visibility',{label,group:e});}
 for(const [i,c] of controls.entries()){
  const target=model.getObjectByName(targets[i]),attachment=scene.getObjectByName('maker-joint-attachment-'+c),offset=metric.attachmentLayout.makerControlOffsets[i];
  const expected=target.localToWorld(new THREE.Vector3(...offset)),actual=point(attachment),trackingError=actual.distanceTo(expected);
  const record={control:c,target:target.name,position:actual.toArray(),trackingErrorM:trackingError};
  if(trackingError>1e-7)failure('maker-attachment-tracking',{label,...record});
  record.rodEndpointErrorM=endpoint('maker-control-rod-'+c+'-joint',actual);record.hornEndpointErrorM=endpoint('maker-control-horn-'+c,actual);
  if(Math.max(record.rodEndpointErrorM,record.hornEndpointErrorM)>1e-7)failure('maker-link-endpoint',{label,...record});
  if(surfaces){record.nearestAssemblySurface=nearest(actual,ownedMeshes(target));record.attachmentRadiusM=.026;if(record.nearestAssemblySurface.distanceM>.026)risk('maker-placement-outside-surface-reach',{label,...record});}
  if(ownerSockets[c]){const declared=ownerSockets[c],surface=findSurface(declared.surfaceObject);record.declaredSurfaceName=declared.surfaceObject;record.loadedSurfaceName=surface?.name;let parent=surface;while(parent&&parent!==target)parent=parent.parent;record.authoredSurfaceOwnerValid=Boolean(parent);if(!parent)failure('authored-socket-wrong-owner',{label,control:c,surface:declared.surfaceObject});if(surface&&surfaces){record.authoredSurfaceDistance=nearest(actual,[surface]);if(record.authoredSurfaceDistance.distanceM>.001)failure('authored-socket-not-on-declared-surface',{label,...record});}}
  result.maker.push(record);
 }
 // Actual segment ends, not copied controller distance metrics.
 for(const side of ['left','right']){
  const knee=point(model.getObjectByName(side+'-shin')),hip=point(model.getObjectByName(side+'-thigh'));
  result.endpointErrors['mechanic-'+side+'-knee']=endpoint('mechanic-'+side+'-slotted-knee-link-slider',knee);
  result.endpointErrors['mechanic-'+side+'-crank']=endpoint('mechanic-'+side+'-slotted-knee-link-sleeve',point(scene.getObjectByName('mechanic-'+side+'-crank-pin')));
  result.endpointErrors['builder-'+side+'-hip']=endpoint('builder-'+side+'-linear-actuator-sleeve',hip);
  result.endpointErrors['builder-'+side+'-knee']=endpoint('builder-'+side+'-actuator-rod',knee);
 }
 if(separationMode(metric)==='connected'){
  result.endpointErrors['builder-shoulder']=endpoint('builder-right-shoulder-actuator',point(nodes['right-mantle']));result.endpointErrors['builder-elbow']=endpoint('builder-right-shoulder-actuator-rod',point(nodes['right-wing-shield']));
 }
 for(const [name,error] of Object.entries(result.endpointErrors))if(error>1e-7)failure('mechanism-link-endpoint',{label,name,errorM:error});
 for(const [name,owner] of [['mechanic-lower-transmission',nodes.body],['builder-power-distribution-manifold',nodes.body],['compact-articulated-tail',nodes.body]]){
  const o=model.getObjectByName(name);if(o.parent!==owner)failure('mechanism-group-detached',{label,name});const seat={name,owner:owner.name,localPosition:o.position.toArray(),worldPosition:point(o).toArray(),effectiveVisible:effectiveVisible(o)};if(surfaces)seat.nearestBodySurface=nearest(point(o),directBodyMeshes());result.groupSeats.push(seat);
 }
 if(surfaces){const bodyMeshes=directBodyMeshes(),manifold=model.getObjectByName('builder-power-distribution-manifold'),seat=nearest(point(manifold),bodyMeshes);if(era==='builder'&&seat.distanceM>.10)risk('manifold-placement-away-from-body',{label,...seat,position:point(manifold).toArray()});
  if(era==='builder'&&metric.inspectionConnections.cervical.every(a=>a.mode==='connected')){result.cervicalSurfaceSeats=[];for(const side of ['left','right']){const bodyEnd=ends('builder-cervical-'+side+'-actuator-sleeve')[0],neckEnd=ends('builder-cervical-'+side+'-actuator-rod')[1];const bodySeat=nearest(bodyEnd,bodyMeshes),neckSeat=nearest(neckEnd,ownedMeshes(nodes.neck));const row={side,actualBodyEndpoint:bodyEnd.toArray(),actualNeckEndpoint:neckEnd.toArray(),nearestBodySurface:bodySeat,nearestNeckSurface:neckSeat,meaning:'Actual cylinder endpoints against source triangles; centre-line consistency does not certify socket/clearance'};result.cervicalSurfaceSeats.push(row);if(bodySeat.distanceM>.028||neckSeat.distanceM>.012)risk('cervical-endpoint-surface-gap',{label,...row});}}
 }
 const visibleBounds=new THREE.Box3();scene.traverseVisible(o=>{if(o.isMesh)visibleBounds.expandByObject(o,false);});result.visibleBounds={min:visibleBounds.min.toArray(),max:visibleBounds.max.toArray()};report.scenarios.push(result);return result;
}
const separationMode=metric=>metric.inspectionConnections.wing.mode;
try{
 switchEra('maker');snapshot('maker-rest');
 for(const id of controls){const witness=probe(model.getObjectByName(targets[controls.indexOf(id)]));controller.setArticulation(id,1);advance(1.8);const top=snapshot('maker-'+id+'-maximum');top.physicalGeometryMotion={mesh:witness.object.name,start:witness.world.toArray(),finish:witness.local.clone().applyMatrix4(witness.object.matrixWorld).toArray(),displacementM:witness.world.distanceTo(witness.local.clone().applyMatrix4(witness.object.matrixWorld))};if(top.physicalGeometryMotion.displacementM<.001)failure('maker-target-geometry-did-not-move',{control:id,...top.physicalGeometryMotion});if(id==='jaw'&&top.jawAngleRad<.319)failure('jaw-maximum-not-reached',{value:top.jawAngleRad});if(id==='tail'&&Math.abs(top.tailAngleRad)<.27)failure('procedural-tail-not-articulated',{value:top.tailAngleRad});controller.setArticulation(id,0);advance(1.8);snapshot('maker-'+id+'-return');}
 // Full return is sampled; intermediate points use the real smoothed controller.
 controller.setArticulation('jaw',1);for(let i=0;i<100;i++){step();if([2,5,10,20,40,99].includes(i))snapshot('maker-jaw-sweep-'+i);}controller.setArticulation('jaw',0);advance(2);snapshot('maker-jaw-sweep-return');
 for(const next of ['maker','mechanic','builder']){
  switchEra(next);const base=snapshot(next+'-era-reset');
  controller.setInspection(true);advance(2);step(1,0);snapshot(next+'-inspection-open',{surfaces:false});step(1,1);const exploded=snapshot(next+'-inspection-exploded',{surfaces:false});
  if(next==='builder'&&exploded.mechanisms.inspectionConnections.wing.mode!=='disengaged-at-sockets')failure('builder-inspection-links-not-disconnected',{});
  controller.setInspection(false);advance(2);controller.reset();motion.resetEra(next);step();const back=snapshot(next+'-inspection-reset');
  for(const seat of base.groupSeats){const now=back.groupSeats.find(g=>g.name===seat.name);if(Math.hypot(...now.localPosition.map((v,i)=>v-seat.localPosition[i]))>1e-9)failure('group-local-reset-drift',{era:next,name:seat.name});}
 }
 switchEra('mechanic');controller.requestRoutine();for(let i=0;i<24*60;i++){step();if(i%120===0)snapshot('mechanic-route-'+i,{surfaces:false});}controller.stopRoutine();advance(4);snapshot('mechanic-route-stop');
 switchEra('builder');for(const kind of ['thrust','jump']){if(!controller.requestPowerMove(kind))failure('power-action-request-rejected',{kind});for(let i=0;i<5*60;i++){step();if(i%30===0)snapshot('builder-'+kind+'-'+i,{surfaces:false});}controller.reset();motion.resetEra('builder');step();snapshot('builder-'+kind+'-reset');}
 switchEra('maker');snapshot('final-maker-reset');
}catch(e){failure('scenario-execution-error',{message:e.message,stack:e.stack});}
report.worstFitRiskPerControl=Object.fromEntries(controls.map(c=>{const r=report.fitRisks.filter(r=>r.control===c).sort((a,b)=>b.nearestAssemblySurface.distanceM-a.nearestAssemblySurface.distanceM)[0];return [c,r??null];}));
report.summary={sampleCount:report.scenarios.length,failures:report.failures.length,fitRisks:report.fitRisks.length,physicalProceduralTailCreated:Boolean(model.getObjectByName('compact-articulated-tail')),activeLayoutStatus:mechanisms.metrics().attachmentLayout.status};
report.status=smoke?'SMOKE ONLY — NOT A V31 RESULT':report.failures.length?'FAIL':report.fitRisks.length?'ALIGNMENT CHECKS COMPLETE WITH FIT RISKS':'BOUNDED INTEGRATION CHECK COMPLETE';
assert.equal(hash(await readFile(modelPath)),report.input.sha256,'Input modified');for(const s of sourceHashes)assert.equal(hash(await readFile(s.path)),s.sha256,'Executed runtime source changed mid-run: '+s.path);
await mkdir(output,{recursive:false});report.executedSources=[];for(const s of sourceHashes){const dest='executed-'+basename(s.path);await copyFile(s.path,resolve(output,dest));report.executedSources.push({...s,frozenPath:dest});}
await writeFile(resolve(output,'integration.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,input:report.input,summary:report.summary,failures:report.failures.slice(0,8),fitRiskKinds:[...new Set(report.fitRisks.map(r=>r.id))],output},null,2));mechanisms.dispose();if(report.failures.length&&!smoke)process.exitCode=1;
