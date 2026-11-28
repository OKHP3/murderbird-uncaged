"""Build the HTTP preview and a complete, file-openable HTML using the same assets."""
from argparse import ArgumentParser
from pathlib import Path
import base64, hashlib, json, os, re, shutil, subprocess
here=Path(__file__).resolve().parent
parser = ArgumentParser(description=__doc__)
parser.add_argument('--loop', type=Path, help='Include the approved seamless FLAC in the hosted preview')
args = parser.parse_args()
loop = args.loop.resolve() if args.loop is not None else here / 'assets' / 'seamless-loop.flac'
if args.loop is not None or loop.exists():
    expected_loop = 'd9bc121c0c2f1a04ff8456b8aeea1ae6d48fdc1777119ef4823bebc458425a72'
    if (not loop.is_file() or loop.stat().st_size != 30_880_257
            or hashlib.sha256(loop.read_bytes()).hexdigest() != expected_loop):
        parser.error('The lossless loop must be the approved 30,880,257-byte FLAC recording.')
os.chdir(here)
bs=lambda b: base64.b64encode(b).decode('ascii')
subprocess.run(['node', 'node_modules/vite/bin/vite.js','build','--config','vite.config.mjs','--configLoader','native'],check=True)
web=here/'web'
if loop.is_file():
    with loop.open('rb') as stream:
        for part in ['loop-a.bin','loop-b.bin']:
            (web/'assets'/part).write_bytes(stream.read(16*1024*1024))
for src in (here/'assets').iterdir():
    if src.suffix in ['.pack','.mp3','.mp4','.jpg','.ico','.svg','.webmanifest','.xml','.png']:
        shutil.copyfile(src,web/'assets'/src.name)
html=(web/'index.html').read_text(encoding='utf-8')
notices="\n\n".join((here/f).read_text(encoding='utf-8') for f in ['LICENSE','NOTICE.md','third-party.txt'])
html=html.replace('</body>','<script type="text/plain" id="rights">'+notices.replace('</script','<\\/script')+'</script>\n</body>')
(web/'index.html').write_bytes(html.encode('utf-8'))
css=(web/'assets'/'index.css').read_text(encoding='utf-8')
js=(web/'assets'/'study.js').read_text(encoding='utf-8')
# Vite emits relative image URLs. The loader resolves packed resource names on open.
js=js.replace('import.meta.url','document.baseURI')
html=re.sub(r'<(?:link|meta)\b[^>]*data-host-only[^>]*>','',html)
html=re.sub(r'<meta[^>]*(?:property="og:image"|name="twitter:image")[^>]*>','',html)
html=html.replace('href="./assets/favicon-32.png"','href="data:image/png;base64,'+bs((web/'assets/favicon-32.png').read_bytes())+'"')
html=re.sub(r'<link[^>]+rel="stylesheet"[^>]*>',lambda _: '<style>'+css+'</style>',html,count=1)
html=re.sub(r'<script[^>]+src="[^"]+study.js"[^>]*></script>','',html,count=1)
policy="""<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline' 'wasm-unsafe-eval'; style-src 'unsafe-inline'; img-src blob: data:; media-src blob:; connect-src blob: data:; worker-src blob:; base-uri 'none'">"""
html=html.replace('<meta charset="utf-8">','<meta charset="utf-8">'+policy)
html=re.sub(r'src="(?:\./)?assets/advanced.jpg"',lambda _: 'src="data:image/jpeg;base64,'+bs((web/'assets/advanced.jpg').read_bytes())+'"',html,count=1)
loader="""<script>
const cache=new Map();
window.exhibitAsset=function(key){
 if(cache.has(key))return cache.get(key);
 const blocks=document.querySelectorAll('script[data-asset="'+key+'"]');
 if(!blocks.length)throw Error('Missing embedded asset '+key);
 const mime=blocks[0].dataset.type,parts=[];
 for(const b of blocks){parts.push(typeof Uint8Array.fromBase64==='function'?Uint8Array.fromBase64(b.textContent):Uint8Array.from(atob(b.textContent),c=>c.charCodeAt(0)));b.remove()}
 const url=URL.createObjectURL(new Blob(parts,{type:mime}));cache.set(key,url);return url;
};
</script>"""
assets=[p for p in sorted((web/'assets').iterdir()) if p.suffix in ['.pack','.jpg','.mp3','.mp4'] or p.name in ['phosphor.png','standing-contact.png']]
manifest={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in assets}
dest=here/'MurderBird-Three-Eras.html'
mime_types = {'.pack': 'application/octet-stream', '.jpg': 'image/jpeg', '.png': 'image/png',
             '.mp3': 'audio/mpeg', '.mp4': 'video/mp4'}
with dest.open('w', encoding='utf-8', newline='\n') as out:
    out.write(html.split('</body>')[0])
    for p in assets:
        typ=mime_types[p.suffix]
        with p.open('rb') as f:
            while block:=f.read(384*1024):
                out.write('<script type="application/octet-stream" data-asset="'+p.name+'" data-type="'+typ+'">'+bs(block)+'</script>\n')
    out.write(loader+'<script type="module">'+js.replace('</script','<\\/script')+'</script></body></html>')
manifest['portable']={'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
(here/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode('utf-8'))
print(dest.name, manifest['portable'])
