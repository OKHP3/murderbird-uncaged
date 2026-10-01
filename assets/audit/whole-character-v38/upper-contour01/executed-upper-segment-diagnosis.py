import bpy,json,runpy
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];A=R/'assets/audit/whole-character-v38/upper-contour01';bpy.ops.wm.open_mainfile(filepath=str(R/'assets/models/whole-character-v38/upper-contour01/murderbird-v38-upper-contour01.blend'));rows=[]
groups=[('source18 collar',(1,.08,.05)),('fixed temporal wall',(.03,.18,1)),('formed lower cheek',(.75,.08,1)),('passive cranial bow',(.05,.8,.1)),('cervical guards',(1,.75,.02)),('other',(.45,.48,.5))]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 g=0 if 'tapered throat cheek' in o.name else 1 if 'fixed temporal receiving wall'in o.name else 2 if 'formed lower cheek'in o.name else 3 if 'passive cranial load bow'in o.name else 4 if 'V23 cervical'in o.name and 'directional guard'in o.name else 5
 o.color=(*groups[g][1],1);o.hide_render=o.get('authoringGuide') is True or 'builder'not in str(o.get('exteriorEras','maker,mechanic,builder')).split(',')
 if g<4:
  v=[o.matrix_world@p.co for p in o.data.vertices];rows.append({'name':o.name,'owner':o.parent.name,'group':groups[g][0],'bounds':[[min(p[k]for p in v),max(p[k]for p in v)]for k in range(3)]})
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';sh=s.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='OBJECT';sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=1200;s.render.resolution_percentage=100
ca=bpy.data.cameras.new('diagnostic source identity');ca.type='ORTHO';ca.ortho_scale=.68;cam=bpy.data.objects.new(ca.name,ca);s.collection.objects.link(cam);s.camera=cam;cam.location=(-7,0,2.1);cam.rotation_euler=(Vector((0,-.55,1.70))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=str(A/'upper-segment-identity.png');bpy.ops.render.render(write_still=True);(A/'upper-segment-identities.json').write_text(json.dumps({'groups':groups,'source':'Saved actual01, read-only object-color diagnostic; no model edits','meshes':rows},indent=2)+'\n')
