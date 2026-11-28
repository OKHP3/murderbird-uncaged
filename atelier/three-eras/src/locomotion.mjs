import {rigidRuns} from './rig-bindings.mjs';

// Rigid motion for the exact frozen GLB. Progress is absolute, normalized 0..1.
// The adapter never owns a playback clock. During cutaway/First Choice, call
// set('rest',0) once before opening panels or sampling the original animation.
export function installLocomotion(T, modelRoot, scene) {
  const V=(x=0,y=0,z=0)=>new T.Vector3(x,y,z);
  const clamp=v=>Math.max(0,Math.min(1,Number.isFinite(v)?v:0));
  const ease=t=>{t=clamp(t);return t*t*(3-2*t);};
  const lerp=(a,b,u)=>a+(b-a)*u;
  const tau=2*Math.PI, xAxis=V(1,0,0),zAxis=V(0,0,1);
  const nodes={}, pivots={}, records=[], ownedGeometry=new Set();
  const grouped = new Map();
  modelRoot.updateWorldMatrix(true,true);
  const rootInverse = modelRoot.matrixWorld.clone().invert();
  modelRoot.traverse(o=>{
    if(o.userData.region)nodes[o.userData.region]=o;
    if(o.userData.fc_region)pivots[o.userData.fc_region]=o;
  });
  if(!nodes['leg']||!nodes['foot']||!nodes['wing.l']||!pivots.neck)throw Error('Expected frozen First Choice nodes');
  function subset(original, array) {
    const g=new T.BufferGeometry();for(const [name,a] of Object.entries(original.attributes))g.setAttribute(name,a);
    g.setIndex(array);g.boundingSphere=original.boundingSphere?.clone()||null;g.boundingBox=original.boundingBox?.clone()||null;
    ownedGeometry.add(g);return g;
  }
  for(const region of ['foot','leg','head','body','torso']){
    const meshes=[];nodes[region].traverse(o=>{if(o.isMesh&&!o.userData.fc_inspection && !o.userData.eraArt)meshes.push(o);});
    for(const o of meshes){
      if(Array.isArray(o.material))continue;
      const original=o.geometry, index=original.index?.array;
      const description=rigidRuns[region+'|'+o.material.name];if(!description)continue;
      const [faceCount,runs]=description;
      if(!index || index.length!==3*faceCount)throw Error('Incorrect GLB primitive '+region+' '+o.material.name);
      const byPart=new Map();let start=0;
      for(let j=0;j<runs.length;j+=2){
        const count=runs[j]*3,part=runs[j+1];if(!byPart.has(part))byPart.set(part,[]);
        const ids=byPart.get(part);for(let k=start;k<start+count;k++)ids.push(index[k]);start+=count;
      }
      if(start!==index.length)throw Error('Incomplete native split map');
      const inv=rootInverse.clone().multiply(o.matrixWorld), revert=inv.clone().invert();
      const rec={o,original,still:subset(original,byPart.get(0)||[]),pieces:[],active:false};
      for(const [id,ids] of byPart){
        if(id===0)continue;
        const child=new T.Mesh(subset(original,ids),o.material);child.name='Authored rigid piece '+id;child.userData.fc_locomotion=true;
        child.castShadow=o.castShadow;child.receiveShadow=o.receiveShadow;child.visible=false;child.matrixAutoUpdate=false;
        o.add(child);rec.pieces.push(child);
        if(!grouped.has(id))grouped.set(id,[]);
        grouped.get(id).push({child,rec,bind:inv,inverseBind:revert});
      }
      records.push(rec);
    }
  }
  for(let id=1;id<=26;id++)if(!grouped.has(id))throw Error('Missing native rigid part '+id);
  const driveNodes=[pivots.torso,pivots.neck,nodes['wing.l'],nodes['wing.r']];
  const rest=new Map(driveNodes.map(o=>[o,{position:o.position.clone(),quaternion:o.quaternion.clone(),scale:o.scale.clone(),local:o.matrix.clone(),parentBind:rootInverse.clone().multiply(o.parent.matrixWorld)}]));
  let engaged=false,state={mode:'rest',leftLift:0,rightLift:0,leftFore:0,rightFore:0,bodyFore:0};
  function resetNodes(){
    for(const [o,r] of rest){o.position.copy(r.position);o.quaternion.copy(r.quaternion);o.scale.copy(r.scale);o.updateMatrix();}
  }
  function activate(){
    for(const rec of records){
      rec.o.geometry=rec.still;
      if(!rec.active){for(const child of rec.pieces)child.visible=true;rec.active=true;}
      for(const child of rec.pieces){child.material=rec.o.material;child.matrix.identity();child.matrixWorldNeedsUpdate=true;}
    }
    resetNodes();engaged=true;
  }
  function release(){
    if(!engaged)return;
    for(const rec of records){rec.o.geometry=rec.original;for(const child of rec.pieces)child.visible=false;rec.active=false;}
    resetNodes();engaged=false;modelRoot.updateWorldMatrix(true,true);
    state={mode:'rest',leftLift:0,rightLift:0,leftFore:0,rightFore:0,bodyFore:0};
  }
  // Rigid displacement maps one joint center and orientation onto another.
  const rot=new T.Matrix4(),local=new T.Matrix4(),tmp=V();
  function delta(a,b,axis,angle){
    rot.makeRotationAxis(axis,angle);tmp.copy(a).applyMatrix4(rot).negate().add(b);rot.setPosition(tmp);return rot;
  }
  function movePart(id,transform){
    // Toe subparts follow the foot rigidly for ordinary walking. Encounter-only
    // curling replaces these matrices after the gait has established stance.
    if(id===4||id===8){const first=id===4?11:19;for(let k=first;k<first+8;k++)movePart(k,transform);}
    for(const {child,bind,inverseBind} of grouped.get(id)){
      child.matrix.multiplyMatrices(inverseBind,transform).multiply(bind);child.matrixWorldNeedsUpdate=true;
    }
  }
  function moveNode(o,transform){
    const r=rest.get(o);local.copy(r.parentBind).invert().multiply(transform).multiply(r.parentBind).multiply(r.local);
    local.decompose(o.position,o.quaternion,o.scale);o.updateMatrix();
  }
  const hinge=[-.165,.865,-.105], knee=[-.167,.590,-.010], hock=[-.175,.285,-.075], ankle=[-.218,.105,-.015];
  const roots=[hinge,knee,hock,ankle].map(a=>V(...a));
  const reference=[roots,roots.map(v=>V(-v.x,v.y,v.z))];
  const vecAngle=(a,b)=>Math.atan2(b.z-a.z,b.y-a.y);
  const yzLength=(a,b)=>Math.hypot(b.y-a.y,b.z-a.z);
  // Set the tarsus from its independent foot target and solve the upper pair
  // by the two-link circle intersection. Round races retain their original X positions.
  function solveLeg(side,bodyFore,bodyHeight,footFore,lift,tip) {
    const [hip0,knee0,hock0,ankle0]=reference[side]; const h=hip0.clone();h.y+=bodyHeight;h.z+=bodyFore;
    const a=ankle0.clone();a.y+=lift;a.z+=footFore;
    const k=hock0.clone().sub(ankle0).applyAxisAngle(xAxis,tip).add(a);
    const dy=k.y-h.y,dz=k.z-h.z,d=Math.hypot(dy,dz),l1=yzLength(hip0,knee0),l2=yzLength(knee0,hock0);
    const chord=(l1*l1-l2*l2+d*d)/(2*d),height=Math.sqrt(Math.max(0,l1*l1-chord*chord));
    const n=V(knee0.x,h.y+chord*dy/d+height*dz/d,h.z+chord*dz/d-height*dy/d);
    const offset=side*4;
    movePart(1+offset,delta(hip0,h,xAxis,vecAngle(h,n)-vecAngle(hip0,knee0)));
    movePart(2+offset,delta(knee0,n,xAxis,vecAngle(n,k)-vecAngle(knee0,hock0)));
    movePart(3+offset,delta(ankle0,a,xAxis,tip));
    movePart(4+offset,delta(ankle0,a,xAxis,0));
    return Math.max(0,d-(l1+l2));
  }
  const vertical=V(0,1,0), pelvisCenter=V(0,.865,-.105);
  function rigidFrame(restJoint,nextJoint,quaternion){
    const m=new T.Matrix4().makeRotationFromQuaternion(quaternion);
    return m.setPosition(restJoint.clone().applyQuaternion(quaternion).negate().add(nextJoint));
  }
  // A shallow indexed Mechanic turn. Feet rotate in their swing phase only;
  // each completed landing retains yaw through its entire next stance.
  function turningLeg(side,bodyFore,bodyHeight,footFore,lift,tip,hipYaw,footYaw){
    const [h0,n0,k0,a0]=reference[side];
    const rootYaw=new T.Quaternion().setFromAxisAngle(vertical,hipYaw);
    const pedalYaw=new T.Quaternion().setFromAxisAngle(vertical,footYaw);
    const ankleFrame=pedalYaw.clone().multiply(new T.Quaternion().setFromAxisAngle(xAxis,tip));
    const h=h0.clone().sub(pelvisCenter).applyQuaternion(rootYaw).add(pelvisCenter).add(V(0,bodyHeight,bodyFore));
    const a=a0.clone().add(V(0,lift,footFore)),k=k0.clone().sub(a0).applyQuaternion(ankleFrame).add(a);
    const run=k.clone().sub(h),d=run.length();run.normalize();
    const restAxis=k0.clone().sub(h0).normalize(),oldBend=n0.clone().sub(h0);
    oldBend.addScaledVector(restAxis,-oldBend.dot(restAxis)).applyQuaternion(rootYaw);
    const bend=oldBend.addScaledVector(run,-oldBend.dot(run)).normalize();
    const l1=h0.distanceTo(n0),l2=n0.distanceTo(k0),chord=(l1*l1-l2*l2+d*d)/(2*d);
    const n=h.clone().addScaledVector(run,chord).addScaledVector(bend,Math.sqrt(Math.max(0,l1*l1-chord*chord)));
    function linkFrame(restA,restB,nextA,nextB,q){
      const before=restB.clone().sub(restA).normalize().applyQuaternion(q),after=nextB.clone().sub(nextA).normalize();
      return rigidFrame(restA,nextA,new T.Quaternion().setFromUnitVectors(before,after).multiply(q));
    }
    const id=1+4*side;
    movePart(id,linkFrame(h0,n0,h,n,rootYaw));
    movePart(id+1,linkFrame(n0,k0,n,k,rootYaw.clone().slerp(pedalYaw,.5)));
    movePart(id+2,rigidFrame(a0,a,ankleFrame));movePart(id+3,rigidFrame(a0,a,pedalYaw));
    return Math.max(0,d-l1-l2);
  }
  const shoulderLeft=V(-.233,1.247,.028),shoulderRight=V(.233,1.247,.028);
  const jawAxis=V(0,1.63788,.20717);const tailAxis=V(0,.947,-.241);
  const neckWorld=V(0,1.30,.105);
  function setWings(left,right){
    moveNode(nodes['wing.l'],delta(shoulderLeft,shoulderLeft,zAxis,-left));
    moveNode(nodes['wing.r'],delta(shoulderRight,shoulderRight,zAxis,right));
  }
  function setBody(z,y,pitch,yaw=0){
    const a=V(0,.865,-.105), b=V(0,.865+y,-.105+z);const orientation=new T.Quaternion().setFromAxisAngle(vertical,yaw).multiply(new T.Quaternion().setFromAxisAngle(xAxis,pitch));
    moveNode(pivots.torso,rigidFrame(a,b,orientation));
  }
  function phaseStep(t,mechanic,stride=1,turn=1){
    // Eight alternating landings. Feet retain their authored model-world position
    // throughout each stance. Reversing direction requires a separate four-step return.
    const stops=(mechanic?[.035,.079,.106,.115,.069,.043,0,0]:[.125,.232,.338,.378,.230,.108,0,0]).map(v=>v*stride);
    const f=clamp(t)*8,step=Math.min(7,Math.floor(f)),phase=f-step;
    const pos=[0,0],lift=[0,0],tip=[0,0];
    for(let i=0;i<step;i++)pos[i%2]=stops[i];
    const side=step%2, pad=mechanic?.20:.11, start=.09;
    const sweep=clamp((phase-start)/(1-start-pad));
    const u=ease(sweep),arc=Math.sin(Math.PI*sweep)**2;
    pos[side]=lerp(pos[side],stops[step],u);
    lift[side]=(mechanic?.026:.072)*arc;tip[side]=(mechanic?.056:.135)*Math.sin(tau*sweep)*arc;
    const z=(pos[0]+pos[1])*.5;
    // Compression at load transfer gives the near-vertical rods room to flex.
    const y=-(mechanic?.006:.014)*arc-(mechanic?.006:.018)*Math.sin(Math.PI*t)**2;
    const pitch=(side===0?1:-1)*arc*(mechanic?.007:.014);
    const yaw=[0,0];
    if(mechanic){
      const notches=[.075,.140,.215,.235,.155,.074,0,0].map(v=>v*turn);
      for(let i=0;i<step;i++)yaw[i%2]=notches[i];yaw[side]=lerp(yaw[side],notches[step],u);
    }
    const hipYaw=(yaw[0]+yaw[1])*.5;
    setBody(z,y,pitch,hipYaw);
    const misses=pos.map((v,i)=>mechanic?turningLeg(i,z,y,v,lift[i],tip[i],hipYaw,yaw[i]):solveLeg(i,z,y,v,lift[i],tip[i]));
    const leftAngle=arc*(side===0?.070:.019),rightAngle=arc*(side===1?.131:.038);
    setWings(leftAngle*(mechanic?.35:1),rightAngle*(mechanic?.35:1));
    state={mode:mechanic?'mechanic':'patrol',...stats(pos,lift,z),side,phase,hipYaw,leftFootYaw:yaw[0],rightFootYaw:yaw[1],maxExtensionMiss:Math.max(...misses),leftGuard:leftAngle*(mechanic?.35:1),rightGuard:rightAngle*(mechanic?.35:1)};
  }
  function stats(pos,lift,z){return {leftFore:pos[0],rightFore:pos[1],leftLift:lift[0],rightLift:lift[1],bodyFore:z};}
  function set(mode,t=0,options={}){
    if(mode==='rest'){release();return;}
    if(mode!=='patrol' && mode!=='mechanic')throw Error('Unknown locomotion mode '+mode);
    t=clamp(t); if(t===0 || t===1){release();return;}
    activate();phaseStep(t,mode==='mechanic',Math.max(-1,Math.min(1,options.stride??1)),options.turn<0?-1:1);modelRoot.updateWorldMatrix(true,true);
  }
  function manual(controls={}){
    const leg=clamp(controls.leg),wing=clamp(controls.wing),tail=clamp(controls.tail),neck=clamp(controls.neck),jaw=clamp(controls.jaw);
    if(!(leg||wing||tail||neck||jaw)){release();return;}
    activate();const hipDrop=-.007*leg;
    setBody(0,hipDrop,0);solveLeg(0,0,hipDrop,.023*leg,.065*leg,.048*leg);solveLeg(1,0,hipDrop,0,0,0);
    setWings(.16*wing,0);
    movePart(9,delta(jawAxis,jawAxis,xAxis,.135*jaw));
    movePart(10,delta(tailAxis,tailAxis,xAxis,.105*tail));
    moveNode(pivots.neck,delta(neckWorld,neckWorld,xAxis,.089*neck));
    state={mode:'manual',...stats([.023*leg,0],[.065*leg,0],0),controls:{leg,wing,tail,neck,jaw}};modelRoot.updateWorldMatrix(true,true);
  }
  const toeSpecs=[
    [[.030,.044],[.118,.215],[.170,.278]],
    [[.002,.050],[.018,.268],[.024,.357]],
    [[-.032,.046],[-.103,.211],[-.141,.282]],
    [[-.005,-.008],[-.040,-.128],[-.059,-.199]],
  ];
  // Use the actual low apex of each exported central talon. The higher beveled
  // rim projects a fraction farther forward and remains clear of the bar.
  const loadedCentralTips=[14,22].map(id=>{
    let front=null;const p=V();
    for(const {child,bind} of grouped.get(id)){
      const a=child.geometry.attributes.position;
      for(const vertex of child.geometry.index.array){
        p.fromBufferAttribute(a,vertex).applyMatrix4(bind);
        if(!front||p.y<front.y)front=p.clone();
      }
    }
    return front;
  });
  function digitTransform(side,number,amount){
    const [start,socket,apex]=toeSpecs[number],sign=side===0?-1:1;
    const root=V(sign*(.218+start[0]),.060,start[1]);
    const hinge=V(sign*(.218+socket[0]),number===3?.046:.050,socket[1]);
    const tip=number===1?loadedCentralTips[side].clone():V(sign*(.218+apex[0]),.0005,apex[1]);
    const axis=V(apex[1]-start[1],0,-sign*(apex[0]-start[0])).normalize();
    const spread=[.62,1,.82,.35][number];
    const body=delta(root,root,axis,amount*spread*.135).clone();
    const blade=body.clone().multiply(delta(hinge,hinge,axis,amount*spread*.265));
    return {body,blade,tip:tip.applyMatrix4(blade)};
  }
  const rail={z:.558,y:.093,r:.013};
  function encounterPose(p={}){
    activate();const side=p.side===1?1:0,q=clamp(p.grip),curl=clamp(p.curl??q);
    const digits=toeSpecs.map((d,i)=>digitTransform(side,i,curl));
    const point=digits[1].tip, floorPos=[p.leftFore||0,p.rightFore||0],height=[p.leftLift||0,p.rightLift||0];
    // Raise the tip above the crown of the round rail before settling into
    // contact, and take the same clear path on release. The extra height
    // vanishes at both the original stance and the fully seated talon.
    const liftArc=Math.sin(Math.PI*q)**2*.064+.19*q*q*(1-q);
    floorPos[side]=lerp(floorPos[side],rail.z-point.z,q);
    height[side]=lerp(height[side],rail.y+rail.r-point.y,q)+liftArc;
    const stance=p.bodyFore??(floorPos[0]+floorPos[1])*.5;
    const bodyHeight=p.bodyHeight??(-.011*q-.008*clamp(p.brace));
    setBody(stance,bodyHeight,p.pitch||0);
    const misses=floorPos.map((z,i)=>solveLeg(i,stance,bodyHeight,z,height[i],0));
    setWings(p.leftGuard||0,p.rightGuard||0);
    const moveFoot=new T.Matrix4().makeTranslation(0,height[side],floorPos[side]);
    for(let i=0;i<digits.length;i++){
      const id=11+side*8+i*2;
      movePart(id,moveFoot.clone().multiply(digits[i].body));movePart(id+1,moveFoot.clone().multiply(digits[i].blade));
    }
    movePart(9,delta(jawAxis,jawAxis,xAxis,.19*clamp(p.jaw)));
    movePart(10,delta(tailAxis,tailAxis,xAxis,.048*clamp(p.brace)));
    const tip=point.clone().applyMatrix4(moveFoot);
    state={mode:'encounter',...stats(floorPos,height,stance),side,curl,grip:q,tip:tip.toArray(),maxExtensionMiss:Math.max(...misses),
      contactGap:Math.hypot(tip.y-rail.y,tip.z-rail.z)-rail.r,leftGuard:p.leftGuard||0,rightGuard:p.rightGuard||0};
    modelRoot.updateWorldMatrix(true,true);return state;
  }
  // The hand rack's terminal clevises follow the actual displaced anatomy. The
  // linkage installer can also be used on its own against the unaltered GLB.
  const anchorQuery=Symbol.for('First Choice · exterior control terminal');
  const priorAnchorQuery=modelRoot[anchorQuery];
  modelRoot[anchorQuery]=(name,restPoint)=>{
    if(state.mode!=='manual' || !engaged)return null;
    const id={leg:1,tail:10,jaw:9}[name];
    if(id){const part=grouped.get(id)[0];return restPoint.clone().applyMatrix4(part.inverseBind).applyMatrix4(part.child.matrixWorld);}
    const node=name==='wing'?nodes['wing.l']:pivots.neck;
    const r=rest.get(node);const bind=r.parentBind.clone().multiply(r.local);
    return restPoint.clone().applyMatrix4(bind.invert()).applyMatrix4(node.matrixWorld);
  };
  function dispose(){if(priorAnchorQuery)modelRoot[anchorQuery]=priorAnchorQuery;else delete modelRoot[anchorQuery];release();for(const rec of records)for(const child of rec.pieces)child.removeFromParent();for(const g of ownedGeometry)g.dispose();}
  return {set,manual,encounterPose,contactRail:Object.freeze({...rail}),snapshot:()=>({...state}),dispose};
}
