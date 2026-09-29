"""V27 compact wing termination: one coarse, reference-led construction.
Native Z-up/-Y-front. Dimensions are inferred authoring controls, not art
measurements. Only the existing two elbow-owned plate/guard/backing fields
change; bearings, load members, nodes, era tags and materials remain exact.
"""
import bpy,bmesh,math,json
from mathutils import Vector
OWNERS=('left-wing-shield','right-wing-shield')

def ease(t):t=max(0,min(1,t));return t*t*(3-2*t)
def names(label):return [f'{label} profiled mantle backing v4 {label}-wing-shield']+[f'V21 refined {label} compact shield course {c} plate {k}' for c,N in [(1,6),(2,6),(3,5)] for k in range(1,N+1)]+[f'V21 refined {label} elbow leading return',f'V21 refined {label} curved elbow sideguard']
def node(o):return (o.parent.name if o.parent else None,tuple(tuple(r) for r in o.matrix_world),json.dumps(dict(o.items()),sort_keys=True,default=lambda x:list(x)))
def snap(o):return (node(o),tuple(tuple(v.co) for v in o.data.vertices),tuple(tuple(f.vertices) for f in o.data.polygons),tuple(m.name if m else None for m in o.data.materials),tuple((q.name,q.type) for q in o.modifiers),o.hide_render,o.hide_viewport)

def warp(p,side,joint):
    # The root/housing and the genuine journal passage are immutable receiving
    # seats. A coordinated lower field eliminates the level sleeve contour.
    radial=math.hypot(p.y-joint.y,p.z-joint.z)
    w=ease((1.025-p.z)/.170)*ease((radial-.070)/.030)
    aft=max(0,min(1,(p.y-.040)/.370))
    q=p.copy();q.z+=w*(.065*(1-aft)**2-.045*aft**1.5)
    q.y+=w*(.014*aft-.004*(1-aft))
    q.x-=side*w*(.023*(1-aft)+.010*aft)
    return q,w

def apply():
    bpy.context.view_layer.update();changed=sum((names(label) for label in ('left','right')),[])
    nodes={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};outside={o.name:snap(o) for o in bpy.data.objects if o.type=='MESH' and o.name not in changed};records=[]
    for label,side in [('left',1),('right',-1)]:
        joint=bpy.data.objects[label+'-wing-shield'].matrix_world.translation.copy()
        assert abs(joint.z-1.007781744)<1e-6 and abs(joint.y-.039195534)<1e-6
        for name in names(label):
            o=bpy.data.objects[name];assert o.parent.name==label+'-wing-shield';assert o.get('surfaceRole') in ('frame','plate','guard')
            original=o.data;o.data=original.copy();o.data.name=name+' V27 sloped compact terminal';bpy.context.view_layer.update();inv=o.matrix_world.inverted();maximum=0;seats=0;modified=0
            for v in o.data.vertices:
                p=o.matrix_world@v.co;q,w=warp(p,side,joint)
                if w==0:seats+=1;continue
                v.co=inv@q;maximum=max(maximum,(q-p).length);modified+=1
            o.data.update();bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
            o['geometryStatus']='V27 sloped compact flightless terminal proposal; one coarse visual/posed review pending'
            o['v27TerminalConstruction']='Coordinated front shortening, aft-down free-edge sweep and lower section taper across actual shield plates, finite returns and load liner; receiving root/journal seats retained. No extended wing train.'
            records.append({'name':name,'owner':o.parent.name,'modifiedVertices':modified,'exactReceivingSeatVertices':seats,'maximumVertexDisplacementM':maximum,'wallPolicy':'Existing finite solid walls/solidify thickness and backing are shaped together; no painted seam or hidden intact sleeve.'})
    bpy.context.view_layer.update();assert nodes=={o.name:node(o) for o in bpy.data.objects if o.type=='EMPTY'};assert all(snap(bpy.data.objects[n])==s for n,s in outside.items())
    return {'region':'compact wing terminal','status':'one coarse inferred mechanical construction proposal; root appearance/motion gate pending','changedMeshes':changed,'added':[],'removed':[],'changedNodes':[],'nodesExact':len(nodes),'outsideMeshesExact':len(outside),'records':records,'contract':{'upperSeatExactAtOrAboveNativeZ':1.025,'elbowReceivingSeatExactWithinYZRadiusM':.070,'actualElbowCenters':[list(bpy.data.objects[n].matrix_world.translation) for n in OWNERS],'foreEdgeLiftAuthoringControlM':.065,'aftEdgeDropAuthoringControlM':.045,'aftSweepAuthoringControlM':.014,'maximumLowerSectionTaperM':.023,'wallDefinitionsExact':True,'materialsAndEraTagsExact':True,'singleRigidOwners':list(OWNERS)},'preserved':['all named pivots/rests and hierarchy','all actual elbow/shoulder bearings/races, shaft/load frame and left travel restriction','all mantle/other body/head/foot geometry','existing materials, era tags and motion APIs'],'limits':['Qualitative reconstruction; no exact dimensions recovered from reference.','Finite rest/short-shove sampling required; no continuous clearance, engineering or owner acceptance implied.']}
