import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { createCervicalArticulation } from '/src/scene/cervical-articulation.js';
import { applyInspectionPose, INSPECTION_EXPLODED_OFFSETS } from '/src/scene/inspection-pose.js';

const MODEL_URL = '/assets/models/whole-character-v24/attempt-form02/murderbird-whole-character-v24.glb';
const FALLBACKS = ['/assets/audit/whole-character-v24/attempt-form02/after-reference-angle.png'];
const $ = id => document.getElementById(id);
const stage = $('viewer-stage');
const host = $('webgl-host');
const fallbackImage = $('fallback-image');
const status = $('load-status');
const candidateLabel = $('candidate-label');

const state = {
  ready: false, era: 'builder', pitch: 0, yaw: 0, jaw: 0,
  breastOpen: 0, explode: 0, materialMode: 'neutral', view: 'three-quarter',
};
let model = null;
let renderer = null;
let controls = null;
let camera = null;
let cervical = null;
let nodes = null;
let rest = null;
let cervicalRestPose = null;
let jawRest = null;
let inspectionRest = null;
let originalMaterials = new Map();
let originalVisibility = new Map();
let neutralMaterials = [];
let bounds = null;
let headBounds = null;
let animationId = 0;
let contextWasLost = false;
let previousFrameTime = performance.now();

function setStatus(message, isError = false) {
  status.textContent = message;
  status.style.color = isError ? '#ffd0bd' : '';
}

function showFallback(message) {
  state.ready = false;
  host.classList.add('hidden');
  fallbackImage.classList.remove('hidden');
  setControlsEnabled(false);
  setStatus(message, true);
}

function setControlsEnabled(enabled) {
  document.querySelectorAll('.controls input, .controls select, .controls button, .viewbar button')
    .forEach(control => { control.disabled = !enabled; });
}

let fallbackIndex = 0;
fallbackImage.addEventListener('error', () => {
  fallbackIndex += 1;
  if (fallbackIndex < FALLBACKS.length) fallbackImage.src = FALLBACKS[fallbackIndex];
  else setStatus('Candidate GLB is not available yet, and no local still image could be loaded.', true);
});

function vectorCopy(value) { return value.clone(); }
function saveNode(node) {
  return { position: vectorCopy(node.position), quaternion: vectorCopy(node.quaternion), scale: vectorCopy(node.scale) };
}
function restoreNode(node, saved) {
  node.position.copy(saved.position);
  node.quaternion.copy(saved.quaternion);
  node.scale.copy(saved.scale);
}

function resolveNodes(loadedModel) {
  const names = [
    'body', 'neck', 'cervical-mid-a', 'cervical-mid-b', 'cervical-upper', 'head', 'jaw',
    'breastplate', 'cranial-cover', 'left-mantle', 'right-mantle', 'left-wing-shield',
    'right-wing-shield', 'winding-drive', 'power-core', 'processing',
  ];
  const result = Object.fromEntries(names.map(name => [name, loadedModel.getObjectByName(name)]));
  const missing = names.filter(name => !result[name]);
  if (missing.length) throw new Error(`Required named assembly missing: ${missing.join(', ')}`);
  return result;
}

function categoryFor(mesh) {
  const owners = new Set(['head', 'jaw', 'upper-bill', 'builder-optics', 'cranial-cover', 'processing', 'bill-contact']);
  const p = mesh.parent?.name;
  if (p === 'neck' || p === 'cervical-upper' || p?.startsWith('cervical-mid')) return 'neck';
  if (['left-mantle', 'right-mantle', 'left-wing-shield', 'right-wing-shield'].includes(p)) return 'mantle';
  if (p === 'breastplate' || mesh.userData.region === 'breast' || mesh.userData.region === 'back') return 'breast';
  if (owners.has(p) || mesh.userData.region === 'head') return 'head';
  return mesh.userData.region || 'body';
}

function neutralMaterial(region, role) {
  const key = `${region}:${role}`;
  const existing = neutralMaterials.find(entry => entry.key === key);
  if (existing) return existing.material;
  const colorByRole = {
    plate: 0xbab9b2, guard: 0x949b98, frame: 0x535b59,
    bearing: 0x777d79, rib: 0x727b78, support: 0x68716e,
  };
  const regionAdjust = { head: 0.022, neck: -0.018, breast: 0, mantle: 0.012, body: -0.012 };
  const base = new THREE.Color(colorByRole[role] ?? 0x9b9d97);
  const adjust = regionAdjust[region] ?? 0;
  base.r = THREE.MathUtils.clamp(base.r + adjust, 0, 1);
  base.g = THREE.MathUtils.clamp(base.g + adjust, 0, 1);
  base.b = THREE.MathUtils.clamp(base.b + adjust, 0, 1);
  const material = new THREE.MeshStandardMaterial({ color: base, metalness: 0.18, roughness: 0.76 });
  neutralMaterials.push({ key, material });
  return material;
}

function installMaterialMode(mode) {
  state.materialMode = mode;
  model.traverse(object => {
    if (!object.isMesh) return;
    if (!originalMaterials.has(object)) originalMaterials.set(object, object.material);
    if (mode === 'original') {
      object.material = originalMaterials.get(object);
      return;
    }
    const region = categoryFor(object);
    const role = object.userData.surfaceRole || (object.userData.constructionClass ? 'frame' : 'plate');
    const material = neutralMaterial(region, role);
    object.material = Array.isArray(object.material) ? object.material.map(() => material) : material;
  });
}

function applyEra(era) {
  state.era = era;
  model.traverse(object => {
    if (!object.isMesh) return;
    if (!originalVisibility.has(object)) originalVisibility.set(object, object.visible);
    const raw = object.userData.exteriorEras ?? object.userData.eras;
    const eligible = typeof raw !== 'string' || raw.split(',').map(x => x.trim()).includes(era);
    object.visible = originalVisibility.get(object) && eligible;
  });
}

function updatePose() {
  if (!state.ready) return;
  cervical.restorePose(cervicalRestPose);
  restoreNode(nodes.jaw, jawRest);
  for (const [name, saved] of Object.entries(inspectionRest)) restoreNode(nodes[name], saved);

  cervical.setPitch(state.pitch, state.yaw, 0);
  // This opposite local pitch is a reading aid for this neck/jaw study only.
  const counterPitch = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -state.pitch);
  nodes.head.quaternion.copy(cervicalRestPose.find(item => item.node === nodes.head).quaternion).multiply(counterPitch);
  nodes.jaw.quaternion.copy(jawRest.quaternion).multiply(
    new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), state.jaw),
  );
  applyInspectionPose(nodes, rest, state.breastOpen, state.explode);
  model.updateMatrixWorld(true);
  setOutputs();
}

function setOutputs() {
  $('pitch-out').value = Number(state.pitch).toFixed(2);
  $('yaw-out').value = Number(state.yaw).toFixed(2);
  $('jaw-out').value = Number(state.jaw).toFixed(3);
  $('breast-out').value = `${Math.round(state.breastOpen * 100)}%`;
  $('explode-out').value = `${Math.round(state.explode * 100)}%`;
}

function setView(view) {
  state.view = view;
  if (!camera || !controls || !bounds) return;
  model.updateMatrixWorld(true);
  bounds.setFromObject(model);
  const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  const span = Math.max(size.x, size.y, size.z, 1);
  const distance = span * 1.98;
  const headTarget = headBounds?.getCenter(new THREE.Vector3()) ?? center.clone();
  const headSize = headBounds?.getSize(new THREE.Vector3()) ?? new THREE.Vector3(span, span, span);
  const headSpan = Math.max(headSize.x, headSize.y, headSize.z, .25);
  const presets = {
    front: { target: center, offset: new THREE.Vector3(0, size.y * .12, distance) },
    side: { target: center, offset: new THREE.Vector3(-distance, size.y * .08, 0) },
    'three-quarter': { target: center, offset: new THREE.Vector3(-distance * .86, size.y * .45, distance * .51) },
    rear: { target: center, offset: new THREE.Vector3(0, size.y * .12, -distance) },
    head: { target: headTarget, offset: new THREE.Vector3(-headSpan * 1.35, headSpan * .45, headSpan * 1.8) },
  };
  const preset = presets[view] ?? presets['three-quarter'];
  controls.target.copy(preset.target);
  camera.position.copy(preset.target).add(preset.offset);
  camera.near = Math.max(.01, span * .005);
  camera.far = span * 20;
  camera.updateProjectionMatrix();
  controls.update();
}

function reset() {
  $('pitch').value = '0'; $('yaw').value = '0'; $('jaw').value = '0';
  $('breast-open').value = '0'; $('explode').value = '0'; $('era').value = 'builder';
  $('materials').value = 'neutral';
  Object.assign(state, { pitch: 0, yaw: 0, jaw: 0, breastOpen: 0, explode: 0 });
  if (state.ready) {
    applyEra('builder'); installMaterialMode('neutral'); updatePose(); setView('three-quarter');
  }
}

let scene = null;
function animate() {
  animationId = requestAnimationFrame(animate);
  const now = performance.now();
  const dt = Math.min(Math.max(0, (now - previousFrameTime) / 1000), .05);
  previousFrameTime = now;
  controls?.update(dt);
  if (scene && renderer && camera) renderer.render(scene, camera);
}

function start() {
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    host.replaceChildren(renderer.domElement);
    host.classList.add('hidden');
    renderer.domElement.addEventListener('webglcontextlost', event => {
      event.preventDefault();
      contextWasLost = true;
      cancelAnimationFrame(animationId);
      controls?.dispose();
      showFallback('WebGL context was lost. The still is shown; reload this local page to retry the viewer.');
    });
  } catch (error) {
    showFallback(`WebGL is unavailable here. Showing the latest local still. (${error.message})`);
    return;
  }

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x151918);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 2.1));
  const key = new THREE.DirectionalLight(0xffffff, 2.5);
  key.position.set(-4, 6, 7); scene.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 1.25);
  fill.position.set(4, 2, -5); scene.add(fill);

  camera = new THREE.PerspectiveCamera(33, 1, .01, 100);
  camera.up.set(0, 1, 0);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = .075;
  controls.minDistance = .15;
  controls.maxDistance = 18;
  controls.target.set(0, 1, 0);
  const resize = () => {
    if (!renderer || !camera) return;
    const width = Math.max(1, stage.clientWidth);
    const height = Math.max(1, stage.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(stage);
  resize();

  setStatus('Loading the local V24 attempt-form02 GLB…');
  new GLTFLoader().load(MODEL_URL, gltf => {
    try {
      if (contextWasLost || renderer.getContext().isContextLost()) {
        showFallback('WebGL context was lost while loading. The still is shown; reload this local page to retry the viewer.');
        return;
      }
      model = gltf.scene;
      scene.add(model);
      model.updateMatrixWorld(true);
      nodes = resolveNodes(model);
      rest = {
        neck: { position: nodes.neck.position.clone() },
        head: { position: nodes.head.position.clone() },
      };
      cervical = createCervicalArticulation(model, nodes, rest);
      cervicalRestPose = cervical.capturePose();
      jawRest = saveNode(nodes.jaw);
      const inspectionNames = ['breastplate', 'cranial-cover', ...Object.keys(INSPECTION_EXPLODED_OFFSETS)];
      inspectionRest = Object.fromEntries([...new Set(inspectionNames)].map(name => [name, saveNode(nodes[name])]));
      rest['cranial-cover'] = inspectionRest['cranial-cover'];
      bounds = new THREE.Box3().setFromObject(model);
      headBounds = new THREE.Box3().setFromObject(nodes.head);
      applyEra(state.era);
      installMaterialMode(state.materialMode);
      state.ready = true;
      updatePose();
      setView('three-quarter');
      host.classList.remove('hidden');
      fallbackImage.classList.add('hidden');
      setControlsEnabled(true);
      candidateLabel.textContent = 'Attempt form02 · local exported GLB';
      setStatus('Real exported model loaded. Orbit by dragging; controls below set the bounded study pose.');
      previousFrameTime = performance.now();
      animate();
      window.v24Review = { model, renderer, controls, cervical, setView, reset, state };
    } catch (error) {
      console.error('V24 viewer initialization failed after GLB load:', error);
      candidateLabel.textContent = 'Attempt form02 · GLB loaded, viewer initialization failed';
      showFallback(`The GLB loaded, but the review viewer could not initialize. Showing the local still. (${error?.message ?? 'initialization error'})`);
      window.v24Review = { model, renderer, controls, cervical, setView, reset, state };
    }
  }, undefined, error => {
    showFallback(`Could not load the V24 candidate GLB. Showing the latest local still. (${error?.message ?? 'load error'})`);
    candidateLabel.textContent = 'Attempt form02 · GLB pending or unavailable; fallback still shown';
    window.v24Review = { model: null, renderer, controls: null, cervical: null, setView, reset, state };
  });
}

function bindControls() {
  $('pitch').addEventListener('input', event => { state.pitch = Number(event.target.value); updatePose(); });
  $('yaw').addEventListener('input', event => { state.yaw = Number(event.target.value); updatePose(); });
  $('jaw').addEventListener('input', event => { state.jaw = Number(event.target.value); updatePose(); });
  $('breast-open').addEventListener('input', event => { state.breastOpen = Number(event.target.value); updatePose(); });
  $('explode').addEventListener('input', event => { state.explode = Number(event.target.value); updatePose(); });
  $('era').addEventListener('change', event => { if (state.ready) applyEra(event.target.value); });
  $('materials').addEventListener('change', event => { if (state.ready) installMaterialMode(event.target.value); });
  $('reset').addEventListener('click', reset);
  document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => setView(button.dataset.view)));
  setControlsEnabled(false);
}

bindControls();
start();
