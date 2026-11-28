import {rigidRuns} from './rig-bindings.mjs';

// Targets use the frozen glTF's Y-up frame; anatomical left is negative X.
const regions = {
  all: ['All exterior panels', [0,1.21,.06], -70,8,3.55,1.55],
  head: ['Head and crown', [-.055,1.73,.22], -70,12,1.75,.8],
  optic: ['Recessed optic', [-.145,1.72,.38], -82,3,1.10,.54],
  bill: ['Bill and mandible',[-.05,1.63,.43], -77,0,1.55,.67],
  neck: ['Neck and collar',[-.045,1.43,.16], -64,10,1.6,.70],
  breast: ['Breast and thorax',[-.075,1.08,.035], -65,7,2.2,.96],
  'left-wing': ['Left shoulder and wing',[-.22,1.17,-.07], -88,14,2.18,1.00],
  'right-wing': ['Right shoulder and wing',[.22,1.17,-.07], 86,15,2.18,1.00],
  rear: ['Back and tail', [0,.91,-.29], -136,12,2.15,.88],
  hips: ['Pelvis and hips', [-.11,.83,-.085], -107,4,1.75,.80],
  'left-leg': ['Left thigh, shin and ankle',[-.19,.47,-.10], -72,5,2.00,.87],
  'right-leg': ['Right thigh, shin and ankle',[.19,.47,-.10], 72,5,2.00,.87],
  'left-foot': ['Left toes and talons',[-.22,.075,.05], -54,23,1.68,.71],
  'right-foot': ['Right toes and talons',[.22,.075,.05], 54,23,1.68,.71],
  service: ['Power, processing and service', [-.04,1.38,.02], -76,6,3.18,1.37],
  support: ['External support and saddle',[-.05,.76,.42], -57,15,1.83,.82],
};
export const regionViews=Object.fromEntries(Object.entries(regions).map(([id,[, ...framing]])=>['region-'+id,framing]));
export const regionOptions=Object.fromEntries(Object.entries(regions).map(([id,row])=>[id,row[0]]));
const eraText={
 maker:{head:'The hand-worked cranial links sit behind the dark eye.',breast:'The operator’s lever acts through the bronze wheel and timber linkage.',manual:'An external operator supplies the motion.'},
 mechanic:{head:'A small regulator sits inside the cranial recess. The optic stays dark.',breast:'The wound clockwork drives the geared train inside this chest.',manual:'Clockwork drives a finite, repeatable movement.'},
 advanced:{head:'Blue processing blades sit behind the amber optic.',breast:'The insulated amber energy vessel occupies the chest, separate from the head processor.',manual:'The bird carries and directs its own motion.'},
};
export function regionCopy(era,id){
 const e=eraText[era]||eraText.advanced;
 const notes={
 all:e.breast+' '+e.head, head:'The crown cover lifts above the socket. '+e.head,
 optic:'The left lens and bezel draw out along the socket axis, revealing the retained recess. '+e.head,
 bill:'The lower mandibular casting separates around the cheek hinge. The hooked upper bill stays seated. '+e.manual,
 neck:'The near overlapping neck guards separate from their underlying bridge. '+e.manual,
 breast:'The near mantle clears the breast cover. '+e.breast,
 'left-wing':'The left mantle opens at its shoulder. Follow the inherited repair and the joint behind its compact folded plates. '+e.manual,
 'right-wing':'The right mantle opens independently. Its shoulder and elbow remain seated behind the outer plates. '+e.manual,
 rear:'The compact tail assembly separates rearward from its attachment under the rump. '+e.manual,
 hips:'The left upper-leg housing slides away from its seat below the pelvis. The opposite hip remains assembled. '+e.manual,
 'left-leg':'The outer casing separates from the left leg. The complementary castings stay with the body. '+e.manual,
 'right-leg':'The outer casing separates from the right leg. The complementary castings stay with the body. '+e.manual,
 'left-foot':'The left toe-end castings separate from their root segments. The supporting foot stays planted. '+e.manual,
 'right-foot':'The right toe-end castings separate from their root segments. The supporting foot stays planted. '+e.manual,
 service:e.breast+' '+e.head,
 support:'The retained saddle lifts clear of its bearing. The fixed post and floor base reveal the support path. '+e.manual,
 };
 return notes[id]||notes.all;
}

// Discrete extraction uses the authored GLB triangle ranges for the mandibular
// and tail castings. Other local selections follow anatomy, material and side.
const extraction={
 optic:{source:'head',travel:[-.16,0,.013],match:(x,y,z,m)=>x<0&&/protected (glass|bronze|core) builder/i.test(m)},
 bill:{source:'head',pivot:[0,-.01,-.065],axis:[1,0,0],turn:.5,travel:[0,-.023,.020],part:9},
 neck:{source:'neck',travel:[-.19,.055,.045],match:(x,y,z,m)=>x<-.005 && /Breast|Steel/.test(m)},
 rear:{source:'body',travel:[0,.085,-.22],part:10},
 hips:{source:'leg',travel:[-.19,.036,-.025],match:(x,y,z,m)=>x<-.005&&y>.735&&/Iron|Steel/.test(m)},
 'left-leg':{source:'leg',travel:[-.185,.014,-.017],match:(x,y,z,m)=>x<-.01&&y<=.737&&/Iron|Steel/.test(m)},
 'right-leg':{source:'leg',travel:[.185,.014,-.017],match:(x,y,z,m)=>x>.01&&y<=.737&&/Iron|Steel/.test(m)},
 'left-foot':{source:'foot',travel:[-.085,.112,.021],match:(x,y,z,m,i)=>x<0&&i>=12&&i%2===0},
 'right-foot':{source:'foot',travel:[.085,.112,.021],match:(x,y,z,m,i)=>x>0&&i>=12&&i%2===0},
};
export function installRegionalParts(T,nodes) {
 const cache=new Map(),owned=new Set();
 const wingRight=nodes.get('wing.r'),saddle=nodes.get('assembly support saddle');
 const origin=new Map([wingRight,saddle].map(o=>[o,{p:o.position.clone(),q:o.quaternion.clone()}]));
 const V=a=>new T.Vector3(...a);
 function sectionGeo(original,index) {
  const g=new T.BufferGeometry();
  for(const [name,attr] of Object.entries(original.attributes))g.setAttribute(name,attr);
  g.setIndex(index);g.boundingBox=original.boundingBox;g.boundingSphere=original.boundingSphere;
  owned.add(g);return g;
 }
 // Capture inputs before any motion adapter replaces original geometry/materials.
 const leaves=new Map();
 for(const key of new Set(Object.values(extraction).map(v=>v.source))){
  leaves.set(key,nodes.get(key).children.filter(o=>o.isMesh&&!o.userData.fc_inspection).map(o=>({o,g:o.geometry,m:o.material.name})));
 }
 function compile(id) {
  const def=extraction[id],rows=[];
  for(const {o,g,m} of leaves.get(def.source)){
   const index=g.index,pos=g.attributes.position,length=index?index.count:pos.count;
   const keep=[],out=[],runs=rigidRuns[def.source+'|'+m]?.[1]||[];
   let k=0,limit=runs[0]||Infinity,piece=runs[1]||0;
   for(let n=0;n<length;n+=3){
    while(n/3>=limit && k+2<runs.length){k+=2;limit+=runs[k];piece=runs[k+1];}
    const a=index?index.getX(n):n,b=index?index.getX(n+1):n+1,c=index?index.getX(n+2):n+2;
    const avg=(attr)=> (pos[attr](a)+pos[attr](b)+pos[attr](c))/3;
    const chosen=def.part!==undefined?piece===def.part:def.match(avg('getX'),avg('getY'),avg('getZ'),m,piece);
    (chosen?out:keep).push(a,b,c);
   }
   if(!out.length)continue;
   const part=new T.Mesh(sectionGeo(g,out),o.material);
   part.name=regionOptions[id]+' · original casting';part.userData.fc_inspection=true;part.visible=false;
   part.castShadow=o.castShadow;part.receiveShadow=o.receiveShadow;o.add(part);
   rows.push({o,g,other:sectionGeo(g,keep),part,total:length/3,moved:out.length/3});
  }
  if(!rows.length)throw Error('No authored triangles matched '+id);
  cache.set(id,rows);return rows;
 }
 const rightAxis=V([0,0,1]),q=new T.Quaternion(),temp=new T.Vector3();
 function apply(id,t){
  if(id==='right-wing'||id==='support'){
   const o=id==='right-wing'?wingRight:saddle,r=origin.get(o);
   o.position.copy(r.p);o.quaternion.copy(r.q);
   if(t && id==='right-wing'){q.setFromAxisAngle(rightAxis,2.15*t);o.quaternion.multiply(q);
    const hinge=V([.238,1.317,.039]);o.position.add(hinge.clone().sub(temp.copy(hinge).applyQuaternion(q)).applyQuaternion(r.q));}
   if(t && id==='support')o.position.addScaledVector(V([0,.16,.082]),t);
   return;
  }
  if(!extraction[id])return;
  const def=extraction[id],rows=cache.get(id)||(t?compile(id):[]);
  for(const {o,g,part,other} of rows){
   o.geometry=t?other:g;part.visible=Boolean(t);part.material=o.material;
   part.quaternion.identity();part.position.set(0,0,0);
   if(t){
    if(def.axis){q.setFromAxisAngle(V(def.axis),def.turn*t);part.quaternion.copy(q);const hinge=V(def.pivot);part.position.copy(hinge).sub(temp.copy(hinge).applyQuaternion(q));}
    part.position.addScaledVector(V(def.travel),t);
   }
  }
 }
 function proof(id){
  const r=cache.get(id);
  if(!r)return null;
  return r.map(({o,g,other,part,total,moved})=>({name:o.name,selectedTriangles:moved,restTriangles:total,visibleTriangles:(o.geometry.index?.count??o.geometry.attributes.position.count)/3+(part.visible?moved:0),originalGeometry:o.geometry===g,remainderActive:o.geometry===other,separated:part.visible,local:part.position.toArray()}));
 }
 function dispose(){
  for(const rows of cache.values())for(const {part} of rows)part.removeFromParent();
  for(const g of owned){for(const name of Object.keys(g.attributes))g.deleteAttribute(name);g.dispose();}
 }
 return {apply,proof,dispose};
}
