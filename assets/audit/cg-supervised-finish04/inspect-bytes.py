"""Read raw PNG/GLB bytes separately from Blender shader/image API."""
from pathlib import Path
from PIL import Image, ImageChops, ImageStat, ImageDraw
import json, struct, hashlib, io, math
OUT=Path(__file__).resolve().parent
sha=lambda x:hashlib.sha256(x).hexdigest()
def stats(raw):
 im=Image.open(io.BytesIO(raw)).convert('RGB');return [x/255 for x in ImageStat.Stat(im).mean]
def decoded_stats(raw):
 im=Image.open(io.BytesIO(raw)).convert('RGB');s=[0,0,0]
 for pixel in im.getdata():
  for i,v in enumerate(pixel):
   a=v/255;s[i]+=a/12.92 if a<=.04045 else ((a+.055)/1.055)**2.4
 return [v/(im.width*im.height) for v in s]
def glb_images(path):
 raw=path.read_bytes();n,kind=struct.unpack_from('<II',raw,12);doc=json.loads(raw[20:20+n]);binary=raw[28+n:];result=[]
 for image in doc['images']:
  view=doc['bufferViews'][image['bufferView']];data=binary[view.get('byteOffset',0):view.get('byteOffset',0)+view['byteLength']]
  result.append({'name':image.get('name'),'sha256':sha(data),'pixel_sha256':sha(Image.open(io.BytesIO(data)).convert('RGB').tobytes()),'raw_mean':stats(data),'decoded_linear_mean':decoded_stats(data) if 'color' in image.get('name','') else None})
 return doc,result
r={'swatch_png':{p.name:{'sha256':sha(p.read_bytes()),'raw_mean':stats(p.read_bytes()),'decoded_linear_mean':decoded_stats(p.read_bytes())} for p in (OUT/'swatch').glob('*.png')}}
swatch=Image.open(OUT/'swatch/emission.png').convert('RGB');r['swatch_render_center_bytes']={'old':swatch.getpixel((64,64)),'corrected':swatch.getpixel((192,64))}
doc,r['swatch_glb_images']=glb_images(OUT/'swatch/swatch.glb');r['swatch_glb_materials']=doc['materials']
doc,images=glb_images(OUT/'verification.glb');r['corrected_glb_images']=[v for v in images if 'finish04' in v['name']]
files={p.name:sha(p.read_bytes()) for p in (OUT/'textures/builder').glob('*.png')}
for rec in r['corrected_glb_images']:
 rec['exact_external_png_match']=files.get(rec['name']+'.png')==rec['sha256']
 rec['exact_rgb_byte_match']=sha(Image.open(OUT/'textures/builder'/(rec['name']+'.png')).convert('RGB').tobytes())==rec['pixel_sha256'] if (OUT/'textures/builder'/(rec['name']+'.png')).exists() else False
assert len([v for v in r['corrected_glb_images'] if 'color' in v['name']])==7
assert all(v['exact_rgb_byte_match'] for v in r['corrected_glb_images'] if 'color' in v['name'])
r['orm_raw_byte_preservation']={}
original=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt03/textures/builder')
for path in (OUT/'textures/builder').glob('*orm.png'):
 previous=original/path.name.replace('finish04','finish02')
 delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(previous).convert('RGB'))
 r['orm_raw_byte_preservation'][path.name]=max(v[1] for v in delta.getextrema())
assert all(v==0 for v in r['orm_raw_byte_preservation'].values())
r['swatch_png']['non-color.png']['data_treatment']='Non-Color: raw mean is the intended numeric value; mathematical sRGB decode above is hypothetical and not used'
a=Image.open(OUT/'neutral-corrected.png').convert('RGB');b=Image.open(OUT/'neutral-reopened.png').convert('RGB');diff=ImageChops.difference(a,b);r['native_reopen_render_max_difference']=max(x[1] for x in diff.getextrema());r['native_reopen_render_mean_difference']=ImageStat.Stat(diff).mean
old=Image.open(OUT/'neutral-old.png').convert('RGB');d=ImageChops.difference(a,old);r['old_new_render_mean_difference']=ImageStat.Stat(d).mean
sheet=Image.new('RGB',(1200,430),'#181818');sheet.paste(old,(0,30));sheet.paste(a,(600,30));draw=ImageDraw.Draw(sheet);draw.text((12,10),'Frozen03 finish02: unencoded linear palette bytes',fill='white');draw.text((612,10),'Same palette: explicit sRGB PNG transfer, finish04',fill='white');sheet.save(OUT/'neutral-side-by-side.png')
assert r['native_reopen_render_max_difference']<=1
(OUT/'byte-evidence.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'swatch_png':r['swatch_png'],'swatch_render':r['swatch_render_center_bytes'],'reopen_max':r['native_reopen_render_max_difference'],'embedded_color_pngs':[v['exact_rgb_byte_match'] for v in r['corrected_glb_images'] if 'color' in v['name']]},indent=2))
