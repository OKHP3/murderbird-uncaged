const fs=require('node:fs'),p=require('node:path'),os=require('node:os'),h=require('node:http'),crypto=require('node:crypto'),assert=require('node:assert/strict'),readline=require('node:readline');
const {pathToFileURL}=require('node:url');
const q=require(require.resolve('playwright',{paths:[p.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
const delivery=p.resolve('../../../delivery'),kit=p.join(delivery,'kit'),three=p.resolve('../../node_modules/three'),cache=p.join(os.homedir(),'Library/Caches/ms-playwright');
const file=p.join(kit,'Open First Choice.html'),glb=p.join(kit,'first-choice.glb'),adapter=p.join(kit,'integration/attach-first-choice.js');
const sha=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const shaRequired='88ff5f671a7359c04177b77c3dc01630491189f58d24e6bc0d85d7ed98ccd12e';
const evidence={testedAt:new Date().toISOString(),portable:{filename:p.basename(file),size:fs.statSync(file).size,sha256:sha(file)},offlineBrowsers:[]};
async function embedded(){
 const banks=new Map();
 for await(const line of readline.createInterface({input:fs.createReadStream(file),crlfDelay:Infinity})){
  const m=/<script[^>]+data-first-choice-file="([^"]+)"[^>]*>([A-Za-z0-9+/=]+)<\/script>/.exec(line);
  if(!m)continue;
  const k=m[1],v=banks.get(k)??{hash:crypto.createHash('sha256'),size:0};const b=Buffer.from(m[2],'base64');v.hash.update(b);v.size+=b.length;banks.set(k,v);
 }
 const model=banks.get('first-choice.glb'),poster=banks.get('first-choice-still.jpg');
 evidence.portable.embeddedAssetCount=banks.size;
 evidence.portable.embeddedGLB={bytes:model.size,sha256:model.hash.digest('hex')};
 evidence.portable.embeddedPoster={bytes:poster.size,sha256:poster.hash.digest('hex')};
 assert.equal(evidence.portable.size,75756517);assert.equal(evidence.portable.embeddedGLB.sha256,shaRequired);assert.equal(sha(glb),shaRequired);assert.equal(fs.statSync(glb).size,model.size);
 assert.equal(sha(p.join(delivery,'web/first-choice-still.jpg')),evidence.portable.embeddedPoster.sha256);
}
const chromiumExe=p.join(cache,'chromium-1248/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing');
async function portableTest(name,flags,expectStill){
 const b=await q[name].launch({headless:true,timeout:18000,...flags});
 try{
  const page=await b.newPage({offline:true,reducedMotion:'reduce',viewport:{width:1100,height:700}});
  const requests=[],pageErrors=[],errors=[];page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>pageErrors.push(String(e)));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
  const url=pathToFileURL(file).href;
  await page.goto(url,{waitUntil:'domcontentloaded',timeout:45000});
  await page.waitForFunction(()=>['ready','fallback'].includes(window.firstChoiceReview?.getState().status),null,{timeout:40000});
  const read=()=>page.evaluate(()=>firstChoiceReview.getState());const first=await read();
  const row={engine:name,browserVersion:b.version(),webglDisabled:expectStill,offline:true,status:first.status,reducedMotion:first.reducedMotion,uncaughtPageErrors:pageErrors};
  if(expectStill){
   assert.equal(first.status,'fallback');assert.equal(first.error,'webgl-unavailable');
   await page.waitForFunction(()=>document.querySelector('#poster').naturalWidth>0);
   row.poster=await page.locator('#poster').evaluate(img=>({visible:!img.hidden,embedded:img.currentSrc.startsWith('blob:'),dimensions:[img.naturalWidth,img.naturalHeight]}));assert.ok(row.poster.visible&&row.poster.embedded);
   row.transportDisabled=await page.locator('#play').isDisabled();assert.equal(row.transportDisabled,true);
  }else{
   assert.equal(first.status,'ready');assert.equal(first.clipName,'First Choice');assert.equal(first.duration,10.5);
   assert.ok(!first.playing&&first.currentTime===0);row.clip=first.clipName;row.duration=first.duration;
   await page.locator('#replay').click();await page.waitForTimeout(300);await page.locator('#play').click();const played=await read();
   assert.ok(played.currentTime>0&&!played.playing);row.playbackReached=played.currentTime;
   await page.evaluate(()=>firstChoiceReview.seek(6.46));await page.locator('[data-view="detail"]').click();const pre=await read();
   const c=await page.locator('#viewer-canvas').boundingBox();await page.mouse.move(c.x+c.width*.5,c.y+c.height*.5);await page.mouse.down();await page.mouse.move(c.x+c.width*.56,c.y+c.height*.5,{steps:6});await page.mouse.up();
   await page.locator('[data-light="neutral"]').click();const post=await read();row.seek=post.currentTime;row.orbitDegrees=post.camera.azimuth-pre.camera.azimuth;row.lighting=post.lighting;assert.equal(row.seek,6.46);assert.ok(Math.abs(row.orbitDegrees)>3);assert.equal(row.lighting,'neutral');
   row.renderer=await page.evaluate(()=>{const g=document.querySelector('#viewer-canvas').getContext('webgl2');const e=g.getExtension('WEBGL_debug_renderer_info');return e?g.getParameter(e.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER)});
   assert.deepEqual(errors,[]);
  }
  row.httpRequests=requests.filter(u=>/^https?:/.test(u)).length;row.otherFileReads=requests.filter(u=>u.startsWith('file:')&&u!==url).length;
  assert.equal(row.httpRequests,0);assert.equal(row.otherFileReads,0);assert.deepEqual(pageErrors,[]);evidence.offlineBrowsers.push(row);console.log(name,first.status,'verified');
 }finally{await b.close()}
}
async function adapterTest(){
 const snippet=`<!doctype html><script type="importmap">{"imports":{"three":"/three/build/three.module.js","three/addons/":"/three/examples/jsm/"}}</script>
 <script type="module">
 import { GLTFLoader } from '/three/examples/jsm/loaders/GLTFLoader.js';
 import { attachFirstChoice } from '/adapter.js';
 const model=await new GLTFLoader().loadAsync('/candidate.glb');const bound=attachFirstChoice(model);const regions=['ground','stand','saddle','torso','neck','head'];
 function claim(node){for(let current=node;current;current=current.parent)if(current.userData.fc_region)return current.userData.fc_region}
 const fixed=[];model.scene.traverse(o=>{if(o.isMesh&&['ground','stand'].includes(claim(o)))fixed.push(o)});
 const times=[0,6.46,10.5,0,6.46];const shots=times.map(t=>{bound.seek(t);return {pivots:Object.fromEntries(regions.map(k=>[k,bound.pivots.get(k).matrixWorld.toArray()])),fixed:fixed.map(o=>o.matrixWorld.toArray())}});
 const max=(a,b)=>Math.max(...a.map((n,i)=>Math.abs(n-b[i])));
 const jointMax=(a,b)=>Math.max(...regions.map(k=>max(a.pivots[k],b.pivots[k])));
 const fixedNodes=Math.max(...shots.flatMap(s=>['ground','stand'].map(k=>max(s.pivots[k],shots[0].pivots[k]))));
 const rigidMax=Math.max(...shots.flatMap(s=>s.fixed.map((m,i)=>max(m,shots[0].fixed[i]))));
 const maxVsRest=Object.fromEntries(regions.map(k=>[k,max(shots[1].pivots[k],shots[0].pivots[k])]));
 window.result={duration:bound.duration,pivotRegions:regions,sampleTimes:times,fixedMeshCount:fixed.length,staticPivotMaxAbsMatrixDelta:fixedNodes,staticMeshMaxAbsMatrixDelta:rigidMax,endToOpeningMaxAbsMatrixDelta:jointMax(shots[2],shots[0]),resetMaxAbsMatrixDelta:jointMax(shots[3],shots[0]),repeatMaxAbsMatrixDelta:jointMax(shots[4],shots[1]),firstDecisionPoseMaxAbsMatrixDeltaByRegion:maxVsRest};bound.dispose();
 </script>`;
 const server=h.createServer((req,res)=>{
  const url=new URL(req.url,'http://localhost').pathname;if(url==='/')return res.writeHead(200,{'Content-Type':'text/html'}).end(snippet);
  let f=url==='/candidate.glb'?glb:url==='/adapter.js'?adapter:url.startsWith('/three/')?p.resolve(three,'.'+url.slice(6)):null;
  if(!f||!fs.existsSync(f))return res.writeHead(404).end();
  res.writeHead(200,{'Content-Type':f.endsWith('.js')?'text/javascript':'model/gltf-binary','Content-Length':fs.statSync(f).size});fs.createReadStream(f).pipe(res);
 });
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let b;
 try{b=await q.chromium.launch({headless:true,executablePath:chromiumExe,args:['--disable-gpu','--disable-background-networking']});
  const page=await b.newPage();const errors=[];page.on('pageerror',e=>{errors.push(String(e));console.error(e.message)});
  await page.goto('http://127.0.0.1:'+server.address().port);await page.waitForFunction(()=>Boolean(window.result),null,{timeout:45000});
  const r=await page.evaluate(()=>window.result);
  assert.equal(r.staticPivotMaxAbsMatrixDelta,0);assert.equal(r.staticMeshMaxAbsMatrixDelta,0);assert.ok(r.fixedMeshCount>0);assert.equal(r.duration,10.5);assert.equal(r.resetMaxAbsMatrixDelta,0);assert.equal(r.repeatMaxAbsMatrixDelta,0);assert.ok(r.endToOpeningMaxAbsMatrixDelta<1e-6);
  for(const k of ['saddle','torso','neck','head'])assert.ok(r.firstDecisionPoseMaxAbsMatrixDeltaByRegion[k]>1e-3);
  assert.deepEqual(errors,[]);evidence.integrationAdapter={path:'integration/attach-first-choice.js',sha256:sha(adapter),threeVersion:JSON.parse(fs.readFileSync(p.join(three,'package.json'),'utf8')).version,driver:'Actual Three.js GLTFLoader imported the packaged GLB in a separate loopback browser host and passed its result to the packaged adapter.',...r};console.log('adapter verified');
 }finally{await b?.close();server.close()}
}
(async()=>{await embedded();await portableTest('chromium',{executablePath:chromiumExe,args:['--use-gl=angle','--use-angle=metal','--disable-background-networking']},false);
await portableTest('webkit',{executablePath:p.join(cache,'webkit-2370/pw_run.sh')},false);
await portableTest('chromium',{executablePath:chromiumExe,args:['--disable-webgl','--disable-gpu','--disable-background-networking']},true);
await adapterTest();evidence.conclusion='PASS';evidence.limits='Desktop browser engines on this Mac. These observations do not establish mobile hardware performance, owner acceptance, or physical fit.';
const out=p.join(delivery,'evidence/portable-review.json');fs.writeFileSync(out,JSON.stringify(evidence,null,2)+'\n');console.log(out);
})().catch(e=>{console.error(e);process.exitCode=1});
