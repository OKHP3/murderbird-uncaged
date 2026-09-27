// A fixed, authentic reference image with a clearly separate assembly diagram.
// No 2D distortion is presented as spatial orbit or as a rendered 3D model.
const referenceUrl = new URL('../../assets/img/webp/murderbird-unified-master-03-2026-09-06-960.webp', import.meta.url).href;
export function createIllustratedExhibit(container, updateMarker) {
  container.innerHTML = `<div class="illustrated-view"><img src="${referenceUrl}" alt="MurderBird production reference: heavy floor-standing mechanical body, hooked bill, compact folded wings and layered patinated armor." /><p class="illustrated-caption">Illustrated reference · fixed view</p><div class="assembly-diagram" hidden><p>ILLUSTRATIVE ASSEMBLY · NOT A 3D VIEW</p><svg viewBox="0 0 500 230" role="img" aria-label="Schematic relationships of shell, drive, power and processing. Parts separate horizontally."><path d="M55 118H450" stroke="#a3a697" stroke-dasharray="5 7"/><g data-schematic="shell"><rect x="40" y="65" width="80" height="105" rx="18" fill="#736c50" stroke="#e6c58d"/><text x="80" y="192">Armor</text></g><g data-schematic="drive"><circle cx="210" cy="115" r="40" fill="#444b42" stroke="#e6c58d"/><circle cx="210" cy="115" r="27" fill="none" stroke="#e6c58d"/><text x="210" y="192">Wound drive</text></g><g data-schematic="power"><rect x="172" y="68" width="76" height="92" rx="9" fill="#d2cbb5"/><text x="210" y="192">Power</text></g><g data-schematic="mind"><rect x="320" y="79" width="80" height="63" fill="#576960" stroke="#e6c58d"/><path d="M330 90h60m-60 15h60m-60 15h60" stroke="#e6c58d"/><text x="360" y="192">Processing</text></g></svg><p class="diagram-note"></p></div></div>`;
  const diagram=container.querySelector('.assembly-diagram');
  const img=container.querySelector('img');
  let open=false,era='builder',separation=0;
  img.addEventListener('error',()=>{img.hidden=true;container.querySelector('.illustrated-caption').textContent='Reference image unavailable. The component descriptions remain available; Retry 3D also retries this image.';});
  function update(){
    for(const id of ['beak','joint','shell','drive','power','mind','guard'])updateMarker(id,0,0,false);
    diagram.hidden=!open;
    for(const name of ['drive','power','mind'])diagram.querySelector(`[data-schematic="${name}"]`).style.display=(name==='drive'?era==='mechanic':era==='builder')?'':'none';
    diagram.querySelector('[data-schematic="shell"]').setAttribute('transform',`translate(${-20*separation} 0)`);
    diagram.querySelector('[data-schematic="mind"]').setAttribute('transform',`translate(${40*separation} 0)`);
    diagram.querySelector('.diagram-note').textContent=era==='maker'?'Ancient mechanism unresolved. No heart or brain is asserted.':era==='mechanic'?'Winding stores finite energy; the cranial chamber remains empty.':'Stored energy in the breast and processing behind the eyes are separate systems.';
  }
  update();
  return {kind:'illustrated',resize:update,tick(){},select(){},reset(){},nudge(){},focus(){},setArmed(){},setEra(value){era=value;update();},setSection(value){open=value;update();},setSeparation(value){separation=value;update();},isAssembled(){return !open;},metrics(){return {kind:'illustrated',era,open,separation};},destroy(){container.replaceChildren();}};
}
