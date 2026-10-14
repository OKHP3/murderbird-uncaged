import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile, readdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  validateBrowserTimingProvenance,
  validateDevicePerformanceReceipt,
} from '../scripts/validate-device-performance-receipt.mjs';

const receiptPath = new URL(
  '../assets/audit/exterior-v1/geometry-correction-2026-09-27/browser-validation.json',
  import.meta.url,
);
const receipt = JSON.parse(await readFile(receiptPath, 'utf8'));
const historicalReceipt = JSON.parse(await readFile(new URL(
  '../assets/audit/exterior-v1/browser-validation.json',
  import.meta.url,
), 'utf8'));
const evaluationPrd = await readFile(new URL('../docs/murderbird-evaluation-prd.md', import.meta.url), 'utf8');
const v37ReleaseNotes = await readFile(new URL('../docs/production-v37.md', import.meta.url), 'utf8');

async function findBrowserValidationReceipts(directory) {
  const matches = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) {
      matches.push(...await findBrowserValidationReceipts(path));
    } else if (entry.name === 'browser-validation.json') {
      matches.push(path);
    }
  }
  return matches;
}

function withMeasuredAsusResult(overrides = {}) {
  return structuredClone({
    ...receipt,
    targetDevicePerformance: {
      status: 'MEASURED',
      device: 'ASUS Vivobook Pro 15 N6506MJ_Q533MJ',
      physicalAccess: 'VERIFIED',
      browser: 'Chrome',
      browserVersion: '152.0.7977.64',
      webglRenderer: 'ANGLE (Intel, Intel Arc)',
      representativeFrameTimings: { medianFrameMs: 16.7 },
      representativeWorkload: 'Run the representative exterior review interaction continuously.',
      observedDurationSeconds: 120,
      viewportCssPixels: { width: 1440, height: 900 },
      devicePixelRatio: 1.25,
      evidence: ['assets/audit/performance/asus-run.json'],
      ...overrides,
    },
  });
}

test('current receipt keeps unverified ASUS, cloud SwiftShader, and historical telemetry distinct', () => {
  assert.deepEqual(validateDevicePerformanceReceipt(receipt), []);
});

test('every archived browser timing report declares its historical status, device, candidate, and eligibility', async () => {
  const auditDirectory = fileURLToPath(new URL('../assets/audit/', import.meta.url));
  const paths = await findBrowserValidationReceipts(auditDirectory);
  let timingReceiptCount = 0;

  for (const path of paths) {
    const candidate = JSON.parse(await readFile(path, 'utf8'));
    const errors = validateBrowserTimingProvenance(candidate);
    assert.deepEqual(errors, [], `${path}: ${errors.join('; ')}`);

    if (candidate.timingEvidenceProvenance) {
      timingReceiptCount += 1;
      assert.equal(candidate.timingEvidenceProvenance.temporalClassification, 'HISTORICAL', path);
      assert.equal(candidate.timingEvidenceProvenance.hardwarePerformanceEligible, false, path);
      assert.ok(candidate.timingEvidenceProvenance.device, `${path}: device provenance missing`);
      assert.ok(candidate.timingEvidenceProvenance.candidate, `${path}: candidate provenance missing`);
    }
  }
  assert.equal(timingReceiptCount, 9, 'the audit should cover all nine archived receipts with numeric timing samples');
});

test('legacy timing samples fail validation when provenance is missing or misleading', () => {
  const candidate = structuredClone(historicalReceipt);
  delete candidate.timingEvidenceProvenance;
  assert.match(
    validateBrowserTimingProvenance(candidate).join('\n'),
    /timing samples require historical\/current, device, candidate, and eligibility labels/,
  );

  candidate.timingEvidenceProvenance = {
    temporalClassification: 'HISTORICAL',
    device: 'NOT RECORDED IN ORIGINAL RECEIPT',
    candidate: 'Exterior v1',
    hardwarePerformanceEligible: true,
  };
  assert.match(
    validateBrowserTimingProvenance(candidate).join('\n'),
    /historical timing data must be ineligible/,
  );
});

test('an ASUS performance claim fails until physical access is verified', () => {
  const candidate = withMeasuredAsusResult({ physicalAccess: 'NOT VERIFIED' });
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /physical access must be VERIFIED or CONFIRMED/,
  );
});

test('an ASUS performance claim requires browser, exact version, and selected renderer evidence', () => {
  for (const [field, expectedMessage] of [
    ['browser', /browser is missing or unverified/],
    ['browserVersion', /exact browserVersion is missing or unverified/],
    ['webglRenderer', /WebGL renderer actually selected on the device is missing or unverified/],
  ]) {
    const candidate = withMeasuredAsusResult({ [field]: null });
    assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), expectedMessage);
  }
});

test('a complete ASUS hardware performance claim passes', () => {
  assert.deepEqual(validateDevicePerformanceReceipt(withMeasuredAsusResult()), []);
});

test('measured ASUS results require a described workload, duration, viewport, and pixel ratio', () => {
  for (const [field, value, expectedMessage] of [
    ['representativeWorkload', null, /representativeWorkload must describe the workload actually run/],
    ['observedDurationSeconds', null, /observedDurationSeconds must be a positive measured duration/],
    ['viewportCssPixels', null, /viewportCssPixels must record positive CSS-pixel width and height/],
    ['devicePixelRatio', null, /devicePixelRatio must be a positive measured number/],
  ]) {
    const candidate = withMeasuredAsusResult({ [field]: value });
    assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), expectedMessage, field);
  }

  for (const [field, value, expectedMessage] of [
    ['observedDurationSeconds', 0, /observedDurationSeconds must be a positive measured duration/],
    ['viewportCssPixels', { width: 1440, height: 0 }, /viewportCssPixels must record positive CSS-pixel width and height/],
    ['devicePixelRatio', Number.NaN, /devicePixelRatio must be a positive measured number/],
  ]) {
    const candidate = withMeasuredAsusResult({ [field]: value });
    assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), expectedMessage, field);
  }
});

test('NOT RUN ASUS receipts do not need workload details', () => {
  const candidate = structuredClone(receipt);
  candidate.targetDevicePerformance.status = 'NOT RUN';
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);
});

test('MEASURED requires actual numeric metrics and a separate evidence reference', () => {
  const missingMetrics = withMeasuredAsusResult({
    status: 'MEASURED',
    representativeFrameTimings: null,
    observedDurationSeconds: null,
  });
  assert.match(
    validateDevicePerformanceReceipt(missingMetrics).join('\n'),
    /MEASURED requires actual numeric measurement evidence/,
  );

  const missingEvidence = withMeasuredAsusResult({
    status: 'MEASURED',
    evidence: null,
  });
  assert.match(
    validateDevicePerformanceReceipt(missingEvidence).join('\n'),
    /MEASURED requires a non-empty evidence path or evidence list/,
  );
});

test('proposed targets alone cannot produce a PASS or FAIL verdict', () => {
  for (const status of ['PASS', 'FAIL']) {
    const candidate = withMeasuredAsusResult({ status });
    assert.match(
      validateDevicePerformanceReceipt(candidate).join('\n'),
      /PASS\/FAIL requires a recorded approved threshold snapshot; proposed targets alone cannot produce a performance verdict/,
    );
  }
});

test('PASS/FAIL is accepted only with measured evidence and documented threshold approval', () => {
  const candidate = withMeasuredAsusResult({
    status: 'PASS',
    measuredAt: '2026-10-13T10:05:00Z',
    comparisonEvidence: 'assets/audit/performance/example-comparison.json',
  });
  candidate.performancePolicy.thresholdClassification = 'APPROVED';
  candidate.performancePolicy.thresholdsStatus = 'APPROVED';
  candidate.performancePolicy.approvalEvidence = 'docs/performance-target-approval.md';
  candidate.performancePolicy.approvedAt = '2026-10-13T10:00:00Z';
  const snapshot = createThresholdSnapshot(
    candidate.performancePolicy.approvedAt,
    candidate.performancePolicy.approvalEvidence,
    [{ metric: 'representativeFrameTimings.medianFrameMs', operator: '<=', limit: 16.7 }],
  );
  candidate.performancePolicy.approvedThresholdRevisions = [snapshot];
  candidate.targetDevicePerformance.thresholdRevision = snapshot.revision;
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);

  const lateSnapshot = createThresholdSnapshot(
    '2026-10-13T10:10:00Z',
    candidate.performancePolicy.approvalEvidence,
    candidate.performancePolicy.approvedThresholdRevisions[0].thresholds,
  );
  candidate.performancePolicy.approvedThresholdRevisions = [lateSnapshot];
  candidate.targetDevicePerformance.thresholdRevision = lateSnapshot.revision;
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /threshold approval must be recorded before the measured run/,
  );
});

test('V37 deployment authorization and owner likeness acceptance remain independent', () => {
  const candidate = structuredClone(receipt);
  candidate.baselineAndAcceptance.v37OwnerLikenessAcceptance =
    candidate.baselineAndAcceptance.v37DeploymentAuthorization;
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /deployment authorization cannot stand in for owner likeness acceptance/,
  );
  assert.match(v37ReleaseNotes, /deployment authorization is not owner likeness acceptance/i);
});

test('the PRD identifies targets as proposals and defines evidence requirements for results', () => {
  assert.ok(evaluationPrd.includes('**Status: PROPOSED REVIEW TARGETS, NOT APPROVED ACCEPTANCE LIMITS OR MEASURED RESULTS.**'));
  assert.ok(evaluationPrd.includes('A **MEASURED** status requires actual observed values plus a traceable evidence reference'));
  assert.ok(evaluationPrd.includes('A **PASS** or **FAIL** status additionally requires thresholds explicitly approved before the run'));
  assert.ok(evaluationPrd.includes('Preserve old snapshots when proposing or approving revised targets'));
});

test('SwiftShader cannot satisfy ASUS hardware renderer evidence', () => {
  const candidate = withMeasuredAsusResult({
    webglRenderer: 'ANGLE (Google, Vulkan, SwiftShader Device)',
  });
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /a software renderer cannot substantiate ASUS hardware performance/,
  );
});

test('cloud SwiftShader timing evidence stays non-ASUS and hardware-ineligible', () => {
  const candidate = structuredClone(receipt);
  candidate.separateCloudSoftwareRendererProbe.representativeFrameTimings = { medianFrameMs: 42 };
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);

  candidate.separateCloudSoftwareRendererProbe.hardwarePerformanceEligible = true;
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /must be explicitly classified as non-ASUS and ineligible/,
  );
});

test('historical telemetry passes only when labeled historical and non-target', () => {
  const candidate = structuredClone(receipt);
  candidate.historicalTelemetryNotUsedAsAcceptanceEvidence.evidenceClass = 'HISTORICAL NON-TARGET TELEMETRY';
  candidate.historicalTelemetryNotUsedAsAcceptanceEvidence.hardwarePerformanceEligible = false;
  candidate.historicalTelemetryNotUsedAsAcceptanceEvidence.representativeFrameTimings = {
    medianFrameMs: 18.4,
  };
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);

  candidate.historicalTelemetryNotUsedAsAcceptanceEvidence.evidenceClass = 'ASUS HARDWARE RESULT';
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /must be explicitly classified as historical, non-target/,
  );

  const missingCandidate = structuredClone(receipt);
  delete missingCandidate.historicalTelemetryNotUsedAsAcceptanceEvidence.candidate;
  assert.match(
    validateDevicePerformanceReceipt(missingCandidate).join('\n'),
    /device and candidate provenance must be identified/,
  );
});

// Duration records test conditions; it cannot replace an observed metric.
test('workload duration alone cannot substantiate MEASURED', () => {
  const candidate = withMeasuredAsusResult({ representativeFrameTimings: null });
  assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), /MEASURED requires actual numeric measurement evidence/);
});

function withApprovedVerdict(status = 'PASS', timings = { medianFrameMs: 16.7 }) {
  const candidate = withMeasuredAsusResult({
    status, representativeFrameTimings: timings,
    measuredAt: '2026-10-13T10:05:00Z',
    comparisonEvidence: 'example-comparison.json',
  });
  Object.assign(candidate.performancePolicy, {
    thresholdClassification: 'APPROVED', thresholdsStatus: 'APPROVED',
    approvalEvidence: 'example-approval.md', approvedAt: '2026-10-13T10:00:00Z',
  });
  const snapshot = createThresholdSnapshot(
    candidate.performancePolicy.approvedAt,
    candidate.performancePolicy.approvalEvidence,
    [{ metric: 'representativeFrameTimings.medianFrameMs', operator: '<=', limit: 16.7 }],
  );
  candidate.performancePolicy.approvedThresholdRevisions = [snapshot];
  candidate.targetDevicePerformance.thresholdRevision = snapshot.revision;
  return candidate;
}

function createThresholdSnapshot(approvedAt, approvalEvidence, thresholds) {
  const snapshot = { approvedAt, approvalEvidence, thresholds };
  const canonicalSnapshot = JSON.stringify([
    approvedAt,
    approvalEvidence,
    thresholds.map((threshold) => [
      threshold?.metric,
      threshold?.operator,
      threshold?.limit,
    ]),
  ]);
  snapshot.revision = `sha256-${createHash('sha256').update(canonicalSnapshot).digest('hex')}`;
  return snapshot;
}

test('an approval label alone cannot substantiate PASS or FAIL', () => {
  for (const status of ['PASS', 'FAIL']) {
    const candidate = withApprovedVerdict(status, { medianFrameMs: 9999 });
    candidate.performancePolicy.approvedThresholdRevisions = [];
    delete candidate.targetDevicePerformance.comparisonEvidence;
    const errors = validateDevicePerformanceReceipt(candidate).join('\n');
    assert.match(errors, /thresholdRevision matching exactly one recorded approved threshold snapshot/);
    assert.match(errors, /requires a comparisonEvidence reference/);
  }
});

test('verdict must agree with actual observations against all approved limits', () => {
  assert.deepEqual(validateDevicePerformanceReceipt(withApprovedVerdict()), []);
  assert.deepEqual(validateDevicePerformanceReceipt(withApprovedVerdict('FAIL', { medianFrameMs: 9999 })), []);
  assert.match(validateDevicePerformanceReceipt(withApprovedVerdict('PASS', { medianFrameMs: 9999 })).join('\n'), /PASS contradicts/);
  assert.match(validateDevicePerformanceReceipt(withApprovedVerdict('FAIL')).join('\n'), /FAIL contradicts/);
  const candidate = withApprovedVerdict('PASS', { medianFrameMs: 16, p95FrameMs: 50 });
  const snapshot = candidate.performancePolicy.approvedThresholdRevisions[0];
  const revisedSnapshot = createThresholdSnapshot(
    snapshot.approvedAt,
    snapshot.approvalEvidence,
    [
      ...snapshot.thresholds,
      { metric: 'representativeFrameTimings.p95FrameMs', operator: '<=', limit: 33.3 },
    ],
  );
  candidate.performancePolicy.approvedThresholdRevisions = [revisedSnapshot];
  candidate.targetDevicePerformance.thresholdRevision = revisedSnapshot.revision;
  assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), /PASS contradicts/);
  candidate.targetDevicePerformance.status = 'FAIL';
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);
});

test('approved limits must identify unique actual metrics and valid numeric comparisons', () => {
  for (const threshold of [
    { metric: 'observedDurationSeconds', operator: '<=', limit: 120 },
    { metric: 'representativeFrameTimings.medianFrameMs', operator: 'about', limit: 16.7 },
    { metric: 'representativeFrameTimings.medianFrameMs', operator: '<=', limit: '16.7' },
    { metric: 'representativeFrameTimings.medianFrameMs', operator: '<=', limit: Infinity },
    { metric: 'representativeFrameTimings.__proto__.value', operator: '<=', limit: 16.7 },
    null,
  ]) {
    const candidate = withApprovedVerdict();
    const revision = createThresholdSnapshot(
      candidate.performancePolicy.approvedAt,
      candidate.performancePolicy.approvalEvidence,
      [threshold],
    );
    candidate.performancePolicy.approvedThresholdRevisions = [revision];
    candidate.targetDevicePerformance.thresholdRevision = revision.revision;
    assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), /each approved threshold/);
  }
  const candidate = withApprovedVerdict();
  const snapshot = candidate.performancePolicy.approvedThresholdRevisions[0];
  const duplicateMetrics = createThresholdSnapshot(
    snapshot.approvedAt,
    snapshot.approvalEvidence,
    [...snapshot.thresholds, snapshot.thresholds[0]],
  );
  candidate.performancePolicy.approvedThresholdRevisions = [duplicateMetrics];
  candidate.targetDevicePerformance.thresholdRevision = duplicateMetrics.revision;
  assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), /each approved threshold/);
  const missingMetric = createThresholdSnapshot(
    snapshot.approvedAt,
    snapshot.approvalEvidence,
    [{ metric: 'representativeFrameTimings.missingMetric', operator: '<=', limit: 16.7 }],
  );
  candidate.performancePolicy.approvedThresholdRevisions = [missingMetric];
  candidate.targetDevicePerformance.thresholdRevision = missingMetric.revision;
  assert.match(validateDevicePerformanceReceipt(candidate).join('\n'), /requires an actual finite numeric observation/);
});

test('verdict criteria come from the referenced snapshot, not later proposal edits', () => {
  const candidate = withApprovedVerdict();
  candidate.performancePolicy.source = 'docs/murderbird-evaluation-prd.md#revised-proposed-performance-targets';
  candidate.performancePolicy.proposedTargets = { medianFrameMs: 9999 };
  candidate.performancePolicy.thresholdClassification = 'PROPOSED';
  candidate.performancePolicy.thresholdsStatus = 'PROPOSED; targets have since been revised';
  candidate.performancePolicy.approvalEvidence = null;
  candidate.performancePolicy.approvedAt = null;
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);

  candidate.performancePolicy.approvedThresholdRevisions[0].thresholds[0].limit = 9999;
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /approved threshold revision does not match its recorded approval timestamp, evidence, and threshold values/,
  );
});

test('V37 verdicts use their own recorded threshold revision', () => {
  const candidate = withApprovedVerdict();
  candidate.v37SustainedPerformanceAttempt = structuredClone(candidate.targetDevicePerformance);
  candidate.targetDevicePerformance.status = 'NOT RUN';
  candidate.targetDevicePerformance.performanceStatus = undefined;
  assert.deepEqual(validateDevicePerformanceReceipt(candidate), []);

  candidate.v37SustainedPerformanceAttempt.thresholdRevision = 'sha256-' + '0'.repeat(64);
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /v37SustainedPerformanceAttempt: PASS\/FAIL requires a thresholdRevision matching exactly one recorded approved threshold snapshot/,
  );
});

test('a verdict cannot refer to a different or missing threshold revision', () => {
  const candidate = withApprovedVerdict();
  candidate.targetDevicePerformance.thresholdRevision = 'sha256-' + '0'.repeat(64);
  assert.match(
    validateDevicePerformanceReceipt(candidate).join('\n'),
    /thresholdRevision matching exactly one recorded approved threshold snapshot/,
  );
});
