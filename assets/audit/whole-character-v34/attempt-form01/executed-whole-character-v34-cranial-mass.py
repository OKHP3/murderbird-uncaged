"""V34 posterior/upper cranial mass proposal; native metres, rigid owners.

The owner whole-bird controls head/body relationship; July controls head only.
This smooth editable envelope grows skull behind and above the unchanged eye.
It does not scale the bill, eye, mandible, journals, throat or runtime nodes.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[2]))
AFT_GROWTH=.075
UPPER_GROWTH=.045
LATERAL_GROWTH=.12

def ease(t):
 t=max(0.,min(1.,t));return t*t*(3.-2.*t)
def map_point(p,origin):
 q=p-origin
 aft=ease((q.y+.200)/.270)
 height=ease((q.z-.180)/.120)
 upper=ease((q.z-.240)/.130)*ease((q.y+.320)/.200)
 return origin+Vector((q.x*(1.+LATERAL_GROWTH*aft*height),q.y+AFT_GROWTH*aft*height,q.z+UPPER_GROWTH*upper))

def apply():
 bpy.context.view_layer.update()
 h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'))
 origin=bpy.data.objects['head'].matrix_world.translation.copy()
 assert abs(origin.y+.322600007)<1e-5,'Unexpected head attachment contract'
 assert all(n in bpy.data.objects for n in ('V33 swept cranial leaf 0 3','V31 optic recessed receiving cup 1','V31 jaw fixed annular journal 1'))
 prefixes=('V33 swept cranial leaf ','V33 swept temporal leaf ','V31 fixed temporal receiving wall ','V31 frontal cranial cap receiving seat')
 selected=[o for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith(prefixes) or o.name.startswith('V33 diagonal brow receiver ') and o.name.endswith((' 0',' 1')))]
 # These passive fittings remain rigidly circular; their root and bearing
 # translate together to the mapped temporal wall, rather than deforming.
 rigid=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('V31 passive temporal fitting ','V31 temporal fitting root '))]
 names={o.name for o in selected+rigid};assert len(selected)==50 and len(rigid)==12,(len(selected),len(rigid))
 protected={o.name:h['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
 nodes={o.name:h['node'](o) for o in bpy.data.objects if o.type=='EMPTY'}
 old={o.name:h['snap'](o) for o in selected+rigid};bounds=[]
 rigid_deltas={}
 for fitting in rigid:
  if not fitting.name.startswith('V31 passive temporal fitting '):continue
  fp=[fitting.matrix_world@v.co for v in fitting.data.vertices];c=sum(fp,Vector())/len(fp)
  rigid_deltas[fitting.name]=map_point(c,origin)-c
 for o in selected+rigid:
  assert o.parent.name in ('head','cranial-cover'),o.name
  world=o.matrix_world.copy();inv=world.inverted();points=[world@v.co for v in o.data.vertices]
  if o in rigid:
   # Paired fitting root and bearing share a target based on the bearing
   # centre so their finite attachment translation stays identical.
   fitting_name=o.name.replace('V31 temporal fitting root ','V31 passive temporal fitting ')
   delta=rigid_deltas[fitting_name]
   mapped=[p+delta for p in points]
  else:mapped=[map_point(p,origin) for p in points]
  for v,p in zip(o.data.vertices,mapped):v.co=inv@p
  o.data.update()
  bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);bm.free()
  assert closed and vol>0 and all(math.isfinite(c) for v in o.data.vertices for c in v.co),o.name
  bounds.append({'name':o.name,'owner':o.parent.name,'before':[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]],'after':[[min(p[k] for p in mapped) for k in range(3)],[max(p[k] for p in mapped) for k in range(3)]],'closedRawSolid':closed,'positiveRawVolumeM3':vol,'method':'rigid fitting translation' if o in rigid else 'shared smooth cranial envelope'})
 # Rebuild the fixed temporal top as a finite receiving underlap using
 # the same actual skull section family as the cap. Old side edge ends
 # near theta .91; the expanded cap slot needs a wall reaching 1.24rad.
 # Only the upper return recesses 6mm radially, so the wall load path and
 # lower temporal field stay substantial while the cap stays independent.
 for side in (-1,1):
  wall=bpy.data.objects[f'V31 fixed temporal receiving wall {side}']
  def fn(u,v):
   width=(.95+.05*h['smooth'](u/.25))*(1-.13*h['smooth']((u-.45)/.55))
   theta=.40+(v-.5)*1.68*width
   y=-.240+.363*u+.007*math.sin(math.pi*v)**2*u
   z,rx,rz=h['section'](y)
   off=-.004-.006*h['smooth']((theta-.73)/.35)
   point=origin+Vector((side*(rx+off)*math.cos(theta),y,z+(rz+off)*math.sin(theta)))
   return map_point(point,origin)-origin
  verts,faces=h['finite_sheet'](fn,nu=40,nv=24,wall=.004,side=side)
  inv=wall.matrix_world.inverted();wall.data.clear_geometry();wall.data.from_pydata([inv@(origin+v) for v in verts],[],faces);wall.data.update()
  bm=bmesh.new();bm.from_mesh(wall.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wall.data);bm.free()
  # Preserve the actual eye bay, centred on the unchanged cup. The finite
 # bore is functional receiver topology, not a dark painted aperture.
  vv,ff=h['cylinder'](side,-.220,.260,.080,.230,.061,count=96)
  data=bpy.data.meshes.new('V34 temporary eye bore');data.from_pydata([origin+v for v in vv],[],ff);data.update()
  cutter=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(cutter)
  bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free();bpy.context.view_layer.update()
  modifier=wall.modifiers.new('V34 finite optic bay receiving bore','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
  bpy.ops.object.select_all(action='DESELECT');wall.select_set(True);bpy.context.view_layer.objects.active=wall;bpy.ops.object.modifier_apply(modifier=modifier.name);wall.select_set(False)
  bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(data)
  bm=bmesh.new();bm.from_mesh(wall.data);assert all(e.is_manifold for e in bm.edges),wall.name;vol=bm.calc_volume(signed=True);assert vol>0;bm.free()
  for p in wall.data.polygons:p.use_smooth=False
  points=[wall.matrix_world@v.co for v in wall.data.vertices]
  record=next(x for x in bounds if x['name']==wall.name);record['after']=[[min(p[k] for p in points) for k in range(3)],[max(p[k] for p in points) for k in range(3)]];record['positiveRawVolumeM3']=vol;record['method']='Shared cranial envelope with finite top receiving return to1.24rad,6mm recessed top,4mm normal wall and unchanged61mm eye bore'
 bpy.context.view_layer.update()
 assert all(h['node'](bpy.data.objects[n])==r for n,r in nodes.items())
 assert all(h['snap'](bpy.data.objects[n])==r for n,r in protected.items())
 changed=[o.name for o in selected+rigid if h['snap'](o)!=old[o.name]]
 return {'region':'cranial-mass','status':'Coarse visual proposal; not likeness or movement acceptance','changedMeshes':changed,'changedNodes':[],'added':[],'removed':[],'protectedMeshesExact':len(protected),'runtimeNodesExact':len(nodes),'materialsChanged':False,'transformContract':{'anchor':'retained head attachment','nativeAxes':'X lateral, Y aft, Z up','aftGrowthMaxM':AFT_GROWTH,'upperGrowthMaxM':UPPER_GROWTH,'lateralGrowthMaxFraction':LATERAL_GROWTH,'lowerFadeZLocalM':[.180,.300],'upperFadeZLocalM':[.240,.370],'eyeBillJawAndThroat':'unchanged'},'meshBounds':bounds,'limits':['Crown opening and new receiving lap gaps require combined movement review.','Aft skin/fitting attachment remains a proposed seat; no engineering or artistic acceptance.']}
