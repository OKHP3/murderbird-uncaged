"""Actual cup+bowl union in rest/jaw.16/.32/.10, source head-fit01; finite ray/cross-sections, no edits."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
model,out=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not out.exists();bpy.ops.wm.open_mainfile(filepath=str(model));jaw=bpy.data.objects['jaw'];rest=jaw.matrix_basis.copy();items=[]
for angle in [0,.10,.16,.32]:
 jaw.matrix_basis=rest@Matrix.Rotation(angle,4,'X');bpy.context.view_layer.update()
 for name in ['V32 formed mandibular bowl']+[f'{prefix} {side}'for prefix in ['V31 optic recessed receiving cup','V31 passive optic cavity floor','V33 recessed optic retaining lip','V31 Advanced optical aperture']for side in[-1,1]]:
  o=bpy.data.objects[name];o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices];t=[tuple(q.vertices)for q in o.data.loop_triangles];items.append((name,angle,p,t,BVHTree.FromPolygons(p,t,all_triangles=True)))
jaw.matrix_basis=rest;bpy.context.view_layer.update();rows=[]
for side in [-1,1]:
 shield=bpy.data.objects[f'V38 optic cheek shield {side} 0'];n=len(shield.data.vertices)//2;p=[shield.matrix_world@v.co for v in shield.data.vertices[:n]]
 for q in p:
  hits=[]
  for name,angle,points,tris,tree in items:
   hit=tree.ray_cast(Vector((side*.4,q.y,q.z)),Vector((-side,0,0)))
   if hit[0]is not None:hits.append({'name':name,'jaw':angle,'x':abs(hit[0].x),'point':list(hit[0]),'normal':list(hit[1])})
  if hits:rows.append({'side':side,'sourceOuter':list(q),'sourceInnerX':abs(q.x)-.0045,'unionOuterX':max(v['x']for v in hits),'requiredOutwardShiftFor1point5mmGap':max(0,max(v['x']for v in hits)+.0015-(abs(q.x)-.0045)),'hits':hits})
# Actual unchanged wall and passive cranial load-bow interface bounds.
receivers=[]
for name in ['V31 fixed temporal receiving wall -1','V31 fixed temporal receiving wall 1','V31 passive cranial load bow -1','V31 passive cranial load bow 1']:
 o=bpy.data.objects[name];p=[o.matrix_world@v.co for v in o.data.vertices];receivers.append({'name':name,'bounds':[[min(v[k]for v in p),max(v[k]for v in p)]for k in range(3)]})
out.write_text(json.dumps({'sourceSha256':hashlib.sha256(model.read_bytes()).hexdigest(),'hardwareUnionAnglesRadians':[0,.10,.16,.32],'samples':rows,'receivingBounds':receivers,'limits':'Exact finite triangle rays at all source outer vertices. Not proof that intervening candidate triangles or footprint fit; final strict union83 screen required.'},indent=2)+'\n');print('UNION',len(rows),'MAX_REQUIRED',max(v['requiredOutwardShiftFor1point5mmGap']for v in rows));print('RECEIVERS',receivers)
