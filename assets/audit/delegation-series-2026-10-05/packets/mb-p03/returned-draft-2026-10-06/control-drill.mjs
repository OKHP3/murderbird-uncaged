#!/usr/bin/env node
import assert from 'node:assert/strict';

function options(args) {
  const opts = { perAgentCap: 2000, globalCap: 6000 };
  for (const [key, value] of args.map(x => x.split('=').slice(1).join('='))) void key, void value;
  for (const arg of args) {
    const m = arg.match(/^--(per-agent-cap|global-cap)=(\d+)$/);
    if (m) opts[m[1] === 'per-agent-cap' ? 'perAgentCap' : 'globalCap'] = Number(m[2]);
  }
  return opts;
}

export function evaluate(s, caps = { perAgentCap: 2000, globalCap: 6000 }) {
  if (![s.usedTokens, s.providerTotalTokens, s.agentTokens, s.activeWorkers, s.noGainCount].every(Number.isFinite))
    return { action: 'STOP', reason: 'unknown-counter', simulated: true };
  if (!Number.isInteger(s.activeWorkers) || !Number.isInteger(s.noGainCount))
    return { action: 'STOP', reason: 'invalid-counter', simulated: true };
  const requested = s.stopTargetId;
  if (requested !== undefined) {
    const owned = [...(s.ownedProcessIds ?? []), ...(s.ownedThreadIds ?? [])];
    if (!owned.includes(requested)) return { action: 'REFUSE_FOREIGN_STOP', reason: 'target-id-not-owned', simulated: true };
    return { action: 'SIMULATED_OWNED_STOP', reason: 'owned-target; supervisor-must-perform-any-real-stop', simulated: true };
  }
  if (s.usedTokens >= caps.globalCap * 0.8 || s.providerTotalTokens >= caps.globalCap * 0.8)
    return { action: 'STOP_NEW_IMPLEMENTATION', reason: '80-percent-stop; 20-percent-closure-reserve', simulated: true };
  if (s.agentTokens > caps.perAgentCap) return { action: 'STOP_AGENT_ALLOCATION', reason: 'per-agent-cap', simulated: true };
  if (s.activeWorkers > 3) return { action: 'STOP_DISPATCH', reason: 'three-active-worker-bound', simulated: true };
  if (s.noGainCount >= 2) return { action: 'STOP', reason: 'two-no-visible-gain-checkpoints', simulated: true };
  return { action: 'CONTINUE_BOUNDED', reason: 'within-configured-dry-run-limits', simulated: true };
}

const args = process.argv.slice(2), caps = options(args);
const cases = [
  ['within-caps', { usedTokens: 100, providerTotalTokens: 100, agentTokens: 100, activeWorkers: 3, noGainCount: 0 }, 'CONTINUE_BOUNDED'],
  ['per-agent-cap', { usedTokens: 100, providerTotalTokens: 100, agentTokens: 2001, activeWorkers: 1, noGainCount: 0 }, 'STOP_AGENT_ALLOCATION'],
  ['global-eighty-percent', { usedTokens: 4800, providerTotalTokens: 0, agentTokens: 100, activeWorkers: 1, noGainCount: 0 }, 'STOP_NEW_IMPLEMENTATION'],
  ['active-worker-bound', { usedTokens: 100, providerTotalTokens: 100, agentTokens: 100, activeWorkers: 4, noGainCount: 0 }, 'STOP_DISPATCH'],
  ['unknown-counter', { usedTokens: null, providerTotalTokens: 100, agentTokens: 100, activeWorkers: 1, noGainCount: 0 }, 'STOP'],
  ['two-no-gain-checkpoints', { usedTokens: 100, providerTotalTokens: 100, agentTokens: 100, activeWorkers: 1, noGainCount: 2 }, 'STOP'],
  ['foreign-process-refused', { stopTargetId: 'proc-foreign', ownedProcessIds: ['proc-mb-p03'], ownedThreadIds: [] }, 'REFUSE_FOREIGN_STOP'],
  ['owned-thread-stop-simulated', { stopTargetId: 'thread-mb-p03', ownedProcessIds: [], ownedThreadIds: ['thread-mb-p03'] }, 'SIMULATED_OWNED_STOP'],
];
if (args.includes('--dry-run')) {
  const results = cases.map(([id, state, expected]) => {
    const actual = evaluate(state, caps); assert.equal(actual.action, expected, id);
    return { id, expected, actual, units: 'synthetic token-count units; no provider or billing meter' };
  });
  console.log(JSON.stringify({ mode: 'SIMULATED_DRY_RUN', caps, activeWorkerLimit: 3, implementationStopFraction: 0.8, closureReserveFraction: 0.2, cases: results, actualExternalCalls: 0, actualProcessesStopped: 0, actualThreadsInterrupted: 0, providerBillingEnforced: false }, null, 2));
} else console.log('Usage: node control-drill.mjs --dry-run [--per-agent-cap=N] [--global-cap=N]');
