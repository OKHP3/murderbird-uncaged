import { readFile, readdir } from 'node:fs/promises';
import { readFileSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { createHash } from 'node:crypto';
import { isAbsolute, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const DEFAULT_RECEIPT = 'assets/audit/exterior-v1/geometry-correction-2026-09-27/browser-validation.json';
const DEFAULT_TIMING_BASELINE = 'tests/fixtures/archived-browser-timing-baseline.json';
const DEFAULT_CAPTURE_CONDITIONS_BASELINE = 'tests/fixtures/archived-browser-capture-conditions-baseline.json';
const DEFAULT_AUDIT_DIRECTORY = 'assets/audit';
const PROJECT_ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const PROJECT_EVIDENCE_ROOT = resolve(homedir(), 'OKH-Local/01_ChatGPT_Exports/murderbird-uncaged/evidence');
const ASUS_RUN_EVIDENCE_SCHEMA = 'asus-browser-run/v1';
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

function isArchivedBrowserTimingKey(key) {
  return BROWSER_TIMING_KEYS.has(key) || /^(?:frameMs|fps)P\d+$/.test(key);
}

function archivedBrowserTimingMeasurements(receipt) {
  const measurements = [];
  const visit = (value, path = []) => {
    if (!value || typeof value !== 'object') return;
    for (const [key, child] of Object.entries(value)) {
      const childPath = [...path, key];
      if (isArchivedBrowserTimingKey(key)) {
        const projected = numericTimingProjection(child);
        if (projected !== undefined) measurements.push({ path: childPath, value: projected });
      }
      visit(child, childPath);
    }
  };
  visit(receipt);
  measurements.sort((left, right) => JSON.stringify(left.path).localeCompare(JSON.stringify(right.path)));
  return measurements;
}

function digestTimingMeasurements(measurements) {
  const canonical = measurements.map(({ path, value }) => [path, value]);
  return `sha256-${createHash('sha256').update(JSON.stringify(canonical)).digest('hex')}`;
}

function timingSnapshot(receipt) {
  const measurements = archivedBrowserTimingMeasurements(receipt);
  return { digest: digestTimingMeasurements(measurements), measurements };
}

function isValidTimingSnapshot(snapshot) {
  if (!snapshot || typeof snapshot !== 'object' || Array.isArray(snapshot)
    || typeof snapshot.digest !== 'string'
    || !/^sha256-[a-f0-9]{64}$/.test(snapshot.digest)
    || !Array.isArray(snapshot.measurements)) {
    return false;
  }
  const measurements = snapshot.measurements;
  if (measurements.some((measurement) => (
    !measurement || typeof measurement !== 'object' || Array.isArray(measurement)
    || !Array.isArray(measurement.path)
    || measurement.path.length === 0
    || measurement.path.some((part) => typeof part !== 'string')
    || numericTimingProjection(measurement.value) === undefined
    || JSON.stringify(numericTimingProjection(measurement.value)) !== JSON.stringify(measurement.value)
  ))) return false;
  const sorted = [...measurements].sort((left, right) => (
    JSON.stringify(left.path).localeCompare(JSON.stringify(right.path))
  ));
  return JSON.stringify(measurements) === JSON.stringify(sorted)
    && digestTimingMeasurements(measurements) === snapshot.digest;
}

const MIN_REBASELINE_REASON_LENGTH = 12;
const MAX_REBASELINE_REASON_LENGTH = 240;

function validateRebaselineReason(reason) {
  return typeof reason === 'string'
    && !/[\r\n]/.test(reason)
    && reason.trim().length >= MIN_REBASELINE_REASON_LENGTH
    && reason.trim().length <= MAX_REBASELINE_REASON_LENGTH;
}

export function createArchivedBrowserTimingRebaseline(beforeReceipt, afterReceipt, reason) {
  if (!validateRebaselineReason(reason)) {
    throw new TypeError(
      `Rebaseline reason must be ${MIN_REBASELINE_REASON_LENGTH}-${MAX_REBASELINE_REASON_LENGTH} characters.`,
    );
  }
  const before = timingSnapshot(beforeReceipt);
  const after = timingSnapshot(afterReceipt);
  if (before.digest === after.digest) {
    throw new TypeError('A timing rebaseline must change at least one numeric timing value.');
  }
  return { reason: reason.trim(), before, after };
}

function formatTimingMeasurements(measurements) {
  if (!Array.isArray(measurements) || measurements.length === 0) return '(no numeric timing values)';
  return measurements.map(({ path, value }) => `${path.join('.')} = ${JSON.stringify(value)}`).join('; ');
}

function numericTimingProjection(value) {
  if (typeof value === 'number') return Number.isFinite(value) ? value : undefined;
  if (Array.isArray(value)) {
    const projected = value.map(numericTimingProjection).filter((item) => item !== undefined);
    return projected.length ? projected : undefined;
  }
  if (value && typeof value === 'object') {
    const projected = Object.fromEntries(
      Object.keys(value).sort()
        .map((key) => [key, numericTimingProjection(value[key])])
        .filter(([, item]) => item !== undefined),
    );
    return Object.keys(projected).length ? projected : undefined;
  }
  return undefined;
}

/**
 * Hash only numeric values under recognized browser timing fields. This keeps
 * provenance and other descriptive metadata editable without unpinning history.
 */
export function archivedBrowserTimingDigest(receipt) {
  return timingSnapshot(receipt).digest;
}

function captureConditionsProjection(value) {
  if (Array.isArray(value)) {
    return value.map(captureConditionsProjection);
  }
  if (!value || typeof value !== 'object') return value;

  return Object.fromEntries(
    Object.keys(value).sort()
      .filter((key) => key !== 'timingEvidenceProvenance'
        && !MEASUREMENT_KEYS.has(key)
        && !isArchivedBrowserTimingKey(key))
      .map((key) => [key, captureConditionsProjection(value[key])]),
  );
}

/**
 * Hash archived report content that describes the run, excluding measurements
 * and provenance so a provenance-only correction does not rewrite history.
 */
export function archivedBrowserCaptureConditionsDigest(receipt) {
  const projection = captureConditionsProjection(receipt);
  return `sha256-${createHash('sha256').update(JSON.stringify(projection)).digest('hex')}`;
}

export function validateArchivedBrowserTimingMeasurements(archive, baseline) {
  const errors = [];
  const archivePaths = Object.keys(archive ?? {}).sort();
  const baselinePaths = Object.keys(baseline ?? {}).sort();

  for (const path of baselinePaths) {
    if (!Object.hasOwn(archive ?? {}, path)) {
      errors.push(`${path}: archived browser-validation report is missing.`);
      continue;
    }
    const actual = timingSnapshot(archive[path]);
    const entry = baseline[path];
    const originalDigest = typeof entry === 'string' ? entry : entry?.digest;
    if (typeof originalDigest !== 'string' || !/^sha256-[a-f0-9]{64}$/.test(originalDigest)) {
      errors.push(`${path}: frozen timing baseline must contain a sha256 digest.`);
      continue;
    }

    let expectedDigest = originalDigest;
    const rebaselines = typeof entry === 'object' && entry !== null
      ? entry.rebaselines ?? []
      : [];
    if (!Array.isArray(rebaselines)) {
      errors.push(`${path}: timing rebaselines must be an array of documented before/after comparisons.`);
      continue;
    }
    let invalidRebaseline = false;
    for (const [index, rebaseline] of rebaselines.entries()) {
      const label = `${path}: timing rebaseline ${index + 1}`;
      if (!rebaseline || typeof rebaseline !== 'object' || Array.isArray(rebaseline)) {
        errors.push(`${label} must be an object with a reason and before/after timing snapshots.`);
        invalidRebaseline = true;
        continue;
      }
      if (!validateRebaselineReason(rebaseline.reason)) {
        errors.push(`${label} requires a concise reason (${MIN_REBASELINE_REASON_LENGTH}-${MAX_REBASELINE_REASON_LENGTH} characters).`);
        invalidRebaseline = true;
      }
      if (!isValidTimingSnapshot(rebaseline.before) || !isValidTimingSnapshot(rebaseline.after)) {
        errors.push(`${label} requires valid, readable before/after timing snapshots.`);
        invalidRebaseline = true;
        continue;
      }
      if (rebaseline.before.digest !== expectedDigest) {
        errors.push(`${label} before digest does not continue the frozen timing history.`);
        invalidRebaseline = true;
      }
      if (rebaseline.before.digest === rebaseline.after.digest) {
        errors.push(`${label} must record a change in numeric timing values.`);
        invalidRebaseline = true;
      }
      expectedDigest = rebaseline.after.digest;
    }
    if (invalidRebaseline) continue;
    if (actual.digest !== expectedDigest) {
      const lastRebaseline = rebaselines.at(-1);
      const comparison = lastRebaseline
        ? ` Last documented change (${lastRebaseline.reason}): before [${formatTimingMeasurements(lastRebaseline.before.measurements)}]; after [${formatTimingMeasurements(lastRebaseline.after.measurements)}]. Current measurements: [${formatTimingMeasurements(actual.measurements)}].`
        : ` Current measurements: [${formatTimingMeasurements(actual.measurements)}].`;
      errors.push(`${path}: archived browser timing values differ from the frozen baseline.${comparison}`);
    }
  }
  for (const path of archivePaths) {
    if (!Object.hasOwn(baseline ?? {}, path)) {
      errors.push(`${path}: browser-validation report is not recorded in the frozen timing baseline.`);
    }
  }
  return errors;
}

export function validateArchivedBrowserCaptureConditions(archive, baseline) {
  const errors = [];
  const archivePaths = Object.keys(archive ?? {}).sort();
  const baselinePaths = Object.keys(baseline ?? {}).sort();

  for (const path of baselinePaths) {
    if (!Object.hasOwn(archive ?? {}, path)) {
      errors.push(`${path}: archived browser-validation report is missing.`);
      continue;
    }
    const actualDigest = archivedBrowserCaptureConditionsDigest(archive[path]);
    if (actualDigest !== baseline[path]) {
      errors.push(`${path}: archived browser capture conditions differ from the frozen baseline.`);
    }
  }
  for (const path of archivePaths) {
    if (!Object.hasOwn(baseline ?? {}, path)) {
      errors.push(`${path}: browser-validation report is not recorded in the frozen capture-conditions baseline.`);
    }
  }
  return errors;
}

async function findBrowserValidationReports(directory) {
  const reports = {};
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = resolve(directory, entry.name);
    if (entry.isDirectory()) {
      Object.assign(reports, await findBrowserValidationReports(path));
    } else if (entry.name === 'browser-validation.json') {
      const relativePath = relative(process.cwd(), path).split('\\').join('/');
      reports[relativePath] = JSON.parse(await readFile(path, 'utf8'));
    }
  }
  return reports;
}

export async function validateArchivedBrowserTimingArchive({
  auditDirectory = resolve(DEFAULT_AUDIT_DIRECTORY),
  baselinePath = resolve(DEFAULT_TIMING_BASELINE),
  captureConditionsBaselinePath = resolve(DEFAULT_CAPTURE_CONDITIONS_BASELINE),
} = {}) {
  const baseline = JSON.parse(await readFile(baselinePath, 'utf8'));
  const captureConditionsBaseline = JSON.parse(
    await readFile(captureConditionsBaselinePath, 'utf8'),
  );
  const archive = await findBrowserValidationReports(auditDirectory);
  return [
    ...validateArchivedBrowserTimingMeasurements(archive, baseline),
    ...validateArchivedBrowserCaptureConditions(archive, captureConditionsBaseline),
  ];
}

/**
 * Legacy browser-validation receipts put timing samples in root-level checks
 * and performance collections. Those samples must declare what they describe.
 */
export function validateBrowserTimingProvenance(receipt) {
  if (!receipt || typeof receipt !== 'object' || Array.isArray(receipt)) return [];
  const hasLegacyTiming = ['checks', 'performance']
    .some((key) => hasBrowserTimingData(receipt[key]));
  if (!hasLegacyTiming && !receipt.timingEvidenceProvenance) return [];

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

export function resolveAsusRunEvidence(evidencePath, evidenceRoot = PROJECT_EVIDENCE_ROOT) {
  if (typeof evidencePath !== 'string' || !evidencePath.endsWith('.json')) {
    throw new Error('rawRunEvidence must reference a JSON file.');
  }
  const external = evidencePath.startsWith('project-evidence:');
  const path = external ? evidencePath.slice('project-evidence:'.length) : evidencePath;
  // Keep references portable and forbid alternate drive, UNC and traversal forms.
  if (!path || path.includes('\\') || path.includes(':') || isAbsolute(path)
    || path.split('/').some(part => !part || part === '.' || part === '..')) {
    throw new Error('rawRunEvidence must stay inside the repository or approved project evidence home.');
  }
  const root = realpathSync(external ? evidenceRoot : PROJECT_ROOT);
  const resolvedPath = realpathSync(resolve(root, path));
  const within = relative(root, resolvedPath);
  if (within.startsWith('..') || isAbsolute(within)) {
    throw new Error('rawRunEvidence must stay inside the repository or approved project evidence home, including symlinks.');
  }
  return resolvedPath;
}

function validateAsusRunEvidence(record, label, evidenceRoot) {
  const errors = [];
  const evidencePath = record.rawRunEvidence;
  const evidenceReferences = typeof record.evidence === 'string'
    ? [record.evidence]
    : Array.isArray(record.evidence) ? record.evidence : [];

  if (typeof evidencePath !== 'string' || !evidencePath.trim()) {
    return [`${label}: rawRunEvidence must reference a machine-readable ASUS browser-run JSON file.`];
  }
  if (!evidenceReferences.includes(evidencePath)) {
    errors.push(`${label}: rawRunEvidence must also appear in the evidence references.`);
  }
  let capture;
  try {
    const resolvedPath = resolveAsusRunEvidence(evidencePath, evidenceRoot);
    capture = JSON.parse(readFileSync(resolvedPath, 'utf8'));
  } catch (error) {
    return [...errors, `${label}: rawRunEvidence could not be read as JSON (${error.message}).`];
  }

  if (!capture || typeof capture !== 'object' || Array.isArray(capture)
    || capture.schema !== ASUS_RUN_EVIDENCE_SCHEMA) {
    return [...errors, `${label}: rawRunEvidence must use the ${ASUS_RUN_EVIDENCE_SCHEMA} format.`];
  }
  if (typeof capture.representativeWorkload !== 'string'
    || !present(capture.representativeWorkload)) {
    errors.push(`${label}: rawRunEvidence representativeWorkload must be a non-empty string.`);
  } else if (capture.representativeWorkload !== record.representativeWorkload) {
    errors.push(`${label}: representativeWorkload does not match rawRunEvidence.`);
  }
  if (typeof capture.observedDurationSeconds !== 'number'
    || !Number.isFinite(capture.observedDurationSeconds)
    || capture.observedDurationSeconds <= 0) {
    errors.push(`${label}: rawRunEvidence observedDurationSeconds must be a positive number.`);
  } else if (capture.observedDurationSeconds !== record.observedDurationSeconds) {
    errors.push(`${label}: observedDurationSeconds does not match rawRunEvidence.`);
  }

  const captureViewport = capture.viewportCssPixels;
  const receiptViewport = record.viewportCssPixels;
  if (!captureViewport || typeof captureViewport !== 'object' || Array.isArray(captureViewport)
    || !Number.isFinite(captureViewport.width) || captureViewport.width <= 0
    || !Number.isFinite(captureViewport.height) || captureViewport.height <= 0) {
    errors.push(`${label}: rawRunEvidence viewportCssPixels must record positive CSS-pixel width and height.`);
  } else if (captureViewport.width !== receiptViewport?.width
    || captureViewport.height !== receiptViewport?.height) {
    errors.push(`${label}: viewportCssPixels does not match rawRunEvidence.`);
  }
  if (typeof capture.devicePixelRatio !== 'number'
    || !Number.isFinite(capture.devicePixelRatio)
    || capture.devicePixelRatio <= 0) {
    errors.push(`${label}: rawRunEvidence devicePixelRatio must be a positive number.`);
  } else if (capture.devicePixelRatio !== record.devicePixelRatio) {
    errors.push(`${label}: devicePixelRatio does not match rawRunEvidence.`);
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
  // Existing proposals and unscored observations have no approved revisions yet.
  if (snapshots === undefined) return errors;
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
export function validateDevicePerformanceReceipt(receipt, { evidenceRoot = PROJECT_EVIDENCE_ROOT } = {}) {
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
      errors.push(...validateAsusRunEvidence(record, label, evidenceRoot));
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
  let archiveErrors;
  try {
    archiveErrors = await validateArchivedBrowserTimingArchive();
  } catch (error) {
    console.error(`FAIL archived browser run baseline: ${error.message}`);
    process.exitCode = 1;
    return;
  }
  if (archiveErrors.length) {
    console.error('FAIL archived browser timing and capture conditions');
    for (const error of archiveErrors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log(`PASS ${receiptPath}: receipt evidence and archived browser timing and capture conditions are valid.`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  await runCli();
}
