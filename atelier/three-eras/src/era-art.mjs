/* Private digital reconstruction for the accepted First Choice form. Coordinates are
 * glTF scene units, +Y up, +Z toward the bill, -X anatomical left. No external assets. */
export function installEraArt(THREE, modelRoot, scene) {
  const T = THREE;
  const V = (x, y, z) => new T.Vector3(x, y, z);
  const vec = a => V(...a);
  const up = V(0, 1, 0);
  const tau = Math.PI * 2;
  const clamp = n => Math.max(0, Math.min(1, Number.isFinite(n) ? n : 0));
  const pivot = {};
  const originals = [];
  modelRoot.traverse(o => {
    if (o.userData.fc_region) pivot[o.userData.fc_region] = o;
    if (o.isMesh && o.material) originals.push([o, o.material]);
  });
  if (!pivot.torso || !pivot.stand || !pivot.head) throw new Error('First Choice rigid pivots are required');
  const originalMaterials = [...new Set(originals.flatMap(([, m]) => Array.isArray(m) ? m : [m]))];
  const generatedMaterials = new Set();
  const geometries = new Set();
  const groups = [];
  const own = g => { geometries.add(g); return g; };
  function material(name, hex, metalness, roughness) {
    const m = new T.MeshStandardMaterial({color: hex, metalness, roughness});
    m.name = name; generatedMaterials.add(m); return m;
  }
  const bronze = material('Forged warm bronze', 0x967341, .72, .5);
  const burnished = material('Worn bronze edges', 0xba9257, .70, .39);
  const iron = material('Blued forged iron', 0x3a4041, .68, .49);
  const worn = material('Worked steel lands', 0x81817a, .82, .39);
  const black = material('Oxidized recess', 0x242320, .51, .69);
  const copper = material('Copper solder and bushing', 0x8b563d, .73, .55);
  const oak = material('Hand-polished walnut', 0x5b3520, .04, .58);
  const patina = material('Oxidized bronze casting', 0x48574c, .54, .7);
  const cord = material('Waxed flax cord', 0x73664b, .03, .89);
  // Tangential tooling lines, oxidation and hand grain. Generated once, shared in
  // memory. Using the approved shell's own fine normal maps keeps the new fittings
  // in the same material world without adding another set of image files.
  const finishMaps = new Set();
  function surfaceGrain(target, kind) {
    const width = 128, bytes = new Uint8Array(width*width*4);
    let seed = kind==='wood'?331:kind==='oxide'?1211:151;
    const noise = () => ((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
    for (let y=0;y<width;y++) for(let x=0;x<width;x++) {
      const u=x/width*tau,v=y/width*tau,grain=noise(), index=(y*width+x)*4;
      const pools=(Math.sin(u*3+Math.sin(v*2))+.7*Math.sin(v*5+u*2)+.4*Math.sin(9*u+v*7))/2.1;
      const lines=kind==='wood'?Math.pow(.5+.5*Math.sin(18*u+.85*Math.sin(v)+2*pools),4):Math.pow(.5+.5*Math.cos(41*v+.3*Math.sin(4*u)),9);
      const value=kind==='wood'?.70+.25*pools-.29*lines+.08*grain:kind==='oxide'?.67+.22*pools-.09*lines+.15*grain:.72+.15*pools-.18*lines+.16*grain;
      bytes[index]=Math.min(255,248*value);bytes[index+1]=Math.min(255,(kind==='wood'?224:245)*value);bytes[index+2]=Math.min(255,(kind==='wood'?192:238)*value);bytes[index+3]=255;
    }
    const map=new T.DataTexture(bytes,width,width);map.colorSpace=T.SRGBColorSpace;
    map.wrapS=map.wrapT=T.RepeatWrapping;map.repeat.set(3,3);map.magFilter=T.LinearFilter;
    map.minFilter=T.LinearMipmapLinearFilter;map.generateMipmaps=true;map.needsUpdate=true;finishMaps.add(map);
    target.map=map;
    const exemplar=originalMaterials.find(m=>m.name.toLowerCase().endsWith(kind==='oxide'?'iron':'steel'));
    if(kind!=='wood' && exemplar?.normalMap){target.normalMap=exemplar.normalMap;target.normalScale.set(.38,.38);}
  }
  for(const target of [iron,worn,bronze,burnished,copper])surfaceGrain(target,'steel');
  for(const target of [patina,black])surfaceGrain(target,'oxide');
  surfaceGrain(oak,'wood');
  const cylinder = own(new T.CylinderGeometry(1, 1, 1, 16));
  const hex = own(new T.CylinderGeometry(1, 1, 1, 6));
  const cube = own(new T.BoxGeometry(1, 1, 1));
  const ball = own(new T.SphereGeometry(1, 16, 12));
  const workingMatrix = new T.Matrix4();
  const tempQuaternion = new T.Quaternion();
  const geometryIDs = new Map();
  const matIDs = new Map();
  const binMap = new Map();
  function group(name, parent, p = [0,0,0]) {
    const g = new T.Group(); g.name = name; parent.add(g); g.position.set(...p); return g;
  }
  function mesh(name, g, m, parent) {
    const a = new T.Mesh(g, m); a.name = name; a.castShadow = true; a.receiveShadow = true;
    parent.add(a); return a;
  }
  // Store repeated hardware by pose owner/shape/material. This keeps pin rows and
  // reinforcement hardware inexpensive without welding independent moving parts.
  function stamp(parent, geo, mat, p, scale, rotation = null) {
    if (!geometryIDs.has(geo)) geometryIDs.set(geo, geometryIDs.size);
    if (!matIDs.has(mat)) matIDs.set(mat, matIDs.size);
    const key = parent.uuid + ':' + geometryIDs.get(geo) + ':' + matIDs.get(mat);
    if (!binMap.has(key)) binMap.set(key, {parent, geo, mat, poses:[]});
    const q = rotation || tempQuaternion.identity();
    binMap.get(key).poses.push(workingMatrix.compose(p, q, scale).clone());
  }
  function flush() {
    for (const {parent, geo, mat, poses} of binMap.values()) {
      const obj = new T.InstancedMesh(geo, mat, poses.length);
      obj.name = mat.name + ' · ' + poses.length; obj.castShadow = true; obj.receiveShadow = true;
      poses.forEach((matrix, index) => obj.setMatrixAt(index, matrix));
      obj.instanceMatrix.needsUpdate = true; obj.computeBoundingSphere(); parent.add(obj);
    }
    binMap.clear();
  }
  function rod(parent, a, b, radius, mat, profile = cylinder) {
    const start = vec(a), end = vec(b), d = end.clone().sub(start), length = d.length();
    if (length < 1e-8) return;
    const q = new T.Quaternion().setFromUnitVectors(up, d.multiplyScalar(1 / length));
    stamp(parent, profile, mat, start.add(end).multiplyScalar(.5), V(radius, length, radius), q);
  }
  function box(parent, p, sizes, m) { stamp(parent, cube, m, vec(p), vec(sizes)); }
  function knob(parent, p, sizes, m) { stamp(parent, ball, m, vec(p), vec(sizes)); }
  function axle(parent, x, y, z, r, width, mat, profile = cylinder) {
    rod(parent, [x-width/2,y,z], [x+width/2,y,z], r, mat, profile);
  }
  function shape(points) {
    const s = new T.Shape(); s.moveTo(...points[0]); points.slice(1).forEach(p => s.lineTo(...p));
    s.closePath(); return s;
  }
  function hole(s, horizontal, vertical, radius) {
    const h = new T.Path(); h.absarc(horizontal, vertical, radius, 0, tau, false); s.holes.push(h);
  }
  // Shape coordinates are (+Z, +Y), and extrusion extends toward anatomical left.
  function plate(parent, name, outline, x, y, z, thickness, m, bevel = .0008) {
    const g = own(new T.ExtrudeGeometry(outline, {depth:thickness,bevelEnabled:bevel>0,bevelSize:bevel,bevelThickness:bevel,bevelSegments:1,curveSegments:20}));
    g.rotateY(-Math.PI/2); const a = mesh(name, g, m, parent); a.position.set(x,y,z); return a;
  }
  function eyeBolt(parent, x,y,z,r) {
    axle(parent,x,y,z,r,.009,black); axle(parent,x-.006,y,z,r*.82,.008,burnished,hex);
    axle(parent,x-.011,y,z,r*.38,.004,iron,hex);
  }
  function link(parent,name,radius,mat) {
    const obj = mesh(name, cylinder, mat, parent);
    return (a,b) => {
      const delta = b.clone().sub(a), length = delta.length();
      obj.visible = length > 1e-7;
      obj.position.copy(a).add(b).multiplyScalar(.5);
      obj.scale.set(radius, Math.max(length,1e-8), radius);
      if (obj.visible) obj.quaternion.setFromUnitVectors(up,delta.multiplyScalar(1/length));
    };
  }
  modelRoot.updateWorldMatrix(true,true);
  function originalPoint(parent, xyz) {
    return parent.worldToLocal(modelRoot.localToWorld(vec(xyz)));
  }
  function rootFrameParent(name, target) {
    const g = group(name,target); g.position.copy(originalPoint(target,[0,0,0])); groups.push(g); return g;
  }
  const maker = rootFrameParent('Maker · fixed hand rack',pivot.stand);
  const mechanic = rootFrameParent('Mechanic · finite spring train',pivot.torso);
  const makerMark = rootFrameParent('Maker · shoulder witness marks',pivot.torso);
  maker.userData.eraArt = 'maker'; makerMark.userData.eraArt = 'maker'; mechanic.userData.eraArt = 'mechanic';

  // A free-standing, stayed control rack. Its splayed timbers, carried axle,
  // socketed fulcrums and drawn linkages are separate from the bird's anatomy.
  const rackX = -.55;
  [-.48, -.10].forEach(z => {
    rod(maker,[rackX-.105,.028,z],[rackX-.012,.47,z],.026,oak,hex);
    rod(maker,[rackX+.113,.028,z],[rackX+.01,.47,z],.024,oak,hex);
    box(maker,[rackX,.036,z],[.285,.042,.083],iron);
    box(maker,[rackX,.409,z],[.075,.049,.065],bronze);
    [-.112,.111].forEach(dx=>rod(maker,[rackX+dx,.055,z],[rackX+dx,.073,z],.012,burnished,hex));
  });
  box(maker,[rackX,.456,-.286],[.095,.058,.47],oak);
  box(maker,[rackX+.058,.432,-.286],[.015,.064,.466],bronze);
  rod(maker,[rackX-.049,.494,-.51],[rackX-.049,.494,-.063],.012,bronze);
  rod(maker,[rackX+.071,.074,-.48],[rackX+.071,.398,-.10],.012,iron);
  rod(maker,[rackX+.071,.074,-.10],[rackX+.071,.398,-.48],.012,iron);
  const controlNames = ['leg','wing','tail','neck','jaw'];
  const guideEnd = [ [-.214,.590,-.010],[-.349,1.101,.042],[-.034,.971,-.376],[-.114,1.390,.114],[-.143,1.576,.313] ];
  const targetPivots = [pivot.ground,pivot.torso,pivot.torso,pivot.neck,pivot.head];
  const levers = [];
  for (let i=0;i<controlNames.length;i++) {
    const z = -.452 + i*.083;
    const fulcrum = group('Hand pull · '+controlNames[i], maker, [rackX-.058,.494,z]);
    const lift = .186 + i*.015;
    const handleTip = V(-.072,lift,0);
    rod(fulcrum,[.026,-.041,0],[-.067,lift-.034,0],.0105,bronze);
    rod(fulcrum,[-.061,lift-.052,0],[-.077,lift+.015,0],.012,oak);
    knob(fulcrum,handleTip.toArray(),[.018,.034,.018],oak);
    rod(fulcrum,[-.066,lift-.042,0],[-.069,lift-.032,0],.013,burnished);
    rod(fulcrum,[.008,-.018,0],[.061,-.062,0],.008,iron);
    rod(maker,[rackX-.055,.465,z-.018],[rackX-.055,.505,z-.018],.013,bronze);
    rod(maker,[rackX-.055,.465,z+.018],[rackX-.055,.505,z+.018],.013,bronze);
    rod(fulcrum,[0,0,-.026],[0,0,.026],.013,worn);
    const guide = V(rackX+.077,.347,z);
    rod(maker,[guide.x,guide.y-.025,z],[guide.x,guide.y+.025,z],.010,bronze);
    const mast = V(-.407,.70+i*.076,-.29+i*.045);
    const sheaveGeo = own(new T.TorusGeometry(.024,.005,8,24));
    const sheave = mesh('External cord guide · '+controlNames[i],sheaveGeo,bronze,maker);
    sheave.position.copy(mast);sheave.rotation.y=Math.PI/2;
    axle(maker,mast.x,mast.y,mast.z,.008,.036,iron);
    rod(maker,[rackX+.048,.473,z],mast.toArray(),.0055,iron);
    rod(maker,guide.toArray(),mast.toArray(),.0022,cord);
    const target = originalPoint(targetPivots[i],guideEnd[i]);
    const clevis = group('Lever clevis · '+controlNames[i],targetPivots[i],target.toArray());
    clevis.userData.eraArt='maker';groups.push(clevis);
    axle(clevis,0,0,0,.012,.026,bronze); axle(clevis,-.014,0,0,.006,.006,worn);
    const takeUp = link(maker,'Hand-operated drawbar · '+controlNames[i],.004,worn);
    const controlLine = link(maker,'Waxed line · '+controlNames[i],.0028,cord);
    levers.push({fulcrum,guide,mast,target,clevis,rootPoint:vec(guideEnd[i]),anchor:targetPivots[i],takeUp,controlLine});
  }

  // A compact, open-faced drive clamped below the left folded guard. The visible
  // spiral, keyed spur pair, eccentric, follower and stop are one series train.
  const bracket = shape([[-.186,-.068],[-.167,-.113],[.157,-.104],[.205,-.045],[.186,.048],[.097,.087],[-.041,.108],[-.162,.052]]);
  hole(bracket,-.110,-.055,.017); hole(bracket,.145,.005,.015);
  plate(mechanic,'Cast cheek plate with relieved pin holes',bracket,-.296,.899,-.004,.034,patina,.003);
  const strap = shape([[-.182,-.014],[-.173,-.021],[.151,-.019],[.177,-.010],[.176,.008],[.142,.016],[-.165,.018]]);
  plate(mechanic,'Forged lower bearer',strap,-.326,.815,-.005,.012,iron,.0017);
  for(const [z,y] of [[-.146,.89],[-.141,.846],[.149,.857],[.124,.957]]) {
    axle(mechanic,-.30,y,z,.026,.080,iron,hex);eyeBolt(mechanic,-.345,y,z,.015);
  }
  const rotorA=group('Clockwork · spring barrel and 32-tooth driver',mechanic,[-.352,.942,-.061]);
  const rotorB=group('Clockwork · 16-tooth pinion and eccentric',mechanic,[-.352,.920,.071]);
  function gear(parent,teeth,pitch,metal,slots) {
    const points=[];
    for(let i=0;i<teeth;i++) {
      for(const [offset,r] of [[-.5,pitch*.94],[-.32,pitch*.94],[-.20,pitch*1.055],[.20,pitch*1.055],[.32,pitch*.94]]) {
        const a=(i+offset)/teeth*tau; points.push([Math.cos(a)*r,Math.sin(a)*r]);
      }
    }
    const s=shape(points); const rr=pitch*.22;
    for(let i=0;i<slots;i++){const a=i/slots*tau;hole(s,Math.cos(a)*pitch*.58,Math.sin(a)*pitch*.58,rr);}
    plate(parent,'Relieved spur wheel '+teeth,s,0,0,0,.012,metal,pitch*.012);
    axle(parent,-.01,0,0,pitch*.23,.035,burnished);axle(parent,-.026,0,0,pitch*.13,.009,iron,hex);
  }
  gear(rotorA,32,.089,iron,5);gear(rotorB,16,.0447,burnished,3);
  rotorB.rotation.x=Math.PI/16;
  function coil(parent) {
    const positions=[],indices=[],steps=210;
    for(let i=0;i<=steps;i++){
      const t=i/steps,a=t*Math.PI*8.5,r=.014+t*.062;
      for(const [x,dr] of [[-.027,-.002],[-.043,-.002],[-.043,.002],[-.027,.002]])
        positions.push(x,Math.sin(a)*(r+dr),Math.cos(a)*(r+dr));
      if(i) for(let k=0;k<4;k++){
        const p=(i-1)*4+k,q=(i-1)*4+(k+1)%4,u=p+4,v=q+4;indices.push(p,q,v,p,v,u);
      }
    }
    const geo=own(new T.BufferGeometry());geo.setAttribute('position',new T.Float32BufferAttribute(positions,3));
    geo.setIndex(indices);geo.computeVertexNormals();mesh('Flat-strip mainspring between retaining cheeks',geo,worn,parent);
    axle(parent,-.046,0,0,.012,.012,copper,hex);
  }
  coil(rotorA);
  // A fixed case rim and retaining dogs keep the spring's outer turn visually seated.
  const rim=mesh('Bronze open spring case',own(new T.TorusGeometry(.080,.0048,8,56)),patina,mechanic);
  rim.position.set(-.402,.942,-.061);rim.rotation.y=Math.PI/2;
  for(const a of [.27,2.34,4.47]) {
    const y=.942+Math.sin(a)*.083,z=-.061+Math.cos(a)*.083;
    axle(mechanic,-.366,y,z,.008,.077,iron);axle(mechanic,-.408,y,z,.010,.010,burnished,hex);
  }
  const cam=shape(Array.from({length:64},(_,i)=>{const a=i/64*tau;return [.022+Math.cos(a)*.031,Math.sin(a)*.031];}));
  plate(rotorB,'Offset circular cam',cam,-.023,0,0,.014,copper,.001);
  axle(rotorB,-.043,0,.022,.008,.013,iron);
  // Set the spring barrel's stops off the moving rotor; their anchors terminate in the case.
  rod(mechanic,[-.413,.878,-.139],[-.406,.90,-.12],.006,iron);
  rod(mechanic,[-.415,.877,-.142],[-.392,.866,-.159],.008,copper);
  const slider=group('Clockwork · guided advance bar',mechanic,[-.393,.920,.132]);
  axle(slider,0,0,0,.009,.022,worn);
  rod(slider,[0,0,0],[0,0,.081],.0057,worn);
  box(slider,[0,0,.060],[.014,.017,.043],iron);
  knob(slider,[0,0,.09],[.006,.008,.009],copper);
  [-.013,.013].forEach(dy=>box(mechanic,[-.393,.920+dy,.179],[.030,.009,.054],patina));
  const cycleRod=link(mechanic,'Follower to lower bellcrank',.005,worn);
  const rocker=group('Clockwork · output bellcrank',mechanic,[-.376,.839,.128]);
  rod(rocker,[0,0,0],[0,.018,.047],.011,iron);axle(rocker,-.010,0,0,.017,.025,burnished);
  const jointLink=link(mechanic,'Bellcrank to retained hip socket',.006,iron);
  const hipCup=V(-.216,.865,-.105);
  axle(mechanic,hipCup.x,hipCup.y,hipCup.z,.021,.075,iron);

  // Place the asymmetric shoulder splice and Maker witnesses on the actual folded
  // guard. Its changing curvature is sampled once, with all new work parented to the torso.
  const leftMesh=[];
  modelRoot.traverse(o=>{if(o.userData.region==='wing.l')o.traverse(child=>{if(child.isMesh)leftMesh.push(child);});});
  // Native piece provenance: retain the backward-fitted bronze keeper and its
  // original peened pins in Maker. Only the later iron splice and its two newer
  // socket-head fasteners are omitted. `bind-maker-shoulder.py` reconstructs
  // these contiguous face runs from the original authoring operation.
  const lateRepairRuns={
    'First Choice · Iron':{triangles:46088,remove:[[45936,152]]},
    'First Choice · Steel':{triangles:8164,remove:[[7794,66],[8012,152]]},
  };
  const chronologicalPatch=[];
  for(const mesh of leftMesh){
    const entry=lateRepairRuns[mesh.material?.name];if(!entry)continue;
    const source=mesh.geometry,i=source.index.array;
    if(i.length!==entry.triangles*3)throw Error('Unrecognized left-shoulder primitive');
    const younger=[];let begin=0;
    for(const [start,count] of entry.remove){
      for(let k=begin;k<start*3;k++)younger.push(i[k]);begin=(start+count)*3;
    }
    for(let k=begin;k<i.length;k++)younger.push(i[k]);
    const clean=own(new T.BufferGeometry());for(const [name,attr] of Object.entries(source.attributes))clean.setAttribute(name,attr);
    clean.setIndex(younger);clean.boundingSphere=source.boundingSphere?.clone()||null;clean.boundingBox=source.boundingBox?.clone()||null;
    chronologicalPatch.push({mesh,source,clean});
  }
  if(chronologicalPatch.length!==2)throw Error('The two fitted shoulder parts could not be resolved');
  const ray=new T.Raycaster();
  function leftSurface(y,z) {
    const origin=modelRoot.localToWorld(V(-.78,y,z)), direction=V(1,0,0).transformDirection(modelRoot.matrixWorld);
    ray.set(origin,direction);
    const hit=ray.intersectObjects(leftMesh,false)[0];
    return hit?modelRoot.worldToLocal(hit.point.clone()):null;
  }
  const repairLine=[];
  for(const [y,z] of [[1.363,.052],[1.349,.065],[1.333,.078],[1.315,.094],[1.298,.108],[1.277,.126],[1.252,.143]]){
    const p=leftSurface(y,z);if(p)repairLine.push(p);
  }
  if(repairLine.length>2){
    const pts=[],inds=[];
    for(const p of repairLine){
      for(const dz of [-.018,.018]){const h=leftSurface(p.y,p.z+dz)||p;pts.push(h.x-.007,h.y,h.z);}
    }
    for(let i=1;i<repairLine.length;i++){const a=(i-1)*2;inds.push(a,a+1,a+3,a,a+3,a+2);}
    const geo=own(new T.BufferGeometry());geo.setAttribute('position',new T.Float32BufferAttribute(pts,3));geo.setIndex(inds);geo.computeVertexNormals();
    const patched=material('Hammered splice · blackened iron',0x454239,.76,.6);patched.side=T.DoubleSide;
    mesh('Mechanic · fitted left shoulder repair strap',geo,patched,mechanic);
    repairLine.forEach((p,i)=>{
      if(i===0 || i===repairLine.length-1 || i===2 || i===4)eyeBolt(mechanic,p.x-.012,p.y,p.z,.0083);
      if(i<repairLine.length-1){const end=repairLine[i+1];rod(mechanic,[p.x-.009,p.y,p.z-.013],[end.x-.009,end.y,end.z-.013],.0021,copper);}
    });
  }
  for(let i=0;i<4;i++) {
    const z=-.045-i*.014,y=1.315-i*.009;
    const a=leftSurface(y,z),b=leftSurface(y-.013,z-.009),c=leftSurface(y-.006,z-.016);
    if(a&&b&&c){for(const p of [a,b,c])p.x-=.0023;rod(makerMark,a.toArray(),b.toArray(),.00135,burnished);rod(makerMark,b.toArray(),c.toArray(),.00135,burnished);}
  }
  flush();

  const eraMaterials = new Map();
  function recolor(base, era) {
    const m=base.clone(); generatedMaterials.add(m); const name=base.name.toLowerCase();
    m.name=(era==='maker'?'Maker · ':'Mechanic · ')+base.name;
    if(name.includes('protected core')){m.visible=false;return m;}
    if(m.emissive){m.emissive.setHex(0);m.emissiveIntensity=0;m.emissiveMap=null;}
    if(name.includes('protected glass')){
      m.map=null;m.color.setHex(era==='maker'?0x101314:0x141512);
      m.roughness=era==='maker'?.25:.43;m.metalness=.32;
      if('transmission' in m)m.transmission=0;
      if('clearcoat' in m)m.clearcoat=era==='maker'?.48:.16;
      return m;
    }
    // Keep all original map, cavity and normal detail. Regional multipliers tint
    // the original patinated maps without reducing each era to one flat metal.
    let tint, roughness;
    const pale=name.includes('mantle')||name.includes('steel');
    const shell=name.includes('breast')||name.includes('brow');
    if(era==='maker'){
      tint=pale?0xd4b18b:shell?0xe4c18d:name.includes('bill')?0xccbaa1:0xdbccae;
      roughness=name.includes('talon')?.61:shell?.63:.69;
    } else {
      tint=pale?0x9eae9b:shell?0xb1aa84:name.includes('bill')?0xadaa9a:0xb0a894;
      roughness=shell?.89:.84;
    }
    if(m.color)m.color.multiply(new T.Color(tint));
    if('roughness'in m)m.roughness=Math.min(1,roughness);
    if('metalness'in m)m.metalness=Math.min(1,Math.max(.35,m.metalness));
    return m;
  }
  for(const era of ['maker','mechanic']) {
    eraMaterials.set(era,new Map(originalMaterials.map(m=>[m,recolor(m,era)])));
  }
  const overrideArrays=new Map();
  for(const era of ['maker','mechanic']){
    const lookup=eraMaterials.get(era), perObject=new Map();
    for(const [obj,m] of originals) perObject.set(obj,Array.isArray(m)?m.map(x=>lookup.get(x)):lookup.get(m));
    overrideArrays.set(era,perObject);
  }
  let active='advanced';let controlValues=Object.fromEntries(controlNames.map(k=>[k,0]));
  function updateLevers(){
    modelRoot.updateWorldMatrix(true,true);
    levers.forEach((item,i)=>{
      item.fulcrum.rotation.z=-.10+controlValues[controlNames[i]]*.58;
      const pick=maker.worldToLocal(item.fulcrum.localToWorld(V(.061,-.062,0)));
      item.takeUp(pick,item.guide);
      const query=modelRoot[Symbol.for('First Choice · exterior control terminal')];
      const terminal=query?.(controlNames[i],item.rootPoint) || item.anchor.localToWorld(item.target.clone());
      item.clevis.position.copy(item.anchor.worldToLocal(terminal.clone()));
      const end=maker.worldToLocal(terminal);
      item.controlLine(item.mast,end);
    });
  }
  function setControls(values) {
    for(const k of controlNames)if(Object.hasOwn(values,k))controlValues[k]=clamp(values[k]);
    if(active==='maker')updateLevers();
  }
  function advance(p) {
    // A dwell on either side of each short advance is visible in the wheel and
    // slider. A whole turn returns both gears and the eccentric to their starting alignment.
    const count=4,t=p*count,whole=Math.floor(t), part=t-whole;
    const u=clamp((part-.14)/.65),e=u*u*(3-2*u);
    const angle=(whole+e)/count*tau;
    rotorA.rotation.x=angle;rotorB.rotation.x=Math.PI/16-angle*2;
    const eccentric=rotorB.rotation.x,c=.022*Math.cos(eccentric),s=.022*Math.sin(eccentric);
    const at=.031*.031-s*s;
    const offset=c+Math.sqrt(Math.max(0,at));
    slider.position.z=.071+offset+.009;
    rocker.rotation.x=(offset-.029)*8;
    const wrist=rocker.position.clone().add(V(0,.018,.047).applyQuaternion(rocker.quaternion));
    cycleRod(slider.position.clone().add(V(0,0,.080)),wrist);
    jointLink(rocker.position.clone().add(V(0,-.021,-.037).applyQuaternion(rocker.quaternion)),hipCup);
  }
  function setPose(progress01) {
    const p=clamp(progress01);
    if(active==='maker')setControls({neck:p});
    if(active==='mechanic')advance(p);
  }
  function setEra(era) {
    if(!['maker','mechanic','advanced'].includes(era))throw new RangeError('Unknown era: '+era);
    active=era;for(const b of chronologicalPatch)b.mesh.geometry=era==='maker'?b.clean:b.source;
    for(const g of groups)g.visible=g.userData.eraArt===era;
    for(const [o,m] of originals)o.material=era==='advanced'?m:overrideArrays.get(era).get(o);
    controlValues=Object.fromEntries(controlNames.map(k=>[k,0]));setPose(0);
  }
  function dispose(){
    setEra('advanced');for(const g of groups){g.traverse(o=>{if(o.isInstancedMesh)o.dispose();});g.removeFromParent();}
    for(const g of geometries)g.dispose();for(const m of generatedMaterials)m.dispose();for(const m of finishMaps)m.dispose();
  }
  setEra('advanced');
  return {setEra,setPose,setControls,dispose};
}
