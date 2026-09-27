/** Bind every published file to one source revision; no source/private files are copied. */
import {readFile,readdir,writeFile} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
async function walk(dir,prefix='') {
 const result=[];
 for(const entry of await readdir(dir,{withFileTypes:true})) {
  const name=prefix+entry.name;
  if(entry.isDirectory())result.push(...await walk(dir+'/'+entry.name,name+'/'));
  else if(name!=='release.json')result.push(name);
 }
 return result.sort();
}
const revision=process.env.GITHUB_SHA||execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim();
const files=[];
for(const path of await walk('dist')){
 const bytes=await readFile('dist/'+path);
 files.push({path,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
}
const dirty=execFileSync('git',['status','--porcelain'],{encoding:'utf8'}).trim().length>0;
await writeFile('dist/release.json',JSON.stringify({revision,workingTreeDirty:dirty,repository:'https://github.com/OKHP3/murderbird-uncaged',status:'Published for assessment; artistic acceptance pending.',files},null,2)+'\n');
console.log(`Release manifest: ${revision}, ${files.length} files${dirty?' (local modified tree)':''}.`);
