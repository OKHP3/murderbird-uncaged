"""Check that the actual Advanced optic is visible through its exterior shell."""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--iteration',required=True)
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
source=ROOT/'assets/models/uncaged-appearance-v1/iterations'/args.iteration/'murderbird-appearance.blend'
bpy.ops.wm.open_mainfile(filepath=str(source))
verts=[];faces=[];owners=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or 'builder' not in o.get('exteriorEras','').split(','):continue
    start=len(verts);verts.extend(o.matrix_world@v.co for v in o.data.vertices)
    for f in o.data.polygons:faces.append(tuple(start+i for i in f.vertices));owners.append(o)
bvh=BVHTree.FromPolygons(verts,faces,all_triangles=False)
checks=[]
for side in [-1,1]:
    lenses=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('surfaceRole')=='optic' and 'builder' in o.get('exteriorEras','').split(',') and 'lens' in o.name.lower() and side*(o.matrix_world@o.data.vertices[0].co).x>0]
    assert lenses,'Missing separate optic lens'
    points=[o.matrix_world@v.co for o in lenses for v in o.data.vertices]
    center=Vector((max(p.x*side for p in points)*side,-.369,1.786))
    for label,position in [('lateral',(side*3,center.y,center.z)),('front-three-quarter',(side*3.8,-6,2.0))]:
        origin=Vector(position);hits=[]
        for r,n in [(0,1),(.010,8),(.020,12)]:
            for k in range(n):
                target=center+Vector((0,r*math.cos(math.tau*k/n),r*math.sin(math.tau*k/n)))
                loc,normal,index,distance=bvh.ray_cast(origin,(target-origin).normalized(),10)
                owner=owners[index] if index is not None else None
                hits.append({'visibleLens':bool(owner and owner in lenses),'hit':owner.name if owner else None})
        visible=sum(h['visibleLens'] for h in hits)
        checks.append({'side':side,'view':label,'lensCenter':list(center),'visibleSamples':visible,'samples':len(hits),'fraction':visible/len(hits),'centerVisible':hits[0]['visibleLens'],'hits':hits})
status='passed' if all(c['centerVisible'] and c['fraction']>=.70 for c in checks) else 'failed'
out=ROOT/'assets/audit/appearance-v1'/args.iteration/'optic-visibility.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({'status':status,'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'checks':checks,'scope':'Static visibility ray tests of the exported-source lens through actual exterior meshes; does not establish likeness or motion clearance.'},indent=2)+'\n')
print('OPTIC_VISIBILITY',status,[(c['side'],c['view'],c['visibleSamples'],c['centerVisible']) for c in checks])
if status!='passed':raise RuntimeError('Exterior geometry occludes the optic; inspect the recorded first-hit mesh names.')
