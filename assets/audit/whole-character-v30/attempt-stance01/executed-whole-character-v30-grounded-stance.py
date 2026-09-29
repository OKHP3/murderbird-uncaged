"""Coherent lower avian rest stance, keeping rigid leg lengths and planted feet.

This authors a new assembled rest pose into geometry and attachment positions.
Every affected solid receives a rigid world transform. Joint bases remain the
existing identity-oriented authoring convention consumed by the runtime solver.
The 100 mm settlement is a qualitative proposal, not a dimension from artwork.
"""
import bpy, math, json
from mathutils import Vector, Matrix

SETTLE = .100

def apply():
    bpy.context.view_layer.update()
    objects = list(bpy.data.objects)
    original = {o.name:o.matrix_world.copy() for o in objects}
    source = {o.name:[original[o.name] @ v.co for v in o.data.vertices] for o in objects if o.type=='MESH'}
    nodes = {o.name:{'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world]} for o in objects if o.type=='EMPTY'}
    body = bpy.data.objects['body']
    upper = {body.name} | {o.name for o in body.children_recursive}
    groups = {}; transforms = {}; chain = []
    for side in ('left','right'):
        hip = bpy.data.objects[side+'-thigh']; knee = bpy.data.objects[side+'-shin']; ankle = bpy.data.objects[side+'-foot']
        h,k,a = [original[o.name].translation.copy() for o in (hip,knee,ankle)]
        hn = h-Vector((0,0,SETTLE)); kn = k.copy()
        # X offset belongs to the transverse hip-to-knee span and stays exact.
        uy,uz = k.y-h.y,k.z-h.z; ly,lz = a.y-k.y,a.z-k.z
        upper_yz = math.hypot(uy,uz); lower_yz = math.hypot(ly,lz)
        dy,dz = a.y-hn.y,a.z-hn.z; distance=math.hypot(dy,dz)
        assert abs(upper_yz-lower_yz) < distance < upper_yz+lower_yz
        along=(upper_yz**2-lower_yz**2+distance**2)/(2*distance)
        across=math.sqrt(max(0,upper_yz**2-along**2))
        # Select the anterior knee branch, retaining an avian zig-zag stance.
        options=[Vector((k.x,hn.y+dy/distance*along+sign*dz/distance*across,
                         hn.z+dz/distance*along-sign*dy/distance*across)) for sign in (-1,1)]
        kn=min(options,key=lambda p:p.y)
        upper_angle=math.atan2(kn.z-hn.z,kn.y-hn.y)-math.atan2(uz,uy)
        lower_angle=math.atan2(a.z-kn.z,a.y-kn.y)-math.atan2(lz,ly)
        ru=Matrix.Rotation(upper_angle,3,'X'); rl=Matrix.Rotation(lower_angle,3,'X')
        assert (ru@(k-h)+hn-kn).length<1e-7
        assert (rl@(a-k)+kn-a).length<1e-7
        foot_names={ankle.name}|{o.name for o in ankle.children_recursive}
        shin_names=({knee.name}|{o.name for o in knee.children_recursive})-foot_names
        thigh_names=({hip.name}|{o.name for o in hip.children_recursive})-shin_names-foot_names
        for names,r,start,end,label in [(thigh_names,ru,h,hn,'thigh'),(shin_names,rl,k,kn,'shin')]:
            for name in names:groups[name]=side+'-'+label
            transforms[side+'-'+label]=(r,start,end)
        for name in foot_names:groups[name]='planted-foot'
        chain.append({'side':side,'oldHip':list(h),'newHip':list(hn),'oldKnee':list(k),'newKnee':list(kn),'ankleExact':list(a),
                      'upperRotationX':upper_angle,'lowerRotationX':lower_angle,
                      'upperLengthBefore':(k-h).length,'upperLengthAfter':(kn-hn).length,
                      'lowerLengthBefore':(a-k).length,'lowerLengthAfter':(a-kn).length})
    def mapped(name,p):
        if name=='anchor-joint':
            r,start,end=transforms['left-shin'];return r@(p-start)+end
        group=groups.get(name)
        if group=='planted-foot':return p.copy()
        if group:
            r,start,end=transforms[group];return r@(p-start)+end
        return p-Vector((0,0,SETTLE)) if name in upper else p.copy()
    def depth(o):
        n=0
        while o.parent:n+=1;o=o.parent
        return n
    changed_nodes=[]
    for o in sorted(objects,key=depth):
        m=original[o.name].copy()
        # Historical excluded curves retain original world poses/data.
        if o.type!='CURVE':m.translation=mapped(o.name,m.translation)
        o.matrix_world=m;bpy.context.view_layer.update()
        if o.type=='EMPTY' and (m.translation-original[o.name].translation).length>1e-9:
            changed_nodes.append({'name':o.name,'oldWorld':list(original[o.name].translation),'newWorld':list(m.translation),'orientationPreserved':True})
    changed=[];protected=[];max_error=0
    for o in objects:
        if o.type!='MESH':continue
        inverse=o.matrix_world.inverted();points=source[o.name]
        expected=[mapped(o.name,p) for p in points]
        altered=max((a-b).length for a,b in zip(points,expected))>1e-9
        if altered:
            for v,p in zip(o.data.vertices,expected):v.co=inverse@p
            o.data.update();changed.append(o.name)
        else:protected.append(o.name)
        actual=[o.matrix_world@v.co for v in o.data.vertices]
        error=max((a-b).length for a,b in zip(actual,expected));max_error=max(max_error,error)
        assert error<1e-6,o.name
        # Rigid transforms preserve every source edge length, including circles.
        for e in o.data.edges:
            i,j=e.vertices
            assert abs((actual[i]-actual[j]).length-(points[i]-points[j]).length)<1e-6,o.name
    bpy.context.view_layer.update()
    for n,before in nodes.items():
        o=bpy.data.objects[n]
        assert (o.parent.name if o.parent else None)==before['parent'],n
        assert max(abs(o.matrix_world[i][j]-before['world'][i][j]) for i in range(3) for j in range(3))<1e-6,n
    return {'region':'whole-body grounded rest stance','status':'Qualitative silhouette proposal, not owner acceptance',
            'changedMeshes':changed,'changedNodes':changed_nodes,'added':[],'removed':[],
            'chain':chain,'bodySettlementM':SETTLE,'preservedFootAndOtherMeshes':protected,
            'maximumExpectedRigidMapErrorM':max_error,'allMeshEdgeLengthsPreservedWithin1eMinus6M':True,
            'reference':'Owner whole-bird controls grounded compact support; 100mm authored settlement is a proposal, not image metrology.',
            'construction':'Paired unchanged-length leg members rotate rigidly to a lower hip. Actual feet and digits stay fixed. New rest attachment positions and geometry authored together; no runtime metal stretching.',
            'eraEligibility':'All existing component roles and era tags retained; no new actuation, sensing or surface finish.',
            'limits':['New joint-angle/guard clearance must be reviewed.','Runtime reach and cage contact must be rerun on the exported rest geometry.','Foot contact preservation is not a force or balance simulation.']}
