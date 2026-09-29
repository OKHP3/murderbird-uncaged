import * as THREE from 'three';
import { solveTransverseLeg } from './rigid-leg-kinematics.js';
import { createCervicalArticulation } from './cervical-articulation.js';

// Metres; Y up, bird forward +Z. Motion is a kinematic production proposal.
// Each support foot is stored in world space. A swing is the only operation
// allowed to change that target; body travel and turning never move it.
const UP = new THREE.Vector3(0, 1, 0);
const clamp = THREE.MathUtils.clamp;
const smooth = t => t * t * (3 - 2 * t);
const angleDelta = (a, b) => Math.atan2(Math.sin(b - a), Math.cos(b - a));
const approach = (a, b, amount) => a + clamp(b - a, -amount, amount);
const MAX_CONTACT_PITCH = .65;
const RAIL_INNER_Z = 2.1 - .021;
const attackHoldRelease = (phase, start, attackEnd, releaseStart, end) => {
  const attack = smooth(clamp((phase - start) / (attackEnd - start), 0, 1));
  const release = 1 - smooth(clamp((phase - releaseStart) / (end - releaseStart), 0, 1));
  return attack * release;
};

function cageFamilyProfile(family, phase) {
  const p = clamp(phase, 0, 1);
  if (family === 'edge-probe') {
    const envelope = attackHoldRelease(p, .10, .27, .46, .59);
    return { envelope, load: .24 * envelope, guard: .20 * envelope, jaw: .12 * envelope };
  }
  if (family === 'seam-rattle') {
    const envelope = Math.max(
      attackHoldRelease(p, .035, .10, .20, .265),
      attackHoldRelease(p, .365, .43, .53, .595),
      attackHoldRelease(p, .695, .76, .86, .925),
    );
    return { envelope, load: .22 * envelope, guard: .18 * envelope, jaw: .04 * envelope };
  }
  // Rail pressing approaches steadily, holds pressure, then eases off.
  const approach = smooth(clamp(p / .30, 0, 1));
  const release = 1 - smooth(clamp((p - .72) / .28, 0, 1));
  const envelope = approach * release;
  return { envelope, load: .42 * envelope, guard: .46 * envelope, jaw: 0 };
}

export function createEraMotion(model, nodes, rest) {
  model.updateMatrixWorld(true);
  const cervical = createCervicalArticulation(model, nodes, rest);
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
    const digits = [1, 2, 3].flatMap(digit => ['proximal', 'distal'].map(segment => {
      const node = model.getObjectByName(`${label}-digit-${digit}-${segment}`);
      return node ? { node, rest: node.rotation.clone(), segment, weight: [.82, 1, .88][digit - 1] } : null;
    })).filter(Boolean);
    return { label, thigh, shin, foot, toes, digits, manualLift: 0, hipRest: thigh.position.clone(), upper: shin.position.clone(), lower: foot.position.clone(), toeRest: toes.rotation.clone(), ideal, position: ideal.clone(), from: ideal.clone(), to: ideal.clone(), yaw: 0, fromYaw: 0, toYaw: 0, phase: 1, swinging: false, plantedFrames: 0, steps: 0, solveError: 0, groundY: floorHeight };
  });
  let x = 0, z = -.25, yaw = 0, speed = 0, velocityX = 0, velocityZ = 0, yawVelocity = 0, time = 0, stride = 0;
  let nextFoot = 0, motionFrame = 0, distance = 0, settled = true, arrived = false, aligned = true;
  let pose = { load: 0, extension: 0, jaw: 0, gaze: 0, guard: 0, counter: 0 };
  let previousState = '', contact = false, contactPoint = new THREE.Vector3(), maxFootError = 0, reachDrop = 0, maxReachDrop = 0;
  let cagePose = null;
  let currentEra='builder', mechanicalCycle=null, camAngle=0, mechanicalPhase=0, mechanicalStage='disengaged';
  const articulation={leg:0,wing:0,tail:0,neck:0,jaw:0};
  let powerPose=null,powerAnchors=null;
  let clawCycle=null,clawPose=null;
  const root = new THREE.Vector3(), q = new THREE.Quaternion(), inverse = new THREE.Quaternion();
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Vector3(), d = new THREE.Vector3();
  const bounds = new THREE.Box3();
  const upperBill=model.getObjectByName('upper-bill');
  if(!upperBill)throw new Error('Dedicated bill contact assembly missing.');
  function leadingBillPoint(){let front=-Infinity;upperBill.traverse(o=>{if(!o.isMesh)return;const position=o.geometry.attributes.position;for(let i=0;i<position.count;i++){a.fromBufferAttribute(position,i).applyMatrix4(o.matrixWorld);if(a.z>front){front=a.z;contactPoint.copy(a);}}});return contactPoint;}
  // Sample actual triangle edges at the selected rail's centre plane. The new
  // forged bill has a broad face: its side vertices alone do not describe the
  // surface that touches a narrow bar between them.
  function billSurfaceAtRail(railX) {
    let front = -Infinity;
    const v = [new THREE.Vector3(), new THREE.Vector3(), new THREE.Vector3()];
    upperBill.traverse(o => {
      if (!o.isMesh) return;
      const position=o.geometry.attributes.position, index=o.geometry.index;
      const count=index?index.count:position.count;
      for(let i=0;i<count;i+=3){
        for(let j=0;j<3;j++)v[j].fromBufferAttribute(position,index?index.getX(i+j):i+j).applyMatrix4(o.matrixWorld);
        for(let j=0;j<3;j++){
          const u=v[j], w=v[(j+1)%3], dx=w.x-u.x;
          if(Math.abs(dx)<1e-9){
            if(Math.abs(u.x-railX)<1e-7)for(const point of [u,w])if(point.z>front){front=point.z;contactPoint.copy(point);}
            continue;
          }
          const t=(railX-u.x)/dx;
          if(t<0||t>1)continue;
          const forward=u.z+(w.z-u.z)*t;
          if(forward>front){front=forward;contactPoint.set(railX,u.y+(w.y-u.y)*t,forward);}
        }
      }
    });
    return Number.isFinite(front);
  }
  // Derive the approach distance from the loaded rigid bill surface. The
  // controller's fallback goal cannot know whether a new bill is shorter.
  // Test both cage and visitor loads at the existing maximum cervical angle;
  // the final contact still solves the actual triangle/rail intersection.
  const contactApproach = (() => {
    const saved=[model,nodes.body,nodes.neck,nodes.head,cervical.upper].filter(Boolean).map(node=>({node,position:node.position.clone(),rotation:node.rotation.clone()}));
    let minimumReach=Infinity;
    model.position.set(0,0,0);model.rotation.set(0,0,0);
    for(const load of [.27,.55,1]){
      nodes.body.position.copy(rest.body.position).add(new THREE.Vector3(0,-.065-load*.075,.12));
      nodes.body.rotation.set(.105+load*.035,0,0);
      cervical.restoreAttachments();cervical.setPitch(MAX_CONTACT_PITCH,0,0);
      nodes.head.position.copy(rest.head.position);nodes.head.rotation.set(-nodes.body.rotation.x*.65-MAX_CONTACT_PITCH,0,0);
      model.updateMatrixWorld(true);
      if(billSurfaceAtRail(0))minimumReach=Math.min(minimumReach,contactPoint.z);
    }
    for(const item of saved){item.node.position.copy(item.position);item.node.rotation.copy(item.rotation);}
    cervical.updateCovers();
    model.updateMatrixWorld(true);contactPoint.set(0,0,0);
    if(!Number.isFinite(minimumReach))throw new Error('Upper bill does not intersect its centre contact plane.');
    const margin=.008,requestedZ=RAIL_INNER_Z-minimumReach+margin;
    return {z:clamp(requestedZ,-.65,1.08),requestedZ,minimumSurfaceReach:minimumReach,arrivalMargin:margin,maximumPitch:MAX_CONTACT_PITCH,clamped:requestedZ<-.65||requestedZ>1.08};
  })();
  for (const foot of feet) foot.position.z += z;

  function idealFoot(f, ahead = 0) {
    return f.ideal.clone().applyAxisAngle(UP, yaw + yawVelocity * ahead).add(new THREE.Vector3(x + Math.sin(yaw) * speed * ahead, 0, z + Math.cos(yaw) * speed * ahead));
  }
  function beginStep(index, target) {
    const f = feet[index];
    f.swinging = true; f.phase = 0; f.duration=clamp(.36-Math.max(0,speed-.28)*.16,.24,.36); f.from.copy(f.position); f.to.copy(target);
    f.to.y = f.groundY; f.fromYaw = f.yaw; f.toYaw = yaw + yawVelocity * .20;
    nextFoot = 1 - index;
  }
  function solveLeg(f, pelvisShift, lift) {
    f.thigh.position.copy(f.hipRest).sub(rest.body.position).applyEuler(nodes.body.rotation).add(nodes.body.position);
    f.thigh.quaternion.identity(); f.shin.quaternion.identity(); f.foot.quaternion.identity();
    model.updateMatrixWorld(true);
    // Solve in model coordinates about the visible local-X knee journal.
    const hip = f.thigh.position.clone();
    const target = model.worldToLocal(f.position.clone());
    const solution = solveTransverseLeg(f.upper, f.lower, target.clone().sub(hip));
    f.thigh.quaternion.copy(solution.hipQuaternion);
    f.shin.quaternion.copy(solution.kneeQuaternion);
    model.updateMatrixWorld(true);
    f.foot.parent.getWorldQuaternion(inverse).invert();
    q.setFromAxisAngle(UP, f.yaw);
    q.multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1, 0, 0), -.13 * lift));
    f.foot.quaternion.copy(inverse).multiply(q);
    f.toes.rotation.copy(f.toeRest); f.toes.rotation.x = .14 * lift;
    // Modest free-air flexion tucks the individually hinged digits during a
    // lifted step. Planting restores their recorded geometry exactly; this is
    // toe clearance choreography, not a supported grasp or force simulation.
    // The Mechanic's lift is lower than the Advanced step; scale its tuck by
    // actual free-air clearance as well as phase so claws stay above the floor.
    const flex = Math.min(smooth(clamp(lift, 0, 1)), clamp((f.position.y - f.groundY) / .105, 0, 1));
    for (const digit of f.digits) {
      digit.node.rotation.copy(digit.rest);
      digit.node.rotation.x += (digit.segment === 'proximal' ? .10 : .17) * digit.weight * flex;
    }
    model.updateMatrixWorld(true);
    f.solveError = f.foot.getWorldPosition(a).distanceTo(f.position);
    maxFootError = Math.max(maxFootError, f.solveError);
  }
  function resetEra(era){
    powerPose=null;powerAnchors=null;clawCycle=null;clawPose=null;cagePose=null;currentEra=era;x=0;z=-.25;yaw=0;speed=0;velocityX=0;velocityZ=0;yawVelocity=0;
    distance=0;stride=0;nextFoot=0;time=0;contact=false;reachDrop=0;maxReachDrop=0;maxFootError=0;
    mechanicalCycle=null;camAngle=0;mechanicalPhase=0;mechanicalStage='disengaged';
    Object.keys(articulation).forEach(k=>articulation[k]=0);Object.keys(pose).forEach(k=>pose[k]=0);
    for(const f of feet){f.position.copy(f.ideal).add(new THREE.Vector3(x,0,z));f.yaw=0;f.phase=1;f.swinging=false;f.steps=0;}
    model.position.set(x,0,z);model.rotation.set(0,0,0);settled=true;arrived=false;aligned=true;
  }
  function tickClawAction(action) {
    const side=action.side==='right'?1:0, f=feet[side], support=feet[1-side];
    if(!clawCycle || clawCycle.side!==side) clawCycle={side,anchor:f.position.clone(),yaw:f.yaw,supportTarget:support.position.clone(),bodyPosition:nodes.body.position.clone(),bodyRotation:nodes.body.rotation.clone()};
    const phase=clamp(action.phase||0,0,1), smoothPhase=smooth(phase), stage=action.stage;
    const planted=clawCycle.anchor, endZ=.11;
    if(clawCycle.lastStage!==stage || (stage==='recovery'&&phase+1e-6<(clawCycle.lastPhase??0))){
      if(stage==='scrape') clawCycle.scrapeFrom=clawCycle.lastPose||{lift:0,reach:.055,curl:.255,footPitch:0};
      if(stage==='release') clawCycle.releaseFrom=clawCycle.lastPose||{lift:0,reach:0,curl:0,footPitch:0};
      if(stage==='recovery') clawCycle.recoveryFrom=clawCycle.lastPose||{lift:0,reach:0,curl:0,footPitch:0};
    }
    let lift=0,reach=0,curl=0,footPitch=0,supportBlend=stage==='approach'?smoothPhase:1;
    if(stage==='lift') { lift=.115*smoothPhase; reach=.055*smoothPhase; }
    else if(stage==='contact') {
      lift=.115; reach=.055;
      // Hold the foot clear while reaching, then articulate the claws during
      // the final descent window. This avoids asking the ankle solver to
      // recover floor clearance abruptly after early curling.
      const contactDescent=smooth(clamp((phase-.2)/.8,0,1));
      lift=.115*(1-contactDescent);
      curl=.255*contactDescent; footPitch=0;
    }
    else if(stage==='scrape') {
      if(!clawCycle.scrapeFrom) clawCycle.scrapeFrom=clawCycle.lastPose||{lift:0,reach:.055,curl:.255,footPitch:0};
      lift=clawCycle.scrapeFrom.lift;reach=.055+.055*smoothPhase;curl=.255;footPitch=0;
    }
    else if(stage==='release') {
      if(!clawCycle.releaseFrom) clawCycle.releaseFrom=clawCycle.lastPose||{lift:0,reach:0,curl:0,footPitch:0};
      const from=clawCycle.releaseFrom;
      lift=THREE.MathUtils.lerp(from.lift,.035,smoothPhase);reach=THREE.MathUtils.lerp(from.reach,endZ,smoothPhase);
      curl=THREE.MathUtils.lerp(from.curl,0,smoothPhase);footPitch=THREE.MathUtils.lerp(from.footPitch,0,smoothPhase);
    }
    else if(stage==='recovery') {
      if(!clawCycle.recoveryFrom) clawCycle.recoveryFrom=clawCycle.lastPose||{lift:0,reach:0,curl:0,footPitch:0};
      const from=clawCycle.recoveryFrom;
      lift=from.lift*(1-smoothPhase);reach=from.reach*(1-smoothPhase);curl=from.curl*(1-smoothPhase);footPitch=from.footPitch*(1-smoothPhase);
      supportBlend=1-smoothPhase;
    }
    f.position.copy(planted).add(new THREE.Vector3(0,lift,reach).applyAxisAngle(UP,yaw));
    f.yaw=clawCycle.yaw; f.swinging=false; f.phase=1;
    nodes.body.position.copy(clawCycle.bodyPosition).add(new THREE.Vector3(side===0?-.012:.012,0,0).multiplyScalar(supportBlend));
    nodes.body.rotation.copy(clawCycle.bodyRotation);
    nodes.body.rotation.z+=(side===0?-.012:.012)*supportBlend;
    model.position.set(x,0,z);model.rotation.set(0,yaw,0);model.updateMatrixWorld(true);
    solveLeg(support,null,0); solveLeg(f,null,0);
    const applyClawPose=()=>{
      f.foot.parent.getWorldQuaternion(inverse).invert();
      q.setFromAxisAngle(UP,f.yaw).multiply(new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(1,0,0),footPitch));
      f.foot.quaternion.copy(inverse).multiply(q);
      f.toes.rotation.copy(f.toeRest); f.toes.rotation.x=.14*curl;
      for(const digit of f.digits){
        digit.node.rotation.copy(digit.rest);
        digit.node.rotation.x+=(digit.segment==='proximal'?.24:.34)*digit.weight*curl;
      }
      model.updateMatrixWorld(true);
    };
    applyClawPose();
    model.updateMatrixWorld(true);
    let tipMin=Infinity;
    for(const digit of f.digits.filter(item=>item.segment==='distal')) tipMin=Math.min(tipMin,new THREE.Box3().setFromObject(digit.node,true).min.y);
    const contactStage=stage==='contact'||stage==='scrape';
    let floorCorrection=0;
    if(Number.isFinite(tipMin)&&(contactStage||tipMin<.002)){
      // Keep the measured distal mesh above the floor throughout curling. A
      // late-phase blend allowed the authored curl to intersect the floor
      // well before the nominal contact window. Corrections are upward only:
      // this remains kinematic clearance/contact positioning, not force sim.
      floorCorrection=clamp(.002-tipMin,0,.25);
      f.position.y+=floorCorrection;
      solveLeg(f,null,0);applyClawPose();
      tipMin=Infinity;
      for(const digit of f.digits.filter(item=>item.segment==='distal')) tipMin=Math.min(tipMin,new THREE.Box3().setFromObject(digit.node,true).min.y);
    }
    const contactStageActive=contactStage&&Number.isFinite(tipMin)&&Math.abs(tipMin-.002)<.006;
    clawCycle.lastPose={lift:lift+floorCorrection,reach,curl,footPitch};
    clawCycle.lastStage=stage;
    clawCycle.lastPhase=phase;
    const supportWorld=support.foot.getWorldPosition(new THREE.Vector3());
    const supportGroundMin=new THREE.Box3().setFromObject(support.foot,true).min.y;
    clawPose={stage,phase,side:f.label,target:action.target||'floor-scrape',tipMinY:tipMin,contact:contactStageActive,supportSide:support.label,supportError:supportWorld.distanceTo(clawCycle.supportTarget),supportTargetError:support.position.distanceTo(clawCycle.supportTarget),supportGroundMin,supportTarget:clawCycle.supportTarget.toArray()};
    speed=0;velocityX=0;velocityZ=0;yawVelocity=0;reachDrop=0;contact=false;
    arrived=true;aligned=true;settled=stage==='approach'||(stage==='recovery'&&phase>=1);
  }
  function finishEarlyEra(){
    model.position.set(x,0,z);model.rotation.set(0,yaw,0);model.updateMatrixWorld(true);
    let neededDrop=0;
    for(const f of feet){
      const hip=f.hipRest.clone().sub(rest.body.position).applyEuler(nodes.body.rotation).add(nodes.body.position);
      const target=model.worldToLocal(f.position.clone()),reach=f.upper.length()+f.lower.length()-.012;
      neededDrop=Math.max(neededDrop,hip.y-target.y-Math.sqrt(Math.max(.01,reach*reach-(hip.x-target.x)**2-(hip.z-target.z)**2)));
    }
    reachDrop=Math.max(0,Math.min(.12,neededDrop));maxReachDrop=Math.max(maxReachDrop,reachDrop);nodes.body.position.y-=reachDrop;
    for(const f of feet)solveLeg(f,null,f.manualLift||(f.swinging?Math.sin(Math.PI*f.phase):0));
    model.updateMatrixWorld(true);contact=false;Object.keys(pose).forEach(k=>pose[k]=0);
  }
  function tickMaker(dt,s){
    const neutral=s.inspectionRequested||s.inspection;
    for(const key of Object.keys(articulation)){
      const target=neutral?0:clamp(s.articulation?.[key]||0,0,1);
      articulation[key]=THREE.MathUtils.lerp(articulation[key],target,1-Math.exp(-dt*5));
      if(Math.abs(target-articulation[key])<.0001)articulation[key]=target;
    }
    x=0;z=-.25;yaw=0;speed=0;
    nodes.body.position.copy(rest.body.position).add(new THREE.Vector3(0,-.065,0));
    cervical.setPitch(-.14*articulation.neck,-.45*articulation.neck);
    nodes.jaw.rotation.x=.32*articulation.jaw;
    nodes['right-mantle'].rotation.x=-.38*articulation.wing;nodes['right-wing-shield'].rotation.x=.16*articulation.wing;
    for(const f of feet){f.position.copy(f.ideal).add(new THREE.Vector3(0,0,z));f.yaw=0;f.swinging=false;f.phase=1;}
    feet[0].position.y+=articulation.leg*.15;feet[0].position.z+=articulation.leg*.065;feet[0].manualLift=articulation.leg;
    finishEarlyEra();arrived=true;aligned=true;settled=Object.values(articulation).every(v=>Math.abs(v)<.003);
  }
  function tickMechanic(dt,s){
    const allowed=s.routineRunning&&!s.inspectionRequested&&!s.inspection&&!s.reducedMotion&&!s.paused;
    const goal=s.goal||{x,z},dx=goal.x-x,dz=goal.z-z,remaining=Math.hypot(dx,dz);
    const wanted=remaining>.025?Math.atan2(dx,dz):(s.heading??yaw);
    const errors=feet.map(f=>f.position.distanceTo(idealFoot(f))+Math.abs(angleDelta(f.yaw,yaw))*.15);
    if(!mechanicalCycle&&dt>0){
      const correction=!allowed&&Math.max(...errors)>.03;
      if(allowed&&(remaining>.012||Math.abs(angleDelta(yaw,wanted))>.06)||correction){
        const side=correction?(errors[0]>errors[1]?0:1):nextFoot,f=feet[side];
        const turn=allowed?clamp(angleDelta(yaw,wanted),-.34,.34):0;
        const travel=allowed&&Math.abs(angleDelta(yaw,wanted))<.25?Math.min(.145,remaining):0;
        const ex=x+(remaining?dx/remaining*travel:0),ez=z+(remaining?dz/remaining*travel:0),ey=yaw+turn;
        const to=f.ideal.clone().applyAxisAngle(UP,ey).add(new THREE.Vector3(ex,0,ez));
        mechanicalCycle={phase:0,side,sx:x,sz:z,sy:yaw,ex,ez,ey,from:f.position.clone(),fromYaw:f.yaw,to,landed:false};
        nextFoot=1-side;
      }
    }
    speed=0;mechanicalStage='disengaged';
    if(mechanicalCycle){
      const cycle=mechanicalCycle,f=feet[cycle.side];
      cycle.phase=Math.min(1,cycle.phase+dt/1.48);camAngle+=dt/1.48*Math.PI*2;mechanicalPhase=cycle.phase;
      const p=cycle.phase,release=smooth(clamp((p-.24)/.44,0,1));
      const px=x,pz=z;x=THREE.MathUtils.lerp(cycle.sx,cycle.ex,release);z=THREE.MathUtils.lerp(cycle.sz,cycle.ez,release);yaw=cycle.sy+angleDelta(cycle.sy,cycle.ey)*release;
      speed=dt?Math.hypot(x-px,z-pz)/dt:0;distance+=Math.hypot(x-px,z-pz);
      f.phase=release;f.swinging=p>.24&&p<.68;f.position.lerpVectors(cycle.from,cycle.to,release);f.position.y=f.groundY+Math.sin(Math.PI*release)*.05;f.yaw=cycle.fromYaw+angleDelta(cycle.fromYaw,cycle.ey)*release;
      mechanicalStage=p<.24?'load':p<.68?'release':p<.84?'settle':'dwell';
      if(p>=.68&&!cycle.landed){cycle.landed=true;f.steps++;stride++;f.swinging=false;f.position.copy(cycle.to);}
      if(p===1)mechanicalCycle=null;
    }
    const load=mechanicalCycle?Math.sin(Math.PI*mechanicalPhase)**2:0;
    nodes.body.position.copy(rest.body.position).add(new THREE.Vector3(0,-.065-.012*load,0));
    nodes.body.rotation.z=(mechanicalCycle?.side===0?-.018:.018)*load;
    cervical.setPitch(0,0,0);nodes.head.rotation.set(0,0,0);nodes.jaw.rotation.set(0,0,0);
    nodes['right-mantle'].rotation.x=-.025*load;nodes['left-mantle'].rotation.x=-.009*load;
    finishEarlyEra();
    arrived=Math.hypot(goal.x-x,goal.z-z)<.025;aligned=Math.abs(angleDelta(yaw,s.heading??yaw))<.08;
    settled=!mechanicalCycle&&feet.every(f=>!f.swinging)&&(!s.inspectionRequested||Math.max(...errors)<.035);
  }
  function tickPowerMove(s){
    const {kind,phase}=s.powerMove,p=clamp(phase,0,1);
    if(!powerAnchors||powerPose?.kind!==kind)powerAnchors=feet.map(f=>f.position.clone());
    let height=0,crouch=0,drive=0,air=0,stage='load';
    if(kind==='jump'){
      if(p<.22)crouch=.11*smooth(p/.22);
      else if(p<.64){
        const flight=(p-.22)/.42;
        height=4*.36*flight*(1-flight);air=Math.sin(Math.PI*flight);
        crouch=.11*(1-smooth(clamp(flight/.12,0,1)));stage='airborne';
      }else if(p<.84){crouch=.105*Math.sin(Math.PI*(p-.64)/.20);stage='landing';}
      else stage='recover';
    }else{
      const load=smooth(clamp(p/.25,0,1));
      drive=p<.25?0:p<.48?smooth((p-.25)/.23):p<.58?1:1-smooth((p-.58)/.42);
      crouch=.06*load*(1-smooth(clamp((p-.58)/.42,0,1)));
      stage=p<.25?'load':p<.48?'drive':p<.58?'brace':'recover';
    }
    model.position.set(x,height,z);model.rotation.set(0,yaw,0);
    speed=0;velocityX=0;velocityZ=0;yawVelocity=0;reachDrop=0;
    nodes.body.position.copy(rest.body.position).add(new THREE.Vector3(0,-.065-crouch,.075*drive));
    nodes.body.rotation.set(.09*drive+.12*crouch,0,-.025*drive);
    cervical.setPitch(-.07*drive,0,0);nodes.head.rotation.set(-.035*drive,0,0);nodes.jaw.rotation.set(0,0,0);
    nodes['right-mantle'].rotation.x=-.64*drive-.12*air;
    nodes['right-wing-shield'].rotation.x=.72*drive+.12*air;
    nodes['left-mantle'].rotation.x=.07*drive+.035*air;
    nodes['left-wing-shield'].rotation.x=.18*drive+.045*air;
    for(let i=0;i<feet.length;i++){
      const f=feet[i];f.position.copy(powerAnchors[i]);f.position.y+=height+air*.035;f.swinging=height>.00001;f.phase=air;
      solveLeg(f,null,air*.5);
    }
    model.updateMatrixWorld(true);contact=false;arrived=true;aligned=true;settled=p>=1;
    Object.assign(pose,{load:crouch/.11,extension:0,jaw:0,gaze:0,guard:drive,counter:0});
    powerPose={kind,phase:p,height,stage,grounded:height===0};
  }
  function tick(dt, s) {
    // Keep support-foot scheduling stable after a slow browser frame. Advancing
    // the root by 100 ms in one solve can outrun the foot that is just lifting.
    // These are bounded kinematic substeps, not a physical dynamics solver.
    if(dt>1/30){
      const elapsed=clamp(dt,0,.1),steps=Math.ceil(elapsed/(1/60));
      for(let i=0;i<steps;i++)tick(elapsed/steps,s);
      return;
    }
    if(s.era!==currentEra)resetEra(s.era);
    if(s.state!=='cage-test')cagePose=null;
    for(const f of feet)f.manualLift=0;
    // Fixed structural attachments, including when a caller omits a pose reset.
    cervical.restoreAttachments();
    // Pause freezes the actual pose, including a foot mid-step.
    if (s.paused && !s.inspectionRequested) dt = 0;
    dt = clamp(dt, 0, .1); time += dt; motionFrame++;
    if(s.era==='maker'){tickMaker(dt,s);return;}
    if(s.era==='mechanic'){tickMechanic(dt,s);return;}
    if(s.clawAction){tickClawAction(s.clawAction);return;}
    if(clawCycle){
      const f=feet[clawCycle.side];
      f.position.copy(clawCycle.anchor);f.yaw=clawCycle.yaw;f.swinging=false;f.phase=1;
      f.toes.rotation.copy(f.toeRest);
      for(const digit of f.digits)digit.node.rotation.copy(digit.rest);
      clawCycle=null;clawPose=null;
    }
    if(s.powerMove){tickPowerMove(s);return;}
    powerPose=null;powerAnchors=null;
    const calm = s.reducedMotion;
    const stop = calm || s.inspectionRequested || s.inspection;
    const goal = s.goal || { x:x+Math.sin(yaw), z:z+Math.cos(yaw) };
    const dx = goal.x - x, dz = goal.z - z, remaining = Math.hypot(dx, dz);
    let desiredHeading = stop ? yaw : (remaining > .045 && s.speed > 0 ? Math.atan2(dx, dz) : (s.heading ?? yaw));
    const headingError = angleDelta(yaw, desiredHeading);
    const yawStep = stop ? 0 : clamp(headingError, -dt * 1.35, dt * 1.35);
    yawVelocity = dt ? yawStep / dt : 0; yaw += yawStep;
    const desiredSpeed = !stop && s.goal && remaining > .004 ? Math.min(s.speed || 0, Math.sqrt(Math.max(0, remaining - .002) * .72)) * Math.max(0, Math.cos(headingError) ** 5) * (Math.abs(headingError) < 1.2 ? 1 : 0) : 0;
    const wantedX=remaining?dx/remaining*desiredSpeed:0, wantedZ=remaining?dz/remaining*desiredSpeed:0;
    const changeX=wantedX-velocityX,changeZ=wantedZ-velocityZ,change=Math.hypot(changeX,changeZ);
    const acceleration=change?Math.min(1,dt*1.35/change):0;
    velocityX+=changeX*acceleration;velocityZ+=changeZ*acceleration;
    speed=Math.hypot(velocityX,velocityZ);
    if(s.goal&&remaining<.006&&speed<.035){velocityX=0;velocityZ=0;speed=0;}
    x+=velocityX*dt;z+=velocityZ*dt;distance+=speed*dt;
    x = clamp(x, -1.6, 1.6); z = clamp(z, -.65, 1.08);
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
    let cageProfile = null, cageFamily = null, cagePhase = null;
    if (!stop) {
      if (state === 'agitated') {load=.18*(s.agitation||0);guard=.22*(s.agitation||0);}
      if (state === 'warning') { load = p; jaw = .75 * p; guard = p; }
      if (state === 'strike') { load = 1 - .45 * p; extension = p; jaw = .75 * (1 - p); guard = 1; }
      if (state === 'contact') { load = .55; extension = 1; guard = 1; }
      if (state === 'recover' && s.actionKind === 'visitor') { extension = 1 - p; load = .55 * (1 - p); guard = 1 - p; }
      if (state === 'cage-test' && arrived && settled && aligned) {
        cageFamily = ['edge-probe','rail-press','seam-rattle'].includes(s.actionFamily) ? s.actionFamily : 'rail-press';
        cagePhase = clamp(s.phase || 0, 0, 1);
        cageProfile = cageFamilyProfile(cageFamily, cagePhase);
        extension = cageProfile.envelope;
        load = cageProfile.load;
        guard = cageProfile.guard;
        jaw = cageProfile.jaw;
      }
    }
    // Approach to new pose is bounded; interruption cannot pop joints to zero.
    const responseRate = state === 'strike' ? 32 : state === 'cage-test' && cageFamily === 'edge-probe' ? 22 : state === 'cage-test' && cageFamily === 'seam-rattle' ? 24 : 7;
    const blend = 1 - Math.exp(-dt * responseRate);
    for (const [key, value] of Object.entries({ load, extension, jaw, guard })) pose[key] = THREE.MathUtils.lerp(pose[key], value, blend);
    if(cageProfile){
      cagePose={family:cageFamily,phase:cagePhase,envelope:cageProfile.envelope,
        extension:pose.extension,load:pose.load,guard:pose.guard,jaw:pose.jaw,contact:false};
    }
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
    cervical.setPitch(-pose.load * .13 + pose.extension * .08, pose.gaze * .48);
    nodes.head.rotation.y = pose.gaze * .52 * (1 - pose.extension);
    nodes.head.rotation.x = -nodes.body.rotation.x * .65;
    nodes.jaw.rotation.x = pose.jaw * .27;
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
    // Fixed-length cervical articulation: bend about the body attachment and
    // counter-rotate the skull. The closer approach goal supplies the missing
    // reach; contact never translates or stretches the apparent anatomy.
    if (pose.extension > .001 && ['strike','contact','recover','cage-test'].includes(state)
        && aligned && Math.abs(angleDelta(yaw, 0)) < .05) {
      const railX=s.lookTarget?.x??s.goal?.x??x;
      const basePitch=cervical.pitch, headBase=nodes.head.rotation.x;
      const applyPitch=pitch=>{
        cervical.setPitch(pitch);
        nodes.head.rotation.x=headBase-pitch;
        model.updateMatrixWorld(true);
        return billSurfaceAtRail(railX);
      };
      let low=0, high=MAX_CONTACT_PITCH;
      const reachable=applyPitch(high)&&contactPoint.z>=RAIL_INNER_Z;
      if(reachable){
        for(let i=0;i<16;i++){
          const mid=(low+high)/2;
          if(applyPitch(mid)&&contactPoint.z>=RAIL_INNER_Z)high=mid;else low=mid;
        }
      }
      const pitch=THREE.MathUtils.lerp(basePitch,high,clamp(pose.extension,0,1));
      const intersects=applyPitch(pitch);
      if(!intersects)leadingBillPoint();
      const radial=Math.hypot(contactPoint.x-railX,contactPoint.z-2.1);
      contact=intersects&&Math.abs(radial-.021)<.008&&(state==='contact'||state==='cage-test');
    }
    if(cagePose)cagePose.contact=contact;
    if(stop)settled=settled&&pose.extension<.003&&pose.load<.003&&Math.abs(pose.counter)<.003;
    previousState = state;
  }
  function visibleModelBounds(){
    const bounds=new THREE.Box3(),vertex=new THREE.Vector3();
    model.traverseVisible(object=>{if(object.isMesh){const positions=object.geometry.attributes.position;for(let i=0;i<positions.count;i++)bounds.expandByPoint(vertex.fromBufferAttribute(positions,i).applyMatrix4(object.matrixWorld));}});
    return bounds;
  }
  return {
    tick(dt, snapshot) {
      tick(dt, snapshot);
      // Head counterrotation is resolved after neck pitch, including early
      // era/power-action returns. Update rigid receivers from that final pose.
      if (cervical.updateCovers()) model.updateMatrixWorld(true);
    }, resetEra,
    driveMetrics:()=>({root:{x,z,yaw,speed},camAngle,mechanicalPhase,mechanicalStage,actualArticulation:{...articulation}}),
    feedback: () => ({ arrived, settled, aligned, contact, contactApproachZ:contactApproach.z, clawContact:clawPose?.contact??false, clawSupportError:clawPose?.supportError??null }),
    metrics() {
      model.updateMatrixWorld(true);
      return { era:currentEra,powerMove:powerPose?{...powerPose}:null,clawAction:clawPose?{...clawPose}:null,cageAction:cagePose?{...cagePose}:null,root: { x, z, yaw, speed }, distance, steps: stride, time, motionFrame, settled, arrived, aligned, contact,camAngle,mechanicalPhase,mechanicalStage,actualArticulation:{...articulation}, cervical:{...cervical.metrics(),baseTranslationError:nodes.neck.position.distanceTo(rest.neck.position),skullTranslationError:nodes.head.position.distanceTo(rest.head.position),neckPitch:nodes.neck.rotation.x,skullPitch:nodes.head.rotation.x,maxContactPitch:MAX_CONTACT_PITCH,contactMethod:'upper-bill triangle / rail-centre plane'}, contactApproach:{...contactApproach}, jawHinge:{axis:'local X',openingSign:1,angle:nodes.jaw.rotation.x,makerMaximum:.32}, contactPoint: contactPoint.toArray(), pose: { ...pose }, maxFootError, reachDrop, maxReachDrop, feet: feet.map(f => ({ side: f.label, target: f.position.toArray(), actual: f.foot.getWorldPosition(new THREE.Vector3()).toArray(), swinging: f.swinging, phase: f.phase, yaw: f.yaw, steps: f.steps, solveError: f.solveError, kneeHinge:{axis:'local X',angle:f.shin.rotation.x,offAxisQuaternion:Math.hypot(f.shin.quaternion.y,f.shin.quaternion.z)}, digits:f.digits.map(d=>({name:d.node.name,angle:d.node.rotation.x,restAngle:d.rest.x})), groundMin: new THREE.Box3().setFromObject(f.foot, true).min.y })), bodyBounds: visibleModelBounds(), headBounds: new THREE.Box3().setFromObject(nodes.head, true) };
    },
  };
}
