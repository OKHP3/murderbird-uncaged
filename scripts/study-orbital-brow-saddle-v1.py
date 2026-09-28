"""A fixed, broad orbital saddle with a recessed mounting bed.

One write-once neutral geometry proposal from the paired bill/mandible native.
Authored stations express the July head's sloping planes; they are not image
measurements. Both brow and supporting bed are edited as one bounded region.
"""
from pathlib import Path
import hashlib, json, runpy, shutil
import bpy
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.blend'
BASE_SHA='7ba7c996fbcffc118217ad4fcd0c1c1316a3e0a6b0cefa77be4794e6f5a4df15'
OUT=ROOT/'assets/models/uncaged-orbital-saddle-study-v1'
AUDIT=ROOT/'assets/audit/orbital-saddle-study-v1'
# Separate upper and lower edge stations avoid widening a rounded trim band.
# XYZ coordinates, anatomical-right mirrored for the opposite cheek.
UPPER=[(.117,-.258,1.885),(.119,-.290,1.909),(.107,-.340,1.916),(.091,-.395,1.891),(.097,-.451,1.852)]
LOWER=[(.145,-.272,1.866),(.153,-.308,1.875),(.153,-.353,1.863),(.143,-.405,1.837),(.112,-.449,1.830)]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}

def main():
    assert sha(BASE)==BASE_SHA and not OUT.exists() and not AUDIT.exists()
    h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
    g=runpy.run_path(str(ROOT/'scripts/study-head-continuous-plates-v2.py'),run_name='grid_helpers')
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']()
    names={f'{kind} {side}' for side in (-1,1) for kind in ('Forged orbital brow','Forged orbital mounting plate')}
    changes=[]
    for side in (-1,1):
        name=f'Forged orbital brow {side}';o=bpy.data.objects[name]
        world=o.matrix_world.copy();o.parent=bpy.data.objects['head'];o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_world=world
        outer=[];inner=[];along,across=40,8
        for j in range(along+1):
            upper=Vector(g['lerp_rows'](UPPER,j/along));lower=Vector(g['lerp_rows'](LOWER,j/along))
            for k in range(across+1):
                p=upper.lerp(lower,k/across)
                outer.append((side*p.x,p.y,p.z));inner.append((side*(p.x-.006),p.y,p.z))
        verts,faces=g['closed_grid'](outer,inner,along,across)
        info=g['apply_mesh'](name,verts,faces)
        o['constructionProposal']='Fixed broad orbital saddle, distinct from independently opening crown'
        # Recess the complete original mounting wall beneath this new rigid
        # plate. Both original skins move together, preserving wall thickness.
        stride=across+1
        front_faces=[(j*stride+k,j*stride+k+1,(j+1)*stride+k+1,(j+1)*stride+k) for j in range(along) for k in range(across)]
        tree=BVHTree.FromPolygons([Vector(p) for p in inner],front_faces)
        mount=bpy.data.objects[f'Forged orbital mounting plate {side}'];m=mount.matrix_world.copy();inv=m.inverted()
        assert len(mount.data.vertices)==896
        count=0;maximum=0
        for i in range(448):
            p=m@mount.data.vertices[i].co
            hit,_,_,_=tree.ray_cast(Vector((side*.4,p.y,p.z)),Vector((-side,0,0)),.4)
            if hit is None:continue
            delta=max(0,abs(p.x)-(abs(hit.x)-.001))
            if delta:
                for index in (i,i+448):
                    q=m@mount.data.vertices[index].co;q.x-=side*delta;mount.data.vertices[index].co=inv@q
                count+=1;maximum=max(maximum,delta)
        mount.data.update()
        changes.append({'brow':name,'geometry':info,'owner':'head','mountingSkinPairsRecessed':count,'maximumMountingRecessM':maximum})
    after=h['scene_snapshot']()
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    for name,old in before['meshes'].items():
        if name not in names:assert after['meshes'][name]==old,name
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True)
    native=OUT/'murderbird-orbital-saddle-study-v1.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    record={'status':'unreviewed fixed orbital construction proposal; not selected','base':art(BASE),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'changes':changes,'upperEdgeXYZ':UPPER,'lowerEdgeXYZ':LOWER,'preservation':{'other695MeshesExact':True,'all51PivotsAnd462GuidesExact':True,'saveReloadExact':True},'referenceScope':'July head only. Sloped broad planes, constructed aperture, fixed cheek and independently opening crown. Authored dimensions and hidden attachment are proposals.','limits':['No export or app change.','Fastener seating, cranial opening clearance and appearance are not established.','Mount recess is limited to projected supporting bed; unrelated wall or crown intersections require review.','Inherited curves are not updated shape authority.']}
    (AUDIT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    render=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders'];render.__globals__['AUDIT']=AUDIT
    record['views']=render(BASE,'before')+render(native,'after')
    (AUDIT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(art(native)))

if __name__=='__main__':main()
