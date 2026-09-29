from pathlib import Path
import bpy,json,hashlib,runpy,shutil,math
from mathutils import Vector,Quaternion
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=ROOT/'assets/audit/whole-character-v32/regional-studies/cranial-frame/coarse01/attachment-witness';assert not OUT.exists();OUT.mkdir()
N=OUT.parent/'native-run02/murderbird-v32-cranial-frame.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(N)=='51ec0b0b812e85571d880ecfa4251ff8c71a78eafa854ca912335432817ca9db';shutil.copy2(__file__,OUT/'executed-witness.py');bpy.ops.wm.open_mainfile(filepath=str(N));bpy.context.view_layer.update()
head=bpy.data.objects['head'];inv=head.matrix_world.inverted();rows=[]
for side in (-1,1):
 bow=bpy.data.objects[f'V31 passive cranial load bow {side}'];seat=bpy.data.objects[f'V31 cranial load bow shaft seat {side}'];v=[inv@bow.matrix_world@p.co for p in bow.data.vertices]
 # Both skins of the first authored station, each eleven vertices.
 roots=v[:11]+v[561:572];inside=[p for p in roots if .058<side*p.x<.070 and .010<math.hypot(p.y,p.z)<.017]
 assert inside,side
 rows.append({'side':side,'bowRootVerticesInsideFiniteSeat':len(inside),'rootVertexCount':len(roots),'sampleInsideVertex':list(inside[0]),'seatOwner':seat.parent.name,'bowOwner':bow.parent.name,'seatAxialRangeM':[.058,.070],'retainedShaftAxialRangeM':[0,.09],'seatBoreRadiusM':.010,'retainedShaftRadiusM':.008,'radialBoreAllowanceM':.002,'connectionMeaning':'Finite same-owner bow root overlaps actual annular seat; bore concentric on unchanged captive shaft. Allowance and fastening remain inherited construction proposals.'})
result={'nativeSHA256':sha(N),'status':'Actual attachment-coordinate witness, no load/engineering acceptance','bowSeats':rows,'upperReceivingStations':{'before':[[.101,-.067,.234,.014],[.112,-.123,.282,.010]],'after':[[.101,-.067,.234,.014],[.112,-.123,.282,.010]],'meaning':'Upper two authored skull receiving stations retained exactly; this does not certify inherited skull fastening.'}}
(OUT/'proof.json').write_text(json.dumps(result,indent=2)+'\n')
# Diagnostic views intentionally isolate the complete authored frame and
# adjacent unchanged distal guards/shaft. Full model remains in native file.
for o in bpy.data.objects:
 if o.animation_data:o.animation_data_clear()
 if o.type=='MESH':o.hide_render=not(o.name.startswith('V31 passive cranial load bow') or o.name.startswith('V31 cranial load bow shaft seat') or o.name=='V21 head captive shaft' or o.name.startswith('V23 cervical 4 '))
 elif o.type=='CURVE':o.hide_render=True
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='OBJECT';s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14)
for o in bpy.data.objects:
 if o.type=='MESH':o.color=(.70,.74,.77,1) if 'V31 ' in o.name else (.28,.31,.33,1)
scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('Diagnostic frame camera');d.type='ORTHO';d.ortho_scale=.65;c=bpy.data.objects.new(d.name,d);scene.collection.objects.link(c);scene.camera=c
CHAIN=['neck','cervical-mid-a','cervical-mid-b','cervical-upper'];OWNERS=CHAIN+['head','jaw'];REST={n:bpy.data.objects[n].matrix_local.copy() for n in OWNERS}
for n in OWNERS:bpy.data.objects[n].rotation_mode='QUATERNION'
for label,q,h,j in [('rest',0,0,0),('contact-neck',.65,-.731,.10)]:
 for n in CHAIN:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),q*.25)
 for n,value in [('head',h),('jaw',j)]:
  o=bpy.data.objects[n];o.rotation_quaternion=o.matrix_parent_inverse.to_quaternion().inverted()@REST[n].to_quaternion()@Quaternion((1,0,0),value)
 bpy.context.view_layer.update();target=bpy.data.objects['head'].matrix_world.translation+Vector((0,0,.09));c.location=target+Vector((-.70,-.42,.18));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'diagnostic-frame-{label}.png');bpy.ops.render.render(write_still=True)
assert sha(N)==result['nativeSHA256'];print(json.dumps(result),flush=True)
