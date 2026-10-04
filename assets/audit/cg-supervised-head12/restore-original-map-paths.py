import bpy,json,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent
BASE=Path('/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt06/murderbird-supervised-builder.blend')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def info(i):return {'path':i.filepath,'size':list(i.size),'colorspace':i.colorspace_settings.name,'packed_bytes':hashlib.sha256(bytes(i.packed_file.data)).hexdigest() if i.packed_file else None}
bpy.ops.wm.open_mainfile(filepath=str(BASE));original={i.name:info(i) for i in bpy.data.images};r={}
for attempt in ('attempt01','attempt02'):
 native=OUT/attempt/'formed-head12.blend';before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));changes={};missing=[n for n in original if n not in bpy.data.images]
 if missing:
  with bpy.data.libraries.load(str(BASE),link=False) as (src,dst):dst.images=missing.copy()
 assert all(n in bpy.data.images for n in original)
 for n,old in original.items():
  now=info(bpy.data.images[n]);assert {k:v for k,v in now.items() if k!='path'}=={k:v for k,v in old.items() if k!='path'},(n,'nonpath image change')
  if now['path']!=old['path']:changes[n]={'before_save_remapped_path':now['path'],'original_restored_path':old['path']};bpy.data.images[n].filepath=old['path']
 ids=set()
 for prop in bpy.data.bl_rna.properties:
  if prop.type=='COLLECTION':
   for item in getattr(bpy.data,prop.identifier):
    if isinstance(item,bpy.types.ID) and not isinstance(item,(bpy.types.WindowManager,bpy.types.Screen,bpy.types.WorkSpace)):ids.add(item)
 bpy.data.libraries.write(str(native),ids,path_remap='NONE',fake_user=False,compress=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert {i.name:info(i) for i in bpy.data.images if i.name in original}==original
 rec=json.loads((OUT/attempt/'receipt.json').read_text());rec['native_sha256']=sha(native);rec['original_packed_map_paths_restored_after_automatic_save_remap']=True;(OUT/attempt/'receipt.json').write_text(json.dumps(rec,indent=2));r[attempt]={'before_sha256':before,'after_sha256':sha(native),'packed_bytes_size_colorspace_unchanged':True,'original_paths_readback_exact':True,'restored_paths':changes,'restored_unused_images':missing,'save_method':'Explicit all-ID library write retains original unused image IDs without fake-user flag changes; no path remapping'};print('HEAD12_MAP_PATH_RESTORATION_COMPLETE',attempt,len(changes),flush=True)
(OUT/'map-path-restoration.json').write_text(json.dumps(r,indent=2))
