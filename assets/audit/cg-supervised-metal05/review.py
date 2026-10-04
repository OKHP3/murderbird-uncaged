from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,struct,io
ROOT=Path(__file__).resolve().parent;INP=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged');font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
source=Image.open(INP/'assets/img/library/murderbird-locked-sept22-composite-owner-reissued-2026-10-03.jpg').convert('RGB').resize((768,512))
def display(im):
 im=im.convert('RGBA');bg=Image.new('RGBA',im.size,(35,36,37,255));bg.alpha_composite(im);return bg.convert('RGB')
sheet=Image.new('RGB',(2304,1110),(24,26,28));d=ImageDraw.Draw(sheet)
for row,profile in enumerate(('neutral','cinematic')):
 for col,(label,im) in enumerate([('Pinned full bird, source lighting',source),('Correct-linear Finish04 baseline',display(Image.open(ROOT/'attempt02'/f'before-whole-{profile}.png'))),('Metal05 attempt02 proposal',display(Image.open(ROOT/'attempt02'/f'after-whole-{profile}.png'))) ]):
  x=col*768;y=row*555;sheet.paste(im,(x,y+38));d.text((x+10,y+8),profile+' / '+label,font=font,fill='white')
sheet.save(ROOT/'whole-comparison.png')
close=Image.new('RGB',(1536,2220),(24,26,28));d=ImageDraw.Draw(close)
for row,(profile,view) in enumerate((('neutral','armor'),('neutral','leg'),('cinematic','armor'),('cinematic','leg'))):
 for col,stage in enumerate(('before','after')):
  x=col*768;y=row*555;close.paste(display(Image.open(ROOT/'attempt02'/f'{stage}-{view}-{profile}.png')),(x,y+38));d.text((x+10,y+8),stage+' / '+view+' / '+profile,font=font,fill='white')
close.save(ROOT/'close-comparison.png')
from PIL import ImageChops
clayequal=ImageChops.difference(Image.open(ROOT/'attempt02/before-whole-clay.png'),Image.open(ROOT/'attempt02/after-whole-clay.png')).getbbox() is None
parity=[]
for era in ('maker','mechanic','builder'):
 path=ROOT/'era-swatch'/(era+'-seven-family.glb')
 if not path.exists():continue
 raw=path.read_bytes();jl=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+jl]);bl=struct.unpack_from('<I',raw,20+jl)[0];binary=raw[28+jl:28+jl+bl]
 receipt=json.loads((ROOT/'era-swatch'/f'metal05-{era}-receipt.json').read_text());records=receipt['materials']
 def embedded(index):
  im=g['images'][g['textures'][index]['source']];v=g['bufferViews'][im['bufferView']];return Image.open(io.BytesIO(binary[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']])).convert('RGB')
 for m in g['materials']:
  family=m.get('extras',{}).get('cgMetal05Family');pbr=m['pbrMetallicRoughness'];record=next(x for x in records if x['family']==family and not x['local_body05_boundary'])
  c=Image.open(ROOT/'era-swatch'/record['paths'][0]).convert('RGB');orm=Image.open(ROOT/'era-swatch'/record['paths'][1]).convert('RGB');ec=embedded(pbr['baseColorTexture']['index']);eo=embedded(pbr['metallicRoughnessTexture']['index'])
  color_equal=ImageChops.difference(c,ec).getbbox() is None
  rough_equal=ImageChops.difference(orm.getchannel('G'),eo.getchannel('G')).getbbox() is None;metal_equal=ImageChops.difference(orm.getchannel('B'),eo.getchannel('B')).getbbox() is None
  parity.append({'era':era,'family':family,'glb_path':str(path.relative_to(ROOT)),'color_rgb_equal':color_equal,'roughness_green_equal':rough_equal,'metallic_blue_equal':metal_equal,'mesh_count':len(g['meshes']),'normal_scale':m.get('normalTexture',{}).get('scale',1)})
verification={'selected':'attempt02','clay_pixel_identity':clayequal,'swatch_parity':parity,'seven_families_all_three_eras':len(parity)==21,'full_geometry_export':False,'browser_webgl':'NOT RUN: swatch encoding/export only; root owns browser integration','artifact_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.rglob('*') if p.is_file() and p.suffix in ('.png','.glb','.py')}}
(ROOT/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
(ROOT/'review.html').write_text('<!doctype html><meta charset="utf-8"><title>Metal05 regional material proposal</title><style>body{background:#181b1d;color:#eee;font:17px system-ui;margin:24px}img{max-width:100%;height:auto}a{color:#7df}</style><h1>Metal05: regional worked-metal proposal</h1><p>Attempt02 selected from two bounded attempts. Fixed Body05 geometry, same cameras and two lighting profiles. Source lighting is unknown and is not reproduced. Original normal-image bytes retained; strength lowered. No source art pixels used in textures. Owner likeness acceptance remains pending.</p><p><a href="handoff.md">Handoff</a> · <a href="verification.json">Verification</a> · <a href="attempt02/metal05-builder-receipt.json">Maps, encoding and preservation</a></p><h2>Source / baseline / proposal</h2><img src="whole-comparison.png"><h2>Before / after armor and leg closeups</h2><img src="close-comparison.png"><h2>First attempt</h2><img src="attempt01/after-armor-neutral.png"><h2>Original geometry clay identity</h2><img src="attempt02/before-whole-clay.png"><img src="attempt02/after-whole-clay.png"><p>No full native scene or character geometry was exported. Seven-plane GLBs only check texture data; they do not establish runtime WebGL parity.</p>')
print('METAL05_REVIEW_COMPLETE',len(parity),'clay equality',clayequal)
