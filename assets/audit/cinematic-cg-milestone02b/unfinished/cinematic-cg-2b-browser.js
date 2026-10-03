import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

/** Mount the CG2b review viewer. assetBase is the directory containing the GLBs. */
export function mount(host, state, assetBase = '../../models/cinematic-cg-milestone02b/') {
  window.cg2Loaded = false;
  window.cg2Era = null;
  window.cg2Meshes = 0;
  window.cg2Error = null;
  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ antialias: true });
  } catch (error) {
    state.textContent = 'WebGL unavailable. Use the rendered comparisons above.';
    window.cg2Error = String(error);
    return { dispose() {}, reset() {}, load() {} };
  }
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  host.appendChild(renderer.domElement);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x181818);
  const pmrem = new THREE.PMREMGenerator(renderer);
  const room = new RoomEnvironment();
  const environment = pmrem.fromScene(room, 0.04);
  scene.environment = environment.texture;
  room.dispose();
  pmrem.dispose();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.01, 100);
  camera.up.set(0, 0, 1);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  function reset() {
    camera.position.set(-2.6, -2.1, 1.8);
    controls.target.set(0, -0.08, 0.87);
    controls.update();
  }
  reset();
  scene.add(new THREE.HemisphereLight(0xc5dbd6, 0x241c16, 1));
  const light = new THREE.DirectionalLight(0xffd4a5, 2);
  light.position.set(-3, -4, 5);
  scene.add(light);
  let activeModel, generation = 0, disposed = false;
  const loader = new GLTFLoader();
  const base = new URL(assetBase.endsWith('/') ? assetBase : assetBase + '/', document.baseURI);
  function release(model) {
    const geometries = new Set(), materials = new Set(), textures = new Set();
    model.traverse(object => {
      if (!object.isMesh) return;
      geometries.add(object.geometry);
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        materials.add(material);
        for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
      }
    });
    geometries.forEach(geometry => geometry.dispose());
    materials.forEach(material => material.dispose());
    textures.forEach(texture => { texture.source?.data?.close?.(); texture.dispose(); });
  }
  function load(era) {
    if (disposed) return;
    if (!['builder', 'maker', 'mechanic'].includes(era)) throw new Error('Unknown CG2b era: ' + era);
    const request = ++generation;
    state.textContent = 'Loading ' + era + ' study…';
    window.cg2Loaded = false;
    window.cg2Error = null;
    window.cg2Meshes = 0;
    loader.load(new URL('murderbird-cg-2b-' + era + '.glb', base).href, gltf => {
      const model = gltf.scene;
      if (disposed || request !== generation) { release(model); return; }
      try {
        // Blender's glTF axes are Y-up. Restore authored Z-up without rescaling.
        model.rotation.x = Math.PI / 2;
        model.updateMatrixWorld(true);
        const box = new THREE.Box3().setFromObject(model);
        if (box.isEmpty() || ![...box.min.toArray(), ...box.max.toArray()].every(Number.isFinite)) {
          throw new Error('Model bounds are empty or non-finite');
        }
        model.position.sub(box.getCenter(new THREE.Vector3())).add(new THREE.Vector3(0, -0.08, 0.87));
        model.updateMatrixWorld(true);
        let meshes = 0;
        model.traverse(object => {
          if (!object.isMesh) return;
          meshes++;
          for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
            if (!(material.transmission > 0)) continue;
            // Use the actual unmerged lens depth recorded by the exporter.
            // FrontSide avoids counting the closed lens twice in transmission.
            const depth = Number(material.userData.cg2bGlassThickness);
            material.thickness = depth > 0 && Number.isFinite(depth) ? depth :
              (material.thickness > 0 ? material.thickness : 0.0143);
            material.side = THREE.FrontSide;
            material.needsUpdate = true;
          }
        });
        if (activeModel) { scene.remove(activeModel); release(activeModel); }
        scene.add(model);
        activeModel = model;
        window.cg2Era = era;
        window.cg2Meshes = meshes;
        window.cg2Loaded = true;
        state.textContent = 'Textured GLB loaded. Drag to orbit; scroll to zoom.';
      } catch (error) {
        release(model);
        state.textContent = 'Preview failed: ' + error.message;
        window.cg2Error = String(error);
      }
    }, undefined, error => {
      if (disposed || request !== generation) return;
      state.textContent = 'Preview failed: ' + (error.message || String(error));
      window.cg2Error = String(error);
    });
  }
  function resize() {
    const width = Math.max(host.clientWidth, 1), height = Math.max(host.clientHeight, 1);
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  const observer = new ResizeObserver(resize);
  observer.observe(host);
  resize();
  const resetButton = document.getElementById('reset');
  const eraSelect = document.getElementById('era');
  const changeEra = event => load(event.target.value);
  resetButton?.addEventListener('click', reset);
  eraSelect?.addEventListener('change', changeEra);
  renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
  load(eraSelect?.value || 'builder');
  return {
    load, reset, scene, camera, renderer,
    dispose() {
      disposed = true;
      generation++;
      observer.disconnect();
      resetButton?.removeEventListener('click', reset);
      eraSelect?.removeEventListener('change', changeEra);
      renderer.setAnimationLoop(null);
      controls.dispose();
      if (activeModel) release(activeModel);
      environment.dispose();
      renderer.dispose();
      renderer.domElement.remove();
      window.cg2Loaded = false;
    },
  };
}
