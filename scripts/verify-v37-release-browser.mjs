/** Bounded public-control smoke test for the production V37 package. */
import {pathToFileURL} from 'node:url';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
const base=process.env.V37_URL||'http://127.0.0.1:4187/';
const out=process.env.V37_OUTPUT||'.local/publication/v37-browser';
await mkdir(out,{recursive:true});
const manifest=JSON.parse(await readFile('assets/review/production-v37.json','utf8'));
const browser=await chromium.launch({channel:'chrome',headless:false});
const report={url:base,generatedAt:new Date().toISOString(),browser:browser.version(),viewport:[1440,1000],errors:[],checks:[],assets:[]};
const context=await browser.newContext({viewport:{width:1440,height:1000},deviceScaleFactor:1});
const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
page.on('response',async r=>{if(r.status()>=400&&r.url().startsWith(new URL(base).origin))report.errors.push(`${r.status()} ${r.url()}`)});
const check=label=>{report.checks.push(label);console.log(label)};
async function era(name){await page.locator(`[data-era="${name}"]`).click();await page.waitForFunction(e=>document.querySelector(`[data-era="${e}"]`).getAttribute('aria-pressed')==='true'&&document.querySelector('#era-transition').hidden,name);}
try{
 await page.goto(base);await page.locator('#loading').waitFor({state:'hidden'});
 assert.match(await page.locator('#render-label').textContent(),/^3D/);
 report.renderer=await page.evaluate(()=>{const gl=document.querySelector('canvas').getContext('webgl2');return gl.getParameter(gl.getExtension('WEBGL_debug_renderer_info').UNMASKED_RENDERER_WEBGL)});
 const release=await (await page.request.get(new URL('release.json',base).href)).json();report.revision=release.revision;
 for(const source of manifest.assets){const file=release.files.find(f=>f.sha256===source.sha256);assert(file,source.path);const r=await page.request.get(new URL(file.path,base).href);assert.equal(r.status(),200);const b=await r.body();assert.equal(createHash('sha256').update(b).digest('hex'),source.sha256);report.assets.push(file.path)}check('Exact V37 model and three fallback binaries served');
 assert.equal(await page.locator('a[href*="assets/audit"],a[href="./review/"]').count(),0);check('No public discarded-study navigation');
 await page.locator('#reduced-motion').check();await page.locator('#part-labels').uncheck();
 for(const name of ['maker','mechanic','builder']){
  await era(name);
  if(name==='maker'){for(const id of ['leg','wing','tail','neck','jaw']){await page.locator('#lever-'+id).fill('100');await page.waitForTimeout(150);await page.locator('#lever-'+id).fill('0')}check('Five Maker controls operated');}
  if(name==='mechanic'){await page.locator('#reduced-motion').uncheck();await page.locator('#run-mechanism').click();await page.waitForTimeout(2200);await page.locator('#stop-mechanism').click();await page.locator('#reduced-motion').check();check('Mechanic engage and stop controls operated');}
  await page.locator('#viewer').screenshot({path:`${out}/${name}.png`});
  await page.locator('#section-toggle').click();await page.waitForFunction(()=>!document.querySelector('#separation').disabled);await page.locator('#separation').fill('65');await page.waitForTimeout(300);await page.locator('#viewer').screenshot({path:`${out}/${name}-inspection.png`});
  await page.locator('#reassemble').click();await page.waitForFunction(()=>document.querySelector('#reassemble').disabled);check(`${name}: era, opening, separation, reassembly`);
 }
 await page.locator('#reduced-motion').uncheck();
 for(const [id,word] of [['power-jump','jump'],['shield-thrust','thrust']]){
  await page.locator('#'+id).click();await page.waitForFunction(w=>document.querySelector('#encounter-status').textContent.toLowerCase().includes(w),word);
  await page.waitForTimeout(1000);await page.locator('#viewer').screenshot({path:`${out}/${word}.png`});await page.waitForTimeout(4500);check(`Advanced ${word} started and returned control`);
 }
 await page.screenshot({path:`${out}/exhibit.png`,fullPage:true});
 const fallback=await context.newPage();await fallback.addInitScript(()=>{const original=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,...args){return /^(webgl2?|experimental-webgl)$/.test(type)?null:original.call(this,type,...args)}});
 await fallback.goto(base);await fallback.locator('#loading').waitFor({state:'hidden'});assert.match(await fallback.locator('#render-label').textContent(),/^ILLUSTRATED/);
 for(const name of ['maker','mechanic','builder']){await fallback.locator(`[data-era="${name}"]`).click();await fallback.waitForFunction(e=>document.querySelector(`[data-era="${e}"]`).getAttribute('aria-pressed')==='true',name);await fallback.waitForFunction(()=>{const i=document.querySelector('#scene img');return i&&i.complete&&i.naturalWidth>0});const src=await fallback.locator('#scene img').getAttribute('src');assert(src.includes(`${name}-preview`),src)}
 await fallback.locator('#viewer').screenshot({path:`${out}/fallback.png`});check('All three V37 illustrated fallbacks load');
 assert.equal(report.errors.length,0,JSON.stringify(report.errors));report.status='PASS';
} catch(error){report.status='FAIL';report.failure=error.stack;throw error}
finally{await writeFile(`${out}/receipt.json`,JSON.stringify(report,null,2)+'\n');await browser.close()}
