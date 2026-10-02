// Fixed renders of this exterior study accompany a separate assembly diagram.
// The image is not animated or presented as an interactive spatial view.
const productionPreviews = {
  maker: new URL('../../assets/models/whole-character-v37/attempt-release02/maker-preview.png', import.meta.url).href,
  mechanic: new URL('../../assets/models/whole-character-v37/attempt-release02/mechanic-preview.png', import.meta.url).href,
  builder: new URL('../../assets/models/whole-character-v37/attempt-release02/builder-preview.png', import.meta.url).href,
};
// Review captures stay outside the production bundle and are explicitly fixed
// authoring renders; the deployed V37 fallback continues to use its own captures.
const cinematicReview = import.meta.env.DEV && new URLSearchParams(location.search).get('review-candidate') === 'cinematic-surface01';
const previews = cinematicReview ? Object.fromEntries(['maker', 'mechanic', 'builder'].map(era => [era,
  `/assets/audit/whole-character-v38/cinematic-surface01/attempt02/candidate-${era}-neutral-fullbird.png`,
])) : productionPreviews;
const captureLabel = cinematicReview ? 'Cinematic surface01 · authoring render' : 'Version 37 · fixed view';
const eraNames = { maker:'Maker', mechanic:'Mechanic', builder:'Advanced' };
const referenceUrl = previews.builder;
export function createIllustratedExhibit(container, updateMarker) {
  container.innerHTML = `<div class="illustrated-view"><img src="${referenceUrl}" alt="MurderBird production reference: heavy floor-standing mechanical body, hooked bill, compact folded wings and layered patinated armor." /><p class="illustrated-caption">${captureLabel}</p><div class="assembly-diagram" hidden><p>ILLUSTRATIVE ASSEMBLY · NOT A 3D VIEW</p><svg viewBox="0 0 500 230" role="img" aria-label="Schematic relationships of shell, drive, power and processing. Parts separate horizontally."><path d="M55 118H450" stroke="#a3a697" stroke-dasharray="5 7"/><g data-schematic="shell"><rect x="40" y="65" width="80" height="105" rx="18" fill="#736c50" stroke="#e6c58d"/><text x="80" y="192">Armor</text></g><g data-schematic="drive"><circle cx="210" cy="115" r="40" fill="#444b42" stroke="#e6c58d"/><circle cx="210" cy="115" r="27" fill="none" stroke="#e6c58d"/><text x="210" y="192">Wound drive</text></g><g data-schematic="power"><rect x="172" y="68" width="76" height="92" rx="9" fill="#d2cbb5"/><text x="210" y="192">Power</text></g><g data-schematic="mind"><rect x="320" y="79" width="80" height="63" fill="#576960" stroke="#e6c58d"/><path d="M330 90h60m-60 15h60m-60 15h60" stroke="#e6c58d"/><text x="360" y="192">Processing</text></g><g data-schematic="external"><path d="M155 105H240M240 85V150M190 120L115 130M105 165V205H140" stroke="#caa779" stroke-width="7" fill="none"/><circle cx="190" cy="105" r="7" fill="#dbb878"/><text x="235" y="192">Outside levers</text></g><g data-schematic="transmission"><path d="M252 115H365M345 115V150L380 165" stroke="#c8ad79" stroke-width="9" fill="none"/><circle cx="315" cy="115" r="24" fill="#756347" stroke="#ead4a3"/><text x="358" y="192">Cam → joints</text></g></svg><p class="diagram-note"></p></div></div>`;
  const diagram=container.querySelector('.assembly-diagram');
  const img=container.querySelector('img');
  let open=false,era='builder',separation=0;
  let imageFailed=false;
  const caption=container.querySelector('.illustrated-caption');
  img.addEventListener('error',()=>{imageFailed=true;img.hidden=true;caption.textContent='Exterior preview unavailable. The component descriptions remain available; Retry 3D also retries this image.';});
  function update(){
    if (img.getAttribute('src') !== previews[era]) { imageFailed=false;img.hidden=false;img.src=previews[era]; }
    img.alt=`${eraNames[era]} MurderBird exterior study, ${cinematicReview ? 'a fixed authoring render of the cinematic surface proposal' : 'a fixed capture of the Version 37 mechanical exhibit'}.`;
    caption.textContent=imageFailed?'Exterior preview unavailable. The component descriptions remain available; Retry 3D also retries this image.':(cinematicReview ? `${eraNames[era]} · ${captureLabel}` : `${eraNames[era]} exhibit · fixed captured view`);
    for(const id of ['beak','joint','shell','drive','power','mind','guard'])updateMarker(id,0,0,false);
    diagram.hidden=!open;
    for(const name of ['drive','power','mind','external','transmission'])diagram.querySelector(`[data-schematic="${name}"]`).style.display=(name==='external'?era==='maker':['drive','transmission'].includes(name)?era==='mechanic':era==='builder')?'':'none';
    diagram.querySelector('[data-schematic="shell"]').setAttribute('transform',`translate(${-20*separation} 0)`);
    diagram.querySelector('[data-schematic="mind"]').setAttribute('transform',`translate(${40*separation} 0)`);
    diagram.querySelector('.diagram-note').textContent=era==='maker'?'An outside operator moves the joints; a cradle supports the body. No internal power or intent. The 3D view demonstrates the control rods.':era==='mechanic'?'A finite mainspring drives reduction gears, cam timing and joint linkages. No sensing or tactical behavior.':'An abundant fictional supply feeds the actuators; sensing and processing control their coordinated action. No winding or power-depletion routine.';
  }
  update();
  return {kind:'illustrated',resize:update,tick(){},select(){},reset(){},nudge(){},focus(){},setArmed(){},setEra(value){era=value;update();},setSection(value){open=value;update();},setSeparation(value){separation=value;update();},isAssembled(){return !open;},metrics(){return {kind:'illustrated',era,open,separation};},destroy(){container.replaceChildren();}};
}
