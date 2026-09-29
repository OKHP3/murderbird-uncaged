"""Write-once coordinated rest-proportion study. Not a runtime-ready rebuild.

Reshapes rigid components in authoring space; no animated metal deformation.
Native Z up / -Y front. Preserve source model, head and foot geometry, circular
bearing radii, part ownership, and the existing asymmetric articulation tree.
"""
from pathlib import Path
import argparse,hashlib,json,math,runpy,shutil,sys
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/whole-character-v21/attempt-construction06/murderbird-whole-character-v21.blend'
BASE_SHA='79ad3e368e7b75edbbc758b1264a1ccaf34f284c6ca185ee8441875576a6f54c'
p=argparse.ArgumentParser();p.add_argument('--attempt',required=True);p.add_argument('--leg-scale',type=float,default=.84);p.add_argument('--neck-rise',type=float,default=.11);p.add_argument('--head-forward',type=float,default=.065);p.add_argument('--body-width',type=float,default=.90);p.add_argument('--leg-frame',action='store_true')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);assert a.attempt.replace('-','').isalnum();assert .65<a.leg_scale<=1 and 0<=a.neck_rise<.25 and 0<a.body_width<=1
AUDIT=ROOT/f'assets/audit/whole-character-v22/attempt-{a.attempt}';OUT=ROOT/f'assets/models/whole-character-v22/attempt-{a.attempt}'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def art(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def smooth(z,stops):
 if z<=stops[0][0]:return stops[0][1]
 for (z0,v0),(z1,v1) in zip(stops,stops[1:]):
  if z<=z1:return v0+(v1-v0)*ease((z-z0)/(z1-z0))
 return stops[-1][1]
def depth(o):
 n=0
 while o.parent:n+=1;o=o.parent
 return n
def within(o,name):
 while o:
  if o.name==name:return True
  o=o.parent
 return False
assert sha(BASE)==BASE_SHA and not AUDIT.exists() and not OUT.exists()
AUDIT.mkdir(parents=True);OUT.mkdir(parents=True);shutil.copyfile(__file__,AUDIT/'executed-builder.py')
h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'))
bpy.ops.wm.open_mainfile(filepath=str(BASE));initial=h['scene_snapshot']();materials={m.name:h['material_signature'](m) for m in bpy.data.materials};module=None
if a.leg_frame:
 src=ROOT/'scripts/regions/whole-character-v22-leg-frame.py';shutil.copyfile(src,AUDIT/'executed-leg-frame.py');module=runpy.run_path(str(AUDIT/'executed-leg-frame.py'))['apply']()
old={o.name:o.matrix_world.copy() for o in bpy.data.objects};oldverts={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.data.objects if o.type=='MESH'}
headset={o.name for o in bpy.data.objects if within(o,'head')};feet={o.name for o in bpy.data.objects if within(o,'left-foot') or within(o,'right-foot')}
shortening=(.875-.330)*(1-a.leg_scale)
head_delta=Vector((0,-.08*old['head'].translation.y-a.head_forward,a.neck_rise-shortening))
def frame_point(point):
 x,y,z=point
 # Foot pivot and complete foot/toe assemblies stay fixed. Above the hip the
 # torso shifts as a unit; upper neck length is then restored separately.
 if z<=.330:nz=z
 elif z<=.875:nz=.330+(z-.330)*a.leg_scale
 else:nz=z-shortening
 nz+=a.neck_rise*max(0,min(1,(z-1.300)/.280))
 body_weight=smooth(z,[(.60,0),(.875,1),(1.30,1),(1.58,0)])
 nx=x*(1+(a.body_width-1)*body_weight)
 # One uniform fore/aft body mapping avoids introducing a waist-like ridge
 # across the breast or a kink through a wing plate field.
 ny=y*.92
 ny+=smooth(z,[(1.30,0),(1.455,.020),(1.58,-a.head_forward)])
 return Vector((nx,ny,nz))
def point_for(name,p):
 if name in feet:return p.copy()
 if name in headset:return p+head_delta
 return frame_point(p)
# Edit the rest centers top-down, restoring every object's own new world basis
# so a parent edit cannot accumulate twice in a descendant.
for o in sorted(bpy.data.objects,key=depth):
 m=old[o.name].copy();m.translation=point_for(o.name,m.translation);o.matrix_world=m;bpy.context.view_layer.update()
round_kept=[];head_error=0;foot_error=0
for o in bpy.data.objects:
 if o.type!='MESH':continue
 inv=o.matrix_world.inverted();pts=oldverts[o.name];center=sum(pts,Vector())/len(pts)
 circular=o.get('surfaceRole','')=='bearing' and o.name not in headset and o.name not in feet
 if circular:round_kept.append(o.name)
 mapped_center=point_for(o.name,center)
 for v,p0 in zip(o.data.vertices,pts):
  target=mapped_center+(p0-center) if circular else point_for(o.name,p0)
  v.co=inv@target
 o.data.update()
 if o.name in headset:
  head_error=max(head_error,max(((o.matrix_world@v.co)-(p0+head_delta)).length for v,p0 in zip(o.data.vertices,pts)))
 if o.name in feet:
  foot_error=max(foot_error,max(((o.matrix_world@v.co)-p0).length for v,p0 in zip(o.data.vertices,pts)))
# Check protected regions again after every mesh has been processed, so shared
# mesh data cannot silently invalidate an earlier per-object check.
for name in headset|feet:
 o=bpy.data.objects[name]
 if o.type=='MESH':
  delta=head_delta if name in headset else Vector()
  assert max(((o.matrix_world@v.co)-(p0+delta)).length for v,p0 in zip(o.data.vertices,oldverts[name]))<2e-6,name
# Historical authoring curves retain exact world poses, and remain hidden in
# review renders. They are deliberately not treated as new manufacturing guides.
for o in bpy.data.objects:
 if o.type=='CURVE':o.matrix_world=old[o.name]
body=bpy.data.objects['body']
for key in ('mechanismLayoutV1','sharedEnvelopeV21'):
 if key in body:body['priorV21_'+key]=body[key];del body[key]
body['v22ConstructionStatus']='Visual rest-proportion proposal only. Mechanism sockets, load-member endpoints, journal fits and motion clearances require reconstruction/rederivation before runtime export.'
body['v22RestMapping']=json.dumps({'footFixedTop':.330,'hipSource':.875,'legScale':a.leg_scale,'torsoDrop':shortening,'neckRise':a.neck_rise,'headRigidDelta':list(head_delta),'bodyWidthFactor':a.body_width,'method':'baked static authoring reshape, rigid animation owners retained'},separators=(',',':'))
bpy.context.view_layer.update();after=h['scene_snapshot']();assert set(initial['empties'])==set(after['empties']);assert all(initial['empties'][n]['parent']==after['empties'][n]['parent'] for n in initial['empties']);assert materials=={m.name:h['material_signature'](m) for m in bpy.data.materials};assert head_error<2e-6 and foot_error<2e-6
finite=[];deps=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
 if o.type=='MESH':
  e=o.evaluated_get(deps);m=e.to_mesh();assert all(math.isfinite(c) for v in m.vertices for c in v.co),o.name;finite.append(o.name);e.to_mesh_clear()
native=OUT/'murderbird-whole-character-v22.blend';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False);bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
receipt={'status':'rest silhouette study; not runtime or joint-clearance acceptance','base':art(BASE),'native':art(native),'source':art(AUDIT/'executed-builder.py'),'parameters':vars(a),'legFrameModule':module,'construction':json.loads(bpy.data.objects['body']['v22RestMapping']),'checks':{'finiteMeshes':len(finite),'namedParentsPreserved':len(initial['empties']),'headRigidTranslationError':head_error,'feetUnchangedWorldError':foot_error,'bearingMeshesKeptCircular':len(round_kept),'materialsExact':True,'saveReopenExact':True},'roundBearingMeshes':round_kept,'pivots':{n:{'before':list(old[n].translation),'after':list(bpy.data.objects[n].matrix_world.translation),'parent':bpy.data.objects[n].parent.name if bpy.data.objects[n].parent else None} for n in initial['empties']},'limits':['Point mapping is an authorial proportion proposal, not a dimension recovered from a perspective illustration.','Static rest reshaping does not stretch metal during animation. Each surface remains attached to one rigid owner.','Preserving bearing radii may create new interfaces needing explicit refitting.','Old mechanism sockets are preserved as historical metadata and removed from active metadata to prevent accidental runtime use.','No GLB, browser selection, publication or artistic acceptance from this script.'],'views':[]}
receipt_path=AUDIT/'receipt.json'
views=[('reference-angle',(-6,-3.5,2.75),(0,-.08,1.02),2.5),('front',(0,-7,1.65),(0,-.08,1.02),2.5),('side',(-7,0,1.35),(0,-.08,1.02),2.5),('rear',(0,7,1.65),(0,-.08,1.02),2.5),('neck',(-6,-3.5,2.45),(0,-.27,1.48),1.30)]
for label,path in [('after',native),('before',BASE)]:
 bpy.ops.wm.open_mainfile(filepath=str(path));scene=bpy.context.scene
 for o in bpy.data.objects:
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
  elif o.type=='CURVE':o.hide_render=True
 scene.render.engine='BLENDER_WORKBENCH';sh=scene.display.shading;sh.light='STUDIO';sh.studio_light='paint.sl';sh.color_type='SINGLE';sh.single_color=(.56,.58,.60);sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 data=bpy.data.cameras.new('Temporary V22 matching camera');data.type='ORTHO';camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera);scene.camera=camera
 for name,pos,target,scale in views:
  camera.location=pos;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();data.ortho_scale=scale;scene.render.filepath=str(AUDIT/f'{label}-{name}.png');bpy.ops.render.render(write_still=True);receipt['views'].append({**art(Path(scene.render.filepath)),'camera':{'position':pos,'target':target,'orthoScale':scale},'lighting':'neutral Workbench no cast shadows'});receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
assert sha(BASE)==BASE_SHA and sha(native)==receipt['native']['sha256'];print(json.dumps({'native':receipt['native'],'checks':receipt['checks'],'views':len(receipt['views'])}))
