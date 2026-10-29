import assert from 'node:assert/strict';
import test from 'node:test';
import { inspectCacheCapacity, validateCacheCapacity } from '../scripts/ci-lfs-cache-capacity.mjs';

const repository = 'OKHP3/murderbird-uncaged';
const head = 'a'.repeat(40);
const now = Date.parse('2026-10-29T12:00:00.000Z');
const timestamp = (age = 0) => new Date(now - age).toISOString();
const plannedBytes = 2_736_090_200;
const reserveBytes = 1_000_000_000;

function report(overrides = {}) {
  return {
    repository,
    observedAt: timestamp(),
    limit: { status: 200, value: 10 },
    usage: { repository, bytes: 100_000_000, count: 2 },
    ...overrides,
  };
}

function approval(overrides = {}) {
  return {
    eventName: 'workflow_dispatch', ref: 'refs/heads/main', head, expectedHead: head,
    plannedBytes, verifiedLimitGB: '', checkedAt: '', now,
    ...overrides,
  };
}

function attestation(overrides = {}) {
  return approval({ verifiedLimitGB: '10', checkedAt: timestamp(60_000), ...overrides });
}

function deniedLimit(overrides = {}) {
  return report({ limit: { status: 403, requestId: 'request-test', acceptedPermissions: 'actions=read' }, ...overrides });
}

function fakeApi({ limitStatus = 200, limitBody = { max_cache_size_gb: 10 },
  usageStatus = 200, usageBody = { full_name: repository, active_caches_size_in_bytes: 100_000_000, active_caches_count: 2 },
  limitRaw, usageRaw } = {}) {
  const calls = [];
  return {
    calls,
    fetchImpl: async (url, options) => {
      calls.push({ url: String(url), options });
      const endpoint = new URL(url);
      assert.equal(endpoint.origin, 'https://api.github.com');
      const isLimit = endpoint.pathname === `/repos/${repository}/actions/cache/storage-limit`;
      assert.ok(isLimit || endpoint.pathname === `/repos/${repository}/actions/cache/usage`, endpoint.pathname);
      const status = isLimit ? limitStatus : usageStatus;
      const body = isLimit ? limitBody : usageBody;
      const raw = isLimit ? limitRaw : usageRaw;
      return new Response(raw ?? JSON.stringify(body), {
        status, headers: { 'content-type': 'application/json', 'x-github-request-id': 'request-test',
          'x-accepted-github-permissions': 'actions=read' },
      });
    },
  };
}

test('API-confirmed free capacity includes the full plan and a one-GB reserve', () => {
  const result = validateCacheCapacity(report(), approval());
  assert.equal(result.authority, 'api');
  assert.equal(result.limitGB, 10);
  assert.equal(result.usedBytes, 100_000_000);
  assert.equal(result.plannedBytes, plannedBytes);
  assert.equal(result.reserveBytes, reserveBytes);
  assert.equal(result.projectedBytes, 100_000_000 + plannedBytes + reserveBytes);
  assert.ok(Number.isFinite(Date.parse(result.checkedAt)));
});

test('only a 403 limit response can use a fresh canonical operator attestation', () => {
  const result = validateCacheCapacity(deniedLimit(), attestation());
  assert.equal(result.authority, 'operator-attestation');
  assert.equal(result.limitGB, 10);
  assert.equal(Date.parse(result.checkedAt), Date.parse(timestamp(60_000)));
  for (const status of [0, 201, 204, 301, 401, 404, 429, 500, undefined]) {
    assert.throws(() => validateCacheCapacity(report({ limit: { status } }), attestation()), `status ${status}`);
  }
});

test('a successful limit response takes precedence over operator claims', () => {
  const result = validateCacheCapacity(report({ limit: { status: 200, value: 5 } }), attestation());
  assert.equal(result.authority, 'api');
  assert.equal(result.limitGB, 5);
  for (const value of [0, -1, 11, 1.5, '10', null, undefined, NaN, Infinity]) {
    assert.throws(() => validateCacheCapacity(report({ limit: { status: 200, value } }), attestation()), `API value ${value}`);
  }
});

test('dispatch, branch and exact valid revision remain mandatory even with attestation', () => {
  const invalid = [
    { eventName: 'push' }, { eventName: 'pull_request' }, { eventName: '' },
    { ref: 'refs/heads/repair' }, { ref: 'refs/pull/81/merge' }, { ref: '' },
    { expectedHead: 'b'.repeat(40) }, { expectedHead: '' },
    { head: '', expectedHead: '' },
    { head: 'a'.repeat(39), expectedHead: 'a'.repeat(39) },
    { head: 'a'.repeat(41), expectedHead: 'a'.repeat(41) },
    { head: 'g'.repeat(40), expectedHead: 'g'.repeat(40) },
  ];
  for (const context of invalid) {
    assert.throws(() => validateCacheCapacity(deniedLimit(), attestation(context)), JSON.stringify(context));
  }
});

test('planned payload must be a positive safe integer within the existing three-GB ceiling', () => {
  for (const value of [0, -1, 1.5, 3_000_000_001, Number.MAX_SAFE_INTEGER + 1, NaN, Infinity, null, undefined]) {
    assert.throws(() => validateCacheCapacity(report(), approval({ plannedBytes: value })), `plan ${value}`);
  }
  assert.equal(validateCacheCapacity(report(), approval({ plannedBytes: 3_000_000_000 })).plannedBytes, 3_000_000_000);
});

test('403 attestation rejects missing, noncanonical or excessive limits', () => {
  for (const value of ['', '0', '-1', '11', '1.5', '01', '10.0', ' 10', '10 ', '+10', '1e1', 10, null, undefined]) {
    assert.throws(() => validateCacheCapacity(deniedLimit(), attestation({ verifiedLimitGB: value })), `attested limit ${value}`);
  }
});

test('attestation requires strict UTC time and expires after thirty minutes', () => {
  for (const checkedAt of ['', undefined, null, '2026-10-29', '2026-10-29T11:59:00',
    '2026-10-29T11:59:00+00:00', '2026-02-31T11:59:00.000Z', 'not-a-date',
    timestamp(-1), timestamp(30 * 60_000 + 1)]) {
    assert.throws(() => validateCacheCapacity(deniedLimit(), attestation({ checkedAt })), `timestamp ${checkedAt}`);
  }
  for (const checkedAt of [timestamp(30 * 60_000), '2026-10-29T11:59:00Z']) {
    assert.equal(validateCacheCapacity(deniedLimit(), attestation({ checkedAt })).authority, 'operator-attestation');
  }
});

test('a capacity report must be no more than five minutes old and never from the future', () => {
  for (const observedAt of ['', undefined, null, 'not-a-date', timestamp(-1), timestamp(5 * 60_000 + 1)]) {
    assert.throws(() => validateCacheCapacity(report({ observedAt }), approval()), `observed ${observedAt}`);
  }
  assert.equal(validateCacheCapacity(report({ observedAt: timestamp(5 * 60_000) }), approval()).authority, 'api');
});

test('usage belongs to the inspected repository and contains actual nonnegative safe integers', () => {
  for (const usage of [undefined, null, {},
    { repository: 'elsewhere/another-repository', bytes: 0, count: 0 },
    { repository, bytes: -1, count: 0 }, { repository, bytes: 0.5, count: 0 },
    { repository, bytes: '0', count: 0 }, { repository, bytes: null, count: 0 },
    { repository, bytes: NaN, count: 0 }, { repository, bytes: Infinity, count: 0 },
    { repository, bytes: Number.MAX_SAFE_INTEGER + 1, count: 0 },
    { repository, bytes: 0, count: -1 }, { repository, bytes: 0, count: 0.5 },
    { repository, bytes: 0, count: '0' }, { repository, bytes: 0, count: null },
    { repository, bytes: 0, count: Number.MAX_SAFE_INTEGER + 1 }]) {
    assert.throws(() => validateCacheCapacity(report({ usage }), approval()), JSON.stringify(usage));
  }
  assert.equal(validateCacheCapacity(report({ usage: { repository, bytes: 0, count: 0 } }), approval()).usedBytes, 0);
});

test('projected capacity includes the reserve, accepts equality and rejects one byte over', () => {
  const boundary = 10_000_000_000 - plannedBytes - reserveBytes;
  const atBoundary = report({ usage: { repository, bytes: boundary, count: 1 } });
  assert.equal(validateCacheCapacity(atBoundary, approval()).projectedBytes, 10_000_000_000);
  assert.throws(() => validateCacheCapacity(report({ usage: { repository, bytes: boundary + 1, count: 1 } }), approval()));
  assert.throws(() => validateCacheCapacity(report({ limit: { status: 200, value: 1 },
    usage: { repository, bytes: 0, count: 0 } }), approval({ plannedBytes: 1 })));
});

test('inspection uses only the two read endpoints with the pinned API version and header-only authentication', async () => {
  const token = 'capacity-test-secret-never-log';
  const api = fakeApi();
  const before = Date.now();
  const result = await inspectCacheCapacity(repository, { token, fetchImpl: api.fetchImpl });
  const after = Date.now();
  assert.equal(api.calls.length, 2);
  assert.equal(new Set(api.calls.map(call => call.url)).size, 2);
  for (const { url, options } of api.calls) {
    const headers = new Headers(options.headers);
    assert.equal(options.method ?? 'GET', 'GET');
    assert.equal(options.body, undefined);
    assert.equal(headers.get('authorization'), `Bearer ${token}`);
    assert.equal(headers.get('x-github-api-version'), '2026-03-10');
    assert.equal(headers.get('accept'), 'application/vnd.github+json');
    assert.equal(new URL(url).search, '');
    assert.ok(!url.includes(token));
  }
  assert.equal(result.repository, repository);
  assert.deepEqual(result.usage, { repository, bytes: 100_000_000, count: 2 });
  assert.equal(result.limit.status, 200);
  assert.equal(result.limit.value, 10);
  assert.ok(Date.parse(result.observedAt) >= before && Date.parse(result.observedAt) <= after);
  assert.ok(!JSON.stringify(result).includes(token));
});

test('inspection records a limit 403 while still requiring independently valid usage', async () => {
  const api = fakeApi({ limitStatus: 403, limitBody: { message: 'Resource not accessible by integration' } });
  const result = await inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: api.fetchImpl });
  assert.equal(result.limit.status, 403);
  assert.equal(result.limit.value, undefined);
  assert.equal(result.limit.requestId, 'request-test');
  assert.equal(result.limit.acceptedPermissions, 'actions=read');
  assert.deepEqual(result.usage, { repository, bytes: 100_000_000, count: 2 });
});

test('inspection rejects unexpected limit statuses and malformed successful limit data', async () => {
  for (const limitStatus of [401, 404, 429, 500]) {
    const api = fakeApi({ limitStatus });
    await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: api.fetchImpl }));
  }
  for (const limitBody of [{}, { max_cache_size_gb: '10' }, { max_cache_size_gb: null },
    { max_cache_size_gb: -1 }, { max_cache_size_gb: 0.5 }]) {
    const api = fakeApi({ limitBody });
    await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: api.fetchImpl }));
  }
  const invalidJson = fakeApi({ limitRaw: 'not JSON' });
  await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: invalidJson.fetchImpl }));
});

test('inspection never substitutes zero usage for an unsuccessful or malformed usage response', async () => {
  for (const usageStatus of [403, 404, 429, 500]) {
    const api = fakeApi({ limitStatus: 403, usageStatus });
    await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: api.fetchImpl }));
  }
  for (const usageBody of [{},
    { full_name: 'elsewhere/another-repository', active_caches_size_in_bytes: 0, active_caches_count: 0 },
    { full_name: repository, active_caches_size_in_bytes: '0', active_caches_count: 0 },
    { full_name: repository, active_caches_size_in_bytes: -1, active_caches_count: 0 },
    { full_name: repository, active_caches_size_in_bytes: 0.5, active_caches_count: 0 },
    { full_name: repository, active_caches_size_in_bytes: 0, active_caches_count: null },
    { full_name: repository, active_caches_size_in_bytes: 0, active_caches_count: '0' },
    { full_name: repository, active_caches_size_in_bytes: 0, active_caches_count: -1 },
    { full_name: repository, active_caches_size_in_bytes: Number.MAX_SAFE_INTEGER + 1, active_caches_count: 0 }]) {
    const api = fakeApi({ limitStatus: 403, usageBody });
    await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: api.fetchImpl }));
  }
  const invalidJson = fakeApi({ usageRaw: 'not JSON' });
  await assert.rejects(inspectCacheCapacity(repository, { token: 'test-token', fetchImpl: invalidJson.fetchImpl }));
});

test('inspection rejects a network failure instead of synthesizing attested capacity', async () => {
  let calls = 0;
  await assert.rejects(inspectCacheCapacity(repository, {
    token: 'test-token', fetchImpl: async () => { calls++; throw new Error('simulated network failure'); },
  }));
  assert.ok(calls >= 1 && calls <= 2);
});
