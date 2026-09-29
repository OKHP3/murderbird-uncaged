"""V27 lower torso transition study, with supporting breast members.

A relative contour proposal from the owner whole-bird reference. These are
new authored coordinates, never measurements claimed from perspective art.
This changes rigid authoring shapes, not deforming runtime armor.
"""
import bpy, math, json
from mathutils import Vector

def bell(z, low, peak, high):
    if z <= low or z >= high: return 0.0
    t=(z-low)/(peak-low) if z<peak else (high-z)/(high-peak)
    return t*t*(3-2*t)

def transform(p):
    lower=bell(p.z,.800,.915,1.165)
    chest=bell(p.z,.835,1.110,1.295)
    anterior=max(0.,min(1.,(-.030-p.y)/.250))
    return Vector((p.x*(1+.145*lower), p.y+.024*chest*anterior+.010*lower, p.z))

def signature(o):
    return (o.parent.name if o.parent else None, tuple(tuple(r) for r in o.matrix_world),
        tuple(tuple(v.co) for v in o.data.vertices), tuple(tuple(f.vertices) for f in o.data.polygons),
        tuple(m.name if m else None for m in o.data.materials),
        json.dumps(dict(o.items()),default=lambda x:list(x),sort_keys=True))

def apply():
    bpy.context.view_layer.update()
    nodes={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world)) for o in bpy.data.objects if o.type=='EMPTY'}
    eligible=[o for o in bpy.data.objects if o.type=='MESH' and o.parent and
        (o.parent.name=='breastplate' or (o.parent.name=='body' and o.get('region') in ('breast','back')))]
    selected=[o for o in eligible if any((transform(o.matrix_world@v.co)-o.matrix_world@v.co).length>1e-9 for v in o.data.vertices)]
    names={o.name for o in selected}
    outside={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
    changed=[]
    for o in selected:
        points=[o.matrix_world@v.co for v in o.data.vertices]; inverse=o.matrix_world.inverted()
        o.data=o.data.copy()
        for v,p in zip(o.data.vertices,points): v.co=inverse@transform(p)
        o.data.update()
        o['v27TorsoTransition']='Lower thoracic volume and supports reshaped together; rigid runtime owners retained'
        after=[o.matrix_world@v.co for v in o.data.vertices]
        assert all(math.isfinite(c) for p in after for c in p)
        assert max(abs(p.z-q.z) for p,q in zip(points,after))<1e-6
        changed.append({'name':o.name,'owner':o.parent.name,'maximumAuthoredDisplacementM':max((p-q).length for p,q in zip(points,after))})
    bpy.context.view_layer.update()
    assert nodes=={o.name:(o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world)) for o in bpy.data.objects if o.type=='EMPTY'}
    assert outside=={o.name:signature(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in names}
    return {'region':'torso-transition','status':'Coarse contour proposal, not accepted likeness',
        'reference':'Owner whole-bird image controls integrated lower body mass; July body excluded',
        'changed':changed,'added':[],'removed':[],
        'construction':'Exterior breast/back and implicated fixed thoracic supports reshaped together. Opening hinge and hip roots remain at their original positions.',
        'parameters':{'lowerWidthIncreaseMaximum':.145,'lowerBandZ':[.800,.915,1.165],'frontChestRetreatMaximumM':.024,'upperBandZ':[.835,1.110,1.295]},
        'preserved':{'rigNodeRests':len(nodes),'outsideMeshes':len(outside),'materialsAndEraEligibility':True},
        'limits':['Authored qualitative proportion study; no dimensions recovered from art.',
            'This does not add or certify a load-bearing hip receiving assembly.',
            'Opening and leg-clearance review required before integration.']}
