// node make-portable.mjs DIST_DIRECTORY FIRST_CHOICE.glb FALLBACK.jpg OUTPUT.html
// Build from the self-contained glTF binary and final Vite viewer assets.
import { createReadStream, createWriteStream } from 'node:fs'
import { open, readFile, realpath, rename, stat, unlink } from 'node:fs/promises'
import { resolve, dirname, basename, extname, relative, isAbsolute } from 'node:path'
import { pipeline } from 'node:stream/promises'
import { randomUUID } from 'node:crypto'

const [distArg, modelArg, stillArg, outputArg] = process.argv.slice(2)
if (process.argv.length !== 6) {
  throw new Error('Usage: node make-portable.mjs DIST_DIRECTORY MODEL.glb FALLBACK.jpg OUTPUT.html')
}

const dist = await realpath(distArg)
const model = await realpath(modelArg)
const still = await realpath(stillArg)
const output = resolve(outputArg)
if (!/\.html?$/i.test(output)) throw new Error('The output must be an HTML file.')
const indexPath = resolve(dist, 'index.html')
if (output === indexPath) throw new Error('Choose a separate portable output. The HTTP index must remain available.')

async function fromDist(parent, asset) {
  if (/[?#:]/.test(asset) || isAbsolute(asset)) throw new Error('Expected a local built asset: ' + asset)
  const file = await realpath(resolve(parent, asset))
  const rel = relative(dist, file)
  if (!rel || rel.startsWith('..') || isAbsolute(rel)) throw new Error('Asset is outside the viewer build.')
  if (!(await stat(file)).isFile()) throw new Error('Built asset is not a file: ' + asset)
  return file
}

async function checkModel() {
  const file = await open(model, 'r')
  try {
    const header = Buffer.alloc(20)
    await file.read(header, 0, header.length, 0)
    if (header.toString('ascii', 0, 4) !== 'glTF' || header.readUInt32LE(4) !== 2 ||
        header.readUInt32LE(8) !== (await file.stat()).size || header.toString('ascii', 16, 20) !== 'JSON') {
      throw new Error('The supplied model is not a complete glTF 2.0 binary.')
    }
    const length = header.readUInt32LE(12)
    if (length < 2 || length > header.readUInt32LE(8) - 20) throw new Error('Invalid glTF JSON length.')
    const json = Buffer.alloc(length)
    const {bytesRead} = await file.read(json, 0, json.length, 20)
    if (bytesRead !== length) throw new Error('Incomplete glTF JSON.')
    const asset = JSON.parse(json.toString('utf8'))
    for (const item of [...asset.buffers ?? [], ...asset.images ?? []]) {
      if (item.uri && !item.uri.startsWith('data:')) throw new Error('The GLB references an external resource.')
    }
    if (!asset.animations?.some(clip => /first[\s_.-]*choice/i.test(clip.name ?? '') && clip.channels?.length)) {
      throw new Error('A named First Choice animation is required for the portable experience.')
    }
  } finally { await file.close() }
}

const index = await readFile(indexPath, 'utf8')
const moduleTag = /<script\b[^>]*\btype="module"[^>]*\bsrc="([^"]+)"[^>]*>\s*<\/script>/gi
const styleTag = /<link\b[^>]*\brel="stylesheet"[^>]*\bhref="([^"]+)"[^>]*>/gi
const modules = [...index.matchAll(moduleTag)]
const styles = [...index.matchAll(styleTag)]
if (modules.length !== 1 || styles.length !== 1) throw new Error('Expected one bundled entry and one stylesheet.')
const modulePath = await fromDist(dist, modules[0][1])
const stylePath = await fromDist(dist, styles[0][1])
const [moduleSource, css] = await Promise.all([readFile(modulePath, 'utf8'), readFile(stylePath, 'utf8')])
if (!moduleSource.includes('firstChoiceEmbeddedAssetURL')) throw new Error('Rebuild the viewer before making the portable file.')
if (/\burl\s*\((?!\s*['"]?data:)|@import\b/i.test(css)) throw new Error('The stylesheet has an external dependency.')

const types = new Map([['.jpg', 'image/jpeg'], ['.jpeg', 'image/jpeg'], ['.png', 'image/png'],
  ['.webp', 'image/webp'], ['.avif', 'image/avif']])
const assets = new Map()
function addAsset(key, file, mime) {
  if (!/^[a-zA-Z0-9][a-zA-Z0-9_.-]*$/.test(key)) throw new Error('Unsupported embedded asset key.')
  if (assets.has(key) && assets.get(key).file !== file) throw new Error('Two asset paths share the same embedded name.')
  assets.set(key, {file, mime})
}

// Vite's relative-base ES build emits each image as new URL(path, import.meta.url).
const relativeURL = /new URL\(\s*(["'`])([^"'`]+)\1\s*,\s*import\.meta\.url\s*\)/g
const maps = [...moduleSource.matchAll(relativeURL)]
for (const match of maps) {
  const file = await fromDist(dirname(modulePath), match[2])
  const mime = types.get(extname(file).toLowerCase())
  if (!mime) throw new Error('Unsupported built asset: ' + match[2])
  addAsset(basename(file), file, mime)
}
if (maps.length !== (moduleSource.match(/import\.meta\.url/g) ?? []).length) {
  throw new Error('The build contains an unrecognized relative asset expression.')
}

await checkModel()
const jpeg = await open(still, 'r')
try {
  const signature = Buffer.alloc(3)
  await jpeg.read(signature, 0, 3, 0)
  if (!signature.equals(Buffer.from([0xff, 0xd8, 0xff]))) throw new Error('The fallback must be a JPEG still.')
} finally { await jpeg.close() }
addAsset('first-choice.glb', model, 'model/gltf-binary')
addAsset('first-choice-still.jpg', still, 'image/jpeg')

// This closure is emitted verbatim into the portable HTML. Decode each asset on
// first use, discarding its base64 DOM nodes as the chunks are decoded.
function installEmbeddedAssets() {
  const encoded = new Map()
  const resolved = new Map()
  for (const node of document.querySelectorAll('script[data-first-choice-file]')) {
    const key = node.dataset.firstChoiceFile
    if (!encoded.has(key)) encoded.set(key, [])
    encoded.get(key).push(node)
  }
  function resolveAsset(input) {
    const url = new URL(input, document.baseURI)
    if (url.protocol === 'blob:' || url.protocol === 'data:') return input
    const key = decodeURIComponent(url.pathname.split('/').pop())
    if (resolved.has(key)) return resolved.get(key)
    const chunks = encoded.get(key)
    if (!chunks) throw new Error('Missing embedded asset: ' + key)
    const type = chunks[0].dataset.mime
    const pieces = []
    for (const node of chunks) {
      if (typeof Uint8Array.fromBase64 === 'function') {
        pieces.push(Uint8Array.fromBase64(node.textContent))
      } else {
        const raw = atob(node.textContent)
        const bytes = new Uint8Array(raw.length)
        for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i)
        pieces.push(bytes)
      }
      node.remove()
      node.textContent = ''
    }
    const objectURL = URL.createObjectURL(new Blob(pieces, {type}))
    resolved.set(key, objectURL)
    encoded.delete(key)
    return objectURL
  }
  Object.defineProperty(window, 'firstChoiceEmbeddedAssetURL', {value: resolveAsset})
}

const policy = "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data: blob:; connect-src blob: data:; worker-src blob:; object-src 'none'; base-uri 'none'\">"
const scaffold = index.replace(modules[0][0], '').replace(styles[0][0], () => '<style>' + css + '</style>')
  .replace('<meta charset="utf-8">', '<meta charset="utf-8">\n  ' + policy)
const insertion = scaffold.lastIndexOf('</body>')
if (insertion < 0) throw new Error('Invalid viewer document.')
const inlineModule = moduleSource.replace(/<\/script/gi, '<\\/script')

async function* documentParts() {
  yield scaffold.slice(0, insertion)
  for (const [key, {file, mime}] of assets) {
    for await (const block of createReadStream(file, {highWaterMark: 384 * 1024})) {
      yield '<script type="application/octet-stream" data-first-choice-file="' + key + '" data-mime="' + mime + '">'
      yield block.toString('base64')
      yield '</script>\n'
    }
  }
  yield '<script>(' + installEmbeddedAssets.toString() + ')()</script>\n'
  yield '<script type="module">' + inlineModule + '</script>\n'
  yield scaffold.slice(insertion)
}

const temp = output + '.' + randomUUID() + '.tmp'
try {
  await pipeline(documentParts(), createWriteStream(temp, {flags: 'wx'}))
  await rename(temp, output)
} catch (error) {
  await unlink(temp).catch(() => {})
  throw error
}
console.log('Portable viewer:', output, '(' + (await stat(output)).size + ' bytes, ' + assets.size + ' embedded assets)')
