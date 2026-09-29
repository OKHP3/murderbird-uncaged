"""V34 region-specific short formed breast plate hierarchy.

Owner whole-bird/Candidate03 guide the directional chest construction.
The V30 profile is calibrated to the actual retained body drop; its old six
skin solids supply a ray-derived receiving footprint. Liner/frame stay exact.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(globals().get('SOURCE_ROOT',Path(__file__).resolve().parents[2]))
OLD=('V30 long central sternal keel','V30 long oblique breast cheek -1','V30 long oblique breast cheek 1','V30 lower tapered sternal overlap -1','V30 lower tapered sternal overlap 1','V30 upper sternal receiving crown')
# Actual world Z, top/bottom/count. These are authored construction controls,
# not measurements recovered from the perspective reference.
ROWS=((1.249,1.154,5),(1.174,1.060,6),(1.082,.964,7),(.988,.870,6),(.890,.782,5),(.805,.706,4))
WALL=.003

def apply():
 bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));s=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v31-head-reconstruction.py'))
 assert all(n in bpy.data.objects for n in OLD);assert abs(bpy.data.objects['breastplate'].matrix_world.translation.z-.6446173)<1e-5
 nodes={o.name:s['node'](o) for o in bpy.data.objects if o.type=='EMPTY'};protected={o.name:s['snap'](o) for o in bpy.data.objects if o.type=='MESH' and o.name not in OLD};old=[bpy.data.objects[n] for n in OLD];tags=dict(old[0].items());materials=list(old[0].data.materials);dg=bpy.context.evaluated_depsgraph_get();mask=[]
 # Continuous liner boundaries preserve true receiving windows while
 # bridging incidental seams between the six obsolete exterior panels.
 for o in old+[bpy.data.objects['V30 continuous tapered breast liner']]:
  e=o.evaluated_get(dg);m=e.to_mesh();m.calc_loop_triangles();mask.append(BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(t.vertices) for t in m.loop_triangles],all_triangles=True));e.to_mesh_clear()
 def footprint(z,a):
  theta=a*h['door_angle'](z+.120);base=h['point'](z+.120,theta,0)-Vector((0,0,.120));n=Vector((math.sin(theta),-math.cos(theta),0));start=base+.060*n
  return any(b.ray_cast(start,-n,.120)[0] is not None for b in mask)
 added=[];finite=[];clips=[]
 for row,(top,bottom,count) in enumerate(ROWS):
  step=2./count
  for col in range(count):
   center=-1+(col+.5)*step+(.035 if row in (1,3) else -.025 if row==2 else 0)
   # Sternum plates are short/broad; flank plates sweep toward the keel.
   # Height staggering avoids a circumferential breast belt/ring pattern.
   stagger=.009*(1 if col%2 else -1)*(abs(center)*.65+.35)
   aa=top+stagger;bb=bottom+.006*abs(center)
   def param(u,v):
    t=2*v-1
    z=aa+(bb-aa)*u+.022*(1 if center>.08 else -1 if center<-.08 else 0)*t*h['ease'](u)-.008*(1-t*t)*h['ease'](u)
    # Neighboring plates share their seam coordinate at actual row height.
    # Width follows the same convergence as centres, keeping a deliberate
    # butt gap instead of the former7% angular overlap at lower margins.
    rowu=max(0.,min(1.,(top-z)/(top-bottom)))
    sweep=1-.14*h['ease'](rowu)
    a=(center+.5*step*.965*t)*sweep
    return z,a
   def point(u,v):
    z,a=param(u,v);theta=a*h['door_angle'](z+.120)
    # The free margin stands over the next row's recessed root. Each row
    # resets the same envelope rather than adding cumulative radius.
    off=.010+.014*h['ease'](u)+.0015*math.sin(math.pi*u)*(1-(2*v-1)**2)
    return h['point'](z+.120,theta,off)-Vector((0,0,.120))
   R,C=18,12;uv=[(i/R,j/C) for i in range(R+1) for j in range(C+1)];vv=[point(u,v) for u,v in uv];valid=[footprint(*param(u,v)) for u,v in uv];faces=[];crossings={}
   def clip(a,b):
    key=tuple(sorted((a,b)))
    if key in crossings:return crossings[key]
    va,vb=uv[a],uv[b];lo,hi=0.,1.;state=valid[a]
    for _ in range(18):
     t=(lo+hi)/2;u=va[0]+(vb[0]-va[0])*t;v=va[1]+(vb[1]-va[1])*t
     if footprint(*param(u,v))==state:lo=t
     else:hi=t
    t=(lo+hi)/2;u=va[0]+(vb[0]-va[0])*t;v=va[1]+(vb[1]-va[1])*t;index=len(vv);vv.append(point(u,v));crossings[key]=index;return index
   for i in range(R):
    for j in range(C):
     a=i*(C+1)+j
     for tri in [(a,a+1,a+C+2),(a,a+C+2,a+C+1)]:
      f=[]
      for x,y in zip(tri,tri[1:]+tri[:1]):
       if valid[x]:f.append(x)
       if valid[x]!=valid[y]:f.append(clip(x,y))
      if len(f)>=3:faces.append(tuple(f))
   if not faces:continue
   used=sorted({i for f in faces for i in f});mapping={v:i for i,v in enumerate(used)};verts=[vv[i] for i in used];faces=[tuple(mapping[i] for i in f) for f in faces]
   name=f'V34 formed breast course {row+1} plate {col+1}';mesh=bpy.data.meshes.new(name+' finite surface');o=bpy.data.objects.new(name,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects['breastplate'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();inv=o.matrix_world.inverted();mesh.from_pydata([inv@v for v in verts],[],faces);mesh.update()
   for m in materials:mesh.materials.append(m)
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
   # Preserve outward source profile winding on every disconnected mask.
   for p in mesh.polygons:p.use_smooth=True
   q=o.modifiers.new('Finite3mm formed breast wall','SOLIDIFY');q.thickness=WALL;q.offset=-1;q.use_even_offset=False
   bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.modifier_apply(modifier=q.name);o.select_set(False)
   bm=bmesh.new();bm.from_mesh(mesh);assert all(e.is_manifold for e in bm.edges),name;volume=bm.calc_volume(signed=True)
   if volume<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces));volume=-volume
   assert volume>0,name;bm.to_mesh(mesh);bm.free();mesh.update()
   for k,v in tags.items():o[k]=v
   o['constructionOwner']='breastplate';o['surfaceRole']='plate';o['region']='breast';o['exteriorEras']='maker,mechanic,builder';o['constructionClass']='proposed-passive';o['wallM']=WALL;o['geometryStatus']='V34 breast hierarchy proposal; actual fit and likeness separate';o['constructionDescription']='Short broad formed directional breast plate; finite receiving footprint, nested free edge, staggered sternum/flank flow'
   added.append(name);finite.append({'name':name,'closed':True,'positiveVolumeM3':volume,'wallM':WALL});clips.append({'name':name,'actualOldFootprintClippedEdges':len(crossings),'worldZRootM':aa,'worldZFreeM':bb,'normalizedDoorCenter':center})
 # Local receiving relief from the five actual guard identities that
 # contacted trial01, using their true evaluated closed surfaces at the
 # seven runtime samples. Avoid a convex multi-pose hull spanning empty
 # throat space: that earlier diagnostic cut was visibly over-broad.
 chain=['neck','cervical-mid-a','cervical-mid-b','cervical-upper']
 rests={n:bpy.data.objects[n].matrix_world.copy() for n in chain}
 states=[(0,0),(-.14,-.45),(.08,.288),(.65,0),(-.07,0),(0,-.45),(0,.45)]
 guardnames=[f'V23 cervical 1 directional guard {i}' for i in (1,2,4,5)]+['V23 cervical 2 directional guard 3']
 reliefs=[];dg=bpy.context.evaluated_depsgraph_get()
 for name in guardnames:
  source=bpy.data.objects[name];ev=source.evaluated_get(dg);mm=ev.to_mesh();raw=[ev.matrix_world@v.co for v in mm.vertices];norm=ev.matrix_world.to_3x3().inverted().transposed();normals=[(norm@v.normal).normalized() for v in mm.vertices];faces=[tuple(f.vertices) for f in mm.polygons];ev.to_mesh_clear()
  for pitch,yaw in states:
   new={};new[chain[0]]=rests[chain[0]]@Matrix.Rotation(pitch*.25,4,'X')@Matrix.Rotation(yaw,4,'Z')
   new[chain[1]]=new[chain[0]]@(rests[chain[0]].inverted()@rests[chain[1]])@Matrix.Rotation(pitch*.25,4,'X')
   change=new[source.parent.name]@rests[source.parent.name].inverted();points=[change@(p+.003*n) for p,n in zip(raw,normals)]
   minimum=[min(p[k] for p in points) for k in range(3)];maximum=[max(p[k] for p in points) for k in range(3)];targets=[]
   for plate in added:
    o=bpy.data.objects[plate];vv=[o.matrix_world@v.co for v in o.data.vertices]
    if not any(max(p[k] for p in vv)<minimum[k] or min(p[k] for p in vv)>maximum[k] for k in range(3)):targets.append(plate)
   if not targets:continue
   cm=bpy.data.meshes.new('V34 actual finite guard lip receiving tool');cm.from_pydata(points,[],faces);cm.update();cutter=bpy.data.objects.new(cm.name,cm);bpy.context.scene.collection.objects.link(cutter);bpy.context.view_layer.update();edited=[]
   for plate in targets:
    o=bpy.data.objects[plate];modifier=o.modifiers.new('Local finite guard receiving relief','BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=modifier.name)
    assert len(o.data.polygons)>0,plate;edited.append(plate)
   bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.meshes.remove(cm)
   reliefs.append({'retainedGuard':name,'receivingPlates':edited,'totalPitchRootYaw':[pitch,yaw],'vertexNormalToolExpansionM':.003,'method':'Actual finite closed guard surface at discrete pose, expanded along actual vertex normals; local breast receiving relief. No empty-space convex hull or hidden part.','limit':'Nominal3mm tool expansion, not a guaranteed constant-normal or continuous gap.'})
 # Revalidate actual receiving topology, not the pre-cut construction.
 finite=[]
 for name in added:
  o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges),name;vol=bm.calc_volume(signed=True);assert vol>0,name;bm.free();finite.append({'name':name,'closed':True,'positiveVolumeM3':vol,'wallM':WALL})
 for o in old:bpy.data.objects.remove(o,do_unlink=True)
 bpy.context.view_layer.update();assert all(s['node'](bpy.data.objects[n])==v for n,v in nodes.items());assert all(s['snap'](bpy.data.objects[n])==v for n,v in protected.items())
 return {'region':'breast-panel-hierarchy','status':'New structural exterior proposal; artistic and moving-fit acceptance pending','changedMeshes':[],'removed':list(OLD),'added':added,'changedNodes':[],'outsideMeshesExact':len(protected),'nodesExact':len(nodes),'materialsChanged':False,'rowsWorldZ':ROWS,'construction':'Six short staggered courses, broad sternum and inward-swept flank plates with3mm finite walls,noncumulative10–24mm radial envelope and12–20mm longitudinal laps. Actual old skins mask receiving windows; retained liner/hinge/frame exact.','footprintMethod':'Native radial ray into actual retained continuous liner plus six original skin footprints (hardware windows; liner bridges obsolete skin seams), then parameter triangle boundary clipping; old profile calibrated+120mm for evaluation and−120mm world placement.','finiteSolids':finite,'plates':clips,'receivingReliefs':reliefs,'limits':['Mask is sampled/refined per source triangle; exact neighboring clearance requires fresh posed screen.','No physics, continuous clearance, finished material or owner likeness acceptance.']}
