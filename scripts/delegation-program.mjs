import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import crypto from 'node:crypto';

export const PROGRAM_PATH = 'docs/delegation-series-2026-10-05/program.json';
export const STATE_PATH = '.local/delegation-series-20261005/state.json';
const activeStates = new Set(['RUNNING', 'WAITING_ON_APPROVAL', 'CLOSING']);
const terminalStates = new Set(['VERIFIED', 'DELIVERED', 'BUDGET_LIMITED_INCOMPLETE', 'FAILED', 'RETIRED_INCOMPLETE']);

export function validateProgram(program, source) {
  const errors = [];
  const packets = program.packets ?? [];
  const ids = packets.map(p => p.packet_id);
  if (packets.length > 30 || new Set(ids).size !== ids.length) errors.push('duplicate packet or more than 30 packets');
  if (program.authority.max_delegate_threads > 30 || program.authority.max_active_delegates > 3) errors.push('thread/concurrency ceiling');
  if (program.authority.superintendent_native_token_budget > 20000000) errors.push('superintendent ceiling');
  if (program.authority.delegate_aggregate_ceiling > 60000000) errors.push('delegate aggregate ceiling');
  const owned = new Set();
  for (const p of packets) {
    if (p.native_goal_ceiling_tokens > 2000000 || !Number.isInteger(p.native_goal_ceiling_tokens) || p.native_goal_ceiling_tokens <= 0) errors.push(`${p.packet_id}: native cap`);
    const normalized = path.posix.normalize(p.owned_path);
    const expectedPath = `assets/audit/delegation-series-2026-10-05/packets/${p.packet_id.toLowerCase()}/`;
    if (normalized !== expectedPath || normalized.includes('..') || owned.has(normalized)) errors.push(`${p.packet_id}: owned path`);
    owned.add(normalized);
    for (const d of p.dispatch_dependencies) if (!ids.includes(d)) errors.push(`${p.packet_id}: missing dependency ${d}`);
  }
  const visiting = new Set(), visited = new Set();
  function visit(id) {
    if (visiting.has(id)) { errors.push(`dependency cycle at ${id}`); return; }
    if (visited.has(id)) return;
    visiting.add(id);
    packets.find(p => p.packet_id === id)?.dispatch_dependencies.forEach(visit);
    visiting.delete(id); visited.add(id);
  }
  ids.forEach(visit);
  if (source) {
    const covered = new Set([...packets.flatMap(p => p.source_task_ids), ...program.reviewed_source.closed_task_ids]);
    const expected = source.tasks.map(t => t.task_id);
    for (const id of expected) if (!covered.has(id)) errors.push(`unmapped source task ${id}`);
    for (const id of covered) if (!expected.includes(id)) errors.push(`invented source task ${id}`);
    const criteria = new Set(packets.flatMap(p => p.criterion_ids));
    const findings = new Set(packets.flatMap(p => p.finding_ids));
    for (const id of Object.keys(source.criterion_task_map)) if (!criteria.has(id) && !source.criterion_task_map[id].task_ids.every(t => program.reviewed_source.closed_task_ids.includes(t))) errors.push(`unmapped criterion ${id}`);
    for (const id of Object.keys(source.finding_task_map)) if (!findings.has(id)) errors.push(`unmapped finding ${id}`);
  }
  return { valid: !errors.length, errors, packet_count: packets.length };
}

export function status(program, state) {
  const threads = state.threads ?? [];
  const active = threads.filter(t => activeStates.has(t.status));
  const verified = new Set([...threads.filter(t => t.status === 'VERIFIED').map(t => t.packet_id),
    ...(state.packet_acceptances??[]).filter(a=>a.status==='VERIFIED_PREP_SLICE').map(a=>a.packet_id)]);
  const already = new Set(threads.filter(t => !terminalStates.has(t.status) || ['VERIFIED','DELIVERED'].includes(t.status)).map(t => t.packet_id));
  const enabled = new Set([...program.initial_execution_tranche, ...(state.root_selected_packet_ids ?? [])]);
  const ready = program.packets.filter(p => enabled.has(p.packet_id) && !already.has(p.packet_id) && p.dispatch_dependencies.every(d => verified.has(d)));
  return { thread_count: threads.length, active_count: active.length, free_worker_slots: Math.max(0, 3-active.length),
    active: active.map(t => t.packet_id), verified: [...verified], ready: ready.map(p => p.packet_id),
    not_selected: program.packets.filter(p => !enabled.has(p.packet_id)).map(p => p.packet_id),
    native_tokens_reported: threads.reduce((s,t) => s+(t.native_tokens_used ?? 0),0),
    missing_usage_threads: threads.filter(t => t.native_tokens_used == null).map(t => t.thread_id),
    provider_total_tokens: null, provider_billing_enforcement: false };
}

export function dispatchRequest(program, state, packetId, checkout, mainRoot) {
  const p = program.packets.find(p => p.packet_id === packetId);
  if (!p) throw new Error('unknown packet');
  const s = status(program,state);
  if (s.active_count >= 3) throw new Error('three active workers already allocated');
  if (s.thread_count >= 30) throw new Error('30-thread limit reached; reuse a completed owned thread if appropriate');
  const booked = state.threads.reduce((sum,t) => sum+(t.native_goal_ceiling_tokens ?? t.operational_native_token_budget ?? 0),0);
  if (booked+p.native_goal_ceiling_tokens > program.authority.delegate_aggregate_ceiling) throw new Error('aggregate delegate cap');
  if (!s.ready.includes(packetId)) throw new Error('packet not selected, already active/complete, or prerequisites unverified');
  if (path.resolve(checkout) === path.resolve(mainRoot)) throw new Error('workers cannot edit the main checkout');
  if (!fs.existsSync(checkout)) throw new Error('isolated checkout absent');
  if (!state.project_id) throw new Error('resolve the native project id with list_projects before generating a launch request');
  return requestForPacket(program,state,p,checkout);
}

export function followupRequest(program,state,packetId,checkout,threadId,mainRoot) {
  const thread=state.threads.find(t=>t.thread_id===threadId);
  const p=program.packets.find(p=>p.packet_id===packetId);
  if (!thread || thread.status!=='VERIFIED') throw new Error('reuse only a completed independently verified thread');
  if (!p || !Number.isFinite(thread.native_tokens_used)) throw new Error('known cumulative thread usage required');
  if (thread.native_tokens_used+p.native_goal_ceiling_tokens>2000000) throw new Error('cumulative per-thread ceiling');
  const verified=status(program,state).verified.map(packet_id=>({packet_id,status:'VERIFIED_PREP_SLICE'}));
  const adjusted={...state,threads:state.threads.filter(t=>t!==thread),packet_acceptances:verified};
  const request=dispatchRequest(program,adjusted,packetId,checkout,mainRoot);
  return {threadId,hostId:thread.host_id,model:request.model,thinking:request.thinking,
    prompt:request.prompt+`\nReuse this completed thread within its cumulative owner ceiling. Prior native usage: ${thread.native_tokens_used}. Create a fresh packet goal only because the prior goal is genuinely complete; report the new goal usage separately so root can add both. Do not overwrite prior packet artifacts.`};
}

function requestForPacket(program,state,p,checkout) {
  const prompt = `You are ${p.packet_id}: ${p.title}. The owner authorized up to 30 individually tracked agents, max 2,000,000 tokens each. Your native goal ceiling is ${p.native_goal_ceiling_tokens}; your smaller checkpoint target is ${p.checkpoint_native_tokens_target} (estimate, not a spending target). FIRST call create_goal with token_budget:${p.native_goal_ceiling_tokens} and this bounded packet objective. Inspect get_goal at checkpoints; stop new implementation at 80% of the native ceiling, within 20 minutes or after two focused attempts; reserve closure. No provider/billing guarantee. No child agents or model change.\nIsolated checkout: ${path.resolve(checkout)} at ${program.source_base_sha}. Verify with git rev-parse HEAD; avoid LFS git status writes if unavailable. Read the current sections of goal.md, AGENTS.md and docs/incremental-delivery.md, plus the narrow Evidence Standard, Artifact Validation and Session Handoff skills under .agents/skills/. Keep historical reads targeted and <=12 bounded tool calls. Main checkout is read-only. Write only within the assigned isolated checkout's ${p.owned_path}; if your native writable roots do not include it, write under your native outputs/ directory and let root import. Never request broader filesystem access. Never modify existing tracked files, source binaries, public/, Git refs/index, remote/browser/apps, dependencies, billing or private archives.\nSource tasks: ${p.source_task_ids.join(', ')}. Current duty: ${p.immediate_duty}\nExpected: ${p.expected_outputs}. Boundary: ${p.acceptance_boundary}\nNo implementation of a visual/animation/mechanics gated phase unless root supplies an explicit current scope. Produce report.md <=900 words, result.json with packet_id/base_sha/outcome/changed_paths/checks/findings/remaining_product_gates/usage, and done.json last. Run only existing appropriate checks; do not rerun npm/build for artifact-only work. Register factual NOT RUN/UNKNOWN honestly; no source/PRD/artistic acceptance by inference. Capture native goal usage and provider_total_tokens:null, complete the goal only after real artifacts/checks exist, then record final completionBudgetReport in done.json. Final <=250 words; root reads artifacts. No cross-thread messages.`;
  return { title:`MurderBird ${p.packet_id}: ${p.title}`,model:p.model,thinking:p.reasoning_effort,
    target:{type:'project',projectId:state.project_id,environment:{type:'local'}},prompt };
}

function main() {
  const [command='status',packetId,checkout,threadId] = process.argv.slice(2);
  const program = JSON.parse(fs.readFileSync(PROGRAM_PATH,'utf8'));
  const state = fs.existsSync(STATE_PATH) ? JSON.parse(fs.readFileSync(STATE_PATH,'utf8')) : {threads:[]};
  if (command === 'check') {
    const bytes = fs.readFileSync(program.reviewed_source.path);
    const receipt = validateProgram(program,JSON.parse(bytes));
    receipt.source_hash_match = crypto.createHash('sha256').update(bytes).digest('hex') === program.reviewed_source.sha256;
    receipt.valid &&= receipt.source_hash_match;
    console.log(JSON.stringify(receipt,null,2));
    if (!receipt.valid) process.exitCode=1;
  } else if (command === 'prompt') {
    console.log(JSON.stringify(dispatchRequest(program,state,packetId,checkout,process.cwd()),null,2));
  } else if (command === 'followup') {
    console.log(JSON.stringify(followupRequest(program,state,packetId,checkout,threadId,process.cwd()),null,2));
  } else if (['status','ready'].includes(command)) console.log(JSON.stringify(status(program,state),null,2));
  else throw new Error('Use check, status, ready, prompt MB-Pxx <isolated-checkout>, or followup MB-Pxx <isolated-checkout> <completed-thread-id>. This CLI never launches or stops an agent.');
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) main();
