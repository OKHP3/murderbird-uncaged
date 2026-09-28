import assert from 'node:assert/strict';

/** Summarize observed motion samples without treating intention labels as acting. */
export function analyzeActingTrace(samples, { measuredSeconds = 120, maxGapSeconds = .25 } = {}) {
  assert(Array.isArray(samples) && samples.length > 1, 'At least two samples are required');
  assert(Number.isFinite(measuredSeconds) && measuredSeconds > 0);
  const first = samples[0].seconds;
  assert(Number.isFinite(first));
  const states = {}, families = {}, plans = [], actions = [], contacts = [], clawActions = [], clawContacts = [];
  let lastTime = first, maxGap = 0, action = null, contact = null, clawAction = null, clawContact = null, clawTelemetrySamples = 0, previousState;
  const finish = (interval, end, output) => {
    if (interval) output.push({ ...interval, end, duration: end - interval.start });
  };
  for (let i = 0; i < samples.length; i++) {
    const s = samples[i], prior = samples[i - 1];
    assert(Number.isFinite(s.seconds), `Sample ${i} has no finite clock`);
    assert(i === 0 || s.seconds > lastTime, `Sample ${i} clock does not advance`);
    assert.equal(s.era, 'builder', `Sample ${i} is not Advanced`);
    assert.equal(s.visitorPresent, false, `Sample ${i} contains visitor interaction`);
    assert.equal(s.paused, false, `Sample ${i} is paused`);
    assert.equal(s.inspection, false, `Sample ${i} is inspection`);
    assert.equal(s.reducedMotion, false, `Sample ${i} has reduced motion enabled`);
    assert.equal(typeof s.state, 'string');
    assert.equal(typeof s.motion?.contact, 'boolean', `Sample ${i} lacks actual contact telemetry`);
    // Older v3 receipts predate claw fields. Preserve their usefulness while
    // rejecting a claw-state sample that omits its actual renderer evidence.
    if (s.state === 'claw-scrape') {
      assert('clawAction' in s, `Sample ${i} lacks controller claw-action telemetry`);
      assert('clawAction' in s.motion, `Sample ${i} lacks renderer claw-action telemetry`);
    }
    assert(s.clawAction == null || typeof s.clawAction === 'object', `Sample ${i} has invalid controller claw-action telemetry`);
    const renderedClaw = s.motion.clawAction ?? null;
    assert(renderedClaw === null || typeof renderedClaw === 'object', `Sample ${i} has invalid renderer claw-action telemetry`);
    if (renderedClaw) {
      clawTelemetrySamples++;
      assert(['approach', 'lift', 'contact', 'scrape', 'release', 'recovery'].includes(renderedClaw.stage), `Sample ${i} has unknown renderer claw stage`);
      assert.equal(typeof renderedClaw.contact, 'boolean', `Sample ${i} lacks renderer claw-contact telemetry`);
      assert(Number.isFinite(renderedClaw.phase), `Sample ${i} lacks renderer claw phase`);
    }
    for (const key of ['x', 'z', 'yaw', 'speed']) assert(Number.isFinite(s.motion?.root?.[key]), `Sample ${i} lacks root.${key}`);
    for (const key of ['distance', 'steps']) assert(Number.isFinite(s.motion?.[key]), `Sample ${i} lacks finite motion.${key}`);
    const dt = s.seconds - lastTime;
    maxGap = Math.max(maxGap, dt);
    if (prior) states[prior.state] = (states[prior.state] || 0) + dt;
    if (s.state === 'pace' && previousState !== 'pace' && s.beatId) {
      plans.push({ start: s.seconds, id: s.beatId, family: s.actionFamily, route: s.routeKind, intensity: s.intensity });
    }
    // Count an action only once its actual action state is observed, not while
    // its family tag is present during a route or attention interval.
    const executing = s.state === 'cage-test';
    if (action && (!executing || action.family !== s.actionFamily)) {
      finish(action, s.seconds, actions); action = null;
    }
    if (executing && !action) action = { start: s.seconds, family: s.actionFamily, beatId: s.beatId };
    if (contact && !s.motion.contact) { finish(contact, s.seconds, contacts); contact = null; }
    if (s.motion.contact && !contact) contact = { start: s.seconds, family: s.actionFamily, beatId: s.beatId };
    // Approach only positions the foot. Start an executed episode only after
    // renderer telemetry shows the lift or a later action stage. A recovery
    // stage alone is insufficient because inspection/reduced-motion can
    // cancel an approach directly into recovery before any lift occurred.
    const clawStage = renderedClaw?.stage;
    const clawHasExecuted = ['lift', 'contact', 'scrape', 'release'].includes(clawStage);
    if (clawAction && !renderedClaw) {
      finish(clawAction, s.seconds, clawActions);
      clawAction = null;
    }
    if (!clawAction && clawHasExecuted) {
      clawAction = {
        start: s.seconds,
        beatId: s.beatId ?? null,
        family: 'claw-scrape',
        planFamily: s.actionFamily ?? null,
        side: renderedClaw.side ?? null,
        target: renderedClaw.target ?? null,
        stagesObserved: [],
        hadRendererContact: false,
      };
    }
    if (clawAction && renderedClaw) {
      if (clawAction.stagesObserved.at(-1) !== clawStage) clawAction.stagesObserved.push(clawStage);
      clawAction.hadRendererContact ||= renderedClaw.contact;
    }
    if (clawContact && !renderedClaw?.contact) {
      finish(clawContact, s.seconds, clawContacts);
      clawContact = null;
    }
    if (renderedClaw?.contact && !clawContact) {
      clawContact = { start: s.seconds, beatId: s.beatId ?? null, side: renderedClaw.side ?? null, target: renderedClaw.target ?? null };
    }
    previousState = s.state; lastTime = s.seconds;
  }
  finish(action, lastTime, actions); finish(contact, lastTime, contacts);
  finish(clawAction, lastTime, clawActions); finish(clawContact, lastTime, clawContacts);
  const duration = lastTime - first;
  assert(duration + 1e-6 >= measuredSeconds, `Only ${duration.toFixed(3)} seconds sampled; ${measuredSeconds} required`);
  assert(maxGap <= maxGapSeconds + 1e-6, `Telemetry gap ${maxGap.toFixed(3)}s exceeds ${maxGapSeconds}s`);
  const executedActions = [...actions, ...clawActions].sort((a, b) => a.start - b.start);
  for (const a of executedActions) families[a.family ?? 'unknown'] = (families[a.family ?? 'unknown'] || 0) + 1;
  const repeatedPlans = plans.filter((p, i) => i > 0 && p.id === plans[i - 1].id).length;
  const repeatedFamilies = executedActions.filter((a, i) => i > 0 && a.family === executedActions[i - 1].family).length;
  return {
    measuredSeconds: duration, sampleCount: samples.length, maxSampleGapSeconds: maxGap,
    statesSeconds: states, selectedPlans: plans, executedActions, executedCageActions: actions,
    executedFamilyCounts: families, contactIntervals: contacts,
    clawTelemetrySamples, clawFieldsAvailable: samples.every(s => 'clawAction' in s && 'clawAction' in s.motion),
    executedClawActions: clawActions, clawContactIntervals: clawContacts,
    consecutiveRepeatedPlans: repeatedPlans, consecutiveRepeatedActionFamilies: repeatedFamilies,
    distanceMetres: samples.at(-1).motion.distance - samples[0].motion.distance,
    steps: samples.at(-1).motion.steps - samples[0].motion.steps,
    warnings: [
      ...(executedActions.length === 0 ? ['No autonomous action was observed in the measured interval.'] : []),
      ...(Object.keys(families).length < 3 ? ['Fewer than three executed action-family labels were observed.'] : []),
      ...(repeatedFamilies ? ['Consecutive repeated executed action-family labels were observed.'] : []),
    ],
    limits: 'Sampled kinematic telemetry only. Renderer claw contact is based on distal-mesh proximity thresholds, not force or physical-contact proof. Labels do not prove distinct visible gestures, natural acting, physical support, collision freedom, or human acceptance. This summary does not verify a video or certify absence of unlogged input.',
  };
}
