/** Verify the explicit exhibit/folio release; the review has its own allowlist. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,readdir,mkdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
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
const core=JSON.parse(await readFile('assets/audit/exterior-v1/asset-validation.json','utf8')).models[0];
const sources=[{path:core.path,bytes:core.bytes,sha256:core.sha256}];
for(const era of ['maker','mechanic','builder']) {
  const path=`assets/models/uncaged-exterior-v1/previews/${era}.png`,bytes=await readFile(path);
  sources.push({path,bytes:bytes.length,sha256:sha(bytes)});
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
for(const name of output) {
  if(name.startsWith('review/'))continue; // Separate pinned-media validator.
  if(/^assets\/[a-zA-Z][a-zA-Z0-9_.-]*-[a-zA-Z0-9_-]{8}\.(?:js|css)$/.test(name))allowed.add(name);
  assert(allowed.has(name),'Unexpected runtime file: '+name);
  assert(!/(?:^|\/)(?:\.local|provenance|context|audit|archives)(?:\/|$)|\.(?:blend|webm|zip|wav)$/i.test(name),'Private/source material: '+name);
}
execFileSync('python3',['scripts/prepare-review-release.py','--check'],{stdio:'inherit'});
await mkdir('.local/publication',{recursive:true});
const report={generatedAt:new Date().toISOString(),status:'passed',revision:process.env.GITHUB_SHA||execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim(),modelSha256:core.sha256,media:proof,files:output};
await writeFile('.local/publication/build-validation.json',JSON.stringify(report,null,2)+'\n');
console.log(`Publication verified: ${output.length} files; ${proof.length} exact model/folio/fallback assets.`);
