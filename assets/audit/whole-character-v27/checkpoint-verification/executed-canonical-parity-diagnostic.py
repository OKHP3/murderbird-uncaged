from pathlib import Path
import bpy,runpy,json,hashlib
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
O=R/'assets/audit/whole-character-v27/checkpoint-verification'
H=runpy.run_path(str(R/'scripts/build-uncaged-alignment-v7.py'))
a=R/'assets/audit/whole-character-v27/head-studies/attempt03/cranial-wrap.blend'
b=R/'assets/models/whole-character-v27/attempt-form01/murderbird-whole-character-v27.blend'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a)=='e9599d5d3926f16db9c379d138df23ff5f1a0e48ac82e91cc09e7303520757b6'
assert sha(b)=='3014ae3156f552716fcd34437b9ace9d567092ff4b99d3a3ded2e6f8bde66ceb'
def canonical():
    result={}
    for o in bpy.data.objects:
        if o.type!='MESH':continue
        vs=tuple(tuple(v.co) for v in o.data.vertices)
        es=tuple(sorted(tuple(sorted(e.vertices)) for e in o.data.edges))
        faces=[]
        for f in o.data.polygons:
            ids=tuple(f.vertices); cy=min(ids[i:]+ids[:i] for i in range(len(ids)))
            faces.append((cy,f.material_index,f.use_smooth))
        result[o.name]={'vertices':vs,'edges':es,'faces':tuple(sorted(faces))}
    return result

bpy.ops.wm.open_mainfile(filepath=str(a));sa=H['scene_snapshot']();ma={m.name:H['material_signature'](m) for m in bpy.data.materials};ca=canonical()
bpy.ops.wm.open_mainfile(filepath=str(b));sb=H['scene_snapshot']();mb={m.name:H['material_signature'](m) for m in bpy.data.materials};cb=canonical()
raw={n:{k:True for k in sa['meshes'][n] if sa['meshes'][n][k]!=sb['meshes'][n][k]} for n in sa['meshes'] if sa['meshes'][n]!=sb['meshes'][n]}
difference={n:[k for k in ca[n] if ca[n][k]!=cb[n][k]] for n in ca if ca[n]!=cb[n]}
result={'status':'Diagnostic only; direct integrated strict screens are separate','rawChangedFields':raw,'canonicalChangedFields':difference,'all670CanonicalMeshesEqual':ca==cb,'materialsEqual':ma==mb,'nodesEqual':sa['empties']==sb['empties'],'method':'Exact vertices, undirected sorted edges, oriented polygon cycles normalized only by cyclic start then sorted; polygon material/smoothing included. No geometric tolerance or winding reversal.'}
(O/'canonical-parity-diagnostic.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
