import {chromium} from '/Users/okh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs';
import {writeFile} from 'node:fs/promises';
const browser=await chromium.launch({headless:false,channel:'chrome'});
const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
 await page.goto('http://127.0.0.1:5183/');await page.locator('#loading').waitFor({state:'hidden'});
 await page.waitForFunction(()=>window.__uncaged?.metrics()?.kind==='webgl');
 await page.locator('#reduced-motion').check();await page.locator('#part-labels').uncheck();
 const frames=[];
 for(const era of ['maker','mechanic','builder']){
  await page.locator(`[data-era="${era}"]`).click();
  await page.waitForFunction(e=>__uncaged.getSnapshot().era===e&&!__uncaged.getSnapshot().pendingEra,era);
  await page.locator('#reset-view').click();
  await page.evaluate(()=>__uncaged.reviewCamera('threeQuarter')); 
  await page.waitForTimeout(500);
  await page.locator('#scene canvas').screenshot({path:`assets/models/whole-character-v37/attempt-release02/${era}-preview.png`});
  frames.push({era,metrics:await page.evaluate(()=>__uncaged.metrics())});
 }
 await writeFile('assets/audit/whole-character-v37/attempt-release02/fallback-capture.json',JSON.stringify({url:page.url(),errors,frames},null,2));
 console.log(JSON.stringify({renderer:await page.evaluate(()=>{const gl=document.querySelector('canvas').getContext('webgl2');return gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL)}),errors,frames:frames.map(f=>({era:f.era,kind:f.metrics.kind}))}));
}finally{await browser.close();}
