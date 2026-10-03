"""Build the bounded 2b review from actual rendered artifacts, never target edits."""
from pathlib import Path
import argparse, html, json
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'assets/audit/cinematic-cg-milestone02b'
p=argparse.ArgumentParser();p.add_argument('--attempt',default='attempt01');p.add_argument('--phase',default='Shape checkpoint');args=p.parse_args()
candidate=AUDIT/args.attempt
canon=ROOT/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg'
def figure(path,label):
    if not (AUDIT/path).exists():return ''
    return '<figure><img src="'+html.escape(path)+'" alt="'+html.escape(label)+'"><figcaption>'+html.escape(label)+'</figcaption></figure>'
def group(items,cls=''):
    return '<section class="'+cls+'">'+''.join(figure(*x) for x in items)+'</section>'
font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
panels=[(canon,'Locked canon'),(AUDIT/'previous/canon-neutral.png','Before: Milestone 2a'),(candidate/'canon-neutral.png',args.phase)]
sheet=Image.new('RGB',(1800,450),(22,22,22));draw=ImageDraw.Draw(sheet)
for i,(path,label) in enumerate(panels):
    im=Image.open(path).convert('RGB');im.thumbnail((600,400));sheet.paste(im,(i*600+(600-im.width)//2,48+(400-im.height)//2));draw.text((i*600+12,10),label,font=font,fill='white')
sheet.save(AUDIT/'comparison.png')
style='body{margin:24px;background:#151515;color:#eee;font:16px/1.5 system-ui;max-width:1600px}section{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}figure{margin:0}img{width:100%;display:block}figcaption{padding:8px 0}a{color:#d9af75}.two{grid-template-columns:1fr 1fr}.angles{grid-template-columns:repeat(4,1fr)}button,select{padding:8px;margin:8px;background:#242424;color:#eee;border:1px solid #777}#viewer{height:620px;background:#181818}#viewer canvas{width:100%;height:100%;display:block}.warn{border-left:4px solid #d9af75;padding:12px;background:#242424}@media(max-width:700px){section,.angles{grid-template-columns:1fr 1fr}body{margin:12px}}'
page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MurderBird — Milestone 2b review</title><style>'+style+'</style><h1>Milestone 2b — avian identity and cinematic construction</h1><p class="warn">'+html.escape(args.phase)+'. A bounded appearance study against the locked artwork. Source assets, the prior study and approved stance remain preserved. Owner artistic review is required; this is not a release or engineering result.</p>'
page+='<h2>Target and matched neutral comparison</h2><p>The two models share camera, exposure and lights. Source-camera registration is an estimate; the artwork is shown as the unchanged target.</p>'+group([('../../img/library/'+canon.name,'Locked canon — full-bird target'),('previous/canon-neutral.png','Before — rejected Milestone 2a'),(args.attempt+'/canon-neutral.png',args.phase)])
page+='<h2>Same grounded cinematic rig</h2>'+group([('previous/cinematic-hero.png','Before — identical perspective, floor and lights'),(args.attempt+'/cinematic-hero.png','Candidate — cinematic study')],'two')
page+=group([(args.attempt+'/cinematic-profile.png','Candidate — second grounded view'),(args.attempt+'/head-closeup.png','Head — hook, face and layered armor'),(args.attempt+'/body-closeup.png','Breast and folded shield — construction detail')])
for prefix,title in [('angle','Eight neutral views'),('exhibit','Eight exhibit-lit views'),('silhouette','Eight silhouette checks')]:
    items=[(args.attempt+'/'+prefix+'-%03d.png'%a,str(a)+' degrees') for a in range(0,360,45)]
    if any((AUDIT/x[0]).exists() for x in items):page+='<h2>'+title+'</h2>'+group(items,'angles')
page+='<h2>One inherited character across eras</h2>'+group([(args.attempt+'/maker/cinematic-hero.png','Maker — newly fabricated finish; dark optic'),(args.attempt+'/mechanic/cinematic-hero.png','Mechanic — aged surfaces; dark optic'),(args.attempt+'/cinematic-hero.png','Advanced — inherited surfaces; restrained awakened optic')])
page+='<h2>Pinned reference scopes</h2><p>July controls head identity; era images control finish; First Choice frames inform screen presence. Unseen details are proposals. The canon remains distinct from prior candidate 03.</p>'+group([('../../../context/threads/assets/murderbird-camera-series-2026-09-05/murderbird-owner-preferred-july-reference.png','July — head identity only'),('../../img/library/murderbird-unified-master-candidate-03-2026-09-06.png','Candidate 03 — prior body direction'),('../cinematic-cg-milestone01/first-choice-03s.png','First Choice — three-second frame')])
page+=group([('../../img/library/murderbird-unified-maker-clean-candidate-2026-09-06.png','Maker finish reference'),('../../img/library/murderbird-unified-mechanic-candidate-2026-09-06.png','Mechanic finish reference'),('../../img/library/murderbird-unified-heart-candidate-2026-09-06.png','Advanced finish reference')])
limits=(AUDIT/'limits.html').read_text() if (AUDIT/'limits.html').exists() else 'Shape checkpoint only. Facial machinery, regional finish and browser parity are still being developed. The previous broad shell and smooth head are not accepted likeness.'
page+='<h2>Review limits and worker evidence</h2><div class="warn" id="limits">'+limits+'</div>'
page+='<p><a href="assignment.json">Bounded assignment</a> · <a href="'+args.attempt+'/receipt.json">Render receipt</a> · <a href="README.md">Handoff and remaining gaps</a> · <a href="../../../goal.md">Shared goal</a></p>'
if (ROOT/'assets/models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.glb').exists() and (ROOT/'scripts/cinematic-cg-2b-browser.js').exists():
    page+='<h2>Interactive model</h2><p>Drag to orbit; scroll to zoom. Fixed renders above are also the fallback if WebGL is unavailable. Browser lighting is a preview and differs from the fixed comparisons.</p><label for="era">Era</label><select id="era"><option value="builder">Advanced</option><option value="maker">Maker</option><option value="mechanic">Mechanic</option></select><button id="reset">Reset view</button><div id="viewer"></div><p id="state">Loading candidate…</p><p><a href="../../models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.blend">Editable native character</a> · <a href="../../models/cinematic-cg-milestone02b/murderbird-cg-2b-builder.glb">Browser character</a></p>'
    if (ROOT/'scripts/cinematic-cg-2b-browser.js').exists():
        page+='<script type="importmap">{"imports":{"three":"../../../node_modules/three/build/three.module.js","three/addons/":"../../../node_modules/three/examples/jsm/"}}</script><script type="module">import {mount} from "../../../scripts/cinematic-cg-2b-browser.js";mount(document.getElementById("viewer"),document.getElementById("state"),"../../models/cinematic-cg-milestone02b/");</script>'
page+='<p>MurderBird source artwork and creative production are all rights reserved. No source artwork pixels were used as character textures. The separate CG branch is a development checkpoint; deployed V37 is unchanged.</p></html>'
(AUDIT/'review.html').write_text(page)
print(AUDIT/'review.html')
