import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const artifact = {
  name: 'MurderBird-Three-Eras.html',
  bytes: 47_367_367,
  sha256: 'ff21d980020c4654ced6e1617df1076e63eb599e99b9af1e6461643db6ad23e9',
};
const channels = { chrome: 'Chrome', msedge: 'Edge' };

async function run() {
  const [filename, selectedChannel, ...extras] = process.argv.slice(2);
  if (!filename || (selectedChannel && !Object.hasOwn(channels, selectedChannel)) || extras.length) {
    throw new Error('Usage: node scripts/verify-three-era-windows-replay.mjs <standalone.html> [chrome|msedge]');
  }
  const sourcePath = resolve(filename);
  await verifyArtifact(sourcePath);
  const { chromium } = createRequire(import.meta.url)('playwright');
  const url = pathToFileURL(sourcePath).href;
  const report = { artifact, results: [] };
  for (const channel of selectedChannel ? [selectedChannel] : Object.keys(channels)) {
    const browser = await chromium.launch({ channel, headless: false, chromiumSandbox: true });
    const result = { browser: channels[channel], version: browser.version() };
    try {
      const options = { viewport: { width: 1440, height: 960 } };
      const interactionPage = await browser.newPage(options);
      try {
        result.runtime = await verifyRuntime(interactionPage, url);
      } finally {
        await interactionPage.context().close();
      }
      const texturePage = await browser.newPage(options);
      try {
        result.textures = await verifyTextures(texturePage, url);
      } finally {
        await texturePage.context().close();
      }
      result.passed = result.runtime.checks.length === 11
        && result.runtime.checks.every(check => check.status === 'PASS')
        && result.runtime.pageErrors === 0
        && result.textures.passed;
    } finally {
      await browser.close();
    }
    report.results.push(result);
  }
  await verifyArtifact(sourcePath);
  console.log(JSON.stringify(report, null, 2));
  if (report.results.some(result => !result.passed)) process.exitCode = 1;
}

async function verifyArtifact(path) {
  const bytes = await readFile(path);
  if (bytes.length !== artifact.bytes || createHash('sha256').update(bytes).digest('hex') !== artifact.sha256) {
    throw new Error('Input standalone size or SHA-256 differs from the recorded replay artifact.');
  }
}

async function verifyRuntime(page, url) {
  const checks=[], issues=[], requests=[];
  const assert=(ok,label)=>{if(!ok)throw new Error(label)};
  const run=async (label,step)=>{
    try{const evidence=await step();checks.push({label,status:'PASS',evidence});return evidence}
    catch(e){checks.push({label,status:'FAIL',error:redact(e.message)});return null}
  };
  const get=()=>page.evaluate(()=>window.murderBirdStudy.snapshot());
  const measured=()=>page.evaluate(()=>window.winThreeEraAudio());
  const press=(sel,key)=>page.locator(sel).press(key,{timeout:3500});
  const wait=(fn,arg,timeout=6500)=>page.waitForFunction(fn,arg,{timeout});
  const choose=era=>page.locator('[data-era="'+era+'"]').click({timeout:3500});
  const reset=()=>page.locator('#reset').click({timeout:3500});
  const peak=frames=>Math.max(0,...frames.flatMap(f=>f.peaks));
  const distance=(a,b)=>a&&b?Math.max(...a.map((x,i)=>Math.abs(x-b[i]))):null;
  page.on('pageerror',err=>issues.push(redact(err.message)));
  page.on('request',req=>{if(/^https?:|^file:/.test(req.url()))requests.push(req.url())});
  await page.addInitScript(()=>{
    const Native=window.AudioContext;
    const graphs=new WeakMap(), contexts=[];
    const starts=[],stops=[],frames=[],digestSamples=[],mediaTransitions=[];
    let serial=0;
    window.AudioContext=new Proxy(Native,{construct(target,args,newTarget){
      const ctx=Reflect.construct(target,args,newTarget);
      contexts.push(ctx);
      return ctx;
    }});
    const rawConnect=AudioNode.prototype.connect;
    const rawStart=OscillatorNode.prototype.start;
    const rawStop=OscillatorNode.prototype.stop;
    const rawDigest=SubtleCrypto.prototype.digest;
    const oscillatorIds=new WeakMap();
    const seconds=()=>performance.now()/1000;
    SubtleCrypto.prototype.digest=async function(alg,bytes){
      const result=await rawDigest.call(this,alg,bytes);
      if(bytes.byteLength>15000000)digestSamples.push({bytes:bytes.byteLength,sha256:Array.from(new Uint8Array(result),b=>b.toString(16).padStart(2,'0')).join('')});
      return result;
    };
    AudioNode.prototype.connect=function(destination,...ports){
      const result=rawConnect.call(this,destination,...ports);
      if(destination instanceof AudioDestinationNode && this instanceof GainNode && !graphs.has(this)){
        const context=this.context;
        const meter=context.createScriptProcessor(512,2,2);
        graphs.set(this,meter);
        rawConnect.call(this,meter);
        rawConnect.call(meter,destination);
        meter.onaudioprocess=e=>{
          const peaks=[];
          for(let i=0;i<2;i++){
            e.outputBuffer.getChannelData(i).fill(0);
            const channel=e.inputBuffer.getChannelData(i);
            let max=0;
            for(const v of channel)max=Math.max(max,Math.abs(v));
            peaks.push(max);
          }
          if(frames.length<9000)frames.push({wall:seconds(),audio:context.currentTime,peaks,gain:this.gain.value});
        };
      }
      return result;
    };
    OscillatorNode.prototype.start=function(...args){
      const id=++serial;
      oscillatorIds.set(this,id);
      starts.push({id,wall:seconds(),clock:this.context.currentTime,when:args[0]??null,frequency:this.frequency.value});
      return rawStart.apply(this,args);
    };
    OscillatorNode.prototype.stop=function(...args){
      stops.push({id:oscillatorIds.get(this),wall:seconds(),clock:this.context.currentTime,when:args[0]??null});
      return rawStop.apply(this,args);
    };
    matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change',e=>mediaTransitions.push({wall:seconds(),matches:e.matches}));
    window.winThreeEraAudio=()=>({context:contexts.map(c=>({state:c.state,time:c.currentTime,sampleRate:c.sampleRate})),starts,stops,frames,digestSamples,mediaTransitions});
  });
  await page.emulateMedia({reducedMotion:'no-preference'});
  await page.context().setOffline(true);
  const wallStart=Date.now();
  await page.goto(url);
  await wait(()=>typeof window.murderBirdStudy?.snapshot==='function',undefined,18000);
  const initial=await get();
  const uiBefore=await page.evaluate(()=>({poster:!document.querySelector('#poster').hidden,songPaused:document.querySelector('#song').paused,
    pilotPaused:document.querySelector('#pilot').paused,foleyPressed:document.querySelector('#sound').getAttribute('aria-pressed'),
    transportDisabled:document.querySelector('#play').disabled}));
  const idleAudio=await measured();
  await run('startup silence and entry control',async()=>{
    assert(!initial.ready&&!initial.playing&&initial.time===0&&initial.era==='advanced'&&initial.muted,'Initial scene not in Advanced poster at rest');
    assert(uiBefore.poster&&uiBefore.songPaused&&uiBefore.pilotPaused&&uiBefore.transportDisabled&&idleAudio.context.length===0&&idleAudio.starts.length===0,'Found active audio or improper controls before entry');
    return {poster:uiBefore.poster,era:initial.era,playing:initial.playing,time:initial.time,foleyMuted:initial.muted,musicPaused:uiBefore.songPaused,pilotPaused:uiBefore.pilotPaused,audioContexts:idleAudio.context.length};
  });
  const beforeEntry=Date.now();
  await page.locator('#load').click({timeout:6500});
  await wait(()=>window.murderBirdStudy.snapshot().ready,undefined,22000);
  const firstDraw=Date.now()-beforeEntry;
  await wait(()=>window.murderBirdStudy.snapshot().detail==='full',undefined,16000);
  const fullSurface=Date.now()-beforeEntry;
  const rendered=await get();
  const gpu=await page.locator('#canvas').evaluate(canvas=>{
    const gl=canvas.getContext('webgl2'); const ext=gl?.getExtension('WEBGL_debug_renderer_info');
    return {renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):null,size:[canvas.width,canvas.height],lost:gl?.isContextLost()};
  });
  const digests=(await measured()).digestSamples;
  await run('hardware WebGL and verified model bytes',async()=>{
    assert(gpu.renderer&&!/software|swiftshader|llvmpipe|basic render|warp/i.test(gpu.renderer)&&!gpu.lost&&rendered.triangles>0,'Hardware renderer not verified');
    assert(rendered.modelDigest==='20632ff6116f93827bc814d53301749dec1ef035165749db2d819bb89edcd41c','Full surface digest differed');
    assert(digests.some(x=>x.sha256===rendered.modelDigest&&x.bytes===55884688),'No measured full GLB digest');
    assert(digests.some(x=>x.sha256==='2f9ff345f3a06732367d5c1dd2d2703b924bc3061b25d7a040bf24b9b597ba54'&&x.bytes===46141044),'No measured preview GLB digest');
    assert(!rendered.playing&&rendered.time===0&&rendered.muted,'Playback or foley started automatically in 3D');
    return {...gpu,firstDrawMs:firstDraw,fullSurfaceMs:fullSurface,readySinceNavigationMs:Date.now()-wallStart,triangles:rendered.triangles,drawnFrames:rendered.frames,digests};
  });
  const inspect=async(era,region,instant)=>{
    await page.locator('#inspection-region').selectOption(region);
    const before=await get();
    await page.locator('#open').click();
    await wait(({era,region})=>{const x=window.murderBirdStudy.snapshot();return x.inspection?.era===era&&x.inspection.region===region&&x.inspection.fraction>.999;},{era,region},6500);
    const opened=await get();
    const note=await page.locator('#region-note').innerText();
    assert(opened.target===1&&!opened.playing&&opened.inspection.panels>0&&opened.inspection.compartments.length>0&&note.trim(),'No visible region separation or content: '+region);
    if(instant)assert(opened.reduced&&opened.muted,'Reduced inspection unexpectedly resumed foley or motion');
    await page.locator('#region-focus').click();
    const focused=await get();
    await press('#cut-fraction','Home');
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.target===0&&x.open===0&&x.inspection.fraction===0;},undefined,4000);
    const recovered=await get();
    assert(recovered.inspection.panels===0&&!recovered.playing&&recovered.time===0,'Region did not return to rest');
    assert(await page.locator('#cutaway').isHidden(),'Cutaway still visible after closure');
    return {era,region,panelCount:opened.inspection.panels,compartmentCount:opened.inspection.compartments.length,view:focused.view,armedBefore:before.target,opened:opened.open,closed:recovered.open};
  };
  await run('Maker five hand controls and automatic idle hold',async()=>{
    await choose('maker');
    const idle=await get();
    await page.waitForTimeout(300);
    const idleAfter=await get();
    assert(idle.era==='maker'&&idle.time===0&&!idle.playing&&distance(idle.joints.ground,idleAfter.joints.ground)===0&&distance(idle.joints.stand,idleAfter.joints.stand)===0,'Maker self-started or fixed supports drifted');
    const levers=[];
    for(const type of ['neck','leg','wing','tail','jaw']){
      await page.locator('#linkage').selectOption(type);
      await press('#handle','End');
      const full=await get();
      assert(full.gait.controls?.[type]===1&&!full.playing&&full.time===0,'No response to '+type+' lever');
      await press('#handle','Home');
      const returned=await get();
      assert(!returned.playing&&(returned.gait.controls?.[type]??0)===0,'Lever did not release: '+type);
      levers.push({type,max:full.gait.controls[type],released:returned.gait.controls?.[type]??0,mode:full.gait.mode,legLift:full.gait.leftLift});
    }
    assert((await measured()).starts.length===0,'Unwanted sound during muted operation');
    return {era:idle.era,idleTime:idleAfter.time,levers};
  });
  await run('Maker regional head inspection and closure',async()=>{await choose('maker');return inspect('maker','head',false)});
  await run('Mechanic finite winding, pause and reset',async()=>{
    await choose('mechanic');
    await page.locator('#play').click();
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.playing&&x.time>.45;});
    const first=await get();
    await page.locator('#play').click();
    const paused=await get();
    await page.waitForTimeout(260);
    const held=await get();
    assert(!paused.playing&&paused.time===held.time,'Mechanic did not pause without drift');
    await page.locator('#play').click();
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.time>=5.199&&!x.playing;},undefined,10500);
    const ended=await get();
    await page.locator('#play').click();
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.playing&&x.time>.18;});
    const opposite=await get();
    assert(first.turnDirection===-opposite.turnDirection,'Second winding did not alternate indexed direction');
    await reset();
    const rest=await get();
    assert(!rest.playing&&rest.time===0&&rest.open===0,'Mechanic reset did not return to rest');
    return {cycleEnd:ended.time,pauseClock:paused.time,freezeClock:held.time,windingDirections:[first.turnDirection,opposite.turnDirection],gait:opposite.gait.phase??opposite.gait.mode,resetClock:rest.time};
  });
  await run('Mechanic breast inspection and closure',async()=>{await choose('mechanic');return inspect('mechanic','breast',false)});
  await run('Advanced First Choice with orbit and Return to rest',async()=>{
    await choose('advanced');
    const rest=await get();
    await page.locator('#play').click();
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.playing&&x.time>.20;});
    const before=await get();
    await press('#canvas','ArrowRight');
    await wait(before=>{const n=window.murderBirdStudy.snapshot();return Math.abs(n.azimuth-before.azimuth)>.025&&n.time>before.time+.002},before,3500);
    const orbit=await get();
    assert(orbit.playing&&orbit.time>before.time&&orbit.view==='custom','Orbit interrupted First Choice');
    await wait(()=>{const x=window.murderBirdStudy.snapshot();return x.time>4.7&&x.playing;},undefined,10000);
    const motion=await get();
    await reset();
    const recovered=await get();
    assert(distance(rest.joints.ground,motion.joints.ground)===0&&distance(rest.joints.stand,motion.joints.stand)===0,'Fixed parts drifted');
    assert(distance(rest.joints.saddle,motion.joints.saddle)>1e-3&&distance(rest.joints.head,motion.joints.head)>1e-3,'No saddle or head movement measured');
    assert(recovered.time===0&&!recovered.playing&&recovered.view==='portrait','Advanced did not reset');
    return {orbit:[before.azimuth,orbit.azimuth],time:[before.time,orbit.time,motion.time,recovered.time],saddle:distance(rest.joints.saddle,motion.joints.saddle),head:distance(rest.joints.head,motion.joints.head),ground:distance(rest.joints.ground,motion.joints.ground),stand:distance(rest.joints.stand,motion.joints.stand)};
  });
  const reducedProof=await run('live reduced motion stops Advanced autonomous foley and animation',async()=>{
    await choose('advanced');
    await page.locator('#sound').click();
    await wait(()=>!window.murderBirdStudy.snapshot().muted&&window.winThreeEraAudio().context.some(c=>c.time>.065),undefined,12500);
    await page.locator('#enclosure').click();
    await wait(()=>{const s=window.murderBirdStudy.snapshot();return s.playing&&s.mode==='enclosure'&&s.time>.36;});
    const start=await get();
    await page.locator('[data-lane="center"]').click();
    await wait(()=>{
      const s=window.murderBirdStudy.snapshot(), a=window.winThreeEraAudio(), newest=a.starts.at(-1);
      return s.mode==='enclosure'&&s.playing&&s.encounter.contactCount>0&&newest&&
        a.frames.slice(-6).some(f=>f.wall>=newest.wall&&f.peaks.some(p=>p>.001));
    },undefined,10000);
    const before=await get();
    const beforeAudio=await measured();
    const triggerAt=await page.evaluate(()=>performance.now()/1000);
    await page.emulateMedia({reducedMotion:'reduce'});
    await wait(()=>{const s=window.murderBirdStudy.snapshot(); return s.reduced&&!s.playing&&s.muted;},undefined,3500);
    const frozen=await get();
    await page.waitForTimeout(650);
    const stable=await get();
    const after=await measured();
    const events=await page.evaluate(()=>window.murderBirdStudy.events());
    const contactSources=beforeAudio.starts.slice(-3);
    const cut=after.stops.filter(s=>s.when===null&&s.wall>=triggerAt&&contactSources.some(t=>s.id===t.id));
    const activeCut=cut.filter(c=>beforeAudio.stops.some(st=>st.id===c.id&&st.when!==null&&st.when>c.clock+.004));
    const signalBefore=peak(beforeAudio.frames.slice(-6));
    const silentBuffers=after.frames.filter(f=>f.wall>triggerAt+.22);
    const signalAfter=peak(silentBuffers);
    assert(before.playing&&!before.muted&&before.encounter.contactCount>=1&&signalBefore>.001,'No measured rail foley while encounter advanced');
    assert(stable.reduced&&stable.muted&&!stable.playing&&stable.time===frozen.time&&stable.mode==='enclosure','Timeline or sound not held after preference switch');
    assert(activeCut.length===3&&silentBuffers.length>15&&signalAfter===0&&after.starts.length===beforeAudio.starts.length,
      'Did not observe all contact oscillators cut while active and zero subsequent PCM: '+JSON.stringify({activeCut,signalAfter,silentBuffers:silentBuffers.length}));
    return {mode:before.mode,autonomousBeforeReach:{time:start.time,phase:start.encounter.phase},
      reachAndContact:events.filter(e=>e.event==='reach'||e.event==='contact'),
      beforeTime:before.time,frozenTime:frozen.time,heldTime:stable.time,holdMs:650,muted:stable.muted,reduced:stable.reduced,
      signalBefore,activeOscillatorsCut:activeCut.length,cutMargins:activeCut.map(c=>beforeAudio.stops.find(st=>st.id===c.id&&st.when!==null).when-c.clock),
      signalAfter,silentPcmBuffers:silentBuffers.length,mediaTransitions:after.mediaTransitions,sampleRate:after.context[0]?.sampleRate};
  });
  await run('Advanced regional inspection still usable under reduced motion',async()=>{
    if(!(await get()).reduced)await page.emulateMedia({reducedMotion:'reduce'});
    assert(reducedProof,'Autonomous reduced-motion check must pass first');
    const head=await inspect('advanced','head',true);
    const breast=await inspect('advanced','breast',true);
    await page.locator('#inspection-region').selectOption('head');
    await page.locator('#open').click();
    await wait(()=>window.murderBirdStudy.snapshot().open===1,undefined,3000);
    await reset();
    const rest=await get();
    assert(rest.reduced&&!rest.playing&&rest.time===0&&rest.muted&&rest.region==='all'&&rest.open===0,'Reduced-mode Return to rest did not restore closed static pose');
    return {regions:[head,breast],rest:{time:rest.time,playing:rest.playing,open:rest.open,muted:rest.muted,region:rest.region}};
  });
  await run('context loss fallback and Retry 3D',async()=>{
    await page.emulateMedia({reducedMotion:'no-preference'});
    const canLose=await page.locator('#canvas').evaluate(c=>{
      const ext=c.getContext('webgl2').getExtension('WEBGL_lose_context');
      if(!ext)return false;
      ext.loseContext();return true;
    });
    assert(canLose,'WEBGL_lose_context unavailable');
    await wait(()=>!window.murderBirdStudy.snapshot().ready&&!document.querySelector('#poster').hidden&&document.querySelector('#load').textContent==='Retry 3D',undefined,6500);
    const fallback=await page.evaluate(()=>({poster:document.querySelector('#poster').naturalWidth,guide:document.querySelector('#guide').open,transportDisabled:document.querySelector('#play').disabled}));
    assert(fallback.poster>0&&fallback.guide&&fallback.transportDisabled,'Fallback did not expose still/guide');
    await page.locator('#load').click({timeout:3500});
    await wait(()=>window.murderBirdStudy?.snapshot().ready&&window.murderBirdStudy.snapshot().detail==='full',undefined,28000);
    const again=await get();
    assert(!again.playing&&again.time===0&&again.muted&&!again.reduced,'Retry did not restore paused/silent full detail');
    return {fallback,recovered:{era:again.era,detail:again.detail,gpuTriangles:again.triangles,time:again.time,muted:again.muted}};
  });
  const network=requests.filter(a=>a.startsWith('http')||(a.startsWith('file:')&&a.split('#')[0]!==url));
  await run('offline boundary',async()=>{
    assert(network.length===0,'Unexpected network or companion-file request count: '+network.length); return {fileOnly:true,unrelatedRequests:network.length};
  });
  return {checks,pageErrors:issues.length,unexpectedRequests:network.length};
}

async function verifyTextures(page, url) {
  const assert=(condition,message)=>{if(!condition)throw new Error(message);};
  const watch=(p)=>{
    const rows=[];
    p.on('console',m=>{const s=m.text();if(/WebGL.*(?:INVALID|overflow)|Offset overflows texture dimensions|Rejected full.*texture/.test(s))rows.push(s);});
    return rows;
  };
  const setHooks=async(p,settings)=>{
    await p.addInitScript(({faultSite,gate})=>{
      const proto=WebGL2RenderingContext.prototype;
      const orig={create:proto.createTexture,dispose:proto.deleteTexture,storage:proto.texStorage2D,image:proto.texImage2D,sub:proto.texSubImage2D,error:proto.getError};
      const byTex=new WeakMap(), rows=[], uploads=[], errors=[], appChecks=[], simulated=[];
      let next=0,detailUrl=null,wasGated=false,release=null;
      const track=(t,context)=>{
        if(!t)return null;
        let r=byTex.get(t);
        if(!r){r={id:++next,t,context,retired:false,allocation:null};byTex.set(t,r);rows.push(r);}
        return r;
      };
      const current=(context,target)=>target===context.TEXTURE_2D?track(context.getParameter(context.TEXTURE_BINDING_2D),context):null;
      const dim=(a,sub)=>{
        if(a.length>=9)return [a[sub?4:3],a[sub?5:4]];
        const source=a[sub?6:5];
        return [source?.videoWidth||source?.width,source?.videoHeight||source?.height];
      };
      const full=(a)=>a[0]===768&&a[1]===768;
      const flatten=(r)=>({id:r.id,allocation:r.allocation,retired:r.retired});
      proto.createTexture=function(){
        const t=orig.create.call(this);
        track(t,this);
        return t;
      };
      proto.deleteTexture=function(t){const r=byTex.get(t);if(r)r.retired=true;return orig.dispose.call(this,t);};
      proto.texStorage2D=function(target,levels,format,width,height){
        const result=orig.storage.call(this,target,levels,format,width,height);
        const r=current(this,target);if(r)r.allocation=[width,height];
        return result;
      };
      proto.texImage2D=function(...a){
        const result=orig.image.apply(this,a);
        if(a[1]===0){
          const r=current(this,a[0]),d=dim(a,false);
          if(r&&d.every(x=>Number.isFinite(x)&&x>0)){
            r.allocation=d;
            if(full(d))uploads.push({id:r.id,dims:d,allocation:r.allocation,matching:true,method:'texImage2D'});
          }
        }
        return result;
      };
      proto.texSubImage2D=function(...a){
        if(a[1]===0){
          const r=current(this,a[0]),d=dim(a,true);
          if(r&&full(d)){
            const allocation=r.allocation??null;
            uploads.push({id:r.id,dims:d,allocation,matching:!!allocation&&allocation[0]===768&&allocation[1]===768&&a[2]===0&&a[3]===0,method:'texSubImage2D'});
          }
        }
        return orig.sub.apply(this,a);
      };
      proto.getError=function(){
        const value=orig.error.call(this);
        const location=String(new Error().stack).split('\n').find(s=>/\bat fv\b/.test(s));
        const site=location?.match(/:(\d+:\d+)\)?$/)?.[1]??null;
        if(value!==this.NO_ERROR)errors.push({code:value,site,wallMs:performance.now()});
        if(site)appChecks.push({site,value,wallMs:performance.now()});
        if(faultSite&&site===faultSite&&value===this.NO_ERROR&&!simulated.length){
          simulated.push({site,reported:this.INVALID_OPERATION,realValue:value,wallMs:performance.now()});
          return this.INVALID_OPERATION;
        }
        return value;
      };
      const originalFetch=window.fetch;
      if(gate){
        let resolver;
        Object.defineProperty(window,'exhibitAsset',{configurable:true,get:()=>resolver,set(fn){
          resolver=typeof fn==='function'?function(name,...args){
            const result=fn.call(this,name,...args);
            if(name==='detail.pack')detailUrl=String(result);
            return result;
          }:fn;
        }});
        window.fetch=async function(resource,...args){
          const href=String(resource?.url??resource);
          if(href===detailUrl&&!wasGated){wasGated=true;await new Promise(r=>release=r);}
          return originalFetch.call(this,resource,...args);
        };
      }
      const drain=(gl)=>{const list=[];for(let i=0;i<16;i++){const e=orig.error.call(gl);if(e===gl.NO_ERROR)break;list.push(e);}return list;};
      const points={192:[[31,151],[127,72],[62,91],[172,19],[107,155]],768:[[221,229],[371,389],[515,575],[713,687],[249,599],[643,305],[553,411],[235,700],[695,220]]};
      function readTier(size){
        const gl=document.querySelector('#canvas').getContext('webgl2');
        const before=drain(gl), samples=[];
        const wanted=rows.filter(r=>r.context===gl&&!r.retired&&r.allocation?.every(v=>v===size)
          &&gl.isTexture(r.t)&&(size!==768||uploads.some(u=>u.id===r.id)));
        const previous=gl.getParameter(gl.READ_FRAMEBUFFER_BINDING);
        const previousRead=gl.getParameter(gl.READ_BUFFER);
        const fb=gl.createFramebuffer();
        gl.bindFramebuffer(gl.READ_FRAMEBUFFER,fb);
        try{
          for(const r of wanted){
            gl.framebufferTexture2D(gl.READ_FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,r.t,0);
            const status=gl.checkFramebufferStatus(gl.READ_FRAMEBUFFER),pointsRead=[];
            if(status===gl.FRAMEBUFFER_COMPLETE){
              gl.readBuffer(gl.COLOR_ATTACHMENT0);
              for(const [x,y] of points[size]){
                const rgba=new Uint8Array(4);
                gl.readPixels(x,y,1,1,gl.RGBA,gl.UNSIGNED_BYTE,rgba);
                pointsRead.push({xy:[x,y],rgba:Array.from(rgba)});
              }
            }
            samples.push({id:r.id,status,complete:status===gl.FRAMEBUFFER_COMPLETE,allocation:r.allocation,points:pointsRead,
              rgbNonzero:pointsRead.some(p=>p.rgba.slice(0,3).some(c=>c>0)),errors:drain(gl)});
          }
        } finally {
          gl.framebufferTexture2D(gl.READ_FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,null,0);
          gl.bindFramebuffer(gl.READ_FRAMEBUFFER,previous);
          gl.readBuffer(previousRead);
          gl.deleteFramebuffer(fb);
        }
        return {size,before,samples,after:drain(gl)};
      }
      window.threeEraTextureProbe={
        gate:()=>wasGated&&!!release,
        release:()=>{const finish=release;release=null;finish?.();},
        trace:()=>({uploads:uploads.slice(),nativeErrors:errors.slice(),appChecks:appChecks.slice(),simulated:simulated.slice(),
          fullTextures:rows.filter(r=>r.allocation?.every(v=>v===768)).map(flatten)}),
        readTier
      };
    },settings);
  };
  const launch=async(p)=>{
    await p.context().setOffline(true);
    await p.goto(url);
    await p.locator('#load').click({timeout:18000});
    await p.waitForFunction(()=>window.murderBirdStudy?.snapshot().ready,undefined,{timeout:22000});
  };
  const full=async p=>{
    await p.waitForFunction(()=>window.murderBirdStudy.snapshot().detail==='full',undefined,{timeout:20000});
    await p.waitForTimeout(220);
    return p.evaluate(()=>{
      const d=window.murderBirdStudy.snapshot(), c=document.querySelector('#canvas');
      const g=c.getContext('webgl2'), x=g.getExtension('WEBGL_debug_renderer_info');
      return {detail:d.detail,digest:d.modelDigest,gpu:g.getParameter(x.UNMASKED_RENDERER_WEBGL),buffer:[c.width,c.height],
        readback:window.threeEraTextureProbe.readTier(768),trace:window.threeEraTextureProbe.trace()};
    });
  };
  const browser=page.context().browser();
  const normalWarnings=watch(page);
  await setHooks(page,{faultSite:null,gate:false});
  await launch(page);
  const normal=await full(page);
  normal.warnings=normalWarnings.slice();
  const calls=normal.trace.appChecks;
  assert(calls.length>=2,'Could not locate both native texture commit checks: '+JSON.stringify(calls));
  const commitSite=calls.at(-1).site;
  await page.close();
  const p=await browser.newPage({viewport:{width:1440,height:960}});
  const retryWarnings=watch(p);
  try{
    await setHooks(p,{faultSite:commitSite,gate:true});
    await launch(p);
    await p.waitForFunction(()=>window.threeEraTextureProbe.gate()&&window.murderBirdStudy.snapshot().detail==='first draw',undefined,{timeout:14000});
    const preview=await p.evaluate(()=>({readback:window.threeEraTextureProbe.readTier(192)}));
    const previewPng=await p.locator('#canvas').screenshot();
    await p.evaluate(()=>window.threeEraTextureProbe.release());
    await p.waitForFunction(()=>document.querySelector('#surface').textContent==='Retry full surfaces'&&!document.querySelector('#surface').hidden,undefined,{timeout:20000});
    const beforeFrame=await p.evaluate(()=>window.murderBirdStudy.snapshot().frames);
    await p.locator('[data-view="portrait"]').click();
    await p.waitForFunction(n=>window.murderBirdStudy.snapshot().frames>n,beforeFrame,{timeout:6500});
    const restored=await p.evaluate(()=>{
      const d=window.murderBirdStudy.snapshot();
      return {detail:d.detail,ready:d.ready,time:d.time,view:d.view,playing:d.playing,readback:window.threeEraTextureProbe.readTier(192),trace:window.threeEraTextureProbe.trace()};
    });
    const restoredPng=await p.locator('#canvas').screenshot();
    await p.locator('#surface').click();
    const retry=await full(p);
    retry.warnings=retryWarnings.slice();
    const pixels=read=>read.samples.map(s=>JSON.stringify(s.points.map(t=>t.rgba))).sort();
    const baseline=JSON.stringify(pixels(preview.readback)), returned=JSON.stringify(pixels(restored.readback));
    const previewMatch = {
      texturesBefore: preview.readback.samples.length,
      texturesAfter: restored.readback.samples.length,
      samplesIdentical: baseline === returned,
      canvasIdentical: previewPng.equals(restoredPng),
      pausedAtRest: restored.ready && !restored.playing && restored.time === 0,
    };
    const normalResult = summarizeTextures(normal, [normal.trace.uploads]);
    const rejectedUploadCount = restored.trace.uploads.length;
    const retryResult = summarizeTextures(retry, [
      retry.trace.uploads.slice(0, rejectedUploadCount),
      retry.trace.uploads.slice(rejectedUploadCount),
    ]);
    const [fault] = retry.trace.simulated;
    const passed = textureStagePassed(normalResult, [57])
      && textureStagePassed(retryResult, [57, 54])
      && retry.trace.simulated.length === 1 && fault.reported === 1282 && fault.realValue === 0
      && previewMatch.texturesBefore === 28 && previewMatch.texturesAfter === 28
      && previewMatch.samplesIdentical && previewMatch.canvasIdentical && previewMatch.pausedAtRest;
    return { passed, normal: normalResult, retry: retryResult, previewMatch };
  } finally {
    await p.context().close();
  }
}

function summarizeTextures(stage, attempts) {
  const { trace, readback, warnings } = stage;
  return {
    uploads: attempts.map(attempt => ({
      total: attempt.length,
      matching: attempt.filter(upload => upload.matching).length,
    })),
    textures: readback.samples.length,
    readableAbove192: readback.samples.filter(texture =>
      texture.complete && texture.rgbNonzero && !texture.errors.length).length,
    nativeErrorCodes: [
      ...trace.nativeErrors.map(error => error.code),
      ...readback.before,
      ...readback.samples.flatMap(texture => texture.errors),
      ...readback.after,
    ],
    textureWarningCount: warnings.length,
    injectedErrors: trace.simulated.map(({ reported, realValue }) => ({ reported, realValue })),
  };
}

function textureStagePassed(result, expectedUploadCounts) {
  return result.uploads.length === expectedUploadCounts.length
    && result.uploads.every((row, index) => row.total === expectedUploadCounts[index] && row.matching === row.total)
    && result.textures === 30 && result.readableAbove192 === 30
    && !result.nativeErrorCodes.length && !result.textureWarningCount;
}

function redact(message) {
  return message
    .replace(/\b(?:file|https?):\/\/[^\s"'\x60]+/gi, '[URL]')
    .replace(/(?:[A-Z]:[\\/]|\/(?:home|Users|tmp|var)\/)[^\n"'\x60]+/gi, '[path]');
}


run().catch(error => {
  console.error(redact(error.message));
  process.exitCode = 1;
});
