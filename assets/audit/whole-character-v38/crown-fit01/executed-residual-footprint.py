"""Read-only exact residual paired triangle/vertex footprint; unchanged epsilon."""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
native,output=map(Path,sys.argv[sys.argv.index('--')+1:]);assert not output.exists()
bpy.ops.wm.open_mainfile(filepath=str(native));bpy.context.view_layer.update()
def mesh(o):
 o.data.calc_loop_triangles();v=[o.matrix_world@x.co for x in o.data.vertices];t=[tuple(x.vertices) for x in o.data.loop_triangles]
 return v,t,BVHTree.FromPolygons(v,t,all_triangles=True,epsilon=1e-7)
def footprint(vertices):
 return {'vertices':sorted(vertices),'outerRows':sorted({v//13 for v in vertices if v<169}),'innerRows':sorted({(v-169)//13 for v in vertices if v>=169}),'columns':sorted({(v%169)%13 for v in vertices})}
records=[]
for col in range(1,6):
 stem=f'V38 swept crown course 3 column {col}';a=bpy.data.objects[stem+' leaf 1'];b=bpy.data.objects[stem+' leaf 2'];va,ta,ba=mesh(a);vb,tb,bb=mesh(b);hits=ba.overlap(bb);av={v for i,j in hits for v in ta[i]};bv={v for i,j in hits for v in tb[j]}
 records.append({'course':stem,'triangleCandidates':len(hits),'triangleIndexPairs':hits,'leading':footprint(av),'trailing':footprint(bv),'trailingExcludedVerticesInCandidates':sorted(bv-set(range(65))-set(range(169,234)))})
output.write_text(json.dumps({'status':'residual exact surface footprint; not penetration or full fit proof','nativeSha256':hashlib.sha256(native.read_bytes()).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'epsilonM':1e-7,'pairs':records},indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ('course','triangleCandidates','leading','trailing','trailingExcludedVerticesInCandidates')} for r in records]))
