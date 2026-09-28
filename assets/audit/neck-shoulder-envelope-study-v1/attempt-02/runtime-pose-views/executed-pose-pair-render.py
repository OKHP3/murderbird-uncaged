from pathlib import Path
import hashlib,json,bpy
from mathutils import Matrix,Vector
ROOT=Path('/Users/okh/.codex/worktrees/review-regression/murderbird-uncaged')
POSE=ROOT/'assets/audit/neutral-runtime-clearance-poses-v1/pose-snapshot.json'
FILES={'baseline':ROOT/'assets/models/uncaged-alignment-v7/murderbird-alignment-v7.blend','study':ROOT/'assets/models/uncaged-neck-shoulder-envelope-study-v1/attempt-02/murderbird-v7-shoulder-envelope-study-v2.blend'}
OUT=ROOT/'assets/audit/neck-shoulder-envelope-study-v1/attempt-02/runtime-pose-views'
POSE_IDS=['advanced-thrust-brace','inspection-open-1-separation-0.5']
EXPECTED={'baseline':'a8fccaf024a096678415215029b34cae8270b348da2301b8872a34e72c75ed3f','study':'3bcba58d332fd691ebcfe9c6887f10532ee659bb0d3f32258e84b40b23f22229'}
POSE_SHA='874396ede48a63d37d743a1a85ae885a10e614a4461f46c50f3a62744a9e2813'
C=Matrix(((1,0,0,0),(0,0,1,0),(0,-1,0,0),(0,0,0,1)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def converted(flat):
 b=Matrix([[flat[col*4+row] for col in range(4)] for row in range(4)])
 return C.inverted()@b@C
def depth(o):
 n=0
 while o.parent is not None:n+=1;o=o.parent
 return n
def setpose(pose,pivots):
 rows={}
 for row in pose['pivotMatrices']:
  if row.get('kind')!='mesh':rows.setdefault(row['name'],[]).append(row)
 assert all(len(rows[n])==1 for n in pivots)
 for name in sorted(pivots,key=lambda n:depth(pivots[n])):
  pivots[name].matrix_world=converted(rows[name][0]['worldMatrix']);bpy.context.view_layer.update()
 return max(abs(pivots[n].matrix_world[r][c]-converted(rows[n][0]['worldMatrix'])[r][c]) for n in pivots for r in range(4) for c in range(4))
def setup():
 s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';q=s.display.shading;q.light='STUDIO';q.studio_light='paint.sl';q.color_type='SINGLE';q.single_color=(.52,.55,.57);q.show_shadows=True;q.show_cavity=True;q.cavity_type='BOTH';q.curvature_ridge_factor=1.25;q.curvature_valley_factor=1.15;q.background_type='WORLD';s.world.color=(.12,.13,.14);s.render.resolution_x=s.render.resolution_y=1100;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.film_transparent=False
 return s
def main():
 assert sha(POSE)==POSE_SHA and not OUT.exists();OUT.mkdir(parents=True)
 pd=json.loads(POSE.read_text());pm={x['id']:x for x in pd['poses']};records=[]
 for label,file in FILES.items():
  assert sha(file)==EXPECTED[label]
  for pid in POSE_IDS:
   bpy.ops.wm.open_mainfile(filepath=str(file));s=setup();pivots={o.name:o for o in bpy.data.objects if o.type=='EMPTY'};assert len(pivots)==51
   err=setpose(pm[pid],pivots);target=(pivots['neck'].matrix_world.translation+pivots['breastplate'].matrix_world.translation)*.5
   for o in bpy.data.objects:
    if o.type=='MESH':
     eras=[x.strip() for x in o.get('exteriorEras','maker,mechanic,builder').split(',')];o.hide_render='builder' not in eras;o.hide_set(False)
   cd=bpy.data.cameras.new('temporary runtime review camera');cam=bpy.data.objects.new('temporary runtime review camera',cd);s.collection.objects.link(cam);s.camera=cam
   for view,off in [('three-quarter',Vector((-3.2,-4.4,1.45))),('side',Vector((-5.2,0,.35)))]:
    cam.location=target+off;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cd.type='ORTHO';cd.ortho_scale=1.72;cd.lens=70;bpy.context.view_layer.update()
    path=OUT/f'{label}-{pid}-{view}.png';s.render.filepath=str(path);bpy.ops.render.render(write_still=True)
    records.append({'file':str(path.relative_to(ROOT)),'sha256':sha(path),'bytes':path.stat().st_size,'candidate':label,'nativeSha256':EXPECTED[label],'poseId':pid,'controllerState':pm[pid]['controller']['state'],'view':view,'poseMatrixErrorMax':err,'cameraLocationWorld':[float(x) for x in cam.location],'targetWorld':[float(x) for x in target],'orthoScale':cd.ortho_scale,'resolution':[1100,1100]})
   bpy.data.objects.remove(cam,do_unlink=True);bpy.data.cameras.remove(cd)
 report={'scope':'read-only matched pose renders; no native save','posePacketSha256':POSE_SHA,'poses':POSE_IDS,'renders':records,'limits':['Exact discrete runtime pivot matrices; not continuous clearance or performance proof.','Neutral Workbench images only; not browser/export or owner acceptance.']}
 (OUT/'review-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'rendered':len(records),'output':str(OUT)}))
main()
