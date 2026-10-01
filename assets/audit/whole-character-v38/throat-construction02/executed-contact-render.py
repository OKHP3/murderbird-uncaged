import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[4];AUDIT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {"path":str(p.relative_to(ROOT)),"bytes":p.stat().st_size,"sha256":sha(p)}
VIEWS=[('full-bird-three-quarter',(-6,-3.5,2.75),(0,-.08,1.03),2.4),('full-bird-profile',(-7,0,2.75),(0,-.08,1.03),2.4),('full-bird-front',(0,-7,2.75),(0,-.08,1.03),2.4),('full-bird-rear',(0,7,2.75),(0,-.08,1.03),2.4)]
VIEWS += [('head-three-quarter',(-5,-3.8,2.1),(0,-.55,1.70),.68),('head-profile',(-7,0,2.1),(0,-.55,1.70),.68)]
POSES={'actual-contact':{'neck':.12030544281,'cervical-mid-a':.12030544281,'cervical-mid-b':.12030544281,'cervical-upper':.12030544281,'head':-.56326345756,'jaw':.02539279294}}
def render_views(prefix,views):
 scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.get('authoringGuide') is True or 'builder' not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
 scene.render.resolution_x=scene.render.resolution_y=1200;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('temporary matched throat construction review');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera;records=[]
 for name,pos,target,scale in views:
  camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale
  path=AUDIT/f'{prefix}-{name}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
  records.append({**art(path),'camera':{'position':pos,'target':target,'orthoScale':scale},'size':[1200,1200],'render':'neutral Workbench single color, no cast shadows'})
  print('MEDIA',str(path),flush=True)
 bpy.data.objects.remove(camera,do_unlink=True);bpy.data.cameras.remove(data);scene.camera=None
 return records

def render_pose(path,prefix):
 records=[]
 for label,angles in POSES.items():
  bpy.ops.wm.open_mainfile(filepath=str(path))
  for owner,angle in angles.items():o=bpy.data.objects[owner];o.matrix_basis=o.matrix_basis@Matrix.Rotation(angle,4,'X')
  bpy.context.view_layer.update();records+=render_views(prefix+'-'+label,[VIEWS[4]])
 return records


rows=[]
for label,path in [('baseline',ROOT/'assets/models/whole-character-v38/bill-relationship02/murderbird-v38-bill-relationship02.blend'),('candidate',ROOT/'assets/models/whole-character-v38/throat-construction02/murderbird-v38-throat-construction02.blend')]:
 pinned=sha(path);bpy.ops.wm.open_mainfile(filepath=str(path))
 for owner,angle in POSES['actual-contact'].items():o=bpy.data.objects[owner];o.matrix_basis=o.matrix_basis@Matrix.Rotation(angle,4,'X')
 bpy.context.view_layer.update();rows+=render_views(label+'-actual-contact',[VIEWS[0]]);assert sha(path)==pinned
(AUDIT/'contact-render-receipt.json').write_text(json.dumps(rows,indent=2)+'\n')
