/** Capture two fresh, uncut, no-input Advanced-era WebGL autonomy runs. */
import {pathToFileURL} from 'node:url';
import {mkdir,writeFile,readFile,stat} from 'node:fs/promises';
import {createHash,randomBytes} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import os from 'node:os';
import assert from 'node:assert/strict';
import {resolve,relative} from 'node:path';

if(!process.argv[2])throw new Error('Pass the installed Playwright entry module as argv[2].');
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
const out=process.env.UNCAGED_AUDIT||'assets/audit/alignment-v4';
const devUrl=process.env.UNCAGED_DEV_URL||'http://127.0.0.1:5177/';
const modelPath='assets/models/uncaged-alignment-v4/murderbird-alignment-v4.glb';
const durationSeconds=120;
const telemetryIntervalMs=100;
const ffmpeg=process.env.FFMPEG||'ffmpeg';
const ffprobe=process.env.FFPROBE||'ffprobe';
const captureId=`${new Date().toISOString().replace(/[:.]/g,'-')}-${process.pid}-${randomBytes(3).toString('hex')}`;
await mkdir(`${out}/autonomy-videos/${captureId}`,{recursive:true});
const bytes=await readFile(modelPath);
const modelIdentity={path:modelPath,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')};
const sourceIdentity=[];
for(const path of ['src/main.js','src/scene/era-controller.js','src/scene/presence-state.js','src/scene/era-motion.js','src/scene/presence-exhibit.js','scripts/capture-alignment-v4-autonomy.mjs']){const data=await readFile(path);sourceIdentity.push({path,bytes:data.length,sha256:createHash('sha256').update(data).digest('hex')});}
const host={platform:os.platform(),architecture:os.arch(),cpu:os.cpus()[0]?.model,totalMemoryBytes:os.totalmem()};
const browser=await chromium.launch({headless:false});
const results=[];

function run(cmd,args){const p=spawnSync(cmd,args,{encoding:'utf8'});if(p.error)throw p.error;if(p.status!==0)throw new Error(`${cmd} failed (${p.status}): ${p.stderr}`);return p.stdout;}
function summarize(samples){
 const counts={};for(const x of samples)counts[x.state]=(counts[x.state]||0)+1;
 const transitions=[];for(let i=1;i<samples.length;i++)if(samples[i].state!==samples[i-1].state)transitions.push({from:samples[i-1].state,to:samples[i].state,seconds:samples[i].seconds});
 const repetitions={};for(const e of transitions)repetitions[e.to]=(repetitions[e.to]||0)+1;
 return{stateSampleCounts:counts,stateTransitionCounts:repetitions,transitionCount:transitions.length,transitions};
}
function sequenceAnalysis(items,key){
 const sequence=items.map(x=>x[key]).filter(x=>typeof x==='string'&&x.length);
 const ngrams={};for(let n=2;n<=Math.min(4,sequence.length);n++){const counts={};for(let i=0;i<=sequence.length-n;i++){const gram=sequence.slice(i,i+n).join(' → ');counts[gram]=(counts[gram]||0)+1;}ngrams[n]=Object.fromEntries(Object.entries(counts).filter(([,count])=>count>1));}
 const counts=sequence.reduce((acc,value)=>(acc[value]=(acc[value]||0)+1,acc),{});
 return{sequence,counts,consecutiveRepeats:sequence.slice(1).filter((value,i)=>value===sequence[i]).length,repeatedAdjacentNgrams:ngrams};
}
function analyzeActing(samples){
 const selectedPlans=[],executedActions=[],contactEvents=[],boundaryEvents=[],clawStageEvents=[];
 let previousBeat=null,previousState=null,previousClawStage=null,previousContact=false,previousClawContact=false;
 for(const s of samples){
  if(s.beatId&&s.beatId!==previousBeat){selectedPlans.push({seconds:s.seconds,id:s.beatId,intention:s.intention,family:s.actionFamily,route:s.routeKind,goal:s.goal});previousBeat=s.beatId;}
  if(s.state==='boundary'&&previousState!=='boundary')boundaryEvents.push({seconds:s.seconds,beatId:s.beatId,intention:s.intention,family:s.actionFamily,route:s.routeKind,goal:s.goal,heading:s.heading});
  if(s.state==='cage-test'&&previousState!=='cage-test')executedActions.push({seconds:s.seconds,kind:'cage-test-started',family:s.actionFamily,beatId:s.beatId,route:s.routeKind});
  const clawStage=s.clawAction?.stage??null;
  if(clawStage&&clawStage!==previousClawStage)clawStageEvents.push({seconds:s.seconds,stage:clawStage,phase:s.clawAction.phase,side:s.clawAction.side,target:s.clawAction.target,actualContact:s.actualClaw?.contact??false,tipMinY:s.actualClaw?.tipMinY??null,beatId:s.beatId,family:s.actionFamily});
  if(s.actualClaw?.contact&&!previousClawContact)executedActions.push({seconds:s.seconds,kind:'claw-contact',family:s.actionFamily||'claw-scrape',beatId:s.beatId,route:s.routeKind,stage:clawStage,tipMinY:s.actualClaw.tipMinY});
  if(Boolean(s.contact)!==previousContact)contactEvents.push({seconds:s.seconds,contact:Boolean(s.contact),state:s.state,family:s.actionFamily,actionKind:s.actionKind,beatId:s.beatId,route:s.routeKind,contactPoint:s.contactPoint});
  previousState=s.state;previousClawStage=clawStage;previousContact=Boolean(s.contact);previousClawContact=Boolean(s.actualClaw?.contact);
 }
 return{selectedPlans,boundaryEvents,contactEvents,clawStageEvents,executedActions,repetition:{selectedPlanIds:sequenceAnalysis(selectedPlans,'id'),selectedPlanFamilies:sequenceAnalysis(selectedPlans,'family'),selectedPlanRoutes:sequenceAnalysis(selectedPlans,'route'),executedActionFamilies:sequenceAnalysis(executedActions,'family')}};
}

try{
 for(let index=1;index<=2;index++){
  const stem=`advanced-autonomy-${index}-${captureId}`;
  const seed=index===1?927:20260928;
  const runUrl=new URL(devUrl);runUrl.searchParams.set('review-seed',String(seed));
  const runReport={run:index,captureId,status:'running',modelIdentity,modelSha256:modelIdentity.sha256,sourceIdentity,host,browser:browser.version(),requestedUrl:runUrl.href,durationTargetSeconds:durationSeconds,seed:{value:seed,scope:'DEV-only review-seed query parameter; each fresh page uses the explicit seed recorded here.'},setup:[],events:[],samples:[],errors:[],integrity:{}};
  await mkdir(`.local/alignment-v4/autonomy-originals/${captureId}`,{recursive:true});
  const context=await browser.newContext({viewport:{width:1600,height:1400},deviceScaleFactor:1,recordVideo:{dir:`.local/alignment-v4/autonomy-originals/${captureId}`,size:{width:1600,height:1400}}});
  const page=await context.newPage();
  page.on('pageerror',e=>runReport.errors.push(e.message));
  await page.route('**/*googletagmanager.com/**',r=>r.fulfill({body:''}));
  let runStartPerf=0,lastEventKey='';
  const sample=async()=>page.evaluate(()=>{
   const m=__uncaged.metrics(),s=__uncaged.getSnapshot();
   return{performanceMs:performance.now(),era:s.era,state:s.state,pendingEra:s.pendingEra,inspection:s.inspection,paused:s.paused,reducedMotion:s.reducedMotion,visitorPresent:s.visitorPresent,energy:s.energy,powerMove:s.powerMove,powerMovePending:s.powerMovePending,clawAction:s.clawAction,beatId:s.beatId,intention:s.intention,routeKind:s.routeKind,actionFamily:s.actionFamily,actionKind:s.actionKind,goal:s.goal,heading:s.heading,phase:s.phase,root:m?.motion?.root,distance:m?.motion?.distance,steps:m?.motion?.steps,feet:m?.motion?.feet,articulation:m?.motion?.actualArticulation,cervical:m?.motion?.cervical,jawHinge:m?.motion?.jawHinge,contact:m?.motion?.contact,contactPoint:m?.motion?.contactPoint,actualClaw:m?.motion?.clawAction,actualCage:m?.motion?.cageAction,fps:m?.meanFps,webgl:m?.kind,modelUrl:m?.modelUrl};
  });
  try{
   await page.goto(runUrl.href);await page.locator('#loading').waitFor({state:'hidden',timeout:60000});
   const ready=await sample();assert.equal(ready.era,'builder','Fresh run must be in Advanced/Builder era');assert.equal(ready.webgl,'webgl','Fresh run must use the actual WebGL scene');
   const response=await page.request.get(new URL(ready.modelUrl,devUrl).href);assert(response.ok(),`Model request failed: ${response.status()}`);
   const servedBytes=await response.body();runReport.servedModelSha256=createHash('sha256').update(servedBytes).digest('hex');assert.equal(runReport.servedModelSha256,modelIdentity.sha256,'Served model SHA must match full local model');
   runReport.setup.push({action:'Fresh page loaded; verified Advanced era, WebGL scene and served model SHA',snapshot:ready});
   await page.evaluate(()=>{
    window.__qaAutonomyStart=performance.now();
    const stamp=document.createElement('div');stamp.id='qa-autonomy-timecode';Object.assign(stamp.style,{position:'fixed',left:'12px',top:'8px',zIndex:999999,background:'#000',color:'#fff',font:'16px monospace',padding:'5px 9px',pointerEvents:'none'});document.body.append(stamp);
    function tick(){stamp.textContent='ADVANCED AUTONOMY · '+((performance.now()-window.__qaAutonomyStart)/1000).toFixed(3)+' s · NO INPUT';requestAnimationFrame(tick);}tick();
   });
   runStartPerf=await page.evaluate(()=>window.__qaAutonomyStart);
   runReport.startedAt=new Date().toISOString();runReport.startPerformanceMs=runStartPerf;
   runReport.captureProtocol=`One continuous 120-second interval measured by browser performance.now and mirrored in a visible clock, with telemetry sampled every ${telemetryIntervalMs} ms. No camera, page or control input occurs after the interval begins. Page-load/setup lead-in remains in the original video before the visible zero marker.`;
   runReport.environment=await page.evaluate(()=>{const canvas=document.querySelector('canvas'),gl=canvas?.getContext('webgl2'),ext=gl?.getExtension('WEBGL_debug_renderer_info');return{renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,viewport:[innerWidth,innerHeight],canvas:canvas?[canvas.width,canvas.height]:null,pixelRatio:devicePixelRatio};});
   while(true){
    const s=await sample();const seconds=(s.performanceMs-runStartPerf)/1000;if(seconds>durationSeconds)break;
    const entry={seconds,...s};runReport.samples.push(entry);
    const key=[s.state,s.beatId,s.powerMove?.kind,s.powerMove?.stage,s.clawAction?.stage,s.actualClaw?.contact,s.contact,s.pendingEra].join('|');
    if(key!==lastEventKey){runReport.events.push({seconds,state:s.state,beatId:s.beatId,intention:s.intention,routeKind:s.routeKind,actionFamily:s.actionFamily,actionKind:s.actionKind,goal:s.goal,powerMove:s.powerMove,clawAction:s.clawAction,actualClaw:s.actualClaw,contact:s.contact,contactPoint:s.contactPoint,pendingEra:s.pendingEra,visitorPresent:s.visitorPresent});lastEventKey=key;}
    await page.waitForTimeout(telemetryIntervalMs);
   }
   runReport.endedAt=new Date().toISOString();runReport.actualDurationSeconds=(await page.evaluate(()=>performance.now())-runStartPerf)/1000;
   assert(runReport.actualDurationSeconds>=durationSeconds,'Capture interval ended before 120 seconds');
   assert.deepEqual(runReport.errors,[],'Browser reported page errors');runReport.stateSummary=summarize(runReport.samples);runReport.actingTrace=analyzeActing(runReport.samples);runReport.status='passed';
  }catch(error){runReport.status='failed';runReport.failure=error.stack;}
  const video=page.video();await context.close();
  const webmPath=`${out}/autonomy-videos/${captureId}/${stem}.webm`;await video.saveAs(webmPath);
  const mp4Path=`${out}/autonomy-videos/${captureId}/${stem}.mp4`;
  try{
   run(ffmpeg,['-n','-i',webmPath,'-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',mp4Path]);
   const probeArgs=['-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=codec_name,width,height,nb_read_frames,duration:format=duration,size','-of','json'];
   const webmProbe=JSON.parse(run(ffprobe,[...probeArgs,webmPath]));
   const mp4Probe=JSON.parse(run(ffprobe,[...probeArgs,mp4Path]));
   const webm=await readFile(webmPath),file=await readFile(mp4Path);runReport.integrity={originalWebm:{path:webmPath,bytes:webm.length,sha256:createHash('sha256').update(webm).digest('hex'),probe:webmProbe},mp4:{path:mp4Path,bytes:file.length,sha256:createHash('sha256').update(file).digest('hex'),probe:mp4Probe}};
   const stream=mp4Probe.streams?.[0];assert(stream&&stream.width===1600&&stream.height===1400,'MP4 video stream dimensions unexpected');assert(Number(stream.nb_read_frames)>0,'MP4 contains no decoded video frames');
   assert(Number(webmProbe.streams?.[0]?.nb_read_frames)>0,'Original WebM contains no decoded video frames');
   assert(Number(mp4Probe.format?.duration)>=durationSeconds,'Encoded MP4 is shorter than the requested capture interval');
  }catch(error){runReport.status='failed';runReport.conversionFailure=error.stack;}
  runReport.scope='Records browser telemetry, event/state transitions, repetition counts, model identity and video integrity. It does not establish visual quality, causal intent, or human acceptance.';
  runReport.media=[{filename:relative(process.cwd(),resolve(webmPath)),sha256:runReport.integrity.originalWebm?.sha256,bytes:runReport.integrity.originalWebm?.bytes},{filename:relative(process.cwd(),resolve(mp4Path)),sha256:runReport.integrity.mp4?.sha256,bytes:runReport.integrity.mp4?.bytes}];
  const receiptPath=`${out}/${stem}.json`;await writeFile(receiptPath,JSON.stringify(runReport,null,2)+'\n',{flag:'wx'});
  const receiptBytes=await readFile(receiptPath);
  results.push({run:index,status:runReport.status,duration:runReport.actualDurationSeconds,transitionCount:runReport.stateSummary?.transitionCount,actingTrace:runReport.actingTrace?.repetition,webm:webmPath,mp4:mp4Path,receipt:relative(process.cwd(),resolve(receiptPath)),receiptSha256:createHash('sha256').update(receiptBytes).digest('hex'),modelSha256:modelIdentity.sha256,media:runReport.media,failure:runReport.failure||runReport.conversionFailure});
 }
const manifestPath=`${out}/autonomy-demonstration-${captureId}.json`;
const manifest={captureId,generatedAt:new Date().toISOString(),modelSha256:modelIdentity.sha256,modelIdentity,sourceIdentity,runs:results.map(r=>({run:r.run,status:r.status,receipt:r.receipt,receiptSha256:r.receiptSha256,modelSha256:r.modelSha256,media:r.media})),scope:'Capture integrity and sampled telemetry index. Does not establish visual quality or human acceptance.'};
await writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n',{flag:'wx'});
}finally{await browser.close();}
console.log(JSON.stringify({captureId,manifest:`${out}/autonomy-demonstration-${captureId}.json`,results},null,2));
if(results.some(x=>x.status!=='passed'))process.exitCode=1;
