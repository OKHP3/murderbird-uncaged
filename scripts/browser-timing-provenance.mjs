import { validateBrowserTimingProvenance } from './validate-device-performance-receipt.mjs';

export const UNVERIFIED_BROWSER_DEVICE =
  'NOT RECORDED — browser environment does not verify physical device identity';

export function createBrowserTimingProvenance(candidate) {
  if (typeof candidate !== 'string' || candidate.trim().length === 0) {
    throw new TypeError('Browser timing provenance requires a non-empty candidate identity.');
  }

  return {
    temporalClassification: 'CURRENT',
    device: UNVERIFIED_BROWSER_DEVICE,
    candidate,
    hardwarePerformanceEligible: false,
    reason: 'Newly captured browser timings are current to this run, but are not verified physical-device performance evidence.',
  };
}

export function assertValidBrowserTimingReport(report) {
  if (!report || typeof report !== 'object' || Array.isArray(report)) {
    throw new TypeError('Browser validation report must be an object.');
  }
  if (!report.timingEvidenceProvenance) {
    throw new Error('Refusing to write browser validation report without timing evidence provenance.');
  }

  const errors = validateBrowserTimingProvenance(report);
  if (errors.length > 0) {
    throw new Error(`Refusing to write invalid browser timing report:\n- ${errors.join('\n- ')}`);
  }
}
