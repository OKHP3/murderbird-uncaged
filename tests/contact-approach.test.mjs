import test from 'node:test';
import assert from 'node:assert/strict';
import { createPresenceState } from '../src/scene/presence-state.js';

test('visitor and autonomous contact routes consume the loaded geometry approach', () => {
  for (const visitor of [true, false]) {
    const machine=createPresenceState({seed:927});
    if(visitor)assert.equal(machine.requestReach({x:0}),true);
    let found=false;
    for(let frame=0;frame<600;frame++) {
      const state=machine.update(.1,{arrived:true,settled:true,aligned:true,contactApproachZ:1.046});
      if(state.state===(visitor?'approach':'boundary')) {
        assert.equal(state.goal.z,1.046);found=true;break;
      }
    }
    assert.ok(found, 'Contact approach state was not reached.');
  }
});

test('invalid geometry feedback cannot send a route outside the existing cage root bounds', () => {
  for(const value of [NaN,Infinity,2,-2]) {
    const machine=createPresenceState();machine.requestReach({x:0});
    let found=false;
    for(let frame=0;frame<20;frame++) {
      const state=machine.update(.1,{arrived:true,settled:true,aligned:true,contactApproachZ:value});
      if(state.state==='approach'){assert.equal(state.goal.z,1.02);found=true;break;}
    }
    assert.ok(found);
  }
});
