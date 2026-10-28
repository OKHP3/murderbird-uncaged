import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import test from 'node:test';

const workflow = readFileSync(new URL('../.github/workflows/validate.yml', import.meta.url), 'utf8');
const uploadGate = /- name: Upload the validated Pages build\r?\n\s+if: ([^\r\n]+)/.exec(workflow)?.[1];
const deployGate = /^  deploy:\r?\n\s+if: ([^\r\n]+)/m.exec(workflow)?.[1];
const sha = 'a'.repeat(40);

test('Pages upload and deployment require an explicit exact-revision main publication', () => {
  assert.ok(uploadGate, 'Pages upload gate exists');
  assert.ok(deployGate, 'Pages deployment gate exists');
  for (const event_name of ['push', 'pull_request', 'workflow_dispatch']) {
    for (const ref of ['refs/heads/main', 'refs/heads/repair', 'refs/pull/81/merge']) {
      for (const publish_pages of [false, true]) {
        for (const expected_revision of ['', 'b'.repeat(40), sha]) {
          const context = { github: { ref, event_name, sha }, inputs: { publish_pages, expected_revision } };
          const expected = event_name === 'workflow_dispatch' && ref === 'refs/heads/main'
            && publish_pages && expected_revision === sha;
          for (const gate of [uploadGate, deployGate]) {
            assert.equal(Boolean(runInNewContext(gate, context, { timeout: 100 })), expected, JSON.stringify(context));
          }
        }
      }
    }
  }
});

test('publication preflight rejects an unapproved revision before checkout', () => {
  const preflight = workflow.indexOf('- name: Check explicit publication approval');
  const checkout = workflow.indexOf('- uses: actions/checkout');
  assert.ok(preflight >= 0 && preflight < checkout);
  const block = workflow.slice(preflight, checkout);
  assert.match(block, /if: github\.event_name == 'workflow_dispatch' && inputs\.publish_pages/);
  assert.match(block, /test "\$GITHUB_REF" = refs\/heads\/main && test "\$EXPECTED_REVISION" = "\$GITHUB_SHA"/);
  assert.match(block, /exit 1/);
});
