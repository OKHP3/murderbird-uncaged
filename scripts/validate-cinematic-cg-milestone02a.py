"""Preservation and export checks; artistic acceptance is separate."""
import bpy,json,hashlib,struct
from pathlib import Path
R=Path(__file__).resolve().parents[1]
report={'status':'PASS','artistic_acceptance':'Pending owner review','eras':{}}
def geometry(o):
 return hashlib.sha256(repr(([(tuple(v.co)) for v in o.data.vertices], [tuple(p.vertices) for p in o.data.polygons], [tuple(v.uv) for l in o.data.uv_layers for v in l.data])).encode()).hexdigest()
for era in ('maker','mechanic','builder'):
 before=R/f'assets/models/cinematic-cg-milestone03/murderbird-cg-3-{era}.blend'
 after=R/f'assets/models/cinematic-cg-milestone02a/murderbird-cg-2a-{era}.blend'
 bpy.ops.wm.open_mainfile(filepath=str(before));bpy.context.view_layer.update()
 old={o.name:{'region':o.get('cg1cRegion'),'matrix':tuple(x for row in o.matrix_world for x in row),'geometry':geometry(o),'role':o.get('surfaceRole')} for o in bpy.context.scene.objects if o.type=='MESH' and not o.get('authoringGuide')}
 bpy.ops.wm.open_mainfile(filepath=str(after));bpy.context.view_layer.update()
 pose_changed=[];legs_checked=0;missing=[];optics=[]
 for name,b in old.items():
  o=bpy.data.objects.get(name)
  assert o is not None,('source object removed',name)
  diff=max(abs(a-z) for a,z in zip(b['matrix'],tuple(x for row in o.matrix_world for x in row)))
  if diff>1e-6 and b['role']!='optic':pose_changed.append(name)
  if b['region'] in ('leg','legs','foot','feet'):
   assert b['geometry']==geometry(o),(name,'leg/foot geometry changed');legs_checked+=1
 assert not pose_changed,pose_changed
 for o in bpy.context.scene.objects:
  if o.type!='MESH' or o.hide_render or o.get('authoringGuide'):continue
  if not o.data.uv_layers:missing.append(o.name)
  for m in o.data.materials:
   if m and m.use_nodes and (o.get('surfaceRole') in ('optic','optic-ring')):
    q=m.node_tree.nodes.get('Principled BSDF')
    if q:optics.append(float(q.inputs['Emission Strength'].default_value))
 assert not missing,missing
 if era!='builder':assert max(optics,default=0)==0,(era,optics)
 glb=(R/f'assets/models/cinematic-cg-milestone02a/murderbird-cg-2a-{era}.glb').read_bytes()
 size,kind=struct.unpack_from('<II',glb,12);g=json.loads(glb[20:20+size])
 assert len(g['images'])==12,(era,len(g['images']))
 assert 'KHR_materials_transmission' in g['extensionsUsed']
 assert all('TEXCOORD_0' in p['attributes'] for m in g['meshes'] for p in m['primitives'])
 assert not any('ground' in n.get('name','').lower() for n in g['nodes'])
 receipt=json.loads((R/'assets/audit/cinematic-cg-milestone02a/attempt02'/('receipt.json' if era=='builder' else era+'/receipt.json')).read_text())
 assert receipt['source_preserved'] and receipt['detail_bounds_guard']['status']=='PASS'
 report['eras'][era]={'original_objects_preserved':len(old),'pose_transforms_preserved_except_authored_optic':True,'leg_foot_geometry_uvs_exact':legs_checked,'visible_missing_uvs':missing,'glb_meshes':len(g['meshes']),'embedded_images':len(g['images']),'extensions':g['extensionsUsed'],'dark_optics':era!='builder','bounds_guard':'PASS'}
(R/'assets/audit/cinematic-cg-milestone02a/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('CG2A_PRESERVATION_PASS',json.dumps(report))
