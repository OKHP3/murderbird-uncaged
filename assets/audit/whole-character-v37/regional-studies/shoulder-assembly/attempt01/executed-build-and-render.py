import bpy,json,hashlib,runpy,bmesh
from pathlib import Path
from mathutils import Vector
R=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');A=Path(__file__).resolve().parent;M=R/'assets/models/whole-character-v37/regional-studies/shoulder-assembly'/A.name/'murderbird-shoulder-assembly.blend';BASE=R/'assets/models/whole-character-v35/attempt-form01/murderbird-whole-character-v35.blend'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(BASE)=='d2c704ccf89f3f0e7dbeb3613dcdbdd964c4ba69991783783830803eecf59cb0';assert not M.exists()
bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.view_layer.update();result=runpy.run_path(str(A/'executed-shoulder-assembly.py'))['apply']();geometry=[];dg=bpy.context.evaluated_depsgraph_get()
for n in result['addedMeshes']:
 o=bpy.data.objects[n];ev=o.evaluated_get(dg);mesh=ev.to_mesh();bm=bmesh.new();bm.from_mesh(mesh);geometry.append({'name':n,'owner':o.parent.name,'closed':all(e.is_manifold for e in bm.edges),'volumeM3':bm.calc_volume(signed=True),'vertices':len(mesh.vertices)});assert geometry[-1]['closed'] and geometry[-1]['volumeM3']>0,n;bm.free();ev.to_mesh_clear()
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(M),check_existing=False);nativeSHA=sha(M);bpy.ops.wm.open_mainfile(filepath=str(M));bpy.context.view_layer.update()
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.get('authoringGuide') or o.type=='CURVE':o.hide_render=True
 elif o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
d=bpy.data.cameras.new('V37 temporary matched camera');d.type='ORTHO';c=bpy.data.objects.new(d.name,d);scene.collection.objects.link(c);scene.camera=c
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('shoulder-close',(-2.5,-1.8,1.7),(0,-.005,1.08),1.20)]
receipt={'status':'Coarse proposal pending actual visual gate','base':{'path':str(BASE.relative_to(R)),'sha256':sha(BASE)},'native':{'path':str(M.relative_to(R)),'sha256':nativeSHA},'source':{'path':str((A/'executed-shoulder-assembly.py').relative_to(R)),'sha256':sha(A/'executed-shoulder-assembly.py')},'result':result,'finiteGeometry':geometry,'views':[]}
for name,pos,target,scale in views:
 c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=scale;scene.render.filepath=str(A/f'after-{name}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({'path':str(Path(scene.render.filepath).relative_to(R)),'sha256':sha(scene.render.filepath),'position':pos,'target':target,'orthoScale':scale})
assert sha(M)==nativeSHA and sha(BASE)==receipt['base']['sha256'];(A/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('READY',nativeSHA,receipt['source']['sha256'],flush=True)
