// Self-contained digital behavior for the Advanced enclosure. The host alone
// supplies time in seconds and opt-in input. The original First Choice is independent.
export function installEncounter(T,root,scene,gait){
  const nodes={};root.traverse(o=>{if(o.userData.fc_region)nodes[o.userData.fc_region]=o;});
  if(!nodes.head||!gait.encounterPose)throw Error('Advanced encounter requires the First Choice segmented rig');
  const neckRest=nodes.neck.quaternion.clone(), headRest=nodes.head.quaternion.clone();
  const geo=new T.CylinderGeometry(1,1,1,18);
  const steel=new T.MeshStandardMaterial({color:0x54544e,metalness:.73,roughness:.48});
  const bronze=new T.MeshStandardMaterial({color:0x837252,metalness:.61,roughness:.54});
  const fixture=new T.Group();fixture.name='Exhibit · removable low test rail';scene.add(fixture);
  const rack=gait.contactRail;
  function rail(name,a,b,r,mat){
    const start=new T.Vector3(...a),end=new T.Vector3(...b),d=end.clone().sub(start);
    const m=new T.Mesh(geo,mat);m.name=name;m.position.copy(start).add(end).multiplyScalar(.5);
    m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),d.clone().normalize());m.scale.set(r,d.length(),r);
    m.castShadow=true;m.receiveShadow=true;fixture.add(m);return m;
  }
  // A low transverse rung connects back to the fixed front boundary, leaving the
  // center floor free. Its radius and center match the loaded central toe witness.
  rail('Toe witness rail',[-.65,rack.y,rack.z],[.65,rack.y,rack.z],rack.r,steel);
  for(const side of [-1,1]){
    rail('Swept return to perimeter',[side*.65,rack.y,rack.z],[side*1.25,.23,1.26],.011,steel);
    rail('Test rail floor stay',[side*.63,.008,rack.z+.10],[side*.63,rack.y,rack.z],.012,steel);
    rail('Worn return collar',[side*.61,rack.y,rack.z],[side*.648,rack.y,rack.z],.016,bronze);
  }
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,Number.isFinite(x)?x:a));
  const smooth=x=>{x=clamp(x);return x*x*(3-2*x);};
  const step=(t,a,b)=>smooth((t-a)/(b-a));
  const bell=(t,a,b,c,d)=>step(t,a,b)*(1-step(t,c,d));
  const lerp=(a,b,t)=>a+(b-a)*t;
  const laneYaw={left:-.54,center:0,right:.54};
  const labels={watch:'Listening behind the rail',scan:'Watching the sides of the enclosure',pace:'Pacing the enclosure',still:'Holding still',test:'Testing the lower rail',notice:'Notice',orient:'Turning toward the visitor',approach:'Shifting toward the rail',warning:'Holding a warning',commit:'Committed snap',contact:'Talon on the rail',recover:'Recovering',cooldown:'Cooling down',withdraw:'The visitor withdrew'};
  let seed=0, intervals=[],commands=[],notes=[],state,lastPhase='',lastSample=-1;
  const observed=new Set();
  function random(index,tag=0){
    let n=(Math.imul(index+1,0x45d9f3b)^Math.imul(seed+13,0x9e3779b1)^Math.imul(tag+3,0x27d4eb2d))>>>0;
    n=Math.imul(n^(n>>>16),0x85ebca6b)>>>0;return ((n^(n>>>13))>>>0)/4294967296;
  }
  function note(time,event,data={}){notes.push({seconds:+time.toFixed(4),event,...data});}
  const idleKinds=['watch','pace','still','test','scan'];
  const durations={watch:[4.4,3.8],pace:[8.1,4.5],still:[3.6,4.0],test:[4.9,1.5],scan:[4.3,3.7]};
  function nextIdleKind(index){
    if(!index)return 'watch';
    const previous=intervals.at(-1).kind;
    let selected,highest=-Infinity;
    for(const [k,kind] of idleKinds.entries()){
      if(kind===previous)continue;
      const last=intervals.findLastIndex(c=>c.kind===kind);
      const age=last<0?index+2:index-last;
      const score=age*.64+random(index,20+k)*3.1;
      if(score>highest){highest=score;selected=kind;}
    }
    return selected;
  }
  function idleInterval(t){
    while(!intervals.length || intervals.at(-1).end<=t){
      const i=intervals.length,start=i?intervals[i-1].end:0;
      const kind=nextIdleKind(i),range=durations[kind];
      const d=range[0]+range[1]*random(i);intervals.push({i,start,end:start+d,kind});
    }
    return intervals.find(a=>a.end>t)||intervals.at(-1);
  }
  function look(yaw,pitch,roll=0){
    nodes.neck.quaternion.copy(neckRest).multiply(new T.Quaternion().setFromEuler(new T.Euler(pitch*.44,yaw*.46,roll*.65,'YXZ')));
    nodes.head.quaternion.copy(headRest).multiply(new T.Quaternion().setFromEuler(new T.Euler(pitch*.56,yaw*.54,roll*.35,'YXZ')));
    root.updateWorldMatrix(true,true);
  }
  function timeline(t,epoch){
    const rel=Math.max(0,t-epoch),cue=idleInterval(rel),u=clamp((rel-cue.start)/(cue.end-cue.start));
    const sign=random(cue.i,3)>.5?1:-1;
    const agitation=.18+.34*random(cue.i,7),easeInOut=Math.sin(Math.PI*u)**2;
    let pose={},aim=0,pitch=0,roll=0;
    if(cue.kind==='pace'){
      gait.set('patrol',u,{stride:-.58-.30*random(cue.i,1)});
      pose=gait.snapshot();aim=sign*(.19+.21*random(cue.i,4))*Math.sin(Math.PI*u*2)*easeInOut;
      pitch=.05*Math.sin(u*8*Math.PI)*easeInOut;
    }else if(cue.kind==='test'){
      const q=bell(u,.11,.43,.65,.89),brace=bell(u,0,.28,.77,1);
      const side=sign<0?0:1;
      pose=gait.encounterPose({side,grip:q,curl:q,brace,pitch:.077*brace,leftGuard:.085*brace,rightGuard:.154*brace,jaw:.35*bell(u,.35,.44,.56,.74)});
      aim=sign*.19*brace;pitch=.17*brace;
    }else{
      // Each attention state changes the profile as well as the head direction.
      // Both stance feet stay on their sockets throughout these weight changes.
      const side=sign<0?0:1;
      let stance={side},amount=0;
      if(cue.kind==='scan'){
        const first=bell(u,.03,.20,.37,.59),second=bell(u,.40,.62,.78,.97);
        amount=Math.max(first,second);
        aim=sign*(.53*first-.41*second);pitch=-.13*amount;roll=sign*.075*(first-second);
        stance={side,bodyFore:-.038*amount,bodyHeight:-.008*amount,pitch:-.12*amount,
          leftGuard:.042*amount,rightGuard:.112*amount};
      }else if(cue.kind==='watch'){
        const settle=bell(u,.03,.24,.72,.96),recheck=bell(u,.42,.52,.59,.67);
        amount=settle;aim=sign*(.26*settle+.09*recheck);pitch=.13*settle-.09*recheck;roll=sign*.080*settle;
        stance={side,bodyFore:.037*settle,bodyHeight:-.020*settle,pitch:.113*settle,brace:.42*settle,
          leftGuard:.043*settle,rightGuard:.133*settle,jaw:.11*recheck};
      }else{
        // The middle of the hold is genuinely still, including the jaw and both neck joints.
        const freeze=bell(u,0,.18,.80,1);
        amount=freeze;aim=sign*.13*freeze;pitch=.235*freeze;roll=-sign*.035*freeze;
        stance={side,bodyFore:.056*freeze,bodyHeight:-.042*freeze,pitch:.164*freeze,brace:.73*freeze,
          leftGuard:.090*freeze,rightGuard:.172*freeze};
      }
      if(amount>0)pose={...gait.encounterPose(stance),bodyHeight:stance.bodyHeight,pitch:stance.pitch,brace:stance.brace||0};
      else {gait.set('rest',0);pose=gait.snapshot();}
    }
    look(aim,pitch,roll);
    return {sourceId:'idle/'+epoch+'/'+cue.i,phase:cue.kind,label:labels[cue.kind],lane:null,aim,pitch,roll,agitation,pose,activeContact:cue.kind==='test'&&pose.grip>.9999&&Math.abs(pose.contactGap)<.00003};
  }
  function faceAt(c,t){return c.withdrawEarly!==undefined && t>=c.withdrawEarly?'withdraw':t<.54?'notice':t<1.23?'orient':t<2.20?'approach':t<3.10?'warning':t<3.62?'commit':t<4.17?'contact':t<5.62?'recover':'cooldown';}
  function eventPose(c,elapsed){
    const r=Math.max(0,elapsed-c.at),phase=faceAt(c,r);
    const early=c.withdrawEarly!==undefined && r>=c.withdrawEarly;
    const h=early?c.withdrawEarly:r;
    const returnScale=early?1-step(r,c.withdrawEarly,c.withdrawEarly+1.05):1-step(r,4.14,5.56);
    const approach=step(h,1.22,2.22),align=step(h,.13,1.23);
    const yaw=lerp(c.fromAim,laneYaw[c.lane],align)*returnScale;
    const grip=step(h,2.92,3.62)*returnScale;
    const brace=step(h,.95,2.38)*returnScale;
    const snap=bell(h,2.85,3.22,3.36,3.85)*returnScale;
    const warning=bell(h,1.75,2.40,3.05,3.28)*returnScale;
    const incoming=1-step(r,0,1.12),s=c.fromPose;
    // Keep an interrupted stance foot planted while the opposite foot completes
    // its short return. Shift any inherited placement only during its lifted turn.
    const returnL=1-step(r,0,.59), returnR=1-step(r,.59,1.18);
    const resumeLiftL=Math.abs(s.leftFore||0)*.38*Math.sin(Math.PI*clamp(r/.59))**2;
    const resumeLiftR=Math.abs(s.rightFore||0)*.38*Math.sin(Math.PI*clamp((r-.59)/.59))**2;
    const side=c.lane==='right'?1:c.lane==='left'?0:c.index%2;
    const pose=gait.encounterPose({side,grip,curl:grip,brace:brace+(s.brace||0)*incoming,bodyHeight:(s.bodyHeight||0)*incoming-.012*brace-.009*snap,pitch:(s.pitch||0)*incoming+.055*brace+.072*snap,
      bodyFore:(s.bodyFore||0)*incoming+.044*approach*returnScale+.029*snap,
      leftFore:(s.leftFore||0)*returnL,rightFore:(s.rightFore||0)*returnR,
      leftLift:(s.leftLift||0)*incoming+resumeLiftL,rightLift:(s.rightLift||0)*incoming+resumeLiftR,
      leftGuard:(s.leftGuard||0)*incoming+.090*brace,rightGuard:(s.rightGuard||0)*incoming+.163*brace,jaw:.91*warning+.18*grip});
    look(yaw,c.fromPitch*incoming+.078*brace-.089*warning+.190*snap,c.fromRoll*incoming+(side===0?1:-1)*.022*brace);
    const contact=grip>.9999 && Math.abs(pose.contactGap)<.00003;
    const cooldown=Math.max(0,c.end-elapsed);
    return {sourceId:'reach/'+c.index+'/'+c.at,phase,label:labels[phase],lane:c.lane,aim:yaw,agitation:early?.18+.30*returnScale:.19+.59*brace,pose,
      activeContact:contact,committed:!early&&r>=3.10,withdrew:c.withdrawEarly!==undefined||c.withdrewLate,cooldownRemaining:phase==='cooldown'||phase==='withdraw'?cooldown:0};
  }
  function select(t){
    let episode;for(const c of commands){if(c.at<=t)episode=c;else break;}
    if(episode&&t<=episode.end)return eventPose(episode,t);
    return timeline(t,episode?episode.end:0);
  }
  function sample(seconds=0){
    const t=Math.max(0,Number.isFinite(seconds)?seconds:0);fixture.visible=true;
    const next=select(t);const phaseKey=next.sourceId+'|'+next.phase,contactKey=next.sourceId+'|rail-contact';
    if(t>=lastSample && phaseKey!==lastPhase && !observed.has(phaseKey)){note(t,'phase',{phase:next.phase,lane:next.lane});observed.add(phaseKey);}
    if(t>=lastSample&&next.activeContact&&!observed.has(contactKey)){note(t,'contact',{lane:next.lane,point:next.pose.tip,gap:next.pose.contactGap});observed.add(contactKey);}
    lastPhase=phaseKey;
    state={...next,seconds:t,contactCount:notes.filter(e=>e.event==='contact'&&e.seconds<=t).length,contactPoint:next.activeContact?next.pose.tip:null};lastSample=t;return snapshot();
  }
  function reach(lane,seconds){
    if(!Object.hasOwn(laneYaw,lane))throw RangeError('Use left, center or right');
    const t=Math.max(0,Number.isFinite(seconds)?seconds:0);const live=commands.find(c=>c.at<=t&&c.end>=t);
    if(live){note(t,'repeat-input-held',{lane,activeLane:live.lane});return {accepted:false,phase:sample(t).phase};}
    const before=sample(t);commands.push({index:commands.length,lane,at:t,end:t+8.85,fromPose:{...before.pose},
      fromAim:before.aim,fromPitch:before.pitch||0,fromRoll:before.roll||0});
    commands.sort((a,b)=>a.at-b.at);note(t,'reach',{lane});return {accepted:true,...sample(t)};
  }
  function retreat(seconds){
    const t=Math.max(0,Number.isFinite(seconds)?seconds:0);const c=commands.find(e=>e.at<=t && e.end>=t);
    if(!c)return {accepted:false,...sample(t)};
    const r=t-c.at;
    if(c.withdrawEarly!==undefined||c.withdrewLate)return {accepted:false,...sample(t)};
    if(r<3.10){c.withdrawEarly=r;c.end=t+2.76;note(t,'early-withdrawal',{lane:c.lane});}
    else{c.withdrewLate=true;note(t,'committed-withdrawal',{lane:c.lane});}
    return {accepted:true,...sample(t)};
  }
  function snapshot(){return state?{...state,pose:{...state.pose}}:{phase:'rest',label:'At rest',seconds:0,agitation:0,activeContact:false,contactCount:0,cooldownRemaining:0,lane:null};}
  function reset(newSeed=0){
    seed=Number.isFinite(newSeed)?newSeed|0:0;intervals=[];commands=[];notes=[];observed.clear();lastPhase='';lastSample=-1;state=null;fixture.visible=false;
    gait.set('rest',0);nodes.neck.quaternion.copy(neckRest);nodes.head.quaternion.copy(headRest);root.updateWorldMatrix(true,true);
  }
  function dispose(){reset();fixture.removeFromParent();geo.dispose();steel.dispose();bronze.dispose();}
  reset();return {sample,reach,retreat,reset,snapshot,events:()=>notes.map(x=>({...x})),dispose};
}
