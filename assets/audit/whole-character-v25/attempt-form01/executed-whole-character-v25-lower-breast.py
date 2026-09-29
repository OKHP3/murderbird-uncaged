"""V25 modest lower-breast taper with its supporting members.

Whole-bird owner reference controls the taper into the exposed leg frame.
This is an authored relative proportion proposal, not measured anatomy.
The upper chest, neck, named pivots, pelvis and leg/foot assemblies stay put.
"""
import bpy,math,json
from mathutils import Vector

def taper_weight(z):
    # Zero at the hip-support line and before the upper breast's full peak.
    if z<=.800 or z>=1.155:return 0.
    if z<.945:
        t=(z-.800)/.145
    else:
        t=(1.155-z)/.210
    return t*t*(3-2*t)

def transform(p):
    w=taper_weight(p.z)
    front=max(0.,min(1.,(-.015-p.y)/.280))
    return Vector((p.x*(1-.12*w),p.y+.032*w*front,p.z))

def snapshot(o):
    return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),
            tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),
            tuple(m.name if m else None for m in o.data.materials),json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True))

def apply():
    bpy.context.view_layer.update()
    nodes={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world)) for o in bpy.data.objects if o.type=='EMPTY'}
    eligible=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and
              (o.parent.name=='breastplate' or (o.parent.name=='body' and o.get('region')=='breast'))]
    selected=[o for o in eligible if any(taper_weight((o.matrix_world@v.co).z)>1e-9 for v in o.data.vertices)]
    names={o.name for o in selected};outside={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
    changed=[]
    for o in selected:
        original=[o.matrix_world@v.co for v in o.data.vertices];inv=o.matrix_world.inverted()
        o.data=o.data.copy()
        for v,p in zip(o.data.vertices,original):v.co=inv@transform(p)
        o.data.update();o['v25LowerBreast']='Authored lower taper; fixed upper breast and hip-line boundaries; rigid at runtime'
        now=[o.matrix_world@v.co for v in o.data.vertices]
        assert all(math.isfinite(c) for p in now for c in p)
        assert max(abs(p.z-q.z) for p,q in zip(original,now))<1e-6
        unchanged=[i for i,p in enumerate(original) if taper_weight(p.z)==0]
        assert all((original[i]-now[i]).length<1e-6 for i in unchanged)
        changed.append({'name':o.name,'owner':o.parent.name,'maxAuthoredDisplacement':max((p-q).length for p,q in zip(original,now)),
          'minBefore':[min(p[k] for p in original) for k in range(3)],'maxBefore':[max(p[k] for p in original) for k in range(3)],
          'minAfter':[min(p[k] for p in now) for k in range(3)],'maxAfter':[max(p[k] for p in now) for k in range(3)]})
    bpy.context.view_layer.update()
    assert nodes=={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world)) for o in bpy.data.objects if o.type=='EMPTY'}
    assert outside=={o.name:snapshot(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
    return {'region':'lower-breast','changed':changed,'added':[],'removed':[],
      'controllingReference':'Owner whole-bird illustration: full upper breast narrowing into visible lower frame',
      'proposedTaper':{'nativeZRange':[.800,1.155],'peakZ':.945,'maximumWidthReduction':.12,'maximumAnteriorRetreat':.032},
      'attachment':'All plates, backing and affected body-fixed breast supports transformed coherently at authoring; each retained on its existing rigid owner',
      'preserved':{'rigNodeRests':len(nodes),'outsideMeshes':len(outside),'upperBreastAndHipLineBoundaryVertices':True},
      'eraEligibility':'Existing eligibility and materials unchanged; no new powered or sensory components',
      'limits':['Relative silhouette proposal, not physical simulation or illustration-derived dimensions.','No new joint clearance or complete-era integration acceptance.']}
