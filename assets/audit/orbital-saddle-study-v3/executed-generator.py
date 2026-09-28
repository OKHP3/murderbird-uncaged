"""Replace the full upper orbital boundary, rather than leaving a cut sliver.

Rigid, editable meshes only. The already frozenV2 crown reliefs are retained;
the mounting bed gets a continuous lower boundary against the broad saddle.
"""
from pathlib import Path
import bpy,hashlib,json,math,runpy,shutil
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'assets/models/uncaged-orbital-saddle-study-v2/murderbird-orbital-saddle-study-v2-review.blend'
ORIGINAL=ROOT/'assets/models/uncaged-paired-bill-mandible-study-v2/murderbird-paired-bill-mandible-study-v2.blend'
OUT=ROOT/'assets/models/uncaged-orbital-saddle-study-v3'
AUDIT=ROOT/'assets/audit/orbital-saddle-study-v3'
OLD_LOWER=[(.145,-.272,1.866),(.153,-.308,1.875),(.153,-.353,1.863),(.143,-.405,1.837),(.112,-.449,1.830)]
LOWER=[(.145,-.272,1.866),(.153,-.308,1.875),(.153,-.353,1.863),(.143,-.405,1.853),(.112,-.449,1.846)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def art(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size}
def main():
    assert sha(BASE)=='7d906cd1672cd955bf4e2b8d3630bb8e6df558ac3fd8d8f02879ceb22e6f1186'
    assert sha(ORIGINAL)=='7ba7c996fbcffc118217ad4fcd0c1c1316a3e0a6b0cefa77be4794e6f5a4df15'
    assert not OUT.exists() and not AUDIT.exists()
    h=runpy.run_path(str(ROOT/'scripts/build-uncaged-alignment-v7.py'),run_name='helpers')
    g=runpy.run_path(str(ROOT/'scripts/study-head-continuous-plates-v2.py'),run_name='grid_helpers')
    def lower_at_y(y):
        lo,hi=0.,1.
        for _ in range(30):
            mid=(lo+hi)/2
            if g['lerp_rows'](LOWER,mid)[1]>y:lo=mid
            else:hi=mid
        return g['lerp_rows'](LOWER,(lo+hi)/2)
    bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL));original={}
    for side in (-1,1):
        o=bpy.data.objects[f'Forged orbital mounting plate {side}']
        original[side]=([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
    bpy.ops.wm.open_mainfile(filepath=str(BASE));before=h['scene_snapshot']();changed=[];fixings=[]
    for side in (-1,1):
        brow=bpy.data.objects[f'Forged orbital brow {side}'];m=brow.matrix_world.copy();inv=m.inverted()
        assert len(brow.data.vertices)==738
        # Raise the fore lower edge16mm to retain a real rim above the seated
        # optic. The original loft would leave insufficient aperture wall.
        for row in range(41):
            dz=g['lerp_rows'](LOWER,row/40)[2]-g['lerp_rows'](OLD_LOWER,row/40)[2]
            for skin in (0,1):
                for col in range(9):
                    v=brow.data.vertices[skin*369+row*9+col];p=m@v.co;p.z+=dz*col/8;v.co=inv@p
        brow.data.update();changed.append({'name':brow.name,'maximumAuthoredForeEdgeRiseM':.016})
        name=f'Forged orbital mounting plate {side}';points,faces=original[side];assert len(points)==896
        boundary=[]
        for i in range(64):
            outer=points[i*7+6].copy();inner=points[i*7].copy()
            if -.449<=outer.y<=-.272:
                x,_,z=lower_at_y(outer.y)
                if outer.z>z-.004:
                    outer.z=z-.004;outer.x=side*(x-.002)
                    # The annular station is oblique: outward wall width is
                    # measured along the aperture'sYZ radial, not worldZ.
                    radial=Vector((0,inner.y+.369,inner.z-1.786)).normalized()
                    assert (outer-inner).dot(radial)>.006,(side,i,list(outer),list(inner))
                    for j in range(7):
                        t=j/6;p=inner.lerp(outer,t);p.x+=side*.0035*math.sin(math.pi*t)
                        points[i*7+j]=p;points[448+i*7+j]=p-Vector((side*.009,0,0))
                    boundary.append({'station':i,'outerWorldXYZ':list(outer)})
        info=g['apply_mesh'](name,points,faces);changed.append({'name':name,'geometry':info,'newBoundary':boundary})
        # Retained fixings stay on their originalYZ axes, but seat to the
        # actual remaining mounting bed or the fixed saddle above it.
        objects=[bpy.data.objects[name],bpy.data.objects[f'Forged orbital brow {side}']]
        vertices=[];triangles=[]
        for o in objects:
            start=len(vertices);vertices.extend(o.matrix_world@v.co for v in o.data.vertices)
            triangles.extend(tuple(start+i for i in f.vertices) for f in o.data.polygons)
        tree=BVHTree.FromPolygons(vertices,triangles)
        for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(f'Orbital mounting fixing {side} ')]:
            m=o.matrix_world.copy();inv=m.inverted();world=[m@v.co for v in o.data.vertices];centre=sum(world,Vector())/len(world)
            hit,_,_,_=tree.ray_cast(Vector((side*.4,centre.y,centre.z)),Vector((-side,0,0)),.4)
            assert hit is not None,('Unseated retained fixing',o.name,list(centre))
            deepest=min(side*p.x for p in world);delta=(side*hit.x-.001)-deepest
            for v,p in zip(o.data.vertices,world):p.x+=side*delta;v.co=inv@p
            o.data.update();fixings.append({'name':o.name,'deltaOutwardM':delta,'mountSurfaceWorldXYZ':list(hit),'nominalBaseEmbedM':.001})
    after=h['scene_snapshot']();allowed={r['name'] for r in changed+fixings}
    assert before['empties']==after['empties'] and before['curves']==after['curves']
    for name,old in before['meshes'].items():
        if name not in allowed:assert after['meshes'][name]==old,name
    OUT.mkdir(parents=True);AUDIT.mkdir(parents=True);native=OUT/'murderbird-orbital-saddle-study-v3.blend'
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(native),check_existing=False)
    bpy.ops.wm.open_mainfile(filepath=str(native));assert h['scene_snapshot']()==after
    shutil.copy2(__file__,AUDIT/'executed-generator.py')
    record={'status':'unreviewed matched orbital boundary proposal; not selected','base':art(BASE),'originalMountSource':art(ORIGINAL),'native':art(native),'generator':art(AUDIT/'executed-generator.py'),'mountChanges':changed,'retainedFixingsReseated':fixings,'preservation':{'untouchedMeshesExact':len(before['meshes'])-len(allowed),'51PivotsAnd462GuidesExact':True,'allRigidNoBooleanDependencies':True,'saveReloadExact':True},'limits':['Inherited guides predate these mesh edits.','Nominal4mm upper boundary relief and1mm fixing embed require evaluated-clearance review.','No movement proof, export, app selection or owner approval.']}
    (AUDIT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    render=runpy.run_path(str(ROOT/'scripts/study-v8-bill-envelope.py'),run_name='renderer')['renders'];render.__globals__['AUDIT']=AUDIT
    record['views']=render(BASE,'before')+render(native,'after');(AUDIT/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(art(native)))
if __name__=='__main__':main()
