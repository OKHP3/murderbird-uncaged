import {installRegionalParts,regionOptions} from './regions.js';
/**
 * Reversible left-side cutaway for the retained04 First Choice GLB.
 * Shell triangles, the wing and all six animation pivots keep their authored parents.
 * Call setOpen with an absolute fraction and setEra with Maker, Mechanic or Advanced.
 */
export function installInspection(THREE, modelRoot, scene) {
  const regions = new Map();
  modelRoot.traverse(object => {
    if (object.userData.region) regions.set(object.userData.region, object);
  });
  for (const region of ['body', 'torso', 'wing', 'wing.l', 'head']) {
    if (!regions.has(region)) throw new Error('Inspection requires the authored region ' + region);
  }

  const generated = [];
  const ownedGeometries = new Set();
  const ownedMaterials = new Set();
  const V = (x, y, z) => new THREE.Vector3(x, y, z);
  const X = V(1, 0, 0), Y = V(0, 1, 0), Z = V(0, 0, 1);
  const offset = new THREE.Vector3();
  let activeEra = 'advanced', selected='all', openness = 0, phase = 0;
  const mechanisms = {};
  const movements = {maker: [], mechanic: [], advanced: []};
  const ease = value => {
    const t = Math.max(0, Math.min(1, value));
    return t * t * (3 - 2 * t);
  };

  function add(parent, object, name) {
    object.name = name;
    object.userData.fc_inspection = true;
    parent.add(object);
    generated.push(object);
    return object;
  }
  function group(parent, name) { return add(parent, new THREE.Group(), name); }
  function shellMaterial(name, color, metalness, roughness, glow = 0) {
    const material = new THREE.MeshStandardMaterial({
      name, color, metalness, roughness, emissive: glow, emissiveIntensity: glow ? .68 : 0
    });
    ownedMaterials.add(material);
    return material;
  }
  // A deterministic fine-grain bump gives the castings, wood and turned metal
  // different responses to the light. The scene needs no external texture.
  const bumpTextures = [];
  function finishTexture(wood) {
    const side=96, values=new Uint8Array(side*side*4);
    let seed=91703;
    const noise=()=>{seed=(1664525*seed+1013904223)>>>0; return seed/4294967296;};
    for(let y=0;y<side;y++) for(let x=0;x<side;x++) {
      const grain=Math.sin((x+.9*Math.sin(y*.12)+.35*Math.cos(y*.27))*.72);
      const v=wood?105+21*grain+9*(noise()-.5):112+45*(noise()-.5);
      const n=4*(y*side+x);
      values[n]=values[n+1]=values[n+2]=v;
      values[n+3]=255;
    }
    const texture=new THREE.DataTexture(values,side,side);
    texture.wrapS=texture.wrapT=THREE.RepeatWrapping;
    texture.minFilter=THREE.LinearMipmapLinearFilter;texture.magFilter=THREE.LinearFilter;
    texture.generateMipmaps=true;texture.needsUpdate=true;
    bumpTextures.push(texture);
    return texture;
  }
  const cast = shellMaterial('Oiled casting', 0x343331, .66, .56);
  const edge = shellMaterial('Worn steel bevel', 0x797b72, .76, .38);
  const dark = shellMaterial('Ceramic shadow', 0x181d1d, .2, .65);
  const brass = shellMaterial('Hand-rubbed brass', 0xb18245, .74, .39);
  const oak = shellMaterial('Seasoned oak', 0x63412a, .06, .83);
  const copper = shellMaterial('Wound copper', 0xae5e32, .78, .35);
  const porcelain = shellMaterial('Fired porcelain', 0xbbbaaa, .06, .37);
  const amber = shellMaterial('Amber reservoir', 0xd7892c, .25, .31, 0xff991d);
  const opal = shellMaterial('Pale blue processor glass', 0x768d9a, .34, .36, 0x5fa7c6);

  const metalGrain=finishTexture(false);
  for(const m of [cast,edge,brass,copper]) {m.bumpMap=metalGrain;m.bumpScale=.0018;}
  oak.bumpMap=finishTexture(true);oak.bumpScale=.003;
  amber.emissiveIntensity=.37;opal.emissiveIntensity=.38;
  function piece(parent, geometry, material, position, name) {
    ownedGeometries.add(geometry);
    const mesh = add(parent, new THREE.Mesh(geometry, material), name);
    mesh.position.copy(position);
    mesh.castShadow = mesh.receiveShadow = true;
    return mesh;
  }
  function box(parent, position, size, material, name) {
    return piece(parent, new THREE.BoxGeometry(...size), material, position, name);
  }
  function rod(parent, from, to, radius, material, name) {
    const delta = to.clone().sub(from);
    const mesh = piece(parent, new THREE.CylinderGeometry(radius, radius, delta.length(), 12),
      material, from.clone().lerp(to, .5), name);
    mesh.quaternion.setFromUnitVectors(Y, delta.normalize());
    return mesh;
  }
  function disc(parent, position, radius, thickness, material, name) {
    const mesh = piece(parent, new THREE.CylinderGeometry(radius, radius, thickness, 32),
      material, position, name);
    mesh.rotation.z = Math.PI / 2;
    return mesh;
  }
  function ring(parent, position, radius, wire, material, name) {
    const mesh = piece(parent, new THREE.TorusGeometry(radius, wire, 8, 48), material, position, name);
    mesh.rotation.y = Math.PI / 2;
    return mesh;
  }
  function hub(parent, y, z, radius, teeth, material) {
    const spindle = group(parent, teeth ? 'Escapement wheel' : 'Lever wheel');
    spindle.position.set(-.14, y, z);
    ring(spindle, V(0,0,0), radius * .85, radius * .086, material, 'Wheel rim');
    disc(spindle, V(0,0,0), radius * .21, .035, material, 'Keyed hub');
    const count = teeth ? 5 : 3;
    for (let i = 0; i < count; i++) {
      const a = 2 * Math.PI * i / count;
      rod(spindle, V(0,0,0), V(0, radius * .83 * Math.cos(a), radius * .83 * Math.sin(a)),
        radius * .062, material, 'Spoke');
    }
    // Cast teeth sit on a continuous annulus; the center stays open in silhouette.
    for (let i = 0; i < teeth; i++) {
      const a = 2 * Math.PI * i / teeth;
      const t = box(spindle, V(0, radius * .958 * Math.cos(a), radius * .958 * Math.sin(a)),
        [.023, radius * .18, radius * Math.PI / teeth], material, 'Gear tooth');
      t.rotation.x = a;
    }
    disc(spindle, V(-.022,0,0), radius * .116, .014, edge, 'Round spindle cap');
    return spindle;
  }
  // These backs and lips follow the compartment's oval rather than cutting
  // a rectangle across the original shell. Local negative X faces the opening.
  function dish(parent, center, ry, rz, metal, name) {
    const profile=[[.013,0],[.012,.64],[.008,.84],[-.003,.94],[-.015,.972],[-.016,1],[.004,1.012]];
    const xyz=[],indices=[],uv=[];
    for(let ringIndex=0;ringIndex<profile.length;ringIndex++) {
      const [depth,radius]=profile[ringIndex];
      for(let i=0;i<64;i++) {
        const a=i*Math.PI/32;
        xyz.push(depth,ry*radius*Math.cos(a),rz*radius*Math.sin(a));
        uv.push(.5+.5*radius*Math.cos(a),.5+.5*radius*Math.sin(a));
        if(ringIndex) {
          const a0=64*(ringIndex-1)+i,b0=64*(ringIndex-1)+(i+1)%64,a1=a0+64,b1=b0+64;
          indices.push(a0,b0,b1,a0,b1,a1);
        }
      }
    }
    const g=new THREE.BufferGeometry();
    g.setAttribute('position',new THREE.Float32BufferAttribute(xyz,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2));
    g.setIndex(indices);g.computeVertexNormals();
    return piece(parent,g,metal,center,name);
  }
  function washer(parent,position,r,material) {
    disc(parent,position,r,.009,material,'Edge washer');
    const cap=piece(parent,new THREE.CylinderGeometry(r*.63,r*.66,.012,6),edge,
      position.clone().add(V(-.006,0,0)),'Hex fastener');
    cap.rotation.z=Math.PI/2;
  }
  function chestMount(root) {
    dish(root,V(-.045,1.047,-.018),.272,.236,cast,'Rolled mounting recess');
    for(const y of [.92,1.17]) for(const z of [-.165,.136])
      washer(root,V(-.07,y,z),.012,brass);
    // A rear secondary frame and stamped mounting lugs are visible between mechanisms.
    for(const z of [-.105,.074]) {
      rod(root,V(-.067,.87,z),V(-.067,1.212,z+.008),.009,cast,'Stiffening rib');
      for (const y of [.900,1.194]) disc(root,V(-.079,y,z),.015,.018,cast,'Mounting boss');
    }
  }
  function headMount(root) {
    dish(root,V(-.047,.051,-.208),.112,.134,cast,'Cranial recess');
    for(const z of [-.307,-.111]) washer(root,V(-.064,.046,z),.008,brass);
  }
  for (const era of Object.keys(movements)) {
    const chest = group(regions.get('body'), era + ' thoracic compartment');
    const head = group(regions.get('head'), era + ' cranial compartment');
    // The service openings swing on the anatomical left. Seat both mechanisms
    // behind the central bulkhead so their fasteners and working faces clear
    // the complete sweep of the original cover, including its hinge-side lip.
    chest.position.x = .188;
    head.position.x = .128;
    mechanisms[era] = [chest,head];
    chest.visible=head.visible=false;
    chestMount(chest);
    headMount(head);
    if (era === 'maker') {
      for (const z of [-.13,.08]) {
        box(chest,V(-.080,1.042,z),[.035,.37,.035],oak,'Oak bearer');
        for (const y of [.90,1.19]) disc(chest,V(-.105,y,z),.016,.014,brass,'Brass washer');
      }
      const wheel = hub(chest,1.025,-.081,.118,0,brass);
      movements.maker.push([wheel,.34]);
      const fulcrum = group(chest,'Hand lever and return rod');
      fulcrum.position.set(-.174,.913,.085);
      rod(fulcrum,V(0,-.04,-.03),V(0,.26,.08),.012,oak,'Hand lever');
      rod(fulcrum,V(0,.16,.049),V(0,.21,-.105),.009,brass,'Clevis link');
      disc(fulcrum,V(-.003,0,0),.022,.017,brass,'Pivot washer');
      movements.maker.push([fulcrum,-.16]);
      for (const y of [.012,.077]) {
        rod(head,V(-.067,y,-.28),V(-.09,y+.024,-.131),.009,brass,'Manual steering rod');
        disc(head,V(-.097,y+.024,-.131),.014,.012,edge,'Linkage pin');
      }
    } else if (era === 'mechanic') {
      for (const [y,z,r,teeth,speed] of [[.987,-.092,.101,24,1],[1.113,.003,.067,16,-1.5],[1.035,.092,.055,14,1.71]]) {
        const wheel = hub(chest,y,z,r,teeth,teeth===16 ? brass : edge);
        movements.mechanic.push([wheel,speed]);
      }
      for (const z of [-.16,.128]) {
        const bracket=box(chest,V(-.084,1.065,z),[.032,.34,.035],cast,'Cast bridge');
        bracket.rotation.x=z<0 ? -.12 : .12;
      }
      for(const [y,z] of [[1.2,-.063],[.883,.065]]) {
        const p=box(chest,V(-.128,y,z),[.028,.040,.095],cast,'Arbor bridge');
        p.rotation.x=.17;washer(chest,V(-.147,y,z),.012,brass);
      }
      const recoil=group(head,'Cranial escapement arbor');
      recoil.position.set(-.085,.05,-.214);
      ring(recoil,V(0,0,0),.055,.006,edge,'Regulator hoop');
      rod(recoil,V(0,-.065,0),V(0,.065,0),.007,brass,'Pallet arm');
      disc(recoil,V(-.008,0,0),.014,.019,brass,'Pallet bearing');
      movements.mechanic.push([recoil,2.7]);
    } else {
      const center=V(-.102,1.05,-.019);
      disc(chest,center,.138,.085,dark,'Insulated energy vessel');
      const lens=piece(chest,new THREE.SphereGeometry(.104,40,20),amber,
        V(-.144,1.05,-.019),'Domed amber energy lens');
      lens.scale.x=.32;
      for(const [x,r,m] of [[-.143,.137,cast],[-.152,.121,copper],[-.156,.112,brass]]) {
        ring(chest,V(x,1.05,-.019),r,.007,m,'Reservoir bezel');
      }
      for(let i=0;i<6;i++){
        const a=i*Math.PI/3+.15;
        washer(chest,V(-.156,1.05+.132*Math.cos(a),-.019+.132*Math.sin(a)),.008,edge);
      }
      for (const y of [.972,1.052,1.128]) {
        const dz=Math.sqrt(.10**2-(y-1.05)**2);
        rod(chest,V(-.175,y,-.019-dz),V(-.175,y,-.019+dz),.004,cast,'Protective lens grille');
      }
      for(const z of [-.162,.13]) {
        rod(chest,V(-.106,.912,z),V(-.106,1.176,z),.018,porcelain,'Insulated bus');
        rod(chest,V(-.107,1.185,z),V(-.094,1.235,z*.53),.01,copper,'Formed return line');
      }
      for(let i=0;i<3;i++) {
        const y=-.007+i*.051;
        box(head,V(-.078,y,-.205),[.035,.025,.157],dark,'Signal ceramic blade');
        box(head,V(-.099,y,-.204),[.01,.008,.092],opal,'Signal light pipe');
        for(let n=0;n<7;n++){
          box(head,V(-.088,y+.012,-.26+n*.018),[.036,.006,.007],edge,'Cooling fin');
        }
        for (const z of [-.274,-.136]) disc(head,V(-.102,y,z),.008,.008,brass,'Blade terminal');
      }
    }
  }

  function isPanel(region,x,y,z) {
    if (region==='head') {
      return x<-.027 && ((y-.053)/.153)**2 + ((z+.213)/.166)**2 < 1;
    }
    return x<-.039 && ((y-1.045)/.323)**2 + ((z+.018)/.322)**2 < 1;
  }
  // Position attributes in these five GLB regions are in their native batch frames.
  // Keep each original vertex buffer, normal, UV, tangent and material intact.
  function subset(source, indices) {
    const geom = new THREE.BufferGeometry();
    for (const [name, attribute] of Object.entries(source.attributes)) geom.setAttribute(name,attribute);
    geom.setIndex(indices);
    geom.boundingSphere=source.boundingSphere;
    geom.boundingBox=source.boundingBox;
    ownedGeometries.add(geom);
    return geom;
  }
  const panels=[];
  for (const region of ['torso','body','wing','head']) {
    const batch=regions.get(region);
    const leaves=[];
    batch.traverse(object=>{if(object.isMesh && !object.userData.fc_inspection) leaves.push(object);});
    for(const original of leaves) {
      const geometry=original.geometry,position=geometry.getAttribute('position'),idx=geometry.getIndex();
      const length=idx ? idx.count : position.count;
      const keep=[],move=[];
      for(let i=0;i<length;i+=3) {
        const a=idx?idx.getX(i):i,b=idx?idx.getX(i+1):i+1,c=idx?idx.getX(i+2):i+2;
        const x=(position.getX(a)+position.getX(b)+position.getX(c))/3;
        const y=(position.getY(a)+position.getY(b)+position.getY(c))/3;
        const z=(position.getZ(a)+position.getZ(b)+position.getZ(c))/3;
        (isPanel(region,x,y,z)?move:keep).push(a,b,c);
      }
      if(!move.length) continue;
      const moving=add(original,new THREE.Mesh(subset(geometry,move),original.material),'Original '+region+' access panel');
      moving.castShadow=original.castShadow;
      moving.receiveShadow=original.receiveShadow;
      moving.visible=false;
      const p=region==='head'?V(-.072,.167,-.21):V(-.135,1.044,-.268);
      panels.push({original,geometry,remainder:subset(geometry,keep),moving,p,head:region==='head'});
    }
  }
  const wing=regions.get('wing.l');
  const rest={position:wing.position.clone(),quaternion:wing.quaternion.clone()};
  const hinge=V(-.238,1.317,.039); // expressed in the authored wing mesh space
  const orientationWing=new THREE.Quaternion();
  function placeMoving(mesh,pivot,axis,angle) {
    mesh.quaternion.setFromAxisAngle(axis,angle);
    mesh.position.copy(pivot).sub(offset.copy(pivot).applyQuaternion(mesh.quaternion));
  }
  const regional=installRegionalParts(THREE,regions);
  function setOpen(value) {
    if(!Number.isFinite(value)) throw new TypeError('Inspection opening must be finite');
    const previouslyOpen=openness>0;
    openness=Math.max(0,Math.min(1,value));
    if(!previouslyOpen&&!openness)return;
    const enabled=openness>0;
    const headSelected=['all','service','head'].includes(selected);
    const chestSelected=['all','service','breast'].includes(selected);
    const wingSelected=chestSelected||selected==='left-wing';
    regional.apply(selected,ease(openness));
    const wingAngle=-2.31*ease(openness/.89);
    orientationWing.setFromAxisAngle(Z,wingAngle);
    if(wingSelected) {
      wing.quaternion.copy(rest.quaternion).multiply(orientationWing);
      wing.position.copy(rest.position);
    }
    if(enabled && wingSelected) {
      offset.copy(hinge).applyQuaternion(orientationWing).negate().add(hinge);
      offset.applyQuaternion(rest.quaternion);
      wing.position.add(offset);
    }
    for(const {original,geometry,remainder,moving,p,head} of panels) {
      if(head ? !headSelected : !chestSelected)continue;
      original.geometry=enabled?remainder:geometry;
      moving.visible=enabled;
      moving.material=original.material;
      placeMoving(moving,p,head?Z:Y,(head?-2.05:-2.31)*ease((openness-(head?.12:.09))/.88));
    }
    for(const [name,parts] of Object.entries(mechanisms)) {
      parts[0].visible=enabled&&activeEra===name&&chestSelected;
      parts[1].visible=enabled&&activeEra===name&&headSelected;
    }
  }
  function setRegion(id){
    if(!Object.hasOwn(regionOptions,id))throw Error('Unknown inspection region '+id);
    if(id===selected)return;
    const t=openness;setOpen(0);selected=id;setOpen(t);
  }
  function snapshot(){
    return {region:selected,era:activeEra,fraction:openness,selection:regional.proof(selected),
     panels:panels.filter(({moving})=>moving.visible).length,
     compartments:(mechanisms[activeEra]||[]).filter(p=>p.visible).map(p=>p.name)};
  }
  function setEra(name) {
    const key=String(name).toLowerCase();
    if(!mechanisms[key]) throw new Error('Unknown inspection era '+name);
    setRegion('all');
    activeEra=key;
    setOpen(openness);
    setMotion(phase);
  }
  function setMotion(value) {
    if(!Number.isFinite(value)) return;
    phase=Math.max(0,Math.min(1,value));
    for(const [object,amount] of movements[activeEra]) {
      const displacement=activeEra==='maker' ? phase*amount : phase*amount*Math.PI*2;
      object.quaternion.setFromAxisAngle(X,displacement);
    }
  }
  function dispose() {
    setOpen(0);
    regional.dispose();
    for(const object of generated.slice().reverse()) object.removeFromParent();
    // Subsets share GLB vertex buffers. The original owns those attributes.
    for(const geometry of ownedGeometries) {
      if (panels.some(p=>p.remainder===geometry || p.moving.geometry===geometry)) {
        for(const name of Object.keys(geometry.attributes)) geometry.deleteAttribute(name);
      }
      geometry.dispose();
    }
    for(const material of ownedMaterials) material.dispose();
    for(const texture of bumpTextures) texture.dispose();
  }
  setOpen(0);
  return {setEra,setOpen,setMotion,setRegion,getRegion:()=>selected,snapshot,dispose};
}
