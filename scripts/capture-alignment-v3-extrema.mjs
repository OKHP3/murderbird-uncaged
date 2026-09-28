/** Freeze actual live poses through the existing pause control before orbiting. */
import {pathToFileURL} from 'node:url';
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
const dir='assets/audit/alignment-v3';const raw=await readFile('assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb');
const browser=await chromium.launch({headless:false});const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const report={generatedAt:new Date().toISOString(),modelSha256:createHash('sha256').update(raw).digest('hex'),browser:browser.version(),network:'Loopback unthrottled; analytics stubbed',method:'Existing pause control is activated in the same polling function that observes the requested live phase. Cameras then orbit the frozen articulated model. These views do not certify swept collisions.',poses:[],screenshots:[],errors:[]};
page.on('pageerror',e=>report.errors.push(e.message));await page.route('**/*googletagmanager.com/**',r=>r.fulfill({body:''}));
async function record(name,views){
 const before=await page.evaluate(()=>({snapshot:__uncaged.getSnapshot(),motion:__uncaged.metrics().motion}));assert(before.snapshot.paused);
 for(const view of views){await page.evaluate(v=>__uncaged.reviewCamera(v),view);if(view==='head'){await page.locator('[data-part=beak]').click();await page.locator('#focus-part').click();}await page.waitForTimeout(180);const file=name+'-frozen-'+view+'.png';await page.locator('#viewer').screenshot({path:dir+'/'+file});const bytes=await readFile(dir+'/'+file);report.screenshots.push({filename:file,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex'),pose:name,view});}
 const after=await page.evaluate(()=>({snapshot:__uncaged.getSnapshot(),motion:__uncaged.metrics().motion}));
 assert.equal(after.snapshot.powerMove?.phase,before.snapshot.powerMove?.phase);assert.equal(after.snapshot.state,before.snapshot.state);
 report.poses.push({name,views,before,after});
}
try{
 await page.goto('http://127.0.0.1:5177/');await page.locator('#loading').waitFor({state:'hidden'});
 const served=await page.request.get(await page.evaluate(()=>__uncaged.metrics().modelUrl));report.servedModelSha256=createHash('sha256').update(await served.body()).digest('hex');assert.equal(report.servedModelSha256,report.modelSha256);
 await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
 for(const kind of ['jump','thrust']){
  await page.waitForFunction(()=>{const s=__uncaged.getSnapshot();return s.canReach&&!s.visitorPresent&&!s.powerMove&&!s.paused;},undefined,{timeout:30000});
  await page.locator(kind==='jump'?'#power-jump':'#shield-thrust').click();
  await page.waitForFunction(kind=>{const p=__uncaged.getSnapshot().powerMove;const low=kind==='jump'?.42:.49;if(p?.kind===kind&&p.phase>low&&p.phase<low+.08){document.querySelector('#pause').click();return true;}return false;},kind,{polling:8,timeout:12000});
  await record('builder-'+kind,['threeQuarter','left','right']);
  await page.locator('#pause').click();await page.waitForFunction(()=>!__uncaged.getSnapshot().powerMove&&!__uncaged.getSnapshot().powerMovePending,undefined,{timeout:10000});
 }
 await page.waitForFunction(()=>__uncaged.getSnapshot().canReach,undefined,{timeout:30000});await page.locator('#reach-position').selectOption('0');await page.locator('#reach').click();
 await page.waitForFunction(()=>{if(__uncaged.getSnapshot().state==='contact'&&__uncaged.metrics().motion.contact){document.querySelector('#pause').click();return true;}return false;},undefined,{polling:8,timeout:30000});
 await record('builder-contact',['threeQuarter','left','right','head']);
 await page.evaluate(()=>__uncaged.reviewLighting('exhibit'));await record('builder-contact-exhibit',['threeQuarter','left','right','head']);await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
 await page.locator('#pause').click();await page.locator('#retreat').click();
 await page.waitForFunction(()=>__uncaged.getSnapshot().canReach&&!__uncaged.getSnapshot().visitorPresent,undefined,{timeout:15000});
 await page.locator('[data-era=maker]').click();await page.waitForFunction(()=>__uncaged.getSnapshot().era==='maker'&&!__uncaged.getSnapshot().pendingEra);
 for(const value of [0,100]){
  await page.locator('#lever-jaw').fill(String(value));await page.waitForFunction(v=>Math.abs(__uncaged.metrics().motion.actualArticulation.jaw-v/100)<.02,value);
  await page.locator('#pause').click();await record('maker-jaw-'+value,['head','left','right']);await page.locator('#pause').click();
 }
 // Focus every visible projected control and activate it with Enter.
 // This is bounded keyboard activation evidence, not a screen-reader journey.
 report.keyboardMarkers=[];
 for(const era of ['maker','mechanic','builder']){
  await page.locator('[data-era='+era+']').click();await page.waitForFunction(e=>__uncaged.getSnapshot().era===e&&!__uncaged.getSnapshot().pendingEra,era);
  await page.locator('#section-toggle').click();await page.waitForFunction(()=>__uncaged.getSnapshot().inspection&&__uncaged.metrics().open>.99,undefined,{timeout:15000});
  await page.locator('#separation').fill('50');await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));await page.waitForTimeout(900);
  const ids=await page.locator('#hotspots button:not([hidden])').evaluateAll(bs=>bs.map(b=>b.dataset.marker));assert(ids.length>=4);
  for(const id of ids){const button=page.locator('[data-marker='+id+']');await button.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('[data-part='+id+']').getAttribute('aria-pressed'),'true');report.keyboardMarkers.push({era,id,focused:await button.evaluate(b=>b===document.activeElement),selected:true});}
  await page.locator('#reassemble').click();await page.waitForFunction(()=>!__uncaged.getSnapshot().inspection,undefined,{timeout:12000});
 }
 assert.deepEqual(report.errors,[]);report.status='passed';
}catch(e){report.status='failed';report.error=e.stack;process.exitCode=1;}finally{await browser.close();await writeFile(dir+'/frozen-extrema.json',JSON.stringify(report,null,2)+'\n');console.log(report.status,report.error||'',report.poses.map(p=>p.name));}
