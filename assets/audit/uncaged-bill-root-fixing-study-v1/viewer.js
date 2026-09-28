// Local-only diagnostic viewer. No application selector or publication input.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const versions = {
  candidate: {
    url: '../../models/uncaged-bill-root-fixing-study-v1/murderbird-bill-root-fixing-study-v1.glb',
    sha: 'f5c0f5ad99ace316ed84426d2a1148a093706612c9602d78b93023d46d989e6e',
  },
  baseline: {
    url: '../../models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.glb',
    sha: 'ad7391eede50aae79fa5430c6125dab8ff982025d25a0aa9362fdc6a757311f1',
  },
};
const panel = document.querySelector('#viewer');
const status = document.querySelector('#load-status');
const modelSelect = document.querySelector('#model');
const eraSelect = document.querySelector('#era');
const jawControl = document.querySelector('#jaw');
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setClearColor(0x64696d);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1;
panel.append(renderer.domElement);
const scene = new THREE.Scene();
scene.add(new THREE.HemisphereLight(0xe4edf5, 0x5e6064, 2.3));
const key = new THREE.DirectionalLight(0xffffff, 3.5);
key.position.set(-3, 5, 4); scene.add(key);
const fill = new THREE.DirectionalLight(0xe4e9ed, 1.8);
fill.position.set(4, 3, -2); scene.add(fill);
const camera = new THREE.OrthographicCamera(-.6, .6, .44, -.44, .01, 30);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 1.78, .29);
controls.enableDamping = false;
controls.minZoom = .7; controls.maxZoom = 3;
const models = new Map();
let current = null, generation = 0;

function render() { renderer.render(scene, camera); }
function view(name) {
  const positions = { front: [0, 1.78, 6], profile: [-6, 1.78, .3], 'three-quarter': [-6, 2.4, 3], 'right-seats': [-6, 1.80, .47], 'left-seats': [6, 1.80, .47] };
  camera.position.set(...positions[name]); camera.zoom = 1;
  if (name.endsWith('-seats')) { camera.zoom = 2.4; controls.target.set(0, 1.80, .47); }
  else controls.target.set(0, 1.78, .29);
  controls.update(); camera.updateProjectionMatrix(); render();
}
function pose() {
  if (!current) return;
  // The selected Mechanic reconstruction locks the head/jaw assembly.
  jawControl.disabled = eraSelect.value === 'mechanic';
  if (jawControl.disabled) jawControl.value = '0';
  current.traverse(object => {
    const eras = object.userData.exteriorEras;
    if (eras) object.visible = (Array.isArray(eras) ? eras : eras.split(',')).includes(eraSelect.value);
  });
  current.getObjectByName('jaw').rotation.x = Number(jawControl.value);
  current.updateMatrixWorld(true); render();
}
async function selectModel() {
  const ticket = ++generation, choice = modelSelect.value, config = versions[choice];
  status.textContent = 'Loading and verifying the exact model…';
  try {
    if (!models.has(choice)) {
      const url = new URL(config.url, location.href);
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Model request returned ${response.status}`);
      const bytes = await response.arrayBuffer();
      const sha = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2, '0')).join('');
      if (sha !== config.sha) throw new Error('The model bytes do not match this review version.');
      const gltf = await new GLTFLoader().parseAsync(bytes, new URL('.', url).href);
      if (!gltf.scene.getObjectByName('jaw')) throw new Error('The jaw attachment is missing.');
      models.set(choice, gltf.scene);
    }
    if (ticket !== generation) return;
    if (current) scene.remove(current);
    current = models.get(choice); scene.add(current); pose();
    status.textContent = `Actual WebGL · ${choice === 'candidate' ? 'Seated bill fixings' : 'Paired bill V2'} · verified SHA-256 ${config.sha}`;
  } catch (error) {
    if (ticket === generation) status.textContent = `3D review unavailable: ${error.message}`;
  }
}
function resize() {
  const width = panel.clientWidth, height = panel.clientHeight;
  renderer.setSize(width, height, false);
  camera.left = -.44 * width / height; camera.right = .44 * width / height;
  camera.updateProjectionMatrix(); render();
}
new ResizeObserver(resize).observe(panel);
controls.addEventListener('change', render);
modelSelect.addEventListener('change', selectModel);
eraSelect.addEventListener('change', pose);
jawControl.addEventListener('input', pose);
document.querySelectorAll('[data-view]').forEach(button => button.addEventListener('click', () => view(button.dataset.view)));
view('three-quarter'); resize(); selectModel();
