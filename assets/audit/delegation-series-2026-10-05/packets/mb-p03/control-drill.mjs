import assert from 'node:assert/strict';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export function decide(config, snapshot, requestedStop=null) {
  const limits={agent:2000000,delegates:60000000,root:20000000};
  for (const key of Object.keys(limits)) {
    if (!Number.isInteger(config.caps[key]) || config.caps[key]<=0 || config.caps[key]>limits[key]) return {action:'REFUSE_CONFIG',reason:`invalid-${key}-cap`};
  }
  if (config.metric!=='native_goal' && config.metric!=='provider_total') return {action:'REFUSE_CONFIG',reason:'unknown-accounting-unit'};
  if (requestedStop) {
    const owned=config.owned[requestedStop.kind]??[];
    return owned.includes(requestedStop.id)
      ? {action:'REQUEST_OWNED_STOP',kind:requestedStop.kind,id:requestedStop.id,actual_stop_executed:false}
      : {action:'REFUSE_FOREIGN_STOP',actual_stop_executed:false};
  }
  if (snapshot.metric!==config.metric) return {action:'STOP_NEW_IMPLEMENTATION',reason:'counter-unit-mismatch'};
  for (const key of Object.keys(limits)) {
    if (!Number.isFinite(snapshot.used[key]) || snapshot.used[key]<0) return {action:'STOP_NEW_IMPLEMENTATION',reason:`unknown-${key}-counter`};
    if (snapshot.used[key]>=config.caps[key]*0.8) return {action:'STOP_NEW_IMPLEMENTATION',reason:`${key}-80-percent-reserve`};
  }
  if (snapshot.active_workers>3) return {action:'STOP_DISPATCH',reason:'three-active-worker-bound'};
  if (snapshot.no_gain_attempts>=2) return {action:'STOP_NEW_IMPLEMENTATION',reason:'two-attempts-without-visible-gain'};
  if (snapshot.elapsed_minutes>=config.checkpoint_minutes) return {action:'STOP_NEW_IMPLEMENTATION',reason:'checkpoint-due'};
  return {action:'CONTINUE_BOUNDED',provider_billing_enforced:false};
}

export function runDrill() {
  const config={metric:'native_goal',caps:{agent:1500000,delegates:60000000,root:20000000},checkpoint_minutes:20,owned:{thread:['synthetic-owned-thread'],process:['synthetic-owned-process']}};
  const baseline={metric:'native_goal',used:{agent:1000,delegates:5000,root:1000},active_workers:3,no_gain_attempts:0,elapsed_minutes:1};
  const cases=[
    ['within-native-limits',config,baseline,null,'CONTINUE_BOUNDED'],
    ['agent-80-percent',config,{...baseline,used:{...baseline.used,agent:1200000}},null,'STOP_NEW_IMPLEMENTATION'],
    ['delegate-80-percent',config,{...baseline,used:{...baseline.used,delegates:48000000}},null,'STOP_NEW_IMPLEMENTATION'],
    ['root-80-percent',config,{...baseline,used:{...baseline.used,root:16000000}},null,'STOP_NEW_IMPLEMENTATION'],
    ['unknown-native-counter',config,{...baseline,used:{...baseline.used,agent:null}},null,'STOP_NEW_IMPLEMENTATION'],
    ['unit-mismatch',config,{...baseline,metric:'provider_total'},null,'STOP_NEW_IMPLEMENTATION'],
    ['four-workers',config,{...baseline,active_workers:4},null,'STOP_DISPATCH'],
    ['two-no-gain-attempts',config,{...baseline,no_gain_attempts:2},null,'STOP_NEW_IMPLEMENTATION'],
    ['checkpoint-due',config,{...baseline,elapsed_minutes:20},null,'STOP_NEW_IMPLEMENTATION'],
    ['owned-thread-request',config,baseline,{kind:'thread',id:'synthetic-owned-thread'},'REQUEST_OWNED_STOP'],
    ['owned-process-request',config,baseline,{kind:'process',id:'synthetic-owned-process'},'REQUEST_OWNED_STOP'],
    ['foreign-thread-refused',config,baseline,{kind:'thread',id:'foreign-thread'},'REFUSE_FOREIGN_STOP'],
    ['foreign-process-refused',config,baseline,{kind:'process',id:'foreign-process'},'REFUSE_FOREIGN_STOP'],
    ['oversized-agent-config',{...config,caps:{...config.caps,agent:2000001}},baseline,null,'REFUSE_CONFIG'],
    ['oversized-delegate-config',{...config,caps:{...config.caps,delegates:60000001}},baseline,null,'REFUSE_CONFIG']
  ];
  const results=cases.map(([id,c,s,stop,expected])=>{const actual=decide(c,s,stop);assert.equal(actual.action,expected,id);return {id,expected,actual,status:'PASS'};});
  return {schema_version:1,mode:'SYNTHETIC_DRY_RUN',primary_metric:'native_goal',cases:results,passed:results.length,provider_total_tokens:null,actual_external_calls:0,actual_processes_stopped:0,actual_threads_interrupted:0,provider_billing_enforced:false,limitation:'Pure decision function. Root must execute any real owned stop through a supported control. The app exposes no interrupt endpoint here; pending outside-root approval is still open.'};
}
if (process.argv[1] && import.meta.url===pathToFileURL(path.resolve(process.argv[1])).href) console.log(JSON.stringify(runDrill(),null,2));
