import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { validateProgram, dispatchRequest, followupRequest, status, PROGRAM_PATH } from '../scripts/delegation-program.mjs';

const program=JSON.parse(fs.readFileSync(PROGRAM_PATH,'utf8'));
const source=JSON.parse(fs.readFileSync(program.reviewed_source.path,'utf8'));
const copy=()=>structuredClone(program);
const main=process.cwd();
const isolated=path.join(main,'tests','fixtures');

test('reviewed source has complete task, criterion and finding assignment coverage',()=>{
  assert.deepEqual(validateProgram(program,source).errors,[]);
  assert.equal(program.packets.length,30);
  assert.equal(new Set(program.packets.flatMap(p=>p.source_task_ids)).size,61);
  assert.deepEqual(program.reviewed_source.closed_task_ids,['MB-T029']);
  assert.equal(Object.keys(program.scenario_task_map).length,18);
});
test('cycle prevents a misleading executable dependency graph',()=>{
  const p=copy();p.packets[0].dispatch_dependencies=['MB-P03'];p.packets[2].dispatch_dependencies=['MB-P01'];
  assert.match(validateProgram(p,source).errors.join(' '),/cycle/);
});
test('over-budget or overlapping/production paths fail validation',()=>{
  const p=copy();p.packets[0].native_goal_ceiling_tokens=2000001;p.packets[1].owned_path=p.packets[0].owned_path;
  assert.match(validateProgram(p,source).errors.join(' '),/native cap/);
  assert.match(validateProgram(p,source).errors.join(' '),/owned path/);
  p.packets[1].owned_path='public/private-session/';
  assert.match(validateProgram(p,source).errors.join(' '),/owned path/);
});
test('an incomplete startup is not a verified prerequisite',()=>{
  const s={threads:[{packet_id:'MB-P01',status:'BUDGET_LIMITED_INCOMPLETE'},{packet_id:'MB-P02',status:'VERIFIED'},{packet_id:'MB-P03',status:'VERIFIED'}]};
  assert.ok(!status(program,s).ready.includes('MB-P05'));
  s.threads[0].status='VERIFIED';assert.ok(status(program,s).ready.includes('MB-P05'));
});
test('gated packets cannot launch accidentally and main cannot be assigned',()=>{
  assert.throws(()=>dispatchRequest(program,{threads:[]},'MB-P06',isolated,main),/not selected/);
  assert.throws(()=>dispatchRequest(program,{threads:[]},'MB-P01',main,main),/main checkout/);
});
test('three active threads including a pending approval block dispatch',()=>{
  const s={threads:['RUNNING','WAITING_ON_APPROVAL','CLOSING'].map((status,i)=>({packet_id:`other${i}`,status}))};
  assert.throws(()=>dispatchRequest(program,s,'MB-P01',isolated,main),/three active/);
});
test('retired budget-limited runs still consume thread and allocation slots',()=>{
  const s={threads:Array.from({length:30},(_,i)=>({packet_id:`other${i}`,status:'BUDGET_LIMITED_INCOMPLETE',native_goal_ceiling_tokens:1500000}))};
  assert.throws(()=>dispatchRequest(program,s,'MB-P01',isolated,main),/30-thread/);
});
test('structured launch uses the small model and registers a real native ceiling',()=>{
  const r=dispatchRequest(program,{threads:[],project_id:'test-project'},'MB-P01',isolated,main);
  assert.equal(r.model,'gpt-6-luna');assert.equal(r.thinking,'low');
  assert.match(r.prompt,/FIRST call create_goal/);assert.match(r.prompt,/provider\/billing guarantee/);
  assert.equal(r.target.environment.type,'local');
});
test('completed verified threads may take another packet within their cumulative ceiling',()=>{
  const s={project_id:'test-project',threads:[{packet_id:'MB-P01',thread_id:'owned-complete',host_id:'local',status:'VERIFIED',native_tokens_used:62680}]};
  const r=followupRequest(program,s,'MB-P23',isolated,'owned-complete',main);
  assert.equal(r.threadId,'owned-complete');assert.match(r.prompt,/Prior native usage: 62680/);
  s.threads[0].native_tokens_used=600000;
  assert.throws(()=>followupRequest(program,s,'MB-P23',isolated,'owned-complete',main),/cumulative/);
  s.threads[0].status='BUDGET_LIMITED_INCOMPLETE';
  assert.throws(()=>followupRequest(program,s,'MB-P23',isolated,'owned-complete',main),/completed independently/);
});

test('reusing a thread does not redispatch its verified earlier packet',()=>{
  const s={project_id:'test-project',threads:[{packet_id:'MB-P17',thread_id:'reused',status:'VERIFIED',native_tokens_used:111353}],
    packet_acceptances:[{packet_id:'MB-P01',status:'VERIFIED_PREP_SLICE'}]};
  assert.ok(status(program,s).verified.includes('MB-P01'));
  assert.ok(!status(program,s).ready.includes('MB-P01'));
  assert.throws(()=>dispatchRequest(program,s,'MB-P01',isolated,main),/already active\/complete/);
});
