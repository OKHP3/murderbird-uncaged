from pathlib import Path
import bpy,json,hashlib,math
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_ray_tri
OUT=Path('/tmp/v31-head-reconstruction/attempt05-fit-f/screen');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=(OUT/'executed-strict-kernel.py').read_text();exec(s[s.index('def inside'):s.index('poses=[]')]);rows=[]
for label,path in [('03fit',Path('/tmp/v31-head-reconstruction/attempt03-fit/head-reconstruction.blend')),('candidate05f',Path('/tmp/v31-head-reconstruction/attempt05-fit-f/head-reconstruction.blend'))]:
 bpy.ops.wm.open_mainfile(filepath=str(path)) if False else bpy.ops.wm.open_mainfile(filepath=str(path));bpy.context.view_layer.update()
 p=(OUT/'executed-pose-input.py').read_text();exec(p[p.index('CHAIN='):p.index('def inside')]);result=[]
 for state in STATES:
  pose(state);dg=bpy.context.evaluated_depsgraph_get();allitems=[mesh(o,dg) for o in bpy.data.objects if o.type=='MESH' and o.parent and o.parent.name in set(CHAIN)|{'head'}];owners={o.name:o.parent.name for o in bpy.data.objects if o.type=='MESH' and o.parent};active={o.name for o in bpy.data.objects if o.type=='MESH' and (o.name.startswith('V31 formed throat receiving guard') if label=='candidate05f' else o.name.startswith('V31 fixed lower skull hood'))};pairs=[]
  for a in allitems:
   if a[0] not in active:continue
   for b in allitems:
    if owners[b[0]] not in CHAIN:continue
    hits=0;first=None
    for ia,ib in a[3].overlap(b[3]):
     A=[a[1][i] for i in a[2][ia]];B=[b[1][i] for i in b[2][ib]]
     if any(edge(A[k],A[(k+1)%3],B) or edge(B[k],B[(k+1)%3],A) for k in range(3)):
      hits+=1
      if first is None:first={'indices':[ia,ib],'activeTriangle':[list(x) for x in A],'neighborTriangle':[list(x) for x in B],'centroid':list(sum(A+B,Vector())/6)}
    if hits:pairs.append({'active':a[0],'neighbor':b[0],'strictTrianglePairs':hits,'firstWitness':first})
  result.append({'pose':state[0],'angles':list(state[1:]),'activeGuards':sorted(active),'pairCount':len(pairs),'pairs':pairs});print(label,state[0],len(pairs),flush=True)
 rows.append({'label':label,'native':str(path),'nativeSHA256':sha(path),'poses':result})
pack={'moduleSHA256':sha(OUT.parent/'executed-head-reconstruction.py'),'screenSHA256':sha(Path(__file__)),'poseInputSHA256':sha(OUT/'executed-pose-input.py'),'method':'Only 03fit/04 head-owned lower receiving hood meshes against all four cervical-owner meshes. Same exact strict kernel and seven discrete runtime-angle samples from existing validator; not whole neck or continuous clearance.','models':rows};(OUT/'receiving-poses.json').write_text(json.dumps(pack,indent=2)+'\n')
