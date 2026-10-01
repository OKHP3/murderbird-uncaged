"""Breast-support02 pure regional restoration, source-exact rows4–6.
Input full breast-support01; no new design or invisible fit offset.
"""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'assets/models/whole-character-v38/lower-support02/murderbird-v38-lower-support02.blend'
LOWER=[f'V34 formed breast course {r} plate {c}'for r,n in((4,6),(5,5),(6,4))for c in range(1,n+1)]
def props(o):return json.loads(json.dumps(dict(o.items()),sort_keys=True,default=lambda v:list(v)))
def mesh(o):
 d={'verts':[list(v.co)for v in o.data.vertices],'edges':[list(v.vertices)for v in o.data.edges],'faces':[(list(p.vertices),p.material_index,p.use_smooth)for p in o.data.polygons],'mats':[m.name if m else None for m in o.data.materials]};return hashlib.sha256(json.dumps(d,sort_keys=True).encode()).hexdigest()
def apply():
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='74e185594a383f44dc1bbc0c09db7a10b5b4fb632f8b09f2a362743147a5d7a2'
 existingObjects=set(bpy.data.objects);existingMaterials=set(bpy.data.materials);targets={n:bpy.data.objects[n]for n in LOWER};receipts=[]
 with bpy.data.libraries.load(str(SOURCE),link=False)as(data_from,data_to):
  assert all(n in data_from.objects for n in LOWER);data_to.objects=LOWER.copy()
 for name,source in zip(LOWER,data_to.objects):
  target=targets[name];assert source is not None;sourceLocal=[list(r)for r in source.matrix_local];targetLocal=[list(r)for r in target.matrix_local];assert sourceLocal==targetLocal,(name,'source/restoration owner transform differs')
  wantedProperties=props(source);data=source.data
  # Map imported canonical stock slots to existing canonical material IDs;
  # data geometry and per-face indices remain exactly the source bytes.
  sourceMatNames=[m.name.removesuffix('.001').removesuffix('.002')if m else None for m in data.materials]
  expected=[s.material.name if s.material else None for s in target.material_slots];assert sourceMatNames==expected,(name,sourceMatNames,expected)
  data.materials.clear()
  for mat in expected:data.materials.append(bpy.data.materials[mat] if mat else None)
  sourceSignature=mesh(source);sourceParent=source.parent.name.removesuffix('.001')if source.parent else None;assert sourceParent==(target.parent.name if target.parent else None)
  target.data=data
  for key in list(target.keys()):del target[key]
  for key,value in source.items():target[key]=value.to_dict()if hasattr(value,'to_dict')else value.to_list()if hasattr(value,'to_list')else value
  assert props(target)==wantedProperties;assert mesh(target)==sourceSignature
  receipts.append({'name':name,'sourceRestoredMeshSha256':sourceSignature,'sourcePropertiesExact':True,'sourceMatrixLocalExact':True,'owner':target.parent.name,'eras':target.get('exteriorEras'),'class':target.get('constructionClass'),'sourceWallM':target.get('wallM'),'annotationQualification':'Entire original source properties restored byte-equivalently; old proposed/historical annotations remain inherited, no upgraded fit or current engineering acceptance.'})
 for o in set(bpy.data.objects)-existingObjects:bpy.data.objects.remove(o,do_unlink=True)
 for m in set(bpy.data.materials)-existingMaterials:
  assert m.users==0,(m.name,m.users);bpy.data.materials.remove(m)
 assert set(bpy.data.objects)==existingObjects;assert set(bpy.data.materials)==existingMaterials;bpy.context.view_layer.update()
 return {'changedMeshes':LOWER,'changedNodes':[],'addedMeshes':[],'removedMeshes':[],'watchMeshes':LOWER+[f'V34 formed breast course 3 plate {i}'for i in range(1,8)]+['V30 continuous tapered breast liner'],'attachmentAndEraMap':receipts,'sourceRestoration':{'native':str(SOURCE.relative_to(ROOT)),'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'identities':15,'rows':[4,5,6],'counts':[6,5,4]},'preserved':'Fuller upper18 plate/liner geometry and metadata source-exact to frozen breast-support01; complete original support/hinge/tab geometry, head/neck/wings/pelvis/legs/feet, rig transforms, materials/profiles and era eligibility unchanged. Only15 source lower-course objects restored; no broad redesign.','limits':['Pure restoration avoids known rebuilt low-course defects; new-row3/source-row4 seam is still a separate actual finite interface.','Restored original source fit warnings remain inherited and cannot be promoted to validated construction.','No continuous swept fit, welded fabrication/engineering or owner likeness acceptance.']}
