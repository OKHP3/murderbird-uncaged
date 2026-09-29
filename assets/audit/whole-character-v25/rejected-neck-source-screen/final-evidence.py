from pathlib import Path
import bpy,runpy,json,hashlib
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OUT=Path('/tmp/v25-neck-laps/attempt02');tools=runpy.run_path('/tmp/v25-neck-laps/baseline.py',run_name='tooling');tools['configure']();bpy.ops.wm.open_mainfile(filepath=str(OUT/'neck-laps.blend'));r=json.loads((OUT/'receipt.json').read_text());old=json.loads(Path('/tmp/v25-neck-laps/baseline.json').read_text());key=lambda p:tuple(sorted((p['a'],p['b'])));comparison=[]
for before,after in zip(old['poses'],r['poses']):
 b={key(x):x for x in before['pairs']};a={key(x):x for x in after['pairs']};comparison.append({'pose':after['pose'],'beforePairCount':len(b),'afterPairCount':len(a),'introducedPairs':[a[k] for k in sorted(a.keys()-b.keys())],'removedPairs':[b[k] for k in sorted(b.keys()-a.keys())],'retainedPairs':[a[k] for k in sorted(a.keys()&b.keys())]})
(OUT/'comparison.json').write_text(json.dumps({'method':'evaluated triangle BVH filtered by mutual noncoplanar plane-straddle epsilon1e-7m; counts are witnesses not depth','baseSHA256':old['baseSha256'],'sourceSHA256':r['sourceSha256'],'poses':comparison},indent=2)+'\n')
examples=[('rest','V23 cervical 1 directional guard 5','V23 cervical 2 directional guard 6','cervical-mid-a','neck'),('contact-neck','V23 cervical 1 directional guard 3','V23 cervical 2 directional guard 3','cervical-mid-a','neck'),('contact-neck','V23 cervical 1 directional guard 3','V24 breast course 01 panel 03','neck','body')];witnesses=[]
for state,a,b,axis,frame in examples:
 tools['pose'](next(s for s in tools['STATES'] if s[0]==state));parts=[];dg=bpy.context.evaluated_depsgraph_get()
 for n in (a,b):
  o=bpy.data.objects[n];ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();v=[ev.matrix_world@x.co for x in m.vertices];tri=[tuple(t.vertices) for t in m.loop_triangles];parts.append((v,tri,BVHTree.FromPolygons(v,tri,all_triangles=True)));ev.to_mesh_clear()
 va,ta,ba=parts[0];vb,tb,bb=parts[1];points=[];count=0
 for i,j in ba.overlap(bb):
  A=[va[n] for n in ta[i]];B=[vb[n] for n in tb[j]]
  if tools['straddle'](A,B) and tools['straddle'](B,A):points.extend(A+B);count+=1
 if points:
  inv=bpy.data.objects[frame].matrix_world.inverted();centre=inv@bpy.data.objects[axis].matrix_world.translation;relative=[inv@p-centre for p in points];witnesses.append({'pose':state,'a':a,'b':b,'strictTriangleWitnessCount':count,'crossingTriangleWorldBounds':tools['bounds'](points),'axis':axis,'measuredInOwnerFrame':frame,'crossingTriangleBoundsRelativeToAxis':tools['bounds'](relative),'limit':'These are crossing triangle vertex extents, not exact penetration extents or depth.'})
(OUT/'causal-witnesses.json').write_text(json.dumps(witnesses,indent=2)+'\n')
# Four remaining angle illustrations from the exact saved candidate; no save.
scene=bpy.context.scene
for o in bpy.data.objects:
 if o.type=='MESH':o.hide_render='builder' not in o.get('exteriorEras','maker,mechanic,builder').split(',')
 elif o.type=='CURVE':o.hide_render=True
scene.render.engine='BLENDER_WORKBENCH';s=scene.display.shading;s.light='STUDIO';s.studio_light='paint.sl';s.color_type='SINGLE';s.single_color=(.56,.58,.60);s.show_shadows=False;s.show_cavity=True;s.cavity_type='BOTH';s.background_type='WORLD';scene.world.color=(.12,.13,.14);scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';d=bpy.data.cameras.new('V25 final lap angle illustrations');d.type='ORTHO';d.ortho_scale=1.40;cam=bpy.data.objects.new(d.name,d);scene.collection.objects.link(cam);scene.camera=cam;cam.location=(-6,-3.5,2.45);cam.rotation_euler=(Vector((0,-.27,1.48))-cam.location).to_track_quat('-Z','Y').to_euler();views=[]
for state in tools['STATES']:
 if state[0] in ('rest','maker-neck-jaw','contact-neck'):continue
 tools['pose'](state);scene.render.filepath=str(OUT/(state[0]+'.png'));bpy.ops.render.render(write_still=True);views.append({'pose':state[0],'path':scene.render.filepath,'sha256':hashlib.sha256(Path(scene.render.filepath).read_bytes()).hexdigest()})
(OUT/'additional-views.json').write_text(json.dumps(views,indent=2)+'\n');print(json.dumps(witnesses))
