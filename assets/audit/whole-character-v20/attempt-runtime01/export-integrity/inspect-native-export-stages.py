"""Read-only native and in-memory export-copy validation; never save/export a model."""
from pathlib import Path
import bpy,bmesh,hashlib,json,math
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v20/attempt-runtime01/export-integrity'
INPUTS=[('v19',ROOT/'assets/models/whole-character-v19/attempt-02/murderbird-whole-character-v19.blend'),('proportions02',ROOT/'assets/models/whole-character-v20/attempt-proportions02/murderbird-whole-character-v20.blend'),('runtime01',ROOT/'assets/models/whole-character-v20/attempt-runtime01/murderbird-whole-character-v20.blend')]
WARN='V17 breast directional lamina 1 1 left'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def arrays(m):return {'coordinates':[list(v.co) for v in m.vertices],'edges':[list(e.vertices) for e in m.edges],'polygons':[{'vertices':list(p.vertices),'material':p.material_index,'smooth':p.use_smooth} for p in m.polygons]}
def small(m):
 m.calc_loop_triangles();deg=[];nonfinite=[]
 for v in m.vertices:
  if not all(math.isfinite(x) for x in v.co):nonfinite.append(v.index)
 for t in m.loop_triangles:
  a,b,c=[m.vertices[i].co for i in t.vertices]
  if ((b-a).cross(c-a)).length/2<=1e-14:deg.append(t.index)
 return {'vertices':len(m.vertices),'edges':len(m.edges),'polygons':len(m.polygons),'loops':len(m.loops),'triangles':len(m.loop_triangles),'nonfiniteVertices':nonfinite,'degenerateTrianglesAreaLE1e14':deg,'materialSlots':len(m.materials),'outOfRangeMaterialFaces':[p.index for p in m.polygons if p.material_index>=max(1,len(m.materials))], 'repeatedVertexFaces':[p.index for p in m.polygons if len(set(p.vertices))!=len(p.vertices)],'attributes':[{'name':a.name,'type':a.data_type,'domain':a.domain,'count':len(a.data)} for a in m.attributes]}
def topo(m):
 bm=bmesh.new();bm.from_mesh(m)
 rec={'boundaryEdges':sum(e.is_boundary for e in bm.edges),'wireEdges':sum(e.is_wire for e in bm.edges),'nonmanifoldEdges':sum(not e.is_manifold for e in bm.edges),'edgesWithMoreThanTwoFaces':sum(len(e.link_faces)>2 for e in bm.edges),'signedVolumeLocalM3':bm.calc_volume(signed=True),'zeroAreaFacesLE1e12':sum(f.calc_area()<1e-12 for f in bm.faces),'connectedSurfaceComponents':None}
 unseen=set(bm.faces);count=0
 while unseen:
  count+=1;todo=[unseen.pop()]
  while todo:
   f=todo.pop()
   for e in f.edges:
    for nxt in e.link_faces:
     if nxt in unseen:unseen.remove(nxt);todo.append(nxt)
 rec['connectedSurfaceComponents']=count;bm.free();return rec

def validation(m,detailed=False):
 c=m.copy();before=small(c) if detailed else {'vertices':len(c.vertices),'edges':len(c.edges),'polygons':len(c.polygons),'loops':len(c.loops)}
 initial=arrays(c) if detailed else None
 # Match installed exporter validation, mutating only disposable in-memory mesh copy.
 repaired=c.validate(verbose=detailed)
 after=small(c) if detailed else {'vertices':len(c.vertices),'edges':len(c.edges),'polygons':len(c.polygons),'loops':len(c.loops)}
 result={'validationRepaired':bool(repaired),'before':before,'after':after}
 if detailed:
  final=arrays(c);result['geometryArraysChanged']=initial!=final;result['topologyBefore']=topo(m);result['topologyAfterValidation']=topo(c)
  result['changedGeometryCategories']=[k for k in initial if initial[k]!=final[k]]
 bpy.data.meshes.remove(c);return result

reports=[]
for label,path in INPUTS:
 start=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 rec={'label':label,'nativePath':path.relative_to(ROOT).as_posix(),'nativeShaBefore':start,'sourceMeshCount':sum(o.type=='MESH' for o in bpy.data.objects),'stages':{},'warnedIndividual':{}}
 for stage in ('raw','evaluated'):
  bad=[];dg=bpy.context.evaluated_depsgraph_get()
  for o in list(bpy.context.scene.objects):
   if o.type!='MESH':continue
   if stage=='raw':m=o.data
   else:e=o.evaluated_get(dg);m=e.to_mesh()
   val=validation(m,o.name==WARN)
   if val['validationRepaired']:bad.append({'object':o.name,'data':o.data.name,'validation':val})
   if o.name==WARN:rec['warnedIndividual'][stage]=val;rec['warnedIndividual']['modifiers']=[{'type':x.type,'name':x.name,'thickness':getattr(x,'thickness',None),'width':getattr(x,'width',None)} for x in o.modifiers]
   if stage=='evaluated':e.to_mesh_clear()
  rec['stages'][stage]={'repairCount':len(bad),'repaired':bad}
 # Exactly repeat conversion, face-only cleanup and normals operation in export helper.
 cleanup=[];converted_bad=[]
 for o in list(bpy.context.scene.objects):
  if o.type!='MESH':continue
  bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
  bm=bmesh.new();bm.from_mesh(o.data);bad=[f for f in bm.faces if f.calc_area()<1e-12]
  if bad:cleanup.append({'name':o.name,'deletedZeroAreaFaces':len(bad) });bmesh.ops.delete(bm,geom=bad,context='FACES_ONLY')
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
  for attr in list(o.data.color_attributes):o.data.color_attributes.remove(attr)
  val=validation(o.data,o.name==WARN)
  if val['validationRepaired']:converted_bad.append({'object':o.name,'data':o.data.name,'validation':val})
  if o.name==WARN:rec['warnedIndividual']['convertedCleaned']=val
 rec['stages']['convertedCleaned']={'repairCount':len(converted_bad),'repaired':converted_bad,'faceOnlyCleanup':cleanup}
 groups={}
 for o in list(bpy.context.scene.objects):
  if o.type=='MESH':groups.setdefault((o.parent,o.get('exteriorEras','maker,mechanic,builder'),o.get('region','back'),o.get('surfaceRole','frame')),[]).append(o)
 joined_bad=[];rec['groups']=[]
 for (parent,eras,region,role),objects in groups.items():
  members=[o.name for o in objects];bpy.ops.object.select_all(action='DESELECT')
  for o in objects:o.select_set(True)
  bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();merged=bpy.context.object;merged.name=f'{parent.name}-{region}-{role}'
  val=validation(merged.data,WARN in members)
  g={'name':merged.name,'dataName':merged.data.name,'members':members,'validation':val,'parent':parent.name,'eras':eras,'region':region,'role':role}
  if val['validationRepaired']:joined_bad.append(g)
  if WARN in members:rec['warnedJoinedGroup']=g
  rec['groups'].append({'name':g['name'],'dataName':g['dataName'],'memberCount':len(members)})
 rec['stages']['joined']={'repairCount':len(joined_bad),'repaired':joined_bad}
 rec['nativeShaAfter']=sha(path);assert rec['nativeShaAfter']==start;reports.append(rec)
 (OUT/f'{label}-stages.json').write_text(json.dumps(rec,indent=2))
 print(json.dumps({'label':label,'stages':{k:v['repairCount'] for k,v in rec['stages'].items()},'warnedGroup':rec['warnedJoinedGroup']['name'],'nativeUnchanged':True}),flush=True)
(OUT/'native-stages-summary.json').write_text(json.dumps([{'label':r['label'],'sha':r['nativeShaBefore'],'stages':{k:v['repairCount'] for k,v in r['stages'].items()},'warnedGroup':r['warnedJoinedGroup']['name']} for r in reports],indent=2))
