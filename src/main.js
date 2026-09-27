import './style.css';
import './fallback.css';
import { createExhibit } from './scene/exhibit.js';
import { createIllustratedExhibit } from './scene/fallback.js';
import { createEncounterState } from './scene/encounter-state.js';
import { createSoundscape } from './audio/soundscape.js';

const eras = {
  maker:{name:'I · Maker',summary:'Handworked bronze. No heart. No brain. The original means of movement remains unexplained in the story.',drive:'The surviving story does not establish the original mechanism. This space is deliberately unresolved; the exhibit does not insert a modern motor or certify an ancient spring design.',power:'No onboard heart is established in this generation.',mind:'No brain is claimed. The story describes early actions and a removed assembly behind the eyes; its function remains unresolved.'},
  mechanic:{name:'II · Mechanic',summary:'Iron repairs and brass bearings. Wound or externally supplied energy produces finite, repeated movement. No heart or brain.',drive:'The story describes workshop belts, pressure lines and wound springs. This drum, arbor and transmission illustrate stored energy passing into movement. Their exact arrangement is a reconstruction.',power:'There is no Builder heart. Wound springs carry only a few untethered steps in the story; external power and stored mechanical energy are distinct from cognition.',mind:'The cranial chamber stays empty. Six attempted assemblies fail to supply the missing capability. A triggered sequence is not learning.'},
  builder:{name:'III · Builder',summary:'The inherited body gains two separate additions: finite onboard power in the breast, and processing behind the eyes.',drive:'Inherited linkages transmit force through the repaired body. The modern power core replaces the old spring drum in this study; actuation topology remains illustrative.',power:'Dense ceramic cells provide steady power; capacitors supply brief surges. A sealed cradle protects the core. This is a fictional finite energy source, not a biological heart or exposed glowing reactor.',mind:'A processing lattice behind the eyes is distinct from the power core. In the story, processing learns from experience. The geometry here illustrates the relationship; it is not a working AI or engineering design.'},
};
const parts=[
  {id:'beak',name:'Bill & skull',title:'A tool with a dangerous edge.',text:'The deep recurved bill, recessed circular optic and segmented crown come from the selected production reference. The hinge and unseen rear surfaces are reconstructed for this study.'},
  {id:'joint',name:'Load & articulation',title:'Weight has a path.',text:'Broad three-toed feet support the body. Pins, bearing collars and paired rods suggest force passing through the legs. The left shoulder carries the inherited repair; this study does not establish its exact historical topology.'},
  {id:'shell',name:'Breastplate',title:'Open the inherited body.',text:'Overlapping armor is separate from the internal frame. The breastplate swings aside in inspection. Dashed lines retain assembly relationships when the parts separate.'},
  {id:'drive',name:'Winding & transmission',title:'Energy becomes movement.'},
  {id:'power',name:'Heart · power',title:'Power is one missing part.'},
  {id:'mind',name:'Mind · processing',title:'Processing is the other.'},
];
const app=document.querySelector('#app');
app.innerHTML=`<a class="skip-link" href="#controls">Skip to exhibit controls</a><div class="site-shell">
<header class="topbar"><a class="wordmark" href="#top"><span class="mark">M/B</span><span>MURDERBIRD<small>UNCAGED</small></span></a><nav aria-label="Main navigation"><a href="#field-notes">Construction record</a><a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Origin story ↗</a></nav><span class="edition">LOCAL ASSEMBLY STUDY / 01</span></header>
<main id="top"><section class="exhibit" id="specimen" aria-labelledby="exhibit-title">
<div class="exhibit-heading"><div><p class="eyebrow">AN ENCOUNTER WITH AN IMPOSSIBLE MACHINE</p><h1 id="exhibit-title">MurderBird: <em>Uncaged.</em></h1></div><p>Drag to orbit. Scroll or pinch to move closer.<br>Reach deliberately. Open it when you’re ready.</p></div>
<div class="exhibit-grid"><div class="viewer-column"><div class="viewer" id="viewer">
<div class="viewer-top"><span id="render-label">LOADING ASSEMBLY…</span><span id="era-label">III · BUILDER</span></div>
<div id="scene" aria-label="MurderBird exhibit"></div><div id="hotspots" class="hotspots"></div><div class="loading" id="loading" role="status">Preparing the mechanical assembly…</div>
<div class="viewer-bottom"><span id="view-label">ENCLOSURE / EXTERIOR</span><span>LIKENESS REVIEW PENDING</span></div>
</div>
<div id="controls" class="toolbar" role="group" aria-label="Encounter and inspection controls" tabindex="-1">
<button id="reach" type="button" class="primary">Reach toward bars</button><button id="arm-reach" type="button" aria-pressed="false">Aim a reach</button><button id="section-toggle" type="button" aria-pressed="false">Open for inspection</button><button id="reset-view" type="button">Reset view</button></div>
<p id="encounter-status" class="encounter-status" role="status">Loading the specimen.</p>
<div class="inspection-controls"><label for="separation">Separate assembly <output id="separation-value">0%</output></label><input id="separation" type="range" min="0" max="100" step="1" value="0" disabled /><button id="reassemble" type="button" disabled>Reassemble & return</button></div>
<div class="secondary-controls"><div class="view-controls" role="group" aria-label="Camera controls"><button data-view="left" aria-label="Orbit left">←</button><button data-view="right" aria-label="Orbit right">→</button><button data-view="up" aria-label="Raise viewpoint">↑</button><button data-view="down" aria-label="Lower viewpoint">↓</button><button data-view="in" aria-label="Zoom in">+</button><button data-view="out" aria-label="Zoom out">−</button></div><button id="pause" type="button" aria-pressed="false">Calm / pause</button><label class="motion-label"><input id="reduced-motion" type="checkbox" /> Reduced motion</label><button id="sound-toggle" type="button" aria-pressed="false">Sound off</button></div>
<p class="viewer-note" id="viewer-note">Reference-informed 3D reconstruction under review. The cage is an exhibit device; hidden surfaces and mechanisms are proposals. Music starts only when you choose Play.</p>
<button id="retry" class="retry" type="button" hidden>Retry 3D</button>
</div><aside class="inspector" aria-label="Construction details"><div class="inspector-header">THREE ERAS / ONE INHERITED BODY</div><div class="era-picker" role="group" aria-label="Choose construction era">${Object.entries(eras).map(([id,era])=>`<button data-era="${id}" aria-pressed="${id==='builder'}">${era.name}</button>`).join('')}</div><p id="era-summary" class="era-summary"></p><div class="part-list" id="part-list">${parts.map((p,i)=>`<button type="button" data-part="${p.id}" aria-pressed="false"><span>${String(i+1).padStart(2,'0')}</span>${p.name}<span class="part-arrow">↗</span></button>`).join('')}</div><div id="detail" class="detail" aria-live="polite"></div><button id="focus-part" type="button">Center selected part</button><p class="inspector-foot">ILLUSTRATIVE MECHANISMS<br>POWER ≠ COGNITION</p></aside></div></section>
<section class="timeline" id="field-notes"><p class="eyebrow">THE CONSTRUCTION RECORD</p><h2>Not born. <em>Built.</em></h2><div class="eras"><article><span>I / MAKER</span><h3>Bronze & an absence.</h3><p>Handworked plates carry the first maker’s marks. The ancient movement is unresolved. This exhibit does not assign it a modern brain or a heart.</p></article><article><span>II / MECHANIC</span><h3>Motion, borrowed.</h3><p>Iron braces and brass bearings restore a body. Belts, pressure and wound springs supply movement. The chamber behind the eyes remains empty.</p></article><article><span>III / BUILDER</span><h3>Two missing parts.</h3><p>Power in the breast; processing behind the eyes. Both live within the old body. Neither replaces the history that the metal carries.</p></article></div><p class="source-note">Fictional history drawn from the preserved story snapshot. The cage and visitor-triggered response are exhibit conventions. <a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Read the published story ↗</a></p></section>
</main><footer><span>© JAMIE HILL / OVERKILL HILL P³ · CREATIVE CONTENT ALL RIGHTS RESERVED</span><span>WORKING STUDY · ARTISTIC ACCEPTANCE PENDING</span></footer></div>`;
const $=id=>document.getElementById(id);
const sound=createSoundscape();
const machine=createEncounterState();machine.setEra('builder');
const motionQuery=matchMedia('(prefers-reduced-motion: reduce)');
$('reduced-motion').checked=motionQuery.matches;machine.setReducedMotion(motionQuery.matches);
const sceneElement=$('scene');
let exhibit,selected='beak',era='builder',section=false,returning=false,armed=false,lastState='',loading=false,loadSequence=0;
const updateMarker=(id,x,y,visible)=>{const m=$('hotspots').querySelector(`[data-marker="${id}"]`);if(!m)return;m.style.left=`${x}px`;m.style.top=`${y}px`;m.hidden=!visible;};
$('hotspots').innerHTML=parts.map((p,i)=>`<button class="marker" type="button" data-marker="${p.id}" aria-label="Inspect ${p.name}" hidden>${i+1}</button>`).join('');

function setArmed(value){armed=value;exhibit?.setArmed(value);$('arm-reach').setAttribute('aria-pressed',String(value));$('arm-reach').textContent=value?'Cancel aimed reach':'Aim a reach';if(value)$('encounter-status').textContent='Tap the view once to approach the marked front contact bar. Dragging will cancel the reach. Escape cancels.';}
function requestReach(point={}){
  if(!exhibit||loading||returning)return;
  if(machine.requestReach(point)){setArmed(false);sound.effect('click');renderState(true);}
}
function renderSelection(id){
  selected=id;const p=parts.find(p=>p.id===id);
  document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===id)));
  $('detail').innerHTML=`<p class="detail-era">${eras[era].name.toUpperCase()}</p><h3>${p.title}</h3><p>${eras[era][id]||p.text}</p><p class="observation">${['drive','power','mind'].includes(id)?'Open for inspection to examine the present assembly. Absent systems remain absent.':'Use the orbit controls to inspect a different side. Hidden geometry is a proposed reconstruction.'}</p>`;
  exhibit?.select(id);
}
function renderState(force=false){
  const s=machine.getSnapshot();
  const token=[s.state,s.paused,s.inspection,s.reducedMotion,era,returning,loading,exhibit?.kind].join(':');
  $('reach').disabled=loading||!exhibit||s.state!=='idle'||s.paused||s.inspection||returning;
  $('arm-reach').disabled=$('reach').disabled||exhibit?.kind!=='webgl';
  if(token===lastState&&!force)return;
  const words={idle:'Watching. Approach the front bar when you’re ready.',notice:'Noticing the approach…',warning:'Warning. The bill opens; the stance stays supported.',strike:'A controlled strike toward the contact bar.',contact:'Contact at the cage boundary.',recover:'Recovering to the resting pose.',cooldown:'Settling. Give the mechanism a moment.'};
  $('encounter-status').textContent=loading?'Preparing the assembly…':returning?'Reassembling. The encounter resumes once every component is seated.':s.inspection?'Inspection is calm. Open assemblies stay still while you examine them.':s.paused?'Paused. The specimen stays calm; you can still orbit.':s.reducedMotion&&s.state!=='idle'?'Approach acknowledged. Reduced motion keeps the specimen still.':words[s.state];
  if(exhibit?.kind==='illustrated'&&!loading)$('encounter-status').textContent+=' Illustrated mode reports the response in text.';
  if(s.state==='contact'&&lastState.split(':')[0]!=='contact')sound.effect('metal');
  $('viewer').dataset.behavior=s.state;$('viewer').dataset.mode=s.inspection?'inspection':'encounter';
  lastState=token;
}
function setSection(value){
  section=value;setArmed(false);$('section-toggle').setAttribute('aria-pressed',String(value));$('section-toggle').textContent=value?'Close inspection':'Open for inspection';
  $('separation').disabled=!value;$('reassemble').disabled=!value;$('view-label').textContent=value?'INSPECTION / ASSEMBLY RELATIONSHIPS':'ENCLOSURE / EXTERIOR';
  exhibit?.setSection(value);
  if(value){returning=false;machine.setInspection(true);sound.effect('open');}
  else{exhibit?.setSeparation(0);$('separation').value=0;$('separation-value').textContent='0%';returning=true;}
  renderState(true);
}
function applyEra(value){
  era=value;machine.setEra(value);setArmed(false);exhibit?.setEra(value);
  document.querySelectorAll('[data-era]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.era===value)));
  $('era-label').textContent=eras[value].name.toUpperCase();$('era-summary').textContent=eras[value].summary;renderSelection(selected);renderState(true);
}
async function loadExhibit(forceFallback=false){
  const sequence=++loadSequence;loading=true;setArmed(false);machine.reset();exhibit?.destroy();exhibit=undefined;sceneElement.replaceChildren();
  $('loading').hidden=false;$('retry').hidden=true;renderState(true);
  const forced=forceFallback||new URLSearchParams(location.search).get('view')==='illustrated';
  try{
    if(forced)throw new Error('Illustrated view explicitly selected.');
    exhibit=await createExhibit(sceneElement,updateMarker,{onReach:requestReach,onContextLost:()=>loadExhibit(true)});
  }catch(error){
    if(sequence!==loadSequence)return;
    sceneElement.replaceChildren();exhibit=createIllustratedExhibit(sceneElement,updateMarker);
    $('retry').hidden=false;$('viewer-note').textContent=`Illustrated mode: a fixed MurderBird reference and a separate assembly schematic. ${forced?'':'The 3D model could not load or WebGL is unavailable. '}Use Retry 3D to try again. Component descriptions remain available.`;
    if(import.meta.env.DEV)console.info('Illustrated exhibit:',error.message);
  }
  loading=false;$('loading').hidden=true;$('render-label').textContent=exhibit.kind==='webgl'?'3D / REFERENCE-INFORMED STUDY':'ILLUSTRATED / FIXED VIEW';
  if(exhibit.kind==='webgl')$('viewer-note').textContent='Reference-informed 3D reconstruction under review. The cage is an exhibit device; hidden surfaces and mechanisms are proposals. Music starts only when you choose Play.';
  document.querySelectorAll('[data-view],#focus-part,#reset-view').forEach(b=>b.disabled=exhibit.kind!=='webgl');
  exhibit.setEra(era);exhibit.setSection(section);exhibit.setSeparation(Number($('separation').value)/100);exhibit.resize();renderState(true);
}
$('reach').addEventListener('click',()=>requestReach());
$('arm-reach').addEventListener('click',()=>setArmed(!armed));
$('section-toggle').addEventListener('click',()=>setSection(!section));
$('reassemble').addEventListener('click',()=>setSection(false));
$('separation').addEventListener('input',e=>{exhibit?.setSeparation(Number(e.target.value)/100);$('separation-value').textContent=`${e.target.value}%`;});
$('reset-view').addEventListener('click',()=>{setArmed(false);exhibit?.reset();});
$('focus-part').addEventListener('click',()=>exhibit?.focus(selected));
$('pause').addEventListener('click',e=>{const paused=!machine.getSnapshot().paused;machine.setPaused(paused);setArmed(false);e.currentTarget.setAttribute('aria-pressed',String(paused));e.currentTarget.textContent=paused?'Resume encounter':'Calm / pause';renderState(true);});
$('reduced-motion').addEventListener('change',e=>{machine.setReducedMotion(e.target.checked);setArmed(false);renderState(true);});
motionQuery.addEventListener('change',e=>{$('reduced-motion').checked=e.matches;machine.setReducedMotion(e.matches);renderState(true);});
document.addEventListener('keydown',e=>{if(e.key==='Escape')setArmed(false);});
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>exhibit?.nudge(b.dataset.view)));
document.querySelectorAll('[data-era]').forEach(b=>b.addEventListener('click',()=>applyEra(b.dataset.era)));
$('part-list').addEventListener('click',e=>{const b=e.target.closest('[data-part]');if(b)renderSelection(b.dataset.part);});
$('hotspots').addEventListener('click',e=>{const b=e.target.closest('[data-marker]');if(b)renderSelection(b.dataset.marker);});
$('retry').addEventListener('click',()=>{const u=new URL(location.href);u.searchParams.delete('view');history.replaceState(null,'',u);loadExhibit();});
$('sound-toggle').addEventListener('click',async e=>{const b=e.currentTarget;b.disabled=true;try{const enabled=await sound.toggle();b.setAttribute('aria-pressed',String(enabled));b.textContent=enabled?'Sound on':'Sound off';}catch{b.textContent='Sound unavailable';}finally{b.disabled=false;}});
const {mountThemePlayer}=await import('./audio/theme-player.js');mountThemePlayer(document.querySelector('.viewer-column'),sound);
applyEra('builder');renderSelection('beak');
new ResizeObserver(()=>exhibit?.resize()).observe($('viewer'));
let previous=performance.now();
function animate(now){const dt=Math.min((now-previous)/1000,.1);previous=now;if(exhibit){const state=machine.update(document.hidden?0:dt);exhibit.tick(document.hidden?0:dt,state);if(returning&&exhibit.isAssembled()){returning=false;machine.setInspection(false);}renderState();}requestAnimationFrame(animate);}
requestAnimationFrame(animate);
// Local QA reads actual loaded scene metrics; this hook is removed by Vite builds.
if(import.meta.env.DEV)window.__uncaged={getSnapshot:()=>machine.getSnapshot(),metrics:()=>exhibit?.metrics()};
await loadExhibit();
