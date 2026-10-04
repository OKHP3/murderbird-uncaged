import bpy,json,hashlib,numpy as np
from pathlib import Path
names=['CGH18 formed dorsal bill root cuff','CGH18 formed distal hooked bill plate','CGH17 broad curved brow course near 0','CGH17 broad curved brow course near 1','CGH17 broad curved brow course near 2','CGH06 connected under-eye bill-root cheek sheet L','CGH06 substantial swept plated mandible L']
result=[];d=bpy.context.evaluated_depsgraph_get()
for name in names:
 o=bpy.context.scene.objects.get(name)
 if not o:result.append(dict(name=name,status='MISSING'));continue
 ev=o.evaluated_get(d);mat=[]
 for i,s in enumerate(o.material_slots):
  m=s.material;p=[p for p in o.data.polygons if p.material_index==i]
  mat.append(dict(slot=i,link=s.link,material=m.name if m else None,evaluatedMaterial=ev.data.materials[i].name if i<len(ev.data.materials) and ev.data.materials[i] else None,faces=len(p),nativeArea=sum(p.area for p in p),images=[dict(node=n.name,label=n.label,image=n.image.name if n.image else None,filepath=n.image.filepath if n.image else None,size=list(n.image.size) if n.image else None,packedSHA=hashlib.sha256(bytes(n.image.packed_file.data)).hexdigest() if n.image and n.image.packed_file else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'],links=[list((l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name)) for l in m.node_tree.links],normalStrength=[float(n.inputs['Strength'].default_value) for n in m.node_tree.nodes if n.type=='NORMAL_MAP']))
 uv=[]
 for layer in o.data.uv_layers:
  coords=[tuple(v.uv) for v in layer.data];rows=[]
  for p in o.data.polygons[:min(4,len(o.data.polygons))]:
   rows.append(dict(face=p.index,slot=p.material_index,xyz=[list(o.data.vertices[o.data.loops[li].vertex_index].co) for li in p.loop_indices],uv=[list(layer.data[li].uv) for li in p.loop_indices]))
  uv.append(dict(name=layer.name,minimum=[min(v[i] for v in coords) for i in [0,1]],maximum=[max(v[i] for v in coords) for i in [0,1]],firstFaces=rows))
 result.append(dict(name=name,hideRender=o.hide_render,hideViewport=o.hide_viewport,hideLayer=o.hide_get(),bounds=[list(v) for v in o.bound_box],worldMatrix=[list(v) for v in o.matrix_world],mesh=o.data.name,vertices=len(o.data.vertices),faces=len(o.data.polygons),slots=mat,uv=uv))
p=Path('/tmp/cg-recursive-finish04-readonly.json');p.write_text(json.dumps(dict(scope='Read-only retained02 builder diagnostic; no source/model changes or future input assumption',objects=result),indent=2)+'\n');print('READONLY_HEAD_REPORT',str(p),flush=True)
