/** Check identity assets, public metadata and the source-bound presentation package. */
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const sha=b=>createHash('sha256').update(b).digest('hex');
const ledger=JSON.parse(await readFile('provenance/presentation-package-2026-09-27.json','utf8'));
for(const item of [...ledger.sources,...ledger.outputs])assert.equal(sha(await readFile(item.path)),item.sha256,item.path);
for(const [path,w,h] of [['public/og-image.png',1200,630],['public/repository-social-preview.png',1280,640],['public/icons/icon-192.png',192,192],['public/icons/icon-512.png',512,512],['public/icons/icon-maskable-512.png',512,512],['public/icons/apple-touch-icon.png',180,180],['public/icons/favicon-32.png',32,32],['public/icons/favicon-16.png',16,16],['public/icons/mstile-150.png',150,150]]){
 const b=await readFile(path);assert.equal(b.toString('hex',0,8),'89504e470d0a1a0a',path);assert.equal(b.readUInt32BE(16),w,path);assert.equal(b.readUInt32BE(20),h,path);
}
const manifest=JSON.parse(await readFile('public/site.webmanifest','utf8'));
assert.equal(manifest.id,'./');assert.equal(manifest.scope,'./');assert.equal(manifest.start_url,'./');assert(manifest.icons.some(i=>i.purpose==='maskable'));
for(const icon of manifest.icons)await readFile('public/'+icon.src.replace(/^\.\//,'').split('?')[0]);
for(const file of ['index.html','folio.html']){
 const html=await readFile(file,'utf8');
 for(const field of ['og:image:width','og:image:height','og:image:alt','twitter:image:alt','msapplication-config','apple-mobile-web-app-title'])assert(html.includes(field),file+': '+field);
 for(const href of [...html.matchAll(/<link[^>]+href="(\.\/[^"#]+)"/g)].map(m=>m[1]))await readFile('public/'+href.slice(2).split('?')[0]);
 for(const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g))JSON.parse(match[1]);
 assert(!/chai|phoebe|joey|glee-fully/i.test(html),file);
}
assert(!/chai|phoebe|joey|glee-fully/i.test(await readFile('README.md','utf8')));
console.log('Presentation verified: provenance hashes, image sizes, icon routes, metadata, JSON-LD and project identity.');
