"""Label the locally rendered primitive studies and create the review gallery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import hashlib
import argparse

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--revision',choices=['01','02','03','04'],default='04')
args=parser.parse_args()
OUT=ROOT/('assets/audit/basic-shape-study'+args.revision)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
font=ImageFont.truetype(FONT,19)
large=ImageFont.truetype(FONT,25)
small=ImageFont.truetype(FONT,16)
views=['front','top','side','rear']
parts=[('head','H','Head + bill'),('neck','N','Neck'),
       ('torso','T','Torso + compact rear'),('legs','L','Legs + feet')]
if args.revision=='04':
    parts.insert(3,('shoulder-wing','S','Shoulders + short folded wing stubs'))

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
comparison_html=''
if args.revision in ('02','03','04'):
    comp=Image.new('RGB',(768,442),'#f8fafb');dc=ImageDraw.Draw(comp)
    prior=f'{int(args.revision)-1:02d}'
    for i,(name,path) in enumerate([(f'Before: study {prior}',ROOT/f'assets/audit/basic-shape-study{prior}/assembled-side.png'),(f'After: study {args.revision}',OUT/'assembled-side.png')]):
        dc.text((i*384+15,14),name,font=large,fill='#1b2730')
        with Image.open(path) as img:comp.paste(img.convert('RGB'),(i*384,58))
    comp.save(OUT/'side-comparison.png')
    comparison_html='<section><h2>Your changes — same-camera side comparison</h2><img src="side-comparison.png" alt="Before and after owner-requested shape adjustments" style="max-width:900px"></section>'
    if args.revision=='04':
        fc=Image.new('RGB',(1536,442),'#f8fafb');fd=ImageDraw.Draw(fc)
        entries=[('03 front',ROOT/'assets/audit/basic-shape-study03/assembled-front.png'),
                 ('04 front',OUT/'assembled-front.png'),
                 ('03 rear',ROOT/'assets/audit/basic-shape-study03/assembled-rear.png'),
                 ('04 rear',OUT/'assembled-rear.png')]
        for i,(name,path) in enumerate(entries):
            fd.text((i*384+15,14),name,font=large,fill='#1b2730')
            with Image.open(path) as img:fc.paste(img.convert('RGB'),(i*384,58))
        fc.save(OUT/'shoulder-comparison.png')
        comparison_html='<section><h2>Shoulder changes — matched front and rear</h2><img src="shoulder-comparison.png" alt="Study03 and study04 shoulder comparison"></section>'+comparison_html
rows=len(parts)
sheet=Image.new('RGB',(1536,rows*442+72),'#f8fafb')
for i,(group,code,title) in enumerate(parts):
    sheet.paste(row(group,code,title),(0,i*442))
draw=ImageDraw.Draw(sheet)
draw.text((15,rows*442+14),'Part rows enlarged separately. Use assembly for relative sizes. Top views: beak/forward at image top.',font=small,fill='#344653')
footer='Draft rounded forms for owner notes — hidden surfaces inferred; no materials, armor or wings.'
if args.revision=='04':footer='Draft rounded forms with short folded wing stubs — hidden surfaces inferred; no materials or armor.'
draw.text((15,rows*442+40),footer,font=small,fill='#344653')
sheet.save(OUT/'parts-sheet.png')
sections='\n'.join(f'<section><h2>{title}</h2><img src="{group}-sheet.png" alt="{title}: front top side rear"></section>' for group,code,title in parts)
(OUT/'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MurderBird — basic shape study</title><style>body{font:17px/1.5 system-ui;color:#24313a;background:#f8fafb;max-width:1500px;margin:30px auto;padding:0 20px}h1,h2{line-height:1.2}img{width:100%;height:auto}section{margin:40px 0}textarea{width:100%;min-height:180px;box-sizing:border-box;padding:15px;font:17px/1.5 system-ui;border:1px solid #8999a3;border-radius:8px}small{color:#586b76}a{color:#315877}</style>
<h1>MurderBird: basic shape study</h1><p>One proposed rounded-form bird, viewed from four directions. This is an editable shape proposal for your notes, not the detailed model or an approved likeness.</p>
<p><b>Front / top / side / rear.</b> Top views point forward toward the top of the image; side views face right. Individual part rows are enlarged independently. The assembly shows their relative sizes.</p>
<section><h2>Whole bird</h2><img src="assembled-sheet.png" alt="Assembly in front top side rear views"></section>
'''+comparison_html+sections+'''<h2>Your adjustment notes</h2><p>Use a view ID such as H3 (head side), T2 (torso top), or L1 (legs front). Describe width, height, length, tilt or connection position. Notes below stay in this browser until you copy them into the chat.</p>
<textarea id="notes" aria-label="Your adjustment notes" placeholder="H3: ...&#10;N3: ...&#10;T2: ...&#10;L1: ..."></textarea><p><small>Next: revise these shapes from your notes, then overlay them on the original reference images. Detailed model changes follow that review.</small></p>
<p><a href="parts-sheet.png">Download all part views</a> · <a href="assembled-sheet.png">Download assembly</a> · <a href="murderbird-basic-shapes.blend">Editable shape study</a></p>
<script>const n=document.getElementById('notes');const k=location.pathname+'-notes';try{n.value=localStorage.getItem(k)||'';n.addEventListener('input',()=>localStorage.setItem(k,n.value));}catch{}</script></html>''')
files=[p for p in OUT.iterdir() if p.suffix in ('.png','.jpg','.blend','.html')]
(OUT/'manifest.json').write_text(json.dumps({
    'status':'owner review pending',
    'generator':'Blender Workbench orthographic renders; Pillow labels and layout; no AI image generation',
    'images':[{'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(files)],
    'validation':{'rendered_views':(len(parts)+1)*4,'view_resolution':[384,384],
                  'source_model_modified':False,'reference_images_modified':False},
},indent=2)+'\n')
