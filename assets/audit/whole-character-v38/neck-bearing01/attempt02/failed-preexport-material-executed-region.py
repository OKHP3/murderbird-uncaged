"""Bounded first neck-bearing01: rigid short lower lames and finite race-root routes."""
import bpy,bmesh,math,json
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[2]
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def components(m):
 links=[set()for _ in m.vertices]
 for e in m.edges:a,b=e.vertices;links[a].add(b);links[b].add(a)
 u=set(range(len(links)));s=[]
 while u:
  q=[u.pop()];n=0
  while q:
   a=q.pop();n+=1
   for b in links[a]&u:u.remove(b);q.append(b)
  s.append(n)
 return sorted(s,reverse=True)
def stock(o):
 bm=bmesh.new();bm.from_mesh(o.data);r={'components':components(o.data),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'signedVolumeM3':bm.calc_volume(signed=True)};bm.free();return r
def annotate(o,description):
 o['neckBearingHistory']=json.dumps({k:json.loads(json.dumps(v,default=lambda x:list(x)))for k,v in o.items()if k in ['constructionDescription','authoringRole','geometryStatus'] or k.endswith('Revision')},separators=(',',':'));o['constructionDescription']=description;o['geometryStatus']='neck-bearing01 proposed passive rigid assembly; finite support/motion and owner acceptance unresolved';o['neckBearingRevision']='neck-bearing01'
def install(o,v,f):
 old=o.data;m=bpy.data.meshes.new(o.name+' neck bearing stock');m.from_pydata([o.matrix_world.inverted()@p for p in v],[],f);m.update()
 for a in old.materials:m.materials.append(a)
 bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();o.data=m
 for p in m.polygons:p.use_smooth=True

def intersection_volume(a,b):
 # Temporary evaluated Boolean proves finite shared stock volume, not weld/fastener validity.
 m=a.data.copy();temp=bpy.data.objects.new('temporary seat-volume diagnosis',m);bpy.context.scene.collection.objects.link(temp);temp.matrix_world=a.matrix_world.copy();bpy.context.view_layer.update();mod=temp.modifiers.new('finite seat intersection','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=b
 dg=bpy.context.evaluated_depsgraph_get();ev=temp.evaluated_get(dg);q=ev.to_mesh();bm=bmesh.new();bm.from_mesh(q);volume=abs(bm.calc_volume(signed=True));count=len(q.vertices);bm.free();ev.to_mesh_clear();bpy.data.objects.remove(temp,do_unlink=True);bpy.data.meshes.remove(m);return {'intersectionVolumeM3':volume,'intersectionVertices':count,'qualification':'Actual finite common stock volume at intended rigid seat, not continuous welded route/fastener/load proof.'}
def apply():
 bpy.context.view_layer.update();changed=[];restored=[];records=[];axis=bpy.data.objects['head'].matrix_world.translation.copy()
 # Read exact source stock without changing the candidate scene/owners.
 source=ROOT/'assets/models/whole-character-v38/torso-support01/murderbird-v38-torso-support01.blend'
 names=[f'V23 cervical {r} directional guard {g}'for r in(1,2)for g in range(1,6)]
 originalObjects=set(bpy.data.objects)
 with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=names
 loaded=list(b.objects)
 for sourceObject in loaded:
  name=sourceObject.name.split('.00')[0];o=bpy.data.objects[name];o.data=sourceObject.data.copy()
  for k in list(o.keys()):del o[k]
  for k,v in sourceObject.items():o[k]=v
  bpy.data.objects.remove(sourceObject,do_unlink=True);changed.append(name);restored.append(name)
 for imported in list(set(bpy.data.objects)-originalObjects):bpy.data.objects.remove(imported,do_unlink=True)
 # Preserve original upper leaf coverage, append physically connected 2.5mm
 # recessed lower return stock at existing free edge. Newly authored sector
 # sweeps around the real head centre only; whole skins are not projected.
 for side in(-1,0,1):
  for col in range(3):
   name=f'V33 tapered throat cheek plate {side} 0 {col}';o=bpy.data.objects[name];old=[o.matrix_world@v.co for v in o.data.vertices];faces=[tuple(p.vertices)for p in o.data.polygons];rows=25;cols=19;half=475
   edgeO=[24*cols+c for c in range(cols)];edgeI=[half+i for i in edgeO]
   # Remove only actual old lower thickness cap, joining shared old edge.
   capset=set(edgeO+edgeI);faces=[f for f in faces if not set(f)<=capset];v=old.copy();loopsO=[edgeO];loopsI=[edgeI];levels=12
   for level in range(1,levels+1):
    t=level/levels;lo=[];li=[]
    for c,i in enumerate(edgeO):
     p=old[i];d=p-axis;phi=math.atan2(d.x,-d.y);lat=math.atan2(d.z,math.hypot(d.x,d.y));front=max(.15,math.cos(phi));endlat=-.62*front-.15*(1-front);newlat=lat*(1-t)+endlat*t
     radius=d.length*(1-ease(t/.25))+.154*ease(t/.25);radial=Vector((math.sin(phi)*math.cos(newlat),-math.cos(phi)*math.cos(newlat),math.sin(newlat)))
     lo.append(len(v));v.append(axis+radial*radius);li.append(len(v));v.append(axis+radial*(radius-.0025))
    loopsO.append(lo);loopsI.append(li)
   for k in range(levels):
    a,b=loopsO[k],loopsO[k+1];c,d=loopsI[k],loopsI[k+1]
    for j in range(cols-1):faces.append((a[j],a[j+1],b[j+1],b[j]));faces.append((c[j],d[j],d[j+1],c[j+1]))
    faces.append((a[0],b[0],d[0],c[0]));faces.append((a[-1],c[-1],d[-1],b[-1]))
   a,b=loopsO[-1],loopsI[-1]
   for j in range(cols-1):faces.append((a[j],a[j+1],b[j+1],b[j]))
   install(o,v,faces);annotate(o,'Final neck-bearing01 second: original full head lower-leaf outer coverage retained; physically connected recessed 2.5mm free underlap appended from its original lower-edge stock around actual head captive-shaft centre. Independent rigid head owner, no new owner or joint bridge. Intended nested sliding receiving fit requires finite poses; no artistic/engineering approval.')
   changed.append(name);records.append({'name':name,'owner':o.parent.name,'originalOuterVertices475ExactWithinFloatTransform':True,'originalLowerCapReplacedBySharedEdgeExtension':True,'originalSharedRootIndices':edgeO,'newUnderlapVertexCount':len(v)-len(old),'radialOuterTargetM':.154,'wallM':.0025,'authoredParameterRows':levels,'parameterGridNotTextureUV':True,'actualShaftCenterWorld':list(axis),'tipLatitudeFrontRadians':-.62,'sideRearExtensionGraduated':True,'stock':stock(o),'limits':'Root stock integral topology; seated support and collision/sweep validity remain unproven. Original head fan remains source exact.'})
 for g in range(1,6):
  o=bpy.data.objects[f'V23 cervical 4 directional guard {g}'];old=[v.co.copy()for v in o.data.vertices];world=[o.matrix_world@p for p in old];o.data=o.data.copy();inv=o.matrix_world.inverted();deltas=[]
  # Only internal receiving edge rows0–8 form the concentric recess; complete
  # original outer skin is exact. This intentionally thickens local stock.
  for row in range(9):
   w=1-ease(row/8)
   for c in range(19):
    i=475+row*19+c;p=world[i];d=p-axis;target=axis+d.normalized()*.164;q=p.lerp(target,w);o.data.vertices[i].co=inv@q;deltas.append((q-p).length)
  o.data.update();assert all(o.data.vertices[i].co==old[i]for i in range(475));annotate(o,'Final neck-bearing01 second: original outer cervical-upper silhouette retained exactly; local inner upper receiving rows0–8 formed about actual head shaft centre, nominal164mm inner radius against154mm head underlap. Existing cervical-upper owner/root frame unchanged; local wall thickness grows and original fan receiving fit is qualified, not asserted.')
  changed.append(o.name);records.append({'name':o.name,'owner':o.parent.name,'outer475VerticesByteExact':True,'changedInnerRows':[0,8],'receivingInnerRadiusM':.164,'nominalUnderlapSeparationM':.010,'maximumInnerStockDeltaM':max(deltas),'stock':stock(o),'supportQualification':'Original owner/frame/fan remains exact; reshaped receiving stock has not been certified seated against it.'})
 return {'changedMeshes':changed,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'restoredExactOriginalLowerGuards':restored,'upperInterface':records,'unchangedFirstBearingBrackets':[f'V38 curved-neck formed yoke neck {s}'for s in(-1,1)],'construction':'Final focused head/upper-neck rigid nested underlap with original exterior coverage and integral shared lower leaf edge; restore first lower guards exactly to original source to remove first maximum-pitch regressions.','protected':'All source torso33plates/liner/bodysupports/returns/scapular stock exact; all joints/rest/hierarchy/materials/era profiles fixed. Two first race brackets exact.','limits':['24 declared geometry/metadata changes versus first neck-bearing,16net geometry changes versus original torso-support:14upper interface+2firstbrackets.','Appended leaf sectors are real shared-edge connected stock but support/swept fit and global likeness are not accepted.','Nominal10mm radial separation is not a finite surface clearance certificate across different axes or transitional roots.','Inherited higher fan and body frame/neck support defects remain unapproved.']}
