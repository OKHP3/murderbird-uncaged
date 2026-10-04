/** Static CG assessment viewer. The animated V37 exhibit retains its own rig. */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

export async function createCGViewer(container, url, { lighting = 'neutral', signal, onProgress, onContextLost } = {}) {
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1.5, 1.5, 1, -1, .01, 100);
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', 'Static MurderBird CG candidate. Drag to orbit, pinch or scroll to zoom. Arrow keys orbit, plus and minus zoom, R resets.');
  container.append(canvas);
  const controls = new OrbitControls(camera, canvas);
  controls.enablePan = false; controls.minZoom = .5; controls.maxZoom = 4;
  const pmrem = new THREE.PMREMGenerator(renderer), room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, .04); room.dispose(); pmrem.dispose();
  scene.environment = environment.texture;
  const hemisphere = new THREE.HemisphereLight(), key = new THREE.DirectionalLight(), fill = new THREE.DirectionalLight();
  key.position.set(-3, 5, 4); fill.position.set(4, 3, 1); scene.add(hemisphere, key, fill);
  let model, disposed = false, center, radius, fittedHeight = 1;
  const render = () => { if (!disposed && model) { renderer.render(scene, camera); container.dataset.cg = JSON.stringify(snapshot()); } };
  const setLighting = mode => {
    const neutral = mode === 'neutral'; lighting = mode;
    scene.background = new THREE.Color(neutral ? '#686868' : '#232b29');
    scene.environmentIntensity = neutral ? .16 : .48;
    renderer.toneMappingExposure = neutral ? 1 : 1.25;
    hemisphere.color.set(neutral ? '#f4f4f4' : '#ddeee8'); hemisphere.groundColor.set(neutral ? '#686868' : '#3b3327'); hemisphere.intensity = neutral ? 1.45 : 1.7;
    key.color.set(neutral ? '#ffffff' : '#ffe0b8'); key.intensity = neutral ? 3 : 4;
    fill.color.set(neutral ? '#ffffff' : '#b1dcd4'); fill.intensity = neutral ? 1.4 : 2.4;
    render();
  };
  const resize = () => {
    const width = Math.max(1, container.clientWidth), height = Math.max(1, container.clientHeight), aspect = width / height;
    renderer.setSize(width, height, false);
    const halfHeight = Math.max(fittedHeight / 2, fittedHeight / 2 / aspect);
    camera.top = halfHeight; camera.bottom = -halfHeight; camera.right = halfHeight * aspect; camera.left = -camera.right;
    camera.updateProjectionMatrix(); render();
  };
  const observer = new ResizeObserver(resize);
  const contextLost = event => { event.preventDefault(); onContextLost?.(); };
  canvas.addEventListener('webglcontextlost', contextLost);
  function snapshot() { return { lighting, camera: camera.position.toArray(), target: controls.target.toArray(), zoom: camera.zoom, triangles: renderer.info.render.triangles }; }
  function zoom(factor) { camera.zoom = THREE.MathUtils.clamp(camera.zoom * factor, .5, 4); camera.updateProjectionMatrix(); render(); }
  function orbit(horizontal, vertical = 0) {
    const offset = camera.position.clone().sub(controls.target);
    offset.applyAxisAngle(camera.up, horizontal);
    const right = new THREE.Vector3().crossVectors(camera.up, offset).normalize();
    offset.applyAxisAngle(right, vertical);
    camera.position.copy(controls.target).add(offset); controls.update(); render();
  }
  function resetView() {
    // Same source direction as checkpoint09; adaptive framing is not native pixel registration.
    camera.up.set(.2257888317, .9612616897, -.1580990553);
    camera.position.copy(center).add(new THREE.Vector3(-.7874193192, .2756373882, .5513570309).normalize().multiplyScalar(radius * 5));
    camera.zoom = 1; controls.target.copy(center); camera.updateProjectionMatrix(); controls.update(); render();
  }
  const keyboard = event => {
    const actions = { ArrowLeft: () => orbit(.15), ArrowRight: () => orbit(-.15), ArrowUp: () => orbit(0, .1), ArrowDown: () => orbit(0, -.1), '+': () => zoom(1.15), '=': () => zoom(1.15), '-': () => zoom(1 / 1.15), r: resetView, R: resetView };
    if (actions[event.key]) { event.preventDefault(); actions[event.key](); }
  };
  canvas.addEventListener('keydown', keyboard); controls.addEventListener('change', render);
  function dispose() {
    if (disposed) return; disposed = true;
    observer.disconnect(); controls.removeEventListener('change', render); controls.dispose();
    canvas.removeEventListener('keydown', keyboard); canvas.removeEventListener('webglcontextlost', contextLost);
    const textures = new Set(), materials = new Set();
    model?.traverse(object => { object.geometry?.dispose(); for (const material of [object.material].flat().filter(Boolean)) materials.add(material); });
    for (const material of materials) { for (const value of Object.values(material)) if (value?.isTexture) textures.add(value); material.dispose(); }
    for (const texture of textures) texture.dispose();
    environment.dispose(); renderer.dispose(); canvas.remove(); delete container.dataset.cg;
  }
  try {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error(`Model request failed (${response.status})`);
    const total = Number(response.headers.get('content-length'));
    let buffer;
    if (response.body && total) {
      const reader = response.body.getReader(), chunks = []; let loaded = 0;
      while (true) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); loaded += value.byteLength; onProgress?.(Math.min(100, Math.round(loaded / total * 100))); }
      const joined = new Uint8Array(loaded); let offset = 0; for (const chunk of chunks) { joined.set(chunk, offset); offset += chunk.byteLength; } buffer = joined.buffer;
    } else buffer = await response.arrayBuffer();
    signal?.throwIfAborted();
    const gltf = await new GLTFLoader().parseAsync(buffer, ''); model = gltf.scene;
    signal?.throwIfAborted(); scene.add(model);
    const box = new THREE.Box3().setFromObject(model); if (box.isEmpty()) throw new Error('Model has no visible geometry');
    center = box.getCenter(new THREE.Vector3()); radius = box.getSize(new THREE.Vector3()).length() / 2;
    fittedHeight = radius * 2.05; camera.near = Math.max(.001, radius / 1000); camera.far = radius * 100;
    setLighting(lighting); resetView(); resize(); observer.observe(container);
    return { setLighting, zoom, orbit, resetView, snapshot, dispose };
  } catch (error) { dispose(); throw error; }
}
