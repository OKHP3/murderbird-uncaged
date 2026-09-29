"""V28 short oblique rigid cervical guards, a coarse whole-form proposal.

Native metres/Z-up/-Y-front. The four original load links are retained, but
long parallel guards are reconstructed as staggered fitted plates. These
coordinates are editable authoring conventions, not dimensions from images.
"""
from pathlib import Path
import bpy,bmesh,math,json,runpy
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
PROFILE=((.78,-.165,.125,.170),(.87,-.247,.139,.210),(.99,-.365,.128,.252),
 (1.12,-.425,.095,.280),(1.245,-.417,.038,.258),(1.335,-.382,-.035,.205),
 (1.410,-.352,-.106,.145),(1.48,-.379,-.160,.116),
 (1.555,-.428,-.213,.109),(1.635,-.446,-.256,.100))
OWNERS=('neck','cervical-mid-a','cervical-mid-b','cervical-upper')
SPANS=((1.430,1.347),(1.500,1.422),(1.570,1.492),(1.644,1.562))
BOUNDARIES=((-1.22,-.74,-.26,.25,.73,1.22),
 (-1.22,-.91,-.40,.14,.67,1.22),
 (-1.22,-.65,-.09,.44,.88,1.22),
 (-1.22,-.87,-.33,.20,.75,1.22))

def properties(o):return json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x))
def node(o):return(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),properties(o))
def snap(o):return(node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials))
def apply(envelope_helper=None):
 lib=runpy.run_path(str(envelope_helper or ROOT/'scripts/regions/whole-character-v21-envelope.py'))
 for name in ('sample','envelope_point'):lib[name].__globals__['PROFILE']=PROFILE
 point=lib['envelope_point'];sample=lib['sample'];names=[f'V23 cervical {i+1} directional guard {k+1}' for i in range(4) for k in range(10)]
 material=bpy.data.objects[names[0]].data.materials[0]
 nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 outside={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
 for n in names:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
 result=[]
 for i,(owner,(top,bottom)) in enumerate(zip(OWNERS,SPANS)):
  fronts=list(zip(BOUNDARIES[i],BOUNDARIES[i][1:]));sectors=fronts+[(1.245,1.82),(1.84,2.45),(-2.45,-1.84),(-1.82,-1.245),(2.47,math.tau-2.47)]
  off=.003+i*.007
  for k,(a,b) in enumerate(sectors):
   n=names[i*10+k];verts=[];faces=[];rows=20;cols=18;center=(a+b)/2
   shear=(.10 if i%2 else -.10)*(1 if center<math.pi else -1)
   for row in range(rows+1):
    t=row/rows;s=t*t*(3-2*t)
    for column in range(cols+1):
     u=column/cols;su=2*u-1
     # Oblique seams are staggered between units; individual free edges vary
     # around the bend. No continuous ring or metal spanning two owners.
     z=top+(bottom-top)*t-.008*su*math.sin(center+.45)-.007*(1-su*su)**2*s
     f,r,w=[sample(z,c) for c in (1,2,3)];ry=(r-f)/2
     inset=.0013/max(.035,math.hypot((w+off)*math.cos(center),(ry+off)*math.sin(center)))
     angle=(a+inset)+(b-a-2*inset)*u+shear*(s-.5)
     verts.append(tuple(point(z,angle,off)))
   for row in range(rows):
    for column in range(cols):
     j=row*(cols+1)+column;faces.append((j,j+cols+1,j+cols+2,j+1))
   mesh=bpy.data.meshes.new(n+' V28 oblique guard mesh');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material)
   o=bpy.data.objects.new(n,mesh);bpy.context.scene.collection.objects.link(o);o.parent=bpy.data.objects[owner];o.matrix_parent_inverse=o.parent.matrix_world.inverted()
   bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
   if mesh.polygons[(rows//2)*cols+cols//2].normal.dot(Vector((math.sin(center),-math.cos(center),0)))<0:
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
   for f in mesh.polygons:f.use_smooth=True
   q=o.modifiers.new('Rigid finite oblique guard wall','SOLIDIFY');q.thickness=.0035;q.offset=-1;q.use_even_offset=False
   q=o.modifiers.new('Formed terminal edge','BEVEL');q.width=.0006;q.segments=2
   o['region']='neck';o['surfaceRole']='plate';o['constructionClass']='inherited-passive';o['exteriorEras']='maker,mechanic,builder';o['proposal']=True
   o['authoringRole']='Short oblique fitted cervical plate, rigid on one existing load segment; explicit joint seam'
   o['geometryStatus']='V28 coarse neck construction; movement and appearance acceptance pending'
   result.append({'name':n,'owner':owner,'top':top,'bottom':bottom,'radialOffset':off,'sector':[a,b],'shear':shear})
 bpy.context.view_layer.update()
 assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'}
 assert outside=={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
 return {'region':'neck guard reconstruction','status':'Single coarse oblique plate proposal; not accepted',
  'changedMeshes':names,'added':[],'removed':[],'plates':result,'preservedNodes':len(nodes),'protectedOutsideMeshes':len(outside),
  'reference':'Owner whole-bird and common master control S outline and directional overlapping guards; July head only',
  'attachment':'One existing rigid load-segment owner per plate; internal links and actual named joints unchanged',
  'eraEligibility':'All new guard shapes are passive inherited plates. No new actuation or sensing.',
  'limits':['Relative authoring coordinates, not perspective-derived measurements.','Joint gaps and interference require evaluated pose screening.','No guide or flexible metal deformation was added.']}
