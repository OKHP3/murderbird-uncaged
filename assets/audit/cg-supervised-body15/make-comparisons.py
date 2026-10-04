from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import hashlib,json,sys
ROOT=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');OUT=Path(__file__).parent/f'attempt{int(sys.argv[1]) if len(sys.argv)>1 else 1:02d}';BEFORE=ROOT/'assets/audit/cg-supervised-body13/attempt01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for new in OUT.glob('final15-*.png'):
 suffix=new.name.removeprefix('final15-')
 for old in ['final13-','receiving06-']:
  source=BEFORE/(old+suffix)
  if source.exists():
   dst=OUT/('before13-'+suffix if old=='final13-' else old+suffix);dst.write_bytes(source.read_bytes());assert sha(dst)==sha(source);records.append(dict(file=dst.name,source=str(source),sha256=sha(dst),method='Byte-exact reuse of actual frozen same-camera source render; no rerender claim'))
def sheet(items,path,w=420,h=320):
 canvas=Image.new('RGB',(w*len(items),h+35),(28,28,28));draw=ImageDraw.Draw(canvas)
 for i,(p,label) in enumerate(items):
  im=Image.open(p).convert('RGB');im=ImageOps.contain(im,(w,h));canvas.paste(im,(i*w+(w-im.width)//2,35+(h-im.height)//2));draw.text((i*w+8,9),label,fill='white')
 canvas.save(path)
for suffix in ['whole35-pbr','whole35-clay','whole64-pbr','whole64-clay','front-clay','body-grazing-clay']:
 fs=[(OUT/(stage+'-'+suffix+'.png'),stage) for stage in ['receiving06','before13','final15']]
 if all(p.exists() for p,l in fs):sheet(fs,OUT/('comparison-'+suffix+'.png'))
ref=ROOT/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg';cand=ROOT/'assets/img/library/murderbird-unified-master-candidate-03-2026-09-06.png'
if (OUT/'final15-whole35-pbr.png').exists():sheet([(ref,'Locked Sept22 - canon'),(cand,'Candidate03 - body direction'),(OUT/'before13-whole35-pbr.png','Before13 fixed35'),(OUT/'final15-whole35-pbr.png','New15 fixed35')],OUT/'source-whole-comparison.png',w=480,h=340)
(OUT/'cached-render-provenance.json').write_text(json.dumps(records,indent=2)+'\n')
