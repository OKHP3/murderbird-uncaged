/** Verify the V37 production release, story media, and complete dist allowlist. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,readdir,mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {assertPublicationBoundary} from './publication-boundary.mjs';

const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const manifestPath = 'assets/review/production-v37.json';
const productionStatus = 'Published current construction; likeness refinement remains open';
const modelPath = 'assets/models/whole-character-v37/attempt-release02/murderbird-whole-character-v37.glb';
const previewPaths = {
  maker: 'assets/models/whole-character-v37/attempt-release02/maker-preview.png',
  mechanic: 'assets/models/whole-character-v37/attempt-release02/mechanic-preview.png',
  builder: 'assets/models/whole-character-v37/attempt-release02/builder-preview.png',
};
const pointerPrefix = Buffer.from('version https://git-lfs.github.com/spec/v1');

async function files(dir,prefix='') {
  const result=[];
  for (const entry of await readdir(dir,{withFileTypes:true})) {
    const relative=prefix+entry.name;
    if(entry.isDirectory())result.push(...await files(dir+'/'+entry.name,relative+'/'));
    else result.push(relative);
  }
  return result.sort();
}

const output=await files('dist');
const allowed=new Set(['index.html','folio.html','release.json']);
const release=JSON.parse(await readFile('dist/release.json','utf8'));
assert.match(release.revision,/^[a-f0-9]{40}$/);
if(process.env.GITHUB_SHA){
  assert.equal(release.revision,process.env.GITHUB_SHA);
  assert.equal(release.workingTreeDirty,false,'CI release must use a clean checkout');
}
assert.deepEqual(release.files.map(file=>file.path).sort(),output.filter(file=>file!=='release.json'));
for(const file of release.files){
  const bytes=await readFile('dist/'+file.path);
  assert.equal(bytes.length,file.bytes,file.path);
  assert.equal(sha(bytes),file.sha256,file.path);
}

for(const name of await files('public')){
  const source=await readFile('public/'+name),built=await readFile('dist/'+name);
  assert(!source.subarray(0,pointerPrefix.length).equals(pointerPrefix),name);
  assert.equal(sha(source),sha(built),'Public asset changed: '+name);
  allowed.add(name);
}

const [presenceSource,fallbackSource]=await Promise.all([
  readFile('src/scene/presence-exhibit.js','utf8'),
  readFile('src/scene/fallback.js','utf8'),
]);
const modelPaths=[...presenceSource.matchAll(/new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.glb)['"],\s*import\.meta\.url\)/g)].map(match=>match[1]);
assert.deepEqual(modelPaths,[modelPath],'The exhibit must select the V37 release GLB.');
const selectedPreviews=Object.fromEntries([...fallbackSource.matchAll(/^\s*(maker|mechanic|builder):\s*new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.png)['"],\s*import\.meta\.url\)/gm)].map(match=>[match[1],match[2]]));
assert.deepEqual(selectedPreviews,previewPaths,'The illustrated fallback must use the V37 release previews.');

const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
assert.deepEqual(Object.keys(manifest).sort(),['assets','schemaVersion','status','version']);
assert.equal(manifest.schemaVersion,1);
assert.equal(manifest.version,'v37');
assert.equal(manifest.status,productionStatus);
assert(Array.isArray(manifest.assets));
assert.equal(manifest.assets.length,4,'The V37 manifest must pin one model and three fallback previews.');
const expectedSources=new Set([modelPath,...Object.values(previewPaths)]);
const sourceByPath=new Map();
for(const asset of manifest.assets){
  assert.deepEqual(Object.keys(asset).sort(),['bytes','path','sha256']);
  assert(expectedSources.has(asset.path),`Unexpected V37 production source: ${asset.path}`);
  assert(!sourceByPath.has(asset.path),`Duplicate V37 production source: ${asset.path}`);
  assert(Number.isSafeInteger(asset.bytes)&&asset.bytes>0,`Invalid byte count: ${asset.path}`);
  assert.match(asset.sha256,/^[a-f0-9]{64}$/i,`Invalid SHA-256: ${asset.path}`);
  const bytes=await readFile(asset.path);
  assert(!bytes.subarray(0,pointerPrefix.length).equals(pointerPrefix),`Unhydrated LFS source: ${asset.path}`);
  if(asset.path===modelPath)assert.equal(bytes.subarray(0,4).toString(),'glTF','V37 model is not a GLB: '+asset.path);
  else assert(bytes.subarray(0,8).equals(Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a])),'V37 fallback is not a PNG: '+asset.path);
  assert.equal(bytes.length,asset.bytes,`Manifest byte count differs: ${asset.path}`);
  assert.equal(sha(bytes),asset.sha256.toLowerCase(),`Manifest hash differs: ${asset.path}`);
  sourceByPath.set(asset.path,asset);
}
assert.deepEqual([...sourceByPath.keys()].sort(),[...expectedSources].sort(),'The manifest must cover exactly the active V37 assets.');

const sources=[...sourceByPath.values(),...JSON.parse(await readFile('provenance/story-media-publication-2026-09-27.json','utf8')).assets];
const emitted=new Map();
for(const name of output.filter(path=>path.startsWith('assets/'))){
  const bytes=await readFile('dist/'+name);
  assert(!bytes.subarray(0,pointerPrefix.length).equals(pointerPrefix),`LFS pointer in output: ${name}`);
  emitted.set(name,{bytes:bytes.length,sha256:sha(bytes)});
}
const proof=[];
for(const source of sources){
  const bytes=await readFile(source.path);
  assert.equal(bytes.length,source.bytes,source.path);
  assert.equal(sha(bytes),source.sha256.toLowerCase(),source.path);
  const matches=[...emitted].filter(([,value])=>value.bytes===source.bytes&&value.sha256===source.sha256.toLowerCase());
  assert.equal(matches.length,1,'Expected one exact emitted copy: '+source.path);
  allowed.add(matches[0][0]);
  proof.push({...source,emitted:matches[0][0]});
}

assertPublicationBoundary(output,allowed);
await mkdir('.local/publication',{recursive:true});
const report={
  generatedAt:new Date().toISOString(),status:'passed',
  revision:process.env.GITHUB_SHA||execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),
  modelSha256:sourceByPath.get(modelPath).sha256,media:proof,files:output,
};
await writeFile('.local/publication/build-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(`Local build boundary verified: ${output.length} files; ${proof.length} exact V37 model/fallback/story-media assets. This does not verify deployment.`);
