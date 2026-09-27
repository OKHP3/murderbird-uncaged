/** Sequential, uncut browser demonstration of the three era control systems. */
import {pathToFileURL} from 'node:url';
if(!process.argv[2])throw new Error('Pass the installed Playwright entry module as argv[2].');
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
import {mkdir,writeFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
const out='assets/audit/structural-reconciliation-v1';await mkdir(out,{recursive:true});
const b=await chromium.launch({headless:false});const ctx=await b.newContext({viewport:{width:1600,height:1400},deviceScaleFactor:1,recordVideo:{dir:'.local/structural/videos',size:{width:1600,height:1400}}});
const recordingStarted=Date.now();const p=await ctx.newPage();const report={date:new Date().toISOString(),browser:b.version(),events:[],samples:[],errors:[]};let began;
p.on('pageerror',e=>report.errors.push(e.message));await p.route('**/*googletagmanager.com/**',r=>r.fulfill({body:''}));
async function sample(){const v=await p.evaluate(()=>{const m=__uncaged.metrics(),s=__uncaged.getSnapshot();return{era:s.era,state:s.state,pendingEra:s.pendingEra,inspection:s.inspection,energy:s.energy,powerMove:s.powerMove,powerPose:m.motion.powerMove,root:m.motion.root,distance:m.motion.distance,steps:m.motion.steps,feet:m.motion.feet,articulation:m.motion.actualArticulation,cam:m.motion.camAngle,drive:m.motion.mechanicalStage,contact:m.motion.contact,cervical:m.motion.cervical,nodes:m.nodes,mechanisms:m.mechanisms,fps:m.meanFps}});v.seconds=(Date.now()-began)/1000;report.samples.push(v);return v;}
async function wait(seconds){const end=Date.now()+seconds*1000;while(Date.now()<end){await sample();await p.waitForTimeout(250);}}
async function event(name){const v=await sample();report.events.push({name,seconds:v.seconds,era:v.era,state:v.state});console.log(name);}
async function era(id){await p.locator(`[data-era=${id}]`).click();await p.waitForFunction(id=>__uncaged.getSnapshot().era===id&&!__uncaged.getSnapshot().pendingEra,id,{timeout:15000});await event('Reconstructed '+id);}
async function inspect(name){
 await p.locator('#section-toggle').click();await p.waitForFunction(()=>__uncaged.getSnapshot().inspection&&__uncaged.metrics().open>.99,undefined,{timeout:12000});
 await p.locator('#separation').fill('75');await p.locator('#part-labels').uncheck();await wait(2);await p.locator('#viewer').screenshot({path:`${out}/${name}-inspection.png`});await event(name+' construction exposed');
 if(name!=='maker'){
  await p.locator('[data-part=drive]').click();await p.locator('#focus-part').click();await p.locator('[data-view=in]').click();await p.locator('[data-view=in]').click();await wait(3);await p.locator('#viewer').screenshot({path:`${out}/${name}-drive-detail.png`});await event(name+' transmission or actuation detail');
  if(name==='advanced'){
   await p.locator('[data-part=power]').click();await p.locator('#focus-part').click();for(let i=0;i<6;i++)await p.locator('[data-view=right]').click();await wait(2);await p.locator('#viewer').screenshot({path:out+'/advanced-power-detail.png'});await event('Advanced separate power supply');
   await p.locator('[data-part=mind]').click();await p.locator('#focus-part').click();await wait(2);await p.locator('#viewer').screenshot({path:out+'/advanced-processing-detail.png'});await event('Advanced separate sensing and processing');
  }
 }
 await p.locator('#part-labels').check();await p.locator('#reassemble').click();await p.waitForFunction(()=>!__uncaged.getSnapshot().inspection,undefined,{timeout:10000});
 await p.locator('#reset-view').click();await p.locator('[data-view=in]').click();await p.locator('[data-view=in]').click();await wait(1);
}
try{
 await p.goto('http://127.0.0.1:5174/');await p.locator('#loading').waitFor({state:'hidden'});began=Date.now();report.leadInSeconds=(began-recordingStarted)/1000;
 report.environment=await p.evaluate(()=>{const gl=document.querySelector('canvas').getContext('webgl2'),e=gl.getExtension('WEBGL_debug_renderer_info');return{renderer:gl.getParameter(e.UNMASKED_RENDERER_WEBGL),viewport:[innerWidth,innerHeight],canvas:[gl.drawingBufferWidth,gl.drawingBufferHeight],pixelRatio:devicePixelRatio};});
 await era('maker');await p.locator('[data-view=in]').click();await p.locator('[data-view=in]').click();await event('Maker untouched and anchored');await wait(4);await p.locator('#viewer').screenshot({path:out+'/maker-rest.png'});
 for(const id of ['leg','wing','tail','neck','jaw']){await p.locator('#lever-'+id).fill('100');await event('Outside lever: '+id);await wait(1.5);if(id==='wing')await p.locator('#viewer').screenshot({path:out+'/maker-operated.png'});}
 await p.locator('#release-levers').click();await wait(2);await inspect('maker');
 await era('mechanic');await wait(2);await p.locator('#run-mechanism').click();await event('Mechanic engaged: spring and cam drive');await wait(12);await p.locator('#viewer').screenshot({path:out+'/mechanic-stepping.png'});await wait(23);await event('Mechanic traversal and segmented turns');await p.locator('#stop-mechanism').click();await p.waitForFunction(()=>__uncaged.getSnapshot().state==='mechanical-ready'&&__uncaged.metrics().motion.settled,{},{timeout:12000});await event('Mechanic stops after its cycle');await wait(2);await inspect('mechanic');
 await era('builder');await event('Advanced coordinated autonomous pacing');await wait(9);await p.locator('#viewer').screenshot({path:out+'/advanced-pacing.png'});
 for(const [id,kind] of [['power-jump','jump'],['shield-thrust','thrust']]){
  await p.waitForFunction(()=>__uncaged.getSnapshot().canReach&&!__uncaged.getSnapshot().visitorPresent);await p.locator('#'+id).click();await event('Advanced '+kind+' requested');
  await p.waitForFunction(()=>{const a=__uncaged.metrics().motion.powerMove;return a&&a.phase>.40&&a.phase<.58;},undefined,{polling:10,timeout:15000});await p.locator('#viewer').screenshot({path:out+'/advanced-'+kind+'.png'});await event('Advanced '+kind+' in action');
  await p.waitForFunction(()=>!__uncaged.getSnapshot().powerMove&&__uncaged.getSnapshot().canReach,undefined,{timeout:10000});await wait(1.5);
 }
 await p.waitForFunction(()=>__uncaged.getSnapshot().canReach,{},{timeout:15000});await p.locator('#reach-position').selectOption('1');await p.locator('#reach').click();await event('Advanced acquires right-rail visitor');await p.waitForFunction(()=>__uncaged.getSnapshot().state==='contact',{},{timeout:24000});assert(await p.evaluate(()=>__uncaged.metrics().motion.contact));await event('Advanced directed contact');await p.locator('#retreat').click();await wait(2.5);await p.locator('#viewer').screenshot({path:out+'/advanced-recovery.png'});await inspect('advanced');await wait(5);await event('Advanced resumes without winding');
 report.model='assets/models/uncaged-structure-v1/murderbird-structure-v1.glb';assert.deepEqual(report.errors,[]);report.durationSeconds=(Date.now()-began)/1000;report.status='passed';
}catch(e){report.status='failed';report.failure=e.stack;process.exitCode=1;}finally{const video=p.video();await ctx.close();await video.saveAs(out+'/structural-motion-demonstration.webm');await b.close();const {samples,...metadata}=report;const serialized=JSON.stringify(metadata,null,2).slice(0,-1).trimEnd()+',\n  \"samples\": [\n'+samples.map(sample=>'    '+JSON.stringify(sample)).join(',\n')+'\n  ]\n}\n';await writeFile(out+'/motion-demonstration.json',serialized);console.log(JSON.stringify({status:report.status,duration:report.durationSeconds,failure:report.failure,errors:report.errors},null,2));}
