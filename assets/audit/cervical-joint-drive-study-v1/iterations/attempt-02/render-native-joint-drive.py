"""Render six neutral close-up views of the immutable attempt-02 native."""
from pathlib import Path
import hashlib, json
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[5]
NATIVE=ROOT/'assets/models/uncaged-cervical-joint-drive-study-v1/iterations/attempt-02/murderbird-cervical-joint-drive-study-v1.blend'
EXPECTED='dff9cf74e0b10819f86efed1bdf5c292ae38619d962d18afeba2b2cca291b9d1'
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sha(NATIVE)!=EXPECTED:raise RuntimeError('Pinned native hash mismatch')
if any((OUT/f'{n}.png').exists() for n in ('joint-right','joint-left','era-maker','era-mechanic','era-advanced')):raise RuntimeError('Refusing to overwrite renders')
bpy.ops.wm.open_mainfile(filepath=str(NATIVE));scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='MATERIAL';s.show_shadows=True;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.11,.12,.13)
scene.render.resolution_x=1000;scene.render.resolution_y=850;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
cd=bpy.data.cameras.new('Joint drive review camera');cam=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(cam);scene.camera=cam;cd.type='ORTHO';target=Vector((0,-.235,1.452))
views=[('joint-right',Vector((-2.6,-3.1,1.9)),None),('joint-left',Vector((2.6,-3.1,1.9)),None),('era-maker',Vector((-2.6,-3.1,1.9)),'maker'),('era-mechanic',Vector((-2.6,-3.1,1.9)),'mechanic'),('era-advanced',Vector((2.6,-3.1,1.9)),'builder')]
rows=[]
for name,pos,era in views:
    for o in bpy.data.objects:
        if o.type=='MESH':
            allowed=o.get('exteriorEras','maker,mechanic,builder').split(',')
            o.hide_render=bool(era and era not in allowed)
    cam.location=target+pos;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.ortho_scale=.62
    p=OUT/f'{name}.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
    rows.append({'file':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'era':era or 'all','cameraOffsetFromTarget':list(pos),'target':list(target),'orthoScale':.62})
(OUT/'render-manifest.json').write_text(json.dumps({'nativeSha256':EXPECTED,'views':rows,'method':'Neutral Blender Workbench stills; authoring views only.'},indent=2)+'\n')
print(json.dumps(rows,indent=2))
