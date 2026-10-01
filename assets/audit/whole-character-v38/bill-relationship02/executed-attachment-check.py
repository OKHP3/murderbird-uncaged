# Actual source/saved owner axes, socket surface and finite topology. Read-only.
import bpy,bmesh,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[4];a=Path(__file__).resolve().parent;out=a/'attachment-check.json';assert not out.exists();names=[f'V32 returned upper bill course {i}'for i in range(3)]+['V32 formed mandibular bowl'];models=[];shapes={}
for label,folder in [('source','orbital-clearance02'),('01','bill-relationship01'),('02','bill-relationship02')]:
 path=r/f'assets/models/whole-character-v38/{folder}/murderbird-v38-{folder}.blend';bpy.ops.wm.open_mainfile(filepath=str(path));jaw=bpy.data.objects['jaw'];bowl=bpy.data.objects[names[-1]];meta=json.loads(jaw['makerControlSocketV1']);p=meta['point'];local=Vector((p[0],-p[2],p[1]));vertex=bowl.matrix_world@bowl.data.vertices[283].co;socket=jaw.matrix_world@local;rows=[]
 for n in names:
  o=bpy.data.objects[n];bm=bmesh.new();bm.from_mesh(o.data);remaining=set(bm.verts);components=0
  while remaining:
   components+=1;stack=[remaining.pop()]
   while stack:
    v=stack.pop()
    for e in v.link_edges:
     q=e.other_vert(v)
     if q in remaining:remaining.remove(q);stack.append(q)
  rows.append({'name':n,'owner':o.parent.name,'components':components,'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'positiveVolumeM3':bm.calc_volume(signed=True),'eraEligibility':o.get('exteriorEras'),'materialNames':[m.name if m else None for m in o.data.materials]});bm.free()
 models.append({'label':label,'nativeSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'jawRestLocalMatrix':[list(row)for row in jaw.matrix_local],'jawRestBasis':[list(row)for row in jaw.matrix_basis],'physicalSocketVertexIndex':283,'physicalSocketLocal':list(bowl.data.vertices[283].co),'socketMetadata':meta,'socketVertexDistanceM':(vertex-socket).length,'region':rows});shapes[label]={n:([list(v.co)for v in bpy.data.objects[n].data.vertices],[tuple(f.vertices)for f in bpy.data.objects[n].data.polygons])for n in names[:3]}
assert models[0]['jawRestLocalMatrix']==models[1]['jawRestLocalMatrix']==models[2]['jawRestLocalMatrix'];assert models[0]['socketMetadata']==models[1]['socketMetadata']==models[2]['socketMetadata'];assert models[0]['physicalSocketLocal']==models[1]['physicalSocketLocal']==models[2]['physicalSocketLocal'];assert shapes['01']==shapes['02'];assert all(q['socketVertexDistanceM']<1e-6 for q in models)
oldkeys=[(row,k)for row in range(53)for k in range(33)if row<=5 or k<=6 or k>=26];first=json.loads((r/'assets/audit/whole-character-v38/bill-relationship01/self-screen.json').read_text())['models'][1]['meshes'][-1]['firstWitness'];first['sourceGridLocation']=[[[oldkeys[i%856][0],oldkeys[i%856][1],'inner'if i>=856 else'outer']for i in tri]for tri in first['vertices']]
out.write_text(json.dumps({'status':'PASS source realjaw axis/rest/socket and01upper3 vs02 exact; topology diagnostic only','models':models,'inventoryCorrection':'source-inventory.json jawRestLocalMatrix was captured after negative0.32 feasibility sample. This output separately reopens actual source and candidates at authoredrest. Its recorded restbasis was already accurate; flawed original record preserved.','first01SelfWitnessMapped':first,'limits':['Finite mesh volume/closure does not prove interpart or self clearance; separate unchanged predicates.','Socket vertex283 is physical source socket footprint, not detached authored marker.','Actual allprotectedparts source snapshot exact in receipts. No owner/art/manufacturing approval.']},indent=2)+'\n');print('attachment-pass',flush=True)
