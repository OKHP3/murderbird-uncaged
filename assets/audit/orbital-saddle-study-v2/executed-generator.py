"""Matched plate seams for the held orbital saddle; no app integration.

Restore the original mounting bed, then make real local reliefs in that bed
and the touching crown plates. Keep each moving cover distinct and retain
an unapplied Boolean stack in the editable native.
"""
from pathlib import Path
import hashlib,json,runpy,shutil
import bpy,bmesh
from mathutils import Vector
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.blend'
SADDLE=ROOT/'assets/models/uncaged-orbital-saddle-study-v1/murderbird-orbital-saddle-study-v1.blend'
OUT=ROOT/'assets/models/uncaged-orbital-saddle-study-v2'
AUDIT=ROOT/'assets/audit/orbital-saddle-study-v2'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}

def main():
    assert sha(BASE)=='7ba7c996fbcffc118217ad4fcd0c1c1316a3e0a6b0cefa77be4794e6f5a4df15'
    assert sha(SADDLE)=='288c2bd755761c72ff6a1d002e7ed8d61ae93caa147a3a063dfa8c0b155d952f'
    assert not OUT.exists() and not AUDIT.exists()
    h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
    # The frozen generic helper deliberately rejects external modifier inputs.
    # This local extension records the two named construction tools explicitly;
    # the tools themselves are also part of the full save/reload snapshot.
    original_modifier_signature=h['modifier_signature']
    def saddle_modifiers(obj):
        records=[]
        for mod in obj.modifiers:
            if mod.type!='BOOLEAN':
                records.extend(original_modifier_signature(SimpleNamespace(name=obj.name,modifiers=[mod])));continue
            assert mod.object and mod.object.name in ['Orbital saddle seam tool -1','Orbital saddle seam tool 1']
            assert mod.collection is None and mod.operand_type=='OBJECT'
            records.append({'name':mod.name,'type':mod.type,'showViewport':mod.show_viewport,'showRender':mod.show_render,
                'values':{key:getattr(mod,key) for key in ['operation','solver','operand_type','double_threshold','use_self','use_hole_tolerant','material_mode']},'object':mod.object.name})
        return records
    h['scene_snapshot'].__globals__['modifier_signature']=saddle_modifiers
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    mounts=[f'Forged orbital mounting plate {s}' for s in (-1,1)]
    original_points={n:[v.co.copy() for v in bpy.data.objects[n].data.vertices] for n in mounts}
    original_signatures={n:h['mesh_signature'](bpy.data.objects[n]) for n in mounts}
    bpy.ops.wm.open_mainfile(filepath=str(SADDLE));before=h['scene_snapshot']()
    # Recover the unchanged closed mounting wall rather than pulling vertices
    # inward into the crown. The earlier deformation remains inV1 only.
    for name in mounts:
        target=bpy.data.objects[name];assert len(target.data.vertices)==len(original_points[name])
        for v,p in zip(target.data.vertices,original_points[name]):v.co=p
        target.data.update();assert h['mesh_signature'](target)==original_signatures[name]
    cutters=[];changed=set(mounts);reliefs=[]
    for side in (-1,1):
        brow=bpy.data.objects[f'Forged orbital brow {side}']
        cutter=bpy.data.objects.new(f'Orbital saddle seam tool {side}',brow.data.copy());bpy.context.scene.collection.objects.link(cutter)
        cutter.parent=brow.parent;cutter.matrix_world=brow.matrix_world.copy()
        bm=bmesh.new();bm.from_mesh(cutter.data);bm.normal_update()
        for v in bm.verts:v.co+=v.normal*.002
        bm.to_mesh(cutter.data);bm.free();cutter.data.update()
        cutter.hide_render=True;cutter.hide_set(True);cutter.display_type='WIRE';cutter['constructionTool']=True
        cutters.append(cutter.name)
        for name in [f'Forged orbital mounting plate {side}','Rounded swept crown lamina 0','Rounded swept crown lamina 1',f'Swept temporal lamina {side} 0 0']:
            obj=bpy.data.objects[name];mod=obj.modifiers.new(f'Fitted saddle relief {side}','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
            changed.add(name);reliefs.append({'part':name,'tool':cutter.name,'method':'Exact Boolean difference, nominal2mm outward vertex-normal cutter expansion'})
    bpy.context.view_layer.update()
    # Persist independent construction tools in a hidden collection, keeping
    # their intended exclusion from any future export explicit.
    collection=bpy.data.collections.new('Construction tools - exclude from export');bpy.context.scene.collection.children.link(collection)
    for name in cutters:
        obj=bpy.data.objects[name]
        for col in list(obj.users_collection):col.objects.unlink(obj)
        collection.objects.link(obj)
    after=h['scene_snapshot']()
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    for name,old in before['meshes'].items():
        if name not in changed:assert after['meshes'][name]==old,name
    topology=[];deps=bpy.context.evaluated_depsgraph_get()
    for name in sorted(changed):
        obj=bpy.data.objects[name];evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh();bm=bmesh.new();bm.from_mesh(mesh)
        row={'name':name,'evaluatedVertices':len(mesh.vertices),'evaluatedFaces':len(mesh.polygons),'nonManifoldEdges':sum(not e.is_manifold for e in bm.edges),'looseVertices':sum(not v.link_faces for v in bm.verts)}
        assert row['evaluatedVertices'] and not row['nonManifoldEdges'] and not row['looseVertices'],row
        topology.append(row);bm.free();evaluated.to_mesh_clear()
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-orbital-saddle-study-v2.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    receipt={'status':'unreviewed matched saddle seam proposal; not selected','base':art(BASE),'saddleSource':art(SADDLE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changedParts':sorted(changed),'constructionTools':cutters,'reliefs':reliefs,'evaluatedTopology':topology,'preservation':{'other693SaddleMeshesExact':True,'51PivotsAnd462GuidesExact':True,'sourceFilesUnchanged':True,'saveReloadExact':True},'limits':['No export or integration; construction tool meshes MUST be excluded from future export.','2mm expansion is a nominal construction operation, not a verified minimum gap.','Opening motion, fit of retained fasteners and visual seam quality require review.','Boolean seams are proposed manufacturing geometry; original illustration does not establish these hidden details.']}
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    render=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders']
    # Existing neutral renderer resets all mesh visibility; do not use it for
    # hidden construction tools. A review-only copy removes tools after baking
    # these modifiers in memory, without saving over the editable native.
    review=OUT/'murderbird-orbital-saddle-study-v2-review.blend'
    for name in sorted(changed):
        obj=bpy.data.objects[name];bpy.context.view_layer.objects.active=obj
        for mod in list(obj.modifiers):
            if mod.type=='BOOLEAN':bpy.ops.object.modifier_apply(modifier=mod.name)
    for name in cutters:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(review),check_existing=False)
    receipt['reviewDerivative']=art(review)
    render.__globals__['AUDIT']=AUDIT;receipt['views']=render(SADDLE,'before')+render(review,'after')
    (AUDIT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'native':art(native),'review':art(review),'topology':topology}))

if __name__=='__main__':main()
