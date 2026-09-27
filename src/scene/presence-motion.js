import * as THREE from 'three';

// Metres; Y up, bird forward +Z. Motion is a kinematic production proposal.
// Each support foot is stored in world space. A swing is the only operation
// allowed to change that target; body travel and turning never move it.
const UP = new THREE.Vector3(0, 1, 0);
const clamp = THREE.MathUtils.clamp;
const smooth = t => t * t * (3 - 2 * t);
const angleDelta = (a, b) => Math.atan2(Math.sin(b - a), Math.cos(b - a));
const approach = (a, b, amount) => a + clamp(b - a, -amount, amount);

export function createPresenceMotion(model, nodes, rest) {
  model.updateMatrixWorld(true);
  const feet = ['left', 'right'].map(label => {
    const thigh = model.getObjectByName(label + '-thigh');
    const shin = model.getObjectByName(label + '-shin');
    const foot = model.getObjectByName(label + '-foot');
    const toes = model.getObjectByName(label + '-toes');
    if (!thigh || !shin || !foot || !toes || shin.parent !== thigh || foot.parent !== shin || toes.parent !== foot) throw new Error('Rigid leg hierarchy missing: ' + label);
    const origin = foot.getWorldPosition(new THREE.Vector3());
    const minY = new THREE.Box3().setFromObject(foot, true).min.y;
    const floorHeight = origin.y - minY + .002;
    const ideal = origin.clone(); ideal.y = floorHeight;
    return { label, thigh, shin, foot, toes, hipRest: thigh.position.clone(), upper: shin.position.clone(), lower: foot.position.clone(), toeRest: toes.rotation.clone(), ideal, position: ideal.clone(), from: ideal.clone(), to: ideal.clone(), yaw: 0, fromYaw: 0, toYaw: 0, phase: 1, swinging: false, plantedFrames: 0, steps: 0, solveError: 0, groundY: floorHeight };
  });
  let x = 0, z = -.25, yaw = 0, speed = 0, velocityX = 0, velocityZ = 0, yawVelocity = 0, time = 0, stride = 0;
  let nextFoot = 0, motionFrame = 0, distance = 0, settled = true, arrived = false, aligned = true;
  let pose = { load: 0, extension: 0, jaw: 0, gaze: 0, guard: 0, counter: 0 };
  let previousState = '', contact = false, contactPoint = new THREE.Vector3(), maxFootError = 0, reachDrop = 0, maxReachDrop = 0;
  const root = new THREE.Vector3(), q = new THREE.Quaternion(), inverse = new THREE.Quaternion();
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), d = new THREE.Vector3();
  const bounds = new THREE.Box3();
  const upperBill=model.getObjectByName('upper-bill');
  if(!upperBill)throw new Error('Dedicated bill contact assembly missing.');
  function leadingBillPoint(){let front=-Infinity;upperBill.traverse(o=>{if(!o.isMesh)return;const position=o.geometry.attributes.position;for(let i=0;i<position.count;i++){a.fromBufferAttribute(position,i).applyMatrix4(o.matrixWorld);if(a.z>front){front=a.z;contactPoint.copy(a);}}});return contactPoint;}
  for (const foot of feet) foot.position.z += z;

  function idealFoot(f, ahead = 0) {
    return f.ideal.clone().applyAxisAngle(UP, yaw + yawVelocity * ahead).add(new THREE.Vector3(x + Math.sin(yaw) * speed * ahead, 0, z + Math.cos(yaw) * speed * ahead));
  }
  function beginStep(index, target) {
    const f = feet[index];
    f.swinging = true; f.phase = 0; f.duration=clamp(.44-Math.max(0,speed-.28)*.32,.29,.44); f.from.copy(f.position); f.to.copy(target);
    f.to.y = f.groundY; f.fromYaw = f.yaw; f.toYaw = yaw + yawVelocity * .20;
    nextFoot = 1 - index;
  }
  function solveLeg(f, pelvisShift, lift) {
    f.thigh.position.copy(f.hipRest).sub(rest.body.position).applyEuler(nodes.body.rotation).add(nodes.body.position);
    f.thigh.quaternion.identity(); f.shin.quaternion.identity(); f.foot.quaternion.identity();
    model.updateMatrixWorld(true);
    // Solve in model coordinates. The knee bends toward the bird's front.
    const hip = f.thigh.position.clone();
    const target = model.worldToLocal(f.position.clone());
    const axis = target.clone().sub(hip);
    const upperLength = f.upper.length(), lowerLength = f.lower.length();
    const length = clamp(axis.length(), .05, upperLength + lowerLength - .001);
    axis.normalize();
    const along = (upperLength ** 2 - lowerLength ** 2 + length ** 2) / (2 * length);
    const height = Math.sqrt(Math.max(0, upperLength ** 2 - along ** 2));
    const bend = new THREE.Vector3(0, 0, 1).addScaledVector(axis, -axis.z).normalize();
    const knee = hip.clone().addScaledVector(axis, along).addScaledVector(bend, height);
    f.thigh.quaternion.setFromUnitVectors(f.upper.clone().normalize(), knee.clone().sub(hip).normalize());
    const lowerDirection = target.clone().sub(knee).applyQuaternion(inverse.copy(f.thigh.quaternion).invert()).normalize();
    f.shin.quaternion.setFromUnitVectors(f.lower.clone().normalize(), lowerDirection);
    model.updateMatrixWorld(true);
    f.foot.parent.getWorldQuaternion(inverse).invert();
    q.setFromAxisAngle(UP, f.yaw);
    q.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -.13 * lift));
    f.foot.quaternion.copy(inverse).multiply(q);
    f.toes.rotation.copy(f.toeRest); f.toes.rotation.x = .14 * lift;
    model.updateMatrixWorld(true);
    f.solveError = f.foot.getWorldPosition(a).distanceTo(f.position);
    maxFootError = Math.max(maxFootError, f.solveError);
  }
  function tick(dt, s) {
    // Pause freezes the actual pose, including a foot mid-step.
    if (s.paused && !s.inspectionRequested) dt = 0;
    dt = clamp(dt, 0, .1); time += dt; motionFrame++;
    const calm = s.reducedMotion || s.era !== 'builder';
    const stop = calm || s.inspectionRequested || s.inspection;
    const goal = s.goal || { x:x+Math.sin(yaw), z:z+Math.cos(yaw) };
    const dx = goal.x - x, dz = goal.z - z, remaining = Math.hypot(dx, dz);
    let desiredHeading = stop ? yaw : (remaining > .045 && s.speed > 0 ? Math.atan2(dx, dz) : (s.heading ?? yaw));
    const headingError = angleDelta(yaw, desiredHeading);
    const yawStep = stop ? 0 : clamp(headingError, -dt * .78, dt * .78);
    yawVelocity = dt ? yawStep / dt : 0; yaw += yawStep;
    const desiredSpeed = !stop && s.goal && remaining > .004 ? Math.min(s.speed || 0, Math.sqrt(Math.max(0, remaining - .002) * .72)) * Math.max(0, Math.cos(headingError) ** 5) * (Math.abs(headingError) < 1.2 ? 1 : 0) : 0;
    const wantedX=remaining?dx/remaining*desiredSpeed:0, wantedZ=remaining?dz/remaining*desiredSpeed:0;
    const changeX=wantedX-velocityX,changeZ=wantedZ-velocityZ,change=Math.hypot(changeX,changeZ);
    const acceleration=change?Math.min(1,dt*.65/change):0;
    velocityX+=changeX*acceleration;velocityZ+=changeZ*acceleration;
    speed=Math.hypot(velocityX,velocityZ);
    if(s.goal&&remaining<.006&&speed<.035){velocityX=0;velocityZ=0;speed=0;}
    x+=velocityX*dt;z+=velocityZ*dt;distance+=speed*dt;
    x = clamp(x, -1.6, 1.6); z = clamp(z, -.65, .75);
    const active = feet.find(f => f.swinging);
    if (active) {
      active.phase = Math.min(1, active.phase + dt / active.duration);
      const p = active.phase, t = smooth(p);
      active.position.lerpVectors(active.from, active.to, t);
      active.position.y = active.groundY + Math.sin(Math.PI * p) ** 1.35 * .105;
      active.yaw = active.fromYaw + angleDelta(active.fromYaw, active.toYaw) * t;
      if (p === 1) { active.swinging = false; active.steps++; stride++; }
    } else {
      const errors = feet.map(f => f.position.distanceTo(idealFoot(f)) + Math.abs(angleDelta(f.yaw, yaw)) * .23);
      // A stopping step places the foot beneath the pelvis before inspection.
      const threshold = stop || remaining < .065 || !s.speed ? .035 : .125;
      let index = nextFoot;
      if (errors[index] < threshold && errors[1 - index] > threshold) index = 1 - index;
      if (errors[index] > threshold && (!calm || errors[index] > .04)) beginStep(index, idealFoot(feet[index], stop ? 0 : .20));
    }
    const moving = speed > .012 || feet.some(f => f.swinging) || Math.abs(yawStep) > .0005;
    arrived = (!s.goal || remaining < .008) && speed < .04;
    aligned = s.heading == null || Math.abs(angleDelta(yaw, s.heading)) < .045;
    settled = !moving && feet.every(f => f.position.distanceTo(idealFoot(f)) < .045);
    const p = smooth(s.phase || 0), state = s.state;
    let load = 0, extension = 0, jaw = 0, guard = 0;
    if (!stop) {
      if (state === 'agitated') {load=.18*(s.agitation||0);guard=.22*(s.agitation||0);}
      if (state === 'warning') { load = p; jaw = .75 * p; guard = p; }
      if (state === 'strike') { load = 1 - .45 * p; extension = p; jaw = .75 * (1 - p); guard = 1; }
      if (state === 'contact') { load = .55; extension = 1; guard = 1; }
      if (state === 'recover' && s.actionKind === 'visitor') { extension = 1 - p; load = .55 * (1 - p); guard = 1 - p; }
      if (state === 'cage-test' && arrived && settled && aligned) { extension = Math.min(1, Math.min(p / .32, (1 - p) / .25)); load = extension * .27; guard = extension * .25; }
    }
    // Approach to new pose is bounded; interruption cannot pop joints to zero.
    const blend = 1 - Math.exp(-dt * (state === 'strike' ? 32 : 7));
    for (const [key, value] of Object.entries({ load, extension, jaw, guard })) pose[key] = THREE.MathUtils.lerp(pose[key], value, blend);
    if (state === 'contact') pose.extension = 1;
    const desiredGaze = stop ? 0 : clamp(angleDelta(yaw, Math.atan2((s.lookTarget?.x ?? x) - x, (s.lookTarget?.z ?? z + 3) - z)), -.6, .6);
    pose.gaze = THREE.MathUtils.lerp(pose.gaze, desiredGaze, 1 - Math.exp(-dt * 4));
    const swing = feet.find(f => f.swinging);
    const supportSide = swing ? (swing.label === 'left' ? -1 : 1) : 0;
    pose.counter = THREE.MathUtils.lerp(pose.counter, supportSide * .032, 1 - Math.exp(-dt * 5));
    const shift = new THREE.Vector3(pose.counter, -.065 - Math.min(speed,.72)*.065 - pose.load * .075, pose.extension * .12);
    model.position.set(x, 0, z); model.rotation.y = yaw;
    nodes.body.position.copy(rest.body.position).add(shift);
    nodes.body.rotation.x = pose.extension * .105 + pose.load * .035;
    nodes.body.rotation.z = -pose.counter * .55;
    nodes.neck.rotation.x = -pose.load * .13 + pose.extension * .08;
    nodes.neck.rotation.y = pose.gaze * .48;
    nodes.head.rotation.y = pose.gaze * .52 * (1 - pose.extension);
    nodes.head.rotation.x = -nodes.body.rotation.x * .65;
    nodes.jaw.rotation.x = -pose.jaw * .27;
    nodes['right-mantle'].rotation.x = -pose.guard * .24 - pose.counter;
    nodes['right-wing-shield'].rotation.x = pose.guard * .38;
    nodes['left-mantle'].rotation.x = pose.guard * .065 - pose.counter * .35;
    nodes['left-wing-shield'].rotation.x = pose.guard * .18;
    model.updateMatrixWorld(true);
    let neededDrop=0;
    for(const f of feet){
      const hip=f.hipRest.clone().sub(rest.body.position).applyEuler(nodes.body.rotation).add(nodes.body.position);
      const target=model.worldToLocal(f.position.clone());
      const horizontal=(hip.x-target.x)**2+(hip.z-target.z)**2;
      const reach=f.upper.length()+f.lower.length()-.012;
      neededDrop=Math.max(neededDrop,hip.y-target.y-Math.sqrt(Math.max(.01,reach*reach-horizontal)));
    }
    // A loaded pelvic saddle yields vertically before a support foot can slide.
    reachDrop=Math.max(Math.min(.12,neededDrop),reachDrop-dt*.10,0);maxReachDrop=Math.max(maxReachDrop,reachDrop);
    nodes.body.position.y-=reachDrop;
    for (const f of feet) solveLeg(f, shift, f.swinging ? Math.sin(Math.PI * f.phase) : 0);
    model.updateMatrixWorld(true);
    contact = false;
    // A bounded telescoping cervical linkage reaches the inside face of the
    // selected front rail only after the feet and heading have settled.
    if (pose.extension > .001 && ['strike','contact','recover','cage-test'].includes(state) && aligned && Math.abs(yaw) < .05) {
      const leading=leadingBillPoint();
      const clearance=2.079-leading.z;
      const worldAxis=new THREE.Vector3(0,0,1).transformDirection(nodes.neck.parent.matrixWorld);
      nodes.neck.position.z+=clamp(clearance/Math.max(.5,worldAxis.z),-.12,.48)*pose.extension;
      model.updateMatrixWorld(true);leadingBillPoint();
      const railX=s.lookTarget?.x??x;
      const radial=Math.hypot(contactPoint.x-railX,contactPoint.z-2.1);
      contact=Math.abs(radial-.021)<.008&&(state==='contact'||state==='cage-test');
    }
    if(stop)settled=settled&&pose.extension<.003&&pose.load<.003&&Math.abs(pose.counter)<.003;
    previousState = state;
  }
  return {
    tick,
    feedback: () => ({ arrived, settled, aligned, contact }),
    metrics() {
      model.updateMatrixWorld(true);
      return { root: { x, z, yaw, speed }, distance, steps: stride, time, motionFrame, settled, arrived, aligned, contact, contactPoint: contactPoint.toArray(), pose: { ...pose }, maxFootError, reachDrop, maxReachDrop, feet: feet.map(f => ({ side: f.label, target: f.position.toArray(), actual: f.foot.getWorldPosition(new THREE.Vector3()).toArray(), swinging: f.swinging, phase: f.phase, yaw: f.yaw, steps: f.steps, solveError: f.solveError, groundMin: new THREE.Box3().setFromObject(f.foot, true).min.y })), bodyBounds: new THREE.Box3().setFromObject(model, true), headBounds: new THREE.Box3().setFromObject(nodes.head, true) };
    },
  };
}
