from pathlib import Path
import bpy,runpy,json,math,hashlib,shutil
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
OUT=Path('/tmp/v27-neck-guide/coarse01');ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged');native=OUT/'murderbird-v27-neck-guide.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();mod=runpy.run_path(str(OUT/'executed-region.py'));tools=runpy.run_path(str(OUT/'pose-screen.py'),run_name='tooling');tools['configure'].__globals__['BASE']=native;tools['configure']();carrier=bpy.data.objects[mod['NAME']];contract=json.loads(carrier['cervicalGuardGuideV1']);paths=json.loads(carrier['guidePaths']);necrest=bpy.data.objects['neck'].matrix_world.copy();midrest=bpy.data.objects['cervical-mid-a'].matrix_world.copy();owned=set(mod['GUARDS']);new=set(json.loads((OUT/'receipt.json').read_text())['result']['addedMeshes'])
def distance(p,line):
 vals=[]
 for a,b in zip(line,line[1:]):
  d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared)) if d.length_squared>1e-14 else 0;vals.append((p-a-d*t).length)
 return min(vals)
def endpoint(o,first):
 verts=list(o.data.vertices);pts=verts[:8] if first else verts[-8:];return o.matrix_world@(sum((v.co for v in pts),Vector())/len(pts))
def sample(state):
 tools['pose'](state);theta=mod['proof_update']();dg=bpy.context.evaluated_depsgraph_get();items=[]
 for o in bpy.data.objects:
  if o.type!='MESH' or not o.parent:continue
  guard=o.name.startswith('V23 cervical ') and 'directional guard' in o.name;hardware=o.name in new
  neighbor=o.parent.name in tools['OWNERS']+['upper-bill','cranial-cover','builder-optics','body','breastplate'] and o.get('surfaceRole') in ['plate','shell','guard','recess','frame','edge','bearing']
  if not(guard or hardware or neighbor):continue
  if 'builder' not in o.get('exteriorEras','maker,mechanic,builder').split(','):continue
  v,t=mod['meshworld'](o);items.append((o.name,o.parent.name,guard,hardware,tools['bounds'](v),mod['tri'](v,t)))
 pairs=[]
 for i,a in enumerate(items):
  for b in items[i+1:]:
   if a[1]==b[1] or not(a[2] or b[2] or a[3] or b[3]) or any(a[4][1][k]<b[4][0][k] or b[4][1][k]<a[4][0][k] for k in range(3)):continue
   hits=mod['crossing'](a[5],b[5])
   if hits:
    category='hardware-hardware' if a[3] and b[3] else 'hardware-original' if a[3] or b[3] else 'moved-guard-original' if a[0] in owned or b[0] in owned else 'inherited-other-guard'
    pairs.append({'a':a[0],'b':b[0],'owners':[a[1],b[1]],'category':category,'strictTriangleWitnesses':hits})
 errs=[]
 for path in paths:
  p=carrier.matrix_world@Vector(path['localPin']);transform=bpy.data.objects['neck'].matrix_world@necrest.inverted() if path['kind']=='fixed-guide' else bpy.data.objects['cervical-mid-a'].matrix_world@midrest.inverted();line=[transform@Vector(v) for v in path['worldRestPath']];errs.append({'kind':path['kind'],'followerToSlotPolylineM':distance(p,line)})
 rod=bpy.data.objects['V27 mid-a rigid push-pull member'];lug=carrier.matrix_world@Vector(json.loads(carrier['pushPullLug']));cam=carrier.matrix_world@Vector(json.loads(carrier['camFollower']));ends={'carrierClevisErrorM':(endpoint(rod,True)-lug).length,'camClevisErrorM':(endpoint(rod,False)-cam).length,'pushPullLengthM':(endpoint(rod,True)-endpoint(rod,False)).length}
 return {'pose':state[0],'angles':list(state[1:]),'driverAngle':theta,'guideTranslation':list(mod['_interpolate'](contract['law'],theta)),'pairs':pairs,'categories':{c:sum(p['category']==c for p in pairs) for c in ['moved-guard-original','inherited-other-guard','hardware-hardware','hardware-original']},'connections':ends,'slotCenters':errs}
rows=[];states=tools['STATES']+[('sweep-p%.5f-y%.2f'%(q,y),q,y,0,0) for q in [-.14+(.65+.14)*i/40 for i in range(41)] for y in [-.45,0,.45]]
for i,state in enumerate(states):
 rows.append(sample(state))
 if i%10==0:print('SCREEN',i,rows[-1]['categories'],flush=True)
 (OUT/'strict-sweep.json').write_text(json.dumps({'method':'Evaluated crossowner strict mutual plane-straddle triangle witnesses epsilon1e-7; finite poses only. Hardware interfaces included; structural design/physics not proven.','poses':rows},indent=2)+'\n')
# An actual isolated hardware view makes the coarse captive paths inspectable.
tools['pose'](('rest',0,0,0,0));mod['proof_update']();scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render=o.name not in new
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V27 coarse hardware camera');d.type='ORTHO';d.ortho_scale=.18;cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-3,-2,1.62);cam.rotation_euler=(Vector((-.075,-.268,1.434))-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/'rest-hardware-isolated.png');bpy.ops.render.render(write_still=True)
summary={'sourceSha256':sha(OUT/'executed-region.py'),'nativeSha256':sha(native),'sampledPoses':len(rows),'maxSlotCenterDeviationM':max(e['followerToSlotPolylineM'] for r in rows for e in r['slotCenters']),'maxPushPullEndpointErrorM':max(max(r['connections']['carrierClevisErrorM'],r['connections']['camClevisErrorM']) for r in rows),'pushPullLengthRangeM':[min(r['connections']['pushPullLengthM'] for r in rows),max(r['connections']['pushPullLengthM'] for r in rows)],'sevenPoseCategories':[{k:r[k] for k in ['pose','categories']} for r in rows[:7]],'denseMovedGuardMaxPairs':max(r['categories']['moved-guard-original'] for r in rows[7:]),'denseHardwareMaxPairs':max(r['categories']['hardware-hardware']+r['categories']['hardware-original'] for r in rows[7:])};(OUT/'sweep-summary.json').write_text(json.dumps(summary,indent=2)+'\n');shutil.copyfile(__file__,OUT/'executed-screen.py');print(json.dumps(summary),flush=True)
