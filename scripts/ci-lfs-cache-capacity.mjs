/** Read-only cache admission checks; never changes a limit or grants permission. */
import { appendFile, readFile, writeFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const RESERVE_BYTES = 1_000_000_000;
const validRepository = value => typeof value === 'string' && /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(value);
const validInteger = value => Number.isSafeInteger(value) && value >= 0;
const validLimit = value => Number.isInteger(value) && value >= 1 && value <= 10;
function freshTime(value, now, maxAge, label) {
  if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z$/.test(value)) throw new Error(`Invalid ${label}`);
  const time = Date.parse(value);
  if (!Number.isFinite(time) || new Date(time).toISOString().replace('.000Z', 'Z') !== value.replace('.000Z', 'Z')
      || time > now || now - time > maxAge) throw new Error(`Stale or future ${label}`);
  return value;
}

export async function inspectCacheCapacity(repository, { token, fetchImpl = fetch } = {}) {
  if (!validRepository(repository) || !token) throw new Error('Repository and existing Actions token are required');
  async function get(suffix) {
    let response;
    try {
      response = await fetchImpl(`https://api.github.com/repos/${repository}/actions/cache/${suffix}`, {
        method: 'GET', redirect: 'error', signal: AbortSignal.timeout(20_000),
        headers: { Accept: 'application/vnd.github+json', Authorization: `Bearer ${token}`, 'X-GitHub-Api-Version': '2026-03-10' },
      });
    } catch { throw new Error(`Cache ${suffix} read failed; no download permitted`); }
    return response;
  }
  const limitResponse = await get('storage-limit');
  const limit = { status: limitResponse.status,
    requestId: limitResponse.headers.get('x-github-request-id'),
    acceptedPermissions: limitResponse.headers.get('x-accepted-github-permissions') };
  if (limit.status === 200) {
    limit.value = (await limitResponse.json()).max_cache_size_gb;
    if (!Number.isInteger(limit.value) || limit.value < 1) throw new Error('Malformed cache storage limit');
  } else if (limit.status !== 403) {
    throw new Error(`Cache storage-limit HTTP ${limit.status}; no attestation fallback`);
  }
  const usageResponse = await get('usage');
  if (usageResponse.status !== 200) throw new Error(`Cache usage HTTP ${usageResponse.status}; no download permitted`);
  const data = await usageResponse.json();
  if (data.full_name !== repository || !validInteger(data.active_caches_size_in_bytes) || !validInteger(data.active_caches_count)) {
    throw new Error('Malformed or mismatched cache usage');
  }
  return { repository, observedAt: new Date().toISOString(), limit,
    usage: { repository: data.full_name, bytes: data.active_caches_size_in_bytes, count: data.active_caches_count } };
}

export function validateCacheCapacity(report, { eventName, ref, head, expectedHead, plannedBytes,
  verifiedLimitGB, checkedAt, now = Date.now() } = {}) {
  if (eventName !== 'workflow_dispatch' || ref !== 'refs/heads/main' || !/^[a-f0-9]{40}$/.test(head ?? '') || expectedHead !== head) {
    throw new Error('Cache fill requires an explicit exact-revision main dispatch');
  }
  if (!validRepository(report?.repository) || report.usage?.repository !== report.repository
      || !validInteger(report.usage?.bytes) || !validInteger(report.usage?.count)) throw new Error('Invalid cache usage evidence');
  freshTime(report.observedAt, now, 5 * 60_000, 'cache observation');
  if (!Number.isSafeInteger(plannedBytes) || plannedBytes <= 0 || plannedBytes > 3_000_000_000) throw new Error('Invalid planned payload bytes');
  let limitGB, authority, verificationTime;
  if (report.limit?.status === 200) {
    limitGB = report.limit.value;
    authority = 'api';
    verificationTime = report.observedAt;
  } else if (report.limit?.status === 403) {
    if (typeof verifiedLimitGB !== 'string' || !/^(?:[1-9]|10)$/.test(verifiedLimitGB)) throw new Error('A 403 requires an explicit verified free cache limit');
    limitGB = Number(verifiedLimitGB);
    verificationTime = freshTime(checkedAt, now, 30 * 60_000, 'operator limit verification');
    authority = 'operator-attestation';
  } else throw new Error('Unsupported cache limit response; no fallback');
  if (!validLimit(limitGB)) throw new Error('Cache limit exceeds the free 10 GB ceiling or is invalid');
  const projectedBytes = report.usage.bytes + plannedBytes + RESERVE_BYTES;
  if (!Number.isSafeInteger(projectedBytes) || projectedBytes > limitGB * 1_000_000_000) throw new Error('Insufficient conservatively estimated free cache capacity');
  return { authority, limitGB, usedBytes: report.usage.bytes, plannedBytes, reserveBytes: RESERVE_BYTES,
    projectedBytes, checkedAt: verificationTime };
}

async function main() {
  const [command, file] = process.argv.slice(2);
  if (!file || !['inspect', 'verify'].includes(command)) throw new Error('Usage: ci-lfs-cache-capacity.mjs inspect|verify REPORT_PATH');
  if (command === 'inspect') {
    const report = await inspectCacheCapacity(process.env.GITHUB_REPOSITORY, { token: process.env.GH_TOKEN });
    await writeFile(file, JSON.stringify(report) + '\n', { flag: 'wx' });
    console.log(JSON.stringify(report));
    return;
  }
  const report = JSON.parse(await readFile(file, 'utf8'));
  if (report.repository !== process.env.GITHUB_REPOSITORY) throw new Error('Cache report belongs to a different repository');
  const result = validateCacheCapacity(report, { eventName: process.env.GITHUB_EVENT_NAME,
    ref: process.env.GITHUB_REF, head: process.env.GITHUB_SHA, expectedHead: process.env.EXPECTED_REVISION,
    plannedBytes: /^(?:0|[1-9][0-9]*)$/.test(process.env.REQUIRED_BYTES ?? '') ? Number(process.env.REQUIRED_BYTES) : NaN,
    verifiedLimitGB: process.env.VERIFIED_CACHE_LIMIT_GB, checkedAt: process.env.CACHE_LIMIT_CHECKED_AT });
  console.log(JSON.stringify(result));
  if (process.env.GITHUB_STEP_SUMMARY) await appendFile(process.env.GITHUB_STEP_SUMMARY,
    `Cache admission (${process.env.GITHUB_SHA}): ${JSON.stringify(result)}. Usage may lag; this estimate is not a billing cap.\n`);
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) main().catch(error => {
  console.error(error.message); process.exitCode = 1;
});
