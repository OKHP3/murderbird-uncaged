"""Owner-directed M2 head/neck posture correction on the detailed native study."""
import math
from mathutils import Matrix,Vector


def apply(scene, scaffold_path=None, era='builder'):
    shoulder=Vector((0,-.09,1.37));junction=Vector((0,-.16,1.55))
    r=Matrix.Rotation(math.radians(-14),4,'X')
    first=Matrix.Translation(shoulder)@r@Matrix.Translation(-shoulder)
    moved_junction=first@junction
    second=Matrix.Translation(moved_junction)@Matrix.Rotation(math.radians(8),4,'X')@Matrix.Translation(-moved_junction)
    head_transform=second@first;heads=[];necks=[]
    for o in list(scene.objects):
        if o.type!='MESH' or o.hide_render or o.get('cg1cSuperseded'):continue
        region=o.get('cg1cRegion')
        if region=='head':
            o.matrix_world=head_transform@o.matrix_world
            o['cg2HeadPoseDegrees']=-6;heads.append(o.name)
        elif region=='neck':
            # Pin the shoulder join and ease progressively to the full neck
            # rotation, preserving modifier/material stacks and object anchors.
            o.data=o.data.copy();world=o.matrix_world.copy();inv=world.inverted()
            for v in o.data.vertices:
                p=world@v.co;t=max(0,min(1,(p.z-1.38)/.105));t=t*t*(3-2*t)
                v.co=inv@(p.lerp(first@p,t))
            o['cg2NeckPoseDegrees']=-14;necks.append(o.name)
    return {'module':'cinematic-cg-2-head-pose','headMeshes':len(heads),'neckMeshes':len(necks),
            'neckRotationXDegrees':-14,'headAdditionalXDegrees':8,'headNetXDegrees':-6,
            'shoulderPivot':list(shoulder),'originalHeadJunction':list(junction),
            'posedHeadJunction':list(moved_junction),'headJunctionDelta':list(moved_junction-junction),
            'lowerNeckPinnedBelowZ':1.38,'neckBlendFullAtZ':1.485,'scaleChange':0,
            'scope':'pure posture correction; body/legs and head geometry/materials retained'}
