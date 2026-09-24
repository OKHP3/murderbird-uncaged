import * as THREE from 'three';

const bronze = new THREE.MeshStandardMaterial({ color: 0x9a6847, metalness: .78, roughness: .36 });
const bronzeLight = new THREE.MeshStandardMaterial({ color: 0xc49562, metalness: .77, roughness: .3 });
const darkMetal = new THREE.MeshStandardMaterial({ color: 0x333b36, metalness: .75, roughness: .4 });
const feather = new THREE.MeshStandardMaterial({ color: 0x5c685b, metalness: .48, roughness: .64 });
const featherLight = new THREE.MeshStandardMaterial({ color: 0x84917a, metalness: .4, roughness: .65 });
const ceramic = new THREE.MeshStandardMaterial({ color: 0xe1c9a2, metalness: .13, roughness: .5 });
const black = new THREE.MeshStandardMaterial({ color: 0x111b1b, metalness: .5, roughness: .17 });
const emissive = new THREE.MeshStandardMaterial({ color: 0xe6a462, emissive: 0xc57235, emissiveIntensity: 1.7, metalness: .45, roughness: .2 });

function addMesh(parent, geometry, material, position, rotation, scale) {
  const mesh = new THREE.Mesh(geometry, material);
  if (position) mesh.position.set(...position);
  if (rotation) mesh.rotation.set(...rotation);
  if (scale) mesh.scale.set(...scale);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

const sphere = new THREE.SphereGeometry(1, 24, 16);
const cylinder = new THREE.CylinderGeometry(1, 1, 1, 12);
const cone = new THREE.ConeGeometry(1, 1, 10);
const torus = new THREE.TorusGeometry(1, .06, 8, 48);
function ball(parent, mat, pos, size) { return addMesh(parent, sphere, mat, pos, null, size); }
function ring(parent, mat, pos, size, rotation = [0, 0, 0]) { return addMesh(parent, torus, mat, pos, rotation, size); }
function strut(parent, a, b, radius, mat) {
  const start = new THREE.Vector3(...a), end = new THREE.Vector3(...b);
  const mesh = addMesh(parent, cylinder, mat, start.clone().add(end).multiplyScalar(.5).toArray(), null, [radius, start.distanceTo(end), radius]);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), end.sub(start).normalize());
  return mesh;
}
function featherShape(parent, mat, from, to, width) {
  const start = new THREE.Vector3(...from), end = new THREE.Vector3(...to);
  const mesh = addMesh(parent, cone, mat, start.clone().add(end).multiplyScalar(.5).toArray(), null, [width, start.distanceTo(end), width * .52]);
  mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), start.sub(end).normalize());
  return mesh;
}

export function createExhibit(container, updateMarker) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.55;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  container.append(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 100);
  camera.position.set(0, 1.1, 9.4);
  camera.lookAt(0, .15, 0);
  scene.add(new THREE.AmbientLight(0xc6d0bd, 1.7));
  const key = new THREE.DirectionalLight(0xffd6a3, 4);
  key.position.set(-4, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.left = -5; key.shadow.camera.right = 5;
  key.shadow.camera.top = 6; key.shadow.camera.bottom = -5;
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xaac6b0, 3);
  rim.position.set(3, 3, -4);
  scene.add(rim);

  const model = new THREE.Group();
  scene.add(model);
  // Turntable and a restrained reference cage, drawn behind the specimen.
  addMesh(scene, new THREE.CylinderGeometry(2.35, 2.45, .13, 64), darkMetal, [0, -2.1, 0]);
  addMesh(scene, new THREE.CylinderGeometry(2.2, 2.25, .045, 64), bronze, [0, -2.005, 0]);
  ring(scene, bronzeLight, [0, -1.975, 0], [2.22, 2.22, 1], [-Math.PI / 2, 0, 0]);
  const ground = addMesh(scene, new THREE.PlaneGeometry(100, 100), new THREE.ShadowMaterial({ color: 0x080c09, opacity: .38 }), [0, -2.2, 0], [-Math.PI / 2, 0, 0]);
  ground.receiveShadow = true;
  const cage = new THREE.Group();
  scene.add(cage);
  const cageMat = new THREE.MeshStandardMaterial({ color: 0x58655a, metalness: .85, roughness: .49, transparent: true, opacity: .33, depthWrite: false });
  for (let i = 0; i < 11; i++) {
    const angle = i / 11 * Math.PI * 2;
    const x = Math.sin(angle) * 2.35, z = Math.cos(angle) * 2.35;
    strut(cage, [x, -1.95, z], [x, 2.35, z], .012, cageMat);
  }
  ring(cage, cageMat, [0, 2.35, 0], [2.35, 2.35, .32], [-Math.PI / 2, 0, 0]);

  // Layered torso, sternum and segmented neck.
  ball(model, darkMetal, [0, .05, -.16], [.83, 1.12, .69]);
  ball(model, feather, [0, .22, -.22], [.84, 1.06, .72]);
  for (let i = 0; i < 5; i++) {
    const y = -.62 + i * .33;
    const w = .54 + .25 * Math.sin(i / 4 * Math.PI);
    ball(model, i % 2 ? bronze : featherLight, [0, y, .48], [w, .14, .18]);
  }
  const chestPlate = new THREE.Group();
  model.add(chestPlate);
  ball(chestPlate, bronze, [0, .27, .55], [.66, .81, .21]);
  ball(chestPlate, feather, [0, .68, .64], [.49, .35, .12]);
  for (const side of [-1, 1]) {
    for (let i = 0; i < 4; i++) {
      featherShape(chestPlate, i % 2 ? bronzeLight : bronze, [side * (.12 + i * .13), .68 - i * .22, .76], [side * (.24 + i * .1), .18 - i * .22, .76], .1);
    }
  }
  const core = new THREE.Group();
  model.add(core);
  ball(core, ceramic, [0, .22, .43], [.36, .48, .27]);
  ball(core, emissive, [0, .22, .72], [.17, .23, .1]);
  for (let i = 0; i < 6; i++) {
    const a = i / 6 * Math.PI * 2;
    strut(core, [Math.sin(a) * .32, .22 + Math.cos(a) * .4, .63], [Math.sin(a) * .16, .22 + Math.cos(a) * .22, .76], .024, bronze);
  }
  ring(core, bronzeLight, [0, .22, .73], [.25, .32, 1], [0, 0, -.2]);
  core.visible = false;
  for (let i = 0; i < 4; i++) {
    const y = .86 + i * .24;
    ball(model, i % 2 ? bronze : darkMetal, [0, y, -.02 - i * .07], [.34 - i * .02, .19, .29]);
  }
  ball(model, feather, [0, 1.54, -.2], [.47, .53, .47]);
  ball(model, bronze, [0, 1.75, .08], [.46, .34, .42]);
  ball(model, featherLight, [0, 1.97, -.21], [.27, .21, .26]);
  // Profile crest and hooked beak.
  for (let i = 0; i < 4; i++) featherShape(model, i % 2 ? featherLight : bronze, [-.19 + i * .13, 2.01, -.3], [-.35 + i * .18, 2.47 - i * .08, -.66], .12);
  addMesh(model, new THREE.ConeGeometry(.28, .9, 5), bronzeLight, [0, 1.69, .72], [Math.PI / 2 + .21, 0, 0], [1, 1, .72]);
  featherShape(model, darkMetal, [0, 1.61, .86], [0, 1.36, 1.07], .16);
  const eyes = [];
  for (const side of [-1, 1]) {
    ball(model, bronzeLight, [side * .36, 1.77, .36], [.17, .17, .09]);
    const eye = ball(model, black, [side * .36, 1.78, .43], [.11, .11, .05]);
    eyes.push(eye);
    ball(model, emissive, [side * .36, 1.78, .47], [.035, .035, .02]);
    // Hinged wings with layered mechanical feathers.
    const wing = new THREE.Group(); wing.position.set(side * .68, .66, -.18); wing.rotation.z = side * .16; model.add(wing);
    ball(wing, darkMetal, [side * .35, -.35, -.08], [.46, .79, .26]);
    ball(wing, feather, [side * .44, -.25, .06], [.48, .77, .2]);
    ring(wing, bronzeLight, [side * .04, .14, .18], [.13, .13, .8]);
    for (let i = 0; i < 6; i++) {
      const x = side * (.25 + i * .15);
      featherShape(wing, i % 2 ? feather : featherLight, [x, -.27 - i * .11, .17], [x + side * .18, -1.11 - i * .09, .02], .14);
    }
    // Exposed piston and joint assembly.
    strut(model, [side * .38, -.78, -.12], [side * .46, -1.42, .1], .09, darkMetal);
    strut(model, [side * .46, -1.36, .12], [side * .51, -1.78, .52], .07, bronzeLight);
    ball(model, bronze, [side * .44, -1.35, .1], [.18, .16, .18]);
    ring(model, bronzeLight, [side * .44, -1.35, .25], [.14, .14, .7]);
    for (let toe = -1; toe <= 1; toe++) {
      const x = side * .51 + toe * .17;
      strut(model, [side * .51, -1.78, .52], [x, -1.93, .86 + (1 - Math.abs(toe)) * .11], .055, darkMetal);
      featherShape(model, bronzeLight, [x, -1.93, .86 + (1 - Math.abs(toe)) * .11], [x, -2.02, 1.07 + (1 - Math.abs(toe)) * .1], .08);
    }
  }
  for (let i = -2; i <= 2; i++) featherShape(model, i % 2 ? bronze : feather, [i * .13, -.58, -.65], [i * .22, -1.62 + Math.abs(i) * .08, -1.18], .18);

  const markers = {
    beak: new THREE.Vector3(0, 1.71, 1.07),
    joint: new THREE.Vector3(.48, -1.33, .42),
    core: new THREE.Vector3(0, .25, .85),
    eye: new THREE.Vector3(.39, 1.8, .49),
  };
  let section = false, selected = 'beak', yaw = -.3, pitch = 0, targetYaw = yaw, targetPitch = pitch, zoom = 9.4, reaction = 0;
  let pointer = null;
  const canvas = renderer.domElement;
  canvas.addEventListener('pointerdown', event => {
    pointer = { x: event.clientX, y: event.clientY, yaw: targetYaw, pitch: targetPitch };
    canvas.setPointerCapture(event.pointerId);
  });
  canvas.addEventListener('pointermove', event => {
    if (!pointer) return;
    targetYaw = pointer.yaw + (event.clientX - pointer.x) * .007;
    targetPitch = THREE.MathUtils.clamp(pointer.pitch + (event.clientY - pointer.y) * .004, -.32, .32);
  });
  canvas.addEventListener('pointerup', () => { pointer = null; });
  canvas.addEventListener('pointercancel', () => { pointer = null; });
  canvas.addEventListener('wheel', event => {
    event.preventDefault();
    zoom = THREE.MathUtils.clamp(zoom + event.deltaY * .008, 6.3, 13);
  }, { passive: false });

  let lastWidth = 0, lastHeight = 0;
  function resize() {
    const width = container.clientWidth, height = container.clientHeight;
    if (!width || !height || width === lastWidth && height === lastHeight) return;
    lastWidth = width; lastHeight = height;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.fov = width < 560 ? 43 : 34;
    camera.updateProjectionMatrix();
  }
  const projected = new THREE.Vector3();
  let frame = 0;
  function animate() {
    frame = requestAnimationFrame(animate);
    yaw = THREE.MathUtils.lerp(yaw, targetYaw, .085);
    pitch = THREE.MathUtils.lerp(pitch, targetPitch, .085);
    model.rotation.set(pitch, yaw, 0);
    cage.rotation.y += .0007;
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, zoom, .1);
    if (section) {
      chestPlate.position.x = THREE.MathUtils.lerp(chestPlate.position.x, 1.07, .09);
      chestPlate.rotation.y = THREE.MathUtils.lerp(chestPlate.rotation.y, -.65, .09);
    } else {
      chestPlate.position.x = THREE.MathUtils.lerp(chestPlate.position.x, 0, .09);
      chestPlate.rotation.y = THREE.MathUtils.lerp(chestPlate.rotation.y, 0, .09);
    }
    if (reaction > 0) {
      reaction -= .025;
      model.rotation.z = Math.sin(reaction * 36) * reaction * .045;
    } else model.rotation.z = Math.sin(performance.now() * .001) * .009;
    emissive.emissiveIntensity = 1.4 + Math.sin(performance.now() * .003) * .45;
    eyes.forEach(eye => { eye.scale.y = Math.max(.05, 1 - Math.max(0, Math.sin(performance.now() * .0017)) ** 35 * .95) * .11; });
    model.updateMatrixWorld();
    Object.entries(markers).forEach(([id, position]) => {
      projected.copy(position).applyMatrix4(model.matrixWorld).project(camera);
      const visible = projected.z < 1 && projected.z > -1 && projected.x > -.95 && projected.x < .95 && projected.y > -.88 && projected.y < .88 && (id !== 'core' || section);
      updateMarker(id, (projected.x + 1) * .5 * lastWidth, (1 - projected.y) * .5 * lastHeight, visible);
    });
    renderer.render(scene, camera);
  }
  resize(); animate();
  return {
    resize,
    select(id) { selected = id; reaction = id === 'eye' ? .7 : .3; },
    setSection(value) { section = value; core.visible = value; reaction = .6; },
    react() { reaction = 1.5; },
    reset() { targetYaw = -.3; targetPitch = 0; zoom = 9.4; reaction = .4; },
    destroy() { cancelAnimationFrame(frame); renderer.dispose(); container.removeChild(canvas); },
  };
}