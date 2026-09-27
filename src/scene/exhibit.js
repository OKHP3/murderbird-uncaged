import * as THREE from 'three';

const materials = {
  bronze: new THREE.MeshStandardMaterial({ color: 0x8a5a39, metalness: .82, roughness: .4 }),
  bronzeLight: new THREE.MeshStandardMaterial({ color: 0xb47b4b, metalness: .8, roughness: .34 }),
  patina: new THREE.MeshStandardMaterial({ color: 0x34483d, metalness: .58, roughness: .66 }),
  darkPatina: new THREE.MeshStandardMaterial({ color: 0x26342d, metalness: .65, roughness: .58 }),
  iron: new THREE.MeshStandardMaterial({ color: 0x242a29, metalness: .76, roughness: .43 }),
  ironEdge: new THREE.MeshStandardMaterial({ color: 0x555b54, metalness: .82, roughness: .36 }),
  brass: new THREE.MeshStandardMaterial({ color: 0xb78a4e, metalness: .78, roughness: .34 }),
  ceramic: new THREE.MeshStandardMaterial({ color: 0xc5b99c, metalness: .18, roughness: .56 }),
  darkLens: new THREE.MeshStandardMaterial({ color: 0x121816, metalness: .38, roughness: .28 }),
  amberLens: new THREE.MeshStandardMaterial({ color: 0xd28643, emissive: 0x351807, emissiveIntensity: .13, metalness: .35, roughness: .28 }),
  wire: new THREE.MeshStandardMaterial({ color: 0x887650, metalness: .72, roughness: .4 }),
};

const unitSphere = new THREE.SphereGeometry(1, 24, 16);
const unitCylinder = new THREE.CylinderGeometry(.82, 1, 1, 12);
const unitCone = new THREE.ConeGeometry(1, 1, 10);
const unitTorus = new THREE.TorusGeometry(1, .055, 8, 40);
const up = new THREE.Vector3(0, 1, 0);
const floorY = -2.48;
function addMesh(parent, geometry, material, position = [0, 0, 0], scale = [1, 1, 1], rotation = [0, 0, 0]) {
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(...position);
  mesh.scale.set(...scale);
  mesh.rotation.set(...rotation);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  parent.add(mesh);
  return mesh;
}

function ball(parent, material, position, scale) {
  return addMesh(parent, unitSphere, material, position, scale);
}

function ring(parent, material, position, scale, rotation = [0, 0, 0]) {
  return addMesh(parent, unitTorus, material, position, scale, rotation);
}

function segment(parent, material, radius, start = [0, 0, 0], end = [0, 1, 0], radiusZ = radius) {
  const mesh = addMesh(parent, unitCylinder, material, [0, 0, 0], [radius, 1, radiusZ]);
  placeSegment(mesh, start, end, radius, radiusZ);
  return mesh;
}

function placeSegment(mesh, start, end, radius = mesh.scale.x, radiusZ = mesh.scale.z) {
  const a = start.isVector3 ? start : new THREE.Vector3(...start);
  const b = end.isVector3 ? end : new THREE.Vector3(...end);
  const direction = b.clone().sub(a);
  mesh.position.copy(a).add(b).multiplyScalar(.5);
  mesh.quaternion.setFromUnitVectors(up, direction.clone().normalize());
  mesh.scale.set(radius, direction.length(), radiusZ);
}

function plateShape(points, depth = .08) {
  const shape = new THREE.Shape();
  shape.moveTo(points[0][0], points[0][1]);
  for (const [x, y] of points.slice(1)) shape.lineTo(x, y);
  shape.closePath();
  return new THREE.ExtrudeGeometry(shape, {
    depth,
    bevelEnabled: true,
    bevelSegments: 2,
    steps: 1,
    bevelSize: .025,
    bevelThickness: .025,
  });
}

function makePlate(parent, material, points, position, depth = .08, rotation = [0, 0, 0]) {
  return addMesh(parent, plateShape(points, depth), material, position, [1, 1, 1], rotation);
}

function addRivets(parent, points, material, radius = .035, z = .05) {
  for (const [x, y] of points) ball(parent, material, [x, y, z], [radius, radius, radius * .55]);
}

export function createExhibit(container, updateMarker) {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.36;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  container.replaceChildren(renderer.domElement);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(34, 1, .1, 100);
  camera.position.set(0, -.04, 9.5);
  camera.lookAt(0, -.1, 0);
  scene.add(new THREE.AmbientLight(0xcbd0bd, 1.55));
  const key = new THREE.DirectionalLight(0xffd8ad, 3.25);
  key.position.set(-4, 7, 5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  key.shadow.camera.left = -5;
  key.shadow.camera.right = 5;
  key.shadow.camera.top = 5;
  key.shadow.camera.bottom = -5;
  scene.add(key);
  const rim = new THREE.DirectionalLight(0xaec6ad, 2.2);
  rim.position.set(3, 3, -4);
  scene.add(rim);

  const ground = addMesh(
    scene,
    new THREE.PlaneGeometry(100, 100),
    new THREE.ShadowMaterial({ color: 0x080c09, opacity: .4 }),
    [0, floorY, 0],
    [1, 1, 1],
    [-Math.PI / 2, 0, 0],
  );
  ground.receiveShadow = true;

  const model = new THREE.Group();
  const body = new THREE.Group();
  model.add(body);
  scene.add(model);

  // Relative proportions are a visual design target (neck ≈ half the torso;
  // legs ≈ torso length), not measurements certified from a reference image.
  // The substantial torso and hip mass replace the earlier small songbird read.
  ball(body, materials.iron, [0, .02, -.08], [.78, .91, .66]);
  ball(body, materials.darkPatina, [0, .04, .08], [.76, .88, .65]);
  ball(body, materials.patina, [0, -.56, -.04], [.78, .39, .67]);
  ball(body, materials.patina, [0, .55, -.02], [.73, .42, .6]);

  const chestCover = new THREE.Group();
  body.add(chestCover);
  const chestPlate = makePlate(
    chestCover,
    materials.bronze,
    [[-.52, .42], [-.44, .72], [-.18, .83], [.36, .74], [.52, .44], [.42, -.38], [.15, -.58], [-.31, -.5], [-.5, -.18]],
    [0, .03, .58],
    .11,
  );
  chestPlate.rotation.z = -.025;
  for (let row = 0; row < 4; row++) {
    const y = .44 - row * .24;
    const width = .48 - row * .035;
    makePlate(
      chestCover,
      row % 2 ? materials.bronzeLight : materials.darkPatina,
      [[-width, .09], [-width * .82, .21], [width * .73, .18], [width, .02], [width * .72, -.12], [-width * .78, -.13]],
      [0, y, .72],
      .035,
    );
  }
  addRivets(chestCover, [[-.37, .56], [.35, .55], [-.36, .04], [.37, .02], [-.25, -.36], [.25, -.35]], materials.bronzeLight, .027, .78);

  // The Maker's inherited left-shoulder plate is visibly asymmetric and
  // twice fitted. This is the anatomical left (positive local X, facing +Z).
  makePlate(body, materials.bronzeLight,
    [[-.2, .22], [-.14, .39], [.19, .31], [.24, -.11], [.04, -.28], [-.2, -.12]],
    [.63, .65, .18], .09, [0, 0, -.17]);
  makePlate(body, materials.bronze,
    [[-.13, .2], [-.08, .31], [.18, .22], [.19, -.11], [-.01, -.21], [-.14, -.1]],
    [.7, .65, .27], .055, [0, 0, -.06]);
  segment(body, materials.ironEdge, .035, [.74, .84, .16], [.68, .39, .18], .045);
  addRivets(body, [[.52, .8], [.76, .68], [.56, .47]], materials.brass, .035, .31);
  makePlate(body, materials.bronze,
    [[-.18, .18], [-.12, .34], [.14, .28], [.18, -.09], [.02, -.2], [-.15, -.08]],
    [-.63, .65, .18], .08, [0, 0, .12]);
  addRivets(body, [[-.72, .77], [-.55, .53]], materials.bronzeLight, .027, .26);

  // A short plated tail keeps the rear contour compact; these are not flight feathers.
  for (let index = -1; index <= 1; index++) {
    const tail = addMesh(body, unitCone, index === 0 ? materials.bronze : materials.patina,
      [index * .17, -.5, -.74], [.15, .26, .13], [-.74, index * .08, 0]);
    tail.castShadow = true;
  }

  const neck = new THREE.Group();
  neck.position.set(0, .65, -.03);
  body.add(neck);
  for (let index = 0; index < 4; index++) {
    const y = .12 + index * .2;
    const width = .37 - index * .025;
    ball(neck, index % 2 ? materials.patina : materials.bronze, [0, y, .02 + index * .035], [width, .19, .38 - index * .025]);
    ring(neck, materials.bronzeLight, [0, y - .075, .035 + index * .035], [width * .77, .07, .82], [0, 0, 0]);
  }

  const head = new THREE.Group();
  head.position.set(0, .79, .13);
  neck.add(head);
  ball(head, materials.darkPatina, [0, .1, 0], [.49, .39, .47]);
  ball(head, materials.bronze, [0, .08, .31], [.38, .31, .25]);
  for (let index = 0; index < 4; index++) {
    const z = -.29 + index * .13;
    makePlate(head, index % 2 ? materials.patina : materials.bronzeLight,
      [[-.25, .07], [-.2, .27], [0, .44], [.2, .27], [.25, .07], [.12, -.02], [-.14, -.02]],
      [0, .17 + index * .015, z], .045, [0, 0, index % 2 ? .05 : -.05]);
    addRivets(head, [[-.15, .25], [.15, .25]], materials.bronze, .022, z + .055);
  }

  // A deep, hooked bill is built along the head's forward axis (+Z).
  const billProfile = new THREE.Shape();
  billProfile.moveTo(-.12, .13);
  billProfile.quadraticCurveTo(.23, .19, .57, .04);
  billProfile.quadraticCurveTo(.88, -.1, .91, -.36);
  billProfile.quadraticCurveTo(.9, -.51, .76, -.59);
  billProfile.quadraticCurveTo(.79, -.38, .55, -.28);
  billProfile.lineTo(.13, -.22);
  billProfile.lineTo(-.13, -.08);
  billProfile.closePath();
  const billGeometry = new THREE.ExtrudeGeometry(billProfile, {
    depth: .34, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: .045, bevelThickness: .05,
  });
  addMesh(head, billGeometry, materials.bronzeLight, [-.17, .0, .35]);
  const lowerJaw = new THREE.Group();
  lowerJaw.position.set(0, -.18, .36);
  head.add(lowerJaw);
  const jawProfile = new THREE.Shape();
  jawProfile.moveTo(-.12, .05);
  jawProfile.lineTo(.12, .1);
  jawProfile.lineTo(.65, .05);
  jawProfile.quadraticCurveTo(.76, -.02, .58, -.15);
  jawProfile.lineTo(.17, -.13);
  jawProfile.closePath();
  addMesh(lowerJaw, new THREE.ExtrudeGeometry(jawProfile, {
    depth: .27, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: .025, bevelThickness: .03,
  }), materials.ironEdge, [-.12, -.03, .02]);
  segment(head, materials.darkPatina, .035, [-.2, -.18, .58], [.2, -.18, .58], .04);

  // The optic housing remains dark in Maker and Mechanic layers.
  ring(head, materials.bronzeLight, [.3, .13, .43], [.19, .19, 1], [0, 0, 0]);
  ball(head, materials.darkLens, [.3, .13, .458], [.135, .135, .045]);
  const builderEye = ball(head, materials.amberLens, [.3, .13, .506], [.087, .087, .035]);
  builderEye.visible = false;

  const wings = [];
  for (const side of [-1, 1]) {
    const wing = new THREE.Group();
    wing.position.set(side * .64, .45, -.12);
    wing.rotation.z = side * .13;
    body.add(wing);
    ball(wing, materials.iron, [side * .08, -.13, -.02], [.29, .48, .24]);
    makePlate(wing, materials.patina,
      [[-.24, .15], [-.22, -.05], [-.14, -.43], [0, -.57], [.2, -.43], [.26, -.1], [.17, .18]],
      [side * .08, -.13, .16], .055, [0, 0, side * .05]);
    for (let index = 0; index < 3; index++) {
      const feather = addMesh(wing, unitCone, index % 2 ? materials.bronze : materials.bronzeLight,
        [side * (.03 + index * .08), -.28 - index * .07, .17],
        [.08, .31, .08], [0, 0, side * -.16]);
      feather.castShadow = true;
    }
    ring(wing, materials.bronzeLight, [side * .09, -.03, .24], [.13, .13, .75], [0, 0, 0]);
    wings.push({ group: wing, side });
  }

  // Mechanic-era iron braces and brass bearings are a distinct later overlay.
  const mechanicLayer = new THREE.Group();
  model.add(mechanicLayer);
  const shoulderStop = segment(mechanicLayer, materials.ironEdge, .065, [.7, .92, .2], [.7, .38, .22], .07);
  ring(mechanicLayer, materials.brass, [.7, .67, .26], [.16, .16, .85], [0, 0, 0]);
  for (const side of [-1, 1]) {
    segment(mechanicLayer, materials.iron, .095, [side * .64, -.47, .1], [side * .74, -.91, .17], .1);
    segment(mechanicLayer, materials.brass, .045, [side * .74, -.51, .19], [side * .74, -.89, .24], .055);
    ring(mechanicLayer, materials.brass, [side * .7, -1.16, .31], [.17, .17, .9], [Math.PI / 2, 0, 0]);
    segment(mechanicLayer, materials.ironEdge, .035, [side * .73, -1.36, -.18], [side * .73, -1.78, -.08], .045);
  }
  for (let index = 0; index < 3; index++) {
    ring(mechanicLayer, materials.brass, [0, -.5 + index * .18, -.68], [.48, .12, .65], [Math.PI / 2, 0, 0]);
  }
  shoulderStop.name = 'limited anatomical left shoulder stop';

  // The Builder adds finite power at the chest and separate processing behind the eyes.
  const builderLayer = new THREE.Group();
  model.add(builderLayer);
  const heart = new THREE.Group();
  heart.position.set(0, -.04, .77);
  builderLayer.add(heart);
  ball(heart, materials.iron, [0, 0, 0], [.36, .48, .12]);
  for (let index = 0; index < 4; index++) {
    const y = -.29 + index * .19;
    ball(heart, materials.ceramic, [0, y, .1], [.2, .075, .1]);
    ring(heart, materials.brass, [0, y, .16], [.21, .06, .7], [0, 0, 0]);
  }
  segment(heart, materials.wire, .025, [-.23, .23, .09], [-.38, .5, .02], .025);
  segment(heart, materials.wire, .025, [.23, -.19, .09], [.42, -.53, .03], .025);

  const mind = new THREE.Group();
  mind.position.set(0, 1.7, -.13);
  body.add(mind);
  ball(mind, materials.iron, [0, 0, 0], [.27, .21, .22]);
  for (let index = -1; index <= 1; index++) {
    segment(mind, materials.brass, .018,
      [index * .11, -.14, .17], [index * .11, .14, .17], .018);
  }
  segment(mind, materials.wire, .022, [0, 0, -.18], [0, -.2, -.46], .022);
  segment(builderLayer, materials.wire, .018, [-.4, .5, -.12], [-.57, .95, -.1], .018);
  heart.visible = false;
  mind.visible = false;
  builderLayer.visible = false;

  const legs = [];
  const feet = [];
  for (const side of [-1, 1]) {
    const leg = {
      side,
      upper: segment(model, materials.patina, .18, [side * .5, -.5, 0], [side * .6, -1, .2], .17),
      lower: segment(model, materials.darkPatina, .12, [side * .6, -1, .2], [side * .68, -1.8, -.18], .12),
      tarsus: segment(model, materials.bronze, .105, [side * .68, -1.8, -.18], [side * .7, -2.3, .16], .1),
      hip: ball(model, materials.darkPatina, [side * .5, -.55, 0], [.24, .22, .24]),
      knee: ball(model, materials.bronzeLight, [side * .6, -1.05, .2], [.18, .17, .2]),
      hock: ball(model, materials.ironEdge, [side * .68, -1.8, -.18], [.15, .16, .16]),
      ankle: ball(model, materials.brass, [side * .7, -2.3, .16], [.13, .12, .14]),
    };
    legs.push(leg);

    const foot = new THREE.Group();
    foot.position.set(side * .7, floorY, .12);
    model.add(foot);
    ball(foot, materials.darkPatina, [0, .08, -.02], [.25, .1, .29]);
    const claws = [];
    for (let toe = -1; toe <= 1; toe++) {
      const spread = toe * .17;
      const start = new THREE.Vector3(spread * .72, .1, .07);
      const end = new THREE.Vector3(spread, .075, .42 + (toe === 0 ? .09 : 0));
      const toeBone = segment(foot, materials.ironEdge, toe === 0 ? .075 : .062, start, end, .065);
      const claw = segment(foot, materials.bronzeLight, .042, end, [spread * 1.12, .035, end.z + .22], .038);
      claws.push({ toeBone, claw, side: toe });
      ball(foot, materials.brass, end.toArray(), [.075, .055, .075]);
    }
    const rearDigit = segment(foot, materials.bronze, .052, [0, .1, -.18], [0, .05, -.36], .05);
    feet.push({ group: foot, claws, rearDigit, side });
  }

  const markerPositions = {
    beak: new THREE.Vector3(.75, 1.08, .78),
    shoulder: new THREE.Vector3(.72, .65, .38),
    ankle: new THREE.Vector3(.7, -2.23, .34),
    heart: new THREE.Vector3(0, .05, .94),
    mind: new THREE.Vector3(0, 1.68, .08),
  };
  let currentEra = 'builder';
  let inspectionOpen = false;
  let yaw = .45;
  let pitch = 0;
  let targetYaw = yaw;
  let targetPitch = 0;
  let zoom = 9.5;
  let pointer = null;
  let lookYaw = 0;
  let lookPitch = 0;
  let targetLookYaw = 0;
  let targetLookPitch = 0;
  let reactionStarted = -Infinity;
  let frame = 0;
  let lastWidth = 0;
  let lastHeight = 0;
  const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('role', 'region');
  canvas.setAttribute('aria-label', 'Interactive procedural MurderBird study. Use arrow keys to rotate, plus and minus to zoom, Enter to trigger a brief reaction, and R to reset.');
  canvas.style.touchAction = 'none';

  function resize() {
    const width = container.clientWidth;
    const height = container.clientHeight;
    if (!width || !height || (width === lastWidth && height === lastHeight)) return;
    lastWidth = width;
    lastHeight = height;
    renderer.setSize(width, height);
    camera.aspect = width / height;
    camera.fov = width < 560 ? 37 : 34;
    camera.position.z = width < 560 ? 9.1 : 9.5;
    camera.updateProjectionMatrix();
  }

  function setEra(era) {
    currentEra = era;
    mechanicLayer.visible = era !== 'maker';
    builderLayer.visible = era === 'builder';
    builderEye.visible = era === 'builder';
    if (era !== 'builder') setInspection(false);
  }

  function setInspection(value) {
    inspectionOpen = Boolean(value && currentEra === 'builder');
    heart.visible = inspectionOpen;
    mind.visible = inspectionOpen;
    const target = inspectionOpen ? 1 : 0;
    chestCover.userData.openTarget = target;
    head.userData.openTarget = target;
  }

  function triggerReaction() {
    reactionStarted = performance.now();
  }

  function reset() {
    targetYaw = .45;
    targetPitch = 0;
    zoom = 9.5;
    targetLookYaw = 0;
    targetLookPitch = 0;
    reactionStarted = -Infinity;
  }

  const onPointerDown = event => {
    pointer = { x: event.clientX, y: event.clientY, yaw: targetYaw, pitch: targetPitch, moved: false };
    canvas.setPointerCapture(event.pointerId);
    canvas.focus({ preventScroll: true });
  };
  const onPointerMove = event => {
    if (!pointer) {
      const rect = canvas.getBoundingClientRect();
      targetLookYaw = THREE.MathUtils.clamp(((event.clientX - rect.left) / rect.width - .5) * .26, -.13, .13);
      targetLookPitch = THREE.MathUtils.clamp(((event.clientY - rect.top) / rect.height - .5) * -.11, -.055, .055);
      return;
    }
    const dx = event.clientX - pointer.x;
    const dy = event.clientY - pointer.y;
    if (Math.abs(dx) + Math.abs(dy) > 4) pointer.moved = true;
    targetYaw = pointer.yaw + dx * .007;
    targetPitch = THREE.MathUtils.clamp(pointer.pitch + dy * .004, -.28, .28);
  };
  const onPointerUp = event => {
    if (pointer && !pointer.moved && event.pointerType !== 'touch') triggerReaction();
    pointer = null;
  };
  const onPointerCancel = () => { pointer = null; };
  const onPointerLeave = () => {
    if (!pointer) {
      targetLookYaw = 0;
      targetLookPitch = 0;
    }
  };
  const onWheel = event => {
    event.preventDefault();
    zoom = THREE.MathUtils.clamp(zoom + event.deltaY * .007, 7.7, 12.5);
  };
  const onKeyDown = event => {
    const step = motionQuery.matches ? .16 : .11;
    if (event.key === 'ArrowLeft') targetYaw -= step;
    else if (event.key === 'ArrowRight') targetYaw += step;
    else if (event.key === 'ArrowUp') targetPitch = THREE.MathUtils.clamp(targetPitch - step, -.28, .28);
    else if (event.key === 'ArrowDown') targetPitch = THREE.MathUtils.clamp(targetPitch + step, -.28, .28);
    else if (event.key === '+' || event.key === '=') zoom = Math.max(7.7, zoom - .7);
    else if (event.key === '-') zoom = Math.min(12.5, zoom + .7);
    else if (event.key.toLowerCase() === 'r') reset();
    else if (event.key === 'Enter') triggerReaction();
    else return;
    event.preventDefault();
  };
  canvas.addEventListener('pointerdown', onPointerDown);
  canvas.addEventListener('pointermove', onPointerMove);
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('pointercancel', onPointerCancel);
  canvas.addEventListener('pointerleave', onPointerLeave);
  canvas.addEventListener('wheel', onWheel, { passive: false });
  canvas.addEventListener('keydown', onKeyDown);

  const markerVector = new THREE.Vector3();
  function bodyPoint(x, y, z) {
    const point = new THREE.Vector3(x, y, z);
    point.applyEuler(body.rotation).add(body.position);
    return point;
  }
  function updateLeg(leg) {
    const side = leg.side;
    const hip = bodyPoint(side * .5, -.48, .03);
    const knee = new THREE.Vector3(
      side * .59 + body.position.x * .48,
      -1.08 + body.position.y * .32,
      .16 + body.position.z * .35,
    );
    const hock = new THREE.Vector3(
      side * .68 + body.position.x * .16,
      -1.79 + body.position.y * .12,
      -.2,
    );
    const ankle = new THREE.Vector3(side * .7, floorY + .18, .12);
    placeSegment(leg.upper, hip, knee, .19, .18);
    placeSegment(leg.lower, knee, hock, .125, .125);
    placeSegment(leg.tarsus, hock, ankle, .105, .1);
    leg.hip.position.copy(hip);
    leg.knee.position.copy(knee);
    leg.hock.position.copy(hock);
    leg.ankle.position.copy(ankle);
  }

  function animate(now) {
    frame = requestAnimationFrame(animate);
    const seconds = now * .001;
    yaw = THREE.MathUtils.lerp(yaw, targetYaw, motionQuery.matches ? 1 : .1);
    pitch = THREE.MathUtils.lerp(pitch, targetPitch, motionQuery.matches ? 1 : .1);
    lookYaw = THREE.MathUtils.lerp(lookYaw, targetLookYaw, motionQuery.matches ? .45 : .055);
    lookPitch = THREE.MathUtils.lerp(lookPitch, targetLookPitch, motionQuery.matches ? .45 : .055);
    model.rotation.set(pitch, yaw, 0);
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, zoom, motionQuery.matches ? 1 : .12);

    const progress = (now - reactionStarted) / 1550;
    const activeReaction = progress >= 0 && progress <= 1;
    const envelope = activeReaction ? Math.sin(progress * Math.PI) : 0;
    const shift = (motionQuery.matches ? 0 : Math.sin(seconds * .72) * .035) + envelope * .085;
    body.position.set(shift, envelope * .012, 0);
    body.rotation.z = envelope * -.028 + (motionQuery.matches ? 0 : Math.sin(seconds * .72) * .009);
    neck.rotation.x = lookPitch - envelope * .1;
    head.rotation.y = lookYaw + envelope * .12;
    head.rotation.x = -lookPitch * .35 - envelope * .04;

    const jawPulse = activeReaction && progress > .37 && progress < .63
      ? Math.sin(((progress - .37) / .26) * Math.PI) * .31
      : 0;
    lowerJaw.rotation.x = jawPulse;
    wings.forEach(({ group, side }) => { group.rotation.z = side * (.13 + envelope * .035); });
    feet.forEach(({ group, claws, side }) => {
      group.rotation.y = side * envelope * .012;
      claws.forEach(({ claw, side: toe }) => {
        claw.rotation.x = envelope * .03;
        claw.rotation.z = toe * envelope * .025;
      });
    });

    const coverTarget = inspectionOpen ? 1 : 0;
    chestCover.position.x = THREE.MathUtils.lerp(chestCover.position.x, coverTarget * .42, motionQuery.matches ? .28 : .08);
    chestCover.rotation.y = THREE.MathUtils.lerp(chestCover.rotation.y, coverTarget * -.58, motionQuery.matches ? .28 : .08);
    head.position.y = THREE.MathUtils.lerp(head.position.y, .79 + coverTarget * .14, motionQuery.matches ? .28 : .08);

    body.updateMatrix();
    legs.forEach(updateLeg);
    model.updateMatrixWorld(true);
    Object.entries(markerPositions).forEach(([id, position]) => {
      markerVector.copy(position).applyMatrix4(model.matrixWorld).project(camera);
      const inEra = (id !== 'heart' && id !== 'mind') || currentEra === 'builder';
      const visible = inEra
        && markerVector.z > -1 && markerVector.z < 1
        && markerVector.x > -.96 && markerVector.x < .96
        && markerVector.y > -.9 && markerVector.y < .9;
      updateMarker(id, (markerVector.x + 1) * .5 * lastWidth, (1 - markerVector.y) * .5 * lastHeight, visible);
    });
    renderer.render(scene, camera);
  }

  resize();
  setEra('builder');
  animate(0);

  return {
    supportsMarkers: true,
    resize,
    select() {},
    setEra,
    setSection: setInspection,
    react: triggerReaction,
    reset,
    destroy() {
      cancelAnimationFrame(frame);
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('pointercancel', onPointerCancel);
      canvas.removeEventListener('pointerleave', onPointerLeave);
      canvas.removeEventListener('wheel', onWheel);
      canvas.removeEventListener('keydown', onKeyDown);
      scene.traverse(object => {
        if (object.isMesh) object.geometry.dispose();
      });
      Object.values(materials).forEach(material => material.dispose());
      renderer.dispose();
      container.replaceChildren();
    },
  };
}