/** Local, headed visual/metadata review for the alignment correction v3. */
import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the already installed Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const devUrl=process.env.UNCAGED_DEV_URL||'http://127.0.0.1:5177/';
const productionUrl=process.env.UNCAGED_PROD_URL||'http://127.0.0.1:4177/';
for(const value of [devUrl,productionUrl])if(!['127.0.0.1','localhost'].includes(new URL(value).hostname))throw new Error('Alignment review is restricted to loopback previews.');
const outputDir=path.resolve(process.env.UNCAGED_AUDIT||'assets/audit/alignment-v3');
await mkdir(outputDir,{recursive:true});
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const eraNames={maker:'Maker',mechanic:'Mechanic',builder:'Advanced'};
const fallbackSource=await readFile('src/scene/fallback.js','utf8');
const previewPaths=Object.fromEntries([...fallbackSource.matchAll(/^\s*(maker|mechanic|builder):\s*new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.png)['"],\s*import\.meta\.url\)/gm)].map(match=>[match[1],match[2]]));
assert.deepEqual(Object.keys(previewPaths).sort(),['builder','maker','mechanic'],'fallback source must select one preview per era');
const inventory=JSON.parse(await readFile('assets/models/uncaged-alignment-v3/alignment-inventory.json','utf8'));
const generatedFiles=new Map(inventory.generatedFiles.map(file=>[file.path,file]));
const expectedPreviews={};
for(const era of ['maker','mechanic','builder']){
  const sourcePath=previewPaths[era];
  assert.equal(sourcePath,`assets/models/uncaged-alignment-v3/${era}-preview.png`,`fallback ${era} source path is unexpected`);
  const record=generatedFiles.get(sourcePath);
  assert(record,`fallback ${era} preview is absent from the alignment inventory`);
  const bytes=await readFile(sourcePath);
  assert.equal(bytes.length,record.bytes,`fallback ${era} preview byte count differs from inventory`);
  assert.equal(sha256(bytes),record.sha256,`fallback ${era} preview hash differs from inventory`);
  assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a',`fallback ${era} source is not PNG`);
  expectedPreviews[era]={sourcePath,sha256:record.sha256,bytes:record.bytes,width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)};
}
const modelPath='assets/models/uncaged-alignment-v3/murderbird-alignment-v3.glb';
const modelBytes=await readFile(modelPath);
const modelIdentity={path:modelPath,bytes:modelBytes.length,sha256:sha256(modelBytes)};
const browser=await chromium.launch({headless:false});
const report={generatedAt:new Date().toISOString(),devUrl,productionUrl,modelIdentity,network:'Loopback, unthrottled; analytics script stubbed',browser:browser.version(),status:'running',checks:[],errors:[],screenshots:[],performance:[],blockedRequests:[],stubbedAnalyticsRequests:[],lifecycle:{}};
const pages=[];
const desktopLabelCounts=new Map();
const lifecycleByPage=new Map();

function observe(page,label){
  const lifecycle={mainFrameNavigations:[],loadEvents:[],viteMessages:[],checkpoints:[]};
  lifecycleByPage.set(page,lifecycle);report.lifecycle[label]=lifecycle;
  page.on('framenavigated',frame=>{if(frame===page.mainFrame())lifecycle.mainFrameNavigations.push({at:new Date().toISOString(),url:frame.url()});});
  page.on('load',()=>lifecycle.loadEvents.push({at:new Date().toISOString(),url:page.url()}));
  page.on('pageerror',error=>report.errors.push({page:label,type:'pageerror',message:error.message}));
  page.on('console',message=>{if(message.type()==='error')report.errors.push({page:label,type:'console',message:message.text()});if(/\bVite\b|\bHMR\b|full reload|page reload/i.test(message.text()))lifecycle.viteMessages.push({at:new Date().toISOString(),type:message.type(),message:message.text()});});
  page.on('request',request=>{const url=new URL(request.url());if(url.hostname==='www.googletagmanager.com'&&url.pathname==='/gtag/js')report.stubbedAnalyticsRequests.push({page:label,url:request.url()});else if(!['127.0.0.1','localhost'].includes(url.hostname)&&!['data:','blob:'].includes(url.protocol))report.blockedRequests.push({page:label,url:request.url()});});
  page.route('**/*',route=>{const url=new URL(route.request().url());if(['127.0.0.1','localhost'].includes(url.hostname)||['data:','blob:'].includes(url.protocol))route.continue();else if(url.hostname==='www.googletagmanager.com'&&url.pathname==='/gtag/js')route.fulfill({status:200,contentType:'application/javascript',body:''});else route.abort();});
}
async function beginStablePage(page,label){
  const lifecycle=lifecycleByPage.get(page);
  lifecycle.baseline=await page.evaluate(()=>({timeOrigin:performance.timeOrigin,href:location.href}));
  lifecycle.baselineNavigationCount=lifecycle.mainFrameNavigations.length;
  lifecycle.baselineLoadCount=lifecycle.loadEvents.length;
  await recordCheckpoint(page,label,'loaded');
}
async function recordCheckpoint(page,label,stage){
  const lifecycle=lifecycleByPage.get(page);
  const state=await page.evaluate(()=>({timeOrigin:performance.timeOrigin,href:location.href,snapshot:window.__uncaged?.getSnapshot?.(),metrics:window.__uncaged?.metrics?.()})).catch(error=>({readError:error.message}));
  const checkpoint={at:new Date().toISOString(),stage,navigationCount:lifecycle.mainFrameNavigations.length,loadCount:lifecycle.loadEvents.length,...state};
  lifecycle.checkpoints.push(checkpoint);
  if(lifecycle.baseline&&(state.timeOrigin!==lifecycle.baseline.timeOrigin||lifecycle.mainFrameNavigations.length!==lifecycle.baselineNavigationCount||lifecycle.loadEvents.length!==lifecycle.baselineLoadCount)){
    throw new Error(`Unexpected ${label} page reload/navigation detected at ${stage}.`);
  }
  return checkpoint;
}
async function screenshot(page,name,era,lighting,view,pose){
  const filename=`${name}.png`;
  const actualLighting=await page.evaluate(()=>window.__uncaged?.metrics?.()?.review?.lighting).catch(()=>null);
  await page.locator('#viewer').screenshot({path:path.join(outputDir,filename)});
  const bytes=await readFile(path.join(outputDir,filename));
  const state=await page.evaluate(()=>({time:performance.now(),snapshot:window.__uncaged?.getSnapshot?.(),motion:window.__uncaged?.metrics?.()?.motion}));
  report.screenshots.push({filename,era,lighting:actualLighting||lighting,view,pose,sha256:sha256(bytes),bytes:bytes.length,stateAfterCapture:state});
}
async function check(page,name,fn){
  console.log(`CHECK ${name}`);
  try{const detail=await fn();report.checks.push({name,status:'passed',detail});return detail;}
  catch(error){
    const diagnostic=await page.evaluate(()=>({snapshot:window.__uncaged?.getSnapshot?.(),metrics:window.__uncaged?.metrics?.()})).catch(()=>null);
    const file=`failure-${name.toLowerCase().replace(/[^a-z0-9]+/g,'-')}.png`;
    await page.locator('#viewer').screenshot({path:path.join(outputDir,file)}).catch(()=>{});
    report.checks.push({name,status:'failed',error:error.message,diagnostic,screenshot:file});throw error;
  }
}
async function waitEra(page,era){
  await page.waitForFunction(target=>{const s=window.__uncaged?.getSnapshot?.();return s?.era===target&&!s.pendingEra;},era,{timeout:15000});
  await page.waitForFunction(()=>window.__uncaged?.metrics?.()?.kind==='webgl',undefined,{timeout:15000});
  await page.waitForFunction(target=>{const m=window.__uncaged.metrics();return m.exterior?.currentEra===target&&m.exterior.taggedObjectCount>0;},era,{timeout:10000});
}
async function setPaused(page,value){
  const current=await page.evaluate(()=>Boolean(__uncaged.getSnapshot().paused));
  if(current!==value)await page.locator('#pause').click();
  await page.waitForFunction(target=>Boolean(__uncaged.getSnapshot().paused)===target,value,{timeout:2000});
}
async function setReducedMotion(page,value){
  const checkbox=page.locator('#reduced-motion');
  if(await checkbox.isChecked()!==value)await checkbox.setChecked(value);
  await page.waitForFunction(target=>Boolean(__uncaged.getSnapshot().reducedMotion)===target,value,{timeout:2000});
}
async function waitForSettle(page,timeout=12000){
  await page.waitForFunction(()=>__uncaged.metrics()?.motion?.settled===true,undefined,{timeout});
}
async function settleInspection(page){
  await page.locator('#section-toggle').click();
  await page.waitForFunction(()=>window.__uncaged.getSnapshot().inspection&&window.__uncaged.metrics().open>.99,undefined,{timeout:10000});
}
async function reassemble(page){
  await page.locator('#reassemble').click();
  await page.waitForFunction(()=>!window.__uncaged.getSnapshot().inspection&&window.__uncaged.metrics().open===0&&window.__uncaged.metrics().separation===0,undefined,{timeout:10000});
}
async function waitPowerComplete(page){await page.waitForFunction(()=>{const s=__uncaged.getSnapshot(),m=__uncaged.metrics();return s.powerMove===null&&s.powerMovePending===null&&m.motion?.powerMove===null&&m.motion?.settled;},undefined,{timeout:12000});}
async function waitTicks(page,milliseconds=2400){await page.waitForTimeout(milliseconds);}
async function samplePerformance(page,era,scenario,milliseconds=8000,exercise){
  const until=Date.now()+milliseconds;
  while(Date.now()<until){await exercise?.();await page.waitForTimeout(400);}
  report.performance.push({era,scenario,...await page.evaluate(()=>__uncaged.metrics().performance)});
}

try{
  const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});pages.push(page);observe(page,'dev');
  await page.goto(devUrl);await page.locator('#loading').waitFor({state:'hidden',timeout:30000});
  await beginStablePage(page,'dev');
  await check(page,'neutral rigid metadata and actual model load',async()=>{
    assert.equal(await page.locator('#scene canvas').count(),1);
    assert.equal(await page.evaluate(()=>typeof window.__uncaged.reviewCamera),'function');
    const m=await page.evaluate(()=>__uncaged.metrics());
    assert.equal(m.kind,'webgl');assert(m.exterior.taggedObjectCount>0,'GLB should expose era-tagged exterior surfaces');
    assert.equal(m.exterior.textures.count,0,'neutral stage deliberately omits final texture maps');
    assert.equal(m.exterior.textures.normalMapCount,0);
    assert(m.exterior.textures.estimatedDecodedMipmapBytes<=48*1024*1024,'decoded texture estimate exceeds 48 MiB budget');
    const modelResource=await page.evaluate(url=>{const entry=performance.getEntriesByType('resource').find(value=>value.name===url);return entry?{transferBytes:entry.transferSize,encodedBytes:entry.encodedBodySize,decodedBytes:entry.decodedBodySize}:null;},m.modelUrl);
    assert(modelResource,'browser resource timing includes the local GLB');
    const servedModel=await page.request.get(m.modelUrl);
    assert.equal(servedModel.status(),200,'runtime GLB response status');
    assert.equal(sha256(await servedModel.body()),modelIdentity.sha256,'loaded GLB must match the frozen local review model');
    assert(modelResource.decodedBytes<=18*1024*1024,'combined GLB exceeds 18 MiB');
    return {modelUrl:m.modelUrl,modelResource,exterior:m.exterior,performance:m.performance};
  });

  for(const era of ['maker','mechanic','builder']){
    await page.locator(`[data-era="${era}"]`).click();await waitEra(page,era);
    await recordCheckpoint(page,'dev',`era-${era}-settled`);
    await setReducedMotion(page,true);await waitForSettle(page);await setPaused(page,true);
    await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));
    await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
    await waitTicks(page);
    const neutral=await page.evaluate(()=>__uncaged.metrics());
    await screenshot(page,`${era}-exterior-neutral`,era,'neutral','threeQuarter','rest');
    await page.evaluate(()=>__uncaged.reviewLighting('exhibit'));
    await waitTicks(page,400);
    const exhibit=await page.evaluate(()=>__uncaged.metrics());
    assert.deepEqual(exhibit.review.camera,neutral.review.camera,'neutral/exhibit camera must match');
    assert.deepEqual(exhibit.review.target,neutral.review.target,'neutral/exhibit target must match');
    await screenshot(page,`${era}-exterior-exhibit`,era,'exhibit','threeQuarter','rest');
    await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
    for(const [view,camera] of [['front','front'],['side-left','left'],['side-right','right'],['rear','rear'],['three-quarter-left','threeQuarterLeft'],['elevated','elevated'],['low','low']]){
      await page.evaluate(name=>__uncaged.reviewCamera(name),camera);await waitTicks(page,350);
      await screenshot(page,`${era}-${view}-neutral`,era,'neutral',camera,'rest');
    }
    for(const [camera,part] of [['head','head'],['neck','neck'],['leftShoulder','shoulder'],['breast','breast'],['feet','feet']]){
      await page.evaluate(name=>__uncaged.reviewCamera(name),camera);await waitTicks(page,350);
      await screenshot(page,`${era}-${part}-closeup`,era,'neutral',camera,'rest');
    }
    await recordCheckpoint(page,'dev',`era-${era}-surface-captures`);
    await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));
    await check(page,`${era} exterior eligibility and region visibility`,async()=>{
      const m=await page.evaluate(()=>__uncaged.metrics());
      assert.equal(m.exterior.currentEra,era);
      assert(m.exterior.byEra[era].eligibleObjects>0,`${era} has eligible tagged objects`);
      assert(m.exterior.byEra[era].visibleObjects>0,`${era} has visible tagged objects`);
      assert(m.exterior.surfaceObjects.every(object=>!object.visible||object.eras.includes(era)),'ineligible exterior variant is effectively visible');
      return {byEra:m.exterior.byEra[era],surfaces:m.exterior.surfaceObjects.filter(object=>object.visible)};
    });
    await settleInspection(page);await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));await waitTicks(page,500);
    await screenshot(page,`${era}-inspection-open`,era,'exhibit','threeQuarter','open');
    await page.locator('#separation').fill('100');await page.waitForFunction(()=>__uncaged.metrics().separation>.99,undefined,{timeout:5000});await waitTicks(page,500);
    await screenshot(page,`${era}-inspection-exploded`,era,'exhibit','threeQuarter','exploded');
    for(const width of [1440,390]){
      await page.setViewportSize({width,height:width===390?844:1000});await waitTicks(page,400);
      for(const separation of [0,50,100])for(const camera of ['threeQuarter','rear']){
       await page.locator('#separation').fill(String(separation));await page.evaluate(c=>__uncaged.reviewCamera(c),camera);await waitTicks(page,900);
       const layout=await page.locator('#hotspots button:not([hidden])').evaluateAll(buttons=>{
        const viewer=document.querySelector('#viewer').getBoundingClientRect();
        const containerStyle=getComputedStyle(document.querySelector('#hotspots'));
        return {containerVisible:containerStyle.display!=='none'&&containerStyle.visibility==='visible'&&Number(containerStyle.opacity)>0,
         viewport:{width:innerWidth,height:innerHeight,scrollX,scrollY},viewer:{left:viewer.left,top:viewer.top,right:viewer.right,bottom:viewer.bottom,width:viewer.width,height:viewer.height},
         labels:buttons.map(button=>{const r=button.getBoundingClientRect(),style=getComputedStyle(button);return {id:button.dataset.marker,x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom,visible:style.display!=='none'&&style.visibility==='visible'&&Number(style.opacity)>0,label:button.getAttribute('aria-label'),tabIndex:button.tabIndex};})};
       });
       const labels=layout.labels;
       assert(layout.containerVisible,`${era}/${width}: hotspot layer must be visible`);
       assert(layout.viewer.width>0&&layout.viewer.height>0,`${era}/${width}: viewer has positive bounds`);
       assert(labels.length>=4,`${era} must expose at least four projected inspection labels at ${width}px`);
       for(let a=0;a<labels.length;a++){
        const label=labels[a],v=layout.viewer;assert(label.label&&label.tabIndex>=0);assert(label.visible,`${label.id} must be visible`);assert(label.w>=37&&label.h>=37,`${label.id} must retain its 38px keyboard/touch target`);assert(label.x>=v.left&&label.y>=v.top&&label.right<=v.right&&label.bottom<=v.bottom,`${label.id} must remain in viewer bounds`);
        for(let b=a+1;b<labels.length;b++){const other=labels[b];assert(label.right<=other.x||other.right<=label.x||label.bottom<=other.y||other.bottom<=label.y,`${label.id}/${other.id}: projected labels overlap`);}
       }
       const combo=`${era}:${separation}:${camera}`;
       if(width===1440)desktopLabelCounts.set(combo,labels.length);
       else assert.equal(labels.length,desktopLabelCounts.get(combo),`${combo}: narrow viewport must preserve desktop label count`);
       if(separation===0&&camera==='threeQuarter'){
        const first=page.locator('#hotspots button:not([hidden])').first(),marker=await first.getAttribute('data-marker');
        await first.focus();assert.equal(await page.evaluate(()=>document.activeElement?.dataset?.marker),marker,'marker receives focus');
        await page.keyboard.press('Enter');assert.equal(await page.locator(`[data-part="${marker}"]`).getAttribute('aria-pressed'),'true','Enter selects inspector item');
        assert.equal(await page.evaluate(()=>document.activeElement?.dataset?.marker),marker,'marker retains focus after Enter');
        report.labelKeyboard??=[];report.labelKeyboard.push({era,width,marker,focused:true,enterSelected:true,focusRetained:true});
       }
       report.labelLayouts??=[];report.labelLayouts.push({era,width,separation,camera,...layout});
       await screenshot(page,`${era}-labels-${width}-${separation}-${camera}`,era,'neutral',camera,'inspection');
      }
     }
     await page.setViewportSize({width:1440,height:1000});
     await page.locator('#separation').fill('0');await page.waitForFunction(()=>__uncaged.metrics().separation<.01,undefined,{timeout:5000});await reassemble(page);
    await setPaused(page,true);
    const perf=await page.evaluate(()=>__uncaged.metrics().performance);
    report.performance.push({era,...perf});
  }

  await page.locator('[data-era="maker"]').click();await waitEra(page,'maker');
  await setReducedMotion(page,false);await setPaused(page,false);
  await page.evaluate(()=>__uncaged.reviewCamera('leftShoulder'));
  await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
  await screenshot(page,'maker-left-shoulder-closeup','maker','neutral','leftShoulder','rest');
  for(const channel of ['leg','wing','tail','neck','jaw']){
   await page.locator('#lever-'+channel).fill('100');await page.waitForFunction(key=>__uncaged.metrics().motion.actualArticulation[key]>.95,channel);
   await page.evaluate(name=>__uncaged.reviewCamera(name),['neck','jaw'].includes(channel)?'head':'threeQuarter');await screenshot(page,'maker-'+channel+'-control-extreme','maker','neutral','actual-control','maximum');
   await page.locator('#release-levers').click();await page.waitForFunction(()=>Object.values(__uncaged.metrics().motion.actualArticulation).every(v=>Math.abs(v)<.02));
  }
  await page.locator('#lever-leg').fill('100');await page.waitForFunction(()=>__uncaged.metrics().motion.actualArticulation.leg>.95,undefined,{timeout:3000});
  await page.evaluate(()=>__uncaged.reviewCamera('feet'));
  await screenshot(page,'maker-feet-extreme','maker','neutral','feet','left-leg-raised');
  await page.locator('#lever-leg').fill('0');await page.waitForFunction(()=>__uncaged.metrics().motion.actualArticulation.leg<.02,undefined,{timeout:3000});
  await page.locator('#lever-wing').fill('100');await page.waitForFunction(()=>__uncaged.metrics().motion.actualArticulation.wing>.95,undefined,{timeout:3000});
  await page.evaluate(()=>__uncaged.reviewCamera('leftShoulder'));
  await screenshot(page,'maker-shoulder-extreme','maker','neutral','leftShoulder','right-wing-lever');
  await page.locator('#release-levers').click();
  await page.waitForFunction(()=>Object.values(__uncaged.metrics().motion.actualArticulation).every(value=>Math.abs(value)<.02),undefined,{timeout:3000});
  await setPaused(page,true);
  await setPaused(page,false);
  let controlCycle=0;const controlValues=[15,85,35,100,55,0];
  await samplePerformance(page,'maker','manual articulation cycling',8000,async()=>{
    const value=controlValues[controlCycle++%controlValues.length];
    await page.locator('#lever-leg').fill(String(value));await page.locator('#lever-wing').fill(String(controlValues[(controlCycle+2)%controlValues.length]));
  });
  assert((await page.evaluate(()=>__uncaged.metrics().motion.actualArticulation.leg))>.1,'Maker external leg lever produces visible articulation');
  await page.locator('#release-levers').click();await setPaused(page,true);

  await page.locator('[data-era="mechanic"]').click();await waitEra(page,'mechanic');
  await setReducedMotion(page,true);await waitForSettle(page);await setPaused(page,true);
  await page.evaluate(()=>__uncaged.reviewCamera('leftShoulder'));
  await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
  await screenshot(page,'mechanic-left-shoulder-repair','mechanic','neutral','leftShoulder','rest');
  await setReducedMotion(page,false);await setPaused(page,false);
  await page.locator('#run-mechanism').click();
  await page.waitForFunction(()=>Math.abs(__uncaged.metrics().motion.root.yaw)>.15,undefined,{timeout:16000});
  await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));
  await screenshot(page,'mechanic-turn-extreme','mechanic','exhibit','threeQuarter','segmented-turn');
  await samplePerformance(page,'mechanic','wound cam routine',8000);
  await page.locator('#stop-mechanism').click();await page.waitForFunction(()=>!__uncaged.getSnapshot().routineRunning&&__uncaged.metrics().motion.settled,undefined,{timeout:8000});
  await setPaused(page,true);

  await page.locator('[data-era="builder"]').click();await waitEra(page,'builder');
  await setReducedMotion(page,true);await waitForSettle(page);await setPaused(page,true);
  await page.evaluate(()=>__uncaged.reviewLighting('neutral'));
  await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));
  await setReducedMotion(page,false);await setPaused(page,false);
  await samplePerformance(page,'builder','autonomous behavior',8000);
  await page.waitForFunction(()=>{const s=__uncaged.getSnapshot();return s.canReach&&!s.visitorPresent&&!s.paused&&!s.reducedMotion&&!s.inspection&&!s.powerMove&&!s.powerMovePending;},undefined,{timeout:20000});
  await page.locator('#power-jump').click();
  await page.waitForFunction(()=>{const move=__uncaged.getSnapshot().powerMove;return move?.kind==='jump'&&move.phase>=.40&&move.phase<=.46;},undefined,{polling:10,timeout:8000});
  await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter'));
  await screenshot(page,'builder-jump-extreme','builder','exhibit','threeQuarter','airborne');
  await waitPowerComplete(page);
  await page.waitForFunction(()=>{const s=__uncaged.getSnapshot();return s.canReach&&!s.visitorPresent&&!s.paused&&!s.reducedMotion&&!s.inspection&&!s.powerMove&&!s.powerMovePending;},undefined,{timeout:20000});
  await page.locator('#shield-thrust').click();
  await page.waitForFunction(()=>{const move=__uncaged.getSnapshot().powerMove;return move?.kind==='thrust'&&move.phase>=.48&&move.phase<=.54;},undefined,{polling:10,timeout:8000});
  await screenshot(page,'builder-thrust-extreme','builder','exhibit','threeQuarter','driven');
  await waitPowerComplete(page);
  await page.waitForFunction(()=>{const s=__uncaged.getSnapshot();return s.canReach&&!s.visitorPresent&&!s.paused&&!s.reducedMotion&&!s.inspection&&!s.powerMove&&!s.powerMovePending;},undefined,{timeout:20000});
  await page.locator('#reach-position').selectOption('0');await page.locator('#reach').click();
  await page.waitForFunction(()=>__uncaged.getSnapshot().state==='strike',undefined,{timeout:15000});
  await screenshot(page,'builder-strike-extreme','builder','exhibit','threeQuarter','strike');
  await page.locator('#retreat').click();await page.waitForFunction(()=>{const s=__uncaged.getSnapshot();return s.canReach&&!s.visitorPresent&&!s.powerMove&&!s.powerMovePending&&__uncaged.metrics().motion.settled;},undefined,{timeout:20000});

  assert.equal(report.labelLayouts.length,36,'all era/viewport/separation/view label layouts were checked');
  assert.equal(report.labelKeyboard.length,6,'each era/viewport receives a focus and Enter check');
  await check(page,'mobile controls fit a narrow viewport',async()=>{
    await page.setViewportSize({width:390,height:844});await page.waitForTimeout(800);
    const layout=await page.evaluate(()=>{
      const rendered=button=>{const r=button.getBoundingClientRect(),style=getComputedStyle(button);return !button.hidden&&r.width>0&&r.height>0&&style.display!=='none'&&style.visibility==='visible'&&Number(style.opacity)>0;};
      const required=['pause','section-toggle','reset-view','sound-toggle','power-jump','shield-thrust','reach','retreat'];
      return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,viewerWidth:document.querySelector('#viewer').getBoundingClientRect().width,
        controlsVisible:[...document.querySelectorAll('#viewer button, .secondary-controls button')].filter(rendered).length,
        missingRequiredControls:required.filter(id=>!rendered(document.getElementById(id))),
        unnamedButtons:[...document.querySelectorAll('button')].filter(button=>rendered(button)&&!button.disabled&&!button.innerText.trim()&&!button.getAttribute('aria-label')).map(button=>button.id||button.className)};
    });
    assert(layout.documentWidth<=layout.width,'page has horizontal overflow at 390 px');
    assert(layout.viewerWidth>0&&layout.controlsVisible>0,'viewer controls remain visible');
    assert.deepEqual(layout.missingRequiredControls,[],'each expected Advanced control has positive rendered bounds');
    assert.deepEqual(layout.unnamedButtons,[],'visible interactive buttons have accessible names');
    await screenshot(page,'builder-mobile-controls','builder','exhibit','threeQuarter','rest');
    return layout;
  });

  await check(page,'production preview has no development review API',async()=>{
    const production=await browser.newPage({viewport:{width:1280,height:900}});pages.push(production);observe(production,'production');
    await production.goto(productionUrl);await production.locator('#loading').waitFor({state:'hidden',timeout:30000});
    await beginStablePage(production,'production');
    assert.equal(await production.evaluate(()=>typeof window.__uncaged),'undefined');
    assert.equal(await production.locator('#scene canvas').count(),1);
    return {title:await production.title(),developmentHook:await production.evaluate(()=>typeof window.__uncaged)};
  });
  await check(page,'production fallback renders the era-specific local previews',async()=>{
    const fallback=await browser.newPage({viewport:{width:1280,height:900}});pages.push(fallback);observe(fallback,'illustrated-fallback');
    const imageResponses=new Map();
    fallback.on('response',response=>{
      if(response.request().resourceType()!=='image')return;
      imageResponses.set(response.url(),response.body().then(bytes=>({status:response.status(),bytes:bytes.length,sha256:sha256(bytes)})));
    });
    const fallbackUrl=new URL(productionUrl);fallbackUrl.searchParams.set('view','illustrated');
    await fallback.goto(fallbackUrl.href);await fallback.locator('#loading').waitFor({state:'hidden',timeout:30000});
    await beginStablePage(fallback,'illustrated-fallback');
    const results=[];
    for(const era of ['maker','mechanic','builder']){
      await fallback.locator(`[data-era="${era}"]`).click();
      await fallback.locator(`[data-era="${era}"][aria-pressed="true"]`).waitFor({state:'visible',timeout:15000});
      const image=fallback.locator('.illustrated-view img');
      await fallback.waitForFunction(target=>{
        const image=document.querySelector('.illustrated-view img');
        const name={maker:'Maker',mechanic:'Mechanic',builder:'Advanced'}[target];
        return document.querySelector(`[data-era="${target}"]`)?.getAttribute('aria-pressed')==='true'
          &&document.querySelector('.illustrated-caption')?.textContent.includes(`${name} exterior study`)
          &&image.complete&&image.naturalWidth>0;
      },era,{timeout:15000});
      const source=new URL(await image.getAttribute('src'),fallback.url()).href;
      const caption=await fallback.locator('.illustrated-caption').innerText();
      const pressedEra=await fallback.locator(`[data-era="${era}"]`).getAttribute('aria-pressed');
      const expected=expectedPreviews[era];
      const responsePromise=imageResponses.get(source);
      assert(responsePromise,`no loaded image response was recorded for ${era} preview ${source}`);
      const response=await responsePromise;
      assert.equal(response.status,200,`${era} preview response status`);
      assert.equal(response.bytes,expected.bytes,`${era} preview response byte count`);
      assert.equal(response.sha256,expected.sha256,`${era} preview response must match its source asset identity (${expected.sourcePath})`);
      const dimensions=await image.evaluate(node=>({width:node.naturalWidth,height:node.naturalHeight}));
      assert.deepEqual(dimensions,{width:expected.width,height:expected.height},`${era} preview natural dimensions`);
      assert.equal(pressedEra,'true',`${era} must remain the selected era`);
      assert.ok(caption.includes(`${eraNames[era]} exterior study`),`${era} preview caption must match the pressed era`);
      await screenshot(fallback,`${era}-fallback-preview`,era,'neutral','fixed-rendered-view','rest');
      results.push({era,source,sourcePath:expected.sourcePath,sourceSha256:expected.sha256,responseSha256:response.sha256,responseBytes:response.bytes,pressedEra,caption,...dimensions});
    }
    return results;
  });
  assert.equal(sha256(await readFile(modelPath)),modelIdentity.sha256,'model must remain unchanged throughout capture');
  report.limits='Bounded automated viewport, sampled motion and fallback checks; no full acting, swept-collision, physical-device, listening, screen-reader or sustained-performance acceptance.';
  report.status=report.errors.length?'failed':'passed';
  assert.equal(report.blockedRequests.length,0,'unexpected non-local resource requests were attempted');
  assert.equal(report.errors.length,0,'browser console/page errors found');
}catch(error){report.status='failed';report.error=String(error?.stack||error);throw error;}
finally{
  const manifestPath=path.join(outputDir,'screenshot-manifest.json');
  await writeFile(manifestPath,JSON.stringify(report.screenshots,null,2)+'\n');
  await writeFile(path.join(outputDir,'browser-validation.json'),JSON.stringify(report,null,2)+'\n');
  await Promise.all(pages.map(page=>page.close().catch(()=>{})));
  await browser.close();
}
console.log(JSON.stringify({status:report.status,screenshots:report.screenshots.length,performance:report.performance,outputDir},null,2));
