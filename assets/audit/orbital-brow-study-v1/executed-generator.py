"""Isolated head-owned broad brow proposal; no app model selection."""
from pathlib import Path
import math, hashlib, json, runpy, shutil
import bpy, bmesh
from mathutils import Vector, Matrix
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-alignment-v8/murderbird-alignment-v8.blend'
OUT=ROOT/'assets/models/uncaged-orbital-brow-study-v1'
AUDIT=ROOT/'assets/audit/orbital-brow-study-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def main():
 assert sha(BASE)=='b12c442e2f517b676cdd1fae1612730cc0ba83251d34f363285b08f2cd482478'
 assert not OUT.exists() and not AUDIT.exists()
 h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
 g=runpy.run_path(str(ROOT/'scripts/study-head-continuous-plates-v2.py'),run_name='grid_helpers')
 bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
 mats={m.name:h['material_signature'](m) for m in bpy.data.materials}
 names=[f'Forged orbital brow {s}' for s in (-1,1)]; changes=[]
 # Authored Y/Z/half-width/transverse-depth stations, not image metrology.
 path=[(-.267,1.869,.008,.151),(-.300,1.898,.025,.155),(-.352,1.901,.037,.153),(-.403,1.879,.034,.144),(-.443,1.850,.019,.127),(-.461,1.828,.004,.110)]
 for side,name in zip((-1,1),names):
  o=bpy.data.objects[name];old_world=o.matrix_world.copy();o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=old_world
  outside=[];inside=[];along=40;across=8
  for row in range(along+1):
   t=row/along;y,z,w,x=g['lerp_rows'](path,t)
   ya,za,*_=g['lerp_rows'](path,max(0,t-.001));yb,zb,*_=g['lerp_rows'](path,min(1,t+.001))
   tangent=Vector((yb-ya,zb-za)).normalized();ny=-tangent.y;nz=tangent.x
   for col in range(across+1):
    q=2*col/across-1; yy=y+ny*q*w;zz=z+nz*q*w
    xx=x+.002*(1-q*q)
    outside.append((side*xx,yy,zz));inside.append((side*(xx-.006),yy,zz))
  v,f=g['closed_grid'](outside,inside,along,across)
  info=g['apply_mesh'](name,v,f);changes.append({'name':name,'previousOwner':'cranial-cover','newOwner':'head','geometry':info})
 after=h['scene_snapshot']();assert before['empties']==after['empties'] and before['curves']==after['curves']
 for n,b in before['meshes'].items():
  if n not in names:assert b==after['meshes'][n],n
 assert mats=={m.name:h['material_signature'](m) for m in bpy.data.materials}
 OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-orbital-brow-study-v1.blend'
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
 bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
 shutil.copy2(__file__,AUDIT/'executed-generator.py')
 receipt={'status':'isolated broad brow geometry proposal, not selected','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changes':changes,'stationsYZHalfWidthX':path,'referenceScope':'July head only; broad formed brow shapes the optic opening. Hidden fastening and the fixed brow/opening crown boundary are reconstructed.','preservation':{'other697MeshesExact':True,'51PivotsAnd462GuideCurvesExact':True,'materialsExact':True,'saveReloadExact':True},'limits':['No new fasteners or era-specific materials added.','No clearance, export, browser or artistic acceptance yet.']}
 (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 renderer=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders'];renderer.__globals__['AUDIT']=AUDIT
 receipt['views']=renderer(BASE,'before')+renderer(native,'after');(AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(art(native)))
if __name__=='__main__':main()
