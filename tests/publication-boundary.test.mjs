import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { assertPublicationBoundary } from '../scripts/publication-boundary.mjs';

test('authorized output inventory accepts its declared files', () => {
  assert.doesNotThrow(() => assertPublicationBoundary(['index.html', 'folio.html'], new Set(['index.html', 'folio.html'])));
});

test('isolated negative fixture rejects an unexpected private output', async () => {
  const fixture = JSON.parse(await readFile(new URL('./fixtures/publication-unexpected-output.json', import.meta.url), 'utf8'));
  assert.throws(
    () => assertPublicationBoundary(fixture.output, new Set(fixture.allowed)),
    /Unexpected runtime file: assets\/private-session\.wav/,
  );
});
