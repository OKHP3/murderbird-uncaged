/** Rebuild the presentation package from preserved MurderBird artwork.
 * Usage: node scripts/build-brand-assets.mjs /absolute/path/to/sharp
 * sharp is an authoring-only tool; it is not an application dependency.
 */
import {readFile,writeFile,copyFile,mkdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {pathToFileURL} from 'node:url';
if(!process.argv[2]) throw new Error('Pass an installed sharp module path.');
const sharp=(await import(pathToFileURL(process.argv[2]).href)).default;
const art='assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png';
const icons='assets/img/favicons/';
const input=await readFile(art);
await mkdir('public/icons',{recursive:true});
const copies={
 'murderbird-v2-icon-opaque-192.png':'public/icons/icon-192.png',
 'murderbird-v2-icon-opaque-512.png':'public/icons/icon-512.png',
 'murderbird-v2-icon-maskable-512.png':'public/icons/icon-maskable-512.png',
 'murderbird-v2-icon-opaque-180.png':'public/icons/apple-touch-icon.png',
 'murderbird-v2-icon-browser-32.png':'public/icons/favicon-32.png',
 'murderbird-v2-icon-browser-16.png':'public/icons/favicon-16.png',
 'murderbird-v2-icon.ico':'public/favicon.ico',
};
for(const [source,dest] of Object.entries(copies))await copyFile(icons+source,dest);
// Native SVG wrappers preserve the existing raster emblem without redrawing it.
for(const [dest,src] of [['public/brand-icon.svg','public/icons/icon-512.png'],['public/favicon.svg','public/icons/favicon-32.png']]){
 const png=await readFile(src);
 await writeFile(dest,`<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 512 512"><title>MurderBird head emblem</title><image width="512" height="512" xlink:href="data:image/png;base64,${png.toString('base64')}"/></svg>\n`);
}
await sharp(await readFile('public/icons/icon-512.png')).resize(150,150).png().toFile('public/icons/mstile-150.png');
const overlay=await readFile('public/social-overlay.svg','utf8');
const composition=overlay.replace('<!-- REFERENCE_ART -->',`<image x="255" y="0" width="945" height="630" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${input.toString('base64')}"/>`);
await sharp(Buffer.from(composition)).png().toFile('public/og-image.png');
await copyFile('public/og-image.png','public/social-preview.png');
// GitHub recommends a 2:1 repository social card. Keep the composition intact.
await sharp('public/og-image.png').resize(1280,640,{fit:'contain',background:'#171a17'}).png().toFile('public/repository-social-preview.png');
const paths=[art,...Object.keys(copies).map(x=>icons+x),'public/social-overlay.svg','public/safari-pinned-tab.svg'];
const outputs=[...Object.values(copies),'public/brand-icon.svg','public/favicon.svg','public/icons/mstile-150.png','public/og-image.png','public/social-preview.png','public/repository-social-preview.png'];
const record=async path=>({path,sha256:createHash('sha256').update(await readFile(path)).digest('hex')});
await writeFile('provenance/presentation-package-2026-09-27.json',JSON.stringify({
 status:'Publication presentation derived from preserved MurderBird references; not approval of character likeness.',
 rights:'Creative content all rights reserved. See NOTICE.md.',
 method:'Existing icon derivatives copied byte-for-byte; native SVG editorial composition rendered with sharp. No new creature imagery generated.',
 sourceScope:'The full-body image is a lead-scoped illustration reference. Icon family delivery is documented in assets/docs/murderbird-v2-delivery-status-2026-09-05.md.',
 referenceArtLabel:'Reference art; exhibit under assessment.',
 sources:await Promise.all(paths.map(record)),outputs:await Promise.all(outputs.map(record)),
},null,2)+'\n');
console.log('MurderBird presentation assets generated.');
