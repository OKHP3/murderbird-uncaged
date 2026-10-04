"""Compose source evidence and actual frozen renders; no generated/repainted pixels."""
from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
source=R/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
records={}
for mode in ['clay','pbr']:
 paths=[source,O/('before06-'+mode+'-source-full-bird.png'),O/'attempt02'/('after-'+mode+'-source-full-bird.png')];labels=['LOCKED SOURCE / WHOLE BIRD','ACTUAL RECEIVING06 / '+mode.upper(),'HEAD15 ATTEMPT02 / '+mode.upper()]
 canvas=Image.new('RGB',(1920,490),(30,30,30));d=ImageDraw.Draw(canvas)
 for i,(p,label) in enumerate(zip(paths,labels)):
  im=Image.open(p).convert('RGB');im=ImageOps.contain(im,(640,427));canvas.paste(im,(i*640+(640-im.width)//2,34));d.text((i*640+12,12),label,fill=(245,245,245));records[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 d.text((12,470),'Same fixed render camera and rig for06/15. Source camera is unknown. No owner acceptance; numeric fit is not likeness.',fill=(245,245,245));canvas.save(O/('whole-source-before06-head15-'+mode+'.png'))
(O/'comparison-provenance.json').write_text(json.dumps({'inputs':records,'composition':'resized actual source/render images only, labeled montage; no generated content','unknown':'source camera/depth; source symmetry; owner acceptance'},indent=2))
