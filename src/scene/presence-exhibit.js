import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { createEraMotion } from './era-motion.js';
import { createEraMechanisms } from './era-mechanisms.js';
import { applyInspectionPose, INSPECTION_EXPLODED_OFFSETS } from './inspection-pose.js';
import { layoutMarkers } from './marker-layout.js';
import { applyEraFinishes } from './era-finish.js';

// Development studies are served from the source tree without emitting them
// into the production build. Production continues to use the selected V37.
const reviewModels = import.meta.env.DEV ? {
  'curved-neck01': '/assets/models/whole-character-v38/curved-neck01/murderbird-v38-curved-neck01-rigid.glb',
  'curved-neck01-strap02': '/assets/models/whole-character-v38/curved-neck01/murderbird-v38-curved-neck01-strap02-rigid.glb',
  'neck-interface01': '/assets/models/whole-character-v38/neck-interface01/murderbird-v38-neck-interface01-rigid.glb',
  'neck-interface01-supported02': '/assets/models/whole-character-v38/neck-interface01/murderbird-v38-neck-interface01-supported02-rigid.glb',
  'neck-continuity01-swept02': '/assets/models/whole-character-v38/neck-continuity01/murderbird-v38-neck-continuity01-swept02-rigid.glb',
  'neck-continuity01': '/assets/models/whole-character-v38/neck-continuity01/murderbird-v38-neck-continuity01-rigid.glb',
  'breast-support02-seam01': '/assets/models/whole-character-v38/breast-support02/murderbird-v38-breast-support02-seam01-rigid.glb',
  'breast-support02': '/assets/models/whole-character-v38/breast-support02/murderbird-v38-breast-support02-rigid.glb',
  'breast-support01': '/assets/models/whole-character-v38/breast-support01/murderbird-v38-breast-support01-rigid.glb',
  'breast-envelope02': '/assets/models/whole-character-v38/breast-envelope02/murderbird-v38-breast-envelope02-rigid.glb',
  'breast-envelope01': '/assets/models/whole-character-v38/breast-envelope01/murderbird-v38-breast-envelope01-rigid.glb',
  'lower-support02': '/assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02-rigid.glb',
  'lower-support01': '/assets/models/whole-character-v38/lower-support01/murderbird-v38-lower-support01-rigid.glb',
  'lower-body02': '/assets/models/whole-character-v38/lower-body02/murderbird-v38-lower-body02-rigid.glb',
  'lower-body01': '/assets/models/whole-character-v38/lower-body01/murderbird-v38-lower-body01-rigid.glb',
  'upper-contour02': '/assets/models/whole-character-v38/upper-contour02/murderbird-v38-upper-contour02-rigid.glb',
  'upper-contour01': '/assets/models/whole-character-v38/upper-contour01/murderbird-v38-upper-contour01-rigid.glb',
  'throat-seated02': '/assets/models/whole-character-v38/throat-seated02/murderbird-v38-throat-seated02-rigid.glb',
  'throat-seated01': '/assets/models/whole-character-v38/throat-seated01/murderbird-v38-throat-seated01-rigid.glb',
  'throat-construction02': '/assets/models/whole-character-v38/throat-construction02/murderbird-v38-throat-construction02-rigid.glb',
  'throat-construction01': '/assets/models/whole-character-v38/throat-construction01/murderbird-v38-throat-construction01-rigid.glb',
  'cervical-guards02': '/assets/models/whole-character-v38/cervical-guards02/murderbird-v38-cervical-guards02-rigid.glb',
  'cervical-guards01': '/assets/models/whole-character-v38/cervical-guards01/murderbird-v38-cervical-guards01-rigid.glb',
  'bill-relationship02': '/assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02-rigid.glb',
  'bill-relationship01': '/assets/models/whole-character-v38/bill-relationship01/murderbird-v38-bill-relationship01-rigid.glb',
  'occipital-envelope01': '/assets/models/whole-character-v38/occipital-envelope01/murderbird-v38-occipital-envelope01-rigid.glb',
  'occipital-envelope02': '/assets/models/whole-character-v38/occipital-envelope02/murderbird-v38-occipital-envelope02-rigid.glb',
  'orbital-clearance02': '/assets/models/whole-character-v38/orbital-clearance02/murderbird-v38-orbital-clearance02-rigid.glb',
  'orbital-clearance01': '/assets/models/whole-character-v38/orbital-clearance01/murderbird-v38-orbital-clearance01-rigid.glb',
  'head-fit02': '/assets/models/whole-character-v38/head-fit02/murderbird-v38-head-fit02-rigid.glb',
  'head-fit01': '/assets/models/whole-character-v38/head-fit01/murderbird-v38-head-fit01-rigid.glb',
  'cheek-nape02': '/assets/models/whole-character-v38/cheek-nape02/murderbird-v38-cheek-nape02-rigid.glb',
  'cheek-nape01': '/assets/models/whole-character-v38/cheek-nape01/murderbird-v38-cheek-nape01-rigid.glb',
  'swept-cranium02': '/assets/models/whole-character-v38/swept-cranium02/murderbird-v38-swept-cranium02-rigid.glb',
  'swept-cranium01': '/assets/models/whole-character-v38/swept-cranium01/murderbird-v38-swept-cranium01-rigid.glb',
  'cranial-volume02': '/assets/models/whole-character-v38/cranial-volume02/murderbird-v38-cranial-volume02-rigid.glb',
  'cranial-volume01': '/assets/models/whole-character-v38/cranial-volume01/murderbird-v38-cranial-volume01-rigid.glb',
  'cranial-transition02': '/assets/models/whole-character-v38/cranial-transition02/murderbird-v38-cranial-transition02-rigid.glb',
  'cranial-transition01': '/assets/models/whole-character-v38/cranial-transition01/murderbird-v38-cranial-transition01-rigid.glb',
  'cheek-layout02': '/assets/models/whole-character-v38/cheek-layout02/murderbird-v38-cheek-layout02-rigid.glb',
  'cheek-layout01': '/assets/models/whole-character-v38/cheek-layout01/murderbird-v38-cheek-layout01-rigid.glb',
  'temple-layering02': '/assets/models/whole-character-v38/temple-layering02/murderbird-v38-temple-layering02-rigid.glb',
  'temple-layering01': '/assets/models/whole-character-v38/temple-layering01/murderbird-v38-temple-layering01-rigid.glb',
  'cheek-interface01': '/assets/models/whole-character-v38/cheek-interface01/murderbird-v38-cheek-interface01-rigid.glb',
  'cheek-supported02': '/assets/models/whole-character-v38/cheek-supported02/murderbird-v38-cheek-supported02-rigid.glb',
  'cheek-supported01': '/assets/models/whole-character-v38/cheek-supported01/murderbird-v38-cheek-supported01-rigid.glb',
  'temporal-construction02': '/assets/models/whole-character-v38/temporal-construction02/murderbird-v38-temporal-construction02-rigid.glb',
  'temporal-construction01': '/assets/models/whole-character-v38/temporal-construction01/murderbird-v38-temporal-construction01-rigid.glb',
  'jaw-fit02': '/assets/models/whole-character-v38/jaw-fit02/murderbird-v38-jaw-fit02-rigid.glb',
  'jaw-fit01': '/assets/models/whole-character-v38/jaw-fit01/murderbird-v38-jaw-fit01-rigid.glb',
  'bill-shell02': '/assets/models/whole-character-v38/bill-shell02/murderbird-v38-bill-shell02-rigid.glb',
  'bill-shell01': '/assets/models/whole-character-v38/bill-shell01/murderbird-v38-bill-shell01-rigid.glb',
  'bill-envelope02': '/assets/models/whole-character-v38/bill-envelope02/murderbird-v38-bill-envelope02-rigid.glb',
  'bill-envelope01': '/assets/models/whole-character-v38/bill-envelope01/murderbird-v38-bill-envelope01-rigid.glb',
  'bill-construction01': '/assets/models/whole-character-v38/bill-construction01/murderbird-v38-bill-construction01-rigid.glb',
  'bill-construction02': '/assets/models/whole-character-v38/bill-construction02/murderbird-v38-bill-construction02-rigid.glb',
  'cheek-assembly02': '/assets/models/whole-character-v38/cheek-assembly02/murderbird-v38-cheek-assembly02-rigid.glb',
  'orbital-frame02': '/assets/models/whole-character-v38/orbital-frame02/murderbird-v38-orbital-frame02-rigid.glb',
  'head-readability02': '/assets/models/whole-character-v38/head-readability02/murderbird-v38-head-readability02-rigid.glb',
  'head-readability01': '/assets/models/whole-character-v38/head-readability01/murderbird-v38-head-readability01-rigid.glb',
  'breast-course01': '/assets/models/whole-character-v38/breast-course01/murderbird-v38-breast-course01-rigid.glb',
  'breast-course02': '/assets/models/whole-character-v38/breast-course02/murderbird-v38-breast-course02-rigid.glb',
  'pectoral-construction01': '/assets/models/whole-character-v38/pectoral-construction01/murderbird-v38-pectoral-construction01-rigid.glb',
  'pectoral-connected01': '/assets/models/whole-character-v38/pectoral-connected01/murderbird-v38-pectoral-connected01-rigid.glb',
  'pectoral-interfaces01': '/assets/models/whole-character-v38/pectoral-interfaces01/murderbird-v38-pectoral-interfaces01-rigid.glb',
  'pectoral-interfaces02': '/assets/models/whole-character-v38/pectoral-interfaces02/murderbird-v38-pectoral-interfaces02-rigid.glb',
  'pectoral-envelope02': '/assets/models/whole-character-v38/pectoral-envelope02/murderbird-v38-pectoral-envelope02-rigid.glb',
  'pectoral-envelope01': '/assets/models/whole-character-v38/pectoral-envelope01/murderbird-v38-pectoral-envelope01-rigid.glb',
  'compact-mantle02': '/assets/models/whole-character-v38/compact-mantle02/murderbird-v38-compact-mantle02-rigid.glb',
  'compact-mantle01': '/assets/models/whole-character-v38/compact-mantle01/murderbird-v38-compact-mantle01-rigid.glb',
  'cheek-seated03': '/assets/models/whole-character-v38/cheek-seated03/murderbird-v38-cheek-seated03-rigid.glb',
  'cheek-seated02': '/assets/models/whole-character-v38/cheek-seated02/murderbird-v38-cheek-seated02-rigid.glb',
  'cheek-seated01': '/assets/models/whole-character-v38/cheek-seated01/murderbird-v38-cheek-seated01-rigid.glb',
  'cheek-envelope01': '/assets/models/whole-character-v38/cheek-envelope01/murderbird-v38-cheek-envelope01-rigid.glb',
  'mechanical-finish01': '/assets/models/whole-character-v37/finish-study01/murderbird-v37-mechanical-finish-study01.glb',
  'contrast-study01': '/assets/models/whole-character-v38/contrast-study01/murderbird-v38-material-contrast-study01.glb',
  'body-finish01': '/assets/models/whole-character-v38/body-finish01/murderbird-v38-material-body-finish01.glb',
  'shoulder-study01': '/assets/models/whole-character-v38/shoulder-study01/murderbird-v38-shoulder-study01-rigid.glb',
  'shoulder-study02': '/assets/models/whole-character-v38/shoulder-study02/murderbird-v38-shoulder-study02-rigid.glb',
  'head-study01': '/assets/models/whole-character-v38/head-study01/murderbird-v38-head-study01-rigid.glb',
  'crown-study01': '/assets/models/whole-character-v38/crown-study01/murderbird-v38-crown-study01-rigid.glb',
  'crown-study02': '/assets/models/whole-character-v38/crown-study02/murderbird-v38-crown-study02-rigid.glb',
  'crown-fit01': '/assets/models/whole-character-v38/crown-fit01/murderbird-v38-crown-fit01-rigid.glb',
  'crown-fit02': '/assets/models/whole-character-v38/crown-fit02/murderbird-v38-crown-fit02-rigid.glb',
  'neck-study01': '/assets/models/whole-character-v38/neck-study01/murderbird-v38-neck-study01-rigid.glb',
  'neck-study02': '/assets/models/whole-character-v38/neck-study02/murderbird-v38-neck-study02-rigid.glb',
  'neck-clearance01': '/assets/models/whole-character-v38/neck-clearance01/murderbird-v38-neck-clearance01-rigid.glb',
  'mantle-study01': '/assets/models/whole-character-v38/mantle-study01/murderbird-v38-mantle-study01-rigid.glb',
  'mantle-study02': '/assets/models/whole-character-v38/mantle-study02/murderbird-v38-mantle-study02-rigid.glb',
  'breast-study01': '/assets/models/whole-character-v38/breast-study01/murderbird-v38-breast-study01-rigid.glb',
  'breast-study02': '/assets/models/whole-character-v38/breast-study02/murderbird-v38-breast-study02-rigid.glb',
  'optic-cheek02-seat-fit01': '/assets/models/whole-character-v38/optic-cheek02-seat-fit01/murderbird-v38-optic-cheek02-seat-fit01-rigid.glb',
  'optic-cheek02': '/assets/models/whole-character-v38/optic-cheek02/murderbird-v38-optic-cheek02-rigid.glb',
  'optic-cheek01': '/assets/models/whole-character-v38/optic-cheek01/murderbird-v38-optic-cheek01-rigid.glb',
  'bill-identity01-socket-fit01': '/assets/models/whole-character-v38/bill-identity01-socket-fit01/murderbird-v38-bill-identity01-socket-fit01-rigid.glb',
  'bill-identity02': '/assets/models/whole-character-v38/bill-identity02/murderbird-v38-bill-identity02-rigid.glb',
  'bill-identity01': '/assets/models/whole-character-v38/bill-identity01/murderbird-v38-bill-identity01-rigid.glb',
  'breast-clearance01': '/assets/models/whole-character-v38/breast-clearance01/murderbird-v38-breast-clearance01-rigid.glb',
  'breast-clearance02': '/assets/models/whole-character-v38/breast-clearance02/murderbird-v38-breast-clearance02-rigid.glb',
} : {};
const reviewModel = import.meta.env.DEV ? reviewModels[new URLSearchParams(location.search).get('review-candidate')] : undefined;
const modelUrl = reviewModel
  ? new URL(reviewModel, location.origin).href
  : new URL('../../assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb', import.meta.url).href;
const FRONT = 2.10;
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
  const rendererName=info?gl.getParameter(info.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER);
  const softwareRenderer=info&&/swiftshader|llvmpipe|software/i.test(gl.getParameter(info.UNMASKED_RENDERER_WEBGL));
  renderer.shadowMap.enabled = !softwareRenderer;
  if(softwareRenderer)renderer.setPixelRatio(.65);
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
  controls.minDistance = 3.0;
  controls.maxDistance = 12;
  controls.minPolarAngle = .25;
  controls.maxPolarAngle = Math.PI / 2 - .03;
  controls.target.set(0, 1.0, 0);
  camera.position.set(-4.0, 2.85, 6.2);
  controls.update();
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, .04);
  scene.environment = environment.texture;
  scene.environmentIntensity = .48;
  room.dispose(); pmrem.dispose();
  const hemisphere = new THREE.HemisphereLight(0xddeee8, 0x3b3327, 1.7);
  scene.add(hemisphere);
  const key = new THREE.DirectionalLight(0xffe0b8, 4);
  key.position.set(-2.5, 4.5, 4); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  Object.assign(key.shadow.camera, { left: -4, right: 4, top: 4, bottom: -4, near: .1, far: 12 });
  key.shadow.bias = -.0004; key.shadow.normalBias = .012;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xb1dcd4, 2.4);
  fill.position.set(3, 2.5, -2); scene.add(fill);
  const exhibitLighting = {
    environment: scene.environment, environmentIntensity: scene.environmentIntensity,
    fog: scene.fog, toneMappingExposure: renderer.toneMappingExposure,
    hemisphereSky: hemisphere.color.clone(), hemisphereGround: hemisphere.groundColor.clone(), hemisphereIntensity: hemisphere.intensity,
    keyColor: key.color.clone(), keyIntensity: key.intensity, fillColor: fill.color.clone(), fillIntensity: fill.intensity,
  };

  const metal = new THREE.MeshStandardMaterial({ color: '#404b45', roughness: .62, metalness: .65 });
  const brass = new THREE.MeshStandardMaterial({ color: '#998260', roughness: .5, metalness: .7 });
  const floorMat = new THREE.MeshStandardMaterial({ color: '#323a36', roughness: .87, metalness: .15 });
  const mesh = (geometry, material, position) => {
    const o = new THREE.Mesh(geometry, material); o.position.set(...position);
    o.castShadow = true; o.receiveShadow = true; scene.add(o); return o;
  };
  mesh(new THREE.BoxGeometry(6.08, .10, 4.42), metal, [0, -.065, 0]);
  mesh(new THREE.BoxGeometry(5.9, .012, 4.24), floorMat, [0, -.009, 0]);
  const ground = mesh(new THREE.PlaneGeometry(200, 200), new THREE.MeshStandardMaterial({color:'#111916',roughness:.95}), [0, -.12, 0]);
  ground.rotation.x = -Math.PI / 2;
  // Soft local contact shadows follow the planted soles in software rendering.
  const footShadows=[];
  if(softwareRenderer){
    for(let side=0;side<2;side++){
      const shadow=mesh(new THREE.CircleGeometry(1,24),new THREE.MeshBasicMaterial({color:'#07100b',transparent:true,opacity:.22,depthWrite:false}),[0,.001,0]);
      shadow.rotation.x=-Math.PI/2;shadow.scale.set(.15,.23,1);footShadows.push(shadow);
    }
  }
  const cage = new THREE.Group(); scene.add(cage);
  const bars = [];
  function bar(a, b, radius, permanent = false) {
    const start = new THREE.Vector3(...a), end = new THREE.Vector3(...b);
    const mat = metal.clone(); mat.transparent = true; mat.opacity = .66; mat.depthWrite = false;
    const o = new THREE.Mesh(new THREE.CylinderGeometry(radius, radius, start.distanceTo(end), 6), mat);
    o.position.copy(start).add(end).multiplyScalar(.5);
    o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), end.sub(start).normalize());
    o.userData.permanent = permanent; cage.add(o); bars.push(o); return o;
  }
  const contactRails=[];
  for (const z of [FRONT, -FRONT]) {
    for (let i = -7; i <= 7; i++) {
      const x=i*.4;
      const rail=bar([x,0,z],[x,2.55,z],.021);
      if(z===FRONT&&[-3,0,3].includes(i))contactRails.push(rail);
    }
    bar([-2.9,2.55,z],[2.9,2.55,z],.045);
    bar([-2.9,.07,z],[2.9,.07,z],.035,true);
  }
  for (const x of [-2.9, 2.9]) {
    for (let i = -5; i <= 5; i++) bar([x,0,i*.4],[x,2.55,i*.4],.021);
    bar([x,2.55,-FRONT],[x,2.55,FRONT],.045);
    bar([x,.07,-FRONT],[x,.07,FRONT],.035,true);
  }
  const target = mesh(new THREE.TorusGeometry(.075,.009,8,24), brass, [0,1.60,FRONT+.018]);
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
  const names = ['body','neck','head','jaw','breastplate','cranial-cover','winding-drive','power-core','processing','industrial-repairs','builder-optics','left-mantle','right-mantle','left-wing-shield','right-wing-shield'];
  for (const name of ['cervical-mid-a', 'cervical-mid-b', 'cervical-upper']) {
    if (model.getObjectByName(name)) names.push(name);
  }
  const nodes = Object.fromEntries(names.map(name => [name, model.getObjectByName(name)]));
  if (names.some(name => !nodes[name]) || nodes['left-wing-shield']?.parent !== nodes['left-mantle'] || nodes['right-wing-shield']?.parent !== nodes['right-mantle']) {
    controls.dispose(); environment.dispose(); renderer.dispose(); canvas.remove();
    throw new Error('Model assembly contract is incomplete.');
  }
  const rest = Object.fromEntries(names.map(name => [name, { position:nodes[name].position.clone(), rotation:nodes[name].rotation.clone() }]));
  const motion=createEraMotion(model,nodes,rest);
  const mechanisms=createEraMechanisms({scene,model,nodes,rest});
  const animationProof={clips:gltf.animations.map(a=>({name:a.name,duration:a.duration,tracks:a.tracks.length})),verified:false};
  // Probe the actual exported transform track before enabling procedural motion.
  if(gltf.animations.length){
    const mixer=new THREE.AnimationMixer(model);const action=mixer.clipAction(gltf.animations[0]);action.play();mixer.setTime(.5);
    animationProof.sampleRotation=nodes.head.rotation.y;animationProof.verified=Math.abs(nodes.head.rotation.y)>.05;
    mixer.stopAllAction();mixer.uncacheRoot(model);
    names.forEach(name=>{nodes[name].position.copy(rest[name].position);nodes[name].rotation.copy(rest[name].rotation);});
  }
  const exteriorSurfaces = [];
  const exteriorTextures = new Set();
  const exteriorNormalMaps = new Set();
  const textureMaps = ['map','metalnessMap','roughnessMap','normalMap','aoMap','emissiveMap','alphaMap','bumpMap'];
  model.traverse(o => {
    if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; }
    const extras=o.userData?.extras||o.userData||{};
    const eraTag=extras.exteriorEras;
    if (typeof eraTag === 'string') {
      const eras=new Set(eraTag.split(',').map(value=>value.trim().toLowerCase()).filter(value=>['maker','mechanic','builder'].includes(value)));
      if (eras.size) exteriorSurfaces.push({ object:o, eras, region:String(extras.region||'unassigned'), surfaceRole:String(extras.surfaceRole||'unassigned') });
    }
    if (o.isMesh) for (const material of (Array.isArray(o.material)?o.material:[o.material])) for (const key of textureMaps) {
      const texture=material?.[key];if(texture?.isTexture){exteriorTextures.add(texture);if(key==='normalMap')exteriorNormalMaps.add(texture);}
    }
  });
  function effectiveVisibility(object) {
    for(let current=object;current&&current!==scene.parent;current=current.parent)if(!current.visible)return false;
    return true;
  }
  function exteriorMetrics() {
    const byEra=Object.fromEntries(['maker','mechanic','builder'].map(value=>[value,{eligibleObjects:0,visibleObjects:0,regions:{}}]));
    const surfaceObjects=exteriorSurfaces.map(entry=>{
      const visible=effectiveVisibility(entry.object);
      for(const eligibleEra of entry.eras){
        const state=byEra[eligibleEra];state.eligibleObjects++;
        if(visible){state.visibleObjects++;state.regions[entry.region]=(state.regions[entry.region]||0)+1;}
      }
      return {name:entry.object.name,eras:[...entry.eras],region:entry.region,surfaceRole:entry.surfaceRole,visible};
    });
    let decodedMipmapBytes=0;
    const textures=[...exteriorTextures].map(texture=>{
      const image=texture.image||texture.source?.data||{};
      const width=Number(image.width||image.naturalWidth||image.videoWidth||0),height=Number(image.height||image.naturalHeight||image.videoHeight||0);
      const estimate=width&&height?Math.ceil(width*height*4*4/3):null;
      if(estimate)decodedMipmapBytes+=estimate;
      return {name:texture.name||texture.uuid,width,height,estimatedRGBABytesWithMipmaps:estimate,normalMap:exteriorNormalMaps.has(texture)};
    });
    return {currentEra:era,taggedObjectCount:exteriorSurfaces.length,byEra,surfaceObjects,textures:{count:textures.length,normalMapCount:exteriorNormalMaps.size,estimatedDecodedMipmapBytes:decodedMipmapBytes,images:textures}};
  }
  const markerNodes = {
    beak: ['head', [0,-.035,.28]], joint:['body',[.28,.6,.07]],
    shell:['breastplate',[.245,-.19,.01]], drive:['winding-drive',[.13,0,0]],
    power:['power-core',[0,0,.055]], mind:['processing',[0,.04,0]], guard:['right-wing-shield',[-.085,.12,.125]],
  };
  const anchors = Object.fromEntries(Object.entries(markerNodes).map(([id,[name,p]])=>{const landmark=model.getObjectByName('anchor-'+id);if(landmark)return [id,landmark];const o=new THREE.Object3D();o.position.set(...p);nodes[name].add(o);return [id,o];}));
  const billTip = model.getObjectByName('bill-contact');
  if(!billTip)throw new Error('Model contact landmark is missing.');
  const exploded = INSPECTION_EXPLODED_OFFSETS;
  const lines = {};
  Object.keys(exploded).forEach(name => { const line=new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(),new THREE.Vector3()]),guideMat);guides.add(line);lines[name]=line; });
  let open = 0, separation = 0, targetOpen = 0, targetSeparation = 0, armed = false, era = 'builder', pointer, frameCount=0;
  let selected = 'beak';
  let lastSnapshot, lastWidth=0, lastHeight=0;
  const vector = new THREE.Vector3();
  const worldTip = new THREE.Vector3();
  const contactBounds = new THREE.Box3();
  const frameTimes = [];
  let lightingMode='exhibit';
  let finishReport;
  const highlight = new THREE.Box3Helper(new THREE.Box3(),0xd9b87b); highlight.visible=false;scene.add(highlight);

  function setEra(value) {
    era=value;
    motion.resetEra(value);mechanisms.setEra(value);
    exteriorSurfaces.forEach(entry=>{entry.object.visible=entry.eras.has(value);});
    finishReport=applyEraFinishes(model,value);
    nodes['winding-drive'].visible=false;
    nodes['power-core'].visible=value==='builder';
    nodes.processing.visible=value==='builder';
    nodes['builder-optics'].visible=value==='builder';
    nodes['industrial-repairs'].visible=value!=='maker';
  }
  function reviewCamera(name) {
    const views={
      wholeBirdTight:{target:[0,1,0],offset:[-1.792,.80,2.752]},
      threeQuarter:{target:[0,1,0],offset:[-2.8,1.25,4.3]},
      threeQuarterLeft:{target:[0,1,0],offset:[2.8,1.25,4.3]},
      elevated:{target:[0,1,0],offset:[-2.8,3.4,4.3]},
      low:{target:[0,1,0],offset:[-2.8,-.7,4.3]},
      front:{target:[0,1,0],offset:[0,1.0,5.2]},
      rear:{target:[0,1,0],offset:[0,1.0,-5.2]},
      left:{target:[0,1,0],offset:[5.2,1.0,0]},
      right:{target:[0,1,0],offset:[-5.2,1.0,0]},
      leftShoulder:{target:[.27,1.49,.02],offset:[1.48,.22,.48]},
      rightShoulder:{target:[-.27,1.49,.02],offset:[-1.48,.22,.48]},
      head:{target:[0,1.72,.1],offset:[-.82,.45,1.92]},
      headOblique:{target:[0,1.72,.1],offset:[-1.6,.24,1.2]},
      headProfile:{target:[0,1.72,.1],offset:[-2,.12,0]},
      headRearOblique:{target:[0,1.72,.1],offset:[-1.4,.25,-1.45]},
      neck:{target:[0,1.48,.02],offset:[-.78,.18,1.55]},
      breast:{target:[0,1.12,.14],offset:[-.68,.12,1.42]},
      feet:{target:[0,.24,0],offset:[-.60,.10,1.30]},
    };
    const view=views[name];if(!view)throw new RangeError(`Unknown review camera: ${name}`);
    const headView=['head','headOblique','headProfile','headRearOblique'].includes(name);
    const closeup=headView||['leftShoulder','rightShoulder','neck','breast','feet'].includes(name);
    controls.minDistance=headView?.5:closeup?1.2:3.0;controls.maxDistance=closeup?4.0:12.0;
    model.updateMatrixWorld(true);
    const rigRoot=model.getObjectByName('murderbird')||model;
    const origin=rigRoot.getWorldPosition(new THREE.Vector3());
    const orientation=rigRoot.getWorldQuaternion(new THREE.Quaternion());
    const target=new THREE.Vector3(...view.target).applyQuaternion(orientation).add(origin);
    const offset=new THREE.Vector3(...view.offset).applyQuaternion(orientation);
    if(headView) {
      // Frame the actual articulated head, not an assumed rest-space height.
      const bounds=new THREE.Box3().setFromObject(nodes.head);
      if(!bounds.isEmpty()) {
        bounds.getCenter(target);
        const sphere=bounds.getBoundingSphere(new THREE.Sphere());
        const vertical=THREE.MathUtils.degToRad(camera.fov)/2;
        const horizontal=Math.atan(Math.tan(vertical)*camera.aspect);
        const distance=sphere.radius/Math.sin(Math.min(vertical,horizontal))*1.12;
        offset.normalize().multiplyScalar(Math.max(.5,distance));
      }
    }
    controls.target.copy(target);camera.position.copy(target).add(offset);controls.update();
    return {name,camera:camera.position.toArray(),target:controls.target.toArray()};
  }
  function reviewLighting(mode) {
    if(mode==='neutral') {
      lightingMode='neutral';scene.environmentIntensity=.16;scene.fog=null;renderer.toneMappingExposure=1;
      hemisphere.color.set('#f4f4f4');hemisphere.groundColor.set('#686868');hemisphere.intensity=1.45;
      key.color.set('#ffffff');key.intensity=3.0;fill.color.set('#ffffff');fill.intensity=1.4;
      cage.visible=false;guides.visible=false;target.visible=false;highlight.visible=false;
    } else if(mode==='exhibit') {
      lightingMode='exhibit';scene.environment=exhibitLighting.environment;scene.environmentIntensity=exhibitLighting.environmentIntensity;scene.fog=exhibitLighting.fog;renderer.toneMappingExposure=exhibitLighting.toneMappingExposure;
      hemisphere.color.copy(exhibitLighting.hemisphereSky);hemisphere.groundColor.copy(exhibitLighting.hemisphereGround);hemisphere.intensity=exhibitLighting.hemisphereIntensity;
      key.color.copy(exhibitLighting.keyColor);key.intensity=exhibitLighting.keyIntensity;fill.color.copy(exhibitLighting.fillColor);fill.intensity=exhibitLighting.fillIntensity;
      cage.visible=true;
    } else throw new RangeError(`Unknown review lighting: ${mode}`);
    return lightingMode;
  }
  function resize() {
    const width=container.clientWidth,height=container.clientHeight;
    if(!width||!height||width===lastWidth&&height===lastHeight)return;
    lastWidth=width;lastHeight=height;renderer.setSize(width,height);camera.aspect=width/height;
    camera.fov=THREE.MathUtils.radToDeg(2*Math.atan(Math.tan(THREE.MathUtils.degToRad(36/2))*Math.max(1,1.53/camera.aspect)));camera.updateProjectionMatrix();
  }
  function reset(){controls.minDistance=3.0;controls.maxDistance=12;controls.target.set(0,1.0,0);camera.position.set(-4.0,2.85,6.2);controls.update();}
  function percentile(values,quantile) {
    if(!values.length)return null;
    const sorted=[...values].sort((a,b)=>a-b);
    return sorted[Math.min(sorted.length-1,Math.floor((sorted.length-1)*quantile))];
  }
  function metrics() {
    const frameP50=percentile(frameTimes,.50),frameP95=percentile(frameTimes,.95);
    return {
      kind:'webgl',modelUrl,era,open,separation,frameCount,meanFps:frameTimes.length/frameTimes.reduce((a,b)=>a+b,0),
      performance:{renderer:rendererName,softwareRenderer:Boolean(softwareRenderer),viewport:{width:lastWidth,height:lastHeight,bufferWidth:canvas.width,bufferHeight:canvas.height,pixelRatio:renderer.getPixelRatio()},frameMsP50:frameP50===null?null:frameP50*1000,frameMsP95:frameP95===null?null:frameP95*1000,fpsP50:frameP50>0?1/frameP50:null,fpsP05:frameP95>0?1/frameP95:null,drawCalls:renderer.info.render.calls,triangles:renderer.info.render.triangles,geometries:renderer.info.memory.geometries,gpuTextures:renderer.info.memory.textures},
      exterior:exteriorMetrics(),finishes:finishReport,review:{lighting:lightingMode,camera:camera.position.toArray(),target:controls.target.toArray()},
      tip:worldTip.toArray(),headFront:contactBounds.setFromObject(nodes.head,true).max.z,
      wingAngles:{leftShoulder:nodes['left-mantle'].rotation.x,leftElbow:nodes['left-wing-shield'].rotation.x,rightShoulder:nodes['right-mantle'].rotation.x,rightElbow:nodes['right-wing-shield'].rotation.x},
      wingBounds:{left:new THREE.Box3().setFromObject(nodes['left-mantle'],true),right:new THREE.Box3().setFromObject(nodes['right-mantle'],true)},contactPlane:FRONT,
      camera:camera.position.toArray(),target:controls.target.toArray(),state:lastSnapshot?.state,motion:motion.metrics(),mechanisms:mechanisms.metrics(),animationProof,
      nodes:Object.fromEntries(['winding-drive','power-core','processing','builder-optics'].map(n=>[n,nodes[n].visible])),
    };
  }
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
    const rect=canvas.getBoundingClientRect();const point=new THREE.Vector2((e.clientX-rect.left)/rect.width*2-1,1-(e.clientY-rect.top)/rect.height*2);const ray=new THREE.Raycaster();ray.setFromCamera(point,camera);const hit=new THREE.Vector3();if(ray.ray.intersectPlane(new THREE.Plane(new THREE.Vector3(0,0,1),-FRONT),hit))onReach?.({x:clamp(hit.x/1.2,-1,1),y:0});
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
    {
      names.forEach(name=>{nodes[name].position.copy(rest[name].position);nodes[name].rotation.copy(rest[name].rotation);});
      motion.tick(dt,snapshot);
    }
    applyInspectionPose(nodes,rest,open,separation);
    model.updateMatrixWorld(true);
    mechanisms.tick(dt,snapshot,motion.driveMetrics(),{open,separation});
    billTip.getWorldPosition(worldTip);
    const state=snapshot.state;
    target.visible=armed||snapshot.visitorPresent;
    target.position.x=snapshot.lookTarget?.x??0;
    target.position.y=1.60;
    const motionInfo=motion.feedback();
    if(softwareRenderer&&frameCount%2===0){
      for(let i=0;i<2;i++){const foot=model.getObjectByName((i?'right':'left')+'-foot');foot.getWorldPosition(vector);footShadows[i].position.set(vector.x,.001,vector.z+.055);}
    }
    const viewDirection=camera.position.clone().sub(controls.target).normalize();
    bars.forEach(o=>{
      const near=o.position.x*viewDirection.x+o.position.z*viewDirection.z>0;
      o.material.opacity=open>.02?.035:near?.12:.48;
      if(contactRails.includes(o)){const hit=Math.abs(o.position.x-(snapshot.lookTarget?.x??0))<.05;const active=hit&&motionInfo.contact;o.material.opacity=open>.02?.035:active?.82:.32;o.position.z=FRONT+(active?.004*Math.sin(snapshot.phase*40):0);}
    });
    guides.visible=separation>.015;
    Object.entries(lines).forEach(([name,line])=>{
      line.visible=nodes[name].visible;
      const a=nodes[name].parent.localToWorld(rest[name].position.clone());
      const b=nodes[name].getWorldPosition(new THREE.Vector3());
      line.geometry.setFromPoints([a,b]);line.computeLineDistances();
    });
    const projectedMarkers = Object.entries(anchors).map(([id,anchor])=>{
      const mechanism=['drive','power','mind'].includes(id);
      const point=mechanism?mechanisms.getAnchor(id):anchor.getWorldPosition(vector);
      const present=Boolean(point);
      if(point)vector.copy(point);vector.project(camera);
      return {id,x:(vector.x+1)*lastWidth/2,y:(1-vector.y)*lastHeight/2,visible:present&&open>.8&&vector.z<1&&Math.abs(vector.x)<.94&&Math.abs(vector.y)<.86};
    });
    projectedMarkers.filter(marker=>!marker.visible).forEach(marker=>updateMarker(marker.id,marker.x,marker.y,false));
    layoutMarkers(projectedMarkers,lastWidth,lastHeight).forEach(marker=>updateMarker(marker.id,marker.x,marker.y,true,marker));
    if(highlight.visible){const part=mechanisms.getPart(selected)||nodes[markerNodes[selected]?.[0]];if(part?.visible)highlight.box.setFromObject(part);else highlight.visible=false;}
    renderer.render(scene,camera);
  }
  setEra(era);resize();
  return {
    kind:'webgl', resize, tick, reset, nudge, setEra,
    driveState:()=>motion.driveMetrics().mechanicalStage,
    feedback:()=>motion.feedback(),
    select(id){selected=id;highlight.visible=targetOpen>0;},
    setSection(value){targetOpen=value?1:0;if(!value)targetSeparation=0;highlight.visible=false;},
    setSeparation(value){targetSeparation=targetOpen?clamp(Number(value)||0,0,1):0;},
    setArmed(value){armed=value;controls.enabled=!value;canvas.style.cursor=value?'crosshair':'grab';pointer=null;},
    isAssembled(){return open===0&&separation===0;},
    focus(id){const point=['drive','power','mind'].includes(id)?mechanisms.getAnchor(id):anchors[id]?.getWorldPosition(new THREE.Vector3());if(!point)return;vector.copy(point);const delta=vector.clone().sub(controls.target),radius=camera.position.distanceTo(controls.target);controls.target.copy(vector);if(['drive','power'].includes(id)&&era!=='maker'){const view=new THREE.Vector3(-6,1.8,2).normalize().applyAxisAngle(new THREE.Vector3(0,1,0),model.rotation.y);camera.position.copy(vector).addScaledVector(view,radius);}else camera.position.add(delta);controls.update();},
    metrics,
    reviewCamera,
    reviewLighting,
    ...(import.meta.env.DEV ? {
      // Copy the last rendered transform cache. A QA read must not tick motion,
      // recalculate the rig, alter the camera, or synthesize a requested pose.
      poseSnapshot(){
        const pivotMatrices=[];
        model.traverse(object=>{
          if(object.isMesh||!object.name)return;
          const path=[];
          for(let node=object;node&&node!==model.parent;node=node.parent)path.unshift(node.name||node.type);
          pivotMatrices.push({name:object.name,path:path.join('/'),parent:object.parent===model.parent?null:object.parent?.name||null,
            kind:'transform',localMatrix:object.matrix.toArray(),worldMatrix:object.matrixWorld.toArray(),
            position:object.position.toArray(),quaternion:object.quaternion.toArray(),scale:object.scale.toArray()});
        });
        return {frameCount,modelUrl,era,open,separation,pivotMatrices,
          coordinateConvention:'Three.js Y-up, forward +Z; column-major matrices copied from the last rendered frame.',
          scope:'Live browser transform capture only; not a surface-clearance or physical-simulation result.'};
      },
    } : {}),
    destroy(){listeners.abort();controls.dispose();environment.dispose();scene.traverse(o=>{o.geometry?.dispose();if(o.material){(Array.isArray(o.material)?o.material:[o.material]).forEach(m=>m.dispose());}});renderer.dispose();canvas.remove();},
  };
}
