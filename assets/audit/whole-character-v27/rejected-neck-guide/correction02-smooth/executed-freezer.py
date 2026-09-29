from pathlib import Path
import bpy,runpy,json,hashlib,shutil
from mathutils import Vector,Matrix
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');OUT=Path('/tmp/v27-neck-guide/correction02-smooth');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();native=OUT/'murderbird-v27-neck-guide.blend';mod=runpy.run_path(str(OUT/'executed-region.py'));tools=runpy.run_path(str(OUT/'pose-screen.py'),run_name='tooling');tools['configure'].__globals__['BASE']=native;tools['configure']();rows=json.loads((OUT/'strict-sweep.json').read_text())['poses'];worst=max((r for r in rows if r['pose'].startswith('sweep-') and -.14<r['angles'][0]<.65),key=lambda r:(r['categories']['moved-guard-original'],sum(p['strictTriangleWitnesses'] for p in r['pairs'] if p['category']=='moved-guard-original')));tools['pose']((worst['pose'],*worst['angles']));mod['proof_update']();scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V27 final diagnosis camera');d.type='ORTHO';cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;new=set(json.loads((OUT/'receipt.json').read_text())['result']['addedMeshes'])
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
d.ortho_scale=1.4;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.48))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'worst-interior-range-neck.png');bpy.ops.render.render(write_still=True);(OUT/'worst-interior-range.json').write_text(json.dumps(worst,indent=2)+'\n')
for label,state in [('rest',('rest',0,0,0,0)),('interior',(worst['pose'],*worst['angles'])),('contact',('contact-neck',.65,0,-.731,.10))]:
 tools['pose'](state);mod['proof_update']()
 for o in bpy.data.objects:
  if o.type=='MESH':o.hide_render=o.name not in new
 d.ortho_scale=.30;cam.location=(-3,-2,1.62);cam.rotation_euler=(Vector((-.055,-.290,1.436))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/f'{label}-hardware-complete.png');bpy.ops.render.render(write_still=True)
# Exact strict witnesses at a relevant actual contact posture.
tools['pose'](('contact-neck',.65,0,-.731,.10));mod['proof_update']();contact=next(r for r in rows if r['pose']=='contact-neck');selected=[p for p in contact['pairs'] if p['category']=='moved-guard-original']+[p for p in contact['pairs'] if p['category'].startswith('hardware')][:6];inv=bpy.data.objects['cervical-mid-a'].matrix_world.inverted();witness=[]
for pair in selected:
 a=mod['tri'](*mod['meshworld'](bpy.data.objects[pair['a']]));b=mod['tri'](*mod['meshworld'](bpy.data.objects[pair['b']]));points=[];first=None
 for i,j in a[2].overlap(b[2]):
  A=[a[0][n] for n in a[1][i]];B=[b[0][n] for n in b[1][j]]
  if mod['straddle'](A,B) and mod['straddle'](B,A):
   points.extend(inv@p for p in A+B)
   if first is None:first=[[list(inv@p) for p in A],[list(inv@p) for p in B]]
 witness.append({**pair,'relativeToJoint':'cervical-mid-a','strictWitnessVertexBoundsM':tools['bounds'](points),'firstStrictTrianglesJointLocal':first})
(OUT/'contact-failure-witnesses.json').write_text(json.dumps({'method':'Exact evaluated mutual plane-straddle triangle witnesses; bounds are triangle-vertex bounds, not penetration depths.','pairs':witness},indent=2)+'\n')
receipt=json.loads((OUT/'receipt.json').read_text());receipt['decision']={'status':'HOLD; failed gate; no replication or runtime integration','appearance':'Directionally layered S-shaped guard forms preserved; root judged initial preview useful.','coarseResidual':'Moving course2 guard2/4 crossed static same-course flank guards1/5; two pairs at contact.','correctedResidual':'Smooth full-angle forward travel clears those flank seam pairs but trades them for six upper-course pairs at contact: each moving front guard2/3/4 vs same sector in courses3/4.','hardwareFailure':'Rigid endpoints remain connected to the authored slot trajectory, but rail/roller/web/push-pull material intersections remain. Endpoint coincidence is not captive-solid clearance.','inheritedOtherHinges':'Untouched guard/head/body crossings and visual opening at other hinges classified separately, not repaired or attributed to this mechanism.','limitedCorrection':'One correction, plus its analytic interpolation implementation fix, preserved separately; no extension.'};receipt['sweepSummary']=json.loads((OUT/'sweep-summary.json').read_text());receipt['worstInteriorRange']={'pose':worst['pose'],'angles':worst['angles'],'categories':worst['categories']};(OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-freezer.py')
for folder in [Path('/tmp/v27-neck-guide/coarse01'),Path('/tmp/v27-neck-guide/correction02'),OUT]:
 (folder/'manifest.json').write_text(json.dumps({'status':'HOLD; not in integrated model','files':{p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.name!='manifest.json'}},indent=2)+'\n')
print(json.dumps({'sourceSha256':sha(OUT/'executed-region.py'),'nativeSha256':sha(native),'worstInteriorRange':worst['pose'],'status':'HOLD'}),flush=True)
