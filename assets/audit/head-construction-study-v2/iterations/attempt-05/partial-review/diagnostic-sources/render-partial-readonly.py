import bpy,hashlib,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
source=ROOT/'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend'
candidate=ROOT/'assets/models/uncaged-head-construction-study-v2/iterations/attempt-05/murderbird-head-construction-study-v2-partial.blend'
outdir=ROOT/'assets/audit/head-construction-study-v2/iterations/attempt-05/partial-review'
cams=[
 {'name':'front-bilateral','position':(0,-6,1.78),'target':(0,-.30,1.78),'ortho':1.05},
 {'name':'anatomical-right-profile','position':(-6,-.30,1.78),'target':(0,-.30,1.78),'ortho':1.10},
 {'name':'three-quarter-a','position':(-6,-3,2.4),'target':(0,-.29,1.78),'ortho':.88},
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results={}
for phase,path in [('before',source),('after',candidate)]:
 bpy.ops.wm.open_mainfile(filepath=str(path)); scene=bpy.context.scene;scene.frame_set(1)
 scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='MATERIAL'
 sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.2;sh.curvature_valley_factor=1.1
 sh.background_type='WORLD';scene.world.color=(.11,.12,.13);scene.render.resolution_x=1100;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 for o in scene.objects:
  if o.type=='MESH': o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  o.hide_set(False)
 camdata=bpy.data.cameras.new('Attempt05 read-only camera');cam=bpy.data.objects.new('Attempt05 read-only camera',camdata);scene.collection.objects.link(cam);scene.camera=cam
 for spec in cams:
  cam.location=spec['position'];cam.rotation_euler=(Vector(spec['target'])-cam.location).to_track_quat('-Z','Y').to_euler();camdata.type='ORTHO';camdata.ortho_scale=spec['ortho']
  p=outdir/f'{phase}-{spec["name"]}.png';scene.render.filepath=str(p);bpy.ops.render.render(write_still=True)
  results[f'{phase}-{spec["name"]}']={'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,'camera':{**spec,'projection':'ORTHO','resolution':[1100,1100]}}
receipt={'title':'Read-only static views of held attempt05 partial native','status':'held diagnostic; not final candidate or art acceptance','source':{'path':str(source.relative_to(ROOT)),'sha256':sha(source)},'partialCandidate':{'path':str(candidate.relative_to(ROOT)),'sha256':sha(candidate),'bytes':candidate.stat().st_size},'renderMethod':'Blender Workbench neutral authoring view; same cameras before/after','views':results,'limits':['Not the final validated candidate; late checks did not complete.','Static authoring views only; no integration, runtime or motion claims.']}
(outdir/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
