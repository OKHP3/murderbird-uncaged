"""Author a versioned exterior over the frozen alignment-v3 rigid interface.

Run with Blender --background --python this-file -- --iteration iteration-01.
Each iteration is new; recorded sources and earlier outputs are never rewritten.
"""
from pathlib import Path
import argparse, ast, hashlib, json, math, runpy, shutil, sys
import bpy, bmesh
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
parser = argparse.ArgumentParser()
parser.add_argument('--iteration', required=True)
opts = parser.parse_args(args)
assert opts.iteration.startswith('iteration-') and '/' not in opts.iteration
OUT = ROOT/'assets/models/uncaged-appearance-v1/iterations'/opts.iteration
OUT.mkdir(parents=True, exist_ok=True)
assert not (OUT/'murderbird-appearance.blend').exists(), 'Preserve prior iteration; use a new iteration name.'
BASE = ROOT/'assets/models/uncaged-alignment-v3/murderbird-alignment-v3.blend'
BASE_SHA = '6de7c16728ac2ac4926b9b0bd608d7eb5e03f702d3e1ef222db997c84fd7ff3a'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(BASE) == BASE_SHA, 'Frozen structural source changed; reconcile explicitly.'
authoring_scripts=['build-uncaged-appearance-v1.py','appearance-head-neck.py','appearance-body-detail.py','appearance-limb-casing.py','appearance-bill-finish.py','appearance-materials.py']
snapshot=OUT/'authoring';snapshot.mkdir(exist_ok=True)
for name in authoring_scripts:shutil.copy2(ROOT/'scripts'/name,snapshot/name)
bpy.ops.wm.open_mainfile(filepath=str(BASE))
for o in bpy.data.objects:
    o.animation_data_clear()
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
bpy.context.scene.frame_set(1)
bpy.context.view_layer.update()
pivots = {o.name:{'parent':o.parent.name if o.parent else None, 'matrix':list(sum((list(row) for row in o.matrix_local), []))} for o in bpy.data.objects if o.type=='EMPTY'}
ALL='maker,mechanic,builder'

def load_functions(path, names):
    tree=ast.parse(path.read_text())
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),str(path),'exec'),globals())
load_functions(ROOT/'scripts/build-uncaged-presence-study.py', {'material','group','mesh','bevel','rod','ring','tube'})
load_functions(ROOT/'scripts/build-uncaged-neutral-v2.py', {'under','tag','wm','wr','wt','mix','sample','envelope','polygon_surface','patch','shell','fastener','curve'})
load_functions(ROOT/'scripts/build-uncaged-alignment-v3.py', {'smooth_profile'})
# Fitted sheet faces keep their authored curvature. The inherited helper uses
# Blender's default angle-limited bevel; weighted normals and bevels at local
# folds can still distort these thin, densely tessellated plates. Remove both
# from new patches and split genuine wall corners after applying Solidify.
legacy_patch = patch
def patch(*args, **kwargs):
    obj = legacy_patch(*args, **kwargs)
    for modifier in list(obj.modifiers):
        if modifier.type in {'BEVEL', 'WEIGHTED_NORMAL'}:
            obj.modifiers.remove(modifier)
        elif modifier.type == 'SOLIDIFY':
            modifier.use_even_offset = False
            modifier.use_quality_normals = True
    obj['appearanceFittedSheet'] = True
    return obj

mat={name:bpy.data.materials['Neutral / '+name] for name in ['plate','edge','frame','recess','bearing','repair','optic','inner']}
parts=[]
ctx={key:globals()[key] for key in ['bpy','Vector','Matrix','math','mat','patch','wm','wr','wt','fastener','sample','envelope','smooth_profile','under','shell']}
ctx.update(root=ROOT,out=OUT)
notes={}
for name in ['appearance-head-neck.py','appearance-body-detail.py','appearance-limb-casing.py','appearance-bill-finish.py']:
    notes[name]=runpy.run_path(str(snapshot/name))['build'](ctx)
bpy.context.view_layer.update()
for name,data in pivots.items():
    o=bpy.data.objects[name]
    assert (o.parent.name if o.parent else None)==data['parent'], name+' changed parent'
    assert max(abs(a-b) for a,b in zip(sum((list(row) for row in o.matrix_local),[]),data['matrix']))<1e-7, name+' changed transform'

# Collapse construction modifiers before UV/material assignment, preserving
# every independently moving owner and source piece in the editable scene.
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    o.hide_set(False);o.hide_render=False
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    bm=bmesh.new();bm.from_mesh(o.data)
    invalid=[f for f in bm.faces if f.calc_area()<1e-12]
    if invalid:bmesh.ops.delete(bm,geom=invalid,context='FACES_ONLY')
    bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bm.to_mesh(o.data);bm.free()
    extent=max((max(abs(v) for v in (o.matrix_world @ vertex.co)) for vertex in o.data.vertices),default=0)
    assert extent < 4.0, f'Runaway construction geometry: {o.name}: {extent:.3f} m'
    if o.get('appearanceFittedSheet'):
        o.data.set_sharp_from_angle(angle=math.radians(50))
material_module=runpy.run_path(str(snapshot/'appearance-materials.py'))
finish=material_module['build'](ctx)
notes['materials']=finish.get('notes',{})

# One shared mechanical interface, separately eligible era surfaces. Native
# pieces are retained; only the export scene batches equivalent surfaces.
source_meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
source_parts=[]
for o in source_meshes:
    allowed=o.get('exteriorEras',ALL).split(',')
    owner=o.parent
    while owner and owner.type!='EMPTY':owner=owner.parent
    assert owner is not None,o.name
    source_name=o.name
    world=o.matrix_world.copy()
    for child in list(o.children):
        child_world=child.matrix_world.copy();child.parent=owner;child.matrix_world=child_world
    for era in allowed:
        clone=o.copy();clone.data=o.data.copy();bpy.context.collection.objects.link(clone)
        clone.name=source_name+' ['+era+']';clone.parent=owner;clone.matrix_world=world
        clone['exteriorEras']=era;clone['appearanceSourcePart']=source_name
        finish['assign'](clone,era)
        clone.hide_render=era!='builder';clone.hide_set(era!='builder')
        source_parts.append({'name':clone.name,'sourcePart':source_name,'owner':owner.name,'era':era,'region':clone.get('region'),'role':clone.get('surfaceRole'),'vertices':len(clone.data.vertices)})
    bpy.data.objects.remove(o,do_unlink=True)
root=bpy.data.objects.get('murderbird')
if root:root['status']='Appearance production candidate; artistic acceptance pending'
bpy.context.preferences.filepaths.save_version=0
native=OUT/'murderbird-appearance.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(native))

groups={}
for o in list(bpy.context.scene.objects):
    if o.type!='MESH':continue
    o.hide_set(False);o.hide_render=False
    groups.setdefault((o.parent,o.get('exteriorEras'),o.get('region'),o.get('surfaceRole')),[]).append(o)
for (parent,era,region,role),objects in groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    if len(objects)>1:bpy.ops.object.join()
    o=bpy.context.object;o.name=f'{parent.name}-{region}-{role}-{era}'
    o['exteriorEras']=era;o['region']=region;o['surfaceRole']=role
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:o.select_set(o.type in {'MESH','EMPTY'})
model=OUT/'murderbird-appearance.glb'
bpy.ops.export_scene.gltf(filepath=str(model),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True,export_cameras=False,export_lights=False,export_animations=False,export_tangents=True)
assert sha(BASE)==BASE_SHA
record={'status':'appearance candidate; owner artistic acceptance pending','iteration':opts.iteration,'structuralBaseline':{'revision':'3e6d340e616e79708d2a62ec9255fd997d14ea4f','path':str(BASE.relative_to(ROOT)),'sha256':BASE_SHA},'preservedPivots':pivots,'parts':source_parts,'notes':notes,'rights':'Creative content all rights reserved under NOTICE.md; new visible details are proposals','generatedFiles':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in [native,model]],'scripts':[{'path':str((ROOT/'scripts'/p).relative_to(ROOT)),'sha256':sha(snapshot/p)} for p in authoring_scripts], 'authoringSnapshot':str(snapshot.relative_to(ROOT))}
(OUT/'appearance-inventory.json').write_text(json.dumps(record,indent=2)+'\n')
print('APPEARANCE_COMPLETE',json.dumps({'iteration':opts.iteration,'nativePieces':len(source_parts),'modelBytes':model.stat().st_size,'modelSha256':sha(model)}))
