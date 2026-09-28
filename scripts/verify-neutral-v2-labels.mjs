/** Focused local verification of projected inspection labels across eras and viewports. */
import assert from 'node:assert/strict';
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the already installed Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const devUrl=process.env.UNCAGED_DEV_URL||'http://127.0.0.1:5174/';
if(!['127.0.0.1','localhost'].includes(new URL(devUrl).hostname))throw new Error('Label review is restricted to a loopback development preview.');
const outputDir=path.resolve(process.env.UNCAGED_AUDIT||'assets/audit/neutral-v2');
await mkdir(outputDir,{recursive:true});
const modelBytes=await readFile('assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb');
const report={modelSha256:createHash('sha256').update(modelBytes).digest('hex'),network:'Loopback, unthrottled; analytics stubbed',generatedAt:new Date().toISOString(),devUrl,status:'running',layouts:[],keyboard:[],screenshots:[]};
const browser=await chromium.launch({headless:false});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const widthByCombo=new Map();
report.browser=browser.version();await page.route('**/*googletagmanager.com/**',r=>r.fulfill({body:''}));

async function waitEra(era){
  await page.waitForFunction(target=>{const s=window.__uncaged?.getSnapshot?.();return s?.era===target&&!s.pendingEra;},era,{timeout:15000});
  await page.waitForFunction(()=>window.__uncaged?.metrics?.()?.kind==='webgl',undefined,{timeout:15000});
  await page.waitForFunction(target=>{const m=window.__uncaged.metrics();return m.exterior?.currentEra===target&&m.exterior.taggedObjectCount>0;},era,{timeout:10000});
}
async function waitTicks(ms=500){await page.waitForTimeout(ms);}
async function screenshot(era,width,separation,camera){
  const filename=`${era}-labels-${width}-${separation}-${camera}.png`;
  await page.locator('#viewer').screenshot({path:path.join(outputDir,filename)});
  report.screenshots.push(filename);
}

try{
  await page.goto(devUrl);
  await page.locator('#loading').waitFor({state:'hidden',timeout:30000});
  assert.equal(await page.evaluate(()=>typeof window.__uncaged?.reviewCamera),'function','development review camera is available');
  await page.locator('#reduced-motion').setChecked(true);

  for(const era of ['maker','mechanic','builder']){
    await page.locator(`[data-era="${era}"]`).click();
    await waitEra(era);
    await page.waitForFunction(()=>__uncaged.metrics()?.motion?.settled===true,undefined,{timeout:12000});
    if(!await page.evaluate(()=>__uncaged.getSnapshot().paused))await page.locator('#pause').click();
    await page.locator('#section-toggle').click();
    await page.waitForFunction(()=>window.__uncaged.getSnapshot().inspection&&window.__uncaged.metrics().open>.99,undefined,{timeout:10000});

    for(const width of [1440,390]){
      await page.setViewportSize({width,height:width===390?844:1000});
      await waitTicks(350);
      for(const separation of [0,50,100])for(const camera of ['threeQuarter','rear']){
        await page.locator('#separation').fill(String(separation));
        await page.evaluate(name=>__uncaged.reviewCamera(name),camera);
        await page.waitForFunction(target=>Math.abs(__uncaged.metrics().separation-target/100)<.02,separation,{timeout:5000});
        await waitTicks(650);
        const layout=await page.locator('#hotspots button:not([hidden])').evaluateAll(buttons=>{
          const viewer=document.querySelector('#viewer').getBoundingClientRect();
          const container=document.querySelector('#hotspots');
          const containerStyle=getComputedStyle(container);
          return {containerVisible:containerStyle.display!=='none'&&containerStyle.visibility==='visible'&&Number(containerStyle.opacity)>0,viewer:{left:viewer.left,top:viewer.top,right:viewer.right,bottom:viewer.bottom},labels:buttons.map(button=>{
            const r=button.getBoundingClientRect(),style=getComputedStyle(button);
            return {id:button.dataset.marker,x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height,visible:style.display!=='none'&&style.visibility==='visible'&&Number(style.opacity)>0,label:button.getAttribute('aria-label'),tabIndex:button.tabIndex};
          })};
        });
        assert(layout.containerVisible,`${era}/${width}: hotspot layer is visible`);
        assert(layout.labels.length>=4,`${era}/${width}/${separation}/${camera}: at least four labels remain available`);
        for(let i=0;i<layout.labels.length;i++){
          const label=layout.labels[i],v=layout.viewer;
          assert(label.visible,`${label.id}: visible`);
          assert(label.label&&label.tabIndex>=0,`${label.id}: accessible and keyboard focusable`);
          assert(label.w>=37&&label.h>=37,`${label.id}: positive 38px target bounds`);
          assert(label.x>=v.left&&label.y>=v.top&&label.right<=v.right&&label.bottom<=v.bottom,`${label.id}: inside viewer bounds`);
          for(let j=i+1;j<layout.labels.length;j++){
            const other=layout.labels[j];
            assert(Math.abs(label.x-other.x)>=Math.min(label.w,other.w)||Math.abs(label.y-other.y)>=Math.min(label.h,other.h),`${label.id}/${other.id}: projected labels do not overlap`);
          }
        }
        const key=`${era}:${separation}:${camera}`;
        if(width===1440)widthByCombo.set(key,layout.labels.length);
        else assert.equal(layout.labels.length,widthByCombo.get(key),`${key}: narrow viewport preserves the desktop label count`);

        if(separation===0&&camera==='threeQuarter'){
          const first=page.locator('#hotspots button:not([hidden])').first();
          const marker=await first.getAttribute('data-marker');
          await first.focus();
          assert.equal(await page.evaluate(()=>document.activeElement?.dataset?.marker),marker,`${era}/${width}: marker receives keyboard focus`);
          await page.keyboard.press('Enter');
          assert.equal(await page.locator(`[data-part="${marker}"]`).getAttribute('aria-pressed'),'true',`${era}/${width}: Enter activates the matching inspector item`);
          assert.equal(await page.evaluate(()=>document.activeElement?.dataset?.marker),marker,`${era}/${width}: focus remains on the marker after Enter`);
          report.keyboard.push({era,width,marker,focused:true,enterSelected:true,focusRetained:true});
        }
        report.layouts.push({era,width,separation,camera,count:layout.labels.length,labels:layout.labels});
        await screenshot(era,width,separation,camera);
      }
    }
    await page.setViewportSize({width:1440,height:1000});
    await page.locator('#separation').fill('0');
    await page.waitForFunction(()=>__uncaged.metrics().separation<.01,undefined,{timeout:5000});
    await page.locator('#reassemble').click();
    await page.waitForFunction(()=>!__uncaged.getSnapshot().inspection&&__uncaged.metrics().open===0&&__uncaged.metrics().separation===0,undefined,{timeout:10000});
  }
  assert.equal(report.layouts.length,36,'all era/viewport/separation/camera combinations were checked');
  assert.equal(report.keyboard.length,6,'keyboard focus and Enter were checked in each era at both widths');
  report.status='passed';
}catch(error){
  report.status='failed';report.error=String(error?.stack||error);throw error;
}finally{
  report.completedAt=new Date().toISOString();
  await writeFile(path.join(outputDir,'label-validation.json'),JSON.stringify(report,null,2)+'\n');
  await page.close().catch(()=>{});
  await browser.close();
}
console.log(JSON.stringify({status:report.status,layouts:report.layouts.length,keyboard:report.keyboard.length,screenshots:report.screenshots.length,outputDir},null,2));
