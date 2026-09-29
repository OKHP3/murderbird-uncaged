import './style.css';
import './fallback.css';
import './review-navigation.css';
import { createExhibit } from './scene/presence-exhibit.js';
import { createIllustratedExhibit } from './scene/fallback.js';
import { createEraController } from './scene/era-controller.js';
import { createSoundscape } from './audio/soundscape.js';

const eras = {
  maker:{name:'I · Maker',summary:'Someone must operate it. A fixed cradle carries the weight; outside levers and rods move individual joints.',drive:'Operate the labeled levers below the view. Each outside control connects to its joint through a visible rod or line. The post and pelvic cradle support the body even with a foot raised. This exact control arrangement is a proposed reconstruction.',power:'No internal power source. The visitor supplies the movement.',mind:'No autonomous attention, brain or intention. Individual joints move only when operated.'},
  mechanic:{name:'II · Mechanic',summary:'It can move itself, but its machinery limits it. A wound spring drives a slow sequence: load, step, settle, pause.',drive:'A mainspring turns reduction gears and a cam shaft. Each cam cycle loads the support leg, releases one short step, then pauses before the next operation. Turns happen in separate increments. This proposed arrangement uses one power source, with no steam boiler or thinking machine.',power:'A wound mainspring stores a limited charge. Wind it, engage the mechanism, or stop after the current cycle. The charge display explains the limitation; it is not an engineering measurement.',mind:'A repeated cam sequence provides limited control. It does not detect or assess a visitor.'},
  builder:{name:'III · Advanced',summary:'Powerful, aware and dangerous. Coordinated actuators and separate sensing and processing give the encounter its speed and intent.',drive:'Power distribution feeds the joint actuators directly. Coordinated legs, neck and shield wings prepare, move and recover together. Power jump loads the legs, clears the floor and absorbs the landing. Shield thrust braces the feet and drives the shoulder and armored elbow. The wings balance and shield; they do not fly. There is no winding cycle or cam-driven pause. Exact actuator geometry is proposed for review.',power:'The enclosed continuity supply provides effectively inexhaustible power for this fictional encounter. Protected conduits distribute it to the actuators. It is separate from cognition, with no routine winding, fuel or pressure recovery.',mind:'Sensing at the eyes feeds the separate cranial processing assembly. Local behavior rules represent attention and tactical intent; this exhibit uses no online AI service.'},
};
const parts=[
  {id:'beak',name:'Bill & skull',title:'A tool with a dangerous edge.',text:'The deep recurved bill, recessed circular optic and segmented crown come from the selected production reference. The hinge and unseen rear surfaces are reconstructed for this study.'},
  {id:'joint',name:'Load & articulation',title:'Weight has a path.',text:'Broad three-toed feet support the body. Pins, bearing collars and paired rods suggest force passing through the legs. The anatomical left shoulder retains limited travel. The original fitted plate and later repair strap are distinct proposals; their exact topology awaits review.'},
  {id:'shell',name:'Breastplate',title:'Open the inherited body.',text:'Overlapping armor is separate from the internal frame. The breastplate opens during inspection. Dashed lines retain assembly relationships when the parts separate.'},
  {id:'drive',name:'Winding & transmission',title:'Energy becomes movement.'},
  {id:'power',name:'Heart · power',title:'Power is one missing part.'},
  {id:'mind',name:'Mind · processing',title:'Processing is the other.'},
  {id:'guard',name:'Wings · balance & shielding',title:'Tuck. Brace. Drive.',text:'MurderBird is flightless. Its folded wings guard the ribs and help balance close, forceful movements. The shoulder leads a short shove while the elbow drives the armored forewing; the opposite wing counters. The repaired left shoulder keeps a smaller range. The exact joint design is reconstructed for this study.'},
];
const currentGeometryReview = import.meta.env.DEV ? '<a href="./assets/audit/whole-character-v32/index.html">Construction review · V32</a>' : '';
const app=document.querySelector('#app');
app.innerHTML=`<a class="skip-link" href="#controls">Skip to exhibit controls</a><div class="site-shell">
<header class="topbar"><a class="wordmark" href="#top"><span class="mark">M/B</span><span>MURDERBIRD<small>UNCAGED</small></span></a><nav aria-label="Main navigation"><a href="./folio.html">Story &amp; media folio</a>${currentGeometryReview}<a href="./review/">Published review</a><a href="#field-notes">Construction record</a><a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Origin story ↗</a></nav><span class="edition">THREE MOVEMENT SYSTEMS / 05</span></header>
<main id="top"><section class="exhibit" id="specimen" aria-labelledby="exhibit-title">
<div class="exhibit-heading"><div><p class="eyebrow">AN ENCOUNTER WITH AN IMPOSSIBLE MACHINE</p><h1 id="exhibit-title">MurderBird: <em>Uncaged.</em></h1></div><p>Drag to orbit. Scroll or pinch to move closer.<br>One inherited body. Three ways to move.<br>Operate. Engage. Encounter.</p></div>
<div class="exhibit-grid"><div class="viewer-column"><div class="viewer" id="viewer">
<div class="viewer-top"><span id="render-label">LOADING ASSEMBLY…</span><span id="era-label">III · BUILDER</span></div>
<div id="scene" aria-label="MurderBird exhibit"></div><div id="hotspots" class="hotspots"></div><div class="era-transition" id="era-transition" hidden role="status">Reconstructing the next era…</div><div class="loading" id="loading" role="status">Preparing the mechanical assembly…</div>
<div class="viewer-bottom"><span id="view-label">ENCLOSURE / EXTERIOR</span><span>LIKENESS REVIEW PENDING</span></div>
</div>
<div id="controls" class="toolbar" role="group" aria-label="Encounter and inspection controls" tabindex="-1">
<label class="reach-position" data-capability="advanced" for="reach-position">Your position<select id="reach-position"><option value="-1">Left rail</option><option value="0" selected>Center rail</option><option value="1">Right rail</option></select></label><button id="reach" data-capability="advanced" type="button" class="primary">Reach toward bars</button><button id="retreat" data-capability="advanced" type="button" disabled>Retreat</button><button id="arm-reach" data-capability="advanced" type="button" aria-pressed="false">Tap-to-reach mode</button><button id="power-jump" data-capability="advanced" type="button">Power jump</button><button id="shield-thrust" data-capability="advanced" type="button">Shield thrust</button><button id="claw-scrape" data-capability="advanced" type="button">Claw scrape</button><button id="section-toggle" type="button" aria-pressed="false">Open for inspection</button><button id="reset-view" type="button">Reset view</button></div>
<div id="maker-controls" class="era-controls" hidden><p><strong>Operate the outside levers</strong> · The cradle holds the bird. Release each lever to return its joint.</p><div class="lever-grid">${[['leg','Lift left leg'],['wing','Raise shield wing'],['tail','Lift short tail'],['neck','Turn neck'],['jaw','Open mouth']].map(([id,label])=>`<label for="lever-${id}">${label}<input id="lever-${id}" data-articulation="${id}" type="range" min="0" max="100" value="0" aria-label="${label}" /></label>`).join('')}</div><button id="release-levers" type="button">Release all levers</button></div>
<div id="mechanic-controls" class="era-controls" hidden><p><strong>Wound mechanical drive</strong> · Load, release, settle, pause.</p><div class="mechanic-actions"><button id="run-mechanism" type="button">Engage mechanism</button><button id="stop-mechanism" type="button">Stop after this cycle</button><button id="wind-mechanism" type="button">Wind spring</button><label for="spring-charge">Spring charge <meter id="spring-charge" min="0" max="1" value="1"></meter><output id="spring-percent">100%</output></label></div><p id="drive-phase" class="drive-phase">Disengaged.</p></div>
<p id="encounter-status" class="encounter-status" role="status">Loading the specimen.</p>
<div class="inspection-controls"><label for="separation">Separate assembly <output id="separation-value">0%</output></label><input id="separation" type="range" min="0" max="100" step="1" value="0" disabled /><button id="reassemble" type="button" disabled>Reassemble & return</button></div>
<div class="secondary-controls"><div class="view-controls" role="group" aria-label="Camera controls"><button data-view="left" aria-label="Orbit left">←</button><button data-view="right" aria-label="Orbit right">→</button><button data-view="up" aria-label="Raise viewpoint">↑</button><button data-view="down" aria-label="Lower viewpoint">↓</button><button data-view="in" aria-label="Zoom in">+</button><button data-view="out" aria-label="Zoom out">−</button></div><button id="pause" type="button" aria-pressed="false">Calm / pause</button><label class="motion-label"><input id="reduced-motion" type="checkbox" /> Reduced motion</label><label class="motion-label"><input id="part-labels" type="checkbox" checked /> Part labels</label><button id="sound-toggle" type="button" aria-pressed="false">Sound off</button></div>
<p class="viewer-note" id="viewer-note">Geometry and articulation are under review. Final era materials are pending. Hidden construction and the enclosure remain proposals. Music starts only when you choose Play.</p>
<button id="retry" class="retry" type="button" hidden>Retry 3D</button>
</div><aside class="inspector" aria-label="Construction details"><div class="inspector-header">THREE ERAS / ONE INHERITED BODY</div><div class="era-picker" role="group" aria-label="Choose construction era">${Object.entries(eras).map(([id,era])=>`<button data-era="${id}" aria-pressed="${id==='builder'}">${era.name}</button>`).join('')}</div><p id="era-summary" class="era-summary"></p><div class="part-list" id="part-list">${parts.map((p,i)=>`<button type="button" data-part="${p.id}" aria-pressed="false"><span>${String(i+1).padStart(2,'0')}</span><span class="part-name">${p.name}</span><span class="part-arrow">↗</span></button>`).join('')}</div><div id="detail" class="detail" aria-live="polite"></div><button id="focus-part" type="button">Center selected part</button><p class="inspector-foot">ILLUSTRATIVE MECHANISMS<br>POWER ≠ COGNITION</p></aside></div></section>
<section class="timeline" id="field-notes"><p class="eyebrow">THE CONSTRUCTION RECORD</p><h2>Not born. <em>Built.</em></h2><div class="eras"><article><span>I / MAKER</span><h3>Movement from outside.</h3><p>A supported articulated construct. Outside levers move its joints; at rest it stays where its maker placed it. No internal power or intention.</p></article><article><span>II / MECHANIC</span><h3>A machine with limits.</h3><p>A wound spring, reduction gears and a cam sequence allow short steps and segmented turns. The pauses belong to the transmission, not to thought.</p></article><article><span>III / BUILDER</span><h3>Power with intent.</h3><p>An abundant fictional supply feeds coordinated actuators. Sensing and processing give the advanced bird responsive attention, fast attacks and controlled recovery.</p></article></div><p class="source-note">This progression follows the owner’s current exhibit direction. The exact control rods, spring transmission and advanced supply are proposed reconstructions. The preserved story remains a separate source. <a href="https://overkillhill.com/writings/murderbird/" target="_blank" rel="noopener noreferrer">Read the published story ↗</a></p></section>
</main><footer><span>© JAMIE HILL / OVERKILL HILL P³ · CREATIVE CONTENT ALL RIGHTS RESERVED</span><span>WORKING STUDY · ARTISTIC ACCEPTANCE PENDING</span></footer></div>`;
const localReviewBody = import.meta.env.DEV ? (new URLSearchParams(location.search).get('review-body') || 'v32-form01') : null;
if (import.meta.env.DEV && ['v32-form01', 'v31-form02', 'v31-form01', 'v10-01', 'v10-02', 'v12-02', 'v13-01', 'v14-03', 'v14-05', 'v14-09', 'v14-11', 'v15-03', 'v15-04', 'v16-02', 'v16-03', 'v17-02', 'v18-01', 'v19-01', 'v19-02', 'v20-runtime01', 'v20-runtime02', 'v21-construction02', 'v21-construction04', 'v21-construction06'].includes(localReviewBody)) {
  const notice = document.createElement('p');
  notice.setAttribute('role', 'status');
  notice.style.cssText = 'margin:0;padding:14px 24px;background:#302c20;color:#f6e4b7;border-bottom:2px solid #a68b52';
  notice.textContent = localReviewBody === 'v32-form01'
    ? 'LOCAL V32 FORM 01 · Near-closed formed jaw, returned bill, separate brow and cheek, and revised crown. The two V31 strike collisions are removed. Earlier neck interference and likeness gaps remain; this is an unapproved construction study. Illustrated fallback depicts V9.'
    : localReviewBody === 'v31-form02'
    ? 'LOCAL V31 FORM 02 · Rebuilt head, open optic aperture, connected throat and seated control attachments. HELD: likeness remains below target; the strike pose adds two head-to-neck collisions. This is a construction proposal with all three era mechanisms. Illustrated fallback depicts V9.'
    : localReviewBody === 'v31-form01'
    ? 'LOCAL V31 FORM 01 · Rebuilt head and authored Maker jaw/wing attachments. Held for jaw, crown and throat intersections; likeness is still below target. This is a diagnostic construction study with the complete era mechanisms. Illustrated fallback depicts V9.'
    : localReviewBody === 'v21-construction06'
    ? 'LOCAL V21 CONSTRUCTION 06 · Revised compact shoulder and elbow shields, rebuilt head and linked neck cover. Whole-character likeness and moving clearances remain unresolved. This is a diagnostic construction proposal. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v21-construction04'
    ? 'LOCAL V21 CONSTRUCTION 04 · Rebuilt bill and jaw, linked rigid neck cover, thirty breast plates and ankle forks. Overall likeness and contacts with neighboring parts remain unresolved. This is a held construction proposal. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v21-construction02'
    ? 'LOCAL V21 CONSTRUCTION STUDY · Curved neck and breast, constructed bill and jaw, overlapping breast panels and ankle forks. Neck guards cross during deep articulation; this candidate is held for joint reconstruction. Likeness remains below target. Illustrated fallback still depicts V9.'
    : localReviewBody.startsWith('v20-')
    ? 'LOCAL V20 BODY STUDY · Fuller breast, revised shoulders and supporting legs. Head, neck and plate construction remain unresolved. Rejected neck variants are excluded. This is a motion study, not approved artwork. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v19-02'
    ? 'LOCAL V19 ATTEMPT 02 · HELD CONSTRUCTION PROPOSAL. Separate front access door and fixed torso walls, revised breast and narrower jaw opening. Likeness and movement clearance remain unresolved. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v19-01'
    ? 'LOCAL V19 CONSTRUCTION PROPOSAL · Revised breast and neck, bottom-opening cover and narrower jaw opening. Likeness and movement clearances remain under review. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v18-01'
    ? 'LOCAL V18 CONSTRUCTION PROPOSAL · Revised head fittings, neck junction and lower-leg construction. Whole-character likeness and moving clearances remain under review. Illustrated fallback still depicts V9.'
    : localReviewBody === 'v17-02'
    ? 'LOCAL V17 PROPOSAL · HELD FOR CORRECTION. Revised breast layers and passive eye supports still intersect neighboring parts in reviewed poses. Likeness remains below target. Illustrated fallback still depicts V9.'
    : localReviewBody.startsWith('v16-')
    ? 'LOCAL V16 PROPORTION STUDY · Fuller breast, lower head, broader shoulders and stronger stance. Joint locations have changed. Likeness and moving clearance remain unapproved. Illustrated fallback still depicts V9.'
    : ['v15-03', 'v15-04'].includes(localReviewBody)
    ? 'LOCAL V15 CONSTRUCTION STUDY · Revised head, breast and leg construction. Likeness and moving clearance remain unapproved. Illustrated fallback still depicts V9. Use the previous exhibit link to compare V9.'
    : ['v14-03', 'v14-05', 'v14-09', 'v14-11'].includes(localReviewBody)
    ? 'LOCAL V14 HEAD STUDY · Revised socket, fixed brow and opening crown. Likeness and moving clearance remain unapproved. Illustrated fallback still depicts V9. Use the previous exhibit link to compare V9.'
    : localReviewBody === 'v13-01'
    ? 'LOCAL V13 HEAD STUDY · A deeper bill and shorter mandible on the V12 body. Likeness and moving clearance remain unapproved. Illustrated fallback still depicts V9. Use the previous exhibit link to compare V9.'
    : localReviewBody === 'v12-02'
    ? 'LOCAL V12 MOTION STUDY · New neck reconstruction, with no owner likeness approval. Joint clearances and external mechanism attachments remain under review. Illustrated fallback still depicts V9. Use the previous exhibit link to compare V9.'
    : 'LOCAL V10 STUDY · Owner-rejected likeness, preserved for diagnosis. Structural clearance remains unresolved. Illustrated fallback still depicts V9. Use the previous exhibit link to compare V9.';
  const previous = document.createElement('a');
  previous.href = localReviewBody === 'v32-form01' ? '?review-body=v31-form02' : localReviewBody === 'v21-construction06' ? '?review-body=v21-construction04' : localReviewBody === 'v21-construction04' ? '?review-body=v21-construction02' : localReviewBody === 'v21-construction02' ? '?review-body=v20-runtime02' : localReviewBody.startsWith('v20-') ? '?review-body=v19-02' : localReviewBody.startsWith('v19-') ? '?review-body=v18-01' : localReviewBody === 'v18-01' ? '?review-body=v17-02' : localReviewBody === 'v17-02' ? '?review-body=v16-03' : '?review-body=stable-v9';
  previous.textContent = localReviewBody === 'v32-form01' ? ' Previous local study (V31 Form02)' : localReviewBody === 'v21-construction06' ? ' Previous local study (V21 Construction04)' : localReviewBody === 'v21-construction04' ? ' Previous local study (V21 Construction02)' : localReviewBody === 'v21-construction02' ? ' Previous local candidate (V20 Runtime 02)' : localReviewBody.startsWith('v20-') ? ' Previous local candidate (V19 attempt 02)' : localReviewBody.startsWith('v19-') ? ' Previous local candidate (V18 attempt 01)' : localReviewBody === 'v18-01' ? ' Previous local candidate (V17 attempt 02)' : localReviewBody === 'v17-02' ? ' Previous local candidate (V16 attempt 03)' : ' Previous exhibit (V9)';
  previous.style.color = 'inherit';
  notice.append(previous);
  document.getElementById('app').prepend(notice);
}
const $=id=>document.getElementById(id);
const sound=createSoundscape();
const reviewSeed = import.meta.env.DEV ? Number(new URLSearchParams(location.search).get('review-seed')) : null;
const machine=createEraController(Number.isSafeInteger(reviewSeed) && reviewSeed > 0 ? {seed:reviewSeed} : undefined);machine.setEra('builder');
const motionQuery=matchMedia('(prefers-reduced-motion: reduce)');
$('reduced-motion').checked=motionQuery.matches;machine.setReducedMotion(motionQuery.matches);
const sceneElement=$('scene');
let exhibit,selected='beak',era='builder',section=false,sectionOpen=false,returning=false,armed=false,lastState='',loading=false,loadSequence=0;
let pendingEra=null,transitionTime=0,transitionCovered=false;
const updateMarker=(id,x,y,visible,layout)=>{const m=$('hotspots').querySelector(`[data-marker="${id}"]`);if(!m)return;m.style.left=`${x}px`;m.style.top=`${y}px`;m.style.setProperty('--leader-length',`${layout?.leaderLength||0}px`);m.style.setProperty('--leader-angle',`${layout?.leaderAngle||0}rad`);m.hidden=!visible;};
$('hotspots').innerHTML=parts.map((p,i)=>`<button class="marker" type="button" data-marker="${p.id}" aria-label="Inspect ${p.name}" hidden>${i+1}</button>`).join('');

function setArmed(value){armed=value;exhibit?.setArmed(value);$('arm-reach').setAttribute('aria-pressed',String(value));$('arm-reach').textContent=value?'Cancel tap-to-reach':'Tap-to-reach mode';if(value)$('encounter-status').textContent='Tap a front rail to choose your virtual approach position. Dragging does not provoke it. Escape cancels targeting.';}
function requestReach(point={x:Number($('reach-position').value),y:0}){
  if(!exhibit||loading||returning||pendingEra)return;
  if(machine.requestReach(point)){setArmed(false);sound.effect('click');renderState(true);}
}
function renderSelection(id){
  selected=id;const p=parts.find(p=>p.id===id);
  document.querySelectorAll('[data-part]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.part===id)));
  const title=id==='drive'?{maker:'Your hand supplies the force.',mechanic:'The cam sets the pace.',builder:'Power reaches the joints.'}[era]:id==='power'?(era==='mechanic'?'Stored work in a spring.':'An abundant fictional supply.'):p.title;
  $('detail').innerHTML=`<p class="detail-era">${eras[era].name.toUpperCase()}</p><h3>${title}</h3><p>${eras[era][id]||p.text}</p><p class="observation">${['drive','power','mind'].includes(id)?'Open for inspection to examine the present assembly. Absent systems remain absent.':'Use the orbit controls to inspect a different side. Hidden geometry is a proposed reconstruction.'}</p>`;
  exhibit?.select(id);
  $('focus-part').disabled=exhibit?.kind!=='webgl'||pendingEra||(id==='power'&&era==='maker')||(id==='mind'&&era!=='builder');
}
function renderState(force=false){
  const s=machine.getSnapshot();
  const token=[s.state,s.paused,s.inspection,s.reducedMotion,era,returning,loading,pendingEra,s.powerMovePending?.kind,s.clawAction?.stage,exhibit?.kind].join(':');
  const blocked=loading||!exhibit||Boolean(pendingEra);
  $('reach').disabled=blocked||!s.canReach||s.paused||s.inspectionRequested||returning;
  for(const id of ['power-jump','shield-thrust'])$(id).disabled=blocked||typeof machine.requestPowerMove!=='function'||era!=='builder'||!s.canReach||s.visitorPresent||s.paused||s.reducedMotion||s.inspectionRequested||s.inspection||returning||exhibit?.kind!=='webgl';
  $('claw-scrape').disabled=blocked||era!=='builder'||!s.canClawAction||s.paused||s.reducedMotion||s.inspectionRequested||s.inspection||returning||exhibit?.kind!=='webgl';
  $('retreat').disabled=loading||!s.visitorPresent||s.inspectionRequested;
  $('arm-reach').disabled=$('reach').disabled||exhibit?.kind!=='webgl';
  $('section-toggle').disabled=blocked;
  $('focus-part').disabled=blocked||exhibit?.kind!=='webgl'||(selected==='power'&&era==='maker')||(selected==='mind'&&era!=='builder');
  document.querySelectorAll('[data-articulation],#release-levers').forEach(el=>el.disabled=blocked||s.paused||s.inspectionRequested||s.inspection||exhibit?.kind!=='webgl');
  $('run-mechanism').disabled=blocked||s.routineRunning||s.paused||s.reducedMotion||s.inspectionRequested||s.inspection||(s.energy??0)<=0||exhibit?.kind!=='webgl';
  $('stop-mechanism').disabled=blocked||!s.routineRunning;
  $('wind-mechanism').disabled=blocked||s.routineRunning||s.inspectionRequested||s.inspection||s.paused||s.reducedMotion||s.state==='mechanical-settle'||!exhibit.feedback?.().settled;
  $('spring-charge').value=s.energy??1;$('spring-percent').textContent=`${Math.round((s.energy??1)*100)}%`;
  if(token===lastState&&!force)return;
  const words={'power-jump':'Load, launch, land. The legs supply the lift; the tucked wings balance it.','power-thrust':'Feet braced. The shoulder drives the shield wing, then recovers.',watch:'Watching the enclosure. Its stillness is deliberate.',pace:'Pacing. Each turn takes another planted step.',boundary:'Following a seam toward the bars.', 'cage-test':({'edge-probe':'Testing one edge with a brief probe.','rail-press':'Testing the cage with a slow, sustained press.','seam-rattle':'Probing the seam in three separate pulses.'}[s.actionFamily]||'Testing the cage with a controlled press.'),notice:'The head turns first. You have its attention.',approach:'Closing toward your position. You can retreat.',warning:'Feet planted. Wings tucked. The body loads for a strike.',strike:'A committed snap toward your chosen rail.',contact:'The bill meets the inside of the cage.',recover:'Decelerating and restoring its stance.',agitated:'Still watching you. The encounter has not been forgotten.',settle:'Finishing its step and settling into inspection.',inspection:'Inspection is calm. Assemblies stay still while open.'};
  const earlyWords={'puppet-rest':'Stationary. The outside levers supply every movement.','puppet-articulation':'Externally operated. The cradle supports the body.','mechanical-ready':'Spring charged. Engage the mechanism to begin its limited routine.','mechanical-run':'The drive repeats a fixed sequence. It is not watching the visitor.','mechanical-settle':'Disengaging after the current step.','mechanical-empty':'The spring has run down. Wind it to restore mechanical movement.'};
  const clawWords={approach:'Weight shifts onto the supporting foot.',lift:'The other claw lifts and reaches forward.',contact:'The claw settles against the floor.',scrape:'The claw draws a short scrape across the floor.',release:'The toes release and lift clear of the floor.',recovery:'The foot returns and plants before movement resumes.'};
  $('encounter-status').textContent=loading?'Preparing the assembly…':pendingEra?'Settling and reassembling before changing construction.':returning?'Reassembling. Movement resumes once every component is seated.':s.inspection?words.inspection:s.powerMovePending?`Planting its feet before the ${s.powerMovePending.kind==='jump'?'jump':'shield thrust'}.`:s.inspectionRequested?words.settle:s.paused?'Paused in place. You can still orbit or inspect.':s.clawAction?clawWords[s.clawAction.stage]||'Preparing the claw.':s.reducedMotion&&era!=='maker'?'Calm view. Automatic travel and strikes are off.':earlyWords[s.state]||words[s.state]||'Ready.';
  if(exhibit?.kind==='illustrated'&&!loading)$('encounter-status').textContent+=' Illustrated mode reports the response in text.';
  if(s.state==='contact'&&lastState.split(':')[0]!=='contact')sound.effect('metal');
  $('viewer').dataset.behavior=s.state;$('viewer').dataset.mode=s.inspection?'inspection':'encounter';
  lastState=token;
}
function setSection(value){
  section=value;setArmed(false);$('section-toggle').setAttribute('aria-pressed',String(value));$('section-toggle').textContent=value?'Close inspection':'Open for inspection';
  $('separation').disabled=true;$('reassemble').disabled=!value;
  if(value){returning=false;machine.setInspection(true);}
  else{sectionOpen=false;exhibit?.setSection(false);exhibit?.setSeparation(0);$('separation').value=0;$('separation-value').textContent='0%';returning=true;}
  renderState(true);
}
function applyEra(value){
  era=value;machine.setEra(value);setArmed(false);exhibit?.setEra(value);
  document.querySelectorAll('[data-capability="advanced"]').forEach(el=>el.hidden=value!=='builder');
  $('maker-controls').hidden=value!=='maker';$('mechanic-controls').hidden=value!=='mechanic';
  document.querySelectorAll('[data-articulation]').forEach(el=>el.value=0);
  document.querySelectorAll('[data-part]').forEach(el=>{const id=el.dataset.part;el.hidden=id==='power'&&value==='maker'||id==='mind'&&value!=='builder';if(id==='drive')el.querySelector('.part-name').textContent={maker:'External controls',mechanic:'Transmission',builder:'Actuators'}[value];if(id==='power')el.querySelector('.part-name').textContent=value==='mechanic'?'Spring barrel':'Power supply';if(id==='mind')el.querySelector('.part-name').textContent='Processing & sensing';});
  if(selected==='power'&&value==='maker'||selected==='mind'&&value!=='builder')selected='drive';
  document.querySelectorAll('[data-era]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.era===value)));
  $('era-label').textContent=eras[value].name.toUpperCase();$('era-summary').textContent=eras[value].summary;renderSelection(selected);renderState(true);
}
function requestEra(value){
  if(!eras[value]||value===era&&!pendingEra||loading)return;
  pendingEra=value;transitionTime=0;transitionCovered=false;setArmed(false);
  section=false;sectionOpen=false;returning=false;machine.setInspection(true);exhibit?.setSection(false);exhibit?.setSeparation(0);
  $('section-toggle').setAttribute('aria-pressed','false');$('section-toggle').textContent='Open for inspection';$('separation').value=0;$('separation-value').textContent='0%';$('separation').disabled=true;$('reassemble').disabled=true;
  renderState(true);
}
async function loadExhibit(forceFallback=false){
  const sequence=++loadSequence;loading=true;pendingEra=null;transitionCovered=false;transitionTime=0;$('era-transition').hidden=true;setArmed(false);machine.reset();exhibit?.destroy();exhibit=undefined;sceneElement.replaceChildren();
  $('loading').hidden=false;$('retry').hidden=true;renderState(true);
  const forced=forceFallback||new URLSearchParams(location.search).get('view')==='illustrated';
  try{
    if(forced)throw new Error('Illustrated view explicitly selected.');
    const loaded=await createExhibit(sceneElement,updateMarker,{onReach:requestReach,onContextLost:()=>loadExhibit(true)});
    if(sequence!==loadSequence){loaded.destroy();return;}
    exhibit=loaded;
  }catch(error){
    if(sequence!==loadSequence)return;
    sceneElement.replaceChildren();exhibit=createIllustratedExhibit(sceneElement,updateMarker);
    $('retry').hidden=false;$('viewer-note').textContent=`Illustrated mode: a fixed MurderBird reference and a separate assembly schematic. ${forced?'':'The 3D model could not load or WebGL is unavailable. '}Use Retry 3D to try again. Component descriptions remain available.`;
    if(import.meta.env.DEV)console.info('Illustrated exhibit:',error.message);
  }
  loading=false;$('loading').hidden=true;$('render-label').textContent=exhibit.kind==='webgl'?'3D / REFERENCE-INFORMED STUDY':'ILLUSTRATED / FIXED VIEW';
  if(exhibit.kind==='webgl')$('viewer-note').textContent='Geometry and articulation are under review. Final era materials are pending. Hidden construction and the enclosure remain proposals. Music starts only when you choose Play.';
  document.querySelectorAll('[data-view],#focus-part,#reset-view').forEach(b=>b.disabled=exhibit.kind!=='webgl');
  exhibit.setEra(era);sectionOpen=false;if(section)machine.setInspection(true);exhibit.setSection(false);exhibit.setSeparation(0);exhibit.resize();renderSelection(selected);renderState(true);
}
$('reach').addEventListener('click',()=>requestReach());
for(const [id,kind] of [['power-jump','jump'],['shield-thrust','thrust']])$(id).addEventListener('click',()=>{machine.requestPowerMove(kind);setArmed(false);renderState(true);});
$('claw-scrape').addEventListener('click',()=>{machine.requestClawAction();setArmed(false);renderState(true);});
$('retreat').addEventListener('click',()=>{machine.requestRetreat();setArmed(false);renderState(true);});
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
document.querySelectorAll('[data-era]').forEach(b=>b.addEventListener('click',()=>requestEra(b.dataset.era)));
document.querySelectorAll('[data-articulation]').forEach(input=>input.addEventListener('input',()=>{machine.setArticulation(input.dataset.articulation,Number(input.value)/100);renderState(true);}));
$('release-levers').addEventListener('click',()=>{document.querySelectorAll('[data-articulation]').forEach(input=>{input.value=0;machine.setArticulation(input.dataset.articulation,0);});renderState(true);});
$('run-mechanism').addEventListener('click',()=>{machine.requestRoutine();renderState(true);});
$('stop-mechanism').addEventListener('click',()=>{machine.stopRoutine();renderState(true);});
$('wind-mechanism').addEventListener('click',()=>{machine.wind();renderState(true);});
$('part-list').addEventListener('click',e=>{const b=e.target.closest('[data-part]');if(b)renderSelection(b.dataset.part);});
$('hotspots').addEventListener('click',e=>{const b=e.target.closest('[data-marker]');if(b)renderSelection(b.dataset.marker);});
$('part-labels').addEventListener('change',e=>{$('hotspots').hidden=!e.target.checked;});
$('retry').addEventListener('click',()=>{const u=new URL(location.href);u.searchParams.delete('view');history.replaceState(null,'',u);loadExhibit();});
$('sound-toggle').addEventListener('click',async e=>{const b=e.currentTarget;b.disabled=true;try{const enabled=await sound.toggle();b.setAttribute('aria-pressed',String(enabled));b.textContent=enabled?'Sound on':'Sound off';}catch{b.textContent='Sound unavailable';}finally{b.disabled=false;}});
const {mountThemePlayer}=await import('./audio/theme-player.js');mountThemePlayer(document.querySelector('.viewer-column'),sound);
applyEra('builder');renderSelection('beak');
new ResizeObserver(()=>exhibit?.resize()).observe($('viewer'));
let previous=performance.now();
function frame(dt,frameDelta=dt){
  if(!exhibit)return;
  const state=machine.update(dt,exhibit.feedback?.()||{arrived:true,settled:true,aligned:true});
  exhibit.tick(dt,state,frameDelta);
  if(era==='mechanic'&&exhibit.kind==='webgl')$('drive-phase').textContent=`Drive cycle: ${exhibit.driveState?.()||'disengaged'}.`;
  if(pendingEra){
    if(!transitionCovered&&state.inspection&&exhibit.isAssembled()){
      transitionCovered=true;$('era-transition').hidden=false;$('era-transition').textContent=`Reconstructing ${eras[pendingEra].name}…`;
    }
    if(transitionCovered){transitionTime+=dt;if(transitionTime>.4){const value=pendingEra;applyEra(value);machine.setInspection(false);pendingEra=null;transitionCovered=false;$('era-transition').hidden=true;$('view-label').textContent='ENCLOSURE / EXTERIOR';}}
    renderState();return;
  }
  if(section&&state.inspection&&!sectionOpen){sectionOpen=true;exhibit.setSection(true);$('separation').disabled=false;$('view-label').textContent='INSPECTION / ASSEMBLY RELATIONSHIPS';sound.effect('open');}
  if(returning&&exhibit.isAssembled()){returning=false;machine.setInspection(false);$('view-label').textContent='ENCLOSURE / EXTERIOR';}
  renderState();
}
function animate(now){const frameDelta=(now-previous)/1000;const dt=Math.min(frameDelta,.1);previous=now;if(!document.hidden)frame(dt,frameDelta);requestAnimationFrame(animate);}
requestAnimationFrame(animate);
// Local QA reads actual loaded scene metrics; this hook is removed by Vite builds.
if(import.meta.env.DEV)window.__uncaged={getSnapshot:()=>({...machine.getSnapshot(),pendingEra}),metrics:()=>exhibit?.metrics(),poseSnapshot:()=>exhibit?.poseSnapshot?.(),step:(seconds)=>{for(let t=0;t<seconds;t+=1/60)frame(Math.min(1/60,seconds-t));},reach:point=>requestReach(point),retreat:()=>machine.requestRetreat(),era:requestEra,articulate:(id,v)=>machine.setArticulation(id,v),powerMove:kind=>machine.requestPowerMove(kind),clawAction:()=>machine.requestClawAction(),reviewCamera:name=>exhibit?.reviewCamera(name),reviewLighting:mode=>exhibit?.reviewLighting(mode)};
await loadExhibit();
