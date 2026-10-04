"""Decode actual extracted GLB embedded images; no model/repository writes."""
import json,hashlib,pathlib,datetime
from PIL import Image
ROOT=pathlib.Path('/tmp/cg-recursive-export-proof02')
x=json.load(open(ROOT/'checker-results.json'));rows=[]
for r in x['results']:
 for item in r['embedded_images']:
  p=pathlib.Path(item['path']);assert p.resolve().is_relative_to(ROOT.resolve());raw=p.read_bytes();record={k:item[k] for k in ['index','name','sha256','native_packed_exact']};record['era']=r['era']
  try:
   with Image.open(p) as im:
    im.load();record.update(decode_status='PASS',format=im.format,mode=im.mode,width=im.width,height=im.height,decoded_pixel_sha256=hashlib.sha256(im.tobytes()).hexdigest(),extrema=im.getextrema(),ICC_profile_present=bool(im.info.get('icc_profile')),sRGB_chunk=im.info.get('srgb'))
  except Exception as e:record.update(decode_status='FAIL',error=repr(e))
  assert hashlib.sha256(raw).hexdigest()==item['sha256'];rows.append(record)
(ROOT/'decoded-images.json').write_text(json.dumps({'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Pillow full image load of actual GLB extracted embedded bytes; native packed compressed-byte equality is from independent Blender checker. No color conversion or resizing. Decoded raw mode pixel hashes and channel extrema retained.','limits':'Native packed byte equality implies same encoded pixels; material sampling, texture transforms and color-management/renderer parity not proven.','images':rows},indent=2)+'\n');print('decoded',len(rows),'failed',sum(r['decode_status']!='PASS' for r in rows))
