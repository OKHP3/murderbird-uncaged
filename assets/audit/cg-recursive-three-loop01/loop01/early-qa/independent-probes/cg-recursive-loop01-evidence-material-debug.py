import bpy,json,pathlib
ps=['/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/models/cg-supervised01/attempt09/murderbird-supervised-builder.blend','/Users/okh/.codex/worktrees/cg-architect-cycle01/murderbird-uncaged/assets/audit/cg-recursive-three-loop01/loop01/integrated/study01/builder/murderbird-recursive-builder.blend']
def val(v):
 if isinstance(v,(str,int,float,bool,type(None))):return v
 if isinstance(v,bpy.types.ID):return [v.bl_rna.identifier,v.name]
 try:return [val(x) for x in v]
 except:return str(v)
def rna(o):
 d={}
 for p in o.bl_rna.properties:
  if p.identifier in ['rna_type','name','location','dimensions','width','height','select','parent'] or p.type=='COLLECTION':continue
  try:d[p.identifier]=val(getattr(o,p.identifier))
  except:pass
 return d
rows=[]
for p in ps:
 bpy.ops.wm.open_mainfile(filepath=p,load_ui=False,use_scripts=False)
 o=bpy.data.objects['H03 hooked bill'];m=bpy.data.materials['CG metal05 / breast-armor / builder / local0'];rows.append({'mod':[(x.name,rna(x)) for x in o.modifiers],'material':rna(m),'node':rna(next(iter(m.node_tree.nodes)))})
for k in rows[0]:
 a,b=rows[0][k],rows[1][k]
 if isinstance(a,dict):print(k,{x:[a[x],b.get(x)] for x in a if a[x]!=b.get(x)})
 else: print(k,a,b)
