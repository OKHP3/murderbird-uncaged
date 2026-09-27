/** Uncut, wall-clock browser encounter. Uses existing external Playwright only. */
import assert from 'node:assert/strict';
import {mkdir,writeFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
const base='http://127.0.0.1:5174/';
const out='assets/audit/uncaged-presence-review';
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:false});
const context=await browser.newContext({viewport:{width:1440,height:1200},deviceScaleFactor:1,recordVideo:{dir:'.local/stage-two/videos',size:{width:1440,height:1200}}});
const page=await context.newPage(),errors=[],warnings=[];
page.on('pageerror',e=>errors.push(e.message));page.on('console',e=>{if(e.type()==='error')errors.push(e.text());if(e.type()==='warning')warnings.push(e.text());});
await page.route('**/*googletagmanager.com/**',r=>r.fulfill({status:200,body:''}));
const report={date:new Date().toISOString(),url:base,browser:browser.version(),viewport:{width:1440,height:1200},checks:[],events:[],samples:[],errors,warnings};
let began;
async function sample(){const v=await page.evaluate(()=>{const m=__uncaged.metrics(),s=__uncaged.getSnapshot();return{state:s.state,phase:s.phase,action:s.actionKind,agitation:s.agitation,visitor:s.visitorPresent,inspection:s.inspection,open:m.open,separation:m.separation,root:m.motion.root,feet:m.motion.feet,steps:m.motion.steps,distance:m.motion.distance,contact:m.motion.contact,contactPoint:m.motion.contactPoint,maxFootError:m.motion.maxFootError,maxReachDrop:m.motion.maxReachDrop,bounds:m.motion.bodyBounds,fps:m.meanFps};});v.seconds=(Date.now()-began)/1000;report.samples.push(v);return v;}
async function until(seconds){while((Date.now()-began)/1000<seconds){await sample();await page.waitForTimeout(200);}}
async function event(name){report.events.push({name,seconds:(Date.now()-began)/1000,state:(await sample()).state});console.log(name);}
try{
await page.goto(base);await page.locator('#loading').waitFor({state:'hidden'});
assert.match(await page.title(),/MurderBird/);assert.equal(await page.locator('vite-error-overlay').count(),0);assert.match(await page.locator('h1').innerText(),/Uncaged/);
report.environment=await page.evaluate(()=>{const m=__uncaged.metrics(),gl=document.querySelector('#scene canvas').getContext('webgl2'),ext=gl.getExtension('WEBGL_debug_renderer_info');return{renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),software:m.softwareRenderer,devicePixelRatio,canvasSize:[gl.drawingBufferWidth,gl.drawingBufferHeight],animationProof:m.animationProof,triangles:m.triangles,drawCalls:m.drawCalls,userAgent:navigator.userAgent};});
assert.equal(report.environment.animationProof.verified,true);
began=Date.now();await event('start — no visitor input');
await page.screenshot({path:out+'/encounter-start.png'});
await until(12);await page.screenshot({path:out+'/autonomous-pacing.png'});
await until(60);
const unattended=[...new Set(report.samples.map(s=>s.state))];
for(const state of ['watch','pace','boundary','cage-test','recover','agitated'])assert(unattended.includes(state),'60s unattended lacks '+state);
assert(report.samples.at(-1).distance>3);assert(report.samples.at(-1).steps>12);assert(report.samples.some(s=>s.action==='cage'&&s.contact));
for(const s of report.samples){assert(s.maxFootError<.002,'foot target drift');assert(s.bounds.min.x> -2.88&&s.bounds.max.x<2.88&&s.bounds.min.z> -2.08&&s.bounds.max.z<2.09,'cage penetration');for(const f of s.feet)if(!f.swinging)assert(Math.abs(f.groundMin-.002)<.002,'planted foot not grounded');}
report.checks.push({name:'60 seconds without input: varied autonomous behavior, planted steps, cage test and clearance',status:'pass',states:unattended});
await page.waitForFunction(()=>__uncaged.getSnapshot().canReach,{},{timeout:8000});
await page.locator('#reach-position').selectOption('0');await page.locator('#reach').click();await event('approach at center rail');
assert.equal(await page.locator('#reach').isDisabled(),true);
let hit=false;const deadline=Date.now()+22000;
while(Date.now()<deadline){const s=await sample();if(s.state==='contact'){assert(s.contact);hit=true;await event('directed contact');break;}await page.waitForTimeout(30);}
assert(hit,'directed attack did not make contact');
await page.locator('#retreat').click();await event('retreat after commitment');
await page.waitForFunction(()=>__uncaged.getSnapshot().state==='agitated',{},{timeout:6000});
const residual=await sample();assert(residual.agitation>.65&&!residual.visitor);await page.screenshot({path:out+'/post-strike-agitation.png'});
report.checks.push({name:'attention, anticipation, directed attack, retreat and residual agitation',status:'pass'});
await page.waitForTimeout(1800);await page.locator('#section-toggle').click();await event('request inspection during residual activity');
await page.waitForFunction(()=>__uncaged.getSnapshot().inspection&&__uncaged.metrics().open>.99,{},{timeout:10000});
await page.locator('#separation').fill('100');await page.waitForTimeout(1200);await sample();await page.screenshot({path:out+'/stable-exploded.png'});await event('stable exploded inspection');
assert((await page.evaluate(()=>__uncaged.metrics().motion.settled))===true);
await page.waitForTimeout(1600);await page.locator('#reassemble').click();await event('reassemble and return');
await page.waitForFunction(()=>!__uncaged.getSnapshot().inspection&&__uncaged.metrics().open===0&&__uncaged.metrics().separation===0,{},{timeout:10000});
const distanceBefore=(await sample()).distance;await until(Math.max(89,(Date.now()-began)/1000+6));
assert((await sample()).distance>distanceBefore+.05,'autonomy did not resume');
report.checks.push({name:'safe inspection, separation, reassembly and resumed travel',status:'pass'});
assert.equal(await page.locator('#sound-toggle').getAttribute('aria-pressed'),'false');assert.equal(await page.locator('#theme-play').innerText(),'Play');assert.deepEqual(errors,[]);
report.checks.push({name:'muted encounter, no autoplay and console health',status:'pass'});
report.durationSeconds=(Date.now()-began)/1000;report.final=await page.evaluate(()=>__uncaged.metrics());
}catch(e){report.failure=e.stack;process.exitCode=1;console.error(e.message);}finally{
const video=page.video();await context.close();await video.saveAs(out+'/milestone-encounter.webm');await browser.close();await writeFile(out+'/browser-encounter.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks:report.checks,failure:report.failure,duration:report.durationSeconds,errors},null,2));
}
