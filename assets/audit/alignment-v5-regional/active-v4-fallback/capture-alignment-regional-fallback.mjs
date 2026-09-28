import assert from 'node:assert/strict';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

if (!process.argv[2]) throw new Error('Pass the installed Playwright entry module as argv[2].');
const { chromium } = await import(pathToFileURL(process.argv[2]).href);
const base = new URL('../../../../', import.meta.url);
const root = path.resolve(new URL('.', base).pathname);
const out = path.dirname(new URL(import.meta.url).pathname);
const url = process.env.UNCAGED_DEV_URL || 'http://127.0.0.1:5177/?view=illustrated';
assert(['127.0.0.1','localhost'].includes(new URL(url).hostname), 'only loopback preview is allowed');
const sha = b => createHash('sha256').update(b).digest('hex');
const eraNames = { maker:'Maker', mechanic:'Mechanic', builder:'Advanced' };
const source = await readFile(path.join(root,'src/scene/fallback.js'),'utf8');
const paths = Object.fromEntries([...source.matchAll(/^\s*(maker|mechanic|builder):\s*new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.png)['"],\s*import\.meta\.url\)/gm)].map(m=>[m[1],m[2]]));
assert.deepEqual(Object.keys(paths).sort(),['builder','maker','mechanic']);
const inventory = JSON.parse(await readFile(path.join(root,'assets/models/uncaged-alignment-v4/alignment-inventory.json'),'utf8'));
const indexed = new Map(inventory.generatedFiles.map(x=>[x.path,x]));
const expected = {};
for (const era of Object.keys(eraNames)) {
  const p=paths[era], bytes=await readFile(path.join(root,p)), rec=indexed.get(p);
  assert.equal(p,`assets/models/uncaged-alignment-v4/${era}-preview.png`);
  assert(rec); assert.equal(bytes.length,rec.bytes); assert.equal(sha(bytes),rec.sha256);
  expected[era]={path:p,sha256:sha(bytes),bytes:bytes.length,width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)};
}
const browser=await chromium.launch({headless:false});
const page=await browser.newPage({viewport:{width:1280,height:900},deviceScaleFactor:1});
const errors=[], blocked=[], stubbedAnalytics=[], responses=new Map();
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
page.on('request',r=>{const u=new URL(r.url());if(u.hostname==='www.googletagmanager.com'&&u.pathname==='/gtag/js')stubbedAnalytics.push(r.url());else if(!['127.0.0.1','localhost'].includes(u.hostname)&&!['data:','blob:'].includes(u.protocol))blocked.push(r.url());});
page.route('**/*',r=>{const u=new URL(r.request().url());if(['127.0.0.1','localhost'].includes(u.hostname)||['data:','blob:'].includes(u.protocol))r.continue();else if(u.hostname==='www.googletagmanager.com'&&u.pathname==='/gtag/js')r.fulfill({status:200,contentType:'application/javascript',body:''});else r.abort();});
page.on('response',r=>{if(r.request().resourceType()==='image')responses.set(r.url(),r.body().then(b=>({status:r.status(),bytes:b.length,sha256:sha(b)})));});
const shots=[];
try {
 await page.goto(url); await page.locator('#loading').waitFor({state:'hidden',timeout:30000});
 for (const era of Object.keys(eraNames)) {
  await page.locator(`[data-era="${era}"]`).click();
  await page.locator(`[data-era="${era}"][aria-pressed="true"]`).waitFor({state:'visible'});
  await page.waitForFunction(e=>{const i=document.querySelector('.illustrated-view img');return document.querySelector(`[data-era="${e}"]`)?.getAttribute('aria-pressed')==='true'&&document.querySelector('.illustrated-caption')?.textContent.includes(`${{maker:'Maker',mechanic:'Mechanic',builder:'Advanced'}[e]} exterior study`)&&i?.complete&&i.naturalWidth>0&&i.getBoundingClientRect().width>0&&i.getBoundingClientRect().height>0;},era,{timeout:15000});
  const img=page.locator('.illustrated-view img'), src=new URL(await img.getAttribute('src'),page.url()).href;
  const response=await responses.get(src); assert(response,`missing image response ${src}`); await response;
  assert.equal(response.status,200); assert.equal(response.bytes,expected[era].bytes); assert.equal(response.sha256,expected[era].sha256);
  const visible=await img.evaluate(i=>{const r=i.getBoundingClientRect();return {naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,bounds:{x:r.x,y:r.y,width:r.width,height:r.height}};});
  assert.deepEqual({width:visible.naturalWidth,height:visible.naturalHeight},{width:expected[era].width,height:expected[era].height});
  assert(visible.bounds.width>0&&visible.bounds.height>0);
  const caption=await page.locator('.illustrated-caption').innerText();
  const filename=`${era}-fallback.png`, filepath=path.join(out,filename);
  await page.locator('#viewer').screenshot({path:filepath}); const shot=await readFile(filepath);
  shots.push({era:eraNames[era],filename,screenshotSha256:sha(shot),screenshotBytes:shot.length,sourceUrl:src,sourcePath:expected[era].path,sourceSha256:expected[era].sha256,responseSha256:response.sha256,responseBytes:response.bytes,httpStatus:response.status,caption,selected:await page.locator(`[data-era="${era}"]`).getAttribute('aria-pressed'),...visible});
 }
 assert.equal(blocked.length,0,JSON.stringify(blocked)); assert.equal(errors.length,0,JSON.stringify(errors));
 const receipt={scope:'unchanged active V4 illustrated fallback assets only; these are not fallback images generated from or representing the combined V5 regional candidate',capturedAt:new Date().toISOString(),url,browser:browser.version(),runtime:'Playwright Chromium headed, local loopback',sourceCode:{path:'src/scene/fallback.js',sha256:sha(Buffer.from(source))},inventory:{path:'assets/models/uncaged-alignment-v4/alignment-inventory.json',sha256:sha(await readFile(path.join(root,'assets/models/uncaged-alignment-v4/alignment-inventory.json')))},status:'passed',errors,blockedRequests:blocked,stubbedAnalyticsRequests:stubbedAnalytics,results:shots};
 await writeFile(path.join(out,'fallback-receipt.json'),JSON.stringify(receipt,null,2)+'\n');
} finally { await browser.close(); }
