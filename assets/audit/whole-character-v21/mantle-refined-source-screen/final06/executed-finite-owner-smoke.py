import hashlib
assert hashlib.sha256(open('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v21/mantle-refined-source-screen/final06/executed-mantle-refined.py','rb').read()).hexdigest()=='c83d7a4932f4fbf4afea985ee0863e59efe0879750df30f9a0b7d57694e10937'
assert hashlib.sha256(open('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend','rb').read()).hexdigest()=='720c343645ef2de298a50e53c82fad66448c187b1eaf9311de2514cac079f280'
import bpy,json,hashlib,math,bmesh
r='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged';bpy.ops.wm.open_mainfile(filepath=r+'/assets/models/whole-character-v21/attempt-envelope03/murderbird-whole-character-v21.blend')
p='/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged/assets/audit/whole-character-v21/mantle-refined-source-screen/final06/executed-mantle-refined.py';s={};exec(compile(open(p).read(),p,'exec'),s);receipt=s['apply']();dg=bpy.context.evaluated_depsgraph_get();issues=[];finite=0;counts={};volumes=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 ev=o.evaluated_get(dg);m=ev.to_mesh();assert all(math.isfinite(x) for v in m.vertices for x in v.co),o.name;finite+=1
 if o.name in receipt['changed'] or o.name.startswith('V21 refined'):
  clone=m.copy()
  if clone.validate(verbose=False):issues.append(o.name)
  bpy.data.meshes.remove(clone)
  bm=bmesh.new();bm.from_mesh(m);volumes.append(bm.calc_volume(signed=True));assert all(e.is_manifold for e in bm.edges),o.name;bm.free()
  assert o.parent.name in s['OWNERS'];assert o.get('exteriorEras')=='maker,mechanic,builder';counts[o.parent.name]=counts.get(o.parent.name,0)+1
 ev.to_mesh_clear()
print('MANTLE_SMOKE',json.dumps({'sourceSHA256':hashlib.sha256(open(p,'rb').read()).hexdigest(),'evaluatedFiniteMeshes':finite,'validationRepairs':issues,'finiteWallClosedMeshCount':len(volumes),'positiveVolumes':sum(v>0 for v in volumes),'minimumSignedVolume':min(volumes),'ownerCountsIncludingLiners':counts,'plateCounts':receipt['ownerPlateCounts'],'removedSkinsAndPins':len(receipt['removed']),'exactOriginalNodes':receipt['preservedOriginalNodes'],'exactOutsideMeshes':receipt['preservedOutsideMeshes']}))
