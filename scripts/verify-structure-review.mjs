// Verify the actual built preview and complete local structural review packet.
import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
if(!process.argv[2])throw Error('Pass the already installed Playwright entry module.');
const {chromium}=await import(pathToFileURL(process.argv[2]).href);
const out='assets/audit/structural-reconciliation-v1';
const b=await chromium.launch({headless:false});const p=await b.newPage({viewport:{width:1440,height:1000}});const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.route('**/*googletagmanager.com/**',r=>r.fulfill({body:''}));
try {
 await p.goto('http://127.0.0.1:4176/');await p.locator('#loading').waitFor({state:'hidden'});assert.equal(await p.evaluate(()=>typeof window.__uncaged),'undefined');assert.equal(await p.locator('#scene canvas').count(),1);
 for(const [button,state] of [['power-jump','power-jump'],['shield-thrust','power-thrust']]){
  await p.locator('#'+button).click();await p.waitForFunction(s=>document.querySelector('#viewer').dataset.behavior===s,state,{timeout:15000});await p.waitForFunction(s=>document.querySelector('#viewer').dataset.behavior!==s,state,{timeout:15000});
 }
 await p.goto('http://127.0.0.1:4176/?view=illustrated');await p.locator('#loading').waitFor({state:'hidden'});assert(await p.getByText('Modern appearance reference · fixed view',{exact:true}).isVisible());assert(await p.locator('.illustrated-view img').evaluate(i=>i.complete&&i.naturalWidth>0));
 await p.goto('http://127.0.0.1:5174/assets/audit/structural-reconciliation-v1/likeness-review.html');
 await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
 const images=await p.locator('img').evaluateAll(imgs=>imgs.map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,height:i.naturalHeight})));assert(images.length>=12);
 await p.waitForFunction(()=>document.querySelector('video').readyState>=1);
 const video=await p.locator('video').evaluate(v=>({duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error?.message||null}));assert(video.duration>100);assert.equal(video.error,null);
 await p.getByRole('button',{name:'Jump and thrust'}).click();await p.waitForFunction(()=>document.querySelector('video').currentTime>=80.9);await p.locator('video').evaluate(v=>v.pause());
 const links=await p.locator('a').evaluateAll(a=>a.map(x=>x.href));for(const url of links){const r=await p.request.get(url);assert(r.ok(),url+' '+r.status());}
 await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:out+'/review-page.png'});
 await p.setViewportSize({width:390,height:844});await p.evaluate(()=>scrollTo(0,0));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await p.screenshot({path:out+'/review-mobile.png'});
 assert.deepEqual(errors,[]);
 await writeFile(out+'/final-preview-validation.json',JSON.stringify({generatedAt:new Date().toISOString(),status:'passed',production:{webgl:true,noDevelopmentHook:true,jump:true,thrust:true,illustratedReferenceCaption:true},review:{images,video,chapters:true,links:links.length,mobileOverflow:false},errors},null,2)+'\n');
 console.log('Built controls, all review images, motion video, local links, and mobile layout passed.');
} finally {await b.close();}
