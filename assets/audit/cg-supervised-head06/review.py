"""Display-only comparison layout; preserves source pixels and files."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
R=Path(__file__).resolve().parents[3];A=R/'assets/audit/cg-supervised-head06';O=A/'attempt02';S=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
sheet=Image.new('RGB',(1920,960),(24,27,29));d=ImageDraw.Draw(sheet)
source=Image.open(S/'context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png').crop((510,25,1000,462));source.thumbnail((640,420));sheet.paste(source,((640-source.width)//2,50));d.text((16,12),'July source: HEAD ONLY (display crop)',font=font,fill='white')
for j,(path,label) in enumerate([(O/'before-pbr-head-profile.png','Completed05 / unchanged profile'),(O/'after-pbr-head-profile.png','Head06 attempt02 / unchanged profile')],1):
 im=Image.open(path);im.thumbnail((640,427));sheet.paste(im,(640*j,50));d.text((640*j+16,12),label,font=font,fill='white')
for j,(path,label) in enumerate([(O/'before-clay-head-profile.png','Completed05 clay'),(O/'after-clay-head-profile.png','Head06 clay'),(O/'after-clay-head-front.png','Head06 front / unresolved broad saddle')]):
 im=Image.open(path);im.thumbnail((640,427));sheet.paste(im,(640*j,530));d.text((640*j+16,494),label,font=font,fill='white')
sheet.save(A/'comparison.png')
(A/'review.html').write_text('''<!doctype html><meta charset="utf-8"><title>Head06 formed sheets</title><style>body{font:17px system-ui;background:#191d20;color:#eee;margin:24px}img{max-width:100%;height:auto}.pair{display:grid;grid-template-columns:1fr 1fr;gap:10px}a{color:#7de}</style><h1>Head06: two bounded formed-sheet attempts</h1><p>Internal CG review. Source character/art all rights reserved. Owner artistic acceptance pending. Camera04 global35 is an estimated source hypothesis, reused identically before/after. No pose changes. <a href="README.md">Handoff</a> · <a href="validation.json">Checks</a> · <a href="attempt02/receipt.json">Exact hashes/settings</a></p><img src="comparison.png"><h2>Same global35 camera, full 1280×853 source aspect</h2><div class="pair"><img src="attempt02/before-clay-source-full-bird.png"><img src="attempt02/after-clay-source-full-bird.png"><img src="attempt02/before-pbr-source-full-bird.png"><img src="attempt02/after-pbr-source-full-bird.png"></div><h2>Eight final regional views</h2>'''+''.join('<img width="600" src="attempt02/after-clay-turntable-%03d.png">'%a for a in range(0,360,45)))
