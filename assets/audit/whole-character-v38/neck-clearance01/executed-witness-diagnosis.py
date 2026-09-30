"""Read-only complete strict footprint, using unchanged seven-pose screen functions."""
import bpy,sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
source=ROOT/'scripts/validate-neck-guard-envelope.py';native=ROOT/'assets/models/whole-character-v38/neck-study02/murderbird-v38-neck-study02.blend';out=Path(__file__).parent/'witness-diagnosis';assert not out.exists()
sys.argv=['diagnosis','--','--model',str(native),'--sha','f3482b83014f420fcfbfe5ddab89282d5dc397952a2c36c6e932c572885fc4e1','--output',str(out)]
namespace={'__file__':str(source),'__name__':'diagnostic_screen_functions'};exec(source.read_text().split("result={'nativeSHA256'")[0],namespace)
namespace['pose'](namespace['STATES'][1]);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
def mesh(o):
 ev=o.evaluated_get(dg);m=ev.to_mesh();m.calc_loop_triangles();points=[ev.matrix_world@v.co for v in m.vertices];triangles=[tuple(t.vertices) for t in m.loop_triangles];ev.to_mesh_clear();return points,triangles,namespace['BVHTree'].FromPolygons(points,triangles,all_triangles=True)
a=bpy.data.objects['V23 cervical 3 directional guard 10'];b=bpy.data.objects['V23 cervical 4 directional guard 10'];va,ta,ba=mesh(a);vb,tb,bb=mesh(b);hits=[]
for ia,ib in ba.overlap(bb):
 tx=[va[i] for i in ta[ia]];ty=[vb[i] for i in tb[ib]]
 if any(namespace['edge'](tx[k],tx[(k+1)%3],ty) or namespace['edge'](ty[k],ty[(k+1)%3],tx) for k in range(3)):
  norm=(tx[1]-tx[0]).cross(tx[2]-tx[0]).normalized();signed=[norm.dot(p-tx[0]) for p in ty]
  hits.append({'lowerTriangle':ia,'upperTriangle':ib,'lowerVertices':ta[ia],'upperVertices':tb[ib],'lowerNormalWorldMaker':list(norm),'upperSignedDistancesToLowerPlaneM':signed,'upperTrianglesWorldMaker':[list(p) for p in ty]})
indices=sorted({i for h in hits for i in h['upperVertices']});report={'status':'Actual strict crossing footprint; not full containment or penetration certificate','nativeSha256':hashlib.sha256(native.read_bytes()).hexdigest(),'screenSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'diagnosisSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'pose':namespace['STATES'][1],'actualStrictTrianglePairs':len(hits),'upperVertexFootprint':indices,'outerRows':sorted({i//19 for i in indices if i<399}),'innerRows':sorted({(i-399)//19 for i in indices if i>=399}),'columns':sorted({i%399%19 for i in indices}),'hits':hits,'upperMakerMatrixWorld':[list(r) for r in b.matrix_world]}
(out/'diagnosis.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['actualStrictTrianglePairs','upperVertexFootprint','outerRows','innerRows','columns']}))
