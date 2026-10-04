/** Static GLB review only. Import from a local Vite review page; no production wiring. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export async function createSupervisedReview(container, glbUrl, { lighting = 'neutral' } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.75));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(36, 1, .01, 100);
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'Static MurderBird material review. Drag to orbit, scroll to zoom.');
  container.append(canvas);
  const controls = new OrbitControls(camera, canvas);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, .04);
  room.dispose(); pmrem.dispose();
  scene.environment = environment.texture;
  const hemisphere = new THREE.HemisphereLight();
  const key = new THREE.DirectionalLight();
  const fill = new THREE.DirectionalLight();
  key.position.set(-2.5, 4.5, 4); fill.position.set(3, 2.5, -2);
  scene.add(hemisphere, key, fill);
  function setLighting(mode) {
    if (!['neutral', 'exhibit'].includes(mode)) throw new RangeError(`Unknown lighting: ${mode}`);
    const neutral = mode === 'neutral';
    scene.background = new THREE.Color(neutral ? '#686868' : '#232b29');
    scene.environmentIntensity = neutral ? .16 : .48;
    renderer.toneMappingExposure = neutral ? 1 : 1.25;
    hemisphere.color.set(neutral ? '#f4f4f4' : '#ddeee8');
    hemisphere.groundColor.set(neutral ? '#686868' : '#3b3327');
    hemisphere.intensity = neutral ? 1.45 : 1.7;
    key.color.set(neutral ? '#ffffff' : '#ffe0b8'); key.intensity = neutral ? 3 : 4;
    fill.color.set(neutral ? '#ffffff' : '#b1dcd4'); fill.intensity = neutral ? 1.4 : 2.4;
    lighting = mode;
  }
  setLighting(lighting);
  let model;
  const resize = () => {
    const width = Math.max(1, container.clientWidth), height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix();
  };
  const observer = new ResizeObserver(resize);
  function dispose() {
    renderer.setAnimationLoop(null); observer.disconnect(); controls.dispose();
    const textures = new Set(), materials = new Set();
    model?.traverse(object => {
      object.geometry?.dispose();
      for (const material of [object.material].flat().filter(Boolean)) materials.add(material);
    });
    for (const material of materials) {
      for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
      material.dispose();
    }
    for (const texture of textures) texture.dispose();
    environment.dispose(); renderer.dispose(); canvas.remove();
  }
  try {
    const gltf = await new GLTFLoader().loadAsync(glbUrl);
    model = gltf.scene; scene.add(model);
    const box = new THREE.Box3().setFromObject(model);
    if (box.isEmpty()) throw new Error('Loaded GLB has no visible geometry');
    const center = box.getCenter(new THREE.Vector3());
    const radius = box.getSize(new THREE.Vector3()).length() / 2;
    const distance = radius / Math.sin(THREE.MathUtils.degToRad(camera.fov / 2)) * 1.1;
    camera.near = Math.max(.001, radius / 1000); camera.far = radius * 100;
    controls.minDistance = radius * .2; controls.maxDistance = radius * 15;
    function setView(position, target) {
      camera.position.fromArray(position); controls.target.fromArray(target); controls.update();
    }
    function resetView() {
      camera.position.copy(center).add(new THREE.Vector3(-.5, .23, 1).normalize().multiplyScalar(distance));
      controls.target.copy(center); controls.update();
    }
    resetView(); resize(); observer.observe(container);
    renderer.setAnimationLoop(() => renderer.render(scene, camera));
    return { kind: 'webgl', renderer, scene, model, camera, controls, setLighting, setView, resetView, resize,
      snapshot: () => ({ lighting, camera: camera.position.toArray(), target: controls.target.toArray(),
        size: [canvas.width, canvas.height], triangles: renderer.info.render.triangles }), dispose };
  } catch (error) { dispose(); throw error; }
}
