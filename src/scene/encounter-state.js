/**
 * A small, renderer-independent timeline for the exhibit's reach response.
 * Time passed to update() is measured in seconds. Each update accepts at most
 * 100 ms so a suspended tab cannot jump straight through the entire response.
 *
 * The `maker` era is an interpretive exhibit response, not evidence of a brain
 * or of neural function. Era labels do not change the mechanics of this model.
 */

export const ENCOUNTER_DURATIONS = Object.freeze({
  notice: 0.8,
  warning: 0.8,
  strike: 0.3,
  contact: 0.2,
  recover: 0.8,
  cooldown: 1.0,
});

const MAX_FRAME_DELTA = 0.1;
const REACH_LIMIT = 1;
const VALID_ERAS = new Set(['maker', 'mechanic', 'builder']);
const NORMAL_TRANSITIONS = Object.freeze({
  notice: 'warning',
  warning: 'strike',
  strike: 'contact',
  contact: 'recover',
  recover: 'cooldown',
  cooldown: 'idle',
});
const REDUCED_TRANSITIONS = Object.freeze({
  notice: 'warning',
  warning: 'recover',
  recover: 'cooldown',
  cooldown: 'idle',
});

function finiteNumber(value, fallback = 0) {
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

/**
 * Create an encounter response state machine.
 *
 * `onChange`, when provided, receives a fresh immutable snapshot whenever a
 * visible value changes. A reach can begin only while idle and unpaused,
 * outside inspection. `requestReach` returns whether the request was accepted.
 */
export function createEncounterState({ onChange } = {}) {
  let state = 'idle';
  let elapsed = 0;
  let reach = { x: 0, y: 0 };
  let paused = false;
  let inspection = false;
  let reducedMotion = false;
  let era = 'maker';

  function makeSnapshot() {
    const snapshot = {
      state,
      phase: state === 'idle' ? 0 : clamp(elapsed / ENCOUNTER_DURATIONS[state], 0, 1),
      reach: { x: reach.x, y: reach.y },
      paused,
      inspection,
      reducedMotion,
      era,
    };
    Object.freeze(snapshot.reach);
    return Object.freeze(snapshot);
  }

  function emit() {
    if (typeof onChange === 'function') onChange(makeSnapshot());
  }

  function cancelReaction(emitWhenUnchanged = false) {
    const changed = state !== 'idle' || elapsed !== 0 || reach.x !== 0 || reach.y !== 0;
    state = 'idle';
    elapsed = 0;
    reach = { x: 0, y: 0 };
    if (changed || emitWhenUnchanged) emit();
  }

  function getSnapshot() {
    return makeSnapshot();
  }

  function requestReach(input = {}) {
    if (state !== 'idle' || paused || inspection) return false;

    const safeInput = input && typeof input === 'object' ? input : {};
    reach = {
      x: clamp(finiteNumber(safeInput.x), -REACH_LIMIT, REACH_LIMIT),
      y: clamp(finiteNumber(safeInput.y), -REACH_LIMIT, REACH_LIMIT),
    };
    state = 'notice';
    elapsed = 0;
    emit();
    return true;
  }

  function update(dtSeconds) {
    if (state === 'idle' || paused || inspection) return getSnapshot();

    const dt = clamp(finiteNumber(dtSeconds), 0, MAX_FRAME_DELTA);
    if (dt === 0) return getSnapshot();

    elapsed += dt;
    let changed = false;
    while (state !== 'idle' && elapsed + 1e-9 >= ENCOUNTER_DURATIONS[state]) {
      elapsed = Math.max(0, elapsed - ENCOUNTER_DURATIONS[state]);
      const transitions = reducedMotion ? REDUCED_TRANSITIONS : NORMAL_TRANSITIONS;
      state = transitions[state];
      changed = true;
      if (state === 'idle') {
        elapsed = 0;
        reach = { x: 0, y: 0 };
      }
    }
    if (changed || dt > 0) emit();
    return getSnapshot();
  }

  function setInspection(value) {
    const next = Boolean(value);
    if (inspection === next) return getSnapshot();
    inspection = next;
    if (next) {
      cancelReaction(true);
    } else {
      emit();
    }
    return getSnapshot();
  }

  function setPaused(value) {
    const next = Boolean(value);
    if (paused === next) return getSnapshot();
    paused = next;
    if (next) {
      cancelReaction(true);
    } else {
      emit();
    }
    return getSnapshot();
  }

  function setReducedMotion(value) {
    const next = Boolean(value);
    if (reducedMotion === next) return getSnapshot();
    reducedMotion = next;
    cancelReaction(true);
    return getSnapshot();
  }

  function setEra(value) {
    if (!VALID_ERAS.has(value)) return false;
    if (era === value) return true;
    era = value;
    state = 'idle';
    elapsed = 0;
    reach = { x: 0, y: 0 };
    emit();
    return true;
  }

  function reset() {
    const changed = state !== 'idle' || elapsed !== 0 || reach.x !== 0 || reach.y !== 0;
    state = 'idle';
    elapsed = 0;
    reach = { x: 0, y: 0 };
    if (changed) emit();
    return getSnapshot();
  }

  return Object.freeze({
    requestReach,
    update,
    setInspection,
    setPaused,
    setReducedMotion,
    setEra,
    reset,
    getSnapshot,
  });
}
