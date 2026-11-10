import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { inflateSync } from 'node:zlib';

const DEFAULT_REPORT = fileURLToPath(new URL(
  '../assets/audit/exterior-v1/dynamic-foot-review-2026-09-28/browser-foot-motion.json',
  import.meta.url,
));
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const REQUIRED_CAPTURES = [
  { movement: 'jump', observedStage: 'airborne', grounded: false },
  { movement: 'thrust', observedStage: 'brace', grounded: true },
];
const REQUIRED_FEET = ['left', 'right'];
const COLOR_CHANNELS = new Map([
  [0, 1], // grayscale
  [2, 3], // truecolor
  [3, 1], // indexed
  [4, 2], // grayscale + alpha
  [6, 4], // truecolor + alpha
]);
const VALID_BIT_DEPTHS = new Map([
  [0, new Set([1, 2, 4, 8, 16])],
  [2, new Set([8, 16])],
  [3, new Set([1, 2, 4, 8])],
  [4, new Set([8, 16])],
  [6, new Set([8, 16])],
]);
const ADAM7_PASSES = [
  [0, 0, 8, 8],
  [4, 0, 8, 8],
  [0, 4, 4, 8],
  [2, 0, 4, 4],
  [0, 2, 2, 4],
  [1, 0, 2, 2],
  [0, 1, 1, 2],
];
const CRC_TABLE = Uint32Array.from({ length: 256 }, (_, value) => {
  let crc = value;
  for (let bit = 0; bit < 8; bit += 1) {
    crc = (crc & 1) ? (0xedb88320 ^ (crc >>> 1)) : (crc >>> 1);
  }
  return crc >>> 0;
});

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function finiteNumber(value) {
  return typeof value === 'number' && Number.isFinite(value);
}

function expectedScreenshotPaths(capture, generationId) {
  const runDirectory = `runs/${generationId}`;
  return [
    `${runDirectory}/${capture.movement}-${capture.observedStage}.png`,
    `${runDirectory}/advanced-${capture.movement}.png`,
  ];
}

function pngCrc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) {
    crc = CRC_TABLE[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function passDimension(size, start, step) {
  return size <= start ? 0 : Math.ceil((size - start) / step);
}

/**
 * Check the complete PNG container and its decoded scanline layout.
 * Throws a diagnostic suitable for attaching to the referenced capture path.
 */
export function inspectPng(bytes) {
  const fail = reason => {
    throw new Error(reason);
  };
  if (!Buffer.isBuffer(bytes) || bytes.length < PNG_SIGNATURE.length
    || !bytes.subarray(0, PNG_SIGNATURE.length).equals(PNG_SIGNATURE)) {
    fail('not a PNG image');
  }

  let offset = PNG_SIGNATURE.length;
  let width;
  let height;
  let bitDepth;
  let colorType;
  let interlace;
  let paletteEntries = 0;
  let sawPalette = false;
  let sawImageData = false;
  let imageDataEnded = false;
  let sawEnd = false;
  let imageDataLength = 0;
  const imageDataParts = [];

  while (offset < bytes.length) {
    if (bytes.length - offset < 12) fail('truncated PNG chunk header');
    const length = bytes.readUInt32BE(offset);
    const chunkTypeBytes = bytes.subarray(offset + 4, offset + 8);
    const chunkType = chunkTypeBytes.toString('ascii');
    if (length > 0x7fffffff) fail(`${chunkType} chunk exceeds the PNG length limit`);
    if (!/^[A-Za-z]{4}$/.test(chunkType)) fail('invalid PNG chunk type');
    if (chunkTypeBytes[2] & 0x20) fail(`invalid reserved bit in ${chunkType} chunk`);
    const end = offset + 12 + length;
    if (!Number.isSafeInteger(end) || end > bytes.length) {
      fail(`truncated ${chunkType} chunk`);
    }
    const data = bytes.subarray(offset + 8, offset + 8 + length);
    const recordedCrc = bytes.readUInt32BE(offset + 8 + length);
    if (pngCrc32(bytes.subarray(offset + 4, offset + 8 + length)) !== recordedCrc) {
      fail(`${chunkType} chunk has an invalid CRC`);
    }

    if (!width && chunkType !== 'IHDR') fail('IHDR must be the first PNG chunk');
    if (chunkType === 'IHDR') {
      if (width !== undefined) fail('duplicate IHDR chunk');
      if (length !== 13) fail('IHDR chunk must contain 13 bytes');
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bitDepth = data[8];
      colorType = data[9];
      if (width === 0 || height === 0) fail('PNG dimensions must be greater than zero');
      if (width > 0x7fffffff || height > 0x7fffffff) fail('PNG dimensions exceed the format limit');
      if (!COLOR_CHANNELS.has(colorType) || !VALID_BIT_DEPTHS.get(colorType).has(bitDepth)) {
        fail(`invalid PNG color type ${colorType} or bit depth ${bitDepth}`);
      }
      if (data[10] !== 0 || data[11] !== 0) fail('unsupported PNG compression or filter method');
      interlace = data[12];
      if (interlace !== 0 && interlace !== 1) fail('invalid PNG interlace method');
    } else if (chunkType === 'PLTE') {
      if (sawPalette || sawImageData) fail('misplaced or duplicate PLTE chunk');
      if (colorType === 0 || colorType === 4) fail('PLTE is not permitted for grayscale PNGs');
      if (length === 0 || length > 768 || length % 3 !== 0) fail('invalid PLTE chunk length');
      paletteEntries = length / 3;
      if (colorType === 3 && paletteEntries > 2 ** bitDepth) {
        fail('PLTE contains more entries than the indexed bit depth permits');
      }
      sawPalette = true;
    } else if (chunkType === 'IDAT') {
      if (imageDataEnded) fail('IDAT chunks must be consecutive');
      if (colorType === 3 && !sawPalette) fail('indexed PNG is missing its PLTE chunk');
      sawImageData = true;
      imageDataLength += length;
      imageDataParts.push(data);
    } else if (chunkType === 'IEND') {
      if (length !== 0) fail('IEND chunk must be empty');
      if (!sawImageData) fail('PNG is missing image data');
      if (sawEnd) fail('duplicate IEND chunk');
      sawEnd = true;
      offset = end;
      if (offset !== bytes.length) fail('unexpected data after IEND chunk');
      break;
    } else {
      if (sawImageData) imageDataEnded = true;
      if ((chunkTypeBytes[0] & 0x20) === 0) fail(`unknown critical ${chunkType} chunk`);
    }

    if (chunkType !== 'IDAT' && sawImageData) imageDataEnded = true;
    offset = end;
  }

  if (width === undefined) fail('PNG is missing IHDR');
  if (!sawEnd) fail('PNG is missing IEND');
  if (colorType === 3 && !sawPalette) fail('indexed PNG is missing its PLTE chunk');
  if (imageDataLength === 0) fail('PNG image data is empty');

  const channels = COLOR_CHANNELS.get(colorType);
  const bitsPerPixel = channels * bitDepth;
  const passes = interlace === 0
    ? [[0, 0, 1, 1]]
    : ADAM7_PASSES;
  let expectedInflatedLength = 0;
  const scanlineLengths = [];
  for (const [startX, startY, stepX, stepY] of passes) {
    const passWidth = passDimension(width, startX, stepX);
    const passHeight = passDimension(height, startY, stepY);
    if (passWidth === 0 || passHeight === 0) continue;
    const scanlineLength = Math.ceil((passWidth * bitsPerPixel) / 8);
    expectedInflatedLength += (scanlineLength + 1) * passHeight;
    scanlineLengths.push({ scanlineLength, passHeight });
  }
  if (!Number.isSafeInteger(expectedInflatedLength) || expectedInflatedLength > 512 * 1024 * 1024) {
    fail('decoded PNG dimensions exceed the validation limit');
  }

  let decoded;
  try {
    const compressed = Buffer.concat(imageDataParts, imageDataLength);
    const result = inflateSync(compressed, {
      maxOutputLength: expectedInflatedLength + 1,
      info: true,
    });
    if (result.engine.bytesWritten !== compressed.length) {
      fail('PNG image data contains trailing bytes after the compressed stream');
    }
    decoded = result.buffer;
  } catch (error) {
    if (error.message === 'PNG image data contains trailing bytes after the compressed stream') {
      throw error;
    }
    fail(`PNG image data cannot be decoded (${error.message})`);
  }
  if (decoded.length !== expectedInflatedLength) {
    fail(`decoded PNG data has ${decoded.length} bytes; expected ${expectedInflatedLength}`);
  }

  let decodedOffset = 0;
  for (const { scanlineLength, passHeight } of scanlineLengths) {
    for (let row = 0; row < passHeight; row += 1) {
      const filter = decoded[decodedOffset];
      if (filter > 4) fail(`invalid PNG scanline filter ${filter}`);
      decodedOffset += scanlineLength + 1;
    }
  }

  return { width, height };
}

/**
 * Validate the report and the screenshot package it references.
 * Paths in the report are interpreted relative to the report file itself.
 */
export async function validateBrowserFootMotionReport(report, reportPath) {
  const errors = [];
  const reportDirectory = dirname(resolve(reportPath));

  if (!isRecord(report)) return ['report must be a JSON object'];
  if (report.status !== 'passed') {
    errors.push(`status must be "passed" (received ${JSON.stringify(report.status)})`);
  }
  const validGenerationId = typeof report.generationId === 'string'
    && /^[A-Za-z0-9-]+$/.test(report.generationId);
  if (!validGenerationId) errors.push('generationId must be a non-empty path-safe run marker');
  if (!Array.isArray(report.captures)) {
    errors.push('captures must be an array');
    return errors;
  }

  for (const required of REQUIRED_CAPTURES) {
    const matching = report.captures.filter(capture =>
      isRecord(capture)
      && capture.movement === required.movement
      && capture.observedStage === required.observedStage);
    if (matching.length !== 1) {
      errors.push(
        `expected exactly one ${required.movement}/${required.observedStage} capture (found ${matching.length})`,
      );
    }
  }

  for (const [index, capture] of report.captures.entries()) {
    const label = `capture[${index}]`;
    if (!isRecord(capture)) {
      errors.push(`${label} must be an object`);
      continue;
    }

    const required = REQUIRED_CAPTURES.find(item =>
      item.movement === capture.movement && item.observedStage === capture.observedStage);
    if (!required) {
      errors.push(`${label} has an unexpected movement/stage: ${capture.movement}/${capture.observedStage}`);
    } else if (capture.grounded !== required.grounded) {
      errors.push(`${label} ${required.movement}/${required.observedStage} grounded must be ${required.grounded}`);
    }

    for (const field of ['frame', 'motionFrame', 'screenshotFrame']) {
      if (!Number.isSafeInteger(capture[field]) || capture[field] < 0) {
        errors.push(`${label} ${field} must be a non-negative integer`);
      }
    }
    if (Number.isSafeInteger(capture.frame) && Number.isSafeInteger(capture.motionFrame)
      && capture.frame !== capture.motionFrame) {
      errors.push(`${label} frame (${capture.frame}) does not match motionFrame (${capture.motionFrame})`);
    }
    if (Number.isSafeInteger(capture.motionFrame) && Number.isSafeInteger(capture.screenshotFrame)
      && capture.screenshotFrame < capture.motionFrame) {
      errors.push(`${label} screenshotFrame (${capture.screenshotFrame}) precedes motionFrame (${capture.motionFrame})`);
    }

    if (!Array.isArray(capture.feet)) {
      errors.push(`${label} feet must be an array with left and right measurements`);
    } else {
      const feetBySide = new Map();
      for (const foot of capture.feet) {
        if (!isRecord(foot) || !REQUIRED_FEET.includes(foot.side)) {
          errors.push(`${label} contains a foot measurement with an invalid side`);
          continue;
        }
        if (feetBySide.has(foot.side)) {
          errors.push(`${label} contains duplicate ${foot.side} foot measurements`);
          continue;
        }
        feetBySide.set(foot.side, foot);
      }

      for (const side of REQUIRED_FEET) {
        const foot = feetBySide.get(side);
        if (!foot) {
          errors.push(`${label} is missing ${side} foot measurement`);
          continue;
        }
        for (const field of ['groundMin', 'restGroundMin', 'clearanceFromRest']) {
          if (!finiteNumber(foot[field])) {
            errors.push(`${label} ${side} foot ${field} must be a finite number`);
          }
        }
        if (finiteNumber(foot.groundMin) && finiteNumber(foot.restGroundMin)
          && finiteNumber(foot.clearanceFromRest)
          && Math.abs((foot.groundMin - foot.restGroundMin) - foot.clearanceFromRest) > 1e-9) {
          errors.push(`${label} ${side} foot clearanceFromRest does not match groundMin - restGroundMin`);
        }
        if (capture.movement === 'jump' && capture.observedStage === 'airborne'
          && finiteNumber(foot.clearanceFromRest) && foot.clearanceFromRest <= 0.2) {
          errors.push(`${label} ${side} airborne clearanceFromRest must be greater than 0.2`);
        }
      }
    }

    if (!validGenerationId) continue;
    const expectedPaths = expectedScreenshotPaths(capture, report.generationId);
    if (!Array.isArray(capture.screenshots) || capture.screenshots.length !== expectedPaths.length) {
      errors.push(`${label} screenshots must contain the stage image and matching legacy image`);
      continue;
    }

    const expectedResolved = new Set(expectedPaths.map(path => resolve(reportDirectory, path)));
    const actualResolved = capture.screenshots.map(path =>
      typeof path === 'string' && path.trim() ? resolve(reportDirectory, path) : null);
    if (actualResolved.some(path => path === null)
      || new Set(actualResolved).size !== expectedPaths.length
      || actualResolved.some(path => !expectedResolved.has(path))) {
      errors.push(
        `${label} screenshot paths must resolve to ${expectedPaths.join(' and ')} relative to the report`,
      );
      continue;
    }

    for (const [screenshotIndex, screenshotPath] of actualResolved.entries()) {
      const screenshotLabel = `${label} screenshot "${capture.screenshots[screenshotIndex]}"`;
      try {
        const bytes = await readFile(screenshotPath);
        inspectPng(bytes);
      } catch (error) {
        if (error.code === 'ENOENT' || error.code === 'EACCES' || error.code === 'EISDIR') {
          errors.push(`${screenshotLabel} does not exist or cannot be read`);
        } else {
          errors.push(`${screenshotLabel} is damaged: ${error.message}`);
        }
      }
    }
  }

  return errors;
}

async function main() {
  const reportPath = resolve(process.argv[2] ?? DEFAULT_REPORT);
  let report;
  try {
    report = JSON.parse(await readFile(reportPath, 'utf8'));
  } catch (error) {
    throw new Error(`cannot read valid JSON report at ${reportPath}: ${error.message}`);
  }

  const errors = await validateBrowserFootMotionReport(report, reportPath);
  if (errors.length) {
    throw new Error(`foot-motion evidence validation failed:\n- ${errors.join('\n- ')}`);
  }
  console.log(`PASS: validated airborne jump and brace thrust evidence in ${reportPath}`);
}

if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main().catch(error => {
    console.error(error.message);
    process.exitCode = 1;
  });
}
