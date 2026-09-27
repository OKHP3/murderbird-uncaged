import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const modelUrl = new URL('../../assets/models/uncaged-mass-study/murderbird-mass-study.glb', import.meta.url).href;
const FRONT = 1.10;
const smooth = t => t * t * (3 - 2 * t);
const clamp = THREE.MathUtils.clamp;

export async function createExhibit(container, updateMarker, { onReach, onContextLost } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.25;
  const gl=renderer.getContext();
  const info=gl.getExtension('WEBGL_debug_renderer_info');
  const softwareRenderer=info&&/swiftshader|llvmpipe|software/i.test(gl.getParameter(info.UNMASKED_RENDERER_WEBGL));
  renderer.shadowMap.enabled = !softwareRenderer;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'MurderBird 3D enclosure. Arrow keys orbit; plus and minus zoom. Use Reach toward bars for a reaction.');
  container.append(canvas);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#232b29');
  scene.fog = new THREE.Fog('#232b29', 5, 13);
  const camera = new THREE.PerspectiveCamera(36, 1, .05, 35);
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false;
  controls.enableDamping = false;
  controls.minDistance = 2.7;
  controls.maxDistance = 6.5;
  controls.minPolarAngle = .25;
  controls.maxPolarAngle = Math.PI / 2 - .03;
  controls.target.set(0, 1.03, 0);
  camera.position.set(-2.85, 1.85, 3.55);
  controls.update();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, .04);
  scene.environment = environment.texture;
  scene.environmentIntensity = .48;
  room.dispose(); pmrem.dispose();
  scene.add(new THREE.HemisphereLight(0xddeee8, 0x3b3327, 1.7));
  const key = new THREE.DirectionalLight(0xffe0b8, 4);
  key.position.set(-2.5, 4.5, 4); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  Object.assign(key.shadow.camera, { left: -2, right: 2, top: 3, bottom: -2, near: .1, far: 12 });
  key.shadow.bias = -.0004; key.shadow.normalBias = .012;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xb1dcd4, 2.4);
  fill.position.set(3, 2.5, -2); scene.add(fill);

  const metal = new THREE.MeshStandardMaterial({ color: '#404b45', roughness: .62, metalness: .65 });
  const brass = new THREE.MeshStandardMaterial({ color: '#998260', roughness: .5, metalness: .7 });
  const floorMat = new THREE.MeshStandardMaterial({ color: '#323a36', roughness: .87, metalness: .15 });
  const mesh = (geometry, material, position) => {
    const o = new THREE.Mesh(geometry, material); o.position.set(...position);
    o.castShadow = true; o.receiveShadow = true; scene.add(o); return o;
  };
  mesh(new THREE.BoxGeometry(2.25, .10, 2.32), metal, [0, -.065, .06]);
  mesh(new THREE.BoxGeometry(2.12, .012, 2.22), floorMat, [0, -.009, .06]);
  const ground = mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({color:'#111916',roughness:.95}), [0, -.12, 0]);
  ground.rotation.x = -Math.PI / 2;
  if(softwareRenderer){
    for(const side of [-1,1])for(let layer=0;layer<4;layer++){
      const shadow=mesh(new THREE.CircleGeometry(1,32),new THREE.MeshBasicMaterial({color:'#0a130d',transparent:true,opacity:.085,depthWrite:false}),[side*.275,.0001+layer*.0001,.16]);
      shadow.rotation.x=-Math.PI/2;shadow.scale.set(.16-layer*.025,.25-layer*.035,1);
    }
  }
  const cage = new THREE.Group(); scene.add(cage);
  const bars = [];
  function bar(a, b, radius, permanent = false) {
    const start = new THREE.Vector3(...a), end = new THREE.Vector3(...b);
    const mat = metal.clone(); mat.transparent = true; mat.opacity = .66; mat.depthWrite = false;
    const o = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, start.distanceTo(end), 8), mat);
    o.position.copy(start).add(end).multiplyScalar(.5);
    o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), end.sub(start).normalize());
    o.userData.permanent = permanent; cage.add(o); bars.push(o); return o;
  }
  for (const z of [FRONT, -.95]) {
    for (let i = -3; i <= 3; i++) bar([i / 3, 0, z], [i / 3, 2.15, z], Math.abs(i) === 3 ? .018 : .011);
    bar([-1, 2.15, z], [1, 2.15, z], .021);
    bar([-1, .07, z], [1, .07, z], .018, true);
  }
  for (const x of [-1, 1]) {
    for (let i = 1; i < 5; i++) bar([x,0,-.95+i*.342],[x,2.15,-.95+i*.342],.011);
    bar([x,2.15,-.95],[x,2.15,FRONT],.021);
    bar([x,.07,-.95],[x,.07,FRONT],.018,true);
  }
  const contactRail = bar([0,1.25,FRONT],[0,1.95,FRONT],.021);
  const target = mesh(new THREE.TorusGeometry(.045,.006,8,32), brass, [0,1.54,FRONT+.005]);
  target.visible = false;
  const guides = new THREE.Group(); scene.add(guides);
  const guideMat = new THREE.LineDashedMaterial({ color: '#dfc899', transparent:true, opacity:.52, dashSize:.025, gapSize:.025 });
  let gltf;
  const abort = new AbortController();
  const timeout = setTimeout(() => abort.abort(), 25000);
  try {
    const response = await fetch(modelUrl, { signal: abort.signal });
    if (!response.ok) throw new Error(`Model request failed (${response.status})`);
    const data = await response.arrayBuffer();
    gltf = await new GLTFLoader().parseAsync(data, '');
  } catch (error) {
    clearTimeout(timeout); controls.dispose(); environment.dispose(); renderer.dispose(); canvas.remove();
    throw error;
  }
  clearTimeout(timeout);
  const model = gltf.scene; scene.add(model);
  const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle'];
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  if (names.some(name => !nodes[name])) {
    controls.dispose(); environment.dispose(); renderer.dispose(); canvas.remove();
    throw new Error('Model assembly contract is incomplete.');
  }
  const rest = Object.fromEntries(names.map(name => [name, { position:nodes[name].position.clone(), rotation:nodes[name].rotation.clone() }]));
  const materialOrigins = new Map();
  model.traverse(o => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; const mats = Array.isArray(o.material) ? o.material : [o.material]; mats.forEach(m=>{ if (!materialOrigins.has(m)) materialOrigins.set(m, { color:m.color.clone(), roughness:m.roughness,vertexColors:m.vertexColors }); }); } });
  const markerNodes = {
    beak: ['head', [0,-.035,.28]], joint:['body',[.28,.6,.07]],
    shell:['breastplate',[.245,-.19,.01]], drive:['winding-drive',[.13,0,0]],
    power:['power-core',[0,0,.055]], mind:['processing',[0,.04,0]],
  };
  const anchors = Object.fromEntries(Object.entries(markerNodes).map(([id,[name,p]])=>{const landmark=model.getObjectByName('anchor-'+id);if(landmark)return [id,landmark];const o=new THREE.Object3D();o.position.set(...p);nodes[name].add(o);return [id,o];}));
  const billTip = model.getObjectByName('bill-contact');
  if(!billTip)throw new Error('Model contact landmark is missing.');
  const exploded = {
    breastplate:[-.70,-.12,.18], 'left-mantle':[.39,.09,0], 'right-mantle':[-.39,.09,0],
    'winding-drive':[-.45,-.10,.22], 'power-core':[.32,-.05,.28], processing:[.28,.20,0], 'cranial-cover':[0,.14,0],
  };
  const lines = {};
  Object.keys(exploded).forEach(name => { const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),guideMat);guides.add(line);lines[name]=line; });
  let open = 0, separation = 0, targetOpen = 0, targetSeparation = 0, armed = false, era = 'builder', pointer, frameCount=0;
  let selected = 'beak';
  let lastSnapshot, lastWidth=0, lastHeight=0;
  const vector = new THREE.Vector3();
  const worldTip = new THREE.Vector3();
  const contactBounds = new THREE.Box3();
  const frameTimes = [];
  const highlight = new THREE.Box3Helper(new THREE.Box3(),0xd9b87b); highlight.visible=false;scene.add(highlight);

  function setEra(value) {
    era=value;
    nodes['winding-drive'].visible=value==='mechanic';
    nodes['power-core'].visible=value==='builder';
    nodes.processing.visible=value==='builder';
    nodes['builder-optics'].visible=value==='builder';
    nodes['industrial-repairs'].visible=value!=='maker';
    materialOrigins.forEach((original,m) => {
      m.color.copy(original.color);m.roughness=original.roughness;m.vertexColors=original.vertexColors;
      if(value==='maker' && (m.name.includes('mineral')||m.name.includes('Industrial iron'))){m.color.set('#826241');m.roughness=.57;m.vertexColors=false;}
      m.needsUpdate=true;
    });
  }
  function resize() {
    const width=container.clientWidth,height=container.clientHeight;
    if(!width||!height||width===lastWidth&&height===lastHeight)return;
    lastWidth=width;lastHeight=height;renderer.setSize(width,height);camera.aspect=width/height;
    camera.fov=width<550?47:36;camera.updateProjectionMatrix();
  }
  function reset(){controls.target.set(0,1.03,0);camera.position.set(-2.85,1.85,3.55);controls.update();}
  function nudge(action){
    const offset=camera.position.clone().sub(controls.target);const s=new THREE.Spherical().setFromVector3(offset);
    if(action==='left')s.theta-=.23;if(action==='right')s.theta+=.23;
    if(action==='up')s.phi-=.14;if(action==='down')s.phi+=.14;
    if(action==='in')s.radius*=.9;if(action==='out')s.radius*=1.1;
    s.radius=clamp(s.radius,controls.minDistance,controls.maxDistance);s.phi=clamp(s.phi,controls.minPolarAngle,controls.maxPolarAngle);
    camera.position.copy(controls.target).add(new THREE.Vector3().setFromSpherical(s));controls.update();
  }
  const listeners = new AbortController();
  const listen=(type,fn,options={})=>canvas.addEventListener(type,fn,{...options,signal:listeners.signal});
  listen('keydown',e=>{ const actions={ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down','+':'in','=':'in','-':'out',Home:'reset'};if(actions[e.key]){e.preventDefault();actions[e.key]==='reset'?reset():nudge(actions[e.key]);}});
  listen('pointerdown',e=>{if(!armed||e.button>0)return;if(pointer){pointer=null;return;}pointer={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});
  listen('pointerup',e=>{
    if(!pointer||pointer.id!==e.pointerId)return;const saved=pointer;pointer=null;
    if(Math.hypot(e.clientX-saved.x,e.clientY-saved.y)>10)return;
    const rect=canvas.getBoundingClientRect();onReach?.({x:(e.clientX-rect.left)/rect.width*2-1,y:1-(e.clientY-rect.top)/rect.height*2});
  });
  listen('pointercancel',()=>{pointer=null;});listen('lostpointercapture',()=>{pointer=null;});
  listen('webglcontextlost',e=>{e.preventDefault();onContextLost?.();});

  function tick(dt,snapshot,frameDelta=dt) {
    lastSnapshot=snapshot; frameCount++;
    if(frameDelta>0&&frameDelta<5){frameTimes.push(frameDelta);if(frameTimes.length>180)frameTimes.shift();}
    const ease=snapshot.reducedMotion?1:1-Math.exp(-dt*8);
    open=THREE.MathUtils.lerp(open,targetOpen,ease);separation=THREE.MathUtils.lerp(separation,targetSeparation,ease);
    if(Math.abs(open-targetOpen)<.001)open=targetOpen;
    if(Math.abs(separation-targetSeparation)<.001)separation=targetSeparation;
    names.forEach(name=>{nodes[name].position.copy(rest[name].position);nodes[name].rotation.copy(rest[name].rotation);});
    nodes.breastplate.rotation.y=-open*1.35;
    nodes['cranial-cover'].position.y+=open*.08;
    Object.entries(exploded).forEach(([name,offset])=>nodes[name].position.addScaledVector(vector.set(...offset),separation));
    const p=smooth(snapshot.phase),state=snapshot.state;
    let extension=0,anticipation=0,beak=0;
    if(!snapshot.reducedMotion&&!snapshot.inspection&&!snapshot.paused){
      if(state==='notice')anticipation=p*.20;
      if(state==='warning'){anticipation=.20+p*.80;beak=p;}
      if(state==='strike'){extension=p;anticipation=1-p;beak=1-p*.8;}
      if(state==='contact'){extension=1;beak=.2*(1-p);}
      if(state==='recover'){extension=1-p;beak=0;}
      nodes.neck.rotation.x=-anticipation*.075+extension*.26;
      nodes.head.rotation.y=snapshot.reach.x*.16*(1-extension);
      nodes.jaw.rotation.x=-beak*.32;
      // The leading modeled surface meets the bar, including the broad curved bill.
      // A tip-only constraint can let the upper hook pass through the rail.
      // The bounded cervical slide remains an illustrative rigid mechanism.
      if(extension>0){
        model.updateMatrixWorld(true);
        contactBounds.setFromObject(nodes.head,true);
        const travel=clamp((FRONT-contactBounds.max.z-.021)/nodes.neck.parent.getWorldScale(vector).z,-.10,.20);
        nodes.neck.position.z+=travel*extension;
      }
    }
    model.updateMatrixWorld(true);
    billTip.getWorldPosition(worldTip);
    target.visible=armed||['notice','warning','strike','contact','recover'].includes(state);
    target.position.x=worldTip.x;
    target.position.y=worldTip.y;
    const viewDirection=camera.position.clone().sub(controls.target).normalize();
    bars.forEach(o=>{
      const near=o.position.x*viewDirection.x+o.position.z*viewDirection.z>0;
      o.material.opacity=open>.02?.035:near?.12:.48;
      if(o===contactRail)o.material.opacity=open>.02?.02:state==='contact'?.85:.29;
    });
    guides.visible=separation>.015;
    Object.entries(lines).forEach(([name,line])=>{
      line.visible=nodes[name].visible;
      const a=nodes[name].parent.localToWorld(rest[name].position.clone());
      const b=nodes[name].getWorldPosition(new THREE.Vector3());
      line.geometry.setFromPoints([a,b]);line.computeLineDistances();
    });
    Object.entries(anchors).forEach(([id,anchor])=>{
      anchor.getWorldPosition(vector);vector.project(camera);
      const present=id==='drive'?era==='mechanic':id==='power'||id==='mind'?era==='builder':true;
      const interior=['drive','power','mind'].includes(id);
      updateMarker(id,(vector.x+1)*lastWidth/2,(1-vector.y)*lastHeight/2,present&&(!interior||open>.8)&&vector.z<1&&Math.abs(vector.x)<.94&&Math.abs(vector.y)<.86);
    });
    if(highlight.visible){const name=markerNodes[selected]?.[0];if(name&&nodes[name].visible)highlight.box.setFromObject(nodes[name]);else highlight.visible=false;}
    renderer.render(scene,camera);
  }
  setEra(era);resize();
  return {
    kind:'webgl', resize, tick, reset, nudge, setEra,
    select(id){selected=id;highlight.visible=targetOpen>0;},
    setSection(value){targetOpen=value?1:0;if(!value)targetSeparation=0;highlight.visible=false;},
    setSeparation(value){targetSeparation=targetOpen?clamp(Number(value)||0,0,1):0;},
    setArmed(value){armed=value;controls.enabled=!value;canvas.style.cursor=value?'crosshair':'grab';pointer=null;},
    isAssembled(){return open===0&&separation===0;},
    focus(id){const anchor=anchors[id];if(!anchor||!nodes[markerNodes[id]?.[0]]?.visible)return;anchor.getWorldPosition(vector);const delta=vector.clone().sub(controls.target);controls.target.copy(vector);camera.position.add(delta);controls.update();},
    metrics(){return {kind:'webgl',softwareRenderer:Boolean(softwareRenderer),era,open,separation,frameCount,meanFps:frameTimes.length/frameTimes.reduce((a,b)=>a+b,0),triangles:renderer.info.render.triangles,drawCalls:renderer.info.render.calls,geometries:renderer.info.memory.geometries,textures:renderer.info.memory.textures,tip:worldTip.toArray(),headFront:contactBounds.setFromObject(nodes.head,true).max.z,contactPlane:FRONT,camera:camera.position.toArray(),target:controls.target.toArray(),state:lastSnapshot?.state,nodes:Object.fromEntries(['winding-drive','power-core','processing','builder-optics'].map(n=>[n,nodes[n].visible]))};},
    destroy(){listeners.abort();controls.dispose();environment.dispose();scene.traverse(o=>{o.geometry?.dispose();if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.dispose());}});renderer.dispose();canvas.remove();},
  };
}
