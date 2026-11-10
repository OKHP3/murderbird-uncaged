import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { deflateSync } from 'node:zlib';
import os from 'node:os';
import { dirname, join } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { inspectPng, validateBrowserFootMotionReport } from '../scripts/validate-browser-foot-motion.mjs';

const VALIDATOR_PATH = fileURLToPath(new URL('../scripts/validate-browser-foot-motion.mjs', import.meta.url));
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc & 1) ? (0xedb88320 ^ (crc >>> 1)) : (crc >>> 1);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function chunk(type, data) {
  const typeBytes = Buffer.from(type, 'ascii');
  const header = Buffer.alloc(4);
  header.writeUInt32BE(data.length);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(Buffer.concat([typeBytes, data])));
  return Buffer.concat([header, typeBytes, data, checksum]);
}

function validPng({ width = 1, height = 1, colorType = 6, interlace = 0 } = {}) {
  const channels = new Map([[0, 1], [2, 3], [3, 1], [4, 2], [6, 4]]).get(colorType);
  const bitsPerPixel = channels * 8;
  const row = Buffer.alloc(1 + width * bitsPerPixel / 8);
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width, 0);
  header.writeUInt32BE(height, 4);
  header[8] = 8;
  header[9] = colorType;
  header[12] = interlace;
  return Buffer.concat([
    PNG_SIGNATURE,
    chunk('IHDR', header),
    chunk('IDAT', deflateSync(Buffer.concat(Array.from({ length: height }, () => row)))),
    chunk('IEND', Buffer.alloc(0)),
  ]);
}

function validReport() {
  return {
    generationId: 'test-generation',
    status: 'passed',
    captures: [
      {
        movement: 'jump',
        observedStage: 'airborne',
        frame: 8,
        motionFrame: 8,
        screenshotFrame: 9,
        grounded: false,
        screenshots: [
          'runs/test-generation/jump-airborne.png',
          'runs/test-generation/advanced-jump.png',
        ],
        feet: [
          { side: 'left', groundMin: 0.4, restGroundMin: 0.002, clearanceFromRest: 0.398 },
          { side: 'right', groundMin: 0.5, restGroundMin: 0.002, clearanceFromRest: 0.498 },
        ],
      },
      {
        movement: 'thrust',
        observedStage: 'brace',
        frame: 12,
        motionFrame: 12,
        screenshotFrame: 13,
        grounded: true,
        screenshots: [
          'runs/test-generation/thrust-brace.png',
          'runs/test-generation/advanced-thrust.png',
        ],
        feet: [
          { side: 'left', groundMin: 0.002, restGroundMin: 0.002, clearanceFromRest: 0 },
          { side: 'right', groundMin: 0.002, restGroundMin: 0.002, clearanceFromRest: 0 },
        ],
      },
    ],
  };
}

async function makePackage(t, report = validReport()) {
  const root = await mkdtemp(join(os.tmpdir(), 'browser-foot-motion-'));
  t.after(() => rm(root, { recursive: true, force: true }));
  const reportPath = join(root, 'review', 'browser-foot-motion.json');
  const reportDirectory = dirname(reportPath);
  await mkdir(reportDirectory, { recursive: true });
  await writeFile(reportPath, JSON.stringify(report));

  for (const path of [
    'runs/test-generation/jump-airborne.png',
    'runs/test-generation/thrust-brace.png',
    'runs/test-generation/advanced-jump.png',
    'runs/test-generation/advanced-thrust.png',
  ]) {
    const imagePath = join(reportDirectory, path);
    await mkdir(dirname(imagePath), { recursive: true });
    await writeFile(imagePath, validPng());
  }
  return { root, reportPath };
}

test('a complete report with full, decodable PNG captures passes', async t => {
  const { reportPath } = await makePackage(t);
  assert.deepEqual(await validateBrowserFootMotionReport(validReport(), reportPath), []);
  assert.deepEqual(inspectPng(validPng()), { width: 1, height: 1 });
  assert.deepEqual(inspectPng(validPng({ interlace: 1 })), { width: 1, height: 1 });
});

test('status and required semantic captures must be present and unique', async t => {
  const { reportPath } = await makePackage(t);
  const report = validReport();
  report.status = 'failed';
  report.captures = report.captures.filter(capture => capture.movement !== 'jump');
  const errors = (await validateBrowserFootMotionReport(report, reportPath)).join('\n');
  assert.match(errors, /status must be "passed"/);
  assert.match(errors, /expected exactly one jump\/airborne capture/);

  const duplicate = validReport();
  duplicate.captures.push(structuredClone(duplicate.captures[0]));
  assert.match(
    (await validateBrowserFootMotionReport(duplicate, reportPath)).join('\n'),
    /expected exactly one jump\/airborne capture \(found 2\)/,
  );
});

test('frame and per-foot measurement omissions or mismatches fail clearly', async t => {
  const { reportPath } = await makePackage(t);
  const report = validReport();
  report.captures[0].frame = 7;
  delete report.captures[0].feet[1].groundMin;
  report.captures[1].feet[0].clearanceFromRest = 0.1;
  const errors = (await validateBrowserFootMotionReport(report, reportPath)).join('\n');
  assert.match(errors, /frame \(7\) does not match motionFrame \(8\)/);
  assert.match(errors, /right foot groundMin must be a finite number/);
  assert.match(errors, /clearanceFromRest does not match groundMin - restGroundMin/);
});

test('missing and mislabeled screenshots fail with report-relative diagnostics', async t => {
  const { reportPath } = await makePackage(t);
  const report = validReport();
  report.captures[0].screenshots[0] = 'runs/test-generation/wrong-stage.png';
  const errors = (await validateBrowserFootMotionReport(report, reportPath)).join('\n');
  assert.match(errors, /screenshot paths must resolve to runs\/test-generation\/jump-airborne\.png/);

  const missing = validReport();
  const screenshot = join(dirname(reportPath), 'runs/test-generation/thrust-brace.png');
  await rm(screenshot);
  assert.match(
    (await validateBrowserFootMotionReport(missing, reportPath)).join('\n'),
    /screenshot "runs\/test-generation\/thrust-brace\.png" does not exist or cannot be read/,
  );
});

test('signature-only or non-PNG files are rejected', async t => {
  const { reportPath } = await makePackage(t);
  const imagePath = join(dirname(reportPath), 'runs/test-generation/jump-airborne.png');
  await writeFile(imagePath, PNG_SIGNATURE);
  assert.match(
    (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n'),
    /screenshot "runs\/test-generation\/jump-airborne\.png" is damaged: PNG is missing IHDR/,
  );

  await writeFile(imagePath, 'not a PNG');
  assert.match(
    (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n'),
    /screenshot "runs\/test-generation\/jump-airborne\.png" is damaged: not a PNG image/,
  );
});

test('truncated image data is rejected and the damaged capture is identified', async t => {
  const { reportPath } = await makePackage(t);
  const imagePath = join(dirname(reportPath), 'runs/test-generation/jump-airborne.png');
  const complete = validPng();
  const idatChunkOffset = complete.indexOf(Buffer.from('IDAT')) - 4;
  const idatLength = complete.readUInt32BE(idatChunkOffset);
  const compressedStart = idatChunkOffset + 8;
  const compressedData = complete.subarray(compressedStart, compressedStart + idatLength);
  const truncated = Buffer.concat([
    complete.subarray(0, idatChunkOffset),
    chunk('IDAT', compressedData.subarray(0, -2)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
  await writeFile(imagePath, truncated);

  const errors = (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n');
  assert.match(
    errors,
    /screenshot "runs\/test-generation\/jump-airborne\.png" is damaged: PNG image data cannot be decoded/,
  );
  assert.deepEqual(await readFile(imagePath), truncated, 'validation must not modify the damaged image');
});

test('invalid PNG chunk checksums are rejected before review', async t => {
  const { reportPath } = await makePackage(t);
  const imagePath = join(dirname(reportPath), 'runs/test-generation/thrust-brace.png');
  const corrupt = validPng();
  const idatTypeOffset = corrupt.indexOf(Buffer.from('IDAT'));
  corrupt[idatTypeOffset + 4] ^= 0x01;
  await writeFile(imagePath, corrupt);

  const errors = (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n');
  assert.match(
    errors,
    /screenshot "runs\/test-generation\/thrust-brace\.png" is damaged: IDAT chunk has an invalid CRC/,
  );
});

test('compressed image data cannot contain trailing bytes', async t => {
  const { reportPath } = await makePackage(t);
  const imagePath = join(dirname(reportPath), 'runs/test-generation/advanced-thrust.png');
  const complete = validPng();
  const idatChunkOffset = complete.indexOf(Buffer.from('IDAT')) - 4;
  const idatLength = complete.readUInt32BE(idatChunkOffset);
  const compressedStart = idatChunkOffset + 8;
  const compressedData = complete.subarray(compressedStart, compressedStart + idatLength);
  const imageWithTrailingBytes = Buffer.concat([
    complete.subarray(0, idatChunkOffset),
    chunk('IDAT', Buffer.concat([compressedData, Buffer.from([0xde, 0xad])])),
    chunk('IEND', Buffer.alloc(0)),
  ]);
  await writeFile(imagePath, imageWithTrailingBytes);

  assert.match(
    (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n'),
    /screenshot "runs\/test-generation\/advanced-thrust\.png" is damaged: PNG image data contains trailing bytes/,
  );
});

test('a PNG with invalid scanline filters is rejected', async t => {
  const { reportPath } = await makePackage(t);
  const imagePath = join(dirname(reportPath), 'runs/test-generation/advanced-jump.png');
  const invalidScanline = Buffer.from([5, 0, 0, 0, 0]);
  const header = Buffer.alloc(13);
  header.writeUInt32BE(1, 0);
  header.writeUInt32BE(1, 4);
  header[8] = 8;
  header[9] = 6;
  const image = Buffer.concat([
    PNG_SIGNATURE,
    chunk('IHDR', header),
    chunk('IDAT', deflateSync(invalidScanline)),
    chunk('IEND', Buffer.alloc(0)),
  ]);
  await writeFile(imagePath, image);
  assert.match(
    (await validateBrowserFootMotionReport(validReport(), reportPath)).join('\n'),
    /screenshot "runs\/test-generation\/advanced-jump\.png" is damaged: invalid PNG scanline filter 5/,
  );
});

test('the CLI exits unsuccessfully and identifies a missing screenshot', async t => {
  const { reportPath } = await makePackage(t);
  await rm(join(dirname(reportPath), 'runs/test-generation/jump-airborne.png'));
  const result = spawnSync(process.execPath, [VALIDATOR_PATH, reportPath], { encoding: 'utf8' });
  assert.equal(result.status, 1);
  assert.match(result.stderr, /foot-motion evidence validation failed/);
  assert.match(
    result.stderr,
    /screenshot "runs\/test-generation\/jump-airborne\.png" does not exist or cannot be read/,
  );
});

test('an incomplete failed run cannot pass by reusing screenshots from an earlier generation', async t => {
  const { reportPath } = await makePackage(t);
  const report = validReport();
  report.status = 'failed';
  report.generationId = 'current-generation';
  report.captures = [report.captures[0]];
  report.captures[0].screenshots = [
    'runs/previous-generation/jump-airborne.png',
    'runs/previous-generation/advanced-jump.png',
  ];
  const previousRun = join(dirname(reportPath), 'runs/previous-generation');
  await mkdir(previousRun, { recursive: true });
  await writeFile(join(previousRun, 'jump-airborne.png'), validPng());
  await writeFile(join(previousRun, 'advanced-jump.png'), validPng());

  const errors = (await validateBrowserFootMotionReport(report, reportPath)).join('\n');
  assert.match(errors, /status must be "passed"/);
  assert.match(errors, /expected exactly one thrust\/brace capture \(found 0\)/);
  assert.match(errors, /screenshot paths must resolve to runs\/current-generation/);
});
