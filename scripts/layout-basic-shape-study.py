"""Label the locally rendered primitive studies and create the review gallery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/audit/basic-shape-study01'
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(FONT,19)
large=ImageFont.truetype(FONT,25)
small=ImageFont.truetype(FONT,16)
views=['front','top','side','rear']
parts=[('head','H','Head + bill'),('neck','N','Neck'),
       ('torso','T','Torso + compact rear'),('legs','L','Legs + feet')]

def row(group,code,title):
    sheet=Image.new('RGB',(1536,442),'#f8fafb')
    draw=ImageDraw.Draw(sheet)
    draw.text((15,7),title,font=large,fill='#1b2730')
    for i,view in enumerate(views):
        path=OUT/f'{group}-{view}.png'
        with Image.open(path) as img:
            assert img.size==(384,384)
            sheet.paste(img.convert('RGB'),(i*384,58))
        draw.text((i*384+15,38),f'{code}{i+1}  {view.upper()}',font=small,fill='#344653')
    sheet.save(OUT/f'{group}-sheet.png')
    return sheet

full=row('assembled','A','Assembly — same scale in all four views')
sheet=Image.new('RGB',(1536,4*442+72),'#f8fafb')
for i,(group,code,title) in enumerate(parts):
    sheet.paste(row(group,code,title),(0,i*442))
draw=ImageDraw.Draw(sheet)
draw.text((15,4*442+14),'Part rows enlarged separately. Use assembly for relative sizes. Top views: beak/forward at image top.',font=small,fill='#344653')
draw.text((15,4*442+40),'Draft rounded forms for owner notes — hidden surfaces inferred; no materials, armor or wings.',font=small,fill='#344653')
sheet.save(OUT/'parts-sheet.png')
sections='\n'.join(f'<section><h2>{title}</h2><img src="{group}-sheet.png" alt="{title}: front top side rear"></section>' for group,code,title in parts)
(OUT/'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MurderBird — basic shape study</title><style>body{font:17px/1.5 system-ui;color:#24313a;background:#f8fafb;max-width:1500px;margin:30px auto;padding:0 20px}h1,h2{line-height:1.2}img{width:100%;height:auto}section{margin:40px 0}textarea{width:100%;min-height:180px;box-sizing:border-box;padding:15px;font:17px/1.5 system-ui;border:1px solid #8999a3;border-radius:8px}small{color:#586b76}a{color:#315877}</style>
<h1>MurderBird: basic shape study</h1><p>One proposed rounded-form bird, viewed from four directions. This is an editable shape proposal for your notes, not the detailed model or an approved likeness.</p>
<p><b>Front / top / side / rear.</b> Top views point forward toward the top of the image; side views face right. Individual part rows are enlarged independently. The assembly shows their relative sizes.</p>
<section><h2>Whole bird</h2><img src="assembled-sheet.png" alt="Assembly in front top side rear views"></section>
'''+sections+'''<h2>Your adjustment notes</h2><p>Use a view ID such as H3 (head side), T2 (torso top), or L1 (legs front). Describe width, height, length, tilt or connection position. Notes below stay in this browser until you copy them into the chat.</p>
<textarea id="notes" aria-label="Your adjustment notes" placeholder="H3: ...&#10;N3: ...&#10;T2: ...&#10;L1: ..."></textarea><p><small>Next: revise these shapes from your notes, then overlay them on the original reference images. Detailed model changes follow that review.</small></p>
<p><a href="parts-sheet.png">Download all part views</a> · <a href="assembled-sheet.png">Download assembly</a> · <a href="murderbird-basic-shapes.blend">Editable shape study</a></p>
<script>const n=document.getElementById('notes');try{n.value=localStorage.getItem('murderbird-basic-shape-study01-notes')||'';n.addEventListener('input',()=>localStorage.setItem('murderbird-basic-shape-study01-notes',n.value));}catch{}</script></html>''')
files=[p for p in OUT.iterdir() if p.suffix in ('.png','.blend','.html')]
(OUT/'manifest.json').write_text(json.dumps({
    'status':'owner review pending',
    'generator':'Blender Workbench orthographic renders; Pillow labels and layout; no AI image generation',
    'images':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)],
    'validation':{'rendered_views':20,'view_resolution':[384,384],
                  'source_model_modified':False,'reference_images_modified':False},
},indent=2)+'\n')
