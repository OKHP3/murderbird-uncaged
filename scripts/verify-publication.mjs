/** Verify the explicit exhibit/folio release; the review has its own allowlist. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,readdir,mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {assertPublicationBoundary} from './publication-boundary.mjs';
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
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
if(process.env.GITHUB_SHA){assert.equal(release.revision,process.env.GITHUB_SHA);assert.equal(release.workingTreeDirty,false,"CI release must use a clean checkout");}
assert.deepEqual(release.files.map(f=>f.path).sort(),output.filter(f=>f!=='release.json'));
for(const file of release.files){const bytes=await readFile('dist/'+file.path);assert.equal(bytes.length,file.bytes,file.path);assert.equal(sha(bytes),file.sha256,file.path);}
const proof=[];
for(const name of await files('public')) {
  const source=await readFile('public/'+name), built=await readFile('dist/'+name);
  assert(!source.subarray(0,45).toString().startsWith('version https://git-lfs'),name);
  assert.equal(sha(source),sha(built),'Public asset changed: '+name);
  allowed.add(name);
}
const [presenceSource,fallbackSource]=await Promise.all([
  readFile('src/scene/presence-exhibit.js','utf8'),
  readFile('src/scene/fallback.js','utf8'),
]);
const modelPaths=[...presenceSource.matchAll(/new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.glb)['"],\s*import\.meta\.url\)/g)].map(match=>match[1]);
assert.deepEqual(modelPaths,['assets/models/uncaged-neutral-v2/murderbird-neutral-v2.glb'],'The exhibit must select the authorized neutral-v2 GLB.');
const previewPaths=Object.fromEntries([...fallbackSource.matchAll(/^\s*(maker|mechanic|builder):\s*new URL\(['"]\.\.\/\.\.\/(assets\/models\/[^'"]+\.png)['"],\s*import\.meta\.url\)/gm)].map(match=>[match[1],match[2]]));
assert.deepEqual(Object.keys(previewPaths).sort(),['builder','maker','mechanic'],'Fallback must select exactly one preview for each era.');
for(const [era,path] of Object.entries(previewPaths))assert.equal(path,`assets/models/uncaged-neutral-v2/${era}-preview.png`,`${era} fallback must select its authorized neutral-v2 preview.`);
const neutralInventory=JSON.parse(await readFile('assets/models/uncaged-neutral-v2/neutral-inventory.json','utf8'));
assert.equal(neutralInventory.status,'neutral geometry proposal awaiting owner review');
assert(Array.isArray(neutralInventory.generatedFiles),'Neutral inventory must enumerate generated source files.');
const generatedFiles=new Map(neutralInventory.generatedFiles.map(file=>[file.path,file]));
assert.equal(generatedFiles.size,neutralInventory.generatedFiles.length,'Neutral inventory contains duplicate generated paths.');
const activeModelSources=[...modelPaths,...Object.values(previewPaths)];
const sources=[];
for(const path of activeModelSources) {
  const recorded=generatedFiles.get(path);
  assert(recorded,`Active exhibit asset is absent from neutral inventory: ${path}`);
  const bytes=await readFile(path);
  assert.equal(bytes.length,recorded.bytes,`Inventory byte count differs: ${path}`);
  assert.equal(sha(bytes),recorded.sha256,`Inventory hash differs: ${path}`);
  sources.push({path,bytes:recorded.bytes,sha256:recorded.sha256});
}
sources.push(...JSON.parse(await readFile('provenance/story-media-publication-2026-09-27.json','utf8')).assets);
const emitted=new Map();
for(const name of output.filter(n=>n.startsWith('assets/'))) {
  const bytes=await readFile('dist/'+name);
  assert(!bytes.subarray(0,45).toString().startsWith('version https://git-lfs'),name);
  emitted.set(name,{bytes:bytes.length,sha256:sha(bytes)});
}
for(const source of sources) {
  const bytes=await readFile(source.path);
  assert.equal(bytes.length,source.bytes,source.path);
  assert.equal(sha(bytes),source.sha256,source.path);
  const matches=[...emitted].filter(([,v])=>v.sha256===source.sha256);
  assert.equal(matches.length,1,'Expected one exact emitted copy: '+source.path);
  allowed.add(matches[0][0]);proof.push({...source,emitted:matches[0][0]});
}
assertPublicationBoundary(output,allowed);
execFileSync('python3',['scripts/prepare-review-release.py','--check'],{stdio:'inherit'});
await mkdir('.local/publication',{recursive:true});
const report={generatedAt:new Date().toISOString(),status:'passed',revision:process.env.GITHUB_SHA||execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),modelSha256:generatedFiles.get(modelPaths[0]).sha256,media:proof,files:output};
await writeFile('.local/publication/build-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(`Publication verified: ${output.length} files; ${proof.length} exact model/folio/fallback assets.`);
