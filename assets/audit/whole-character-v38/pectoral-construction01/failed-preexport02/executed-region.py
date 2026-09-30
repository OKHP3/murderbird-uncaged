"""Pectoral-construction01: reconstructed upper panels and connected backing.
Native Z-up, negativeY anterior. Original compact-mantle02 input; no plate warp.
"""
from pathlib import Path
import bpy,bmesh,math,runpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
NAMES=[f'V34 formed breast course {r} plate {i}'for r,n in [(1,5),(2,6)]for i in range(1,n+1)]
LINER='V30 continuous tapered breast liner'
PROFILE=[(1.075,.281,-.408),(1.13,.282,-.410),(1.19,.269,-.394),(1.25,.240,-.357),(1.32,.191,-.294)]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def section(z):
 for i,(a,b)in enumerate(zip(PROFILE,PROFILE[1:])):
  if a[0]<=z<=b[0]:
   u=(z-a[0])/(b[0]-a[0]);h=b[0]-a[0];v=[]
   for k in [1,2]:
    d=(b[k]-a[k])/h;m0=d if i==0 else(b[k]-PROFILE[i-1][k])/(b[0]-PROFILE[i-1][0]);m1=d if i+2==len(PROFILE)else(PROFILE[i+2][k]-a[k])/(PROFILE[i+2][0]-a[0]);v.append((2*u**3-3*u*u+1)*a[k]+(u**3-2*u*u+u)*h*m0+(-2*u**3+3*u*u)*b[k]+(u**3-u*u)*h*m1)
   return v
 return PROFILE[0][1:] if z<PROFILE[0][0]else PROFILE[-1][1:]
def point(z,a):
 rx,y=section(z);return Vector((rx*math.sin(a),y*math.cos(a),z))
def meshworld(o):return [o.matrix_world@v.co for v in o.data.vertices],[tuple(f.vertices)for f in o.data.polygons]
def bvh(o):
 e=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=e.to_mesh();m.calc_loop_triangles();tree=BVHTree.FromPolygons([e.matrix_world@v.co for v in m.vertices],[tuple(f.vertices)for f in m.loop_triangles],all_triangles=True);e.to_mesh_clear();return tree

def install(o,v,f):
 old=o.data;mesh=bpy.data.meshes.new(o.name+' reconstructed finite wall');inv=o.matrix_world.inverted();mesh.from_pydata([inv@p for p in v],[],f);mesh.update()
 for m in old.materials:mesh.materials.append(m)
 bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(mesh);bm.free();mesh.update();o.data=mesh
 for p in mesh.polygons:p.use_smooth=True
 o['v38PectoralConstruction']='New curved finite panel/backing reconstruction; inherited passive cover; fit/likeness proposal'

def cut(o,tool,operation='DIFFERENCE'):
 q=o.modifiers.new('Finite reconstructed receiving interface', 'BOOLEAN');q.operation=operation;q.solver='EXACT';q.object=tool
 with bpy.context.temp_override(object=o,active_object=o,selected_objects=[o],selected_editable_objects=[o]):bpy.ops.object.modifier_apply(modifier=q.name)
 assert len(o.data.polygons)>0,o.name

def apply():
 bpy.context.view_layer.update();h=runpy.run_path(str(ROOT/'scripts/regions/whole-character-v30-breast-form.py'));sheet=h['solid_sheet'];records=[];liner=bpy.data.objects[LINER];source=bvh(liner);sourceV,sourceF=meshworld(liner)
 # Preserve lower backing geometry below the actual Z1.11 seam plane, then
 # join a new formed upper backing through a finite15mm receiving overlap.
 bm=bmesh.new();bm.from_mesh(liner.data);inv=liner.matrix_world.inverted();plane=inv@Vector((0,0,1.11));normal=(liner.matrix_world.to_3x3().transposed()@Vector((0,0,1))).normalized();result=bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=plane,plane_no=normal,clear_outer=True,clear_inner=False);edges=[e for e in result['geom_cut']if isinstance(e,bmesh.types.BMEdge)and e.is_boundary]
 if edges:bmesh.ops.holes_fill(bm,edges=edges,sides=0)
 mesh=bpy.data.meshes.new('Pectoral retained lower backing seam');bm.to_mesh(mesh);bm.free()
 for m in liner.data.materials:mesh.materials.append(m)
 liner.data=mesh
 def back(u,v):
  z=1.32-(1.32-1.095)*u;a=(2*v-1)*.91;p=point(z,a)
  if z<1.125:
   target=source.find_nearest(p)[0];w=ease((1.125-z)/.030);p.y=p.y+(target.y-p.y)*w
  return p
 v,f=sheet(back,44,40,.005);tmp=bpy.data.objects.new('temporary new upper backing union',bpy.data.meshes.new('finite new upper backing'));bpy.context.scene.collection.objects.link(tmp);tmp.data.from_pydata(v,[],f);tmp.data.update();bpy.context.view_layer.update();cut(liner,tmp,'UNION');bpy.data.objects.remove(tmp,do_unlink=True);liner['v38PectoralConstruction']='Retained lower backing plus Boolean-unioned5mm formed upper liner; finite15mm seam overlap proposal'
 seams={'sourceCutWorldZM':1.11,'newBackingBottomNominalZM':1.095,'nominalLongitudinalLapM':.015,'method':'Actual finite Boolean UNION of retained lower backing and new5mm curved upper sheet; Bottom-grid Y ordinates follow actual source backing nearest surfaces; X/Z construction grid held to avoid collapsed folded projection.','limits':'Boolean union/closed edge topology does not prove all interface weld quality or constant stock.'}
 for r,n,top,bottom in [(1,5,1.32,1.155),(2,6,1.18,1.045)]:
  for c in range(1,n+1):
   name=f'V34 formed breast course {r} plate {c}';o=bpy.data.objects[name];center=-1+(c-.5)*2/n;step=2/n
   def fn(u,v):
    t=2*v-1;z=top+(bottom-top)*u+.014*(1 if center>0 else -1 if center<0 else 0)*t*ease(u)-.008*(1-t*t)*ease(u);a=(center+.5*step*.985*t)*(1-.11*ease(u))*.90
    p=point(z,a)
    if z<1.10:
     q=source.find_nearest(p)[0];p=p.lerp(q,ease((1.10-z)/.055))
    radial=Vector((math.sin(a),-math.cos(a),0));return p+radial*(.009+.014*ease(u))
   v,f=sheet(fn,30,20,.0035);install(o,v,f);o['wallM']=.0035;o['geometryStatus']='Pectoral-construction01 replacement; passive rigid breast-cover plate; reconstruction'
 # Receiving windows follow actual protected finite root neck guard solids
 # at declared retained-chain samples, never guessed throat planes.
 chain=['neck','cervical-mid-a'];rest={n:bpy.data.objects[n].matrix_world.copy()for n in chain};reliefs=[]
 from mathutils import Matrix
 for pitch,yaw in [(0,0),(-.14,-.45),(.08,.288),(.65,0),(-.07,0),(0,-.45),(0,.45)]:
  transforms={chain[0]:rest[chain[0]]@Matrix.Rotation(pitch*.25,4,'X')@Matrix.Rotation(yaw,4,'Z')};transforms[chain[1]]=transforms[chain[0]]@(rest[chain[0]].inverted()@rest[chain[1]])@Matrix.Rotation(pitch*.25,4,'X')
  for guard in [o for o in bpy.data.objects if o.type=='MESH'and o.parent and o.parent.name in chain and o.name.startswith('V23 cervical ' )]:
   change=transforms[guard.parent.name]@rest[guard.parent.name].inverted();normal=guard.matrix_world.to_3x3().inverted().transposed();gv=[change@(guard.matrix_world@q.co+.003*(normal@q.normal).normalized())for q in guard.data.vertices];lo=[min(p[k]for p in gv)for k in range(3)];hi=[max(p[k]for p in gv)for k in range(3)];targets=[]
   for name in NAMES+[LINER]:
    pts,_=meshworld(bpy.data.objects[name])
    if not any(max(p[k]for p in pts)<lo[k]or min(p[k]for p in pts)>hi[k]for k in range(3)):targets.append(name)
   if not targets:continue
   m=bpy.data.meshes.new('actual cervical finite receiving tool');m.from_pydata(gv,[],[tuple(f.vertices)for f in guard.data.polygons]);m.update();tool=bpy.data.objects.new(m.name,m);bpy.context.scene.collection.objects.link(tool);bpy.context.view_layer.update()
   for name in targets:cut(bpy.data.objects[name],tool)
   bpy.data.objects.remove(tool,do_unlink=True);reliefs.append({'guard':guard.name,'pitchYaw':[pitch,yaw],'targets':targets,'nominalVertexNormalToolExpansionM':.003})
 for name in NAMES+[LINER]:
  o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);closed=all(e.is_manifold for e in bm.edges);volume=abs(bm.calc_volume(signed=True));bm.free();records.append({'name':name,'owner':o.parent.name,'surfaceRole':o.get('surfaceRole'),'constructionClass':o.get('constructionClass'),'eras':o.get('exteriorEras'),'materials':[m.name for m in o.data.materials],'closedEdgeManifold':closed,'positiveVolumeM3':volume,'wallM':o.get('wallM'),'vertices':len(o.data.vertices),'stockScope':'New3.5mm formed plates and5mm upperbacking. Actual Boolean receiving trims may alter local wall; not universal engineering validation.'});assert volume>0,name
 return {'changedMeshes':NAMES+[LINER],'addedMeshes':[],'removedMeshes':[],'changedNodes':[],'attachmentAndEraMap':records,'upperBackingSeam':seams,'guardReceivingReliefs':reliefs,'authoredProfile':PROFILE,'supportCoherence':'Upper finite backing joined to retained lower cover backing; original tabs/returns/shaft/hinge exact. All on independent breastplate owner; fixed load frame exact. Existing16.25mm fixed receiving gap WARN remains.','rigidVsFlexible':'Rigid finite cover/backing only; no tissue or powered addition.','confirmed':'Master03/Maker-clean carry deep breast into curved neck/shoulder with shaped overlapping armor.','reconstruction':'New panel topology/profile/hidden lap are authored geometry proposals; not art metrology.','limits':['Actual7sample receiving tools expanded along vertex normals: not constant-normal gap or continuous motion proof.','Fresh rest/open screen required; positivevolume and closure alone do not prove fit or support weld.']}
