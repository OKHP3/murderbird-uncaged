"""Read-only matched renders for the owner's September 28 progress checkpoint."""
from pathlib import Path
import bpy,hashlib,json,shutil
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/audit/supervisor-checkpoint-2026-09-28'
OUT.mkdir(parents=True,exist_ok=True)
assert not (OUT/'render-manifest.json').exists(),'Do not overwrite a frozen checkpoint'
shutil.copy2(__file__,OUT/'executed-render.py')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
models=[('inspection-baseline','assets/models/uncaged-exterior-v1/murderbird-exterior-v1.blend'),
        ('selected-v9','assets/models/uncaged-alignment-v9/murderbird-alignment-v9.blend')]
views=[('three-quarter',(-3.8,-6,3.2),(0,-.08,.98),2.55),
       ('profile',(-7.5,0,1.25),(0,-.08,.98),2.55),
       ('head',(-3.4,-5,2.05),(0,-.27,1.72),.85)]
for label,rel in models:
    source=ROOT/rel;digest=sha(source);assert source.stat().st_size>100000
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60)
    s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
    scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    for o in bpy.data.objects:
        if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',');o.hide_set(False)
    cd=bpy.data.cameras.new('Checkpoint matched camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO'
    for name,pos,target,scale in views:
        cam.location=Vector(pos);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=scale
        out=OUT/f'{label}-{name}.png';scene.render.filepath=str(out);bpy.ops.render.render(write_still=True)
        records.append({'label':label,'source':rel,'sourceSha256':digest,'view':name,'file':out.name,'sha256':sha(out),'camera':{'position':pos,'target':target,'orthoScale':scale},'era':'builder','lighting':'neutral Workbench; no finished materials','scope':'native rest geometry; runtime mechanisms not included'})
    assert sha(source)==digest
(OUT/'render-manifest.json').write_text(json.dumps({'status':'read-only matched comparison','views':records,'limits':['Inspection baseline is the historical exterior-v1 model, not a newly retrieved deployed response.','The selected V9 native and held neck V2 remain distinct.','Same camera, scale and neutral light; no image warp or geometry normalization.','This qualitative comparison does not establish a likeness score or acceptance.']},indent=2)+'\n')
