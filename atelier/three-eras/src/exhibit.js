import * as T from 'three'
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js'
import {OrbitControls} from 'three/addons/controls/OrbitControls.js'
import {makeStage} from './stage.js'
import {createFoley} from './foley.js'
import {installEncounter} from './encounter.mjs'
import {installLocomotion} from './locomotion.mjs'
import {installEraArt} from './era-art.mjs'
import {installInspection} from './inspection.js'
import {fetchModel,applyDetail} from './transport.js'
import {installMedia} from './media.js'
import {regionOptions,regionViews,regionCopy} from './regions.js'

const el=id=>document.getElementById(id)
const reduced=matchMedia('(prefers-reduced-motion: reduce)')
const data={
 maker:{name:'Maker · The body',action:'Operate the lever',seconds:0,
 caption:'An outside hand works the bronze bird. Its dark eye stays fixed until you move the lever.',
 walk:'Move the lever to raise the linkage, then return it to lower the head. The bird stays on its support. Open the shell to follow the external control into the body.',
 inside:'Follow the handle into the bronze linkage. Movement starts with an operator outside the body.'},
 mechanic:{name:'Mechanic · The winding',action:'Wind the clockwork',seconds:5.2,
 caption:'Wind the spring. The repaired assembly advances through a finite cam cycle, reaches its stop and rests with the eye dark.',
 walk:'Wind once to start a short cycle. Watch the cam lift, hold and release the follower. The cycle ends without a second winding. Open the shell to inspect the train.',
 inside:'The clockwork occupies the chest cavity. Industrial repairs and the spring assembly distinguish this body from the Maker’s casting.'},
 advanced:{name:'Advanced · First Choice',action:'Play First Choice',seconds:10.5,
 caption:'The saddle gives. The feet hold. The bird shifts its weight and lowers its head toward the bolt before anyone asks.',
 walk:'Choose Saddle. The support yields, the torso takes the load over planted talons and the head finally inclines. Approach the rail for a separate encounter. Open the exterior to inspect the chest and head.',
 inside:'The power cells sit in the chest. The processing lattice sits behind the eye in the head. The inherited left shoulder still limits its reach.'},
}
const views={portrait:[[0,.99,.07],-65,7,4.35,1.7],profile:[[0,.99,.09],-89,3,4.33,1.7],detail:[[-.07,1.68,.27],-72,7,1.65,.84],support:[[-.1,.81,.44],-59,12,2.44,1.03],interior:[[0,1.21,.06],-70,8,3.55,1.55]}
Object.assign(views,regionViews)
for(const [value,label] of Object.entries(regionOptions)){el('inspection-region').add(new Option(label,value))}
const state={region:'all',era:'advanced',mode:'advanced',ready:false,busy:false,playing:false,time:0,open:0,target:0,view:'portrait',light:'workshop',frames:0}
let playbackBeganReduced=false;
let loadEpoch=0,lastOpen=0,encounter,visits=0,lastContact=0
const seedBase=Number(new URLSearchParams(location.search).get('seed'))||0
let winding=0,turnDirection=1
let saddleRocked=false
let gait,manualValues={leg:0,wing:0,tail:0,neck:0,jaw:0}
let scene,camera,renderer,orbit,stage,root,mixer,clip,art,inside,pivots,rest,frame,cage,readyAt,renderTime,driveClock
const foley=createFoley()
const source=name=>window.exhibitAsset?.(name) ?? new URL('assets/'+name,document.baseURI).href
const buttons=selector=>Array.from(document.querySelectorAll(selector))
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v))
const bell=x=>Math.sin(Math.PI*clamp(x))
function repaint() { if(!frame && state.ready && !document.hidden) frame=requestAnimationFrame(draw) }
function setCam(key) {
  state.view=key
  if (!orbit) return
  const [target,a,e,d,width]=views[key],az=a*Math.PI/180,elv=e*Math.PI/180
  const dist=Math.max(d,width/(2*Math.tan(camera.fov*Math.PI/360)*camera.aspect))
  orbit.target.fromArray(target);camera.position.set(Math.sin(az)*Math.cos(elv),Math.sin(elv),Math.cos(az)*Math.cos(elv)).multiplyScalar(dist).add(orbit.target)
  orbit.update();for(const b of buttons('[data-view]')) b.setAttribute('aria-pressed',String(b.dataset.view===key));repaint()
}
function resize(){
  if(!renderer)return
  const w=el('stage').clientWidth,h=el('stage').clientHeight;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix()
  if(views[state.view])setCam(state.view);repaint()
}
function duration(){return state.mode==='enclosure'?Infinity:state.mode==='patrol'?8:state.mode==='approach'?4.6:data[state.era].seconds}
function updateUI(){
 const era=data[state.era]
 el('era-title').textContent=era.name;el('manual').hidden=state.era!=='maker';el('transport').hidden=state.era==='maker'||state.mode==='enclosure';el('visitor').hidden=state.mode!=='enclosure'||!state.ready;el('enclosure').hidden=state.era!=='advanced'
 el('play').hidden=state.era==='maker';el('approach').hidden=el('patrol').hidden=state.era!=='advanced'
 el('play').textContent=state.playing?'Pause':state.time>0&&state.time<duration()?'Resume':era.action
 el('open').textContent=state.target?'Reassemble':'Open the exterior';el('open').setAttribute('aria-expanded',String(Boolean(state.target)))
 el('cut-fraction').value=Math.round(state.target*100);el('cut-fraction').setAttribute('aria-valuetext',Math.round(state.target*100)+' percent open');el('cutaway').hidden=!state.target;el('cutaway').textContent=state.region==='all'?era.inside:regionCopy(state.era,state.region);el('region-note').textContent=regionCopy(state.era,state.region);el('inspection-region').value=state.region
 el('sound').textContent=foley.enabled?'Mute foley':'Enable foley';el('sound').setAttribute('aria-pressed',String(foley.enabled))
 el('light').textContent=state.light==='workshop'?'Neutral light':'Workshop light'
 el('position').max=Number.isFinite(duration())?(duration()||1):1;el('position').value=state.time;el('clock').value=state.time.toFixed(1)+' s'
 el('walk').textContent=era.walk
 for(const b of buttons('[data-era]')) b.setAttribute('aria-pressed',String(b.dataset.era===state.era))
 for(const b of [...buttons('[data-view]'),...['play','approach','patrol','enclosure','linkage','position','open','sound','reset','handle','light','cut-fraction','inspection-region','region-focus'].map(el)])b.disabled=!state.ready
}
function stop(){state.playing=false;driveClock=undefined;foley.silence()}
function seek(t) {stop();state.time=clamp(t,0,duration());sample();updateUI();repaint()}
function setEra(era) {
 stop();encounter?.reset(seedBase+visits);lastContact=0;state.era=era;state.region='all';state.mode=era;state.time=0;state.open=0;state.target=0;manualValues={leg:0,wing:0,tail:0,neck:0,jaw:0};el('handle').value=0
 gait?.set('rest',0);if(inside)inside.setOpen(0);lastOpen=0
 art?.setEra(era);inside?.setEra(era);inside?.setRegion('all')
 if(stage){stage.setLighting(state.light);if(state.light==='workshop')renderer.toneMappingExposure*=({maker:1.09,mechanic:.88,advanced:1})[era]}
 el('caption').textContent=data[era].caption
 el('poster').src=source(era+'.jpg');el('poster').alt='Front-left view of the '+era+' bird in its enclosure.'
 el('guide-image').src=source(era+'-open.jpg');el('guide-image').alt='Open '+era+' shell with its era-specific interior visible.'
 setCam('portrait');sample();updateUI();repaint()
}
function rotate(region,x,y=0,z=0) {
 const p=pivots[region];p.quaternion.copy(rest[region]).multiply(new T.Quaternion().setFromEuler(new T.Euler(x,y,z)))
}
function sample() {
 if(!root)return
 if(saddleRocked){pivots.saddle.quaternion.copy(rest.saddle);saddleRocked=false}
 let saddleRelease=0
 const moving=state.era==='mechanic'||state.mode==='patrol'||state.mode==='enclosure'||state.era==='maker'
 if(!moving||state.open||state.target)gait.set('rest',0)
 if(lastOpen!==state.open){inside.setOpen(state.open);lastOpen=state.open}
 clip.time=state.era==='advanced'&&state.mode==='advanced'?state.time:0;mixer.update(0)
 const p=state.era==='maker'?Number(el('handle').value)/100:state.time/duration()
 if(state.era==='maker'&&!state.target&&!state.open){
   gait.manual(manualValues);saddleRelease=.045*manualValues.leg
 }
 if(state.era==='mechanic'&&!state.target&&!state.open){
   // The wound bird steps away from the planted bed. At load transfer the
   // existing shoe rocks on its axle; once the bird steps clear it stays still.
   gait.set('mechanic',p,{turn:turnDirection,stride:-1})
   const step=gait.snapshot(), supported=clamp(1-Math.abs(step.bodyFore)/.045)
   saddleRelease=1.4*Math.max(step.leftLift,step.rightLift)*supported
   const a=Math.PI*2*clamp(p),stroke=.5-.5*Math.cos(3*a)
   rotate('neck',.108*stroke);rotate('head',.11*stroke)
 }
 if(state.mode==='patrol'&&!state.target&&!state.open){
   gait.set('patrol',p);const look=Math.sin(2*Math.PI*p)*Math.sin(Math.PI*p);rotate('neck',.045*look,-.17*look);rotate('head',-.07*look,-.14*look)
 }
 pivots.stand.visible=!['patrol','enclosure'].includes(state.mode)
 if(state.mode==='enclosure'&&!state.open&&!state.target){
  const e=encounter.sample(state.time)
  if(el('caption').textContent!==e.label)el('caption').textContent=e.label
  if(e.contactCount>lastContact && state.playing)foley.contact(e.lane)
  lastContact=e.contactCount
 }
 if(state.mode==='approach'){
   const attention=bell(state.time/4.6),reach=bell((state.time-1.55)/1.55)
   saddleRelease=.143*reach+.009*attention
   rotate('torso',.07*reach,0,-.022*attention);rotate('neck',.12*reach,-.19*attention);rotate('head',-.17*attention+.19*reach,-.20*attention)
 }
 // The shoe gives at its retained transverse bearing; the stand base,
 // shaft and foot surfaces remain in their authored frames.
 if(saddleRelease){pivots.saddle.rotateX(-saddleRelease);saddleRocked=true}
 if(state.era==='maker')art.setControls(manualValues);else art.setPose(clamp(p));inside.setMotion?.(clamp(p));root.updateMatrixWorld(true)
}
function clock(){return foley.enabled?foley.time:performance.now()/1000}
function play(mode){
 if(!state.ready||state.era==='maker')return
 if(mode==='mechanic' && (state.time===0||state.time>=duration()))turnDirection=++winding%2?1:-1
 if(state.mode!==mode||state.time>=duration()){state.mode=mode;state.time=0}
 state.target=0;state.open=0;if(lastOpen){inside.setOpen(0);lastOpen=0};playbackBeganReduced=reduced.matches;state.playing=true;driveClock=clock();updateUI();repaint()
}
function draw(now){
 frame=undefined;if(!state.ready||document.hidden)return
 if(state.playing&&reduced.matches&&!playbackBeganReduced)applyReducedMotion()
 const dt=clamp((now-(renderTime??now))/1000,0,.1);renderTime=now
 if(state.playing){
   const t=clock(),last=state.time;state.time=clamp(last+Math.max(0,t-driveClock),0,duration());driveClock=t
   foley.advance(state.mode,last,state.time,Math.cos(orbit.getAzimuthalAngle()+1.0))
   if(state.time>=duration())stop()
 }
 if(state.open!==state.target)state.open+=Math.sign(state.target-state.open)*Math.min(Math.abs(state.target-state.open),dt*1.7)
 sample();renderer.render(scene,camera);state.frames++;el('position').value=state.time;el('clock').value=state.time.toFixed(1)+' s'
 if(state.playing||state.open!==state.target)repaint();else updateUI()
}
function inspect(){
 if(state.mode==='enclosure')setEra(state.era)
 stop();state.time=0;for(const key of Object.keys(manualValues))manualValues[key]=0;el('handle').value=0;state.target=state.target?0:1
 if(reduced.matches)state.open=state.target
 if(state.target)setCam('region-'+state.region)
 updateUI();sample();repaint()
}
function addRail(){
 const group=new T.Group(),mat=new T.MeshStandardMaterial({color:0x554b3f,metalness:.68,roughness:.62})
 const line=(a,b,r)=>{const x=new T.Vector3(...a),y=new T.Vector3(...b),v=y.clone().sub(x);const m=new T.Mesh(new T.CylinderGeometry(r,r,v.length(),10),mat);m.position.copy(x).addScaledVector(v,.5);m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),v.normalize());group.add(m)}
 // Low visitor rail marks the perimeter while leaving sightlines open.
 for(const x of [-1.25,1.25])for(const z of [-1.15,1.26])line([x,0,z],[x,.50,z],.023)
 for(const z of [-1.15,1.26])line([-1.25,.49,z],[1.25,.49,z],.014)
 for(const x of [-1.25,1.25])line([x,.49,-1.15],[x,.49,1.26],.014)
 group.name='Exhibit boundary';scene.add(group);return group
}
function fallback(text){
 loadEpoch++;stop();state.busy=false;state.ready=false;foley.mute();el('entry').hidden=false;el('load').hidden=false;el('load').textContent='Retry 3D';el('load-status').textContent=text
 el('poster').hidden=false;el('canvas').hidden=true;el('guide').open=true;updateUI()
}
async function load(){
 if(state.busy||state.ready)return
 if(renderer && !state.ready && el('load').textContent==='Retry 3D'){const dest=new URL(location.href);dest.hash='enter-3d';location.replace(dest.href);location.reload();return}
 const epoch=++loadEpoch;state.busy=true;el('load').hidden=true;el('load-status').textContent='Opening the workshop…'
 try{
  const canvas=el('canvas');renderer=new T.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'})
  renderer.setPixelRatio(Math.min(devicePixelRatio,1.5));renderer.outputColorSpace=T.SRGBColorSpace;renderer.toneMapping=T.ACESFilmicToneMapping;renderer.shadowMap.enabled=true
  if(window.exhibitAsset)T.DefaultLoadingManager.setURLModifier(url=>{if(/^(blob|data):/.test(url))return url;return window.exhibitAsset(new URL(url,document.baseURI).pathname.split('/').pop())})
  scene=new T.Scene();camera=new T.PerspectiveCamera(30,1,.025,75);orbit=new OrbitControls(camera,canvas);orbit.enablePan=false;orbit.minDistance=.55;orbit.maxDistance=9;orbit.maxPolarAngle=1.64;orbit.minPolarAngle=.17
  orbit.addEventListener('change',repaint);orbit.addEventListener('start',()=>{state.view='custom';for(const b of buttons('[data-view]'))b.setAttribute('aria-pressed','false')})
  stage=makeStage(renderer,scene);cage=addRail();resize();new ResizeObserver(resize).observe(el('stage'))
  const first=await fetchModel(source('bird.pack'))
  if(epoch!==loadEpoch)return
  const gltf=await new GLTFLoader().parseAsync(first,'')
  if(epoch!==loadEpoch||renderer.getContext().isContextLost())return
  root=gltf.scene;scene.add(root);pivots={};rest={}
  root.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}if(o.userData.fc_region){pivots[o.userData.fc_region]=o;rest[o.userData.fc_region]=o.quaternion.clone()}})
  mixer=new T.AnimationMixer(root);clip=mixer.clipAction(gltf.animations.find(c=>c.name==='First Choice'));clip.setLoop(T.LoopOnce,1);clip.clampWhenFinished=true;clip.play();clip.paused=true
  art=installEraArt(T,root,scene);inside=installInspection(T,root,scene);gait=installLocomotion(T,root,scene);encounter=installEncounter(T,root,scene,gait)
  state.ready=true;state.busy=false;canvas.hidden=false;el('announce').textContent='Model ready. Use the arrow keys to orbit.';canvas.focus({preventScroll:true});el('poster').hidden=true;el('entry').hidden=true
  setEra(state.era);renderer.render(scene,camera);readyAt=performance.now();state.detail='first draw'
  const finishDetail=async()=>{
    try{
      const digest=await applyDetail(source('detail.pack'),first,gltf,renderer)
      if(epoch!==loadEpoch)return
      state.detail='full';state.modelDigest=digest;el('surface').hidden=true;repaint()
    }catch(e){
      if(epoch!==loadEpoch)return
      state.detail='first draw';el('surface').hidden=false;el('surface').disabled=false;el('surface').textContent='Retry full surfaces';el('surface').onclick=()=>{el('surface').disabled=true;finishDetail()}
    }
  }
  requestAnimationFrame(()=>requestAnimationFrame(finishDetail))
 }catch(error){if(epoch!==loadEpoch)return;console.error(error);fallback('3D unavailable. The illustrated walkthrough is ready.')}
}
for(const b of buttons('[data-era]'))b.onclick=()=>setEra(b.dataset.era)
for(const b of buttons('[data-view]'))b.onclick=()=>setCam(b.dataset.view)
el('load').onclick=load
el('play').onclick=()=>{if(state.playing){stop();updateUI()}else if(state.time>0&&state.time<duration())play(state.mode);else {if(state.mode!==state.era)setEra(state.era);play(state.era)}}
el('enclosure').onclick=()=>{setEra('advanced');encounter.reset(seedBase+visits++);lastContact=0;state.mode='enclosure';play('enclosure')}
for(const b of buttons('[data-lane]'))b.onclick=()=>{if(state.mode==='enclosure'){encounter.reach(b.dataset.lane,state.time);play('enclosure')}}
el('withdraw').onclick=()=>{if(state.mode==='enclosure'){encounter.retreat(state.time);play('enclosure')}}
el('patrol').onclick=()=>{setEra('advanced');state.mode='patrol';el('caption').textContent='Away from its saddle, the bird paces inside the rail. One foot takes the load while the other advances. The old left shoulder stays close.';play('patrol')}
el('approach').onclick=()=>{setEra('advanced');state.mode='approach';state.time=0;el('caption').textContent='Inside the rail, the bird fixes on the visitor, leans toward the boundary, then eases back.';play('approach')}
el('reset').onclick=()=>setEra(state.era)
el('position').oninput=()=>seek(+el('position').value)
let lastDetent=0
el('linkage').onchange=()=>{el('handle').value=manualValues[el('linkage').value]*100;lastDetent=Math.round(+el('handle').value*.08)}
el('handle').oninput=()=>{const v=+el('handle').value/100;manualValues[el('linkage').value]=v;state.target=state.open=0;const next=Math.round(v*8);if(next!==lastDetent)foley.hand(v);lastDetent=next;sample();updateUI();repaint()}
el('inspection-region').onchange=()=>{
 const selection=el('inspection-region').value
 if(state.mode==='enclosure')setEra(state.era)
 stop();state.time=0;for(const k of Object.keys(manualValues))manualValues[k]=0;el('handle').value=0
 gait.set('rest',0);state.region=selection;inside.setRegion(selection);setCam('region-'+selection);sample();updateUI();repaint()
}
el('region-focus').onclick=()=>setCam('region-'+state.region)
el('open').onclick=inspect
el('cut-fraction').oninput=()=>{
 const fraction=+el('cut-fraction').value/100;if(state.mode==='enclosure')setEra(state.era)
 stop();state.time=0;for(const key of Object.keys(manualValues))manualValues[key]=0;el('handle').value=0;state.target=state.open=fraction
 if(state.target)setCam('region-'+state.region);sample();updateUI();repaint()
}
el('light').onclick=()=>{state.light=state.light==='workshop'?'neutral':'workshop';stage.setLighting(state.light);updateUI();repaint()}
el('sound').onclick=async()=>{stop();try{if(foley.enabled)foley.mute();else {media.pause();await foley.enable()}}catch{el('caption').textContent='Foley unavailable. The scene can be played silently.'}updateUI()}
const media=installMedia(source,()=>{foley.mute();updateUI()})
el('canvas').onkeydown=e=>{
 if(!orbit)return
 const d=new T.Spherical().setFromVector3(camera.position.clone().sub(orbit.target));const step=(e.shiftKey?15:5)*Math.PI/180
 if(e.key==='Home'){e.preventDefault();setCam('portrait');return}
 if(e.key==='ArrowRight')d.theta+=step;else if(e.key==='ArrowLeft')d.theta-=step;else if(e.key==='ArrowUp')d.phi-=step;else if(e.key==='ArrowDown')d.phi+=step;else if(['+','='].includes(e.key))d.radius/=1.12;else if(e.key==='-')d.radius*=1.12;else return
 e.preventDefault();d.phi=clamp(d.phi,.17,1.64);d.radius=clamp(d.radius,.55,9);camera.position.setFromSpherical(d).add(orbit.target);state.view='custom';for(const b of buttons('[data-view]'))b.setAttribute('aria-pressed','false');orbit.update();repaint()
}
el('canvas').addEventListener('webglcontextlost',e=>{e.preventDefault();fallback('3D was interrupted. Continue with the illustrated walkthrough.')})
document.addEventListener('visibilitychange',()=>{if(document.hidden){stop();foley.mute();media.pause();updateUI()}else repaint()})
function applyReducedMotion(){stop();foley.mute();media.pause();state.open=state.target;sample();updateUI();repaint()}
reduced.addEventListener('change',()=>{if(reduced.matches)applyReducedMotion()})
window.murderBirdStudy={cameraPose(target,offset,fov){
 if(!orbit||![target,offset].every(v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite))||!Number.isFinite(fov))return false
 orbit.target.fromArray(target);camera.position.fromArray(offset).add(orbit.target);camera.fov=clamp(fov,12,75);camera.updateProjectionMatrix();state.view='custom';orbit.update();repaint();return true
},events:()=>encounter?.events()??[],snapshot:()=>({...state,readyAt,remaining:duration()-state.time,turnDirection,inspection:inside?.snapshot(),gait:gait?.snapshot(),encounter:encounter?.snapshot(),cues:foley.count,muted:!foley.enabled,reduced:reduced.matches,triangles:renderer?.info.render.triangles,azimuth:orbit?.getAzimuthalAngle(),joints:root&&Object.fromEntries(Object.entries(pivots).map(([k,v])=>[k,v.matrixWorld.toArray()]))})}
setEra('advanced')
if(location.hash==='#enter-3d'){try{history.replaceState(null,'',location.href.split('#')[0])}catch{};load()}
