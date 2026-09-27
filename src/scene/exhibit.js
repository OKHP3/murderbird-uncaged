import * as THREE from 'three';

const bronze = new THREE.MeshStandardMaterial({ color: 0x9a6847, metalness: .78, roughness: .36 });
const bronzeLight = new THREE.MeshStandardMaterial({ color: 0xc49562, metalness: .77, roughness: .3 });
const darkMetal = new THREE.MeshStandardMaterial({ color: 0x333b36, metalness: .75, roughness: .4 });
const feather = new THREE.MeshStandardMaterial({ color: 0x4c594c, metalness: .48, roughness: .64 });
const featherLight = new THREE.MeshStandardMaterial({ color: 0x75816a, metalness: .4, roughness: .65 });
const ceramic = new THREE.MeshStandardMaterial({ color: 0xc7b99c, metalness: .13, roughness: .56 });
const black = new THREE.MeshStandardMaterial({ color: 0x111b1b, metalness: .5, roughness: .17 });
const opticGlow = new THREE.MeshStandardMaterial({ color: 0xd98243, emissive: 0x6b3216, emissiveIntensity: .35, metalness: .45, roughness: .24 });

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
  renderer.shadowMap.type = THREE.PCFShadowMap;
  container.append(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 100);
  camera.position.set(0, .7, 9.4);
  camera.lookAt(0, .12, 0);
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
  // The floor supports the body directly; the workbench/CRT are represented
  // only in the scoped story stills, never as a perch or weight-bearing base.
  const ground = addMesh(scene, new THREE.PlaneGeometry(100, 100), new THREE.ShadowMaterial({ color: 0x080c09, opacity: .43 }), [0, -2.08, 0], [-Math.PI / 2, 0, 0]);
  ground.receiveShadow = true;

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
  // Builder-era power and processing are shown as separate, non-emissive
  // study forms. This is not a decorative reactor or a completed mind.
  ball(core, ceramic, [0, .22, .47], [.34, .46, .22]);
  ball(core, darkMetal, [0, .22, .71], [.17, .23, .07]);
  for (let i = 0; i < 6; i++) {
    const a = i / 6 * Math.PI * 2;
    strut(core, [Math.sin(a) * .32, .22 + Math.cos(a) * .4, .61], [Math.sin(a) * .16, .22 + Math.cos(a) * .22, .74], .024, bronze);
  }
  ring(core, bronzeLight, [0, .22, .74], [.23, .29, 1], [0, 0, -.2]);
  core.visible = false;
  for (let i = 0; i < 4; i++) {
    const y = .86 + i * .24;
    ball(model, i % 2 ? bronze : darkMetal, [0, y, -.02 - i * .07], [.34 - i * .02, .19, .29]);
  }
  ball(model, feather, [0, 1.54, -.2], [.47, .53, .47]);
  ball(model, bronze, [0, 1.75, .08], [.46, .34, .42]);
  ball(model, featherLight, [0, 1.97, -.21], [.27, .21, .26]);
  // Segmented swept crown and deep hooked profile bill.
  for (let i = 0; i < 4; i++) featherShape(model, i % 2 ? featherLight : bronze, [-.19 + i * .13, 2.01, -.3], [-.35 + i * .18, 2.47 - i * .08, -.66], .12);
  const billShape = new THREE.Shape();
  billShape.moveTo(-.3, 1.87);
  billShape.quadraticCurveTo(.24, 1.98, .55, 1.78);
  billShape.quadraticCurveTo(.89, 1.56, .84, 1.34);
  billShape.quadraticCurveTo(.78, 1.49, .55, 1.56);
  billShape.lineTo(.18, 1.58);
  billShape.lineTo(-.31, 1.69);
  billShape.closePath();
  const bill = new THREE.Mesh(new THREE.ExtrudeGeometry(billShape, { depth: .32, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: .045, bevelThickness: .05 }), bronzeLight);
  bill.position.z = .53;
  bill.castShadow = true;
  model.add(bill);
  featherShape(model, darkMetal, [-.24, 1.56, .75], [.34, 1.54, .81], .1);
  // The modern Builder optic is singular in this study and stays visually
  // separate from the dark, inert Water and Mechanic imagery below.
  ball(model, bronzeLight, [.3, 1.83, .34], [.18, .18, .1]);
  ball(model, black, [.3, 1.83, .42], [.12, .12, .05]);
  ball(model, opticGlow, [.3, 1.83, .47], [.055, .055, .025]);

  for (const side of [-1, 1]) {
    // Compact folded ornamental wing plates, not flight-feather spans.
    const wing = new THREE.Group();
    wing.position.set(side * .56, .68, -.22);
    wing.rotation.z = side * .1;
    model.add(wing);
    ball(wing, darkMetal, [side * .12, -.23, -.08], [.3, .55, .2]);
    ball(wing, feather, [side * .17, -.2, .08], [.29, .52, .16]);
    for (let i = 0; i < 5; i++) {
      const x = side * (.1 + i * .055);
      featherShape(wing, i % 2 ? featherLight : bronze, [x, .06 - i * .12, .16], [x + side * .035, -.48 - i * .08, .11], .075);
    }
    // Exposed piston and joint assembly.
    strut(model, [side * .38, -.78, -.12], [side * .46, -1.39, .1], .13, darkMetal);
    strut(model, [side * .46, -1.34, .12], [side * .51, -1.78, .52], .1, bronzeLight);
    ball(model, bronze, [side * .44, -1.35, .1], [.2, .19, .19]);
    ring(model, bronzeLight, [side * .44, -1.35, .25], [.16, .16, .7]);
    for (let toe = -1; toe <= 1; toe++) {
      const x = side * .51 + toe * .19;
      const toeTip = .86 + (1 - Math.abs(toe)) * .11;
      strut(model, [side * .51, -1.78, .52], [x, -1.91, toeTip], .075, darkMetal);
      featherShape(model, bronzeLight, [x, -1.91, toeTip], [x, -2.055, toeTip + .16], .09);
    }
    // Anatomical LEFT shoulder (positive local X with the Bird facing +Z)
    // alone carries the inherited double refit and a limited-travel stop.
    if (side === 1) {
      ball(model, bronzeLight, [side * .61, .73, .05], [.12, .24, .25]);
      ball(model, bronze, [side * .67, .68, .06], [.08, .2, .24]);
      strut(model, [side * .64, .85, -.03], [side * .64, .46, -.03], .045, darkMetal);
    }
  }
  for (let i = -2; i <= 2; i++) featherShape(model, i % 2 ? bronze : feather, [i * .13, -.58, -.65], [i * .17, -1.05 + Math.abs(i) * .05, -1.0], .12);

  const markers = {
    beak: new THREE.Vector3(.45, 1.66, .96),
    joint: new THREE.Vector3(.48, -1.33, .42),
    core: new THREE.Vector3(0, .25, .85),
    eye: new THREE.Vector3(.3, 1.83, .49),
  };
  let section = false, selected = 'beak', yaw = -.3, pitch = 0, targetYaw = yaw, targetPitch = pitch, zoom = 9.4;
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
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, zoom, .1);
    if (section) {
      chestPlate.position.x = THREE.MathUtils.lerp(chestPlate.position.x, 1.07, .09);
      chestPlate.rotation.y = THREE.MathUtils.lerp(chestPlate.rotation.y, -.65, .09);
    } else {
      chestPlate.position.x = THREE.MathUtils.lerp(chestPlate.position.x, 0, .09);
      chestPlate.rotation.y = THREE.MathUtils.lerp(chestPlate.rotation.y, 0, .09);
    }
    model.rotation.z = 0;
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
    supportsMarkers: true,
    resize,
    select(id) { selected = id; },
    setSection(value) { section = value; core.visible = value; },
    react() {},
    reset() { targetYaw = -.3; targetPitch = 0; zoom = 9.4; reaction = .4; },
    destroy() { cancelAnimationFrame(frame); renderer.dispose(); container.removeChild(canvas); },
  };
}