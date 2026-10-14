import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const DEFAULT_RECEIPT = 'assets/audit/exterior-v1/geometry-correction-2026-09-27/browser-validation.json';
const UNMEASURED_STATUSES = new Set([
  'PROPOSED',
  'NOT RUN',
  'NOT MEASURED',
  'NOT SELECTED',
  'BLOCKED',
  'PENDING',
  'IN PROGRESS',
  'NO PERFORMANCE CLAIM',
]);
const UNVERIFIED_VALUES = new Set([
  '',
  'UNKNOWN',
  'NOT VERIFIED',
  'NOT VERIFIED ON THIS DEVICE',
  'NOT RECORDED',
  'NOT RUN',
]);

function present(value) {
  if (value === null || value === undefined || value === false) return false;
  if (typeof value === 'string') {
    const normalized = value.trim().toUpperCase();
    return !UNVERIFIED_VALUES.has(normalized);
  }
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

const MEASUREMENT_KEYS = new Set([
    'representativeFrameTimings',
    'frameTimeMs',
    'frameRate',
    'fps',
    'samples',
    'memory',
    'stutters',
    'essentialInputResponse',
]);

const BROWSER_TIMING_KEYS = new Set([
  'representativeFrameTimings',
  'frameTimeMs',
  'medianFrameMs',
  'frameRate',
  'fps',
  'meanFps',
  'durationSeconds',
  'observedDurationSeconds',
]);

function hasActualMeasurementData(record) {
  const isMeasurement = (value) => {
    if (typeof value === 'number') return Number.isFinite(value);
    if (Array.isArray(value)) return value.length > 0 && value.some(isMeasurement);
    if (value && typeof value === 'object') {
      return Object.values(value).some(isMeasurement);
    }
    return false;
  };

  const visit = (value) => {
    if (!value || typeof value !== 'object') return false;
    return Object.entries(value).some(([key, child]) => (
      (MEASUREMENT_KEYS.has(key) && isMeasurement(child)) || visit(child)
    ));
  };
  return visit(record);
}

function hasNumericTimingValue(value) {
  if (typeof value === 'number') return Number.isFinite(value);
  if (Array.isArray(value)) return value.some(hasNumericTimingValue);
  if (value && typeof value === 'object') {
    return Object.values(value).some(hasNumericTimingValue);
  }
  return false;
}

function hasBrowserTimingData(value) {
  if (!value || typeof value !== 'object') return false;
  return Object.entries(value).some(([key, child]) => (
    ((BROWSER_TIMING_KEYS.has(key) || /^(?:frameMs|fps)P\d+$/.test(key))
      && hasNumericTimingValue(child))
    || hasBrowserTimingData(child)
  ));
}

/**
 * Legacy browser-validation receipts put timing samples in root-level checks
 * and performance collections. Those samples must declare what they describe.
 */
export function validateBrowserTimingProvenance(receipt) {
  if (!receipt || typeof receipt !== 'object' || Array.isArray(receipt)) return [];
  const hasLegacyTiming = ['checks', 'performance']
    .some((key) => hasBrowserTimingData(receipt[key]));
  if (!hasLegacyTiming) return [];

  const errors = [];
  const provenance = receipt.timingEvidenceProvenance;
  if (!provenance || typeof provenance !== 'object' || Array.isArray(provenance)) {
    return ['timingEvidenceProvenance: browser timing samples require historical/current, device, candidate, and eligibility labels.'];
  }
  if (!['HISTORICAL', 'CURRENT'].includes(provenance.temporalClassification)) {
    errors.push('timingEvidenceProvenance: temporalClassification must be HISTORICAL or CURRENT.');
  }
  if (!present(provenance.device)) {
    errors.push('timingEvidenceProvenance: device must be identified or explicitly marked as not recorded.');
  }
  if (!present(provenance.candidate)) {
    errors.push('timingEvidenceProvenance: candidate must be identified or explicitly marked as not recorded.');
  }
  if (typeof provenance.hardwarePerformanceEligible !== 'boolean') {
    errors.push('timingEvidenceProvenance: hardwarePerformanceEligible must be an explicit boolean.');
  }
  if (provenance.temporalClassification === 'HISTORICAL'
    && provenance.hardwarePerformanceEligible !== false) {
    errors.push('timingEvidenceProvenance: historical timing data must be ineligible for current hardware-performance claims.');
  }
  if (provenance.temporalClassification === 'CURRENT'
    && provenance.hardwarePerformanceEligible === true
    && !/\bASUS\b/i.test(String(provenance.device ?? ''))) {
    errors.push('timingEvidenceProvenance: eligible current-device timings must identify the ASUS target.');
  }
  return errors;
}

function hasMeasurementEvidence(record) {
  const evidence = record.evidence ?? record.evidencePath;
  if (typeof evidence === 'string') return evidence.trim().length > 0;
  return Array.isArray(evidence)
    && evidence.length > 0
    && evidence.every((item) => typeof item === 'string' && item.trim().length > 0);
}

function parseEvidenceTimestamp(value) {
  if (typeof value !== 'string'
    || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value)) {
    return null;
  }
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp) ? timestamp : null;
}

function isPerformanceClaim(record) {
  const status = String(record.performanceStatus ?? record.status ?? '').trim().toUpperCase();
  return (status !== '' && !UNMEASURED_STATUSES.has(status)) || hasActualMeasurementData(record);
}

function getRenderer(record) {
  return record.webglRenderer
    ?? record.selectedWebGLRenderer
    ?? record.webglRendererActuallySelected
    ?? record.selectedWebglRenderer
    ?? null;
}

function validateWorkloadConditions(record, label) {
  const errors = [];
  if (typeof record.representativeWorkload !== 'string'
    || !present(record.representativeWorkload)) {
    errors.push(`${label}: representativeWorkload must describe the workload actually run.`);
  }

  if (typeof record.observedDurationSeconds !== 'number'
    || !Number.isFinite(record.observedDurationSeconds)
    || record.observedDurationSeconds <= 0) {
    errors.push(`${label}: observedDurationSeconds must be a positive measured duration.`);
  }

  const viewport = record.viewportCssPixels;
  if (!viewport || typeof viewport !== 'object' || Array.isArray(viewport)
    || !Number.isFinite(viewport.width) || viewport.width <= 0
    || !Number.isFinite(viewport.height) || viewport.height <= 0) {
    errors.push(`${label}: viewportCssPixels must record positive CSS-pixel width and height.`);
  }

  if (typeof record.devicePixelRatio !== 'number'
    || !Number.isFinite(record.devicePixelRatio)
    || record.devicePixelRatio <= 0) {
    errors.push(`${label}: devicePixelRatio must be a positive measured number.`);
  }
  return errors;
}

function isVerifiedPhysicalAccess(value) {
  if (value === true) return true;
  return ['VERIFIED', 'CONFIRMED'].includes(String(value ?? '').trim().toUpperCase());
}

function thresholdRevisionFor(snapshot) {
  const thresholds = Array.isArray(snapshot?.thresholds)
    ? snapshot.thresholds.map((threshold) => [
      threshold?.metric,
      threshold?.operator,
      threshold?.limit,
    ])
    : [];
  const canonicalSnapshot = JSON.stringify([
    snapshot?.approvedAt,
    snapshot?.approvalEvidence,
    thresholds,
  ]);
  return `sha256-${createHash('sha256').update(canonicalSnapshot).digest('hex')}`;
}

function validateThresholdSnapshots(policy) {
  const errors = [];
  const snapshots = policy?.approvedThresholdRevisions;
  if (!Array.isArray(snapshots)) {
    return ['performancePolicy: approvedThresholdRevisions must be an array of immutable approved threshold snapshots.'];
  }

  const seenRevisions = new Set();
  for (const snapshot of snapshots) {
    if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)) {
      errors.push('performancePolicy: each approved threshold revision must be an object.');
      continue;
    }
    const revision = snapshot.revision;
    if (typeof revision !== 'string' || !/^sha256-[a-f0-9]{64}$/.test(revision)
      || seenRevisions.has(revision)) {
      errors.push('performancePolicy: each approved threshold revision must have a unique sha256 revision identifier.');
    }
    if (typeof revision === 'string') seenRevisions.add(revision);
    if (parseEvidenceTimestamp(snapshot.approvedAt) === null) {
      errors.push('performancePolicy: each approved threshold revision requires an ISO approval timestamp.');
    }
    if (!present(snapshot.approvalEvidence)) {
      errors.push('performancePolicy: each approved threshold revision requires an approval evidence reference.');
    }
    if (!Array.isArray(snapshot.thresholds) || snapshot.thresholds.length === 0) {
      errors.push('performancePolicy: each approved threshold revision requires a non-empty thresholds list.');
      continue;
    }
    const operators = new Set(['<=', '<', '>=', '>']);
    const seenMetrics = new Set();
    for (const threshold of snapshot.thresholds) {
      const metric = threshold?.metric;
      const path = typeof metric === 'string' ? metric.split('.') : [];
      if (!path.length || !MEASUREMENT_KEYS.has(path[0])
        || path.some((part) => !part || ['__proto__', 'prototype', 'constructor'].includes(part))
        || seenMetrics.has(metric) || !operators.has(threshold?.operator)
        || typeof threshold?.limit !== 'number' || !Number.isFinite(threshold.limit)) {
        errors.push('performancePolicy: each approved threshold revision must contain unique observed metrics, supported operators, and finite numeric limits.');
        continue;
      }
      seenMetrics.add(metric);
    }
    if (revision !== thresholdRevisionFor(snapshot)) {
      errors.push('performancePolicy: approved threshold revision does not match its recorded approval timestamp, evidence, and threshold values.');
    }
  }
  return errors;
}

function validateVerdictComparison(record, policy, label, status) {
  const errors = [];
  if (!hasMeasurementEvidence({ evidence: record.comparisonEvidence })) {
    errors.push(`${label}: PASS/FAIL requires a comparisonEvidence reference.`);
  }
  const revision = record.thresholdRevision;
  const snapshots = policy?.approvedThresholdRevisions;
  const matchingSnapshots = Array.isArray(snapshots)
    ? snapshots.filter((snapshot) => snapshot?.revision === revision)
    : [];
  if (typeof revision !== 'string' || matchingSnapshots.length !== 1) {
    errors.push(`${label}: PASS/FAIL requires a thresholdRevision matching exactly one recorded approved threshold snapshot.`);
    return errors;
  }
  const snapshot = matchingSnapshots[0];
  if (revision !== thresholdRevisionFor(snapshot)) {
    errors.push(`${label}: threshold evidence does not match the recorded thresholdRevision.`);
    return errors;
  }
  const thresholds = snapshot.thresholds;
  if (!Array.isArray(thresholds) || thresholds.length === 0) {
    errors.push(`${label}: PASS/FAIL requires a non-empty approved threshold snapshot.`);
    return errors;
  }
  const operators = {
    '<=': (value, limit) => value <= limit,
    '<': (value, limit) => value < limit,
    '>=': (value, limit) => value >= limit,
    '>': (value, limit) => value > limit,
  };
  const seen = new Set();
  const outcomes = [];
  for (const threshold of thresholds) {
    const metric = threshold?.metric;
    const path = typeof metric === 'string' ? metric.split('.') : [];
    if (!path.length || !MEASUREMENT_KEYS.has(path[0])
      || path.some((part) => !part || ['__proto__', 'prototype', 'constructor'].includes(part))
      || seen.has(metric) || !Object.hasOwn(operators, threshold?.operator)
      || typeof threshold?.limit !== 'number' || !Number.isFinite(threshold.limit)) {
      errors.push(`${label}: each approved threshold must uniquely identify an observed metric, supported operator, and finite numeric limit.`);
      continue;
    }
    seen.add(metric);
    let observed = record;
    for (const part of path) {
      observed = observed && typeof observed === 'object' && Object.hasOwn(observed, part)
        ? observed[part] : undefined;
    }
    if (typeof observed !== 'number' || !Number.isFinite(observed)) {
      errors.push(`${label}: approved metric ${metric} requires an actual finite numeric observation.`);
      continue;
    }
    outcomes.push(operators[threshold.operator](observed, threshold.limit));
  }
  if (outcomes.length === thresholds.length) {
    const calculatedStatus = outcomes.every(Boolean) ? 'PASS' : 'FAIL';
    if (status !== calculatedStatus) {
      errors.push(`${label}: ${status} contradicts the approved threshold comparison (${calculatedStatus}).`);
    }
  }
  return errors;
}

/**
 * Checks that ASUS performance claims are backed by verified, on-device evidence,
 * while keeping cloud/software and historical evidence explicitly ineligible.
 */
export function validateDevicePerformanceReceipt(receipt) {
  const errors = [];
  if (!receipt || typeof receipt !== 'object' || Array.isArray(receipt)) {
    return ['Receipt must be a JSON object.'];
  }
  errors.push(...validateBrowserTimingProvenance(receipt));

  const policy = receipt.performancePolicy;
  if (!policy || typeof policy !== 'object') {
    errors.push('performancePolicy: proposed thresholds and their source must be explicitly recorded.');
  } else {
    errors.push(...validateThresholdSnapshots(policy));
    const classification = String(policy.thresholdClassification ?? '').trim().toUpperCase();
    const approved = classification === 'APPROVED';
    const statusText = String(policy.thresholdsStatus ?? '').toUpperCase();
    const statusSaysProposed = /\bPROPOSED\b/.test(statusText);
    const statusSaysApproved = /\bAPPROVED\b/.test(statusText)
      && !/\bNOT\s+APPROVED\b/.test(statusText);
    if (!['PROPOSED', 'APPROVED'].includes(classification)) {
      errors.push('performancePolicy: thresholdClassification must be PROPOSED or APPROVED; thresholds are not measurements.');
    }
    if ((classification === 'PROPOSED' && (!statusSaysProposed || statusSaysApproved))
      || (approved && (!statusSaysApproved || statusSaysProposed))) {
      errors.push('performancePolicy: thresholdClassification and thresholdsStatus must describe the same proposed or approved state.');
    }
    if (!present(policy.source)) {
      errors.push('performancePolicy: the source of the thresholds is missing.');
    }
    if (approved && !present(policy.approvalEvidence)) {
      errors.push('performancePolicy: approved thresholds require an approval evidence reference.');
    }
    if (approved && parseEvidenceTimestamp(policy.approvedAt) === null) {
      errors.push('performancePolicy: approved thresholds require an ISO timestamp for approval.');
    }
    if (approved && (!Array.isArray(policy.approvedThresholdRevisions)
      || policy.approvedThresholdRevisions.length === 0)) {
      errors.push('performancePolicy: approved thresholds require at least one immutable approved threshold revision.');
    }
  }

  const approvals = receipt.baselineAndAcceptance;
  if (!approvals || typeof approvals !== 'object'
    || !present(approvals.v37DeploymentAuthorization)
    || !present(approvals.v37OwnerLikenessAcceptance)) {
    errors.push('baselineAndAcceptance: V37 deployment authorization and owner likeness acceptance must have separate recorded statuses.');
  } else if (
    String(approvals.v37DeploymentAuthorization).trim().toUpperCase()
      === String(approvals.v37OwnerLikenessAcceptance).trim().toUpperCase()
    || /LIKEness/i.test(String(approvals.v37DeploymentAuthorization))
    || /DEPLOYMENT/i.test(String(approvals.v37OwnerLikenessAcceptance))
  ) {
    errors.push('baselineAndAcceptance: deployment authorization cannot stand in for owner likeness acceptance, or vice versa.');
  }

  for (const sectionName of ['targetDevicePerformance', 'v37SustainedPerformanceAttempt']) {
    const record = receipt[sectionName];
    if (!record || typeof record !== 'object' || !isPerformanceClaim(record)) continue;

    const label = sectionName;
    const status = String(record.performanceStatus ?? record.status ?? '').trim().toUpperCase();
    const hasMeasurement = hasActualMeasurementData(record);
    if (['MEASURED', 'PASS', 'FAIL'].includes(status) || hasMeasurement) {
      errors.push(...validateWorkloadConditions(record, label));
    }
    if (status === 'MEASURED' || status === 'PASS' || status === 'FAIL') {
      if (!hasMeasurement) {
        errors.push(`${label}: ${status} requires actual numeric measurement evidence.`);
      }
      if (!hasMeasurementEvidence(record)) {
        errors.push(`${label}: ${status} requires a non-empty evidence path or evidence list.`);
      }
    }
    if (status === 'PASS' || status === 'FAIL') {
      errors.push(...validateVerdictComparison(record, policy, label, status));
      const revision = record.thresholdRevision;
      const snapshots = policy?.approvedThresholdRevisions;
      const matchingSnapshot = Array.isArray(snapshots)
        ? snapshots.find((snapshot) => snapshot?.revision === revision)
        : null;
      if (!matchingSnapshot || !present(matchingSnapshot.approvalEvidence)) {
        errors.push(`${label}: PASS/FAIL requires a recorded approved threshold snapshot; proposed targets alone cannot produce a performance verdict.`);
      }
      const snapshotApprovedAt = parseEvidenceTimestamp(matchingSnapshot?.approvedAt);
      const measuredAt = parseEvidenceTimestamp(record.measuredAt);
      if (measuredAt === null) {
        errors.push(`${label}: PASS/FAIL requires an ISO measurement timestamp.`);
      } else if (snapshotApprovedAt === null || snapshotApprovedAt > measuredAt) {
        errors.push(`${label}: threshold approval must be recorded before the measured run.`);
      }
    }

    const device = String(record.device ?? record.deviceUsed ?? '').trim();
    if (!/\bASUS\b/i.test(device)) {
      errors.push(`${label}: a performance result must identify the ASUS device used.`);
    }
    if (!isVerifiedPhysicalAccess(record.physicalAccess)) {
      errors.push(`${label}: physical access must be VERIFIED or CONFIRMED.`);
    }
    if (!present(record.browser)) {
      errors.push(`${label}: browser is missing or unverified.`);
    }
    if (!present(record.browserVersion)) {
      errors.push(`${label}: exact browserVersion is missing or unverified.`);
    }
    const renderer = getRenderer(record);
    if (!present(renderer)) {
      errors.push(`${label}: the WebGL renderer actually selected on the device is missing or unverified.`);
    } else if (/swiftshader|llvmpipe|software rasterizer/i.test(String(renderer))) {
      errors.push(`${label}: a software renderer cannot substantiate ASUS hardware performance.`);
    }
  }

  const cloudProbe = receipt.separateCloudSoftwareRendererProbe;
  if (cloudProbe && typeof cloudProbe === 'object') {
    if (cloudProbe.evidenceClass !== 'NON-ASUS CLOUD/SOFTWARE PROBE'
      || cloudProbe.hardwarePerformanceEligible !== false) {
      errors.push('separateCloudSoftwareRendererProbe: must be explicitly classified as non-ASUS and ineligible for hardware performance.');
    }
    const cloudLabel = `${cloudProbe.status ?? ''} ${cloudProbe.notes ?? ''}`;
    if (!/NOT AN ASUS|NON-ASUS|NOT ASUS/i.test(cloudLabel)) {
      errors.push('separateCloudSoftwareRendererProbe: status or notes must explicitly say this is not an ASUS result.');
    }
    const cloudRenderer = String(cloudProbe.webglRendererActuallySelected ?? '');
    const gpuClass = String(cloudProbe.gpuClass ?? '');
    if (/swiftshader/i.test(`${cloudRenderer} ${gpuClass}`)
      && !/swiftshader|software/i.test(gpuClass)) {
      errors.push('separateCloudSoftwareRendererProbe: SwiftShader must be labeled as a software renderer.');
    }
  }

  const historical = receipt.historicalTelemetryNotUsedAsAcceptanceEvidence;
  if (historical && typeof historical === 'object') {
    if (historical.evidenceClass !== 'HISTORICAL NON-TARGET TELEMETRY'
      || historical.hardwarePerformanceEligible !== false) {
      errors.push('historicalTelemetryNotUsedAsAcceptanceEvidence: must be explicitly classified as historical, non-target, and ineligible for hardware performance.');
    }
    const historicalContext = `${historical.reason ?? ''} ${historical.evidenceClass ?? ''}`;
    if (!/historical/i.test(historicalContext) || !/non.target|not (?:the )?target|not used/i.test(historicalContext)) {
      errors.push('historicalTelemetryNotUsedAsAcceptanceEvidence: must state that it is historical and not target-device evidence.');
    }
    if (historical.temporalClassification !== 'HISTORICAL') {
      errors.push('historicalTelemetryNotUsedAsAcceptanceEvidence: temporalClassification must be HISTORICAL.');
    }
    if (!present(historical.device) || !present(historical.candidate)) {
      errors.push('historicalTelemetryNotUsedAsAcceptanceEvidence: device and candidate provenance must be identified or explicitly marked as not recorded.');
    }
  }

  return errors;
}

async function runCli() {
  const receiptPath = resolve(process.argv[2] ?? DEFAULT_RECEIPT);
  let receipt;
  try {
    receipt = JSON.parse(await readFile(receiptPath, 'utf8'));
  } catch (error) {
    console.error(`FAIL ${receiptPath}: ${error.message}`);
    process.exitCode = 1;
    return;
  }

  const errors = validateDevicePerformanceReceipt(receipt);
  if (errors.length) {
    console.error(`FAIL ${receiptPath}`);
    for (const error of errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log(`PASS ${receiptPath}: proposed targets, measured evidence, approvals, cloud/software, and historical evidence are properly separated.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await runCli();
}
