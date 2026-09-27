import * as THREE from 'three';

const UP = new THREE.Vector3(0, 1, 0);
const clamp = THREE.MathUtils.clamp;

/** Era-specific, explicitly reconstructed motion systems for the shared bird rig. */
export function createEraMechanisms({ scene, model, nodes, rest }) {
  const madeGeometry = new Set();
  const madeMaterial = new Set();
  const root = model.getObjectByName('murderbird') || model;
  const body = nodes.body;
  const find=name=>nodes[name]||model.getObjectByName(name);
  const eraGroups = Object.fromEntries(['maker', 'mechanic', 'builder'].map(era => {
    const group = new THREE.Group();
    group.name = `era-${era}-mechanisms`;
    scene.add(group);
    return [era, group];
  }));
  const material = (name, color, metalness, roughness) => {
    const m = new THREE.MeshStandardMaterial({ name, color, metalness, roughness });
    madeMaterial.add(m);
    return m;
  };
  const wood = material('Maker control wood (proposed)', '#59422a', .08, .83);
  const rope = material('Maker tension line (proposed)', '#ad8d5e', .05, .9);
  const bronze = material('Era mechanism bronze (proposed)', '#927b55', .72, .48);
  const darkIron = material('Era mechanism iron (proposed)', '#29312e', .82, .43);
  const brass = material('Era mechanism brass (proposed)', '#b28c4e', .78, .38);
  const copper = material('Builder power distribution copper (proposed)', '#895b43', .76, .44);
  const ceramic = material('Builder actuator ceramic (proposed)', '#aaa28a', .31, .38);
  const black = material('Mechanism recess (proposed)', '#151a18', .48, .56);

  function geometry(g) { madeGeometry.add(g); return g; }
  function mesh(parent, name, g, m, position = [0, 0, 0]) {
    const o = new THREE.Mesh(geometry(g), m);
    o.name = name; o.position.set(...position); o.castShadow = true; o.receiveShadow = true;
    parent.add(o); return o;
  }
  function group(parent, name, position = [0, 0, 0]) {
    const g = new THREE.Group(); g.name = name; g.position.set(...position); parent.add(g); return g;
  }
  function cylinder(parent, name, radius, length, m, position, axis = 'y') {
    const o = mesh(parent, name, new THREE.CylinderGeometry(radius, radius, length, 12), m, position);
    if (axis === 'x') o.rotation.z = Math.PI / 2;
    if (axis === 'z') o.rotation.x = Math.PI / 2;
    return o;
  }
  function box(parent, name, size, m, position) {
    return mesh(parent, name, new THREE.BoxGeometry(...size), m, position);
  }
  function sphere(parent, name, radius, m, position) {
    return mesh(parent, name, new THREE.SphereGeometry(radius, 12, 8), m, position);
  }
  function dynamicSegment(parent, name, radius, m) {
    const o = mesh(parent, name, new THREE.CylinderGeometry(radius, radius, 1, 8), m);
    o.userData.link = true;
    return o;
  }
  function setSegment(o, from, to) {
    const delta = new THREE.Vector3().subVectors(to, from);
    const length = delta.length();
    o.visible = length > 1e-4;
    if (!o.visible) return;
    o.position.copy(from).addScaledVector(delta, .5);
    o.quaternion.setFromUnitVectors(UP, delta.multiplyScalar(1 / length));
    o.scale.y = length;
  }
  function worldPoint(object, target = new THREE.Vector3()) {
    return object.getWorldPosition(target);
  }
  function visibleAnchor(object) { return object?.visible ? object.getWorldPosition(new THREE.Vector3()) : undefined; }

  // Maker: stationary support and externally operated rods. No powered internals.
  // The control rig shares the bird root's local frame so its cradle and rods
  // remain registered when the whole encounter model is repositioned.
  const maker = eraGroups.maker;
  scene.remove(maker);
  root.add(maker);
  const makerBase = box(maker, 'maker-wide-floor-base', [.94, .10, .76], wood, [0, .055, -.49]);
  for (const x of [-.37, .37]) for (const z of [-.75, -.23]) {
    const foot = box(maker, 'maker-base-foot', [.12, .06, .12], darkIron, [x, .035, z]);
    foot.rotation.z = x * .12;
  }
  // Cradle is attached to the root frame; its post endpoint is updated to the actual pelvis.
  const cradle = box(maker, 'maker-pelvic-cradle', [.62, .085, .25], darkIron, [0, 0, 0]);
  const supportPost = dynamicSegment(maker, 'maker-pelvis-support-post', .048, darkIron);
  const supportBraceL = dynamicSegment(maker, 'maker-support-brace-left', .023, bronze);
  const supportBraceR = dynamicSegment(maker, 'maker-support-brace-right', .023, bronze);
  const postBase = new THREE.Vector3(0, .11, -.55);
  const braceBaseL = new THREE.Vector3(-.34, .10, -.52);
  const braceBaseR = new THREE.Vector3(.34, .10, -.52);
  const controls = group(maker, 'maker-external-control-rack', [-1.1, .24, .2]);
  box(controls, 'maker-control-console', [.96, .12, .18], wood, [0, 0, 0]);
  box(controls, 'maker-control-stand', [.72, .16, .10], darkIron, [0, -.16, .03]);
  const leverInputs = ['leg', 'wing', 'tail', 'neck', 'jaw'];
  const leverNodes = [];
  for (let i = 0; i < leverInputs.length; i++) {
    const x = (i - 2) * .18;
    const lever = group(controls, `maker-lever-${leverInputs[i]}`, [x, .075, -.015]);
    cylinder(lever, `maker-lever-pivot-${leverInputs[i]}`, .035, .055, brass, [0, 0, 0], 'x');
    cylinder(lever, `maker-lever-arm-${leverInputs[i]}`, .012, .22, bronze, [0, .11, 0]);
    sphere(lever, `maker-lever-handle-${leverInputs[i]}`, .026, wood, [0, .22, 0]);
    leverNodes.push(lever);
  }
  const makerTargets = ['left-foot', 'right-mantle', 'compact-articulated-tail', 'neck', 'jaw'];
  const controlOffsets=[[.065,.015,.045],[-.095,-.10,.10],[-.07,0,-.16],[-.16,.06,.02],[-.18,-.06,.20]];
  const makerLines = makerTargets.map((target, i) => ({
    target,
    first: dynamicSegment(maker, `maker-control-line-${leverInputs[i]}-outer`, .009, rope),
    second: dynamicSegment(maker, `maker-control-rod-${leverInputs[i]}-joint`, .013, bronze),
    guidePost: dynamicSegment(maker, `maker-guide-support-${leverInputs[i]}`, .014, darkIron),
    pulley:sphere(maker,`maker-guide-pulley-${leverInputs[i]}`,.025,brass,[0,0,0]),
    attachment:sphere(maker,`maker-joint-attachment-${leverInputs[i]}`,.026,brass,[0,0,0]),
    guide: new THREE.Vector3(),
    from: new THREE.Vector3(),
    end: new THREE.Vector3(),
  }));

  // A short, hinged rear feather plate keeps the same compact bird outline in every era.
  const tail = group(body, 'compact-articulated-tail', [0, .20, -.31]);
  for (let i = 0; i < 3; i++) {
    const plate = box(tail, `short-tail-plate-${i + 1}`, [.16 - i * .025, .045, .15],
      i === 1 ? bronze : darkIron, [0, -.012 * i, -.07 - i * .043]);
    plate.rotation.x = -.11;
  }

  // Mechanic: wound spring -> reduction pair -> cross-shaft -> articulated hip cranks.
  const mechanic = eraGroups.mechanic;
  const gearbox = group(body, 'mechanic-lower-transmission');
  const spring = group(gearbox, 'mechanic-mainspring-barrel', [-.17, .08, .035]);
  const springShell=cylinder(spring, 'mainspring-drum', .115, .20, darkIron, [0, 0, 0], 'x');
  const springCaps=[];
  for (const x of [-.085, .085]) springCaps.push(cylinder(spring, 'mainspring-end-cap', .12, .018, brass, [x, 0, 0], 'x'));
  const helixPoints = [];
  for (let i = 0; i <= 112; i++) {
    const t = i / 112;
    const a = t * Math.PI * 10,r=.018+t*.084;
    helixPoints.push(new THREE.Vector3(-.04, Math.cos(a) * r, Math.sin(a) * r));
  }
  const springCurve = new THREE.CatmullRomCurve3(helixPoints);
  mesh(spring, 'visible-wound-mainspring', new THREE.TubeGeometry(springCurve, 120, .008, 6, false), brass);
  const gear1 = makeGear(gearbox, 'mechanic-reduction-driver', .095, 12, [-.36, .08, .035], bronze);
  const gear2 = makeGear(gearbox, 'mechanic-reduction-follower', .145, 18, [-.36, -.16, .035], brass);
  cylinder(gearbox,'mechanic-spring-arbor',.028,.28,darkIron,[-.25,.08,.035],'x');
  cylinder(gearbox, 'mechanic-cross-shaft', .035, .76, darkIron, [0, -.16, .035], 'x');
  cylinder(gearbox, 'mechanic-cross-shaft-left-hub', .074, .055, brass, [-.36, -.16, .035], 'x');
  cylinder(gearbox, 'mechanic-cross-shaft-right-hub', .074, .055, brass, [.36, -.16, .035], 'x');
  const sequencingCam=group(gearbox,'mechanic-sequencing-cam',[-.43,-.16,.035]);
  cylinder(sequencingCam,'mechanic-cam-eccentric-lobe',.082,.045,bronze,[0,.035,0],'x');
  cylinder(sequencingCam,'mechanic-cam-hub',.027,.08,darkIron,[0,0,0],'x');
  const mechanicLinks = ['left', 'right'].map((side, i) => ({
    side,
    crank: dynamicSegment(mechanic, `mechanic-${side}-crank-link`, .021, brass),
    pin: sphere(mechanic, `mechanic-${side}-crank-pin`, .033, bronze, [0, 0, 0]),
    load: dynamicSegment(mechanic, `mechanic-${side}-knee-link`, .015, darkIron),
    thigh: find(side + '-thigh'),
    shin: find(side + '-shin'),
    sign: i === 0 ? 1 : -1,
  }));

  // Builder: existing story power/processing nodes feed visible distribution and link actuators.
  const builder = eraGroups.builder;
  const distribution = group(body, 'builder-power-distribution-manifold', [-.22, -.06, .15]);
  box(distribution, 'builder-sealed-bus-case', [.20, .14, .29], darkIron, [0, 0, 0]);
  box(distribution, 'builder-copper-bus-cover', [.055, .105, .24], copper, [-.105, .005, 0]);
  for (const z of [-.08, 0, .08]) cylinder(distribution, 'builder-bus-terminal', .018, .09, brass, [.09, 0, z], 'x');
  const builderBranches = ['left', 'right'].map((side, i) => {
    const sign = i === 0 ? 1 : -1;
    const thigh = find(side + '-thigh');
    const shin = find(side + '-shin');
    const housing = dynamicSegment(builder, `builder-${side}-linear-actuator-sleeve`, .044, ceramic);
    const piston = dynamicSegment(builder, `builder-${side}-actuator-rod`, .018, copper);
    const conduitOuter = [dynamicSegment(builder, `builder-${side}-power-conduit-a`, .022, darkIron), dynamicSegment(builder, `builder-${side}-power-conduit-b`, .022, darkIron)];
    const conduitInner = dynamicSegment(builder, `builder-${side}-copper-conduit`, .008, copper);
    return { side, sign, thigh, shin, housing, piston, conduitOuter, conduitInner };
  });
  const shoulderActuator = {
    housing: dynamicSegment(builder, 'builder-right-shoulder-actuator', .043, ceramic),
    rod: dynamicSegment(builder, 'builder-right-shoulder-actuator-rod', .017, copper),
    conduit: dynamicSegment(builder, 'builder-shoulder-power-conduit', .020, darkIron),
  };
  const manifoldLink = dynamicSegment(builder, 'builder-core-to-distribution-conduit', .027, darkIron);
  const manifoldCopper = dynamicSegment(builder, 'builder-distribution-copper-run', .009, copper);
  const builderAnchor = new THREE.Vector3();
  let era = 'builder';
  let tickCount = 0;
  let last = { maker: false, mechanic: false, builder: true };
  const tempA = new THREE.Vector3(), tempB = new THREE.Vector3(), tempC = new THREE.Vector3(), tempD = new THREE.Vector3();

  function makeGear(parent, name, radius, teeth, position, mat) {
    const g = group(parent, name, position);
    const disk = cylinder(g, `${name}-wheel`, radius * .84, .045, mat, [0, 0, 0], 'x');
    for (let i = 0; i < teeth; i++) {
      const a = i * Math.PI * 2 / teeth;
      const tooth = box(g, `${name}-tooth`, [.05, radius * .28, .045], darkIron,
        [0, Math.cos(a) * radius, Math.sin(a) * radius]);
      tooth.rotation.x = a;
    }
    cylinder(g, `${name}-hub`, radius * .22, .075, brass, [0, 0, 0], 'x');
    g.userData.disk = disk;
    return g;
  }

  function makeTailArticulation(value) {
    tail.rotation.x = -.28 * clamp(value || 0, 0, 1);
  }

  function setEra(value) {
    era = ['maker', 'mechanic', 'builder'].includes(value) ? value : 'builder';
    for (const [key, group] of Object.entries(eraGroups)) group.visible = key === era;
    maker.visible = era === 'maker';
    gearbox.visible = era === 'mechanic';
    distribution.visible = era === 'builder';
    tail.visible = true;
    last = { maker: maker.visible, mechanic: mechanic.visible && gearbox.visible, builder: builder.visible && distribution.visible };
  }

  function tick(dt, s = {}, motionMetrics = {}, inspection = {}) {
    tickCount++;
    const art = motionMetrics.actualArticulation || s.articulation || {};
    makeTailArticulation(art.tail);
    // Maintain the Maker's rigid support and route each external control to a named live joint.
    model.updateMatrixWorld(true);
    const pelvis = worldPoint(body, tempA);
    const pelvisLocal = root.worldToLocal(pelvis.clone());
    cradle.position.copy(pelvisLocal).add(new THREE.Vector3(0, -.035, 0));
    setSegment(supportPost, postBase, pelvisLocal);
    setSegment(supportBraceL, braceBaseL, tempB.copy(pelvisLocal).add(tempC.set(-.29, -.02, 0)));
    setSegment(supportBraceR, braceBaseR, tempB.copy(pelvisLocal).add(tempC.set(.29, -.02, 0)));
    for (let i = 0; i < makerLines.length; i++) {
      const line = makerLines[i];
      const amount = clamp(art[leverInputs[i]] || 0, 0, 1);
      leverNodes[i].rotation.z = -.55 * amount;
      const target = find(line.target);
      if (!target) { line.first.visible = false; line.second.visible = false; continue; }
      model.updateMatrixWorld(true);
      const end = root.worldToLocal(target.localToWorld(line.end.set(...controlOffsets[i])));
      const side = end.x >= 0 ? 1 : -1;
      line.from.copy(root.worldToLocal(leverNodes[i].localToWorld(tempD.set(0,.19,0))));
      if(!line.guideReady&&era==='maker'){line.guide.set(side*.67,end.y+.07,-.55);line.guideReady=true;}
      line.pulley.position.copy(line.guide);line.attachment.position.copy(end);
      setSegment(line.guidePost,tempC.set(line.guide.x,.07,line.guide.z),line.guide);
      setSegment(line.first, line.from, line.guide);
      setSegment(line.second, line.guide, end);
    }

    // Mechanic gear train and cranks follow its actual constrained gait phase.
    const phase = Number.isFinite(motionMetrics.mechanicalPhase) ? motionMetrics.mechanicalPhase : 0;
    const angle = Number.isFinite(motionMetrics.camAngle) ? motionMetrics.camAngle : phase * Math.PI * 2;
    gear1.rotation.x = -angle*1.5;
    gear2.rotation.x = angle+Math.PI/18;
    spring.rotation.x = -angle*1.5;
    sequencingCam.rotation.x=angle;
    springShell.visible=inspection.open<.2;springCaps[0].visible=inspection.open<.2;
    for (const link of mechanicLinks) {
      model.updateMatrixWorld(true);
      const knee = worldPoint(link.shin, tempB);
      const spindleLocal=new THREE.Vector3(link.sign*.4,-.16,.035);
      const crankBase=body.localToWorld(spindleLocal.clone());
      const pinLocal=spindleLocal.clone();
      pinLocal.y+=Math.cos(angle+(link.sign<0?Math.PI:0))*.067;
      pinLocal.z+=Math.sin(angle+(link.sign<0?Math.PI:0))*.067;
      body.localToWorld(pinLocal);
      link.pin.position.copy(pinLocal);
      setSegment(link.crank,crankBase,pinLocal);
      setSegment(link.load,pinLocal,knee);
    }

    // Builder bus starts at the actual retained core; branch actuators terminate at actual leg/wing groups.
    model.updateMatrixWorld(true);
    const core = nodes['power-core'];
    const source = worldPoint(core, builderAnchor);
    const lateral=new THREE.Vector3(1,0,0).transformDirection(body.matrixWorld);
    const manifoldWorld = body.localToWorld(tempA.set(-.22, -.06, .15)).clone();
    setSegment(manifoldLink, source, manifoldWorld);
    setSegment(manifoldCopper, source.clone().addScaledVector(lateral,-.028), manifoldWorld.clone().addScaledVector(lateral,-.028));
    for (const actuator of builderBranches) {
      model.updateMatrixWorld(true);
      const hip = worldPoint(actuator.thigh, tempA);
      const knee = worldPoint(actuator.shin, tempB);
      const mid = hip.clone().lerp(knee, .58);
      setSegment(actuator.housing, hip, mid);
      setSegment(actuator.piston, mid, knee);
      const sideRoute = mid.clone().addScaledVector(lateral,actuator.sign*.16);
      const sourceRoute = manifoldWorld.clone().addScaledVector(lateral,actuator.sign*.36);
      setSegment(actuator.conduitOuter[0], source, sourceRoute);
      setSegment(actuator.conduitOuter[1], sourceRoute, sideRoute);
      setSegment(actuator.conduitInner, sideRoute.clone().addScaledVector(lateral,actuator.sign*.025), hip);
    }
    const shoulder = worldPoint(nodes['right-mantle'], tempC);
    const elbow = worldPoint(nodes['right-wing-shield'], tempD);
    const shoulderMid = shoulder.clone().lerp(elbow, .56);
    setSegment(shoulderActuator.housing, shoulder, shoulderMid);
    setSegment(shoulderActuator.rod, shoulderMid, elbow);
    setSegment(shoulderActuator.conduit, manifoldWorld, shoulder);

    // Inspection may separate the body; attached mechanism groups remain with their assemblies,
    // while world-linked conduits keep endpoints updated rather than floating free.
    // Endpoints are refreshed from the actual rig every frame; no cumulative
    // inspection offset is applied to these world-space links.
  }

  function getAnchor(id) {
    if (era === 'maker') {
      if (id === 'drive') return controls.getWorldPosition(new THREE.Vector3());
      return undefined;
    }
    if (era === 'mechanic') {
      if (id === 'drive') return gear1.getWorldPosition(new THREE.Vector3());
      if (id === 'power') return spring.getWorldPosition(new THREE.Vector3());
      return undefined;
    }
    if (id === 'drive') return body.localToWorld(new THREE.Vector3(-.22, -.06, .15));
    if (id === 'power') return visibleAnchor(nodes['power-core']);
    if (id === 'mind') return visibleAnchor(nodes.processing);
    return undefined;
  }

  function getPart(id) {
    if(era==='maker')return id==='drive'?controls:undefined;
    if(era==='mechanic')return id==='drive'?gearbox:id==='power'?spring:undefined;
    return id==='drive'?distribution:id==='power'?nodes['power-core']:id==='mind'?nodes.processing:undefined;
  }

  function metrics() {
    return {
      era, tickCount, visible: { ...last },
      anchors: ['drive', 'power', 'mind'].map(id => ({ id, available: Boolean(getAnchor(id)) })),
      externalControlTargets: makerLines.map(line => line.target),
      mechanicTargets: mechanicLinks.map(link => `${link.side}-thigh/${link.side}-shin`),
      builderTargets: ['left-thigh/left-shin', 'right-thigh/right-shin', 'right-mantle/right-wing-shield'],
    };
  }

  function dispose() {
    scene.remove(...Object.values(eraGroups));
    root.remove(maker);
    body.remove(tail, distribution, gearbox);
    for (const g of madeGeometry) g.dispose();
    for (const m of madeMaterial) m.dispose();
  }

  setEra('builder');
  return { setEra, tick, metrics, getAnchor, getPart, dispose };
}
