import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const mount = document.querySelector('#viewer');
const status = document.querySelector('#status');
const still = document.querySelector('#render-fallback');
const eraSelect = document.querySelector('#era');
const toggle = document.querySelector('#toggle-render');
const cameraButtons = [...document.querySelectorAll('[data-camera]')];
const modelUrl = new URL('../../models/whole-silhouette-v16/attempt-03/murderbird-whole-silhouette-v16.glb', import.meta.url).href;

let model;
let renderer;
let camera;
let controls;
let fixed = false;

const cameraViews = {
  reference: { position: [-6, 2.75, 3.5], target: [0, 1.02, 0.08], zoom: 1 },
  front: { position: [0, 1.65, 7], target: [0, 1.02, 0.08], zoom: 1 },
  side: { position: [-7.5, 1.25, 0], target: [0, 1.02, 0.08], zoom: 1 },
  rear: { position: [0, 1.65, -7], target: [0, 1.02, 0.08], zoom: 1 },
  head: { position: [-6, 2.45, 3.5], target: [0, 1.56, 0.27], zoom: 1.85 },
  legs: { position: [-6, 1.65, 3.5], target: [0, 0.42, -0.03], zoom: 1.75 },
};

function showCamera(name) {
  const view = cameraViews[name];
  if (!view || !camera || !controls) return;
  camera.position.fromArray(view.position);
  camera.zoom = view.zoom;
  camera.updateProjectionMatrix();
  controls.target.fromArray(view.target);
  controls.update();
  cameraButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.camera === name)));
}

function applyEra() {
  const choice = eraSelect.value;
  model?.traverse(object => {
    if (object.isMesh) {
      object.visible = String(object.userData.exteriorEras || 'maker,mechanic,builder').split(',').includes(choice);
    }
  });
}

function showFixed(value) {
  if (!value && !model) return;
  fixed = value;
  mount.hidden = value;
  still.hidden = !value;
  toggle.setAttribute('aria-pressed', String(value));
  toggle.textContent = value ? 'Show actual 3D' : 'Show fixed render';
  status.textContent = value
    ? 'Fixed native reference-angle render · not interactive motion.'
    : 'Exported neutral-rest model · fresh kinematic checks and browser observations exist; full surface clearance and likeness remain unresolved.';
  cameraButtons.forEach(button => { button.disabled = value; });
  eraSelect.disabled = value;
}

toggle.disabled = true;
eraSelect.disabled = true;
cameraButtons.forEach(button => { button.disabled = true; });
toggle.addEventListener('click', () => showFixed(!fixed));

try {
  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.setClearColor(0x53575b);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.1;
  mount.appendChild(renderer.domElement);

  const scene = new THREE.Scene();
  scene.add(new THREE.HemisphereLight(0xffffff, 0x626874, 2.1));
  for (const [position, intensity] of [[[-3, 5, 4], 3.4], [[4, 3, -2], 1.6]]) {
    const light = new THREE.DirectionalLight(0xffffff, intensity);
    light.position.fromArray(position);
    scene.add(light);
  }

  camera = new THREE.OrthographicCamera(-1.25, 1.25, 1.25, -1.25, 0.01, 50);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.minZoom = 0.6;
  controls.maxZoom = 3.2;
  const resize = () => {
    const width = mount.clientWidth || 400;
    const height = mount.clientHeight || 530;
    camera.left = -1.25 * width / height;
    camera.right = 1.25 * width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  };
  new ResizeObserver(resize).observe(mount);
  resize();
  showCamera('reference');

  const gltf = await new GLTFLoader().loadAsync(modelUrl);
  model = gltf.scene;
  const clay = new THREE.MeshStandardMaterial({ color: 0xadb0b3, metalness: 0.05, roughness: 0.72 });
  let meshCount = 0;
  model.traverse(object => {
    if (object.isMesh) {
      object.material = clay;
      meshCount += 1;
    }
  });
  scene.add(model);
  applyEra();

  const gl = renderer.getContext();
  const debug = gl.getExtension('WEBGL_debug_renderer_info');
  window.__silhouetteReview = {
    modelUrl,
    scope: 'static exported rest geometry; discrete native pose illustrations and fresh kinematic/browser observations are separately recorded; full surface clearance and likeness remain unresolved',
    meshCount,
    renderer: debug ? gl.getParameter(debug.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER),
    snapshot: () => {
      let visibleMeshes = 0;
      model.traverse(object => { if (object.isMesh && object.visible) visibleMeshes += 1; });
      return {
        era: eraSelect.value,
        fixedRender: fixed,
        visibleMeshes,
        drawCalls: renderer.info.render.calls,
        triangles: renderer.info.render.triangles,
        camera: camera.position.toArray(),
        target: controls.target.toArray(),
      };
    },
  };

  toggle.disabled = false;
  eraSelect.disabled = false;
  cameraButtons.forEach(button => { button.disabled = false; });
  status.textContent = 'Exported neutral-rest model · fresh kinematic checks and browser observations exist; full surface clearance and likeness remain unresolved.';
  eraSelect.addEventListener('change', applyEra);
  cameraButtons.forEach(button => button.addEventListener('click', () => showCamera(button.dataset.camera)));
  renderer.setAnimationLoop(() => {
    if (!fixed) {
      controls.update();
      renderer.render(scene, camera);
    }
  });
} catch (error) {
  showFixed(true);
  toggle.textContent = 'Fixed render only';
  status.textContent = 'Fixed native render shown. The 3D preview is unavailable; reload this page to retry.';
  console.error(error);
}
